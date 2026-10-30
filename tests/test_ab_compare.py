# SPDX-License-Identifier: MIT
"""scripts/ab_compare.py: the metric functions, A1's observed loss and, in the slow tier, a whole dry run.

The dry run uses a synthetic B pack made from the A1 baseline: each rule of
two direct maps is split into an in-hop and an out-hop through a canonical
signal, so B must equal A1 there, and a planted fault must fail M1 and M1s.
"""
from copy import deepcopy
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ab_compare  # noqa: E402

SLOW = os.environ.get('RCEF_SLOW_TESTS') == '1'
ARKIT, FB2 = 'arkit.coefficient.', 'openxr.fb2.XR_FACE_EXPRESSION2_'


def result(values=None, labels=None, refused=None, dropped=None):
    return {'values': values or {}, 'labels': labels or {}, 'refused': refused or {}, 'dropped': dropped or []}


class Metrics(unittest.TestCase):
    def test_m1_counts_value_and_sign_of_zero_differences_on_outputs_both_write(self):
        a1 = [result({'x': 0.5, 'y': 0.0, 'z': 1.0})]
        b = [result({'x': 0.5000000000000001, 'y': -0.0})]
        counts, failures = ab_compare.m1(a1, b)
        self.assertEqual(counts, {'compared': 2, 'value_differences': 1, 'sign_differences': 1})
        self.assertEqual(len(failures), 2)

    def test_m2_finds_wider_refusals_missing_outputs_and_other_dropped_inputs(self):
        a1 = [result({'x': 1.0}, {'y': 'refused at a'}), result({'x': 1.0}), result({'x': 1.0}, dropped=['s'])]
        b = [result({'x': 1.0, 'y': 0.5}), result({}, {'x': 'refused upstream at m'}), result({'x': 1.0})]
        counts, failures = ab_compare.m2(a1, b)
        self.assertEqual(counts['violations'], 2)
        self.assertEqual([f[0] for f in failures], [1, 2])
        self.assertIn('refused x', failures[0][1])

    def test_not_available_is_never_a_refusal(self):
        a1 = [result({'x': 1.0})]
        b = [result({'x': 1.0}, {'y': ab_compare.rcef_route.NOT_AVAILABLE})]
        self.assertEqual(ab_compare.m2(a1, b)[0]['violations'], 0)

    def test_b_must_equal_the_oracle_bit_for_bit_with_the_same_codes_and_labels(self):
        refused = {'m': {'codes': ['E_DOMAIN'], 'refs': ['rules/out']}}
        b = [result({'x': 0.0}), result(refused=refused), result(refused=refused)]
        o = [{'values': {'x': -0.0}, 'refused': {}, 'labels': {}},
             {'values': {}, 'refused': refused, 'labels': {}},
             {'values': {}, 'refused': {'m': {'codes': ['E_DOMAIN'], 'refs': ['in']}}, 'labels': {}}]
        counts, failures = ab_compare.equals_oracle(b, o)
        self.assertEqual((counts['differences'], [f[0] for f in failures]), (2, [0, 2]))
        self.assertEqual(failures[0], [0, 'value', 'x', '0.0', '-0.0'])
        self.assertEqual(failures[1][:2], [2, 'refusal'])
        # Labels and notes are compared and listed too.
        b = [result(labels={'y': 'not available from source'})]
        b[0]['notes'] = ['META validity not asserted']
        o = [{'values': {}, 'refused': {}, 'labels': {'y': 'refused at m'}, 'notes': []}]
        counts, failures = ab_compare.equals_oracle(b, o)
        self.assertEqual([f[1] for f in failures], ['label', 'notes'])

    def test_observed_loss_ignores_dropped_and_declared_inputs(self):
        frames = [{'values': {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0}}] + [
            {'values': {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0, k: v}} for k in 'abcd' for v in (1.0, 0.5)]
        results = [result({'o': 0.0})] + [result({'o': 1.0 if k == 'a' else 0.0}, dropped=['b'] if k == 'b' else [])
                                          for k in 'abcd' for _ in (1.0, 0.5)]
        self.assertEqual(ab_compare.observed_loss(results, frames, declared={'c'}), ['d'])

    def test_linear_forms_compose_exactly_across_two_hops(self):
        rules = {'mean': {'inputs': ['l', 'r'], 'operator': {'id': 'weighted_sum', 'weights': [0.5, 0.5]}},
                 'knee': {'inputs': ['l'], 'operator': {'id': 'piecewise_linear', 'knots': [[0, 0], [1, 1]]}}}
        outer = ab_compare.linear_form(rules, 'mean')
        self.assertEqual(outer, (Fraction(0), {'l': Fraction(1, 2), 'r': Fraction(1, 2)}))
        self.assertIsNone(ab_compare.linear_form(rules, 'knee'))
        inner = {'l': (Fraction(0), {'s': Fraction(1)}), 'r': (Fraction(0), {'s': Fraction(1)})}
        self.assertEqual(ab_compare.compose(outer, inner), (Fraction(0), {'s': Fraction(1)}))

    def test_round_trips_are_exact_except_rounding_outputs_and_frames_that_break_exclusivity(self):
        a, b, c = ab_compare.M3_ROUNDING[0], 'openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB', 'x'
        source = {'gaze_pairs': [[a, b]]}
        frames = [{'values': {a: 0.3, b: 0.0, c: 0.25}}, {'values': {a: 0.3, b: 0.1, c: 0.25}},
                  {'values': {a: 0.0, b: 0.0, c: 0.25}}]
        back = [result({a: 0.30000000000000004, b: 0.0, c: 0.25}), result({a: 0.2, b: 0.0, c: 0.25}),
                result({a: 0.0, b: 0.0, c: 0.5})]
        counts, failures = ab_compare.m3_exact(frames, back, source)
        self.assertEqual((counts['errors'], counts['non_exclusive_frames']), (1, 1))
        self.assertEqual(failures, [[2, c, '0.25', '0.5']])
        # VRCFaceTracking Openness comes back as 1 - (1 - x), so its rounding is reported, not counted.
        openness = 'vrcft.eye.Left.Openness'
        counts, _ = ab_compare.m3_exact([{'values': {openness: 0.3}}], [result({openness: 0.30000000000000004})],
                                        {'gaze_pairs': []})
        self.assertEqual((counts['errors'], counts['max_excluded_error']), (0, 0.30000000000000004 - 0.3))

    def test_the_excluded_round_trip_outputs_have_bounds_and_a_larger_error_fails(self):
        a, b = ab_compare.M3_ROUNDING[0], FB2 + 'EYES_LOOK_RIGHT_L_FB'
        source = {'gaze_pairs': [[a, b]]}
        up = math.nextafter(0.3, 1.0)
        # Exclusive frames: one ulp of 0.3 is 2**-54, the bound; two ulps are past it.
        for value, over in ((up, 0), (math.nextafter(up, 1.0), 1)):
            counts, failures = ab_compare.m3_exact([{'values': {a: 0.3, b: 0.0}}], [result({a: value, b: 0.0})],
                                                   source)
            self.assertEqual((counts['errors'], counts['over_bound']), (0, over), value)
        self.assertEqual(counts['max_rounding_error'], 2.0 ** -53)
        # Frames that break exclusivity: off by the smaller input (0.1) passes, by more fails.
        frame = [{'values': {a: 0.3, b: 0.1}}]
        self.assertEqual(ab_compare.m3_exact(frame, [result({a: 0.19999999999999998, b: 0.0})], source)[0][
            'over_bound'], 0)
        counts, failures = ab_compare.m3_exact(frame, [result({a: 0.1, b: 0.0})], source)
        self.assertEqual((counts['over_bound'], failures), (1, [[0, a, '0.3', '0.1']]))
        # A partner outside 0 to 1 (a perturbed frame) is refused, so it nets nothing: the output must be exact.
        frame = [{'values': {a: 0.3, b: -0.1}}]
        self.assertEqual(ab_compare.m3_exact(frame, [result({a: 0.3})], source)[0]['over_bound'], 0)
        self.assertEqual(ab_compare.m3_exact(frame, [result({a: 0.25})], source)[0]['over_bound'], 1)
        # VRCFaceTracking Openness: a planted error larger than the rounding fails.
        openness = 'vrcft.eye.Right.Openness'
        counts, _ = ab_compare.m3_exact([{'values': {openness: 0.3}}], [result({openness: 0.31})], {'gaze_pairs': []})
        self.assertEqual((counts['errors'], counts['over_bound']), (0, 1))
        self.assertEqual(ab_compare.status('M3 exact', [counts]), 'FAIL')

    def test_facs_coverage_must_follow_the_frozen_list(self):
        expected = [{'a': 0.5, 'b': 0.0, 'c': 0.0}]
        b = [result({'a': 0.5}, {'b': ab_compare.rcef_route.NOT_AVAILABLE, 'c': 'refused at m'})]
        counts, _ = ab_compare.facs_compare(b, expected, ['b'])
        self.assertEqual((counts['value_differences'], counts['coverage_violations']), (0, 1))
        counts, _ = ab_compare.facs_compare(b, expected, ['b', 'c'])
        self.assertEqual(counts['coverage_violations'], 1)
        b[0]['labels']['c'] = ab_compare.rcef_route.NOT_AVAILABLE
        self.assertEqual(ab_compare.facs_compare(b, expected, ['b', 'c'])[0]['coverage_violations'], 0)
        # The unwritten outputs must be the whole frozen list: B writing a listed output is a violation too.
        self.assertEqual(ab_compare.facs_compare(b, expected, ['a', 'b', 'c'])[0]['coverage_violations'], 1)

    def test_a_family_that_names_its_channels_is_held_only_to_the_outputs_they_reach(self):
        pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        route = ab_compare.rcef_route.Route('facs.code', 'arkit.coefficient')
        pair = {'in_hops': [[m] for m in route.in_maps], 'out_hops': [[m] for m in route.out_maps]}
        flat = [list(link) for link in ab_compare.links(pack, pair, route.outputs)]
        zero = result(dict.fromkeys({o for _, o in flat}, 0.0))
        # The letter family leaves AU19 and AU43 at 0, so the outputs only they reach stay 0.
        unvaried = {'facs.code.au19', 'facs.code.au43_left', 'facs.code.au43_right'}
        only = {o for s, o in flat if s in unvaried} - {o for s, o in flat if s not in unvaried}
        self.assertEqual(only, {ARKIT + 'eyeBlinkLeft', ARKIT + 'eyeBlinkRight', ARKIT + 'tongueOut'})
        seeded = {'facs_letters': [result({o: 0.0 if o in only else 0.5 for o in zero['values']})]}
        channels = {'facs_letters': {s for s, _ in flat} - unvaried}
        args = (pack, pair, [zero], [zero], [zero], flat, seeded)
        self.assertEqual(ab_compare.m3_coverage(*args)[0]['violations'], 3)
        self.assertEqual(ab_compare.m3_coverage(*args, channels)[0]['violations'], 0)

    def test_a_weighted_sum_input_with_weight_0_is_not_a_link(self):
        pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        route = ab_compare.rcef_route.Route('openxr.visemes', 'arkit.coefficient')
        pair = {'source': 'openxr.visemes', 'target': 'arkit.coefficient', **ab_compare.route_hops(route)}
        found = ab_compare.links(pack, pair, route.outputs)
        # Every pose weight of sil is 0, so META SIL reaches no ARKit output; the other classes reach some.
        sources = {s.split('VISEME_')[1] for s, _ in found}
        self.assertNotIn('SIL_META', sources)
        self.assertIn('AA_META', sources)
        self.assertTrue(all(knots for knots in found.values()))  # each path runs through the bridge's clamp

    def test_r3_counts_listed_departures_and_finds_other_differences(self):
        reference = {'cases': [{'expected': {'a': 0.5, 'b': 0.0, 'c': 0.25}}, {'expected': {'a': 1.0, 't': 1.0}}]}
        b = [result({'a': 0.5, 'b': 0.5, 'c': 0.25}), result({'a': 1.0})]
        counts, failures = ab_compare.r3(b, reference, ['b', 't', 'u'])
        self.assertEqual(counts, {'cases': 2, 'outputs': 5, 'exact': 3, 'departures': 2, 'departures_not_seen': 1,
                                  'differences': 0})
        counts, failures = ab_compare.r3(b, reference, ['b'])
        self.assertEqual((counts['differences'], failures), (1, [[1, 't', '1.0', "'not written'"]]))

    def test_the_draft_pins_r3_and_its_departures(self):
        self.assertEqual(ab_compare.R3_KINDS, {'fb2_to_ue': 'openxr.fb2'})
        reference = json.loads((ROOT / ab_compare.R3_FILE).read_text(encoding='utf-8'))
        outputs = {o for c in reference['cases'] for o in c['expected']}
        self.assertLessEqual(set(ab_compare.R3_DEPARTURES), outputs)
        self.assertEqual(len(ab_compare.R3_DEPARTURES), 9)


