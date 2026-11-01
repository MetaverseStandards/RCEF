<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map `arkit.to_rcef_expression`

One map into the canonical expression set (`rcef.canonical_expression`): from `arkit.coefficient` to `rcef.canonical_expression`.

- Mappings: 60, in 9 parts.
- Evidence status of its mappings: proposed (60).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#arkitto_rcef_expression).

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

## Mappings by part

- `face`: `arkit_rcef.brow_inner_raise_left`, `arkit_rcef.brow_inner_raise_right`, `arkit_rcef.brow_outer_raise_left`, `arkit_rcef.brow_outer_raise_right`, `arkit_rcef.brow_lower_left`, `arkit_rcef.brow_lower_right`, `arkit_rcef.lid_tighten_left`, `arkit_rcef.lid_tighten_right`, `arkit_rcef.upper_lid_raise_left`, `arkit_rcef.upper_lid_raise_right`, `arkit_rcef.cheek_raise_left`, `arkit_rcef.cheek_raise_right`, `arkit_rcef.nose_wrinkle_left`, `arkit_rcef.nose_wrinkle_right`, `arkit_rcef.jaw_drop`, `arkit_rcef.lip_corner_pull_left`, `arkit_rcef.lip_corner_pull_right`, `arkit_rcef.lip_corner_depress_left`, `arkit_rcef.lip_corner_depress_right`, `arkit_rcef.dimple_left`, `arkit_rcef.dimple_right`, `arkit_rcef.lip_stretch_left`, `arkit_rcef.lip_stretch_right`, `arkit_rcef.chin_raise`, `arkit_rcef.lip_funnel_upper_left`, `arkit_rcef.lip_funnel_upper_right`, `arkit_rcef.lip_funnel_lower_left`, `arkit_rcef.lip_funnel_lower_right`, `arkit_rcef.lip_pucker_left`, `arkit_rcef.lip_pucker_right`, `arkit_rcef.lip_suck_upper_left`, `arkit_rcef.lip_suck_upper_right`, `arkit_rcef.lip_suck_lower_left`, `arkit_rcef.lip_suck_lower_right`, `arkit_rcef.lip_press_left`, `arkit_rcef.lip_press_right`, `arkit_rcef.lips_toward`, `arkit_rcef.upper_lip_raise_left`, `arkit_rcef.upper_lip_raise_right`, `arkit_rcef.lower_lip_depress_left`, `arkit_rcef.lower_lip_depress_right`.
- `cheek_puff`: `arkit_rcef.cheek_puff_left`, `arkit_rcef.cheek_puff_right`.
- `jaw_thrust`: `arkit_rcef.jaw_thrust`.
- `jaw_sideways`: `arkit_rcef.jaw_sideways_left`, `arkit_rcef.jaw_sideways_right`.
- `mouth_shift`: `arkit_rcef.mouth_shift_left`, `arkit_rcef.mouth_shift_right`.
- `chin_raise_upper_lip`: `arkit_rcef.chin_raise_upper_lip`.
- `blink`: `arkit_rcef.eye_close_left`, `arkit_rcef.eye_close_right`.
- `gaze`: `arkit_rcef.gaze_in_left`, `arkit_rcef.gaze_in_right`, `arkit_rcef.gaze_out_left`, `arkit_rcef.gaze_out_right`, `arkit_rcef.gaze_up_left`, `arkit_rcef.gaze_up_right`, `arkit_rcef.gaze_down_left`, `arkit_rcef.gaze_down_right`.
- `tongue_out`: `arkit_rcef.tongue_out`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`apple_blendshapes`](../../references.md#apple_blendshapes) | 60 |
| [`vrcft_code_parameters`](../../references.md#vrcft_code_parameters) | 14 |
| [`vrcft_docs_movement`](../../references.md#vrcft_docs_movement) | 49 |
| [`vrcft_docs_arkit`](../../references.md#vrcft_docs_arkit) | 58 |
| [`ict_facekit`](../../references.md#ict_facekit) | 49 |
| [`godot_face_modifier`](../../references.md#godot_face_modifier) | 60 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 60 |
| [`godot_vendors_fb2`](../../references.md#godot_vendors_fb2) | 58 |
| [`vrcft_simple_expressions`](../../references.md#vrcft_simple_expressions) | 4 |
| [`vrcft_docs_shapes`](../../references.md#vrcft_docs_shapes) | 1 |
| [`vrcft_docs_overview`](../../references.md#vrcft_docs_overview) | 1 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `arkit_browdown_outer`: 2
- `arkit_eyesquint_face`: 2
- `arkit_cheeksquint_cheek`: 2
- `arkit_mouthsmile_upward`: 2
- `arkit_mouthstretchright_text_side`: 1
- `arkit_mouthshrug_outward`: 2
- `arkit_mouthpucker_compression`: 2
- `arkit_mouthpress_lower_lip`: 2
- `arkit_mouthclose_jaw_unresolved`: 1
- `ict_au33_cheek_blow`: 2
- `ict_au45_blink`: 2
- `arkit_gaze_eyelid`: 8

## Parts this map does not have

The [ARKit section](../canonical-set-audit.md#arkit) of the definitions audit names no `arkit.coefficient` signal for the canonical signals of these groups, so no mapping writes them. A route labels the outputs that need them "not available from source", which is not a refusal.

- `cheek_suck` (2): `cheek_suck_left`, `cheek_suck_right`
- `lip_tighten` (2): `lip_tighten_left`, `lip_tighten_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other maps into the canonical expression set

| Map | Parts | Mappings |
|---|---|---|
| [`facs.to_rcef_expression`](facs.to_rcef_expression.md) | 8 | 53 |
| [`fb2.to_rcef_expression`](fb2.to_rcef_expression.md) | 12 | 70 |
| [`vrcft_eye.to_rcef_expression`](vrcft_eye.to_rcef_expression.md) | 2 | 4 |
| [`vrm.to_rcef_expression`](vrm.to_rcef_expression.md) | 1 | 2 |
