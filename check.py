#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check the installed msf-tools and the calibration records, then the shared pack and its readable RCEF reports."""
from __future__ import annotations
import argparse
import base64
import csv
import datetime
import hashlib
from importlib import metadata
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
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


def recorded_commits(dist: metadata.Distribution) -> tuple[str | None, str | None]:
    """The commit in the package's own build record, and the commit a Git install's direct_url names."""
    build = Path(dist.locate_file(BUILD_INFO))
    built = json.loads(build.read_text(encoding='utf-8')).get('commit') if build.is_file() else None
    return built, direct_url(dist).get('vcs_info', {}).get('commit_id')


def commit_conflict(dist: metadata.Distribution) -> str | None:
    built, vcs = recorded_commits(dist)
    if built and vcs and built != vcs:
        return (f'installed {DISTRIBUTION} has {BUILD_INFO} naming commit {built}, '
                f'but its direct_url.json names commit {vcs}')
    return None


def installed_commit(dist: metadata.Distribution) -> str | None:
    """The source commit: from the package's own build record, else from a Git install's direct_url."""
    built, vcs = recorded_commits(dist)
    return built or vcs


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
    if conflict := commit_conflict(dist):
        raise ValueError(conflict)
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
    if conflict := commit_conflict(dist):
        problems.append(conflict)
    elif commit != lock['git_commit']:
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


CALIBRATION = ROOT / 'calibration'
# Records are TOML text, but not named *.toml: msf-tools reads every .toml file
# in the checkout as pack authoring.
RECORD_SUFFIX = '.cal'
RECORD_FORMAT = 'rcef.calibration/1'
SEED_RULE = 'rcef.calibration.seeds/1'
CITATION = 'calibration.'
MIN_CONDITIONS = 20
SHA256 = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'[0-9a-f]{40}')
RECORD_ID = re.compile(r'[a-z0-9][a-z0-9._-]*')
RECORD_FIELDS = {'format': str, 'id': str, 'version': int, 'status': str, 'scope': str, 'method': str,
                 'channels': list, 'reference_rig': str, 'inputs': list, 'renderer': dict, 'code_commit': str,
                 'training': dict, 'held_out': dict, 'evaluation': dict, 'curves': list,
                 'licence': str, 'limitations': list}
# A record without cells is a pre-registration: frozen and in the ledger, with no results yet.
OPTIONAL_FIELDS = {'scan_origin': str, 'cells': list}
SCOPE = 'software-only; not a measurement of any tracker'
SCAN_ORIGIN = 'light-stage scans of real people'
ICT = re.compile(r'\bict\b|identity\d{3}', re.IGNORECASE)
# A limitation shorter than this is a placeholder, not a statement.
MIN_LIMITATION_WORDS, MIN_LIMITATION_CHARS = 5, 30
LEDGER = 'FREEZES'
LEDGER_LINE = re.compile(r'(\S+) v([1-9][0-9]*) (\S+) (\S+)(?: (.*\S))?')


def load_record(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding='utf-8'))


