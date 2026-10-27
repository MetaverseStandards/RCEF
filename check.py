#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the shared pack and its readable RCEF reports."""
from __future__ import annotations
import argparse
import base64
import csv
import hashlib
from importlib import metadata
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / 'evidence' / 'tooling.lock.json'
PREVIOUS_LOCK_NAME = 'tooling.lock.previous.json'
DISTRIBUTION = 'msf-tools'
PACKAGE = 'msf_tools'
SOURCE = 'https://github.com/Kjakubzak/msf-tools'


LOCK_VERSION = 2
BUILD_INFO = f'{PACKAGE}/_build_info.json'


def direct_url(dist: metadata.Distribution) -> dict:
    text = dist.read_text('direct_url.json')
    return json.loads(text) if text else {}


def installed_commit(dist: metadata.Distribution) -> str | None:
    """The source commit: from the package's own build record, else from a Git install's direct_url."""
    build = Path(dist.locate_file(BUILD_INFO))
    if build.is_file():
        return json.loads(build.read_text(encoding='utf-8')).get('commit')
    return direct_url(dist).get('vcs_info', {}).get('commit_id')


def installed_tags(dist: metadata.Distribution) -> list[str]:
    """The wheel tags in the install's WHEEL file (py3-none-any, cp311-cp311-..., cp312-abi3-...)."""
    text = dist.read_text('WHEEL') or ''
    return [line.split(':', 1)[1].strip() for line in text.splitlines() if line.startswith('Tag:')]


def wheel_sha256(dist: metadata.Distribution) -> str | None:
    """The installed wheel's sha256, when the installer recorded one (installs from a wheel file)."""
    info = direct_url(dist).get('archive_info', {})
    value = info.get('hashes', {}).get('sha256')
    if value is None and info.get('hash', '').startswith('sha256='):
        value = info['hash'][len('sha256='):]
    return value


def cached(name: str) -> bool:
    return '__pycache__' in name.split('/')


def recorded_files(dist: metadata.Distribution) -> dict[str, str]:
    """RECORD hashes, as hex sha256, for every file in the package directory.

    The console script, the dist-info files and bytecode caches differ between
    installers and interpreters, so they are not locked.
    """
    files = {}
    for entry in dist.files or ():
        name = entry.as_posix()
        if not name.startswith(PACKAGE + '/') or cached(name):
            continue
        if entry.hash is None or entry.hash.mode != 'sha256':
            raise ValueError(f'RECORD has no sha256 hash for {name}')
        digest = base64.urlsafe_b64decode(entry.hash.value + '=' * (-len(entry.hash.value) % 4))
        files[name] = digest.hex()
    return dict(sorted(files.items()))


def files_on_disk(dist: metadata.Distribution) -> set[str]:
    """Every file under the installed package directory except bytecode caches, whatever its type."""
    package = Path(dist.locate_file(PACKAGE))
    names = {f'{PACKAGE}/{p.relative_to(package).as_posix()}' for p in package.rglob('*') if p.is_file()}
    return {name for name in names if not cached(name)}


def wheel_file_sha256(dist: metadata.Distribution, wheel: Path) -> str:
    """The sha256 of the wheel file `dist` was installed from, after checking that it holds the same package files."""
    with zipfile.ZipFile(wheel) as archive:
        record = next((n for n in archive.namelist() if n.endswith('.dist-info/RECORD')), None)
        if record is None:
            raise ValueError(f'{wheel} has no RECORD')
        files = {}
        for row in csv.reader(io.StringIO(archive.read(record).decode('utf-8'))):
            if row and row[0].startswith(PACKAGE + '/') and not cached(row[0]):
                mode, _, value = row[1].partition('=')
                if mode != 'sha256':
                    raise ValueError(f'{wheel} RECORD has no sha256 hash for {row[0]}')
                files[row[0]] = base64.urlsafe_b64decode(value + '=' * (-len(value) % 4)).hex()
    if files != recorded_files(dist):
        raise ValueError(f'{wheel} does not hold the installed {DISTRIBUTION} files')
    return hashlib.sha256(wheel.read_bytes()).hexdigest()


def lock_for(dist: metadata.Distribution, wheel: Path | None = None) -> dict:
    commit = installed_commit(dist)
    if not commit:
        raise ValueError(f'{DISTRIBUTION} records no source commit (no {BUILD_INFO} and no Git direct_url.json)')
    tags = installed_tags(dist)
    if len(tags) != 1:
        raise ValueError(f'{DISTRIBUTION} should have exactly one wheel tag, not {tags}')
    return {'lock_version': LOCK_VERSION, 'dependency': DISTRIBUTION, 'source': SOURCE, 'git_commit': commit,
            'package_version': dist.version,
            'wheels': {tags[0]: {'sha256': wheel_file_sha256(dist, wheel) if wheel else wheel_sha256(dist),
                                 'files': recorded_files(dist)}}}


def write_lock(dist: metadata.Distribution, path: Path = LOCK, wheel: Path | None = None) -> None:
    """Record the installed wheel under its tag, keeping the current lock for rollback.

    Entries for other tags are kept if they are the same commit and version, so
    running this from each interpreter builds one lock that serves them all;
    the rollback copy is then left alone, so it stays the lock for the last release.
    """
    lock = lock_for(dist, wheel)
    if path.exists():
        old = json.loads(path.read_text(encoding='utf-8'))
        if (old.get('lock_version'), old.get('git_commit'), old.get('package_version')) == \
                (LOCK_VERSION, lock['git_commit'], lock['package_version']):
            lock['wheels'] = dict(sorted({**old['wheels'], **lock['wheels']}.items()))
        else:
            path.replace(path.with_name(PREVIOUS_LOCK_NAME))
    path.write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')


