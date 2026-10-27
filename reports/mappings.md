# RCEF authored mappings

Pack: rcef.parity; data version: 0.2.0.

Generated from rcef.pack.json; SHA-256: 9e7450b57f365d665a926f3a95ae596d89325ef861cd6da2fa0440d0ca473c24.

Original RCEF data and arrangement: RCEF contributors (2026), CC-BY-SA-4.0. Existing provider attribution and source terms remain in ../THIRD_PARTY_NOTICES.md.

Rules preserve their declared direction, status, assumptions and losses. Unresolved rules are inventory records; they are not executable correspondences.

## Proposed rules

Proposed rules translate between providers. Each formula assumes the calibration stated in its rule below; losses list what the translation cannot carry.

| Mapping | Rule | Source → target | Formula | Losses | Evidence status |
| --- | --- | --- | --- | --- | --- |
| fb2.to_arkit | fb2_arkit.eyeBlinkLeft | openxr.fb2 → arkit.coefficient | eyeBlinkLeft = 1·XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.eyeBlinkRight | openxr.fb2 → arkit.coefficient | eyeBlinkRight = 1·XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.jawOpen | openxr.fb2 → arkit.coefficient | jawOpen = 1·XR_FACE_EXPRESSION2_JAW_DROP_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthClose | openxr.fb2 → arkit.coefficient | mouthClose = 1·XR_FACE_EXPRESSION2_LIPS_TOWARD_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; jaw-relative versus jaw-independent lip closure | proposed |
| fb2.to_arkit | fb2_arkit.browInnerUp | openxr.fb2 → arkit.coefficient | browInnerUp = 0.5·XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB + 0.5·XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.cheekPuff | openxr.fb2 → arkit.coefficient | cheekPuff = 0.5·XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB + 0.5·XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthSmileLeft | openxr.fb2 → arkit.coefficient | mouthSmileLeft = 1·XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 also pulls the corner back and laterally; ARKit describes upward movement only | proposed |
| fb2.to_arkit | fb2_arkit.mouthSmileRight | openxr.fb2 → arkit.coefficient | mouthSmileRight = 1·XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 also pulls the corner back and laterally; ARKit describes upward movement only | proposed |
| fb2.to_arkit | fb2_arkit.mouthShrugUpper | openxr.fb2 → arkit.coefficient | mouthShrugUpper = 1·XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 describes upward lip motion induced by the chin raiser; ARKit describes outward upper-lip movement | proposed |
| fb2.to_arkit | fb2_arkit.mouthShrugLower | openxr.fb2 → arkit.coefficient | mouthShrugLower = 1·XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 describes upward chin and lower-lip motion; ARKit describes outward lower-lip movement | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookOutLeft | openxr.fb2 → arkit.coefficient | eyeLookOutLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookInLeft | openxr.fb2 → arkit.coefficient | eyeLookInLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookOutRight | openxr.fb2 → arkit.coefficient | eyeLookOutRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookInRight | openxr.fb2 → arkit.coefficient | eyeLookInRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| visemes.to_vrm | visemes_vrm.aa | openxr.visemes → vrm.preset | aa = 1·XR_FACE_TRACKING_VISEME_AA_META | consonant visemes are dropped, so outputs no longer sum to 1; a viseme probability becomes an asset-authored expression weight | proposed |
| visemes.to_vrm | visemes_vrm.ih | openxr.visemes → vrm.preset | ih = 1·XR_FACE_TRACKING_VISEME_IH_META | consonant visemes are dropped, so outputs no longer sum to 1; a viseme probability becomes an asset-authored expression weight; vowel quality differs: META IH is the vowel in "tip", VRM ih is remarked "i" | proposed |
| visemes.to_vrm | visemes_vrm.ou | openxr.visemes → vrm.preset | ou = 1·XR_FACE_TRACKING_VISEME_OU_META | consonant visemes are dropped, so outputs no longer sum to 1; a viseme probability becomes an asset-authored expression weight | proposed |
| visemes.to_vrm | visemes_vrm.ee | openxr.visemes → vrm.preset | ee = 1·XR_FACE_TRACKING_VISEME_E_META | consonant visemes are dropped, so outputs no longer sum to 1; a viseme probability becomes an asset-authored expression weight | proposed |
| visemes.to_vrm | visemes_vrm.oh | openxr.visemes → vrm.preset | oh = 1·XR_FACE_TRACKING_VISEME_OH_META | consonant visemes are dropped, so outputs no longer sum to 1; a viseme probability becomes an asset-authored expression weight | proposed |

