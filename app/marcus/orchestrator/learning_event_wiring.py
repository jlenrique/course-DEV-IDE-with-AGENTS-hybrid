"""Marcus gate decision wiring for learning-event capture."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from scripts.utilities.learning_event_capture import append_to_ledger, create_event


def record_gate_2_decision(run_id: UUID, run_dir: Path) -> None:
    """Record Gate 2 learning event."""
    event = create_event(run_id=run_id, gate="G2C", event_type="approval")
    append_to_ledger(event, run_dir)


def record_gate_3_decision(run_id: UUID, run_dir: Path) -> None:
    """Record Gate 3 learning event."""
    event = create_event(run_id=run_id, gate="G3", event_type="revision")
    append_to_ledger(event, run_dir)


def record_gate_4_decision(run_id: UUID, run_dir: Path) -> None:
    """Record Gate 4 learning event."""
    event = create_event(run_id=run_id, gate="G4", event_type="waiver")
    append_to_ledger(event, run_dir)
