"""Live tests: runner threads planning_context to Irene Pass-1 only (AC-H2)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.marcus.lesson_plan.source_assessment import GapSummary, SourceAssessment
from app.specialists.dispatch_errors import SpecialistDispatchError

TRIAL_ID = UUID("abcdef00-1234-4234-8234-abcdef012345")


def _seed_run_dir(runs_root: Path, trial_id: UUID) -> Path:
    run_dir = runs_root / str(trial_id)
    run_dir.mkdir(parents=True)
    assessment = SourceAssessment(
        course_or_corpus_id="hai-510",
        richness="thin",
        tags=("course-source-bundle", "module:module-01"),
        gap_summaries=(
            GapSummary(kind="missing_lecture_video", count=1, sample_message="no video"),
        ),
        gap_count=1,
        asset_record_count=2,
        detected_file_count=3,
    )
    (run_dir / "planning-ratification.json").write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "purpose": "Teach clinicians when generative AI is appropriate",
                "audience": "Practicing clinicians new to generative AI",
                "source_assessment": assessment.model_dump(mode="json"),
                "assets_to_create": [],
                "workflow": "narrated-deck",
                "gap_fill": {
                    "chosen": "synthesize",
                    "considered": ["synthesize", "wait"],
                    "rationale": "thin",
                },
                "claim_fence": (
                    "Does not claim full lecture ingestion or "
                    "lecture-complete selection."
                ),
                "s8_intent": {
                    "ratification_status": "ratified",
                    "bundle_id": "narrated-deck",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "ratified-los.json").write_text(
        json.dumps(
            {
                "ratified_los": [
                    {
                        "objective_id": "lo-001",
                        "statement": "Identify appropriate generative-AI use cases",
                        "bloom_level": "understand",
                        "status": "ratified",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_dir


def test_irene_pass1_receives_planning_context_when_artifacts_present(
    tmp_path: Path,
) -> None:
    _seed_run_dir(tmp_path, TRIAL_ID)
    for specialist_id in ("irene_pass1", "irene-pass1"):
        payload = _runner_payload_for_specialist(
            specialist_id=specialist_id,
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=TRIAL_ID,
        )
        assert payload is not None
        assert "planning_context" in payload
        ctx = payload["planning_context"]
        assert "clinicians" in ctx["purpose"].lower()
        assert len(ctx["learning_objectives"]) == 1


def test_irene_pass1_omits_planning_context_when_absent(tmp_path: Path) -> None:
    (tmp_path / str(TRIAL_ID)).mkdir(parents=True)
    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1",
        directive_path=None,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=TRIAL_ID,
    )
    # No floor, no planning context → None (clean; no None-leak of the key)
    assert payload is None or "planning_context" not in (payload or {})


def test_other_specialists_do_not_receive_planning_context(tmp_path: Path) -> None:
    _seed_run_dir(tmp_path, TRIAL_ID)
    for specialist_id in ("texas", "gary", "irene", "kira", "cd"):
        payload = _runner_payload_for_specialist(
            specialist_id=specialist_id,
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=TRIAL_ID,
        )
        if payload is None:
            continue
        assert "planning_context" not in payload


def test_malformed_planning_context_raises_specialist_dispatch_error(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    (run_dir / "planning-ratification.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(SpecialistDispatchError, match="planning_context") as excinfo:
        _runner_payload_for_specialist(
            specialist_id="irene_pass1",
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=TRIAL_ID,
        )
    assert excinfo.value.tag == "irene_pass1.planning_context.malformed"
