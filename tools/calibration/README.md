# Calibration tools

Optional tools that produce calibration records (see [calibration/README.md](../../calibration/README.md)). They need packages RCEF itself does not use, so `check.py` and the tests never run them; the tests check only their pure fitting and scoring code.

## MediaPipe's response to untextured ICT renders (`k4_mediapipe.py`)

Measures how MediaPipe's Face Landmarker scores renders of ICT-FaceKit, one ARKit coefficient at a time, and fits a curve from each MediaPipe score back to the ICT weight. The licence check for the model is [docs/calibration/mediapipe-licence.md](../../docs/calibration/mediapipe-licence.md).

Needs Python 3.11+, numpy, mediapipe, msf-tools at the locked commit with msf-tools-ufbx (for Rocketbox), and a renderer built from [tools/render](../render/README.md). With uv:

```sh
uv venv k4-venv && uv pip install --python k4-venv/bin/python mediapipe numpy \
  "msf-tools @ git+https://github.com/Kjakubzak/msf-tools@COMMIT" \
  "msf-tools-ufbx @ git+https://github.com/Kjakubzak/msf-tools@COMMIT#subdirectory=native/ufbx"
swiftc -O -o meshrender tools/render/meshrender.swift
```

Steps, in order:

1. `k4-venv/bin/python tools/calibration/k4_mediapipe.py fetch` downloads ICT-FaceKit's neutral head, its 53 expression shapes and its first 10 identity modes, at commit `da5f95a`, and MediaPipe's model, into `~/.cache/rcef-ict-full`, checking each file against the SHA-256 in [ict_files.json](ict_files.json) or the script. Nothing is committed.
2. `train --renderer meshrender` renders 24 training conditions, each on its own ICT identity, with every channel swept alone at 0, 0.2, …, 1, and scores every render with MediaPipe.
3. `freeze --renderer meshrender` fits each channel and writes `calibration/mediapipe.ict-response.cal` without cells, plus its line in `calibration/FREEZES`. The harness must be committed first, because the record names the commit. **Commit the record and the ledger line before step 4.**
4. `heldout --renderer meshrender` refuses unless that commit exists, the installed msf-tools passes `check.py`'s lock check, every cached input has the SHA-256 the record's `inputs` pin, and every repository file the run imports (found from the loaded modules, so `check.py` and `examples/` count too), `ict_files.json` and the renderer source are exactly as at the record's `code_commit`; it prints that file list and saves it with the scores (to reproduce a published record, check out its freeze commit). It then renders 20 held-out conditions from the seeds the record's frozen hash fixes: on new ICT identities, and on Rocketbox Male, which training never used.
5. `evaluate` adds the cells to the record and writes rules for the channels whose cells all pass to [results/mediapipe_arkit.rules](results/), which moves into `mappings/` once RCEF adopts msf-tools operators 1.1.

Renders and scores go to `~/.cache/rcef-k4`. A run takes a few minutes on an Apple M-series Mac.

## Rig gains: re-running the held-out evaluation (`k3_heldout.py`)

Record `rig-gains.ict-rocketbox-female` was made by `examples/rig_gains.py` (see [examples/README.md](../../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name)), frozen at commit `91f57f7` with `code_commit` `ac0b953`, before `provenance.py` existed. Later commits changed `check.py` and `tools/render`, so a held-out run must use a checkout of the freeze commit. `k3_heldout.py`, run from a current checkout, checks that checkout first, in the same way as `k4_record.py heldout`:

- the record and its ledger line are committed there;
- the installed msf-tools passes that checkout's lock check;
- every cached input has the SHA-256 the record pins;
- every repository file the run imports, the landmarks and the renderer source are as at `code_commit`;
- the renderer binary is the one the record names.

It then runs the evaluation and reports whether its cells equal the published ones.

```sh
git worktree add /tmp/k3-freeze 91f57f7
python tools/calibration/k3_heldout.py --checkout /tmp/k3-freeze --ict-cache DIR --rig-cache DIR \
  --renderer BIN --work /tmp/k3-work --out heldout.json
```

To reproduce the published cells, three things must match the record, not the current checkout:

- **Code:** a checkout of the freeze commit `91f57f7`. Its `examples/`, `check.py` and `tools/render` are as at `code_commit` `ac0b953`.
- **msf-tools:** `746a5fe` (0.2.0.dev0), the lock at that commit, installed with `msf-tools-ufbx` from the same commit. RCEF's lock has since moved to 0.3.0, so use a separate venv. The freeze checkout's `check.py` refuses any other build.
- **Renderer:** the pinned binary (`binary_sha256` `a7cd2229…` in the record), or a build of source `e4bd7391…` (`git show 91f57f7:tools/render/meshrender.swift`). A rebuild has a new binary hash, so `k3_heldout.py` refuses it; images also depend on OS and GPU (record: macOS 27.0.1 arm64, Apple M4 Max). `tools/render/meshrender.swift` on main has changed since.

The published cells were reproduced exactly this way, with all three.
