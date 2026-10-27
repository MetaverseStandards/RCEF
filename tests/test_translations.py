# SPDX-License-Identifier: MIT
"""Cross-provider translations checked against expectations derived from public sources.

The expected values come from tests/fixtures/fb2_goldens.json, which
scripts/derive_fb2_goldens.py derives from the pinned Godot, VRCFT, META and
VRM sources without reading RCEF's mapping data.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

import msf_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = {
    'fb2.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
    'fb2_gaze.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
    'visemes.to_vrm': ('openxr.visemes', 'vrm.preset'),
    'arkit.to_fb2': ('arkit.coefficient', 'openxr.fb2'),
    'arkit_gaze.to_fb2': ('arkit.coefficient', 'openxr.fb2'),
    'arkit.to_vrcft_artist': ('arkit.coefficient', 'vrcft.artist.base'),
}
KIND = {'fb2_to_arkit': ('fb2.to_arkit', 'fb2_gaze.to_arkit'), 'visemes_to_vrm': ('visemes.to_vrm',),
        'arkit_to_fb2': ('arkit.to_fb2', 'arkit_gaze.to_fb2'), 'arkit_to_ue': ('arkit.to_vrcft_artist',)}
SIDED = ('Left', 'Right', '_L_FB', '_R_FB')


class Translations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = shared_pack.document()
        cls.pack = shared_pack.pack()
        cls.compiled = {m: shared_pack.mapping(m, s, t) for m, (s, t) in MAPPINGS.items()}
        cls.goldens = json.loads((ROOT / 'tests/fixtures/fb2_goldens.json').read_text())

    def rules(self, mapping):
        return next(m['rules'] for m in self.document['mappings'] if m['id'] == mapping)

    def inputs(self, mapping):
        return {i for rule in self.rules(mapping) for i in rule['inputs']}

    def outputs(self, mapping):
        return {o for rule in self.rules(mapping) for o in rule['outputs']}

    def run_frame(self, mapping, values, validity=None):
        frame = {'timestamp': 0.0, 'values': values,
                 'validity': validity if validity is not None else dict.fromkeys(values, True)}
        return msf.evaluate_mapping(self.compiled[mapping], [frame])

    def evaluate(self, mapping, frames):
        """Output values for each frame; a frame holds every input, zero unless given.

        msf-tools rechecks the whole pack on every call, so the frames, which are
        independent, go in one call.
        """
        zero = dict.fromkeys(self.inputs(mapping), 0.0)
        for values in frames:
            self.assertLessEqual(set(values), set(zero))
        samples = [{'timestamp': 0.0, 'values': {**zero, **values}, 'validity': dict.fromkeys(zero, True)}
                   for values in frames]
        result = msf.evaluate_mapping(self.compiled[mapping], samples)
        self.assertIsNotNone(result.value, result.report.to_dict())
        return [sample['values'] for sample in result.value.samples]

    def test_fb2_rules_match_source_derived_vectors(self):
        checked = set()
        for mapping in KIND['fb2_to_arkit']:
            cases = [c for c in self.goldens['cases'] if c['mapping_kind'] == 'fb2_to_arkit'
                     and set(c['expected']) <= self.outputs(mapping)]
            for case in cases:
                self.assertLessEqual(set(case['inputs']), self.inputs(mapping),
                                     f'RCEF and the sources use different inputs ({case["sources"]})')
            results = self.evaluate(mapping, [c['inputs'] for c in cases])
            for case, values in zip(cases, results):
                (target, expected), = case['expected'].items()
                with self.subTest(target=target, inputs=case['inputs']):
                    self.assertEqual(values[target], expected, case['sources'])
                    checked.add(target)
        expected = {o for c in self.goldens['cases'] if c['mapping_kind'] == 'fb2_to_arkit' for o in c['expected']}
        self.assertEqual(checked, expected, 'every coefficient the sources route needs a rule, and only those')

    def whole_frames(self, kind):
        """The golden frames that set every input at once, each to its own value."""
        frames = [c for c in self.goldens['cases'] if c['mapping_kind'] == kind and len(c['inputs']) > 4
                  or c['mapping_kind'] == kind == 'fb2_to_vrm']
        self.assertEqual(len(frames), 2, kind)
        return frames

    def check_whole_frames(self, kind, compiled=None):
        """Per output: True if it matches the golden value in every whole frame."""
        matches = {}
        for mapping in KIND[kind]:
            frames = self.whole_frames(kind)
            inputs = self.inputs(mapping)
            samples = [{'timestamp': 0.0, 'values': {k: v for k, v in f['inputs'].items() if k in inputs},
                        'validity': dict.fromkeys(inputs, True)} for f in frames]
            result = msf.evaluate_mapping((compiled or self.compiled)[mapping], samples)
            self.assertIsNotNone(result.value, result.report.to_dict())
            for frame, sample in zip(frames, result.value.samples):
                for output in self.outputs(mapping):
                    matches[output] = matches.get(output, True) and sample['values'][output] == frame['expected'][output]
        return matches

    def test_whole_frames_match_the_sources(self):
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            with self.subTest(kind):
                matches = self.check_whole_frames(kind)
                expected = set(self.whole_frames(kind)[0]['expected'])
                self.assertEqual(set(matches), expected)
                self.assertEqual([o for o, ok in matches.items() if not ok], [])

    def changed_copies(self, kind, change):
        """Each mapping of `kind` compiled from a small copy of the pack in which `change` has edited every rule."""
        compiled = {}
        for mapping in KIND[kind]:
            source, target = MAPPINGS[mapping]
            document = deepcopy(self.document)
            rules = next(m for m in document['mappings'] if m['id'] == mapping)['rules']
            members = {sid for r in rules for sid in r['inputs'] + r['outputs']}
            profiles = [{**p, 'signal_ids': [sid for sid in p['signal_ids'] if sid in members]}
                        for p in document['profiles'] if p['id'] in (source, target)]
            signals = [x for x in document['signals'] if x['id'] in members]
            cited = {e for record in profiles + signals + rules for e in record.get('evidence', [])}
            change(rules)
            small = {**document, 'profiles': profiles, 'signals': signals,
                     'mappings': [m for m in document['mappings'] if m['id'] == mapping],
                     'evidence': [e for e in document['evidence'] if e['id'] in cited]}
            authored = msf.validate_authoring(small)
            self.assertTrue(authored.ok, authored.report.to_dict())
            pack = msf.compile_pack(authored.value).value
            result = msf.compile_mapping(pack, msf.profile_snapshot(pack, source).value,
                                         msf.profile_snapshot(pack, target).value, mapping, True)
            self.assertIsNotNone(result.value, result.report.to_dict())
            compiled[mapping] = result.value
        return compiled

    def test_halving_every_rule_changes_every_output(self):
        # Each rule writes one output and reads no other rule's output, so halving
        # them all at once and checking each output is the same as halving one at a time.
        def halve(rules):
            for rule in rules:
                operator = rule['operator']
                if operator['id'] == 'affine':
                    operator['scale'] *= 0.5
                else:
                    operator['weights'] = [w * 0.5 for w in operator['weights']]
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            with self.subTest(kind):
                matches = self.check_whole_frames(kind, self.changed_copies(kind, halve))
                self.assertEqual([o for o, ok in matches.items() if ok], [])

    def test_swapping_every_left_and_right_rule_changes_both_outputs(self):
        def side_free(sid):
            return re.sub(r'(Left|Right)$|_[LR](?=[TB]?_FB$)|_(LEFT|RIGHT)(?=_FB$)', '#', sid)

        def swap(rules):
            by_key = {}
            for rule in rules:
                by_key.setdefault(side_free(rule['outputs'][0]), []).append(rule)
            for pair in by_key.values():
                if len(pair) == 2:
                    pair[0]['inputs'], pair[1]['inputs'] = pair[1]['inputs'], pair[0]['inputs']
        for kind in KIND:
            if kind == 'visemes_to_vrm':
                continue
            with self.subTest(kind):
                swapped = set()
                for mapping in KIND[kind]:
                    pairs = {}
                    for rule in self.rules(mapping):
                        pairs.setdefault(side_free(rule['outputs'][0]), []).append(rule)
                    # A copied composite feeds both sides from one input; swapping changes nothing there.
                    swapped |= {r['outputs'][0] for pair in pairs.values() if len(pair) == 2
                                and pair[0]['inputs'] != pair[1]['inputs'] for r in pair}
                self.assertTrue(swapped)
                matches = self.check_whole_frames(kind, self.changed_copies(kind, swap))
                self.assertEqual(sorted(o for o in swapped if matches[o]), [])

    def test_fb2_to_arkit_after_arkit_to_fb2_returns_every_coefficient(self):
        frames = self.whole_frames('arkit_to_fb2')
        for frame in frames:
            fb2 = {}
            for mapping in KIND['arkit_to_fb2']:
                inputs = self.inputs(mapping)
                values, = self.evaluate(mapping, [{k: v for k, v in frame['inputs'].items() if k in inputs}])
                fb2.update(values)
            arkit = {}
            for mapping in KIND['fb2_to_arkit']:
                values, = self.evaluate(mapping, [{k: v for k, v in fb2.items() if k in self.inputs(mapping)}])
                arkit.update(values)
            self.assertEqual(arkit, frame['inputs'])

    def test_inverse_gaze_declares_that_fb2_exclusivity_cannot_be_enforced(self):
        rules = self.rules('arkit_gaze.to_fb2')
        self.assertEqual(len(rules), 8)
        for rule in rules:
            with self.subTest(rule['id']):
                self.assertTrue(any('exclusive' in loss['reason'] and 'operator gap' in loss['reason']
                                    for loss in rule['loss_annotations']))
        self.assertFalse(self.inputs('arkit_gaze.to_fb2') & self.inputs('arkit.to_fb2'))

    def test_vrcft_composites_of_the_copied_parts_return_the_arkit_value(self):
        # VRCFT's BrowDown is 0.75 BrowLowerer + 0.25 BrowPinch and its MouthSmile 0.8
        # CornerPull + 0.2 CornerSlant; its other blended shapes are means of their parts.
        frame = self.whole_frames('arkit_to_ue')[0]
        values, = self.evaluate('arkit.to_vrcft_artist', [frame['inputs']])
        ue = 'vrcft.artist.base.{}'.format
        for side in ('Left', 'Right'):
            down = 0.75 * values[ue(f'BrowLowerer{side}')] + 0.25 * values[ue(f'BrowPinch{side}')]
            smile = 0.8 * values[ue(f'MouthCornerPull{side}')] + 0.2 * values[ue(f'MouthCornerSlant{side}')]
            self.assertAlmostEqual(down, frame['inputs'][f'arkit.coefficient.browDown{side}'], places=12)
            self.assertAlmostEqual(smile, frame['inputs'][f'arkit.coefficient.mouthSmile{side}'], places=12)
        funnel = sum(values[ue(f'LipFunnel{p}')] for p in ('UpperLeft', 'UpperRight', 'LowerLeft', 'LowerRight')) / 4
        self.assertEqual(funnel, frame['inputs']['arkit.coefficient.mouthFunnel'])

    def test_viseme_rules_match_source_derived_vectors_and_drop_consonants(self):
        case, = (c for c in self.goldens['cases'] if c['mapping_kind'] == 'visemes_to_vrm')
        inputs = self.inputs('visemes.to_vrm')
        kept = {k: v for k, v in case['inputs'].items() if k in inputs}
        dropped = sum(v for k, v in case['inputs'].items() if k not in inputs)
        self.assertEqual(sum(case['inputs'].values()), 1.0)  # a valid META frame
        self.assertGreater(dropped, 0.0)
        outputs, = self.evaluate('visemes.to_vrm', [kept])
        self.assertEqual(dict(outputs), case['expected'])
        self.assertEqual(sum(outputs.values()) + dropped, 1.0, 'the probability lost is the consonant mass')

    def test_averaged_pairs_lose_exactly_half_the_difference(self):
        averaged = [r for r in self.rules('fb2.to_arkit') if r['operator']['id'] == 'weighted_sum']
        self.assertEqual(sorted(r['outputs'][0] for r in averaged),
                         [f'arkit.coefficient.{n}' for n in ('browInnerUp', 'cheekPuff', 'mouthFunnel', 'mouthPucker',
                                                             'mouthRollLower', 'mouthRollUpper')])
        funnel, = (r for r in averaged if len(r['inputs']) == 4)
        self.assertEqual(funnel['operator']['weights'], [0.25] * 4)
        averaged = [r for r in averaged if len(r['inputs']) == 2]
        levels = (0.0, 0.25, 0.5, 0.75, 1.0)
        for rule in averaged:
            left, right = rule['inputs']
            output = rule['outputs'][0]
            pairs = [(a, b) for a in levels for b in levels]
            results = self.evaluate('fb2.to_arkit', [{left: a, right: b} for a, b in pairs])
            for (a, b), values in zip(pairs, results):
                with self.subTest(output=output, left=a, right=b):
                    # Driving both halves with the one value misses each by |L - R| / 2.
                    self.assertEqual(abs(values[output] - a), abs(a - b) / 2)
                    self.assertEqual(abs(values[output] - b), abs(a - b) / 2)
            losses = [loss.to_dict() for loss in self.compiled['fb2.to_arkit'].losses]
            self.assertTrue(any(loss['reason'] == 'asymmetry irrecoverable'
                                and set(loss['refs']) == {left, right, output} for loss in losses), output)

    def test_face_valid_gaze_invalid_frame_keeps_face_outputs(self):
        # FB2 may report the face valid while eye following is not; the eight gaze
        # weights are then zero and their validity false.
        gaze = self.inputs('fb2_gaze.to_arkit')
        face = self.inputs('fb2.to_arkit')
        self.assertFalse(gaze & face)
        values = {**dict.fromkeys(face, 0.5), **dict.fromkeys(gaze, 0.0)}
        validity = {**dict.fromkeys(face, True), **dict.fromkeys(gaze, False)}
        for mapping, inputs in (('fb2.to_arkit', face), ('fb2_gaze.to_arkit', gaze)):
            result = self.run_frame(mapping, {k: values[k] for k in inputs}, {k: validity[k] for k in inputs})
            if mapping == 'fb2.to_arkit':
                self.assertIsNotNone(result.value, result.report.to_dict())
                self.assertEqual(set(result.value.samples[0]['values']), self.outputs(mapping))
                self.assertEqual(result.value.samples[0]['values']['arkit.coefficient.eyeBlinkLeft'], 0.5)
            else:
                self.assertIsNone(result.value)
                self.assertEqual({d.code for d in result.report.diagnostics}, {'E_INVALID_SAMPLE'})
        # msf-tools refuses any supplied channel marked invalid, even one the mapping
        # does not use, so consumers must give each mapping only its own inputs.
        result = self.run_frame('fb2.to_arkit', values, validity)
        self.assertIsNone(result.value)
        self.assertEqual({d.code for d in result.report.diagnostics}, {'E_INVALID_SAMPLE'})
        self.assertEqual({d.ref.rsplit('/', 1)[-1] for d in result.report.diagnostics}, gaze)

    def test_translations_need_the_approximation_opt_in(self):
        for mapping, (source, target) in MAPPINGS.items():
            with self.subTest(mapping=mapping):
                result = msf.compile_mapping(self.pack, msf.profile_snapshot(self.pack, source).value,
                                             msf.profile_snapshot(self.pack, target).value, mapping)
                self.assertIsNone(result.value)
                self.assertIn('E_APPROXIMATION', {d.code for d in result.report.diagnostics})

    def test_every_rule_is_proposed_with_two_sources_assumptions_and_losses(self):
        for mapping in MAPPINGS:
            for rule in self.rules(mapping):
                with self.subTest(rule=rule['id']):
                    self.assertEqual((rule['evidence_status'], rule['mapping_quality'], rule['disposition']),
                                     ('proposed', 'approximate', 'mapped'))
                    self.assertGreaterEqual(len(set(rule['evidence'])), 2)
                    self.assertTrue(rule['assumptions'])
                    self.assertTrue(rule['loss_annotations'])
                    if any(s in sid for sid in (*rule['inputs'], *rule['outputs']) for s in SIDED):
                        self.assertTrue(any("subject's own face" in a for a in rule['assumptions']),
                                        'left/right rules state the side convention')


if __name__ == '__main__':
    unittest.main()
