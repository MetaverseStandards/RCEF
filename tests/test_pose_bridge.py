# SPDX-License-Identifier: MIT
"""The viseme pose bridge against its calibration record and Route, without the generator.

- the bridge reads only partition classes, and exactly those whose held-out cells all pass;
- each weight is the record's frozen pose, read through one copy per class and one clamp per output;
- the clamp chain gives clamp(sum of weight times pose, 0, 1) on random frames;
- it writes whole canonical expression groups, and only cites the record on its sums;
- Route runs it only from a viseme set to an expression set, and every other route is as without it;
- refusals, labels, dropped classes and the classes a source cannot write.
"""
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

_spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)

BRIDGE = 'rcef_viseme.to_rcef_expression'
RECORD = 'viseme-poses.rocketbox-features'
VISEME, EXPRESSION = 'rcef.canonical_viseme', 'rcef.canonical_expression'
GROUPS = {'face', 'cheek_puff', 'jaw_thrust', 'chin_raise_upper_lip'}
COPY = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
META = 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META'
META_NAMES = ['SIL', 'PP', 'FF', 'TH', 'DD', 'KK', 'CH', 'SS', 'NN', 'RR', 'AA', 'E', 'IH', 'OH', 'OU']
SETS = ['arkit.coefficient', 'openxr.fb2', 'openxr.visemes', 'vrm.preset', 'vrcft.artist.base', 'vrcft.eye',
        'facs.code']


