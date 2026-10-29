#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Input frames for the A/B comparison of the pivot route with the direct maps (ab/README.md).

Usage: python scripts/ab_frames.py ABREG OUT_DIR

Writes one JSON-lines file per family to OUT_DIR/frames/ and their SHA-256
to OUT_DIR/SHA256SUMS. A frame is {"family", "label", "values", "flags"},
plus "keys" (FACS library keys) in the FACS key families.

- Channel lists, domains, validity flags, opposing gaze pairs, family sizes
  and value ranges come only from the registration (.abreg). The script never
  reads the live pack. pinned_source() copies them from a pack document at
  registration time: from the A1 fixture, or from the B pack for sets only B
  reads.
- Seeded families draw full-mantissa binary64 values and 6-decimal values,
  mixed value by value. Seed i is the first 8 bytes, big-endian, of
  sha256("<seed_root>:<i>"), as calibration records do (check.py), and i is
  the family's place in the registration's family list.
- The grid, edge and impulse families are fixed lists: they do not depend on
  seed_root, so every A1 figure the registration records can be computed
  before seed_root exists.
- Random numbers come only from getrandbits, whose output for a given seed
  does not change between Python versions.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SEED_RULE = 'rcef.ab.seeds/1'
FORMAT = 'rcef.ab.frames/1'
DECIMALS = 10 ** 6


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', x))[0]


# Family 5: values that exercise signed zero, rounding near the knots, float32 inputs and products near underflow.
EDGE_VALUES = (0.0, -0.0, 1.0, 2.0 ** -30, 0.1, 0.3, 2.0 ** -54, 2.0 ** -53, 0.5,
               math.nextafter(0.5, 0.0), math.nextafter(0.5, 1.0), math.nextafter(1.0, 0.0),
               f32(0.1), f32(0.3), f32(1 / 3), f32(0.7),
               5e-324, 1.5e-323, (1 + 2.0 ** -52) * 2.0 ** -1021, 2.0 ** -1020, 2.0 ** -1022)
GAZE_PAIR_VALUES = ((0.3, 0.1), (0.1, 0.3), (0.3, 0.3), (1.0, 1.0))
IMPULSE_AMPLITUDES = (1.0, 0.5)
GRID_STEPS = 16
LETTER_VALUES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
# Opposing gaze directions, in the naming styles of the pinned sets: FB2 and ARKit.
OPPOSING = (re.compile(r'(.*EYES_LOOK_)(LEFT|UP)(_[LR]_FB)$'), re.compile(r'(.*eyeLook)(In|Up)(Left|Right)$'))
PARTNER = {'LEFT': 'RIGHT', 'UP': 'DOWN', 'In': 'Out', 'Up': 'Down'}


# ---------------------------------------------------------------- what the registration pins

def opposing_pairs(channels: list[str]) -> list[list[str]]:
    pairs = []
    for sid in channels:
        for pattern in OPPOSING:
            match = pattern.fullmatch(sid)
            if match and (other := f'{match[1]}{PARTNER[match[2]]}{match[3]}') in channels:
                pairs.append([sid, other])
    return pairs


def pinned_source(document: dict, profile: str) -> dict:
    """What the generator needs about one source set, copied from a pack document into the registration."""
    signals = {s['id']: s for s in document['signals']}
    members = next(p['signal_ids'] for p in document['profiles'] if p['id'] == profile)
    # Count sentinels are inventory records, not weights a runtime reports.
    channels = [sid for sid in members if signals[sid]['disposition'] != 'excluded']
    validity = {sid: signals[sid]['validity'] for sid in channels if signals[sid].get('validity')}
    flags = sorted({f.strip() for v in validity.values() for f in v.split(' AND ')})
    domains = {sid: [signals[sid]['domain'].get('min'), signals[sid]['domain'].get('max')] for sid in channels}
    return {'channels': channels, 'domains': domains, 'validity': validity, 'flags': flags,
            'gaze_pairs': opposing_pairs(channels)}


# ---------------------------------------------------------------- values

def seed(seed_root: str, index: int) -> int:
    return int.from_bytes(hashlib.sha256(f'{seed_root}:{index}'.encode()).digest()[:8], 'big')


def below(rng: random.Random, n: int) -> int:
    """A uniform integer in [0, n), by rejection from getrandbits."""
    while True:
        value = rng.getrandbits(n.bit_length())
        if value < n:
            return value


