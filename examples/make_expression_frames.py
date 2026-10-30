#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write expression and talking frames from examples/data/expressions.json.

Usage: python examples/make_expression_frames.py

- fb2_expression_frames.csv: each expression ramps in, holds and ramps out,
  with a neutral frame before it. The "amount" column is the fraction of the
  expression's weights in that frame, and "note" names prototype AUs that FB2
  has no channel for.
- viseme_talk_frames.csv: "bed car toe book" as META visemes, each held and
  crossfaded into the next, so every frame sums to one.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

import make_demo_frames

DATA = Path(__file__).resolve().parent / 'data'
FPS = make_demo_frames.FPS
RAMP, HOLD = 3, 3
TALK_HOLD, TALK_FADE = 2, 3


def library(path: Path = DATA / 'expressions.json') -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


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


def talk_rows(lib: dict) -> list[dict]:
    sequence = lib['talk']['sequence']
    rows = []
    for index, (word, viseme) in enumerate(sequence):
        rows += [{'segment': word, 'phase': 'hold', 'viseme': viseme, 'values': {viseme: 1.0}}] * TALK_HOLD
        if index + 1 < len(sequence):
            next_word, next_viseme = sequence[index + 1]
            for k in range(1, TALK_FADE + 1):
                t = k / (TALK_FADE + 1)
                rows.append({'segment': next_word, 'phase': 'fade', 'viseme': f'{viseme}>{next_viseme}',
                             'values': {viseme: 1.0 - t, next_viseme: t}})
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


def write_all(folder: Path) -> dict[str, int]:
    lib = library()
    fb2, visemes = list(make_demo_frames.FB2_CHANNELS), list(make_demo_frames.VISEME_CHANNELS)
    return {
        'fb2_expression_frames.csv': write(folder / 'fb2_expression_frames.csv', ['phase', 'amount', 'note'], fb2,
                                           ['isValid', 'isEyeFollowingBlendshapesValid'], expression_rows(lib, fb2)),
        'viseme_talk_frames.csv': write(folder / 'viseme_talk_frames.csv', ['phase', 'viseme'], visemes,
                                        ['isValid'], talk_rows(lib)),
    }


def main() -> int:
    for name, count in write_all(DATA).items():
        print(f'examples/data/{name}: {count} frames')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
