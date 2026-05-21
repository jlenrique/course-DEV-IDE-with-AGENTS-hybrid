from __future__ import annotations

import re
from pathlib import Path

VERDICT = Path("_bmad-output/implementation-artifacts/slab-4-m4-acceptance-verdict.md")
AGENTS = ("Winston", "Murat", "Paige", "Quinn-R", "Amelia")
PER_AGENT = r"GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED|ABSTAIN"


def _agent_section(text: str, agent: str) -> str:
    match = re.search(
        rf"^### {re.escape(agent)}\n(?P<body>.*?)(?=^### |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, agent
    return match.group("body")


def test_slab_4_party_mode_5_agent_recording() -> None:
    text = VERDICT.read_text(encoding="utf-8")
    party = re.search(
        r"^## Party-Mode Verdict \(5 agents\)\n(?P<body>.*)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    assert VERDICT.is_file()
    assert party is not None
    assert re.search(
        r"^Consensus verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED)$",
        party.group("body"),
        flags=re.MULTILINE,
    )
    for agent in AGENTS:
        body = _agent_section(text, agent)
        verdict_lines = re.findall(rf"^Verdict: ({PER_AGENT})$", body, flags=re.MULTILINE)
        assert len(verdict_lines) == 1, agent
        body_without_verdict = re.sub(rf"^Verdict: ({PER_AGENT})$", "", body, flags=re.MULTILINE)
        assert len(body_without_verdict.strip()) >= 150, agent

