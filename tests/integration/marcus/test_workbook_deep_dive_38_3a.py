from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.deep_dive_projection import (
    DEEP_DIVE_UNAVAILABLE_MARKER,
    BoldTermMarker,
    DeepDiveAbilityInput,
    DeepDiveAbilitySection,
    DeepDiveSkeletonClaim,
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonWriterResult,
    NarrationSourceSpan,
    SourceClaim,
    compose_deep_dive_skeleton,
)
from app.marcus.lesson_plan.prework_artifact import (
    DeepDiveExecutionReceiptV1,
    WorkbookBriefArtifactV1,
    WorkbookBriefPayloadV1,
    WorkbookBriefRuntimeContext,
    canonical_payload_digest,
    read_workbook_brief,
    write_runtime_context,
    write_workbook_brief,
)
from app.marcus.lesson_plan.prework_projection import (
    ObjectiveInput,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.promise_projection import (
    PromiseObjectiveResolution,
    PromiseObjectiveResolutionError,
)
from app.marcus.lesson_plan.research_demand import (
    AskAResearchDemandV1,
    ResearchDemandShapeError,
    resolve_enrichment_demand,
)
from app.marcus.lesson_plan.workbook_enrichment import RunEnvelopeCorruptError
from app.marcus.orchestrator import workbook_prework_writers, workbook_wiring
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.state.component_selection import ComponentSelection
from app.models.state.run_state import RunState
from app.pass1_generation_lock import pass1_generation_lock
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.workbook_producer._act import (
    WorkbookProducerActError,
    _reconcile_workbook_brief_authority,
)
from tests.helpers.workbook_slide_authority import (
    install_manifest_slide_authority,
    install_single_slide_authority,
)

ROOT = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()
LEGACY_RUN = Path(
    "_bmad-output/implementation-artifacts/evidence/"
    "prework-36-4-fresh-input-380ecd47/run"
)


class SceneWriter:
    last_cost_unavailable_reason = "test-writer-no-cost"

    def __call__(self, request):
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
    last_cost_unavailable_reason = "test-writer-no-cost"

    def __call__(self, request):
        return PromiseProjection(
            status="authored",
            vows=(PromiseVow(objective_id="LO-1", text="I can choose a first move."),),
            known_losses=(),
            marker=None,
        )


class DeepWriter:
    model_config_digest = "sha256:" + "2" * 64

    def __init__(self) -> None:
        self.calls_made = 0
        self.last_request_id = "req-38-3a"
        self.last_latency_ms = 2.0
        self.last_input_tokens = 10
        self.last_output_tokens = 5
        self.last_cost_usd = 0.001
        self.last_cost_unavailable_reason = None
        self.model_config = type("Config", (), {"default_model": "test-model"})()

    def __call__(self, request):
        self.calls_made += 1
        return DeepDiveSkeletonWriterResult(
            status="unavailable",
            sections=(),
            bold_terms=(),
            known_losses=("deep_dive_writer_unavailable",),
            marker=DEEP_DIVE_UNAVAILABLE_MARKER,
        )


def _authored_candidate(request) -> DeepDiveSkeletonWriterResult:
    marked = False
    claims = []
    terms = []
    for index, source in enumerate(request.source_claims):
        text = source.text.replace("**", "")
        if not marked and "structural" in text:
            text = text.replace("structural", "**structural**", 1)
            terms.append(BoldTermMarker(term="structural"))
            marked = True
        claims.append(
            DeepDiveSkeletonClaim(
                skeleton_claim_id=f"skeleton-{index + 1}",
                text=text,
                source_claim_refs=(source.claim_id,),
                source_span_refs=source.source_span_refs,
            )
        )
    return DeepDiveSkeletonWriterResult(
        status="authored",
        sections=(
            DeepDiveAbilitySection(
                ability_id=request.abilities[0].ability_id,
                prose=" ".join(claim.text for claim in claims),
                claims=tuple(claims),
            ),
        ),
        bold_terms=tuple(terms),
        known_losses=(),
        marker=None,
    )


class AuthoredDeepWriter(DeepWriter):
    def __call__(self, request):
        self.calls_made += 1
        return _authored_candidate(request)


def test_carrier_failure_precedes_every_workbook_writer_and_side_effect(
    tmp_path: Path, monkeypatch
) -> None:
    class CountingScene(SceneWriter):
        calls = 0

        def __call__(self, request):
            self.calls += 1
            return super().__call__(request)

    class CountingPromise(PromiseWriter):
        calls = 0

        def __call__(self, request):
            self.calls += 1
            return super().__call__(request)

    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={"lesson_plan": {"plan_units": []}},
            model_used="fixture",
        )
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output={"slides": []},
            model_used="fixture",
        )
    )
    scene = CountingScene()
    promise = CountingPromise()
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=scene,
        promise_writer=promise,
        deep_dive_writer=deep,
    )

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=envelope, runtime_context=context
        )

    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert (scene.calls, promise.calls, deep.calls_made) == (0, 0, 0)
    assert not (tmp_path / "workbook-brief.v1.json").exists()
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()
    assert envelope.get_contribution("workbook_brief", node_id="07W.1") is None


