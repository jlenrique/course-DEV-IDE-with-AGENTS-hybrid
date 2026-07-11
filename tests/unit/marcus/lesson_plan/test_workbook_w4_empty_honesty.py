"""Hermetic pin for W4 detective-OFF empty honesty (live arm is primary)."""

from __future__ import annotations

import os
from pathlib import Path

from app.marcus.lesson_plan.glossary_projection import glossary_inputs_from_run
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
