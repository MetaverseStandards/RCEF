#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Consumer acceptance tests: scalar results against independent expected values, and refusal of bad authoring."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import msf_tools as msf

try:
    import shared_pack
except ModuleNotFoundError:  # run by file path from the repository root
    from tests import shared_pack

ROOT = Path(__file__).resolve().parents[1]


class Parity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = shared_pack.document()
        cls.pack = shared_pack.pack()
        # msf-tools rechecks the whole pack on every evaluation. The fixture
        # maps are evaluated many times, so they use a pack holding only them.
        fixtures = deepcopy(cls.document)
        fixtures['profiles'] = [p for p in fixtures['profiles'] if p['id'] in ('fixture.source', 'fixture.target')]
        kept = {s for p in fixtures['profiles'] for s in p['signal_ids']}
        fixtures['signals'] = [s for s in fixtures['signals'] if s['id'] in kept]
        fixtures['mappings'] = [m for m in fixtures['mappings'] if m['id'] in ('fixture.affine', 'fixture.bilateral')]
        cls.fixture_pack = msf.compile_pack(msf.validate_authoring(fixtures).value).value
        cls.source = msf.profile_snapshot(cls.fixture_pack, 'fixture.source').value
        cls.target = msf.profile_snapshot(cls.fixture_pack, 'fixture.target').value
        cls.fixtures = json.loads((ROOT / 'fixtures/mapping_samples.json').read_text())

    def ok(self, result):
        self.assertIsNotNone(result.value, result.report.to_dict())
        self.assertFalse(any(d.severity == 'error' for d in result.report.diagnostics))
        return result.value

    def rejected(self, result, code=None):
        self.assertIsNone(result.value, result.report.to_dict())
        codes = [d.code for d in result.report.diagnostics if d.severity == 'error']
        self.assertTrue(codes, result.report.to_dict())
        if code:
            self.assertIn(code, codes)

    def compile(self, mapping, approximation=False):
        return msf.compile_mapping(self.fixture_pack, self.source, self.target, mapping,
                                   allow_approximation=approximation)

    def frame(self, values, validity=None):
        return {'timestamp': 0.125, 'values': values,
                'validity': validity if validity is not None else {k: True for k in values}}

    def test_affine_analytical_endpoints_and_midpoint(self):
        compiled = self.ok(self.compile('fixture.affine'))
        frames = [self.frame({'fixture.affine.signed': f['input']}) for f in self.fixtures['affine']]
        evaluated = self.ok(msf.evaluate_mapping(compiled, frames))
        self.assertEqual([s['values']['fixture.affine.unit'] for s in evaluated.samples],
                         [f['expected'] for f in self.fixtures['affine']])
        self.assertTrue(all(s['timestamp'] == 0.125 for s in evaluated.samples))

    def test_bilateral_loss_opt_in_and_irrecoverable_asymmetry(self):
        self.rejected(self.compile('fixture.bilateral'))
        result = self.compile('fixture.bilateral', True)
        compiled = self.ok(result)
        self.assertTrue(any(loss.reason == 'asymmetry irrecoverable' for loss in result.report.losses))
        frames = [self.frame(dict(zip(('fixture.brow.left', 'fixture.brow.right'), f['input'])))
                  for f in self.fixtures['bilateral']]
        samples = self.ok(msf.evaluate_mapping(compiled, frames)).samples
        self.assertEqual([s['values']['fixture.brow.shared'] for s in samples],
                         [f['expected'] for f in self.fixtures['bilateral']])
        self.assertEqual(samples[0]['values'], samples[1]['values'])

    def test_all_provider_identities_share_explicit_calibration(self):
        signals = {s['id']: s for s in self.document['signals']}
        for mapping, profile in [('arkit.to_canonical', 'arkit.coefficient'),
                                 ('fb2.to_canonical', 'openxr.fb2'),
                                 ('vrcft_eye.to_canonical', 'vrcft.eye')]:
            with self.subTest(mapping=mapping):
                compiled = shared_pack.mapping(mapping, profile, 'rcef.canonical', False)
                rules = next(m['rules'] for m in self.document['mappings'] if m['id'] == mapping)
                values = {r['inputs'][0]: 0.25 for r in rules}
                sample = self.ok(msf.evaluate_mapping(compiled, [self.frame(values)])).samples[0]
                for rule in rules:
                    input_id, output_id = rule['inputs'][0], rule['outputs'][0]
                    self.assertEqual(signals[input_id]['calibration'], signals[output_id]['calibration'])
                    self.assertIn('provider', rule['assumptions'][-1].lower())
                    self.assertEqual(sample['values'][output_id], 0.25)

    def test_unresolved_cross_provider_refused(self):
        self.rejected(msf.compile_mapping(self.pack, shared_pack.snapshot('mediapipe.label'),
                                          shared_pack.snapshot('rcef.canonical'), 'survey.ambiguous', True))

    def test_invalid_missing_boolean_nonfinite_and_domain_samples(self):
        compiled = self.ok(self.compile('fixture.affine'))
        for frame in [self.frame({}), self.frame({'fixture.affine.signed': 0.0}, {'fixture.affine.signed': False}),
                      self.frame({'fixture.affine.signed': 0.0}, {}),
                      *[self.frame({'fixture.affine.signed': v})
                        for v in (True, '0.5', float('nan'), float('inf'), -1.01, 1.01)]]:
            with self.subTest(frame=str(frame)):
                self.rejected(msf.evaluate_mapping(compiled, [frame]))

    def test_output_domain_checked_without_clamping(self):
        document = deepcopy(self.document)
        rule = next(m for m in document['mappings'] if m['id'] == 'fixture.affine')['rules'][0]
        rule['operator']['scale'] = 2.0
        pack = self.ok(msf.compile_pack(self.ok(msf.validate_authoring(document))))
        compiled = self.ok(msf.compile_mapping(pack, self.ok(msf.profile_snapshot(pack, 'fixture.source')),
                                              self.ok(msf.profile_snapshot(pack, 'fixture.target')), 'fixture.affine'))
        self.rejected(msf.evaluate_mapping(compiled, [self.frame({'fixture.affine.signed': 1.0})]))

    def test_strict_authoring_duplicate_unknown_reference_and_operator(self):
        cases = []
        d = deepcopy(self.document); d['signals'].append(deepcopy(d['signals'][0])); cases.append(d)
        d = deepcopy(self.document); d['signals'][0]['surprise'] = True; cases.append(d)
        d = deepcopy(self.document); d['signals'][0]['label'] = 2; cases.append(d)
        d = deepcopy(self.document); d['signals'][0]['evidence'] = ['missing.evidence']; cases.append(d)
        d = deepcopy(self.document); d['profiles'][0]['signal_ids'].append('missing.signal'); cases.append(d)
        d = deepcopy(self.document); d['mappings'][0]['rules'][0]['operator']['id'] = 'clamp'; cases.append(d)
        d = deepcopy(self.document); d['signals'][0]['domain']['max'] = float('inf'); cases.append(d)
        for i, document in enumerate(cases):
            with self.subTest(case=i): self.rejected(msf.validate_authoring(document))

    def test_output_drift_missing_extra_modified_and_reordered(self):
        with tempfile.TemporaryDirectory(prefix='rcef-test-') as tmp:
            path = Path(tmp)
            for name in ('pack.toml', 'data', 'profiles', 'mappings', 'evidence'):
                source = ROOT / name
                if source.is_dir(): shutil.copytree(source, path / name)
                else: shutil.copy2(source, path / name)
            runner = [sys.executable, '-B', '-P', '-m', 'msf_tools', 'check', str(path),
                      '--pack', str(path / 'generated/rcef.pack.json'),
                      '--csv', str(path / 'generated/rcef_mapping.csv')]
            def run(write=False):
                return subprocess.run(runner + (['--write'] if write else []), capture_output=True)
            self.assertEqual(run(True).returncode, 0)
            outputs = path / 'generated'
            baseline = {p.name: p.read_bytes() for p in outputs.iterdir()}
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run(True).returncode, 0)
            self.assertEqual({p.name: p.read_bytes() for p in outputs.iterdir()}, baseline)
            for kind in ('missing', 'extra', 'modified'):
                with self.subTest(kind=kind):
                    csv = outputs / 'rcef_mapping.csv'
                    if kind == 'missing': csv.unlink()
                    if kind == 'extra': (outputs / 'unexpected.csv').write_text('extra\n')
                    if kind == 'modified': csv.write_bytes(baseline[csv.name] + b'\n')
                    self.assertNotEqual(run().returncode, 0)
                    for p in outputs.iterdir():
                        if p.name not in baseline:p.unlink()
                    for name, data in baseline.items(): (outputs / name).write_bytes(data)
            canonical = path / 'data/canonical.toml'
            blocks = canonical.read_text().split('[[signals]]')
            canonical.write_text(blocks[0] + '[[signals]]' + blocks[2] + '[[signals]]' + blocks[1]
                                 + ''.join('[[signals]]' + b for b in blocks[3:]))
            self.assertNotEqual(run().returncode, 0, 'authoring order drift must be detected')

    def test_inventory_source_counts_and_semantic_constraints(self):
        expected = {'arkit.coefficient':52, 'mediapipe.label':52, 'openxr.fb':63, 'openxr.fb2':70,
                    'openxr.visemes':15, 'vrcft.transport':88, 'vrcft.eye':12,
                    'vrcft.artist.base':102, 'vrcft.artist.blended':42, 'godot.base':102,
                    'godot.blended':41, 'vrm.preset':18, 'roblox.control':50,
                    'vrcft.parameter.float':124, 'vrcft.parameter.flags':3}
        profiles = {p['id']: p for p in self.document['profiles']}
        signals = {s['id']: s for s in self.document['signals']}
        for id, count in expected.items():
            with self.subTest(profile=id):
                selected = [signals[s] for s in profiles[id]['signal_ids']
                            if signals[s]['metadata'].get('selected', True)]
                self.assertEqual(len(selected), count)
        self.assertEqual(signals['mediapipe.label._neutral']['disposition'], 'excluded')
        self.assertEqual(signals['vrcft.eye.Left.Openness']['native_default'], 1.0)
        self.assertNotIn('neutral', signals['vrcft.eye.Left.Openness'])
        self.assertEqual(signals['vrcft.eye.Left.PupilDiameter_MM']['units'], 'mm')
        self.assertEqual(signals['vrcft.eye.Combined.PupilDiameter_MM']['units'], '1')
        self.assertEqual(signals['vrm.preset.blink']['metadata']['binary_boundary_outputs'], [0.0, 0.0, 1.0])
        self.assertNotEqual(profiles['roblox.control']['metadata']['required_pose_list_A'],
                            profiles['roblox.control']['metadata']['required_pose_list_B'])
        self.assertTrue(all(signals[s]['metadata']['reason'] for p in expected
                            for s in profiles[p]['signal_ids']))

    def test_coverage_contains_all_evidence_and_partitions(self):
        coverage = json.loads((ROOT / 'generated/coverage.json').read_text())
        self.assertTrue('evidence' in coverage, 'coverage must enumerate all source records')
        self.assertTrue('dispositions' in coverage and 'mapping_quality' in coverage,
                        'coverage must partition dispositions and quality')
        signal_ids = {s['id'] for s in self.document['signals']}
        disposition_ids = [id for ids in coverage['dispositions'].values() for id in ids]
        self.assertEqual(set(disposition_ids), signal_ids)
        self.assertEqual(len(disposition_ids), len(signal_ids))
        rules = [r for m in self.document['mappings'] for r in m['rules']]
        mapped = [r for r in rules if r['disposition'] == 'mapped']
        self.assertEqual(sorted(i for ids in coverage['mapping_quality'].values() for i in ids),
                         sorted(r['id'] for r in mapped))
        for quality, ids in coverage['mapping_quality'].items():
            self.assertEqual(coverage['mapping_quality_counts'][quality], len(ids))
            self.assertEqual(set(ids), {r['id'] for r in mapped if r['mapping_quality'] == quality})
        self.assertEqual({r['id'] for r in coverage['rules']}, {r['id'] for r in rules})
        self.assertEqual(coverage['totals']['signals'], len(signal_ids))
        self.assertEqual(len(coverage['profiles']), len(self.document['profiles']))
        self.assertEqual({e['id'] for e in coverage['evidence']},
                         {e['id'] for e in self.document['evidence']})
        self.assertEqual({s['id'] for s in coverage['signals']},
                         {s['id'] for s in self.document['signals']})


if __name__ == '__main__':
    unittest.main(verbosity=2)
