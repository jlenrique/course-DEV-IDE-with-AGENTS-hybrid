from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import yaml

from app.marcus.lesson_plan.ask_a_enrichment import (
    AskAContributionOutputV1,
    canonical_digest,
)
from app.marcus.lesson_plan.ask_b_hot_topics import AskBContributionOutputV1
from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker, DeepDiveAbilityInput
from app.marcus.lesson_plan.prework_artifact import (
    WorkbookBriefRuntimeContext,
    write_runtime_context,
)
from app.marcus.lesson_plan.prework_projection import (
    ObjectiveInput,
    PromiseProjection,
    PromiseTransformRequest,
    PromiseVow,
)
from app.marcus.lesson_plan.promise_projection import PromiseObjectiveResolution
from app.marcus.lesson_plan.research_demand import (
    AskAResearchDemandV1,
    AskBHotTopicsDemandV1,
    resolve_enrichment_demand,
)
from app.marcus.orchestrator import (
    ask_a_research_wiring,
    ask_b_research_wiring,
    workbook_wiring,
)
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.specialist_model_config import SpecialistModelConfig
from app.specialists.dispatch_errors import SpecialistDispatchError
from tests.helpers.workbook_slide_authority import (
    _plan_authority_receipt,
    install_single_slide_authority,
    single_slide_authority_payloads,
    write_single_slide_plan_sidecar,
)


def _empty_envelope() -> ProductionEnvelope:
    return ProductionEnvelope(trial_id=uuid4())


def _persist_run_json(envelope: ProductionEnvelope, run_dir: Path) -> None:
    """Persist the inner envelope like the sole runner writer would."""
    trial = ProductionTrialEnvelope(
        trial_id=envelope.trial_id,
        preset="production",
        corpus_path="fixture",
        operator_id="operator_test",
        started_at=datetime(2026, 7, 16, tzinfo=UTC),
        status="in-flight",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _ask_b_ready_demand() -> AskBHotTopicsDemandV1:
    raw = {
        "schema_version": "ask-b-hot-topics-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        "status": "ready",
        "workbook_brief_payload_digest": "sha256:" + "a" * 64,
        "abilities": (
            DeepDiveAbilityInput(ability_id="lo-1", text="Choose a first move."),
        ),
        "scene_digest": "sha256:" + "b" * 64,
        "scene_text": "A clinic hits workflow friction.",
        "known_losses": (),
    }
    raw["demand_digest"] = canonical_digest(raw)
    return AskBHotTopicsDemandV1.model_validate(raw, strict=True)


def _ask_b_provider_result() -> SimpleNamespace:
    row = SimpleNamespace(
        provider="scite",
        source_id="10.1000/first-move",
        title="Choosing a first move",
        body="Choose a first move with explicit decision criteria.",
        provider_metadata={"scite": {"venue": "Journal"}},
        authority_tier="peer_reviewed",
    )
    return SimpleNamespace(
        provider="scite",
        rows=[row],
        acceptance_met=True,
        iterations_used=1,
        refinement_log=[],
    )


COURSE_SOURCE_ROOT = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()


def _deep_dive_resolution() -> PromiseObjectiveResolution:
    return PromiseObjectiveResolution(
        status="authored",
        objectives=(ObjectiveInput(objective_id="LO-1", text="Choose a move.", status="ratified"),),
        authority_variants=("plan_dialogue",),
        authority_refs=("ratified-los.json#ratified_los/0",),
    )


def _authored_promise(request: PromiseTransformRequest) -> PromiseProjection:
    objectives = request.objectives
    return PromiseProjection(
        status="authored",
        vows=tuple(
            PromiseVow(objective_id=item.objective_id, text="I can choose a first move.")
            for item in objectives
        ),
        known_losses=(),
        marker=None,
    )


def _install_persisted_promise_writer(monkeypatch: pytest.MonkeyPatch) -> None:
    real_context_for_run = workbook_wiring.runtime_context_for_run

    def context_for_run(
        run_dir: Path, *, node_id: str | None = None
    ) -> WorkbookBriefRuntimeContext:
        context = real_context_for_run(run_dir, node_id=node_id)
        return context.model_copy(update={"promise_writer": _authored_promise})

    monkeypatch.setattr(workbook_wiring, "runtime_context_for_run", context_for_run)


def _write_deep_dive_authority(run_dir: Path) -> None:
    exports = run_dir / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        "segments:\n"
        "  - segment_id: seg-01\n"
        "    slide_id: slide-01\n"
        "    narration_text: Healthcare systems expose workflow friction.\n",
        encoding="utf-8",
    )


def _offline_context(tmp_path: Path) -> WorkbookBriefRuntimeContext:
    _write_deep_dive_authority(tmp_path)
    return WorkbookBriefRuntimeContext(
        run_dir=tmp_path,
        course_source_root=COURSE_SOURCE_ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
        promise_writer=_authored_promise,
    )


