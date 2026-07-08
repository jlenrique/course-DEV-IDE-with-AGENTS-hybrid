from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app.composers.section_02a.composer import (
    DirectiveCompositionError,
    _walk_corpus_files,
    compose,
)
from app.marcus.orchestrator.g0_enrichment_wiring import _enumerate
from tests.composers.section_02a._helpers import RoutingChatModel, payload


def _write(path: Path, text: str = "body") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_course_root_refuses_as_non_runnable_scope(tmp_path: Path) -> None:
    _write(
        tmp_path / "course.yaml",
        "runtime_contract:\n  runnable_input_scope: lesson_corpus_leaf\n",
    )
    _write(tmp_path / "modules" / "module-01" / "lessons" / "lesson-01" / "source.md")

    with pytest.raises(DirectiveCompositionError, match="non-runnable-scope"):
        _walk_corpus_files(tmp_path)


def test_module_root_refuses_as_non_runnable_scope(tmp_path: Path) -> None:
    _write(tmp_path / "module.yaml", "module_id: module-01\n")
    _write(tmp_path / "lessons" / "lesson-01" / "source.md")

    with pytest.raises(DirectiveCompositionError, match="lesson_corpus_leaf"):
        _walk_corpus_files(tmp_path)


def test_lesson_leaf_passes_without_scanning_ancestors(tmp_path: Path) -> None:
    root = tmp_path / "course-root"
    leaf = root / "modules" / "module-01" / "lessons" / "lesson-01"
    _write(root / "course.yaml", "course_id: c\n")
    _write(root / "modules" / "module-01" / "module.yaml", "module_id: module-01\n")
    _write(leaf / "source.md")

    assert _walk_corpus_files(leaf) == [leaf / "source.md"]


def test_compose_refuses_broad_root_before_llm_invoke(tmp_path: Path) -> None:
    _write(
        tmp_path / "course.yaml",
        "runtime_contract:\n  runnable_input_scope: lesson_corpus_leaf\n",
    )
    _write(tmp_path / "sources" / "course" / "README.md")
    llm = RoutingChatModel(
        responses={
            "README.md": payload(
                role="primary",
                expected_min_words=500,
                description="Should not be invoked.",
            )
        }
    )

    with pytest.raises(DirectiveCompositionError, match="non-runnable-scope"):
        compose(tmp_path, llm=llm, run_id=uuid4())

    assert llm.invoke_count == 0


def test_g0_enrichment_enumeration_inherits_broad_root_refusal(tmp_path: Path) -> None:
    _write(
        tmp_path / "course.yaml",
        "runtime_contract:\n  runnable_input_scope: lesson_corpus_leaf\n",
    )
    _write(tmp_path / "sources" / "course" / "source.md")

    with pytest.raises(DirectiveCompositionError, match="non-runnable-scope"):
        _enumerate(tmp_path)
