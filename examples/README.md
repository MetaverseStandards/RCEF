# RCEF end-to-end examples

Original documentation: CC-BY-SA-4.0.

These examples run RCEF's published translations with the msf-tools public API, from CSV frames in to translated weights out, and then on a real face mesh. Everything here is synthetic input; nothing comes from a device.

## 1. Set up a fresh environment

From the RCEF checkout, with Python 3.11 or newer:

```sh
python3 -m venv .venv
. .venv/bin/activate
COMMIT=$(python -c "import json; print(json.load(open('evidence/tooling.lock.json'))['git_commit'])")
python -m pip install "git+https://github.com/Kjakubzak/msf-tools@$COMMIT"
# or, from a local checkout: python -m pip install "git+file://$(cd ../msf-tools && pwd -P)@$COMMIT"
# for the Rocketbox (FBX) rigs, also msf-tools' FBX reader from the same checkout:
# python -m pip install ../msf-tools/native/ufbx
python -B check.py
```

`check.py` refuses to run unless the installed msf-tools is exactly the locked commit, so a passing check also confirms the install. The examples need nothing else; they use only the Python standard library and msf-tools (with its FBX extra, `msf-tools-ufbx`, for the Rocketbox rigs, which needs a C compiler).

## 2. Translate FB2 frames to ARKit

```sh
python examples/translate_fb2_to_arkit.py
```

This reads `examples/data/fb2_demo_frames.csv` and writes `~/.cache/rcef-examples/fb2_to_arkit.csv` (under `$XDG_CACHE_HOME` instead of `~/.cache` when it is set), so nothing lands in the checkout. To choose the files, pass them: `python examples/translate_fb2_to_arkit.py INPUT.csv OUTPUT.csv`.

The input has one row per frame: `time`, a `segment` label, all 70 FB2 weights, and FB2's two validity flags, `isValid` and `isEyeFollowingBlendshapesValid`. The output has all 52 ARKit weights that RCEF's rules produce, plus two columns:

- `refused`: which mapping refused the frame and why. For example, when eye following is lost, `fb2_gaze.to_arkit` is refused while the face weights still come through.
- `dropped`: non-zero inputs that no RCEF rule reads, such as the tongue positions other than `TONGUE_OUT`.

The demo frames come from `examples/make_demo_frames.py`. They cover a neutral pose, a jaw sweep, gaze left and right with both eyes and then with each eye alone, asymmetric brows, asymmetric cheeks both ways round, closed lips with the jaw closed, each smile, chin raiser and blink channel on its own, every other channel an FB2 rule reads on its own, lost eye following during a blink, a lost face, and a tongue position with no rule. Every one of the 52 FB2 rules is the only thing moving in some frame, so `tests/test_examples.py` can check that halving the rules, swapping each left rule with its right one, or dropping an input of an averaged rule makes the face pipeline's oracles fail for every shape.

How it works (see `examples/rcef_translate.py`):

- It loads `generated/rcef.pack.json` and compiles `fb2.to_arkit` and `fb2_gaze.to_arkit` with the approximation opt-in, because RCEF's cross-provider rules are proposed approximations.
- Each mapping gets only its own `required_inputs`. msf-tools refuses a frame if any channel it is given is marked invalid, even one the mapping does not use. If each mapping were given the whole FB2 frame, invalid gaze would also stop the face.
- Each input's validity is the AND of the provider flags its signal record names, for example `isValid AND isEyeFollowingBlendshapesValid` for gaze.

`rcef_translate.arkit_to_fb2()` goes the other way, ARKit to FB2, with RCEF's inverse rules. FB2 allows only one of two opposing gaze weights (left/right, up/down) to be non-zero, and no msf-tools operator can enforce that, so a frame whose ARKit gaze would set both is refused for gaze, with a `refused` label naming the pair; the face weights still come through.

## 3. Translate META visemes to VRM

```sh
python examples/translate_visemes_to_vrm.py
```