def test_irene_pass1_runner_payload_binds_run_identity_for_both_aliases(
    tmp_path: Path,
) -> None:
    from app.marcus.orchestrator import production_runner

    trial_id = UUID("92345678-1234-4234-8234-123456789abc")
    expected = {"runs_root": tmp_path.as_posix(), "run_id": str(trial_id)}

    for specialist_id in ("irene-pass1", "irene_pass1"):
        payload = production_runner._runner_payload_for_specialist(
            specialist_id=specialist_id,
            directive_path=None,
            bundle_dir=None,
            runs_root=tmp_path,
            trial_id=trial_id,
        )
        assert payload is not None
        assert {key: payload[key] for key in expected} == expected


def test_start_walk_reaches_07w1_with_persisted_normalized_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.marcus.orchestrator import production_runner
    from app.models.state.component_selection import ComponentSelection

    trial_id = UUID("82345678-1234-4234-8234-123456789abc")
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir(parents=True)
    source_root = COURSE_SOURCE_ROOT
    _write_deep_dive_authority(run_dir)
    lesson_plan, package = write_single_slide_plan_sidecar(run_dir, source_root)
    monkeypatch.setattr(
        workbook_wiring, "resolve_promise_objectives", lambda _: _deep_dive_resolution()
    )
    _install_persisted_promise_writer(monkeypatch)
    write_runtime_context(
        WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=source_root,
            encounter_mode="recorded",
            context_origin="new_start",
            writer_execution_mode="offline_stub",
        )
    )
    captured = []
    real_hook = workbook_wiring.run_workbook_band_node

    class _Adapter:
        def invoke_specialist(
            self, *, specialist_id, envelope, node_id=None, cost_usd=0.0, **kwargs
        ):
            updated = envelope.model_copy(deep=True)
            outputs = {
                "irene_pass1": {"lesson_plan": lesson_plan},
                "package_builder": package,
            }
            effective_id = "irene_pass1" if node_id == "05B" else specialist_id
            output = (
                {"lesson_plan": lesson_plan}
                if node_id == "05B"
                else outputs.get(specialist_id, {"specialist_id": specialist_id})
            )
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=effective_id,
                    node_id=node_id,
                    output=output,
                    model_used="fixture",
                    cost_usd=cost_usd,
                )
            )
            return updated

    def spy(**kwargs):
        if kwargs["node_id"] == "07W.1":
            captured.append(kwargs["runtime_context"])
            kwargs["production_envelope"] = install_single_slide_authority(
                kwargs["production_envelope"],
                run_dir=run_dir,
                course_source_root=source_root,
            )
        # 38-2 AC 7: disk-mediated predecessor visibility in the START walk —
        # when 07W.2 / 07W.4 dispatch, the sole-writer-persisted run.json
        # already carries the predecessor band contribution.
        if kwargs["node_id"] in {"07W.2", "07W.4"}:
            persisted = json.loads((run_dir / "run.json").read_text("utf-8"))
            coordinates = {
                (item["specialist_id"], item["node_id"])
                for item in persisted["production_envelope"]["contributions"]
            }
            predecessor = (
                ("workbook_brief", "07W.1")
                if kwargs["node_id"] == "07W.2"
                else ("workbook_review", "07W.3")
            )
            assert predecessor in coordinates
        return real_hook(**kwargs)

    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "0")
    monkeypatch.setattr(production_runner, "production_gate_ids", lambda _manifest: set())
    monkeypatch.setattr(workbook_wiring, "run_workbook_band_node", spy)
    result = production_runner.run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        allow_offline_cost_report=True,
        pause_at_gates=False,
        max_specialist_calls=100,
        component_selection=ComponentSelection(deck=True, motion=True, workbook=True),
        hud="off",
    )
    assert result.status == "completed"
    assert len(captured) == 1
    context = captured[0]
    assert (
        context.run_dir.resolve(),
        context.course_source_root.resolve(),
        context.encounter_mode,
        context.context_origin,
        context.writer_execution_mode,
    ) == (run_dir.resolve(), source_root, "recorded", "new_start", "offline_stub")
    assert (run_dir / "workbook-brief.v1.json").is_file()


