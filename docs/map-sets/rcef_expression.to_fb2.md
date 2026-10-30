<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `rcef_expression.to_fb2`

One map out of the canonical expression set (`rcef.canonical_expression`): from `rcef.canonical_expression` to `openxr.fb2`.

- Mappings: 74, in 12 parts.
- Evidence status of its mappings: proposed (74).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_expressionto_fb2).

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
| `gaze` | 8 of 8 | 12 | weighted_sum 1, -1 (4), piecewise_linear (-1, 0) (0, 0) (1, 1) (4), piecewise_linear (-1, 1) (0, 0) (1, 0) (4) | proposed (12) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `cheek_suck` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `lip_tighten` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `tongue_place` | 6 of 6 | 6 | copy (affine 1, 0) (6) | proposed (6) |

## Mappings by part

- `face`: `rcef_fb2.BROW_LOWERER_L`, `rcef_fb2.BROW_LOWERER_R`, `rcef_fb2.INNER_BROW_RAISER_L`, `rcef_fb2.INNER_BROW_RAISER_R`, `rcef_fb2.OUTER_BROW_RAISER_L`, `rcef_fb2.OUTER_BROW_RAISER_R`, `rcef_fb2.CHEEK_RAISER_L`, `rcef_fb2.CHEEK_RAISER_R`, `rcef_fb2.LID_TIGHTENER_L`, `rcef_fb2.LID_TIGHTENER_R`, `rcef_fb2.UPPER_LID_RAISER_L`, `rcef_fb2.UPPER_LID_RAISER_R`, `rcef_fb2.JAW_DROP`, `rcef_fb2.LIPS_TOWARD`, `rcef_fb2.DIMPLER_L`, `rcef_fb2.DIMPLER_R`, `rcef_fb2.LIP_CORNER_DEPRESSOR_L`, `rcef_fb2.LIP_CORNER_DEPRESSOR_R`, `rcef_fb2.LIP_FUNNELER_LB`, `rcef_fb2.LIP_FUNNELER_LT`, `rcef_fb2.LIP_FUNNELER_RB`, `rcef_fb2.LIP_FUNNELER_RT`, `rcef_fb2.LOWER_LIP_DEPRESSOR_L`, `rcef_fb2.LOWER_LIP_DEPRESSOR_R`, `rcef_fb2.LIP_PRESSOR_L`, `rcef_fb2.LIP_PRESSOR_R`, `rcef_fb2.LIP_PUCKER_L`, `rcef_fb2.LIP_PUCKER_R`, `rcef_fb2.LIP_SUCK_LB`, `rcef_fb2.LIP_SUCK_RB`, `rcef_fb2.LIP_SUCK_LT`, `rcef_fb2.LIP_SUCK_RT`, `rcef_fb2.CHIN_RAISER_B`, `rcef_fb2.LIP_CORNER_PULLER_L`, `rcef_fb2.LIP_CORNER_PULLER_R`, `rcef_fb2.LIP_STRETCHER_L`, `rcef_fb2.LIP_STRETCHER_R`, `rcef_fb2.UPPER_LIP_RAISER_L`, `rcef_fb2.UPPER_LIP_RAISER_R`, `rcef_fb2.NOSE_WRINKLER_L`, `rcef_fb2.NOSE_WRINKLER_R`.
- `cheek_puff`: `rcef_fb2.CHEEK_PUFF_L`, `rcef_fb2.CHEEK_PUFF_R`.
- `jaw_thrust`: `rcef_fb2.JAW_THRUST`.
- `jaw_sideways`: `rcef_fb2.JAW_SIDEWAYS_LEFT`, `rcef_fb2.JAW_SIDEWAYS_RIGHT`.
- `mouth_shift`: `rcef_fb2.MOUTH_LEFT`, `rcef_fb2.MOUTH_RIGHT`.
- `chin_raise_upper_lip`: `rcef_fb2.CHIN_RAISER_T`.
- `blink`: `rcef_fb2.EYES_CLOSED_L`, `rcef_fb2.EYES_CLOSED_R`.
- `gaze`: `rcef_fb2.gaze_in_minus_out_left`, `rcef_fb2.EYES_LOOK_RIGHT_L`, `rcef_fb2.EYES_LOOK_LEFT_L`, `rcef_fb2.gaze_up_minus_down_left`, `rcef_fb2.EYES_LOOK_UP_L`, `rcef_fb2.EYES_LOOK_DOWN_L`, `rcef_fb2.gaze_in_minus_out_right`, `rcef_fb2.EYES_LOOK_LEFT_R`, `rcef_fb2.EYES_LOOK_RIGHT_R`, `rcef_fb2.gaze_up_minus_down_right`, `rcef_fb2.EYES_LOOK_UP_R`, `rcef_fb2.EYES_LOOK_DOWN_R`.
- `tongue_out`: `rcef_fb2.TONGUE_OUT`.
- `cheek_suck`: `rcef_fb2.CHEEK_SUCK_L`, `rcef_fb2.CHEEK_SUCK_R`.
- `lip_tighten`: `rcef_fb2.LIP_TIGHTENER_L`, `rcef_fb2.LIP_TIGHTENER_R`.
- `tongue_place`: `rcef_fb2.TONGUE_RETREAT`, `rcef_fb2.TONGUE_TIP_INTERDENTAL`, `rcef_fb2.TONGUE_TIP_ALVEOLAR`, `rcef_fb2.TONGUE_FRONT_DORSAL_PALATE`, `rcef_fb2.TONGUE_MID_DORSAL_PALATE`, `rcef_fb2.TONGUE_BACK_DORSAL_VELAR`.

4 intermediate values (`rcef.intermediate`) are computed inside the map and read only by its own later mappings.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`xr_fb2`](../../references.md#xr_fb2) | 74 |
| [`godot_vendors_fb2`](../../references.md#godot_vendors_fb2) | 62 |
| [`godot_face_modifier`](../../references.md#godot_face_modifier) | 62 |
| [`vrcft_docs_arkit`](../../references.md#vrcft_docs_arkit) | 47 |
| [`vrcft_docs_movement`](../../references.md#vrcft_docs_movement) | 53 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 74 |
| [`vrcft_code_parameters`](../../references.md#vrcft_code_parameters) | 14 |
| [`vrcft_docs_shapes`](../../references.md#vrcft_docs_shapes) | 1 |
| [`vrcft_docs_overview`](../../references.md#vrcft_docs_overview) | 1 |
| [`godot_enum`](../../references.md#godot_enum) | 4 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `fb2_gaze_rotation`: 8
- `fb2_gaze_max_angle_unspecified`: 8

## Parts this map does not have

The [FB2 section](../canonical-set-audit.md#fb2) of the definitions audit names no `openxr.fb2` signal for the canonical signals of these groups, so no mapping reads them. On a route to `openxr.fb2`, a source input that reaches only these groups is listed as dropped.

- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other map sets out of the canonical expression set

| Map set | Parts | Mappings |
|---|---|---|
| [`rcef_expression.to_arkit`](rcef_expression.to_arkit.md) | 9 | 52 |
| [`rcef_expression.to_facs`](rcef_expression.to_facs.md) | 8 | 49 |
| [`rcef_expression.to_vrcft_artist`](rcef_expression.to_vrcft_artist.md) | 11 | 72 |
| [`rcef_expression.to_vrcft_eye`](rcef_expression.to_vrcft_eye.md) | 2 | 4 |
| [`rcef_expression.to_vrm`](rcef_expression.to_vrm.md) | 1 | 2 |