class Revise(unittest.TestCase):
    """The "revise" gate compares B with the B of the revised freeze on the same frames."""

    def test_finer_refusals_pass_and_are_counted(self):
        before = [result({'x': 0.5}, {'y': 'refused at m', 'z': 'refused upstream at m'})]
        after = [result({'x': 0.5, 'y': 0.25}, {'z': ab_compare.rcef_route.NOT_AVAILABLE})]
        counts, failures = ab_compare.revise_compare(before, after, {})
        self.assertEqual(failures, [])
        self.assertEqual(counts, {'frames': 1, 'value_differences': 0, 'not_written': 0, 'newly_refused': 0,
                                  'dropped_differences': 0, 'notes_lost': 0, 'newly_written': 1,
                                  'refused_now_not_available': 1})

    def test_a_changed_value_a_lost_output_a_new_refusal_and_changed_dropped_inputs_or_notes_fail(self):
        before = [{**result({'x': 0.5, 'w': 1.0}, dropped=['s']), 'notes': ['bridge old.m: the source writes no a']}]
        after = [{**result({'x': 0.5000000000000001}, {'w': 'refused at m', 'v': 'refused at m'}), 'notes': []}]
        counts, failures = ab_compare.revise_compare(before, after, {})
        self.assertEqual([counts[k] for k in ('value_differences', 'not_written', 'newly_refused',
                                              'dropped_differences', 'notes_lost')], [1, 1, 2, 1, 1])
        self.assertEqual([f[2] for f in failures], ['value', 'not written', 'refused', 'refused', 'dropped', 'notes'])

    def test_notes_are_compared_under_the_map_renames(self):
        before = [{**result({'x': 0.5}), 'notes': ['bridge old.m: the source writes no a; counted as 0']}]
        after = [{**result({'x': 0.5}), 'notes': ['bridge new.m: the source writes no a; counted as 0']}]
        self.assertEqual(ab_compare.revise_compare(before, after, {'old.m': 'new.m'})[0]['notes_lost'], 0)
        self.assertEqual(ab_compare.revise_compare(before, after, {})[0]['notes_lost'], 1)

    def test_maps_renamed_to_one_id_become_one_hop_in_their_first_place(self):
        pair = {'in_hops': [['a_face.x', 'c'], ['a_gaze.x', 'c']], 'bridges': [['p.b', 'c2']],
                'out_hops': [['c.y', 't'], ['c.z', 't']]}
        renames = {'a_face.x': 'a.x', 'a_gaze.x': 'a.x', 'p.b': 'q.b'}
        self.assertEqual(ab_compare.renamed_hops(pair, renames),
                         {'in_hops': [['a.x', 'c']], 'bridges': [['q.b', 'c2']],
                          'out_hops': [['c.y', 't'], ['c.z', 't']]})


