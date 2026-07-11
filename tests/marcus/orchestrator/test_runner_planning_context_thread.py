"""Live tests: runner threads planning_context to Irene Pass-1 only (AC-H2)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.marcus.lesson_plan.source_assessment import GapSummary, SourceAssessment
from app.specialists.dispatch_errors import SpecialistDispatchError

TRIAL_ID = UUID("abcdef00-1234-4234-8234-abcdef012345")


def _write_valid_ratification(run_dir: Path) -> None:
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


def _write_valid_ratified_los(run_dir: Path) -> None:
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


def _seed_run_dir(runs_root: Path, trial_id: UUID) -> Path:
    run_dir = runs_root / str(trial_id)
    run_dir.mkdir(parents=True)
    _write_valid_ratification(run_dir)
    _write_valid_ratified_los(run_dir)
    return run_dir


def _floor_directive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: int) -> Path:
    """Mirror test_irene_pass1_floor_threading's positive arrangement: temp SSOT
    binding ``scripted.min_cluster_floor = value`` + a directive that binds it."""
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "style_guides": {
                    "multi-beat": {
                        "production_mode": "api",
                        "scripted": [
                            {
                                "class": "min_cluster_floor",
                                "value": value,
                                "rationale": "multi-beat walk",
                                "provenance": {
                                    "authoring_styleguide": "x",
                                    "envelope_write_stamp": "z",
                                },
                            }
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {"gamma_settings": [{"variant_id": "A", "styleguide": "multi-beat"}]}
        ),
        encoding="utf-8",
    )
    return directive


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


@pytest.mark.parametrize("specialist_id", ["irene_pass1", "irene-pass1"])
@pytest.mark.parametrize(
    "zero_byte_companion",
    ["ratification-only", "valid-ratification-plus-zero-byte-los"],
)
def test_zero_byte_planning_context_raises_specialist_dispatch_error(
    tmp_path: Path, specialist_id: str, zero_byte_companion: str
) -> None:
    """0-byte companion at the runner seam fails LOUD, never silent framing.

    Parametrized over BOTH alias forms (F1 lesson: the walk passes the
    CANONICALIZED underscore id; a hyphen-only pin would miss a regression on
    every real dispatch) AND over WHICH companion is 0-byte (ratification
    alone vs valid ratification + 0-byte ratified-los).
    """
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    if zero_byte_companion == "ratification-only":
        (run_dir / "planning-ratification.json").write_bytes(b"")
    else:
        _write_valid_ratification(run_dir)
        (run_dir / "ratified-los.json").write_bytes(b"")
    with pytest.raises(SpecialistDispatchError, match="planning_context") as excinfo:
        _runner_payload_for_specialist(
            specialist_id=specialist_id,
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=TRIAL_ID,
        )
    assert excinfo.value.tag == "irene_pass1.planning_context.malformed"


def test_empty_object_companions_omit_planning_context_key(tmp_path: Path) -> None:
    """``{}`` companions → NO planning_context key in the irene payload.

    Empty-but-present companions are treated as absent by explicit design
    (the has_framing() treat-as-absent return in load_planning_context): the
    loader returns None and the runner seam omits the key entirely — never a
    partial/phantom framing dict. Whether empty-but-present should warn
    instead is filed in _bmad-output/implementation-artifacts/deferred-work.md
    (warn-on-empty design question), not decided by this pin.
    """
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    (run_dir / "planning-ratification.json").write_text("{}", encoding="utf-8")
    (run_dir / "ratified-los.json").write_text("{}", encoding="utf-8")
    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1",
        directive_path=None,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=TRIAL_ID,
    )
    # No floor + treat-as-absent context → EXACTLY None (empty dict collapses
    # via ``irene_payload or None``); never a dict carrying an explicit None.
    assert payload is None


def test_empty_object_companions_with_floor_yield_floor_only_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``{}`` companions + a bound floor → floor-only dict, NO planning_context key.

    Makes the dict arm live: when the directive threads min_cluster_floor the
    payload IS a dict, and the never-leak-explicit-None invariant requires the
    planning_context key to be entirely ABSENT from it (not present-with-None).
    """
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    (run_dir / "planning-ratification.json").write_text("{}", encoding="utf-8")
    (run_dir / "ratified-los.json").write_text("{}", encoding="utf-8")
    directive = _floor_directive(tmp_path, monkeypatch, 5)
    payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1",
        directive_path=directive,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=TRIAL_ID,
    )
    assert payload == {"min_cluster_floor": 5}
    assert "planning_context" not in payload


@pytest.mark.parametrize("specialist_id", ["irene_pass1", "irene-pass1"])
def test_malformed_planning_context_raises_specialist_dispatch_error(
    tmp_path: Path, specialist_id: str
) -> None:
    """Malformed companion fails LOUD under BOTH alias forms (F1 lesson)."""
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    (run_dir / "planning-ratification.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(SpecialistDispatchError, match="planning_context") as excinfo:
        _runner_payload_for_specialist(
            specialist_id=specialist_id,
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=TRIAL_ID,
        )
    assert excinfo.value.tag == "irene_pass1.planning_context.malformed"
