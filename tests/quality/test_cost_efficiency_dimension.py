"""Story Q2.1 — cost_efficiency signal readers + drift math + cross-dimensional
integration (hermetic + real). No live calls, no ``--run-live``.

The cost_efficiency dimension is scored from the EXISTING economics emitters (GL-15 —
reuse, no parallel plumbing): the budget-stop DEFAULT posture (``check_trial_budget`` /
``MARCUS_TRIAL_BUDGET_USD``), ``cost_posture``, per-agent drift
(``compute_per_agent_drift``), and cost transparency. This module covers:

  * the four readers against hermetic fixture ``TrialEconomicsReport``s (exact +
    lower-bound + drift-alert) AND real repo/env state;
  * the budget-stop reader env-INDEPENDENCE + the seeded on/off anti-drift (monkeypatch
    ``MARCUS_TRIAL_BUDGET_USD``) + the signal→level derivation;
  * the drift MATH pinned (a ≥50% per-call deviation vs a rolling median fires an alert);
  * the cross-dimensional GL-13 interleave (cost paid-walk leak among DID's) + the
    coverage guard clean on the real repo;
  * the deterministic projector picking up the new dimension with NO projector change.

The honesty-pin RED-under-seeded proofs (budget-fence-claim, cost leak-count + slug
identity, arithmetic) live in ``test_scorecard_honesty_pins.py`` (the registered pins).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.models.runtime.trial_economics_report import (
    AgentCostEntry,
    BudgetStatus,
    DriftAlert,
    TrialEconomicsReport,
)
from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import (
    _COST_KEY,
    _COVERAGE_KEY,
    _DID_KEY,
    _FIDELITY_KEY,
    read_scorecard_block,
)
from app.quality.signals import (
    budget_stop_default_signal,
    cost_drift_signal,
    cost_leak_count_signal,
    cost_posture_signal,
    cost_transparency_signal,
    level_from_signal,
)
from app.runtime.economics import check_trial_budget, compute_per_agent_drift

_SHA = "a" * 64
_BUDGET_ENV = "MARCUS_TRIAL_BUDGET_USD"
_CLEAN = {"strong", "uniform"}


# --------------------------------------------------------------------------- #
# Hermetic fixture builders (build real models — strict validation is the point).
# --------------------------------------------------------------------------- #
def _agent(cost_usd: float, call_count: int = 1) -> AgentCostEntry:
    return AgentCostEntry(
        agent_name="gary",
        model_assigned="gpt-5",
        call_count=call_count,
        input_tokens=100,
        output_tokens=100,
        cost_usd=cost_usd,
    )


def _report(
    *,
    trial_id: str = "t-fixture",
    gary_cost: float = 1.0,
    call_count: int = 1,
    posture: str = "exact",
    unavailable: int = 0,
    drift_alerts: list[DriftAlert] | None = None,
    budget_state: str = "no-cap",
) -> TrialEconomicsReport:
    return TrialEconomicsReport(
        trial_id=trial_id,
        measured_at=datetime(2026, 7, 19, 12, 0, tzinfo=UTC),
        total_cost_usd=gary_cost,
        per_agent_breakdown={"gary": _agent(gary_cost, call_count)},
        per_model_breakdown={"gpt-5": gary_cost},
        cascade_config_digest=_SHA,
        pricing_table_digest=_SHA,
        drift_alerts=drift_alerts or [],
        budget_status=BudgetStatus(state=budget_state, over_by_usd=0.0),
        cost_posture=posture,
        unavailable_attempt_count=unavailable,
    )


# =========================== CE1 — budget-stop default =========================== #


def test_budget_stop_default_is_opt_in_weak(monkeypatch: pytest.MonkeyPatch) -> None:
    """Real production-preset posture: no default budget → ``check_trial_budget(total,
    None)=='no-cap'`` → ``default_budget_enforced`` False → derived level ``weak``."""
    monkeypatch.delenv(_BUDGET_ENV, raising=False)
    sig = budget_stop_default_signal()
    assert sig["status"] == "ok"
    assert sig["default_budget_usd"] is None
    assert sig["budget_status_state"] == "no-cap"
    assert sig["default_budget_enforced"] is False
    assert level_from_signal("budget_stop_default_on", sig) == "weak"


def test_budget_stop_close_path_is_reader_reachable() -> None:
    """FIX-1 — the reader is NOT a hardcoded constant and the doc's close-path is
    REACHABLE: the reader delegates to the runtime budget SOURCE via an ``env`` mapping,
    so a clean env resolves ``None`` → ``weak`` (the preset default, today), while an env
    carrying a wired default budget resolves that cap → ``strong``. If the preset gains a
    default-budget source the resolver returns, CE1 legitimately earns strong (and pin
    (a) AGREES rather than false-REDs the operator who closes the leak)."""
    off = budget_stop_default_signal(env={})  # preset-default posture: no source → weak
    assert off["default_budget_enforced"] is False
    assert level_from_signal("budget_stop_default_on", off) == "weak"
    on = budget_stop_default_signal(env={_BUDGET_ENV: "50"})  # a wired default budget
    assert on["default_budget_usd"] == 50.0
    assert on["default_budget_enforced"] is True
    assert level_from_signal("budget_stop_default_on", on) == "strong"


def test_budget_stop_reader_is_read_only_no_env_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-6 — the reader NEVER mutates ``os.environ`` (the prior version popped/restored
    the key, perturbing concurrent runs). Calling it (any variant) leaves the ambient env
    byte-identical."""
    import os

    monkeypatch.setenv(_BUDGET_ENV, "7.5")
    before = dict(os.environ)
    budget_stop_default_signal()
    budget_stop_default_signal(env={})
    budget_stop_default_signal(default_budget_usd=3.0)
    assert dict(os.environ) == before
    assert os.environ[_BUDGET_ENV] == "7.5"  # untouched