## arkit.to_canonical

### arkit.coefficient.eyeBlinkLeft.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkLeft | rcef.arkit.coefficient.eyeBlinkLeft | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:eyeBlinkLeft: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.eyeBlinkRight.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkRight | rcef.arkit.coefficient.eyeBlinkRight | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:eyeBlinkRight: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.jawForward.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawForward | rcef.arkit.coefficient.jawForward | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:jawForward: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.jawOpen.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawOpen | rcef.arkit.coefficient.jawOpen | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:jawOpen: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.browDownLeft.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownLeft | rcef.arkit.coefficient.browDownLeft | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:browDownLeft: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.browDownRight.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownRight | rcef.arkit.coefficient.browDownRight | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:browDownRight: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.browInnerUp.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browInnerUp | rcef.arkit.coefficient.browInnerUp | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:browInnerUp: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.browOuterUpLeft.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpLeft | rcef.arkit.coefficient.browOuterUpLeft | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:browOuterUpLeft: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

### arkit.coefficient.browOuterUpRight.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpRight | rcef.arkit.coefficient.browOuterUpRight | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration arkit.coefficient.v1:browOuterUpRight: face-relative native neutral-to-maximum coefficient.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: apple_blendshapes, rcef_definitions

## fb2.to_canonical

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

### openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB | rcef.openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration openxr.fb2.v1:XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB: native direction-specific angle fraction; maximum angle unspecified.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: xr_registry, xr_fb2, rcef_definitions

## fb2.to_arkit

### fb2_arkit.eyeBlinkLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB | arkit.coefficient.eyeBlinkLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_CLOSED_L corresponds to ARKit eyeBlinkLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB","arkit.coefficient.eyeBlinkLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeBlinkRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB | arkit.coefficient.eyeBlinkRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_CLOSED_R corresponds to ARKit eyeBlinkRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB","arkit.coefficient.eyeBlinkRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.jawOpen

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB | arkit.coefficient.jawOpen | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 JAW_DROP corresponds to ARKit jawOpen.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB","arkit.coefficient.jawOpen"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

### fb2_arkit.mouthClose

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIPS_TOWARD_FB | arkit.coefficient.mouthClose | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIPS_TOWARD corresponds to ARKit mouthClose.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- FB2 closes the lips regardless of the jaw position; Unified Expressions closes the mouth in relation to JawOpen and SRanipal requires Jaw_Open to be inactive. The value is copied without compensating for the jaw.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIPS_TOWARD_FB","arkit.coefficient.mouthClose"],"units":"1"},{"category":"signal","effect":"approximated","reason":"jaw-relative versus jaw-independent lip closure","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIPS_TOWARD_FB","arkit.coefficient.mouthClose"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, vrcft_docs_shapes, vrcft_docs_overview

### fb2_arkit.browInnerUp

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB, openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB | arkit.coefficient.browInnerUp | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- ARKit browInnerUp is one coefficient for both sides; it is the mean of FB2 INNER_BROW_RAISER_L and INNER_BROW_RAISER_R, as VRCFaceTracking computes BrowInnerUp; Godot has no combined inner-brow shape.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB","arkit.coefficient.browInnerUp"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB","arkit.coefficient.browInnerUp"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_code_parameters, vrcft_docs_movement, vrcft_docs_arkit, ict_facekit

### fb2_arkit.cheekPuff

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB, openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB | arkit.coefficient.cheekPuff | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- ARKit cheekPuff is one coefficient for both sides; it is the mean of FB2 CHEEK_PUFF_L and CHEEK_PUFF_R, as the Godot OpenXR vendors plugin computes CheekPuff.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB","arkit.coefficient.cheekPuff"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB","arkit.coefficient.cheekPuff"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_code_parameters, ict_facekit

