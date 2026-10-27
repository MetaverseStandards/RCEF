# MediaPipe Face Landmarker: licence and training-data check

Before RCEF fits any curve to MediaPipe's blendshape scores, this note records what the model's licence and training-data statements say, as downloaded on 2026-10-27. The downloaded files are not committed; their SHA-256 hashes are below so they can be checked again.

**Result: passed.** The three model cards linked from Google's Face Landmarker guide each state "Licensed under Apache License, Version 2.0", and the blendshape model card describes its training data. Using the model to score renders of RCEF's example rigs, and publishing curves fitted to those scores under CC BY-SA 4.0, is compatible with Apache 2.0 as far as this check can tell. This is not legal advice.

## What was downloaded

| File | URL | SHA-256 | Server last-modified |
|---|---|---|---|
| `face_landmarker.task` (float16, version 1) | https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task | `64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff` | 2023-05-03 |
| the same bundle at `float16/latest` | https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task | same bytes as version 1 | 2023-05-03 |
| Blendshape V2 model card (PDF, 6 pages) | https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf | `c8e9cf60a39998f4b341740623917590e050d1c97004e2de4568d84e026445ae` | 2023-05-12 |
| Face Mesh V2 model card (PDF, 7 pages) | https://storage.googleapis.com/mediapipe-assets/Model%20Card%20MediaPipe%20Face%20Mesh%20V2.pdf | `c6add060f4ebfb37b2690136b6c711c7e5fcb7038baa2649ae3338b83979565a` | 2023-05-12 |
| BlazeFace short-range detector model card (PDF) | https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf | `cd335c06fc0de7807cd815a0777a697932598bcdb28fa98adaaabf847485f758` | 2023-05-04 |
| Face Landmarker guide (HTML) | https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker (redirects to developers.google.com/edge/…) | `7f2d18484346d41ec509f671de3ae940e2fdf5573c5ea5321c7fce7c1dcd4525` (page bytes change with each render) | page says "Last updated 2026-10-09" |

The bundle holds four files: `face_detector.tflite`, `face_landmarks_detector.tflite`, `face_blendshapes.tflite` and `geometry_pipeline_metadata_landmarks.binarypb`. It contains no licence file; the licence comes from the model cards. The guide's "Models" section links these three cards for this bundle and names the blendshape model with its 1 × 146 × 2 input.

## What the cards say

**Blendshape V2** (model date 11 November 2022; authors Grishchenko, Yan, Zanfir and Bazavan, Google):
- Licensed under Apache License, Version 2.0.
- Predicts 52 blendshape coefficients in [0, 1] from 146 of FaceMesh's 478 landmarks.
- Training data: "millions of samples generated with diverse identities", from samples "captured in a controlled environment in the lab", each with "aligned multi-view images with reconstructed unified 3D GHUM Mesh of a human subject" performing a predefined set of expressions. The 52 blendshapes were "automatically transferred from the canonical Mesh", whose blendshapes "were designed by an artist".
- Intended for AR entertainment from selfie video; not for faces turned more than 80° from the camera, less than half visible, or too small.
- Evaluation: 18,199 test items, mean absolute deviation 0.199 overall, reported across perceived gender and skin tone (Monk scale).

**Face Mesh V2** (model date 15 September 2022): Apache License, Version 2.0. Trained on smartphone front-camera selfies in real-world conditions; evaluated over 17 geographic subregions.

**BlazeFace short range** (date 9 June 2021): Apache License, Version 2.0. "Trained and evaluated on consented images of people using a mobile AR application."

## Things to note

- The Blendshape V2 card lists 52 names, including `tongueOut` and `cheekPuff` "predicted by the FaceMesh model". The runtime task graph RCEF already pins (evidence `mediapipe`, MediaPipe `f6988c4`) returns `_neutral` and 51 ARKit names, without `tongueOut`. RCEF follows the runtime list.
- The cards were last modified in May 2023 and the bundle in May 2023; the guide still links these cards for the current bundle. No newer card was found.
- Nothing here says how the scores relate to Apple's ARKit coefficients beyond sharing their names. That relationship is what the K4 fit measures, and only for untextured renders: any curve is "MediaPipe's response to untextured ICT renders", not a calibration of MediaPipe on real faces.
- Running the model needs the `mediapipe` Python package (Apache 2.0). It is an optional tool dependency, not used by `check.py` or the tests.
