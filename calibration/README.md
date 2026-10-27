# Calibration records

Each file here records one software-only calibration fit: how it was made, from what, the bounds it had to meet, and how it did on data it was not fitted to. A rule whose curve comes from a fit cites the record, and `check.py` refuses the checkout unless that rule's knots are exactly the record's frozen knots and every held-out cell for its channel passed.

No record is published yet. The format is exercised by the test fixtures in [tests/fixtures/calibration/](../tests/fixtures/calibration/), whose numbers are invented.

## Status: software-only

Records are `calibrated_software`: fitted to renders of example rigs, with no people and no biometric data. Like `proposed`, this never means `verified_current`. `calibrated_measured` is reserved for physical capture, designed but not run in [docs/calibration/physical-protocol.md](../docs/calibration/physical-protocol.md), and is refused for now. A software fit can say how a model or rig responds to renders; it says nothing about a real tracker's response to a real face (tracker gains, gaze angles, pupils, tongue, differences between people, latency, or what confidence values mean). Every record says so in its `scope` field.

## Files

- `<id>.cal`: one record per fit. The content is TOML, but the file is not named `.toml`, because msf-tools reads every `.toml` file in the checkout as pack authoring. The record's `id` must equal the file name without `.cal`, and uses lowercase letters, digits, `.`, `_` and `-`.
- `FREEZES`: the freeze ledger (below).

## Fields

Every field is required, except `scan_origin` where noted, and no others are allowed. Dates, if any, are written as text, not as TOML dates.

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
| `renderer` | table | `source_sha256` and `binary_sha256` of the renderer (see [tools/render](../tools/render/README.md)), and the `compiler`, `os` and `gpu` it ran with |
| `code_commit` | text | the full 40-character commit of the code that ran the fit |
| `training` | table | `conditions`, the number of training conditions (a positive integer), and a `description` of them |
| `held_out` | table | `seed_rule` = `rcef.calibration.seeds/1`, `count` of held-out seeds, and `frozen_sha256` (below) |
| `evaluation` | table | `min_conditions`, the fewest held-out conditions a cell may have (at least 20), and `bounds`: for each channel, the largest acceptable `median`, `p95` and `neutral` error |
| `curves` | list of tables | the frozen curves: `input` (one of `channels`), `output`, and `knots` |
| `cells` | list of tables | per-cell results on the held-out seeds (below) |
| `licence` | text | the licence of the record's numbers |
| `limitations` | list of text | what the fit does not show: at least one statement, each at least 5 words and 30 characters |

All hashes are lowercase hex SHA-256.

**Knots** are `[input, output]` pairs: at least two, finite, with strictly increasing inputs, and monotone outputs (never rising after falling, or the reverse; a falling curve is allowed). Between knots the curve is linear, and it is not extrapolated past the end knots. This is the form RCEF expects the msf-tools `piecewise_linear` operator to take; until that operator exists no pack rule uses it.

**Cells** are one per channel, side, stimulus and identity: `channel` (one of `channels`), `side`, `stimulus`, `identity`, `conditions`, `failures`, and three error measures, each a finite number at least 0: `median`, `p95` (not below the median) and `neutral` (the error at rest). A cell uses the first `conditions` held-out seeds, so `conditions` is at least `evaluation.min_conditions` and at most `held_out.count`. `failures` counts conditions where the expected response was not detected at all (at most `conditions`).

A cell **passes** if it has no failures and its median, p95 and neutral errors are each within the channel's frozen bounds. Results are per cell: no pooling across cells and no shifting to a best fit. A record whose cells fail is still a valid record, a published negative result; but no rule may cite it for a channel unless every cell for that channel passes.

## Frozen part, ledger and held-out seeds

Everything in a record except `cells` is the frozen part: method, inputs, renderer, curves, the bounds and the minimum conditions. `frozen_sha256` is the SHA-256 of that part, without `frozen_sha256` itself, written as compact JSON with sorted keys (`json.dumps(part, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`, UTF-8). The held-out seeds come from it: seed *i*, for *i* from 0 to `count` − 1, is the first 8 bytes, read big-endian, of SHA-256 of the text `<frozen_sha256>:<i>`. `check.py`'s `held_out_seeds()` computes them.

A record can recompute its own hash, so the hash alone does not stop anyone re-rolling the seeds by changing a frozen value. The freeze ledger does. `FREEZES` has one line per freeze:

```
<id> v<version> <frozen_sha256> <date YYYY-MM-DD> [reason]
```

Lines are only ever added at the end, so dates never go backwards. Versions of an id start at `v1` and go up by one; every version after the first carries a reason of at least three words. `check.py` refuses a record unless its `version` is the latest in the ledger for its id and its frozen hash is the one recorded there. So changing anything frozen, a knot or a bound for example, needs a new ledger line with a reason, which is visible in review.

What this guarantees: the ledger line for a freeze is committed before the results, and Git history shows that it came first and that it never changed afterwards. It does not prove that nobody looked at held-out data before freezing, and `check.py` cannot see Git history; the order is checked in review. The metrics in `cells` are deliberately not hashed and are not self-proving: they are trusted only because they can be reproduced. The record pins everything needed to do that: the code commit, the input asset hashes, the renderer's source and binary hashes with its OS and GPU, and the seeds.

## Rules that cite a record

A rule cites a record with the evidence id `calibration.<id>`. Its operator must be `piecewise_linear` with `knots` exactly equal to those of the record's curve with the same input and output, and every cell for its input channel must pass. `check.py` checks this for every rule in the checkout's authoring files, without msf-tools, after verifying the installed msf-tools and before running it.

## ICT-FaceKit identities

ICT-FaceKit's identity modes are derived from light-stage scans of real people. They may be used as geometry for fits, on condition that every record using them says so; `check.py` enforces this through `scan_origin`.
