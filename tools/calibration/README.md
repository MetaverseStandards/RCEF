# Calibration tools

These optional tools make calibration records (see [calibration/README.md](../../calibration/README.md)). They need packages that RCEF itself does not use, so `check.py` and the tests never run them. The tests check only the parts that fit curves and score cells, without rendering.

## MediaPipe's response to untextured ICT renders (`k4_mediapipe.py`)

This tool renders ICT-FaceKit with one ARKit coefficient moving at a time and scores each render with MediaPipe's Face Landmarker. It then fits a curve from each MediaPipe score back to the ICT weight. The licence check for the model is in [docs/calibration/mediapipe-licence.md](../../docs/calibration/mediapipe-licence.md).

The tool needs Python 3.11+, numpy, mediapipe, the locked msf-character-tools release wheel (it reads the Rocketbox FBX rigs itself), and a renderer built from [tools/render](../render/README.md). `msf-character-tools.txt` is the hashed requirement from [Getting started](../../README.md#getting-started). It is a separate install because `--require-hashes` needs a hash for every package it installs. With uv:

```sh
uv venv k4-venv && uv pip install --python k4-venv/bin/python mediapipe numpy
uv pip install --python k4-venv/bin/python --require-hashes -r "$DIR/msf-character-tools.txt"
swiftc -O -o meshrender tools/render/meshrender.swift
```

Do these steps in this order:

1. `k4-venv/bin/python tools/calibration/k4_mediapipe.py fetch` downloads ICT-FaceKit's neutral head, its 53 expression shapes and its first 10 identity modes (commit `da5f95a`), and MediaPipe's model. It saves them in `~/.cache/rcef-ict-full` and checks each file against the SHA-256 in [ict_files.json](ict_files.json) or in the script. Nothing is committed.
2. `train --renderer meshrender` renders 24 training conditions, each on a different ICT identity. In each condition, every channel moves alone through 0, 0.2, …, 1. MediaPipe scores every render.
3. `freeze --renderer meshrender` fits each channel. It writes `calibration/mediapipe.ict-response.cal` without cells and adds its line to `calibration/FREEZES`. Commit the harness first, because the record names the commit. **Commit the record and the ledger line before step 4.** To freeze a record again as a new version, add `--reason TEXT`. The step then writes the next version and puts the reason on its ledger line.
4. `heldout --renderer meshrender` first checks the setup and refuses to run unless all of these are true:
   - the freeze commit exists;
   - the installed msf-character-tools passes `check.py`'s lock check;
   - every cached input has the SHA-256 that the record's `inputs` pin;
   - every repository file that the run imports, `ict_files.json` and the renderer source are exactly as at the record's `code_commit`. The file list comes from the loaded modules, so `check.py` and `examples/` count too.

   The step prints that file list and saves it with the scores. To reproduce a published record, check out its freeze commit (for `mediapipe.ict-response` v2, `dd9ecd2`, with `code_commit` `7cd8ff9`), and use the renderer binary that the record names. The step then renders 20 held-out conditions from the seeds that the record's frozen hash sets. They use new ICT identities, and Rocketbox Male, which training never used. The v2 record used msf-character-tools 0.5.0 (the locked release wheel) and the renderer it pins (source `913c1641…`, binary `60e618ff…`) on macOS 27.0.1 arm64 with an Apple M4 Max. Images, and so scores, may differ slightly on another OS or GPU.
5. `evaluate` adds the cells to the record. It writes a mapping for each channel whose cells all pass to [results/mediapipe_arkit.rules](results/). For the published record no channel passed, so that file has no mappings and no mapping cites the record.

Renders and scores go to `~/.cache/rcef-k4`. A run takes a few minutes on an Apple M-series Mac.

## Rig gains: running the held-out evaluation again (`k3_heldout.py`)

`examples/rig_gains.py` made the record `rig-gains.ict-rocketbox-female` (see [examples/README.md](../../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name)). Version 2 of the record was frozen at commit `dd9ecd2`, with `code_commit` `7cd8ff9`. Version 1 was made before the Git history was rewritten for publication, and its commits are not in this repository. The v2 frozen part is v1's with only `version`, `code_commit` and the renderer hashes replaced (and so `frozen_sha256`). Its knots come from `python examples/rig_gains.py fit` at `code_commit`, and they are equal to v1's. Give `k3_heldout.py` a checkout of the freeze commit with `--checkout`. A later commit is also accepted if the code that the record names has not changed since `code_commit`. That holds only for commits before `f32c1b2`, which changed `check.py`; from then on, use the freeze commit. Like the `heldout` step of `k4_mediapipe.py`, it first checks that the checkout meets these conditions:

- the record and its ledger line are committed there;
- the installed msf-character-tools passes that checkout's lock check;
- every cached input has the SHA-256 that the record pins;
- every repository file that the run imports, the landmarks and the renderer source are as at `code_commit`;
- the renderer binary is the one that the record names.

It then runs the evaluation. If the record in the checkout that holds `k3_heldout.py` has cells with the same frozen hash, the tool reports whether the new cells are equal to them.

```sh
git worktree add /tmp/k3-freeze dd9ecd2
python tools/calibration/k3_heldout.py --checkout /tmp/k3-freeze --ict-cache DIR --rig-cache DIR \
  --renderer BIN --work /tmp/k3-work --out heldout.json
```

To reproduce the published cells, three things must match the record:

- **Code:** the freeze commit `dd9ecd2`. Its `examples/`, `check.py`, `tools/calibration/k3_heldout.py`, `tools/calibration/provenance.py` and `tools/render` are as at `code_commit` `7cd8ff9`.
- **msf-character-tools:** 0.5.0, the release wheel that the lock at the freeze commit names, installed by hash (see [Getting started](../../README.md#getting-started)). The `check.py` in the checkout refuses any other build.
- **Renderer:** the pinned binary (`binary_sha256` `60e618ff…` in the record), or a build of source `913c1641…` (`tools/render/meshrender.swift` at the freeze commit) with `swiftc -O`. A rebuild may have a different binary hash, and `k3_heldout.py` refuses a binary whose hash differs. Images also depend on the OS and GPU (record: macOS 27.0.1 arm64, Apple M4 Max).

A second held-out run, with the same code, msf-character-tools build and renderer binary, gave cells equal to the published ones.

## Viseme poses: META viseme shapes in ARKit shapes (`viseme_poses.py`)

This tool makes the record `viseme-poses.rocketbox-multi`. For each canonical viseme class, it fits one combination of ARKit shapes, with weights from 0 to 1, to the META viseme shapes of the 10 training rigs at once. It carries the weights to canonical expression signals through the ARKit in-maps. The result is one pose per canonical viseme class. The pose bridge in the [canonical set](../../docs/canonical-set.md#viseme-pose-bridge) uses the poses of the classes that pass. The earlier record `viseme-poses.rocketbox-female` was made by this tool at its freeze commit `a0381b2` (see [calibration/README.md](../../calibration/README.md#frozen-part-ledger-and-held-out-seeds)); the tool no longer makes it.

The tool uses only mesh geometry, so it needs no renderer and no extra packages: Python 3.11+ and the locked msf-character-tools release wheel, which reads the Rocketbox FBX files. The rig sets are in [viseme_rigs.json](viseme_rigs.json) (see [below](#rig-sets-for-the-multi-rig-viseme-poses-viseme_rigsjson)). Do these steps in this order:

1. Commit the code. `python tools/calibration/viseme_poses.py cv --rig-cache DIR` prints the leave-one-rig-out comparison of the candidate methods. It loads only the training rigs. It takes about 6 minutes.
2. `freeze --rig-cache DIR` checks that the rig sets follow their rule, fits the training rigs, writes `calibration/viseme-poses.rocketbox-multi.cal` without cells and adds its line to `calibration/FREEZES`. It never loads a held-out rig. **Commit the record and the ledger line before step 3.**
3. `heldout --rig-cache DIR` refuses to run unless the record and its ledger line are committed, the installed msf-character-tools passes `check.py`'s lock check, the rig files and the pack have the SHA-256 that the record pins, and every repository file that the run imports, and `viseme_rigs.json`, is as at the record's `code_commit`. It then loads the held-out rigs, scores one cell per class and rig on the held-out seeds and adds the cells to the record. `--out FILE` also writes the cells, each cell's error at full weight and the list of code files as JSON. It takes under a minute.

The fit:

- **Basis:** the 37 ARKit shapes that the in-maps of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip` read. Left and Right shapes have their own weights. The blink and gaze shapes (`eyeBlink*`, `eyeLook*`), `jawLeft`, `jawRight`, `mouthLeft`, `mouthRight` and `tongueOut` are left out; the lid and cheek shapes (`eyeSquint`, `eyeWide`, `cheekSquint`) are in.
- **Region:** on each rig, every vertex except the tongue, which is every vertex that the rig's `tongueOut` moves by more than 1% of its largest move.
- **Objective:** on each training rig, the error is the distance between the fit and the rig's viseme shape, divided by how far the viseme shape moves the face. The fit makes the largest error over the training rigs as small as it can.
- **Solver:** Lawson reweighting, 100 rounds. Each round fits bounded least squares (weights from 0 to 1) to the sum of each rig's weight times its squared error, by cyclic coordinate descent on the normal equations until no weight changes by more than 10⁻¹³. Each rig's weight starts at 1 and is then multiplied by its error. Weights are rounded to 3 decimals.

How the method was chosen, on the training rigs only. Each candidate was fitted to 9 training rigs and scored on the 10th, for each of the 10 rigs. The candidates were: an objective that sums the squared errors or makes the largest error small (minimax); Left and Right with their own weights or one shared weight (mirror-symmetric, as in the earlier record); and the lip region (the vertices that `mouthFunnel` moves by more than 20% of its largest move) weighted 5 times or not. The rule was to take the candidate with the most classes at or below 0.5 on every left-out rig, then the lowest mean of the largest error per class. Results (`cv` at `c0b8b8b`):

| Candidate | Classes at or below 0.5 on every left-out rig | Mean of the largest error per class |
|---|---|---|
| Female_Adult_01 alone, mirror-symmetric, least squares (the earlier method) | 7 | 0.514 |
| minimax, Left and Right apart (chosen) | 8 | 0.479 |
| least squares, Left and Right apart | 7 | 0.484 |
| minimax, mirror-symmetric | 8 | 0.506 |
| least squares, mirror-symmetric | 7 | 0.513 |
| minimax, Left and Right apart, lip region ×5 | 6 | 0.499 |
| least squares, Left and Right apart, lip region ×5 | 7 | 0.495 |
| minimax, mirror-symmetric, lip region ×5 | 6 | 0.526 |
| least squares, mirror-symmetric, lip region ×5 | 7 | 0.522 |
| each rig fitted to itself (a floor, not a candidate) | 9 | 0.443 |

With the chosen method, the 8 classes are `vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `postalveolar` (largest 0.497), `coronal_stop`, `dorsal` and `sil`. `rhotic` reached 0.628 and `coronal_nasal_lateral` 0.590 on one left-out rig, Female_Adult_12. The lip weighting gave no lip class a pass: `bilabial` stayed at 0.71 or more and `labiodental` at 0.91 or more on its worst left-out rig. Even when each rig is fitted to itself, `vowel_mid_spread`, `vowel_close_rounded`, `bilabial`, `labiodental` and `alveolar_sibilant` stay above 0.5 on every rig, and `coronal_nasal_lateral` reaches 0.511 on one.

The held-out cell of a class on a rig has 24 conditions, one per seed: the class at a weight from 0.2 to 1, and in half the conditions `sil` at 1 minus that weight. The error is the distance between the rig's own viseme shapes at those weights and the reconstruction, divided by how far the viseme shapes move the face. The reconstruction is the rig's ARKit shapes at the weights that the pack's ARKit out-maps give for the clamped sum of the frozen poses. Distances are Euclidean norms over all vertices except the rig's tongue. A cell passes if its median and p95 errors are at most 0.5 (the error is at most half the motion) and its neutral error is at most 0.01. A class passes if its cells pass on all 4 held-out rigs. The neutral bound cannot fail: at weight 0 the bridged weights are 0, so both faces are neutral.

## Rig sets for the multi-rig viseme poses (`viseme_rigs.json`)

The viseme pose record `viseme-poses.rocketbox-multi` is fitted on several Rocketbox rigs and held out on others. [viseme_rigs.json](viseme_rigs.json) fixes the rig sets. They were chosen by a rule, before any new rig was downloaded. Only the HTTP status and size of each file at Rocketbox commit `0943055` were known then.

- **Candidates:** every `Female_Adult_NN` and `Male_Adult_NN` facial FBX at that commit, except `_01`. That is `Female_Adult_02` to `_17` and `Male_Adult_02` to `_21`.
- **Training:** `Female_Adult_01` and `Male_Adult_01`, plus 4 new rigs of each sex. Rocketbox Male_Adult_01 was the held-out rig of `viseme-poses.rocketbox-female`, so it may be used for training but never again as a held-out rig.
- **Held out:** 2 new rigs of each sex.
- **Rule:** for each sex, sort the candidates by the lowercase hex SHA-256 of their name (for example `Female_Adult_04`, UTF-8). The first 2 are held out, and the next 4 are training. If a chosen rig cannot be downloaded or loaded, or does not have the 52 ARKit shapes and the 15 viseme shapes, it goes under `replaced`, and the next unused candidate of the same sex in that order takes its place.

The result: training `Female_Adult_01`, `_08`, `_10`, `_12`, `_14`, `Male_Adult_01`, `_03`, `_10`, `_13` and `_17`; held out `Female_Adult_04`, `_13`, `Male_Adult_05` and `_11`. The fit and its method choices may use only the training rigs. No held-out geometry is read before the record's frozen part and ledger line are committed.
