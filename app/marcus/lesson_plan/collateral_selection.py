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

from app.marcus.course_source.input_bundle import LessonPlanningInputBundle
from app.marcus.lesson_plan.bundle_catalog import BUNDLE_CATALOG, BundleId, get_bundle
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
    input_bundle: LessonPlanningInputBundle | None = Field(
        default=None,
        description=(
            "Optional ratified lesson-planning input bundle whose component "
            "selection must resolve through the closed bundle catalog."
        ),
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
    source: Literal["absent", "unratified", "ratified", "plan_collateral"]


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
            "ratified collateral intent requires bundle_id, collateral, or input_bundle"
        )
    if collateral.declaration == "present":
        return "narrated-deck-with-workbook"
    return _DEFAULT_BUNDLE_ID


def _bundle_from_component_selection(selection: ComponentSelection) -> str:
    matches = [
        record.id for record in BUNDLE_CATALOG.values() if record.selection == selection
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise CollateralSelectionError(
            "input_bundle.component_selection matches multiple closed catalog bundles"
        )
    raise CollateralSelectionError(
        "input_bundle.component_selection must match one closed catalog bundle"
    )


def _bundle_from_intent(intent: RatifiedLessonPlanCollateralIntent) -> str:
    if (
        intent.bundle_id == "narrated-deck-with-workbook"
        and intent.collateral is not None
        and intent.collateral.declaration != "present"
    ):
        raise CollateralSelectionError(
            "narrated-deck-with-workbook requires collateral.declaration == "
            "'present' with a workbook payload"
        )
    claims: list[tuple[str, str]] = []
    if intent.bundle_id is not None:
        claims.append(("bundle_id", intent.bundle_id))
    if intent.collateral is not None and (
        intent.collateral.declaration == "present"
        or (intent.bundle_id is None and intent.input_bundle is None)
    ):
        claims.append(("collateral", _bundle_from_collateral(intent.collateral)))
    if intent.input_bundle is not None:
        claims.append(
            (
                "input_bundle.component_selection",
                _bundle_from_component_selection(intent.input_bundle.component_selection),
            )
        )
    if not claims:
        raise CollateralSelectionError(
            "ratified collateral intent requires bundle_id, collateral, or input_bundle"
        )
    winner_name, winner_bundle = claims[0]
    for name, bundle_id in claims[1:]:
        if bundle_id != winner_bundle:
            raise CollateralSelectionError(
                f"ratified collateral intent conflict: {winner_name} selects "
                f"{winner_bundle!r} but {name} selects {bundle_id!r}"
            )
    return winner_bundle


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

    bundle_id = _bundle_from_intent(intent)
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


def derive_selection_from_lesson_plan(
    plan: dict[str, Any] | None,
    *,
    source_ref: str | None = None,
) -> ResolvedCollateralSelection:
    """Derive ComponentSelection from Irene Pass-1 ``lesson_plan`` collateral.

    Phase-2 Mine 1 (Winston Option A): the plan's ``collateral`` block is the
    single truth. No separate ratification recorder is required for this path.
    Missing/invalid collateral fails loud — never silent default.
    """
    if not isinstance(plan, dict) or not plan:
        raise CollateralSelectionError(
            "lesson_plan is required to derive component selection from collateral"
        )
    raw_collateral = plan.get("collateral")
    if raw_collateral is None:
        raise CollateralSelectionError(
            "lesson_plan.collateral is required to derive component selection "
            "(absent key is not a silent default)"
        )
    try:
        collateral = (
            raw_collateral
            if isinstance(raw_collateral, CollateralSpec)
            else CollateralSpec.model_validate(raw_collateral)
        )
    except ValidationError as exc:
        raise CollateralSelectionError(
            f"lesson_plan.collateral failed CollateralSpec validation: {exc}"
        ) from exc

    intent = RatifiedLessonPlanCollateralIntent(
        ratification_status="ratified",
        collateral=collateral,
        source_ref=source_ref,
    )
    resolved = resolve_lesson_plan_collateral_selection(intent)
    return ResolvedCollateralSelection(
        bundle_id=resolved.bundle_id,
        selection=resolved.selection,
        source="plan_collateral",
    )


def load_selection_from_lesson_plan_json(path: Path) -> ResolvedCollateralSelection:
    """Load ``irene-pass1.lesson-plan.json`` (or equivalent) and derive selection."""
    if not path.is_file():
        raise CollateralSelectionError(
            f"lesson-plan JSON file does not exist: {path}"
        )
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise CollateralSelectionError(
            f"lesson-plan JSON file is not valid JSON/YAML: {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise CollateralSelectionError(
            f"lesson-plan JSON must decode to an object: {path}"
        )
    # Accept either bare plan or {lesson_plan: {...}} contribution wrapper.
    plan = payload.get("lesson_plan") if "lesson_plan" in payload else payload
    if not isinstance(plan, dict):
        raise CollateralSelectionError(
            f"lesson-plan JSON missing plan object: {path}"
        )
    return derive_selection_from_lesson_plan(
        plan, source_ref=path.as_posix()
    )


__all__ = [
    "CollateralSelectionError",
    "RatifiedLessonPlanCollateralIntent",
    "ResolvedCollateralSelection",
    "derive_selection_from_lesson_plan",
    "load_lesson_plan_collateral_selection",
    "load_selection_from_lesson_plan_json",
    "resolve_lesson_plan_collateral_selection",
]