@pytest.mark.parametrize("mutation", ["carrier", "manifest", "plan-sidecar"])
def test_authority_is_revalidated_after_prework_before_deep_dive_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)

    class MutatingScene(SceneWriter):
        def __call__(self, request):
            result = super().__call__(request)
            if mutation == "carrier":
                (tmp_path / "workbook-slide-authority-map.v1.json").unlink()
            elif mutation == "manifest":
                manifest = tmp_path / "exports" / "segment-manifest-storyboard-b.yaml"
                manifest.write_text(
                    manifest.read_text(encoding="utf-8") + "# changed after Scene\n",
                    encoding="utf-8",
                )
            else:
                sidecar = tmp_path / "irene-pass1.lesson-plan.json"
                sidecar.write_text(
                    sidecar.read_text(encoding="utf-8") + " ", encoding="utf-8"
                )
            return result

    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=MutatingScene(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=deep,
    )

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=initial,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert deep.calls_made == 0
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def test_dispatch_lock_blocks_deep_dive_spend_and_is_held_during_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    lock_path = tmp_path / ".workbook-slide-authority-map.v1.json.dispatch.lock"

    blocked = DeepWriter()
    blocked_context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=blocked,
    )
    with (
        workbook_wiring._slide_authority_dispatch_lock(tmp_path),
        pytest.raises(SpecialistDispatchError) as caught,
    ):
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=initial,
            runtime_context=blocked_context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-persistence-failed"
    assert blocked.calls_made == 0

    class LockAwareWriter(DeepWriter):
        def __call__(self, request):
            assert lock_path.is_file()
            return super().__call__(request)

    aware = LockAwareWriter()
    context = blocked_context.model_copy(update={"deep_dive_writer": aware})
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=initial,
        runtime_context=context,
    )
    assert aware.calls_made == 1
    assert lock_path.is_file()


def test_journal_directory_flush_failure_blocks_provider_spend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    writer = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=writer,
    )

    def _fail_flush(_path: Path) -> None:
        raise OSError("directory flush denied")

    monkeypatch.setattr(workbook_wiring, "_fsync_directory", _fail_flush)
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=initial,
            runtime_context=context,
        )

    assert caught.value.tag == "workbook-brief.deep-dive-persistence-failed"
    assert writer.calls_made == 0


def test_pass1_generation_lock_blocks_authority_revalidation_and_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    class _CountingScene(SceneWriter):
        def __init__(self) -> None:
            self.calls_made = 0

        def __call__(self, request):
            self.calls_made += 1
            return super().__call__(request)

    class _CountingPromise(PromiseWriter):
        def __init__(self) -> None:
            self.calls_made = 0

        def __call__(self, request):
            self.calls_made += 1
            return super().__call__(request)

    scene = _CountingScene()
    promise = _CountingPromise()
    writer = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=scene,
        promise_writer=promise,
        deep_dive_writer=writer,
    )

    with pass1_generation_lock(tmp_path), pytest.raises(
        SpecialistDispatchError
    ) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=initial,
            runtime_context=context,
        )

    assert caught.value.tag == "workbook-brief.deep-dive-persistence-failed"
    assert scene.calls_made == 0
    assert promise.calls_made == 0
    assert writer.calls_made == 0


def test_completed_journal_temporary_recovers_over_in_progress_target(
    tmp_path: Path,
) -> None:
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    temporary = journal_path.with_suffix(journal_path.suffix + ".tmp")
    identity = {
        "schema_version": "workbook-deep-dive-call.v1",
        "idempotency_key": "sha256:" + "1" * 64,
        "authority_digest": "sha256:" + "2" * 64,
        "model_config_digest": "sha256:" + "3" * 64,
        "slide_authority_map_digest": "sha256:" + "4" * 64,
    }
    journal_path.write_text(
        json.dumps({**identity, "state": "call_in_progress"}), encoding="utf-8"
    )
    completed = {**identity, "state": "completed", "candidate": {}}
    temporary.write_text(json.dumps(completed), encoding="utf-8")

    workbook_wiring._recover_journal_temporary(tmp_path, journal_path)

    assert json.loads(journal_path.read_text(encoding="utf-8")) == completed
    assert not temporary.exists()


def test_dispatch_lock_cleanup_failure_uses_stable_persistence_taxonomy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_close = workbook_wiring.os.close

    def close_then_fail(descriptor: int) -> None:
        real_close(descriptor)
        raise OSError("simulated close failure")

    with monkeypatch.context() as scoped:
        scoped.setattr(workbook_wiring.os, "close", close_then_fail)
        with pytest.raises(
            workbook_wiring.SlideAuthorityPersistenceError,
            match="cleanup failed",
        ), workbook_wiring._slide_authority_dispatch_lock(tmp_path):
                pass


def test_dispatch_lock_rejects_hard_link_without_mutating_external_file(
    tmp_path: Path,
) -> None:
    external = tmp_path / "external.txt"
    external.write_bytes(b"")
    lock_path = tmp_path / ".workbook-slide-authority-map.v1.json.dispatch.lock"
    try:
        workbook_wiring.os.link(external, lock_path)
    except OSError as exc:
        pytest.skip(f"host cannot create hard links: {exc}")

    with pytest.raises(
        workbook_wiring.SlideAuthorityPersistenceError,
        match="unavailable",
    ), workbook_wiring._slide_authority_dispatch_lock(tmp_path):
        pass
    assert external.read_bytes() == b""


