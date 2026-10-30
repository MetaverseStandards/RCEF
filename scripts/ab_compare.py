#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run the A/B comparison of the pivot route (B) with the retired A1 direct maps and the other arms.

Usage:
  python scripts/ab_compare.py draft OUT.abreg [--b-pack PACK] [--date YYYY-MM-DD]
  python scripts/ab_compare.py run ABREG OUT_DIR [--b-pack PACK] [--dry-run]
  python scripts/ab_compare.py check
  python scripts/ab_compare.py a1-loss
  python scripts/ab_compare.py r5 README

- draft writes a first registration with every pin and A1 figure it can
  compute. Write it outside ab/, complete and review it, then commit it to
  ab/ and, in a later commit, its line in ab/FREEZES (ab/README.md).
- run checks the registration's pins, makes its frames (scripts/ab_frames.py),
  runs every arm and writes the results to OUT_DIR. A run whose pins do not
  match is refused, unless --dry-run, which marks the results unregistered.
- check prints every way ab/FREEZES, the registrations and the results break
  the rules in ab/README.md. tests/test_ab_registration.py runs it.
- a1-loss prints A1's observed loss on the fixed impulse frames (metric M4).
- r5 writes tests/fixtures/ict_facekit_facs.json (reference R5, metric M11)
  from ICT-FaceKit's README at the commit of record ict_facekit, after
  checking the record's SHA-256.

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
import ab_geometry  # noqa: E402
import ab_mutations  # noqa: E402
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
# Every file a run reads, besides the pack, the A1 fixture and the fixed inputs (pinned in fixed_inputs): the code of
# each arm and metric, and the files that the structure and pose-bridge tests (M7's checks) read.
CODE = {'route': 'examples/rcef_route.py', 'compare': 'scripts/ab_compare.py', 'generator': 'scripts/ab_frames.py',
        'oracle': 'tests/ab_oracle.py', 'codec': 'examples/facs_codec.py', 'geometry': 'scripts/ab_geometry.py',
        'mutations': 'scripts/ab_mutations.py', 'structure': 'tests/test_pivot_structure.py',
        'codec_data': 'examples/data/facs_codes.json', 'a3': 'tests/ab_a3.py',
        'translate': 'examples/rcef_translate.py', 'rigs': 'examples/rigs.py', 'ict_facekit': 'examples/ict_facekit.py',
        'check': 'check.py', 'tooling_lock': 'evidence/tooling.lock.json',
        'generator_canonical': 'scripts/build_canonical.py',
        'audit_doc': 'docs/canonical-set-audit.md', 'signal_doc': 'docs/canonical-set.md',
        'pose_bridge_tests': 'tests/test_pose_bridge.py',
        'pose_record': 'calibration/viseme-poses.rocketbox-features.cal', 'calibration_ledger': 'calibration/FREEZES',
        'intermediate': 'data/intermediate.toml', 'rocketbox_au_names': 'tests/fixtures/rocketbox_au_names.json',
        'ipa_symbols': 'tests/fixtures/ipa_chart_symbols.json'}
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
           # Through the viseme pose bridge: viseme classes become canonical expression signals.
           'META -> ARKit': ('openxr.visemes', 'arkit.coefficient'), 'META -> FB2': ('openxr.visemes', 'openxr.fb2'),
           'META -> VRCFT UE': ('openxr.visemes', 'vrcft.artist.base'), 'META -> FACS': ('openxr.visemes', 'facs.code'),
           'VRM -> VRCFT UE': ('vrm.preset', 'vrcft.artist.base'),
           **{f'{n} -> VRCFT eye': (p, 'vrcft.eye') for n, p in (('ARKit', 'arkit.coefficient'), ('FB2', 'openxr.fb2'),
                                                                 ('FACS', 'facs.code'), ('VRM', 'vrm.preset'))},
           **{f'{n} -> {n}': (p, p) for n, p in (('ARKit', 'arkit.coefficient'), ('FB2', 'openxr.fb2'),
                                                ('META', 'openxr.visemes'), ('VRM', 'vrm.preset'),
                                                ('VRCFT eye', 'vrcft.eye'), ('FACS', 'facs.code'))}}
A1_SOURCES = ('openxr.fb2', 'arkit.coefficient', 'openxr.visemes')
GOLDEN_KINDS = {'fb2_to_arkit': 'openxr.fb2', 'arkit_to_fb2': 'arkit.coefficient', 'arkit_to_ue': 'arkit.coefficient',
                'fb2_to_vrm': 'openxr.fb2', 'visemes_to_vrm': 'openxr.visemes'}
GOLDEN_PAIRS = {'fb2_to_arkit': 'FB2 -> ARKit', 'arkit_to_fb2': 'ARKit -> FB2', 'arkit_to_ue': 'ARKit -> VRCFT UE',
                'fb2_to_vrm': 'FB2 -> VRM blink', 'visemes_to_vrm': 'META -> VRM'}
# R3: FB2 -> Unified Expressions as Godot's plugin gives it, in a file of its own (scripts/derive_fb2_goldens.py).
R3_FILE, R3_KINDS, R3_PAIR = 'tests/fixtures/fb2_vrcft_ue_goldens.json', {'fb2_to_ue': 'openxr.fb2'}, 'FB2 -> VRCFT UE'
# Where B departs from R3 by design: Godot sets these parts to 0 ("Not measured") where the canonical value is
# copied into each part, and Godot fills TongueFlat from TONGUE_RETREAT, which RCEF does not map.
R3_DEPARTURES = [f'vrcft.artist.base.{n}' for n in (
    'BrowPinchLeft', 'BrowPinchRight', 'MouthCornerSlantLeft', 'MouthCornerSlantRight', 'MouthUpperLeft',
    'MouthUpperRight', 'MouthLowerLeft', 'MouthLowerRight', 'TongueFlat')]
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
# FB2 gaze outputs on the negative knot segment, and VRCFaceTracking Openness through the blink hops: both give
# fl(1 - fl(1 - x)), which rounds, so M3 reports their error.
M3_ROUNDING = [f'{FB2[0]}EYES_LOOK_{c}_FB' for c in ('LEFT_L', 'RIGHT_R', 'DOWN_L', 'DOWN_R')] + [
    f'vrcft.eye.{side}.Openness' for side in ('Left', 'Right')]
