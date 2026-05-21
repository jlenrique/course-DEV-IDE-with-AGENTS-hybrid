"""Shim verdict vocabulary closure (Story 7a.7, AC-7.7-D).

7a.7 shims emit OperatorVerdict.verb (closed enum {approve, edit, reject}).
The shim modules themselves should NOT contain inline string-literal verdict
tokens; they should reference the OperatorVerdict model exclusively.

This is a structural test that AST-scans the 4 shim modules + asserts no
inline verdict-shape string literals leak into emit-call sites.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SHIM_DIR = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "marcus"
    / "cli"
    / "gate_shims"
)

SHIMS = ["g1_shim.py", "g2c_shim.py", "g3_shim.py", "g4_shim.py"]

# Tokens that must NOT appear as bare string literals in shim source
# (they must come from the OperatorVerdict enum / vocabulary registry).
SUSPECT_VERDICT_TOKENS = {"approve", "edit", "reject"}


def _string_literals_in_call_args(source: str) -> set[str]:
    """Collect string-literal call-arg values across the module AST."""
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.add(arg.value)
            for kw in node.keywords:
                if (
                    isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                ):
                    found.add(kw.value.value)
    return found


@pytest.mark.parametrize("shim_name", SHIMS)
def test_shim_does_not_contain_inline_verdict_tokens_in_calls(shim_name: str) -> None:
    shim_path = SHIM_DIR / shim_name
    source = shim_path.read_text(encoding="utf-8")
    found = _string_literals_in_call_args(source)
    leaks = found & SUSPECT_VERDICT_TOKENS
    assert not leaks, (
        f"{shim_name} contains inline verdict tokens in call args: {leaks}; "
        f"must use OperatorVerdict enum instead"
    )
