#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The three `*.to_canonical` identity maps and their signals, checked against tests/fixtures/identity_expectations.json."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import msf_character_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]


class IdentityLiterals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = shared_pack.document()
        cls.pack = shared_pack.pack()
        cls.expectations = json.loads((ROOT / 'tests/fixtures/identity_expectations.json').read_text())['rows']

    def ok(self, result):
        self.assertTrue(result.report.ok, result.report.to_dict())
        self.assertIsNotNone(result.value, result.report.to_dict())
        return result.value

    @staticmethod
    def frame(values):
        return {'timestamp': .125, 'values': values, 'validity': {k: True for k in values}}

    def evaluate(self, compiled, frames):
        before = deepcopy(frames)
        result = msf.evaluate_mapping(compiled, frames)
        self.assertEqual(frames, before)
        return result

    def assert_literals(self, document):
        signals = {s['id']: s for s in document['signals']}
        mappings = {m['id']: m['rules'] for m in document['mappings']}
        for row in self.expectations:
            for endpoint in ('source', 'target'):
                sid = row['input_id'] if endpoint == 'source' else row['output_id']
                actual = signals[sid]
                for key, value in row[f'expected_{endpoint}_fields'].items():
                    observed = actual['metadata'][key] if key in ('provider_basis', 'definition') else actual[key]
                    self.assertEqual(observed, value, (sid, key))
                for key in row[f'{endpoint}_fields_required_absent']:
                    self.assertNotIn(key, actual, (sid, key))
            rule = next(r for r in mappings[row['mapping_id']] if r['id'] == row['expected_rule']['id'])
            self.assertEqual(rule, row['expected_rule'])
        for mapping, count in (('arkit.to_canonical', 9), ('fb2.to_canonical', 8), ('vrcft_eye.to_canonical', 4)):
            expected = [r['expected_rule']['id'] for r in self.expectations if r['mapping_id'] == mapping]
            self.assertEqual(len(expected), count)
            self.assertEqual([r['id'] for r in mappings[mapping]], expected)

    def test_sem01_literal_identities_and_63_single_direction_comparisons(self):
        self.assertEqual(len(self.expectations), 21)
        self.assert_literals(self.document)
        self.assert_literals(json.loads((ROOT / 'generated/rcef.pack.json').read_text()))
        self.assertEqual(self.pack.to_bytes(), (ROOT / 'generated/rcef.pack.json').read_bytes())
        compiled = {}
        for mapping, source in (('arkit.to_canonical', 'arkit.coefficient'),
                                ('fb2.to_canonical', 'openxr.fb2'), ('vrcft_eye.to_canonical', 'vrcft.eye')):
            compiled[mapping] = shared_pack.mapping(mapping, source, 'rcef.canonical', False)
        comparisons = 0
        for mapping, mapping_compiled in compiled.items():
            rows = [r for r in self.expectations if r['mapping_id'] == mapping]
            peers = [r['input_id'] for r in rows]
            # One frame per (signal, value), and each frame sets a single signal. Frames
            # are evaluated independently, so one call covers the whole map.
            cases, frames = [], []
            for row in rows:
                for value, expected in ((0., 0.), (.25, .25), (1., 1.)):
                    values = dict.fromkeys(peers, 0.)
                    values[row['input_id']] = value
                    cases.append((row, value, expected))
                    frames.append(self.frame(values))
            samples = self.ok(self.evaluate(mapping_compiled, frames)).samples
            self.assertEqual(len(samples), len(cases))
            for (row, value, expected), sample in zip(cases, samples):
                with self.subTest(signal=row['input_id'], value=value):
                    self.assertEqual(sample['values'][row['output_id']], expected)
                    self.assertEqual(sample['timestamp'], .125)
                    self.assertIs(sample['validity'][row['output_id']], True)
                    comparisons += 1
        self.assertEqual(comparisons, 63)
        raw = compiled['vrcft_eye.to_canonical']
        values = {'vrcft.eye.Left.Openness': 1.5e308, 'vrcft.eye.Right.Openness': -3.,
                  'vrcft.eye.Left.PupilDiameter_MM': -3., 'vrcft.eye.Right.PupilDiameter_MM': 1.5e308}
        sample = self.ok(self.evaluate(raw, [self.frame(values)])).samples[0]
        self.assertEqual(dict(sample['values']), {'rcef.' + k: v for k, v in values.items()})

    def test_sem07_literal_audit_rejects_paired_relabels_and_invented_neutral(self):
        for cause in ('neutral', 'side', 'units', 'definition'):
            with self.subTest(cause=cause):
                d = {**self.document, 'signals': deepcopy(self.document['signals'])}; signals = {s['id']: s for s in d['signals']}
                if cause == 'neutral': signals['rcef.vrcft.eye.Left.Openness']['neutral'] = 1.
                elif cause == 'side':
                    for sid in ('vrcft.eye.Left.Openness', 'rcef.vrcft.eye.Left.Openness'): signals[sid]['side'] = 'shared'
                elif cause == 'units':
                    for sid in ('vrcft.eye.Left.PupilDiameter_MM', 'rcef.vrcft.eye.Left.PupilDiameter_MM'): signals[sid]['units'] = '1'
                else: signals['rcef.arkit.coefficient.eyeBlinkLeft']['metadata']['definition'] = 'Measured physiology.'
                with self.assertRaises(AssertionError): self.assert_literals(d)


if __name__ == '__main__':
    unittest.main(verbosity=2)
