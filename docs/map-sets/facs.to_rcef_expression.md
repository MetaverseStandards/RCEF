<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `facs.to_rcef_expression`

One map into the canonical expression set (`rcef.canonical_expression`): from `facs.code` to `rcef.canonical_expression`.

- Mappings: 53, in 8 parts.
- Evidence status of its mappings: proposed (53).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#facsto_rcef_expression).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `face` | 41 of 41 | 41 | copy (affine 1, 0) (41) | proposed (41) |
| `cheek_puff` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `jaw_thrust` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `jaw_sideways` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `cheek_suck` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `lip_tighten` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |

## Mappings by part

- `face`: `facs_rcef.brow_inner_raise_left`, `facs_rcef.brow_inner_raise_right`, `facs_rcef.brow_outer_raise_left`, `facs_rcef.brow_outer_raise_right`, `facs_rcef.brow_lower_left`, `facs_rcef.brow_lower_right`, `facs_rcef.lid_tighten_left`, `facs_rcef.lid_tighten_right`, `facs_rcef.upper_lid_raise_left`, `facs_rcef.upper_lid_raise_right`, `facs_rcef.cheek_raise_left`, `facs_rcef.cheek_raise_right`, `facs_rcef.nose_wrinkle_left`, `facs_rcef.nose_wrinkle_right`, `facs_rcef.jaw_drop`, `facs_rcef.lip_corner_pull_left`, `facs_rcef.lip_corner_pull_right`, `facs_rcef.lip_corner_depress_left`, `facs_rcef.lip_corner_depress_right`, `facs_rcef.dimple_left`, `facs_rcef.dimple_right`, `facs_rcef.lip_stretch_left`, `facs_rcef.lip_stretch_right`, `facs_rcef.chin_raise`, `facs_rcef.lip_funnel_upper_left`, `facs_rcef.lip_funnel_upper_right`, `facs_rcef.lip_funnel_lower_left`, `facs_rcef.lip_funnel_lower_right`, `facs_rcef.lip_pucker_left`, `facs_rcef.lip_pucker_right`, `facs_rcef.lip_suck_upper_left`, `facs_rcef.lip_suck_upper_right`, `facs_rcef.lip_suck_lower_left`, `facs_rcef.lip_suck_lower_right`, `facs_rcef.lip_press_left`, `facs_rcef.lip_press_right`, `facs_rcef.lips_toward`, `facs_rcef.upper_lip_raise_left`, `facs_rcef.upper_lip_raise_right`, `facs_rcef.lower_lip_depress_left`, `facs_rcef.lower_lip_depress_right`.
- `cheek_puff`: `facs_rcef.cheek_puff_left`, `facs_rcef.cheek_puff_right`.
- `jaw_thrust`: `facs_rcef.jaw_thrust`.
- `jaw_sideways`: `facs_rcef.jaw_sideways_left`, `facs_rcef.jaw_sideways_right`.
- `blink`: `facs_rcef.eye_close_left`, `facs_rcef.eye_close_right`.
- `tongue_out`: `facs_rcef.tongue_out`.
- `cheek_suck`: `facs_rcef.cheek_suck_left`, `facs_rcef.cheek_suck_right`.
- `lip_tighten`: `facs_rcef.lip_tighten_left`, `facs_rcef.lip_tighten_right`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`facs_wikipedia`](../../references.md#facs_wikipedia) | 53 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 53 |
| [`facs_hager_2002`](../../references.md#facs_hager_2002) | 2 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `facs_ordinal_intensity`: 53
- `facs_side_frame_unresolved`: 48
- `facs_mouth_opening_split`: 1
- `facs_au17_no_split`: 1
- `facs_gross_code_no_intensity`: 9
- `facs_au30_direction_unresolved`: 2
- `facs_eyelid_events`: 2

## Parts this map does not have

The [FACS section](../canonical-set-audit.md#facs) of the definitions audit names no `facs.code` signal for the canonical signals of these groups, so no mapping writes them. A route labels the outputs that need them "not available from source", which is not a refusal.

- `mouth_shift` (2): `mouth_shift_left`, `mouth_shift_right`
- `chin_raise_upper_lip` (1): `chin_raise_upper_lip`
- `gaze` (8): `gaze_in_left`, `gaze_in_right`, `gaze_out_left`, `gaze_out_right`, `gaze_up_left`, `gaze_up_right`, `gaze_down_left`, `gaze_down_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other map sets into the canonical expression set

| Map set | Parts | Mappings |
|---|---|---|
| [`arkit.to_rcef_expression`](arkit.to_rcef_expression.md) | 9 | 60 |
| [`fb2.to_rcef_expression`](fb2.to_rcef_expression.md) | 12 | 70 |
| [`vrcft_eye.to_rcef_expression`](vrcft_eye.to_rcef_expression.md) | 2 | 4 |
| [`vrm.to_rcef_expression`](vrm.to_rcef_expression.md) | 1 | 2 |