class Pins(unittest.TestCase):
    def test_m5_r2_needs_its_reference_pinned_with_the_right_hash(self):
        b_path = ROOT / ab_compare.B_PACK
        pins = {'a1_sha256': ab_compare.A1_SHA256, 'b_pack_sha256': ab_compare.sha256_bytes(b_path.read_bytes()),
                'code': ab_compare.code_hashes(), 'runtime': ab_compare.runtime_pins()}
        abreg = {'pins': pins, 'pairs': {'FB2 -> ARKit': {}}, 'fixed_inputs': {}}
        self.assertEqual(ab_compare.pin_problems(abreg, ROOT, b_path),
                         [f'M5 R2 reads {ab_compare.R2_FILE}, but the registration does not pin it'])
        abreg['fixed_inputs']['r2'] = {'path': ab_compare.R2_FILE, 'sha256': '0' * 64}
        self.assertEqual(ab_compare.pin_problems(abreg, ROOT, b_path),
                         [f'{ab_compare.R2_FILE} does not have the SHA-256 the registration pins'])
        abreg['fixed_inputs']['r2']['sha256'] = ab_compare.sha256_bytes((ROOT / ab_compare.R2_FILE).read_bytes())
        self.assertEqual(ab_compare.pin_problems(abreg, ROOT, b_path), [])

    def test_the_code_pins_cover_the_files_the_checks_read(self):
        for path in ('examples/rcef_translate.py', 'scripts/build_canonical.py', 'docs/canonical-set-audit.md',
                     'tests/test_pose_bridge.py', 'examples/rigs.py', 'examples/ict_facekit.py', 'check.py'):
            self.assertIn(path, ab_compare.CODE.values())


