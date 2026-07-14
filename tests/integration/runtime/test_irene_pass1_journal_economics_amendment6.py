from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan import pass1_call_journal as journal_module
from app.marcus.lesson_plan.pass1_call_journal import (
    begin_or_resume_pass1_call,
    build_pass1_call_identity,
    record_pass1_candidate_processing,
    record_pass1_response,
)
from app.models.runtime import AgentCostEntry, BudgetStatus, TrialEconomicsReport
from app.runtime import economics as economics_module
from app.runtime.cascade_config import load_pricing
from app.runtime.economics import record_trial_cost_report

ATTEMPT_LEDGER = "irene-pass1-provider-attempts.v1.json"


def _base_report(trial_id: str) -> TrialEconomicsReport:
    return TrialEconomicsReport(
        trial_id=trial_id,
        measured_at=datetime(2026, 7, 14, 12, 0, tzinfo=UTC),
        total_cost_usd=0.01,
        per_agent_breakdown={
            "texas": AgentCostEntry(
                agent_name="texas",
                model_assigned="gpt-5-nano",
                call_count=1,
                input_tokens=100,
                output_tokens=20,
                cost_usd=0.01,
            )
        },
        per_model_breakdown={"gpt-5-nano": 0.01},
        cascade_config_digest="a" * 64,
        pricing_table_digest=load_pricing().sha256_digest,
        langsmith_trace_url=None,
        drift_alerts=[],
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
    )


def _begin_attempt(
    run_dir: Path,
    trial_id: str,
    *,
    model_id: str = "gpt-5.4",
    node_id: str = "04A",
):
    identity = build_pass1_call_identity(
        run_id=trial_id,
        node_id=node_id,
        model_id=model_id,
        model_config_digest="sha256:" + "a" * 64,
        catalog_digest="sha256:" + "b" * 64,
        messages=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ],
    )
    resume = begin_or_resume_pass1_call(run_dir=run_dir, identity=identity)
    return identity, resume


def _downgrade_response_journal_to_v1(path: Path) -> dict[str, object]:
    journal = json.loads(path.read_text(encoding="utf-8"))
    journal["processor_version"] = journal_module.LEGACY_PROCESSOR_VERSION
    identity_body = {
        key: journal[key]
        for key in journal_module._IDENTITY_KEYS  # noqa: SLF001
        if key != "request_digest"
    }
    journal["request_digest"] = journal_module._digest(identity_body)  # noqa: SLF001
    path.write_text(json.dumps(journal), encoding="utf-8")
    return journal


def test_returned_failed_validation_attempt_is_priced_from_durable_usage(
    tmp_path: Path,
) -> None:
    trial_id = "failed-validation-priced"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response='{"source_ref_ids":["unknown"]}',
        provider_evidence={
            "usage_metadata": {"input_tokens": 1200, "output_tokens": 300},
            "response_metadata": {"finish_reason": "stop"},
            "response_id": "resp-failed-validation",
        },
    )

    json_path = record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    report = TrialEconomicsReport.model_validate_json(json_path.read_text(encoding="utf-8"))
    expected = load_pricing().compute_cost("gpt-5.4", input_tokens=1200, output_tokens=300)
    assert report.per_agent_breakdown["irene_pass1"].call_count == 1
    assert report.per_agent_breakdown["irene_pass1"].cost_usd == round(expected, 8)
    assert report.total_cost_usd == round(0.01 + expected, 8)

    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["journal_state"] == "response_received"
    assert ledger["attempts"][0]["cost_status"] == "known"
    assert ledger["attempts"][0]["cost_usd"] == round(expected, 8)
    assert ledger["unavailable_attempt_count"] == 0


def test_candidate_decoded_attempt_is_priced_exactly_once(tmp_path: Path) -> None:
    trial_id = "candidate-decoded-priced-once"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    candidate = {"plan_units": []}
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response=json.dumps(candidate),
        provider_evidence={
            "usage_metadata": {"input_tokens": 1200, "output_tokens": 300},
            "response_id": "resp-candidate-decoded",
        },
    )
    record_pass1_candidate_processing(
        path=resume.path,
        identity=identity,
        action="strict-json",
        framing="plain",
        removed_byte=None,
        removed_offset=None,
        processed_candidate=candidate,
    )

    json_path = record_trial_cost_report(
        trial_id, _base_report(trial_id), runs_root=tmp_path
    )
    report = TrialEconomicsReport.model_validate_json(
        json_path.read_text(encoding="utf-8")
    )
    expected = load_pricing().compute_cost(
        "gpt-5.4", input_tokens=1200, output_tokens=300
    )
    assert report.per_agent_breakdown["irene_pass1"].call_count == 1
    assert report.per_agent_breakdown["irene_pass1"].cost_usd == round(expected, 8)
    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["journal_state"] == "candidate_decoded"


