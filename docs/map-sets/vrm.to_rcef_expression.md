<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `vrm.to_rcef_expression`

One map into the canonical expression set (`rcef.canonical_expression`): from `vrm.preset` to `rcef.canonical_expression`.

- Mappings: 2, in 1 parts.
- Evidence status of its mappings: proposed (2).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#vrmto_rcef_expression).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |

## Mappings by part

- `blink`: `vrm_rcef.eye_close_left`, `vrm_rcef.eye_close_right`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`vrm_expressions`](../../references.md#vrm_expressions) | 2 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 2 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `vrm_blink_side_unresolved`: 2

## Parts this map does not have

The [VRM section](../canonical-set-audit.md#vrm) of the definitions audit names no `vrm.preset` signal for the canonical signals of these groups, so no mapping writes them. A route labels the outputs that need them "not available from source", which is not a refusal.

- `face` (41): `brow_inner_raise_left`, `brow_inner_raise_right`, `brow_outer_raise_left`, `brow_outer_raise_right`, `brow_lower_left`, `brow_lower_right`, `lid_tighten_left`, `lid_tighten_right`, `upper_lid_raise_left`, `upper_lid_raise_right`, `cheek_raise_left`, `cheek_raise_right`, `nose_wrinkle_left`, `nose_wrinkle_right`, `jaw_drop`, `lip_corner_pull_left`, `lip_corner_pull_right`, `lip_corner_depress_left`, `lip_corner_depress_right`, `dimple_left`, `dimple_right`, `lip_stretch_left`, `lip_stretch_right`, `chin_raise`, `lip_funnel_upper_left`, `lip_funnel_upper_right`, `lip_funnel_lower_left`, `lip_funnel_lower_right`, `lip_pucker_left`, `lip_pucker_right`, `lip_suck_upper_left`, `lip_suck_upper_right`, `lip_suck_lower_left`, `lip_suck_lower_right`, `lip_press_left`, `lip_press_right`, `lips_toward`, `upper_lip_raise_left`, `upper_lip_raise_right`, `lower_lip_depress_left`, `lower_lip_depress_right`
- `cheek_puff` (2): `cheek_puff_left`, `cheek_puff_right`
- `jaw_thrust` (1): `jaw_thrust`
- `jaw_sideways` (2): `jaw_sideways_left`, `jaw_sideways_right`
- `mouth_shift` (2): `mouth_shift_left`, `mouth_shift_right`
- `chin_raise_upper_lip` (1): `chin_raise_upper_lip`
- `gaze` (8): `gaze_in_left`, `gaze_in_right`, `gaze_out_left`, `gaze_out_right`, `gaze_up_left`, `gaze_up_right`, `gaze_down_left`, `gaze_down_right`
- `tongue_out` (1): `tongue_out`
- `cheek_suck` (2): `cheek_suck_left`, `cheek_suck_right`
- `lip_tighten` (2): `lip_tighten_left`, `lip_tighten_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other map sets into the canonical expression set

| Map set | Parts | Mappings |
|---|---|---|
| [`arkit.to_rcef_expression`](arkit.to_rcef_expression.md) | 9 | 60 |
| [`facs.to_rcef_expression`](facs.to_rcef_expression.md) | 8 | 53 |
| [`fb2.to_rcef_expression`](fb2.to_rcef_expression.md) | 12 | 70 |
| [`vrcft_eye.to_rcef_expression`](vrcft_eye.to_rcef_expression.md) | 2 | 4 |