def frozen_sha256(record: dict) -> str:
    """The sha256 of everything in a record except its metrics (cells) and this hash itself.

    The part is serialised as compact, key-sorted JSON, so the hash depends on
    the values, not on how the TOML is laid out.
    """
    frozen = {k: v for k, v in record.items() if k != 'cells'}
    if isinstance(frozen.get('held_out'), dict):
        frozen['held_out'] = {k: v for k, v in frozen['held_out'].items() if k != 'frozen_sha256'}
    text = json.dumps(frozen, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def held_out_seeds(record: dict) -> list[int]:
    """Seed i is the first 8 bytes, big-endian, of sha256('<frozen_sha256>:<i>')."""
    frozen = record['held_out']['frozen_sha256']
    return [int.from_bytes(hashlib.sha256(f'{frozen}:{i}'.encode()).digest()[:8], 'big')
            for i in range(record['held_out']['count'])]


def _number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _text(value) -> bool:
    return isinstance(value, str) and value.strip() != ''


def _fields(table: dict, required: dict, where: str) -> list[str]:
    """Missing, unknown and wrongly typed fields of a table; `required` maps each field to a check and a description."""
    problems = [f'{where}{name} is missing' for name in required if name not in table]
    problems += [f'{where}{name} is not a field of this format' for name in table if name not in required]
    problems += [f'{where}{name} must be {kind}' for name, (ok, kind) in required.items()
                 if name in table and not ok(table[name])]
    return problems


def _hashes(table: dict, names: tuple, where: str) -> list[str]:
    return [f'{where}{name} {table[name]!r} is not a lowercase hex sha256' for name in names
            if isinstance(table.get(name), str) and not SHA256.fullmatch(table[name])]


def record_problems(record: dict, name: str) -> list[str]:
    """Every way a calibration record departs from the format in calibration/README.md."""
    kinds = {str: 'text', list: 'a list', dict: 'a table', int: 'a positive integer'}

    def typed(kind):
        if kind is int:
            return lambda v: type(v) is int and v > 0
        return lambda v: isinstance(v, kind) and (kind is not str or _text(v))
    fields = {k: (typed(t), kinds[t]) for k, t in RECORD_FIELDS.items()}
    problems = _fields({k: v for k, v in record.items() if k not in OPTIONAL_FIELDS}, fields, '')
    problems += [f'{k} must be {kinds[t]}' for k, t in OPTIONAL_FIELDS.items() if k in record and not typed(t)(record[k])]

    def get(key, kind):
        return record.get(key) if isinstance(record.get(key), kind) else None
    if record.get('format') != RECORD_FORMAT:
        problems.append(f'format must be {RECORD_FORMAT}')
    if get('id', str) is not None and (record['id'] != name or not RECORD_ID.fullmatch(record['id'])):
        problems.append(f'id {record["id"]} must be the file name ({name}), in lowercase letters, digits, . _ -')
    if 'status' in record and record['status'] != 'calibrated_software':
        problems.append(f'status {record["status"]} is not allowed: records are calibrated_software '
                        '(calibrated_measured is reserved for physical capture)')
    if 'scope' in record and record['scope'] != SCOPE:
        problems.append(f'scope must be exactly "{SCOPE}"')
    uses_ict = any(ICT.search(text) for text in [str(record.get('reference_rig', ''))]
                   + [str(item.get('name', '')) for item in get('inputs', list) or () if isinstance(item, dict)])
    if uses_ict and not (_text(record.get('scan_origin')) and SCAN_ORIGIN in record['scan_origin']):
        problems.append(f'scan_origin must say that ICT-FaceKit identities come from {SCAN_ORIGIN}, since this '
                        'record uses ICT-FaceKit')
    channels = get('channels', list)
    if channels is not None and (not channels or not all(_text(c) for c in channels)
                                 or len(set(channels)) != len(channels)):
        problems.append('channels must be a non-empty list of distinct signal ids')
    limitations = get('limitations', list)
    if limitations is not None and (not limitations or not all(
            isinstance(x, str) and len(x.strip()) >= MIN_LIMITATION_CHARS and len(x.split()) >= MIN_LIMITATION_WORDS
            for x in limitations)):
        problems.append(f'limitations must be a non-empty list of statements, each at least {MIN_LIMITATION_WORDS} '
                        f'words and {MIN_LIMITATION_CHARS} characters')
    inputs = get('inputs', list)
    if inputs is not None and not inputs:
        problems.append('inputs must list at least one input asset')
    for i, item in enumerate(inputs or ()):
        where = f'inputs[{i}].'
        if not isinstance(item, dict):
            problems.append(f'inputs[{i}] must be a table')
            continue
        problems += _fields(item, {'name': (_text, 'text'), 'sha256': (_text, 'text')}, where)
        problems += _hashes(item, ('sha256',), where)
    renderer = get('renderer', dict)
    if renderer is not None:
        problems += _fields(renderer, {k: (_text, 'text') for k in
                                       ('source_sha256', 'binary_sha256', 'compiler', 'os', 'gpu')}, 'renderer.')
        problems += _hashes(renderer, ('source_sha256', 'binary_sha256'), 'renderer.')
    if get('code_commit', str) is not None and not COMMIT.fullmatch(record['code_commit']):
        problems.append(f'code_commit {record["code_commit"]!r} is not a full lowercase hex Git commit')
    training = get('training', dict)
    if training is not None:
        problems += _fields(training, {'conditions': (lambda v: type(v) is int and v > 0, 'a positive integer'),
                                       'description': (_text, 'text')}, 'training.')
    held_out = get('held_out', dict)
    if held_out is not None:
        problems += _fields(held_out, {'seed_rule': (lambda v: v == SEED_RULE, SEED_RULE),
                                       'count': (lambda v: type(v) is int and v > 0, 'a positive integer'),
                                       'frozen_sha256': (_text, 'text')}, 'held_out.')
        problems += _hashes(held_out, ('frozen_sha256',), 'held_out.')
        try:
            frozen = frozen_sha256(record)
        except (TypeError, ValueError):
            frozen = None
            problems.append('the record holds a value JSON cannot represent (a date, or a non-finite number)')
        if frozen and held_out.get('frozen_sha256') != frozen:
            problems.append(f'held_out.frozen_sha256 is not the hash of the frozen part ({frozen}): everything but '
                            'cells is frozen before the held-out seeds are drawn')
    metric = (lambda v: _number(v) and v >= 0, 'a finite number >= 0')
    evaluation = get('evaluation', dict)
    minimum = None
    if evaluation is not None:
        problems += _fields(evaluation, {
            'min_conditions': (lambda v: type(v) is int and v >= MIN_CONDITIONS, f'an integer >= {MIN_CONDITIONS}'),
            'bounds': (lambda v: isinstance(v, dict), 'a table')}, 'evaluation.')
        if type(evaluation.get('min_conditions')) is int and evaluation['min_conditions'] >= MIN_CONDITIONS:
            minimum = evaluation['min_conditions']
        bounds = evaluation.get('bounds') if isinstance(evaluation.get('bounds'), dict) else {}
        if channels is not None and set(bounds) != set(channels):
            problems.append(f'evaluation.bounds must give bounds for exactly the channels: {", ".join(channels)}')
        for channel, bound in bounds.items():
            if not isinstance(bound, dict):
                problems.append(f'evaluation.bounds.{channel} must be a table')
                continue
            problems += _fields(bound, {'median': metric, 'p95': metric, 'neutral': metric},
                                f'evaluation.bounds.{channel}.')
    pairs = set()
    curves = get('curves', list)
    if curves is not None and not curves:
        problems.append('curves must list at least one curve')
    for i, curve in enumerate(curves or ()):
        where = f'curves[{i}].'
        if not isinstance(curve, dict):
            problems.append(f'curves[{i}] must be a table')
            continue
        problems += _fields(curve, {'input': (_text, 'text'), 'output': (_text, 'text'),
                                    'knots': (lambda v: isinstance(v, list), 'a list')}, where)
        if channels is not None and _text(curve.get('input')) and curve['input'] not in channels:
            problems.append(f'{where}input {curve["input"]} is not one of the channels')
        pair = (curve.get('input'), curve.get('output'))
        if pair in pairs:
            problems.append(f'the curve {pair[0]} -> {pair[1]} appears twice')
        pairs.add(pair)
        knots = curve.get('knots')
        if not isinstance(knots, list):
            continue
        if len(knots) < 2 or not all(isinstance(k, list) and len(k) == 2 for k in knots):
            problems.append(f'{where}knots must be at least two [input, output] pairs')
        elif not all(_number(v) for k in knots for v in k):
            problems.append(f'{where}knots must be finite numbers')
        else:
            xs, ys = [k[0] for k in knots], [k[1] for k in knots]
            if any(b <= a for a, b in zip(xs, xs[1:])):
                problems.append(f'{where}knots must have strictly increasing inputs')
            rises = [b - a for a, b in zip(ys, ys[1:])]
            if any(d < 0 for d in rises) and any(d > 0 for d in rises):
                problems.append(f'{where}knots must be monotone (never rising after falling, or the reverse)')
    cells = get('cells', list)
    if cells is not None and not cells:
        problems.append('cells must list at least one cell')
    count = held_out.get('count') if held_out is not None and type(held_out.get('count')) is int else None
    for i, cell in enumerate(cells or ()):
        where = f'cells[{i}].'
        if not isinstance(cell, dict):
            problems.append(f'cells[{i}] must be a table')
            continue
        problems += _fields(cell, {'channel': (_text, 'text'), 'side': (_text, 'text'), 'stimulus': (_text, 'text'),
                                   'identity': (_text, 'text'),
                                   'conditions': (lambda v: type(v) is int and v >= (minimum or MIN_CONDITIONS),
                                                  f'an integer >= evaluation.min_conditions'),
                                   'failures': (lambda v: type(v) is int and v >= 0, 'an integer >= 0'),
                                   'median': metric, 'p95': metric, 'neutral': metric}, where)
        conditions = cell.get('conditions')
        if type(conditions) is int and count is not None and conditions > count:
            problems.append(f'{where}conditions {conditions} is more than held_out.count {count}: each cell uses the '
                            'first conditions seeds')
        if type(cell.get('failures')) is int and type(conditions) is int and cell['failures'] > conditions:
            problems.append(f'{where}failures {cell["failures"]} is more than its conditions {conditions}')
        if channels is not None and _text(cell.get('channel')) and cell['channel'] not in channels:
            problems.append(f'{where}channel {cell["channel"]} is not one of the channels')
        if _number(cell.get('median')) and _number(cell.get('p95')) and cell['median'] > cell['p95']:
            problems.append(f'{where}median {cell["median"]} is above p95 {cell["p95"]}')
    return problems


def read_ledger(path: Path) -> tuple[dict, list[str]]:
    """The freeze ledger as {(id, version): frozen_sha256}, and every way it is malformed."""
    entries, latest, problems, previous = {}, {}, [], None
    if not path.is_file():
        return entries, problems
    for number, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        where = f'{LEDGER} line {number}'
        match = LEDGER_LINE.fullmatch(line)
        if not match:
            problems.append(f'{where} must be "<id> v<version> <frozen_sha256> <date YYYY-MM-DD> [reason]"')
            continue
        record_id, version, sha, day, reason = match.groups()
        version = int(version)
        if not RECORD_ID.fullmatch(record_id):
            problems.append(f'{where}: {record_id} is not a record id')
        if not SHA256.fullmatch(sha):
            problems.append(f'{where}: {sha} is not a lowercase hex sha256')
        try:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', day):
                raise ValueError(day)
            date = datetime.date.fromisoformat(day)
        except ValueError:
            problems.append(f'{where}: {day} is not a date written YYYY-MM-DD')
            date = None
        if date and previous and date < previous:
            problems.append(f'{where}: its date {day} is earlier than the line before; lines are only ever added at '
                            'the end')
        previous = date or previous
        expected = latest.get(record_id, 0) + 1
        if version != expected:
            problems.append(f'{where}: {record_id} v{version} should be v{expected}; versions start at v1 and go up '
                            'by one, and each is frozen once')
            continue
        if version > 1 and (reason is None or len(reason.split()) < 3):
            problems.append(f'{where}: {record_id} v{version} needs a reason for re-freezing, of at least three words')
        entries[(record_id, version)] = sha
        latest[record_id] = version
    return entries, problems


def freeze_problem(record: dict, entries: dict) -> str | None:
    """Why a record's frozen hash is not the latest one the ledger recorded for it, if it is not."""
    versions = [v for i, v in entries if i == record['id']]
    frozen = record['held_out']['frozen_sha256']
    if not versions:
        return (f'its frozen hash is not in {LEDGER}: add "{record["id"]} v{record["version"]} {frozen} <date>" '
                'there and commit it before any results')
    if record['version'] != max(versions):
        return f'it is v{record["version"]}, but {LEDGER} has frozen v{max(versions)}'
    if entries[(record['id'], record['version'])] != frozen:
        return (f'its frozen hash {frozen} is not the one {LEDGER} recorded for v{record["version"]}; changing a '
                'frozen value needs a new version, with a reason, in the ledger')
    return None


def cell_passes(record: dict, cell: dict) -> bool:
    """A cell passes if nothing was missed and every error is within the channel's frozen bounds."""
    bound = record['evaluation']['bounds'][cell['channel']]
    return cell['failures'] == 0 and all(cell[k] <= bound[k] for k in ('median', 'p95', 'neutral'))


def pack_rules(root: Path = ROOT) -> list[dict]:
    """Every mapping rule in the checkout's authoring files, found the way msf-tools finds them."""
    rules = []
    for directory, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d != 'generated')
        for name in sorted(names):
            if name.endswith('.toml') and not name.startswith('.'):
                document = tomllib.loads((Path(directory) / name).read_text(encoding='utf-8'))
                rules += [r for m in document.get('mappings', []) for r in m.get('rules', [])]
    return rules


