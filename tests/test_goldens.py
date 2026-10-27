# SPDX-License-Identifier: MIT
"""The source-derived expectations themselves: coverage, second sources and frames that cannot hide a rule."""
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FLAGGED = {'mouthLeft', 'mouthRight'}  # ARKit name step from Godot only; see the notes column


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
                    values = list(frame['inputs'].values())
                    self.assertEqual(len(set(values)), len(values))
                    self.assertTrue(all(0 < v < 1 for v in values))


if __name__ == '__main__':
    unittest.main()
