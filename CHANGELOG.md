# Changelog

Original documentation: CC-BY-SA-4.0.

## Data 0.5.0 — unreleased

The draft canonical expression set joins the data, with maps into it and out
of it. A translation can now run from a source set through the canonical
expression set to a target set. The 7 direct maps do not change.

- New profile `rcef.canonical_expression` in
  `data/canonical_expression.toml`: 60 signals, vocabulary version `1.0`,
  status `draft`, as `docs/canonical-set.md` defines them. The groups are
  `face` (41), `cheek_puff` (2), `jaw_thrust` (1), `jaw_sideways` (2),
  `mouth_shift` (2), `chin_raise_upper_lip` (1), `blink` (2), `gaze` (8) and
  `tongue_out` (1). Each signal's metadata gives its definition, its 0 and 1,
  its FACS code where it has one, its group, the provider names aligned to
  it and its rows in the definitions audit.
- 306 new mappings in 46 maps, one map per group and direction: ARKit and FB2
  into the canonical expression set (120 mappings in 18 maps), and the
  canonical expression set to ARKit, FB2, VRCFaceTracking Unified
  Expressions and VRM per-eye blinks (186 mappings in 28 maps). The FB2 gaze
  out-map has 4 internal steps, which write 4 new `rcef.intermediate`
  signals (8 in all).
- Each new mapping states, as assumptions: the correspondence; the
  endpoints, with a clause that matches its operator; whether the evidence
  of today's direct maps carries over to the canonical signal or is
  withdrawn, with the loss that withdraws it (a transfer is withdrawn when
  the hop's own audit row or the other set's row for the canonical signal is
  `differs` or `unresolved`); and every other assumption of
  today's direct maps, as the assumption catalogue in
  `docs/canonical-set-audit.md` places it.
- Evidence status: every canonical expression signal and every new mapping
  is `proposed` and `approximate`. The identity maps into `rcef.canonical`
  stay `verified_current`. The canonical pupils, which would be
  `verified_current`, are not in this version.
- Losses added by the definitions audit, on the hops that the audit names:
  the ARKit `mouthClose` jaw relation (`arkit_mouthclose_jaw_unresolved`),
  the ARKit definitions that differ from the canonical ones, the VRM blink
  side (`vrm_blink_side_unresolved`, until now an assumption only), the
  Unified Expressions definitions that differ, and the ICT-FaceKit FACS
  crosswalk codes that differ from the canonical codes
  (`ict_au33_cheek_blow`, `ict_au45_blink`). No loss of today's maps is
  corrected.
- On the pairs that the direct maps also translate (FB2 → ARKit,
  ARKit → FB2, ARKit → Unified Expressions, FB2 → VRM blinks), the route
  through the canonical expression set gives the same weights as the direct
  maps. FB2 → Unified Expressions is new: it runs through the canonical
  expression set.
- New evidence records: `rcef_canonical_v1` (the original canonical
  expression vocabulary), `facs_wikipedia` (FACS code numbers, Wikipedia
  revision 1357638399), `rcsf_proposal` (the RCSF proposal at `f6c3ea8`),
  and six figure records for the FB2 and Unified Expressions figures that
  the definitions cite.
- `scripts/build_canonical.py` writes the profile and the 46 maps from
  `docs/canonical-set.md`, its audit and the direct maps. New tests:
  `tests/test_canonical_vocabulary.py` and `tests/test_pivot_structure.py`.
  The capability matrix in the second reads the names of FACS,
  `XR_FB_face_tracking`, `XR_ANDROID_face_tracking` and
  `XR_ML_facial_expression` from `tests/fixtures/capability_sets.json`,
  which `scripts/derive_capability_sets.py` writes from cached source bytes.
- The viseme part of the canonical set is not in this version.

## Data 0.4.0 — not released (A/B baseline at `dea1713`, pack SHA-256 `630d37a5…`)

Adopt msf-tools (now msf-character-tools) operators 1.1
(`operator_version = "1.1"`). FB2 requires opposing gaze directions to be
exclusive, and the data now builds this in.

- `arkit_gaze.to_fb2` now has 12 mappings. For each eye, a weighted sum
  takes ARKit in minus out (and up minus down). Two one-sided
  `piecewise_linear` splits then turn each difference into the two opposing
  FB2 directions. FB2 allows only one direction of a pair to be non-zero. A
  split is exactly zero on its flat side, so both directions of a pair are
  never non-zero together. When ARKit sets both directions, only their
  difference is kept, and this is declared as a loss. The example translator
  no longer refuses such frames.
- New `rcef.intermediate` profile (4 signals) for those differences, in
  `data/intermediate.toml`.
