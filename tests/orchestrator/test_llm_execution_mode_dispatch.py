"""B6-land: vision-only llm_execution_mode dispatch overlay + T7 spies."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import apply_llm_execution_mode_overlay
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision.payload_contract import VisionProviderResponse


def test_batch_mode_overlays_only_vision_payload() -> None:
    rs = RunState(graph_version="v42", llm_execution_mode="batch")
    out = apply_llm_execution_mode_overlay(
        specialist_id="vision",
        run_state=rs,
        runner_payload={"export_dir": "/tmp"},
    )
    assert out == {"export_dir": "/tmp", "llm_execution_mode": "batch"}


def test_realtime_default_does_not_overlay_vision_payload() -> None:
    rs = RunState(graph_version="v42")  # default realtime
    out = apply_llm_execution_mode_overlay(
        specialist_id="vision",
        run_state=rs,
        runner_payload={"export_dir": "/tmp"},
    )
    assert out == {"export_dir": "/tmp"}
    assert "llm_execution_mode" not in out


def test_batch_mode_nonvision_payload_has_no_llm_execution_mode() -> None:
    rs = RunState(graph_version="v42", llm_execution_mode="batch")
    for specialist_id in ("irene", "gary", "texas", "cd", "elevenlabs"):
        out = apply_llm_execution_mode_overlay(
            specialist_id=specialist_id,
            run_state=rs,
            runner_payload={"k": 1, "llm_execution_mode": "batch"},
        )
        assert out == {"k": 1}
        assert "llm_execution_mode" not in out


def test_t7_realtime_default_never_touches_batch_adapter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Affirmative T7 spies — not 'suite stayed green'."""

    spies = {"submit": 0, "batch_route": 0, "create_file": 0, "create_batch": 0}

    def boom_submit(*_a: Any, **_k: Any) -> Any:
        spies["submit"] += 1
        raise AssertionError("submit_and_receipt must not run on realtime default")

    def boom_batch(*_a: Any, **_k: Any) -> Any:
        spies["batch_route"] += 1
        raise AssertionError("batch route must not run on realtime default")

    def boom_create_file(*_a: Any, **_k: Any) -> Any:
        spies["create_file"] += 1
        raise AssertionError("litellm.create_file must not run on realtime default")

    def boom_create_batch(*_a: Any, **_k: Any) -> Any:
        spies["create_batch"] += 1
        raise AssertionError("litellm.create_batch must not run on realtime default")

    monkeypatch.setattr(
        "app.runtime.llm_batch.adapter.LiteLlmBatchAdapter.submit_and_receipt",
        boom_submit,
    )
    monkeypatch.setattr(_act, "run_vision_batch_perception", boom_batch)
    monkeypatch.setattr("litellm.create_file", boom_create_file)
    monkeypatch.setattr("litellm.create_batch", boom_create_batch)
    monkeypatch.setattr(
        "app.runtime.llm_batch.adapter.litellm.create_file", boom_create_file
    )
    monkeypatch.setattr(
        "app.runtime.llm_batch.adapter.litellm.create_batch", boom_create_batch
    )

    png = tmp_path / "s.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")

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

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    monkeypatch.setattr(_act, "with_llm_primary_reading_path", lambda a: a)

    state = RunState(
        run_id=uuid4(),
        graph_version="v42",
        llm_execution_mode="realtime",
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
        cache_state=CacheState(
            cache_prefix=json.dumps(
                {"slides": [{"slide_id": "slide-01", "file_path": str(png)}]}
            ),
            entries_count=1,
        ),
    )
    # Production dispatch seam: overlay must not inject batch on default.
    overlaid = apply_llm_execution_mode_overlay(
        specialist_id="vision",
        run_state=state,
        runner_payload=None,
    )
    assert overlaid is None

    out = _act.act(state, runs_root=tmp_path)
    assert spies["submit"] == 0
    assert spies["batch_route"] == 0
    assert spies["create_file"] == 0
    assert spies["create_batch"] == 0
    assert not any(p for p in tmp_path.rglob("llm_batch") if p.is_dir())
    assert '"llm_execution_mode": "realtime"' in out["cache_state"]["cache_prefix"]
