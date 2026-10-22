# SPDX-License-Identifier: MIT
"""Stdlib component checks for the readable-report and reviewed-gate union.

Subprocesses are captured fake seams. These tests provide no public, native,
shared dependency or host qualification credit.
"""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate_recipes import document_recipe, source_complete_fixture

ROOT = Path(__file__).resolve().parents[1]


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UnionRegressions(unittest.TestCase):
    def test_copied_fixture_preserves_every_readable_and_architecture_output(self):
        with tempfile.TemporaryDirectory(prefix='rcef-union-copy-') as temporary:
            with patch('subprocess.run', side_effect=AssertionError('copy must not launch')):
                checkout, _ = source_complete_fixture(ROOT, Path(temporary))
            names = [p.relative_to(ROOT) for directory in ('reports', 'docs')
                     for p in sorted((ROOT / directory).iterdir()) if p.is_file()]
            names += [Path('check.py'), Path('scripts/export_reports.py'),
                      Path('tests/test_readable_reports.py')]
            for relative in names:
                with self.subTest(path=str(relative)):
                    self.assertTrue((checkout / relative).is_file(), str(relative))
                    self.assertEqual((checkout / relative).read_bytes(), (ROOT / relative).read_bytes())

    def test_documents_preserve_navigation_and_separate_nonwriting_acceptance(self):
        readme = (ROOT / 'README.md').read_text()
        for target in ('docs/architecture.html', 'docs/architecture.md', 'docs/architecture.svg',
                       'docs/toml-index.csv', 'reports/inventory.md', 'reports/inventory.csv',
                       'reports/mappings.md', 'reports/mappings.csv',
                       'reports/canonical_correspondence.md', 'reports/canonical_correspondence.csv'):
            self.assertIn('](' + target + ')', readme)
        for name in ('README.md', 'CONTRIBUTING.md'):
            text = (ROOT / name).read_text()
            full = document_recipe(text, subset=False)
            copied = document_recipe(text, subset=True)
            self.assertNotIn('--write', full)
            self.assertNotIn('--qualification-only', full)
            self.assertEqual(copied.count('--qualification-only'), 1)
            self.assertIn('acceptance_runner_regressions.py', full)
            self.assertIn('acceptance_gate_regressions.py', full)

    def test_check_success_runs_readable_drift_and_propagates_its_refusal(self):
        wrapper = load('check.py', 'rcef_union_check_success')
        calls = []
        def capture(argv, **kwargs):
            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(argv, 0 if len(calls) == 1 else 7)
        with patch.object(sys, 'argv', ['check.py']), patch.object(wrapper.subprocess, 'run', capture):
            self.assertEqual(wrapper.main(), 7)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0][:4], [sys.executable, '-B', '-m', 'msf_tools'])
        self.assertEqual(calls[1][0], [sys.executable, '-B', str(ROOT / 'scripts/export_reports.py'),
                                      '--root', str(ROOT)])
        self.assertEqual(calls[1][1], {'check': False})

    def test_check_shared_failure_stops_before_readable_export(self):
        wrapper = load('check.py', 'rcef_union_check_failure')
        with patch.object(sys, 'argv', ['check.py', '--write']), \
                patch.object(wrapper.subprocess, 'run', return_value=subprocess.CompletedProcess([], 4)) as run:
            self.assertEqual(wrapper.main(), 4)
        self.assertEqual(run.call_count, 1)
        self.assertIn('--write', run.call_args.args[0])

    def metadata_control(self, omit_addition=False):
        gate = load('tests/test_gate.py', 'rcef_union_gate_subject')
        readable = load('tests/test_readable_reports.py', 'rcef_union_readable_source_only')
        manifest = json.loads((ROOT / 'scripts/acceptance_cases.json').read_text())
        original = sorted(method for group in manifest['required_methods'].values()
                          for method in group if not method.startswith(('test_gate.', 'test_qualification_gate.')))
        additions = sorted('test_readable_reports.ReadableReports.' + method
                           for method in unittest.defaultTestLoader.getTestCaseNames(readable.ReadableReports))
        self.assertEqual(len(original), 46)
        self.assertEqual(len(additions), 10)
        selected = original + additions
        def synthetic_suite(*args, **kwargs):
            cases = []
            for identifier in selected:
                module, cls, method = identifier.rsplit('.', 2)
                case = type(cls, (unittest.TestCase,), {'__module__': module,
                    method: lambda self: self.fail('discovery must never execute these bodies')})(method)
                cases.append(case)
            return unittest.TestSuite(cases)
        mutated = False
        calls = []
        def capture(argv, **kwargs):
            nonlocal mutated
            self.assertEqual(argv[:2], ['/bin/sh', '-c'])
            calls.append(argv)
            script = argv[2]
            if '--write' in script:
                # Explicit fake generation seam: supply the eleven original
                # wrong rows so the real Gate's independent metadata assertions
                # execute. No compiler, shared package or shell is invoked.
                pack = Path(kwargs['cwd']) / 'generated/rcef.pack.json'
                value = json.loads(pack.read_text())
                wrong = {identity for rows in gate.WRONG_ROWS.values() for identity in rows}
                for signal in value['signals']:
                    if signal['id'] in wrong:
                        signal.update(region='eyelid', side='shared')
                pack.write_text(json.dumps(value))
                mutated = True
            if mutated and 'scripts/run_acceptance.py' in script:
                record = {'qualification': 'REFUSE', 'required_methods': original,
                          'tests_run': 56, 'executed_methods': selected[:-1] if omit_addition else selected,
                          'failures': 22, 'errors': 0,
                          'skips': [('test_native_consumer.NativeConsumer.test_' + str(i), 'native unconfigured')
                                    for i in range(9)]}
                output = ('test_primary_metadata_rows_in_authoring\n'
                          'test_primary_metadata_rows_in_generated_pack\n'
                          'Ran 56 tests in 0.01s\nFAILED (failures=22, skipped=9)\n' + json.dumps(record))
                return subprocess.CompletedProcess(argv, 1, stdout=output)
            return subprocess.CompletedProcess(argv, 0, stdout='')
        with patch.object(gate.subprocess, 'run', capture), \
                patch.object(unittest.defaultTestLoader, 'discover', synthetic_suite), \
                patch.dict(os.environ, {key: value for key, value in os.environ.items()
                                        if key not in {'MSF_NATIVE_PATH', 'MSF_NATIVE_SHA256', 'RCEF_REQUIRE_NATIVE'}}, clear=True), \
                redirect_stdout(io.StringIO()):
            gate.Gate('test_published_gates_reject_coherent_wrong_metadata').test_published_gates_reject_coherent_wrong_metadata()
        self.assertEqual(len(calls), 8)

    def test_original_metadata_negative_accepts_complete_readable_additions(self):
        self.metadata_control()

    def test_original_metadata_negative_refuses_missing_readable_execution(self):
        with self.assertRaisesRegex(AssertionError, 'leaf execution differs'):
            self.metadata_control(omit_addition=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
