from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.gates.resume_api import compute_decision_card_digest
from app.models.decision_cards import G1Card, G2BCard, G4ACard
from app.models.runtime import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from scripts.utilities import marcus_spoc_live_test_runner as runner

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def _policy(root: Path | None = None, **budget_overrides: int) -> runner.DelegationPolicy:
    budget = {
        "max_gate_actions": 12,
        "max_wall_seconds": 600,
        "max_specialist_calls_per_segment": 12,
        **budget_overrides,
    }
    return runner.DelegationPolicy.model_validate(
        {
            "schema_version": runner.POLICY_SCHEMA,
            "delegate_id": runner.DELEGATE_ID,
            "approved_by": "Juanl",
            "authority_spec": (
                "_bmad-output/implementation-artifacts/"
                "spec-delegated-live-test-hil-runner.md"
            ),
            "scope": {
                "purpose": "epics-36-40-workbook-live-verification",
                "epics": [36, 37, 38, 39, 40],
                "customer_facing_approval": False,
            },
            "allowed_runs_roots": [
                str(root / "runs") if root else "runs"
            ],
            "allowed_input_roots": [
                str(root / "corpus") if root else "course-content"
            ],
            "allowed_evidence_root": str(root / "evidence") if root else (
                "_bmad-output/implementation-artifacts/evidence/workbook-live-hil"
            ),
            "gate_rules": {
                "G0E": {"action": "approve"},
                "G0R": {"action": "approve"},
                "G1": {"action": "approve"},
                "G2B": {
                    "action": "select",
                    "selection_field": "slide_variant_selections",
                    "strategy": "first_offered",
                },
                "G2C": {"action": "approve"},
                "G3": {"action": "approve"},
                "G4": {"action": "approve"},
                "G4A": {
                    "action": "select",
                    "selection_field": "selected_voice_id",
                    "strategy": "first_offered",
                },
            },
            "stop_states": sorted(runner._STOP_STATES),
            "terminal_success_state": "completed",
            "budgets": budget,
        }
    )


def _policy_digest(policy: runner.DelegationPolicy) -> str:
    return runner._digest(policy.model_dump(mode="json"))


def _envelope(
    status: str,
    *,
    gate: str | None,
    corpus_path: Path | None = None,
) -> ProductionTrialEnvelope:
    return ProductionTrialEnvelope(
        trial_id=TRIAL_ID,
        preset="production",
        corpus_path=(corpus_path or Path("course-content/course/module/lesson")).as_posix(),
        operator_id=runner.DELEGATE_ID,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC) if status == "completed" else None,
        status=status,
        paused_gate=gate,
        paused_error_tag="test-error" if status == "paused-at-error" else None,
        waiting_batch_id="batch-1" if status == "waiting_for_provider_batch" else None,
        production_clone_launch_evidence=status == "completed",
        production_envelope=ProductionEnvelope(trial_id=TRIAL_ID, fixture_run=True),
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _valid_directive_text(*, run_id: UUID, corpus: Path) -> str:
    return (
        f"run_id: {run_id}\n"
        f"corpus_dir: {corpus.as_posix()}\n"
        "sources:\n"
        "  - ref_id: src-1\n"
        "    locator: source.md\n"
        "    provider: local_file\n"
        "    role: primary\n"
        "    expected_min_words: 1\n"
        "composed_at: '2026-07-13T12:00:00Z'\n"
        "schema_version: 1\n"
    )


def _card(gate: str, *, candidates: list[str] | None = None):
    common = {
        "card_id": uuid4(),
        "trial_id": TRIAL_ID,
        "decision_card_digest": "0" * 64,
        "meta": {"cache_state": "healthy", "affected_nodes": [], "override_trail": []},
        "verb": "approve",
    }
    if gate == "G1":
        return G1Card(
            **common,
            trial_summary="Ready for bounded workbook verification.",
            opened_by="marcus",
            next_nodes=["04A"],
        )
    if gate == "G2B":
        choices = candidates if candidates is not None else ["B", "A"]
        return G2BCard(
            **common,
            variant_candidates=choices,
            pick_context=[
                {
                    "kind": "variant-options",
                    "slides": [
                        {
                            "slide_id": "slide-1",
                            "variants": [{"variant": item} for item in choices],
                        },
                        {
                            "slide_id": "slide-2",
                            "variants": [{"variant": item} for item in reversed(choices)],
                        },
                    ],
                }
            ] if choices else [],
            operator_prompt="Select one offered variant.",
        )
    if gate == "G4A":
        return G4ACard(
            **common,
            voice_candidates=candidates if candidates is not None else ["voice-2", "voice-1"],
            operator_prompt="Select one offered voice.",
        )
    raise AssertionError(gate)


