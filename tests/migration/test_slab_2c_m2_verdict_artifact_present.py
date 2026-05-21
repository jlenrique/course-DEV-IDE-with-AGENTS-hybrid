from __future__ import annotations

import re
from pathlib import Path

VERDICT = Path("_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md")


def _section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    assert match is not None, heading
    return match.group("body")


def _table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] != "Anchor":
            rows.append(cells)
    return rows


def test_m2_verdict_artifact_has_time_to_deploy_math() -> None:
    assert VERDICT.is_file()
    text = VERDICT.read_text(encoding="utf-8")
    section = _section(text, "Time-to-Deploy Measurement")
    rows = _table_rows(section)
    assert len(rows) >= 11
    assert any(row[0] == "T_first_real_artifact" and "DEFERRED" in row[2] for row in rows)

    cumulative_values = [float(row[4]) for row in rows]
    delta_sum = sum(float(row[3]) for row in rows)
    final_cumulative = cumulative_values[-1]
    assert abs(delta_sum - final_cumulative) <= 0.1

    summary = _section(text, "M2 Required Evidence Summary")
    verdict_line = re.search(
        r"^Time-to-deploy verdict: "
        r"(GREEN-LIGHT|CONDITIONAL-GREEN|YELLOW|RED) "
        r"\((?P<hours>[0-9.]+) active hours\)",
        summary,
        flags=re.MULTILINE,
    )
    assert verdict_line is not None
    hours = float(verdict_line.group("hours"))
    expected = "CONDITIONAL-GREEN" if "DEFERRED-PENDING-OPERATOR-WINDOW" in summary else (
        "GREEN-LIGHT" if hours <= 6 else "YELLOW" if hours <= 8 else "RED"
    )
    assert verdict_line.group(1) == expected
