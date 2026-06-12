"""LLM-driven Section 02A directive composition."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from langchain_core.language_models import BaseChatModel

from app.composers.section_02a._cache import ComposerCache
from app.composers.section_02a._prompt import (
    cache_key_for_prompt,
    corpus_summary_for,
    render_classification_prompt,
)
from app.composers.section_02a.directive_model import (
    Directive,
    DirectiveRole,
    DirectiveSource,
    ExcludedReason,
)

URLS_FILE_BASENAMES = ("urls.txt", "URLS.txt", "Urls.txt")


class DirectiveCompositionError(RuntimeError):
    """Raised when the Section 02A corpus cannot be composed."""


def _walk_corpus_files(corpus_dir: Path) -> list[Path]:
    if not corpus_dir.exists():
        raise DirectiveCompositionError(f"corpus path does not exist: {corpus_dir}")
    if not corpus_dir.is_dir():
        raise DirectiveCompositionError(f"corpus path is not a directory: {corpus_dir}")
    return [
        path
        for path in sorted(corpus_dir.rglob("*"))
        if path.is_file() and path.name not in URLS_FILE_BASENAMES
    ]


def _rule_based_exclusion(file_path: Path) -> ExcludedReason | None:
    if file_path.name == ".gitkeep":
        return ExcludedReason.GIT_MARKER
    if file_path.name == ".DS_Store":
        return ExcludedReason.MACOS_METADATA
    if file_path.name.lower() == "thumbs.db":
        return ExcludedReason.WINDOWS_METADATA
    return None


def _message_content(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    raise DirectiveCompositionError("LLM response content must be a string")


def _load_llm_payload(response_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise DirectiveCompositionError("LLM response must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise DirectiveCompositionError("LLM response JSON must be an object")
    return payload


def _source_from_payload(
    *,
    ref_id: str,
    locator: str,
    payload: dict[str, Any],
) -> DirectiveSource:
    return DirectiveSource(
        ref_id=ref_id,
        locator=locator,
        role=payload["role"],
        expected_min_words=payload.get("expected_min_words"),
        description=payload.get("description"),
    )


def _ignored_source(
    *,
    ref_id: str,
    locator: str,
    excluded_reason: ExcludedReason,
) -> DirectiveSource:
    return DirectiveSource(
        ref_id=ref_id,
        locator=locator,
        role=DirectiveRole.IGNORED,
        excluded_reason=excluded_reason,
        description=f"Rule-excluded Section 02A corpus file: {locator}",
    )


def _classify_with_llm(
    *,
    file_path: Path,
    corpus_dir: Path,
    ref_id: str,
    llm: BaseChatModel,
    cache: ComposerCache,
    corpus_summary: str,
) -> DirectiveSource:
    locator = file_path.relative_to(corpus_dir).as_posix()
    prompt = render_classification_prompt(
        file_path=file_path,
        corpus_dir=corpus_dir,
        corpus_summary=corpus_summary,
    )
    cache_key = cache_key_for_prompt(prompt)
    response_text = cache.get(cache_key)
    if response_text is None:
        response_text = _message_content(llm.invoke(prompt))
        cache.set(cache_key, response_text)
    payload = _load_llm_payload(response_text)
    return _source_from_payload(ref_id=ref_id, locator=locator, payload=payload)


def compose(
    corpus_dir: Path,
    *,
    llm: BaseChatModel,
    cache: ComposerCache | None = None,
    run_id: UUID,
) -> Directive:
    """Compose a validated Section 02A directive from a corpus directory."""

    files = _walk_corpus_files(corpus_dir)
    if not files:
        raise DirectiveCompositionError(f"no files under corpus path: {corpus_dir}")

    composer_cache = cache or ComposerCache()
    corpus_summary = corpus_summary_for(files, corpus_dir)
    sources: list[DirectiveSource] = []
    for index, file_path in enumerate(files, start=1):
        ref_id = f"src-{index:03d}"
        locator = file_path.relative_to(corpus_dir).as_posix()
        excluded_reason = _rule_based_exclusion(file_path)
        if excluded_reason is not None:
            sources.append(
                _ignored_source(
                    ref_id=ref_id,
                    locator=locator,
                    excluded_reason=excluded_reason,
                )
            )
            continue
        sources.append(
            _classify_with_llm(
                file_path=file_path,
                corpus_dir=corpus_dir,
                ref_id=ref_id,
                llm=llm,
                cache=composer_cache,
                corpus_summary=corpus_summary,
            )
        )

    return Directive(
        run_id=run_id,
        corpus_dir=corpus_dir.resolve().as_posix(),
        sources=sources,
        composed_at=datetime.now(tz=UTC),
    )


def write_directive_yaml(directive: Directive, directive_path: Path) -> Path:
    """Write a validated directive YAML using explicit UTF-8 encoding."""

    directive_path.parent.mkdir(parents=True, exist_ok=True)
    payload = directive.model_dump(mode="json")
    text = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        line_break="\n",
    )
    directive_path.write_text(text, encoding="utf-8")
    return directive_path


__all__ = [
    "DirectiveCompositionError",
    "URLS_FILE_BASENAMES",
    "compose",
    "write_directive_yaml",
]
