<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Getting started

This page shows how to install the locked msf-character-tools and check an RCEF checkout. It also shows how to update the lock. The README section [Getting started](../README.md#getting-started) gives a short form.

## What you need

- Python 3.11 or newer.
- [msf-character-tools](https://github.com/MetaverseStandards/msf_character_tools), a separate project. RCEF locks msf-character-tools 0.6.0 in [tooling.lock.json](../evidence/tooling.lock.json).

## Find the wheel tag

The lock has one entry per release wheel. The key of each entry is the wheel's tag, and the entry holds the wheel's SHA-256. Find the tag for your platform and Python:

| Platform | Python 3.11 | Python 3.12 and later |
|---|---|---|
| macOS 11 or later, Apple silicon | `cp311-cp311-macosx_11_0_arm64` | `cp312-abi3-macosx_11_0_arm64` |
| Linux x86_64 (glibc 2.28 or later) | `cp311-cp311-manylinux_2_28_x86_64` | `cp312-abi3-manylinux_2_28_x86_64` |
| Linux aarch64 (glibc 2.28 or later) | `cp311-cp311-manylinux_2_28_aarch64` | `cp312-abi3-manylinux_2_28_aarch64` |

## Install the wheel by hash

Download the wheel for your tag from the [msf-character-tools v0.6.0 release](https://github.com/MetaverseStandards/msf_character_tools/releases/tag/v0.6.0). Then install it with the hash from the lock. Set `TAG` to your tag. Replace `PATH/TO/python` with the Python that you use for RCEF. Run the commands from the RCEF checkout:

```sh
TAG=cp312-abi3-macosx_11_0_arm64
WHEEL=msf_character_tools-0.6.0-$TAG.whl
DIR=$(mktemp -d)
curl -fsSL -o "$DIR/$WHEEL" "https://github.com/MetaverseStandards/msf_character_tools/releases/download/v0.6.0/$WHEEL"
SHA=$(python3 -c 'import json, sys; print(json.load(open("evidence/tooling.lock.json"))["wheels"][sys.argv[1]]["sha256"])' "$TAG")
echo "msf-character-tools @ file://$DIR/$WHEEL --hash=sha256:$SHA" > "$DIR/msf-character-tools.txt"
uv pip install --python PATH/TO/python --require-hashes -r "$DIR/msf-character-tools.txt"
```

When the release is public, the download needs no login or token. Without uv, `python3 -m pip install --require-hashes -r "$DIR/msf-character-tools.txt"` does the same.

## Build the wheels yourself

You can also build the wheels with msf-character-tools' `scripts/build_release.sh` at the locked commit. Its `docs/building.md` lists the pinned inputs that give the same bytes. `check.py` refuses any other build: every installed file must match the lock.

## Check the install

Run these commands from the RCEF checkout. The first command checks the outputs. The second command runs the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

If the install does not match the lock, `check.py` prints `Refusing to check` and exits 2. It does this before it reads any data.

## How checking works

`check.py` runs four steps in order. It stops at the first failure. [Section 2](architecture.md#2-what-checkpy-does) of the architecture guide describes each step.

1. The lock. It checks that the installed msf-character-tools is exactly a locked release wheel. If not, it exits 2 before it reads any data.
2. The calibration records. It checks the records in [calibration/](../calibration/README.md) and the mappings that cite them. This step does not use msf-character-tools.
3. The shared outputs. It runs msf-character-tools to make the files in `generated/`: `rcef.pack.json`, `rcef_mapping.csv`, `coverage.json` and `SHA256SUMS`. With `--write` it writes them. Without `--write` it checks that they have not changed.
4. The readable reports. It runs `scripts/export_reports.py` in the same way.

The lock records a SHA-256 for every file in the installed package, for each wheel tag. One lock is valid for several Python versions. The check never clones or downloads anything. [The msf-character-tools lock](architecture.md#the-msf-character-tools-lock) gives the full rules. It also tells you how to adopt a new release and how to return to the previous release.

[Section 7](architecture.md#7-generated-files-and-readable-reports) of the architecture guide gives the encoding of the outputs. [Section 8](architecture.md#8-edit-regenerate-check-and-qualify) says what the tests show and what they do not show.

## Run the local CI

GitHub Actions is not active for this repository. Run `sh scripts/ci_local.sh` instead. It runs `check.py` and the tests on Python 3.11 and 3.12. Paste its summary into the pull request. It needs a venv for each Python version, with the locked wheel installed. The comment at the top of the script gives the paths.

## Update the lock

1. Install the reviewed new release wheel by hash.
2. Run `python3 -B check.py --update-lock --wheel PATH/TO/WHEEL`.
3. Do step 2 once from each Python and platform whose wheel tag you support.
4. Run `check.py` and the tests again.
5. Update the version, the wheel table and the install commands on this page.
6. Update the msf-character-tools version in AGENTS.md and `docs/architecture.md`.
7. Add a CHANGELOG entry.

Commit these files together: `evidence/tooling.lock.json`, `evidence/tooling.lock.previous.json` (if the update made one), this page, AGENTS.md, `docs/architecture.md` and the CHANGELOG. [The msf-character-tools lock](architecture.md#the-msf-character-tools-lock) gives the full rules.
