"""Blueprint producer for lesson-plan units marked for blueprint handling.

Audience: blueprint authors and reviewers consuming the first concrete
``ModalityProducer`` implementation. This module emits a deterministic markdown
blueprint draft plus an explicit human-review checkpoint.

Discipline notes:

* 31-4 stays artifact-focused: it emits a markdown draft and returns a valid
  :class:`ProducedAsset`; it does not implement 29-3 co-authoring or 31-5 gate
  logic.
* The default drafting path is deterministic and offline. Callers may inject a
  richer body renderer, but the producer always appends the stable review
  markers required by downstream stories.
* The output path is repo-relative by default under ``_bmad-output/artifacts``.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Final

from app.marcus.lesson_plan.modality_producer import ModalityProducer
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT_OUTPUT_ROOT: Final[str] = "_bmad-output/artifacts/blueprints"
HUMAN_REVIEW_SECTION_HEADING: Final[str] = "## Human Review Checkpoint"
IRENE_REVIEW_MARKER: Final[str] = "- [ ] Irene blueprint review complete"
WRITER_SIGNOFF_MARKER: Final[str] = "- [ ] Writer sign-off complete"
SIGNOFF_STATUS_MARKER: Final[str] = "Sign-off status: pending"

BlueprintBodyRenderer = Callable[[PlanUnit, ProductionContext], str]


class BlueprintScopeError(ValueError):
    """Raised when a plan unit is not eligible for blueprint production."""


def _resolve_output_root(output_root: str | Path) -> Path:
    path = Path(output_root)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"BlueprintProducer output_root must live under the repo root; got {path}"
        ) from exc
    return path


def _relative_asset_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _validate_blueprint_target(plan_unit: PlanUnit) -> None:
    if (
        plan_unit.scope_decision is not None
        and plan_unit.scope_decision.scope != "blueprint"
    ):
        raise BlueprintScopeError(
            "BlueprintProducer requires scope_decision.scope='blueprint' when "
            f"scope_decision is present; got {plan_unit.scope_decision.scope!r} "
            f"for unit_id={plan_unit.unit_id!r}"
        )
    if plan_unit.modality_ref not in {None, "blueprint"}:
        raise BlueprintScopeError(
            "BlueprintProducer requires modality_ref to be null or 'blueprint'; "
            f"got {plan_unit.modality_ref!r} for unit_id={plan_unit.unit_id!r}"
        )
    if plan_unit.scope_decision is None and plan_unit.modality_ref != "blueprint":
        raise BlueprintScopeError(
            "BlueprintProducer requires either a blueprint scope_decision or "
            "modality_ref='blueprint'; got neither for "
            f"unit_id={plan_unit.unit_id!r}"
        )


def render_blueprint_body(plan_unit: PlanUnit, context: ProductionContext) -> str:
    """Return the deterministic blueprint body section for ``plan_unit``."""
    scope_value = (
        plan_unit.scope_decision.scope if plan_unit.scope_decision is not None else "blueprint"
    )
    rationale = plan_unit.rationale or "No explicit rationale supplied."
    return "\n".join(
        [
            "### Instructional Objective",
            f"Turn `{plan_unit.event_type}` into a reviewable lesson blueprint.",
            "",
            "### Source Signals",
            f"- source_fitness_diagnosis: {plan_unit.source_fitness_diagnosis}",
            f"- weather_band: {plan_unit.weather_band}",
            f"- scope_decision: {scope_value}",
            f"- lesson_plan_revision: {context.lesson_plan_revision}",
            f"- lesson_plan_digest: {context.lesson_plan_digest}",
            "",
            "### Draft Blueprint",
            f"Use the source material for `{plan_unit.unit_id}` to draft a blueprint",
            "that names the learning move, the evidence to preserve, and the",
            "places where a human writer must turn the outline into final prose.",
            "",
            "### Rationale",
            rationale,
        ]
    )


def compose_blueprint_markdown(
    plan_unit: PlanUnit,
    context: ProductionContext,
    *,
    body: str,
) -> str:
    """Wrap the rendered body in the canonical markdown artifact shape."""
    return "\n".join(
        [
            f"# Blueprint Draft: {plan_unit.event_type}",
            "",
            f"Unit ID: `{plan_unit.unit_id}`",
            f"Fulfills target: `{plan_unit.unit_id}@{context.lesson_plan_revision}`",
            "",
            "This draft captures the blueprint branch for a unit the APP cannot",
            "finish alone. It is intentionally review-bound and awaits human sign-off.",
            "",
            body.strip(),
            "",
            HUMAN_REVIEW_SECTION_HEADING,
            IRENE_REVIEW_MARKER,
            WRITER_SIGNOFF_MARKER,
            f"- {SIGNOFF_STATUS_MARKER}",
            "",
        ]
    )


class BlueprintProducer(ModalityProducer):
    """Concrete producer for the ``blueprint`` modality."""

    modality_ref = "blueprint"
    status = "ready"

    def __init__(
        self,
        *,
        output_root: str | Path = DEFAULT_BLUEPRINT_OUTPUT_ROOT,
        body_renderer: BlueprintBodyRenderer | None = None,
    ) -> None:
        self._output_root = _resolve_output_root(output_root)
        self._body_renderer = body_renderer or render_blueprint_body

    def produce(
        self,
        plan_unit: PlanUnit,
        context: ProductionContext,
    ) -> ProducedAsset:
        _validate_blueprint_target(plan_unit)

        body = self._body_renderer(plan_unit, context)
        markdown = compose_blueprint_markdown(plan_unit, context, body=body)

        output_path = (
            self._output_root
            / f"{plan_unit.unit_id}@{context.lesson_plan_revision}.md"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

        asset_path = _relative_asset_path(output_path)
        return ProducedAsset(
            asset_ref=f"blueprint-{plan_unit.unit_id}@{context.lesson_plan_revision}",
            modality_ref=self.modality_ref,
            source_plan_unit_id=plan_unit.unit_id,
            asset_path=asset_path,
            fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}",
        )


__all__ = [
    "BlueprintProducer",
    "BlueprintScopeError",
    "DEFAULT_BLUEPRINT_OUTPUT_ROOT",
    "HUMAN_REVIEW_SECTION_HEADING",
    "IRENE_REVIEW_MARKER",
    "SIGNOFF_STATUS_MARKER",
    "WRITER_SIGNOFF_MARKER",
    "compose_blueprint_markdown",
    "render_blueprint_body",
]
