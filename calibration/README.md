# Calibration records

Each file here records one software-only calibration fit. It says how the fit was made and from what inputs. It also gives the bounds the fit had to meet and its results on data it was not fitted to. A mapping whose curve comes from a fit cites the record. `check.py` refuses the checkout unless that mapping's knots are exactly the record's frozen knots and every held-out cell for its channel passed.

Records:

- [mediapipe.ict-response](mediapipe.ict-response.cal): MediaPipe's response to untextured ICT renders. This is a negative result. 25 of MediaPipe's 51 ARKit-named scores rose enough in training to fit a curve. None of them met its bounds on held-out ICT identities or on Rocketbox Male, so no mapping cites the record. Made with [tools/calibration](../tools/calibration/README.md).
- [rig-gains.ict-rocketbox-female](rig-gains.ict-rocketbox-female.cal): rig intensity normalisation between two example rigs, ICT-FaceKit (the reference) and Rocketbox Female, for 51 ARKit shapes. 3 shapes pass (browInnerUp, cheekSquintLeft, cheekSquintRight). 48 fail, and they stay published as negative results. See [examples/README.md](../examples/README.md#6-rig-gains-how-strongly-two-rigs-render-the-same-arkit-name).

- [viseme-poses.rocketbox-female](viseme-poses.rocketbox-female.cal): the pose of each canonical viseme class in canonical expression signals, fitted to Rocketbox Female's 15 META viseme shapes in her own ARKit shapes, on mesh geometry only (no renderer), and held out on Rocketbox Male. 9 of 15 classes pass: `vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `coronal_stop`, `coronal_nasal_lateral`, `dorsal`, `rhotic` and `sil`. History: `viseme-poses.rocketbox-features` replaces it, and no mapping cites it.
- [viseme-poses.rocketbox-multi](viseme-poses.rocketbox-multi.cal): the pose of each canonical viseme class, fitted to the META viseme shapes of 10 Rocketbox rigs at once, on mesh geometry only. Version 1 (Left and Right weights apart; held out on Female_Adult_04, Female_Adult_13, Male_Adult_05 and Male_Adult_11) passed 9 of 15 classes, but its poses moved the two sides differently by up to 0.56, while its limitations called the difference slight; it is in the Git history (results commit `f166568`). Version 2, in the checkout, ties each Left and Right pair and is held out on 4 fresh rigs (Female_Adult_06, Female_Adult_17, Male_Adult_02 and Male_Adult_19): 7 of 15 classes pass (`vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `coronal_stop`, `dorsal` and `sil`). [tools/calibration/results/viseme_lips.json](../tools/calibration/results/viseme_lips.json) has report-only lip measures of version 2 for PP, FF and OU. History: `viseme-poses.rocketbox-features` replaces it, and no mapping cites it.
- [viseme-poses.rocketbox-features](viseme-poses.rocketbox-features.cal): the pose of each canonical viseme class, fitted to 18 Rocketbox rigs with each Left and Right pair tied, with a [perceptual gate](#perceptual-gate) for `bilabial`, `vowel_close_rounded`, `vowel_mid_spread` and `alveolar_sibilant`: visible mouth features, each with a frozen tolerance. Held out on 4 fresh rigs (Female_Adult_09, Female_Adult_15, Male_Adult_08 and Male_Adult_15) from round 3 of the rule in `viseme_rigs.json`. 11 of 15 classes pass: 7 by their shape cells (`vowel_open`, `vowel_close_spread`, `vowel_mid_rounded`, `dental`, `coronal_stop`, `dorsal` and `sil`) and 4 by every feature cell (`bilabial`, `vowel_close_rounded`, `vowel_mid_spread` and `alveolar_sibilant`). `labiodental`, `postalveolar`, `coronal_nasal_lateral` and `rhotic` fail, and they stay published as negative results. **Pass rule and use, decided before the held-out run:** a class passes if its shape cells pass on every held-out rig, or if every one of its feature cells passes on every held-out rig. The [viseme pose bridge](../docs/canonical-set.md#viseme-pose-bridge) is written from this record alone and reads exactly the classes that pass, replacing `viseme-poses.rocketbox-multi` and `viseme-poses.rocketbox-female` for every class. Made with [tools/calibration](../tools/calibration/README.md#viseme-poses-meta-viseme-shapes-in-arkit-shapes-viseme_posespy).

The test fixtures in [tests/fixtures/calibration/](../tests/fixtures/calibration/) also use this format. Their numbers are invented.

## Status: software-only

Records are `calibrated_software`. They are fitted to renders or mesh geometry of example rigs, with no people and no biometric data. Like `proposed`, this never means `verified_current`. The pack's evidence record for a record, `calibration.<id>`, is still `verified_current`, as every record in `evidence/sources.toml` is: that status says only that the cited source is what the record claims, here the committed `.cal` file at its frozen hash. The mappings that cite it stay `proposed` (see [AGENTS.md](../AGENTS.md#evidence-status)). `calibrated_measured` is reserved for physical capture. [docs/calibration/physical-protocol.md](../docs/calibration/physical-protocol.md) designs that capture, but it has not been run, and `check.py` refuses `calibrated_measured` for now. A software fit can show how a model or rig responds to renders. It shows nothing about how a real tracker responds to a real face: tracker gains, gaze angles, pupils, tongue, differences between people, latency, or what confidence values mean. Every record says so in its `scope` field.

## Files

- `<id>.cal`: one record per fit. The content is TOML, but the file is not named `.toml`, because msf-character-tools reads every `.toml` file in the checkout as pack authoring. The record's `id` must be the file name without `.cal`. It uses only lowercase letters, digits, `.`, `_` and `-`.
- `FREEZES`: the freeze ledger (below).

## Fields

Every field is required, except `scan_origin` and `renderer` (see their rows), `cells`, and `features` and `feature_cells`. No other fields are allowed. A record without `cells` is a pre-registration: its frozen part and ledger line are committed before the held-out run, and the cells are added after it. No mapping may cite the record until then. Write any dates as text, not as TOML dates.

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
| `features` | list of tables | optional, frozen: the perceptual gate (below) |
| `feature_cells` | list of tables | optional: per-feature results on the held-out seeds (below) |
| `licence` | text | the licence of the record's numbers |
| `limitations` | list of text | what the fit does not show: at least one statement, each at least 5 words and 30 characters |

All hashes are lowercase hex SHA-256.

**Knots** are `[input, output]` pairs. There must be at least two, all finite, with strictly increasing inputs and monotone outputs: the outputs never rise after falling, or fall after rising. A falling curve is allowed. Between knots the curve is linear, and it is not extrapolated past the end knots. This is the form of the msf-character-tools `piecewise_linear` operator (operators 1.1). In the pack, the 8 gaze splits in `rcef_expression.to_fb2`, the clamp in `visemes.to_rcef_viseme` and the 45 clamps of the viseme pose bridge use that operator. None of them cites a calibration record; the bridge's weighted sums do.

There is one **cell** per channel, side, stimulus and identity. A cell has `channel` (one of `channels`), `side`, `stimulus`, `identity`, `conditions`, `failures`, and three error measures. Each error measure is a finite number, at least 0: `median`, `p95` (not below the median) and `neutral` (the error at rest). A cell uses the first `conditions` held-out seeds, so `conditions` is at least `evaluation.min_conditions` and at most `held_out.count`. `failures` counts the conditions where the expected response was not detected at all. It is at most `conditions`.

A cell **passes** if it has no failures and its median, p95 and neutral errors are each within the channel's frozen bounds. Results are per cell. Cells are not pooled, and no cell is shifted to a best fit. A record whose cells fail is still a valid record: it is a published negative result. But no mapping may cite it for a channel unless every cell for that channel passes.

## Perceptual gate

A record may also give some channels a perceptual gate: a few visible features, each with a frozen tolerance. The gate checks named features of the face, such as how far the lips are apart on the mid line, not the whole-mesh shape. A channel then passes if every one of its shape cells passes, **or** if every one of its features has a passing feature cell for every held-out identity of its shape cells.

Each entry of `features` has `channel` (one of `channels`), `feature` (a name; each channel and feature appear once), `kind`, `units`, `tolerance` (a finite number, at least 0) and a `description`. There are two kinds:

- `difference`: the error of a condition is the absolute difference between the feature of the reconstruction and the feature of the target.
- `range`: the entry also has `low` and `high` (`low` below `high`), and the error of a condition is how far the feature of the reconstruction lies outside them (0 inside).

Every channel that has features must also have the guard `whole_face_error`: a `range` feature with `low` 0 whose `high` plus `tolerance` is at most 1. Its value is the condition's shape error, as in the shape cells. So a channel cannot pass by its features while its reconstruction is further from the target than the neutral face is.

A feature cell has `channel`, `feature` (one of the features), `identity`, `conditions` (at least `evaluation.min_conditions`, at most `held_out.count`), `failures`, and the `median`, `p95` and `max` of the errors (finite, at least 0, in that order or equal). A feature cell passes if it has no failures and its `max` is within the feature's `tolerance`: every condition must pass, not only most. `features` are part of the frozen part; `feature_cells` are results, like `cells`, and are not hashed. A record with `feature_cells` must have `cells` too: both come from one held-out run.

## Frozen part, ledger and held-out seeds

Everything in a record except `cells` and `feature_cells` is the frozen part: method, inputs, renderer (if any), curves, features, the bounds and the minimum conditions. `frozen_sha256` is the SHA-256 of that part, without `frozen_sha256` itself. The part is written as compact JSON with sorted keys (`json.dumps(part, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`, UTF-8). The held-out seeds come from this hash. Seed *i*, for *i* from 0 to `count` − 1, is the first 8 bytes, read big-endian, of the SHA-256 of the text `<frozen_sha256>:<i>`. `held_out_seeds()` in `check.py` computes them.

Anyone can recompute a record's hash. So the hash alone does not stop someone from changing a frozen value to get new seeds. The freeze ledger stops this. `FREEZES` has one line per freeze:

```
<id> v<version> <frozen_sha256> <date YYYY-MM-DD> [reason]
```

A new version of an id refits the same thing from the same kind of inputs, for example after a history rewrite. A fit to a different training set gets a new id. A re-fit also gets a new id while a mapping cites the current version: `check.py` compares the mapping's weights with the frozen poses of the latest version, so a new version would make it refuse the mapping until the mapping is rewritten. Lines are only added at the end, so dates never go backwards. Versions of an id start at `v1` and go up by one. Every version after the first has a reason of at least three words. `check.py` refuses a record unless its `version` is the latest one in the ledger for its id and its frozen hash is the one recorded there. So a change to anything frozen, for example a knot or a bound, needs a new ledger line with a reason. Reviewers can see that line.

The MediaPipe and rig-gains records are version 2. Version 1 was made before the Git history was rewritten for publication, and its commits are not in this repository. Version 2 of each record was fitted again with the code at `code_commit` `7cd8ff9`, msf-character-tools 0.5.0 (the locked release wheel) and a renderer built from `tools/render/meshrender.swift` at `7cd8ff9` (source SHA-256 `913c1641…`). Freeze commit `dd9ecd2` holds both frozen parts and their ledger lines. Results commit `2fa1be4` added the cells. [tools/calibration](../tools/calibration/README.md) tells how to run the held-out step again.

`viseme-poses.rocketbox-female` is version 1, with `code_commit` `703ee7c` and msf-character-tools 0.5.0. Freeze commit `605c4f9` holds its frozen part and ledger line. Results commit `ba58c88` added the cells. To reproduce them, check out `605c4f9` (`check.py` changed afterwards) and run `python tools/calibration/viseme_poses.py heldout --rig-cache DIR` there; it refuses unless the code is as at `code_commit` and the inputs have the pinned SHA-256. The neutral bound of this record cannot fail (at weight 0 the bridged weights are 0), and `sil` passes trivially, because neither rig's SIL shape moves the face: so 8 of the 14 speech classes pass.

`viseme-poses.rocketbox-multi` is version 1, with `code_commit` `6624079` (the code is as at `0d3ee83`) and msf-character-tools 0.5.0. It is a new id, not version 2 of `viseme-poses.rocketbox-female`, because its training set is different. The rig sets were committed at `1387500` and the rig files pinned at `73f266f`, before any new rig was loaded. Freeze commit `6417863` holds its frozen part, its ledger line and the rule for its use. Results commit `f166568` added the cells: one per class and held-out rig, 60 in all. To reproduce them, check out `6417863` and run `python tools/calibration/viseme_poses.py heldout --rig-cache DIR` there.

`viseme-poses.rocketbox-multi` version 2 has `code_commit` `836d826` (the code is as at `1f77cdd`). The extended rig rule was committed at `78d0819` and the new rigs pinned at `aff11cf`. Freeze commit `61660f1` holds its frozen part and its ledger line with the reason. Results commit `7873008` added the cells. `check.py` refuses the bridge's sums in `61660f1`, `7873008` and `9acf65d` (the report-only lip measures), because the bridge still cited the poses of version 1 until it was rewritten in `211e19d`. When bisecting, skip them: `git bisect skip 61660f1 7873008 9acf65d`. To reproduce the cells, check out `61660f1` and run the `heldout` step there.

`viseme-poses.rocketbox-features` is version 1, with `code_commit` `ea7a8bd` (the code is as at `333d928`; `check.py` learnt the perceptual gate at `d0833b0`). Round 3 of the rig rule was committed at `8cf1ecd` and its rigs pinned at `f3655c3`. Freeze commit `4a5768c` holds its frozen part, its ledger line, the pass rule and the use rule. Results commit `43a5735` added the cells and the feature cells. To reproduce them, check out `4a5768c` and run `python tools/calibration/viseme_poses.py heldout --rig-cache DIR` there. A second run from that commit gave the same record, byte for byte.

What this guarantees: the ledger line for a freeze is committed before the results. Git history shows that the line came first and did not change after that. It does not prove that nobody looked at held-out data before the freeze. For the viseme pose records, the held-out rigs were loaded before each freeze only to count their shapes, as the replacement clause of the rig rule needs. Also, `check.py` cannot see Git history, so reviewers check the order. The metrics in `cells` are not hashed, on purpose, and they do not prove themselves. They are trusted only because they can be reproduced. The record pins everything needed to reproduce them: the code commit, the input asset hashes, the renderer's source and binary hashes with its OS and GPU, and the seeds.

## Mappings that cite a record

A mapping cites a record with the evidence id `calibration.<id>`, and the pack holds an evidence record with that id that points to the file. Its operator must be `piecewise_linear` or `weighted_sum`.

- **`piecewise_linear`:** its `knots` must be exactly equal to the knots of the record's curve with the same input and output. Its input channel must pass: every cell, or, if the record gives it features, every feature cell.
- **`weighted_sum` (a pose sum):** the record's curves are poses, with knots `[[0, 0], [1, pose]]`: input channel *c* at weight 1 gives output *j* the value `pose`. Each input of the sum must be a copy (`affine` with scale 1 and offset 0) of one channel, made by one mapping, and have one weight. Exactly one mapping reads the sum: the clamp, a `piecewise_linear` mapping with the sum as its only input, the knots `[[0, 0], [1, 1], [n, 1]]` for *n* inputs (`[[0, 0], [1, 1]]` for one) and the output *j*. Each weight must be exactly the pose of the curve from its channel to *j*. Every channel that the sum reads must pass: all its cells, or, if the record gives it features, all its feature cells.

`check.py` checks this for every mapping in the checkout's authoring files. It does this without msf-character-tools, after it verifies the installed msf-character-tools and before it runs msf-character-tools.

A MediaPipe record that passes does not become a direct MediaPipe → ARKit map. It becomes part of a MediaPipe in-map to the draft [canonical expression set](../docs/canonical-set.md#calibrated-mediapipe-records), `mediapipe.to_rcef_expression`. The in-map cites the record and the [definitions audit](../docs/canonical-set-audit.md#arkit) rows of the ARKit in-map. `tools/calibration/k4_record.py` stays as it is until a record passes, although the `.rules` file it writes says that its rules can move to a direct `mappings/mediapipe_arkit.toml`. Then the tool changes under a new `code_commit`, and the record is frozen again with a new ledger line.

## ICT-FaceKit identities

ICT-FaceKit's identity modes come from light-stage scans of real people. Fits may use them as geometry, but every record that uses them must say so. `check.py` checks this through `scan_origin`.
