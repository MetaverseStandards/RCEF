<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Guide for coding agents

This guide is for coding agents that use RCEF or change it. It gives the facts that are hard to find in the tree, and links to the full documents for the rest. Part 1 is for an agent that only reads RCEF's outputs. Part 2 is for an agent that changes RCEF.

## Part 1: Using RCEF

RCEF is an open catalogue of face-expression standards (ARKit, OpenXR FB2, META visemes, MediaPipe, VRCFaceTracking, VRM, Godot, Roblox) and the maps between them. The TOML files are the data. msf-character-tools is a separate package. It is the engine that checks the data, builds the pack and evaluates the maps. The current data is 0.5.0 (unreleased), checked with msf-character-tools 0.5.0.

### Outputs

| File | What it holds |
|---|---|
| `generated/rcef.pack.json` | The complete validated data: signals, profiles, maps (each mapping with its operator, assumptions, losses and evidence) and evidence records. Load this file. |
| `generated/SHA256SUMS` | SHA-256 of the pack, `rcef_mapping.csv` and `coverage.json`. |
| `generated/coverage.json` | Signals by disposition, mappings by quality, evidence and rule use, totals, and `pack_sha256`. |
| `generated/rcef_mapping.csv` | A matrix: one row per signal, one column per profile. It is not a list of mappings. |
| `reports/mappings.md`, `.csv` | Every mapping with its operator, status, assumptions and losses. |
| `reports/inventory.md`, `.csv` | Every signal in every profile: native names, indices, ranges, calibration, evidence and reasons. |
| `reports/canonical_correspondence.md`, `.csv` | The 21 signals of `rcef.canonical` against the authored mappings. |
| `reports/SHA256SUMS` | SHA-256 of the six report files. Each Markdown report also records the pack's SHA-256. |

The README's [Mappings](README.md#mappings) table lists each map with its source and target profile.

### Translate tracker values

Use the msf-character-tools public API on the pack. Cross-provider maps are `proposed`, so `compile_mapping` refuses them (`E_APPROXIMATION`) unless you give `allow_approximation=True`. Run this from the RCEF checkout. It prints `0.5`:

```python
import json
import msf_character_tools as msf

doc = json.load(open('generated/rcef.pack.json', encoding='utf-8'))
pack = msf.compile_pack(msf.validate_authoring(doc).value).value
fb2 = msf.profile_snapshot(pack, 'openxr.fb2').value
arkit = msf.profile_snapshot(pack, 'arkit.coefficient').value
result = msf.compile_mapping(pack, fb2, arkit, 'fb2.to_arkit', allow_approximation=True)
assert result.ok, result.report.to_dict()
mapping = result.value
inputs = sorted(mapping.required_inputs)
values = dict.fromkeys(inputs, 0.0)
values['openxr.fb2.XR_FACE_EXPRESSION2_JAW_DROP_FB'] = 0.5
frame = {'timestamp': 0.0, 'values': values, 'validity': dict.fromkeys(inputs, True)}
out = msf.evaluate_mapping(mapping, [frame])
assert out.ok, out.report.to_dict()
print(out.value.samples[0]['values']['arkit.coefficient.jawOpen'])
```

What [examples/rcef_translate.py](examples/rcef_translate.py) does, and why:

- Every input in `required_inputs` must be in the frame, or the frame is refused (`E_MISSING_SAMPLE`).
- If any channel you give is marked invalid, msf-character-tools refuses the whole frame (`E_INVALID_SAMPLE`), even a channel that the map does not read. So give each map only its own inputs.
- An input's validity is the AND of the provider flags in its signal's `validity` field, for example `isValid AND isEyeFollowingBlendshapesValid` for FB2 gaze.
- If one frame in a call is refused, the call returns no values for any frame. Each error's `ref` begins with `/samples/<n>`, for example `/samples/1/openxr.fb2.XR_FACE_EXPRESSION2_BROW_LOWERER_L_FB`. Use it to find the refused frames, then evaluate the rest again.
- Face and gaze are separate maps: `fb2.to_arkit` with `fb2_gaze.to_arkit`, and `arkit.to_fb2` with `arkit_gaze.to_fb2`.
- To translate through the draft canonical expression set, use [examples/rcef_route.py](examples/rcef_route.py). It finds the in-maps and out-maps of a source and target set, runs each group's in-map and out-map, and reports a refused group without refusing the others.

[examples/README.md](examples/README.md) shows complete runs from CSV to CSV and onto face meshes.

### Evidence status

