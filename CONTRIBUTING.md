# Contributing

Original documentation: CC-BY-SA-4.0.

Coding agents: read [AGENTS.md](AGENTS.md) first. It lists the commands, the rules that must not break and the known traps.

Edit the TOML authoring files, and run all commands from the RCEF checkout. Install the msf-character-tools release wheel locked in [tooling.lock.json](evidence/tooling.lock.json) into the Python you use for RCEF, by hash, as [Generate and check](README.md#generate-and-check) in the README shows.

Then regenerate the outputs:

```sh
python3 -B check.py --write
```

Review the generated diffs, then check existing outputs without writing and run the tests:

```sh
python3 -B check.py
python3 -B -m unittest discover -s tests
```

Review every generated diff. The tests cover declared storage and arithmetic. Provider frames and physiology need their own separate review. The tests and their subprocesses use the installed msf-character-tools. The shared tooling, which is maintained separately, owns the rendering, validation and evaluation algorithms.

A new or changed provider entry needs all of these: a public primary source; an exact revision, or a retrieval date and content digest; a locator; an original summary; evidence for its units, domain and calibration; and an explicit disposition. A position in a documentation list is an inventory ordinal, unless the source defines a native index. Keep contradictions between sources, and keep unresolved mappings. Names alone do not justify a cross-provider identity.

Every mapping with disposition `mapped` states its assumptions, quality and losses. Keep native defaults separate from measured neutral values and from invalid data. Test against expected values found independently, and test refusals that matter. Do not copy the shared implementation into a test to check it. Core code is MIT. Original documentation, data and fixtures are CC-BY-SA-4.0. Inherited source terms stay as they are. Put raw source downloads in a cache that you choose, outside the repository.

A change includes the affected evidence, the generated files, the test results and the limitations that remain. Review meaning and calibration separately from executable correctness. A proposal does not change the wire contract or any support claim until it passes its review and gates.

When GitHub Actions is turned on, the GitHub workflow runs on every push and pull request, and you can also start it by hand. It downloads the locked msf-character-tools release wheel for Linux x86_64 from the public [msf-character-tools releases](https://github.com/MetaverseStandards/msf_character_tools/releases), and installs it by hash. It needs no token. Then it runs `check.py` and the tests on Python 3.11 and 3.12. GitHub Actions is not turned on for this repository. Instead, run `scripts/ci_local.sh`, which does the same on the local 3.11 and 3.12 venvs, and paste its summary into the pull request.
