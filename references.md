# Public source references

SPDX-License-Identifier: CC-BY-SA-4.0

Generated from [evidence/sources.toml](evidence/sources.toml) by `scripts/export_references.py`. Edit the TOML, not this file. Each entry identifies the exact bytes RCEF verified: the URL, the revision (or `retrieval-digest` for documentation pages that change), the retrieval date and the SHA-256. `scripts/verify_sources.py` downloads them again. Provider names and enums are used as facts, with attribution. Source prose, figures and algorithms are not included.

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

Unified Expressions shape descriptions; MouthClosed is defined relative to JawOpen.

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

## rcef_canonical_v1

Original RCEF canonical expression vocabulary, version 1 (draft): signal definitions, groups, the meaning of 0 and 1, the definitions audit and the assumptions each hop states; no measured gain, response curve or cross-provider equivalence.

- Original authorship: RCEF contributors (2026)
- License or terms: CC-BY-SA-4.0
- Locator: docs/canonical-set.md; docs/canonical-set-audit.md; data/canonical_expression.toml

## calibration.viseme-poses.rocketbox-features

RCEF calibration record viseme-poses.rocketbox-features, version 1 (calibrated_software): the pose of each canonical viseme class in canonical expression signals, with each Left and Right pair tied, fitted to the META viseme shapes of 18 Microsoft Rocketbox rigs in their own ARKit shapes, with a perceptual gate (visible mouth features with frozen tolerances) for bilabial, vowel_close_rounded, vowel_mid_spread and alveolar_sibilant; frozen before a held-out evaluation on 4 other Rocketbox rigs (Female_Adult_09, Female_Adult_15, Male_Adult_08 and Male_Adult_15); 11 of 15 classes pass, 7 by their shape and 4 by the perceptual gate. A fit to the geometry of example rigs, not a measurement of any tracker.

- Original authorship: RCEF contributors (2026); fitted to the Microsoft Rocketbox avatar library (MIT)
- License or terms: CC-BY-SA-4.0
- Locator: calibration/viseme-poses.rocketbox-features.cal; calibration/FREEZES; tools/calibration/viseme_rigs.json

## facs_wikipedia

FACS code numbers, short names, table membership, intensity letters, modifier letters and visibility-region names used as facts; no prose copied; not the FACS manual.

