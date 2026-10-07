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

Sources and exact digests are in [sources.toml](evidence/sources.toml). Generated coverage partitions every signal by disposition and every mapped rule by quality. Selected counts and ancillary records are separately identified by profile/signal metadata. All evidence sources appear in coverage even when they support unresolved or excluded records.

## Semantics that remain distinct

`mapped`, `unsupported`, `unresolved`, and `excluded` are dispositions. Mapping quality is present only on mapped rules. Evidence status describes verification independently of execution. A verified native identifier may still have an unresolved canonical mapping.

A tracking validity flag is not a neutral coefficient. VRCFT openness initializes to 1; that does not establish measured neutral. The raw `PupilDiameter_MM` fields represent millimetres, while the combined method places normalized dilation in a field with the same name and recovers NaN as 0.5. Combined gaze is unconditionally averaged by the pinned implementation despite different validity-dependent prose. No such stateful behavior is implemented by a scalar identity.

ARKit eye-look coefficients, ARKit eye transforms, FB2 direction fractions and VRCFT normalized Cartesian avatar parameters are separate bases. Unknown maximum angles or model calibration prevent cross-provider identity. Physical diameter and normalized dilation are different quantities.

VRM binary metadata records `0.49 → 0`, `0.5 → 0`, `0.51 → 1` because the comparison is strictly `> 0.5`. Overrides operate after that binary decision when applicable. LookAt describes a shared direction and model-specific range maps; independent divergent eyes are outside that component's expressive scope. Execution of bindings/materials/overrides is deferred.

Roblox's FaceControls documentation and dynamic-head specifications list different 17 required poses at the same pinned revision. Both lists and each control's membership are inventoried. Frame 0 is the neutral joint pose; combination correctives store a difference from combined base poses. Certification and corrective execution remain unresolved.

VRCFT artist lower-lip names conflict with direction wording; sad-side wording conflicts with names/components. Public parameter nasal constriction wording swaps sides. The binary page describes both a `2^N-1` range and `1/2^N` bit values. These conflicts block derived rules. Four artist footnotes report no interface use; that is retrieval-scoped source evidence, not an assertion of impossibility.

## General morph weights

The [pinned glTF source](references.md) allows morph coefficients outside 0..1. Tracked signal domains do not impose universal morph domains. Signed or greater-than-one geometric weights, bind/rest transforms, asset hashes and host execution belong to shared tooling and downstream asset tests; RCEF does not synthesize geometry.
