"""AC-T.7 + AC-T.8 + AC-T.9 — summary rollup and deterministic emission."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.coverage_manifest import (
    CoverageInventoryEntry,
    CoverageManifestError,
    CoverageSurface,
    _load_story_statuses,
    emit_coverage_manifest,
    summarize_surfaces,
)
from app.marcus.lesson_plan.schema import PlanRef


def test_summary_marks_pending_rows_not_trial_ready() -> None:
    summary = summarize_surfaces(
        [
            CoverageSurface(
                step_id="05",
                surface_name="pending surface",
                owner_story_key="30-4-plan-lock-fanout",
                module_path="marcus/lesson_plan/step_05.py",
                artifact_kind="envelope",
                plan_ref_mode="top-level-fields",
                has_lesson_plan_revision=False,
                has_lesson_plan_digest=False,
                assert_plan_fresh_required=True,
                assert_plan_fresh_verified=False,
                status="pending",
                notes="Still pending.",
            )
        ]
    )
    assert summary.pending_surfaces == 1
    assert summary.trial_ready is False


def test_emit_coverage_manifest_is_deterministic_for_unchanged_inputs(tmp_path: Path) -> None:
    fixtures_root = (
        Path(__file__).resolve().parent / "fixtures" / "lesson_plan" / "coverage_manifest"
    )
    inventory = [
        CoverageInventoryEntry(
            step_id="11",
            surface_name="wrapper consumer boundary",
            owner_story_key="story-b",
            module_path=str(fixtures_root.relative_to(Path.cwd()) / "wrapper_consumer.py"),
            artifact_kind="produced-asset",
            plan_ref_mode="nested-plan-ref",
            assert_plan_fresh_required=True,
            notes="Implemented nested boundary.",
            consumer_entrypoint="consume",
            sample_factory=lambda: SimpleNamespace(
                plan_ref=PlanRef(lesson_plan_revision=5, lesson_plan_digest="abc")
            ),
        ),
        CoverageInventoryEntry(
            step_id="05",
            surface_name="direct consumer boundary",
            owner_story_key="story-a",
            module_path=str(fixtures_root.relative_to(Path.cwd()) / "direct_consumer.py"),
            artifact_kind="envelope",
            plan_ref_mode="top-level-fields",
            assert_plan_fresh_required=True,
            notes="Implemented top-level boundary.",
            consumer_entrypoint="consume",
            sample_factory=lambda: SimpleNamespace(
                lesson_plan_revision=5,
                lesson_plan_digest="abc",
            ),
        ),
    ]
    story_statuses = {"story-a": "done", "story-b": "done"}
    fixed_now = datetime(2026, 4, 18, 12, 0, tzinfo=UTC)
    target = tmp_path / "coverage.json"

    first = emit_coverage_manifest(
        inventory=inventory,
        project_root=Path.cwd(),
        story_statuses=story_statuses,
        generated_at=fixed_now,
        output_path=target,
    )
    first_bytes = target.read_bytes()
    second = emit_coverage_manifest(
        inventory=inventory,
        project_root=Path.cwd(),
        story_statuses=story_statuses,
        generated_at=fixed_now,
        output_path=target,
    )
    second_bytes = target.read_bytes()

    assert [surface.surface_name for surface in first.surfaces] == [
        "direct consumer boundary",
        "wrapper consumer boundary",
    ]
    assert first.summary.trial_ready is True
    assert second.summary.trial_ready is True
    assert first_bytes == second_bytes


def test_emit_coverage_manifest_rejects_unknown_owner_story_key(tmp_path: Path) -> None:
    fixtures_root = (
        Path(__file__).resolve().parent / "fixtures" / "lesson_plan" / "coverage_manifest"
    )
    inventory = [
        CoverageInventoryEntry(
            step_id="05",
            surface_name="direct consumer boundary",
            owner_story_key="unknown-story",
            module_path=str(fixtures_root.relative_to(Path.cwd()) / "direct_consumer.py"),
            artifact_kind="envelope",
            plan_ref_mode="top-level-fields",
            assert_plan_fresh_required=True,
            notes="Should fail fast on unknown sprint-status owner key.",
            consumer_entrypoint="consume",
            sample_factory=lambda: SimpleNamespace(
                lesson_plan_revision=5,
                lesson_plan_digest="abc",
            ),
        )
    ]

    with pytest.raises(CoverageManifestError, match="unknown-story"):
        emit_coverage_manifest(
            inventory=inventory,
            project_root=Path.cwd(),
            story_statuses={},
            generated_at=datetime(2026, 4, 18, 12, 0, tzinfo=UTC),
            output_path=tmp_path / "coverage.json",
        )


def test_load_story_statuses_accepts_letter_suffixed_story_keys(tmp_path: Path) -> None:
    sprint_status = tmp_path / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    sprint_status.parent.mkdir(parents=True)
    sprint_status.write_text(
        "\n".join(
            [
                "development_status:",
                "  30-2b-pre-packet-envelope-emission: backlog",
                "  30-3a-4a-skeleton-and-lock: review",
                "  32-2-plan-ref-envelope-coverage-manifest: in-progress",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert _load_story_statuses(tmp_path) == {
        "30-2b-pre-packet-envelope-emission": "backlog",
        "30-3a-4a-skeleton-and-lock": "review",
        "32-2-plan-ref-envelope-coverage-manifest": "in-progress",
    }