TINY = 2.0 ** -1020
# fl(1 - fl(1 - x)) is within 2**-54 of x on [0, 1]: 1 - x rounds by at most half an ulp of [0.5, 1), and the outer
# subtraction is exact (Sterbenz). On frames that break FB2's exclusivity only the difference of a pair is kept, so a
# gaze output can be off by the smaller input of its pair, plus the rounding of the difference.
ROUNDING_BOUND = 2.0 ** -54
NON_EXCLUSIVE_SLACK = 2.0 ** -52
THRESHOLDS = {
    'M1': 'B equals A1 on every output both write, sign of zero included; on the edge set B equals O',
    'M1s': 'exact Fraction composition of B equals A1 on every linear A1 output',
    'B equals O': 'B gives the oracle\'s values, bit for bit, refusal codes, labels and notes on every frame of every '
                  'pair',
    'M2': "in every frame B's refused outputs are among A1's, B writes every output A1 writes, dropped inputs equal",
    'M2c': "for every A1 output, B's hop evidence holds every evidence ID of the A1 rules that write it",
    'M3 exact': 'round trips exact on the listed channels; the rounding outputs within 2**-54 on exclusive frames and '
                'each gaze output within min(a, b) + 2**-52 on frames that break FB2 exclusivity',
    'M3 coverage': 'on every impulse frame B changes exactly the outputs O changes; every composed link is changed or '
                   'on the frozen flat list; every reached output non-zero on at least 1% of each seeded family that '
                   'sets a linked input',
    'M4': 'B observed loss 0; A1 observed loss equals the registered baseline',
    'M5 R1': 'R1: 129 of 129 goldens exact through B',
    'M5 R2': 'R2: per ARKit target, the composed B weights equal the 52 source-derived rows but the listed departures',
    'M8 R3': 'report: FB2 -> VRCFT UE, B equals R3 (the Godot route) on every R3 output but the listed departures',
    'M10': 'FACS -> FB2: B equals A3 on outputs both write; coverage list frozen; B refuses 0 frames',
    'M10b': 'FACS -> ARKit: B equals A3 then A1 on outputs both write; coverage list frozen',
    'M4 keys': 'every (A1 rule, A1 loss reason) of the frozen table is covered by the B losses it names on the route; '
               'every audit key B adds on an A1 pair is on the audit-added list',
    'M4b': 'every catalogue entry of each replaced A1 rule is held by the hop assumption keys it names on the route, '
           'or is superseded with a cited reason',
    'M6': 'report: B and A1 (A3 then A1 for FACS) pose each rig identically, vertex for vertex; the harness oracles '
          'pass',
    'M7': 'every registered mutation of the B pack is caught by each check it names',
    'M11': 'report: per ICT-FaceKit FACS row, B ARKit -> FACS links give the same ARKit shapes, or a listed '
           'difference',
}
# Gates these tools cannot compute yet: their frozen tables come from the definitions audit and the canonical data.
PENDING = {'M4 keys': 'the rule-scoped reason -> key table', 'M4b': 'the assumption catalogue',
           'M6': 'the rig caches (run --rig NAME=DIR) and the pinned rig hashes', 'M7': 'the mutation set',
           'M11': 'B ARKit -> FACS links and the R5 table', 'M8 R3': 'the R3 goldens'}


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
    bridges = [tuple(h) for h in pair.get('bridges', [])]
    return [oracle.route(pair['source'], pair['target'], [tuple(h) for h in pair['in_hops']],
                         [tuple(h) for h in pair['out_hops']], f['values'], f['flags'], bridges) for f in frames]


def equals_oracle(b: list[dict], o: list[dict]) -> tuple[dict, list]:
    """B's values (bit for bit), refusals by map (codes and references), labels and notes equal O's."""
    counts, failures = {'frames': len(b), 'differences': 0}, []
    for n, (x, y) in enumerate(zip(b, o, strict=True)):
        found = []
        for output in sorted(x['values'].keys() | y['values'].keys()):
            u, v = x['values'].get(output), y['values'].get(output)
            if u is None or v is None or bits(u) != bits(v):
                found.append(['value', output, repr(u), repr(v)])
        for output in sorted(x['labels'].keys() | y['labels'].keys()):
            if x['labels'].get(output) != y['labels'].get(output):
                found.append(['label', output, str(x['labels'].get(output)), str(y['labels'].get(output))])
        if x['refused'] != y['refused']:
            found.append(['refusal', '', json.dumps(x['refused'], sort_keys=True),
                          json.dumps(y['refused'], sort_keys=True)])
        if x.get('notes', []) != y.get('notes', []):
            found.append(['notes', '', ' | '.join(x.get('notes', [])), ' | '.join(y.get('notes', []))])
        if found:
            counts['differences'] += 1
            failures += [[n, *f] for f in found]
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


def weighted_upstream(rules: dict, sid: str) -> tuple[list[dict], set]:
    """As upstream, but a weighted_sum input with weight 0 carries nothing, so it is not followed."""
    found, leaves, todo = [], set(), [sid]
    while todo:
        current = todo.pop()
        rule = rules.get(current)
        if rule is None:
            leaves.add(current)
            continue
        found.append(rule)
        weights = rule['operator'].get('weights') if rule['operator']['id'] == 'weighted_sum' else None
        todo += [s for n, s in enumerate(rule['inputs']) if weights is None or weights[n] != 0]
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


def trace(document: dict, pair: dict, output: str) -> tuple[list[dict], set]:
    """The rules of every hop that an output of a pair depends on, and the source inputs at their far end.

    Out-map, then any bridge, then in-maps. A canonical value that no hop
    writes (not available, or a bridge input counted as 0) is not a source
    input, and neither is a weighted_sum input with weight 0.
    """
    out_rules = rules_by_output(document, [h[0] for h in pair['out_hops']])
    rules, leaves = weighted_upstream(out_rules, output)
    if not pair['in_hops']:
        return rules, leaves
    bridge_rules = rules_by_output(document, [h[0] for h in pair.get('bridges', [])])
    in_rules = rules_by_output(document, [h[0] for h in pair['in_hops']])
    sources = set()
    for leaf in leaves:
        more, ends = weighted_upstream(bridge_rules, leaf) if leaf in bridge_rules else ([], {leaf})
        rules += more
        for end in ends:
            if end in in_rules:
                found, far = weighted_upstream(in_rules, end)
                rules += found
                sources |= far
    return rules, sources


