# Calibration records

Each file here records one software-only calibration fit. It says how the fit was made and from what inputs. It also gives the bounds the fit had to meet and its results on data it was not fitted to. A mapping whose curve comes from a fit cites the record. `check.py` refuses the checkout unless that mapping's knots are exactly the record's frozen knots and every held-out cell for its channel passed.

Records:

- [mediapipe.ict-response](mediapipe.ict-response.cal): MediaPipe's response to untextured ICT renders. This is a negative result. 25 of MediaPipe's 51 ARKit-named scores rose enough in training to fit a curve. None of them met its bounds on held-out ICT identities or on Rocketbox Male, so no mapping cites the record. Made with [tools/calibration](../tools/calibration/README.md).
- [rig-gains.ict-rocketbox-female](rig-gains.ict-rocketbox-female.cal): rig intensity normalisation between two example rigs, ICT-FaceKit (the reference) and Rocketbox Female, for 51 ARKit shapes. 3 shapes pass (browInnerUp, cheekSquintLeft, cheekSquintRight). 48 fail, and they stay published as negative results. See [examples/README.md](../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name).

- [viseme-poses.rocketbox-female](viseme-poses.rocketbox-female.cal): the pose of each canonical viseme class in canonical expression signals, fitted to Rocketbox Female's 15 META viseme shapes in her own ARKit shapes, on mesh geometry only (no renderer), and held out on Rocketbox Male. 9 of 15 classes pass (`vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal`, `rhotic` and `sil`). 6 fail (`vowel_mid_spread`, `vowel_close_rounded`, `bilabial`, `labiodental`, `alveolar_sibilant` and `postalveolar`), and they stay published as negative results. The weighted sums of the [viseme pose bridge](../docs/canonical-set.md#viseme-pose-bridge) cite the record for the 9 classes that pass, and read no other class. Made with [tools/calibration](../tools/calibration/README.md#viseme-poses-meta-viseme-shapes-in-arkit-shapes-viseme_posespy).

The test fixtures in [tests/fixtures/calibration/](../tests/fixtures/calibration/) also use this format. Their numbers are invented.

## Status: software-only

Records are `calibrated_software`. They are fitted to renders or mesh geometry of example rigs, with no people and no biometric data. Like `proposed`, this never means `verified_current`. `calibrated_measured` is reserved for physical capture. [docs/calibration/physical-protocol.md](../docs/calibration/physical-protocol.md) designs that capture, but it has not been run, and `check.py` refuses `calibrated_measured` for now. A software fit can show how a model or rig responds to renders. It shows nothing about how a real tracker responds to a real face: tracker gains, gaze angles, pupils, tongue, differences between people, latency, or what confidence values mean. Every record says so in its `scope` field.

## Files

- `<id>.cal`: one record per fit. The content is TOML, but the file is not named `.toml`, because msf-character-tools reads every `.toml` file in the checkout as pack authoring. The record's `id` must be the file name without `.cal`. It uses only lowercase letters, digits, `.`, `_` and `-`.
- `FREEZES`: the freeze ledger (below).

## Fields

Every field is required, except `scan_origin` and `renderer` (see their rows) and `cells`. No other fields are allowed. A record without `cells` is a pre-registration: its frozen part and ledger line are committed before the held-out run, and the cells are added after it. No mapping may cite the record until then. Write any dates as text, not as TOML dates.

| Field | Type | Meaning |
|---|---|---|
| `format` | text | `rcef.calibration/1` |
| `id` | text | the record's id, equal to the file name |
| `version` | positive integer | which freeze of this id the record is (see the ledger) |
| `status` | text | `calibrated_software` |
| `scope` | text | exactly `software-only; not a measurement of any tracker` |
| `scan_origin` | text | required when the reference rig or any input is from ICT-FaceKit (its name contains `ICT` or `identityNNN`); must say the identities come from `light-stage scans of real people` |
| `method` | text | the fitting method, for example `landmark_monotone_fit` |
| `channels` | list of text | the signal ids the fit measured, distinct |
| `reference_rig` | text | the rig whose response is the reference |
| `inputs` | list of tables | every input asset: `name` and its `sha256` |
| `renderer` | table | `source_sha256` and `binary_sha256` of the renderer (see [tools/render](../tools/render/README.md)), and the `compiler`, `os` and `gpu` it ran with; required when the fit or its evaluation renders images, and left out when both use only mesh geometry |
| `code_commit` | text | the full 40-character commit of the code that ran the fit |
| `training` | table | `conditions`, the number of training conditions (a positive integer), and a `description` of them |
| `held_out` | table | `seed_rule` = `rcef.calibration.seeds/1`, `count` of held-out seeds, and `frozen_sha256` (below) |
| `evaluation` | table | `min_conditions`, the fewest held-out conditions a cell may have (at least 20), and `bounds`: for each channel, the largest acceptable `median`, `p95` and `neutral` error |
| `curves` | list of tables | the frozen curves: `input` (one of `channels`), `output`, and `knots` |
| `cells` | list of tables | per-cell results on the held-out seeds (below) |
| `licence` | text | the licence of the record's numbers |
| `limitations` | list of text | what the fit does not show: at least one statement, each at least 5 words and 30 characters |

All hashes are lowercase hex SHA-256.

