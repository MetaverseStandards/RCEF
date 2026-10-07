# RCEF: expression inventory and authoring parity

RCEF records public expression interfaces, their calibration limits, and explicit directional scalar rules. TOML is the authoritative data. Names are inventoried as attributed facts; definitions and examples are original.

## Contents

Selected inventories: ARKit 52, MediaPipe 52, OpenXR FB 63 and FB2 70, optional META visemes 15, VRCFT transport 88, raw/combined eye data, artist 102+42, publicly listed numeric avatar parameters 124 and activity flags 3, Godot 102+41, VRM 18, and Roblox 50. Ancillary enums, sentinels and encoding surfaces remain visible. These counts describe interfaces, not tracking fidelity.

The canonical subset has 21 explicitly provider-calibrated scalar projections spanning blink, jaw, brow, directional gaze and physical pupil diameter. Executable identities preserve the stated provider basis. General calibration ambiguity is unresolved. Original affine and lossy bilateral fixtures demonstrate the shared runtime without claiming visual equivalence.

## Generate and check

Python 3.11+ and `msf_tools` are required. Install the separately maintained shared tools, or supply an explicit local checkout:

```sh
python3 -B check.py --tools-path ../msf-tools --write
python3 -B check.py --tools-path ../msf-tools
python3 -B tests/test_parity.py --tools-path ../msf-tools
```

The tested immutable dependency commit and source fingerprints are in [tooling.lock.json](evidence/tooling.lock.json). Check out that commit before using a local tools path. Without `--tools-path`, the installed package is used. The wrapper delegates to `python3 -B -m msf_tools check AUTHORING --pack PATH --csv PATH [--write]`. No automatic cloning or source download occurs during checking.

Outputs are `generated/rcef.pack.json`, `rcef_mapping.csv`, `coverage.json`, and `SHA256SUMS`. JSON uses the shared sorted-key, indented stdlib encoding with UTF-8 and final LF, finite numbers and normalized negative zero. Arrays retain authoring order. CSV uses UTF-8, LF and minimal standard CSV quoting. All bytes are rendered and validated before each file is atomically replaced; several replacements are not one transaction.

See [survey](survey.md), [proposal](proposal.md), [references](references.md), [source evidence](evidence/sources.toml), [review](REVIEW.md), and [notices](THIRD_PARTY_NOTICES.md). `scripts/verify_sources.py` optionally checks exact public source digests and saves source bytes only to an explicit cache outside this repository. `scripts/audit_inventories.py --cache CACHE` then compares exact selected names, order and genuine enum indices against those verified bytes.

Read [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md) before extending or releasing the inventory.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Inherited source licenses and provenance are retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Referenced provider documentation is not relicensed by RCEF.
