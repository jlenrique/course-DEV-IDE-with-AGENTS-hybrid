"""Runner-side projection emission tests (Story 35.2).

Verifies the MINIMAL runner integration: ``_persist_envelope`` emits a
projection AFTER (and byte-identically preserving) the ``run.json`` write for
every status transition, and every resume/recover/resume-batch entry point
reconciles-on-entry from run.json truth BEFORE doing anything else (AD-17).

Design note (documented per the story spec): a full live walk (compose ->
compile -> live specialists) is too heavy for a hermetic unit; per the spec's
sanctioned fallback we drive ``_persist_envelope`` directly for every status
transition and exercise the reconcile-on-entry ordering through the three real
entry points (each raises a status guard right after the reconcile emit, so the
projection write is observable without a paid walk). Both-walk pause-path
emission is additionally covered by the assembler unit goldens.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.orchestrator import production_runner as pr
from app.marcus.orchestrator.production_runner import (
    _persist_envelope,
    recover_production_trial,
    resume_batch_production_trial,
    resume_production_trial,
)
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    read_operator_surface_lenient,
)
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope


def _now() -> datetime:
    return datetime.now(UTC)


def _envelope(tid, status: str, **kw) -> ProductionTrialEnvelope:
    fields = dict(
        trial_id=tid,
        preset="production",
        corpus_path="lesson-alpha",
        operator_id="operator_cli",
        started_at=_now(),
        status=status,
        production_clone_launch_evidence=False,
        production_envelope=ProductionEnvelope(trial_id=tid),
    )
    fields.update(kw)
    return ProductionTrialEnvelope(**fields)


def _projection(run_dir: Path) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient((run_dir / "operator-surface.json").read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def _write_card(run_dir: Path, gate_id: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"decision-card-{gate_id}.json").write_text(
        json.dumps({"card": {"card_id": str(uuid4())}, "digest": "digest123"}),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------
# _persist_envelope: run.json unchanged + projection emitted
# --------------------------------------------------------------------------


def test_persist_envelope_preserves_run_json_and_emits_projection(tmp_path: Path) -> None:
    tid = uuid4()
    env = _envelope(tid, "registered")
    path = _persist_envelope(env, tmp_path)

    # run.json write semantics unchanged: exact model_dump_json(indent=2) + "\n"
    assert path.read_text(encoding="utf-8") == env.model_dump_json(indent=2) + "\n"

    # projection emitted alongside, deriving its digest from those exact bytes
    proj = _projection(tmp_path / str(tid))
    assert proj.envelope.status == "registered"
    expected_digest = hashlib.sha256(
        (env.model_dump_json(indent=2) + "\n").encode("utf-8")
    ).hexdigest()
    assert proj.envelope_digest == expected_digest


def test_every_status_transition_emits(tmp_path: Path) -> None:
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    _write_card(run_dir, "G1")

    transitions = [
        _envelope(tid, "registered"),
        _envelope(tid, "in-flight"),
        _envelope(tid, "paused-at-gate", paused_gate="G1"),
        _envelope(tid, "in-flight"),
        _envelope(tid, "paused-at-error", paused_error_tag="gamma_blip"),
        _envelope(tid, "waiting_for_provider_batch", waiting_batch_id="batch_1"),
        _envelope(tid, "in-flight"),
        _envelope(tid, "completed", completed_at=_now()),
    ]
    last_seq = -1
    for env in transitions:
        _persist_envelope(env, tmp_path)
        proj = _projection(run_dir)
        assert proj.envelope.status == env.status
        assert proj.seq == last_seq + 1  # seq bumps on every write
        last_seq = proj.seq
    # a terminal completed projection carries completed_at
    assert _projection(run_dir).envelope.completed_at is not None


def test_paused_at_gate_projection_carries_next_action(tmp_path: Path) -> None:
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    _write_card(run_dir, "G1")
    _persist_envelope(_envelope(tid, "in-flight"), tmp_path)
    _persist_envelope(_envelope(tid, "paused-at-gate", paused_gate="G1"), tmp_path)
    proj = _projection(run_dir)
    assert proj.next_action is not None
    # F-E2E-1: gate-class next-action emits the cross-process `trial resume`
    # inline-verdict command (former `gate decide` read an empty in-memory card
    # store cross-shell and failed card_missing).
    assert proj.next_action.command.startswith("trial resume")


# --------------------------------------------------------------------------
# Reconcile-on-entry (AD-17): run.json truth after any entry-point touch
# --------------------------------------------------------------------------


def _seed_skew(tmp_path: Path):
    """Seed a stale projection (registered) then overwrite run.json to in-flight."""
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    # stale projection: emit a registered envelope
    _persist_envelope(_envelope(tid, "registered"), tmp_path)
    stale = _projection(run_dir)
    assert stale.envelope.status == "registered"
    # now make run.json newer/different: in-flight (projection left stale)
    in_flight = _envelope(tid, "in-flight")
    (run_dir / "run.json").write_text(
        in_flight.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    return tid, run_dir, in_flight


def test_resume_reconciles_on_entry(tmp_path: Path) -> None:
    tid, run_dir, in_flight = _seed_skew(tmp_path)
    # run.json says in-flight; resume expects paused-at-gate -> raises AFTER reconcile
    with pytest.raises(RuntimeError):
        resume_production_trial(trial_id=tid, verdict=None, runs_root=tmp_path)  # type: ignore[arg-type]
    proj = _projection(run_dir)
    assert proj.envelope.status == "in-flight"  # run.json truth rendered
    expected = hashlib.sha256(
        (in_flight.model_dump_json(indent=2) + "\n").encode("utf-8")
    ).hexdigest()
    assert proj.envelope_digest == expected


def test_recover_reconciles_on_entry(tmp_path: Path) -> None:
    tid, run_dir, _in_flight = _seed_skew(tmp_path)
    with pytest.raises(RuntimeError):
        recover_production_trial(trial_id=tid, runs_root=tmp_path)
    assert _projection(run_dir).envelope.status == "in-flight"


def test_resume_batch_reconciles_on_entry(tmp_path: Path) -> None:
    tid, run_dir, _in_flight = _seed_skew(tmp_path)
    with pytest.raises(RuntimeError):
        resume_batch_production_trial(trial_id=tid, runs_root=tmp_path)
    assert _projection(run_dir).envelope.status == "in-flight"


def test_emit_wrapper_never_raises_into_runner(tmp_path: Path, monkeypatch) -> None:
    tid = uuid4()

    class _Boom(pr.OperatorSurfaceAssembler):
        def emit(self, envelope):  # type: ignore[override]
            raise RuntimeError("assembler blew up")

    monkeypatch.setattr(pr, "OperatorSurfaceAssembler", _Boom)
    # _persist_envelope must still succeed (run.json written) despite emit fault
    path = _persist_envelope(_envelope(tid, "registered"), tmp_path)
    assert path.exists()
    assert path.read_text(encoding="utf-8").strip() != ""
