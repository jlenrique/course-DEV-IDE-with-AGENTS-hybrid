"""Hermetic tests for Agentic Research Foundations R2 — evidence bolster."""

from __future__ import annotations

import pytest

from app.marcus.orchestrator.research_wiring import (
    DeterministicPostureSelector,
    EVIDENCE_BOLSTER_ENV,
    RESEARCH_DETECTIVE_LIVE_ENV,
    evidence_bolster_active,
)
from skills.bmad_agent_tracy.scripts.posture_dispatcher import PostureDispatcher


class TestEvidenceBolsterKnob:
    def test_default_off(self, monkeypatch) -> None:
        monkeypatch.delenv(EVIDENCE_BOLSTER_ENV, raising=False)
        assert evidence_bolster_active() is False
        assert evidence_bolster_active({}) is False

    def test_brief_true_wins_over_env_false(self, monkeypatch) -> None:
        monkeypatch.delenv(EVIDENCE_BOLSTER_ENV, raising=False)
        assert evidence_bolster_active({"evidence_bolster": True}) is True

    def test_env_on(self, monkeypatch) -> None:
        monkeypatch.setenv(EVIDENCE_BOLSTER_ENV, "1")
        assert evidence_bolster_active() is True


class TestBolsterCorroborateSelector:
    def test_bolster_off_corroborate_stays_scite_only(self, monkeypatch) -> None:
        monkeypatch.delenv(EVIDENCE_BOLSTER_ENV, raising=False)
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
        intent = DeterministicPostureSelector().select_posture(
            {
                "claim": "Worked examples improve novice transfer.",
                "source_context": "need cite",
                "evidence_bolster": False,
            }
        )
        assert [h.provider for h in intent.provider_hints] == ["scite"]
        assert intent.cross_validate is False

    def test_bolster_on_corroborate_scite_and_consensus(self, monkeypatch) -> None:
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
        intent = DeterministicPostureSelector().select_posture(
            {
                "claim": "Worked examples improve novice transfer.",
                "source_context": "need cite",
                "evidence_bolster": True,
            }
        )
        named = [h.provider for h in intent.provider_hints]
        assert named == ["scite", "consensus"]
        assert intent.cross_validate is True
        assert all(h.params.get("evidence_bolster") is True for h in intent.provider_hints)
        assert all(h.params.get("posture") == "corroborate" for h in intent.provider_hints)

    def test_bolster_on_gap_fill_stays_scite_only(self, monkeypatch) -> None:
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
        intent = DeterministicPostureSelector().select_posture(
            {
                "gap_description": "Need background on cognitive load",
                "evidence_bolster": True,
            }
        )
        assert [h.provider for h in intent.provider_hints] == ["scite"]
        assert intent.cross_validate is False

    def test_flag_off_bolster_off_bit_identical(self, monkeypatch) -> None:
        monkeypatch.delenv(RESEARCH_DETECTIVE_LIVE_ENV, raising=False)
        monkeypatch.delenv(EVIDENCE_BOLSTER_ENV, raising=False)
        intent = DeterministicPostureSelector().select_posture(
            {"gap_description": "trend evidence", "target_element": "u1"}
        )
        assert intent.intent == (
            "Find evidence for research-enrichment gap on u1: trend evidence"
        )
        assert [h.provider for h in intent.provider_hints] == ["scite"]
        assert intent.provider_hints[0].params == {"mode": "search"}


class TestPostureDispatcherBolster:
    def test_corroborate_bolster_kwarg(self, monkeypatch) -> None:
        monkeypatch.setenv(RESEARCH_DETECTIVE_LIVE_ENV, "1")
        intent = PostureDispatcher().corroborate(
            "claim text",
            "context",
            evidence_bolster=True,
        )
        assert [h.provider for h in intent.provider_hints] == ["scite", "consensus"]
        assert intent.cross_validate is True
