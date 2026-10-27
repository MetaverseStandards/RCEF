# SPDX-License-Identifier: MIT
"""The train, freeze, held-out and evaluate steps of k4_mediapipe.py, and the record and rules they write."""
from __future__ import annotations
import datetime
import json
from pathlib import Path
import platform
import subprocess
import tempfile

import k4_mediapipe as k
import check
import provenance

RECORD_ID = 'mediapipe.ict-response'
RECORD = k.ROOT / 'calibration' / f'{RECORD_ID}.cal'
LEDGER = k.ROOT / 'calibration' / 'FREEZES'
RULES = k.ROOT / 'tools/calibration/results/mediapipe_arkit.rules'
HELD_OUT_CONDITIONS = 20
BOUNDS = {'median': 0.05, 'p95': 0.15, 'neutral': 0.03}
CELLS = {'ict': 'ICT-FaceKit held-out identities (a new identity in every condition, drawn from the held-out seeds)',
         'rocketbox-male': 'Rocketbox Male_Adult_01 (a rig not used in training)'}
STIMULUS = 'the channel alone at 0, 0.2, 0.4, 0.6, 0.8 and 1, from a neutral face'
q = json.dumps


ICT_INPUT = f'ICT-FaceKit {k.ICT_COMMIT[:7]} '
TASK_INPUT = 'MediaPipe face_landmarker.task (float16, version 1)'
ROCKETBOX_INPUT = 'Microsoft Rocketbox Male_Adult_01_facial.fbx'


def input_paths(record: dict, cache: Path, rig_cache: Path) -> dict[Path, str]:
    """The cache file behind each of the record's inputs, with the SHA-256 the record pins for it."""
    paths = {}
    for item in record['inputs']:
        name = item['name']
        if name.startswith(ICT_INPUT):
            path = cache / Path(name[len(ICT_INPUT):]).name
        elif name == TASK_INPUT:
            path = cache / 'face_landmarker.task'
        elif name == ROCKETBOX_INPUT:
            path = rig_cache / 'Male_Adult_01_facial.fbx'
        else:
            raise SystemExit(f'the record names an input this tool does not know: {name}')
        paths[path] = item['sha256']
    return paths


def git(*args) -> str:
    return subprocess.run(['git', *args], cwd=k.ROOT, check=True, capture_output=True, text=True).stdout.strip()


def require_committed(*paths) -> None:
    status = git('status', '--porcelain', '--', *[str(p.relative_to(k.ROOT)) for p in paths])
    if status:
        raise SystemExit(f'commit these first:\n{status}')


def renderer(args) -> Path:
    if not args.renderer or not args.renderer.is_file():
        raise SystemExit('give --renderer, a meshrender binary built from tools/render (see tools/render/README.md)')
    return args.renderer


def save(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding='utf-8')


def train(args) -> int:
    k.fetch(args.cache)
    rig = k.load_ict(args.cache)
    conditions = k.training_conditions()
    with tempfile.TemporaryDirectory(prefix='rcef-k4-') as work:
        results = k.sweep_runs(rig, conditions, k.CHANNELS, renderer(args), k.Scorer(args.cache / 'face_landmarker.task'),
                               Path(work))
    save(args.out / 'training.json', {'conditions': conditions, 'results': results})
    return 0


