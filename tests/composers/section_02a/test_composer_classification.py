from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.composers.section_02a import DirectiveRole, ExcludedReason, compose
from tests.composers.section_02a._helpers import RoutingChatModel, payload


def _write(path: Path, content: bytes = b"fixture") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_compose_classifies_sources_and_skips_known_metadata(tmp_path: Path) -> None:
    for name in [
        ".gitkeep",
        ".DS_Store",
        "Thumbs.db",
        "lesson.docx",
        "visual.png",
        "photo.jpg",
    ]:
        _write(tmp_path / name)

    llm = RoutingChatModel(
        responses={
            "lesson.docx": payload(
                role="primary",
                expected_min_words=500,
                description="Primary lesson content.",
            ),
            "visual.png": payload(description="Supporting visual reference."),
            "photo.jpg": payload(description="Supporting photo reference."),
        }
    )

    directive = compose(tmp_path, llm=llm)
    by_locator = {source.locator: source for source in directive.sources}

    assert by_locator[".gitkeep"].role is DirectiveRole.IGNORED
    assert by_locator[".gitkeep"].excluded_reason is ExcludedReason.GIT_MARKER
    assert by_locator[".DS_Store"].excluded_reason is ExcludedReason.MACOS_METADATA
    assert by_locator["Thumbs.db"].excluded_reason is ExcludedReason.WINDOWS_METADATA
    assert by_locator["lesson.docx"].role is DirectiveRole.PRIMARY
    assert by_locator["visual.png"].expected_min_words is None
    assert by_locator["photo.jpg"].expected_min_words is None
    assert llm.invoke_count == 3


def test_compose_raises_validation_error_on_malformed_llm_classification(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "lesson.docx")
    llm = RoutingChatModel(
        responses={
            "lesson.docx": payload(
                role="primary",
                expected_min_words=None,
                description="Malformed missing word floor.",
            )
        }
    )

    with pytest.raises(ValidationError, match="requires expected_min_words"):
        compose(tmp_path, llm=llm)

