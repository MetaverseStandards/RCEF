# SPDX-License-Identifier: MIT
"""Viseme poses with a perceptual gate: each META viseme class as one combination of ARKit shapes, fitted on several
Rocketbox rigs, with visible mouth features for the classes that the whole-mesh shape test cannot pass.

The fit gives, for each canonical viseme class c and each canonical expression signal j that the bridge writes,
a pose value pose[c][j] in [0, 1]. A class at weight 1 is meant to give expression j the value pose[c][j]. The
record curves are [[0, 0], [1, pose]].

Rig sets: tools/calibration/viseme_rigs.json, one round per record version, each chosen by a rule before its rigs
were downloaded. This tool makes viseme-poses.rocketbox-features (round 3). The fit loads only the training rigs;
the held-out step loads only the held-out rigs.

Fit (mesh geometry only, no renders):
- basis: the ARKit shapes that the ARKit in-map reads into the groups in GROUPS (37 shapes); blink, gaze, the
  sideways jaw and mouth shifts and tongueOut are left out. Each Left and Right pair shares one weight, so the
  basis has 24 columns (13 pairs and 11 single shapes);
- region: on each rig, every vertex except the tongue: the vertices that the rig's tongueOut shape moves by more
  than 1% of its largest move;
- every class: one set of ARKit weights u in [0, 1] for all training rigs, with the smallest largest whole-mesh
  error e_r(u) = |A_r u - t_r| / |t_r| (Lawson reweighting of bounded least squares, ITERATIONS rounds, each by
  cyclic coordinate descent to a change below TOLERANCE);
- the classes in FEATURES: from there, Gauss-Newton steps (with Levenberg damping) on the sum over training rigs of
  MU e_r(u)^2 plus the squared feature errors, each divided by its tolerance (a range feature: the distance from
  the middle of its range, divided by half its width);
- the weights are rounded to 3 decimals and go to their canonical signals through the ARKit in-map (copies).

Features (Geometry.mouth): the signed lip opening on the mid line, the forward movement of the lips, the width
between the mouth corners as a ratio to the neutral width, the drop of the lower teeth, and the distance from the
upper teeth to the lower lip, all from landmark vertices that the rig's own ARKit shapes pick out. Tolerances of
difference features: the largest distance of a training rig's own viseme feature from the training median, at
least FLOOR; they are frozen in the record.

The cv step reproduces the choice of features and of MU by leave-one-rig-out cross-validation within the training
rigs, and says whether the neutral face would pass each feature set.

Held-out evaluation (the held-out rigs, which the fit never loads): for each class and rig, one condition per
held-out seed. The class gets a weight w in [0.2, 1] from the seed; in half the conditions the rest class sil gets
1 - w. The frozen poses give canonical values clamp(sum_c pose[c][j] * weight_c, 0, 1); the ARKit out-maps of the
pack turn them into the rig's ARKit weights. Shape cell error: |reconstruction - target| / |target - neutral|,
Euclidean norms over the rig's region, where the target is the rig's own viseme shapes at the same weights; neutral
is the error at weight 0. Feature cell error, for the classes in FEATURES, per feature and condition: the absolute
difference between the feature of the reconstruction and of the target (difference), or how far the feature of the
reconstruction lies outside its range (range); the whole-face guard is the shape error, range [0, 1]. A class
passes if its shape cells pass on every held-out rig, or if all its feature cells pass (largest error within the
tolerance) on every held-out rig.

Usage:
  viseme_poses.py cv --rig-cache DIR                      # leave-one-rig-out choice of features and MU
  viseme_poses.py freeze --rig-cache DIR [--reason TEXT]  # commit the record and FREEZES before the next step
  viseme_poses.py heldout --rig-cache DIR [--out summary.json]
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'examples')]
import check  # noqa: E402
import provenance  # noqa: E402

RECORD_ID = 'viseme-poses.rocketbox-features'
RECORD = ROOT / 'calibration' / f'{RECORD_ID}.cal'
LEDGER = ROOT / 'calibration' / 'FREEZES'
PACK = ROOT / 'generated/rcef.pack.json'
GROUPS = ('face', 'cheek_puff', 'jaw_thrust', 'chin_raise_upper_lip')
# The maps the fit reads: META into the canonical viseme classes, ARKit into and out of the canonical expression set.
CLASS_MAP, IN_MAP, OUT_MAP = 'visemes.to_rcef_viseme', 'arkit.to_rcef_expression', 'rcef_expression.to_arkit'
CLASS_GROUPS = ('viseme_vowel', 'viseme_consonant', 'viseme_rest')
META = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')
REST = 'rcef.canonical_viseme.sil'
TOLERANCE = 1e-13
ITERATIONS = 100
TONGUE = 0.01
DECIMALS = 3
HELD_OUT = 24
LOW_WEIGHT = 0.2
BOUNDS = {'median': 0.5, 'p95': 0.5, 'neutral': 0.01}
COPY = check.COPY
V = 'rcef.canonical_viseme.'
# Mouth landmarks, in metres: the lips are the vertices that mouthFunnel moves by more than LIP of its largest move;
# MIDLINE is the half-width of the mid-line band and MOUTH the reach around the mouth.
LIP, MIDLINE, MOUTH = 0.2, 0.003, 0.01
# The perceptual gate, chosen by the cv step on the training rigs: per class, (feature, kind, range or None).
# bilabial: the lips closed on the mid line (a hard range in mm) and drawn back like the rig's own; the others as
# their own viseme. labiodental and coronal_nasal_lateral have no gate (see the cv step).
CLOSED = (-2.0, 0.5)
FEATURES = {
    V + 'bilabial': [('lip_opening_mm', 'range', CLOSED), ('lip_protrusion_mm', 'difference', None)],
    V + 'vowel_close_rounded': [('corner_width_ratio', 'difference', None), ('lip_protrusion_mm', 'difference', None)],
    V + 'vowel_mid_spread': [('corner_width_ratio', 'difference', None), ('lip_opening_mm', 'difference', None)],
    V + 'alveolar_sibilant': [('lip_opening_mm', 'difference', None), ('jaw_drop_mm', 'difference', None)],
}
GUARD = ('whole_face_error', 'range', (0.0, 1.0))
FLOOR = {'mm': 0.5, '1': 0.02}
UNITS = {'lip_opening_mm': 'mm', 'lip_protrusion_mm': 'mm', 'corner_width_ratio': '1', 'jaw_drop_mm': 'mm',
         'teeth_to_lower_lip_mm': 'mm', 'whole_face_error': '1'}
DESCRIPTIONS = {
    'lip_opening_mm': 'signed vertical opening of the lips on the mid line, in mm: the lowest upper-lip landmark '
                      'minus the highest lower-lip landmark (negative when the inner edges overlap)',
    'lip_protrusion_mm': 'forward movement of the mid-line lip landmarks from neutral, mean, in mm',
    'corner_width_ratio': 'distance between the two mouth-corner landmarks, divided by the neutral distance',
    'jaw_drop_mm': 'downward movement of the lower-teeth landmarks from neutral, mean, in mm',
    'teeth_to_lower_lip_mm': 'smallest distance from an upper-teeth landmark to a lower-lip landmark, in mm',
    'whole_face_error': 'the whole-mesh shape error of the condition (as in the shape cells); at most 1 means the '
                        'reconstruction is no further from the target than the neutral face is',
}
MU = 1.0
GAUSS_NEWTON, STEP = 8, 0.02
RIG_SETS = ROOT / 'tools/calibration/viseme_rigs.json'
DATA_FILES = [RIG_SETS.relative_to(ROOT).as_posix()]
SETS = json.loads(RIG_SETS.read_text(encoding='utf-8'))
TRAINING, HELD_OUT_RIGS = SETS['rounds'][-1]['training'], SETS['rounds'][-1]['held_out']
INPUT_FILES = {**{f'Microsoft Rocketbox {a}_facial.fbx': f'{a}_facial.fbx' for a in TRAINING + HELD_OUT_RIGS},
               'Microsoft Rocketbox LICENSE.md': 'ROCKETBOX_LICENSE.md'}
PACK_INPUT = 'RCEF generated/rcef.pack.json (the ARKit in-maps and out-maps)'
STIMULUS = ('class weight w in [0.2, 1] from the held-out seed; in half the conditions the rest class sil gets '
            "1 - w; the rig's ARKit weights from the frozen poses through the ARKit out-maps")
q = json.dumps


# ---------------------------------------------------------------------------------------------- pure parts

def dot(a, b) -> float:
    return math.fsum(x * y for x, y in zip(a, b))


def gram(columns: list[list[float]]) -> list[list[float]]:
    k = len(columns)
    g = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(i, k):
            g[i][j] = g[j][i] = dot(columns[i], columns[j])
    return g


def quadratic(w: list[float], g: list[list[float]]) -> float:
    return math.fsum(w[i] * g[i][j] * w[j] for i in range(len(w)) for j in range(len(w)))


def bounded_least_squares(g: list[list[float]], b: list[float], tolerance: float = TOLERANCE,
                          limit: int = 1_000_000, start: list[float] | None = None) -> list[float]:
    """The u in [0, 1]^k that minimises u'Gu - 2b'u, by cyclic coordinate descent from `start` (default u = 0).

    Each step sets one weight to its exact minimiser with the others fixed, clipped to [0, 1]. The objective is
    convex, so the sweeps converge; they stop when no weight changes by more than `tolerance`.
    """
    k = len(b)
    u = list(start) if start else [0.0] * k
    for _ in range(limit):
        change = 0.0
        for i in range(k):
            if g[i][i] <= 0.0:
                continue
            rest = math.fsum(g[i][j] * u[j] for j in range(k) if j != i)
            new = min(1.0, max(0.0, (b[i] - rest) / g[i][i]))
            change, u[i] = max(change, abs(new - u[i])), new
        if change <= tolerance:
            return u
    raise SystemExit('the pose fit did not converge')


def minimax(systems: list[tuple[list[list[float]], list[float], float]], iterations: int = ITERATIONS,
            tolerance: float = TOLERANCE) -> list[float]:
    """Weights u in [0, 1]^k that approach the smallest largest error |A_r u - t_r| / |t_r| over the systems.

    Each system is (G_r, b_r, t_r't_r) with G_r = A_r'A_r and b_r = A_r't_r. Lawson's reweighting: each round fits
    the bounded least squares of the sum of w_r e_r(u)^2, then multiplies each w_r by e_r and normalises the w_r to
    sum to their number. Systems with t_r = 0 are left out; with none left, u = 0.
    """
    live = [s for s in systems if s[2] > 0.0]
    k = len(systems[0][1])
    u, weights = [0.0] * k, [1.0] * len(live)
    for _ in range(iterations if live else 0):
        g = [[math.fsum(w / tt * gr[i][j] for w, (gr, _, tt) in zip(weights, live)) for j in range(k)]
             for i in range(k)]
        b = [math.fsum(w / tt * br[i] for w, (_, br, tt) in zip(weights, live)) for i in range(k)]
        u = bounded_least_squares(g, b, tolerance, start=u)
        errors = [error(u, *system) for system in live]
        total = math.fsum(w * e for w, e in zip(weights, errors))
        if total == 0.0:
            break
        weights = [w * e * len(live) / total for w, e in zip(weights, errors)]
    return u


def error(u: list[float], g: list[list[float]], b: list[float], tt: float) -> float:
    """|A u - t| / |t| from G = A'A, b = A't and t't."""
    return ratio(quadratic(u, g) - 2 * dot(u, b) + tt, tt)[0]


def chosen(sets: dict) -> list[tuple[list[str], list[str]]]:
    """(training, held out) of each round that the rules in viseme_rigs.json give for its candidates and
    replacements.

    For each sex, the candidates in the order of the SHA-256 of their name fill 10 slots in turn: 2 held out in
    round 1, 4 training in round 1, 2 held out in round 2 and 2 held out in round 3. A replaced rig's slot goes to the
    next unused candidate of the same sex after the slots. Round 2 trains on round 1's training rigs; round 3 on
    those and every rig held out in rounds 1 and 2.
    """
    replaced = {r['name'] for r in sets['replaced']}
    slots = {}
    for sex in ('Female', 'Male'):
        order = sorted((c['name'] for c in sets['candidates'][sex]),
                       key=lambda n: hashlib.sha256(n.encode('utf-8')).hexdigest())
        spare = iter(order[10:])
        slots[sex] = [n if n not in replaced else next(x for x in spare if x not in replaced) for n in order[:10]]

    def take(a, b):
        return [n for sex in ('Female', 'Male') for n in slots[sex][a:b]]
    first = (['Female_Adult_01', 'Male_Adult_01'] + take(2, 6), take(0, 2))
    second = (first[0], take(6, 8))
    third = (first[0] + first[1] + second[1], take(8, 10))
    return [first, second, third]


def unit_draws(seed: int, channel: str) -> tuple[float, bool]:
    """A uniform number in [0, 1) and a fair bit, from the SHA-256 of '<seed>:<channel>'."""
    digest = hashlib.sha256(f'{seed}:{channel}'.encode()).digest()
    return int.from_bytes(digest[:8], 'big') / 2 ** 64, bool(digest[8] & 1)


def conditions(seeds: list[int], channel: str) -> list[dict[str, float]]:
    """One frame of canonical class weights per seed: the class at w in [0.2, 1], and in half of them sil at 1 - w."""
    frames = []
    for seed in seeds:
        u, blend = unit_draws(seed, channel)
        w = round(LOW_WEIGHT + (1 - LOW_WEIGHT) * u, 6)
        frames.append({channel: w, REST: round(1 - w, 6)} if blend and channel != REST else {channel: w})
    return frames


def bridge(poses: dict[str, dict[str, float]], frame: dict[str, float]) -> dict[str, float]:
    """Canonical expression values clamp(sum_c pose[c][j] * weight_c, 0, 1) for every j the poses name."""
    outputs = next(iter(poses.values()))
    return {j: min(1.0, max(0.0, math.fsum(poses[c][j] * w for c, w in frame.items()))) for j in outputs}


def ratio(error2: float, motion2: float) -> tuple[float, bool]:
    """|error| / |motion| from their squares; (1.0, True), a failure, if only the error is non-zero."""
    error, motion = math.sqrt(max(error2, 0.0)), math.sqrt(max(motion2, 0.0))
    if motion == 0.0:
        return (0.0, False) if error == 0.0 else (1.0, True)
    return error / motion, False


def p95(values: list[float]) -> float:
    """The nearest-rank 95th percentile, as in examples/rig_gains.py."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def cell(errors: list[float], failures: int, neutral: float) -> dict:
    return {'failures': failures, 'median': round(statistics.median(errors), 6), 'p95': round(p95(errors), 6),
            'neutral': round(neutral, 6)}


# ---------------------------------------------------------------------------------------------- pack and rigs

def pack_document() -> dict:
    return json.loads(PACK.read_text(encoding='utf-8'))


def correspondences(document: dict) -> tuple[dict[str, str], dict[str, list[str]], list[str]]:
    """META viseme -> canonical class; ARKit name -> canonical signals; and the canonical signals in pack order."""
    maps = {m['id']: m['rules'] for m in document['mappings']}
    group = {s['id']: s.get('metadata', {}).get('group') for s in document['signals']}
    classes, arkit, signals = {}, {}, []
    for rule in (r for r in maps[CLASS_MAP] if group.get(r['outputs'][0]) in CLASS_GROUPS):
        if rule['operator'] != COPY:
            raise SystemExit(f'{rule["id"]} is not a copy')
        classes[rule['inputs'][0][len(META[0]):-len(META[1])]] = rule['outputs'][0]
    for name in GROUPS:
        for rule in (r for r in maps[IN_MAP] if group.get(r['outputs'][0]) == name):
            if rule['operator'] != COPY:
                raise SystemExit(f'{rule["id"]} is not a copy')
            arkit.setdefault(rule['inputs'][0].split('.', 2)[2], []).append(rule['outputs'][0])
            signals.append(rule['outputs'][0])
    return classes, arkit, signals


class Geometry:
    """A Rocketbox rig's vertex displacements (rig units) for its viseme and ARKit shapes, without the tongue."""

    def __init__(self, cache: Path, avatar: str, basis: list[str]):
        import msf_character_tools as msf
        import rigs
        self.msf, self.rigs = msf, rigs
        self.avatar = avatar
        which, _, number = avatar.split('_')
        self.rig = rigs.load(rigs.rocketbox_name(which, number), cache)
        count = len(self.rig.targets)
        rest = self._positions([0.0] * count)
        arkit = {a: i for i, a, _ in self.rig.shapes}

        def delta(index):
            vector = [0.0] * count
            vector[index] = 1.0
            return [p - r for p, r in zip(self._positions(vector), rest)]
        tongue = delta(arkit['tongueOut'])
        moved = [math.hypot(*tongue[3 * v:3 * v + 3]) for v in range(len(rest) // 3)]
        # Above 1% of the largest move: the tongue's vertices move by centimetres, the rest by float noise.
        self.keep = [v for v, m in enumerate(moved) if m <= TONGUE * max(moved)]
        self.tongue = len(rest) // 3 - len(self.keep)
        self.rest = self._region(rest)
        self.basis = [self._region(delta(arkit[a])) for a in basis]
        self.arkit = {a: self._region(delta(arkit[a]))
                      for a in ('jawOpen', 'mouthFunnel', 'mouthSmileLeft', 'mouthSmileRight')}
        if len(self.rig.visemes) != 15:
            raise SystemExit(f'{avatar} has {len(self.rig.visemes)} viseme shapes, not 15')
        self.visemes = {meta: self._region(delta(i)) for meta, i in self.rig.visemes.items()}

    def _positions(self, vector):
        geometry = self.rigs.require(self.msf.evaluate_geometry(self.rig.snapshot,
                                                                morph_weights={self.rig.node: vector}))
        return [c for instance in geometry.instances for primitive in instance['primitives']
                for p in primitive['positions'] for c in p]

    def _region(self, values):
        return [values[3 * v + k] for v in self.keep for k in range(3)]

    def systems(self, metas: list[str], columns: list[list[float]] | None = None,
                scale: list[float] | None = None) -> tuple[list[list[float]], dict[str, tuple]]:
        """G and, per viseme, (G, b, t't) of the least-squares problem; with `scale`, every coordinate is weighted."""
        columns = columns or self.basis
        weighted = [[x * w for x, w in zip(c, scale)] for c in columns] if scale else columns
        g = [[dot(a, c) for c in columns] for a in weighted]
        return g, {m: (g, [dot(c, self.visemes[m]) for c in weighted],
                       dot(self.visemes[m], [x * w for x, w in zip(self.visemes[m], scale)] if scale else
                           self.visemes[m])) for m in metas}


class Mouth:
    """The mouth landmarks of one rig, and its features evaluated on those vertices only.

    Landmarks are indices into the rig's region (without the tongue), picked out by the rig's own ARKit shapes, so the
    rule applies to any Rocketbox rig (x across the face, y backwards, z up, in metres):
    - centre: the vertex that jawOpen moves most;
    - lips: the vertices that mouthFunnel moves by more than LIP of its largest move, within MOUTH of the centre's
      height; upper lip if jawOpen moves them by less than 0.3 of its largest move, lower lip if by more than 0.6;
    - mid line: |x| <= MIDLINE; the lip-opening sets use the lips above, the protrusion sets the lips within 2 MOUTH
      of the centre's height;
    - corners: the lip vertices that mouthSmileLeft and mouthSmileRight move most;
    - upper teeth: vertices that jawOpen and mouthFunnel each move by less than 0.05 of their largest move, with
      |x| <= MOUTH, behind the front of the mid-line upper lip by at most 2 MOUTH, and between MOUTH below the
      centre's height and MOUTH / 2 above the lowest mid-line upper-lip vertex;
    - lower teeth: the same box, but within 1.5 MOUTH of the centre's height and moved by jawOpen by more than 0.8.
    """

    def __init__(self, geometry: 'Geometry', columns: list[list[float]]):
        def moved(shape):
            values = [math.hypot(*shape[3 * v:3 * v + 3]) for v in range(len(shape) // 3)]
            top = max(values)
            return [x / top for x in values]
        jaw, funnel = moved(geometry.arkit['jawOpen']), moved(geometry.arkit['mouthFunnel'])
        point = [tuple(geometry.rest[3 * v:3 * v + 3]) for v in range(len(geometry.rest) // 3)]
        centre = point[max(range(len(jaw)), key=jaw.__getitem__)]

        def lips(reach):
            return [v for v, f in enumerate(funnel) if f > LIP and abs(point[v][2] - centre[2]) <= reach]
        near, wide = lips(MOUTH), lips(2 * MOUTH)
        mid = [v for v in near if abs(point[v][0]) <= MIDLINE]
        sets = {'upper': [v for v in mid if jaw[v] < 0.3], 'lower': [v for v in mid if jaw[v] > 0.6],
                'lips': [v for v in wide if abs(point[v][0]) <= MIDLINE and (jaw[v] < 0.3 or jaw[v] > 0.6)],
                'lower_lip': [v for v in near if jaw[v] > 0.6 and abs(point[v][0]) <= MOUTH],
                'corners': [max(near, key=moved(geometry.arkit[side]).__getitem__)
                            for side in ('mouthSmileLeft', 'mouthSmileRight')]}
        if not sets['upper'] or not sets['lower']:
            raise SystemExit(f'{geometry.avatar}: no mid-line lip landmarks')
        front = min(point[v][1] for v in sets['upper'])
        edge = min(point[v][2] for v in sets['upper'])

        def box(v, p):
            return funnel[v] < 0.05 and abs(p[0]) <= MOUTH and front < p[1] <= front + 2 * MOUTH
        sets['teeth'] = [v for v, p in enumerate(point) if box(v, p) and jaw[v] < 0.05
                         and centre[2] - MOUTH <= p[2] <= edge + MOUTH / 2]
        sets['lower_teeth'] = [v for v, p in enumerate(point) if box(v, p) and jaw[v] > 0.8
                               and abs(p[2] - centre[2]) <= 1.5 * MOUTH]
        if not sets['teeth'] or not sets['lower_teeth']:
            raise SystemExit(f'{geometry.avatar}: no teeth landmarks')
        self.sets = sets
        self.vertices = sorted({v for vs in sets.values() for v in vs})

        def sub(values):
            return {v: tuple(values[3 * v:3 * v + 3]) for v in self.vertices}
        self.rest = sub(geometry.rest)
        self.columns = [sub(c) for c in columns]
        self.visemes = {m: sub(d) for m, d in geometry.visemes.items()}
        self.targets = {}

    def pose(self, weights: list[float]) -> dict:
        """Displacements of the landmarks for the column weights."""
        return {v: tuple(math.fsum(w * c[v][k] for w, c in zip(weights, self.columns) if w) for k in range(3))
                for v in self.vertices}

    def own(self, frame: dict[str, float]) -> dict:
        """Displacements of the landmarks for the rig's own viseme shapes at the weights of `frame` (META names)."""
        return {v: tuple(math.fsum(w * self.visemes[m][v][k] for m, w in frame.items()) for k in range(3))
                for v in self.vertices}

    def target(self, meta: str) -> dict[str, float]:
        """The features of the rig's own viseme `meta` at weight 1."""
        if meta not in self.targets:
            self.targets[meta] = self.features(self.own({meta: 1.0}))
        return self.targets[meta]

    def features(self, displacement: dict) -> dict[str, float]:
        p = {v: tuple(r + d for r, d in zip(self.rest[v], displacement[v])) for v in self.vertices}
        s = self.sets
        left, right = s['corners']
        return {
            'lip_opening_mm': 1000 * (min(p[v][2] for v in s['upper']) - max(p[v][2] for v in s['lower'])),
            'lip_protrusion_mm': 1000 * statistics.mean(-(p[v][1] - self.rest[v][1]) for v in s['lips']),
            'corner_width_ratio': math.dist(p[left], p[right]) / math.dist(self.rest[left], self.rest[right]),
            'jaw_drop_mm': 1000 * statistics.mean(-(p[v][2] - self.rest[v][2]) for v in s['lower_teeth']),
            'teeth_to_lower_lip_mm': 1000 * min(math.dist(p[a], p[b]) for a in s['teeth'] for b in s['lower_lip'])}


# ---------------------------------------------------------------------------------------------- perceptual gate

def feature_error(kind: str, span, value: float, target: float) -> float:
    """difference: |value - target|; range: how far value lies outside span (0 inside)."""
    if kind == 'range':
        return max(0.0, span[0] - value, value - span[1])
    return abs(value - target)


def tolerances(mouths: dict, meta: str, spec: list) -> dict[str, float]:
    """For each difference feature: the largest distance of a rig's own viseme feature from the median over the
    rigs, at least FLOOR, rounded up to 3 decimals. Range features have tolerance 0."""
    own = {a: m.target(meta) for a, m in mouths.items()}
    out = {}
    for feature, kind, _ in spec:
        if kind == 'range':
            out[feature] = 0.0
            continue
        values = [own[a][feature] for a in mouths]
        middle = statistics.median(values)
        spread = max(max(abs(v - middle) for v in values), FLOOR[UNITS[feature]])
        out[feature] = math.ceil(round(spread * 1000, 9)) / 1000
    return out


def residuals(mouth: Mouth, meta: str, spec: list, tol: dict, weights: list[float]) -> list[float]:
    """The feature residuals of one rig that the fit squares: (value - own) / tolerance, or for a range feature
    (value - middle) / half its width."""
    value, own = mouth.features(mouth.pose(weights)), mouth.target(meta)
    out = []
    for feature, kind, span in spec:
        if kind == 'range':
            out.append((value[feature] - (span[0] + span[1]) / 2) / ((span[1] - span[0]) / 2))
        else:
            out.append((value[feature] - own[feature]) / tol[feature])
    return out


def feature_objective(systems: list, mouths: list, meta: str, spec: list, tol: dict, mu: float,
                      weights: list[float]) -> float:
    return math.fsum(mu * error(weights, *system) ** 2
                     + math.fsum(x * x for x in residuals(m, meta, spec, tol, weights))
                     for system, m in zip(systems, mouths))


def feature_fit(systems: list, mouths: list, meta: str, spec: list, tol: dict, mu: float,
                start: list[float]) -> list[float]:
    """Gauss-Newton steps from `start` on the sum over rigs of mu e_r^2 plus the squared feature residuals, with
    forward-difference Jacobians (step STEP, backwards at the upper bound) and Levenberg damping; each step is a
    bounded least-squares problem, and a step is kept only if it lowers the objective."""
    k, u, damping = len(start), list(start), 1.0
    best = feature_objective(systems, mouths, meta, spec, tol, mu, u)
    for _ in range(GAUSS_NEWTON):
        g, b = [[0.0] * k for _ in range(k)], [0.0] * k
        for (gr, br, tt), m in zip(systems, mouths):
            if tt > 0.0:
                for i in range(k):
                    b[i] += mu * br[i] / tt
                    for j in range(k):
                        g[i][j] += mu * gr[i][j] / tt
            base = residuals(m, meta, spec, tol, u)
            jacobian = []
            for i in range(k):
                step = STEP if u[i] + STEP <= 1.0 else -STEP
                moved = list(u)
                moved[i] += step
                jacobian.append([(a - c) / step for a, c in zip(residuals(m, meta, spec, tol, moved), base)])
            linear = [math.fsum(jacobian[j][n] * u[j] for j in range(k)) - base[n] for n in range(len(base))]
            for i in range(k):
                b[i] += math.fsum(jacobian[i][n] * linear[n] for n in range(len(base)))
                for j in range(k):
                    g[i][j] += math.fsum(jacobian[i][n] * jacobian[j][n] for n in range(len(base)))
        while True:
            damped = [[g[i][j] + (damping if i == j else 0.0) for j in range(k)] for i in range(k)]
            candidate = bounded_least_squares(damped, [b[i] + damping * u[i] for i in range(k)], 1e-12, start=u)
            value = feature_objective(systems, mouths, meta, spec, tol, mu, candidate)
            if value < best:
                u, best, damping = candidate, value, damping / 3
                break
            damping *= 4
            if damping > 1e6:
                return u
    return u


def gate_passes(mouth: Mouth, system: tuple, meta: str, spec: list, tol: dict, weights: list[float]) -> bool:
    """cv: every feature and the whole-face guard within tolerance at class weights 1, 0.6 and 0.2."""
    for scale in (1.0, 0.6, 0.2):
        scaled = [w * scale for w in weights]
        value, own = mouth.features(mouth.pose(scaled)), mouth.features(mouth.own({meta: scale}))
        if any(feature_error(kind, span, value[f], own[f]) > tol[f] for f, kind, span in spec):
            return False
    # The whole-mesh error does not change with the class weight (linear shapes, no clamp for one class).
    return feature_error(*GUARD[1:], error(weights, *system), 0.0) == 0.0


# ---------------------------------------------------------------------------------------------- steps

def git(*args) -> str:
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def require_committed(*paths: Path) -> None:
    status = git('status', '--porcelain', '--', *[str(p.relative_to(ROOT)) for p in paths])
    if status:
        raise SystemExit(f'commit these first:\n{status}')


def pair(name: str) -> str:
    """The weight a shape shares in the mirror-symmetric fit: mouthSmileLeft and mouthSmileRight share mouthSmile."""
    return name.removesuffix('Left').removesuffix('Right')


def tied(geometry: Geometry, basis: list[str]) -> tuple[list[str], list[list[float]]]:
    """The mirror-symmetric basis: each Left and Right pair summed into one column, in the order of first use."""
    keys = list(dict.fromkeys(pair(a) for a in basis))
    columns = {k: None for k in keys}
    for name, shape in zip(basis, geometry.basis):
        key = pair(name)
        columns[key] = shape if columns[key] is None else [a + b for a, b in zip(columns[key], shape)]
    return keys, list(columns.values())


def avatars(names: list[str]) -> str:
    """'Female_Adult_01, _08, Male_Adult_01 and _03' style list of Rocketbox avatars."""
    parts, last = [], None
    for name in sorted(names):
        head, number = name.rsplit('_', 1)
        parts.append(name if head != last else f'_{number}')
        last = head
    return ', '.join(parts[:-1]) + f' and {parts[-1]}' if len(parts) > 1 else parts[0]


def load_rigs(cache: Path, names: list[str], basis: list[str]) -> dict[str, Geometry]:
    return {avatar: Geometry(cache, avatar, basis) for avatar in names}


def training_problem(cache: Path) -> tuple:
    """Per training rig: the tied basis keys, the shape systems per META viseme, and the mouth landmarks."""
    classes, arkit, signals = correspondences(pack_document())
    basis = list(arkit)
    rigs = load_rigs(cache, TRAINING, basis)
    systems, mouths = {}, {}
    for avatar, geometry in rigs.items():
        keys, columns = tied(geometry, basis)
        systems[avatar] = geometry.systems(list(classes), columns)[1]
        mouths[avatar] = Mouth(geometry, columns)
    return classes, arkit, signals, basis, keys, systems, mouths, {a: g.tongue for a, g in rigs.items()}


def fit(cache: Path) -> tuple:
    """The pose of every canonical class in the canonical signals, the shape residual of each class on each
    training rig, the tongue vertices left out of each rig, the frozen feature tolerances, and the training feature
    errors."""
    classes, arkit, signals, basis, keys, systems, mouths, tongue = training_problem(cache)
    poses, residual, tol, train = {}, {}, {}, {}
    for meta, cid in classes.items():
        rigs = list(systems)
        u = minimax([systems[a][meta] for a in rigs])
        if cid in FEATURES:
            spec = FEATURES[cid]
            tol[cid] = tolerances(mouths, meta, spec)
            u = feature_fit([systems[a][meta] for a in rigs], [mouths[a] for a in rigs], meta, spec, tol[cid], MU, u)
        u = [round(x, DECIMALS) for x in u]
        residual[cid] = {a: error(u, *systems[a][meta]) for a in rigs}
        if cid in FEATURES:
            train[cid] = {f: max(feature_error(kind, span, mouths[a].features(mouths[a].pose(u))[f],
                                               mouths[a].target(meta)[f]) for a in rigs)
                          for f, kind, span in FEATURES[cid]}
        weights = dict(zip(keys, u))
        by_signal = {j: weights[pair(a)] for a in basis for j in arkit[a]}
        poses[cid] = {j: by_signal[j] for j in signals}
    return poses, residual, tongue, tol, train


# The feature sets that the cv step compares: the chosen ones, and for labiodental the two that were tried.
CANDIDATES = {**{c: [spec] for c, spec in FEATURES.items()},
              V + 'labiodental': [[('teeth_to_lower_lip_mm', 'difference', None)],
                                  [('teeth_to_lower_lip_mm', 'difference', None),
                                   ('lip_opening_mm', 'difference', None)]]}


def cv(args) -> int:
    """Leave-one-rig-out cross-validation of the perceptual gate, within the training rigs only."""
    classes, arkit, signals, basis, keys, systems, mouths, _ = training_problem(args.rig_cache)
    meta_of = {cid: m for m, cid in classes.items()}
    rigs = list(systems)
    print('Per class and feature set: folds (of the left-out training rigs) where a feature or the whole-face guard '
          'fails at class weight 1, 0.6 or 0.2; the largest error / tolerance over the folds (range features: mm '
          'outside the range); and on how many training rigs the neutral face would pass.')
    for cid, specs in CANDIDATES.items():
        meta = meta_of[cid]
        for spec in specs:
            names = ', '.join(f for f, _, _ in spec)
            tol_all = tolerances(mouths, meta, spec)
            neutral = sum(gate_passes(mouths[a], systems[a][meta], meta, spec, tol_all, [0.0] * len(keys))
                          for a in rigs)
            for mu in (None, 1.0, 4.0):
                failing, worst = [], {f: 0.0 for f, _, _ in spec}
                worst['whole_face_error'] = 0.0
                for out in rigs:
                    inside = [a for a in rigs if a != out]
                    tol = tolerances({a: mouths[a] for a in inside}, meta, spec)
                    u = minimax([systems[a][meta] for a in inside])
                    if mu is not None:
                        u = feature_fit([systems[a][meta] for a in inside], [mouths[a] for a in inside], meta, spec,
                                        tol, mu, u)
                    u = [round(x, DECIMALS) for x in u]
                    if not gate_passes(mouths[out], systems[out][meta], meta, spec, tol, u):
                        failing.append(out)
                    value, own = mouths[out].features(mouths[out].pose(u)), mouths[out].target(meta)
                    for f, kind, span in spec:
                        e = feature_error(kind, span, value[f], own[f])
                        worst[f] = max(worst[f], e if kind == 'range' else e / tol[f])
                    worst['whole_face_error'] = max(worst['whole_face_error'], error(u, *systems[out][meta]))
                label = 'shape only' if mu is None else f'MU {mu:g}'
                print(f'{cid.rsplit(".", 1)[1]:20} [{names}] {label:10}: {len(failing):2d} of {len(rigs)} folds fail; '
                      + ', '.join(f'{f} {v:.3f}' for f, v in worst.items())
                      + f'; neutral passes on {neutral} of {len(rigs)}', flush=True)
    return 0


def limitations() -> list[str]:
    return [
        'Software-only geometry of example rigs: the poses are the sculpted viseme shapes of 18 Rocketbox rigs '
        'measured in their own ARKit shapes. They say nothing about any tracker, any real face or how people '
        'articulate.',
        'All training and held-out rigs come from one library, and their viseme and ARKit shapes were authored by the '
        'same team, so agreement on the held-out rigs may partly reflect shared authoring rather than transfer to '
        'independent rigs.',
        'The perceptual gate checks a few landmark features of the mouth (lip opening and protrusion, corner width, '
        'jaw drop) and a loose whole-face guard; a class that passes by it may still differ from its viseme '
        'elsewhere on the face by up to the whole motion of the viseme.',
        'The landmarks are single vertices or small vertex sets of low-polygon meshes, picked out by the rigs\' own '
        'ARKit shapes; features are as coarse as the meshes, and their tolerances come from 18 rigs of one library.',
        'The perceptual tolerances are the spread of the training rigs\' own visemes, not measured perceptual '
        'thresholds; no viewer judged them.',
        'Teeth and tongue are not represented beyond the teeth landmarks: the tongue is left out of the fit and of the '
        'error, and tongueOut is not in the basis.',
        'The poses write no blink, gaze, jaw_sideways, mouth_shift or tongue_out values. Each Left and Right pair '
        'shares one weight, so every pose gives the Left and Right canonical signals equal values; the rigs\' Left '
        'and Right shapes are not exact mirror images, so the two sides of a rig can still move slightly differently.',
        'Coarticulation is not modelled: each class is one static pose, and a blend of classes is the clamped sum '
        'of their poses; the gate tests each class alone.',
        'The weights are bounded to [0, 1] by design; whatever viseme motion the 37 ARKit shapes cannot reach that '
        'way is lost. On these rigs the ARKit shapes press the lips together only by moving their inner edges past '
        'each other, so the bilabial gate asks for closed lips and drawn-back lips, not for the lip compression of '
        'the rigs\' own bilabial shapes.',
        'The error is a ratio of Euclidean norms over all vertices except the tongue, so it weighs every vertex '
        'equally: large-area motion of the jaw and chin counts more than small lip details.',
        'Rigs from other libraries render the same ARKit weight differently (record rig-gains.ict-rocketbox-female), '
        'so on such a rig the poses give other geometry.',
        'Every rig held out by an earlier viseme pose record is a training rig here; no earlier record or tool loaded '
        'the four held-out rigs of this record.',
    ]


def freeze(args) -> int:
    require_committed(ROOT / 'tools/calibration', ROOT / 'examples', ROOT / 'check.py', PACK)
    if chosen(SETS) != [(r['training'], r['held_out']) for r in SETS['rounds']]:
        raise SystemExit(f'{RIG_SETS.name}: the rig sets are not the ones its rules give')
    entries, problems = check.read_ledger(LEDGER)
    if problems:
        raise SystemExit('\n'.join(problems))
    version = 1 + max((v for (i, v) in entries if i == RECORD_ID), default=0)
    reason = ' '.join((args.reason or '').split())
    if version > 1 and len(reason.split()) < 3:
        raise SystemExit(f'{RECORD_ID} is in the ledger already; give --reason (at least three words) for v{version}')
    if version == 1 and RECORD.exists():
        raise SystemExit(f'{RECORD} exists but the ledger has no line for it')
    poses, residuals, tongue, tol, train = fit(args.rig_cache)
    import rigs
    inputs = [(name, rigs.FILES[file][1]) for name, file in INPUT_FILES.items()]
    inputs.append((PACK_INPUT, hashlib.sha256(PACK.read_bytes()).hexdigest()))
    channels = list(poses)
    gated = ', '.join(c.rsplit('.', 1)[1] for c in FEATURES)
    method = ('minimax_bounded_least_squares_pose_fit with a perceptual gate: for each canonical viseme class, one '
              'set of ARKit weights in [0, 1] for all 18 training rigs, from the 37 ARKit shapes of the groups face, '
              'cheek_puff, jaw_thrust and chin_raise_upper_lip, each Left and Right pair sharing one weight. On each '
              "training rig the shape error is |fit - viseme| / |viseme| over every vertex except the tongue (the "
              "vertices that the rig's tongueOut moves by more than 1% of its largest move). Every class starts from "
              f'the weights with the smallest largest shape error (Lawson reweighting: {ITERATIONS} rounds of bounded '
              'least squares, each by cyclic coordinate descent to a change below 1e-13). For the gated classes '
              f'({gated}), {GAUSS_NEWTON} Gauss-Newton steps with Levenberg damping then lower the sum over the '
              f'training rigs of {MU:g} times the squared shape error plus each squared feature error divided by its '
              'tolerance (a range feature: its distance from the middle of the range, divided by half the width). '
              'The weights are rounded to 3 decimals and carried to canonical signals by the ARKit in-maps. Each '
              'curve gives the canonical value at class weight 1. Features are measured on landmark vertices that '
              "each rig's own ARKit shapes pick out (tools/calibration/viseme_poses.py, Mouth). The tolerance of a "
              "difference feature is the largest distance of a training rig's own viseme feature from the median over "
              'the training rigs, at least 0.5 mm or 0.02, rounded up to 3 decimals. The features and the fit weight '
              f'{MU:g} were chosen by leave-one-rig-out cross-validation within the training rigs; labiodental and '
              'coronal_nasal_lateral have no gate. Shape cell error, one cell per class and held-out rig: '
              "|reconstruction - target| / |target - neutral| over the rig's vertices except the tongue, where the "
              "target is the rig's own viseme shapes and the reconstruction is the rig's ARKit shapes at the weights "
              'that the ARKit out-maps give for clamp(sum of pose times class weight, 0, 1); neutral is that error at '
              'weight 0. A condition is a failure if the rig has no shape for the class, or if the target does not '
              'move the face but the reconstruction does; its error counts as 1. Feature cell error, one cell per '
              'gated class, feature and held-out rig, on the same 24 conditions: the absolute difference between the '
              'feature of the reconstruction and of the target, or how far the feature of the reconstruction lies '
              'outside its range; whole_face_error is the shape error of the condition. Pass rule: a class passes if '
              'its shape cells pass on every held-out rig, or if every one of its feature cells passes (largest error '
              'within the tolerance) on every held-out rig. Use: the viseme pose bridge is written from this record '
              'alone and reads exactly the classes that pass; it replaces viseme-poses.rocketbox-multi and '
              'viseme-poses.rocketbox-female for every class, whether more or fewer classes pass.')
    worst = {c: max(residuals[c].values()) for c in channels}
    middle = {c: statistics.median(residuals[c].values()) for c in channels}
    shapes = ', '.join(f'{c.rsplit(".", 1)[1]} {middle[c]:.3f}/{worst[c]:.3f}' for c in channels)
    features = '; '.join(f'{c.rsplit(".", 1)[1]}: ' + ', '.join(f'{f} {e:.3f}' for f, e in train[c].items())
                         for c in FEATURES)
    description = (f'The 15 viseme shapes of each of the {len(TRAINING)} training rigs ({avatars(TRAINING)}) at '
                   f'weight 1, fitted once per class over all rigs, each rig without its tongue '
                   f'({min(tongue.values())} to {max(tongue.values())} vertices). Shape residual |viseme - fit| / '
                   f'|viseme| after rounding, median/largest over the training rigs: {shapes} (sil does not move the '
                   f'face). Largest feature error over the training rigs (mm or ratio; range features: outside the '
                   f'range): {features}.')
    reference = (f'Microsoft Rocketbox facial FBX files ({rigs.ROCKETBOX_COMMIT[:7]}) of the {len(TRAINING)} training '
                 f'rigs {avatars(TRAINING)}: each has 15 viseme shapes and 52 ARKit shapes on one mesh. Held out: '
                 f'{avatars(HELD_OUT_RIGS)}. Rig sets by round 3 of the rules in tools/calibration/viseme_rigs.json')
    lines = ['# SPDX-License-Identifier: CC-BY-SA-4.0',
             '# Written by tools/calibration/viseme_poses.py. Everything but cells and feature_cells was frozen, and',
             '# its hash written to calibration/FREEZES, before the held-out run.',
             'format = "rcef.calibration/1"', f'id = {q(RECORD_ID)}', f'version = {version}',
             'status = "calibrated_software"', f'scope = {q(check.SCOPE)}', f'method = {q(method)}',
             'channels = [' + ', '.join(q(c) for c in channels) + ']',
             f'reference_rig = {q(reference)}',
             f'code_commit = {q(git("rev-parse", "HEAD"))}', 'licence = "CC-BY-SA-4.0"',
             'limitations = [', *[f'  {q(x)},' for x in limitations()], ']', '']
    for name, digest in inputs:
        lines += ['[[inputs]]', f'name = {q(name)}', f'sha256 = {q(digest)}', '']
    lines += ['[training]', f'conditions = {len(channels) * len(TRAINING)}', f'description = {q(description)}',
              '', '[held_out]', 'seed_rule = "rcef.calibration.seeds/1"', f'count = {HELD_OUT}',
              'frozen_sha256 = "PENDING"', '', '[evaluation]', f'min_conditions = {HELD_OUT}', '']
    for c in channels:
        lines += [f'[evaluation.bounds.{q(c)}]', *[f'{m} = {b}' for m, b in BOUNDS.items()], '']
    for c, spec in FEATURES.items():
        for feature, kind, span in spec + [GUARD]:
            lines += ['[[features]]', f'channel = {q(c)}', f'feature = {q(feature)}', f'kind = {q(kind)}',
                      f'units = {q(UNITS[feature])}']
            if kind == 'range':
                lines += [f'low = {float(span[0])!r}', f'high = {float(span[1])!r}', 'tolerance = 0.0']
            else:
                lines += [f'tolerance = {tol[c][feature]!r}']
            lines += [f'description = {q(DESCRIPTIONS[feature])}', '']
    for c in channels:
        for j, pose in poses[c].items():
            lines += ['[[curves]]', f'input = {q(c)}', f'output = {q(j)}', f'knots = [[0.0, 0.0], [1.0, {pose!r}]]',
                      '']
    RECORD.write_text('\n'.join(lines), encoding='utf-8')
    frozen = check.frozen_sha256(check.load_record(RECORD))
    RECORD.write_text(RECORD.read_text(encoding='utf-8').replace('"PENDING"', q(frozen)), encoding='utf-8')
    with LEDGER.open('a', encoding='utf-8') as ledger:
        ledger.write(f'{RECORD_ID} v{version} {frozen} {datetime.date.today().isoformat()}' +
                     (f' {reason}' if version > 1 else '') + '\n')
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    print(f'shape residual ratios (median/largest): {shapes}')
    print(f'feature tolerances: {tol}')
    print(f'largest training feature errors: {features}')
    print(f'Commit {RECORD.name} and FREEZES now, before the held-out step.')
    return 0


def out_maps(document: dict):
    """The ARKit out-map, compiled from the pack. It also writes the shapes of other groups; they are left out."""
    import msf_character_tools as msf
    from rcef_translate import load_pack
    pack = load_pack(document)
    source = msf.profile_snapshot(pack, 'rcef.canonical_expression').value
    target = msf.profile_snapshot(pack, 'arkit.coefficient').value
    result = msf.compile_mapping(pack, source, target, OUT_MAP, True)
    if not result.ok:
        raise SystemExit(result.report.to_dict())
    return msf, [result.value]


def arkit_weights(msf, compiled, values: dict[str, float]) -> dict[str, float]:
    """The ARKit weights that the given canonical values write; partial evaluation leaves out the outputs that read
    a canonical value not given."""
    out = {}
    for mapping in compiled:
        inputs = sorted(s for s in mapping.required_inputs if s in values)
        sample = {'timestamp': 0.0, 'values': {s: values[s] for s in inputs}, 'validity': dict.fromkeys(inputs, True)}
        result = msf.evaluate_mapping(mapping, [sample], partial=True)
        if not result.ok or result.value.refusals:
            raise SystemExit(result.report.to_dict() if not result.ok else result.value.to_dict())
        out.update({s.split('.', 2)[2]: v for s, v in result.value.samples[0]['values'].items()})
    return out


def identity(avatar: str) -> str:
    return f'Rocketbox {avatar} (held-out rig, not loaded by any fit or earlier evaluation)'


def summary(errors: list[float], failures: int) -> dict:
    return {'failures': failures, 'median': round(statistics.median(errors), 6), 'p95': round(p95(errors), 6),
            'max': round(max(errors), 6)}


def evaluate(record: dict, cache: Path) -> tuple[dict, dict]:
    """The shape cells keyed by (avatar, channel), with the error at full weight, and the feature cells keyed by
    (avatar, channel, feature)."""
    document = pack_document()
    classes, arkit, _ = correspondences(document)
    basis = list(arkit)
    poses = {}
    for curve in record['curves']:
        poses.setdefault(curve['input'], {})[curve['output']] = curve['knots'][1][1]
    features = {}
    for f in record.get('features', []):
        features.setdefault(f['channel'], []).append(f)
    msf, compiled = out_maps(document)
    meta = {cid: m for m, cid in classes.items()}
    seeds = check.held_out_seeds(record)
    cells, feature_cells = {}, {}
    for avatar in HELD_OUT_RIGS:
        geometry = Geometry(cache, avatar, basis)
        mouth = Mouth(geometry, geometry.basis)
        shapes = [c for c in record['channels'] if meta[c] in geometry.visemes]
        if REST not in shapes:
            raise SystemExit(f'{avatar} has no shape for sil, which the blend conditions use')
        vectors = {c: geometry.visemes[meta[c]] for c in shapes}
        g = gram(geometry.basis)
        cross = {c: [dot(b, vectors[c]) for b in geometry.basis] for c in shapes}
        inner = {(a, b): dot(vectors[a], vectors[b]) for a in shapes for b in shapes}

        def weights_for(frame):
            u = arkit_weights(msf, compiled, bridge(poses, frame))
            return [u[a] for a in basis]

        def frame_error(frame, w=None):
            """|R - T| / |T|: R from the rig's ARKit weights, T from its viseme shapes, both relative to neutral."""
            w = weights_for(frame) if w is None else w
            across = math.fsum(f * dot(w, cross[c]) for c, f in frame.items())
            motion = math.fsum(fa * fb * inner[(a, b)] for a, fa in frame.items() for b, fb in frame.items())
            return ratio(quadratic(w, g) - 2 * across + motion, motion)

        for channel in record['channels']:
            if channel not in shapes:
                cells[(avatar, channel)] = {**cell([1.0] * HELD_OUT, HELD_OUT, 1.0), 'full_weight': 1.0}
                for f in features.get(channel, []):
                    feature_cells[(avatar, channel, f['feature'])] = summary([0.0], HELD_OUT)
                continue
            frames = conditions(seeds, channel)
            weights = [weights_for(frame) for frame in frames]
            results = [frame_error(frame, w) for frame, w in zip(frames, weights)]
            zero = arkit_weights(msf, compiled, bridge(poses, {channel: 0.0}))
            neutral = ratio(quadratic([zero[a] for a in basis], g), inner[(channel, channel)])[0]
            failures = sum(f for _, f in results)
            cells[(avatar, channel)] = {**cell([e for e, _ in results], failures, neutral),
                                        'full_weight': round(frame_error({channel: 1.0})[0], 6)}
            if channel not in features:
                continue
            values = [mouth.features(mouth.pose(w)) for w in weights]
            targets = [mouth.features(mouth.own({meta[c]: x for c, x in frame.items()})) for frame in frames]
            for f in features[channel]:
                span = (f.get('low'), f.get('high'))
                if f['feature'] == GUARD[0]:
                    errors = [feature_error('range', span, e, 0.0) for e, _ in results]
                else:
                    errors = [feature_error(f['kind'], span, v[f['feature']], t[f['feature']])
                              for v, t in zip(values, targets)]
                feature_cells[(avatar, channel, f['feature'])] = summary(errors, failures)
    return cells, feature_cells


def heldout(args) -> int:
    require_committed(RECORD, LEDGER)
    problems = check.verify_environment()
    if problems:
        raise SystemExit('the installed msf-character-tools is not the locked build:\n' + '\n'.join(problems))
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    record = check.load_record(RECORD)
    if 'cells' in record:
        raise SystemExit(f'{RECORD.name} already has its cells')
    paths = {(args.rig_cache / INPUT_FILES[i['name']] if i['name'] in INPUT_FILES else PACK): i['sha256']
             for i in record['inputs']}
    problems = provenance.input_problems(paths)
    if problems:
        raise SystemExit('inputs differ from the record:\n' + '\n'.join(problems))
    import msf_character_tools  # noqa: F401  (imported now so that the code check covers what follows)
    import rcef_translate  # noqa: F401
    import rigs  # noqa: F401
    code = provenance.loaded_files(ROOT) + DATA_FILES
    if problem := provenance.code_problem(ROOT, record['code_commit'], code):
        raise SystemExit(problem)
    print(f'code as at {record["code_commit"][:12]}: {", ".join(code)}')
    cells, feature_cells = evaluate(record, args.rig_cache)
    unchecked = sorted(set(provenance.loaded_files(ROOT)) - set(code))
    if unchecked:
        raise SystemExit(f'the run imported repository code that was not checked first: {", ".join(unchecked)}')
    blocks = []
    for (avatar, channel), result in cells.items():
        blocks += ['[[cells]]', f'channel = {q(channel)}', 'side = "both"', f'stimulus = {q(STIMULUS)}',
                   f'identity = {q(identity(avatar))}', f'conditions = {HELD_OUT}',
                   *[f'{key} = {result[key]!r}' for key in ('failures', 'median', 'p95', 'neutral')], '']
    for (avatar, channel, feature), result in feature_cells.items():
        blocks += ['[[feature_cells]]', f'channel = {q(channel)}', f'feature = {q(feature)}',
                   f'identity = {q(identity(avatar))}', f'conditions = {HELD_OUT}',
                   *[f'{key} = {result[key]!r}' for key in ('failures', 'median', 'p95', 'max')], '']
    RECORD.write_text(RECORD.read_text(encoding='utf-8').rstrip('\n') + '\n\n' + '\n'.join(blocks), encoding='utf-8')
    record = check.load_record(RECORD)
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    for (avatar, channel), result in cells.items():
        verdict = 'pass' if check.cell_passes(record, {'channel': channel, **result}) else 'FAIL'
        print(f'{avatar:16} {channel.rsplit(".", 1)[1]:24} shape {verdict}  median {result["median"]:.3f}  '
              f'p95 {result["p95"]:.3f}')
        for (a, c, feature), r in feature_cells.items():
            if (a, c) == (avatar, channel):
                ok = check.feature_cell_passes(record, {'channel': c, 'feature': feature, **r})
                print(f'{"":42} {feature:22} {"pass" if ok else "FAIL"}  median {r["median"]:.3f}  max {r["max"]:.3f}')
    passing = [c for c in record['channels'] if check.channel_passes(record, c)]
    if args.out:
        args.out.write_text(json.dumps({
            'passing': passing, 'code_files': code,
            'cells': [{'rig': a, 'channel': c, **r} for (a, c), r in cells.items()],
            'feature_cells': [{'rig': a, 'channel': c, 'feature': f, **r} for (a, c, f), r in feature_cells.items()]},
            indent=1), encoding='utf-8')
    names = ', '.join(c.rsplit('.', 1)[1] for c in passing)
    print(f'{len(passing)} of {len(record["channels"])} classes pass: {names}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=['cv', 'freeze', 'heldout'])
    parser.add_argument('--rig-cache', type=Path, required=True, help='directory for the Rocketbox files')
    parser.add_argument('--reason', help='freeze: why a new version is frozen')
    parser.add_argument('--out', type=Path, help='heldout: also write the cells and the code files as JSON')
    args = parser.parse_args(argv)
    return {'cv': cv, 'freeze': freeze, 'heldout': heldout}[args.step](args)


if __name__ == '__main__':
    raise SystemExit(main())