def _write_state(
    root: Path,
    *,
    envelope: ProductionTrialEnvelope,
    card=None,
    workbook: bool = True,
    digest_override: str | None = None,
) -> Path:
    run_dir = root / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    corpus = root.parent / "corpus"
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / "source.md").write_text("source", encoding="utf-8")
    envelope = envelope.model_copy(update={"corpus_path": corpus.as_posix()})
    _write_json(run_dir / "run.json", envelope.model_dump(mode="json"))
    checkpoint = {
        "trial_id": str(TRIAL_ID),
        "gate_id": envelope.paused_gate,
        "run_state": {
            "component_selection": {"deck": True, "motion": False, "workbook": workbook}
        },
    }
    _write_json(run_dir / "checkpoint.json", checkpoint)
    _write_json(
        run_dir / "workbook-runtime-context.v1.json",
        {
            "schema_version": "workbook-runtime-context.v1",
            "course_source_root": corpus.as_posix(),
            "encounter_mode": "recorded",
            "context_origin": "new_start",
            "writer_execution_mode": "live",
        },
    )
    if card is not None:
        issued_at = datetime.now(UTC)
        nonce = uuid4().hex
        digest = compute_decision_card_digest(
            card=card,
            trial_id=TRIAL_ID,
            issuance_timestamp=issued_at,
            server_nonce=nonce,
        )
        _write_json(
            run_dir / f"decision-card-{card.gate_id}.json",
            {
                "card": card.model_dump(mode="json"),
                "digest": digest_override or digest,
                "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
                "server_nonce": nonce,
                "checkpoint_path": (run_dir / "checkpoint.json").as_posix(),
            },
        )
    return run_dir


def _drive(
    tmp_path: Path,
    *,
    envelope: ProductionTrialEnvelope,
    card=None,
    policy: runner.DelegationPolicy | None = None,
    resume_fn=None,
) -> dict:
    runs = tmp_path / "runs"
    evidence = tmp_path / "evidence"
    _write_state(runs, envelope=envelope, card=card)
    effective_policy = policy or _policy(tmp_path)

    def authoritative_resume(**call_kwargs):
        returned = resume_fn(**call_kwargs)
        returned = returned.model_copy(
            update={"corpus_path": (tmp_path / "corpus").as_posix()}
        )
        _write_json(
            runs / str(TRIAL_ID) / "run.json",
            returned.model_dump(mode="json"),
        )
        return returned

    return runner.drive_paused_trial(
        trial_id=TRIAL_ID,
        runs_root=runs,
        policy=effective_policy,
        policy_digest=_policy_digest(effective_policy),
        evidence_root=evidence,
        **({"resume_fn": authoritative_resume} if resume_fn is not None else {}),
    )


def test_standing_policy_is_strict_and_identity_bound() -> None:
    policy, digest = runner.load_policy(
        runner.PROJECT_ROOT
        / "tests/fixtures/marcus_spoc/workbook_live_hil_policy.json"
    )
    assert policy.delegate_id == "codex_hil_runner"
    assert policy.scope.epics == (36, 37, 38, 39, 40)
    assert policy.scope.customer_facing_approval is False
    assert len(digest) == 64


@pytest.mark.parametrize("bad_epics", [[36, 37, 38, 39], [35, 36, 37, 38, 39, 40]])
def test_policy_refuses_scope_expansion_or_contraction(bad_epics: list[int]) -> None:
    payload = _policy().model_dump(mode="json")
    payload["scope"]["epics"] = bad_epics
    with pytest.raises(Exception, match="Epics 36-40"):
        runner.DelegationPolicy.model_validate(payload)


def test_standard_gate_uses_one_real_card_bound_delegate_verdict(tmp_path: Path) -> None:
    seen = []

    def resume(**kwargs):
        seen.append(kwargs)
        return _envelope("completed", gate=None)

    summary = _drive(
        tmp_path,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
        resume_fn=resume,
    )
    verdict = seen[0]["verdict"]
    assert summary["success"] is True and summary["status"] == "completed"
    assert len(seen) == 1
    assert verdict.operator_id == "codex_hil_runner"
    assert verdict.verb == "approve"
    assert verdict.gate_id == "G1"
    assert len(verdict.decision_card_digest) == 64