**Knots** are `[input, output]` pairs. There must be at least two, all finite, with strictly increasing inputs and monotone outputs: the outputs never rise after falling, or fall after rising. A falling curve is allowed. Between knots the curve is linear, and it is not extrapolated past the end knots. This is the form of the msf-character-tools `piecewise_linear` operator (operators 1.1). In the pack, the 8 gaze splits in `arkit_gaze.to_fb2` use that operator; none of them cites a calibration record.

There is one **cell** per channel, side, stimulus and identity. A cell has `channel` (one of `channels`), `side`, `stimulus`, `identity`, `conditions`, `failures`, and three error measures. Each error measure is a finite number, at least 0: `median`, `p95` (not below the median) and `neutral` (the error at rest). A cell uses the first `conditions` held-out seeds, so `conditions` is at least `evaluation.min_conditions` and at most `held_out.count`. `failures` counts the conditions where the expected response was not detected at all. It is at most `conditions`.

A cell **passes** if it has no failures and its median, p95 and neutral errors are each within the channel's frozen bounds. Results are per cell. Cells are not pooled, and no cell is shifted to a best fit. A record whose cells fail is still a valid record: it is a published negative result. But no mapping may cite it for a channel unless every cell for that channel passes.

## Frozen part, ledger and held-out seeds

Everything in a record except `cells` is the frozen part: method, inputs, renderer (if any), curves, the bounds and the minimum conditions. `frozen_sha256` is the SHA-256 of that part, without `frozen_sha256` itself. The part is written as compact JSON with sorted keys (`json.dumps(part, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`, UTF-8). The held-out seeds come from this hash. Seed *i*, for *i* from 0 to `count` − 1, is the first 8 bytes, read big-endian, of the SHA-256 of the text `<frozen_sha256>:<i>`. `held_out_seeds()` in `check.py` computes them.

Anyone can recompute a record's hash. So the hash alone does not stop someone from changing a frozen value to get new seeds. The freeze ledger stops this. `FREEZES` has one line per freeze:

```
<id> v<version> <frozen_sha256> <date YYYY-MM-DD> [reason]
```

Lines are only added at the end, so dates never go backwards. Versions of an id start at `v1` and go up by one. Every version after the first has a reason of at least three words. `check.py` refuses a record unless its `version` is the latest one in the ledger for its id and its frozen hash is the one recorded there. So a change to anything frozen, for example a knot or a bound, needs a new ledger line with a reason. Reviewers can see that line.

The MediaPipe and rig-gains records are version 2. Version 1 was made before the Git history was rewritten for publication, and its commits are not in this repository. Version 2 of each record was fitted again with the code at `code_commit` `7cd8ff9`, msf-character-tools 0.5.0 (the locked release wheel) and a renderer built from `tools/render/meshrender.swift` at `7cd8ff9` (source SHA-256 `913c1641…`). Freeze commit `dd9ecd2` holds both frozen parts and their ledger lines. Results commit `2fa1be4` added the cells. [tools/calibration](../tools/calibration/README.md) tells how to run the held-out step again.

`viseme-poses.rocketbox-female` is version 1, with `code_commit` `d7e0f50` and msf-character-tools 0.5.0. Freeze commit `a0381b2` holds its frozen part and ledger line. Results commit `e43a0ca` added the cells.

What this guarantees: the ledger line for a freeze is committed before the results. Git history shows that the line came first and did not change after that. It does not prove that nobody looked at held-out data before the freeze. Also, `check.py` cannot see Git history, so reviewers check the order. The metrics in `cells` are not hashed, on purpose, and they do not prove themselves. They are trusted only because they can be reproduced. The record pins everything needed to reproduce them: the code commit, the input asset hashes, the renderer's source and binary hashes with its OS and GPU, and the seeds.

## Mappings that cite a record

A mapping cites a record with the evidence id `calibration.<id>`, and the pack holds an evidence record with that id that points to the file. Its operator must be `piecewise_linear` or `weighted_sum`.

- **`piecewise_linear`:** its `knots` must be exactly equal to the knots of the record's curve with the same input and output. Every cell for its input channel must pass.
- **`weighted_sum` (a pose sum):** the record's curves are poses, with knots `[[0, 0], [1, pose]]`: input channel *c* at weight 1 gives output *j* the value `pose`. Each input of the sum must be a copy (`affine` with scale 1 and offset 0) of one channel, made by one mapping. Exactly one `piecewise_linear` mapping reads the sum, the clamp, and its output is *j*. Each weight must be exactly the pose of the curve from its channel to *j*. Every cell of every channel that the sum reads must pass.

`check.py` checks this for every mapping in the checkout's authoring files. It does this without msf-character-tools, after it verifies the installed msf-character-tools and before it runs msf-character-tools.

A MediaPipe record that passes does not become a direct MediaPipe → ARKit map. It becomes a MediaPipe in-hop to the draft [canonical expression set](../docs/canonical-set.md#calibrated-mediapipe-records), `mediapipe_<group>.to_rcef`. The in-hop cites the record and the [definitions audit](../docs/canonical-set-audit.md#arkit) rows of the ARKit in-hop. `tools/calibration/k4_record.py` stays as it is until a record passes, although the `.rules` file it writes says that its rules can move to a direct `mappings/mediapipe_arkit.toml`. Then the tool changes under a new `code_commit`, and the record is frozen again with a new ledger line.

## ICT-FaceKit identities

ICT-FaceKit's identity modes come from light-stage scans of real people. Fits may use them as geometry, but every record that uses them must say so. `check.py` checks this through `scan_origin`.
