"""Deterministic Gagne diagnostician for Lesson Planner stories (29-2).

This module is Irene-authored behavior that lives in the shared
``app.marcus.lesson_plan`` package because the returned artifact is a shared
transport contract, not a private specialist surface.

Discipline notes:

* 29-2 CONSTRUCTS and VALIDATES :class:`FitReport` instances; it does not write
  them to the log. The fit-report emission seam remains Marcus-Orchestrator's
  canonical caller.
* ``modality_ref`` validity is delegated to 31-3's registry via
  :func:`get_modality_entry`; there is no second modality taxonomy here.
* The diagnostician is intentionally hardcoded to the MVP Gagne-9 seam.
  Unsupported event types fail explicitly rather than being silently
  normalized.
* Duplicate diagnosis targets are rejected here, at construction time,
  instead of relying on 29-1's validator to collapse them.
* The named fallback contract is ``summary-only``. When runtime breaches the
  configured threshold, commentary is rebuilt in a shorter deterministic form
  while preserving one diagnosis per unit and a valid FitReport.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from time import perf_counter
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.event_type_registry import KNOWN_PLAN_UNIT_EVENT_TYPES
from app.marcus.lesson_plan.fit_report import validate_fit_report
from app.marcus.lesson_plan.modality_registry import get_modality_entry
from app.marcus.lesson_plan.schema import (
    FitDiagnosis,
    FitReport,
    LessonPlan,
    PlanRef,
    PlanUnit,
)

__all__ = [
    "DEFAULT_BUDGET_FALLBACK_MODE",
    "DuplicateDiagnosisTargetError",
    "PriorDeclinedRationale",
    "UnsupportedGagneEventTypeError",
    "diagnose_lesson_plan",
    "diagnose_plan_unit",
]


DEFAULT_BUDGET_FALLBACK_MODE: Final[str] = "summary-only"


class UnsupportedGagneEventTypeError(ValueError):
    """Raised when a plan unit carries an unsupported event_type for 29-2."""


class DuplicateDiagnosisTargetError(ValueError):
    """Raised when diagnosis construction would target the same unit_id twice."""


class PriorDeclinedRationale(BaseModel):
    """Minimal carry-forward seam for 31-5's future Declined-with-rationale output."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unit_id: str = Field(..., min_length=1)
    rationale: str = Field(default="")


def _normalize_prior_declined_rationales(
    prior_declined_rationales: Mapping[str, str] | Sequence[PriorDeclinedRationale] | None,
) -> dict[str, str]:
    if prior_declined_rationales is None:
        return {}

    normalized: dict[str, str] = {}
    if isinstance(prior_declined_rationales, Mapping):
        items = prior_declined_rationales.items()
    else:
        items = ((entry.unit_id, entry.rationale) for entry in prior_declined_rationales)

    for unit_id, rationale in items:
        if unit_id in normalized:
            raise DuplicateDiagnosisTargetError(
                f"prior Declined rationale duplicated for unit_id={unit_id!r}"
            )
        normalized[unit_id] = rationale
    return normalized


def _ensure_supported_event_type(unit: PlanUnit) -> None:
    if unit.event_type not in KNOWN_PLAN_UNIT_EVENT_TYPES:
        raise UnsupportedGagneEventTypeError(
            f"29-2 Gagne diagnostician only supports MVP Gagne event types; "
            f"got event_type={unit.event_type!r} on unit_id={unit.unit_id!r}"
        )


def _modality_ref_is_valid(modality_ref: str | None) -> bool:
    if modality_ref is None:
        return True
    return get_modality_entry(modality_ref) is not None


def _derive_fitness(
    unit: PlanUnit,
    *,
    modality_ref_is_valid: bool,
    prior_declined_rationale: str | None,
) -> Literal["sufficient", "partial", "absent"]:
    if not modality_ref_is_valid:
        return "absent"

    if unit.scope_decision is not None and unit.scope_decision.scope == "out-of-scope":
        return "absent"

    if (
        prior_declined_rationale
        and unit.scope_decision is not None
        and unit.scope_decision.scope == "out-of-scope"
    ):
        return "absent"

    if unit.weather_band in {"gold", "green"}:
        fitness: Literal["sufficient", "partial", "absent"] = "sufficient"
    elif unit.weather_band == "amber":
        fitness = "partial"
    else:
        fitness = "absent"

    if unit.gaps and fitness == "sufficient":
        fitness = "partial"

    if (
        unit.scope_decision is not None
        and unit.scope_decision.scope in {"delegated", "blueprint"}
        and fitness == "sufficient"
    ):
        fitness = "partial"

    return fitness


def _derive_recommended_scope_decision(
    unit: PlanUnit,
    *,
    fitness: Literal["sufficient", "partial", "absent"],
    modality_ref_is_valid: bool,
    prior_declined_rationale: str | None,
) -> Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None:
    if unit.scope_decision is not None:
        return unit.scope_decision.scope

    if unit.modality_ref == "blueprint":
        return "blueprint"

    if prior_declined_rationale and fitness == "absent":
        return "out-of-scope"

    if unit.modality_ref is not None and modality_ref_is_valid:
        return "delegated"

    if fitness in {"sufficient", "partial"}:
        return "in-scope"
    return "out-of-scope"


def _derive_recommended_weather_band(
    unit: PlanUnit,
    *,
    modality_ref_is_valid: bool,
) -> Literal["gold", "green", "amber", "gray"] | None:
    if not modality_ref_is_valid:
        return "gray"
    return unit.weather_band


