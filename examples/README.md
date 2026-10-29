# RCEF end-to-end examples

Original documentation: CC-BY-SA-4.0.

These examples run RCEF's published translations with the msf-character-tools public API. They start with CSV frames in and translated weights out, and then drive a real face mesh. All input here is synthetic; nothing comes from a device.

## 1. Set up a fresh environment

From the RCEF checkout, with Python 3.11 or newer:

```sh
python3 -m venv .venv
. .venv/bin/activate
```

Install the locked msf-character-tools release wheel into it by hash, as [Getting started](../README.md#getting-started) shows. With this venv's pip, the last step is `python -m pip install --require-hashes -r "$DIR/msf-character-tools.txt"`. Then check the install:

```sh
python -B check.py
```

`check.py` refuses to run unless the installed msf-character-tools is exactly the locked release wheel, so a passing check also confirms the install. The examples need nothing else. They use only the Python standard library and msf-character-tools, which reads the Rocketbox FBX rigs itself.

## 2. Translate FB2 frames to ARKit

```sh
python examples/translate_fb2_to_arkit.py
```

This reads `examples/data/fb2_demo_frames.csv` and writes `~/.cache/rcef-examples/fb2_to_arkit.csv` (under `$XDG_CACHE_HOME` instead of `~/.cache` when it is set), so nothing is written to the checkout. To choose the files, give them as arguments: `python examples/translate_fb2_to_arkit.py INPUT.csv OUTPUT.csv`.

The input has one row per frame: `time`, a `segment` label, all 70 FB2 weights, and FB2's two validity flags, `isValid` and `isEyeFollowingBlendshapesValid`. The output has all 52 ARKit weights that RCEF's mappings produce, plus two columns:

- `refused`: which map refused the frame, and why. For example, when eye following is lost, `fb2_gaze.to_arkit` is refused, but the face weights still come through.
- `dropped`: non-zero inputs that no RCEF mapping reads, such as the tongue positions other than `TONGUE_OUT`.

The demo frames come from `examples/make_demo_frames.py`. They cover a neutral pose, a jaw sweep, gaze left and right with both eyes and then with each eye alone, asymmetric brows, asymmetric cheeks both ways round, closed lips with the jaw closed, each smile, chin raiser and blink channel on its own, every other channel that an FB2 mapping reads, on its own; lost eye following during a blink; a lost face; and a tongue position with no mapping. Each of the 52 FB2 mappings is the only thing moving in some frame. Section 4 explains how the tests use this.

How it works (see `examples/rcef_translate.py`):

- It loads `generated/rcef.pack.json` and compiles `fb2.to_arkit` and `fb2_gaze.to_arkit` with the approximation opt-in, because RCEF's cross-provider mappings are proposed approximations.
- Each map gets only its own `required_inputs`. msf-character-tools refuses a frame if any channel it is given is marked invalid, even a channel that the map does not use. If each map got the whole FB2 frame, invalid gaze would also stop the face.
- Each input's validity is the AND of the provider flags its signal record names, for example `isValid AND isEyeFollowingBlendshapesValid` for gaze.

`rcef_translate.arkit_to_fb2()` goes the other way, from ARKit to FB2, with RCEF's inverse mappings. FB2 allows only one of two opposing gaze weights (left/right, up/down) to be non-zero. The mappings take the difference of the two ARKit directions and split it into its two sides. So when ARKit sets both, only the larger one survives, reduced by the smaller one, and the two are never both non-zero.

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
| `rocketbox-female`, `rocketbox-male` | Microsoft Rocketbox `Female_Adult_01_facial.fbx` and `Male_Adult_01_facial.fbx` (MIT, commit `0943055`; ARKit shapes by Fang Ma and Matias Volonte), loaded directly with msf-character-tools' FBX reader | all 52 ARKit shapes (`AK_*`); its FACS action-unit shapes (`AU_*`) for the comparison panel; its 15 viseme shapes (`AA_VI_*`) in section 5 |
| `ict` | ICT-FaceKit Light (MIT, USC Institute for Creative Technologies, commit `da5f95a`), converted to a GLB | 16 of its ARKit shapes (all 53 would exceed msf-character-tools' budget); `browInnerUp` and `cheekPuff` are split into halves |

Each file is downloaded on first use and checked against a pinned SHA-256; none is stored in this repository. Rocketbox is a full-body avatar with a small face, so a renderer has to frame the head. All 53 ICT shapes would need about 4.3 million position components, more than msf-character-tools' 4 million budget, so only the 16 are converted.

### The frames

`examples/data/fb2_expression_frames.csv` comes from `examples/data/expressions.json` through `examples/make_expression_frames.py`. It holds 18 expressions (the seven EMFACS emotions, a compound "happily surprised", brow raise, squint, winks, smirk, pucker, cheek puff, lip suck and jaw sideways) and a gaze sweep, each as FACS action units with the sources that give them. FB2 channels are named after the action units, so the AUs become FB2 weights by name. FACS intensity letters become weights on an assumed linear scale (A = 0.2 … E = 1.0). Each expression ramps in, holds and ramps out, and its frames carry the expression name, the phase (`in`, `hold`, `out`) and the amount. AU 25 (lips part) and AU 27 (mouth stretch) have no FB2 channel; frames that need them say so.

### What is compared

For each frame the rig is evaluated with `msf_character_tools.evaluate_geometry(morph_weights=...)`:

- **direct**: the FB2 values routed to the ARKit shapes as the Godot and VRCFT sources route them (`tests/fixtures/godot_fb2_rules.csv`), all 52 on Rocketbox. On ICT each brow and cheek half takes its own FB2 side.
- **translated**: RCEF's translated ARKit weights. RCEF writes all 52 coefficients. If no mapping wrote a shape, that shape would stay at rest and be named on the frame ("no RCEF rule yet, direct render only"). FB2 channels that no mapping reads (the tongue positions other than `TONGUE_OUT`) are listed as dropped.
- **facs** (Rocketbox only): Rocketbox's own FACS action-unit shapes driven with the expression's AUs, beside the translated render with its own difference colours. This compares the meaning of two shape sets that were authored independently. It is labelled "not an error measure" and is never an oracle. AUs Rocketbox has no shape for are named on the frame.

Outputs in the output directory:

| File | Contents |
|---|---|
| `fb2_to_arkit.csv` | the translated weights, refusals and dropped channels |
| `sidecar.json` | the msf-character-tools sidecar binding each ARKit shape to its ARKit signal |
| `mesh/indices.u32` | triangle indices of every mesh of the rig, little-endian uint32 |
| `mesh/direct/NNNN.f32`, `mesh/translated/NNNN.f32`, `mesh/facs/NNNN.f32` | vertex positions per frame, little-endian float32 xyz |
| `mesh/difference/NNNN.f32`, `mesh/facs_difference/NNNN.f32` | per-vertex difference colours, float32 RGB (blue = none, red = `heat_scale` or more) |
| `frames.json` | the rig and its credit, the captions, and every frame's time, expression, phase, amount, files, labels, largest vertex difference and oracle result |
| `residuals.csv`, `residuals.md` | the residual report, per frame and per channel |

The position, index and colour files are in the format of the offscreen renderer used for the msf-tools geometry video.

The report checks four things:

- Exact mappings have residual ≤ 1e-9. On Rocketbox, `browInnerUp` and `cheekPuff` are single shapes, so their averaging mappings are exact there too.
- On ICT, each half of an averaged pair is within |L − R| / 2 of its own side.
- The largest vertex difference stays within the sum of each residual times that shape's largest vertex move, plus the whole direct movement of shapes that no mapping writes yet.
- Refused and dropped channels, and shapes without a mapping, are labelled on their frame. They are never shown as a silent zero.

The pipeline exits non-zero if any oracle fails. `residuals.md` counts channels that are zero in both paths as "at rest in both paths", separately from "exact (moving)". For each shape, it lists whether an RCEF mapping writes it and in how many frames its FB2 input moves.

`examples/data/fb2_demo_frames.csv` is built so that each of the 52 FB2 mappings is the only thing moving in some frame. `tests/test_examples.py` uses this to check that these oracles fail for every shape if the mappings are halved, if each left mapping is swapped with its right one, or if an input of an averaged mapping is dropped.

**What this shows and what it does not.** It shows that RCEF's mappings connect names and meanings in the same way as the public sources, on two rigs that were authored independently. It is not a calibration result. Neither provider publishes its gain, so equal weights are assumed to mean equal expressions. Also, the two rigs are not expected to look the same.

## 5. Talking: visemes on a face

```sh
python examples/viseme_pipeline.py                  # Rocketbox, its own viseme shapes
python examples/viseme_pipeline.py --rig vrm-twist  # the VRM sample, through RCEF
```

The frames (`examples/data/viseme_talk_frames.csv`) say "bed car toe book", which are the example words of the META viseme specification. Each viseme is held for two frames and crossfaded into the next, so every frame sums to one.

- **Rocketbox** has a shape for each of the 15 META visemes, numbered in the same order (it spells IH, OH and OU as I, O and U), so the frames drive them directly by name.
- **VRM1_Constraint_Twist_Sample** (pixiv Inc., VRM Public License 1.0, redistribution and modification allowed, credit not required; vrm-specification commit `94e82dd`) has the five vowel presets. RCEF's `visemes.to_vrm` map translates the frames, and `examples/vrm_presets.py` turns presets into morph weights through the model's own binds, following the VRM 1.0 expression specification (values clamped to [0, 1], `isBinary`, binds accumulated). The same binds driven through the vowel pairs that `scripts/derive_fb2_goldens.py` reads from the pinned VRM and META texts (`tests/fixtures/fb2_goldens.json`) must give the same morph weights within 1e-9. Consonants have no VRM preset and are labelled as dropped. Overrides are not applied and are labelled if a frame would need one. After the talk come the two winks from the expression library. RCEF's `fb2.to_vrm` map turns FB2 `EYES_CLOSED_L` and `_R` into `blinkLeft` and `blinkRight`. This is checked in the same way, against the blink pairs read from the pinned OpenXR and VRM texts. `blink` (both eyes) is left unset, so a model that binds all three is not driven twice.

Outputs go to `~/.cache/rcef-examples/visemes/RIG`, in the same format as section 4.

To run the pipelines as tests (the slow tier, not part of the default suite; about ten minutes):

```sh
RCEF_SLOW_TESTS=1 RCEF_ICT_CACHE=~/.cache/rcef-ict-facekit RCEF_RIG_CACHE=~/.cache/rcef-face-rigs \
  python -B -m unittest tests/test_examples_slow.py
```

With `RCEF_SLOW_TESTS=1`, `tests/test_translations.py` also halves each translation mapping on its own and checks that only its output changes (about half a minute).

## 6. Rig gains: how strongly two rigs render the same ARKit name

Sections 4 and 5 assume that equal weights mean equal expressions. Between two example rigs, software can test that assumption. `examples/rig_gains.py` fits, for each ARKit shape that ICT-FaceKit and Rocketbox Female both have (51; ICT has no `tongueOut`), a monotone curve from an ICT weight to the Rocketbox Female weight that moves her face about as much, and evaluates it on an ICT identity it was not fitted to. It follows the calibration-record protocol in [calibration/README.md](../calibration/README.md); the record is `calibration/rig-gains.ict-rocketbox-female.cal`.

This calibrates how two example rigs render ARKit names. ICT-FaceKit is the reference by choice. It is not a measurement of any tracker, not a provider claim and not pack data. Rocketbox Male is never loaded, because it is kept back as an unseen rig for a later method.

```sh
swiftc -O -o /tmp/meshrender tools/render/meshrender.swift
python examples/rig_gains.py fit --ict-cache DIR --rig-cache DIR --renderer /tmp/meshrender --work /tmp/k3 --out fit.json
python examples/rig_gains.py evaluate --record calibration/rig-gains.ict-rocketbox-female.cal \
  --ict-cache DIR --rig-cache DIR --renderer /tmp/meshrender --work /tmp/k3 --out cells.json
python examples/rig_gains.py export --record calibration/rig-gains.ict-rocketbox-female.cal --out examples/data/rig_gains.json
```

The ICT cache needs ICT-FaceKit's 53 expression shapes and its first ten identity modes (`ict_facekit.CALIBRATION_FILES`, about 160 MB, fetched and checked on first use). The identity modes are principal components of light-stage scans of real people; they are used only as geometry.

**How motion is compared.** `examples/data/rig_landmarks.json` has 37 landmarks per rig: Multi-PIE 68 points on ICT, and counterparts on Rocketbox that were picked by hand or by a rule, each with its provenance. The landmarks are painted as small coloured markers on otherwise black meshes. `tools/render/meshrender` renders them unlit, from cameras with small random offsets, framed by each rig's own eye distance. A marker's position is its colour centroid in the image, so markers hidden by a lid or a lip drop out. For each ICT pose, the best Rocketbox weight is the one whose marker displacements are nearest to ICT's. The curve's knots at ICT weights 0.25, 0.5, 0.75 and 1 are the medians over 24 training conditions (8 ICT identities, 3 cameras), made non-decreasing. The module docstring gives every constant and failure rule.

**Results are per shape.** A shape passes if, on the held-out identity, the curve's error is within the record's bounds and the expected response is detected in every condition. A condition is a failure if Rocketbox at its best weight explains less than half of ICT's motion (the shapes move different regions or directions), or if Rocketbox cannot reach ICT's motion at weight 1. A monotone curve cannot fix either problem, so those shapes are published as failed, not forced to fit.

`examples/data/rig_gains.json` holds the curves of the shapes that passed and lists the others. `python examples/rigs.py --rig rocketbox-female --cache DIR --set mouthSmileLeft=0.6 --normalise --out pose` poses Rocketbox Female through it; without `--normalise` the weights are used as they are.

To reproduce the fit and the held-out cells for two shapes as a test (slow tier, about half a minute):

```sh
RCEF_SLOW_TESTS=1 RCEF_K3_ICT_CACHE=DIR RCEF_RIG_CACHE=DIR RCEF_RENDERER=/tmp/meshrender \
  python -B -m unittest tests/test_rig_gains.py
```

## 7. Visemes on faces without viseme shapes: the pose bridge

```sh
python examples/viseme_bridge.py                                       # "bed car toe book"
python examples/viseme_bridge.py --frames examples/data/viseme_demo_frames.csv
```

Route carries the META frames through the canonical viseme set, the [viseme pose bridge](../docs/canonical-set.md#viseme-pose-bridge) and the canonical expression set to ARKit weights (`bridge_arkit.csv`). The weights then pose Rocketbox Male_Adult_01 and ICT-FaceKit. ICT has no viseme shapes; the script reads all 53 of its expression shapes from the OBJ files in `~/.cache/rcef-ict-full` (`--ict-cache`), the cache of `tools/calibration/k4_mediapipe.py fetch`. Rocketbox Male's own viseme shapes, driven by the same frames by name, are the comparison. For each frame the script writes the meshes (bridged and direct for Male, with a difference colour map, and bridged for ICT) to `~/.cache/rcef-examples/viseme-bridge/mesh/`, and in `frames.json` the error `|bridged - direct| / |direct|` over Male's vertices except the tongue, as in the calibration record, and the RMS distance in millimetres.

On Rocketbox Male at full weight, the error is 0.22 to 0.48 for the classes the bridge reads, as in the calibration record (for `vowel_open` 0.29, an RMS distance of 4.0 mm over the vertices that move). Frames on `bilabial`, `vowel_mid_spread` or `vowel_close_rounded` (META PP, E and OU) give a neutral face, error 1, because those classes failed their bounds and the bridge does not read them; the route lists their values as dropped. On ICT the same ARKit weights give other geometry, often a much wider mouth: the weights are Rocketbox Female's units, and the two rigs render ARKit names differently (section 6).
