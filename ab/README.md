<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# A/B comparison of the pivot route with the direct maps

The pivot route (arm B) translates every pair of expression sets through RCEF's canonical sets: source → canonical → target. This folder holds the pre-registered comparison of B with today's direct maps (arm A1) and with the other arms. Each run is registered before it starts, and its thresholds and frozen lists never change inside a registration.

The tools are in the repository, not in this folder:

| File | What it does |
|---|---|
| [examples/rcef_route.py](../examples/rcef_route.py) | `Route`: runs B, and runs A1 in its one-hop mode. `tests/test_route_runner.py` anchors the one-hop mode to `rcef_translate.Translator`. |
| [scripts/ab_frames.py](../scripts/ab_frames.py) | Makes the input frames from a registration only. It never reads the live pack. |
| [scripts/ab_compare.py](../scripts/ab_compare.py) | Writes a registration draft, checks the pins, runs every arm and writes the results. It also checks this folder. |
| [tests/ab_oracle.py](../tests/ab_oracle.py) | The oracle (O): a pure-Python copy of how msf-character-tools evaluates a map. It gives B's expected values and refusal codes. |
| [tests/ab_a3.py](../tests/ab_a3.py) | Arm A3: the expression library's AU → FB2 table, frozen at dea1713 in `tests/fixtures/a3-dea1713/`. |
| [examples/facs_codec.py](../examples/facs_codec.py) | Reads FACS notation into `facs.code` values, for B's FACS input. Its table is `examples/data/facs_codes.json`. |

## Arms

- **A1:** the pack at dea1713, committed as `tests/fixtures/baseline-dea1713.pack.json` (SHA-256 `630d37a5b01e4983f8e5cbcbd54d8268abeffb09248ea793d4842bd2df5cd4f7`). `ab_compare.py` checks the hash, and also checks the file against Git when the history is there. A1 always comes from this file, never from the live pack.
- **A2:** two direct maps in turn, only where no direct map exists: FB2 → ARKit → VRCFT UE, and ARKit → FB2 → VRM blink.
- **A3:** the expression library's AU table, for FACS → FB2. **A3 then A1** gives FACS → ARKit.
- **B:** `Route` on the B pack.
- **O:** the oracle, on B's maps.

## Files in this folder

- `FREEZES`: the ledger (below).
- `<id>-v<N>.abreg`: one registration per freeze, for example `ab.pivot-v1.abreg`. It is JSON, not TOML, because msf-character-tools reads every `.toml` file in the checkout as pack authoring.
- `results/v<N>/` (for `ab.pivot`) or `results/<id>-v<N>/` (for a new A/B): the results of one registered run.

## The ledger

`FREEZES` uses the line format of `calibration/FREEZES`:

```
<id> v<N> <abreg_sha256> <YYYY-MM-DD> [reason]
```

- `abreg_sha256` is the SHA-256 of the registration's compact, key-sorted JSON, so it does not depend on the file's layout.
- Versions of an id start at v1 and go up by one. Dates never go back. Every version after v1 needs a reason of at least three words.
- Every registration that is ever committed gets a line, abandoned ones included, so a registration that is made again is still visible. A registration file is never removed.
- Lines are only added at the end.

`check.read_ledger` reads the file, and `tests/test_ab_registration.py` checks it with the rules of this page (`python3 -B scripts/ab_compare.py check` prints the same problems).

## Freeze kinds

A registration's `kind` is one of five:

| Kind | When | Seeds |
|---|---|---|
| `first` | `ab.pivot` v1. | A new `seed_root`. |
| `fix` | After a failing run: B, the oracle, the generator, the codec, the A3 harness, `Route` or `ab_compare.py` changes. The registration says what changed. Thresholds stay. | A new `seed_root` from its own registration. The families of every earlier freeze become regression families, labelled "seen before the change". |
| `revise` | After a passing run: B changes but keeps every value, for example a rename or new definition text. The registration lists each change, and the project's release owners accept the list before the run. Every B value must be bit-identical to the revised freeze's results. A rename carries a frozen old → new ID map. | A new `seed_root`; earlier families become regression families. |
| `reproduce` | The re-run of an unchanged B, after the direct maps are retired. It reproduces the latest passing `first`, `fix` or `revise` freeze. | It copies that freeze's `seed_root`, generator hash, channel lists and runtime pins. |
| `new` | A new A/B, with a new id such as `ab.pivot2`: when A1 itself changes, or when an intended value difference is accepted. Its v1 sets its own thresholds. | A new `seed_root`. |

Thresholds never change inside an id. A frozen list that changes from one version to the next needs the project's release owners' acceptance, written in the registration's `acceptance` table under the list's name.

## The seed rule

