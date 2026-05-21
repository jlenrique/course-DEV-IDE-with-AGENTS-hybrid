from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(30)
def test_vera_summary_lands_at_canonical_specialist_summary_path(tmp_path: Path) -> None:
    output = json.loads(
        _act(
            build_vera_state(
                {
                    "gate_id": "G0",
                    "runs_root": str(tmp_path),
                    "extracted_text": "claim [evidence: src]",
                }
            )
        )["cache_state"]["cache_prefix"]
    )
    summary = Path(output["summary_path"])
    text = summary.read_text(encoding="utf-8")

    assert summary.parent.name == "specialist-summaries"
    assert "specialist_id: vera" in text
    assert "gate_id: G0" in text
