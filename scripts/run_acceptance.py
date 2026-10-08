#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run complete RCEF qualification with pinned required methods and native skips."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECURSIVE_GATES = {'test_gate.py', 'test_qualification_gate.py'}


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


class CoverageResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed = []

    def startTest(self, test):
        self.executed.append(test.id())
        super().startTest(test)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools-path', type=Path, default=os.environ.get('MSF_TOOLS_PATH'))
    parser.add_argument('--native-path', type=Path, default=os.environ.get('MSF_NATIVE_PATH'))
    parser.add_argument('--native-sha256', default=os.environ.get('MSF_NATIVE_SHA256'))
    parser.add_argument('--require-native', action='store_true', default=os.environ.get('RCEF_REQUIRE_NATIVE') == '1')
    parser.add_argument('--qualification-only', action='store_true',
                        help='run the nonrecursive qualification suites inside copied gate controls')
    args = parser.parse_args()
    if args.tools_path is None:
        parser.error('select --tools-path or MSF_TOOLS_PATH')
    tools = args.tools_path.resolve(strict=True)
    if not (tools / 'msf_tools/__init__.py').is_file():
        parser.error('tools path must contain msf_tools/__init__.py')
    os.environ['MSF_TOOLS_PATH'] = str(tools)
    sys.path.insert(0, str(tools))
    msf = importlib.import_module('msf_tools')
    if Path(msf.__file__).resolve().parent.parent != tools:
        parser.error(f'unexpected shared import origin: {msf.__file__}')
    required_native = args.require_native or args.native_path is not None
    native_origin = None
    native_hash = None
    if required_native:
        if args.native_path is None:
            parser.error('required native qualification needs --native-path or MSF_NATIVE_PATH')
        if args.native_sha256 is None or not re.fullmatch('[0-9a-f]{64}', args.native_sha256):
            parser.error('configured native qualification needs its accepted --native-sha256 or MSF_NATIVE_SHA256')
        native_path = args.native_path.resolve(strict=True)
        os.environ['MSF_NATIVE_PATH'] = str(native_path)
        os.environ['RCEF_REQUIRE_NATIVE'] = '1'
        os.environ['MSF_NATIVE_SHA256'] = args.native_sha256
        sys.path.insert(0, str(native_path))
        native = importlib.import_module('_msf_native')
        native_origin = Path(native.__file__).resolve()
        if native_origin.parent != native_path:
            parser.error(f'unexpected native import origin: {native_origin}')
        native_hash = hashlib.sha256(native_origin.read_bytes()).hexdigest()
        if native_hash != args.native_sha256:
            parser.error(f'native artifact digest differs: {native_origin}')
    manifest = json.loads((ROOT / 'scripts/acceptance_cases.json').read_text())
    required = {method for file, methods in manifest['required_methods'].items()
                for method in methods
                if not args.qualification_only or file not in RECURSIVE_GATES}
    discovered_suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
    selected = [test for test in cases(discovered_suite)
                if not args.qualification_only or test.id().split('.')[0] + '.py' not in RECURSIVE_GATES]
    discovered = Counter(test.id() for test in selected)
    missing = sorted(required - discovered.keys())
    duplicates = sorted(method for method, count in discovered.items() if count != 1)
    if missing or duplicates:
        print(json.dumps({'qualification': 'REFUSE', 'missing_required_methods': missing,
                          'duplicate_methods': duplicates}, sort_keys=True), flush=True)
        return 1
    result = unittest.TextTestRunner(verbosity=2, resultclass=CoverageResult).run(unittest.TestSuite(selected))
    unexecuted = sorted(required - set(result.executed))
    admitted = result.wasSuccessful() and not unexecuted and (not required_native or not result.skipped)
    print(json.dumps({'qualification': 'PASS' if admitted else 'REFUSE',
                      'interpreter': sys.executable, 'tools_origin': msf.__file__,
                      'native_origin': str(native_origin) if native_origin else None,
                      'native_sha256': native_hash, 'native_required': required_native,
                      'native_qualified': required_native and admitted,
                      'tests_run': result.testsRun, 'required_methods': sorted(required),
                      'executed_methods': result.executed, 'unexecuted_required_methods': unexecuted,
                      'skips': [(test.id(), reason) for test, reason in result.skipped],
                      'failures': len(result.failures), 'errors': len(result.errors)}, sort_keys=True), flush=True)
    return 0 if admitted else 1


if __name__ == '__main__':
    raise SystemExit(main())
