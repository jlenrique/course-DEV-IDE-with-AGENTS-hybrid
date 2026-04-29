"""Materialization tests for ``materialize_directive`` (Story 7a.1, AC-7.1-B).

Covers write-roundtrip, digest stability, idempotency, and golden bytes (M-R6).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.directive_composer import (
    ComposedDirective,
    ComposedDirectiveSource,
    compose_directive,
    materialize_directive,
)

RUN_ID = "TRIAL-7A1-MATERIALIZE"

GOLDEN_FIXTURE_PATH = (
    Path(__file__).resolve().parents[4]
    / "tests"
    / "fixtures"
    / "directives"
    / "composed_directive_golden.yaml.bytes"
)


def _three_file_corpus(tmp_path: Path) -> Path:
    for name in ("intro.md", "chapter-1.md", "appendix.md"):
        (tmp_path / name).write_text("body", encoding="utf-8")
    return tmp_path


def test_write_roundtrip(tmp_path: Path) -> None:
    """materialize writes a parseable directive.yaml under run_dir."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _three_file_corpus(corpus)
    run_dir = tmp_path / "run-001"
    composed = compose_directive(corpus_path=corpus, run_id=RUN_ID)
    directive_path, digest = materialize_directive(composed, run_dir)
    assert directive_path == run_dir / "directive.yaml"
    assert directive_path.exists()
    assert len(digest) == 64  # sha256 hex
    parsed = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    assert parsed["run_id"] == RUN_ID
    assert len(parsed["sources"]) == 3


def test_digest_stability_across_runs(tmp_path: Path) -> None:
    """Re-materializing the same composed directive produces an identical digest."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _three_file_corpus(corpus)
    composed = compose_directive(corpus_path=corpus, run_id=RUN_ID)
    run_dir_a = tmp_path / "run-a"
    run_dir_b = tmp_path / "run-b"
    _, digest_a = materialize_directive(composed, run_dir_a)
    _, digest_b = materialize_directive(composed, run_dir_b)
    assert digest_a == digest_b
    bytes_a = (run_dir_a / "directive.yaml").read_bytes()
    bytes_b = (run_dir_b / "directive.yaml").read_bytes()
    assert bytes_a == bytes_b


def test_idempotent_overwrite(tmp_path: Path) -> None:
    """Materializing twice into the same run_dir is byte-stable."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _three_file_corpus(corpus)
    run_dir = tmp_path / "run-only"
    composed = compose_directive(corpus_path=corpus, run_id=RUN_ID)
    _, first = materialize_directive(composed, run_dir)
    _, second = materialize_directive(composed, run_dir)
    assert first == second


def test_run_dir_created_when_absent(tmp_path: Path) -> None:
    """materialize creates the run_dir parent chain (mkdir parents=True)."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _three_file_corpus(corpus)
    nested = tmp_path / "deeply" / "nested" / "run-dir"
    composed = compose_directive(corpus_path=corpus, run_id=RUN_ID)
    directive_path, _ = materialize_directive(composed, nested)
    assert directive_path.parent == nested
    assert nested.exists()


def test_golden_bytes_fixture_present_and_matches(tmp_path: Path) -> None:
    """M-R6: regression-pin the canonical 3-file directive bytes against a golden fixture.

    If ruamel emission shifts (formatting, key order, indent), the fixture must
    be reviewed and re-baselined explicitly. This test rejects silent drift.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    _three_file_corpus(corpus)
    composed = compose_directive(
        corpus_path=corpus, run_id="GOLDEN-RUN-001"
    )
    run_dir = tmp_path / "golden-run"
    directive_path, _ = materialize_directive(composed, run_dir)
    actual_bytes = directive_path.read_bytes()
    if not GOLDEN_FIXTURE_PATH.exists():
        pytest.skip(
            "Golden bytes fixture missing; baseline at "
            f"{GOLDEN_FIXTURE_PATH} (write actual_bytes to seed)."
        )
    expected = GOLDEN_FIXTURE_PATH.read_bytes()
    assert actual_bytes == expected, (
        "directive.yaml bytes drifted from golden fixture; review ruamel "
        f"output and re-baseline {GOLDEN_FIXTURE_PATH} if intentional."
    )


def test_materialize_explicit_directive_with_url_source(tmp_path: Path) -> None:
    """Materialize a hand-built ComposedDirective with mixed providers."""
    composed = ComposedDirective(
        run_id="MIXED-PROVIDERS",
        sources=(
            ComposedDirectiveSource(
                ref_id="src-001",
                provider="local_file",
                locator="intro.md",
                role="primary",
                description="seed",
                expected_min_words=200,
            ),
            ComposedDirectiveSource(
                ref_id="src-002",
                provider="url",
                locator="https://example.com/article",
                role="supporting",
                description="from urls.txt",
                expected_min_words=200,
            ),
        ),
    )
    run_dir = tmp_path / "mixed"
    directive_path, digest = materialize_directive(composed, run_dir)
    assert directive_path.exists()
    parsed = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    assert {s["provider"] for s in parsed["sources"]} == {"local_file", "url"}
    # Re-derive digest from disk bytes — guard against mismatched return value.
    on_disk_digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    assert digest == on_disk_digest
