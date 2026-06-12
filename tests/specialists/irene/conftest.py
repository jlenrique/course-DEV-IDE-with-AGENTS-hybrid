"""Shared grounding fixtures for Irene Pass-2 tests (dp-v1.1, 2026-06-12).

Pass 2 is grounded fail-loud: corpus (bundle_reference → extracted.md),
latest refined lesson_plan, and Gary's real slide roster are REQUIRED
payload inputs. Tests exercising `_act`'s pass-2 leg build payloads here
instead of hand-rolling ungrounded ones (the ungrounded shape IS the
cycle-4 defect).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def make_grounded_pass2_payload(tmp_path: Path, **extra: Any) -> dict[str, Any]:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "extracted.md").write_text(
        "# Source corpus\n\nMacro trends in healthcare delivery.\n",
        encoding="utf-8",
    )
    payload: dict[str, Any] = {
        "bundle_reference": str(bundle_dir),
        "lesson_plan": {"title": "Macro Trends", "objectives": ["obj-1"]},
        "gary_slide_output": [
            {"slide_id": "s1", "visual_description": "Dual-axis chart"},
            {"slide_id": "s2", "visual_description": "Burnout infographic"},
        ],
    }
    payload.update(extra)
    return payload


def joined_pass2_response(
    narration: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """A parseable Pass-2 response whose deltas join the conftest roster."""
    return {
        "narration_script": narration
        or [
            {"id": "seg-1", "narration_text": "Opening."},
            {"id": "seg-2", "narration_text": "Closing."},
        ],
        "segment_manifest_deltas": [
            {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
            {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
        ],
    }