def b_forms(document: dict, pair: dict) -> dict:
    """The composed linear form of every B output of a pair, or None where it is not linear (a bridge never is)."""
    out_rules = rules_by_output(document, [h[0] for h in pair['out_hops']])
    in_rules = rules_by_output(document, [h[0] for h in pair['in_hops']])
    bridged = set(rules_by_output(document, [h[0] for h in pair.get('bridges', [])]))
    outputs = [o for h in pair['out_hops'] for o in rcef_route.map_ends(
        next(m['rules'] for m in document['mappings'] if m['id'] == h[0]))[1]]
    inner = {}
    forms = {}
    for output in outputs:
        outer = linear_form(out_rules, output)
        if outer is not None:
            for leaf in outer[1]:
                if leaf not in inner and leaf not in bridged:
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
    output on frames that break FB2's exclusivity; values below 2**-1020 are not claimed.

    The excluded outputs have bounds: the rounding outputs within ROUNDING_BOUND, and a gaze output on a
    non-exclusive frame within the smaller input of its pair plus NON_EXCLUSIVE_SLACK. A value past its bound
    counts in over_bound, which fails the gate.
    """
    counts = {'frames': len(frames), 'non_exclusive_frames': 0, 'errors': 0, 'max_excluded_error': 0.0,
              'excluded_became_zero': 0, 'max_rounding_error': 0.0, 'over_bound': 0}
    failures, partner = [], {}
    for a, b in source['gaze_pairs']:
        partner[a], partner[b] = b, a
    for n, (frame, result) in enumerate(zip(frames, back, strict=True)):
        exclusive = not any(frame['values'].get(a) and frame['values'].get(b) for a, b in source['gaze_pairs'])
        counts['non_exclusive_frames'] += not exclusive
        excluded = set(M3_ROUNDING) if exclusive else set(partner)
        for sid, value in result['values'].items():
            original = frame['values'].get(sid)
            if original is None:
                continue
            if sid in excluded or 0 < abs(original) < TINY:
                error = abs(value - original)
                counts['max_excluded_error'] = max(counts['max_excluded_error'], error)
                counts['excluded_became_zero'] += value == 0 and original != 0
                if 0 < abs(original) < TINY:
                    continue
                if exclusive:
                    counts['max_rounding_error'] = max(counts['max_rounding_error'], error)
                    bound = ROUNDING_BOUND
                else:
                    bound = min(original, frame['values'].get(partner[sid], 0.0)) + NON_EXCLUSIVE_SLACK
                if error > bound:
                    counts['over_bound'] += 1
                    failures.append([n, sid, repr(original), repr(value)])
            elif value != original:
                counts['errors'] += 1
                failures.append([n, sid, repr(original), repr(value)])
    return counts, failures


def links(document: dict, pair: dict, outputs) -> dict:
    """Each (source input, output) link of the composed hop weights: True when a piecewise operator is on the way."""
    found = {}
    for output in outputs:
        rules, leaves = trace(document, pair, output)
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
                seeded: dict, channels: dict | None = None) -> tuple[dict, list]:
    """Impulse frames change exactly O's outputs; every composed link is in O's set or the frozen flat list; every
    reached output is non-zero on at least 1% of each seeded family of the pair's source. A family that names its
    channels (the FACS letter family) is held only to the outputs that those channels reach."""
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
        varied = (channels or {}).get(name)
        for output in sorted({o for s, o in linked if varied is None or s in varied}):
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


def r3(results: list[dict], goldens: dict, departures: list[str]) -> tuple[dict, list]:
    """M8 R3: each R3 case through B gives its expected value on every output, except the listed departures."""
    counts = {'cases': len(goldens['cases']), 'outputs': 0, 'exact': 0, 'departures': 0, 'departures_not_seen': 0,
              'differences': 0}
    failures, seen = [], set()
    for n, (case, result) in enumerate(zip(goldens['cases'], results, strict=True)):
        for output, value in sorted(case['expected'].items()):
            counts['outputs'] += 1
            same = output in result['values'] and bits(result['values'][output]) == bits(value)
            if same:
                counts['exact'] += 1
            elif output in departures:
                counts['departures'] += 1
                seen.add(output)
            else:
                counts['differences'] += 1
                failures.append([n, output, repr(value), repr(result['values'].get(output, 'not written'))])
    counts['departures_not_seen'] = len(set(departures) - seen)
    return counts, failures


# ---------------------------------------------------------------- M4 keys and M4b: today's losses and assumptions

AUDIT_DOC = 'docs/canonical-set-audit.md'
PROVIDER_TOKENS = {'FB2': 'openxr.fb2', 'ARKit': 'arkit.coefficient', 'UE': 'vrcft.artist.base', 'VRM': 'vrm.preset',
                   'META': 'openxr.visemes'}
PAIR_NAMES = {'Unified Expressions': 'VRCFT UE'}
# The audit key's owning set, from the start of the key (docs/canonical-set-audit.md, loss keys).
KEY_OWNERS = (('fb2_', 'FB2'), ('arkit_', 'ARKit'), ('ict_', 'ARKit'), ('vrcft_ue_', 'UE'), ('vrm_', 'VRM'),
              ('meta_', 'META'))
# The gain loss on each hop, by set; VRM has none (its out-hop has the weight loss instead).
GAIN = {'FB2': 'FB2 gain and full-activation pose not published',
        'ARKit': 'ARKit gain and full-activation pose not published',
        'UE': 'Unified Expressions gain and full-activation pose not published',
        'META': 'META gain and full-activation pose not published'}
SYMMETRY = ('in', 'asymmetry unknown: symmetry is invented')
ASYMMETRY = ('out', 'asymmetry irrecoverable')
NETTING = ('out', 'FB2 allows only one of two opposing gaze directions to be non-zero; when both canonical directions '
                  'of a pair are non-zero, only their difference is kept, as the larger direction reduced by the '
                  'smaller')
TONGUE = 'the tongue extension has no stated length'
# The audit's table "Mapping today's losses to keys": the start of each loss reason of today's maps, and where it
# lives on the pivot route of the same rule. A plain string is an audit key, on the hop of the set that owns it;
# (side, text) is a loss reason on that side; 'gain' and 'split' are resolved per rule.
REASON_HOMES = [
    ('provider gain and full-activation pose are not published', ['gain']),
    ('Unified Expressions splits this shape into parts', ['split']),
    ('FB2 maximum gaze angle is unspecified', ['fb2_gaze_max_angle_unspecified']),
    ('asymmetry unknown: symmetry is invented', [SYMMETRY]),
    ('FB2 allows only one of two opposing gaze directions', [NETTING]),
    ('ARKit describes eyelid movement consistent with the gaze; FB2', ['arkit_gaze_eyelid', 'fb2_gaze_rotation']),
    ('FB2 describes eye rotation; ARKit describes eyelid', ['fb2_gaze_rotation', 'arkit_gaze_eyelid']),
    ('FB2 opposing directions are mutually exclusive', ['fb2_gaze_exclusive']),
    ('ARKit and Unified Expressions both describe eyelid', ['arkit_gaze_eyelid', 'vrcft_ue_gaze_no_angle']),
    ('asymmetry irrecoverable', [ASYMMETRY]),
    ('consonant visemes are dropped',
     [('out', 'consonant and rest classes are dropped, so outputs no longer sum to 1')]),
    ('a viseme probability becomes', ['vrm_vowel_asset_weight']),
    ('both are extension shapes with no stated length', [('in', TONGUE), ('out', TONGUE)]),
    ('FB2 also pulls the corner back and laterally', ['arkit_mouthsmile_upward']),
    ('an FB2 weight becomes an asset-authored expression weight',
     [('out', 'a canonical value becomes an asset-authored expression weight')]),
    ('VRM blink (both eyes) is left unset', ['same']),
    ('a model may mark the preset isBinary', ['same']),
    ('jaw-relative versus jaw-independent lip closure', ['arkit_mouthclose_jaw_unresolved']),
    ('FB2 describes upward lip motion induced by the chin raiser', ['arkit_mouthshrug_outward']),
    ('FB2 describes upward chin and lower-lip motion', ['arkit_mouthshrug_outward']),
    ('vowel quality differs', ['vrm_ih_vowel_quality']),
]
# Unified Expressions parts that the canonical set holds itself, so today's split moves to the ARKit in-hop fan-out.
CANONICAL_PARTS = re.compile(r'\.(BrowInnerUp|CheekPuff|LipFunnel|LipSuck)\w+$')
# Each provider's own definition records: a rule that cites more than these (and the FACS crosswalk) has a transfer.
OWN_RECORDS = {'arkit.coefficient': {'apple_blendshapes'}, 'openxr.fb2': {'xr_fb2'},
               'vrcft.artist.base': {'vrcft_artist', 'vrcft_docs_shapes'}, 'vrm.preset': {'vrm_expressions'},
               'openxr.visemes': set()}
# The audit's assumption catalogue: the hop assumption keys each template needs on the route, by set, or the cited
# reason it is superseded. 'transfer' needs transfer.provider or transfer.withdrawn, where the rule cites a crosswalk.
TEMPLATE_HOMES = {
    'a01': {'ARKit': ['endpoints'], 'UE': ['endpoints']},
    'a02': 'the canonical side field (canonical-set.md, Fields); frames ARKit same and Unified Expressions same',
    'a03': {'ARKit': ['endpoints'], 'FB2': ['endpoints']},
    'a04': 'the canonical side field (canonical-set.md, Fields); frames ARKit same and FB2 same',
    'a05': {'FB2': ['endpoints'], 'ARKit': ['endpoints']},
    'a06': 'the canonical side field (canonical-set.md, Fields); frames FB2 same and ARKit same',
    'a07': {'FB2': ['correspondence'], 'ARKit': ['correspondence'], 'any': ['transfer']},
    'a08': {'ARKit': ['correspondence'], 'UE': ['transfer']},
    'a09': {'ARKit': ['correspondence'], 'FB2': ['correspondence']},
    'a10': {'UE': ['fan_out.vrcft_ue']},
    'a11': {'ARKit': ['endpoints']},
    'a12': {'FB2': ['net.fb2_gaze']},
    'a13': {'UE': ['fan_out.vrcft_ue']},
    'a14': {'FB2': ['evidence.vrcft_tables_not_cited']},
    'a15': {'VRM': ['vrm.downstream_effects']},
    'a16': {'META': ['correspondence'], 'VRM': ['correspondence']},
    'a17': {'VRM': ['vrm.probability_as_weight']},
    'a18': {'VRM': ['vrm.phoneme_label_only']},
    'a19': {'FB2': ['net.fb2_gaze', 'correspondence']},
    'a20': {'FB2': ['net.fb2_gaze', 'correspondence']},
    'a21': {'UE': ['fan_out.vrcft_ue']},
    'a22': {'FB2': ['net.fb2_gaze']},
    'a23': {'FB2': ['gaze.fb2_exclusive']},
    'a24': {'UE': ['evidence.godot_only_mouth_shift']},
    'a25': {'ARKit': ['mean.arkit']},
    'a26': {'VRM': ['vrm.side_caveat']},
    'a27': {'FB2': ['correspondence'], 'VRM': ['correspondence', 'vrm.definitional_only']},
    'a28': {'VRM': ['endpoints']},
    'a29': {'FB2': ['evidence.godot_only_mouth_shift'], 'ARKit': ['evidence.godot_only_mouth_shift']},
    'a30': {'ARKit': ['evidence.godot_only_mouth_shift'], 'FB2': ['evidence.godot_only_mouth_shift']},
    'a31': {'FB2': ['evidence.vrcft_tables_not_cited']},
    'a32': {'ARKit': ['mean.arkit']},
    'a33': {'ARKit': ['mean.arkit']},
    'a34': {'ARKit': ['mean.arkit']},
    'a35': {'ARKit': ['lips_toward.jaw_not_compensated']},
}
A10_SUPERSEDED = ('the canonical split: the canonical set holds these parts, so the Unified Expressions out-hop is a '
                  '1:1 copy and the copy into each part moves to the ARKit in-hop')


def doc_table(text: str, heading: str) -> list[dict]:
    """The first Markdown table after a heading, as one dict per row (cells stripped)."""
    lines = text.split('\n')
    start = lines.index(heading)
    rows = []
    for line in lines[start + 1:]:
        if line.startswith('#'):
            break
        if line.startswith('|'):
            rows.append([c.strip() for c in line.strip().strip('|').split('|')])
        elif rows:
            break
    return [dict(zip(rows[0], r)) for r in rows[2:]]


def template_pattern(template: str) -> re.Pattern:
    """A catalogue template (with <ARKit>, <q>, <w>, <side> and list placeholders) as a whole-string pattern."""
    text = template.strip('`')
    pattern = ''
    for part in re.split(r'(<[^<>]+>)', text):
        if not part.startswith('<'):
            pattern += re.escape(part)
        elif part.endswith('…>') or part == '<q>':
            pattern += r'.+?'
        elif part == '<w>':
            pattern += r'[\w.]+'  # a decimal weight, or (a16) an example word
        elif part == '<side>':
            pattern += r'(?:left|right)'
        else:
            pattern += r'\w+'
    return re.compile(pattern)


def side_of(token: str, pair: dict) -> str | None:
    """'in' or 'out': the hop side of a pair where a set's maps are; None if the set is at neither end."""
    profile = PROVIDER_TOKENS[token]
    return 'in' if profile == pair['source'] else 'out' if profile == pair['target'] else None


