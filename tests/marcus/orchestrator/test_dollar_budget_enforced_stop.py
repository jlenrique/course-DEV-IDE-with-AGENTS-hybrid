"""Story 41-4 — dollar-budget enforced stop (BOTH walks).

``MARCUS_TRIAL_BUDGET_USD`` was a SOFT-cap gauge: ``BudgetStatus``
(``app/models/runtime/trial_economics_report.py``) warned at cost-report time
but the walk never STOPPED. Story 41-3 removed the call-count throttle and
declared the interim in words — *"spend is bounded by the finite composed graph,
per-node idempotency, and human gate-pauses; there is NO early dollar cutoff
until the budget-enforcement follow-on lands."* This is that follow-on: the
dollar budget becomes a real economic BRAKE.

Enforcement is a SHARED chokepoint (both walks, adjacent to 41-2's
``_assert_specialist_dispatched_or_raise``): ``_assert_within_dollar_budget_or_raise``
runs PRE-spend (before a dispatch — don't spend the crossing call) and POST-spend
(after a dispatch — catch a single call that overshoots). ONE SOURCE OF TRUTH
(AC-3): the decision is ``check_trial_budget(accumulated, cap)`` — the identical
posture computation that produces the ``BudgetStatus`` in the trial economics
report, so the report and the brake agree by construction. The hard stop fires
exactly when that computation returns ``over-budget-warning`` (accumulated spend
has crossed the cap); the distinct tag is ``budget.exceeded`` (dollar), separate
from 41-2's ``dispatch.live-unavailable`` (keyless).

Harness (reuses the 41-2/41-3 pattern): the tests drive the SHARED continuation
walk (``_continue_production_walk``) and ``run_production_trial`` (the start leg)
directly against trimmed manifests with a fake ProductionDispatchAdapter that
stamps a per-specialist ``cost_usd`` onto each contribution. No live LLM, no
network. Contributions carry the deterministic builder-model marker so they
register no billable span (cost recording is stubbed and out of scope — the brake
reads the accumulated per-contribution ``cost_usd`` in the envelope, exactly as
the operator-surface cost reading does mid-walk).
"""

from __future__ import annotations

import inspect
import json
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.orchestrator import package_builders
from app.marcus.orchestrator import production_runner as pr
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.run_state import RunState
from app.runtime.economics import check_trial_budget

TRIAL = UUID("bc747b51-7009-4742-9f65-8de6abc29ca4")

_IRENE_OUTPUT = {
    "lesson_plan": {
        "plan_units": [
            {
                "unit_id": "PU-1",
                "title": "Unit",
                "learning_objective": "Objective",
                "scope_decision": "in-scope",
            }
        ]
    }
}
_CD_OUTPUT = {"cd_directive": {"experience_profile": "text-led"}}

# Three un-seeded specialist nodes (all in the dispatch registry) so accumulated
# spend can cross a cap MID-walk at a determinable "crossing node".
_MULTI_SPECIALIST_MANIFEST_YAML = textwrap.dedent(
    """
    schema_version: "1.0"
    lane: "run_graph"
    entrypoint: "4.75"
    frozen_graph_version: "v42"
    nodes:
      - id: "4.75"
        specialist_id: "cd"
      - id: "05"
        specialist_id: "vera"
      - id: "05B"
        specialist_id: "desmond"
    edges:
      - from: "__start__"
        to: "4.75"
      - from: "4.75"
        to: "05"
      - from: "05"
        to: "05B"
      - from: "05B"
        to: "__end__"
    """
).lstrip()

# A specialist-terminal walk (cd only) so "proceeding past cd" COMPLETES without
# dragging in the §06 package-builder plan-authority contract.
_CD_ONLY_MANIFEST_YAML = textwrap.dedent(
    """
    schema_version: "1.0"
    lane: "run_graph"
    entrypoint: "4.75"
    frozen_graph_version: "v42"
    nodes:
      - id: "4.75"
        specialist_id: "cd"
    edges:
      - from: "__start__"
        to: "4.75"
      - from: "4.75"
        to: "__end__"
    """
).lstrip()

