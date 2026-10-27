# Changelog

Original documentation: CC-BY-SA-4.0.

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
