#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run complete RCEF qualification with pinned required methods and native skips."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import sys
import stat
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECURSIVE_GATES = {'test_gate.py', 'test_qualification_gate.py'}
ORIGINAL_MANIFEST_SHA256 = 'a94f545ab96a23a2f006396bda7ccb4e4355773c31111929295a8f58ccc28e1f'
SKIP_CONTRACT_SHA256 = '055cf17f5d8e7a86ddca5a106b72cde396659d748ee2c0610ee2254c45c54cea'

R2_BINDINGS_SHA256 = 'cf1ae80636de31ce6ad178f8b25a1ad52e5fdbfc6f9bfffbbe398b9f2e2071b8'


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f'duplicate metadata key: {key}')
        value[key] = item
    return value


def _read_r2_bindings(path):
    """Read a bounded regular metadata file and verify its named endpoints."""
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or stat.S_IMODE(before.st_mode) != 0o644:
            raise ValueError('R2 source bindings must be a regular 0644 file')
        if not 0 < before.st_size <= 16 * 1024 * 1024:
            raise ValueError('R2 source bindings exceed bounded payload size')
        raw = bytearray()
        remaining = before.st_size
        while remaining:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            if not chunk:
                raise ValueError('R2 source bindings ended during consumption')
            raw.extend(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise ValueError('R2 source bindings grew during consumption')
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size',
                  'st_mtime_ns', 'st_ctime_ns')
        signature = tuple(getattr(before, field) for field in fields)
        after = os.fstat(fd)
        if signature != tuple(getattr(after, field) for field in fields):
            raise ValueError('R2 source bindings changed during consumption')
        current_fd = os.open(path, flags)
        try:
            current = os.fstat(current_fd)
            if signature != tuple(getattr(current, field) for field in fields):
                raise ValueError('R2 source bindings named file changed')
        finally:
            os.close(current_fd)
        return raw
    finally:
        os.close(fd)


