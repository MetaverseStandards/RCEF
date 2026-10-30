# SPDX-License-Identifier: MIT
"""docs/routes.svg and docs/ab-coverage.svg are what scripts/export_figures.py writes from the data."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Figures(unittest.TestCase):
    def test_figures_are_current(self):
        result = subprocess.run([sys.executable, '-B', 'scripts/export_figures.py'], cwd=ROOT, capture_output=True,
                                text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
