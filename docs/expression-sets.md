<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Expression sets

Each file in [profiles/](../profiles) records one public expression set, except `fixture.toml`, which holds RCEF's own synthetic fixtures. This page lists every profile file and where its set comes from. The README's [Mappings](../README.md#mappings) table shows what translates to what.

- Documentation: the usual web page for the set.
- Pinned source: the exact revision or retrieval that RCEF verified. [references.md](../references.md) and [evidence/sources.toml](../evidence/sources.toml) list it with its SHA-256.
- Role in maps: at least one executable mapping reads a "source" set, and at least one writes a "target" set. An "inventory only" set is recorded but not translated yet.

`tests/test_readme_sources.py` checks this table against the profile files, the evidence records and the pack. Edit it by hand when a profile file changes.

## Where each set comes from

| Profile file | Expression set and revision | Signals | Role in maps | Documentation | Pinned source | License or terms |
|---|---|---|---|---|---|---|
| [`profiles/arkit.ancillary.toml`](../profiles/arkit.ancillary.toml) | Apple ARKit `ARFaceAnchor.leftEyeTransform` and the `BlendShapeLocation` raw-value initializer (documentation retrieved 2026-10-26) | 2 | inventory only | [Apple: leftEyeTransform](https://developer.apple.com/documentation/arkit/arfaceanchor/lefteyetransform)¹ and [BlendShapeLocation](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation)¹ | [apple_blendshapes](../references.md#apple_blendshapes), [apple_eye](../references.md#apple_eye) | Reference only; Apple prose not redistributed |
| [`profiles/arkit.coefficient.toml`](../profiles/arkit.coefficient.toml) | Apple ARKit `ARFaceAnchor.BlendShapeLocation`, 52 coefficients (documentation retrieved 2026-10-26) | 52 | source and target | [Apple: BlendShapeLocation](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation)¹ | [apple_blendshapes](../references.md#apple_blendshapes) | Reference only; Apple prose not redistributed |
| [`profiles/facs.code.toml`](../profiles/facs.code.toml) | FACS code numbers and names from a public list (Wikipedia, "Facial Action Coding System", revision 1357638399), split by side where the canonical signal is. `facs.code` names the code numbers; its numeric encoding is RCEF's own and is not a FACS interface, and its values are not FACS scores | 92 | source and target | [Wikipedia: Facial Action Coding System](https://en.wikipedia.org/wiki/Facial_Action_Coding_System) and [facs-intensity.md](../docs/facs-intensity.md) | [facs_wikipedia](../references.md#facs_wikipedia), [rocketbox_avatars](../references.md#rocketbox_avatars), [facs_hager_2002](../references.md#facs_hager_2002) | CC-BY-SA-4.0 (code numbers and names as facts; no FACS manual used) |
| [`profiles/fixture.toml`](../profiles/fixture.toml) | RCEF original synthetic fixtures (profiles `fixture`, `fixture.source`, `fixture.target`) | 5 | source and target (synthetic) | [fixtures/mapping_samples.json](../fixtures/mapping_samples.json) | [rcef_definitions](../references.md#rcef_definitions) | CC-BY-SA-4.0 (original RCEF work) |
| [`profiles/godot.base.toml`](../profiles/godot.base.toml) | Godot `XRFaceTracker` base blend shapes (`BlendShapeEntry`), Godot `e7b12e7` | 102 | inventory only | [Godot: XRFaceTracker](https://docs.godotengine.org/en/stable/classes/class_xrfacetracker.html) | [godot_enum](../references.md#godot_enum), [godot_setters](../references.md#godot_setters) | MIT |
| [`profiles/godot.blended.toml`](../profiles/godot.blended.toml) | Godot `XRFaceTracker` blended blend shapes (`BlendShapeEntry`), Godot `e7b12e7` | 42 | inventory only | [Godot: XRFaceTracker](https://docs.godotengine.org/en/stable/classes/class_xrfacetracker.html) | [godot_enum](../references.md#godot_enum), [godot_setters](../references.md#godot_setters) | MIT |
| [`profiles/mediapipe.label.toml`](../profiles/mediapipe.label.toml) | MediaPipe Face Landmarker blendshape labels (`kBlendshapeNames`), MediaPipe `f6988c4` | 53 | inventory only (its one mapping is unresolved) | [Google: Face landmark detection guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) | [mediapipe](../references.md#mediapipe) | Apache-2.0 upstream; names used as facts |
| [`profiles/mediapipe.score.toml`](../profiles/mediapipe.score.toml) | MediaPipe Face Landmarker blendshape scores as numbers in [0, 1] (the same 52 outputs, MediaPipe `f6988c4`), for calibration against renders | 52 | inventory only | [Google: Face landmark detection guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) | [mediapipe](../references.md#mediapipe), [mediapipe_blendshape_card](../references.md#mediapipe_blendshape_card) | Apache-2.0 upstream; names used as facts |
| [`profiles/openxr.ancillary.toml`](../profiles/openxr.ancillary.toml) | OpenXR `XR_FB_face_tracking` and `XR_FB_face_tracking2` confidence, data-source and expression-set enums, OpenXR-Docs `5a82d45` | 10 | inventory only | [OpenXR: XR_FB_face_tracking2](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking2) | [xr_registry](../references.md#xr_registry) | Apache-2.0 OR MIT (`xr.xml`); identifiers used as facts |
| [`profiles/openxr.fb.toml`](../profiles/openxr.fb.toml) | OpenXR `XR_FB_face_tracking` (`XrFaceExpressionFB`), OpenXR-Docs `5a82d45` | 65 | inventory only | [OpenXR: XR_FB_face_tracking](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking) | [xr_fb](../references.md#xr_fb), [xr_registry](../references.md#xr_registry) | CC-BY-4.0 (extension text) |
| [`profiles/openxr.fb2.toml`](../profiles/openxr.fb2.toml) | OpenXR `XR_FB_face_tracking2` (`XrFaceExpression2FB`), OpenXR-Docs `5a82d45` | 71 | source and target | [OpenXR: XR_FB_face_tracking2](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_FB_face_tracking2) | [xr_fb2](../references.md#xr_fb2), [xr_registry](../references.md#xr_registry) | CC-BY-4.0 (extension text) |
| [`profiles/openxr.visemes.toml`](../profiles/openxr.visemes.toml) | META visemes: OpenXR `XR_META_face_tracking_visemes` (`XrFaceTrackingVisemeMETA`), OpenXR-Docs `5a82d45` | 15 | source and target | [OpenXR: XR_META_face_tracking_visemes](https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.html#XR_META_face_tracking_visemes) | [xr_registry](../references.md#xr_registry), [xr_visemes](../references.md#xr_visemes) | CC-BY-4.0 (extension text) |
| [`profiles/roblox.control.toml`](../profiles/roblox.control.toml) | Roblox FACS `FaceControls` for dynamic heads, creator-docs `a0fce04` | 50 | inventory only | [Roblox: FaceControls](https://create.roblox.com/docs/reference/engine/classes/FaceControls)² and [FACS poses reference](https://create.roblox.com/docs/avatar/dynamic-heads/facs-poses-reference) | [roblox_authoring](../references.md#roblox_authoring), [roblox_controls](../references.md#roblox_controls), [roblox_poses](../references.md#roblox_poses), [roblox_requirements](../references.md#roblox_requirements) | CC-BY-4.0 |
| [`profiles/vrcft.artist.base.toml`](../profiles/vrcft.artist.base.toml) | VRCFaceTracking Unified Expressions base shapes for avatar artists (documentation retrieved 2026-10-07) | 102 | target | [VRCFT: Unified Expressions](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes) | [vrcft_artist](../references.md#vrcft_artist) | Documentation, reference only |
| [`profiles/vrcft.artist.blended.toml`](../profiles/vrcft.artist.blended.toml) | VRCFaceTracking Unified Expressions blended shapes for avatar artists (documentation retrieved 2026-10-07) | 42 | inventory only | [VRCFT: Unified Expressions](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes) | [vrcft_artist](../references.md#vrcft_artist) | Documentation, reference only |
| [`profiles/vrcft.eye.toml`](../profiles/vrcft.eye.toml) | VRCFaceTracking raw and combined eye data (`UnifiedData.cs`), VRCFaceTracking `6432e6a` | 20 | source and target | [GitHub: UnifiedData.cs at 6432e6a](https://github.com/benaclejames/VRCFaceTracking/blob/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Data/UnifiedData.cs) | [vrcft_data](../references.md#vrcft_data) | Apache-2.0 |
| [`profiles/vrcft.parameter.encoding.toml`](../profiles/vrcft.parameter.encoding.toml) | VRCFaceTracking binary avatar-parameter encoding (documentation retrieved 2026-10-07) | 7 | inventory only | [VRCFT: Binary parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/binary) | [vrcft_binary](../references.md#vrcft_binary) | Documentation, reference only |
| [`profiles/vrcft.parameter.flags.toml`](../profiles/vrcft.parameter.flags.toml) | VRCFaceTracking tracking-activity flags (documentation retrieved 2026-10-07) | 3 | inventory only | [VRCFT: Parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters) | [vrcft_float](../references.md#vrcft_float), [vrcft_parameters](../references.md#vrcft_parameters) | Documentation, reference only |
| [`profiles/vrcft.parameter.float.toml`](../profiles/vrcft.parameter.float.toml) | VRCFaceTracking numeric avatar parameters (`v2/*`, documentation retrieved 2026-10-07) | 124 | inventory only | [VRCFT: Float parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/float) | [vrcft_float](../references.md#vrcft_float), [vrcft_parameters](../references.md#vrcft_parameters) | Documentation, reference only |
| [`profiles/vrcft.transport.toml`](../profiles/vrcft.transport.toml) | VRCFaceTracking Unified Expressions transport enum (`UnifiedExpressions.cs`), VRCFaceTracking `6432e6a` | 89 | inventory only | [GitHub: UnifiedExpressions.cs at 6432e6a](https://github.com/benaclejames/VRCFaceTracking/blob/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedExpressions.cs) | [vrcft_data](../references.md#vrcft_data), [vrcft_enum](../references.md#vrcft_enum) | Apache-2.0 |
| [`profiles/vrm.preset.toml`](../profiles/vrm.preset.toml) | VRM 1.0 expression presets (`VRMC_vrm` expressions and lookAt), vrm-specification `94e82dd` | 18 | source and target | [GitHub: VRM 1.0 expressions.md at 94e82dd](https://github.com/vrm-c/vrm-specification/blob/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/expressions.md) | [vrm_expressions](../references.md#vrm_expressions), [vrm_lookat](../references.md#vrm_lookat) | Reference only; redistribution of specification prose unresolved |

¹ Apple's documentation pages build their content with JavaScript. Without JavaScript the page is empty. The pinned source is Apple's JSON data for the same page.

² On 2026-10-26, create.roblox.com returned HTTP 502 to scripted checks. It may still work in a browser. The same reference is in the Roblox creator-docs repository as [FaceControls.yaml at a0fce04](https://github.com/Roblox/creator-docs/blob/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/reference/engine/classes/FaceControls.yaml).

## Signal counts

The Signals column counts every inventory row, including count sentinels and rows recorded as absent. So it can be higher than the selected-interface counts in the README section [What RCEF covers](../README.md#what-rcef-covers). FB2 has 70 weights plus `COUNT` (71). FB has 63 plus `COUNT` and an absent tongue row (65). The VRCFT transport enum has 88 plus `Max` (89). MediaPipe has its 52 labels plus an absent `tongueOut` row (53). Godot blended has 41 shapes plus the `FT_MAX` sentinel (42).

## RCEF's own sets

The draft canonical expression set, `rcef.canonical_expression` (72 signals), is in [data/canonical_expression.toml](../data/canonical_expression.toml). [canonical-set.md](canonical-set.md) defines it. ARKit, FB2, FACS codes (`facs.code`), VRCFaceTracking eye data and VRM blinks map into it. It maps to ARKit, FB2, Unified Expressions, VRCFaceTracking eye data, VRM blinks and FACS codes. The draft canonical viseme set, `rcef.canonical_viseme` (16 signals: 15 IPA shape classes and the aggregate `alveolar_floor`), is in [data/canonical_viseme.toml](../data/canonical_viseme.toml), and [canonical-set.md](canonical-set.md#visemes) defines it too. META visemes and the VRM vowel presets map into it and out of it. The README's [Mappings](../README.md#mappings) tables list these maps. RCEF's intermediate values, `rcef.intermediate` (61 signals), are in [data/intermediate.toml](../data/intermediate.toml). 4 are the signed difference of two opposing gaze directions of the canonical expression set, which `rcef_expression.to_fb2` computes. The 5th is the sum of META's SS, DD, NN and RR before the clamp, which the aggregate part of `visemes.to_rcef_viseme` computes. The other 56 belong to the [viseme pose bridge](canonical-set.md#viseme-pose-bridge), `rcef_viseme.to_rcef_expression`. Each passing viseme class gives the activation of its pose, and each expression signal has a sum of poses before the clamp. Each map computes them internally, and no provider reads or writes them.

## The canonical sets in data 0.5.0

This section gives the details of the two canonical sets and their maps. The README section [What RCEF covers](../README.md#what-rcef-covers) gives the totals, and its [Mappings](../README.md#mappings) tables list each map.

### The canonical expression set

The canonical expression set, `rcef.canonical_expression`, is a draft. It has 72 signals in 13 groups:

| Group | Signals | Group | Signals |
|---|---:|---|---:|
| `face` | 41 | `gaze` | 8 |
| `cheek_puff` | 2 | `tongue_out` | 1 |
| `jaw_thrust` | 1 | `cheek_suck` | 2 |
| `jaw_sideways` | 2 | `lip_tighten` | 2 |
| `mouth_shift` | 2 | `tongue_place` | 6 |
| `chin_raise_upper_lip` | 1 | `pupil_mm` | 2 |
| `blink` | 2 | | |

[canonical-set.md](canonical-set.md) defines each signal, and the [definitions audit](canonical-set-audit.md) compares it with each source. 442 mappings in 11 maps go into and out of it:

- ARKit, FB2, FACS codes, VRCFaceTracking eye data and VRM per-eye blinks go into the canonical expression set: 189 mappings in 5 maps.
- The canonical expression set goes to ARKit, FB2, VRCFaceTracking Unified Expressions, VRCFaceTracking eye data, VRM per-eye blinks and FACS codes: 253 mappings in 6 maps. The gaze part of the FB2 out-map has 4 internal steps.

Each expression set has at most one map in each direction, and each map has one part per group that it fills.

VRCFaceTracking eye data fills two groups. In `blink`, `eye_close` is 1 − `Openness`. The map refuses an `Openness` outside 0 to 1. VRCFaceTracking does not say that 1 is a relaxed open eye. In `pupil_mm`, the maps copy the pupil diameters in millimetres exactly. These 4 mappings and the 2 canonical pupil signals are `verified_current`.

VRM fills `blink` from `blinkLeft` and `blinkRight`. RCEF does not read VRM `blink`, which closes both eyes. A route lists a non-zero `blink` as dropped.

The FACS codes are a separate expression set, `facs.code`. It is a draft. It has 92 rows for 70 code numbers from a public list (record `facs_wikipedia`). If the canonical signal has sides, RCEF gives the code one row for each side. 49 rows are mapped, 25 are `unresolved` and 18 are `excluded`. Their values are RCEF's own numeric encoding of the FACS intensity letters. They are not FACS scores, and RCEF does not code faces. [facs-intensity.md](facs-intensity.md) gives the letter codec, and `examples/facs_codec.py` implements it.

FACS fills 8 of the 13 groups. It has no code for mouth shift, the upper-lip part of chin raise, gaze, the tongue places or the pupils.

### The canonical viseme set

The canonical viseme set, `rcef.canonical_viseme`, is a draft with 16 signals. 15 are partition classes: vowel 5, consonant 9 and rest 1. 14 of them are mouth-shape classes that together contain every symbol of the IPA chart. The rest class is `sil`. From a valid META frame, their values sum to 1. The 16th signal, `alveolar_floor`, is the sum of the three alveolar classes and `rhotic`, clamped at 1. It is the class that joins them in the IPA strict floor.

42 mappings in 4 maps go into and out of it:

- META visemes and the VRM vowel presets go into the canonical viseme set: 22 mappings in 2 maps. The part that writes `alveolar_floor` has 1 internal step.
- The canonical viseme set goes to META visemes and the VRM vowel presets: 20 mappings in 2 maps.

`visemes.to_rcef_viseme` writes `alveolar_floor` through one helper value. No map reads `alveolar_floor`.

### Evidence status of the canonical maps

On the pairs that the retired direct maps translated, the composed route gives the same weights as they did. `tests/test_pivot_structure.py` compares it with the frozen baseline. The registered A/B comparison checks this on every frame ([ab/README.md](../ab/README.md)). Of the 484 mappings in the 15 maps of the two canonical sets, all but the 4 pupil copies are proposed and approximate. The pupil copies are exact and `verified_current`. `scripts/build_canonical.py` writes both canonical profiles, the `facs.code` profile and these maps from [canonical-set.md](canonical-set.md) and its definitions audit.

Data 0.5.0 downgrades 19 mappings. The 21 retired identity mappings into `rcef.canonical` were exact and `verified_current`. Their signals now go through the hops of the canonical expression set. These hops are proposed and approximate, because each canonical signal has RCEF's own declared meaning. Only the 2 pupil diameters keep an exact, `verified_current` copy.

### The viseme pose bridge

The viseme pose bridge, `rcef_viseme.to_rcef_expression`, joins the two canonical sets. It has 101 proposed mappings in 1 map, with 56 helper values in `rcef.intermediate`. It writes canonical expression values from 11 viseme classes. These classes pass the shape gate or the perceptual gate on all 4 held-out rigs in the calibration record `viseme-poses.rocketbox-features`. `scripts/build_canonical.py` writes it from the record.

The bridge goes from the canonical viseme set to the canonical expression set. It writes the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`. Each of these signals is the sum of each class weight times the class's pose, clamped at 1.

The poses come from the calibration record [`viseme-poses.rocketbox-features`](../calibration/README.md). The record measures the viseme shapes of 18 Rocketbox rigs in their own ARKit shapes, with Left and Right tied. It keeps 4 other rigs for the held-out test. A class passes by its whole-face shape or by a perceptual gate of visible mouth features.

The bridge reads only the 11 classes that pass on every held-out rig. One of them is `bilabial` (p, b and m). Its pose keeps the lips closed and moves them backward, like the rigs' own shapes. `labiodental`, `postalveolar`, `coronal_nasal_lateral` and `rhotic` fail and move nothing. So META visemes and VRM vowels can drive ARKit, FB2 and Unified Expressions faces, and FACS values. [canonical-set.md](canonical-set.md#viseme-pose-bridge) gives the limits.

### Retired direct maps

Data 0.5.0 retires the direct maps of earlier data versions. It retires the 187 direct cross-provider mappings and their 4 internal gaze steps. These maps went from FB2 to ARKit and back, and from ARKit to VRCFaceTracking Unified Expressions. Other retired maps went from FB2 to VRM blinks and from META visemes to VRM. It also retires the old 21-signal canonical set `rcef.canonical` and the 21 identity mappings into it.

Every translation now runs through the canonical sets. [retired-ids.csv](retired-ids.csv) lists every retired ID. The A/B comparison keeps the direct maps in its frozen baseline, `tests/fixtures/baseline-dea1713.pack.json` ([ab/README.md](../ab/README.md)).

### Synthetic fixtures

Two original fixtures, one affine and one lossy bilateral, show the shared runtime. They do not claim visual equivalence. [The architecture guide](architecture.md#5-examples-of-each-operator) shows how they work.

## Planned expression sets

This section is a plan, not data. It goes with the draft [canonical expression set](canonical-set.md), through which every translation is to run. Phase 1 is data 0.5.0, the first release of the draft canonical sets. Its sources are ARKit, FB2, META visemes, VRM (blinks and vowels), VRCFaceTracking eye data and FACS codes (`facs.code`); Unified Expressions is a target only. The README's [Routes](../README.md#routes) table lists its 37 routes. The meaning of the canonical signals still needs review by the working group: until then, both canonical sets have `vocabulary_status = "draft"`.

### Rule for every new set

A set joins only with a pinned public source and a known licence. It gets a profile, evidence records, rows in the [definitions audit](canonical-set-audit.md), and in-maps or out-maps. It also gets a row in the test that checks which canonical groups each set can fill. A new copyright holder of CC-BY-4.0 text gets a row in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). A product name in a profile ID gets a trademark check. New sets join after data 0.5.0, so they do not change the frozen A/B comparison ([ab/README.md](../ab/README.md)). Their routes have no direct map to compare with, so each is labelled "no external reference" unless a public route exists.

### How the list was made

It has RCEF's own profiles and other sets that the authors knew of. It also has every face, facial, lip and eye-expression weight enum in the OpenXR registry at `5a82d45` (`xr_registry`). So it is complete for OpenXR at that commit. It is not a complete list of public sets.

### Sets that already have a profile

| Set | Public source | Licence or terms | Signals | Phase | Notes |
|---|---|---|---:|---|---|
| OpenXR `XR_FB_face_tracking` (FB v1) | `xr_fb`, `xr_registry` at `5a82d45` | CC-BY-4.0 extension text; `xr.xml` Apache-2.0 OR MIT | 63 | 1b | 63 copies, in one in-map with one part per group |
| VRCFaceTracking Unified Expressions: in-maps, transport and part shapes | `vrcft_*` records, VRCFaceTracking `6432e6a` | Apache-2.0 code; documentation reference only | 88 transport; 102 base and 42 blended artist shapes | out-maps: in data 0.5.0; in-maps 2 | the parts need new IDs and blended weights |
| Godot `XRFaceTracker` | `godot_enum` at `e7b12e7` | MIT | 102 base and 41 blended | out-maps 2; in-maps 3 | the names follow Unified Expressions (`godot_enum` lines 38-40) |
| MediaPipe | `mediapipe` at `f6988c4` | Apache-2.0 | 52 | 2, if the project decides to map it | a passing calibration record becomes part of an in-map ([calibration/README.md](../calibration/README.md#mappings-that-cite-a-record)) |
| Roblox `FaceControls` | `roblox_*` records at `a0fce04` | CC-BY-4.0 | 50, all `unresolved` today | 3 | joint poses with FACS-style names but no code numbers; side convention not checked |
| VRM emotions and `look*` presets | `vrm_*` records | reference only | not counted | not planned | out of scope ([README](../README.md#out-of-scope)) |

### New public sets

| Set | Public source | Licence or terms | Signals | Phase | Notes |
|---|---|---|---:|---|---|
| OpenXR `XR_ANDROID_face_tracking` | `xr_registry`: `xr.xml` lines 8629-8698, extension line 20744; extension text in OpenXR-Docs at `5a82d45` | CC-BY-4.0 extension text; `xr.xml` Apache-2.0 OR MIT | 68: 64 with FB2 names, plus 4 tongue directions | 1b | 64 copies; the 4 tongue directions are not mapped |
| OpenXR `XR_ML_facial_expression` | `xr.xml` lines 8948-8996, extension line 21105 | CC-BY-4.0 extension text | 46: 45 with FB2 names, plus CHIN_RAISER | 1b | CHIN_RAISER → `chin_raise`; `chin_raise_upper_lip` is not available, as for FACS 17. It can fill the `face` group because cheek puff, jaw thrust and jaw sideways have groups of their own |
| OpenXR `XR_BD_facial_simulation` | `xr.xml` lines 9485-9561, extension line 19731 | CC-BY-4.0 extension text | 72: 52 face shapes and 20 lip classes | 2 | the lip classes differ from META's 15 and need their own audit against the IPA shape classes |
| OpenXR `XR_HTC_facial_tracking` | `xr.xml` lines 8422-8478, extension line 16244 | CC-BY-4.0 extension text | 51: 14 eye and 37 lip shapes | 2 | no brow or nose shapes, so it cannot fill `face`; it needs a split of `face` into one group per action |
| OpenFace 2.x action unit outputs | OpenFace wiki pages "Action-Units" and "Output-Format" (not pinned to a commit) | software licensed for noncommercial academic research only; the licence grants no trademark rights; the wiki pages state no licence | 18 action units; intensity 0 to 5 for 17 of them | 2 | column names and the scale used as facts only; in-maps only, by `piecewise_linear` knots (0, 0), (1, 0.2) to (5, 1.0). No sides, so each sided signal is a fan-out; cannot fill `face` (no 8, 16, 18, 22, 24 or 28); needs a trademark check |
| Py-Feat action unit outputs | `feat/pretrained.py` at `4ebb4ec` (lines 89-108) | code MIT; model weights noncommercial | 20 action units | 2 | output scale not checked; in-maps only; cannot fill `face` (no 8, 16, 18 or 22) |
| Microsoft Rocketbox AU shapes | Rocketbox at `0943055` | MIT | 48 shapes | test asset | a target asset for FACS, not a new set |
| MetaHuman curves; MPEG-4 facial animation parameters; Apple Vision Pro personas | Epic documentation; ISO/IEC 14496-2; Apple documentation | MetaHuman DNA calibration files: Epic terms, Unreal Engine only; ISO standard paid | not counted | not planned | MetaHuman only if Epic publishes the names under usable terms |
| Live Link Face; Unity AR Foundation | Epic and Unity documentation | not checked | ARKit's 52 | no new set | these pass ARKit values through; use the ARKit profile |
| FACS emotion presets (EMFACS) | `facs_wikipedia` raw lines 36-53 | CC-BY-SA-4.0 article text | 7 emotions | examples only | stay in `examples/data/expressions.json`, not pack data |

Phase 1b also adds the FACS gaze codes 61-64, with the loss key `facs_side_frame_unresolved`. Phase 2 adds the FACS-only signals that the action unit detectors need, such as `lips_part` (25), as version 1.1 signals ([reserved names](canonical-set.md#reserved-names)).
