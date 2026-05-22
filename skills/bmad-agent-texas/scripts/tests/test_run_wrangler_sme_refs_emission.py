"""Story 34-4 regression tests for metadata.json sme_refs emission."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_THIS_DIR = Path(__file__).resolve().parent
_RUNNER_PATH = _THIS_DIR.parent / "run_wrangler.py"
_FIXTURE_DIR = _THIS_DIR / "fixtures" / "wrangler-golden"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_story_34_4_under_test", _RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_story_34_4_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


_runner = _load_runner()


def _write_directive(tmp_path: Path, body: dict) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    return path


def _outcome(
    ref_id: str,
    *,
    provider: str = "local_file",
    locator: str = "sources/primary.md",
    content_text: str = "Primary source body",
) -> object:
    return _runner.SourceOutcome(
        ref_id=ref_id,
        provider=provider,
        locator=locator,
        role="primary",
        description=f"{ref_id} description",
        extractor_used="test-extractor",
        fetched_at="2026-05-22T12:00:00Z",
        content_text=content_text,
        section_title=f"Section {ref_id}",
        report=object(),
    )


def test_metadata_json_emits_sme_refs_with_source_ref_shape(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    first_text = "first source body"
    second_text = "second source body"

    metadata_path = _runner._write_metadata_json(
        bundle,
        "TEST-34-4",
        [
            _outcome(
                "src-local",
                locator="corpus/local.md",
                content_text=first_text,
            ),
            _outcome(
                "src-url",
                provider="url",
                locator="https://example.test/source",
                content_text=second_text,
            ),
        ],
        "2026-05-22T12:00:00Z",
    )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert [entry["ref_id"] for entry in metadata["provenance"]] == [
        "src-local",
        "src-url",
    ]
    assert metadata["sme_refs"] == [
        {
            "source_id": "src-local",
            "path": "corpus/local.md",
            "content_digest": hashlib.sha256(first_text.encode("utf-8")).hexdigest(),
        },
        {
            "source_id": "src-url",
            "path": None,
            "content_digest": hashlib.sha256(second_text.encode("utf-8")).hexdigest(),
        },
    ]
    assert all(
        set(entry) == {"source_id", "path", "content_digest"}
        for entry in metadata["sme_refs"]
    )


def test_sme_refs_are_per_source_not_whole_bundle_digest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    source_text = "per-source text"
    whole_bundle_text = "# Source bundle\n\nper-source text\n"

    metadata_path = _runner._write_metadata_json(
        bundle,
        "TEST-34-4-DIGEST",
        [_outcome("src-primary", content_text=source_text)],
        "2026-05-22T12:00:00Z",
    )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    emitted_digest = metadata["sme_refs"][0]["content_digest"]
    assert emitted_digest == hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    assert emitted_digest != hashlib.sha256(
        whole_bundle_text.encode("utf-8")
    ).hexdigest()


def test_ignored_rows_are_excluded_from_sme_refs(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-34-4-IGNORED",
            "sources": [
                {
                    "ref_id": "src-primary",
                    "provider": "local_file",
                    "locator": str(_FIXTURE_DIR / "primary.md"),
                    "role": "primary",
                    "description": "primary source",
                    "expected_min_words": 200,
                },
                {
                    "ref_id": "src-ignored",
                    "provider": "local_file",
                    "locator": str(_FIXTURE_DIR / "validation.md"),
                    "role": "ignored",
                    "description": "ignored source",
                    "excluded_reason": "llm-classified-out-of-scope",
                },
            ],
        },
    )

    exit_code = _runner.main(["--directive", str(directive), "--bundle-dir", str(bundle)])
    assert exit_code == _runner.EXIT_COMPLETE
    assert "src-ignored" in capsys.readouterr().err

    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    assert [entry["source_id"] for entry in metadata["sme_refs"]] == ["src-primary"]
    assert [entry["ref_id"] for entry in metadata["provenance"]] == ["src-primary"]
