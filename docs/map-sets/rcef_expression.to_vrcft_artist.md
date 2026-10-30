<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `rcef_expression.to_vrcft_artist`

One map out of the canonical expression set (`rcef.canonical_expression`): from `rcef.canonical_expression` to `vrcft.artist.base`.

- Mappings: 72, in 11 parts.
- Evidence status of its mappings: proposed (72).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_expressionto_vrcft_artist).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `face` | 41 of 41 | 47 | copy (affine 1, 0) (47) | proposed (47) |
| `cheek_puff` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `jaw_thrust` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `jaw_sideways` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `mouth_shift` | 2 of 2 | 4 | copy (affine 1, 0) (4) | proposed (4) |
| `chin_raise_upper_lip` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `gaze` | 8 of 8 | 8 | copy (affine 1, 0) (8) | proposed (8) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `cheek_suck` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `lip_tighten` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |

## Mappings by part

- `face`: `rcef_vrcft_artist.BrowLowererLeft`, `rcef_vrcft_artist.BrowPinchLeft`, `rcef_vrcft_artist.BrowLowererRight`, `rcef_vrcft_artist.BrowPinchRight`, `rcef_vrcft_artist.BrowInnerUpRight`, `rcef_vrcft_artist.BrowInnerUpLeft`, `rcef_vrcft_artist.BrowOuterUpLeft`, `rcef_vrcft_artist.BrowOuterUpRight`, `rcef_vrcft_artist.CheekSquintLeft`, `rcef_vrcft_artist.CheekSquintRight`, `rcef_vrcft_artist.EyeSquintLeft`, `rcef_vrcft_artist.EyeSquintRight`, `rcef_vrcft_artist.EyeWideLeft`, `rcef_vrcft_artist.EyeWideRight`, `rcef_vrcft_artist.JawOpen`, `rcef_vrcft_artist.MouthClosed`, `rcef_vrcft_artist.MouthDimpleLeft`, `rcef_vrcft_artist.MouthDimpleRight`, `rcef_vrcft_artist.MouthFrownLeft`, `rcef_vrcft_artist.MouthFrownRight`, `rcef_vrcft_artist.LipFunnelUpperRight`, `rcef_vrcft_artist.LipFunnelUpperLeft`, `rcef_vrcft_artist.LipFunnelLowerRight`, `rcef_vrcft_artist.LipFunnelLowerLeft`, `rcef_vrcft_artist.MouthLowerDownLeft`, `rcef_vrcft_artist.MouthLowerDownRight`, `rcef_vrcft_artist.MouthPressLeft`, `rcef_vrcft_artist.MouthPressRight`, `rcef_vrcft_artist.LipPuckerUpperRight`, `rcef_vrcft_artist.LipPuckerUpperLeft`, `rcef_vrcft_artist.LipPuckerLowerRight`, `rcef_vrcft_artist.LipPuckerLowerLeft`, `rcef_vrcft_artist.LipSuckLowerRight`, `rcef_vrcft_artist.LipSuckLowerLeft`, `rcef_vrcft_artist.LipSuckUpperRight`, `rcef_vrcft_artist.LipSuckUpperLeft`, `rcef_vrcft_artist.MouthRaiserLower`, `rcef_vrcft_artist.MouthCornerPullLeft`, `rcef_vrcft_artist.MouthCornerSlantLeft`, `rcef_vrcft_artist.MouthCornerPullRight`, `rcef_vrcft_artist.MouthCornerSlantRight`, `rcef_vrcft_artist.MouthStretchLeft`, `rcef_vrcft_artist.MouthStretchRight`, `rcef_vrcft_artist.MouthUpperUpLeft`, `rcef_vrcft_artist.MouthUpperUpRight`, `rcef_vrcft_artist.NoseSneerLeft`, `rcef_vrcft_artist.NoseSneerRight`.
- `cheek_puff`: `rcef_vrcft_artist.CheekPuffRight`, `rcef_vrcft_artist.CheekPuffLeft`.
- `jaw_thrust`: `rcef_vrcft_artist.JawForward`.
- `jaw_sideways`: `rcef_vrcft_artist.JawLeft`, `rcef_vrcft_artist.JawRight`.
- `mouth_shift`: `rcef_vrcft_artist.MouthUpperLeft`, `rcef_vrcft_artist.MouthLowerLeft`, `rcef_vrcft_artist.MouthUpperRight`, `rcef_vrcft_artist.MouthLowerRight`.
- `chin_raise_upper_lip`: `rcef_vrcft_artist.MouthRaiserUpper`.
- `blink`: `rcef_vrcft_artist.EyeClosedLeft`, `rcef_vrcft_artist.EyeClosedRight`.
- `gaze`: `rcef_vrcft_artist.EyeLookDownLeft`, `rcef_vrcft_artist.EyeLookDownRight`, `rcef_vrcft_artist.EyeLookInLeft`, `rcef_vrcft_artist.EyeLookInRight`, `rcef_vrcft_artist.EyeLookOutLeft`, `rcef_vrcft_artist.EyeLookOutRight`, `rcef_vrcft_artist.EyeLookUpLeft`, `rcef_vrcft_artist.EyeLookUpRight`.
- `tongue_out`: `rcef_vrcft_artist.TongueOut`.
- `cheek_suck`: `rcef_vrcft_artist.CheekSuckLeft`, `rcef_vrcft_artist.CheekSuckRight`.
- `lip_tighten`: `rcef_vrcft_artist.MouthTightenerLeft`, `rcef_vrcft_artist.MouthTightenerRight`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`vrcft_artist`](../../references.md#vrcft_artist) | 72 |
| [`vrcft_docs_shapes`](../../references.md#vrcft_docs_shapes) | 72 |
| [`godot_face_modifier`](../../references.md#godot_face_modifier) | 72 |
| [`vrcft_docs_arkit`](../../references.md#vrcft_docs_arkit) | 64 |
| [`vrcft_simple_expressions`](../../references.md#vrcft_simple_expressions) | 8 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 72 |
| [`vrcft_code_parameters`](../../references.md#vrcft_code_parameters) | 16 |
| [`vrcft_docs_movement`](../../references.md#vrcft_docs_movement) | 8 |
| [`godot_vendors_fb2`](../../references.md#godot_vendors_fb2) | 4 |
| [`godot_enum`](../../references.md#godot_enum) | 4 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `vrcft_ue_set_equal`: 16
- `vrcft_ue_cheeksquint_cheek`: 2
- `vrcft_ue_eyesquint_socket`: 2
- `vrcft_ue_mouthclosed_jaw_relative`: 1
- `vrcft_ue_mouthlowerdown_direction_unresolved`: 2
- `vrcft_ue_mouthstretch_down`: 2
- `vrcft_ue_gaze_no_angle`: 8

## Parts this map does not have

The [VRCFaceTracking Unified Expressions section](../canonical-set-audit.md#vrcfacetracking-unified-expressions) of the definitions audit names no `vrcft.artist.base` signal for the canonical signals of these groups, so no mapping reads them. A route labels the outputs that need them "not available from source", which is not a refusal.

- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other map sets out of the canonical expression set

| Map set | Parts | Mappings |
|---|---|---|
| [`rcef_expression.to_arkit`](rcef_expression.to_arkit.md) | 9 | 52 |
| [`rcef_expression.to_facs`](rcef_expression.to_facs.md) | 8 | 49 |
| [`rcef_expression.to_fb2`](rcef_expression.to_fb2.md) | 12 | 74 |
| [`rcef_expression.to_vrcft_eye`](rcef_expression.to_vrcft_eye.md) | 2 | 4 |
| [`rcef_expression.to_vrm`](rcef_expression.to_vrm.md) | 1 | 2 |
