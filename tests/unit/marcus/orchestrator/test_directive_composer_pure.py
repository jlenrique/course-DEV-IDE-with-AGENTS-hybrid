"""Pure-function tests for ``compose_directive`` (Story 7a.1, AC-7.1-A)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.orchestrator.directive_composer import (
    DEFAULT_EXPECTED_MIN_WORDS,
    ComposedDirectiveSource,
    DirectiveCompositionError,
    EmptyCorpusError,
    compose_directive,
)

RUN_ID = "TRIAL-7A1-TEST"


def _write(tmp: Path, name: str, body: str = "lorem ipsum dolor sit amet") -> Path:
    target = tmp / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


def test_pure_function_no_side_effects(tmp_path: Path) -> None:
    """Composer reads files only — no env vars, no network, no subprocess."""
    _write(tmp_path, "intro.md")
    _write(tmp_path, "chapter-1.md")
    # Ensure no module-level side effects by executing twice; outputs equal byte-for-byte.
    first = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    second = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    assert first == second


def test_flat_corpus_default_walker(tmp_path: Path) -> None:
    """Flat dir with N files → primary + N-1 supporting, sorted, local_file provider."""
    _write(tmp_path, "appendix.md")
    _write(tmp_path, "chapter-1.md")
    _write(tmp_path, "intro.md")
    composed = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    assert composed.run_id == RUN_ID
    assert len(composed.sources) == 3
    refs = [s.ref_id for s in composed.sources]
    assert refs == ["src-001", "src-002", "src-003"]
    roles = [s.role for s in composed.sources]
    assert roles == ["primary", "supporting", "supporting"]
    providers = {s.provider for s in composed.sources}
    assert providers == {"local_file"}
    # Sorted alphabetically (rglob then sorted on POSIX form)
    locators = [s.locator for s in composed.sources]
    assert locators == ["appendix.md", "chapter-1.md", "intro.md"]


def test_nested_corpus_uses_relative_posix_paths(tmp_path: Path) -> None:
    """Nested dir paths emit cross-platform-stable POSIX locators (W-R6)."""
    _write(tmp_path, "module-1/intro.md")
    _write(tmp_path, "module-1/lesson-a.md")
    _write(tmp_path, "module-2/lesson-b.md")
    composed = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    assert len(composed.sources) == 3
    locators = [s.locator for s in composed.sources]
    # POSIX form on every platform — no backslashes
    assert all("\\" not in loc for loc in locators)
    assert "module-1/intro.md" in locators


def test_urls_txt_emits_url_provider_after_files(tmp_path: Path) -> None:
    """urls.txt sibling → provider:url entries appended after on-disk files."""
    _write(tmp_path, "intro.md")
    _write(tmp_path, "urls.txt", "https://example.com/article-1\n# comment\n\nhttps://example.com/article-2\n")
    composed = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    providers = [s.provider for s in composed.sources]
    assert providers == ["local_file", "url", "url"]
    assert composed.sources[1].locator == "https://example.com/article-1"
    assert composed.sources[2].locator == "https://example.com/article-2"
    # role: primary lands on the first emitted entry overall
    assert composed.sources[0].role == "primary"


def test_operator_overrides_pin_expected_min_words(tmp_path: Path) -> None:
    """Operator can override expected_min_words for a specific source."""
    _write(tmp_path, "intro.md")
    _write(tmp_path, "chapter-1.md")
    composed = compose_directive(
        corpus_path=tmp_path,
        run_id=RUN_ID,
        operator_directives={
            "sources": {"src-001": {"expected_min_words": 500}},
        },
    )
    assert composed.sources[0].expected_min_words == 500
    assert composed.sources[1].expected_min_words == DEFAULT_EXPECTED_MIN_WORDS


def test_operator_override_unknown_ref_id_raises(tmp_path: Path) -> None:
    """Override referencing an unknown ref_id raises DirectiveCompositionError (W-R2)."""
    _write(tmp_path, "intro.md")
    with pytest.raises(DirectiveCompositionError, match="unknown ref_ids"):
        compose_directive(
            corpus_path=tmp_path,
            run_id=RUN_ID,
            operator_directives={
                "sources": {"src-999": {"expected_min_words": 500}},
            },
        )


def test_operator_override_unknown_field_raises(tmp_path: Path) -> None:
    """Override containing a field not on ComposedDirectiveSource raises."""
    _write(tmp_path, "intro.md")
    with pytest.raises(DirectiveCompositionError, match="unknown field"):
        compose_directive(
            corpus_path=tmp_path,
            run_id=RUN_ID,
            operator_directives={
                "sources": {"src-001": {"not_a_real_field": True}},
            },
        )


def test_empty_corpus_raises(tmp_path: Path) -> None:
    """Empty corpus dir raises EmptyCorpusError — NOT silent empty directive."""
    with pytest.raises(EmptyCorpusError):
        compose_directive(corpus_path=tmp_path, run_id=RUN_ID)


def test_missing_corpus_raises(tmp_path: Path) -> None:
    """Missing corpus path raises EmptyCorpusError with explicit message."""
    missing = tmp_path / "does-not-exist"
    with pytest.raises(EmptyCorpusError, match="does not exist"):
        compose_directive(corpus_path=missing, run_id=RUN_ID)


def test_explicit_source_authority_map_overrides_default_walker(
    tmp_path: Path,
) -> None:
    """Caller-provided source_authority_map skips the default walker entirely."""
    _write(tmp_path, "intro.md")
    explicit = {
        "src-A": ComposedDirectiveSource(
            ref_id="src-A",
            provider="notion",
            locator="https://notion.so/page-id",
            role="primary",
            description="Notion source pinned by caller",
            expected_min_words=300,
        )
    }
    composed = compose_directive(
        corpus_path=tmp_path,
        run_id=RUN_ID,
        source_authority_map=explicit,
    )
    assert len(composed.sources) == 1
    assert composed.sources[0].provider == "notion"
    assert composed.sources[0].ref_id == "src-A"


def test_purity_no_environment_variables_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Composer must not depend on env state — change env, output unchanged."""
    _write(tmp_path, "intro.md")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    expected = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    monkeypatch.setenv("EDITOR", "emacs")
    actual = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    assert expected == actual


def test_composed_directive_to_dict_round_trip_keys(tmp_path: Path) -> None:
    """to_dict() emits canonical Texas directive shape (run_id + sources[]).

    Cross-verified against tests/fixtures/specialists/texas/fixture_directive.yaml.
    """
    _write(tmp_path, "intro.md")
    composed = compose_directive(corpus_path=tmp_path, run_id=RUN_ID)
    payload = composed.to_dict()
    assert set(payload.keys()) == {"run_id", "sources"}
    assert isinstance(payload["sources"], list)
    src0 = payload["sources"][0]
    assert set(src0.keys()) == {
        "ref_id",
        "provider",
        "locator",
        "role",
        "description",
        "expected_min_words",
    }
