<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map `rcef_expression.to_arkit`

One map out of the canonical expression set (`rcef.canonical_expression`): from `rcef.canonical_expression` to `arkit.coefficient`.

- Mappings: 52, in 9 parts.
- Evidence status of its mappings: proposed (52).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_expressionto_arkit).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `face` | 41 of 41 | 34 | copy (affine 1, 0) (29), mean of 2 (weighted_sum) (4), mean of 4 (weighted_sum) | proposed (34) |
| `cheek_puff` | 2 of 2 | 1 | mean of 2 (weighted_sum) | proposed |
| `jaw_thrust` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `jaw_sideways` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `mouth_shift` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `chin_raise_upper_lip` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `gaze` | 8 of 8 | 8 | copy (affine 1, 0) (8) | proposed (8) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |

## Mappings by part

- `face`: `rcef_arkit.jawOpen`, `rcef_arkit.mouthClose`, `rcef_arkit.browInnerUp`, `rcef_arkit.mouthSmileLeft`, `rcef_arkit.mouthSmileRight`, `rcef_arkit.mouthShrugLower`, `rcef_arkit.browDownLeft`, `rcef_arkit.browDownRight`, `rcef_arkit.browOuterUpLeft`, `rcef_arkit.browOuterUpRight`, `rcef_arkit.cheekSquintLeft`, `rcef_arkit.cheekSquintRight`, `rcef_arkit.eyeSquintLeft`, `rcef_arkit.eyeSquintRight`, `rcef_arkit.eyeWideLeft`, `rcef_arkit.eyeWideRight`, `rcef_arkit.mouthDimpleLeft`, `rcef_arkit.mouthDimpleRight`, `rcef_arkit.mouthFrownLeft`, `rcef_arkit.mouthFrownRight`, `rcef_arkit.mouthFunnel`, `rcef_arkit.mouthLowerDownLeft`, `rcef_arkit.mouthLowerDownRight`, `rcef_arkit.mouthPressLeft`, `rcef_arkit.mouthPressRight`, `rcef_arkit.mouthPucker`, `rcef_arkit.mouthRollLower`, `rcef_arkit.mouthRollUpper`, `rcef_arkit.mouthStretchLeft`, `rcef_arkit.mouthStretchRight`, `rcef_arkit.mouthUpperUpLeft`, `rcef_arkit.mouthUpperUpRight`, `rcef_arkit.noseSneerLeft`, `rcef_arkit.noseSneerRight`.
- `cheek_puff`: `rcef_arkit.cheekPuff`.
- `jaw_thrust`: `rcef_arkit.jawForward`.
- `jaw_sideways`: `rcef_arkit.jawLeft`, `rcef_arkit.jawRight`.
- `mouth_shift`: `rcef_arkit.mouthLeft`, `rcef_arkit.mouthRight`.
- `chin_raise_upper_lip`: `rcef_arkit.mouthShrugUpper`.
- `blink`: `rcef_arkit.eyeBlinkLeft`, `rcef_arkit.eyeBlinkRight`.
- `gaze`: `rcef_arkit.eyeLookOutLeft`, `rcef_arkit.eyeLookInLeft`, `rcef_arkit.eyeLookOutRight`, `rcef_arkit.eyeLookInRight`, `rcef_arkit.eyeLookDownLeft`, `rcef_arkit.eyeLookDownRight`, `rcef_arkit.eyeLookUpLeft`, `rcef_arkit.eyeLookUpRight`.
- `tongue_out`: `rcef_arkit.tongueOut`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`apple_blendshapes`](../../references.md#apple_blendshapes) | 52 |
| [`vrcft_docs_movement`](../../references.md#vrcft_docs_movement) | 42 |
| [`vrcft_docs_arkit`](../../references.md#vrcft_docs_arkit) | 50 |
| [`godot_vendors_fb2`](../../references.md#godot_vendors_fb2) | 51 |
| [`godot_face_modifier`](../../references.md#godot_face_modifier) | 52 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 52 |
| [`vrcft_docs_shapes`](../../references.md#vrcft_docs_shapes) | 1 |
| [`vrcft_docs_overview`](../../references.md#vrcft_docs_overview) | 1 |
| [`vrcft_code_parameters`](../../references.md#vrcft_code_parameters) | 6 |
| [`ict_facekit`](../../references.md#ict_facekit) | 41 |
| [`vrcft_simple_expressions`](../../references.md#vrcft_simple_expressions) | 4 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `arkit_mouthclose_jaw_unresolved`: 1
- `arkit_mouthsmile_upward`: 2
- `arkit_mouthshrug_outward`: 2
- `arkit_browdown_outer`: 2
- `arkit_cheeksquint_cheek`: 2
- `arkit_eyesquint_face`: 2
- `arkit_mouthpress_lower_lip`: 2
- `arkit_mouthpucker_compression`: 1
- `arkit_mouthstretchright_text_side`: 1
- `ict_au33_cheek_blow`: 1
- `ict_au45_blink`: 2
- `arkit_gaze_eyelid`: 8

## Parts this map does not have

The [ARKit section](../canonical-set-audit.md#arkit) of the definitions audit names no `arkit.coefficient` signal for the canonical signals of these groups, so no mapping reads them. On a route to `arkit.coefficient`, a source input that reaches only these groups is listed as dropped.

- `cheek_suck` (2): `cheek_suck_left`, `cheek_suck_right`
- `lip_tighten` (2): `lip_tighten_left`, `lip_tighten_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other maps out of the canonical expression set

| Map | Parts | Mappings |
|---|---|---|
| [`rcef_expression.to_facs`](rcef_expression.to_facs.md) | 8 | 49 |
| [`rcef_expression.to_fb2`](rcef_expression.to_fb2.md) | 12 | 74 |
| [`rcef_expression.to_vrcft_artist`](rcef_expression.to_vrcft_artist.md) | 11 | 72 |
| [`rcef_expression.to_vrcft_eye`](rcef_expression.to_vrcft_eye.md) | 2 | 4 |
| [`rcef_expression.to_vrm`](rcef_expression.to_vrm.md) | 1 | 2 |