- For a `first`, `new`, `fix` or `revise` freeze, `seed_root` is the SHA-256 of the registration's compact, key-sorted JSON without the `seed_root` field. A `reproduce` freeze copies it.
- Seed *i* is the first 8 bytes, big-endian, of `sha256("<seed_root>:<i>")`, as for calibration records. *i* is the family's place in the registration's `families` list.
- The generator draws numbers only with `getrandbits`, whose output for a seed does not change between Python versions.

Anyone can compute `seed_root` from a registration that is not committed yet. So the held-out frames are held out by procedure: the ledger, the registration test, and the order of the commits below. The scoreboard says so.

## Fixed inputs: the edge set and the impulse frames

These families are fixed lists. They do not depend on `seed_root`, so every A1 figure in a registration (A1's refusals on the edge set and A1's observed loss) is computed before `seed_root` exists, in one pass. `ab_compare.py` checks this by computing the figures again from the registration with its `seed_root` field removed, and comparing them with the recorded ones.

- **Edge set:** each of these values on every channel at once, and on each channel alone: ±0, 1, 2⁻³⁰, 0.1, 0.3, 2⁻⁵⁴, 2⁻⁵³, 0.5 and its two neighbours, the value below 1, float32 roundings of 0.1, 0.3, 1/3 and 0.7, 5e-324, 1.5e-323, (1 + 2⁻⁵²)·2⁻¹⁰²¹, 2⁻¹⁰²⁰ and 2⁻¹⁰²². Then each pair of opposing gaze directions at (0.3, 0.1), (0.1, 0.3), (0.3, 0.3) and (1, 1).
- **Impulse frames:** the all-zero frame, then each channel alone at 1 and at 0.5.
- **Grid frames:** every channel at k/16 for k = 0 to 16, then each pattern of validity flags on a frame with every channel at 0.5.
- **Other fixed inputs:** the goldens in `tests/fixtures/fb2_goldens.json` (each on its source set, every other channel 0), the four example CSVs, the 221 FACS library frames and the 132 FACS key impulses. The registration pins the SHA-256 of each input file.

The seeded families mix full-mantissa binary64 values with 6-decimal values. The perturbation families leave out each input of a few seeded frames, set it to 1.5 and to −0.1, and clear each validity flag.

## Registration order

1. `python3 -B scripts/ab_compare.py draft OUT.abreg --date YYYY-MM-DD` writes a draft outside this folder. It pins the channel lists, the input hashes, the code hashes, the runtime and the B pack, freezes the maps of each B pair, and computes the A1 figures.
2. Fill in the frozen lists that the definitions audit and the data give (the loss-key table, the assumption catalogue, the audit-added keys and the others in `lists`). The project's release owners review the registration. Then compute `seed_root` again (`ab_compare.seed_root`).
3. Commit the registration to this folder. Then, in a later commit, add its line to `FREEZES`.
4. Run it: `python3 -B scripts/ab_compare.py run ab/ab.pivot-v1.abreg ab/results/v1`. A run whose pins do not match the checkout is refused. `--dry-run` runs anyway and marks the results as not registered.
5. Commit the results. Merge without squashing, so the commit order stays visible.

## Results

`results/v<N>/` holds:

- `scoreboard.md`: one row per metric with its threshold and status, and one row per pair with the evidence status, the M2c shortfall, M4b and whether an external reference exists ("no external reference" for pairs only B runs);
- one CSV per metric, a `*_failures.csv` that lists every failing frame or output, and `refusals.csv`, `losses.csv` and `assumptions.csv`;
- `manifest.json`: the freeze id, version, kind, the registration hash, every code and input hash and the runtime;
- `SHA256SUMS`: the hash of each result file and of each generated frame file;
- `timings.json`, which no hash covers.

Freeze ids, hashes and paths are only in `manifest.json`. So a `reproduce` run can match the results of the freeze it reproduces byte for byte, apart from `manifest.json`, its line in `SHA256SUMS`, and `timings.json`, which has no line there.

## What the tools compute today

`ab_compare.py` computes M1, M1s, M2, M2b, M2c, M3, M4 (observed loss), M5, M8 (B against A2), M10, M10b and B against O on every pair. The draft takes the M3 list of flat links from O: links of the composed hop weights that enter a piecewise operator on its flat side, so their impulse changes nothing. A `fix` or `revise` run makes the seeded families of every earlier freeze again with the generator that freeze pinned, taken from Git history, and checks their hashes against the earlier run's `SHA256SUMS`. The scoreboard marks the rest as pending until their frozen tables exist: the rule-scoped loss-key table for M4, the assumption catalogue for M4b, the geometry harness for M6, the mutation set for M7, the R3 goldens and the ICT-FaceKit comparison for M11. A run with a pending gate cannot pass.

A1's observed loss on the fixed impulse frames is 0 on all five A1 pairs (`python3 -B scripts/ab_compare.py a1-loss`). The first registration records it as A1's baseline.
