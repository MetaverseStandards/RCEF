# Public source references

SPDX-License-Identifier: CC-BY-SA-4.0

Generated from [evidence/sources.toml](evidence/sources.toml) by `scripts/export_references.py`; edit the TOML, not this file. Each entry gives the exact bytes RCEF verified: the URL, the revision (or `retrieval-digest` for mutable documentation pages), the retrieval date and the SHA-256. `scripts/verify_sources.py` re-fetches them. Provider names and enums are extracted as facts with attribution; source prose, figures and algorithms are not bundled.

## rcsf_readme

Pinned survey/authoring baseline and provider presentation; historical parity reference.

- Source: [rcsf_readme](https://raw.githubusercontent.com/MetaverseStandards/RCSF/f6c3ea8a00d4901496326b4a6fe6a24913a563c6/README.md)
- Revision: `f6c3ea8a00d4901496326b4a6fe6a24913a563c6`
- Retrieved: 2026-10-07
- SHA-256: `a4726117f9de285a8ab66651b6e33f31195c67f55a9db72c028b3d60a6100ce1`
- License or terms: CC-BY-SA-4.0 (stated in the README)
- Locator: README sections

## rcsf_checker

Pinned baseline checker provides table join and comparison behavior; no runtime evaluator claim.

- Source: [rcsf_checker](https://raw.githubusercontent.com/MetaverseStandards/RCSF/f6c3ea8a00d4901496326b4a6fe6a24913a563c6/join_csv.py)
- Revision: `f6c3ea8a00d4901496326b4a6fe6a24913a563c6`
- Retrieved: 2026-10-07
- SHA-256: `a49573c0d18a1bfc52d9f9f5cbff669c978295f11c442ba00fa2c359cab21e47`
- License or terms: no file-level notice; the RCSF README states CC-BY-SA-4.0; cited, not copied
- Locator: join_csv.py

## apple_blendshapes

52 coefficient identifiers; native coefficient domain 0..1 and face-relative sides.

- Source: [apple_blendshapes](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/blendshapelocation.json)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-26
- SHA-256: `c7a074ab7e8b14bfe15d727a8a856a8bdf8f83cb84f1b08d0f8b4a2b458300e3`
- License or terms: reference only; source prose not redistributed
- Locator: topicSections except initializer; Discussion

## apple_eye

Eye pose is a transform, a separate interface from eyelid movement coefficients.

- Source: [apple_eye](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/lefteyetransform.json)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-26
- SHA-256: `637d94fc9a384aaadd68c5f4e6a3c3e1d2837fb09b1b0a6dfb2471546b7c37e0`
- License or terms: reference only; source prose not redistributed
- Locator: declarations and Discussion

## mediapipe

kBlendshapeNames contains 52 labels including _neutral and excluding tongueOut; scores returned without threshold filtering.

- Source: [mediapipe](https://raw.githubusercontent.com/google-ai-edge/mediapipe/f6988c4769278bde600efd488dfc8645432dc92b/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc)
- Revision: `f6988c4769278bde600efd488dfc8645432dc92b`
- Retrieved: 2026-10-07
- SHA-256: `a3826ad2738315f1e046b36fd883825980e151db677e53d21ff35eaff64e4bd3`
- License or terms: Apache-2.0
- Locator: kBlendshapeNames; ConvertTensorToBlendshapes

## xr_fb

FB weight ordering, separate eye-following validity, upper/lower confidence and XrTime; numeric weight bounds not explicit here.

- Source: [xr_fb](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/fb/fb_face_tracking.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-07
- SHA-256: `2676aa103e48595031d368ef3a7301a9c2b006f1d6eee9f1eca03f3132a78cb9`
- License or terms: CC-BY-4.0
- Locator: XrFaceExpressionWeightsFB; XrFaceExpressionStatusFB; confidence areas

## xr_fb2

FB2 0..1 weights, tongue entries, two validity flags, confidence/time/data source and directional rotation fractions.

- Source: [xr_fb2](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/fb/fb_face_tracking2.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-07
- SHA-256: `db7c6e3a0dee91f5bc7397830405e8596fe19e5eafc7608912b807163ab9a2ef`
- License or terms: CC-BY-4.0
- Locator: XrFaceExpressionWeights2FB; Conventions of facial expressions; eye rotation paragraph

## xr_visemes

Optional FB2-dependent extension; 15 probabilities including silence; valid sum 1 and independent validity.

- Source: [xr_visemes](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/meta/meta_face_tracking_visemes.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-07
- SHA-256: `4d1f4ccf48364f0ff37bf68496ac939521dcb6fe64f797e8201b05e159f00678`
- License or terms: CC-BY-4.0
- Locator: Overview; XrFaceTrackingVisemesMETA; XrFaceTrackingVisemeMETA

## xr_registry

Exact FB63, FB2 70 and META15 identifiers and indices plus count sentinels and negotiation enums.

- Source: [xr_registry](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/registry/xr.xml)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-07
- SHA-256: `e9b6b0bb9e5100c56467ec80ae30b78ff36b4dcc8a332c269fa5e3e8429ed0aa`
- License or terms: Apache-2.0 OR MIT (SPDX header of xr.xml); identifiers extracted as facts
- Locator: enums XrFaceExpressionFB, XrFaceExpression2FB, XrFaceTrackingVisemeMETA

## vrcft_enum

UnifiedExpressions has 88 active transport names and Max sentinel; commented eye names use a separate structure.

- Source: [vrcft_enum](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedExpressions.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- Retrieved: 2026-10-07
- SHA-256: `0db0ebbdcc4a9d325e28d0386daf7d099da44ab549d84140df505d08035c67e2`
- License or terms: Apache-2.0
- Locator: UnifiedExpressions enum before SRanipal_LipShape_v2

## vrcft_data

Raw single-eye Gaze, pupil millimetres and openness initialization 1; combined normalization/averaging, recovery 0.5, byte clamping/quantization and reserved bytes.

- Source: [vrcft_data](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Data/UnifiedData.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- Retrieved: 2026-10-07
- SHA-256: `9517612c1bdf60e61ce4e0309d1c14592cd4e2ce0a467a87562945d68dc36412`
- License or terms: Apache-2.0
- Locator: UnifiedSingleEyeData; UnifiedEyeData.Combined/CopyTo; UnifiedTrackingData.CopyTo

## vrcft_license

Pinned VRCFT repository source license is Apache-2.0.

- Source: [vrcft_license](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/LICENSE)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- Retrieved: 2026-10-07
- SHA-256: `ee667e443a1119a143331d985b8aa9daa770f2f2068cb7bb9e0d36d9802b705c`
- License or terms: Apache-2.0
- Locator: LICENSE

## vrcft_artist

Artist tables contain 102 base and 42 blended names; component lists, unsupported footnotes and side/direction contradictions retained.

- Source: [vrcft_artist](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-07
- SHA-256: `10f91ba8ed0c534139d3a1860b52f58978da80b401825896bfeb92af34c2a245`
- License or terms: documentation with no published license; reference only, source prose not redistributed
- Locator: #ue-base-shapes; #ue-blended-shapes; footnote 1

## godot_enum

BlendShapeEntry declares 102 base and 41 blended names plus FT_MAX; enum availability is not device support.

- Source: [godot_enum](https://raw.githubusercontent.com/godotengine/godot/e7b12e749220a75ef87e800e080bd2732ad46854/servers/xr/xr_face_tracker.h)
- Revision: `e7b12e749220a75ef87e800e080bd2732ad46854`
- Retrieved: 2026-10-07
- SHA-256: `e8d4144834598faa862262c41e246d932e07be5d52d9116042a75618c683a2a3`
- License or terms: MIT
- Locator: BlendShapeEntry

## godot_setters

Godot initializes array to zero and setters store supplied values without numeric clamping.

- Source: [godot_setters](https://raw.githubusercontent.com/godotengine/godot/e7b12e749220a75ef87e800e080bd2732ad46854/servers/xr/xr_face_tracker.cpp)
- Revision: `e7b12e749220a75ef87e800e080bd2732ad46854`
- Retrieved: 2026-10-07
- SHA-256: `4f01af298dba233495893d5e6cc9bd5facfd7f6952ac4cb08ad6837af5a2bebf`
- License or terms: MIT
- Locator: set_blend_shape; set_blend_shapes; header array initialization

## vrm_expressions

18 optional presets; model-specific bindings, isBinary >0.5, procedural overrides and custom names.

- Source: [vrm_expressions](https://raw.githubusercontent.com/vrm-c/vrm-specification/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/expressions.md)
- Revision: `94e82dd346fa6cf0337c4421728640e5252dd38e`
- Retrieved: 2026-10-07
- SHA-256: `e1d27d4717de6625189d01abbe77c46550ac71d4f1caed7ed5dccad1a6ebd0c9`
- License or terms: reference only; source prose not redistributed
- Locator: Preset Expressions; Expression; Procedural override; binding tables

## vrm_lookat

LookAt bone/expression surfaces and range maps are model-specific; one line of sight cannot express independent divergent eyes.

- Source: [vrm_lookat](https://raw.githubusercontent.com/vrm-c/vrm-specification/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/lookAt.md)
- Revision: `94e82dd346fa6cf0337c4421728640e5252dd38e`
- Retrieved: 2026-10-07
- SHA-256: `859e7c5d1d56ee7b0d795826c1bd70df628e8fe337392f808e788a7dbc714ee8`
- License or terms: reference only; source prose not redistributed
- Locator: Overview; RangeMap; Interpretation when type is expression

## roblox_controls

50 float FaceControls in domain 0..1; joint mapping and 17 required pose list A.

- Source: [roblox_controls](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/reference/engine/classes/FaceControls.yaml)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- Retrieved: 2026-10-07
- SHA-256: `ef2e9dd53dac6acc5deaf1f2b633fbbf1b24530c932c910755c16ae9de4c208b`
- License or terms: CC-BY-4.0
- Locator: properties; Animatable Heads in the Marketplace

## roblox_requirements

Different 17 required poses list B and 5 validation actions; authority conflict unresolved.

- Source: [roblox_requirements](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/avatar/dynamic-heads/specifications.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- Retrieved: 2026-10-07
- SHA-256: `37e9e1bfba7448ec72a12eb8e4e7b00240fbd2eb54e46d34712dcf57e1c262c9`
- License or terms: CC-BY-4.0
- Locator: #facs-poses

## roblox_authoring

Neutral Frame 0, named pose-to-joint mappings and combination corrective differences; host execution deferred.

- Source: [roblox_authoring](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/art/characters/facial-animation/create-basic-heads.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- Retrieved: 2026-10-07
- SHA-256: `2b156475fab59d86a81a12995c5e68ab630c769c1d5e1e550072f99ba8399f28`
- License or terms: CC-BY-4.0
- Locator: #posing; #combination-poses; #map-each-pose

## roblox_poses

50 pose headings cross-check FaceControls identifiers and include list B required-pose notices.

- Source: [roblox_poses](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/avatar/dynamic-heads/facs-poses-reference.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- Retrieved: 2026-10-07
- SHA-256: `6c7ed3b647e5bdf0720cdf964ae3c99be789166f60543187ef1887eec4f283a2`
- License or terms: CC-BY-4.0
- Locator: pose headings

## roblox_license

Roblox creator documentation source license is CC-BY-4.0.

- Source: [roblox_license](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/LICENSE)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- Retrieved: 2026-10-07
- SHA-256: `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411`
- License or terms: CC-BY-4.0
- Locator: LICENSE

## gltf_morph

Morph weight coefficients are not generally limited to 0..1; relative Basis and defaults are separate from tracked signals.

- Source: [gltf_morph](https://raw.githubusercontent.com/KhronosGroup/glTF/8e691206fa2e981fc3b8c8bc57e671595576c971/specification/2.0/Specification.adoc)
- Revision: `8e691206fa2e981fc3b8c8bc57e671595576c971`
- Retrieved: 2026-10-07
- SHA-256: `c305d1b0ea93c7eb101059db09ae4687c56fe5388c6655cd9bf83d44b2932664`
- License or terms: CC-BY-4.0 (SPDX header of Specification.adoc)
- Locator: #morph-targets; #applying-morph-targets

## vrcft_parameters

127 publicly listed parameter rows: 124 numeric parameters and 3 activity flags; optional prefixes, units and compositions.

- Source: [vrcft_parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-07
- SHA-256: `1f0b92e5955ef08fd772da3624cc492cf2cd6a6242fd63a7452087abf86678c2`
- License or terms: documentation with no published license; reference only, source prose not redistributed
- Locator: 16 parameter tables; Tracking Active Parameters

## vrcft_float

Float avatar parameter surface; documentation does not establish physical calibration equivalence.

- Source: [vrcft_float](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/float)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-07
- SHA-256: `54b585f8f9170da70caa3a679fbe120ba76204fe406106130b61ccd3f742df5e`
- License or terms: documentation with no published license; reference only, source prose not redistributed
- Locator: Float Parameters

## vrcft_binary

Binary parameter encoding surface and sign parameter evidence; numeric transforms remain non-executable inventory.

- Source: [vrcft_binary](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/binary)
- Revision: `retrieval-digest`
- Retrieved: 2026-10-07
- SHA-256: `9d8dae1b944d8cd877147800517a11ea9a7e2dd04344e63861df9248e4686c68`
- License or terms: documentation with no published license; reference only, source prose not redistributed
- Locator: Binary Parameters

## rcef_definitions

Original provider-calibrated scalar projections and synthetic affine/bilateral fixture definitions; no cross-provider equivalence.

- Original authorship: RCEF contributors (2026)
- License or terms: CC-BY-SA-4.0
- Locator: data/canonical.toml; fixtures/mapping_samples.json

## vrcft_docs_arkit

VRCFT documentation table relating Unified Expressions shapes to ARKit coefficients by name.

- Source: [vrcft_docs_arkit](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/arkit.mdx)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-26
- SHA-256: `fa0c5218c2d4350b605e189386e59960f45212beceef18ded56bae6357a2266d`
- License or terms: reference only; source prose not redistributed
- Locator: ARKit Comparison table

## vrcft_docs_movement

VRCFT documentation table relating Unified Expressions shapes to Meta Movement (FB2) weights by name; contains known side and spelling errors.

- Source: [vrcft_docs_movement](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/meta-movement.mdx)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-26
- SHA-256: `d20c3f2e4c02eeb702137e87ceeab007b3b00ea960527747616ad61a3d3f603a`
- License or terms: reference only; source prose not redistributed
- Locator: Meta Movement comparison table

## vrcft_docs_overview

VRCFT overview table across Unified Expressions, ARKit, SRanipal and Meta Movement; bold rows are blended shapes; SRanipal mouth closure negates jaw open.

- Source: [vrcft_docs_overview](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/overview.mdx)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-26
- SHA-256: `1b0044b39e4a1b44dca46678ad3c34464f76a3b2fa086ba72e417ce4eafae80b`
- License or terms: reference only; source prose not redistributed
- Locator: Standard Comparison Table; legend

## vrcft_docs_shapes

Unified Expressions shape descriptions; MouthClosed closes the mouth in relation to JawOpen.

- Source: [vrcft_docs_shapes](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/_unified-shape-table.mdx)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-26
- SHA-256: `208dce0a6bfdb9e5139de3933c26b0a4f0a5cefb9030d60023f17024cabc2dcb`
- License or terms: reference only; source prose not redistributed
- Locator: MouthClosed row

## vrcft_code_parameters

VRCFaceTracking computes combined parameters (brow inner up, cheek puff, lip suck, lip funnel, lip pucker) as the mean of their Unified Expressions parts.

- Source: [vrcft_code_parameters](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedExpressionsParameters.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- Retrieved: 2026-10-26
- SHA-256: `f00131c515a8778cc1372aa79372eb3c1171cca46307c8d16b507ccdcf42c9eb`
- License or terms: Apache-2.0
- Locator: v2/BrowInnerUp; v2/CheekPuffSuck; v2/LipSuckUpper, LipSuckLower; v2/LipFunnel; v2/LipPucker

## godot_vendors_fb2

Godot OpenXR vendors plugin maps FB2 weights to Godot face-tracker shapes, directly or as the mean of two shapes.

- Source: [godot_vendors_fb2](https://raw.githubusercontent.com/GodotVR/godot_openxr_vendors/b0654f162448ddf1519eb2826b5b69dda10900b9/plugin/src/main/cpp/extensions/openxr_fb_face_tracking_extension.cpp)
- Revision: `b0654f162448ddf1519eb2826b5b69dda10900b9`
- Retrieved: 2026-10-26
- SHA-256: `fd53cd284527bc544ff51eb60ed1aef28fce0a5a22c0b9a74a28454f91d65789`
- License or terms: MIT
- Locator: average(); weight mapping block

## godot_face_modifier

Godot blend-shape name table relating face-tracker shapes to Unified Expressions, ARKit, SRanipal and Meta names.

- Source: [godot_face_modifier](https://raw.githubusercontent.com/godotengine/godot/e7b12e749220a75ef87e800e080bd2732ad46854/scene/3d/xr/xr_face_modifier_3d.cpp)
- Revision: `e7b12e749220a75ef87e800e080bd2732ad46854`
- Retrieved: 2026-10-26
- SHA-256: `6b2c8305a0d8067f6a8f1e90544cbcab6895a0d0207b8a3c3e0ff4fe51db918d`
- License or terms: MIT
- Locator: find_face_blend_shape blend_map

## ict_facekit

ICT-FaceKit relates FACS action units to ARKit-named shapes, with brow-inner and cheek-puff split per side.

- Source: [ict_facekit](https://raw.githubusercontent.com/USC-ICT/ICT-FaceKit/da5f95a607f5e6b37755b38d3385d7f2853732e5/README.md)
- Revision: `da5f95a607f5e6b37755b38d3385d7f2853732e5`
- Retrieved: 2026-10-26
- SHA-256: `614116987854431bbdadbf7772f7352edeeca55580f62021dccb78aaf76febf6`
- License or terms: MIT
- Locator: FACS unit table

## vrcft_simple_expressions

VRCFaceTracking defines its simple BrowDown as 0.75 BrowLowerer + 0.25 BrowPinch and MouthSmile as 0.8 MouthCornerPull + 0.2 MouthCornerSlant.

- Source: [vrcft_simple_expressions](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedSimpleExpressions.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- Retrieved: 2026-10-26
- SHA-256: `662030f71b3ea1cb1e248c0b89e2f28861c714152874bfd4dc5a02ae96006a22`
- License or terms: Apache-2.0
- Locator: UnifiedSimpleExpressions enum comments; UnifiedSimplifier.ExpressionMap BrowDown and MouthSmile entries

## mediapipe_blendshape_card

MediaPipe's Blendshape V2 model card: 52 blendshape coefficients in [0, 1] predicted from 146 FaceMesh landmarks; licensed under Apache License 2.0; trained on lab-captured multi-view reconstructions of human subjects with blendshapes transferred from an artist-designed canonical mesh.

- Source: [mediapipe_blendshape_card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf)
- Retrieved: 2026-10-27
- SHA-256: `c8e9cf60a39998f4b341740623917590e050d1c97004e2de4568d84e026445ae`
- License or terms: Apache-2.0
- Locator: Model specifications (Output(s)); Licensed under; Factors and subgroups (Instrumentation, Environments); Appendix (list of predicted blendshapes)

## mediapipe_face_landmarker

MediaPipe Face Landmarker model bundle (float16, version 1), holding face_detector, face_landmarks_detector and face_blendshapes models.

- Source: [mediapipe_face_landmarker](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task)
- Retrieved: 2026-10-27
- SHA-256: `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`
- License or terms: Apache-2.0
- Locator: face_blendshapes.tflite in the bundle
