from __future__ import annotations

from pathlib import Path

MATRIX = Path("_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md")


def test_15_invariant_stub_absorption() -> None:
    text = MATRIX.read_text(encoding="utf-8")

    assert "slab-2c-wondercraft-invariant-stub.md" in text
    assert "slab-3-marcus-invariant-stub.md" in text
    assert "#13 Specialist registry authoritative" in text
    assert "#1 Marcus SPOT" in text

