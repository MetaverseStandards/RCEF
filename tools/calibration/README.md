# Calibration tools

These optional tools make calibration records (see [calibration/README.md](../../calibration/README.md)). They need packages that RCEF itself does not use, so `check.py` and the tests never run them. The tests check only the parts that fit curves and score cells, without rendering.

## MediaPipe's response to untextured ICT renders (`k4_mediapipe.py`)

This tool renders ICT-FaceKit with one ARKit coefficient moving at a time and scores each render with MediaPipe's Face Landmarker. It then fits a curve from each MediaPipe score back to the ICT weight. The licence check for the model is in [docs/calibration/mediapipe-licence.md](../../docs/calibration/mediapipe-licence.md).

The tool needs Python 3.11+, numpy, mediapipe, msf-tools at the locked commit with msf-tools-ufbx (for Rocketbox), and a renderer built from [tools/render](../render/README.md). With uv:

```sh
uv venv k4-venv && uv pip install --python k4-venv/bin/python mediapipe numpy \
  "msf-tools @ git+https://github.com/Kjakubzak/msf-tools@COMMIT" \
  "msf-tools-ufbx @ git+https://github.com/Kjakubzak/msf-tools@COMMIT#subdirectory=native/ufbx"
swiftc -O -o meshrender tools/render/meshrender.swift
```

Do these steps in this order:

1. `k4-venv/bin/python tools/calibration/k4_mediapipe.py fetch` downloads ICT-FaceKit's neutral head, its 53 expression shapes and its first 10 identity modes (commit `da5f95a`), and MediaPipe's model. It saves them in `~/.cache/rcef-ict-full` and checks each file against the SHA-256 in [ict_files.json](ict_files.json) or in the script. Nothing is committed.
2. `train --renderer meshrender` renders 24 training conditions, each on a different ICT identity. In each condition, every channel moves alone through 0, 0.2, …, 1. MediaPipe scores every render.
3. `freeze --renderer meshrender` fits each channel. It writes `calibration/mediapipe.ict-response.cal` without cells and adds its line to `calibration/FREEZES`. Commit the harness first, because the record names the commit. **Commit the record and the ledger line before step 4.**
4. `heldout --renderer meshrender` first checks the setup and refuses to run unless all of these are true:
   - the freeze commit exists;
   - the installed msf-tools passes `check.py`'s lock check;
   - every cached input has the SHA-256 that the record's `inputs` pin;
   - every repository file that the run imports, `ict_files.json` and the renderer source are exactly as at the record's `code_commit`. The file list comes from the loaded modules, so `check.py` and `examples/` count too.

   The step prints that file list and saves it with the scores. To reproduce a published record, check out its freeze commit. The step then renders 20 held-out conditions from the seeds that the record's frozen hash sets. They use new ICT identities, and Rocketbox Male, which training never used.
5. `evaluate` adds the cells to the record. It writes a rule for each channel whose cells all pass to [results/mediapipe_arkit.rules](results/). For the published record no channel passed, so that file has no rules and no mapping cites the record.

Renders and scores go to `~/.cache/rcef-k4`. A run takes a few minutes on an Apple M-series Mac.

## Rig gains: running the held-out evaluation again (`k3_heldout.py`)

`examples/rig_gains.py` made the record `rig-gains.ict-rocketbox-female` (see [examples/README.md](../../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name)). The record was frozen at commit `91f57f7` with `code_commit` `ac0b953`, before `provenance.py` existed. Later commits changed `check.py` and `tools/render`, so a held-out run must use a checkout of the freeze commit. Run `k3_heldout.py` from a current checkout. Like the `heldout` step of `k4_mediapipe.py`, it first checks that the freeze checkout meets these conditions:

- the record and its ledger line are committed there;
- the installed msf-tools passes that checkout's lock check;
- every cached input has the SHA-256 that the record pins;
- every repository file that the run imports, the landmarks and the renderer source are as at `code_commit`;
- the renderer binary is the one that the record names.

It then runs the evaluation and reports whether its cells are equal to the published ones.

```sh
git worktree add /tmp/k3-freeze 91f57f7
python tools/calibration/k3_heldout.py --checkout /tmp/k3-freeze --ict-cache DIR --rig-cache DIR \
  --renderer BIN --work /tmp/k3-work --out heldout.json
```

To reproduce the published cells, three things must match the record, not the current checkout:

- **Code:** a checkout of the freeze commit `91f57f7`. Its `examples/`, `check.py` and `tools/render` are as at `code_commit` `ac0b953`.
- **msf-tools:** `746a5fe` (0.2.0.dev0), with the lock at that commit, and `msf-tools-ufbx` from the same commit. RCEF's lock has since moved to 0.3.0, so use a separate venv. The `check.py` in the freeze checkout refuses any other build.
- **Renderer:** the pinned binary (`binary_sha256` `a7cd2229…` in the record), or a build of source `e4bd7391…` (`git show 91f57f7:tools/render/meshrender.swift`). A rebuild may have a different binary hash, and `k3_heldout.py` refuses a binary whose hash differs. Images also depend on the OS and GPU (record: macOS 27.0.1 arm64, Apple M4 Max). `tools/render/meshrender.swift` on main has changed since the freeze.

The published cells were reproduced exactly in this way, with all three.
