"""Shared fixtures for Section 06B tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

RUN_ID = UUID("66666666-6666-4666-8666-666666666666")
PLAN_UNIT_ID = "unit-06b"
SUBMITTED_AT = datetime(2026, 5, 6, 10, 0, tzinfo=UTC)


def fixture_literal_visual_targets() -> dict[str, object]:
    return {
        "plan_unit_id": PLAN_UNIT_ID,
        "target_section": "section-06b",
        "cards": [
            {
                "slide_index": 1,
                "visual_kind": "flowchart",
                "specification": "Show the literal-visual branch.",
                "caption": "Literal visual branch",
            }
        ],
    }


def fixture_build_payload() -> dict[str, object]:
    return {
        "target_section": "section-06b",
        "slide_specifications": [
            {
                "slide_index": 1,
                "visual_kind": "flowchart",
                "specification": "Show the literal-visual branch.",
                "caption": "Literal visual branch",
            }
        ],
    }


__all__ = [
    "PLAN_UNIT_ID",
    "RUN_ID",
    "SUBMITTED_AT",
    "fixture_build_payload",
    "fixture_literal_visual_targets",
]
