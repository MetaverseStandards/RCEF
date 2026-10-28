# RCEF: expression inventory and authoring parity

RCEF records public expression interfaces, their calibration limits, and explicit one-way scalar mappings between them. The TOML files are the authoritative data. RCEF records provider names as facts, with attribution. Its definitions and examples are original.

## Contents

RCEF has these selected inventories: ARKit 52, MediaPipe 52, OpenXR FB 63 and FB2 70, optional META visemes 15, VRCFT transport 88, raw/combined eye data, artist 102+42, publicly listed numeric avatar parameters 124 and activity flags 3, Godot 102+41, VRM 18, and Roblox 50. It also records ancillary enums, sentinels and encoding surfaces. These counts describe interfaces. They do not say how well anything tracks a face.

The canonical subset has 21 scalar projections, and each one states its provider's calibration. They cover blink, jaw, brow, directional gaze and physical pupil diameter. The identity mappings keep the stated provider basis. In general, how one provider's calibration relates to another's is still unresolved. Two original fixtures, one affine and one lossy bilateral, show the shared runtime. They do not claim visual equivalence.

Data 0.4.0 has 187 cross-provider mappings. They translate:

- FB2 to all 52 ARKit coefficients, and back (face and, separately, gaze);
- ARKit to VRCFaceTracking Unified Expressions;
- FB2 eye closure to VRM per-eye blinks;
- META visemes to VRM lip-sync presets.

The ARKit → FB2 gaze map also has 4 internal steps. Each step takes one eye's two opposing ARKit gaze directions (in and out, or up and down) to one intermediate difference. All of these mappings are proposed and approximate. They compile only with the approximation opt-in, and each one states its calibration assumptions and losses (see the [CHANGELOG](CHANGELOG.md)). Their tests compare results with expected values that `scripts/derive_fb2_goldens.py` derives from the pinned public sources, not from RCEF's own mappings.

## Expression sets and where they come from

The Mappings table shows what translates to what. The Expression sets table shows where each set comes from. Each file in `profiles/` records one public expression set, except `fixture.toml`, which holds RCEF's own synthetic fixtures. The documentation link is the usual web page for the set. The pinned source is the exact revision or retrieval that RCEF verified. [references.md](references.md) and [evidence/sources.toml](evidence/sources.toml) list it with its SHA-256. At least one executable mapping reads a **source** set, and at least one writes a **target** set. An **inventory only** set is recorded but not translated yet.

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

[docs/expression-sets.md](docs/expression-sets.md) lists every profile file: its expression set and revision, signal count, role in maps, documentation, pinned source, and license or terms. It also explains the signal counts and describes RCEF's own canonical and intermediate sets.

## Generate and check

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

You can build the wheels yourself with msf-character-tools' `scripts/build_release.sh` at the locked commit; its `docs/building.md` lists the pinned inputs that give the same bytes. `check.py` refuses any other build: every installed file must match the lock.

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

The 21 provider identities and 63 scalar comparisons keep the declared storage and the provider-specific assumptions. The FB2 direction tests move one direction at a time. Raw pupil fields and native defaults do not show a physical measurement, a calibrated neutral or cross-provider equivalence. Provider frame context, devices, capture and physiology are separate gates.

`check.py` uses the installed package. The lock (format 2) records msf-character-tools' commit and version. It also has one entry per wheel tag. Each entry has that wheel's SHA-256, when known, and a SHA-256 for every installed file in the `msf_character_tools` package, not only the Python files. One lock serves several Pythons: `check.py` checks each install against the entry for its own tag, which it reads from the install's `WHEEL` file. Before it does anything else, `check.py` verifies that the installed package was built from the locked commit. It reads the commit from `msf_character_tools/_build_info.json`, or, if that file is missing, from a Git install's `direct_url.json`. If both name a commit and they differ, it refuses. It also verifies that the install's tag has an entry, and that every file in the package directory, of any type, matches both its `RECORD` entry and the lock. Bytecode caches are ignored. If anything differs, it lists the problems and exits non-zero. It compares the wheel hash after installation only if the installer recorded it. uv does not record it, so for uv installs `--require-hashes` checks the hash at install time. The lock's `source` URL is for information only. The commit and file hashes identify the package, so `check.py` accepts local `file://` installs. To adopt a reviewed new msf-character-tools version, install it and run `python3 -B check.py --update-lock`. Add `--wheel PATH` to record the sha256 of the wheel file you installed; `check.py` first confirms that the wheel holds the installed files. Run the command once from each Python whose tag you support. Entries for the same commit and version are merged. When the commit or version changes, the old lock is kept as `evidence/tooling.lock.previous.json`. msf-character-tools 0.5.0 is the first release from the public repository, so this checkout has no previous lock yet. To roll back, copy that file over `tooling.lock.json`, install msf-character-tools at its commit, and use the `check.py` from the same RCEF commit as that lock. The wrapper calls `python3 -B -m msf_character_tools check AUTHORING --pack PATH --csv PATH [--write]`. Checking never clones or downloads anything.

