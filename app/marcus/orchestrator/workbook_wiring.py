"""Deterministic orchestration seam for the four-node workbook band."""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Final, Literal, TypeAlias

from app.marcus.lesson_plan.lesson_type_classifier import (
    LessonTypeClassification,
    LessonTypeEvidence,
)
from app.marcus.lesson_plan.prework_artifact import (
    PromiseAuthoringReceipt,
    SceneAuthoringReceipt,
    WorkbookBriefArtifactV1,
    WorkbookBriefPayloadV1,
    WorkbookBriefRuntimeContext,
    WriterExecutionReceipt,
    canonical_payload_digest,
    read_runtime_context,
    read_workbook_brief,
    write_workbook_brief,
)
from app.marcus.lesson_plan.prework_from_run import load_part2_scene_source
from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    SceneBrief,
    offline_promise_transformer,
    offline_scene_composer,
)
from app.marcus.lesson_plan.promise_projection import (
    PromiseProjectionRequest,
    compose_promise_projection,
    resolve_promise_objectives,
)
from app.marcus.lesson_plan.research_packet import (
    ASK_A_ENRICHMENT_NODE_ID,
    ASK_A_ENRICHMENT_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
    ASK_B_HOT_TOPICS_SPECIALIST_ID,
)
from app.marcus.lesson_plan.scene_extraction import (
    SceneGateReceipt,
    SceneProjectionRequest,
    compose_scene_projection,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.specialists.dispatch_errors import SpecialistDispatchError

WORKBOOK_BRIEF_NODE_ID: Final[str] = "07W.1"
WORKBOOK_REVIEW_NODE_ID: Final[str] = "07W.3"
WORKBOOK_BRIEF_SPECIALIST_ID: Final[str] = "workbook_brief"
LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID: Final[str] = "workbook_brief_stub"
WORKBOOK_REVIEW_SPECIALIST_ID: Final[str] = "workbook_review_stub"
WORKBOOK_BAND_MODEL_MARKER: Final[str] = "deterministic-workbook-band-stub"
WORKBOOK_BAND_NODE_IDS: Final[tuple[str, ...]] = (
    WORKBOOK_BRIEF_NODE_ID,
    ASK_A_ENRICHMENT_NODE_ID,
    WORKBOOK_REVIEW_NODE_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
)

WorkbookBandFactory: TypeAlias = Callable[..., dict[str, object]]

WORKBOOK_BAND_SPECIALIST_IDS: Final[dict[str, str]] = {
    WORKBOOK_BRIEF_NODE_ID: WORKBOOK_BRIEF_SPECIALIST_ID,
    ASK_A_ENRICHMENT_NODE_ID: ASK_A_ENRICHMENT_SPECIALIST_ID,
    WORKBOOK_REVIEW_NODE_ID: WORKBOOK_REVIEW_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID: ASK_B_HOT_TOPICS_SPECIALIST_ID,
}


def _brief_factory(
    _node_id: str,
    _envelope: ProductionEnvelope,
    *,
    runtime_context: WorkbookBriefRuntimeContext,
) -> dict[str, object]:
    """Author and atomically persist the real 07W.1 handoff."""
    source = None
    scene_calls = 0
    promise_calls = 0

    def measured_scene_writer(request):
        nonlocal scene_calls
        scene_calls += 1
        return (runtime_context.scene_writer or offline_scene_composer)(request)

    def measured_promise_writer(request):
        nonlocal promise_calls
        promise_calls += 1
        return (runtime_context.promise_writer or offline_promise_transformer)(request)

    scene_introduced_terms: tuple[str, ...] = ()
    if runtime_context.course_source_root is None:
        scene = SceneBrief(
            status="unavailable",
            text=None,
            source_refs=(),
            known_losses=("scene_course_source_root_absent",),
            marker="scene_source_request_required",
        )
        selected_id = selected_ref = lesson_type = archetype = None
        scene_warnings: tuple[str, ...] = ("encounter_mode_defaulted_recorded",)
        scene_classification = LessonTypeClassification(
            status="insufficient",
            lesson_type=None,
            archetype=None,
            confidence=None,
            evidence_refs=("legacy:missing-course-root",),
        )
        scene_gate = SceneGateReceipt(failures=scene.known_losses)
        scene_extraction_losses: tuple[str, ...] = ()
    else:
        try:
            source = load_part2_scene_source(runtime_context.course_source_root)
        except (FileNotFoundError, ValueError, OSError) as exc:
            scene = SceneBrief(
                status="unavailable",
                text=None,
                source_refs=(),
                known_losses=("scene_source_substrate_unavailable",),
                marker="scene_source_request_required",
            )
            selected_id = selected_ref = lesson_type = archetype = None
            scene_warnings = (f"scene_source_detail:{type(exc).__name__}",)
            scene_classification = LessonTypeClassification(
                status="insufficient",
                lesson_type=None,
                archetype=None,
                confidence=None,
                evidence_refs=("source:unavailable",),
            )
            scene_gate = SceneGateReceipt(failures=scene.known_losses)
            scene_extraction_losses = scene.known_losses
        else:
            ref = str(source.raw_candidates[0]["source_ref"])
            scene_result = compose_scene_projection(
                SceneProjectionRequest.from_raw_candidates(
                    raw_candidates=source.raw_candidates,
                    candidate_ids=("part2-q5",),
                    lesson_type_evidence=LessonTypeEvidence(
                        fresh_pain=True,
                        bridge_identity=False,
                        skill_build=False,
                        evidence_refs=(ref,),
                    ),
                    payoff_slide_inventory=source.payoff_slide_inventory,
                    payoff_slide_keys=source.payoff_slide_keys,
                    requested_coverage="full_deck",
                    required_capabilities=("scene",),
                    available_coverage="full_deck",
                    available_capabilities=("scene",),
                ),
                measured_scene_writer,
            )
            scene = scene_result.scene
            selected_id, selected_ref = (
                scene_result.selected_seed_id,
                scene_result.selected_seed_ref,
            )
            lesson_type = scene_result.classification.lesson_type
            archetype = scene_result.classification.archetype
            scene_warnings = scene_result.operator_warnings
            scene_classification = scene_result.classification
            scene_gate = scene_result.gate_receipt
            scene_extraction_losses = scene_result.extraction_losses
            scene_introduced_terms = scene_result.introduced_terms

    resolution = resolve_promise_objectives(runtime_context.run_dir)
    forbidden = ()
    if source is not None:
        forbidden = source.forbidden_resolution_spans
    promise_result = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=resolution,
            scene_context=scene.text,
            friction_context=FRICTION_SCALE.rating_prompt,
            forbidden_resolution_spans=forbidden,
        ),
        measured_promise_writer,
    )
    promise: PromiseProjection = promise_result.projection
    losses = scene.known_losses + promise.known_losses
    brief = PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=losses),
    )
    payload = WorkbookBriefPayloadV1(
        pre_work=brief,
        selected_seed_id=selected_id,
        selected_seed_ref=selected_ref,
        lesson_type=lesson_type,
        archetype=archetype,
        promise_authority_refs=promise_result.authority_refs,
        encounter_mode=runtime_context.encounter_mode,
        writer_execution_mode=runtime_context.writer_execution_mode,
        scene_receipt=SceneAuthoringReceipt(
            classification=scene_classification,
            gate=scene_gate,
            extraction_losses=scene_extraction_losses,
            operator_warnings=scene_warnings,
            introduced_terms=scene_introduced_terms,
        ),
        promise_receipt=PromiseAuthoringReceipt(
            gate=promise_result.gate_receipt,
            authority_refs=promise_result.authority_refs,
            operator_warnings=promise_result.operator_warnings,
        ),
        writer_receipts=(
            _writer_receipt("scene", runtime_context, scene_calls),
            _writer_receipt("promise", runtime_context, promise_calls),
        ),
        warnings=tuple(dict.fromkeys((*scene_warnings, *promise_result.operator_warnings))),
        known_losses=losses,
    )
    artifact = WorkbookBriefArtifactV1(
        payload=payload, payload_digest=canonical_payload_digest(payload)
    )
    path = write_workbook_brief(runtime_context.run_dir, artifact)
    assert path.relative_to(runtime_context.run_dir).as_posix() == "workbook-brief.v1.json"
    return workbook_brief_contribution_receipt(artifact)


