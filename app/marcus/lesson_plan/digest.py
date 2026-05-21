"""Canonical-JSON digest helpers (Story 31-1 AC-B.10 / AC-C.4 / AC-T.7).

The digest is the sha256 of the canonical-JSON serialization of a LessonPlan
with its ``digest`` field cleared before hashing. Canonical form is:

    json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=_json_default,  # datetime -> ISO 8601 UTC string
    )

Two explicit semantic contracts (R2 rider AM-3):

1. **Nested list order is semantic.** ``PlanUnit.gaps = [a, b, c]`` MUST
   produce a different digest from ``PlanUnit.gaps = [a, c, b]``. Canonical
   serialization sorts dict keys, but lists are preserved in insertion order
   — AM-3 asserts that this is the chosen contract, not an accident.

2. **None equals missing-field.** A field with value ``None`` digests
   IDENTICALLY to the same field being absent. Canonical JSON achieves this
   by filtering ``None`` values out of the payload before serialization
   (the chosen contract per AM-3). Downstream consumers can rely on
   ``optional_field=None`` and ``optional_field absent`` producing the same
   sha256 — useful for shape-evolution where a later writer may omit a
   previously-None field entirely.

3. **Timezone-aware datetime contract (MF-4).** Every datetime field on the
   lesson-plan shapes (``LessonPlan.updated_at``, ``ScopeDecision.locked_at``,
   ``ScopeDecisionTransition.timestamp``, ``EventEnvelope.timestamp``,
   ``FitReport.generated_at``) rejects naive (``tzinfo is None``) values at
   validation time. Any timezone-aware datetime is accepted — not strictly
   UTC — because Pydantic's ISO 8601 serialization includes the offset,
   making the canonical string deterministic across timezones. This keeps
   the digest stable regardless of authoring timezone.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.marcus.lesson_plan.schema import LessonPlan


def _json_default(value: Any) -> Any:  # pragma: no cover - thin adapter
    """JSON encoder fallback for non-native types."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__} for canonical digest")


def _strip_none(payload: Any) -> Any:
    """Recursively drop ``None`` values so ``field=None`` == ``field absent`` (AM-3).

    Drops ``None`` values from dict values recursively (including dicts
    inside lists). Does NOT strip ``None`` elements from lists — list order
    and content is semantic per AM-3 nested-list-order contract, so any
    ``None`` element inside a list is preserved as ``null`` in the
    canonicalized payload.
    """
    if isinstance(payload, dict):
        return {
            key: _strip_none(inner)
            for key, inner in payload.items()
            if inner is not None
        }
    if isinstance(payload, list):
        return [_strip_none(item) for item in payload]
    return payload


def _canonicalize(payload: Any) -> str:
    """Serialize ``payload`` to the canonical JSON form used for digesting."""
    return json.dumps(
        _strip_none(payload),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=_json_default,
    )


def compute_digest(plan: LessonPlan) -> str:
    """Return the sha256 hex-digest of the canonical-JSON serialization of ``plan``.

    The stored ``digest`` field is cleared before hashing so that the digest
    of a plan remains stable across "compute -> store -> recompute" cycles.
    """
    payload = plan.model_dump(mode="json")
    payload["digest"] = ""
    canonical = _canonicalize(payload)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def assert_digest_matches(plan: LessonPlan) -> None:
    """Validate that ``plan.digest`` equals :func:`compute_digest` (AC-B.10)."""
    computed = compute_digest(plan)
    if plan.digest != computed:
        raise ValueError(
            f"LessonPlan digest mismatch: stored={plan.digest!r} computed={computed!r}"
        )


__all__ = [
    "assert_digest_matches",
    "compute_digest",
]
