# SPDX-License-Identifier: MIT
"""Arm A3 of the A/B comparison: the expression library's AU -> FB2 table, frozen at dea1713.

The functions below are copies of intensity, split_side, channels_for,
fb2_weights, missing_aus, expression_rows and write in
examples/make_expression_frames.py at dea1713. FPS and the 70 FB2 channels,
in their order, are frozen from the fixture's CSV. A3 reads only
tests/fixtures/a3-dea1713/ (expressions.json and fb2_expression_frames.csv
at dea1713, SHA-256 pinned below), so it cannot move when the library, the
generator or the pack changes, and it needs no msf-character-tools.

b_inputs() gives B's input for the same frames: each library value becomes
intensity(value) * amount, in the library's order, and the shipped FACS codec
reads the result. So A3 and B start from the same bits, and a difference
between them tests the codec and the FACS maps, not a second converter.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/a3-dea1713'
COMMIT = 'dea171370bba25dda3aa6b9846a346b5fca43aa5'
SHA256 = {'expressions.json': 'e470015e53ff2a8a7c24d6e3aafd368384f4ae7aec7e752de17ef9b56e9b6422',
          'fb2_expression_frames.csv': '0f6e0cef34688b2a46bdc5129f64f2094975059209d6e1f8a5db6c1dbf2c3cdb'}
FPS = 15
RAMP, HOLD = 3, 3
LABELS = ['phase', 'amount', 'note']
FLAGS = ['isValid', 'isEyeFollowingBlendshapesValid']


def fixture_problems() -> list[str]:
    return [f'{name} does not have the pinned SHA-256' for name, digest in SHA256.items()
            if hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() != digest]


def library() -> dict:
    if fixture_problems():
        raise SystemExit('; '.join(fixture_problems()))
    return json.loads((FIXTURE / 'expressions.json').read_text(encoding='utf-8'))


def channels() -> list[str]:
    """The 70 FB2 channels, in the order of the fixture's CSV header."""
    with (FIXTURE / 'fb2_expression_frames.csv').open(encoding='utf-8', newline='') as handle:
        header = next(csv.reader(handle))
    return header[2 + len(LABELS):-len(FLAGS)]


# ---------------------------------------------------------------- copies of make_expression_frames.py at dea1713

def intensity(value, lib: dict) -> float:
    return lib['intensity'][value] if isinstance(value, str) else float(value)


def split_side(key: str) -> tuple[str, str]:
    """'L12' -> ('L', '12'); '12' -> ('', '12')."""
    return (key[0], key[1:]) if key[0] in 'LR' else ('', key)


def channels_for(key: str, lib: dict, channels: list[str]) -> list[str]:
    side, au = split_side(key)
    target = lib['au_channels'][au]
    if isinstance(target, dict):
        if not side:
            raise ValueError(f'AU {au} needs a side or direction')
        return [target[side]]
    if target in channels:
        return [target]
    # The sided channels: _L/_R, or the four lip quarters _LB, _LT, _RB, _RT.
    found = [c for c in channels if c.startswith(target + '_') and c[len(target) + 1:] in ('L', 'R', 'LB', 'LT', 'RB', 'RT')]
    if side:
        found = [c for c in found if c[len(target) + 1] == side]
    if not found:
        raise ValueError(f'AU {key}: no FB2 channel {target}')
    return found


def fb2_weights(expression: dict, lib: dict, channels: list[str]) -> dict[str, float]:
    weights = {}
    for key, value in expression['aus'].items():
        if split_side(key)[1] in lib['no_fb2_channel']:
            continue
        for channel in channels_for(key, lib, channels):
            weights[channel] = intensity(value, lib)
    return weights


def missing_aus(expression: dict, lib: dict) -> list[str]:
    return [f'AU {au} ({lib["no_fb2_channel"][au]}): no FB2 channel'
            for au in (split_side(k)[1] for k in expression['aus']) if au in lib['no_fb2_channel']]


def expression_rows(lib: dict, channels: list[str]) -> list[dict]:
    rows = []
    for expression in lib['expressions']:
        weights = fb2_weights(expression, lib, channels)
        note = '; '.join(missing_aus(expression, lib))
        rows.append({'segment': 'neutral', 'phase': '', 'amount': 0.0, 'note': '', 'values': {}})
        amounts = ([('in', k / (RAMP + 1)) for k in range(1, RAMP + 1)] + [('hold', 1.0)] * HOLD
                   + [('out', k / (RAMP + 1)) for k in range(RAMP, 0, -1)])
        for phase, amount in amounts:
            rows.append({'segment': expression['name'], 'phase': phase, 'amount': amount, 'note': note,
                         'values': {c: w * amount for c, w in weights.items()}})
    rows.append({'segment': 'neutral', 'phase': '', 'amount': 0.0, 'note': '', 'values': {}})
    return rows


def write(path: Path, label_columns: list[str], channels: list[str], flags: list[str], rows: list[dict]) -> int:
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['time', 'segment', *label_columns, *channels, *flags])
        for frame, row in enumerate(rows):
            labels = [f'{row[c]:g}' if isinstance(row[c], float) else row[c] for c in label_columns]
            writer.writerow([f'{frame / FPS:.6f}', row['segment'], *labels,
                             *(repr(row['values'].get(c, 0.0)) for c in channels), *('1' for _ in flags)])
    return len(rows)


# ---------------------------------------------------------------- the arm

def rewrite(path: Path) -> int:
    """Write fb2_expression_frames.csv as at dea1713, from the fixture alone."""
    lib, fb2 = library(), channels()
    return write(path, LABELS, fb2, FLAGS, expression_rows(lib, fb2))


def a3_frames() -> list[dict]:
    """A3's FB2 values for the 221 library frames; every channel no AU sets is 0.0, as the writer fills it."""
    lib, fb2 = library(), channels()
    return [{c: row['values'].get(c, 0.0) for c in fb2} for row in expression_rows(lib, fb2)]


def a3_keys(keys: dict[str, float]) -> dict[str, float]:
    """A3's FB2 values for one set of library keys at amount 1, such as a held-out letter frame or a key impulse."""
    lib, fb2 = library(), channels()
    weights = fb2_weights({'aus': keys}, lib, fb2)
    return {c: weights[c] * 1.0 if c in weights else 0.0 for c in fb2}


def b_keys() -> list[dict]:
    """B's input keys for the 221 library frames: intensity(value) * amount for each key, in the library's order."""
    lib = library()
    keys = []
    for row in expression_rows(lib, channels()):
        expression = next((e for e in lib['expressions'] if e['name'] == row['segment']), None)
        keys.append({k: intensity(v, lib) * row['amount'] for k, v in expression['aus'].items()}
                    if expression else {})
    return keys


def b_inputs(codec) -> list:
    """B's facs.code input for the 221 library frames: the codec's reading of each frame's keys."""
    return [codec.read(keys) for keys in b_keys()]
