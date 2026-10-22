"""CMD01/02/03 only: future baseline-compatible command-construction controls.

The private sentinel ends capture. It is neither semantic RED nor completion of
the original Gate. No CompletedProcess, shell, lock operation or fake output.
"""
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from control_support import EXPECT, SOURCE, isolated, load_subject

class _CaptureComplete(BaseException):
    pass

class BaselineCommands(unittest.TestCase):
    def capture_workflow(self):
        calls = []
        with tempfile.TemporaryDirectory(prefix="rcef-r2-capture-") as scratch:
            inert_tools = Path(scratch) / "inert-tools"
            inert_tools.mkdir()
            environment = dict(EXPECT["future_environment"], MSF_TOOLS_PATH=str(inert_tools))
            with isolated(environment) as (restored, stack):
                gate = load_subject("tests/test_gate.py", "rcef_r2_gate_subject")
                def capture(argv, **kwargs):
                    calls.append({"argv": list(argv), **kwargs})
                    calls[-1]["copied_gate_sources"] = {
                        name: (Path(kwargs["cwd"]) / "tests" / name).is_file()
                        for name in ("test_gate.py", "test_qualification_gate.py")}
                    raise _CaptureComplete()
                stack.enter_context(patch.object(gate.subprocess, "run", side_effect=capture))
                try:
                    gate.Gate("test_published_gates_reject_coherent_wrong_metadata").test_published_gates_reject_coherent_wrong_metadata()
                except _CaptureComplete:
                    pass
                else:
                    self.fail("fixture failure: first subprocess boundary was not captured")
            self.assertTrue(all(restored.values()), restored)
        self.assertEqual(len(calls), 1, "fixture failure: capture must stop at the first boundary")
        call = calls[0]
        self.assertEqual(call["argv"][:2], ["/bin/sh", "-c"])
        self.assertEqual(len(call["argv"]), 3)
        self.assertTrue(call["argv"][2].startswith("set -e\n"))
        self.assertEqual(Path(call["cwd"]).name, "RCEF")
        workspace = Path(call["cwd"]).parent
        self.assertEqual(call["env"]["MSF_TOOLS_PATH"], str(workspace / ".ci-tools"))
        self.assertEqual(call["env"]["PYTHONPATH"], str(workspace / ".ci-tools"))
        self.assertEqual(call["env"]["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(call["timeout"], 120)
        self.assertIs(call["check"], False)
        self.assertIs(call["text"], True)
        self.assertEqual(call["stdout"], subprocess.PIPE)
        self.assertEqual(call["stderr"], subprocess.STDOUT)
        self.assertTrue(call["env"]["PATH"].startswith(str(workspace / "bin") + os.pathsep))
        return call

    def test_CMD01_complete_current_named_lock_before_workload(self):
        script = self.capture_workflow()["argv"][2]
        lock = EXPECT["commands"]["lock_heredoc"]
        drift = EXPECT["commands"]["workflow_drift"]
        self.assertIn(lock, script, "CMD01 semantic defect: complete named lock heredoc omitted")
        self.assertIn(drift, script)
        self.assertLess(script.index(lock), script.index(drift))
        self.assertEqual(script.count(lock), 1)

    def test_CMD02_copied_workflow_uses_observed_leaf_runner(self):
        script = self.capture_workflow()["argv"][2]
        drift = EXPECT["commands"]["workflow_drift"]
        runner = EXPECT["commands"]["workflow_subset"]
        self.assertIn(runner, script, "CMD02 semantic defect: observed46 lifecycle runner omitted")
        self.assertLess(script.index(drift), script.index(runner))
        self.assertNotIn(EXPECT["commands"]["baseline_raw_discover"], script)

    def test_CMD03_documents_publish_separated_nonwriting_acceptance(self):
        for name in ("README.md", "CONTRIBUTING.md"):
            with self.subTest(document=name), tempfile.TemporaryDirectory(prefix="rcef-r2-doc-") as scratch:
                checkout = Path(scratch)
                (checkout / "README.md").write_bytes((SOURCE / name).read_bytes())
                with isolated() as (restored, stack):
                    module = load_subject("tests/test_qualification_gate.py", "rcef_r2_qualification_subject")
                    stack.enter_context(patch.object(module.subprocess, "run",
                                                    side_effect=AssertionError("fixture failure: public_script launched a process")))
                    script = module.QualificationGate.public_script(checkout)
                self.assertTrue(all(restored.values()), restored)
                self.assertNotIn("--write", script, "CMD03 semantic defect: generation remains in acceptance")
                for command in EXPECT["commands"]["document_exports"]:
                    self.assertIn(command, script)
                drift = EXPECT["commands"]["document_drift"]
                runner = EXPECT["commands"]["document_subset"]
                self.assertIn(drift, script)
                self.assertIn(runner, script)
                self.assertLess(script.index(drift), script.index(runner))

if __name__ == "__main__":
    unittest.main(verbosity=2)
