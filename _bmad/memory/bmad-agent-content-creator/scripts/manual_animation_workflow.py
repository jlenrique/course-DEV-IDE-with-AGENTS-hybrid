# /// script
# requires-python = ">=3.10"
# ///
"""Manual animation guidance and import validation for Epic 14."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".webm"}


class ManualAnimationError(ValueError):
    """Invalid manual animation request or import payload."""


def generate_animation_guidance(
    slide_assignment: dict[str, Any],
    *,
    tool: str | None = None,
) -> dict[str, Any]:
    """Produce tool-agnostic animation guidance for one slide."""
    slide_id = str(slide_assignment.get("slide_id") or "").strip()
    if not slide_id:
        raise ManualAnimationError("slide_assignment requires slide_id")

    motion_brief = str(slide_assignment.get("motion_brief") or "Animate the approved slide").strip()
    guidance_notes = str(slide_assignment.get("guidance_notes") or "").strip()
    narration_intent = str(slide_assignment.get("narration_intent") or "").strip()
    duration_seconds = float(slide_assignment.get("motion_duration_seconds") or 6.0)
    tool_name = str(tool or slide_assignment.get("tool") or "").strip().lower()

    body_lines = [
        f"# Animation Guidance: {slide_id}",
        "",
        f"- Visual description: {motion_brief}",
        f"- Suggested duration: {duration_seconds:.1f}s",
        "- Key frames: start state, midpoint emphasis, end state",
    ]
    if narration_intent:
        body_lines.append(f"- Narration alignment: {narration_intent}")
    if guidance_notes:
        body_lines.append(f"- Guidance notes: {guidance_notes}")
    if tool_name == "vyond":
        body_lines.append("- Tool mode: Vyond-specific timing and scene guidance requested.")
    else:
        body_lines.append("- Tool mode: tool-agnostic guidance; adapt to the animation tool of choice.")

    return {
        "slide_id": slide_id,
        "duration_seconds": duration_seconds,
        "tool_mode": "vyond" if tool_name == "vyond" else "generic",
        "content": "\n".join(body_lines),
    }


def import_manual_motion_asset(
    slide_assignment: dict[str, Any],
    asset_path: str | Path,
    *,
    duration_seconds: float,
    expected_min_seconds: float = 2.0,
    expected_max_seconds: float = 15.0,
) -> dict[str, Any]:
    """Validate and record a manual animation asset import."""
    path = Path(asset_path)
    if not path.is_file():
        raise ManualAnimationError(f"Imported motion asset does not exist: {path}")
    if path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        raise ManualAnimationError(
            f"Unsupported motion asset format {path.suffix}; expected one of {sorted(SUPPORTED_VIDEO_FORMATS)}"
        )
    if not (expected_min_seconds <= float(duration_seconds) <= expected_max_seconds):
        raise ManualAnimationError(
            "Imported motion asset duration is outside the expected range "
            f"({expected_min_seconds}-{expected_max_seconds}s)"
        )

    updated = deepcopy(slide_assignment)
    updated["motion_type"] = "animation"
    updated["motion_source"] = "manual"
    updated["motion_asset_path"] = str(path).replace("\\", "/")
    updated["motion_duration_seconds"] = float(duration_seconds)
    updated["motion_status"] = "imported"
    return updated
