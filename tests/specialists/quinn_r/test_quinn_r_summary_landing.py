from __future__ import annotations

import json
from pathlib import Path

from app.specialists.quinn_r.graph import _act
from tests.specialists.quinn_r.conftest import make_state


def test_quinn_r_summary_lands_in_7a5_envelope(tmp_path: Path) -> None:
    state = make_state(
        json.dumps(
            {
                "gate_id": "G2C",
                "gate_phase": "pre-composition",
                "runs_root": str(tmp_path),
                "slides": [{"slide_id": "s1", "title": "Opening"}],
            }
        )
    )
    output = json.loads(_act(state)["cache_state"]["cache_prefix"])
    summary = Path(output["summary_path"])
    lines = [line for line in summary.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert summary.parent == tmp_path / str(state.run_id) / "specialist-summaries"
    assert 15 <= len(lines) <= 25
    assert any("specialist_id: quinn_r" in line for line in lines)