def full_mantissa(rng: random.Random) -> float:
    """Uniform on [0, 1) with all 52 mantissa bits random: ldexp(1 + m * 2**-52, -1 - k).

    k counts the leading zero bits of a random 64-bit word, so the exponent
    falls by one with probability one half, as for a uniform value.
    """
    word = rng.getrandbits(64)
    k = 64 - word.bit_length()
    return math.ldexp(1 + rng.getrandbits(52) * 2.0 ** -52, -1 - k)


def decimal6(rng: random.Random) -> float:
    """A value with 6 decimal places, as in the example CSVs: n / 10**6, correctly rounded."""
    return below(rng, DECIMALS + 1) / DECIMALS


def mixed(rng: random.Random, low: float = 0.0, high: float = 1.0) -> float:
    value = full_mantissa(rng) if rng.getrandbits(1) else decimal6(rng)
    return value if (low, high) == (0.0, 1.0) else low + (high - low) * value


# ---------------------------------------------------------------- fixed families

def frame(family, label, values, source, flags=None):
    return {'family': family, 'label': label, 'values': values,
            'flags': flags if flags is not None else dict.fromkeys(source['flags'], True)}


def zero(source):
    return dict.fromkeys(source['channels'], 0.0)


def grid_family(name: str, source: dict) -> list[dict]:
    """Family 4: every channel at k/16, then each pattern of validity flags on a half-way frame."""
    frames = [frame(name, f'all {k}/{GRID_STEPS}', dict.fromkeys(source['channels'], k / GRID_STEPS), source)
              for k in range(GRID_STEPS + 1)]
    flags = source['flags']
    for pattern in range(2 ** len(flags)):
        states = {f: not pattern >> n & 1 for n, f in enumerate(flags)}
        cleared = [f for f, ok in states.items() if not ok]
        frames.append(frame(name, f'flags cleared: {" ".join(cleared) or "none"}',
                            dict.fromkeys(source['channels'], 0.5), source, states))
    return frames


def edge_family(name: str, source: dict) -> list[dict]:
    """Family 5: each edge value on every channel at once and on each channel alone, and the opposing gaze pairs."""
    frames = []
    for value in EDGE_VALUES:
        frames.append(frame(name, f'all {value!r}', dict.fromkeys(source['channels'], value), source))
    for sid in source['channels']:
        for value in EDGE_VALUES:
            frames.append(frame(name, f'{sid} {value!r}', {**zero(source), sid: value}, source))
    for a, b in source['gaze_pairs']:
        for x, y in GAZE_PAIR_VALUES:
            frames.append(frame(name, f'{a} {x!r}, {b} {y!r}', {**zero(source), a: x, b: y}, source))
    return frames


def impulse_family(name: str, source: dict) -> list[dict]:
    """Family 6: the all-zero frame, then each channel alone at each fixed amplitude."""
    frames = [frame(name, 'all zero', zero(source), source)]
    for sid in source['channels']:
        for amplitude in IMPULSE_AMPLITUDES:
            frames.append(frame(name, f'{sid} {amplitude!r}', {**zero(source), sid: amplitude}, source))
    return frames


def golden_family(name: str, goldens: dict, sources: dict, kinds: dict) -> list[dict]:
    """Family 1: each golden case on its own source set, every other channel 0."""
    frames = []
    for n, case in enumerate(goldens['cases']):
        source = sources[kinds[case['mapping_kind']]]
        frames.append(frame(name, f'case {n} {case["mapping_kind"]}', {**zero(source), **case['inputs']}, source))
    return frames


def csv_family(name: str, path: Path, source: dict, prefix: str, suffix: str) -> list[dict]:
    """Family 2: an example CSV; columns are channels named without the prefix and suffix, then flags."""
    with path.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    channels = [c for c in rows[0] if f'{prefix}{c}{suffix}' in source['channels']]
    return [frame(name, f'{r["time"]} {r.get("segment", "")}', {f'{prefix}{c}{suffix}': float(r[c]) for c in channels},
                  source, {f: r[f] == '1' for f in source['flags']}) for r in rows]


def facs_key(sid: str) -> str:
    """facs.code.au01_left -> 'L1', facs.code.au17 -> '17': FACS notation, the library's key form."""
    match = re.fullmatch(r'facs\.code\.au(\d\d)(?:_(left|right))?', sid)
    side = {'left': 'L', 'right': 'R', None: ''}[match[2]]
    return f'{side}{int(match[1])}'