def test_engine_exception_becomes_secret_free_refusal_summary(tmp_path: Path) -> None:
    def explode(**kwargs):
        del kwargs
        raise RuntimeError("API_KEY=must-not-be-journaled")

    with pytest.raises(runner.RunnerRefusal, match="engine-call-failed"):
        _drive(
            tmp_path,
            envelope=_envelope("paused-at-gate", gate="G1"),
            card=_card("G1"),
            resume_fn=explode,
        )
    summary = json.loads(
        (
            tmp_path
            / "evidence"
            / str(TRIAL_ID)
            / "summary.json"
        ).read_text(encoding="utf-8")
    )
    assert summary["reason"] == "engine-call-failed"
    assert "must-not-be-journaled" not in json.dumps(summary)


@pytest.mark.parametrize(
    ("gate", "field", "expected"),
    [
        (
            "G2B",
            "slide_variant_selections",
            {"slide-1": "B", "slide-2": "A"},
        ),
        ("G4A", "selected_voice_id", "voice-2"),
    ],
)
def test_selection_gate_selects_only_first_offered_id(
    tmp_path: Path, gate: str, field: str, expected: object
) -> None:
    seen = []

    def resume(**kwargs):
        seen.append(kwargs["verdict"])
        return _envelope("completed", gate=None)

    _drive(
        tmp_path,
        envelope=_envelope("paused-at-gate", gate=gate),
        card=_card(gate),
        resume_fn=resume,
    )
    assert seen[0].verb == "select"
    assert seen[0].edit_payload == {field: expected}