def calibration_problems(records: Path, rules: list[dict]) -> list[str]:
    """Invalid calibration records, and rules whose knots are not exactly their record's frozen knots."""
    problems, valid, invalid = [], {}, set()
    paths = sorted(records.iterdir()) if records.is_dir() else []
    problems += [f'{p.name}: calibration records are named *{RECORD_SUFFIX}; msf-tools would read a .toml file '
                 'as pack authoring' for p in paths if p.suffix == '.toml']
    ledger, found = read_ledger(records / LEDGER)
    problems += found
    for path in (p for p in paths if p.suffix == RECORD_SUFFIX):
        name = path.name[:-len(RECORD_SUFFIX)]
        try:
            record = load_record(path)
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
            problems.append(f'{path.name}: not valid TOML ({error})')
            invalid.add(name)
            continue
        found = record_problems(record, name)
        if not found and (problem := freeze_problem(record, ledger)):
            found = [problem]
        if found:
            problems.append(f'{path.name}: ' + '; '.join(found))
            invalid.add(name)
        else:
            valid[name] = record
    for rule in rules:
        for cited in (e[len(CITATION):] for e in rule.get('evidence', []) if e.startswith(CITATION)):
            label = f'rule {rule.get("id")} cites calibration record {cited}'
            if cited in invalid:
                continue
            if cited not in valid:
                problems.append(f'{label}, which does not exist in {records.name}/')
                continue
            operator = rule.get('operator', {})
            if operator.get('id') != 'piecewise_linear':
                problems.append(f'{label} but its operator is {operator.get("id")}, not piecewise_linear')
                continue
            curve = [c for c in valid[cited]['curves'] if [c['input']] == rule.get('inputs')
                     and [c['output']] == rule.get('outputs')]
            if not curve:
                problems.append(f'{label}, which has no curve from {rule.get("inputs")} to {rule.get("outputs")}')
            elif operator.get('knots') != curve[0]['knots']:
                problems.append(f'{label}, but its knots are not exactly the frozen knots of that curve')
            if 'cells' not in valid[cited]:
                problems.append(f'{label}, which has no results yet')
                continue
            cells = [c for c in valid[cited]['cells'] if [c['channel']] == rule.get('inputs')]
            if not cells:
                problems.append(f'{label}, which has no held-out cell for {rule.get("inputs")}')
            problems += [f'{label}, but its cell for {c["stimulus"]}, {c["identity"]}, side {c["side"]} fails the '
                         'frozen bounds' for c in cells if not cell_passes(valid[cited], c)]
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
        try:
            write_lock(metadata.distribution(DISTRIBUTION), wheel=args.wheel)
        except ValueError as error:
            print(f'Refusing to update the lock: {error}', file=sys.stderr)
            return 2
        return 0
    problems = verify_environment()
    if problems:
        print(f'Refusing to check: the installed {DISTRIBUTION} does not match '
              f'{LOCK.relative_to(ROOT)}.', file=sys.stderr)
        for problem in problems:
            print(f'  - {problem}', file=sys.stderr)
        lock = json.loads(LOCK.read_text(encoding='utf-8'))
        print(f"Install the {DISTRIBUTION} {lock['package_version']} release wheel for your platform by its locked hash "
              f"(commit {lock['git_commit']}; see README). To adopt a reviewed new version instead, install it "
              'and run check.py --update-lock.', file=sys.stderr)
        return 2
    problems = calibration_problems(CALIBRATION, pack_rules(ROOT))
    if problems:
        print('Refusing to check: calibration records, or the rules that cite them, are wrong.', file=sys.stderr)
        for problem in problems:
            print(f'  - {problem}', file=sys.stderr)
        return 1
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
