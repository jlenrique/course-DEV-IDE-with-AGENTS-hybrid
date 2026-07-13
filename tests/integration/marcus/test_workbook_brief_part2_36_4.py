import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.prework_artifact import WorkbookBriefRuntimeContext, read_workbook_brief
from app.marcus.lesson_plan.prework_projection import (
    ObjectiveInput,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.promise_projection import PromiseObjectiveResolution
from app.marcus.orchestrator import workbook_wiring
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.specialists.dispatch_errors import SpecialistDispatchError

ROOT = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()
FIXTURES = Path("tests/fixtures/prework_36_4")


class SceneWriter:
    def __init__(self):
        self.calls = 0

    def __call__(self, request):
        self.calls += 1
        return SceneBrief(
            status="authored",
            text=request.seed_text,
            source_refs=request.source_refs,
            known_losses=(),
            marker=None,
            lesson_type=request.lesson_type,
            archetype=request.archetype,
        )


class PromiseWriter:
    def __init__(self):
        self.calls = 0

    def __call__(self, request):
        self.calls += 1
        return PromiseProjection(
            status="authored",
            vows=tuple(
                PromiseVow(
                    objective_id=o.objective_id, text="I can identify the first workflow move."
                )
                for o in request.objectives
            ),
            known_losses=(),
            marker=None,
        )


def test_part2_real_factory_is_exact_once_and_digest_bound(tmp_path, monkeypatch) -> None:
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(
                objective_id="LO-1", text="Identify the first workflow move.", status="ratified"
            ),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _run: resolution)
    scene, promise = SceneWriter(), PromiseWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
        scene_writer=scene,
        promise_writer=promise,
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=ProductionEnvelope(trial_id=uuid4()),
        runtime_context=context,
    )
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=envelope,
        runtime_context=context,
    )
    artifact = read_workbook_brief(tmp_path)
    assert repeated is envelope
    assert scene.calls == promise.calls == 1
    assert artifact.payload.selected_seed_id == "part2-q5"
    assert artifact.payload.selected_seed_ref.endswith("chapter-2-knowledge-check.md#Q5")
    assert artifact.payload.lesson_type == "fresh_pain"
    assert artifact.payload.archetype == "external_friction"
    assert artifact.payload.pre_work.scene.status == "authored"
    assert artifact.payload.pre_work.promise.status == "authored"
    assert tuple(receipt.calls for receipt in artifact.payload.writer_receipts) == (1, 1)
    expected = json.loads((FIXTURES / "deterministic-expected-receipt.json").read_text("utf-8"))
    assert artifact.payload.schema_version == expected["schema_version"]
    assert artifact.payload.node_id == expected["node_id"]
    assert artifact.payload.specialist_id == expected["specialist_id"]
    assert list(artifact.payload.pre_work.beat_order) == expected["beat_order"]
    assert artifact.payload.lesson_type == expected["lesson_type"]
    assert artifact.payload.archetype == expected["archetype"]
    assert [receipt.calls for receipt in artifact.payload.writer_receipts] == expected[
        "writer_calls"
    ]


def test_missing_source_and_objectives_are_zero_call_honest_unavailable(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        workbook_wiring,
        "load_part2_scene_source",
        lambda _root: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )
    monkeypatch.setattr(
        workbook_wiring,
        "resolve_promise_objectives",
        lambda _run: PromiseObjectiveResolution(
            status="unavailable", known_losses=("promise_ratified_los_absent",)
        ),
    )
    scene, promise = SceneWriter(), PromiseWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
        scene_writer=scene,
        promise_writer=promise,
    )
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=ProductionEnvelope(trial_id=uuid4()),
        runtime_context=context,
    )
    artifact = read_workbook_brief(tmp_path)
    assert scene.calls == promise.calls == 0
    assert artifact.payload.pre_work.scene.status == "unavailable"
    assert artifact.payload.pre_work.promise.status == "unavailable"
    assert tuple(receipt.calls for receipt in artifact.payload.writer_receipts) == (0, 0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_path", "planted.json"),
        ("artifact_path", ""),
        ("schema_version", "workbook-brief.v0"),
        ("node_id", "07W.2"),
        ("specialist_id", "wrong"),
        ("status_summary", {"scene": "authored", "promise": "degraded"}),
        ("warning_summary", []),
        ("loss_summary", ["planted"]),
    ],
)
def test_resume_rejects_any_mutated_contribution_receipt(
    tmp_path, monkeypatch, field, value
) -> None:
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Identify a move.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _run: resolution)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=ProductionEnvelope(trial_id=uuid4()),
        runtime_context=context,
    )
    original = envelope.contributions[0]
    output = dict(original.output)
    output[field] = value
    planted = ProductionEnvelope(trial_id=envelope.trial_id)
    planted.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.1",
            output=output,
            model_used=original.model_used,
        )
    )
    with pytest.raises(SpecialistDispatchError, match="mismatch"):
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=planted, runtime_context=context
        )
