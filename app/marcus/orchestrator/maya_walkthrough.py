"""Maya journey walkthrough — Story 32-4.

Drives the landed MVP chain through a canned 7-page SME fixture and records
stage-by-stage evidence against Sally's R1 amendment 4 pantomime AC:

    Maya pastes source, sees weather ribbon, clicks a gray card, Marcus proposes
    delegation, Maya types one sentence, card turns gold.

Maya-facing note
----------------

Maya sees one Marcus. This module exists for release-gate ceremony; it does
not route user-facing traffic and does not surface its internal seams.

Developer discipline note
-------------------------

* No new schema shape. :class:`MayaWalkthroughResult` is an in-module result
  container; none of its sub-models are exported through
  :mod:`marcus.lesson_plan`.
* Zero new Lesson Plan log events. The walkthrough reads through existing
  seams (``prepare_and_emit_irene_packet``, :meth:`Facade.run_4a`,
  :func:`render_retrieval_narration`) and emits nothing beyond what those
  functions already emit.
* Pantomime stage 6 ("card turns gold") pins the observable system-level
  invariant — ``scope_decision.state == "ratified"`` + rationale verbatim —
  not a :attr:`PlanUnit.weather_band` mutation. The MVP does not auto-mutate
  ``weather_band``; gold rendering is a downstream UI concern.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.facade import get_facade
from app.marcus.intake.pre_packet import prepare_and_emit_irene_packet
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.retrieval_narration_grammar import render_retrieval_narration
from app.marcus.lesson_plan.schema import (
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)
from app.marcus.orchestrator.dispatch import dispatch_intake_pre_packet

__all__ = (
    "CardTurnedGoldEvidence",
    "ClickGrayCardEvidence",
    "MarcusDelegationProposal",
    "MayaWalkthroughError",
    "MayaWalkthroughResult",
    "OperatorRationaleSentence",
    "PasteSourceEvidence",
    "WeatherRibbonEvidence",
    "run_maya_walkthrough",
)

# ---------------------------------------------------------------------------
# Canned pantomime contract
# ---------------------------------------------------------------------------

OPERATOR_RATIONALE_VERBATIM: Final[str] = (
    "I want students to feel like they've earned the moment of realization, "
    "not had it handed to them."
)
"""Sally's pantomime stage-5 operator sentence, stored byte-for-byte."""

DECLINED_UNIT_RATIONALE: Final[str] = (
    "This section is about assessment theory, not the sensing loop — "
    "out of scope for this lesson."
)
"""Pre-scripted rationale for the out-of-scope unit (§6-C articulation pin)."""

_CANNED_TRACY_RESULT: Final[dict[str, Any]] = {
    "status": "success",
    "posture": "corroborate",
    "output": {"classification": "supporting"},
}
"""Canned Tracy posture result used for stage-4 delegation narration."""

_GRAY_UNIT_ID: Final[str] = "u-sensing-loop"
_GREEN_UNIT_ID: Final[str] = "u-techniques"
_DECLINED_UNIT_ID: Final[str] = "u-assessment-theory"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Stage-evidence models
# ---------------------------------------------------------------------------


class MayaWalkthroughError(ValueError):
    """Raised when a walkthrough stage invariant fails.

    The error message is Maya-safe: no Intake / Orchestrator / dispatch /
    facade / loop tokens; first-person where applicable; terminates with
    an invitation to re-run.
    """


class PasteSourceEvidence(BaseModel):
    """Stage 1 evidence — pre-packet snapshot emission."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bundle_sha256: str = Field(..., min_length=1)
    pre_packet_revision: int = Field(..., ge=0)
    events_appended: int = Field(..., ge=1)


class WeatherRibbonEvidence(BaseModel):
    """Stage 2 evidence — weather ribbon populated with no-red discipline."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unit_count: int = Field(..., ge=1)
    band_distribution: dict[str, int]

    @field_validator("band_distribution")
    @classmethod
    def _reject_red_and_unknowns(cls, value: dict[str, int]) -> dict[str, int]:
        allowed = {"gold", "green", "amber", "gray"}
        if "red" in value:
            raise ValueError(
                "weather ribbon must not carry a 'red' band (Sally's no-red rule)"
            )
        leaks = set(value) - allowed
        if leaks:
            raise ValueError(
                f"weather ribbon carries unknown band(s) {sorted(leaks)}; "
                f"allowed bands are {sorted(allowed)}"
            )
        return value


class ClickGrayCardEvidence(BaseModel):
    """Stage 3 evidence — Maya selects a gray unit."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unit_id: str = Field(..., min_length=1)
    weather_band: Literal["gray"]
    source_fitness_diagnosis: str = Field(..., min_length=1)


class MarcusDelegationProposal(BaseModel):
    """Stage 4 evidence — Marcus's posture sentence for the gray card."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    posture: Literal["embellish", "corroborate", "gap-fill"]
    sentence: str = Field(..., min_length=1)