def test_missing_selection_choices_makes_zero_engine_calls(tmp_path: Path) -> None:
    calls = []
    with pytest.raises(runner.RunnerRefusal, match="missing-or-ambiguous"):
        _drive(
            tmp_path,
            envelope=_envelope("paused-at-gate", gate="G2B"),
            card=_card("G2B", candidates=[]),
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


@pytest.mark.parametrize(
    "offered",
    [["B", "A", ""], ["B", "A", "B"]],
    ids=["blank-unreferenced-id", "duplicate-unreferenced-id"],
)
def test_g2b_rejects_malformed_offered_candidates_absent_from_slide_rows(
    tmp_path: Path, offered: list[str]
) -> None:
    calls = []
    card = _card("G2B").model_copy(update={"variant_candidates": offered})

    with pytest.raises(runner.RunnerRefusal, match="missing-or-ambiguous"):
        _drive(
            tmp_path,
            envelope=_envelope("paused-at-gate", gate="G2B"),
            card=card,
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )

    assert calls == []


def test_malformed_card_digest_makes_zero_engine_calls(tmp_path: Path) -> None:
    calls = []
    runs = tmp_path / "runs"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
        digest_override="b" * 64,
    )
    with pytest.raises(runner.RunnerRefusal, match="decision-card-digest-mismatch"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=_policy(tmp_path),
            policy_digest=_policy_digest(_policy(tmp_path)),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_non_workbook_trial_makes_zero_engine_calls(tmp_path: Path) -> None:
    calls = []
    runs = tmp_path / "runs"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
        workbook=False,
    )
    with pytest.raises(runner.RunnerRefusal, match="trial-not-workbook-scoped"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=_policy(tmp_path),
            policy_digest=_policy_digest(_policy(tmp_path)),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_restart_with_consumed_current_card_stops_split_brain(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    evidence = tmp_path / "evidence"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    card_payload = json.loads((run_dir / "decision-card-G1.json").read_text())
    policy = _policy(tmp_path)
    digest = _policy_digest(policy)
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID, policy_digest=digest, evidence_root=evidence
    )
    journal.append(
        "submission-started",
        gate_id="G1",
        decision_card_digest=card_payload["digest"],
    )
    calls = []
    with pytest.raises(runner.RunnerRefusal, match="split-brain"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=digest,
            evidence_root=evidence,
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_restart_reconciles_advanced_envelope_without_resubmit(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    evidence = tmp_path / "evidence"
    _write_state(runs, envelope=_envelope("completed", gate=None))
    policy = _policy(tmp_path)
    digest = _policy_digest(policy)
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID, policy_digest=digest, evidence_root=evidence
    )
    journal.append(
        "submission-started",
        gate_id="G4A",
        decision_card_digest="b" * 64,
    )
    calls = []
    summary = runner.drive_paused_trial(
        trial_id=TRIAL_ID,
        runs_root=runs,
        policy=policy,
        policy_digest=digest,
        evidence_root=evidence,
        resume_fn=lambda **kwargs: calls.append(kwargs),
    )
    assert summary["success"] is True
    assert calls == []
    assert journal.path.exists()
    reloaded = json.loads(journal.path.read_text())
    assert reloaded["events"][-1]["kind"] == "submission-reconciled"


@pytest.mark.parametrize(
    "status", ["paused-at-error", "waiting_for_provider_batch", "failed"]
)
def test_non_gate_stop_is_never_success(
    tmp_path: Path, status: str
) -> None:
    calls = []
    summary = _drive(
        tmp_path,
        envelope=_envelope(status, gate=None),
        resume_fn=lambda **kwargs: calls.append(kwargs),
    )
    assert summary["success"] is False
    assert summary["status"] == status
    assert calls == []


def test_exclusive_trial_lock_rejects_concurrent_runner(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    with (
        runner.exclusive_trial_lock(
            run_dir, trial_id=TRIAL_ID, policy_digest="a" * 64
        ),
        pytest.raises(runner.RunnerRefusal, match="trial-lock-held"),
        runner.exclusive_trial_lock(
            run_dir, trial_id=TRIAL_ID, policy_digest="a" * 64
        ),
    ):
        pytest.fail("second lock entered")
    assert not (run_dir / ".codex-hil-runner.lock").exists()


def test_symlinked_decision_card_is_refused_before_engine_call(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    original = run_dir / "original.json"
    card_path = run_dir / "decision-card-G1.json"
    card_path.replace(original)
    try:
        card_path.symlink_to(original)
    except OSError:
        pytest.skip("symlink creation unavailable")
    calls = []
    with pytest.raises(runner.RunnerRefusal, match="symlink-or-reparse"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=_policy(tmp_path),
            policy_digest=_policy_digest(_policy(tmp_path)),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_gate_budget_exhaustion_makes_zero_engine_calls(tmp_path: Path) -> None:
    calls = []
    runs = tmp_path / "runs"
    evidence = tmp_path / "evidence"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    policy = _policy(tmp_path, max_gate_actions=1)
    digest = _policy_digest(policy)
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID, policy_digest=digest, evidence_root=evidence
    )
    journal.append(
        "submission-started", gate_id="G0E", decision_card_digest="b" * 64
    )
    journal.append(
        "transition-recorded",
        decision_card_digest="b" * 64,
        resulting_status="paused-at-gate",
        resulting_gate="G1",
    )
    with pytest.raises(runner.RunnerRefusal, match="gate-action-budget"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=digest,
            evidence_root=evidence,
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_g0_callback_validates_structure_and_records_digest(tmp_path: Path) -> None:
    input_path = tmp_path / "corpus"
    input_path.mkdir()
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    evidence = tmp_path / "evidence"
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID, policy_digest="a" * 64, evidence_root=evidence
    )
    directive = run_dir / "directive.yaml"
    raw = _valid_directive_text(run_id=TRIAL_ID, corpus=input_path).encode()
    directive.write_bytes(raw)
    callback = runner._directive_confirmation(
        trial_id=TRIAL_ID,
        input_path=input_path,
        run_dir=run_dir,
        journal=journal,
    )
    assert callback(directive_path=directive, auto_confirm_directive=False) == "confirmed"
    assert journal.events[-1]["kind"] == "g0-directive-confirmed"
    assert journal.events[-1]["directive_digest"] == hashlib.sha256(raw).hexdigest()


def test_g0_callback_refuses_wrong_trial_without_dispatch(tmp_path: Path) -> None:
    input_path = tmp_path / "corpus"
    input_path.mkdir()
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID,
        policy_digest="a" * 64,
        evidence_root=tmp_path / "evidence",
    )
    directive = run_dir / "directive.yaml"
    directive.write_text(
        _valid_directive_text(run_id=uuid4(), corpus=input_path), encoding="utf-8"
    )
    callback = runner._directive_confirmation(
        trial_id=TRIAL_ID,
        input_path=input_path,
        run_dir=run_dir,
        journal=journal,
    )
    with pytest.raises(runner.RunnerRefusal, match="g0-directive-trial-mismatch"):
        callback(directive_path=directive, auto_confirm_directive=False)
    assert journal.events == []


def test_start_uses_injected_g0_and_workbook_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    run_dir = runs / str(TRIAL_ID)
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "source.md").write_text("source", encoding="utf-8")
    evidence = tmp_path / "evidence"
    captured = {}

    def fake_start(**kwargs):
        captured.update(kwargs)
        assert (run_dir / ".codex-hil-runner.lock").is_file()
        directive = run_dir / "directive.yaml"
        directive.write_text(
            _valid_directive_text(run_id=TRIAL_ID, corpus=corpus),
            encoding="utf-8",
        )
        assert kwargs["confirm_fn"](
            directive_path=directive, auto_confirm_directive=False
        ) == "confirmed"
        return {"status": "paused-at-gate"}

    monkeypatch.setattr(runner, "start_trial", fake_start)
    monkeypatch.setattr(
        runner,
        "_drive_with_evidence_handling",
        lambda **kwargs: {"success": True, "status": "completed"},
    )
    policy = _policy(tmp_path)
    summary = runner.start_and_drive_trial(
        trial_id=TRIAL_ID,
        input_path=corpus,
        course_source_root=corpus,
        encounter_mode="recorded",
        runs_root=runs,
        policy=policy,
        policy_digest=_policy_digest(policy),
        evidence_root=evidence,
    )
    assert summary["success"] is True
    assert captured["operator_id"] == "codex_hil_runner"
    assert captured["auto_confirm_directive"] is False
    assert captured["component_selection"].workbook is True
    assert captured["hud"] == "off"
    assert captured["course_source_root"] == corpus
    assert captured["encounter_mode"] == "recorded"


def test_cli_run_contract_requires_workbook_context_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        runner,
        "load_policy",
        lambda path: (_policy(tmp_path), "a" * 64),
    )
    with pytest.raises(runner.RunnerRefusal, match="start-workbook-context-required"):
        runner.run(
            mode="start",
            trial_id=TRIAL_ID,
            policy_path=tmp_path / "policy.json",
            runs_root=tmp_path / "runs",
            evidence_root=tmp_path / "evidence",
            input_path=tmp_path / "corpus",
        )


def test_public_start_rejects_unknown_encounter_mode(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match="encounter-mode-invalid"):
        runner.start_and_drive_trial(
            trial_id=TRIAL_ID,
            input_path=corpus,
            course_source_root=corpus,
            encounter_mode="invented",  # type: ignore[arg-type]
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
        )


def test_start_failure_is_summarized_without_exception_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "source.md").write_text("source", encoding="utf-8")
    evidence = tmp_path / "evidence"

    def fail_start(**kwargs):
        del kwargs
        raise RuntimeError("password=must-not-be-recorded")

    monkeypatch.setattr(runner, "start_trial", fail_start)
    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match="start-failed"):
        runner.start_and_drive_trial(
            trial_id=TRIAL_ID,
            input_path=corpus,
            course_source_root=corpus,
            encounter_mode="recorded",
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=evidence,
        )
    evidence_text = (evidence / str(TRIAL_ID) / "journal.json").read_text(
        encoding="utf-8"
    )
    assert "must-not-be-recorded" not in evidence_text
    assert '"reason": "start-failed"' in evidence_text


