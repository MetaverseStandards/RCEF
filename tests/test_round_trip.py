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

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

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
        document = shared_pack.document()
        forward_rules = {m['id']: m['rules'] for m in document['mappings'] if m['id'] in FORWARD}
        by_output = {o: i for i, o in source_pairs()}
        cls.one_to_one = {}
        backs = []
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
            backs.append({'id': back_id, 'rules': back})
        # The way back is compiled in a small pack holding only the four profiles it
        # touches, which compiles and evaluates much faster than the full pack.
        profiles = {p for _, s, t in BACK.values() for p in (s, t)}
        document['profiles'] = [p for p in document['profiles'] if p['id'] in profiles]
        kept = {sid for p in document['profiles'] for sid in p['signal_ids']}
        document['signals'] = [s for s in document['signals'] if s['id'] in kept]
        document['mappings'] = backs
        validated = msf.validate_authoring(document)
        if not validated.ok:
            raise AssertionError(validated.report.to_dict())
        back_pack = msf.compile_pack(validated.value).value
        cls.compiled = {m: shared_pack.mapping(m, s, t) for m, (s, t) in FORWARD.items()}
        for back_id, source, target in BACK.values():
            result = msf.compile_mapping(back_pack, msf.profile_snapshot(back_pack, source).value,
                                         msf.profile_snapshot(back_pack, target).value, back_id, True)
            if result.value is None:
                raise AssertionError((back_id, result.report.to_dict()))
            cls.compiled[back_id] = result.value

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
        self.assertEqual(checked, 51)  # 38 face, 8 gaze, 5 viseme one-to-one rules


if __name__ == '__main__':
    unittest.main()