- The msf-tools lock moves to 0.4.0 (commit `05ca053` in the rewritten history), which provides
  operators 1.1. It has one entry for each of the six release wheels:
  CPython 3.11 and 3.12 or later, on macOS arm64, Linux x86_64 and Linux
  aarch64. Each entry has the wheel's SHA-256 and the hash of every file
  it installs. Install the release wheel for your platform by hash;
  `check.py` refuses any other build. Earlier in this cycle the lock moved
  to 0.3.0 (commit `710bb49`).
- VRCFaceTracking's signed eye gaze is not split into FB2 directions. Its
  units and range are unresolved in RCEF's inventory, and `piecewise_linear`
  needs a declared range.
- msf-tools has a new name, msf-character-tools. The lock moves to
  msf-character-tools 0.5.0, which behaves the same as msf-tools 0.4.0.
  The import package is `msf_character_tools`. `check.py`, the tests, the
  examples and the calibration tools use the new names.
- RCEF is now at https://github.com/MetaverseStandards/RCEF, and
  msf-character-tools is at
  https://github.com/MetaverseStandards/msf_character_tools. Both are
  public.
- The GitHub workflow downloads the public release wheel with `curl`. It
  needs no token. It still installs the wheel by hash.
- The licence and notice files name the Metaverse Standards Forum as the
  copyright holder. The licences do not change. Attribution and the
  `authorship` fields still name RCEF contributors (2026), so the generated
  files do not change.
- `evidence/tooling.lock.previous.json` is removed. The earlier locks name
  commits that are not in the public history, and file hashes that a public
  install cannot match. The next lock update writes the file again.
- The Git history was rewritten before publication, so older commit hashes
  are different.
- Both calibration records are frozen again, as version 2. Version 1 names
  commits that are not in the rewritten history. Version 2 was fitted again
  with the code at `code_commit` `7cd8ff9`, msf-character-tools 0.5.0
  and a renderer built from `tools/render/meshrender.swift` at that commit
  (source SHA-256 `913c1641…`). Each record has a new line in
  `calibration/FREEZES` with the reason. The method, inputs, bounds,
  counts, limitations and all knots are the same as in v1. The held-out
  runs used the new seeds that the v2 frozen hashes set.
- The v2 results have the same pass and fail pattern as v1. In
  `mediapipe.ict-response`, 0 of 25 fitted channels pass, so no mapping
  cites the record. In `rig-gains.ict-rocketbox-female`, 3 of 51 shapes
  pass (browInnerUp, cheekSquintLeft, cheekSquintRight) and 48 fail. The
  cell numbers are different. The held-out seeds are different.
  `examples/data/rig_gains.json` has the new frozen hash; its curves do not
  change. `calibration/README.md` and `tools/calibration/README.md` tell
  how to reproduce v2.
- The pack and the generated files do not change, so the data version
  stays 0.4.0.

## Calibration and examples — unreleased

- Calibration record `calibration/rig-gains.ict-rocketbox-female.cal`
  (software-only; not a measurement of any tracker): one monotone curve per
  ARKit shape from an ICT-FaceKit weight to the Rocketbox Female weight whose
  rendered landmark motion matches, fitted on 8 ICT identities and evaluated
  on a held-out one. 3 of 51 shapes pass (browInnerUp, cheekSquintLeft,
  cheekSquintRight). 48 fail and are published as negative results. In these,
  Rocketbox moves differently (mouthPucker, mouthFunnel, cheekPuff, noseSneer,
  the squints and gaze, among others), or it cannot reach ICT's motion
  (jawOpen, the smiles, mouthLeft and mouthRight). mouthClose, evaluated
  alone, hides its own markers. The record was frozen in `calibration/FREEZES`
  before the held-out run. Example data only, not pack data: `examples/rig_gains.py`,
  `examples/data/rig_landmarks.json`, `examples/data/rig_gains.json` and
  `rigs.py --normalise`. Rocketbox Male was never loaded.
- The examples and the calibration tools read the Rocketbox FBX rigs with
  msf-tools 0.4.0 itself, so they no longer need `msf-tools-ufbx` or a C
  compiler.

## Data 0.3.0 — 2026-10-26

Complete FB2 -> ARKit, read it back, and add ARKit -> Unified Expressions
and FB2 -> VRM blinks: 168 new mappings, 187 in all. As in 0.2.0, all new
mappings are proposed and approximate. They compile only with the
approximation opt-in. Each one states its calibration assumption and losses
and cites at least two public sources.

- `fb2.to_arkit` gains 34 mappings and `fb2_gaze.to_arkit` gains vertical
  gaze (4 mappings), so all 52 ARKit coefficients are written. 4 are
  averages: mouthFunnel (the four lip quarters), mouthPucker, mouthRollUpper
  and mouthRollLower. mouthLeft and mouthRight are flagged. Only Godot names
  the ARKit coefficient for the FB2 channel, though VRCFaceTracking pairs the
  FB2 channel with its Unified shape and the definitions agree.

