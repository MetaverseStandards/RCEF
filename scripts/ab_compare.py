#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run the A/B comparison of the pivot route (B) with today's direct maps (A1) and the other arms.

Usage:
  python scripts/ab_compare.py draft OUT.abreg [--b-pack PACK] [--date YYYY-MM-DD]
  python scripts/ab_compare.py run ABREG OUT_DIR [--b-pack PACK] [--dry-run]
  python scripts/ab_compare.py check
  python scripts/ab_compare.py a1-loss

- draft writes a first registration with every pin and A1 figure it can
  compute. Write it outside ab/, complete and review it, then commit it to
  ab/ and, in a later commit, its line in ab/FREEZES (ab/README.md).
- run checks the registration's pins, makes its frames (scripts/ab_frames.py),
  runs every arm and writes the results to OUT_DIR. A run whose pins do not
  match is refused, unless --dry-run, which marks the results unregistered.
- check prints every way ab/FREEZES, the registrations and the results break
  the rules in ab/README.md. tests/test_ab_registration.py runs it.
- a1-loss prints A1's observed loss on the fixed impulse frames (metric M4).

Freeze IDs, hashes and paths go only in the run manifest, never in
scoreboard.md or a metric CSV, so a "reproduce" run can match the results of
the freeze it reproduces byte for byte. Timings go to timings.json, which no
hash covers.
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'examples'), str(ROOT / 'scripts'), str(ROOT / 'tests')]
import ab_a3  # noqa: E402
import ab_frames  # noqa: E402
import ab_oracle  # noqa: E402
import check  # noqa: E402
import facs_codec  # noqa: E402
import rcef_route  # noqa: E402
import rcef_translate  # noqa: E402

A1_FIXTURE = 'tests/fixtures/baseline-dea1713.pack.json'
A1_SHA256 = '630d37a5b01e4983f8e5cbcbd54d8268abeffb09248ea793d4842bd2df5cd4f7'
A1_COMMIT = 'dea171370bba25dda3aa6b9846a346b5fca43aa5'
B_PACK = 'generated/rcef.pack.json'
LEDGER = 'ab/FREEZES'
RESULTS = 'ab/results'
FORMAT = 'rcef.ab/1'
FIRST = 'ab.pivot'
KINDS = ('first', 'new', 'fix', 'revise', 'reproduce')
CODE = {'route': 'examples/rcef_route.py', 'compare': 'scripts/ab_compare.py', 'generator': 'scripts/ab_frames.py',
        'oracle': 'tests/ab_oracle.py', 'codec': 'examples/facs_codec.py',
        'codec_data': 'examples/data/facs_codes.json', 'a3': 'tests/ab_a3.py'}
FB2 = ('openxr.fb2.XR_FACE_EXPRESSION2_', '_FB')
VISEMES = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')
ARKIT = 'arkit.coefficient.'
A1_PAIRS = {'FB2 -> ARKit': ('openxr.fb2', 'arkit.coefficient', ['fb2.to_arkit', 'fb2_gaze.to_arkit']),
            'ARKit -> FB2': ('arkit.coefficient', 'openxr.fb2', ['arkit.to_fb2', 'arkit_gaze.to_fb2']),
            'ARKit -> VRCFT UE': ('arkit.coefficient', 'vrcft.artist.base', ['arkit.to_vrcft_artist']),
            'FB2 -> VRM blink': ('openxr.fb2', 'vrm.preset', ['fb2.to_vrm']),
            'META -> VRM': ('openxr.visemes', 'vrm.preset', ['visemes.to_vrm'])}
A2_PAIRS = {'FB2 -> VRCFT UE': [('openxr.fb2', 'arkit.coefficient', ['fb2.to_arkit', 'fb2_gaze.to_arkit']),
                                ('arkit.coefficient', 'vrcft.artist.base', ['arkit.to_vrcft_artist'])],
            'ARKit -> VRM blink': [('arkit.coefficient', 'openxr.fb2', ['arkit.to_fb2']),
                                   ('openxr.fb2', 'vrm.preset', ['fb2.to_vrm'])]}
# Every pair B may run; a registration freezes the maps of those the B pack can route.
B_PAIRS = {**{name: (s, t) for name, (s, t, _) in A1_PAIRS.items()},
           'FB2 -> VRCFT UE': ('openxr.fb2', 'vrcft.artist.base'),
           'ARKit -> VRM blink': ('arkit.coefficient', 'vrm.preset'),
           'FACS -> FB2': ('facs.code', 'openxr.fb2'), 'FACS -> ARKit': ('facs.code', 'arkit.coefficient'),
           'FACS -> VRCFT UE': ('facs.code', 'vrcft.artist.base'), 'FACS -> VRM blink': ('facs.code', 'vrm.preset'),
           'ARKit -> FACS': ('arkit.coefficient', 'facs.code'), 'FB2 -> FACS': ('openxr.fb2', 'facs.code'),
           'VRCFT eye -> FACS': ('vrcft.eye', 'facs.code'), 'VRM -> FACS': ('vrm.preset', 'facs.code'),
           'VRCFT eye -> ARKit': ('vrcft.eye', 'arkit.coefficient'), 'VRCFT eye -> FB2': ('vrcft.eye', 'openxr.fb2'),
           'VRCFT eye -> VRCFT UE': ('vrcft.eye', 'vrcft.artist.base'), 'VRCFT eye -> VRM': ('vrcft.eye', 'vrm.preset'),
           'VRM -> ARKit': ('vrm.preset', 'arkit.coefficient'), 'VRM -> FB2': ('vrm.preset', 'openxr.fb2'),
           'VRM -> META': ('vrm.preset', 'openxr.visemes'),
           **{f'{n} -> {n}': (p, p) for n, p in (('ARKit', 'arkit.coefficient'), ('FB2', 'openxr.fb2'),
                                                ('META', 'openxr.visemes'), ('VRM', 'vrm.preset'),
                                                ('VRCFT eye', 'vrcft.eye'), ('FACS', 'facs.code'))}}
A1_SOURCES = ('openxr.fb2', 'arkit.coefficient', 'openxr.visemes')
GOLDEN_KINDS = {'fb2_to_arkit': 'openxr.fb2', 'arkit_to_fb2': 'arkit.coefficient', 'arkit_to_ue': 'arkit.coefficient',
                'fb2_to_vrm': 'openxr.fb2', 'visemes_to_vrm': 'openxr.visemes'}
GOLDEN_PAIRS = {'fb2_to_arkit': 'FB2 -> ARKit', 'arkit_to_fb2': 'ARKit -> FB2', 'arkit_to_ue': 'ARKit -> VRCFT UE',
                'fb2_to_vrm': 'FB2 -> VRM blink', 'visemes_to_vrm': 'META -> VRM'}
CSV_INPUTS = [('examples/data/fb2_demo_frames.csv', 'openxr.fb2', *FB2),
              ('examples/data/fb2_expression_frames.csv', 'openxr.fb2', *FB2),
              ('examples/data/viseme_demo_frames.csv', 'openxr.visemes', *VISEMES),
              ('examples/data/viseme_talk_frames.csv', 'openxr.visemes', *VISEMES)]
# The seeded families and their default sizes (ab/README.md). A family whose source the B pack cannot route is
# left out of a draft.
UNIT = [0.0, 1.0]
FAMILIES = [{'name': 'fb2_contract', 'kind': 'fb2_contract', 'source': 'openxr.fb2', 'count': 2000, 'range': UNIT},
            {'name': 'fb2_breaking', 'kind': 'uniform', 'source': 'openxr.fb2', 'count': 2000, 'range': UNIT},
            {'name': 'arkit_uniform', 'kind': 'uniform', 'source': 'arkit.coefficient', 'count': 2000, 'range': UNIT},
            {'name': 'viseme_simplex', 'kind': 'simplex', 'source': 'openxr.visemes', 'count': 500, 'decimals': 6},
            {'name': 'vrm', 'kind': 'vrm', 'source': 'vrm.preset', 'count': 200, 'range': UNIT,
             'blink': 'vrm.preset.blink',
             'vowels': [f'vrm.preset.{v}' for v in ('aa', 'ih', 'ou', 'ee', 'oh')]},
            {'name': 'vrcft_eye', 'kind': 'uniform', 'source': 'vrcft.eye', 'count': 200, 'range': UNIT,
             'outside': {'every': 10, 'channels': ['vrcft.eye.Left.Openness', 'vrcft.eye.Right.Openness'],
                         'values': [1.2, -0.1]}},
            {'name': 'facs_uniform', 'kind': 'uniform', 'source': 'facs.code', 'count': 2000, 'range': UNIT},
            {'name': 'facs_letters', 'kind': 'facs_letters', 'count': 500, 'values': list(ab_frames.LETTER_VALUES)}]
