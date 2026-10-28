# SPDX-License-Identifier: MIT
"""Run the rig-gain record's held-out evaluation after the provenance checks in tools/calibration/provenance.py.

The run uses the checkout given with --checkout. It must be a checkout of the record's freeze commit or of a later
commit that does not change the code the record names. This tool first checks that:

- the record and its ledger line are committed in that checkout;
- the msf-character-tools installed for this interpreter passes that checkout's check.py lock check;
- every cached input has the SHA-256 the record pins;
- every repository file the run imports (found from the loaded modules), the landmarks and the renderer source are
  exactly as at code_commit, and the renderer binary is the one the record names.

It then runs rig_gains.py's evaluation in this process. If this checkout's
calibration/rig-gains.ict-rocketbox-female.cal has cells and the same frozen hash, it reports whether the new cells
are equal to them.

Usage:
  git worktree add /tmp/k3-freeze FREEZE_COMMIT
  python tools/calibration/k3_heldout.py --checkout /tmp/k3-freeze --ict-cache DIR --rig-cache DIR \\
    --renderer BIN --work DIR --out heldout.json
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import provenance

RECORD_ID = 'rig-gains.ict-rocketbox-female'
PUBLISHED = Path(__file__).resolve().parents[2] / f'calibration/{RECORD_ID}.cal'
DATA_FILES = ['examples/data/rig_landmarks.json']


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # so loaded_files() sees it
    spec.loader.exec_module(module)
    return module


def record_path(checkout: Path) -> Path:
    for path in (checkout / f'calibration/{RECORD_ID}.cal', checkout / f'calibration/pending/{RECORD_ID}.cal'):
        if path.is_file():
            return path
    raise SystemExit(f'no record {RECORD_ID} in {checkout}/calibration')


def require_committed(checkout: Path, *paths: Path) -> None:
    for path in paths:
        rel = path.relative_to(checkout).as_posix()
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', rel], cwd=checkout, capture_output=True)
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=checkout, capture_output=True, text=True)
        if tracked.returncode or dirty.stdout.strip():
            raise SystemExit(f'{rel} must be committed, unchanged, before the held-out run')


def input_paths(record: dict, checkout: Path, ict_cache: Path, rig_cache: Path) -> dict[Path, str]:
    """Where each of the record's inputs is cached, with the SHA-256 the record pins."""
    out = {}
    for item in record['inputs']:
        name = item['name']
        if name.startswith('ICT-FaceKit '):
            path = ict_cache / name.split()[1]
        elif name.startswith('Microsoft Rocketbox '):
            path = rig_cache / name.split()[2]
        elif name.startswith('RCEF '):
            path = checkout / name.split()[1]
        else:
            raise SystemExit(f'unknown input {name}')
        out[path] = item['sha256']
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--checkout', type=Path, required=True, help="a checkout of the record's freeze commit")
    parser.add_argument('--ict-cache', type=Path, required=True)
    parser.add_argument('--rig-cache', type=Path, required=True)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    checkout = args.checkout.resolve()
    record_file = record_path(checkout)
    require_committed(checkout, record_file, checkout / 'calibration/FREEZES')
    check = load_module('rcef_check_frozen', checkout / 'check.py')
    problems = check.verify_environment()
    if problems:
        raise SystemExit('the installed msf-character-tools is not the locked build:\n' + '\n'.join(problems))
    record = check.load_record(record_file)
    entries, problems = check.read_ledger(checkout / 'calibration/FREEZES')
    if problems or (problem := check.freeze_problem(record, entries)):
        raise SystemExit('\n'.join(problems) or problem)
    problems = provenance.input_problems(input_paths(record, checkout, args.ict_cache, args.rig_cache))
    if problems:
        raise SystemExit('cached inputs differ from the record:\n' + '\n'.join(problems))
    sys.path.insert(0, str(checkout / 'examples'))
    import rig_gains  # noqa: E402  (imported from the checkout, so the code check covers it)
    import rigs  # noqa: E402,F401
    code = provenance.loaded_files(checkout) + DATA_FILES + ['tools/render']
    if problem := provenance.code_problem(checkout, record['code_commit'], code):
        raise SystemExit(problem)
    print(f'code as at {record["code_commit"][:12]}: {", ".join(code)}')
    if hashlib.sha256(args.renderer.read_bytes()).hexdigest() != record['renderer']['binary_sha256']:
        raise SystemExit('this is not the renderer binary the record names')
    status = rig_gains.main(['evaluate', '--record', str(record_file), '--ict-cache', str(args.ict_cache),
                             '--rig-cache', str(args.rig_cache), '--renderer', str(args.renderer),
                             '--work', str(args.work), '--out', str(args.out)])
    unchecked = sorted(set(provenance.loaded_files(checkout)) - set(code))
    if unchecked:
        raise SystemExit(f'the run imported repository code that was not checked first: {", ".join(unchecked)}')
    result = json.loads(args.out.read_text(encoding='utf-8'))
    result.update(code_commit=record['code_commit'], code_files=code)
    published = check.load_record(PUBLISHED) if PUBLISHED.is_file() else {}
    if published.get('cells'):
        if published['held_out']['frozen_sha256'] != record['held_out']['frozen_sha256']:
            raise SystemExit(f'{PUBLISHED.name} is not the record frozen in {checkout}')
        result['reproduces_record_cells'] = result['cells'] == published['cells']
        print('cells reproduce the record exactly' if result['reproduces_record_cells'] else 'cells DIFFER from the record')
    args.out.write_text(json.dumps(result, indent=1), encoding='utf-8')
    return status if result.get('reproduces_record_cells', True) else 1


if __name__ == '__main__':
    raise SystemExit(main())