def key_side(key: str, pair: dict) -> str | None:
    owner = next(o for prefix, o in KEY_OWNERS if key.startswith(prefix))
    return side_of(owner, pair)


def a1_rule_routes(a1_document: dict, b_document: dict, pair_name: str, pair: dict) -> dict:
    """For each rule of the pair's A1 maps: the B rules of its route, by side ('in', 'out').

    The route of an output is traced from B's out-map back through its
    in-maps. Today's internal gaze steps write no output, so their route is
    the routes of the A1 rules that read them.
    """
    _, _, maps = A1_PAIRS[pair_name]
    out_rules = rules_by_output(b_document, [h[0] for h in pair['out_hops']])
    in_rules = rules_by_output(b_document, [h[0] for h in pair['in_hops']])
    rules = [r for m in a1_document['mappings'] if m['id'] in maps for r in m['rules']]

    def of_output(output):
        found, leaves = upstream(out_rules, output)
        return {'out': found, 'in': [r for leaf in leaves for r in upstream(in_rules, leaf)[0]]}

    routes = {}
    for rule in rules:
        output = rule['outputs'][0]
        if output in out_rules:
            routes[rule['id']] = of_output(output)
    for rule in rules:
        if rule['id'] not in routes:
            readers = [r for r in rules if rule['outputs'][0] in r['inputs']]
            routes[rule['id']] = {side: [x for r in readers for x in routes.get(r['id'], {}).get(side, [])]
                                  for side in ('in', 'out')}
    return routes


def loss_ids(rule: dict, keys) -> set:
    """A rule's losses as identifiers: the audit key for an audit loss, else the exact loss reason."""
    found = set()
    for loss in rule['loss_annotations']:
        head = loss['reason'].split(':', 1)[0]
        found.add(head if head in keys else loss['reason'])
    return found


def audit_keys(root: Path = ROOT) -> list[str]:
    text = (root / AUDIT_DOC).read_text(encoding='utf-8')
    return [r['Key'].strip('`') for r in doc_table(text, '## Loss keys')]


def reason_key_table(a1_document: dict, b_document: dict, pairs: dict, root: Path = ROOT) -> dict:
    """The rule-scoped reason -> key table: per (A1 rule, A1 loss reason), the B losses that must cover it, by side."""
    table = {}
    for pair_name, (_, _, maps) in A1_PAIRS.items():
        if pair_name not in pairs:
            continue  # B cannot route it; M4 keys then has no row for it and fails
        pair = pairs[pair_name]
        for mapping in a1_document['mappings']:
            if mapping['id'] not in maps:
                continue
            for rule in mapping['rules']:
                for loss in rule['loss_annotations']:
                    reason = loss['reason']
                    homes = [h for start, h in REASON_HOMES if reason.startswith(start)]
                    if len(homes) != 1:
                        raise SystemExit(f'{rule["id"]}: loss reason {reason!r} has {len(homes)} homes in REASON_HOMES')
                    need = {'in': set(), 'out': set()}
                    for home in homes[0]:
                        if home == 'gain':
                            for token, text in GAIN.items():
                                if side := side_of(token, pair):
                                    need[side].add(text)
                        elif home == 'split':
                            if CANONICAL_PARTS.search(rule['outputs'][0]):
                                need[SYMMETRY[0]].add(SYMMETRY[1])
                            else:
                                need[key_side('vrcft_ue_set_equal', pair)].add('vrcft_ue_set_equal')
                        elif home == 'same':
                            need['out'].add(reason)
                        elif isinstance(home, tuple):
                            need[home[0]].add(home[1])
                        else:
                            need[key_side(home, pair)].add(home)
                    table[f'{rule["id"]} | {reason}'] = {'pair': pair_name,
                                                          **{s: sorted(v) for s, v in need.items()}}
    return table