def facs_key_impulses(name: str, sided: list[str], shared: list[str], directions: list[str]) -> list[dict]:
    """Item 9: each sided code as a two-sided, an L and an R key, each shared code and each direction, at 1 and 0.5.

    No side prefix goes on a shared code: the A3 table ignores it there, while the codec refuses it.
    """
    keys = [k for code in sided for k in (code, f'L{code}', f'R{code}')] + list(shared) + list(directions)
    return [{'family': name, 'label': f'{key} {amplitude!r}', 'keys': {key: amplitude}}
            for key in keys for amplitude in IMPULSE_AMPLITUDES]


# ---------------------------------------------------------------- seeded families

def uniform_family(spec, source, rng):
    low, high = spec.get('range', [0.0, 1.0])
    frames = []
    for n in range(spec['count']):
        values = {sid: mixed(rng, low, high) for sid in source['channels']}
        label = 'uniform'
        if spec.get('kind') == 'fb2_contract':
            # FB2 reports at most one direction of each opposing gaze pair as non-zero.
            for pair in source['gaze_pairs']:
                values[pair[below(rng, 2)]] = 0.0
            label = 'gaze exclusive'
        outside = spec.get('outside')
        if outside and n % outside['every'] == 0:
            sid = outside['channels'][below(rng, len(outside['channels']))]
            values[sid] = outside['values'][below(rng, len(outside['values']))]
            label = f'outside [0, 1]: {sid}'
        frames.append(frame(spec['name'], label, values, source))
    return frames


def simplex_family(spec, source, rng):
    """Class probabilities that sum to 1 in decimal: 10**6 split at random cut points."""
    frames, k = [], len(source['channels'])
    for _ in range(spec['count']):
        cuts = sorted(below(rng, DECIMALS + 1) for _ in range(k - 1))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [DECIMALS])]
        frames.append(frame(spec['name'], 'simplex', {sid: p / DECIMALS for sid, p in zip(source['channels'], parts)},
                            source))
    return frames


def vrm_family(spec, source, rng):
    """Uniform frames, frames with only the both-eyes blink set, all-zero frames and multi-vowel frames, in turn."""
    frames = []
    for n in range(spec['count']):
        kind = n % 4
        if kind == 0:
            values, label = {sid: mixed(rng) for sid in source['channels']}, 'uniform'
        elif kind == 1:
            values, label = {**zero(source), spec['blink']: mixed(rng)}, 'only blink'
        elif kind == 2:
            values, label = zero(source), 'all zero'
        else:
            values, label = {**zero(source), **{v: mixed(rng) for v in spec['vowels']}}, 'several vowels'
        frames.append(frame(spec['name'], label, values, source))
    return frames


def letter_family(spec, rng):
    """The held-out FACS letter frames: each shared channel at 0, 0.2, ... or 1.0, as library keys."""
    frames = []
    for _ in range(spec['count']):
        keys = {}
        for sid in spec['channels']:
            value = LETTER_VALUES[below(rng, len(LETTER_VALUES))]
            if value:
                keys[facs_key(sid)] = value
        frames.append({'family': spec['name'], 'label': 'letters', 'keys': keys})
    return frames


SEEDED = {'uniform': uniform_family, 'fb2_contract': uniform_family, 'simplex': simplex_family, 'vrm': vrm_family}


def seeded_family(spec: dict, sources: dict, seed_root: str, index: int) -> list[dict]:
    rng = random.Random(seed(seed_root, index))
    if spec['kind'] == 'facs_letters':
        return letter_family(spec, rng)
    return SEEDED[spec['kind']](spec, sources[spec['source']], rng)


def perturbation_family(name: str, bases: list[dict], source: dict) -> list[dict]:
    """Family 7: each input of each base frame left out, set to 1.5 and set to -0.1, and each flag cleared."""
    frames = []
    for n, base in enumerate(bases):
        for sid in source['channels']:
            frames.append({**base, 'family': name, 'label': f'base {n}: {sid} left out',
                           'values': {k: v for k, v in base['values'].items() if k != sid}})
            for value in (1.5, -0.1):
                frames.append({**base, 'family': name, 'label': f'base {n}: {sid} {value!r}',
                               'values': {**base['values'], sid: value}})
        for flag in source['flags']:
            frames.append({**base, 'family': name, 'label': f'base {n}: {flag} cleared',
                           'flags': {**base['flags'], flag: False}})
    return frames