def platform_text() -> dict:
    gpu = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True).stdout
    chip = next((line.split(':', 1)[1].strip() for line in gpu.splitlines() if 'Chipset Model' in line), 'unknown')
    compiler = subprocess.run(['swiftc', '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    return {'compiler': compiler, 'os': f'macOS {platform.mac_ver()[0]} ({platform.machine()})', 'gpu': chip}


def limitations(unfitted: dict) -> list[str]:
    out = [
        "Software-only: this is MediaPipe's response to untextured ICT renders. It says nothing about MediaPipe on "
        'real faces or photographs, or about any tracker.',
        "MediaPipe's blendshape model learned expressions transferred from an artist-designed base mesh (its model "
        "card), and ICT-FaceKit's shapes follow the same artist-made ARKit conventions, so agreement here may partly "
        'reflect those shared conventions rather than an independent measurement.',
        'Each channel was swept alone from a neutral face; combinations of expressions, which change MediaPipe\'s '
        'scores, were not measured.',
        'Renders are grey Lambert surfaces with no texture, eyelashes, eyebrows or skin detail.',
        "Held-out ICT identities vary only ICT's first 10 identity modes.",
        "The curves invert MediaPipe's median response on ICT; a rig with different shapes needs its own check, which "
        'is what the Rocketbox cells test.',
    ]
    if unfitted:
        out.append('No curve was fitted for ' + '; '.join(f'{c} ({why})' for c, why in sorted(unfitted.items())) + '.')
    return out


def freeze(args) -> int:
    """Fit each channel on the training scores and write the record's frozen part, with no cells, and its ledger line."""
    require_committed(k.ROOT / 'tools/calibration', k.ROOT / 'tools/render')
    if RECORD.exists():
        raise SystemExit(f'{RECORD} exists; a new fit needs a new version and a reason in the ledger')
    training = json.loads((args.out / 'training.json').read_text(encoding='utf-8'))
    sweeps = k.by_channel(training['results'], k.CHANNELS)
    fits = {c: k.fit_channel(sweeps[c]) for c in k.CHANNELS}
    fitted = [c for c in k.CHANNELS if fits[c][0]]
    unfitted = {c: why for c, (knots, why) in fits.items() if not knots}
    import rigs
    inputs = [(ICT_INPUT + name, digest) for name, digest in k.ICT_FILES.items() if name.endswith('.obj')]
    inputs += [(TASK_INPUT, k.TASK_SHA256), (ROCKETBOX_INPUT, rigs.FILES['Male_Adult_01_facial.fbx'][1])]
    lines = ['# SPDX-License-Identifier: CC-BY-SA-4.0',
             '# Written by tools/calibration/k4_mediapipe.py. Everything but cells was frozen, and its hash written to',
             '# calibration/FREEZES, before the held-out run.',
             'format = "rcef.calibration/1"', f'id = {q(RECORD_ID)}', 'version = 1', 'status = "calibrated_software"',
             f'scope = {q(check.SCOPE)}',
             'scan_origin = "ICT-FaceKit\'s identity modes are principal components of light-stage scans of real '
             'people; they are used here only as geometry, through 10 modes drawn from a standard normal."',
             f'method = {q("inverse_monotone_median_fit: for each channel, the median MediaPipe score at each swept weight over the training conditions, made nondecreasing (pool-adjacent-violators), then inverted to a score-to-weight curve by linear interpolation; a flat stretch keeps its lowest weight; scores below the first or above the last median map to 0 and 1. Cell errors are |curve(score) - weight| over every swept weight of the first conditions held-out conditions; neutral is the median error at weight 0; a condition in which MediaPipe finds no face at any weight is a failure.")}',
             'channels = [' + ', '.join(q(f'mediapipe.score.{c}') for c in fitted) + ']',
             f'reference_rig = {q(f"ICT-FaceKit Light {k.ICT_COMMIT[:7]}: generic neutral head and 53 expression shapes, with identity modes 0-9")}',
             f'code_commit = {q(git("rev-parse", "HEAD"))}',
             'licence = "CC-BY-SA-4.0"',
             'limitations = [', *[f'  {q(x)},' for x in limitations(unfitted)], ']', '']
    for name, digest in inputs:
        lines += ['[[inputs]]', f'name = {q(name)}', f'sha256 = {q(digest)}', '']
    platform_info = platform_text()
    lines += ['[renderer]', f'source_sha256 = {q(k.sha256(k.ROOT / "tools/render/meshrender.swift"))}',
              f'binary_sha256 = {q(k.sha256(renderer(args)))}', *[f'{key} = {q(v)}' for key, v in platform_info.items()],
              '', '[training]', f'conditions = {k.TRAINING_CONDITIONS}',
              f'description = {q(f"{k.TRAINING_CONDITIONS} conditions, each on its own ICT identity (10 modes from a standard normal), from seeds rcef.k4.training:0 to :{k.TRAINING_CONDITIONS - 1}; {k.CONDITION_TEXT}. Every channel is swept alone at each condition.")}',
              '', '[held_out]', 'seed_rule = "rcef.calibration.seeds/1"', f'count = {HELD_OUT_CONDITIONS}',
              'frozen_sha256 = "PENDING"', '', '[evaluation]', f'min_conditions = {HELD_OUT_CONDITIONS}', '']
    for c in fitted:
        lines += [f'[evaluation.bounds."mediapipe.score.{c}"]', *[f'{m} = {b}' for m, b in BOUNDS.items()], '']
    for c in fitted:
        lines += ['[[curves]]', f'input = "mediapipe.score.{c}"', f'output = "arkit.coefficient.{c}"',
                  'knots = [' + ', '.join(f'[{x!r}, {y!r}]' for x, y in fits[c][0]) + ']', '']
    RECORD.write_text('\n'.join(lines), encoding='utf-8')
    frozen = check.frozen_sha256(check.load_record(RECORD))
    RECORD.write_text(RECORD.read_text(encoding='utf-8').replace('"PENDING"', q(frozen)), encoding='utf-8')
    with LEDGER.open('a', encoding='utf-8') as ledger:
        ledger.write(f'{RECORD_ID} v1 {frozen} {datetime.date.today().isoformat()}\n')
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    print(f'fitted {len(fitted)} channels; no curve for {len(unfitted)}. Commit {RECORD.name} and FREEZES now.')
    return 0


def heldout(args) -> int:
    """Render and score the held-out conditions; refuses unless the frozen record and its ledger line are committed."""
    require_committed(RECORD, LEDGER)
    problems = check.verify_environment()
    if problems:
        raise SystemExit('the installed msf-tools is not the locked build:\n' + '\n'.join(problems))
    problems = check.calibration_problems(RECORD.parent, [])
    if problems:
        raise SystemExit('\n'.join(problems))
    record = check.load_record(RECORD)
    problems = provenance.input_problems(input_paths(record, args.cache, args.rig_cache))
    if problems:
        raise SystemExit('cached inputs differ from the record:\n' + '\n'.join(problems))
    import rigs  # noqa: F401  (Rocketbox and ICT geometry; imported now so the code check covers it)
    code = provenance.loaded_files(k.ROOT) + k.DATA_FILES + ['tools/render']
    if problem := provenance.code_problem(k.ROOT, record['code_commit'], code):
        raise SystemExit(problem)
    print(f'code as at {record["code_commit"][:12]}: {", ".join(code)}')
    if k.sha256(renderer(args)) != record['renderer']['binary_sha256']:
        raise SystemExit('this is not the renderer binary the record names')
    seeds = check.held_out_seeds(record)
    channels = [c['input'].split('.', 2)[2] for c in record['curves']]
    scorer = k.Scorer(args.cache / 'face_landmarker.task')
    out = {}
    for rig in (k.load_ict(args.cache), k.load_rocketbox_male(args.rig_cache)):
        conditions = k.held_out_conditions(seeds, rig.name == 'ict')
        with tempfile.TemporaryDirectory(prefix='rcef-k4-') as work:
            out[rig.name] = {'conditions': conditions,
                             'results': k.sweep_runs(rig, conditions, channels, renderer(args), scorer, Path(work))}
    unchecked = sorted(set(provenance.loaded_files(k.ROOT)) - set(code))
    if unchecked:
        raise SystemExit(f'the run imported repository code that was not checked first: {", ".join(unchecked)}')
    save(args.out / 'heldout.json', {**out, 'code_commit': record['code_commit'], 'code_files': code})
    return 0


def side(channel: str) -> str:
    return 'left' if channel.endswith('Left') else 'right' if channel.endswith('Right') else 'none'


def evaluate(args) -> int:
    """Add each channel's held-out cells to the record, and write rules for the channels whose cells all pass."""
    record = check.load_record(RECORD)
    if 'cells' in record:
        raise SystemExit(f'{RECORD.name} already has its cells')
    heldout = json.loads((args.out / 'heldout.json').read_text(encoding='utf-8'))
    curves = {c['input'].split('.', 2)[2]: c['knots'] for c in record['curves']}
    blocks, cells = [], {}
    for channel, knots in curves.items():
        for rig, label in CELLS.items():
            sweeps = k.by_channel(heldout[rig]['results'], [channel])[channel]
            result = k.cell(knots, sweeps, HELD_OUT_CONDITIONS)
            cells[(channel, rig)] = result
            blocks += ['[[cells]]', f'channel = "mediapipe.score.{channel}"', f'side = "{side(channel)}"',
                       f'stimulus = {q(STIMULUS)}', f'identity = {q(label)}', f'conditions = {HELD_OUT_CONDITIONS}',
                       *[f'{key} = {result[key]!r}' for key in ('failures', 'median', 'p95', 'neutral')], '']
    RECORD.write_text(RECORD.read_text(encoding='utf-8').rstrip('\n') + '\n\n' + '\n'.join(blocks), encoding='utf-8')
    record = check.load_record(RECORD)
    passing = [c for c in curves if all(check.cell_passes(record, x) for x in record['cells']
                                        if x['channel'] == f'mediapipe.score.{c}')]
    RULES.parent.mkdir(exist_ok=True)
    RULES.write_text(rules_text(record, passing), encoding='utf-8')
    problems = check.calibration_problems(RECORD.parent, read_rules())
    if problems:
        raise SystemExit('\n'.join(problems))
    summary = {c: {rig: cells[(c, rig)] for rig in CELLS} for c in curves}
    save(args.out / 'summary.json', {'passing': passing, 'cells': summary})
    print(f'{len(passing)} of {len(curves)} fitted channels pass every cell: {", ".join(passing) or "none"}')
    return 0


def rules_text(record: dict, passing: list[str]) -> str:
    knots = {c['input']: c['knots'] for c in record['curves']}
    if not passing:
        lines = ['# SPDX-License-Identifier: CC-BY-SA-4.0',
                 f'# Published negative result for calibration record {RECORD_ID}: 0 of',
                 f"# MediaPipe's {len(k.CHANNELS)} ARKit-named scores pass. {len(knots)} rose enough in training to fit a",
                 '# curve, and none met its bounds on held-out ICT identities or on Rocketbox Male,',
                 '# so no mapping cites the record. The file is TOML, but it is not named .toml,',
                 '# so msf-tools does not read it.',
                 '',
                 '# No channel passed every held-out cell, so there are no rules.', '']
        return '\n'.join(lines)
    # calibrated_software needs authoring schema 1.1; RCEF's pack.toml is on 1.0.
    lines = ['# SPDX-License-Identifier: CC-BY-SA-4.0',
             '# These mappings use evidence_status = "calibrated_software", which needs authoring',
             '# schema 1.1. They can move to mappings/mediapipe_arkit.toml once pack.toml uses',
             '# schema 1.1. The file is TOML, but it is not named .toml, so msf-tools does not read it.',
             '']
    lines += ['[[mappings]]', 'id = "mediapipe.to_arkit"', '']
    for channel in passing:
        source, target = f'mediapipe.score.{channel}', f'arkit.coefficient.{channel}'
        lines += ['[[mappings.rules]]', f'id = "mediapipe_arkit.{channel}"', f'inputs = [{q(source)}]',
                  f'outputs = [{q(target)}]',
                  'operator = { "id" = "piecewise_linear", "knots" = [' +
                  ', '.join(f'[{x!r}, {y!r}]' for x, y in knots[source]) + '] }',
                  'disposition = "mapped"', 'mapping_quality = "approximate"', 'evidence_status = "calibrated_software"',
                  'assumptions = [', *[f'  {q(text)},' for text in assumptions(channel)], ']', f'evidence = ["calibration.{RECORD_ID}", "mediapipe", "mediapipe_blendshape_card", "apple_blendshapes"]',
                  'loss_annotations = [',
                  f'  {{ "category" = "signal", "effect" = "approximated", "reason" = "fitted to renders of one artist-made rig; real faces and other rigs may respond differently", "refs" = [{q(source)}, {q(target)}], "units" = "1" }},',
                  ']', '']
    return '\n'.join(lines)


def assumptions(channel: str) -> list[str]:
    out = [f"The curve is MediaPipe's response to untextured ICT renders, inverted: it maps the {channel} score "
           f"MediaPipe gave renders of ICT-FaceKit back to the ICT {channel} weight that produced it.",
           'Software-only: not a calibration of MediaPipe on real faces, and not a measurement of any tracker.']
    if side(channel) != 'none':
        out.append(f"Both name sides from the subject's own face: MediaPipe's {channel} is paired with ICT's "
                   f"{k.ict_names(channel)[0]}, and the held-out cells test that pairing.")
    return out


def read_rules() -> list[dict]:
    import tomllib
    if not RULES.exists():
        return []
    return [r for m in tomllib.loads(RULES.read_text(encoding='utf-8')).get('mappings', []) for r in m.get('rules', [])]
