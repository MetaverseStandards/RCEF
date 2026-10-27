# SPDX-License-Identifier: MIT
"""One compiled RCEF pack shared by the test modules that only read it.

Loading and compiling the full pack takes about a second, and msf-tools
records are immutable, so modules share one copy instead of compiling their own.
"""
from functools import cache
from pathlib import Path

import msf_tools as msf

ROOT = Path(__file__).resolve().parents[1]


@cache
def authoring():
    loaded = msf.load_authoring(ROOT)
    if loaded.value is None:
        raise AssertionError(loaded.report.to_dict())
    return loaded.value


def document():
    """A fresh, editable dictionary copy of the authored data."""
    return authoring().to_dict()


@cache
def pack():
    compiled = msf.compile_pack(authoring())
    if compiled.value is None:
        raise AssertionError(compiled.report.to_dict())
    return compiled.value


@cache
def mapping(mapping_id, source, target, approximate=True):
    result = msf.compile_mapping(pack(), msf.profile_snapshot(pack(), source).value,
                                 msf.profile_snapshot(pack(), target).value, mapping_id, approximate)
    if result.value is None:
        raise AssertionError((mapping_id, result.report.to_dict()))
    return result.value