def _writer_receipt(
    writer: Literal["scene", "promise"],
    context: WorkbookBriefRuntimeContext,
    calls: int,
) -> WriterExecutionReceipt:
    instance = context.scene_writer if writer == "scene" else context.promise_writer
    config = getattr(instance, "model_config", None)
    return WriterExecutionReceipt(
        writer=writer,
        mode=context.writer_execution_mode,
        calls=1 if calls else 0,
        model=getattr(config, "default_model", None),
        model_config_digest=getattr(instance, "model_config_digest", None),
        request_id=getattr(instance, "last_request_id", None),
        latency_ms=getattr(instance, "last_latency_ms", None),
        input_tokens=getattr(instance, "last_input_tokens", None),
        output_tokens=getattr(instance, "last_output_tokens", None),
        cost_usd=getattr(instance, "last_cost_usd", None),
        cost_unavailable_reason=getattr(instance, "last_cost_unavailable_reason", None),
    )


def workbook_brief_contribution_receipt(
    artifact: WorkbookBriefArtifactV1,
) -> dict[str, object]:
    payload = artifact.payload
    return {
        "artifact_path": "workbook-brief.v1.json",
        "payload_digest": artifact.payload_digest,
        "schema_version": payload.schema_version,
        "status_summary": {
            "scene": payload.pre_work.scene.status,
            "promise": payload.pre_work.promise.status,
        },
        "warning_summary": list(payload.warnings),
        "loss_summary": list(payload.known_losses),
        "node_id": payload.node_id,
        "specialist_id": payload.specialist_id,
    }