def test_new_factory_without_run_json_never_gets_mapless_compatibility(
    tmp_path: Path,
) -> None:
    scene = SceneWriter()
    promise = PromiseWriter()
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=scene,
        promise_writer=promise,
        deep_dive_writer=deep,
    )

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=uuid4()),
            runtime_context=context,
        )

    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert deep.calls_made == 0
    assert not (tmp_path / "workbook-brief.v1.json").exists()
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def test_slide_authority_digest_binds_journal_receipt_and_zero_call_replay(
    tmp_path: Path,
) -> None:
    map_digest = "sha256:" + "9" * 64
    request = DeepDiveSkeletonRequest(
        lesson_ref="exports/segment-manifest-storyboard-b.yaml",
        source_spans=(
            NarrationSourceSpan(
                span_id="vo:seg-01",
                text="Systems have visible workflow symptoms.",
                source_ref="exports/segment-manifest-storyboard-b.yaml#segments/seg-01/narration_text",
            ),
        ),
        source_claims=(
            SourceClaim(
                claim_id="claim:vo:seg-01",
                text="Systems have visible workflow symptoms.",
                source_span_refs=("vo:seg-01",),
                role="vo",
            ),
        ),
        abilities=(
            DeepDiveAbilityInput(ability_id="LO-1", text="I can choose a first move."),
        ),
        slide_authority_map_digest=map_digest,
    )
    writer = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        deep_dive_writer=writer,
    )
    trial_id = uuid4()

    first, receipt = workbook_wiring._compose_deep_dive(
        request=request, context=context, trial_id=trial_id
    )
    replayed, replay_receipt = workbook_wiring._compose_deep_dive(
        request=request, context=context, trial_id=trial_id
    )

    assert replayed == first
    assert writer.calls_made == 1
    assert receipt.slide_authority_map_digest == map_digest
    assert replay_receipt.slide_authority_map_digest == map_digest
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert journal["slide_authority_map_digest"] == map_digest
    assert journal["provider_receipt"]["slide_authority_map_digest"] == map_digest

    journal["slide_authority_map_digest"] = "sha256:" + "8" * 64
    journal_path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring._compose_deep_dive(
            request=request, context=context, trial_id=trial_id
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


@pytest.mark.parametrize(
    "error_type", [PromiseObjectiveResolutionError, RunEnvelopeCorruptError]
)
def test_promise_authority_corruption_uses_deep_dive_authority_tag(
    tmp_path: Path, monkeypatch, error_type: type[ValueError]
) -> None:
    _authority(tmp_path)

    def corrupt_authority(_run_dir: Path) -> PromiseObjectiveResolution:
        raise error_type("persisted Promise authority is corrupt")

    monkeypatch.setattr(
        workbook_wiring, "resolve_promise_objectives", corrupt_authority
    )
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=DeepWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=uuid4()),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert not (tmp_path / "workbook-brief.v1.json").exists()
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def test_malformed_run_lineage_uses_deep_dive_authority_tag(tmp_path: Path) -> None:
    _authority(tmp_path)
    (tmp_path / "run.json").write_text("{malformed", encoding="utf-8")
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=DeepWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=uuid4()),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert not (tmp_path / "workbook-brief.v1.json").exists()
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def _authority(run_dir: Path) -> None:
    exports = run_dir / "exports"
    exports.mkdir()
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        "segments:\n"
        "  - segment_id: seg-01\n"
        "    slide_id: slide-01\n"
        "    narration_text: Systems have visible workflow symptoms.\n",
        encoding="utf-8",
    )


def _persist_envelope(
    run_dir: Path, trial: ProductionTrialEnvelope, envelope: ProductionEnvelope
) -> None:
    (run_dir / "run.json").write_text(
        trial.model_copy(update={"production_envelope": envelope}).model_dump_json(indent=2),
        encoding="utf-8",
    )


def _load_current_legacy_trial(run_dir: Path) -> ProductionTrialEnvelope:
    trial = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text("utf-8")
    )
    return trial.model_copy(
        update={
            "production_envelope": install_manifest_slide_authority(
                trial.production_envelope,
                run_dir=run_dir,
                course_source_root=ROOT,
            )
        }
    )


def test_07w1_live_deep_dive_journals_once_and_resumes_without_recall(
    tmp_path: Path, monkeypatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="LO-1", text="Choose a move.", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=deep,
    )
    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=initial,
        runtime_context=context,
    )
    artifact = read_workbook_brief(tmp_path)
    assert artifact.payload.deep_dive_skeleton is not None
    assert artifact.payload.deep_dive_writer_receipt is not None
    assert artifact.payload.deep_dive_writer_receipt.calls == 1
    journal = json.loads((tmp_path / "workbook-deep-dive-call.v1.json").read_text("utf-8"))
    assert journal["state"] == "completed"
    assert journal["provider_contract_mode"] == "raw-json-schema"
    assert journal["provider_normalizer_version"] == "deep-dive-provider-normalizer.v1"
    assert journal["raw_provider_payload_digest"].startswith("sha256:")
    assert journal["normalized_provider_payload_digest"].startswith("sha256:")
    assert (
        journal["candidate_digest"]
        == artifact.payload.deep_dive_skeleton.candidate_payload_digest
    )
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=envelope, runtime_context=context
    )
    assert repeated is envelope
    assert deep.calls_made == 1
    rolled_forward = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=initial, runtime_context=context
    )
    assert deep.calls_made == 1
    assert rolled_forward.get_contribution("workbook_brief", node_id="07W.1") is not None

    journal["raw_provider_payload"]["status"] = "authored"
    (tmp_path / "workbook-deep-dive-call.v1.json").write_text(
        json.dumps(journal), encoding="utf-8"
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=envelope, runtime_context=context
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=initial, runtime_context=context
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


@pytest.mark.parametrize("reentry", ["activated", "rollforward"])
def test_mapped_reentry_requires_existing_carrier_and_never_regenerates_it(
    tmp_path: Path, reentry: str
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=deep,
    )
    activated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    carrier = tmp_path / "workbook-slide-authority-map.v1.json"
    carrier.unlink()
    supplied = activated if reentry == "activated" else trial.production_envelope

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=supplied,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"
    assert deep.calls_made == 1
    assert not carrier.exists()


def test_offline_valid_authority_projects_typed_unavailable_demand(
    tmp_path: Path, monkeypatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(
            ObjectiveInput(objective_id="LO-1", text="Choose a move.", status="ratified"),
        ),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
    )
    initial = install_single_slide_authority(
        ProductionEnvelope(trial_id=uuid4()),
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=initial,
        runtime_context=context,
    )
    trial = ProductionTrialEnvelope(
        trial_id=envelope.trial_id,
        preset="production",
        corpus_path="fixture",
        operator_id="test",
        started_at=datetime.now(UTC),
        status="in-flight",
        production_clone_launch_evidence=False,
        production_envelope=envelope,
    )
    (tmp_path / "run.json").write_text(trial.model_dump_json(indent=2), encoding="utf-8")
    artifact = read_workbook_brief(tmp_path)
    assert artifact.payload.deep_dive_writer_receipt.model_config_digest == (
        "sha256:" + "0" * 64
    )
    demand = resolve_enrichment_demand(tmp_path)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("deep_dive_skeleton_unavailable",)

    mapped_request = artifact.payload.deep_dive_skeleton.authority.model_copy(
        update={"slide_authority_map_digest": "sha256:" + "7" * 64}
    )
    mapped_skeleton = compose_deep_dive_skeleton(
        mapped_request,
        lambda _: DeepDiveSkeletonWriterResult(
            status="unavailable",
            sections=(),
            bold_terms=(),
            known_losses=("deep_dive_writer_unavailable",),
            marker=DEEP_DIVE_UNAVAILABLE_MARKER,
        ),
    )
    contradictory_receipt = artifact.payload.deep_dive_writer_receipt.model_copy(
        update={"slide_authority_map_digest": "sha256:" + "8" * 64}
    )
    with pytest.raises(ValueError, match="receipt map digest"):
        WorkbookBriefPayloadV1.model_validate(
            artifact.payload.model_copy(
                update={
                    "deep_dive_skeleton": mapped_skeleton,
                    "deep_dive_writer_receipt": contradictory_receipt,
                }
            ).model_dump()
        )


def test_targeted_matching_legacy_null_upgrade_preserves_prework_without_scene_promise_recall(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    before = read_workbook_brief(tmp_path)
    current = install_manifest_slide_authority(
        trial.production_envelope,
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        deep_dive_writer=deep,
    )
    upgraded = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=current,
        runtime_context=context,
    )
    after = read_workbook_brief(tmp_path)
    assert after.payload.pre_work == before.payload.pre_work
    assert after.payload.writer_receipts == before.payload.writer_receipts
    assert after.payload.deep_dive_skeleton is not None
    assert after.payload.deep_dive_skeleton.authority.slide_authority_map_digest
    assert after.payload.deep_dive_writer_receipt.calls == 1
    assert after.payload.deep_dive_writer_receipt.prior_payload_digest == before.payload_digest
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=upgraded, runtime_context=context
    )
    assert repeated is upgraded
    assert deep.calls_made == 1