PERTURB_BASES = 4
# FACS channels that A3 and B share: every mapped facs.code signal but AU19 and AU43, which A3's table lacks.
FACS_UNSHARED = ('facs.code.au19', 'facs.code.au43_left', 'facs.code.au43_right')
FACS_MAPPED, FACS_SHARED = 49, 46
# Outputs that the FACS route cannot write but A3 (and A3 then A1) writes as zero or from AU61-64 (M10, M10b).
M10_NOT_AVAILABLE = [f'{FB2[0]}{c}{FB2[1]}' for c in (
    'MOUTH_LEFT', 'MOUTH_RIGHT', 'CHIN_RAISER_T', 'TONGUE_RETREAT', 'TONGUE_TIP_INTERDENTAL', 'TONGUE_TIP_ALVEOLAR',
    'TONGUE_FRONT_DORSAL_PALATE', 'TONGUE_MID_DORSAL_PALATE', 'TONGUE_BACK_DORSAL_VELAR',
    *(f'EYES_LOOK_{d}_{s}' for d in ('LEFT', 'RIGHT', 'UP', 'DOWN') for s in 'LR'))]
M10B_NOT_AVAILABLE = [ARKIT + c for c in ('mouthLeft', 'mouthRight', 'mouthShrugUpper', *(
    f'eyeLook{d}{s}' for d in ('In', 'Out', 'Up', 'Down') for s in ('Left', 'Right')))]
# FB2 gaze outputs on the negative knot segment: fl(1 - fl(1 - b)) rounds, so M3 reports their error.
M3_ROUNDING = [f'{FB2[0]}EYES_LOOK_{c}_FB' for c in ('LEFT_L', 'RIGHT_R', 'DOWN_L', 'DOWN_R')]
TINY = 2.0 ** -1020
THRESHOLDS = {
    'M1': 'B equals A1 on every output both write, sign of zero included; on the edge set B equals O',
    'M1s': 'exact Fraction composition of B equals A1 on every linear A1 output',
    'B equals O': 'B gives the oracle\'s values, bit for bit, refusal codes and labels on every frame of every pair',
    'M2': "in every frame B's refused outputs are among A1's, B writes every output A1 writes, dropped inputs equal",
    'M2c': "for every A1 output, B's hop evidence holds every evidence ID of the A1 rules that write it",
    'M3': 'round trips exact on the listed channels; B equals O on every round-trip and impulse frame; every '
          'reached output non-zero on at least 1% of each seeded family that sets a linked input',
    'M4': 'B observed loss 0; A1 observed loss equals the registered baseline',
    'M5': 'R1: 129 of 129 goldens exact through B; R2: composed B weights equal the 52 rows but the listed departures',
    'M10': 'FACS -> FB2: B equals A3 on outputs both write; coverage list frozen; B refuses 0 frames',
    'M10b': 'FACS -> ARKit: B equals A3 then A1 on outputs both write; coverage list frozen',
}
# Gates these tools cannot compute yet: their frozen tables come from the definitions audit and the canonical data.
PENDING = {'M4 keys': 'the rule-scoped reason -> key table', 'M4b': 'the assumption catalogue',
           'M6': 'the geometry harness', 'M7': 'the mutation set', 'M11': 'B ARKit -> FACS links and the R5 table',
           'M8 R3': 'the R3 goldens'}


# ---------------------------------------------------------------- hashes, files and pins

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> str:
    """Compact, key-sorted JSON, as check.py hashes a calibration record."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def abreg_sha256(abreg: dict) -> str:
    """The hash a ledger line records: of the whole registration, seed_root included, laid out canonically."""
    return sha256_bytes(canonical(abreg).encode('utf-8'))


def seed_root(abreg: dict) -> str:
    """For a first, new, fix or revise freeze: the hash of its own registration without seed_root."""
    return sha256_bytes(canonical({k: v for k, v in abreg.items() if k != 'seed_root'}).encode('utf-8'))


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)


def load_a1(root: Path = ROOT) -> dict:
    """The A1 pack document from the committed fixture, after its hash and, where history exists, a Git cross-check."""
    data = (root / A1_FIXTURE).read_bytes()
    if sha256_bytes(data) != A1_SHA256:
        raise SystemExit(f'{A1_FIXTURE} does not have the pinned SHA-256 {A1_SHA256}')
    shown = subprocess.run(['git', 'show', f'{A1_COMMIT}:generated/rcef.pack.json'], cwd=root, capture_output=True)
    if shown.returncode == 0 and shown.stdout != data:
        raise SystemExit(f'{A1_FIXTURE} is not generated/rcef.pack.json at {A1_COMMIT[:7]}')
    return json.loads(data)


def code_hashes(root: Path = ROOT) -> dict:
    return {name: sha256_bytes((root / path).read_bytes()) for name, path in CODE.items()}


def runtime_pins(root: Path = ROOT) -> dict:
    from importlib import metadata
    lock = json.loads((root / 'evidence/tooling.lock.json').read_text(encoding='utf-8'))
    dist = metadata.distribution(check.DISTRIBUTION)
    tag = next((t for t in check.installed_tags(dist) if t in lock['wheels']), None)
    return {'wheel': f'{check.PACKAGE}-{dist.version}-{tag}.whl',
            'wheel_sha256': lock['wheels'][tag]['sha256'] if tag else None,
            'python': platform.python_version(), 'platform': f'{sys.platform}-{platform.machine()}'}


# ---------------------------------------------------------------- running arms

def run_route(route: rcef_route.Route, frames: list[dict]) -> list[dict]:
    return route.translate([{**f, 'time': 0.0} for f in frames])


def chain(routes: list[rcef_route.Route], frames: list[dict]) -> list[dict]:
    """Two direct hops in turn (A2, A3 then A1): each later hop reads the earlier hop's values as valid inputs."""
    results = run_route(routes[0], frames)
    for route in routes[1:]:
        flags = sorted({f.strip() for s in route.signals.values() if s.get('validity')
                        for f in s['validity'].split(' AND ')})
        later = run_route(route, [{'values': r['values'], 'flags': dict.fromkeys(flags, True)} for r in results])
        results = [{**b, 'refused': {**a['refused'], **b['refused']}, 'dropped': a['dropped']}
                   for a, b in zip(results, later)]
    return results


def bits(value: float) -> bytes:
    return struct.pack('>d', value)


def facs_values(frames: list[dict]) -> list[dict]:
    """B's facs.code frames for FACS key frames, read by the shipped codec; a refused reading gives no values."""
    out = []
    for frame in frames:
        reading = facs_codec.read(frame['keys'])
        out.append({**frame, 'values': reading.values or {}, 'flags': {}})
    return out


# ---------------------------------------------------------------- metrics

def refused_outputs(result: dict) -> set:
    return {o for o, label in result['labels'].items() if label.startswith('refused')}


def m1(a1: list[dict], b: list[dict]) -> tuple[dict, list]:
    """Value and sign-of-zero differences on outputs both arms write."""
    counts, failures = {'compared': 0, 'value_differences': 0, 'sign_differences': 0}, []
    for n, (x, y) in enumerate(zip(a1, b, strict=True)):
        for output in sorted(x['values'].keys() & y['values'].keys()):
            counts['compared'] += 1
            u, v = x['values'][output], y['values'][output]
            if u != v:
                counts['value_differences'] += 1
                failures.append([n, output, repr(u), repr(v)])
            elif bits(u) != bits(v):
                counts['sign_differences'] += 1
                failures.append([n, output, repr(u), repr(v)])
    return counts, failures


def m2(a1: list[dict], b: list[dict]) -> tuple[dict, list]:
    """B refuses no output A1 writes or does not refuse, writes every output A1 writes, and drops the same inputs."""
    counts, failures = {'frames': len(a1), 'violations': 0}, []
    for n, (x, y) in enumerate(zip(a1, b, strict=True)):
        problems = [f'refused {o}' for o in sorted(refused_outputs(y) - refused_outputs(x))]
        problems += [f'not written {o}' for o in sorted(set(x['values']) - set(y['values']))]
        if x['dropped'] != y['dropped']:
            problems.append('dropped inputs differ')
        if problems:
            counts['violations'] += 1
            failures.append([n, '; '.join(problems)])
    return counts, failures


