from __future__ import annotations

import re
from pathlib import Path


def test_m5_inherited_conditional_resolved() -> None:
    text = Path("_bmad-output/implementation-artifacts/m5-decision.md").read_text(
        encoding="utf-8"
    )
    section = re.search(
        r"^## Inherited Conditional States\n(?P<body>.*?)(?:^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert section is not None
    body = section.group("body")
    assert "M2:" in body
    assert "M3:" in body
    assert "M4:" in body
    assert "5a.2 rider:" in body
    assert "slab-3-m5-dispatch-registry-swap:" in body
    assert "5a.3 ratification: RESOLVED 2026-04-26" in body
    assert "2026-05-03" in text
