# RCEF authored mappings

Pack: rcef.parity; data version: 0.4.0.

Generated from rcef.pack.json; SHA-256: 8b31f8b838f906042689efc07e7ded83f224d371b8b40af90ed23b36eb9da829.

Original RCEF data and arrangement: RCEF contributors (2026), CC-BY-SA-4.0. Provider attribution and source terms are in ../THIRD_PARTY_NOTICES.md.

Each mapping keeps its declared direction, status, assumptions and losses. An unresolved mapping is an inventory record. It cannot be executed.

## Proposed rules

Proposed mappings translate between providers. Each formula assumes the calibration stated with its mapping below. Losses list what the translation cannot carry.

| Map | Mapping | Source → target | Formula | Losses | Evidence status |
| --- | --- | --- | --- | --- | --- |
| arkit.to_fb2 | arkit_fb2.BROW_LOWERER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB = 1·browDownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.BROW_LOWERER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB = 1·browDownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.INNER_BROW_RAISER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB = 1·browInnerUp | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.INNER_BROW_RAISER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB = 1·browInnerUp | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.OUTER_BROW_RAISER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB = 1·browOuterUpLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.OUTER_BROW_RAISER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB = 1·browOuterUpRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHEEK_PUFF_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB = 1·cheekPuff | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHEEK_PUFF_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB = 1·cheekPuff | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHEEK_RAISER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB = 1·cheekSquintLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHEEK_RAISER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB = 1·cheekSquintRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.EYES_CLOSED_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB = 1·eyeBlinkLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.EYES_CLOSED_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB = 1·eyeBlinkRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LID_TIGHTENER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB = 1·eyeSquintLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LID_TIGHTENER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB = 1·eyeSquintRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.UPPER_LID_RAISER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB = 1·eyeWideLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.UPPER_LID_RAISER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB = 1·eyeWideRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.JAW_THRUST | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_JAW_THRUST_FB = 1·jawForward | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.JAW_SIDEWAYS_LEFT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB = 1·jawLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.JAW_DROP | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_JAW_DROP_FB = 1·jawOpen | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.JAW_SIDEWAYS_RIGHT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB = 1·jawRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIPS_TOWARD | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIPS_TOWARD_FB = 1·mouthClose | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.DIMPLER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_DIMPLER_L_FB = 1·mouthDimpleLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.DIMPLER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_DIMPLER_R_FB = 1·mouthDimpleRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_CORNER_DEPRESSOR_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB = 1·mouthFrownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_CORNER_DEPRESSOR_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB = 1·mouthFrownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_FUNNELER_LB | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB = 1·mouthFunnel | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_FUNNELER_LT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB = 1·mouthFunnel | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_FUNNELER_RB | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB = 1·mouthFunnel | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_FUNNELER_RT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB = 1·mouthFunnel | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.MOUTH_LEFT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_MOUTH_LEFT_FB = 1·mouthLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LOWER_LIP_DEPRESSOR_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB = 1·mouthLowerDownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LOWER_LIP_DEPRESSOR_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB = 1·mouthLowerDownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_PRESSOR_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB = 1·mouthPressLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_PRESSOR_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB = 1·mouthPressRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_PUCKER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB = 1·mouthPucker | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_PUCKER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB = 1·mouthPucker | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.MOUTH_RIGHT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB = 1·mouthRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_SUCK_LB | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB = 1·mouthRollLower | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_SUCK_RB | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB = 1·mouthRollLower | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_SUCK_LT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB = 1·mouthRollUpper | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_SUCK_RT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB = 1·mouthRollUpper | asymmetry unknown: symmetry is invented; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHIN_RAISER_B | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB = 1·mouthShrugLower | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.CHIN_RAISER_T | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB = 1·mouthShrugUpper | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_CORNER_PULLER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB = 1·mouthSmileLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_CORNER_PULLER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB = 1·mouthSmileRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_STRETCHER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB = 1·mouthStretchLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.LIP_STRETCHER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB = 1·mouthStretchRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.UPPER_LIP_RAISER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB = 1·mouthUpperUpLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.UPPER_LIP_RAISER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB = 1·mouthUpperUpRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.NOSE_WRINKLER_L | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB = 1·noseSneerLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.NOSE_WRINKLER_R | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB = 1·noseSneerRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_fb2 | arkit_fb2.TONGUE_OUT | arkit.coefficient → openxr.fb2 | XR_FACE_EXPRESSION2_TONGUE_OUT_FB = 1·tongueOut | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; both are extension shapes with no stated length | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.gaze_in_minus_out_L | arkit.coefficient → rcef.intermediate | arkit_gaze_in_minus_out_L = 1·eyeLookInLeft + -1·eyeLookOutLeft | FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_RIGHT_L | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB = {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_LEFT_L | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB = {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.gaze_up_minus_down_L | arkit.coefficient → rcef.intermediate | arkit_gaze_up_minus_down_L = 1·eyeLookUpLeft + -1·eyeLookDownLeft | FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_UP_L | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB = {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_DOWN_L | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB = {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.gaze_in_minus_out_R | arkit.coefficient → rcef.intermediate | arkit_gaze_in_minus_out_R = 1·eyeLookInRight + -1·eyeLookOutRight | FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_LEFT_R | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB = {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_RIGHT_R | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB = {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.gaze_up_minus_down_R | arkit.coefficient → rcef.intermediate | arkit_gaze_up_minus_down_R = 1·eyeLookUpRight + -1·eyeLookDownRight | FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_UP_R | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB = {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit_gaze.to_fb2 | arkit_fb2.EYES_LOOK_DOWN_R | rcef.intermediate → openxr.fb2 | XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB = {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; FB2 maximum gaze angle is unspecified; ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation; FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowLowererLeft | arkit.coefficient → vrcft.artist.base | BrowLowererLeft = 1·browDownLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowPinchLeft | arkit.coefficient → vrcft.artist.base | BrowPinchLeft = 1·browDownLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowLowererRight | arkit.coefficient → vrcft.artist.base | BrowLowererRight = 1·browDownRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowPinchRight | arkit.coefficient → vrcft.artist.base | BrowPinchRight = 1·browDownRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowInnerUpRight | arkit.coefficient → vrcft.artist.base | BrowInnerUpRight = 1·browInnerUp | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowInnerUpLeft | arkit.coefficient → vrcft.artist.base | BrowInnerUpLeft = 1·browInnerUp | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowOuterUpLeft | arkit.coefficient → vrcft.artist.base | BrowOuterUpLeft = 1·browOuterUpLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.BrowOuterUpRight | arkit.coefficient → vrcft.artist.base | BrowOuterUpRight = 1·browOuterUpRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.CheekPuffRight | arkit.coefficient → vrcft.artist.base | CheekPuffRight = 1·cheekPuff | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.CheekPuffLeft | arkit.coefficient → vrcft.artist.base | CheekPuffLeft = 1·cheekPuff | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.CheekSquintLeft | arkit.coefficient → vrcft.artist.base | CheekSquintLeft = 1·cheekSquintLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.CheekSquintRight | arkit.coefficient → vrcft.artist.base | CheekSquintRight = 1·cheekSquintRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeClosedLeft | arkit.coefficient → vrcft.artist.base | EyeClosedLeft = 1·eyeBlinkLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeClosedRight | arkit.coefficient → vrcft.artist.base | EyeClosedRight = 1·eyeBlinkRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookDownLeft | arkit.coefficient → vrcft.artist.base | EyeLookDownLeft = 1·eyeLookDownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookDownRight | arkit.coefficient → vrcft.artist.base | EyeLookDownRight = 1·eyeLookDownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookInLeft | arkit.coefficient → vrcft.artist.base | EyeLookInLeft = 1·eyeLookInLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookInRight | arkit.coefficient → vrcft.artist.base | EyeLookInRight = 1·eyeLookInRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookOutLeft | arkit.coefficient → vrcft.artist.base | EyeLookOutLeft = 1·eyeLookOutLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookOutRight | arkit.coefficient → vrcft.artist.base | EyeLookOutRight = 1·eyeLookOutRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookUpLeft | arkit.coefficient → vrcft.artist.base | EyeLookUpLeft = 1·eyeLookUpLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeLookUpRight | arkit.coefficient → vrcft.artist.base | EyeLookUpRight = 1·eyeLookUpRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeSquintLeft | arkit.coefficient → vrcft.artist.base | EyeSquintLeft = 1·eyeSquintLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeSquintRight | arkit.coefficient → vrcft.artist.base | EyeSquintRight = 1·eyeSquintRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeWideLeft | arkit.coefficient → vrcft.artist.base | EyeWideLeft = 1·eyeWideLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.EyeWideRight | arkit.coefficient → vrcft.artist.base | EyeWideRight = 1·eyeWideRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.JawForward | arkit.coefficient → vrcft.artist.base | JawForward = 1·jawForward | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.JawLeft | arkit.coefficient → vrcft.artist.base | JawLeft = 1·jawLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.JawOpen | arkit.coefficient → vrcft.artist.base | JawOpen = 1·jawOpen | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.JawRight | arkit.coefficient → vrcft.artist.base | JawRight = 1·jawRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthClosed | arkit.coefficient → vrcft.artist.base | MouthClosed = 1·mouthClose | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthDimpleLeft | arkit.coefficient → vrcft.artist.base | MouthDimpleLeft = 1·mouthDimpleLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthDimpleRight | arkit.coefficient → vrcft.artist.base | MouthDimpleRight = 1·mouthDimpleRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthFrownLeft | arkit.coefficient → vrcft.artist.base | MouthFrownLeft = 1·mouthFrownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthFrownRight | arkit.coefficient → vrcft.artist.base | MouthFrownRight = 1·mouthFrownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipFunnelUpperRight | arkit.coefficient → vrcft.artist.base | LipFunnelUpperRight = 1·mouthFunnel | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipFunnelUpperLeft | arkit.coefficient → vrcft.artist.base | LipFunnelUpperLeft = 1·mouthFunnel | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipFunnelLowerRight | arkit.coefficient → vrcft.artist.base | LipFunnelLowerRight = 1·mouthFunnel | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipFunnelLowerLeft | arkit.coefficient → vrcft.artist.base | LipFunnelLowerLeft = 1·mouthFunnel | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthUpperLeft | arkit.coefficient → vrcft.artist.base | MouthUpperLeft = 1·mouthLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthLowerLeft | arkit.coefficient → vrcft.artist.base | MouthLowerLeft = 1·mouthLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthLowerDownLeft | arkit.coefficient → vrcft.artist.base | MouthLowerDownLeft = 1·mouthLowerDownLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthLowerDownRight | arkit.coefficient → vrcft.artist.base | MouthLowerDownRight = 1·mouthLowerDownRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthPressLeft | arkit.coefficient → vrcft.artist.base | MouthPressLeft = 1·mouthPressLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthPressRight | arkit.coefficient → vrcft.artist.base | MouthPressRight = 1·mouthPressRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipPuckerUpperRight | arkit.coefficient → vrcft.artist.base | LipPuckerUpperRight = 1·mouthPucker | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipPuckerUpperLeft | arkit.coefficient → vrcft.artist.base | LipPuckerUpperLeft = 1·mouthPucker | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipPuckerLowerRight | arkit.coefficient → vrcft.artist.base | LipPuckerLowerRight = 1·mouthPucker | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipPuckerLowerLeft | arkit.coefficient → vrcft.artist.base | LipPuckerLowerLeft = 1·mouthPucker | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthUpperRight | arkit.coefficient → vrcft.artist.base | MouthUpperRight = 1·mouthRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthLowerRight | arkit.coefficient → vrcft.artist.base | MouthLowerRight = 1·mouthRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipSuckLowerRight | arkit.coefficient → vrcft.artist.base | LipSuckLowerRight = 1·mouthRollLower | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipSuckLowerLeft | arkit.coefficient → vrcft.artist.base | LipSuckLowerLeft = 1·mouthRollLower | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipSuckUpperRight | arkit.coefficient → vrcft.artist.base | LipSuckUpperRight = 1·mouthRollUpper | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.LipSuckUpperLeft | arkit.coefficient → vrcft.artist.base | LipSuckUpperLeft = 1·mouthRollUpper | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthRaiserLower | arkit.coefficient → vrcft.artist.base | MouthRaiserLower = 1·mouthShrugLower | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthRaiserUpper | arkit.coefficient → vrcft.artist.base | MouthRaiserUpper = 1·mouthShrugUpper | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthCornerPullLeft | arkit.coefficient → vrcft.artist.base | MouthCornerPullLeft = 1·mouthSmileLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthCornerSlantLeft | arkit.coefficient → vrcft.artist.base | MouthCornerSlantLeft = 1·mouthSmileLeft | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthCornerPullRight | arkit.coefficient → vrcft.artist.base | MouthCornerPullRight = 1·mouthSmileRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthCornerSlantRight | arkit.coefficient → vrcft.artist.base | MouthCornerSlantRight = 1·mouthSmileRight | Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal; provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthStretchLeft | arkit.coefficient → vrcft.artist.base | MouthStretchLeft = 1·mouthStretchLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthStretchRight | arkit.coefficient → vrcft.artist.base | MouthStretchRight = 1·mouthStretchRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthUpperUpLeft | arkit.coefficient → vrcft.artist.base | MouthUpperUpLeft = 1·mouthUpperUpLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.MouthUpperUpRight | arkit.coefficient → vrcft.artist.base | MouthUpperUpRight = 1·mouthUpperUpRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.NoseSneerLeft | arkit.coefficient → vrcft.artist.base | NoseSneerLeft = 1·noseSneerLeft | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.NoseSneerRight | arkit.coefficient → vrcft.artist.base | NoseSneerRight = 1·noseSneerRight | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal | proposed |
| arkit.to_vrcft_artist | arkit_vrcft_artist.TongueOut | arkit.coefficient → vrcft.artist.base | TongueOut = 1·tongueOut | provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal; both are extension shapes with no stated length | proposed |
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
| fb2.to_vrm | fb2_vrm.blinkLeft | openxr.fb2 → vrm.preset | blinkLeft = 1·XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB | an FB2 weight becomes an asset-authored expression weight; VRM blink (both eyes) is left unset, so a model that binds only blink, not blinkLeft and blinkRight, does not blink; a model may mark the preset isBinary, which turns a partial closure into fully open or fully closed | proposed |
| fb2.to_vrm | fb2_vrm.blinkRight | openxr.fb2 → vrm.preset | blinkRight = 1·XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB | an FB2 weight becomes an asset-authored expression weight; VRM blink (both eyes) is left unset, so a model that binds only blink, not blinkLeft and blinkRight, does not blink; a model may mark the preset isBinary, which turns a partial closure into fully open or fully closed | proposed |
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

## arkit.to_fb2

### arkit_fb2.BROW_LOWERER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownLeft | openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownLeft corresponds to FB2 BROW_LOWERER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownLeft","openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.BROW_LOWERER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownRight | openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownRight corresponds to FB2 BROW_LOWERER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownRight","openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.INNER_BROW_RAISER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browInnerUp | openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browInnerUp is one coefficient; FB2 INNER_BROW_RAISER_L is set to it, as are INNER_BROW_RAISER_R, so that FB2 -&gt; ARKit gives browInnerUp back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.browInnerUp","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browInnerUp","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_code_parameters, vrcft_docs_movement, vrcft_docs_arkit, ict_facekit

### arkit_fb2.INNER_BROW_RAISER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browInnerUp | openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browInnerUp is one coefficient; FB2 INNER_BROW_RAISER_R is set to it, as are INNER_BROW_RAISER_L, so that FB2 -&gt; ARKit gives browInnerUp back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.browInnerUp","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browInnerUp","openxr.fb2.XR_FACE_EXPRESSION2_INNER_BROW_RAISER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_code_parameters, vrcft_docs_movement, vrcft_docs_arkit, ict_facekit

### arkit_fb2.OUTER_BROW_RAISER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpLeft | openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browOuterUpLeft corresponds to FB2 OUTER_BROW_RAISER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browOuterUpLeft","openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.OUTER_BROW_RAISER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpRight | openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browOuterUpRight corresponds to FB2 OUTER_BROW_RAISER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browOuterUpRight","openxr.fb2.XR_FACE_EXPRESSION2_OUTER_BROW_RAISER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.CHEEK_PUFF_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekPuff | openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekPuff is one coefficient; FB2 CHEEK_PUFF_L is set to it, as are CHEEK_PUFF_R, so that FB2 -&gt; ARKit gives cheekPuff back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.cheekPuff","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekPuff","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_code_parameters, ict_facekit

### arkit_fb2.CHEEK_PUFF_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekPuff | openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekPuff is one coefficient; FB2 CHEEK_PUFF_R is set to it, as are CHEEK_PUFF_L, so that FB2 -&gt; ARKit gives cheekPuff back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.cheekPuff","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekPuff","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_PUFF_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_code_parameters, ict_facekit

### arkit_fb2.CHEEK_RAISER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekSquintLeft | openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekSquintLeft corresponds to FB2 CHEEK_RAISER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekSquintLeft","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.CHEEK_RAISER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekSquintRight | openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekSquintRight corresponds to FB2 CHEEK_RAISER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekSquintRight","openxr.fb2.XR_FACE_EXPRESSION2_CHEEK_RAISER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.EYES_CLOSED_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkLeft | openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeBlinkLeft corresponds to FB2 EYES_CLOSED_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeBlinkLeft","openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.EYES_CLOSED_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkRight | openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeBlinkRight corresponds to FB2 EYES_CLOSED_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeBlinkRight","openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.LID_TIGHTENER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeSquintLeft | openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeSquintLeft corresponds to FB2 LID_TIGHTENER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_SQUINT_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeSquintLeft","openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.LID_TIGHTENER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeSquintRight | openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeSquintRight corresponds to FB2 LID_TIGHTENER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_SQUINT_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeSquintRight","openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.UPPER_LID_RAISER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeWideLeft | openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeWideLeft corresponds to FB2 UPPER_LID_RAISER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_WIDEN_L, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeWideLeft","openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.UPPER_LID_RAISER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeWideRight | openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeWideRight corresponds to FB2 UPPER_LID_RAISER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_WIDEN_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeWideRight","openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.JAW_THRUST

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawForward | openxr.fb2.XR_FACE_EXPRESSION2_JAW_THRUST_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawForward corresponds to FB2 JAW_THRUST; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawForward","openxr.fb2.XR_FACE_EXPRESSION2_JAW_THRUST_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.JAW_SIDEWAYS_LEFT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawLeft | openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawLeft corresponds to FB2 JAW_SIDEWAYS_LEFT; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawLeft","openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_LEFT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### arkit_fb2.JAW_DROP

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawOpen | openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawOpen corresponds to FB2 JAW_DROP; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawOpen","openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

### arkit_fb2.JAW_SIDEWAYS_RIGHT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawRight | openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawRight corresponds to FB2 JAW_SIDEWAYS_RIGHT; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawRight","openxr.fb2.XR_FACE_EXPRESSION2_JAW_SIDEWAYS_RIGHT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### arkit_fb2.LIPS_TOWARD

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthClose | openxr.fb2.XR_FACE_EXPRESSION2_LIPS_TOWARD_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthClose corresponds to FB2 LIPS_TOWARD; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthClose","openxr.fb2.XR_FACE_EXPRESSION2_LIPS_TOWARD_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, vrcft_docs_shapes, vrcft_docs_overview

### arkit_fb2.DIMPLER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthDimpleLeft | openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthDimpleLeft corresponds to FB2 DIMPLER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthDimpleLeft","openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.DIMPLER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthDimpleRight | openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthDimpleRight corresponds to FB2 DIMPLER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthDimpleRight","openxr.fb2.XR_FACE_EXPRESSION2_DIMPLER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_CORNER_DEPRESSOR_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFrownLeft | openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFrownLeft corresponds to FB2 LIP_CORNER_DEPRESSOR_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFrownLeft","openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_CORNER_DEPRESSOR_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFrownRight | openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFrownRight corresponds to FB2 LIP_CORNER_DEPRESSOR_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFrownRight","openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_DEPRESSOR_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_FUNNELER_LB

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is one coefficient; FB2 LIP_FUNNELER_LB is set to it, as are LIP_FUNNELER_LT, LIP_FUNNELER_RB, LIP_FUNNELER_RT, so that FB2 -&gt; ARKit gives mouthFunnel back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LB_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_FUNNELER_LT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is one coefficient; FB2 LIP_FUNNELER_LT is set to it, as are LIP_FUNNELER_LB, LIP_FUNNELER_RB, LIP_FUNNELER_RT, so that FB2 -&gt; ARKit gives mouthFunnel back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_LT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_FUNNELER_RB

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is one coefficient; FB2 LIP_FUNNELER_RB is set to it, as are LIP_FUNNELER_LB, LIP_FUNNELER_LT, LIP_FUNNELER_RT, so that FB2 -&gt; ARKit gives mouthFunnel back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RB_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_FUNNELER_RT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is one coefficient; FB2 LIP_FUNNELER_RT is set to it, as are LIP_FUNNELER_LB, LIP_FUNNELER_LT, LIP_FUNNELER_RB, so that FB2 -&gt; ARKit gives mouthFunnel back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","openxr.fb2.XR_FACE_EXPRESSION2_LIP_FUNNELER_RT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.MOUTH_LEFT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLeft | openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_LEFT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLeft corresponds to FB2 MOUTH_LEFT; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- FLAGGED: only Godot names ARKit mouthLeft for this channel; see fb2_arkit.mouthLeft.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLeft","openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_LEFT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_movement

### arkit_fb2.LOWER_LIP_DEPRESSOR_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLowerDownLeft | openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLowerDownLeft corresponds to FB2 LOWER_LIP_DEPRESSOR_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled LOWER_LIP_DEPRESSER_L, a misspelling (not counted: typo), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLowerDownLeft","openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.LOWER_LIP_DEPRESSOR_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLowerDownRight | openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLowerDownRight corresponds to FB2 LOWER_LIP_DEPRESSOR_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLowerDownRight","openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_PRESSOR_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPressLeft | openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPressLeft corresponds to FB2 LIP_PRESSOR_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPressLeft","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_PRESSOR_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPressRight | openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPressRight corresponds to FB2 LIP_PRESSOR_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPressRight","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PRESSOR_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_PUCKER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is one coefficient; FB2 LIP_PUCKER_L is set to it, as are LIP_PUCKER_R, so that FB2 -&gt; ARKit gives mouthPucker back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthPucker","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_PUCKER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is one coefficient; FB2 LIP_PUCKER_R is set to it, as are LIP_PUCKER_L, so that FB2 -&gt; ARKit gives mouthPucker back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthPucker","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","openxr.fb2.XR_FACE_EXPRESSION2_LIP_PUCKER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.MOUTH_RIGHT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRight | openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRight corresponds to FB2 MOUTH_RIGHT; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- FLAGGED: only Godot names ARKit mouthRight for this channel; see fb2_arkit.mouthRight.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRight","openxr.fb2.XR_FACE_EXPRESSION2_MOUTH_RIGHT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_movement

### arkit_fb2.LIP_SUCK_LB

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollLower | openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollLower is one coefficient; FB2 LIP_SUCK_LB is set to it, as are LIP_SUCK_RB, so that FB2 -&gt; ARKit gives mouthRollLower back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthRollLower","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollLower","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LB_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_SUCK_RB

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollLower | openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollLower is one coefficient; FB2 LIP_SUCK_RB is set to it, as are LIP_SUCK_LB, so that FB2 -&gt; ARKit gives mouthRollLower back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthRollLower","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollLower","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RB_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_SUCK_LT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollUpper | openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollUpper is one coefficient; FB2 LIP_SUCK_LT is set to it, as are LIP_SUCK_RT, so that FB2 -&gt; ARKit gives mouthRollUpper back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthRollUpper","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollUpper","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_LT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.LIP_SUCK_RT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollUpper | openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollUpper is one coefficient; FB2 LIP_SUCK_RT is set to it, as are LIP_SUCK_LT, so that FB2 -&gt; ARKit gives mouthRollUpper back. How the coefficient divides between the FB2 parts is unknown.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"asymmetry unknown: symmetry is invented","refs":["arkit.coefficient.mouthRollUpper","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollUpper","openxr.fb2.XR_FACE_EXPRESSION2_LIP_SUCK_RT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, vrcft_code_parameters, ict_facekit

### arkit_fb2.CHIN_RAISER_B

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthShrugLower | openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthShrugLower corresponds to FB2 CHIN_RAISER_B; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthShrugLower","openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_B_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

### arkit_fb2.CHIN_RAISER_T

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthShrugUpper | openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthShrugUpper corresponds to FB2 CHIN_RAISER_T; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthShrugUpper","openxr.fb2.XR_FACE_EXPRESSION2_CHIN_RAISER_T_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier

### arkit_fb2.LIP_CORNER_PULLER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileLeft | openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileLeft corresponds to FB2 LIP_CORNER_PULLER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileLeft","openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.LIP_CORNER_PULLER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileRight | openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileRight corresponds to FB2 LIP_CORNER_PULLER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileRight","openxr.fb2.XR_FACE_EXPRESSION2_LIP_CORNER_PULLER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, vrcft_docs_movement, vrcft_docs_arkit, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.LIP_STRETCHER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthStretchLeft | openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthStretchLeft corresponds to FB2 LIP_STRETCHER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthStretchLeft","openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.LIP_STRETCHER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthStretchRight | openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthStretchRight corresponds to FB2 LIP_STRETCHER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthStretchRight","openxr.fb2.XR_FACE_EXPRESSION2_LIP_STRETCHER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.UPPER_LIP_RAISER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthUpperUpLeft | openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthUpperUpLeft corresponds to FB2 UPPER_LIP_RAISER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthUpperUpLeft","openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### arkit_fb2.UPPER_LIP_RAISER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthUpperUpRight | openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthUpperUpRight corresponds to FB2 UPPER_LIP_RAISER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthUpperUpRight","openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LIP_RAISER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

### arkit_fb2.NOSE_WRINKLER_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.noseSneerLeft | openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit noseSneerLeft corresponds to FB2 NOSE_WRINKLER_L; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.noseSneerLeft","openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.NOSE_WRINKLER_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.noseSneerRight | openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit noseSneerRight corresponds to FB2 NOSE_WRINKLER_R; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.noseSneerRight","openxr.fb2.XR_FACE_EXPRESSION2_NOSE_WRINKLER_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.TONGUE_OUT

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.tongueOut | openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit tongueOut corresponds to FB2 TONGUE_OUT; this is the FB2 -&gt; ARKit rule read back.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.tongueOut","openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"both are extension shapes with no stated length","refs":["arkit.coefficient.tongueOut","openxr.fb2.XR_FACE_EXPRESSION2_TONGUE_OUT_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement

## arkit_gaze.to_fb2

### arkit_fb2.gaze_in_minus_out_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookInLeft, arkit.coefficient.eyeLookOutLeft | rcef.intermediate.arkit_gaze_in_minus_out_L | {"id":"weighted_sum","weights":[1.0,-1.0]} | mapped | approximate |

Assumptions:

- ARKit eyeLookInLeft and eyeLookOutLeft are opposing directions of one eye; their difference, from -1 to 1, carries both.
- FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["arkit.coefficient.eyeLookInLeft","arkit.coefficient.eyeLookOutLeft","rcef.intermediate.arkit_gaze_in_minus_out_L"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes

### arkit_fb2.EYES_LOOK_RIGHT_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_in_minus_out_L | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB | {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookInLeft corresponds to FB2 EYES_LOOK_RIGHT_L; this is the FB2 -&gt; ARKit rule read back, taking eyeLookInLeft minus eyeLookOutLeft where it is above zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.EYES_LOOK_LEFT_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_in_minus_out_L | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB | {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookOutLeft corresponds to FB2 EYES_LOOK_LEFT_L; this is the FB2 -&gt; ARKit rule read back, taking how far eyeLookInLeft minus eyeLookOutLeft is below zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_in_minus_out_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.gaze_up_minus_down_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookUpLeft, arkit.coefficient.eyeLookDownLeft | rcef.intermediate.arkit_gaze_up_minus_down_L | {"id":"weighted_sum","weights":[1.0,-1.0]} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpLeft and eyeLookDownLeft are opposing directions of one eye; their difference, from -1 to 1, carries both.
- FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["arkit.coefficient.eyeLookUpLeft","arkit.coefficient.eyeLookDownLeft","rcef.intermediate.arkit_gaze_up_minus_down_L"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes

### arkit_fb2.EYES_LOOK_UP_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_up_minus_down_L | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB | {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpLeft corresponds to FB2 EYES_LOOK_UP_L; this is the FB2 -&gt; ARKit rule read back, taking eyeLookUpLeft minus eyeLookDownLeft where it is above zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.EYES_LOOK_DOWN_L

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_up_minus_down_L | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB | {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookDownLeft corresponds to FB2 EYES_LOOK_DOWN_L; this is the FB2 -&gt; ARKit rule read back, taking how far eyeLookUpLeft minus eyeLookDownLeft is below zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_up_minus_down_L","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_L_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.gaze_in_minus_out_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookInRight, arkit.coefficient.eyeLookOutRight | rcef.intermediate.arkit_gaze_in_minus_out_R | {"id":"weighted_sum","weights":[1.0,-1.0]} | mapped | approximate |

Assumptions:

- ARKit eyeLookInRight and eyeLookOutRight are opposing directions of one eye; their difference, from -1 to 1, carries both.
- FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["arkit.coefficient.eyeLookInRight","arkit.coefficient.eyeLookOutRight","rcef.intermediate.arkit_gaze_in_minus_out_R"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes

### arkit_fb2.EYES_LOOK_LEFT_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_in_minus_out_R | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB | {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookInRight corresponds to FB2 EYES_LOOK_LEFT_R; this is the FB2 -&gt; ARKit rule read back, taking eyeLookInRight minus eyeLookOutRight where it is above zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_LEFT_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.EYES_LOOK_RIGHT_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_in_minus_out_R | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB | {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookOutRight corresponds to FB2 EYES_LOOK_RIGHT_R; this is the FB2 -&gt; ARKit rule read back, taking how far eyeLookInRight minus eyeLookOutRight is below zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_in_minus_out_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_RIGHT_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### arkit_fb2.gaze_up_minus_down_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookUpRight, arkit.coefficient.eyeLookDownRight | rcef.intermediate.arkit_gaze_up_minus_down_R | {"id":"weighted_sum","weights":[1.0,-1.0]} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpRight and eyeLookDownRight are opposing directions of one eye; their difference, from -1 to 1, carries both.
- FB2 says only one of two opposing gaze directions is non-zero at a time (xr_fb2 lines 648-649).
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["arkit.coefficient.eyeLookUpRight","arkit.coefficient.eyeLookDownRight","rcef.intermediate.arkit_gaze_up_minus_down_R"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes

### arkit_fb2.EYES_LOOK_UP_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_up_minus_down_R | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB | {"id":"piecewise_linear","knots":[[-1.0,0.0],[0.0,0.0],[1.0,1.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpRight corresponds to FB2 EYES_LOOK_UP_R; this is the FB2 -&gt; ARKit rule read back, taking eyeLookUpRight minus eyeLookDownRight where it is above zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_UP_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

### arkit_fb2.EYES_LOOK_DOWN_R

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| rcef.intermediate.arkit_gaze_up_minus_down_R | openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB | {"id":"piecewise_linear","knots":[[-1.0,1.0],[0.0,0.0],[1.0,0.0]]} | mapped | approximate |

Assumptions:

- ARKit eyeLookDownRight corresponds to FB2 EYES_LOOK_DOWN_R; this is the FB2 -&gt; ARKit rule read back, taking how far eyeLookUpRight minus eyeLookDownRight is below zero.
- ARKit neutral (0) and maximum (1) are taken to equal FB2 weight 0 (not active) and 1 (fully active), linear in between; neither provider publishes its gain curve or full-activation pose.
- A one-sided split is exactly zero on its flat side, so the two FB2 directions of a pair are never both non-zero.
- Both providers name sides from the subject's own face (ARKit coefficients are face-relative; FB2 describes 'the left eye').

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 maximum gaze angle is unspecified","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit describes eyelid movement consistent with the gaze; FB2 describes eye rotation","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB"],"units":"1"},{"category":"signal","effect":"approximated","reason":"FB2 allows only one of two opposing gaze directions to be non-zero; when ARKit sets both, only their difference is kept, as the larger direction reduced by the smaller","refs":["rcef.intermediate.arkit_gaze_up_minus_down_R","openxr.fb2.XR_FACE_EXPRESSION2_EYES_LOOK_DOWN_R_FB"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, vrcft_docs_arkit, vrcft_docs_movement, ict_facekit

## arkit.to_vrcft_artist

### arkit_vrcft_artist.BrowLowererLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownLeft | vrcft.artist.base.BrowLowererLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownLeft is a blended Unified Expressions shape; BrowLowererLeft is set to the ARKit value, as is BrowPinchLeft. VRCFaceTracking defines the blended shape as 0.75 x BrowLowererLeft + 0.25 x BrowPinchLeft; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browDownLeft","vrcft.artist.base.BrowLowererLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownLeft","vrcft.artist.base.BrowLowererLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.BrowPinchLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownLeft | vrcft.artist.base.BrowPinchLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownLeft is a blended Unified Expressions shape; BrowPinchLeft is set to the ARKit value, as is BrowLowererLeft. VRCFaceTracking defines the blended shape as 0.75 x BrowLowererLeft + 0.25 x BrowPinchLeft; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browDownLeft","vrcft.artist.base.BrowPinchLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownLeft","vrcft.artist.base.BrowPinchLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.BrowLowererRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownRight | vrcft.artist.base.BrowLowererRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownRight is a blended Unified Expressions shape; BrowLowererRight is set to the ARKit value, as is BrowPinchRight. VRCFaceTracking defines the blended shape as 0.75 x BrowLowererRight + 0.25 x BrowPinchRight; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browDownRight","vrcft.artist.base.BrowLowererRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownRight","vrcft.artist.base.BrowLowererRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.BrowPinchRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browDownRight | vrcft.artist.base.BrowPinchRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browDownRight is a blended Unified Expressions shape; BrowPinchRight is set to the ARKit value, as is BrowLowererRight. VRCFaceTracking defines the blended shape as 0.75 x BrowLowererRight + 0.25 x BrowPinchRight; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browDownRight","vrcft.artist.base.BrowPinchRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browDownRight","vrcft.artist.base.BrowPinchRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.BrowInnerUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browInnerUp | vrcft.artist.base.BrowInnerUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browInnerUp is a blended Unified Expressions shape; BrowInnerUpRight is set to the ARKit value, as is BrowInnerUpLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browInnerUp","vrcft.artist.base.BrowInnerUpRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browInnerUp","vrcft.artist.base.BrowInnerUpRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.BrowInnerUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browInnerUp | vrcft.artist.base.BrowInnerUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browInnerUp is a blended Unified Expressions shape; BrowInnerUpLeft is set to the ARKit value, as is BrowInnerUpRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.browInnerUp","vrcft.artist.base.BrowInnerUpLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browInnerUp","vrcft.artist.base.BrowInnerUpLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.BrowOuterUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpLeft | vrcft.artist.base.BrowOuterUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browOuterUpLeft corresponds to Unified Expressions BrowOuterUpLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browOuterUpLeft","vrcft.artist.base.BrowOuterUpLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.BrowOuterUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.browOuterUpRight | vrcft.artist.base.BrowOuterUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit browOuterUpRight corresponds to Unified Expressions BrowOuterUpRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.browOuterUpRight","vrcft.artist.base.BrowOuterUpRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.CheekPuffRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekPuff | vrcft.artist.base.CheekPuffRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekPuff is a blended Unified Expressions shape; CheekPuffRight is set to the ARKit value, as is CheekPuffLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.cheekPuff","vrcft.artist.base.CheekPuffRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekPuff","vrcft.artist.base.CheekPuffRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.CheekPuffLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekPuff | vrcft.artist.base.CheekPuffLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekPuff is a blended Unified Expressions shape; CheekPuffLeft is set to the ARKit value, as is CheekPuffRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.cheekPuff","vrcft.artist.base.CheekPuffLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekPuff","vrcft.artist.base.CheekPuffLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.CheekSquintLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekSquintLeft | vrcft.artist.base.CheekSquintLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekSquintLeft corresponds to Unified Expressions CheekSquintLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekSquintLeft","vrcft.artist.base.CheekSquintLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.CheekSquintRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.cheekSquintRight | vrcft.artist.base.CheekSquintRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit cheekSquintRight corresponds to Unified Expressions CheekSquintRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.cheekSquintRight","vrcft.artist.base.CheekSquintRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeClosedLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkLeft | vrcft.artist.base.EyeClosedLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeBlinkLeft corresponds to Unified Expressions EyeClosedLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeBlinkLeft","vrcft.artist.base.EyeClosedLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeClosedRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeBlinkRight | vrcft.artist.base.EyeClosedRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeBlinkRight corresponds to Unified Expressions EyeClosedRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeBlinkRight","vrcft.artist.base.EyeClosedRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookDownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookDownLeft | vrcft.artist.base.EyeLookDownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookDownLeft corresponds to Unified Expressions EyeLookDownLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookDownLeft","vrcft.artist.base.EyeLookDownLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookDownLeft","vrcft.artist.base.EyeLookDownLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookDownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookDownRight | vrcft.artist.base.EyeLookDownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookDownRight corresponds to Unified Expressions EyeLookDownRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookDownRight","vrcft.artist.base.EyeLookDownRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookDownRight","vrcft.artist.base.EyeLookDownRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookInLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookInLeft | vrcft.artist.base.EyeLookInLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookInLeft corresponds to Unified Expressions EyeLookInLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookInLeft","vrcft.artist.base.EyeLookInLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookInLeft","vrcft.artist.base.EyeLookInLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookInRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookInRight | vrcft.artist.base.EyeLookInRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookInRight corresponds to Unified Expressions EyeLookInRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookInRight","vrcft.artist.base.EyeLookInRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookInRight","vrcft.artist.base.EyeLookInRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookOutLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookOutLeft | vrcft.artist.base.EyeLookOutLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookOutLeft corresponds to Unified Expressions EyeLookOutLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookOutLeft","vrcft.artist.base.EyeLookOutLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookOutLeft","vrcft.artist.base.EyeLookOutLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookOutRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookOutRight | vrcft.artist.base.EyeLookOutRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookOutRight corresponds to Unified Expressions EyeLookOutRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookOutRight","vrcft.artist.base.EyeLookOutRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookOutRight","vrcft.artist.base.EyeLookOutRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookUpLeft | vrcft.artist.base.EyeLookUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpLeft corresponds to Unified Expressions EyeLookUpLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookUpLeft","vrcft.artist.base.EyeLookUpLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookUpLeft","vrcft.artist.base.EyeLookUpLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeLookUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeLookUpRight | vrcft.artist.base.EyeLookUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeLookUpRight corresponds to Unified Expressions EyeLookUpRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeLookUpRight","vrcft.artist.base.EyeLookUpRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"ARKit and Unified Expressions both describe eyelid and eye movement for gaze; neither states a maximum angle","refs":["arkit.coefficient.eyeLookUpRight","vrcft.artist.base.EyeLookUpRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeSquintLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeSquintLeft | vrcft.artist.base.EyeSquintLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeSquintLeft corresponds to Unified Expressions EyeSquintLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeSquintLeft","vrcft.artist.base.EyeSquintLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeSquintRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeSquintRight | vrcft.artist.base.EyeSquintRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeSquintRight corresponds to Unified Expressions EyeSquintRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeSquintRight","vrcft.artist.base.EyeSquintRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeWideLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeWideLeft | vrcft.artist.base.EyeWideLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeWideLeft corresponds to Unified Expressions EyeWideLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeWideLeft","vrcft.artist.base.EyeWideLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.EyeWideRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.eyeWideRight | vrcft.artist.base.EyeWideRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit eyeWideRight corresponds to Unified Expressions EyeWideRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.eyeWideRight","vrcft.artist.base.EyeWideRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.JawForward

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawForward | vrcft.artist.base.JawForward | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawForward corresponds to Unified Expressions JawForward (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawForward","vrcft.artist.base.JawForward"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.JawLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawLeft | vrcft.artist.base.JawLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawLeft corresponds to Unified Expressions JawLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawLeft","vrcft.artist.base.JawLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.JawOpen

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawOpen | vrcft.artist.base.JawOpen | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawOpen corresponds to Unified Expressions JawOpen (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawOpen","vrcft.artist.base.JawOpen"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.JawRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.jawRight | vrcft.artist.base.JawRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit jawRight corresponds to Unified Expressions JawRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.jawRight","vrcft.artist.base.JawRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthClosed

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthClose | vrcft.artist.base.MouthClosed | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthClose corresponds to Unified Expressions MouthClosed (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthClose","vrcft.artist.base.MouthClosed"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthDimpleLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthDimpleLeft | vrcft.artist.base.MouthDimpleLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthDimpleLeft corresponds to Unified Expressions MouthDimpleLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthDimpleLeft","vrcft.artist.base.MouthDimpleLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthDimpleRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthDimpleRight | vrcft.artist.base.MouthDimpleRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthDimpleRight corresponds to Unified Expressions MouthDimpleRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthDimpleRight","vrcft.artist.base.MouthDimpleRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthFrownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFrownLeft | vrcft.artist.base.MouthFrownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFrownLeft corresponds to Unified Expressions MouthFrownLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFrownLeft","vrcft.artist.base.MouthFrownLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthFrownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFrownRight | vrcft.artist.base.MouthFrownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFrownRight corresponds to Unified Expressions MouthFrownRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFrownRight","vrcft.artist.base.MouthFrownRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.LipFunnelUpperRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | vrcft.artist.base.LipFunnelUpperRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is a blended Unified Expressions shape; LipFunnelUpperRight is set to the ARKit value, as is LipFunnelUpperLeft, LipFunnelLowerRight, LipFunnelLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelUpperRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelUpperRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipFunnelUpperLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | vrcft.artist.base.LipFunnelUpperLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is a blended Unified Expressions shape; LipFunnelUpperLeft is set to the ARKit value, as is LipFunnelUpperRight, LipFunnelLowerRight, LipFunnelLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelUpperLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelUpperLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipFunnelLowerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | vrcft.artist.base.LipFunnelLowerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is a blended Unified Expressions shape; LipFunnelLowerRight is set to the ARKit value, as is LipFunnelUpperRight, LipFunnelUpperLeft, LipFunnelLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelLowerRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelLowerRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipFunnelLowerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthFunnel | vrcft.artist.base.LipFunnelLowerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthFunnel is a blended Unified Expressions shape; LipFunnelLowerLeft is set to the ARKit value, as is LipFunnelUpperRight, LipFunnelUpperLeft, LipFunnelLowerRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelLowerLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthFunnel","vrcft.artist.base.LipFunnelLowerLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.MouthUpperLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLeft | vrcft.artist.base.MouthUpperLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLeft is a blended Unified Expressions shape; MouthUpperLeft is set to the ARKit value, as is MouthLowerLeft. Godot builds the blended shape from these two parts; VRCFaceTracking pairs FB2 MOUTH_LEFT with the blended shape.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- FLAGGED: VRCFaceTracking's ARKit table has no mouthLeft row; only Godot names the ARKit coefficient for the blended Unified shape.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthLeft","vrcft.artist.base.MouthUpperLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLeft","vrcft.artist.base.MouthUpperLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_movement

### arkit_vrcft_artist.MouthLowerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLeft | vrcft.artist.base.MouthLowerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLeft is a blended Unified Expressions shape; MouthLowerLeft is set to the ARKit value, as is MouthUpperLeft. Godot builds the blended shape from these two parts; VRCFaceTracking pairs FB2 MOUTH_LEFT with the blended shape.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- FLAGGED: VRCFaceTracking's ARKit table has no mouthLeft row; only Godot names the ARKit coefficient for the blended Unified shape.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthLeft","vrcft.artist.base.MouthLowerLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLeft","vrcft.artist.base.MouthLowerLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_movement

### arkit_vrcft_artist.MouthLowerDownLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLowerDownLeft | vrcft.artist.base.MouthLowerDownLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLowerDownLeft corresponds to Unified Expressions MouthLowerDownLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLowerDownLeft","vrcft.artist.base.MouthLowerDownLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthLowerDownRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthLowerDownRight | vrcft.artist.base.MouthLowerDownRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthLowerDownRight corresponds to Unified Expressions MouthLowerDownRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthLowerDownRight","vrcft.artist.base.MouthLowerDownRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthPressLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPressLeft | vrcft.artist.base.MouthPressLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPressLeft corresponds to Unified Expressions MouthPressLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPressLeft","vrcft.artist.base.MouthPressLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthPressRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPressRight | vrcft.artist.base.MouthPressRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPressRight corresponds to Unified Expressions MouthPressRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPressRight","vrcft.artist.base.MouthPressRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.LipPuckerUpperRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | vrcft.artist.base.LipPuckerUpperRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is a blended Unified Expressions shape; LipPuckerUpperRight is set to the ARKit value, as is LipPuckerUpperLeft, LipPuckerLowerRight, LipPuckerLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerUpperRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerUpperRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipPuckerUpperLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | vrcft.artist.base.LipPuckerUpperLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is a blended Unified Expressions shape; LipPuckerUpperLeft is set to the ARKit value, as is LipPuckerUpperRight, LipPuckerLowerRight, LipPuckerLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerUpperLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerUpperLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipPuckerLowerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | vrcft.artist.base.LipPuckerLowerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is a blended Unified Expressions shape; LipPuckerLowerRight is set to the ARKit value, as is LipPuckerUpperRight, LipPuckerUpperLeft, LipPuckerLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerLowerRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerLowerRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipPuckerLowerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthPucker | vrcft.artist.base.LipPuckerLowerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthPucker is a blended Unified Expressions shape; LipPuckerLowerLeft is set to the ARKit value, as is LipPuckerUpperRight, LipPuckerUpperLeft, LipPuckerLowerRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerLowerLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthPucker","vrcft.artist.base.LipPuckerLowerLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.MouthUpperRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRight | vrcft.artist.base.MouthUpperRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRight is a blended Unified Expressions shape; MouthUpperRight is set to the ARKit value, as is MouthLowerRight. Godot builds the blended shape from these two parts; VRCFaceTracking pairs FB2 MOUTH_RIGHT with the blended shape.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- FLAGGED: VRCFaceTracking's ARKit table has no mouthRight row; only Godot names the ARKit coefficient for the blended Unified shape.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRight","vrcft.artist.base.MouthUpperRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRight","vrcft.artist.base.MouthUpperRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_movement

### arkit_vrcft_artist.MouthLowerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRight | vrcft.artist.base.MouthLowerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRight is a blended Unified Expressions shape; MouthLowerRight is set to the ARKit value, as is MouthUpperRight. Godot builds the blended shape from these two parts; VRCFaceTracking pairs FB2 MOUTH_RIGHT with the blended shape.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- FLAGGED: VRCFaceTracking's ARKit table has no mouthRight row; only Godot names the ARKit coefficient for the blended Unified shape.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRight","vrcft.artist.base.MouthLowerRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRight","vrcft.artist.base.MouthLowerRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_movement

### arkit_vrcft_artist.LipSuckLowerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollLower | vrcft.artist.base.LipSuckLowerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollLower is a blended Unified Expressions shape; LipSuckLowerRight is set to the ARKit value, as is LipSuckLowerLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRollLower","vrcft.artist.base.LipSuckLowerRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollLower","vrcft.artist.base.LipSuckLowerRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipSuckLowerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollLower | vrcft.artist.base.LipSuckLowerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollLower is a blended Unified Expressions shape; LipSuckLowerLeft is set to the ARKit value, as is LipSuckLowerRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRollLower","vrcft.artist.base.LipSuckLowerLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollLower","vrcft.artist.base.LipSuckLowerLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipSuckUpperRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollUpper | vrcft.artist.base.LipSuckUpperRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollUpper is a blended Unified Expressions shape; LipSuckUpperRight is set to the ARKit value, as is LipSuckUpperLeft. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRollUpper","vrcft.artist.base.LipSuckUpperRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollUpper","vrcft.artist.base.LipSuckUpperRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.LipSuckUpperLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthRollUpper | vrcft.artist.base.LipSuckUpperLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthRollUpper is a blended Unified Expressions shape; LipSuckUpperLeft is set to the ARKit value, as is LipSuckUpperRight. VRCFaceTracking computes the blended shape as the mean of these parts, so copying the ARKit value into each part gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthRollUpper","vrcft.artist.base.LipSuckUpperLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthRollUpper","vrcft.artist.base.LipSuckUpperLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_code_parameters

### arkit_vrcft_artist.MouthRaiserLower

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthShrugLower | vrcft.artist.base.MouthRaiserLower | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthShrugLower corresponds to Unified Expressions MouthRaiserLower (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthShrugLower","vrcft.artist.base.MouthRaiserLower"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthRaiserUpper

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthShrugUpper | vrcft.artist.base.MouthRaiserUpper | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthShrugUpper corresponds to Unified Expressions MouthRaiserUpper (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthShrugUpper","vrcft.artist.base.MouthRaiserUpper"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthCornerPullLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileLeft | vrcft.artist.base.MouthCornerPullLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileLeft is a blended Unified Expressions shape; MouthCornerPullLeft is set to the ARKit value, as is MouthCornerSlantLeft. VRCFaceTracking defines the blended shape as 0.8 x MouthCornerPullLeft + 0.2 x MouthCornerSlantLeft; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthSmileLeft","vrcft.artist.base.MouthCornerPullLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileLeft","vrcft.artist.base.MouthCornerPullLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.MouthCornerSlantLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileLeft | vrcft.artist.base.MouthCornerSlantLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileLeft is a blended Unified Expressions shape; MouthCornerSlantLeft is set to the ARKit value, as is MouthCornerPullLeft. VRCFaceTracking defines the blended shape as 0.8 x MouthCornerPullLeft + 0.2 x MouthCornerSlantLeft; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthSmileLeft","vrcft.artist.base.MouthCornerSlantLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileLeft","vrcft.artist.base.MouthCornerSlantLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.MouthCornerPullRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileRight | vrcft.artist.base.MouthCornerPullRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileRight is a blended Unified Expressions shape; MouthCornerPullRight is set to the ARKit value, as is MouthCornerSlantRight. VRCFaceTracking defines the blended shape as 0.8 x MouthCornerPullRight + 0.2 x MouthCornerSlantRight; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthSmileRight","vrcft.artist.base.MouthCornerPullRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileRight","vrcft.artist.base.MouthCornerPullRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.MouthCornerSlantRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthSmileRight | vrcft.artist.base.MouthCornerSlantRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthSmileRight is a blended Unified Expressions shape; MouthCornerSlantRight is set to the ARKit value, as is MouthCornerPullRight. VRCFaceTracking defines the blended shape as 0.8 x MouthCornerPullRight + 0.2 x MouthCornerSlantRight; the weights sum to 1, so copying the ARKit value into both parts gives it back.
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"Unified Expressions splits this shape into parts whose ratio cannot be recovered from ARKit; the parts are set equal","refs":["arkit.coefficient.mouthSmileRight","vrcft.artist.base.MouthCornerSlantRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthSmileRight","vrcft.artist.base.MouthCornerSlantRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit, vrcft_simple_expressions

### arkit_vrcft_artist.MouthStretchLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthStretchLeft | vrcft.artist.base.MouthStretchLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthStretchLeft corresponds to Unified Expressions MouthStretchLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthStretchLeft","vrcft.artist.base.MouthStretchLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthStretchRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthStretchRight | vrcft.artist.base.MouthStretchRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthStretchRight corresponds to Unified Expressions MouthStretchRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthStretchRight","vrcft.artist.base.MouthStretchRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthUpperUpLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthUpperUpLeft | vrcft.artist.base.MouthUpperUpLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthUpperUpLeft corresponds to Unified Expressions MouthUpperUpLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthUpperUpLeft","vrcft.artist.base.MouthUpperUpLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.MouthUpperUpRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.mouthUpperUpRight | vrcft.artist.base.MouthUpperUpRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit mouthUpperUpRight corresponds to Unified Expressions MouthUpperUpRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.mouthUpperUpRight","vrcft.artist.base.MouthUpperUpRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.NoseSneerLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.noseSneerLeft | vrcft.artist.base.NoseSneerLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit noseSneerLeft corresponds to Unified Expressions NoseSneerLeft (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.noseSneerLeft","vrcft.artist.base.NoseSneerLeft"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.NoseSneerRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.noseSneerRight | vrcft.artist.base.NoseSneerRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit noseSneerRight corresponds to Unified Expressions NoseSneerRight (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.
- Both name sides from the subject's own face (ARKit coefficients are face-relative; Unified Expressions shapes name the avatar's own side).

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.noseSneerRight","vrcft.artist.base.NoseSneerRight"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

### arkit_vrcft_artist.TongueOut

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| arkit.coefficient.tongueOut | vrcft.artist.base.TongueOut | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- ARKit tongueOut corresponds to Unified Expressions TongueOut (VRCFaceTracking ARKit table; Godot face-modifier name table).
- ARKit neutral (0) and maximum (1) are taken to equal the Unified Expressions shape at rest (0) and fully applied (1), linear in between; neither publishes its gain curve or full-activation pose.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["arkit.coefficient.tongueOut","vrcft.artist.base.TongueOut"],"units":"1"},{"category":"signal","effect":"approximated","reason":"both are extension shapes with no stated length","refs":["arkit.coefficient.tongueOut","vrcft.artist.base.TongueOut"],"units":"1"}]

Evidence: apple_blendshapes, vrcft_artist, godot_face_modifier, vrcft_docs_arkit

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
- FB2 closes the lips regardless of the jaw position; Unified Expressions defines MouthClosed relative to JawOpen and SRanipal requires Jaw_Open to be inactive. The value is copied without compensating for the jaw.

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
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_SQUINT_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_L_FB","arkit.coefficient.eyeSquintLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeSquintRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB | arkit.coefficient.eyeSquintRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 LID_TIGHTENER_R corresponds to ARKit eyeSquintRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_SQUINT_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LID_TIGHTENER_R_FB","arkit.coefficient.eyeSquintRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeWideLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB | arkit.coefficient.eyeWideLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LID_RAISER_L corresponds to ARKit eyeWideLeft.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_WIDEN_L, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_L_FB","arkit.coefficient.eyeWideLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

### fb2_arkit.eyeWideRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB | arkit.coefficient.eyeWideRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 UPPER_LID_RAISER_R corresponds to ARKit eyeWideRight.
- FB2 weight 0 (not active) and 1 (fully active) are taken to equal ARKit neutral (0) and maximum (1), linear in between; neither provider publishes its gain curve or full-activation pose.
- Both providers name sides from the subject's own face (FB2 describes 'the left eye'; ARKit coefficients are face-relative).
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled EYES_WIDEN_R, not an OpenXR name (not counted: non-OpenXR label), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_UPPER_LID_RAISER_R_FB","arkit.coefficient.eyeWideRight"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

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
- VRCFaceTracking's tables are not cited: its Movement row for this shape is labelled LOWER_LIP_DEPRESSER_L, a misspelling (not counted: typo), and without that row its ARKit table does not reach FB2.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"provider gain and full-activation pose are not published; 0 and 1 endpoints assumed equal","refs":["openxr.fb2.XR_FACE_EXPRESSION2_LOWER_LIP_DEPRESSOR_L_FB","arkit.coefficient.mouthLowerDownLeft"],"units":"1"}]

Evidence: xr_fb2, apple_blendshapes, godot_vendors_fb2, godot_face_modifier, ict_facekit

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

## fb2.to_vrm

### fb2_vrm.blinkLeft

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB | vrm.preset.blinkLeft | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_CLOSED_L (lowers the top eyelid of the left eye) corresponds to VRM preset blinkLeft (closes the left eyelid); definitional only: the definitions agree, but no published table maps FB2 to VRM.
- FB2 weight (0 to 1) is used directly as the VRM expression weight (0 to 1).
- Both name sides from the subject's own face. FLAGGED: VRM gives no normative side; on the VRM 1.0 Twist sample blinkLeft moves the avatar's own left eyelid.
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"an FB2 weight becomes an asset-authored expression weight","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB","vrm.preset.blinkLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"VRM blink (both eyes) is left unset, so a model that binds only blink, not blinkLeft and blinkRight, does not blink","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB","vrm.preset.blinkLeft"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a model may mark the preset isBinary, which turns a partial closure into fully open or fully closed","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_L_FB","vrm.preset.blinkLeft"],"units":"1"}]

Evidence: xr_fb2, vrm_expressions

### fb2_vrm.blinkRight

| Inputs | Outputs | Operator | Status | Quality |
| --- | --- | --- | --- | --- |
| openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB | vrm.preset.blinkRight | {"id":"affine","offset":0.0,"scale":1.0} | mapped | approximate |

Assumptions:

- FB2 EYES_CLOSED_R (lowers the top eyelid of the right eye) corresponds to VRM preset blinkRight (closes the right eyelid); definitional only: the definitions agree, but no published table maps FB2 to VRM.
- FB2 weight (0 to 1) is used directly as the VRM expression weight (0 to 1).
- Both name sides from the subject's own face. FLAGGED: VRM gives no normative side; on the VRM 1.0 Twist sample blinkRight moves the avatar's own right eyelid.
- VRM isBinary and override effects happen downstream in the VRM runtime and are not modelled.

Loss annotations: [{"category":"signal","effect":"approximated","reason":"an FB2 weight becomes an asset-authored expression weight","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB","vrm.preset.blinkRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"VRM blink (both eyes) is left unset, so a model that binds only blink, not blinkLeft and blinkRight, does not blink","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB","vrm.preset.blinkRight"],"units":"1"},{"category":"signal","effect":"approximated","reason":"a model may mark the preset isBinary, which turns a partial closure into fully open or fully closed","refs":["openxr.fb2.XR_FACE_EXPRESSION2_EYES_CLOSED_R_FB","vrm.preset.blinkRight"],"units":"1"}]

Evidence: xr_fb2, vrm_expressions

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

