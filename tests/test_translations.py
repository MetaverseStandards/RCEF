# SPDX-License-Identifier: MIT
"""Cross-provider translations checked against expectations derived from public sources.

The expected values come from tests/fixtures/fb2_goldens.json, which
scripts/derive_fb2_goldens.py derives from the pinned Godot, VRCFT, META and
VRM sources without reading RCEF's mapping data.
"""
import json
from pathlib import Path
import unittest

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = {
    'fb2.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
    'fb2_gaze.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
    'visemes.to_vrm': ('openxr.visemes', 'vrm.preset'),
}
KIND = {'fb2_to_arkit': ('fb2.to_arkit', 'fb2_gaze.to_arkit'), 'visemes_to_vrm': ('visemes.to_vrm',)}
SIDED = ('Left', 'Right', '_L_FB', '_R_FB')


class Translations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loaded = msf.load_authoring(ROOT)
        if loaded.value is None:
            raise AssertionError(loaded.report.to_dict())
        cls.document = loaded.value.to_dict()
        cls.pack = msf.compile_pack(loaded.value).value
        cls.compiled = {}
        for mapping, (source, target) in MAPPINGS.items():
            result = msf.compile_mapping(cls.pack, msf.profile_snapshot(cls.pack, source).value,
                                         msf.profile_snapshot(cls.pack, target).value, mapping, True)
            if result.value is None:
                raise AssertionError((mapping, result.report.to_dict()))
            cls.compiled[mapping] = result.value
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
        self.assertEqual(checked, self.outputs('fb2.to_arkit') | self.outputs('fb2_gaze.to_arkit'),
                         'every translated coefficient needs a source-derived vector')

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
                         ['arkit.coefficient.browInnerUp', 'arkit.coefficient.cheekPuff'])
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
