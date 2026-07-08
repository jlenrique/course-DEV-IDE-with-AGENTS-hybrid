"""CLI-side adapter bridging Section 02A composer to the path/digest contract.

Owned by the Section 02A composer module (Winston W-A1, 2026-05-21 SCP section 7)
so future consumers reuse this call-shape bridge instead of reinventing it.

The Section 02A composer module exposes:
    compose(corpus_dir, *, llm, cache, run_id) -> Directive
    write_directive_yaml(directive, path) -> Path

Callers historically expect:
    compose_legacy(...) -> Composed
    materialize(composed, run_dir) -> (Path, str)

This adapter is the canonical bridge between those shapes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from langchain_core.language_models import BaseChatModel

from app.composers.section_02a._cache import ComposerCache
from app.composers.section_02a.composer import (
    assert_lesson_corpus_leaf,
    compose,
    write_directive_yaml,
)


def compose_and_write(
    corpus_dir: Path,
    run_dir: Path,
    *,
    run_id: UUID,
    llm: BaseChatModel | None = None,
    gamma_settings: list[dict[str, Any]] | None = None,
) -> tuple[Path, str]:
    """Compose a Section 02A directive for ``corpus_dir`` and write it.

    Threads operator-supplied run_id (J-A1(a)) and writes model_resolution_trail
    sidecar (J-A1(b)).
    """

    assert_lesson_corpus_leaf(corpus_dir)

    handle = None
    if llm is None:
        from app.models.adapter import make_chat_model

        handle = make_chat_model("marcus")
        llm = handle.chat

    run_dir.mkdir(parents=True, exist_ok=True)
    if handle is not None:
        (run_dir / "model_resolution_trail.json").write_text(
            json.dumps(
                [handle.entry.model_dump(mode="json")],
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    directive = compose(corpus_dir, llm=llm, cache=ComposerCache(), run_id=run_id)
    directive.gamma_settings = gamma_settings
    directive_path = run_dir / "directive.yaml"
    write_directive_yaml(directive, directive_path)
    digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return directive_path, digest


__all__ = ["compose_and_write"]
