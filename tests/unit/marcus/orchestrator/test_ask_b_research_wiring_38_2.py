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


# ---------------------------------------------------------------------------
# 38-2 T4 remediation pins (review findings R1, R7, R8, R12, R13)
# ---------------------------------------------------------------------------


def test_intent_init_failure_is_typed_and_never_strands_call_in_progress(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1a (B1/E4/E5/E2, live-repro'd): ALL fallible construction happens
    BEFORE any claim/journal write — an intent-init failure is typed
    ``ask-b.dispatch-init-failed``, leaves NO lock and NO ``call_in_progress``
    journal, and the coordinate stays dispatchable on re-entry."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    monkeypatch.setattr(
        wiring, "_build_intent", lambda _: (_ for _ in ()).throw(RuntimeError("init boom"))
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.dispatch-init-failed"
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()  # never stranded
    assert not (tmp_path / wiring.LOCK_FILENAME).exists()
    # Re-entry after the init defect is fixed dispatches cleanly.
    monkeypatch.setattr(wiring, "_build_intent", lambda scope: scope.query)
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    assert output.disposition == "completed_ready"


def test_scope_build_failure_is_typed_dispatch_init_failed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1a (B1): a scope-construction failure is typed — never a raw
    ValueError escaping the seam, never a stranded claim."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    monkeypatch.setattr(
        wiring, "build_scope", lambda *a, **k: (_ for _ in ()).throw(ValueError("bad scope"))
    )
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.dispatch-init-failed"
    assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()
    assert not (tmp_path / wiring.LOCK_FILENAME).exists()


def test_blank_after_window_excerpt_is_indexed_evidence_loss(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1b (E4): a body whose first 2000 chars are whitespace passes the
    raw-body check but yields a blank stored excerpt — an indexed per-row
    loss, never a post-spend ``ask-b.output-invalid``."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    result = _result(body=" " * 2000 + "text past the stored window")
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )
    assert output.disposition == "completed_empty"
    assert output.known_losses == ("ask_b_row_evidence_invalid:0",)


def test_control_char_provider_or_source_id_is_indexed_source_loss(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1b (B1, live-repro'd poisoning): provider/source_id carrying ANY
    line-control character (or strip-inequality) is an indexed per-row loss
    aligned with the entry validator — money spent never escalates to
    output-invalid."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    poisoned = _result()
    poisoned.rows[0].provider = "sci\nte"
    good = _result()
    good.rows[0].source_id = " 10.1000/leading-space"
    for run_dir, result in ((tmp_path / "a", poisoned), (tmp_path / "b", good)):
        run_dir.mkdir()
        output = wiring.run_ask_b_research(
            run_dir=run_dir,
            trial_id="trial",
            dispatch_live=True,
            dispatch=lambda _, r=result: r,
        )
        assert output.disposition == "completed_empty"
        assert output.known_losses == ("ask_b_row_source_invalid:0",)


def test_row_entry_validator_failure_is_indexed_loss_after_spend(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1b (B1/E2): per-row loss coverage is EXHAUSTIVE over entry-validator
    failures — a validator rejection during entry construction (simulated
    upstream-helper drift) becomes ``ask_b_row_entry_invalid:{index}`` and the
    mint continues; it never escalates to ``ask-b.output-invalid``."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    row_ok = _result().rows[0]
    row_bad = _result().rows[0]
    row_bad.source_id = "10.1000/second-row"
    result = SimpleNamespace(
        provider="scite",
        rows=[row_ok, row_bad],
        acceptance_met=True,
        iterations_used=1,
        refinement_log=[],
    )
    real_hash = wiring.compute_source_hash

    def drifting_hash(row: object) -> str:
        if getattr(row, "source_id", "") == "10.1000/second-row":
            return "not-a-digest"  # entry validator rejects this shape
        return real_hash(row)

    monkeypatch.setattr(wiring, "compute_source_hash", drifting_hash)
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )
    assert output.disposition == "completed_degraded"
    assert output.known_losses == ("ask_b_row_entry_invalid:1",)
    assert len(output.research_entries) == 1  # the clean row still minted


def test_thousand_row_mint_keeps_contiguous_natural_width_citations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1c (E5): >999 rows must not break the citation mint — the format
    widens naturally at row 1000 and the entry regex admits it."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    template = _result().rows[0]
    rows = []
    for index in range(1000):
        row = SimpleNamespace(**vars(template))
        row.source_id = f"10.1000/workflow-{index:04d}"
        rows.append(row)
    result = SimpleNamespace(
        provider="scite",
        rows=rows,
        acceptance_met=True,
        iterations_used=1,
        refinement_log=[],
    )
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: result
    )
    assert output.disposition == "completed_ready"
    assert len(output.research_entries) == 1000
    assert output.research_entries[998].citation_id == "ask-b-cite-999"
    assert output.research_entries[999].citation_id == "ask-b-cite-1000"


def test_journal_unicode_decode_error_is_reconciliation_failed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R1d (E1): a journal that is not valid UTF-8 routes to the typed
    ``ask-b.reconciliation-failed`` — never an uncaught UnicodeDecodeError."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    (tmp_path / wiring.JOURNAL_FILENAME).write_bytes(b"\xff\xfe{ not utf-8 }")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.reconciliation-failed"


def test_query_limit_is_operational_never_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R7 (B3): the query limit is enforced pre-dispatch ONLY and never
    enters scope/idempotency/fingerprint identity — a completed journal
    replays green after the env var changes (even to garbage), and the limit
    VALUE is recorded in the journal for observability."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    monkeypatch.delenv("MARCUS_ASK_B_QUERY_MAX_CHARS", raising=False)
    first = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    assert first.disposition == "completed_ready"
    journal = json.loads((tmp_path / wiring.JOURNAL_FILENAME).read_text("utf-8"))
    assert journal["query_limit"] == 8192  # observability, non-identity

    def raising(_: object) -> object:
        raise AssertionError("replay must make zero dispatcher invocations")

    for knob in ("64", "not-an-int"):
        monkeypatch.setenv("MARCUS_ASK_B_QUERY_MAX_CHARS", knob)
        replay = wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=raising
        )
        assert replay == first  # identity survived the operational knob


def test_non_integer_query_limit_is_typed_config_invalid(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R7 (B3): a non-integer/invalid MARCUS_ASK_B_QUERY_MAX_CHARS on the
    dispatch path is ``ask-b.config-invalid`` — never a scope-overflow claim
    about the demand; zero dispatch, zero claim."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    for knob in ("not-an-int", "0", "-5"):
        monkeypatch.setenv("MARCUS_ASK_B_QUERY_MAX_CHARS", knob)
        with pytest.raises(SpecialistDispatchError) as exc:
            wiring.run_ask_b_research(
                run_dir=tmp_path,
                trial_id="trial",
                dispatch_live=True,
                dispatch=lambda _: _result(),
            )
        assert exc.value.tag == "ask-b.config-invalid"
        assert not (tmp_path / wiring.JOURNAL_FILENAME).exists()
        assert not (tmp_path / wiring.LOCK_FILENAME).exists()


def test_provider_config_fingerprint_binds_dispatch_shaping_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4 R8 (B10): the fingerprint digests the ACTUAL dispatch-shaping inputs
    (provider, mode, adapter qualname, iteration budget, acceptance
    constants) — provider drift changes it; the query limit does not enter."""
    from app.marcus.lesson_plan.ask_b_hot_topics import canonical_digest as digest

    expected = digest(
        {
            "provider": wiring._PROVIDER_NAME,
            "mode": wiring._PROVIDER_MODE,
            "adapter": wiring._ADAPTER_QUALNAME,
            "contract": wiring._ADAPTER_CONTRACT,
            "iteration_budget": wiring._ITERATION_BUDGET,
            "acceptance_mechanical": wiring._ACCEPTANCE_MECHANICAL,
            "semantic_deferred": wiring._SEMANTIC_DEFERRED,
            "convergence_required": wiring._CONVERGENCE_REQUIRED,
            "cross_validate": wiring._CROSS_VALIDATE,
        }
    )
    baseline = wiring._provider_config_fingerprint()
    assert baseline == expected
    # An injected test double at the owned seam (the M-4 posture) must NOT
    # flip replay identity — the adapter qualname is a static constant.
    monkeypatch.setattr(wiring, "_default_dispatch", lambda intent: intent)
    assert wiring._provider_config_fingerprint() == baseline
    monkeypatch.setattr(wiring, "_ITERATION_BUDGET", 5)
    assert wiring._provider_config_fingerprint() != baseline  # drift is visible


def test_replay_divergence_check_includes_research_intake(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R12 (E9): a completed journal whose recorded research_intake
    disagrees with the replayed truth fails reconciliation — intake is part
    of the divergence check, not a blind spot."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    path = tmp_path / wiring.JOURNAL_FILENAME
    journal = json.loads(path.read_text("utf-8"))
    forged = journal["research_intake"]
    forged["covered_ability_ids"], forged["uncovered_ability_ids"] = (
        forged["uncovered_ability_ids"],
        forged["covered_ability_ids"],
    )
    path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(SpecialistDispatchError) as exc:
        wiring.run_ask_b_research(
            run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
        )
    assert exc.value.tag == "ask-b.reconciliation-failed"


def test_parent_directory_fsync_intent_covers_lock_and_journal_writes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """T4 R13 (B11): the platform-guarded ``_fsync_dir`` helper is invoked for
    the lock create and for EVERY journal ``os.replace`` (pre-call +
    completed) — intent recorded on all platforms, real durability on
    POSIX."""
    monkeypatch.setattr(wiring, "resolve_hot_topics_demand", lambda _: _demand())
    synced: list[Path] = []
    real = wiring._fsync_dir

    def spy(path: Path) -> None:
        synced.append(Path(path))
        real(path)

    monkeypatch.setattr(wiring, "_fsync_dir", spy)
    output = wiring.run_ask_b_research(
        run_dir=tmp_path, trial_id="trial", dispatch_live=True, dispatch=lambda _: _result()
    )
    assert output.disposition == "completed_ready"
    assert len(synced) == 3  # lock claim + pre-call replace + completed replace
    assert all(path == tmp_path for path in synced)
