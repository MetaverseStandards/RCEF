# Contributing

Original documentation: CC-BY-SA-4.0.

Edit TOML authoring, then run `python3 -B check.py --tools-path ../msf-tools --write`, review all generated diffs and run `python3 -B tests/test_parity.py --tools-path ../msf-tools`. The separately maintained shared tooling owns rendering, validation and evaluation algorithms. Use a reviewed dependency revision recorded in `evidence/tooling.lock.json`.

New or changed provider entries need a public primary source, exact revision or retrieval/content digest, locator, original summary, units/domain/calibration evidence and explicit disposition. Documentation positions are inventory ordinals unless the source defines a native index. Preserve source contradictions and unresolved mappings. Names alone do not justify cross-provider identities.

Every mapped rule states its assumptions, quality and losses. Keep native defaults separate from measured neutral and invalid data. Test independent expected values and meaningful rejection cases; do not duplicate the shared implementation to test it. Core code is MIT; original docs/data/fixtures are CC-BY-SA-4.0; inherited source terms remain intact. Raw source downloads belong in an explicitly chosen cache outside the repository.

Changes should include the affected evidence, generated artifacts, test results and remaining limitations. Review semantics and calibration separately from executable correctness. A proposal changes neither the wire contract nor support claims until its review and gates pass.

The manual GitHub workflow takes a shared repository and immutable commit. Configure a token only when that dependency is private. Local commands remain the verified workflow while shared tooling is local.