def _ask_a_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_a_not_yet_wired"],
    }


def _review_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }


def _ask_b_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_b_not_yet_wired"],
    }


DEFAULT_WORKBOOK_BAND_FACTORIES: Final[dict[str, WorkbookBandFactory]] = {
    WORKBOOK_BRIEF_NODE_ID: _brief_factory,
    ASK_A_ENRICHMENT_NODE_ID: _ask_a_stub,
    WORKBOOK_REVIEW_NODE_ID: _review_stub,
    ASK_B_HOT_TOPICS_NODE_ID: _ask_b_stub,
}


def runtime_context_for_run(
    run_dir: Path, *, node_id: str | None = None
) -> WorkbookBriefRuntimeContext:
    """Reconstruct persisted context, or identify an honest pre-36.4 run."""
    context_path = Path(run_dir) / "workbook-runtime-context.v1.json"
    if context_path.is_file():
        try:
            context = read_runtime_context(run_dir)
        except ValueError as exc:
            raise SpecialistDispatchError(str(exc), tag="workbook-brief.context-corrupt") from exc
        if context.writer_execution_mode == "live" and node_id == WORKBOOK_BRIEF_NODE_ID:
            from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: PLC0415
                LivePromiseTransformer,
                LiveSceneComposer,
            )

            try:
                return context.model_copy(
                    update={
                        "scene_writer": LiveSceneComposer(),
                        "promise_writer": LivePromiseTransformer(),
                    }
                )
            except Exception as exc:
                raise SpecialistDispatchError(
                    f"workbook writer initialization failed: {exc}",
                    tag="workbook-brief.writer-init-failed",
                ) from exc
        return context
    return WorkbookBriefRuntimeContext(
        run_dir=Path(run_dir),
        course_source_root=None,
        encounter_mode="recorded",
        context_origin="legacy_default",
        writer_execution_mode="offline_stub",
    )


