#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the shared pack and its readable RCEF reports."""
from __future__ import annotations
import argparse
import base64
import hashlib
from importlib import metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / 'evidence' / 'tooling.lock.json'
PREVIOUS_LOCK_NAME = 'tooling.lock.previous.json'
DISTRIBUTION = 'msf-tools'
PACKAGE = 'msf_tools'
SOURCE = 'https://github.com/Kjakubzak/msf-tools'


def installed_commit(dist: metadata.Distribution) -> str | None:
    text = dist.read_text('direct_url.json')
    if text is None:
        return None
    return json.loads(text).get('vcs_info', {}).get('commit_id')


def recorded_files(dist: metadata.Distribution) -> dict[str, str]:
    """RECORD hashes, as hex sha256, for the importable package files.

    Only the package directory is locked. The console script, the dist-info
    files and any compiled bytecode differ between installers and interpreters.
    """
    files = {}
    for entry in dist.files or ():
        name = entry.as_posix()
        if not name.startswith(PACKAGE + '/') or name.endswith('.pyc'):
            continue
        if entry.hash is None or entry.hash.mode != 'sha256':
            raise ValueError(f'RECORD has no sha256 hash for {name}')
        digest = base64.urlsafe_b64decode(entry.hash.value + '=' * (-len(entry.hash.value) % 4))
        files[name] = digest.hex()
    return dict(sorted(files.items()))


def lock_for(dist: metadata.Distribution) -> dict:
    commit = installed_commit(dist)
    if not commit:
        raise ValueError(f'{DISTRIBUTION} was not installed from a Git commit (no direct_url.json commit)')
    return {'dependency': DISTRIBUTION, 'source': SOURCE, 'git_commit': commit,
            'package_version': dist.version, 'files': recorded_files(dist)}


def write_lock(dist: metadata.Distribution, path: Path = LOCK) -> None:
    """Record the installed distribution, keeping the current lock for rollback."""
    new = json.dumps(lock_for(dist), indent=2) + '\n'
    if path.exists():
        path.replace(path.with_name(PREVIOUS_LOCK_NAME))
    path.write_text(new, encoding='utf-8')


def verify_installed(lock: dict, dist: metadata.Distribution) -> list[str]:
    """Return every way the installed distribution differs from the lock."""
    problems = []
    commit = installed_commit(dist)
    if commit != lock['git_commit']:
        problems.append(f"installed {DISTRIBUTION} is from commit {commit or '(none recorded)'}, "
                        f"but the lock requires {lock['git_commit']}")
    if dist.version != lock['package_version']:
        problems.append(f"installed {DISTRIBUTION} is version {dist.version}, "
                        f"but the lock requires {lock['package_version']}")
    locked = lock['files']
    try:
        recorded = recorded_files(dist)
    except ValueError as error:
        return problems + [str(error)]
    package = Path(dist.locate_file(PACKAGE))
    on_disk = {f'{PACKAGE}/{p.relative_to(package).as_posix()}' for p in package.rglob('*.py')}
    for name in sorted(set(locked) | set(recorded) | on_disk):
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
    args = parser.parse_args()
    if args.update_lock:
        write_lock(metadata.distribution(DISTRIBUTION))
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
    command = [sys.executable, '-B', '-m', PACKAGE, 'check', str(ROOT),
               '--pack', str(ROOT / 'generated' / 'rcef.pack.json'),
               '--csv', str(ROOT / 'generated' / 'rcef_mapping.csv')]
    if args.write:
        command.append('--write')
    status = subprocess.run(command, check=False).returncode
    if status:
        return status
    reports = [sys.executable, '-B', str(ROOT / 'scripts/export_reports.py'),
               '--root', str(ROOT)]
    if args.write:
        reports.append('--write')
    return subprocess.run(reports, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