def test_legacy_v1_response_received_is_priced_exactly_once(tmp_path: Path) -> None:
    trial_id = "legacy-v1-priced-once"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={
            "usage_metadata": {"input_tokens": 1200, "output_tokens": 300},
            "response_id": "resp-legacy-v1",
        },
    )
    _downgrade_response_journal_to_v1(resume.path)

    json_path = record_trial_cost_report(
        trial_id, _base_report(trial_id), runs_root=tmp_path
    )
    report = TrialEconomicsReport.model_validate_json(
        json_path.read_text(encoding="utf-8")
    )
    expected = load_pricing().compute_cost(
        "gpt-5.4", input_tokens=1200, output_tokens=300
    )
    assert report.per_agent_breakdown["irene_pass1"].call_count == 1
    assert report.per_agent_breakdown["irene_pass1"].cost_usd == round(expected, 8)
    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["journal_state"] == "response_received"


def test_malformed_legacy_v1_journal_fails_economics_closed(tmp_path: Path) -> None:
    trial_id = "legacy-v1-malformed"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 1, "output_tokens": 1}},
    )
    legacy = _downgrade_response_journal_to_v1(resume.path)
    legacy["unexpected"] = True
    resume.path.write_text(json.dumps(legacy), encoding="utf-8")

    with pytest.raises(RuntimeError, match="provider-attempt journal invalid"):
        record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)


def test_returned_attempt_without_usage_is_explicitly_cost_unavailable(
    tmp_path: Path,
) -> None:
    trial_id = "failed-validation-usage-unavailable"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response='{"source_ref_ids":["unknown"]}',
        provider_evidence={"usage_metadata": None, "response_id": "resp-no-usage"},
    )

    json_path = record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    report = TrialEconomicsReport.model_validate_json(json_path.read_text(encoding="utf-8"))
    assert report.per_agent_breakdown["irene_pass1"].call_count == 1
    assert report.per_agent_breakdown["irene_pass1"].cost_usd == 0.0
    assert report.total_cost_usd == 0.01
    assert report.cost_posture == "known-lower-bound-with-explicit-unavailable-attempts"
    assert report.unavailable_attempt_count == 1

    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["cost_status"] == "unavailable"
    assert ledger["attempts"][0]["cost_unavailable_reason"] == (
        "provider_usage_metadata_unavailable"
    )
    assert ledger["unavailable_attempt_count"] == 1
    markdown = json_path.with_suffix(".md").read_text(encoding="utf-8")
    assert "excludes 1 unavailable Irene attempt" in markdown


def test_rehashed_malformed_provider_evidence_cannot_be_priced(
    tmp_path: Path,
) -> None:
    trial_id = "malformed-evidence-not-priced"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={
            "usage_metadata": {"input_tokens": 10, "output_tokens": 5}
        },
    )
    journal = json.loads(resume.path.read_text(encoding="utf-8"))
    journal["provider_evidence"]["usage_metadata"]["total_tokens"] = 99
    journal["provider_evidence_digest"] = economics_module._canonical_digest(
        journal["provider_evidence"]
    )
    resume.path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="journal invalid"):
        record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)


