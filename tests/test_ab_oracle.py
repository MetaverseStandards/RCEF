# SPDX-License-Identifier: MIT
"""The A/B oracle (tests/ab_oracle.py) against msf-character-tools on today's direct maps and the pose bridge.

The oracle must give the same values, bit for bit, and the same refusals as
msf-character-tools on the A1 baseline for every edge input and for 1,000
random frames per source set, including gaze pairs that break FB2's
exclusivity. On the fixed impulse frames, the outputs it says change must be
the outputs that change in A1.

The viseme pose bridge (copy, weighted sum, clamp) is checked the same way:
alone against msf-character-tools, and inside the eight routes that run it
(META and VRM to ARKit, FB2, Unified Expressions and FACS) against Route, with
the zero-filled classes, their notes and the refusals upstream.

Partial evaluation, which Route uses, is checked against msf-character-tools'
partial mode on every in-map and out-map of the B pack: the written values,
bit for bit, and for each refused output its codes and references, and for
each output that is not available its missing inputs.
"""
from copy import deepcopy
import json
from pathlib import Path
import random
import struct
import sys
import unittest

import msf_character_tools as msf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
sys.path.insert(0, str(ROOT / 'scripts'))
import ab_frames  # noqa: E402
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

try:
    import ab_oracle
    import test_route_runner
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import ab_oracle, test_route_runner

FIXTURE = ROOT / 'tests/fixtures/baseline-dea1713.pack.json'
B_PACK = ROOT / 'generated/rcef.pack.json'
BRIDGE = 'rcef_viseme.to_rcef_expression'
VISEME, EXPRESSION = 'rcef.canonical_viseme', 'rcef.canonical_expression'
BRIDGE_SOURCES = {'META': 'openxr.visemes', 'VRM': 'vrm.preset'}
BRIDGE_TARGETS = {'ARKit': 'arkit.coefficient', 'FB2': 'openxr.fb2', 'VRCFT UE': 'vrcft.artist.base',
                  'FACS': 'facs.code'}
MAPS = {'fb2.to_arkit': ('openxr.fb2', 'arkit.coefficient'), 'fb2_gaze.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
        'arkit.to_fb2': ('arkit.coefficient', 'openxr.fb2'), 'arkit_gaze.to_fb2': ('arkit.coefficient', 'openxr.fb2'),
        'arkit.to_vrcft_artist': ('arkit.coefficient', 'vrcft.artist.base'), 'fb2.to_vrm': ('openxr.fb2', 'vrm.preset'),
        'visemes.to_vrm': ('openxr.visemes', 'vrm.preset')}
PAIRS = {'FB2 -> ARKit': ['fb2.to_arkit', 'fb2_gaze.to_arkit'], 'ARKit -> FB2': ['arkit.to_fb2', 'arkit_gaze.to_fb2'],
         'ARKit -> VRCFT UE': ['arkit.to_vrcft_artist'], 'FB2 -> VRM blink': ['fb2.to_vrm'],
         'META -> VRM': ['visemes.to_vrm']}
RANDOM_FRAMES = 1000
# The maps of the synthetic route pack (tests/test_route_runner.py).
IN, OUT = 'src.to_rcef_expression', 'rcef_expression.to_tgt'
ARKIT, FB2 = 'arkit.coefficient.{}', 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'


def bits(values):
    return {k: struct.pack('>d', v) for k, v in values.items()}


def msf_results(compiled, samples):
    """Per sample: (values, []) or (None, sorted (code, ref) pairs), from batched msf-character-tools calls."""
    outcome = msf.evaluate_mapping(compiled, samples)
    if outcome.ok:
        return [(dict(s['values']), []) for s in outcome.value.samples]
    results, refused = [None] * len(samples), {}
    for d in outcome.report.diagnostics:
        refused.setdefault(int(d.ref.split('/')[2]), []).append((d.code, d.ref))
    for n, diagnostics in refused.items():
        results[n] = (None, sorted(diagnostics))
    rest = [n for n in range(len(samples)) if n not in refused]
    if rest:
        again = msf.evaluate_mapping(compiled, [samples[n] for n in rest])
        assert again.ok, again.report.to_dict()
        for n, sample in zip(rest, again.value.samples):
            results[n] = (dict(sample['values']), [])
    return results


