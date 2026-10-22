#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Public gate coverage controls with an actual configured native artifact."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gate_recipes import document_recipe, gate_record, source_complete_fixture

ROOT = Path(__file__).resolve().parents[1]
PROBE = 'RCEF_QUALIFICATION_PROBE_EXECUTED'


class QualificationGate(unittest.TestCase):
    def fixture(self, workspace):
        return source_complete_fixture(ROOT, workspace)

    def run_command(self, checkout, env, argv):
        r = subprocess.run(argv, cwd=checkout, env=env, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=240, check=False)
        print(f'QUALIFICATION_GATE argv={argv!r} exit={r.returncode}\n{r.stdout}', flush=True)
        return r

    @staticmethod
    def public_script(checkout):
        return document_recipe((checkout / 'README.md').read_text(), subset=True)

    def test_copied_public_gate_exercises_direct_new_qualification_probe(self):
        with tempfile.TemporaryDirectory(prefix='rcef-coverage-') as tmp:
            checkout, env = self.fixture(Path(tmp))
            p = checkout / 'tests/test_hardening.py'
            with p.open('a') as stream:
                stream.write('\nclass ControlledProbe(unittest.TestCase):\n'
                             '    def test_controlled_probe(self):\n'
                             f'        self.fail({PROBE!r})\n')
            direct = self.run_command(checkout, env, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_hardening.py', '-v'])
            self.assertNotEqual(direct.returncode, 0)
            self.assertIn(PROBE, direct.stdout)
            copied = self.run_command(checkout, env, [sys.executable, '-B', 'scripts/run_acceptance.py',
                                                       '--observe-gate-control', '--tools-path', env['MSF_TOOLS_PATH']])
            self.assertNotEqual(copied.returncode, 0, 'copied public gate omitted the new qualification probe')
            self.assertIn(PROBE, copied.stdout)
            selected_ids = [
                'test_gate.Gate.test_published_gates_reject_coherent_wrong_metadata',
                'test_gate.Gate.test_published_workflow_refuses_wrong_shared_commit',
                'test_gate.Gate.test_published_acceptance_gates_refuse_generated_drift',
                'test_gate.Gate.test_published_gates_refuse_semantic_skip',
            ]
            record = gate_record(copied.stdout, copied.returncode, selected_ids)
            self.assertEqual(record['observation'], 'REFUSE')
            self.assertEqual(record['tests_run'], 4)
            self.assertNotEqual(record.get('qualification'), 'PASS')

    @unittest.skipUnless(os.environ.get('MSF_NATIVE_PATH'), 'native skip control requires configured artifact')
    def test_configured_public_gate_refuses_controlled_native_skip(self):
        with tempfile.TemporaryDirectory(prefix='rcef-skip-') as tmp:
            checkout, env = self.fixture(Path(tmp)); env['RCEF_REQUIRE_NATIVE'] = '1'
            # Keep gate source fixtures; the copied recipe selects only leaf execution.
            p = checkout / 'tests/test_native_consumer.py'
            s = p.read_text(); marker = '    def test_nat01_full_vector_and_integer_numeric_inputs(self):'
            self.assertEqual(s.count(marker), 1)
            p.write_text(s.replace(marker, "    @unittest.skip('controlled required native case')\n" + marker))
            plain = self.run_command(checkout, env, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_native_consumer.py', '-v'])
            self.assertEqual(plain.returncode, 0, plain.stdout)
            self.assertIn('controlled required native case', plain.stdout)
            self.assertIn('skipped=1', plain.stdout)
            script = self.public_script(checkout)
            self.assertTrue(script)
            public = self.run_command(checkout, env, ['/bin/sh', '-c', 'set -e\n' + script])
            self.assertNotEqual(public.returncode, 0, 'configured public gate accepted a skipped required native method')
            self.assertIn('controlled required native case', public.stdout)

    @unittest.skipUnless(os.environ.get('MSF_NATIVE_PATH'), 'native omission control requires configured artifact')
    def test_configured_public_gate_refuses_omitted_required_method(self):
        with tempfile.TemporaryDirectory(prefix='rcef-omitted-') as tmp:
            checkout, env = self.fixture(Path(tmp)); env['RCEF_REQUIRE_NATIVE'] = '1'
            p = checkout / 'tests/test_native_consumer.py'
            s = p.read_text(); marker = 'def test_nat01_full_vector_and_integer_numeric_inputs('
            self.assertEqual(s.count(marker), 1)
            p.write_text(s.replace(marker, 'def omitted_nat01_full_vector_and_integer_numeric_inputs('))
            plain = self.run_command(checkout, env, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_native_consumer.py', '-v'])
            self.assertEqual(plain.returncode, 0, plain.stdout)
            self.assertIn('Ran 8 tests', plain.stdout)
            script = self.public_script(checkout)
            public = self.run_command(checkout, env, ['/bin/sh', '-c', 'set -e\n' + script])
            self.assertNotEqual(public.returncode, 0, 'configured public gate omitted a required native method')
            self.assertIn('test_nat01_full_vector_and_integer_numeric_inputs', public.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
