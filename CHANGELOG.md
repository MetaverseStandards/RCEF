# Changelog

Original documentation: CC-BY-SA-4.0.

## Data 0.4.0 — unreleased

Adopt msf-tools operators 1.1 (`operator_version = "1.1"`) and build FB2's
gaze exclusivity into the data.

- `arkit_gaze.to_fb2` now has 12 rules. For each eye, a weighted sum takes
  ARKit in minus out (and up minus down), and two one-sided
  `piecewise_linear` splits turn each difference into the two opposing FB2
  directions. FB2 allows only one of a pair to be non-zero, and a split is
  exactly zero on its flat side, so the pair can never both be non-zero.
  When ARKit sets both directions, only their difference is kept; this is
  declared as a loss. The example translator no longer refuses such frames.
- New `rcef.intermediate` profile (4 signals) for those differences, in
  `data/intermediate.toml`.
- The msf-tools lock moves to 0.3.0 (commit `e799dfb`), which provides
  operators 1.1. It records the hash of the `py3-none-any` wheel built
  from that commit; the 0.2.0.dev0 lock is kept as
  `evidence/tooling.lock.previous.json`.
- VRCFaceTracking's signed eye gaze is not split into FB2 directions: its
  units and range are unresolved in RCEF's inventory, and `piecewise_linear`
  needs a declared range.

## Calibration and examples — unreleased

- Calibration record `calibration/rig-gains.ict-rocketbox-female.cal`
  (software-only; not a measurement of any tracker): one monotone curve per
  ARKit shape from an ICT-FaceKit weight to the Rocketbox Female weight whose
  rendered landmark motion matches, fitted on 8 ICT identities and evaluated
  on a held-out one. 3 of 51 shapes pass (browInnerUp, cheekSquintLeft,
  cheekSquintRight). 48 fail and are published as negative results: Rocketbox
  moves differently (mouthPucker, mouthFunnel, cheekPuff, noseSneer, the
  squints and gaze, among others), cannot reach ICT's motion (jawOpen, the
  smiles, mouthLeft and mouthRight), or mouthClose, evaluated alone, hides
  its own markers. The record was frozen in `calibration/FREEZES` before the
  held-out run. Example data only, not pack data: `examples/rig_gains.py`,
  `examples/data/rig_landmarks.json`, `examples/data/rig_gains.json` and
  `rigs.py --normalise`. Rocketbox Male was never loaded.

## Data 0.3.0 — 2026-10-26

Complete FB2 -> ARKit, read it back, and add ARKit -> Unified Expressions
and FB2 -> VRM blinks: 168 new rules, 187 in all. All new rules are proposed
and approximate, as in 0.2.0: they compile only with the approximation
opt-in, and each one states its calibration assumption and losses and cites
at least two public sources.

- `fb2.to_arkit` gains 34 rules and `fb2_gaze.to_arkit` gains vertical gaze
  (4 rules), so all 52 ARKit coefficients are written. 4 are averages:
  mouthFunnel (the four lip quarters), mouthPucker, mouthRollUpper and
  mouthRollLower. mouthLeft and mouthRight are flagged: only Godot names the
  ARKit coefficient for the FB2 channel, though VRCFaceTracking pairs the FB2
  channel with its Unified shape and the definitions agree.

- `arkit.to_fb2` (52 rules) and `arkit_gaze.to_fb2` (8 rules) read the FB2 ->
  ARKit routes back. A coefficient FB2 splits into parts (browInnerUp,
  cheekPuff, mouthPucker, mouthRollUpper, mouthRollLower, mouthFunnel) is
  copied to each part, so FB2 -> ARKit returns it exactly; those rules declare
  that the symmetry is invented. The gaze rules declare that FB2 requires
  opposing directions to be exclusive and that no operator can enforce it;
  the example translator refuses such frames.