def audit_added_keys(root: Path = ROOT) -> dict:
    """The audit's "Keys added on today's pairs" table, as {pair: [keys]}."""
    text = (root / AUDIT_DOC).read_text(encoding='utf-8')
    added = {}
    for row in doc_table(text, "## Keys added on today's pairs"):
        keys = re.findall(r'`([a-z0-9_]+)`', row['Key'])
        for pair in re.sub(r'\(.*?\)', '', row['Pairs where it is added']).split(','):
            name = pair.strip().replace('→', '->')
            for long, short in PAIR_NAMES.items():
                name = name.replace(long, short)
            added.setdefault(name, set()).update(keys)
    return {pair: sorted(keys) for pair, keys in sorted(added.items())}


AUDIT_SECTIONS = {'openxr.fb2': ('## FB2', 'openxr.fb2.XR_FACE_EXPRESSION2_', '_FB'),
                  'arkit.coefficient': ('## ARKit', 'arkit.coefficient.', ''),
                  'vrcft.artist.base': ('## VRCFaceTracking Unified Expressions', 'vrcft.artist.base.', '')}


def audit_verdicts(text: str) -> dict:
    """{(set, provider name): {canonical short name: verdict}} from the audit's per-set tables."""
    found = {}
    for profile, (heading, _, _) in AUDIT_SECTIONS.items():
        for row in doc_table(text, heading):
            short = re.findall(r'`([^`]+)`', row['Signal'])[0]
            for name in re.split(r',| and ', row['Source name'].replace('`', '')):
                found.setdefault((profile, name.strip()), {})[short] = row['Verdict']
    return found


def transfer_keys(rule: dict, pair: dict, verdicts: dict) -> str:
    """The transfer keys a hop of this A1 rule may hold: transfer.withdrawn where either set's audit row for the
    canonical signal is differs or unresolved, transfer.provider where both are same."""
    rows = []
    for profile in (pair['source'], pair['target']):
        _, prefix, suffix = AUDIT_SECTIONS[profile]
        for sid in rule['inputs'] + rule['outputs']:
            if sid.startswith(prefix) and sid.endswith(suffix):
                rows.append(verdicts.get((profile, sid[len(prefix):len(sid) - len(suffix) or None]), {}))
    shorts = set.intersection(*(set(r) for r in rows)) if rows and all(rows) else set()
    if not shorts:
        raise SystemExit(f'{rule["id"]}: no canonical signal that the audit rows of both sets share')
    allowed = set()
    for short in shorts:
        same = all(r[short] == 'same' for r in rows)
        allowed.add('transfer.provider' if same else 'transfer.withdrawn')
    return '|'.join(sorted(allowed))


def assumption_catalogue(a1_document: dict, pairs: dict, root: Path = ROOT) -> dict:
    """The frozen catalogue, per (A1 rule, template): the hop keys the route needs by side, or why it is superseded.

    Templates come from the audit's catalogue table; every assumption string of
    today's maps must match exactly one, and the count of strings per template
    must be the table's.
    """
    text = (root / AUDIT_DOC).read_text(encoding='utf-8')
    rows = doc_table(text, '## Assumption catalogue')
    verdicts = audit_verdicts(text)
    patterns = {r['ID']: template_pattern(r['Template']) for r in rows}
    counts = dict.fromkeys(patterns, 0)
    catalogue = {}
    for pair_name, (_, _, maps) in A1_PAIRS.items():
        if pair_name not in pairs:
            continue  # B cannot route it; M4b then has no row for it and fails
        pair = pairs[pair_name]
        for mapping in a1_document['mappings']:
            if mapping['id'] not in maps:
                continue
            for rule in mapping['rules']:
                for assumption in rule['assumptions']:
                    hits = [i for i, pattern in patterns.items() if pattern.fullmatch(assumption)]
                    if len(hits) != 1:
                        raise SystemExit(f'{rule["id"]}: {assumption!r} matches templates {hits}')
                    template = hits[0]
                    counts[template] += 1
                    home = TEMPLATE_HOMES[template]
                    entry = {'pair': pair_name}
                    if isinstance(home, str):
                        entry['superseded'] = home
                    elif template == 'a10' and CANONICAL_PARTS.search(rule['outputs'][0]):
                        entry['superseded'] = A10_SUPERSEDED
                    else:
                        own = OWN_RECORDS[pair['source']] | OWN_RECORDS[pair['target']]
                        crosswalk = bool(set(rule['evidence']) - own - {'ict_facekit'})
                        need = {'in': set(), 'out': set(), 'any': set()}
                        for token, keys in home.items():
                            side = 'any' if token == 'any' else side_of(token, pair)
                            for key in keys:
                                if key == 'transfer':
                                    if crosswalk:
                                        need[side].add(transfer_keys(rule, pair, verdicts))
                                else:
                                    need[side].add(key)
                        entry.update({s: sorted(v) for s, v in need.items()})
                    catalogue[f'{rule["id"]} | {template}'] = entry
    expected = {r['ID']: int(r['Strings']) for r in rows}
    if counts != expected and set(pairs) >= set(A1_PAIRS):
        raise SystemExit(f'assumption strings per template {counts} differ from the catalogue {expected}')
    return catalogue


def hop_keys(rule: dict) -> set:
    return {a.split(':', 1)[0] for a in rule['assumptions']}


def held(need: str, present: set) -> bool:
    return any(option in present for option in need.split('|'))


def m4_keys(abreg: dict, a1_document: dict, b_document: dict, root: Path = ROOT) -> tuple[list, list]:
    """Per A1 pair: the reason -> key table's B losses missing from the route, and audit keys B adds unlisted.

    Returns (rows, failures). A1 loss corrections (by "rule | reason") are left out.
    """
    keys = set(abreg['lists']['audit_keys'])
    table, corrections = abreg['lists']['reason_key_table'], set(abreg['lists']['a1_loss_corrections'])
    added = abreg['lists']['audit_added_keys']
    rows, failures = [], []
    for pair_name in (p for p in A1_PAIRS if p in abreg['pairs']):
        pair = abreg['pairs'][pair_name]
        routes = a1_rule_routes(a1_document, b_document, pair_name, pair)
        counts = {'entries': 0, 'shortfall': 0, 'unlisted_added': 0}
        covered = {}
        for entry_id, entry in table.items():
            if entry['pair'] != pair_name or entry_id in corrections:
                continue
            counts['entries'] += 1
            rule_id = entry_id.split(' | ', 1)[0]
            for side in ('in', 'out'):
                present = set().union(*(loss_ids(r, keys) for r in routes[rule_id][side]))
                for need in entry[side]:
                    if need not in present:
                        counts['shortfall'] += 1
                        failures.append([pair_name, entry_id, side, need, 'missing on the route'])
                covered.setdefault(rule_id, set()).update(n for n in entry[side] if n in keys)
        helpers = {r['id'] for m in a1_document['mappings'] for r in m['rules']
                   if r['outputs'][0].startswith('rcef.intermediate.')}
        for rule_id, route in routes.items():
            if rule_id in helpers:
                continue  # an internal gaze step writes no output; the rules that read it carry its keys
            found = set().union(*(loss_ids(r, keys) & keys for side in ('in', 'out') for r in route[side]))
            for key in sorted(found - covered.get(rule_id, set()) - set(added.get(pair_name, []))):
                counts['unlisted_added'] += 1
                failures.append([pair_name, rule_id, '', key, 'an audit key the route adds, not on the added list'])
        rows.append({'pair': pair_name, **counts})
    return rows, failures


