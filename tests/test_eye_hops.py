# SPDX-License-Identifier: MIT
"""The VRCFaceTracking eye and VRM blink hops, against docs/canonical-set.md and its audit, without the generator.

- VRCFaceTracking eye blink, both ways: eye_close = 1 - Openness (affine -1, 1), with the Openness assumption and
  its loss key on both hops; the in-hop refuses an Openness outside 0 to 1 with E_DOMAIN, and only for that eye;
- the pupil copies, both ways: exact and verified_current, citing only verified_current records, and the
  canonical pupils are verified_current; a round trip gives every diameter back;
- the VRM blink in-hop reads blinkLeft and blinkRight only and states that blink (both eyes) is not read; a route
  lists a non-zero blink as dropped; both VRM blink hops carry the side caveat and the side key.
"""
import json
from pathlib import Path
import random
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

PREFIX = 'rcef.canonical_expression.'
EYE = 'vrcft.eye.'
INVERT = {'id': 'affine', 'scale': -1.0, 'offset': 1.0}
COPY = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
SIDES = {'left': 'Left', 'right': 'Right'}
EYE_IN, EYE_OUT = 'vrcft_eye.to_rcef_expression', 'rcef_expression.to_vrcft_eye'
VRM_IN, VRM_OUT = 'vrm.to_rcef_expression', 'rcef_expression.to_vrm'


