from __future__ import annotations

import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.ask_a_enrichment import canonical_digest
from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker, DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import AskAResearchDemandV1
from app.marcus.orchestrator import ask_a_research_wiring as wiring
from app.specialists.dispatch_errors import SpecialistDispatchError


def _demand(*, status: str = "ready") -> AskAResearchDemandV1:
    if status == "ready":
        values = dict(
            status="ready",
            workbook_brief_payload_digest="sha256:" + "a" * 64,
            skeleton_authority_digest="sha256:" + "b" * 64,
            skeleton_candidate_digest="sha256:" + "c" * 64,
            abilities=(DeepDiveAbilityInput(ability_id="lo-1", text="Explain model drift risk"),),
            bold_terms=(BoldTermMarker(term="Model Drift"),),
            source_claim_refs=("claim-1",),
            known_losses=(),
        )
    else:
        values = dict(
            status="unavailable",
            workbook_brief_payload_digest=None,
            skeleton_authority_digest=None,
            skeleton_candidate_digest=None,
            abilities=(),
            bold_terms=(),
            source_claim_refs=(),
            known_losses=("workbook_brief_absent",),
        )
    raw = {
        "schema_version": "ask-a-research-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        **values,
    }
    raw["demand_digest"] = canonical_digest(raw)
    return AskAResearchDemandV1.model_validate(raw, strict=True)


def _result() -> SimpleNamespace:
    row = SimpleNamespace(
        provider="scite",
        source_id="10.1000/model-drift",
        title="Model Drift review",
        body="Model Drift evidence explains model drift risk in clinical deployment.",
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


def test_nonready_and_disabled_are_typed_zero_call(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        wiring, "resolve_enrichment_demand", lambda _: _demand(status="unavailable")
    )
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    output = wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
    )
    assert output.disposition == "retryable_demand_not_ready"
    assert calls == 0
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()

    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    output = wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=False, dispatch=dispatch
    )
    assert output.disposition == "retryable_dispatch_disabled"
    assert calls == 0


def test_one_dispatch_completed_journal_and_zero_call_replay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    calls = 0

    def dispatch(intent: object) -> object:
        nonlocal calls
        calls += 1
        assert "Model Drift" in intent.intent
        return _result()

    first = wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
    )
    assert first.disposition == "completed_ready"
    assert calls == 1
    assert first.research_entries[0].evidence_excerpt.startswith("Model Drift")
    second = wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
    )
    assert second == first
    assert calls == 1


def test_duplicate_loss_uses_original_raw_row_index(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    result = _result()
    duplicate = SimpleNamespace(**vars(result.rows[0]))
    invalid = SimpleNamespace(**{**vars(result.rows[0]), "source_id": ""})
    result.rows = [invalid, result.rows[0], duplicate]

    output = wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )

    assert output.disposition == "completed_degraded"
    assert output.known_losses == (
        "ask_a_row_source_invalid:0",
        "ask_a_row_duplicate:2",
    )
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["normalization_records"][2] == {
        "index": 2,
        "disposition": "duplicate",
        "source_ref": "retrieval:scite:10.1000/model-drift",
    }


def test_provider_exception_preserves_ambiguous_claim(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())

    def dispatch(_: object) -> object:
        raise RuntimeError("provider boom")

    with pytest.raises(SpecialistDispatchError) as first:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert first.value.tag == "ask-a.provider-execution-failed"
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-a.call-ambiguous"


def test_barrier_two_workers_exactly_one_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    entered = threading.Event()
    release = threading.Event()
    calls = 0
    outcomes: list[object] = []

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(5)
        return _result()

    def worker() -> None:
        try:
            outcomes.append(
                wiring.run_ask_a_research(
                    run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
                )
            )
        except Exception as exc:
            outcomes.append(exc)

    first = threading.Thread(target=worker)
    first.start()
    assert entered.wait(5)
    second = threading.Thread(target=worker)
    second.start()
    second.join(5)
    release.set()
    first.join(5)
    assert calls == 1
    assert any(getattr(item, "tag", None) == "ask-a.call-ambiguous" for item in outcomes)
    assert any(getattr(item, "disposition", None) == "completed_ready" for item in outcomes)


def test_scope_overflow_fails_before_claim_or_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    monkeypatch.setenv("MARCUS_ASK_A_QUERY_MAX_CHARS", "10")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-a.scope-overflow"
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()


def test_precall_write_failure_preserves_lock_and_reentry_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    real = wiring._atomic_json
    monkeypatch.setattr(wiring, "_atomic_json", lambda *_: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-a.dispatch-init-failed"
    assert (tmp_path / wiring.LOCK_FILENAME).is_file()
    monkeypatch.setattr(wiring, "_atomic_json", real)
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-a.call-ambiguous"


def test_completed_write_failure_leaves_in_progress_and_reentry_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    real = wiring._atomic_json
    writes = 0

    def fail_second(path: Path, payload: dict) -> None:
        nonlocal writes
        writes += 1
        if writes == 2:
            raise OSError("completed write failed")
        real(path, payload)

    monkeypatch.setattr(wiring, "_atomic_json", fail_second)
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-a.persistence-failed"
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["state"] == "call_in_progress"
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-a.call-ambiguous"


def test_temp_collision_fails_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    (tmp_path / (wiring.JOURNAL_FILENAME + ".tmp")).write_text("collision", encoding="utf-8")
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert exc.value.tag == "ask-a.dispatch-init-failed"
    assert calls == 0


def test_completed_raw_body_mutation_fails_replay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    wiring.run_ask_a_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    path = tmp_path / wiring.JOURNAL_FILENAME
    journal = json.loads(path.read_text("utf-8"))
    journal["raw_rows"][0]["body"] += " mutation"
    path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_a_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-a.reconciliation-failed"


def test_invalid_journal_state_and_effective_query_limit_drift_fail_reconciliation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_enrichment_demand", lambda _: _demand())
    wiring.run_ask_a_research(
        run_dir=tmp_path,
        trial_id="trial",
        dispatch_live=True,
        provider_config_fingerprint="sha256:" + "d" * 64,
        dispatch=lambda _: _result(),
    )
    path = tmp_path / wiring.JOURNAL_FILENAME
    journal = json.loads(path.read_text("utf-8"))
    journal["state"] = "unknown"
    path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as invalid:
        wiring.run_ask_a_research(
            run_dir=tmp_path,
            trial_id="trial",
            dispatch_live=True,
            provider_config_fingerprint="sha256:" + "d" * 64,
            dispatch=lambda _: _result(),
        )
    assert invalid.value.tag == "ask-a.reconciliation-failed"

    journal["state"] = "completed"
    path.write_text(json.dumps(journal), encoding="utf-8")
    monkeypatch.setenv("MARCUS_ASK_A_QUERY_MAX_CHARS", "8191")
    with pytest.raises(SpecialistDispatchError) as drift:
        wiring.run_ask_a_research(
            run_dir=tmp_path,
            trial_id="trial",
            dispatch_live=True,
            provider_config_fingerprint="sha256:" + "d" * 64,
            dispatch=lambda _: _result(),
        )
    assert drift.value.tag == "ask-a.reconciliation-failed"
