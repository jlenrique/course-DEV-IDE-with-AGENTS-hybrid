"""Ratified lesson-plan collateral intent -> curated ComponentSelection.

This is the selection edge only. It reads a local, ratified lesson-plan intent,
resolves it through the existing bundle catalog, and returns the catalog's
blessed ComponentSelection for the production runner.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.marcus.lesson_plan.bundle_catalog import BundleId, get_bundle
from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.models.state.component_selection import ComponentSelection

_REMOTE_REF = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_DEFAULT_BUNDLE_ID = "narrated-deck-with-motion"


class CollateralSelectionError(RuntimeError):
    """Raised when explicit collateral selection intent is malformed or unsafe."""


class RatifiedLessonPlanCollateralIntent(BaseModel):
    """Closed local intent shape allowed to drive production component selection."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    ratification_status: Literal["ratified"] = Field(
        ..., description="Only a ratified lesson-plan intent may bind selection."
    )
    bundle_id: BundleId | None = Field(
        default=None,
        description=(
            "Optional closed catalog bundle id. If absent, the resolver derives "
            "the bundle from CollateralSpec.declaration."
        ),
    )
    collateral: CollateralSpec | None = Field(
        default=None,
        description="Optional local collateral spec carried by the ratified lesson plan.",
    )
    source_ref: str | None = Field(
        default=None,
        description="Optional local provenance reference; remote URLs are refused.",
    )

    @field_validator("source_ref")
    @classmethod
    def _source_ref_is_local(cls, value: str | None) -> str | None:
        if value is not None and _REMOTE_REF.search(value.strip()):
            raise ValueError(
                "source_ref must be local; remote collateral intent is refused"
            )
        return value


@dataclass(frozen=True)
class ResolvedCollateralSelection:
    """Resolved bundle + selection passed into the production runtime seam."""

    bundle_id: str
    selection: ComponentSelection
    source: Literal["absent", "unratified", "ratified"]


def _default_result(source: Literal["absent", "unratified"]) -> ResolvedCollateralSelection:
    record = get_bundle(_DEFAULT_BUNDLE_ID)
    if record is None:  # pragma: no cover - import-time catalog invariant guard
        raise CollateralSelectionError(
            f"default bundle {_DEFAULT_BUNDLE_ID!r} is missing from the catalog"
        )
    return ResolvedCollateralSelection(
        bundle_id=record.id,
        selection=record.selection,
        source=source,
    )


def _bundle_from_collateral(collateral: CollateralSpec | None) -> str:
    if collateral is None:
        raise CollateralSelectionError(
            "ratified collateral intent requires bundle_id or collateral"
        )
    if collateral.declaration == "present":
        return "narrated-deck-with-workbook"
    return _DEFAULT_BUNDLE_ID


def _validate_bundle_collateral_pair(
    *,
    bundle_id: str,
    collateral: CollateralSpec | None,
) -> None:
    if (
        bundle_id == "narrated-deck-with-workbook"
        and (collateral is None or collateral.declaration != "present")
    ):
        raise CollateralSelectionError(
            "narrated-deck-with-workbook requires collateral.declaration == "
            "'present' with a workbook payload"
        )
    if (
        collateral is not None
        and collateral.declaration == "present"
        and bundle_id != "narrated-deck-with-workbook"
    ):
        raise CollateralSelectionError(
            "workbook collateral may select workbook only through "
            "'narrated-deck-with-workbook'"
        )


def _validate_unknown_bundle(payload: dict[str, Any]) -> None:
    bundle_id = payload.get("bundle_id")
    if bundle_id is not None and get_bundle(str(bundle_id)) is None:
        raise CollateralSelectionError(
            f"unknown bundle id {bundle_id!r}; expected a closed catalog id"
        )


def resolve_lesson_plan_collateral_selection(
    payload: Any,
) -> ResolvedCollateralSelection:
    """Resolve optional lesson-plan collateral intent to ComponentSelection.

    ``None`` preserves today's production default. Non-ratified mappings are
    treated as draft material and also preserve the default. A ratified mapping
    must satisfy the closed intent shape and closed bundle catalog before the
    production runner composes a graph.
    """
    if payload is None:
        return _default_result("absent")
    if isinstance(payload, RatifiedLessonPlanCollateralIntent):
        intent = payload
    elif not isinstance(payload, dict):
        raise CollateralSelectionError(
            "lesson-plan collateral intent must be a mapping or None"
        )
    else:
        ratification = payload.get("ratification_status")
        if ratification != "ratified":
            return _default_result("unratified")
        _validate_unknown_bundle(payload)
        try:
            intent = RatifiedLessonPlanCollateralIntent.model_validate(payload)
        except ValidationError as exc:
            raise CollateralSelectionError(
                f"closed ratified intent validation failed: {exc}"
            ) from exc

    bundle_id = intent.bundle_id or _bundle_from_collateral(intent.collateral)
    _validate_bundle_collateral_pair(bundle_id=bundle_id, collateral=intent.collateral)
    record = get_bundle(bundle_id)
    if record is None:
        raise CollateralSelectionError(
            f"unknown bundle id {bundle_id!r}; expected a closed catalog id"
        )
    return ResolvedCollateralSelection(
        bundle_id=record.id,
        selection=record.selection,
        source="ratified",
    )


def load_lesson_plan_collateral_selection(path: Path) -> ResolvedCollateralSelection:
    """Load a local YAML/JSON ratified intent file and resolve its selection."""
    if not path.is_file():
        raise CollateralSelectionError(
            f"lesson-plan collateral intent file does not exist: {path}"
        )
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise CollateralSelectionError(
            f"lesson-plan collateral intent file is not valid YAML/JSON: {path}"
        ) from exc
    return resolve_lesson_plan_collateral_selection(payload)


__all__ = [
    "CollateralSelectionError",
    "RatifiedLessonPlanCollateralIntent",
    "ResolvedCollateralSelection",
    "load_lesson_plan_collateral_selection",
    "resolve_lesson_plan_collateral_selection",
]
