from __future__ import annotations

import re
from pathlib import Path


def test_5a_2_parity_evidence_present() -> None:
    matches = sorted(
        Path("_bmad-output/implementation-artifacts").glob("5a-2-parity-evidence-*.md")
    )
    assert matches, "expected 5a-2 parity evidence markdown"
    text = matches[0].read_text(encoding="utf-8")
    assert "## Tier 1" in text
    assert "## Tier 2" in text

    tier1 = re.search(r"TIER 1 Score: (?P<score>\d+)% .*threshold: (?P<threshold>\d+)%", text)
    tier2 = re.search(r"TIER 2 Score: (?P<score>\d+)% .*threshold: (?P<threshold>\d+)%", text)
    assert tier1 is not None
    assert tier2 is not None
    assert int(tier1.group("score")) >= int(tier1.group("threshold"))
    assert int(tier2.group("score")) >= int(tier2.group("threshold"))
