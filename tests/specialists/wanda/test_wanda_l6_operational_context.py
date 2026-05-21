from __future__ import annotations

import re

from app.specialists.wanda.graph import SANCTUM_DIR, _read_sanctum_digest


def test_legacy_l6_context_folded_into_capabilities() -> None:
    path = SANCTUM_DIR / "CAPABILITIES.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "Folded Operational Context" in text
    for pattern in (
        r"^### Voice-ID catalog",
        r"^### Episode-template skeleton",
        r"^### Style-guide overrides",
    ):
        assert re.search(pattern, text, flags=re.MULTILINE)
    assert "<!-- TODO: operator-populate via First Breath ceremony -->" in text
    assert "CAPABILITIES.md\t" in _read_sanctum_digest()