def test_lexical_parent_traversal_is_refused_before_evidence_creation(
    tmp_path: Path,
) -> None:
    runs = tmp_path / "runs"
    _write_state(runs, envelope=_envelope("completed", gate=None))
    policy = _policy(tmp_path)
    traversing = tmp_path / "not-created" / "child" / ".." / "evidence"
    with pytest.raises(runner.RunnerRefusal, match="parent-traversal-refused"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=traversing,
        )
    assert not (tmp_path / "not-created").exists()


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("operator_id", "Juanl", "trial-operator-not-delegate"),
        ("preset", "explore", "trial-preset-out-of-scope"),
    ],
)
def test_attach_requires_delegated_production_trial(
    tmp_path: Path, field: str, value: str, reason: str
) -> None:
    runs = tmp_path / "runs"
    envelope = _envelope("paused-at-gate", gate="G1").model_copy(
        update={field: value}
    )
    _write_state(runs, envelope=envelope, card=_card("G1"))
    calls = []
    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match=reason):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_attach_recursively_refuses_reparse_entry_in_course_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    marker = tmp_path / "corpus" / "reparse-marker"
    marker.write_text("x", encoding="utf-8")
    real_check = runner._is_reparse_point
    monkeypatch.setattr(
        runner,
        "_is_reparse_point",
        lambda path: path == marker or real_check(path),
    )
    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match="source-tree-link-refused"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
        )


