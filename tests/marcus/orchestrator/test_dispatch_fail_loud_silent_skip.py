"""Story 41-2 + 41-3 — specialist-dispatch fail-loud + throttle removal (BOTH walks).

Binding invariant (Winston P-2, 41-2): in a production run
(``allow_offline_cost_report=False``) a specialist node that is ENTERED and is
NOT already-carrying its contribution MUST emit a contribution or FAIL LOUD at
that node. Silent advance is forbidden.

Root cause reproduced (trial ``bc747b51``): CD @ node ``4.75`` was entered but
never dispatched — ``max_specialist_calls=1`` was spent upstream (irene_pass1),
so CD was call-count-starved while live was fully available. The old specialist
branch set ``graph_step_completed = True`` UNCONDITIONALLY, so CD silently
no-opped and the failure MISATTRIBUTED three nodes later at §06 as
``builder.gary.upstream-missing``.

Story 41-3 (Option R — REMOVE the throttle, party 4/4): the call-count throttle
(``max_specialist_calls``) is the footgun that starved CD, so it is REMOVED. A
specialist node now dispatches whenever ``_has_live_openai() and not
allow_offline_cost_report`` — no per-call budget gate. ``dispatch.budget-exhausted``
is retired (nothing to fire on); ``dispatch.live-unavailable`` (keyless, a real
fail-loud) stays. ``max_specialist_calls`` is retained as an INERT ``None =
unbounded`` parameter (never re-defaults to 1 for production) purely as a
signature/test-injection seam — it no longer governs production dispatch. The
anti-starvation pins below prove EVERY specialist node dispatches (cd @ 4.75
included) with no cap in play; the idempotency pin proves the already-carrying
skip still blocks re-dispatch with the counter gone.

Harness note: these tests drive the SHARED continuation walk
(``_continue_production_walk``, the resume/recover leg) and ``run_production_trial``
(the start leg) directly against a mutated/trimmed copy of the ``bc747b51`` node
path (``4.75`` cd specialist → ``06`` gary package builder). No live LLM, no
network. Contributions are seeded with the deterministic builder-model marker so
they never register as billable LLM spans (keeps cost recording out of scope).
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

# The frozen RED-reproduction substrate. Hermetic tests below use mutated/trimmed
# copies of this shape; this path is only consulted (skip-if-absent) to pin the
# exact misattribution the fix eliminates.
FROZEN_RUN_DIR = Path(
    "state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4"
)

TRIAL = UUID("bc747b51-7009-4742-9f65-8de6abc29ca4")

# REAL-shaped irene_pass1 output so the §06 builder has a valid plane to compile
# from once CD is present — mirrors the gate-pause suite fixture.
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

# The bc747b51 node path, trimmed to the two nodes that carry the defect +
# misattribution: cd (specialist @ 4.75) then the gary package builder (§06,
# node_kind "orchestration", requires irene_pass1 + cd upstream).
_MANIFEST_YAML = textwrap.dedent(
    """
    schema_version: "1.0"
    lane: "run_graph"
    entrypoint: "4.75"
    frozen_graph_version: "v42"
    nodes:
      - id: "4.75"
        specialist_id: "cd"
      - id: "06"
        specialist_id: "marcus"
    edges:
      - from: "__start__"
        to: "4.75"
      - from: "4.75"
        to: "06"
      - from: "06"
        to: "__end__"
    """
).lstrip()


class _FakeAdapter:
    """Dispatches any specialist deterministically (no billable span, no network)."""

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict,
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict | None = None,
        projection_map: dict | None = None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state, runner_supplied_payload, projection_map
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=_CD_OUTPUT if specialist_id == "cd" else {"specialist_id": specialist_id},
                model_used=package_builders.BUILDER_MODEL_MARKER,
                cost_usd=0.0,
                node_id=node_id,
            )
        )
        return updated


class _SpyAdapter(_FakeAdapter):
    """Records every specialist_id it actually dispatches (order-preserving).

    Story 41-3 idempotency pin: prove the already-carrying per-node skip fires
    BEFORE dispatch even with the call-count counter gone — a pre-seeded node is
    never handed to the adapter, so its id never lands in ``dispatched``.
    """

    dispatched: list[str] = []

    def invoke_specialist(self, *, specialist_id: str, **kwargs):  # type: ignore[override]
        type(self).dispatched.append(specialist_id)
        return super().invoke_specialist(specialist_id=specialist_id, **kwargs)


# Full-composed-walk anti-starvation substrate: THREE un-seeded specialist nodes
# (all in the dispatch registry). Under the OLD throttle (cap=1) only the first
# would dispatch; the 2nd/3rd starved. Post-41-3 all three dispatch — no cap.
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


def _write_manifest(tmp_path: Path) -> Path:
    mp = tmp_path / "manifest.yaml"
    mp.write_text(_MANIFEST_YAML, encoding="utf-8")
    return mp


def _seed_contribution(
    envelope: ProductionEnvelope, *, specialist_id: str, output: dict, node_id: str
) -> None:
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            output=output,
            # deterministic marker → excluded from continuation child_runs, so a
            # seeded upstream never trips cost recording (out of scope here).
            model_used=package_builders.BUILDER_MODEL_MARKER,
            cost_usd=0.0,
            node_id=node_id,
        )
    )


def _build_envelope(*, seed_cd: bool = False) -> tuple[pr.ProductionTrialEnvelope, RunState]:
    pe = ProductionEnvelope(trial_id=TRIAL, fixture_run=True)
    # irene_pass1 already carried (as in the frozen run — only cd was missing @06).
    _seed_contribution(pe, specialist_id="irene_pass1", output=_IRENE_OUTPUT, node_id="04A")
    if seed_cd:
        _seed_contribution(pe, specialist_id="cd", output=_CD_OUTPUT, node_id="4.75")
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


# cd-only manifest: a specialist-terminal walk so "proceeding past cd" COMPLETES
# without dragging in the §06 package-builder's plan-authority contract (out of
# scope for the anti-starvation pins — those test dispatch, not §06 builder input).
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


def _drive_continuation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    live: bool,
    allow_offline: bool,
    max_specialist_calls: int | None,
    seed_cd: bool = False,
    adapter_cls: type = _FakeAdapter,
    manifest_yaml: str = _MANIFEST_YAML,
    stub_cost: bool = False,
) -> pr.ProductionTrialEnvelope:
    """Drive the SHARED resume/recover walk (``_continue_production_walk``)."""
    (tmp_path / str(TRIAL)).mkdir(parents=True, exist_ok=True)
    mp = tmp_path / "manifest.yaml"
    mp.write_text(manifest_yaml, encoding="utf-8")
    pte, rs = _build_envelope(seed_cd=seed_cd)
    if live:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    else:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    if stub_cost:
        # A completing LIVE walk records cost; the deterministic builder-model
        # marker registers no billable span, so stub cost recording (mirrors the
        # gate-pause integration suite) — cost paths are out of scope here.
        monkeypatch.setattr(
            pr, "_record_cost", lambda **_k: tmp_path / str(TRIAL) / "cost-report.json"
        )
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", adapter_cls)
    runner = {
        "allow_offline_cost_report": allow_offline,
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
        max_specialist_calls=max_specialist_calls,
    )


def _error_pause(tmp_path: Path) -> dict:
    return json.loads(
        (tmp_path / str(TRIAL) / "error-pause.json").read_text(encoding="utf-8")
    )


# --------------------------------------------------------------------------- #
# Frozen-run evidence: pin the exact misattribution the fix eliminates.
# --------------------------------------------------------------------------- #


def test_frozen_bc747b51_documents_the_misattribution_being_fixed() -> None:
    """The frozen error-pause halted at §06 (``builder.gary.upstream-missing``)
    three nodes past the real cause (CD @ 4.75). This test documents the buggy
    contract the behavioral tests below supersede."""
    ep_path = FROZEN_RUN_DIR / "error-pause.json"
    if not ep_path.exists():
        pytest.skip(f"frozen run dir absent: {ep_path}")
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    # The misattribution: the run paused at §06 naming the builder, not at 4.75
    # naming cd. 41-2 moves the honest stop back to the node.
    assert ep["node_id"] == "06"
    assert ep["tag"] == "builder.gary.upstream-missing"
    assert ep["specialist_id"] == "package_builder"
    assert "cd" in ep["message"]
    assert ep["runner"]["allow_offline_cost_report"] is False


# --------------------------------------------------------------------------- #
# AC-3 (BLOCKING) — resume/recover walk, keyless: fail loud AT 4.75.
# --------------------------------------------------------------------------- #


def test_ac3_resume_keyless_fails_loud_at_475_not_06(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED against the pre-41-2 code (CD silently advanced, no fail-loud);
    GREEN after: the keyless resume/recover walk over the bc747b51 shape halts
    AT 4.75 with ``dispatch.live-unavailable`` (cd) — NOT at 06 with
    ``builder.gary.upstream-missing``."""
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=False,
        allow_offline=False,
        max_specialist_calls=1,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_gate is None
    assert envelope.paused_error_tag == "dispatch.live-unavailable"

    ep = _error_pause(tmp_path)
    assert ep["node_id"] == "4.75"
    assert ep["specialist_id"] == "cd"
    assert ep["tag"] == "dispatch.live-unavailable"
    # The misattribution is gone: the run never reached §06.
    assert ep["tag"] != "builder.gary.upstream-missing"
    assert ep["node_id"] != "06"
    assert "cd" in ep["message"] and "4.75" in ep["message"]


