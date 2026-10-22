"""Future conformance; absent new APIs are not baseline defect evidence."""
import ast
from collections import Counter
import hashlib
import json
import os
import sys
from pathlib import Path
import tempfile
import traceback
import unittest
from unittest.mock import patch
from control_support import (EXPECT, PACKET, SOURCE, UNIVERSE, FULL, LEAF,
                             GATE, PROBE, GATE_ADDITIONS, Harness, isolated,
                             load_subject, make_case)
import acceptance_gate_baseline_controls as baseline

class Recipes(unittest.TestCase):
    def setUp(self):
        self.scope = isolated()
        self.restored, self.stack = self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)
        self.recipe = load_subject("tests/gate_recipes.py", "rcef_r2_recipes")
        self.stack.enter_context(patch("subprocess.run",
                                      side_effect=AssertionError("construction must not launch a process")))

    def test_CMD05_named_lock_and_all_supported_steps_are_complete(self):
        text = (PACKET / "future_tests/fixtures/complete_workflow.yml").read_text()
        workspace = Path("/rcef-control-workspace")
        environment = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
        for subset in (False, True):
            with self.subTest(subset=subset):
                recipe = self.recipe.workflow_recipe(text, workspace, environment, subset=subset)
                keys = ("lock_heredoc", "workflow_drift",
                        "workflow_subset" if subset else "workflow_default",
                        "additive44", "r2_development")
                self.assertEqual(recipe["script"], "\n".join(EXPECT["commands"][key] for key in keys))
                self.assertEqual(recipe["cwd"], workspace / "RCEF")
                self.assertEqual(recipe["env"], dict(environment,
                    MSF_TOOLS_PATH=str(workspace / ".ci-tools"),
                    PYTHONPATH=str(workspace / ".ci-tools")))

    def test_CMD05_refuses_only_unsupported_workflow_syntax(self):
        text = (PACKET / "future_tests/fixtures/complete_workflow.yml").read_text()
        variants = {
            "folded": text.replace("run: |", "run: >"),
            "conditional": text.replace("        run: |", "        if: success()\n        run: |"),
            "continue_on_error": text.replace("        run: |", "        continue-on-error: true\n        run: |"),
            "unsupported_shell": text.replace("        run: |", "        shell: powershell\n        run: |"),
            "unsupported_cwd": text.replace("working-directory: RCEF", "working-directory: elsewhere"),
            "unresolved_expression": text.replace("${{ github.workspace }}", "${{ inputs.unresolved }}"),
        }
        for name, variant in variants.items():
            with self.subTest(syntax=name), self.assertRaises(ValueError):
                self.recipe.workflow_recipe(variant, Path("/rcef-control-workspace"), {}, subset=True)

    def test_CMD04_markers_and_noncommand_literals_are_preserved(self):
        text = (PACKET / "future_tests/fixtures/marked_document.md").read_text()
        for subset in (False, True):
            with self.subTest(subset=subset):
                script = self.recipe.document_recipe(text, subset=subset)
                commands = list(EXPECT["commands"]["document_exports"])
                commands += [EXPECT["commands"]["document_drift"], "echo scripts/run_acceptance.py",
                             EXPECT["commands"]["document_subset" if subset else "document_default"],
                             EXPECT["commands"]["additive44"], EXPECT["commands"]["r2_development"]]
                self.assertEqual(script.strip(), "\n".join(commands))
                self.assertNotIn("--write", script)
        variants = [text + text, text.replace("RCEF:END ACCEPTANCE", "RCEF:END GENERATE"),
                    text.replace("<!-- RCEF:BEGIN ACCEPTANCE -->", ""),
                    text.replace("<!-- RCEF:BEGIN ACCEPTANCE -->",
                                 "<!-- RCEF:BEGIN ACCEPTANCE -->\n<!-- RCEF:BEGIN ACCEPTANCE -->")]
        for variant in variants:
            with self.subTest(malformed=variant[:50]), self.assertRaises(ValueError):
                self.recipe.document_recipe(variant, subset=True)

    def test_CMD04_rebases_commands_only_and_refuses_compounds(self):
        original = EXPECT["commands"]["document_default"]
        copied = EXPECT["commands"]["document_subset"]
        literal = "echo scripts/run_acceptance.py"
        script = literal + "\n" + EXPECT["commands"]["lock_heredoc"] + "\n" + original
        self.assertEqual(self.recipe.subset_script(script),
                         literal + "\n" + EXPECT["commands"]["lock_heredoc"] + "\n" + copied)
        for command in (original + " && echo done",
                        original + " --qualification-only",
                        original + " --observe-gate-control",
                        original.replace("scripts/run_acceptance.py", "$RUNNER")):
            with self.subTest(command=command), self.assertRaises(ValueError):
                self.recipe.subset_script(command)

class RunnerContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rcef-r2-conformance-")
        self.addCleanup(temporary.cleanup)
        self.h = Harness(temporary.name)

    def cases(self, identifiers=LEAF, seen=None):
        def body(case):
            if seen is not None:
                seen.append(case.id())
        return [make_case(i, body) for i in identifiers]

    def restored(self):
        self.assertTrue(self.h.contexts_completed)
        self.assertTrue(all(self.h.restoration.values()), self.h.restoration)

    def refused(self, code):
        self.assertIsNone(self.h.caught, repr(self.h.caught))
        self.assertEqual(code, 1, self.h.output + self.h.diagnostic)
        self.assertIsNotNone(self.h.payload)
        self.assertEqual(self.h.payload.get("observation",
                         self.h.payload.get("qualification")), "REFUSE")
        self.restored()

    def observed(self, identifiers):
        p = self.h.payload
        self.assertEqual(p["scope"], "gate-control")
        self.assertEqual(p["original_required_methods"], [GATE])
        self.assertEqual(p["selected_methods"], sorted(identifiers))
        self.assertEqual(p["tests_run"], len(identifiers))
        self.assertEqual(Counter(p["executed_methods"]), Counter(identifiers))
        self.assertNotEqual(p.get("qualification"), "PASS")
        self.assertIsNot(p.get("native_qualified"), True)

    def test_SEL01_existing46_supports_absent_gate_sources_and_native9(self):
        for name in ("test_gate.py", "test_qualification_gate.py"):
            (self.h.root / "tests" / name).unlink()
        selected = self.cases()
        for case in selected:
            if case.id().startswith("test_native_consumer."):
                setattr(type(case), case._testMethodName,
                        unittest.skip(EXPECT["preservation"]["native_skip_reason"])(
                            getattr(type(case), case._testMethodName)))
        self.assertEqual(self.h.invoke(selected), 0, self.h.output + self.h.diagnostic)
        self.assertEqual(self.h.payload["required_methods"], sorted(LEAF))
        self.assertEqual(self.h.payload["tests_run"], 46)
        self.assertEqual(len(self.h.payload["skips"]), 9)
        self.restored()

    def test_SEL02_source_present46_excludes_both_gate_bodies(self):
        seen = []
        for name in ("test_gate.py", "test_qualification_gate.py"):
            self.assertTrue((self.h.root / "tests" / name).is_file())
        self.assertEqual(self.h.invoke(self.cases(FULL, seen)), 0)
        self.assertEqual(Counter(seen), Counter(LEAF))
        self.assertEqual(set(self.h.payload), set(UNIVERSE["literals"]["FINAL_KEYS"]))
        self.restored()

    def test_SEL03_observation_executes_gate_and_all_additions(self):
        seen = []
        ids = (GATE,) + GATE_ADDITIONS
        self.assertEqual(self.h.invoke(self.cases(ids, seen), observe=True), 0)
        self.observed(ids)
        self.assertEqual(Counter(seen), Counter(ids))
        self.assertEqual(self.h.payload["observation"], "PASS")
        self.assertEqual(len(self.h.discovery_calls), 1)
        args, kwargs = self.h.discovery_calls[0]
        self.assertEqual(kwargs.get("pattern", args[1] if len(args) > 1 else None), "test_gate.py")
        self.restored()
        with isolated():
            recipes = load_subject("tests/gate_recipes.py", "rcef_r2_record_recipes")
            self.assertEqual(recipes.gate_observation(self.h.output, self.h.code, list(ids)), self.h.payload)
            for expected_ids in ([GATE], list(ids) + ["test_gate.Extra.test_unselected"]):
                with self.assertRaises(ValueError):
                    recipes.gate_observation(self.h.output, self.h.code, expected_ids)
            with self.assertRaises(ValueError):
                recipes.gate_observation(self.h.output, 1, list(ids))

    def test_SEL04_missing_and_duplicates_refuse_before_bodies(self):
        for ids, missing, duplicates in (
            (GATE_ADDITIONS, [GATE], []),
            ((GATE, GATE), [], [GATE]),
            ((GATE,) + GATE_ADDITIONS + (GATE_ADDITIONS[0],), [], [GATE_ADDITIONS[0]]),
        ):
            with self.subTest(ids=ids):
                seen = []
                self.refused(self.h.invoke(self.cases(ids, seen), observe=True))
                self.assertEqual(seen, [])
                self.assertIsNone(self.h.result)
                self.assertEqual(self.h.payload["missing_required_methods"], missing)
                self.assertEqual(self.h.payload["duplicate_methods"], duplicates)

    def test_SEL04_conflict_precedes_import_and_is_not_unknown_option(self):
        with patch.object(self.h.runner.importlib, "import_module",
                          side_effect=AssertionError("conflict must precede imports")) as imported:
            self.h.invoke(self.cases((GATE,)), observe=True, extra_argv=("--qualification-only",))
        self.assertIsInstance(self.h.caught, SystemExit)
        self.assertEqual(self.h.caught.code, 2)
        self.assertNotIn("unrecognized arguments", self.h.diagnostic)
        self.assertEqual(self.h.discovery_calls, [])
        imported.assert_not_called()
        self.restored()

    def test_SEL04_import_failure_is_never_silently_filtered(self):
        def import_failure(case):
            raise ImportError("RCEF_CONTROL_IMPORT_FAILURE")
        failed = make_case("unittest.loader._FailedTest.test_gate", import_failure)
        self.refused(self.h.invoke(self.cases((GATE,)) + [failed], observe=True))
        self.assertIn("RCEF_CONTROL_IMPORT_FAILURE", self.h.output + self.h.diagnostic)
        self.assertNotEqual(self.h.payload.get("observation"), "PASS")

    def test_SEL05_selected_non_gate_addition_has_real_failing_body(self):
        seen = []
        def probe(case):
            seen.append(PROBE)
            case.fail(EXPECT["preservation"]["probe_marker"])
        self.refused(self.h.invoke(self.cases(LEAF, seen) + [make_case(PROBE, probe)]))
        self.assertEqual(Counter(seen), Counter(LEAF + (PROBE,)))
        self.assertEqual(self.h.payload["tests_run"], 47)
        self.assertEqual(self.h.payload["required_methods"], sorted(LEAF))
        self.assertIn(EXPECT["preservation"]["probe_marker"], self.h.diagnostic)

    def test_SEL06_real_child_pass_cannot_complete_faulted_parent(self):
        child = Harness(self.h.root / "child")
        first = RuntimeError("parent callback after real child PASS")
        def gate_body(case):
            seen = []
            code = child.invoke(self.cases(LEAF, seen))
            self.assertEqual(code, 0, child.output + child.diagnostic)
            self.assertEqual(Counter(seen), Counter(LEAF))
            self.assertEqual(child.payload["qualification"], "PASS")
            print(child.output, end="")
        original_success = unittest.TextTestResult.addSuccess
        def fault(result, case):
            if case.id() == GATE:
                raise first
            return original_success(result, case)
        self.h.invoke([make_case(GATE, gate_body)], observe=True, delegates={"addSuccess": fault})
        self.assertIs(self.h.caught, first)
        self.assertTrue(any(r.get("qualification") == "PASS" for r in self.h.records))
        self.assertFalse(any(r.get("observation") == "PASS" for r in self.h.records))
        with isolated():
            recipes = load_subject("tests/gate_recipes.py", "rcef_r2_faulted_record_recipes")
            with self.assertRaises(ValueError):
                recipes.gate_observation(self.h.output, 1, [GATE])
        self.restored()

    def test_PIN01_three_raw_buffers_are_consumed_once(self):
        paths = [self.h.root / p for p in ("scripts/acceptance_cases.json",
                 "evidence/input-contracts/qualification-skip.contract.json",
                 EXPECT["sidecar"]["relative_path"])]
        counts = dict.fromkeys(paths, 0)
        original = Path.open
        def once(path, *args, **kwargs):
            if path in counts:
                counts[path] += 1
                if counts[path] != 1:
                    raise AssertionError("metadata second-read trap")
            return original(path, *args, **kwargs)
        # Observe Path.open and contiguous os.read payloads for these paths.
        # Payload-free descriptor lookups are ignored; a rewind or overlap
        # on an observed opening must still trip the consumption oracle.
        opened = {}
        original_fd_open = os.open
        original_fd_read = os.read
        original_fd_seek = os.lseek
        def open_fd(path, *args, **kwargs):
            fd = original_fd_open(path, *args, **kwargs)
            if Path(path) in counts:
                opened[fd] = (Path(path), 0)
            else:
                opened.pop(fd, None)
            return fd
        def read_fd(fd, *args, **kwargs):
            raw = original_fd_read(fd, *args, **kwargs)
            if raw and fd in opened:
                path, consumed = opened[fd]
                next_offset = consumed + len(raw)
                if original_fd_seek(fd, 0, os.SEEK_CUR) != next_offset:
                    raise AssertionError("metadata repeated or noncontiguous read trap")
                if consumed == 0:
                    counts[path] += 1
                    if counts[path] != 1:
                        raise AssertionError("metadata second-read trap")
                opened[fd] = (path, next_offset)
            return raw
        with patch.object(Path, "open", once), patch.object(os, "open", open_fd), \
                patch.object(os, "read", read_fd):
            self.assertEqual(self.h.invoke(self.cases()), 0)
        self.assertEqual(list(counts.values()), [1, 1, 1])
        self.restored()

    def test_PIN02_missing_or_changed_raw_sidecar_refuses_before_discovery(self):
        path = self.h.root / EXPECT["sidecar"]["relative_path"]
        original = path.read_bytes()
        self.assertEqual(getattr(self.h.runner, EXPECT["sidecar"]["runner_pin_name"]),
                         hashlib.sha256(original).hexdigest())
        for missing in (True, False):
            with self.subTest(missing=missing):
                if missing:
                    path.unlink()
                else:
                    path.write_bytes(original + b"\n")
                self.refused(self.h.invoke(self.cases()))
                self.assertEqual(self.h.discovery_calls, [])
                self.assertIsNone(self.h.result)
                path.write_bytes(original)

    def test_PIN03_matching_digest_cannot_authorize_overrides(self):
        path = self.h.root / EXPECT["sidecar"]["relative_path"]
        original = path.read_bytes()
        good = json.loads(original)
        variants = []
        for key, value in (("reason", "changed"), ("source_condition", "True"),
                           ("eligible_skip_count", 0), ("required_methods", []),
                           ("original_groups", []), ("native_source_sha256", "0" * 64)):
            variant = json.loads(original)
            variant[key] = value
            variants.append(json.dumps(variant).encode())
        variant = json.loads(original)
        variant["source_bindings"].append(dict(variant["source_bindings"][0]))
        variants.append(json.dumps(variant).encode())
        variant = json.loads(original)
        variant["source_bindings"][0]["file"] = "tests/test_native_consumer.py"
        variants.append(json.dumps(variant).encode())
        variant = json.loads(original)
        variant["locators"][1]["id"] = variant["locators"][0]["id"]
        variants.append(json.dumps(variant).encode())
        variant = json.loads(original)
        variant["locators"][0]["id"] = PROBE
        variants.append(json.dumps(variant).encode())
        variant = json.loads(original)
        variant["locators"][0]["reason"] = "matching digest cannot override sealed reason"
        variants.append(json.dumps(variant).encode())
        variants.append(json.dumps(good).encode().replace(b'"schema_version":', b'"schema_version": 1, "schema_version":', 1))
        for raw in variants:
            with self.subTest(raw_sha256=hashlib.sha256(raw).hexdigest()):
                path.write_bytes(raw)
                # Matching test-only pin tests schema separately from raw drift.
                with patch.object(self.h.runner, EXPECT["sidecar"]["runner_pin_name"],
                                  hashlib.sha256(raw).hexdigest()):
                    self.refused(self.h.invoke(self.cases()))
                self.assertEqual(self.h.discovery_calls, [])
                self.assertIsNone(self.h.result)
        path.write_bytes(original)
        self.assertEqual(set(good), set(EXPECT["sidecar"]["exact_keys"]))

    def test_PIN04_exact_successor_rebases_and_admits_original11(self):
        selected = self.cases(FULL)
        reasons = {i: EXPECT["preservation"]["native_skip_reason"]
                   for i in FULL if i.startswith("test_native_consumer.")}
        reasons.update(zip(EXPECT["sidecar"]["locator_ids"],
                           ("native skip control requires configured artifact",
                            "native omission control requires configured artifact")))
        for case in selected:
            if case.id() in reasons:
                setattr(type(case), case._testMethodName,
                        unittest.skip(reasons[case.id()])(
                            getattr(type(case), case._testMethodName)))
        self.assertEqual(self.h.invoke(selected, full=True), 0, self.h.output + self.h.diagnostic)
        self.assertEqual(self.h.payload["tests_run"], 50)
        self.assertEqual(len(self.h.payload["skips"]), 11)
        self.assertEqual(self.h.payload["required_methods"], sorted(FULL))
        self.restored()

    def test_PIN04_sidecar_exact_literals_source_and_locators(self):
        sidecar = json.loads((self.h.root / EXPECT["sidecar"]["relative_path"]).read_bytes())
        specification = EXPECT["sidecar"]
        self.assertEqual(set(sidecar), set(specification["exact_keys"]))
        self.assertEqual(sidecar["schema_version"], 1)
        for name in ("original_manifest_sha256", "original_skip_contract_sha256"):
            self.assertEqual(sidecar[name], specification[name])
        self.assertEqual(len(sidecar["source_bindings"]), 1)
        source = sidecar["source_bindings"][0]
        self.assertEqual(set(source), set(specification["source_row_exact_keys"]))
        self.assertEqual(source["file"], "tests/test_qualification_gate.py")
        self.assertEqual(source["type"], "regular")
        self.assertEqual(source["mode"], 420)
        path = self.h.root / source["file"]
        self.assertFalse(path.is_symlink())
        raw = path.read_bytes()
        self.assertEqual(source["bytes"], len(raw))
        self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
        tree = ast.parse(raw)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "QualificationGate")
        methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual([r["id"] for r in sidecar["locators"]], specification["locator_ids"])
        reasons = ("native skip control requires configured artifact",
                   "native omission control requires configured artifact")
        for locator, reason in zip(sidecar["locators"], reasons):
            self.assertEqual(set(locator), set(specification["locator_row_exact_keys"]))
            method = methods[locator["id"].split(".")[-1]]
            self.assertEqual(method.lineno, locator["method_line"])
            self.assertEqual(len(method.decorator_list), 1)
            decorator = method.decorator_list[0]
            self.assertEqual(decorator.lineno, locator["decorator_line"])
            self.assertEqual(ast.dump(decorator.func), ast.dump(ast.parse("unittest.skipUnless", mode="eval").body))
            self.assertEqual(ast.dump(decorator.args[0]), ast.dump(ast.parse("os.environ.get('MSF_NATIVE_PATH')", mode="eval").body))
            self.assertEqual(ast.literal_eval(decorator.args[1]), reason)

    def test_PIN05_changed_control_source_is_refused_at_skip_admission(self):
        path = self.h.root / "tests/test_qualification_gate.py"
        original = path.read_bytes()
        path.write_bytes(original + b"\n# changed whole-source binding\n")
        selected = self.cases(FULL)
        identifier = EXPECT["sidecar"]["locator_ids"][0]
        for case in selected:
            if case.id() == identifier:
                setattr(type(case), case._testMethodName,
                        unittest.skip("native skip control requires configured artifact")(
                            getattr(type(case), case._testMethodName)))
        self.refused(self.h.invoke(selected, full=True))
        self.assertEqual(self.h.payload["tests_run"], 50)
        path.write_bytes(original)

    def test_LIFE01_all_modes_reuse_helpers_and_execute_stock_hooks(self):
        for mode, ids in (("full", FULL), ("subset", LEAF), ("observe", (GATE,) + GATE_ADDITIONS)):
            with self.subTest(mode=mode):
                seen, hooks = [], []
                target = ids[0]
                def body(case):
                    seen.append(case.id())
                    if case.id() == target:
                        hooks.append("body")
                        with case.subTest(healthy=True):
                            hooks.append("subtest")
                            case.assertEqual(1, 1)
                def setup(case):
                    hooks.append("setUp")
                    case.addCleanup(hooks.append, "cleanup")
                def teardown(case):
                    hooks.append("tearDown")
                selected = [make_case(i, body, {"setUp": setup, "tearDown": teardown}
                                     if i == target else {}) for i in ids]
                with patch.object(self.h.runner, "run_observed", wraps=self.h.runner.run_observed) as run_core, \
                     patch.object(self.h.runner, "admit_observed", wraps=self.h.runner.admit_observed) as admit_core:
                    code = self.h.invoke(selected, full=mode == "full", observe=mode == "observe")
                self.assertEqual(code, 0, self.h.output + self.h.diagnostic)
                run_core.assert_called_once()
                admit_core.assert_called_once()
                self.assertEqual(Counter(seen), Counter(ids))
                self.assertEqual(hooks, ["setUp", "body", "subtest", "tearDown", "cleanup"])
                starts, stops, terminals, expected = self.h.ledger(ids)
                self.assertEqual(starts, expected)
                self.assertEqual(stops, expected)
                self.assertEqual(terminals, expected)
                self.assertEqual(self.h.result.lifecycle[target], ["startTest", "addSuccess", "stopTest"])
                self.restored()

    def test_LIFE02_stock_failure_and_error_terminals_refuse(self):
        def fail(case):
            case.fail("ordinary assertion control")
        def failed_subtests(case):
            for value in (1, 2):
                with case.subTest(value=value):
                    case.fail("failed subtest control")
        def cleanup(case):
            def cleanup_fault():
                raise RuntimeError("cleanup control")
            case.addCleanup(cleanup_fault)
        def hook_fault(case):
            raise RuntimeError("hook control")
        for name, body, hooks, expecting in (
            ("assertion", fail, {}, False), ("subtests", failed_subtests, {}, False),
            ("setup", None, {"setUp": hook_fault}, False),
            ("teardown", None, {"tearDown": hook_fault}, False),
            ("cleanup", cleanup, {}, False),
            ("expected", fail, {}, True), ("unexpected", None, {}, True)):
            with self.subTest(outcome=name):
                case = make_case(GATE, body, hooks)
                if expecting:
                    setattr(type(case), case._testMethodName,
                            unittest.expectedFailure(getattr(type(case), case._testMethodName)))
                self.refused(self.h.invoke([case], observe=True))
        def two_errors(case):
            case.addCleanup(hook_fault, case)
        self.refused(self.h.invoke([make_case(GATE, two_errors, {"tearDown": hook_fault})], observe=True))
        self.assertEqual(self.h.payload["errors"], 2)
        self.assertEqual([name for i, name in self.h.result.terminals if i == GATE], ["addError", "addError"])

    def test_LIFE03_first_object_traceback_and_later_fault_survive_all_modes(self):
        for mode, ids in (("full", FULL), ("subset", LEAF), ("observe", (GATE,) + GATE_ADDITIONS)):
            for stopping in ("stopTest", "stopTestRun"):
                with self.subTest(mode=mode, stopping=stopping):
                    first, second = RuntimeError("callback A"), RuntimeError("callback B")
                    def callback_A(result, case):
                        raise first
                    def callback_B(*args):
                        raise second
                    self.h.invoke(self.cases(ids), full=mode == "full", observe=mode == "observe",
                                  delegates={"addSuccess": callback_A, stopping: callback_B})
                    self.assertIs(self.h.caught, first)
                    self.assertIs(self.h.result.first_callback_fault, first)
                    self.assertIn("callback_A", [f.name for f in traceback.extract_tb(
                                  self.h.result.first_callback_traceback)])
                    self.assertTrue(any(error is second for error, _ in self.h.result.callback_faults))
                    chain, current = [], first
                    while current is not None and not any(current is item for item in chain):
                        chain.append(current)
                        current = current.__cause__ or current.__context__
                    self.assertTrue(any(error is second for error in chain))
                    self.assertFalse(any(r.get("observation") == "PASS" or
                                         r.get("qualification") == "PASS" for r in self.h.records))
                    self.restored()

    def test_LIFE03_duration_fault_on312_and_healthy_stock311(self):
        ids = (GATE,) + GATE_ADDITIONS
        seen = []
        if hasattr(unittest.TextTestResult, "addDuration"):
            first, second = RuntimeError("duration callback A"), RuntimeError("duration finally B")
            def duration_A(result, case, elapsed):
                raise first
            def stop_B(result):
                raise second
            self.h.invoke(self.cases(ids, seen), observe=True,
                          delegates={"addDuration": duration_A, "stopTestRun": stop_B})
            self.assertIs(self.h.caught, first)
            self.assertIs(self.h.result.first_callback_fault, first)
            self.assertIn("duration_A", [f.name for f in traceback.extract_tb(
                          self.h.result.first_callback_traceback)])
            self.assertTrue(any(error is second for error, _ in self.h.result.callback_faults))
            self.assertFalse(any(r.get("observation") == "PASS" for r in self.h.records))
        else:
            self.assertEqual(self.h.invoke(self.cases(ids, seen), observe=True), 0)
            self.assertEqual(Counter(seen), Counter(ids))
            self.assertEqual(self.h.result.skipped, [])
        self.restored()

    def test_LIFE04_observation_refuses_malformed_protocol_and_missing_addition(self):
        ids = (GATE,) + GATE_ADDITIONS
        def start_only(suite, result, debug=False):
            for case in suite:
                result.startTest(case)
            return result
        def no_stop(suite, result, debug=False):
            for case in suite:
                result.startTest(case)
                result.addSuccess(case)
            return result
        def reverse(suite, result, debug=False):
            for case in suite:
                result.stopTest(case)
                result.addSuccess(case)
                result.startTest(case)
            return result
        stock = unittest.TestSuite.run
        def duplicate(suite, result, debug=False):
            for case in suite:
                result.startTest(case)
                case(result)
            return result
        def foreign(suite, result, debug=False):
            stock(suite, result, debug)
            make_case("test_foreign.Injected.test_unselected")(result)
            return result
        def missing_addition(suite, result, debug=False):
            for case in suite:
                if case.id() != GATE_ADDITIONS[0]:
                    case(result)
            return result
        for action in (start_only, no_stop, reverse, duplicate, foreign, missing_addition):
            with self.subTest(protocol=action.__name__):
                self.refused(self.h.invoke(self.cases(ids), observe=True, suite_run=action))
        original_start = unittest.TextTestResult.startTest
        for offset in (-3, -1, 1):
            with self.subTest(counter_offset=offset):
                seen = []
                def counter(result, case):
                    original_start(result, case)
                    if case.id() == GATE:
                        result.testsRun += offset
                self.refused(self.h.invoke(self.cases(ids, seen), observe=True,
                                          delegates={"startTest": counter}))
                self.assertEqual(Counter(seen), Counter(ids))

    def test_LIFE05_streams_restore_after_pass_refusal_and_callback_fault(self):
        self.assertEqual(self.h.invoke(self.cases((GATE,)), observe=True), 0)
        self.restored()
        def fail(case):
            case.fail("stream refusal control")
        self.refused(self.h.invoke([make_case(GATE, fail)], observe=True))
        first = RuntimeError("stream callback A")
        def callback_A(result, case):
            raise first
        self.h.invoke(self.cases((GATE,)), observe=True, delegates={"addSuccess": callback_A})
        self.assertIs(self.h.caught, first)
        self.restored()

    def test_LIFE06_entry_and_exit_faults_never_claim_context_completion(self):
        first, second = RuntimeError("actual callback A"), RuntimeError("context exit B")
        class BrokenExit:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                raise second
        def callback_A(result, case):
            raise first
        self.h.invoke(self.cases((GATE,)), observe=True, delegates={"addSuccess": callback_A},
                      exit_context=BrokenExit())
        self.assertIs(self.h.caught, first)
        self.assertIn(second, self.h.secondary)
        self.assertIsNone(self.h.code)
        self.assertFalse(self.h.contexts_completed)
        self.assertEqual(set(self.h.restoration), {"stdout", "stderr", "argv", "path", "environment", "modules"})
        entry = RuntimeError("context entry control")
        class BrokenEntry:
            def __enter__(self):
                raise entry
            def __exit__(self, *args):
                raise AssertionError("unentered context must not be released")
        self.h.invoke(self.cases((GATE,)), observe=True, exit_context=BrokenEntry())
        self.assertIs(self.h.caught, entry)
        self.assertFalse(self.h.contexts_completed)
        self.assertEqual(self.h.discovery_calls, [])