def m4b(abreg: dict, a1_document: dict, b_document: dict) -> tuple[list, list, list]:
    """Per A1 pair: catalogue entries whose route lacks a needed hop assumption key. Also one row per entry."""
    catalogue = abreg['lists']['assumption_catalogue']
    rows, failures, entries = [], [], []
    for pair_name in (p for p in A1_PAIRS if p in abreg['pairs']):
        pair = abreg['pairs'][pair_name]
        routes = a1_rule_routes(a1_document, b_document, pair_name, pair)
        counts = {'entries': 0, 'superseded': 0, 'shortfall': 0}
        for entry_id, entry in catalogue.items():
            if entry['pair'] != pair_name:
                continue
            counts['entries'] += 1
            rule_id, template = entry_id.split(' | ', 1)
            if 'superseded' in entry:
                counts['superseded'] += 1
                entries.append([pair_name, rule_id, template, f'superseded: {entry["superseded"]}'])
                continue
            route = routes[rule_id]
            present = {side: set().union(*(hop_keys(r) for r in route[side])) for side in ('in', 'out')}
            present['any'] = present['in'] | present['out']
            missing = [f'{side}: {need}' for side in ('in', 'out', 'any') for need in entry.get(side, [])
                       if not held(need, present[side])]
            if missing:
                counts['shortfall'] += 1
                failures.append([pair_name, rule_id, template, '; '.join(missing)])
            entries.append([pair_name, rule_id, template, '; '.join(
                f'{side}: {" ".join(entry[side])}' for side in ('in', 'out', 'any') if entry.get(side))])
        rows.append({'pair': pair_name, **counts})
    return rows, failures, entries


# ---------------------------------------------------------------- M11: B's ARKit -> FACS links against R5 (ICT-FaceKit)

R5_FILE = 'tests/fixtures/ict_facekit_facs.json'
R2_FILE = 'tests/fixtures/godot_fb2_rules.csv'
R5_LINES = (154, 184)
# Where B departs from ICT-FaceKit's FACS table on purpose (the audit's ICT crosswalk rows and notes).
M11_DIFFERENCES = {
    'AU10': 'ICT relates mouthShrugUpper; B relates mouthUpperUp (canonical upper_lip_raise has code 10)',
    'AU11': 'ICT relates mouthUpperUp; B has no AU11',
    'AU27': 'ICT relates jawOpen; B reads AU27 as AU26 into jaw_drop and writes jawOpen back as AU26',
    'AU33': 'ICT relates cheekPuff; B writes cheekPuff as AU34',
    'AU45': 'ICT relates eyeBlink; B writes eyeBlink as AU43',
    **{f'AU{n}': 'B has no FACS gaze in phase 1' for n in (61, 62, 63, 64)},
}


def write_r5(readme: Path, root: Path = ROOT) -> dict:
    """The R5 fixture: ICT-FaceKit's FACS table with the record it comes from."""
    import tomllib
    record = next(r for r in tomllib.loads((root / 'evidence/sources.toml').read_text(encoding='utf-8'))['evidence']
                  if r['id'] == 'ict_facekit')
    fixture = {'record': record['id'], 'url': record['url'], 'sha256': record['sha256'], 'license': record['license'],
               'credit': 'ICT-FaceKit, Copyright (c) 2020 USC Institute for Creative Technologies, MIT license',
               'lines': list(R5_LINES), 'rows': r5_rows(readme.read_bytes(), record['sha256'])}
    (root / R5_FILE).write_text(json.dumps(fixture, indent=1) + '\n', encoding='utf-8')
    return fixture


def r5_rows(readme: bytes, sha256: str) -> list[dict]:
    """ICT-FaceKit's FACS table (README lines 154-184 at the pinned commit) as rows of FACS unit and shape names."""
    if sha256_bytes(readme) != sha256:
        raise SystemExit('the ICT-FaceKit README does not have the SHA-256 of record ict_facekit')
    rows = []
    for number, line in enumerate(readme.decode('utf-8').split('\n'), 1):
        if R5_LINES[0] <= number <= R5_LINES[1] and (m := re.fullmatch(r'\| (AU\d+ [^|]*?)\s*\| ([^|]*?)\s*\|', line)):
            rows.append({'line': number, 'unit': m[1], 'shapes': [s.strip() for s in m[2].split('+')]})
    return rows


def ict_arkit(shape: str) -> str:
    """An ICT-FaceKit shape name as the ARKit coefficient it splits or renames: browInnerUp_L -> browInnerUp,
    eyeBlink_L -> eyeBlinkLeft."""
    base, _, side = shape.rpartition('_')
    if not base:
        return shape
    return base if base in ('browInnerUp', 'cheekPuff') else base + {'L': 'Left', 'R': 'Right'}[side]


def m11(document: dict, pair: dict, reference: dict, differences: dict) -> tuple[list, list]:
    """Per R5 row: the ARKit shapes ICT relates to the FACS unit, and those B links to the same facs.code outputs."""
    outputs = [o for h in pair['out_hops'] for o in rcef_route.map_ends(
        next(m['rules'] for m in document['mappings'] if m['id'] == h[0]))[1]]
    linked = links(document, pair, outputs)
    rows, failures = [], []
    for row in reference['rows']:
        m = re.fullmatch(r'AU(\d+) (.*?)(?: \((left|right)\))?', row['unit'])
        code, direction = f'AU{int(m[1])}', m[3]
        sides = ('_' + direction,) if direction else ('', '_left', '_right')
        wanted = {f'facs.code.au{int(m[1]):02d}{s}' for s in sides}
        b = sorted({s[len(ARKIT):] for s, o in linked if o in wanted})
        ict = sorted({ict_arkit(s) for s in row['shapes']})
        if b == ict:
            verdict = 'listed but the same' if code in differences else 'same'
        else:
            verdict = 'listed difference' if code in differences else 'unlisted difference'
        rows.append({'line': row['line'], 'unit': row['unit'], 'ict': ' '.join(ict), 'b': ' '.join(b) or 'none',
                     'verdict': verdict})
        if verdict not in ('same', 'listed difference'):
            failures.append([row['line'], row['unit'], ' '.join(ict), ' '.join(b), verdict])
    return rows, failures


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
            pairs[name] = {'source': source, 'target': target, **route_hops(route)}
    return pairs


def route_hops(route: rcef_route.Route) -> dict:
    """The maps a route runs, as a registration freezes them: in-maps, bridges and out-maps, with their profiles."""
    return {'in_hops': [[m, dst] for m, _, dst in route.hops if m in route.in_maps],
            'bridges': [[m, src, dst] for m, src, dst in route.hops if m in route.bridges],
            'out_hops': [[m, src] for m, src, _ in route.hops if m in route.out_maps]}


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
            'r3': {'path': R3_FILE, 'kinds': R3_KINDS, 'sha256': sha256_bytes((root / R3_FILE).read_bytes())},
            'r5': {'path': R5_FILE, 'sha256': sha256_bytes((root / R5_FILE).read_bytes())},
            'r2': {'path': R2_FILE, 'sha256': sha256_bytes((root / R2_FILE).read_bytes())},
            'a3': ab_a3.SHA256},
        'pairs': pairs,
        'metrics': THRESHOLDS,
        'lists': {'intended_differences': [], 'a1_loss_corrections': [], 'audit_added_keys': audit_added_keys(root),
                  'side_exceptions': [], 'audit_keys': audit_keys(root),
                  'reason_key_table': reason_key_table(a1, b_document, pairs, root),
                  'assumption_catalogue': assumption_catalogue(a1, pairs, root), 'no_target': [],
                  'r3': R3_DEPARTURES, 'r2_departures': ['browInnerUp'], 'm3_flat_links': [],
                  'm3_rounding': M3_ROUNDING, 'm10_not_available': M10_NOT_AVAILABLE,
                  'm10b_not_available': M10B_NOT_AVAILABLE, 'm11_differences': M11_DIFFERENCES,
                  'm7_mutations': ab_mutations.MUTATIONS},
        'acceptance': {}, 'changes': [],
        'pins': {'a1_sha256': A1_SHA256, 'b_pack_sha256': sha256_bytes(b_path.read_bytes()),
                 'code': code_hashes(root), 'runtime': runtime_pins(root), 'rigs': ab_geometry.rig_pins()},
        'not_registered': sorted(set(B_PAIRS) - set(pairs)),
    }
    oracle, fixed = ab_oracle.Oracle(b_document), ab_frames.fixed_families(abreg)
    flat = set()
    for pair in pairs.values():
        impulse = fixed[f'impulse:{pair["source"]}']
        flat |= {tuple(link) for link in flat_links(b_document, pair, impulse, oracle_results(oracle, pair, impulse))}
    abreg['lists']['m3_flat_links'] = sorted(map(list, flat))
    abreg['lists']['no_target'] = rest_inputs(b_document, pairs)
    abreg['a1_figures'] = a1_figures(abreg, a1)
    abreg['seed_root'] = seed_root(abreg)
    return abreg


