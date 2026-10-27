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
CHANNEL = 'fixture.source.jaw'
SCAN_NOTE = ('Identity modes come from ICT-FaceKit, which derives them from light-stage scans of real people; '
             'they are used only as geometry.')


def fixture_rule():
    return json.loads((FIXTURES / 'fixture_rule.json').read_text(encoding='utf-8'))


def refreeze(record):
    record['held_out']['frozen_sha256'] = check.frozen_sha256(record)
    return record


class Records(unittest.TestCase):
    def setUp(self):
        self.record = check.load_record(RECORD)

    def problems(self, record=None, name='fixture.jaw-gain'):
        return check.record_problems(self.record if record is None else record, name)

    def changed(self, change, freeze=False):
        record = deepcopy(self.record)
        change(record)
        return self.problems(refreeze(record) if freeze else record)

    def assertRefused(self, change, *words, freeze=False):
        problems = self.changed(change, freeze)
        self.assertTrue(problems, 'the change was accepted')
        for word in words:
            self.assertTrue(any(word in p for p in problems), problems)

    def test_the_fixture_record_is_valid(self):
        self.assertEqual(self.problems(), [])

    def test_the_id_must_be_the_file_name(self):
        self.assertTrue(any('fixture.other' in p for p in self.problems(name='fixture.other')))

    def test_required_fields_and_their_types(self):
        for field in ('version', 'scope', 'method', 'channels', 'reference_rig', 'inputs', 'renderer', 'code_commit',
                      'training', 'held_out', 'evaluation', 'curves', 'cells', 'licence', 'limitations'):
            with self.subTest(field):
                self.assertRefused(lambda r: r.pop(field), field)
        self.assertRefused(lambda r: r.update(limitations=[]), 'limitations')
        self.assertRefused(lambda r: r.update(channels=CHANNEL), 'channels')
        self.assertRefused(lambda r: r.update(version=0), 'version')
        self.assertRefused(lambda r: r.update(surprise=1), 'surprise')

    def test_only_software_calibration_is_accepted_for_now(self):
        self.assertRefused(lambda r: r.update(status='calibrated_measured'), 'calibrated_measured')
        self.assertRefused(lambda r: r.update(status='verified_current'), 'verified_current')

    def test_the_record_states_it_is_software_only(self):
        self.assertRefused(lambda r: r.update(scope='calibrated on a Quest Pro'), 'scope', freeze=True)

    def test_placeholder_limitations_are_refused(self):
        self.assertRefused(lambda r: r.update(limitations=['ok']), 'limitations', freeze=True)
        self.assertRefused(lambda r: r['limitations'].append('TBD'), 'limitations', freeze=True)

    def test_records_using_ict_must_state_the_scan_origin(self):
        self.assertRefused(lambda r: r.update(reference_rig='ICT-FaceKit (neutral identity)'), 'scan_origin',
                           freeze=True)
        self.assertRefused(lambda r: r['inputs'][1].update(name='identity012.obj'), 'scan_origin', freeze=True)
        self.assertRefused(lambda r: r.update(reference_rig='ICT-FaceKit', scan_origin='Scanned.'), 'light-stage',
                           freeze=True)
        self.assertEqual(self.changed(lambda r: r.update(reference_rig='ICT-FaceKit', scan_origin=SCAN_NOTE),
                                      freeze=True), [])

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
        self.assertEqual(self.changed(lambda r: r['curves'][0].update(knots=[[-1.0, 1.0], [0.0, 0.0], [1.0, 0.0]]),
                                      freeze=True), [])

    def test_bounds_and_minimum_conditions_are_set_in_advance_for_every_channel(self):
        self.assertRefused(lambda r: r['evaluation'].update(min_conditions=19), '20', freeze=True)
        self.assertRefused(lambda r: r['evaluation']['bounds'].pop(CHANNEL), CHANNEL, freeze=True)
        self.assertRefused(lambda r: r['evaluation']['bounds'][CHANNEL].pop('p95'), 'p95', freeze=True)
        self.assertRefused(lambda r: r['evaluation']['bounds'][CHANNEL].update(neutral=-1.0), 'neutral', freeze=True)
        self.assertRefused(lambda r: r['evaluation']['bounds'][CHANNEL].update(p95=0.15000001), 'frozen_sha256')
        self.assertRefused(lambda r: r['evaluation'].update(min_conditions=20), 'frozen_sha256')

    def test_each_cell_has_enough_conditions_its_failures_and_its_three_metrics(self):
        self.assertRefused(lambda r: r['cells'][0].update(conditions=23), 'min_conditions')
        self.assertRefused(lambda r: r['cells'][0].update(conditions=25), 'held_out.count')
        self.assertRefused(lambda r: r['cells'][0].pop('failures'), 'failures')
        self.assertRefused(lambda r: r['cells'][0].update(failures=25), 'failures')
        self.assertRefused(lambda r: r['cells'][0].pop('p95'), 'p95')
        self.assertRefused(lambda r: r['cells'][0].update(median=0.05, p95=0.04), 'p95')
        self.assertRefused(lambda r: r['cells'][0].update(neutral=-0.01), 'neutral')
        self.assertRefused(lambda r: r['cells'][0].update(channel='fixture.source.other'), 'fixture.source.other')
        self.assertRefused(lambda r: r['cells'][0].pop('identity'), 'identity')

    def test_a_failing_cell_is_a_valid_negative_result(self):
        self.assertEqual(self.changed(lambda r: r['cells'][0].update(failures=2, p95=0.4)), [])

    def test_the_frozen_part_cannot_change_without_a_new_hash(self):
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
        self.assertNotEqual(check.held_out_seeds(refreeze(other))[:3], seeds[:3])
        self.assertRefused(lambda r: r['held_out'].update(seed_rule='random'), 'seed_rule')
        self.assertRefused(lambda r: r['held_out'].update(count=0), 'count')

    def test_a_toml_date_is_refused_not_a_crash(self):
        text = RECORD.read_text(encoding='utf-8').replace('description = "Jaw at', 'description = 2026-10-27\nnote = "Jaw at')
        with tempfile.TemporaryDirectory(prefix='rcef-cal-') as tmp:
            path = Path(tmp) / RECORD.name
            path.write_text(text, encoding='utf-8')
            shutil.copy(FIXTURES / 'FREEZES', tmp)
            problems = check.calibration_problems(Path(tmp), [])
            self.assertTrue(any('description' in p for p in problems), problems)