### fb2_arkit.mouthSmileLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB | arkit.coefficient.mouthSmileLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_CORNER_PULLER_L corresponds to ARKit mouthSmileLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB","arkit.coefficient.mouthSmileLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 also pulls the corner back and laterally; ARKit describes upward movement only","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB","arkit.coefficient.mouthSmileLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.mouthSmileRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB | arkit.coefficient.mouthSmileRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_CORNER_PULLER_R corresponds to ARKit mouthSmileRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB","arkit.coefficient.mouthSmileRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 also pulls the corner back and laterally; ARKit describes upward movement only","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB","arkit.coefficient.mouthSmileRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.mouthShrugUpper

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB | arkit.coefficient.mouthShrugUpper | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 CHIN_RAISER_T corresponds to ARKit mouthShrugUpper.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB","arkit.coefficient.mouthShrugUpper"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes upward lip motion induced by the chin raiser; ARKit describes outward upper-lip movement","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB","arkit.coefficient.mouthShrugUpper"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

### fb2_arkit.mouthShrugLower

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB | arkit.coefficient.mouthShrugLower | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 CHIN_RAISER_B corresponds to ARKit mouthShrugLower.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB","arkit.coefficient.mouthShrugLower"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes upward chin and lower-lip motion; ARKit describes outward lower-lip movement","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB","arkit.coefficient.mouthShrugLower"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

## fb2_gaze.to_arkit

### fb2_arkit.eyeLookOutLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | arkit.coefficient.eyeLookOutLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_LEFT_L corresponds to ARKit eyeLookOutLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB","arkit.coefficient.eyeLookOutLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB","arkit.coefficient.eyeLookOutLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB","arkit.coefficient.eyeLookOutLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB","arkit.coefficient.eyeLookOutLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeLookInLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | arkit.coefficient.eyeLookInLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_RIGHT_L corresponds to ARKit eyeLookInLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB","arkit.coefficient.eyeLookInLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB","arkit.coefficient.eyeLookInLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB","arkit.coefficient.eyeLookInLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB","arkit.coefficient.eyeLookInLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeLookOutRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | arkit.coefficient.eyeLookOutRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_RIGHT_R corresponds to ARKit eyeLookOutRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB","arkit.coefficient.eyeLookOutRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB","arkit.coefficient.eyeLookOutRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB","arkit.coefficient.eyeLookOutRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB","arkit.coefficient.eyeLookOutRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeLookInRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | arkit.coefficient.eyeLookInRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_LEFT_R corresponds to ARKit eyeLookInRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB","arkit.coefficient.eyeLookInRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB","arkit.coefficient.eyeLookInRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB","arkit.coefficient.eyeLookInRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB","arkit.coefficient.eyeLookInRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

## fixture.affine

### fixture.affine.convert

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| fixture.affine.signed | fixture.affine.unit | {"id":"affine","offset":0.5,"scale":0.5} | mapped | exact |

Assumptions:

- Original fixture states matching low/mid/high at -1/0/1 and 0/0.5/1; explicit basis conversion.

Loss annotations: []

Evidence: rcef_definitions

## fixture.bilateral

### fixture.brow.collapse

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| fixture.brow.left, fixture.brow.right | fixture.brow.shared | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- Original synthetic channels share a declared normalized scale; arithmetic mean chosen for this fixture only.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["fixture.brow.left","fixture.brow.right","fixture.brow.shared"],"units":"1"},{"category":"geometry","effect":"unknown","reason":"No geometry evaluated by scalar fixture.","refs":["fixture.brow.shared"]}]

Evidence: rcef_definitions

## survey.ambiguous

### survey.mediapipe_arkit.blink

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| mediapipe.label.eyeBlinkLeft | rcef.arkit.coefficient.eyeBlinkLeft | {"id":"identity"} | unresolved | not declared |

Assumptions:

- Names alone cannot establish model/provider calibration.

Loss annotations: []

Evidence: mediapipe, apple_blendshapes

## visemes.to_vrm

### visemes_vrm.aa

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.visemes.XR_FACE_TRACKING_VISEME_AA_META | vrm.preset.aa | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- META viseme AA corresponds to VRM preset aa (META "A:" as in car; VRM remark "aa").
- Phoneme-label correspondence only; no published table maps META visemes to VRM presets.
- META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"consonant visemes are dropped, so outputs no longer sum to 1","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_AA_META","vrm.preset.aa"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a viseme probability becomes an asset-authored expression weight","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_AA_META","vrm.preset.aa"],"units":"1"}]

