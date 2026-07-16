"""Hermetic tests for the exactly-once Ask-B wiring at ``07W.4`` (38.2 AC 1-5).

Dispatch is injected ONLY at the owned ``ask_b_research_wiring`` seam; no
network. Covers the deterministic I/O matrix rows 1-3 and 10-17 plus the
journal failure injections mirrored from the 38-1 discipline.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.ask_b_hot_topics import canonical_digest
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import (
    AskBHotTopicsDemandV1,
    ResearchDemandShapeError,
)
from app.marcus.orchestrator import ask_b_research_wiring as wiring
from app.specialists.dispatch_errors import SpecialistDispatchError


def _demand(*, status: str = "ready", scene: bool = True) -> AskBHotTopicsDemandV1:
    if status == "ready":
        values = dict(
            status="ready",
            workbook_brief_payload_digest="sha256:" + "a" * 64,
            abilities=(
                DeepDiveAbilityInput(
                    ability_id="lo-1", text="Distinguish workflow symptoms from causes"
                ),
            ),
            scene_digest=("sha256:" + "b" * 64) if scene else None,
            scene_text="A clinic drowns in workflow friction." if scene else None,
            known_losses=() if scene else ("scene_identity_absent",),
        )
    else:
        values = dict(
            status="unavailable",
            workbook_brief_payload_digest=None,
            abilities=(),
            scene_digest=None,
            scene_text=None,
            known_losses=("workbook_brief_absent",),
        )
    raw = {
        "schema_version": "ask-b-hot-topics-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        **values,
    }
    raw["demand_digest"] = canonical_digest(raw)
    return AskBHotTopicsDemandV1.model_validate(raw, strict=True)


def _result(*, body: str | None = None) -> SimpleNamespace:
    row = SimpleNamespace(
        provider="scite",
        source_id="10.1000/workflow-trends",
        title="Workflow symptom trends",
        body=body
        if body is not None
        else "Emerging workflow symptoms research distinguishes causes in clinics.",
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
    """Matrix rows 2 + 10: typed retryables; zero dispatch; no journal."""
    monkeypatch.setattr(
        wiring, "resolve_hot_topics_demand", lambda _: _demand(status="unavailable")
    )
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
    )
    assert output.disposition == "retryable_demand_not_ready"
    assert output.known_losses == ("ask_b_demand_not_ready",)
    assert calls == 0
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()
    assert not (tmp_path / wiring.LOCK_FILENAME).exists()

    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=False, dispatch=dispatch
    )
    assert output.disposition == "retryable_dispatch_disabled"
    assert output.known_losses == ("ask_b_dispatch_disabled",)
    assert calls == 0
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()


def test_credentials_absent_is_typed_zero_call(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 11: no injected dispatch + no creds → typed retryable."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    monkeypatch.setattr(wiring, "_credentials_present", lambda: False)
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True
    )
    assert output.disposition == "retryable_credentials_unavailable"
    assert output.known_losses == ("ask_b_credentials_unavailable",)
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()
    assert not (tmp_path / wiring.LOCK_FILENAME).exists()


def test_one_dispatch_completed_journal_and_zero_call_replay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 1: exactly one dispatcher invocation; completed journal;
    replay recomputes the exact output with zero calls."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    calls = 0

    def dispatch(intent: object) -> object:
        nonlocal calls
        calls += 1
        assert "[lo-1] Distinguish workflow symptoms from causes" in intent.intent
        assert "scene: A clinic drowns in workflow friction." in intent.intent
        return _result()

    first = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
    )
    assert first.disposition == "completed_ready"
    assert first.dispatcher_invocations == 1
    assert first.research_entries[0].citation_id == "ask-b-cite-001"
    assert first.research_entries[0].supports_ability_ids == ("lo-1",)
    assert calls == 1
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["schema_version"] == "ask-b-hot-topics-call.v1"
    assert journal["state"] == "completed"

    def raising(_: object) -> object:
        raise AssertionError("replay must make zero dispatcher invocations")

    second = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=raising
    )
    assert second == first
    assert calls == 1


def test_completed_empty_is_honest_bounded_and_terminal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 3: zero usable rows → completed_empty with typed losses;
    scope still bound via intake; terminal — never recalled."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    result = _result()
    result.rows[0].body = "   "  # evidence-invalid row
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )
    assert output.disposition == "completed_empty"
    assert output.known_losses == ("ask_b_row_evidence_invalid:0",)
    assert output.research_entries == ()
    assert output.research_intake is not None
    assert output.research_intake.uncovered_ability_ids == ("lo-1",)

    def raising(_: object) -> object:
        raise AssertionError("honest-empty is terminal; no recall")

    replay = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=raising
    )
    assert replay == output


def test_unassociated_rows_are_indexed_losses_never_fabricated(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    result = _result(body="Quantum chromodynamics lattice results.")
    result.rows[0].title = "Unrelated physics"
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )
    assert output.disposition == "completed_empty"
    assert output.known_losses == ("ask_b_row_ability_unassociated:0",)


def test_scene_absent_scope_loss_leads_completed_losses(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Ready-with-loss demand (W-3): scene loss leads the packet losses."""
    monkeypatch.setattr(
        wiring, "resolve_hot_topics_demand", lambda _: _demand(scene=False)
    )
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    assert output.disposition == "completed_degraded"
    assert output.known_losses[0] == "scene_identity_absent"
    assert output.research_entries  # usable rows still minted