- `arkit.to_vrcft_artist` (68 rules) writes VRCFaceTracking's Unified
  Expressions base shapes. Where Unified Expressions builds an ARKit
  coefficient from several shapes, the value is copied into each, so
  VRCFaceTracking's own composite gives it back: a mean for most, and its
  published 0.75/0.25 and 0.8/0.2 splits for browDown and mouthSmile (new
  evidence record `vrcft_simple_expressions`). mouthLeft and mouthRight are
  flagged as above.

- `fb2.to_vrm` (2 rules): EYES_CLOSED_L and _R to VRM blinkLeft and
  blinkRight. `blink` is left unset so a model binding all three is not
  driven twice. VRM does not say whose left blinkLeft is; a slow test reads
  the side from the VRM sample's geometry.

The signals these rules use for the first time become `mapped`. The demo
frames move every channel an FB2 rule reads on its own, and the VRM viseme
example ends with the expression library's two winks. The slow tier halves
each rule on its own as a cross-check on the fast all-at-once test.

Still unresolved, with reasons in the README: VRM look presets, VRM emotions,
MediaPipe -> ARKit, Unified Expressions -> ARKit and FB2 -> Unified
Expressions.

## Data 0.2.0 — 2026-10-26

Add the first cross-provider translations. All 19 rules are proposed and
approximate: they compile only with the approximation opt-in, and each one
states its calibration assumption and losses and cites at least two public
sources.

- `fb2.to_arkit` (10 rules): blink left/right, jaw open, mouth close, brow
  inner up (mean of left and right), cheek puff (mean of left and right),
  smile left/right, shrug upper/lower.
- `fb2_gaze.to_arkit` (4 rules): horizontal gaze in/out for each eye. This
  is a separate mapping because FB2 can report the face valid while eye
  following is not.
- `visemes.to_vrm` (5 rules): META visemes AA, IH, OU, E, OH to VRM aa, ih,
  ou, ee, oh. This is a phoneme-label correspondence; no published table maps
  META visemes to VRM.

The 32 signals these rules use for the first time become `mapped`. ARKit
cheekPuff gains `bilateral_shared` coupling. New evidence records cover the
Godot OpenXR vendors plugin, Godot's face-modifier name table, the VRCFT
compatibility tables and parameter code, and ICT-FaceKit. The Apple
documentation pins are refreshed after Apple re-rendered those pages.

Deferred: vertical gaze (FB2 EYES_LOOK_UP/DOWN to ARKit eyeLookUp/Down),
which is equally well sourced, and signed-to-one-sided splits and curves,
which need new msf-tools operators.

## Data 0.1.1 — 2026-10-07

Correct eleven records using the pinned primary definitions:

- Set the Godot base, VRCFT artist base, VRCFT numeric parameter and VRCFT
  transport MouthClosed regions to `mouth`.
- Set all six VRCFT numeric Eye X/Y parameter regions to `gaze`; set the four
  unilateral parameters to their anatomical `left` or `right` side. Combined
  EyeX/EyeY keep `shared` side and composite coupling.
- Set Apple ancillary leftEyeTransform to `gaze` region and `left` side. It
  remains excluded, with its native `matrix4x4` metadata and scalar inventory
  placeholder; scalar wire 1.0 does not execute this transform.

Schema and operator versions remain 1.0. IDs, names, order, scalar values,
provider bases, dispositions, rules and evidence records are preserved. The
pack digest, coverage's pack digest and output checksums change; survey CSV
bytes remain identical. This revision establishes metadata and scalar
preservation only; device calibration and consumer hardening have separate gates.

Outputs were rendered with the pinned msf-tools 0.1.0 baseline commit
`acf869d3d7b05d8e9653284bc9a0197412519c75`. The dependency lock remains at that
baseline; it will be updated after independent acceptance of the shared
hardening commit and RCEF dependency integration.

Data 0.1.0 is retained at RCEF commit
`282fc3857b2bc464a3fb77bb3d6a64744a17d1c9` for rollback, including its known
metadata defects. Select that complete artifact with its checksums when reverting.
