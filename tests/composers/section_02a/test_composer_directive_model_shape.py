from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.composers.section_02a.directive_model import (
    DIRECTIVE_ROLE_LITERAL_ADAPTER,
    Directive,
    DirectiveRole,
    DirectiveSource,
    ExcludedReason,
)


def _source(**overrides: object) -> DirectiveSource:
    payload = {
        "src_id": "src-001",
        "locator": "lesson.docx",
        "role": DirectiveRole.PRIMARY,
        "expected_min_words": 500,
        "description": "Primary lesson source.",
    }
    payload.update(overrides)
    return DirectiveSource(**payload)


def test_directive_role_closed_enum_rejects_red_values() -> None:
    assert _source(role="primary").role is DirectiveRole.PRIMARY

    with pytest.raises(ValidationError):
        _source(role="bogus")
    with pytest.raises(ValidationError):
        DIRECTIVE_ROLE_LITERAL_ADAPTER.validate_python("bogus")


def test_directive_source_forbids_extra_and_validates_assignment() -> None:
    source = _source()

    with pytest.raises(ValidationError):
        DirectiveSource(
            src_id="src-001",
            locator="lesson.docx",
            role="primary",
            expected_min_words=500,
            unexpected=True,
        )
    with pytest.raises(ValidationError):
        source.role = "bogus"  # type: ignore[assignment]


def test_role_conditional_invariants() -> None:
    with pytest.raises(ValidationError, match="requires excluded_reason"):
        _source(role="ignored", expected_min_words=None)
    with pytest.raises(ValidationError, match="forbids expected_min_words"):
        _source(
            role="ignored",
            excluded_reason=ExcludedReason.GIT_MARKER,
            expected_min_words=1,
        )
    with pytest.raises(ValidationError, match="requires expected_min_words"):
        _source(locator="lesson.md", expected_min_words=None)
    with pytest.raises(ValidationError, match="forbids excluded_reason"):
        _source(excluded_reason=ExcludedReason.LLM_CLASSIFIED_OUT_OF_SCOPE)


def test_trial_2_binary_file_anti_pattern_rejected() -> None:
    with pytest.raises(ValidationError, match="Trial-2 finding #2 anti-pattern"):
        _source(
            locator="visual.png",
            role=DirectiveRole.SUPPORTING,
            expected_min_words=200,
        )


def test_directive_top_level_shape_and_schema() -> None:
    directive = Directive(
        run_id=uuid4(),
        corpus_dir="C:/tmp/corpus",
        sources=[_source()],
        composed_at=datetime.now(tz=UTC),
    )

    dumped = directive.model_dump(mode="json")
    assert Directive.model_validate(dumped).schema_version == 1
    schema = Directive.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["DirectiveSource"]["additionalProperties"] is False

    with pytest.raises(ValidationError, match="timezone-aware"):
        Directive(
            run_id=uuid4(),
            corpus_dir="C:/tmp/corpus",
            sources=[_source()],
            composed_at=datetime(2026, 5, 5, 12, 0, 0),
        )