# Two specialist nodes for the START-walk crossing (start walks begin with an
# empty envelope, so the second dispatch is where accumulated spend crosses).
_TWO_SPECIALIST_START_MANIFEST_YAML = textwrap.dedent(
    """
    schema_version: "1.0"
    lane: "run_graph"
    entrypoint: "4.75"
    frozen_graph_version: "v42"
    nodes:
      - id: "4.75"
        specialist_id: "cd"
      - id: "05"
        specialist_id: "vera"
    edges:
      - from: "__start__"
        to: "4.75"
      - from: "4.75"
        to: "05"
      - from: "05"
        to: "__end__"
    """
).lstrip()


def _make_costing_adapter(costs: dict[str, float], default: float = 0.0) -> type:
    """A fake ProductionDispatchAdapter that stamps a per-specialist ``cost_usd``.

    Records every dispatched specialist id on the class so the pre-spend pins can
    prove the crossing call was NOT spent (the adapter never saw it).
    """

    class _CostingAdapter:
        dispatched: list[str] = []

        def invoke_specialist(  # type: ignore[no-untyped-def]
            self,
            *,
            specialist_id: str,
            envelope: ProductionEnvelope,
            node_id: str | None = None,
            **kwargs,
        ) -> ProductionEnvelope:
            del kwargs
            type(self).dispatched.append(specialist_id)
            cost = costs.get(specialist_id, default)
            updated = envelope.model_copy(deep=True)
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=specialist_id,
                    output=_CD_OUTPUT
                    if specialist_id == "cd"
                    else {"specialist_id": specialist_id},
                    model_used=package_builders.BUILDER_MODEL_MARKER,
                    cost_usd=cost,
                    node_id=node_id,
                )
            )
            return updated

    _CostingAdapter.dispatched = []
    return _CostingAdapter


def _seed(
    envelope: ProductionEnvelope, *, specialist_id: str, output: dict, node_id: str, cost: float
) -> None:
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            output=output,
            model_used=package_builders.BUILDER_MODEL_MARKER,
            cost_usd=cost,
            node_id=node_id,
        )
    )


def _build_envelope(
    *, seed_irene_cost: float = 0.0
) -> tuple[pr.ProductionTrialEnvelope, RunState]:
    pe = ProductionEnvelope(trial_id=TRIAL, fixture_run=True)
    _seed(
        pe,
        specialist_id="irene_pass1",
        output=_IRENE_OUTPUT,
        node_id="04A",
        cost=seed_irene_cost,
    )
    rs = RunState(run_id=TRIAL, graph_version="v42")
    pte = pr.ProductionTrialEnvelope(
        trial_id=TRIAL,
        preset="production",
        corpus_path="corpus",
        operator_id="operator_test",
        started_at=datetime.now(UTC),
        status="paused-at-error",
        production_clone_launch_evidence=False,
        production_envelope=pe,
    )
    return pte, rs


def _drive_continuation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    budget: str | None,
    manifest_yaml: str,
    adapter_cls: type,
    seed_irene_cost: float = 0.0,
) -> pr.ProductionTrialEnvelope:
    """Drive the SHARED resume/recover walk (``_continue_production_walk``)."""
    (tmp_path / str(TRIAL)).mkdir(parents=True, exist_ok=True)
    mp = tmp_path / "manifest.yaml"
    mp.write_text(manifest_yaml, encoding="utf-8")
    pte, rs = _build_envelope(seed_irene_cost=seed_irene_cost)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    if budget is None:
        monkeypatch.delenv("MARCUS_TRIAL_BUDGET_USD", raising=False)
    else:
        monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", budget)
    # Deterministic builder-model contributions register no billable span; stub
    # cost recording (mirrors the 41-2/41-3 harness) — the brake reads the live
    # accumulated per-contribution cost_usd, not the persisted report.
    monkeypatch.setattr(
        pr, "_record_cost", lambda **_k: tmp_path / str(TRIAL) / "cost-report.json"
    )
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", adapter_cls)
    runner = {
        "allow_offline_cost_report": False,
        "manifest_path": mp.as_posix(),
        "preset": "production",
        "operator_id": "operator_test",
    }
    return pr._continue_production_walk(
        trial_id=TRIAL,
        envelope=pte,
        run_state=rs,
        runner=runner,
        manifest_path=mp,
        runs_root=tmp_path,
        start_index=0,
        last_gate_crossed="G1",
        max_specialist_calls=None,
    )


