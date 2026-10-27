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


class LoadedCode(unittest.TestCase):
    """The code a run depends on is every repository module it has imported, wherever it lives."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-prov-')
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name).resolve()
        self.git = CodeCommit.git.__get__(self)
        self.commit = CodeCommit.commit.__get__(self)
        self.git('init', '-q')
        (self.repo / 'examples').mkdir()
        (self.repo / 'tools').mkdir()
        (self.repo / 'examples/rcef_prov_helper.py').write_text('SCALE = 1\n')
        (self.repo / 'tools/rcef_prov_tool.py').write_text('import rcef_prov_helper\n')
        self.code = self.commit('harness')
        for name in ('examples', 'tools'):
            sys.path.insert(0, str(self.repo / name))
            self.addCleanup(sys.path.remove, str(self.repo / name))
        import rcef_prov_tool  # noqa: F401
        self.addCleanup(sys.modules.pop, 'rcef_prov_tool')
        self.addCleanup(sys.modules.pop, 'rcef_prov_helper')

    def test_imported_modules_inside_the_repository_are_the_code(self):
        self.assertEqual(provenance.loaded_files(self.repo), ['examples/rcef_prov_helper.py', 'tools/rcef_prov_tool.py'])

    def test_a_changed_helper_outside_tools_is_refused(self):
        (self.repo / 'examples/rcef_prov_helper.py').write_text('SCALE = 2\n')
        self.commit('change the helper')
        problem = provenance.code_problem(self.repo, self.code, provenance.loaded_files(self.repo))
        self.assertIn('examples/rcef_prov_helper.py', problem)


if __name__ == '__main__':
    unittest.main()