def test_unknown_journal_envelope_fields_cannot_be_priced(tmp_path: Path) -> None:
    trial_id = "unknown-envelope-not-priced"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={
            "usage_metadata": {"input_tokens": 10, "output_tokens": 5}
        },
    )
    journal = json.loads(resume.path.read_text(encoding="utf-8"))
    journal["forged_extension"] = {"accepted": True}
    resume.path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="journal invalid"):
        record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("processor_version", "not-the-current-processor"),
        ("schema_version", "irene-pass1-call.v999"),
        ("catalog_digest", "not-a-digest"),
        ("messages", [{"role": "user", "content": "wrong order"}]),
    ],
)
def test_rehashed_noncanonical_call_identity_cannot_be_priced(
    tmp_path: Path, field: str, value: object
) -> None:
    trial_id = f"noncanonical-identity-{field}"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={
            "usage_metadata": {"input_tokens": 10, "output_tokens": 5}
        },
    )
    journal = json.loads(resume.path.read_text(encoding="utf-8"))
    journal[field] = value
    if field == "messages":
        journal["messages_digest"] = economics_module._canonical_digest(value)
    identity_keys = {
        "schema_version",
        "processor_version",
        "run_id",
        "node_id",
        "model_id",
        "model_config_digest",
        "catalog_digest",
        "messages",
        "messages_digest",
    }
    journal["request_digest"] = economics_module._canonical_digest(
        {key: journal[key] for key in identity_keys}
    )
    resume.path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="journal invalid"):
        record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)


def test_ambiguous_dispatch_is_counted_with_explicit_unavailable_posture(
    tmp_path: Path,
) -> None:
    trial_id = "ambiguous-attempt-unavailable"
    run_dir = tmp_path / trial_id
    _identity, _resume = _begin_attempt(run_dir, trial_id)

    record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["journal_state"] == "call_in_progress"
    assert ledger["attempts"][0]["cost_status"] == "unavailable"
    assert ledger["attempts"][0]["cost_unavailable_reason"] == ("provider_outcome_ambiguous")


def test_matching_trace_bucket_is_not_double_counted(tmp_path: Path) -> None:
    trial_id = "already-traced-attempt"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 1200, "output_tokens": 300}},
    )
    expected = round(
        load_pricing().compute_cost("gpt-5.4", input_tokens=1200, output_tokens=300),
        8,
    )
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=1,
        input_tokens=1200,
        output_tokens=300,
        cost_usd=expected,
    )
    report.per_model_breakdown["gpt-5.4"] = expected
    report.total_cost_usd = round(0.01 + expected, 8)
    object.__setattr__(
        report,
        "_trace_provider_attempts",
        (
            {
                "trace_run_id": "trace-irene-1",
                "request_digest": identity["request_digest"],
                "response_id": None,
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 1200,
                "output_tokens": 300,
                "cost_usd": expected,
            },
        ),
    )

    path = record_trial_cost_report(trial_id, report, runs_root=tmp_path)
    loaded = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    assert loaded.total_cost_usd == report.total_cost_usd
    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["trace_reconciliation_status"] == "all_correlated"
    assert ledger["attempts"][0]["trace_correlation"] == "request_digest"


def test_uncorrelated_existing_irene_trace_fails_instead_of_guessing(
    tmp_path: Path,
) -> None:
    trial_id = "uncorrelated-irene-trace"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 12, "output_tokens": 3}},
    )
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=1,
        input_tokens=12,
        output_tokens=3,
        cost_usd=0.001,
    )

    with pytest.raises(RuntimeError, match="without per-attempt correlation"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_reconciliation_recomputes_budget_and_drift(tmp_path: Path) -> None:
    trial_id = "recompute-budget-drift"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 1200, "output_tokens": 300}},
    )
    report = _base_report(trial_id)
    object.__setattr__(report, "_budget_usd", 0.010001)
    history = []
    for index in range(5):
        prior = _base_report(f"prior-{index}")
        prior.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
            agent_name="irene_pass1",
            model_assigned="gpt-5.4",
            call_count=1,
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.000001,
        )
        history.append(prior)
    object.__setattr__(report, "_economics_history", tuple(history))

    path = record_trial_cost_report(trial_id, report, runs_root=tmp_path)
    loaded = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    assert loaded.budget_status.state == "over-budget-warning"
    assert loaded.budget_status.over_by_usd > 0
    assert [alert.agent_name for alert in loaded.drift_alerts] == ["irene_pass1"]


