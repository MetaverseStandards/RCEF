# RCEF: expression inventory and authoring parity

RCEF records public expression interfaces, their calibration limits, and explicit directional scalar rules. TOML is the authoritative data. Names are inventoried as attributed facts; definitions and examples are original.

## Contents

Selected inventories: ARKit 52, MediaPipe 52, OpenXR FB 63 and FB2 70, optional META visemes 15, VRCFT transport 88, raw/combined eye data, artist 102+42, publicly listed numeric avatar parameters 124 and activity flags 3, Godot 102+41, VRM 18, and Roblox 50. Ancillary enums, sentinels and encoding surfaces remain visible. These counts describe interfaces, not tracking fidelity.

The canonical subset has 21 explicitly provider-calibrated scalar projections spanning blink, jaw, brow, directional gaze and physical pupil diameter. Executable identities preserve the stated provider basis. General calibration ambiguity is unresolved. Original affine and lossy bilateral fixtures demonstrate the shared runtime without claiming visual equivalence.

Data 0.2.0 adds the first 19 cross-provider rules: FB2 to ARKit (face and, separately, horizontal gaze) and META visemes to VRM lip-sync presets. All are proposed and approximate, compile only with the approximation opt-in, and state their calibration assumptions and losses; see the [CHANGELOG](CHANGELOG.md). Their tests compare against expectations that `scripts/derive_fb2_goldens.py` derives from the pinned public sources, not from RCEF's own rules.

## Expression sets and where they come from

