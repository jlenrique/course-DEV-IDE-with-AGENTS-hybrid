"""Live tests: planning_context prompt section + LO coverage receipt (AC-H3/H5).

Also covers absent-path prompt stability (AC-H4) and corpus hash pin (AC-H6).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.marcus.lesson_plan.planning_context import (
    LearningObjectiveBrief,
    PlanningContext,
    assert_lo_coverage_or_fail,
    assess_lo_coverage,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene_pass1 import _act as pass1_act
from tests._helpers.pass1_bundle import write_primary_slide_bundle
from tests._helpers.pass1_catalog_response import select_catalog_ids


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(
            content=select_catalog_ids(self.response_text, messages),
            usage_metadata=None,
        )


@dataclass
class _RecordingHandle:
    response_text: str
    chat: _RecordingChat = field(init=False)

    def __post_init__(self) -> None:
        self.chat = _RecordingChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


def _unit(
    *,
    unit_id: str = "u1",
    title: str = "T",
    learning_objective: str = "lo",
) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "title": title,
        "learning_objective": learning_objective,
        "scope_decision": "in-scope",
        "rationale": "r",
        "cluster_id": f"c-{unit_id}",
        "cluster_role": "head",
        "cluster_position": "establish",
        "narrative_arc": "From a to b through c",
        "master_behavioral_intent": "credible",
        "cluster_interstitial_count": 0,
        "source_refs": ["anchor one"],
    }


def _response_for_units(units: list[dict[str, Any]]) -> str:
    return json.dumps({"lesson_summary": "s", "plan_units": units})


def _planning_context_payload() -> dict[str, Any]:
    return PlanningContext(
        purpose="Teach clinicians when generative AI is appropriate",
        audience="Practicing clinicians new to generative AI",
        learning_objectives=(
            LearningObjectiveBrief(
                objective_id="lo-001",
                statement="Identify appropriate generative-AI use cases in clinic",
            ),
            LearningObjectiveBrief(
                objective_id="lo-002",
                statement="List risks of generative AI in clinical documentation",
            ),
        ),
        sources_present=("planning-ratification.json", "ratified-los.json"),
    ).to_payload_dict()


def test_prompt_surfaces_labeled_planning_context_section() -> None:
    _, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1", "planning_context": _planning_context_payload()},
        extracted_source="# Corpus\n\nCells divide.",
    )
    assert pass1_act._PLANNING_CONTEXT_SECTION_MARKER in user
    assert "FRAMING ONLY" in user
    assert "ONLY topic/source-of-truth" in user or "ONLY planning basis" in user
    assert "Identify appropriate generative-AI use cases" in user
    assert "Teach clinicians" in user
    # Corpus still leads and remains the topic basis marker.
    assert user.index("Source corpus") < user.index(
        pass1_act._PLANNING_CONTEXT_SECTION_MARKER
    )
    # BH-4: planning_context must NOT also appear unlabeled in envelope JSON.
    assert '"planning_context"' not in user
    assert "planning_context" not in user.split("## Envelope payload")[-1]


def test_absent_planning_context_omits_section() -> None:
    _, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"},
        extracted_source="# Corpus\n\nCells divide.",
    )
    assert pass1_act._PLANNING_CONTEXT_SECTION_MARKER not in user


def test_soft_receipt_partial_coverage() -> None:
    ctx = PlanningContext.model_validate(_planning_context_payload())
    plan = {
        "plan_units": [
            _unit(
                title="Clinic use cases",
                learning_objective=(
                    "Identify appropriate generative-AI use cases in clinic"
                ),
            )
        ]
    }
    receipt = assess_lo_coverage(ctx, plan)
    assert receipt.lo_coverage == "partial"
    assert "lo-001" in receipt.supported_objective_ids
    assert "lo-002" in receipt.weak_or_missing_objective_ids
    assert_lo_coverage_or_fail(ctx, receipt)  # partial must NOT fail


def test_fail_loud_on_total_lo_ignore() -> None:
    ctx = PlanningContext.model_validate(_planning_context_payload())
    plan = {
        "plan_units": [
            _unit(title="Unrelated geology", learning_objective="Name rock types")
        ]
    }
    receipt = assess_lo_coverage(ctx, plan)
    assert receipt.lo_coverage == "absent"
    with pytest.raises(SpecialistDispatchError, match="totally ignored"):
        assert_lo_coverage_or_fail(ctx, receipt)


def test_fail_loud_on_empty_plan_units_with_los() -> None:
    ctx = PlanningContext.model_validate(_planning_context_payload())
    receipt = assess_lo_coverage(ctx, {"plan_units": []})
    assert receipt.lo_coverage == "absent"
    with pytest.raises(SpecialistDispatchError, match="totally ignored"):
        assert_lo_coverage_or_fail(ctx, receipt)


def test_act_emits_coverage_receipt_on_partial(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    corpus = "# Corpus\n\nGenerative AI in clinic documentation risks.\nanchor one"
    write_primary_slide_bundle(bundle, corpus)
    # Seed companion files so provenance digests can be computed.
    run_dir = tmp_path / "run-pc-partial"
    run_dir.mkdir()
    (run_dir / "planning-ratification.json").write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "purpose": "Teach clinicians when generative AI is appropriate",
                "audience": "Practicing clinicians new to generative AI",
                "source_assessment": {
                    "course_or_corpus_id": "hai",
                    "richness": "thin",
                    "tags": ["course-source-bundle", "module:m1"],
                    "gap_summaries": [],
                    "gap_count": 0,
                    "asset_record_count": 1,
                    "detected_file_count": 1,
                },
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
            }
        ),
        encoding="utf-8",
    )
    units = [
        _unit(
            title="Clinic use cases for generative AI",
            learning_objective=(
                "Identify appropriate generative-AI use cases in clinic"
            ),
        )
    ]
    handle = _RecordingHandle(_response_for_units(units))
    result = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-pc-partial",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
                "planning_context": _planning_context_payload(),
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert "planning_context_coverage" in output
    assert output["planning_context_coverage"]["lo_coverage"] == "partial"
    assert "planning_provenance" in output["lesson_plan"]
    prov = output["lesson_plan"]["planning_provenance"]
    assert prov["schema_version"] == "0.1"
    assert prov["ratification_path"] == "planning-ratification.json"
    assert prov["ratification_digest"] and prov["ratification_digest"].startswith(
        "sha256:"
    )
    assert prov["coverage_lo_status"] == "partial"
    # Prompt must have carried the labeled section (Murat three-signal).
    assert handle.chat.calls
    user = handle.chat.calls[0][1]["content"]
    assert pass1_act._PLANNING_CONTEXT_SECTION_MARKER in user


def test_locked_act_uses_resolved_root_when_payload_omits_runs_root(
    tmp_path: Path,
) -> None:
    run_id = "run-pc-resolved-root"
    payload_run_id = "payload-run-id-must-not-win"
    bundle = tmp_path / "bundle-resolved-root"
    bundle.mkdir()
    write_primary_slide_bundle(
        bundle, "# Corpus\n\nGenerative AI clinic use cases.\nanchor one"
    )
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    ratification = b'{"ratified":true}\n'
    (run_dir / "planning-ratification.json").write_bytes(ratification)
    payload = {
        "mode": "pass-1",
        "run_id": payload_run_id,
        "bundle_reference": str(bundle),
        "planning_context": _planning_context_payload(),
    }
    units = [
        _unit(
            title="Clinic use cases for generative AI",
            learning_objective="Identify appropriate generative-AI use cases in clinic",
        )
    ]
    result = pass1_act._act_locked(
        _state(payload),
        handle=_RecordingHandle(_response_for_units(units)),
        model_id="gpt-5.4",
        payload=payload,
        run_id=run_id,
        runs_root=tmp_path,
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    provenance = output["planning_provenance"]
    assert provenance == output["lesson_plan"]["planning_provenance"]
    assert provenance["ratification_path"] == "planning-ratification.json"
    assert provenance["ratification_digest"] == (
        "sha256:" + hashlib.sha256(ratification).hexdigest()
    )
    assert not (tmp_path / payload_run_id).exists()


def test_coverage_failure_uses_resolved_root_when_payload_omits_runs_root(
    tmp_path: Path,
) -> None:
    run_id = "run-pc-ignore-resolved-root"
    payload_run_id = "payload-ignore-run-id-must-not-win"
    bundle = tmp_path / "bundle-ignore-resolved-root"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nRocks.\nanchor one")
    payload = {
        "mode": "pass-1",
        "run_id": payload_run_id,
        "bundle_reference": str(bundle),
        "planning_context": _planning_context_payload(),
    }
    handle = _RecordingHandle(
        _response_for_units(
            [_unit(title="Geology intro", learning_objective="Name rock types")]
        )
    )
    with pytest.raises(SpecialistDispatchError, match="totally ignored"):
        pass1_act._act_locked(
            _state(payload),
            handle=handle,
            model_id="gpt-5.4",
            payload=payload,
            run_id=run_id,
            runs_root=tmp_path,
        )
    receipt_path = tmp_path / run_id / "planning-context-coverage.json"
    assert receipt_path.is_file()
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["lo_coverage"] == (
        "absent"
    )
    assert not (tmp_path / payload_run_id).exists()


def test_absent_path_omits_planning_provenance(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nCells.\nanchor one")
    handle = _RecordingHandle(_response_for_units([_unit()]))
    result = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-pc-absent-prov",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert "planning_provenance" not in output
    assert "planning_provenance" not in output["lesson_plan"]


def test_claim_b_plan_delta_vs_control_hashes(tmp_path: Path) -> None:
    """Claim B: treatment plan with context differs from control without context."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(
        bundle, "# Corpus\n\nClinic generative AI documentation.\nanchor one"
    )
    units_control = [_unit(title="Generic intro", learning_objective="Cover basics")]
    units_treatment = [
        _unit(
            title="Clinic use cases for generative AI",
            learning_objective=(
                "Identify appropriate generative-AI use cases in clinic"
            ),
        ),
        _unit(
            unit_id="u2",
            title="Documentation risks of generative AI",
            learning_objective=(
                "List risks of generative AI in clinical documentation"
            ),
        ),
    ]
    control = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "control",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=_RecordingHandle(_response_for_units(units_control)),
        model_id="gpt-5.4",
    )
    treatment = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "treatment",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
                "planning_context": _planning_context_payload(),
            }
        ),
        handle=_RecordingHandle(_response_for_units(units_treatment)),
        model_id="gpt-5.4",
    )
    c_out = json.loads(control["cache_state"]["cache_prefix"])
    t_out = json.loads(treatment["cache_state"]["cache_prefix"])
    c_hash = hashlib.sha256(
        Path(c_out["artifact_path"]).read_bytes()
    ).hexdigest()
    t_hash = hashlib.sha256(
        Path(t_out["artifact_path"]).read_bytes()
    ).hexdigest()
    assert c_hash != t_hash
    assert "planning_context_coverage" in t_out
    assert t_out["planning_context_coverage"]["lo_coverage"] == "present"
    assert "planning_provenance" in t_out["lesson_plan"]
    assert "planning_provenance" not in c_out["lesson_plan"]
    # Purpose/audience ack when tokens overlap plan text.
    assert t_out["planning_context_coverage"]["purpose_acknowledged"] is True
    assert t_out["planning_context_coverage"]["audience_acknowledged"] is True