def test_budget_stop_seeded_default_flips_to_strong() -> None:
    """Seeded-world proof: if a default budget WERE wired, the reader reports
    ``default_budget_enforced`` True → the derived level is ``strong`` (both under-budget
    and over-budget states enforce a real cap)."""
    for cap in (5.0, 0.5):  # under-budget and over-budget-warning both enforce
        sig = budget_stop_default_signal(default_budget_usd=cap)
        assert sig["default_budget_enforced"] is True
        assert level_from_signal("budget_stop_default_on", sig) == "strong"


def test_budget_stop_reader_tracks_real_check_trial_budget() -> None:
    """The reader's claim is grounded in the REAL ``check_trial_budget`` SSOT: None →
    no-cap; a set cap → an enforcing state. If that function changed, the reader would."""
    assert check_trial_budget(1.0, None).state == "no-cap"
    assert check_trial_budget(1.0, 5.0).state == "under-budget"
    assert check_trial_budget(1.0, 0.5).state == "over-budget-warning"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "default_budget_enforced": True}, "strong"),
        ({"status": "ok", "default_budget_enforced": False}, "weak"),
        ({"status": "ok", "default_budget_enforced": None}, "unavailable"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_ce_budget_total(sig: object, expected: str) -> None:
    got = level_from_signal("budget_stop_default_on", sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


# =========================== CE2 — cost_posture ================================= #


def test_cost_posture_exact_report() -> None:
    sig = cost_posture_signal(_report(posture="exact", unavailable=0))
    assert sig["status"] == "ok"
    assert sig["cost_posture"] == "exact"
    assert sig["is_exact"] is True and sig["is_lower_bound"] is False
    assert sig["unavailable_attempt_count"] == 0


def test_cost_posture_lower_bound_report_is_a_floor() -> None:
    rpt = _report(
        posture="known-lower-bound-with-explicit-unavailable-attempts", unavailable=2
    )
    sig = cost_posture_signal(rpt)
    assert sig["is_lower_bound"] is True and sig["is_exact"] is False
    assert sig["unavailable_attempt_count"] == 2


def test_cost_posture_reads_plain_json_path(tmp_path) -> None:
    """A run's ``cost-report.json`` is read as PLAIN JSON (no app import in app.quality)."""
    import json

    p = tmp_path / "cost-report.json"
    p.write_text(
        json.dumps({"cost_posture": "exact", "unavailable_attempt_count": 0}),
        encoding="utf-8",
    )
    sig = cost_posture_signal(str(p))
    assert sig["cost_posture"] == "exact" and sig["is_exact"] is True


def test_cost_posture_no_report_is_honest_marker() -> None:
    sig = cost_posture_signal(None)
    assert sig["status"] == "no-report"
    assert sig["cost_posture"] is None


def test_cost_posture_model_validator_forbids_dishonest_exact() -> None:
    """The posture cannot lie: the ``TrialEconomicsReport`` validator rejects ``exact``
    with unavailable attempts (so a lower-bound can never masquerade as exact)."""
    with pytest.raises(ValueError):
        _report(posture="exact", unavailable=3)


# =========================== CE3 — drift (math pinned) ========================= #


def test_cost_drift_monitoring_wired() -> None:
    sig = cost_drift_signal(None)
    assert sig["status"] == "ok"
    assert sig["drift_monitoring_wired"] is True
    assert sig["drift_alert_count"] is None  # no report supplied


def test_cost_drift_status_unavailable_when_monitor_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-4 RED-first: if ``compute_per_agent_drift`` cannot be imported (the monitor is
    absent), the reader must report ``status="unavailable"`` — NOT ``ok`` — so a consumer
    keying on ``status=="ok"`` never reads wiring-absent as healthy. Simulate the import
    failure by removing ``app.runtime.economics`` from ``sys.modules`` and blocking its
    re-import."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "app.runtime.economics", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.runtime.economics":
            raise ImportError("seeded: economics monitor unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = cost_drift_signal(None)
    assert sig["drift_monitoring_wired"] is False
    assert sig["status"] == "unavailable"


def test_cost_drift_signal_reports_alert_count() -> None:
    alert = DriftAlert(
        agent_name="gary",
        rolling_median_usd_per_call=1.0,
        observed_usd_per_call=2.0,
        deviation_pct=100.0,
    )
    sig = cost_drift_signal(_report(drift_alerts=[alert]))
    assert sig["drift_alert_count"] == 1


def test_drift_math_fires_on_50pct_deviation() -> None:
    """Pin the drift MATH: 5 history trials at $1.00/call establish a rolling median of
    1.0; a current trial at $2.00/call is a +100% deviation (≥50%) → a DriftAlert."""
    history = [_report(trial_id=f"h{i}", gary_cost=1.0) for i in range(5)]
    current = _report(trial_id="cur", gary_cost=2.0)
    alerts = compute_per_agent_drift(current, history)
    assert "gary" in alerts
    assert alerts["gary"].deviation_pct == pytest.approx(100.0)
    # and the reader surfaces that alert as a count of 1
    report_with_alert = _report(gary_cost=2.0, drift_alerts=list(alerts.values()))
    assert cost_drift_signal(report_with_alert)["drift_alert_count"] == 1


def test_drift_math_quiet_within_band() -> None:
    """A within-band deviation (<50%) does NOT fire — the monitor is honest, not noisy."""
    history = [_report(trial_id=f"h{i}", gary_cost=1.0) for i in range(5)]
    current = _report(trial_id="cur", gary_cost=1.2)  # +20% < 50%
    assert compute_per_agent_drift(current, history) == {}


# =========================== CE4 — cost transparency =========================== #


def test_cost_transparency_all_present_on_full_report() -> None:
    sig = cost_transparency_signal(_report())
    assert sig["status"] == "ok"
    assert sig["all_present"] is True
    assert all(sig["fields_present"].values())


def test_cost_transparency_flags_missing_digest() -> None:
    data = {
        "per_agent_breakdown": {"gary": {}},
        "per_model_breakdown": {"gpt-5": 1.0},
        "cascade_config_digest": "not-a-sha",
        "pricing_table_digest": _SHA,
    }
    sig = cost_transparency_signal(data)
    assert sig["all_present"] is False
    assert sig["fields_present"]["cascade_config_digest"] is False
    assert sig["fields_present"]["pricing_table_digest"] is True


def test_cost_transparency_reds_on_empty_breakdown() -> None:
    """FIX-3 RED-first: an EMPTY ``per_agent_breakdown={}`` / ``per_model_breakdown={}``
    is NOT a reproducible attestation — a report with no cost data must NOT claim
    ``all_present``. Empty dicts pass ``isinstance(dict)`` but must fail the non-empty
    requirement."""
    data = {
        "per_agent_breakdown": {},  # empty — no cost data
        "per_model_breakdown": {},  # empty
        "cascade_config_digest": _SHA,
        "pricing_table_digest": _SHA,
    }
    sig = cost_transparency_signal(data)
    assert sig["all_present"] is False
    assert sig["fields_present"]["per_agent_breakdown"] is False
    assert sig["fields_present"]["per_model_breakdown"] is False


def test_cost_transparency_accepts_uppercase_digest() -> None:
    """FIX-5: a valid UPPERCASE 64-hex digest must NOT read as absent (case-insensitive)."""
    data = {
        "per_agent_breakdown": {"gary": {}},
        "per_model_breakdown": {"gpt-5": 1.0},
        "cascade_config_digest": ("A" * 64),  # uppercase hex — still valid
        "pricing_table_digest": ("a" * 64),
    }
    sig = cost_transparency_signal(data)
    assert sig["fields_present"]["cascade_config_digest"] is True
    assert sig["all_present"] is True


def test_cost_transparency_no_report_marker() -> None:
    sig = cost_transparency_signal(None)
    assert sig["status"] == "no-report"
    assert sig["all_present"] is None


# =========================== leak-count reader ================================= #


def test_cost_leak_count_real_repo_is_one() -> None:
    sig = cost_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["cost_leak_count"] == 1


def test_cost_leak_count_fixture(tmp_path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Cost-Efficiency Scorecard Leak Registry\n\n"
        "- cost_leak: alpha\n- cost_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- cost_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert cost_leak_count_signal(p)["cost_leak_count"] == 2


# =========================== GL-13 cross-dimensional =========================== #


def test_cost_leak_is_lane_grouped_among_did_paid_walk_leaks() -> None:
    """GL-13 (FIX-8 — assertion sharpened to match the claim): the cost_efficiency
    paid-walk leak aggregates into the ONE shared ranked list and is LANE-GROUPED with
    DID's paid-walk leaks — i.e. the cost leak sits INSIDE the contiguous paid-walk block
    (alongside the two DID paid-walk leaks) and ahead of every learner-trust/governance
    leak. This proves cross-dimensional lane grouping (not a per-dimension concatenation),
    which is the actual GL-13 aggregation contract."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    lanes = [e["lane"] for e in ranked]
    dims = [e["dimension"] for e in ranked]
    slugs = [e["slug"] for e in ranked]
    cost_slug = "cost-efficiency-budget-stop-opt-in-default-no-cap"
    assert cost_slug in slugs
    cost_idx = slugs.index(cost_slug)
    # the leading contiguous block is exactly the paid-walk lane...
    paid_block = [i for i, ln in enumerate(lanes) if ln == "paid-walk"]
    assert paid_block == list(range(len(paid_block))), "paid-walk leaks must be contiguous at front"
    # ...and it contains BOTH the cost leak AND DID paid-walk leaks (cross-dimensional).
    assert cost_idx in paid_block
    assert {dims[i] for i in paid_block} == {_COST_KEY, _DID_KEY}
    # every learner-trust / governance leak sorts strictly AFTER the paid-walk block.
    for i, ln in enumerate(lanes):
        if ln in ("learner-trust", "governance"):
            assert i > max(paid_block)
    # multiple dimensions contribute overall (cross-dimensional, not DID-only). Q2.2
    # added coverage_honesty as a THIRD contributor (a learner-trust leak); Q2.3 added
    # fidelity_trust as a FOURTH (also learner-trust); Q3.1 added capability_honesty as a
    # FIFTH (a governance leak); Q3.2 added tracker_coherence as a SIXTH (also governance).
    assert set(dims) == {
        _DID_KEY,
        _COST_KEY,
        _COVERAGE_KEY,
        _FIDELITY_KEY,
        "capability_honesty",
        "tracker_coherence",
    }


def test_leak_coverage_clean_with_cost_dimension() -> None:
    """The coverage guard stays clean: cost_efficiency declares open_leaks=1 AND carries
    a ``leaks`` list, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_cost_dimension_with_no_code_change() -> None:
    """AC5: ``render_scorecard_final_report`` picks up cost_efficiency automatically —
    its Band row, its per-criterion trace, its ranked leak, and its ▬ baseline trend all
    render with NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": True}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Cost-efficiency | B- |" in out
    assert "cost-efficiency-budget-stop-opt-in-default-no-cap" in out
    assert "| Cost-efficiency | ▬ baseline |" in out
    # the budget criterion trace row (weak, 1/4) is present.
    assert "| Cost-efficiency | budget_stop_default_on | weak | 1/4 |" in out
    assert "/100" not in out  # never a false-precise headline