After it verifies msf-character-tools and before it runs msf-character-tools, `check.py` also checks the software-only calibration records in [calibration/](calibration/README.md). It refuses a mapping that cites a record unless the mapping's knots are exactly the record's frozen knots and every held-out cell for its channel passed. The renderer for those fits is in [tools/render/](tools/render/README.md).

The outputs are `generated/rcef.pack.json`, `rcef_mapping.csv`, `coverage.json`, and `SHA256SUMS`. JSON uses the shared stdlib encoding: sorted keys, indented, UTF-8 with a final LF, finite numbers and normalized negative zero. Arrays keep the authoring order. CSV uses UTF-8, LF and minimal standard CSV quoting. All bytes are rendered and validated before any file is replaced. Each file is replaced atomically, but the replacements together are not one transaction.

## Examples

[examples/README.md](examples/README.md) uses RCEF from start to end with the msf-character-tools public API. It translates FB2 frames to ARKit weights, and META visemes to VRM presets, from CSV. It then drives two Microsoft Rocketbox faces and the ICT-FaceKit face with a FACS-based expression library, both directly and through RCEF's mappings, and reports the residuals. It also renders a short spoken phrase as visemes on Rocketbox and on a VRM model.

## Architecture and TOML guide

The [Markdown guide](docs/architecture.md) explains what `check.py` does, how TOML is discovered and validated, how maps compile and run in memory, the generated reports, and worked examples of each operator. The [visual architecture report](docs/architecture.html), [standalone diagram](docs/architecture.svg) and [TOML file index](docs/toml-index.csv) describe the same data 0.4.0 tree as the guide.

## Readable inventories and mappings

The checker also generates and checks [readable reports](reports/inventory.md):

- [Inventory Markdown](reports/inventory.md) and [CSV](reports/inventory.csv): every signal and profile membership, including excluded, unsupported and unresolved records. They show native names, indices, ranges, calibration, evidence and reasons. Native defaults and calibrated neutral values are kept separate.
- [Mapping Markdown](reports/mappings.md) and [CSV](reports/mappings.csv): every authored one-way mapping with its operator, status, assumptions and loss annotations.
- [Canonical correspondence Markdown](reports/canonical_correspondence.md) and [CSV](reports/canonical_correspondence.csv): a comparison table that uses only authored mappings. A dash means no authored mapping. Unresolved relationships stay labeled. These tables do not show cross-provider or anatomical equivalence.

These reports come from `generated/rcef.pack.json`. To update them, edit the authoritative TOML and run `check.py --write`. `check.py` checks both the shared outputs and the readable reports. To check only the presentation files with Python's standard library, use `python3 -B scripts/export_reports.py`; add `--write` to regenerate them. Each Markdown report records the SHA-256 of the pack bytes it read, and `reports/SHA256SUMS` records the hashes of all six presentation files. `generated/SHA256SUMS` and the generated mapping bytes keep their original contract. Each file is replaced atomically, but the replacements are not one transaction across all files. Report generation adds no third-party dependency. Data and documentation keep their CC BY-SA 4.0 license and attribution.

See [survey](survey.md), [proposal](proposal.md), [references](references.md), [source evidence](evidence/sources.toml), [review](REVIEW.md), and [notices](THIRD_PARTY_NOTICES.md). `scripts/verify_sources.py` is optional. It checks the exact digests of the public sources, and it saves source bytes only to a cache that you name, outside this repository. `scripts/audit_inventories.py --cache CACHE` then compares the selected names, their order and the real enum indices with those verified bytes.

Read [CONTRIBUTING](CONTRIBUTING.md) and [GOVERNANCE](GOVERNANCE.md) before extending or releasing the inventory.

Coding agents: read [AGENTS.md](AGENTS.md) first.

## Licenses

Original code: [MIT](LICENSES/MIT.txt). Original data, documentation and fixtures: [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt), attribution to RCEF contributors (2026). Copyright (c) 2026 Metaverse Standards Forum. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) keeps the inherited source licenses and provenance. RCEF does not relicense the provider documentation it refers to.
