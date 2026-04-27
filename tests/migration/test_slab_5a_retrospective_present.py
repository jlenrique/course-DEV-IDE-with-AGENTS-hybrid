from __future__ import annotations

import re
from pathlib import Path


def test_slab_5a_retrospective_exists_with_required_sections_and_verdicts() -> None:
    retrospective_path = Path("_bmad-output/implementation-artifacts/slab-5a-retrospective.md")
    text = retrospective_path.read_text(encoding="utf-8")
    next_slab_section = re.search(
        r"^## Next-Slab Preparation(?P<body>.*?)(?:^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert retrospective_path.is_file()
    for header in (
        "## Pre-Audit Bundle",
        "## Slab Outcomes",
        "## Next-Slab Preparation",
        "## Slab 5b Handoff",
    ):
        assert re.search(rf"^{re.escape(header)}", text, flags=re.MULTILINE)
    assert "deferred-inventory.md" in text
    assert next_slab_section is not None
    verdicts = re.findall(
        r"[235][a-z0-9\.-]*[-a-z0-9 ]+:\s*"
        r"(?:RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE)",
        next_slab_section.group("body"),
    )
    assert len(verdicts) >= 3
    assert "5a-5-m5-conditional-window-2026-05-03: DEFERRED-CONTINUES" in (
        next_slab_section.group("body")
    )


def test_slab_5a_retrospective_handoff_section_present() -> None:
    text = Path("_bmad-output/implementation-artifacts/slab-5a-retrospective.md").read_text(
        encoding="utf-8"
    )

    assert "## Slab 5b Handoff" in text
    assert "SHIP-CONDITIONAL" in text
