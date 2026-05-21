from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.vera._act import G0_DIMENSIONS
from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(30)
def test_g0_scores_texas_extracted_md_and_writes_oia_trace(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted.md"
    extracted.write_text(
        "The source claim is preserved. [evidence: texas-src]\n",
        encoding="utf-8",
    )
    update = _act(
        build_vera_state(
            {"gate_id": "G0", "extracted_path": str(extracted), "runs_root": str(tmp_path)}
        )
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    report = json.loads(Path(output["trace_report_path"]).read_text(encoding="utf-8"))

    assert set(report["rubrics"]["G0"]["dimensions"]) == set(G0_DIMENSIONS)
    assert all(
        "evidence_sentence" in item
        for item in report["rubrics"]["G0"]["dimensions"].values()
    )
    assert {"O", "I", "A"} == {finding["category"] for finding in report["findings"]}
    assert report["verdict"]["verb"] == "proceed"