- `arkit.to_fb2` (52 mappings) and `arkit_gaze.to_fb2` (8 mappings) read the
  FB2 -> ARKit routes back. Where FB2 splits a coefficient into parts
  (browInnerUp, cheekPuff, mouthPucker, mouthRollUpper, mouthRollLower,
  mouthFunnel), the value is copied to each part, so FB2 -> ARKit returns it
  exactly. Those mappings declare that the symmetry is invented. The gaze
  mappings declare that FB2 requires opposing directions to be exclusive and
  that no operator can enforce this. The example translator refuses such
  frames.

- `arkit.to_vrcft_artist` (68 mappings) writes VRCFaceTracking's Unified
  Expressions base shapes. Where Unified Expressions builds an ARKit
  coefficient from several shapes, the value is copied into each one, so
  VRCFaceTracking's own composite gives it back. The composite is a mean for
  most shapes, and its published 0.75/0.25 and 0.8/0.2 splits for browDown
  and mouthSmile (new evidence record `vrcft_simple_expressions`). mouthLeft
  and mouthRight are flagged as above.

- `fb2.to_vrm` (2 mappings): EYES_CLOSED_L and _R to VRM blinkLeft and
  blinkRight. `blink` is left unset, so a model that binds all three is not
  driven twice. VRM does not say whose left blinkLeft is. A slow test reads
  the side from the VRM sample's geometry.

The signals that these mappings use for the first time become `mapped`.
The demo frames move each channel that an FB2 mapping reads on its own. The
VRM viseme example ends with the expression library's two winks. The slow
tier halves each mapping on its own, to cross-check the fast test that
halves them all at once.

Still unresolved, with reasons in the README: VRM look presets, VRM emotions,
MediaPipe -> ARKit, Unified Expressions -> ARKit and FB2 -> Unified
Expressions.

## Data 0.2.0 — 2026-10-26

Add the first cross-provider translations. All 19 mappings are proposed
and approximate. They compile only with the approximation opt-in. Each one
states its calibration assumption and losses and cites at least two public
sources.

- `fb2.to_arkit` (10 mappings): blink left/right, jaw open, mouth close, brow
  inner up (mean of left and right), cheek puff (mean of left and right),
  smile left/right, shrug upper/lower.
- `fb2_gaze.to_arkit` (4 mappings): horizontal gaze in/out for each eye.
  This is a separate map because FB2 can report the face as valid while eye
  following is not valid.
- `visemes.to_vrm` (5 mappings): META visemes AA, IH, OU, E, OH to VRM aa, ih,
  ou, ee, oh. This is a phoneme-label correspondence; no published table maps
  META visemes to VRM.

The 32 signals that these mappings use for the first time become `mapped`. ARKit
cheekPuff gains `bilateral_shared` coupling. New evidence records cover the
Godot OpenXR vendors plugin, Godot's face-modifier name table, the VRCFT
compatibility tables and parameter code, and ICT-FaceKit. The Apple
documentation pins are refreshed after Apple re-rendered those pages.

Left for later: vertical gaze (FB2 EYES_LOOK_UP/DOWN to ARKit
eyeLookUp/Down), which has equally good sources, and splits from signed to
one-sided values and curves, which need new msf-tools operators.

## Data 0.1.1 — 2026-10-07

Correct eleven records using the pinned primary definitions:

- Set the Godot base, VRCFT artist base, VRCFT numeric parameter and VRCFT
  transport MouthClosed regions to `mouth`.
- Set all six VRCFT numeric Eye X/Y parameter regions to `gaze`; set the four
  unilateral parameters to their anatomical `left` or `right` side. Combined
  EyeX/EyeY keep `shared` side and composite coupling.
- Set Apple ancillary leftEyeTransform to `gaze` region and `left` side. It
  stays excluded, with its native `matrix4x4` metadata and scalar inventory
  placeholder. Scalar wire 1.0 does not execute this transform.

Schema and operator versions stay at 1.0. IDs, names, order, scalar values,
provider bases, dispositions, mappings and evidence records do not change.
The pack digest, coverage's pack digest and output checksums change. The
survey CSV bytes stay identical. This revision shows only that metadata and
scalars are kept. Device calibration and consumer hardening have their own gates.

Outputs were rendered with the pinned msf-tools 0.1.0 baseline commit
`acf869d3d7b05d8e9653284bc9a0197412519c75`. The dependency lock stays at that
baseline. It will be updated after the shared hardening commit and its
integration into RCEF are independently accepted.

Data 0.1.0 is kept at RCEF commit
`282fc3857b2bc464a3fb77bb3d6a64744a17d1c9` for rollback, with its known
metadata defects. To revert, use that complete set of files with its checksums.
