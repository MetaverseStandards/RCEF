<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Public expression survey

## Overview

This survey describes the public face-expression interfaces that RCEF records. It covers ARKit, MediaPipe, three OpenXR extensions (FB, FB2 and META visemes), VRCFaceTracking, Godot, VRM, Roblox and the FACS codes. For each set, it gives the source, the signals and the meaning of the values. It also gives the maps into and out of the canonical sets, and the gaps.

Every number comes from the pack, `generated/rcef.pack.json`, or from a document that the text links. The counts describe interfaces. They do not say how well a tracker follows a face. The canonical sets and `facs.code` are drafts, and the cross-provider mappings are proposed approximations.

Read [How RCEF reads each set](#how-rcef-reads-each-set) first. It defines the terms that every family section uses. [Selected scope](#selected-scope) gives one line for each set. Each family section then has the same five parts ([Parts of each family section](#parts-of-each-family-section)). [Comparison across sets](#comparison-across-sets) compares the sets and gives the effect of their shared problems on the canonical design.

Other documents give more detail. The pinned source and licence of each profile file are in [docs/expression-sets.md](docs/expression-sets.md). [docs/canonical-set.md](docs/canonical-set.md) defines the canonical signals, and the [definitions audit](docs/canonical-set-audit.md) compares them with each source. Every signal is in [reports/inventory.md](reports/inventory.md), and every mapping is in [reports/mappings.md](reports/mappings.md).

## How RCEF reads each set

### Selection criteria

A set joins the survey only when it meets all of these criteria:

- It is a public interface: a list of expression names in a published specification, documentation page or source file.
- It has a pinned source: an exact revision, or a retrieval date and a SHA-256 digest of the bytes.
- Each fact has a locator, such as line numbers or a named section of the pinned source.
- Its licence or terms are known. Where the terms do not allow copying, RCEF writes its own summary and cites the evidence record.

The list of sets in [docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets) has every face, facial, lip and eye expression weight enum in the OpenXR registry at commit `5a82d45` (record `xr_registry`). It also has RCEF's own sets and other sets that the authors knew of. So that list is complete for OpenXR at that commit. It is not a complete list of public sets. This survey covers only the sets that have a profile. [references.md](references.md) lists every evidence record with its URL, revision and digest.

### Provider text and devices

RCEF uses provider names, indices and interface facts as facts, with attribution. It writes its own summary of each source and does not copy provider prose or figures that have no open licence ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). The family sections name only the sources whose terms add a limit.

RCEF's [physical capture design](docs/calibration/physical-protocol.md) names a device for some sets. Nobody has run it. So no family section says how a tracker responds to a real face.

### Profiles, rows and selected entries

A profile records one expression set, or one part of a set. Each row of a profile is a signal. A profile can also hold rows outside the public interface: count sentinels, rows that record an absent entry, reserved bytes and state fields. RCEF keeps these rows so that the gaps stay visible.

The selected entries are the names of the public interface itself. The profile metadata field `selected_count` gives their number. In a profile with selected entries, the signal metadata field `selected = false` marks a row outside them. So FB2 has 70 selected entries in 71 rows.

The ancillary profiles `arkit.ancillary`, `openxr.ancillary` and `vrcft.parameter.encoding` have no selected entries. `facs.code` and `mediapipe.score` have no `selected_count`. `facs.code` is RCEF's own encoding of public code numbers, and `mediapipe.score` is a second view of the 52 outputs of `mediapipe.label`.

A native index is an index that the source defines, for example an enum value. An inventory ordinal is a position in a documentation list. RCEF records an inventory ordinal where the source defines no index.

### Dispositions

Each signal has one disposition and a reason in its metadata. The 20 profiles of the survey (19 of public sets, and `facs.code`) hold 1011 signals.

| Disposition | Meaning | Signals |
|---|---|---:|
| `mapped` | At least one mapping uses the signal. | 269 |
| `unresolved` | The evidence is missing or conflicts, or RCEF has not researched the signal yet. | 682 |
| `excluded` | Out of scope, for example a count sentinel or a confidence enum. | 54 |
| `unsupported` | The source has the value, but RCEF supports no executable mapping for it. | 6 |

A `mapped` signal does not guarantee that every map or frame that reads it can run.

### Evidence status

Each signal and each mapping has an `evidence_status`. It describes how much evidence supports the signal or mapping. It is separate from the disposition and from the mapping quality (`exact` or `approximate`).

| Status | Meaning |
|---|---|
| `verified_current` | The signal or mapping restates a verified source fact. |
| `proposed` | An approximate translation that sources support. It compiles only with the approximation opt-in. |
| `unresolved` | Recorded but not executable. `compile_mapping` refuses it, also with the opt-in. |

The 484 mappings of the 15 maps into and out of the canonical sets are `proposed` and `approximate`, except 4. The 4 exceptions are the pupil copies between VRCFaceTracking eye data and the canonical expression set, which are `exact` and `verified_current`. The 101 mappings of the viseme pose bridge are `proposed` and `approximate`. All 81 evidence records have the status `verified_current`. That status says only that each cited source is what the record claims.

### Side conventions

A side name, such as `Left` or `_L`, can name the subject's own side or the side that a viewer sees. The definitions audit settles this once for each source ([Frames](docs/canonical-set-audit.md#frames-whose-left)). The same frame applies to the direction words of gaze, jaw and mouth shift. A provider's own text or figure settles a frame. Agreement between implementers settles only which output gets a value.

| Source | Frame | Evidence | Audit verdict |
|---|---|---|---|
| ARKit | the subject's own side (Apple calls it the face's own side) | Apple's text (`apple_blendshapes`), with one exception for `mouthStretchRight` | `same` |
| FB2 | the subject's own side | three FB2 figures (`xr_fb2_fig_*`) and the text | `same` |
| VRCFaceTracking artist shapes | the subject's own side | three Unified Expressions figures (`vrcft_fig_*`) | `same` |
| VRCFaceTracking eye data | as the artist shapes | the project computes `v2/EyeClosedLeft` from `Left.Openness` | `same` |
| VRM | not stated by the source; RCEF reads the subject's own side as an assumption | `vrm_expressions` | `unresolved` |
| FACS codes | not stated by the source; RCEF reads L and R as the subject's own side, as an assumption | `facs_wikipedia` raw line 78 | `unresolved` |
| FB, MediaPipe, Godot, Roblox, VRCFaceTracking transport and avatar parameters | taken from the name; not checked | none | no audit row |

### Values and calibration

Each signal states its units, its domain and its calibration. A calibration string is a declaration, not a measurement. Units `unknown` and an empty domain `{}` keep a gap visible. A `neutral` value is a stated reference. A `native_default` is the value that storage starts with, and it is not a measured neutral.

