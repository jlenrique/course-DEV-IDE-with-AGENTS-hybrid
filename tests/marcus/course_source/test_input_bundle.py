from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.course_source.input_bundle import (
    LessonPlanningInputBundle,
    build_lesson_planning_input_bundle,
    load_input_bundle,
    render_input_bundle_yaml,
    write_input_bundle,
)
from app.models.state.component_selection import ComponentSelection
from scripts.utilities.build_lesson_planning_input_bundle import (
    assert_output_outside_course_root,
)

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
PHS_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "juan-leon-phs-620-teaching-learning-seminar"
)


def _hai_bundle() -> LessonPlanningInputBundle:
    return build_lesson_planning_input_bundle(
        course_root=HAI_ROOT,
        proposal_path=EVIDENCE / "hai-510" / "module-metadata.yaml",
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )


def _phs_bundle() -> LessonPlanningInputBundle:
    return build_lesson_planning_input_bundle(
        course_root=PHS_ROOT,
        proposal_path=EVIDENCE / "phs-620" / "module-metadata.yaml",
        module_id="module-01",
        operator_focus="Enhance existing course content after Confluence and Canvas access.",
    )


def test_bundles_preserve_source_purpose_scope_and_gaps() -> None:
    hai = _hai_bundle()
    phs = _phs_bundle()

    assert hai.course.source_purpose == "new_build"
    assert phs.course.source_purpose == "enhancement"
    assert hai.module.module_id == "module-01-foundations-of-ai-in-healthcare"
    assert phs.module.module_id == "module-01"
    assert hai.course_learning_objectives
    assert phs.course_learning_objectives
    assert hai.gap_ledger
    assert phs.gap_ledger
    assert any(gap.access_note for gap in hai.gap_ledger)
    assert any(gap.access_note for gap in phs.gap_ledger)
    assert all(
        entry.scope in {"course", "shared"} or entry.module_id == hai.module.module_id
        for entry in hai.scoped_source_manifest.entries
    )
    assert all(
        entry.scope in {"course", "shared"} or entry.module_id == phs.module.module_id
        for entry in phs.scoped_source_manifest.entries
    )


def test_asset_records_and_styleguide_fallback_are_honest() -> None:
    hai = _hai_bundle()
    phs = _phs_bundle()

    assert {record.status for record in hai.asset_records} == {"required_gap"}
    assert {record.status for record in phs.asset_records} == {"required_gap"}
    assert all(record.derivation == "syllabus_requirement" for record in hai.asset_records)
    assert all(record.derivation == "syllabus_requirement" for record in phs.asset_records)
    assert hai.styleguide_resolution.fallback is True
    assert phs.styleguide_resolution.fallback is True
    assert hai.styleguide_resolution.styleguide_id is None
    assert phs.styleguide_resolution.styleguide_id is None
    assert hai.styleguide_resolution.sme_key == "hai-510"
    assert phs.styleguide_resolution.sme_key == "phs-620"
    assert hai.styleguide_resolution.attribution != phs.styleguide_resolution.attribution
    assert hai.styleguide_resolution.styleguide_id is None
    assert "Tejal" not in hai.styleguide_resolution.reason or "not reuse Tejal" in hai.styleguide_resolution.reason
    assert "gap" in hai.styleguide_resolution.reason.lower() or "unbound" in hai.styleguide_resolution.reason.lower()

def test_scoped_manifest_recomputes_summary_counts() -> None:
    bundle = _hai_bundle()

    assert bundle.scoped_source_manifest.gap_summary == {
        gap.kind: sum(item.kind == gap.kind for item in bundle.gap_ledger)
        for gap in bundle.gap_ledger
    }
    assert bundle.scoped_source_manifest.detected["scaffold_file_count"] == sum(
        entry.source_role == "scaffold"
        for entry in bundle.scoped_source_manifest.entries
    )


def test_component_selection_contract_is_real_shape_without_reshaping() -> None:
    bundle = _hai_bundle()

    assert isinstance(bundle.component_selection, ComponentSelection)
    assert bundle.component_selection == ComponentSelection.model_validate(
        bundle.component_selection.model_dump()
    )
    assert bundle.component_selection.canonical_bytes()


def test_bundle_rejects_unknown_workflow_and_model_copy_bypass() -> None:
    bundle = _hai_bundle()

    with pytest.raises(ValidationError, match="unknown workflow"):
        LessonPlanningInputBundle.model_validate(
            bundle.model_dump(mode="json")
            | {"workflow_capabilities": ("deck", "quiz")}
        )

    with pytest.raises(ValidationError, match="gap_ledger"):
        bundle.model_copy(update={"gap_ledger": ()})

    with pytest.raises(ValidationError, match="asset_records"):
        bundle.model_copy(update={"asset_records": ()})


def test_bundle_rejects_non_verified_or_cross_course_proposal(tmp_path: Path) -> None:
    non_verified = tmp_path / "proposal.yaml"
    proposal_data = (EVIDENCE / "hai-510" / "module-metadata.yaml").read_text(
        encoding="utf-8"
    )
    non_verified.write_text(
        proposal_data.replace(
            "extraction_status: verified",
            "extraction_status: format_unsupported",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="verified"):
        build_lesson_planning_input_bundle(
            course_root=HAI_ROOT,
            proposal_path=non_verified,
            module_id="module-01-foundations-of-ai-in-healthcare",
            operator_focus="focus",
        )

    with pytest.raises(ValueError, match="course root"):
        build_lesson_planning_input_bundle(
            course_root=PHS_ROOT,
            proposal_path=EVIDENCE / "hai-510" / "module-metadata.yaml",
            module_id="module-01",
            operator_focus="focus",
        )


def test_bundle_rejects_missing_module_proposal(tmp_path: Path) -> None:
    proposal_data = (EVIDENCE / "phs-620" / "module-metadata.yaml").read_text(
        encoding="utf-8"
    )
    missing = tmp_path / "missing-module.yaml"
    missing.write_text(
        proposal_data.replace("status: proposed", "status: missing", 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing"):
        build_lesson_planning_input_bundle(
            course_root=PHS_ROOT,
            proposal_path=missing,
            module_id="module-01",
            operator_focus="focus",
        )


def test_bundle_output_fence_rejects_course_container_target(tmp_path: Path) -> None:
    assert_output_outside_course_root(HAI_ROOT, tmp_path / "bundle.yaml")

    with pytest.raises(ValueError, match="outside the course container"):
        assert_output_outside_course_root(HAI_ROOT, HAI_ROOT / "bundle.yaml")


def test_bundle_render_is_stable_and_schema_valid() -> None:
    bundle = _phs_bundle()
    first = render_input_bundle_yaml(bundle)
    second = render_input_bundle_yaml(bundle)

    assert first == second
    loaded = LessonPlanningInputBundle.model_validate_json(bundle.model_dump_json())
    assert loaded == bundle


def test_bundle_public_write_load_round_trip(tmp_path: Path) -> None:
    bundle = _hai_bundle()
    output = tmp_path / "input-bundle.yaml"

    assert write_input_bundle(bundle, output) == output
    assert load_input_bundle(output) == bundle


def test_story_d_negative_fence_has_no_trigger_path_edits() -> None:
    diff_paths = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    ).stdout.splitlines()

    forbidden = {
        "app/marcus/lesson_plan/composition.py",
        "app/models/state/component_selection.py",
        "app/marcus/lesson_plan/bundle_catalog.py",
        "app/marcus/cli/front_door.py",
        "state/config/pipeline-manifest.yaml",
    }
    assert forbidden.isdisjoint(diff_paths)
