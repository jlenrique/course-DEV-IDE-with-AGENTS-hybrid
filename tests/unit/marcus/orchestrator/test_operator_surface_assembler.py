"""Unit tests for the operator-surface assembler (Story 35.2).

Covers: registered/minimal emit, seq-every-write vs progress-seq-only-on-progress
(AD-10), freshness tick (seq-only), pause-class next-action wiring, read-merge-write
section preservation, walk-index regression => walk_generation re-entry marker,
atomic-write bounded retry (success-after-transient + fault-injected exhaustion),
and emit-never-raises fault injection (greenlight amendment 8).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.marcus.orchestrator import operator_surface_assembler as osa
from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    read_operator_surface_lenient,
)

# --------------------------------------------------------------------------
# Fixtures / helpers
# --------------------------------------------------------------------------


class _StubEnvelope:
    """Minimal envelope stand-in: exposes the fields emit() reads + model_dump_json."""

    def __init__(
        self,
        trial_id: UUID,
        status: str,
        *,
        paused_gate: str | None = None,
        paused_error_tag: str | None = None,
        waiting_batch_id: str | None = None,
        completed_at: datetime | None = None,
        corpus_path: str = "lesson-alpha",
        preset: str = "production",
        operator_id: str = "operator_cli",
    ) -> None:
        self.trial_id = trial_id
        self.status = status
        self.paused_gate = paused_gate
        self.paused_error_tag = paused_error_tag
        self.waiting_batch_id = waiting_batch_id
        self.completed_at = completed_at
        self.corpus_path = corpus_path
        self.preset = preset
        self.operator_id = operator_id

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "trial_id": str(self.trial_id),
                "status": self.status,
                "paused_gate": self.paused_gate,
                "paused_error_tag": self.paused_error_tag,
                "waiting_batch_id": self.waiting_batch_id,
                "completed_at": self.completed_at.isoformat()
                if self.completed_at
                else None,
            },
            indent=indent,
            sort_keys=True,
        )


def _read(assembler: OperatorSurfaceAssembler) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient(assembler.projection_path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def _write_gate_card(run_dir: Path, gate_id: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"decision-card-{gate_id}.json").write_text(
        json.dumps(
            {
                "card": {"card_id": str(uuid4()), "trial_id": str(uuid4())},
                "digest": "deadbeefdigest",
                "issued_at": "2026-07-11T00:00:00Z",
                "server_nonce": "nonce-xyz",
                "checkpoint_path": "checkpoint.json",
            }
        ),
        encoding="utf-8",
    )


def _assembler(tmp_path: Path, trial_id: UUID) -> OperatorSurfaceAssembler:
    # hud_config_path points at a nonexistent file -> loader returns defaults, ok.
    return OperatorSurfaceAssembler(
        trial_id, tmp_path, hud_config_path=tmp_path / "no-such-hud-config.yaml"
    )


def _write_g1_card(run_dir: Path) -> None:
    """G1 shape: drafted_proposal + confidence, NO operator_prompt (real fixture)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "decision-card-G1.json").write_text(
        json.dumps(
            {
                "card": {
                    "gate_focus": "trial_open",
                    "gate_id": "G1",
                    "drafted_proposal": {
                        "confidence": 0.72,
                        "decision": "revise",
                        "rationale": "minor taxonomy issues remain",
                    },
                    "evidence": [
                        {"kind": "production-runner", "node_id": "04"},
                        {"kind": "specialist-summary", "path": "runs/x/texas.md"},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )


def _write_g4a_card(run_dir: Path) -> None:
    """G4A shape: gate_focus/operator_prompt/pick_context, NO drafted_proposal."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "decision-card-G4A.json").write_text(
        json.dumps(
            {
                "card": {
                    "gate_focus": "voice_selection",
                    "gate_id": "G4A",
                    "operator_prompt": (
                        "Approve the proposed voice, or edit to select an alternate."
                    ),
                    "pick_context": [
                        {"kind": "production-runner", "node_id": "11-gate"},
                        {"kind": "specialist-summary", "path": "runs/x/enrique.md"},
                        {
                            "kind": "voice-options",
                            "voices": [
                                {"voice_name": "Sarah", "voice_id": "a"},
                                {"voice_name": "Shannon", "voice_id": "b"},
                            ],
                        },
                    ],
                }
            }
        ),
        encoding="utf-8",
    )


def _write_error_pause(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "error-pause.json").write_text(
        json.dumps(
            {
                "message": "scope=narration; slide slide-05 narration figures not present",
                "node_id": "08",
                "node_index": 33,
                "tag": "irene.pass2.figure-contradiction",
            }
        ),
        encoding="utf-8",
    )


def _write_completion_artifacts(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_summary.yaml").write_text(
        "terminal_gate: G4A\n"
        "component_selection:\n  deck: true\n  motion: true\n  workbook: true\n",
        encoding="utf-8",
    )
    (run_dir / "cost-report.json").write_text(
        json.dumps({"total_cost_usd": 0.44444605}), encoding="utf-8"
    )
    exports = run_dir / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    (exports / "gary-dispatch-payload.json").write_text("{}", encoding="utf-8")
    (exports / "storyboard-A-pack").mkdir(exist_ok=True)


# --------------------------------------------------------------------------
# Registered / minimal emit
# --------------------------------------------------------------------------


def test_registered_emit_creates_minimal_projection(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    assert asm.emit(_StubEnvelope(tid, "registered")) is True

    proj = _read(asm)
    assert proj.schema_version == "v1"
    assert proj.seq == 0
    assert proj.progress_seq == 0
    assert proj.envelope.status == "registered"
    assert proj.identity.trial_id == tid
    assert proj.identity.preset == "production"
    assert proj.notifications_echo is not None
    # pre-flight sections are absent at registered
    assert proj.steps is None
    assert proj.health is None
    assert proj.next_action is None
    # envelope_digest reflects the run.json bytes emit derives from
    assert len(proj.envelope_digest) == 64


# --------------------------------------------------------------------------
# seq / progress_seq semantics (AD-10)
# --------------------------------------------------------------------------


def test_seq_bumps_every_write_progress_only_on_progress(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)

    asm.emit(_StubEnvelope(tid, "registered"))
    p0 = _read(asm)
    assert (p0.seq, p0.progress_seq) == (0, 0)

    # health refresh: seq bump, NO progress bump (AD-10 forbids it)
    asm.update_health([{"as_of": _now(), "label": "openai", "value": "ok"}])
    p1 = _read(asm)
    assert p1.seq == 1
    assert p1.progress_seq == 0

    # freshness tick: seq bump, NO progress bump
    asm._freshness_tick_once()
    p2 = _read(asm)
    assert p2.seq == 2
    assert p2.progress_seq == 0

    # envelope transition registered -> in-flight: progress event
    asm.emit(_StubEnvelope(tid, "in-flight"))
    p3 = _read(asm)
    assert p3.seq == 3
    assert p3.progress_seq == 1
    assert p3.last_progress_at >= p0.last_progress_at


def test_progress_bumps_on_pause_identity_change(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_gate_card(run_dir, "G1")
    _write_gate_card(run_dir, "G2B")

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    p_g1 = _read(asm)
    # re-emit SAME status + SAME gate -> not a progress event (reconcile only)
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    p_same = _read(asm)
    assert p_same.progress_seq == p_g1.progress_seq
    assert p_same.seq == p_g1.seq + 1
    # same status but NEW gate identity (G1 -> G2B) IS a progress event
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G2B"))
    p_g2 = _read(asm)
    assert p_g2.progress_seq == p_g1.progress_seq + 1


def test_freshness_tick_context_manager_ticks_and_stops(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    before = _read(asm).seq
    with asm.freshness_tick(interval=0.02):
        # let a few ticks fire
        import time

        time.sleep(0.12)
    after = _read(asm).seq
    assert after > before
    # after the context exits, no further ticks bump seq
    settled = _read(asm).seq
    import time

    time.sleep(0.08)
    assert _read(asm).seq == settled
    # ticks never advance progress_seq
    assert _read(asm).progress_seq == 0


# --------------------------------------------------------------------------
# Pause-class next-action wiring (AD-3)
# --------------------------------------------------------------------------


def test_paused_at_gate_emits_next_action_command(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_gate_card(run_dir, "G1")

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    proj = _read(asm)
    assert proj.next_action is not None
    assert proj.next_action.pause_class == "paused-at-gate"
    assert proj.next_action.command.startswith("gate decide")
    assert f"--trial-id {tid}" in proj.next_action.command
    assert "--gate-id G1" in proj.next_action.command


def test_error_and_batch_pause_next_actions(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))

    asm.emit(_StubEnvelope(tid, "paused-at-error", paused_error_tag="gamma_blip"))
    err = _read(asm)
    assert err.next_action.pause_class == "paused-at-error"
    assert err.next_action.command == f"trial recover --trial-id {tid}"

    asm.emit(
        _StubEnvelope(tid, "waiting_for_provider_batch", waiting_batch_id="batch_1")
    )
    batch = _read(asm)
    assert batch.next_action.pause_class == "waiting_for_provider_batch"
    assert batch.next_action.command == f"trial resume-batch --trial-id {tid}"


def test_next_action_cleared_on_resume_to_in_flight(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-error", paused_error_tag="blip"))
    assert _read(asm).next_action is not None
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert _read(asm).next_action is None


# --------------------------------------------------------------------------
# Section read-merge-write preservation + steps walk index / re-entry
# --------------------------------------------------------------------------


def test_read_merge_write_preserves_sections(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    manifest = SimpleNamespace(
        nodes=[SimpleNamespace(id="n1", label="One", hud_tracked=True),
               SimpleNamespace(id="n2", label="Two", hud_tracked=False)]
    )
    asm.update_steps(manifest, 0)
    asm.update_health([{"as_of": _now(), "label": "gamma", "value": 42}])
    asm.append_trace("started", detail="walk began")

    # a subsequent envelope emit must NOT drop steps/health/trace
    asm.emit(_StubEnvelope(tid, "in-flight"))
    proj = _read(asm)
    assert proj.steps is not None and proj.steps.node_count == 2
    assert proj.steps.entries[0].stage == "stage-2"  # hud_tracked
    assert proj.steps.entries[1].stage == "stage-1"
    assert proj.health is not None and proj.health.tiles[0].label == "gamma"
    assert proj.trace is not None and proj.trace.events[-1].event == "started"


def test_update_steps_walk_index_regression_marks_reentry(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    manifest = SimpleNamespace(
        nodes=[SimpleNamespace(id=f"n{i}", label=None, hud_tracked=False) for i in range(5)]
    )
    asm.update_steps(manifest, 3)
    p3 = _read(asm)
    assert p3.steps.walk_index == 3
    assert p3.steps.walk_generation == 0
    assert p3.steps.reentered_from is None
    # regression to an earlier index == recover-reenter; the run re-entered
    # FROM the previous (higher) walk position (review S2)
    asm.update_steps(manifest, 1)
    p1 = _read(asm)
    assert p1.steps.walk_index == 1
    assert p1.steps.walk_generation == 1
    assert p1.steps.reentered_from == 3


def test_freshness_tick_start_failure_degrades_without_raising(
    tmp_path: Path, monkeypatch
) -> None:
    """Review MUST-1: a tick thread that cannot start never raises into the walk."""
    import threading as _threading

    tid = uuid4()
    asm = _assembler(tmp_path, tid)

    def _boom(self) -> None:
        raise RuntimeError("can't start new thread")

    monkeypatch.setattr(_threading.Thread, "start", _boom)
    with asm.freshness_tick(interval=0.01):
        pass  # walk body proceeds tick-less; no exception escapes


def test_atomic_write_retries_with_real_held_reader(tmp_path: Path) -> None:
    """Review S3: deterministic held-open-reader smoke — a reader holding the
    destination open while the writer replaces must end with a consistent
    winning write (bounded retry covers the transient PermissionError)."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    path = asm.projection_path
    with open(path, "rb") as held:
        held.read(1)  # hold an open handle across the writer's os.replace
        asm.emit(_StubEnvelope(tid, "paused-at-gate"))
    final = _read(asm)
    # Either the retry won during the hold or the next emit self-heals; the
    # file must be a coherent projection either way.
    assert final is not None and final.envelope.status in (
        "in-flight",
        "paused-at-gate",
    )
    asm.emit(_StubEnvelope(tid, "paused-at-gate"))
    assert _read(asm).envelope.status == "paused-at-gate"


# --------------------------------------------------------------------------
# Atomic write bounded retry (AD-2)
# --------------------------------------------------------------------------


@pytest.mark.serial
def test_atomic_write_retries_then_succeeds(tmp_path: Path, monkeypatch) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "registered"))  # establish a projection

    real_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src: Any, dst: Any) -> None:
        calls["n"] += 1
        if calls["n"] <= 2:  # fail the first two attempts
            raise PermissionError("held open by a reader")
        real_replace(src, dst)

    monkeypatch.setattr(osa.os, "replace", flaky_replace)
    ok = asm.emit(_StubEnvelope(tid, "in-flight"))
    assert ok is True
    assert calls["n"] >= 3
    assert _read(asm).envelope.status == "in-flight"


@pytest.mark.serial
def test_atomic_write_exhaustion_logs_and_skips(tmp_path: Path, monkeypatch, caplog) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "registered"))
    before = asm.projection_path.read_bytes()

    def always_fail(src: Any, dst: Any) -> None:
        raise PermissionError("reader never releases")

    monkeypatch.setattr(osa.os, "replace", always_fail)
    # exhaustion must NOT raise; returns False; prior projection untouched
    ok = asm.emit(_StubEnvelope(tid, "in-flight"))
    assert ok is False
    assert asm.projection_path.read_bytes() == before
    assert "exhausted" in caplog.text.lower()


