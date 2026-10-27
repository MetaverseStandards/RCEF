# SPDX-License-Identifier: MIT
"""A held-out run must use exactly the code a calibration record names."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/calibration'))
import provenance  # noqa: E402


class CodeCommit(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-prov-')
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        self.git('init', '-q')
        (self.repo / 'tool').mkdir()
        (self.repo / 'tool/fit.py').write_text('A = 1\n')
        self.code = self.commit('harness')
        (self.repo / 'record.cal').write_text('frozen\n')
        self.commit('freeze')

    def git(self, *args):
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def problem(self, commit):
        return provenance.code_problem(self.repo, commit, ['tool'])

    def test_the_freeze_commit_after_the_code_commit_is_accepted(self):
        self.assertIsNone(self.problem(self.code))

    def test_changed_code_since_the_record_is_refused(self):
        (self.repo / 'tool/fit.py').write_text('A = 2\n')
        self.commit('change the fit')
        problem = self.problem(self.code)
        self.assertIn('tool/fit.py', problem)
        self.assertIn(self.code[:12], problem)

    def test_uncommitted_code_is_refused(self):
        (self.repo / 'tool/fit.py').write_text('A = 3\n')
        self.assertIn('uncommitted', self.problem(self.code))

    def test_a_commit_that_is_not_in_the_history_is_refused(self):
        self.git('checkout', '-q', '--orphan', 'other')
        self.commit('unrelated')
        self.assertIn('not an ancestor', self.problem(self.code))
        self.assertIn('not a commit', self.problem('0' * 40))


if __name__ == '__main__':
    unittest.main()