class RestInputs(unittest.TestCase):
    def test_sil_is_declared_only_while_it_has_no_link_to_an_output(self):
        pack = json.loads((ROOT / 'generated/rcef.pack.json').read_text(encoding='utf-8'))
        route = ab_compare.rcef_route.Route('openxr.visemes', 'arkit.coefficient')
        pairs = {'META -> ARKit': {'source': 'openxr.visemes', 'target': 'arkit.coefficient',
                                   **ab_compare.route_hops(route)}}
        sil = 'openxr.visemes.XR_FACE_TRACKING_VISEME_SIL_META'
        self.assertEqual([e['input'] for e in ab_compare.rest_inputs(pack, pairs)], [sil])
        # Give SIL a second path, into vowel_open, whose pose moves the face: SIL is linked, so it is not declared.
        rule = next(r for m in pack['mappings'] for r in m['rules'] if r['id'] == 'visemes_rcef.vowel_open')
        rule['inputs'] = [sil]
        self.assertEqual(ab_compare.rest_inputs(pack, pairs), [])


class RequiredRows(unittest.TestCase):
    def test_a_gate_with_no_rows_for_a_required_pair_or_family_fails(self):
        abreg = {'pairs': {'META -> VRM': {}, 'FB2 -> FB2': {}}}
        report = {'metrics': {'M1': [{'pair': 'META -> VRM', 'value_differences': 0, 'sign_differences': 0}],
                              'B equals O': [{'pair': 'META -> VRM', 'differences': 0}],
                              'M3 exact': [{'pair': 'FB2 -> FB2', 'errors': 0, 'over_bound': 0}]}}
        missing = ab_compare.missing_rows(report, abreg)
        self.assertEqual(set(missing['M1']), set(ab_compare.A1_PAIRS) - {'META -> VRM'})
        self.assertEqual(missing['B equals O'], ['FB2 -> FB2'])
        self.assertEqual(missing['M10'], ['facs_library', 'facs_key_impulses', 'facs_letters'])
        self.assertNotIn('M3 exact', missing)
        statuses = ab_compare.statuses(report, abreg)
        self.assertEqual((statuses['M1'], statuses['M10'], statuses['M3 exact']), ('FAIL', 'FAIL', 'pass'))


