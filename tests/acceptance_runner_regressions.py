# SPDX-License-Identifier: MIT
"""Explicit DEVELOPMENT_ONLY runner regressions, outside test_* discovery.

The original IDs, skip reasons and expected diagnostics below are independent
oracles. Discovery is synthetic; the runner and unittest execution are real.
No native artifact or broad SDK/component qualification is exercised.
"""
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
import types
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
TOOLS = Path(os.environ['MSF_TOOLS_PATH']).resolve()
NATIVE_REASON = 'native unqualified: MSF_NATIVE_PATH not configured'
ORIGINALS = {
    'test_gate.Gate': ('test_published_gates_reject_coherent_wrong_metadata',),
    'test_hardening.Hardening': (
        'test_sem01_literal_identities_and_63_single_direction_comparisons',
        'test_sem02_each_empty_own_evidence_refuses_execution',
        'test_sem03_all_27_status_combinations',
        'test_sem03_each_input_intermediate_output_and_zero_weight_isolated',
        'test_sem04_rf12_at_three_locations',
        'test_sem04_mr12_both_orders_and_both_correct_positives',
        'test_sem04_all_bad_reference_order_and_proposed_rule_current_endpoints',
        'test_sem04_unknown_missing_and_invalid_status_structural_controls',
        'test_sem05_identity_neutral_side_presence_value_and_null',
        'test_sem06_coupling_presence_and_values',
        'test_sem07_literal_audit_rejects_paired_relabels_and_invented_neutral',
        'test_sem08_existing_identity_basis_domain_and_units',
        'test_der01_affine_and_bilateral_literal_outputs_and_losses',
        'test_der02_declared_loss_assumptions_and_allowed_numerical_changes',
        'test_der03_proposed_mixed_basis_retains_statuses_and_losses',
        'test_fr01_empty_and_missing_top_level_fields',
        'test_fr02_explicit_validity_and_paired_values',
        'test_fr03_timestamp_types_nonfinite_giant_and_domain'),
    'test_metadata.Metadata': (
        'test_primary_metadata_rows_in_authoring', 'test_primary_metadata_rows_in_generated_pack',
        'test_only_reviewed_fields_change', 'test_version_axes_and_rendered_bytes',
        'test_inventory_counts_names_and_order', 'test_matrix_exclusion_and_unedited_direction_controls',
        'test_all_21_native_scalar_bases', 'test_63_independent_scalar_endpoints',
        'test_csv_coverage_and_checksums_preservation'),
    'test_native_consumer.NativeConsumer': (
        'test_nat01_full_vector_and_integer_numeric_inputs',
        'test_nat02_strict_types_setter_timing_and_atomic_state',
        'test_nat03_shape_bindings_writers_and_instruction_order',
        'test_nat04_large_finite_nonfinite_and_overflow',
        'test_nat05_all_slots_placeholders_and_required_validity',
        'test_nat06_caller_outer_nested_and_return_copies',
        'test_nat06_old_getters_survive_vector_replacement_and_clear',
        'test_nat07_matrix_order_storage_and_original_projective_refusal',
        'test_nat07_huge_axes_nonfinite_and_multiply_overflow'),
    'test_parity.Parity': (
        'test_affine_analytical_endpoints_and_midpoint',
        'test_bilateral_loss_opt_in_and_irrecoverable_asymmetry',
        'test_all_provider_identities_share_explicit_calibration',
        'test_unresolved_cross_provider_refused',
        'test_invalid_missing_boolean_nonfinite_and_domain_samples',
        'test_output_domain_checked_without_clamping',
        'test_strict_authoring_duplicate_unknown_reference_and_operator',
        'test_output_drift_missing_extra_modified_and_reordered',
        'test_inventory_source_counts_and_semantic_constraints',
        'test_coverage_contains_all_evidence_and_partitions'),
    'test_qualification_gate.QualificationGate': (
        'test_copied_public_gate_exercises_direct_new_qualification_probe',
        'test_configured_public_gate_refuses_controlled_native_skip',
        'test_configured_public_gate_refuses_omitted_required_method'),
}
FULL_IDS = tuple(c + '.' + m for c, methods in ORIGINALS.items() for m in methods)
SUBSET_IDS = tuple(i for i in FULL_IDS if not i.startswith(('test_gate.', 'test_qualification_gate.')))
NAT01 = 'test_native_consumer.NativeConsumer.test_nat01_full_vector_and_integer_numeric_inputs'
SEM01 = 'test_hardening.Hardening.test_sem01_literal_identities_and_63_single_direction_comparisons'
ADDITION = 'test_hardening.ControlledProbe.test_controlled_probe'
EARLY_KEYS = {'qualification', 'missing_required_methods', 'duplicate_methods'}
FINAL_KEYS = {'qualification', 'interpreter', 'tools_origin', 'native_origin', 'native_sha256',
              'native_required', 'native_qualified', 'tests_run', 'required_methods',
              'executed_methods', 'unexecuted_required_methods', 'skips', 'failures', 'errors'}


