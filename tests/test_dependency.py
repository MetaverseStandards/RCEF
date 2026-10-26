# SPDX-License-Identifier: MIT
"""How RCEF finds and checks its msf-tools dependency."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def plain_env():
    """The caller's environment without any explicit msf-tools checkout selection."""
    env = dict(os.environ)
    for name in ('MSF_TOOLS_PATH', 'PYTHONPATH'):
        env.pop(name, None)
    return env


class InstalledPackage(unittest.TestCase):
    def test_test_modules_import_the_installed_package(self):
        modules = sorted(p.stem for p in (ROOT / 'tests').glob('test_*.py'))
        result = subprocess.run([sys.executable, '-B', '-c', 'import sys\nfor m in sys.argv[1:]: __import__(m)',
                                 *modules], cwd=ROOT / 'tests', env=plain_env(),
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_has_no_checkout_override(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'check.py'), '--help'],
                                env=plain_env(), capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('--tools-path', result.stdout)


if __name__ == '__main__':
    unittest.main()
