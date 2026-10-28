# SPDX-License-Identifier: MIT
"""How RCEF finds and checks its msf-character-tools dependency."""
import base64
from copy import deepcopy
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('rcef_check', ROOT / 'check.py')
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)
LOCKED_COMMIT = json.loads((ROOT / 'evidence/tooling.lock.json').read_text())['git_commit']
OTHER_COMMIT = '0' * 40
PURE = 'py3-none-any'
CP311 = 'cp311-cp311-macosx_11_0_arm64'
CP312 = 'cp312-abi3-macosx_11_0_arm64'
# Running the fake package writes this file, so a test can tell whether check.py
# got as far as starting msf-character-tools.
FAKE_MAIN = 'import os, pathlib\npathlib.Path(os.environ["RCEF_TEST_MARKER"]).write_text("ran")\n'


def plain_env():
    """The caller's environment without any explicit msf-character-tools checkout selection."""
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
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


def fake_site(root, commit, version='0.1.1', tag=PURE, build_info=None, vcs=True):
    """A minimal site-packages holding an msf-character-tools wheel install.

    `commit` goes in direct_url.json (as a Git install records it) unless `vcs`
    is false; `build_info`, if given, is the commit written to _build_info.json.
    """
    site = Path(root) / 'site'
    package = site / 'msf_character_tools'
    info = site / f'msf_character_tools-{version}.dist-info'
    package.mkdir(parents=True)
    info.mkdir()
    (package / '__init__.py').write_text('VALUE = 1\n')
    (package / '__main__.py').write_text(FAKE_MAIN)
    if build_info:
        (package / '_build_info.json').write_text(json.dumps({'version': version, 'commit': build_info}))
    if tag != PURE:
        (package / '_core.so').write_bytes(b'\x7fELF ' + tag.encode())
    (info / 'METADATA').write_text(f'Metadata-Version: 2.1\nName: msf-character-tools\nVersion: {version}\n')
    (info / 'WHEEL').write_text(f'Wheel-Version: 1.0\nRoot-Is-Purelib: {"true" if tag == PURE else "false"}\n'
                                f'Tag: {tag}\n')
    if vcs:
        (info / 'direct_url.json').write_text(json.dumps(
            {'url': 'file:///msf-character-tools', 'vcs_info': {'vcs': 'git', 'commit_id': commit}}))
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
        self.assertEqual(check.verify_installed(lock, metadata.distribution('msf-character-tools')), [])

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
        (self.site / 'msf_character_tools/__init__.py').write_text('VALUE = 2\n')
        problems = self.problems()
        self.assertTrue(problems)
        self.assertTrue(all('msf_character_tools/__init__.py' in p for p in problems), problems)

    def test_tampered_file_with_matching_record_is_refused(self):
        (self.site / 'msf_character_tools/__init__.py').write_text('VALUE = 2\n')
        write_record(self.site)
        self.assertTrue(any('msf_character_tools/__init__.py' in p for p in self.problems()))

    def test_unlocked_extra_module_is_refused(self):
        (self.site / 'msf_character_tools/extra.py').write_text('')
        self.assertTrue(any('msf_character_tools/extra.py' in p for p in self.problems()))
        write_record(self.site)
        self.assertTrue(any('msf_character_tools/extra.py' in p for p in self.problems()))

    def test_deleted_locked_file_is_refused(self):
        (self.site / 'msf_character_tools/__main__.py').unlink()
        self.assertTrue(any('msf_character_tools/__main__.py' in p for p in self.problems()))

    def test_lock_records_every_package_file_under_the_wheel_tag(self):
        site = fake_site(self.temp / 'native', LOCKED_COMMIT, tag=CP311)
        (site / 'msf_character_tools/py.typed').write_text('')
        write_record(site)
        lock = check.lock_for(distribution(site))
        self.assertEqual(list(lock['wheels']), [CP311])
        self.assertEqual(sorted(lock['wheels'][CP311]['files']),
                         ['msf_character_tools/__init__.py', 'msf_character_tools/__main__.py',
                          'msf_character_tools/_core.so', 'msf_character_tools/py.typed'])

    def test_unrecorded_shared_library_is_refused(self):
        (self.site / 'msf_character_tools/_speedups.so').write_bytes(b'\x7fELF')
        self.assertTrue(any('msf_character_tools/_speedups.so' in p for p in self.problems()))
        write_record(self.site)
        self.assertTrue(any('msf_character_tools/_speedups.so' in p for p in self.problems()))

    def test_any_extra_file_is_refused_but_bytecode_caches_are_not(self):
        (self.site / 'msf_character_tools/data.bin').write_bytes(b'x')
        self.assertTrue(any('msf_character_tools/data.bin' in p for p in self.problems()))
        (self.site / 'msf_character_tools/data.bin').unlink()
        (self.site / 'msf_character_tools/__pycache__').mkdir()
        (self.site / 'msf_character_tools/__pycache__/__init__.cpython-312.pyc').write_bytes(b'cache')
        self.assertEqual(self.problems(), [])

    def test_wheel_tag_without_a_lock_entry_is_refused(self):
        site = fake_site(self.temp / 'native', LOCKED_COMMIT, tag=CP311)
        problems = check.verify_installed(self.lock, distribution(site))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(CP311, problems[0])
        self.assertIn(PURE, problems[0])

    def test_one_lock_serves_each_tag_with_its_own_files(self):
        lock_path = self.temp / 'tooling.lock.json'
        sites = {tag: fake_site(self.temp / tag, LOCKED_COMMIT, tag=tag) for tag in (CP311, CP312)}
        for site in sites.values():
            check.write_lock(distribution(site), lock_path)
        lock = json.loads(lock_path.read_text())
        self.assertEqual(sorted(lock['wheels']), [CP311, CP312])
        self.assertFalse((self.temp / 'tooling.lock.previous.json').exists(), 'adding a tag is not a new release')
        for site in sites.values():
            self.assertEqual(check.verify_installed(lock, distribution(site)), [])
        # The 3.12 library is not acceptable in the 3.11 install, even with a matching RECORD.
        core = 'msf_character_tools/_core.so'
        (sites[CP311] / core).write_bytes((sites[CP312] / core).read_bytes())
        write_record(sites[CP311])
        self.assertTrue(any(core in p for p in check.verify_installed(lock, distribution(sites[CP311]))))

    def test_lock_for_a_new_commit_drops_the_other_tags(self):
        lock_path = self.temp / 'tooling.lock.json'
        check.write_lock(distribution(fake_site(self.temp / 'a', LOCKED_COMMIT, tag=CP311)), lock_path)
        check.write_lock(distribution(fake_site(self.temp / 'b', OTHER_COMMIT, tag=CP312)), lock_path)
        lock = json.loads(lock_path.read_text())
        self.assertEqual((lock['git_commit'], sorted(lock['wheels'])), (OTHER_COMMIT, [CP312]))

    def test_build_info_commit_is_the_source_commit_when_present(self):
        site = fake_site(self.temp / 'built', None, build_info=OTHER_COMMIT, vcs=False)
        self.assertEqual(check.lock_for(distribution(site))['git_commit'], OTHER_COMMIT)
        problems = check.verify_installed(self.lock, distribution(site))
        self.assertTrue(any(OTHER_COMMIT in p for p in problems), problems)
        plain = fake_site(self.temp / 'index', None, build_info=LOCKED_COMMIT, vcs=False)
        lock = check.lock_for(distribution(plain))
        self.assertEqual(lock['git_commit'], LOCKED_COMMIT)
        self.assertEqual(check.verify_installed(lock, distribution(plain)), [])

    def test_build_info_and_git_commits_that_disagree_are_refused(self):
        site = fake_site(self.temp / 'both', OTHER_COMMIT, build_info=LOCKED_COMMIT)
        lock = deepcopy(self.lock)
        lock['wheels'][PURE]['files'] = check.recorded_files(distribution(site))
        problems = check.verify_installed(lock, distribution(site))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(OTHER_COMMIT, problems[0])
        self.assertIn('_build_info.json', problems[0])
        with self.assertRaises(ValueError):
            check.lock_for(distribution(site))

    def test_wheel_hash_is_recorded_and_checked_when_the_installer_knows_it(self):
        info = next(self.site.glob('*.dist-info'))
        wheel = 'a' * 64
        (info / 'direct_url.json').write_text(json.dumps({'url': 'file:///w.whl', 'archive_info': {
            'hashes': {'sha256': wheel}}}))
        (self.site / 'msf_character_tools/_build_info.json').write_text(
            json.dumps({'version': '0.1.1', 'commit': LOCKED_COMMIT}))
        write_record(self.site)
        lock = check.lock_for(distribution(self.site))
        self.assertEqual(lock['wheels'][PURE]['sha256'], wheel)
        self.assertEqual(self.lock['wheels'][PURE]['sha256'], None)
        lock['wheels'][PURE]['sha256'] = 'b' * 64
        self.assertTrue(any('b' * 64 in p for p in check.verify_installed(lock, distribution(self.site))))

    def test_lock_records_the_installed_wheel_files_hash_only_if_it_holds_the_same_files(self):
        wheel = self.temp / 'msf_character_tools-0.1.1-py3-none-any.whl'
        with zipfile.ZipFile(wheel, 'w') as archive:
            for path in sorted(self.site.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(self.site).as_posix())
        lock = check.lock_for(distribution(self.site), wheel)
        self.assertEqual(lock['wheels'][PURE]['sha256'], hashlib.sha256(wheel.read_bytes()).hexdigest())
        (self.site / 'msf_character_tools/__init__.py').write_text('VALUE = 2\n')
        write_record(self.site)
        with self.assertRaises(ValueError):
            check.lock_for(distribution(self.site), wheel)

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
        self.assertFalse(ran, 'msf-character-tools ran despite the commit mismatch')
        self.assertIn(OTHER_COMMIT, result.stderr)

    def test_package_in_working_directory_cannot_replace_the_verified_one(self):
        foreign = self.temp / 'cwd' / 'msf_character_tools'
        foreign.mkdir(parents=True)
        (foreign / '__init__.py').write_text('')
        (foreign / '__main__.py').write_text(FAKE_MAIN)
        marker = self.temp / 'marker'
        env = plain_env()
        env['RCEF_TEST_MARKER'] = str(marker)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'check.py')], cwd=foreign.parent, env=env,
                                capture_output=True, text=True, timeout=60)
        self.assertFalse(marker.exists(), 'msf_character_tools from the working directory ran')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_refuses_tampered_package_before_any_work(self):
        # A version and tag the real lock has, so check.py gets as far as comparing files.
        lock = json.loads(check.LOCK.read_text())
        site = fake_site(self.temp / 'locked-tag', LOCKED_COMMIT, version=lock['package_version'],
                         tag=next(iter(lock['wheels'])))
        result, ran = self.run_check(site)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(ran, 'msf-character-tools ran despite the file mismatch')
        self.assertIn('msf_character_tools/__init__.py', result.stderr)


if __name__ == '__main__':
    unittest.main()