class Ledger(unittest.TestCase):
    """Each record's frozen hash is first written to calibration/FREEZES, which only grows."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-cal-')
        self.addCleanup(temp.cleanup)
        self.records = Path(temp.name)
        shutil.copy(RECORD, self.records)
        self.record = check.load_record(RECORD)
        self.line = (FIXTURES / 'FREEZES').read_text(encoding='utf-8').strip().splitlines()[-1]

    def write(self, record=None, lines=()):
        if record is not None:
            text = RECORD.read_text(encoding='utf-8')
            for old, new in record:
                assert old in text, old
                text = text.replace(old, new)
            path = self.records / RECORD.name
            path.write_text(text, encoding='utf-8')
            loaded = check.load_record(path)
            path.write_text(text.replace(self.record['held_out']['frozen_sha256'], check.frozen_sha256(loaded)),
                            encoding='utf-8')
        (self.records / 'FREEZES').write_text('# id version frozen_sha256 date [reason]\n' + '\n'.join(lines) + '\n')
        return check.calibration_problems(self.records, [])

    def refit(self):
        return [('[0.5, 0.41]', '[0.5, 0.40]')]

    def frozen(self):
        return check.frozen_sha256(check.load_record(self.records / RECORD.name))

    def test_a_record_frozen_in_the_ledger_is_accepted(self):
        self.assertEqual(self.write(lines=[self.line]), [])

    def test_a_record_missing_from_the_ledger_is_refused(self):
        problems = self.write(lines=[])
        self.assertTrue(any('FREEZES' in p for p in problems), problems)

    def test_rehashing_an_edited_record_does_not_re_roll_the_seeds(self):
        problems = self.write(self.refit(), [self.line])
        self.assertTrue(any('FREEZES' in p and 'fixture.jaw-gain' in p for p in problems), problems)

    def test_a_refit_needs_a_new_version_with_a_reason(self):
        self.write(self.refit() + [('version = 1', 'version = 2')], [self.line])
        new = self.frozen()
        self.assertEqual(self.write(self.refit() + [('version = 1', 'version = 2')],
                                    [self.line, f'fixture.jaw-gain v2 {new} 2026-10-28 knot at 0.5 refitted after a '
                                                'renderer fix']), [])
        problems = self.write(self.refit() + [('version = 1', 'version = 2')],
                              [self.line, f'fixture.jaw-gain v2 {new} 2026-10-28'])
        self.assertTrue(any('reason' in p for p in problems), problems)

    def test_a_record_older_than_its_latest_freeze_is_refused(self):
        line = f'fixture.jaw-gain v2 {"5" * 64} 2026-10-28 refitted after a renderer fix'
        problems = self.write(lines=[self.line, line])
        self.assertTrue(any('v2' in p for p in problems), problems)

    def test_ledger_lines_must_be_well_formed_and_in_order(self):
        sha = self.record['held_out']['frozen_sha256']
        cases = {'fixture.jaw-gain 1 {sha} 2026-10-27': 'version',
                 'fixture.jaw-gain v1 {short} 2026-10-27': 'sha256',
                 'fixture.jaw-gain v1 {sha} 27/10/2026': 'date',
                 'fixture.jaw-gain v1 {sha}': 'date'}
        for line, word in cases.items():
            with self.subTest(line):
                problems = self.write(lines=[line.format(sha=sha, short=sha[:10])])
                self.assertTrue(any(word in p for p in problems), problems)
        problems = self.write(lines=[self.line, self.line])
        self.assertTrue(any('twice' in p or 'v1' in p for p in problems), problems)
        problems = self.write(lines=[self.line, f'fixture.jaw-gain v3 {"5" * 64} 2026-10-28 skipped a version'])
        self.assertTrue(any('v3' in p for p in problems), problems)
        problems = self.write(lines=[f'other.fit v1 {"6" * 64} 2026-10-28', self.line])
        self.assertTrue(any('date' in p for p in problems), problems)


class CitingRules(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-cal-')
        self.addCleanup(temp.cleanup)
        self.records = Path(temp.name)
        shutil.copy(RECORD, self.records)
        shutil.copy(FIXTURES / 'FREEZES', self.records)

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

    def test_a_rule_needs_every_cell_of_its_channel_to_pass_the_frozen_bounds(self):
        path = self.records / RECORD.name
        for old, new in (('failures = 0', 'failures = 1'), ('p95 = 0.041', 'p95 = 0.16'),
                         ('neutral = 0.004', 'neutral = 0.031'),
                         ('median = 0.012\np95 = 0.041', 'median = 0.051\np95 = 0.06')):
            with self.subTest(new):
                path.write_text(RECORD.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
                self.assertEqual(check.calibration_problems(self.records, []), [], 'a negative result is valid')
                problems = self.problems(fixture_rule())
                self.assertTrue(any('fails' in p and 'fixture.jaw.calibrated' in p for p in problems), problems)

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
        self.assertTrue((ROOT / 'calibration/FREEZES').is_file())

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
