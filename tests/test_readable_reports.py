# SPDX-License-Identifier: MIT
"""Public exporter checks with independently authored presentation expectations."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / 'scripts/export_reports.py'
FILES = {'inventory.csv', 'inventory.md', 'mappings.csv', 'mappings.md',
         'canonical_correspondence.csv', 'canonical_correspondence.md', 'SHA256SUMS'}


def fixture():
    def signal(identity, label, disposition='mapped', **extra):
        return dict(id=identity, label=label, value_type='scalar', units='1',
                    domain={'min': 0.0, 'max': 1.0}, calibration='provider-owned',
                    disposition=disposition, evidence=['source'],
                    evidence_status='verified_current', **extra)
    return {
        'id': 'rcef.fixture', 'license': 'CC-BY-SA-4.0', 'data_version': '0.1.1',
        'signals': [signal('canonical.blink', 'Canonical blink', neutral=0.0),
                    signal('source.left', 'Lid | left\nÉ', native_id='Left', native_default=1.0,
                           metadata={'reason': 'Keep provider calibration', 'native_index': 4}),
                    signal('source.right', 'Right', disposition='unresolved', native_id='Right'),
                    signal('orphan', '<hidden>', disposition='excluded')],
        'profiles': [dict(id='rcef.canonical', label='Canonical', signal_ids=['canonical.blink']),
                     dict(id='source', label='Source', signal_ids=['source.left', 'source.right'])],
        'mappings': [dict(id='source.to_canonical', source_profile='source',
                         target_profile='rcef.canonical', rules=[
                             dict(id='left.identity', inputs=['source.left'], outputs=['canonical.blink'],
                                  operator={'id': 'identity'}, disposition='mapped', mapping_quality='exact',
                                  assumptions=['Provider only'], loss_annotations=[], evidence=['source']),
                             dict(id='right.ambiguous', inputs=['source.right'], outputs=['canonical.blink'],
                                  operator={'id': 'identity'}, disposition='unresolved',
                                  assumptions=['Calibration unknown'], loss_annotations=[], evidence=['source'])])],
        'evidence': [dict(id='source', url='https://example.org/source', claim='Native facts')],
    }


class ReadableReports(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rcef-readable-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'generated').mkdir()
        self.pack = self.root / 'generated/rcef.pack.json'
        self.pack.write_text(json.dumps(fixture(), ensure_ascii=False) + '\n', encoding='utf-8')
        self.original = self.pack.read_bytes()

    def run_export(self, write=False):
        return subprocess.run([sys.executable, '-B', '-s', str(EXPORTER), '--root', str(self.root),
                               *(['--write'] if write else [])], capture_output=True,
                              timeout=15, text=True)

    def write(self):
        run = self.run_export(True)
        self.assertEqual(run.returncode, 0, run.stderr)

    def csv_rows(self, name):
        return list(csv.DictReader(io.StringIO((self.root / 'reports' / name).read_text(encoding='utf-8'))))

    def test_complete_outputs_checksums_and_input_preservation(self):
        self.write()
        directory = self.root / 'reports'
        self.assertEqual({p.name for p in directory.iterdir()}, FILES)
        self.assertEqual(self.pack.read_bytes(), self.original)
        sums = dict(line.split('  ', 1)[::-1] for line in (directory / 'SHA256SUMS').read_text().splitlines())
        self.assertEqual(set(sums), FILES - {'SHA256SUMS'})
        for name, digest in sums.items():
            self.assertEqual(hashlib.sha256((directory / name).read_bytes()).hexdigest(), digest)
        self.assertIn(hashlib.sha256(self.original).hexdigest(), (directory / 'inventory.md').read_text())

    def test_inventory_is_complete_and_keeps_neutral_distinct_from_default(self):
        self.write()
        rows = self.csv_rows('inventory.csv')
        self.assertEqual([r['signal_id'] for r in rows],
                         ['canonical.blink', 'source.left', 'source.right', 'orphan'])
        self.assertEqual(rows[0]['neutral'], '0.0')
        self.assertEqual(rows[1]['neutral'], '')
        self.assertEqual(rows[1]['native_default'], '1.0')
        self.assertEqual(rows[1]['native_index'], '4')
        self.assertEqual(rows[1]['label'], 'Lid | left\nÉ')
        self.assertEqual(rows[2]['disposition'], 'unresolved')
        self.assertEqual(rows[3]['profile_id'], '')
        self.assertEqual(rows[3]['disposition'], 'excluded')

    def test_markdown_preserves_readable_text_and_escapes_table_and_html(self):
        self.write()
        text = (self.root / 'reports/inventory.md').read_text(encoding='utf-8')
        self.assertIn('Lid \\| left<br>É', text)
        self.assertIn('&lt;hidden&gt;', text)
        self.assertIn('4 distinct signals', text)
        self.assertIn('2 profiles', text)
        self.assertIn('Keep provider calibration', text)
        self.assertIn('CC-BY-SA-4.0', text)

    def test_correspondences_use_only_authored_rules_and_mark_unresolved(self):
        self.write()
        rows = self.csv_rows('canonical_correspondence.csv')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['canonical_id'], 'canonical.blink')
        self.assertIn('Left', rows[0]['source'])
        self.assertIn('left.identity', rows[0]['source'])
        self.assertIn('mapped', rows[0]['source'])
        self.assertIn('right.ambiguous', rows[0]['source'])
        self.assertIn('unresolved', rows[0]['source'])
        self.assertNotIn('orphan', rows[0]['source'])
        rows = self.csv_rows('mappings.csv')
        self.assertEqual([r['rule_id'] for r in rows], ['left.identity', 'right.ambiguous'])
        self.assertEqual(json.loads(rows[1]['assumptions']), ['Calibration unknown'])

    def test_drift_check_is_read_only_and_regeneration_is_deterministic(self):
        self.assertNotEqual(self.run_export().returncode, 0)
        self.assertFalse((self.root / 'reports').exists())
        self.write()
        directory = self.root / 'reports'
        baseline = {p.name: p.read_bytes() for p in directory.iterdir()}
        self.assertEqual(self.run_export().returncode, 0)
        self.write()
        self.assertEqual({p.name: p.read_bytes() for p in directory.iterdir()}, baseline)
        (directory / 'inventory.csv').write_bytes(baseline['inventory.csv'] + b'changed\n')
        changed = (directory / 'inventory.csv').read_bytes()
        self.assertNotEqual(self.run_export().returncode, 0)
        self.assertEqual((directory / 'inventory.csv').read_bytes(), changed)

    def test_duplicate_signal_and_missing_reference_refuse_before_output(self):
        for mutate in ('duplicate', 'missing'):
            value = fixture()
            if mutate == 'duplicate':
                value['signals'].append(dict(value['signals'][0]))
            else:
                value['profiles'][0]['signal_ids'].append('absent')
            self.pack.write_text(json.dumps(value))
            run = self.run_export(True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse((self.root / 'reports').exists())

    def test_invalid_json_duplicate_keys_and_nonfinite_refuse(self):
        for raw in ('{"id":"a","id":"b"}', '{"signals":[NaN]}', '{bad json'):
            self.pack.write_text(raw)
            self.assertNotEqual(self.run_export(True).returncode, 0)
            self.assertFalse((self.root / 'reports').exists())

    def test_output_symlink_and_input_hardlink_refuse(self):
        directory = self.root / 'reports'
        directory.mkdir()
        output = directory / 'inventory.csv'
        output.symlink_to(self.pack)
        self.assertNotEqual(self.run_export(True).returncode, 0)
        self.assertEqual(self.pack.read_bytes(), self.original)
        output.unlink()
        output.hardlink_to(self.pack)
        self.assertNotEqual(self.run_export(True).returncode, 0)
        self.assertEqual(self.pack.read_bytes(), self.original)

    def test_output_directory_symlink_refuses(self):
        other = self.root / 'other'
        other.mkdir()
        (self.root / 'reports').symlink_to(other, target_is_directory=True)
        self.assertNotEqual(self.run_export(True).returncode, 0)
        self.assertEqual(list(other.iterdir()), [])

    def test_multi_profile_rule_displays_every_required_input(self):
        value = fixture()
        value['signals'].append(dict(value['signals'][1], id='outside.partner',
                                     native_id='Partner', label='Outside partner'))
        value['profiles'].append(dict(id='outside', label='Outside', signal_ids=['outside.partner']))
        value['mappings'][0]['rules'].append(dict(
            id='coupled.mean', inputs=['source.left', 'outside.partner'], outputs=['canonical.blink'],
            operator={'id': 'weighted_sum', 'weights': [0.5, 0.5]}, disposition='mapped',
            mapping_quality='approximate', assumptions=['Both provider inputs required'],
            loss_annotations=[], evidence=['source']))
        self.pack.write_text(json.dumps(value))
        self.write()
        row = self.csv_rows('canonical_correspondence.csv')[0]
        for profile in ('source', 'outside'):
            relation = next(cell for cell in row[profile].split('; ') if 'coupled.mean' in cell)
            self.assertIn('Left + Partner', relation)


if __name__ == '__main__':
    # Keep the acceptance runner's explicit tooling option compatible; these
    # presentation tests use stdlib only and do not load that dependency.
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--tools-path')
    _, remaining = parser.parse_known_args()
    unittest.main(argv=[sys.argv[0], *remaining])
