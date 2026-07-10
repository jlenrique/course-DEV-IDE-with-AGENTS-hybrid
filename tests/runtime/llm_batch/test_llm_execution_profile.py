"""A1 hermetic tests: vision LLM execution profile load + cascade untouched."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.runtime.cascade_config import load_cascade
from app.runtime.llm_execution_config import load_llm_execution


def test_load_llm_execution_vision_defaults() -> None:
    cfg = load_llm_execution()
    assert cfg.default_mode == "realtime"
    vision = cfg.node("vision")
    assert vision.default_mode == "realtime"
    assert vision.realtime.model == "gpt-5.5"
    assert vision.realtime.provider == "openai"
    assert vision.realtime.max_completion_tokens == 8192
    assert vision.batch is not None
    assert vision.batch.model == "gpt-5.5"
    assert vision.batch.model == vision.realtime.model
    assert vision.batch.batch_model_fallback_family == "gpt-5"
    assert vision.batch.harness_baseline_batch_id == (
        "batch_6a457bcac6488190b79224e61ea89b26"
    )


def test_resolve_profile_realtime_vs_batch() -> None:
    cfg = load_llm_execution()
    assert cfg.resolve_profile("vision", mode="realtime").model == "gpt-5.5"
    assert cfg.resolve_profile("vision", mode="batch").model == "gpt-5.5"
    assert cfg.resolve_profile("vision").model == "gpt-5.5"  # node default_mode


def test_cascade_vision_realtime_untouched() -> None:
    """T7 precursor: A1 must not change economics cascade vision → gpt-5.5."""

    cascade = load_cascade()
    entry = cascade.specialists["vision"]
    assert entry.model == "gpt-5.5"


def test_llm_execution_rejects_missing_vision(tmp_path: Path) -> None:
    target = tmp_path / "llm_execution.yaml"
    target.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "default_mode": "realtime",
                "nodes": {},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="vision"):
        load_llm_execution(target)


def test_llm_execution_rejects_vision_without_batch(tmp_path: Path) -> None:
    target = tmp_path / "llm_execution.yaml"
    target.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "default_mode": "realtime",
                "nodes": {
                    "vision": {
                        "default_mode": "realtime",
                        "realtime": {
                            "provider": "openai",
                            "model": "gpt-5.5",
                            "max_completion_tokens": 100,
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError, match="batch"):
        load_llm_execution(target)