def test_corrupt_demand_is_demand_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 15: corrupt/forged demand → ask-b.demand-invalid; zero dispatch."""

    def broken(_: Path) -> AskBHotTopicsDemandV1:
        raise ResearchDemandShapeError("forged authority")

    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", broken)
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert exc.value.tag == "ask-b.demand-invalid"
    assert calls == 0


def test_scope_overflow_fails_before_claim_or_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 16: over-limit scope fails BEFORE dispatch; never truncated."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    monkeypatch.setenv("MARCUS_ASK_B_QUERY_MAX_CHARS", "10")
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert exc.value.tag == "ask-b.scope-overflow"
    assert calls == 0
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()
    assert not (tmp_path / wiring.LOCK_FILENAME).exists()


def test_call_in_progress_journal_is_hard_pause(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 12: an in-progress journal is ambiguous; zero recall."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    (tmp_path / wiring.JOURNAL_FILENAME).write_text(
        json.dumps(
            {
                "schema_version": "ask-b-hot-topics-call.v1",
                "state": "call_in_progress",
                "idempotency_key": "sha256:" + "9" * 64,
                "scope": {},
            }
        ),
        encoding="utf-8",
    )
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert exc.value.tag == "ask-b.call-ambiguous"
    assert calls == 0


def test_lock_without_journal_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    (tmp_path / wiring.LOCK_FILENAME).write_text("held", encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.call-ambiguous"


def test_provider_exception_preserves_ambiguous_claim(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())

    def dispatch(_: object) -> object:
        raise RuntimeError("provider boom")

    with pytest.raises(SpecialistDispatchError) as first:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert first.value.tag == "ask-b.provider-execution-failed"
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["state"] == "call_in_progress"
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-b.call-ambiguous"


def test_barrier_two_workers_exactly_one_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 17: exclusive claim — the losing worker makes ZERO calls."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
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
                wiring.run_ask_b_research(
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
    assert any(getattr(item, "tag", None) == "ask-b.call-ambiguous" for item in outcomes)
    assert any(
        getattr(item, "disposition", None) == "completed_ready" for item in outcomes
    )


def test_precall_write_failure_preserves_lock_and_reentry_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    real = wiring._atomic_json
    monkeypatch.setattr(
        wiring, "_atomic_json", lambda *_: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.dispatch-init-failed"
    assert (tmp_path / wiring.LOCK_FILENAME).is_file()
    monkeypatch.setattr(wiring, "_atomic_json", real)
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-b.call-ambiguous"


def test_completed_write_failure_leaves_in_progress_and_reentry_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
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
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.persistence-failed"
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["state"] == "call_in_progress"
    with pytest.raises(SpecialistDispatchError) as replay:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert replay.value.tag == "ask-b.call-ambiguous"


def test_temp_collision_fails_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    (tmp_path / (wiring.JOURNAL_FILENAME + ".tmp")).write_text(
        "collision", encoding="utf-8"
    )
    calls = 0

    def dispatch(_: object) -> object:
        nonlocal calls
        calls += 1
        return _result()

    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=dispatch
        )
    assert exc.value.tag == "ask-b.dispatch-init-failed"
    assert calls == 0


def test_completed_raw_body_mutation_fails_replay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 8 (negative witness): mutated raw journal body REJECTS."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    path = tmp_path / wiring.JOURNAL_FILENAME
    journal = json.loads(path.read_text("utf-8"))
    journal["raw_rows"][0]["body"] += " mutation"
    path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.reconciliation-failed"


def test_forged_journal_schema_and_state_fail_reconciliation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Matrix row 8 (negative witness): forged schema/state REJECTS."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    path = tmp_path / wiring.JOURNAL_FILENAME
    path.write_text(
        json.dumps({"schema_version": "forged.v1", "state": "completed"}),
        encoding="utf-8",
    )
    with pytest.raises(SpecialistDispatchError) as forged:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert forged.value.tag == "ask-b.reconciliation-failed"

    path.unlink()
    wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    journal = json.loads(path.read_text("utf-8"))
    journal["state"] = "unknown"
    path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as invalid:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert invalid.value.tag == "ask-b.reconciliation-failed"


def test_journal_idempotency_binds_trial_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial-a", dispatch_live=True, dispatch=lambda _: _result()
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path,
            trial_id="trial-b",
            dispatch_live=True,
            dispatch=lambda _: _result(),
        )
    assert exc.value.tag == "ask-b.reconciliation-failed"


def test_ask_b_journal_and_lock_are_own_coordinates() -> None:
    """Own journal/lock/idempotency — never the Ask-A or 04.55 coordinates."""
    from app.marcus.orchestrator import ask_a_research_wiring

    assert wiring.JOURNAL_FILENAME == "ask-b-hot-topics-call.v1.json"
    assert wiring.LOCK_FILENAME == "ask-b-hot-topics-call.v1.lock"
    assert wiring.JOURNAL_FILENAME != ask_a_research_wiring.JOURNAL_FILENAME
    assert wiring.LOCK_FILENAME != ask_a_research_wiring.LOCK_FILENAME
