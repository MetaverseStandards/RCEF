# Calibration records

Each file here records one software-only calibration fit: how it was made, from what, and how well it held up on data it was not fitted to. A rule whose curve comes from a fit cites the record, and `check.py` refuses the checkout unless that rule's knots are exactly the record's frozen knots.

No record is published yet. The format is exercised by the test fixture [tests/fixtures/calibration/fixture.jaw-gain.cal](../tests/fixtures/calibration/fixture.jaw-gain.cal), whose numbers are invented.

## Status: software-only

Records are `calibrated_software`: fitted to renders of example rigs, with no people and no biometric data. Like `proposed`, this never means `verified_current`. `calibrated_measured` is reserved for physical capture and is refused for now. A software fit can say how a model or rig responds to renders; it says nothing about a real tracker's response to a real face (tracker gains, gaze angles, pupils, tongue, differences between people, latency, or what confidence values mean).

## Files

One record per fit, named `<id>.cal`. The content is TOML, but the file is not named `.toml`, because msf-tools reads every `.toml` file in the checkout as pack authoring. The record's `id` must equal the file name without `.cal`, and uses lowercase letters, digits, `.`, `_` and `-`.

## Fields

Every field is required, and no others are allowed. Dates, if any, are written as text, not as TOML dates.

| Field | Type | Meaning |
|---|---|---|
| `format` | text | `rcef.calibration/1` |
| `id` | text | the record's id, equal to the file name |
| `status` | text | `calibrated_software` |
| `method` | text | the fitting method, for example `landmark_monotone_fit` |
| `channels` | list of text | the signal ids the fit measured, distinct |
| `reference_rig` | text | the rig whose response is the reference |
| `inputs` | list of tables | every input asset: `name` and its `sha256` |
| `renderer` | table | `source_sha256` and `binary_sha256` of the renderer (see [tools/render](../tools/render/README.md)), and the `compiler`, `os` and `gpu` it ran with |
| `code_commit` | text | the full 40-character commit of the code that ran the fit |
| `training` | table | `conditions`, the number of training conditions (a positive integer), and a `description` of them |
| `held_out` | table | `seed_rule` = `rcef.calibration.seeds/1`, `count` of held-out seeds, and `frozen_sha256` (below) |
| `curves` | list of tables | the frozen curves: `input` (one of `channels`), `output`, and `knots` |
| `cells` | list of tables | per-cell results on the held-out seeds (below) |
| `licence` | text | the licence of the record's numbers |
| `limitations` | list of text | what the fit does not show, at least one statement |

All hashes are lowercase hex SHA-256.

**Knots** are `[input, output]` pairs: at least two, finite, with strictly increasing inputs, and monotone outputs (never rising after falling, or the reverse; a falling curve is allowed). Between knots the curve is linear, and it is not extrapolated past the end knots. This is the form RCEF expects the msf-tools `piecewise_linear` operator to take; until that operator exists no pack rule uses it.

**Cells** are one per channel, side, stimulus and identity: `channel` (one of `channels`), `side`, `stimulus`, `identity`, `conditions` (at least 20 jittered conditions), and three error measures, each a finite number at least 0: `median`, `p95` (not below the median) and `neutral` (the error at rest). Results are reported per cell: no pooling across cells, and a missed detection counts as a failure. A channel that misses its bounds ships a negative result and no rule.

## Frozen part and held-out seeds

Everything in a record except `cells` is frozen before the held-out evaluation. `frozen_sha256` is the SHA-256 of that part, without `frozen_sha256` itself, written as compact JSON with sorted keys (`json.dumps(part, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`, UTF-8). The held-out seeds come from it: seed *i*, for *i* from 0 to `count` − 1, is the first 8 bytes, read big-endian, of SHA-256 of the text `<frozen_sha256>:<i>`. So the seeds cannot be chosen after seeing the fit, and changing any frozen value, a knot for example, changes the hash; `check.py` refuses a record whose hash no longer matches. The metrics in `cells` are measured afterwards and are not part of the hash. `check.py`'s `held_out_seeds()` computes the seeds.

## Rules that cite a record

A rule cites a record with the evidence id `calibration.<id>`. Its operator must be `piecewise_linear` with `knots` exactly equal to those of the record's curve with the same input and output. `check.py` checks this for every rule in the checkout's authoring files, without msf-tools, after verifying the installed msf-tools and before running it.

## Limitations to state

Each record states its limitations. For example, ICT-FaceKit's identity modes are derived from light-stage scans of real people. They may be used as geometry for fits, on condition that every record using them says so in its limitations.
