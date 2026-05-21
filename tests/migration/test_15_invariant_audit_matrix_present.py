from __future__ import annotations

from pathlib import Path

MATRIX = Path("_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md")


def test_15_invariant_audit_matrix_present() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    assert MATRIX.is_file()
    rows = [
        line
        for line in text.splitlines()
        if line.startswith("| #")
    ]
    assert len(rows) >= 15
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        assert len(cells) == 7
        assert all(cells)