The Mappings table shows what translates to what; the Expression sets table below shows where each set comes from. Each file in `profiles/` records one public expression set (or, for `fixture.toml`, RCEF's own synthetic fixtures). The documentation link is the normal web page for that set; the pinned source is the exact revision or retrieval RCEF verified, listed with its SHA-256 in [references.md](references.md) and [evidence/sources.toml](evidence/sources.toml). A **source** set is read by at least one executable mapping, a **target** set is written by one, and an **inventory only** set is recorded but not yet translated.

### Mappings

How to read this: each row is one group of rules that turns values from the source set into the target set. `verified_current` means the rule restates a verified source fact (provider-to-canonical copies and RCEF's synthetic fixtures); `proposed` means a source-backed but approximate cross-provider translation that compiles only with the approximation opt-in; `unresolved` means recorded but not executable. Every rule, with its assumptions, losses and evidence, is in [reports/mappings.md](reports/mappings.md).

| Mapping | Source set → target set | Rules | Evidence status |
|---|---|---|---|
| [`arkit.to_canonical`](reports/mappings.md#arkitto_canonical) | `arkit.coefficient` → `rcef.canonical` | 9 | verified_current |
| [`fb2.to_canonical`](reports/mappings.md#fb2to_canonical) | `openxr.fb2` → `rcef.canonical` | 8 | verified_current |
| [`vrcft_eye.to_canonical`](reports/mappings.md#vrcft_eyeto_canonical) | `vrcft.eye` → `rcef.canonical` | 4 | verified_current |
| [`fb2.to_arkit`](reports/mappings.md#fb2to_arkit) | `openxr.fb2` → `arkit.coefficient` | 44 | proposed |
| [`fb2_gaze.to_arkit`](reports/mappings.md#fb2_gazeto_arkit) | `openxr.fb2` → `arkit.coefficient` | 8 | proposed |
| [`arkit.to_fb2`](reports/mappings.md#arkitto_fb2) | `arkit.coefficient` → `openxr.fb2` | 52 | proposed |
| [`arkit_gaze.to_fb2`](reports/mappings.md#arkit_gazeto_fb2) | `arkit.coefficient` → `openxr.fb2` | 8 | proposed |
| [`visemes.to_vrm`](reports/mappings.md#visemesto_vrm) | `openxr.visemes` → `vrm.preset` | 5 | proposed |
| [`fixture.affine`](reports/mappings.md#fixtureaffine) | `fixture.source` → `fixture.target` | 1 | verified_current (synthetic) |
| [`fixture.bilateral`](reports/mappings.md#fixturebilateral) | `fixture.source` → `fixture.target` | 1 | verified_current (synthetic) |
| [`survey.ambiguous`](reports/mappings.md#surveyambiguous) | `mediapipe.label` → `rcef.canonical` | 1 | unresolved (not executable) |

### Expression sets

How to read this: start with the Role column. Source and target sets have executable rules; inventory-only sets are recorded but not yet translated.

| Profile file | Expression set and revision | Signals | Role in mappings | Documentation | Pinned source | License or terms |
|---|---|---|---|---|---|---|
| [`profiles/arkit.ancillary.toml`](profiles/arkit.ancillary.toml) | Apple ARKit `ARFaceAnchor.leftEyeTransform` and the `BlendShapeLocation` raw-value initializer (documentation retrieved 2026-10-26) | 2 | inventory only | [Apple: leftEyeTransform](https://developer.apple.com/documentation/arkit/arfaceanchor/lefteyetransform)¹ and [BlendShapeLocation](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation)¹ | [apple_blendshapes](references.md#apple_blendshapes), [apple_eye](references.md#apple_eye) | Reference only; Apple prose not redistributed |
| [`profiles/arkit.coefficient.toml`](profiles/arkit.coefficient.toml) | Apple ARKit `ARFaceAnchor.BlendShapeLocation`, 52 coefficients (documentation retrieved 2026-10-26) | 52 | source and target | [Apple: BlendShapeLocation](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation)¹ | [apple_blendshapes](references.md#apple_blendshapes) | Reference only; Apple prose not redistributed |
| [`profiles/fixture.toml`](profiles/fixture.toml) | RCEF original synthetic fixtures (profiles `fixture`, `fixture.source`, `fixture.target`) | 5 | source and target (synthetic) | [fixtures/mapping_samples.json](fixtures/mapping_samples.json) | [rcef_definitions](references.md#rcef_definitions) | CC-BY-SA-4.0 (original RCEF work) |
| [`profiles/godot.base.toml`](profiles/godot.base.toml) | Godot `XRFaceTracker` base blend shapes (`BlendShapeEntry`), Godot `e7b12e7` | 102 | inventory only | [Godot: XRFaceTracker](https://docs.godotengine.org/en/stable/classes/class_xrfacetracker.html) | [godot_enum](references.md#godot_enum), [godot_setters](references.md#godot_setters) | MIT |
| [`profiles/godot.blended.toml`](profiles/godot.blended.toml) | Godot `XRFaceTracker` blended blend shapes (`BlendShapeEntry`), Godot `e7b12e7` | 42 | inventory only | [Godot: XRFaceTracker](https://docs.godotengine.org/en/stable/classes/class_xrfacetracker.html) | [godot_enum](references.md#godot_enum), [godot_setters](references.md#godot_setters) | MIT |
| [`profiles/mediapipe.label.toml`](profiles/mediapipe.label.toml) | MediaPipe Face Landmarker blendshape labels (`kBlendshapeNames`), MediaPipe `f6988c4` | 53 | inventory only (its one rule is unresolved) | [Google: Face landmark detection guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) | [mediapipe](references.md#mediapipe) | Apache-2.0 upstream; names used as facts |
| [`profiles/openxr.ancillary.toml`](profiles/openxr.ancillary.toml) | OpenXR `XR_FB_face_tracking` and `XR_FB_face_tracking2` confidence, data-source and expression-set enums, OpenXR-Docs `5a82d45` | 10 | inventory only | [OpenXR: XR_FB_face_tracking2](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking2) | [xr_registry](references.md#xr_registry) | Apache-2.0 OR MIT (`xr.xml`); identifiers used as facts |
| [`profiles/openxr.fb.toml`](profiles/openxr.fb.toml) | OpenXR `XR_FB_face_tracking` (`XrFaceExpressionFB`), OpenXR-Docs `5a82d45` | 65 | inventory only | [OpenXR: XR_FB_face_tracking](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking) | [xr_fb](references.md#xr_fb), [xr_registry](references.md#xr_registry) | CC-BY-4.0 (extension text) |
| [`profiles/openxr.fb2.toml`](profiles/openxr.fb2.toml) | OpenXR `XR_FB_face_tracking2` (`XrFaceExpression2FB`), OpenXR-Docs `5a82d45` | 71 | source and target | [OpenXR: XR_FB_face_tracking2](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking2) | [xr_fb2](references.md#xr_fb2), [xr_registry](references.md#xr_registry) | CC-BY-4.0 (extension text) |
| [`profiles/openxr.visemes.toml`](profiles/openxr.visemes.toml) | META visemes: OpenXR `XR_META_face_tracking_visemes` (`XrFaceTrackingVisemeMETA`), OpenXR-Docs `5a82d45` | 15 | source | [OpenXR: XR_META_face_tracking_visemes](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_META_face_tracking_visemes) | [xr_registry](references.md#xr_registry), [xr_visemes](references.md#xr_visemes) | CC-BY-4.0 (extension text) |
| [`profiles/roblox.control.toml`](profiles/roblox.control.toml) | Roblox FACS `FaceControls` for dynamic heads, creator-docs `a0fce04` | 50 | inventory only | [Roblox: FaceControls](https://create.roblox.com/docs/reference/engine/classes/FaceControls)² and [FACS poses reference](https://create.roblox.com/docs/avatar/dynamic-heads/facs-poses-reference) | [roblox_authoring](references.md#roblox_authoring), [roblox_controls](references.md#roblox_controls), [roblox_poses](references.md#roblox_poses), [roblox_requirements](references.md#roblox_requirements) | CC-BY-4.0 |
| [`profiles/vrcft.artist.base.toml`](profiles/vrcft.artist.base.toml) | VRCFaceTracking Unified Expressions base shapes for avatar artists (documentation retrieved 2026-10-07) | 102 | inventory only | [VRCFT: Unified Expressions](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes) | [vrcft_artist](references.md#vrcft_artist) | Documentation, reference only |
| [`profiles/vrcft.artist.blended.toml`](profiles/vrcft.artist.blended.toml) | VRCFaceTracking Unified Expressions blended shapes for avatar artists (documentation retrieved 2026-10-07) | 42 | inventory only | [VRCFT: Unified Expressions](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes) | [vrcft_artist](references.md#vrcft_artist) | Documentation, reference only |
| [`profiles/vrcft.eye.toml`](profiles/vrcft.eye.toml) | VRCFaceTracking raw and combined eye data (`UnifiedData.cs`), VRCFaceTracking `6432e6a` | 20 | source | [GitHub: UnifiedData.cs at 6432e6a](https://github.com/benaclejames/VRCFaceTracking/blob/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Data/UnifiedData.cs) | [vrcft_data](references.md#vrcft_data) | Apache-2.0 |
| [`profiles/vrcft.parameter.encoding.toml`](profiles/vrcft.parameter.encoding.toml) | VRCFaceTracking binary avatar-parameter encoding (documentation retrieved 2026-10-07) | 7 | inventory only | [VRCFT: Binary parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/binary) | [vrcft_binary](references.md#vrcft_binary) | Documentation, reference only |
| [`profiles/vrcft.parameter.flags.toml`](profiles/vrcft.parameter.flags.toml) | VRCFaceTracking tracking-activity flags (documentation retrieved 2026-10-07) | 3 | inventory only | [VRCFT: Parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters) | [vrcft_float](references.md#vrcft_float), [vrcft_parameters](references.md#vrcft_parameters) | Documentation, reference only |
| [`profiles/vrcft.parameter.float.toml`](profiles/vrcft.parameter.float.toml) | VRCFaceTracking numeric avatar parameters (`v2/*`, documentation retrieved 2026-10-07) | 124 | inventory only | [VRCFT: Float parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/float) | [vrcft_float](references.md#vrcft_float), [vrcft_parameters](references.md#vrcft_parameters) | Documentation, reference only |
| [`profiles/vrcft.transport.toml`](profiles/vrcft.transport.toml) | VRCFaceTracking Unified Expressions transport enum (`UnifiedExpressions.cs`), VRCFaceTracking `6432e6a` | 89 | inventory only | [GitHub: UnifiedExpressions.cs at 6432e6a](https://github.com/benaclejames/VRCFaceTracking/blob/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedExpressions.cs) | [vrcft_data](references.md#vrcft_data), [vrcft_enum](references.md#vrcft_enum) | Apache-2.0 |
| [`profiles/vrm.preset.toml`](profiles/vrm.preset.toml) | VRM 1.0 expression presets (`VRMC_vrm` expressions and lookAt), vrm-specification `94e82dd` | 18 | target | [GitHub: VRM 1.0 expressions.md at 94e82dd](https://github.com/vrm-c/vrm-specification/blob/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/expressions.md) | [vrm_expressions](references.md#vrm_expressions), [vrm_lookat](references.md#vrm_lookat) | Reference only; redistribution of specification prose unresolved |

The Signals column counts every inventory row, including count sentinels and rows recorded as absent, so it can be higher than the counts in Contents above: FB2 has 70 weights plus `COUNT` (71), FB has 63 plus `COUNT` and an absent tongue row (65), the VRCFT transport enum has 88 plus `Max` (89), and MediaPipe has its 52 labels plus an absent `tongueOut` row (53).

RCEF's own canonical set, `rcef.canonical` (21 signals), is in [data/canonical.toml](data/canonical.toml); it is the target of the three `*.to_canonical` mappings.

¹ Apple's documentation pages build their content with JavaScript; without it the page is an empty shell. The pinned source is Apple's JSON data for the same page.

² create.roblox.com answered scripted checks with HTTP 502 on 2026-10-26, though it may work in a browser. The same reference is in the Roblox creator-docs repository as [FaceControls.yaml at a0fce04](https://github.com/Roblox/creator-docs/blob/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/reference/engine/classes/FaceControls.yaml).

## Generate and check

Python 3.11+ and the separately maintained `msf-tools` package are required. Install msf-tools at the commit recorded as `git_commit` in [tooling.lock.json](evidence/tooling.lock.json), from GitHub or from a local checkout, into the Python you use for RCEF:

```sh
python3 -m pip install "git+https://github.com/Kjakubzak/msf-tools@COMMIT"
# or: python3 -m pip install "git+file://$(cd ../msf-tools && pwd -P)@COMMIT"
```

Then regenerate the outputs:

```sh
python3 -B check.py --write
```

Review the generated diffs, then check existing outputs without writing and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

Run these commands from the RCEF checkout.

The 21 provider identities and 63 scalar comparisons preserve declared storage and provider-specific assumptions. FB2 direction tests activate one direction at a time. Raw pupil fields and native defaults do not establish physical measurement, calibrated neutral or cross-provider equivalence. Provider frame context and device/capture/physiology remain separate gates.

`check.py` uses the installed package. The lock records its commit, version and a SHA-256 for every installed package file. Before doing anything else, `check.py` verifies that the installed package was built from the locked commit (from its `direct_url.json`) and that every package file matches both its `RECORD` entry and the lock; on any difference it lists the problems and exits non-zero. The lock's `source` URL is informational: the commit and file hashes identify the package, so local `file://` installs are accepted. To adopt a reviewed new msf-tools version, install it and run `python3 -B check.py --update-lock`; the old lock is kept as [tooling.lock.previous.json](evidence/tooling.lock.previous.json). To roll back, copy that file over `tooling.lock.json` and install msf-tools at its commit. The wrapper delegates to `python3 -B -m msf_tools check AUTHORING --pack PATH --csv PATH [--write]`. No automatic cloning or source download occurs during checking.

Outputs are `generated/rcef.pack.json`, `rcef_mapping.csv`, `coverage.json`, and `SHA256SUMS`. JSON uses the shared sorted-key, indented stdlib encoding with UTF-8 and final LF, finite numbers and normalized negative zero. Arrays retain authoring order. CSV uses UTF-8, LF and minimal standard CSV quoting. All bytes are rendered and validated before each file is atomically replaced; several replacements are not one transaction.

## Examples

[examples/README.md](examples/README.md) walks through RCEF end to end with the msf-tools public API. It translates FB2 frames to ARKit weights and META visemes to VRM presets from CSV. It then drives two Microsoft Rocketbox faces and the ICT-FaceKit face with a FACS-based expression library, both directly and through RCEF's rules, and reports the residuals. It also renders a short spoken phrase as visemes on Rocketbox and on a VRM model.

## Architecture and TOML guide

See the [visual architecture report](docs/architecture.html), [Markdown guide](docs/architecture.md), [standalone diagram](docs/architecture.svg), and [TOML file index](docs/toml-index.csv). The guide explains discovery, validation, in-memory mapping, generated reports, and worked rule examples.

## Readable inventories and mappings

The checker also generates and checks [readable reports](reports/inventory.md):

- [Inventory Markdown](reports/inventory.md) and [CSV](reports/inventory.csv): every signal and profile membership, including excluded, unsupported and unresolved records. Native names, indices, ranges, calibration, evidence and reasons stay visible. Native defaults and calibrated neutral values remain separate.
- [Mapping Markdown](reports/mappings.md) and [CSV](reports/mappings.csv): every authored directional rule with its operator, status, assumptions and loss annotations.
- [Canonical correspondence Markdown](reports/canonical_correspondence.md) and [CSV](reports/canonical_correspondence.csv): a comparison table using authored rules only. A dash means no authored rule; unresolved relationships remain labeled. These tables do not establish cross-provider or anatomical equivalence.

These reports are derived from `generated/rcef.pack.json`; edit the authoritative TOML and run `check.py --write` to update them. `check.py` checks both shared outputs and readable reports. To check or regenerate only the presentation files with Python's standard library, use `python3 -B scripts/export_reports.py` or add `--write`. Each Markdown report binds the consumed pack bytes by SHA-256, and `reports/SHA256SUMS` binds all six presentation files. Existing `generated/SHA256SUMS` and generated mapping bytes retain their original contract. Publication uses atomic replacement per file and is not a transaction across all files. Report generation adds no third-party dependency; data and documentation retain their existing CC BY-SA 4.0 license and attribution.

See [survey](survey.md), [proposal](proposal.md), [references](references.md), [source evidence](evidence/sources.toml), [review](REVIEW.md), and [notices](THIRD_PARTY_NOTICES.md). `scripts/verify_sources.py` optionally checks exact public source digests and saves source bytes only to an explicit cache outside this repository. `scripts/audit_inventories.py --cache CACHE` then compares exact selected names, order and genuine enum indices against those verified bytes.

Read [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md) before extending or releasing the inventory.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Inherited source licenses and provenance are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Referenced provider documentation is not relicensed by RCEF.
