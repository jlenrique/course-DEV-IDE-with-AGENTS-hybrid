"""OFF non-interference pin — affirmative spies (Murat MUST-T1 / John MUST-1)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision.payload_contract import VisionProviderResponse


def _png(tmp_path: Path) -> Path:
    path = tmp_path / "s.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    return path


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="0" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )


@pytest.mark.parametrize(
    "mode",
    [None, "realtime", "", "not-batch", "BATCH"],
)
def test_off_modes_never_touch_batch_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mode: str | None
) -> None:
    png = _png(tmp_path)
    payload: dict[str, Any] = {
        "slides": [{"slide_id": "slide-01", "file_path": str(png)}],
    }
    if mode is not None:
        payload["llm_execution_mode"] = mode

    spies = {"batch_route": 0, "jsonl": 0}

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        return VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",
            coverage="perceived",
            confidence_score=0.9,
            slide_title="T",
            extracted_text="x",
            layout_description="y",
            text_blocks=["x"],
            visual_elements=[],
            provider_model_id="gpt-5.5",
            source_png_path=str(path),
        )

    def boom_batch(*_a: Any, **_k: Any) -> list[Any]:
        spies["batch_route"] += 1
        raise AssertionError("run_vision_batch_perception must not run when OFF")

    def boom_build(*_a: Any, **_k: Any) -> list[Any]:
        spies["jsonl"] += 1
        raise AssertionError("build_vision_batch_rows must not run when OFF")

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    monkeypatch.setattr(_act, "run_vision_batch_perception", boom_batch)
    monkeypatch.setattr(
        "app.specialists.vision.batch_route.build_vision_batch_rows",
        boom_build,
    )
    monkeypatch.setattr(_act, "with_llm_primary_reading_path", lambda artifact: artifact)

    state = _state(payload)
    out = _act.act(state, runs_root=tmp_path)
    assert spies["batch_route"] == 0
    assert spies["jsonl"] == 0
    assert not any(tmp_path.rglob("receipt.json"))
    assert not any(p for p in tmp_path.rglob("llm_batch") if p.is_dir())
    assert not (tmp_path / str(state.run_id)).exists()
    assert '"llm_execution_mode": "realtime"' in out["cache_state"]["cache_prefix"]
    assert out["model_resolution_trail"][-1].reason == "vision.parsed.ok"
