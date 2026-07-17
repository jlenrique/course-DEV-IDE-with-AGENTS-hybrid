from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.gates.errors import GateError
from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a.2 — file-corpus dormant-path migration (D-kill-switch pin).

    These walks pass a README FILE as ``corpus_path`` and first-pause at G1 on the
    dormant path. The 3b default flip wakes G0-enrichment's corpus-DIRECTORY
    enumeration, which crashes pre-gate with ``DirectiveCompositionError`` on a file
    corpus. Pinning ``MARCUS_G0_ENRICHMENT_ACTIVE`` OFF explicitly preserves the
    enrichment-orthogonal downstream subject under the flip (explicit ``"0"`` survives
    the code-default flip). TEST-ONLY: no production/default change.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


# Minimal REAL-shaped upstream outputs: since S3 the resume walk executes
# the §06 package builder, which fail-louds (correctly) if irene_pass1/cd
# contributions are absent or shapeless. The pause-machinery tests need a
# valid data plane to walk through, not just any contributions.
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


class _FakeAdapter:
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


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


def _pause(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    return production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        # Open throttle: with the default cap of 1, the resume walk reaches
        # the §06 builder without a cd contribution and fail-louds (the
        # finding-#8 starvation class made visible by S3 — correct behavior,
        # wrong fixture for testing pause machinery).
        max_specialist_calls=12,
    )


def _verdict(tmp_path: Path, verb: str, *, gate_id: str = "G1", **overrides) -> OperatorVerdict:
    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / f"decision-card-{gate_id}.json").read_text()
    )
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb=verb,
        gate_id=gate_id,
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=overrides.pop("digest", payload["digest"]),
        **overrides,
    )


def test_cap_that_used_to_starve_cd_now_dispatches_it_on_resume(
    tmp_path: Path, monkeypatch
) -> None:
    """Story 41-3 — the bc747b51 STARVATION is removed (Option R, party 4/4).

    Durable regression pin, repurposed from 41-2's retired
    ``test_starved_resume_fails_loud_budget_exhausted_at_cd_node``. Trial
    bc747b51 ran with ``max_specialist_calls=1`` (spent upstream by irene_pass1),
    which STARVED CD @ node 4.75 — the call-count throttle footgun. 41-2 made that
    starvation fail loud at 4.75 with ``dispatch.budget-exhausted``; 41-3 REMOVES
    the throttle entirely, so that tag can no longer fire and the *same* cap value
    that used to starve CD now dispatches it.

    The contract this test now pins: a resume passing the formerly-starving
    ``max_specialist_calls=1`` no longer starves CD — CD DISPATCHES, carries its
    contribution at node 4.75, and the walk ADVANCES PAST 4.75. No
    ``dispatch.budget-exhausted`` error-pause is ever written, and the run never
    halts AT 4.75 for a call-count reason. This is the durable "cd is no longer
    starved on resume" signal: if the throttle ever returned, cd would starve at
    4.75 and these assertions would flip.

    (The walk advances into the §06 package builder, which — with the fake
    adapter that writes no live Pass-1 plan-authority receipt — pauses on its own
    input contract three nodes past cd. That downstream pause is a receipt-less-
    fixture artifact, NOT starvation: the anti-starvation contract is that cd
    dispatched and the walk left 4.75, asserted directly below. Preflight + cost
    recording are stubbed so this pins the walk contract in the sandbox, exactly
    as the fake-adapter behavioral suites do.)
    """
    monkeypatch.setattr(
        production_runner,
        "_run_start_preflight_gate",
        lambda *_a, **_k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(
        production_runner,
        "_record_cost",
        lambda **_k: tmp_path / str(TRIAL_ID) / "cost-report.json",
    )
    _pause(tmp_path, monkeypatch)

    # Resume passing the cap value (1) that STARVED CD pre-41-3. The throttle is
    # gone, so it is inert: CD dispatches and the walk advances past 4.75.
    resumed = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    # (1) CD @ 4.75 dispatched — the starvation cause is eliminated at the source.
    assert (
        resumed.production_envelope.get_contribution("cd", node_id="4.75") is not None
    )
    # (2) The retired budget tag never fires anywhere.
    assert resumed.paused_error_tag != "dispatch.budget-exhausted"
    # (3) The run did NOT halt AT 4.75 for a call-count reason — it advanced past
    # cd. (Any pause is downstream of 4.75; here the receipt-less §06 builder.)
    error_pause_path = tmp_path / str(TRIAL_ID) / "error-pause.json"
    if error_pause_path.exists():
        error_pause = json.loads(error_pause_path.read_text(encoding="utf-8"))
        assert error_pause["node_id"] != "4.75"
        assert error_pause["tag"] != "dispatch.budget-exhausted"


def test_approve_verdict_resumes_execution_then_pauses_at_g2b(
    tmp_path: Path, monkeypatch
) -> None:
    """Resume after G1 verdict executes specialist nodes, then PAUSES at G2B.

    Arc 2 (2026-06-18) woke the variant-pick gate G2B (07B-gate), which sits
    AFTER node 07B (quinn-r variant eval) and BEFORE G2C (07C storyboard-A). So
    the first gate the resume reaches after G1 is now G2B, not G2C — the woken
    variant pick. (Multi-gate pause-and-resume mechanism implemented 2026-06-11
    Trial-3 attempt-3 defect #5; the former GateBypassError raise was converted
    to the shared `_pause_at_gate` pause — silent bypass remains impossible
    because an undecided gate pauses with a registered DecisionCard, and decided
    gates are never revisited.)
    """
    _pause(tmp_path, monkeypatch)

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2B"
    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G2B.json").read_text()
    )
    assert card_payload["card"]["gate_id"] == "G2B"
    assert len(card_payload["digest"]) == 64