Each mapping (and each signal) has an `evidence_status` field. It says how well the mapping itself is supported. It is not the `status` of the evidence records it cites: all records in `evidence/sources.toml` are `verified_current`, including the records that `proposed` mappings cite. The values of `evidence_status` are:

- `verified_current`: the mapping restates a verified source fact. The three `*.to_canonical` maps and the synthetic `fixture.affine` and `fixture.bilateral` use it.
- `proposed`: an approximate cross-provider translation, backed by sources. It compiles only with the approximation opt-in. All 187 direct cross-provider mappings and their 4 internal gaze steps are `proposed`, and so are the 348 mappings into and out of the canonical expression and viseme sets and their 76 signals, and the 99 mappings of the viseme pose bridge between the two sets.
- `unresolved`: recorded but not executable. `compile_mapping` refuses it, even with the opt-in. The MediaPipe → ARKit map `survey.ambiguous` is the example.

`calibrated_software` is the `status` of the records in [calibration/](calibration/README.md). They are fits to renders or mesh geometry of example rigs, not measurements of a tracker. The pack uses schema 1.0, which does not have this value. So the mappings that cite a calibration record, the 45 weighted sums of the viseme pose bridge (`calibration.viseme-poses.rocketbox-female`), are `proposed`, and their assumptions say why.

`evidence_status` and `disposition` (`mapped`, `unresolved`, `excluded`, `unsupported`) are separate fields.

### Limits

