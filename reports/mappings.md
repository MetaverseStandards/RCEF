# RCEF authored mappings

Pack: rcef.parity; data version: 0.3.0.

Generated from rcef.pack.json; SHA-256: a7ae2fc4202b53b15672afaef0c83d4e099fdaeb8efe9c0a9c904d427f36b1f0.

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
| fb2.to_arkit | fb2_arkit.browDownLeft | openxr.fb2 → arkit.coefficient | browDownLeft = 1·XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.browDownRight | openxr.fb2 → arkit.coefficient | browDownRight = 1·XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.browOuterUpLeft | openxr.fb2 → arkit.coefficient | browOuterUpLeft = 1·XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.browOuterUpRight | openxr.fb2 → arkit.coefficient | browOuterUpRight = 1·XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.cheekSquintLeft | openxr.fb2 → arkit.coefficient | cheekSquintLeft = 1·XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.cheekSquintRight | openxr.fb2 → arkit.coefficient | cheekSquintRight = 1·XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.eyeSquintLeft | openxr.fb2 → arkit.coefficient | eyeSquintLeft = 1·XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.eyeSquintRight | openxr.fb2 → arkit.coefficient | eyeSquintRight = 1·XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.eyeWideLeft | openxr.fb2 → arkit.coefficient | eyeWideLeft = 1·XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.eyeWideRight | openxr.fb2 → arkit.coefficient | eyeWideRight = 1·XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.jawForward | openxr.fb2 → arkit.coefficient | jawForward = 1·XR_FACE_EXPRESSION2_JAW_THRUST_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.jawLeft | openxr.fb2 → arkit.coefficient | jawLeft = 1·XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.jawRight | openxr.fb2 → arkit.coefficient | jawRight = 1·XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthDimpleLeft | openxr.fb2 → arkit.coefficient | mouthDimpleLeft = 1·XR_FACE_EXPRESSION2_DIMPLER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthDimpleRight | openxr.fb2 → arkit.coefficient | mouthDimpleRight = 1·XR_FACE_EXPRESSION2_DIMPLER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthFrownLeft | openxr.fb2 → arkit.coefficient | mouthFrownLeft = 1·XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthFrownRight | openxr.fb2 → arkit.coefficient | mouthFrownRight = 1·XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthFunnel | openxr.fb2 → arkit.coefficient | mouthFunnel = 0.25·XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB + 0.25·XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB + 0.25·XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB + 0.25·XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthLeft | openxr.fb2 → arkit.coefficient | mouthLeft = 1·XR_FACE_EXPRESSION2_MOUTH_LEFT_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthLowerDownLeft | openxr.fb2 → arkit.coefficient | mouthLowerDownLeft = 1·XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthLowerDownRight | openxr.fb2 → arkit.coefficient | mouthLowerDownRight = 1·XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthPressLeft | openxr.fb2 → arkit.coefficient | mouthPressLeft = 1·XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthPressRight | openxr.fb2 → arkit.coefficient | mouthPressRight = 1·XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthPucker | openxr.fb2 → arkit.coefficient | mouthPucker = 0.5·XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB + 0.5·XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthRight | openxr.fb2 → arkit.coefficient | mouthRight = 1·XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthRollLower | openxr.fb2 → arkit.coefficient | mouthRollLower = 0.5·XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB + 0.5·XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthRollUpper | openxr.fb2 → arkit.coefficient | mouthRollUpper = 0.5·XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB + 0.5·XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB | asymmetry irrecoverable; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthStretchLeft | openxr.fb2 → arkit.coefficient | mouthStretchLeft = 1·XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthStretchRight | openxr.fb2 → arkit.coefficient | mouthStretchRight = 1·XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthUpperUpLeft | openxr.fb2 → arkit.coefficient | mouthUpperUpLeft = 1·XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.mouthUpperUpRight | openxr.fb2 → arkit.coefficient | mouthUpperUpRight = 1·XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.noseSneerLeft | openxr.fb2 → arkit.coefficient | noseSneerLeft = 1·XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.noseSneerRight | openxr.fb2 → arkit.coefficient | noseSneerRight = 1·XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| fb2.to_arkit | fb2_arkit.tongueOut | openxr.fb2 → arkit.coefficient | tongueOut = 1·XR_FACE_EXPRESSION2_TONGUE_OUT_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; both are extension shapes with no stated length | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookOutLeft | openxr.fb2 → arkit.coefficient | eyeLookOutLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookInLeft | openxr.fb2 → arkit.coefficient | eyeLookInLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookOutRight | openxr.fb2 → arkit.coefficient | eyeLookOutRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookInRight | openxr.fb2 → arkit.coefficient | eyeLookInRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookDownLeft | openxr.fb2 → arkit.coefficient | eyeLookDownLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookDownRight | openxr.fb2 → arkit.coefficient | eyeLookDownRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookUpLeft | openxr.fb2 → arkit.coefficient | eyeLookUpLeft = 1·XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
| fb2_gaze.to_arkit | fb2_arkit.eyeLookUpRight | openxr.fb2 → arkit.coefficient | eyeLookUpRight = 1·XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze; FB2 opposing directions are mutually exclusive; ARKit states no such constraint | proposed |
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

