# SPDX-License-Identifier: MIT
"""Calibration records and the knots of the rules that cite them, as check.py checks them."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)
FIXTURES = ROOT / 'tests/fixtures/calibration'
RECORD = FIXTURES / 'fixture.jaw-gain.cal'


def fixture_rule():
    return json.loads((FIXTURES / 'fixture_rule.json').read_text(encoding='utf-8'))


class Records(unittest.TestCase):
    def setUp(self):
        self.record = check.load_record(RECORD)

    def problems(self, record=None, name='fixture.jaw-gain'):
        return check.record_problems(self.record if record is None else record, name)

    def changed(self, change):
        record = deepcopy(self.record)
        change(record)
        return self.problems(record)

    def assertRefused(self, change, *words):
        problems = self.changed(change)
        self.assertTrue(problems, 'the change was accepted')
        for word in words:
            self.assertTrue(any(word in p for p in problems), problems)

    def test_the_fixture_record_is_valid(self):
        self.assertEqual(self.problems(), [])

    def test_the_id_must_be_the_file_name(self):
        self.assertTrue(any('fixture.other' in p for p in self.problems(name='fixture.other')))

    def test_required_fields_and_their_types(self):
        for field in ('method', 'channels', 'reference_rig', 'inputs', 'renderer', 'code_commit', 'training',
                      'held_out', 'curves', 'cells', 'licence', 'limitations'):
            with self.subTest(field):
                self.assertRefused(lambda r: r.pop(field), field)
        self.assertRefused(lambda r: r.update(limitations=[]), 'limitations')
        self.assertRefused(lambda r: r.update(channels='fixture.source.jaw'), 'channels')
        self.assertRefused(lambda r: r.update(surprise=1), 'surprise')

    def test_only_software_calibration_is_accepted_for_now(self):
        self.assertRefused(lambda r: r.update(status='calibrated_measured'), 'calibrated_measured')
        self.assertRefused(lambda r: r.update(status='verified_current'), 'verified_current')

    def test_hashes_and_commit_must_be_well_formed(self):
        self.assertRefused(lambda r: r['inputs'][0].update(sha256='ABC'), 'inputs', 'ABC')
        self.assertRefused(lambda r: r['inputs'][1].update(sha256='2' * 63), 'inputs')
        self.assertRefused(lambda r: r['renderer'].update(binary_sha256='4' * 63 + 'G'), 'binary_sha256')
        self.assertRefused(lambda r: r['renderer'].update(source_sha256='3' * 63 + 'A'), 'source_sha256')
        self.assertRefused(lambda r: r.update(code_commit='0123456'), 'code_commit')
        self.assertRefused(lambda r: r.update(inputs=[]), 'inputs')

    def test_renderer_names_its_os_gpu_and_compiler(self):
        for field in ('os', 'gpu', 'compiler'):
            with self.subTest(field):
                self.assertRefused(lambda r: r['renderer'].pop(field), field)

    def test_curves_are_monotone_with_strictly_increasing_inputs(self):
        self.assertRefused(lambda r: r['curves'][0].update(knots=[[0.0, 0.0]]), 'knots')
        self.assertRefused(lambda r: r['curves'][0].update(knots=[[0.0, 0.0], [0.5, 0.4], [0.5, 0.6], [1.0, 1.0]]),
                           'increasing')
        self.assertRefused(lambda r: r['curves'][0].update(knots=[[0.0, 0.0], [0.5, 0.6], [0.7, 0.5], [1.0, 1.0]]),
                           'monotone')
        self.assertRefused(lambda r: r['curves'][0].update(knots=[[0.0, 0.0], [1.0, float('inf')]]), 'finite')
        self.assertRefused(lambda r: r['curves'][0].update(input='fixture.source.other'), 'fixture.source.other')
        self.assertRefused(lambda r: r['curves'].append(deepcopy(r['curves'][0])), 'twice')

    def test_a_falling_curve_is_monotone_too(self):
        record = deepcopy(self.record)
        record['curves'][0]['knots'] = [[-1.0, 1.0], [0.0, 0.0], [1.0, 0.0]]
        record['held_out']['frozen_sha256'] = check.frozen_sha256(record)
        self.assertEqual(self.problems(record), [])

    def test_each_cell_has_at_least_20_conditions_and_its_three_metrics(self):
        self.assertRefused(lambda r: r['cells'][0].update(conditions=19), '20')
        self.assertRefused(lambda r: r['cells'][0].pop('p95'), 'p95')
        self.assertRefused(lambda r: r['cells'][0].update(median=0.05, p95=0.04), 'p95')
        self.assertRefused(lambda r: r['cells'][0].update(neutral=-0.01), 'neutral')
        self.assertRefused(lambda r: r['cells'][0].update(channel='fixture.source.other'), 'fixture.source.other')
        self.assertRefused(lambda r: r['cells'][0].pop('identity'), 'identity')

    def test_the_frozen_part_cannot_change_after_the_seeds_are_drawn(self):
        self.assertRefused(lambda r: r['curves'][0]['knots'][1].__setitem__(1, 0.19), 'frozen_sha256')
        self.assertRefused(lambda r: r['training'].update(conditions=47), 'frozen_sha256')
        self.assertRefused(lambda r: r['held_out'].update(count=23), 'frozen_sha256')

    def test_metrics_are_not_frozen(self):
        # The metrics are measured on the held-out seeds, so they come after the hash.
        self.assertEqual(self.changed(lambda r: r['cells'][0].update(median=0.02)), [])

    def test_held_out_seeds_come_from_the_frozen_hash(self):
        seeds = check.held_out_seeds(self.record)
        self.assertEqual(len(seeds), self.record['held_out']['count'])
        self.assertEqual(len(set(seeds)), len(seeds))
        self.assertEqual(seeds, check.held_out_seeds(check.load_record(RECORD)))
        other = deepcopy(self.record)
        other['curves'][0]['knots'][1][1] = 0.19
        other['held_out']['frozen_sha256'] = check.frozen_sha256(other)
        self.assertNotEqual(check.held_out_seeds(other)[:3], seeds[:3])
        self.assertRefused(lambda r: r['held_out'].update(seed_rule='random'), 'seed_rule')
        self.assertRefused(lambda r: r['held_out'].update(count=0), 'count')

    def test_a_toml_date_is_refused_not_a_crash(self):
        text = RECORD.read_text(encoding='utf-8').replace('description = "Jaw at', 'description = 2026-10-27\nnote = "Jaw at')
        with tempfile.TemporaryDirectory(prefix='rcef-cal-') as tmp:
            path = Path(tmp) / RECORD.name
            path.write_text(text, encoding='utf-8')
            problems = check.calibration_problems(Path(tmp), [])
            self.assertTrue(any('description' in p for p in problems), problems)


class CitingRules(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-cal-')
        self.addCleanup(temp.cleanup)
        self.records = Path(temp.name)
        shutil.copy(RECORD, self.records)

    def problems(self, rule):
        return check.calibration_problems(self.records, [rule])

    def test_a_rule_with_the_records_knots_is_accepted(self):
        self.assertEqual(self.problems(fixture_rule()), [])

    def test_knots_must_equal_the_frozen_knots_exactly(self):
        rule = fixture_rule()
        rule['operator']['knots'][2][1] = 0.41 + 1e-12
        problems = self.problems(rule)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn('fixture.jaw.calibrated', problems[0])
        rule = fixture_rule()
        rule['operator']['knots'] = rule['operator']['knots'][:-1]
        self.assertTrue(self.problems(rule))

    def test_the_rule_must_match_one_curve_of_the_record(self):
        rule = fixture_rule()
        rule['outputs'] = ['fixture.target.other']
        self.assertTrue(any('fixture.target.other' in p for p in self.problems(rule)))

    def test_a_rule_citing_a_missing_record_is_refused(self):
        rule = fixture_rule()
        rule['evidence'] = ['calibration.fixture.missing']
        self.assertTrue(any('fixture.missing' in p for p in self.problems(rule)))

    def test_a_rule_citing_a_record_must_use_its_curve(self):
        rule = fixture_rule()
        rule['operator'] = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
        self.assertTrue(any('piecewise_linear' in p for p in self.problems(rule)))

    def test_an_invalid_record_is_reported_once_with_its_file(self):
        (self.records / RECORD.name).write_text(RECORD.read_text(encoding='utf-8').replace(
            'licence = "CC-BY-SA-4.0"\n', ''), encoding='utf-8')
        problems = check.calibration_problems(self.records, [fixture_rule()])
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(RECORD.name, problems[0])

    def test_a_toml_file_among_the_records_is_refused(self):
        (self.records / 'stray.toml').write_text('x = 1\n')
        self.assertTrue(any('stray.toml' in p for p in check.calibration_problems(self.records, [])))

    def test_rules_without_a_record_are_ignored(self):
        rule = fixture_rule()
        rule['evidence'] = ['xr_fb2']
        rule['operator'] = {'id': 'affine', 'scale': 1.0, 'offset': 0.0}
        self.assertEqual(self.problems(rule), [])


class Repository(unittest.TestCase):
    def test_the_repository_records_and_rules_pass(self):
        self.assertEqual(check.calibration_problems(ROOT / 'calibration', check.pack_rules(ROOT)), [])

    def test_pack_rules_are_read_from_every_authoring_file(self):
        ids = {r['id'] for r in check.pack_rules(ROOT)}
        self.assertIn('fb2_vrm.blinkLeft', ids)
        self.assertIn('arkit.coefficient.eyeBlinkLeft.identity', ids)

    def test_records_are_not_toml_files_so_msf_tools_does_not_read_them_as_authoring(self):
        for directory in (ROOT / 'calibration', FIXTURES):
            self.assertEqual([p.name for p in directory.glob('*.toml')], [])

    def test_check_py_uses_only_the_standard_library(self):
        tree = ast.parse((ROOT / 'check.py').read_text(encoding='utf-8'))
        modules = {alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names}
        modules |= {node.module.split('.')[0] for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0}
        self.assertEqual(sorted(modules - set(sys.stdlib_module_names) - {'__future__'}), [])


if __name__ == '__main__':
    unittest.main()
