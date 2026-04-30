"""Motion Gate receipt reader — published receipt contract for Irene Pass 2.

Satisfies Story §7.1 AC-B.3 (upstream-reference cross-validation). Amelia's
separation-of-concerns rider pulls this out of the Pass 2 emission lint so
receipt parsing has its own module and test surface — if Motion Gate
receipt format evolves, only this module updates in lockstep.

Public API:
- load_receipt(path) -> dict         # raw JSON load (for audit trail)
- read_motion_durations(path) -> dict[str, float]
                                      # {slide_id: duration_seconds} for
                                      # approved non-static slides; empty
                                      # dict when gate is approved but all
                                      # slides are static.
- MotionGateReceiptError              # raised on any shape violation
"""

from __future__ import annotations

import json
import math
from pathlib import Path


class MotionGateReceiptError(ValueError):
    """Raised when a Motion Gate receipt violates the expected shape."""


def load_receipt(path: Path) -> dict:
    """Return the raw JSON payload of a Motion Gate receipt.

    Does not validate shape beyond "parseable JSON"; callers that need
    schema-level checks should use read_motion_durations (which calls this
    and then validates).
    """
    if not path.exists():
        raise MotionGateReceiptError(f"Motion Gate receipt not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MotionGateReceiptError(
            f"Motion Gate receipt is malformed JSON ({path}): {exc}"
        ) from exc


def read_motion_durations(path: Path) -> dict[str, float]:
    """Return {slide_id: duration_seconds} for all approved motion slides.

    Raises MotionGateReceiptError when:
    - file missing
    - JSON malformed
    - gate_decision missing or not 'approved'
    - non_static_slides missing or not a list
    - any entry missing slide_id or duration_seconds
    - any duration_seconds <= 0
    - duplicate slide_id in non_static_slides

    Returns empty dict when gate_decision is 'approved' and non_static_slides
    is empty (static-only deck).
    """
    receipt = load_receipt(path)
    if not isinstance(receipt, dict):
        raise MotionGateReceiptError(
            f"Motion Gate receipt root must be a JSON object, got "
            f"{type(receipt).__name__} ({path})"
        )

    gate_decision = receipt.get("gate_decision")
    if gate_decision is None:
        raise MotionGateReceiptError(
            f"Motion Gate receipt is missing gate_decision ({path})"
        )
    if not isinstance(gate_decision, str):
        raise MotionGateReceiptError(
            f"gate_decision must be a string, got {type(gate_decision).__name__} "
            f"({path})"
        )
    if gate_decision != "approved":
        raise MotionGateReceiptError(
            f"Motion Gate receipt is not approved (gate_decision={gate_decision!r}, "
            f"path={path})"
        )

    non_static = receipt.get("non_static_slides")
    if non_static is None or not isinstance(non_static, list):
        raise MotionGateReceiptError(
            f"Motion Gate receipt is missing non_static_slides list ({path})"
        )

    durations: dict[str, float] = {}
    for idx, entry in enumerate(non_static):
        if not isinstance(entry, dict):
            raise MotionGateReceiptError(
                f"non_static_slides[{idx}] must be a mapping, got "
                f"{type(entry).__name__} ({path})"
            )
        slide_id = entry.get("slide_id")
        if slide_id is None:
            raise MotionGateReceiptError(
                f"non_static_slides[{idx}] is missing slide_id ({path})"
            )
        if not isinstance(slide_id, str) or not slide_id:
            raise MotionGateReceiptError(
                f"non_static_slides[{idx}] slide_id must be a non-empty string, "
                f"got {slide_id!r} ({path})"
            )
        if slide_id in durations:
            raise MotionGateReceiptError(
                f"duplicate slide_id {slide_id!r} in non_static_slides ({path})"
            )
        duration = entry.get("duration_seconds")
        # Reject bool explicitly — isinstance(True, int) is True in Python,
        # and `True > 0` evaluates True, so without this guard a
        # `duration_seconds: true` in JSON would coerce to 1.0 silently.
        if (
            duration is None
            or isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or duration <= 0
            or math.isnan(duration)
            or math.isinf(duration)
        ):
            raise MotionGateReceiptError(
                f"non_static_slides[{idx}] has invalid duration "
                f"({duration!r}) for slide_id {slide_id!r} ({path})"
            )
        durations[slide_id] = float(duration)

    return durations
