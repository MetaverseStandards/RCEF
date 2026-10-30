# SPDX-License-Identifier: MIT
"""Round trip through the one-to-one translations and back.

The way there is the route the examples run (examples/rcef_route.py), source ->
canonical -> target. A one-to-one translation is an out-map mapping with one
input whose canonical signal an in-map mapping copies from one source signal.
The way back is built in this test only, from the source-derived routes in
tests/fixtures/godot_fb2_rules.csv and the viseme pairs in
tests/fixtures/fb2_goldens.json, read in reverse. It is not built by
inverting RCEF's own rules, so it checks the rules against the sources.
Averaged pairs have no inverse and are left out.
"""
import csv
import json
from pathlib import Path
import sys
import unittest

import msf_character_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_frames  # noqa: E402

FB2 = 'openxr.fb2.XR_FACE_EXPRESSION2_{}_FB'
ARKIT = 'arkit.coefficient.{}'
VISEME = 'openxr.visemes.XR_FACE_TRACKING_VISEME_{}_META'
VRM = 'vrm.preset.{}'
FORWARD = {'fb2_to_arkit': ('openxr.fb2', 'arkit.coefficient'), 'visemes_to_vrm': ('openxr.visemes', 'vrm.preset')}
BACK = {'fb2_to_arkit': ('test.arkit_to_fb2', 'arkit.coefficient', 'openxr.fb2'),
        'visemes_to_vrm': ('test.vrm_to_visemes', 'vrm.preset', 'openxr.visemes')}
FLAGS = {'isValid': True, 'isEyeFollowingBlendshapesValid': True}


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
        rules = {m['id']: m['rules'] for m in document['mappings']}
        by_output = {o: i for i, o in source_pairs()}
        cls.routes, cls.one_to_one, backs = {}, {}, []
        for kind, (source, target) in FORWARD.items():
            route = cls.routes[kind] = rcef_frames.Frames(source, target, '', '', pack=shared_pack.pack()).route
            copies = {r['outputs'][0]: r['inputs'][0] for m in route.in_maps for r in rules[m] if len(r['inputs']) == 1}
            # (source signal, target signal, out-map) for each one-to-one translation
            cls.one_to_one[kind] = [(copies[r['inputs'][0]], r['outputs'][0], m) for m in route.out_maps
                                    for r in rules[m] if len(r['inputs']) == 1 and r['inputs'][0] in copies]
            back = []
            for _, output, _ in cls.one_to_one[kind]:
                back.append({'id': f'test.back.{output}', 'inputs': [output], 'outputs': [by_output[output]],
                             'operator': {'id': 'affine', 'scale': 1.0, 'offset': 0.0}, 'disposition': 'mapped',
                             'mapping_quality': 'approximate', 'evidence_status': 'proposed',
                             'assumptions': ['Test-only reverse of a source-derived one-to-one pair.'],
                             'evidence': ['xr_fb2'],
                             'loss_annotations': [{'category': 'signal', 'effect': 'approximated', 'units': '1',
                                                   'reason': 'test only', 'refs': [output, by_output[output]]}]})
            backs.append({'id': BACK[kind][0], 'rules': back})
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
        cls.back = {}
        for kind, (back_id, source, target) in BACK.items():
            result = msf.compile_mapping(back_pack, msf.profile_snapshot(back_pack, source).value,
                                         msf.profile_snapshot(back_pack, target).value, back_id, True)
            if result.value is None:
                raise AssertionError((back_id, result.report.to_dict()))
            cls.back[kind] = result.value

    def test_one_to_one_pairs_return_their_input(self):
        checked = {}
        for kind, pairs in self.one_to_one.items():
            with self.subTest(kind=kind):
                route = self.routes[kind]
                inputs = sorted({i for m in route.in_maps for i in route.mappings[m].required_inputs})
                frames = [dict.fromkeys(inputs, 0.25), dict.fromkeys(inputs, 1.0),
                          {sid: (n % 8) / 8 for n, sid in enumerate(inputs)}]
                results = route.translate([{'time': float(i), 'values': f, 'flags': FLAGS}
                                           for i, f in enumerate(frames)])
                self.assertEqual([r['refused'] for r in results], [{}] * len(frames))
                kept = {o for _, o, _ in pairs}
                samples = [{'timestamp': float(i), 'values': {k: v for k, v in r['values'].items() if k in kept},
                            'validity': dict.fromkeys(kept, True)} for i, r in enumerate(results)]
                back = msf.evaluate_mapping(self.back[kind], samples)
                self.assertIsNotNone(back.value, back.report.to_dict())
                one_to_one_inputs = {i for i, _, _ in pairs}
                for frame, returned in zip(frames, back.value.samples):
                    self.assertEqual(dict(returned['values']),
                                     {k: v for k, v in frame.items() if k in one_to_one_inputs})
                for _, _, mapping in pairs:
                    group = ('viseme' if kind == 'visemes_to_vrm' else
                             'gaze' if mapping == 'rcef_gaze.to_arkit' else 'face')
                    checked[group] = checked.get(group, 0) + 1
        self.assertEqual(checked, {'face': 38, 'gaze': 8, 'viseme': 5})
        self.assertEqual(sum(checked.values()), 51)  # 38 face, 8 gaze, 5 viseme one-to-one mappings


if __name__ == '__main__':
    unittest.main()
