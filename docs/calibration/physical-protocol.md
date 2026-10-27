# Physical capture protocol (design only)

This is a design. It has not been run, no one has been recorded, and nothing in RCEF depends on it. It describes how RCEF could one day measure what software-only calibration cannot: how real trackers respond to real faces. Before any of it is run it needs a named owner, ethics and legal review, and Ken's approval.

## What it would measure, and what it would not

Software-only records (see [calibration/README.md](../../calibration/README.md)) can say how a model or rig responds to renders. They cannot say how a tracker responds to a person. This protocol targets three questions:

| Package | Question | Devices |
|---|---|---|
| R-CAP1 | How do iPhone ARKit and MediaPipe each report the same blink and jaw opening? | iPhone with a TrueDepth camera running ARKit face tracking; MediaPipe Face Landmarker run on the same camera frames |
| R-CAP2 | How does Quest Pro FB2 face tracking compare with ARKit for the same movements? | Quest Pro (FB2 face tracking) and the iPhone, recorded together |
| R-CAP3 | What pupil diameter, in millimetres, goes with a reported pupil value? | a calibrated eye-tracking instrument that reports pupil diameter in mm |

It would not establish anything about people the sample does not represent, about devices or software versions not tested, about latency beyond the sync error, or about what a provider's confidence values mean.

## R-CAP1: ARKit and MediaPipe on one camera feed

- One iPhone records the ARKit coefficients and the colour frames ARKit used, with ARKit's own timestamps. MediaPipe runs on those same frames afterwards, so both see exactly the same images and no camera-to-camera alignment is needed.
- Stimuli: blink (both eyes, then each eye), and jaw open in slow steps from closed to fully open and back, each held for a few seconds. Prompts are shown on a screen next to the camera.
- The video frames exist only long enough to run MediaPipe during the session (see Retention).

## R-CAP2: Quest Pro FB2 with the iPhone

- **Lower face, headset on.** The participant wears the Quest Pro while the iPhone records the face at the same time. The headset hides the brows and eyes from the iPhone, so only lower-face channels (jaw, lips, cheeks) are compared in this session.
- **Upper face, headset off.** A separate session, iPhone only, with the same prompts for brows, lids and eyes. FB2 and ARKit upper-face responses are then compared through the prompts, not frame by frame, because they were never recorded together. This is weaker evidence and records must say so.
- **Gaze.** A fixation reference: targets at known angles on a screen at a measured distance, so each gaze sample has a known direction. Without it neither provider's gaze values can be turned into angles.

## R-CAP3: pupil with an instrument

A calibrated eye tracker that reports pupil diameter in millimetres runs alongside the tracker under test, under controlled light steps. The instrument's own calibration certificate or procedure is recorded. No pupil claim is made from cameras alone.

## Clock sync

- A flash event at the start and end of each recording (a screen flash visible to every camera, plus its timestamp on the controlling machine) gives each device's offset and drift.
- A jaw-open cross-correlation then refines the alignment: jaw opening is large and visible to every tracker, so the lag that best lines up the jaw signals is checked against the flash offset. If the two disagree by more than one frame, the recording is not used.
- The remaining sync error is reported with the results.

## Participants

- Typical studies of this kind use 10 to 30 participants. The number, and how participants are chosen to cover face shape, skin tone, age, glasses and facial hair, is fixed before recruiting and written into the record's frozen part.
- Results are held out by participant, not by frame: participants used to fit a curve are never used to test it.

## Consent, law and retention

This is a list of what review must cover, not legal advice.

- **Consent:** informed, written, specific to this study, withdrawable at any time, with a plain description of what is kept.
- **DPIA:** a data protection impact assessment before any capture.
- **GDPR Article 9:** face geometry processed this way may be special-category (biometric) data; the legal basis and safeguards must be settled first.
- **BIPA (Illinois) and similar laws:** a written retention and destruction policy, written consent before collection, and no sale or sharing of biometric data.
- **Retention:** weights only. Video and images are processed during the session and deleted at capture; they are never written to long-term storage. What is kept is the per-frame tracker outputs (ARKit coefficients, MediaPipe scores, FB2 weights, pupil values) with timestamps, under a random participant code, and the code-to-person key is destroyed after the session. Published records contain only fitted curves and aggregate metrics, never per-participant data.

## From results to records

Results would become calibration records in the K1 format with status `calibrated_measured`, which `check.py` refuses today. Allowing it needs a reviewed change to the format and to `check.py`. The intended shape:

- **Freeze first.** Before capture: the method, channels, devices and software versions, prompts, participant numbers, the split into fit and held-out participants, the bounds and the minimum conditions per cell go into the record's frozen part, and its hash goes into `calibration/FREEZES`.
- **Devices instead of a renderer.** A `capture` table would replace `renderer`: device models, OS and app or runtime versions, the eye-tracking instrument and its calibration, and the measured sync error.
- **Cells per participant group, not per person.** Each cell reports median, p95, neutral error and failures (missed detections) over at least 20 conditions, for the held-out participants only, without pooling across cells.
- **Scope and limitations.** `scope` would name the devices and versions tested, and the limitations would state who the sample does not represent and, for R-CAP2's upper face, that the comparison is across sessions.
- A channel that misses its bounds is published as a negative result, with no rule.
