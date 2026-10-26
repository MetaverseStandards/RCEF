#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""R-HARD declared storage and arithmetic qualification; no provider-frame claim."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]

C, P, U = 'verified_current', 'proposed', 'unresolved'
SOURCE = 'arkit.coefficient.eyeBlinkLeft'
TARGET = 'rcef.arkit.coefficient.eyeBlinkLeft'
RULE = 'arkit.coefficient.eyeBlinkLeft.identity'
FIXTURE_PROFILES = ('fixture.source', 'fixture.target')
FIXTURE_MAPPINGS = ('fixture.affine', 'fixture.bilateral')
# Explicit admitted table from the accepted readiness contract. Locations name
# the status errors; reference failures are tested separately.
ST_ROWS = (
    ('CCC', ()), ('CCP', ('target',)), ('CCU', ('target',)),
    ('CPC', ('source',)), ('CPP', ('source', 'target')), ('CPU', ('source', 'target')),
    ('CUC', ('source',)), ('CUP', ('source', 'target')), ('CUU', ('source', 'target')),
    ('PCC', ()), ('PCP', ()), ('PCU', ('target',)),
    ('PPC', ()), ('PPP', ()), ('PPU', ('target',)),
    ('PUC', ('source',)), ('PUP', ('source',)), ('PUU', ('source', 'target')),
    ('UCC', ('rule',)), ('UCP', ('rule',)), ('UCU', ('rule', 'target')),
    ('UPC', ('rule',)), ('UPP', ('rule',)), ('UPU', ('rule', 'target')),
    ('UUC', ('rule', 'source')), ('UUP', ('rule', 'source')),
    ('UUU', ('rule', 'source', 'target')),
)
RF_ROWS = (
    (C, (C,), True), (C, (C, P), False), (C, (C, U), False), (C, (), False),
    (P, (C,), True), (P, (C, P), True), (P, (C, U), False), (P, (), False),
    (U, (C,), False), (U, (C, P), False), (U, (C, U), False), (U, (), False),
)