class EyeHops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        cls.pack = rcef_translate.load_pack(cls.document)
        cls.maps = {m['id']: m['rules'] for m in cls.document['mappings']}
        cls.signals = {s['id']: s for s in cls.document['signals']}
        cls.records = {e['id']: e for e in cls.document['evidence']}
        audit = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')
        cls.keys = dict(re.findall(r'^\| `(\w+)` \| \w+ \| [^|]+ \| (.+) \|$', audit, re.M))

        doc = (ROOT / 'docs/canonical-set.md').read_text(encoding='utf-8')
        cls.not_read = re.search(r'It declares the loss "([^"]+)", and the route lists a non-zero `blink` as dropped',
                                 doc).group(1)

    def part(self, map_id, group):
        """The rules of a map that read or write a canonical signal of one group."""
        return [r for r in self.maps[map_id] if any(self.signals[s].get('metadata', {}).get('group') == group
                                                     for s in r['inputs'] + r['outputs'] if s.startswith(PREFIX))]

    def reasons(self, rule):
        return [loss['reason'] for loss in rule['loss_annotations']]

    def route(self, source, target):
        return rcef_route.Route(source, target, pack=self.pack)

    def test_vrcft_eye_blink_hops_invert_openness_with_the_assumption_and_its_loss(self):
        key = 'vrcft_eye_openness_neutral_unresolved'
        text = self.keys[key]
        self.assertTrue(text.startswith('eye_close is 1 − Openness. Openness 1 is taken as eye_close 0'))
        for map_id, into in ((EYE_IN, True), (EYE_OUT, False)):
            rules = self.part(map_id, 'blink')
            self.assertEqual(len(rules), 2)
            for side, name in SIDES.items():
                eye, canonical = f'{EYE}{name}.Openness', f'{PREFIX}eye_close_{side}'
                rule, = [r for r in rules if eye in r['inputs'] + r['outputs']]
                with self.subTest(rule=rule['id']):
                    self.assertEqual((rule['inputs'], rule['outputs']),
                                     ([eye], [canonical]) if into else ([canonical], [eye]))
                    self.assertEqual(rule['operator'], INVERT)
                    self.assertIn(f'vrcft_eye.openness: {text}.', rule['assumptions'])
                    self.assertIn(f'{key}: {text}', self.reasons(rule))
                    self.assertIn('eye_close is 1 − Openness', next(a for a in rule['assumptions']
                                                                     if a.startswith('endpoints: ')))

    def test_the_in_hop_refuses_an_openness_outside_0_to_1(self):
        route = self.route('vrcft.eye', 'vrcft.eye')
        frames = [{'time': n / 60, 'values': {f'{EYE}Left.Openness': x, f'{EYE}Right.Openness': 0.5,
                                              f'{EYE}Left.PupilDiameter_MM': 3.0, f'{EYE}Right.PupilDiameter_MM': 3.0},
                   'flags': {}} for n, x in enumerate((1.2, -0.1, 0.0, 0.5, 1.0))]
        results = route.translate(frames)
        for result in results[:2]:
            self.assertEqual(result['refused'], {EYE_IN: {
                'codes': ['E_DOMAIN'], 'refs': ['rules/vrcft_eye_rcef.eye_close_left'],
                'outputs': [f'{PREFIX}eye_close_left']}})
            self.assertEqual(result['labels'], {f'{EYE}Left.Openness': f'refused upstream at {EYE_IN}'})
            self.assertEqual(result['values'][f'{EYE}Right.Openness'], 0.5)
            self.assertEqual(result['values'][f'{EYE}Left.PupilDiameter_MM'], 3.0)
        for result in results[2:]:
            self.assertEqual(result['refused'], {})

    def test_an_openness_round_trip_gives_one_minus_one_minus_the_value(self):
        route = self.route('vrcft.eye', 'vrcft.eye')
        rng = random.Random(3)
        values = [0.0, 1.0, 0.5, 0.25] + [rng.random() for _ in range(2000)]
        frames = [{'time': 0.0, 'values': {f'{EYE}Left.Openness': x, f'{EYE}Right.Openness': x,
                                           f'{EYE}Left.PupilDiameter_MM': x * 8, f'{EYE}Right.PupilDiameter_MM': x * 8},
                   'flags': {}} for x in values]
        for x, result in zip(values, route.translate(frames)):
            self.assertEqual(result['values'][f'{EYE}Left.Openness'], 1.0 - (1.0 - x))
            self.assertLessEqual(abs(result['values'][f'{EYE}Left.Openness'] - x), 2.0 ** -53)
            self.assertEqual(result['values'][f'{EYE}Right.PupilDiameter_MM'], x * 8)

    def test_the_pupil_hops_are_exact_verified_copies(self):
        for map_id, into in ((EYE_IN, True), (EYE_OUT, False)):
            rules = self.part(map_id, 'pupil_mm')
            self.assertEqual(len(rules), 2)
            for side, name in SIDES.items():
                eye, canonical = f'{EYE}{name}.PupilDiameter_MM', f'{PREFIX}pupil_diameter_mm_{side}'
                rule, = [r for r in rules if eye in r['inputs'] + r['outputs']]
                with self.subTest(rule=rule['id']):
                    self.assertEqual((rule['inputs'], rule['outputs']),
                                     ([eye], [canonical]) if into else ([canonical], [eye]))
                    self.assertEqual(rule['operator'], COPY)
                    self.assertEqual((rule['mapping_quality'], rule['evidence_status']), ('exact', 'verified_current'))
                    self.assertEqual(rule['evidence'], ['vrcft_data', 'rcef_canonical_v1'])
                    self.assertTrue(all(self.records[e]['status'] == 'verified_current' for e in rule['evidence']))
                    self.assertEqual(rule['loss_annotations'], [])
                    for sid in (eye, canonical):
                        self.assertEqual((self.signals[sid]['units'], self.signals[sid]['evidence_status']),
                                         ('mm', 'verified_current'))

    def test_the_vrm_blink_in_hop_reads_only_the_per_eye_presets(self):
        self.assertEqual(self.not_read, 'VRM blink (both eyes) not read; when a model drives only blink, '
                                        'eye_close reads open')
        rules = self.maps[VRM_IN]
        self.assertEqual(sorted(i for r in rules for i in r['inputs']),
                         ['vrm.preset.blinkLeft', 'vrm.preset.blinkRight'])
        for rule in rules:
            self.assertEqual(rule['operator'], COPY)
            self.assertIn(self.not_read, self.reasons(rule))
        readers = [r['id'] for rules in self.maps.values() for r in rules
                   if 'vrm.preset.blink' in r['inputs'] and r['disposition'] == 'mapped']
        self.assertEqual(readers, [])
        self.assertNotEqual(self.signals['vrm.preset.blink']['disposition'], 'mapped')

    def test_both_vrm_blink_hops_carry_the_side_caveat_and_the_side_key(self):
        key = 'vrm_blink_side_unresolved'
        for map_id in (VRM_IN, VRM_OUT):
            for rule in self.maps[map_id]:
                preset = next(s for s in rule['inputs'] + rule['outputs'] if s.startswith('vrm.preset.'))
                side = preset.removeprefix('vrm.preset.blink').lower()
                with self.subTest(rule=rule['id']):
                    caveat = (f'vrm.side_caveat: VRM gives no normative side; on the VRM 1.0 Twist sample '
                              f'{preset.rsplit(".", 1)[1]} moves the avatar\'s own {side} eyelid.')
                    self.assertIn(caveat, rule['assumptions'])
                    self.assertIn(f'{key}: {self.keys[key]}', self.reasons(rule))

    def test_a_route_lists_a_non_zero_vrm_blink_as_dropped(self):
        route = self.route('vrm.preset', 'arkit.coefficient')
        self.assertIn(VRM_IN, route.in_maps)
        presets = {f'vrm.preset.{p}': 0.0 for p in ('aa', 'ee', 'ih', 'oh', 'ou')}
        on, off = route.translate([
            {'time': 0.0, 'values': {**presets, 'vrm.preset.blink': 0.7, 'vrm.preset.blinkLeft': 0.25,
                                     'vrm.preset.blinkRight': 0.0}, 'flags': {}},
            {'time': 0.1, 'values': {**presets, 'vrm.preset.blink': 0.0, 'vrm.preset.blinkLeft': 0.25,
                                     'vrm.preset.blinkRight': 0.0}, 'flags': {}}])
        self.assertEqual(on['dropped'], ['vrm.preset.blink'])
        self.assertEqual(off['dropped'], [])
        for result in (on, off):
            self.assertEqual(result['values']['arkit.coefficient.eyeBlinkLeft'], 0.25)
            self.assertEqual(result['values']['arkit.coefficient.eyeBlinkRight'], 0.0)


if __name__ == '__main__':
    unittest.main()