def test_g2c_pause_invokes_online_storyboard_publisher(
    tmp_path: Path, monkeypatch, storyboard_publish_calls
) -> None:
    """S5 criterion 7 wiring pin (operator-ratified 2026-06-12): the live
    G2C pause publishes the ONLINE storyboard BEFORE issuing the decision
    card — the review surface is part of reaching the gate.

    Arc 2 (2026-06-18): the woken G2B variant-pick now pauses before G2C, so
    reaching G2C takes an extra resume hop (approve G1 → pause G2B → approve
    G2B → pause G2C). G2B is intentionally NOT a storyboard gate (pinned in
    test_storyboard_publisher_skips_non_storyboard_gates)."""
    _pause(tmp_path, monkeypatch)
    # Hop 1: approve G1 → pauses at the woken G2B variant pick.
    paused_g2b = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )
    assert paused_g2b.paused_gate == "G2B"
    # Hop 2: approve G2B → pauses at G2C (storyboard publishes here).
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve", gate_id="G2B"),
        runs_root=tmp_path,
    )
    gate_ids = [call["gate_id"] for call in storyboard_publish_calls]
    assert "G2C" in gate_ids
    g2c_call = next(c for c in storyboard_publish_calls if c["gate_id"] == "G2C")
    assert g2c_call["trial_id"] == str(TRIAL_ID)


def test_content_error_pauses_recoverably_and_persists_progress(
    tmp_path: Path, monkeypatch
) -> None:
    """PIN-AUD-3P (audio-arc 2026-06-12): cycle-5's CoverageGapError was a
    bare ValueError — process CRASH, nodes 10-12 progress lost. Re-based to
    the dispatch family, a content error now (a) error-pauses instead of
    crashing, (b) PERSISTS the contributions completed before the failure,
    and (c) `trial recover` re-enters at the failed node and continues."""
    from app.specialists.quinn_r.quality_control_dispatch import CoverageGapError

    failing = {"on": True}

    class _ContentErrorAdapter(_FakeAdapter):
        def invoke_specialist(self, *, specialist_id: str, **kwargs):
            if specialist_id == "gary" and failing["on"]:
                raise CoverageGapError("missing narration coverage: ['s9']")
            return super().invoke_specialist(specialist_id=specialist_id, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", _ContentErrorAdapter
    )
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )
    assert envelope.status == "paused-at-error"
    assert envelope.paused_error_tag == "quinn_r.g5.coverage-gap"
    persisted = {
        c.node_id for c in envelope.production_envelope.contributions
    }
    assert {"04A", "4.75", "05", "05B", "06"}.issubset(persisted), (
        "progress completed before the content error was lost — the "
        "cycle-5 crash class"
    )
    failing["on"] = False
    recovered = production_runner.recover_production_trial(
        trial_id=TRIAL_ID, runs_root=tmp_path
    )
    assert recovered.status == "paused-at-gate"
    # Arc 2 (2026-06-18): the content error is at node 07B (first quinn_r after
    # §06); recovery re-runs it clean and pauses at the woken G2B variant pick
    # (which precedes G2C) — was G2C before the wake.
    assert recovered.paused_gate == "G2B"