def healthy(test):
    pass


def make_case(identifier, body=healthy, reason=None):
    module, cls, method = identifier.split('.')
    def run_method(test):
        return body(test)
    if getattr(body, '__unittest_expecting_failure__', False):
        run_method = unittest.expectedFailure(run_method)
    if reason is not None:
        run_method = unittest.skip(reason)(run_method)
    return type(cls, (unittest.TestCase,), {'__module__': module, method: run_method})(method)


class RunnerRegressions(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='rcef-r1-')
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        for directory in ('scripts', 'evidence/input-contracts', 'tests'):
            (self.root / directory).mkdir(parents=True)
        for rel in ('scripts/acceptance_cases.json', 'evidence/input-contracts/qualification-skip.contract.json',
                    'evidence/input-contracts/qualification-skip.r2-bindings.json',
                    'tests/test_native_consumer.py', 'tests/test_qualification_gate.py',
                    'tests/test_gate.py', 'tests/test_hardening.py'):
            shutil.copy2(REPO / rel, self.root / rel)
        spec = importlib.util.spec_from_file_location('rcef_runner_under_test', REPO / 'scripts/run_acceptance.py')
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        self.runner.ROOT = self.root
        self.result = None

    def suite(self, full=False, bodies=None, reasons=None):
        bodies, reasons = bodies or {}, reasons or {}
        return [make_case(i, bodies.get(i, healthy), reasons.get(i)) for i in (FULL_IDS if full else SUBSET_IDS)]

    def invoke(self, selected, full=False, configured=False, resultclass=None, run=None, delegate=None):
        output, diagnostic = io.StringIO(), io.StringIO()
        argv = ['run_acceptance.py', '--tools-path', str(TOOLS)]
        if not full:
            argv.append('--qualification-only')
        fake_native = types.ModuleType('_msf_native')
        fake_native.__file__ = str(self.root / '_msf_native.so')
        if configured:
            Path(fake_native.__file__).write_bytes(b'synthetic native boundary; never loaded')
            argv.extend(['--native-path', str(self.root), '--native-sha256',
                         hashlib.sha256(b'synthetic native boundary; never loaded').hexdigest()])
        parent = resultclass or self.runner.CoverageResult
        owner = self
        class Captured(parent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                owner.result = self
        caught = None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {'MSF_TOOLS_PATH': str(TOOLS)}, clear=True))
            stack.enter_context(patch.object(sys, 'argv', argv))
            stack.enter_context(patch.object(sys, 'path', sys.path[:]))
            stack.enter_context(patch.dict(sys.modules, {'_msf_native': fake_native}))
            stack.enter_context(patch.object(unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite(selected)))
            stack.enter_context(patch.object(self.runner, 'CoverageResult', Captured))
            if run:
                stack.enter_context(patch.object(unittest.TestSuite, 'run', run))
            if delegate:
                for name, callback in delegate.items():
                    stack.enter_context(patch.object(unittest.TextTestResult, name, callback))
            stack.enter_context(redirect_stdout(output)); stack.enter_context(redirect_stderr(diagnostic))
            try:
                code = self.runner.main()
            except BaseException as error:
                caught, code = error, None
        self.output, self.diagnostic, self.caught = output.getvalue(), diagnostic.getvalue(), caught
        records = [json.loads(line) for line in self.output.splitlines() if line.startswith('{')]
        self.payload = records[-1] if records else None
        return code

    def refusal(self, code):
        self.assertIsNone(self.caught, repr(self.caught))
        self.assertEqual(code, 1, self.output + self.diagnostic)
        self.assertEqual(self.payload['qualification'], 'REFUSE')

    def first_fault(self, first, second=None, frame=None):
        self.assertIs(self.caught, first, self.output + self.diagnostic)
        self.assertNotIn('"qualification": "PASS"', self.output)
        if second is not None:
            chain = []; current = first
            while current is not None and current not in chain:
                chain.append(current); current = current.__cause__ or current.__context__
            self.assertTrue(any(item is second for item in chain), repr(chain))
        if frame:
            self.assertIn(frame, [item.name for item in traceback.extract_tb(first.__traceback__)])

    def test_full_healthy_preserves_public_keys_and_originals(self):
        self.assertEqual(len(FULL_IDS), 50); self.assertEqual(len(SUBSET_IDS), 46)
        self.assertEqual(self.invoke(self.suite(full=True), full=True), 0)
        self.assertEqual(set(self.payload), FINAL_KEYS)
        self.assertEqual(self.payload['required_methods'], sorted(FULL_IDS))
        self.assertFalse(self.payload['native_qualified'])

    def test_eligible_skips_are_not_quotas(self):
        self.assertEqual(self.invoke(self.suite()), 0)
        self.assertEqual(self.payload['skips'], [])

    def test_each_raw_metadata_buffer_is_consumed_once(self):
        paths = {self.root / 'scripts/acceptance_cases.json': 0,
                 self.root / 'evidence/input-contracts/qualification-skip.contract.json': 0}
        original = Path.open
        def counted(path, *args, **kwargs):
            if path in paths:
                paths[path] += 1
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', counted):
            self.assertEqual(self.invoke(self.suite()), 0)
        self.assertEqual(list(paths.values()), [1, 1])

    def test_original_nine_skips_are_admitted_in_copied_subset(self):
        for file in ('test_gate.py', 'test_qualification_gate.py'):
            (self.root / 'tests' / file).unlink()
        reasons = {i: NATIVE_REASON for i in SUBSET_IDS if i.startswith('test_native_consumer.')}
        self.assertEqual(self.invoke(self.suite(reasons=reasons)), 0, self.output + self.diagnostic)
        self.assertEqual(len(self.payload['skips']), 9)

    def test_full_eleven_source_bound_skips(self):
        reasons = {i: NATIVE_REASON for i in FULL_IDS if i.startswith('test_native_consumer.')}
        reasons.update({
            'test_qualification_gate.QualificationGate.test_configured_public_gate_refuses_controlled_native_skip': 'native skip control requires configured artifact',
            'test_qualification_gate.QualificationGate.test_configured_public_gate_refuses_omitted_required_method': 'native omission control requires configured artifact'})
        self.assertEqual(self.invoke(self.suite(full=True, reasons=reasons), full=True), 0)
        self.assertEqual(len(self.payload['skips']), 11)

    def test_semantic_skip_is_refused(self):
        self.refusal(self.invoke(self.suite(reasons={SEM01: NATIVE_REASON})))

    def test_native_wrong_reason_is_refused(self):
        self.refusal(self.invoke(self.suite(reasons={NAT01: 'native unavailable'})))

    def test_addition_skip_is_refused(self):
        self.refusal(self.invoke(self.suite() + [make_case(ADDITION, reason=NATIVE_REASON)]))

    def test_changed_native_module_condition_is_refused_on_skip(self):
        p = self.root / 'tests/test_native_consumer.py'
        p.write_text(p.read_text().replace('native = None', 'native = object()'))
        self.refusal(self.invoke(self.suite(reasons={NAT01: NATIVE_REASON})))

    def test_changed_native_decorator_is_refused_on_skip(self):
        p = self.root / 'tests/test_native_consumer.py'
        p.write_text(p.read_text().replace('native is not None', 'False'))
        self.refusal(self.invoke(self.suite(reasons={NAT01: NATIVE_REASON})))

    def test_configured_changed_control_reaches_exact_skip_reason(self):
        p = self.root / 'tests/test_native_consumer.py'
        marker = '    def test_nat01_full_vector_and_integer_numeric_inputs(self):'
        p.write_text(p.read_text().replace(marker, "    @unittest.skip('controlled required native case')\n" + marker))
        self.refusal(self.invoke(self.suite(reasons={NAT01: 'controlled required native case'}), configured=True))
        self.assertIn('controlled required native case', self.diagnostic)
        self.assertEqual(self.payload['tests_run'], 46)

    def test_configured_omission_reaches_original_name_before_execution(self):
        p = self.root / 'tests/test_native_consumer.py'
        p.write_text(p.read_text().replace('def test_nat01_', 'def omitted_nat01_'))
        self.refusal(self.invoke([t for t in self.suite() if t.id() != NAT01], configured=True))
        self.assertEqual(set(self.payload), EARLY_KEYS)
        self.assertEqual(self.payload['missing_required_methods'], [NAT01])
        self.assertIsNone(self.result)

    def test_duplicate_discovery_is_refused_before_execution(self):
        self.refusal(self.invoke(self.suite() + [make_case(SEM01)]))
        self.assertEqual(self.payload['duplicate_methods'], [SEM01])
        self.assertIsNone(self.result)

    def test_manifest_duplicate_key_is_refused_before_execution(self):
        p = self.root / 'scripts/acceptance_cases.json'
        p.write_text(p.read_text().replace('"groups": [', '"groups": [], "groups": [', 1))
        self.refusal(self.invoke(self.suite()))
        self.assertIsNone(self.result)

    def test_manifest_changed_original_is_refused_before_execution(self):
        p = self.root / 'scripts/acceptance_cases.json'
        p.write_text(p.read_text().replace(SEM01, ADDITION))
        self.refusal(self.invoke(self.suite() + [make_case(ADDITION)]))
        self.assertIsNone(self.result)

    def test_skip_contract_duplicate_key_is_refused_before_execution(self):
        p = self.root / 'evidence/input-contracts/qualification-skip.contract.json'
        p.write_text(p.read_text().replace('"revision": 2', '"revision": 1, "revision": 2', 1))
        self.refusal(self.invoke(self.suite()))
        self.assertIsNone(self.result)

    def test_skip_contract_wrong_allowlist_is_refused_before_execution(self):
        p = self.root / 'evidence/input-contracts/qualification-skip.contract.json'
        p.write_text(p.read_text().replace('"eligible_skip_count": 9', '"eligible_skip_count": 8', 1))
        self.refusal(self.invoke(self.suite()))
        self.assertIsNone(self.result)

    def test_selected_addition_runs_without_changing_original_denominator(self):
        self.assertEqual(self.invoke(self.suite() + [make_case(ADDITION)]), 0)
        self.assertEqual(self.payload['tests_run'], 47)
        self.assertEqual(self.payload['required_methods'], sorted(SUBSET_IDS))
        self.assertIn(ADDITION, self.payload['executed_methods'])

    def test_appended_source_probe_reaches_marker(self):
        p = self.root / 'tests/test_hardening.py'
        source = "\nclass ControlledProbe(unittest.TestCase):\n    def test_controlled_probe(self):\n        self.fail('RCEF_QUALIFICATION_PROBE_EXECUTED')\n"
        with p.open('a') as stream:
            stream.write(source)
        namespace = {'unittest': unittest, '__name__': 'test_hardening'}
        exec(compile(source, str(p), 'exec'), namespace)
        probe = namespace['ControlledProbe']('test_controlled_probe')
        self.refusal(self.invoke(self.suite() + [probe]))
        self.assertIn('RCEF_QUALIFICATION_PROBE_EXECUTED', self.diagnostic)
        self.assertEqual(self.payload['tests_run'], 47)

    def test_original_wrong_metadata_diagnostic_still_runs_46_with_22_failures(self):
        def wrong_rows(test):
            for row in range(11):
                with test.subTest(independent_wrong_row=row):
                    test.fail('wrong metadata row')
        bodies = {'test_metadata.Metadata.test_primary_metadata_rows_in_authoring': wrong_rows,
                  'test_metadata.Metadata.test_primary_metadata_rows_in_generated_pack': wrong_rows}
        reasons = {i: NATIVE_REASON for i in SUBSET_IDS if i.startswith('test_native_consumer.')}
        self.refusal(self.invoke(self.suite(bodies=bodies, reasons=reasons)))
        self.assertIn('test_primary_metadata_rows_in_authoring', self.diagnostic)
        self.assertIn('test_primary_metadata_rows_in_generated_pack', self.diagnostic)
        self.assertRegex(self.diagnostic, r'Ran 46 tests\b')
        self.assertRegex(self.diagnostic, r'FAILED \(failures=22, skipped=9\)')

    def test_start_only_cannot_pass(self):
        def starts(suite, result, debug=False):
            for test in suite:
                result.startTest(test)
            return result
        self.refusal(self.invoke(self.suite(), run=starts))

    def test_missing_addition_execution_cannot_pass(self):
        def originals_only(suite, result, debug=False):
            for test in suite:
                if test.id() != ADDITION:
                    test(result)
            return result
        self.refusal(self.invoke(self.suite() + [make_case(ADDITION)], run=originals_only))

    def test_missing_stop_cannot_pass(self):
        def omit_stops(suite, result, debug=False):
            for test in suite:
                result.startTest(test); result.addSuccess(test)
            return result
        self.refusal(self.invoke(self.suite(), run=omit_stops))

    def test_duplicate_start_callback_cannot_pass(self):
        def twice(suite, result, debug=False):
            for test in suite:
                result.startTest(test); test(result)
            return result
        self.refusal(self.invoke(self.suite(), run=twice))

    def test_foreign_callback_cannot_pass(self):
        original = unittest.TestSuite.run
        def foreign(suite, result, debug=False):
            original(suite, result, debug)
            make_case('test_foreign.Injected.test_unselected')(result)
            return result
        self.refusal(self.invoke(self.suite(), run=foreign))

    def test_duplicate_parent_terminal_cannot_pass(self):
        original = unittest.TextTestResult.addSuccess
        def double_terminal(result, test):
            original(result, test)
            result.addSkip(test, NATIVE_REASON)
        self.refusal(self.invoke(self.suite(), delegate={'addSuccess': double_terminal}))

    def test_healthy_subtest_is_not_a_parent_terminal(self):
        def subtests(test):
            with test.subTest(value=1):
                test.assertEqual(1, 1)
        self.assertEqual(self.invoke(self.suite(bodies={SEM01: subtests})), 0)

    def test_healthy_subtest_callback_fault_cannot_become_an_ordinary_outcome(self):
        first = RuntimeError('healthy subtest delegate fault')
        def subtests(test):
            with test.subTest(value=1):
                pass
        def subtest_delegate(result, test, subtest, err):
            raise first
        self.invoke(self.suite(bodies={SEM01: subtests}), delegate={'addSubTest': subtest_delegate})
        self.first_fault(first, frame='subtest_delegate')

    def test_first_callback_survives_TestCase_stop_and_runner_stop_finally(self):
        first, second = RuntimeError('first success delegate'), RuntimeError('later stop delegate')
        def first_delegate(result, test):
            raise first
        def stop_delegate(result, test):
            raise second
        self.invoke(self.suite(), delegate={'addSuccess': first_delegate, 'stopTest': stop_delegate})
        self.first_fault(first, second, 'first_delegate')

    def test_first_callback_survives_stopTestRun_fault(self):
        first, second = RuntimeError('first success'), RuntimeError('runner finally')
        def first_delegate(result, test):
            raise first
        def stop_run(result):
            raise second
        self.invoke(self.suite(), delegate={'addSuccess': first_delegate, 'stopTestRun': stop_run})
        self.first_fault(first, second, 'first_delegate')

    def test_record_and_delegate_pair_retains_first_record_object(self):
        first, second = RuntimeError('record append'), RuntimeError('start delegate')
        class BrokenList(list):
            def append(self, value):
                raise first
        class BrokenRecord(self.runner.CoverageResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.executed = BrokenList()
        def start_delegate(result, test):
            raise second
        self.invoke(self.suite(), resultclass=BrokenRecord, delegate={'startTest': start_delegate})
        self.first_fault(first, second, 'append')

    def test_setup_teardown_cleanup_expected_and_unexpected_faults_refuse(self):
        def failure(test):
            test.fail('ordinary assertion')
        def cleanup(test):
            test.addCleanup(lambda: (_ for _ in ()).throw(RuntimeError('cleanup')))
        @unittest.expectedFailure
        def expected(test):
            test.fail('expected failure is unqualified')
        @unittest.expectedFailure
        def unexpected(test):
            pass
        for body in (failure, cleanup, expected, unexpected):
            with self.subTest(body=body):
                self.refusal(self.invoke(self.suite(bodies={SEM01: body})))
        for name in ('setUp', 'tearDown'):
            with self.subTest(hook=name):
                selected = self.suite()
                setattr(type(selected[0]), name, lambda test: (_ for _ in ()).throw(RuntimeError('hook')))
                self.refusal(self.invoke(selected))


class IndependentLifecycleReview(unittest.TestCase):
    """Asha's two repros plus order, accounting and diagnostic controls."""
    def setUp(self):
        self.harness = RunnerRegressions('test_eligible_skips_are_not_quotas')
        self.harness.setUp()
        self.addCleanup(self.harness.doCleanups)

    def assert_ledger(self, selected):
        from collections import Counter
        result = self.harness.result
        expected = Counter(test.id() for test in selected)
        self.assertEqual(Counter(result.started), expected)
        self.assertEqual(Counter(result.stopped), expected)
        self.assertEqual(Counter(identifier for identifier, _ in result.terminals), expected)

    def test_stop_terminal_start_original46_must_refuse(self):
        def reverse_lifecycle(suite, result, debug=False):
            for case in suite:
                result.stopTest(case)
                result.addSuccess(case)
                result.startTest(case)
            return result
        selected = self.harness.suite()
        code = self.harness.invoke(selected, run=reverse_lifecycle)
        self.assert_ledger(selected)
        self.assertEqual(self.harness.payload['tests_run'], 46)
        self.harness.refusal(code)

    def test_terminal_after_stop_original_and_addition_must_refuse(self):
        for malformed_id in (SEM01, ADDITION):
            with self.subTest(malformed_id=malformed_id):
                def late_terminal(suite, result, debug=False):
                    for case in suite:
                        if case.id() == malformed_id:
                            result.startTest(case)
                            result.stopTest(case)
                            result.addSuccess(case)
                        else:
                            case(result)
                    return result
                selected = self.harness.suite() + [make_case(ADDITION)]
                code = self.harness.invoke(selected, run=late_terminal)
                self.assert_ledger(selected)
                self.harness.refusal(code)

    def test_other_malformed_orders_original_and_addition_must_refuse(self):
        for order in (('addSuccess', 'startTest', 'stopTest'),
                      ('addSuccess', 'stopTest', 'startTest'),
                      ('stopTest', 'startTest', 'addSuccess')):
            for malformed_id in (SEM01, ADDITION):
                with self.subTest(order=order, malformed_id=malformed_id):
                    def unordered(suite, result, debug=False):
                        for case in suite:
                            if case.id() == malformed_id:
                                for callback in order:
                                    getattr(result, callback)(case)
                            else:
                                case(result)
                        return result
                    selected = self.harness.suite() + [make_case(ADDITION)]
                    code = self.harness.invoke(selected, run=unordered)
                    self.assert_ledger(selected)
                    self.harness.refusal(code)

    def test_interleaved_late_addition_terminal_must_refuse(self):
        def interleaved(suite, result, debug=False):
            selected = list(suite)
            for case in selected:
                result.startTest(case)
            addition = selected[-1]
            result.stopTest(addition)
            for case in selected[:-1]:
                result.addSuccess(case)
                result.stopTest(case)
            result.addSuccess(addition)
            return result
        selected = self.harness.suite() + [make_case(ADDITION)]
        code = self.harness.invoke(selected, run=interleaved)
        self.assert_ledger(selected)
        self.harness.refusal(code)

    def test_healthy_interleaved_originals_and_addition_pass(self):
        def interleaved(suite, result, debug=False):
            selected = list(suite)
            for case in selected:
                result.startTest(case)
            for case in reversed(selected):
                result.addSuccess(case)
            for case in selected:
                result.stopTest(case)
            return result
        selected = self.harness.suite() + [make_case(ADDITION)]
        self.assertEqual(self.harness.invoke(selected, run=interleaved), 0)
        self.assert_ledger(selected)
        self.assertEqual(self.harness.payload['tests_run'], 47)
        self.assertEqual(self.harness.payload['required_methods'], sorted(SUBSET_IDS))
        self.assertEqual(set(self.harness.payload), FINAL_KEYS)

    def test_reported_zero_tests_with_46_completed_ids_must_refuse(self):
        bodies_run = []
        def body(case):
            bodies_run.append(case.id())
        def no_counter_start(result, case):
            return None
        selected = self.harness.suite(bodies={identifier: body for identifier in SUBSET_IDS})
        code = self.harness.invoke(selected, delegate={'startTest': no_counter_start})
        self.assertEqual(bodies_run, list(SUBSET_IDS))
        self.assert_ledger(selected)
        self.assertEqual(self.harness.payload['tests_run'], 0)
        self.assertEqual(self.harness.payload['executed_methods'], list(SUBSET_IDS))
        self.harness.refusal(code)

    def test_addition_count_under_and_over_report_must_refuse(self):
        original = unittest.TextTestResult.startTest
        for offset in (-1, 1):
            with self.subTest(offset=offset):
                def wrong_counter(result, case):
                    original(result, case)
                    if case.id() == ADDITION:
                        result.testsRun += offset
                selected = self.harness.suite() + [make_case(ADDITION)]
                code = self.harness.invoke(selected, delegate={'startTest': wrong_counter})
                self.assert_ledger(selected)
                self.assertEqual(self.harness.payload['tests_run'], 47 + offset)
                self.harness.refusal(code)

    def test_full50_counter_mismatch_must_refuse(self):
        def no_counter_start(result, case):
            return None
        selected = self.harness.suite(full=True)
        code = self.harness.invoke(selected, full=True, delegate={'startTest': no_counter_start})
        self.assert_ledger(selected)
        self.assertEqual(self.harness.payload['required_methods'], sorted(FULL_IDS))
        self.assertEqual(self.harness.payload['tests_run'], 0)
        self.harness.refusal(code)

    def test_delegated_stop_before_terminal_returns_must_refuse(self):
        original = unittest.TextTestResult.addSuccess
        def terminal_delegate(result, case):
            original(result, case)
            result.stopTest(case)
        def nested(suite, result, debug=False):
            for case in suite:
                result.startTest(case)
                result.addSuccess(case)
            return result
        selected = self.harness.suite()
        code = self.harness.invoke(selected, run=nested, delegate={'addSuccess': terminal_delegate})
        self.assert_ledger(selected)
        self.harness.refusal(code)

    def test_stock_teardown_and_cleanup_errors_both_remain_diagnostic(self):
        def cleanup_fault():
            raise RuntimeError('independent cleanup diagnostic')
        def body(case):
            case.addCleanup(cleanup_fault)
        def teardown(case):
            raise RuntimeError('independent teardown diagnostic')
        selected = self.harness.suite(bodies={SEM01: body})
        case = next(case for case in selected if case.id() == SEM01)
        type(case).tearDown = teardown
        code = self.harness.invoke(selected)
        self.harness.refusal(code)
        self.assertEqual(self.harness.payload['errors'], 2)
        self.assertIn('independent teardown diagnostic', self.harness.diagnostic)
        self.assertIn('independent cleanup diagnostic', self.harness.diagnostic)
        self.assertEqual([name for identifier, name in self.harness.result.terminals
                          if identifier == SEM01], ['addError', 'addError'])

    def test_callback_A_then_stop_B_retains_identity_traceback_and_secondary(self):
        first, second = RuntimeError('independent A'), RuntimeError('independent B')
        def callback_A(result, case):
            raise first
        def stop_B(result, case):
            raise second
        self.harness.invoke(self.harness.suite(), delegate={'addSuccess': callback_A, 'stopTest': stop_B})
        self.harness.first_fault(first, second, 'callback_A')
        result = self.harness.result
        self.assertIs(result.first_callback_fault, first)
        self.assertIn('callback_A', [frame.name for frame in traceback.extract_tb(result.first_callback_traceback)])
        self.assertTrue(any(error is second for error, _ in result.callback_faults))

    def test_failed_subtests_keep_diagnostics_without_parent_success(self):
        def failed_subtests(case):
            for value in (1, 2):
                with case.subTest(independent_value=value):
                    case.fail('independent subtest diagnostic')
        code = self.harness.invoke(self.harness.suite(bodies={SEM01: failed_subtests}))
        self.harness.refusal(code)
        self.assertEqual(self.harness.payload['failures'], 2)
        self.assertIn('independent_value=1', self.harness.diagnostic)
        self.assertIn('independent_value=2', self.harness.diagnostic)
        self.assertFalse(any(identifier == SEM01 for identifier, _ in self.harness.result.terminals))


if __name__ == '__main__':
    unittest.main(verbosity=2)
