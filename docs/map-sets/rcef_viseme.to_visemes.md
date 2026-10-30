<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Written by scripts/export_map_sets.py from generated/rcef.pack.json. Do not edit. -->

# Map set `rcef_viseme.to_visemes`

One map out of the canonical viseme set (`rcef.canonical_viseme`): from `rcef.canonical_viseme` to `openxr.visemes`.

- Mappings: 15, in 3 parts.
- Evidence status of its mappings: proposed (15).
- Every mapping, with its assumptions and losses: [reports/mappings.md](../../reports/mappings.md#rcef_visemeto_visemes).

A part is the mappings of the map that read or write one group of a canonical set. The groups are metadata of the canonical signals (`metadata.group`); they document the parts of the set. The map runs as one whole: a bad or missing input stops only the outputs that read it ([examples/rcef_route.py](../../examples/rcef_route.py)).

## Parts

| Part (canonical group) | Canonical signals | Mappings | Operators | Evidence status |
|---|---|---|---|---|
| `viseme_vowel` | 5 of 5 | 5 | copy (affine 1, 0) (5) | proposed (5) |
| `viseme_consonant` | 9 of 9 | 9 | copy (affine 1, 0) (9) | proposed (9) |
| `viseme_rest` | 1 of 1 | 1 | copy (affine 1, 0) | proposed |

## Mappings by part

- `viseme_vowel`: `rcef_visemes.AA`, `rcef_visemes.E`, `rcef_visemes.IH`, `rcef_visemes.OH`, `rcef_visemes.OU`.
- `viseme_consonant`: `rcef_visemes.PP`, `rcef_visemes.FF`, `rcef_visemes.TH`, `rcef_visemes.SS`, `rcef_visemes.CH`, `rcef_visemes.DD`, `rcef_visemes.NN`, `rcef_visemes.KK`, `rcef_visemes.RR`.
- `viseme_rest`: `rcef_visemes.SIL`.

## Evidence

| Evidence record | Mappings that cite it |
|---|---|
| [`xr_visemes`](../../references.md#xr_visemes) | 15 |
| [`xr_registry`](../../references.md#xr_registry) | 15 |
| [`ipa_chart_doulos_2020`](../../references.md#ipa_chart_doulos_2020) | 15 |
| [`rcef_canonical_v1`](../../references.md#rcef_canonical_v1) | 15 |

## Loss keys

Loss keys of the [definitions audit](../canonical-set-audit.md#loss-keys) that its mappings state, with the number of mappings:

- `meta_viseme_class_scope`: 15

## Parts this map does not have

The [META visemes section](../canonical-set-audit.md#meta-visemes) of the definitions audit names no `openxr.visemes` signal for the canonical signals of these groups, so no mapping reads them. On a route to `openxr.visemes`, a source input that reaches only these groups is listed as dropped.

- `viseme_aggregate` (1): `alveolar_floor`

## Other map sets out of the canonical viseme set

| Map set | Parts | Mappings |
|---|---|---|
| [`rcef_viseme.to_vrm`](rcef_viseme.to_vrm.md) | 1 | 5 |
