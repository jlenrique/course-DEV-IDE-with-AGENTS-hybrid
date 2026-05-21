from __future__ import annotations

import re
from pathlib import Path

import pytest


def _parse_consensus_verdict() -> str:
    text = Path("_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md").read_text(
        encoding="utf-8"
    )
    match = re.search(r"^Consensus verdict:\s*(\S+)", text, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


def _parse_sprint_status_with_comment(key: str) -> tuple[str, str]:
    text = Path("_bmad-output/implementation-artifacts/sprint-status.yaml").read_text(
        encoding="utf-8"
    )
    match = re.search(rf"^\s*{re.escape(key)}:\s*(\S+)(?:\s*#\s*(.*))?$", text, re.MULTILINE)
    assert match is not None
    return match.group(1), match.group(2) or ""


def test_slab_2c_close_state_matches_2c3_m2_verdict() -> None:
    verdict = _parse_consensus_verdict()
    sprint_state, sprint_comment = _parse_sprint_status_with_comment(
        "migration-epic-2c-slab-2-wondercraft-pilot"
    )

    assert sprint_state == "done"
    if verdict == "GREEN-LIGHT":
        assert "GREEN-LIGHT" in sprint_comment
        assert "CONDITIONAL" not in sprint_comment
    elif verdict == "CONDITIONAL-GREEN":
        assert "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM" in sprint_comment
        assert "2c-3-m2-verdict-conditional-on-2c-2-live-artifact" in sprint_comment
    else:
        pytest.fail(f"verdict {verdict} not in {{GREEN-LIGHT, CONDITIONAL-GREEN}}")