def test_legacy_null_sidecar_without_contribution_cannot_self_authorize_upgrade(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    sidecar = tmp_path / "workbook-brief.v1.json"
    before = sidecar.read_bytes()
    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        deep_dive_writer=deep,
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=trial.trial_id),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-split-brain"
    assert sidecar.read_bytes() == before
    assert deep.calls_made == 0
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def test_legacy_null_upgrade_missing_authority_preserves_original_bytes(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    sidecar = tmp_path / "workbook-brief.v1.json"
    before = sidecar.read_bytes()
    (tmp_path / "exports/segment-manifest-storyboard-b.yaml").unlink()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-authority-invalid"
    assert sidecar.read_bytes() == before
    assert not (tmp_path / "workbook-deep-dive-call.v1.json").exists()


def test_serialized_envelope_and_sidecar_project_one_ready_demand(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    deep = AuthoredDeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=deep,
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    artifact = read_workbook_brief(tmp_path)
    request = artifact.payload.deep_dive_skeleton.authority
    mismatched_receipt = artifact.payload.deep_dive_writer_receipt.model_copy(
        update={"mode": "offline_stub", "calls": 0}
    )
    with pytest.raises(ValueError, match="receipt mode"):
        WorkbookBriefPayloadV1.model_validate(
            artifact.payload.model_copy(
                update={"deep_dive_writer_receipt": mismatched_receipt}
            ).model_dump()
        )
    _persist_envelope(tmp_path, trial, envelope)
    demand = resolve_enrichment_demand(tmp_path)
    assert demand.status == "ready"
    assert demand.abilities == request.abilities
    assert demand.bold_terms == (BoldTermMarker(term="structural"),)
    assert demand.source_claim_refs == tuple(claim.claim_id for claim in request.source_claims)
    forged_demand = demand.model_dump(mode="json")
    forged_demand["abilities"] *= 2
    forged_demand["bold_terms"] *= 2
    forged_demand["source_claim_refs"] *= 2
    unsigned = {
        key: value for key, value in forged_demand.items() if key != "demand_digest"
    }
    forged_demand["demand_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    with pytest.raises(ValueError, match="unique ability IDs"):
        AskAResearchDemandV1.model_validate_json(
            json.dumps(forged_demand), strict=True
        )
    state = RunState(
        graph_version="v42",
        status="running",
        production_envelope=envelope,
        component_selection=ComponentSelection(deck=True, workbook=True),
    )
    assert _reconcile_workbook_brief_authority(state, tmp_path) == artifact
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    journal = json.loads(journal_path.read_text("utf-8"))
    journal["raw_provider_payload"]["marker"] = "forged"
    journal_path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(ResearchDemandShapeError, match="raw provider payload digest"):
        resolve_enrichment_demand(tmp_path)


def test_ready_demand_rejects_cross_trial_and_sidecar_receipt_substitution(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=AuthoredDeepWriter(),
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    _persist_envelope(tmp_path, trial, envelope)
    assert resolve_enrichment_demand(tmp_path).status == "ready"

    foreign = envelope.model_copy(update={"trial_id": uuid4()})
    _persist_envelope(tmp_path, trial, foreign)
    with pytest.raises(ResearchDemandShapeError, match="trial"):
        resolve_enrichment_demand(tmp_path)

    _persist_envelope(tmp_path, trial, envelope)
    artifact = read_workbook_brief(tmp_path)
    forged_receipt = artifact.payload.deep_dive_writer_receipt.model_copy(
        update={"request_id": "forged-request"}
    )
    forged_payload = WorkbookBriefPayloadV1.model_validate(
        artifact.payload.model_copy(
            update={"deep_dive_writer_receipt": forged_receipt}
        ).model_dump()
    )
    forged = WorkbookBriefArtifactV1(
        payload=forged_payload,
        payload_digest=canonical_payload_digest(forged_payload),
    )
    write_workbook_brief(tmp_path, forged)
    forged_envelope = envelope.model_copy(deep=True)
    forged_envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.1",
            output=workbook_wiring.workbook_brief_contribution_receipt(forged),
            model_used="forged",
        )
    )
    _persist_envelope(tmp_path, trial, forged_envelope)
    with pytest.raises(ResearchDemandShapeError, match="receipt"):
        resolve_enrichment_demand(tmp_path)


@pytest.mark.parametrize(
    ("specialist_id", "node_id"),
    [("wrong_specialist", "07W.1"), ("workbook_brief", "07W.9")],
)
def test_demand_reader_rejects_coordinate_collisions(
    tmp_path: Path, specialist_id: str, node_id: str
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    envelope = trial.production_envelope.model_copy(deep=True)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output={"planted": True},
            model_used="planted",
        )
    )
    _persist_envelope(tmp_path, trial, envelope)
    with pytest.raises(ResearchDemandShapeError, match="coordinate collision"):
        resolve_enrichment_demand(tmp_path)


def test_demand_reader_rejects_duplicate_exact_contributions(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    contribution = trial.production_envelope.get_contribution(
        "workbook_brief", node_id="07W.1"
    )
    assert contribution is not None
    duplicate = trial.production_envelope.model_copy(
        update={
            "contributions": (
                *trial.production_envelope.contributions,
                contribution,
            )
        }
    )
    _persist_envelope(tmp_path, trial, duplicate)
    with pytest.raises(ResearchDemandShapeError, match="coordinate collision"):
        resolve_enrichment_demand(tmp_path)


def test_terminal_rejects_simultaneous_real_and_legacy_contributions(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    legacy = SpecialistContribution.from_output(
        specialist_id="workbook_brief_stub",
        node_id="07W.1",
        output={"stub_status": "legacy"},
        model_used="legacy",
    )
    contradictory = trial.production_envelope.model_copy(
        update={"contributions": (*trial.production_envelope.contributions, legacy)}
    )
    state = RunState(
        graph_version="v42",
        status="running",
        production_envelope=contradictory,
        component_selection=ComponentSelection(deck=True, workbook=True),
    )
    with pytest.raises(WorkbookProducerActError) as caught:
        _reconcile_workbook_brief_authority(state, tmp_path)
    assert caught.value.tag == "workbook-brief.sidecar-mismatch"


def test_legacy_stub_cannot_mask_real_sidecar(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    envelope = ProductionEnvelope(trial_id=trial.production_envelope.trial_id)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief_stub",
            node_id="07W.1",
            output={"stub_status": "legacy"},
            model_used="legacy",
        )
    )
    _persist_envelope(tmp_path, trial, envelope)
    with pytest.raises(ResearchDemandShapeError, match="contradicts"):
        resolve_enrichment_demand(tmp_path)


def test_broken_brief_symlink_fails_all_envelope_aware_consumers(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    brief = tmp_path / "workbook-brief.v1.json"
    brief.unlink()
    try:
        brief.symlink_to(tmp_path / "missing-workbook-brief.json")
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")

    with pytest.raises(ResearchDemandShapeError, match="symlink"):
        resolve_enrichment_demand(tmp_path)

    state = RunState(
        graph_version="v42",
        status="running",
        production_envelope=trial.production_envelope,
        component_selection=ComponentSelection(deck=True, workbook=True),
    )
    with pytest.raises(WorkbookProducerActError) as terminal:
        _reconcile_workbook_brief_authority(state, tmp_path)
    assert terminal.value.tag == "workbook-brief.sidecar-invalid"

    deep = DeepWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=deep,
    )
    with pytest.raises(SpecialistDispatchError) as wiring:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert wiring.value.tag == "workbook-brief.sidecar-invalid"
    assert deep.calls_made == 0


@pytest.mark.parametrize("collision", ["duplicate", "wrong-specialist", "wrong-node"])
def test_resume_and_terminal_reject_all_workbook_brief_coordinate_collisions(
    tmp_path: Path, collision: str
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = ProductionTrialEnvelope.model_validate_json(
        (tmp_path / "run.json").read_text("utf-8")
    )
    exact = trial.production_envelope.get_contribution("workbook_brief", node_id="07W.1")
    assert exact is not None
    if collision == "duplicate":
        planted = exact
    elif collision == "wrong-specialist":
        planted = SpecialistContribution.from_output(
            specialist_id="planted",
            node_id="07W.1",
            output={"planted": True},
            model_used="planted",
        )
    else:
        planted = SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.9",
            output={"planted": True},
            model_used="planted",
        )
    contradictory = trial.production_envelope.model_copy(
        update={"contributions": (*trial.production_envelope.contributions, planted)}
    )
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as wiring:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=contradictory,
            runtime_context=context,
        )
    assert wiring.value.tag == "workbook-brief.sidecar-mismatch"

    state = RunState(
        graph_version="v42",
        status="running",
        production_envelope=contradictory,
        component_selection=ComponentSelection(deck=True, workbook=True),
    )
    with pytest.raises(WorkbookProducerActError) as terminal:
        _reconcile_workbook_brief_authority(state, tmp_path)
    assert terminal.value.tag == "workbook-brief.sidecar-mismatch"


def test_offline_new_sidecar_old_contribution_requires_completed_live_journal(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    live_context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=live_context,
    )
    activated = read_workbook_brief(tmp_path)
    assert activated.payload.deep_dive_skeleton is not None
    assert activated.payload.deep_dive_writer_receipt.calls == 1
    (tmp_path / "workbook-deep-dive-call.v1.json").unlink()
    offline_context = live_context.model_copy(
        update={"writer_execution_mode": "offline_stub", "deep_dive_writer": None}
    )

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=offline_context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-split-brain"


def test_writer_supplied_provider_evidence_must_match_local_recomputation(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)

    class ForgedEvidenceWriter(DeepWriter):
        last_provider_normalizations = ("forged-normalization",)

    writer = ForgedEvidenceWriter()
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=writer,
    )
    before = (tmp_path / "workbook-brief.v1.json").read_bytes()
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-writer-output-invalid"
    assert (tmp_path / "workbook-brief.v1.json").read_bytes() == before
    journal = json.loads(
        (tmp_path / "workbook-deep-dive-call.v1.json").read_text("utf-8")
    )
    assert journal["state"] == "call_in_progress"


