<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `rcef_viseme.to_rcef_expression`

The viseme pose bridge: one map from the canonical viseme set (`rcef.canonical_viseme`) to the canonical expression set (`rcef.canonical_expression`).

- Mappings: 101, in 7 parts.
- Evidence status of its mappings: proposed (101).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_visemeto_rcef_expression).

Its mapping IDs keep the prefix `rcef_viseme_pose.` by design: a mapping ID never changes when its map is renamed ([docs/retired-ids.csv](../retired-ids.csv) gives the old map ID).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `viseme_vowel` | 5 of 5 | 5 | copy (affine 1, 0) (5) | proposed (5) |
| `viseme_consonant` | 5 of 9 | 5 | copy (affine 1, 0) (5) | proposed (5) |
| `viseme_rest` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `face` | 41 of 41 | 82 | weighted_sum of 11 (41), piecewise_linear (0, 0) (1, 1) (11, 1) (41) | proposed (82) |
| `cheek_puff` | 2 of 2 | 4 | weighted_sum of 11 (2), piecewise_linear (0, 0) (1, 1) (11, 1) (2) | proposed (4) |
| `jaw_thrust` | 1 of 1 | 2 | weighted_sum of 11, piecewise_linear (0, 0) (1, 1) (11, 1) | proposed (2) |
| `chin_raise_upper_lip` | 1 of 1 | 2 | weighted_sum of 11, piecewise_linear (0, 0) (1, 1) (11, 1) | proposed (2) |

## Mappings by part

