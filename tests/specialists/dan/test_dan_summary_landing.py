from __future__ import annotations

import json
from pathlib import Path

from app.models.state import specialist_summary_artifacts as summary_writer
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.dan.graph import _emit_spans


def test_dan_summary_lands_via_7a5_facade(tmp_path: Path, monkeypatch) -> None:
    original_emit = summary_writer.emit_summary_for_state

    def _emit_with_tmp_root(
        specialist_id: str, state: RunState, *, gate_id: str = "specialist-complete"
    ) -> dict[str, object]:
        return original_emit(specialist_id, state, gate_id=gate_id, runs_root=tmp_path)

    monkeypatch.setattr(
        "app.specialists.dan.graph.specialist_summary_writer.emit_summary_for_state",
        _emit_with_tmp_root,
    )
    state = RunState(
        graph_version="v0.1-stub",
        cache_state=CacheState(cache_prefix=json.dumps({"contributions": []})),
    )
    _emit_spans(state)
    summary_dir = tmp_path / str(state.run_id) / "specialist-summaries"
    summaries = list(summary_dir.glob("dan-*.md"))
    assert len(summaries) == 1
    text = summaries[0].read_text(encoding="utf-8")
    assert "Dan" in text
    assert "G2" in text
    assert "deferred: false" in text
