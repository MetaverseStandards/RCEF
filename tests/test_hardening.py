#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""R-HARD: tests of declared storage and arithmetic. They make no claim about provider frames."""
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

C, P, U = 'verified_current', 'proposed', 'unresolved'
SOURCE = 'fixture.identity.plain.source'
TARGET = 'fixture.identity.plain.target'
RULE = 'fixture.identity.plain'
IDENTITY_PROFILES = ('fixture.identity.source', 'fixture.identity.target')
FIXTURE_PROFILES = ('fixture.source', 'fixture.target')
FIXTURE_MAPPINGS = ('fixture.affine', 'fixture.bilateral')
# The admitted table from the accepted readiness contract. Each row names where
# the status errors are. Reference failures have their own tests.
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
        cls.document = shared_pack.document()
        # msf-character-tools rechecks the whole pack on every evaluation, so the fixture
        # maps, which many tests evaluate repeatedly, use a pack holding only them.
        cls.fixture_pack = cls.compile_pack(cls.only(FIXTURE_PROFILES, FIXTURE_MAPPINGS))
        cls.shared_mappings = {}
        cls.identity_fixture = json.loads((ROOT / 'tests/fixtures/fixture_identity.json').read_text())

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

    def compile(self, document, mapping='fixture.identity', source=IDENTITY_PROFILES[0],
                target=IDENTITY_PROFILES[1], approximate=False):
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

    def shared_mapping(self, mapping, approximate):
        key = mapping, approximate
        if key not in self.shared_mappings:
            snapshots = [self.ok(msf.profile_snapshot(self.fixture_pack, p)) for p in FIXTURE_PROFILES]
            self.shared_mappings[key] = msf.compile_mapping(self.fixture_pack, *snapshots, mapping, approximate)
        return self.shared_mappings[key]

    @classmethod
    def only(cls, profiles, mappings):
        """A copy of the document reduced to some profiles and mappings, which compiles quickly."""
        d = cls.subset(lambda p: p['id'] in profiles, lambda s: True, lambda m: m['id'] in mappings)
        kept = {s for p in d['profiles'] for s in p['signal_ids']}
        d['signals'] = [s for s in d['signals'] if s['id'] in kept]
        return d

    @classmethod
    def subset(cls, profile, signal, mapping):
        """A deep copy of only the profiles, signals and mappings kept; copying the whole document is slow."""
        d = {k: v for k, v in cls.document.items() if k not in ('profiles', 'signals', 'mappings')}
        d['profiles'] = [p for p in cls.document['profiles'] if profile(p)]
        d['signals'] = [s for s in cls.document['signals'] if signal(s)]
        d['mappings'] = [m for m in cls.document['mappings'] if mapping(m)]
        return deepcopy(d)

    def identity(self):
        """A copy of the identity fixture reduced to the one mapping SOURCE -> TARGET."""
        d = deepcopy(self.identity_fixture)
        d['signals'] = [s for s in d['signals'] if s['id'] in (SOURCE, TARGET)]
        for p in d['profiles']:
            p['signal_ids'] = [s for s in p['signal_ids'] if s in (SOURCE, TARGET)]
        d['mappings'][0]['rules'] = [r for r in d['mappings'][0]['rules'] if r['id'] == RULE]
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

    def test_sem01_fixture_identities_copy_values_and_raw_storage(self):
        rules = self.identity_fixture['mappings'][0]['rules']
        compiled = self.ok(self.compile(deepcopy(self.identity_fixture))[1])
        peers = [r['inputs'][0] for r in rules]
        # One frame per (signal, value), and each frame sets a single signal.
        cases, frames = [], []
        for rule in rules:
            for value in (0., .25, 1.):
                values = dict.fromkeys(peers, 0.)
                values[rule['inputs'][0]] = value
                cases.append((rule, value))
                frames.append(self.frame(values))
        samples = self.ok(self.evaluate(compiled, frames)).samples
        self.assertEqual(len(samples), 15)
        for (rule, value), sample in zip(cases, samples):
            with self.subTest(rule=rule['id'], value=value):
                output = rule['outputs'][0]
                self.assertEqual(sample['values'][output], value)
                self.assertEqual(sample['timestamp'], .125)
                self.assertIs(sample['validity'][output], True)
        raw = ('fixture.identity.raw.source', 'fixture.identity.raw_mm.source')
        self.assertEqual([s['domain'] for s in self.identity_fixture['signals'] if s['id'] in raw], [{}, {}])
        frames = [self.frame({**dict.fromkeys(peers, 0.), **dict(zip(raw, pair))}) for pair in ((1.5e308, -3.), (-3., 1.5e308))]
        for frame, sample in zip(frames, self.ok(self.evaluate(compiled, frames)).samples):
            self.assertEqual(dict(sample['values']), {r['outputs'][0]: frame['values'][r['inputs'][0]] for r in rules})

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
        next(p for p in d['profiles'] if p['id'] == IDENTITY_PROFILES[0])['signal_ids'] = [SOURCE, 'synthetic.b']
        next(p for p in d['profiles'] if p['id'] == IDENTITY_PROFILES[1])['signal_ids'] = [TARGET, 'synthetic.parallel']
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
        for rule in ('fixture.identity.shared', 'fixture.identity.exclusive'):
            for cause in ('delete', 'change', 'empty'):
                with self.subTest(rule=rule, cause=cause):
                    d = deepcopy(self.identity_fixture)
                    s = next(s for s in d['signals'] if s['id'] == rule + '.target')
                    if cause == 'delete': del s['coupling']
                    elif cause == 'change': s['coupling'] = 'composite'
                    else: s['coupling'] = []
                    self.errors(self.compile(d)[1], 'E_COUPLING_COMPATIBILITY', rule)
        d = self.identity(); self.records(d)['target']['coupling'] = 'bilateral_shared'
        self.errors(self.compile(d)[1], 'E_COUPLING_COMPATIBILITY', RULE)
        for value in ([], 'bilateral_shared'):
            d = self.identity()
            for s in d['signals']: s['coupling'] = value
            self.ok(self.compile(d)[1])
        d = self.identity(); self.records(d)['target']['coupling'] = None
        self.assertIn('E_TYPE', [e.code for e in msf.validate_authoring(d).report.diagnostics])

    def test_sem08_existing_identity_basis_domain_and_units(self):
        for field, value, code in (('calibration', 'other.basis', 'E_CALIBRATION'),
                                    ('domain', {'min': 0., 'max': 2.}, 'E_DOMAIN_COMPATIBILITY'),
                                    ('units', 'mm', 'E_UNITS')):
            d = self.identity(); self.records(d)['target'][field] = value
            self.errors(self.compile(d)[1], code, RULE)

    def fixture(self, mapping, approximate=False, document=None):
        if document is None:
            return self.shared_mapping(mapping, approximate)
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