class Manifest(unittest.TestCase):
    def test_the_manifest_hashes_the_code_of_the_checkout_it_ran_in(self):
        with tempfile.TemporaryDirectory(prefix='rcef-ab-') as tmp:
            root = Path(tmp)
            for path in [*ab_compare.CODE.values(), 'evidence/tooling.lock.json']:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_bytes((ROOT / path).read_bytes())
            (root / ab_compare.CODE['oracle']).write_text('# another oracle\n', encoding='utf-8')
            b_path = root / 'b.pack.json'
            b_path.write_text('{}', encoding='utf-8')
            abreg = {'id': 'ab.pivot', 'version': 1, 'kind': 'first', 'seed_root': 'a' * 64, 'pairs': {}}
            report = {'metrics': {}, 'failures': {}, 'refusals': [], 'observed_loss': [], 'assumptions': [],
                      'regression': []}
            manifest = ab_compare.write_results(root / 'out', abreg, report, {}, {}, [], True, b_path, root)
            self.assertEqual(manifest['code'], ab_compare.code_hashes(root))
            self.assertNotEqual(manifest['code'], ab_compare.code_hashes(ROOT))


class FlatLinks(unittest.TestCase):
    def test_o_lists_the_eight_fb2_gaze_cross_links_from_the_knots(self):
        document = ab_compare.load_a1()
        pair = {'source': 'arkit.coefficient', 'target': 'openxr.fb2', 'in_hops': [],
                'out_hops': [['arkit.to_fb2', None], ['arkit_gaze.to_fb2', None]]}
        impulse = ab_compare.ab_frames.impulse_family('impulse', ab_compare.ab_frames.pinned_source(
            document, 'arkit.coefficient'))
        o = ab_compare.oracle_results(ab_compare.ab_oracle.Oracle(document), pair, impulse)
        flat = ab_compare.flat_links(document, pair, impulse, o)
        self.assertEqual(len(flat), 8)
        self.assertIn([ARKIT + 'eyeLookOutLeft', FB2 + 'EYES_LOOK_RIGHT_L_FB'], flat)