def run_workbook_band_node(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    factories: Mapping[str, WorkbookBandFactory] | None = None,
    runtime_context: WorkbookBriefRuntimeContext | None = None,
) -> ProductionEnvelope:
    """Run one node, skipping an exact persisted coordinate before its factory."""
    if not isinstance(production_envelope, ProductionEnvelope):
        raise SpecialistDispatchError(
            "workbook band requires a ProductionEnvelope context",
            tag="workbook.band.invalid-context",
        )
    specialist_id = WORKBOOK_BAND_SPECIALIST_IDS.get(node_id)
    if specialist_id is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    existing = production_envelope.get_contribution(specialist_id, node_id=node_id)
    if existing is not None:
        if node_id == WORKBOOK_BRIEF_NODE_ID:
            if runtime_context is None:
                raise SpecialistDispatchError(
                    "07W.1 resume requires runtime context", tag="workbook-brief.context-missing"
                )
            try:
                artifact = read_workbook_brief(runtime_context.run_dir)
            except ValueError as exc:
                raise SpecialistDispatchError(
                    str(exc), tag="workbook-brief.sidecar-invalid"
                ) from exc
            if existing.output != workbook_brief_contribution_receipt(artifact):
                raise SpecialistDispatchError(
                    "07W.1 contribution/sidecar mismatch", tag="workbook-brief.sidecar-mismatch"
                )
        return production_envelope

    selected = DEFAULT_WORKBOOK_BAND_FACTORIES if factories is None else factories
    factory = selected.get(node_id)
    if factory is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    try:
        if node_id == WORKBOOK_BRIEF_NODE_ID:
            requires_context = factory is DEFAULT_WORKBOOK_BAND_FACTORIES[node_id]
            if runtime_context is None and requires_context:
                raise SpecialistDispatchError(
                    "07W.1 requires explicit runtime context", tag="workbook-brief.context-missing"
                )
            if (
                runtime_context is not None
                and "runtime_context" in inspect.signature(factory).parameters
            ):
                output = factory(node_id, production_envelope, runtime_context=runtime_context)
            else:  # compatibility for injected pre-36.4 test/deterministic factories
                output = factory(node_id, production_envelope)
        else:
            output = factory(node_id, production_envelope)
    except SpecialistDispatchError:
        raise
    except Exception as exc:
        raise SpecialistDispatchError(
            f"workbook band factory failed at node {node_id!r}: {exc}",
            tag="workbook.band.factory-failed",
        ) from exc
    if not isinstance(output, dict):
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned "
            f"{type(output).__name__}, expected dict",
            tag="workbook.band.invalid-output",
        )
    try:
        json.dumps(output, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned non-serializable output: {exc}",
            tag="workbook.band.invalid-output",
        ) from exc
    updated = production_envelope.model_copy(deep=True)
    model_used = WORKBOOK_BAND_MODEL_MARKER
    if node_id == WORKBOOK_BRIEF_NODE_ID and runtime_context is not None:
        if runtime_context.writer_execution_mode == "live":
            config = getattr(runtime_context.scene_writer, "model_config", None)
            model_used = getattr(config, "default_model", None) or "workbook-writer-live"
        else:
            model_used = "workbook-brief-offline"
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=output,
            model_used=model_used,
        )
    )
    return updated


__all__ = [
    "DEFAULT_WORKBOOK_BAND_FACTORIES",
    "WORKBOOK_BAND_MODEL_MARKER",
    "WORKBOOK_BAND_NODE_IDS",
    "WORKBOOK_BAND_SPECIALIST_IDS",
    "WORKBOOK_BRIEF_NODE_ID",
    "WORKBOOK_BRIEF_SPECIALIST_ID",
    "LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID",
    "WORKBOOK_REVIEW_NODE_ID",
    "WORKBOOK_REVIEW_SPECIALIST_ID",
    "WorkbookBandFactory",
    "run_workbook_band_node",
    "runtime_context_for_run",
    "workbook_brief_contribution_receipt",
]
