"""Fixture builders for the HUD server/reader tests (Story 35.4).

Importable helper module (namespace-package path ``tests.hud._helpers``,
matching the repo's existing ``tests._helpers.*`` convention) so test modules
share one projection builder.

Fixture projections are built through the STRICT producer model here on
purpose: building a byte-valid fixture is the producer's job, not a consumer
strict-parse (the AD-4 import-linter fence forbids the strict parse inside
``app.hud`` only). Everything the server does with these files goes through
the lenient reader.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.hud.data import PROJECTION_FILENAME
from app.models.runtime.operator_surface import (
    HUD_CONFIG_DEFAULTS,
    EnvelopeSection,
    IdentitySection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
)


def _now() -> datetime:
    return datetime(2026, 7, 11, 12, 0, 0, tzinfo=UTC)


def build_registered_projection(
    *,
    trial_id: uuid.UUID | None = None,
    seq: int = 1,
    progress_seq: int = 0,
    lesson: str = "tejal-part-3",
) -> OperatorSurfaceProjection:
    """A minimal, contract-valid projection at ``registered`` (AD-15 presence)."""
    now = _now()
    tid = trial_id if trial_id is not None else uuid.uuid4()
    return OperatorSurfaceProjection(
        seq=seq,
        progress_seq=progress_seq,
        last_progress_at=now,
        envelope_digest="deadbeef",
        as_of=now,
        identity=IdentitySection(
            as_of=now,
            trial_id=tid,
            lesson=lesson,
            preset="production",
            operator_id="juanleon",
        ),
        envelope=EnvelopeSection(as_of=now, status="registered"),
        notifications_echo=NotificationsEchoSection(
            as_of=now,
            config=HUD_CONFIG_DEFAULTS,
            parse_status="ok",
        ),
    )


def projection_json_bytes(projection: OperatorSurfaceProjection) -> bytes:
    """Serialize a projection to the on-disk JSON byte form."""
    return (json.dumps(projection.model_dump(mode="json"), indent=2) + "\n").encode("utf-8")


def write_projection_file(run_dir: Path, raw: bytes) -> Path:
    """Write raw projection bytes to the canonical filename under ``run_dir``."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / PROJECTION_FILENAME
    path.write_bytes(raw)
    return path


def write_projection(run_dir: Path, projection: OperatorSurfaceProjection) -> Path:
    return write_projection_file(run_dir, projection_json_bytes(projection))


def mutate_projection_dict(
    projection: OperatorSurfaceProjection, **overrides: Any
) -> dict[str, Any]:
    """Dump a projection to a JSON-able dict and apply top-level overrides."""
    data = projection.model_dump(mode="json")
    data.update(overrides)
    return data