def verify_installed(lock: dict, dist: metadata.Distribution) -> list[str]:
    """Return every way the installed distribution differs from the lock."""
    if lock.get('lock_version') != LOCK_VERSION:
        return [f'the lock is format {lock.get("lock_version", 1)}, but this check.py reads format {LOCK_VERSION}']
    problems = []
    commit = installed_commit(dist)
    if commit != lock['git_commit']:
        problems.append(f"installed {DISTRIBUTION} is from commit {commit or '(none recorded)'}, "
                        f"but the lock requires {lock['git_commit']}")
    if dist.version != lock['package_version']:
        problems.append(f"installed {DISTRIBUTION} is version {dist.version}, "
                        f"but the lock requires {lock['package_version']}")
    tags = [tag for tag in installed_tags(dist) if tag in lock['wheels']]
    if len(tags) != 1:
        return problems + [f"installed {DISTRIBUTION} has wheel tag(s) {', '.join(installed_tags(dist)) or '(none)'}, "
                           f"but the lock has entries only for {', '.join(lock['wheels'])}"]
    entry = lock['wheels'][tags[0]]
    sha = wheel_sha256(dist)
    if entry.get('sha256') and sha and sha != entry['sha256']:
        problems.append(f'installed {DISTRIBUTION} came from a wheel with sha256 {sha}, '
                        f"but the lock requires {entry['sha256']}")
    locked = entry['files']
    try:
        recorded = recorded_files(dist)
    except ValueError as error:
        return problems + [str(error)]
    for name in sorted(set(locked) | set(recorded) | files_on_disk(dist)):
        if name not in locked:
            problems.append(f'{name} is installed but not in the lock')
            continue
        path = Path(dist.locate_file(name))
        if not path.is_file():
            problems.append(f'{name} is in the lock but not installed')
        elif name not in recorded:
            problems.append(f'{name} is installed but not listed in RECORD')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != recorded[name]:
            problems.append(f'{name} has been modified since installation (it no longer matches RECORD)')
        elif recorded[name] != locked[name]:
            problems.append(f'{name} differs from the locked version')
    return problems


def verify_environment() -> list[str]:
    """Check that the msf_tools this interpreter imports is the locked distribution."""
    try:
        dist = metadata.distribution(DISTRIBUTION)
    except metadata.PackageNotFoundError:
        return [f'{DISTRIBUTION} is not installed for {sys.executable}']
    problems = verify_installed(json.loads(LOCK.read_text(encoding='utf-8')), dist)
    spec = importlib.util.find_spec(PACKAGE)
    expected = Path(dist.locate_file(f'{PACKAGE}/__init__.py')).resolve()
    if spec is None or spec.origin is None or Path(spec.origin).resolve() != expected:
        origin = spec.origin if spec else None
        problems.append(f'{PACKAGE} imports from {origin}, not from the installed distribution at {expected}')
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate all outputs')
    parser.add_argument('--update-lock', action='store_true',
                        help=f'record the installed {DISTRIBUTION} in {LOCK.relative_to(ROOT)}, keep the old lock '
                             f'as {PREVIOUS_LOCK_NAME}, and exit')
    parser.add_argument('--wheel', type=Path,
                        help='with --update-lock: the wheel file just installed, whose sha256 the lock records '
                             'for --require-hashes installs')
    args = parser.parse_args()
    if args.update_lock:
        write_lock(metadata.distribution(DISTRIBUTION), wheel=args.wheel)
        return 0
    problems = verify_environment()
    if problems:
        print(f'Refusing to check: the installed {DISTRIBUTION} does not match '
              f'{LOCK.relative_to(ROOT)}.', file=sys.stderr)
        for problem in problems:
            print(f'  - {problem}', file=sys.stderr)
        commit = json.loads(LOCK.read_text(encoding='utf-8'))['git_commit']
        print(f'Install {DISTRIBUTION} at commit {commit}. To adopt a reviewed new version '
              'instead, install it and run check.py --update-lock.', file=sys.stderr)
        return 2
    # -P keeps the caller's working directory off the import path, so the
    # subprocess imports the msf_tools verified above. An empty bytecode cache
    # makes it run the verified source rather than any cached .pyc files.
    with tempfile.TemporaryDirectory(prefix='rcef-pycache-') as cache:
        command = [sys.executable, '-B', '-P', '-X', f'pycache_prefix={cache}', '-m', PACKAGE,
                   'check', str(ROOT), '--pack', str(ROOT / 'generated' / 'rcef.pack.json'),
                   '--csv', str(ROOT / 'generated' / 'rcef_mapping.csv')]
        if args.write:
            command.append('--write')
        status = subprocess.run(command, check=False, cwd=ROOT).returncode
    if status:
        return status
    reports = [sys.executable, '-B', '-P', str(ROOT / 'scripts/export_reports.py'),
               '--root', str(ROOT)]
    if args.write:
        reports.append('--write')
    return subprocess.run(reports, check=False, cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
