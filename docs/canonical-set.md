<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Canonical expression set (draft)

Original documentation: CC-BY-SA-4.0. Copyright (c) 2026 Metaverse Standards Forum.

**Author affiliation: to be added by the release owners before this document goes to the working group.**

**Status:** a draft proposal for review. Vocabulary version `1.0`, status `draft`. Data 0.5.0 holds the expression part: the profile `rcef.canonical_expression` with its 72 signals, and the maps of ARKit, FB2, Unified Expressions, VRCFaceTracking eye data, VRM blinks and FACS codes, with the [FACS](#facs) profile `facs.code`. It also holds the viseme part: the profile `rcef.canonical_viseme` with its 16 signals and the maps of META and VRM vowels, and the [viseme pose bridge](#viseme-pose-bridge) from the viseme set to the expression set. Data 0.5.0 retires the direct maps and the older `rcef.canonical` set of 21 signals, with tombstones in [retired-ids.csv](retired-ids.csv). In this document, "today's maps" are those retired direct maps. They stay frozen in `tests/fixtures/baseline-dea1713.pack.json` for the [A/B comparison](../ab/README.md).

This document uses the proposal form of [GOVERNANCE.md](../GOVERNANCE.md): the problem, the proposal, the public evidence, the effect on compatibility, the alternatives, the tests and the open questions. Two documents go with it:

- the [definitions audit](canonical-set-audit.md), which compares each canonical signal with each public source that maps it, and records the assumptions of today's maps;
- [facs-intensity.md](facs-intensity.md), which says how FACS intensity letters become numbers.

## Problem

Before data 0.5.0, RCEF mapped one provider directly to another: 7 maps with 187 cross-provider mappings. Each new pair needed a new map. Where no map existed, the only route was through ARKit. The 21 signals of the old `rcef.canonical` set each kept their provider's calibration, so they could not act as a common point between providers.

RCSF does this job for skeletons. It calls itself a pivot for translating between formats, not a new universal skeleton that everyone must adopt (`rcsf_readme`, README line 9, RCSF `f6c3ea8`). This proposal does the same for face expressions.

## Proposal in brief

- Two new profiles: `rcef.canonical_expression` with 72 signals (70 without units, 2 in millimetres), and `rcef.canonical_viseme` with 16 signals: 15 IPA shape classes (14 speech classes and `sil`) and one aggregate, `alveolar_floor`.
- Every translation runs source → canonical set → target. An in-map turns a provider's values into canonical values. An out-map turns canonical values into a provider's values.
- The FACS code numbers become an expression set of their own, `facs.code`, with in-maps and out-maps ([FACS](#facs)).
- RCEF is a pivot for translating between expression sets. It is not a set that everyone must adopt. Each canonical signal has a declared meaning, but no shared or measured gain.

## Names and IDs

- **Expression IDs:** `rcef.canonical_expression.<short_name>`, in lowercase snake_case. Sides use `_left` and `_right`. Lip quadrants use `_upper_left`, `_upper_right`, `_lower_left` and `_lower_right`.
- **Viseme IDs:** `rcef.canonical_viseme.<class>`, in ASCII snake_case, named by IPA place of articulation or vowel shape: `sil`, `bilabial`, `labiodental`, `dental`, `alveolar_sibilant`, `postalveolar`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal`, `rhotic`, `vowel_open`, `vowel_mid_spread`, `vowel_close_spread`, `vowel_mid_rounded`, `vowel_close_rounded`, and the aggregate `alveolar_floor`. IPA symbols appear only in labels and metadata. Each viseme signal has a `definition` that names any difference between its ID and its members.
- Short names are unique across both profiles.
- The prefix of each ID is its profile ID. The new IDs do not reuse the `rcef.canonical.` namespace.
- An ID never holds a version. Versions are in the calibration string and in the profile metadata.
- An ID never changes. A new meaning gets a new ID. A retired ID needs a tombstone ([GOVERNANCE.md](../GOVERNANCE.md)).
- New IDs become permanent at the first release that contains them.
- **Labels** are plain English, for example "Inner brow raise, left". The label carries the readable name.
- **Why snake_case.** RCSF uses readable names such as "Hips" (RCSF `joints.csv`, `f6c3ea8`). RCEF uses snake_case IDs instead, as a neutral style: ARKit and VRM use lowerCamelCase, FB2 uses UPPER_SNAKE and VRCFaceTracking Unified Expressions uses PascalCase. One-word IDs look the same in any lowercase style. For example, the viseme class `dental` reads the same in every lowercase style.

## Fields

Every canonical signal has these fields.

| Field | Value |
|---|---|
| `value_type`, `units`, `domain`, `neutral` | `scalar`, `"1"`, `{min = 0.0, max = 1.0}`, `0.0`. Exceptions: visemes use `units = "probability"` and have no `neutral` field. The pupils use `units = "mm"`, `domain = {}` and no `neutral` field. |
| `calibration` | The string for the signal's class (below). |
| `side` | `left`, `right` or `shared`, from the subject's own face. On `jaw_sideways_*` and `mouth_shift_*` the suffix names a direction: `_left` means "toward the subject's own left". Their side is `shared`, because the whole jaw or mouth moves. |
| `region` | As in the [signal table](#expression-signals). |
| `coupling` | None on expression signals. On visemes it is a label only: `probability_simplex` on the 15 partition signals, `aggregate_of_simplex_classes` on aggregates and `refinement_of_simplex_class` on refinements. |
| `disposition` | `mapped` once a mapping uses the signal. |
| `evidence_status` | `proposed`. The two pupil signals are `verified_current`, and their evidence holds only `verified_current` records (`rcef_canonical_v1`, `vrcft_data`). msf-character-tools needs this for a `verified_current` mapping ([architecture.md](architecture.md#map-compilation-is-stricter-than-inventory-validation)). |
| `evidence` | `rcef_canonical_v1`, the original record for this vocabulary. Signals with a FACS code also cite `facs_wikipedia`. The jaw and mouth-shift signals also cite `xr_fb2`, the FB2 figure records and `apple_blendshapes` for their direction wording. |
| `metadata` | `definition` (RCEF's own text), `zero`, `one`, `facs_au` (empty where the table shows none), `facs_table` (`main` or `gross_behavior`), `group`, `aligned_names` (provider names, as facts) and `audit` (a pointer to the [audit](canonical-set-audit.md) rows). Viseme signals have their own fields ([Viseme metadata](#viseme-metadata)). |

Both profiles also have `vocabulary_version` and `vocabulary_status` in their metadata ([How the set grows](#how-the-set-grows)).

**Calibration strings:**

- **Expression signals:** `rcef.canonical.v1:<short_name>: declared 0 = neutral face, 1 = full activation of the action RCEF defines; assumed to agree with each source at 0 and 1; values between are passed through by the hop operator, and RCEF assumes, without evidence, that each source's in-between values correspond in this way; no measured gain or response curve`
- **Gaze:** `rcef.canonical.v1:<short_name>: fraction of the source's maximum gaze in this direction; source-relative; no angle and no curve claimed`
- **Viseme classes:** `rcef.canonical.v1:<short_name>: probability of the IPA shape class (docs/canonical-set.md) as the source reports it; no per-class neutral; rest is sil = 1`
- **Viseme aggregates:** `rcef.canonical.v1:<short_name>: sum of the IPA shape classes <classes>, clamped to [0,1]; not part of the simplex sum; no per-class neutral`
- **Viseme refinements:** `rcef.canonical.v1:<short_name>: probability of the IPA shape subclass (part of <parent>) as the source reports it; not part of the simplex sum`
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
| weighted_sum [1, 1, 1, 1] and clamp knots (viseme aggregate in-hop) | "the canonical value is the sum of the META classes SS, DD, NN and RR, clamped at 1" |

FACS hops start with their own assumption instead: "FACS intensity E, the maximum for the person, is assumed to be canonical 1, and 'absent' (a scored frame does not list the code) is assumed to be canonical 0; FACS defines only the ordered letters A-E, so values between are RCEF's encoding ([facs-intensity.md](facs-intensity.md)) and correspond as the operator passes them; no evidence supports this, and no response curve is measured". On the hops of the gross behaviour codes (29, 30, 34, 35 and 43) it reads: "the action at its fullest, as RCEF assumes, is canonical 1, and 'absent' (a scored frame does not list the code) is assumed to be canonical 0; the source gives no intensity scale for gross behaviour codes; FACS defines only the ordered letters A-E, so values between are RCEF's encoding ([facs-intensity.md](facs-intensity.md)) and correspond as the operator passes them; no evidence supports this, and no response curve is measured".

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
| `viseme_vowel` | 5 | `vowel_open`, `vowel_mid_spread`, `vowel_close_spread`, `vowel_mid_rounded`, `vowel_close_rounded` |
| `viseme_consonant` | 9 | `bilabial`, `labiodental`, `dental`, `alveolar_sibilant`, `postalveolar`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal`, `rhotic` |
| `viseme_rest` | 1 | `sil` |
| `viseme_aggregate` | 1 | `alveolar_floor` |

A META vowel never shares a group with a consonant or `sil`, so the VRM vowel route reads META's vowels only. A `viseme_refinement` group comes with the first refinement, and a `viseme_vowel_aggregate` group with the first vowel aggregate.

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
| `tongue_tip_interdental` | Tongue tip between the teeth | shared | Tongue | tongue_place | The tongue tip touches the upper teeth and shows between the teeth, as for META's TH viseme (canonical `dental`). | none | TONGUE_TIP_INTERDENTAL | none |
| `tongue_tip_alveolar` | Tongue tip behind the upper teeth | shared | Tongue | tongue_place | The tongue tip touches the back of the upper teeth, as for META's NN viseme (canonical `coronal_nasal_lateral`). | none | TONGUE_TIP_ALVEOLAR | none |
| `tongue_front_dorsal_palate` | Tongue front on the palate | shared | Tongue | tongue_place | The front of the tongue presses on the palate, as for META's CH viseme (canonical `postalveolar`). | none | TONGUE_FRONT_DORSAL_PALATE | none |
| `tongue_mid_dorsal_palate` | Tongue middle on the palate | shared | Tongue | tongue_place | The middle of the tongue presses on the palate, as for the DD viseme. FB2 describes DD's tongue this way; RCEF's `coronal_stop` is the IPA coronal class. | none | TONGUE_MID_DORSAL_PALATE | none |
| `tongue_back_dorsal_velar` | Tongue back on the palate | shared | Tongue | tongue_place | The back of the tongue presses on the palate, as for META's KK viseme (canonical `dorsal`). | none | TONGUE_BACK_DORSAL_VELAR | none |
| `pupil_diameter_mm_left` | Pupil diameter (mm), left | left | Pupils | pupil_mm | The diameter of the left pupil in millimetres, as the tracker reports it (VRCFaceTracking eye `Left.PupilDiameter_MM`). Units `mm`; no range is declared. | none | none | none |
| `pupil_diameter_mm_right` | Pupil diameter (mm), right | right | Pupils | pupil_mm | The diameter of the right pupil in millimetres, as the tracker reports it (VRCFaceTracking eye `Right.PupilDiameter_MM`). Units `mm`; no range is declared. | none | none | none |

### Viseme signals

The canonical visemes are classes of visible mouth shape, defined by the International Phonetic Alphabet (IPA). Each class is a set of IPA chart symbols (record `ipa_chart_doulos_2020`), and each of the 107 chart symbols belongs to exactly one class. [IPA chart assignment](#ipa-chart-assignment) lists every symbol with its chart cell and evidence level. The values are probabilities ([Visemes](#visemes)).

There are 15 partition signals: 14 speech classes and `sil`. Together they partition the chart, and only they carry `coupling = "probability_simplex"`. The 16th signal, `alveolar_floor`, is an aggregate: its value is the sum of four partition classes, clamped at 1 ([Viseme aggregates](#viseme-aggregates)).

| Short name | Label | Group | IPA chart symbols | By rule | Definition | Shape class | Shape floor | META | VRM |
|---|---|---|---|---|---|---|---|---|---|
| `sil` | Rest: no speech articulation | viseme_rest | none | none | No speech articulation: silence and pauses. sil is not an IPA segment, and RCEF asserts no mouth pose for it. | rest | rest | SIL | none |
| `bilabial` | Bilabial: lips closed or close together | viseme_consonant | p b m ʙ ɸ β ʘ ɓ | β̞; pʼ; the double articulations k͡p ɡ͡b ŋ͡m | RCEF class: bilabial consonants; the lips close or come close together. | bilabial | bilabial | PP | none |
| `labiodental` | Labiodental: lower lip to upper teeth | viseme_consonant | ɱ ⱱ f v ʋ | p͡f b͡v | RCEF class: labiodental consonants; the lower lip touches the upper teeth. | labiodental | labiodental | FF | none |
| `dental` | Dental fricative, interdental or linguolabial: tongue tip visible | viseme_consonant | θ ð | interdental coronals (t̪̟ n̪͆) and linguolabials (t̼ p̼); t͡θ d͡ð | RCEF class: dental fricatives, interdental and linguolabial coronals; the tongue tip shows at or between the teeth, or at the upper lip. IPA dental stops, nasals and laterals (t̪ d̪ n̪ l̪) stay in the coronal classes. | dental | dental | TH | none |
| `alveolar_sibilant` | Alveolar sibilant: teeth close | viseme_consonant | s z | t͡s d͡z; sʼ | RCEF class: alveolar sibilants; the teeth are close together. | alveolar_sibilant | alveolar_floor | SS | none |
| `postalveolar` | Postalveolar sibilant: lips forward, teeth close | viseme_consonant | ʃ ʒ ʂ ʐ ɕ ʑ ɧ | t͡ʃ d͡ʒ t͡ɕ d͡ʑ ʈ͡ʂ ɖ͡ʐ; sʷ zʷ | RCEF class: postalveolar sibilants, including retroflex and alveolo-palatal sibilants; the lips push forward and the teeth are close. | postalveolar | postalveolar | CH | none |
| `coronal_stop` | Coronal stop or tap | viseme_consonant | t d ʈ ɖ ɾ ɽ ǀ ǃ ǂ ɗ | tʼ; t̪ d̪ | RCEF class: coronal stops and taps, including retroflex stops and the coronal clicks; no lip target of their own. | coronal_stop_nasal_lateral | alveolar_floor | DD | none |
| `coronal_nasal_lateral` | Coronal nasal or lateral | viseme_consonant | n ɳ ɬ ɮ l ɭ ǁ ɺ | ɫ; t͡ɬ d͡ɮ; n̪ l̪ | RCEF class: coronal nasals and laterals, including retroflex ones and the lateral click; no lip target of their own. | coronal_stop_nasal_lateral | alveolar_floor | NN | none |
| `dorsal` | Dorsal and laryngeal: no front target | viseme_consonant | c ɟ k ɡ q ɢ ʔ ɲ ŋ ɴ ʀ ç ʝ x ɣ χ ʁ ħ ʕ h ɦ ʎ ʟ ʄ ɠ ʛ ʜ ʢ ʡ | kʼ; k͡x | RCEF class: dorsal consonants, including pharyngeal, epiglottal and glottal consonants (no front target). | dorsal | dorsal | KK | none |
| `rhotic` | Coronal rhotic | viseme_consonant | r ɹ ɻ | ɚ ɝ (ə˞ ɜ˞); ɹʷ | RCEF class: the coronal rhotics r ɹ ɻ and the r-coloured mid-central vowels; the uvular ʀ ʁ are dorsal. A partition class kept for META RR; in the shape floor it goes with the coronals. | rhotic | alveolar_floor | RR | none |
| `vowel_open` | Open and near-open unrounded vowels | viseme_vowel | æ ɐ a ɑ | a˞ | RCEF class: open and near-open unrounded vowels only (the open rounded ɒ ɶ are in vowel_mid_rounded). | vowel_open | open | AA | aa |
| `vowel_mid_spread` | Close-mid to open-mid unrounded vowels | viseme_vowel | e ɘ ɤ ə ɛ ɜ ʌ | ɘ˞ | RCEF class: close-mid, mid and open-mid unrounded vowels. | vowel_mid_spread | mid_spread | E | ee |
| `vowel_close_spread` | Close and near-close unrounded vowels and glides | viseme_vowel | j ɰ i ɨ ɯ ɪ | none | RCEF class: close and near-close unrounded vowels, and the glides j ɰ. | vowel_close_spread | close_spread | IH | ih |
| `vowel_mid_rounded` | Close-mid to open rounded vowels | viseme_vowel | ø ɵ o œ ɞ ɔ ɶ ɒ | o˞; eʷ eᵝ | RCEF class: close-mid to open rounded vowels, including the open ɒ ɶ by rounding. | vowel_mid_rounded | mid_rounded | OH | oh |
| `vowel_close_rounded` | Close and near-close rounded vowels and glides | viseme_vowel | ʍ w ɥ y ʉ u ʏ ʊ | kʷ tʷ hʷ kᵝ and other consonants with no lip target of their own when labialised or compressed; ɯᵝ jʷ | RCEF class: close and near-close rounded vowels, and the glides w ʍ ɥ. | vowel_close_rounded | close_rounded | OU | ou |
| `alveolar_floor` | Alveolar floor (aggregate) | viseme_aggregate | union of `alveolar_sibilant`, `coronal_stop`, `coronal_nasal_lateral` and `rhotic` | as its classes | RCEF aggregate: the alveolar and retroflex stops, taps, trills, rhotic approximants r ɹ ɻ (and ɚ ɝ by rule), nasals and laterals, the coronal clicks and s z; not θ ð or ʃ ʒ ʂ ʐ, which are coronal too. | none | alveolar_floor | SS + DD + NN + RR, clamped at 1 | none |

"By rule" lists symbols that are not single chart cells and join the class by the [IPA rules](#ipa-rules). The META and VRM columns name the provider classes that the hops copy, as facts.

**Visible shape.** The shape of each class, in RCEF's words. The sources are JALI's articulation rules (record `jali_2016`), the IPA's description of protruded and compressed rounding (record `wikipedia_roundedness`, raw lines 52-56) and META's reference images (records `xr_visemes_fig_*`); the rest is RCEF's articulatory inference.

| Short name | Lips | Teeth | Tongue | Jaw |
|---|---|---|---|---|
| `sil` | no pose asserted | no pose asserted | no pose asserted | no pose asserted |
| `bilabial` | closed for the stops, nasal, trill, click and implosive; close together but not closed for the fricatives | hidden | not visible | close |
| `labiodental` | the lower lip touches the upper teeth | upper teeth visible | hidden | close |
| `dental` | apart, neutral | slightly apart | tip visible at or between the teeth, or at the upper lip | slightly open |
| `alveolar_sibilant` | neutral to spread | close together, visible | hidden | narrowed |
| `postalveolar` | pushed forward or flared | close together | hidden | narrowed |
| `coronal_stop` | follow the neighbouring vowel | follow the neighbouring vowel | tip or blade raised to the teeth or the ridge; visible only with an open jaw | follows the neighbouring vowel |
| `coronal_nasal_lateral` | follow the neighbouring vowel | follow the neighbouring vowel | as for `coronal_stop`; the sides of the tongue are not visible from the front | follows the neighbouring vowel |
| `dorsal` | follow the neighbouring vowel | follow the neighbouring vowel | hidden | follows the neighbouring vowel |
| `rhotic` | no lip target of their own; some English speakers round slightly | slightly apart | hidden | mid-close |
| `vowel_open` | relaxed, with a wide vertical opening | lower teeth may show | low | open |
| `vowel_mid_spread` | spread or neutral | apart; upper teeth visible | hidden | mid |
| `vowel_close_spread` | spread, corners drawn back | close, often visible | hidden | close |
| `vowel_mid_rounded` | rounded: pushed forward for o ɔ ɵ ɞ, compressed for ø œ ɶ | mostly hidden | hidden | mid; open for ɒ ɶ |
| `vowel_close_rounded` | tightly rounded with a small opening: pushed forward for u ʉ ʊ w ʍ, compressed for y ʏ ɥ | hidden | hidden | close |

**Notes on shape classes and the floor.** The shape class and the shape floor are explained in [Why these classes](#why-these-classes-minimal-under-parity).

| Short name | Shape note | Shape-floor note |
|---|---|---|
| `alveolar_sibilant` | none | sibilant split mixed (7 of 14 maps); the DD and NN split in the merge band (4 of 15) |
| `coronal_stop` | manner split kept by 4 of 15 maps (Binnie, Kricos, Lee, Hazen); kept for META DD and NN | sibilant split mixed (7 of 14 maps); the DD and NN split in the merge band (4 of 15) |
| `coronal_nasal_lateral` | manner split kept by 4 of 15 maps (Binnie, Kricos, Lee, Hazen); kept for META DD and NN | sibilant split mixed (7 of 14 maps); the DD and NN split in the merge band (4 of 15) |
| `rhotic` | counted on English [ɹʷ]; IPA r ɹ ɻ show no attested visible difference from the coronals | split from the coronals (11 of 15) and from w (6 of 12) counted on English [ɹʷ]; IPA r ɹ ɻ are unlabialised with no lip target, so they go with the coronals by IPA definition (A) |
| `vowel_mid_rounded` | apart from ɑ in 2 of 5 count-matched English maps (mixed; some Northern Cities speakers make /ɔ/ unrounded); kept by rounding; ɒ ɶ contested (the least-rounded open vowels) | none |

## Gaze

- **Signals:** `gaze_{in,out,up,down}_{left,right}`, each from 0 to 1. "In" means toward the nose. "Out" means toward the temple.
- **Meaning:** the fraction of the source's maximum gaze in that direction. The value describes eye rotation, or the eyelid movement that goes with it, as the source reports it. No angle is claimed, and no curve is claimed.
- **Why both rotation and eyelids:** ARKit's eye-look coefficients describe eyelid movement (`apple_blendshapes`), and FB2 describes eye rotation (`xr_fb2` lines 643-649). A definition that says rotation only would add a claim that today's ARKit → Unified Expressions map does not make.
- **Whose side.** Apple names left and right from the face, so `eyeLookInLeft` (left eyelids, rightward gaze) is toward the nose (`apple_blendshapes`, Discussion). FB2's figure for EYES_LOOK_LEFT_L turns the subject's own left eye toward the temple (record `xr_fb2_fig_eyes_look_left_l`).
- **FB2 names:** LOOK_LEFT_L → `gaze_out_left`, LOOK_RIGHT_L → `gaze_in_left`, LOOK_LEFT_R → `gaze_in_right`, LOOK_RIGHT_R → `gaze_out_right`. The retired `fb2_gaze.to_arkit` routed the values the same way, and so does the Godot OpenXR vendors plugin (`godot_vendors_fb2` lines 201-208).
- **FB2 out-map helpers.** The FB2 gaze out-map nets each opposing pair through 4 helper values, with the orientation and knots of the retired `arkit_gaze.to_fb2`: `rcef.intermediate.gaze_in_minus_out_left`, `gaze_in_minus_out_right`, `gaze_up_minus_down_left` and `gaze_up_minus_down_right`. They replace that map's 4 helpers, `rcef.intermediate.arkit_gaze_in_minus_out_L`, `arkit_gaze_up_minus_down_L`, `arkit_gaze_in_minus_out_R` and `arkit_gaze_up_minus_down_R`, which data 0.5.0 retires with tombstones.
- **No exclusivity claim.** FB2 says that only one of two opposing directions is non-zero (`xr_fb2` lines 648-649). The canonical set states no such constraint, so the FB2 gaze in-hop carries the loss `fb2_gaze_exclusive`. The FB2 out-map keeps only the difference of each opposing pair. When both directions of a pair are non-zero, each FB2 output loses up to the smaller of the two values.
- **Rounding on the FB2 out-map.** The four outputs on the negative knot segment may change by up to 2⁻⁵⁴ when below 0.5, and values at or below 2⁻⁵⁴ become 0. The design goal was that these values equal those of the retired `arkit_gaze.to_fb2`; the pre-registered comparison found that they do ([scoreboard](../ab/results/v1/scoreboard.md), M1).
- **Why directions, not signed angles:** the design keeps the values of every current gaze route (the comparison tests this), and FB2's 0 to 1 range stays. **Why in and out:** the names do not change under mirroring, and they match ARKit, Unified Expressions and Godot.
- **No FACS code on gaze.** FACS 61 and 62 turn both eyes left or right together. Which eye turns toward the nose depends on whose "left" Wikipedia means, and the article does not say. Public crosswalks disagree on it. So the gaze signals have no `facs_au` for now. A later step may add 61-64 with the loss key `facs_side_frame_unresolved`.

## Visemes

### What a viseme value means

- Visemes are speech classes, not muscle actions. So they are a separate profile, `rcef.canonical_viseme`.
- A value is the weight of "the frame's articulation belongs to this IPA shape class", as the source reports it: META's class probability (`xr_visemes` lines 104-107), or a VRM weight as each model's author set it (loss `vrm_vowel_asset_weight`). It is not a phoneme detection or a transcription.
- The fields are `units = "probability"`, a domain from 0 to 1, no `neutral` field and `side = "shared"`. The rules of [Meaning of 0, 1 and neutral](#meaning-of-0-1-and-neutral) do not apply.
- **Sum.** From a valid META frame, the 15 partition values sum to 1, as META delivers them. From VRM there is no sum constraint. RCEF enforces no sum and never renormalises.
- **Consumers.** A sum, an argmax or a renormalisation uses only the signals with `coupling = "probability_simplex"` (groups `viseme_vowel`, `viseme_consonant` and `viseme_rest`). Aggregates and refinements overlap them: with SS = DD = NN = 0.3 and AA = 0.1, the whole profile sums to 1.9 and its largest value is `alveolar_floor` (0.9). No RCEF out-map reads an aggregate or refinement together with any of its parts.
- **Rest.** `sil` = 1 means no speech articulation. It is not an IPA segment, and RCEF asserts no mouth pose for it. META's reference image for SIL shows the lips together and relaxed (record `xr_visemes_fig_sil`), while JALI notes that pauses usually leave the mouth open (record `jali_2016`); a rig chooses. An invalid META frame (all values 0) is refused at the META in-hop and never becomes `sil`. A source with no rest class leaves `sil` absent, never 0.
- **Coarticulation.** `coronal_stop`, `coronal_nasal_lateral`, `dorsal` and plain `rhotic` have no lip shape of their own: the lips follow the neighbouring vowel (record `jali_2016`). RCEF has no operator over time, so it does not model this.
- **Not available.** A class that no selected in-map writes is absent. An out-map that reads it labels its outputs "not available from source"; this is not a refusal.
- **From VRM:** VRM's vowel presets are weights authored per model. The in-map treats them as probabilities. There is no sum constraint (aa = 1 and oh = 1 sum to 2), and VRM gives no `sil`.
- **To META from another source:** only the five vowels have values. The route never claims META validity: it writes no `isValid`, and it labels the frame "META validity not asserted". The vowel out-map's loss reads: "from a source other than META: consonant and rest classes not produced; outputs may sum to 0 or above 1; META validity contract (sum 1 when valid; invalid arrays are zero) not met".

### The IPA basis

- Each class is a set of IPA chart symbols with a place and manner, or a height, backness and rounding. Each of the 107 chart symbols is in exactly one class ([IPA chart assignment](#ipa-chart-assignment)). Symbols that are not single chart cells follow the [IPA rules](#ipa-rules).
- **Evidence levels.** E: a cited source states it. A: an articulatory inference or an RCEF convention. The viseme maps that RCEF counts are English, so every consonant outside English is A. `ipa_members_assumed` lists every A member of a class.
- **Vowel rows.** The vowel classes use one height cut for every backness value, following the chart rows. The IPA's lip clines agree: the back unrounded vowels follow the same spreading cline as the front ones, ɨ is fully spread, and a and ɑ are both neutral (record `wikipedia_roundedness`, raw lines 15-21, which cite the IPA Handbook). The central and back unrounded vowels, æ and ə are still A, because the English maps put æ with ɛ and ʌ with ɑ. ʊ with u is E but contested: two of the counted maps group ʊ elsewhere.
- **Provider labels.** Each META and VRM label is read literally and by its example word. Every reading lands in one class, and META's 14 speech classes go to 14 different classes. META RR, written "r" (a trill in IPA) with the example "red" (English ɹ), is one class, `rhotic`. META IH (ɪ, "tip") and VRM ih (remark "i") share `vowel_close_spread`. VRM ou, if it is read as Japanese [ɯᵝ], stays in `vowel_close_rounded`.
- **DD.** FB2 describes the tongue for DD as mid-dorsal on the palate (`xr_fb2` lines 915-917). RCEF's `coronal_stop` is the IPA coronal class.

### Why these classes: minimal under parity

The partition is **minimal under parity when the META and VRM hops target partition classes**. It is META's 14 speech classes and rest, extended to the whole IPA chart and named by IPA. It is not the pure shape floor (below). The class count and boundaries come from META; the evidence does not show that the world's mouth shapes fall into exactly these 14 classes.

- **Parity.** Each META vowel goes to its own canonical class by a copy, and each VRM vowel preset is copied from it, so a META → VRM route gives today's values. No two META classes share a canonical class, so META → canonical → META gives every value back. Together these need at least 14 speech-class signals.
- **The floor test.** For each candidate split, RCEF counts the published English viseme maps that list both sides: the 15 consonant maps of Bear and Harvey's Table 3 plus the composite groups of Owens and Blazek, or the 8 vowel maps of Table 2 (records `bear_harvey_2017`, `pubmed_owens_blazek_1985`). A split that at least two thirds of these maps keep is a **shape split**. A split that at most one third keep is in the **merge band**. The others are **mixed**. The threshold is an RCEF convention. With the rounding rule below applied in any band, every reading of the counts (all maps; the three maps that share an author counted as one; the rows whose counts Bear and Harvey's Table 5 confirms; both readings of the Jeffers vowel row) gives one consonant floor and one vowel floor, the same for any threshold above one half up to 9/13. No floor decision falls at the one-third boundary.
- **Limits of the test.** The counted maps are English phoneme maps (Bear and Harvey adapt American maps to British English), so members outside English are placed by convention from the chart. The maps are not independent: Bear and Harvey call many of them incremental improvements of earlier sets, and three share an author. With those three counted as one vote, the floor does not change.

| Split | Maps that keep it / maps that list both | Band |
|---|---|---|
| p b m vs f v | 16 / 16 | shape split |
| postalveolar vs the rest | 15 / 16 | shape split |
| dental θ ð vs the rest | 11 / 15 | shape split |
| t d vs k ɡ (coronal vs dorsal) | 11 / 15 | shape split |
| r vs the coronals t d n l s z | 11 / 15 | shape split by count; merged by the rounding rule |
| s z vs t d n l | 7 / 14 | mixed |
| l vs t d n | 7 / 15 | mixed |
| r vs w | 6 / 12 (2 / 7 on the confirmed rows, same-author maps as one) | mixed (merge band on the narrower reading); kept by the rounding rule |
| t d vs n l (META DD and NN) | 4 / 15 | merge band |
| rounded vs spread (u vs i) | 8 / 8 | shape split |
| mid vs close rounded (o ɔ vs u ʊ) | 6 / 7 | shape split |
| mid rounded vs mid spread | 6 / 7 | shape split |
| open vs mid spread | 5 / 6 | shape split |
| close vs mid spread | 6 / 8 | shape split |
| mid rounded vs open (ɔ vs ɑ) | 2 / 5 count-matched maps (2 or 3 / 6 by reading of the Jeffers row) | mixed or merge band; kept by the rounding rule |

- **The rounding rule.** Where an English count, in any band, can rest on an English pronunciation whose lip rounding differs from the IPA definition, and a cited source attests that pronunciation, the IPA definition decides. Classes that differ in IPA rounding stay apart; classes with the same rounding and no lip target merge, as other coronal manner differences do (ɾ ɽ with t d, ɺ with l). This is an RCEF convention (A). It applies three times:
  - **o ɔ vs ɑ, kept apart.** The only count is English /ɔ/ against /ɑ/. It tests no [o], ø or œ. Some speakers in the Northern Cities shift make /ɔ/ with unround lips, a variant that is harder to see (record `pubmed_havenhill_do_2018`). Where the maps test rounding at equal height they keep it (u vs i, 8 of 8). So `vowel_mid_rounded` is a floor shape.
  - **r vs w, kept apart.** No map puts r with a vowel. IPA w is labial-velar, while IPA r ɹ ɻ have no lip rounding; rounding on them is written ɹʷ (record `wikipedia_labialization`, raw line 20). Many English accents labialise /r/ (raw lines 512-514), which explains the English merges.
  - **r vs the coronals, merged.** The 11 maps that keep r apart count the same English /r/, whose visible difference is that labialisation. IPA r ɹ ɻ, like t d n l, define no lip shape, and no cited source gives them another visible difference. So in the floor r ɹ ɻ go with the coronals, in `alveolar_floor`: Spanish *pero* [ɾ] and *perro* [r] share a floor shape. The partition keeps `rhotic` as a class for META RR.
  - The rule is not applied to the postalveolar split (15 of 16 maps): the only source for labialised English /ʃ ʒ/ is marked "citation needed".
- **Perception studies,** each stated as what it found: in the visual channel, French listeners perceive vowel rounding better than height, and backness is almost invisible (record `pubmed_robert_ribes_1998`); for Dutch front vowels, rounding is carried mainly by vision and height by hearing (`pubmed_valkenier_2012`); American English vowels show a rounding dimension and a height dimension, not ranked (`pubmed_montgomery_jackson_1983`), although the same authors' map merges /ɔ/ with /ɑ/. Voicing and nasality are not visible: each of Owens and Blazek's groups mixes them (`pubmed_owens_blazek_1985`). JALI's tongue-only visemes do not move the lips (`jali_2016`).
- **The strict floor** has 6 consonant shapes (bilabial, labiodental, dental, postalveolar, alveolar_floor and dorsal) and 5 vowel shapes, plus rest: 11 classes and rest. r joins a consonant class, never a vowel class, so the floor keeps today's META → VRM values. It loses the META round trip: META SS, DD, NN and RR would share one class, and writing them back would need quarters, which do not give the values back. A floor that kept r apart from the coronals on the English count would have 12 classes and need an invented three-way split.
- **Splits kept for META.** The partition keeps three splits that the floor merges: `alveolar_sibilant` (mixed, 7 of 14 maps); `rhotic` (its splits from w and from the coronals are both counted on labialised English /r/; for IPA r ɹ ɻ it is a META convention, A); and the manner split of DD and NN (merge band, 4 of 15 maps; two of them, Lee and Hazen, are among Bear and Harvey's best consonant maps on isolated words). The two DD and NN signals share `shape_class = coronal_stop_nasal_lateral`, an RCEF convention: they differ only in manner, with no lip or jaw target of their own.
- **The floor class as a value.** The one floor class that is not a partition class, `alveolar_floor`, is written from META as an aggregate ([Viseme aggregates](#viseme-aggregates)). So every strict-floor class is a signal. `shape_floor` on each signal names its class in this IPA strict floor, with 12 values: bilabial, labiodental, dental, postalveolar, alveolar_floor, dorsal, open, mid_rounded, mid_spread, close_spread, close_rounded and rest. `shape_class` has 14 values: the partition's shapes on the English counts, including the mixed sibilant split and `rhotic` (noted "counted on English [ɹʷ]").
- **Not coarser.** Woodward's map of 4 consonant groups, the best on continuous speech, merges three splits that most maps keep. Merging r with w and u, or o ɔ with ɑ, as some English maps do, would change today's META → VRM values through RR and OH.
- **Not finer.** A separate lateral class (7 of 15 maps, mixed) would need an invented split of META NN. Finer shapes wait as [refinements](#viseme-refinements).
- **Vowels.** The maps disagree on the vowel set: they have 3 to 9 vowel classes (Bear and Harvey Table 5). On isolated words, Lee's vowel classes are the best. They are five classes on the same height and rounding lines as RCEF's, but Lee puts æ with e and ʌ with ɑ, where RCEF puts æ in `vowel_open` and ʌ in `vowel_mid_spread`.

### IPA rules

These rules place symbols that are not single chart cells. `tests/ipa_classes.py` applies them, and the tests check 113 cases and 4 symbols that have no rule.

- **Labialisation (ʷ, ᶣ).** On a class with no lip target of its own (`coronal_stop`, `coronal_nasal_lateral`, `dorsal`) the symbol goes to `vowel_close_rounded`, the class of w and ɥ (kʷ, tʷ, hʷ). On `alveolar_sibilant` it goes to `postalveolar` (sʷ). On an unrounded vowel or glide it goes to the rounded class of the same height band (eʷ → `vowel_mid_rounded`; jʷ → `vowel_close_rounded`). On the other classes there is no change (pʷ, θʷ). ɹʷ stays `rhotic`, because META RR covers English labialised /r/.
- **Compression (ᵝ, ᶹ).** On a class with no lip target of its own the symbol goes to `vowel_close_rounded` (kᵝ). On an unrounded vowel it goes to the rounded class of its height band (ɯᵝ → `vowel_close_rounded`; an open vowel → `vowel_mid_rounded`). On other symbols there is no change (record `wikipedia_roundedness`, raw lines 52-56).
- **Rhoticity (˞).** On ə or ɜ the symbol goes to `rhotic`, so ə˞ = ɚ and ɜ˞ = ɝ. Any other letter, vowel or consonant, keeps its class (a˞ → `vowel_open`).
- **Dental and interdental.** The dental mark ̪ alone keeps the class: t̪ d̪ n̪ l̪ stay coronal, because the tongue tip stays behind the teeth. The advanced mark ̟ alone keeps the class. ̪ with ̟ on a coronal or rhotic gives `dental` (t̪̟), but not on a sibilant (s̪̟ stays `alveolar_sibilant`). The extIPA bridge ͆ with ̪, ̺ or ̻ on those classes gives `dental` (n̪͆; this mark is not on the IPA chart). ͆ in any other use has no rule (record `wikipedia_interdental`).
- **Linguolabial (̼).** On a letter of a labial class, `dental`, `coronal_stop`, `coronal_nasal_lateral`, `rhotic` or `alveolar_sibilant`, the symbol goes to `dental`, because the tongue tip or blade touches the upper lip (t̼, θ̼, p̼). On any other letter, including the postalveolars (ʃ̼), there is no rule. ̺ on a labial letter, the older apico-labial notation, also gives `dental` (p̺) (record `wikipedia_linguolabial`).
- **Leading superscripts.** A superscript nasal or ʰ before the letter (ᵐb, ⁿd, ʰt) is dropped; the letter keeps its class.
- **Other marks keep the class:** ʲ ˠ ˤ, the velarised or pharyngealised tilde (ɫ), voicing, aspiration, nasalisation, nasal and lateral release, length, syllabic and non-syllabic marks, more and less rounded, raised and lowered (β̞, ɹ̝), tongue root, centralised, apical and laminal.
- **Affricates** (tie bar) take the class of their release: t͡s → `alveolar_sibilant`, t͡ʃ → `postalveolar`, p͡f → `labiodental`, t͡ɬ → `coronal_nasal_lateral`, k͡x → `dorsal`. **Double articulations** (k͡p, ɡ͡b, ŋ͡m) are `bilabial`: the lip closure is the visible one. **Ejectives** (ʼ) keep the class of the base consonant.
- **Laryngeals** h ɦ ʔ ħ ʕ ʜ ʢ ʡ are always `dorsal`, by one fixed convention.
- **Not classes.** A diphthong is two shapes in sequence. Stress, length, boundary and tone marks are not segments.
- **Contrary readings.** Each A-level convention has a contrary reading. For example, trill r could go to `coronal_stop` with the tap ɾ, as other coronal manner differences merge (then *pero* and *perro* would share a partition class, as they already share `alveolar_floor`); ɚ ɝ could go to `vowel_mid_spread`, because the IPA defines them as unrounded mid-central vowels; ɒ ɶ could go to `vowel_open`, because on the IPA rounding cline they are the least-rounded rounded vowels (record `wikipedia_roundedness`, raw lines 17 and 21); the lateral click ǁ could go to `coronal_stop`; ɹʷ could go to `vowel_close_rounded`; the glides j ɰ could go to `dorsal`. A change of class keeps every META and VRM value, because no provider writes these symbols.

### Viseme aggregates

- An **aggregate** is a derived signal whose members are the union of two or more whole partition classes of one group (`metadata.aggregates`). Its value is the sum of their values, clamped at 1. It is outside the simplex sum: `coupling = "aggregate_of_simplex_classes"`, no `shape_class`, and its own group (`viseme_aggregate` for consonant aggregates).
- **The one class exception.** [Base shapes only](#whole-actions-first) has one exception: viseme aggregates, which are unions of whole simplex classes in one group, written as clamped sums with weights 1 and their own coupling. Weighted blends stay excluded. `alveolar_floor` is the only aggregate in this version.
- **`alveolar_floor`** = `alveolar_sibilant` + `coronal_stop` + `coronal_nasal_lateral` + `rhotic` (23 chart symbols). Its in-map, `visemes_aggregate.to_rcef`, has two mappings. The first is a `weighted_sum` with weights [1, 1, 1, 1] of META SS, DD, NN and RR into the helper `rcef.intermediate.viseme_alveolar_floor_sum`, which runs from 0 to 4 and has the source units, `probability`, because these operators cannot change units. The second clamps it with the `piecewise_linear` knots (0, 0), (1, 1), (4, 1). These two operators are named exceptions to the census of hop operators (weights of powers of two and today's knots); they are allowed only in this map. Both mappings carry the loss `meta_viseme_aggregate_sum`.
- No out-map reads an aggregate in this version, so a route never selects the aggregate in-map. A later out-map that reads one selects it on its own routes only.
- **Reserved aggregates** (not signals yet). A later aggregate needs no new exception, but its fan-in is named here, as a census exception, when it ships.

| Reserved aggregate | Classes | Note |
|---|---|---|
| `coronal_stop_nasal_lateral` | `coronal_stop`, `coronal_nasal_lateral` | for a source with one t d n l class |
| `alveolar_or_dorsal` | `alveolar_sibilant`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal` | Owens and Blazek's large group, which has no r; a planned source for a coarse "most consonants" class |
| `vowel_rounded` | `vowel_mid_rounded`, `vowel_close_rounded` | one rounded vowel class, as in Hazen's map |
| `vowel_open_or_mid_rounded` | `vowel_open`, `vowel_mid_rounded` | an English-map view (English /ɔ/ with /ɑ/); not a floor class |

### Viseme refinements

- A finer class is a **refinement** signal with `metadata.refines` set to one partition class. Its members must be a subset of that class, and the partition class stays the total. A refinement is outside the simplex sum (`coupling = "refinement_of_simplex_class"`) and has its own group, `viseme_refinement`. A finer source writes the refinement and also the parent total; coarse out-maps read the parent. Refinements may overlap, and no RCEF out-map computes a complement.
- **Reserved refinements** (not signals yet):

| Reserved refinement | Refines | Members |
|---|---|---|
| `bilabial_fricative` | `bilabial` | ɸ β; β̞ by rule |
| `lateral` | `coronal_nasal_lateral` | l ɭ ɬ ɮ ɺ ǁ |
| `palatal` | `dorsal` | c ɟ ɲ ç ʝ ʎ |
| `vowel_close_compressed` | `vowel_close_rounded` | y ʏ ɥ |
| `vowel_mid_compressed` | `vowel_mid_rounded` | ø œ ɶ |
| `vowel_lower_mid_spread` | `vowel_mid_spread` | ɛ ɜ ʌ |
| `vowel_lower_mid_rounded` | `vowel_mid_rounded` | ɔ œ ɞ ɒ ɶ |
| `vowel_close_back_unrounded` | `vowel_close_spread` | ɯ ɰ (an English-map refinement) |
| `vowel_mid_nonfront_unrounded` | `vowel_mid_spread` | ɘ ə ɜ ɤ ʌ (an English-map refinement) |
| `vowel_open_nonfront_unrounded` | `vowel_open` | ɑ ɐ (an English-map refinement) |

The three English-map refinements follow the English maps' split of back from front unrounded vowels; the IPA lip clines do not support a lip difference there.

### Coarse viseme sources

The copy rule for coarse sources does not apply to viseme classes, because copies into two partition classes would break the simplex sum:

- An in-map never copies one source class into two partition classes, and an out-map never reads two partition classes back by a mean. Copies into a parent and its refinement, or into an aggregate, are allowed.
- A coarse source splits a class by halves (`affine(0.5, 0)`) or leaves the parts unwritten, which splits the group.
- Every fan-in of k inputs is a `weighted_sum` with weights 1 into a helper from 0 to k in the input units, then the clamp knots (0, 0), (1, 1), (k, 1), then a copy where the units change. Each such fan-in is a named census exception, scoped to its map. This version has one: `visemes_aggregate.to_rcef`.

### Viseme metadata

Each viseme signal has these metadata fields, in addition to the [fields](#fields) every signal has:

- `definition`: RCEF's meaning, naming any difference between the ID's place or height term and its members;
- `ipa_members` (NFC; ɡ is U+0261) and `ipa_members_assumed` (the A-level members); `ipa_rules` (the symbols that join by rule);
- for consonant classes `ipa_place` and `ipa_manner`, for vowel classes `ipa_height`, `ipa_backness` and `ipa_rounding`, from the chart cells of the members;
- `shape` (lips, teeth, tongue, jaw), `shape_class`, `shape_note` where there is one, `shape_floor` and `shape_floor_note`;
- `group`, `aligned_names` (META and VRM names, as facts) and `audit` (pointers to the audit rows);
- on aggregates, `aggregates` (the list of classes); on refinements, `refines`.

### Viseme pose bridge

A viseme is a mouth shape, so each class reaches a pose of the face. The bridge `rcef_viseme_pose.to_rcef_expression` writes canonical expression values from canonical viseme values:

expression_j = clamp(Σ_c pose[c][j] · viseme_c, 0, 1)

Here pose[c][j] is the value that class *c* at weight 1 gives expression signal *j*. With the bridge, META visemes and the VRM vowels can drive ARKit, FB2 and Unified Expressions faces, also on rigs that have no viseme shapes of their own, such as ICT-FaceKit, and give `facs.code` values.

- **Where the poses come from.** The calibration record `viseme-poses.rocketbox-features` (record `calibration.viseme-poses.rocketbox-features`) fits one pose per class to 18 Rocketbox rigs at once. For each class it finds one set of ARKit weights from 0 to 1 for all of them. Each Left and Right pair shares one weight, so every pose moves the two sides by the same weight. The fit first makes the largest whole-mesh error over the training rigs as small as it can. For `bilabial`, `vowel_close_rounded`, `vowel_mid_spread` and `alveolar_sibilant` it then also fits the visible mouth features of the perceptual gate (below). The fit leaves out the tongue vertices, the blink and gaze shapes (`eyeBlink*`, `eyeLook*`), the sideways jaw and mouth shifts and `tongueOut`. The ARKit in-maps, which are copies, then carry each weight to its canonical signals. [tools/calibration](../tools/calibration/README.md#viseme-poses-meta-viseme-shapes-in-arkit-shapes-viseme_posespy) gives the method and how it was chosen.
- **Two gates.** A rule chose the training and held-out rigs before the new rigs were downloaded ([viseme_rigs.json](../tools/calibration/viseme_rigs.json), round 3). The poses, the bounds, the features, their tolerances and the rule for using the record were frozen, and the ledger line committed, before the evaluation on 4 rigs that no fit or earlier evaluation loaded: Female_Adult_09, Female_Adult_15, Male_Adult_08 and Male_Adult_15. Before the freeze they were loaded only to count their shapes, as the rule's replacement clause needs. A class passes if it passes one of two gates on every held-out rig:
  - **Shape gate** (as in the earlier records). The error is the distance between the rig's own viseme shape and its ARKit shapes at the bridged weights, divided by how far the viseme shape moves the face, over every vertex except the tongue. It must be at most 0.5.
  - **Perceptual gate.** It checks a few visible features of the mouth, not the whole-mesh shape. The features are measured on landmark vertices that each rig's own ARKit shapes pick out: the mid-line lips, the mouth corners and the lower teeth. `bilabial`: the lips must be closed on the mid line (signed lip opening from −2.0 to 0.5 mm, a hard range, not relative), and drawn back like the rig's own (lip protrusion within 0.5 mm). `vowel_close_rounded`: corner width ratio within 0.041 and lip protrusion within 0.732 mm of the rig's own. `vowel_mid_spread`: corner width ratio within 0.197 and lip opening within 0.779 mm. `alveolar_sibilant`: lip opening within 2.35 mm and jaw drop within 0.5 mm (the teeth stay closed). Every gated class also has a loose whole-face guard: its whole-mesh error must be at most 1, no worse than the neutral face. Each feature cell has the same 24 conditions as the shape cells, and every condition must be within tolerance. A tolerance is the largest distance of a training rig's own viseme feature from the training median, at least 0.5 mm or 0.02. It is the spread of the library's own sculpts, not a measured perceptual threshold.
- **Which classes the bridge reads.** 11 of the 15 classes pass, and the bridge reads only those. 7 pass the shape gate: `vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `coronal_stop`, `dorsal` and `sil` (shape errors 0.24 to 0.38; `sil` passes trivially, because no rig's SIL shape moves the face). 4 pass the perceptual gate: `bilabial`, `vowel_close_rounded`, `vowel_mid_spread` and `alveolar_sibilant`. Their shape errors stay at 0.57 to 0.75, but every feature cell passes. For example, at full weight the bridged `bilabial` pose leaves a lip opening of −0.55 to −1.02 mm on the held-out rigs (their own PP shapes: −0.62 to −1.40 mm) and draws the lips back by 1.00 to 1.19 mm (their own: 1.03 to 1.19 mm). So a META PP frame keeps the lips closed, moves their inner edges past each other by 0.55 to 1.02 mm and draws them back about 1 mm, like the rigs' own PP. The lips at rest already lie in the closed range (0.02 to 0.49 mm on all 22 rigs), so what the gate adds is the evidence of the retraction and the overlap. These fail: `labiodental` (0.90 to 0.93), `rhotic` (0.54 to 0.59), `postalveolar` (0.45 to 0.53; it fails on both held-out male rigs) and `coronal_nasal_lateral` (0.50 to 0.53; it passes on Male_Adult_15 only). They have no perceptual gate. They stay in the record as negative results, and no mapping reads them; Route lists their values as dropped. From VRM, all five vowel presets drive the bridge.
- **Why `labiodental` has no gate.** On these rigs the only candidate feature that the cross-validation could meet, the distance from the upper teeth to the lower lip, is met by the neutral face on all 18 training rigs, so it tests nothing. With the lip opening added, the cross-validation failed on one training rig. So `labiodental` stays on the shape gate alone, and it fails. `coronal_nasal_lateral` has no visible feature of its own (its lips follow the neighbouring vowel), so it also has the shape gate alone.
- **Use of the record, fixed before the held-out run.** The bridge is written from `viseme-poses.rocketbox-features` alone, and it reads exactly the classes that pass there. It replaces the earlier records for every class: `viseme-poses.rocketbox-female` (one training rig; 9 classes passed), and `viseme-poses.rocketbox-multi` version 1 (10 training rigs, Left and Right weights apart; 9 classes passed, but its poses moved the two sides differently by up to 0.56) and version 2 (Left and Right tied; 7 classes passed). Those records stay in [calibration/](../calibration/README.md) or in the Git history as history, and no mapping cites them.
- **What it writes.** All 45 signals of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip`, with equal values for each Left and Right pair. A pose that the fit found as 0 is written as a definite 0, not left out. A consumer that merges the bridge's output with an eye tracker or another face source must decide which source owns the eye, brow and cheek signals; the bridge's 0 is a pose, not an absent value. The bridge writes no `blink`, `gaze`, `jaw_sideways`, `mouth_shift`, `tongue_out`, `cheek_suck`, `lip_tighten` or `tongue_place` value, so out-maps of those groups label their outputs "not available from source".
- **How it is written.** For each class, a copy into a helper `rcef.intermediate.viseme_pose_<class>`; the unit changes there from probability to 1. For each expression signal, a `weighted_sum` of the 11 helpers, with the frozen poses as weights, into `rcef.intermediate.viseme_pose_sum_<signal>` (0 to 11), then the clamp knots (0, 0), (1, 1), (11, 1). The weighted sums cite the record, and `check.py` refuses them unless each weight is exactly the record's frozen pose and every class read passes one of the two gates ([calibration/README.md](../calibration/README.md#mappings-that-cite-a-record)). These weights and knots are named census exceptions, allowed only in this map. `scripts/build_canonical.py` writes the map and its 56 helpers from the record.
- **Evidence status.** The record's status is `calibrated_software`. Pack schema 1.0 has no such value, so every mapping of the bridge is `proposed` and `approximate`, and says so in its assumptions.
- **Routes.** Route runs the bridge only when the target reads what it writes, the source cannot write that itself, and the source writes some of what the bridge reads: from META or VRM to ARKit, FB2, Unified Expressions or FACS. Then the route runs in-maps, the bridge, then out-maps. A class that no selected in-map can write (VRM has no consonants and no `sil`) counts as 0 in the bridge's sum, and the frame's notes say so. A refused in-map refuses the bridge's outputs on that frame. Every other route gives the same values as without the bridge.

**Limits.**

- The poses are Rocketbox's: sculpted shapes of 22 rigs from one library, measured in their ARKit units. Rigs from other libraries render the same ARKit weights differently (record `rig-gains.ict-rocketbox-female`: 3 of 51 shapes pass). On ICT-FaceKit the bridged `bilabial` pose opens the lips by about 2.3 mm on the mid line instead of keeping them closed (examples/README.md, section 7), so the closed, drawn-back lips hold on Rocketbox rigs only.
- The perceptual gate checks only its features. A class that passes by it can still differ from its viseme elsewhere on the face by more than half of the motion, up to the whole-face guard. For example, the bridged `vowel_mid_spread` pose draws the lips back by about 3 mm, against about 1.7 mm for the rigs' own E shapes, and the bridged `vowel_close_rounded` pose opens the lips less than the rigs' own OU shapes; neither feature is in that class's gate.
- The landmarks are single vertices or small vertex sets of low-polygon meshes. The tolerances come from 18 rigs of one library and no viewer judged them. Two are loose because the rigs split: the `alveolar_sibilant` lip-opening tolerance (2.35 mm) comes from one training rig, Male_Adult_03 (about 0.96 mm without it), and the `vowel_mid_spread` corner width ratio is about 1.0 on 7 training rigs and about 1.2 on the other 11, so its tolerance (0.197) spans both. On these rigs the ARKit shapes press the lips together only by moving their inner edges past each other, so the `bilabial` gate asks for closed and drawn-back lips, not for the lip compression of the rigs' own PP shapes.
- A pose value is a fit coefficient, not a statement about the action.
- All 22 rigs come from one library, with viseme and ARKit shapes by the same authors. A pass on the held-out rigs may partly show shared authoring, not transfer to independent rigs.
- Coarticulation is not modelled: each class is one static pose, and the poses of a blend add up. The gates test each class alone. Teeth and tongue are not represented beyond the teeth landmarks.
- The test is software-only. It says nothing about any tracker or any real face.

**No expression to viseme map.** The bridge goes one way. A face pose does not identify the sound: `coronal_stop`, `coronal_nasal_lateral` and `dorsal` have no lip target of their own, and different classes can reach similar poses. So RCEF has no map from the canonical expression set to the canonical viseme set, and it does not plan one.

## Eye closure from VRM and VRCFaceTracking

- **VRM `blink` is not read.** VRM has `blinkLeft`, `blinkRight` and `blink`, which closes both eyes (`vrm_expressions` lines 177-179). The VRM in-map reads only `blinkLeft` and `blinkRight`. It declares the loss "VRM blink (both eyes) not read; when a model drives only blink, eye_close reads open", and the route lists a non-zero `blink` as dropped. Toward VRM, the out-map writes `blinkLeft` and `blinkRight` and leaves `blink` unset, with today's loss.
- **VRM side.** Both VRM blink hops keep today's caveat, "VRM gives no normative side; on the VRM 1.0 Twist sample blinkLeft moves the avatar's own left eyelid", and add the loss key `vrm_blink_side_unresolved` ([audit](canonical-set-audit.md#vrm)).
- **VRCFaceTracking eye.** `eye_close` is 1 − `Openness`. `Openness` 1 is taken as `eye_close` 0, relaxed open lids, but VRCFaceTracking does not say that 1 is neutral (loss key `vrcft_eye_openness_neutral_unresolved`). An `Openness` outside 0 to 1 would give a value outside the canonical domain of 0 to 1, so the in-hop refuses it: msf-character-tools reports `E_DOMAIN`. Both blink hops state this as an assumption and as the loss.
- **VRCFaceTracking pupils.** The pupil diameters are copied in millimetres both ways. These 4 mappings are `exact` and `verified_current`, and they cite only `vrcft_data` and `rcef_canonical_v1`.

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
- **No viseme from a pose:** the [viseme pose bridge](#viseme-pose-bridge) goes from visemes to expressions only.
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

**Base shapes only.** Blended or combined shapes are never canonical signals. The out-maps of this first phase write base shapes only, and the consumer computes any blended shape from them: for example Unified Expressions BrowDown (0.75 BrowLowerer + 0.25 BrowPinch) and MouthSmile (0.8 MouthCornerPull + 0.2 MouthCornerSlant) (`vrcft_simple_expressions`). Blended out-maps wait until hop weights other than powers of two are allowed. Viseme aggregates are the one class exception ([Viseme aggregates](#viseme-aggregates)).

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

Viseme refinements and aggregates are reserved in [Visemes](#viseme-refinements).

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
- **Fields:** `value_type = "scalar"`, `units = "1"`, `domain = {min = 0.0, max = 1.0}`, `neutral = 0.0`, `evidence_status = "proposed"`. Evidence is `facs_wikipedia`, plus `rocketbox_avatars` where `aligned_names` holds a Rocketbox name, and `facs_hager_2002` on the AU43 signals and on 41, 42 and 44, whose reasons rest on it. The code numbers are facts, but the scalar encoding is RCEF's, so the signals are `proposed`.
- **Calibration strings.** `au<NN>` stands for the local name of the signal, for example `au01_left`. Main codes: `rcef.facs.v1:au<NN>: 0 = absent (a scored frame does not list the code); 1 = intensity E, the maximum possible for the individual person (Wikipedia FACS, raw line 70); FACS defines only the ordered letters A-E and no numeric scale, so values between are an RCEF encoding (docs/facs-intensity.md), not a FACS measure`. Gross codes 29, 30, 34, 35 and 43: `rcef.facs.v1:au<NN>: 0 = absent (a scored frame does not list the code); 1 = the action at its fullest, as RCEF assumes; the source gives no intensity scale for gross behaviour codes (Wikipedia FACS, raw lines 65, 224); FACS defines only the ordered letters A-E and no numeric scale, so values between are an RCEF encoding (docs/facs-intensity.md), not a FACS measure`. AU43 takes the gross form, because Wikipedia lists 43 as a gross code (raw line 257). A frame that is not coded is left out, never 0.
- **Profile metadata:** `vocabulary_version = "1.0"` and `vocabulary_status = "draft"`, and the text "FACS code numbers and names from a public list; not FACS coding; values are not FACS scores".

**Rows that are not mapped.** Each row's reason names the gap. The [codec](facs-intensity.md#codes-that-are-not-mapped) says how it reads each code.

| Codes | Disposition | Region | Reason |
|---|---|---|---|
| 11 | unresolved | cheek | no canonical signal; the name `nasolabial_deepen` is reserved; the codec does not read it |
| 13 | unresolved | mouth | no canonical signal; the name `sharp_lip_pull` is reserved; the codec does not read it. Rocketbox names its AU 13 shape `AU_13_CheekPuffer`, but Wikipedia names 13 Sharp lip puller; it is not cheek puff (34) |
| 21 | unresolved | other | no canonical signal; the name `neck_tighten` is reserved; the codec does not read it |
| 25 | unresolved | mouth | no canonical signal; the name `lips_part` is reserved; the codec does not read it, and toward FACS all mouth opening is written as 26 |
| 27 | unresolved | jaw | no signal of its own; the name `mouth_stretch` is reserved; the codec reads it as AU26, and toward FACS all mouth opening is written as 26 |
| 31 | unresolved | jaw | no canonical signal; the codec does not read it |
| 32 | unresolved | mouth | no canonical signal; the codec does not read it |
| 36 | unresolved | tongue | no canonical signal; the codec does not read it |
| 40 | unresolved | nose | no canonical signal; the codec does not read it |
| 33 | unresolved | cheek | no canonical signal; a coder may score it instead of 34, so the codec leaves the `cheek_puff` signals out |
| 37 | unresolved | mouth | no canonical signal; a coder may score it instead of 19, so the codec leaves `tongue_out` out |
| 38, 39 | unresolved | nose | no canonical signal; the names `nostril_dilate` and `nostril_compress` are reserved; the codec does not read it |
| 41, 42 | unresolved | eyelid | FACS 2002 folds it into AU43 intensity, with letters that no public source gives; the codec leaves the `blink` signals out |
| 44 | unresolved | eyelid | FACS 2002 folds it into AU43 intensity, with letters that no public source gives; the codec leaves the `blink` signals and `lid_tighten` out |
| 45, 46 | unresolved | eyelid | no signal of its own; the codec reads it as AU43, and toward FACS all eye closure is written as 43 |
| 61, 62, 63, 64 | unresolved | gaze | canonical gaze has no FACS code, because the source does not say whose left it means ([Gaze](#gaze)); the codec does not read it |
| 65, 66, 69 | unresolved | gaze | no canonical signal; the codec does not read it |
| 51, 52, 53, 54, 55, 56, 57, 58 | excluded | other | head pose is out of scope |
| 50, 80, 81, 82, 84, 85, 91, 92, 97\*, 98\* | excluded | other | a behaviour event, not a face weight |


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
| `ipa_chart_kiel_2020`, `ipa_chart_doulos_2020` | The IPA chart (revised to 2020), the Kiel and Doulos SIL archive files of the International Phonetic Association. The Doulos file carries the 107 symbols and the cell locators of [IPA chart assignment](#ipa-chart-assignment) | CC BY-SA 3.0 Unported at issue; the IPA now states CC BY-SA 4.0 for the IPA Chart in IPA Kiel and all its subparts; RCEF's adapted fixture is CC-BY-SA-4.0 under BY-SA 3.0 section 4(b) |
| `wikipedia_roundedness`, `wikipedia_labialization`, `wikipedia_interdental`, `wikipedia_linguolabial` | Wikipedia articles at pinned revisions (raw wikitext): lip rounding and its clines, labialisation, interdental and linguolabial consonants | CC-BY-SA-4.0; facts only, no prose copied |
| `xr_visemes_fig_sil`, `_dd`, `_nn`, `_kk`, `_rr`, `_th`, `_rr_rot`, `_ch_rot`, `_ou_rot`, `_sil_rot` | META's reference images for the visemes, OpenXR-Docs `5a82d45` | CC-BY-4.0 (Khronos REUSE sidecars) |
| `polly_license`, `polly_ph_table_en_us` | The archived Amazon Polly developer guide at `97b0d81ab6468129948d48beb767da1d692f2f27`: its licence and en-US phoneme table. The archive is out of date relative to the live AWS documentation, which is not cited | CC-BY-SA-4.0 |
| `bear_harvey_2017`, `fernandez_lopez_sukno_2017`, `zhou_visemenet_2018`, `jali_2016` | Viseme literature: versioned arXiv files and the JALI author copy | Reference only; facts, paraphrased |
| `pubmed_owens_blazek_1985`, `pubmed_robert_ribes_1998`, `pubmed_montgomery_jackson_1983`, `pubmed_benguerel_pichora_fuller_1982`, `pubmed_auer_bernstein_1997`, `pubmed_valkenier_2012`, `pubmed_havenhill_do_2018` | PubMed abstracts, one pinned NCBI efetch file per article | Reference only; facts, paraphrased |

The data change that adds `facs.code` adds four more records. The last two support audit notes only; no hop cites them.

| Record | Source | Licence or terms |
|---|---|---|
| `facs_hager_2002` | The FACS publisher's page on the 2002 manual, Internet Archive capture `20081218070149` (original bytes), lines 204-205. The live page now returns HTTP 404 | Reference only |
| `rocketbox_avatars` | Microsoft Rocketbox README at `0943055` (lines 21 and 55). The 48 `AU_*` shape names come from the facial files of Female_Adult_01 and Male_Adult_01 that `examples/rigs.py` pins, through `scripts/derive_rocketbox_au_names.py` | MIT |
| `pyfeat_au_reference` | Py-Feat `docs/pages/au_reference.md` at `4ebb4ec` | MIT |
| `ozel_arkit_facs` | Melinda Ozel, "ARKit to FACS" cheat sheet, Internet Archive capture `20261010185714` (original bytes). The live page's bytes change over time with template and plugin updates, so the record pins an archive capture | Reference only; all rights reserved |

## Effect on compatibility

- New profiles and maps are added. No existing value changes. In the META viseme profile, the 10 consonant and SIL signals become `mapped`, because the new hops use them.
- Data 0.5.0 retires the 7 direct maps, the 3 identity maps, the old `rcef.canonical` profile and its 21 signals, and the 4 old intermediate signals, with tombstones in [retired-ids.csv](retired-ids.csv). There is no deprecation period.
- Every hop is `approximate` and `proposed`, except the 4 pupil copies, which are `exact` and `verified_current`. So 19 of the 21 `verified_current` mappings in the three retired identity maps have only `proposed` routes in their place.
- The design goal was that two-hop routes give the same values as the direct maps on every output that both write. The pre-registered comparison tested this before the direct maps were retired, and B equalled A1 on every such output ([scoreboard](../ab/results/v1/scoreboard.md), M1).

## Alternatives considered

| Choice | Chosen | Alternative and why not |
|---|---|---|
| Gaze form | 8 directional fractions | Signed yaw and pitch: changes today's values |
| Gaze names | in and out | Subject left and right: the names change under mirroring |
| Granularity | the finest first-phase source | Add the Unified Expressions parts now: no first-phase source writes them |
| Visemes | a separate profile with four groups and no neutral | Inside the expression profile: visemes are classes, not actions |
| Viseme classes | IPA shape classes, minimal under parity, plus the floor aggregate `alveolar_floor`; where an English count rests on lip rounding that the IPA does not define, the floor follows the IPA, so r stays apart from w and the rounded vowels, and unlabialised r ɹ ɻ go with the coronals | META's IDs with IPA members: the same values, but provider names; the pure shape floor as the partition: loses the META round trip; the floor as metadata only: no floor value; `alveolar_floor` without `rhotic`: r apart from the coronals only on the English count |
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
- for `facs.code`: 92 rows with the dispositions 49, 25 and 18; the ID pattern; the calibration strings; `facs_au` agrees with the FACS maps;
- for the visemes: every one of the 107 chart symbols in exactly one partition class; the 113 rule cases and the 4 symbols with no rule; refinements are subsets of one class and aggregates unions of whole classes in one group; only the 15 partition signals carry `probability_simplex`; every IPA string is in NFC; the aggregate in-map's clause and its fan-in are the only hop operators outside the census; its chain gives the clamped binary64 sum of META SS, DD, NN and RR on random frames; no route selects it; no out-map reads an aggregate or refinement together with any of its parts.

- for the viseme pose bridge (`tests/test_pose_bridge.py`, without the generator): it is written from `viseme-poses.rocketbox-features` alone; it reads only the partition classes that pass the shape or the perceptual gate on all 4 held-out rigs; each weight is the record's frozen pose; the copy, sum and clamp chain gives the clamped sum on random frames; it writes whole expression groups; Route runs it only from META or VRM to ARKit, FB2, Unified Expressions or FACS, and every other route gives the same values as without it.

## Open questions

- Do the FB2 JAW_SIDEWAYS_LEFT and Unified Expressions JawLeft figures show the subject's own left? The FB2 figure, enlarged, shows the chin and lower lip moving toward the viewer's right, that is the subject's own left, which agrees with the FB2 text. The JawLeft figure has no neutral figure beside it, so it is hard to read. Until a figure contradicts its text, the jaw rows follow the text.
- Which way does Unified Expressions MouthLowerDown move? The name says down; the description says up.
- Does `lips_toward` act as a jaw corrective, and what does a non-zero value mean at `jaw_drop` = 0? Do ARKit `mouthClose` and FB2 LIPS_TOWARD agree on this?
- Does any public FACS source say whose left and right the L and R modifiers, and AU30, mean?
- Are the FACS letter steps equal? Only the closed manual says. RCEF never assumes more than its codec does.
- What are the real ranges of VRCFaceTracking `Openness` and `PupilDiameter_MM`?
- Should the tongue-position signals ever be linked to the Unified Expressions tongue directions?
- Who in the working group reviews meaning, and how long does it take?
- Would the perceptual tolerances hold for viewers? They are the spread of one library's sculpts. Would `labiodental` pass with a basis beyond the ARKit shapes, or a feature that its neutral face does not already meet? A held-out rig from another library would test transfer better than one library.
- Are y vs u, ɯ vs i, o ɔ vs ɑ, r ɹ ɻ vs w and unlabialised r ɹ ɻ vs t d n l visibly different outside English? No study RCEF read measures these contrasts; the rounding rule infers them from studies of rounding as a feature. The split of tap ɾ (`coronal_stop`) from trill r (`rhotic`) follows META, with no shape evidence; both are in one floor shape.
- Does labialised English /ʃ ʒ/ make the postalveolar split look larger in the English maps than the IPA shapes would? The only source is marked "citation needed", so the rounding rule is not applied there.

## IPA chart assignment

Every symbol of the IPA chart (revised to 2020; record `ipa_chart_doulos_2020`), with its chart section and cell, its canonical viseme class and the evidence level of that placement: E, a cited source states it; A, an RCEF convention or articulatory inference. The counted viseme maps are English, so every consonant outside English is A. "Contested" marks a placement with a contrary reading ([IPA rules](#ipa-rules)). The same list is in `tests/fixtures/ipa_chart_symbols.json`, which the tests read.

| Symbol | Code points | Chart section | Cell | Class | Evidence |
|---|---|---|---|---|---|
| p | U+0070 | Pulmonic consonants | Plosive × Bilabial | `bilabial` | E |
| b | U+0062 | Pulmonic consonants | Plosive × Bilabial | `bilabial` | E |
| t | U+0074 | Pulmonic consonants | Plosive × Alveolar | `coronal_stop` | E |
| d | U+0064 | Pulmonic consonants | Plosive × Alveolar | `coronal_stop` | E |
| ʈ | U+0288 | Pulmonic consonants | Plosive × Retroflex | `coronal_stop` | A |
| ɖ | U+0256 | Pulmonic consonants | Plosive × Retroflex | `coronal_stop` | A |
| c | U+0063 | Pulmonic consonants | Plosive × Palatal | `dorsal` | A |
| ɟ | U+025F | Pulmonic consonants | Plosive × Palatal | `dorsal` | A |
| k | U+006B | Pulmonic consonants | Plosive × Velar | `dorsal` | E |
| ɡ | U+0261 | Pulmonic consonants | Plosive × Velar | `dorsal` | E |
| q | U+0071 | Pulmonic consonants | Plosive × Uvular | `dorsal` | A |
| ɢ | U+0262 | Pulmonic consonants | Plosive × Uvular | `dorsal` | A |
| ʔ | U+0294 | Pulmonic consonants | Plosive × Glottal | `dorsal` | A |
| m | U+006D | Pulmonic consonants | Nasal × Bilabial | `bilabial` | E |
| ɱ | U+0271 | Pulmonic consonants | Nasal × Labiodental | `labiodental` | A |
| n | U+006E | Pulmonic consonants | Nasal × Alveolar | `coronal_nasal_lateral` | E |
| ɳ | U+0273 | Pulmonic consonants | Nasal × Retroflex | `coronal_nasal_lateral` | A |
| ɲ | U+0272 | Pulmonic consonants | Nasal × Palatal | `dorsal` | A |
| ŋ | U+014B | Pulmonic consonants | Nasal × Velar | `dorsal` | E |
| ɴ | U+0274 | Pulmonic consonants | Nasal × Uvular | `dorsal` | A |
| ʙ | U+0299 | Pulmonic consonants | Trill × Bilabial | `bilabial` | A |
| r | U+0072 | Pulmonic consonants | Trill × Alveolar | `rhotic` | A |
| ʀ | U+0280 | Pulmonic consonants | Trill × Uvular | `dorsal` | A |
| ⱱ | U+2C71 | Pulmonic consonants | Tap or Flap × Labiodental | `labiodental` | A |
| ɾ | U+027E | Pulmonic consonants | Tap or Flap × Alveolar | `coronal_stop` | A |
| ɽ | U+027D | Pulmonic consonants | Tap or Flap × Retroflex | `coronal_stop` | A |
| ɸ | U+0278 | Pulmonic consonants | Fricative × Bilabial | `bilabial` | A |
| β | U+03B2 | Pulmonic consonants | Fricative × Bilabial | `bilabial` | A |
| f | U+0066 | Pulmonic consonants | Fricative × Labiodental | `labiodental` | E |
| v | U+0076 | Pulmonic consonants | Fricative × Labiodental | `labiodental` | E |
| θ | U+03B8 | Pulmonic consonants | Fricative × Dental | `dental` | E |
| ð | U+00F0 | Pulmonic consonants | Fricative × Dental | `dental` | E |
| s | U+0073 | Pulmonic consonants | Fricative × Alveolar | `alveolar_sibilant` | E |
| z | U+007A | Pulmonic consonants | Fricative × Alveolar | `alveolar_sibilant` | E |
| ʃ | U+0283 | Pulmonic consonants | Fricative × Postalveolar | `postalveolar` | E |
| ʒ | U+0292 | Pulmonic consonants | Fricative × Postalveolar | `postalveolar` | E |
| ʂ | U+0282 | Pulmonic consonants | Fricative × Retroflex | `postalveolar` | A |
| ʐ | U+0290 | Pulmonic consonants | Fricative × Retroflex | `postalveolar` | A |
| ç | U+00E7 | Pulmonic consonants | Fricative × Palatal | `dorsal` | A |
| ʝ | U+029D | Pulmonic consonants | Fricative × Palatal | `dorsal` | A |
| x | U+0078 | Pulmonic consonants | Fricative × Velar | `dorsal` | A |
| ɣ | U+0263 | Pulmonic consonants | Fricative × Velar | `dorsal` | A |
| χ | U+03C7 | Pulmonic consonants | Fricative × Uvular | `dorsal` | A |
| ʁ | U+0281 | Pulmonic consonants | Fricative × Uvular | `dorsal` | A |
| ħ | U+0127 | Pulmonic consonants | Fricative × Pharyngeal | `dorsal` | A |
| ʕ | U+0295 | Pulmonic consonants | Fricative × Pharyngeal | `dorsal` | A |
| h | U+0068 | Pulmonic consonants | Fricative × Glottal | `dorsal` | A |
| ɦ | U+0266 | Pulmonic consonants | Fricative × Glottal | `dorsal` | A |
| ɬ | U+026C | Pulmonic consonants | Lateral fricative × Alveolar | `coronal_nasal_lateral` | A |
| ɮ | U+026E | Pulmonic consonants | Lateral fricative × Alveolar | `coronal_nasal_lateral` | A |
| ʋ | U+028B | Pulmonic consonants | Approximant × Labiodental | `labiodental` | A |
| ɹ | U+0279 | Pulmonic consonants | Approximant × Alveolar | `rhotic` | E |
| ɻ | U+027B | Pulmonic consonants | Approximant × Retroflex | `rhotic` | A |
| j | U+006A | Pulmonic consonants | Approximant × Palatal | `vowel_close_spread` | A |
| ɰ | U+0270 | Pulmonic consonants | Approximant × Velar | `vowel_close_spread` | A |
| l | U+006C | Pulmonic consonants | Lateral approximant × Alveolar | `coronal_nasal_lateral` | E |
| ɭ | U+026D | Pulmonic consonants | Lateral approximant × Retroflex | `coronal_nasal_lateral` | A |
| ʎ | U+028E | Pulmonic consonants | Lateral approximant × Palatal | `dorsal` | A |
| ʟ | U+029F | Pulmonic consonants | Lateral approximant × Velar | `dorsal` | A |
| ʘ | U+0298 | Non-pulmonic consonants | Clicks × Bilabial | `bilabial` | A |
| ǀ | U+01C0 | Non-pulmonic consonants | Clicks × Dental | `coronal_stop` | A |
| ǃ | U+01C3 | Non-pulmonic consonants | Clicks × (Post)alveolar | `coronal_stop` | A |
| ǂ | U+01C2 | Non-pulmonic consonants | Clicks × Palatoalveolar | `coronal_stop` | A |
| ǁ | U+01C1 | Non-pulmonic consonants | Clicks × Alveolar lateral | `coronal_nasal_lateral` | A |
| ɓ | U+0253 | Non-pulmonic consonants | Voiced implosives × Bilabial | `bilabial` | A |
| ɗ | U+0257 | Non-pulmonic consonants | Voiced implosives × Dental/alveolar | `coronal_stop` | A |
| ʄ | U+0284 | Non-pulmonic consonants | Voiced implosives × Palatal | `dorsal` | A |
| ɠ | U+0260 | Non-pulmonic consonants | Voiced implosives × Velar | `dorsal` | A |
| ʛ | U+029B | Non-pulmonic consonants | Voiced implosives × Uvular | `dorsal` | A |
| ʍ | U+028D | Other symbols | Voiceless labial-velar fricative | `vowel_close_rounded` | A |
| w | U+0077 | Other symbols | Voiced labial-velar approximant | `vowel_close_rounded` | A |
| ɥ | U+0265 | Other symbols | Voiced labial-palatal approximant | `vowel_close_rounded` | A |
| ʜ | U+029C | Other symbols | Voiceless epiglottal fricative | `dorsal` | A |
| ʢ | U+02A2 | Other symbols | Voiced epiglottal fricative | `dorsal` | A |
| ʡ | U+02A1 | Other symbols | Epiglottal plosive | `dorsal` | A |
| ɕ | U+0255 | Other symbols | Alveolo-palatal fricatives | `postalveolar` | A |
| ʑ | U+0291 | Other symbols | Alveolo-palatal fricatives | `postalveolar` | A |
| ɺ | U+027A | Other symbols | Voiced alveolar lateral flap | `coronal_nasal_lateral` | A |
| ɧ | U+0267 | Other symbols | Simultaneous ʃ and x | `postalveolar` | A |
| i | U+0069 | Vowels | Close × Front, unrounded | `vowel_close_spread` | E |
| y | U+0079 | Vowels | Close × Front, rounded | `vowel_close_rounded` | E |
| ɨ | U+0268 | Vowels | Close × Central, unrounded | `vowel_close_spread` | A |
| ʉ | U+0289 | Vowels | Close × Central, rounded | `vowel_close_rounded` | E |
| ɯ | U+026F | Vowels | Close × Back, unrounded | `vowel_close_spread` | A |
| u | U+0075 | Vowels | Close × Back, rounded | `vowel_close_rounded` | E |
| ɪ | U+026A | Vowels | Near-close × Near-front, unrounded | `vowel_close_spread` | E |
| ʏ | U+028F | Vowels | Near-close × Near-front, rounded | `vowel_close_rounded` | E |
| ʊ | U+028A | Vowels | Near-close × Near-back, rounded | `vowel_close_rounded` | E, contested |
| e | U+0065 | Vowels | Close-mid × Front, unrounded | `vowel_mid_spread` | E |
| ø | U+00F8 | Vowels | Close-mid × Front, rounded | `vowel_mid_rounded` | E |
| ɘ | U+0258 | Vowels | Close-mid × Central, unrounded | `vowel_mid_spread` | A |
| ɵ | U+0275 | Vowels | Close-mid × Central, rounded | `vowel_mid_rounded` | E |
| ɤ | U+0264 | Vowels | Close-mid × Back, unrounded | `vowel_mid_spread` | A |
| o | U+006F | Vowels | Close-mid × Back, rounded | `vowel_mid_rounded` | E |
| ə | U+0259 | Vowels | Mid × Central, unrounded | `vowel_mid_spread` | A |
| ɛ | U+025B | Vowels | Open-mid × Front, unrounded | `vowel_mid_spread` | E |
| œ | U+0153 | Vowels | Open-mid × Front, rounded | `vowel_mid_rounded` | E |
| ɜ | U+025C | Vowels | Open-mid × Central, unrounded | `vowel_mid_spread` | A |
| ɞ | U+025E | Vowels | Open-mid × Central, rounded | `vowel_mid_rounded` | E |
| ʌ | U+028C | Vowels | Open-mid × Back, unrounded | `vowel_mid_spread` | A |
| ɔ | U+0254 | Vowels | Open-mid × Back, rounded | `vowel_mid_rounded` | E |
| æ | U+00E6 | Vowels | Near-open × Front, unrounded | `vowel_open` | A |
| ɐ | U+0250 | Vowels | Near-open × Central, unrounded | `vowel_open` | A |
| a | U+0061 | Vowels | Open × Front, unrounded | `vowel_open` | E |
| ɶ | U+0276 | Vowels | Open × Front, rounded | `vowel_mid_rounded` | A, contested |
| ɑ | U+0251 | Vowels | Open × Back, unrounded | `vowel_open` | E |
| ɒ | U+0252 | Vowels | Open × Back, rounded | `vowel_mid_rounded` | A, contested |
