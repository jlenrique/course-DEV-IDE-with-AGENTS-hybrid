from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.vera._act import G1_DIMENSIONS
from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(30)
def test_g1_emits_six_ingestion_quality_verdicts(tmp_path: Path) -> None:
    update = _act(
        build_vera_state(
            {
                "gate_id": "G1",
                "runs_root": str(tmp_path),
                "manifest": {"artifacts": [{"path": "extracted.md", "sha256": "abc"}]},
                "cross_validation_hints": ["compare against citation list"],
            }
        )
    )
    report = json.loads(
        Path(json.loads(update["cache_state"]["cache_prefix"])["trace_report_path"]).read_text(
            encoding="utf-8"
        )
    )
    dimensions = report["rubrics"]["G1"]["dimensions"]
    assert set(dimensions) == set(G1_DIMENSIONS)
    assert all({"verdict", "severity", "description"} <= set(item) for item in dimensions.values())
