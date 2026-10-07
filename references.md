# Public source references

SPDX-License-Identifier: CC-BY-SA-4.0

Exact bytes were fetched on 2026-10-07. Mutable documentation is pinned by retrieval digest; source code/specification repositories use the reviewed revisions. Provider names/enums are extracted as facts with attribution. Source prose, figures and algorithms are not bundled.

## rcsf_readme

Pinned survey/authoring baseline and provider presentation; historical parity reference.

- Source: [rcsf_readme](https://raw.githubusercontent.com/MetaverseStandards/RCSF/f6c3ea8a00d4901496326b4a6fe6a24913a563c6/README.md)
- Revision: `f6c3ea8a00d4901496326b4a6fe6a24913a563c6`
- SHA-256: `a4726117f9de285a8ab66651b6e33f31195c67f55a9db72c028b3d60a6100ce1`
- Locator: README sections

## rcsf_checker

Pinned baseline checker provides table join and comparison behavior; no runtime evaluator claim.

- Source: [rcsf_checker](https://raw.githubusercontent.com/MetaverseStandards/RCSF/f6c3ea8a00d4901496326b4a6fe6a24913a563c6/join_csv.py)
- Revision: `f6c3ea8a00d4901496326b4a6fe6a24913a563c6`
- SHA-256: `a49573c0d18a1bfc52d9f9f5cbff669c978295f11c442ba00fa2c359cab21e47`
- Locator: join_csv.py

## apple_blendshapes

52 coefficient identifiers; native coefficient domain 0..1 and face-relative sides.

- Source: [apple_blendshapes](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/blendshapelocation.json)
- Revision: `retrieval-digest`
- SHA-256: `50691c512eedecaa3e54b73f313816409ff47b8b1bd3628460ca2c096903009b`
- Locator: topicSections except initializer; Discussion

## apple_eye

Eye pose is a transform, a separate interface from eyelid movement coefficients.

- Source: [apple_eye](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/lefteyetransform.json)
- Revision: `retrieval-digest`
- SHA-256: `74d13ebf8d550d9052e6d0f051c763d72b5c8e32ec2ce325a725271964cb918e`
- Locator: declarations and Discussion

## mediapipe

kBlendshapeNames contains 52 labels including _neutral and excluding tongueOut; scores returned without threshold filtering.

- Source: [mediapipe](https://raw.githubusercontent.com/google-ai-edge/mediapipe/f6988c4769278bde600efd488dfc8645432dc92b/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc)
- Revision: `f6988c4769278bde600efd488dfc8645432dc92b`
- SHA-256: `a3826ad2738315f1e046b36fd883825980e151db677e53d21ff35eaff64e4bd3`
- Locator: kBlendshapeNames; ConvertTensorToBlendshapes

## xr_fb

FB weight ordering, separate eye-following validity, upper/lower confidence and XrTime; numeric weight bounds not explicit here.

- Source: [xr_fb](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/fb/fb_face_tracking.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- SHA-256: `2676aa103e48595031d368ef3a7301a9c2b006f1d6eee9f1eca03f3132a78cb9`
- Locator: XrFaceExpressionWeightsFB; XrFaceExpressionStatusFB; confidence areas

## xr_fb2

FB2 0..1 weights, tongue entries, two validity flags, confidence/time/data source and directional rotation fractions.

- Source: [xr_fb2](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/fb/fb_face_tracking2.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- SHA-256: `db7c6e3a0dee91f5bc7397830405e8596fe19e5eafc7608912b807163ab9a2ef`
- Locator: XrFaceExpressionWeights2FB; Conventions of facial expressions; eye rotation paragraph

## xr_visemes

Optional FB2-dependent extension; 15 probabilities including silence; valid sum 1 and independent validity.

- Source: [xr_visemes](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/sources/chapters/extensions/meta/meta_face_tracking_visemes.adoc)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- SHA-256: `4d1f4ccf48364f0ff37bf68496ac939521dcb6fe64f797e8201b05e159f00678`
- Locator: Overview; XrFaceTrackingVisemesMETA; XrFaceTrackingVisemeMETA

## xr_registry

Exact FB63, FB2 70 and META15 identifiers and indices plus count sentinels and negotiation enums.

- Source: [xr_registry](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d/specification/registry/xr.xml)
- Revision: `5a82d45bc9e0adbaa24b6c4a3e5b6d50e08c887d`
- SHA-256: `e9b6b0bb9e5100c56467ec80ae30b78ff36b4dcc8a332c269fa5e3e8429ed0aa`
- Locator: enums XrFaceExpressionFB, XrFaceExpression2FB, XrFaceTrackingVisemeMETA

## vrcft_enum

UnifiedExpressions has 88 active transport names and Max sentinel; commented eye names use a separate structure.

- Source: [vrcft_enum](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Expressions/UnifiedExpressions.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- SHA-256: `0db0ebbdcc4a9d325e28d0386daf7d099da44ab549d84140df505d08035c67e2`
- Locator: UnifiedExpressions enum before SRanipal_LipShape_v2

## vrcft_data

Raw single-eye Gaze, pupil millimetres and openness initialization 1; combined normalization/averaging, recovery 0.5, byte clamping/quantization and reserved bytes.

- Source: [vrcft_data](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/VRCFaceTracking.Core/Params/Data/UnifiedData.cs)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- SHA-256: `9517612c1bdf60e61ce4e0309d1c14592cd4e2ce0a467a87562945d68dc36412`
- Locator: UnifiedSingleEyeData; UnifiedEyeData.Combined/CopyTo; UnifiedTrackingData.CopyTo

## vrcft_license

Pinned VRCFT repository source license is Apache-2.0.

- Source: [vrcft_license](https://raw.githubusercontent.com/benaclejames/VRCFaceTracking/6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35/LICENSE)
- Revision: `6432e6a8d85fa7ec5115fc725c6abcb6dbdd4f35`
- SHA-256: `ee667e443a1119a143331d985b8aa9daa770f2f2068cb7bb9e0d36d9802b705c`
- Locator: LICENSE

## vrcft_artist

Artist tables contain 102 base and 42 blended names; component lists, unsupported footnotes and side/direction contradictions retained.

- Source: [vrcft_artist](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes)
- Revision: `retrieval-digest`
- SHA-256: `10f91ba8ed0c534139d3a1860b52f58978da80b401825896bfeb92af34c2a245`
- Locator: #ue-base-shapes; #ue-blended-shapes; footnote 1

## godot_enum

BlendShapeEntry declares 102 base and 41 blended names plus FT_MAX; enum availability is not device support.

- Source: [godot_enum](https://raw.githubusercontent.com/godotengine/godot/e7b12e749220a75ef87e800e080bd2732ad46854/servers/xr/xr_face_tracker.h)
- Revision: `e7b12e749220a75ef87e800e080bd2732ad46854`
- SHA-256: `e8d4144834598faa862262c41e246d932e07be5d52d9116042a75618c683a2a3`
- Locator: BlendShapeEntry

## godot_setters

Godot initializes array to zero and setters store supplied values without numeric clamping.

- Source: [godot_setters](https://raw.githubusercontent.com/godotengine/godot/e7b12e749220a75ef87e800e080bd2732ad46854/servers/xr/xr_face_tracker.cpp)
- Revision: `e7b12e749220a75ef87e800e080bd2732ad46854`
- SHA-256: `4f01af298dba233495893d5e6cc9bd5facfd7f6952ac4cb08ad6837af5a2bebf`
- Locator: set_blend_shape; set_blend_shapes; header array initialization

## vrm_expressions

18 optional presets; model-specific bindings, isBinary >0.5, procedural overrides and custom names.

- Source: [vrm_expressions](https://raw.githubusercontent.com/vrm-c/vrm-specification/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/expressions.md)
- Revision: `94e82dd346fa6cf0337c4421728640e5252dd38e`
- SHA-256: `e1d27d4717de6625189d01abbe77c46550ac71d4f1caed7ed5dccad1a6ebd0c9`
- Locator: Preset Expressions; Expression; Procedural override; binding tables

## vrm_lookat

LookAt bone/expression surfaces and range maps are model-specific; one line of sight cannot express independent divergent eyes.

- Source: [vrm_lookat](https://raw.githubusercontent.com/vrm-c/vrm-specification/94e82dd346fa6cf0337c4421728640e5252dd38e/specification/VRMC_vrm-1.0/lookAt.md)
- Revision: `94e82dd346fa6cf0337c4421728640e5252dd38e`
- SHA-256: `859e7c5d1d56ee7b0d795826c1bd70df628e8fe337392f808e788a7dbc714ee8`
- Locator: Overview; RangeMap; Interpretation when type is expression

## roblox_controls

50 float FaceControls in domain 0..1; joint mapping and 17 required pose list A.

- Source: [roblox_controls](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/reference/engine/classes/FaceControls.yaml)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- SHA-256: `ef2e9dd53dac6acc5deaf1f2b633fbbf1b24530c932c910755c16ae9de4c208b`
- Locator: properties; Animatable Heads in the Marketplace

## roblox_requirements

Different 17 required poses list B and 5 validation actions; authority conflict unresolved.

- Source: [roblox_requirements](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/avatar/dynamic-heads/specifications.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- SHA-256: `37e9e1bfba7448ec72a12eb8e4e7b00240fbd2eb54e46d34712dcf57e1c262c9`
- Locator: #facs-poses

## roblox_authoring

Neutral Frame 0, named pose-to-joint mappings and combination corrective differences; host execution deferred.

- Source: [roblox_authoring](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/art/characters/facial-animation/create-basic-heads.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- SHA-256: `2b156475fab59d86a81a12995c5e68ab630c769c1d5e1e550072f99ba8399f28`
- Locator: #posing; #combination-poses; #map-each-pose

## roblox_poses

50 pose headings cross-check FaceControls identifiers and include list B required-pose notices.

- Source: [roblox_poses](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/content/en-us/avatar/dynamic-heads/facs-poses-reference.md)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- SHA-256: `6c7ed3b647e5bdf0720cdf964ae3c99be789166f60543187ef1887eec4f283a2`
- Locator: pose headings

## roblox_license

Roblox creator documentation source license is CC-BY-4.0.

- Source: [roblox_license](https://raw.githubusercontent.com/Roblox/creator-docs/a0fce044c480e8c580dc99b0645d127ad83a3873/LICENSE)
- Revision: `a0fce044c480e8c580dc99b0645d127ad83a3873`
- SHA-256: `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411`
- Locator: LICENSE

## gltf_morph

Morph weight coefficients are not generally limited to 0..1; relative Basis and defaults are separate from tracked signals.

- Source: [gltf_morph](https://raw.githubusercontent.com/KhronosGroup/glTF/8e691206fa2e981fc3b8c8bc57e671595576c971/specification/2.0/Specification.adoc)
- Revision: `8e691206fa2e981fc3b8c8bc57e671595576c971`
- SHA-256: `c305d1b0ea93c7eb101059db09ae4687c56fe5388c6655cd9bf83d44b2932664`
- Locator: #morph-targets; #applying-morph-targets

## vrcft_parameters

127 publicly listed parameter rows: 124 numeric parameters and 3 activity flags; optional prefixes, units and compositions.

- Source: [vrcft_parameters](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters)
- Revision: `retrieval-digest`
- SHA-256: `1f0b92e5955ef08fd772da3624cc492cf2cd6a6242fd63a7452087abf86678c2`
- Locator: 16 parameter tables; Tracking Active Parameters

## vrcft_float

Float avatar parameter surface; documentation does not establish physical calibration equivalence.

- Source: [vrcft_float](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/float)
- Revision: `retrieval-digest`
- SHA-256: `54b585f8f9170da70caa3a679fbe120ba76204fe406106130b61ccd3f742df5e`
- Locator: Float Parameters

## vrcft_binary

Binary parameter encoding surface and sign parameter evidence; numeric transforms remain non-executable inventory.

- Source: [vrcft_binary](https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/parameters/types/binary)
- Revision: `retrieval-digest`
- SHA-256: `9d8dae1b944d8cd877147800517a11ea9a7e2dd04344e63861df9248e4686c68`
- Locator: Binary Parameters

## rcef_definitions

Original provider-calibrated scalar projections and synthetic affine/bilateral fixture definitions; no cross-provider equivalence.

- Original authorship: RCEF contributors (2026)
- License: CC-BY-SA-4.0
- Locator: data/canonical.toml; fixtures/mapping_samples.json