def test_default_band_executes_real_brief_and_typed_ask_retryables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absent = tmp_path / "absent-demand"
    absent.mkdir()
    nonready = resolve_enrichment_demand(absent)
    monkeypatch.setattr(ask_a_research_wiring, "resolve_enrichment_demand", lambda _: nonready)
    monkeypatch.setattr(
        workbook_wiring, "resolve_promise_objectives", lambda _: _deep_dive_resolution()
    )
    envelope = install_single_slide_authority(
        _empty_envelope(),
        run_dir=tmp_path,
        course_source_root=COURSE_SOURCE_ROOT,
    )
    # 38-2 (conscious flip, A-3): 07W.4 is ACTIVATED — every band node now
    # takes runtime context, and the envelope is persisted between nodes the
    # way the sole runner writer does, so the disk-only Ask-B demand reader
    # sees the real 07W.1 brief authority.
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        _persist_run_json(envelope, tmp_path)
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id,
            production_envelope=envelope,
            runtime_context=_offline_context(tmp_path),
            dispatch_live=False,
        )
    _persist_run_json(envelope, tmp_path)

    # 37.2b (deliberate pin update, amendment A1): 07W.3 is ACTIVATED at the
    # exact coordinate — the legacy workbook_review_stub row never appears.
    assert [(item.node_id, item.specialist_id) for item in envelope.contributions] == [
        ("05B", "irene_pass1"),
        ("06", "package_builder"),
        ("07W.1", "workbook_brief"),
        ("07W.2", "ask_a_enrichment"),
        ("07W.3", "workbook_review"),
        ("07W.4", "ask_b_hot_topics"),
    ]
    assert envelope.contributions[2].model_used == "workbook-brief-offline"
    assert envelope.contributions[3].model_used == "deterministic-ask-a-research-wiring"
    assert envelope.contributions[4].model_used == "workbook-review-offline"
    # 38-2 (conscious flip, A-3): the generic stub marker at 07W.4 is retired
    # by activation — the node-specific deterministic marker takes its place.
    assert envelope.contributions[5].model_used == "deterministic-ask-b-hot-topics-wiring"
    assert envelope.contributions[2].output["schema_version"] == "workbook-brief.v1"
    assert envelope.contributions[2].output["status_summary"] == {
        "scene": "degraded",
        "promise": "authored",
    }
    assert envelope.contributions[3].output["disposition"] == "retryable_demand_not_ready"
    assert envelope.contributions[3].output["known_losses"] == ["ask_a_demand_not_ready"]
    # The offline brief carries a PRESENT-but-non-authored (offline-stub)
    # skeleton, so the activated review node degrades honestly: no enrichment
    # result, a typed loss NAMING the skeleton's recorded state (R5 — never
    # the "no skeleton" loss), Check/Reflection honestly stubbed.
    # R15: the expected payload is a hand-written LITERAL, never computed from
    # the function under test (the digest was computed once, out-of-band, from
    # the canonical-JSON sha256 of the payload minus its digest field).
    assert envelope.contributions[4].output == {
        "schema_version": "workbook-review-contribution.v1",
        "node_id": "07W.3",
        "specialist_id": "workbook_review",
        "deep_dive_enrichment": None,
        "deep_dive_enrichment_receipt": None,
        "known_losses": [
            "deep_dive_enrichment_skeleton_not_authored_unavailable",
            "check_writer_not_yet_wired",
            "reflection_writer_not_yet_wired",
        ],
        "output_digest": (
            "sha256:15a48dba512d2790dbcb92872725d3fae39c1e50e506d90faa331bed92e4d314"
        ),
    }
    # 38-2 (conscious flip, A-3): the `ask_b_not_yet_wired` stub-output pin is
    # consciously retired — the offline brief carries an authored Promise +
    # degraded Scene, so the REAL Ask-B demand is ready-with-scene-loss and
    # the kill-switch-off posture yields the typed retryable (zero calls).
    assert envelope.contributions[5].output == AskBContributionOutputV1.build_retryable(
        disposition="retryable_dispatch_disabled", loss="ask_b_dispatch_disabled"
    ).model_dump(mode="json")


# 38-2 M-7: the 38-1 upgrade/no-op proof is PARAMETRIZED over the ask band
# coordinates (07W.2, 07W.4) — one module, one coordinate axis, never a
# hand-cloned second suite. M-4 posture: factories is None (default registry)
# and the dispatch is monkeypatched ONLY at the owned wiring seam — injecting
# a factories override would route around the `and factories is None` guard
# and leave the resume-skip fix (row 7) dead.
@pytest.mark.parametrize(
    ("node_id", "specialist_id", "stub_loss", "module", "run_name", "output", "marker"),
    [
        (
            "07W.2",
            "ask_a_enrichment",
            "ask_a_not_yet_wired",
            ask_a_research_wiring,
            "run_ask_a_research",
            AskAContributionOutputV1.build_retryable(
                disposition="retryable_dispatch_disabled", loss="ask_a_dispatch_disabled"
            ),
            "deterministic-ask-a-research-wiring",
        ),
        (
            "07W.4",
            "ask_b_hot_topics",
            "ask_b_not_yet_wired",
            ask_b_research_wiring,
            "run_ask_b_research",
            AskBContributionOutputV1.build_retryable(
                disposition="retryable_dispatch_disabled", loss="ask_b_dispatch_disabled"
            ),
            "deterministic-ask-b-hot-topics-wiring",
        ),
    ],
)
def test_ask_default_factory_upgrades_stub_and_retryable_is_exact_noop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    node_id: str,
    specialist_id: str,
    stub_loss: str,
    module: object,
    run_name: str,
    output: object,
    marker: str,
) -> None:
    """Matrix row 7: a persisted `not_yet_wired` stub upgrades at the SAME
    coordinate under the DEFAULT registry (the resume-skip fix), and an
    unchanged retryable resume is an exact no-op."""
    calls = 0

    def run(**_: object) -> object:
        nonlocal calls
        calls += 1
        return output

    monkeypatch.setattr(module, run_name, run)
    envelope = _empty_envelope()
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output={
                "research_entries": [],
                "stub_status": "not_yet_wired",
                "known_losses": [stub_loss],
            },
            model_used="deterministic-workbook-band-stub",
        )
    )
    first = workbook_wiring.run_workbook_band_node(
        node_id=node_id,
        production_envelope=envelope,
        runtime_context=_offline_context(tmp_path),
        dispatch_live=False,
    )
    exact = first.get_contribution(specialist_id, node_id=node_id)
    assert exact is not None
    assert exact.output == output.model_dump(mode="json")
    assert exact.model_used == marker
    second = workbook_wiring.run_workbook_band_node(
        node_id=node_id,
        production_envelope=first,
        runtime_context=_offline_context(tmp_path),
        dispatch_live=False,
    )
    assert second is first
    assert calls == 2


