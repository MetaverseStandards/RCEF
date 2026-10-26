# RCEF: expression inventory and authoring parity

RCEF records public expression interfaces, their calibration limits, and explicit directional scalar rules. TOML is the authoritative data. Names are inventoried as attributed facts; definitions and examples are original.

## Contents

Selected inventories: ARKit 52, MediaPipe 52, OpenXR FB 63 and FB2 70, optional META visemes 15, VRCFT transport 88, raw/combined eye data, artist 102+42, publicly listed numeric avatar parameters 124 and activity flags 3, Godot 102+41, VRM 18, and Roblox 50. Ancillary enums, sentinels and encoding surfaces remain visible. These counts describe interfaces, not tracking fidelity.

The canonical subset has 21 explicitly provider-calibrated scalar projections spanning blink, jaw, brow, directional gaze and physical pupil diameter. Executable identities preserve the stated provider basis. General calibration ambiguity is unresolved. Original affine and lossy bilateral fixtures demonstrate the shared runtime without claiming visual equivalence.

## Generate and check

Python 3.11+ and the separately maintained `msf-tools` package are required. Install msf-tools at the commit recorded as `git_commit` in [tooling.lock.json](evidence/tooling.lock.json), from GitHub or from a local checkout, into the Python you use for RCEF:

```sh
python3 -m pip install "git+https://github.com/Kjakubzak/msf-tools@COMMIT"
# or: python3 -m pip install "git+file://$(cd ../msf-tools && pwd -P)@COMMIT"
```

Then regenerate the outputs:

```sh
python3 -B check.py --write
```

Review the generated diffs, then check existing outputs without writing and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

Run these commands from the RCEF checkout.

The 21 provider identities and 63 scalar comparisons preserve declared storage and provider-specific assumptions. FB2 direction tests activate one direction at a time. Raw pupil fields and native defaults do not establish physical measurement, calibrated neutral or cross-provider equivalence. Provider frame context and device/capture/physiology remain separate gates.

`check.py` uses the installed package. The lock records its commit, version and a SHA-256 for every installed package file. Before doing anything else, `check.py` verifies that the installed package was built from the locked commit (from its `direct_url.json`) and that every package file matches both its `RECORD` entry and the lock; on any difference it lists the problems and exits non-zero. The lock's `source` URL is informational: the commit and file hashes identify the package, so local `file://` installs are accepted. To adopt a reviewed new msf-tools version, install it and run `python3 -B check.py --update-lock`; the old lock is kept as [tooling.lock.previous.json](evidence/tooling.lock.previous.json). To roll back, copy that file over `tooling.lock.json` and install msf-tools at its commit. The wrapper delegates to `python3 -B -m msf_tools check AUTHORING --pack PATH --csv PATH [--write]`. No automatic cloning or source download occurs during checking.

Outputs are `generated/rcef.pack.json`, `rcef_mapping.csv`, `coverage.json`, and `SHA256SUMS`. JSON uses the shared sorted-key, indented stdlib encoding with UTF-8 and final LF, finite numbers and normalized negative zero. Arrays retain authoring order. CSV uses UTF-8, LF and minimal standard CSV quoting. All bytes are rendered and validated before each file is atomically replaced; several replacements are not one transaction.

## Architecture and TOML guide

See the [visual architecture report](docs/architecture.html), [Markdown guide](docs/architecture.md), [standalone diagram](docs/architecture.svg), and [TOML file index](docs/toml-index.csv). The guide explains discovery, validation, in-memory mapping, generated reports, and worked rule examples.

## Readable inventories and mappings

The checker also generates and checks [readable reports](reports/inventory.md):

- [Inventory Markdown](reports/inventory.md) and [CSV](reports/inventory.csv): every signal and profile membership, including excluded, unsupported and unresolved records. Native names, indices, ranges, calibration, evidence and reasons stay visible. Native defaults and calibrated neutral values remain separate.
- [Mapping Markdown](reports/mappings.md) and [CSV](reports/mappings.csv): every authored directional rule with its operator, status, assumptions and loss annotations.
- [Canonical correspondence Markdown](reports/canonical_correspondence.md) and [CSV](reports/canonical_correspondence.csv): a comparison table using authored rules only. A dash means no authored rule; unresolved relationships remain labeled. These tables do not establish cross-provider or anatomical equivalence.

These reports are derived from `generated/rcef.pack.json`; edit the authoritative TOML and run `check.py --write` to update them. `check.py` checks both shared outputs and readable reports. To check or regenerate only the presentation files with Python's standard library, use `python3 -B scripts/export_reports.py` or add `--write`. Each Markdown report binds the consumed pack bytes by SHA-256, and `reports/SHA256SUMS` binds all six presentation files. Existing `generated/SHA256SUMS` and generated mapping bytes retain their original contract. Publication uses atomic replacement per file and is not a transaction across all files. Report generation adds no third-party dependency; data and documentation retain their existing CC BY-SA 4.0 license and attribution.

See [survey](survey.md), [proposal](proposal.md), [references](references.md), [source evidence](evidence/sources.toml), [review](REVIEW.md), and [notices](THIRD_PARTY_NOTICES.md). `scripts/verify_sources.py` optionally checks exact public source digests and saves source bytes only to an explicit cache outside this repository. `scripts/audit_inventories.py --cache CACHE` then compares exact selected names, order and genuine enum indices against those verified bytes.

Read [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md) before extending or releasing the inventory.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Inherited source licenses and provenance are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Referenced provider documentation is not relicensed by RCEF.