### fb2_arkit.browDownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB | arkit.coefficient.browDownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 BROW_LOWERER_L corresponds to ARKit browDownLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB","arkit.coefficient.browDownLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.browDownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB | arkit.coefficient.browDownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 BROW_LOWERER_R corresponds to ARKit browDownRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB","arkit.coefficient.browDownRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.browOuterUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB | arkit.coefficient.browOuterUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 OUTER_BROW_RAISER_L corresponds to ARKit browOuterUpLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB","arkit.coefficient.browOuterUpLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.browOuterUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB | arkit.coefficient.browOuterUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 OUTER_BROW_RAISER_R corresponds to ARKit browOuterUpRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB","arkit.coefficient.browOuterUpRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.cheekSquintLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB | arkit.coefficient.cheekSquintLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 CHEEK_RAISER_L corresponds to ARKit cheekSquintLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB","arkit.coefficient.cheekSquintLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.cheekSquintRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB | arkit.coefficient.cheekSquintRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 CHEEK_RAISER_R corresponds to ARKit cheekSquintRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB","arkit.coefficient.cheekSquintRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeSquintLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB | arkit.coefficient.eyeSquintLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LID_TIGHTENER_L corresponds to ARKit eyeSquintLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB","arkit.coefficient.eyeSquintLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeSquintRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB | arkit.coefficient.eyeSquintRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LID_TIGHTENER_R corresponds to ARKit eyeSquintRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB","arkit.coefficient.eyeSquintRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeWideLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB | arkit.coefficient.eyeWideLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LID_RAISER_L corresponds to ARKit eyeWideLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB","arkit.coefficient.eyeWideLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeWideRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB | arkit.coefficient.eyeWideRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LID_RAISER_R corresponds to ARKit eyeWideRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB","arkit.coefficient.eyeWideRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.jawForward

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_JAW_THRUST_FB | arkit.coefficient.jawForward | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 JAW_THRUST corresponds to ARKit jawForward.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_JAW_THRUST_FB","arkit.coefficient.jawForward"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.jawLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB | arkit.coefficient.jawLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 JAW_SIDEWAYS_LEFT corresponds to ARKit jawLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB","arkit.coefficient.jawLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### fb2_arkit.jawRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB | arkit.coefficient.jawRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 JAW_SIDEWAYS_RIGHT corresponds to ARKit jawRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB","arkit.coefficient.jawRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### fb2_arkit.mouthDimpleLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_L_FB | arkit.coefficient.mouthDimpleLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 DIMPLER_L corresponds to ARKit mouthDimpleLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_L_FB","arkit.coefficient.mouthDimpleLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthDimpleRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_R_FB | arkit.coefficient.mouthDimpleRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 DIMPLER_R corresponds to ARKit mouthDimpleRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_R_FB","arkit.coefficient.mouthDimpleRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthFrownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB | arkit.coefficient.mouthFrownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_CORNER_DEPRESSOR_L corresponds to ARKit mouthFrownLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB","arkit.coefficient.mouthFrownLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthFrownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB | arkit.coefficient.mouthFrownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_CORNER_DEPRESSOR_R corresponds to ARKit mouthFrownRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB","arkit.coefficient.mouthFrownRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthFunnel

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB | arkit.coefficient.mouthFunnel | {"id":"weighted_sum","weights":[0.25,0.25,0.25,0.25]} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is one coefficient; it is the mean of the four quarters of FB2 LIP_FUNNELER_LB, LIP_FUNNELER_LT, LIP_FUNNELER_RB, LIP_FUNNELER_RT, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB","arkit.coefficient.mouthFunnel"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB","arkit.coefficient.mouthFunnel"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### fb2_arkit.mouthLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_LEFT_FB | arkit.coefficient.mouthLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 MOUTH_LEFT corresponds to ARKit mouthLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- FLAGGED: only Godot names ARKit mouthLeft for this channel (its face-modifier alias); VRCFaceTracking pairs the FB2 channel with Unified MouthLeft, and the FB2 and Apple definitions agree.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_LEFT_FB","arkit.coefficient.mouthLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_movement

