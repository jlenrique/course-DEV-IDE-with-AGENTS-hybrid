from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANTI_PATTERN_CATALOG = REPO_ROOT / "docs/dev-guide/specialist-anti-patterns.md"


def test_a11_contains_slab_7c_cp1252_worked_example():
    text = ANTI_PATTERN_CATALOG.read_text(encoding="utf-8")
    match = re.search(
        r"^### A11\..*?(?=^### A12\.)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )

    assert match is not None
    section = match.group(0)
    normalized_section = section.lower()
    for keyword in (
        "Slab 7c",
        "§02A",
        "U+202F",
        "structural fix",
        "PYTHONIOENCODING",
        "cp1252",
    ):
        assert keyword.lower() in normalized_section
