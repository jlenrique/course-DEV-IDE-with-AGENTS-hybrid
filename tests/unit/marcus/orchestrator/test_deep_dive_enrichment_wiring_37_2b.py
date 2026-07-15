"""Story 37.2b — exactly-once journaled 07W.3 dispatch + band reconciliation."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichedWriterResult,
    build_workbook_review_contribution,
)
from app.marcus.lesson_plan.deep_dive_enrichment_provider_contract import (
    canonical_json_mapping,
    normalize_deep_dive_enrichment_provider_payload,
    provider_payload_digest,
)
from app.marcus.lesson_plan.prework_artifact import WorkbookBriefRuntimeContext
from app.marcus.orchestrator import workbook_wiring
from app.marcus.orchestrator.deep_dive_enrichment_wiring import (
    DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME,
    run_workbook_review,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.specialists.dispatch_errors import SpecialistDispatchError
from tests.helpers.deep_dive_enrichment_37_2b import (
    ask_a_output_payload,
    degraded_candidate,
    enriched_candidate,
    install_brief,
    install_run_json,
    make_request,
)

COURSE_SOURCE_ROOT = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()


def _context(
    run_dir: Path,
    *,
    mode: str = "offline_stub",
    writer: object | None = None,
) -> WorkbookBriefRuntimeContext:
    return WorkbookBriefRuntimeContext(
        run_dir=run_dir,
        course_source_root=COURSE_SOURCE_ROOT,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode=mode,  # type: ignore[arg-type]
        deep_dive_enrichment_writer=writer,
    )


class _FakeEnrichmentWriter:
    """Duck-typed live writer honoring the provider-evidence attribute contract."""

    def __init__(self, factory) -> None:
        self._factory = factory
        self.calls_made = 0
        self.model_config = SimpleNamespace(default_model="gpt-5")
        self.model_config_digest = "sha256:" + "4" * 64
        self.provider_schema = DeepDiveEnrichedWriterResult.model_json_schema()
        self.provider_schema_digest = provider_payload_digest(self.provider_schema)
        self.last_raw_provider_payload: dict[str, Any] | None = None
        self.last_raw_provider_payload_digest: str | None = None
        self.last_provider_normalizations: tuple[str, ...] = ()
        self.last_normalized_provider_payload_digest: str | None = None
        self.last_provider_normalization_error: str | None = None
        self.last_request_id = "req-fixture"
        self.last_latency_ms = 12.5
        self.last_input_tokens = 100
        self.last_output_tokens = 50
        self.last_cost_usd = 0.01
        self.last_cost_unavailable_reason = None

    def __call__(self, request) -> DeepDiveEnrichedWriterResult:
        self.calls_made += 1
        candidate = self._factory(request)
        payload = canonical_json_mapping(candidate.model_dump(mode="json"))
        self.last_raw_provider_payload = payload
        self.last_raw_provider_payload_digest = provider_payload_digest(payload)
        normalized, records = normalize_deep_dive_enrichment_provider_payload(payload)
        self.last_provider_normalizations = records
        self.last_normalized_provider_payload_digest = provider_payload_digest(normalized)
        return candidate


def _prepare_run(tmp_path: Path) -> Path:
    install_brief(tmp_path)
    install_run_json(tmp_path, ask_a_output=ask_a_output_payload())
    return tmp_path


# ---------------------------------------------------------------------------
# Offline compose (honest non-authored; goldens run without a model)
# ---------------------------------------------------------------------------


def test_offline_mode_composes_without_journal(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=_context(run_dir)
    )
    assert output["deep_dive_enrichment"]["status"] == "unavailable"
    assert output["deep_dive_enrichment"]["known_losses"] == [
        "deep_dive_enrichment_writer_unavailable"
    ]
    assert output["deep_dive_enrichment_receipt"]["calls"] == 0
    assert output["known_losses"] == [
        "check_writer_not_yet_wired",
        "reflection_writer_not_yet_wired",
    ]
    assert not (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).exists()


def test_missing_brief_yields_typed_skeleton_unavailable(tmp_path: Path) -> None:
    install_run_json(tmp_path, ask_a_output=ask_a_output_payload())
    output = run_workbook_review(
        run_dir=tmp_path, trial_id="trial-x", runtime_context=_context(tmp_path)
    )
    assert output["deep_dive_enrichment"] is None
    assert output["known_losses"] == [
        "deep_dive_enrichment_skeleton_unavailable",
        "check_writer_not_yet_wired",
        "reflection_writer_not_yet_wired",
    ]


# ---------------------------------------------------------------------------
# Live journal — exactly-once, crash-safe, zero-recall replay
# ---------------------------------------------------------------------------


def test_live_dispatch_journals_and_replays_with_zero_provider_calls(
    tmp_path: Path,
) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert writer.calls_made == 1
    journal = json.loads(
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal["schema_version"] == "workbook-deep-dive-enrichment-call.v1"
    assert journal["state"] == "completed"
    assert journal["raw_provider_payload"] == writer.last_raw_provider_payload
    assert journal["provider_receipt"]["idempotency_key"] == journal["idempotency_key"]
    assert output["deep_dive_enrichment"]["status"] == "enriched"
    replayed = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert writer.calls_made == 1  # zero provider calls on replay
    assert replayed == output


def test_call_in_progress_journal_is_ambiguous_hard_pause(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    request = make_request()
    del request
    (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).write_text(
        json.dumps(
            {
                "schema_version": "workbook-deep-dive-enrichment-call.v1",
                "state": "call_in_progress",
                "idempotency_key": "sha256:" + "5" * 64,
            }
        )
        + "\n",
        "utf-8",
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(
            run_dir=run_dir,
            trial_id="trial-x",
            runtime_context=_context(run_dir, mode="live", writer=writer),
        )
    assert caught.value.tag == "workbook-review.enrichment-call-ambiguous"
    assert writer.calls_made == 0


def test_journal_identity_mismatch_fails_reconciliation(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    journal_path = run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME
    journal = json.loads(journal_path.read_text("utf-8"))
    journal["idempotency_key"] = "sha256:" + "6" * 64
    journal_path.write_text(json.dumps(journal) + "\n", "utf-8")
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(
            run_dir=run_dir, trial_id="trial-x", runtime_context=context
        )
    assert caught.value.tag == "workbook-review.enrichment-reconciliation-failed"
    assert writer.calls_made == 1


def test_writer_failure_persists_evidence_then_next_entry_is_prior_failure(
    tmp_path: Path,
) -> None:
    run_dir = _prepare_run(tmp_path)

    def _boom(_request) -> DeepDiveEnrichedWriterResult:
        raise RuntimeError("provider socket dropped")

    writer = _FakeEnrichmentWriter(_boom)
    context = _context(run_dir, mode="live", writer=writer)
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert caught.value.tag == "workbook-review.enrichment-writer-execution-failed"
    journal = json.loads(
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal["state"] == "call_in_progress"
    assert journal["provider_failure"]["type"] == "RuntimeError"
    # R12: first-run-stands — a journal carrying a RECORDED provider failure
    # redispatches to its own fail-loud tag, distinct from the ambiguous-call
    # pause (outcome known: it failed).
    with pytest.raises(SpecialistDispatchError) as second:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert second.value.tag == "workbook-review.enrichment-prior-failure"
    # A journal at bare call_in_progress (no recorded failure) stays the
    # ambiguous hard pause.
    del journal["provider_failure"]
    (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).write_text(
        json.dumps(journal) + "\n", "utf-8"
    )
    with pytest.raises(SpecialistDispatchError) as third:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert third.value.tag == "workbook-review.enrichment-call-ambiguous"


def test_orphan_pre_dispatch_temporary_is_recovered(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    temporary = run_dir / (DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME + ".tmp")
    temporary.write_text(
        json.dumps(
            {
                "schema_version": "workbook-deep-dive-enrichment-call.v1",
                "state": "call_in_progress",
            }
        )
        + "\n",
        "utf-8",
    )
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert not temporary.exists()
    assert output["deep_dive_enrichment"]["status"] == "enriched"


def test_completed_temporary_rolls_forward_over_in_progress_target(
    tmp_path: Path,
) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    journal_path = run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME
    completed = json.loads(journal_path.read_text("utf-8"))
    in_progress = {
        key: completed[key]
        for key in (
            "schema_version",
            "idempotency_key",
            "request_digest",
            "pool_packet_digest",
            "skeleton_authority_digest",
            "skeleton_candidate_digest",
            "model_config_digest",
            "request",
        )
    }
    in_progress["state"] = "call_in_progress"
    journal_path.write_text(json.dumps(in_progress) + "\n", "utf-8")
    (run_dir / (DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME + ".tmp")).write_text(
        json.dumps(completed) + "\n", "utf-8"
    )
    replayed = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert writer.calls_made == 1
    assert replayed == output
    assert json.loads(journal_path.read_text("utf-8"))["state"] == "completed"


def test_degraded_honest_decline_is_first_class_live_outcome(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(
        lambda _request: degraded_candidate("deep_dive_enrichment_pool_unused")
    )
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    result = output["deep_dive_enrichment"]
    assert result["status"] == "degraded"
    assert result["known_losses"] == ["deep_dive_enrichment_pool_unused"]
    assert result["gate"]["disposition"] == "degraded_pool_unused"
    assert result["gate"]["unused_citation_ids"] == ["ask-a-cite-001"]


def test_live_writer_missing_fails_init_tag(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(
            run_dir=run_dir,
            trial_id="trial-x",
            runtime_context=_context(run_dir, mode="live", writer=None),
        )
    assert caught.value.tag == "workbook-review.enrichment-writer-init-failed"


# ---------------------------------------------------------------------------
# Band-level reconciliation (upgrade / no-op / split-brain / context)
# ---------------------------------------------------------------------------


def _band_envelope(*contributions: SpecialistContribution) -> ProductionEnvelope:
    envelope = ProductionEnvelope(trial_id=uuid4())
    for contribution in contributions:
        envelope.add_contribution(contribution)
    return envelope


def _legacy_stub_contribution() -> SpecialistContribution:
    return SpecialistContribution.from_output(
        specialist_id="workbook_review_stub",
        node_id="07W.3",
        output={
            "stub_status": "not_yet_wired",
            "review_payload": {},
            "known_losses": ["semantic_writers_not_yet_wired"],
        },
        model_used="deterministic-workbook-band-stub",
    )


def test_legacy_stub_upgrades_at_exact_coordinate(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    envelope = _band_envelope(_legacy_stub_contribution())
    updated = workbook_wiring.run_workbook_band_node(
        node_id="07W.3",
        production_envelope=envelope,
        runtime_context=_context(run_dir),
    )
    assert updated.get_contribution("workbook_review_stub", node_id="07W.3") is None
    activated = updated.get_contribution("workbook_review", node_id="07W.3")
    assert activated is not None
    assert activated.output["schema_version"] == "workbook-review-contribution.v1"
    assert activated.model_used == "workbook-review-offline"


def test_offline_reentry_is_exact_noop(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    first = workbook_wiring.run_workbook_band_node(
        node_id="07W.3",
        production_envelope=_band_envelope(),
        runtime_context=_context(run_dir),
    )
    second = workbook_wiring.run_workbook_band_node(
        node_id="07W.3",
        production_envelope=first,
        runtime_context=_context(run_dir),
    )
    assert second is first


def test_completed_live_contribution_without_journal_is_split_brain(
    tmp_path: Path,
) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).unlink()
    envelope = _band_envelope(
        SpecialistContribution.from_output(
            specialist_id="workbook_review",
            node_id="07W.3",
            output=output,
            model_used="gpt-5",
        )
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.3",
            production_envelope=envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-review.enrichment-split-brain"


def test_completed_live_contribution_reconciles_and_never_recalls(
    tmp_path: Path,
) -> None:
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    first = workbook_wiring.run_workbook_band_node(
        node_id="07W.3",
        production_envelope=_band_envelope(),
        runtime_context=context,
    )
    assert writer.calls_made == 1
    activated = first.get_contribution("workbook_review", node_id="07W.3")
    assert activated is not None
    assert activated.output["deep_dive_enrichment"]["status"] == "enriched"
    second = workbook_wiring.run_workbook_band_node(
        node_id="07W.3",
        production_envelope=first,
        runtime_context=context,
    )
    assert second is first  # completed output reconciles; never recalled
    assert writer.calls_made == 1


def test_coordinate_collision_fails_closed(tmp_path: Path) -> None:
    run_dir = _prepare_run(tmp_path)
    envelope = _band_envelope(
        _legacy_stub_contribution(),
        SpecialistContribution.from_output(
            specialist_id="workbook_review",
            node_id="07W.3",
            output=json.loads(
                build_workbook_review_contribution(None, None).model_dump_json()
            ),
            model_used="workbook-review-offline",
        ),
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.3",
            production_envelope=envelope,
            runtime_context=_context(run_dir),
        )
    assert caught.value.tag == "workbook-review.coordinate-collision"


def test_default_factory_requires_runtime_context() -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.3", production_envelope=_band_envelope()
        )
    assert caught.value.tag == "workbook-review.runtime-context-missing"


# ---------------------------------------------------------------------------
# Remediation pins (orchestrator-triaged set, 2026-07-15)
# ---------------------------------------------------------------------------


def _prepare_empty_pool_run(tmp_path: Path) -> Path:
    install_brief(tmp_path)
    install_run_json(tmp_path, ask_a_output=None)
    return tmp_path


def test_r1_empty_pool_live_mode_makes_zero_writer_calls_and_journals_decline(
    tmp_path: Path,
) -> None:
    """R1: an empty pool NEVER dispatches the paid writer — the row-d degraded
    contribution is built deterministically and journaled zero-call under its
    own replayable state."""
    from app.marcus.orchestrator.deep_dive_enrichment_wiring import (
        JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH,
    )

    run_dir = _prepare_empty_pool_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert writer.calls_made == 0  # no paid call
    result = output["deep_dive_enrichment"]
    assert result["status"] == "degraded"
    assert result["known_losses"] == ["deep_dive_enrichment_pool_empty"]
    assert result["gate"]["status"] == "pass"
    assert result["gate"]["disposition"] == "degraded_pool_empty"
    receipt = output["deep_dive_enrichment_receipt"]
    assert (receipt["mode"], receipt["calls"]) == ("live", 0)
    journal = json.loads(
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal["state"] == JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH
    assert journal["dispatch_declined_reason"] == "deep_dive_enrichment_pool_empty"
    # Distinct + replayable: re-entry replays the decline with zero calls.
    replayed = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    assert writer.calls_made == 0
    assert replayed == output


def test_r1_system_prompt_names_both_decline_losses_keyed_to_pool_state() -> None:
    from app.marcus.orchestrator.workbook_prework_writers import (
        LiveDeepDiveEnrichmentWriter,
    )

    writer = LiveDeepDiveEnrichmentWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=None)
    )
    nonempty = make_request()
    prompt = writer._system_prompt(nonempty)
    assert "deep_dive_enrichment_pool_unused" in prompt
    assert "known_losses=['deep_dive_enrichment_pool_unused']" in prompt
    empty = make_request(pool_rows=(), pool_status="empty", pool_scope_digest=None)
    prompt = writer._system_prompt(empty)
    assert "known_losses=['deep_dive_enrichment_pool_empty']" in prompt
    assert "'deep_dive_enrichment_pool_unused'" not in prompt


def test_r2_live_unavailable_candidate_fails_loud_not_journaled_completed(
    tmp_path: Path,
) -> None:
    """R2: a SUCCESSFUL live call returning a writer-unavailable candidate is
    dishonest — fail loud with the node-scoped tag; no completed journal."""
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(
        lambda _request: degraded_candidate("deep_dive_enrichment_writer_unavailable")
    )
    context = _context(run_dir, mode="live", writer=writer)
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert caught.value.tag == "workbook-review.enrichment-writer-output-invalid"
    assert "unavailable_shape_dishonest" in str(caught.value)
    journal = json.loads(
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal["state"] == "call_in_progress"  # never completed


def test_r4_offline_stub_never_shadows_an_existing_journal(tmp_path: Path) -> None:
    """R4: journal present (ANY state) + offline mode -> fail-loud, never the
    deterministic stub (paid evidence must never be shadowed)."""
    run_dir = _prepare_run(tmp_path)
    for state in ("call_in_progress", "completed", "completed_without_dispatch"):
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).write_text(
            json.dumps(
                {
                    "schema_version": "workbook-deep-dive-enrichment-call.v1",
                    "state": state,
                }
            )
            + "\n",
            "utf-8",
        )
        with pytest.raises(SpecialistDispatchError) as caught:
            run_workbook_review(
                run_dir=run_dir, trial_id="trial-x", runtime_context=_context(run_dir)
            )
        assert caught.value.tag == "workbook-review.enrichment-reconciliation-failed"


def test_r5_not_authored_skeleton_routes_to_typed_state_naming_loss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R5: typed exception routing — a present-but-DEGRADED skeleton yields the
    state-naming loss, never the 'no skeleton' note; a MISSING skeleton keeps
    the skeleton_unavailable loss."""
    from app.marcus.lesson_plan.deep_dive_enrichment import (
        DeepDiveSkeletonMissingError,
        DeepDiveSkeletonNotAuthoredError,
    )
    from app.marcus.orchestrator import deep_dive_enrichment_wiring

    run_dir = _prepare_run(tmp_path)

    def _degraded_skeleton(_run_dir):
        raise DeepDiveSkeletonNotAuthoredError("degraded")

    monkeypatch.setattr(
        deep_dive_enrichment_wiring,
        "build_deep_dive_enrichment_request",
        _degraded_skeleton,
    )
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=_context(run_dir)
    )
    assert output["deep_dive_enrichment"] is None
    assert output["known_losses"][0] == (
        "deep_dive_enrichment_skeleton_not_authored_degraded"
    )

    def _missing_skeleton(_run_dir):
        raise DeepDiveSkeletonMissingError(
            "workbook brief carries no Deep Dive skeleton"
        )

    monkeypatch.setattr(
        deep_dive_enrichment_wiring,
        "build_deep_dive_enrichment_request",
        _missing_skeleton,
    )
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=_context(run_dir)
    )
    assert output["known_losses"][0] == "deep_dive_enrichment_skeleton_unavailable"


