from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.lesson_plan.collateral_selection import (
    CollateralSelectionError,
    load_lesson_plan_collateral_selection,
    resolve_lesson_plan_collateral_selection,
)
from app.marcus.lesson_plan.collateral_spec import (
    CollateralSpec,
    DepthDeltaContract,
    WorkbookSection,
    WorkbookSpec,
)
from app.models.state.component_selection import ComponentSelection


def _workbook_collateral() -> CollateralSpec:
    return CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(
            sections=[
                WorkbookSection(
                    section_id="sec-1",
                    learning_objective_id="obj-1",
                    title="Read in depth",
                    depth_delta=DepthDeltaContract(
                        deferred_from_slide="slide-1",
                        deferred_depth="the supporting method",
                    ),
                )
            ]
        ),
    )


def test_ratified_workbook_collateral_intent_resolves_catalog_bundle() -> None:
    result = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "ratified",
            "collateral": _workbook_collateral().model_dump(mode="json"),
        }
    )

    assert result.bundle_id == "narrated-deck-with-workbook"
    assert result.selection == ComponentSelection(deck=True, motion=True, workbook=True)


def test_absent_collateral_intent_preserves_production_default() -> None:
    result = resolve_lesson_plan_collateral_selection(None)

    assert result.bundle_id == "narrated-deck-with-motion"
    assert result.selection == ComponentSelection.production_default()
    assert result.source == "absent"


def test_unratified_collateral_intent_does_not_override_default() -> None:
    result = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "draft",
            "bundle_id": "narrated-deck-with-workbook",
            "collateral": _workbook_collateral().model_dump(mode="json"),
        }
    )

    assert result.bundle_id == "narrated-deck-with-motion"
    assert result.selection == ComponentSelection.production_default()
    assert result.source == "unratified"


def test_unknown_component_shape_fails_loud_before_selection() -> None:
    with pytest.raises(CollateralSelectionError, match="closed ratified intent"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "components": ["deck", "quiz"],
            }
        )


def test_unknown_bundle_fails_loud_before_selection() -> None:
    with pytest.raises(CollateralSelectionError, match="unknown bundle"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "bundle_id": "narrated-deck-video-export",
            }
        )


def test_remote_source_ref_fails_loud_before_selection() -> None:
    with pytest.raises(CollateralSelectionError, match="remote"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "bundle_id": "narrated-deck",
                "source_ref": "https://example.test/course.json",
            }
        )


def test_workbook_bundle_requires_workbook_collateral_payload() -> None:
    with pytest.raises(CollateralSelectionError, match="requires collateral"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "bundle_id": "narrated-deck-with-workbook",
                "collateral": CollateralSpec(declaration="none").model_dump(mode="json"),
            }
        )


def test_load_lesson_plan_collateral_selection_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "ratified-collateral-intent.yaml"
    path.write_text(
        "\n".join(
            [
                "ratification_status: ratified",
                "bundle_id: narrated-deck",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = load_lesson_plan_collateral_selection(path)

    assert result.bundle_id == "narrated-deck"
    assert result.selection == ComponentSelection(deck=True, motion=False, workbook=False)


def test_load_lesson_plan_collateral_selection_rejects_invalid_utf8(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid-utf8.yaml"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(CollateralSelectionError, match="not valid YAML/JSON"):
        load_lesson_plan_collateral_selection(path)