def test_broken_brief_pauses_at_error_not_quality_theater(
    tmp_path: Path, monkeypatch, storyboard_publish_calls
) -> None:
    """S5 criterion 5 (negative test, party consensus 2026-06-12 — Murat/John;
    halt mechanism migrated crash→error-pause WAVE-0 tranche 2, party-ratified
    2026-06-17 Winston/Murat/John).

    A BROKEN brief upstream of the storyboard gate must make the run FAIL —
    halting AT §06 — and must NEVER pause at G2C for approval over hollow
    content, and the online storyboard must NEVER publish. The anti-quality-
    theater core (no G2C card, no publish) is asserted VERBATIM; only the halt
    transport changed from a propagating raise to a recoverable error-pause.
    The fixture corrupts the lesson plan to the shape the §06 builder refuses
    (plan_units empty → builder.gary.lesson-plan-shape)."""

    class _BrokenBriefAdapter(_FakeAdapter):
        def invoke_specialist(self, *, specialist_id: str, **kwargs):
            if specialist_id == "irene_pass1":
                envelope = kwargs["envelope"].model_copy(deep=True)
                envelope.add_contribution(
                    SpecialistContribution.from_output(
                        specialist_id=specialist_id,
                        output={"lesson_plan": {"plan_units": []}},
                        model_used="gpt-5-nano",
                        cost_usd=kwargs["cost_usd"],
                        node_id=kwargs.get("node_id"),
                    )
                )
                return envelope
            return super().invoke_specialist(specialist_id=specialist_id, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", _BrokenBriefAdapter
    )
    # No exception escapes — the §06 wrap converts the broken-brief refusal to
    # a recoverable error-pause (was: a propagating BuilderInputError that
    # killed the cycle). The anti-theater guarantees below are asserted
    # verbatim — the halt still occurs strictly before G2C.
    errored = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )
    assert errored.status == "paused-at-error"
    # The theater door (paused-at-gate over hollow content) is explicitly
    # closed — a refactor that let the broken brief reach an approvable gate
    # would flip this.
    assert errored.paused_gate is None
    assert errored.paused_error_tag == "builder.gary.lesson-plan-shape"
    error_pause = json.loads(
        (tmp_path / str(TRIAL_ID) / "error-pause.json").read_text(encoding="utf-8")
    )
    assert error_pause["specialist_id"] == "package_builder"
    assert error_pause["tag"] == "builder.gary.lesson-plan-shape"
    # --- S5-crit-5 anti-quality-theater core, PRESERVED VERBATIM (John binding
    #     condition 1): no gate over hollow content, no storyboard publish. ---
    assert not (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").exists(), (
        "gate opened over a broken brief — the attempt-4 quality-theater class"
    )
    assert all(c["gate_id"] != "G2C" for c in storyboard_publish_calls), (
        "storyboard published for a run that never legitimately reached G2C"
    )

    # Recover with the brief STILL broken must not be an escape hatch into the
    # gate: §06 re-pauses, no card opens, nothing publishes (Murat MUST-FIX —
    # the recover loop cannot silently degrade into gate-over-hollow-content).
    recovered = production_runner.recover_production_trial(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )
    assert recovered.status == "paused-at-error"
    assert recovered.paused_gate is None
    assert recovered.paused_error_tag == "builder.gary.lesson-plan-shape"
    assert not (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").exists()
    assert all(c["gate_id"] != "G2C" for c in storyboard_publish_calls)


def test_edit_verdict_propagates_to_resume_state(tmp_path: Path, monkeypatch) -> None:
    """Edit verdict's payload reaches resume state; the resume then pauses at
    the woken G2B variant pick (Arc 2 2026-06-18 — was G2C before the wake;
    multi-gate pause implemented 2026-06-11). The state mutation is verified via
    the resume-command.json artifact."""
    _pause(tmp_path, monkeypatch)
    edit_payload = {"slide_count": 3}

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "edit", edit_payload=edit_payload),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2B"
    command = json.loads((tmp_path / str(TRIAL_ID) / "resume-command.json").read_text())
    assert json.loads(command["run_state"]["cache_state"]["cache_prefix"]) == edit_payload


def test_g2b_operator_shim_resumes_the_paused_trial(tmp_path: Path, monkeypatch, capsys) -> None:
    """Murat P2 (2026-06-18): exercise the OPERATOR's actual entrypoint at a
    live G2B pause — g2b_shim.main(--verdict-file ...) → resume_production_trial
    → JSON payload. The shims were previously only smoke-tested at argparse
    level; this pins the load-verdict → trial-id-match → resume round-trip."""
    from app.marcus.cli.gate_shims import g2b_shim

    _pause(tmp_path, monkeypatch)
    # Approve G1 → the trial pauses at the woken G2B variant pick.
    paused = production_runner.resume_production_trial(
        trial_id=TRIAL_ID, verdict=_verdict(tmp_path, "approve"), runs_root=tmp_path
    )
    assert paused.paused_gate == "G2B"

    # The operator authors a G2B verdict file and runs the shim.
    verdict_file = tmp_path / "g2b-verdict.json"
    verdict_file.write_text(
        _verdict(tmp_path, "approve", gate_id="G2B").model_dump_json(), encoding="utf-8"
    )
    exit_code = g2b_shim.main(
        [
            "--trial-id",
            str(TRIAL_ID),
            "--verdict-file",
            str(verdict_file),
            "--runs-root",
            str(tmp_path),
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["gate_id"] == "G2B"
    assert payload["status"] in {"paused-at-gate", "completed"}
    assert payload["transport_kind"] == "cli"


def test_reject_verdict_halts_trial(tmp_path: Path, monkeypatch) -> None:
    _pause(tmp_path, monkeypatch)

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "reject", reject_reason="not acceptable"),
        runs_root=tmp_path,
    )

    assert envelope.status == "failed"


def test_digest_mismatch_refuses_resume(tmp_path: Path, monkeypatch) -> None:
    _pause(tmp_path, monkeypatch)

    with pytest.raises(GateError, match="digest_mismatch"):
        production_runner.resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=_verdict(tmp_path, "approve", digest="b" * 64),
            runs_root=tmp_path,
        )
