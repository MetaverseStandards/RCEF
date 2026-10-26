# Contributing

Original documentation: CC-BY-SA-4.0.

Edit TOML authoring, then run the following from the RCEF checkout, selecting the reviewed shared checkout in the first line:

```sh
export MSF_TOOLS_PATH="$(cd ../msf-tools && pwd -P)"
export PYTHONPATH="$MSF_TOOLS_PATH"
python3 -B check.py --tools-path "$MSF_TOOLS_PATH" --write
```

Review the generated diffs, then check existing outputs without writing and run the tests:

```sh
export MSF_TOOLS_PATH="$(cd ../msf-tools && pwd -P)"
export PYTHONPATH="$MSF_TOOLS_PATH"
python3 -B check.py --tools-path "$MSF_TOOLS_PATH"
python3 -B -m unittest discover -s tests
```

Review all generated diffs. Tests preserve declared storage/arithmetic scope; provider-frame and physiological admission remain separate. Both environment variables select the same shared checkout for the tests and their subprocesses. The separately maintained shared tooling owns rendering, validation and evaluation algorithms. The earlier `evidence/tooling.lock.json` remains pending separate R-DEP verifier and lock integration.

New or changed provider entries need a public primary source, exact revision or retrieval/content digest, locator, original summary, units/domain/calibration evidence and explicit disposition. Documentation positions are inventory ordinals unless the source defines a native index. Preserve source contradictions and unresolved mappings. Names alone do not justify cross-provider identities.

Every mapped rule states its assumptions, quality and losses. Keep native defaults separate from measured neutral and invalid data. Test independent expected values and meaningful rejection cases; do not duplicate the shared implementation to test it. Core code is MIT; original docs/data/fixtures are CC-BY-SA-4.0; inherited source terms remain intact. Raw source downloads belong in an explicitly chosen cache outside the repository.

Changes should include the affected evidence, generated artifacts, test results and remaining limitations. Review semantics and calibration separately from executable correctness. A proposal changes neither the wire contract nor support claims until its review and gates pass.

The manual GitHub workflow takes a shared repository and immutable commit. Configure a token only when that dependency is private. Local commands remain the verified workflow while shared tooling is local.
