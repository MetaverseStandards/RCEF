#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the shared pack and its readable RCEF reports."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate all outputs')
    parser.add_argument('--tools-path', type=Path, help='explicit local msf-tools checkout')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    prefix = []
    if args.tools_path:
        package_root = args.tools_path.resolve(strict=True)
        if not (package_root / 'msf_tools' / '__init__.py').is_file():
            parser.error('--tools-path must contain msf_tools/__init__.py')
        # Use an explicit interpreter import path without changing persistent environment.
        prefix = ['-c', 'import runpy,sys;sys.path.insert(0,sys.argv.pop(1));'
                  'sys.argv[0]="msf_tools";runpy.run_module("msf_tools",run_name="__main__")',
                  str(package_root)]
    else:
        prefix = ['-m', 'msf_tools']
    command = [sys.executable, '-B', *prefix, 'check', str(root),
               '--pack', str(root / 'generated' / 'rcef.pack.json'),
               '--csv', str(root / 'generated' / 'rcef_mapping.csv')]
    if args.write:
        command.append('--write')
    status = subprocess.run(command, check=False).returncode
    if status:
        return status
    reports = [sys.executable, '-B', str(root / 'scripts/export_reports.py'),
               '--root', str(root)]
    if args.write:
        reports.append('--write')
    return subprocess.run(reports, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