class Regression(unittest.TestCase):
    """A fix freeze makes the earlier freeze's seeded families again with the generator that freeze pinned."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-ab-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'ab').mkdir()
        generator = self.root / ab_compare.CODE['generator']
        generator.write_bytes((ROOT / ab_compare.CODE['generator']).read_bytes())
        self.git('init', '-q')
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'generator')
        old = ab_compare.sha256_bytes(generator.read_bytes())
        source = {'channels': ['a', 'b'], 'flags': [], 'gaze_pairs': []}
        self.first = {'id': 'ab.pivot', 'version': 1, 'kind': 'first', 'sources': {'s': source},
                      'families': [{'name': 'u', 'kind': 'uniform', 'source': 's', 'count': 3,
                                    'range': [0.0, 1.0]}],
                      'pins': {'code': {'generator': old}}}
        self.first['seed_root'] = ab_compare.seed_root(self.first)
        (self.root / 'ab/ab.pivot-v1.abreg').write_text(json.dumps(self.first), encoding='utf-8')
        generator.write_text(generator.read_text(encoding='utf-8') + '# changed\n', encoding='utf-8')
        self.fix = {**self.first, 'version': 2, 'kind': 'fix', 'renames': {'a': 'a2'}}

    def git(self, *args):
        subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=self.root, check=True,
                       capture_output=True)

    def test_the_earlier_families_come_back_from_the_pinned_generator_with_renames(self):
        families, sources, problems = ab_compare.regression_families(self.fix, self.root)
        self.assertEqual(problems, [])
        self.assertEqual(sources, {'regression:v1:u': 's'})
        frames = families['regression:v1:u']
        self.assertEqual(len(frames), 3)
        self.assertEqual(set(frames[0]['values']), {'a2', 'b'})

    def test_frames_that_differ_from_the_earlier_run_are_a_problem(self):
        folder = self.root / ab_compare.RESULTS / 'v1'
        folder.mkdir(parents=True)
        (folder / 'SHA256SUMS').write_text(f'{"0" * 64}  frames/u.jsonl\n', encoding='utf-8')
        self.assertEqual(ab_compare.regression_families(self.fix, self.root)[2],
                         ['v1: frames/u.jsonl does not have the hash its run recorded'])

    def test_a_first_freeze_has_no_regression_families(self):
        self.assertEqual(ab_compare.regression_families(self.first, self.root), ({}, {}, []))


def facs_profile():
    """A facs.code profile with the planned rows: 49 mapped signals, 25 unresolved and 18 excluded codes."""
    codes = ab_compare.facs_codec.table()['codes']
    mapped = ab_compare.facs_codec.signals()
    others = [(f'facs.code.au{int(c.rstrip("*")):02d}', e['disposition']) for c, e in codes.items()
              if e['disposition'] in ('unresolved', 'excluded')]
    signals = [{'id': sid, 'disposition': d, 'domain': {'min': 0.0, 'max': 1.0}}
               for sid, d in [(s, 'mapped') for s in mapped] + others]
    return {'signals': signals, 'profiles': [{'id': 'facs.code', 'signal_ids': [s['id'] for s in signals]}]}


class FacsFamilies(unittest.TestCase):
    """The FACS families take the mapped rows only, whatever else the profile holds."""

    def test_the_planned_profile_gives_49_uniform_and_46_letter_channels(self):
        document = facs_profile()
        rows = [s['disposition'] for s in document['signals']]
        self.assertEqual((rows.count('mapped'), rows.count('unresolved'), rows.count('excluded')), (49, 25, 18))
        sources = ab_compare.pinned_sources(ab_compare.load_a1(), document, {'FACS -> FB2': {'source': 'facs.code'}})
        self.assertEqual(sources['facs.code']['channels'], ab_compare.facs_codec.signals())
        letters = next(f for f in ab_compare.registered_families(sources) if f['name'] == 'facs_letters')
        self.assertEqual(len(letters['channels']), 46)
        abreg = {'seed_root': 'a' * 64, 'sources': sources, 'families': [{**letters, 'count': 50}]}
        frames = ab_compare.ab_frames.seeded_families(abreg)['facs_letters']
        self.assertEqual([f['keys'] for f in frames if ab_compare.facs_codec.read(f['keys']).values is None], [])


class Baseline(unittest.TestCase):
    def test_a1_has_no_observed_loss_on_the_impulse_frames(self):
        figures = ab_compare.a1_loss()
        self.assertEqual({p: f['observed_loss'] for p, f in figures.items()}, dict.fromkeys(ab_compare.A1_PAIRS, []))
        self.assertEqual({p: (f['inputs'], f['dropped']) for p, f in figures.items()},
                         {'FB2 -> ARKit': (70, 10), 'ARKit -> FB2': (52, 0), 'ARKit -> VRCFT UE': (52, 0),
                          'FB2 -> VRM blink': (70, 68), 'META -> VRM': (15, 10)})

    def test_a_changed_fixture_is_refused(self):
        with tempfile.TemporaryDirectory(prefix='rcef-ab-') as tmp:
            fixture = Path(tmp) / ab_compare.A1_FIXTURE
            fixture.parent.mkdir(parents=True)
            fixture.write_bytes((ROOT / ab_compare.A1_FIXTURE).read_bytes().replace(b'"0.4.0"', b'"0.4.1"', 1))
            with self.assertRaises(SystemExit):
                ab_compare.load_a1(Path(tmp))

    def test_the_seed_root_leaves_out_its_own_field(self):
        abreg = {'id': 'ab.pivot', 'version': 1}
        root = ab_compare.seed_root(abreg)
        self.assertEqual(root, ab_compare.seed_root({**abreg, 'seed_root': root}))
        self.assertNotEqual(ab_compare.abreg_sha256(abreg), ab_compare.abreg_sha256({**abreg, 'seed_root': root}))


def synthetic_b(document):
    """B for two A1 pairs: each rule of visemes.to_vrm and fb2.to_vrm split into two hops, and a way back to FB2."""
    doc = deepcopy(document)
    signals = {s['id']: s for s in doc['signals']}
    members = {'rcef.canonical_expression': [], 'rcef.canonical_viseme': []}

    def hop(rule, rid, inputs, outputs):
        return {**deepcopy(rule), 'id': rid, 'inputs': inputs, 'outputs': outputs,
                'loss_annotations': [{**loss, 'refs': inputs + outputs} for loss in rule['loss_annotations']]}

    rules = {m['id']: m['rules'] for m in doc['mappings']}
    for a1, profile, group, source in (('visemes.to_vrm', 'rcef.canonical_viseme', 'vowel', 'visemes'),
                                       ('fb2.to_vrm', 'rcef.canonical_expression', 'blink', 'fb2')):
        ins, outs, back = [], [], []
        for rule in rules[a1]:
            name = rule['outputs'][0].rsplit('.', 1)[1].lower()
            like = signals[rule['inputs'][0]]
            canonical = {k: like[k] for k in ('value_type', 'units', 'domain', 'side')}
            canonical.update(id=f'{profile}.{name}', label=name, calibration=f'rcef.canonical.v1:{name}',
                             disposition='mapped', evidence=['rcef_definitions'], evidence_status='proposed')
            doc['signals'].append(canonical)
            members[profile].append(canonical['id'])
            ins.append(hop(rule, f'{source}_{group}.{name}', rule['inputs'], [canonical['id']]))
            outs.append(hop(rule, f'rcef_{group}.{name}', [canonical['id']], rule['outputs']))
            back.append(hop(rule, f'rcef_{group}.back.{name}', [canonical['id']], rule['inputs']))
        canon = profile.replace('.canonical_', '_')  # rcef_viseme or rcef_expression, as the map IDs name them
        doc['mappings'] += [{'id': f'{source}.to_{canon}', 'rules': ins}, {'id': f'{canon}.to_vrm', 'rules': outs}]
        if group == 'blink':
            doc['mappings'].append({'id': f'{canon}.to_fb2', 'rules': back})
    doc['profiles'] += [{'id': p, 'label': p, 'signal_ids': s} for p, s in members.items()]
    return doc


@unittest.skipUnless(SLOW, 'slow tier: set RCEF_SLOW_TESTS=1')
class DryRun(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-ab-')
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        self.document = synthetic_b(ab_compare.load_a1())

    def register(self, document):
        b_path = self.tmp / 'b.pack.json'
        b_path.write_text(json.dumps(document), encoding='utf-8')
        abreg = ab_compare.draft(b_path=b_path, date='2026-11-01')
        for family in abreg['families']:
            family['count'] = 20
        abreg['seed_root'] = ab_compare.seed_root(abreg)
        (self.tmp / 'x.abreg').write_text(json.dumps(abreg), encoding='utf-8')
        return abreg, b_path

    def test_b_equal_to_a1_passes_every_gate_it_reaches(self):
        abreg, b_path = self.register(self.document)
        self.assertEqual(sorted(abreg['pairs']), ['FB2 -> FB2', 'FB2 -> VRM blink', 'META -> VRM'])
        manifest = ab_compare.run(self.tmp / 'x.abreg', self.tmp / 'out', b_path=b_path, dry_run=True)
        rows = manifest['row_statuses']
        self.assertEqual(rows.pop('M5 R1'), 'FAIL')  # 126 of the 129 goldens need pairs this B cannot route
        # These hops carry today's assumption and loss text, not the hop keys, and lack the rules the mutations name.
        self.assertEqual([rows.pop(m) for m in ('M4 keys', 'M4b', 'M7')], ['FAIL', 'FAIL', 'FAIL'])
        self.assertEqual(set(rows.values()), {'pass', 'report'})
        # The rows that exist pass, but the ARKit pairs, FACS -> FB2 and FACS -> ARKit have none: those gates fail.
        missing = {'ARKit -> FB2', 'ARKit -> VRCFT UE', 'FB2 -> ARKit'}
        for metric in ('M1', 'M1s', 'M2', 'M2c'):
            self.assertEqual(set(manifest['missing_rows'][metric]), missing, metric)
            self.assertEqual(manifest['statuses'][metric], 'FAIL', metric)
        self.assertEqual((manifest['statuses']['M10'], manifest['statuses']['M10b']), ('FAIL', 'FAIL'))
        self.assertEqual(manifest['statuses']['M3 exact'], 'pass')
        self.assertFalse(manifest['passed'])
        scoreboard = (self.tmp / 'out/scoreboard.md').read_text(encoding='utf-8')
        self.assertIn('Dry run', scoreboard)
        self.assertNotIn('were committed before this run', scoreboard)
        self.assertNotIn(manifest['abreg_sha256'], scoreboard)
        sums = (self.tmp / 'out/SHA256SUMS').read_text(encoding='utf-8')
        self.assertIn('frames/edge__openxr.fb2.jsonl', sums)
        self.assertNotIn('timings.json', sums)

    def test_a_planted_fault_in_one_hop_fails_m1_and_m1s_but_not_the_oracle(self):
        rule = next(r for m in self.document['mappings'] if m['id'] == 'rcef_viseme.to_vrm' for r in m['rules'])
        rule['operator']['scale'] = 0.5
        _, b_path = self.register(self.document)
        statuses = ab_compare.run(self.tmp / 'x.abreg', self.tmp / 'out', b_path=b_path, dry_run=True)['row_statuses']
        self.assertEqual((statuses['M1'], statuses['M1s'], statuses['B equals O']), ('FAIL', 'FAIL', 'pass'))

    def test_a_run_whose_pins_do_not_match_is_refused(self):
        abreg, b_path = self.register(self.document)
        abreg['pins']['code']['oracle'] = '0' * 64
        (self.tmp / 'x.abreg').write_text(json.dumps(abreg), encoding='utf-8')
        with self.assertRaises(SystemExit):
            ab_compare.run(self.tmp / 'x.abreg', self.tmp / 'out', b_path=b_path)


if __name__ == '__main__':
    unittest.main()