def test_scope_is_revalidated_immediately_before_submission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    real_load = runner._load_bound_card
    loads = 0

    def mutate_scope(*args, **kwargs):
        nonlocal loads
        result = real_load(*args, **kwargs)
        loads += 1
        if loads == 2:
            checkpoint = json.loads((run_dir / "checkpoint.json").read_text())
            checkpoint["run_state"]["component_selection"]["workbook"] = False
            _write_json(run_dir / "checkpoint.json", checkpoint)
        return result

    monkeypatch.setattr(runner, "_load_bound_card", mutate_scope)
    calls = []
    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match="trial-not-workbook-scoped"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_partial_workbook_runtime_context_is_refused(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    _write_json(
        run_dir / "workbook-runtime-context.v1.json",
        {
            "schema_version": "workbook-runtime-context.v1",
            "course_source_root": (tmp_path / "corpus").as_posix(),
            "encounter_mode": "recorded",
        },
    )
    policy = _policy(tmp_path)
    with pytest.raises(
        runner.RunnerRefusal, match="workbook-runtime-context-invalid"
    ):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
        )


def test_public_drive_refuses_policy_digest_before_evidence_or_engine(
    tmp_path: Path,
) -> None:
    runs = tmp_path / "runs"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    calls = []
    with pytest.raises(runner.RunnerRefusal, match="policy-digest-mismatch"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=_policy(tmp_path),
            policy_digest="0" * 64,
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []
    assert not (tmp_path / "evidence").exists()


def test_public_start_refuses_policy_digest_before_evidence_or_engine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    calls = []
    monkeypatch.setattr(runner, "start_trial", lambda **kwargs: calls.append(kwargs))
    with pytest.raises(runner.RunnerRefusal, match="policy-digest-mismatch"):
        runner.start_and_drive_trial(
            trial_id=TRIAL_ID,
            input_path=corpus,
            course_source_root=corpus,
            encounter_mode="recorded",
            runs_root=runs,
            policy=_policy(tmp_path),
            policy_digest="0" * 64,
            evidence_root=tmp_path / "evidence",
        )
    assert calls == []
    assert not (tmp_path / "evidence").exists()


def test_run_refuses_unknown_mode_without_loading_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        runner,
        "load_policy",
        lambda path: pytest.fail("unknown mode must fail before policy load"),
    )
    with pytest.raises(runner.RunnerRefusal, match="unknown-runner-mode"):
        runner.run(
            mode="bogus",  # type: ignore[arg-type]
            trial_id=TRIAL_ID,
            policy_path=tmp_path / "policy.json",
            runs_root=tmp_path / "runs",
            evidence_root=tmp_path / "evidence",
        )


def test_deadline_expires_before_submission_journal_and_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = tmp_path / "runs"
    _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    ticks = iter((0.0, 2.0))
    monkeypatch.setattr(runner.time, "monotonic", lambda: next(ticks))
    calls = []
    with pytest.raises(runner.RunnerRefusal, match="wall-clock-budget-exhausted"):
        runner._drive_paused_trial_impl(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=_policy(tmp_path, max_wall_seconds=1),
            policy_digest="a" * 64,
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
            started_at=0.0,
        )
    journal = json.loads(
        (tmp_path / "evidence" / str(TRIAL_ID) / "journal.json").read_text()
    )
    assert calls == []
    assert not any(event["kind"] == "submission-started" for event in journal["events"])


def test_public_drive_cannot_bypass_existing_trial_lock(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )
    calls = []
    policy = _policy(tmp_path)
    with (
        runner.exclusive_trial_lock(
            run_dir, trial_id=TRIAL_ID, policy_digest="a" * 64
        ),
        pytest.raises(runner.RunnerRefusal, match="trial-lock-held"),
    ):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            resume_fn=lambda **kwargs: calls.append(kwargs),
        )
    assert calls == []


