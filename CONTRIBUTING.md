# Contributing

Original documentation: CC-BY-SA-4.0.

Edit TOML authoring, then run the following from the RCEF checkout, selecting the reviewed shared checkout in the first line:

```sh
export MSF_TOOLS_PATH="$(cd ../msf-tools && pwd -P)"
export PYTHONPATH="$MSF_TOOLS_PATH"
python3 -B check.py --tools-path "$MSF_TOOLS_PATH" --write
python3 -B check.py --tools-path "$MSF_TOOLS_PATH"
python3 -B scripts/run_acceptance.py --tools-path "$MSF_TOOLS_PATH"
```

Review all generated diffs. Acceptance requires the drift check and the qualification runner, which discovers every `tests/test_*.py` file and checks the pinned required methods. An unconfigured native run explicitly reports native unqualified; a configured `MSF_NATIVE_PATH` requires its accepted `MSF_NATIVE_SHA256` and zero skips. Use the binding artifact for the exact interpreter. Tests preserve declared storage/arithmetic scope; provider-frame and physiological admission remain separate. Both environment variables select the same shared checkout for discovery and its subprocess tests. The separately maintained shared tooling owns rendering, validation and evaluation algorithms. For local R-HARD qualification, use the accepted source archive and runtime-specific native artifact recorded in the reviewed consumer draft. The earlier `evidence/tooling.lock.json` remains pending separate R-DEP verifier and lock integration.

New or changed provider entries need a public primary source, exact revision or retrieval/content digest, locator, original summary, units/domain/calibration evidence and explicit disposition. Documentation positions are inventory ordinals unless the source defines a native index. Preserve source contradictions and unresolved mappings. Names alone do not justify cross-provider identities.

Every mapped rule states its assumptions, quality and losses. Keep native defaults separate from measured neutral and invalid data. Test independent expected values and meaningful rejection cases; do not duplicate the shared implementation to test it. Core code is MIT; original docs/data/fixtures are CC-BY-SA-4.0; inherited source terms remain intact. Raw source downloads belong in an explicitly chosen cache outside the repository.

Changes should include the affected evidence, generated artifacts, test results and remaining limitations. Review semantics and calibration separately from executable correctness. A proposal changes neither the wire contract nor support claims until its review and gates pass.

The manual GitHub workflow takes a shared repository and immutable commit. Configure a token only when that dependency is private. Local commands remain the verified workflow while shared tooling is local.
