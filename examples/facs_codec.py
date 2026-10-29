#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read FACS notation into facs.code values, RCEF's numeric encoding of FACS codes.

Usage: python examples/facs_codec.py "1C+2C+L12B"

The input is a string of codes joined by "+", each with an optional side
letter before it and an optional intensity letter after it, or the dict form
of examples/data/expressions.json ({"L12": "B", "17": 0.6}, a number taken as
is). The output is a value for every mapped facs.code signal: the code's
intensity, or 0 when a scored frame does not list it.

The code table and every reading rule come from examples/data/facs_codes.json
(CC-BY-SA-4.0); this file holds only the logic. Each rule is an RCEF
assumption, and the values are not FACS scores:

- A-E are 0.2-1.0, and a code with no letter is C;
- no side letter sets both sides of a sided code; L or R sets one side; on a
  direction code (30) L or R is the direction;
- refused, with the codes named: U and A; a direction code or a wink (46)
  with no side letter; a side letter on a code whose every signal (written,
  read as another code or left out) is shared, such as 17, 27 or 37, or on a
  visibility code;
  the same code twice; two codes that write one signal (26 and 27; two of 43,
  45 and 46 on one eye); a code that is not in the list (M codes included;
  97* and 98* are written with their asterisk, as the list writes them);
- some codes are read as another code (27 as 26; 45 and 46 as 43), some
  leave signals out (41, 42, 44, 33, 37 and the visibility codes 70-74),
  and the rest are listed as not read. A left-out signal has no value at
  all, never 0, so the in-map refuses its group.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import cache
import json
from pathlib import Path
import re
import sys

DATA = Path(__file__).resolve().parent / 'data' / 'facs_codes.json'
TOKEN = re.compile(r'([LRUA]?)(M?)(\d+\*?)([A-E]?)')
KEY = re.compile(r'([LRUA]?)(M?)(\d+\*?)')
SIDES = {'L': ('left',), 'R': ('right',), '': ('left', 'right')}


@dataclass(frozen=True)
class Reading:
    """values is None when the notation is refused; refused then names each problem and its codes."""
    values: dict[str, float] | None
    left_out: tuple[str, ...] = ()
    not_read: tuple[str, ...] = ()
    refused: tuple[str, ...] = ()


@cache
def table(path: Path = DATA) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def signal_id(code: str, side: str | None = None) -> str:
    return f'facs.code.au{int(code):02d}' + (f'_{side}' if side else '')


def signals(data: dict | None = None) -> list[str]:
    """The mapped facs.code signals, in code order, left before right."""
    data = data or table()
    found = []
    for code, entry in data['codes'].items():
        if entry['read'] in ('sided', 'direction'):
            found += [signal_id(code, side) for side in SIDES['']]
        elif entry['read'] == 'shared':
            found.append(signal_id(code))
    return found


def _targets(code: str, side: str, data: dict) -> list[str]:
    """The signals a mapped code writes on the given side ('' for both sides of a sided code)."""
    read = data['codes'][code]['read']
    return [signal_id(code)] if read == 'shared' else [signal_id(code, s) for s in SIDES[side]]


def _items(notation, data):
    """(text, side, m, code, value) for each code, or a refusal message."""
    if isinstance(notation, str):
        tokens = [t.strip() for t in notation.split('+')] if notation.strip() else []
        for token in tokens:
            match = TOKEN.fullmatch(token)
            if not match:
                yield f'{token or "(empty)"}: not FACS notation'
                continue
            side, m, code, letter = match.groups()
            yield token, side, m, code, data['letters'][letter or data['no_letter']]
        return
    for key, value in notation.items():
        match = KEY.fullmatch(key) if isinstance(key, str) else None
        if not match:
            yield f'{key}: not a FACS code key'
        elif isinstance(value, str) and value in data['letters']:
            yield (key, *match.groups(), data['letters'][value])
        elif type(value) in (int, float):
            yield (key, *match.groups(), float(value))
        else:
            yield f'{key}: {value!r} is neither an intensity letter nor a number'


def read(notation: str | dict, data: dict | None = None) -> Reading:
    data = data or table()
    codes, refused, not_read, seen = data['codes'], [], [], set()
    writes, left_out = {}, set()
    for item in _items(notation, data):
        if isinstance(item, str):
            refused.append(item)
            continue
        text, side, m, code, value = item
        if (side, m, code) in seen:
            refused.append(f'{text}: the same code twice')
            continue
        seen.add((side, m, code))
        if side in ('U', 'A'):
            refused.append(f'{text}: {side} (one side unstated, or both sides with one stronger) cannot be encoded')
            continue
        if m:
            if f'M{code}' in data['m_codes']:
                not_read.append(text)
            else:
                refused.append(f'{text}: not a code in the FACS list')
            continue
        if code in data['visibility']:
            if side:
                refused.append(f'{text}: a visibility code names a region, not a side')
                continue
            region = data['visibility'][code]['leave_out']
            region = [c for c, e in codes.items() if e['disposition'] == 'mapped'] if region == 'all' else region
            left_out.update(s for c in region for s in _targets(c, '', data))
            continue
        if code not in codes:
            refused.append(f'{text}: not a code in the FACS list')
            continue
        rule = codes[code]['read']
        if rule == 'none':
            not_read.append(text)
            continue
        if isinstance(rule, dict) and 'leave_out' in rule:
            if side and all(codes[c]['read'] == 'shared' for c in rule['leave_out']):
                refused.append(f'{text}: code {code} leaves out only signals with no sides in facs.code')
                continue
            left_out.update(s for c in rule['leave_out'] for s in _targets(c, side, data))
            continue
        target = rule['as'] if isinstance(rule, dict) else code
        needs_side = codes[target]['read'] == 'direction' or isinstance(rule, dict) and rule.get('side') == 'required'
        if needs_side and not side:
            refused.append(f'{text}: needs L or R')
            continue
        if side and codes[target]['read'] == 'shared':
            refused.append(f'{text}: code {target} has no sides in facs.code')
            continue
        for sid in _targets(target, side, data):
            if sid in writes:
                refused.append(f'{writes[sid][0]} and {text}: two codes write {sid}')
            writes[sid] = (text, value)
    if refused:
        return Reading(None, refused=tuple(dict.fromkeys(refused)))
    values = {sid: writes[sid][1] if sid in writes else 0.0 for sid in signals(data) if sid not in left_out}
    return Reading(values, tuple(s for s in signals(data) if s in left_out), tuple(not_read))


def letter(value: float, data: dict | None = None) -> str:
    """The intensity letter a value shows, or '' (absent); for display only."""
    if not 0 <= value <= 1:
        raise ValueError(f'{value!r} is outside [0, 1]')
    shown = ''
    for bound, name in (data or table())['decode']:
        if value >= bound:
            shown = name
    return shown


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.split('\n\n')[1], file=sys.stderr)
        return 2
    reading = read(argv[0])
    if reading.values is None:
        print('refused:\n' + '\n'.join(f'  {r}' for r in reading.refused))
        return 1
    for sid, value in reading.values.items():
        if value:
            print(f'{sid} = {value!r} ({letter(value) if 0 <= value <= 1 else "?"})')
    for label, items in (('left out', reading.left_out), ('not read', reading.not_read)):
        if items:
            print(f'{label}: {" ".join(items)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
