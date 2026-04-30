from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.specialists.quinn_r.graph import _act
from tests.specialists.quinn_r.conftest import make_state


def test_g3b_post_composition_returns_forensic_verdict(
    monkeypatch, tmp_path: Path
) -> None:
    artifact = tmp_path / "assembled.txt"
    artifact.write_text("assembled", encoding="utf-8")
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.dispatch_to_sensory_bridges",
        lambda **_: {"confidence": "HIGH", "layout_description": "assembled video"},
    )
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.run_postcomposition_validators",
        lambda **_: {"status": "ok", "dimension_scores": {"composition": "PASS"}},
    )
    state = make_state(
        json.dumps(
            {
                "gate_id": "G3B",
                "gate_phase": "post-composition",
                "runs_root": str(tmp_path),
                "artifact_path": str(artifact),
                "modality": "video",
            }
        )
    )
    verdict: dict[str, Any] = json.loads(_act(state)["cache_state"]["cache_prefix"])[
        "quinn_r_review"
    ]
    assert verdict["mode"] == "post-composition"
    assert verdict["perception"]["confidence"] == "HIGH"
    assert verdict["deterministic"]["status"] == "ok"