def test_successful_candidate_rejects_stale_normalization_error_state(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)

    class StaleErrorWriter(DeepWriter):
        last_provider_normalization_error = "TypeError: stale failure"

    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=StaleErrorWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-writer-output-invalid"


def test_runtime_context_symlink_is_never_authority(tmp_path: Path) -> None:
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="offline_stub",
    )
    context_path = write_runtime_context(context)
    external = tmp_path.parent / f"{tmp_path.name}-external-runtime-context.json"
    context_path.replace(external)
    try:
        context_path.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.runtime_context_for_run(tmp_path)
    assert caught.value.tag == "workbook-brief.context-corrupt"


def test_nonregular_runtime_context_is_never_legacy_absence(tmp_path: Path) -> None:
    (tmp_path / "workbook-runtime-context.v1.json").mkdir()
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.runtime_context_for_run(tmp_path)
    assert caught.value.tag == "workbook-brief.context-corrupt"


def test_metadata_minimal_injected_writer_gets_honest_receipt_and_stable_failures(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)

    class MinimalWriter:
        def __call__(self, request):
            return DeepWriter()(request)

    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=MinimalWriter(),
    )
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    receipt = read_workbook_brief(tmp_path).payload.deep_dive_writer_receipt
    assert receipt.cost_usd is None
    assert receipt.cost_unavailable_reason == "injected_writer_supplied_no_cost_evidence"

    shutil.rmtree(tmp_path)
    shutil.copytree(LEGACY_RUN, tmp_path)
    trial = _load_current_legacy_trial(tmp_path)

    class ContradictoryMetadataWriter(MinimalWriter):
        last_cost_usd = 0.01
        last_cost_unavailable_reason = "contradictory"

    invalid_context = context.model_copy(
        update={"deep_dive_writer": ContradictoryMetadataWriter()}
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=invalid_context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-writer-output-invalid"


def test_injected_writer_cannot_select_a_noncanonical_provider_schema(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)

    class WrongSchemaWriter(DeepWriter):
        provider_schema = {"type": "object"}
        provider_schema_digest = workbook_wiring._sha256(provider_schema)

    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=WrongSchemaWriter(),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-writer-output-invalid"


def test_completed_journal_replay_never_trusts_injected_schema_digest(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    upgraded = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    journal = json.loads(journal_path.read_text("utf-8"))
    forged_digest = "sha256:" + "f" * 64
    journal["provider_schema_digest"] = forged_digest
    journal_path.write_text(json.dumps(journal), encoding="utf-8")

    class ForgedSchemaDigestWriter(DeepWriter):
        provider_schema_digest = forged_digest

    forged_context = context.model_copy(
        update={"deep_dive_writer": ForgedSchemaDigestWriter()}
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=upgraded,
            runtime_context=forged_context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


def test_successful_07w1_reentry_replaces_lone_legacy_stub(
    tmp_path: Path, monkeypatch
) -> None:
    _authority(tmp_path)
    resolution = PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="LO-1", text="Choose.", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )
    monkeypatch.setattr(workbook_wiring, "resolve_promise_objectives", lambda _: resolution)
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief_stub",
            node_id="07W.1",
            output={"stub_status": "legacy"},
            model_used="legacy",
        )
    )
    envelope = install_single_slide_authority(
        envelope,
        run_dir=tmp_path,
        course_source_root=ROOT,
    )
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
        scene_writer=SceneWriter(),
        promise_writer=PromiseWriter(),
        deep_dive_writer=DeepWriter(),
    )
    updated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=envelope, runtime_context=context
    )
    assert updated.get_contribution("workbook_brief", node_id="07W.1") is not None
    assert updated.get_contribution("workbook_brief_stub", node_id="07W.1") is None


