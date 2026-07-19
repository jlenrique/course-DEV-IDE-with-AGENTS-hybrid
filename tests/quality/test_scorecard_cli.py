"""Story Q1.1 — FIX-2: ``_fmt_summary`` must not crash on a well-typed-but-degenerate
machine block (dict block whose ``dimensions`` is null/list, or whose DID key maps to
a scalar). The reader is fail-soft; the CLI's summary formatter must be too — a
malformed-but-parseable block should format gracefully rather than AttributeError.

Hermetic: the CLI module is loaded by file path (it is a ``scripts/utilities`` tool,
not an installed package) and ``_fmt_summary`` is exercised directly on in-memory
blocks. RED-first: before the ``isinstance`` guards, each parametrized block raised
``AttributeError`` inside ``_fmt_summary`` (``None.get`` / ``list.get`` / scalar
``.get``); after the guard each returns a string.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

_CLI_PATH = Path(__file__).resolve().parents[2] / "scripts" / "utilities" / "quality_scorecard.py"


def _load_cli() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_q1_quality_scorecard_cli", _CLI_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "block",
    [
        pytest.param({"schema": "quality-scorecard/v2", "dimensions": None}, id="dimensions-null"),
        pytest.param(
            {"schema": "quality-scorecard/v2", "dimensions": ["not", "a", "mapping"]},
            id="dimensions-list",
        ),
        pytest.param(
            {
                "schema": "quality-scorecard/v2",
                "dimensions": {"dynamic_intelligence_vs_determinism": "scalar-not-a-dict"},
            },
            id="did-scalar",
        ),
        pytest.param({}, id="empty-block"),
    ],
)
def test_fmt_summary_does_not_raise_on_degenerate_block(block: dict) -> None:
    cli = _load_cli()
    out = cli._fmt_summary(block)  # must NOT raise
    assert isinstance(out, str)
    assert "Project Quality Scorecard" in out
