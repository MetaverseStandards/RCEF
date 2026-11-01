<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map `rcef_expression.to_facs`

One map out of the canonical expression set (`rcef.canonical_expression`): from `rcef.canonical_expression` to `facs.code`.

- Mappings: 49, in 8 parts.
- Evidence status of its mappings: proposed (49).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_expressionto_facs).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `face` | 41 of 41 | 37 | copy (affine 1, 0) (33), mean of 2 (weighted_sum) (4) | proposed (37) |
| `cheek_puff` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `jaw_thrust` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `jaw_sideways` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `blink` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `tongue_out` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `cheek_suck` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |
| `lip_tighten` | 2 of 2 | 2 | copy (affine 1, 0) (2) | proposed (2) |

## Mappings by part

- `face`: `rcef_facs.au01_left`, `rcef_facs.au01_right`, `rcef_facs.au02_left`, `rcef_facs.au02_right`, `rcef_facs.au04_left`, `rcef_facs.au04_right`, `rcef_facs.au05_left`, `rcef_facs.au05_right`, `rcef_facs.au06_left`, `rcef_facs.au06_right`, `rcef_facs.au07_left`, `rcef_facs.au07_right`, `rcef_facs.au08`, `rcef_facs.au09_left`, `rcef_facs.au09_right`, `rcef_facs.au10_left`, `rcef_facs.au10_right`, `rcef_facs.au12_left`, `rcef_facs.au12_right`, `rcef_facs.au14_left`, `rcef_facs.au14_right`, `rcef_facs.au15_left`, `rcef_facs.au15_right`, `rcef_facs.au16_left`, `rcef_facs.au16_right`, `rcef_facs.au17`, `rcef_facs.au18_left`, `rcef_facs.au18_right`, `rcef_facs.au20_left`, `rcef_facs.au20_right`, `rcef_facs.au22_left`, `rcef_facs.au22_right`, `rcef_facs.au24_left`, `rcef_facs.au24_right`, `rcef_facs.au26`, `rcef_facs.au28_left`, `rcef_facs.au28_right`.
- `cheek_puff`: `rcef_facs.au34_left`, `rcef_facs.au34_right`.
- `jaw_thrust`: `rcef_facs.au29`.
- `jaw_sideways`: `rcef_facs.au30_left`, `rcef_facs.au30_right`.
- `blink`: `rcef_facs.au43_left`, `rcef_facs.au43_right`.
- `tongue_out`: `rcef_facs.au19`.
- `cheek_suck`: `rcef_facs.au35_left`, `rcef_facs.au35_right`.
- `lip_tighten`: `rcef_facs.au23_left`, `rcef_facs.au23_right`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`facs_wikipedia`](../../references.md#facs_wikipedia) | 49 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 49 |
| [`facs_hager_2002`](../../references.md#facs_hager_2002) | 2 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `facs_ordinal_intensity`: 49
- `facs_side_frame_unresolved`: 44
- `facs_au17_no_split`: 1
- `facs_mouth_opening_split`: 1
- `facs_gross_code_no_intensity`: 9
- `facs_au30_direction_unresolved`: 2
- `facs_eyelid_events`: 2

## Parts this map does not have

The [FACS section](../canonical-set-audit.md#facs) of the definitions audit names no `facs.code` signal for the canonical signals of these groups, so no mapping reads them. On a route to `facs.code`, a source input that reaches only these groups is listed as dropped.

- `mouth_shift` (2): `mouth_shift_left`, `mouth_shift_right`
- `chin_raise_upper_lip` (1): `chin_raise_upper_lip`
- `gaze` (8): `gaze_in_left`, `gaze_in_right`, `gaze_out_left`, `gaze_out_right`, `gaze_up_left`, `gaze_up_right`, `gaze_down_left`, `gaze_down_right`
- `tongue_place` (6): `tongue_retreat`, `tongue_tip_interdental`, `tongue_tip_alveolar`, `tongue_front_dorsal_palate`, `tongue_mid_dorsal_palate`, `tongue_back_dorsal_velar`
- `pupil_mm` (2): `pupil_diameter_mm_left`, `pupil_diameter_mm_right`

## Other maps out of the canonical expression set

| Map | Parts | Mappings |
|---|---|---|
| [`rcef_expression.to_arkit`](rcef_expression.to_arkit.md) | 9 | 52 |
| [`rcef_expression.to_fb2`](rcef_expression.to_fb2.md) | 12 | 74 |
| [`rcef_expression.to_vrcft_artist`](rcef_expression.to_vrcft_artist.md) | 11 | 72 |
| [`rcef_expression.to_vrcft_eye`](rcef_expression.to_vrcft_eye.md) | 2 | 4 |
| [`rcef_expression.to_vrm`](rcef_expression.to_vrm.md) | 1 | 2 |