def oracle_results(oracle: ab_oracle.Oracle, pair: dict, frames: list[dict]) -> list[dict]:
    return [oracle.route(pair['source'], pair['target'], [tuple(h) for h in pair['in_hops']],
                         [tuple(h) for h in pair['out_hops']], f['values'], f['flags']) for f in frames]


def equals_oracle(b: list[dict], o: list[dict]) -> tuple[dict, list]:
    """B's values (bit for bit), refusals by map (codes and references) and labels equal O's."""
    counts, failures = {'frames': len(b), 'differences': 0}, []
    for n, (x, y) in enumerate(zip(b, o, strict=True)):
        if ({k: bits(v) for k, v in x['values'].items()} != {k: bits(v) for k, v in y['values'].items()}
                or x['refused'] != y['refused'] or x['labels'] != y['labels']):
            counts['differences'] += 1
            failures.append([n, json.dumps(x['refused'], sort_keys=True), json.dumps(y['refused'], sort_keys=True)])
    return counts, failures


def impulse_channel(frame: dict) -> str | None:
    """The one non-zero channel of an impulse frame, or None for the all-zero frame."""
    hot = [k for k, v in frame['values'].items() if v]
    return hot[0] if len(hot) == 1 else None


def observed_loss(results: list[dict], frames: list[dict], declared=()) -> list[str]:
    """Source inputs whose impulse frames change no output, and that are not dropped, not available or declared.

    frames[0] is the all-zero frame, as ab_frames.impulse_family makes it.
    """
    hits = {}
    for n, frame in enumerate(frames[1:], 1):
        hits.setdefault(impulse_channel(frame), []).append(n)
    lost = []
    for sid, frames_of in hits.items():
        if sid is None or sid in declared:
            continue
        if any(ab_oracle.changed(results[0], results[n]) for n in frames_of):
            continue
        if all(sid in results[n]['dropped'] for n in frames_of):
            continue
        lost.append(sid)
    return lost


def rules_by_output(document: dict, maps: list[str]) -> dict:
    return {r['outputs'][0]: r for m in document['mappings'] if m['id'] in maps for r in m['rules']}


def upstream(rules: dict, sid: str) -> tuple[list[dict], set]:
    """The rules a value depends on within a map, and the inputs at their far end."""
    found, leaves, todo = [], set(), [sid]
    while todo:
        current = todo.pop()
        rule = rules.get(current)
        if rule is None:
            leaves.add(current)
            continue
        found.append(rule)
        todo += rule['inputs']
    return found, leaves


def linear_form(rules: dict, sid: str):
    """An output as exact constant + sum of Fraction weights over the inputs, or None through a piecewise operator."""
    rule = rules.get(sid)
    if rule is None:
        return Fraction(0), {sid: Fraction(1)}
    operator = rule['operator']
    terms = []
    if operator['id'] in ('identity', 'affine'):
        terms = [(Fraction(operator.get('scale', 1.0)), rule['inputs'][0])]
        constant = Fraction(operator.get('offset', 0.0))
    elif operator['id'] == 'weighted_sum':
        terms, constant = list(zip(map(Fraction, operator['weights']), rule['inputs'])), Fraction(0)
    else:
        return None
    weights = {}
    for weight, sid_in in terms:
        form = linear_form(rules, sid_in)
        if form is None:
            return None
        constant += weight * form[0]
        for leaf, w in form[1].items():
            weights[leaf] = weights.get(leaf, 0) + weight * w
    return constant, {k: v for k, v in weights.items() if v}


def compose(outer, inner_forms: dict):
    """Substitute each canonical leaf of an out-hop form by its in-hop form; None if any part is not linear."""
    if outer is None:
        return None
    constant, weights = outer[0], {}
    for leaf, w in outer[1].items():
        inner = inner_forms.get(leaf)
        if inner is None:
            return None
        constant += w * inner[0]
        for source, v in inner[1].items():
            weights[source] = weights.get(source, 0) + w * v
    return constant, {k: v for k, v in weights.items() if v}


def b_forms(document: dict, pair: dict) -> dict:
    """The composed linear form of every B output of a pair, or None where it is not linear."""
    out_rules = rules_by_output(document, [h[0] for h in pair['out_hops']])
    in_rules = rules_by_output(document, [h[0] for h in pair['in_hops']])
    outputs = [o for h in pair['out_hops'] for o in rcef_route.map_ends(
        next(m['rules'] for m in document['mappings'] if m['id'] == h[0]))[1]]
    inner = {}
    forms = {}
    for output in outputs:
        outer = linear_form(out_rules, output)
        if outer is not None:
            for leaf in outer[1]:
                if leaf not in inner:
                    inner[leaf] = linear_form(in_rules, leaf) if pair['in_hops'] else (Fraction(0), {leaf: Fraction(1)})
        forms[output] = compose(outer, inner) if pair['in_hops'] else outer
    return forms


def m1s(a1_document: dict, b_document: dict, pair_name: str, pair: dict) -> tuple[dict, list]:
    _, _, maps = A1_PAIRS[pair_name]
    a1_rules = rules_by_output(a1_document, maps)
    forms = b_forms(b_document, pair)
    counts, failures = {'linear_outputs': 0, 'differences': 0}, []
    for output in forms:
        expected = linear_form(a1_rules, output) if output in a1_rules else None
        if expected is None:
            continue
        counts['linear_outputs'] += 1
        if forms[output] != expected:
            counts['differences'] += 1
            failures.append([output, str(expected), str(forms[output])])
    return counts, failures


def m2c(a1_document: dict, b_document: dict, pair_name: str, pair: dict) -> tuple[dict, list]:
    """For every A1 output, the evidence IDs of the A1 rules that write it, less those of B's hops: must be empty."""
    _, _, maps = A1_PAIRS[pair_name]
    a1_rules = rules_by_output(a1_document, maps)
    out_rules = rules_by_output(b_document, [h[0] for h in pair['out_hops']])
    in_rules = rules_by_output(b_document, [h[0] for h in pair['in_hops']])
    counts, failures = {'outputs': 0, 'shortfall': 0}, []
    for output in sorted(o for o in a1_rules if o in out_rules):
        counts['outputs'] += 1
        a1_evidence = {e for r in upstream(a1_rules, output)[0] for e in r['evidence']}
        found, leaves = upstream(out_rules, output)
        found += [r for leaf in leaves for r in upstream(in_rules, leaf)[0]]
        missing = a1_evidence - {e for r in found for e in r['evidence']}
        if missing:
            counts['shortfall'] += len(missing)
            failures.append([output, ' '.join(sorted(missing))])
    return counts, failures


def m2b(a1_document: dict, b_document: dict, pair_name: str, pair: dict) -> dict:
    """Report only: the evidence statuses of the rules on each path."""
    _, _, maps = A1_PAIRS[pair_name]
    a1 = sorted({r['evidence_status'] for r in rules_by_output(a1_document, maps).values()})
    b = sorted({r['evidence_status'] for h in pair['in_hops'] + pair['out_hops']
                for r in rules_by_output(b_document, [h[0]]).values()})
    return {'a1': ' '.join(a1), 'b': ' '.join(b)}


def m3_exact(frames: list[dict], back: list[dict], source: dict) -> tuple[dict, list]:
    """X -> C -> X: 0 error on every written channel, except the rounding outputs on exclusive frames and every gaze
    output on frames that break FB2's exclusivity; values below 2**-1020 are not claimed."""
    counts = {'frames': len(frames), 'non_exclusive_frames': 0, 'errors': 0, 'max_excluded_error': 0.0,
              'excluded_became_zero': 0}
    failures, gaze = [], {s for pair in source['gaze_pairs'] for s in pair}
    for n, (frame, result) in enumerate(zip(frames, back, strict=True)):
        exclusive = not any(frame['values'].get(a) and frame['values'].get(b) for a, b in source['gaze_pairs'])
        counts['non_exclusive_frames'] += not exclusive
        excluded = set(M3_ROUNDING) if exclusive else gaze
        for sid, value in result['values'].items():
            original = frame['values'].get(sid)
            if original is None:
                continue
            if sid in excluded or 0 < abs(original) < TINY:
                counts['max_excluded_error'] = max(counts['max_excluded_error'], abs(value - original))
                counts['excluded_became_zero'] += value == 0 and original != 0
            elif value != original:
                counts['errors'] += 1
                failures.append([n, sid, repr(original), repr(value)])
    return counts, failures


