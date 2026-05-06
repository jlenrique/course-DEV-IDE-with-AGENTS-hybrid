"""Shared fixtures for Section 04.55 run-constants lock tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

RUN_ID = UUID("22222222-2222-4222-8222-222222222222")
SUBMITTED_AT = datetime(2026, 5, 5, 12, 0, tzinfo=UTC)


def fixture_run_constants() -> dict[str, object]:
    return {
        "run_id": "RUN-CONSTANTS-001",
        "lesson_slug": "agentic-production-platform",
        "experience_profile": "visual-led",
        "cluster_density": {
            "establish": 0.2,
            "tension": 0.3,
            "develop": 0.3,
            "resolve": 0.2,
        },
        "motion_enabled": False,
    }


__all__ = ["RUN_ID", "SUBMITTED_AT", "fixture_run_constants"]

