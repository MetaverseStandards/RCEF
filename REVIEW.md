# Adversarial implementation review

SPDX-License-Identifier: CC-BY-SA-4.0

Reviewed 2026-10-07 against the consolidated authoring/API contract. This is an implementation self-review, not an external approval or visual-equivalence review.

## Actual delivered scope

893 signals in 22 profiles; 21 original canonical scalar projections; 6 mapping groups containing 24 rules: 22 exact, 1 approximate, 1 unresolved. Signal partitions: 47 mapped, 805 unresolved, 6 unsupported, 35 excluded. Every signal has a disposition, reason and valid evidence; every public source has exact digest, revision/retrieval and locator. Coverage retains all 27 evidence records, including unused baseline/license sources.

Exact selected names/order were audited against digest-verified public bytes: ARKit52, MediaPipe52, FB63/FB2 70, optional visemes15, VRCFT transport88/eye12/artist102+42/numeric parameters124+activity3, Godot102+41, VRM18, Roblox50. Genuine enum indices are checked; documentation list positions are called inventory ordinals. Constructors, count sentinels, absent tongue, transforms, confidence/configuration enums, reserved eye bytes and binary naming schemes remain visible separately.

## Actual commands and results

| Command / gate | Actual result |
|---|---|
| `python3 -B check.py --tools-path ../msf-tools --write` | PASS; four outputs rendered by shared tooling; zero diagnostics |
| `python3 -B check.py --tools-path ../msf-tools` | PASS; byte-identical outputs |
| `python3 -B tests/test_parity.py --tools-path ../msf-tools` | PASS: 10 tests, Python 3.12.15 |
| `python3.11 -B tests/test_parity.py --tools-path ../msf-tools` | PASS: 10 tests, Python 3.11.17 |
| `python3.11 -B check.py --tools-path ../msf-tools` | PASS; same pack/csv/coverage/SHA256SUMS bytes as 3.12 |
| Shared `AuthoringTests`, `MappingTests`, `CLITests` from `tests/test_reference.py`, loaded with stdlib unittest | PASS: 13 relevant shared tests; algorithms not copied here |
| `python3 -B scripts/verify_sources.py --cache CACHE` | PASS: all 26 public records re-fetched and SHA256 matched, zero failures |
| `python3 -B scripts/audit_inventories.py --cache CACHE` | PASS: all15 selected profile surfaces exact names/order/counts; enum indices agree |
| Public-artifact path scan and local Markdown link check | PASS after review file creation; no private/internal source paths/session identifiers |

The cache is an explicitly supplied directory outside the public repository. Source verification downloads are bounded to5MB/25seconds per request. Generated pack SHA256: `99ea6893ddbc4c68686d90f6f2202b33db71c330c2266dfbc95e27e644a046d8`. Other hashes are in [SHA256SUMS](generated/SHA256SUMS). The tested shared source fingerprint is in [tooling.lock.json](evidence/tooling.lock.json); the implementation publisher has now frozen the tested local dependency commit.

Numerical tests use independent literal expectations: signed affine endpoints/midpoint, asymmetric bilateral collapse, and all21 explicit provider-calibrated identities. Refusal tests cover missing/invalid required data, boolean/string/nonfinite scalars, input/output domain violations, unresolved cross-provider mapping and malformed authoring. Shared tests cover cycles, multiple writers, topology, calibration/units, deterministic exports and input/output alias protection. Drift tests actually reject missing, extra, manually edited and reordered outputs, and verify repeated generation bytes.

## Findings and corrections

1. A combined fixture source/target profile made the output a source driver. Shared compilation correctly rejected it; separate fixture.source and fixture.target manifests fixed the input.
2. Shared initial coverage omitted evidence/partitions and initial checking allowed an extra generated file. Both failures were reported via status files, corrected by the shared tooling owner, then re-tested. The consumer test's guessed `partitions` key was corrected to the shared `dispositions`/`mapping_quality` fields.
3. Native documentation positions were initially called native indices. Renamed to inventory ordinals; actual enums retain verified indices. Parameter native names retain `v2/` while stable IDs use portable separators.
4. VRCFT physical-pupil records initially imposed an unsupported positive domain. Removed that inferred bound; raw millimetre storage is preserved without adding a clamp.
5. Apple shared inner-brow coupling was initially implicit. Declared bilateral_shared; its canonical definition states that separate inner-side activation is not recoverable.
6. Preserved lower-lip/sad-side/nasal-side/binary-denominator contradictions as unresolved metadata; no derived identity or operator resolves them by guess.
7. Expanded VRM morph/material/texture binding fields/defaults and binary override semantics; VRCFT normalization state fields retained as excluded ancillary records. Artist component order retained as source inventory without executable weights.
8. Original MIT code and CC-BY-SA-4.0 data/docs/fixtures are separated by notices; inherited terms retained. Source prose/figures/algorithms remain unbundled. Exact source cache is external.

## Remaining evidence and gates

- MediaPipe model calibration/provenance; FB1 numeric bounds; FB2 direction maximum angles; VRCFT raw gaze units and documented contradictions; Roblox authoritative required-pose set. Affected mappings remain unresolved.
- Permission for redistributing VRM specification prose remains unknown. Current artifacts contain attributed names/facts and links, with original summaries.
- The tested shared dependency is pinned in `evidence/tooling.lock.json`. Shared tooling has no remote publisher yet; its remote CI remains pending. RCEF private repository publication is handled by the implementation publisher separately from this worker review.
- Device integration, physical calibration, geometry visual equivalence, VRM binding/material/override execution, Roblox certification, native/host acceptance and standards adoption are downstream gates. Scalar acceptance makes no claim that these ran.

Verdict: selected inventory and scalar authoring parity implemented and tested; remaining evidence limits are explicit, not reported as resolved.