# ---------------------------------------------------------------- all families of a registration

def family_source(name: str, abreg: dict) -> str:
    """The source set of a family: in its name ("edge:<profile>"), its spec, or facs.code for the FACS key families."""
    if name.startswith('perturb:'):
        name = name.split(':', 1)[1]
    spec = next((f for f in abreg['families'] if f['name'] == name), None)
    if spec:
        return spec.get('source', 'facs.code')
    if name.startswith('facs_'):
        return 'facs.code'
    return name.split(':')[1]


def fixed_families(abreg: dict) -> dict[str, list[dict]]:
    """Families 4, 5 and 6 for every pinned source; they read no seed."""
    families = {}
    for profile, source in abreg['sources'].items():
        families[f'grid:{profile}'] = grid_family(f'grid:{profile}', source)
        families[f'edge:{profile}'] = edge_family(f'edge:{profile}', source)
        families[f'impulse:{profile}'] = impulse_family(f'impulse:{profile}', source)
    return families


def fixed_inputs(abreg: dict, root: Path = ROOT) -> dict[str, list[dict]]:
    """Families 1 and 2 and the FACS key impulses (item 9); each input file must have its pinned SHA-256."""
    spec, families = abreg.get('fixed_inputs', {}), {}

    def read(entry):
        data = (root / entry['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise SystemExit(f'{entry["path"]} does not have the SHA-256 the registration pins')
        return root / entry['path']
    if 'goldens' in spec:
        goldens = json.loads(read(spec['goldens']).read_text(encoding='utf-8'))
        for source in dict.fromkeys(spec['goldens']['kinds'].values()):
            kinds = spec['goldens']['kinds']
            cases = {**goldens, 'cases': [c for c in goldens['cases'] if kinds[c['mapping_kind']] == source]}
            families[f'goldens:{source}'] = golden_family(f'goldens:{source}', cases, abreg['sources'],
                                                          spec['goldens']['kinds'])
    for entry in spec.get('csv', []):
        name = f'csv:{entry["source"]}:{Path(entry["path"]).stem}'
        families[name] = csv_family(name, read(entry), abreg['sources'][entry['source']], entry['prefix'],
                                    entry['suffix'])
    if 'facs_keys' in spec:
        keys = spec['facs_keys']
        families['facs_key_impulses'] = facs_key_impulses('facs_key_impulses', keys['sided'], keys['shared'],
                                                          keys['directions'])
    return families


def seeded_families(abreg: dict) -> dict[str, list[dict]]:
    """Families 3 and 7, from the registration's seed_root."""
    families = {}
    for index, spec in enumerate(abreg['families']):
        families[spec['name']] = seeded_family(spec, abreg['sources'], abreg['seed_root'], index)
    for spec in abreg.get('perturbations', []):
        bases = families[spec['family']][:spec['bases']]
        source = abreg['sources'][next(f['source'] for f in abreg['families'] if f['name'] == spec['family'])]
        families[f'perturb:{spec["family"]}'] = perturbation_family(f'perturb:{spec["family"]}', bases, source)
    return families


def file_text(frames: list[dict]) -> str:
    """One compact, key-sorted JSON object per line; floats keep every bit (repr), including -0.0."""
    return ''.join(json.dumps(f, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n' for f in frames)


def write(families: dict[str, list[dict]], out: Path) -> dict[str, str]:
    """Write each family and SHA256SUMS; return {relative path: sha256}."""
    (out / 'frames').mkdir(parents=True, exist_ok=True)
    sums = {}
    for name, frames in sorted(families.items()):
        relative = f'frames/{name.replace(":", "__")}.jsonl'
        data = file_text(frames).encode('utf-8')
        (out / relative).write_bytes(data)
        sums[relative] = hashlib.sha256(data).hexdigest()
    (out / 'SHA256SUMS').write_text(''.join(f'{h}  {p}\n' for p, h in sorted(sums.items())), encoding='utf-8')
    return sums


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.split('\n\n')[1], file=sys.stderr)
        return 2
    abreg = json.loads(Path(argv[0]).read_text(encoding='utf-8'))
    families = {**fixed_inputs(abreg), **fixed_families(abreg), **seeded_families(abreg)}
    for path, digest in write(families, Path(argv[1])).items():
        print(f'{digest}  {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
