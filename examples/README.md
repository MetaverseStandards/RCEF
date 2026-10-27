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
python -B check.py
```

`check.py` refuses to run unless the installed msf-tools is exactly the locked commit, so a passing check also confirms the install. The examples need nothing else; they use only the Python standard library and msf-tools.

## 2. Translate FB2 frames to ARKit

```sh
python examples/translate_fb2_to_arkit.py examples/data/fb2_demo_frames.csv fb2_to_arkit.csv
```

The input has one row per frame: `time`, a `segment` label, all 70 FB2 weights, and FB2's two validity flags, `isValid` and `isEyeFollowingBlendshapesValid`. The output has the 14 ARKit weights that RCEF's rules produce, plus two columns:

- `refused`: which mapping refused the frame and why. For example, when eye following is lost, `fb2_gaze.to_arkit` is refused while the face weights still come through.
- `dropped`: non-zero inputs that no RCEF rule reads, such as `TONGUE_OUT`.

The demo frames come from `examples/make_demo_frames.py`. They cover a neutral pose, a jaw sweep, gaze left and right, asymmetric brows and cheeks, lost eye following during a blink, a lost face, and a tongue with no rule.

How it works (see `examples/rcef_translate.py`):

- It loads `generated/rcef.pack.json` and compiles `fb2.to_arkit` and `fb2_gaze.to_arkit` with the approximation opt-in, because RCEF's cross-provider rules are proposed approximations.
- Each mapping gets only its own `required_inputs`. msf-tools refuses a frame if any channel it is given is marked invalid, even one the mapping does not use. If each mapping were given the whole FB2 frame, invalid gaze would also stop the face.
- Each input's validity is the AND of the provider flags its signal record names, for example `isValid AND isEyeFollowingBlendshapesValid` for gaze.

## 3. Translate META visemes to VRM

```sh
python examples/translate_visemes_to_vrm.py examples/data/viseme_demo_frames.csv visemes_to_vrm.csv
```

The five vowel visemes become VRM `aa`, `ih`, `ou`, `ee` and `oh`. Consonant visemes have no VRM preset, so they appear in `dropped`. This is a phoneme-label correspondence; no published table maps META visemes to VRM.

## 4. Drive a face mesh and compare

```sh
python examples/face_pipeline.py --cache ~/.cache/rcef-ict-facekit --out out/face
```

This takes about a minute.

1. It downloads 17 files from ICT-FaceKit Light (MIT, USC Institute for Creative Technologies, commit `da5f95a`) into the cache and checks their SHA-256 values. The meshes are not stored in this repository.
2. It converts the neutral head and the 16 ARKit-named shapes RCEF's rules can drive into one GLB with morph targets: triangulated quads, and each target is the shape minus the neutral. All 53 shapes would need about 4.3 million position components, more than msf-tools' 4 million budget, and sparse accessors don't help because msf-tools counts them at full size.
3. It writes an msf-tools sidecar binding each shape to its ARKit signal. ICT splits `browInnerUp` and `cheekPuff` into left and right halves, and both halves are bound to the one ARKit coefficient.
4. For each frame it evaluates the mesh twice with `msf_tools.evaluate_geometry(morph_weights=...)`:
   - **direct**: the FB2 values routed to the shapes as the Godot and VRCFT sources route them (`tests/fixtures/godot_fb2_rules.csv`), with each brow and cheek half taking its own FB2 side;
   - **translated**: RCEF's translated ARKit weights.

Outputs in `out/face/`:

| File | Contents |
|---|---|
| `fb2_to_arkit.csv` | the translated weights, refusals and dropped channels |
| `ict_facekit_subset.glb`, `ict_facekit_subset.sidecar.json` | the converted mesh and its bindings |
| `mesh/indices.u32` | triangle indices, little-endian uint32 |
| `mesh/direct/NNNN.f32`, `mesh/translated/NNNN.f32` | vertex positions per frame, little-endian float32 xyz |
| `mesh/difference/NNNN.f32` | per-vertex difference colours, float32 RGB (blue = none, red = `heat_scale` or more) |
| `frames.json` | every frame's time, segment, files, labels, largest vertex difference and oracle result |
| `residuals.csv`, `residuals.md` | the residual report, per frame and per channel |

The position, index and colour files are in the format of the offscreen renderer used for the msf-tools geometry video, so the frames can be rendered side by side: direct, translated and difference.

The report checks four things:

- Exact rules have residual ≤ 1e-9.
- Each half of an averaged pair is within |L − R| / 2 of its own side.
- The largest vertex difference stays within the sum of each residual times that shape's largest vertex move.
- Refused and dropped channels are labelled on their frame and never shown as a silent zero.

The pipeline exits non-zero if any oracle fails.

**What this shows and what it doesn't.** It shows that RCEF's rules connect names and meanings the way the public sources do, on one rig. It is not a calibration result: neither provider publishes its gain, so equal weights are assumed to mean equal expressions.

To run the pipeline as a test (the slow tier, not part of the default suite):

```sh
RCEF_SLOW_TESTS=1 RCEF_ICT_CACHE=~/.cache/rcef-ict-facekit python -B -m unittest tests/test_examples_slow.py
```
