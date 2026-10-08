#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute the published gates against coherent metadata regressions."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

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
            checkout = workspace / 'RCEF'
            checkout.mkdir()
            for name in ('pack.toml', 'check.py', 'data', 'profiles', 'mappings',
                         'evidence', 'fixtures', 'generated', 'scripts'):
                source = ROOT / name
                if source.is_dir():
                    shutil.copytree(source, checkout / name)
                else:
                    shutil.copy2(source, checkout / name)
            shutil.copytree(ROOT / 'tests', checkout / 'tests',
                            ignore=shutil.ignore_patterns('__pycache__', 'test_gate.py',
                                                         'test_qualification_gate.py'))
            # The copied public commands exercise all nonrecursive suites. The
            # parent discovery runs these integration controls exactly once.
            for name in ('msf-tools', '.ci-tools'):
                (workspace / name).symlink_to(tools, target_is_directory=True)
            binaries = workspace / 'bin'
            binaries.mkdir()
            for name in ('python', 'python3'):
                (binaries / name).symlink_to(sys.executable)
            environment = os.environ.copy()
            environment.pop('PYTHONPATH', None)
            environment['PATH'] = str(binaries) + os.pathsep + environment['PATH']
            environment['PYTHONDONTWRITEBYTECODE'] = '1'

            workflow = (ROOT / '.github/workflows/check.yml').read_text()
            commands = re.findall(r'^      - run: (.+)$', workflow, re.MULTILINE)
            self.assertTrue(commands, 'workflow must have executable gate steps')
            workflow_environment = environment.copy()
            for key, value in re.findall(r'^      (MSF_TOOLS_PATH|PYTHONPATH): (.+)$',
                                         workflow, re.MULTILINE):
                workflow_environment[key] = value.replace('${{ github.workspace }}', str(workspace))
            gates = [('workflow', '\n'.join(commands), workflow_environment)]
            for name in ('README.md', 'CONTRIBUTING.md'):
                text = (ROOT / name).read_text()
                blocks = re.findall(r'```sh\n(.*?)```', text, re.DOTALL)
                script = '\n'.join(blocks) if blocks else '\n'.join(
                    re.findall(r'`(python3 -B [^`]+)`', text))
                self.assertTrue(script, f'{name} must publish executable local commands')
                script = script.replace('scripts/run_acceptance.py',
                                        'scripts/run_acceptance.py --qualification-only')
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
                    self.assertRegex(result.stdout, r'Ran 46 tests\b')
                    self.assertRegex(result.stdout, r'FAILED \(failures=22(?:, skipped=9)?\)')


if __name__ == '__main__':
    unittest.main(verbosity=2)
