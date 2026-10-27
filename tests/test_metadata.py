#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Signal metadata, the provider identities, and invariants of the authored data and its outputs."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

import msf_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]

# Literal F-9/F-10/F-18 and reviewed A-03 expectations. The gaze parameter
# documentation and actual EParam getters distinguish anatomy from direction;
# Apple's matrix describes eye orientation. No substring classification is used.
# Entries are (ID, native name/label, inventory position, region, anatomical side).
ROWS = (
    ('godot.base.FT_MOUTH_CLOSED', 'FT_MOUTH_CLOSED', 39, 'mouth', 'shared'),
    ('vrcft.artist.base.MouthClosed', 'MouthClosed', 39, 'mouth', 'shared'),
    ('vrcft.parameter.float.v2.MouthClosed', 'v2/MouthClosed', 33, 'mouth', 'shared'),
    ('vrcft.transport.MouthClosed', 'MouthClosed', 29, 'mouth', 'shared'),
    ('vrcft.parameter.float.v2.EyeLeftX', 'v2/EyeLeftX', 0, 'gaze', 'left'),
    ('vrcft.parameter.float.v2.EyeLeftY', 'v2/EyeLeftY', 1, 'gaze', 'left'),
    ('vrcft.parameter.float.v2.EyeRightX', 'v2/EyeRightX', 2, 'gaze', 'right'),
    ('vrcft.parameter.float.v2.EyeRightY', 'v2/EyeRightY', 3, 'gaze', 'right'),
    ('vrcft.parameter.float.v2.EyeX', 'v2/EyeX', 88, 'gaze', 'shared'),
    ('vrcft.parameter.float.v2.EyeY', 'v2/EyeY', 89, 'gaze', 'shared'),
    ('arkit.ancillary.leftEyeTransform', 'leftEyeTransform', 0, 'gaze', 'left'),
)
DISPOSITIONS = {'mapped', 'unresolved', 'excluded', 'unsupported'}
CSV_FIELDS = ['id', 'label', 'value_type', 'units', 'disposition', 'evidence_status']
INVENTORY_SNAPSHOT = ROOT / 'tests/fixtures/inventory_snapshot.csv'
# Disposition is left out on purpose: mapping work changes dispositions, while
# the inventory itself should only change through a reviewed data correction.
SNAPSHOT_FIELDS = ['id', 'native_id', 'label', 'units', 'min', 'max', 'native_index', 'inventory_ordinal',
                   'region', 'side', 'coupling', 'calibration']


def inventory_rows(document):
    """One row per signal, in authoring order, with an empty cell for an absent value."""
    def cell(value):
        return '' if value is None else value if isinstance(value, str) else json.dumps(value)
    rows = []
    for s in document['signals']:
        values = {**s, **s.get('domain', {}), **{k: s.get('metadata', {}).get(k)
                                               for k in ('native_index', 'inventory_ordinal')}}
        rows.append([cell(values.get(field)) for field in SNAPSHOT_FIELDS])
    return rows


def write_inventory_snapshot(document):
    with INVENTORY_SNAPSHOT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(SNAPSHOT_FIELDS)
        writer.writerows(inventory_rows(document))

# Exact admitted native subset, independent of the mapping's declared rules.
IDENTITIES = (
    ('arkit.to_canonical', 'arkit.coefficient', (
        ('eyeBlinkLeft', 'eyelid', 'left'), ('eyeBlinkRight', 'eyelid', 'right'),
        ('jawForward', 'jaw', 'shared'), ('jawOpen', 'jaw', 'shared'),
        ('browDownLeft', 'brow', 'left'), ('browDownRight', 'brow', 'right'),
        ('browInnerUp', 'brow', 'shared'), ('browOuterUpLeft', 'brow', 'left'),
        ('browOuterUpRight', 'brow', 'right'),
    )),
    ('fb2.to_canonical', 'openxr.fb2', (
        ('XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB', 'gaze', 'left'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB', 'gaze', 'right'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB', 'gaze', 'left'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB', 'gaze', 'right'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB', 'gaze', 'left'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB', 'gaze', 'right'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB', 'gaze', 'left'),
        ('XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB', 'gaze', 'right'),
    )),
    ('vrcft_eye.to_canonical', 'vrcft.eye', (
        ('Left.Openness', 'eyelid', 'left'), ('Left.PupilDiameter_MM', 'pupil', 'left'),
        ('Right.Openness', 'eyelid', 'right'), ('Right.PupilDiameter_MM', 'pupil', 'right'),
    )),
)



class Metadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authoring = shared_pack.document()
        cls.pack = shared_pack.pack()
        cls.generated = json.loads((ROOT / 'generated/rcef.pack.json').read_text())

    def ok(self, result):
        self.assertIsNotNone(result.value, result.report.to_dict())
        self.assertFalse(any(d.severity == 'error' for d in result.report.diagnostics))
        return result.value

    def assert_rows(self, document):
        signals = {s['id']: s for s in document['signals']}
        for sid, name, ordinal, region, side in ROWS:
            with self.subTest(signal=sid):
                row = signals[sid]
                self.assertEqual((row['region'], row['side']), (region, side))
                self.assertEqual((row['native_id'], row['label']), (name, name))
                position = row['metadata'].get('native_index', row['metadata'].get('inventory_ordinal'))
                self.assertEqual(position, ordinal)

    def test_primary_metadata_rows_in_authoring(self):
        self.assert_rows(self.authoring)

    def test_primary_metadata_rows_in_generated_pack(self):
        self.assert_rows(self.generated)

    def test_ids_unique_and_order_stable(self):
        document = self.authoring
        for kind in ('signals', 'profiles', 'mappings', 'evidence'):
            ids = [item['id'] for item in document[kind]]
            self.assertEqual(len(ids), len(set(ids)), f'duplicate {kind} ID')
        rule_ids = [r['id'] for m in document['mappings'] for r in m['rules']]
        self.assertEqual(len(rule_ids), len(set(rule_ids)), 'duplicate rule ID')
        for profile in document['profiles']:
            self.assertEqual(len(profile['signal_ids']), len(set(profile['signal_ids'])), profile['id'])
        # The generated pack keeps authoring order everywhere, and compiling again
        # gives the same bytes.
        for kind in ('signals', 'profiles', 'mappings', 'evidence'):
            self.assertEqual([i['id'] for i in self.generated[kind]], [i['id'] for i in document[kind]], kind)
        self.assertEqual([[r['id'] for r in m['rules']] for m in self.generated['mappings']],
                         [[r['id'] for r in m['rules']] for m in document['mappings']])
        self.assertEqual(self.ok(msf.compile_pack(self.ok(msf.validate_authoring(document)))).to_bytes(),
                         self.pack.to_bytes())

    def test_inventory_matches_reviewed_snapshot(self):
        with INVENTORY_SNAPSHOT.open(encoding='utf-8', newline='') as handle:
            expected = list(csv.reader(handle))
        self.assertEqual(expected[0], SNAPSHOT_FIELDS)
        actual = inventory_rows(self.authoring)
        self.assertEqual([r[0] for r in actual], [r[0] for r in expected[1:]], 'signal IDs or order changed')
        for row, wanted in zip(actual, expected[1:]):
            self.assertEqual(dict(zip(SNAPSHOT_FIELDS, row)), dict(zip(SNAPSHOT_FIELDS, wanted)), row[0])

    def test_version_axes_and_rendered_bytes(self):
        self.assertEqual(self.authoring['data_version'], self.generated['data_version'])
        self.assertRegex(self.authoring['data_version'], r'^[0-9]+\.[0-9]+\.[0-9]+$')
        for document in (self.authoring, self.generated):
            self.assertEqual(document['schema_version'], '1.0')
            self.assertEqual(document['operator_version'], '1.1')
        self.assertEqual(self.pack.to_bytes(), (ROOT / 'generated/rcef.pack.json').read_bytes())

    def test_dispositions_partition_signals_and_rules_reference_mapped_signals(self):
        signals = {s['id']: s for s in self.authoring['signals']}
        counts = Counter(s['disposition'] for s in signals.values())
        self.assertLessEqual(set(counts), DISPOSITIONS)
        self.assertEqual(sum(counts.values()), len(self.authoring['signals']))
        members = {sid for p in self.authoring['profiles'] for sid in p['signal_ids']}
        self.assertLessEqual(members, set(signals), 'profile lists an unknown signal')
        self.assertEqual(members, set(signals), 'signal belongs to no profile')
        endpoints = set()
        for mapping in self.authoring['mappings']:
            for rule in mapping['rules']:
                refs = [*rule['inputs'], *rule['outputs']]
                self.assertLessEqual(set(refs), set(signals), rule['id'])
                if rule['disposition'] == 'mapped':
                    endpoints.update(refs)
        # A signal is mapped exactly when some mapped rule uses it.
        self.assertEqual(endpoints, {sid for sid, s in signals.items() if s['disposition'] == 'mapped'})

    def test_matrix_exclusion_and_unedited_direction_controls(self):
        signals = {s['id']: s for s in self.authoring['signals']}
        matrix = signals['arkit.ancillary.leftEyeTransform']
        self.assertEqual(matrix['disposition'], 'excluded')
        self.assertEqual(matrix['metadata']['native_value_type'], 'matrix4x4')
        self.assertEqual(matrix['value_type'], 'scalar')  # Inventory placeholder in scalar wire 1.0.
        self.assertEqual(matrix['domain'], {})
        # Baseline lookLeft/lookRight side labels describe directions, not
        # unilateral anatomy (F-52). Preserve them in this eleven-row patch;
        # any taxonomy repair needs its own reviewed data correction.
        for direction, side in (('lookLeft', 'left'), ('lookRight', 'right'),
                                ('lookUp', 'shared'), ('lookDown', 'shared')):
            self.assertEqual(signals['vrm.preset.' + direction]['side'], side)
        for name in ('EyeX', 'EyeY'):
            self.assertEqual(signals['vrcft.parameter.float.v2.' + name]['coupling'], 'composite')
        rule_refs = {sid for m in self.authoring['mappings'] for r in m['rules']
                     for sid in (*r['inputs'], *r['outputs'])}
        self.assertNotIn(matrix['id'], rule_refs)

    def test_all_21_native_scalar_bases(self):
        signals = {s['id']: s for s in self.authoring['signals']}
        checked = 0
        for _, profile, entries in IDENTITIES:
            for name, region, side in entries:
                sid = profile + '.' + name
                with self.subTest(signal=sid):
                    if profile == 'arkit.coefficient':
                        basis = f'arkit.coefficient.v1:{name}: face-relative native neutral-to-maximum coefficient'
                    elif profile == 'openxr.fb2':
                        basis = f'openxr.fb2.v1:{name}: native direction-specific angle fraction; maximum angle unspecified'
                    else:
                        basis = f'vrcft.eye.storage.v1:{name}'
                    expected = {'value_type': 'scalar', 'calibration': basis, 'region': region,
                                'side': side, 'units': 'mm' if region == 'pupil' else '1',
                                'domain': {} if profile == 'vrcft.eye' else {'min': 0.0, 'max': 1.0}}
                    if profile != 'vrcft.eye':
                        expected['neutral'] = 0.0
                    if profile == 'openxr.fb2':
                        expected['coupling'] = 'opposing_direction_exclusive'
                    elif name == 'browInnerUp':
                        expected['coupling'] = 'bilateral_shared'
                    keys = ('value_type', 'calibration', 'region', 'side', 'units', 'domain', 'neutral', 'coupling')
                    for row in (signals[sid], signals['rcef.' + sid]):
                        self.assertEqual({k: row[k] for k in keys if k in row}, expected)
                    if name in ('Left.Openness', 'Right.Openness'):
                        self.assertEqual(signals[sid]['native_default'], 1.0)
                    checked += 1
        self.assertEqual(checked, 21)

    def test_63_independent_scalar_endpoints(self):
        assertions = 0
        for mapping, profile, entries in IDENTITIES:
            compiled = shared_pack.mapping(mapping, profile, 'rcef.canonical', False)
            input_ids = [profile + '.' + name for name, _, _ in entries]
            frames = [{'timestamp': float(i), 'values': {sid: value for sid in input_ids},
                       'validity': {sid: True for sid in input_ids}}
                      for i, value in enumerate((0.0, 0.25, 1.0))]
            samples = self.ok(msf.evaluate_mapping(compiled, frames)).samples
            self.assertEqual(len(samples), 3)
            for i, value in enumerate((0.0, 0.25, 1.0)):
                self.assertEqual(samples[i]['timestamp'], float(i))
                self.assertEqual(set(samples[i]['values']), {'rcef.' + sid for sid in input_ids})
                self.assertEqual(dict(samples[i]['validity']), {'rcef.' + sid: True for sid in input_ids})
                for sid in input_ids:
                    with self.subTest(mapping=mapping, signal=sid, value=value):
                        self.assertEqual(samples[i]['values']['rcef.' + sid], value)
                    assertions += 1
        self.assertEqual(assertions, 63)

    def test_csv_coverage_and_checksums_agree_with_pack(self):
        outputs = ROOT / 'generated'
        pack_bytes = (outputs / 'rcef.pack.json').read_bytes()
        document = self.generated
        profiles = [p['id'] for p in document['profiles']]
        members = {p['id']: set(p['signal_ids']) for p in document['profiles']}
        rows = list(csv.reader(io.StringIO((outputs / 'rcef_mapping.csv').read_text(encoding='utf-8'))))
        self.assertEqual(rows[0], [*CSV_FIELDS, *profiles])
        self.assertEqual([r[0] for r in rows[1:]], [s['id'] for s in document['signals']])
        for row, signal in zip(rows[1:], document['signals']):
            self.assertEqual(row[CSV_FIELDS.index('disposition')], signal['disposition'], signal['id'])
            self.assertEqual(row[len(CSV_FIELDS):],
                             ['1' if signal['id'] in members[p] else '' for p in profiles], signal['id'])
        coverage = json.loads((outputs / 'coverage.json').read_text())
        self.assertEqual(coverage['pack_sha256'], hashlib.sha256(pack_bytes).hexdigest())
        rules = [r for m in document['mappings'] for r in m['rules']]
        self.assertEqual(coverage['totals'], {'signals': len(document['signals']), 'profiles': len(profiles),
                                              'rules': len(rules), 'evidence': len(document['evidence'])})
        self.assertEqual({k: v for k, v in coverage['disposition_counts'].items() if v},
                         Counter(s['disposition'] for s in document['signals']))
        self.assertEqual(coverage['mapping_quality_counts'],
                         Counter(r['mapping_quality'] for r in rules if r['disposition'] == 'mapped'))
        checksums = {}
        for line in (outputs / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ', 1)
            self.assertNotIn(name, checksums)
            checksums[name] = digest
        self.assertEqual(set(checksums), {'rcef.pack.json', 'rcef_mapping.csv', 'coverage.json'})
        for name, expected in checksums.items():
            self.assertEqual(hashlib.sha256((outputs / name).read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    if sys.argv[1:] == ['--write-inventory-snapshot']:
        # After a reviewed data correction: rewrite the snapshot, then review its diff.
        write_inventory_snapshot(msf.load_authoring(ROOT).value.to_dict())
    else:
        unittest.main(verbosity=2)
