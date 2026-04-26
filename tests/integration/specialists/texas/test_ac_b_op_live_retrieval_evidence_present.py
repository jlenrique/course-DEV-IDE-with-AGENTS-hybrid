from __future__ import annotations

import re
from pathlib import Path


def test_texas_live_retrieval_evidence_block_present() -> None:
    verdict = Path("_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md")
    text = verdict.read_text(encoding="utf-8")
    section = re.search(
        r"^## Texas AC-B-OP Live Evidence(?P<body>.*?)(?:^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert section is not None
    for marker in ("M1:", "M2:", "M3:", "M4:", "M5:"):
        assert marker in section.group("body")
    assert "DEFERRED-PENDING-OPERATOR-WINDOW" in section.group("body")
