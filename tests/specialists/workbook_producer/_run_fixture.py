"""Shared test helper: write a valid ``run.json`` carrying Irene's collateral.

S7 canonical-arc: the 07W producer now CONSUMES Irene's authored
``lesson_plan["collateral"]`` (+ the S6 ``research_entries``) off the persisted
``<run_dir>/run.json`` ProductionEnvelope. Producer-node tests therefore seed a
real (validated) trial envelope on disk — built through the model classes so the
producer's ``ProductionTrialEnvelope.model_validate_json`` read succeeds.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

_IRENE_NODE_ID = "03"
_RESEARCH_NODE_ID = "04.55"


def collateral_present(
    sections: list[dict[str, Any]],
    *,
    research_goals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """A ``declaration=="present"`` collateral block with the given sections."""
    return {
        "declaration": "present",
        "workbook": {"sections": sections},
        "research_goals": research_goals or [],
    }


def section(
    section_id: str,
    objective_id: str,
    *,
    title: str = "Section",
    deferred_depth: str = "deferred depth carried into the read-channel workbook",
    exercises: list[dict[str, Any]] | None = None,
    narrative_intent: str = "",
    deferred_from_slide: str = "slide-01",
) -> dict[str, Any]:
    """Build a WorkbookSection dict for a collateral blueprint."""
    return {
        "section_id": section_id,
        "learning_objective_id": objective_id,
        "title": title,
        "depth_delta": {
            "deferred_from_slide": deferred_from_slide,
            "deferred_depth": deferred_depth,
        },
        "exercises": exercises or [],
        "narrative_intent": narrative_intent,
    }


def write_run_json(
    run_dir: Path,
    *,
    collateral: dict[str, Any],
    plan_units: list[dict[str, Any]] | None = None,
    lesson_summary: str = "companion workbook lesson",
    research_entries: list[dict[str, Any]] | None = None,
) -> Path:
    """Write a valid ``<run_dir>/run.json`` with Irene's collateral (+ research).

    Built via the model classes so the producer's model_validate_json read
    succeeds; ``collateral`` is carried verbatim on the irene_pass1 lesson_plan.
    """
    trial_id = uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            output={
                "lesson_plan": {
                    "lesson_summary": lesson_summary,
                    "plan_units": plan_units or [],
                    "collateral": collateral,
                }
            },
            model_used="fixture-irene",
            node_id=_IRENE_NODE_ID,
        )
    )
    if research_entries is not None:
        envelope.add_contribution(
            SpecialistContribution.from_output(
                specialist_id="research_wiring",
                output={"research_entries": research_entries},
                model_used="fixture-research",
                node_id=_RESEARCH_NODE_ID,
            )
        )
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="course-content/courses/fixture-lesson",
        operator_id="fixture-operator",
        started_at=datetime.now(UTC),
        status="in-flight",
        production_clone_launch_evidence=False,
        production_envelope=envelope,
    )
    path = run_dir / "run.json"
    path.write_text(trial.model_dump_json(), encoding="utf-8")
    return path