def r2_source_contract(contract):
    """Consume the independently pinned sidecar without semantic overrides."""
    path = ROOT / 'evidence/input-contracts/qualification-skip.r2-bindings.json'
    raw = _read_r2_bindings(path)
    if hashlib.sha256(raw).hexdigest() != R2_BINDINGS_SHA256:
        raise ValueError('R2 source bindings fingerprint differs')
    sidecar = json.loads(raw, object_pairs_hook=unique_object)
    keys = {'schema_version', 'original_manifest_sha256', 'original_skip_contract_sha256',
            'source_bindings', 'locators'}
    if (not isinstance(sidecar, dict) or set(sidecar) != keys
            or type(sidecar['schema_version']) is not int or sidecar['schema_version'] != 1
            or sidecar['original_manifest_sha256'] != ORIGINAL_MANIFEST_SHA256
            or sidecar['original_skip_contract_sha256'] != SKIP_CONTRACT_SHA256):
        raise ValueError('unsupported R2 source binding schema or original references')
    sources = sidecar['source_bindings']
    if not isinstance(sources, list) or len(sources) != 1:
        raise ValueError('R2 bindings require exactly one qualification source')
    source = sources[0]
    relative = 'tests/test_qualification_gate.py'
    if (not isinstance(source, dict) or set(source) != {'file', 'type', 'mode', 'bytes', 'sha256'}
            or source['file'] != relative or source['type'] != 'regular'
            or type(source['mode']) is not int or source['mode'] != 0o644
            or type(source['bytes']) is not int or not 0 < source['bytes'] <= 16 * 1024 * 1024
            or not isinstance(source['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', source['sha256'])):
        raise ValueError('unsupported R2 source override')
    original_entries = [entry for entry in contract['exact_source_bound_skips']
                        if entry['source']['file'] == relative]
    locators = sidecar['locators']
    if (len(original_entries) != 2 or not isinstance(locators, list) or len(locators) != 2):
        raise ValueError('R2 bindings require exactly the original two control locators')
    for locator, entry in zip(locators, original_entries):
        if (not isinstance(locator, dict) or set(locator) != {'id', 'decorator_line', 'method_line'}
                or locator['id'] != entry['id']
                or type(locator['decorator_line']) is not int or locator['decorator_line'] <= 0
                or type(locator['method_line']) is not int
                or locator['method_line'] != locator['decorator_line'] + 1):
            raise ValueError('unsupported R2 locator override')
    # The consumed historical object remains intact. Only this in-memory view
    # replaces qualification-source bytes/type/mode and the two source locators.
    effective = dict(contract)
    effective['source_bindings'] = []
    for binding in contract['source_bindings']:
        updated = dict(binding)
        if str(Path(binding['path']).relative_to(contract['source_root'])) == relative:
            updated.update(bytes=source['bytes'], sha256=source['sha256'],
                           raw_type=source['type'], raw_mode=oct(source['mode']),
                           followed_mode=oct(source['mode']))
        effective['source_bindings'].append(updated)
    successors = {locator['id']: locator for locator in locators}
    effective['exact_source_bound_skips'] = []
    for entry in contract['exact_source_bound_skips']:
        updated = dict(entry)
        if entry['id'] in successors:
            updated['source'] = dict(entry['source'],
                decorator_line=successors[entry['id']]['decorator_line'],
                method_line=successors[entry['id']]['method_line'])
        effective['exact_source_bound_skips'].append(updated)
    return effective


def input_contracts(subset):
    # Each original buffer is consumed once. Historical runner/source-root
    # bindings are provenance; only the original data fingerprints are pins.
    manifest_raw = (ROOT / 'scripts/acceptance_cases.json').read_bytes()
    skip_raw = (ROOT / 'evidence/input-contracts/qualification-skip.contract.json').read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != ORIGINAL_MANIFEST_SHA256:
        raise ValueError('original acceptance manifest fingerprint differs')
    if hashlib.sha256(skip_raw).hexdigest() != SKIP_CONTRACT_SHA256:
        raise ValueError('qualification skip contract fingerprint differs')
    manifest = json.loads(manifest_raw, object_pairs_hook=unique_object)
    contract = json.loads(skip_raw, object_pairs_hook=unique_object)
    full = contract['modes']['full50parent11']
    selected = contract['modes']['original46subset9']
    methods = manifest['required_methods']
    originals = [method for group in methods.values() for method in group]
    subset_methods = {file: group for file, group in methods.items() if file not in RECURSIVE_GATES}
    if (len(methods) != 6 or len(originals) != 50 or len(set(originals)) != 50
            or len(manifest['groups']) != 21 or manifest['groups'] != contract['original_groups']
            or methods != full['required_methods'] or subset_methods != selected['required_methods']
            or sum(map(len, subset_methods.values())) != 46
            or full['eligible_skip_count'] != 11 or len(set(full['eligible_skip_ids'])) != 11
            or selected['eligible_skip_count'] != 9 or len(set(selected['eligible_skip_ids'])) != 9
            or contract['modes']['configured0']['eligible_skip_ids'] != []):
        raise ValueError('original 50/46 methods, 21 groups or skip allowlists differ')
    mode = selected if subset else full
    required = {method for group in mode['required_methods'].values() for method in group}
    return required, r2_source_contract(contract), set(mode['eligible_skip_ids'])


def source_bound_skip(test, reason, contract, eligible, source_cache):
    identifier = test.id()
    if identifier not in eligible:
        return False
    entries = [entry for entry in contract['exact_source_bound_skips'] if entry['id'] == identifier]
    if len(entries) != 1 or entries[0]['reason'] != reason:
        return False
    entry = entries[0]
    relative = entry['source']['file']
    if relative not in source_cache:
        # Rebase the relevant source to a copied ROOT. Do this only for an
        # unconfigured skip, so configured controls and additions still run.
        bindings = [binding for binding in contract['source_bindings']
                    if str(Path(binding['path']).relative_to(contract['source_root'])) == relative]
        path = ROOT / relative
        raw = path.read_bytes()
        if (len(bindings) != 1 or not stat.S_ISREG(path.lstat().st_mode)
                or oct(stat.S_IMODE(path.lstat().st_mode)) != bindings[0]['raw_mode']
                or len(raw) != bindings[0]['bytes']
                or hashlib.sha256(raw).hexdigest() != bindings[0]['sha256']):
            source_cache[relative] = None
        else:
            source_cache[relative] = ast.parse(raw, filename=str(path))
    tree = source_cache[relative]
    if tree is None:
        return False
    module_name, class_name, method_name = identifier.split('.')
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        return False
    cls = classes[0]
    if 'scope' in entry['source']:
        decorators = cls.decorator_list
        # The unchanged module initializes native to None and guards its only
        # native import with NATIVE_PATH. Check the configuration and live
        # module too, when discovery has imported it; metadata text is not eval.
        initializers = [node for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'native' for target in node.targets)]
        if (len(initializers) != 1 or not isinstance(initializers[0].value, ast.Constant)
                or initializers[0].value.value is not None or os.environ.get('MSF_NATIVE_PATH')
                or os.environ.get('RCEF_REQUIRE_NATIVE') == '1'):
            return False
        module = sys.modules.get(module_name)
        if module is not None and (getattr(module, 'native', object()) is not None
                or getattr(module, 'NATIVE_PATH', None)
                or Path(module.__file__).resolve() != (ROOT / relative).resolve()):
            return False
    else:
        methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name]
        if len(methods) != 1 or methods[0].lineno != entry['source']['method_line']:
            return False
        decorators = methods[0].decorator_list
        if os.environ.get('MSF_NATIVE_PATH'):
            return False
    condition = ast.dump(ast.parse(entry['source_condition'], mode='eval').body)
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
               and isinstance(node.func.value, ast.Name) and node.func.value.id == 'unittest'
               and node.func.attr == 'skipUnless' and node.lineno == entry['source']['decorator_line']
               and len(node.args) == 2 and ast.dump(node.args[0]) == condition
               and isinstance(node.args[1], ast.Constant) and node.args[1].value == reason
               for node in decorators)


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
        self.started = []
        self.stopped = []
        self.terminals = []
        self.lifecycle = {}
        self.first_callback_fault = None
        self.first_callback_traceback = None
        self.callback_faults = []

    def remember_fault(self, error):
        # First custody precedes optional multi-fault recording. If recording
        # itself raises, main can still resolve the original object/traceback.
        if self.first_callback_fault is None:
            self.first_callback_fault = error
            self.first_callback_traceback = error.__traceback__
        if not any(error is item[0] for item in self.callback_faults):
            self.callback_faults.append((error, error.__traceback__))

    def rethrow_first(self, later=None):
        first, original_traceback = self.first_callback_fault, self.first_callback_traceback
        secondary = later if later is not None and later is not first else next(
            (error for error, _ in self.callback_faults[1:] if error is not first), None)
        if secondary is not None:
            raise first.with_traceback(original_traceback) from secondary
        raise first.with_traceback(original_traceback)

    def callback(self, name, *args, record=None, before=None):
        # Retain the first object before another callback/finally can replace
        # it. A record fault does not prevent attempting the delegated callback.
        local_fault = None
        if before is not None:
            try:
                before()
            except BaseException as error:
                self.remember_fault(error)
                local_fault = error
        try:
            value = getattr(super(), name)(*args)
        except BaseException as error:
            self.remember_fault(error)
            if local_fault is None:
                local_fault = error
        else:
            if record is not None:
                try:
                    record()
                except BaseException as error:
                    self.remember_fault(error)
                    if local_fault is None:
                        local_fault = error
        if local_fault is not None:
            raise local_fault
        return value

    def record_event(self, name, test):
        # Only a normally returning delegate records a completed event. Keep
        # every failure terminal for diagnostics, including repeated cleanup
        # errors; malformed order is refused after execution, without raising.
        identifier = test.id()
        if name == 'startTest':
            self.started.append(identifier)
        elif name == 'stopTest':
            self.stopped.append(identifier)
        else:
            self.terminals.append((identifier, name))
        self.lifecycle.setdefault(identifier, []).append(name)

    def startTest(self, test):
        return self.callback('startTest', test,
                             before=lambda: self.executed.append(test.id()),
                             record=lambda: self.record_event('startTest', test))

    def stopTest(self, test):
        return self.callback('stopTest', test, record=lambda: self.record_event('stopTest', test))

    def startTestRun(self):
        return self.callback('startTestRun')

    def stopTestRun(self):
        return self.callback('stopTestRun')

    def terminal(self, name, test, *args):
        return self.callback(name, test, *args, record=lambda: self.record_event(name, test))

    def addSuccess(self, test):
        return self.terminal('addSuccess', test)

    def addSkip(self, test, reason):
        return self.terminal('addSkip', test, reason)

    def addFailure(self, test, err):
        return self.terminal('addFailure', test, err)

    def addError(self, test, err):
        return self.terminal('addError', test, err)

    def addExpectedFailure(self, test, err):
        return self.terminal('addExpectedFailure', test, err)

    def addUnexpectedSuccess(self, test):
        return self.terminal('addUnexpectedSuccess', test)

    def addSubTest(self, test, subtest, err):
        # Healthy subtests are not parent terminals. Delegate failures must
        # survive unittest's outcome handling even if it converts them to errors.
        return self.callback('addSubTest', test, subtest, err)

    def addDuration(self, test, elapsed):
        return self.callback('addDuration', test, elapsed)

    def incomplete(self, selected):
        starts, stops = Counter(self.started), Counter(self.stopped)
        terminals = Counter(identifier for identifier, _ in self.terminals)
        expected = Counter(selected)
        identifiers = expected.keys() | starts.keys() | stops.keys() | terminals.keys() | self.lifecycle.keys()
        incomplete = []
        for identifier in identifiers:
            events = self.lifecycle.get(identifier, [])
            if (expected[identifier] != 1 or starts[identifier] != 1
                    or stops[identifier] != 1 or terminals[identifier] != 1
                    or len(events) != 3 or events[0] != 'startTest' or events[2] != 'stopTest'
                    or events[1] not in {'addSuccess', 'addSkip', 'addFailure', 'addError',
                                         'addExpectedFailure', 'addUnexpectedSuccess'}):
                incomplete.append(identifier)
        return sorted(incomplete)


