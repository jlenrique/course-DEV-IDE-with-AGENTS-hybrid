"""Hermetic pin for W4 detective-OFF empty honesty (live arm is primary).

39.1 pin flip (enumerated in the story diff): the learner-deliverable glossary
path is now the TERM-KEYED projection keyed off the 07W.3 contribution — its
empty honesty (bold-term authority absent) is pinned alongside the legacy
run-level empties (the legacy path survives only for frozen evidence scripts).
"""

from __future__ import annotations

import os
from pathlib import Path

from app.marcus.lesson_plan.glossary_projection import (
    BOLD_TERM_AUTHORITY_ABSENT_REASON,
    glossary_inputs_from_run,
    glossary_projection_from_contribution,
    render_glossary_projection_markdown,
)
from app.marcus.lesson_plan.trends_projection import trends_inputs_from_run
from app.marcus.orchestrator.research_wiring import RESEARCH_DETECTIVE_LIVE_ENV


def test_detective_off_empty_paths_are_honest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)
    assert os.environ.get(RESEARCH_DETECTIVE_LIVE_ENV, "") == ""

    articles, g_reason, _ = glossary_inputs_from_run(tmp_path)
    trends = trends_inputs_from_run(tmp_path)

    assert articles == ()
    assert g_reason is not None
    assert "fabricat" in g_reason.lower() or "empty" in g_reason.lower()
    assert not trends.usable
    assert trends.empty_reason is not None
    assert "fabricat" in trends.empty_reason.lower() or "empty" in trends.empty_reason.lower()


def test_term_keyed_glossary_authority_absent_is_honest() -> None:
    """39.1 (matrix row d): no 07W.3 contribution ⇒ explicitly-empty, never
    fabricated — the reason carries the ``bold-term authority absent`` literal."""
    projection = glossary_projection_from_contribution(None)
    assert projection.authority == "absent"
    assert projection.entries == ()
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in (projection.empty_reason or "")
    assert "fabricat" in (projection.empty_reason or "").lower()
    rendered = render_glossary_projection_markdown(projection)
    assert BOLD_TERM_AUTHORITY_ABSENT_REASON in rendered
    assert "https://doi.org/" not in rendered
