# Contributing

Original documentation: CC-BY-SA-4.0.

Edit TOML authoring, then work from the RCEF checkout. Install msf-tools at the commit recorded as `git_commit` in [tooling.lock.json](evidence/tooling.lock.json), from GitHub or from a local checkout, into the Python you use for RCEF:

```sh
python3 -m pip install "git+https://github.com/Kjakubzak/msf-tools@COMMIT"
# or: python3 -m pip install "git+file://$(cd ../msf-tools && pwd -P)@COMMIT"
```

Then regenerate the outputs:

```sh
python3 -B check.py --write
```

Review the generated diffs, then check existing outputs without writing and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

Review all generated diffs. Tests preserve declared storage/arithmetic scope; provider-frame and physiological admission remain separate. The tests and their subprocesses use the installed msf-tools. The separately maintained shared tooling owns rendering, validation and evaluation algorithms.

New or changed provider entries need a public primary source, exact revision or retrieval/content digest, locator, original summary, units/domain/calibration evidence and explicit disposition. Documentation positions are inventory ordinals unless the source defines a native index. Preserve source contradictions and unresolved mappings. Names alone do not justify cross-provider identities.

Every mapped rule states its assumptions, quality and losses. Keep native defaults separate from measured neutral and invalid data. Test independent expected values and meaningful rejection cases; do not duplicate the shared implementation to test it. Core code is MIT; original docs/data/fixtures are CC-BY-SA-4.0; inherited source terms remain intact. Raw source downloads belong in an explicitly chosen cache outside the repository.

Changes should include the affected evidence, generated artifacts, test results and remaining limitations. Review semantics and calibration separately from executable correctness. A proposal changes neither the wire contract nor support claims until its review and gates pass.

The GitHub workflow runs on every push and pull request, and can be started by hand. It installs msf-tools from `Kjakubzak/msf-tools` at the locked commit, using the read-only `MSF_TOOLS_TOKEN` repository secret, then runs `check.py` and the tests on Python 3.11 and 3.12. GitHub Actions is not enabled on these repositories at the moment, so run `scripts/ci_local.sh`, which does the same on the local 3.11 and 3.12 venvs, and paste its summary into the pull request.
