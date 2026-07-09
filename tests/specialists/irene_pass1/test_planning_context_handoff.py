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
    assess_lo_coverage,
    assert_lo_coverage_or_fail,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene_pass1 import _act as pass1_act


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(content=self.response_text, usage_metadata=None)


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
    corpus = "# Corpus\n\nGenerative AI in clinic documentation risks."
    (bundle / "extracted.md").write_text(corpus, encoding="utf-8")
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
    # Prompt must have carried the labeled section (Murat three-signal).
    assert handle.chat.calls
    user = handle.chat.calls[0][1]["content"]
    assert pass1_act._PLANNING_CONTEXT_SECTION_MARKER in user


def test_act_fails_loud_on_total_ignore(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# Corpus\n\nRocks.", encoding="utf-8")
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


def test_absent_path_act_unchanged_no_receipt(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# Corpus\n\nCells.", encoding="utf-8")
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
    corpus_path = bundle / "extracted.md"
    corpus = "# Corpus\n\nImmutable source text for hash pin.\n"
    corpus_path.write_text(corpus, encoding="utf-8")
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
    (bundle / "extracted.md").write_text("# Corpus\n\nClinic AI.", encoding="utf-8")
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