### fb2_arkit.mouthLowerDownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB | arkit.coefficient.mouthLowerDownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LOWER_LIP_DEPRESSOR_L corresponds to ARKit mouthLowerDownLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB","arkit.coefficient.mouthLowerDownLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthLowerDownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB | arkit.coefficient.mouthLowerDownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LOWER_LIP_DEPRESSOR_R corresponds to ARKit mouthLowerDownRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB","arkit.coefficient.mouthLowerDownRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthPressLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB | arkit.coefficient.mouthPressLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_PRESSOR_L corresponds to ARKit mouthPressLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB","arkit.coefficient.mouthPressLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthPressRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB | arkit.coefficient.mouthPressRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_PRESSOR_R corresponds to ARKit mouthPressRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB","arkit.coefficient.mouthPressRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthPucker

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB | arkit.coefficient.mouthPucker | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is one coefficient; it is the mean of FB2 LIP_PUCKER_L, LIP_PUCKER_R, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB","arkit.coefficient.mouthPucker"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB","arkit.coefficient.mouthPucker"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### fb2_arkit.mouthRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB | arkit.coefficient.mouthRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 MOUTH_RIGHT corresponds to ARKit mouthRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- FLAGGED: only Godot names ARKit mouthRight for this channel (its face-modifier alias); VRCFaceTracking pairs the FB2 channel with Unified MouthRight, and the FB2 and Apple definitions agree.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB","arkit.coefficient.mouthRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_movement

### fb2_arkit.mouthRollLower

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB | arkit.coefficient.mouthRollLower | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- ARKit mouthRollLower is one coefficient; it is the mean of FB2 LIP_SUCK_LB, LIP_SUCK_RB, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB","arkit.coefficient.mouthRollLower"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB","arkit.coefficient.mouthRollLower"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### fb2_arkit.mouthRollUpper

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB, openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB | arkit.coefficient.mouthRollUpper | {"id":"weighted_sum","weights":[0.5,0.5]} | mapped | approximate |

Assumptions:

- ARKit mouthRollUpper is one coefficient; it is the mean of FB2 LIP_SUCK_LT, LIP_SUCK_RT, as the Godot OpenXR vendors plugin computes it and VRCFaceTracking averages the matching Unified shapes.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry irrecoverable","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB","arkit.coefficient.mouthRollUpper"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB","arkit.coefficient.mouthRollUpper"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### fb2_arkit.mouthStretchLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB | arkit.coefficient.mouthStretchLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_STRETCHER_L corresponds to ARKit mouthStretchLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB","arkit.coefficient.mouthStretchLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthStretchRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB | arkit.coefficient.mouthStretchRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LIP_STRETCHER_R corresponds to ARKit mouthStretchRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB","arkit.coefficient.mouthStretchRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.mouthUpperUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB | arkit.coefficient.mouthUpperUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LIP_RAISER_L corresponds to ARKit mouthUpperUpLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB","arkit.coefficient.mouthUpperUpLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### fb2_arkit.mouthUpperUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB | arkit.coefficient.mouthUpperUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LIP_RAISER_R corresponds to ARKit mouthUpperUpRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB","arkit.coefficient.mouthUpperUpRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### fb2_arkit.noseSneerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB | arkit.coefficient.noseSneerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 NOSE_WRINKLER_L corresponds to ARKit noseSneerLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB","arkit.coefficient.noseSneerLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.noseSneerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB | arkit.coefficient.noseSneerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 NOSE_WRINKLER_R corresponds to ARKit noseSneerRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB","arkit.coefficient.noseSneerRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.tongueOut

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB | arkit.coefficient.tongueOut | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 TONGUE_OUT corresponds to ARKit tongueOut.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB","arkit.coefficient.tongueOut"],"units":"1"},{"category":"signal","effect":"approximated","reason":"both are extension shapes with no stated length","refs":["openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB","arkit.coefficient.tongueOut"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

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

### fb2_arkit.eyeLookDownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB | arkit.coefficient.eyeLookDownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_DOWN_L corresponds to ARKit eyeLookDownLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB","arkit.coefficient.eyeLookDownLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB","arkit.coefficient.eyeLookDownLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB","arkit.coefficient.eyeLookDownLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB","arkit.coefficient.eyeLookDownLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeLookDownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB | arkit.coefficient.eyeLookDownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_DOWN_R corresponds to ARKit eyeLookDownRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB","arkit.coefficient.eyeLookDownRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB","arkit.coefficient.eyeLookDownRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB","arkit.coefficient.eyeLookDownRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB","arkit.coefficient.eyeLookDownRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeLookUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB | arkit.coefficient.eyeLookUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_UP_L corresponds to ARKit eyeLookUpLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB","arkit.coefficient.eyeLookUpLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB","arkit.coefficient.eyeLookUpLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB","arkit.coefficient.eyeLookUpLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB","arkit.coefficient.eyeLookUpLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### fb2_arkit.eyeLookUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB | arkit.coefficient.eyeLookUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_LOOK_UP_R corresponds to ARKit eyeLookUpRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB","arkit.coefficient.eyeLookUpRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB","arkit.coefficient.eyeLookUpRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 describes eye rotation; ARKit describes eyelid movement consistent with the gaze","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB","arkit.coefficient.eyeLookUpRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 opposing directions are mutually exclusive; ARKit states no such constraint","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB","arkit.coefficient.eyeLookUpRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

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