def _error_pause(tmp_path: Path, trial_id: UUID = TRIAL) -> dict:
    return json.loads(
        (tmp_path / str(trial_id) / "error-pause.json").read_text(encoding="utf-8")
    )


# --------------------------------------------------------------------------- #
# AC-1 — enforced stop at/over budget: pause-at-error `budget.exceeded` at the
# crossing node, in BOTH walks.
# --------------------------------------------------------------------------- #


def test_ac1_continuation_walk_pauses_budget_exceeded_at_crossing_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """cd (0.60) then vera (0.60) with cap 1.00: cd stays under (0.60); vera's
    dispatch overshoots (1.20 > 1.00) and the resume/recover walk PAUSES at node
    05 with ``budget.exceeded`` (accumulated $, cap $, node in the message) rather
    than continuing to spend on desmond."""
    adapter = _make_costing_adapter({"cd": 0.60, "vera": 0.60, "desmond": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="1.00",
        manifest_yaml=_MULTI_SPECIALIST_MANIFEST_YAML,
        adapter_cls=adapter,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_gate is None
    assert envelope.paused_error_tag == "budget.exceeded"

    ep = _error_pause(tmp_path)
    assert ep["node_id"] == "05"
    assert ep["specialist_id"] == "vera"
    assert ep["tag"] == "budget.exceeded"
    assert "05" in ep["message"]
    assert "1.20" in ep["message"] and "1.00" in ep["message"]
    # desmond (the third node) was NEVER spent — the brake stopped the walk.
    assert "desmond" not in adapter.dispatched
    assert (
        envelope.production_envelope.get_contribution("desmond", node_id="05B") is None
    )


def test_ac1_start_walk_pauses_budget_exceeded_at_crossing_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Start-walk parity: ``run_production_trial`` over cd (0.80) then vera (0.80)
    with cap 1.00 pauses at node 05 with ``budget.exceeded`` too. Preflight is
    stubbed green so the keyed production start walk reaches the specialist
    branch (41-1's front door is orthogonal)."""
    from types import SimpleNamespace

    start_trial = UUID("aaaaaaaa-1234-4234-8234-123456789abc")
    mp = tmp_path / "manifest.yaml"
    mp.write_text(_TWO_SPECIALIST_START_MANIFEST_YAML, encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", "1.00")
    monkeypatch.setattr(
        pr, "_record_cost", lambda **_k: tmp_path / str(start_trial) / "cost-report.json"
    )
    monkeypatch.setattr(
        pr, "ProductionDispatchAdapter", _make_costing_adapter({"cd": 0.80, "vera": 0.80})
    )
    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    envelope = pr.run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_test",
        trial_id=start_trial,
        runs_root=tmp_path,
        manifest_path=mp,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "budget.exceeded"
    ep = _error_pause(tmp_path, trial_id=start_trial)
    assert ep["node_id"] == "05"
    assert ep["specialist_id"] == "vera"
    assert ep["tag"] == "budget.exceeded"


def test_ac1_pre_spend_brake_does_not_spend_the_crossing_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PRE-spend stop (the preferred stop): when accumulated spend has ALREADY
    crossed the cap before a node, the walk pauses BEFORE dispatching it — the
    crossing call is never spent (the adapter never sees cd)."""
    adapter = _make_costing_adapter({"cd": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="1.00",
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        adapter_cls=adapter,
        seed_irene_cost=1.50,  # already over the 1.00 cap before cd is entered
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "budget.exceeded"
    ep = _error_pause(tmp_path)
    assert ep["node_id"] == "4.75"
    assert ep["specialist_id"] == "cd"
    # The crossing call was NOT spent: cd never reached the adapter, carries nothing.
    assert "cd" not in adapter.dispatched
    assert envelope.production_envelope.get_contribution("cd", node_id="4.75") is None


# --------------------------------------------------------------------------- #
# AC-2 — no-cap unchanged (back-compat): a no-cap run NEVER budget-pauses.
# --------------------------------------------------------------------------- #


def test_ac2_no_cap_never_budget_pauses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With ``MARCUS_TRIAL_BUDGET_USD`` unset, even a huge accumulated spend
    (5.00 per node) NEVER budget-pauses — behavior is exactly the 41-3 interim
    (finite graph + idempotency + gate-pauses remain the only bound). The walk
    completes with no error-pause and no budget tag."""
    adapter = _make_costing_adapter({"cd": 5.0, "vera": 5.0, "desmond": 5.0})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget=None,  # unset → no-cap
        manifest_yaml=_MULTI_SPECIALIST_MANIFEST_YAML,
        adapter_cls=adapter,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()
    # Every node dispatched — a no-cap run is not throttled by dollars.
    for specialist_id, node_id in (("cd", "4.75"), ("vera", "05"), ("desmond", "05B")):
        assert (
            envelope.production_envelope.get_contribution(specialist_id, node_id=node_id)
            is not None
        )


def test_ac2_no_cap_helper_never_raises_regardless_of_spend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unit pin: the shared brake helper is a strict no-op when no-cap/unset —
    it never raises no matter how large the accumulated spend."""
    monkeypatch.delenv("MARCUS_TRIAL_BUDGET_USD", raising=False)
    pe = ProductionEnvelope(trial_id=TRIAL, fixture_run=True)
    _seed(pe, specialist_id="cd", output=_CD_OUTPUT, node_id="4.75", cost=999.0)
    # Must not raise.
    pr._assert_within_dollar_budget_or_raise(
        production_envelope=pe, node_id="4.75", specialist_id="cd"
    )


# --------------------------------------------------------------------------- #
# AC-4 — resume-safe: raised cap continues; same cap re-pauses (no double spend).
# --------------------------------------------------------------------------- #


def test_ac4_resume_same_cap_repauses_no_double_spend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A resume that is still over the SAME cap re-pauses PRE-spend — the node is
    never re-dispatched, so there is no silent double-spend."""
    adapter = _make_costing_adapter({"cd": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="1.00",  # same cap the first pause used
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        adapter_cls=adapter,
        seed_irene_cost=1.50,  # persisted over-budget spend carried into the resume
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "budget.exceeded"
    assert "cd" not in adapter.dispatched  # not re-dispatched — no double spend


def test_ac4_resume_raised_cap_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A resume with a RAISED cap continues past the previously-blocking node and
    completes: 1.50 accumulated + cd (0.60) = 2.10 stays under the raised 5.00
    cap, so cd dispatches and the walk finishes cleanly."""
    adapter = _make_costing_adapter({"cd": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="5.00",  # raised
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        adapter_cls=adapter,
        seed_irene_cost=1.50,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()
    assert "cd" in adapter.dispatched
    assert (
        envelope.production_envelope.get_contribution("cd", node_id="4.75") is not None
    )


# --------------------------------------------------------------------------- #
# AC-3 — warn-band vs hard-stop boundary + report/brake agree (one SSOT).
# --------------------------------------------------------------------------- #


def test_ac3_at_cap_exactly_does_not_hard_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Boundary: accumulated spend EXACTLY at the cap is ``under-budget`` (the
    SSOT ``check_trial_budget`` uses ``running_total > cap``), so the walk does
    NOT hard-stop — cd (0.60) under a 0.60 cap completes."""
    adapter = _make_costing_adapter({"cd": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="0.60",  # exactly the accumulated spend after cd
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        adapter_cls=adapter,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()


def test_ac3_just_over_cap_hard_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Boundary: one cent over the cap (0.60 accumulated vs 0.59 cap) is
    ``over-budget-warning`` — the hard stop fires (``budget.exceeded``)."""
    adapter = _make_costing_adapter({"cd": 0.60})
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="0.59",
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        adapter_cls=adapter,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "budget.exceeded"
    ep = _error_pause(tmp_path)
    assert ep["node_id"] == "4.75"
    assert ep["specialist_id"] == "cd"


@pytest.mark.parametrize(
    ("accumulated", "cap"),
    [
        (0.0, 1.0),
        (0.5, 1.0),
        (1.0, 1.0),  # exactly at cap → under-budget → no brake
        (1.0000001, 1.0),  # just over → over-budget-warning → brake
        (1.5, 1.0),
        (2.0, 1.0),
        (0.0, 0.0),  # zero cap, zero spend → under-budget → no brake
        (0.01, 0.0),  # any spend over a zero cap → brake
    ],
)
def test_ac3_report_and_brake_agree_on_one_ssot(
    monkeypatch: pytest.MonkeyPatch, accumulated: float, cap: float
) -> None:
    """The brake raises IFF ``check_trial_budget(accumulated, cap)`` returns
    ``over-budget-warning`` — the report and the brake use ONE source of truth.
    Pinning the equivalence across the boundary proves the enforcement decision is
    not a re-derived, drift-prone second computation."""
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", repr(cap))
    pe = ProductionEnvelope(trial_id=TRIAL, fixture_run=True)
    _seed(pe, specialist_id="cd", output=_CD_OUTPUT, node_id="4.75", cost=accumulated)

    report_says_stop = check_trial_budget(accumulated, cap).state == "over-budget-warning"
    try:
        pr._assert_within_dollar_budget_or_raise(
            production_envelope=pe, node_id="4.75", specialist_id="cd"
        )
        brake_fired = False
    except pr.SpecialistDispatchError as exc:
        brake_fired = True
        assert exc.tag == "budget.exceeded"

    assert brake_fired == report_says_stop


# --------------------------------------------------------------------------- #
# AC-5 — distinct + aligned; two-walk parity (the shared brake in BOTH walks).
# --------------------------------------------------------------------------- #


def test_ac5_tag_is_distinct_from_dispatch_live_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The dollar brake's tag is ``budget.exceeded`` — distinct from 41-2's
    keyless ``dispatch.live-unavailable`` and from the retired 41-3 call-count
    ``dispatch.budget-exhausted``."""
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", "1.00")
    pe = ProductionEnvelope(trial_id=TRIAL, fixture_run=True)
    _seed(pe, specialist_id="cd", output=_CD_OUTPUT, node_id="4.75", cost=2.0)
    with pytest.raises(pr.SpecialistDispatchError) as excinfo:
        pr._assert_within_dollar_budget_or_raise(
            production_envelope=pe, node_id="4.75", specialist_id="cd"
        )
    assert excinfo.value.tag == "budget.exceeded"
    assert excinfo.value.tag != "dispatch.live-unavailable"
    assert excinfo.value.tag != "dispatch.budget-exhausted"


def test_ac5_shared_dollar_brake_invoked_in_both_walks() -> None:
    """The dollar brake is enforced through ONE shared helper called from BOTH
    node walks, at TWO points each (PRE-spend + POST-spend) — 1 definition + 4
    invocations = 5 occurrences. Drop a call site and this count drops:
    kill-the-mutant guard against the two-walk trap (mirrors the 41-2 pin)."""
    source = inspect.getsource(pr)
    assert source.count("_assert_within_dollar_budget_or_raise(") == 5
    assert source.count("def _assert_within_dollar_budget_or_raise(") == 1


# --------------------------------------------------------------------------- #
# AC-6 — operator-surface honest: the pause carries the "$X of $Y" message the
# existing error-pause → operator-surface path already surfaces.
# --------------------------------------------------------------------------- #


def test_ac6_pause_message_is_operator_honest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The persisted error-pause carries an actionable, operator-honest message
    (accumulated $, cap $, node) via the SAME error-pause channel 41-2 uses — no
    new leak, no bespoke surface."""
    adapter = _make_costing_adapter({"cd": 0.60, "vera": 0.60, "desmond": 0.60})
    _drive_continuation(
        tmp_path,
        monkeypatch,
        budget="1.00",
        manifest_yaml=_MULTI_SPECIALIST_MANIFEST_YAML,
        adapter_cls=adapter,
    )
    ep = _error_pause(tmp_path)
    assert ep["tag"] == "budget.exceeded"
    msg = ep["message"]
    assert "budget" in msg.lower()
    assert "1.20" in msg  # accumulated $
    assert "1.00" in msg  # cap $
    assert "05" in msg  # the crossing node
