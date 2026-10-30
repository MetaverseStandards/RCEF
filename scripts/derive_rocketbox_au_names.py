#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the Rocketbox FACS shape names (AU_*) for the facs.code profile.

The names come from the two facial FBX files that examples/rigs.py pins
(Female_Adult_01 and Male_Adult_01), read with msf_character_tools. Both must
have the same names. scripts/build_canonical.py reads the output as the
aligned names of the facs.code signals, cited to the record rocketbox_avatars.

Output: tests/fixtures/rocketbox_au_names.json.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import rigs  # noqa: E402

OUTPUT = ROOT / 'tests/fixtures/rocketbox_au_names.json'
AVATARS = ('Female_Adult_01', 'Male_Adult_01')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--cache', type=Path, required=True, help='directory for the rig files')
    args = parser.parse_args()
    names = {}
    for avatar in AVATARS:
        which, _, number = avatar.split('_')
        names[avatar] = list(rigs.load_rocketbox(args.cache, which, number).facs)
    if len({tuple(n) for n in names.values()}) != 1:
        raise SystemExit('the pinned Rocketbox rigs have different AU_* shapes')
    document = {'record': 'rocketbox_avatars', 'commit': rigs.ROCKETBOX_COMMIT,
                'files': {f'{a}_facial.fbx': rigs.ROCKETBOX_SHA256[a] for a in AVATARS},
                'note': 'AU_* shape names in file order, as facts: AU_<code>_<name> or AU_<code>_<L or R>_<name>',
                'names': names[AVATARS[0]]}
    OUTPUT.write_text(json.dumps(document, indent=1) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