def test_r10_provider_parse_failure_journal_preserves_bounded_raw_text(
    tmp_path: Path,
) -> None:
    """R10: on provider parse failure the failure journal persists the raw
    provider text (bounded) — never an empty evidence mapping."""
    from app.marcus.orchestrator.deep_dive_enrichment_wiring import (
        RAW_PROVIDER_TEXT_BOUND,
    )
    from app.marcus.orchestrator.workbook_prework_writers import (
        DeepDiveEnrichmentProviderOutputError,
    )

    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    huge_text = "NOT-JSON " * 10_000

    def _parse_boom(_request):
        writer.last_raw_provider_text = huge_text
        raise DeepDiveEnrichmentProviderOutputError("structured writer parse failed")

    writer._factory = _parse_boom
    context = _context(run_dir, mode="live", writer=writer)
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert caught.value.tag == "workbook-review.enrichment-writer-output-invalid"
    journal = json.loads(
        (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal["provider_failure"]["type"] == (
        "DeepDiveEnrichmentProviderOutputError"
    )
    assert journal["raw_provider_text"] == huge_text[:RAW_PROVIDER_TEXT_BOUND]
    assert len(journal["raw_provider_text"]) == RAW_PROVIDER_TEXT_BOUND
    # No raw payload/text captured at all still records explicit evidence.
    run_dir2 = tmp_path / "no-capture"
    run_dir2.mkdir()
    install_brief(run_dir2)
    install_run_json(run_dir2, ask_a_output=ask_a_output_payload())
    writer2 = _FakeEnrichmentWriter(
        lambda _request: (_ for _ in ()).throw(RuntimeError("socket dropped"))
    )
    with pytest.raises(SpecialistDispatchError):
        run_workbook_review(
            run_dir=run_dir2,
            trial_id="trial-x",
            runtime_context=_context(run_dir2, mode="live", writer=writer2),
        )
    journal2 = json.loads(
        (run_dir2 / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
    )
    assert journal2["raw_provider_text"].startswith("<no raw provider payload")


def test_r10_live_writer_captures_raw_text_on_structured_parse_failure() -> None:
    from app.marcus.orchestrator.workbook_prework_writers import (
        DeepDiveEnrichmentProviderOutputError,
        LiveDeepDiveEnrichmentWriter,
    )

    response = {
        "parsed": None,
        "parsing_error": ValueError("truncated JSON"),
        "raw": SimpleNamespace(content="RAW PROVIDER TEXT", response_metadata={}),
    }
    handle = SimpleNamespace(
        chat=SimpleNamespace(
            with_structured_output=lambda schema, include_raw=True: SimpleNamespace(
                invoke=lambda _messages: response
            )
        )
    )
    writer = LiveDeepDiveEnrichmentWriter(chat_factory=lambda *a, **k: handle)
    with pytest.raises(DeepDiveEnrichmentProviderOutputError, match="parse failed"):
        writer(make_request())
    assert writer.last_raw_provider_text == "RAW PROVIDER TEXT"
    assert writer.last_raw_provider_payload is None


def test_r13_legacy_upgrade_validates_payload_before_deleting_stub(
    tmp_path: Path,
) -> None:
    """R13: a garbage upgrade payload never destroys the legacy stub row."""

    def _garbage(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
        return {"schema_version": "garbage", "anything": True}

    envelope = _band_envelope(_legacy_stub_contribution())
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.3",
            production_envelope=envelope,
            factories={"07W.3": _garbage},
        )
    assert caught.value.tag == "workbook-review.output-invalid"
    # The recorded legacy row survives the refused upgrade.
    assert (
        envelope.get_contribution("workbook_review_stub", node_id="07W.3") is not None
    )


def test_r14_calls_one_contribution_with_non_completed_journal_is_split_brain(
    tmp_path: Path,
) -> None:
    """R14: bare journal EXISTENCE is not evidence — the prior-receipt guard
    requires state == 'completed'."""
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    context = _context(run_dir, mode="live", writer=writer)
    output = run_workbook_review(
        run_dir=run_dir, trial_id="trial-x", runtime_context=context
    )
    journal_path = run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME
    journal = json.loads(journal_path.read_text("utf-8"))
    journal["state"] = "call_in_progress"
    journal_path.write_text(json.dumps(journal) + "\n", "utf-8")
    envelope = _band_envelope(
        SpecialistContribution.from_output(
            specialist_id="workbook_review",
            node_id="07W.3",
            output=output,
            model_used="gpt-5",
        )
    )
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.3",
            production_envelope=envelope,
            runtime_context=context,
        )
    assert caught.value.tag == "workbook-review.enrichment-split-brain"


def test_r18_live_writer_without_model_config_digest_fails_loud(
    tmp_path: Path,
) -> None:
    """R18: the live journal identity digest must come from the writer — no
    silent all-zeros fallback in live mode."""
    run_dir = _prepare_run(tmp_path)
    writer = _FakeEnrichmentWriter(lambda request: enriched_candidate(request))
    del writer.model_config_digest
    context = _context(run_dir, mode="live", writer=writer)
    with pytest.raises(SpecialistDispatchError) as caught:
        run_workbook_review(run_dir=run_dir, trial_id="trial-x", runtime_context=context)
    assert caught.value.tag == "workbook-review.enrichment-writer-identity-missing"
    assert writer.calls_made == 0
    assert not (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).exists()


def test_runtime_context_for_run_injects_live_enrichment_writer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.marcus.lesson_plan.prework_artifact import write_runtime_context
    from app.marcus.orchestrator import workbook_prework_writers

    write_runtime_context(
        WorkbookBriefRuntimeContext(
            run_dir=tmp_path,
            course_source_root=COURSE_SOURCE_ROOT,
            encounter_mode="recorded",
            context_origin="new_start",
            writer_execution_mode="live",
        )
    )
    sentinel = object()
    monkeypatch.setattr(
        workbook_prework_writers,
        "LiveDeepDiveEnrichmentWriter",
        lambda: sentinel,
    )
    context = workbook_wiring.runtime_context_for_run(tmp_path, node_id="07W.3")
    assert context.deep_dive_enrichment_writer is sentinel
    # Other nodes do NOT construct the enrichment writer.
    context = workbook_wiring.runtime_context_for_run(tmp_path, node_id="07W.2")
    assert context.deep_dive_enrichment_writer is None
