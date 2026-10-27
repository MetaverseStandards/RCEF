# Public expression survey

SPDX-License-Identifier: CC-BY-SA-4.0

## Selected scope

| Surface | Selected entries | Calibration and execution boundary |
|---|---:|---|
| ARKit coefficient | 52 | Native 0..1, face-relative sides; 9 identities preserve this native coefficient basis. Eye transforms stay separate. |
| MediaPipe label | 52 | 51 names shared with ARKit, plus `_neutral`, no `tongueOut`; model calibration unresolved. `_neutral` is excluded. |
| OpenXR FB | 63 | Validity, eye-following validity, confidence and time retained. Explicit numeric range unresolved in the pinned extension text. No tongue entries. |
| OpenXR FB2 | 70 | Native 0..1, seven tongue entries, visual/audio negotiation; eight gaze identities preserve native directional fractions. Maximum angles unresolved. |
| Optional META visemes | 15 | FB2 dependency, probabilities, valid sum 1, separate validity; valid silence differs from invalid all-zero data. |
| VRCFT transport | 88 | Active enum separated from eye data and artist vocabulary. Byte transport clamps and truncates; those losses are inventory, not an implicit runtime operation. |
| VRCFT eye | 12 scalar components | Left/right/combined gaze x/y, openness, pupil field. Four raw openness/diameter identities; combined computation unresolved. |
| VRCFT artist base/blended | 102 / 42 | Artist components and unsupported footnotes retained. Component lists do not define weights or executable operators. |
| VRCFT avatar numeric/flags | 124 / 3 | Publicly listed floats, optional prefixes and status flags. Binary encoding scheme inventoried separately; expanded avatar-specific names are not guessed. |
| Godot base/blended | 102 / 41 | `FT_TONGUE_BLEND_DOWN` spelling retained. Setters store floats without clamp; initial array zero is initialization. No device availability inferred. |
| VRM 1.0 presets | 18 | All optional and asset-authored; morph/material/texture bindings, thresholds, overrides and LookAt metadata preserved. |
| Roblox FaceControls | 50 | Native 0..1 but asset-specific joint poses/correctives. Neutral Frame 0 and requirement conflicts retained. |

Sources and exact digests are in [sources.toml](evidence/sources.toml). The generated coverage groups every signal by disposition and every mapping with disposition `mapped` by quality. Profile and signal metadata tell selected entries apart from ancillary records. Every evidence source appears in coverage, even if it supports only unresolved or excluded records.

## Semantics that remain distinct

`mapped`, `unsupported`, `unresolved` and `excluded` are dispositions. Only mappings with disposition `mapped` have a mapping quality. Evidence status describes verification, separately from execution. A verified native identifier can still have an unresolved canonical mapping.

A tracking validity flag is not a neutral coefficient. VRCFT openness starts at 1, but that is not a measured neutral. The raw `PupilDiameter_MM` fields hold millimetres. The combined method, however, puts normalized dilation in a field with the same name, and it replaces NaN with 0.5. The pinned implementation always averages combined gaze, although the documentation describes behaviour that depends on validity. No scalar identity implements behaviour with state like this.

ARKit eye-look coefficients, ARKit eye transforms, FB2 direction fractions and VRCFT normalized Cartesian avatar parameters are separate bases. Because maximum angles and model calibration are unknown, no cross-provider identity is possible. Physical diameter and normalized dilation are different quantities.

VRM binary metadata records `0.49 → 0`, `0.5 → 0`, `0.51 → 1`, because the comparison is strictly `> 0.5`. Where overrides apply, they act after that binary decision. LookAt describes one shared direction and range maps specific to each model. It cannot express two eyes that point in different directions. Executing bindings, materials and overrides is left for later.

At the same pinned revision, Roblox's FaceControls documentation and its dynamic-head specifications each list 17 required poses, but the lists differ. RCEF records both lists and which list each control is in. Frame 0 is the neutral joint pose. A combination corrective stores a difference from the combined base poses. Certification and executing correctives are still unresolved.

VRCFT's artist lower-lip names conflict with their direction wording. The sad-side wording conflicts with the names and components. The public parameter wording for nasal constriction swaps the sides. The binary page describes both a `2^N-1` range and `1/2^N` bit values. These conflicts block derived mappings. Four artist footnotes mark their shapes as unused by all interfaces. That is source evidence as of the retrieval date, not a statement that the shapes cannot be used.

## General morph weights

The [pinned glTF source](references.md) allows morph coefficients outside 0..1. The domains of tracked signals do not set a domain for every morph. Signed geometric weights or weights above one, bind and rest transforms, asset hashes and host execution belong to the shared tooling and to later asset tests. RCEF does not make geometry.
