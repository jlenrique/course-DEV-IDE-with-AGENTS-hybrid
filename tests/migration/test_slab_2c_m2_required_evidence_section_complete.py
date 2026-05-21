from __future__ import annotations

import re
from pathlib import Path

VERDICT = Path("_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md")


def test_m2_required_evidence_section_complete() -> None:
    text = VERDICT.read_text(encoding="utf-8")
    match = re.search(
        r"^## M2 Required Evidence Summary\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    body = match.group("body")
    assert re.search(
        r"^Time-to-deploy verdict: (GREEN-LIGHT|CONDITIONAL-GREEN|YELLOW|RED)",
        body,
        flags=re.MULTILINE,
    )
    for prefix in (
        "Cost summary:",
        "Diff-evidence verdict:",
        "Conformance-green verdict:",
    ):
        assert re.search(rf"^{re.escape(prefix)}", body, flags=re.MULTILINE)