def test_split_brain_rollforward_without_course_authority_keeps_reconciliation_tag(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    live_context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=live_context,
    )
    missing_authority = live_context.model_copy(
        update={"course_source_root": None, "context_origin": "legacy_default"}
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=missing_authority,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


def test_journal_backed_rollforward_replaces_lone_legacy_stub(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    legacy_only = ProductionEnvelope(trial_id=trial.trial_id)
    legacy_only.add_contribution(
        trial.production_envelope.get_contribution("irene_pass1", node_id="05B")
    )
    legacy_only.add_contribution(
        trial.production_envelope.get_contribution("package_builder", node_id="06")
    )
    legacy_only.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief_stub",
            node_id="07W.1",
            output={"stub_status": "legacy"},
            model_used="legacy",
        )
    )
    rolled = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=legacy_only, runtime_context=context
    )
    assert rolled.get_contribution("workbook_brief", node_id="07W.1") is not None
    assert rolled.get_contribution("workbook_brief_stub", node_id="07W.1") is None


def test_normalization_failure_journals_available_raw_provider_evidence(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    raw = {
        "status": "authored",
        "sections": [],
        "bold_terms": ({"term": "workflow"}, {"term": "workflow"}),
        "known_losses": [],
        "marker": None,
    }

    class TupleChat:
        def with_structured_output(self, schema, *, include_raw=False):
            return SimpleNamespace(
                invoke=lambda messages: {
                    "parsed": raw,
                    "raw": SimpleNamespace(response_metadata={}),
                    "parsing_error": None,
                }
            )

    writer = workbook_prework_writers.LiveDeepDiveWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=TupleChat(), entry=None)
    )
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=writer,
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-writer-output-invalid"
    journal = json.loads(
        (tmp_path / "workbook-deep-dive-call.v1.json").read_text("utf-8")
    )
    assert journal["state"] == "call_in_progress"
    assert journal["raw_provider_payload"]["bold_terms"] == list(raw["bold_terms"])
    assert journal["raw_provider_payload_digest"].startswith("sha256:")
    assert journal["provider_schema_digest"].startswith("sha256:")
    assert journal["provider_normalizer_version"] == "deep-dive-provider-normalizer.v1"
    assert journal["provider_normalizations"] == []
    assert "JSON list" in journal["provider_normalization_error"]
    assert journal["provider_failure"]["type"] == "DeepDiveProviderOutputError"


