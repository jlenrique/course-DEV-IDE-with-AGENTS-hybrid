"""Cross-field validators for `RunState` (NFR-M5 four-file-lockstep).

One invariant: ``status == "complete"`` requires ``completed_at`` to be set
(parallels `NodeCheckpoint`'s same invariant). Lifted as a standalone
function so the test surface can hit it without constructing the full
`RunState` (which has many required fields).
"""

from __future__ import annotations

from datetime import datetime


def enforce_complete_requires_completed_at(
    *,
    status: str,
    completed_at: datetime | None,
) -> None:
    """Raise ValueError if RunState.status='complete' without completed_at."""
    if status == "complete" and completed_at is None:
        raise ValueError("RunState.status='complete' requires completed_at to be set")
    if status != "complete" and completed_at is not None:
        raise ValueError(
            f"RunState.completed_at is only valid when status='complete'; "
            f"got status={status!r} with completed_at set"
        )
