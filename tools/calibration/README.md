# Calibration tools

These optional tools make calibration records (see [calibration/README.md](../../calibration/README.md)). They need packages that RCEF itself does not use, so `check.py` and the tests never run them. The tests check only the parts that fit curves and score cells, without rendering.

## MediaPipe's response to untextured ICT renders (`k4_mediapipe.py`)

This tool renders ICT-FaceKit with one ARKit coefficient moving at a time and scores each render with MediaPipe's Face Landmarker. It then fits a curve from each MediaPipe score back to the ICT weight. The licence check for the model is in [docs/calibration/mediapipe-licence.md](../../docs/calibration/mediapipe-licence.md).

The tool needs Python 3.11+, numpy, mediapipe, the locked msf-character-tools release wheel (it reads the Rocketbox FBX rigs itself), and a renderer built from [tools/render](../render/README.md). `msf-character-tools.txt` is the hashed requirement from [Getting started](../../docs/getting-started.md#install-the-wheel-by-hash). It is a separate install because `--require-hashes` needs a hash for every package it installs. With uv:

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

`examples/rig_gains.py` made the record `rig-gains.ict-rocketbox-female` (see [examples/README.md](../../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name)). Version 2 of the record was frozen at commit `dd9ecd2`, with `code_commit` `7cd8ff9`. Version 1 was made before the Git history was rewritten for publication, and its commits are not in this repository. The v2 frozen part is v1's with only `version`, `code_commit` and the renderer hashes replaced (and so `frozen_sha256`). Its knots come from `python examples/rig_gains.py fit` at `code_commit`, and they are equal to v1's. Give `k3_heldout.py` a checkout of the freeze commit with `--checkout`. A later commit is also accepted if the code that the record names has not changed since `code_commit`. That holds only for commits before `c98ca32`, which changed `check.py`; from then on, use the freeze commit. Like the `heldout` step of `k4_mediapipe.py`, it first checks that the checkout meets these conditions:

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
- **msf-character-tools:** 0.5.0, the release wheel that the lock at the freeze commit names, installed by hash (see [Getting started](../../docs/getting-started.md#install-the-wheel-by-hash)). The `check.py` in the checkout refuses any other build.
- **Renderer:** the pinned binary (`binary_sha256` `60e618ff…` in the record), or a build of source `913c1641…` (`tools/render/meshrender.swift` at the freeze commit) with `swiftc -O`. A rebuild may have a different binary hash, and `k3_heldout.py` refuses a binary whose hash differs. Images also depend on the OS and GPU (record: macOS 27.0.1 arm64, Apple M4 Max).

A second held-out run, with the same code, msf-character-tools build and renderer binary, gave cells equal to the published ones.

## Viseme poses: META viseme shapes in ARKit shapes (`viseme_poses.py`)

This tool makes the record `viseme-poses.rocketbox-features`. For each canonical viseme class, it fits one combination of ARKit shapes, with weights from 0 to 1 and each Left and Right pair tied, to the META viseme shapes of the 18 training rigs at once. For 4 classes it also fits visible mouth features, which the record's perceptual gate checks. It carries the weights to canonical expression signals through the ARKit in-maps. The pose bridge in the [canonical set](../../docs/canonical-set.md#viseme-pose-bridge) uses the poses of the classes that pass.

The earlier records were made by earlier versions of this tool (see [calibration/README.md](../../calibration/README.md#frozen-part-ledger-and-held-out-seeds)). The versions frozen before the history rewrite (`viseme-poses.rocketbox-female` v1, freeze commit `605c4f9`; `viseme-poses.rocketbox-multi` v1, `6417863`, and v2, `61660f1`; `viseme-poses.rocketbox-features` v1, `4a5768c`) name code commits that are not in this repository, so their held-out step can no longer be run. The versions in the checkout were frozen again after the history rewrite, each on a branch from the freeze commit of the version before it, and each is reproduced from its own freeze commit: `viseme-poses.rocketbox-female` v2 from `01a8862`, `viseme-poses.rocketbox-multi` v3 from `bd4eeea` and `viseme-poses.rocketbox-features` v2 from `533602a`. The method choice of version 1 (the table below, left and right apart) was made with the `cv` step at `0d3ee83`; version 2 took the best mirror-symmetric candidate of that table.

The tool uses only mesh geometry, so it needs no renderer and no extra packages: Python 3.11+ and the locked msf-character-tools release wheel, which reads the Rocketbox FBX files. The rig sets are in [viseme_rigs.json](viseme_rigs.json) (see [below](#rig-sets-for-the-multi-rig-viseme-poses-viseme_rigsjson)). Do these steps in this order:

1. Commit the code. `python tools/calibration/viseme_poses.py cv --rig-cache DIR` prints the leave-one-rig-out comparison of the feature sets and fit weights. It loads only the training rigs. It takes about 6 minutes.
2. `freeze --rig-cache DIR` checks that the rig sets follow their rules, fits the training rigs, sets the feature tolerances, writes `calibration/viseme-poses.rocketbox-features.cal` without cells and adds its line to `calibration/FREEZES`. It never loads a held-out rig. **Commit the record and the ledger line before step 3.**
3. `heldout --rig-cache DIR` refuses to run unless the record and its ledger line are committed, the installed msf-character-tools passes `check.py`'s lock check, the rig files and the pack have the SHA-256 that the record pins, and every repository file that the run imports, and `viseme_rigs.json`, is as at the record's `code_commit`. It then loads the held-out rigs and adds one shape cell per class and rig, and one feature cell per gated class, feature and rig, all on the held-out seeds. `--out FILE` also writes them as JSON. It takes under a minute.

The fit:

- **Basis:** the 37 ARKit shapes that the in-maps of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip` read, each Left and Right pair sharing one weight (24 weights). The blink and gaze shapes (`eyeBlink*`, `eyeLook*`), `jawLeft`, `jawRight`, `mouthLeft`, `mouthRight` and `tongueOut` are left out.
- **Region:** on each rig, every vertex except the tongue, which is every vertex that the rig's `tongueOut` moves by more than 1% of its largest move.
- **Every class:** the weights with the smallest largest whole-mesh error over the training rigs (Lawson reweighting of bounded least squares, 100 rounds, each by cyclic coordinate descent to a change below 10⁻¹³).
- **Gated classes** (`bilabial`, `vowel_close_rounded`, `vowel_mid_spread`, `alveolar_sibilant`): from there, 8 Gauss-Newton steps with Levenberg damping on the sum over the training rigs of the squared whole-mesh error plus each squared feature error divided by its tolerance (for a range feature, its distance from the middle of the range divided by half the width).
- Weights are rounded to 3 decimals.

The features (class `Mouth` in the tool) are measured on landmark vertices that each rig's own ARKit shapes pick out, so the same rule applies to any Rocketbox rig. The centre is the vertex that `jawOpen` moves most. The lips are the vertices that `mouthFunnel` moves by more than 20% of its largest move, within 1 cm of the centre's height. A lip vertex is upper lip if `jawOpen` moves it by less than 30% of its largest move, and lower lip if by more than 60%. The mid line is |x| ≤ 3 mm. The corners are the lip vertices that `mouthSmileLeft` and `mouthSmileRight` move most. The lower teeth are vertices that `jawOpen` moves by more than 80% and `mouthFunnel` by less than 5%, behind the lips and near the centre.

- `lip_opening_mm`: the lowest mid-line upper-lip landmark minus the highest mid-line lower-lip landmark. It is negative when the inner edges overlap.
- `lip_protrusion_mm`: the mean forward movement of the mid-line lip landmarks within 2 cm of the centre's height.
- `corner_width_ratio`: the distance between the corners, divided by the neutral distance.
- `jaw_drop_mm`: the mean downward movement of the lower-teeth landmarks.
- `teeth_to_lower_lip_mm` (tried for `labiodental`, not used): the smallest distance from an upper-teeth landmark to a lower-lip landmark.
- `whole_face_error`, the guard of every gated class: the whole-mesh error of the condition, which must be at most 1.

The tolerance of a difference feature is the largest distance of a training rig's own viseme feature from the median over the 18 training rigs, at least 0.5 mm or 0.02, rounded up to 3 decimals. The `bilabial` lip opening has a fixed range instead, from −2.0 to 0.5 mm. The upper end is the largest neutral opening of any training rig (0.49 mm), rounded up: lips at rest count as closed. The lower end allows the overlap of the rigs' own PP shapes (down to −1.4 mm) and no deeper pass-through.

Two tolerances are loose because the training rigs split. The `alveolar_sibilant` lip-opening tolerance, 2.35 mm, comes from one rig: Male_Adult_03's SS opens the lips by 2.06 mm, against a median of 4.41 mm. Without that rig it would be about 0.96 mm. The `vowel_mid_spread` corner width ratio falls into two groups: 1.00 to 1.02 on 7 training rigs, whose E shape does not widen the mouth, and 1.07 to 1.24 on the other 11. Its tolerance, 0.197, spans both groups, so a pose passes it with either width.

How the gate was chosen, on the training rigs only. For each candidate feature set, the poses were fitted to 17 training rigs and scored on the 18th, for each of the 18 rigs, at class weights 1, 0.6 and 0.2. A set was kept if every fold passed and the neutral face passes it on at most half of the training rigs, so that it tests something. The fit weight of the whole-mesh error, 1 or 4, was the one with the most classes kept, then the lowest largest error over tolerance. Results (`cv` at `333d928`; largest error over tolerance in the folds, range features in mm outside the range):

| Class | Features | Shape-only pose: folds failing | Fit weight 1: folds failing | Largest error / tolerance (weight 1) | Whole-mesh error (largest) | Neutral face passes |
|---|---|---|---|---|---|---|
| `bilabial` | lip opening (range), protrusion | 18 of 18 | 0 of 18 | 0.000 mm, 0.178 | 0.819 | 0 of 18 |
| `vowel_close_rounded` | corner width, protrusion | 18 of 18 | 0 of 18 | 0.584, 0.466 | 0.928 | 0 of 18 |
| `vowel_mid_spread` | corner width, lip opening | 18 of 18 | 0 of 18 | 0.450, 0.643 | 0.635 | 0 of 18 |
| `alveolar_sibilant` | lip opening, jaw drop | 0 of 18 | 0 of 18 | 0.665, 0.001 | 0.780 | 1 of 18 |
| `labiodental` | teeth to lower lip | 0 of 18 | 0 of 18 | 0.282 | 0.933 | 18 of 18 (rejected) |
| `labiodental` | teeth to lower lip, lip opening | 14 of 18 | 1 of 18 (rejected) | 0.169, 2.671 | 0.969 | 0 of 18 |

Fit weight 4 kept the same classes with slightly larger errors over tolerance, so weight 1 was chosen. A first trial for `bilabial` asked for the lip compression of the rigs' own PP shapes (the lips get about 5 mm thinner). No combination of the ARKit shapes met it without moving the inner lip edges past each other, so the gate asks for closed and drawn-back lips instead.

The held-out cells use 24 conditions, one per seed: the class at a weight from 0.2 to 1, and in half the conditions `sil` at 1 minus that weight. The shape error is as in the earlier records. The feature error of a condition compares the reconstruction with the rig's own viseme shapes at the same weights. A shape cell passes if its median and p95 errors are at most 0.5 and its neutral error is at most 0.01. A feature cell passes if its largest error is within the tolerance. A class passes if its shape cells pass on all 4 held-out rigs, or if all its feature cells do.

### Version 1 and 2 of `viseme-poses.rocketbox-multi`

How version 1's method was chosen, on its 10 training rigs only. Each candidate was fitted to 9 training rigs and scored on the 10th, for each of the 10 rigs. The candidates were: an objective that sums the squared errors or makes the largest error small (minimax); Left and Right with their own weights or one shared weight (mirror-symmetric); and the lip region (the vertices that `mouthFunnel` moves by more than 20% of its largest move) weighted 5 times or not. The rule was to take the candidate with the most classes at or below 0.5 on every left-out rig, then the lowest mean of the largest error per class. Results (`cv` at `0d3ee83`):

| Candidate | Classes at or below 0.5 on every left-out rig | Mean of the largest error per class |
|---|---|---|
| Female_Adult_01 alone, mirror-symmetric, least squares (the method of `viseme-poses.rocketbox-female`) | 7 | 0.514 |
| minimax, Left and Right apart (version 1) | 8 | 0.479 |
| least squares, Left and Right apart | 7 | 0.484 |
| minimax, mirror-symmetric (version 2) | 8 | 0.506 |
| least squares, mirror-symmetric | 7 | 0.513 |
| minimax, Left and Right apart, lip region ×5 | 6 | 0.499 |
| least squares, Left and Right apart, lip region ×5 | 7 | 0.495 |
| minimax, mirror-symmetric, lip region ×5 | 6 | 0.526 |
| least squares, mirror-symmetric, lip region ×5 | 7 | 0.522 |
| each rig fitted to itself (a floor, not a candidate) | 9 | 0.443 |

Version 1 left Left and Right apart. Its poses differed between the sides by up to 0.56, more than its limitations said, so version 2 tied them and was held out on fresh rigs. Its report-only lips step wrote [results/viseme_lips.json](results/viseme_lips.json).

## Rig sets for the multi-rig viseme poses (`viseme_rigs.json`)

The viseme pose record `viseme-poses.rocketbox-multi` is fitted on several Rocketbox rigs and held out on others. [viseme_rigs.json](viseme_rigs.json) fixes the rig sets. They were chosen by a rule, before any new rig was downloaded. Only the HTTP status and size of each file at Rocketbox commit `0943055` were known then.

- **Candidates:** every `Female_Adult_NN` and `Male_Adult_NN` facial FBX at that commit, except `_01`. That is `Female_Adult_02` to `_17` and `Male_Adult_02` to `_21`.
- **Training:** `Female_Adult_01` and `Male_Adult_01`, plus 4 new rigs of each sex. Rocketbox Male_Adult_01 was the held-out rig of `viseme-poses.rocketbox-female`, so it may be used for training but never again as a held-out rig.
- **Held out:** 2 new rigs of each sex.
- **Rule:** for each sex, sort the candidates by the lowercase hex SHA-256 of their name (for example `Female_Adult_04`, UTF-8). The first 2 are held out, and the next 4 are training. If a chosen rig cannot be downloaded or loaded, or does not have the 52 ARKit shapes and the 15 viseme shapes, it goes under `replaced`, and the next unused candidate of the same sex in that order takes its place.

The result: training `Female_Adult_01`, `_08`, `_10`, `_12`, `_14`, `Male_Adult_01`, `_03`, `_10`, `_13` and `_17`; held out `Female_Adult_04`, `_13`, `Male_Adult_05` and `_11`. The fit and its method choices may use only the training rigs. Before each freeze, the held-out rigs were loaded only to count their shapes (52 ARKit and 15 viseme shapes), as the replacement clause of the rule needs. No fit, cross-validation or tolerance read their geometry before the record's frozen part and ledger line were committed.

**Version 2.** Version 1 of the record gave Left and Right their own weights, and its poses differed between the sides by up to 0.56, more than its limitations said. Version 2 ties Left and Right and needs fresh held-out rigs, because the version 1 held-out rigs have been seen. The extended rule, committed before any of the new rigs was downloaded:

- The rigs that version 1 held out (`Female_Adult_04`, `_13`, `Male_Adult_05` and `_11`) go under `seen`. They are never held out again. They do not join training: training stays as in version 1.
- For each sex, the next 2 candidates in the same SHA-256 order that no set has used are held out. Replacement works as before.

The result: held out `Female_Adult_06`, `_17`, `Male_Adult_02` and `_19`.

**Rounds.** From the perceptual record on, `viseme_rigs.json` lists one round per record version under `rounds`, each with its rule, training and held-out rigs. Round 3, for `viseme-poses.rocketbox-features` v1, was committed before any of its new rigs was downloaded:

- Training is the 10 training rigs of round 2 plus the 8 rigs that rounds 1 and 2 held out: 18 rigs. The reason is training-only: the perceptual tolerances are set from how much the rigs' own visemes differ, and the leave-one-rig-out cross-validation that chooses the method needs as many rigs as can be had. No rig that was held out is held out again.
- For each sex, the next 2 candidates in the SHA-256 order that no round has used are held out: `Female_Adult_09`, `_15`, `Male_Adult_08` and `_15`.