# --------------------------------------------------------------------------
# emit-never-raises fault injection (greenlight amendment 8)
# --------------------------------------------------------------------------


def test_emit_never_raises_on_internal_fault(tmp_path: Path, monkeypatch) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)

    def boom(*_a: Any, **_k: Any) -> Any:
        raise RuntimeError("assembler internals exploded")

    # fault-inject the config loader used while building notifications_echo
    monkeypatch.setattr(osa, "load_hud_config", boom)
    # must swallow, return False, never propagate into the (would-be) walk
    assert asm.emit(_StubEnvelope(tid, "registered")) is False


def test_unrecognized_prior_projection_is_rebuilt(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.projection_path.parent.mkdir(parents=True, exist_ok=True)
    asm.projection_path.write_text("{ not valid json", encoding="utf-8")
    # a garbage prior file self-heals: emit rebuilds fresh from the envelope
    assert asm.emit(_StubEnvelope(tid, "registered")) is True
    proj = _read(asm)
    assert proj.seq == 0
    assert proj.envelope.status == "registered"


# --------------------------------------------------------------------------
# Story 35.9 — decision_card / error_message / deliverables (verb-conditional)
# --------------------------------------------------------------------------


def test_gate_pause_populates_decision_card_g1_shape(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_g1_card(run_dir)

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    proj = _read(asm)
    assert proj.decision_card is not None
    assert proj.decision_card.gate_focus == "trial_open"
    assert proj.decision_card.operator_prompt is None  # G1 has none
    assert proj.decision_card.drafted_proposal.decision == "revise"
    assert proj.decision_card.drafted_proposal.confidence == 0.72
    assert "runs/x/texas.md" in proj.decision_card.evidence
    # error_message / deliverables are absent at a gate pause
    assert proj.error_message is None
    assert proj.deliverables is None


def test_gate_pause_populates_decision_card_g4a_shape(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_g4a_card(run_dir)

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G4A"))
    proj = _read(asm)
    assert proj.decision_card is not None
    assert proj.decision_card.gate_focus == "voice_selection"
    assert proj.decision_card.operator_prompt.startswith("Approve the proposed voice")
    assert proj.decision_card.drafted_proposal is None  # G4A has none
    joined = " | ".join(proj.decision_card.pick_context)
    assert "runs/x/enrique.md" in joined
    assert "voice options: Sarah, Shannon" in joined


def test_decision_card_clears_on_resume(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_g1_card(run_dir)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    assert _read(asm).decision_card is not None
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert _read(asm).decision_card is None


def test_error_pause_populates_error_message(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_error_pause(run_dir)

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(
        _StubEnvelope(
            tid, "paused-at-error", paused_error_tag="irene.pass2.figure-contradiction"
        )
    )
    proj = _read(asm)
    assert proj.error_message is not None
    assert proj.error_message.message.startswith("scope=narration")
    assert proj.error_message.node_index == 33
    assert proj.error_message.tag == "irene.pass2.figure-contradiction"
    assert proj.decision_card is None


def test_completion_populates_deliverables(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    _write_completion_artifacts(run_dir)

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(
        _StubEnvelope(tid, "completed", completed_at=datetime.now(UTC))
    )
    proj = _read(asm)
    assert proj.deliverables is not None
    assert proj.deliverables.components.deck is True
    assert proj.deliverables.components.motion is True
    assert proj.deliverables.components.workbook is True
    assert proj.deliverables.total_cost_usd == 0.44444605
    assert "exports/gary-dispatch-payload.json" in proj.deliverables.export_paths
    assert "exports/storyboard-A-pack" in proj.deliverables.export_paths


def test_garbage_decision_card_never_sinks_emit(tmp_path: Path) -> None:
    """Amendment 8: a corrupt decision-card artifact yields None, emit still writes."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "decision-card-G1.json").write_text("{ not valid json", encoding="utf-8")

    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1")) is True
    proj = _read(asm)
    assert proj.envelope.status == "paused-at-gate"  # envelope still landed
    assert proj.decision_card is None  # garbage card omitted, not fatal


def test_missing_completion_artifacts_yield_no_deliverables(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    # no run_summary / cost-report / exports on disk
    assert asm.emit(_StubEnvelope(tid, "completed", completed_at=datetime.now(UTC))) is True
    proj = _read(asm)
    assert proj.envelope.status == "completed"
    assert proj.deliverables is None


def test_partial_completion_artifacts_populate_available_fields(tmp_path: Path) -> None:
    """Independent guards: a missing cost report never suppresses the booleans."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_summary.yaml").write_text(
        "component_selection:\n  deck: true\n  motion: false\n  workbook: true\n",
        encoding="utf-8",
    )
    (run_dir / "cost-report.json").write_text("{ corrupt", encoding="utf-8")

    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.emit(_StubEnvelope(tid, "completed", completed_at=datetime.now(UTC)))
    proj = _read(asm)
    assert proj.deliverables is not None
    assert proj.deliverables.components.deck is True
    assert proj.deliverables.components.motion is False
    assert proj.deliverables.total_cost_usd is None  # corrupt cost report -> None


def _now() -> str:
    return datetime.now(UTC).isoformat()