- The mappings connect names and meanings the way the public sources do. Intensities are not calibrated: no provider publishes its gain, so equal weights are assumed to mean equal expressions. Each mapping states its assumptions and losses in `reports/mappings.md`.
- The only calibration data is the published calibration records. They are software-only. In `rig-gains.ict-rocketbox-female`, 3 of 51 shapes pass. In `viseme-poses.rocketbox-multi`, 9 of 15 viseme classes pass on all 4 held-out rigs (`sil` trivially, so 8 of 14 speech classes), and the viseme pose bridge reads only those. The earlier `viseme-poses.rocketbox-female` stays as history; no mapping cites it.
- The viseme pose bridge lets META visemes and VRM vowels drive ARKit, FB2 and Unified Expressions faces. Its poses are one rig's (Rocketbox Female's) viseme shapes in its own ARKit units. Classes that failed (among them `bilabial` and `vowel_mid_spread`) move nothing. There is no map from expressions back to visemes.
- The VRM maps come from specification texts only. No published table maps META visemes to VRM; `visemes.to_vrm` is a phoneme-label correspondence.
- The README lists what is [not translated yet](README.md#mappings), and why.

## Part 2: Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/architecture.md](docs/architecture.md) first. They give the full rules.

### Layout

| Path | Contents |
|---|---|
| `pack.toml` | Root metadata, including `data_version`. |
| `data/` | RCEF's own sets: `rcef.canonical` (21 signals), the draft `rcef.canonical_expression` (60), the draft `rcef.canonical_viseme` (16) and `rcef.intermediate` (63). `canonical_expression.toml` and `canonical_viseme.toml` are generated, and so is the part of `intermediate.toml` below its marker line (the 54 helpers of the viseme pose bridge, and the profile). |
| `profiles/` | One public expression set per file. `fixture.toml` holds synthetic fixtures. |
| `mappings/` | Maps. Each map is a group of one-way mappings. `canonical_*.toml` hold the maps into and out of the canonical sets, and `canonical_viseme_pose.toml` the viseme pose bridge between them; they are generated. |
| `evidence/` | `sources.toml` (pinned public sources), `tooling.lock.json` (the msf-character-tools lock), `input-contracts/`. |
| `calibration/` | `*.cal` software-only calibration records and the `FREEZES` ledger. |
| `generated/`, `reports/` | Outputs of `check.py --write`. Do not edit them by hand. |
| `scripts/` | Export, comparison, source-check and local CI scripts, and `build_canonical.py`, which writes the canonical expression set and its maps. |
| `tools/calibration/` | Optional tools that make calibration records. Most need extra packages; `viseme_poses.py` needs only msf-character-tools. `check.py` and the tests never run them; the tests check only the fitting and cell scoring. |
| `tools/render/` | `meshrender.swift`, the macOS offscreen renderer for calibration fits. |
| `examples/` | End-to-end translations and face pipelines; inputs in `examples/data/`. |
| `docs/` | Architecture guide and visuals, `expression-sets.md`, `toml-index.csv`, `godot_comparison.md`, calibration notes, and the draft canonical expression set: `canonical-set.md`, `canonical-set-audit.md` and `facs-intensity.md`. |
| `fixtures/` | `mapping_samples.json`: sample inputs and expected outputs for the affine, bilateral and identity checks in `tests/test_parity.py`. It is not `tests/fixtures/`, and it holds no signals (those are in `profiles/fixture.toml`). |
| `tests/` | The `unittest` suite and its inputs in `tests/fixtures/`. |

### Commands

Install the locked msf-character-tools wheel by hash as the README's [Getting started](README.md#getting-started) shows. Run every command from the checkout.

```sh
python3 -B check.py                          # check msf-character-tools, calibration, outputs; writes nothing
python3 -B check.py --write                  # regenerate generated/ and reports/
python3 -B -m unittest discover -s tests
python3 -B scripts/export_reports.py         # reports only; add --write to regenerate
python3 -B scripts/export_references.py --write   # references.md from evidence/sources.toml
python3 -B scripts/compare_godot.py --write       # docs/godot_comparison.md
python3 -B scripts/export_toml_index.py --write   # docs/toml-index.csv
python3 -B scripts/build_canonical.py --write     # data/canonical_expression.toml, data/canonical_viseme.toml, mappings/canonical_*.toml
sh scripts/ci_local.sh                       # check.py and tests on Python 3.11 and 3.12
```

Without `--write`, each script checks its output and exits non-zero if the output is out of date. `ci_local.sh` uses `$MSF/_tools/rcef-venv3.11` and `rcef-venv3.12`; `MSF` defaults to `~/.local/share/msf`.

### Rules that must not break

| Rule | What enforces it |
|---|---|
| Every provider fact cites a public source in `evidence/sources.toml`. The record needs the items that CONTRIBUTING lists. | msf-character-tools refuses a reference to a missing evidence id (`E_REFERENCE`). It also refuses a record with no `url`, unless the record is original work with `authorship` and `license` (`E_EVIDENCE`). No offline check reads the digests. Run `scripts/verify_sources.py --cache DIR` (outside the repo) and review the result. |
| Generated files and reports change only through the commands above, in the same commit as the source change. | `check.py` (byte drift), `tests/test_metadata.py`, `tests/test_readable_reports.py`. |
| The README's Mappings and Expression sets tables, the table in `docs/expression-sets.md`, `references.md`, `docs/toml-index.csv` and `docs/godot_comparison.md` agree with the data. You edit the three tables by hand; scripts write the others. | `tests/test_readme_sources.py`, `test_references.py`, `test_toml_index.py`, `test_godot_comparison.py`. The README test reads the README text between `### Mappings`, `### Expression sets` and `## Getting started`, and the `docs/expression-sets.md` text between `## Where each set comes from` and `## Signal counts`. Keep those headings. |
| Test expectations come from public sources, not from RCEF's mappings. | `scripts/derive_fb2_goldens.py` writes `tests/fixtures/fb2_goldens.json` and `godot_fb2_rules.csv` from cached source bytes, and never reads `mappings/`, `profiles/` or `data/`. Reviewers check that nobody edits them by hand. |
| Calibration records are frozen. `FREEZES` is append-only. A mapping can cite a record (`calibration.<id>`) only if its values are the frozen values and every held-out cell of every channel it reads passed: a `piecewise_linear` mapping has exactly the frozen knots; a `weighted_sum` (a pose sum) reads copies of the channels, is read only by one clamp with the knots (0, 0), (1, 1), (n, 1), and has exactly the frozen poses as weights. | `check.py`, before msf-character-tools runs; `tests/test_calibration.py`. `check.py` checks the ledger: the record must be the latest version, with its hash. Versions go up by one, dates never go back, and a re-freeze needs a reason. `check.py` cannot see Git history. Reviewers check that no line changed and that the ledger line came before the results. See [calibration/README.md](calibration/README.md). |
| msf-character-tools is exactly a locked release wheel. | `check.py` exits 2 for any other build; `tests/test_dependency.py`. |
| Each data change has an entry in [CHANGELOG.md](CHANGELOG.md). | Reviewers. The top section is `Data 0.5.0 — unreleased`: add entries there. Calibration records have their own ledger, so their entries go in the separate `Calibration and examples — unreleased` section. It sits below the two unreleased data sections (0.5.0 and 0.4.0) and above `Data 0.3.0`. `tests/test_metadata.py` checks that `data_version` in `pack.toml` equals the pack's and has the form `X.Y.Z`. |
| Code is MIT. Data and documentation are CC-BY-SA-4.0. Third-party facts are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Do not copy provider prose that has no open licence: write your own summary and cite the source. | Reviewers. Start each new file with a licence line, as the existing files do. |

To adopt a new msf-character-tools release: install its wheel by hash, then run `python3 -B check.py --update-lock --wheel PATH/TO/WHEEL`. Do this once from each Python and platform whose wheel tag you support. If the lock has the same commit and the same version, the new tag's entry is merged into it. If the commit or the version is different, the old lock moves to `tooling.lock.previous.json` and the new lock has only the new tag. Always give `--wheel` after a uv install. uv does not record the wheel's hash, so without `--wheel` the tag's `sha256` becomes `null`, and the README's install-by-hash steps then fail for that tag. pip records the hash, so after a pip install `--wheel` is optional.

### Known traps

- `check.py` checks the msf-character-tools install before anything else. If the install is wrong, it prints `Refusing to check` and exits 2 before it reads the data or the calibration records. It also refuses an `msf_character_tools` that would import from anywhere other than the installed distribution, for example through `PYTHONPATH`.
- `tests/test_dependency.py` builds fake msf-character-tools installs and checks that `check.py` refuses each one before msf-character-tools runs (a marker file shows whether it ran). If you change the lock format or the order of steps in `check.py`, keep these tests meaningful. For example, the tampered-package fake must use a version and wheel tag that the lock has, or it is refused for the wrong reason.
- Any change to a string in any TOML file changes the pack bytes and so the pack hash. Then `rcef.pack.json`, `coverage.json`, `generated/SHA256SUMS`, all three Markdown reports, `reports/SHA256SUMS` and `docs/toml-index.csv` change. A CSV report changes only if the string is one of its columns. `rcef_mapping.csv` changes only if a signal's id, label, value type, units, disposition, evidence status or profile membership changes. Regenerate everything, and commit what changed.
- `data/canonical_expression.toml`, `data/canonical_viseme.toml`, `mappings/canonical_*.toml` and the part of `data/intermediate.toml` below its marker line are written by `scripts/build_canonical.py` from `docs/canonical-set.md`, `docs/canonical-set-audit.md`, `tests/fixtures/ipa_chart_symbols.json`, `tests/fixtures/baseline-dea1713.pack.json` and, for the viseme pose bridge, `calibration/viseme-poses.rocketbox-female.cal`. Do not edit them by hand: `tests/test_pivot_structure.py` fails if they differ from what the script writes. Change the documents, then run the script with `--write`.
- The 7 direct maps (`fb2.to_arkit`, `fb2_gaze.to_arkit`, `arkit.to_fb2`, `arkit_gaze.to_fb2`, `arkit.to_vrcft_artist`, `fb2.to_vrm`, `visemes.to_vrm`) are frozen. `tests/test_pivot_structure.py` compares them, their signals and their evidence records with `tests/fixtures/baseline-dea1713.pack.json`.
- msf-character-tools reads every `*.toml` file in the tree as pack data, wherever it is (only hidden names and `generated/` are skipped). That is why calibration records are named `.cal`. Do not add other TOML files.
- `docs/architecture.html`, `.svg` and `.png` are made by hand, and no test checks them. When the data changes, update them and the counts in `docs/architecture.md`, and render the PNG from the SVG at the same size (1160 × 560). See the checklist in [docs/architecture.md](docs/architecture.md#9-independent-validation-checklist).
- The face and viseme pipelines download rigs on first use and check their hashes (`--cache DIR` for rig files, `--out DIR` for outputs; the defaults are under `~/.cache`). The slow tests skip unless their variables are set. See [examples/README.md](examples/README.md).
  - `tests/test_examples_slow.py`: `RCEF_SLOW_TESTS=1`, plus `RCEF_ICT_CACHE` for the ICT tests and `RCEF_RIG_CACHE` for the Rocketbox and VRM tests.
  - `tests/test_rig_gains.py` (slow part): `RCEF_SLOW_TESTS=1`, `RCEF_K3_ICT_CACHE`, `RCEF_RIG_CACHE` and `RCEF_RENDERER`.
  - `tests/test_translations.py` (slow part): `RCEF_SLOW_TESTS=1` only.

### Change workflow

1. Make small commits, one topic each.
2. Run `scripts/ci_local.sh`. It runs `check.py` and the tests on Python 3.11 and 3.12. Paste its summary into the pull request. GitHub Actions is not turned on for this repository.
3. Get an independent review. Review meaning and calibration separately from executable correctness.
4. Write in plain English (below).

## Writing style

- Use plain English in the style of ASD-STE100: short sentences, active voice, common words, one instruction per sentence. Leave out filler.
- In prose, one rule is a **mapping** and a group such as `fb2.to_arkit` is a **map** ("the FB2 → ARKit map has 44 mappings").
- Do not change code and schema names, such as `[[mappings]]` and `rules`.