def links(document: dict, pair: dict, outputs) -> dict:
    """Each (source input, output) link of the composed hop weights: True when a piecewise operator is on the way."""
    out_rules = rules_by_output(document, [h[0] for h in pair['out_hops']])
    in_rules = rules_by_output(document, [h[0] for h in pair['in_hops']])
    found = {}
    for output in outputs:
        rules, leaves = upstream(out_rules, output)
        if pair['in_hops']:
            inner = [(leaf, upstream(in_rules, leaf)) for leaf in leaves if leaf in in_rules]
            rules = rules + [r for _, (more, _) in inner for r in more]
            leaves = {s for _, (_, sources) in inner for s in sources}
        knots = any(r['operator']['id'] == 'piecewise_linear' for r in rules)
        found.update({(s, output): knots for s in leaves})
    return found


def flat_links(document: dict, pair: dict, impulse: list[dict], o: list[dict]) -> list[list[str]]:
    """The links O never changes on the impulse frames because they enter a piecewise operator on its flat side."""
    changed = {}
    for n in range(1, len(impulse)):
        changed.setdefault(impulse_channel(impulse[n]), set()).update(ab_oracle.changed(o[0], o[n]))
    return sorted([s, out] for (s, out), knots in links(document, pair, o[0]['values']).items()
                  if knots and out not in changed.get(s, set()))


def m3_coverage(document: dict, pair: dict, impulse: list[dict], b: list[dict], o: list[dict], flat: list,
                seeded: dict) -> tuple[dict, list]:
    """Impulse frames change exactly O's outputs; every composed link is in O's set or the frozen flat list; every
    reached output is non-zero on at least 1% of each seeded family of the pair's source."""
    counts, failures = {'impulse_frames': len(impulse) - 1, 'violations': 0}, []
    changed_b = {}
    for n in range(1, len(impulse)):
        sid = impulse_channel(impulse[n])
        got, want = ab_oracle.changed(b[0], b[n]), ab_oracle.changed(o[0], o[n])
        changed_b.setdefault(sid, set()).update(got)
        if got != want:
            counts['violations'] += 1
            failures.append([impulse[n]['label'], 'changed outputs differ from O'])
    linked = sorted(links(document, pair, b[0]['values']))
    for s, output in linked:
        if output not in changed_b.get(s, set()) and [s, output] not in flat:
            counts['violations'] += 1
            failures.append([f'{s} -> {output}', 'linked but never changed, and not in the flat list'])
    for name, results in seeded.items():
        for output in sorted({o for s, o in linked}):
            share = sum(bool(r['values'].get(output)) for r in results) / max(len(results), 1)
            if share < 0.01:
                counts['violations'] += 1
                failures.append([f'{name}: {output}', f'non-zero on {share:.4f} of the frames'])
    return counts, failures


def facs_compare(b: list[dict], expected: list[dict], not_available: list[str]) -> tuple[dict, list]:
    """M10 and M10b: values on outputs both write, B's coverage equal to the frozen list, and B's refusals."""
    counts = {'frames': len(b), 'value_differences': 0, 'coverage_violations': 0, 'b_refusals': 0}
    failures = []
    for n, (x, values) in enumerate(zip(b, expected, strict=True)):
        counts['b_refusals'] += bool(x['refused'])
        for output in sorted(x['values'].keys() & values.keys()):
            if bits(x['values'][output]) != bits(values[output]):
                counts['value_differences'] += 1
                failures.append([n, output, repr(values[output]), repr(x['values'][output])])
        # The outputs B leaves unwritten must be exactly the frozen list, each labelled "not available".
        unwritten = set(values) - set(x['values'])
        wrong = (unwritten ^ set(not_available)) | {
            o for o in unwritten if x['labels'].get(o) != rcef_route.NOT_AVAILABLE}
        extra = set(x['values']) - set(values)
        if wrong or extra:
            counts['coverage_violations'] += 1
            failures.append([n, 'coverage', ' '.join(sorted(wrong | extra)), ''])
    return counts, failures


def r1(b_runs: dict, goldens: dict) -> tuple[dict, list]:
    """M5 R1: each golden case through B gives exactly its expected values."""
    counts, failures = {'cases': 0, 'exact': 0, 'not_run': 0}, []
    for n, case in enumerate(goldens['cases']):
        counts['cases'] += 1
        results = b_runs.get(GOLDEN_PAIRS[case['mapping_kind']])
        if results is None:
            counts['not_run'] += 1
            continue
        result = results.pop(0)
        if all(o in result['values'] and bits(result['values'][o]) == bits(v) for o, v in case['expected'].items()):
            counts['exact'] += 1
        else:
            failures.append([n, case['mapping_kind'], json.dumps(case['expected'], sort_keys=True)])
    return counts, failures


def r2(b_document: dict, pair: dict, rows: list[dict], departures: list[str]) -> tuple[dict, list]:
    """M5 R2: per ARKit output, the composed B weights equal the source-derived row, except the listed departures."""
    forms = b_forms(b_document, pair)
    counts, failures = {'rows': len(rows), 'equal': 0, 'departures': 0, 'differences': 0}, []
    for row in rows:
        expected = (Fraction(0), {f'{FB2[0]}{term.split("*")[0]}{FB2[1]}': Fraction(term.split('*')[1])
                                  for term in row['fb2_inputs'].split(';')})
        got = forms.get(ARKIT + row['arkit'])
        if got == expected:
            counts['equal'] += 1
        elif row['arkit'] in departures:
            counts['departures'] += 1
        else:
            counts['differences'] += 1
            failures.append([row['arkit'], str(expected), str(got)])
    return counts, failures


# ---------------------------------------------------------------- A1 figures (fixed inputs only)

def a1_figures(abreg: dict, document: dict) -> dict:
    """A1's edge-set refusals and observed loss on the fixed families: nothing here reads seed_root."""
    pack = rcef_translate.load_pack(document)
    fixed = ab_frames.fixed_families(abreg)
    figures = {'edge_refusals': {}, 'observed_loss': {}}
    for pair, (source, target, maps) in A1_PAIRS.items():
        route = rcef_route.Route(source, target, pack=pack, maps=maps)
        edge = run_route(route, fixed[f'edge:{source}'])
        figures['edge_refusals'][pair] = {str(n): {m: r['codes'] for m, r in result['refused'].items()}
                                          for n, result in enumerate(edge) if result['refused']}
        impulse = fixed[f'impulse:{source}']
        figures['observed_loss'][pair] = observed_loss(run_route(route, impulse), impulse)
    return figures


# ---------------------------------------------------------------- drafts

def b_pairs(document: dict) -> dict:
    """The maps of every B pair the pack can route, with each hop's canonical profile."""
    pack, pairs = rcef_translate.load_pack(document), {}
    profiles = {p['id'] for p in document['profiles']}
    for name, (source, target) in B_PAIRS.items():
        if source not in profiles or target not in profiles:
            continue
        route = rcef_route.Route(source, target, pack=pack)
        if route.in_maps and route.out_maps:
            pairs[name] = {'source': source, 'target': target,
                           'in_hops': [[m, dst] for m, _, dst in route.hops if m in route.in_maps],
                           'out_hops': [[m, src] for m, src, _ in route.hops if m in route.out_maps]}
    return pairs


def pinned_sources(a1: dict, b_document: dict, pairs: dict) -> dict:
    """The A1 source sets from the A1 fixture; the sets only B reads from the B pack."""
    sources = {p: ab_frames.pinned_source(a1, p) for p in A1_SOURCES}
    for pair in pairs.values():
        if pair['source'] not in sources:
            sources[pair['source']] = ab_frames.pinned_source(b_document, pair['source'],
                                                              mapped_only=pair['source'] == 'facs.code')
    if 'facs.code' in sources and len(sources['facs.code']['channels']) != FACS_MAPPED:
        raise SystemExit(f'facs.code has {len(sources["facs.code"]["channels"])} mapped signals, not {FACS_MAPPED}')
    return sources