def test_journal_pricing_must_match_report_identity(tmp_path: Path) -> None:
    trial_id = "pricing-mismatch"
    _identity_value, _resume = _begin_attempt(tmp_path / trial_id, trial_id)
    report = _base_report(trial_id)
    report.pricing_table_digest = "f" * 64

    with pytest.raises(RuntimeError, match="pricing identity"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_untraced_multi_model_attempts_add_correct_per_model_costs(
    tmp_path: Path,
) -> None:
    trial_id = "multi-model-irene"
    run_dir = tmp_path / trial_id
    for node_id, model_id in (("04A", "gpt-5.4"), ("05", "gpt-5-mini")):
        identity, resume = _begin_attempt(run_dir, trial_id, model_id=model_id, node_id=node_id)
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response="{}",
            provider_evidence={"usage_metadata": {"input_tokens": 120, "output_tokens": 30}},
        )

    path = record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    loaded = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    assert loaded.per_agent_breakdown["irene_pass1"].model_assigned == "mixed"
    for model_id in ("gpt-5.4", "gpt-5-mini"):
        expected = round(
            load_pricing().compute_cost(model_id, input_tokens=120, output_tokens=30),
            8,
        )
        assert loaded.per_model_breakdown[model_id] == expected


def test_cost_artifact_transaction_rolls_forward_after_interrupted_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial_id = "recover-cost-transaction"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 120, "output_tokens": 30}},
    )
    original = economics_module._atomic_write_bytes
    writes = 0

    def _interrupt(path: Path, content: bytes) -> None:
        nonlocal writes
        writes += 1
        original(path, content)
        if writes == 2:
            raise OSError("simulated crash")

    monkeypatch.setattr(economics_module, "_atomic_write_bytes", _interrupt)
    with pytest.raises(OSError, match="simulated crash"):
        record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    assert (run_dir / economics_module.COST_TRANSACTION_FILENAME).is_file()

    monkeypatch.setattr(economics_module, "_atomic_write_bytes", original)
    path = record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    assert path.is_file()
    assert not (run_dir / economics_module.COST_TRANSACTION_FILENAME).exists()
    assert (run_dir / ATTEMPT_LEDGER).is_file()


def test_zero_provider_usage_is_untrusted_instead_of_exact_free(tmp_path: Path) -> None:
    trial_id = "zero-usage-untrusted"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 0, "output_tokens": 0}},
    )

    path = record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    report = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    assert report.cost_posture == "known-lower-bound-with-explicit-unavailable-attempts"
    ledger = json.loads((run_dir / ATTEMPT_LEDGER).read_text(encoding="utf-8"))
    assert ledger["attempts"][0]["cost_unavailable_reason"] == "provider_usage_zero_untrusted"


