# SPDX-License-Identifier: MIT
"""Round trip through the one-to-one translations and back.

The way back is built in this test only, from the source-derived routes in
tests/fixtures/godot_fb2_rules.csv and the viseme pairs in
tests/fixtures/fb2_goldens.json, read in reverse. It is not built by
inverting RCEF's own rules, so it checks the rules against the sources.
Averaged pairs have no inverse and are left out.
"""
import csv
from copy import deepcopy
import json
from pathlib import Path
import unittest

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]
FB2 = 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'
ARKIT = 'arkit.coefficient.{}'
VISEME = 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META'
VRM = 'vrm.preset.{}'
FORWARD = {'fb2.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
           'fb2_gaze.to_arkit': ('openxr.fb2', 'arkit.coefficient'),
           'visemes.to_vrm': ('openxr.visemes', 'vrm.preset')}
BACK = {'fb2.to_arkit': ('test.arkit_to_fb2', 'arkit.coefficient', 'openxr.fb2'),
        'fb2_gaze.to_arkit': ('test.arkit_gaze_to_fb2', 'arkit.coefficient', 'openxr.fb2'),
        'visemes.to_vrm': ('test.vrm_to_visemes', 'vrm.preset', 'openxr.visemes')}


def source_pairs():
    """(forward input, forward output) pairs that the sources give as one-to-one."""
    pairs = []
    with (ROOT / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            name, weight = row['fb2_inputs'].split('*') if ';' not in row['fb2_inputs'] else (None, None)
            if name and float(weight) == 1.0:
                pairs.append((FB2.format(name), ARKIT.format(row['arkit'])))
    goldens = json.loads((ROOT / 'tests/fixtures/fb2_goldens.json').read_text())
    pairs += [(VISEME.format(p['viseme']), VRM.format(p['vrm'])) for p in goldens['viseme_pairs']]
    return pairs


class RoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        document = msf.load_authoring(ROOT).value.to_dict()
        forward_rules = {m['id']: m['rules'] for m in document['mappings'] if m['id'] in FORWARD}
        by_output = {o: i for i, o in source_pairs()}
        cls.one_to_one = {}
        for mapping, rules in forward_rules.items():
            cls.one_to_one[mapping] = [r for r in rules if len(r['inputs']) == 1]
            back_id = BACK[mapping][0]
            back = []
            for rule in cls.one_to_one[mapping]:
                output = rule['outputs'][0]
                back.append({'id': f'test.back.{output}', 'inputs': [output], 'outputs': [by_output[output]],
                             'operator': {'id': 'affine', 'scale': 1.0, 'offset': 0.0}, 'disposition': 'mapped',
                             'mapping_quality': 'approximate', 'evidence_status': 'proposed',
                             'assumptions': ['Test-only reverse of a source-derived one-to-one pair.'],
                             'evidence': rule['evidence'], 'loss_annotations': deepcopy(rule['loss_annotations'])})
            document['mappings'].append({'id': back_id, 'rules': back})
        validated = msf.validate_authoring(document)
        if not validated.ok:
            raise AssertionError(validated.report.to_dict())
        cls.pack = msf.compile_pack(validated.value).value
        cls.compiled = {}
        for mapping, (source, target) in [*FORWARD.items(), *[(b, (s, t)) for b, s, t in BACK.values()]]:
            result = msf.compile_mapping(cls.pack, msf.profile_snapshot(cls.pack, source).value,
                                         msf.profile_snapshot(cls.pack, target).value, mapping, True)
            if result.value is None:
                raise AssertionError((mapping, result.report.to_dict()))
            cls.compiled[mapping] = result.value

    def evaluate(self, mapping, frames):
        samples = [{'timestamp': float(i), 'values': f, 'validity': dict.fromkeys(f, True)}
                   for i, f in enumerate(frames)]
        result = msf.evaluate_mapping(self.compiled[mapping], samples)
        self.assertIsNotNone(result.value, result.report.to_dict())
        return [dict(s['values']) for s in result.value.samples]

    def test_one_to_one_pairs_return_their_input(self):
        checked = 0
        for mapping, rules in self.one_to_one.items():
            with self.subTest(mapping=mapping):
                inputs = sorted({i for r in self.compiled[mapping].instructions for i in r['inputs']})
                frames = [dict.fromkeys(inputs, 0.25), dict.fromkeys(inputs, 1.0),
                          {sid: (n % 8) / 8 for n, sid in enumerate(inputs)}]
                outputs = self.evaluate(mapping, frames)
                kept = {r['outputs'][0] for r in rules}
                back = self.evaluate(BACK[mapping][0], [{k: v for k, v in o.items() if k in kept} for o in outputs])
                one_to_one_inputs = {r['inputs'][0] for r in rules}
                for frame, returned in zip(frames, back):
                    self.assertEqual(returned, {k: v for k, v in frame.items() if k in one_to_one_inputs})
                checked += len(rules)
        self.assertEqual(checked, 17)  # 8 face, 4 gaze, 5 viseme one-to-one rules


if __name__ == '__main__':
    unittest.main()