def _format_commentary(
    unit: PlanUnit,
    *,
    fitness: Literal["sufficient", "partial", "absent"],
    modality_ref_is_valid: bool,
    prior_declined_rationale: str | None,
    summary_only: bool,
) -> str:
    if summary_only:
        if prior_declined_rationale:
            return (
                f"{unit.event_type}: {fitness}; prior Declined rationale carried "
                f"forward."
            )
        if unit.modality_ref is not None and not modality_ref_is_valid:
            return (
                f"{unit.event_type}: {fitness}; modality_ref={unit.modality_ref!r} "
                "is not registered."
            )
        return f"{unit.event_type}: {fitness}; {unit.source_fitness_diagnosis}"

    parts = [f"{unit.event_type} assessed as {fitness}."]
    parts.append(unit.source_fitness_diagnosis)

    if prior_declined_rationale:
        parts.append(
            "Prior Declined rationale carried forward instead of re-diagnosing "
            f"from zero: {prior_declined_rationale}"
        )

    if unit.modality_ref is not None:
        if modality_ref_is_valid:
            parts.append(f"modality_ref={unit.modality_ref!r} is registered.")
        else:
            parts.append(
                f"modality_ref={unit.modality_ref!r} is not present in "
                "MODALITY_REGISTRY."
            )

    if unit.scope_decision is not None:
        parts.append(f"Current scope_decision is {unit.scope_decision.scope!r}.")

    if unit.gaps:
        gap_ids = ", ".join(gap.gap_id for gap in unit.gaps)
        parts.append(f"Identified gaps remain open: {gap_ids}.")

    return " ".join(parts)


def diagnose_plan_unit(
    unit: PlanUnit,
    *,
    prior_declined_rationale: str | None = None,
    summary_only_fallback: bool = False,
) -> FitDiagnosis:
    """Return one deterministic :class:`FitDiagnosis` for ``unit``."""
    _ensure_supported_event_type(unit)
    modality_valid = _modality_ref_is_valid(unit.modality_ref)
    fitness = _derive_fitness(
        unit,
        modality_ref_is_valid=modality_valid,
        prior_declined_rationale=prior_declined_rationale,
    )
    return FitDiagnosis(
        unit_id=unit.unit_id,
        fitness=fitness,
        commentary=_format_commentary(
            unit,
            fitness=fitness,
            modality_ref_is_valid=modality_valid,
            prior_declined_rationale=prior_declined_rationale,
            summary_only=summary_only_fallback,
        ),
        recommended_scope_decision=_derive_recommended_scope_decision(
            unit,
            fitness=fitness,
            modality_ref_is_valid=modality_valid,
            prior_declined_rationale=prior_declined_rationale,
        ),
        recommended_weather_band=_derive_recommended_weather_band(
            unit,
            modality_ref_is_valid=modality_valid,
        ),
    )


def diagnose_lesson_plan(
    plan: LessonPlan,
    *,
    source_ref: str,
    prior_declined_rationales: (
        Mapping[str, str] | Sequence[PriorDeclinedRationale] | None
    ) = None,
    generated_at: datetime | None = None,
    budget_threshold_ms: int = 30_000,
    fallback_mode: str = DEFAULT_BUDGET_FALLBACK_MODE,
    time_source: Callable[[], float] = perf_counter,
) -> FitReport:
    """Return a validated :class:`FitReport` for ``plan``.

    The diagnostician first attempts the full commentary path. If runtime
    breaches ``budget_threshold_ms`` and ``fallback_mode == "summary-only"``,
    it rebuilds the diagnoses in summary-only mode before constructing the
    returned report. The returned ``irene_budget_ms`` always reflects total
    elapsed time until the report is ready to return.
    """
    if budget_threshold_ms < 0:
        raise ValueError("budget_threshold_ms must be >= 0")
    if fallback_mode != DEFAULT_BUDGET_FALLBACK_MODE:
        raise ValueError(
            f"unsupported fallback_mode={fallback_mode!r}; expected "
            f"{DEFAULT_BUDGET_FALLBACK_MODE!r}"
        )

    normalized_prior = _normalize_prior_declined_rationales(prior_declined_rationales)
    start = time_source()

    diagnoses = [
        diagnose_plan_unit(
            unit,
            prior_declined_rationale=normalized_prior.get(unit.unit_id),
        )
        for unit in plan.plan_units
    ]

    unit_ids = [diagnosis.unit_id for diagnosis in diagnoses]
    if len(unit_ids) != len(set(unit_ids)):
        duplicates = sorted({uid for uid in unit_ids if unit_ids.count(uid) > 1})
        raise DuplicateDiagnosisTargetError(
            f"diagnosis construction targeted duplicate unit_ids: {duplicates}"
        )

    elapsed_ms = int(round((time_source() - start) * 1000))
    if elapsed_ms > budget_threshold_ms:
        diagnoses = [
            diagnose_plan_unit(
                unit,
                prior_declined_rationale=normalized_prior.get(unit.unit_id),
                summary_only_fallback=True,
            )
            for unit in plan.plan_units
        ]
        elapsed_ms = int(round((time_source() - start) * 1000))

    report = FitReport(
        source_ref=source_ref,
        plan_ref=PlanRef(
            lesson_plan_revision=plan.revision,
            lesson_plan_digest=plan.digest,
        ),
        diagnoses=diagnoses,
        generated_at=generated_at or datetime.now(tz=UTC),
        irene_budget_ms=elapsed_ms,
    )
    return validate_fit_report(report, plan=plan)