def test_timeout_failure_is_one_call_fail_loud_and_never_publishes_brief(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)

    class TimeoutWriter(DeepWriter):
        def __call__(self, request):
            self.calls_made += 1
            raise TimeoutError("provider request timed out")

    def fake_factory(*args, **kwargs):
        return SimpleNamespace(chat=object(), entry=None)

    writer = TimeoutWriter()
    writer.model_config_digest = workbook_prework_writers.LiveDeepDiveWriter(
        chat_factory=fake_factory
    ).model_config_digest
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=writer,
    )
    before = (tmp_path / "workbook-brief.v1.json").read_bytes()

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )

    assert caught.value.tag == "workbook-brief.deep-dive-writer-execution-failed"
    assert writer.calls_made == 1
    assert (tmp_path / "workbook-brief.v1.json").read_bytes() == before
    journal = json.loads(
        (tmp_path / "workbook-deep-dive-call.v1.json").read_text("utf-8")
    )
    assert journal["state"] == "call_in_progress"
    assert journal["provider_failure"] == {
        "type": "TimeoutError",
        "message": "provider request timed out",
    }
    assert not (tmp_path / "ask-a-research-call.v1.json").exists()
    assert (
        trial.production_envelope.get_contribution("ask_a_enrichment", node_id="07W.2")
        is None
    )

    failed_journal = (tmp_path / "workbook-deep-dive-call.v1.json").read_bytes()
    drifted = DeepWriter()
    drifted.model_config_digest = workbook_prework_writers.LiveDeepDiveWriter(
        chat_factory=fake_factory,
        request_timeout=301.0,
    ).model_config_digest
    drifted_context = context.model_copy(update={"deep_dive_writer": drifted})
    with pytest.raises(SpecialistDispatchError) as replay:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=drifted_context,
        )
    assert replay.value.tag == "workbook-brief.deep-dive-call-ambiguous"
    assert drifted.calls_made == 0
    assert (tmp_path / "workbook-deep-dive-call.v1.json").read_bytes() == failed_journal


def test_completed_journal_replay_rejects_deep_dive_timeout_identity_drift(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    def fake_factory(*args, **kwargs):
        return SimpleNamespace(chat=object(), entry=None)

    default_identity = workbook_prework_writers.LiveDeepDiveWriter(
        chat_factory=fake_factory
    ).model_config_digest
    drifted_identity = workbook_prework_writers.LiveDeepDiveWriter(
        chat_factory=fake_factory,
        request_timeout=301.0,
    ).model_config_digest

    writer = DeepWriter()
    writer.model_config_digest = default_identity
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=writer,
    )
    activated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    drifted = DeepWriter()
    drifted.model_config_digest = drifted_identity
    drifted_context = context.model_copy(update={"deep_dive_writer": drifted})

    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=activated,
            runtime_context=drifted_context,
        )

    assert default_identity != drifted_identity
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"
    assert drifted.calls_made == 0


def test_unicode_term_variants_survive_workbook_brief_disk_roundtrip(
    tmp_path: Path,
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    before = read_workbook_brief(tmp_path)
    composed = "caf\u00e9"
    decomposed = "cafe\u0301"
    source_text = f"Compare {composed} with {decomposed}."
    marked_text = f"Compare **{composed}** with **{decomposed}**."
    abilities = tuple(
        DeepDiveAbilityInput(ability_id=vow.objective_id, text=vow.text)
        for vow in before.payload.pre_work.promise.vows
    )
    request = DeepDiveSkeletonRequest(
        lesson_ref="run:unicode-roundtrip",
        source_spans=(
            NarrationSourceSpan(
                span_id="vo:seg-01",
                text=source_text,
                source_ref="exports/segment-manifest-storyboard-b.yaml#segments/seg-01/narration_text",
            ),
            NarrationSourceSpan(
                span_id="delta:slide-01",
                text=source_text,
                source_ref="slides/slide-1-unicode.md#Narration (Speaker Notes)",
            ),
        ),
        source_claims=(
            SourceClaim(
                claim_id="claim:vo:seg-01",
                text=source_text,
                source_span_refs=("vo:seg-01",),
                role="vo",
            ),
            SourceClaim(
                claim_id="claim:delta:slide-01",
                text=source_text,
                source_span_refs=("delta:slide-01",),
                role="source_supported_delta",
            ),
        ),
        abilities=abilities,
    )
    candidate = DeepDiveSkeletonWriterResult(
        status="authored",
        sections=tuple(
            DeepDiveAbilitySection(
                ability_id=ability.ability_id,
                prose=f"{marked_text} {marked_text}",
                claims=(
                    DeepDiveSkeletonClaim(
                        skeleton_claim_id=f"skeleton-{index}",
                        text=marked_text,
                        source_claim_refs=("claim:vo:seg-01",),
                        source_span_refs=("vo:seg-01",),
                    ),
                    DeepDiveSkeletonClaim(
                        skeleton_claim_id=f"skeleton-{index}-delta",
                        text=marked_text,
                        source_claim_refs=("claim:delta:slide-01",),
                        source_span_refs=("delta:slide-01",),
                    ),
                ),
            )
            for index, ability in enumerate(abilities, start=1)
        ),
        bold_terms=(BoldTermMarker(term=composed), BoldTermMarker(term=decomposed)),
        known_losses=(),
        marker=None,
    )
    result = compose_deep_dive_skeleton(request, lambda _: candidate)
    receipt = DeepDiveExecutionReceiptV1(
        mode="live",
        calls=1,
        idempotency_key="sha256:" + "1" * 64,
        prior_payload_digest=before.payload_digest,
        model="test-model",
        model_config_digest="sha256:" + "2" * 64,
        cost_unavailable_reason="roundtrip-fixture-no-provider-call",
    )
    payload = WorkbookBriefPayloadV1.model_validate(
        before.payload.model_copy(
            update={"deep_dive_skeleton": result, "deep_dive_writer_receipt": receipt}
        ).model_dump()
    )
    artifact = WorkbookBriefArtifactV1(
        payload=payload,
        payload_digest=canonical_payload_digest(payload),
    )
    write_workbook_brief(tmp_path, artifact)
    reread = read_workbook_brief(tmp_path)
    assert tuple(term.term for term in reread.payload.deep_dive_skeleton.bold_terms) == (
        composed,
        decomposed,
    )
    assert reread.payload.deep_dive_skeleton.sections[0].prose == f"{marked_text} {marked_text}"


def test_corrupt_journal_state_and_receipt_fail_reconciliation(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    journal = json.loads(journal_path.read_text("utf-8"))
    journal["state"] = "unknown"
    journal_path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=envelope.trial_id),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"

    journal["state"] = "completed"
    journal["provider_receipt"]["mode"] = "offline_stub"
    journal["provider_receipt"]["calls"] = 0
    journal_path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=envelope.trial_id),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"

    journal_path.write_text("[]", encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=envelope.trial_id),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