def run_observed(selected):
    """Execute stock unittest with R1 first-fault custody across finally paths."""
    result = None
    def result_factory(*arguments, **keywords):
        nonlocal result
        result = CoverageResult(*arguments, **keywords)
        return result
    try:
        result = unittest.TextTestRunner(verbosity=2, resultclass=result_factory).run(unittest.TestSuite(selected))
    except BaseException as later:
        if result is not None and result.first_callback_fault is not None:
            result.rethrow_first(later)
        raise
    if result.first_callback_fault is not None:
        result.rethrow_first()
    return result


def admit_observed(result, selected_ids, allow_skip):
    """Admit complete callbacks and counters for every selected original/addition."""
    incomplete = result.incomplete(selected_ids)
    try:
        skips_admitted = all(allow_skip(test, reason) for test, reason in result.skipped)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError):
        skips_admitted = False
    admitted = (result.wasSuccessful() and not incomplete and skips_admitted
                and result.testsRun == len(selected_ids)
                and not result.expectedFailures and not result.unexpectedSuccesses
                and all(name in {'addSuccess', 'addSkip'} for _, name in result.terminals))
    return admitted, incomplete


def gate_refusal(required, selected_ids, missing, duplicates):
    return {'scope': 'gate-control', 'observation': 'REFUSE',
            'original_required_methods': sorted(required), 'selected_methods': sorted(selected_ids),
            'tests_run': 0, 'executed_methods': [], 'failures': 0, 'errors': 0, 'skips': [],
            'missing_required_methods': missing, 'duplicate_methods': duplicates}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools-path', type=Path, default=os.environ.get('MSF_TOOLS_PATH'))
    parser.add_argument('--native-path', type=Path, default=os.environ.get('MSF_NATIVE_PATH'))
    parser.add_argument('--native-sha256', default=os.environ.get('MSF_NATIVE_SHA256'))
    parser.add_argument('--require-native', action='store_true', default=os.environ.get('RCEF_REQUIRE_NATIVE') == '1')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--qualification-only', action='store_true',
                       help='run the nonrecursive qualification suites inside copied gate controls')
    modes.add_argument('--observe-gate-control', action='store_true',
                       help='observe the original Gate and every gate-file addition; no qualification credit')
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
    gate_required = {'test_gate.Gate.test_published_gates_reject_coherent_wrong_metadata'}
    try:
        required, skip_contract, eligible_skips = input_contracts(args.qualification_only)
        if args.observe_gate_control:
            required = {identifier for identifier in required if identifier.startswith('test_gate.')}
            if required != gate_required:
                raise ValueError('original Gate requirement differs')
            eligible_skips = set()
    except (OSError, ValueError, KeyError, TypeError) as error:
        record = (gate_refusal(gate_required, [], [str(error)], []) if args.observe_gate_control else
                  {'qualification': 'REFUSE', 'missing_required_methods': [str(error)], 'duplicate_methods': []})
        print(json.dumps(record, sort_keys=True), flush=True)
        return 1
    pattern = 'test_gate.py' if args.observe_gate_control else 'test_*.py'
    discovered_suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern)
    selected = [test for test in cases(discovered_suite)
                if not args.qualification_only or test.id().split('.')[0] + '.py' not in RECURSIVE_GATES]
    selected_ids = tuple(test.id() for test in selected)
    discovered = Counter(selected_ids)
    missing = sorted(required - discovered.keys())
    duplicates = sorted(method for method, count in discovered.items() if count != 1)
    if missing or duplicates:
        record = (gate_refusal(required, selected_ids, missing, duplicates) if args.observe_gate_control else
                  {'qualification': 'REFUSE', 'missing_required_methods': missing, 'duplicate_methods': duplicates})
        print(json.dumps(record, sort_keys=True), flush=True)
        return 1
    result = run_observed(selected)
    source_cache = {}
    def allow_skip(test, reason):
        if args.observe_gate_control or required_native:
            return False
        return source_bound_skip(test, reason, skip_contract, eligible_skips, source_cache)
    admitted, incomplete = admit_observed(result, selected_ids, allow_skip)
    unexecuted = sorted(required & set(incomplete))
    if args.observe_gate_control:
        print(json.dumps({'scope': 'gate-control', 'observation': 'PASS' if admitted else 'REFUSE',
                          'original_required_methods': sorted(required), 'selected_methods': sorted(selected_ids),
                          'tests_run': result.testsRun, 'executed_methods': result.executed,
                          'incomplete_methods': incomplete, 'unexecuted_required_methods': unexecuted,
                          'skips': [(test.id(), reason) for test, reason in result.skipped],
                          'failures': len(result.failures), 'errors': len(result.errors)}, sort_keys=True), flush=True)
        return 0 if admitted else 1
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