class OperatorRationaleSentence(BaseModel):
    """Stage 5 evidence — operator rationale stored byte-for-byte."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stored: str = Field(..., min_length=1)


class CardTurnedGoldEvidence(BaseModel):
    """Stage 6 evidence — ratified scope-decision + rationale verbatim.

    ``weather_band_observed`` is recorded for operator-debug observability
    only. The MVP does not auto-mutate ``weather_band``; UI rendering of
    "gold" is the downstream layer's responsibility.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    unit_id: str = Field(..., min_length=1)
    weather_band_observed: Literal["gold", "green", "amber", "gray"]
    scope_decision_state: Literal["ratified", "locked"]
    stored_rationale: str
    rationale_matches_operator_input: bool


class MayaWalkthroughResult(BaseModel):
    """Aggregate result of :func:`run_maya_walkthrough`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    paste_source: PasteSourceEvidence
    weather_ribbon: WeatherRibbonEvidence
    click_gray_card: ClickGrayCardEvidence
    marcus_delegation_proposal: MarcusDelegationProposal
    operator_rationale_sentence: OperatorRationaleSentence
    card_turned_gold: CardTurnedGoldEvidence
    declined_articulations: tuple[str, ...]
    started_at: datetime
    ended_at: datetime
    elapsed_seconds: float = Field(..., ge=0.0)

    @field_validator("started_at", "ended_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("walkthrough timestamps must be timezone-aware (UTC)")
        return value


# ---------------------------------------------------------------------------
# Canned plan builder
# ---------------------------------------------------------------------------


def _build_canned_plan() -> LessonPlan:
    """Build the canned plan pinned to the pantomime AC stages."""
    now = datetime.now(tz=UTC)
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id=_GREEN_UNIT_ID,
                event_type="gagne-event-present-content",
                source_fitness_diagnosis=(
                    "Source covers the four low-cognitive-load techniques in "
                    "Section 3; directly answers this plan unit."
                ),
                weather_band="green",
                rationale="",
            ),
            PlanUnit(
                unit_id=_GRAY_UNIT_ID,
                event_type="gagne-event-stimulate-recall",
                source_fitness_diagnosis=(
                    "Source gestures at the sensing loop in Section 6 but "
                    "stops short of naming the habit-cycle; Marcus leans in "
                    "with one delegated corroboration."
                ),
                weather_band="gray",
                rationale="",
            ),
            PlanUnit(
                unit_id=_DECLINED_UNIT_ID,
                event_type="gagne-event-assess-performance",
                source_fitness_diagnosis=(
                    "Source is about formative sensing, not summative "
                    "assessment theory; explicitly out of Maya's lesson focus."
                ),
                weather_band="amber",
                rationale="",
            ),
        ],
        revision=0,
        updated_at=now,
    )
    return plan


def _canned_intake_callable(
    _state: Any,
    unit_id: str,
) -> tuple[ScopeDecision, str]:
    """Pre-scripted Maya responses per pantomime unit."""
    if unit_id == _GRAY_UNIT_ID:
        decision = ScopeDecision(
            state="ratified",
            scope="delegated",
            proposed_by="operator",
            ratified_by="maya",
        )
        return decision, OPERATOR_RATIONALE_VERBATIM
    if unit_id == _GREEN_UNIT_ID:
        decision = ScopeDecision(
            state="ratified",
            scope="in-scope",
            proposed_by="operator",
            ratified_by="maya",
        )
        return decision, ""
    raise MayaWalkthroughError(
        "I hit a unit I wasn't expecting during this walkthrough. "
        "Could you re-run the canned fixture from a clean bundle?"
    )


# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------


def _stage_1_paste_source(
    fixture_dir: Path,
    *,
    log: LessonPlanLog,
    run_id: str,
    output_path: Path,
) -> PasteSourceEvidence:
    events_before = sum(1 for _ in log.read_events())
    bundle_sha256 = hashlib.sha256(
        (fixture_dir / "extracted.md").read_bytes()
    ).hexdigest()
    dispatch = partial(dispatch_intake_pre_packet, log=log)
    prepare_and_emit_irene_packet(
        fixture_dir,
        run_id,
        output_path,
        dispatch=dispatch,
        plan_revision=0,
    )
    events_after = sum(1 for _ in log.read_events())
    events_appended = events_after - events_before
    if events_appended < 1:
        raise MayaWalkthroughError(
            "I didn't see your source land in the log. "
            "Could you re-run the walkthrough from a clean bundle?"
        )
    return PasteSourceEvidence(
        bundle_sha256=bundle_sha256,
        pre_packet_revision=0,
        events_appended=events_appended,
    )


def _stage_2_weather_ribbon(plan: LessonPlan) -> WeatherRibbonEvidence:
    band_distribution: dict[str, int] = {}
    for unit in plan.plan_units:
        band_distribution[unit.weather_band] = (
            band_distribution.get(unit.weather_band, 0) + 1
        )
    return WeatherRibbonEvidence(
        unit_count=len(plan.plan_units),
        band_distribution=band_distribution,
    )


def _stage_3_click_gray_card(plan: LessonPlan) -> ClickGrayCardEvidence:
    for unit in plan.plan_units:
        if unit.weather_band == "gray":
            return ClickGrayCardEvidence(
                unit_id=unit.unit_id,
                weather_band="gray",
                source_fitness_diagnosis=unit.source_fitness_diagnosis,
            )
    raise MayaWalkthroughError(
        "I couldn't find a gray card in this plan. "
        "Could you re-run the walkthrough from the canned fixture?"
    )


def _stage_4_marcus_delegation() -> MarcusDelegationProposal:
    sentence = render_retrieval_narration(_CANNED_TRACY_RESULT)
    return MarcusDelegationProposal(posture="corroborate", sentence=sentence)


def _stage_5_operator_rationale() -> OperatorRationaleSentence:
    return OperatorRationaleSentence(stored=OPERATOR_RATIONALE_VERBATIM)


def _stage_6_card_turned_gold(locked_plan: LessonPlan) -> CardTurnedGoldEvidence:
    for unit in locked_plan.plan_units:
        if unit.unit_id != _GRAY_UNIT_ID:
            continue
        if unit.scope_decision is None:
            raise MayaWalkthroughError(
                "I never heard a decision on the gray card. "
                "Could you re-run the walkthrough from a clean bundle?"
            )
        return CardTurnedGoldEvidence(
            unit_id=unit.unit_id,
            weather_band_observed=unit.weather_band,
            scope_decision_state=unit.scope_decision.state,
            stored_rationale=unit.rationale,
            rationale_matches_operator_input=(
                unit.rationale == OPERATOR_RATIONALE_VERBATIM
            ),
        )
    raise MayaWalkthroughError(
        "I lost track of the gray card after the lock. "
        "Could you re-run the walkthrough from a clean bundle?"
    )


def _collect_declined_articulations(locked_plan: LessonPlan) -> tuple[str, ...]:
    rationales: list[str] = []
    for unit in locked_plan.plan_units:
        if unit.scope_decision is None:
            continue
        if unit.scope_decision.scope == "out-of-scope":
            rationales.append(unit.rationale)
    return tuple(rationales)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_maya_walkthrough(
    fixture_dir: Path,
    *,
    log: LessonPlanLog | None = None,
    run_id: str = "maya-walkthrough-001",
    output_path: Path | None = None,
) -> MayaWalkthroughResult:
    """Drive the canned Maya pantomime walkthrough and return staged evidence.

    Args:
        fixture_dir: Path to the canned SME bundle (``extracted.md`` +
            ``metadata.json`` + ``operator-directives.md`` + optional
            ``ingestion-quality-gate-receipt.md``). The committed fixture
            lives at ``tests/fixtures/maya_walkthrough/sme_corpus/``.
        log: Optional :class:`LessonPlanLog` for test isolation. Defaults to
            a production log instance.
        run_id: Run identifier surfaced in the pre-packet emission.
        output_path: Where to write the generated irene-packet. Defaults to
            ``state/runtime/maya-walkthrough/<run_id>/irene-packet.md`` under
            the repository root (keeps committed fixtures read-only).

    Returns:
        :class:`MayaWalkthroughResult` — aggregate stage-by-stage evidence.

    Raises:
        MayaWalkthroughError: When any stage invariant is violated.
    """
    target_log = log or LessonPlanLog()
    target_output = output_path or (
        _REPO_ROOT / "state" / "runtime" / "maya-walkthrough" / run_id / "irene-packet.md"
    )

    started_at = datetime.now(tz=UTC)

    paste_source = _stage_1_paste_source(
        fixture_dir,
        log=target_log,
        run_id=run_id,
        output_path=target_output,
    )

    packet_plan = _build_canned_plan()

    weather_ribbon = _stage_2_weather_ribbon(packet_plan)
    click_gray_card = _stage_3_click_gray_card(packet_plan)
    marcus_delegation_proposal = _stage_4_marcus_delegation()
    operator_rationale_sentence = _stage_5_operator_rationale()

    locked_plan = get_facade().run_4a(
        packet_plan,
        intake_callable=_canned_intake_callable,
        prior_declined_rationales=(
            (_DECLINED_UNIT_ID, DECLINED_UNIT_RATIONALE),
        ),
        log=target_log,
    )

    card_turned_gold = _stage_6_card_turned_gold(locked_plan)
    declined_articulations = _collect_declined_articulations(locked_plan)

    ended_at = datetime.now(tz=UTC)
    elapsed_seconds = (ended_at - started_at).total_seconds()
    if elapsed_seconds > 720.0:
        raise MayaWalkthroughError(
            "The walkthrough ran longer than the 12-minute budget. "
            "Could you re-run on a fresh bundle and see if it settles?"
        )

    return MayaWalkthroughResult(
        paste_source=paste_source,
        weather_ribbon=weather_ribbon,
        click_gray_card=click_gray_card,
        marcus_delegation_proposal=marcus_delegation_proposal,
        operator_rationale_sentence=operator_rationale_sentence,
        card_turned_gold=card_turned_gold,
        declined_articulations=declined_articulations,
        started_at=started_at,
        ended_at=ended_at,
        elapsed_seconds=elapsed_seconds,
    )
