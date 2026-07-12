"""Hermetic test helpers for the notifier suite (Story 35.6).

A :class:`FakeApprise` spy stands in for the real Apprise transport, and
:func:`make_projection` builds contract-valid ``OperatorSurfaceProjection``
instances so tests drive the service through the same lenient-read path
production uses. Nothing here touches the network.
"""

from __future__ import annotations

import itertools
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.models.runtime.operator_surface import (
    HUD_CONFIG_DEFAULTS,
    EnvelopeSection,
    HealthSection,
    HealthTile,
    IdentitySection,
    NextActionSection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
    StepEntry,
    StepsSection,
)
from app.notify.service import PROJECTION_FILENAME

BASE_TIME = datetime(2026, 7, 11, 12, 0, 0, tzinfo=UTC)

_PAUSE_CLASS_FOR_STATUS = {
    "paused-at-gate": "paused-at-gate",
    "paused-at-error": "paused-at-error",
    "waiting_for_provider_batch": "waiting_for_provider_batch",
}


class FakeApprise:
    """In-memory Apprise stand-in: records adds + notifies; never hits network."""

    def __init__(self) -> None:
        self.added: list[str] = []
        self.notifications: list[tuple[str, str]] = []
        self.raise_on_notify = False

    def add(self, url: str) -> bool:
        self.added.append(url)
        return True

    def notify(self, *, title: str, body: str) -> bool:
        self.notifications.append((title, body))
        if self.raise_on_notify:
            raise RuntimeError("injected transport failure")
        return True


class FlakyApprise:
    """Scripted transport for push-retry tests (review S3).

    Each ``notify()`` consumes one script entry: ``True`` delivers, ``False``
    reports a delivery failure, ``"raise"`` blows up in-flight. An exhausted
    script delivers. Only DELIVERED notifies are recorded (unlike FakeApprise,
    which records the attempt) so tests can assert exactly-once delivery.
    """

    def __init__(self, script: tuple | list = ()) -> None:
        self.added: list[str] = []
        self.script: list = list(script)
        self.delivered: list[tuple[str, str]] = []
        self.attempts = 0

    def add(self, url: str) -> bool:
        self.added.append(url)
        return True

    def notify(self, *, title: str, body: str) -> bool:
        self.attempts += 1
        outcome = self.script.pop(0) if self.script else True
        if outcome == "raise":
            raise RuntimeError("injected transport failure")
        if outcome:
            self.delivered.append((title, body))
        return bool(outcome)


def make_projection(
    *,
    status: str = "in-flight",
    seq: int = 1,
    progress_seq: int = 1,
    last_progress_at: datetime | None = None,
    as_of: datetime | None = None,
    trial_id=None,
    lesson: str = "Test Lesson",
    paused_gate: str | None = None,
    paused_error_tag: str | None = None,
    waiting_batch_id: str | None = None,
    completed_at: datetime | None = None,
    next_command: str = "trial continue --trial-id X --gate G1 --decide approve",
    health_state: str = "nominal",
    health_label: str = "run_cost",
    walk_index: int = 0,
) -> OperatorSurfaceProjection:
    """Build a contract-valid projection for ``status`` (lifecycle rules honoured)."""
    ts = as_of or BASE_TIME
    lpa = last_progress_at or ts
    tid = trial_id or uuid4()

    identity = IdentitySection(
        as_of=ts, trial_id=tid, lesson=lesson, preset="production", operator_id="op-1"
    )
    envelope = EnvelopeSection(
        as_of=ts,
        status=status,
        paused_gate=paused_gate,
        paused_error_tag=paused_error_tag,
        waiting_batch_id=waiting_batch_id,
        completed_at=completed_at,
    )
    echo = NotificationsEchoSection(as_of=ts, config=HUD_CONFIG_DEFAULTS, parse_status="ok")

    kwargs: dict = {
        "seq": seq,
        "progress_seq": progress_seq,
        "last_progress_at": lpa,
        "envelope_digest": "digest-abc",
        "as_of": ts,
        "identity": identity,
        "envelope": envelope,
        "notifications_echo": echo,
    }

    if status != "registered":
        kwargs["steps"] = StepsSection(
            as_of=ts,
            manifest_digest="mdigest",
            node_count=2,
            walk_index=walk_index,
            entries=[
                StepEntry(step_id="07G", label="Narration", stage="stage-1", status="running"),
                StepEntry(step_id="08B", label="Assembly", stage="stage-1", status="pending"),
            ],
        )
        kwargs["health"] = HealthSection(
            as_of=ts,
            tiles=[
                HealthTile(
                    as_of=ts, label=health_label, value=1.0, threshold_state=health_state
                )
            ],
        )
    if status in _PAUSE_CLASS_FOR_STATUS:
        kwargs["next_action"] = NextActionSection(
            as_of=ts, command=next_command, pause_class=_PAUSE_CLASS_FOR_STATUS[status]
        )
    return OperatorSurfaceProjection(**kwargs)


class ProjectionWriter:
    """Writes projections to a run dir with monotonic mtimes (change detection)."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.path = run_dir / PROJECTION_FILENAME
        # Step mtimes by a full second per write: NTFS mtime resolution is
        # ~100ns, so a sub-100ns step would collapse consecutive writes into
        # one mtime and defeat the mtime-gate under test.
        self._clock = itertools.count(start=1_700_000_000, step=1)

    def _bump_mtime(self) -> None:
        seconds = next(self._clock)
        os.utime(self.path, (seconds, seconds))

    def write(self, projection: OperatorSurfaceProjection) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(projection.model_dump_json(), encoding="utf-8")
        self._bump_mtime()

    def write_raw(self, text: str) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text, encoding="utf-8")
        self._bump_mtime()
