from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.gates.errors import GateError
from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


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


def _verdict(tmp_path: Path, verb: str, **overrides) -> OperatorVerdict:
    payload = json.loads((tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text())
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb=verb,
        gate_id="G1",
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=overrides.pop("digest", payload["digest"]),
        **overrides,
    )


def test_starved_resume_pauses_at_error_at_06_builder(
    tmp_path: Path, monkeypatch
) -> None:
    """Finding-#8 made flesh — intent preserved across a mechanism migration.

    Originally pinned as a crash (Murat + Amelia MUST-FIX, party review
    2026-06-12): a cap-starved resume reaching §06 without the cd contribution
    must REFUSE and must not silently re-feed the path. WAVE-0 tranche 2
    (party-ratified 2026-06-17, Winston/Murat/John) migrated the HALT MECHANISM
    crash→error-pause — the contract is unchanged: the refusal is non-silent
    (tagged), halts AT §06, and opens no gate. The original 'no refactor
    re-feeds the path silently' guarantee is now carried by the recover
    assertions: recover re-enters §06 and re-pauses while still starved, never
    skipping forward into §07. (Old crash-mechanism pin retired, NOT the
    contract.)"""
    _pause(tmp_path, monkeypatch)

    # (1) No exception escapes — the §06 wrap caught it. This is the inverse of
    # the old crash pin: an un-wrap regression would raise BuilderInputError
    # out of resume and this call would error instead of returning.
    errored = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    # (2) Exact terminal status + (3) the SPECIFIC tag, persisted non-silently.
    assert errored.status == "paused-at-error"
    assert errored.paused_gate is None
    assert errored.paused_error_tag == "builder.gary.upstream-missing"
    error_pause = json.loads(
        (tmp_path / str(TRIAL_ID) / "error-pause.json").read_text(encoding="utf-8")
    )
    assert error_pause["specialist_id"] == "package_builder"
    assert error_pause["tag"] == "builder.gary.upstream-missing"

    # (4) No gate opened over the starved brief: §06 halts BEFORE the gate, so
    # no G2C DecisionCard exists (anti-quality-theater core preserved).
    assert not (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").exists()

    # (5)+(6) Determinism / no-silent-refeed (Murat MUST-FIX): recover
    # re-enters §06 (still starved under the persisted cap=1) and re-pauses
    # with the SAME tag — it never walks past the refusal into §07.
    recovered = production_runner.recover_production_trial(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )
    assert recovered.status == "paused-at-error"
    assert recovered.paused_error_tag == "builder.gary.upstream-missing"
    assert not (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").exists()


def test_approve_verdict_resumes_execution_then_pauses_at_g2c(
    tmp_path: Path, monkeypatch
) -> None:
    """Resume after G1 verdict executes specialist nodes, then PAUSES at G2C.

    Multi-gate pause-and-resume was the `7a-2-deferred-resume-mode-multi-gate-
    pause` follow-on this test's predecessor documented; implemented 2026-06-11
    (Trial-3 attempt-3 defect #5, party-mode 4-of-4 Option-A consensus). The
    former GateBypassError raise is deliberately converted to the shared
    `_pause_at_gate` pause — silent bypass remains impossible because an
    undecided gate pauses with a registered DecisionCard, and decided gates
    are never revisited (resume starts at checkpoint.next_node_index).
    """
    _pause(tmp_path, monkeypatch)

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2C"
    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G2C.json").read_text()
    )
    assert card_payload["card"]["gate_id"] == "G2C"
    assert len(card_payload["digest"]) == 64


def test_g2c_pause_invokes_online_storyboard_publisher(
    tmp_path: Path, monkeypatch, storyboard_publish_calls
) -> None:
    """S5 criterion 7 wiring pin (operator-ratified 2026-06-12): the live
    G2C pause publishes the ONLINE storyboard BEFORE issuing the decision
    card — the review surface is part of reaching the gate."""
    _pause(tmp_path, monkeypatch)
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "approve"),
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
    assert recovered.paused_gate == "G2C"


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
    G2C (multi-gate pause implemented 2026-06-11). The state mutation is
    verified via the resume-command.json artifact."""
    _pause(tmp_path, monkeypatch)
    edit_payload = {"slide_count": 3}

    envelope = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_verdict(tmp_path, "edit", edit_payload=edit_payload),
        runs_root=tmp_path,
    )

    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G2C"
    command = json.loads((tmp_path / str(TRIAL_ID) / "resume-command.json").read_text())
    assert json.loads(command["run_state"]["cache_state"]["cache_prefix"]) == edit_payload


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