The gain of a signal is how far the face moves for a given value. No provider publishes the gain of its values or its pose at full activation. So every mapping into or out of a canonical set makes the same assumption, except the 4 pupil copies in millimetres. It assumes that the ends of the source range are canonical 0 and 1. It also assumes that the values between correspond as the operator passes them. No evidence supports this, and RCEF has measured no response curve ([canonical-set.md](docs/canonical-set.md#meaning-of-0-1-and-neutral)).

Most maps state this as a loss of the form "ARKit gain and full-activation pose not published". A loss key is a stable name for a loss in the [definitions audit](docs/canonical-set-audit.md#loss-keys). The FACS maps state the loss key `facs_ordinal_intensity` instead. The VRM maps state that an asset-authored weight becomes a canonical value.

The 5 records in [calibration/](calibration/README.md) are software-only. They are fits to renders or mesh geometry of example rigs. None of them measures a tracker. Each family section names the records that read the values of its set.

### Maps, parts and routes

RCEF has at most one map for each pair of an expression set and a canonical set, in each direction. The ID has the form `<from>.to_<to>`, for example `fb2.to_rcef_expression` (the FB2 in-map) and `rcef_expression.to_fb2` (the FB2 out-map). A part of a map is its mappings for one canonical group. The canonical expression set has 72 signals in 13 groups. The canonical viseme set has 16 signals in 4 groups. Each map has a page in [docs/map-sets/](docs/map-sets/).

A route runs from a source set through a canonical set to a target set ([README.md](README.md#routes)). It writes only the target signals of the groups that both sets fill. It labels the other target outputs "not available from source", and it lists as dropped each non-zero source input that it does not use. Data 0.5.0 retired the direct maps between providers, so every route goes through a canonical set.

Where the audit finds that a source definition `differs` from the canonical one, or leaves it `unresolved`, the row gives a loss key. Every mapping of that signal states the loss key.

### What a set needs before it gets a map

The rule for every new set is in [docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets). A set needs these items:

1. A pinned public source and a known licence.
2. A profile and evidence records.
3. Rows in the definitions audit, with a frame row for its side names.
4. A row in the test that checks which canonical groups each set can fill.
5. In-maps or out-maps.
6. A row in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for a new holder of CC-BY-4.0 text, and a trademark check for a product name in a profile ID.

New sets join after data 0.5.0, so they do not change the frozen A/B comparison ([ab/README.md](ab/README.md)). Their routes have no direct map to compare with, so RCEF labels each route "no external reference", unless a public route exists. The family sections of the sets with no map list only the items that are missing.

### Parts of each family section

| Part | What it gives |
|---|---|
| Technical context | who publishes the set, what produces or reads the values, the evidence records and the licence |
| Signal structure | the profiles, the names, the regions and sides, and the special entries |
| Values, neutral and calibration | units, range, neutral, the calibration string, and the calibration records that read the values |
| Mapping to the canonical sets | the maps, their parts and losses, the routes, and the signals that no map reads |
| Gaps and conflicts | each gap or conflict, its evidence, and what it blocks |

## Selected scope

| Surface | Selected entries | Calibration and execution boundary |
|---|---:|---|
| ARKit coefficient | 52 | Native 0 to 1. Sides are the subject's own side (Apple calls it the face's own side). Proposed approximate copies and means read and write all 52. Eye transforms stay separate. |
| MediaPipe label | 52 | 51 names shared with ARKit, plus `_neutral`; no `tongueOut`. Model calibration unresolved. `_neutral` is `excluded`. |
| OpenXR FB | 63 | RCEF keeps validity, eye-following validity, confidence and time. The pinned extension text gives no explicit numeric range. No tongue entries. |
| OpenXR FB2 | 70 | Native 0 to 1. Seven tongue entries, a choice of visual or audio data source, and eight native gaze fractions, one for each direction of each eye. Maximum angles unresolved. |
| Optional META visemes | 15 | Needs FB2. Probabilities with a valid sum of 1 and a separate validity flag. Valid silence differs from invalid all-zero data. |
| VRCFaceTracking transport | 88 | The active enum, kept apart from the eye data and the artist vocabulary. The byte transport clamps and truncates. RCEF records these losses as inventory, and no map runs them. |
| VRCFaceTracking eye | 12 scalar components | Gaze x and y, openness and pupil diameter, for left, right and combined. The four raw openness and diameter fields are `mapped`. The combined computation is unresolved. |
| VRCFaceTracking artist base/blended | 102 / 42 | RCEF keeps the artist components and the 4 footnoted `unsupported` shapes. The component lists define no weights and no executable operators. |
| VRCFaceTracking avatar numeric/flags | 124 / 3 | Floats from the public list, optional prefixes and status flags. A separate profile records the binary encoding. RCEF does not guess expanded avatar-specific names. |
| Godot base/blended | 102 / 41 | RCEF keeps the spelling `FT_TONGUE_BLEND_DOWN`. The setters store floats with no clamp. The initial zero of the array is initialization. RCEF infers no device availability. |
| VRM 1.0 presets | 18 | All optional and authored for each asset. RCEF keeps the morph, material and texture bindings, the thresholds, the overrides and the LookAt metadata. |
| Roblox FaceControls | 50 | Native 0 to 1, but the joint poses and correctives are specific to each asset. RCEF keeps the neutral Frame 0 and the conflict between the required pose lists. |
| FACS codes | 92 rows (70 code numbers) | RCEF's own numeric encoding of public code numbers. The values are not FACS scores. Draft. 49 rows `mapped`. |

[sources.toml](evidence/sources.toml) gives the digests. The coverage report, `generated/coverage.json`, counts the signals of each disposition.

## ARKit

### Technical context

Apple publishes ARKit, its augmented reality framework. In face tracking, ARKit gives a face anchor, `ARFaceAnchor`, which reports 52 blend-shape coefficients. Each coefficient is one value for one named movement of the face. RCEF's physical capture design names an iPhone with a TrueDepth camera as the ARKit device.

Other software, for example Live Link Face and Unity AR Foundation, gives the same 52 values without change. So RCEF gives them no profile of their own ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). Avatar rigs with ARKit-named shapes read the values. The RCEF examples and calibration records use rigs from two such libraries: ICT-FaceKit and Microsoft Rocketbox.

| Evidence record | What RCEF takes from it | Retrieved | Licence or terms, as RCEF records them |
|---|---|---|---|
| [`apple_blendshapes`](references.md#apple_blendshapes) | the 52 coefficient names, the native range 0 to 1, and the sides: the subject's own side (Apple calls it the face's own side) | 2026-10-26 | reference only; source prose not redistributed |
| [`apple_eye`](references.md#apple_eye) | the eye pose is a transform, separate from the eyelid coefficients | 2026-10-26 | reference only; source prose not redistributed |

Apple's documentation pages build their content with JavaScript. So each record pins Apple's JSON data for the page by its SHA-256, and has no revision ID. The definitions audit gives an RCEF paraphrase of each Apple definition.

### Signal structure

| Profile | Rows | Selected entries | Dispositions | Role in maps |
|---|---:|---:|---|---|
| `arkit.coefficient` | 52 | 52 | 52 `mapped` | source and target |
| `arkit.ancillary` | 2 | 0 | 2 `excluded` | inventory only |

Each name is in lower camel case. It starts with a region word, then names a movement, and ends with `Left` or `Right` when the movement has a side. Examples are `eyeBlinkLeft`, `jawOpen` and `mouthSmileRight`. ARKit gives no numeric index, so RCEF keeps the order of the pinned documentation data as the inventory ordinals 0 to 51.

| Region | Signals | Names |
|---|---:|---|
| gaze | 8 | `eyeLookDown`, `eyeLookIn`, `eyeLookOut`, `eyeLookUp`, each `Left` and `Right` |
| eyelid | 6 | `eyeBlink`, `eyeSquint`, `eyeWide`, each `Left` and `Right` |
| brow | 5 | `browDownLeft`, `browDownRight`, `browInnerUp`, `browOuterUpLeft`, `browOuterUpRight` |
| cheek | 3 | `cheekPuff`, `cheekSquintLeft`, `cheekSquintRight` |
| nose | 2 | `noseSneerLeft`, `noseSneerRight` |
| jaw | 4 | `jawForward`, `jawLeft`, `jawRight`, `jawOpen` |
| mouth | 23 | `mouthClose`, `mouthFunnel`, `mouthPucker`, `mouthLeft`, `mouthRight`, `mouthRollLower`, `mouthRollUpper`, `mouthShrugLower`, `mouthShrugUpper`, and the `Left` and `Right` forms of `mouthSmile`, `mouthFrown`, `mouthDimple`, `mouthStretch`, `mouthPress`, `mouthLowerDown` and `mouthUpperUp` |
| tongue | 1 | `tongueOut` |

The profile has 20 left, 20 right and 12 shared signals. In Apple's text, the side in a name is the subject's own side (Apple calls it the face's own side). So `eyeBlinkRight` is the subject's own right eye. The direction words of `jawLeft`, `jawRight`, `mouthLeft` and `mouthRight` use the same frame.

Some ARKit signals are one value where other sets have two or four. `browInnerUp` and `cheekPuff` have the coupling `bilateral_shared`: one value for both sides. `mouthFunnel`, `mouthPucker`, `mouthRollUpper` and `mouthRollLower` are also single values, and the canonical set splits each of them.

Special entries:

- `tongueOut` is the only tongue signal.
- The 8 `eyeLook*` coefficients describe eyelid movement that goes with a gaze direction. They do not describe eyeball rotation ([audit](docs/canonical-set-audit.md#arkit)).
- The eye pose is a 4 × 4 transform. `arkit.ancillary` records `leftEyeTransform` as `excluded`, because the scalar wire format of version 1 does not execute transforms. RCEF records no row for the right-eye transform.
- `init(rawValue:)` is a constructor that accepts any key. It is not one of the 52 coefficients, so it is `excluded`.
- RCEF records no count sentinel, confidence value or validity flag for ARKit.

### Values, neutral and calibration

| Property | Value |
|---|---|
| Value type and units | scalar, units `1` |
| Range | 0 to 1 (`apple_blendshapes`) |
| Neutral | 0.0 |
| Calibration string | `arkit.coefficient.v1:<name>: face-relative native neutral-to-maximum coefficient` |

Apple's text says that each coefficient goes from 0.0, the neutral position, to 1.0, the maximum movement. Apple does not publish the gain of a coefficient, or the pose of full activation as geometry or as an angle. Every ARKit mapping states the loss "ARKit gain and full-activation pose not published".

The software-only record [`rig-gains.ict-rocketbox-female`](calibration/README.md) compares how ICT-FaceKit and Rocketbox Female render 51 ARKit shapes. 3 shapes pass (`browInnerUp`, `cheekSquintLeft` and `cheekSquintRight`), and 48 fail. The record also notes that ICT's `eyeLook` shapes move only the eyelids, while Rocketbox's shapes move the eyeballs. The record describes rigs. It does not describe a tracker.

### Mapping to the canonical sets

| Map | Direction | Mappings | Parts | Operators | Evidence status |
|---|---|---:|---:|---|---|
| [`arkit.to_rcef_expression`](docs/map-sets/arkit.to_rcef_expression.md) | `arkit.coefficient` → `rcef.canonical_expression` | 60 | 9 | 60 copies (affine 1, 0) | `proposed` (60) |
| [`rcef_expression.to_arkit`](docs/map-sets/rcef_expression.to_arkit.md) | `rcef.canonical_expression` → `arkit.coefficient` | 52 | 9 | 46 copies, 6 means (`weighted_sum`) | `proposed` (52) |

The in-map reads all 52 coefficients and writes 60 canonical signals. Five coefficients each write two canonical signals, left and right: `browInnerUp`, `cheekPuff`, `mouthPucker`, `mouthRollUpper` and `mouthRollLower`. `mouthFunnel` writes the four quarters of the lips. These 14 mappings state the loss "asymmetry unknown: symmetry is invented". The out-map takes the mean of the same canonical signals, with the loss "asymmetry irrecoverable".

| Canonical group | Canonical signals | In-map mappings | Out-map mappings |
|---|---:|---:|---:|
| `face` | 41 | 41 | 34 |
| `cheek_puff` | 2 | 2 | 1 |
| `jaw_thrust` | 1 | 1 | 1 |
| `jaw_sideways` | 2 | 2 | 2 |
| `mouth_shift` | 2 | 2 | 2 |
| `chin_raise_upper_lip` | 1 | 1 | 1 |
| `blink` | 2 | 2 | 2 |
| `gaze` | 8 | 8 | 8 |
| `tongue_out` | 1 | 1 | 1 |
| `cheek_suck`, `lip_tighten`, `tongue_place`, `pupil_mm` | 12 | none | none |

ARKit fills 9 of the 13 groups. The ARKit section of the audit names no ARKit signal for `cheek_suck`, `lip_tighten`, `tongue_place` or `pupil_mm`.

Every mapping cites `apple_blendshapes`. The correspondence between ARKit names and canonical signals comes from crosswalks. A crosswalk is a public table of another project that pairs the names of two sets. On the in-map, every mapping cites at least three crosswalks, and 36 of the 60 cite five. The [map page](docs/map-sets/arkit.to_rcef_expression.md) lists the count for each record. The assumptions of each mapping say which crosswalks apply to the canonical signal.

The audit has 60 ARKit rows: 36 `same`, 22 `differs` and 2 `unresolved`.

| Loss key | What differs | In-map | Out-map |
|---|---|---:|---:|
| `arkit_gaze_eyelid` | eyelid movement, not eyeball rotation | 8 | 8 |
| `arkit_browdown_outer` | only the outer brow drops | 2 | 2 |
| `arkit_eyesquint_face` | the face around the eye, not the lids only | 2 | 2 |
| `arkit_cheeksquint_cheek` | the cheek lift only | 2 | 2 |
| `arkit_mouthsmile_upward` | upward corner movement only | 2 | 2 |
| `arkit_mouthshrug_outward` | the lip moves out, not up | 2 | 2 |
| `arkit_mouthpucker_compression` | the closed lips compress, with no forward push | 2 | 1 |
| `arkit_mouthpress_lower_lip` | the lower lip is pushed up | 2 | 2 |
| `arkit_mouthstretchright_text_side` | the text names the other corner | 1 | 1 |
| `arkit_mouthclose_jaw_unresolved` | the relation to the jaw is unresolved | 1 | 1 |

ARKit is the source of 6 routes and the target of 7 routes ([README.md](README.md#routes)). Data 0.5.0 retired the direct maps `arkit.to_fb2`, `arkit_gaze.to_fb2`, `arkit.to_vrcft_artist`, `fb2.to_arkit` and `fb2_gaze.to_arkit`, and the identity map `arkit.to_canonical` ([docs/retired-ids.csv](docs/retired-ids.csv)).

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| Apple's abstract for `mouthStretchRight` applies the pull to the other corner. The name and RCEF's profile say right. | `apple_blendshapes`; `arkit_mouthstretchright_text_side` | A `same` verdict for `lip_stretch_right`. The maps take the side from the name. |
| Apple's text and RCEF's record `rig-gains.ict-rocketbox-female` conflict on whether `mouthClose` depends on the jaw. On ICT-FaceKit, `mouthClose` alone failed 24 of 24 held-out conditions. | `apple_blendshapes`; `arkit_mouthclose_jaw_unresolved` | A `same` verdict for `lips_toward`. The out-map copies the value and does not compensate for the jaw. |
| 22 audit rows find that the ARKit definition differs from the canonical definition. | [audit](docs/canonical-set-audit.md#arkit) | Exact mappings. The mappings run, and each one states the difference as a loss. |
| No gain and no full-activation pose. | every ARKit mapping | Measured intensities. |
| No maximum gaze angle, and eye transforms are not executed. | `apple_eye`; `arkit_gaze_eyelid` | Gaze as an angle, and any identity with the gaze of another provider. |
| Only Godot names ARKit `mouthLeft` and `mouthRight` for the `mouth_shift` signals. | assumption `evidence.godot_only_mouth_shift` | A correspondence for that part from a second source. |

## MediaPipe

### Technical context

Google publishes MediaPipe, and its code is under Apache-2.0. The MediaPipe Face Landmarker task finds a face in a camera image. It gives face landmarks and a list of blendshape scores. The model bundle holds a face detector, a face landmark detector and a blendshape model ([docs/calibration/mediapipe-licence.md](docs/calibration/mediapipe-licence.md)). The Blendshape V2 model card says that the model predicts 52 coefficients in [0, 1] from 146 of the 478 face landmarks. The card gives AR entertainment from selfie video as the intended use.

To run the model, a user needs the `mediapipe` Python package. RCEF uses the model only in an optional calibration tool. `check.py` and the tests do not use it.

| Evidence record | Source | What RCEF takes from it | Retrieved | Licence |
|---|---|---|---|---|
| [`mediapipe`](references.md#mediapipe) | `face_blendshapes_graph.cc` at MediaPipe `f6988c4` | the label list `kBlendshapeNames`: 52 labels with `_neutral` and without `tongueOut`; scores are returned without a threshold filter | 2026-10-07 | Apache-2.0 |
| [`mediapipe_blendshape_card`](references.md#mediapipe_blendshape_card) | Blendshape V2 model card (PDF) | 52 coefficients in [0, 1] from 146 landmarks; the licence; how the training data was made | 2026-10-27 | Apache-2.0 |
| [`mediapipe_face_landmarker`](references.md#mediapipe_face_landmarker) | `face_landmarker.task`, float16, version 1 | the blendshape model that the calibration record uses to score renders | 2026-10-27 | Apache-2.0 |

The model bundle has no licence file. The licence comes from the model cards, which each state Apache License 2.0. RCEF's licence check concluded, within its limits, that the licence lets RCEF score renders of its example rigs. It also lets RCEF publish curves fitted to those scores under CC-BY-SA-4.0. The check is not legal advice.

The card says that the training samples come from multi-view lab captures of people. An automatic process moved the 52 blendshapes from a base mesh that an artist designed.

### Signal structure

RCEF records MediaPipe in two profiles. Both are inventory only.

| Profile | Rows | What the rows are | Dispositions |
|---|---:|---|---|
| `mediapipe.label` | 53 | the 52 labels, plus a row that records the absent `tongueOut` | 51 `unresolved`, 1 `excluded` (`_neutral`), 1 `unsupported` (`tongueOut.absent`) |
| `mediapipe.score` | 52 | the same 52 outputs as numbers in [0, 1], for calibration against renders | 51 `unresolved`, 1 `excluded` (`_neutral`) |

The list starts with `_neutral`. The other 51 labels follow in alphabetical order, and each one is an ARKit coefficient name. The ARKit name `tongueOut` is not in the list. RCEF keeps the list position as the inventory ordinal.

Each of the 51 labels has the region and the side of the ARKit coefficient with the same name. So the profile has 20 left, 20 right and 11 shared expression labels, and `_neutral` is shared. RCEF takes the side from the name. The audit has no MediaPipe row, so RCEF does not record whether the sides are the subject's own or the viewer's.

Special entries:

- `_neutral` is a reserved model output. MediaPipe's own code tells users to ignore it, so RCEF records it as `excluded`.
- `tongueOut.absent` records that the runtime list has no `tongueOut` channel. It has the inventory ordinal −1 and is `unsupported`.
- The profile metadata records that MediaPipe returns the scores without a threshold filter (`coefficients_returned_unfiltered`).
- RCEF records no validity flag, confidence value or gaze transform for MediaPipe.

### Values, neutral and calibration

| Property | `mediapipe.label` | `mediapipe.score` |
|---|---|---|
| Units | `unknown` | `1` |
| Range | none | 0 to 1 (`mediapipe_blendshape_card`) |
| Neutral | none | none |
| Calibration string | `mediapipe.label: native basis; no canonical calibration established` | `mediapipe.score.v1: Face Landmarker blendshape score in [0, 1], the model's output; no provider calibration` |

RCEF records no source text that says what 0 and 1 mean for one score. The output `_neutral` is not a neutral value for the other scores: it is a separate output, and RCEF excludes it. The label profile records `model_calibration = "unresolved"`.

RCEF tested the scores in the software-only record [`mediapipe.ict-response`](calibration/README.md), version 2. The tool rendered ICT-FaceKit with one ARKit shape at a time, at the weights 0, 0.2, 0.4, 0.6, 0.8 and 1. It used 24 training conditions. Each condition used a different ICT identity and varied the head pose, the camera and the light in set ranges. For each score, it fitted a curve from the MediaPipe score back to the ARKit weight.

| Result | Count |
|---|---:|
| ARKit-named scores tested | 51 |
| Scores that rose enough in training to fit a curve | 25 |
| Scores with no curve | 26 |
| Held-out cells: for each fitted score, one on 20 new ICT identities and one on Rocketbox Male_Adult_01 | 50 |
| Held-out cells within the bounds (median error at most 0.05, 95th percentile at most 0.15, neutral error at most 0.03) | 0 |

So the record is a negative result, and no mapping cites it. Some scores did not move at all. For example, the median scores of `cheekPuff`, `mouthClose`, `noseSneerLeft` and `noseSneerRight` rose by 0.000 from weight 0 to weight 1. The median score of `jawForward` also rose by 0.000. Other scores are high on a neutral render: the fitted curve for `eyeSquintLeft` maps every score up to 0.456 to weight 0.

The record states its limits. It describes MediaPipe on untextured grey renders, not on real faces or photographs. Each shape moved alone, so it does not measure combinations. MediaPipe and ICT-FaceKit both follow artist-made ARKit conventions, so their agreement may come partly from those shared conventions.

### Mapping to the canonical sets

MediaPipe has no executable map, and no route starts or ends at a MediaPipe profile. RCEF records one mapping on purpose: `survey.mediapipe_rcef.blink` in the map `survey.ambiguous` ([mappings/unresolved.toml](mappings/unresolved.toml)). It reads `mediapipe.label.eyeBlinkLeft` and writes the canonical `eye_close_left` with the `identity` operator. Its disposition and its evidence status are both `unresolved`. Its assumption is that names alone cannot establish the calibration of a model or a provider. `compile_mapping` refuses it, also with the approximation opt-in, and the architecture checklist uses it to check this refusal ([docs/architecture.md](docs/architecture.md)).

RCEF has no MediaPipe maps for three reasons. Only one independent implementation, in three.js, maps MediaPipe to ARKit. The licence check found no statement in the model card that relates the scores to ARKit coefficients, apart from the shared names. The calibration record found no score that passes.

A MediaPipe map can come only from a calibration record ([calibration/README.md](calibration/README.md#mappings-that-cite-a-record), [docs/canonical-set.md](docs/canonical-set.md#calibrated-mediapipe-records)). Every held-out cell of a score must pass. The passing curve then becomes a `piecewise_linear` mapping of an in-map, `mediapipe.to_rcef_expression`, with exactly the frozen knots of the record. It never becomes a direct MediaPipe → ARKit map. The plan puts MediaPipe in phase 2, if the project decides to map it ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). The runtime list has no `tongueOut`, so a MediaPipe in-map could not fill the `tongue_out` group.

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| No evidence for the model calibration and provenance of the scores. | [README.md](README.md#open-questions), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open) | Every derived mapping from MediaPipe. |
| The model card lists 52 names, with `tongueOut` and `cheekPuff`. The runtime list returns `_neutral` and 51 ARKit names, without `tongueOut`. RCEF follows the runtime list. | `mediapipe_blendshape_card`, `mediapipe` | A `tongueOut` signal. |
| No source relates a MediaPipe score to an ARKit coefficient, apart from the name. | [docs/calibration/mediapipe-licence.md](docs/calibration/mediapipe-licence.md) | A copy from a label to an ARKit or canonical signal. |
| The software-only calibration failed on every held-out cell. | `mediapipe.ict-response` | A calibrated in-map under the current rule. |
| The fitted curves include `eyeLookInRight` and `eyeLookOutLeft`, but not `eyeLookInLeft` or `eyeLookOutRight`. The last limitation of the record gives the reason: in training, their median scores rose only 0.064 and 0.050, too little to fit a curve. RCEF records no reason why the left and right eyes differ. | `calibration/mediapipe.ict-response.cal` | Nothing directly. It is an open question for the gaze scores. |
| No evidence for the side frame of the label names. | no audit row | Side assignment in any future in-map. |
| The physical capture design would record ARKit and MediaPipe from the same iPhone frames. Before any part of it runs, it needs a named owner, an ethics and legal review, and approval from the project's release owners. | [docs/calibration/physical-protocol.md](docs/calibration/physical-protocol.md) | Any statement on how MediaPipe responds to a real face. |

## OpenXR FB (`XR_FB_face_tracking`)

### Technical context

`XR_FB_face_tracking` is an extension of the OpenXR specification, which the Khronos Group publishes. Its weight enum is `XrFaceExpressionFB`. The extension gives the weights as one array (`XrFaceExpressionWeightsFB`), with validity flags, confidence values and a time stamp. RCEF records no device or runtime that produces these values, and no application that reads them.

RCEF calls this set FB, or FB v1. Its successor, FB2, has the same first 63 names in the same order, with `EXPRESSION2` in place of `EXPRESSION`.

| Item | Value |
|---|---|
| Profile | `openxr.fb` ([profiles/openxr.fb.toml](profiles/openxr.fb.toml)) |
| Extension text | record [`xr_fb`](references.md#xr_fb): `fb_face_tracking.adoc` in OpenXR-Docs at `5a82d45`, retrieved 2026-10-07 |
| Names and indices | record [`xr_registry`](references.md#xr_registry): `xr.xml` at the same commit, enum `XrFaceExpressionFB` |
| Licence | CC-BY-4.0 for the extension text; Apache-2.0 OR MIT for `xr.xml` (its SPDX header), whose identifiers RCEF uses as facts |
| Role in maps | inventory only |

RCEF's notices name the Khronos Group and Meta Platforms, LLC and affiliates as holders of the cited extension text ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). The record `xr_fb` supports the order of the weights, the separate eye-following validity flag, the upper and lower confidence values and the `XrTime` stamp. The same record states that this text gives no explicit numeric bounds for the weights.

### Signal structure

Each name has the form `XR_FACE_EXPRESSION_<ACTION>_FB`. The action part names a face movement, for example `BROW_LOWERER`, `LIP_CORNER_PULLER` or `JAW_DROP`. Where the movement has a side, a suffix follows: `_L` or `_R`, or `_LB`, `_LT`, `_RB` and `_RT` for the four quarters of the lips. `CHIN_RAISER` has a `_B` entry and a `_T` entry, for the bottom and the top lip.

| Rows in `openxr.fb` | Count | Disposition |
|---|---:|---|
| Selected weights, native indices 0 to 62 | 63 | `unresolved` |
| `XR_FACE_EXPRESSION_COUNT_FB`, the count sentinel at index 63 | 1 | `excluded` |
| `tongue.absent`, a row that records that the enum has no tongue entry | 1 | `unsupported` |
| Total | 65 | |

The profile `openxr.ancillary` holds the configuration enums of FB and FB2. All are `excluded`. Their reason is "Configuration/confidence region enum; not an expression amplitude." Four of its 10 rows belong to FB: `XR_FACE_CONFIDENCE_LOWER_FACE_FB`, `XR_FACE_CONFIDENCE_UPPER_FACE_FB`, `XR_FACE_CONFIDENCE_COUNT_FB` and `XR_FACE_EXPRESSION_SET_DEFAULT_FB`.

| Region | Selected rows | Examples |
|---|---:|---|
| mouth | 29 | lip corners, lip quarters, `CHIN_RAISER_B` and `_T`, `LIPS_TOWARD`, `MOUTH_LEFT` |
| gaze | 8 | `EYES_LOOK_{DOWN,LEFT,RIGHT,UP}_{L,R}` |
| brow | 6 | inner and outer brow raisers, brow lowerers |
| cheek | 6 | cheek puff, cheek raiser, cheek suck |
| other | 6 | the `DIMPLER`, `LID_TIGHTENER` and `UPPER_LID_RAISER` pairs |
| jaw | 4 | `JAW_DROP`, `JAW_SIDEWAYS_LEFT`, `JAW_SIDEWAYS_RIGHT`, `JAW_THRUST` |
| eyelid | 2 | `EYES_CLOSED_L`, `EYES_CLOSED_R` |
| nose | 2 | `NOSE_WRINKLER_L`, `NOSE_WRINKLER_R` |

Of the 63 selected rows, 27 are left, 27 are right and 9 are shared. The shared rows are the two chin raisers, the four jaw entries, `LIPS_TOWARD` and the two mouth directions. The profile takes the side from the name suffix. The audit has a frame row for FB2 and none for FB, so no RCEF document settles the side frame of the FB names.

The 8 gaze rows are valid only when `isValid` and `isEyeFollowingBlendshapesValid` are both true. The other 55 rows use `isValid` alone. Every selected row records the upper and lower confidence values, with no threshold, and the `XrTime` stamp, which a consumer must convert to seconds. FB has no tongue entries and no choice of data source.

### Values, neutral and calibration

| Property | What RCEF records |
|---|---|
| Range | Every FB row has the units `1` and an empty domain. The profile metadata sets `numeric_domain_status = "unresolved"`, because the pinned text states no numeric bounds. |
| 0 and 1 | RCEF records no FB statement about what 0 or 1 means. The FB2 text defines them, but RCEF does not apply that definition to FB. |
| Neutral | No FB row has a `neutral` field. |
| Calibration string | `openxr.fb: native basis; no canonical calibration established` on every row. No calibration record reads FB values. |

The missing numeric bounds are on the list of missing evidence as "FB1 numeric bounds" ([proposal.md](proposal.md#release-limits-and-remaining-evidence), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open)).

### Mapping to the canonical sets

FB has no map in either direction, and no route starts or ends at `openxr.fb`. Each selected row has the reason "Native identifier evidenced; canonical calibration and executable mapping remain unresolved."

A test checks which canonical groups each set can fill. For FB, it reads a committed list of the 63 names (`tests/fixtures/capability_sets.json`, from `xr.xml` lines 7507 to 7572). It expects this result:

| Canonical groups FB can fill | Canonical groups FB cannot fill |
|---|---|
| `face`, `cheek_puff`, `jaw_thrust`, `jaw_sideways`, `mouth_shift`, `chin_raise_upper_lip`, `blink`, `gaze`, `cheek_suck`, `lip_tighten` | `tongue_out` and `tongue_place` (no tongue entries), `pupil_mm` (no pupil entry) |

The plan puts FB in phase 1b, as 63 copies in one in-map with one part per group ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). FB already has a source, a profile and a capability row. It still needs a public source for the numeric range of the weights, a section of the audit with a frame row, and the in-map.

### Gaps and conflicts

| Gap | Evidence | What it blocks |
|---|---|---|
| The pinned FB text gives no numeric bounds for the weights. | `xr_fb` | Every FB mapping: the canonical domain is 0 to 1, and RCEF has no evidence that FB values stay in it. |
| The audit has no frame row for FB, and RCEF has no FB figure records. | [audit](docs/canonical-set-audit.md#frames-whose-left) | A verdict on the side frame of the FB suffixes. |
| No source gives the FB gain or the full-activation pose. | `xr_fb` | Any claim that an FB weight and an FB2 weight with the same name give the same face. |

RCEF records no conflict inside the FB sources.

## OpenXR FB2 (`XR_FB_face_tracking2`)

### Technical context

`XR_FB_face_tracking2` is the second face-tracking extension with the FB prefix in the OpenXR specification. Its weight enum is `XrFaceExpression2FB`. It keeps the 63 weight names of FB and adds 7 tongue weights. It also adds a choice of data source, visual or audio. RCEF calls it FB2.

| Item | Value |
|---|---|
| Profile | `openxr.fb2` ([profiles/openxr.fb2.toml](profiles/openxr.fb2.toml)) |
| Extension text | record [`xr_fb2`](references.md#xr_fb2): `fb_face_tracking2.adoc` in OpenXR-Docs at `5a82d45`, retrieved 2026-10-07 |
| Names and indices | record [`xr_registry`](references.md#xr_registry): `xr.xml` at the same commit, enum `XrFaceExpression2FB` |
| Figures | records `xr_fb2_fig_eyes_closed_l`, `xr_fb2_fig_eyes_look_left_l` and `xr_fb2_fig_mouth_left`, retrieved 2026-10-29; cited, not copied |
| Licence | CC-BY-4.0 for the extension text and the figures; Apache-2.0 OR MIT for `xr.xml` |
| Role in maps | source and target |

RCEF's physical capture design names a Quest Pro as the FB2 device. RCEF records two pieces of public software that read FB2 values. The Godot OpenXR vendors plugin copies each FB2 weight to a Godot shape (record `godot_vendors_fb2`). The VRCFaceTracking documentation pairs each Unified Expressions shape with an FB2 name in its Movement table (record `vrcft_docs_movement`). RCEF cites both as crosswalk evidence, and neither one sets the meaning of an FB2 name.

The examples translate synthetic FB2 face frames to ARKit through the canonical expression set ([examples/README.md](examples/README.md)). `scripts/derive_fb2_goldens.py` writes the FB2 test goldens from cached source bytes and never reads RCEF's maps.

### Signal structure

Each name has the form `XR_FACE_EXPRESSION2_<ACTION>_FB`, with the same suffixes as FB. The tongue names describe a tongue position, for example `TONGUE_TIP_ALVEOLAR` or `TONGUE_BACK_DORSAL_VELAR`.

| Rows in `openxr.fb2` | Count | Disposition |
|---|---:|---|
| Selected weights, native indices 0 to 69 | 70 | `mapped` |
| `XR_FACE_EXPRESSION2_COUNT_FB`, the count sentinel at index 70 | 1 | `excluded` |
| Total | 71 | |

| Suffix | Selected rows | Meaning |
|---|---:|---|
| `_L`, `_R` | 23 each | the subject's own left or right |
| `_LB`, `_LT`, `_RB`, `_RT` | 2 each | a quarter of the lips (`LIP_FUNNELER`, `LIP_SUCK`) |
| `_B`, `_T` | 1 each | `CHIN_RAISER`, bottom and top lip |
| none | 14 | the jaw entries, `LIPS_TOWARD`, `MOUTH_LEFT`, `MOUTH_RIGHT` and the 7 tongue entries |

Six rows of `openxr.ancillary` belong to FB2, all `excluded`: `XR_FACE_CONFIDENCE2_LOWER_FACE_FB`, `XR_FACE_CONFIDENCE2_UPPER_FACE_FB`, `XR_FACE_CONFIDENCE2_COUNT_FB`, `XR_FACE_TRACKING_DATA_SOURCE2_VISUAL_FB`, `XR_FACE_TRACKING_DATA_SOURCE2_AUDIO_FB` and `XR_FACE_EXPRESSION_SET2_DEFAULT_FB`.

The regions of the 70 selected rows are those of FB, plus 7 tongue rows at indices 63 to 69. The counts are 29 mouth, 8 gaze, 7 tongue, 6 brow, 6 cheek, 6 other, 4 jaw, 2 eyelid and 2 nose. Of the 70, 27 are left, 27 are right and 16 are shared.

FB2 names sides from the subject's own face. The audit settles this with the FB2 figures:

- `EYES_CLOSED_L` closes the eye on the viewer's right (record `xr_fb2_fig_eyes_closed_l`).
- `EYES_LOOK_LEFT_L` turns that eye toward the viewer's right, which is toward the temple (record `xr_fb2_fig_eyes_look_left_l`).
- `MOUTH_LEFT` moves the mouth toward the viewer's right (record `xr_fb2_fig_mouth_left`). The text ties the direction to the side name (`xr_fb2` lines 835 to 836).

The 8 gaze rows are valid only when `isValid` and `isEyeFollowingBlendshapesValid` are both true. Each has `coupling = "opposing_direction_exclusive"` and `neutral = 0.0`. The other 62 rows use `isValid` alone. A route reads validity as the AND of the flags in the `validity` field. When eye-following validity is false, the route refuses only the gaze outputs. Every row records the upper and lower confidence values, with no threshold, and the `XrTime` stamp.

The canonical set names gaze by "in" (toward the nose) and "out" (toward the temple):

| FB2 name | Canonical signal |
|---|---|
| `EYES_LOOK_LEFT_L` | `gaze_out_left` |
| `EYES_LOOK_RIGHT_L` | `gaze_in_left` |
| `EYES_LOOK_LEFT_R` | `gaze_in_right` |
| `EYES_LOOK_RIGHT_R` | `gaze_out_right` |
| `EYES_LOOK_UP_L`, `_R` | `gaze_up_left`, `gaze_up_right` |
| `EYES_LOOK_DOWN_L`, `_R` | `gaze_down_left`, `gaze_down_right` |

### Values, neutral and calibration

| Property | What RCEF records |
|---|---|
| Range | Every weight is in 0 to 1. A weight of 0 means that the shape is not active, and 1 means that it is fully active (`xr_fb2` lines 351 to 353). Each selected row has the domain 0 to 1, and the profile sets `numeric_domain_status = "verified_current"`. |
| Neutral | The 8 gaze rows have `neutral = 0.0`. The other 62 selected rows have no `neutral` field. |
| Calibration string | `openxr.fb2: native basis; no canonical calibration established` on 62 selected rows. Each gaze row has `openxr.fb2.v1:<name>: native direction-specific angle fraction; maximum angle unspecified`. |
| Gaze values | A gaze weight is proportional to the rotation angle and reaches 1 at the largest angle. At most one weight of an opposing pair is above zero (`xr_fb2` lines 643 to 649). The text gives no maximum angle. |
| Data source | RCEF records the visual and audio data sources as enum rows only. It does not record whether the two sources give the same values for the same face. |

Every FB2 mapping that reads or writes an FB2 weight states the loss "FB2 gain and full-activation pose not published". The calibration records are software fits to rigs, and none of them reads FB2 values.

### Mapping to the canonical sets

| Map | Direction | Mappings | Parts | Operators | Evidence status |
|---|---|---:|---:|---|---|
| [`fb2.to_rcef_expression`](docs/map-sets/fb2.to_rcef_expression.md) | `openxr.fb2` → `rcef.canonical_expression` | 70 | 12 | 70 copies (affine 1, 0) | `proposed` (70) |
| [`rcef_expression.to_fb2`](docs/map-sets/rcef_expression.to_fb2.md) | `rcef.canonical_expression` → `openxr.fb2` | 74 | 12 | 62 copies, 4 `weighted_sum`, 8 `piecewise_linear` | `proposed` (74) |

The out-map has a gaze part of 12 mappings. In it, 4 weighted sums with the weights 1 and −1 compute the difference of each opposing pair. Each difference goes into a helper value, for example `rcef.intermediate.gaze_in_minus_out_left`. Then 8 `piecewise_linear` curves split each difference back into two one-sided FB2 weights.

| Canonical group | Canonical signals | In-map mappings | Out-map mappings |
|---|---:|---:|---:|
| `face` | 41 | 41 | 41 |
| `gaze` | 8 | 8 | 12 |
| `tongue_place` | 6 | 6 | 6 |
| `cheek_puff`, `jaw_sideways`, `mouth_shift`, `blink`, `cheek_suck`, `lip_tighten` | 2 each | 2 each | 2 each |
| `jaw_thrust`, `chin_raise_upper_lip`, `tongue_out` | 1 each | 1 each | 1 each |
| `pupil_mm` | 2 | none | none |

FB2 fills 12 of the 13 groups. The audit names no FB2 signal for the two pupil diameters. FB2 has no map into or out of the canonical viseme set. All 70 selected FB2 signals are `mapped`, and only the count sentinel is outside the maps. The audit has 70 FB2 rows: 62 `same` and the 8 gaze rows `differs`.

| Loss | In-map | Out-map |
|---|---:|---:|
| FB2 gain and full-activation pose not published | 70 | 70 |
| `fb2_gaze_rotation`: the source describes eye rotation, linear in angle; the canonical value claims no curve | 8 | 8 |
| `fb2_gaze_max_angle_unspecified` | 8 | 8 |
| `fb2_gaze_exclusive`: the canonical set states no exclusivity | 8 | 0 |
| only one of two opposing directions can be non-zero in FB2 | 0 | 12 |
| rounding of up to 2⁻⁵⁴ on the negative knot segment | 0 | 4 |
| the tongue extension has no stated length | 1 | 1 |

The crosswalk evidence is different for each mapping. In each direction, 36 mappings apply an ARKit and FB2 correspondence to the canonical signal, because the audit finds the ARKit definition `same`. In 24 mappings the correspondence does not apply, because the ARKit definition differs (22) or is unresolved (2). The 4 mappings of `cheek_suck_*` and `lip_tighten_*` use the VRCFaceTracking Movement table and a crosswalk in two steps through Godot ([audit](docs/canonical-set-audit.md#crosswalks-of-the-fb2-only-signals)). The 6 `tongue_place` mappings cite no crosswalk. The [FB2 map page](docs/map-sets/fb2.to_rcef_expression.md) lists how many mappings cite each evidence record.

From FB2, a route can reach `arkit.coefficient`, `facs.code`, `openxr.fb2`, `vrcft.artist.base`, `vrcft.eye` and `vrm.preset` ([README.md](README.md#routes)). FB2 is a target of every source of the canonical expression set. META visemes and the VRM vowels also reach FB2 through the viseme pose bridge, which writes only the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`.

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| No maximum gaze angle in any direction. | `xr_fb2` | A map that works in angles, for example to the VRM `look*` presets, which use range maps in degrees. |
| No published gain or full-activation pose. | `xr_fb2` | Any claim that equal weights give equal expressions across providers. |
| Opposing gaze directions are exclusive in FB2. The canonical set states no such constraint. | `xr_fb2` lines 648 to 649 | Exact gaze values toward FB2: when both directions of a pair are non-zero, each output loses up to the smaller value. |
| The figure for `CHEEK_RAISER` (line 535) is not yet an evidence record. | `xr_fb2` | Nothing today. The audit row agrees with the text. |
| Whether `LIPS_TOWARD` acts as a jaw corrective, and what it means when the jaw is closed, is an open question. | [canonical-set.md](docs/canonical-set.md#open-questions) | A settled reading of `lips_toward` against ARKit `mouthClose`. |
| The VRCFaceTracking Movement table labels 5 FB2 rows with a name that is not an OpenXR name, or with a misspelling. | `vrcft_docs_movement` | Use of that table on those 5 mappings in each direction. |

## OpenXR META visemes (`XR_META_face_tracking_visemes`)

### Technical context

`XR_META_face_tracking_visemes` is an optional OpenXR extension that depends on `XR_FB_face_tracking2`. Its enum is `XrFaceTrackingVisemeMETA`. It gives one probability for each of 15 speech classes, silence included. RCEF calls it META visemes.

| Item | Value |
|---|---|
| Profile | `openxr.visemes` ([profiles/openxr.visemes.toml](profiles/openxr.visemes.toml)) |
| Extension text | record [`xr_visemes`](references.md#xr_visemes): `meta_face_tracking_visemes.adoc` in OpenXR-Docs at `5a82d45`, retrieved 2026-10-07 |
| Names and indices | record [`xr_registry`](references.md#xr_registry), enum `XrFaceTrackingVisemeMETA` |
| Reference images | 10 records `xr_visemes_fig_*`, retrieved 2026-10-29: front views of SIL, DD, NN, KK, RR and TH; three-quarter views of RR, CH, OU and SIL. RCEF cites them and does not copy them. |
| Licence | CC-BY-4.0 for the extension text; CC-BY-4.0 for the images, from their Khronos REUSE sidecars |
| Role in maps | source and target |

RCEF records no device that produces META viseme values. The calibration record `viseme-poses.rocketbox-features` fits poses to the viseme shapes of 18 Rocketbox rigs, one shape for each META class. These shapes are sculpted rig shapes, not tracker output.

### Signal structure

Each name has the form `XR_FACE_TRACKING_VISEME_<CLASS>_META`. The class part is a short label, for example `PP` or `AA`. The META text lists English example sounds for each class.

| Index | META class | Example sounds in the META text | Canonical class | Canonical group |
|---:|---|---|---|---|
| 0 | `SIL` | silence; META's table calls it neutral | `sil` | `viseme_rest` |
| 1 | `PP` | p, b, m | `bilabial` | `viseme_consonant` |
| 2 | `FF` | f, v | `labiodental` | `viseme_consonant` |
| 3 | `TH` | th | `dental` | `viseme_consonant` |
| 4 | `DD` | t, d | `coronal_stop` | `viseme_consonant` |
| 5 | `KK` | k, g | `dorsal` | `viseme_consonant` |
| 6 | `CH` | tS, dZ, S | `postalveolar` | `viseme_consonant` |
| 7 | `SS` | s, z | `alveolar_sibilant` | `viseme_consonant` |
| 8 | `NN` | n, l | `coronal_nasal_lateral` | `viseme_consonant` |
| 9 | `RR` | r, as in "red" | `rhotic` | `viseme_consonant` |
| 10 | `AA` | A:, as in "car" | `vowel_open` | `viseme_vowel` |
| 11 | `E` | e, as in "bed" | `vowel_mid_spread` | `viseme_vowel` |
| 12 | `IH` | ih, as in "tip" | `vowel_close_spread` | `viseme_vowel` |
| 13 | `OH` | oh, as in "toe" | `vowel_mid_rounded` | `viseme_vowel` |
| 14 | `OU` | ou, as in "book" | `vowel_close_rounded` | `viseme_vowel` |

The profile has 15 rows, and all 15 are selected and `mapped`. RCEF records no count sentinel and no ancillary rows for this enum. Every row has `side = "shared"`, the region other, units `probability` and `coupling = "probability_simplex"`. The validity flag is `isValid`, separate from the FB2 flags. The confidence field reads "not provided", and the time stamp is `XrTime`.

| Metadata field | Value | Meaning |
|---|---|---|
| `optional_feature` | `true` | the extension is optional |
| `depends_on` | `XR_FB_face_tracking2` | the extension needs FB2 |
| `valid_sum` | `1.0` | the 15 values sum to 1 when the frame is valid |
| `invalid_array_zero` | `true` | an invalid frame has all values at 0 |
| `silence_valid` | `true` on `SIL`, `false` on the other 14 rows | silence is a valid frame, different from an invalid one |

### Values, neutral and calibration

| Property | What RCEF records |
|---|---|
| Range | Each value is a probability from 0 to 1. The values sum to 1 when `isValid` is true (`xr_visemes` lines 104 to 107). |
| Invalid frames and silence | An invalid frame has all 15 values at 0. A valid silent frame sums to 1, as every valid frame does. The META in-map refuses an invalid frame, so it never becomes `sil`. |
| Neutral | No row has a `neutral` field. The rest class of the canonical viseme set is `sil = 1`, which means no speech articulation. |
| The SIL pose | META's reference image for SIL shows the lips together and relaxed (record `xr_visemes_fig_sil`). The JALI paper notes that pauses usually leave the mouth open (record `jali_2016`). RCEF asserts no mouth pose for `sil`, and the rig chooses. |
| Calibration string | `openxr.visemes: native basis; no canonical calibration established` on every row. |

Every META mapping states the loss "META gain and full-activation pose not published". RCEF has no evidence of how a META probability relates to a mouth shape on a face. The viseme pose bridge uses poses that the record `viseme-poses.rocketbox-features` fits to rig geometry. In that record, 11 of 15 classes pass on all 4 held-out rigs: 7 by the shape gate and 4 by the perceptual gate. `labiodental`, `postalveolar`, `coronal_nasal_lateral` and `rhotic` fail. The record is software-only.

### Mapping to the canonical sets

| Map | Direction | Mappings | Parts | Evidence status |
|---|---|---:|---:|---|
| [`visemes.to_rcef_viseme`](docs/map-sets/visemes.to_rcef_viseme.md) | `openxr.visemes` → `rcef.canonical_viseme` | 17 | 4 | `proposed` (17) |
| [`rcef_viseme.to_visemes`](docs/map-sets/rcef_viseme.to_visemes.md) | `rcef.canonical_viseme` → `openxr.visemes` | 15 | 3 | `proposed` (15) |

| Part | Canonical signals | In-map mappings | Out-map mappings |
|---|---:|---:|---:|
| `viseme_vowel` | 5 | 5 copies | 5 copies |
| `viseme_consonant` | 9 | 9 copies | 9 copies |
| `viseme_rest` | 1 | 1 copy | 1 copy |
| `viseme_aggregate` | 1 | 2 | none |

The canonical classes contain the META classes one to one, so 15 mappings in each direction are copies. The aggregate part writes `alveolar_floor` in two steps. A weighted sum of `SS`, `DD`, `NN` and `RR`, each with the weight 1, goes into one helper value. Then the clamp knots (0, 0), (1, 1) and (4, 1) limit it to 1. META has no class for `alveolar_floor`, so the out-map has no aggregate part, and no map reads `alveolar_floor`.

Every mapping cites `xr_visemes`, `xr_registry`, `ipa_chart_doulos_2020` and `rcef_canonical_v1`. The audit has 16 META rows: 15 `same`, and `alveolar_floor` as `differs`. One more row, the scope of META's classes, is `unresolved`.

| Loss | In-map | Out-map |
|---|---:|---:|
| META gain and full-activation pose not published | 17 | 15 |
| `meta_viseme_class_scope`: the META text does not state the class of IPA sounds outside its examples; RCEF assigns them by shape | 15 | 15 |
| `meta_viseme_aggregate_sum`: sum of the listed classes, clamped at 1 | 2 | 0 |
| from a source other than META: consonant and rest classes not produced; the META validity contract is not met | 0 | 5 |

META visemes reach `openxr.visemes` and `vrm.preset` through the canonical viseme set. Through the viseme pose bridge and the canonical expression set, they also reach `arkit.coefficient`, `facs.code`, `openxr.fb2` and `vrcft.artist.base` ([README.md](README.md#routes)).

| Route | What happens |
|---|---|
| To VRM | Only the five vowels have VRM presets, so the route reads META's vowels only. The VRM out-map drops the consonant and rest classes, so the outputs no longer sum to 1. The map states this loss. No published table maps META visemes to VRM presets, and the correspondence rests on phoneme labels only. |
| Through the bridge | The bridge reads the 11 classes that pass, and it writes 45 expression signals in the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`. The 4 classes that fail move nothing, and the route lists their values as dropped. |
| Back to META from another source | Only the vowel outputs get values. The route writes no `isValid`, and it labels the frame "META validity not asserted". |

RCEF has no map from the canonical expression set to the canonical viseme set, because a face pose does not identify the sound.

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| META gives English example sounds only. The text does not state the class of other IPA sounds. | `xr_visemes` lines 142 to 245 | A verified class for any sound outside the examples. RCEF assigns them by shape, with the key `meta_viseme_class_scope`. |
| META shows `DD`, `KK` and `NN` in isolation with the teeth close. RCEF's classes have no front target of their own. | `xr_visemes_fig_dd`, `_kk`, `_nn` | Use of these images as the pose of the class. RCEF reads each one as a rig choice. |
| The `RR` images show no clear lip protrusion from the front and slight protrusion in the three-quarter view, on one speaker. | `xr_visemes_fig_rr`, `xr_visemes_fig_rr_rot` | Strong evidence for the lip shape of `rhotic`. |
| The split of tap ɾ (`coronal_stop`) from trill r (`rhotic`) follows META, with no shape evidence. | [canonical-set.md](docs/canonical-set.md#open-questions) | A shape basis for that split. |
| The META SIL image and the JALI paper disagree on the mouth at rest. | `xr_visemes_fig_sil`, `jali_2016` | A pose for `sil` that holds for every rig. |
| The bridge poses come from one rig library. On ICT-FaceKit, the bridged `bilabial` pose opens the lips by about 2.3 mm. | [canonical-set.md](docs/canonical-set.md#viseme-pose-bridge) | Use of the bridge poses on rigs from other libraries. |
| RCEF has no operator over time. | [canonical-set.md](docs/canonical-set.md#what-a-viseme-value-means) | Coarticulation: the lips of `coronal_stop`, `coronal_nasal_lateral`, `dorsal` and `rhotic` follow the neighbouring vowel. |

## VRCFaceTracking

### Technical context

VRCFaceTracking is an open-source project. Its code repository, `benaclejames/VRCFaceTracking`, is under Apache-2.0 (record [`vrcft_license`](references.md#vrcft_license)). The code defines Unified Expressions, a set of face expression shapes, and a structure for eye data. The project documentation tells avatar artists which shapes to make, and lists the avatar parameters that the project sends.

RCEF records VRCFaceTracking in seven profiles. RCEF pins the code at commit `6432e6a`. It pins the documentation pages by the SHA-256 of the bytes that it retrieved on 2026-10-07.

| Profile | What it records | Rows | Selected entries | Evidence records | Licence of the source, as RCEF records it |
|---|---|---:|---:|---|---|
| `vrcft.transport` | the `UnifiedExpressions` enum in the code | 89 | 88 | [`vrcft_enum`](references.md#vrcft_enum), [`vrcft_data`](references.md#vrcft_data) | Apache-2.0 |
| `vrcft.eye` | raw and combined eye data in `UnifiedData.cs` | 20 | 12 | [`vrcft_data`](references.md#vrcft_data) | Apache-2.0 |
| `vrcft.artist.base` | base shapes in the artist tables | 102 | 102 | [`vrcft_artist`](references.md#vrcft_artist) | documentation with no published licence; reference only |
| `vrcft.artist.blended` | blended shapes in the artist tables | 42 | 42 | [`vrcft_artist`](references.md#vrcft_artist) | as above |
| `vrcft.parameter.float` | numeric avatar parameters (`v2/*`) | 124 | 124 | [`vrcft_parameters`](references.md#vrcft_parameters), [`vrcft_float`](references.md#vrcft_float) | as above |
| `vrcft.parameter.flags` | tracking activity flags | 3 | 3 | [`vrcft_parameters`](references.md#vrcft_parameters), [`vrcft_float`](references.md#vrcft_float) | as above |
| `vrcft.parameter.encoding` | the binary parameter encoding | 7 | 0 | [`vrcft_binary`](references.md#vrcft_binary) | as above |

The maps also cite four documentation tables at docs commit `3036f46`, retrieved 2026-10-26. They are the shape descriptions (`vrcft_docs_shapes`) and an overview table (`vrcft_docs_overview`). The other two relate the names to ARKit (`vrcft_docs_arkit`) and to Meta Movement, which is FB2 (`vrcft_docs_movement`). These records are reference only.

Two more code records at `6432e6a` give weights: `vrcft_code_parameters` and `vrcft_simple_expressions`. Three figure records (`vrcft_fig_eyeclosedleft`, `vrcft_fig_eyelookoutleft`, `vrcft_fig_mouthupperleft`) settle the side frame.

### Signal structure

The names are in upper camel case. A sided name ends in `Right` or `Left`, for example `EyeSquintRight`. The same names occur in the transport enum and in the artist tables. RCEF checked the selected names and their order against the pinned bytes ([REVIEW.md](REVIEW.md)).

| Profile | Rows by disposition | Sides (right / left / shared), all rows | Regions, all rows |
|---|---|---|---|
| `vrcft.transport` | 88 `unresolved`, 1 `excluded` | 35 / 35 / 19 | mouth 41, tongue 12, brow 8, jaw 7, nose 6, cheek 6, other 5, eyelid 4 |
| `vrcft.eye` | 4 `mapped`, 8 `unresolved`, 8 `excluded` | 4 / 4 / 8, and 4 with no side | eyelid 7, gaze 6, pupil 3, and 4 with no region |
| `vrcft.artist.base` | 72 `mapped`, 26 `unresolved`, 4 `unsupported` | 42 / 42 / 18 | mouth 41, tongue 12, gaze 8, eyelid 8, brow 8, jaw 7, nose 6, cheek 6, other 4, pupil 2 |
| `vrcft.artist.blended` | 42 `unresolved` | 5 / 5 / 32 | mouth 24, brow 7, eyelid 4, nose 3, cheek 3, pupil 1 |
| `vrcft.parameter.float` | 124 `unresolved` | 39 / 39 / 46 | mouth 56, brow 16, other 10, tongue 8, nose 7, gaze 6, eyelid 6, cheek 6, jaw 5, pupil 4 |
| `vrcft.parameter.flags` | 3 `excluded` | 0 / 0 / 3 | eyelid 1, mouth 1, other 1 |
| `vrcft.parameter.encoding` | 7 `excluded` | 0 / 0 / 7 | other 6, jaw 1 |

The transport enum has 88 expression names and the sentinel `Max` (record `vrcft_enum`). `Max` is `excluded`, because it sets the size of storage and is not an expression. The serialized frame is 102 bytes. Bytes 0 to 9 hold eye data, bytes 10 to 13 are reserved, and the expressions start at byte 14. The legacy enum `SRanipal_LipShape_v2` is an internal compatibility enum, so RCEF leaves it out of the selected transport.

The 102 base artist shapes are the 88 transport names plus 14 eye names: 8 `EyeLook*` directions, 2 `EyeClosed*`, 2 `EyeDilation*` and 2 `EyeConstrict*`. Each of the 42 blended shapes has a list of base components, with the coupling `composite`. RCEF records the composition operator as "unspecified; list is not executable". The list for `EyeWide` is empty. Footnote 1 of the artist page marks 4 base shapes as unused by all interfaces at retrieval: `SoftPalateClose`, `ThroatSwallow`, `NeckFlexRight` and `NeckFlexLeft`. RCEF keeps them as `unsupported` vocabulary.

The 12 selected eye entries are `Gaze.x`, `Gaze.y`, `Openness` and `PupilDiameter_MM`, for `Left`, `Right` and `Combined`. The 4 reserved bytes 10 to 13 and the 4 state fields of the combined pupil normalization (`_maxDilation`, `_minDilation`, `_leftDiameter`, `_rightDiameter`) are `excluded` ancillary rows. The 4 combined entries have the coupling `bilateral_shared`.

The 124 numeric parameters come from 15 tables of the parameter page, and the 3 flags from a 16th table. Every parameter allows an optional prefix. 36 parameters have the coupling `composite`, for example `v2/BrowExpression` and `v2/SmileSad`. RCEF does not guess parameters that the page does not list. The flags are `EyeTrackingActive`, `ExpressionTrackingActive` and `LipTrackingActive`. They are booleans that the project sends on load or when a tracking module changes state.

The 7 encoding rows are `ParameterNegative`, the bit parameters `Parameter1`, `Parameter2`, `Parameter4` and `Parameter8`, the placeholder `Parameterx` and the page's example `JawForward1`. They describe bit and sign operations on booleans. The scalar pack cannot hold these, so they are `excluded`.

The Unified Expressions figures show the subject's own side: `EyeClosedLeft` closes the eye on the viewer's right ([audit](docs/canonical-set-audit.md#frames-whose-left)). So the artist shapes use the subject's own side. The eye data takes the same frame, because the project computes `v2/EyeClosedLeft` as 1 − `Left.Openness` (`vrcft_code_parameters` line 40). The audit has no frame row for the transport enum or the avatar parameters, so RCEF takes their side from the name.

### Values, neutral and calibration

| Profile or field | Units | Range recorded | Neutral or default recorded |
|---|---|---|---|
| `vrcft.transport` | `1` | none | native default 0.0 |
| `vrcft.eye`, `Openness` | `1` | none | native default 1.0; not a measured neutral |
| `vrcft.eye`, raw `PupilDiameter_MM` | `mm` | none | none |
| `vrcft.eye`, `Combined.PupilDiameter_MM` | `1` (normalized dilation) | 0 to 1 | none; NaN becomes 0.5 |
| `vrcft.eye`, `Gaze.x` and `Gaze.y` | `unknown` | none | none |
| `vrcft.artist.base`, `vrcft.artist.blended` | `unknown` | none | none |
| `vrcft.parameter.float` | `1` (121), `cm` (3) | 0 to 1 (97), −1 to 1 (27) | none |

To serialize the transport, the code scales each value by 255, clamps it and truncates it to one byte. RCEF records this as inventory (`byte_scale`, `byte_clamped`, `byte_quantization`). It is not a runtime operation in any map.

`Openness` starts at 1. No source says that this start value is the open, resting eye, so RCEF has no evidence for that point. The raw pupil fields hold millimetres. An earlier RCEF version set a positive domain on them. No source supports a domain, so RCEF removed it and adds no clamp ([REVIEW.md](REVIEW.md)).

The combined pupil field has the same name as the raw fields. It holds a normalized dilation, which the code computes from a minimum and a maximum that change at run time. The parameter page gives the pupil parameters in centimetres. RCEF records the three quantities separately and infers no identity between them.

On the three `v2/EyeLid*` parameters, RCEF records the value 0.75 as `openness_widen_boundary`. The 27 parameters with the range −1 to 1 include `v2/CheekPuffSuckLeft`, `v2/JawX` and `v2/TongueY`. Raw gaze units are unresolved. The documentation does not establish that the avatar parameters have the same calibration as the transport or the artist shapes (record `vrcft_float`).

### Mapping to the canonical sets

| Map | Direction | Mappings | Parts | Evidence status |
|---|---|---:|---:|---|
| [`vrcft_eye.to_rcef_expression`](docs/map-sets/vrcft_eye.to_rcef_expression.md) | `vrcft.eye` → `rcef.canonical_expression` | 4 | 2 | 2 `proposed`, 2 `verified_current` |
| [`rcef_expression.to_vrcft_eye`](docs/map-sets/rcef_expression.to_vrcft_eye.md) | `rcef.canonical_expression` → `vrcft.eye` | 4 | 2 | 2 `proposed`, 2 `verified_current` |
| [`rcef_expression.to_vrcft_artist`](docs/map-sets/rcef_expression.to_vrcft_artist.md) | `rcef.canonical_expression` → `vrcft.artist.base` | 72 | 11 | `proposed` (72) |

Both eye maps fill the groups `blink` and `pupil_mm`. In `blink`, `eye_close` is 1 − `Openness` (affine −1, 1). An `Openness` outside 0 to 1 gives a canonical value outside 0 to 1, and msf-character-tools refuses it (`E_DOMAIN`). These 2 mappings in each direction state the loss key `vrcft_eye_openness_neutral_unresolved` and the loss "VRCFaceTracking eye gain and full-activation pose not published".

In `pupil_mm`, the maps copy the left and right diameters in millimetres. These 4 copies are the only `exact` and `verified_current` mappings in the maps of the canonical sets. The eye maps do not fill `gaze`, because the raw gaze units are unresolved. The combined entries need a policy for state and validity, so no map reads them.

The Unified Expressions out-map writes the 72 `mapped` base shapes, one mapping each. Every mapping is a copy (affine 1, 0) and states the loss "Unified Expressions gain and full-activation pose not published".

| Part | Canonical signals | Mappings | Notes |
|---|---|---:|---|
| `face` | 41 of 41 | 47 | brow lower, lip corner pull and lip pucker each write two shapes per side |
| `cheek_puff` | 2 of 2 | 2 | |
| `jaw_thrust` | 1 of 1 | 1 | |
| `jaw_sideways` | 2 of 2 | 2 | |
| `mouth_shift` | 2 of 2 | 4 | `MouthUpper*` and `MouthLower*` |
| `chin_raise_upper_lip` | 1 of 1 | 1 | |
| `blink` | 2 of 2 | 2 | |
| `gaze` | 8 of 8 | 8 | loss key `vrcft_ue_gaze_no_angle` |
| `tongue_out` | 1 of 1 | 1 | |
| `cheek_suck` | 2 of 2 | 2 | crosswalk in two steps through Godot |
| `lip_tighten` | 2 of 2 | 2 | crosswalk in two steps through Godot |

In 16 mappings, one canonical signal writes two Unified Expressions shapes. These mappings state the loss key `vrcft_ue_set_equal`. The source splits one action into two shapes and gives no ratio, so the out-map sets both shapes equal. For brow lower and smile, the code defines the simple expression as 0.75 and 0.25, or 0.8 and 0.2, of its two shapes (`vrcft_simple_expressions`). These weights add up to 1, so equal shapes give the canonical value back. The out-map has no `tongue_place` part and no `pupil_mm` part, because the audit names no base shape for those canonical signals.

The audit has 64 Unified Expressions rows: 39 `same`, 23 `differs` and 2 `unresolved`. It has 4 rows for the eye data: 2 `same` and 2 `unresolved`.

| Signals that no map reads or writes | Disposition | Reason that RCEF records |
|---|---|---|
| 26 base shapes: `EyeDilation*`, `EyeConstrict*`, `NasalDilation*`, `NasalConstrict*`, `JawBackward`, `JawClench`, `JawMandibleRaise`, `LipSuckCorner*`, `MouthUpperDeepen*` and 11 tongue shapes | `unresolved` | no canonical signal and no calibration evidence |
| 4 footnoted base shapes | `unsupported` | marked unused by all interfaces at retrieval |
| 42 blended shapes | `unresolved` | component lists give no weights; 2 also have a side conflict |
| 88 transport names | `unresolved` | enum presence does not show device availability or calibration |
| 124 avatar parameters | `unresolved` | no equivalence with the transport or artist calibration; 2 also have a side conflict |
| 3 flags, 7 encoding rows, `Max` | `excluded` | booleans, bit operations or a sentinel |

RCEF has no in-map from Unified Expressions yet. The plan puts the in-maps in phase 2 ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). They need new IDs for the split shapes and weights for the blended shapes.

Data 0.5.0 retired the direct map `arkit.to_vrcft_artist`. On the pair that it translated, the route through the canonical expression set gives the same weights (A/B metric M1, [ab/README.md](ab/README.md)). The A/B report M8 R3 compares FB2 → Unified Expressions with the Godot route ([Godot](#godot)).

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| The source does not state the raw gaze units. | `vrcft.eye` metadata `raw_gaze_units = "unresolved"` | A `gaze` part in the eye maps. |
| The code always averages the two eyes for combined gaze. The documentation describes a result that depends on validity. | `vrcft_data`; `combined_gaze_documentation_conflicts_with_code` | Any map of the combined entries. |
| No source states the meaning of `Openness` 1. | loss key `vrcft_eye_openness_neutral_unresolved` | A `verified_current` blink mapping. |
| Raw pupil millimetres, combined normalized dilation and parameter centimetres have similar names. | `vrcft_data`, `vrcft_parameters` | An identity between the pupil fields. |
| `MouthLowerDown*`: the name and the artist wording give opposite directions. | loss key `vrcft_ue_mouthlowerdown_direction_unresolved` | A `same` verdict. The 2 mappings state the loss. |
| `MouthSadRight` and `MouthSadLeft`: the side wording conflicts with the name and the components. | `vrcft_artist` | A derived rule for these blended shapes. |
| `v2/NasalConstrictRight` and `v2/NasalConstrictLeft`: the parameter wording swaps the sides. | `vrcft_parameters` | A side for these parameters. |
| The binary page gives a `2^N-1` range and also `1/2^N` bit values. | `vrcft_binary` | Any execution of the encoding. |
| The Movement table has known side and spelling errors. It names FB2 weights `EYES_LOOK_IN/OUT_*` that the OpenXR registry does not have. | `vrcft_docs_movement`; [docs/godot_comparison.md](docs/godot_comparison.md) | Use of that table to settle sides. |
| The source defines `MouthClosed` relative to `JawOpen`. | loss key `vrcft_ue_mouthclosed_jaw_relative` | A `same` verdict for `lips_toward`. |
| The source publishes no gain and no full-activation pose. | every Unified Expressions mapping | Calibrated values. |

The footnote says that no interface used the four shapes at the retrieval date. This is a fact about the source at that date. It does not say that nobody can use the shapes. The shapes with no FB2 counterpart, for example pupil dilation, the tongue directions and `TongueFlat`, have no map yet ([README.md](README.md#not-translated-yet-planned)).

## Godot

### Technical context

Godot is an open-source engine under the MIT licence. Its `XRFaceTracker` class holds face tracking values as blend-shape weights, one for each entry of the enum `BlendShapeEntry`. Other Godot code writes and reads these values. The Godot OpenXR vendors plugin sets the Godot shapes from FB2 weights, directly or as the mean of two weights (record [`godot_vendors_fb2`](references.md#godot_vendors_fb2)). The face modifier relates each Godot shape to Unified Expressions, ARKit, SRanipal and Meta names, and drives the shapes of an avatar mesh ([`godot_face_modifier`](references.md#godot_face_modifier)).

| Evidence record | File | Pinned revision | What RCEF takes from it | Licence |
|---|---|---|---|---|
| [`godot_enum`](references.md#godot_enum) | `servers/xr/xr_face_tracker.h` | Godot `e7b12e7` | the 102 base and 41 blended names, their indices and `FT_MAX` | MIT |
| [`godot_setters`](references.md#godot_setters) | `servers/xr/xr_face_tracker.cpp` | Godot `e7b12e7` | the array starts at zero; the setters store values with no clamp | MIT |
| [`godot_face_modifier`](references.md#godot_face_modifier) | `scene/3d/xr/xr_face_modifier_3d.cpp` | Godot `e7b12e7` | the name table against other sets | MIT |
| [`godot_vendors_fb2`](references.md#godot_vendors_fb2) | `openxr_fb_face_tracking_extension.cpp` | godot_openxr_vendors `b0654f1` | how each FB2 weight sets a Godot shape | MIT |

An enum entry does not show that a device supports it, so RCEF infers no device for any value.

### Signal structure

The names are upper case with underscores and the prefix `FT_`, for example `FT_EYE_SQUINT_RIGHT`. A sided name ends in `_RIGHT` or `_LEFT`. The Godot source states that the shapes come from Unified Expressions (`godot_enum` lines 38 to 40).

| Profile | Native indices | Rows | Selected entries | Dispositions | Sides of the selected entries (right / left / shared) |
|---|---|---:|---:|---|---|
| `godot.base` | 0 to 101 | 102 | 102 | 102 `unresolved` | 42 / 42 / 18 |
| `godot.blended` | 102 to 143 | 42 | 41 | 41 `unresolved`, 1 `excluded` | 5 / 5 / 31 |

The base list has the names and the order of the Unified Expressions base shapes, with one difference. Index 92 is `FT_TONGUE_BLEND_DOWN`, where Unified Expressions has `TongueBendDown`. RCEF keeps the Godot spelling (`native_spelling_retained`). The base regions have the same counts as those of `vrcft.artist.base`.

The blended list has the Unified Expressions blended names except `BrowInnerUp`, so it has 41 shapes and not 42. Index 143 is the sentinel `FT_MAX`. It is `excluded`, because it is not a sampled blend shape. RCEF records no components for the Godot blended shapes.

The special entries are the 8 gaze directions (`FT_EYE_LOOK_*`), the 12 tongue shapes, and pupil dilation and constriction. RCEF records no validity flag for Godot.

RCEF takes the side from the name. The audit has no frame row for Godot, because no Godot map exists. The Godot names follow Unified Expressions, whose figures show the subject's own side. RCEF does not apply that frame to Godot without a Godot source.

### Values, neutral and calibration

| Property | What RCEF records |
|---|---|
| Value type and units | scalar, units `unknown` |
| Range | none; the setters store any float with no clamp (`setters_clamp = false` on every row) |
| Default | native default 0.0, because the array starts at zero; this is initialization, not a measured neutral |
| Meaning of 1 | not stated by the enum or the setters |
| Calibration string | `godot.base: native basis; no canonical calibration established`, and the same for `godot.blended` |

The enum and the store give no numeric calibration and no device availability. The vendors plugin writes FB2 weights into the store unchanged or as a mean of two (`godot_vendors_fb2`). So values that come from FB2 keep the FB2 basis. RCEF records no such fact for other producers.

### Mapping to the canonical sets

Godot has no map in data 0.5.0. Both profiles are inventory only. The plan puts Godot out-maps in phase 2 and in-maps in phase 3 ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). Godot still needs audit rows with a frame verdict from a Godot source, a capability row and the maps. A map that reads or writes the blended shapes also needs their weights.

Godot sources are evidence for other maps:

| Use | Evidence | Count |
|---|---|---:|
| correspondence for the Unified Expressions out-map | `godot_face_modifier` | 72 of 72 mappings |
| crosswalk in two steps for `cheek_suck_*` and `lip_tighten_*` (FB2 → Godot shape → Unified Expressions name) | `godot_vendors_fb2`, `godot_enum` | 4 mappings in each FB2 map and in the Unified Expressions out-map |
| comparison of RCEF's FB2 → ARKit route with Godot ([docs/godot_comparison.md](docs/godot_comparison.md)) | `godot_vendors_fb2`, `godot_face_modifier` | 52 ARKit coefficients |
| A/B reference R3, FB2 → Unified Expressions as Godot computes it ([ab/README.md](ab/README.md)) | `godot_vendors_fb2`, `godot_face_modifier` | 73 shapes |

In the comparison, RCEF's FB2 → ARKit weights agree with Godot on every coefficient that Godot routes. Godot has no route for `browInnerUp`, and RCEF uses VRCFaceTracking's mean of the two inner brow raisers.

In the A/B report M8 R3, 256 of 292 outputs are exact, and the other 36 are listed departures on 9 shapes. RCEF departs from Godot on these 9 shapes by design. Godot leaves `BrowPinch*`, `MouthCornerSlant*`, `MouthUpper*` and `MouthLower*` at 0 when it sets the blended shape, and RCEF copies the canonical value into each shape. Godot fills `TongueFlat` from `TONGUE_RETREAT`. RCEF does not map these two (`godot_vendors_fb2` line 296). In Unified Expressions the tongue flattens and thins (`vrcft_docs_shapes` line 507), while `tongue_retreat` moves the tongue back.

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| Godot spells index 92 `FT_TONGUE_BLEND_DOWN`, and Unified Expressions has `TongueBendDown`. | `godot_enum` | Nothing. RCEF keeps the spelling. |
| The blended list has no `BrowInnerUp`, which Unified Expressions has. | `godot_enum`, `vrcft_artist` | A name-for-name copy of the blended lists. |
| The source states no range, unit or meaning of 1, and the setters do not clamp. | `godot_setters` | Calibrated values. |
| An enum entry does not show which device writes which value. | `godot_enum` | A statement of device support. |
| No Godot source settles the side frame. | no audit row | The audit rows that a Godot map needs. |
| Godot names the ARKit coefficients for mouth shift. VRCFaceTracking's ARKit table has no row for them. | assumption `evidence.godot_only_mouth_shift` | Nothing in Godot. The note is on the ARKit, FB2 and Unified Expressions maps. |

## VRM

### Technical context

VRM 1.0 is a file format for humanoid avatars. Its `VRMC_vrm` extension defines expressions and lookAt. An expression is a named weight that the author of a model binds to morph targets, material colours and texture transforms. An application sets the weight. The VRM runtime then applies the binds, the `isBinary` setting and the overrides.

RCEF reads VRM values as asset weights, not as tracker output. RCEF records no particular application that sets them.

| Item | Value |
|---|---|
| Profile | `vrm.preset` ([profiles/vrm.preset.toml](profiles/vrm.preset.toml)) |
| Expressions | record [`vrm_expressions`](references.md#vrm_expressions): `expressions.md` in vrm-specification at `94e82dd`, retrieved 2026-10-07 |
| LookAt | record [`vrm_lookat`](references.md#vrm_lookat): `lookAt.md` at the same commit, retrieved 2026-10-07 |
| Holders named in RCEF's notices | VRM Consortium and vrm-c contributors |
| Licence or terms | reference only; source prose not redistributed; permission to redistribute the specification prose is unresolved |
| Role in maps | source and target |

Permission to redistribute the specification prose is unresolved. So RCEF links to the specification and does not copy its prose, code examples or figures. The record `vrm_expressions` states that all 18 presets are optional, and that the specification also allows custom expression names. RCEF records the presets only.

### Signal structure

The 18 presets have the inventory ordinals 0 to 17, their positions in the documentation list. Every row cites `vrm_expressions` and `vrm_lookat`, and has `optional = true` and `coupling = "asset_specific"`.

| Ordinals | Presets | Side in the profile | Region | Disposition |
|---|---|---|---|---|
| 0 to 4 | `happy`, `angry`, `sad`, `relaxed`, `surprised` | shared | other | `unresolved` |
| 5 to 9 | `aa`, `ih`, `ou`, `ee`, `oh` | shared | other | `mapped` |
| 10 | `blink` | shared | eyelid | `unresolved` |
| 11, 12 | `blinkLeft`, `blinkRight` | left, right | eyelid | `mapped` |
| 13, 14 | `lookUp`, `lookDown` | shared | gaze | `unresolved` |
| 15, 16 | `lookLeft`, `lookRight` | left, right | gaze | `unresolved` |
| 17 | `neutral` | shared | other | `unresolved` |

Of the 18 rows, 7 are `mapped` and 11 are `unresolved`. VRM rows have no validity, confidence or time fields, and no count sentinel.

Each row records the binding and runtime fields of the specification as metadata:

| Field group | What the profile records |
|---|---|
| Bindings | `morphTargetBinds`, `materialColorBinds`, `textureTransformBinds` |
| Morph target bind | `node`, `index`, `weight`; the weight domain is 0 to 1 |
| Material colour bind | `material`, `type`, `targetValue` (4 components); six colour types: `color`, `emissionColor`, `shadeColor`, `matcapColor`, `rimColor`, `outlineColor` |
| Texture transform bind | `material`, `scale` (default 1, 1), `offset` (default 0, 0) |
| `isBinary` | threshold 0.5 with the comparison `>`; the inputs 0.49, 0.5 and 0.51 give 0, 0 and 1 |
| Overrides | `overrideMouth`, `overrideBlink`, `overrideLookAt`, each `none`, `block` or `blend`; overrides act after the binary decision; the application defines the scope of custom overrides |
| LookAt | the range map fields `inputMaxValue` and `outputScale`; for the expression type, the horizontal map field `rangeMapHorizontalOuter` |
| Clamp | "specified by VRM; not implicit in RCEF rules" |

VRM gives no normative side. The audit marks both blink rows unresolved, with the key `vrm_blink_side_unresolved`. RCEF reads `blinkLeft` and `blinkRight` as the subject's own left and right, as an assumption. The mappings keep a caveat: on the VRM 1.0 Twist sample, `blinkLeft` moves the avatar's own left eyelid.

The profile metadata sets `lookat_shared_direction = true`. LookAt describes one line of sight for both eyes, so it cannot describe two eyes that point in different directions (record `vrm_lookat`).

### Values, neutral and calibration

| Property | What RCEF records |
|---|---|
| Range | Every preset has the units `1` and the domain 0 to 1. |
| 0 and 1 | The calibration string of each row is `vrm1.preset:<name>: asset-authored binding weights`. The face that a weight gives depends on the binds of each model. So RCEF records no meaning of 0 or 1 that holds across models. |
| Neutral | No VRM row has a `neutral` field. VRM has a preset named `neutral`, which RCEF records as an `unresolved` row. |
| Binary presets | A model can mark a preset `isBinary`. The preset then gives 1 only when the weight is strictly above 0.5, and 0 otherwise. |
| Execution | The profile metadata reads "unsupported; bindings and override order require asset semantics". RCEF does not run binds, materials or overrides. |
| Gaze presets | VRM drives the `look*` presets by angle, through range maps whose input is in degrees. Each model sets its own range maps. |

No source states how a VRM weight compares with a tracker weight. The VRM maps read an asset weight as a canonical value, and a canonical value as an asset weight, and state this as a loss. No calibration record reads VRM bindings. The five vowel presets drive the viseme pose bridge, whose poses come from Rocketbox rigs.

### Mapping to the canonical sets

VRM has four maps, two into and two out of the canonical sets. Every mapping is a copy (affine 1, 0) with the evidence status `proposed`.

| Map | Direction | Mappings | Part |
|---|---|---:|---|
| [`vrm.to_rcef_expression`](docs/map-sets/vrm.to_rcef_expression.md) | `vrm.preset` → `rcef.canonical_expression` | 2 | `blink` |
| [`rcef_expression.to_vrm`](docs/map-sets/rcef_expression.to_vrm.md) | `rcef.canonical_expression` → `vrm.preset` | 2 | `blink` |
| [`vrm.to_rcef_viseme`](docs/map-sets/vrm.to_rcef_viseme.md) | `vrm.preset` → `rcef.canonical_viseme` | 5 | `viseme_vowel` |
| [`rcef_viseme.to_vrm`](docs/map-sets/rcef_viseme.to_vrm.md) | `rcef.canonical_viseme` → `vrm.preset` | 5 | `viseme_vowel` |

In the canonical expression set, VRM fills only `blink`, from `blinkLeft` and `blinkRight`. In the canonical viseme set, VRM fills only `viseme_vowel`:

| VRM preset | Remark in the specification | Canonical class |
|---|---|---|
| `aa` | "aa" | `vowel_open` |
| `ih` | "i" | `vowel_close_spread` |
| `ou` | "u" | `vowel_close_rounded` |
| `ee` | "eh" | `vowel_mid_spread` |
| `oh` | "oh" | `vowel_mid_rounded` |

VRM has no consonant classes and no `sil`, so it does not fill `viseme_consonant`, `viseme_rest` or `viseme_aggregate`. The audit has 7 VRM rows: the 5 vowels `differs` and the 2 blinks `unresolved`.

| Loss | Maps that state it |
|---|---|
| `vrm_blink_side_unresolved` | both blink maps (2 mappings each) |
| an asset-authored expression weight becomes a canonical value, or the reverse | both blink maps |
| VRM `blink` (both eyes) not read; when a model drives only `blink`, `eye_close` reads open | `vrm.to_rcef_expression` |
| VRM `blink` is left unset, so a model that binds only `blink` does not blink | `rcef_expression.to_vrm` |
| a model may mark the preset `isBinary`, which turns a partial closure into fully open or fully closed | `rcef_expression.to_vrm` |
| `vrm_vowel_asset_weight`: asset weights read as probabilities, with no sum constraint and no `sil` | both vowel maps (5 mappings each) |
| `vrm_ih_vowel_quality`: META IH and VRM `ih` are different vowels in one shape class | both vowel maps (1 mapping each) |
| consonant and rest classes are dropped, so the outputs no longer sum to 1 | `rcef_viseme.to_vrm` |

The 4 blink mappings also state that the correspondence is definitional only: the definitions agree, but no published table maps another set to VRM (`vrm.definitional_only`). Only the 5 mappings of `rcef_viseme.to_vrm` state that the vowel correspondence rests on phoneme labels only (`vrm.phoneme_label_only`). The two out-maps state that `isBinary` and the overrides act in the VRM runtime, and RCEF does not model them (`vrm.downstream_effects`).

VRM appears in three rows of the [Routes](README.md#routes) table. Its blinks go through the canonical expression set to six targets. Its vowels go through the canonical viseme set to META visemes and VRM. Through the viseme pose bridge, its vowels also reach ARKit, FACS codes, FB2 and Unified Expressions.

| Presets with no map | Reason that RCEF records |
|---|---|
| `blink` | The in-map reads only the presets for one eye, and a route lists a non-zero `blink` as dropped. The out-map leaves `blink` unset. |
| `lookUp`, `lookDown`, `lookLeft`, `lookRight` | VRM drives gaze by angle, through range maps in degrees. FB2 and ARKit publish no maximum angle. A translation needs an operator for angles and curves. |
| `happy`, `angry`, `sad`, `relaxed`, `surprised` | To turn face movements into an emotion label is a classification, not a linear calculation. Each model also authors its own binds. |
| `neutral` | The general reason: canonical calibration and executable mapping remain unresolved. |

The plan lists the VRM emotion and `look*` presets as not planned ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)).

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| VRM gives no normative side for `blinkLeft` and `blinkRight`. | `vrm_expressions` | A verified side. RCEF reads the subject's own side as an assumption. |
| The profile records `side = "left"` on `blinkLeft` with no caveat, while the audit marks the side unresolved. | [audit](docs/canonical-set-audit.md#frames-whose-left) | Nothing in the maps. The conflict is inside RCEF's own records. |
| The `ih` remark ("i") and META IH ("tip") name different vowels. | `vrm_expressions` line 164, `xr_visemes` | An exact vowel class for `ih`. Both are in `vowel_close_spread`. |
| VRM states no language for its remarks. Read as Japanese, `ou` stays in `vowel_close_rounded`. | `vrm_expressions` line 165 | A reading of the vowel presets for one language. |
| The vowel weights are specific to each model and have no sum constraint. | `vrm_expressions` | Probability semantics: `aa = 1` and `oh = 1` sum to 2. |
| RCEF does not run `isBinary`, the overrides, the material binds or the texture binds. | `vrm_expressions` | Visual equivalence on a VRM model. Running bindings is a later gate. |
| LookAt describes one shared direction, with range maps for each model. | `vrm_lookat` | Two eyes that point in different directions, and any map of the `look*` presets. |
| Permission to redistribute the specification prose is unresolved. | [REVIEW.md](REVIEW.md#evidence-and-gates-still-open) | Copying VRM text into RCEF. RCEF links and writes its own summary. |

## Roblox

### Technical context

Roblox Corporation publishes the Roblox engine and its creator documentation. `FaceControls` is an engine class for dynamic heads, which are avatar heads that support animation. Each of its 50 properties is a number from 0 to 1. Each property drives a joint pose that the creator of the head authors. The Roblox documentation calls these poses FACS poses (`roblox_poses`).

Frame 0 of the head's animation is the neutral pose. Each named pose maps to a frame, and combination poses store correctives (`roblox_authoring`). RCEF records nothing about which trackers or devices write the values.

All five records are at creator-docs commit `a0fce04`, retrieved on 2026-10-07, under CC-BY-4.0.

| Evidence record | Source page | What RCEF takes from it |
|---|---|---|
| [`roblox_controls`](references.md#roblox_controls) | `FaceControls.yaml` (engine reference) | 50 float controls with the domain 0 to 1; the joint mapping; required pose list A (17 poses) |
| [`roblox_requirements`](references.md#roblox_requirements) | dynamic-head specifications | a different required pose list B (17 poses) and 5 validation actions |
| [`roblox_authoring`](references.md#roblox_authoring) | create basic heads | neutral Frame 0, pose-to-joint mappings, and combination correctives as differences |
| [`roblox_poses`](references.md#roblox_poses) | FACS poses reference | 50 pose headings that cross-check the control names, with list B notices |
| [`roblox_license`](references.md#roblox_license) | `LICENSE` | the CC-BY-4.0 licence of the documentation |

On 2026-10-26, `create.roblox.com` returned HTTP 502 to scripted checks. The same reference is in the creator-docs repository, which RCEF pins.

### Signal structure

RCEF records Roblox in one profile, `roblox.control`. It has 50 rows, all selected and all `unresolved`, and it is inventory only.

Each name is in upper camel case and uses an action name in the style of FACS, such as `LeftInnerBrowRaiser` or `JawDrop`. A sided control starts with `Left` or `Right`. Some controls end with a direction instead, such as `EyesLookLeft`, `JawLeft` and `MouthLeft`. The names give no FACS code numbers. RCEF lists the controls in alphabetical order as inventory ordinals.

| Region | Controls | Names |
|---|---:|---|
| mouth | 18 | `ChinRaiser`, `ChinRaiserUpperLip`, `LipPresser`, `LipsTogether`, `LowerLipSuck`, `UpperLipSuck`, `MouthLeft`, `MouthRight`, and the `Left` and `Right` forms of `LipCornerDown`, `LipCornerPuller`, `LipStretcher`, `LowerLipDepressor` and `UpperLipRaiser` |
| brow | 6 | `BrowLowerer`, `InnerBrowRaiser`, `OuterBrowRaiser`, each `Left` and `Right` |
| other | 6 | `Corrugator`, `FlatPucker`, `Funneler`, `Pucker`, `LeftDimpler`, `RightDimpler` |
| cheek | 4 | `CheekPuff`, `CheekRaiser`, each `Left` and `Right` |
| eyelid | 4 | `EyeClosed`, `EyeUpperLidRaiser`, each `Left` and `Right` |
| gaze | 4 | `EyesLookDown`, `EyesLookLeft`, `EyesLookRight`, `EyesLookUp` |
| jaw | 3 | `JawDrop`, `JawLeft`, `JawRight` |
| tongue | 3 | `TongueDown`, `TongueOut`, `TongueUp` |
| nose | 2 | `LeftNoseWrinkler`, `RightNoseWrinkler` |

The profile has 17 left, 17 right and 16 shared controls. RCEF takes the side from the name, so `EyesLookLeft` has the side left and `EyesLookUp` is shared. RCEF has not checked the side frame.

Each control has metadata for its place in the two required pose lists. The two lists come from pages at the same commit, and they differ.

| Membership | Controls | Count |
|---|---|---:|
| both lists | `EyesLookDown`, `JawDrop`, `LeftEyeClosed`, `RightEyeClosed`, `LeftLipCornerPuller`, `RightLipCornerPuller`, `LeftLowerLipDepressor`, `RightLowerLipDepressor`, `Pucker` | 9 |
| list A only (`roblox_controls`) | `EyesLookLeft`, `EyesLookRight`, `EyesLookUp`, `LeftLipStretcher`, `RightLipStretcher`, `LeftUpperLipRaiser`, `RightUpperLipRaiser`, `LipsTogether` | 8 |
| list B only (`roblox_requirements`, `roblox_poses`) | `ChinRaiser`, `ChinRaiserUpperLip`, `LeftCheekRaiser`, `RightCheekRaiser`, `LeftInnerBrowRaiser`, `RightInnerBrowRaiser`, `LeftLipCornerDown`, `RightLipCornerDown` | 8 |
| neither list | the other controls | 25 |

So 34 controls have the requirement status `agrees_in_two_lists`, and 16 have `unresolved`. The profile records `required_pose_authority = "unresolved"`.

Every control has the coupling `asset_specific_correctives`. The profile names the joint mapping fields `RootFaceJoint` and `FrameN`. A corrective combines 2 or 3 named poses, with the names joined by underscores. RCEF records no sentinel, enum or validity flag for Roblox.

### Values, neutral and calibration

| Property | Value |
|---|---|
| Value type and units | scalar, units `1` |
| Range | 0 to 1 (`roblox_controls`) |
| Neutral | no `neutral` value; metadata `neutral_frame = 0` |
| Calibration string | `roblox.FaceControls:<name>: asset-specific joint pose mapping` |

The neutral state is Frame 0, the neutral joint pose of the head. RCEF records it as metadata, not as a value of the control. A value of 1 gives the pose that the creator authored for that control on that head. So the meaning of 1 depends on the asset, and no shared gain exists. A combination corrective stores a difference from the combined base poses. RCEF records the execution of correctives as "unsupported; pose/joint data required".

### Mapping to the canonical sets

Roblox has no maps, and no route starts or ends at `roblox.control`. Each control has the reason "Native identifier evidenced; canonical calibration and executable mapping remain unresolved."

The plan puts Roblox in phase 3 ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)). Roblox already has a pinned source, a known licence, a profile, evidence records and a row in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). It still needs a section of the audit, a capability row, the maps and a trademark check. Some controls have no canonical signal. For example, `TongueUp` and `TongueDown` would need the reserved names `tongue_up` and `tongue_down`, which are not signals yet ([docs/canonical-set.md](docs/canonical-set.md#reserved-names)).

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| The engine reference and the dynamic-head pages give two different lists of 17 required poses. 16 controls are in one list only. | `roblox_controls`, `roblox_requirements`, `roblox_poses` | A statement of which poses a head must have, and so certification. |
| The specifications page lists 5 validation actions. RCEF records them only in the evidence claim, not as signals. | `roblox_requirements` | Any check of a head against those actions. |
| RCEF has not checked the side frame. | [docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets) | Side assignment in any map. |
| The audit has no Roblox rows, and the names have no FACS code numbers. | [audit](docs/canonical-set-audit.md) | Every in-map and out-map. |
| Each value drives a pose that the creator authors for one head. | `roblox_authoring`; coupling `asset_specific_correctives` | A shared meaning of 1 across heads. |
| Correctives need pose and joint data, which RCEF does not hold. | metadata `corrective_execution` | Execution of combination poses. |
| Roblox certification is a later gate, which needs its own measured acceptance. | [GOVERNANCE.md](GOVERNANCE.md), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open) | Any claim that a head complies. |

## FACS codes

### Technical context

FACS is the Facial Action Coding System. Human coders use it to score facial actions as numbered codes, with an intensity letter from A to E. The FACS manual is closed. RCEF does not read, quote or paraphrase it ([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)). Other expression sets name their shapes after FACS actions: Roblox calls its face poses FACS poses, and many FB2 names match FACS names.

FACS publishes no numeric interface. So the profile `facs.code` is RCEF's own encoding of public code numbers. Its values are not FACS scores, and RCEF does not code faces. The profile is a draft (`vocabulary_status = "draft"`), and the working group has not reviewed its meaning. All 92 rows have the evidence status `proposed`: the code numbers are facts, but the scalar encoding is RCEF's.

| Evidence record | Source | Pinned revision | What RCEF takes from it | Licence |
|---|---|---|---|---|
| [`facs_wikipedia`](references.md#facs_wikipedia) | Wikipedia, "Facial Action Coding System" | revision 1357638399, retrieved 2026-10-28 | code numbers, short names, table membership, intensity letters, modifier letters and visibility-region names, as facts | CC-BY-SA-4.0 |
| [`facs_hager_2002`](references.md#facs_hager_2002) | the FACS publisher's page on the 2002 manual | Internet Archive capture of 2008-12-18, retrieved 2026-10-29 | the 2002 changes for AU 41, 42, 43 and 44, and the revised scoring of 25, 26 and 27 | reference only |
| [`rocketbox_avatars`](references.md#rocketbox_avatars) | Microsoft Rocketbox avatar library | `0943055` | the 48 `AU_*` shape names of the facial rig files, as `aligned_names` | MIT |

The codec in [docs/facs-intensity.md](docs/facs-intensity.md) turns FACS notation, for example `1C+2C+L12B`, into `facs.code` values and back. `examples/facs_codec.py` implements it. The examples drive Rocketbox and ICT-FaceKit faces from an expression library that uses FACS codes.

### Signal structure

The IDs are `facs.code.au<NN>` with two digits, plus `_left` or `_right` on a sided signal. The `native_id` is the FACS notation, for example `L1`, `17` or `L30`. The label gives the code and the Wikipedia name, for example "AU 1 Inner brow raiser, left".

The 92 rows hold 70 code numbers. 22 codes have two rows: 21 codes are split by side, and AU 30 is split into `au30_left` and `au30_right`. RCEF keeps the stars on `97*` and `98*`.

| Wikipedia table | Rows | `mapped` | `unresolved` | `excluded` |
|---|---:|---:|---:|---:|
| Main codes | 45 | 40 | 5 | 0 |
| Gross behaviour codes | 32 | 9 | 13 | 10 |
| Head movement codes | 8 | 0 | 0 | 8 |
| Eye movement codes | 7 | 0 | 7 | 0 |
| Total | 92 | 49 | 25 | 18 |

The 49 `mapped` rows are these:

- 42 sided signals for 21 codes, two signals for each code;
- 5 shared codes: 8, 17, 19, 26 and 29;
- the 2 rows of AU 30.

Sided codes are 1, 2, 4, 5, 6, 7, 9, 10, 12, 14, 15, 16, 18, 20, 22, 23, 24, 28, 34, 35 and 43. The mapped gross behaviour codes are 29, 30, 34, 35 and 43. Code 0 (neutral face) is not a row, because it is the all-zero frame. The 10 "M" codes and the visibility codes 70 to 74 are not rows either. 52 rows hold Rocketbox shape names in `aligned_names`.

Wikipedia allows L or R before a code, but does not say from whose view (raw line 78). RCEF reads L and R as the subject's own side, as an assumption with the loss key `facs_side_frame_unresolved`. 44 rows carry this assumption as a side note. RCEF also reads `L30` and `R30` as movements toward the subject's own left and right, as an assumption with the loss key `facs_au30_direction_unresolved`. RCEF splits a code by side only where the canonical signal has sides, so a round trip FACS → canonical → FACS loses no side.

The eye movement codes 61 to 64 are `unresolved`, because the source does not say whose left they mean ([Gaze](docs/canonical-set.md#gaze)). The tongue codes are 19 (mapped to `tongue_out`) and 36 (`unresolved`). FACS has no validity flag for each code. The visibility codes 70 to 74 mark parts of the face that the coder could not see, and the codec leaves out their signals. The codec leaves out a frame that nobody scored, and it never turns it into a frame of zeros.

### Values, neutral and calibration

The 49 `mapped` rows have units `1`, the domain 0 to 1 and `neutral = 0.0`. The other 43 rows have units `unknown` and no domain, and no map reads them.

| Value | Main codes | Gross behaviour codes 29, 30, 34, 35 and 43 |
|---|---|---|
| 0 | absent: a scored frame does not list the code | absent |
| 1 | intensity E, the maximum possible for the person (raw line 70) | the action at its fullest, as RCEF assumes; the source gives these codes no intensity scale |
| between 0 and 1 | RCEF's encoding of the letters | RCEF's encoding of the letters |

The codec uses the letter table `rcef.facs.letters.v1`: A 0.2, B 0.4, C 0.6, D 0.8 and E 1.0. A code with no letter is C, 0.6. For display, the codec turns a value back into a letter by fixed ranges, and a value below 0.1 is "absent". Each of these rules is an RCEF assumption.

The calibration is unresolved in four ways:

- FACS intensity is ordinal. RCEF does not claim equal steps between letters, and measures no gain (`facs_ordinal_intensity`).
- The gross behaviour codes have no intensity scale in the source (`facs_gross_code_no_intensity`).
- The 2002 manual scores AU 43 by intensity, but no public source gives its letters (`facs_hager_2002`).
- Only the closed manual says which codes can be one-sided, and on whose side.

### Mapping to the canonical sets

| Map | Direction | Mappings | Parts | Evidence status |
|---|---|---:|---:|---|
| [`facs.to_rcef_expression`](docs/map-sets/facs.to_rcef_expression.md) | `facs.code` → `rcef.canonical_expression` | 53 | 8 | `proposed` (53) |
| [`rcef_expression.to_facs`](docs/map-sets/rcef_expression.to_facs.md) | `rcef.canonical_expression` → `facs.code` | 49 | 8 | `proposed` (49) |

| Part | Canonical signals | In-map mappings | Out-map mappings | FACS codes |
|---|---|---:|---:|---|
| `face` | 41 of 41 | 41 | 37 | 1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28 |
| `cheek_puff` | 2 of 2 | 2 | 2 | 34 |
| `jaw_thrust` | 1 of 1 | 1 | 1 | 29 |
| `jaw_sideways` | 2 of 2 | 2 | 2 | 30 |
| `blink` | 2 of 2 | 2 | 2 | 43 |
| `tongue_out` | 1 of 1 | 1 | 1 | 19 |
| `cheek_suck` | 2 of 2 | 2 | 2 | 35 |
| `lip_tighten` | 2 of 2 | 2 | 2 | 23 |

The in-map has 38 sided copies, 8 fan-outs, 5 shared copies and the 2 rows of AU 30. FACS has no upper and lower split for AU 22 and AU 28. So the fan-outs copy each side into the upper and the lower canonical signal.

The out-map has 38 sided copies and 5 shared copies. It also has 4 means of two for AU 22 and AU 28, and the 2 rows of AU 30. The operators are `affine(1,0)` and `weighted_sum [0.5, 0.5]`. An identity is not possible, because the FACS calibration string differs from the canonical one ([docs/canonical-set.md](docs/canonical-set.md#facs)).

FACS fills 8 of the 13 groups of the canonical expression set.

| Group that FACS does not fill | Reason |
|---|---|
| `mouth_shift` | FACS has no code for it. |
| `chin_raise_upper_lip` | AU 17 is the whole chin raise, with no upper and lower split (`facs_au17_no_split`). |
| `gaze` | The source does not say whose left the codes 61 to 64 mean. |
| `tongue_place` | FACS has no code for the tongue positions. |
| `pupil_mm` | FACS has no code for pupil size. |

So FACS → ARKit writes 41 of the 52 ARKit outputs, and FACS → FB2 writes 53 of the 70 FB2 outputs. The out-map never writes codes 25 and 27, because it writes all mouth opening as 26. It never writes 41, 42, 44, 45 and 46, because it writes all eye closure as 43. The audit has 53 FACS signal rows (49 `same`, 2 `differs`, 2 `unresolved`) and 3 encoding rows (all `differs`).

| Rows that no map reads | Disposition | How the codec reads them |
|---|---|---|
| 27 | `unresolved` | as 26 at its own letter (`facs_mouth_opening_split`) |
| 45, 46 | `unresolved` | as 43, on both eyes or on one eye (`facs_eyelid_events`) |
| 41, 42, 44 | `unresolved` | leaves the `blink` signals out; 44 also leaves `lid_tighten` out |
| 33 | `unresolved` | leaves the `cheek_puff` signals out, because a coder may score 33 instead of 34 |
| 37 | `unresolved` | leaves `tongue_out` out, because a coder may score 37 instead of 19 |
| 11, 13, 21, 25, 31, 32, 36, 38, 39, 40, 61 to 66, 69 | `unresolved` | not read; the route lists them as dropped |
| 51 to 58 | `excluded` | head pose is out of scope |
| 50, 80, 81, 82, 84, 85, 91, 92, 97\*, 98\* | `excluded` | behaviour events, not face weights |

A signal that the codec leaves out is never 0. It has no value, so the in-map writes no output that reads it, and the route labels the target outputs "not available from source". The A/B comparison checks FACS → FB2 against the AU table of RCEF's expression library. The route equals the table on every output that both write (metric M10, pass). The report M11 compares the ARKit → FACS links with the FACS table of ICT-FaceKit. 20 of its 29 rows are the same, and 9 are listed differences ([ab/README.md](ab/README.md)).

### Gaps and conflicts

| Gap or conflict | Evidence | What it blocks |
|---|---|---|
| Wikipedia does not say whose side L and R mean. | raw line 78; `facs_side_frame_unresolved` | A `same` verdict on the 42 sided rows and the 2 rows of AU 30. |
| The source does not state whose left `L30` and `R30` mean. | `facs_au30_direction_unresolved` | A verified jaw direction. |
| The source does not state whose left the eye codes 61 and 62 mean, and public crosswalks disagree. | [Gaze](docs/canonical-set.md#gaze) | A `gaze` part in both FACS maps. |
| FACS splits mouth opening into 25, 26 and 27, and the 2002 manual revised their scoring. | `facs_wikipedia`, `facs_hager_2002` | A signal of its own for 25 or 27. |
| The 2002 manual folds 41, 42 and 44 into AU 43 intensity, but no public source gives those letters. | `facs_hager_2002` | Any reading of 41, 42 and 44. |
| FACS scores blink (45) and wink (46) as events, apart from 43. | `facs_eyelid_events` | Values for 45 and 46 in each frame. |
| Rocketbox names its AU 13 shape `AU_13_CheekPuffer`, while Wikipedia names 13 "Sharp lip puller". | `rocketbox_avatars`, `facs_wikipedia` | Use of the Rocketbox name for 13. |
| ICT-FaceKit relates ARKit `cheekPuff` to 33, `eyeBlink` to 45 and `jawOpen` to 27. RCEF uses 34, 43 and 26. | loss keys `ict_au33_cheek_blow`, `ict_au45_blink`; [docs/godot_comparison.md](docs/godot_comparison.md) | Use of the ICT crosswalk for these FACS codes. |
| AU 22 and AU 28 have no upper and lower split. | loss "symmetry is invented" on 8 fan-outs | Upper and lower asymmetry from FACS. |
| The canonical set and `facs.code` are drafts. | `vocabulary_status = "draft"` | The status `accepted`. |

The plan adds the eye movement codes 61 to 64 in phase 1b, with the loss key `facs_side_frame_unresolved`. Phase 2 adds signals that only FACS has and that action unit detectors need, for example `lips_part` (25), under reserved names ([docs/expression-sets.md](docs/expression-sets.md#planned-expression-sets)).

## Comparison across sets

### Canonical groups that each set fills

This table shows which groups of the canonical sets each set fills through its maps. "In" means that the in-map writes the group, and "out" means that the out-map reads it. The table counts the parts of each map from the pack. MediaPipe, OpenXR FB, Godot and Roblox have no maps, so they fill no group.

| Canonical group | ARKit | FB2 | FACS codes | VRCFaceTracking eye | Unified Expressions | VRM | META visemes |
|---|---|---|---|---|---|---|---|
| `face` | in and out | in and out | in and out | no | out | no | no |
| `blink` | in and out | in and out | in and out | in and out | out | in and out | no |
| `gaze` | in and out | in and out | no | no | out | no | no |
| `cheek_puff` | in and out | in and out | in and out | no | out | no | no |
| `cheek_suck` | no | in and out | in and out | no | out | no | no |
| `jaw_thrust` | in and out | in and out | in and out | no | out | no | no |
| `jaw_sideways` | in and out | in and out | in and out | no | out | no | no |
| `mouth_shift` | in and out | in and out | no | no | out | no | no |
| `chin_raise_upper_lip` | in and out | in and out | no | no | out | no | no |
| `lip_tighten` | no | in and out | in and out | no | out | no | no |
| `tongue_out` | in and out | in and out | in and out | no | out | no | no |
| `tongue_place` | no | in and out | no | no | no | no | no |
| `pupil_mm` | no | no | no | in and out | no | no | no |
| `viseme_rest` | no | no | no | no | no | no | in and out |
| `viseme_consonant` | no | no | no | no | no | no | in and out |
| `viseme_vowel` | no | no | no | no | no | in and out | in and out |
| `viseme_aggregate` | no | no | no | no | no | no | in |

The viseme pose bridge reads `viseme_rest`, `viseme_consonant` and `viseme_vowel`. It writes `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`. [docs/routes.svg](docs/routes.svg) shows the same groups as a figure.

### Problems that every set shares

| Problem | Where it occurs | Effect on the canonical design |
|---|---|---|
| No published gain | Every set. No source shows that a full activation in one set equals a full activation in another. | Each canonical signal has a declared meaning and no measured gain. Every in-map and out-map assumes that the source's 0 and 1 are canonical 0 and 1. So every cross-provider mapping is `proposed`. |
| Side frames | ARKit, FB2 and Unified Expressions settle their frame with their own text or figures. VRM and the FACS source do not state it. RCEF has not checked the frame of the sets with no map. | The canonical set names sides from the subject's own face. Where a source does not state its frame, RCEF reads the subject's own side as an assumption and states a loss key, for example `vrm_blink_side_unresolved`. |
| Different gaze bases | ARKit describes eyelid movement. FB2 gives fractions of a maximum angle that it does not state. VRM uses angles in degrees. The VRCFaceTracking raw gaze units are unresolved. | Canonical gaze is a fraction of the source's maximum gaze in one direction, with no angle. The ARKit and FB2 maps state the difference as a loss. No map reads the VRM `look*` presets or the VRCFaceTracking raw gaze. |
| Asset-authored weights | A VRM preset drives the binds that each model author sets. A Roblox control drives a joint pose that the creator of each head authors. | The meaning of 1 depends on the model. The canonical set defines each signal by a face action, and the binds of a model are outside the set. The VRM maps state this as a loss, and Roblox has no maps. |

### Semantics that remain distinct

RCEF never treats these quantities as the same, even when their names are alike:

- `disposition`, `evidence_status` and `mapping_quality` are separate fields. A verified native name can still have an unresolved mapping.
- A validity flag, a `neutral` value and a `native_default` are different things. VRCFaceTracking `Openness` starts at 1, and its source does not state that this start value is a neutral.
- ARKit eye-look coefficients, ARKit eye transforms, FB2 direction fractions and VRCFaceTracking normalized avatar parameters are separate gaze bases. The maximum angles and the model calibration are unknown, so no cross-provider identity is possible.
- A raw pupil diameter in millimetres, a combined normalized dilation and a parameter in centimetres are different quantities.
- An asset-authored weight and a tracker weight are different quantities.

### General morph weights

The [pinned glTF source](references.md#gltf_morph) allows morph coefficients outside 0 to 1. The domains of tracked signals do not set a domain for every morph. Signed geometric weights or weights above one, bind and rest transforms, and asset hashes belong to the shared tooling and to later asset tests. Host execution also belongs there. RCEF does not make geometry.

## Data notes

Data 0.5.0 retired 21 identity mappings into the old 21-signal set `rcef.canonical` ([docs/retired-ids.csv](docs/retired-ids.csv)). From that time, 21 signals still have `mapping_quality = "exact"` in their metadata. For the 2 raw VRCFaceTracking pupil fields, this agrees with their current mappings. The other 19 are 9 ARKit coefficients, the 8 FB2 gaze weights and the 2 VRCFaceTracking `Openness` fields. Their current mappings are `approximate`.

Nothing executable reads this field. The latest A/B freeze holds a hash of the signal metadata, so a change to the field needs a new freeze.
