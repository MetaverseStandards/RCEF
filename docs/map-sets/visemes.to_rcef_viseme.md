<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map `visemes.to_rcef_viseme`

One map into the canonical viseme set (`rcef.canonical_viseme`): from `openxr.visemes` to `rcef.canonical_viseme`.

- Mappings: 17, in 4 parts.
- Evidence status of its mappings: proposed (17).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#visemesto_rcef_viseme).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `viseme_vowel` | 5 of 5 | 5 | copy (affine 1, 0) (5) | proposed (5) |
| `viseme_consonant` | 9 of 9 | 9 | copy (affine 1, 0) (9) | proposed (9) |
| `viseme_rest` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |
| `viseme_aggregate` | 1 of 1 | 2 | weighted_sum 1, 1, 1, 1, piecewise_linear (0, 0) (1, 1) (4, 1) | proposed (2) |

## Mappings by part

- `viseme_vowel`: `visemes_rcef.vowel_open`, `visemes_rcef.vowel_mid_spread`, `visemes_rcef.vowel_close_spread`, `visemes_rcef.vowel_mid_rounded`, `visemes_rcef.vowel_close_rounded`.
- `viseme_consonant`: `visemes_rcef.bilabial`, `visemes_rcef.labiodental`, `visemes_rcef.dental`, `visemes_rcef.alveolar_sibilant`, `visemes_rcef.postalveolar`, `visemes_rcef.coronal_stop`, `visemes_rcef.coronal_nasal_lateral`, `visemes_rcef.dorsal`, `visemes_rcef.rhotic`.
- `viseme_rest`: `visemes_rcef.sil`.
- `viseme_aggregate`: `visemes_rcef.viseme_alveolar_floor_sum`, `visemes_rcef.alveolar_floor`.

1 intermediate values (`rcef.intermediate`) are computed inside the map and read only by its own later mappings.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`xr_visemes`](../../references.md#xr_visemes) | 17 |
| [`xr_registry`](../../references.md#xr_registry) | 17 |
| [`ipa_chart_doulos_2020`](../../references.md#ipa_chart_doulos_2020) | 17 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 17 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `meta_viseme_class_scope`: 15
- `meta_viseme_aggregate_sum`: 2

## Parts this map does not have

None: the map writes every group of the canonical viseme set.

## Other maps into the canonical viseme set

| Map | Parts | Mappings |
|---|---|---|
| [`vrm.to_rcef_viseme`](vrm.to_rcef_viseme.md) | 1 | 5 |
