"""Shared fixtures for Section 07C tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

RUN_ID = UUID("77777777-7777-4777-8777-777777777777")
PLAN_UNIT_ID = "unit-07c"
SUBMITTED_AT = datetime(2026, 5, 6, 10, 15, tzinfo=UTC)
HTML_DIGEST = "b" * 64


def fixture_storyboard_targets() -> dict[str, object]:
    return {
        "plan_unit_id": PLAN_UNIT_ID,
        "target_section": "section-07c",
        "slides": [
            {
                "slide_index": 1,
                "title": "Opening",
                "body": "Introduce the operator build.",
                "caption": "Storyboard opening",
            }
        ],
    }


def fixture_build_payload() -> dict[str, object]:
    return {
        "target_section": "section-07c",
        "storyboard_html_path": "storyboard/review.html",
        "slide_count": 1,
        "storyboard_html_digest": HTML_DIGEST,
    }


__all__ = [
    "HTML_DIGEST",
    "PLAN_UNIT_ID",
    "RUN_ID",
    "SUBMITTED_AT",
    "fixture_build_payload",
    "fixture_storyboard_targets",
]
