from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.lesson_type_classifier import LessonTypeClassification
from app.marcus.lesson_plan.prework_artifact import (
    PromiseAuthoringReceipt,
    SceneAuthoringReceipt,
    WorkbookBriefArtifactV1,
    WorkbookBriefPayloadV1,
    WorkbookBriefRuntimeContext,
    WriterExecutionReceipt,
    canonical_payload_digest,
    read_workbook_brief,
    write_workbook_brief,
)
from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.promise_projection import PromiseGateReceipt
from app.marcus.lesson_plan.scene_extraction import SceneGateReceipt
from app.marcus.orchestrator import workbook_wiring
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.state.component_selection import ComponentSelection
from app.models.state.run_state import RunState
from app.specialists.workbook_producer._act import (
    WorkbookProducerActError,
    _reconcile_workbook_brief_authority,
)


def _brief() -> PreWorkBrief:
    scene = SceneBrief(
        status="authored",
        text="A recurring patient transport delay blocks the work.",
        source_refs=("assessments/chapter-2-knowledge-check.md#Q5",),
        known_losses=(),
        marker=None,
        lesson_type="fresh_pain",
        archetype="external_friction",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can identify the first move."),),
        known_losses=(),
        marker=None,
    )
    return PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=()),
    )


def test_workbook_brief_round_trip_and_payload_only_digest(tmp_path: Path) -> None:
    payload = WorkbookBriefPayloadV1(
        pre_work=_brief(),
        selected_seed_id="part2-q5",
        selected_seed_ref="assessments/chapter-2-knowledge-check.md#Q5",
        lesson_type="fresh_pain",
        archetype="external_friction",
        promise_authority_refs=("ratified-los.json#ratified_los/0",),
        encounter_mode="recorded",
        writer_execution_mode="offline_stub",
        scene_receipt=SceneAuthoringReceipt(
            classification=LessonTypeClassification(
                status="decisive",
                lesson_type="fresh_pain",
                archetype="external_friction",
                confidence=1.0,
                evidence_refs=("assessments/chapter-2-knowledge-check.md#Q5",),
            ),
            gate=SceneGateReceipt(failures=()),
        ),
        promise_receipt=PromiseAuthoringReceipt(
            gate=PromiseGateReceipt(),
            authority_refs=("ratified-los.json#ratified_los/0",),
        ),
        writer_receipts=(
            WriterExecutionReceipt(writer="scene", mode="offline_stub", calls=1),
            WriterExecutionReceipt(writer="promise", mode="offline_stub", calls=1),
        ),
        warnings=("operator_check",),
        known_losses=(),
    )
    artifact = WorkbookBriefArtifactV1(
        payload=payload, payload_digest=canonical_payload_digest(payload)
    )
    path = write_workbook_brief(tmp_path, artifact)
    assert path.name == "workbook-brief.v1.json"
    assert read_workbook_brief(tmp_path) == artifact
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["payload"]["node_id"] = "07W.2"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="coordinate|digest"):
        read_workbook_brief(tmp_path)


def test_runtime_context_origin_and_mode_are_strict(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=root,
        encounter_mode="live",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
    )
    assert context.encounter_mode == "live"
    with pytest.raises(ValueError):
        WorkbookBriefRuntimeContext(
            run_dir=tmp_path,
            course_source_root=None,
            encounter_mode="recorded",
            context_origin="new_start",
            writer_execution_mode="offline_stub",
        )


def _artifact() -> WorkbookBriefArtifactV1:
    payload = WorkbookBriefPayloadV1(
        pre_work=_brief(),
        selected_seed_id="part2-q5",
        selected_seed_ref="assessments/chapter-2-knowledge-check.md#Q5",
        lesson_type="fresh_pain",
        archetype="external_friction",
        promise_authority_refs=("ratified-los.json#ratified_los/0",),
        encounter_mode="recorded",
        writer_execution_mode="offline_stub",
        scene_receipt=SceneAuthoringReceipt(
            classification=LessonTypeClassification(
                status="decisive",
                lesson_type="fresh_pain",
                archetype="external_friction",
                confidence=1.0,
                evidence_refs=("assessments/chapter-2-knowledge-check.md#Q5",),
            ),
            gate=SceneGateReceipt(failures=()),
        ),
        promise_receipt=PromiseAuthoringReceipt(
            gate=PromiseGateReceipt(),
            authority_refs=("ratified-los.json#ratified_los/0",),
        ),
        writer_receipts=(
            WriterExecutionReceipt(writer="scene", mode="offline_stub", calls=1),
            WriterExecutionReceipt(writer="promise", mode="offline_stub", calls=1),
        ),
    )
    return WorkbookBriefArtifactV1(
        payload=payload, payload_digest=canonical_payload_digest(payload)
    )


def _state(envelope: ProductionEnvelope) -> RunState:
    return RunState(
        graph_version="v42",
        status="running",
        production_envelope=envelope,
        component_selection=ComponentSelection(deck=True, workbook=True),
    )


def test_terminal_requires_exact_real_contribution_authority(tmp_path: Path) -> None:
    artifact = _artifact()
    write_workbook_brief(tmp_path, artifact)
    real = ProductionEnvelope(trial_id=uuid4())
    real.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.1",
            output=workbook_wiring.workbook_brief_contribution_receipt(artifact),
            model_used="workbook-brief-offline",
        )
    )
    assert _reconcile_workbook_brief_authority(_state(real), tmp_path) == artifact

    planted = ProductionEnvelope(trial_id=real.trial_id)
    with pytest.raises(WorkbookProducerActError, match="no real contribution"):
        _reconcile_workbook_brief_authority(_state(planted), tmp_path)


def test_terminal_legacy_missing_and_corrupt_sidecar_tags(tmp_path: Path) -> None:
    legacy = ProductionEnvelope(trial_id=uuid4())
    legacy.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief_stub",
            node_id="07W.1",
            output={"stub_status": "not_yet_wired"},
            model_used="deterministic-workbook-band-stub",
        )
    )
    with pytest.raises(WorkbookProducerActError) as caught:
        _reconcile_workbook_brief_authority(_state(legacy), tmp_path)
    assert caught.value.tag == "workbook-brief.legacy-reentry-required"

    artifact = _artifact()
    real = ProductionEnvelope(trial_id=legacy.trial_id)
    real.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.1",
            output=workbook_wiring.workbook_brief_contribution_receipt(artifact),
            model_used="workbook-brief-offline",
        )
    )
    with pytest.raises(WorkbookProducerActError) as missing:
        _reconcile_workbook_brief_authority(_state(real), tmp_path)
    assert missing.value.tag == "workbook-brief.sidecar-invalid"
    (tmp_path / "workbook-brief.v1.json").write_text("{}", "utf-8")
    with pytest.raises(WorkbookProducerActError) as corrupt:
        _reconcile_workbook_brief_authority(_state(real), tmp_path)
    assert corrupt.value.tag == "workbook-brief.sidecar-invalid"


def test_atomic_writer_rejects_planted_temp_and_target_symlink(tmp_path: Path) -> None:
    artifact = _artifact()
    planted = tmp_path / "workbook-brief.v1.json.tmp"
    planted.write_text("attacker", "utf-8")
    with pytest.raises(ValueError, match="already exists"):
        write_workbook_brief(tmp_path, artifact)
    planted.unlink()
    outside = tmp_path / "outside.json"
    outside.write_text("untouched", "utf-8")
    target = tmp_path / "workbook-brief.v1.json"
    try:
        target.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(ValueError, match="symlink"):
        write_workbook_brief(tmp_path, artifact)
    assert outside.read_text("utf-8") == "untouched"