def rest_inputs(document: dict, pairs: dict) -> list[dict]:
    """Source inputs that write a bridge class whose pose is the rest face (every weight 0) and have no link to any
    output of the pair (weight-0 inputs are not links).

    Their impulse moves no output, by design, so M4's observed loss leaves them out.
    """
    found = []
    for name, pair in sorted(pairs.items()):
        for bridge, *_ in pair.get('bridges', []):
            rules = next(m['rules'] for m in document['mappings'] if m['id'] == bridge)
            weights = {}
            for rule in rules:
                if rule['operator']['id'] == 'weighted_sum':
                    for weight, sid in zip(rule['operator']['weights'], rule['inputs']):
                        weights.setdefault(sid, set()).add(weight)
            helpers = {r['outputs'][0]: r['inputs'][0] for r in rules if r['operator']['id'] == 'affine'}
            still = {helpers[h] for h, ws in weights.items() if ws == {0.0} and h in helpers}
            in_rules = rules_by_output(document, [h[0] for h in pair['in_hops']])
            outputs = [o for h in pair['out_hops'] for o in rcef_route.map_ends(
                next(m['rules'] for m in document['mappings'] if m['id'] == h[0]))[1]]
            linked = {s for s, _ in links(document, pair, outputs)}
            for cls in sorted(still):
                if cls in in_rules:
                    for sid in sorted(upstream(in_rules, cls)[1] - linked):
                        found.append({'pair': name, 'input': sid, 'reason': (
                            f'{sid.rsplit(".", 1)[1]} reaches {bridge} only as {cls.rsplit(".", 1)[1]}, whose pose '
                            'is the rest face: every weight of it in the bridge is 0')})
    return found


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
    if 'rigs' in pins and pins['rigs'] != ab_geometry.rig_pins():
        problems.append('the rig files pinned in examples/rigs.py and examples/ict_facekit.py differ from the pins')
    for name in ('r2', 'r5'):
        entry = abreg.get('fixed_inputs', {}).get(name)
        if entry and sha256_bytes((root / entry['path']).read_bytes()) != entry['sha256']:
            problems.append(f'{entry["path"]} does not have the SHA-256 the registration pins')
    if 'FB2 -> ARKit' in abreg['pairs'] and 'r2' not in abreg.get('fixed_inputs', {}):
        problems.append(f'M5 R2 reads {R2_FILE}, but the registration does not pin it')
    return problems + ab_a3.fixture_problems()


def run(abreg_path: Path, out: Path, root: Path = ROOT, b_path: Path | None = None, dry_run: bool = False,
        rig_caches: dict | None = None) -> dict:
    """Run a registration. rig_caches ({rig name: cache folder}) lets M6 pose the rigs; without them M6 is pending."""
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
    report = {'metrics': {}, 'failures': {}, 'refusals': [], 'observed_loss': [], 'assumptions': [],
              'regression': sorted(regression)}

    def record(metric, row, counts, failures=()):
        report['metrics'].setdefault(metric, []).append({**row, **counts})
        report['failures'].setdefault(metric, []).extend([[*row.values(), *f] for f in failures])

    # Route cross-check: the maps B runs are the maps the registration froze.
    routes = {}
    for name, pair in abreg['pairs'].items():
        route = rcef_route.Route(pair['source'], pair['target'], pack=b_pack)
        hops = route_hops(route)
        if hops != {k: pair.get(k, []) for k in hops}:
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
        declared = {e['input'] for e in abreg['lists']['no_target'] if e['pair'] == name}
        lost = observed_loss(b_runs[name, impulse_name], families[impulse_name], declared)
        report['observed_loss'] += [['B', name, sid] for sid in lost]
        record('M4', {'pair': name, 'arm': 'B'}, {'observed_loss': len(lost), 'baseline': '', 'matches_baseline': ''})
        seeded = {f: b_runs[name, f] for f in by_source[pair['source']]
                  if any(s['name'] == f for s in abreg['families'])}
        channels = {s['name']: set(s['channels']) for s in abreg['families'] if 'channels' in s}
        record('M3 coverage', {'pair': name}, *m3_coverage(
            b_document, pair, families[impulse_name], b_runs[name, impulse_name], o_runs[name, impulse_name],
            abreg['lists']['m3_flat_links'], seeded, channels))
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
        a3a1_runs = {}
        for family, values in expected.items():
            if ('FACS -> FB2', family) in b_runs:
                record('M10', {'family': family}, *facs_compare(b_runs['FACS -> FB2', family], values,
                                                                abreg['lists']['m10_not_available']))
            if ('FACS -> ARKit', family) in b_runs:
                flags = {'isValid': True, 'isEyeFollowingBlendshapesValid': True}
                a3a1 = a3a1_runs[family] = run_route(a1, [{'values': v, 'flags': flags} for v in values])
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
        r2_path = root / abreg['fixed_inputs'].get('r2', {}).get('path', R2_FILE)
        with r2_path.open(encoding='utf-8', newline='') as handle:
            rows = list(csv.DictReader(handle))
        record('M5 R2', {'reference': 'R2'}, *r2(b_document, abreg['pairs']['FB2 -> ARKit'], rows,
                                                 abreg['lists']['r2_departures']))
    if (R3_PAIR, f'r3:{R3_KINDS["fb2_to_ue"]}') in b_runs:
        reference = json.loads((root / abreg['fixed_inputs']['r3']['path']).read_text(encoding='utf-8'))
        record('M8 R3', {'reference': 'R3'}, *r3(b_runs[R3_PAIR, f'r3:{R3_KINDS["fb2_to_ue"]}'], reference,
                                                 abreg['lists']['r3']))
    lists = abreg['lists']
    if lists.get('reason_key_table'):
        rows, failures = timed('M4 keys', m4_keys, abreg, a1_document, b_document, root)
        for row in rows:
            record('M4 keys', {'pair': row['pair']}, {k: v for k, v in row.items() if k != 'pair'},
                   [f[1:] for f in failures if f[0] == row['pair']])
    if lists.get('assumption_catalogue'):
        rows, failures, entries = timed('M4b', m4b, abreg, a1_document, b_document)
        for row in rows:
            record('M4b', {'pair': row['pair']}, {k: v for k, v in row.items() if k != 'pair'},
                   [f[1:] for f in failures if f[0] == row['pair']])
        report['assumptions'] = entries
    if lists.get('m7_mutations'):
        rows, failures = timed('M7', ab_mutations.m7, abreg, b_document, a1_document, families)
        for row in rows:
            record('M7', {'mutation': row['mutation']}, {k: v for k, v in row.items() if k != 'mutation'},
                   [f[1:] for f in failures if f[0] == row['mutation']])
    r5 = abreg.get('fixed_inputs', {}).get('r5')
    if r5 and 'ARKit -> FACS' in abreg['pairs']:
        reference = json.loads((root / r5['path']).read_text(encoding='utf-8'))
        rows, failures = m11(b_document, abreg['pairs']['ARKit -> FACS'], reference, lists['m11_differences'])
        for row in rows:
            record('M11', {'line': row['line']}, {k: v for k, v in row.items() if k != 'line'},
                   [f[1:] for f in failures if f[0] == row['line']])
    if rig_caches and 'rigs' in abreg['pins']:
        posed = timed('M6 rigs', ab_geometry.load, rig_caches)
        arms = [('FB2 -> ARKit', f, a1_runs.get(('FB2 -> ARKit', f))) for f in by_source.get('openxr.fb2', [])
                if f.startswith(('csv:', 'goldens:'))]
        if 'facs.code' in abreg['sources']:
            arms += [('FACS -> ARKit', f, a3a1_runs.get(f)) for f in FACS_FAMILIES]
        for name, rig in posed.items():
            problems = timed('M6 oracles', ab_geometry.oracle_problems, rig)
            for pair_name, family, other in arms:
                if other is None or (pair_name, family) not in b_runs:
                    continue
                counts = timed('M6', ab_geometry.vertex_difference, rig, other, b_runs[pair_name, family])
                record('M6', {'pair': pair_name, 'rig': name, 'family': family},
                       {**counts, 'arkit_outputs_bound': ab_geometry.bound(rig), 'oracle_problems': len(problems)},
                       [[p] for p in problems])
    timings['total'] = round(time.perf_counter() - started, 3)
    return write_results(out, abreg, report, frame_sums, timings, pins, dry_run, b_path, root)