@pytest.mark.parametrize(
    "mutation",
    ["normalization-records", "normalized-digest", "candidate-snapshot", "candidate-digest"],
)
def test_completed_journal_raw_to_normalized_mutations_fail_independently(
    tmp_path: Path, mutation: str
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    upgraded = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    journal = json.loads(journal_path.read_text("utf-8"))
    if mutation == "normalization-records":
        journal["provider_normalizations"] = ["forged"]
    elif mutation == "normalized-digest":
        journal["normalized_provider_payload_digest"] = "sha256:" + "f" * 64
    elif mutation == "candidate-snapshot":
        journal["candidate"]["extra"] = "forged"
    else:
        journal["candidate_digest"] = "sha256:" + "f" * 64
    journal_path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=upgraded,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


def test_journal_symlink_fails_closed(tmp_path: Path) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    external = tmp_path.parent / f"{tmp_path.name}-external-journal.json"
    journal_path.replace(external)
    try:
        journal_path.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=ProductionEnvelope(trial_id=envelope.trial_id),
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-reconciliation-failed"


def test_foreign_journal_temporary_file_is_not_deleted(tmp_path: Path) -> None:
    journal_path = tmp_path / "workbook-deep-dive-call.v1.json"
    temporary = journal_path.with_suffix(journal_path.suffix + ".tmp")
    temporary.write_text("owned-by-another-writer", encoding="utf-8")
    with pytest.raises(FileExistsError):
        workbook_wiring._atomic_json(journal_path, {"state": "new"})
    assert temporary.read_text("utf-8") == "owned-by-another-writer"

def test_brief_write_failure_keeps_deep_dive_persistence_tag(
    tmp_path: Path, monkeypatch
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    monkeypatch.setattr(
        workbook_wiring,
        "write_workbook_brief",
        lambda *_: (_ for _ in ()).throw(OSError("disk unavailable")),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=trial.production_envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-brief.deep-dive-persistence-failed"


def test_runtime_writer_initialization_preserves_base_and_deep_dive_tags(
    tmp_path: Path, monkeypatch
) -> None:
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="live",
    )
    write_runtime_context(context)

    class Boom:
        def __init__(self) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(workbook_prework_writers, "LiveSceneComposer", Boom)
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.runtime_context_for_run(tmp_path, node_id="07W.1")
    assert caught.value.tag == "workbook-brief.writer-init-failed"

    monkeypatch.setattr(
        workbook_prework_writers, "LiveSceneComposer", lambda: (lambda _: None)
    )
    monkeypatch.setattr(
        workbook_prework_writers, "LivePromiseTransformer", lambda: (lambda _: None)
    )
    monkeypatch.setattr(workbook_prework_writers, "LiveDeepDiveWriter", Boom)
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.runtime_context_for_run(tmp_path, node_id="07W.1")
    assert caught.value.tag == "workbook-brief.deep-dive-writer-init-failed"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "authored"),
        ("authority_digest", "sha256:" + "a" * 64),
        ("candidate_payload_digest", "sha256:" + "b" * 64),
        ("execution", {"schema_version": "planted"}),
        ("missing", None),
        ("extra", "planted"),
    ],
)
def test_activated_summary_mutations_fail_closed(
    tmp_path: Path, field: str, value: object
) -> None:
    shutil.copytree(LEGACY_RUN, tmp_path, dirs_exist_ok=True)
    trial = _load_current_legacy_trial(tmp_path)
    context = WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=ROOT,
        encounter_mode="recorded",
        context_origin="operator_migrated",
        writer_execution_mode="live",
        deep_dive_writer=DeepWriter(),
    )
    upgraded = workbook_wiring.run_workbook_band_node(
        node_id="07W.1",
        production_envelope=trial.production_envelope,
        runtime_context=context,
    )
    original = upgraded.get_contribution("workbook_brief", node_id="07W.1")
    output = dict(original.output)
    summary = dict(output["deep_dive_summary"])
    if field == "missing":
        output.pop("deep_dive_summary")
    elif field == "extra":
        summary["extra"] = value
        output["deep_dive_summary"] = summary
    else:
        summary[field] = value
        output["deep_dive_summary"] = summary
    planted = ProductionEnvelope(trial_id=upgraded.trial_id)
    planted.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief",
            node_id="07W.1",
            output=output,
            model_used="planted",
        )
    )
    with pytest.raises(SpecialistDispatchError):
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=planted, runtime_context=context
        )
