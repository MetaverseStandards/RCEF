# SPDX-License-Identifier: MIT
"""The A/B metrics built from frozen tables and harnesses: M4 keys, M4b, M6, M7 and M11.

Each metric must pass on today's B pack and fail when its target defect is
planted. The tables are checked against the figures that the definitions
audit states (docs/canonical-set-audit.md), not against the code that builds
them. M6 runs on a tiny rig made in the format of ICT-FaceKit's files, so it
needs no download.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import tempfile
import tomllib
import unittest

import msf_character_tools as msf

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'examples')]
import ab_compare  # noqa: E402
import ab_geometry  # noqa: E402
import ab_mutations  # noqa: E402
import ict_facekit  # noqa: E402
import rigs  # noqa: E402

AUDIT = (ROOT / 'docs/canonical-set-audit.md').read_text(encoding='utf-8')


def rule(document, rule_id):
    return next(r for m in document['mappings'] for r in m['rules'] if r['id'] == rule_id)


def b_pack():
    return json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))


class Tables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b, cls.a1 = b_pack(), ab_compare.load_a1()
        cls.pairs = ab_compare.b_pairs(cls.b)
        cls.abreg = {'pairs': cls.pairs, 'lists': {
            'audit_keys': ab_compare.audit_keys(), 'a1_loss_corrections': [],
            'audit_added_keys': ab_compare.audit_added_keys(),
            'reason_key_table': ab_compare.reason_key_table(cls.a1, cls.b, cls.pairs),
            'assumption_catalogue': ab_compare.assumption_catalogue(cls.a1, cls.pairs)}}

    def m4_keys(self, document):
        rows, failures = ab_compare.m4_keys(self.abreg, self.a1, document)
        return sum(r['shortfall'] for r in rows), sum(r['unlisted_added'] for r in rows), failures

    def m4b(self, document):
        rows, failures, _ = ab_compare.m4b(self.abreg, self.a1, document)
        return sum(r['shortfall'] for r in rows), failures

    def test_the_reason_table_covers_each_reason_on_as_many_rules_as_the_audit_says(self):
        section = AUDIT.split("## Mapping today's losses to keys")[1].split('## Keys added')[0]
        rows = re.findall(r'^\| (.+?) \| (\d+) \| .+ \|$', section, re.M)
        documented = {reason: int(count) for reason, count in rows}
        found = {}
        for entry_id in self.abreg['lists']['reason_key_table']:
            reason = entry_id.split(' | ', 1)[1]
            key = next(d for d in documented if reason.startswith(d.split(' (on ')[0][:40]))
            found[key] = found.get(key, 0) + 1
        self.assertEqual(len(documented), 21)
        self.assertEqual(found, documented)

    def test_today_b_holds_every_frozen_loss_key_and_adds_only_listed_keys(self):
        self.assertEqual(self.m4_keys(self.b), (0, 0, []))

    def test_m4_keys_fails_when_a_hop_loses_a_key_or_its_gain_loss(self):
        for rule_id, key in (('rcef_arkit.mouthClose', 'arkit_mouthclose_jaw_unresolved'),
                             ('rcef_arkit.eyeBlinkLeft', 'ARKit gain and full-activation pose not published')):
            changed = deepcopy(self.b)
            r = rule(changed, rule_id)
            r['loss_annotations'] = [x for x in r['loss_annotations'] if not x['reason'].startswith(key)]
            shortfall, _, failures = self.m4_keys(changed)
            with self.subTest(key=key):
                self.assertGreater(shortfall, 0)
                self.assertEqual({f[3] for f in failures}, {key})

    def test_m4_keys_fails_when_a_key_sits_on_the_wrong_side_of_the_route(self):
        changed = deepcopy(self.b)
        out_hop, in_hop = rule(changed, 'rcef_arkit.mouthClose'), rule(changed, 'fb2_rcef.lips_toward')
        moved = [x for x in out_hop['loss_annotations'] if x['reason'].startswith('arkit_mouthclose_jaw_unresolved')]
        out_hop['loss_annotations'] = [x for x in out_hop['loss_annotations'] if x not in moved]
        in_hop['loss_annotations'] += moved
        shortfall, _, failures = self.m4_keys(changed)
        self.assertGreater(shortfall, 0)
        self.assertEqual({(f[2], f[3]) for f in failures}, {('out', 'arkit_mouthclose_jaw_unresolved')})

    def test_m4_keys_fails_when_a_route_adds_an_audit_key_that_is_not_listed(self):
        changed = deepcopy(self.b)
        r = rule(changed, 'fb2_rcef.brow_lower_left')
        r['loss_annotations'].append({**r['loss_annotations'][0], 'reason': 'vrm_ih_vowel_quality: planted'})
        shortfall, added, failures = self.m4_keys(changed)
        self.assertEqual((shortfall, added), (0, 1))
        self.assertEqual(failures[0][:4], ['FB2 -> ARKit', 'fb2_arkit.browDownLeft', '', 'vrm_ih_vowel_quality'])

    def test_the_catalogue_has_the_audit_counts(self):
        catalogue = self.abreg['lists']['assumption_catalogue']
        stated = re.search(r'they carry \*\*(\d+) assumption strings\*\*.*?into \*\*(\d+) templates\*\*', AUDIT, re.S)
        self.assertEqual((len(catalogue), len({k.split(' | ')[1] for k in catalogue})),
                         (int(stated[1]), int(stated[2])))
        superseded = re.search(r'(\d+) entries are superseded', AUDIT)
        self.assertEqual(sum('superseded' in e for e in catalogue.values()), int(superseded[1]))

    def test_today_b_holds_every_catalogue_entry(self):
        self.assertEqual(self.m4b(self.b), (0, []))

    def test_m4b_accepts_a_withdrawn_transfer_only_where_the_audit_row_is_not_same(self):
        # fb2_arkit.eyeBlinkLeft: both audit rows of eye_close_left are same, so its route must keep transfer.provider.
        changed = deepcopy(self.b)
        for rule_id in ('fb2_rcef.eye_close_left', 'rcef_arkit.eyeBlinkLeft'):
            r = rule(changed, rule_id)
            r['assumptions'] = [a.replace('transfer.provider:', 'transfer.withdrawn:', 1) for a in r['assumptions']]
        shortfall, failures = self.m4b(changed)
        self.assertEqual(shortfall, 1)
        self.assertEqual(failures[0][:3], ['FB2 -> ARKit', 'fb2_arkit.eyeBlinkLeft', 'a07'])
        self.assertIn('transfer.provider', failures[0][3])

    def test_m4b_fails_when_one_hop_loses_one_assumption(self):
        for rule_id, key, side in (('rcef_arkit.eyeBlinkLeft', 'correspondence', 'out'),
                                   ('fb2_rcef.eye_close_left', 'endpoints', 'in'),
                                   ('rcef_fb2.EYES_LOOK_LEFT_L', 'correspondence', 'out')):
            changed = ab_mutations.mutate(self.b, {'op': 'delete_assumption', 'rule': rule_id, 'key': key})
            shortfall, failures = self.m4b(changed)
            with self.subTest(rule=rule_id):
                self.assertGreater(shortfall, 0)
                self.assertTrue(all(f'{side}: {key}' in f[3] for f in failures), failures[:2])


class Mutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = b_pack()

    def test_each_registered_change_alters_only_its_rules(self):
        before = {r['id']: r for m in self.b['mappings'] for r in m['rules']}
        for mutation in ab_mutations.MUTATIONS:
            change = mutation['change']
            changed = ab_mutations.mutate(self.b, change)
            touched = {r['id'] for m in changed['mappings'] for r in m['rules'] if r != before[r['id']]}
            named = {i for pair in change.get('pairs', []) for i in pair} | {change.get('rule')} - {None}
            with self.subTest(mutation=mutation['id']):
                if change['op'] == 'merge_maps':
                    self.assertEqual((len(changed['mappings']), touched), (len(self.b['mappings']) - 1, set()))
                else:
                    self.assertEqual(touched, named)

    def test_the_set_covers_the_planned_faults_and_names_a_check_for_each(self):
        ops = [m['change']['op'] for m in ab_mutations.MUTATIONS]
        self.assertEqual((len(ops), ops.count('swap_outputs')), (12, 5))
        for mutation in ab_mutations.MUTATIONS:
            self.assertLessEqual(set(mutation['caught_by']), set(ab_mutations.CHECKS))
            if mutation['change']['op'] == 'swap_outputs':
                self.assertTrue({'side test', 'direction-suffix test'} & set(mutation['caught_by']), mutation['id'])

    def test_the_test_checks_catch_a_swap_on_a_changed_pack_and_pass_on_the_unchanged_one(self):
        names = ['side test', 'direction-suffix test']
        self.assertEqual(ab_mutations.test_failures(self.b, names), (set(), set()))
        eye = next(m for m in ab_mutations.MUTATIONS if 'VRCFaceTracking eye' in m['id'])
        self.assertEqual(ab_mutations.test_failures(ab_mutations.mutate(self.b, eye['change']), names),
                         ({'side test'}, set()))
        # The direction-suffix test fails inside a subTest; that counts as a catch too.
        au30 = next(m for m in ab_mutations.MUTATIONS if 'au30' in m['id'])
        self.assertEqual(ab_mutations.test_failures(ab_mutations.mutate(self.b, au30['change']), names),
                         ({'direction-suffix test'}, set()))

    def test_a_test_class_that_cannot_be_set_up_catches_nothing(self):
        broken = {k: v for k, v in self.b.items() if k != 'profiles'}
        self.assertEqual(ab_mutations.test_failures(broken, ['side test', 'pose-bridge chain test']),
                         (set(), {'side test', 'pose-bridge chain test'}))

    def test_the_bridge_mutations_are_caught_by_the_pose_bridge_tests_and_the_calibration_check(self):
        names = ['pose-bridge weight test', 'pose-bridge chain test']
        self.assertEqual(ab_mutations.test_failures(self.b, names), (set(), set()))
        self.assertFalse(ab_mutations.calibration_fails(self.b))
        weight, knot = (next(m for m in ab_mutations.MUTATIONS if word in m['id']) for word in ('weight', 'knot'))
        changed = ab_mutations.mutate(self.b, weight['change'])
        self.assertEqual(ab_mutations.test_failures(changed, names), ({'pose-bridge weight test'}, set()))
        self.assertTrue(ab_mutations.calibration_fails(changed))
        changed = ab_mutations.mutate(self.b, knot['change'])
        self.assertEqual(ab_mutations.test_failures(changed, names), ({'pose-bridge chain test'}, set()))

    def test_an_unknown_or_empty_change_is_refused(self):
        with self.assertRaises(SystemExit):
            ab_mutations.mutate(self.b, {'op': 'operator', 'rule': 'fb2_rcef.brow_lower_left',
                                         'operator': rule(self.b, 'fb2_rcef.brow_lower_left')['operator']})
        with self.assertRaises(SystemExit):
            ab_mutations.mutate(self.b, {'op': 'rename'})


class R5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = b_pack()
        cls.fixture = json.loads((ROOT / ab_compare.R5_FILE).read_text(encoding='utf-8'))
        route = ab_compare.rcef_route.Route('arkit.coefficient', 'facs.code')
        cls.pair = {'source': 'arkit.coefficient', 'target': 'facs.code', **ab_compare.route_hops(route)}

    def test_the_fixture_is_the_table_of_the_pinned_record(self):
        record = next(r for r in tomllib.loads((ROOT / 'evidence/sources.toml').read_text(encoding='utf-8'))[
            'evidence'] if r['id'] == 'ict_facekit')
        self.assertEqual((self.fixture['sha256'], self.fixture['url']), (record['sha256'], record['url']))
        self.assertEqual([r['line'] for r in self.fixture['rows']], list(range(156, 185)))
        self.assertEqual(self.fixture['rows'][0], {'line': 156, 'unit': 'AU1 Inner brow raiser',
                                                   'shapes': ['browInnerUp_L', 'browInnerUp_R']})

    def test_b_matches_ict_on_20_rows_and_departs_only_where_listed(self):
        rows, failures = ab_compare.m11(self.b, self.pair, self.fixture, ab_compare.M11_DIFFERENCES)
        self.assertEqual(failures, [])
        self.assertEqual(sorted(r['unit'].split()[0] for r in rows if r['verdict'] == 'listed difference'),
                         sorted(ab_compare.M11_DIFFERENCES))
        self.assertEqual(sum(r['verdict'] == 'same' for r in rows), 20)
        au30 = [r for r in rows if r['unit'].startswith('AU30')]
        self.assertEqual([(r['ict'], r['b']) for r in au30], [('jawLeft', 'jawLeft'), ('jawRight', 'jawRight')])

    def test_a_changed_link_is_an_unlisted_difference_and_a_listed_row_that_agrees_is_flagged(self):
        changed = deepcopy(self.b)
        rule(changed, 'arkit_rcef.brow_outer_raise_left')['inputs'] = ['arkit.coefficient.browDownLeft']
        _, failures = ab_compare.m11(changed, self.pair, self.fixture, ab_compare.M11_DIFFERENCES)
        self.assertEqual([(f[1], f[4]) for f in failures], [('AU2 Outer brow raiser', 'unlisted difference')])
        _, failures = ab_compare.m11(self.b, self.pair, self.fixture, {**ab_compare.M11_DIFFERENCES, 'AU1': 'planted'})
        self.assertEqual([(f[1], f[4]) for f in failures], [('AU1 Inner brow raiser', 'listed but the same')])


class Geometry(unittest.TestCase):
    """M6 on a tiny rig in the format of ICT-FaceKit's files: one triangle and the 16 ARKit-named shapes."""

    def rig(self, still=None):
        with tempfile.TemporaryDirectory(prefix='rcef-m6-') as folder:
            cache = Path(folder)
            neutral = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

            def obj(name, points):
                lines = [f'v {x!r} {y!r} {z!r}' for x, y, z in points] + ['f 1 2 3']
                (cache / f'{name}.obj').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            obj(ict_facekit.NEUTRAL, neutral)
            for n, name in enumerate(ict_facekit.SHAPES):
                obj(name, [(x, y, z + (0.0 if name == still else (n + 1) / 16)) for x, y, z in neutral])
            glb, targets, _ = ict_facekit.build_glb(cache)
        snapshot = rigs.require(msf.inspect_asset(glb, 'glb'))
        return rigs.Rig('tiny', 'test', snapshot, 0, targets, shapes=rigs.ict_shapes(targets))

    def test_the_oracles_pass_on_a_sound_rig_and_find_a_shape_that_moves_nothing(self):
        self.assertEqual(ab_geometry.oracle_problems(self.rig()), [])
        self.assertEqual(ab_geometry.oracle_problems(self.rig(still='jawOpen')), ['tiny: jawOpen at 1 moves no vertex'])

    def test_equal_values_give_equal_vertices_and_a_planted_difference_shows(self):
        rig, arkit = self.rig(), ab_geometry.ARKIT
        a = [{'values': {arkit + 'jawOpen': 0.5, arkit + 'eyeBlinkLeft': 0.25}},
             {'values': {arkit + 'browInnerUp': 1.0}}]
        same = ab_geometry.vertex_difference(rig, a, deepcopy(a))
        self.assertEqual((same['posed'], same['frames_with_difference'], same['max_vertex_difference']), (2, 0, 0.0))
        b = deepcopy(a)
        b[0]['values'][arkit + 'jawOpen'] = 0.25
        b[1]['values'][arkit + 'mouthClose'] = 1.0  # written by one arm only, so it does not pose the rig
        planted = ab_geometry.vertex_difference(rig, a, b)
        self.assertEqual(planted['frames_with_difference'], 1)
        self.assertGreater(planted['max_vertex_difference'], 0.0)

    def test_the_row_says_how_many_arkit_outputs_the_rig_binds(self):
        # ICT's 16 shapes name 14 ARKit outputs: browInnerUp and cheekPuff come in halves.
        self.assertEqual(ab_geometry.bound(self.rig()), '14 of 52')

    def test_the_rig_pins_are_the_files_the_examples_check(self):
        pins = ab_geometry.rig_pins()
        self.assertEqual(pins['rocketbox-female'], {'Female_Adult_01_facial.fbx':
                                                    rigs.FILES['Female_Adult_01_facial.fbx'][1]})
        self.assertEqual(pins['ict'], ict_facekit.FILES)
        self.assertTrue(all(re.fullmatch(r'[0-9a-f]{64}', h) for h in pins['ict'].values()))


if __name__ == '__main__':
    unittest.main()
