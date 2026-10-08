#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""R-DATA row semantics and preservation, independently bounded to data 0.1.1."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--tools-path', type=Path, default=os.environ.get('MSF_TOOLS_PATH'))
args, remaining = parser.parse_known_args()
if args.tools_path is None:
    parser.error('select the shared checkout with --tools-path or MSF_TOOLS_PATH')
TOOLS = Path(args.tools_path).resolve(strict=True)
sys.path.insert(0, str(TOOLS))
import msf_tools as msf

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
SIDE_EDITS = {
    'vrcft.parameter.float.v2.EyeLeftX', 'vrcft.parameter.float.v2.EyeLeftY',
    'vrcft.parameter.float.v2.EyeRightX', 'vrcft.parameter.float.v2.EyeRightY',
    'arkit.ancillary.leftEyeTransform',
}
REGION_EDITS = {row[0] for row in ROWS}

# Committed 282fc385 baseline fingerprints, captured before production edits.
# These freeze preservation only; the literal primary row table supplies meaning.
PRESERVED_STRUCTURE_SHA256 = '97da5e6f0c8ec771a51c5086ce0e92886a63bef51d77dd706de447216eba2038'
NAME_ORDER_SHA256 = 'be93863a39ed72d30f980306bd8441d422321dc3cddaad0b12368ae00c1844ce'
COVERAGE_STRUCTURE_SHA256 = 'd562fa95870a5c64cd0114163b1f6a01160b2be75793f46af5722c6a2c91a4dd'
CSV_SHA256 = 'bb82978b01f389c0e87ad6e18c3f5a0913f87e80af0c1d5de0aff4093b5c9591'
SELECTED_COUNTS = {
    'rcef.canonical': 21, 'arkit.ancillary': 1, 'arkit.coefficient': 52,
    'fixture': 5, 'fixture.source': 3, 'fixture.target': 2,
    'godot.base': 102, 'godot.blended': 41, 'mediapipe.label': 52,
    'openxr.ancillary': 10, 'openxr.fb': 63, 'openxr.fb2': 70,
    'openxr.visemes': 15, 'roblox.control': 50, 'vrcft.artist.base': 102,
    'vrcft.artist.blended': 42, 'vrcft.eye': 12, 'vrcft.parameter.encoding': 7,
    'vrcft.parameter.flags': 3, 'vrcft.parameter.float': 124,
    'vrcft.transport': 88, 'vrm.preset': 18,
}

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


def structural_hash(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode('utf-8')).hexdigest()


class Metadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if Path(msf.__file__).resolve().parent.parent != TOOLS:
            raise AssertionError(f'unexpected shared import: {msf.__file__}')
        loaded = msf.load_authoring(ROOT)
        if loaded.value is None:
            raise AssertionError(loaded.report.to_dict())
        cls.authoring = loaded.value.to_dict()
        compiled = msf.compile_pack(loaded.value)
        if compiled.value is None:
            raise AssertionError(compiled.report.to_dict())
        cls.pack = compiled.value
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

    def test_only_reviewed_fields_change(self):
        for label, document in [('authoring', self.authoring), ('generated', self.generated)]:
            with self.subTest(document=label):
                preserved = deepcopy(document)
                preserved.pop('data_version')
                for signal in preserved['signals']:
                    if signal['id'] in REGION_EDITS:
                        signal.pop('region')
                    if signal['id'] in SIDE_EDITS:
                        signal.pop('side')
                self.assertEqual(structural_hash(preserved), PRESERVED_STRUCTURE_SHA256,
                                 'extra value/basis/coupling/metadata/ID/order change')

    def test_version_axes_and_rendered_bytes(self):
        for document in (self.authoring, self.generated):
            with self.subTest(version=document['data_version']):
                self.assertEqual(document['data_version'], '0.1.1')
                self.assertEqual(document['schema_version'], '1.0')
                self.assertEqual(document['operator_version'], '1.0')
        self.assertEqual(self.pack.to_bytes(), (ROOT / 'generated/rcef.pack.json').read_bytes())

    def test_inventory_counts_names_and_order(self):
        signals = {s['id']: s for s in self.authoring['signals']}
        self.assertEqual(len(signals), 893)
        self.assertEqual(Counter(s['disposition'] for s in signals.values()),
                         {'mapped': 47, 'unresolved': 805, 'excluded': 35, 'unsupported': 6})
        self.assertEqual(len(self.authoring['evidence']), 27)
        self.assertEqual(sum(len(m['rules']) for m in self.authoring['mappings']), 24)
        counts = {p['id']: sum(signals[s]['metadata'].get('selected', True)
                               for s in p['signal_ids']) for p in self.authoring['profiles']}
        self.assertEqual(counts, SELECTED_COUNTS)
        self.assertEqual(structural_hash([[s['id'], s.get('native_id'), s['label']]
                                          for s in self.authoring['signals']]), NAME_ORDER_SHA256)

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
        target = self.ok(msf.profile_snapshot(self.pack, 'rcef.canonical'))
        assertions = 0
        for mapping, profile, entries in IDENTITIES:
            source = self.ok(msf.profile_snapshot(self.pack, profile))
            compiled = self.ok(msf.compile_mapping(self.pack, source, target, mapping))
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

    def test_csv_coverage_and_checksums_preservation(self):
        outputs = ROOT / 'generated'
        self.assertEqual(hashlib.sha256((outputs / 'rcef_mapping.csv').read_bytes()).hexdigest(), CSV_SHA256)
        coverage = json.loads((outputs / 'coverage.json').read_text())
        self.assertEqual(coverage.pop('pack_sha256'),
                         hashlib.sha256((outputs / 'rcef.pack.json').read_bytes()).hexdigest())
        self.assertEqual(structural_hash(coverage), COVERAGE_STRUCTURE_SHA256)
        checksums = {}
        for line in (outputs / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ', 1)
            self.assertNotIn(name, checksums)
            checksums[name] = digest
        self.assertEqual(set(checksums), {'rcef.pack.json', 'rcef_mapping.csv', 'coverage.json'})
        for name, expected in checksums.items():
            self.assertEqual(hashlib.sha256((outputs / name).read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