# --------------------------------------------------------------------------- #
# AC-2 — the SAME fail-loud lands in the START walk (run_production_trial).
# --------------------------------------------------------------------------- #


def test_ac2_start_walk_fails_loud_at_475(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Start-walk parity: ``run_production_trial`` fails loud at the cd node too.
    Preflight is stubbed green so the keyless production start walk reaches the
    specialist branch (the preflight abort is 41-1's front door, orthogonal)."""
    from types import SimpleNamespace

    mp = tmp_path / "manifest.yaml"
    mp.write_text(
        textwrap.dedent(
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
        ).lstrip(),
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", _FakeAdapter)
    monkeypatch.setattr(
        pr,
        "_run_start_preflight_gate",
        lambda *a, **k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    envelope = pr.run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_test",
        trial_id=UUID("aaaaaaaa-1234-4234-8234-123456789abc"),
        runs_root=tmp_path,
        manifest_path=mp,
        max_specialist_calls=1,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "dispatch.live-unavailable"
    ep = json.loads(
        (tmp_path / "aaaaaaaa-1234-4234-8234-123456789abc" / "error-pause.json").read_text(
            encoding="utf-8"
        )
    )
    assert ep["node_id"] == "4.75"
    assert ep["specialist_id"] == "cd"


# --------------------------------------------------------------------------- #
# M-1 pin (1) — ANTI-STARVATION: the throttle is gone; CD @ 4.75 always dispatches.
# (Repurposed from 41-2's retired ``test_ac6_budget_exhausted_*``: budget-exhausted
#  can no longer fire — it was the footgun 41-3 removes.)
# --------------------------------------------------------------------------- #


def test_no_starvation_cd_dispatches_even_when_cap_would_have_starved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The EXACT bc747b51 cause is gone. Under 41-2, live present +
    ``max_specialist_calls=0`` budget-starved CD @ 4.75 and failed loud with
    ``dispatch.budget-exhausted``. Post-41-3 the call-count throttle is inert, so
    the *same* cap value CANNOT starve: CD dispatches, carries its contribution,
    and the walk completes with NO error-pause and NO budget-exhausted tag."""
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=True,
        allow_offline=False,
        max_specialist_calls=0,  # the value that USED to starve — now inert
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        stub_cost=True,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()
    # CD @ 4.75 dispatched (the headline: the starvation cause is eliminated).
    assert (
        envelope.production_envelope.get_contribution("cd", node_id="4.75") is not None
    )


def test_no_starvation_every_specialist_dispatches_uncapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M-1 pin (1) headline — a full composed walk over THREE un-seeded specialist
    nodes (cd/vera/desmond) dispatches EVERY one with no cap in play. Under the
    old cap=1 throttle only the first dispatched and the rest starved; post-41-3
    all three carry their contributions and the walk completes cleanly."""
    (tmp_path / str(TRIAL)).mkdir(parents=True, exist_ok=True)
    mp = tmp_path / "manifest.yaml"
    mp.write_text(_MULTI_SPECIALIST_MANIFEST_YAML, encoding="utf-8")
    pte, rs = _build_envelope()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # A completing LIVE walk records cost; the deterministic builder-model marker
    # registers no billable span, so stub cost recording (out of scope here).
    monkeypatch.setattr(
        pr, "_record_cost", lambda **_k: tmp_path / str(TRIAL) / "cost-report.json"
    )
    monkeypatch.setattr(pr, "ProductionDispatchAdapter", _FakeAdapter)
    runner = {
        "allow_offline_cost_report": False,
        "manifest_path": mp.as_posix(),
        "preset": "production",
        "operator_id": "operator_test",
    }
    envelope = pr._continue_production_walk(
        trial_id=TRIAL,
        envelope=pte,
        run_state=rs,
        runner=runner,
        manifest_path=mp,
        runs_root=tmp_path,
        start_index=0,
        last_gate_crossed="G1",
        max_specialist_calls=None,  # unbounded — the production default
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()
    # EVERY specialist node dispatched — none starved for a call-count reason.
    for specialist_id, node_id in (("cd", "4.75"), ("vera", "05"), ("desmond", "05B")):
        assert (
            envelope.production_envelope.get_contribution(specialist_id, node_id=node_id)
            is not None
        ), f"{specialist_id} @ {node_id} was starved — throttle removal regressed"


# --------------------------------------------------------------------------- #
# M-1 pin (2) — idempotency STILL holds with the call-count counter gone.
# (AC-2 of 41-3: the already-carrying per-node skip is the loop protection that
#  lets the throttle go — a node that carries its contribution never re-dispatches.)
# --------------------------------------------------------------------------- #


def test_ac4_idempotent_resume_preserved_no_raise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A resume where 4.75 ALREADY carries its cd contribution advances past it
    cleanly (no raise) even keyless — the S2 per-node idempotency skip is
    untouched by the throttle removal."""
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=False,
        allow_offline=False,
        max_specialist_calls=1,
        seed_cd=True,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()
    # cd contribution survived the walk (never re-dispatched, never dropped).
    assert (
        envelope.production_envelope.get_contribution("cd", node_id="4.75") is not None
    )


def test_idempotency_blocks_redispatch_even_live_with_counter_gone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M-1 pin (2) headline — with the call-count counter removed, a node that
    ALREADY carries its contribution is still NOT re-dispatched. Live is present
    (dispatch WOULD fire on an un-carried node), cd is pre-seeded, and a spy
    adapter records every dispatch. cd never reaches the adapter — the per-node
    idempotency skip fires first — so there is no dispatch loop without the
    counter (the loop-protection the throttle removal relies on)."""
    _SpyAdapter.dispatched = []
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=True,
        allow_offline=False,
        max_specialist_calls=None,  # unbounded — dispatch is gated only by carry
        seed_cd=True,
        adapter_cls=_SpyAdapter,
        manifest_yaml=_CD_ONLY_MANIFEST_YAML,
        stub_cost=True,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    # cd was pre-carried → the idempotency skip fired BEFORE dispatch: the spy
    # never saw cd (no re-dispatch, no loop) even though live was available.
    assert "cd" not in _SpyAdapter.dispatched
    assert (
        envelope.production_envelope.get_contribution("cd", node_id="4.75") is not None
    )


# --------------------------------------------------------------------------- #
# AC-5 — offline harness preserved: no raise when allow_offline_cost_report=True.
# --------------------------------------------------------------------------- #


def test_ac5_offline_harness_skips_without_raise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With ``allow_offline_cost_report=True`` a specialist node still skips
    dispatch WITHOUT raising — the fail-loud is strictly gated on
    ``not allow_offline_cost_report`` (offline reports never dispatch live)."""
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=False,
        allow_offline=True,
        max_specialist_calls=1,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None
    assert not (tmp_path / str(TRIAL) / "error-pause.json").exists()


def test_ac5_offline_skips_without_raise_regardless_of_max_specialist_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Offline never raises regardless of the (now-inert) ``max_specialist_calls``
    — the offline dispatch-skip is the one untouched exception to the fail-loud
    (Scope Fence). Passing the formerly-starving cap=0 changes nothing offline."""
    envelope = _drive_continuation(
        tmp_path,
        monkeypatch,
        live=False,
        allow_offline=True,
        max_specialist_calls=0,
    )
    assert envelope.status == "completed"
    assert envelope.paused_error_tag is None


# --------------------------------------------------------------------------- #
# Two-walk parity — the shared guard is invoked in BOTH walks (cannot drift).
# --------------------------------------------------------------------------- #


def test_shared_guard_invoked_in_both_walks() -> None:
    """The fail-loud invariant is enforced through ONE shared helper called from
    BOTH node walks (start + resume/recover), mirroring the existing
    two-walk-parity source pins (Yui/Winston). Drop a call site and this count
    drops — kill-the-mutant guard against the two-walk trap."""
    source = inspect.getsource(pr)
    assert source.count("_assert_specialist_dispatched_or_raise(") == 3  # defn + 2 calls
    # Exactly two INVOCATIONS (one per walk), plus the single definition.
    assert source.count("def _assert_specialist_dispatched_or_raise(") == 1
