"""Error-pause + verdict-less recovery (S4 part 2, SCP 2026-06-11).

Amelia trap 1: a transient dispatch blip (Gamma outage, bridge hiccup)
previously unwound the entire walk — the operator paid a fresh cycle to
retry one node. These tests pin the conversion: a typed
SpecialistDispatchError pauses the run as ``paused-at-error`` with an
``error-pause.json`` record, and ``recover_production_trial`` re-enters the
walk AT the failed node (unshifted index) without an operator verdict.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.gamma_dispatch import GammaDispatchError
from app.specialists.texas._act import BundleDispatchError

TRIAL_ID = UUID("32345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")

# Real-shaped upstream outputs so the §06 builder (S3) has a valid data
# plane to compile from — mirrors the gate-pause suite's fixture.
_REAL_SHAPED_OUTPUTS: dict[str, dict] = {
    "irene_pass1": {
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
    },
    "cd": {"cd_directive": {"experience_profile": "text-led"}},
}


def _install_adapter(
    monkeypatch,
    *,
    fail_specialist: str | None = None,
    fail_times: int = 0,
    error: SpecialistDispatchError | None = None,
) -> dict[str, int]:
    """Install a strict-signature fake adapter that fails N dispatches.

    The failure budget lives in shared state so it survives the fresh
    adapter instantiation each walk performs — a recovery walk sees a
    healthy backend once the budget is exhausted, exactly like a transient
    outage clearing.
    """
    state = {"remaining": fail_times}

    class _Adapter:
        def invoke_specialist(
            self,
            *,
            specialist_id: str,
            envelope: ProductionEnvelope,
            dependency_map: dict[str, str],
            cost_usd: float,
            base_state=None,
            node_id: str | None = None,
            runner_supplied_payload: dict | None = None,
            projection_map: dict | None = None,
        ) -> ProductionEnvelope:
            del dependency_map, base_state, runner_supplied_payload, projection_map
            if specialist_id == fail_specialist and state["remaining"] > 0:
                state["remaining"] -= 1
                raise error or GammaDispatchError(
                    "synthetic transient outage", tag="gamma.input.missing"
                )
            updated = envelope.model_copy(deep=True)
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=specialist_id,
                    output=_REAL_SHAPED_OUTPUTS.get(
                        specialist_id, {"specialist_id": specialist_id}
                    ),
                    model_used="gpt-5-nano",
                    cost_usd=cost_usd,
                    node_id=node_id,
                )
            )
            return updated

    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)
    return state


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


def _start(tmp_path: Path, monkeypatch) -> production_runner.ProductionTrialEnvelope:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    return production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )


def _g1_verdict(tmp_path: Path) -> OperatorVerdict:
    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text()
    )
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=payload["digest"],
    )


def test_start_walk_dispatch_error_pauses_instead_of_dying(
    tmp_path: Path, monkeypatch
) -> None:
    _install_adapter(
        monkeypatch,
        fail_specialist="texas",
        fail_times=1,
        error=BundleDispatchError(
            "wrangler receipt unusable", tag="bundle.dispatch.input-missing"
        ),
    )

    envelope = _start(tmp_path, monkeypatch)

    assert envelope.status == "paused-at-error"
    assert envelope.paused_gate is None
    assert envelope.paused_error_tag == "bundle.dispatch.input-missing"
    error_pause = json.loads(
        (tmp_path / str(TRIAL_ID) / "error-pause.json").read_text(encoding="utf-8")
    )
    assert error_pause["specialist_id"] == "texas"
    assert error_pause["tag"] == "bundle.dispatch.input-missing"
    # Unshifted on purpose: recovery retries the failed node itself, unlike
    # the gate checkpoint's next_node_index (+1) past a decided gate.
    assert isinstance(error_pause["node_index"], int)
    persisted = production_runner.ProductionTrialEnvelope.model_validate_json(
        (tmp_path / str(TRIAL_ID) / "run.json").read_text(encoding="utf-8")
    )
    assert persisted.status == "paused-at-error"


def test_recover_continues_from_failed_node_to_g1(
    tmp_path: Path, monkeypatch
) -> None:
    _install_adapter(monkeypatch, fail_specialist="texas", fail_times=1)
    _start(tmp_path, monkeypatch)

    envelope = production_runner.recover_production_trial(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G1"
    # A subsequent (gate) pause clears the error tag.
    assert envelope.paused_error_tag is None
    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text()
    )
    assert card_payload["card"]["gate_id"] == "G1"
    # The failed node was retried, not skipped: texas now carries its
    # contribution at the node recorded in the error-pause.
    error_pause = json.loads(
        (tmp_path / str(TRIAL_ID) / "error-pause.json").read_text(encoding="utf-8")
    )
    assert (
        envelope.production_envelope.get_contribution(
            "texas", node_id=error_pause["node_id"]
        )
        is not None
    )


def test_resume_walk_error_pauses_then_recover_reaches_g2c(
    tmp_path: Path, monkeypatch
) -> None:
    """The Amelia-trap scenario end-to-end: healthy to G1, Gamma blips at
    §07 during the approved resume, recovery crosses to the G2C pause."""
    state = _install_adapter(monkeypatch, fail_specialist="gary", fail_times=1)
    paused = _start(tmp_path, monkeypatch)
    assert paused.status == "paused-at-gate"
    assert paused.paused_gate == "G1"
    assert state["remaining"] == 1  # gary not reached pre-G1

    errored = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_g1_verdict(tmp_path),
        runs_root=tmp_path,
    )
    assert errored.status == "paused-at-error"
    assert errored.paused_gate is None
    assert errored.paused_error_tag == "gamma.input.missing"
    error_pause = json.loads(
        (tmp_path / str(TRIAL_ID) / "error-pause.json").read_text(encoding="utf-8")
    )
    assert error_pause["specialist_id"] == "gary"
    assert error_pause["last_gate_crossed"] == "G1"

    recovered = production_runner.recover_production_trial(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )
    assert recovered.status == "paused-at-gate"
    # Arc 2 (2026-06-18): the gary error is at node 07 (precedes 07B); recovery
    # re-runs gary clean, then pauses at the woken G2B variant pick (07B-gate)
    # before G2C — was G2C before the wake.
    assert recovered.paused_gate == "G2B"
    assert recovered.paused_error_tag is None
    assert (
        recovered.production_envelope.get_contribution(
            "gary", node_id=error_pause["node_id"]
        )
        is not None
    )


def test_recover_refuses_gate_paused_run(tmp_path: Path, monkeypatch) -> None:
    _install_adapter(monkeypatch)
    paused = _start(tmp_path, monkeypatch)
    assert paused.status == "paused-at-gate"

    with pytest.raises(RuntimeError, match="not paused at a dispatch error"):
        production_runner.recover_production_trial(
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
        )


def test_resume_refuses_error_paused_run(tmp_path: Path, monkeypatch) -> None:
    _install_adapter(monkeypatch, fail_specialist="texas", fail_times=1)
    errored = _start(tmp_path, monkeypatch)
    assert errored.status == "paused-at-error"

    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID("42345678-1234-4234-8234-123456789abc"),
        operator_id="operator_test",
        decision_card_digest="a" * 64,
    )
    with pytest.raises(RuntimeError, match="not paused at a gate"):
        production_runner.resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=verdict,
            runs_root=tmp_path,
        )


def test_dispatch_error_family_shares_recoverable_base() -> None:
    """The runner catches the BASE — every S0 seam class must stay on it,
    or its failures regress to cycle death silently."""
    from app.specialists.kira.kling_dispatch import KlingDispatchError
    from app.specialists.quinn_r.sensory_bridges_dispatch import (
        SensoryBridgeDispatchError as QuinnRSensoryError,
    )
    from app.specialists.vera.sensory_bridges_dispatch import (
        SensoryBridgeDispatchError as VeraSensoryError,
    )
    from app.specialists.wanda.wondercraft_dispatch import WondercraftDispatchError

    for cls in (
        GammaDispatchError,
        BundleDispatchError,
        KlingDispatchError,
        VeraSensoryError,
        QuinnRSensoryError,
        WondercraftDispatchError,
    ):
        assert issubclass(cls, SpecialistDispatchError)
        instance = cls("boom", tag="x.y.z")
        assert instance.tag == "x.y.z"


def test_builder_node_error_pause_wraps_both_walkers() -> None:
    """WAVE-0 tranche 2 (2026-06-17, party-ratified): the §06 package builder
    is invoked at TWO call sites (start walker + resume/recover walker). Both
    must route a BuilderInputError into _pause_at_error under the dedicated
    ``package_builder`` identity, or a node-06 starvation regresses to cycle
    death on whichever sibling is left unwrapped (Amelia MUST: cover both
    sites; Murat: kill-the-mutant guard — drop a wrap and a count drops).

    §06 sits post-G1, so it is only behaviorally reachable on the resume/
    recover walker (pinned end-to-end in test_production_runner_gate_pause_
    resume.py::test_starved_resume_pauses_at_error_at_06_builder and
    ::test_broken_brief_pauses_at_error_not_quality_theater). This source pin
    guards the start-walker sibling that those black-box tests cannot reach,
    and pins Winston's identity axis at BOTH sites (the envelope must name
    package_builder, never the Marcus persona)."""
    source = inspect.getsource(production_runner)
    assert source.count("package_builders.run_builder_node(") == 2
    assert source.count("specialist_id=package_builders.BUILDER_SPECIALIST_ID") == 2


def test_single_shared_dispatch_call_site() -> None:
    """Winston d.2 ratchet: both walkers route dispatch through ONE call
    site (_dispatch_specialist_at_node). A second `adapter.invoke_specialist(`
    occurrence means the A23 fork pattern is back."""
    source = inspect.getsource(production_runner)
    assert source.count("adapter.invoke_specialist(") == 1