def registered_families(sources: dict) -> list[dict]:
    """The seeded families whose source set is pinned, with the FACS letter family's channels."""
    families = []
    for spec in FAMILIES:
        if spec['kind'] == 'facs_letters':
            if 'facs.code' in sources:
                channels = [s for s in sources['facs.code']['channels'] if s not in FACS_UNSHARED]
                if len(channels) != FACS_SHARED:
                    raise SystemExit(f'the FACS letter family has {len(channels)} channels, not {FACS_SHARED}')
                families.append({**spec, 'channels': channels})
        elif spec['source'] in sources:
            families.append(spec)
    return families


def draft(root: Path = ROOT, b_path: Path | None = None, date: str = '') -> dict:
    """A first registration (ab.pivot v1) with every pin the tools can compute; the audit and data fill the lists."""
    a1 = load_a1(root)
    b_path = b_path or root / B_PACK
    b_document = json.loads(b_path.read_text(encoding='utf-8'))
    pairs = b_pairs(b_document)
    sources = pinned_sources(a1, b_document, pairs)
    families = registered_families(sources)
    codes = facs_codec.table()['codes']
    keys = {'sided': [c for c, e in codes.items() if e['read'] == 'sided' and c != '43'],
            'shared': [c for c, e in codes.items() if e['read'] == 'shared' and c != '19'],
            'directions': [f'{s}{c}' for c, e in codes.items() if e['read'] == 'direction' for s in 'LR']}
    abreg = {
        'format': FORMAT, 'id': FIRST, 'version': 1, 'kind': 'first', 'date': date,
        'seed_rule': ab_frames.SEED_RULE, 'sources': sources, 'families': families,
        'perturbations': [{'family': f['name'], 'bases': PERTURB_BASES} for f in families
                          if f['kind'] != 'facs_letters'],
        'fixed_inputs': {
            'goldens': {'path': 'tests/fixtures/fb2_goldens.json', 'kinds': GOLDEN_KINDS,
                        'sha256': sha256_bytes((root / 'tests/fixtures/fb2_goldens.json').read_bytes())},
            'csv': [{'path': p, 'source': s, 'prefix': pre, 'suffix': suf,
                     'sha256': sha256_bytes((root / p).read_bytes())} for p, s, pre, suf in CSV_INPUTS],
            'facs_keys': keys,
            'a3': ab_a3.SHA256},
        'pairs': pairs,
        'metrics': THRESHOLDS,
        'lists': {'intended_differences': [], 'a1_loss_corrections': [], 'audit_added_keys': [], 'side_exceptions': [],
                  'reason_key_table': {}, 'assumption_catalogue': {}, 'no_target': [], 'r3': [],
                  'r2_departures': ['browInnerUp'], 'm3_flat_links': [], 'm3_rounding': M3_ROUNDING,
                  'm10_not_available': M10_NOT_AVAILABLE, 'm10b_not_available': M10B_NOT_AVAILABLE,
                  'm11_differences': []},
        'acceptance': {}, 'changes': [],
        'pins': {'a1_sha256': A1_SHA256, 'b_pack_sha256': sha256_bytes(b_path.read_bytes()),
                 'code': code_hashes(root), 'runtime': runtime_pins(root)},
        'not_registered': sorted(set(B_PAIRS) - set(pairs)),
    }
    oracle, fixed = ab_oracle.Oracle(b_document), ab_frames.fixed_families(abreg)
    flat = set()
    for pair in pairs.values():
        impulse = fixed[f'impulse:{pair["source"]}']
        flat |= {tuple(link) for link in flat_links(b_document, pair, impulse, oracle_results(oracle, pair, impulse))}
    abreg['lists']['m3_flat_links'] = sorted(map(list, flat))
    abreg['a1_figures'] = a1_figures(abreg, a1)
    abreg['seed_root'] = seed_root(abreg)
    return abreg


# ---------------------------------------------------------------- registration checks

def ledger_commit(root: Path, sha: str) -> str | None:
    """The first commit whose ab/FREEZES holds a hash."""
    found = git(root, 'log', '--reverse', '--format=%H', '-S', sha, '--', LEDGER)
    lines = found.stdout.split()
    return lines[0] if found.returncode == 0 and lines else None


def added_commit(root: Path, path: str) -> str | None:
    found = git(root, 'log', '--reverse', '--diff-filter=A', '--format=%H', '--', path)
    lines = found.stdout.split()
    return lines[0] if found.returncode == 0 and lines else None


def registration_problems(root: Path = ROOT, recompute: bool = True, history: bool | None = None) -> list[str]:
    """Every way the ledger, the registrations and the results break the rules in ab/README.md.

    `history` says whether to check the commit order; by default, when `root` is in a Git repository.
    """
    entries, problems = check.read_ledger(root / LEDGER)
    problems = [p.replace(check.LEDGER, LEDGER) for p in problems]
    abregs = {}
    for path in sorted((root / 'ab').glob('*.abreg')):
        abreg = json.loads(path.read_text(encoding='utf-8'))
        where = f'ab/{path.name}'
        key = (abreg.get('id'), abreg.get('version'))
        if path.name != f'{key[0]}-v{key[1]}.abreg':
            problems.append(f'{where} must be named <id>-v<version>.abreg')
        if abreg.get('format') != FORMAT or abreg.get('kind') not in KINDS:
            problems.append(f'{where} needs format {FORMAT} and a kind among {", ".join(KINDS)}')
            continue
        if entries.get(key) != abreg_sha256(abreg):
            problems.append(f'{where} has no line in {LEDGER} with its hash {abreg_sha256(abreg)}; every committed '
                            'registration needs one, abandoned ones included')
        abregs[key] = abreg
    for key in entries:
        if key not in abregs:
            problems.append(f'{LEDGER} has {key[0]} v{key[1]}, but ab/{key[0]}-v{key[1]}.abreg is missing; '
                            'registrations are never removed')
    if history is None:
        history = git(root, 'rev-parse', '--git-dir').returncode == 0
    manifests = {}
    for path in sorted((root / RESULTS).glob('*/manifest.json')):
        manifest = json.loads(path.read_text(encoding='utf-8'))
        manifests[manifest.get('id'), manifest.get('version')] = (path, manifest)
    for key, abreg in sorted(abregs.items(), key=lambda item: (item[0][0], item[0][1])):
        where = f'ab/{key[0]}-v{key[1]}.abreg'
        problems += [f'{where}: {p}' for p in abreg_problems(abreg, abregs, manifests, root, recompute)]
        registered = ledger_commit(root, abreg_sha256(abreg)) if history else None
        if registered:
            committed = added_commit(root, where)
            if not committed or committed == registered or not is_ancestor(root, committed, registered):
                problems.append(f'{where} must be committed before its line in {LEDGER}')
    for key, (path, manifest) in manifests.items():
        where = path.relative_to(root).as_posix()
        abreg = abregs.get(key)
        if abreg is None:
            problems.append(f'{where} names {key[0]} v{key[1]}, which has no registration')
            continue
        if manifest.get('abreg_sha256') != abreg_sha256(abreg) or manifest.get('kind') != abreg['kind']:
            problems.append(f'{where} must name the registration hash, version and freeze kind it ran')
        expected = f'v{key[1]}' if key[0] == FIRST else f'{key[0]}-v{key[1]}'
        if path.parent.name != expected:
            problems.append(f'{where} must be in {RESULTS}/{expected}/')
        if not history:
            continue
        registered, results = ledger_commit(root, abreg_sha256(abreg)), added_commit(root, where)
        if results and not registered:
            problems.append(f'{where} is committed, but its line in {LEDGER} is not committed')
        elif registered and results and (registered == results or not is_ancestor(root, registered, results)):
            problems.append(f'{where} was committed before, or with, its line in {LEDGER}')
    return problems


def is_ancestor(root: Path, older: str, newer: str) -> bool:
    return git(root, 'merge-base', '--is-ancestor', older, newer).returncode == 0


