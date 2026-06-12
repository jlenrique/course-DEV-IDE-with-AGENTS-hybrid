from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.kira.kling_dispatch import dispatch_to_kling


def test_dispatch_to_kling_returns_fixture_when_context_missing() -> None:
    # S0 fail-loud policy: fixture path now requires explicit opt-in.
    receipt = dispatch_to_kling(
        kling_prompt="camera pan over diagram",
        model_name="kling-v1",
        mode="std",
        duration=5.0,
        allow_fixture=True,
    )
    assert receipt["status"] == "mocked"
    assert receipt["motion_asset_path"].endswith(".mp4")
    assert receipt["kling_choices"]["model_name"] == "kling-v1"


def test_dispatch_to_kling_raises_when_target_missing_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _BadModule:
        pass

    monkeypatch.setattr(
        "app.specialists.kira.kling_dispatch._load_target_module", lambda: _BadModule()
    )
    with pytest.raises(RuntimeError, match="missing run_motion_generation_for_slide"):
        dispatch_to_kling(
            kling_prompt="camera pan",
            model_name="kling-v1",
            mode="std",
            duration=5.0,
            motion_plan_path=Path("dummy-plan.yaml"),
            slide_id="slide-001",
        )
