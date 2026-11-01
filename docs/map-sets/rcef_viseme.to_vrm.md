<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map `rcef_viseme.to_vrm`

One map out of the canonical viseme set (`rcef.canonical_viseme`): from `rcef.canonical_viseme` to `vrm.preset`.

- Mappings: 5, in 1 parts.
- Evidence status of its mappings: proposed (5).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_visemeto_vrm).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `viseme_vowel` | 5 of 5 | 5 | copy (affine 1, 0) (5) | proposed (5) |

## Mappings by part

- `viseme_vowel`: `rcef_vrm.aa`, `rcef_vrm.ih`, `rcef_vrm.ou`, `rcef_vrm.ee`, `rcef_vrm.oh`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`vrm_expressions`](../../references.md#vrm_expressions) | 5 |
| [`ipa_chart_doulos_2020`](../../references.md#ipa_chart_doulos_2020) | 5 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 5 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `vrm_vowel_asset_weight`: 5
- `vrm_ih_vowel_quality`: 1

## Parts this map does not have

The [VRM section](../canonical-set-audit.md#vrm) of the definitions audit names no `vrm.preset` signal for the canonical signals of these groups, so no mapping reads them. On a route to `vrm.preset`, a source input that reaches only these groups is listed as dropped.

- `viseme_consonant` (9): `bilabial`, `labiodental`, `dental`, `alveolar_sibilant`, `postalveolar`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal`, `rhotic`
- `viseme_rest` (1): `sil`
- `viseme_aggregate` (1): `alveolar_floor`

## Other maps out of the canonical viseme set

| Map | Parts | Mappings |
|---|---|---|
| [`rcef_viseme.to_visemes`](rcef_viseme.to_visemes.md) | 3 | 15 |
