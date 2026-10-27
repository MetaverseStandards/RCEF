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
4. `heldout --renderer meshrender` refuses unless that commit exists, the installed msf-tools passes `check.py`'s lock check, and every repository file the run imports (found from the loaded modules, so `check.py` and `examples/` count too) and the renderer source are exactly as at the record's `code_commit`; it prints that file list and saves it with the scores (to reproduce a published record, check out its freeze commit). It then renders 20 held-out conditions from the seeds the record's frozen hash fixes: on new ICT identities, and on Rocketbox Male, which training never used.
5. `evaluate` adds the cells to the record and writes rules for the channels whose cells all pass to [results/mediapipe_arkit.rules](results/), which moves into `mappings/` once RCEF adopts msf-tools operators 1.1.

Renders and scores go to `~/.cache/rcef-k4`. A run takes a few minutes on an Apple M-series Mac.
