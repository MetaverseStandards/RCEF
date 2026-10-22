#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute the published gates against coherent metadata regressions."""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest

from gate_recipes import document_recipe, workflow_recipe, source_complete_fixture

ROOT = Path(__file__).resolve().parents[1]
WRONG_ROWS = {
    'godot.base.toml': ('godot.base.FT_MOUTH_CLOSED',),
    'vrcft.artist.base.toml': ('vrcft.artist.base.MouthClosed',),
    'vrcft.transport.toml': ('vrcft.transport.MouthClosed',),
    'vrcft.parameter.float.toml': (
        'vrcft.parameter.float.v2.MouthClosed',
        'vrcft.parameter.float.v2.EyeLeftX', 'vrcft.parameter.float.v2.EyeLeftY',
        'vrcft.parameter.float.v2.EyeRightX', 'vrcft.parameter.float.v2.EyeRightY',
        'vrcft.parameter.float.v2.EyeX', 'vrcft.parameter.float.v2.EyeY',
    ),
    'arkit.ancillary.toml': ('arkit.ancillary.leftEyeTransform',),
}


class Gate(unittest.TestCase):
    def test_published_gates_reject_coherent_wrong_metadata(self):
        tools = Path(os.environ['MSF_TOOLS_PATH']).resolve(strict=True)
        with tempfile.TemporaryDirectory(prefix='rcef-gate-') as temporary:
            workspace = Path(temporary)
            checkout, environment = source_complete_fixture(ROOT, workspace)

            workflow = (ROOT / '.github/workflows/check.yml').read_text()
            recipe = workflow_recipe(workflow, workspace, environment, subset=True)
            commands = recipe['script'].splitlines()
            self.assertTrue(commands, 'workflow must have executable gate steps')
            self.assertEqual(recipe['cwd'], checkout)
            gates = [('workflow', recipe['script'], recipe['env'])]
            for name in ('README.md', 'CONTRIBUTING.md'):
                text = (ROOT / name).read_text()
                script = document_recipe(text, subset=True)
                self.assertTrue(script, f'{name} must publish executable local commands')
                gates.append((name, script, environment))

            def run(name, script, selected_environment):
                result = subprocess.run(['/bin/sh', '-c', 'set -e\n' + script],
                                        cwd=checkout, env=selected_environment,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, check=False, timeout=120)
                print(f'GATE {name}: cwd={checkout}, interpreter={sys.executable}, '
                      f'MSF_TOOLS_PATH={selected_environment.get("MSF_TOOLS_PATH")}, '
                      f'PYTHONPATH={selected_environment.get("PYTHONPATH")}, '
                      f'exit={result.returncode}\n{script}\n{result.stdout}', flush=True)
                return result

            for name, script, selected_environment in gates:
                result = run(name + ' current', script, selected_environment)
                self.assertEqual(result.returncode, 0, result.stdout)

            leaf_ids = self.leaf_methods()
            self.assertGreaterEqual(len(leaf_ids), 46)
            edited = 0
            for filename, identities in WRONG_ROWS.items():
                path = checkout / 'profiles' / filename
                blocks = path.read_text().split('[[signals]]')
                for index in range(1, len(blocks)):
                    signal = tomllib.loads('[[signals]]' + blocks[index])['signals'][0]
                    if signal['id'] in identities:
                        for field, value in (('region', 'eyelid'), ('side', 'shared')):
                            blocks[index], replacements = re.subn(
                                rf'^{field} = "[^"]+"$', f'{field} = "{value}"',
                                blocks[index], flags=re.MULTILINE)
                            self.assertEqual(replacements, 1)
                        edited += 1
                path.write_text('[[signals]]'.join(blocks))
            self.assertEqual(edited, 11)
            render = run('wrong metadata regeneration',
                         f'python3 -B check.py --tools-path "{tools}" --write', environment)
            self.assertEqual(render.returncode, 0, render.stdout)
            generated = json.loads((checkout / 'generated/rcef.pack.json').read_text())
            self.assertEqual(generated['data_version'], '0.1.1')
            signals = {signal['id']: signal for signal in generated['signals']}
            for identities in WRONG_ROWS.values():
                for identity in identities:
                    self.assertEqual((signals[identity]['region'], signals[identity]['side']),
                                     ('eyelid', 'shared'))
            drift = run('wrong metadata drift',
                        f'python3 -B check.py --tools-path "{tools}"', environment)
            self.assertEqual(drift.returncode, 0, drift.stdout)
            for name, script, selected_environment in gates:
                with self.subTest(gate=name):
                    result = run(name + ' wrong metadata', script, selected_environment)
                    self.assertNotEqual(result.returncode, 0,
                                        f'{name} accepted all eleven metadata defects')
                    self.assertIn('test_primary_metadata_rows_in_authoring', result.stdout)
                    self.assertIn('test_primary_metadata_rows_in_generated_pack', result.stdout)
                    # Preserve the original46 oracle when no leaf additions
                    # exist; the current tree also selects readable-report tests.
                    if len(leaf_ids) == 46:
                        self.assertRegex(result.stdout, r'Ran 46 tests\b')
                    else:
                        self.assertRegex(result.stdout, rf'Ran {len(leaf_ids)} tests\b')
                    self.assertRegex(result.stdout, r'FAILED \(failures=22(?:, skipped=9)?\)')
                    record = self.qualification_record(result.stdout)
                    self.assertEqual(record['qualification'], 'REFUSE')
                    self.assertEqual(len(record['required_methods']), 46)
                    if len(leaf_ids) == 46:
                        self.assertEqual(record['tests_run'], 46)
                    else:
                        self.assertEqual(record['tests_run'], len(leaf_ids))
                    self.assertEqual(Counter(record['executed_methods']), Counter(leaf_ids),
                                     'leaf execution differs from independent discovery')
                    self.assertEqual(record['failures'], 22)
                    self.assertEqual(record['errors'], 0)
                    self.assertEqual(len(record['skips']), 0 if os.environ.get('MSF_NATIVE_PATH') else 9)


    def leaf_methods(self):
        """Independently discover the original46 plus all current leaf additions."""
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
        pending, identifiers = [suite], []
        while pending:
            item = pending.pop()
            if isinstance(item, unittest.TestSuite):
                pending.extend(item)
            elif item.id().split('.')[0] not in {'test_gate', 'test_qualification_gate'}:
                identifiers.append(item.id())
        self.assertEqual(len(set(identifiers)), len(identifiers), 'duplicate independently discovered leaf')
        return tuple(sorted(identifiers))

    def published_recipes(self, workspace, environment):
        recipe = workflow_recipe((ROOT / '.github/workflows/check.yml').read_text(),
                                 workspace, environment, subset=True)
        gates = [('workflow', recipe['script'], recipe['env'])]
        for name in ('README.md', 'CONTRIBUTING.md'):
            gates.append((name, document_recipe((ROOT / name).read_text(), subset=True), environment))
        return gates

    def run_recipe(self, checkout, environment, script):
        result = subprocess.run(['/bin/sh', '-c', 'set -e\n' + script], cwd=checkout,
                                env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, check=False, timeout=120)
        print(f'GATE_CONTROL cwd={checkout} exit={result.returncode}\n{script}\n{result.stdout}', flush=True)
        return result

    def qualification_record(self, output):
        records = []
        for line in output.splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict) and 'qualification' in record:
                records.append(record)
        self.assertTrue(records, 'public leaf must emit its own qualification record')
        return records[-1]

    def test_published_workflow_refuses_wrong_shared_commit(self):
        with tempfile.TemporaryDirectory(prefix='rcef-lock-') as temporary:
            workspace = Path(temporary)
            checkout, environment = source_complete_fixture(ROOT, workspace)
            _, script, selected_environment = self.published_recipes(workspace, environment)[0]
            current = self.run_recipe(checkout, selected_environment, script)
            self.assertEqual(current.returncode, 0, current.stdout)
            path = checkout / 'evidence/tooling.lock.json'
            lock = json.loads(path.read_text())
            lock['git_commit'] = '0' * 40
            path.write_text(json.dumps(lock, indent=2) + '\n')
            marker = 'RCEF_WORKLOAD_AFTER_LOCK_STARTED'
            drift = 'python -B check.py --tools-path ../.ci-tools'
            self.assertEqual(script.count(drift), 1)
            instrumented = script.replace(drift, f'echo {marker}\n' + drift)
            wrong = self.run_recipe(checkout, selected_environment, instrumented)
            self.assertNotEqual(wrong.returncode, 0, wrong.stdout)
            self.assertIn('Shared dependency differs from lock:', wrong.stdout)
            self.assertNotIn(marker, wrong.stdout)
            self.assertNotIn('Ran ', wrong.stdout)

    def test_published_acceptance_gates_refuse_generated_drift(self):
        with tempfile.TemporaryDirectory(prefix='rcef-drift-') as temporary:
            workspace = Path(temporary)
            checkout, environment = source_complete_fixture(ROOT, workspace)
            gates = self.published_recipes(workspace, environment)
            tools = Path(os.environ['MSF_TOOLS_PATH']).resolve(strict=True)
            generation = f'python3 -B check.py --tools-path "{tools}" --write'
            rendered = self.run_recipe(checkout, environment, generation)
            self.assertEqual(rendered.returncode, 0, rendered.stdout)
            for name, script, selected_environment in gates:
                current = self.run_recipe(checkout, selected_environment, script)
                self.assertEqual(current.returncode, 0, f'{name}: {current.stdout}')
            path = checkout / 'generated/rcef.pack.json'
            path.write_bytes(path.read_bytes() + b' ')
            tampered = path.read_bytes()
            direct = self.run_recipe(checkout, environment,
                                     f'python3 -B check.py --tools-path "{tools}"')
            self.assertNotEqual(direct.returncode, 0, direct.stdout)
            self.assertEqual(path.read_bytes(), tampered)
            for name, script, selected_environment in gates:
                with self.subTest(gate=name):
                    self.assertNotIn('--write', script)
                    refused = self.run_recipe(checkout, selected_environment, script)
                    self.assertNotEqual(refused.returncode, 0, refused.stdout)
                    self.assertNotIn('Ran ', refused.stdout)
                    self.assertEqual(path.read_bytes(), tampered)

    def test_published_gates_refuse_semantic_skip(self):
        with tempfile.TemporaryDirectory(prefix='rcef-semantic-skip-') as temporary:
            workspace = Path(temporary)
            checkout, environment = source_complete_fixture(ROOT, workspace)
            gates = self.published_recipes(workspace, environment)
            for name, script, selected_environment in gates:
                current = self.run_recipe(checkout, selected_environment, script)
                self.assertEqual(current.returncode, 0, f'{name}: {current.stdout}')
            leaf_ids = self.leaf_methods()
            method = 'test_sem01_literal_identities_and_63_single_direction_comparisons'
            identifier = 'test_hardening.Hardening.' + method
            reason = 'controlled unauthorized semantic skip'
            path = checkout / 'tests/test_hardening.py'
            source = path.read_text()
            marker = f'    def {method}(self):'
            self.assertEqual(source.count(marker), 1)
            path.write_text(source.replace(marker, f'    @unittest.skip({reason!r})\n' + marker))
            direct = self.run_recipe(checkout, environment,
                f'python3 -B -m unittest discover -s tests -p test_hardening.py -k {method} -v')
            self.assertEqual(direct.returncode, 0, direct.stdout)
            self.assertIn(reason, direct.stdout)
            self.assertIn('skipped=1', direct.stdout)
            for name, script, selected_environment in gates:
                with self.subTest(gate=name):
                    public = self.run_recipe(checkout, selected_environment, script)
                    self.assertNotEqual(public.returncode, 0, public.stdout)
                    self.assertIn(identifier, public.stdout)
                    self.assertIn(reason, public.stdout)
                    record = self.qualification_record(public.stdout)
                    self.assertEqual(record['qualification'], 'REFUSE')
                    self.assertEqual(len(record['required_methods']), 46)
                    if len(leaf_ids) == 46:
                        self.assertEqual(record['tests_run'], 46)
                    else:
                        self.assertEqual(record['tests_run'], len(leaf_ids))
                    self.assertEqual(Counter(record['executed_methods']), Counter(leaf_ids),
                                     'leaf execution differs from independent discovery')
                    self.assertIn([identifier, reason], record['skips'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