class OracleMatchesMsf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)
        cls.sources = {p: ab_frames.pinned_source(cls.document, p)
                       for p in ('openxr.fb2', 'arkit.coefficient', 'openxr.visemes')}
        cls.compiled = {}
        for mapping, (source, target) in MAPS.items():
            snapshots = [msf.profile_snapshot(cls.pack, p).value for p in (source, target)]
            cls.compiled[mapping] = msf.compile_mapping(cls.pack, *snapshots, mapping, True).value

    def compare(self, mapping, frames):
        source, target = MAPS[mapping]
        required = self.compiled[mapping].required_inputs
        samples = [{'timestamp': 0.0, 'values': {s: f['values'][s] for s in required},
                    'validity': {s: self.oracle.valid(s, f['flags']) for s in required}} for f in frames]
        expected = msf_results(self.compiled[mapping], samples)
        mismatches, refused = [], 0
        for n, (sample, (values, diagnostics)) in enumerate(zip(samples, expected)):
            got, got_diagnostics = self.oracle.frame(mapping, source, target, sample['values'], sample['validity'], n)
            refused += values is None
            if (got is None) != (values is None) or got_diagnostics != diagnostics or (
                    got is not None and bits(got) != bits(values)):
                mismatches.append((frames[n]['label'], diagnostics, got_diagnostics))
        self.assertEqual(mismatches[:3], [], f'{mapping}: {len(mismatches)} frames differ')
        return refused

    def test_every_edge_input_on_every_a1_map(self):
        refused = {}
        for mapping, (source, _) in MAPS.items():
            with self.subTest(mapping):
                refused[mapping] = self.compare(mapping, ab_frames.edge_family('edge', self.sources[source]))
        # Products such as 0.5 * 5e-324 underflow, so the edge set is refused somewhere on every map that averages.
        self.assertGreater(refused['fb2.to_arkit'], 0)

    def test_random_frames_on_every_a1_map(self):
        for mapping, (source, _) in MAPS.items():
            with self.subTest(mapping):
                rng = random.Random(f'ab_oracle {mapping}')
                spec = {'name': 'random', 'count': RANDOM_FRAMES, 'range': [0.0, 1.0]}
                self.compare(mapping, ab_frames.uniform_family(spec, self.sources[source], rng))

    def test_gaze_pairs_that_break_exclusivity_keep_only_the_difference(self):
        def look(**values):
            frame = {**dict.fromkeys(self.compiled['arkit_gaze.to_fb2'].required_inputs, 0.0),
                     **{ARKIT.format(k): v for k, v in values.items()}}
            return self.oracle.frame('arkit_gaze.to_fb2', *MAPS['arkit_gaze.to_fb2'], frame, dict.fromkeys(frame, True))
        cases = {(0.3, 0.1): {'EYES_LOOK_RIGHT_L': 0.19999999999999998},
                 (0.1, 0.3): {'EYES_LOOK_LEFT_L': 0.19999999999999996},
                 (0.3, 0.3): {}, (1.0, 1.0): {}, (0.3, 0.0): {'EYES_LOOK_RIGHT_L': 0.3}}
        for (inward, outward), written in cases.items():
            with self.subTest(inward=inward, outward=outward):
                values, diagnostics = look(eyeLookInLeft=inward, eyeLookOutLeft=outward)
                self.assertEqual(diagnostics, [])
                self.assertEqual({k: v for k, v in values.items() if v}, {FB2.format(k): v for k, v in written.items()})
        frames = [f for f in ab_frames.edge_family('edge', self.sources['arkit.coefficient'])
                  if ', ' in f['label']]
        self.assertEqual(len(frames), 4 * 4)
        self.compare('arkit_gaze.to_fb2', frames)


