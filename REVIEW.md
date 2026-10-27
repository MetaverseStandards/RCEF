# Adversarial implementation review

SPDX-License-Identifier: CC-BY-SA-4.0

This review was done on 2026-10-07 against the consolidated authoring and API contract. It is a self-review of the implementation. It is not an outside approval, and it does not review visual equivalence. The numbers below describe the repository on that date.

## Scope delivered

893 signals in 22 profiles; 21 original canonical scalar projections; 6 maps with 24 mappings: 22 exact, 1 approximate, 1 unresolved. Signal dispositions: 47 mapped, 805 unresolved, 6 unsupported, 35 excluded. Every signal has a disposition, a reason and valid evidence. Every public source has an exact digest, a revision or retrieval date, and a locator. Coverage keeps all 27 evidence records, including baseline and licence sources that nothing uses.

The exact selected names and their order were audited against public bytes with verified digests: ARKit 52, MediaPipe 52, FB 63 and FB2 70, optional visemes 15, VRCFT transport 88, eye 12, artist 102+42, numeric parameters 124 and activity flags 3, Godot 102+41, VRM 18, Roblox 50. Real enum indices are checked. Positions in documentation lists are called inventory ordinals. Constructors, count sentinels, the absent tongue row, transforms, confidence and configuration enums, reserved eye bytes and binary naming schemes are each recorded separately and stay visible.

## Commands run and results

| Command or gate | Result |
|---|---|
| `python3 -B check.py --tools-path ../msf-tools --write` | PASS; the shared tooling rendered four outputs; zero diagnostics |
| `python3 -B check.py --tools-path ../msf-tools` | PASS; outputs identical byte for byte |
| `python3 -B tests/test_parity.py --tools-path ../msf-tools` | PASS: 10 tests, Python 3.12.15 |
| `python3.11 -B tests/test_parity.py --tools-path ../msf-tools` | PASS: 10 tests, Python 3.11.17 |
| `python3.11 -B check.py --tools-path ../msf-tools` | PASS; the same pack, CSV, coverage and SHA256SUMS bytes as on 3.12 |
| Shared `AuthoringTests`, `MappingTests`, `CLITests` from `tests/test_reference.py`, loaded with stdlib unittest | PASS: 13 relevant shared tests; their algorithms are not copied here |
| `python3 -B scripts/verify_sources.py --cache CACHE` | PASS: all 26 public records downloaded again and their SHA256 matched; zero failures |
| `python3 -B scripts/audit_inventories.py --cache CACHE` | PASS: all 15 selected profile surfaces have exact names, order and counts; enum indices agree |
| Scan of public files for paths, and check of local Markdown links | PASS after this review file was created; no private or internal source paths and no session identifiers |

The cache is a directory given on the command line, outside the public repository. Each download for source verification is limited to 5 MB and 25 seconds. Generated pack SHA256: `99ea6893ddbc4c68686d90f6f2202b33db71c330c2266dfbc95e27e644a046d8`. The other hashes are in [SHA256SUMS](generated/SHA256SUMS). The fingerprint of the tested shared source is in [tooling.lock.json](evidence/tooling.lock.json). The publisher of the implementation has since frozen the tested local dependency commit.

The numerical tests use expected values written independently of the code: the endpoints and midpoint of the signed affine fixture, the asymmetric bilateral collapse, and all 21 explicit provider-calibrated identities. The refusal tests cover missing or invalid required data; boolean, string and non-finite scalars; input and output domain violations; an unresolved cross-provider mapping; and malformed authoring. The shared tests cover cycles, multiple writers, topology, calibration and units, deterministic exports, and protection against input and output aliases. The drift tests reject missing, extra, hand-edited and reordered outputs, and they check that repeated generation gives the same bytes.

## Findings and corrections

1. One combined fixture profile, used as both source and target, made the output a source driver. Shared compilation rightly refused it. Separate `fixture.source` and `fixture.target` profiles fixed the input.
2. The first shared coverage left out evidence and partitions, and the first check allowed an extra generated file. Both failures were reported through status files, fixed by the owner of the shared tooling, and tested again. The consumer test had guessed a `partitions` key; it was changed to the shared `dispositions` and `mapping_quality` fields.
3. Positions in native documentation were first called native indices. They were renamed to inventory ordinals; real enums keep their verified indices. Parameter native names keep `v2/`, while stable IDs use portable separators.
4. The VRCFT physical-pupil records first set a positive domain that no source supports. That inferred bound was removed. Raw millimetre storage is kept, with no clamp added.
5. Apple's shared inner-brow coupling was first only implied. It is now declared as `bilateral_shared`, and its canonical definition states that a separate inner-side activation cannot be recovered.
6. The contradictions about the lower lip, the sad side, the nasal side and the binary denominator are kept as unresolved metadata. No derived identity or operator resolves them by guessing.
7. The VRM morph, material and texture binding fields and defaults, and the binary override behaviour, were recorded in more detail. VRCFT normalization state fields are kept as excluded ancillary records. The order of artist components is kept as source inventory, with no executable weights.
8. Notices separate the original MIT code from the CC-BY-SA-4.0 data, documentation and fixtures, and inherited terms are kept. Source prose, figures and algorithms are not included. The exact source cache is kept outside the repository.

## Evidence and gates still open

- MediaPipe model calibration and provenance; FB1 numeric bounds; FB2 maximum angles per direction; VRCFT raw gaze units and the documented contradictions; the authoritative Roblox set of required poses. The affected mappings stay unresolved.
- It is still unknown whether VRM specification prose may be redistributed. The current files contain names and facts with attribution, links, and original summaries.
- The tested shared dependency is pinned in `evidence/tooling.lock.json`. The shared tooling has no remote publisher yet, so its remote CI is still pending. The publisher of the implementation handles publication of the private RCEF repository, separately from this review.
- Device integration, physical calibration, visual equivalence of geometry, execution of VRM bindings, materials and overrides, Roblox certification, native and host acceptance, and standards adoption are later gates. Scalar acceptance does not claim that any of them ran.

Verdict: the selected inventory and scalar authoring parity are implemented and tested. The remaining evidence limits are stated, not reported as resolved.
