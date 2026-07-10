from __future__ import annotations

from pathlib import Path

import json
import pytest

from app.marcus.course_source.input_bundle import (
    LessonPlanningInputBundle,
    build_lesson_planning_input_bundle,
)
from app.marcus.lesson_plan import collateral_selection
from app.marcus.lesson_plan.bundle_catalog import get_bundle
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

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "s7p2-story-b-syllabus-metadata-20260708T110225"
)
HAI_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)


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


def _hai_input_bundle(
    selection: ComponentSelection | None = None,
) -> LessonPlanningInputBundle:
    bundle = build_lesson_planning_input_bundle(
        course_root=HAI_ROOT,
        proposal_path=EVIDENCE / "hai-510" / "module-metadata.yaml",
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )
    if selection is None:
        return bundle
    return bundle.model_copy(update={"component_selection": selection})


def test_ratified_workbook_collateral_intent_resolves_catalog_bundle() -> None:
    result = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "ratified",
            "collateral": _workbook_collateral().model_dump(mode="json"),
        }
    )

    assert result.bundle_id == "narrated-deck-with-workbook"
    assert result.selection == ComponentSelection(deck=True, motion=True, workbook=True)


def test_ratified_input_bundle_resolves_component_selection_through_catalog() -> None:
    bundle = _hai_input_bundle()

    result = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "ratified",
            "input_bundle": bundle.model_dump(mode="json"),
        }
    )

    assert result.bundle_id == "narrated-deck-with-motion"
    assert result.selection == ComponentSelection(deck=True, motion=True, workbook=False)
    assert result.source == "ratified"


def test_input_bundle_selection_conflict_fails_loud() -> None:
    bundle = _hai_input_bundle()

    with pytest.raises(CollateralSelectionError, match="conflict"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "bundle_id": "narrated-deck",
                "input_bundle": bundle.model_dump(mode="json"),
            }
        )


def test_input_bundle_selection_must_match_closed_catalog() -> None:
    bundle = _hai_input_bundle(
        ComponentSelection(deck=False, motion=False, workbook=False)
    )

    with pytest.raises(CollateralSelectionError, match="closed catalog"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "input_bundle": bundle.model_dump(mode="json"),
            }
        )


def test_input_bundle_selection_must_match_exactly_one_catalog_bundle(monkeypatch) -> None:
    bundle = _hai_input_bundle()
    record = get_bundle("narrated-deck-with-motion")
    assert record is not None
    monkeypatch.setattr(
        collateral_selection,
        "BUNDLE_CATALOG",
        {"primary": record, "duplicate": record},
    )

    with pytest.raises(CollateralSelectionError, match="multiple"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "input_bundle": bundle.model_dump(mode="json"),
            }
        )


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


def test_workbook_bundle_requires_collateral_payload_even_without_collateral() -> None:
    with pytest.raises(CollateralSelectionError, match="requires collateral"):
        resolve_lesson_plan_collateral_selection(
            {
                "ratification_status": "ratified",
                "bundle_id": "narrated-deck-with-workbook",
            }
        )


def test_none_collateral_does_not_conflict_with_explicit_non_workbook_bundle() -> None:
    result = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "ratified",
            "bundle_id": "narrated-deck",
            "collateral": CollateralSpec(declaration="none").model_dump(mode="json"),
        }
    )

    assert result.bundle_id == "narrated-deck"
    assert result.selection == ComponentSelection(deck=True, motion=False, workbook=False)


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


def test_derive_selection_from_lesson_plan_workbook_present() -> None:
    from app.marcus.lesson_plan.collateral_selection import (
        derive_selection_from_lesson_plan,
    )

    plan = {
        "lesson_summary": "Bridge lesson",
        "plan_units": [{"unit_id": "u1", "title": "T"}],
        "collateral": _workbook_collateral().model_dump(mode="json"),
    }
    result = derive_selection_from_lesson_plan(plan, source_ref="test")
    assert result.bundle_id == "narrated-deck-with-workbook"
    assert result.selection == ComponentSelection(deck=True, motion=True, workbook=True)
    assert result.source == "plan_collateral"


def test_derive_selection_from_lesson_plan_declaration_none() -> None:
    from app.marcus.lesson_plan.collateral_selection import (
        derive_selection_from_lesson_plan,
    )

    plan = {
        "plan_units": [],
        "collateral": {"declaration": "none", "workbook": None, "research_goals": []},
    }
    result = derive_selection_from_lesson_plan(plan)
    assert result.bundle_id == "narrated-deck-with-motion"
    assert result.selection == ComponentSelection.production_default()
    assert result.source == "plan_collateral"


def test_derive_selection_fails_loud_when_collateral_absent() -> None:
    from app.marcus.lesson_plan.collateral_selection import (
        derive_selection_from_lesson_plan,
    )

    with pytest.raises(CollateralSelectionError, match="collateral is required"):
        derive_selection_from_lesson_plan({"plan_units": []})


def test_load_selection_from_lesson_plan_json_round_trip(tmp_path: Path) -> None:
    from app.marcus.lesson_plan.collateral_selection import (
        load_selection_from_lesson_plan_json,
    )

    path = tmp_path / "irene-pass1.lesson-plan.json"
    path.write_text(
        json.dumps(
            {
                "lesson_summary": "x",
                "plan_units": [],
                "collateral": _workbook_collateral().model_dump(mode="json"),
            }
        ),
        encoding="utf-8",
    )
    result = load_selection_from_lesson_plan_json(path)
    assert result.source == "plan_collateral"
    assert result.bundle_id == "narrated-deck-with-workbook"