class PoseBridge(unittest.TestCase):
    @classmethod
    def load_pack(cls) -> dict:
        """The pack under test; the A/B mutation check (scripts/ab_mutations.py) gives a changed copy instead."""
        return json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))

    @classmethod
    def setUpClass(cls):
        cls.document = cls.load_pack()
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.signals = {s['id']: s for s in cls.document['signals']}
        cls.members = {p['id']: p['signal_ids'] for p in cls.document['profiles']}
        cls.rules = next(m['rules'] for m in cls.document['mappings'] if m['id'] == BRIDGE)
        cls.record = tomllib.loads((ROOT / f'calibration/{RECORD}.cal').read_text(encoding='utf-8'))
        cls.passing = [c for c in cls.record['channels'] if check.channel_passes(cls.record, c)]
        cls.writer = {r['outputs'][0]: r for r in cls.rules}
        cls.sums = [r for r in cls.rules if r['operator']['id'] == 'weighted_sum']
        cls.clamp = {r['inputs'][0]: r for r in cls.rules if r['operator']['id'] == 'piecewise_linear'}
        cls.compiled = {}

    def route(self, source, target, pack=None, compiled=None):
        """A Route that reuses the maps already compiled from the same pack."""
        compiled = self.compiled if compiled is None else compiled
        route = rcef_route.Route(source, target, pack=pack or self.pack, compiled=compiled)
        compiled.update(route.mappings)
        return route

    def classes_of(self, rule):
        """The canonical classes a sum reads, through the copy that makes each input."""
        out = []
        for sid in rule['inputs']:
            copy = self.writer[sid]
            self.assertEqual(copy['operator'], COPY, copy['id'])
            out.append(copy['inputs'][0])
        return out

    def poses(self):
        """{expression signal: {class: weight}} as the bridge applies them."""
        return {self.clamp[r['outputs'][0]]['outputs'][0]: dict(zip(self.classes_of(r), r['operator']['weights']))
                for r in self.sums}

    def test_it_reads_only_partition_classes_and_exactly_the_passing_ones(self):
        inputs, outputs = rcef_route.map_ends(self.rules)
        partition = {s for s in self.members[VISEME] if self.signals[s]['coupling'] == 'probability_simplex'}
        self.assertEqual(len(partition), 15)
        self.assertLessEqual(set(inputs), partition)
        self.assertNotIn(f'{VISEME}.alveolar_floor', inputs)
        self.assertEqual(sorted(inputs), sorted(self.passing))
        self.assertEqual(len(self.passing), 11)
        for rule in self.sums:
            self.assertEqual(self.classes_of(rule), self.passing, rule['id'])

    def test_it_is_written_from_the_perceptual_record_alone(self):
        rigs = {c['identity'] for c in self.record['cells']}
        self.assertEqual(len(rigs), 4)
        for channel in self.record['channels']:
            self.assertEqual(len([c for c in self.record['cells'] if c['channel'] == channel]), 4, channel)
        self.assertEqual([c.rsplit('.', 1)[1] for c in self.passing],
                         ['vowel_open', 'vowel_mid_spread', 'vowel_close_spread', 'vowel_mid_rounded',
                          'vowel_close_rounded', 'bilabial', 'dental', 'alveolar_sibilant', 'coronal_stop', 'dorsal',
                          'sil'])
        gated = {c for c in self.passing
                 if not all(check.cell_passes(self.record, x) for x in self.record['cells'] if x['channel'] == c)}
        self.assertEqual(sorted(c.rsplit('.', 1)[1] for c in gated),
                         ['alveolar_sibilant', 'bilabial', 'vowel_close_rounded', 'vowel_mid_spread'])
        for old in ('viseme-poses.rocketbox-female', 'viseme-poses.rocketbox-multi'):
            cited = f'calibration.{old}'
            self.assertFalse([r['id'] for m in self.document['mappings'] for r in m['rules'] if cited in r['evidence']])
            self.assertNotIn(cited, {e['id'] for e in self.document['evidence']})
            self.assertTrue((ROOT / f'calibration/{old}.cal').is_file())

    def test_each_weight_is_the_frozen_pose_of_the_record(self):
        curves = {(c['input'], c['output']): c['knots'] for c in self.record['curves']}
        poses = self.poses()
        self.assertEqual(len(poses), 45)
        for output, weights in poses.items():
            for cls, weight in weights.items():
                self.assertEqual(curves[(cls, output)], [[0.0, 0.0], [1.0, weight]], (cls, output))

    def test_it_writes_whole_expression_groups_and_nothing_else(self):
        _, outputs = rcef_route.map_ends(self.rules)
        whole = {s for s in self.members[EXPRESSION] if self.signals[s]['metadata']['group'] in GROUPS}
        self.assertEqual(set(outputs), whole)
        self.assertEqual(len(outputs), len(set(outputs)))

    def test_the_chain_is_copy_then_sum_then_clamp(self):
        k = float(len(self.passing))
        for rule in self.rules:
            for sid in rule['inputs'] + rule['outputs']:
                if sid.startswith('rcef.intermediate.'):
                    self.assertIn(sid, self.members['rcef.intermediate'])
                    self.assertEqual(self.signals[sid]['units'], '1')
        for rule in self.sums:
            [helper] = rule['outputs']
            self.assertEqual(self.signals[helper]['domain'], {'min': 0.0, 'max': k})
            self.assertEqual(self.clamp[helper]['operator']['knots'], [[0.0, 0.0], [1.0, 1.0], [k, 1.0]])
        self.assertEqual(len(self.rules), len(self.passing) + 2 * len(self.sums))

    def test_the_compiled_bridge_gives_the_clamped_sum(self):
        compiled = self.route('openxr.visemes', 'arkit.coefficient').mappings[BRIDGE]
        poses, rng = self.poses(), random.Random(20261029)
        frames = []
        for n in range(200):
            values = {c: rng.random() * (1.0 if n % 2 else 1.0 / len(self.passing)) for c in self.passing}
            frames.append({'timestamp': float(n), 'values': values, 'validity': dict.fromkeys(values, True)})
        result = rcef_route.msf.evaluate_mapping(compiled, frames)
        self.assertTrue(result.ok, result.report.to_dict())
        clamped = 0
        for frame, sample in zip(frames, result.value.samples):
            for output, weights in poses.items():
                total = 0.0
                for cls in self.passing:
                    total += frame['values'][cls] * weights[cls]
                self.assertAlmostEqual(sample['values'][output], min(max(total, 0.0), 1.0), places=12)
                clamped += total > 1.0
        self.assertGreater(clamped, 0)

    def test_only_the_sums_cite_the_record(self):
        cited = [r['id'] for r in self.rules if f'calibration.{RECORD}' in r['evidence']]
        self.assertEqual(cited, [r['id'] for r in self.sums])
        self.assertEqual({r['evidence_status'] for r in self.rules}, {'proposed'})
        self.assertEqual({r['mapping_quality'] for r in self.rules}, {'approximate'})
        self.assertIn(f'calibration.{RECORD}', {e['id'] for e in self.document['evidence']})
        self.assertEqual(check.calibration_problems(ROOT / 'calibration', check.pack_rules(ROOT)), [])

    def test_route_runs_the_bridge_only_from_a_viseme_set_to_an_expression_set(self):
        for source, target in itertools.product(SETS, SETS):
            with self.subTest(source=source, target=target):
                route = self.route(source, target)
                expected = source in ('openxr.visemes', 'vrm.preset') and target in (
                    'arkit.coefficient', 'openxr.fb2', 'vrcft.artist.base', 'facs.code')
                self.assertEqual(route.bridges, [BRIDGE] if expected else [])
                if expected:
                    self.assertTrue(route.in_maps)
                    self.assertLessEqual(set(route.in_maps), {'visemes.to_rcef_viseme', 'vrm.to_rcef_expression',
                                                              'vrm.to_rcef_viseme'})

    def test_every_other_route_is_as_without_the_bridge(self):
        without = dict(self.document, mappings=[m for m in self.document['mappings'] if m['id'] != BRIDGE])
        bare = rcef_translate.load_pack(without)
        flags = {f.strip(): True for s in self.signals.values() if s.get('validity')
                 for f in s['validity'].split(' AND ')}
        rng, cache = random.Random(7), {}
        for source, target in itertools.product(SETS, SETS):
            route = self.route(source, target)
            if route.bridges:
                continue
            with self.subTest(source=source, target=target):
                old = self.route(source, target, bare, cache)
                self.assertEqual((route.in_maps, route.out_maps, route.hops, route.kept),
                                 (old.in_maps, old.out_maps, old.hops, old.kept))
                inputs = sorted(old.kept or {i for m in old.in_maps for i in old.mappings[m].required_inputs})
                frames = [{'time': float(n), 'values': {s: rng.random() for s in inputs}, 'flags': flags}
                          for n in range(5)]
                self.assertEqual(route.translate(frames), old.translate(frames))

    def meta_frame(self, valid=True, **weights):
        return {'time': 0.0, 'values': {META.format(n): weights.get(n, 0.0) for n in META_NAMES},
                'flags': {'isValid': valid}}

    def test_meta_to_arkit_drops_failing_classes_and_refuses_upstream(self):
        route = self.route('openxr.visemes', 'arkit.coefficient')
        aa, ff, sil, bad, pp = route.translate([self.meta_frame(AA=1.0), self.meta_frame(FF=1.0),
                                                self.meta_frame(SIL=1.0), self.meta_frame(False, AA=1.0),
                                                self.meta_frame(PP=1.0)])
        self.assertEqual(aa['values']['arkit.coefficient.jawOpen'],
                         self.poses()[f'{EXPRESSION}.jaw_drop'][f'{VISEME}.vowel_open'])
        self.assertEqual(aa['dropped'], [])
        self.assertEqual(ff['dropped'], [META.format('FF')])
        self.assertEqual(set(ff['values'].values()), {0.0})
        # bilabial passes by its perceptual gate, so PP now drives lip closure.
        self.assertEqual(pp['dropped'], [])
        self.assertEqual(pp['values']['arkit.coefficient.mouthRollLower'],
                         self.poses()[f'{EXPRESSION}.lip_suck_lower_left'][f'{VISEME}.bilabial'])
        self.assertEqual(set(sil['values'].values()), {0.0})
        # The groups the bridge does not write are not available, never refused.
        self.assertEqual(set(aa['labels'].values()), {rcef_route.NOT_AVAILABLE})
        self.assertIn('arkit.coefficient.eyeBlinkLeft', aa['labels'])
        self.assertIn('arkit.coefficient.jawLeft', aa['labels'])
        self.assertEqual(set(bad['values']), set())
        refused = {lab for lab in bad['labels'].values() if lab != rcef_route.NOT_AVAILABLE}
        self.assertEqual(refused, {'refused upstream at visemes.to_rcef_viseme'})
        self.assertNotIn(BRIDGE, bad['refused'])
        self.assertEqual(aa['notes'], [])

    def test_vrm_vowels_drive_the_bridge_with_the_classes_vrm_lacks_at_zero(self):
        route = self.route('vrm.preset', 'arkit.coefficient')
        vowels = {f'{VISEME}.{v}' for v in ('vowel_open', 'vowel_mid_spread', 'vowel_close_spread',
                                             'vowel_mid_rounded', 'vowel_close_rounded')}
        self.assertEqual(route.fill[BRIDGE], sorted(set(self.passing) - vowels))
        presets = {s: 0.0 for s in route.kept | {f'vrm.preset.{p}' for p in ('aa', 'ee', 'ih', 'oh', 'ou')}}
        vrm, = route.translate([{'time': 0.0, 'values': {**presets, 'vrm.preset.aa': 1.0, 'vrm.preset.ee': 0.5},
                                 'flags': {}}])
        meta, = self.route('openxr.visemes', 'arkit.coefficient').translate([self.meta_frame(AA=1.0, E=0.5)])
        # VRM also writes the blink group itself, through its blink in-map.
        blinks = {f'arkit.coefficient.eyeBlink{s}': 0.0 for s in ('Left', 'Right')}
        self.assertEqual(vrm['values'], {**meta['values'], **blinks})
        self.assertEqual(vrm['dropped'], [])
        self.assertEqual(len(vrm['notes']), 1)
        self.assertIn('counted as 0', vrm['notes'][0])

    def synthetic(self, change):
        """A pack compiled from a changed copy of the published pack document."""
        document = json.loads(json.dumps(self.document))
        change(document)
        return rcef_translate.load_pack(document)

    def test_no_bridge_where_the_source_writes_the_bridge_outputs_itself(self):
        def add_jaw_in_map(document):
            maps = {m['id']: m for m in document['mappings']}
            rule = json.loads(json.dumps(maps['vrm.to_rcef_viseme']['rules'][0]))
            rule.update(id='synthetic.jaw', outputs=[f'{EXPRESSION}.jaw_drop'])
            for loss in rule['loss_annotations']:
                loss['refs'] = rule['inputs'] + rule['outputs']
            maps['vrm.to_rcef_expression']['rules'].append(rule)
        route = rcef_route.Route('vrm.preset', 'arkit.coefficient', pack=self.synthetic(add_jaw_in_map))
        self.assertEqual(route.bridges, [])
        self.assertEqual(route.in_maps, ['vrm.to_rcef_expression'])

    def test_a_frame_the_bridge_refuses_labels_its_outputs_and_gets_no_note(self):
        def narrow(document):
            helper = next(s for s in document['signals'] if s['id'] == 'rcef.intermediate.viseme_pose_vowel_open')
            helper['domain'] = {'min': 0.0, 'max': 0.5}
        route = rcef_route.Route('vrm.preset', 'arkit.coefficient', pack=self.synthetic(narrow))
        presets = {f'vrm.preset.{p}': 0.0 for p in ('aa', 'ee', 'ih', 'oh', 'ou', 'blinkLeft', 'blinkRight')}
        refused, ran = route.translate([{'time': 0.0, 'values': {**presets, 'vrm.preset.aa': 1.0}, 'flags': {}},
                                        {'time': 0.1, 'values': {**presets, 'vrm.preset.aa': 0.25}, 'flags': {}}])
        self.assertEqual(refused['refused'][BRIDGE]['codes'], ['E_DOMAIN'])
        # Only the blinks, which VRM writes through its own in-map, still have values.
        self.assertEqual(refused['values'], {f'arkit.coefficient.eyeBlink{s}': 0.0 for s in ('Left', 'Right')})
        self.assertIn(f'refused upstream at {BRIDGE}', refused['labels'].values())
        self.assertEqual(refused['notes'], [])
        self.assertEqual(ran['refused'], {})
        self.assertEqual(len(ran['notes']), 1)
        self.assertTrue(ran['values'])


if __name__ == '__main__':
    unittest.main()
