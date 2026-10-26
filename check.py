#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the shared pack and its readable RCEF reports."""
from __future__ import annotations
import argparse
import base64
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / 'evidence' / 'tooling.lock.json'
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


def write_lock(dist: metadata.Distribution) -> None:
    LOCK.write_text(json.dumps(lock_for(dist), indent=2) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate all outputs')
    parser.add_argument('--update-lock', action='store_true',
                        help=f'record the installed {DISTRIBUTION} in {LOCK.relative_to(ROOT)} and exit')
    args = parser.parse_args()
    if args.update_lock:
        write_lock(metadata.distribution(DISTRIBUTION))
        return 0
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
