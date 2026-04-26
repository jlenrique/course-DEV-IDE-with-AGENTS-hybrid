from __future__ import annotations

import re

from app.specialists.wanda.graph import SANCTUM_DIR, _read_sanctum_digest


def test_l6_wondercraft_context_present_and_structural() -> None:
    path = SANCTUM_DIR / "L6-operational" / "wondercraft-context.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert len(text.splitlines()) >= 60
    for pattern in (
        r"^## Voice-ID catalog",
        r"^## Episode-template skeleton",
        r"^## Style-guide overrides",
    ):
        assert re.search(pattern, text, flags=re.MULTILINE)
    assert "<!-- TODO: operator-populate via First Breath ceremony -->" in text
    assert "L6-operational/wondercraft-context.md\t" in _read_sanctum_digest()
