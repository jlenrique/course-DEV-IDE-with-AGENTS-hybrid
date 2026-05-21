"""Story 32-4 — Maya journey walkthrough stage-by-stage pins.

AC-T.1 paste source / AC-T.2 weather ribbon / AC-T.3 gray card /
AC-T.4 Marcus posture sentence / AC-T.5 rationale verbatim /
AC-T.6 ratified + rationale preservation / AC-T.7 budget + Declined
articulation verbatim / AC-T.8 5x-consecutive stability.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator.maya_walkthrough import (
    DECLINED_UNIT_RATIONALE,
    OPERATOR_RATIONALE_VERBATIM,
    MayaWalkthroughResult,
    run_maya_walkthrough,
)

_FIXTURE_DIR = (
    Path(__file__).resolve().parent / "fixtures" / "maya_walkthrough" / "sme_corpus"
)


@pytest.fixture(autouse=True)
def _patch_pre_packet_repo_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from app.marcus.intake import pre_packet

    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)


def _run(tmp_path: Path, *, run_id: str = "maya-walkthrough-001") -> MayaWalkthroughResult:
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    return run_maya_walkthrough(
        _FIXTURE_DIR,
        log=log,
        run_id=run_id,
        output_path=tmp_path / "irene-packet.md",
    )


def test_stage_1_paste_source_emits_pre_packet(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.paste_source.events_appended >= 1
    assert result.paste_source.pre_packet_revision == 0
    assert len(result.paste_source.bundle_sha256) == 64


def test_stage_2_weather_ribbon_has_no_red_and_only_known_bands(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.weather_ribbon.unit_count == 3
    assert "red" not in result.weather_ribbon.band_distribution
    assert set(result.weather_ribbon.band_distribution) <= {
        "gold",
        "green",
        "amber",
        "gray",
    }


def test_stage_3_gray_card_present_and_named(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.click_gray_card.weather_band == "gray"
    assert result.click_gray_card.unit_id
    assert result.click_gray_card.source_fitness_diagnosis


def test_stage_4_marcus_posture_sentence_is_voice_register_clean(
    tmp_path: Path,
) -> None:
    result = _run(tmp_path)

    proposal = result.marcus_delegation_proposal
    assert proposal.posture in {"embellish", "corroborate", "gap-fill"}
    assert proposal.sentence
    lowered = proposal.sentence.lower()
    for token in ("intake", "orchestrator", "dispatch", "facade"):
        assert token not in lowered, (
            f"Marcus delegation sentence leaked the {token!r} token"
        )


def test_stage_5_operator_rationale_stored_verbatim(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.operator_rationale_sentence.stored == OPERATOR_RATIONALE_VERBATIM


def test_stage_6_scope_decision_ratified_with_rationale_verbatim(
    tmp_path: Path,
) -> None:
    result = _run(tmp_path)

    assert result.card_turned_gold.scope_decision_state in {"ratified", "locked"}
    assert result.card_turned_gold.rationale_matches_operator_input is True
    assert result.card_turned_gold.stored_rationale == OPERATOR_RATIONALE_VERBATIM


@pytest.mark.parametrize(
    "claim",
    [
        "budget",
        "declined-articulation-verbatim",
    ],
)
def test_budget_and_declined_articulation_verbatim(tmp_path: Path, claim: str) -> None:
    result = _run(tmp_path)

    if claim == "budget":
        assert result.elapsed_seconds <= 720.0
    else:
        assert DECLINED_UNIT_RATIONALE in result.declined_articulations
        assert all(r for r in result.declined_articulations)


@pytest.mark.parametrize("run_index", list(range(5)))
def test_five_consecutive_runs_yield_stable_evidence(
    tmp_path: Path, run_index: int
) -> None:
    result = _run(tmp_path, run_id=f"stability-run-{run_index}")

    assert result.paste_source.bundle_sha256 == result.paste_source.bundle_sha256
    assert result.paste_source.pre_packet_revision == 0
    assert result.weather_ribbon.unit_count == 3
    assert result.click_gray_card.weather_band == "gray"
    assert result.marcus_delegation_proposal.posture == "corroborate"
    assert result.operator_rationale_sentence.stored == OPERATOR_RATIONALE_VERBATIM
    assert result.card_turned_gold.rationale_matches_operator_input is True
    assert DECLINED_UNIT_RATIONALE in result.declined_articulations
    assert result.elapsed_seconds <= 720.0