def test_reconcile_not_skip_set_is_exactly_the_activated_band_tail() -> None:
    """38-2 W-2 named set-membership pin: SET EQUALITY, not membership-of-one.

    This trap has recurred once per band-node activation — a node missing
    from this set is silently skipped FOREVER on resume under the default
    registry. Any future band-node activation must extend this set AND this
    pin in the same diff.
    """
    assert frozenset(
        {"07W.2", "07W.3", "07W.4"}
    ) == workbook_wiring.WORKBOOK_BAND_RECONCILE_NODE_IDS


def test_ask_b_completed_contribution_resume_is_exact_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Matrix row 9 (M-4, paired with row 7): persisted COMPLETED Ask-B
    contribution + resume → zero dispatch AND zero persistence/projection
    effects — an exact no-op, never a recall."""
    envelope = _empty_envelope()
    demand = _ask_b_ready_demand()
    monkeypatch.setattr(
        ask_b_research_wiring, "resolve_hot_topics_demand", lambda _: demand
    )
    completed = ask_b_research_wiring.run_ask_b_research(
        run_dir=tmp_path,
        trial_id=envelope.trial_id,
        dispatch_live=True,
        dispatch=lambda _: _ask_b_provider_result(),
    )
    assert completed.disposition.startswith("completed")
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="ask_b_hot_topics",
            node_id="07W.4",
            output=completed.model_dump(mode="json"),
            model_used="deterministic-ask-b-hot-topics-wiring",
        )
    )

    def no_dispatch(_: object) -> object:
        raise AssertionError("completed resume must make zero dispatcher invocations")

    monkeypatch.setattr(ask_b_research_wiring, "_default_dispatch", no_dispatch)
    resumed = workbook_wiring.run_workbook_band_node(
        node_id="07W.4",
        production_envelope=envelope,
        runtime_context=_offline_context(tmp_path),
        dispatch_live=True,
    )
    assert resumed is envelope  # identity → nothing to persist/project/emit


# 38-2 M-7: split-brain proof parametrized over the ask coordinates.
@pytest.mark.parametrize("ask", ["ask-a", "ask-b"])
def test_ask_completed_envelope_without_journal_fails_split_brain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ask: str
) -> None:
    source_run = tmp_path / "source-run"
    source_run.mkdir()
    if ask == "ask-a":
        raw_demand = {
            "schema_version": "ask-a-research-demand.v1",
            "specialist_id": "workbook_brief",
            "node_id": "07W.1",
            "status": "ready",
            "workbook_brief_payload_digest": "sha256:" + "a" * 64,
            "skeleton_authority_digest": "sha256:" + "b" * 64,
            "skeleton_candidate_digest": "sha256:" + "c" * 64,
            "abilities": (DeepDiveAbilityInput(ability_id="lo-1", text="Choose a move."),),
            "bold_terms": (BoldTermMarker(term="first move"),),
            "source_claim_refs": ("claim-1",),
            "known_losses": (),
        }
        raw_demand["demand_digest"] = canonical_digest(raw_demand)
        demand = AskAResearchDemandV1.model_validate(raw_demand, strict=True)
        monkeypatch.setattr(
            ask_a_research_wiring, "resolve_enrichment_demand", lambda _: demand
        )
        node_id, specialist_id, marker = (
            "07W.2",
            "ask_a_enrichment",
            "deterministic-ask-a-research-wiring",
        )
        completed = ask_a_research_wiring.run_ask_a_research(
            run_dir=source_run,
            trial_id="source",
            dispatch_live=True,
            dispatch=lambda _: _ask_b_provider_result(),
        )
        expected_tag = "ask-a.split-brain"
    else:
        monkeypatch.setattr(
            ask_b_research_wiring,
            "resolve_hot_topics_demand",
            lambda _: _ask_b_ready_demand(),
        )
        node_id, specialist_id, marker = (
            "07W.4",
            "ask_b_hot_topics",
            "deterministic-ask-b-hot-topics-wiring",
        )
        completed = ask_b_research_wiring.run_ask_b_research(
            run_dir=source_run,
            trial_id="source",
            dispatch_live=True,
            dispatch=lambda _: _ask_b_provider_result(),
        )
        expected_tag = "ask-b.split-brain"
    assert completed.disposition.startswith("completed")
    envelope = _empty_envelope()
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=completed.model_dump(mode="json"),
            model_used=marker,
        )
    )
    target_run = tmp_path / "target-run"
    target_run.mkdir()

    with pytest.raises(SpecialistDispatchError) as exc:
        workbook_wiring.run_workbook_band_node(
            node_id=node_id,
            production_envelope=envelope,
            runtime_context=_offline_context(target_run),
            dispatch_live=True,
        )

    assert exc.value.tag == expected_tag


# 38-2 T4 R2 (Auditor row-14, M-7 idiom): the conflicting-completed
# split-brain branch gets its OWN parametrized proof — distinct from the
# completed-WITHOUT-journal branch above.
@pytest.mark.parametrize("ask", ["ask-a", "ask-b"])
def test_ask_conflicting_completed_contribution_fails_split_brain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ask: str
) -> None:
    """T4 R2: completed journal PRESENT at the run coordinate + persisted
    COMPLETED contribution whose body DIFFERS from the journal replay →
    ``ask-{a,b}.split-brain`` (workbook_wiring conflicting-completed branch),
    with zero re-dispatch."""

    def variant_result(body: str) -> SimpleNamespace:
        result = _ask_b_provider_result()
        result.rows[0].body = body
        return result

    journal_body = "Choose a first move with explicit decision criteria."
    conflict_body = "Choose a first move quickly across clinic workflows."
    conflicting_run = tmp_path / "conflicting-run"
    conflicting_run.mkdir()
    if ask == "ask-a":
        raw_demand = {
            "schema_version": "ask-a-research-demand.v1",
            "specialist_id": "workbook_brief",
            "node_id": "07W.1",
            "status": "ready",
            "workbook_brief_payload_digest": "sha256:" + "a" * 64,
            "skeleton_authority_digest": "sha256:" + "b" * 64,
            "skeleton_candidate_digest": "sha256:" + "c" * 64,
            "abilities": (DeepDiveAbilityInput(ability_id="lo-1", text="Choose a move."),),
            "bold_terms": (BoldTermMarker(term="first move"),),
            "source_claim_refs": ("claim-1",),
            "known_losses": (),
        }
        raw_demand["demand_digest"] = canonical_digest(raw_demand)
        demand = AskAResearchDemandV1.model_validate(raw_demand, strict=True)
        monkeypatch.setattr(
            ask_a_research_wiring, "resolve_enrichment_demand", lambda _: demand
        )
        module, run_name = ask_a_research_wiring, "run_ask_a_research"
        node_id, specialist_id, expected_tag = (
            "07W.2",
            "ask_a_enrichment",
            "ask-a.split-brain",
        )
    else:
        monkeypatch.setattr(
            ask_b_research_wiring,
            "resolve_hot_topics_demand",
            lambda _: _ask_b_ready_demand(),
        )
        module, run_name = ask_b_research_wiring, "run_ask_b_research"
        node_id, specialist_id, expected_tag = (
            "07W.4",
            "ask_b_hot_topics",
            "ask-b.split-brain",
        )
    run = getattr(module, run_name)
    envelope = _empty_envelope()
    # Journal at the RESUME coordinate (tmp_path) replays to output A ...
    journal_backed = run(
        run_dir=tmp_path,
        trial_id=envelope.trial_id,
        dispatch_live=True,
        dispatch=lambda _: variant_result(journal_body),
    )
    # ... while the persisted contribution carries a DIFFERENT completed body.
    conflicting = run(
        run_dir=conflicting_run,
        trial_id=envelope.trial_id,
        dispatch_live=True,
        dispatch=lambda _: variant_result(conflict_body),
    )
    assert journal_backed.disposition.startswith("completed")
    assert conflicting.disposition.startswith("completed")
    assert journal_backed != conflicting
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=conflicting.model_dump(mode="json"),
            model_used=f"deterministic-{ask}-wiring-fixture",
        )
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        workbook_wiring.run_workbook_band_node(
            node_id=node_id,
            production_envelope=envelope,
            runtime_context=_offline_context(tmp_path),
            dispatch_live=True,
        )
    assert exc.value.tag == expected_tag


# 38-2 T4 R3 (B2, live-repro'd; conscious symmetric hardening at BOTH band
# coordinates): stub detection keys on FULL stub-shape equality — never the
# single `stub_status` magic key.
@pytest.mark.parametrize("ask", ["ask-a", "ask-b"])
def test_forged_completed_contribution_with_stub_magic_key_never_redispatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ask: str
) -> None:
    """T4 R3 negative pin: a forged completed-CLAIMING contribution that
    carries the `stub_status: not_yet_wired` magic key must go to strict
    validation and REJECT (``ask-{a,b}.reconciliation-failed``) — never be
    treated as the honest stub and re-dispatched (paid-call poisoning)."""
    if ask == "ask-a":
        module, run_name = ask_a_research_wiring, "run_ask_a_research"
        node_id, specialist_id, expected_tag = (
            "07W.2",
            "ask_a_enrichment",
            "ask-a.reconciliation-failed",
        )
    else:
        module, run_name = ask_b_research_wiring, "run_ask_b_research"
        node_id, specialist_id, expected_tag = (
            "07W.4",
            "ask_b_hot_topics",
            "ask-b.reconciliation-failed",
        )

    def never_dispatch(**_: object) -> object:
        raise AssertionError("forged magic-key contribution must never re-dispatch")

    monkeypatch.setattr(module, run_name, never_dispatch)
    forged = {
        "schema_version": (
            "ask-a-contribution-output.v1" if ask == "ask-a" else "ask-b-contribution-output.v1"
        ),
        "disposition": "completed_ready",
        "research_entries": [],
        "known_losses": [],
        "research_intake": None,
        "dispatcher_invocations": 1,
        "output_digest": "sha256:" + "9" * 64,
        "stub_status": "not_yet_wired",  # the B2 magic key
    }
    envelope = _empty_envelope()
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=forged,
            model_used="forged-fixture",
        )
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        workbook_wiring.run_workbook_band_node(
            node_id=node_id,
            production_envelope=envelope,
            runtime_context=_offline_context(tmp_path),
            dispatch_live=True,
        )
    assert exc.value.tag == expected_tag


def test_atomic_outer_writer_preserves_last_durable_run_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.marcus.orchestrator import production_runner

    production = _empty_envelope()
    outer = ProductionTrialEnvelope(
        trial_id=production.trial_id,
        preset="production",
        corpus_path="fixture",
        operator_id="operator_test",
        started_at=datetime(2026, 7, 13, tzinfo=UTC),
        status="in-flight",
        production_clone_launch_evidence=True,
        production_envelope=production,
    )
    run_dir = tmp_path / str(production.trial_id)
    run_dir.mkdir()
    durable = run_dir / "run.json"
    durable.write_text("durable-before\n", encoding="utf-8")

    def fail_replace(*_: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(production_runner.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        production_runner._persist_envelope(outer, tmp_path)
    assert durable.read_text("utf-8") == "durable-before\n"
    assert not (run_dir / "run.json.tmp").exists()


def test_factory_is_not_called_when_exact_coordinate_exists() -> None:
    calls: list[str] = []

    def spy(node_id: str, envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"spy": True}

    factories: dict[str, Callable[[str, ProductionEnvelope], dict[str, object]]] = {"07W.3": spy}
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.3", production_envelope=_empty_envelope(), factories=factories
    )
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.3", production_envelope=envelope, factories=factories
    )
    assert calls == ["07W.3"]
    assert repeated is envelope


def test_partial_resume_only_calls_missing_nodes() -> None:
    calls: list[str] = []

    def spy(node_id: str, envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"node": node_id}

    factories = dict.fromkeys(workbook_wiring.WORKBOOK_BAND_NODE_IDS, spy)
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=_empty_envelope(), factories=factories
    )
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        if node_id == "07W.1":
            continue
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=envelope, factories=factories
        )
    assert calls == list(workbook_wiring.WORKBOOK_BAND_NODE_IDS)


def test_serialized_partial_resume_only_invokes_missing_factories() -> None:
    calls: list[str] = []

    def spy(node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"node": node_id}

    factories = dict.fromkeys(workbook_wiring.WORKBOOK_BAND_NODE_IDS, spy)
    envelope = _empty_envelope()
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS[:2]:
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=envelope, factories=factories
        )
    reloaded = ProductionEnvelope.model_validate_json(envelope.model_dump_json())
    calls.clear()
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        if node_id == "07W.1":
            continue
        reloaded = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=reloaded, factories=factories
        )
    assert calls == ["07W.3", "07W.4"]


@pytest.mark.parametrize(
    ("factory", "tag"),
    [
        (
            lambda _n, _e: (_ for _ in ()).throw(RuntimeError("boom")),
            "workbook.band.factory-failed",
        ),
        (lambda _n, _e: ["not-a-dict"], "workbook.band.invalid-output"),
        (lambda _n, _e: {"bad": object()}, "workbook.band.invalid-output"),
    ],
)
def test_factory_failures_are_tagged(factory: object, tag: str) -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=_empty_envelope(),
            factories={"07W.1": factory},  # type: ignore[dict-item]
        )
    assert caught.value.tag == tag


def test_invalid_context_is_tagged() -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=object(),  # type: ignore[arg-type]
        )
    assert caught.value.tag == "workbook.band.invalid-context"


def test_unknown_node_is_tagged() -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.9", production_envelope=_empty_envelope()
        )
    assert caught.value.tag == "workbook.band.unknown-node"


def test_manifest_band_and_model_config_are_pinned() -> None:
    raw = yaml.safe_load(Path("state/config/pipeline-manifest.yaml").read_text("utf-8"))
    nodes = {node["id"]: node for node in raw["nodes"]}
    order = [node["id"] for node in raw["nodes"]]
    assert order[-5:] == ["07W.1", "07W.2", "07W.3", "07W.4", "07W"]
    expected_after = {
        "07W.1": "15",
        "07W.2": "07W.1",
        "07W.3": "07W.2",
        "07W.4": "07W.3",
        "07W": "07W.4",
    }
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        node = nodes[node_id]
        assert node["specialist_id"] is None
        assert node["gate"] is False
        assert node["hud_tracked"] is False
        assert node["sub_phase_of"] == "07W"
        assert node["insertion_after"] == expected_after[node_id]
    config = SpecialistModelConfig.model_validate(
        yaml.safe_load(
            Path("app/marcus/orchestrator/workbook_writer_model_config.yaml").read_text("utf-8")
        )
    )
    assert config.model_dump() == {
        "specialist_id": "workbook_writer",
        "default_model": "gpt-5",
        "per_node_overrides": {},
        "temperature_default": 0.2,
    }
    config_ref = "app/marcus/orchestrator/workbook_writer_model_config.yaml"
    assert nodes["07W.1"]["model_config_ref"] == config_ref
    assert nodes["07W.3"]["model_config_ref"] == config_ref
    assert nodes["07W.2"]["model_config_ref"] is None
    assert nodes["07W.4"]["model_config_ref"] is None
    assert nodes["07W"]["model_config_ref"] is None


@pytest.mark.parametrize(
    ("offline_after_g1", "failure_tag"),
    [
        (False, None),
        (True, None),
        (True, "workbook.band.invalid-context"),
        (True, "workbook.band.unknown-node"),
    ],
)
def test_real_start_then_continuation_reaches_band_in_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    offline_after_g1: bool,
    failure_tag: str | None,
) -> None:
    """Behavioral two-walk proof: pre-band pause, then one real resume walk."""
    from app.gates.resume_api import clear_resume_registry
    from app.marcus.orchestrator import production_runner
    from app.models.state.component_selection import ComponentSelection
    from app.models.state.operator_verdict import OperatorVerdict

    trial_id = UUID("72345678-1234-4234-8234-123456789abc")
    lesson_plan, package = single_slide_authority_payloads(COURSE_SOURCE_ROOT)
    calls: list[str] = []
    contexts: list[WorkbookBriefRuntimeContext] = []
    real_hook = workbook_wiring.run_workbook_band_node

    class _Adapter:
        def invoke_specialist(
            self,
            *,
            specialist_id: str,
            envelope: ProductionEnvelope,
            cost_usd: float = 0.0,
            node_id: str | None = None,
            **_kwargs: object,
        ) -> ProductionEnvelope:
            updated = envelope.model_copy(deep=True)
            outputs = {
                "irene_pass1": {"lesson_plan": lesson_plan},
                "package_builder": package,
                "cd": {"cd_directive": {"experience_profile": "text-led"}},
            }
            effective_id = "irene_pass1" if node_id == "05B" else specialist_id
            output = (
                # Story 41-2: with the walk now KEYED (so texas@02 dispatches
                # instead of silently skipping), the §06 builder actually runs on
                # the live [False-None] continuation and validates the Pass-1
                # authority receipt — so the fake §05B irene contribution must
                # carry a matching receipt (mirrors install_single_slide_authority).
                {
                    "lesson_plan": lesson_plan,
                    "plan_authority_receipt": _plan_authority_receipt(
                        lesson_plan, COURSE_SOURCE_ROOT
                    ),
                }
                if node_id == "05B"
                else outputs.get(specialist_id, {"specialist_id": specialist_id})
            )
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=effective_id,
                    output=output,
                    model_used="gpt-5-nano",
                    cost_usd=cost_usd,
                    node_id=node_id,
                )
            )
            return updated

    def _spy(**kwargs: object) -> ProductionEnvelope:
        calls.append(str(kwargs["node_id"]))
        if kwargs["node_id"] == "07W.1" and isinstance(
            kwargs.get("runtime_context"), WorkbookBriefRuntimeContext
        ):
            contexts.append(kwargs["runtime_context"])
            kwargs["production_envelope"] = install_single_slide_authority(
                kwargs["production_envelope"],  # type: ignore[arg-type]
                run_dir=tmp_path / str(trial_id),
                course_source_root=COURSE_SOURCE_ROOT,
            )
        # 38-2 AC 7: disk-mediated predecessor visibility in the CONTINUATION
        # walk — 07W.3 → disk → 07W.4 (and 07W.1 → disk → 07W.2) through the
        # sole `_persist_envelope` writer.
        if kwargs["node_id"] in {"07W.2", "07W.4"} and failure_tag is None:
            persisted = json.loads(
                (tmp_path / str(trial_id) / "run.json").read_text("utf-8")
            )
            coordinates = {
                (item["specialist_id"], item["node_id"])
                for item in persisted["production_envelope"]["contributions"]
            }
            predecessor = (
                ("workbook_brief", "07W.1")
                if kwargs["node_id"] == "07W.2"
                else ("workbook_review", "07W.3")
            )
            assert predecessor in coordinates
        if failure_tag == "workbook.band.invalid-context":
            return real_hook(
                node_id=str(kwargs["node_id"]),
                production_envelope=object(),  # type: ignore[arg-type]
            )
        if failure_tag == "workbook.band.unknown-node":
            return real_hook(
                node_id="07W.9",
                production_envelope=kwargs["production_envelope"],  # type: ignore[arg-type]
            )
        return real_hook(**kwargs)  # type: ignore[arg-type]

    clear_resume_registry()
    # Story 41-2: a production run (allow_offline_cost_report=False) now fails
    # loud at any entered, not-already-carrying specialist that does not
    # dispatch. This behavioral proof installs a fake ProductionDispatchAdapter,
    # so the walk must be KEYED for that adapter to dispatch texas@02 (and the
    # post-G1 specialists) — the prior keyless setup relied on the now-removed
    # silent-skip of texas to reach G1. Keying is the valid production-run config
    # for this fake-adapter behavioral test.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "0")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)
    monkeypatch.setattr(production_runner, "production_gate_ids", lambda _m: {"G1"})
    monkeypatch.setattr(production_runner, "_record_cost", lambda **_kwargs: None)
    monkeypatch.setattr(
        production_runner,
        "_run_start_preflight_gate",
        lambda *_args, **_kwargs: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(workbook_wiring, "run_workbook_band_node", _spy)

    started = production_runner.run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=100,
        component_selection=ComponentSelection(deck=True, motion=True, workbook=True),
        hud="off",
    )
    assert started.paused_gate == "G1"
    assert calls == []
    source_root = COURSE_SOURCE_ROOT
    run_dir = tmp_path / str(trial_id)
    _write_deep_dive_authority(run_dir)
    write_single_slide_plan_sidecar(run_dir, source_root)
    monkeypatch.setattr(
        workbook_wiring, "resolve_promise_objectives", lambda _: _deep_dive_resolution()
    )
    _install_persisted_promise_writer(monkeypatch)
    write_runtime_context(
        WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=source_root,
            encounter_mode="recorded",
            context_origin="new_start",
            writer_execution_mode="offline_stub",
        )
    )

    card_payload = json.loads(
        (tmp_path / str(trial_id) / "decision-card-G1.json").read_text("utf-8")
    )
    verdict = OperatorVerdict(
        trial_id=trial_id,
        verb="approve",
        gate_id="G1",
        card_id=UUID(card_payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=card_payload["digest"],
    )
    # The start walk must be a genuine gated walk. Once G1 is accepted, switch
    # only the persisted continuation harness to offline traversal so later
    # unrelated production gates do not prevent this continuation reaching the
    # terminal band. The band hook itself is required to ignore this flag.
    checkpoint_path = tmp_path / str(trial_id) / "checkpoint.json"
    if offline_after_g1:
        checkpoint = json.loads(checkpoint_path.read_text("utf-8"))
        checkpoint["runner"]["allow_offline_cost_report"] = True
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", "utf-8")
    resumed = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=verdict,
        runs_root=tmp_path,
        max_specialist_calls=100,
    )
    for _ in range(12):
        if resumed.status != "paused-at-gate":
            break
        gate_id = resumed.paused_gate
        assert gate_id is not None
        payload = json.loads(
            (tmp_path / str(trial_id) / f"decision-card-{gate_id}.json").read_text("utf-8")
        )
        resumed = production_runner.resume_production_trial(
            trial_id=trial_id,
            verdict=OperatorVerdict(
                trial_id=trial_id,
                verb="approve",
                gate_id=gate_id,
                card_id=UUID(payload["card"]["card_id"]),
                operator_id="operator_test",
                decision_card_digest=payload["digest"],
            ),
            runs_root=tmp_path,
            max_specialist_calls=100,
        )
    if failure_tag is not None:
        assert resumed.status == "paused-at-error"
        assert calls == ["07W.1"]
        error_pause = json.loads((tmp_path / str(trial_id) / "error-pause.json").read_text("utf-8"))
        assert error_pause["node_id"] == "07W.1"
        assert error_pause["tag"] == failure_tag
        assert (
            resumed.production_envelope.get_contribution(
                workbook_wiring.WORKBOOK_BRIEF_SPECIALIST_ID, node_id="07W.1"
            )
            is None
        )
        return
    assert resumed.status == "completed", resumed.model_dump(mode="json")
    assert calls == list(workbook_wiring.WORKBOOK_BAND_NODE_IDS)
    assert len(contexts) == 1
    context = contexts[0]
    assert (
        context.run_dir.resolve(),
        context.course_source_root.resolve(),
        context.encounter_mode,
        context.context_origin,
        context.writer_execution_mode,
    ) == (run_dir.resolve(), source_root, "recorded", "new_start", "offline_stub")
    assert (run_dir / "workbook-brief.v1.json").is_file()
    for node_id, specialist_id in workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS.items():
        assert (
            resumed.production_envelope.get_contribution(specialist_id, node_id=node_id) is not None
        )