class Preservation(unittest.TestCase):
    def test_original44_method_asts_and_literal_universes_are_unchanged(self):
        oracle = json.loads((PACKET / "PRESERVATION_ORACLE.json").read_text())
        tree = ast.parse((SOURCE / "tests/acceptance_runner_regressions.py").read_bytes())
        actual = {}
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                for method in cls.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith("test_"):
                        actual[(cls.name, method.name)] = ast.dump(method, include_attributes=False)
        expected = {(r["class_name"], r["method"]): r["ast_by_runtime"][f"{sys.version_info.major}.{sys.version_info.minor}"]
                    for r in oracle["original44"]}
        self.assertEqual(len(expected), 44)
        self.assertEqual(actual, expected)
        assignments = {t.id: ast.dump(n, include_attributes=False)
                       for n in tree.body if isinstance(n, ast.Assign)
                       for t in n.targets if isinstance(t, ast.Name)}
        for name, expected_ast in oracle["original44_assignments"].items():
            self.assertEqual(assignments[name], expected_ast)

    def test_original_assertions_and_three_honest_additions_remain(self):
        original_literals = json.loads((PACKET / "ORIGINAL_GATE_LITERALS.json").read_text())
        for relative, name in (("tests/test_gate.py", "WRONG_ROWS"),
                               ("tests/test_qualification_gate.py", "PROBE")):
            tree = ast.parse((SOURCE / relative).read_bytes())
            value = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
            self.assertEqual(json.loads(json.dumps(value)), original_literals[name])
        required = json.loads((PACKET / "REQUIRED_CONTROL_ASSERTIONS.json").read_text())
        for relative, rows in required.items():
            tree = ast.parse((SOURCE / relative).read_bytes())
            calls, methods = {}, []
            for cls in tree.body:
                if isinstance(cls, ast.ClassDef):
                    for method in cls.body:
                        if isinstance(method, ast.FunctionDef):
                            key = cls.name + "." + method.name
                            if method.name in ("test_configured_public_gate_refuses_controlled_native_skip", "test_configured_public_gate_refuses_omitted_required_method"):
                                self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "unlink" for n in ast.walk(method)), "native controls must retain gate sources throughout")
                            methods.append(relative.removeprefix("tests/").removesuffix(".py") + "." + key)
                            calls[key] = Counter(ast.dump(n, include_attributes=False)
                                                 for n in ast.walk(method) if isinstance(n, ast.Call))
            for row in rows:
                self.assertGreaterEqual(calls[row["method"]][row["ast"]], 1)
            if relative == "tests/test_gate.py":
                for identifier in EXPECT["preservation"]["actual_three_public_additions"]:
                    self.assertEqual(methods.count(identifier), 1)

    def test_original_sealed_and_leaf_source_bytes_are_unchanged(self):
        bindings = json.loads((PACKET / "SOURCE_BINDINGS.json").read_text())
        oracle = json.loads((PACKET / "PRESERVATION_ORACLE.json").read_text())
        rows = {r["relative_path"]: r for r in bindings["files"]}
        for relative in oracle["unchanged_files"]:
            raw = (SOURCE / relative).read_bytes()
            self.assertEqual(len(raw), rows[relative]["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), rows[relative]["sha256"])

    def test_native_control_copies_retain_both_gate_sources(self):
        with tempfile.TemporaryDirectory(prefix="rcef-r2-source-copy-") as scratch:
            workspace = Path(scratch)
            tools = workspace / "inert-tools"
            tools.mkdir()
            environment = dict(EXPECT["future_environment"], MSF_TOOLS_PATH=str(tools))
            with isolated(environment) as (_, stack):
                module = load_subject("tests/test_qualification_gate.py", "rcef_r2_copy_subject")
                stack.enter_context(patch.object(module.subprocess, "run",
                        side_effect=AssertionError("source fixture must not execute")))
                checkout, env = module.QualificationGate("test_configured_public_gate_refuses_controlled_native_skip").fixture(workspace)
                for name in ("test_gate.py", "test_qualification_gate.py"):
                    self.assertEqual((checkout / "tests" / name).read_bytes(),
                                     (SOURCE / "tests" / name).read_bytes())
        call = baseline.BaselineCommands("test_CMD01_complete_current_named_lock_before_workload").capture_workflow()
        self.assertTrue(all(call["copied_gate_sources"].values()))

if __name__ == "__main__":
    unittest.main(verbosity=2)
