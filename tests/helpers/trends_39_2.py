"""Shared 39.2 test substrate — Door-Ajar (Research Trends) section helpers.

The frozen ``u01@1.rendered-workbook.md`` fixture carries the PRE-39.2 trends
section (populated from the retired generic ``04.55`` read). Post-re-point the
runner's ``_assert_trends_door_ajar_conformant`` clause recomputes the brief
from the run's Ask-B packet (``ask_b_hot_topics@07W.4``) — so conforming rigs
swap the fixture section for the recomputed render, exactly like the 39.1
``swap_glossary_section`` precedent (the fixture file itself stays frozen /
digest-pinned; the swap happens on the in-memory copy).

The REAL frozen Ask-B pack (M-5 fixture grounding) is the digest-bound extract
of the ``ask_b_hot_topics@07W.4`` contribution from the 38-2 probe attempt
``79f1920e`` evidence run — mutants derive from it, never hand-invented.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.trends_projection import (
    render_trends_markdown,
    trends_inputs_from_run,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_ASK_B_RUN_JSON = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "ask-b-38-2-live-79f1920e"
    / "run"
    / "run.json"
)
# Digest-bound (M-5): the frozen contribution's own ``output_digest`` as
# recorded in the evidence pack — extraction asserts it so silent drift of the
# frozen pack fails loud here, not downstream.
FROZEN_ASK_B_OUTPUT_DIGEST = (
    "a10c67b950558fe677091204de1c5ff438d78a28d4e15f4f8d2356ab5dbc6b55"
)

_TRENDS_HEADING = "## Research Trends"


def frozen_ask_b_output() -> dict[str, Any]:
    """The REAL ``ask_b_hot_topics@07W.4`` contribution output (digest-bound
    extract of the frozen 79f1920e pack; M-5)."""
    trial = json.loads(FROZEN_ASK_B_RUN_JSON.read_text(encoding="utf-8"))
    envelope = trial.get("production_envelope", trial)
    matches = [
        contribution
        for contribution in envelope["contributions"]
        if contribution["specialist_id"] == "ask_b_hot_topics"
        and contribution.get("node_id") == "07W.4"
    ]
    assert len(matches) == 1, "frozen pack must carry exactly one Ask-B contribution"
    assert matches[0]["output_digest"] == FROZEN_ASK_B_OUTPUT_DIGEST, (
        "frozen 79f1920e Ask-B extract drifted from its recorded output_digest"
    )
    return matches[0]["output"]


def conforming_trends_body(run_dir: Path) -> str:
    """The recomputed Door-Ajar section body for ``run_dir`` — the same
    deterministic recompute authority the 39.2 bar clause asserts against."""
    return render_trends_markdown(trends_inputs_from_run(run_dir))


def swap_trends_section(markdown: str, run_dir: Path) -> str:
    """Replace the fixture MD's (pre-39.2) trends section with the conforming
    recomputed render for ``run_dir`` — the fixture file itself stays frozen
    (digest-pinned); the swap happens on the in-memory copy."""
    body = conforming_trends_body(run_dir)
    pattern = re.compile(
        rf"(\n{re.escape(_TRENDS_HEADING)}\n)(.*?)(?=\n## )", re.DOTALL
    )
    replaced, count = pattern.subn(lambda m: f"{m.group(1)}\n{body}\n", markdown)
    if count != 1:
        raise AssertionError(
            "fixture markdown must carry exactly one Research Trends section"
        )
    return replaced
