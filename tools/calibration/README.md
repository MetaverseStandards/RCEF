# Calibration tools

These optional tools make calibration records (see [calibration/README.md](../../calibration/README.md)). They need packages that RCEF itself does not use, so `check.py` and the tests never run them. The tests check only the parts that fit curves and score cells, without rendering.

## MediaPipe's response to untextured ICT renders (`k4_mediapipe.py`)

This tool renders ICT-FaceKit with one ARKit coefficient moving at a time and scores each render with MediaPipe's Face Landmarker. It then fits a curve from each MediaPipe score back to the ICT weight. The licence check for the model is in [docs/calibration/mediapipe-licence.md](../../docs/calibration/mediapipe-licence.md).

The tool needs Python 3.11+, numpy, mediapipe, the locked msf-character-tools release wheel (it reads the Rocketbox FBX rigs itself), and a renderer built from [tools/render](../render/README.md). `msf-character-tools.txt` is the hashed requirement from [Generate and check](../../README.md#generate-and-check). It is a separate install because `--require-hashes` needs a hash for every package it installs. With uv:

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

   The step prints that file list and saves it with the scores. To reproduce a published record, check out its freeze commit (for `mediapipe.ict-response` v2, `dd9ecd2`, with `code_commit` `7cd8ff9`), and use the renderer binary that the record names. The step then renders 20 held-out conditions from the seeds that the record's frozen hash sets. They use new ICT identities, and Rocketbox Male, which training never used.
5. `evaluate` adds the cells to the record. It writes a mapping for each channel whose cells all pass to [results/mediapipe_arkit.rules](results/). For the published record no channel passed, so that file has no mappings and no mapping cites the record.

Renders and scores go to `~/.cache/rcef-k4`. A run takes a few minutes on an Apple M-series Mac.

## Rig gains: running the held-out evaluation again (`k3_heldout.py`)

`examples/rig_gains.py` made the record `rig-gains.ict-rocketbox-female` (see [examples/README.md](../../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name)). Version 2 of the record was frozen at commit `dd9ecd2`, with `code_commit` `7cd8ff9`. Version 1 was made before the Git history was rewritten for publication, and its commits are not in this repository. Give `k3_heldout.py` a checkout of the freeze commit with `--checkout`. A later commit is also accepted if the code that the record names has not changed since `code_commit`. Like the `heldout` step of `k4_mediapipe.py`, it first checks that the checkout meets these conditions:

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
- **msf-character-tools:** 0.5.0, the release wheel that the lock at the freeze commit names, installed by hash (see [Generate and check](../../README.md#generate-and-check)). The `check.py` in the checkout refuses any other build.
- **Renderer:** the pinned binary (`binary_sha256` `60e618ff…` in the record), or a build of source `913c1641…` (`tools/render/meshrender.swift` at the freeze commit) with `swiftc -O`. A rebuild may have a different binary hash, and `k3_heldout.py` refuses a binary whose hash differs. Images also depend on the OS and GPU (record: macOS 27.0.1 arm64, Apple M4 Max).

A second held-out run, with the same code, msf-character-tools build and renderer binary, gave cells equal to the published ones.