def abreg_problems(abreg: dict, abregs: dict, manifests: dict, root: Path, recompute: bool) -> list[str]:
    problems, version, kind = [], abreg['version'], abreg['kind']
    if version == 1 and kind not in ('first', 'new') or version > 1 and kind in ('first', 'new'):
        problems.append('v1 is a "first" freeze (ab.pivot) or a "new" A/B (any other id); later versions are fix, '
                        'revise or reproduce')
    if kind == 'first' and abreg['id'] != FIRST or kind == 'new' and abreg['id'] == FIRST:
        problems.append(f'a "first" freeze is {FIRST} v1; a new A/B needs a new id, such as ab.pivot2')
    previous = abregs.get((abreg['id'], version - 1))
    if kind == 'reproduce':
        target = abreg.get('reproduces', {})
        reproduced = abregs.get((target.get('id'), target.get('version')))
        manifest = manifests.get((target.get('id'), target.get('version')), (None, {}))[1]
        passing = [v for (i, v), other in abregs.items() if i == abreg['id'] and v < version
                   and other['kind'] in ('first', 'new', 'fix', 'revise') and manifests.get((i, v), (None, {}))[1].get(
                       'passed') and not manifests[(i, v)][1].get('dry_run')]
        if reproduced is None or not manifest.get('passed') or manifest.get('dry_run'):
            problems.append('a "reproduce" freeze must name a registered freeze whose results passed')
        elif target.get('id') != abreg['id'] or target.get('version') != max(passing, default=None):
            latest = f'{abreg["id"]} v{max(passing)}' if passing else 'a first, new, fix or revise freeze'
            problems.append(f'a "reproduce" freeze reproduces the latest passing freeze, {latest}')
        elif any(abreg.get(k) != reproduced.get(k) for k in ('seed_root', 'sources', 'families', 'perturbations')) or (
                abreg['pins']['code'].get('generator') != reproduced['pins']['code'].get('generator')
                or abreg['pins']['runtime'] != reproduced['pins']['runtime']):
            problems.append('a "reproduce" freeze copies the seed_root, generator, channel lists and runtime pins of '
                            'the freeze it reproduces')
    elif abreg.get('seed_root') != seed_root(abreg):
        problems.append('seed_root must be the SHA-256 of the registration without seed_root')
    if previous is not None:
        if abreg.get('metrics') != previous.get('metrics'):
            problems.append('thresholds must equal those of the previous freeze; only a new A/B sets its own')
        for name in sorted(set(abreg.get('lists', {})) | set(previous.get('lists', {}))):
            if abreg['lists'].get(name) != previous['lists'].get(name) and not abreg.get('acceptance', {}).get(name):
                problems.append(f'list {name} changed without the release owners\' acceptance in "acceptance"')
    if kind == 'fix' and not abreg.get('changes'):
        problems.append('a "fix" freeze names what changed in "changes"')
    if kind == 'revise' and (not abreg.get('changes') or not abreg.get('acceptance', {}).get('changes')):
        problems.append('a "revise" freeze lists each change, and the release owners accept the list before the run')
    if recompute and abreg.get('a1_figures') is not None:
        # Computed from the registration without its seed_root, so no figure can depend on it.
        unseeded = {k: v for k, v in abreg.items() if k != 'seed_root'}
        if a1_figures(unseeded, load_a1(root)) != abreg['a1_figures']:
            problems.append('its A1 figures are not what the fixed inputs give: no A1 figure may depend on seed_root')
    return problems


# ---------------------------------------------------------------- regression families

def generator_at(root: Path, digest: str):
    """The frame generator whose file has this SHA-256: the checkout's, or one from Git history; None if neither."""
    if sha256_bytes((root / CODE['generator']).read_bytes()) == digest:
        return ab_frames
    for commit in git(root, 'log', '--format=%H', '--', CODE['generator']).stdout.split():
        shown = subprocess.run(['git', 'show', f'{commit}:{CODE["generator"]}'], cwd=root, capture_output=True)
        if shown.returncode == 0 and sha256_bytes(shown.stdout) == digest:
            module = types.ModuleType(f'ab_frames_{commit[:12]}')
            module.__file__ = str(root / CODE['generator'])
            # The generator uses only the standard library, so its old text runs on its own.
            exec(compile(shown.stdout, f'{CODE["generator"]} at {commit[:12]}', 'exec'), module.__dict__)
            return module
    return None


def results_folder(abreg: dict) -> str:
    return f'v{abreg["version"]}' if abreg['id'] == FIRST else f'{abreg["id"]}-v{abreg["version"]}'


def regression_families(abreg: dict, root: Path = ROOT) -> tuple[dict, dict, list[str]]:
    """The seeded families of every earlier freeze, made again by the generator each one pinned.

    Only a fix or revise freeze, or a reproduce freeze of one, has them. Their
    frame hashes must equal the earlier run's SHA256SUMS, where it exists. A
    rename map in the registration ("renames") is applied to their signal IDs.
    Returns the families, the source set of each and any problems.
    """
    target = abreg
    if abreg['kind'] == 'reproduce':
        reproduced = root / 'ab' / f'{abreg["reproduces"]["id"]}-v{abreg["reproduces"]["version"]}.abreg'
        target = json.loads(reproduced.read_text(encoding='utf-8'))
    if target['kind'] not in ('fix', 'revise'):
        return {}, {}, []
    families, sources, problems = {}, {}, []
    renames = abreg.get('renames', {})
    for version in range(1, target['version']):
        path = root / 'ab' / f'{target["id"]}-v{version}.abreg'
        earlier = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
        if earlier is None or earlier['kind'] == 'reproduce':
            continue
        generator = generator_at(root, earlier['pins']['code']['generator'])
        if generator is None:
            problems.append(f'v{version}: no generator in the history has the pinned hash')
            continue
        sums_path = root / RESULTS / results_folder(earlier) / 'SHA256SUMS'
        sums = dict(reversed(line.split('  ', 1)) for line in sums_path.read_text(encoding='utf-8').splitlines()) \
            if sums_path.is_file() else {}
        for name, frames in generator.seeded_families(earlier).items():
            relative = f'frames/{name.replace(":", "__")}.jsonl'
            if sums and sums.get(relative) != sha256_bytes(generator.file_text(frames).encode('utf-8')):
                problems.append(f'v{version}: {relative} does not have the hash its run recorded')
            label = f'regression:v{version}:{name}'
            families[label] = [{**f, 'values': {renames.get(k, k): v for k, v in f.get('values', {}).items()}}
                               if 'values' in f else f for f in frames]
            sources[label] = renames.get(ab_frames.family_source(name, earlier), ab_frames.family_source(name, earlier))
    return families, sources, problems


# ---------------------------------------------------------------- the run

def pin_problems(abreg: dict, root: Path, b_path: Path) -> list[str]:
    pins, problems = abreg['pins'], []
    if pins['a1_sha256'] != A1_SHA256:
        problems.append('the A1 fixture hash differs from the pin')
    if pins['b_pack_sha256'] != sha256_bytes(b_path.read_bytes()):
        problems.append('the B pack hash differs from the pin')
    for name, digest in code_hashes(root).items():
        if pins['code'].get(name) != digest:
            problems.append(f'{CODE[name]} differs from its pinned hash')
    if pins['runtime'] != runtime_pins(root):
        problems.append(f'the runtime {runtime_pins(root)} differs from the pinned {pins["runtime"]}')
    return problems + ab_a3.fixture_problems()


