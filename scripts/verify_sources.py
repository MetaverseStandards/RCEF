#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Download public evidence, with size and time limits, and check it against its recorded digest."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib
from urllib.error import URLError
from urllib.request import Request, urlopen

MAX_BYTES = 5_000_000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, help='optional directory for exact fetched bytes')
    parser.add_argument('--source', action='append', help='verify only named evidence IDs')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = tomllib.loads((root / 'evidence/sources.toml').read_text())['evidence']
    known = {r['id'] for r in records}
    if args.source and not set(args.source) <= known:
        parser.error('unknown evidence ID')
    if args.cache:
        cache = args.cache.resolve()
        if cache == root or root in cache.parents:
            parser.error('keep exact source cache outside the public repository')
        cache.mkdir(parents=True, exist_ok=True)
    failures = []
    count = 0
    for record in records:
        if 'url' not in record or args.source and record['id'] not in args.source:
            continue
        if not re.fullmatch(r'[a-z0-9_]+', record['id']):
            parser.error('non-portable source ID')
        try:
            request = Request(record['url'], headers={'User-Agent': 'RCEF-evidence/0.1'})
            with urlopen(request, timeout=25) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError('source exceeds bounded response size')
            digest = hashlib.sha256(data).hexdigest()
            if digest != record['sha256']:
                raise ValueError('source bytes changed; evidence needs review')
            if args.cache:
                (cache / record['id']).write_bytes(data)
            count += 1
        except (URLError, OSError, ValueError) as exc:
            failures.append({'id': record['id'], 'message': str(exc)})
    print(json.dumps({'verified': count, 'failures': failures}, sort_keys=True))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
