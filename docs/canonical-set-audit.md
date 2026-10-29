<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Canonical expression set: definitions audit (draft)

Original documentation: CC-BY-SA-4.0. Copyright (c) 2026 Metaverse Standards Forum.

This audit goes with the draft [canonical expression set](canonical-set.md). It compares each canonical signal with the public definition of each source that maps it. It also lists the assumptions of today's direct maps and where each one goes in the pivot routes. The audit is fixed before the pre-registered comparison of the pivot routes with today's maps.

"Today's maps" (A1) means the direct maps at commit `dea1713`: `arkit.to_fb2`, `arkit_gaze.to_fb2`, `fb2.to_arkit`, `fb2_gaze.to_arkit`, `arkit.to_vrcft_artist`, `fb2.to_vrm` and `visemes.to_vrm`.

## How to read the audit

- **Rows.** There are three kinds of row:
  - one row for each pair of canonical signal and phase-1 source that maps it;
  - one row for each pair of canonical signal with a FACS code and FACS crosswalk record that a hop of that signal cites. Today the only such record is `ict_facekit`. A crosswalk difference on a signal whose hops do not cite the record is a [note](#crosswalk-notes) with no key;
  - one row for each canonical signal that a FACS hop links, plus rows for the FACS encoding and frame.
- **Each row** gives the source's name, the evidence record and locator, and an RCEF paraphrase of the source's definition. The canonical definitions are in the [signal table](canonical-set.md#expression-signals). Records whose licence is "reference only", or that state no licence, allow no copying of prose: the Apple, VRM and VRCFaceTracking documentation records. RCEF paraphrases every row in the same way, whatever the licence.
- **Verdicts:**
  - `same`: the source's own text or figure names the action that the canonical definition describes. It needs a cited locator. Without evidence the verdict is `unresolved`.
  - `differs`: the source defines a different or wider action. The row gives the owning hop and a stable loss key.
  - `unresolved`: the evidence is missing or conflicts. The row gives the owning hop and a stable loss key.
- **Hops.** "ARKit in and out" means the ARKit in-map and out-map of the signal's group, for example `arkit_face.to_rcef` and `rcef_face.to_arkit`. The [loss keys](#loss-keys) table gives each key's text.
- **Locators** are line numbers in the pinned source file of the record, unless the row says otherwise. For `apple_blendshapes` the locator is the abstract of the named coefficient in Apple's JSON data.

## Evidence rule

- A provider's own text or figure settles a meaning or a frame (whose left, and what moves). A figure in the provider's specification or documentation is part of its definition.
- Agreement between implementers (today's maps, Godot, VRCFaceTracking) settles only which output gets a value. It never settles a provider's frame or meaning.
- When the provider's text and RCEF's own records conflict, the verdict is `unresolved`.
- The rule applies in the same way to side names and to direction words (gaze, jaw, mouth shift), for every provider.

## Frames: whose left

| Source | Signals | Evidence | Verdict | Owning hop, key |
|---|---|---|---|---|
| ARKit | every sided ARKit row, and the direction words of `jaw_sideways_*`, `mouth_shift_*` and gaze | `apple_blendshapes`, Discussion: left and right in the coefficient names are relative to the face, and `eyeBlinkRight` is the face's right eye | `same` | — |
| FB2 | every FB2 row with a side or a direction suffix, gaze and `jaw_sideways_*` and `mouth_shift_*` included | The figures show the subject's own side: EYES_CLOSED_L closes the eye on the viewer's right (`xr_fb2_fig_eyes_closed_l`); EYES_LOOK_LEFT_L turns that eye toward the viewer's right, the temple (`xr_fb2_fig_eyes_look_left_l`); MOUTH_LEFT moves the mouth toward the viewer's right (`xr_fb2_fig_mouth_left`). The text ties the direction to the side name: MOUTH_LEFT pulls the left lip corner leftward (`xr_fb2` 835-836). The JAW_SIDEWAYS_LEFT figure (`xr_fb2` 671), enlarged, shows the chin and lower lip moving toward the viewer's right; this agrees | `same` | — |
| Unified Expressions | every sided Unified Expressions row | The figures show the subject's own side: EyeClosedLeft closes the eye on the viewer's right (`vrcft_fig_eyeclosedleft`); EyeLookOutLeft turns that eye toward the viewer's right, the temple (`vrcft_fig_eyelookoutleft`); MouthUpperLeft moves the upper lip toward the viewer's right (`vrcft_fig_mouthupperleft`). The JawLeft figure has no neutral figure beside it, so it settles nothing; the jaw rows follow the text and the MouthUpperLeft figure | `same` | — |
| VRCFaceTracking eye | `eye_close_*`, `pupil_diameter_mm_*` | The same project computes `v2/EyeClosedLeft` as 1 − `Eye.Left.Openness` (`vrcft_code_parameters` 40), so the EyeClosedLeft figure applies | `same` | — |
| VRM | `eye_close_*` | Today's map says "VRM gives no normative side" (`mappings/fb2_vrm.toml` at `dea1713`, lines 19 and 40). RCEF's profile records `side = "left"` on `blinkLeft` with no caveat (`profiles/vrm.preset.toml` lines 203-204) | `unresolved` | VRM blink in and out, `vrm_blink_side_unresolved` |
| FACS | every sided `facs.code` signal (42) and the 2 AU30 directions | Wikipedia says that R is the right side of the face and L the left (`facs_wikipedia` raw line 78), but not from whose view. It is a secondary source, and FACS's own text is the closed manual. RCEF reads L and R as the subject's own side, as an assumption | `unresolved` | every sided FACS hop and both AU30 hops, `facs_side_frame_unresolved` |

## FB2

Record `xr_fb2` (OpenXR-Docs `5a82d45`, CC-BY-4.0). Every weight is in [0, 1]: 0 is not active, 1 is fully active (lines 351-353). 70 rows: 62 `same`, 8 `differs`. The two gaze keys are `fb2_gaze_rotation` and `fb2_gaze_max_angle_unspecified`.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `brow_inner_raise_left` | INNER_BROW_RAISER_L | `xr_fb2` 654-655 | lifts the inner part of the left brow and the forehead | same | — |
| `brow_inner_raise_right` | INNER_BROW_RAISER_R | `xr_fb2` 660-661 | lifts the inner part of the right brow and the forehead | same | — |
| `brow_outer_raise_left` | OUTER_BROW_RAISER_L | `xr_fb2` 861-862 | lifts the outer part of the left brow and the forehead | same | — |
| `brow_outer_raise_right` | OUTER_BROW_RAISER_R | `xr_fb2` 867-868 | lifts the outer part of the right brow and the forehead | same | — |
| `brow_lower_left` | BROW_LOWERER_L | `xr_fb2` 512-513 | lowers the left brow and draws it in; the middle of the forehead lowers too | same | — |
| `brow_lower_right` | BROW_LOWERER_R | `xr_fb2` 518-519 | lowers the right brow and draws it in; the middle of the forehead lowers too | same | — |
| `eye_close_left` | EYES_CLOSED_L | `xr_fb2` 585-586 | lowers the upper lid until it covers the left eye | same | — |
| `eye_close_right` | EYES_CLOSED_R | `xr_fb2` 591-592 | lowers the upper lid until it covers the right eye | same | — |
| `lid_tighten_left` | LID_TIGHTENER_L | `xr_fb2` 687-689 | tightens the rings around the left eyelids and pushes the lower lid toward the inner corner | same | — |
| `lid_tighten_right` | LID_TIGHTENER_R | `xr_fb2` 693-695 | tightens the rings around the right eyelids and pushes the lower lid toward the inner corner | same | — |
| `upper_lid_raise_left` | UPPER_LID_RAISER_L | `xr_fb2` 873-874 | pulls the left upper lid up and back, so the eye opens wider | same | — |
| `upper_lid_raise_right` | UPPER_LID_RAISER_R | `xr_fb2` 879-880 | pulls the right upper lid up and back, so the eye opens wider | same | — |
| `gaze_in_left` | EYES_LOOK_RIGHT_L | `xr_fb2` 621-622 | moves the left eye with a rightward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_in_right` | EYES_LOOK_LEFT_R | `xr_fb2` 615-616 | moves the right eye with a leftward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_out_left` | EYES_LOOK_LEFT_L | `xr_fb2` 609-610 | moves the left eye with a leftward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_out_right` | EYES_LOOK_RIGHT_R | `xr_fb2` 627-628 | moves the right eye with a rightward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_up_left` | EYES_LOOK_UP_L | `xr_fb2` 633-634 | moves the left eye with a upward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_up_right` | EYES_LOOK_UP_R | `xr_fb2` 639-640 | moves the right eye with a upward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_down_left` | EYES_LOOK_DOWN_L | `xr_fb2` 597-598 | moves the left eye with a downward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `gaze_down_right` | EYES_LOOK_DOWN_R | `xr_fb2` 603-604 | moves the right eye with a downward gaze; the eight LOOK weights are linear in angle, 1 is the maximum angle, and only one of two opposing directions is non-zero (lines 643-649) | differs | FB2 gaze in and out, `fb2_gaze_rotation` |
| `cheek_puff_left` | CHEEK_PUFF_L | `xr_fb2` 524-525 | fills the left cheek with air so that it rounds outward | same | — |
| `cheek_puff_right` | CHEEK_PUFF_R | `xr_fb2` 530-531 | fills the right cheek with air so that it rounds outward | same | — |
| `cheek_raise_left` | CHEEK_RAISER_L | `xr_fb2` 536-537 | tightens the outer rings around the left eye and narrows the outer eye corner | same | — |
| `cheek_raise_right` | CHEEK_RAISER_R | `xr_fb2` 542-543 | tightens the outer rings around the right eye and narrows the outer eye corner | same | — |
| `cheek_suck_left` | CHEEK_SUCK_L | `xr_fb2` 548-549 | draws the left cheek in against the teeth | same | — |
| `cheek_suck_right` | CHEEK_SUCK_R | `xr_fb2` 554-555 | draws the right cheek in against the teeth | same | — |
| `nose_wrinkle_left` | NOSE_WRINKLER_L | `xr_fb2` 847-849 | lifts the left side of the nose, the nostril and the middle of the upper lip | same | — |
| `nose_wrinkle_right` | NOSE_WRINKLER_R | `xr_fb2` 854-856 | lifts the right side of the nose, the nostril and the middle of the upper lip | same | — |
| `jaw_drop` | JAW_DROP | `xr_fb2` 666-667 | moves the lower jaw down and back | same | — |
| `jaw_thrust` | JAW_THRUST | `xr_fb2` 682 | moves the lower jaw forward | same | — |
| `jaw_sideways_left` | JAW_SIDEWAYS_LEFT | `xr_fb2` 672 | moves the lower jaw leftward | same | — |
| `jaw_sideways_right` | JAW_SIDEWAYS_RIGHT | `xr_fb2` 677 | moves the lower jaw rightward | same | — |
| `lip_corner_pull_left` | LIP_CORNER_PULLER_L | `xr_fb2` 709-710 | draws the left lip corner up, back and outward | same | — |
| `lip_corner_pull_right` | LIP_CORNER_PULLER_R | `xr_fb2` 715-716 | draws the right lip corner up, back and outward | same | — |
| `lip_corner_depress_left` | LIP_CORNER_DEPRESSOR_L | `xr_fb2` 699 | draws the left lip corner down | same | — |
| `lip_corner_depress_right` | LIP_CORNER_DEPRESSOR_R | `xr_fb2` 704 | draws the right lip corner down | same | — |
| `dimple_left` | DIMPLER_L | `xr_fb2` 573-575 | presses the left lip corner against the teeth and draws it back, often up | same | — |
| `dimple_right` | DIMPLER_R | `xr_fb2` 579-581 | presses the right lip corner against the teeth and draws it back, often up | same | — |
| `lip_stretch_left` | LIP_STRETCHER_L | `xr_fb2` 769-770 | draws the left lip corner outward and stretches the lips | same | — |
| `lip_stretch_right` | LIP_STRETCHER_R | `xr_fb2` 775-776 | draws the right lip corner outward and stretches the lips | same | — |
| `mouth_shift_left` | MOUTH_LEFT | `xr_fb2` 835-836 | pulls the left lip corner leftward and pushes the other side of the mouth toward it | same | — |
| `mouth_shift_right` | MOUTH_RIGHT | `xr_fb2` 841-842 | pulls the right lip corner rightward and pushes the other side of the mouth toward it | same | — |
| `chin_raise` | CHIN_RAISER_B | `xr_fb2` 560-561 | pushes the chin skin and the lower lip up | same | — |
| `chin_raise_upper_lip` | CHIN_RAISER_T | `xr_fb2` 566-568 | pushes the upper lip up; the text says the upward push of CHIN_RAISER_B causes it | same | — |
| `lip_funnel_upper_left` | LIP_FUNNELER_LT | `xr_fb2` 727-729 | pushes the upper left lip outward and forward; the mouth tends to round and the lips to part | same | — |
| `lip_funnel_upper_right` | LIP_FUNNELER_RT | `xr_fb2` 739-741 | pushes the upper right lip outward and forward; the mouth tends to round and the lips to part | same | — |
| `lip_funnel_lower_left` | LIP_FUNNELER_LB | `xr_fb2` 721-723 | pushes the lower left lip outward and forward; the mouth tends to round and the lips to part | same | — |
| `lip_funnel_lower_right` | LIP_FUNNELER_RB | `xr_fb2` 733-735 | pushes the lower right lip outward and forward; the mouth tends to round and the lips to part | same | — |
| `lip_pucker_left` | LIP_PUCKER_L | `xr_fb2` 757-758 | draws the left lip corner toward the middle so that the lips push forward | same | — |
| `lip_pucker_right` | LIP_PUCKER_R | `xr_fb2` 763-764 | draws the right lip corner toward the middle so that the lips push forward | same | — |
| `lip_suck_upper_left` | LIP_SUCK_LT | `xr_fb2` 787-788 | draws the upper left lip into the mouth | same | — |
| `lip_suck_upper_right` | LIP_SUCK_RT | `xr_fb2` 799-800 | draws the upper right lip into the mouth | same | — |
| `lip_suck_lower_left` | LIP_SUCK_LB | `xr_fb2` 781-782 | draws the lower left lip into the mouth | same | — |
| `lip_suck_lower_right` | LIP_SUCK_RB | `xr_fb2` 793-794 | draws the lower right lip into the mouth | same | — |
| `lip_press_left` | LIP_PRESSOR_L | `xr_fb2` 745-746 | presses the left upper and lower lips together | same | — |
| `lip_press_right` | LIP_PRESSOR_R | `xr_fb2` 751-752 | presses the right upper and lower lips together | same | — |
| `lip_tighten_left` | LIP_TIGHTENER_L | `xr_fb2` 805-806 | narrows the left lips in the horizontal plane | same | — |
| `lip_tighten_right` | LIP_TIGHTENER_R | `xr_fb2` 811-812 | narrows the right lips in the horizontal plane | same | — |
| `lips_toward` | LIPS_TOWARD | `xr_fb2` 817-818 | brings the lips into contact and keeps the mouth closed, whatever the jaw position | same | — |
| `upper_lip_raise_left` | UPPER_LIP_RAISER_L | `xr_fb2` 885-886 | lifts the left upper lip, more to the side than the nose wrinkler does | same | — |
| `upper_lip_raise_right` | UPPER_LIP_RAISER_R | `xr_fb2` 891-892 | lifts the right upper lip, more to the side than the nose wrinkler does | same | — |
| `lower_lip_depress_left` | LOWER_LIP_DEPRESSOR_L | `xr_fb2` 823-824 | draws the left lower lip down and a little outward | same | — |
| `lower_lip_depress_right` | LOWER_LIP_DEPRESSOR_R | `xr_fb2` 829-830 | draws the right lower lip down and a little outward | same | — |
| `tongue_out` | TONGUE_OUT | `xr_fb2` 928 | puts the tongue out | same | — |
| `tongue_retreat` | TONGUE_RETREAT | `xr_fb2` 933-934 | pulls the tongue back toward the throat and keeps it low, as for the AA viseme | same | — |
| `tongue_tip_interdental` | TONGUE_TIP_INTERDENTAL | `xr_fb2` 897-899 | puts the tongue tip on the upper teeth, just past the teeth line, as for the TH viseme | same | — |
| `tongue_tip_alveolar` | TONGUE_TIP_ALVEOLAR | `xr_fb2` 904-905 | puts the tongue tip on the back of the upper teeth, as for the NN viseme | same | — |
| `tongue_front_dorsal_palate` | TONGUE_FRONT_DORSAL_PALATE | `xr_fb2` 910-911 | presses the front of the tongue on the palate, as for the CH viseme | same | — |
| `tongue_mid_dorsal_palate` | TONGUE_MID_DORSAL_PALATE | `xr_fb2` 916-917 | presses the middle of the tongue on the palate, as for the DD viseme | same | — |
| `tongue_back_dorsal_velar` | TONGUE_BACK_DORSAL_VELAR | `xr_fb2` 922-923 | presses the back of the tongue on the palate, as for the KK viseme | same | — |

## ARKit

Record `apple_blendshapes` (Apple documentation data, reference only). Each coefficient goes from 0.0, neutral, to 1.0, the maximum movement (Discussion). 60 rows: 36 `same`, 22 `differs`, 2 `unresolved`.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `brow_inner_raise_left` | browInnerUp | `apple_blendshapes`, abstract of `browInnerUp` | the inner parts of both brows move up (one coefficient for both sides) | same | — |
| `brow_inner_raise_right` | browInnerUp | `apple_blendshapes`, abstract of `browInnerUp` | the inner parts of both brows move up (one coefficient for both sides) | same | — |
| `brow_outer_raise_left` | browOuterUpLeft | `apple_blendshapes`, abstract of `browOuterUpLeft` | the outer part of the left brow moves up | same | — |
| `brow_outer_raise_right` | browOuterUpRight | `apple_blendshapes`, abstract of `browOuterUpRight` | the outer part of the right brow moves up | same | — |
| `brow_lower_left` | browDownLeft | `apple_blendshapes`, abstract of `browDownLeft` | the outer part of the left brow moves down; the canonical signal is the whole brow lowering | differs | ARKit in and out, `arkit_browdown_outer` |
| `brow_lower_right` | browDownRight | `apple_blendshapes`, abstract of `browDownRight` | the outer part of the right brow moves down; the canonical signal is the whole brow lowering | differs | ARKit in and out, `arkit_browdown_outer` |
| `eye_close_left` | eyeBlinkLeft | `apple_blendshapes`, abstract of `eyeBlinkLeft` | the lids close over the left eye | same | — |
| `eye_close_right` | eyeBlinkRight | `apple_blendshapes`, abstract of `eyeBlinkRight` | the lids close over the right eye | same | — |
| `lid_tighten_left` | eyeSquintLeft | `apple_blendshapes`, abstract of `eyeSquintLeft` | the face around the left eye contracts; the canonical signal is the lids only | differs | ARKit in and out, `arkit_eyesquint_face` |
| `lid_tighten_right` | eyeSquintRight | `apple_blendshapes`, abstract of `eyeSquintRight` | the face around the right eye contracts; the canonical signal is the lids only | differs | ARKit in and out, `arkit_eyesquint_face` |
| `upper_lid_raise_left` | eyeWideLeft | `apple_blendshapes`, abstract of `eyeWideLeft` | the lids around the left eye widen | same | — |
| `upper_lid_raise_right` | eyeWideRight | `apple_blendshapes`, abstract of `eyeWideRight` | the lids around the right eye widen | same | — |
| `gaze_in_left` | eyeLookInLeft | `apple_blendshapes`, abstract of `eyeLookInLeft` | the left eyelids move as they do with a rightward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_in_right` | eyeLookInRight | `apple_blendshapes`, abstract of `eyeLookInRight` | the right eyelids move as they do with a leftward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_out_left` | eyeLookOutLeft | `apple_blendshapes`, abstract of `eyeLookOutLeft` | the left eyelids move as they do with a leftward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_out_right` | eyeLookOutRight | `apple_blendshapes`, abstract of `eyeLookOutRight` | the right eyelids move as they do with a rightward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_up_left` | eyeLookUpLeft | `apple_blendshapes`, abstract of `eyeLookUpLeft` | the left eyelids move as they do with a upward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_up_right` | eyeLookUpRight | `apple_blendshapes`, abstract of `eyeLookUpRight` | the right eyelids move as they do with a upward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_down_left` | eyeLookDownLeft | `apple_blendshapes`, abstract of `eyeLookDownLeft` | the left eyelids move as they do with a downward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `gaze_down_right` | eyeLookDownRight | `apple_blendshapes`, abstract of `eyeLookDownRight` | the right eyelids move as they do with a downward gaze; eyelid movement, not eye rotation | differs | ARKit in and out, `arkit_gaze_eyelid` |
| `cheek_puff_left` | cheekPuff | `apple_blendshapes`, abstract of `cheekPuff` | both cheeks move outward (one coefficient for both sides) | same | — |
| `cheek_puff_right` | cheekPuff | `apple_blendshapes`, abstract of `cheekPuff` | both cheeks move outward (one coefficient for both sides) | same | — |
| `cheek_raise_left` | cheekSquintLeft | `apple_blendshapes`, abstract of `cheekSquintLeft` | the cheek around and below the left eye moves up; the canonical signal is the tightening of the ring around the eye | differs | ARKit in and out, `arkit_cheeksquint_cheek` |
| `cheek_raise_right` | cheekSquintRight | `apple_blendshapes`, abstract of `cheekSquintRight` | the cheek around and below the right eye moves up; the canonical signal is the tightening of the ring around the eye | differs | ARKit in and out, `arkit_cheeksquint_cheek` |
| `nose_wrinkle_left` | noseSneerLeft | `apple_blendshapes`, abstract of `noseSneerLeft` | the left side of the nose rises around the nostril | same | — |
| `nose_wrinkle_right` | noseSneerRight | `apple_blendshapes`, abstract of `noseSneerRight` | the right side of the nose rises around the nostril | same | — |
| `jaw_drop` | jawOpen | `apple_blendshapes`, abstract of `jawOpen` | the lower jaw opens | same | — |
| `jaw_thrust` | jawForward | `apple_blendshapes`, abstract of `jawForward` | the lower jaw moves forward | same | — |
| `jaw_sideways_left` | jawLeft | `apple_blendshapes`, abstract of `jawLeft` | the lower jaw moves leftward | same | — |
| `jaw_sideways_right` | jawRight | `apple_blendshapes`, abstract of `jawRight` | the lower jaw moves rightward | same | — |
| `lip_corner_pull_left` | mouthSmileLeft | `apple_blendshapes`, abstract of `mouthSmileLeft` | the left mouth corner moves up; upward only, where the canonical signal is also back and outward | differs | ARKit in and out, `arkit_mouthsmile_upward` |
| `lip_corner_pull_right` | mouthSmileRight | `apple_blendshapes`, abstract of `mouthSmileRight` | the right mouth corner moves up; upward only, where the canonical signal is also back and outward | differs | ARKit in and out, `arkit_mouthsmile_upward` |
| `lip_corner_depress_left` | mouthFrownLeft | `apple_blendshapes`, abstract of `mouthFrownLeft` | the left mouth corner moves down | same | — |
| `lip_corner_depress_right` | mouthFrownRight | `apple_blendshapes`, abstract of `mouthFrownRight` | the right mouth corner moves down | same | — |
| `dimple_left` | mouthDimpleLeft | `apple_blendshapes`, abstract of `mouthDimpleLeft` | the left mouth corner moves back | same | — |
| `dimple_right` | mouthDimpleRight | `apple_blendshapes`, abstract of `mouthDimpleRight` | the right mouth corner moves back | same | — |
| `lip_stretch_left` | mouthStretchLeft | `apple_blendshapes`, abstract of `mouthStretchLeft` | the left mouth corner moves leftward | same | — |
| `lip_stretch_right` | mouthStretchRight | `apple_blendshapes`, abstract of `mouthStretchRight` | the abstract describes rightward movement but names the left mouth corner; the coefficient name and RCEF's profile (`side = "right"`) say right | unresolved | ARKit in and out, `arkit_mouthstretchright_text_side` |
| `mouth_shift_left` | mouthLeft | `apple_blendshapes`, abstract of `mouthLeft` | both lips move leftward together | same | — |
| `mouth_shift_right` | mouthRight | `apple_blendshapes`, abstract of `mouthRight` | both lips move rightward together | same | — |
| `chin_raise` | mouthShrugLower | `apple_blendshapes`, abstract of `mouthShrugLower` | the lower lip moves outward; the canonical signal pushes the chin and lower lip up | differs | ARKit in and out, `arkit_mouthshrug_outward` |
| `chin_raise_upper_lip` | mouthShrugUpper | `apple_blendshapes`, abstract of `mouthShrugUpper` | the upper lip moves outward; the canonical signal pushes it up | differs | ARKit in and out, `arkit_mouthshrug_outward` |
| `lip_funnel_upper_left` | mouthFunnel | `apple_blendshapes`, abstract of `mouthFunnel` | both lips contract into an open shape (one coefficient for all four parts) | same | — |
| `lip_funnel_upper_right` | mouthFunnel | `apple_blendshapes`, abstract of `mouthFunnel` | both lips contract into an open shape (one coefficient for all four parts) | same | — |
| `lip_funnel_lower_left` | mouthFunnel | `apple_blendshapes`, abstract of `mouthFunnel` | both lips contract into an open shape (one coefficient for all four parts) | same | — |
| `lip_funnel_lower_right` | mouthFunnel | `apple_blendshapes`, abstract of `mouthFunnel` | both lips contract into an open shape (one coefficient for all four parts) | same | — |
| `lip_pucker_left` | mouthPucker | `apple_blendshapes`, abstract of `mouthPucker` | both closed lips contract and are compressed (one coefficient for both sides); no forward push is stated, where the canonical signal pushes the lips forward | differs | ARKit in and out, `arkit_mouthpucker_compression` |
| `lip_pucker_right` | mouthPucker | `apple_blendshapes`, abstract of `mouthPucker` | both closed lips contract and are compressed (one coefficient for both sides); no forward push is stated, where the canonical signal pushes the lips forward | differs | ARKit in and out, `arkit_mouthpucker_compression` |
| `lip_suck_upper_left` | mouthRollUpper | `apple_blendshapes`, abstract of `mouthRollUpper` | the upper lip moves into the mouth (one coefficient for both sides) | same | — |
| `lip_suck_upper_right` | mouthRollUpper | `apple_blendshapes`, abstract of `mouthRollUpper` | the upper lip moves into the mouth (one coefficient for both sides) | same | — |
| `lip_suck_lower_left` | mouthRollLower | `apple_blendshapes`, abstract of `mouthRollLower` | the lower lip moves into the mouth (one coefficient for both sides) | same | — |
| `lip_suck_lower_right` | mouthRollLower | `apple_blendshapes`, abstract of `mouthRollLower` | the lower lip moves into the mouth (one coefficient for both sides) | same | — |
| `lip_press_left` | mouthPressLeft | `apple_blendshapes`, abstract of `mouthPressLeft` | the lower lip is compressed upward on the left side; the canonical signal presses both lips together | differs | ARKit in and out, `arkit_mouthpress_lower_lip` |
| `lip_press_right` | mouthPressRight | `apple_blendshapes`, abstract of `mouthPressRight` | the lower lip is compressed upward on the right side; the canonical signal presses both lips together | differs | ARKit in and out, `arkit_mouthpress_lower_lip` |
| `lips_toward` | mouthClose | `apple_blendshapes`, abstract of `mouthClose` | the lips close, and the abstract stresses that this is apart from the jaw position. RCEF's own calibration record reads ARKit as defining it together with jawOpen (`calibration/rig-gains.ict-rocketbox-female.cal` line 21), and on the ICT rig mouthClose alone failed 24 of 24 held-out conditions (`examples/data/rig_gains.json` line 105). The evidence conflicts | unresolved | ARKit in and out, `arkit_mouthclose_jaw_unresolved` |
| `upper_lip_raise_left` | mouthUpperUpLeft | `apple_blendshapes`, abstract of `mouthUpperUpLeft` | the upper lip moves up on the left side | same | — |
| `upper_lip_raise_right` | mouthUpperUpRight | `apple_blendshapes`, abstract of `mouthUpperUpRight` | the upper lip moves up on the right side | same | — |
| `lower_lip_depress_left` | mouthLowerDownLeft | `apple_blendshapes`, abstract of `mouthLowerDownLeft` | the lower lip moves down on the left side | same | — |
| `lower_lip_depress_right` | mouthLowerDownRight | `apple_blendshapes`, abstract of `mouthLowerDownRight` | the lower lip moves down on the right side | same | — |
| `tongue_out` | tongueOut | `apple_blendshapes`, abstract of `tongueOut` | the tongue extends; no length is stated (existing loss "no stated length" on each `tongue_out` hop) | same | — |

## VRCFaceTracking Unified Expressions

Record `vrcft_docs_shapes` (VRCFaceTracking docs `3036f46`, reference only). Phase 1 has out-maps only. 64 rows: 41 `same`, 21 `differs`, 2 `unresolved`. The out-hops for `cheek_suck_*` and `lip_tighten_*` come with the FB2-only signals.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `brow_inner_raise_left` | BrowInnerUpLeft | `vrcft_docs_shapes` 147 | the inner part of the left brow pulls up | same | — |
| `brow_inner_raise_right` | BrowInnerUpRight | `vrcft_docs_shapes` 142 | the inner part of the right brow pulls up | same | — |
| `brow_outer_raise_left` | BrowOuterUpLeft | `vrcft_docs_shapes` 157 | the outer part of the left brow pulls up | same | — |
| `brow_outer_raise_right` | BrowOuterUpRight | `vrcft_docs_shapes` 152 | the outer part of the right brow pulls up | same | — |
| `brow_lower_left` | BrowLowererLeft and BrowPinchLeft | `vrcft_docs_shapes` 137, 127 | two parts: the outer left brow pulls down, and the left brow pinches in; the canonical signal is the whole action, and the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `brow_lower_right` | BrowLowererRight and BrowPinchRight | `vrcft_docs_shapes` 132, 122 | two parts: the outer right brow pulls down, and the right brow pinches in; the canonical signal is the whole action, and the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `eye_close_left` | EyeClosedLeft | `vrcft_docs_shapes` 77 | closes the left eyelid | same | — |
| `eye_close_right` | EyeClosedRight | `vrcft_docs_shapes` 72 | closes the right eyelid | same | — |
| `lid_tighten_left` | EyeSquintLeft | `vrcft_docs_shapes` 87 | squeezes the muscles of the left eye socket; the canonical signal is the lids only | differs | VRCFT UE out, `vrcft_ue_eyesquint_socket` |
| `lid_tighten_right` | EyeSquintRight | `vrcft_docs_shapes` 82 | squeezes the muscles of the right eye socket; the canonical signal is the lids only | differs | VRCFT UE out, `vrcft_ue_eyesquint_socket` |
| `upper_lid_raise_left` | EyeWideLeft | `vrcft_docs_shapes` 97 | the left eyelid opens wider than relaxed | same | — |
| `upper_lid_raise_right` | EyeWideRight | `vrcft_docs_shapes` 92 | the right eyelid opens wider than relaxed | same | — |
| `gaze_in_left` | EyeLookInLeft | `vrcft_docs_shapes` 57 | the left eye looks in; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_in_right` | EyeLookInRight | `vrcft_docs_shapes` 37 | the right eye looks in; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_out_left` | EyeLookOutLeft | `vrcft_docs_shapes` 52 | the left eye looks out; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_out_right` | EyeLookOutRight | `vrcft_docs_shapes` 32 | the right eye looks out; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_up_left` | EyeLookUpLeft | `vrcft_docs_shapes` 62 | the left eye looks up; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_up_right` | EyeLookUpRight | `vrcft_docs_shapes` 42 | the right eye looks up; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_down_left` | EyeLookDownLeft | `vrcft_docs_shapes` 67 | the left eye looks down; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `gaze_down_right` | EyeLookDownRight | `vrcft_docs_shapes` 47 | the right eye looks down; no maximum angle is stated | differs | VRCFT UE out, `vrcft_ue_gaze_no_angle` |
| `cheek_puff_left` | CheekPuffLeft | `vrcft_docs_shapes` 207 | puffs the left cheek | same | — |
| `cheek_puff_right` | CheekPuffRight | `vrcft_docs_shapes` 202 | puffs the right cheek | same | — |
| `cheek_raise_left` | CheekSquintLeft | `vrcft_docs_shapes` 197 | raises the left cheek; the canonical signal is the tightening of the ring around the eye | differs | VRCFT UE out, `vrcft_ue_cheeksquint_cheek` |
| `cheek_raise_right` | CheekSquintRight | `vrcft_docs_shapes` 192 | raises the right cheek; the canonical signal is the tightening of the ring around the eye | differs | VRCFT UE out, `vrcft_ue_cheeksquint_cheek` |
| `cheek_suck_left` | CheekSuckLeft | `vrcft_docs_shapes` 217 | sucks in the left cheek (out-hop added with the FB2-only signals) | same | — |
| `cheek_suck_right` | CheekSuckRight | `vrcft_docs_shapes` 212 | sucks in the right cheek (out-hop added with the FB2-only signals) | same | — |
| `nose_wrinkle_left` | NoseSneerLeft | `vrcft_docs_shapes` 167 | the left side of the face sneers; the shape is named for the nose | same | — |
| `nose_wrinkle_right` | NoseSneerRight | `vrcft_docs_shapes` 162 | the right side of the face sneers; the shape is named for the nose | same | — |
| `jaw_drop` | JawOpen | `vrcft_docs_shapes` 222 | opens the jaw | same | — |
| `jaw_thrust` | JawForward | `vrcft_docs_shapes` 242 | pushes the jaw forward | same | — |
| `jaw_sideways_left` | JawLeft | `vrcft_docs_shapes` 237 | pushes the jaw to the left | same | — |
| `jaw_sideways_right` | JawRight | `vrcft_docs_shapes` 232 | pushes the jaw to the right | same | — |
| `lip_corner_pull_left` | MouthCornerPullLeft and MouthCornerSlantLeft | `vrcft_docs_shapes` 387, 397 | two parts: the left corner pulls up and out on a diagonal, and the left corner slants up; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `lip_corner_pull_right` | MouthCornerPullRight and MouthCornerSlantRight | `vrcft_docs_shapes` 382, 392 | two parts: the right corner pulls up and out on a diagonal, and the right corner slants up; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `lip_corner_depress_left` | MouthFrownLeft | `vrcft_docs_shapes` 407 | the left lip corner pulls down | same | — |
| `lip_corner_depress_right` | MouthFrownRight | `vrcft_docs_shapes` 402 | the right lip corner pulls down | same | — |
| `dimple_left` | MouthDimpleLeft | `vrcft_docs_shapes` 427 | the left lip corner moves back | same | — |
| `dimple_right` | MouthDimpleRight | `vrcft_docs_shapes` 422 | the right lip corner moves back | same | — |
| `lip_stretch_left` | MouthStretchLeft | `vrcft_docs_shapes` 417 | the left lip corner pulls out and down | same | — |
| `lip_stretch_right` | MouthStretchRight | `vrcft_docs_shapes` 412 | the right lip corner pulls out and down | same | — |
| `mouth_shift_left` | MouthUpperLeft and MouthLowerLeft | `vrcft_docs_shapes` 367, 377 | two parts: the upper lip moves to the left, and the lower lip moves to the left; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `mouth_shift_right` | MouthUpperRight and MouthLowerRight | `vrcft_docs_shapes` 362, 372 | two parts: the upper lip moves to the right, and the lower lip moves to the right; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `chin_raise` | MouthRaiserLower | `vrcft_docs_shapes` 437 | the lower mouth rises and pushes out a little | same | — |
| `chin_raise_upper_lip` | MouthRaiserUpper | `vrcft_docs_shapes` 432 | the upper mouth rises and pushes out a little | same | — |
| `lip_funnel_upper_left` | LipFunnelUpperLeft | `vrcft_docs_shapes` 297 | the upper left part of the lips pushes into a funnel | same | — |
| `lip_funnel_upper_right` | LipFunnelUpperRight | `vrcft_docs_shapes` 292 | the upper right part of the lips pushes into a funnel | same | — |
| `lip_funnel_lower_left` | LipFunnelLowerLeft | `vrcft_docs_shapes` 307 | the lower left part of the lips pushes into a funnel | same | — |
| `lip_funnel_lower_right` | LipFunnelLowerRight | `vrcft_docs_shapes` 302 | the lower right part of the lips pushes into a funnel | same | — |
| `lip_pucker_left` | LipPuckerUpperLeft and LipPuckerLowerLeft | `vrcft_docs_shapes` 317, 327 | two parts: the upper and the lower left part of the lips push outward; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `lip_pucker_right` | LipPuckerUpperRight and LipPuckerLowerRight | `vrcft_docs_shapes` 312, 322 | two parts: the upper and the lower right part of the lips push outward; the out-hop sets both parts equal | differs | VRCFT UE out, `vrcft_ue_set_equal` |
| `lip_suck_upper_left` | LipSuckUpperLeft | `vrcft_docs_shapes` 267 | the upper left part of the lips tucks into the mouth | same | — |
| `lip_suck_upper_right` | LipSuckUpperRight | `vrcft_docs_shapes` 262 | the upper right part of the lips tucks into the mouth | same | — |
| `lip_suck_lower_left` | LipSuckLowerLeft | `vrcft_docs_shapes` 277 | the lower left part of the lips tucks into the mouth | same | — |
| `lip_suck_lower_right` | LipSuckLowerRight | `vrcft_docs_shapes` 272 | the lower right part of the lips tucks into the mouth | same | — |
| `lip_press_left` | MouthPressLeft | `vrcft_docs_shapes` 447 | the left lips press together and flatten vertically | same | — |
| `lip_press_right` | MouthPressRight | `vrcft_docs_shapes` 442 | the right lips press together and flatten vertically | same | — |
| `lip_tighten_left` | MouthTightenerLeft | `vrcft_docs_shapes` 457 | the left lips squeeze together horizontally (out-hop added with the FB2-only signals) | same | — |
| `lip_tighten_right` | MouthTightenerRight | `vrcft_docs_shapes` 452 | the right lips squeeze together horizontally (out-hop added with the FB2-only signals) | same | — |
| `lips_toward` | MouthClosed | `vrcft_docs_shapes` 227 | closes the mouth relative to JawOpen; the canonical signal is defined at any jaw opening | differs | VRCFT UE out, `vrcft_ue_mouthclosed_jaw_relative` |
| `upper_lip_raise_left` | MouthUpperUpLeft | `vrcft_docs_shapes` 337 | the upper left part of the lip pulls up | same | — |
| `upper_lip_raise_right` | MouthUpperUpRight | `vrcft_docs_shapes` 332 | the upper right part of the lip pulls up | same | — |
| `lower_lip_depress_left` | MouthLowerDownLeft | `vrcft_docs_shapes` 347 | the docs say the lower left part of the lip pulls up, while the name says down (RCEF's profile, `profiles/vrcft.artist.base.toml` lines 1009 and 1025) | unresolved | VRCFT UE out, `vrcft_ue_mouthlowerdown_direction_unresolved` |
| `lower_lip_depress_right` | MouthLowerDownRight | `vrcft_docs_shapes` 342 | the docs say the lower right part of the lip pulls up, while the name says down (RCEF's profile, `profiles/vrcft.artist.base.toml` lines 1009 and 1025) | unresolved | VRCFT UE out, `vrcft_ue_mouthlowerdown_direction_unresolved` |
| `tongue_out` | TongueOut | `vrcft_docs_shapes` 462 | the tongue sticks out of the mouth where it can be seen; no length is stated (existing loss "no stated length") | same | — |

## VRCFaceTracking eye

Record `vrcft_data` (VRCFaceTracking `6432e6a`, Apache-2.0). 4 rows: 2 `same`, 2 `differs`.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `eye_close_left` | `Left.Openness` | `vrcft_data` 14; `vrcft_code_parameters` 40 | how open the left eye is, starting at 1; the same project computes the left eye's closure as 1 − openness. It does not say that 1 is a relaxed open eye | differs | VRCFaceTracking eye blink in and out, `vrcft_eye_openness_endpoint` |
| `eye_close_right` | `Right.Openness` | `vrcft_data` 14; `vrcft_code_parameters` 41 | as for the left eye | differs | VRCFaceTracking eye blink in and out, `vrcft_eye_openness_endpoint` |
| `pupil_diameter_mm_left` | `Left.PupilDiameter_MM` | `vrcft_data` 13 | the pupil diameter of the left eye in millimetres | same | — |
| `pupil_diameter_mm_right` | `Right.PupilDiameter_MM` | `vrcft_data` 13 | the pupil diameter of the right eye in millimetres | same | — |

## VRM

Record `vrm_expressions` (vrm-specification `94e82dd`, reference only). 7 rows: 5 `differs`, 2 `unresolved`.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `eye_close_left` | `blinkLeft` | `vrm_expressions` 178 | closes the left eyelid; whose left is not stated ([Frames](#frames-whose-left)) | unresolved | VRM blink in and out, `vrm_blink_side_unresolved` |
| `eye_close_right` | `blinkRight` | `vrm_expressions` 179 | closes the right eyelid; whose right is not stated | unresolved | VRM blink in and out, `vrm_blink_side_unresolved` |
| `aa` | `aa` | `vrm_expressions` 163 | a lip-sync preset whose weight each model authors; remarked "aa" | differs | VRM vowel in and out, `vrm_vowel_asset_weight` |
| `ih` | `ih` | `vrm_expressions` 164 | a lip-sync preset; remarked "i", while META's IH is the vowel in "tip" | differs | VRM vowel in and out, `vrm_vowel_asset_weight`, `vrm_ih_vowel_quality` |
| `ou` | `ou` | `vrm_expressions` 165 | a lip-sync preset; remarked "u" | differs | VRM vowel in and out, `vrm_vowel_asset_weight` |
| `e` | `ee` | `vrm_expressions` 166 | a lip-sync preset; remarked "eh" | differs | VRM vowel in and out, `vrm_vowel_asset_weight` |
| `oh` | `oh` | `vrm_expressions` 167 | a lip-sync preset; remarked "oh" | differs | VRM vowel in and out, `vrm_vowel_asset_weight` |

## META visemes

Record `xr_visemes` (OpenXR-Docs `5a82d45`, CC-BY-4.0). Each value is a probability from 0 to 1, and the values sum to 1 when `isValid` is true (lines 104-107). The canonical visemes follow META, so all 15 rows are `same`.

| Signal | Source name | Locator | Paraphrase | Verdict | Owning hop, key |
|---|---|---|---|---|---|
| `sil` | SIL | `xr_visemes` 142 | silence; META lists it as neutral | same | — |
| `pp` | PP | `xr_visemes` 149 | the PP class, phonemes p, b, m | same | — |
| `ff` | FF | `xr_visemes` 156 | the FF class, phonemes f, v | same | — |
| `th` | TH | `xr_visemes` 163 | the TH class, phonemes th | same | — |
| `dd` | DD | `xr_visemes` 170 | the DD class, phonemes t, d | same | — |
| `kk` | KK | `xr_visemes` 177 | the KK class, phonemes k, g | same | — |
| `ch` | CH | `xr_visemes` 184 | the CH class, phonemes tS, dZ, S | same | — |
| `ss` | SS | `xr_visemes` 191 | the SS class, phonemes s, z | same | — |
| `nn` | NN | `xr_visemes` 198 | the NN class, phonemes n, l | same | — |
| `rr` | RR | `xr_visemes` 205 | the RR class, phonemes r | same | — |
| `aa` | AA | `xr_visemes` 212 | the AA class, phonemes A:, as in car | same | — |
| `e` | E | `xr_visemes` 219 | the E class, phonemes e, as in bed | same | — |
| `ih` | IH | `xr_visemes` 226 | the IH class, phonemes ih, as in tip | same | — |
| `oh` | OH | `xr_visemes` 233 | the OH class, phonemes oh, as in toe | same | — |
| `ou` | OU | `xr_visemes` 240 | the OU class, phonemes ou, as in book | same | — |

## FACS

Record `facs_wikipedia` (Wikipedia revision 1357638399, CC-BY-SA-4.0). Wikipedia gives a code number and a name, not a criterion. So `same` means only that the FACS name names the action that the canonical definition describes. Code names are given as facts. 53 signal rows: 49 `same`, 2 `differs`, 2 `unresolved`. The four encoding and frame rows follow the table.

| Signal | FACS code (`facs.code` ID) | Locator | Code and name | Difference | Verdict | Owning hop, key |
|---|---|---|---|---|---|---|
| `brow_inner_raise_left` | L1 (`facs.code.au01_left`) | `facs_wikipedia` raw line 89 | 1 Inner brow raiser | none on the action | same | — |
| `brow_inner_raise_right` | R1 (`facs.code.au01_right`) | `facs_wikipedia` raw line 89 | 1 Inner brow raiser | none on the action | same | — |
| `brow_outer_raise_left` | L2 (`facs.code.au02_left`) | `facs_wikipedia` raw line 91 | 2 Outer brow raiser | none on the action | same | — |
| `brow_outer_raise_right` | R2 (`facs.code.au02_right`) | `facs_wikipedia` raw line 91 | 2 Outer brow raiser | none on the action | same | — |
| `brow_lower_left` | L4 (`facs.code.au04_left`) | `facs_wikipedia` raw line 93 | 4 Brow lowerer | none on the action | same | — |
| `brow_lower_right` | R4 (`facs.code.au04_right`) | `facs_wikipedia` raw line 93 | 4 Brow lowerer | none on the action | same | — |
| `eye_close_left` | L43 (`facs.code.au43_left`) | `facs_wikipedia` raw line 257 | 43 Eyes closed | none on the action. Wikipedia gives 43 no intensity scale (gross table, line 224); FACS 2002 scores it by intensity (`facs_hager_2002`), but no public source gives its letters, so 1 = eye fully closed is RCEF's assumption (gross-code row below) | same | — |
| `eye_close_right` | R43 (`facs.code.au43_right`) | `facs_wikipedia` raw line 257 | 43 Eyes closed | none on the action. Wikipedia gives 43 no intensity scale (gross table, line 224); FACS 2002 scores it by intensity (`facs_hager_2002`), but no public source gives its letters, so 1 = eye fully closed is RCEF's assumption (gross-code row below) | same | — |
| `lid_tighten_left` | L7 (`facs.code.au07_left`) | `facs_wikipedia` raw line 99 | 7 Lid tightener | none on the action | same | — |
| `lid_tighten_right` | R7 (`facs.code.au07_right`) | `facs_wikipedia` raw line 99 | 7 Lid tightener | none on the action | same | — |
| `upper_lid_raise_left` | L5 (`facs.code.au05_left`) | `facs_wikipedia` raw line 95 | 5 Upper lid raiser | none on the action | same | — |
| `upper_lid_raise_right` | R5 (`facs.code.au05_right`) | `facs_wikipedia` raw line 95 | 5 Upper lid raiser | none on the action | same | — |
| `cheek_puff_left` | L34 (`facs.code.au34_left`) | `facs_wikipedia` raw line 239 | 34 [Cheek] puff | none on the action | same | — |
| `cheek_puff_right` | R34 (`facs.code.au34_right`) | `facs_wikipedia` raw line 239 | 34 [Cheek] puff | none on the action | same | — |
| `cheek_raise_left` | L6 (`facs.code.au06_left`) | `facs_wikipedia` raw line 97 | 6 Cheek raiser | none on the action | same | — |
| `cheek_raise_right` | R6 (`facs.code.au06_right`) | `facs_wikipedia` raw line 97 | 6 Cheek raiser | none on the action | same | — |
| `cheek_suck_left` | L35 (`facs.code.au35_left`) | `facs_wikipedia` raw line 241 | 35 [Cheek] suck | none on the action | same | — |
| `cheek_suck_right` | R35 (`facs.code.au35_right`) | `facs_wikipedia` raw line 241 | 35 [Cheek] suck | none on the action | same | — |
| `nose_wrinkle_left` | L9 (`facs.code.au09_left`) | `facs_wikipedia` raw line 103 | 9 Nose wrinkler | none on the action | same | — |
| `nose_wrinkle_right` | R9 (`facs.code.au09_right`) | `facs_wikipedia` raw line 103 | 9 Nose wrinkler | none on the action | same | — |
| `jaw_drop` | 26 (`facs.code.au26`) | `facs_wikipedia` raw line 137 | 26 Jaw drop | FACS splits mouth opening into 25 Lips part (line 135), 26 Jaw drop and 27 Mouth stretch (line 139); the canonical signal is the whole jaw opening. The muscles listed for 27 open the jaw; those for 25 are lip muscles. FACS 2002 revised the intensity scoring of 25, 26 and 27 (`facs_hager_2002`) | differs | both FACS jaw hops, `facs_mouth_opening_split` |
| `jaw_thrust` | 29 (`facs.code.au29`) | `facs_wikipedia` raw line 229 | 29 Jaw thrust | none on the action | same | — |
| `jaw_sideways_left` | L30 (`facs.code.au30_left`) | `facs_wikipedia` raw line 231 | 30 Jaw sideways | Wikipedia's L and R modifiers name a side of the face (line 78). RCEF reads L30 and R30 as directions, as `examples/data/expressions.json` line 21 and `ict_facekit` lines 177-178 do. Whose left is not stated | unresolved | FACS in and out, `facs_au30_direction_unresolved` |
| `jaw_sideways_right` | R30 (`facs.code.au30_right`) | `facs_wikipedia` raw line 231 | 30 Jaw sideways | Wikipedia's L and R modifiers name a side of the face (line 78). RCEF reads L30 and R30 as directions, as `examples/data/expressions.json` line 21 and `ict_facekit` lines 177-178 do. Whose left is not stated | unresolved | FACS in and out, `facs_au30_direction_unresolved` |
| `lip_corner_pull_left` | L12 (`facs.code.au12_left`) | `facs_wikipedia` raw line 109 | 12 Lip corner puller | none on the action | same | — |
| `lip_corner_pull_right` | R12 (`facs.code.au12_right`) | `facs_wikipedia` raw line 109 | 12 Lip corner puller | none on the action | same | — |
| `lip_corner_depress_left` | L15 (`facs.code.au15_left`) | `facs_wikipedia` raw line 115 | 15 Lip corner depressor | none on the action | same | — |
| `lip_corner_depress_right` | R15 (`facs.code.au15_right`) | `facs_wikipedia` raw line 115 | 15 Lip corner depressor | none on the action | same | — |
| `dimple_left` | L14 (`facs.code.au14_left`) | `facs_wikipedia` raw line 113 | 14 Dimpler | none on the action | same | — |
| `dimple_right` | R14 (`facs.code.au14_right`) | `facs_wikipedia` raw line 113 | 14 Dimpler | none on the action | same | — |
| `lip_stretch_left` | L20 (`facs.code.au20_left`) | `facs_wikipedia` raw line 125 | 20 Lip stretcher | none on the action | same | — |
| `lip_stretch_right` | R20 (`facs.code.au20_right`) | `facs_wikipedia` raw line 125 | 20 Lip stretcher | none on the action | same | — |
| `chin_raise` | 17 (`facs.code.au17`) | `facs_wikipedia` raw line 119 | 17 Chin raiser | FACS 17 has no upper/lower split. The canonical set keeps the induced upper-lip push apart (`chin_raise_upper_lip`; `xr_fb2` lines 566-568; `examples/data/expressions.json` line 21) | differs | FACS in and out, `facs_au17_no_split` |
| `lip_funnel_upper_left` | L22 (`facs.code.au22_left`) | `facs_wikipedia` raw line 129 | 22 Lip funneler | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_funnel_upper_right` | R22 (`facs.code.au22_right`) | `facs_wikipedia` raw line 129 | 22 Lip funneler | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_funnel_lower_left` | L22 (`facs.code.au22_left`) | `facs_wikipedia` raw line 129 | 22 Lip funneler | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_funnel_lower_right` | R22 (`facs.code.au22_right`) | `facs_wikipedia` raw line 129 | 22 Lip funneler | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_pucker_left` | L18 (`facs.code.au18_left`) | `facs_wikipedia` raw line 121 | 18 Lip pucker | none on the action | same | — |
| `lip_pucker_right` | R18 (`facs.code.au18_right`) | `facs_wikipedia` raw line 121 | 18 Lip pucker | none on the action | same | — |
| `lip_suck_upper_left` | L28 (`facs.code.au28_left`) | `facs_wikipedia` raw line 141 | 28 Lip suck | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_suck_upper_right` | R28 (`facs.code.au28_right`) | `facs_wikipedia` raw line 141 | 28 Lip suck | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_suck_lower_left` | L28 (`facs.code.au28_left`) | `facs_wikipedia` raw line 141 | 28 Lip suck | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_suck_lower_right` | R28 (`facs.code.au28_right`) | `facs_wikipedia` raw line 141 | 28 Lip suck | FACS has no upper/lower split; same on the action, and the split loss is on the hop | same | FACS in: "symmetry is invented" (upper/lower); FACS out: "asymmetry irrecoverable" |
| `lip_press_left` | L24 (`facs.code.au24_left`) | `facs_wikipedia` raw line 133 | 24 Lip pressor | none on the action | same | — |
| `lip_press_right` | R24 (`facs.code.au24_right`) | `facs_wikipedia` raw line 133 | 24 Lip pressor | none on the action | same | — |
| `lip_tighten_left` | L23 (`facs.code.au23_left`) | `facs_wikipedia` raw line 131 | 23 Lip tightener | none on the action | same | — |
| `lip_tighten_right` | R23 (`facs.code.au23_right`) | `facs_wikipedia` raw line 131 | 23 Lip tightener | none on the action | same | — |
| `lips_toward` | 8 (`facs.code.au08`) | `facs_wikipedia` raw line 101 | 8 Lips toward each other | Wikipedia states no jaw relation | same | — |
| `upper_lip_raise_left` | L10 (`facs.code.au10_left`) | `facs_wikipedia` raw line 105 | 10 Upper lip raiser | none on the action | same | — |
| `upper_lip_raise_right` | R10 (`facs.code.au10_right`) | `facs_wikipedia` raw line 105 | 10 Upper lip raiser | none on the action | same | — |
| `lower_lip_depress_left` | L16 (`facs.code.au16_left`) | `facs_wikipedia` raw line 117 | 16 Lower lip depressor | none on the action | same | — |
| `lower_lip_depress_right` | R16 (`facs.code.au16_right`) | `facs_wikipedia` raw line 117 | 16 Lower lip depressor | none on the action | same | — |
| `tongue_out` | 19 (`facs.code.au19`) | `facs_wikipedia` raw line 123 | 19 Tongue show | none beyond the existing "no stated length" | same | each `tongue_out` hop (existing loss) |

| Canonical signals | FACS codes | Difference | Verdict | Owning hop, key |
|---|---|---|---|---|
| `eye_close_left`, `eye_close_right` | 45 Blink (raw line 261), 46 Wink (263); 41 Lid droop (253), 42 Slit (255), 44 Squint (259) | FACS scores blink and wink as events, apart from 43; RCEF carries closure per frame only. The codec reads 45 as two-sided AU43 and L46 or R46 as one-sided AU43, as `examples/face_pipeline.py` lines 142-147 already do. 41, 42 and 44 leave `eye_close` out ([codec](facs-intensity.md#codes-that-are-not-mapped)) | differs | the 4 AU43 hops, `facs_eyelid_events` |
| every sided `facs.code` signal (42) and both AU30 directions | modifiers L and R (raw line 78) | see [Frames](#frames-whose-left) | unresolved | every sided FACS hop and both AU30 hops, `facs_side_frame_unresolved` |
| every mapped `facs.code` signal (49) | intensity letters A-E (raw lines 69-75) | FACS intensity is ordinal, and E is the person's maximum; the canonical value is a declared fraction | differs | every FACS hop, `facs_ordinal_intensity` |
| `jaw_thrust`, `jaw_sideways_*`, `cheek_puff_*`, `cheek_suck_*`, `eye_close_*` | gross behaviour codes 29, 30, 34, 35 and 43 (raw line 224; action descriptors, raw line 65) | the source gives no intensity scale for these codes; 1 is RCEF's assumption | differs | the 18 hops of these codes, `facs_gross_code_no_intensity` |

## FACS crosswalk: ICT-FaceKit

Record `ict_facekit` (ICT-FaceKit `da5f95a`, MIT; README FACS table, lines 154-184). Today's maps cite it on 90 FB2 ↔ ARKit mappings. ICT names only ARKit shapes, so in the pivot routes it goes on ARKit hops only, never on FB2 hops. These are the canonical signals with a FACS code whose ARKit hops cite it. 41 rows: 37 `same`, 4 `differs`.

| Signal | ARKit shape | Locator | ICT FACS unit | Canonical code | Difference | Verdict | Owning hop, key |
|---|---|---|---|---|---|---|---|
| `brow_inner_raise_left` | browInnerUp | `ict_facekit` line 156 | AU1 Inner brow raiser | 1 | none | same | — |
| `brow_inner_raise_right` | browInnerUp | `ict_facekit` line 156 | AU1 Inner brow raiser | 1 | none | same | — |
| `brow_outer_raise_left` | browOuterUpLeft | `ict_facekit` line 157 | AU2 Outer brow raiser | 2 | none | same | — |
| `brow_outer_raise_right` | browOuterUpRight | `ict_facekit` line 157 | AU2 Outer brow raiser | 2 | none | same | — |
| `brow_lower_left` | browDownLeft | `ict_facekit` line 158 | AU4 Brow lowerer | 4 | none | same | — |
| `brow_lower_right` | browDownRight | `ict_facekit` line 158 | AU4 Brow lowerer | 4 | none | same | — |
| `eye_close_left` | eyeBlinkLeft | `ict_facekit` line 180 | AU45 Blink | 43 | ICT relates eyeBlink to AU45 Blink; the canonical code is 43 Eyes closed | differs | ARKit in and out, `ict_au45_blink` |
| `eye_close_right` | eyeBlinkRight | `ict_facekit` line 180 | AU45 Blink | 43 | ICT relates eyeBlink to AU45 Blink; the canonical code is 43 Eyes closed | differs | ARKit in and out, `ict_au45_blink` |
| `lid_tighten_left` | eyeSquintLeft | `ict_facekit` line 161 | AU7 Lid tightener | 7 | none | same | — |
| `lid_tighten_right` | eyeSquintRight | `ict_facekit` line 161 | AU7 Lid tightener | 7 | none | same | — |
| `upper_lid_raise_left` | eyeWideLeft | `ict_facekit` line 160 | AU5 Upper lid raiser | 5 | none | same | — |
| `upper_lid_raise_right` | eyeWideRight | `ict_facekit` line 160 | AU5 Upper lid raiser | 5 | none | same | — |
| `cheek_puff_left` | cheekPuff | `ict_facekit` line 179 | AU33 Cheek blow | 34 | ICT relates cheekPuff to AU33 Cheek blow; the canonical code is 34 [Cheek] puff | differs | ARKit in and out, `ict_au33_cheek_blow` |
| `cheek_puff_right` | cheekPuff | `ict_facekit` line 179 | AU33 Cheek blow | 34 | ICT relates cheekPuff to AU33 Cheek blow; the canonical code is 34 [Cheek] puff | differs | ARKit in and out, `ict_au33_cheek_blow` |
| `cheek_raise_left` | cheekSquintLeft | `ict_facekit` line 159 | AU6 Cheek raiser | 6 | none | same | — |
| `cheek_raise_right` | cheekSquintRight | `ict_facekit` line 159 | AU6 Cheek raiser | 6 | none | same | — |
| `nose_wrinkle_left` | noseSneerLeft | `ict_facekit` line 162 | AU9 Nose Wrinkler | 9 | none | same | — |
| `nose_wrinkle_right` | noseSneerRight | `ict_facekit` line 162 | AU9 Nose Wrinkler | 9 | none | same | — |
| `jaw_thrust` | jawForward | `ict_facekit` line 176 | AU29 Jaw thrust | 29 | none | same | — |
| `lip_corner_pull_left` | mouthSmileLeft | `ict_facekit` line 165 | AU12 Lip corner puller | 12 | none | same | — |
| `lip_corner_pull_right` | mouthSmileRight | `ict_facekit` line 165 | AU12 Lip corner puller | 12 | none | same | — |
| `lip_corner_depress_left` | mouthFrownLeft | `ict_facekit` line 167 | AU15 Lip corner depressor | 15 | none | same | — |
| `lip_corner_depress_right` | mouthFrownRight | `ict_facekit` line 167 | AU15 Lip corner depressor | 15 | none | same | — |
| `dimple_left` | mouthDimpleLeft | `ict_facekit` line 166 | AU14 Dimpler | 14 | none | same | — |
| `dimple_right` | mouthDimpleRight | `ict_facekit` line 166 | AU14 Dimpler | 14 | none | same | — |
| `lip_stretch_left` | mouthStretchLeft | `ict_facekit` line 171 | AU20 Lip stretcher | 20 | none | same | — |
| `lip_stretch_right` | mouthStretchRight | `ict_facekit` line 171 | AU20 Lip stretcher | 20 | none | same | — |
| `lip_funnel_upper_left` | mouthFunnel | `ict_facekit` line 172 | AU22 Lip Funneler | 22 | none | same | — |
| `lip_funnel_upper_right` | mouthFunnel | `ict_facekit` line 172 | AU22 Lip Funneler | 22 | none | same | — |
| `lip_funnel_lower_left` | mouthFunnel | `ict_facekit` line 172 | AU22 Lip Funneler | 22 | none | same | — |
| `lip_funnel_lower_right` | mouthFunnel | `ict_facekit` line 172 | AU22 Lip Funneler | 22 | none | same | — |
| `lip_pucker_left` | mouthPucker | `ict_facekit` line 170 | AU18 Lip Pucker | 18 | none | same | — |
| `lip_pucker_right` | mouthPucker | `ict_facekit` line 170 | AU18 Lip Pucker | 18 | none | same | — |
| `lip_suck_upper_left` | mouthRollUpper | `ict_facekit` line 175 | AU28 Lip Suck | 28 | none | same | — |
| `lip_suck_upper_right` | mouthRollUpper | `ict_facekit` line 175 | AU28 Lip Suck | 28 | none | same | — |
| `lip_suck_lower_left` | mouthRollLower | `ict_facekit` line 175 | AU28 Lip Suck | 28 | none | same | — |
| `lip_suck_lower_right` | mouthRollLower | `ict_facekit` line 175 | AU28 Lip Suck | 28 | none | same | — |
| `lip_press_left` | mouthPressLeft | `ict_facekit` line 173 | AU24 Lip pressor | 24 | none | same | — |
| `lip_press_right` | mouthPressRight | `ict_facekit` line 173 | AU24 Lip pressor | 24 | none | same | — |
| `lower_lip_depress_left` | mouthLowerDownLeft | `ict_facekit` line 168 | AU16 Lower lip depressor | 16 | none | same | — |
| `lower_lip_depress_right` | mouthLowerDownRight | `ict_facekit` line 168 | AU16 Lower lip depressor | 16 | none | same | — |

ICT also relates AU61-64 to the ARKit eye-look shapes (lines 181-184). The gaze signals have no FACS code, so on the 16 ARKit gaze hops ICT is name agreement only: "no FACS transfer claimed; canonical gaze has no FACS code".

## Crosswalk notes

No hop cites these sources for the signals named, so they get no loss key.

- **ICT-FaceKit.** `jaw_drop`: ICT relates jawOpen to AU27 Mouth stretch (line 174); the canonical code is 26. `upper_lip_raise`: ICT relates mouthUpperUp to AU11 Nasolabial deepener (line 164); the canonical code is 10. `chin_raise_upper_lip`: ICT relates mouthShrugUpper to AU10 Upper lip raiser (line 163); the canonical signal has no FACS code. [godot_comparison.md](godot_comparison.md) already records these three. `chin_raise` and `jaw_sideways_*` agree with ICT (AU17, line 169; AU30 left and right, lines 177-178).
- **Py-Feat** (`pyfeat_au_reference`, Py-Feat `docs/pages/au_reference.md` at `4ebb4ec`, MIT; the page calls its ARKit column approximate, line 13). It relates AU10 to mouthUpperUp (line 74), as the canonical set does. It relates both AU23 and AU24 to mouthPress (lines 87-88); the canonical set gives AU23 to `lip_tighten`, which has no ARKit shape. It relates AU25, AU26 and AU27 to jawOpen at different strengths (lines 89-91), and AU43, AU45 and AU46 all to eyeBlink (lines 106, 108 and 109). It relates AU61 to eyeLookInLeft and eyeLookOutRight, but its muscle column for AU61 describes a gaze toward the subject's own left (line 118), and the two columns disagree.
- **Melinda Ozel, "ARKit to FACS"** (`ozel_arkit_facs`, reference only; paraphrased). Its eyeBlink entry gives AU45. Its jawOpen entry allows AU26 or AU27. Its mouthShrugUpper entry treats the shape as the upper part of AU17 that depends on mouthShrugLower, and says that ICT's AU10 reading is a mistake. This supports `chin_raise_upper_lip` as a part of chin raising. Its eye-look note pairs eyeLookInRight with eyeLookOutLeft for a leftward gaze.

## Reason scan

- Every `mapped` provider signal's `metadata.reason` was scanned for "unresolved", "conflict", "contradict", "while", "differs" and "unclear". Only Unified Expressions `MouthLowerDownLeft` and `MouthLowerDownRight` match (`profiles/vrcft.artist.base.toml` lines 1009 and 1025). Their rows are `unresolved`.
- Today's assumptions marked "FLAGGED" are the VRM side (catalogue a26) and the Godot-only mouthLeft and mouthRight names (a24, a29, a30). The VRM side is an `unresolved` row. The mouth names concern which output gets a value, not a frame; the ARKit and FB2 frame rows settle the direction.
- New in this audit: Apple's abstract for `mouthStretchRight` describes rightward movement of the left corner of the mouth. The name and RCEF's profile say right. The row is `unresolved`.

## Loss keys

| Key | Verdict | Owning hops | Loss text |
|---|---|---|---|
| `fb2_gaze_rotation` | differs | FB2 gaze in and out | source describes eye rotation, linear in angle; the canonical value claims no curve |
| `fb2_gaze_max_angle_unspecified` | differs | FB2 gaze in and out | FB2 maximum gaze angle is unspecified |
| `fb2_gaze_exclusive` | differs | FB2 gaze in and out | FB2 opposing directions are mutually exclusive; the canonical set states no such constraint |
| `arkit_gaze_eyelid` | differs | ARKit gaze in and out | source describes eyelid movement consistent with the gaze |
| `vrcft_ue_gaze_no_angle` | differs | Unified Expressions gaze out | source describes eye movement in a direction; no maximum angle stated |
| `arkit_browdown_outer` | differs | ARKit face in and out | ARKit describes the outer part of the brow; the canonical signal is the whole brow lowering |
| `arkit_eyesquint_face` | differs | ARKit face in and out | ARKit describes contraction of the face around the eye; the canonical signal is the lids only |
| `arkit_cheeksquint_cheek` | differs | ARKit face in and out | ARKit describes the cheek moving up around and below the eye; the canonical signal is the tightening of the ring around the eye |
| `arkit_mouthpress_lower_lip` | differs | ARKit face in and out | ARKit describes upward compression of the lower lip; the canonical signal presses both lips together |
| `arkit_mouthsmile_upward` | differs | ARKit face in and out | ARKit describes upward movement only; the canonical signal also draws the corner back and outward |
| `arkit_mouthshrug_outward` | differs | ARKit face in and out; ARKit `chin_raise_upper_lip` in and out | ARKit describes outward lip movement; the canonical signals push up |
| `arkit_mouthpucker_compression` | differs | ARKit face in and out | ARKit describes contraction and compression of the closed lips; the canonical signal pushes the lips forward |
| `arkit_mouthstretchright_text_side` | unresolved | ARKit face in and out | Apple's abstract for mouthStretchRight names the left corner; the side is taken from the name |
| `arkit_mouthclose_jaw_unresolved` | unresolved | ARKit face in and out | ARKit mouthClose: the jaw relation is unresolved; Apple's abstract and RCEF's own calibration record conflict |
| `ict_au33_cheek_blow` | differs | ARKit `cheek_puff` in and out | ICT relates cheekPuff to AU33 cheek blow; the canonical code is AU34; the ICT crosswalk does not carry over for the FACS code |
| `ict_au45_blink` | differs | ARKit blink in and out | ICT relates eyeBlink to AU45 blink; the canonical code is AU43; the ICT crosswalk does not carry over for the FACS code |
| `vrcft_ue_set_equal` | differs | Unified Expressions out, 16 mappings: brow 4, mouth shift 4, corner 4, pucker 4 | Unified Expressions splits this shape into parts whose ratio the canonical set does not record; the parts are set equal |
| `vrcft_ue_eyesquint_socket` | differs | Unified Expressions face out | Unified Expressions describes the muscles of the eye socket; the canonical signal is the lids only |
| `vrcft_ue_cheeksquint_cheek` | differs | Unified Expressions face out | Unified Expressions describes a cheek raise; the canonical signal is the tightening of the ring around the eye |
| `vrcft_ue_mouthclosed_jaw_relative` | differs | Unified Expressions face out | Unified Expressions defines MouthClosed relative to JawOpen; the canonical signal is defined at any jaw opening |
| `vrcft_ue_mouthlowerdown_direction_unresolved` | unresolved | Unified Expressions face out | provider direction unresolved (native name versus artist wording) |
| `vrcft_eye_openness_endpoint` | differs | VRCFaceTracking eye blink in and out | eye_close is 1 − Openness. Openness 1 is taken as eye_close 0 (relaxed open lids); VRCFaceTracking does not state that 1 is neutral; Openness outside [0,1] gives an output outside [0,1] and is refused |
| `vrm_blink_side_unresolved` | unresolved | VRM blink in and out | VRM gives no normative side; RCEF reads blinkLeft as the subject's own left |
| `vrm_vowel_asset_weight` | differs | VRM vowel in and out | in: asset-authored weights treated as probabilities; no sum constraint (aa = 1 and oh = 1 give a sum of 2); sil not provided. Out: a viseme probability becomes an asset-authored expression weight |
| `vrm_ih_vowel_quality` | differs | VRM vowel in and out (`ih`) | vowel quality differs: META IH is the vowel in "tip", VRM ih is remarked "i" |
| `facs_ordinal_intensity` | differs | every FACS hop (102) | FACS intensity is ordinal (letters A-E, E the person's maximum); the numeric value is an RCEF encoding; equal steps are not claimed; no gain is measured |
| `facs_side_frame_unresolved` | unresolved | every sided FACS hop and both AU30 hops | FACS names L and R without saying whose side; RCEF reads them as the subject's own |
| `facs_au30_direction_unresolved` | unresolved | FACS AU30 in and out | FACS L30 and R30 are read as directions toward the subject's own left and right; the source does not say whose left |
| `facs_au17_no_split` | differs | FACS AU17 in and out | FACS AU17 is the whole chin raise; the induced upper-lip push is not written from FACS and is dropped toward FACS |
| `facs_mouth_opening_split` | differs | FACS AU26 in and out | from FACS, 27 is read as 26 and 25 is not read; toward FACS all opening is written as 26 |
| `facs_eyelid_events` | differs | FACS AU43 in and out | FACS blink and wink are events apart from 43; from FACS, 45 and 46 are read as 43; toward FACS all closure is written as 43 |
| `facs_gross_code_no_intensity` | differs | the 18 FACS hops of 29, 30, 34, 35 and 43 | the source gives no intensity scale for gross behaviour codes; 1 is RCEF's assumption |

Hops also carry losses that are not audit verdicts: the gain loss of each hop, "asymmetry unknown: symmetry is invented" (ARKit in-hop fan-outs, FACS AU22 and AU28 in-hop fan-outs), "asymmetry irrecoverable" (ARKit and FACS out-hop means), "only their difference is kept" and the rounding loss (FB2 gaze out-hop), "no stated length" (every `tongue_out` hop) and the other VRM losses (consonants dropped, `isBinary`, `blink` not set or not read).

## Mapping today's losses to keys

Each loss reason of today's maps maps to the keys that cover it on the pivot route of the same rule. The table is keyed on the rule and the reason, not on the reason alone. Today's 7 direct maps hold 21 distinct reasons. A 22nd, "No geometry evaluated by scalar fixture.", is only in `mappings/fixtures.toml` and is out of scope.

| A1 loss reason | A1 rules | Keys on the pivot route |
|---|---:|---|
| provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | 180 | the gain loss of each of the two hops |
| Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal | 28 | 16 rules (BrowLowerer and BrowPinch, MouthUpper and MouthLower, MouthCornerPull and MouthCornerSlant, LipPucker upper and lower): `vrcft_ue_set_equal`. 12 rules (BrowInnerUp, CheekPuff, LipFunnel, LipSuck): the ARKit in-hop's "asymmetry unknown: symmetry is invented" |
| FB2 maximum gaze angle is unspecified | 16 | `fb2_gaze_max_angle_unspecified` |
| asymmetry unknown: symmetry is invented | 14 | the ARKit in-hop's fan-out loss |
| FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | 12 | the FB2 gaze out-hop's "only their difference is kept" |
| ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation | 8 | `arkit_gaze_eyelid` and `fb2_gaze_rotation` |
| FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze | 8 | `fb2_gaze_rotation` and `arkit_gaze_eyelid` |
| FB2 opposing directions are mutually exclusive; ARKit states no such constraint | 8 | `fb2_gaze_exclusive` on the FB2 gaze out-hop |
| ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | 8 | `arkit_gaze_eyelid` and `vrcft_ue_gaze_no_angle` |
| asymmetry irrecoverable | 6 | the ARKit out-hop's mean loss |
| consonant visemes are dropped, so outputs no longer sum to 1 | 5 | the VRM vowel out-hop's consonant loss |
| a viseme probability becomes an asset-authored expression weight | 5 | `vrm_vowel_asset_weight` |
| both are extension shapes with no stated length | 3 | "no stated length" on each `tongue_out` hop |
| FB2 also pulls the corner back and laterally; ARKit describes upward movement only | 2 | `arkit_mouthsmile_upward` |
| an FB2 weight becomes an asset-authored expression weight | 2 | the VRM blink out-hop's weight loss |
| VRM blink (both eyes) is left unset, so a model that binds only blink, not blinkLeft and blinkRight, does not blink | 2 | the VRM blink out-hop's `blink` loss |
| a model may mark the preset isBinary, which turns a partial closure into fully open or fully closed | 2 | the VRM blink out-hop's `isBinary` loss |
| jaw-relative versus jaw-independent lip closure | 1 | `arkit_mouthclose_jaw_unresolved` on the ARKit out-hop |
| FB2 describes upward lip motion induced by the chin raiser; ARKit describes outward upper-lip movement | 1 | `arkit_mouthshrug_outward` |
| FB2 describes upward chin and lower-lip motion; ARKit describes outward lower-lip movement | 1 | `arkit_mouthshrug_outward` |
| vowel quality differs: META IH is the vowel in "tip", VRM ih is remarked "i" | 1 | `vrm_ih_vowel_quality` |

## Keys added on today's pairs

A pivot route may carry an audit key that today's rule for the same pair does not carry. Each such key is listed here. Any other added key is an error.

| Key | Pairs where it is added |
|---|---|
| `arkit_browdown_outer`, `arkit_eyesquint_face`, `arkit_cheeksquint_cheek`, `arkit_mouthpress_lower_lip`, `arkit_mouthpucker_compression`, `arkit_mouthstretchright_text_side`, `ict_au33_cheek_blow`, `ict_au45_blink` | FB2 → ARKit, ARKit → FB2, ARKit → Unified Expressions |
| `arkit_mouthsmile_upward`, `arkit_mouthshrug_outward` | ARKit → FB2, ARKit → Unified Expressions |
| `arkit_mouthclose_jaw_unresolved` | ARKit → FB2, ARKit → Unified Expressions (on FB2 → ARKit it covers today's jaw loss) |
| `vrcft_ue_eyesquint_socket`, `vrcft_ue_cheeksquint_cheek`, `vrcft_ue_mouthclosed_jaw_relative`, `vrcft_ue_mouthlowerdown_direction_unresolved` | ARKit → Unified Expressions |
| `fb2_gaze_exclusive` | FB2 → ARKit (on ARKit → FB2 it covers today's exclusivity loss) |
| `vrm_blink_side_unresolved` | FB2 → VRM blink (today an assumption only) |

## Corrections to today's losses

A correction would need a public citation and a CHANGELOG line. The list is empty. Today's FB2 → ARKit `mouthClose` jaw loss is covered by the `unresolved` ARKit key.

## Assumption catalogue

Today's 7 direct maps hold 191 rules: 187 mappings and the 4 internal gaze steps. Together they carry **589 assumption strings**, 216 of them distinct. With provider names replaced by placeholders, the strings fall into **35 templates**.

How the templates were made: each string was taken from `mappings/arkit_fb2.toml`, `fb2_arkit.toml`, `arkit_vrcft.toml`, `fb2_vrm.toml` and `visemes_vrm.toml` at commit `dea1713`. In each string, every ARKit, FB2, Unified Expressions and VRM signal name was replaced by `<ARKit>`, `<FB2>`, `<UE>` or `<VRM>`, a META viseme name by `<META>`, a quoted phrase by `<q>`, a decimal weight by `<w>`, "left" or "right" by `<side>`, and a list of names by one placeholder with "…".

The catalogue is keyed on (A1 rule, template). For each entry, the pivot route holds the hop assumption key in the last column, or the entry is superseded by the canonical definition, with the cited section or rows. "Linear in between" is not superseded: it maps to the operator clause of each hop ([Meaning of 0, 1 and neutral](canonical-set.md#meaning-of-0-1-and-neutral)). 178 entries are superseded (a02, a04, a06 and 12 rules of a10). The other 411 map to a hop key.

| ID | Template | Strings | A1 rules | Home in the pivot routes |
|---|---|---:|---|---|
| a01 | `ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.` | 68 | every rule of `arkit.to_vrcft_artist` (68) | `endpoints` on the ARKit in-hop and the Unified Expressions out-hop. The operator clause is "carried over unchanged" on the 1:1 copies, "copied into each Unified Expressions part" on the 16 `vrcft_ue_set_equal` rules, and "copied into each part" where the ARKit in-hop fans out |
| a02 | `Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).` | 62 | `arkit.to_vrcft_artist` (62): every rule except `arkit_vrcft_artist.JawForward`, `arkit_vrcft_artist.JawOpen`, `arkit_vrcft_artist.MouthClosed`, `arkit_vrcft_artist.MouthRaiserLower`, `arkit_vrcft_artist.MouthRaiserUpper`, `arkit_vrcft_artist.TongueOut` | Superseded by the canonical `side` field ([Fields](canonical-set.md#fields)), with the frame rows ARKit `same` and Unified Expressions `same` ([Frames](#frames-whose-left)) |
| a03 | `ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.` | 60 | every rule of `arkit.to_fb2` (52); `arkit_gaze.to_fb2` (8): every rule except `arkit_fb2.gaze_in_minus_out_L`, `arkit_fb2.gaze_up_minus_down_L`, `arkit_fb2.gaze_in_minus_out_R`, `arkit_fb2.gaze_up_minus_down_R` | `endpoints` on the ARKit in-hop and the FB2 out-hop; on the 8 gaze splits the clause is the netting clause |
| a04 | `Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes <q>).` | 58 | `arkit.to_fb2` (46): every rule except `arkit_fb2.JAW_THRUST`, `arkit_fb2.JAW_DROP`, `arkit_fb2.LIPS_TOWARD`, `arkit_fb2.CHIN_RAISER_B`, `arkit_fb2.CHIN_RAISER_T`, `arkit_fb2.TONGUE_OUT`; every rule of `arkit_gaze.to_fb2` (12) | Superseded by the canonical `side` field ([Fields](canonical-set.md#fields)), with the frame rows ARKit `same` and FB2 `same` ([Frames](#frames-whose-left)) |
| a05 | `FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.` | 52 | every rule of `fb2.to_arkit` (44); every rule of `fb2_gaze.to_arkit` (8) | `endpoints` on the FB2 in-hop and the ARKit out-hop; on the 6 means the clause is "the ARKit value is the mean of the canonical parts" |
| a06 | `Both providers name sides from the subject's own face (FB2 describes <q>; ARKit coefficients are face-relative).` | 46 | `fb2.to_arkit` (38): every rule except `fb2_arkit.jawOpen`, `fb2_arkit.mouthClose`, `fb2_arkit.mouthShrugUpper`, `fb2_arkit.mouthShrugLower`, `fb2_arkit.jawForward`, `fb2_arkit.tongueOut`; every rule of `fb2_gaze.to_arkit` (8) | Superseded by the canonical `side` field ([Fields](canonical-set.md#fields)), with the frame rows FB2 `same` and ARKit `same` ([Frames](#frames-whose-left)) |
| a07 | `FB2 <FB2> corresponds to ARKit <ARKit>.` | 46 | `fb2.to_arkit` (38): every rule except `fb2_arkit.browInnerUp`, `fb2_arkit.cheekPuff`, `fb2_arkit.mouthFunnel`, `fb2_arkit.mouthPucker`, `fb2_arkit.mouthRollLower`, `fb2_arkit.mouthRollUpper`; every rule of `fb2_gaze.to_arkit` (8) | `correspondence` on the FB2 in-hop and the ARKit out-hop, with `transfer.provider` for the crosswalk records the rule cites; withdrawn, with the loss, where the ARKit row is `differs` or `unresolved` |
| a08 | `ARKit <ARKit> corresponds to Unified Expressions <UE> (VRCFaceTracking ARKit table; Godot face-modifier name table).` | 40 | `arkit.to_vrcft_artist` (40): every rule except the 28 rules of a10, a13 and a21 | `transfer.provider` on the Unified Expressions out-hop (P = ARKit), and `correspondence` on the ARKit in-hop. Withdrawn, with the loss, where the ARKit row is `differs` or `unresolved`: `lid_tighten`, `cheek_raise`, `lip_press`, `chin_raise`, `chin_raise_upper_lip`, `lips_toward`, `lip_stretch_right` and the 8 gaze signals; and for `lower_lip_depress`, whose Unified Expressions row is `unresolved` |
| a09 | `ARKit <ARKit> corresponds to FB2 <FB2>; this is the FB2 -> ARKit rule read back.` | 38 | `arkit.to_fb2` (38): every rule except the 14 rules of a11 | `correspondence` on the ARKit in-hop and the FB2 out-hop. "Read back" holds by construction: both directions pass through the same canonical signal |
| a10 | `ARKit <ARKit> is a blended Unified Expressions shape; <UE> is set to the ARKit value, as is <UE…>. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.` | 16 | `arkit.to_vrcft_artist` (16): `arkit_vrcft_artist.BrowInnerUpRight`, `arkit_vrcft_artist.BrowInnerUpLeft`, `arkit_vrcft_artist.CheekPuffRight`, `arkit_vrcft_artist.CheekPuffLeft`, `arkit_vrcft_artist.LipFunnelUpperRight`, `arkit_vrcft_artist.LipFunnelUpperLeft`, `arkit_vrcft_artist.LipFunnelLowerRight`, `arkit_vrcft_artist.LipFunnelLowerLeft`, `arkit_vrcft_artist.LipPuckerUpperRight`, `arkit_vrcft_artist.LipPuckerUpperLeft`, `arkit_vrcft_artist.LipPuckerLowerRight`, `arkit_vrcft_artist.LipPuckerLowerLeft`, `arkit_vrcft_artist.LipSuckLowerRight`, `arkit_vrcft_artist.LipSuckLowerLeft`, `arkit_vrcft_artist.LipSuckUpperRight`, `arkit_vrcft_artist.LipSuckUpperLeft` | 12 rules (BrowInnerUp, CheekPuff, LipFunnel, LipSuck): superseded by the canonical split. The canonical set holds these parts, so the out-hop is a 1:1 copy (Unified Expressions rows `same`), and the copy into each part moves to the ARKit in-hop (`endpoints`, fan-out clause). 4 rules (LipPucker): `fan_out.vrcft_ue`, with the mean rationale kept; their ARKit transfer is withdrawn with `arkit_mouthpucker_compression` |
| a11 | `ARKit <ARKit> is one coefficient; FB2 <FB2> is set to it, as are <FB2…>, so that FB2 -> ARKit gives <ARKit> back. How the coefficient divides between the FB2 parts is unknown.` | 14 | `arkit.to_fb2` (14): `arkit_fb2.INNER_BROW_RAISER_L`, `arkit_fb2.INNER_BROW_RAISER_R`, `arkit_fb2.CHEEK_PUFF_L`, `arkit_fb2.CHEEK_PUFF_R`, `arkit_fb2.LIP_FUNNELER_LB`, `arkit_fb2.LIP_FUNNELER_LT`, `arkit_fb2.LIP_FUNNELER_RB`, `arkit_fb2.LIP_FUNNELER_RT`, `arkit_fb2.LIP_PUCKER_L`, `arkit_fb2.LIP_PUCKER_R`, `arkit_fb2.LIP_SUCK_LB`, `arkit_fb2.LIP_SUCK_RB`, `arkit_fb2.LIP_SUCK_LT`, `arkit_fb2.LIP_SUCK_RT` | `endpoints` on the ARKit in-hop, fan-out clause ("the one ARKit value is copied into each part"), with the loss "asymmetry unknown: symmetry is invented" |
| a12 | `A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.` | 8 | `arkit_gaze.to_fb2` (8): every rule except `arkit_fb2.gaze_in_minus_out_L`, `arkit_fb2.gaze_up_minus_down_L`, `arkit_fb2.gaze_in_minus_out_R`, `arkit_fb2.gaze_up_minus_down_R` | `net.fb2_gaze` on the FB2 gaze out-hop |
| a13 | `ARKit <ARKit> is a blended Unified Expressions shape; <UE> is set to the ARKit value, as is <UE…>. VRCFaceTracking defines the blended shape as <w> x <UE> + <w> x <UE>; the weights sum to 1, so copying the ARKit value into both parts gives it back.` | 8 | `arkit.to_vrcft_artist` (8): `arkit_vrcft_artist.BrowLowererLeft`, `arkit_vrcft_artist.BrowPinchLeft`, `arkit_vrcft_artist.BrowLowererRight`, `arkit_vrcft_artist.BrowPinchRight`, `arkit_vrcft_artist.MouthCornerPullLeft`, `arkit_vrcft_artist.MouthCornerSlantLeft`, `arkit_vrcft_artist.MouthCornerPullRight`, `arkit_vrcft_artist.MouthCornerSlantRight` | `fan_out.vrcft_ue` on the Unified Expressions out-hop, with the blend weights kept as the rationale; the ARKit transfer is withdrawn with `arkit_browdown_outer` (brow) and `arkit_mouthsmile_upward` (corner) |
| a14 | `VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled <FB2>, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.` | 8 | `arkit.to_fb2` (4): `arkit_fb2.LID_TIGHTENER_L`, `arkit_fb2.LID_TIGHTENER_R`, `arkit_fb2.UPPER_LID_RAISER_L`, `arkit_fb2.UPPER_LID_RAISER_R`; `fb2.to_arkit` (4): `fb2_arkit.eyeSquintLeft`, `fb2_arkit.eyeSquintRight`, `fb2_arkit.eyeWideLeft`, `fb2_arkit.eyeWideRight` | `evidence.vrcft_tables_not_cited` on the FB2 in-hop and out-hop of the same FB2 signal |
| a15 | `VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.` | 7 | every rule of `fb2.to_vrm` (2); every rule of `visemes.to_vrm` (5) | `vrm.downstream_effects` on `rcef_blink.to_vrm` and `rcef_viseme_vowel.to_vrm` |
| a16 | `META viseme <META> corresponds to VRM preset <VRM> (META <q> as in <w>; VRM remark <q>).` | 5 | every rule of `visemes.to_vrm` (5) | `correspondence` on the META in-hop and the VRM vowel out-hop |
| a17 | `META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).` | 5 | every rule of `visemes.to_vrm` (5) | `vrm.probability_as_weight` on the VRM vowel out-hop |
| a18 | `Phoneme-label correspondence only; no published table maps META visemes to VRM presets.` | 5 | every rule of `visemes.to_vrm` (5) | `vrm.phoneme_label_only` on the VRM vowel out-hop |
| a19 | `ARKit <ARKit> corresponds to FB2 <FB2>; this is the FB2 -> ARKit rule read back, taking <ARKit> minus <ARKit> where it is above zero.` | 4 | `arkit_gaze.to_fb2` (4): `arkit_fb2.EYES_LOOK_RIGHT_L`, `arkit_fb2.EYES_LOOK_UP_L`, `arkit_fb2.EYES_LOOK_LEFT_R`, `arkit_fb2.EYES_LOOK_UP_R` | `net.fb2_gaze` and `correspondence` (FB2 gaze names, [Gaze](canonical-set.md#gaze)) on the FB2 gaze out-hop, positive segment |
| a20 | `ARKit <ARKit> corresponds to FB2 <FB2>; this is the FB2 -> ARKit rule read back, taking how far <ARKit> minus <ARKit> is below zero.` | 4 | `arkit_gaze.to_fb2` (4): `arkit_fb2.EYES_LOOK_LEFT_L`, `arkit_fb2.EYES_LOOK_DOWN_L`, `arkit_fb2.EYES_LOOK_RIGHT_R`, `arkit_fb2.EYES_LOOK_DOWN_R` | `net.fb2_gaze` and `correspondence` on the FB2 gaze out-hop, negative segment |
| a21 | `ARKit <ARKit> is a blended Unified Expressions shape; <UE> is set to the ARKit value, as is <UE…>. Godot builds the blended shape from these two parts; VRCFaceTracking pairs FB2 <FB2> with the blended shape.` | 4 | `arkit.to_vrcft_artist` (4): `arkit_vrcft_artist.MouthUpperLeft`, `arkit_vrcft_artist.MouthLowerLeft`, `arkit_vrcft_artist.MouthUpperRight`, `arkit_vrcft_artist.MouthLowerRight` | `fan_out.vrcft_ue` on the Unified Expressions out-hop |
| a22 | `ARKit <ARKit…> are opposing directions of one eye; their difference, from -1 to 1, carries both.` | 4 | `arkit_gaze.to_fb2` (4): `arkit_fb2.gaze_in_minus_out_L`, `arkit_fb2.gaze_up_minus_down_L`, `arkit_fb2.gaze_in_minus_out_R`, `arkit_fb2.gaze_up_minus_down_R` | `net.fb2_gaze` on the FB2 gaze out-hop (the 4 helper values `rcef.intermediate.gaze_in_minus_out_*` and `gaze_up_minus_down_*`) |
| a23 | `FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).` | 4 | `arkit_gaze.to_fb2` (4): `arkit_fb2.gaze_in_minus_out_L`, `arkit_fb2.gaze_up_minus_down_L`, `arkit_fb2.gaze_in_minus_out_R`, `arkit_fb2.gaze_up_minus_down_R` | `gaze.fb2_exclusive` on the FB2 gaze out-hop |
| a24 | `FLAGGED: VRCFaceTracking's ARKit table has no <ARKit> row; only Godot names the ARKit coefficient for the blended Unified shape.` | 4 | `arkit.to_vrcft_artist` (4): `arkit_vrcft_artist.MouthUpperLeft`, `arkit_vrcft_artist.MouthLowerLeft`, `arkit_vrcft_artist.MouthUpperRight`, `arkit_vrcft_artist.MouthLowerRight` | `evidence.godot_only_mouth_shift` on the Unified Expressions out-hop for `mouth_shift_*` |
| a25 | `ARKit <ARKit> is one coefficient; it is the mean of FB2 <FB2…>, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.` | 3 | `fb2.to_arkit` (3): `fb2_arkit.mouthPucker`, `fb2_arkit.mouthRollLower`, `fb2_arkit.mouthRollUpper` | `mean.arkit` on the ARKit out-hop, with the implementer agreement kept |
| a26 | `Both name sides from the subject's own face. FLAGGED: VRM gives no normative side; on the VRM 1.0 Twist sample <VRM> moves the avatar's own <side> eyelid.` | 2 | every rule of `fb2.to_vrm` (2) | `vrm.side_caveat` (the A1 text kept) on both VRM blink hops, with the audit key `vrm_blink_side_unresolved` |
| a27 | `FB2 <FB2> (lowers the top eyelid of the <side> eye) corresponds to VRM preset <VRM> (closes the <side> eyelid); definitional only: the definitions agree, but no published table maps FB2 to VRM.` | 2 | every rule of `fb2.to_vrm` (2) | `correspondence` on the FB2 blink in-hop and the VRM blink out-hop, and `vrm.definitional_only` on the VRM blink out-hop |
| a28 | `FB2 weight (0 to 1) is used directly as the VRM expression weight (0 to 1).` | 2 | every rule of `fb2.to_vrm` (2) | `endpoints` on the VRM blink out-hop |
| a29 | `FLAGGED: only Godot names ARKit <ARKit> for this channel (its face-modifier alias); VRCFaceTracking pairs the FB2 channel with Unified <UE>, and the FB2 and Apple definitions agree.` | 2 | `fb2.to_arkit` (2): `fb2_arkit.mouthLeft`, `fb2_arkit.mouthRight` | `evidence.godot_only_mouth_shift` on the FB2 in-hop and the ARKit out-hop; the "definitions agree" part is the `mouth_shift_*` rows, FB2 `same` and ARKit `same` |
| a30 | `FLAGGED: only Godot names ARKit <ARKit> for this channel; see fb2_arkit.<ARKit>.` | 2 | `arkit.to_fb2` (2): `arkit_fb2.MOUTH_LEFT`, `arkit_fb2.MOUTH_RIGHT` | `evidence.godot_only_mouth_shift` on the ARKit in-hop and the FB2 out-hop |
| a31 | `VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled <FB2>, a misspelling (not counted: typo), and without that row its ARKit table does not reach FB2.` | 2 | `arkit.to_fb2` (1): `arkit_fb2.LOWER_LIP_DEPRESSOR_L`; `fb2.to_arkit` (1): `fb2_arkit.mouthLowerDownLeft` | As a14 |
| a32 | `ARKit <ARKit> is one coefficient for both sides; it is the mean of FB2 <FB2…>, as VRCFaceTracking computes <UE>; Godot has no combined inner-brow shape.` | 1 | `fb2.to_arkit` (1): `fb2_arkit.browInnerUp` | `mean.arkit` on the ARKit out-hop |
| a33 | `ARKit <ARKit> is one coefficient for both sides; it is the mean of FB2 <FB2…>, as the Godot OpenXR vendors plugin computes <UE>.` | 1 | `fb2.to_arkit` (1): `fb2_arkit.cheekPuff` | `mean.arkit` on the ARKit out-hop |
| a34 | `ARKit <ARKit> is one coefficient; it is the mean of the four quarters of FB2 <FB2…>, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.` | 1 | `fb2.to_arkit` (1): `fb2_arkit.mouthFunnel` | `mean.arkit` on the ARKit out-hop |
| a35 | `FB2 closes the lips regardless of the jaw position; Unified Expressions defines <UE> relative to <UE> and SRanipal requires Jaw_Open to be inactive. The value is copied without compensating for the jaw.` | 1 | `fb2.to_arkit` (1): `fb2_arkit.mouthClose` | `lips_toward.jaw_not_compensated` on the ARKit out-hop, citing the `lips_toward` definition and its rows: FB2 `same`, ARKit `unresolved`, Unified Expressions `differs` |

**Hop assumption keys:**

| Key | Text on the hop |
|---|---|
| `endpoints` | the opening assumption and the operator clause ([Meaning of 0, 1 and neutral](canonical-set.md#meaning-of-0-1-and-neutral)) |
| `correspondence` | "provider name X corresponds to canonical `<short_name>`", from `aligned_names` |
| `transfer.provider` | "correspondence evidence is P↔provider; it carries over because `<short_name>` is defined to match P `<name>`" |
| `fan_out.vrcft_ue` | why the parts are set equal, with the blend rule the source gives |
| `net.fb2_gaze` | the FB2 gaze netting: the difference of each opposing pair is split back into two one-sided values, each exactly zero on its flat side |
| `gaze.fb2_exclusive` | FB2 says only one of two opposing gaze directions is non-zero at a time (`xr_fb2` 648-649) |
| `mean.arkit` | the ARKit value is the mean of the canonical parts, and which implementers compute it the same way |
| `evidence.vrcft_tables_not_cited` | why VRCFaceTracking's comparison tables are not cited on this FB2 hop |
| `evidence.godot_only_mouth_shift` | only Godot names the ARKit coefficient for this mouth shift |
| `vrm.downstream_effects` | VRM `isBinary` and override effects happen downstream and are not modelled |
| `vrm.probability_as_weight` | a viseme probability is used directly as the VRM expression weight |
| `vrm.phoneme_label_only` | phoneme-label correspondence only; no published table maps META visemes to VRM presets |
| `vrm.side_caveat` | the A1 text: VRM gives no normative side; on the VRM 1.0 Twist sample `blinkLeft` moves the avatar's own left eyelid |
| `vrm.definitional_only` | the definitions agree, but no published table maps FB2 to VRM |
| `lips_toward.jaw_not_compensated` | the value is copied without compensating for the jaw |

## Summary

| Rows | same | differs | unresolved | Total |
|---|---:|---:|---:|---:|
| FB2 | 62 | 8 | 0 | 70 |
| ARKit | 36 | 22 | 2 | 60 |
| Unified Expressions | 41 | 21 | 2 | 64 |
| VRCFaceTracking eye | 2 | 2 | 0 | 4 |
| VRM | 0 | 5 | 2 | 7 |
| META visemes | 15 | 0 | 0 | 15 |
| FACS signal rows | 49 | 2 | 2 | 53 |
| FACS encoding and frame rows | 0 | 3 | 1 | 4 |
| ICT-FaceKit crosswalk | 37 | 4 | 0 | 41 |
| Frames | 4 | 0 | 2 | 6 |
| **All** | 246 | 67 | 11 | 324 |
