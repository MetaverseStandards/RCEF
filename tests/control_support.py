"""Future DEVELOPMENT_ONLY fixtures. This file is not executed during freezing."""
from collections import Counter
from contextlib import ExitStack, contextmanager, redirect_stdout, redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent if (HERE.parent / "FROZEN_EXPECTATIONS.json").is_file() else HERE / "fixtures/r2-controls"
EXPECT = json.loads((PACKET / "FROZEN_EXPECTATIONS.json").read_text())
SOURCE = Path(EXPECT["baseline_root"]) if PACKET == HERE.parent else HERE.parent
UNIVERSE = json.loads((PACKET / "LITERAL_UNIVERSES.json").read_text())
FULL = tuple(UNIVERSE["full_ids"])
LEAF = tuple(UNIVERSE["leaf_ids"])
GATE = "test_gate.Gate.test_published_gates_reject_coherent_wrong_metadata"
PROBE = "test_hardening.ControlledProbe.test_controlled_probe"
GATE_ADDITIONS = ("test_gate.Extra.test_alpha", "test_gate.Extra.test_beta")

def load_subject(relative, name):
    spec = importlib.util.spec_from_file_location(name, SOURCE / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

@contextmanager
def isolated(environment=None):
    """Restore declared fixture state; this supplies no general state credit."""
    before = dict(stdout=sys.stdout, stderr=sys.stderr, argv=sys.argv,
                  path=sys.path, environ=dict(os.environ), modules=dict(sys.modules))
    status = {}
    try:
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, environment or EXPECT["future_environment"], clear=True))
            stack.enter_context(patch.object(sys, "argv", sys.argv[:]))
            stack.enter_context(patch.object(sys, "path", [str(SOURCE / "tests")] + sys.path[:]))
            stack.enter_context(patch.dict(sys.modules))
            yield status, stack
    finally:
        status.update(stdout=sys.stdout is before["stdout"],
                      stderr=sys.stderr is before["stderr"],
                      argv=sys.argv is before["argv"], path=sys.path is before["path"],
                      environment=dict(os.environ) == before["environ"],
                      modules=dict(sys.modules) == before["modules"])

def make_case(identifier, body=None, hooks=None):
    module, cls, method = identifier.rsplit(".", 2)
    def run(case):
        if body is not None:
            body(case)
    attributes = {"__module__": module, method: run}
    attributes.update(hooks or {})
    return type(cls, (unittest.TestCase,), attributes)(method)

class Harness:
    """Real runner/main and stock TestCases; inert SDK at the import seam."""
    def __init__(self, scratch):
        self.root = Path(scratch)
        for relative in EXPECT["unit_fixture_sources"]:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / relative, destination)
        self.tools = self.root / "inert-tools"
        (self.tools / "msf_tools").mkdir(parents=True)
        (self.tools / "msf_tools/__init__.py").write_bytes(b"")
        with isolated() as (_, stack):
            self.runner = load_subject("scripts/run_acceptance.py", "rcef_r2_subject_runner")
        self.runner.ROOT = self.root
        self.result = None

    def invoke(self, selected, *, observe=False, full=False, delegates=None,
               suite_run=None, extra_argv=(), exit_context=None):
        selected = list(selected)
        output, diagnostic = io.StringIO(), io.StringIO()
        self.caught, self.secondary, self.code = None, [], None
        self.discovery_calls = []
        argv = ["run_acceptance.py", "--tools-path", str(self.tools)]
        if observe:
            argv.append("--observe-gate-control")
        elif not full:
            argv.append("--qualification-only")
        argv.extend(extra_argv)
        fake = types.ModuleType("msf_tools")
        fake.__file__ = str(self.tools / "msf_tools/__init__.py")
        owner = self
        parent = self.runner.CoverageResult
        class Captured(parent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                owner.result = self
        def discovery(*args, **kwargs):
            self.discovery_calls.append((args, kwargs))
            return unittest.TestSuite(selected)
        self.result = None
        self.contexts_completed = False
        state = {}
        try:
            with isolated({"MSF_TOOLS_PATH": str(self.tools)}) as (state, stack):
                stack.enter_context(patch.object(sys, "argv", argv))
                stack.enter_context(patch.dict(sys.modules, {"msf_tools": fake}))
                stack.enter_context(patch.object(unittest.defaultTestLoader, "discover", side_effect=discovery))
                stack.enter_context(patch.object(self.runner, "CoverageResult", Captured))
                if suite_run:
                    stack.enter_context(patch.object(unittest.TestSuite, "run", suite_run))
                for name, callback in (delegates or {}).items():
                    stack.enter_context(patch.object(unittest.TextTestResult, name, callback))
                stack.enter_context(redirect_stdout(output))
                stack.enter_context(redirect_stderr(diagnostic))
                if exit_context:
                    stack.enter_context(exit_context)
                try:
                    self.code = self.runner.main()
                except BaseException as error:
                    self.caught = error
            self.contexts_completed = True
        except BaseException as error:
            if self.caught is None:
                self.caught = error
            elif error is not self.caught:
                self.secondary.append(error)
            self.code = None
        self.restoration = state
        self.output, self.diagnostic = output.getvalue(), diagnostic.getvalue()
        self.records = []
        for line in self.output.splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                self.records.append(record)
        self.payload = self.records[-1] if self.records else None
        return self.code

    def ledger(self, selected):
        expected = Counter(selected)
        return (Counter(self.result.started), Counter(self.result.stopped),
                Counter(i for i, _ in self.result.terminals), expected)
