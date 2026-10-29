# SPDX-License-Identifier: MIT
"""Viseme poses: each META viseme shape of Rocketbox Female as a bounded combination of her own ARKit shapes.

The fit gives, for each canonical viseme class c and each canonical expression signal j that the bridge writes,
a pose value pose[c][j] in [0, 1]. A class at weight 1 is meant to give expression j the value pose[c][j]. The
record curves are [[0, 0], [1, pose]].

Fit (training rig Rocketbox Female, mesh geometry only, no renders):
- basis: the ARKit shapes that the ARKit in-maps of the groups in GROUPS read (37 shapes); blink, gaze, the
  sideways jaw and mouth shifts and tongueOut are left out. The fit is mirror-symmetric: each Left and Right pair
  shares one weight, so the basis has 24 columns (13 pairs and 11 single shapes);
- region: every vertex except the tongue: the vertices that the rig's tongueOut shape moves by more than 1% of
  its largest move;
- for each viseme shape, the weights u in [0, 1] that minimise the squared distance between the viseme's vertex
  displacements and those of sum(u_a * ARKit shape a) over the region (bounded least squares, solved by cyclic
  coordinate descent on the normal equations to a change below TOLERANCE), rounded to 3 decimals;
- each ARKit weight then goes to its canonical signals through the ARKit in-maps, which are copies.

Held-out evaluation (Rocketbox Male, which the fit never loads): for each class, one condition per held-out
seed. The class gets a weight w in [0.2, 1] from the seed; in half the conditions the rest class sil gets 1 - w.
The frozen poses give canonical values clamp(sum_c pose[c][j] * weight_c, 0, 1); the ARKit out-maps of the pack
turn them into Male ARKit weights. The error is |reconstruction - target| / |target - neutral|, Euclidean norms
over Male's region, where the target is Male's own viseme shapes at the same weights. A condition is a failure if
Male has no shape for the class, or if the target does not move the region but the reconstruction does; its error
counts as 1. Neutral is the error at weight 0.

Usage:
  viseme_poses.py freeze --rig-cache DIR [--reason TEXT]   # commit the record and FREEZES before the next step
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

RECORD_ID = 'viseme-poses.rocketbox-female'
RECORD = ROOT / 'calibration' / f'{RECORD_ID}.cal'
LEDGER = ROOT / 'calibration' / 'FREEZES'
PACK = ROOT / 'generated/rcef.pack.json'
GROUPS = ('face', 'cheek_puff', 'jaw_thrust', 'chin_raise_upper_lip')
CLASS_MAPS = ('visemes_vowel.to_rcef', 'visemes_consonant.to_rcef', 'visemes_rest.to_rcef')
META = ('openxr.visemes.XR_FACE_TRACKING_VISEME_', '_META')
REST = 'rcef.canonical_viseme.sil'
TOLERANCE = 1e-13
TONGUE = 0.01
DECIMALS = 3
HELD_OUT = 24
LOW_WEIGHT = 0.2
BOUNDS = {'median': 0.5, 'p95': 0.5, 'neutral': 0.01}
COPY = check.COPY
FIT_RIG, HELD_OUT_RIG = 'rocketbox-female', 'rocketbox-male'
INPUT_FILES = {'Microsoft Rocketbox Female_Adult_01_facial.fbx': 'Female_Adult_01_facial.fbx',
               'Microsoft Rocketbox Male_Adult_01_facial.fbx': 'Male_Adult_01_facial.fbx',
               'Microsoft Rocketbox LICENSE.md': 'ROCKETBOX_LICENSE.md'}
PACK_INPUT = 'RCEF generated/rcef.pack.json (the ARKit in-maps and out-maps)'
STIMULUS = ('class weight w in [0.2, 1] from the held-out seed; in half the conditions the rest class sil gets '
            '1 - w; Male ARKit weights from the frozen poses through the ARKit out-maps')
IDENTITY = 'Rocketbox Male_Adult_01 (held-out rig, not loaded by the fit)'
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
                          limit: int = 1_000_000) -> list[float]:
    """The u in [0, 1]^k that minimises u'Gu - 2b'u, by cyclic coordinate descent from u = 0.

    Each step sets one weight to its exact minimiser with the others fixed, clipped to [0, 1]. The objective is
    convex, so the sweeps converge; they stop when no weight changes by more than `tolerance`.
    """
    k = len(b)
    u = [0.0] * k
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

    def __init__(self, cache: Path, name: str, basis: list[str]):
        import msf_character_tools as msf
        import rigs
        self.msf, self.rigs = msf, rigs
        self.rig = rigs.load(name, cache)
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
        self.visemes = {meta: self._region(delta(i)) for meta, i in self.rig.visemes.items()}

    def _positions(self, vector):
        geometry = self.rigs.require(self.msf.evaluate_geometry(self.rig.snapshot,
                                                                morph_weights={self.rig.node: vector}))
        return [c for instance in geometry.instances for primitive in instance['primitives']
                for p in primitive['positions'] for c in p]

    def _region(self, values):
        return [values[3 * v + k] for v in self.keep for k in range(3)]


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


def fit(cache: Path) -> tuple[dict, dict, int]:
    """The pose of every canonical class in the canonical signals, the training residual ratios, and the number of
    tongue vertices left out."""
    classes, arkit, signals = correspondences(pack_document())
    basis = list(arkit)
    geometry = Geometry(cache, FIT_RIG, basis)
    columns = {}
    for name, shape in zip(basis, geometry.basis):
        key = pair(name)
        columns[key] = [a + b for a, b in zip(columns[key], shape)] if key in columns else shape
    keys = list(columns)
    g = gram(list(columns.values()))
    poses, residuals = {}, {}
    for meta, cid in classes.items():
        target = geometry.visemes[meta]
        b = [dot(c, target) for c in columns.values()]
        u = [round(x, DECIMALS) for x in bounded_least_squares(g, b)]
        residuals[cid] = ratio(quadratic(u, g) - 2 * dot(u, b) + dot(target, target), dot(target, target))[0]
        weights = dict(zip(keys, u))
        by_signal = {j: weights[pair(a)] for a in basis for j in arkit[a]}
        poses[cid] = {j: by_signal[j] for j in signals}
    return poses, residuals, geometry.tongue


def limitations() -> list[str]:
    return [
        "Software-only geometry of two example rigs: the poses are Rocketbox Female's sculpted viseme shapes "
        'measured in her own ARKit shapes. They say nothing about any tracker, any real face or how people '
        'articulate.',
        'Rocketbox Female and Male come from one library, and their ARKit shapes were authored by the same team, so '
        'agreement on Male may partly reflect shared authoring rather than transfer to independent rigs.',
        'Teeth and tongue are not represented: the tongue is left out of the fit and of the error, tongueOut is not '
        'in the basis, and the teeth count only as part of the face mesh that moves with the jaw.',
        'The poses write no blink, gaze, jaw_sideways, mouth_shift or tongue_out values: those shapes are not in '
        'the basis. The fit is mirror-symmetric, so a pose moves both sides equally, although the training visemes '
        "are not exactly symmetric and Rocketbox Female's Left and Right ARKit shapes are not mirror images.",
        'Coarticulation is not modelled: each class is one static pose, and a blend of classes is the clamped sum '
        'of their poses.',
        'The weights are bounded to [0, 1] by design; whatever viseme motion the 37 ARKit shapes cannot reach that '
        'way is lost, and it shows as the error.',
        'Rocketbox morph targets are linear and the poses are summed linearly below the clamp, so the error of a '
        'class alone is the same at every weight; the weight and sil-blend conditions check the clamp and the rest '
        'blend, and the result at full weight decides.',
        'The error is a ratio of Euclidean norms over all vertices except the tongue, so it weighs every vertex '
        'equally: large-area motion of the jaw and chin counts more than small lip details.',
        'Other rigs render the same ARKit weight differently (record rig-gains.ict-rocketbox-female), so on another '
        'rig the poses give other geometry.',
        "Earlier tools rendered Rocketbox Male's shapes (examples/viseme_pipeline.py and the MediaPipe record), but "
        'no Male geometry was used for this fit or its bounds.',
    ]


def freeze(args) -> int:
    require_committed(ROOT / 'tools/calibration', ROOT / 'examples', ROOT / 'check.py', PACK)
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
    method = ('bounded_least_squares_pose_fit: for each Rocketbox Female viseme shape, the ARKit weights in [0, 1] '
              'that minimise the squared vertex distance to it over every vertex except the tongue (the vertices '
              'that tongueOut moves by more than 1% of its largest move), with the 37 ARKit shapes of the groups '
              'face, cheek_puff, jaw_thrust and chin_raise_upper_lip, each Left and Right pair sharing one weight; '
              'cyclic coordinate descent on the normal equations to a change below 1e-13, rounded to 3 decimals, '
              'and carried to canonical signals by the ARKit in-maps. Each curve gives the canonical value at class '
              "weight 1. Cell error: |reconstruction - target| / |target - neutral| over Rocketbox Male's vertices "
              "except the tongue, where the target is Male's own viseme shapes and the reconstruction is Male's "
              'ARKit shapes at the weights that the ARKit out-maps give for clamp(sum of pose times class weight, 0, '
              '1); neutral is that error at weight 0. A condition is a failure if Male has no shape for the class, '
              'or if the target does not move the face but the reconstruction does; its error counts as 1.')
    training = ', '.join(f'{c.rsplit(".", 1)[1]} {residuals[c]:.3f}' for c in channels)
    description = (f"Each of Rocketbox Female's 15 viseme shapes at weight 1, fitted once, over {tongue} fewer "
                   f'vertices than the mesh (the tongue). Residual |viseme - fit| / |viseme| after rounding: '
                   f'{training} (sil does not move the face).')
    reference = (f'Microsoft Rocketbox Female_Adult_01 facial FBX ({rigs.ROCKETBOX_COMMIT[:7]}): its 15 viseme shapes '
                 'and 52 ARKit shapes on one mesh')
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
    lines += ['[training]', f'conditions = {len(channels)}', f'description = {q(description)}',
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
    print(f'training residual ratios: {training}')
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


def evaluate(record: dict, cache: Path) -> dict[str, dict]:
    """Each class's cell on the held-out rig, with its error at full weight."""
    document = pack_document()
    classes, arkit, _ = correspondences(document)
    basis = list(arkit)
    poses = {}
    for curve in record['curves']:
        poses.setdefault(curve['input'], {})[curve['output']] = curve['knots'][1][1]
    geometry = Geometry(cache, HELD_OUT_RIG, basis)
    msf, compiled = out_maps(document)
    meta = {cid: m for m, cid in classes.items()}
    shapes = [c for c in record['channels'] if meta[c] in geometry.visemes]
    if REST not in shapes:
        raise SystemExit(f'{HELD_OUT_RIG} has no shape for sil, which the blend conditions use')
    vectors = {c: geometry.visemes[meta[c]] for c in shapes}
    g = gram(geometry.basis)
    cross = {c: [dot(b, vectors[c]) for b in geometry.basis] for c in shapes}
    inner = {(a, b): dot(vectors[a], vectors[b]) for a in shapes for b in shapes}

    def error(frame):
        """|R - T| / |T|: R from the Male ARKit weights, T from Male's viseme shapes, both relative to neutral."""
        u = arkit_weights(msf, compiled, bridge(poses, frame))
        w = [u[a] for a in basis]
        across = math.fsum(f * dot(w, cross[c]) for c, f in frame.items())
        motion = math.fsum(fa * fb * inner[(a, b)] for a, fa in frame.items() for b, fb in frame.items())
        return ratio(quadratic(w, g) - 2 * across + motion, motion)

    seeds = check.held_out_seeds(record)
    cells = {}
    for channel in record['channels']:
        if channel not in shapes:
            cells[channel] = {**cell([1.0] * HELD_OUT, HELD_OUT, 1.0), 'full_weight': 1.0}
            continue
        results = [error(frame) for frame in conditions(seeds, channel)]
        zero = arkit_weights(msf, compiled, bridge(poses, {channel: 0.0}))
        neutral = ratio(quadratic([zero[a] for a in basis], g), inner[(channel, channel)])[0]
        cells[channel] = {**cell([e for e, _ in results], sum(f for _, f in results), neutral),
                          'full_weight': round(error({channel: 1.0})[0], 6)}
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
    code = provenance.loaded_files(ROOT)
    if problem := provenance.code_problem(ROOT, record['code_commit'], code):
        raise SystemExit(problem)
    print(f'code as at {record["code_commit"][:12]}: {", ".join(code)}')
    cells = evaluate(record, args.rig_cache)
    unchecked = sorted(set(provenance.loaded_files(ROOT)) - set(code))
    if unchecked:
        raise SystemExit(f'the run imported repository code that was not checked first: {", ".join(unchecked)}')
    blocks = []
    for channel, result in cells.items():
        blocks += ['[[cells]]', f'channel = {q(channel)}', 'side = "shared"', f'stimulus = {q(STIMULUS)}',
                   f'identity = {q(IDENTITY)}', f'conditions = {HELD_OUT}',
                   *[f'{key} = {result[key]!r}' for key in ('failures', 'median', 'p95', 'neutral')], '']
    RECORD.write_text(RECORD.read_text(encoding='utf-8').rstrip('\n') + '\n\n' + '\n'.join(blocks), encoding='utf-8')
    record = check.load_record(RECORD)
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    passing = [c['channel'] for c in record['cells'] if check.cell_passes(record, c)]
    for channel, result in cells.items():
        verdict = 'pass' if channel in passing else 'FAIL'
        print(f'{channel.rsplit(".", 1)[1]:24} {verdict}  failures {result["failures"]}  median {result["median"]:.3f}'
              f'  p95 {result["p95"]:.3f}  full weight {result["full_weight"]:.3f}')
    if args.out:
        args.out.write_text(json.dumps({'passing': passing, 'cells': cells, 'code_files': code}, indent=1),
                            encoding='utf-8')
    print(f'{len(passing)} of {len(cells)} classes pass every cell')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=['freeze', 'heldout'])
    parser.add_argument('--rig-cache', type=Path, required=True, help='directory for the Rocketbox files')
    parser.add_argument('--reason', help='freeze: why a new version is frozen')
    parser.add_argument('--out', type=Path, help='heldout: also write the cells and the code files as JSON')
    args = parser.parse_args(argv)
    return freeze(args) if args.step == 'freeze' else heldout(args)


if __name__ == '__main__':
    raise SystemExit(main())
