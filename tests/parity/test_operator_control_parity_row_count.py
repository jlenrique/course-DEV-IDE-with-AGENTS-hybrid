"""SG-2 floor structural enforcement: 33-row parity-test suite."""

from __future__ import annotations

import importlib
import re
from pathlib import Path


def test_parity_test_suite_has_exactly_33_rows() -> None:
    suite_path = Path(__file__).parent / "test_operator_control_parity.py"
    text = suite_path.read_text(encoding="utf-8")
    test_funcs = re.findall(r"^def (test_row_\d+_\w+)", text, re.MULTILINE)
    assert len(test_funcs) == 33, (
        f"SG-2 floor violation: parity-test suite has {len(test_funcs)} test "
        "functions; expected exactly 33. Adding/removing rows requires "
        "party-mode consensus per NFR-V3."
    )


def test_parity_test_suite_declares_row_metadata_and_fr_references() -> None:
    module = importlib.import_module("tests.parity.test_operator_control_parity")
    rows: set[int] = set()

    for name in dir(module):
        if not name.startswith("test_row_"):
            continue
        test_func = getattr(module, name)
        row = getattr(test_func, "MAPPING_CHECKLIST_ROW", None)
        refs = getattr(test_func, "REFERENCES_FRS", None)
        assert isinstance(row, int), name
        assert isinstance(refs, list) and refs, name
        assert all(str(item).startswith("FR") for item in refs), name
        rows.add(row)

    assert rows == set(range(1, 34))