# ---------------------------------------------------------------- results

GATES = {'M1': ('value_differences', 'sign_differences'), 'B equals O': ('differences',), 'M1s': ('differences',),
         'M2': ('violations',), 'M2c': ('shortfall',), 'M3 exact': ('errors', 'over_bound'),
         'M3 coverage': ('violations',),
         'M5 R2': ('differences',), 'M10': ('value_differences', 'coverage_violations', 'b_refusals'),
         'M10b': ('value_differences', 'coverage_violations'), 'M4 keys': ('shortfall', 'unlisted_added'),
         'M4b': ('shortfall',), 'M7': ('missed', 'setup_errors')}
REPORT_ONLY = ('M2b', 'M8', 'M8 R3', 'M6', 'M11')


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
                'M10': ('family', FACS_FAMILIES), 'M10b': ('family', FACS_FAMILIES),
                'M4 keys': ('pair', list(A1_PAIRS)), 'M4b': ('pair', list(A1_PAIRS))}
    missing = {}
    for metric, (key, names) in required.items():
        if metric not in rows and metric in PENDING:
            continue  # shown as pending instead
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
    files['assumptions.csv'] = csv_text([['pair', 'A1 rule', 'template', 'B keys by side, or superseded'],
                                         *report['assumptions']])
    lines = ['# A/B comparison: scoreboard', '']
    if dry_run:
        lines += ['The pivot route (B) against the direct maps (A1) and the other arms.', '',
                  '**Dry run: not a registered result.** Its registration and ledger line need not be committed, so '
                  'no frame here is held out.', '']
    else:
        lines += ['The pivot route (B) against the direct maps (A1) and the other arms. The held-out frames are held '
                  'out by procedure: the registration and its ledger line were committed before this run.', '']
    if report['regression']:
        lines += ['Frames seen before the change (regression families, made again by the generator each earlier '
                  f'freeze pinned): {", ".join(report["regression"])}.', '']
    lines += ['| Metric | Threshold | Status |', '|---|---|---|']
    for metric in sorted(gate_statuses):
        threshold = THRESHOLDS.get(metric, 'report only')
        shown = gate_statuses[metric] + (f' (no rows for {", ".join(missing[metric])})' if metric in missing else '')
        lines.append(f'| {metric} | {threshold} | {shown} |')
    pending = {m: needs for m, needs in PENDING.items() if m not in report['metrics']}
    for metric, needs in pending.items():
        lines.append(f'| {metric} | needs {needs} | pending |')
    lines += ['', '| Pair | Evidence status (A1 / B) | M2c shortfall | M4b | External reference |',
              '|---|---|---|---|---|']
    m2b_rows = {r['pair']: r for r in report['metrics'].get('M2b', [])}
    m2c_rows = {r['pair']: r for r in report['metrics'].get('M2c', [])}
    m4b_rows = {r['pair']: r for r in report['metrics'].get('M4b', [])}
    for name in abreg['pairs']:
        reference = 'A1' if name in A1_PAIRS else 'A2' if name in A2_PAIRS else (
            'A3' if name.startswith('FACS -> ') and name.split(' -> ')[1] in ('FB2', 'ARKit') else
            'no external reference')
        evidence = f'{m2b_rows[name]["a1"]} / {m2b_rows[name]["b"]}' if name in m2b_rows else ''
        shortfall = m2c_rows[name]['shortfall'] if name in m2c_rows else ''
        if name in m4b_rows:
            m4b_cell = f'shortfall {m4b_rows[name]["shortfall"]} of {m4b_rows[name]["entries"]}'
        else:
            m4b_cell = 'pending' if 'M4b' not in report['metrics'] else 'no A1 rule'
        lines.append(f'| {name} | {evidence} | {shortfall} | {m4b_cell} | {reference} |')
    files['scoreboard.md'] = '\n'.join(lines) + '\n'
    for name, text in files.items():
        (out / name).write_text(text, encoding='utf-8')
    passed = all(s in ('pass', 'report') for s in gate_statuses.values()) and not pending and not dry_run
    manifest = {'id': abreg['id'], 'version': abreg['version'], 'kind': abreg['kind'],
                'abreg_sha256': abreg_sha256(abreg), 'seed_root': abreg['seed_root'], 'dry_run': dry_run,
                'pin_problems': pins, 'passed': passed, 'statuses': gate_statuses, 'row_statuses': row_statuses,
                'missing_rows': missing, 'pending': pending,
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
    p.add_argument('--rig', action='append', default=[], metavar='NAME=DIR',
                   help=f'a rig cache for M6, for each of {", ".join(ab_geometry.RIGS)}')
    commands.add_parser('check')
    commands.add_parser('a1-loss')
    p = commands.add_parser('r5')
    p.add_argument('readme', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'draft':
        if args.out.resolve().parent == (ROOT / 'ab').resolve():
            raise SystemExit('write a draft outside ab/: every registration in ab/ needs a ledger line')
        args.out.write_text(json.dumps(draft(ROOT, args.b_pack, args.date), indent=1, sort_keys=True) + '\n',
                            encoding='utf-8')
        print(f'{args.out}: review it and fill in the frozen lists before you register it')
    elif args.command == 'run':
        caches = {name: Path(folder).expanduser() for name, folder in (r.split('=', 1) for r in args.rig)}
        manifest = run(args.abreg, args.out, ROOT, args.b_pack, args.dry_run, caches)
        print(json.dumps(manifest['statuses'], indent=1, sort_keys=True))
        return 0 if manifest['passed'] else 1
    elif args.command == 'r5':
        print(f'{R5_FILE}: {len(write_r5(args.readme)["rows"])} rows')
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
