<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `fb2.to_rcef_expression`

One map into the canonical expression set (`rcef.canonical_expression`): from `openxr.fb2` to `rcef.canonical_expression`.

- Mappings: 70, in 12 parts.
- Evidence status of its mappings: proposed (70).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#fb2to_rcef_expression).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `face` | 41 of 41 | 41 | copy (affine 1, 0) (41) | proposed (41) |
| `cheek_puff` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `jaw_thrust` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `jaw_sideways` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `mouth_shift` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `chin_raise_upper_lip` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `gaze` | 8 of 8 | 8 | copy (affine 1, 0) (8) | proposed (8) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `cheek_suck` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `lip_tighten` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `tongue_place` | 6 of 6 | 6 | copy (affine 1, 0) (6) | proposed (6) |

## Mappings by part

- `face`: `fb2_rcef.brow_inner_raise_left`, `fb2_rcef.brow_inner_raise_right`, `fb2_rcef.brow_outer_raise_left`, `fb2_rcef.brow_outer_raise_right`, `fb2_rcef.brow_lower_left`, `fb2_rcef.brow_lower_right`, `fb2_rcef.lid_tighten_left`, `fb2_rcef.lid_tighten_right`, `fb2_rcef.upper_lid_raise_left`, `fb2_rcef.upper_lid_raise_right`, `fb2_rcef.cheek_raise_left`, `fb2_rcef.cheek_raise_right`, `fb2_rcef.nose_wrinkle_left`, `fb2_rcef.nose_wrinkle_right`, `fb2_rcef.jaw_drop`, `fb2_rcef.lip_corner_pull_left`, `fb2_rcef.lip_corner_pull_right`, `fb2_rcef.lip_corner_depress_left`, `fb2_rcef.lip_corner_depress_right`, `fb2_rcef.dimple_left`, `fb2_rcef.dimple_right`, `fb2_rcef.lip_stretch_left`, `fb2_rcef.lip_stretch_right`, `fb2_rcef.chin_raise`, `fb2_rcef.lip_funnel_upper_left`, `fb2_rcef.lip_funnel_upper_right`, `fb2_rcef.lip_funnel_lower_left`, `fb2_rcef.lip_funnel_lower_right`, `fb2_rcef.lip_pucker_left`, `fb2_rcef.lip_pucker_right`, `fb2_rcef.lip_suck_upper_left`, `fb2_rcef.lip_suck_upper_right`, `fb2_rcef.lip_suck_lower_left`, `fb2_rcef.lip_suck_lower_right`, `fb2_rcef.lip_press_left`, `fb2_rcef.lip_press_right`, `fb2_rcef.lips_toward`, `fb2_rcef.upper_lip_raise_left`, `fb2_rcef.upper_lip_raise_right`, `fb2_rcef.lower_lip_depress_left`, `fb2_rcef.lower_lip_depress_right`.
- `cheek_puff`: `fb2_rcef.cheek_puff_left`, `fb2_rcef.cheek_puff_right`.
- `jaw_thrust`: `fb2_rcef.jaw_thrust`.
- `jaw_sideways`: `fb2_rcef.jaw_sideways_left`, `fb2_rcef.jaw_sideways_right`.
- `mouth_shift`: `fb2_rcef.mouth_shift_left`, `fb2_rcef.mouth_shift_right`.
- `chin_raise_upper_lip`: `fb2_rcef.chin_raise_upper_lip`.
- `blink`: `fb2_rcef.eye_close_left`, `fb2_rcef.eye_close_right`.
- `gaze`: `fb2_rcef.gaze_in_left`, `fb2_rcef.gaze_in_right`, `fb2_rcef.gaze_out_left`, `fb2_rcef.gaze_out_right`, `fb2_rcef.gaze_up_left`, `fb2_rcef.gaze_up_right`, `fb2_rcef.gaze_down_left`, `fb2_rcef.gaze_down_right`.
- `tongue_out`: `fb2_rcef.tongue_out`.
- `cheek_suck`: `fb2_rcef.cheek_suck_left`, `fb2_rcef.cheek_suck_right`.
- `lip_tighten`: `fb2_rcef.lip_tighten_left`, `fb2_rcef.lip_tighten_right`.
- `tongue_place`: `fb2_rcef.tongue_retreat`, `fb2_rcef.tongue_tip_interdental`, `fb2_rcef.tongue_tip_alveolar`, `fb2_rcef.tongue_front_dorsal_palate`, `fb2_rcef.tongue_mid_dorsal_palate`, `fb2_rcef.tongue_back_dorsal_velar`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`xr_fb2`](../../references.md#xr_fb2) | 70 |
| [`vrcft_code_parameters`](../../references.md#vrcft_code_parameters) | 14 |
| [`vrcft_docs_movement`](../../references.md#vrcft_docs_movement) | 53 |
| [`vrcft_docs_arkit`](../../references.md#vrcft_docs_arkit) | 47 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 70 |
| [`godot_vendors_fb2`](../../references.md#godot_vendors_fb2) | 62 |
| [`godot_face_modifier`](../../references.md#godot_face_modifier) | 62 |
| [`vrcft_docs_shapes`](../../references.md#vrcft_docs_shapes) | 1 |
| [`vrcft_docs_overview`](../../references.md#vrcft_docs_overview) | 1 |
| [`godot_enum`](../../references.md#godot_enum) | 4 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `fb2_gaze_rotation`: 8
- `fb2_gaze_max_angle_unspecified`: 8
- `fb2_gaze_exclusive`: 8

## Parts this map does not have

The [FB2 section](../canonical-set-audit.md#fb2) of the definitions audit names no `openxr.fb2` signal for the canonical signals of these groups, so no mapping writes them. A route labels the outputs that need them "not available from source", which is not a refusal.

- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other map sets into the canonical expression set

| Map set | Parts | Mappings |
|---|---|---|
| [`arkit.to_rcef_expression`](arkit.to_rcef_expression.md) | 9 | 60 |
| [`facs.to_rcef_expression`](facs.to_rcef_expression.md) | 8 | 53 |
| [`vrcft_eye.to_rcef_expression`](vrcft_eye.to_rcef_expression.md) | 2 | 4 |
| [`vrm.to_rcef_expression`](vrm.to_rcef_expression.md) | 1 | 2 |