def test_extra_irene_trace_without_journal_fails_closed(tmp_path: Path) -> None:
    trial_id = "trace-without-journal"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 12, "output_tokens": 3}},
    )
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=2,
        input_tokens=24,
        output_tokens=6,
        cost_usd=0.001,
    )
    object.__setattr__(
        report,
        "_trace_provider_attempts",
        (
            {
                "trace_run_id": "trace-one",
                "request_digest": identity["request_digest"],
                "response_id": None,
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 12,
                "output_tokens": 3,
                "cost_usd": round(
                    load_pricing().compute_cost(
                        "gpt-5.4", input_tokens=12, output_tokens=3
                    ),
                    8,
                ),
            },
            {
                "trace_run_id": "trace-two",
                "request_digest": "sha256:" + "f" * 64,
                "response_id": "resp-unJournaled",
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 12,
                "output_tokens": 3,
                "cost_usd": 0.0001,
            },
        ),
    )

    with pytest.raises(RuntimeError, match="without durable journals"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_one_trace_attempt_cannot_satisfy_two_journals(tmp_path: Path) -> None:
    trial_id = "trace-reused-by-journals"
    run_dir = tmp_path / trial_id
    for node_id in ("04A", "05"):
        identity, resume = _begin_attempt(run_dir, trial_id, node_id=node_id)
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response="{}",
            provider_evidence={
                "usage_metadata": {"input_tokens": 12, "output_tokens": 3},
                "response_id": "resp-shared",
            },
        )
    expected = round(
        load_pricing().compute_cost("gpt-5.4", input_tokens=12, output_tokens=3),
        8,
    )
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=1,
        input_tokens=12,
        output_tokens=3,
        cost_usd=expected,
    )
    object.__setattr__(
        report,
        "_trace_provider_attempts",
        (
            {
                "trace_run_id": "trace-one",
                "request_digest": None,
                "response_id": "resp-shared",
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 12,
                "output_tokens": 3,
                "cost_usd": expected,
            },
        ),
    )

    with pytest.raises(RuntimeError, match="cannot satisfy multiple journals"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_incomplete_cost_transaction_is_not_accepted(tmp_path: Path) -> None:
    run_dir = tmp_path / "incomplete-transaction"
    run_dir.mkdir()
    content = "{}\n"
    transaction = {
        "schema_version": "cost-report-transaction.v1",
        "artifacts": {
            "cost-report.json": {
                "content": content,
                "sha256": economics_module.hashlib.sha256(content.encode()).hexdigest(),
            }
        },
    }
    (run_dir / economics_module.COST_TRANSACTION_FILENAME).write_text(
        json.dumps(transaction), encoding="utf-8"
    )

    with pytest.raises(RuntimeError, match="artifact set is incomplete"):
        economics_module._recover_cost_artifact_transaction(run_dir)


def test_irene_trace_without_any_journal_fails_closed(tmp_path: Path) -> None:
    trial_id = "trace-no-journals"
    (tmp_path / trial_id).mkdir()
    report = _base_report(trial_id)
    object.__setattr__(
        report,
        "_trace_provider_attempts",
        (
            {
                "trace_run_id": "trace-only",
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 12,
                "output_tokens": 3,
                "cost_usd": 0.001,
            },
        ),
    )

    with pytest.raises(RuntimeError, match="without durable journals"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_unknown_cost_cannot_report_under_budget_or_irene_drift(tmp_path: Path) -> None:
    trial_id = "unknown-cost-budget"
    run_dir = tmp_path / trial_id
    _identity_value, _resume = _begin_attempt(run_dir, trial_id)
    report = _base_report(trial_id)
    object.__setattr__(report, "_budget_usd", 1.0)
    object.__setattr__(
        report,
        "_economics_history",
        tuple(_base_report(f"p-{i}") for i in range(5)),
    )

    path = record_trial_cost_report(trial_id, report, runs_root=tmp_path)
    loaded = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    assert loaded.budget_status.state == "unknown-cost"
    assert loaded.drift_alerts == []


def test_report_rewrite_without_journals_removes_stale_attempt_ledger(tmp_path: Path) -> None:
    trial_id = "remove-stale-ledger"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": {"input_tokens": 12, "output_tokens": 3}},
    )
    record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    ledger = run_dir / ATTEMPT_LEDGER
    assert ledger.is_file()
    for journal in run_dir.glob("irene-pass1-call-*.v1.json"):
        journal.unlink()

    record_trial_cost_report(trial_id, _base_report(trial_id), runs_root=tmp_path)
    assert not ledger.exists()


def test_crossed_request_and_response_correlations_fail_closed(tmp_path: Path) -> None:
    trial_id = "crossed-correlations"
    run_dir = tmp_path / trial_id
    identity, resume = _begin_attempt(run_dir, trial_id)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={
            "usage_metadata": {"input_tokens": 12, "output_tokens": 3},
            "response_id": "response-journal",
        },
    )
    expected = round(
        load_pricing().compute_cost("gpt-5.4", input_tokens=12, output_tokens=3),
        8,
    )
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=1,
        input_tokens=12,
        output_tokens=3,
        cost_usd=expected,
    )
    object.__setattr__(
        report,
        "_trace_provider_attempts",
        (
            {
                "trace_run_id": "trace-crossed",
                "request_digest": identity["request_digest"],
                "response_id": "response-other",
                "agent_name": "irene_pass1",
                "model_id": "gpt-5.4",
                "input_tokens": 12,
                "output_tokens": 3,
                "cost_usd": expected,
            },
        ),
    )

    with pytest.raises(RuntimeError, match="identifiers conflict"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)


def test_irene_aggregate_without_journals_or_private_trace_fails_closed(
    tmp_path: Path,
) -> None:
    trial_id = "aggregate-no-journals"
    (tmp_path / trial_id).mkdir()
    report = _base_report(trial_id)
    report.per_agent_breakdown["irene_pass1"] = AgentCostEntry(
        agent_name="irene_pass1",
        model_assigned="gpt-5.4",
        call_count=1,
        input_tokens=12,
        output_tokens=3,
        cost_usd=0.001,
    )

    with pytest.raises(RuntimeError, match="without durable journals"):
        record_trial_cost_report(trial_id, report, runs_root=tmp_path)