- Source: [facs_wikipedia](https://en.wikipedia.org/w/index.php?title=Facial_Action_Coding_System&oldid=1357638399&action=raw)
- Revision: `1357638399`
- Retrieved: 2026-10-28
- SHA-256: `04e85bb6602305aa367c5d2b3f3f4fc4b78d8c213e73303f2694225453f5733a`
- License or terms: CC-BY-SA-4.0
- Locator: raw wikitext lines 69-75 (intensity letters), 78 (side modifiers), 82-142 (main codes), 144-176 (head movement codes), 178-204 (eye movement codes), 206-221 (visibility codes) and 223-284 (gross behavior codes)

## facs_hager_2002

The FACS publisher's page on the 2002 manual lists the re-assignment of the old 41, 42 and 44 scores to intensities of AU 43, and revised scoring for AUs 25, 26 and 27 with intensities; it gives no letters. Another public page, at Carnegie Mellon, names 41, 42 and 43 instead and does not name 44; RCEF takes no value from either.

- Source: [facs_hager_2002](https://web.archive.org/web/20081218070149id_/http://www.face-and-emotion.com:80/dataface/facs/new_version.jsp)
- Revision: `Internet Archive capture 20081218070149, original bytes (id_)`
- Retrieved: 2026-10-29
- SHA-256: `12d6e115d6dcde65097df99005a938b25170d842e7597b1db1ab2da5946e5b1f`
- License or terms: reference only; source prose not redistributed
- Locator: lines 204-205 (list of features of the 2002 manual)

## rocketbox_avatars

The Microsoft Rocketbox avatars have facial blendshapes, 48 of them FACS shapes, and the README credits Matias Volonte with creating the blendshapes. The 48 AU_* shape names (code number, optional side letter, name) are read as facts from the facial FBX files that examples/rigs.py pins (Female_Adult_01 and Male_Adult_01, which have the same 48 names).

- Source: [rocketbox_avatars](https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/0943055db6ec570bcef9f2c8b41c9e5467c808f9/README.md)
- Revision: `0943055db6ec570bcef9f2c8b41c9e5467c808f9`
- Retrieved: 2026-10-29
- SHA-256: `bcf8013e3d5817a5dee5d1770b9943278189cd76b2d9b2abc243db99b703ecd6`
- License or terms: MIT
- Locator: README lines 21 (48 FACS) and 55 (blendshape credit); the shape names from the pinned facial FBX files

## pyfeat_au_reference

Py-Feat's action-unit reference relates FACS codes to muscles and, approximately by its own statement, to ARKit shapes; cited in audit notes only, not on any hop.

- Source: [pyfeat_au_reference](https://raw.githubusercontent.com/cosanlab/py-feat/4ebb4ecade769d02e962d18c5e6704f01045d931/docs/pages/au_reference.md)
- Revision: `4ebb4ecade769d02e962d18c5e6704f01045d931`
- Retrieved: 2026-10-29
- SHA-256: `c8d6281bae16c154b39e1cdf3df810f46ebc0af065d9ec0920154223d96ed35b`
- License or terms: MIT
- Locator: lines 13 (the ARKit column is approximate), 74, 87-91, 100, 106-109 and 118

## ozel_arkit_facs

Melinda Ozel's ARKit to FACS cheat sheet relates ARKit shapes to FACS codes, with notes on mouthShrugUpper and on eye-look pairs; cited in audit notes only, paraphrased, not on any hop.

- Source: [ozel_arkit_facs](https://web.archive.org/web/20261010185714id_/https://melindaozel.com/ARKit-to-FACS-cheat-sheet/)
- Revision: `Internet Archive capture 20261010185714, original bytes (id_); page modified 2026-02-19`
- Retrieved: 2026-10-29
- SHA-256: `2139bc1752ac8074f1d23a40f65ff79dc4850d367a9eeaca929f1366b9e479b1`
- License or terms: reference only; (c) 2020-2026 Melinda Ozel, all rights reserved; source prose not redistributed
- Locator: HTML lines 698-704 (eyeBlink), 788 (eye-look pairs), 1048-1076 (mouthShrugUpper) and 1320-1326 (jawOpen)

## rcsf_proposal

RCSF design aims: coverage of most distinct joints across the analysed standards, format neutrality, and neutral territory for standards organizations; cited for RCEF's aims and its stated departures, not copied.

- Source: [rcsf_proposal](https://raw.githubusercontent.com/MetaverseStandards/RCSF/f6c3ea8a00d4901496326b4a6fe6a24913a563c6/proposal.md)
- Revision: `f6c3ea8a00d4901496326b4a6fe6a24913a563c6`
- Retrieved: 2026-10-29
- SHA-256: `7f7c771789140e78fb71b24e67ff1460eb59033d28054622b8206fe08c8dda99`
- License or terms: CC-BY-SA-4.0 (stated in the RCSF README)
- Locator: lines 70, 74 and 107

## xr_fb2_fig_eyes_closed_l

FB2 front-view figure for EYES_CLOSED_L: the eye on the viewer's right closes, so FB2 names sides from the subject's own face; cited, not copied.

- Source: [xr_fb2_fig_eyes_closed_l](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_FB_Face_Expression_2_Eyes_Closed_L.png)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `78456d18833a58cdfe5edb54aeb31c2e5a3601de32f78d74b3f4b33a367efb12`
- License or terms: CC-BY-4.0
- Locator: whole image; referenced from fb_face_tracking2.adoc line 584

## xr_fb2_fig_eyes_look_left_l

FB2 front-view figure for EYES_LOOK_LEFT_L: the eye on the viewer's right turns toward the viewer's right, the temple, so the subject's own left eye looks out; cited, not copied.

- Source: [xr_fb2_fig_eyes_look_left_l](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_FB_Face_Expression_2_Eyes_Look_Left_L.png)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `30794e175a00ff7c0d13e8a537d75315c4477359dae910ceef872f49dbe3b8cb`
- License or terms: CC-BY-4.0
- Locator: whole image; referenced from fb_face_tracking2.adoc line 608

## xr_fb2_fig_mouth_left

FB2 front-view figure for MOUTH_LEFT: the mouth moves toward the viewer's right, the subject's own left; cited, not copied.

- Source: [xr_fb2_fig_mouth_left](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_FB_Face_Expression_2_Mouth_Left.png)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `07465af6b55f6fbc835b05b3d51401300705b24d115ca8425d1d6d1a9272d4f0`
- License or terms: CC-BY-4.0
- Locator: whole image; referenced from fb_face_tracking2.adoc line 834

## vrcft_fig_eyeclosedleft

VRCFaceTracking reference figure for EyeClosedLeft: the eye on the viewer's right closes, so Unified Expressions names sides from the subject's own face; cited, not copied.

- Source: [vrcft_fig_eyeclosedleft](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/img/avatar/avatar_ref_eyeclosedleft.png)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-29
- SHA-256: `128dc5f1dad57f703c57aded753bbaa621a46d28fbbed795f5cf5b62f98b3cbb`
- License or terms: reference only; source figure not redistributed
- Locator: whole image; referenced from _unified-shape-table.mdx line 75

## vrcft_fig_eyelookoutleft

VRCFaceTracking reference figure for EyeLookOutLeft: the eye on the viewer's right turns toward the viewer's right, the temple; cited, not copied.

- Source: [vrcft_fig_eyelookoutleft](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/img/avatar/avatar_ref_eyelookoutleft.png)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-29
- SHA-256: `22fbb1ca0adefec555b8b86e5c317954b98de5efa97df5aba60c96a041583759`
- License or terms: reference only; source figure not redistributed
- Locator: whole image; referenced from _unified-shape-table.mdx line 50

## vrcft_fig_mouthupperleft

VRCFaceTracking reference figure for MouthUpperLeft: the upper lip moves toward the viewer's right, the subject's own left; cited, not copied.

- Source: [vrcft_fig_mouthupperleft](https://raw.githubusercontent.com/VRCFaceTracking/docs/3036f4668322f2364a918a885dc3a72c828359f3/docs/tutorial-avatars/tutorial-avatars-extras/img/avatar/avatar_ref_mouthupperleft.png)
- Revision: `3036f4668322f2364a918a885dc3a72c828359f3`
- Retrieved: 2026-10-29
- SHA-256: `60c5a1c618f10998ddae848868c9aa609b3711a040a927cee098478b53157cff`
- License or terms: reference only; source figure not redistributed
- Locator: whole image; referenced from _unified-shape-table.mdx line 365

## ipa_chart_kiel_2020

The IPA chart (revised to 2020), Kiel typeface: the symbol inventory and its places, manners, heights, backness and rounding; its text layer uses legacy font codes, so symbols are checked against the Doulos file.

- Source: [ipa_chart_kiel_2020](https://www.internationalphoneticassociation.org/IPAcharts/common_files/pdfs/pdfs_IPA_charts_archive/IPA_Kiel_2020.pdf)
- Revision: `2020 (the 2015/2005 symbol set with updated years)`
- Retrieved: 2026-10-29
- SHA-256: `52c7c15eeaaf40d517ab9a7d1142fe6604709b254830a36efb89b10ddac97647`
- License or terms: CC BY-SA 3.0 Unported at issue (both 2020 files); the IPA now states CC BY-SA 4.0 for the IPA Chart in IPA Kiel and all its subparts; RCEF's adapted fixture is CC-BY-SA-4.0 under BY-SA 3.0 section 4(b)
- Locator: chart sections and cells (pulmonic consonants, non-pulmonic consonants, other symbols, vowels, diacritics)

## ipa_chart_doulos_2020

The IPA chart (revised to 2020), Doulos SIL typeface: the 107 chart symbols, their places and manners, vowel heights, backness and rounding, and the diacritics used by the canonical viseme classes and tests/fixtures/ipa_chart_symbols.json.

- Source: [ipa_chart_doulos_2020](https://www.internationalphoneticassociation.org/IPAcharts/common_files/pdfs/pdfs_IPA_charts_archive/IPA_Doulos_2020.pdf)
- Revision: `2020 (the 2015/2005 symbol set with updated years)`
- Retrieved: 2026-10-29
- SHA-256: `63b09d419619a82f6458991415c50bcbcfd2ed4465da000d5e598431a9ba8912`
- License or terms: CC BY-SA 3.0 Unported at issue (both 2020 files); the IPA now states CC BY-SA 4.0 for the IPA Chart in IPA Kiel and all its subparts; RCEF's adapted fixture is CC-BY-SA-4.0 under BY-SA 3.0 section 4(b)
- Locator: chart sections and cells, for example "Pulmonic consonants, Fricative x Dental" (tests/fixtures/ipa_chart_symbols.json)

## polly_license

Licence of the archived Amazon Polly developer guide (CC BY-SA 4.0 for the documentation); the archive is out of date relative to the live AWS documentation, which is not cited.

- Source: [polly_license](https://raw.githubusercontent.com/awsdocs/amazon-polly-developer-guide/97b0d81ab6468129948d48beb767da1d692f2f27/LICENSE)
- Revision: `97b0d81ab6468129948d48beb767da1d692f2f27`
- Retrieved: 2026-10-29
- SHA-256: `a39a4b3d0f411a8217b7c6dd35dc8b06003784ce32d3593d0d2d780a7e9c2f8c`
- License or terms: CC-BY-SA-4.0
- Locator: LICENSE

## polly_ph_table_en_us

Archived Amazon Polly en-US phoneme and viseme table: IPA phonemes and the viseme each belongs to; a roadmap source only.

- Source: [polly_ph_table_en_us](https://raw.githubusercontent.com/awsdocs/amazon-polly-developer-guide/97b0d81ab6468129948d48beb767da1d692f2f27/doc_source/ph-table-english-us.md)
- Revision: `97b0d81ab6468129948d48beb767da1d692f2f27`
- Retrieved: 2026-10-29
- SHA-256: `ec4c47270921bb094b5db3a2637ca34507ed10bc18b7f66a4db4b528087db6d7`
- License or terms: CC-BY-SA-4.0
- Locator: doc_source/ph-table-english-us.md, whole table

## wikipedia_roundedness

Lip rounding: the IPA clines of rounding and spreading (back unrounded vowels parallel to the front ones; close central vowels fully spread and closely rounded; open rounded vowels least rounded), protruded and compressed rounding, rounded glides; facts only, no prose copied.

- Source: [wikipedia_roundedness](https://en.wikipedia.org/w/index.php?title=Roundedness&oldid=1373837679&action=raw)
- Revision: `1373837679`
- Retrieved: 2026-10-29
- SHA-256: `a03d3afcd24c6fbac8cb3833a646dcbf9f207379eb425a85052c920347ac79d0`
- License or terms: CC-BY-SA-4.0
- Locator: raw wikitext lines 15-21 (clines), 52-56 (protrusion and compression), 85 (unrounded realisations)

## wikipedia_labialization

Labialization is written with superscript w; labialised postalveolar approximant listed for many dialects of English; facts only, no prose copied.

- Source: [wikipedia_labialization](https://en.wikipedia.org/w/index.php?title=Labialization&oldid=1379064613&action=raw)
- Revision: `1379064613`
- Retrieved: 2026-10-29
- SHA-256: `f877902cafe962bdb3ea1ae2bfcb20264301e4cf23fb5a6376aaf8b57bf3e2ff`
- License or terms: CC-BY-SA-4.0
- Locator: raw wikitext lines 20 and 512-514

## wikipedia_interdental

Interdental consonants: the extIPA bridge transcription, the advanced-alveolar alternative, sibilants not interdental, Australian laminal dentals; facts only, no prose copied.

- Source: [wikipedia_interdental](https://en.wikipedia.org/w/index.php?title=Interdental_consonant&oldid=1363969577&action=raw)
- Revision: `1363969577`
- Retrieved: 2026-10-29
- SHA-256: `92090b5ff4c86bc2d2ead471862d0e27db96da8ba75a4d4d52f67a254b983018`
- License or terms: CC-BY-SA-4.0
- Locator: raw wikitext lines 10, 12, 22 and 24

## wikipedia_linguolabial

Linguolabial consonants: the tongue tip or blade against the upper lip; the seagull diacritic on alveolar, dental and labial letters, and the earlier apical notation; facts only, no prose copied.

- Source: [wikipedia_linguolabial](https://en.wikipedia.org/w/index.php?title=Linguolabial_consonant&oldid=1374589336&action=raw)
- Revision: `1374589336`
- Retrieved: 2026-10-29
- SHA-256: `f680e1fc645ad2a49c50a085a321e4db3f6bd1520d4ee3ba6b3411a8ca069477`
- License or terms: CC-BY-SA-4.0
- Locator: raw wikitext lines 10, 19 and 21

## xr_visemes_fig_sil

META reference image for SIL, front view: lips together, jaw closed, relaxed; cited, not copied.

- Source: [xr_visemes_fig_sil](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_SIL.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `d5d03b8b194559b3ecbeede8691d694d7af2466d95bc5a52bc9b540f829887f1`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_SIL.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 145

## xr_visemes_fig_dd

META reference image for DD, front view, shown in isolation: teeth close and visible; cited, not copied.

- Source: [xr_visemes_fig_dd](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_DD.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `d06beb076b091497c4afbc97344b096d7b447ffb55bfeff1b7fd346ac959e9bc`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_DD.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 173

## xr_visemes_fig_nn

META reference image for NN, front view, shown in isolation: teeth close and visible; cited, not copied.

- Source: [xr_visemes_fig_nn](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_NN.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `9a9f7416dbdbaad296bc4acc366ea67fdfca6809e475ebf3f601dec3b8272749`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_NN.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 201

## xr_visemes_fig_kk

META reference image for KK, front view, shown in isolation: teeth close and visible; cited, not copied.

- Source: [xr_visemes_fig_kk](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_KK.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `009eec02094c44b0381aabadbb32619b1d429e17633dc95cf5d69e66137b8281`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_KK.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 180

## xr_visemes_fig_rr

META reference image for RR, front view: lips slightly parted, no clear protrusion; cited, not copied.

- Source: [xr_visemes_fig_rr](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_RR.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `c4ce3b30790617267d98ecf74228cee33db5c9aa48448eac0513997aaadf1699`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_RR.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 208

## xr_visemes_fig_th

META reference image for TH, front view: lips parted, tongue tip visible at the teeth; cited, not copied.

- Source: [xr_visemes_fig_th](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_TH.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `6652003f64b032bd3faf9c0b2aac211798c562dcd775c2c2a99424515bd21d1c`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_TH.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 166

## xr_visemes_fig_rr_rot

META reference image for RR, three-quarter view: the lips sit slightly forward of SIL and IH, the lower lip slightly everted (a judgement on one speaker); cited, not copied.

- Source: [xr_visemes_fig_rr_rot](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_RR_rot.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `87cb5bc78a969e01780f401381b0866bc02cbd9b4f1dff27b049c0efa303f429`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_RR_rot.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 210

## xr_visemes_fig_ch_rot

META reference image for CH, three-quarter view: lips forward; cited, not copied.

- Source: [xr_visemes_fig_ch_rot](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_CH_rot.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `9a024434c87745822022bc3005a0e01101ed51ef60ffa85b8efd702672180d27`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_CH_rot.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 189

## xr_visemes_fig_ou_rot

META reference image for OU, three-quarter view: lips protruded and rounded; cited, not copied.

- Source: [xr_visemes_fig_ou_rot](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_OU_rot.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `7c33e83679353b8208c31060f189bdc28c713ea59f33f7d9b785d1b7bbf43614`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_OU_rot.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 245

## xr_visemes_fig_sil_rot

META reference image for SIL, three-quarter view: lips together, relaxed; cited, not copied.

- Source: [xr_visemes_fig_sil_rot](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/images/XR_META_Face_Tracking_Viseme_SIL_rot.jpg)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- Retrieved: 2026-10-29
- SHA-256: `7afe5bb9e061524b2a5bb04e1ed3d4ade3a1732b7eed73c3c98c26fc286b4740`
- License or terms: CC-BY-4.0 (REUSE sidecar XR_META_Face_Tracking_Viseme_SIL_rot.jpg.license: Copyright (c) 2021-2026 The Khronos Group Inc., SPDX-License-Identifier CC-BY-4.0)
- Locator: whole image; referenced from meta_face_tracking_visemes.adoc line 147

## bear_harvey_2017

Bear and Harvey, "Phoneme-to-viseme mappings: the good, the bad, and the ugly", Speech Communication 2017 (doi 10.1016/j.specom.2017.07.001): the published English vowel and consonant viseme maps that RCEF counts, their class counts, and which maps perform best on isolated words and on continuous speech.

- Source: [bear_harvey_2017](https://arxiv.org/pdf/1805.02934v1)
- Revision: `arXiv 1805.02934v1`
- Retrieved: 2026-10-29
- SHA-256: `20b32ad6054d6b96f7430e76046680475f3e37eba8a8b116555890ffadf492b9`
- License or terms: reference only; arXiv non-exclusive distribution licence 1.0; facts only, paraphrased
- Locator: Table 2 (vowel maps), Table 3 (consonant maps), Table 5 (class counts), Section 3.4 and Table 8 (best maps)

## fernandez_lopez_sukno_2017

Fernandez-Lopez and Sukno, 2017: Spanish viseme sets of different sizes compared for phoneme recovery; a bilabial fricative kept apart.

- Source: [fernandez_lopez_sukno_2017](https://arxiv.org/pdf/1704.08035v1)
- Revision: `arXiv 1704.08035v1`
- Retrieved: 2026-10-29
- SHA-256: `e21f7b39fd42def3dc29805ed9da95a92d47f20a678d49d002781483eb3e1ca9`
- License or terms: reference only; arXiv non-exclusive distribution licence 1.0; facts only, paraphrased
- Locator: viseme sets and results sections

## zhou_visemenet_2018

Zhou et al., "VisemeNet", 2018: 20 JALI-style viseme groups listed with IPA phonemes.

- Source: [zhou_visemenet_2018](https://arxiv.org/pdf/1805.09488v1)
- Revision: `arXiv 1805.09488v1`
- Retrieved: 2026-10-29
- SHA-256: `fcd9812cbe19600ceab9ab07e457443f57af8326e87c281c5c73de21319618f2`
- License or terms: reference only; arXiv non-exclusive distribution licence 1.0; facts only, paraphrased
- Locator: viseme group table

## jali_2016

Edwards et al., "JALI", SIGGRAPH 2016 (doi 10.1145/2897824.2925984): articulation constraints for visemes; tongue-only visemes do not move the lips; pauses usually leave the mouth open.

- Source: [jali_2016](https://www.dgp.toronto.edu/~elf/JALISIG16.pdf)
- Revision: `SIGGRAPH 2016 author copy`
- Retrieved: 2026-10-29
- SHA-256: `8a02957a91b705d4d357226d7db1fbeab59e8204308ac952ca7e34ea15190707`
- License or terms: reference only; (c) ACM; facts only, paraphrased
- Locator: section on viseme articulation constraints and coarticulation rules

## pubmed_owens_blazek_1985

Owens and Blazek 1985, PubMed abstract (PMID 4046579): composite consonant viseme groups seen by hearing-impaired and normal-hearing viewers; each group mixes voicing and nasality.

- Source: [pubmed_owens_blazek_1985](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=4046579&rettype=abstract&retmode=text)
- Revision: `PMID 4046579`
- Retrieved: 2026-10-29
- SHA-256: `f81bc090fd75705bc60b716cfe6cc0e14d20abcf129c621ca4bd7f412d877575`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_robert_ribes_1998

Robert-Ribes et al. 1998, PubMed abstract (PMID 9637049): for French oral vowels, rounding is perceived better than height in the visual channel, and backness is almost invisible.

- Source: [pubmed_robert_ribes_1998](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=9637049&rettype=abstract&retmode=text)
- Revision: `PMID 9637049`
- Retrieved: 2026-10-29
- SHA-256: `de6e2adbff10ee34a5426912724e57334c27e312812d847207927bdc8b071aad`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_montgomery_jackson_1983

Montgomery and Jackson 1983, PubMed abstract (PMID 6875099): visual vowel perception shows a lip spreading and rounding dimension and a tongue height dimension.

- Source: [pubmed_montgomery_jackson_1983](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=6875099&rettype=abstract&retmode=text)
- Revision: `PMID 6875099`
- Retrieved: 2026-10-29
- SHA-256: `649109c5c5a11f2c91bc67133e4acb5db54438fd1972c30512e8cb577d6b6ed4`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_benguerel_pichora_fuller_1982

Benguerel and Pichora-Fuller 1982, PubMed abstract (PMID 7162162): labial, rounded and alveolar or palatal place carry more visual information than continuancy.

- Source: [pubmed_benguerel_pichora_fuller_1982](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=7162162&rettype=abstract&retmode=text)
- Revision: `PMID 7162162`
- Retrieved: 2026-10-29
- SHA-256: `0ff5199ebf97428d6954f87675e37a4f6e1b71a8ad4cd0dba223fe9bdbbd1621`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_auer_bernstein_1997

Auer and Bernstein 1997, PubMed abstract (PMID 9407662): with about 12 phonemic equivalence classes, most words are visually similar to only a few others.

- Source: [pubmed_auer_bernstein_1997](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=9407662&rettype=abstract&retmode=text)
- Revision: `PMID 9407662`
- Retrieved: 2026-10-29
- SHA-256: `59e5004fd776cae10de6a5fb8f48401c17d3ba3961a9f94c851a6f9077a507c5`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_valkenier_2012

Valkenier et al. 2012, PubMed abstract (PMID 22992710): for Dutch front vowels, lip rounding is carried mainly by the visual channel and height by the auditory channel.

- Source: [pubmed_valkenier_2012](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22992710&rettype=abstract&retmode=text)
- Revision: `PMID 22992710`
- Retrieved: 2026-10-29
- SHA-256: `e79c8fa4d577efec3f784c14190194a60da413d9bd75e1e64955a1589a8c21a5`
- License or terms: reference only; abstract (c) publisher; facts only, paraphrased
- Locator: abstract

## pubmed_havenhill_do_2018

Havenhill and Do 2018, PubMed abstract (PMID 29867686): some Northern Cities speakers produce /ɔ/ with unround lips, which is perceptually weaker than rounded /ɔ/.

- Source: [pubmed_havenhill_do_2018](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29867686&rettype=abstract&retmode=text)
- Revision: `PMID 29867686`
- Retrieved: 2026-10-29
- SHA-256: `c352ee8b7be8a2e73c2f449f2ded7a5041e85a5fbe257e47667dc3209edd56a6`
- License or terms: reference only; open access (CC BY per the journal policy, not verified on the article page); facts only, paraphrased
- Locator: abstract
