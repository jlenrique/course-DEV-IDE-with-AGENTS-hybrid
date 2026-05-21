from __future__ import annotations

import re
from pathlib import Path


def test_langgraph_state_idioms_section_6_finalized() -> None:
    doc_path = Path("docs/dev-guide/langgraph-state-idioms.md")
    text = doc_path.read_text(encoding="utf-8")
    section = re.search(
        r"^## 6\.(?P<body>.*?)(?:^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert doc_path.is_file()
    assert section is not None
    assert "<!-- TODO -->" not in section.group("body")
    assert len(re.findall(r"\b\w+\b", section.group("body"))) >= 200
    assert "```python" in section.group("body")

