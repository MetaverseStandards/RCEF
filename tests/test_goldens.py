# SPDX-License-Identifier: MIT
"""The source-derived expectations themselves: coverage, second sources and frames that cannot hide a rule."""
import csv
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
FLAGGED = {'mouthLeft', 'mouthRight'}  # ARKit name step from Godot only; see the notes column
UE = 'vrcft.artist.base.'
FB2 = ('openxr.fb2.XR_FACE_EXPRESSION2_', '_FB')
# R3: the parts that Godot's FB2 plugin leaves at 0 inside a blended shape it sets from FB2.
ZERO_PARTS = {'BrowPinchLeft': 'BROW_LOWERER_L', 'BrowPinchRight': 'BROW_LOWERER_R',
              'MouthCornerSlantLeft': 'LIP_CORNER_PULLER_L', 'MouthCornerSlantRight': 'LIP_CORNER_PULLER_R',
              'MouthUpperLeft': 'MOUTH_LEFT', 'MouthLowerLeft': 'MOUTH_LEFT', 'MouthUpperRight': 'MOUTH_RIGHT',
              'MouthLowerRight': 'MOUTH_RIGHT'}


class Goldens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
            cls.routes = list(csv.DictReader(handle))
        cls.goldens = json.loads((ROOT / 'tests/fixtures/fb2_goldens.json').read_text(encoding='utf-8'))

    def test_every_arkit_coefficient_has_a_route_and_a_second_source(self):
        self.assertEqual(len(self.routes), 52)
        for route in self.routes:
            with self.subTest(route['arkit']):
                if route['arkit'] in FLAGGED:
                    self.assertEqual(route['second_sources'], '')
                    self.assertIn('single project for the ARKit name (Godot)', route['notes'])
                else:
                    self.assertTrue(route['second_sources'], route['notes'])

    def test_vrcft_labels_outside_the_registry_are_not_counted(self):
        by_name = {r['arkit']: r for r in self.routes}
        for arkit in ('eyeSquintLeft', 'eyeWideRight', 'eyeLookInLeft', 'mouthLowerDownLeft'):
            self.assertNotIn('vrcft', by_name[arkit]['second_sources'].split(';'), arkit)
            self.assertIn('not in the registry', by_name[arkit]['notes'])
        self.assertIn('vrcft', by_name['eyeLookUpLeft']['second_sources'].split(';'))
        self.assertNotIn('ict', by_name['mouthUpperUpLeft']['second_sources'].split(';'))
        self.assertIn('AU11', by_name['mouthUpperUpLeft']['notes'])

    def test_unified_routes_cover_every_arkit_coefficient(self):
        routes = self.goldens['unified_routes']
        self.assertEqual(len(routes), 52)
        outputs = [o for r in routes for o in r['outputs']]
        self.assertEqual(len(outputs), 68)
        self.assertEqual(len(set(outputs)), 68)
        brow = next(r for r in routes if r['arkit'] == 'browDownLeft')
        self.assertEqual(brow['outputs'], ['BrowLowererLeft', 'BrowPinchLeft'])
        self.assertIn('vrcft_simple_expressions:L39', brow['sources'])

    def test_blink_pairs_follow_the_side_each_text_names(self):
        self.assertEqual({p['fb2']: p['vrm'] for p in self.goldens['blink_pairs']},
                         {'EYES_CLOSED_L': 'blinkLeft', 'EYES_CLOSED_R': 'blinkRight'})

    def test_whole_frames_give_every_input_its_own_value(self):
        for kind in ('fb2_to_arkit', 'arkit_to_fb2', 'arkit_to_ue', 'fb2_to_vrm'):
            frames = [c for c in self.goldens['cases'] if c['mapping_kind'] == kind and len(c['inputs']) > 4
                      or c['mapping_kind'] == kind == 'fb2_to_vrm']
            with self.subTest(kind):
                self.assertEqual(len(frames), 2)
                for frame in frames:
                    # FB2 allows only one of two opposing gaze directions to be non-zero, so
                    # the inverse frames leave one ARKit direction of each pair at zero.
                    values = [v for v in frame['inputs'].values() if v or kind != 'arkit_to_fb2']
                    self.assertEqual(len(set(values)), len(values))
                    self.assertTrue(all(0 < v < 1 for v in values))
                at_rest = [{k for k, v in f['inputs'].items() if not v} for f in frames]
                self.assertEqual(len(at_rest[0]), 4 if kind == 'arkit_to_fb2' else 0)
                self.assertFalse(at_rest[0] & at_rest[1], 'every input moves in one of the frames')


