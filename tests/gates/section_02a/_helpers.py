"""Shared fixtures for Section 02A poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.composers.section_02a.directive_model import (
    Directive,
    DirectiveRole,
    DirectiveSource,
)

RUN_ID = UUID("11111111-1111-4111-8111-111111111111")


def fixture_directive() -> Directive:
    return Directive(
        run_id=RUN_ID,
        corpus_dir="C:/course/corpus",
        composed_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        sources=[
            DirectiveSource(
                src_id="src-001",
                locator="primary.docx",
                role=DirectiveRole.PRIMARY,
                description="Primary source",
                expected_min_words=120,
            ),
            DirectiveSource(
                src_id="src-002",
                locator="support.png",
                role=DirectiveRole.SUPPORTING,
                description="Supporting image",
            ),
            DirectiveSource(
                src_id="src-003",
                locator="notes.md",
                role=DirectiveRole.SUPPORTING,
                description="Supporting notes",
                expected_min_words=50,
            ),
        ],
    )


__all__ = ["RUN_ID", "fixture_directive"]