class Refusals(unittest.TestCase):
    """Every refusal the oracle reproduces, against msf-character-tools on the synthetic route pack.

    Codes and references are compared in full, so one check cannot hide
    another: an out-of-range input that the oracle failed to refuse would show
    up as a rule's output E_DOMAIN with a different reference.
    """

    @classmethod
    def setUpClass(cls):
        document = test_route_runner.synthetic_document()
        rule = deepcopy(document['mappings'][1]['rules'][0])
        extra = {'src_big.to_tgt': (['src.brow_l', 'src.brow_r'], 'tgt.big', {'id': 'weighted_sum',
                                                                             'weights': [1e308, 1e308]}),
                 'src_knee.to_tgt': (['src.jaw'], 'tgt.knee', {'id': 'piecewise_linear', 'knots': [
                     [0.0, 1.0], [0.2, 0.68], [0.88, 0.08], [1.0, 0.0]]})}
        for mapping, (inputs, output, operator) in extra.items():
            document['mappings'].append({'id': mapping, 'rules': [{
                **rule, 'id': mapping, 'inputs': inputs, 'outputs': [output], 'operator': operator,
                'loss_annotations': [{**rule['loss_annotations'][0], 'refs': inputs + [output]}]}]})
        tgt = next(p for p in document['profiles'] if p['id'] == 'tgt')
        for sid, domain in (('tgt.big', {}), ('tgt.knee', {'min': 0.0, 'max': 1.0})):
            document['signals'].append({**document['signals'][-1], 'id': sid, 'label': sid, 'domain': domain})
            tgt['signal_ids'].append(sid)
        cls.oracle = ab_oracle.Oracle(document)
        cls.pack = rcef_translate.load_pack(document)

    def check(self, mapping, source, target, values, validity):
        snapshots = [msf.profile_snapshot(self.pack, p).value for p in (source, target)]
        compiled = msf.compile_mapping(self.pack, *snapshots, mapping, True).value
        outcome = msf.evaluate_mapping(compiled, [{'timestamp': 0.0, 'values': values, 'validity': validity}])
        expected = (dict(outcome.value.samples[0]['values']), []) if outcome.ok else (
            None, sorted((d.code, d.ref) for d in outcome.report.diagnostics))
        got = self.oracle.frame(mapping, source, target, values, validity)
        self.assertEqual(got[1], expected[1])
        self.assertEqual(got[0] is None, expected[0] is None)
        if got[0] is not None:
            self.assertEqual(bits(got[0]), bits(expected[0]))
        return expected

    def partial(self, mapping, source, target, values, validity):
        """msf-character-tools' partial evaluation of one frame as (written, refused, unavailable), as O gives it."""
        snapshots = [msf.profile_snapshot(self.pack, p).value for p in (source, target)]
        compiled = msf.compile_mapping(self.pack, *snapshots, mapping, True).value
        outcome = msf.evaluate_mapping(compiled, [{'timestamp': 0.0, 'values': values, 'validity': validity}],
                                       partial=True)
        self.assertTrue(outcome.ok, outcome.report.to_dict())
        return (dict(outcome.value.samples[0]['values']),
                {r['output']: sorted((d.code, d.ref) for d in r['diagnostics']) for r in outcome.value.refusals},
                {r['output']: sorted(r['inputs']) for r in outcome.value.unavailable})

    def test_each_refusal_and_the_clamp_match_msf(self):
        c = 'rcef.canonical_expression.'
        full = {'src.brow_l': 0.25, 'src.brow_r': 0.75, 'src.jaw': 0.25, 'src.eye': 0.5, 'src.tongue': 0.0}
        valid = dict.fromkeys(full, True)
        canonical = {c + n: 0.25 for n in ('brow_left', 'brow_right', 'jaw', 'eye', 'cheek')}
        cases = {
            'cleared flag': (IN, 'src', 'rcef.canonical_expression', {**full, 'src.eye': 0.5},
                             {**valid, 'src.eye': False}, 'E_INVALID_SAMPLE'),
            'missing input': (IN, 'src', 'rcef.canonical_expression', {'src.brow_l': 0.5},
                              {'src.brow_l': True}, 'E_MISSING_SAMPLE'),
            'input above its domain': (IN, 'src', 'rcef.canonical_expression', {**full, 'src.jaw': 1.5},
                                       valid, 'E_DOMAIN'),
            'output above its domain': (OUT, 'rcef.canonical_expression', 'tgt', {**canonical, c + 'jaw': 0.75},
                                        dict.fromkeys(canonical, True), 'E_DOMAIN'),
            'out-of-range input of an out-map': (OUT, 'rcef.canonical_expression', 'tgt',
                                                 {**canonical, c + 'jaw': 1.5}, dict.fromkeys(canonical, True),
                                                 'E_DOMAIN'),
            'cleared flag and out of range': (IN, 'src', 'rcef.canonical_expression', {**full, 'src.eye': 1.5},
                                              {**valid, 'src.eye': False}, 'E_DOMAIN'),
            'sum overflows': ('src_big.to_tgt', 'src', 'tgt', {'src.brow_l': 1.0, 'src.brow_r': 1.0},
                              {'src.brow_l': True, 'src.brow_r': True}, 'E_NONFINITE'),
        }
        for name, (mapping, source, target, values, validity, code) in cases.items():
            with self.subTest(name):
                _, diagnostics = self.check(mapping, source, target, values, validity)
                self.assertEqual({d[0] for d in diagnostics}, {code})
                expected = self.partial(mapping, source, target, values, validity)
                written, refused, unavailable = self.oracle.partial(mapping, source, target, values, validity)
                self.assertEqual((bits(written), refused, unavailable), (bits(expected[0]), *expected[1:]))
                self.assertTrue(refused or unavailable)
                self.assertTrue(written or mapping == 'src_big.to_tgt')
        # t rounds to 1 on the segment [0.2, 0.88], so ya + t * (yb - ya) is just below yb until it is clamped.
        values, _ = self.check('src_knee.to_tgt', 'src', 'tgt', {'src.jaw': 0.8799999999999999},
                               {'src.jaw': True})
        self.assertEqual(values, {'tgt.knee': 0.08})

    def test_route_refusals_and_labels_match_the_oracle_route(self):
        route = rcef_route.Route('src', 'tgt', pack=self.pack)
        in_hops = [(m, d) for m, _, d in route.hops if m in route.in_maps]
        out_hops = [(m, s) for m, s, _ in route.hops if m in route.out_maps]
        base = {'src.brow_l': 0.25, 'src.brow_r': 0.75, 'src.jaw': 0.25, 'src.eye': 0.5}
        flags = {'isValid': True, 'isEyeValid': True}
        frames = [(base, {**flags, 'isEyeValid': False}), ({k: v for k, v in base.items() if k != 'src.jaw'}, flags),
                  ({**base, 'src.jaw': 1.5}, flags), ({**base, 'src.jaw': 0.75}, flags),
                  ({**base, 'src.eye': 1.5}, {**flags, 'isEyeValid': False})]
        frames += [({**base, 'src.brow_l': 1.5}, flags),
                   ({k: v for k, v in base.items() if k != 'src.brow_r'} | {'src.brow_l': 1.5}, flags)]
        results = route.translate([{'time': 0.0, 'values': v, 'flags': f} for v, f in frames])
        for (values, frame_flags), result in zip(frames, results):
            expected = self.oracle.route('src', 'tgt', in_hops, out_hops, values, frame_flags)
            self.assertEqual(result['refused'], expected['refused'])
            self.assertEqual(result['labels'], expected['labels'])
            self.assertEqual(bits(result['values']), bits(expected['values']))
        self.assertEqual(results[2]['refused'], {IN: {'codes': ['E_DOMAIN'], 'refs': ['src.jaw'],
                                                      'outputs': ['rcef.canonical_expression.jaw']}})
        self.assertEqual(results[1]['labels']['tgt.jaw'], rcef_route.NOT_AVAILABLE)
        self.assertEqual(results[5]['labels']['tgt.brow'], f'refused upstream at {IN}')
        self.assertEqual(results[6]['labels']['tgt.brow'], rcef_route.NOT_AVAILABLE)


