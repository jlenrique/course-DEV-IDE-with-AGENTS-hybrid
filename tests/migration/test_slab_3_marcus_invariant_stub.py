from __future__ import annotations

import re
from pathlib import Path


def test_slab_3_marcus_invariant_stub_present() -> None:
    path = Path("_bmad-output/implementation-artifacts/slab-3-marcus-invariant-stub.md")
    text = path.read_text(encoding="utf-8")

    assert path.is_file()
    entries = re.findall(r"^- \*\*[^*]+\*\*:", text, flags=re.MULTILINE)
    assert len(entries) >= 6
    assert "Marcus" in text
    assert "OperatorVerdict" in text
