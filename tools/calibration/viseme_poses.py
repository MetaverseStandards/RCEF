# SPDX-License-Identifier: MIT
"""Viseme poses: each META viseme class as one combination of ARKit shapes, fitted on several Rocketbox rigs.

The fit gives, for each canonical viseme class c and each canonical expression signal j that the bridge writes,
a pose value pose[c][j] in [0, 1]. A class at weight 1 is meant to give expression j the value pose[c][j]. The
record curves are [[0, 0], [1, pose]].

Rig sets: tools/calibration/viseme_rigs.json, chosen by a rule before any new rig was downloaded. The fit loads
only the training rigs; the held-out step loads only the held-out rigs.

Fit (mesh geometry only, no renders):
- basis: the ARKit shapes that the ARKit in-maps of the groups in GROUPS read (37 shapes); blink, gaze, the
  sideways jaw and mouth shifts and tongueOut are left out. Left and Right shapes have their own weights;
- region: on each rig, every vertex except the tongue: the vertices that the rig's tongueOut shape moves by more
  than 1% of its largest move;
- for each class, one set of ARKit weights u in [0, 1] for all training rigs. On rig r the error is
  e_r(u) = |A_r u - t_r| / |t_r|, where t_r is the rig's viseme shape and A_r its ARKit shapes, as vertex
  displacements over its region. The fit approaches the u with the smallest largest e_r by Lawson's reweighting:
  ITERATIONS rounds of a bounded least-squares fit to the sum of w_r e_r(u)^2, each w_r starting at 1 and then
  multiplied by e_r and normalised. Each round is solved by cyclic coordinate descent on the normal equations
  to a change below TOLERANCE. The weights are rounded to 3 decimals;
- each ARKit weight then goes to its canonical signals through the ARKit in-maps, which are copies.

The cv step compares the candidate methods by leave-one-rig-out cross-validation within the training rigs.

Held-out evaluation (the held-out rigs, which the fit never loads): for each class and rig, one condition per
held-out seed. The class gets a weight w in [0.2, 1] from the seed; in half the conditions the rest class sil gets
1 - w. The frozen poses give canonical values clamp(sum_c pose[c][j] * weight_c, 0, 1); the ARKit out-maps of the
pack turn them into the rig's ARKit weights. The error is |reconstruction - target| / |target - neutral|,
Euclidean norms over the rig's region, where the target is the rig's own viseme shapes at the same weights. A
condition is a failure if the rig has no shape for the class, or if the target does not move the region but the
reconstruction does; its error counts as 1. Neutral is the error at weight 0. One cell per class and rig.

Usage:
  viseme_poses.py cv --rig-cache DIR                      # leave-one-rig-out table of the candidate methods
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

RECORD_ID = 'viseme-poses.rocketbox-multi'
RECORD = ROOT / 'calibration' / f'{RECORD_ID}.cal'
LEDGER = ROOT / 'calibration' / 'FREEZES'
PACK = ROOT / 'generated/rcef.pack.json'
GROUPS = ('face', 'cheek_puff', 'jaw_thrust', 'chin_raise_upper_lip')
CLASS_MAPS = ('visemes_vowel.to_rcef', 'visemes_consonant.to_rcef', 'visemes_rest.to_rcef')
META = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')
REST = 'rcef.canonical_viseme.sil'
TOLERANCE = 1e-13
ITERATIONS = 100
TONGUE = 0.01
# cv only: the lip region (vertices that mouthFunnel moves by more than 20% of its largest move) and its weight.
LIP, LIP_WEIGHT = 0.2, 5.0
DECIMALS = 3
HELD_OUT = 24
LOW_WEIGHT = 0.2
BOUNDS = {'median': 0.5, 'p95': 0.5, 'neutral': 0.01}
COPY = check.COPY
RIG_SETS = ROOT / 'tools/calibration/viseme_rigs.json'
DATA_FILES = [RIG_SETS.relative_to(ROOT).as_posix()]
SETS = json.loads(RIG_SETS.read_text(encoding='utf-8'))
TRAINING, HELD_OUT_RIGS = SETS['training'], SETS['held_out']
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


def chosen(sets: dict) -> tuple[list[str], list[str]]:
    """The training and held-out rigs that the rule in viseme_rigs.json gives for its candidates and replacements.

    For each sex, the candidates in the order of the SHA-256 of their name: the first 2 are held out, the next 4
    are training. A replaced rig's place goes to the next unused candidate of the same sex in that order.
    """
    training, held = ['Female_Adult_01', 'Male_Adult_01'], []
    replaced = {r['name'] for r in sets['replaced']}
    for sex in ('Female', 'Male'):
        order = sorted((c['name'] for c in sets['candidates'][sex]),
                       key=lambda n: hashlib.sha256(n.encode('utf-8')).hexdigest())
        picks, spare = order[:6], iter(order[6:])
        picks = [n if n not in replaced else next(x for x in spare if x not in replaced) for n in picks]
        held += picks[:2]
        training += picks[2:]
    return training, held


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
    classes, arkit, signals = {}, {}, []
    for rule in (r for m in CLASS_MAPS for r in maps[m]):
        if rule['operator'] != COPY:
            raise SystemExit(f'{rule["id"]} is not a copy')
        classes[rule['inputs'][0][len(META[0]):-len(META[1])]] = rule['outputs'][0]
    for group in GROUPS:
        for rule in maps[f'arkit_{group}.to_rcef']:
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
        self.basis = [self._region(delta(arkit[a])) for a in basis]
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

    def lip_scale(self, basis: list[str]) -> list[float]:
        """cv only: weight LIP_WEIGHT on the coordinates of the vertices that mouthFunnel moves by more than LIP of its
        largest move, 1 elsewhere."""
        funnel = self.basis[basis.index('mouthFunnel')]
        moved = [math.hypot(*funnel[3 * v:3 * v + 3]) for v in range(len(funnel) // 3)]
        return [LIP_WEIGHT if moved[i // 3] > LIP * max(moved) else 1.0 for i in range(len(funnel))]


# ---------------------------------------------------------------------------------------------- steps

def git(*args) -> str:
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def require_committed(*paths: Path) -> None:
    status = git('status', '--porcelain', '--', *[str(p.relative_to(ROOT)) for p in paths])
    if status:
        raise SystemExit(f'commit these first:\n{status}')


def pair(name: str) -> str:
    """cv only: the weight a shape shares in a mirror-symmetric fit: mouthSmileLeft and mouthSmileRight share
    mouthSmile."""
    return name.removesuffix('Left').removesuffix('Right')


def load_training(cache: Path, basis: list[str]) -> dict[str, Geometry]:
    return {avatar: Geometry(cache, avatar, basis) for avatar in TRAINING}


def fit(cache: Path) -> tuple[dict, dict, dict]:
    """The pose of every canonical class in the canonical signals, the training residual ratio of each class on
    each training rig, and the number of tongue vertices left out of each rig."""
    classes, arkit, signals = correspondences(pack_document())
    basis = list(arkit)
    rigs = load_training(cache, basis)
    systems = {avatar: geometry.systems(list(classes))[1] for avatar, geometry in rigs.items()}
    poses, residuals = {}, {}
    for meta, cid in classes.items():
        u = [round(x, DECIMALS) for x in minimax([systems[a][meta] for a in rigs])]
        residuals[cid] = {a: error(u, *systems[a][meta]) for a in rigs}
        by_signal = {j: w for a, w in zip(basis, u) for j in arkit[a]}
        poses[cid] = {j: by_signal[j] for j in signals}
    return poses, residuals, {a: g.tongue for a, g in rigs.items()}


def cv(args) -> int:
    """Leave-one-rig-out cross-validation of the candidate methods, within the training rigs only."""
    classes, arkit, _ = correspondences(pack_document())
    basis, metas = list(arkit), list(classes)
    rigs = load_training(args.rig_cache, basis)
    keys = list(dict.fromkeys(pair(a) for a in basis))
    tie = [[1.0 if pair(a) == k else 0.0 for a in basis] for k in keys]  # paired weight -> ARKit shapes

    def tied(geometry):
        return [[math.fsum(c[i] for c, t in zip(geometry.basis, row) if t) for i in range(len(geometry.basis[0]))]
                for row in tie]
    plain = {a: g.systems(metas)[1] for a, g in rigs.items()}
    variants = {}
    for symmetric in (False, True):
        for lip in (False, True):
            fitted = {a: g.systems(metas, tied(g) if symmetric else None, g.lip_scale(basis) if lip else None)[1]
                      for a, g in rigs.items()}
            for objective in ('minimax', 'sum'):
                variants[(objective, symmetric, lip)] = fitted

    def expand(u, symmetric):
        return [math.fsum(t * w for t, w in zip((row[i] for row in tie), u)) for i in range(len(basis))] \
            if symmetric else u

    def solve(objective, systems):
        if objective == 'minimax':
            return minimax(systems)
        k = len(systems[0][1])
        live = [s for s in systems if s[2] > 0.0]
        g = [[math.fsum(gr[i][j] / tt for gr, _, tt in live) for j in range(k)] for i in range(k)]
        return bounded_least_squares(g, [math.fsum(br[i] / tt for _, br, tt in live) for i in range(k)]) \
            if live else [0.0] * k
    rows = []
    # The single-rig fit of viseme-poses.rocketbox-female (Female_Adult_01, symmetric, plain least squares), scored
    # on the other training rigs.
    single = {}
    for meta in metas:
        u = expand([round(x, DECIMALS) for x in solve('sum', [variants[('sum', True, False)]['Female_Adult_01'][meta]])],
                   True)
        single[meta] = [error(u, *plain[a][meta]) for a in rigs if a != 'Female_Adult_01']
    rows.append(('Female_Adult_01 only, symmetric, least squares', single))
    # A floor, not a candidate: each rig fitted to itself (Left and Right apart, least squares).
    rows.append(('each rig fitted to itself', {m: [error([round(x, DECIMALS) for x in solve('sum', [plain[a][m]])],
                                                         *plain[a][m]) for a in rigs] for m in metas}))
    for (objective, symmetric, lip), fitted in variants.items():
        table = {}
        for meta in metas:
            table[meta] = []
            for out in rigs:
                u = solve(objective, [fitted[a][meta] for a in rigs if a != out])
                table[meta].append(error(expand([round(x, DECIMALS) for x in u], symmetric), *plain[out][meta]))
        rows.append((f'{objective}, {"symmetric" if symmetric else "Left and Right apart"}'
                     f'{", lip region x5" if lip else ""}', table))
    short = {m: classes[m].rsplit('.', 1)[1] for m in metas}
    print('error on the left-out rig at full weight, median / max over the folds; classes <= 0.5 on every fold')
    for name, table in rows:
        passing = [short[m] for m in metas if max(table[m]) <= BOUNDS['median']]
        print(f'\n{name}: {len(passing)} classes; mean of the per-class max {statistics.mean(map(max, table.values())):.3f}')
        print('  ' + ', '.join(f'{short[m]} {statistics.median(table[m]):.3f}/{max(table[m]):.3f}' for m in metas))
    return 0


def avatars(names: list[str]) -> str:
    """'Female_Adult_01, _08, Male_Adult_01 and _03' style list of Rocketbox avatars."""
    parts, last = [], None
    for name in sorted(names):
        head, number = name.rsplit('_', 1)
        parts.append(name if head != last else f'_{number}')
        last = head
    return ', '.join(parts[:-1]) + f' and {parts[-1]}' if len(parts) > 1 else parts[0]


def limitations() -> list[str]:
    return [
        'Software-only geometry of example rigs: the poses are the sculpted viseme shapes of 10 Rocketbox rigs '
        'measured in their own ARKit shapes. They say nothing about any tracker, any real face or how people '
        'articulate.',
        'All training and held-out rigs come from one library, and their viseme and ARKit shapes were authored by the '
        'same team, so agreement on the held-out rigs may partly reflect shared authoring rather than transfer to '
        'independent rigs.',
        'Teeth and tongue are not represented: the tongue is left out of the fit and of the error, tongueOut is not '
        'in the basis, and the teeth count only as part of the face mesh that moves with the jaw.',
        'The poses write no blink, gaze, jaw_sideways, mouth_shift or tongue_out values: those shapes are not in '
        'the basis. Left and Right shapes have their own weights, so a pose may move the two sides by slightly '
        'different amounts, as the training rigs do.',
        'Coarticulation is not modelled: each class is one static pose, and a blend of classes is the clamped sum '
        'of their poses.',
        'The weights are bounded to [0, 1] by design; whatever viseme motion the 37 ARKit shapes cannot reach that '
        'way is lost, and it shows as the error. For some classes this is more than half of the motion even on the '
        'training rigs (see training).',
        'Rocketbox morph targets are linear and the poses are summed linearly below the clamp, so the error of a '
        'class alone is the same at every weight; the weight and sil-blend conditions check the clamp and the rest '
        'blend, and the result at full weight decides.',
        'The error is a ratio of Euclidean norms over all vertices except the tongue, so it weighs every vertex '
        'equally: large-area motion of the jaw and chin counts more than small lip details.',
        'The fit makes the worst training rig as good as it can, so one unusual training rig can pull a pose away '
        'from what suits the others; Lawson reweighting stops after a fixed number of rounds, near the minimax fit.',
        'Rigs from other libraries render the same ARKit weight differently (record rig-gains.ict-rocketbox-female), '
        'so on such a rig the poses give other geometry.',
        'Rocketbox Male_Adult_01 was the held-out rig of viseme-poses.rocketbox-female and is a training rig here. '
        'No earlier record or tool loaded the four held-out rigs.',
    ]


def freeze(args) -> int:
    require_committed(ROOT / 'tools/calibration', ROOT / 'examples', ROOT / 'check.py', PACK)
    if chosen(SETS) != (TRAINING, HELD_OUT_RIGS):
        raise SystemExit(f'{RIG_SETS.name}: the rig sets are not the ones its rule gives')
    entries, problems = check.read_ledger(LEDGER)
    if problems:
        raise SystemExit('\n'.join(problems))
    version = 1 + max((v for (i, v) in entries if i == RECORD_ID), default=0)
    reason = ' '.join((args.reason or '').split())
    if version > 1 and len(reason.split()) < 3:
        raise SystemExit(f'{RECORD_ID} is in the ledger already; give --reason (at least three words) for v{version}')
    if version == 1 and RECORD.exists():
        raise SystemExit(f'{RECORD} exists but the ledger has no line for it')
    poses, residuals, tongue = fit(args.rig_cache)
    import rigs
    inputs = [(name, rigs.FILES[file][1]) for name, file in INPUT_FILES.items()]
    inputs.append((PACK_INPUT, hashlib.sha256(PACK.read_bytes()).hexdigest()))
    channels = list(poses)
    method = ('minimax_bounded_least_squares_pose_fit: for each canonical viseme class, one set of ARKit weights in '
              '[0, 1] for all training rigs, from the 37 ARKit shapes of the groups face, cheek_puff, jaw_thrust and '
              'chin_raise_upper_lip, Left and Right apart. On each training rig the error is |fit - viseme| / '
              "|viseme| over the vertex displacements of every vertex except the tongue (the vertices that the rig's "
              'tongueOut moves by more than 1% of its largest move). The fit approaches the weights with the '
              f'smallest largest error by Lawson reweighting: {ITERATIONS} rounds of bounded least squares on the sum '
              'of rig weight times squared error, each rig weight starting at 1 and then multiplied by its error and '
              'normalised; each round by cyclic coordinate descent on the normal equations to a change below 1e-13. '
              'The weights are rounded to 3 decimals and carried to canonical signals by the ARKit in-maps. Each '
              'curve gives the canonical value at class weight 1. This method was chosen over a single-rig fit, a '
              'sum of squared errors, a mirror-symmetric fit and a lip-region weighting by leave-one-rig-out '
              'cross-validation within the training rigs. Cell error, one cell per class and held-out rig: '
              "|reconstruction - target| / |target - neutral| over the rig's vertices except the tongue, where the "
              "target is the rig's own viseme shapes and the reconstruction is the rig's ARKit shapes at the weights "
              'that the ARKit out-maps give for clamp(sum of pose times class weight, 0, 1); neutral is that error '
              'at weight 0. A condition is a failure if the rig has no shape for the class, or if the target does not '
              'move the face but the reconstruction does; its error counts as 1. A class passes if its cells pass on '
              'every held-out rig. Use: the viseme pose bridge is written from this record alone and reads exactly '
              'the classes that pass; it replaces viseme-poses.rocketbox-female for every class, whether more or '
              'fewer classes pass.')
    worst = {c: max(residuals[c].values()) for c in channels}
    middle = {c: statistics.median(residuals[c].values()) for c in channels}
    training = ', '.join(f'{c.rsplit(".", 1)[1]} {middle[c]:.3f}/{worst[c]:.3f}' for c in channels)
    description = (f'The 15 viseme shapes of each of the {len(TRAINING)} training rigs ({avatars(TRAINING)}) at '
                   f'weight 1, fitted once per class over all rigs, each rig without its tongue '
                   f'({min(tongue.values())} to {max(tongue.values())} vertices). Residual |viseme - fit| / |viseme| '
                   f'after rounding, median/largest over the training rigs: {training} (sil does not move the face).')
    reference = (f'Microsoft Rocketbox facial FBX files ({rigs.ROCKETBOX_COMMIT[:7]}) of the {len(TRAINING)} training '
                 f'rigs {avatars(TRAINING)}: each has 15 viseme shapes and 52 ARKit shapes on one mesh. Held out: '
                 f'{avatars(HELD_OUT_RIGS)}. Rig sets by the rule in tools/calibration/viseme_rigs.json')
    lines = ['# SPDX-License-Identifier: CC-BY-SA-4.0',
             '# Written by tools/calibration/viseme_poses.py. Everything but cells was frozen, and its hash written to',
             '# calibration/FREEZES, before the held-out run.',
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
    print(f'training residual ratios (median/largest): {training}')
    print(f'Commit {RECORD.name} and FREEZES now, before the held-out step.')
    return 0


def out_maps(document: dict):
    """The ARKit out-maps of GROUPS, compiled from the pack."""
    import msf_character_tools as msf
    from rcef_translate import load_pack
    pack = load_pack(document)
    source = msf.profile_snapshot(pack, 'rcef.canonical_expression').value
    target = msf.profile_snapshot(pack, 'arkit.coefficient').value
    compiled = []
    for group in GROUPS:
        result = msf.compile_mapping(pack, source, target, f'rcef_{group}.to_arkit', True)
        if not result.ok:
            raise SystemExit(result.report.to_dict())
        compiled.append(result.value)
    return msf, compiled


def arkit_weights(msf, compiled, values: dict[str, float]) -> dict[str, float]:
    out = {}
    for mapping in compiled:
        inputs = sorted(mapping.required_inputs)
        sample = {'timestamp': 0.0, 'values': {s: values[s] for s in inputs}, 'validity': dict.fromkeys(inputs, True)}
        result = msf.evaluate_mapping(mapping, [sample])
        if not result.ok:
            raise SystemExit(result.report.to_dict())
        out.update({s.split('.', 2)[2]: v for s, v in result.value.samples[0]['values'].items()})
    return out


def identity(avatar: str) -> str:
    return f'Rocketbox {avatar} (held-out rig, not loaded by the fit)'


def evaluate(record: dict, cache: Path) -> dict[tuple[str, str], dict]:
    """Each class's cell on each held-out rig, with its error at full weight, keyed by (avatar, channel)."""
    document = pack_document()
    classes, arkit, _ = correspondences(document)
    basis = list(arkit)
    poses = {}
    for curve in record['curves']:
        poses.setdefault(curve['input'], {})[curve['output']] = curve['knots'][1][1]
    msf, compiled = out_maps(document)
    meta = {cid: m for m, cid in classes.items()}
    seeds = check.held_out_seeds(record)
    cells = {}
    for avatar in HELD_OUT_RIGS:
        geometry = Geometry(cache, avatar, basis)
        shapes = [c for c in record['channels'] if meta[c] in geometry.visemes]
        if REST not in shapes:
            raise SystemExit(f'{avatar} has no shape for sil, which the blend conditions use')
        vectors = {c: geometry.visemes[meta[c]] for c in shapes}
        g = gram(geometry.basis)
        cross = {c: [dot(b, vectors[c]) for b in geometry.basis] for c in shapes}
        inner = {(a, b): dot(vectors[a], vectors[b]) for a in shapes for b in shapes}

        def frame_error(frame):
            """|R - T| / |T|: R from the rig's ARKit weights, T from its viseme shapes, both relative to neutral."""
            u = arkit_weights(msf, compiled, bridge(poses, frame))
            w = [u[a] for a in basis]
            across = math.fsum(f * dot(w, cross[c]) for c, f in frame.items())
            motion = math.fsum(fa * fb * inner[(a, b)] for a, fa in frame.items() for b, fb in frame.items())
            return ratio(quadratic(w, g) - 2 * across + motion, motion)

        for channel in record['channels']:
            if channel not in shapes:
                cells[(avatar, channel)] = {**cell([1.0] * HELD_OUT, HELD_OUT, 1.0), 'full_weight': 1.0}
                continue
            results = [frame_error(frame) for frame in conditions(seeds, channel)]
            zero = arkit_weights(msf, compiled, bridge(poses, {channel: 0.0}))
            neutral = ratio(quadratic([zero[a] for a in basis], g), inner[(channel, channel)])[0]
            cells[(avatar, channel)] = {**cell([e for e, _ in results], sum(f for _, f in results), neutral),
                                        'full_weight': round(frame_error({channel: 1.0})[0], 6)}
    return cells


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
    cells = evaluate(record, args.rig_cache)
    unchecked = sorted(set(provenance.loaded_files(ROOT)) - set(code))
    if unchecked:
        raise SystemExit(f'the run imported repository code that was not checked first: {", ".join(unchecked)}')
    blocks = []
    for (avatar, channel), result in cells.items():
        blocks += ['[[cells]]', f'channel = {q(channel)}', 'side = "both"', f'stimulus = {q(STIMULUS)}',
                   f'identity = {q(identity(avatar))}', f'conditions = {HELD_OUT}',
                   *[f'{key} = {result[key]!r}' for key in ('failures', 'median', 'p95', 'neutral')], '']
    RECORD.write_text(RECORD.read_text(encoding='utf-8').rstrip('\n') + '\n\n' + '\n'.join(blocks), encoding='utf-8')
    record = check.load_record(RECORD)
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    failing = {c['channel'] for c in record['cells'] if not check.cell_passes(record, c)}
    passing = [c for c in record['channels'] if c not in failing]
    for (avatar, channel), result in cells.items():
        verdict = 'pass' if check.cell_passes(record, {'channel': channel, **result}) else 'FAIL'
        print(f'{avatar:16} {channel.rsplit(".", 1)[1]:24} {verdict}  failures {result["failures"]}  median '
              f'{result["median"]:.3f}  p95 {result["p95"]:.3f}  full weight {result["full_weight"]:.3f}')
    if args.out:
        args.out.write_text(json.dumps({'passing': passing, 'code_files': code,
                                        'cells': [{'rig': a, 'channel': c, **r} for (a, c), r in cells.items()]},
                                       indent=1), encoding='utf-8')
    print(f'{len(passing)} of {len(record["channels"])} classes pass every cell on every held-out rig')
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
