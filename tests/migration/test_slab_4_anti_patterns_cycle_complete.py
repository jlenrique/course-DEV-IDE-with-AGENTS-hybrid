from __future__ import annotations

import re
from pathlib import Path


def test_slab_4_anti_patterns_catalog_harvest_cycle_complete() -> None:
    catalog_path = Path("docs/dev-guide/specialist-anti-patterns.md")

    text = catalog_path.read_text(encoding="utf-8")
    entry_count = len(re.findall(r"^### A\d+\.", text, flags=re.MULTILINE))

    assert catalog_path.is_file()
    assert entry_count >= 5
    assert entry_count >= 14
    assert "Slab 4 harvest cycle complete" in text
    assert "Format version: 1" in text

