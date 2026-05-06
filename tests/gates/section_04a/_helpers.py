"""Shared fixtures for Section 04A poll-surface tests."""

from __future__ import annotations

from marcus.lesson_plan.schema import PlanUnit, ScopeDecision


def fixture_plan_unit() -> PlanUnit:
    return PlanUnit(
        unit_id="gagne-event-3",
        event_type="present-content",
        source_fitness_diagnosis="Primary source supports this unit.",
        scope_decision=ScopeDecision(
            state="ratified",
            scope="in-scope",
            proposed_by="system",
            ratified_by="maya",
        ),
        weather_band="green",
        modality_ref="slides",
        rationale="This unit is ready for ratification.",
    )


__all__ = ["fixture_plan_unit"]