Evidence: xr_visemes, vrm_expressions

### visemes_vrm.ih

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.visemes.XR_FACE_TRACKING_VISEME_IH_META | vrm.preset.ih | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- META viseme IH corresponds to VRM preset ih (META "ih" as in tip; VRM remark "i").
- Phoneme-label correspondence only; no published table maps META visemes to VRM presets.
- META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"consonant visemes are dropped, so outputs no longer sum to 1","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_IH_META","vrm.preset.ih"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a viseme probability becomes an asset-authored expression weight","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_IH_META","vrm.preset.ih"],"units":"1"},{"category":"signal","effect":"approximated","reason":"vowel quality differs: META IH is the vowel in \\"tip\\", VRM ih is remarked \\"i\\"","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_IH_META","vrm.preset.ih"],"units":"1"}]

Evidence: xr_visemes, vrm_expressions

### visemes_vrm.ou

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.visemes.XR_FACE_TRACKING_VISEME_OU_META | vrm.preset.ou | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- META viseme OU corresponds to VRM preset ou (META "ou" as in book; VRM remark "u").
- Phoneme-label correspondence only; no published table maps META visemes to VRM presets.
- META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"consonant visemes are dropped, so outputs no longer sum to 1","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_OU_META","vrm.preset.ou"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a viseme probability becomes an asset-authored expression weight","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_OU_META","vrm.preset.ou"],"units":"1"}]

Evidence: xr_visemes, vrm_expressions

### visemes_vrm.ee

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.visemes.XR_FACE_TRACKING_VISEME_E_META | vrm.preset.ee | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- META viseme E corresponds to VRM preset ee (META "e" as in bed; VRM remark "eh").
- Phoneme-label correspondence only; no published table maps META visemes to VRM presets.
- META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"consonant visemes are dropped, so outputs no longer sum to 1","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_E_META","vrm.preset.ee"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a viseme probability becomes an asset-authored expression weight","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_E_META","vrm.preset.ee"],"units":"1"}]

Evidence: xr_visemes, vrm_expressions

### visemes_vrm.oh

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.visemes.XR_FACE_TRACKING_VISEME_OH_META | vrm.preset.oh | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- META viseme OH corresponds to VRM preset oh (META "oh" as in toe; VRM remark "oh").
- Phoneme-label correspondence only; no published table maps META visemes to VRM presets.
- META viseme probability (0 to 1) is used directly as the VRM expression weight (0 to 1).
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"consonant visemes are dropped, so outputs no longer sum to 1","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_OH_META","vrm.preset.oh"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a viseme probability becomes an asset-authored expression weight","refs":["openxr.visemes.XR_FACE_TRACKING_VISEME_OH_META","vrm.preset.oh"],"units":"1"}]

Evidence: xr_visemes, vrm_expressions

## vrcft_eye.to_canonical

### vrcft.eye.Left.Openness.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| vrcft.eye.Left.Openness | rcef.vrcft.eye.Left.Openness | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration vrcft.eye.storage.v1:Left.Openness.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: vrcft_data, rcef_definitions

### vrcft.eye.Left.PupilDiameter_MM.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| vrcft.eye.Left.PupilDiameter_MM | rcef.vrcft.eye.Left.PupilDiameter_MM | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration vrcft.eye.storage.v1:Left.PupilDiameter_MM.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: vrcft_data, rcef_definitions

### vrcft.eye.Right.Openness.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| vrcft.eye.Right.Openness | rcef.vrcft.eye.Right.Openness | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration vrcft.eye.storage.v1:Right.Openness.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: vrcft_data, rcef_definitions

### vrcft.eye.Right.PupilDiameter_MM.identity

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| vrcft.eye.Right.PupilDiameter_MM | rcef.vrcft.eye.Right.PupilDiameter_MM | {"id":"identity"} | mapped | exact |

Assumptions:

- Valid scalar sample supplied with native calibration vrcft.eye.storage.v1:Right.PupilDiameter_MM.
- Output preserves native coefficient meaning only; no cross-provider or visual equivalence.

Loss annotations: []

Evidence: vrcft_data, rcef_definitions