def run(abreg_path: Path, out: Path, root: Path = ROOT, b_path: Path | None = None, dry_run: bool = False) -> dict:
    started = time.perf_counter()
    abreg = json.loads(abreg_path.read_text(encoding='utf-8'))
    b_path = b_path or root / B_PACK
    pins = pin_problems(abreg, root, b_path)
    regression, regression_sources, problems = regression_families(abreg, root)
    pins += problems
    if pins and not dry_run:
        raise SystemExit('refusing a registered run:\n' + '\n'.join(f'  {p}' for p in pins))
    timings = {}

    def timed(label, function, *args):
        start = time.perf_counter()
        value = function(*args)
        timings[label] = round(timings.get(label, 0) + time.perf_counter() - start, 3)
        return value

    a1_document = load_a1(root)
    b_document = json.loads(b_path.read_text(encoding='utf-8'))
    a1_pack, b_pack = rcef_translate.load_pack(a1_document), rcef_translate.load_pack(b_document)
    oracle = ab_oracle.Oracle(b_document)
    families = {**ab_frames.fixed_inputs(abreg, root), **ab_frames.fixed_families(abreg),
                **ab_frames.seeded_families(abreg), **regression}
    if 'facs.code' in abreg['sources']:
        families['facs_library'] = [{'family': 'facs_library', 'label': str(n), 'keys': keys}
                                    for n, keys in enumerate(ab_a3.b_keys())]
    frame_sums = {f'frames/{name.replace(":", "__")}.jsonl': sha256_bytes(ab_frames.file_text(frames).encode('utf-8'))
                  for name, frames in families.items()}
    for name, frames in families.items():
        if frames and 'keys' in frames[0]:
            families[name] = facs_values(frames)
    by_source = {}
    for name in families:
        source = regression_sources.get(name) or ab_frames.family_source(name, abreg)
        by_source.setdefault(source, []).append(name)
    report = {'metrics': {}, 'failures': {}, 'refusals': [], 'observed_loss': [], 'regression': sorted(regression)}

    def record(metric, row, counts, failures=()):
        report['metrics'].setdefault(metric, []).append({**row, **counts})
        report['failures'].setdefault(metric, []).extend([[*row.values(), *f] for f in failures])

    # Route cross-check: the maps B runs are the maps the registration froze.
    routes = {}
    for name, pair in abreg['pairs'].items():
        route = rcef_route.Route(pair['source'], pair['target'], pack=b_pack)
        hops = {'in_hops': [[m, d] for m, _, d in route.hops if m in route.in_maps],
                'out_hops': [[m, s] for m, s, _ in route.hops if m in route.out_maps]}
        if hops != {k: pair[k] for k in hops}:
            raise SystemExit(f'{name}: Route selects maps the registration did not freeze')
        routes[name] = route
    b_runs, o_runs = {}, {}
    for name, pair in abreg['pairs'].items():
        for family in by_source.get(pair['source'], []):
            b_runs[name, family] = timed(f'B {name}', run_route, routes[name], families[family])
            o_runs[name, family] = timed(f'O {name}', oracle_results, oracle, pair, families[family])
            counts, failures = equals_oracle(b_runs[name, family], o_runs[name, family])
            record('B equals O', {'pair': name, 'family': family}, counts, failures)
            for n, result in enumerate(b_runs[name, family]):
                for mapping, refusal in result['refused'].items():
                    report['refusals'].append(['B', name, family, n, mapping, ' '.join(refusal['codes'])])
    a1_runs = {}
    for name, (source, target, maps) in A1_PAIRS.items():
        route = rcef_route.Route(source, target, pack=a1_pack, maps=maps)
        for family in by_source.get(source, []):
            a1_runs[name, family] = timed(f'A1 {name}', run_route, route, families[family])
            for n, result in enumerate(a1_runs[name, family]):
                for mapping, refusal in result['refused'].items():
                    report['refusals'].append(['A1', name, family, n, mapping, ' '.join(refusal['codes'])])
            if (name, family) in b_runs:
                record('M1', {'pair': name, 'family': family}, *m1(a1_runs[name, family], b_runs[name, family]))
                record('M2', {'pair': name, 'family': family}, *m2(a1_runs[name, family], b_runs[name, family]))
        impulse = families[f'impulse:{source}']
        lost = observed_loss(a1_runs[name, f'impulse:{source}'], impulse)
        report['observed_loss'] += [['A1', name, sid] for sid in lost]
        baseline = abreg['a1_figures']['observed_loss'][name]
        record('M4', {'pair': name, 'arm': 'A1'}, {'observed_loss': len(lost), 'baseline': len(baseline),
                                                   'matches_baseline': lost == baseline})
        if name in abreg['pairs']:
            pair = abreg['pairs'][name]
            record('M1s', {'pair': name}, *m1s(a1_document, b_document, name, pair))
            record('M2c', {'pair': name}, *m2c(a1_document, b_document, name, pair))
            record('M2b', {'pair': name}, m2b(a1_document, b_document, name, pair))
    for name, pair in abreg['pairs'].items():
        impulse_name = f'impulse:{pair["source"]}'
        if (name, impulse_name) not in b_runs:
            continue
        declared = set(abreg['lists']['no_target'])
        lost = observed_loss(b_runs[name, impulse_name], families[impulse_name], declared)
        report['observed_loss'] += [['B', name, sid] for sid in lost]
        record('M4', {'pair': name, 'arm': 'B'}, {'observed_loss': len(lost), 'baseline': '', 'matches_baseline': ''})
        seeded = {f: b_runs[name, f] for f in by_source[pair['source']]
                  if any(s['name'] == f for s in abreg['families'])}
        record('M3 coverage', {'pair': name}, *m3_coverage(
            b_document, pair, families[impulse_name], b_runs[name, impulse_name], o_runs[name, impulse_name],
            abreg['lists']['m3_flat_links'], seeded))
        if pair['source'] == pair['target']:
            for family in by_source[pair['source']]:
                record('M3 exact', {'pair': name, 'family': family},
                       *m3_exact(families[family], b_runs[name, family], abreg['sources'][pair['source']]))
    for name, hops in A2_PAIRS.items():
        a2 = [rcef_route.Route(s, t, pack=a1_pack, maps=m) for s, t, m in hops]
        for family in by_source.get(hops[0][0], []):
            results = timed(f'A2 {name}', chain, a2, families[family])
            if (name, family) in b_runs:
                counts, failures = m1(results, b_runs[name, family])
                counts['a2_outputs'] = sum(len(r['values']) for r in results)
                counts['b_outputs'] = sum(len(r['values']) for r in b_runs[name, family])
                record('M8', {'pair': name, 'family': family}, counts, failures)
    if 'facs.code' in abreg['sources']:
        a3_fb2 = [f'{FB2[0]}{c}{FB2[1]}' for c in ab_a3.channels()]
        expected = {'facs_library': [dict(zip(a3_fb2, f.values())) for f in ab_a3.a3_frames()]}
        for family in ('facs_key_impulses', 'facs_letters'):
            if family in families:
                expected[family] = [dict(zip(a3_fb2, ab_a3.a3_keys(f['keys']).values())) for f in families[family]]
        a1 = rcef_route.Route(*A1_PAIRS['FB2 -> ARKit'][:2], pack=a1_pack, maps=A1_PAIRS['FB2 -> ARKit'][2])
        for family, values in expected.items():
            if ('FACS -> FB2', family) in b_runs:
                record('M10', {'family': family}, *facs_compare(b_runs['FACS -> FB2', family], values,
                                                                abreg['lists']['m10_not_available']))
            if ('FACS -> ARKit', family) in b_runs:
                flags = {'isValid': True, 'isEyeFollowingBlendshapesValid': True}
                a3a1 = run_route(a1, [{'values': v, 'flags': flags} for v in values])
                record('M10b', {'family': family}, *facs_compare(b_runs['FACS -> ARKit', family],
                                                                 [r['values'] for r in a3a1],
                                                                 abreg['lists']['m10b_not_available']))
    goldens = json.loads((root / abreg['fixed_inputs']['goldens']['path']).read_text(encoding='utf-8'))
    golden_runs = {}
    for kind, pair_name in GOLDEN_PAIRS.items():
        source = GOLDEN_KINDS[kind]
        if pair_name in abreg['pairs'] and (pair_name, f'goldens:{source}') in b_runs:
            cases = [c for c in goldens['cases'] if GOLDEN_KINDS[c['mapping_kind']] == source]
            golden_runs[pair_name] = [r for c, r in zip(cases, b_runs[pair_name, f'goldens:{source}'])
                                      if c['mapping_kind'] == kind]
    record('M5 R1', {'reference': 'R1'}, *r1(golden_runs, goldens))
    if 'FB2 -> ARKit' in abreg['pairs']:
        with (root / 'tests/fixtures/godot_fb2_rules.csv').open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        record('M5 R2', {'reference': 'R2'}, *r2(b_document, abreg['pairs']['FB2 -> ARKit'], rows,
                                                 abreg['lists']['r2_departures']))
    timings['total'] = round(time.perf_counter() - started, 3)
    return write_results(out, abreg, report, frame_sums, timings, pins, dry_run, b_path, root)


# ---------------------------------------------------------------- results

GATES = {'M1': ('value_differences', 'sign_differences'), 'B equals O': ('differences',), 'M1s': ('differences',),
         'M2': ('violations',), 'M2c': ('shortfall',), 'M3 exact': ('errors',), 'M3 coverage': ('violations',),
         'M5 R2': ('differences',), 'M10': ('value_differences', 'coverage_violations', 'b_refusals'),
         'M10b': ('value_differences', 'coverage_violations')}
REPORT_ONLY = ('M2b', 'M8')


def status(metric: str, rows: list[dict]) -> str:
    if metric in REPORT_ONLY:
        return 'report'
    if metric == 'M4':
        ok = all(r['observed_loss'] == 0 if r['arm'] == 'B' else r['matches_baseline'] for r in rows)
    elif metric == 'M5 R1':
        ok = all(r['exact'] == r['cases'] - r['not_run'] and not r['not_run'] for r in rows)
    else:
        ok = all(not r[field] for r in rows for field in GATES[metric])
    return 'pass' if ok else 'FAIL'