def test_g0_rejects_shape_that_is_not_a_production_directive(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    directive = run_dir / "directive.yaml"
    directive.write_text(
        f"run_id: {TRIAL_ID}\ncorpus_dir: {corpus.as_posix()}\nsources: []\n",
        encoding="utf-8",
    )
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID,
        policy_digest="a" * 64,
        evidence_root=tmp_path / "evidence",
    )
    callback = runner._directive_confirmation(
        trial_id=TRIAL_ID,
        input_path=corpus,
        run_dir=run_dir,
        journal=journal,
    )
    with pytest.raises(runner.RunnerRefusal, match="g0-directive-malformed"):
        callback(directive_path=directive, auto_confirm_directive=False)
    assert journal.events == []


def test_g0_hashes_and_validates_the_same_single_read_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    directive = run_dir / "directive.yaml"
    original = _valid_directive_text(run_id=TRIAL_ID, corpus=corpus).encode()
    directive.write_bytes(original)
    real_read = Path.read_bytes
    reads = 0

    def read_then_mutate(path: Path) -> bytes:
        nonlocal reads
        payload = real_read(path)
        if path == directive:
            reads += 1
            path.write_text("not: a production directive\n", encoding="utf-8")
        return payload

    monkeypatch.setattr(Path, "read_bytes", read_then_mutate)
    journal = runner.EvidenceJournal(
        trial_id=TRIAL_ID,
        policy_digest="a" * 64,
        evidence_root=tmp_path / "evidence",
    )
    callback = runner._directive_confirmation(
        trial_id=TRIAL_ID,
        input_path=corpus,
        run_dir=run_dir,
        journal=journal,
    )
    with pytest.raises(
        runner.RunnerRefusal, match="g0-directive-mutated-during-review"
    ):
        callback(directive_path=directive, auto_confirm_directive=False)
    assert reads == 1
    assert journal.events == []


def test_late_resume_return_cannot_claim_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = {"now": 0.0}
    monkeypatch.setattr(runner.time, "monotonic", lambda: clock["now"])

    def late_resume(**kwargs):
        del kwargs
        clock["now"] = 2.0
        return _envelope("completed", gate=None)

    with pytest.raises(runner.RunnerRefusal, match="wall-clock-budget-exhausted"):
        _drive(
            tmp_path,
            envelope=_envelope("paused-at-gate", gate="G1"),
            card=_card("G1"),
            policy=_policy(tmp_path, max_wall_seconds=1),
            resume_fn=late_resume,
        )


def test_late_start_return_cannot_enter_drive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = {"now": 0.0}
    monkeypatch.setattr(runner.time, "monotonic", lambda: clock["now"])
    runs = tmp_path / "runs"
    runs.mkdir()
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "source.md").write_text("source", encoding="utf-8")

    def late_start(**kwargs):
        del kwargs
        clock["now"] = 2.0
        return {"status": "paused-at-gate"}

    monkeypatch.setattr(runner, "start_trial", late_start)
    policy = _policy(tmp_path, max_wall_seconds=1)
    with pytest.raises(runner.RunnerRefusal, match="wall-clock-budget-exhausted"):
        runner.start_and_drive_trial(
            trial_id=TRIAL_ID,
            input_path=corpus,
            course_source_root=corpus,
            encounter_mode="recorded",
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            started_at=0.0,
        )


def test_expired_completed_attach_cannot_claim_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(runner.time, "monotonic", lambda: 2.0)
    runs = tmp_path / "runs"
    _write_state(runs, envelope=_envelope("completed", gate=None))
    policy = _policy(tmp_path, max_wall_seconds=1)
    with pytest.raises(runner.RunnerRefusal, match="wall-clock-budget-exhausted"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            started_at=0.0,
        )


def test_resume_return_must_match_authoritative_run_json(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    run_dir = _write_state(
        runs,
        envelope=_envelope("paused-at-gate", gate="G1"),
        card=_card("G1"),
    )

    def split_brain(**kwargs):
        del kwargs
        returned = _envelope(
            "completed", gate=None, corpus_path=tmp_path / "corpus"
        )
        persisted = _envelope(
            "failed", gate=None, corpus_path=tmp_path / "corpus"
        )
        _write_json(run_dir / "run.json", persisted.model_dump(mode="json"))
        return returned

    policy = _policy(tmp_path)
    with pytest.raises(runner.RunnerRefusal, match="resume-return-disk-mismatch"):
        runner.drive_paused_trial(
            trial_id=TRIAL_ID,
            runs_root=runs,
            policy=policy,
            policy_digest=_policy_digest(policy),
            evidence_root=tmp_path / "evidence",
            resume_fn=split_brain,
        )
