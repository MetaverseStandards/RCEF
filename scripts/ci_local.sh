#!/bin/sh
# SPDX-License-Identifier: MIT
# Run check.py and the test suite on the local Python 3.11 and 3.12 venvs and
# print a pass/fail summary to paste into a pull request. GitHub Actions is not
# turned on for this repository, so this is the CI run.
#
# The venv of Python X.Y is $RCEF_VENVS/X.Y (for example $RCEF_VENVS/3.11).
# RCEF_VENVS defaults to ${XDG_DATA_HOME:-$HOME/.local/share}/rcef/venvs, the
# XDG data directory; a symbolic link to an existing venv is fine. Each venv
# must have the msf-character-tools release wheel recorded in
# evidence/tooling.lock.json installed by hash.
set -u
VENVS=${RCEF_VENVS:-${XDG_DATA_HOME:-$HOME/.local/share}/rcef/venvs}
ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
LOGS=$(mktemp -d "${TMPDIR:-/tmp}/rcef-ci.XXXXXX")
cd "$ROOT" || exit 2
# check.py would refuse an msf-character-tools selected through PYTHONPATH;
# keep the run clean.
unset PYTHONPATH

overall=PASS
rows=''
for version in 3.11 3.12; do
    python="$VENVS/$version/bin/python"
    if [ ! -x "$python" ]; then
        rows="$rows| $version | missing venv | not run |
"
        overall=FAIL
        continue
    fi
    if "$python" -B check.py >"$LOGS/check-$version.log" 2>&1; then
        check=pass
    else
        check="FAIL (log: $LOGS/check-$version.log)"
        overall=FAIL
    fi
    if "$python" -B -m unittest discover -s tests >"$LOGS/tests-$version.log" 2>&1; then
        tests=pass
    else
        tests=FAIL
        overall=FAIL
    fi
    ran=$(grep -E '^Ran [0-9]+ tests? in' "$LOGS/tests-$version.log" | tail -1)
    detail=$(grep -E '^(OK|FAILED)' "$LOGS/tests-$version.log" | tail -1)
    if [ "$tests" = FAIL ]; then
        tests="FAIL: $ran, $detail (log: $LOGS/tests-$version.log)"
    else
        tests="pass: $ran"
    fi
    rows="$rows| $version | $check | $tests |
"
done

commit=$(git rev-parse --short HEAD)
dirty=$(git status --porcelain | head -1)
locked=$(sed -n 's/.*"git_commit": "\([0-9a-f]*\)".*/\1/p' evidence/tooling.lock.json | cut -c1-12)
echo "### Local CI: $overall"
echo
echo "RCEF \`$commit\`${dirty:+ (with uncommitted changes)}; msf-character-tools locked at \`$locked\`."
echo "check.py verifies the installed msf-character-tools against the lock before checking."
echo
echo "| Python | check.py | tests |"
echo "|---|---|---|"
printf '%s' "$rows"
[ "$overall" = PASS ] && rm -rf "$LOGS"
rmdir "$LOGS" 2>/dev/null
[ "$overall" = PASS ]
