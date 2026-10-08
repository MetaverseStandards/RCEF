# Changelog

Original documentation: CC-BY-SA-4.0.

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
