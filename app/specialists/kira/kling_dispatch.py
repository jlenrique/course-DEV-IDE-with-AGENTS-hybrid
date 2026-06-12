"""Thin dispatch seam for Kira motion generation.

Story 2a.3 keeps dev-agent paths mockable and non-billing by default. When no
runtime motion-plan context is provided, this module returns a deterministic
fixture MP4 path. Operator workflows can pass `motion_plan_path` + `slide_id`
to run the real backend.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
TARGET_PATH = REPO_ROOT / "skills" / "kling-video" / "scripts" / "run_motion_generation.py"
DEFAULT_FIXTURE_MOTION_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "kira" / "mock_motion.mp4"
)


def _load_target_module() -> Any:
    spec = importlib.util.spec_from_file_location("kling_run_motion_generation", TARGET_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load kling runner from {TARGET_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class KlingDispatchError(SpecialistDispatchError):
    """Raised when Kling dispatch inputs are missing (S0 fail-loud policy)."""


def dispatch_to_kling(
    *,
    kling_prompt: str,
    model_name: str,
    mode: str,
    duration: float,
    negative_prompt: str | None = None,
    motion_plan_path: str | Path | None = None,
    slide_id: str | None = None,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    """Dispatch Kira's composed prompt to Kling.

    S0 fail-loud policy (SCP 2026-06-11 segment-data-plane): missing
    motion-plan context RAISES; the fixture MP4 is reachable only via
    explicit ``allow_fixture`` opt-in, which production dispatch never sets.
    """
    # Truthy guard (EH-3): empty-string slide_id / motion_plan_path must NOT
    # dispatch to the live runner. Without this guard, `slide_id=""` passed an
    # `is None` check and fell through to a paid Kuaishou call that would fail
    # mid-runner with a deep filesystem/billing-API error.
    if not motion_plan_path or not slide_id:
        if allow_fixture:
            return {
                "status": "mocked",
                "motion_asset_path": str(DEFAULT_FIXTURE_MOTION_PATH),
                "kling_choices": {
                    "model_name": model_name,
                    "mode": mode,
                    "duration": duration,
                    "negative_prompt": negative_prompt or "",
                },
                "kling_prompt": kling_prompt,
            }
        missing = "motion_plan_path" if not motion_plan_path else "slide_id"
        raise KlingDispatchError(
            f"dispatch_to_kling missing required input: {missing}",
            tag="kling.input.missing",
        )
    module = _load_target_module()
    if not hasattr(module, "run_motion_generation_for_slide"):
        raise RuntimeError("kling runner missing run_motion_generation_for_slide")
    receipt = module.run_motion_generation_for_slide(
        motion_plan_path=motion_plan_path,
        slide_id=slide_id,
    )
    motion_asset = receipt.get("motion_asset_path") or receipt.get("output_path")
    return {
        "status": str(receipt.get("status") or "generated"),
        "motion_asset_path": str(motion_asset or ""),
        "kling_choices": {
            "model_name": model_name,
            "mode": mode,
            "duration": duration,
            "negative_prompt": negative_prompt or "",
        },
        "kling_prompt": kling_prompt,
        "receipt": receipt,
    }


__all__ = ["DEFAULT_FIXTURE_MOTION_PATH", "KlingDispatchError", "dispatch_to_kling"]