class PartialMatchesMsf(unittest.TestCase):
    """O's partial evaluation against msf-character-tools' on every in-map and out-map of the B pack."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(B_PACK.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)
        profiles = {p['id']: set(p['signal_ids']) for p in cls.document['profiles']}
        cls.hops = []
        for mapping in cls.document['mappings']:
            if all(r['disposition'] == 'unresolved' for r in mapping['rules']):
                continue  # a record, such as survey.ambiguous: msf-character-tools never compiles it
            inputs, outputs = rcef_route.map_ends(mapping['rules'])
            ends = [next((p for p, members in profiles.items() if p != 'rcef.intermediate' and set(sids) <= members),
                         None) for sids in (inputs, outputs)]
            if None not in ends and (VISEME in ends or EXPRESSION in ends) and len(set(ends)) == 2:
                cls.hops.append((mapping['id'], *ends))

    def test_every_hop_map_on_frames_with_bad_and_missing_inputs(self):
        self.assertEqual(len(self.hops), 16)
        seen = {'written': 0, 'refused': 0, 'unavailable': 0}
        for mapping, source, target in self.hops:
            snapshots = [msf.profile_snapshot(self.pack, p).value for p in (source, target)]
            compiled = msf.compile_mapping(self.pack, *snapshots, mapping, True).value
            required = list(compiled.required_inputs)
            rng = random.Random(f'partial {mapping}')
            samples = []
            for n in range(60):
                values = {s: rng.choice((0.0, 0.25, 1.0, rng.random(), 1.5, -0.1, 5e-324)) for s in required}
                validity = {s: rng.random() > 0.1 for s in required}
                for s in rng.sample(required, min(len(required), n % 4)):
                    del values[s], validity[s]
                samples.append({'timestamp': 0.0, 'values': values, 'validity': validity})
            outcome = msf.evaluate_mapping(compiled, samples, partial=True)
            self.assertTrue(outcome.ok, outcome.report.to_dict())
            refusals, unavailable = {}, {}
            for row in outcome.value.refusals:
                refusals.setdefault(row['sample'], {})[row['output']] = sorted((d.code, d.ref) for d in row['diagnostics'])
            for row in outcome.value.unavailable:
                unavailable.setdefault(row['sample'], {})[row['output']] = sorted(row['inputs'])
            with self.subTest(mapping=mapping):
                for n, (sample, written) in enumerate(zip(samples, outcome.value.samples)):
                    got = self.oracle.partial(mapping, source, target, sample['values'], sample['validity'], n)
                    self.assertEqual(bits(got[0]), bits(dict(written['values'])), n)
                    self.assertEqual(got[1], refusals.get(n, {}), n)
                    self.assertEqual(got[2], unavailable.get(n, {}), n)
                    seen['written'] += bool(got[0])
                    seen['refused'] += bool(got[1])
                    seen['unavailable'] += bool(got[2])
        self.assertTrue(all(seen.values()), seen)


class ImpulseLinks(unittest.TestCase):
    """O's changed-output sets on the impulse frames equal A1's, run through Route's one-hop mode."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)

    def test_changed_outputs_match_on_every_a1_pair(self):
        links = {}
        for pair, maps in PAIRS.items():
            source, target = MAPS[maps[0]]
            frames = ab_frames.impulse_family('impulse', ab_frames.pinned_source(self.document, source))
            route = rcef_route.Route(source, target, pack=self.pack, maps=maps)
            actual = route.translate([{**f, 'time': 0.0} for f in frames])
            expected = [self.oracle.route(source, target, [], [(m, None) for m in maps], f['values'], f['flags'])
                        for f in frames]
            with self.subTest(pair):
                for frame, a, e in zip(frames, actual, expected):
                    self.assertEqual(bits(a['values']), bits(e['values']), frame['label'])
                    self.assertEqual(a['refused'], e['refused'], frame['label'])
                for frame, a in zip(frames[1:], actual[1:]):
                    links[pair, frame['label']] = ab_oracle.changed(actual[0], a)
                    self.assertEqual(links[pair, frame['label']], ab_oracle.changed(expected[0], self.oracle.route(
                        source, target, [], [(m, None) for m in maps], frame['values'], frame['flags'])))
        # The weight-linked LOOK_RIGHT_L stays 0: eyeLookOutLeft enters its knots on the flat side.
        self.assertEqual(links['ARKit -> FB2', f'{ARKIT.format("eyeLookOutLeft")} 1.0'],
                         {FB2.format('EYES_LOOK_LEFT_L')})


