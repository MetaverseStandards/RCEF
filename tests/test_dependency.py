# SPDX-License-Identifier: MIT
"""How RCEF finds and checks its msf-tools dependency."""
import base64
import hashlib
import importlib.util
from importlib import metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)
LOCKED_COMMIT = json.loads((ROOT / 'evidence/tooling.lock.json').read_text())['git_commit']
OTHER_COMMIT = '0' * 40
# Running the fake package writes this file, so a test can tell whether check.py
# got as far as starting msf-tools.
FAKE_MAIN = 'import os, pathlib\npathlib.Path(os.environ["RCEF_TEST_MARKER"]).write_text("ran")\n'


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



def record_line(site, name):
    digest = hashlib.sha256((site / name).read_bytes()).digest()
    value = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return f'{name},sha256={value},{(site / name).stat().st_size}'


def fake_site(root, commit, version='0.1.1'):
    """A minimal site-packages holding an msf-tools distribution installed from Git."""
    site = Path(root) / 'site'
    package = site / 'msf_tools'
    info = site / f'msf_tools-{version}.dist-info'
    package.mkdir(parents=True)
    info.mkdir()
    (package / '__init__.py').write_text('VALUE = 1\n')
    (package / '__main__.py').write_text(FAKE_MAIN)
    (info / 'METADATA').write_text(f'Metadata-Version: 2.1\nName: msf-tools\nVersion: {version}\n')
    (info / 'direct_url.json').write_text(json.dumps(
        {'url': 'file:///msf-tools', 'vcs_info': {'vcs': 'git', 'commit_id': commit}}))
    write_record(site)
    return site


def write_record(site):
    info = next(site.glob('*.dist-info'))
    names = [p.relative_to(site).as_posix() for p in sorted(site.rglob('*'))
             if p.is_file() and p.name != 'RECORD']
    lines = [record_line(site, name) for name in names] + [f'{info.name}/RECORD,,']
    (info / 'RECORD').write_text('\n'.join(lines) + '\n')


def distribution(site):
    return metadata.Distribution.at(next(site.glob('*.dist-info')))


class LockVerification(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rcef-dep-')
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        self.site = fake_site(self.temp, LOCKED_COMMIT)
        self.lock = check.lock_for(distribution(self.site))

    def problems(self):
        return check.verify_installed(self.lock, distribution(self.site))

    def test_matching_install_is_accepted(self):
        self.assertEqual(self.problems(), [])

    def test_real_installed_package_matches_the_lock(self):
        lock = json.loads(check.LOCK.read_text())
        self.assertEqual(check.verify_installed(lock, metadata.distribution('msf-tools')), [])

    def test_wrong_commit_is_refused(self):
        self.lock['git_commit'] = OTHER_COMMIT
        problems = self.problems()
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(LOCKED_COMMIT, problems[0])
        self.assertIn(OTHER_COMMIT, problems[0])

    def test_missing_git_commit_is_refused(self):
        (next(self.site.glob('*.dist-info')) / 'direct_url.json').write_text('{"url": "file:///x", "dir_info": {}}')
        write_record(self.site)
        self.assertTrue(any('commit' in p for p in self.problems()))

    def test_wrong_version_is_refused(self):
        self.lock['package_version'] = '9.9.9'
        self.assertTrue(any('9.9.9' in p for p in self.problems()))

    def test_tampered_installed_file_is_refused(self):
        (self.site / 'msf_tools/__init__.py').write_text('VALUE = 2\n')
        problems = self.problems()
        self.assertTrue(problems)
        self.assertTrue(all('msf_tools/__init__.py' in p for p in problems), problems)

    def test_tampered_file_with_matching_record_is_refused(self):
        (self.site / 'msf_tools/__init__.py').write_text('VALUE = 2\n')
        write_record(self.site)
        self.assertTrue(any('msf_tools/__init__.py' in p for p in self.problems()))

    def test_unlocked_extra_module_is_refused(self):
        (self.site / 'msf_tools/extra.py').write_text('')
        self.assertTrue(any('msf_tools/extra.py' in p for p in self.problems()))
        write_record(self.site)
        self.assertTrue(any('msf_tools/extra.py' in p for p in self.problems()))

    def test_deleted_locked_file_is_refused(self):
        (self.site / 'msf_tools/__main__.py').unlink()
        self.assertTrue(any('msf_tools/__main__.py' in p for p in self.problems()))

    def test_lock_update_keeps_the_previous_lock(self):
        lock_path = self.temp / 'tooling.lock.json'
        lock_path.write_text('{"previous": true}\n')
        check.write_lock(distribution(self.site), lock_path)
        self.assertEqual(json.loads(lock_path.read_text()), self.lock)
        self.assertEqual(json.loads((self.temp / 'tooling.lock.previous.json').read_text()), {'previous': True})

    def run_check(self, site):
        marker = self.temp / 'marker'
        env = plain_env()
        env.update(PYTHONPATH=str(site), RCEF_TEST_MARKER=str(marker))
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'check.py')], env=env,
                                capture_output=True, text=True, timeout=30)
        return result, marker.exists()

    def test_check_refuses_wrong_commit_before_any_work(self):
        result, ran = self.run_check(fake_site(self.temp / 'other', OTHER_COMMIT))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(ran, 'msf-tools ran despite the commit mismatch')
        self.assertIn(OTHER_COMMIT, result.stderr)

    def test_package_in_working_directory_cannot_replace_the_verified_one(self):
        foreign = self.temp / 'cwd' / 'msf_tools'
        foreign.mkdir(parents=True)
        (foreign / '__init__.py').write_text('')
        (foreign / '__main__.py').write_text(FAKE_MAIN)
        marker = self.temp / 'marker'
        env = plain_env()
        env['RCEF_TEST_MARKER'] = str(marker)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'check.py')], cwd=foreign.parent, env=env,
                                capture_output=True, text=True, timeout=60)
        self.assertFalse(marker.exists(), 'msf_tools from the working directory ran')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_refuses_tampered_package_before_any_work(self):
        result, ran = self.run_check(self.site)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(ran, 'msf-tools ran despite the file mismatch')
        self.assertIn('msf_tools/__init__.py', result.stderr)


if __name__ == '__main__':
    unittest.main()
