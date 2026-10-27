# Physical capture protocol (design only)

This is a design only. It has not been run, no one has been recorded, and nothing in RCEF depends on it. It describes how RCEF could one day measure what software-only calibration cannot: how real trackers respond to real faces. Before any part of it runs, it needs a named owner, an ethics and legal review, and Ken's approval.

## What it would measure, and what it would not

Software-only records (see [calibration/README.md](../../calibration/README.md)) can show how a model or rig responds to renders. They cannot show how a tracker responds to a person. This protocol asks three questions:

| Package | Question | Devices |
|---|---|---|
| R-CAP1 | How do iPhone ARKit and MediaPipe each report the same blink and jaw opening? | iPhone with a TrueDepth camera running ARKit face tracking; MediaPipe Face Landmarker run on the same camera frames |
| R-CAP2 | How does Quest Pro FB2 face tracking compare with ARKit for the same movements? | Quest Pro (FB2 face tracking) and the iPhone, recorded together |
| R-CAP3 | What pupil diameter, in millimetres, goes with a reported pupil value? | a calibrated eye-tracking instrument that reports pupil diameter in mm |

It would show nothing about people the sample does not represent, about devices or software versions that were not tested, about latency beyond the sync error, or about what a provider's confidence values mean.

## R-CAP1: ARKit and MediaPipe on one camera feed

- One iPhone records the ARKit coefficients and the colour frames that ARKit used, with ARKit's own timestamps. MediaPipe runs on the same frames afterwards. So both see exactly the same images, and no alignment between cameras is needed.
- Stimuli: blink (both eyes, then each eye), and jaw open in slow steps from closed to fully open and back, each held for a few seconds. Prompts are shown on a screen next to the camera.
- The video frames exist only long enough to run MediaPipe during the session (see Retention).

## R-CAP2: Quest Pro FB2 with the iPhone

- **Lower face, headset on.** The participant wears the Quest Pro, and the iPhone records the face at the same time. The headset hides the brows and eyes from the iPhone, so this session compares only lower-face channels (jaw, lips, cheeks).
- **Upper face, headset off.** A separate session uses only the iPhone, with the same prompts for brows, lids and eyes. FB2 and ARKit upper-face responses are then compared through the prompts, not frame by frame, because they were never recorded together. This is weaker evidence, and records must say so.
- **Gaze.** A fixation reference gives each gaze sample a known direction: targets at known angles on a screen at a measured distance. Without it, neither provider's gaze values can be turned into angles.

## R-CAP3: pupil with an instrument

A calibrated eye tracker that reports pupil diameter in millimetres runs next to the tracker under test, under controlled steps of light. The instrument's own calibration certificate or procedure is recorded. No claim about pupils is made from cameras alone.

## Clock sync, per device

Each pairing gets a sync event that both of its devices can actually sense.

- **R-CAP1 needs none.** ARKit and MediaPipe read the same camera frames, so they share ARKit's frame timestamps.
- **R-CAP2, Quest Pro and iPhone (headset on).** The Quest Pro's face cameras face inward, and its FB2 output is only weights, so it cannot see a screen flash. The headset also hides the eyes from the iPhone, so blinks cannot be used. Instead, the participant makes three sharp jaw-open pulses on cue at the start of each recording, and three at the end. Both devices report jaw opening. The lag that best lines up the two jaw signals around each set of pulses gives the offset, and the start and end sets together give the drift. If the jaw signals around the pulses still differ by more than one frame after alignment, the recording is not used. The remaining error is reported with the results.
- **R-CAP2, upper face (headset off).** Only the iPhone records, so there is nothing to sync between devices. Prompts are matched by the timestamps of the controlling machine.
- **R-CAP3, pupil.** The instrument does not report jaw movement, so the light steps are its sync events. The light controller logs the time of each step. Both the instrument and the tracker under test see the pupil constriction that follows. The step onsets align the two, and the error is reported in the same way.

## Participants

- Before recruiting starts, the record's frozen part fixes the number of participants, the reason for that number, and how participants are chosen to cover face shape, skin tone, age, glasses and facial hair.
- Results are held out by participant, not by frame: participants used to fit a curve are never used to test it.

## Consent, law and retention

This is a list of what review must cover, not legal advice.

- **Consent:** informed, written, specific to this study, with a plain description of what is kept. A participant can withdraw and have their data deleted until the code-to-person key is destroyed at the end of their session. After that, their data can no longer be told apart from anyone else's, and it cannot be removed. The consent text says this.
- **DPIA:** a data protection impact assessment before any capture.
- **GDPR Article 9:** face geometry processed this way may be special-category (biometric) data. The legal basis and safeguards must be settled first.
- **BIPA (Illinois) and similar laws:** a written retention and destruction policy, written consent before collection, and no sale or sharing of biometric data.
- **Retention:** weights only. Video and images are processed during the session and deleted at capture. They are never written to long-term storage. Only the per-frame tracker outputs (ARKit coefficients, MediaPipe scores, FB2 weights, pupil values) are kept, with timestamps, under a random participant code. The code-to-person key is destroyed after the session. Published records contain only fitted curves and aggregate metrics, never data for one participant.

## From results to records

Results would become calibration records in the K1 format ([calibration/README.md](../../calibration/README.md)) with status `calibrated_measured`, which `check.py` refuses today. To allow it, the format and `check.py` need a reviewed change. The plan:

- **Freeze first.** Before capture, the record's frozen part gets the method, channels, devices and software versions, prompts, participant numbers, the split into fit and held-out participants, the bounds and the minimum conditions per cell. Its hash goes into `calibration/FREEZES`.
- **Devices instead of a renderer.** A `capture` table would replace `renderer`. It would list device models, OS and app or runtime versions, the eye-tracking instrument and its calibration, and the measured sync error.
- **Cells per participant group, not per person.** Each cell reports median, p95, neutral error and failures (missed detections) over at least 20 conditions, for the held-out participants only, without pooling across cells.
- **Scope and limitations.** `scope` would name the devices and versions tested. The limitations would state who the sample does not represent, and, for R-CAP2's upper face, that the comparison is across sessions.
- A channel that misses its bounds is published as a negative result, with no mapping.