class PoseBridge(unittest.TestCase):
    """The pose bridge hop: O against msf-character-tools alone, and O's routes against Route on the bridge pairs."""

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(B_PACK.read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.oracle = ab_oracle.Oracle(cls.document)
        snapshots = [msf.profile_snapshot(cls.pack, p).value for p in (VISEME, EXPRESSION)]
        cls.compiled = msf.compile_mapping(cls.pack, *snapshots, BRIDGE, True).value

    def test_the_bridge_alone_matches_msf_on_edge_random_and_simplex_frames(self):
        source = {'channels': list(self.compiled.required_inputs), 'flags': [], 'gaze_pairs': []}
        rng = random.Random('ab_oracle pose bridge')
        frames = (ab_frames.edge_family('edge', source)
                  + ab_frames.uniform_family({'name': 'random', 'count': RANDOM_FRAMES, 'range': [0.0, 1.0]}, source,
                                             rng)
                  + ab_frames.simplex_family({'name': 'simplex', 'count': 500, 'decimals': 6}, source, rng))
        samples = [{'timestamp': 0.0, 'values': f['values'], 'validity': dict.fromkeys(f['values'], True)}
                   for f in frames]
        mismatches, refused, clamped = [], 0, 0
        for n, (sample, (values, diagnostics)) in enumerate(zip(samples, msf_results(self.compiled, samples))):
            got, got_diagnostics = self.oracle.frame(BRIDGE, VISEME, EXPRESSION, sample['values'],
                                                     sample['validity'], n)
            refused += values is None
            clamped += values is not None and 1.0 in values.values()
            if got_diagnostics != diagnostics or (got is None) != (values is None) or (
                    got is not None and bits(got) != bits(values)):
                mismatches.append((frames[n]['label'], diagnostics, got_diagnostics))
        self.assertEqual(mismatches[:3], [], f'{len(mismatches)} frames differ')
        # 5e-324 times a weight below 1 underflows, so the edge set refuses the bridge itself; the random frames
        # reach the clamp at 1.
        self.assertGreater(refused, 0)
        self.assertGreater(clamped, 0)

    def test_every_bridge_route_matches_route_with_its_zero_fill_notes_and_refusals(self):
        seen = {'bridge refused': 0, 'blocked upstream': 0, 'refused at the bridge': 0, 'zero-fill notes': 0}
        for (s, source), (t, target) in [(a, b) for a in BRIDGE_SOURCES.items() for b in BRIDGE_TARGETS.items()]:
            route = rcef_route.Route(source, target, pack=self.pack)
            self.assertEqual(route.bridges, [BRIDGE])
            in_hops = [(m, d) for m, _, d in route.hops if m in route.in_maps]
            bridges = [(m, a, b) for m, a, b in route.hops if m in route.bridges]
            out_hops = [(m, a) for m, a, _ in route.hops if m in route.out_maps]
            pinned = ab_frames.pinned_source(self.document, source)
            rng = random.Random(f'ab_oracle {s} -> {t}')
            frames = ab_frames.edge_family('edge', pinned) + ab_frames.uniform_family(
                {'name': 'random', 'count': 300, 'range': [-0.2, 1.2]}, pinned, rng)
            results = route.translate([{**f, 'time': 0.0} for f in frames])
            with self.subTest(pair=f'{s} -> {t}'):
                for frame, result in zip(frames, results):
                    expected = self.oracle.route(source, target, in_hops, out_hops, frame['values'], frame['flags'],
                                                 bridges)
                    self.assertEqual(bits(result['values']), bits(expected['values']), frame['label'])
                    self.assertEqual(result['refused'], expected['refused'], frame['label'])
                    self.assertEqual(result['labels'], expected['labels'], frame['label'])
                    self.assertEqual(result['notes'], expected['notes'], frame['label'])
                    labels = set(expected['labels'].values())
                    seen['bridge refused'] += BRIDGE in expected['refused']
                    seen['refused at the bridge'] += f'refused upstream at {BRIDGE}' in labels
                    seen['blocked upstream'] += any(x.startswith('refused upstream at') and BRIDGE not in x
                                                    for x in labels)
                    seen['zero-fill notes'] += any('counted as 0' in n for n in expected['notes'])
        self.assertTrue(all(seen.values()), seen)

    def test_classes_no_in_map_writes_count_as_zero_and_the_frame_says_which(self):
        route = rcef_route.Route('vrm.preset', 'arkit.coefficient', pack=self.pack)
        in_hops = [(m, d) for m, _, d in route.hops if m in route.in_maps]
        bridges = [(m, a, b) for m, a, b in route.hops if m in route.bridges]
        out_hops = [(m, a) for m, a, _ in route.hops if m in route.out_maps]
        values = {**dict.fromkeys(ab_frames.pinned_source(self.document, 'vrm.preset')['channels'], 0.0),
                  'vrm.preset.aa': 1.0}
        expected = self.oracle.route('vrm.preset', 'arkit.coefficient', in_hops, out_hops, values, {}, bridges)
        # VRM's five vowels fill five classes; the other six bridge inputs have no VRM source.
        self.assertEqual(expected['notes'], [f'bridge {BRIDGE}: the source writes no alveolar_sibilant, bilabial, '
                                             'coronal_stop, dental, dorsal, sil; counted as 0'])
        self.assertGreater(expected['values']['arkit.coefficient.jawOpen'], 0.0)
        result = route.translate([{'time': 0.0, 'values': values, 'flags': {}}])[0]
        self.assertEqual((result['notes'], bits(result['values'])), (expected['notes'], bits(expected['values'])))


if __name__ == '__main__':
    unittest.main()
