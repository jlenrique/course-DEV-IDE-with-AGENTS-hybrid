"""No-leak grep for Story 31-4 blueprint producer."""

from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

from app.marcus.lesson_plan.blueprint_producer import BlueprintProducer
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit, ScopeDecision

REPO_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_TOKEN_PATTERN = re.compile(r"\b(intake|orchestrator)\b", re.IGNORECASE)


def _make_plan_unit() -> PlanUnit:
    return PlanUnit(
        unit_id="gagne-event-8",
        event_type="gagne-event-8",
        source_fitness_diagnosis="Source supports a blueprint draft.",
        scope_decision=ScopeDecision(
            state="proposed",
            scope="blueprint",
            proposed_by="system",
            _internal_proposed_by="marcus",
        ),
        weather_band="gray",
        modality_ref="blueprint",
        rationale="A human writer still has to finish this path.",
        gaps=[],
        dials=None,
    )


def test_blueprint_producer_module_text_has_no_forbidden_tokens() -> None:
    path = REPO_ROOT / "app" / "marcus" / "lesson_plan" / "blueprint_producer.py"
    text = path.read_text(encoding="utf-8")
    match = FORBIDDEN_TOKEN_PATTERN.search(text)
    assert match is None, f"Forbidden token {match.group()!r} found in {path}"


def test_rendered_markdown_has_no_forbidden_tokens() -> None:
    output_root = (
        REPO_ROOT
        / "_bmad-output"
        / "test-artifacts"
        / "blueprint-no-leak"
        / uuid.uuid4().hex
    )
    try:
        producer = BlueprintProducer(output_root=output_root)
        asset = producer.produce(
            _make_plan_unit(),
            ProductionContext(
                lesson_plan_revision=2,
                lesson_plan_digest="digest-no-leak",
            ),
        )
        markdown = (REPO_ROOT / asset.asset_path).read_text(encoding="utf-8")
        match = FORBIDDEN_TOKEN_PATTERN.search(markdown)
        assert match is None, (
            f"Forbidden token {match.group()!r} found in rendered blueprint markdown"
        )
    finally:
        shutil.rmtree(output_root, ignore_errors=True)
