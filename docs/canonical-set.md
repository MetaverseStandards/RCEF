<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Canonical expression set (draft)

Original documentation: CC-BY-SA-4.0. Copyright (c) 2026 Metaverse Standards Forum.

**Author affiliation: to be added by the release owners before this document goes to the working group.**

**Status:** a draft proposal for review. Vocabulary version `1.0`, status `draft`. Data 0.5.0 holds the expression part: the profile `rcef.canonical_expression` with 60 of its 72 signals (every group except `cheek_suck`, `lip_tighten`, `tongue_place` and the pupils), and the maps of ARKit, FB2, Unified Expressions and VRM blinks. The viseme profile and its maps are not in the data yet. The pack also keeps the older `rcef.canonical` set of 21 signals, and each of those keeps its provider's calibration ([expression-sets.md](expression-sets.md#rcefs-own-sets)).

This document uses the proposal form of [GOVERNANCE.md](../GOVERNANCE.md): the problem, the proposal, the public evidence, the effect on compatibility, the alternatives, the tests and the open questions. Two documents go with it:

- the [definitions audit](canonical-set-audit.md), which compares each canonical signal with each public source that maps it, and records the assumptions of today's maps;
- [facs-intensity.md](facs-intensity.md), which says how FACS intensity letters become numbers.

## Problem

