# SPDX-License-Identifier: MIT
"""Check that a held-out run uses exactly the code a calibration record names in code_commit."""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True)


def code_problem(repo: Path, code_commit: str, paths: list[str]) -> str | None:
    """Why the checkout's code under `paths` is not the code at `code_commit`, or None if it is.

    The record is committed after the code it names, so HEAD is normally a later
    commit. What must hold is that `code_commit` is in HEAD's history and that
    nothing under `paths` has changed since then, committed or not.
    """
    if _git(repo, 'cat-file', '-e', f'{code_commit}^{{commit}}').returncode:
        return f'code_commit {code_commit} is not a commit in this repository'
    if _git(repo, 'merge-base', '--is-ancestor', code_commit, 'HEAD').returncode:
        return f'code_commit {code_commit[:12]} is not an ancestor of HEAD; check out the history the record was made in'
    changed = _git(repo, 'diff', '--name-only', code_commit, 'HEAD', '--', *paths).stdout.split()
    if changed:
        return (f'the code has changed since code_commit {code_commit[:12]}: {", ".join(changed)}; a held-out run '
                'must use the code the record names')
    dirty = _git(repo, 'status', '--porcelain', '--', *paths).stdout.strip()
    if dirty:
        return f'uncommitted changes to the code the record names:\n{dirty}'
    return None


def loaded_files(repo: Path) -> list[str]:
    """Repository-relative paths of every imported module whose file is inside `repo`.

    Taken after the run's imports, this is the repository code the run depends
    on, wherever it lives (check.py, examples/, tools/), without a list to keep.
    """
    root = Path(repo).resolve()
    files = set()
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path:
            path = Path(path).resolve()
            if path.is_relative_to(root):
                files.add(path.relative_to(root).as_posix())
    return sorted(files)
