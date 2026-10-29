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

This tool makes the record `viseme-poses.rocketbox-female`. It fits each of Rocketbox Female's 15 META viseme shapes as a combination of her own ARKit shapes, with weights from 0 to 1, and carries the weights to canonical expression signals through the ARKit in-maps. The result is one pose per canonical viseme class. The pose bridge in the [canonical set](../../docs/canonical-set.md#viseme-pose-bridge) uses the poses of the classes that pass.

The tool uses only mesh geometry, so it needs no renderer and no extra packages: Python 3.11+ and the locked msf-character-tools release wheel, which reads the Rocketbox FBX files. Do these steps in this order:

1. Commit the code. `python tools/calibration/viseme_poses.py freeze --rig-cache DIR` fits Rocketbox Female, writes `calibration/viseme-poses.rocketbox-female.cal` without cells and adds its line to `calibration/FREEZES`. It never loads Rocketbox Male. **Commit the record and the ledger line before step 2.**
2. `heldout --rig-cache DIR` refuses to run unless the record and its ledger line are committed, the installed msf-character-tools passes `check.py`'s lock check, the rig files and the pack have the SHA-256 that the record pins, and every repository file that the run imports is as at the record's `code_commit`. It then loads Rocketbox Male, scores one cell per class on the held-out seeds and adds the cells to the record. `--out FILE` also writes the cells, each class's error at full weight and the list of code files as JSON.

The fit:

- **Basis:** the 37 ARKit shapes that the in-maps of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip` read. Each Left and Right pair shares one weight, so a pose moves both sides equally. The blink and gaze shapes (`eyeBlink*`, `eyeLook*`), `jawLeft`, `jawRight`, `mouthLeft`, `mouthRight` and `tongueOut` are left out; the lid and cheek shapes (`eyeSquint`, `eyeWide`, `cheekSquint`) are in.
- **Region:** every vertex except the tongue, which is every vertex that the rig's `tongueOut` moves by more than 1% of its largest move.
- **Solver:** bounded least squares on the vertex displacements (weights from 0 to 1), by cyclic coordinate descent on the normal equations until no weight changes by more than 10⁻¹³. Weights are rounded to 3 decimals.

The held-out cell of a class has 24 conditions, one per seed: the class at a weight from 0.2 to 1, and in half the conditions `sil` at 1 minus that weight. The error is the distance between Rocketbox Male's own viseme shapes at those weights and the reconstruction, divided by how far the viseme shapes move the face. The reconstruction is Male's ARKit shapes at the weights that the pack's ARKit out-maps give for the clamped sum of the frozen poses. Distances are Euclidean norms over all vertices except Male's tongue. A cell passes if its median and p95 errors are at most 0.5 (the error is at most half the motion) and its neutral error is at most 0.01. The neutral bound cannot fail: at weight 0 the bridged weights are 0, so both faces are neutral. A run takes under a minute.

## Rig sets for the multi-rig viseme poses (`viseme_rigs.json`)

The next viseme pose record, `viseme-poses.rocketbox-multi`, is fitted on several Rocketbox rigs and held out on others. [viseme_rigs.json](viseme_rigs.json) fixes the rig sets. They were chosen by a rule, before any new rig was downloaded. Only the HTTP status and size of each file at Rocketbox commit `0943055` were known then.

- **Candidates:** every `Female_Adult_NN` and `Male_Adult_NN` facial FBX at that commit, except `_01`. That is `Female_Adult_02` to `_17` and `Male_Adult_02` to `_21`.
- **Training:** `Female_Adult_01` and `Male_Adult_01`, plus 4 new rigs of each sex. Rocketbox Male_Adult_01 was the held-out rig of `viseme-poses.rocketbox-female`, so it may be used for training but never again as a held-out rig.
- **Held out:** 2 new rigs of each sex.
- **Rule:** for each sex, sort the candidates by the lowercase hex SHA-256 of their name (for example `Female_Adult_04`, UTF-8). The first 2 are held out, and the next 4 are training. If a chosen rig cannot be downloaded or loaded, or does not have the 52 ARKit shapes and the 15 viseme shapes, it goes under `replaced`, and the next unused candidate of the same sex in that order takes its place.

The result: training `Female_Adult_01`, `_08`, `_10`, `_12`, `_14`, `Male_Adult_01`, `_03`, `_10`, `_13` and `_17`; held out `Female_Adult_04`, `_13`, `Male_Adult_05` and `_11`. The fit and its method choices may use only the training rigs. No held-out geometry is read before the record's frozen part and ledger line are committed.
