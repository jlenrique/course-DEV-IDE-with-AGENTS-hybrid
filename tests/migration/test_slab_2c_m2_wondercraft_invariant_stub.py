from __future__ import annotations

from pathlib import Path

STUB = Path("_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md")


def test_wondercraft_invariant_stub_has_two_populated_rows() -> None:
    assert STUB.is_file()
    text = STUB.read_text(encoding="utf-8")
    assert "STUB FOR SLAB 5A INVARIANT AUDIT EPIC ABSORPTION" in text
    for specialist in ("wanda", "wanda_validation"):
        matching_rows = [
            line
            for line in text.splitlines()
            if line.startswith(f"| {specialist} |")
        ]
        assert len(matching_rows) == 1
        cells = [cell.strip() for cell in matching_rows[0].strip("|").split("|")]
        assert len(cells) == 8
        assert all(cells)
