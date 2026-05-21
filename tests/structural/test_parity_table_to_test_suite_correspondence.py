"""Bidirectional parity-table to test-suite correspondence."""

from __future__ import annotations

import re
from pathlib import Path

TABLE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "operator"
    / "legacy-vs-langgraph-control-parity.md"
)
SUITE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "parity"
    / "test_operator_control_parity.py"
)


def _table_test_ids() -> list[str]:
    ids = []
    for line in TABLE_PATH.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| ?\d+ ?\|", line):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            ids.append(cells[3].strip("`"))
    return ids


def _suite_test_ids() -> set[str]:
    text = SUITE_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"^def (test_row_\d+_\w+)", text, re.MULTILINE))


def test_each_parity_table_row_names_real_test_function() -> None:
    suite_ids = _suite_test_ids()
    for test_id in _table_test_ids():
        assert test_id in suite_ids


def test_each_parity_test_function_is_named_by_table() -> None:
    assert _suite_test_ids() == set(_table_test_ids())