def test_act_fails_loud_on_total_ignore(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nRocks.\nanchor one")
    handle = _RecordingHandle(
        _response_for_units(
            [_unit(title="Geology intro", learning_objective="Name rock types")]
        )
    )
    with pytest.raises(SpecialistDispatchError, match="totally ignored"):
        pass1_act.act(
            _state(
                {
                    "mode": "pass-1",
                    "run_id": "run-pc-ignore",
                    "runs_root": str(tmp_path),
                    "bundle_reference": str(bundle),
                    "planning_context": _planning_context_payload(),
                }
            ),
            handle=handle,
            model_id="gpt-5.4",
        )


def test_authority_failure_precedes_planning_coverage_persistence(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nRocks.")
    candidate = json.loads(_response_for_units([_unit()]))
    candidate["plan_units"][0].pop("source_refs", None)
    candidate["plan_units"][0]["source_ref_ids"] = [
        "span:sha256:" + "f" * 64
    ]
    handle = _RecordingHandle(json.dumps(candidate))
    run_id = "run-authority-before-coverage"

    with pytest.raises(pass1_act.Pass1AuthorityError, match="unknown or stale"):
        pass1_act.act(
            _state(
                {
                    "mode": "pass-1",
                    "run_id": run_id,
                    "runs_root": str(tmp_path),
                    "bundle_reference": str(bundle),
                    "planning_context": _planning_context_payload(),
                }
            ),
            handle=handle,
            model_id="gpt-5.4",
        )

    assert len(handle.chat.calls) == 1
    assert not (tmp_path / run_id / "planning-context-coverage.json").exists()


def test_absent_path_act_unchanged_no_receipt(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nCells.\nanchor one")
    handle = _RecordingHandle(_response_for_units([_unit()]))
    result = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-pc-absent",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert "planning_context_coverage" not in output
    user = handle.chat.calls[0][1]["content"]
    assert pass1_act._PLANNING_CONTEXT_SECTION_MARKER not in user


def test_corpus_bytes_unchanged_after_prompt_assembly(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    corpus = "# Corpus\n\nImmutable source text for hash pin.\n"
    corpus_path = write_primary_slide_bundle(bundle, corpus)
    before = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
    pass1_act.assemble_pass1_prompt(
        {
            "mode": "pass-1",
            "planning_context": _planning_context_payload(),
            "bundle_reference": str(bundle),
        },
        extracted_source=corpus,
    )
    after = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
    assert before == after


def test_lesson_plan_artifact_still_written(tmp_path: Path) -> None:
    """AC-H6 continuity: lesson_plan artifact path still produced."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "# Corpus\n\nClinic AI.\nanchor one")
    units = [
        _unit(
            title="Clinic use cases for generative AI",
            learning_objective=(
                "Identify appropriate generative-AI use cases in clinic"
            ),
        ),
        _unit(
            unit_id="u2",
            title="Documentation risks of generative AI",
            learning_objective=(
                "List risks of generative AI in clinical documentation"
            ),
        ),
    ]
    handle = _RecordingHandle(_response_for_units(units))
    result = pass1_act.act(
        _state(
            {
                "mode": "pass-1",
                "run_id": "run-pc-continuity",
                "runs_root": str(tmp_path),
                "bundle_reference": str(bundle),
                "planning_context": _planning_context_payload(),
            }
        ),
        handle=handle,
        model_id="gpt-5.4",
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert output["planning_context_coverage"]["lo_coverage"] == "present"
    artifact = Path(output["artifact_path"])
    assert artifact.is_file()
    written = artifact.read_text(encoding="utf-8")
    assert "Irene Pass-1 Lesson Plan" in written
    assert "plan_units" in output["lesson_plan"]
    assert len(output["lesson_plan"]["plan_units"]) == 2
    # Consumer-shaped continuity: SPOC narrate path reads irene-pass1.md.
    assert artifact.name == "irene-pass1.md"
    assert (tmp_path / "run-pc-continuity" / "irene-pass1.md").is_file()
    # Envelope contribution shape used by lesson_plan_from_run consumers.
    assert isinstance(output["lesson_plan"], dict)
    assert output["specialist_id"] == "irene_pass1"