This writes `~/.cache/rcef-examples/visemes_to_vrm.csv`; it takes the same optional input and output paths.

The five vowel visemes become VRM `aa`, `ih`, `ou`, `ee` and `oh`. Consonant visemes have no VRM preset, so they appear in `dropped`. This is a phoneme-label correspondence; no published table maps META visemes to VRM.

## 4. Drive a face and compare

```sh
python examples/face_pipeline.py                 # Rocketbox Female_Adult_01, the expression library
python examples/face_pipeline.py --rig rocketbox-male
python examples/face_pipeline.py --rig ict --frames examples/data/fb2_demo_frames.csv
```

Rig files go to `~/.cache/rcef-face-rigs` (`~/.cache/rcef-ict-facekit` for ICT) and the outputs to `~/.cache/rcef-examples/face/RIG` (under `$XDG_CACHE_HOME` when it is set); `--cache DIR` and `--out DIR` choose others. A Rocketbox run takes about three minutes, ICT about one.

### The faces

| Rig | Source | Shapes used |
|---|---|---|
| `rocketbox-female`, `rocketbox-male` | Microsoft Rocketbox `Female_Adult_01_facial.fbx` and `Male_Adult_01_facial.fbx` (MIT, commit `0943055`; ARKit shapes by Fang Ma and Matias Volonte), loaded directly with msf-tools' FBX reader | all 52 ARKit shapes (`AK_*`); its FACS action-unit shapes (`AU_*`) for the comparison panel; its 15 viseme shapes (`AA_VI_*`) in section 5 |
| `ict` | ICT-FaceKit Light (MIT, USC Institute for Creative Technologies, commit `da5f95a`), converted to a GLB | 16 of its ARKit shapes (all 53 would exceed msf-tools' budget); `browInnerUp` and `cheekPuff` are split into halves |

Each file is downloaded on first use and checked against a pinned SHA-256; none is stored in this repository. Rocketbox is a full-body avatar with a small face, so a renderer has to frame the head. All 53 ICT shapes would need about 4.3 million position components, more than msf-tools' 4 million budget, so only the 16 are converted.

### The frames

`examples/data/fb2_expression_frames.csv` comes from `examples/data/expressions.json` through `examples/make_expression_frames.py`. It holds 18 expressions (the seven EMFACS emotions, a compound "happily surprised", brow raise, squint, winks, smirk, pucker, cheek puff, lip suck and jaw sideways) and a gaze sweep, each as FACS action units with the sources that give them. FB2 channels are named after the action units, so the AUs become FB2 weights by name. FACS intensity letters become weights on an assumed linear scale (A = 0.2 … E = 1.0). Each expression ramps in, holds and ramps out, and its frames carry the expression name, the phase (`in`, `hold`, `out`) and the amount. AU 25 (lips part) and AU 27 (mouth stretch) have no FB2 channel; frames that need them say so.

### What is compared

For each frame the rig is evaluated with `msf_tools.evaluate_geometry(morph_weights=...)`:

- **direct**: the FB2 values routed to the ARKit shapes as the Godot and VRCFT sources route them (`tests/fixtures/godot_fb2_rules.csv`), all 52 on Rocketbox. On ICT each brow and cheek half takes its own FB2 side.
- **translated**: RCEF's translated ARKit weights. RCEF now writes all 52 coefficients; a shape a rule set did not write would stay at rest and be named on the frame ("no RCEF rule yet, direct render only"). FB2 channels no rule reads (the tongue positions other than `TONGUE_OUT`) are listed as dropped.
- **facs** (Rocketbox only): Rocketbox's own FACS action-unit shapes driven with the expression's AUs, beside the translated render with its own difference colours. This is a semantic comparison between two independently authored shape sets, labelled "not an error measure", and never an oracle. AUs Rocketbox has no shape for are named on the frame.

Outputs in the output directory:

| File | Contents |
|---|---|
| `fb2_to_arkit.csv` | the translated weights, refusals and dropped channels |
| `sidecar.json` | the msf-tools sidecar binding each ARKit shape to its ARKit signal |
| `mesh/indices.u32` | triangle indices of every mesh of the rig, little-endian uint32 |
| `mesh/direct/NNNN.f32`, `mesh/translated/NNNN.f32`, `mesh/facs/NNNN.f32` | vertex positions per frame, little-endian float32 xyz |
| `mesh/difference/NNNN.f32`, `mesh/facs_difference/NNNN.f32` | per-vertex difference colours, float32 RGB (blue = none, red = `heat_scale` or more) |
| `frames.json` | the rig and its credit, the captions, and every frame's time, expression, phase, amount, files, labels, largest vertex difference and oracle result |
| `residuals.csv`, `residuals.md` | the residual report, per frame and per channel |

The position, index and colour files are in the format of the offscreen renderer used for the msf-tools geometry video.

The report checks four things:

- Exact rules have residual ≤ 1e-9. On Rocketbox, `browInnerUp` and `cheekPuff` are single shapes, so their averaging rules are exact there too.
- On ICT, each half of an averaged pair is within |L − R| / 2 of its own side.
- The largest vertex difference stays within the sum of each residual times that shape's largest vertex move, plus the whole direct movement of shapes no rule writes yet.
- Refused and dropped channels, and shapes without a rule, are labelled on their frame and never shown as a silent zero.

The pipeline exits non-zero if any oracle fails. `residuals.md` counts channels that are zero in both paths as "at rest in both paths", apart from "exact (moving)", and lists for each shape whether an RCEF rule writes it and in how many frames its FB2 input moves.

`examples/data/fb2_demo_frames.csv` is built so that every one of the 52 FB2 rules is the only thing moving in some frame; `tests/test_examples.py` checks that halving the rules, swapping each left rule with its right one, or dropping an input of an averaged rule makes these oracles fail for every shape.

**What this shows and what it doesn't.** It shows that RCEF's rules connect names and meanings the way the public sources do, on two independently authored rigs. It is not a calibration result: neither provider publishes its gain, so equal weights are assumed to mean equal expressions. No cross-rig equality is expected either.

## 5. Talking: visemes on a face

```sh
python examples/viseme_pipeline.py                  # Rocketbox, its own viseme shapes
python examples/viseme_pipeline.py --rig vrm-twist  # the VRM sample, through RCEF
```

The frames (`examples/data/viseme_talk_frames.csv`) say "bed car toe book", the META viseme specification's own example words: each viseme is held for two frames and crossfaded into the next, so every frame sums to one.

- **Rocketbox** has a shape for each of the 15 META visemes, numbered in the same order (it spells IH, OH and OU as I, O and U), so the frames drive them directly by name.
- **VRM1_Constraint_Twist_Sample** (pixiv Inc., VRM Public License 1.0, redistribution and modification allowed, credit not required; vrm-specification commit `94e82dd`) has the five vowel presets. RCEF's `visemes.to_vrm` rules translate the frames, and `examples/vrm_presets.py` turns presets into morph weights through the model's own binds, following the VRM 1.0 expression specification (values clamped to [0, 1], `isBinary`, binds accumulated). The same binds driven through the vowel pairs that `scripts/derive_fb2_goldens.py` reads from the pinned VRM and META texts (`tests/fixtures/fb2_goldens.json`) must give the same morph weights within 1e-9. Consonants have no VRM preset and are labelled as dropped. Overrides are not applied and are labelled if a frame would need one. After the talk come the two winks from the expression library: RCEF's `fb2.to_vrm` rules turn FB2 `EYES_CLOSED_L` and `_R` into `blinkLeft` and `blinkRight`, checked the same way against the blink pairs read from the pinned OpenXR and VRM texts. `blink` (both eyes) is left unset, so a model that binds all three is not driven twice.

Outputs go to `~/.cache/rcef-examples/visemes/RIG`, in the same format as section 4.

To run the pipelines as tests (the slow tier, not part of the default suite; about ten minutes):

```sh
RCEF_SLOW_TESTS=1 RCEF_ICT_CACHE=~/.cache/rcef-ict-facekit RCEF_RIG_CACHE=~/.cache/rcef-face-rigs \
  python -B -m unittest tests/test_examples_slow.py
```

With `RCEF_SLOW_TESTS=1`, `tests/test_translations.py` also halves each translation rule on its own and checks that only its output changes (about half a minute).

## 6. Rig gains: how strongly two rigs render the same ARKit name

Sections 4 and 5 assume equal weights mean equal expressions. Between two example rigs that assumption can be tested in software. `examples/rig_gains.py` fits, for each ARKit shape that ICT-FaceKit and Rocketbox Female both have (51; ICT has no `tongueOut`), a monotone curve from an ICT weight to the Rocketbox Female weight that moves her face about as much, and evaluates it on an ICT identity it was not fitted to. It follows the calibration-record protocol in [calibration/README.md](../calibration/README.md); the record is `calibration/rig-gains.ict-rocketbox-female.cal`.

This calibrates how two example rigs render ARKit names, with ICT-FaceKit as the reference by choice. It is not a measurement of any tracker, not a provider claim and not pack data. Rocketbox Male is never loaded: it is reserved as an unseen rig for a later method.

```sh
swiftc -O -o /tmp/meshrender tools/render/meshrender.swift
python examples/rig_gains.py fit --ict-cache DIR --rig-cache DIR --renderer /tmp/meshrender --work /tmp/k3 --out fit.json
python examples/rig_gains.py evaluate --record calibration/rig-gains.ict-rocketbox-female.cal \
  --ict-cache DIR --rig-cache DIR --renderer /tmp/meshrender --work /tmp/k3 --out cells.json
python examples/rig_gains.py export --record calibration/rig-gains.ict-rocketbox-female.cal --out examples/data/rig_gains.json
```

The ICT cache needs ICT-FaceKit's 53 expression shapes and its first ten identity modes (`ict_facekit.CALIBRATION_FILES`, about 160 MB, fetched and checked on first use). The identity modes are principal components of light-stage scans of real people; they are used only as geometry.

**How motion is compared.** The landmarks in `examples/data/rig_landmarks.json` (37 per rig: Multi-PIE 68 points on ICT, hand-picked or rule-based counterparts on Rocketbox, each with its provenance) are painted as small coloured markers on otherwise black meshes and rendered unlit with `tools/render/meshrender`, from jittered cameras framed by each rig's own eye distance. A marker's position is its colour centroid in the image, so markers hidden by a lid or a lip drop out. For each ICT pose, the best Rocketbox weight is the one whose marker displacements are nearest to ICT's. The curve's knots at ICT weights 0.25, 0.5, 0.75 and 1 are the medians over 24 training conditions (8 ICT identities, 3 cameras), made non-decreasing. The module docstring gives every constant and failure rule.

**Results are per shape.** A shape passes if, on the held-out identity, the curve's error is within the record's bounds and the expected response is detected in every condition. A condition is a failure if Rocketbox at its best weight explains less than half of ICT's motion (the shapes move different regions or directions), or if Rocketbox cannot reach ICT's motion at weight 1. A monotone curve cannot fix either, so those shapes are published as failed rather than forced.

`examples/data/rig_gains.json` holds the curves of the shapes that passed and lists the others. `python examples/rigs.py --rig rocketbox-female --cache DIR --set mouthSmileLeft=0.6 --normalise --out pose` poses Rocketbox Female through it; without `--normalise` the weights are used as they are.

To reproduce the fit and the held-out cells for two shapes as a test (slow tier, about half a minute):

```sh
RCEF_SLOW_TESTS=1 RCEF_K3_ICT_CACHE=DIR RCEF_RIG_CACHE=DIR RCEF_RENDERER=/tmp/meshrender \
  python -B -m unittest tests/test_rig_gains.py
```
