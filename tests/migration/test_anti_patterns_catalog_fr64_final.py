from __future__ import annotations

import re
from pathlib import Path

CATALOG = Path("docs/dev-guide/specialist-anti-patterns.md")


def test_anti_patterns_catalog_fr64_final() -> None:
    text = CATALOG.read_text(encoding="utf-8")

    assert CATALOG.is_file()
    assert "Slab 1+2+3+4+5a harvest cycle complete" in text
    entries = re.findall(r"^### A\d+\.", text, flags=re.MULTILINE)
    assert len(entries) >= 5
    for entry in entries[:5]:
        start = text.index(entry)
        next_heading = text.find("\n### ", start + 1)
        body = text[start:] if next_heading == -1 else text[start:next_heading]
        assert "**Example" in body
        assert "**Counter-pattern:**" in body
        assert "Slab-of-discovery" in body or "Slab of discovery" in body
