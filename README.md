# Reference Canonical Expression Framework (RCEF)

## Purpose

The Reference Canonical Expression Framework (RCEF) is about face expression signals. Face trackers and avatar systems each publish their own set of these signals. ARKit, OpenXR FB2, MediaPipe, VRCFaceTracking, VRM, Godot and Roblox use different names, scales and calibrations. So you cannot simply copy a value from one system into another.

RCEF does four things:

- It records each public expression interface as data, with its calibration limits and a pinned public source.
- It defines a draft canonical expression set of 72 signals and a draft canonical viseme set of 16 signals, each with a meaning that RCEF declares.
- It defines explicit one-way scalar mappings into and out of the canonical sets. Each mapping states its assumptions and its losses. A translation runs from a source set through a canonical set to a target set.
- It checks all of this with [msf-character-tools](https://github.com/MetaverseStandards/msf_character_tools), which is maintained separately.

RCEF records provider names as facts, with attribution. Its definitions and examples are original.

RCEF is not these things:

- It is not a new universal blendshape set. "Canonical" does not mean one universal anatomy or one shared calibration.
- It is not a claim of visual equivalence. Its cross-provider mappings are proposed approximations.
- It does not describe how a stylized character looks. RCEF describes what a signal means. Stylization is a separate layer on top of RCEF.

[RCSF](https://github.com/MetaverseStandards/RCSF), the Reference Canonical Skeletal Framework, does a similar job for skeletons. It is also in the Metaverse Standards Forum organization on GitHub. Its README is a pinned source for RCEF ([rcsf_readme](references.md#rcsf_readme)).

## Contents

RCEF is mostly data in plain-text TOML files (`key = value` lines). Scripts build everything else from that data.

### The data (edit these)

- `profiles/`: one file per public expression set, for example ARKit, OpenXR FB2 or VRM. Each file lists the set's signals: name, value range (often 0 to 1), face side, neutral value and public source.
- `data/`: RCEF's own sets. `canonical_expression.toml` is the draft canonical expression set of 72 signals, and `canonical_viseme.toml` the draft canonical viseme set of 16 signals. `intermediate.toml` holds 61 helper values: 4 that the map from the canonical expression set to FB2 gaze uses inside, 1 that the META map to `alveolar_floor` uses inside, and 56 that the viseme pose bridge uses inside (`scripts/build_canonical.py` writes those).
- `mappings/`: the maps. A map turns the signals of one set into those of another, for example FB2 into ARKit. Each mapping names its inputs, outputs and formula (a copy, a scale and offset, a weighted sum or a curve), and states its assumptions and losses. The `canonical_*.toml` files hold the maps into and out of the canonical expression set.
- `evidence/`: `sources.toml` lists each public source with its exact revision and SHA-256. `tooling.lock.json` pins the msf-character-tools build that checks the data. `input-contracts/` holds an optional schema that RCEF does not use.
- `calibration/`: curves fitted to software renders of example faces. The `FREEZES` ledger only grows. It shows that each fit was fixed before it was tested.
- `pack.toml`: the version numbers, ID and licence of the whole data set.

### Generated files (do not edit)

- `generated/`: all the data merged into one JSON file (`rcef.pack.json`), plus a CSV table, a coverage summary and checksums.
- `reports/`: the same data as readable Markdown and CSV tables: every signal, every mapping, and how each set lines up with the canonical set.
- `references.md`, `docs/toml-index.csv` and `docs/godot_comparison.md`: the source list, an index of the TOML files, and a comparison with Godot.

`check.py --write` writes `generated/` and `reports/`. [Editing the data](#editing-the-data) names the scripts for the other files.

### Code and tests

- `check.py`: the main check. It verifies the locked msf-character-tools, the calibration records and the generated files in `generated/` and `reports/`. `--write` rebuilds those files.
- `scripts/`: helper programs. They write the canonical expression set and its maps, the source list and the TOML index, compare RCEF with Godot, check the public sources and the audit's source locators, and run the local CI.
- `tests/`: the automated tests, with their inputs in `tests/fixtures/`. `scripts/derive_fb2_goldens.py` makes three of those inputs from cached public sources, `scripts/derive_capability_sets.py` makes the name lists in `capability_sets.json`, and `scripts/derive_rocketbox_au_names.py` reads the 48 Rocketbox FACS shape names from the pinned rig files into `rocketbox_au_names.json`.
- `fixtures/`: small made-up inputs with known answers. They show how the formulas behave.
- `tools/`: optional tools that make the calibration records, and the small macOS renderer they use.

### Examples

- `examples/`: programs you can run. Through the canonical sets, they translate synthetic FB2 face frames to ARKit, turn speech visemes into VRM mouth shapes, and drive 3D example faces. Their inputs are in `examples/data/`.

### Documents

- `docs/`: the [architecture guide](docs/architecture.md) (also as a diagram and a web page), the [full table of expression sets](docs/expression-sets.md), calibration notes, and the draft [canonical expression set](docs/canonical-set.md) with its [definitions audit](docs/canonical-set-audit.md) and [FACS intensity codec](docs/facs-intensity.md).
- `survey.md`: what RCEF selected from each system, and the limits of each.
- `proposal.md`: the data format, the API and the release limits.
- `CHANGELOG.md`, `CONTRIBUTING.md` and `GOVERNANCE.md`: the changes in each data version, what a change must include, and who owns releases.
- `REVIEW.md`: a self-review dated 2026-10-07.
- `AGENTS.md`: instructions for AI coding assistants. `CLAUDE.md` points to it.
- `LICENSE`, `LICENSES/` and `THIRD_PARTY_NOTICES.md`: the licences and the credits for public sources.
- `.github/workflows/check.yml`: a GitHub workflow.

## What RCEF covers

RCEF records these selected inventories. The numbers describe interfaces. They do not say how well anything tracks a face.

- ARKit: 52 coefficients.
- MediaPipe: 52 labels.
- OpenXR: FB 63, FB2 70, and the optional META visemes 15.
- VRCFaceTracking: transport 88; raw and combined eye data; artist shapes 102 base and 42 blended; 124 publicly listed numeric avatar parameters; 3 activity flags.
- Godot: 102 base and 41 blended.
- VRM: 18 presets.
- Roblox: 50 face controls.
- FACS: 92 code numbers from a public list, 49 of them mapped, in RCEF's own numeric encoding (not a FACS interface).

RCEF also records ancillary enums, sentinels and encoding surfaces.

Two original fixtures, one affine and one lossy bilateral, show the shared runtime. They do not claim visual equivalence.

Data 0.5.0 retires the direct maps of earlier data versions: the 187 direct cross-provider mappings (FB2 to and from ARKit, ARKit to VRCFaceTracking Unified Expressions, FB2 to VRM blinks and META visemes to VRM), their 4 internal gaze steps, and the 21 identity mappings into the old 21-signal canonical set `rcef.canonical`, which is retired too. Every translation now runs through the canonical sets. [docs/retired-ids.csv](docs/retired-ids.csv) lists every retired ID. The A/B comparison keeps the direct maps in its frozen baseline, `tests/fixtures/baseline-dea1713.pack.json` ([ab/README.md](ab/README.md)).

The canonical expression set, `rcef.canonical_expression`, is a draft: 72 signals in 13 groups (face 41, cheek puff 2, jaw thrust 1, jaw sideways 2, mouth shift 2, chin raise upper lip 1, blink 2, gaze 8, tongue out 1, cheek suck 2, lip tighten 2, tongue place 6, pupil diameter 2). [docs/canonical-set.md](docs/canonical-set.md) defines each signal, and the [definitions audit](docs/canonical-set-audit.md) compares it with each source. 442 mappings in 75 maps go into and out of it:

- ARKit, FB2, FACS codes, VRCFaceTracking eye data and VRM per-eye blinks into the canonical expression set (189 mappings in 32 maps);
- the canonical expression set to ARKit, FB2, VRCFaceTracking Unified Expressions, VRCFaceTracking eye data, VRM per-eye blinks and FACS codes (253 mappings in 43 maps, with 4 internal steps in the FB2 gaze map).

So a translation can run from ARKit, FB2, FACS codes, VRCFaceTracking eye data or VRM blinks through the canonical expression set to ARKit, FB2, Unified Expressions, VRCFaceTracking eye data, VRM blinks or FACS codes. Each group has one map in each direction.

VRCFaceTracking eye data fills two groups. In `blink`, `eye_close` is 1 − `Openness`; an `Openness` outside 0 to 1 is refused, and VRCFaceTracking does not say that 1 is a relaxed open eye. In `pupil_mm`, the pupil diameters in millimetres are copied exactly; these 4 mappings and the 2 canonical pupil signals are `verified_current`. VRM fills `blink` from `blinkLeft` and `blinkRight`. VRM `blink`, which closes both eyes, is not read, and a route lists a non-zero `blink` as dropped.

The FACS codes are an expression set of their own, `facs.code` (draft): 92 rows, one per code number from a public list (record `facs_wikipedia`), split by side where the canonical signal is. 49 are mapped, 25 `unresolved` and 18 `excluded`. Their values are RCEF's own numeric encoding of the FACS intensity letters, not FACS scores, and RCEF does not code faces. [docs/facs-intensity.md](docs/facs-intensity.md) gives the letter codec, and `examples/facs_codec.py` implements it. FACS fills 8 of the 13 groups; it has no code for mouth shift, the upper-lip part of chin raise, gaze, the tongue places or the pupils.

The draft canonical viseme set, `rcef.canonical_viseme`, has 16 signals. 15 are partition classes (vowel 5, consonant 9, rest 1): 14 mouth-shape classes that hold every symbol of the IPA chart, and the rest class `sil`. From a valid META frame their values sum to 1. The 16th, `alveolar_floor`, is the sum of the three alveolar classes and `rhotic`, clamped at 1: the class that joins them in the IPA strict floor. 42 mappings in 9 maps go into and out of it:

- META visemes and the VRM vowel presets into the canonical viseme set (22 mappings in 5 maps, with 1 internal step in the map that writes `alveolar_floor`);
- the canonical viseme set to META visemes and the VRM vowel presets (20 mappings in 4 maps).

On the pairs that the retired direct maps translated, the composed route gives the same weights as they did (`tests/test_pivot_structure.py` compares it with the frozen baseline). Of the 484 mappings in the 84 maps of the two canonical sets, all but the 4 pupil copies are proposed and approximate; the pupil copies are exact and `verified_current`. `scripts/build_canonical.py` writes both canonical profiles, the `facs.code` profile and these maps from the two documents.

The viseme pose bridge, `rcef_viseme_pose.to_rcef_expression`, joins the two canonical sets: 101 proposed mappings in 1 map, with 56 helper values in `rcef.intermediate`. It writes canonical expression values from the 11 viseme classes that pass the shape or the perceptual gate on all 4 held-out rigs in the calibration record `viseme-poses.rocketbox-features`. `scripts/build_canonical.py` writes it from the record.

### Mappings

Each row is one map: a group of mappings that turns values in the source set into values in the target set. `verified_current` means that the mapping restates a verified source fact (it copies a provider value exactly). `proposed` means an approximate cross-provider translation that is backed by sources and compiles only with the approximation opt-in. [reports/mappings.md](reports/mappings.md) lists every mapping with its assumptions, losses and evidence. That report also lists the maps that these tables leave out: RCEF's synthetic test maps (`fixture.affine`, `fixture.bilateral`) and `survey.ambiguous`, which is recorded but cannot be executed.

#### Maps into the canonical expression set

Each map reads one source set and writes one whole group of the canonical expression set.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`arkit_face.to_rcef`](reports/mappings.md#arkit_faceto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 41 | proposed |
| [`arkit_cheek_puff.to_rcef`](reports/mappings.md#arkit_cheek_puffto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 2 | proposed |
| [`arkit_jaw_thrust.to_rcef`](reports/mappings.md#arkit_jaw_thrustto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 1 | proposed |
| [`arkit_jaw_sideways.to_rcef`](reports/mappings.md#arkit_jaw_sidewaysto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 2 | proposed |
| [`arkit_mouth_shift.to_rcef`](reports/mappings.md#arkit_mouth_shiftto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 2 | proposed |
| [`arkit_chin_raise_upper_lip.to_rcef`](reports/mappings.md#arkit_chin_raise_upper_lipto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 1 | proposed |
| [`arkit_blink.to_rcef`](reports/mappings.md#arkit_blinkto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 2 | proposed |
| [`arkit_gaze.to_rcef`](reports/mappings.md#arkit_gazeto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 8 | proposed |
| [`arkit_tongue_out.to_rcef`](reports/mappings.md#arkit_tongue_outto_rcef) | `arkit.coefficient` → `rcef.canonical_expression` | 1 | proposed |
| [`fb2_face.to_rcef`](reports/mappings.md#fb2_faceto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 41 | proposed |
| [`fb2_cheek_puff.to_rcef`](reports/mappings.md#fb2_cheek_puffto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_jaw_thrust.to_rcef`](reports/mappings.md#fb2_jaw_thrustto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 1 | proposed |
| [`fb2_jaw_sideways.to_rcef`](reports/mappings.md#fb2_jaw_sidewaysto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_mouth_shift.to_rcef`](reports/mappings.md#fb2_mouth_shiftto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_chin_raise_upper_lip.to_rcef`](reports/mappings.md#fb2_chin_raise_upper_lipto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 1 | proposed |
| [`fb2_blink.to_rcef`](reports/mappings.md#fb2_blinkto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_gaze.to_rcef`](reports/mappings.md#fb2_gazeto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 8 | proposed |
| [`fb2_tongue_out.to_rcef`](reports/mappings.md#fb2_tongue_outto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 1 | proposed |
| [`fb2_cheek_suck.to_rcef`](reports/mappings.md#fb2_cheek_suckto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_lip_tighten.to_rcef`](reports/mappings.md#fb2_lip_tightento_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 2 | proposed |
| [`fb2_tongue_place.to_rcef`](reports/mappings.md#fb2_tongue_placeto_rcef) | `openxr.fb2` → `rcef.canonical_expression` | 6 | proposed |
| [`vrcft_eye_blink.to_rcef`](reports/mappings.md#vrcft_eye_blinkto_rcef) | `vrcft.eye` → `rcef.canonical_expression` | 2 | proposed |
| [`vrcft_eye_pupil_mm.to_rcef`](reports/mappings.md#vrcft_eye_pupil_mmto_rcef) | `vrcft.eye` → `rcef.canonical_expression` | 2 | verified_current |
| [`vrm_blink.to_rcef`](reports/mappings.md#vrm_blinkto_rcef) | `vrm.preset` → `rcef.canonical_expression` | 2 | proposed |
| [`facs_face.to_rcef`](reports/mappings.md#facs_faceto_rcef) | `facs.code` → `rcef.canonical_expression` | 41 | proposed |
| [`facs_cheek_puff.to_rcef`](reports/mappings.md#facs_cheek_puffto_rcef) | `facs.code` → `rcef.canonical_expression` | 2 | proposed |
| [`facs_jaw_thrust.to_rcef`](reports/mappings.md#facs_jaw_thrustto_rcef) | `facs.code` → `rcef.canonical_expression` | 1 | proposed |
| [`facs_jaw_sideways.to_rcef`](reports/mappings.md#facs_jaw_sidewaysto_rcef) | `facs.code` → `rcef.canonical_expression` | 2 | proposed |
| [`facs_blink.to_rcef`](reports/mappings.md#facs_blinkto_rcef) | `facs.code` → `rcef.canonical_expression` | 2 | proposed |
| [`facs_tongue_out.to_rcef`](reports/mappings.md#facs_tongue_outto_rcef) | `facs.code` → `rcef.canonical_expression` | 1 | proposed |
| [`facs_cheek_suck.to_rcef`](reports/mappings.md#facs_cheek_suckto_rcef) | `facs.code` → `rcef.canonical_expression` | 2 | proposed |
| [`facs_lip_tighten.to_rcef`](reports/mappings.md#facs_lip_tightento_rcef) | `facs.code` → `rcef.canonical_expression` | 2 | proposed |

#### Maps out of the canonical expression set

Each map reads one group and writes the target set's signals for it. An out-map gives values only when the in-map of its group gave values for the whole group.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`rcef_face.to_arkit`](reports/mappings.md#rcef_faceto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 34 | proposed |
| [`rcef_cheek_puff.to_arkit`](reports/mappings.md#rcef_cheek_puffto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 1 | proposed |
| [`rcef_jaw_thrust.to_arkit`](reports/mappings.md#rcef_jaw_thrustto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 1 | proposed |
| [`rcef_jaw_sideways.to_arkit`](reports/mappings.md#rcef_jaw_sidewaysto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 2 | proposed |
| [`rcef_mouth_shift.to_arkit`](reports/mappings.md#rcef_mouth_shiftto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 2 | proposed |
| [`rcef_chin_raise_upper_lip.to_arkit`](reports/mappings.md#rcef_chin_raise_upper_lipto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 1 | proposed |
| [`rcef_blink.to_arkit`](reports/mappings.md#rcef_blinkto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 2 | proposed |
| [`rcef_gaze.to_arkit`](reports/mappings.md#rcef_gazeto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 8 | proposed |
| [`rcef_tongue_out.to_arkit`](reports/mappings.md#rcef_tongue_outto_arkit) | `rcef.canonical_expression` → `arkit.coefficient` | 1 | proposed |
| [`rcef_face.to_fb2`](reports/mappings.md#rcef_faceto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 41 | proposed |
| [`rcef_cheek_puff.to_fb2`](reports/mappings.md#rcef_cheek_puffto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_jaw_thrust.to_fb2`](reports/mappings.md#rcef_jaw_thrustto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 1 | proposed |
| [`rcef_jaw_sideways.to_fb2`](reports/mappings.md#rcef_jaw_sidewaysto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_mouth_shift.to_fb2`](reports/mappings.md#rcef_mouth_shiftto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_chin_raise_upper_lip.to_fb2`](reports/mappings.md#rcef_chin_raise_upper_lipto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 1 | proposed |
| [`rcef_blink.to_fb2`](reports/mappings.md#rcef_blinkto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_gaze.to_fb2`](reports/mappings.md#rcef_gazeto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 12 | proposed |
| [`rcef_tongue_out.to_fb2`](reports/mappings.md#rcef_tongue_outto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 1 | proposed |
| [`rcef_cheek_suck.to_fb2`](reports/mappings.md#rcef_cheek_suckto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_lip_tighten.to_fb2`](reports/mappings.md#rcef_lip_tightento_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 2 | proposed |
| [`rcef_tongue_place.to_fb2`](reports/mappings.md#rcef_tongue_placeto_fb2) | `rcef.canonical_expression` → `openxr.fb2` | 6 | proposed |
| [`rcef_face.to_vrcft_artist`](reports/mappings.md#rcef_faceto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 47 | proposed |
| [`rcef_cheek_puff.to_vrcft_artist`](reports/mappings.md#rcef_cheek_puffto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 2 | proposed |
| [`rcef_jaw_thrust.to_vrcft_artist`](reports/mappings.md#rcef_jaw_thrustto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 1 | proposed |
| [`rcef_jaw_sideways.to_vrcft_artist`](reports/mappings.md#rcef_jaw_sidewaysto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 2 | proposed |
| [`rcef_mouth_shift.to_vrcft_artist`](reports/mappings.md#rcef_mouth_shiftto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 4 | proposed |
| [`rcef_chin_raise_upper_lip.to_vrcft_artist`](reports/mappings.md#rcef_chin_raise_upper_lipto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 1 | proposed |
| [`rcef_blink.to_vrcft_artist`](reports/mappings.md#rcef_blinkto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 2 | proposed |
| [`rcef_gaze.to_vrcft_artist`](reports/mappings.md#rcef_gazeto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 8 | proposed |
| [`rcef_tongue_out.to_vrcft_artist`](reports/mappings.md#rcef_tongue_outto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 1 | proposed |
| [`rcef_cheek_suck.to_vrcft_artist`](reports/mappings.md#rcef_cheek_suckto_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 2 | proposed |
| [`rcef_lip_tighten.to_vrcft_artist`](reports/mappings.md#rcef_lip_tightento_vrcft_artist) | `rcef.canonical_expression` → `vrcft.artist.base` | 2 | proposed |
| [`rcef_blink.to_vrm`](reports/mappings.md#rcef_blinkto_vrm) | `rcef.canonical_expression` → `vrm.preset` | 2 | proposed |
| [`rcef_blink.to_vrcft_eye`](reports/mappings.md#rcef_blinkto_vrcft_eye) | `rcef.canonical_expression` → `vrcft.eye` | 2 | proposed |
| [`rcef_pupil_mm.to_vrcft_eye`](reports/mappings.md#rcef_pupil_mmto_vrcft_eye) | `rcef.canonical_expression` → `vrcft.eye` | 2 | verified_current |
| [`rcef_face.to_facs`](reports/mappings.md#rcef_faceto_facs) | `rcef.canonical_expression` → `facs.code` | 37 | proposed |
| [`rcef_cheek_puff.to_facs`](reports/mappings.md#rcef_cheek_puffto_facs) | `rcef.canonical_expression` → `facs.code` | 2 | proposed |
| [`rcef_jaw_thrust.to_facs`](reports/mappings.md#rcef_jaw_thrustto_facs) | `rcef.canonical_expression` → `facs.code` | 1 | proposed |
| [`rcef_jaw_sideways.to_facs`](reports/mappings.md#rcef_jaw_sidewaysto_facs) | `rcef.canonical_expression` → `facs.code` | 2 | proposed |
| [`rcef_blink.to_facs`](reports/mappings.md#rcef_blinkto_facs) | `rcef.canonical_expression` → `facs.code` | 2 | proposed |
| [`rcef_tongue_out.to_facs`](reports/mappings.md#rcef_tongue_outto_facs) | `rcef.canonical_expression` → `facs.code` | 1 | proposed |
| [`rcef_cheek_suck.to_facs`](reports/mappings.md#rcef_cheek_suckto_facs) | `rcef.canonical_expression` → `facs.code` | 2 | proposed |
| [`rcef_lip_tighten.to_facs`](reports/mappings.md#rcef_lip_tightento_facs) | `rcef.canonical_expression` → `facs.code` | 2 | proposed |

#### Maps into the canonical viseme set

Each map reads one source set and writes one group of the canonical viseme set. `visemes_aggregate.to_rcef` writes `alveolar_floor`, the sum of the three alveolar classes and `rhotic` clamped at 1, through one helper value.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`visemes_vowel.to_rcef`](reports/mappings.md#visemes_vowelto_rcef) | `openxr.visemes` → `rcef.canonical_viseme` | 5 | proposed |
| [`visemes_consonant.to_rcef`](reports/mappings.md#visemes_consonantto_rcef) | `openxr.visemes` → `rcef.canonical_viseme` | 9 | proposed |
| [`visemes_rest.to_rcef`](reports/mappings.md#visemes_restto_rcef) | `openxr.visemes` → `rcef.canonical_viseme` | 1 | proposed |
| [`visemes_aggregate.to_rcef`](reports/mappings.md#visemes_aggregateto_rcef) | `openxr.visemes` → `rcef.canonical_viseme` | 2 | proposed |
| [`vrm_vowel.to_rcef`](reports/mappings.md#vrm_vowelto_rcef) | `vrm.preset` → `rcef.canonical_viseme` | 5 | proposed |

#### Maps out of the canonical viseme set

Each map reads one group and writes the target set's visemes for it. No map reads `alveolar_floor`.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`rcef_viseme_vowel.to_visemes`](reports/mappings.md#rcef_viseme_vowelto_visemes) | `rcef.canonical_viseme` → `openxr.visemes` | 5 | proposed |
| [`rcef_viseme_consonant.to_visemes`](reports/mappings.md#rcef_viseme_consonantto_visemes) | `rcef.canonical_viseme` → `openxr.visemes` | 9 | proposed |
| [`rcef_viseme_rest.to_visemes`](reports/mappings.md#rcef_viseme_restto_visemes) | `rcef.canonical_viseme` → `openxr.visemes` | 1 | proposed |
| [`rcef_viseme_vowel.to_vrm`](reports/mappings.md#rcef_viseme_vowelto_vrm) | `rcef.canonical_viseme` → `vrm.preset` | 5 | proposed |

#### The viseme pose bridge

The bridge goes from the canonical viseme set to the canonical expression set. Each canonical expression signal of the groups `face`, `cheek_puff`, `jaw_thrust` and `chin_raise_upper_lip` is the sum of each class weight times the class's pose, clamped at 1. The poses come from the calibration record [`viseme-poses.rocketbox-features`](calibration/README.md): the viseme shapes of 18 Rocketbox rigs, measured in their own ARKit shapes with Left and Right tied, and held out on 4 others. A class passes by its whole-face shape or by a perceptual gate of visible mouth features. The bridge reads only the 11 classes that pass on every held-out rig, among them `bilabial` (p, b and m), whose pose keeps the lips closed and draws them back like the rigs' own. `labiodental`, `postalveolar`, `coronal_nasal_lateral` and `rhotic` fail and move nothing. So META visemes and VRM vowels can drive ARKit, FB2 and Unified Expressions faces, and FACS values, with the limits that [canonical-set.md](docs/canonical-set.md#viseme-pose-bridge) gives.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`rcef_viseme_pose.to_rcef_expression`](reports/mappings.md#rcef_viseme_poseto_rcef_expression) | `rcef.canonical_viseme` → `rcef.canonical_expression` | 101 | proposed |

Not translated yet, and why:

- **VRM lookUp/Down/Left/Right:** VRM drives gaze by angle, through range maps whose input is in degrees. FB2 and ARKit publish no maximum angle. A translation needs an operator for angles and curves.
- **VRM emotions** (happy, angry, sad, relaxed, surprised): to turn muscle movements into an emotion label is a classification, not a linear calculation. Also, each model authors its own binds.
- **MediaPipe to ARKit:** only one independent implementation (three.js) maps MediaPipe to ARKit. The model card that would state the ARKit basis has not been reviewed.
- **Unified Expressions to ARKit or FB2:** there is no map from Unified Expressions into the canonical expression set yet. FB2 to Unified Expressions now runs through the canonical expression set.
- **Unified Expressions shapes with no FB2 counterpart** (pupil dilation and constriction, tongue directions, TongueFlat and others): no map writes them yet. Cheek suck and mouth tightener now come from FB2 through the canonical expression set.
- **FACS gaze codes (61-64) and FACS codes with no canonical signal** (for example 25 Lips part and 27 Mouth stretch): the source does not say whose left the gaze codes mean, so canonical gaze has no FACS code yet. The other codes are `unresolved` rows; the codec reads 27 as 26 and 45 and 46 as 43.
- **Expression to viseme:** a face pose does not identify the sound, so no map goes from the canonical expression set to the canonical viseme set.
- **Viseme sets other than META and the VRM vowels** (for example Amazon Polly, or sets with one class for several canonical classes): each needs its own audit against the canonical viseme classes before it gets maps.

### Expression sets

This table shows which expression sets the maps read or write. Each name is a file in `profiles/` without `.toml`, except `rcef.canonical_expression`, `rcef.canonical_viseme` and `rcef.intermediate`, which are in `data/`. [docs/expression-sets.md](docs/expression-sets.md) gives each file's revision, signal count, role, documentation, pinned source and licence or terms. It also explains the signal counts and RCEF's own sets.

| Provider | Read or written by a map | Inventory only |
|---|---|---|
| Apple ARKit | `arkit.coefficient` | `arkit.ancillary` |
| OpenXR (FB and META extensions) | `openxr.fb2`, `openxr.visemes` | `openxr.fb`, `openxr.ancillary` |
| VRCFaceTracking | `vrcft.eye`, `vrcft.artist.base` | `vrcft.artist.blended`, `vrcft.transport`, `vrcft.parameter.float`, `vrcft.parameter.flags`, `vrcft.parameter.encoding` |
| VRM 1.0 | `vrm.preset` | none |
| FACS (code numbers from a public list) | `facs.code` | none |
| MediaPipe | none | `mediapipe.label`, `mediapipe.score` |
| Godot | none | `godot.base`, `godot.blended` |
| Roblox | none | `roblox.control` |
| RCEF | `rcef.canonical_expression`, `rcef.canonical_viseme`, `rcef.intermediate` (RCEF's own sets), `fixture` (synthetic) | none |

## Getting started

You need Python 3.11 or newer and [msf-character-tools](https://github.com/MetaverseStandards/msf_character_tools), which is maintained separately. RCEF locks msf-character-tools 0.5.0 in [tooling.lock.json](evidence/tooling.lock.json). The lock has one entry per release wheel, keyed by the wheel's tag, with the wheel's SHA-256. Pick the tag for your platform and Python:

| Platform | Python 3.11 | Python 3.12 and later |
|---|---|---|
| macOS 11 or later, Apple silicon | `cp311-cp311-macosx_11_0_arm64` | `cp312-abi3-macosx_11_0_arm64` |
| Linux x86_64 (glibc 2.28 or later) | `cp311-cp311-manylinux_2_28_x86_64` | `cp312-abi3-manylinux_2_28_x86_64` |
| Linux aarch64 (glibc 2.28 or later) | `cp311-cp311-manylinux_2_28_aarch64` | `cp312-abi3-manylinux_2_28_aarch64` |

Download that wheel from the [msf-character-tools v0.5.0 release](https://github.com/MetaverseStandards/msf_character_tools/releases/tag/v0.5.0), then install it with the hash from the lock:

```sh
TAG=cp312-abi3-macosx_11_0_arm64
WHEEL=msf_character_tools-0.5.0-$TAG.whl
DIR=$(mktemp -d)
curl -fsSL -o "$DIR/$WHEEL" "https://github.com/MetaverseStandards/msf_character_tools/releases/download/v0.5.0/$WHEEL"
SHA=$(python3 -c 'import json, sys; print(json.load(open("evidence/tooling.lock.json"))["wheels"][sys.argv[1]]["sha256"])' "$TAG")
echo "msf-character-tools @ file://$DIR/$WHEEL --hash=sha256:$SHA" > "$DIR/msf-character-tools.txt"
uv pip install --python PATH/TO/python --require-hashes -r "$DIR/msf-character-tools.txt"
```

The release is public, so the download needs no login or token. Without uv, `python3 -m pip install --require-hashes -r "$DIR/msf-character-tools.txt"` does the same.

You can also build the wheels yourself with msf-character-tools' `scripts/build_release.sh` at the locked commit. Its `docs/building.md` lists the pinned inputs that give the same bytes. `check.py` refuses any other build: every installed file must match the lock.

Run these commands from the RCEF checkout. Check the outputs and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

## Editing the data

Edit the TOML files, then regenerate the outputs and review the diffs. Two commands cover the shared outputs and the reports:

```sh
python3 -B check.py            # CHECK: do the outputs still match the TOML? Writes nothing.
python3 -B check.py --write    # APPLY: regenerate generated/ and reports/ from the TOML.
```

Four more scripts write the other generated files. Without `--write`, each one only checks its files and fails if they are out of date:

```sh
python3 -B scripts/build_canonical.py --write     # data/canonical_expression.toml, data/canonical_viseme.toml, profiles/facs.code.toml and mappings/canonical_*.toml from docs/canonical-set.md and its audit
python3 -B scripts/export_references.py --write   # references.md from evidence/sources.toml
python3 -B scripts/export_toml_index.py --write   # docs/toml-index.csv from all TOML files
python3 -B scripts/compare_godot.py --write       # docs/godot_comparison.md from the pack
```

Any change to a TOML file changes `docs/toml-index.csv`. Any change to a string in a TOML file also changes the pack hash. Then `rcef.pack.json`, `coverage.json`, both `SHA256SUMS` files and the three Markdown reports change too. [AGENTS.md](AGENTS.md#known-traps) says when the CSV files change. Regenerate everything, review every diff, and commit the TOML and the generated files together. Each data change also needs an entry in [CHANGELOG.md](CHANGELOG.md), in the top section, `Data 0.5.0 — unreleased`.

GitHub Actions is not turned on for this repository. Run `sh scripts/ci_local.sh` instead. It runs `check.py` and the tests on Python 3.11 and 3.12. Paste its summary into the pull request. It expects a venv for each version with the locked wheel installed. The comment at the top of the script gives the paths.

### Common tasks

- **Fix or add a mapping in an existing map**

  1. Edit or add the mapping in its file in `mappings/`. In the TOML, a mapping is one entry in the map's `rules` array. It needs `id`, `inputs`, `outputs`, `operator`, `disposition`, `assumptions`, `evidence`, `evidence_status` and `loss_annotations`, and `mapping_quality` when its disposition is `mapped`. See [Maps, mappings and loss annotations](docs/architecture.md#maps-mappings-and-loss-annotations).
     Do not edit `data/canonical_expression.toml`, `data/canonical_viseme.toml` or `mappings/canonical_*.toml` by hand. `scripts/build_canonical.py --write` writes them from `docs/canonical-set.md`, its definitions audit, the IPA chart assignment in `tests/fixtures/ipa_chart_symbols.json` and the retired direct maps as frozen in `tests/fixtures/baseline-dea1713.pack.json`; change the documents, then run it.
     The maps of the canonical sets are frozen as in the latest passing A/B freeze: `tests/test_pivot_structure.py` fails if one differs from `tests/fixtures/b-maps-ab.pivot-v1.json`. A change that keeps every value needs a "revise" freeze first ([ab/README.md](ab/README.md)).
  2. Cite only evidence IDs that are in `evidence/sources.toml`. To add a source, follow the evidence steps in the next tasks.
  3. Run `python3 -B check.py --write` and `python3 -B scripts/export_toml_index.py --write`. If you changed an FB2 in-map or an ARKit out-map, also run `python3 -B scripts/compare_godot.py --write`.
  4. If the number of mappings changed, update the map's row in the [Mappings](#mappings) table, the totals in [What RCEF covers](#what-rcef-covers) and AGENTS.md, and the counts in `docs/architecture.md`.
  5. Add a CHANGELOG entry, and run the tests.

  Commit the TOML, `generated/`, `reports/`, `docs/toml-index.csv`, any other changed generated file, the README and the CHANGELOG together.

- **Add a new map**

  1. Add a `[[mappings]]` record with a new `id` and its `rules`, in a file in `mappings/`. Mapping IDs must be unique across all maps. The file name must end in lowercase `.toml`.
  2. Regenerate as in the first task.
  3. Add a row for the map to the [Mappings](#mappings) table: a link to `reports/mappings.md#` followed by the map ID without dots, the source and target sets, the number of mappings and the evidence status. `tests/test_readme_sources.py` fails until the row agrees with the pack.
  4. Update the counts in `docs/architecture.md`, and the hand-made visuals. See [the validation checklist](docs/architecture.md#9-independent-validation-checklist).
  5. Add a CHANGELOG entry, and run the tests.

- **Add or update an expression set**

  1. Add or update its evidence record in `evidence/sources.toml`. [CONTRIBUTING](CONTRIBUTING.md) lists what a provider entry needs. Then run `python3 -B scripts/export_references.py --write` to update `references.md`.
  2. Add or edit `profiles/<name>.toml`: the `[[signals]]` records, each with a disposition and its evidence, and the `[[profiles]]` record that lists them.
  3. Add or update the file's row in [docs/expression-sets.md](docs/expression-sets.md), and its name in the [Expression sets](#expression-sets) table above. Add a new provider to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
  4. Regenerate as in the first task. Update the counts in [What RCEF covers](#what-rcef-covers), AGENTS.md and `docs/architecture.md`.
  5. Optional: check the source bytes. `python3 -B scripts/verify_sources.py --source ID --cache DIR` checks the exact digest of a public source. It saves source bytes only to the cache that you name. Use a directory outside this repository. Then `python3 -B scripts/audit_inventories.py --cache DIR` compares the selected names, their order and the real enum indices with those verified bytes. The auditor needs every source it uses, so first run `verify_sources.py --cache DIR` without `--source`.
  6. Add a CHANGELOG entry, and run the tests.

  Commit the evidence, `references.md`, the profile, the generated files, the documentation tables and the CHANGELOG together.

- **Update the msf-character-tools lock**

  Install the reviewed new release wheel by hash. Then run `python3 -B check.py --update-lock --wheel PATH/TO/WHEEL`, once from each Python and platform whose wheel tag you support. Run `check.py` and the tests again. Update the version, the wheel table and the install commands in [Getting started](#getting-started), and the "0.5.0" mentions in AGENTS.md and `docs/architecture.md`. Add a CHANGELOG entry. Commit `evidence/tooling.lock.json`, `evidence/tooling.lock.previous.json` (if the update made one), the README and the CHANGELOG together. [The msf-character-tools lock](docs/architecture.md#the-msf-character-tools-lock) gives the full rules.

## How checking works

`check.py` runs four steps in order. It stops at the first failure. [Section 2](docs/architecture.md#2-what-checkpy-does) of the architecture guide describes each step.

1. **The lock.** It checks that the installed msf-character-tools is exactly a locked release wheel. If not, it exits 2 before it reads any data.
2. **The calibration records.** It checks the records in [calibration/](calibration/README.md) and the mappings that cite them. This step does not use msf-character-tools.
3. **The shared outputs.** It runs msf-character-tools to build the files in `generated/`: `rcef.pack.json`, `rcef_mapping.csv`, `coverage.json` and `SHA256SUMS`. With `--write` it writes them. Without `--write` it checks that they have not changed.
4. **The readable reports.** It runs `scripts/export_reports.py` in the same way.

The lock records a SHA-256 for every file in the installed package, for each wheel tag. One lock serves several Pythons. Checking never clones or downloads anything. [The msf-character-tools lock](docs/architecture.md#the-msf-character-tools-lock) gives the full rules, and tells how to adopt a new release and how to roll back.

[Section 7](docs/architecture.md#7-generated-files-and-readable-reports) gives the encoding of the outputs. [Section 8](docs/architecture.md#8-edit-regenerate-check-and-qualify) says what the tests show and what they do not show.

## Reports

These readable reports come from `generated/rcef.pack.json` (step 4 above):

- [Inventory Markdown](reports/inventory.md) and [CSV](reports/inventory.csv): every signal and profile membership, including excluded, unsupported and unresolved records. They show native names, indices, ranges, calibration, evidence and reasons. Native defaults and calibrated neutral values are kept separate.
- [Mapping Markdown](reports/mappings.md) and [CSV](reports/mappings.csv): every authored one-way mapping with its operator, status, assumptions and loss annotations.
- [Canonical correspondence Markdown](reports/canonical_correspondence.md) and [CSV](reports/canonical_correspondence.csv): a comparison table that uses only authored mappings. A dash means no authored mapping. Unresolved relationships stay labeled. These tables do not show cross-provider or anatomical equivalence.

To check only the reports with Python's standard library, run `python3 -B scripts/export_reports.py`. Add `--write` to regenerate them. [Section 7](docs/architecture.md#7-generated-files-and-readable-reports) describes the report checksums.

## Examples

[examples/README.md](examples/README.md) uses RCEF from start to end with the msf-character-tools public API. It translates FB2 frames to ARKit weights, and META visemes to VRM presets, from CSV, through the canonical expression and viseme sets. It then drives two Microsoft Rocketbox faces and the ICT-FaceKit face with a FACS-based expression library, both directly and through RCEF's mappings, and reports the residuals. It also renders a short spoken phrase as visemes on Rocketbox and on a VRM model, and drives a held-out Rocketbox rig and ICT-FaceKit with visemes through the viseme pose bridge.

## Calibration

[calibration/](calibration/README.md) holds software-only calibration records. They are fits to renders or mesh geometry of example rigs, not measurements of a tracker. `check.py` refuses a mapping that cites a record unless its values are exactly the record's frozen values (knots, or the poses of a weighted sum) and each channel it reads passed its held-out cells. A record may also give a channel a perceptual gate: frozen visible features with tolerances; the channel then passes by its shape cells or by all its feature cells. In data 0.5.0 the 45 weighted sums of the viseme pose bridge cite `viseme-poses.rocketbox-features`, for the 11 classes that pass. The earlier `viseme-poses.rocketbox-female` and `viseme-poses.rocketbox-multi` stay as history; no mapping cites them. The renderer for the rendered fits is in [tools/render/](tools/render/README.md), and the tools that make the records are in [tools/calibration/](tools/calibration/README.md).

## Open questions

Each open item below is stated in full in the linked document.

- **Calibration between providers.** In general, how one provider's calibration relates to another's is still unresolved. Maximum angles and model calibration are unknown, so no cross-provider identity is possible ([survey.md](survey.md#semantics-that-remain-distinct)). No provider publishes its gain, so the mappings assume that equal weights mean equal expressions ([AGENTS.md](AGENTS.md#limits)).
- **Missing evidence.** RCEF has no evidence yet for: MediaPipe model calibration and provenance, FB1 numeric bounds, FB2 maximum angles per direction, VRCFT raw gaze units and source contradictions, and which Roblox list of required poses is authoritative. These gaps block the derived mappings that depend on them ([proposal.md](proposal.md#release-limits-and-remaining-evidence), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open)). [docs/calibration/mediapipe-licence.md](docs/calibration/mediapipe-licence.md) records a later check of the MediaPipe model's licence and training-data statements.
- **VRM specification prose.** It is still unknown whether VRM specification prose may be redistributed. RCEF links to it and does not copy it ([REVIEW.md](REVIEW.md#evidence-and-gates-still-open)).
- **Mappings not translated yet.** See the list under [Mappings](#mappings).
- **Physical capture.** [docs/calibration/physical-protocol.md](docs/calibration/physical-protocol.md) designs a capture with real trackers and real faces. It has not been run. Before any part of it runs, it needs a named owner, an ethics and legal review, and approval from the project's release owners ([GOVERNANCE.md](GOVERNANCE.md)).
- **Later gates.** Device integration, physical calibration, visual equivalence of geometry, execution of VRM bindings, Roblox certification, native and host acceptance, and standards adoption are later gates. Each one needs its own measured acceptance ([GOVERNANCE.md](GOVERNANCE.md), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open)).

## More documentation

- [Architecture guide](docs/architecture.md): what `check.py` does, how TOML is discovered and validated, how maps compile and run in memory, the generated reports, and worked examples of each operator. The [visual architecture report](docs/architecture.html), [standalone diagram](docs/architecture.svg) and [TOML file index](docs/toml-index.csv) describe the same data 0.5.0 tree as the guide.
- [Expression sets](docs/expression-sets.md): every profile file, with its documentation, pinned source and licence.
- [Godot comparison](docs/godot_comparison.md): RCEF's FB2 → ARKit mappings compared with the routes in Godot's public sources.
- [Canonical expression set (draft)](docs/canonical-set.md): the proposed pivot vocabulary, with its [definitions audit](docs/canonical-set-audit.md) and the [FACS intensity codec](docs/facs-intensity.md). It is a proposal for review. Data 0.5.0 holds its expression part as the draft profile `rcef.canonical_expression` and its visemes as the draft profile `rcef.canonical_viseme`, with their maps; the FACS codes are the draft profile `facs.code`.
- [Survey](survey.md), [proposal](proposal.md), [references](references.md) and [source evidence](evidence/sources.toml).
- [Review](REVIEW.md) and [third-party notices](THIRD_PARTY_NOTICES.md).
- [Calibration notes](docs/calibration/): the physical capture design, the action unit dataset review and the MediaPipe licence check.
- [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md): read them before you extend or release the inventory.
- [AGENTS.md](AGENTS.md): coding agents, read this first.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Copyright (c) 2026 Metaverse Standards Forum. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) keeps the inherited source licenses and provenance. RCEF does not relicense the provider documentation it refers to.