class GodotUnifiedGoldens(unittest.TestCase):
    """R3: FB2 -> Unified Expressions base shapes as Godot's FB2 plugin and face modifier give them."""

    @classmethod
    def setUpClass(cls):
        cls.r3 = json.loads((ROOT / 'tests/fixtures/fb2_vrcft_ue_goldens.json').read_text(encoding='utf-8'))
        cls.routes = {r['ue']: r for r in cls.r3['routes']}

    def test_each_shape_is_one_fb2_weight_or_a_part_left_at_zero(self):
        self.assertEqual(len(self.r3['routes']), 73)
        self.assertEqual(len(self.routes), 73)
        zero = {ue: r for ue, r in self.routes.items() if not r['inputs']}
        self.assertEqual({ue: r['blend_inputs'] for ue, r in zero.items()},
                         {ue: [fb2] for ue, fb2 in ZERO_PARTS.items()})
        for ue, r in self.routes.items():
            with self.subTest(ue):
                if ue in zero:
                    self.assertTrue(r['basis'].startswith('set to 0; a part of '), r['basis'])
                else:
                    self.assertEqual(list(r['inputs'].values()), [1.0])
                    self.assertNotIn('blend_inputs', r)
        self.assertEqual(self.routes['TongueFlat']['inputs'], {'TONGUE_RETREAT': 1.0})
        self.assertEqual(self.routes['CheekSuckLeft']['inputs'], {'CHEEK_SUCK_L': 1.0})
        self.assertEqual(self.routes['MouthTightenerRight']['inputs'], {'LIP_TIGHTENER_R': 1.0})
        self.assertEqual(self.routes['LipPuckerUpperRight']['inputs'], self.routes['LipPuckerLowerRight']['inputs'])
        self.assertEqual(self.routes['EyeLookOutLeft']['inputs'], {'EYES_LOOK_LEFT_L': 1.0})

    def test_every_shape_cites_godot_and_the_unified_table_and_is_a_unified_base_shape(self):
        base = {s['id'] for s in tomllib.loads((ROOT / 'profiles/vrcft.artist.base.toml').read_text(
            encoding='utf-8'))['signals']}
        records = {r['id']: r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text(
            encoding='utf-8'))['evidence']}
        self.assertEqual(self.r3['sources'], {k: records[k]['sha256'] for k in self.r3['sources']})
        self.assertEqual(sorted(self.r3['sources']),
                         ['godot_enum', 'godot_face_modifier', 'godot_vendors_fb2', 'vrcft_docs_shapes'])
        for ue, r in self.routes.items():
            with self.subTest(ue):
                self.assertIn(UE + ue, base)
                cited = {s.split(':')[0] for s in r['sources']}
                self.assertEqual(cited, set(self.r3['sources']))

    def test_single_inputs_and_whole_frames(self):
        cases = self.r3['cases']
        singles = [c for c in cases if len(c['inputs']) == 1]
        wholes = [c for c in cases if len(c['inputs']) > 1]
        self.assertEqual((len(singles), len(wholes)), (130, 2))
        for case in singles:
            [(sid, level)] = case['inputs'].items()
            name = sid.removeprefix(FB2[0]).removesuffix(FB2[1])
            expected = {UE + ue: (level if r['inputs'] else 0.0) for ue, r in self.routes.items()
                        if name in r['inputs'] or name in r.get('blend_inputs', [])}
            self.assertEqual(case['expected'], expected, sid)
        for case in wholes:
            values = list(case['inputs'].values())
            self.assertEqual(len(set(values)), len(values))
            self.assertTrue(all(0 < v < 1 for v in values))
            self.assertEqual(set(case['expected']), {UE + ue for ue in self.routes})
            for ue in ZERO_PARTS:
                self.assertEqual(case['expected'][UE + ue], 0.0)
                self.assertGreater(case['inputs'][FB2[0] + ZERO_PARTS[ue] + FB2[1]], 0)


if __name__ == '__main__':
    unittest.main()
