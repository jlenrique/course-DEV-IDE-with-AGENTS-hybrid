from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.models.state import specialist_summary_artifacts as summary_writer


@pytest.mark.timeout(30)
def test_compositor_summary_lands_active_g3_envelope(tmp_path) -> None:
    path = summary_writer.emit_summary(
        specialist_id="compositor",
        trial_id=UUID("12345678-1234-4234-8234-123456789abc"),
        gate_id="G3",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 30, tzinfo=UTC),
        artifact_paths=["bundle/DESCRIPT-ASSEMBLY-GUIDE.md"],
        resolution_trail=["deterministic -> deterministic-compositor-v0: no LLM"],
    )

    text = path.read_text(encoding="utf-8")
    assert path.name.startswith("compositor-")
    assert "specialist_id: compositor" in text
    assert "gate_id: G3" in text
    assert "deferred: false" in text