- `viseme_vowel`: `rcef_viseme_pose.vowel_open`, `rcef_viseme_pose.vowel_mid_spread`, `rcef_viseme_pose.vowel_close_spread`, `rcef_viseme_pose.vowel_mid_rounded`, `rcef_viseme_pose.vowel_close_rounded`.
- `viseme_consonant`: `rcef_viseme_pose.bilabial`, `rcef_viseme_pose.dental`, `rcef_viseme_pose.alveolar_sibilant`, `rcef_viseme_pose.coronal_stop`, `rcef_viseme_pose.dorsal`.
- `viseme_rest`: `rcef_viseme_pose.sil`.
- `face`: `rcef_viseme_pose.brow_inner_raise_left_sum`, `rcef_viseme_pose.brow_inner_raise_left`, `rcef_viseme_pose.brow_inner_raise_right_sum`, `rcef_viseme_pose.brow_inner_raise_right`, `rcef_viseme_pose.brow_outer_raise_left_sum`, `rcef_viseme_pose.brow_outer_raise_left`, `rcef_viseme_pose.brow_outer_raise_right_sum`, `rcef_viseme_pose.brow_outer_raise_right`, `rcef_viseme_pose.brow_lower_left_sum`, `rcef_viseme_pose.brow_lower_left`, `rcef_viseme_pose.brow_lower_right_sum`, `rcef_viseme_pose.brow_lower_right`, `rcef_viseme_pose.lid_tighten_left_sum`, `rcef_viseme_pose.lid_tighten_left`, `rcef_viseme_pose.lid_tighten_right_sum`, `rcef_viseme_pose.lid_tighten_right`, `rcef_viseme_pose.upper_lid_raise_left_sum`, `rcef_viseme_pose.upper_lid_raise_left`, `rcef_viseme_pose.upper_lid_raise_right_sum`, `rcef_viseme_pose.upper_lid_raise_right`, `rcef_viseme_pose.cheek_raise_left_sum`, `rcef_viseme_pose.cheek_raise_left`, `rcef_viseme_pose.cheek_raise_right_sum`, `rcef_viseme_pose.cheek_raise_right`, `rcef_viseme_pose.nose_wrinkle_left_sum`, `rcef_viseme_pose.nose_wrinkle_left`, `rcef_viseme_pose.nose_wrinkle_right_sum`, `rcef_viseme_pose.nose_wrinkle_right`, `rcef_viseme_pose.jaw_drop_sum`, `rcef_viseme_pose.jaw_drop`, `rcef_viseme_pose.lip_corner_pull_left_sum`, `rcef_viseme_pose.lip_corner_pull_left`, `rcef_viseme_pose.lip_corner_pull_right_sum`, `rcef_viseme_pose.lip_corner_pull_right`, `rcef_viseme_pose.lip_corner_depress_left_sum`, `rcef_viseme_pose.lip_corner_depress_left`, `rcef_viseme_pose.lip_corner_depress_right_sum`, `rcef_viseme_pose.lip_corner_depress_right`, `rcef_viseme_pose.dimple_left_sum`, `rcef_viseme_pose.dimple_left`, `rcef_viseme_pose.dimple_right_sum`, `rcef_viseme_pose.dimple_right`, `rcef_viseme_pose.lip_stretch_left_sum`, `rcef_viseme_pose.lip_stretch_left`, `rcef_viseme_pose.lip_stretch_right_sum`, `rcef_viseme_pose.lip_stretch_right`, `rcef_viseme_pose.chin_raise_sum`, `rcef_viseme_pose.chin_raise`, `rcef_viseme_pose.lip_funnel_upper_left_sum`, `rcef_viseme_pose.lip_funnel_upper_left`, `rcef_viseme_pose.lip_funnel_upper_right_sum`, `rcef_viseme_pose.lip_funnel_upper_right`, `rcef_viseme_pose.lip_funnel_lower_left_sum`, `rcef_viseme_pose.lip_funnel_lower_left`, `rcef_viseme_pose.lip_funnel_lower_right_sum`, `rcef_viseme_pose.lip_funnel_lower_right`, `rcef_viseme_pose.lip_pucker_left_sum`, `rcef_viseme_pose.lip_pucker_left`, `rcef_viseme_pose.lip_pucker_right_sum`, `rcef_viseme_pose.lip_pucker_right`, `rcef_viseme_pose.lip_suck_upper_left_sum`, `rcef_viseme_pose.lip_suck_upper_left`, `rcef_viseme_pose.lip_suck_upper_right_sum`, `rcef_viseme_pose.lip_suck_upper_right`, `rcef_viseme_pose.lip_suck_lower_left_sum`, `rcef_viseme_pose.lip_suck_lower_left`, `rcef_viseme_pose.lip_suck_lower_right_sum`, `rcef_viseme_pose.lip_suck_lower_right`, `rcef_viseme_pose.lip_press_left_sum`, `rcef_viseme_pose.lip_press_left`, `rcef_viseme_pose.lip_press_right_sum`, `rcef_viseme_pose.lip_press_right`, `rcef_viseme_pose.lips_toward_sum`, `rcef_viseme_pose.lips_toward`, `rcef_viseme_pose.upper_lip_raise_left_sum`, `rcef_viseme_pose.upper_lip_raise_left`, `rcef_viseme_pose.upper_lip_raise_right_sum`, `rcef_viseme_pose.upper_lip_raise_right`, `rcef_viseme_pose.lower_lip_depress_left_sum`, `rcef_viseme_pose.lower_lip_depress_left`, `rcef_viseme_pose.lower_lip_depress_right_sum`, `rcef_viseme_pose.lower_lip_depress_right`.
- `cheek_puff`: `rcef_viseme_pose.cheek_puff_left_sum`, `rcef_viseme_pose.cheek_puff_left`, `rcef_viseme_pose.cheek_puff_right_sum`, `rcef_viseme_pose.cheek_puff_right`.
- `jaw_thrust`: `rcef_viseme_pose.jaw_thrust_sum`, `rcef_viseme_pose.jaw_thrust`.
- `chin_raise_upper_lip`: `rcef_viseme_pose.chin_raise_upper_lip_sum`, `rcef_viseme_pose.chin_raise_upper_lip`.

56 intermediate values (`rcef.intermediate`) are computed inside the map and read only by its own later mappings.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`xr_visemes`](../../references.md#xr_visemes) | 101 |
| [`apple_blendshapes`](../../references.md#apple_blendshapes) | 101 |
| [`ipa_chart_doulos_2020`](../../references.md#ipa_chart_doulos_2020) | 101 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 101 |
| [`calibration.viseme-poses.rocketbox-features`](../../references.md#calibrationviseme-posesrocketbox-features) | 45 |

## Parts this map does not have

The bridge writes only the groups of a mouth pose. Its calibration record fits no pose for the groups below, so it writes none of them, and a route labels the outputs that need them "not available from source" ([canonical-set.md](../canonical-set.md#viseme-pose-bridge)):

- `jaw_sideways` (2): `jaw_sideways_left`, `jaw_sideways_right`
- `mouth_shift` (2): `mouth_shift_left`, `mouth_shift_right`
- `blink` (2): `eye_close_left`, `eye_close_right`
- `gaze` (8): `gaze_in_left`, `gaze_in_right`, `gaze_out_left`, `gaze_out_right`, `gaze_up_left`, `gaze_up_right`, `gaze_down_left`, `gaze_down_right`
- `tongue_out` (1): `tongue_out`
- `cheek_suck` (2): `cheek_suck_left`, `cheek_suck_right`
- `lip_tighten` (2): `lip_tighten_left`, `lip_tighten_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`