class Hardening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loaded = msf.load_authoring(ROOT)
        if not loaded.ok:
            raise AssertionError(loaded.report.to_dict())
        cls.document = loaded.value.to_dict()
        # Compiling the full pack takes a large share of the suite's time, so it is
        # compiled once here and tests that do not edit the document share it.
        # msf-tools rechecks the whole pack on every evaluation, so the fixture
        # mappings, which many tests evaluate repeatedly, use a pack holding only them.
        cls.pack = cls.compile_pack(cls.document)
        cls.fixture_pack = cls.compile_pack(cls.only(FIXTURE_PROFILES, FIXTURE_MAPPINGS))
        cls.shared_mappings = {}
        cls.expectations = json.loads((ROOT / 'tests/fixtures/identity_expectations.json').read_text())['rows']

    def ok(self, result):
        self.assertTrue(result.report.ok, result.report.to_dict())
        self.assertIsNotNone(result.value, result.report.to_dict())
        return result.value

    def errors(self, result, code, ref, message=None):
        self.assertIsNone(result.value, result.report.to_dict())
        self.assertFalse(result.report.ok)
        matches = [d for d in result.report.diagnostics if (d.code, d.severity, d.ref) == (code, 'error', ref)]
        self.assertTrue(matches, result.report.to_dict())
        if message is not None:
            self.assertEqual(matches[0].message, message)
        self.assertNotIn('E_INPUT', [d.code for d in result.report.diagnostics])
        self.assertNotIn('E_INTERNAL', [d.code for d in result.report.diagnostics])
        return matches

    def compile(self, document=None, mapping='arkit.to_canonical', source='arkit.coefficient',
                target='rcef.canonical', approximate=False):
        if document is None:
            return self.pack, self.shared_mapping(self.pack, mapping, source, target, approximate)
        before = deepcopy(document)
        pack = self.ok(msf.compile_pack(self.ok(msf.validate_authoring(document))))
        result = msf.compile_mapping(pack, self.ok(msf.profile_snapshot(pack, source)),
                                     self.ok(msf.profile_snapshot(pack, target)), mapping, approximate)
        self.assertEqual(document, before)
        return pack, result

    @staticmethod
    def compile_pack(document):
        validated = msf.validate_authoring(deepcopy(document))
        compiled = msf.compile_pack(validated.value) if validated.ok else validated
        if not compiled.ok:
            raise AssertionError(compiled.report.to_dict())
        return compiled.value

    def shared_mapping(self, pack, mapping, source, target, approximate):
        key = (pack is self.fixture_pack, mapping, source, target, approximate)
        if key not in self.shared_mappings:
            self.shared_mappings[key] = msf.compile_mapping(
                pack, self.ok(msf.profile_snapshot(pack, source)),
                self.ok(msf.profile_snapshot(pack, target)), mapping, approximate)
        return self.shared_mappings[key]

    @classmethod
    def only(cls, profiles, mappings):
        """A copy of the document reduced to some profiles and mappings, which compiles quickly."""
        d = deepcopy(cls.document)
        d['profiles'] = [p for p in d['profiles'] if p['id'] in profiles]
        kept = {s for p in d['profiles'] for s in p['signal_ids']}
        d['signals'] = [s for s in d['signals'] if s['id'] in kept]
        d['mappings'] = [m for m in d['mappings'] if m['id'] in mappings]
        return d

    def identity(self, source=SOURCE, target=TARGET, rule=RULE, mapping='arkit.to_canonical'):
        d = deepcopy(self.document)
        d['signals'] = [s for s in d['signals'] if s['id'] in (source, target)]
        d['profiles'] = [p for p in d['profiles'] if p['id'] in ('arkit.coefficient', 'rcef.canonical')]
        for p in d['profiles']:
            p['signal_ids'] = [s for s in p['signal_ids'] if s in (source, target)]
        m = next(m for m in d['mappings'] if m['id'] == mapping)
        m['rules'] = [r for r in m['rules'] if r['id'] == rule]
        d['mappings'] = [m]
        return d

    @staticmethod
    def records(d):
        signals = {s['id']: s for s in d['signals']}
        return {'rule': d['mappings'][0]['rules'][0], 'source': signals[SOURCE], 'target': signals[TARGET]}

    @staticmethod
    def evidence(d, id, status):
        d['evidence'].append({'id': id, 'license': 'CC-BY-SA-4.0',
                              'authorship': 'RCEF contributors (2026)', 'locator': 'DESIGN_02.md section 4',
                              'claim': 'Original synthetic storage identity only.', 'status': status})

    @staticmethod
    def frame(values, validity=None):
        return {'timestamp': .125, 'values': values,
                'validity': {k: True for k in values} if validity is None else validity}

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
            compiled[mapping] = self.ok(self.compile(mapping=mapping, source=source)[1])
        comparisons = 0
        for mapping, mapping_compiled in compiled.items():
            rows = [r for r in self.expectations if r['mapping_id'] == mapping]
            peers = [r['input_id'] for r in rows]
            # One frame per (signal, value), each activating a single signal; frames
            # are evaluated independently, so one call covers the whole mapping.
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

    def test_sem02_each_empty_own_evidence_refuses_execution(self):
        for location in ('rule', 'source', 'target'):
            with self.subTest(location=location):
                d = self.identity(); record = self.records(d)[location]; record['evidence'] = []
                _, result = self.compile(d)
                kind = 'Rule' if location == 'rule' else 'Signal'
                self.errors(result, 'E_EVIDENCE_REQUIRED', record['id'],
                            f"{kind} {record['id']} requires nonempty evidence for execution.")

    def test_sem03_all_27_status_combinations(self):
        status = {'C': C, 'P': P, 'U': U}
        allowed = refused = 0
        for index, (row, locations) in enumerate(ST_ROWS, 1):
            with self.subTest(case=f'ST-{index:02}', statuses=row):
                d = self.identity(); records = self.records(d)
                for location, letter in zip(('rule', 'source', 'target'), row):
                    records[location]['evidence_status'] = status[letter]
                pack, result = self.compile(d)
                self.assertEqual([s['evidence_status'] for s in pack.document['signals']],
                                 [s['evidence_status'] for s in d['signals']])
                if locations:
                    for location in locations:
                        self.errors(result, 'E_EVIDENCE_STATUS', records[location]['id'])
                    self.assertEqual([e.ref for e in result.report.diagnostics], [records[k]['id'] for k in locations])
                    refused += 1
                else:
                    c = self.ok(result)
                    self.assertEqual(c.instructions[0]['evidence_status'], status[row[0]])
                    self.assertEqual(self.ok(self.evaluate(c, [self.frame({SOURCE: .25})])).samples[0]['values'][TARGET], .25)
                    allowed += 1
        self.assertEqual((allowed, refused), (5, 22))

    def chain(self):
        d = self.identity()
        base = d['signals'][0]
        for sid in ('synthetic.b', 'synthetic.mid', 'synthetic.parallel'):
            s = deepcopy(base); s['id'] = sid; s['label'] = sid; d['signals'].append(s)
        next(p for p in d['profiles'] if p['id'] == 'arkit.coefficient')['signal_ids'] = [SOURCE, 'synthetic.b']
        next(p for p in d['profiles'] if p['id'] == 'rcef.canonical')['signal_ids'] = [TARGET, 'synthetic.parallel']
        template = d['mappings'][0]['rules'][0]
        def rule(id, inputs, output, op):
            r = deepcopy(template); r.update(id=id, inputs=inputs, outputs=[output], operator=op); return r
        d['mappings'][0]['rules'] = [
            rule('synthetic.final', ['synthetic.mid'], TARGET, {'id': 'identity'}),
            rule('synthetic.sum', [SOURCE, 'synthetic.b'], 'synthetic.mid', {'id': 'weighted_sum', 'weights': [.5, .5]}),
            rule('synthetic.parallel', [SOURCE], 'synthetic.parallel', {'id': 'identity'}),
        ]
        return d

    def test_sem03_each_input_intermediate_output_and_zero_weight_isolated(self):
        d = self.chain()
        _, result = self.compile(d); compiled = self.ok(result)
        self.assertEqual([r['id'] for r in compiled.instructions], ['synthetic.sum', 'synthetic.parallel', 'synthetic.final'])
        self.assertEqual(dict(self.ok(self.evaluate(compiled, [self.frame({SOURCE: .25, 'synthetic.b': .75})])).samples[0]['values']),
                         {TARGET: .5, 'synthetic.parallel': .25})
        for sid in (SOURCE, 'synthetic.b', 'synthetic.mid', TARGET):
            for cause in ('status', 'empty', 'bad_ref'):
                with self.subTest(signal=sid, cause=cause):
                    case = deepcopy(d); s = next(s for s in case['signals'] if s['id'] == sid)
                    if cause == 'status': s['evidence_status'] = P; code = 'E_EVIDENCE_STATUS'
                    elif cause == 'empty': s['evidence'] = []; code = 'E_EVIDENCE_REQUIRED'
                    else:
                        self.evidence(case, 'design02.test.bad', P); s['evidence'].append('design02.test.bad'); code = 'E_EVIDENCE_COMPATIBILITY'
                    self.errors(self.compile(case)[1], code, sid)
        case = deepcopy(d)
        case['mappings'][0]['rules'][1]['operator']['weights'] = [1., 0.]
        next(s for s in case['signals'] if s['id'] == 'synthetic.b')['evidence_status'] = U
        self.errors(self.compile(case)[1], 'E_EVIDENCE_STATUS', 'synthetic.b')
        for r in d['mappings'][0]['rules']: r['evidence_status'] = P
        for s in d['signals']: s['evidence_status'] = P
        compiled = self.ok(self.compile(d)[1])
        self.assertEqual([r['evidence_status'] for r in compiled.instructions], [P, P, P])
        self.assertEqual(self.ok(self.evaluate(compiled, [self.frame({SOURCE: .25, 'synthetic.b': .75})])).samples[0]['values'][TARGET], .5)

    def test_sem04_rf12_at_three_locations(self):
        for location in ('rule', 'source', 'target'):
            for index, (status, refs, allowed) in enumerate(RF_ROWS, 1):
                with self.subTest(location=location, case=f'RF-{index:02}'):
                    d = self.identity(); records = self.records(d); record = records[location]
                    records['rule']['evidence_status'] = C if status == C else P
                    record['evidence_status'] = status
                    record['evidence'] = []
                    for i, ref_status in enumerate(refs):
                        eid = f'design02.ref.{i}'; self.evidence(d, eid, ref_status); record['evidence'].append(eid)
                    _, result = self.compile(d)
                    if allowed:
                        self.ok(result)
                    else:
                        code = 'E_EVIDENCE_STATUS' if status == U else 'E_EVIDENCE_REQUIRED' if not refs else 'E_EVIDENCE_COMPATIBILITY'
                        self.errors(result, code, record['id'])

    def test_sem04_mr12_both_orders_and_both_correct_positives(self):
        index = 0
        for location in ('rule', 'source', 'target'):
            for bad_status in (P, U):
                for order in (('design02.test.good', 'design02.test.bad'), ('design02.test.bad', 'design02.test.good')):
                    index += 1
                    with self.subTest(case=f'MR-{index:02}', location=location):
                        d = self.identity(); self.evidence(d, 'design02.test.good', C); self.evidence(d, 'design02.test.bad', bad_status)
                        record = self.records(d)[location]; record['evidence'] = list(order)
                        positive = deepcopy(d); positive['evidence'][-1]['status'] = C
                        self.ok(self.compile(positive)[1])
                        positive = deepcopy(d); self.records(positive)[location]['evidence'] = ['design02.test.good']
                        self.ok(self.compile(positive)[1])
                        kind = 'Rule' if location == 'rule' else 'Signal'
                        self.errors(self.compile(d)[1], 'E_EVIDENCE_COMPATIBILITY', record['id'],
                                    f"{kind} {record['id']} includes evidence design02.test.bad with status {bad_status}, incompatible with its evidence_status {C}.")
        self.assertEqual(index, 12)

    def test_sem04_all_bad_reference_order_and_proposed_rule_current_endpoints(self):
        for location in ('rule', 'source', 'target'):
            d = self.identity(); self.evidence(d, 'bad.first', P); self.evidence(d, 'bad.second', U)
            record = self.records(d)[location]; record['evidence'] = ['bad.second', 'bad.first']
            result = self.compile(d)[1]
            errors = self.errors(result, 'E_EVIDENCE_COMPATIBILITY', record['id'])
            self.assertEqual([e.message.split(' includes evidence ')[1].split(' with status ')[0] for e in errors], ['bad.second', 'bad.first'])
        for location in ('source', 'target'):
            d = self.identity(); self.records(d)['rule']['evidence_status'] = P
            self.evidence(d, 'design02.test.bad', P); self.records(d)[location]['evidence'].append('design02.test.bad')
            self.errors(self.compile(d)[1], 'E_EVIDENCE_COMPATIBILITY', self.records(d)[location]['id'])

    def test_sem04_unknown_missing_and_invalid_status_structural_controls(self):
        for location in ('rule', 'source', 'target'):
            for cause, code in (('unknown', 'E_REFERENCE'), ('missing', 'E_REQUIRED'), ('invalid', 'E_ENUM')):
                with self.subTest(location=location, cause=cause):
                    d = self.identity(); record = self.records(d)[location]
                    if cause == 'unknown': record['evidence'] = ['missing.evidence']
                    elif cause == 'missing': del record['evidence_status']
                    else: record['evidence_status'] = 'current-ish'
                    result = msf.validate_authoring(d)
                    self.assertIsNone(result.value)
                    self.assertIn(code, [e.code for e in result.report.diagnostics])

    def test_sem05_identity_neutral_side_presence_value_and_null(self):
        for field, value in (('neutral', 1.), ('side', 'right')):
            for cause in ('value', 'absent', 'null'):
                with self.subTest(field=field, cause=cause):
                    d = self.identity(); target = self.records(d)['target']
                    if cause == 'value': target[field] = value
                    elif cause == 'absent': del target[field]
                    else: target[field] = None
                    if cause == 'null':
                        self.assertIn('E_TYPE', [e.code for e in msf.validate_authoring(d).report.diagnostics])
                    else: self.errors(self.compile(d)[1], f'E_{field.upper()}_COMPATIBILITY', RULE)
            d = self.identity()
            for r in (self.records(d)['source'], self.records(d)['target']): r.pop(field)
            self.ok(self.compile(d)[1])
        d = self.identity()
        for r in (self.records(d)['source'], self.records(d)['target']): r['neutral'] = .5
        self.ok(self.compile(d)[1])

    def test_sem06_coupling_presence_and_values(self):
        cases = (('arkit.coefficient.browInnerUp', 'arkit.to_canonical', 'arkit.coefficient'),
                 ('openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB', 'fb2.to_canonical', 'openxr.fb2'))
        for sid, mapping, source_profile in cases:
            for cause in ('delete', 'change', 'empty'):
                with self.subTest(signal=sid, cause=cause):
                    d = self.only((source_profile, 'rcef.canonical'), (mapping,))
                    s = next(s for s in d['signals'] if s['id'] == 'rcef.' + sid)
                    if cause == 'delete': del s['coupling']
                    elif cause == 'change': s['coupling'] = 'composite'
                    else: s['coupling'] = []
                    self.errors(self.compile(d, mapping, source_profile)[1], 'E_COUPLING_COMPATIBILITY', sid + '.identity')
        d = self.identity(); self.records(d)['target']['coupling'] = 'bilateral_shared'
        self.errors(self.compile(d)[1], 'E_COUPLING_COMPATIBILITY', RULE)
        for value in ([], 'bilateral_shared'):
            d = self.identity()
            for s in d['signals']: s['coupling'] = value
            self.ok(self.compile(d)[1])
        d = self.identity(); self.records(d)['target']['coupling'] = None
        self.assertIn('E_TYPE', [e.code for e in msf.validate_authoring(d).report.diagnostics])

    def test_sem07_literal_audit_rejects_paired_relabels_and_invented_neutral(self):
        for cause in ('neutral', 'side', 'units', 'definition'):
            with self.subTest(cause=cause):
                d = deepcopy(self.document); signals = {s['id']: s for s in d['signals']}
                if cause == 'neutral': signals['rcef.vrcft.eye.Left.Openness']['neutral'] = 1.
                elif cause == 'side':
                    for sid in ('vrcft.eye.Left.Openness', 'rcef.vrcft.eye.Left.Openness'): signals[sid]['side'] = 'shared'
                elif cause == 'units':
                    for sid in ('vrcft.eye.Left.PupilDiameter_MM', 'rcef.vrcft.eye.Left.PupilDiameter_MM'): signals[sid]['units'] = '1'
                else: signals[TARGET]['metadata']['definition'] = 'Measured physiology.'
                with self.assertRaises(AssertionError): self.assert_literals(d)

    def test_sem08_existing_identity_basis_domain_and_units(self):
        for field, value, code in (('calibration', 'other.basis', 'E_CALIBRATION'),
                                    ('domain', {'min': 0., 'max': 2.}, 'E_DOMAIN_COMPATIBILITY'),
                                    ('units', 'mm', 'E_UNITS')):
            d = self.identity(); self.records(d)['target'][field] = value
            self.errors(self.compile(d)[1], code, RULE)

    def fixture(self, mapping, approximate=False, document=None):
        if document is None:
            return self.shared_mapping(self.fixture_pack, mapping, 'fixture.source', 'fixture.target', approximate)
        return self.compile(document, mapping, 'fixture.source', 'fixture.target', approximate)[1]

    def test_der01_affine_and_bilateral_literal_outputs_and_losses(self):
        affine = self.ok(self.fixture('fixture.affine'))
        frames = [self.frame({'fixture.affine.signed': v}) for v in (-1., 0., 1.)]
        self.assertEqual([s['values']['fixture.affine.unit'] for s in self.ok(self.evaluate(affine, frames)).samples], [0., .5, 1.])
        self.errors(self.fixture('fixture.bilateral'), 'E_APPROXIMATION', 'fixture.brow.collapse')
        mean = self.ok(self.fixture('fixture.bilateral', True))
        expected_losses = [
            {'category': 'signal', 'effect': 'approximated', 'reason': 'asymmetry irrecoverable',
             'refs': ['fixture.brow.left', 'fixture.brow.right', 'fixture.brow.shared'], 'units': '1'},
            {'category': 'geometry', 'effect': 'unknown', 'reason': 'No geometry evaluated by scalar fixture.', 'refs': ['fixture.brow.shared']},
        ]
        self.assertEqual([l.to_dict() for l in mean.losses], expected_losses)
        frames = [self.frame({'fixture.brow.left': a, 'fixture.brow.right': b}) for a, b in ((1, 0), (0, 1), (0, 0), (1, 1), (.25, .75))]
        result = self.ok(self.evaluate(mean, frames))
        self.assertEqual([s['values']['fixture.brow.shared'] for s in result.samples], [.5, .5, 0., 1., .5])

    def test_der02_declared_loss_assumptions_and_allowed_numerical_changes(self):
        for cause in ('quality', 'basis', 'losses', 'assumptions'):
            with self.subTest(cause=cause):
                d = self.only(FIXTURE_PROFILES, ('fixture.bilateral',))
                rule = next(m for m in d['mappings'] if m['id'] == 'fixture.bilateral')['rules'][0]
                if cause == 'quality': rule['mapping_quality'] = 'exact'
                elif cause == 'basis': next(s for s in d['signals'] if s['id'] == 'fixture.brow.shared')['calibration'] = 'different.synthetic.basis'
                elif cause == 'losses': rule['loss_annotations'] = []
                else: rule['assumptions'] = []
                result = self.fixture('fixture.bilateral', True, d)
                if cause in ('quality', 'basis'):
                    c = self.ok(result); self.assertEqual(len(c.losses), 2)
                    self.errors(self.fixture('fixture.bilateral', False, d), 'E_APPROXIMATION', rule['id'])
                else:
                    self.errors(result, 'E_LOSS_REQUIRED' if cause == 'losses' else 'E_DERIVATION_ASSUMPTIONS', rule['id'])
        d = self.identity(); rule = self.records(d)['rule']
        rule['operator'] = {'id': 'affine', 'scale': .5, 'offset': 0.}; rule['assumptions'] = []
        self.ok(self.compile(d)[1])
        for cause in ('basis', 'units', 'declared_loss'):
            case = deepcopy(d)
            if cause == 'basis': self.records(case)['target']['calibration'] = 'different.synthetic.basis'
            elif cause == 'units': self.records(case)['target']['units'] = 'mm'
            else: self.records(case)['rule']['loss_annotations'] = [{'category': 'signal', 'effect': 'unknown', 'reason': 'Synthetic scope only.', 'refs': [TARGET]}]
            self.errors(self.compile(case, approximate=True)[1], 'E_DERIVATION_ASSUMPTIONS', RULE)

    def test_der03_proposed_mixed_basis_retains_statuses_and_losses(self):
        d = json.loads((ROOT / 'tests/fixtures/proposed_composite.json').read_text())
        mapping = d['mappings'][0]['id']; source, target = [p['id'] for p in d['profiles']]
        rule = d['mappings'][0]['rules'][0]
        self.errors(self.compile(d, mapping, source, target)[1], 'E_APPROXIMATION', rule['id'])
        pack, result = self.compile(d, mapping, source, target, True); c = self.ok(result)
        self.assertEqual(c.instructions[0]['evidence_status'], P)
        self.assertEqual([s['evidence_status'] for s in pack.document['signals']], [P, P, P])
        self.assertEqual([l.to_dict() for l in c.losses], rule['loss_annotations'])
        frames = [self.frame({'synthetic.open': a, 'synthetic.wide': b}) for a, b in ((.25, .75), (.75, .25), (0., 1.), (1., 0.))]
        self.assertEqual([s['values']['synthetic.lid'] for s in self.ok(self.evaluate(c, frames)).samples], [.375, .625, .25, .75])
        case = deepcopy(d); case['mappings'][0]['rules'][0]['evidence_status'] = C
        self.errors(self.compile(case, mapping, source, target, True)[1], 'E_EVIDENCE_STATUS', 'synthetic.open')

    def test_fr01_empty_and_missing_top_level_fields(self):
        c = self.ok(self.fixture('fixture.affine'))
        self.assertEqual(self.ok(self.evaluate(c, [])).samples, ())
        self.errors(self.evaluate(c, [self.frame({})]), 'E_MISSING_SAMPLE', '/samples/0/fixture.affine.signed')
        for field in ('timestamp', 'values', 'validity'):
            frame = self.frame({'fixture.affine.signed': 0.}); del frame[field]
            self.errors(self.evaluate(c, [frame]), 'E_REQUIRED', '/samples/0')

    def test_fr02_explicit_validity_and_paired_values(self):
        c = self.ok(self.fixture('fixture.affine')); sid = 'fixture.affine.signed'
        for values, validity, code in (({sid: 0.}, {}, 'E_VALIDITY'), ({sid: 0.}, {sid: 1}, 'E_VALIDITY'),
                                       ({}, {sid: True}, 'E_VALIDITY'), ({sid: 0.}, {sid: False}, 'E_INVALID_SAMPLE')):
            self.errors(self.evaluate(c, [self.frame(values, validity)]), code, '/samples/0/' + sid)
        self.assertEqual(self.ok(self.evaluate(c, [self.frame({sid: 0})])).samples[0]['values']['fixture.affine.unit'], .5)

    def test_fr03_timestamp_types_nonfinite_giant_and_domain(self):
        c = self.ok(self.fixture('fixture.affine')); sid = 'fixture.affine.signed'
        for timestamp in (True, -.1, '0.125', float('nan'), float('inf'), -float('inf'), 10**400):
            frame = self.frame({sid: 0.}); frame['timestamp'] = timestamp
            self.errors(self.evaluate(c, [frame]), 'E_TIMESTAMP', '/samples/0/timestamp')
        self.errors(self.evaluate(c, [self.frame({'unknown.channel': 0.})]), 'E_SAMPLE_REFERENCE', '/samples/0')
        for value in (True, '0.5', float('nan'), float('inf'), -float('inf'), 10**400):
            self.errors(self.evaluate(c, [self.frame({sid: value})]), 'E_TYPE', '/samples/0/' + sid)
        self.errors(self.evaluate(c, [self.frame({sid: 1.01})]), 'E_DOMAIN', '/samples/0/' + sid)
        for field in ('scale', 'offset'):
            for value in (True, '0.5', float('nan'), float('inf'), -float('inf'), 10**400):
                d = self.only(FIXTURE_PROFILES, ('fixture.affine',))
                rule = next(m for m in d['mappings'] if m['id'] == 'fixture.affine')['rules'][0]
                rule['operator'][field] = value
                self.assertIn('E_TYPE', [e.code for e in msf.validate_authoring(d).report.diagnostics])


if __name__ == '__main__':
    unittest.main(verbosity=2)
