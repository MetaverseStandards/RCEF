# Contributing

Original documentation: CC-BY-SA-4.0.

Edit the TOML authoring files, and run all commands from the RCEF checkout. Install msf-tools at the commit recorded as `git_commit` in [tooling.lock.json](evidence/tooling.lock.json), from GitHub or from a local checkout, into the Python you use for RCEF:

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

Review every generated diff. The tests cover declared storage and arithmetic. Provider frames and physiology need their own separate review. The tests and their subprocesses use the installed msf-tools. The shared tooling, which is maintained separately, owns the rendering, validation and evaluation algorithms.

A new or changed provider entry needs all of these: a public primary source; an exact revision, or a retrieval date and content digest; a locator; an original summary; evidence for its units, domain and calibration; and an explicit disposition. A position in a documentation list is an inventory ordinal, unless the source defines a native index. Keep contradictions between sources, and keep unresolved mappings. Names alone do not justify a cross-provider identity.

Every mapping with disposition `mapped` states its assumptions, quality and losses. Keep native defaults separate from measured neutral values and from invalid data. Test against expected values found independently, and test refusals that matter. Do not copy the shared implementation into a test to check it. Core code is MIT. Original documentation, data and fixtures are CC-BY-SA-4.0. Inherited source terms stay as they are. Put raw source downloads in a cache that you choose, outside the repository.

A change includes the affected evidence, the generated files, the test results and the limitations that remain. Review meaning and calibration separately from executable correctness. A proposal does not change the wire contract or any support claim until it passes its review and gates.

The GitHub workflow runs on every push and pull request, and you can also start it by hand. It installs msf-tools from `Kjakubzak/msf-tools` at the locked commit, with the read-only `MSF_TOOLS_TOKEN` repository secret. Then it runs `check.py` and the tests on Python 3.11 and 3.12. GitHub Actions is not turned on for these repositories at the moment. Instead, run `scripts/ci_local.sh`, which does the same on the local 3.11 and 3.12 venvs, and paste its summary into the pull request.
