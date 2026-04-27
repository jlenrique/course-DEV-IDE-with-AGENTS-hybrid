from __future__ import annotations

import re
from pathlib import Path

VERDICT = Path("_bmad-output/implementation-artifacts/m5-decision.md")
SPRINT_STATUS = Path("_bmad-output/implementation-artifacts/sprint-status.yaml")
DEFERRED = Path("_bmad-output/planning-artifacts/deferred-inventory.md")


def _parse_consensus_verdict(text: str) -> str:
    match = re.search(
        r"^Consensus verdict: (SHIP|ITERATE|ROLLBACK|SHIP-WITH-RIDERS|SHIP-CONDITIONAL)$",
        text,
        flags=re.MULTILINE,
    )
    assert match is not None
    return match.group(1)


def _parse_sprint_status_with_comment(text: str, key: str) -> tuple[str, str]:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(\S+)(?:\s*#\s*(.*))?$", text, re.MULTILINE)
    assert match is not None, key
    return match.group(1), match.group(2) or ""


def test_m5_verdict_consequence_path() -> None:
    verdict_text = VERDICT.read_text(encoding="utf-8")
    sprint_text = SPRINT_STATUS.read_text(encoding="utf-8")
    deferred_text = DEFERRED.read_text(encoding="utf-8")

    verdict = _parse_consensus_verdict(verdict_text)
    story_status, _ = _parse_sprint_status_with_comment(
        sprint_text, "migration-5a-5-m5-ship-decision-and-slab-close"
    )
    epic_status, epic_comment = _parse_sprint_status_with_comment(
        sprint_text, "migration-epic-5a-acceptance"
    )
    master_status, master_comment = _parse_sprint_status_with_comment(
        sprint_text, "migration-master-status"
    )

    assert story_status == "done"
    assert epic_status == "done"

    if verdict == "SHIP":
        assert Path("_bmad-output/upstream-state.md").is_file()
        assert master_status == "shipped"
    elif verdict == "SHIP-WITH-RIDERS":
        assert Path("_bmad-output/upstream-state.md").is_file()
        assert Path("_bmad-output/implementation-artifacts/m5-ship-riders.md").is_file()
        assert master_status == "shipped"
    elif verdict == "SHIP-CONDITIONAL":
        assert Path("_bmad-output/upstream-state.md").is_file()
        assert "`5a-5-m5-conditional-window-2026-05-03`" in deferred_text
        assert master_status == "shipped"
        assert "SHIP-CONDITIONAL" in epic_comment
        assert "2026-05-03" in master_comment
    elif verdict == "ITERATE":
        assert master_status == "iterate-pending"
        assert re.search(r"migration-5a-5-iter-\d+-", sprint_text)
    elif verdict == "ROLLBACK":
        assert master_status == "rolled-back"
    else:
        raise AssertionError(f"Unhandled verdict {verdict}")
