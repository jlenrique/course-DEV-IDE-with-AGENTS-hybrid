"""Shared Pydantic-v2 idiom helpers for the `app.models.state` family.

Centralizes the tz-aware-datetime + UUID4-version-pin validators so the eight
state models inherit them by reference rather than duplicating per file.
The bundle §3 14-idiom checklist mandates these on every applicable field;
re-implementing per file invites G6 MUST-FIX drift like the 31-1 datetime
findings.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

__all__ = ["enforce_tz_aware", "enforce_uuid4_version"]


def enforce_tz_aware(value: datetime) -> datetime:
    """Field validator: reject naive datetimes (Pydantic v2 idiom #2).

    Use as ``@field_validator("<field>")`` body returning ``enforce_tz_aware(v)``.
    Naive datetimes are the G6 MF-4 hazard from Story 31-1; this helper makes
    skipping it a typo, not a default.
    """
    if value.tzinfo is None:
        raise ValueError("datetime field must be timezone-aware")
    return value


def enforce_uuid4_version(value: UUID) -> UUID:
    """Field validator: reject UUIDs that are not version 4 (Pydantic v2 idiom #3).

    Pydantic accepts any UUID into a ``UUID``-typed field by default; this
    helper enforces the version-4 contract that the SoT for identity fields
    is the random UUID4 namespace, not UUID1/3/5. Hardens against the G6 SF-5
    pattern from Story 31-1.
    """
    if value.version != 4:
        raise ValueError(f"UUID field must be UUID4; got version={value.version}")
    return value
