# SPDX-License-Identifier: MIT
"""Actual readable bodies through the controlled core, with fake original leaves.

The 46 original identities are unchanged expectations. Their semantic/SDK
bodies are explicitly substituted stock unittest leaves; they earn no semantic
or qualification credit. The ten ReadableReports bodies and exporter are real.
"""
from collections import Counter
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = []

def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ObservedReadable(unittest.TestCase):
    def exercise(self, omission=False):
        runner = load('scripts/run_acceptance.py', 'rcef_readable_controlled_core')
        # Import with the original module identity; loader executes its unchanged source.
        readable = load('tests/test_readable_reports.py', 'test_readable_reports')
        manifest = json.loads((ROOT/'scripts/acceptance_cases.json').read_text())
        originals = sorted(m for group in manifest['required_methods'].values() for m in group
                           if not m.startswith(('test_gate.', 'test_qualification_gate.')))
        real = list(runner.cases(unittest.defaultTestLoader.loadTestsFromTestCase(readable.ReadableReports)))
        real_ids = sorted(test.id() for test in real)
        self.assertEqual(len(originals), 46)
        self.assertEqual(len(real_ids), 10)
        fake_calls = []
        def fake_body(case):
            fake_calls.append(case.id())
        fake = []
        for identifier in originals:
            mod, cls, method = identifier.rsplit('.', 2)
            fake.append(type(cls, (unittest.TestCase,), {'__module__':mod, method:fake_body})(method))
        expected = originals + real_ids
        selected = fake + real
        captured = []
        core = runner.run_observed
        omitted = real_ids[-1] if omission else None
        def observed(cases):
            # Execution fault injection only; discovery and selected expectations remain 56.
            execution = [case for case in cases if case.id() != omitted]
            result = core(execution)
            captured.append(result)
            return result
        tools = Path(os.environ['MSF_TOOLS_PATH']).resolve(strict=True)
        stub = types.ModuleType('msf_tools')
        stub.__file__ = str(tools/'msf_tools/__init__.py')
        output = io.StringIO()
        with patch.object(sys,'argv',['run_acceptance.py','--tools-path',str(tools),'--qualification-only']), \
             patch.object(runner.unittest.defaultTestLoader,'discover',return_value=unittest.TestSuite(selected)), \
             patch.object(runner.importlib,'import_module',return_value=stub), \
             patch.object(runner,'run_observed',observed), \
             patch.dict(os.environ,{k:v for k,v in os.environ.items() if k not in
                 {'MSF_NATIVE_PATH','MSF_NATIVE_SHA256','RCEF_REQUIRE_NATIVE'}},clear=True), \
             redirect_stdout(output):
            code = runner.main()
        self.assertEqual(len(captured),1)
        result = captured[0]
        record = json.loads(output.getvalue().strip().split('\n')[-1])
        observation = {'test':self.id(),'omitted_id':omitted, 'selected_ids':expected,
            'original46_fake_ids':originals,'fake_body_calls':fake_calls,'actual_readable_ids':real_ids,
            'starts':result.started,'terminals':result.terminals,'stops':result.stopped,
            'lifecycle':result.lifecycle,'observed_count':result.testsRun,
            'incomplete':result.incomplete(expected),'runner_exit':code,'runner_record':record,
            'full_qualification_credit':0,'scope':'controlled component; original semantic/SDK leaves fake'}
        OBSERVATIONS.append(observation)
        self.assertEqual(Counter(fake_calls),Counter(originals))
        self.assertEqual(record['required_methods'], originals)
        executed = [identifier for identifier in expected if identifier != omitted]
        self.assertEqual(record['tests_run'],len(executed))
        self.assertEqual(Counter(record['executed_methods']),Counter(executed))
        self.assertEqual(Counter(result.started),Counter(executed))
        self.assertEqual(Counter(result.stopped),Counter(executed))
        self.assertEqual(Counter(identifier for identifier,_ in result.terminals),Counter(executed))
        for identifier in executed:
            self.assertEqual(result.lifecycle[identifier], ['startTest','addSuccess','stopTest'])
        self.assertEqual(record['failures'],0)
        self.assertEqual(record['errors'],0)
        self.assertEqual(record['skips'],[])
        self.assertFalse(record['native_qualified'])
        self.assertEqual(result.incomplete(expected),[omitted] if omission else [])
        self.assertEqual(code,1 if omission else 0)
        self.assertEqual(record['qualification'],'REFUSE' if omission else 'PASS')

    def test_all_ten_unchanged_readable_bodies_are_observed(self):
        self.exercise()

    def test_omitted_body_refuses_unchanged_selected_expectations(self):
        self.exercise(omission=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