FACS_FAMILIES = ['facs_library', 'facs_key_impulses', 'facs_letters']


def missing_rows(report: dict, abreg: dict) -> dict:
    """Per gate, the pairs or families it has no row for. A gate with a missing row fails: no rows is no evidence."""
    rows = report['metrics']
    required = {**{m: ('pair', list(A1_PAIRS)) for m in ('M1', 'M1s', 'M2', 'M2c')},
                'B equals O': ('pair', list(abreg['pairs'])), 'M3 coverage': ('pair', list(abreg['pairs'])),
                'M10': ('family', FACS_FAMILIES), 'M10b': ('family', FACS_FAMILIES)}
    missing = {}
    for metric, (key, names) in required.items():
        have = {r.get(key) for r in rows.get(metric, [])}
        if absent := [n for n in names if n not in have]:
            missing[metric] = absent
    if not rows.get('M3 exact'):
        missing['M3 exact'] = ['a round-trip pair']
    m4 = {(r['arm'], r['pair']) for r in rows.get('M4', [])}
    if absent := [f'{arm} {p}' for arm, names in (('A1', A1_PAIRS), ('B', abreg['pairs'])) for p in names
                  if (arm, p) not in m4]:
        missing['M4'] = absent
    return missing


def statuses(report: dict, abreg: dict) -> dict:
    """Each gate's status: FAIL if any row fails or a required row is missing."""
    found = {m: status(m, rows) for m, rows in report['metrics'].items()}
    for metric in missing_rows(report, abreg):
        found[metric] = 'FAIL'
    return found


def csv_text(rows: list[list]) -> str:
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator='\n').writerows(rows)
    return buffer.getvalue()


def write_results(out: Path, abreg: dict, report: dict, frame_sums: dict, timings: dict, pins: list, dry_run: bool,
                  b_path: Path, root: Path = ROOT) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    row_statuses = {m: status(m, rows) for m, rows in report['metrics'].items()}
    missing = missing_rows(report, abreg)
    gate_statuses = statuses(report, abreg)
    files = {}
    for metric, rows in report['metrics'].items():
        slug = re.sub(r'[^a-z0-9]+', '_', metric.lower()).strip('_')
        files[f'{slug}.csv'] = csv_text([list(rows[0])] + [[r[k] for k in rows[0]] for r in rows])
        if report['failures'][metric]:
            files[f'{slug}_failures.csv'] = csv_text(report['failures'][metric])
    files['refusals.csv'] = csv_text([['arm', 'pair', 'family', 'frame', 'map', 'codes'], *report['refusals']])
    files['losses.csv'] = csv_text([['arm', 'pair', 'observed loss'], *report['observed_loss']])
    files['assumptions.csv'] = csv_text([['pair', 'A1 rule', 'template', 'B key or superseded reason'],
                                         ['pending', 'the assumption catalogue (M4b) is not frozen yet', '', '']])
    lines = ['# A/B comparison: scoreboard', '',
             'The pivot route (B) against the direct maps (A1) and the other arms. The held-out frames are held out '
             'by procedure: the registration and its ledger line were committed before this run.', '']
    if dry_run:
        lines += ['**Dry run: not a registered result.**', '']
    if report['regression']:
        lines += ['Frames seen before the change (regression families, made again by the generator each earlier '
                  f'freeze pinned): {", ".join(report["regression"])}.', '']
    lines += ['| Metric | Threshold | Status |', '|---|---|---|']
    for metric in sorted(gate_statuses):
        threshold = THRESHOLDS.get(metric) or THRESHOLDS.get(metric.split()[0], 'report only')
        shown = gate_statuses[metric] + (f' (no rows for {", ".join(missing[metric])})' if metric in missing else '')
        lines.append(f'| {metric} | {threshold} | {shown} |')
    for metric, needs in PENDING.items():
        lines.append(f'| {metric} | needs {needs} | pending |')
    lines += ['', '| Pair | Evidence status (A1 / B) | M2c shortfall | M4b | External reference |',
              '|---|---|---|---|---|']
    m2b_rows = {r['pair']: r for r in report['metrics'].get('M2b', [])}
    m2c_rows = {r['pair']: r for r in report['metrics'].get('M2c', [])}
    for name in abreg['pairs']:
        reference = 'A1' if name in A1_PAIRS else 'A2' if name in A2_PAIRS else (
            'A3' if name.startswith('FACS -> ') and name.split(' -> ')[1] in ('FB2', 'ARKit') else
            'no external reference')
        evidence = f'{m2b_rows[name]["a1"]} / {m2b_rows[name]["b"]}' if name in m2b_rows else ''
        shortfall = m2c_rows[name]['shortfall'] if name in m2c_rows else ''
        lines.append(f'| {name} | {evidence} | {shortfall} | pending | {reference} |')
    files['scoreboard.md'] = '\n'.join(lines) + '\n'
    for name, text in files.items():
        (out / name).write_text(text, encoding='utf-8')
    passed = all(s in ('pass', 'report') for s in gate_statuses.values()) and not PENDING and not dry_run
    manifest = {'id': abreg['id'], 'version': abreg['version'], 'kind': abreg['kind'],
                'abreg_sha256': abreg_sha256(abreg), 'seed_root': abreg['seed_root'], 'dry_run': dry_run,
                'pin_problems': pins, 'passed': passed, 'statuses': gate_statuses, 'row_statuses': row_statuses,
                'missing_rows': missing, 'pending': PENDING,
                'a1_sha256': A1_SHA256, 'b_pack': b_path.name, 'b_pack_sha256': sha256_bytes(b_path.read_bytes()),
                'code': code_hashes(root), 'runtime': runtime_pins(root)}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    (out / 'timings.json').write_text(json.dumps(timings, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    sums = {name: sha256_bytes((out / name).read_bytes()) for name in [*files, 'manifest.json']}
    sums.update(frame_sums)
    (out / 'SHA256SUMS').write_text(''.join(f'{h}  {p}\n' for p, h in sorted(sums.items())), encoding='utf-8')
    return manifest


# ---------------------------------------------------------------- command line

def a1_loss(root: Path = ROOT) -> dict:
    """A1's observed loss per pair on the fixed impulse frames, with the figures behind it."""
    document = load_a1(root)
    pack = rcef_translate.load_pack(document)
    figures = {}
    for pair, (source, target, maps) in A1_PAIRS.items():
        channels = ab_frames.pinned_source(document, source)
        impulse = ab_frames.impulse_family('impulse', channels)
        results = run_route(rcef_route.Route(source, target, pack=pack, maps=maps), impulse)
        dropped = sorted({s for r in results[1:] for s in r['dropped']})
        figures[pair] = {'inputs': len(channels['channels']), 'dropped': len(dropped),
                         'observed_loss': observed_loss(results, impulse)}
    return figures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('draft')
    p.add_argument('out', type=Path)
    p.add_argument('--b-pack', type=Path)
    p.add_argument('--date', default='')
    p = commands.add_parser('run')
    p.add_argument('abreg', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--b-pack', type=Path)
    p.add_argument('--dry-run', action='store_true')
    commands.add_parser('check')
    commands.add_parser('a1-loss')
    args = parser.parse_args(argv)
    if args.command == 'draft':
        if args.out.resolve().parent == (ROOT / 'ab').resolve():
            raise SystemExit('write a draft outside ab/: every registration in ab/ needs a ledger line')
        args.out.write_text(json.dumps(draft(ROOT, args.b_pack, args.date), indent=1, sort_keys=True) + '\n',
                            encoding='utf-8')
        print(f'{args.out}: review it and fill in the frozen lists before you register it')
    elif args.command == 'run':
        manifest = run(args.abreg, args.out, ROOT, args.b_pack, args.dry_run)
        print(json.dumps(manifest['statuses'], indent=1, sort_keys=True))
        return 0 if manifest['passed'] else 1
    elif args.command == 'check':
        problems = registration_problems(ROOT)
        print('\n'.join(problems) or 'ab/: no problems')
        return 1 if problems else 0
    else:
        for pair, figure in a1_loss(ROOT).items():
            print(f'{pair}: {figure["inputs"]} inputs, {figure["dropped"]} dropped (no map reads them), '
                  f'observed loss {len(figure["observed_loss"])} {" ".join(figure["observed_loss"])}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
