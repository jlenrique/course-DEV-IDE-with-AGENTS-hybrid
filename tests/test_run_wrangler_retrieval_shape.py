"""AC-T.5 — run_wrangler.py dispatcher-wiring regression (Story 27-2 AC-B.6).

Three behavioral tests:
  1. retrieval-shape directive routes through the dispatcher → schema v1.1 output.
  2. legacy locator-shape directive preserves the existing `_fetch_source` path
     → schema v1.0 output, no retrieval-shape fields.
  3. malformed-shape directive (both `intent` and `provider+locator` keys) →
     exit 30 with a clear error.

Plus AC-C.11 writer-discriminant teeth: mismatched `code_path` + outcome types
raise `ValueError` on both directions.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import responses
import yaml

_THIS_DIR = Path(__file__).resolve().parent
_WRANGLER_PATH = (
    _THIS_DIR.parent
    / "skills"
    / "bmad-agent-texas"
    / "scripts"
    / "run_wrangler.py"
)
_SCITE_FIXTURE_DIR = _THIS_DIR / "fixtures" / "retrieval" / "scite"
_LEGACY_FIXTURE_DIR = (
    _THIS_DIR.parent
    / "skills"
    / "bmad-agent-texas"
    / "scripts"
    / "tests"
    / "fixtures"
    / "wrangler-golden"
)


def _load_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_under_test_2", _WRANGLER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_under_test_2"] = mod
    spec.loader.exec_module(mod)
    return mod


_runner = _load_runner()


def _write_directive(tmp_path: Path, body: dict[str, Any]) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def _scite_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCITE_USER_NAME", "test-user")
    monkeypatch.setenv("SCITE_PASSWORD", "test-pass")


# ---------------------------------------------------------------------------
# AC-T.5 Test 1 — retrieval-shape routes through dispatcher (schema v1.1)
# ---------------------------------------------------------------------------


def test_retrieval_shape_directive_routes_through_dispatcher(tmp_path: Path) -> None:
    """Retrieval-shape directive → dispatcher.dispatch() → schema v1.1 output."""
    from retrieval.scite_provider import SCITE_MCP_URL

    from tests._helpers.mcp_fixtures import jsonrpc_response

    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-RETRIEVAL-001",
            "sources": [
                {
                    "ref_id": "src-retrieval-1",
                    "role": "primary",
                    "intent": "sleep hygiene studies",
                    "provider_hints": [{"provider": "scite"}],
                    "acceptance_criteria": {"mechanical": {"min_results": 1}},
                    "iteration_budget": 3,
                }
            ],
        },
    )

    fixture = json.loads(
        (_SCITE_FIXTURE_DIR / "search_happy.json").read_text(encoding="utf-8")
    )

    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=fixture))
        envelope = _runner.run(directive, bundle)

    # Envelope-level assertions (result.yaml shape).
    assert envelope["schema_version"] == "1.1"
    assert envelope["directive_shape"] == "retrieval"
    assert envelope["rows_total"] == 3

    # Extraction-report.yaml assertions (v1.1 additive fields per source entry).
    report = yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )
    assert report["schema_version"] == "1.1"
    assert len(report["sources"]) == 3
    first_row = report["sources"][0]
    # All 6 v1.1 additive fields must be present. PATCH-9 (2026-04-18): prior
    # loop had 5 fields; AC-T.5 Test 1 spec'd all 6, including convergence_signal.
    for v1_1_field in (
        "retrieval_intent",
        "provider_hints",
        "cross_validate",
        "convergence_signal",
        "source_origin",
        "tracy_row_ref",
    ):
        assert v1_1_field in first_row, (
            f"retrieval-shape source entry missing v1.1 field: {v1_1_field}"
        )
    # convergence_signal is None for single-provider dispatch (no cross-validation).
    assert first_row["convergence_signal"] is None
    assert first_row["retrieval_intent"] == "sleep hygiene studies"


# ---------------------------------------------------------------------------
# AC-T.5 Test 2 — legacy locator-shape preserves legacy path (schema v1.0)
# ---------------------------------------------------------------------------


def test_locator_shape_directive_preserves_legacy_path(tmp_path: Path) -> None:
    """Legacy directive → existing `_fetch_source` path → schema v1.0, no v1.1 fields."""
    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-LOCATOR-001",
            "sources": [
                {
                    "ref_id": "src-locator-1",
                    "provider": "local_file",
                    "locator": str(_LEGACY_FIXTURE_DIR / "primary.md"),
                    "role": "primary",
                    "description": "Legacy locator-shape directive",
                    "expected_min_words": 200,
                }
            ],
        },
    )

    envelope = _runner.run(directive, bundle)

    # Legacy envelope shape unchanged (no schema_version top-level; materials, etc.).
    # PATCH-8 (2026-04-18): explicit assert that `schema_version` is absent from
    # the legacy result envelope — prior version only checked `materials in
    # envelope`, which would pass even if the legacy path started emitting a
    # top-level schema_version by accident.
    assert "materials" in envelope
    assert "schema_version" not in envelope, (
        "Legacy locator-shape result.yaml must NOT carry a top-level "
        "schema_version field (AC-B.6 dual-emit contract: v1.0 is the "
        "extraction-report.yaml schema, NOT the result envelope)."
    )
    assert "directive_shape" not in envelope, (
        "Legacy envelope must not carry `directive_shape` — that field "
        "is retrieval-shape-specific (v1.1 addition)."
    )
    # Extraction-report.yaml stays on v1.0 (no v1.1 shape drift).
    report = yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )
    assert report["schema_version"] == "1.0"
    first_source = report["sources"][0]
    # No v1.1 additive fields on legacy path (anti-pattern #3 preservation).
    for forbidden in (
        "retrieval_intent",
        "provider_hints",
        "cross_validate",
        "convergence_signal",
    ):
        assert forbidden not in first_source, (
            f"locator-shape entry must not carry v1.1 field: {forbidden}"
        )


def test_local_markdown_authority_and_extraction_share_captured_aba_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "primary.md"
    original = b"\\# Original\n\nExact authority text.\n"
    source.write_bytes(original)

    def _aba_capture(_path: Path) -> bytes:
        source.write_text("# Changed\n\nDifferent text.\n", encoding="utf-8")
        source.write_bytes(original)
        return original

    monkeypatch.setattr(_runner, "_read_stable_regular_bytes", _aba_capture)
    outcome = _runner._wrangle_source(
        {
            "ref_id": "src-changing-md",
            "provider": "local_file",
            "locator": str(source),
            "role": "primary",
        },
        "2026-07-13T00:00:00Z",
    )

    assert outcome.content_text.startswith("# Original")
    assert outcome.authority_text == original.decode("utf-8")
    assert outcome.error_detail is None


# ---------------------------------------------------------------------------
# AC-T.5 Test 3 — malformed-shape directive exits 30
# ---------------------------------------------------------------------------


def test_malformed_shape_directive_exits_30(tmp_path: Path) -> None:
    """Row with both `intent` and `provider+locator` keys → DirectiveError (exit 30)."""
    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-MALFORMED-001",
            "sources": [
                {
                    "ref_id": "src-ambig-1",
                    "role": "primary",
                    "intent": "oops",
                    "provider_hints": [{"provider": "scite"}],
                    "provider": "local_file",
                    "locator": "path/to/file",
                }
            ],
        },
    )

    with pytest.raises(_runner.DirectiveError, match="ambiguous shape"):
        _runner.run(directive, bundle)


# ---------------------------------------------------------------------------
# AC-C.11 — writer-discriminant raises on mismatched row / code_path
# ---------------------------------------------------------------------------


def test_write_extraction_report_rejects_retrieval_row_on_locator_path(
    tmp_path: Path,
) -> None:
    """RetrievalOutcome + code_path='locator' → ValueError (AC-C.11 teeth)."""
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    bogus = _runner.RetrievalOutcome(
        ref_id="x",
        role="primary",
        fetched_at="2026-04-18T00:00:00Z",
        intent="",
        provider_hints=[],
        cross_validate=False,
        source_origin="operator-named",
        tracy_row_ref=None,
        rows=[],
        acceptance_met=False,
        iterations_used=0,
        refinement_log=[],
    )
    with pytest.raises(ValueError, match="non-locator row on locator code path"):
        _runner._write_extraction_report(
            bundle,
            "RUN-1",
            "blocked",
            [bogus],
            [],
            [],
            "2026-04-18T00:00:00Z",
            code_path="locator",
        )


def test_write_extraction_report_rejects_locator_row_on_retrieval_path(
    tmp_path: Path,
) -> None:
    """SourceOutcome + code_path='retrieval' → ValueError (AC-C.11 teeth)."""
    from dataclasses import asdict  # noqa: F401 — kept for potential future use

    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    # Build a minimal SourceOutcome via the internal dataclass.
    bogus = _runner.SourceOutcome(
        ref_id="x",
        provider="local_file",
        locator="/tmp/fake",
        role="primary",
        description="test",
        extractor_used="local_text_read",
        fetched_at="2026-04-18T00:00:00Z",
        content_text="",
        section_title="",
        report=None,
    )
    with pytest.raises(ValueError, match="non-retrieval row on retrieval code path"):
        _runner._write_extraction_report(
            bundle,
            "RUN-1",
            "blocked",
            [bogus],
            [],
            [],
            "2026-04-18T00:00:00Z",
            code_path="retrieval",
        )
