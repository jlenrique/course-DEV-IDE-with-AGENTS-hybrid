"""Hermetic tests for Agentic Research Foundations R1 — posture-aware selector."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.orchestrator.research_wiring import (
    DeterministicPostureSelector,
    RESEARCH_DETECTIVE_LIVE_ENV,
    resolve_research_posture,
)
from skills.bmad_agent_tracy.scripts.posture_dispatcher import PostureDispatcher

_SMOKE_DIR = (
    Path(__file__).resolve().parents[3]
    / "fixtures"
    / "retrieval"
    / "tracy_smoke"
)


def _load_smoke_brief(fixture_id: str) -> dict:
    path = _SMOKE_DIR / f"{fixture_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return dict(payload["brief"])


class TestResolveResearchPosture:
    def test_claim_maps_to_corroborate(self) -> None:
        assert (
            resolve_research_posture({"claim": "X improves Y"}) == "corroborate"
        )

    def test_enrichment_maps_to_embellish(self) -> None:
        assert (
            resolve_research_posture(
                {"gap_type": "enrichment", "enrichment_type": "examples"}
            )
            == "embellish"
        )

    def test_research_goal_defaults_to_gap_fill(self) -> None:
        assert (
            resolve_research_posture(
                {
                    "gap_description": "Need background on cognitive load",
                    "research_goal_id": "rg-1",
                }
            )
            == "gap_fill"
        )

    def test_smoke_fixtures_resolve(self) -> None:
        assert (
            resolve_research_posture(_load_smoke_brief("corroborate_supporting"))
            == "corroborate"
        )
        assert (
            resolve_research_posture(_load_smoke_brief("gap_fill_background"))
            == "gap_fill"
        )
        assert (
            resolve_research_posture(_load_smoke_brief("embellish_examples"))
            == "embellish"
        )


class TestFlagOffBitIdentical:
    def test_flag_off_preserves_legacy_intent_text(self, monkeypatch) -> None:
        monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)
        selector = DeterministicPostureSelector()
        brief = {"gap_description": "trend evidence", "target_element": "u1"}
        intent = selector.select_posture(brief)
        assert intent.intent == (
            "Find evidence for research-enrichment gap on u1: trend evidence"
        )
        assert intent.provider_hints[0].params == {"mode": "search"}
        assert "posture" not in intent.provider_hints[0].params

    def test_flag_off_preserves_research_goal_provenance_only(
        self, monkeypatch
    ) -> None:
        monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)
        selector = DeterministicPostureSelector()
        intent = selector.select_posture(
            {
                "gap_description": "pedagogical seed",
                "target_element": "LO-1",
                "research_goal_id": "rg-tejal-1",
            }
        )
        assert intent.provider_hints[0].params == {
            "mode": "search",
            "research_goal_id": "rg-tejal-1",
        }


class TestDetectiveOnPostureAware:
    @pytest.fixture(autouse=True)
    def _enable_detective(self, monkeypatch) -> None:
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")

    def test_corroborate_smoke_brief(self) -> None:
        selector = DeterministicPostureSelector()
        brief = _load_smoke_brief("corroborate_supporting")
        intent = selector.select_posture(brief)
        assert intent.intent.startswith("Corroborate claim:")
        assert intent.provider_hints[0].params["posture"] == "corroborate"
        assert intent.provider_hints[0].provider == "scite"

    def test_gap_fill_smoke_brief(self) -> None:
        selector = DeterministicPostureSelector()
        brief = _load_smoke_brief("gap_fill_background")
        intent = selector.select_posture(brief)
        assert intent.intent.startswith("Fill research gap")
        assert intent.provider_hints[0].params["posture"] == "gap_fill"

    def test_embellish_smoke_brief(self) -> None:
        selector = DeterministicPostureSelector()
        brief = _load_smoke_brief("embellish_examples")
        intent = selector.select_posture(brief)
        assert intent.intent.startswith("Embellish")
        assert intent.provider_hints[0].params["posture"] == "embellish"


class TestPostureDispatcherFacade:
    def test_three_postures_emit_retrieval_intents(self, monkeypatch) -> None:
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
        dispatcher = PostureDispatcher()
        emb = dispatcher.embellish("gagne-event-02", "examples")
        cor = dispatcher.corroborate(
            "Worked examples improve novice transfer.",
            "Need supporting citation.",
        )
        gap = dispatcher.gap_fill(
            "Missing prerequisite explanation.",
            "background",
            "unit",
        )
        assert emb.provider_hints[0].params["posture"] == "embellish"
        assert cor.provider_hints[0].params["posture"] == "corroborate"
        assert gap.provider_hints[0].params["posture"] == "gap_fill"
        assert all(h.provider == "scite" for h in emb.provider_hints)

    def test_select_posture_delegates_to_selector(self, monkeypatch) -> None:
        monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)
        dispatcher = PostureDispatcher()
        intent = dispatcher.select_posture(
            {"gap_description": "x", "target_element": "u1"}
        )
        assert "Find evidence for research-enrichment gap" in intent.intent