Today RCEF maps one provider directly to another: 7 maps with 187 cross-provider mappings ([README](../README.md#mappings)). Each new pair needs a new map. Where no map exists, the only route is through ARKit. The 21 signals of `rcef.canonical` each keep their provider's calibration, so they cannot act as a common point between providers.

RCSF does this job for skeletons. It calls itself a pivot for translating between formats, not a new universal skeleton that everyone must adopt (`rcsf_readme`, README line 9, RCSF `f6c3ea8`). This proposal does the same for face expressions.

## Proposal in brief

- Two new profiles: `rcef.canonical_expression` with 72 signals (70 without units, 2 in millimetres), and `rcef.canonical_viseme` with 15 signals.
- Every translation runs source → canonical set → target. An in-map turns a provider's values into canonical values. An out-map turns canonical values into a provider's values.
- The FACS code numbers become an expression set of their own, `facs.code`, with in-maps and out-maps ([FACS](#facs)).
- RCEF is a pivot for translating between expression sets. It is not a set that everyone must adopt. Each canonical signal has a declared meaning, but no shared or measured gain.

## Names and IDs

- **Expression IDs:** `rcef.canonical_expression.<short_name>`, in lowercase snake_case. Sides use `_left` and `_right`. Lip quadrants use `_upper_left`, `_upper_right`, `_lower_left` and `_lower_right`.
- **Viseme IDs:** `rcef.canonical_viseme.<class>`. The classes are `sil`, `pp`, `ff`, `th`, `dd`, `kk`, `ch`, `ss`, `nn`, `rr`, `aa`, `e`, `ih`, `oh` and `ou`.
- Short names are unique across both profiles.
- The prefix of each ID is its profile ID. The new IDs do not reuse the `rcef.canonical.` namespace.
- An ID never holds a version. Versions are in the calibration string and in the profile metadata.
- An ID never changes. A new meaning gets a new ID. A retired ID needs a tombstone ([GOVERNANCE.md](../GOVERNANCE.md)).
- New IDs become permanent at the first release that contains them.
- **Labels** are plain English, for example "Inner brow raise, left". The label carries the readable name.
- **Why snake_case.** RCSF uses readable names such as "Hips" (RCSF `joints.csv`, `f6c3ea8`). RCEF uses snake_case IDs instead, as a neutral style: ARKit and VRM use lowerCamelCase, FB2 uses UPPER_SNAKE and VRCFaceTracking Unified Expressions uses PascalCase. One-word IDs look the same in any lowercase style. For example, the viseme classes `aa`, `ih`, `oh` and `ou` equal VRM preset names.

## Fields

Every canonical signal has these fields.

| Field | Value |
|---|---|
| `value_type`, `units`, `domain`, `neutral` | `scalar`, `"1"`, `{min = 0.0, max = 1.0}`, `0.0`. Exceptions: visemes use `units = "probability"` and have no `neutral` field. The pupils use `units = "mm"`, `domain = {}` and no `neutral` field. |
| `calibration` | The string for the signal's class (below). |
| `side` | `left`, `right` or `shared`, from the subject's own face. On `jaw_sideways_*` and `mouth_shift_*` the suffix names a direction: `_left` means "toward the subject's own left". Their side is `shared`, because the whole jaw or mouth moves. |
| `region` | As in the [signal table](#expression-signals). |
| `coupling` | None on expression signals. `probability_simplex` on visemes; this is a label only. |
| `disposition` | `mapped` once a mapping uses the signal. |
| `evidence_status` | `proposed`. The two pupil signals are `verified_current`, and their evidence holds only `verified_current` records (`rcef_canonical_v1`, `vrcft_data`). msf-character-tools needs this for a `verified_current` mapping ([architecture.md](architecture.md#map-compilation-is-stricter-than-inventory-validation)). |
| `evidence` | `rcef_canonical_v1`, the original record for this vocabulary. Signals with a FACS code also cite `facs_wikipedia`. The jaw and mouth-shift signals also cite `xr_fb2`, the FB2 figure records and `apple_blendshapes` for their direction wording. |
| `metadata` | `definition` (RCEF's own text), `zero`, `one`, `facs_au` (empty where the table shows none), `facs_table` (`main` or `gross_behavior`), `group`, `aligned_names` (provider names, as facts) and `audit` (a pointer to the [audit](canonical-set-audit.md) rows). |

Both profiles also have `vocabulary_version` and `vocabulary_status` in their metadata ([How the set grows](#how-the-set-grows)).

**Calibration strings:**

- **Expression signals:** `rcef.canonical.v1:<short_name>: declared 0 = neutral face, 1 = full activation of the action RCEF defines; assumed to agree with each source at 0 and 1; values between are passed through by the hop operator, and RCEF assumes, without evidence, that each source's in-between values correspond in this way; no measured gain or response curve`
- **Gaze:** `rcef.canonical.v1:<short_name>: fraction of the source's maximum gaze in this direction; source-relative; no angle and no curve claimed`
- **Visemes:** `rcef.canonical.v1:<short_name>: class probability as the source reports it; no per-class neutral; silence is sil = 1`
- **Pupils:** `rcef.canonical.v1:<short_name>: tracker-reported pupil diameter in millimetres`

## Meaning of 0, 1 and neutral

These rules apply to the expression signals. The pupils are a length. [Gaze](#gaze) and [visemes](#visemes) have their own rules.

- **0 is the neutral face:** the face is relaxed; the lids are open and relaxed; the eyes look ahead; the lips are together and the jaw is closed; the tongue is at rest. This text is RCEF's own.
- **1 is full activation of the named action,** as its definition describes it. The closest public wording is FB2's: a weight of 1 means that the blend shape is fully active (`xr_fb2` lines 351-353).
- **Each source is assumed to agree with the canonical set at 0 and at 1, and in between as the hop operator passes the values.** These are assumptions, not facts. No response curve is measured.
- No value constraint between canonical signals is declared. This is not a claim that shapes add up on a rig. For example, the six tongue-contact signals cannot all be true at once.

**What each hop says.** Every hop starts with this assumption: "provider X's 0 and 1 for this shape are assumed to be canonical 0 and 1, and values between are assumed to correspond as the operator passes them; no evidence supports this, and no response curve is measured". Then it adds the clause for its operator:

| Operator on the hop | Added clause |
|---|---|
| affine(1,0), one input, one output | "the value is carried over unchanged" |
| affine(1,0) fan-out (ARKit in-hop) | "the one ARKit value is copied into each part" |
| affine(1,0) fan-out (Unified Expressions out-hop) | "the one canonical value is copied into each Unified Expressions part" |
| weighted_sum mean (ARKit out-hop) | "the ARKit value is the mean of the canonical parts" |
| weighted_sum [1, −1] and knots (FB2 gaze out-hop) | "the larger of two opposing directions is reduced by the smaller; only the difference is kept" |
| affine(−1,1) (VRCFaceTracking eye blink hops) | "eye_close is 1 − Openness" |
| affine(1,0) on millimetres (pupils) | "the tracker-reported diameter is carried over unchanged" |
| affine(1,0), FACS, one input, one output | "the value is carried over unchanged" |
| affine(1,0) fan-out (FACS in-hop, AU22 and AU28 per side) | "the one FACS side value is copied into the upper and the lower part" |
| weighted_sum mean (FACS out-hop, AU22 and AU28 per side) | "the FACS side value is the mean of the upper and lower canonical parts" |

FACS hops start with their own assumption instead: "FACS intensity E, the maximum for the person, is assumed to be canonical 1, and 'absent' (a scored frame does not list the code) is assumed to be canonical 0; FACS defines only the ordered letters A-E, so values between are RCEF's encoding ([facs-intensity.md](facs-intensity.md)) and correspond as the operator passes them; no evidence supports this, and no response curve is measured". On the hops of the gross behaviour codes (29, 30, 34, 35 and 43) the first clause reads: "the action at its fullest, as RCEF assumes, is canonical 1; the source gives no intensity scale for gross behaviour codes".

Where the [audit](canonical-set-audit.md) marks a row `differs` or `unresolved`, the hop adds: "the endpoints are assumed equal although the defined actions differ or are unresolved; see loss `<key>`". Every hop also has its own gain loss, for example "FB2 gain and full-activation pose not published".

## Signals

### Groups

A group is the set of signals that one in-map writes and one out-map reads. A source must fill a whole group, or the out-maps that read it give no values.

| Group | Signals | Contents |
|---|---:|---|
| `face` | 41 | brows, `lid_tighten`, `upper_lid_raise`, `cheek_raise`, `nose_wrinkle`, `jaw_drop`, the lip-corner and lip signals, `chin_raise`, `lips_toward` |
| `cheek_puff` | 2 | `cheek_puff_left`, `cheek_puff_right` |
| `jaw_thrust` | 1 | `jaw_thrust` |
| `jaw_sideways` | 2 | `jaw_sideways_left`, `jaw_sideways_right` |
| `mouth_shift` | 2 | `mouth_shift_left`, `mouth_shift_right` |
| `chin_raise_upper_lip` | 1 | `chin_raise_upper_lip` |
| `blink` | 2 | `eye_close_left`, `eye_close_right` |
| `gaze` | 8 | the 8 gaze directions |
| `tongue_out` | 1 | `tongue_out` |
| `cheek_suck` | 2 | `cheek_suck_left`, `cheek_suck_right` |
| `lip_tighten` | 2 | `lip_tighten_left`, `lip_tighten_right` |
| `tongue_place` | 6 | the 6 tongue positions |
| `pupil_mm` | 2 | the 2 pupil diameters |
| `viseme_vowel` | 5 | `aa`, `e`, `ih`, `oh`, `ou` |
| `viseme_consonant` | 10 | `sil`, `pp`, `ff`, `th`, `dd`, `kk`, `ch`, `ss`, `nn`, `rr` |

**Why these groups.** FACS has no code for `mouth_shift_*` or `chin_raise_upper_lip`. The OpenXR `XR_ML_facial_expression` set has no cheek puff, jaw thrust or jaw sideways shapes (`xr_registry`, `xr.xml` lines 8948-8996). If these signals were in `face`, neither source could fill `face`, and no face value could be written from them. So they are small groups of their own.

### Expression signals

The table gives every signal of `rcef.canonical_expression`. 0 is the neutral face for every signal except the pupils. The FB2 and ARKit columns give the provider names that the in-maps read and the out-maps write (`aligned_names`). Two more sources write a few signals: VRCFaceTracking eye data writes `eye_close_*` (as 1 − `Openness`) and the pupils, and VRM writes `eye_close_*` (`blinkLeft`, `blinkRight`) and the five vowels.

| Short name | Label | Side | Region | Group | Definition | FACS code (table) | FB2 | ARKit |
|---|---|---|---|---|---|---|---|---|
| `brow_inner_raise_left` | Inner brow raise, left | left | Brows | face | The inner part of the left brow lifts, and the forehead above it lifts with it. | 1 (`main`) | INNER_BROW_RAISER_L | browInnerUp (copied to both sides) |
| `brow_inner_raise_right` | Inner brow raise, right | right | Brows | face | The inner part of the right brow lifts, and the forehead above it lifts with it. | 1 (`main`) | INNER_BROW_RAISER_R | browInnerUp (copied to both sides) |
| `brow_outer_raise_left` | Outer brow raise, left | left | Brows | face | The outer part of the left brow lifts, and the forehead above it lifts with it. | 2 (`main`) | OUTER_BROW_RAISER_L | browOuterUpLeft |
| `brow_outer_raise_right` | Outer brow raise, right | right | Brows | face | The outer part of the right brow lifts, and the forehead above it lifts with it. | 2 (`main`) | OUTER_BROW_RAISER_R | browOuterUpRight |
| `brow_lower_left` | Brow lower, left | left | Brows | face | The left brow lowers and draws toward the middle of the face. This is the whole action: the inner and outer parts move together. | 4 (`main`) | BROW_LOWERER_L | browDownLeft |
| `brow_lower_right` | Brow lower, right | right | Brows | face | The right brow lowers and draws toward the middle of the face. This is the whole action: the inner and outer parts move together. | 4 (`main`) | BROW_LOWERER_R | browDownRight |
| `eye_close_left` | Eye close, left | left | Eyes and eyelids | blink | The upper lid of the left eye lowers until it covers the eye. 1 is the eye fully closed. | 43 (`gross_behavior`) | EYES_CLOSED_L | eyeBlinkLeft |
| `eye_close_right` | Eye close, right | right | Eyes and eyelids | blink | The upper lid of the right eye lowers until it covers the eye. 1 is the eye fully closed. | 43 (`gross_behavior`) | EYES_CLOSED_R | eyeBlinkRight |
| `lid_tighten_left` | Lid tighten, left | left | Eyes and eyelids | face | The lids of the left eye tighten and narrow the eye opening. The lower lid moves toward the inner corner. | 7 (`main`) | LID_TIGHTENER_L | eyeSquintLeft |
| `lid_tighten_right` | Lid tighten, right | right | Eyes and eyelids | face | The lids of the right eye tighten and narrow the eye opening. The lower lid moves toward the inner corner. | 7 (`main`) | LID_TIGHTENER_R | eyeSquintRight |
| `upper_lid_raise_left` | Upper lid raise, left | left | Eyes and eyelids | face | The upper lid of the left eye lifts and the eye opens wider. | 5 (`main`) | UPPER_LID_RAISER_L | eyeWideLeft |
| `upper_lid_raise_right` | Upper lid raise, right | right | Eyes and eyelids | face | The upper lid of the right eye lifts and the eye opens wider. | 5 (`main`) | UPPER_LID_RAISER_R | eyeWideRight |
| `gaze_in_left` | Gaze in, left | left | Gaze | gaze | The left eye turns toward the nose, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_RIGHT_L | eyeLookInLeft |
| `gaze_in_right` | Gaze in, right | right | Gaze | gaze | The right eye turns toward the nose, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_LEFT_R | eyeLookInRight |
| `gaze_out_left` | Gaze out, left | left | Gaze | gaze | The left eye turns toward the temple, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_LEFT_L | eyeLookOutLeft |
| `gaze_out_right` | Gaze out, right | right | Gaze | gaze | The right eye turns toward the temple, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_RIGHT_R | eyeLookOutRight |
| `gaze_up_left` | Gaze up, left | left | Gaze | gaze | The left eye turns up, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_UP_L | eyeLookUpLeft |
| `gaze_up_right` | Gaze up, right | right | Gaze | gaze | The right eye turns up, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_UP_R | eyeLookUpRight |
| `gaze_down_left` | Gaze down, left | left | Gaze | gaze | The left eye turns down, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_DOWN_L | eyeLookDownLeft |
| `gaze_down_right` | Gaze down, right | right | Gaze | gaze | The right eye turns down, as a fraction of the source's maximum gaze in that direction (see [Gaze](#gaze)). | none | EYES_LOOK_DOWN_R | eyeLookDownRight |
| `cheek_puff_left` | Cheek puff, left | left | Cheeks | cheek_puff | Air fills the left cheek and pushes it outward. | 34 (`gross_behavior`) | CHEEK_PUFF_L | cheekPuff (copied to both sides) |
| `cheek_puff_right` | Cheek puff, right | right | Cheeks | cheek_puff | Air fills the right cheek and pushes it outward. | 34 (`gross_behavior`) | CHEEK_PUFF_R | cheekPuff (copied to both sides) |
| `cheek_raise_left` | Cheek raise, left | left | Cheeks | face | The outer part of the muscle ring around the left eye tightens, narrowing the outer corner of the eye; the skin below the eye and the upper cheek are pushed up. | 6 (`main`) | CHEEK_RAISER_L | cheekSquintLeft |
| `cheek_raise_right` | Cheek raise, right | right | Cheeks | face | The outer part of the muscle ring around the right eye tightens, narrowing the outer corner of the eye; the skin below the eye and the upper cheek are pushed up. | 6 (`main`) | CHEEK_RAISER_R | cheekSquintRight |
| `cheek_suck_left` | Cheek suck, left | left | Cheeks | cheek_suck | The left cheek draws in against the teeth and hollows. | 35 (`gross_behavior`) | CHEEK_SUCK_L | none |
| `cheek_suck_right` | Cheek suck, right | right | Cheeks | cheek_suck | The right cheek draws in against the teeth and hollows. | 35 (`gross_behavior`) | CHEEK_SUCK_R | none |
| `nose_wrinkle_left` | Nose wrinkle, left | left | Nose | face | The left side of the nose and the nostril lift, and the skin over the nose wrinkles. | 9 (`main`) | NOSE_WRINKLER_L | noseSneerLeft |
| `nose_wrinkle_right` | Nose wrinkle, right | right | Nose | face | The right side of the nose and the nostril lift, and the skin over the nose wrinkles. | 9 (`main`) | NOSE_WRINKLER_R | noseSneerRight |
| `jaw_drop` | Jaw drop | shared | Jaw | face | The lower jaw moves down and the mouth opens. This is the whole opening of the jaw. | 26 (`main`) | JAW_DROP | jawOpen |
| `jaw_thrust` | Jaw thrust | shared | Jaw | jaw_thrust | The lower jaw moves forward. | 29 (`gross_behavior`) | JAW_THRUST | jawForward |
| `jaw_sideways_left` | Jaw sideways left | shared | Jaw | jaw_sideways | The lower jaw moves toward the subject's own left. | 30 (L30, R30 read as directions) (`gross_behavior`) | JAW_SIDEWAYS_LEFT | jawLeft |
| `jaw_sideways_right` | Jaw sideways right | shared | Jaw | jaw_sideways | The lower jaw moves toward the subject's own right. | 30 (L30, R30 read as directions) (`gross_behavior`) | JAW_SIDEWAYS_RIGHT | jawRight |
| `lip_corner_pull_left` | Lip corner pull, left | left | Mouth | face | The left lip corner is drawn up, back and outward. | 12 (`main`) | LIP_CORNER_PULLER_L | mouthSmileLeft |
| `lip_corner_pull_right` | Lip corner pull, right | right | Mouth | face | The right lip corner is drawn up, back and outward. | 12 (`main`) | LIP_CORNER_PULLER_R | mouthSmileRight |
| `lip_corner_depress_left` | Lip corner depress, left | left | Mouth | face | The left lip corner is drawn down. | 15 (`main`) | LIP_CORNER_DEPRESSOR_L | mouthFrownLeft |
| `lip_corner_depress_right` | Lip corner depress, right | right | Mouth | face | The right lip corner is drawn down. | 15 (`main`) | LIP_CORNER_DEPRESSOR_R | mouthFrownRight |
| `dimple_left` | Dimple, left | left | Mouth | face | The left lip corner tightens against the teeth and is drawn back. | 14 (`main`) | DIMPLER_L | mouthDimpleLeft |
| `dimple_right` | Dimple, right | right | Mouth | face | The right lip corner tightens against the teeth and is drawn back. | 14 (`main`) | DIMPLER_R | mouthDimpleRight |
| `lip_stretch_left` | Lip stretch, left | left | Mouth | face | The left lip corner is drawn outward, toward the ear, and the lips stretch. | 20 (`main`) | LIP_STRETCHER_L | mouthStretchLeft |
| `lip_stretch_right` | Lip stretch, right | right | Mouth | face | The right lip corner is drawn outward, toward the ear, and the lips stretch. | 20 (`main`) | LIP_STRETCHER_R | mouthStretchRight |
| `mouth_shift_left` | Mouth shift left | shared | Mouth | mouth_shift | The whole mouth moves toward the subject's own left. | none | MOUTH_LEFT | mouthLeft |
| `mouth_shift_right` | Mouth shift right | shared | Mouth | mouth_shift | The whole mouth moves toward the subject's own right. | none | MOUTH_RIGHT | mouthRight |
| `chin_raise` | Chin raise | shared | Mouth | face | The skin of the chin and the lower lip are pushed up. | 17 (`main`) | CHIN_RAISER_B | mouthShrugLower |
| `chin_raise_upper_lip` | Chin raise, upper lip | shared | Mouth | chin_raise_upper_lip | The upper lip is pushed up by the rising lower lip. This is the part of chin raising that moves the upper lip; `chin_raise` holds the rest. | none | CHIN_RAISER_T | mouthShrugUpper |
| `lip_funnel_upper_left` | Lip funnel, upper left | left | Lips | face | The upper left part of the lips pushes forward and turns outward into a funnel. The mouth rounds and the lips may part. | 22 (`main`) | LIP_FUNNELER_LT | mouthFunnel (copied to all four parts) |
| `lip_funnel_upper_right` | Lip funnel, upper right | right | Lips | face | The upper right part of the lips pushes forward and turns outward into a funnel. The mouth rounds and the lips may part. | 22 (`main`) | LIP_FUNNELER_RT | mouthFunnel (copied to all four parts) |
| `lip_funnel_lower_left` | Lip funnel, lower left | left | Lips | face | The lower left part of the lips pushes forward and turns outward into a funnel. The mouth rounds and the lips may part. | 22 (`main`) | LIP_FUNNELER_LB | mouthFunnel (copied to all four parts) |
| `lip_funnel_lower_right` | Lip funnel, lower right | right | Lips | face | The lower right part of the lips pushes forward and turns outward into a funnel. The mouth rounds and the lips may part. | 22 (`main`) | LIP_FUNNELER_RB | mouthFunnel (copied to all four parts) |
| `lip_pucker_left` | Lip pucker, left | left | Lips | face | The left lip corner is drawn toward the middle of the mouth and the lips push forward. | 18 (`main`) | LIP_PUCKER_L | mouthPucker (copied to both sides) |
| `lip_pucker_right` | Lip pucker, right | right | Lips | face | The right lip corner is drawn toward the middle of the mouth and the lips push forward. | 18 (`main`) | LIP_PUCKER_R | mouthPucker (copied to both sides) |
| `lip_suck_upper_left` | Lip suck, upper left | left | Lips | face | The upper left part of the lips rolls into the mouth. | 28 (`main`) | LIP_SUCK_LT | mouthRollUpper (copied to both sides) |
| `lip_suck_upper_right` | Lip suck, upper right | right | Lips | face | The upper right part of the lips rolls into the mouth. | 28 (`main`) | LIP_SUCK_RT | mouthRollUpper (copied to both sides) |
| `lip_suck_lower_left` | Lip suck, lower left | left | Lips | face | The lower left part of the lips rolls into the mouth. | 28 (`main`) | LIP_SUCK_LB | mouthRollLower (copied to both sides) |
| `lip_suck_lower_right` | Lip suck, lower right | right | Lips | face | The lower right part of the lips rolls into the mouth. | 28 (`main`) | LIP_SUCK_RB | mouthRollLower (copied to both sides) |
| `lip_press_left` | Lip press, left | left | Lips | face | The left halves of the upper and lower lips press together. | 24 (`main`) | LIP_PRESSOR_L | mouthPressLeft |
| `lip_press_right` | Lip press, right | right | Lips | face | The right halves of the upper and lower lips press together. | 24 (`main`) | LIP_PRESSOR_R | mouthPressRight |
| `lip_tighten_left` | Lip tighten, left | left | Lips | lip_tighten | The left halves of the lips narrow and tighten. | 23 (`main`) | LIP_TIGHTENER_L | none |
| `lip_tighten_right` | Lip tighten, right | right | Lips | lip_tighten | The right halves of the lips narrow and tighten. | 23 (`main`) | LIP_TIGHTENER_R | none |
| `lips_toward` | Lips toward each other | shared | Lips | face | The lips move toward each other until they meet, at any jaw opening (FB2 LIPS_TOWARD, `xr_fb2` lines 817-818; FACS AU8). At `jaw_drop` = 0 the lips are already together; RCEF does not define what a non-zero value adds there. | 8 (`main`) | LIPS_TOWARD | mouthClose |
| `upper_lip_raise_left` | Upper lip raise, left | left | Lips | face | The left part of the upper lip lifts. | 10 (`main`) | UPPER_LIP_RAISER_L | mouthUpperUpLeft |
| `upper_lip_raise_right` | Upper lip raise, right | right | Lips | face | The right part of the upper lip lifts. | 10 (`main`) | UPPER_LIP_RAISER_R | mouthUpperUpRight |
| `lower_lip_depress_left` | Lower lip depress, left | left | Lips | face | The left part of the lower lip is drawn down. | 16 (`main`) | LOWER_LIP_DEPRESSOR_L | mouthLowerDownLeft |
| `lower_lip_depress_right` | Lower lip depress, right | right | Lips | face | The right part of the lower lip is drawn down. | 16 (`main`) | LOWER_LIP_DEPRESSOR_R | mouthLowerDownRight |
| `tongue_out` | Tongue out | shared | Tongue | tongue_out | The tongue moves forward and out of the mouth. No length is stated. | 19 (`main`) | TONGUE_OUT | tongueOut |
| `tongue_retreat` | Tongue retreat | shared | Tongue | tongue_place | The tongue draws back toward the throat and stays low in the mouth. | none | TONGUE_RETREAT | none |
| `tongue_tip_interdental` | Tongue tip between the teeth | shared | Tongue | tongue_place | The tongue tip touches the upper teeth and shows between the teeth, as for the TH viseme. | none | TONGUE_TIP_INTERDENTAL | none |
| `tongue_tip_alveolar` | Tongue tip behind the upper teeth | shared | Tongue | tongue_place | The tongue tip touches the back of the upper teeth, as for the NN viseme. | none | TONGUE_TIP_ALVEOLAR | none |
| `tongue_front_dorsal_palate` | Tongue front on the palate | shared | Tongue | tongue_place | The front of the tongue presses on the palate, as for the CH viseme. | none | TONGUE_FRONT_DORSAL_PALATE | none |
| `tongue_mid_dorsal_palate` | Tongue middle on the palate | shared | Tongue | tongue_place | The middle of the tongue presses on the palate, as for the DD viseme. | none | TONGUE_MID_DORSAL_PALATE | none |
| `tongue_back_dorsal_velar` | Tongue back on the palate | shared | Tongue | tongue_place | The back of the tongue presses on the palate, as for the KK viseme. | none | TONGUE_BACK_DORSAL_VELAR | none |
| `pupil_diameter_mm_left` | Pupil diameter (mm), left | left | Pupils | pupil_mm | The diameter of the left pupil in millimetres, as the tracker reports it (VRCFaceTracking eye `Left.PupilDiameter_MM`). Units `mm`; no range is declared. | none | none | none |
| `pupil_diameter_mm_right` | Pupil diameter (mm), right | right | Pupils | pupil_mm | The diameter of the right pupil in millimetres, as the tracker reports it (VRCFaceTracking eye `Right.PupilDiameter_MM`). Units `mm`; no range is declared. | none | none | none |

### Viseme signals

The values are class probabilities, as the META viseme extension defines them (`xr_visemes` lines 104-107). The phoneme classes are META's (`xr_visemes` lines 142-245).

| Short name | Label | Group | Definition | META | VRM |
|---|---|---|---|---|---|
| `sil` | Viseme SIL | viseme_consonant | The probability that the frame is silence. `sil` = 1 is the silent frame. | SIL | none |
| `pp` | Viseme PP | viseme_consonant | The probability that the frame shows the PP viseme class (phonemes: p, b, m). | PP | none |
| `ff` | Viseme FF | viseme_consonant | The probability that the frame shows the FF viseme class (phonemes: f, v). | FF | none |
| `th` | Viseme TH | viseme_consonant | The probability that the frame shows the TH viseme class (phonemes: th). | TH | none |
| `dd` | Viseme DD | viseme_consonant | The probability that the frame shows the DD viseme class (phonemes: t, d). | DD | none |
| `kk` | Viseme KK | viseme_consonant | The probability that the frame shows the KK viseme class (phonemes: k, g). | KK | none |
| `ch` | Viseme CH | viseme_consonant | The probability that the frame shows the CH viseme class (phonemes: tS, dZ, S). | CH | none |
| `ss` | Viseme SS | viseme_consonant | The probability that the frame shows the SS viseme class (phonemes: s, z). | SS | none |
| `nn` | Viseme NN | viseme_consonant | The probability that the frame shows the NN viseme class (phonemes: n, l). | NN | none |
| `rr` | Viseme RR | viseme_consonant | The probability that the frame shows the RR viseme class (phonemes: r). | RR | none |
| `aa` | Viseme AA | viseme_vowel | The probability that the frame shows the AA viseme class (phonemes: A:, as in car). | AA | aa |
| `e` | Viseme E | viseme_vowel | The probability that the frame shows the E viseme class (phonemes: e, as in bed). | E | ee |
| `ih` | Viseme IH | viseme_vowel | The probability that the frame shows the IH viseme class (phonemes: ih, as in tip). | IH | ih |
| `oh` | Viseme OH | viseme_vowel | The probability that the frame shows the OH viseme class (phonemes: oh, as in toe). | OH | oh |
| `ou` | Viseme OU | viseme_vowel | The probability that the frame shows the OU viseme class (phonemes: ou, as in book). | OU | ou |

## Gaze

- **Signals:** `gaze_{in,out,up,down}_{left,right}`, each from 0 to 1. "In" means toward the nose. "Out" means toward the temple.
- **Meaning:** the fraction of the source's maximum gaze in that direction. The value describes eye rotation, or the eyelid movement that goes with it, as the source reports it. No angle is claimed, and no curve is claimed.
- **Why both rotation and eyelids:** ARKit's eye-look coefficients describe eyelid movement (`apple_blendshapes`), and FB2 describes eye rotation (`xr_fb2` lines 643-649). A definition that says rotation only would add a claim that today's ARKit → Unified Expressions map does not make.
- **Whose side.** Apple names left and right from the face, so `eyeLookInLeft` (left eyelids, rightward gaze) is toward the nose (`apple_blendshapes`, Discussion). FB2's figure for EYES_LOOK_LEFT_L turns the subject's own left eye toward the temple (record `xr_fb2_fig_eyes_look_left_l`).
- **FB2 names:** LOOK_LEFT_L → `gaze_out_left`, LOOK_RIGHT_L → `gaze_in_left`, LOOK_LEFT_R → `gaze_in_right`, LOOK_RIGHT_R → `gaze_out_right`. Today's `fb2_gaze.to_arkit` and the Godot OpenXR vendors plugin route the values the same way (`godot_vendors_fb2` lines 201-208).
- **FB2 out-map helpers.** The FB2 gaze out-map nets each opposing pair through 4 helper values, with today's orientation and knots: `rcef.intermediate.gaze_in_minus_out_left`, `gaze_in_minus_out_right`, `gaze_up_minus_down_left` and `gaze_up_minus_down_right`. They replace today's 4 helpers, `rcef.intermediate.arkit_gaze_in_minus_out_L`, `arkit_gaze_up_minus_down_L`, `arkit_gaze_in_minus_out_R` and `arkit_gaze_up_minus_down_R` (`data/intermediate.toml`), which get tombstones when the direct maps are retired.
- **No exclusivity claim.** FB2 says that only one of two opposing directions is non-zero (`xr_fb2` lines 648-649). The canonical set states no such constraint, so the FB2 gaze in-hop carries the loss `fb2_gaze_exclusive`. The FB2 out-map keeps only the difference of each opposing pair. When both directions of a pair are non-zero, each FB2 output loses up to the smaller of the two values.
- **Rounding on the FB2 out-map.** The four outputs on the negative knot segment may change by up to 2⁻⁵⁴ when below 0.5, and values at or below 2⁻⁵⁴ become 0. The design goal is that these values equal those of today's `arkit_gaze.to_fb2`; the pre-registered comparison tests this.
- **Why directions, not signed angles:** the design keeps the values of every current gaze route (the comparison tests this), and FB2's 0 to 1 range stays. **Why in and out:** the names do not change under mirroring, and they match ARKit, Unified Expressions and Godot.
- **No FACS code on gaze.** FACS 61 and 62 turn both eyes left or right together. Which eye turns toward the nose depends on whose "left" Wikipedia means, and the article does not say. Public crosswalks disagree on it. So the gaze signals have no `facs_au` for now. A later step may add 61-64 with the loss key `facs_side_frame_unresolved`.

## Visemes

- Visemes are speech classes, not muscle actions. So they are a separate profile, `rcef.canonical_viseme`.
- The values are class probabilities, as META defines them (`xr_visemes` lines 104-107). There is no neutral per signal. Silence is `sil` = 1; META lists SIL as neutral (`xr_visemes` lines 142-143).
- The rules of [Meaning of 0, 1 and neutral](#meaning-of-0-1-and-neutral) do not apply.
- **From VRM:** VRM's vowel presets are weights authored per model. The in-map treats them as probabilities. There is no sum constraint (aa = 1 and oh = 1 sum to 2), and VRM gives no `sil`.
- **To META from another source:** the out-map writes the five vowels only. It never claims META validity: it writes no `isValid`, and it labels the frame "META validity not asserted". The loss reads: "consonant classes not produced; outputs may sum to 0 or above 1; META validity contract (sum 1 when valid; invalid arrays are zero) not met".

## Eye closure from VRM and VRCFaceTracking

- **VRM `blink` is not read.** VRM has `blinkLeft`, `blinkRight` and `blink`, which closes both eyes (`vrm_expressions` lines 177-179). The VRM in-map reads only `blinkLeft` and `blinkRight`. It declares the loss "VRM blink (both eyes) not read; when a model drives only blink, eye_close reads open", and the route lists a non-zero `blink` as dropped. Toward VRM, the out-map writes `blinkLeft` and `blinkRight` and leaves `blink` unset, with today's loss.
- **VRM side.** Both VRM blink hops keep today's caveat, "VRM gives no normative side; on the VRM 1.0 Twist sample blinkLeft moves the avatar's own left eyelid", and add the loss key `vrm_blink_side_unresolved` ([audit](canonical-set-audit.md#vrm)).
- **VRCFaceTracking eye.** `eye_close` is 1 − `Openness`. `Openness` 1 is taken as `eye_close` 0, relaxed open lids, but VRCFaceTracking does not say that 1 is neutral (loss key `vrcft_eye_openness_neutral_unresolved`). An `Openness` outside 0 to 1 would give a value outside the canonical domain of 0 to 1, so the hop is designed to refuse it.

## No equivalent

RCEF never shows a bare "-" for a missing value. This departs from RCSF, whose `joints.csv` uses "-" (`f6c3ea8`). A "-" cannot say why a value is missing. Each cell of the generated wide table shows one of these:

- a formula: `= X`, `mean(X,Y)`, `copy of X` or `net(X−Y)`;
- or the provider signal's own disposition, with its own `metadata.reason`:
  - `unsupported`: no executable mapping is supported; see the reason. Some providers have the value but mark it unused (`profiles/vrcft.artist.base.toml` lines 1579-1629);
  - `unresolved`: not researched, or not enough evidence;
  - `excluded`: out of scope.

The table never applies one note to every cell.

## What the set does not claim

- **No measured quantities:** no shared or measured gain, response curve or angle, and no physical length except the pupil diameter. In-between values are only assumed to correspond, per hop.
- **No equivalence:** not equal geometry on any rig, not the same pose across providers, not that shapes add up, not that opposing gaze directions are possible together, and not that sources agree at 0 and 1 (this is assumed).
- **No status:** no FACS, MPEG-4 or OpenXR conformance, no completeness, no outside approval or endorsement, and no claim that everyone must adopt it. The status `accepted` is RCEF's own status only ([How the set grows](#how-the-set-grows)).
- **No FACS coding.** RCEF values are not FACS scores, and RCEF does not code faces ([facs-intensity.md](facs-intensity.md)).

## Format neutrality

- **Where the split comes from.** The face signals have FB2's degrees of freedom, because FB2 is at least as fine as ARKit in every current mapping: all 52 ARKit outputs come from FB2 by a copy or a mean. The definitions are RCEF's own. They use FACS action units as a reference, and the [audit](canonical-set-audit.md) records every difference from every provider, FB2 included, and from every FACS crosswalk that a hop cites.
- **Narrower than RCSF's coverage.** RCSF aims to include most distinct joints across all the standards it analysed (RCSF `proposal.md` line 70, `f6c3ea8`). RCEF's rule is narrower: one signal for each distinct quantity that an expression set in this first phase writes, at its finest side or quadrant split. The Unified Expressions and Godot part shapes, MediaPipe and the [planned sets](expression-sets.md#planned-expression-sets) wait for later.
- **FACS is in the first phase.** It is a public code list that does not belong to one provider. RCEF uses only its code numbers and names, as facts. The canonical definitions stay RCEF's own text.
- **Departures from RCSF conventions,** each with a reason: snake_case IDs ([Names and IDs](#names-and-ids)) and three markers instead of "-" ([No equivalent](#no-equivalent)).
- **Neutral ground.** RCSF describes itself as neutral territory for standards organizations, and its design avoids favouring one standard (RCSF `proposal.md` lines 74 and 107, `f6c3ea8`). RCEF takes the same aim.
- **Review.** The Forum's 3D Assets working group reviews the meaning. Release depends on its acceptance. RCSF maintainers are asked to align.
- **RCSF sources:** `README.md` line 9, `proposal.md` lines 70, 74 and 107, and `joints.csv`, all at RCSF commit `f6c3ea8`. They are cited through the existing `rcsf_readme` record and a new `rcsf_proposal` record at the same commit.

## How the set grows

### Version and status

- Profile metadata holds `vocabulary_version = "1.0"` and `vocabulary_status = "draft"`. The calibration strings carry `v1`.
- Acceptance changes only `vocabulary_status`, to `"accepted"`. It never changes IDs, calibration strings or maps.
- `"accepted"` means only that the project's release owners and the 3D Assets working group accepted the vocabulary for RCEF, after the meaning review that [GOVERNANCE.md](../GOVERNANCE.md) requires. It is not a standard, an outside approval or an endorsement.
- Version 1.x may only add signals. Each addition raises the minor version.

### Whole actions first

A version 1 signal stands for the whole action. For example, `brow_lower` is the whole brow lowering, and `lip_corner_pull` is the whole corner pull. When a source with finer parts joins, for example Unified Expressions BrowLowerer and BrowPinch, each part gets a new ID. That source's in-map then also writes the version 1 total.

**Base shapes only.** Blended or combined shapes are never canonical signals. The out-maps of this first phase write base shapes only, and the consumer computes any blended shape from them: for example Unified Expressions BrowDown (0.75 BrowLowerer + 0.25 BrowPinch) and MouthSmile (0.8 MouthCornerPull + 0.2 MouthCornerSlant) (`vrcft_simple_expressions`). Blended out-maps wait until hop weights other than powers of two are allowed.

### Group splits

If a later source cannot fill a whole group, RCEF splits the group into smaller groups with new out-map IDs. The old out-map IDs get tombstones. An in-map never writes a made-up 0 to fill a group.

### Reserved names

These short names are reserved for actions that no first-phase source writes. They are not signals yet. Each becomes a version 1.x signal when a source needs it, with its own definition and audit rows.

| Reserved short names | Source of the action |
|---|---|
| `nasal_dilate_{left,right}`, `nasal_constrict_{left,right}` | Godot `FT_NASAL_DILATION_*`, `FT_NASAL_CONSTRICT_*` (`godot_enum` lines 78-81) |
| `jaw_backward`, `jaw_clench`, `jaw_mandible_raise` | Godot `FT_JAW_BACKWARD`, `FT_JAW_CLENCH`, `FT_JAW_MANDIBLE_RAISE` (lines 93-95) |
| `lip_suck_corner_{left,right}` | Godot `FT_LIP_SUCK_CORNER_*` (lines 100-101) |
| `upper_lip_deepen_{left,right}` | Godot `FT_MOUTH_UPPER_DEEPEN_*` (lines 114-115) |
| `tongue_up`, `tongue_down`, `tongue_right`, `tongue_left`, `tongue_roll`, `tongue_bend_down`, `tongue_curl_up`, `tongue_squish`, `tongue_flat`, `tongue_twist_right`, `tongue_twist_left` | Godot tongue directions (lines 137-147) |
| `pupil_dilate_{left,right}`, `pupil_constrict_{left,right}` | Godot `FT_EYE_DILATION_*`, `FT_EYE_CONSTRICT_*` (lines 64-67) |
| `soft_palate_close`, `throat_swallow`, `neck_flex_{left,right}` | Godot lines 148-151 |
| `lips_part` (25), `mouth_stretch` (27), `nasolabial_deepen` (11), `sharp_lip_pull` (13), `nostril_dilate` (38), `nostril_compress` (39), `neck_tighten` (21) | FACS codes with no canonical signal (`facs_wikipedia`) |

Some pairs may name one action: Godot nasal dilation and constriction and FACS 38 and 39, and Godot upper deepen and FACS 11. The audit decides this before either name becomes a signal, and only one signal is added per action.

## Calibrated MediaPipe records

A future MediaPipe calibration record that passes its held-out test becomes a MediaPipe in-hop (`mediapipe_<group>.to_rcef`), never a direct MediaPipe → ARKit map. The in-hop cites the record and the ARKit in-hop's audit rows. `tools/calibration/k4_record.py` stays as it is until a record passes. Then it changes under a new `code_commit`, and the record is frozen again. [calibration/README.md](../calibration/README.md#mappings-that-cite-a-record) states the same rule.

## FACS

FACS is the Facial Action Coding System. Other expression sets name their shapes after its action units: Roblox calls its face poses FACS poses (`roblox_poses`), and many FB2 names, such as INNER_BROW_RAISER, match Wikipedia's FACS names, here AU1 "Inner brow raiser" (`facs_wikipedia` raw line 89), although the FB2 text never names FACS. FACS publishes no numeric interface. So `facs.code` is RCEF's own encoding of public code numbers. "FACS" here means facial action codes; the profile names FACS code numbers from a public list. It is not FACS coding, and its values are not FACS scores.

**Source.** The code numbers, names, table membership and letters come from the Wikipedia article "Facial Action Coding System", revision 1357638399, as facts (record `facs_wikipedia`, CC-BY-SA-4.0). No article prose is copied. The FACS manual is not read, quoted or paraphrased ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)).

**Profile `facs.code`:**

- **IDs:** `facs.code.au<NN>` with two digits, plus `_left` or `_right` on sided signals: for example `facs.code.au01_left`, `facs.code.au17` and `facs.code.au30_left`. "au" follows the column header of the Wikipedia tables, "AU number".
- **`native_id`:** FACS notation, for example `L1`, `R1`, `17` or `L30`.
- **Label:** for example "AU 1 Inner brow raiser, left". Names are as Wikipedia gives them. RCEF does not claim a FACS edition. `aligned_names` holds the Microsoft Rocketbox shape names, for example `AU_18_LipPuckerer`, as facts.
- **Rows: 92.**
  - 49 `mapped` signals: 21 codes per side (1, 2, 4, 5, 6, 7, 9, 10, 12, 14, 15, 16, 18, 20, 22, 23, 24, 28, 34, 35, 43), so 42 signals; 5 shared codes (8, 17, 19, 26, 29); and 2 directions, `au30_left` and `au30_right` (side `shared`; the suffix names the direction, as on `jaw_sideways_*`).
  - 25 `unresolved` rows, one each, side `shared`: 11, 13, 21, 25, 27; 31, 32, 33, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46; 61, 62, 63, 64, 65, 66, 69. Each reason names the gap, for example "no canonical signal" or "the codec reads it as AU43".
  - 18 `excluded` rows: head codes 51-58 (head pose is out of scope) and gross codes 50, 80, 81, 82, 84, 85, 91, 92, 97\* and 98\* (behaviour events, not face weights).
  - Not rows: code 0 "Neutral face" (it is the all-zero frame), the 10 "M" codes (timed combinations) and the visibility codes 70-74 (handled by the [codec](facs-intensity.md#visibility-codes)).
- **Groups** follow the canonical groups they fill: `face` (37), `cheek_puff` (2), `jaw_thrust` (1), `jaw_sideways` (2), `blink` (2), `cheek_suck` (2), `lip_tighten` (2) and `tongue_out` (1).
- **Sides.** Wikipedia allows an L or R before a code (raw line 78). Which codes FACS lets be one-sided is in the closed manual. RCEF splits a code by side exactly where the canonical signal is split by side, so a FACS → canonical → FACS round trip loses nothing. AU22 and AU28 are split by side only, because FACS has no upper/lower split.
- **Side note** on every sided row: "FACS names L and R without saying whose side; RCEF reads them as the subject's own (assumption; loss key `facs_side_frame_unresolved`)".
- **Fields:** `value_type = "scalar"`, `units = "1"`, `domain = {min = 0.0, max = 1.0}`, `neutral = 0.0`, `evidence_status = "proposed"`. Evidence is `facs_wikipedia`, plus `rocketbox_avatars` where `aligned_names` holds a Rocketbox name, and `facs_hager_2002` on the AU43 signals. The code numbers are facts, but the scalar encoding is RCEF's, so the signals are `proposed`.
- **Calibration strings.** Main codes: `rcef.facs.v1:au<NN>: 0 = absent (a scored frame does not list the code); 1 = intensity E, the maximum possible for the individual person (Wikipedia FACS, raw line 70); FACS defines only the ordered letters A-E and no numeric scale, so values between are an RCEF encoding (docs/facs-intensity.md), not a FACS measure`. Gross codes 29, 30, 34, 35 and 43: `… 1 = the action at its fullest, as RCEF assumes; the source gives no intensity scale for gross behaviour codes (raw lines 65, 224) …`. AU43 takes the gross form, because Wikipedia lists 43 as a gross code (raw line 257). A frame that is not coded is left out, never 0.
- **Profile metadata:** `vocabulary_version = "1.0"` and `vocabulary_status = "draft"`, and the text "FACS code numbers and names from a public list; not FACS coding; values are not FACS scores".

**Maps.** Both directions, 102 mappings in 16 maps.

- **In-maps (53 mappings):** 38 sided copies (19 codes × 2), 8 fan-outs (AU22 and AU28 per side, to the upper and the lower part), 5 shared copies and the 2 AU30 directions.
- **Out-maps (49 mappings):** 38 sided copies, 4 means (AU22 and AU28 per side), 5 shared copies and the 2 AU30 directions.
- **Operators:** `affine(1,0)` copies and fan-outs, and `weighted_sum [0.5, 0.5]` means. `identity` is not possible, because the FACS calibration string differs from the canonical one. Giving FACS the canonical string would hide the ordinal encoding.
- **Evidence on each hop:** `facs_wikipedia` and `rcef_canonical_v1`, plus `facs_hager_2002` on the AU43 hops. No crosswalk record goes on a FACS hop.
- **Not available toward FACS** (no FACS code): `mouth_shift_*`, `chin_raise_upper_lip`, the 8 gaze signals, the 6 tongue positions, the pupils and the visemes.
- **FACS codes never written:** 25 and 27 (all opening is written as 26), 41, 42, 44, 45 and 46 (all closure is written as 43), and every other `unresolved` or `excluded` row.

**Losses on FACS hops:**

- every hop: `facs_ordinal_intensity` ("FACS intensity is ordinal (letters A-E, E the person's maximum); the numeric value is an RCEF encoding; equal steps are not claimed; no gain is measured");
- every sided hop and both AU30 hops: `facs_side_frame_unresolved`;
- the AU30 hops: `facs_au30_direction_unresolved`; the AU17 hops: `facs_au17_no_split`; the AU26 hops: `facs_mouth_opening_split`; the AU43 hops: `facs_eyelid_events`;
- the 18 hops of codes 29, 30, 34, 35 and 43: `facs_gross_code_no_intensity`;
- AU22 and AU28: "symmetry is invented" on the 8 in-map fan-outs, and "asymmetry irrecoverable" on the 4 out-map means;
- AU19: "no stated length", as on every `tongue_out` hop.

**The `facs_au` field.** For each canonical signal, `facs_au` equals the code of the `facs.code` signal that the FACS in-map writes into it, and the reverse. A test checks this.

**What FACS fills.** FACS fills the canonical groups `face`, `cheek_puff`, `jaw_thrust`, `jaw_sideways`, `blink`, `cheek_suck`, `lip_tighten` and `tongue_out`. It fills none of `mouth_shift`, `chin_raise_upper_lip`, `gaze`, `tongue_place`, `pupil_mm` or the viseme groups. So FACS → ARKit writes 41 of the 52 ARKit outputs, and FACS → FB2 writes 53 of the 70 FB2 outputs.

## Public evidence

These existing records support the definitions and the audit: `roblox_poses`, `xr_fb2`, `xr_visemes`, `xr_registry`, `apple_blendshapes`, `vrcft_docs_shapes`, `vrcft_data`, `vrcft_code_parameters`, `vrcft_simple_expressions`, `vrm_expressions`, `godot_enum`, `godot_vendors_fb2`, `ict_facekit` and `rcsf_readme` ([references.md](../references.md)).

The data change that adds the profiles also adds these records. Each image record is cited, never copied.

| Record | Source | Licence or terms |
|---|---|---|
| `rcef_canonical_v1` | This document; original RCEF work | CC-BY-SA-4.0 |
| `facs_wikipedia` | Wikipedia, "Facial Action Coding System", [revision 1357638399](https://en.wikipedia.org/w/index.php?title=Facial_Action_Coding_System&oldid=1357638399); raw wikitext SHA-256 `04e85bb6602305aa367c5d2b3f3f4fc4b78d8c213e73303f2694225453f5733a`. Locators: raw lines 69-75 (intensity letters), 78 (side modifiers), 82-142 (main codes), 144-176 (head movement codes), 178-204 (eye movement codes), 206-221 (visibility codes), 223-284 (gross behavior codes) | CC-BY-SA-4.0 |
| `rcsf_proposal` | RCSF `proposal.md` at `f6c3ea8a00d4901496326b4a6fe6a24913a563c6` | CC-BY-SA-4.0 (stated in the RCSF README) |
| `xr_fb2_fig_eyes_closed_l` | OpenXR-Docs `5a82d45`, `specification/sources/images/XR_FB_Face_Expression_2_Eyes_Closed_L.png`, SHA-256 `78456d18833a58cdfe5edb54aeb31c2e5a3601de32f78d74b3f4b33a367efb12` | CC-BY-4.0 |
| `xr_fb2_fig_eyes_look_left_l` | Same folder, `XR_FB_Face_Expression_2_Eyes_Look_Left_L.png`, SHA-256 `30794e175a00ff7c0d13e8a537d75315c4477359dae910ceef872f49dbe3b8cb` | CC-BY-4.0 |
| `xr_fb2_fig_mouth_left` | Same folder, `XR_FB_Face_Expression_2_Mouth_Left.png`, SHA-256 `07465af6b55f6fbc835b05b3d51401300705b24d115ca8425d1d6d1a9272d4f0` | CC-BY-4.0 |
| `vrcft_fig_eyeclosedleft` | VRCFaceTracking docs `3036f46`, `docs/tutorial-avatars/tutorial-avatars-extras/img/avatar/avatar_ref_eyeclosedleft.png`, SHA-256 `128dc5f1dad57f703c57aded753bbaa621a46d28fbbed795f5cf5b62f98b3cbb` | Reference only |
| `vrcft_fig_eyelookoutleft` | Same folder, `avatar_ref_eyelookoutleft.png`, SHA-256 `22fbb1ca0adefec555b8b86e5c317954b98de5efa97df5aba60c96a041583759` | Reference only |
| `vrcft_fig_mouthupperleft` | Same folder, `avatar_ref_mouthupperleft.png`, SHA-256 `60c5a1c618f10998ddae848868c9aa609b3711a040a927cee098478b53157cff` | Reference only |

The data change that adds `facs.code` adds four more records: `facs_hager_2002` (the FACS publisher's page on the 2002 edition, an archived copy of 2008-12-18; reference only), `rocketbox_avatars` (Microsoft Rocketbox at `0943055`, MIT; the 48 `AU_*` shape names), `pyfeat_au_reference` (Py-Feat `docs/pages/au_reference.md` at `4ebb4ec`, MIT) and `ozel_arkit_facs` (Melinda Ozel, "ARKit to FACS", reference only). The last two support audit notes only; no hop cites them.

## Effect on compatibility

- New profiles and maps are added. Nothing changes in the existing profiles or values.
- The 7 direct maps, the 3 identity maps, the old `rcef.canonical` profile and its 21 signals, and the 4 old intermediate signals are retired later, with tombstones. Until then they stay as they are.
- Every hop is `approximate` and `proposed`, except the 4 pupil copies, which are `exact` and `verified_current`. So 19 of the 21 `verified_current` mappings in today's three identity maps have only `proposed` routes in their place.
- The design goal is that two-hop routes give the same values as today's direct maps on every output that both write. A pre-registered comparison tests this before the direct maps are retired; until then it is a goal, not a result.

## Alternatives considered

| Choice | Chosen | Alternative and why not |
|---|---|---|
| Gaze form | 8 directional fractions | Signed yaw and pitch: changes today's values |
| Gaze names | in and out | Subject left and right: the names change under mirroring |
| Granularity | the finest first-phase source | Add the Unified Expressions parts now: no first-phase source writes them |
| Visemes | a separate profile with two groups and no neutral | Inside the expression profile: visemes are classes, not actions |
| Pupil | millimetres, outside the unitless exports | Back to `unresolved`: loses an exact route |
| ID style | snake_case | PascalCase, like RCSF: matches one provider's style |
| `lips_toward` | follows FB2: lips meet at any jaw opening | A jaw-relative corrective, like Unified Expressions: adds a loss on every FB2 hop |
| Blink name | `eye_close` | `eye_blink`: a blink is an event, the signal is a state |
| FACS | an expression set with maps | A cross-reference column only: no FACS route |
| FACS intensity | a scalar from 0 to 1 and a documented letter codec outside the pack | `piecewise_linear` steps: false precision |
| `face` group | split into six groups | One `face` group: FACS and `XR_ML_facial_expression` could write no face value |

## Tests

These tests come with the data change:

- unique short names across both profiles; each unitless expression signal has neutral 0, range 0 to 1 and the metadata fields; gaze has the gaze calibration string; visemes have no neutral; the pupils are the only `verified_current` signals; groups partition each profile; signals with `facs_au` cite `facs_wikipedia` and have `facs_table`;
- an audit row for each pair of canonical signal and mapped provider, and for each pair of signal with a FACS code and cited FACS crosswalk;
- each hop's assumption clause matches its operator; every assumption of today's maps has a home on each route ([assumption catalogue](canonical-set-audit.md#assumption-catalogue));
- the side and direction suffixes agree between the two ends of every mapping;
- a capability matrix: for each set (FACS, FB v1, `XR_ANDROID_face_tracking` and `XR_ML_facial_expression`, from a committed list of their names with record and locator), which canonical groups it can fill, plus a synthetic partial source;
- a FACS-crosswalk record goes only on hops of the provider whose names it uses (`ict_facekit`: ARKit hops only), and no crosswalk record goes on a FACS hop;
- for `facs.code`: 92 rows with the dispositions 49, 25 and 18; the ID pattern; the calibration strings; `facs_au` agrees with the FACS maps.

## Open questions

- Do the FB2 JAW_SIDEWAYS_LEFT and Unified Expressions JawLeft figures show the subject's own left? The FB2 figure, enlarged, shows the chin and lower lip moving toward the viewer's right, that is the subject's own left, which agrees with the FB2 text. The JawLeft figure has no neutral figure beside it, so it is hard to read. Until a figure contradicts its text, the jaw rows follow the text.
- Which way does Unified Expressions MouthLowerDown move? The name says down; the description says up.
- Does `lips_toward` act as a jaw corrective, and what does a non-zero value mean at `jaw_drop` = 0? Do ARKit `mouthClose` and FB2 LIPS_TOWARD agree on this?
- Does any public FACS source say whose left and right the L and R modifiers, and AU30, mean?
- Are the FACS letter steps equal? Only the closed manual says. RCEF never assumes more than its codec does.
- What are the real ranges of VRCFaceTracking `Openness` and `PupilDiameter_MM`?
- Should the tongue-position signals ever be linked to the Unified Expressions tongue directions?
- Who in the working group reviews meaning, and how long does it take?
