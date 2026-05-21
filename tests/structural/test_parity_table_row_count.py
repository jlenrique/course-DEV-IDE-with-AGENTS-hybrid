"""Parity table row-count pins for Story 7a.6."""

from __future__ import annotations

import re
from pathlib import Path

TABLE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "operator"
    / "legacy-vs-langgraph-control-parity.md"
)


def _numbered_rows() -> list[list[str]]:
    rows = []
    for line in TABLE_PATH.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| ?\d+ ?\|", line):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def test_parity_table_has_exactly_33_numbered_rows() -> None:
    assert len(_numbered_rows()) == 33


def test_parity_table_rows_have_non_empty_test_ids() -> None:
    for row in _numbered_rows():
        assert row[3].startswith("`test_row_")
        assert row[3].endswith("`")
