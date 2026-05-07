"""Irene blueprint co-author protocol for Story 29-3.

This module consumes a concrete 31-4 blueprint draft, records Irene + writer
approval in a deterministic sidecar artifact, and returns an updated
``PlanUnit`` carrying a typed ``blueprint_signoff`` pointer.

Discipline notes:

* 29-3 consumes the 31-4 artifact contract; it does not rewrite the producer
  contract or impersonate the Quinn-R gate.
* The sign-off record is explicit and typed. Downstream stories should read
  ``plan_unit.blueprint_signoff`` rather than scraping the blueprint markdown.
* 29-3 does not emit to the Lesson Plan log and does not call fit-report
  emission surfaces.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Final

from app.marcus.lesson_plan.blueprint_producer import (
    HUMAN_REVIEW_SECTION_HEADING,
    IRENE_REVIEW_MARKER,
    WRITER_SIGNOFF_MARKER,
)
from app.marcus.lesson_plan.produced_asset import ProducedAsset
from app.marcus.lesson_plan.schema import BlueprintSignoff, PlanUnit

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT_SIGNOFF_ROOT: Final[str] = "_bmad-output/artifacts/blueprints/signoffs"
IRENE_APPROVED_MARKER: Final[str] = "- [x] Irene blueprint review complete"
WRITER_APPROVED_MARKER: Final[str] = "- [x] Writer sign-off complete"


class BlueprintCoauthorError(ValueError):
    """Raised when a blueprint draft cannot enter the 29-3 co-author path."""


def _resolve_output_root(output_root: str | Path) -> Path:
    path = Path(output_root)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BlueprintCoauthorError(
            f"Blueprint signoff output_root must live under the repo root; got {path}"
        ) from exc
    return path


def _relative_asset_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _parse_revision_from_fulfills(fulfills: str) -> str:
    unit_id, sep, revision = fulfills.partition("@")
    if not sep or not unit_id or not revision:
        raise BlueprintCoauthorError(
            f"ProducedAsset.fulfills must be <unit_id>@<revision>; got {fulfills!r}"
        )
    return revision


def _validate_blueprint_plan_unit(plan_unit: PlanUnit) -> None:
    if (
        plan_unit.scope_decision is not None
        and plan_unit.scope_decision.scope != "blueprint"
    ):
        raise BlueprintCoauthorError(
            "29-3 requires a blueprint-scoped plan unit; "
            f"got scope={plan_unit.scope_decision.scope!r}"
        )
    if plan_unit.modality_ref not in {None, "blueprint"}:
        raise BlueprintCoauthorError(
            "29-3 requires modality_ref to be null or 'blueprint'; "
            f"got {plan_unit.modality_ref!r}"
        )


def _load_blueprint_markdown(asset: ProducedAsset, plan_unit: PlanUnit) -> tuple[Path, str]:
    if asset.modality_ref != "blueprint":
        raise BlueprintCoauthorError(
            "29-3 requires a blueprint ProducedAsset; "
            f"got modality_ref={asset.modality_ref!r}"
        )
    if asset.source_plan_unit_id != plan_unit.unit_id:
        raise BlueprintCoauthorError(
            "ProducedAsset.source_plan_unit_id must match the plan unit under review; "
            f"got asset={asset.source_plan_unit_id!r} unit={plan_unit.unit_id!r}"
        )

    posix_path = PurePosixPath(asset.asset_path)
    if posix_path.is_absolute() or ".." in posix_path.parts:
        raise BlueprintCoauthorError(
            f"ProducedAsset.asset_path must be repo-relative; got {asset.asset_path!r}"
        )
    path = REPO_ROOT / asset.asset_path
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BlueprintCoauthorError(
            f"ProducedAsset.asset_path must stay under the repo root; got {path}"
        ) from exc
    if not path.exists():
        raise BlueprintCoauthorError(
            f"Blueprint artifact missing at {asset.asset_path!r}"
        )

    text = path.read_text(encoding="utf-8")
    required_markers = (
        HUMAN_REVIEW_SECTION_HEADING,
        IRENE_REVIEW_MARKER,
        WRITER_SIGNOFF_MARKER,
    )
    for marker in required_markers:
        if marker not in text:
            raise BlueprintCoauthorError(
                "Blueprint artifact is missing the stable 31-4 review marker "
                f"{marker!r}"
            )
    return path, text


def compose_blueprint_signoff_markdown(
    plan_unit: PlanUnit,
    blueprint_asset: ProducedAsset,
    *,
    irene_commentary: str,
    writer_commentary: str,
    signed_at: datetime,
) -> str:
    """Return the deterministic sign-off sidecar artifact for ``plan_unit``."""
    return "\n".join(
        [
            f"# Blueprint Sign-off: {plan_unit.event_type}",
            "",
            f"Unit ID: `{plan_unit.unit_id}`",
            f"Blueprint draft: `{blueprint_asset.asset_path}`",
            f"Fulfills target: `{blueprint_asset.fulfills}`",
            "",
            "## Irene Co-author Notes",
            irene_commentary,
            "",
            "## Writer Approval Notes",
            writer_commentary,
            "",
            "## Sign-off Status",
            IRENE_APPROVED_MARKER,
            WRITER_APPROVED_MARKER,
            f"- Signed at: {signed_at.isoformat()}",
            "",
        ]
    )


def coauthor_blueprint(
    plan_unit: PlanUnit,
    blueprint_asset: ProducedAsset,
    *,
    irene_commentary: str,
    writer_commentary: str,
    signoff_root: str | Path = DEFAULT_BLUEPRINT_SIGNOFF_ROOT,
    signed_at: datetime | None = None,
) -> PlanUnit:
    """Return ``plan_unit`` with a typed `blueprint_signoff` pointer attached."""
    if not irene_commentary.strip():
        raise BlueprintCoauthorError("Irene commentary must be non-empty")
    if not writer_commentary.strip():
        raise BlueprintCoauthorError("Writer commentary must be non-empty")

    _validate_blueprint_plan_unit(plan_unit)
    _load_blueprint_markdown(blueprint_asset, plan_unit)
    output_root = _resolve_output_root(signoff_root)
    effective_signed_at = signed_at or datetime.now(tz=UTC)
    if effective_signed_at.tzinfo is None:
        raise BlueprintCoauthorError("signed_at must be timezone-aware")

    revision = _parse_revision_from_fulfills(blueprint_asset.fulfills)
    signoff_path = output_root / f"{plan_unit.unit_id}@{revision}.signoff.md"
    signoff_path.parent.mkdir(parents=True, exist_ok=True)
    signoff_markdown = compose_blueprint_signoff_markdown(
        plan_unit,
        blueprint_asset,
        irene_commentary=irene_commentary.strip(),
        writer_commentary=writer_commentary.strip(),
        signed_at=effective_signed_at,
    )
    signoff_path.write_text(signoff_markdown, encoding="utf-8")

    updated = plan_unit.model_copy(deep=True)
    updated.blueprint_signoff = BlueprintSignoff(
        blueprint_asset_path=blueprint_asset.asset_path,
        signoff_artifact_path=_relative_asset_path(signoff_path),
        irene_review_complete=True,
        writer_signoff_complete=True,
        signed_at=effective_signed_at,
    )
    return updated


__all__ = [
    "BlueprintCoauthorError",
    "DEFAULT_BLUEPRINT_SIGNOFF_ROOT",
    "IRENE_APPROVED_MARKER",
    "WRITER_APPROVED_MARKER",
    "coauthor_blueprint",
    "compose_blueprint_signoff_markdown",
]
