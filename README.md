# RCEF: Reference Canonical Expression Framework

## Purpose

Face trackers and avatar systems each publish their own set of expression signals. ARKit, OpenXR FB2, MediaPipe, VRCFaceTracking, VRM, Godot and Roblox give these signals different names. They also use different scales and calibrations. So a value from one system cannot simply be copied into another system.

RCEF records public expression interfaces, their calibration limits, and explicit one-way scalar mappings between them:

- It records each public expression interface as data. Each record states its calibration limits and cites a pinned public source.
- It defines a small canonical set of 21 signals. Each canonical signal keeps the calibration of its provider.
- It authors explicit one-way mappings from one set to another. Each mapping states its assumptions and its losses.
- It checks all of this with [msf-character-tools](https://github.com/MetaverseStandards/msf_character_tools), which is maintained separately.

The TOML files are the authoritative data. RCEF records provider names as facts, with attribution. Its definitions and examples are original.

RCEF is not these things:

- It is not a new universal blendshape set. "Canonical" does not mean one universal anatomy or one shared calibration.
- Its cross-provider mappings are proposed approximations. They do not claim visual equivalence.
- It does not describe how a stylized character looks. RCEF describes what a signal means. Stylization is a separate layer on top of RCEF.

[RCSF](https://github.com/MetaverseStandards/RCSF), the Reference Canonical Skeletal Framework, does the same job for skeletons in the same Metaverse Standards Forum organization on GitHub.

## Contents

You edit the TOML files: `pack.toml`, `profiles/`, `data/`, `mappings/` and `evidence/sources.toml`. They are the source of truth. Scripts write everything in `generated/` and `reports/`, and also `references.md`, `docs/toml-index.csv` and `docs/godot_comparison.md`. Do not edit those files by hand.

- `profiles/` - One TOML file per public expression set. `fixture.toml` holds RCEF's own synthetic fixtures. Source of truth.
- `data/` - RCEF's own sets: `rcef.canonical` (21 signals) and `rcef.intermediate` (4 signals). Source of truth.
- `mappings/` - The maps. Each map is a group of one-way mappings. Source of truth.
- `pack.toml` - Root metadata: the schema, data and operator versions, the pack ID and the licence. Source of truth.
- `evidence/` - `sources.toml` (the pinned public sources, source of truth), `tooling.lock.json` (the msf-character-tools lock) and `input-contracts/` (an optional input schema that RCEF itself does not use).
- `calibration/` - Software-only calibration records (`*.cal`) and the append-only `FREEZES` ledger.
- `generated/` - Generated: the pack, the signal and profile matrix CSV, coverage and checksums.
- `reports/` - Generated: readable inventory, mapping and canonical correspondence reports, in Markdown and CSV, with checksums.
- `fixtures/` - `mapping_samples.json`: sample inputs and expected outputs for the affine, bilateral and identity checks.
- `examples/` - End-to-end translations and face pipelines. Their inputs are in `examples/data/`.
- `tools/` - Optional tools that make calibration records (`tools/calibration/`), and the macOS renderer for calibration fits (`tools/render/`).
- `scripts/` - Export, comparison, source-check and local CI scripts.
- `check.py` - Checks the msf-character-tools install, the calibration records and all outputs. With `--write` it regenerates the outputs.
- `docs/` - The architecture guide and its visuals, the full expression-set table, `toml-index.csv`, `godot_comparison.md` and calibration notes.
- `tests/` - The `unittest` suite. Its inputs are in `tests/fixtures/`.
- `survey.md` - The selected scope of each surveyed interface and its calibration boundary.
- `proposal.md` - The authoring and mapping proposal: wire contract, executable examples and release limits.
- `references.md` - Generated from `evidence/sources.toml`: each public source with its revision, retrieval date and SHA-256.
- `CHANGELOG.md` - Changes for each data version.
- `CONTRIBUTING.md` - What a change must include.
- `GOVERNANCE.md` - Ownership and release gates.
- `AGENTS.md` - The guide for coding agents. `CLAUDE.md` points to it.
- `REVIEW.md` - The implementation self-review of 2026-10-07.
- `LICENSE`, `LICENSES/`, `THIRD_PARTY_NOTICES.md` - The licences, their full texts, and the inherited source licences and provenance.
- `.github/workflows/check.yml` - The GitHub workflow. GitHub Actions is not turned on for this repository.

## What RCEF covers

RCEF has these selected inventories: ARKit 52, MediaPipe 52, OpenXR FB 63 and FB2 70, optional META visemes 15, VRCFT transport 88, raw/combined eye data, artist 102+42, publicly listed numeric avatar parameters 124 and activity flags 3, Godot 102+41, VRM 18, and Roblox 50. It also records ancillary enums, sentinels and encoding surfaces. These counts describe interfaces. They do not say how well anything tracks a face.

The canonical set has 21 scalar projections, and each one states its provider's calibration. They cover blink, jaw, brow, directional gaze and physical pupil diameter. The identity mappings keep the stated provider basis. Two original fixtures, one affine and one lossy bilateral, show the shared runtime. They do not claim visual equivalence.

Data 0.4.0 has 187 cross-provider mappings. They translate:

- FB2 to all 52 ARKit coefficients, and back (face and, separately, gaze);
- ARKit to VRCFaceTracking Unified Expressions;
- FB2 eye closure to VRM per-eye blinks;
- META visemes to VRM lip-sync presets.

The ARKit → FB2 gaze map also has 4 internal steps. Each step takes one eye's two opposing ARKit gaze directions (in and out, or up and down) to one intermediate difference. All of these mappings are proposed and approximate. They compile only with the approximation opt-in. Each one states its calibration assumptions and losses (see the [CHANGELOG](CHANGELOG.md)). Their tests compare results with expected values that `scripts/derive_fb2_goldens.py` derives from the pinned public sources, not from RCEF's own mappings.

### Mappings

Each row is one map: a group of mappings that turns values in the source set into values in the target set. `verified_current` means that the mapping restates a verified source fact (it copies a provider value to the canonical set). `proposed` means an approximate cross-provider translation that is backed by sources and compiles only with the approximation opt-in. [reports/mappings.md](reports/mappings.md) lists every mapping with its assumptions, losses and evidence. That report also lists the maps that this table leaves out: RCEF's synthetic test maps (`fixture.affine`, `fixture.bilateral`) and `survey.ambiguous`, which is recorded but cannot be executed.

| Map | Source set → target set | Mappings | Evidence status |
|---|---|---|---|
| [`arkit.to_canonical`](reports/mappings.md#arkitto_canonical) | `arkit.coefficient` → `rcef.canonical` | 9 | verified_current |
| [`fb2.to_canonical`](reports/mappings.md#fb2to_canonical) | `openxr.fb2` → `rcef.canonical` | 8 | verified_current |
| [`vrcft_eye.to_canonical`](reports/mappings.md#vrcft_eyeto_canonical) | `vrcft.eye` → `rcef.canonical` | 4 | verified_current |
| [`fb2.to_arkit`](reports/mappings.md#fb2to_arkit) | `openxr.fb2` → `arkit.coefficient` | 44 | proposed |
| [`fb2_gaze.to_arkit`](reports/mappings.md#fb2_gazeto_arkit) | `openxr.fb2` → `arkit.coefficient` | 8 | proposed |
| [`arkit.to_fb2`](reports/mappings.md#arkitto_fb2) | `arkit.coefficient` → `openxr.fb2` | 52 | proposed |
| [`arkit_gaze.to_fb2`](reports/mappings.md#arkit_gazeto_fb2) | `arkit.coefficient` → `openxr.fb2` | 12 | proposed |
| [`arkit.to_vrcft_artist`](reports/mappings.md#arkitto_vrcft_artist) | `arkit.coefficient` → `vrcft.artist.base` | 68 | proposed |
| [`fb2.to_vrm`](reports/mappings.md#fb2to_vrm) | `openxr.fb2` → `vrm.preset` | 2 | proposed |
| [`visemes.to_vrm`](reports/mappings.md#visemesto_vrm) | `openxr.visemes` → `vrm.preset` | 5 | proposed |

Not translated yet, and why:

- **VRM lookUp/Down/Left/Right:** VRM drives gaze by angle, through range maps whose input is in degrees. FB2 and ARKit publish no maximum angle. A translation needs an operator for angles and curves.
- **VRM emotions** (happy, angry, sad, relaxed, surprised): to turn muscle movements into an emotion label is a classification, not a linear calculation. Also, each model authors its own binds.
- **MediaPipe to ARKit:** only one independent implementation (three.js) maps MediaPipe to ARKit. The model card that would state the ARKit basis has not been reviewed.
- **Unified Expressions to ARKit, and FB2 to Unified Expressions:** these wait for the next round. FB2 to Unified Expressions is mostly FB2 to ARKit, then ARKit to Unified Expressions.
- **Unified Expressions shapes with no ARKit counterpart** (cheek suck, mouth tightener, pupil dilation and constriction, tongue directions and others): `arkit.to_vrcft_artist` does not write them.

### Expression sets

This table shows which expression sets the maps read or write. Each provider name is a file in `profiles/`, without `.toml`. RCEF's own sets are in `data/`. [docs/expression-sets.md](docs/expression-sets.md) has the full table: for each profile file, the expression set and revision, the signal count, the role in maps, the documentation, the pinned source, and the licence or terms. It also explains the signal counts and describes RCEF's own sets.

| Provider | Read or written by a map | Inventory only |
|---|---|---|
| Apple ARKit | `arkit.coefficient` | `arkit.ancillary` |
| OpenXR (FB and META extensions) | `openxr.fb2`, `openxr.visemes` | `openxr.fb`, `openxr.ancillary` |
| VRCFaceTracking | `vrcft.eye`, `vrcft.artist.base` | `vrcft.artist.blended`, `vrcft.transport`, `vrcft.parameter.float`, `vrcft.parameter.flags`, `vrcft.parameter.encoding` |
| VRM 1.0 | `vrm.preset` | none |
| MediaPipe | none | `mediapipe.label`, `mediapipe.score` |
| Godot | none | `godot.base`, `godot.blended` |
| Roblox | none | `roblox.control` |
| RCEF | `rcef.canonical`, `rcef.intermediate` (RCEF's own sets), `fixture` (synthetic) | none |

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

Run these commands from the RCEF checkout. Regenerate the outputs:

```sh
python3 -B check.py --write
```

Review the generated diffs. Then check the outputs without writing, and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

## Editing the data

The TOML files are the source of truth. Edit them, then regenerate the outputs. Two commands cover the shared outputs and the reports:

```sh
python3 -B check.py            # CHECK: do the outputs still match the TOML? Writes nothing.
python3 -B check.py --write    # APPLY: regenerate generated/ and reports/ from the TOML.
```

Three more scripts write the other generated files. Without `--write`, each one only checks its file and fails if the file is out of date:

```sh
python3 -B scripts/export_references.py --write   # references.md from evidence/sources.toml
python3 -B scripts/export_toml_index.py --write   # docs/toml-index.csv from all TOML files
python3 -B scripts/compare_godot.py --write       # docs/godot_comparison.md from the pack
```

Any change to a TOML file changes `docs/toml-index.csv`. Any change to a string in a TOML file also changes the pack hash. Then `rcef.pack.json`, `coverage.json`, both `SHA256SUMS` files and the three Markdown reports change too. [AGENTS.md](AGENTS.md#known-traps) says when the CSV files change. Regenerate everything, review every diff, and commit the TOML and the generated files together. Each data change also needs an entry in [CHANGELOG.md](CHANGELOG.md), in the top section, `Data 0.4.0 — unreleased`.

GitHub Actions is not turned on for this repository. Run `sh scripts/ci_local.sh` instead. It runs `check.py` and the tests on Python 3.11 and 3.12. Paste its summary into the pull request.

### Common tasks

- **Fix or add a mapping in an existing map**
  1. Edit the rule in its file in `mappings/`. A rule needs `id`, `inputs`, `outputs`, `operator`, `disposition`, `assumptions`, `evidence`, `evidence_status` and `loss_annotations`, and `mapping_quality` when it is mapped. See [Maps, mappings and loss annotations](docs/architecture.md#maps-mappings-and-loss-annotations).
  2. Cite only evidence IDs that are in `evidence/sources.toml`. To add a source, follow the evidence steps in the next tasks.
  3. Run `python3 -B check.py --write` and `python3 -B scripts/export_toml_index.py --write`. If you changed `fb2.to_arkit` or `fb2_gaze.to_arkit`, also run `python3 -B scripts/compare_godot.py --write`.
  4. If the number of mappings in the map changed, update the map's row in the [Mappings](#mappings) table, and the counts in [docs/architecture.md](docs/architecture.md).
  5. Add a CHANGELOG entry, and run the tests.

  Commit the TOML, `generated/`, `reports/`, `docs/toml-index.csv`, any other changed generated file, the README and the CHANGELOG together.

- **Add a new map**
  1. Add a `[[mappings]]` record with a new `id` and its `rules`, in a file in `mappings/`. Rule IDs must be unique across all maps. The file name must end in lowercase `.toml`.
  2. Regenerate as in the first task.
  3. Add a row for the map to the [Mappings](#mappings) table: a link to `reports/mappings.md#` followed by the map ID without dots, the source and target sets, the number of mappings and the evidence status. `tests/test_readme_sources.py` fails until the row agrees with the pack.
  4. Update the counts in `docs/architecture.md`, and the hand-made visuals. See [the validation checklist](docs/architecture.md#9-independent-validation-checklist).
  5. Add a CHANGELOG entry, and run the tests.

- **Add or update an expression set**
  1. Add or update its evidence record in `evidence/sources.toml`. [CONTRIBUTING](CONTRIBUTING.md) lists what a provider entry needs. Then run `python3 -B scripts/export_references.py --write` to update `references.md`.
  2. Add or edit `profiles/<name>.toml`: the `[[signals]]` records, each with a disposition and its evidence, and the `[[profiles]]` record that lists them.
  3. Add or update the file's row in [docs/expression-sets.md](docs/expression-sets.md), and its name in the [Expression sets](#expression-sets) table above. Add a new provider to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
  4. Regenerate as in the first task, and update the counts in `docs/architecture.md`.
  5. Optional: check the source bytes with `python3 -B scripts/verify_sources.py --source ID --cache DIR`. Use a cache directory outside this repository.
  6. Add a CHANGELOG entry, and run the tests.

  Commit the evidence, `references.md`, the profile, the generated files, the documentation tables and the CHANGELOG together.

- **Regenerate and check all outputs**
  Run `python3 -B check.py --write` and the three scripts above with `--write`. Review the diffs. Then run `python3 -B check.py`, the tests and `sh scripts/ci_local.sh`.

- **Update the msf-character-tools lock**
  Install the reviewed new release wheel by hash. Then run `python3 -B check.py --update-lock --wheel PATH/TO/WHEEL`, once from each Python and platform whose wheel tag you support. Run `check.py` and the tests again. Update the version, the wheel table and the install commands in [Getting started](#getting-started), and add a CHANGELOG entry. Commit `evidence/tooling.lock.json`, `evidence/tooling.lock.previous.json` (if the update made one), the README and the CHANGELOG together. [The msf-character-tools lock](docs/architecture.md#the-msf-character-tools-lock) gives the full rules.

## How checking works

`check.py` runs four steps in order. It stops at the first failure. [Section 2](docs/architecture.md#2-what-checkpy-does) of the architecture guide describes each step.

1. **The lock.** It checks that the installed msf-character-tools is exactly a locked release wheel. If not, it exits 2 before it reads any data.
2. **The calibration records.** It checks the records in [calibration/](calibration/README.md) and the mappings that cite them. This step does not use msf-character-tools.
3. **The shared outputs.** It runs msf-character-tools to build `generated/rcef.pack.json`, `rcef_mapping.csv`, `coverage.json` and `SHA256SUMS`. With `--write` it writes them. Without `--write` it checks that they have not changed.
4. **The readable reports.** It runs `scripts/export_reports.py` in the same way.

The lock records a SHA-256 for every file in the installed package, for each wheel tag. One lock serves several Pythons. Checking never clones or downloads anything. [The msf-character-tools lock](docs/architecture.md#the-msf-character-tools-lock) gives the full rules, and tells how to adopt a new release and how to roll back.

[Section 7](docs/architecture.md#7-generated-files-and-readable-reports) gives the encoding of the outputs. [Section 8](docs/architecture.md#8-edit-regenerate-check-and-qualify) says what the tests show and what they do not show.

`scripts/verify_sources.py` is optional. It checks the exact digests of the public sources, and it saves source bytes only to a cache that you name, outside this repository. `scripts/audit_inventories.py --cache CACHE` then compares the selected names, their order and the real enum indices with those verified bytes.

## Reports

`check.py --write` also writes readable reports from `generated/rcef.pack.json`, and `check.py` checks them:

- [Inventory Markdown](reports/inventory.md) and [CSV](reports/inventory.csv): every signal and profile membership, including excluded, unsupported and unresolved records. They show native names, indices, ranges, calibration, evidence and reasons. Native defaults and calibrated neutral values are kept separate.
- [Mapping Markdown](reports/mappings.md) and [CSV](reports/mappings.csv): every authored one-way mapping with its operator, status, assumptions and loss annotations.
- [Canonical correspondence Markdown](reports/canonical_correspondence.md) and [CSV](reports/canonical_correspondence.csv): a comparison table that uses only authored mappings. A dash means no authored mapping. Unresolved relationships stay labeled. These tables do not show cross-provider or anatomical equivalence.

To check only the reports with Python's standard library, run `python3 -B scripts/export_reports.py`. Add `--write` to regenerate them. [Section 7](docs/architecture.md#7-generated-files-and-readable-reports) describes the report checksums.

## Examples

[examples/README.md](examples/README.md) uses RCEF from start to end with the msf-character-tools public API. It translates FB2 frames to ARKit weights, and META visemes to VRM presets, from CSV. It then drives two Microsoft Rocketbox faces and the ICT-FaceKit face with a FACS-based expression library, both directly and through RCEF's mappings, and reports the residuals. It also renders a short spoken phrase as visemes on Rocketbox and on a VRM model.

## Calibration

[calibration/](calibration/README.md) holds software-only calibration records. They are fits to renders of example rigs, not measurements of a tracker. `check.py` refuses a mapping that cites a record unless the mapping's knots are exactly the record's frozen knots and every held-out cell for its channel passed. No mapping in data 0.4.0 cites a record. The renderer for those fits is in [tools/render/](tools/render/README.md), and the tools that make the records are in [tools/calibration/](tools/calibration/README.md).

## Open questions

These items are open. Each one is already stated in the document that is linked.

- **Calibration between providers.** In general, how one provider's calibration relates to another's is still unresolved. Maximum angles and model calibration are unknown, so no cross-provider identity is possible ([survey.md](survey.md#semantics-that-remain-distinct)). No provider publishes its gain, so the mappings assume that equal weights mean equal expressions ([AGENTS.md](AGENTS.md#limits)).
- **Missing evidence.** MediaPipe model calibration and provenance, FB1 numeric bounds, FB2 maximum angles per direction, VRCFT raw gaze units and source contradictions, and which Roblox list of required poses is authoritative. These gaps block the derived mappings that depend on them ([proposal.md](proposal.md#release-limits-and-remaining-evidence), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open)). [docs/calibration/mediapipe-licence.md](docs/calibration/mediapipe-licence.md) records a later check of the MediaPipe model's licence and training-data statements.
- **VRM specification prose.** It is still unknown whether VRM specification prose may be redistributed. RCEF links to it and does not copy it ([REVIEW.md](REVIEW.md#evidence-and-gates-still-open)).
- **Mappings not translated yet.** See the list under [Mappings](#mappings).
- **Physical capture.** [docs/calibration/physical-protocol.md](docs/calibration/physical-protocol.md) designs a capture with real trackers and real faces. It has not been run. Before any part of it runs, it needs a named owner, an ethics and legal review, and Ken's approval.
- **Later gates.** Device integration, physical calibration, visual equivalence of geometry, execution of VRM bindings, Roblox certification, native and host acceptance, and standards adoption are later gates. Each one needs its own measured acceptance ([GOVERNANCE.md](GOVERNANCE.md), [REVIEW.md](REVIEW.md#evidence-and-gates-still-open)).

## More documentation

- [Architecture guide](docs/architecture.md): what `check.py` does, how TOML is discovered and validated, how maps compile and run in memory, the generated reports, and worked examples of each operator. The [visual architecture report](docs/architecture.html), [standalone diagram](docs/architecture.svg) and [TOML file index](docs/toml-index.csv) describe the same data 0.4.0 tree as the guide.
- [Expression sets](docs/expression-sets.md): every profile file, with its documentation, pinned source and licence.
- [Godot comparison](docs/godot_comparison.md): RCEF's FB2 → ARKit mappings compared with the routes in Godot's public sources.
- [Survey](survey.md), [proposal](proposal.md), [references](references.md) and [source evidence](evidence/sources.toml).
- [Review](REVIEW.md) and [third-party notices](THIRD_PARTY_NOTICES.md).
- [Calibration notes](docs/calibration/): the physical capture design, the action unit dataset review and the MediaPipe licence check.
- [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md): read them before you extend or release the inventory.
- [AGENTS.md](AGENTS.md): coding agents, read this first.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Copyright (c) 2026 Metaverse Standards Forum. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) keeps the inherited source licenses and provenance. RCEF does not relicense the provider documentation it refers to.
