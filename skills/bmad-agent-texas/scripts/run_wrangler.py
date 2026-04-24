"""Texas runtime wrangling runner.

Executes the Marcus -> Texas delegation contract end-to-end:
  1. Load a wrangling directive YAML
  2. For each source, dispatch to the appropriate fetch helper and extract text
  3. Run extraction_validator.validate_extraction per source
  4. Run cross_validator.cross_validate for each validation-role asset
  5. Write the full bundle: extracted.md, metadata.json, manifest.json,
     extraction-report.yaml, ingestion-evidence.md, result.yaml
  6. Emit a structured result to stdout and exit with a status-matched code.

Invocation (direct-path; skills/bmad-agent-texas uses hyphens so -m is unavailable):

    python skills/bmad-agent-texas/scripts/run_wrangler.py \\
        --directive <path-to-directive.yaml> \\
        --bundle-dir <bundle-directory> \\
        [--json]

Exit codes:
  0  complete                — all sources at tier 1
 10  complete_with_warnings  — one or more sources at tier 2 but all passed
 20  blocked                 — any source at tier 3/4 after fallbacks, OR
                               unsupported provider, OR fetch failure
 30  directive/IO error      — malformed directive, missing files, etc.

The runner embodies the "30-line-stub tripwire is non-negotiable" contract:
thin extractions (tier DEGRADED/FAILED) exit 20 and are surfaced as blocking
issues in result.yaml. See references/extraction-report-schema.md for the
canonical output shape and references/delegation-contract.md for the
envelope contract with Marcus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Add the repo root to sys.path so we can import sibling scripts without
# requiring the tree to be packaged. Hyphenated directory names prevent
# standard -m invocation; this is the boring-technology workaround.
_THIS_DIR = Path(__file__).resolve().parent
# _THIS_DIR                 = .../skills/bmad-agent-texas/scripts/
# _THIS_DIR.parents[0]      = .../skills/bmad-agent-texas/
# _THIS_DIR.parents[1]      = .../skills/
# _THIS_DIR.parents[2]      = repo root
_REPO_ROOT = _THIS_DIR.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from marcus.dispatch.contract import (  # noqa: E402
    DispatchKind,
    DispatchOutcome,
    build_dispatch_envelope,
    build_dispatch_receipt,
)

# Load Texas library modules by path (the hyphenated parent path blocks import).
from scripts.utilities.skill_module_loader import load_module_from_path  # noqa: E402

_extraction_validator = load_module_from_path(
    "texas_extraction_validator",
    _THIS_DIR / "extraction_validator.py",
)
_cross_validator = load_module_from_path(
    "texas_cross_validator",
    _THIS_DIR / "cross_validator.py",
)
_source_ops = load_module_from_path(
    "texas_source_wrangler_operations",
    _THIS_DIR / "source_wrangler_operations.py",
)
_cli_encoding = load_module_from_path(
    "texas_cli_encoding",
    _THIS_DIR / "_cli_encoding.py",
)

# Story 26-7 AC-C.2 + code-review finding: fire the guard at import time,
# not just in main(). If this module is `python -m`-loaded (or imported
# by another harness), any import-time print — from sibling modules,
# from tracebacks during load, from wrapper scripts — would hit stdout
# BEFORE main() runs. The guard must precede any possible stdout write.
_cli_encoding.ensure_utf8_stdout()


VALIDATOR_VERSION = "extraction_validator.py@2026-04-17"
RUNNER_VERSION = "run_wrangler.py@2026-04-17"
# Extraction-report envelope schema (distinct from retrieval.SCHEMA_VERSION
# which pins the RetrievalIntent / AcceptanceCriteria / TexasRow contracts).
# Rename eliminates the cross-module name collision flagged by code-review
# 2026-04-18 (finding M-9). Legacy alias `SCHEMA_VERSION` retained below for
# internal callers — future cleanup can drop it when call-sites migrate.
EXTRACTION_REPORT_SCHEMA_VERSION = "1.0"
SCHEMA_VERSION = EXTRACTION_REPORT_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Exit codes and status mapping
# ---------------------------------------------------------------------------

EXIT_COMPLETE = 0
EXIT_COMPLETE_WITH_WARNINGS = 10
EXIT_BLOCKED = 20
EXIT_DIRECTIVE_OR_IO_ERROR = 30

_STATUS_TO_EXIT = {
    "complete": EXIT_COMPLETE,
    "complete_with_warnings": EXIT_COMPLETE_WITH_WARNINGS,
    "blocked": EXIT_BLOCKED,
}


def _to_dispatch_outcome(overall_status: str) -> DispatchOutcome:
    if overall_status == "complete":
        return DispatchOutcome.COMPLETE
    if overall_status == "complete_with_warnings":
        return DispatchOutcome.PARTIAL
    return DispatchOutcome.FAILED

# extractor_used string per provider, for provenance clarity in the report.
# Used as the fallback when the SourceRecord.kind from _fetch_source does not
# match _EXTRACTOR_LABELS_BY_KIND (below).
_EXTRACTOR_LABELS: dict[str, str] = {
    "local_file": "local_text_read",
    "pdf": "pypdf",
    "md": "markdown_unescape",
    "url": "requests+html_to_text",
    "notion": "notion_client",
    "playwright_html": "playwright_file",
    "image": "sensory_bridges_image",
}

# extractor_used string per SourceRecord.kind — preferred lookup because it
# distinguishes extractors within a single provider (e.g., local_file splits
# into local_text_read / local_pdf / local_docx / local_md based on file suffix).
_EXTRACTOR_LABELS_BY_KIND: dict[str, str] = {
    "local_file": "local_text_read",
    "local_pdf": "pypdf",
    "local_docx": "python-docx",
    "local_md": "markdown_unescape",
    "notion_page": "notion_client",
    "playwright_saved_html": "playwright_file",
    "image_source": "sensory_bridges_image",
}

# Provider -> default source_type passed into the validator's expected-words heuristic.
_PROVIDER_SOURCE_TYPE: dict[str, str] = {
    "local_file": "default",
    "pdf": "pdf",
    "docx": "docx",
    "md": "default",
    "url": "html",
    "notion": "notion",
    "playwright_html": "html",
    "image": "image",
}


# ---------------------------------------------------------------------------
# Internal data classes
# ---------------------------------------------------------------------------


@dataclass
class SourceOutcome:
    """Collected per-source result used to build both extraction-report.yaml
    and the runner's return envelope."""

    ref_id: str
    provider: str
    locator: str
    role: str
    description: str
    extractor_used: str
    fetched_at: str
    content_text: str
    section_title: str
    report: Any  # extraction_validator.ExtractionReport
    error_kind: str | None = None
    error_detail: str | None = None


@dataclass
class RetrievalOutcome:
    """Collected per-source result for Story 27-2 retrieval-shape dispatch.

    One `RetrievalOutcome` per directive source-row, carrying the full dispatcher
    output (rows + acceptance + iteration stats + refinement log) plus the
    retrieval context (intent / provider_hints / cross_validate) needed to
    populate schema v1.1 additive fields in the extraction-report writer.
    """

    ref_id: str
    role: str
    fetched_at: str
    # Retrieval context from the directive row (carried onto every row for v1.1 fields).
    intent: str
    provider_hints: list[dict[str, Any]]
    cross_validate: bool
    source_origin: str  # "operator-named" | "tracy-suggested"
    tracy_row_ref: str | None
    # Dispatcher output.
    rows: list[Any]  # list[retrieval.TexasRow]
    acceptance_met: bool
    iterations_used: int
    refinement_log: list[Any]  # list[retrieval.RefinementLogEntry]
    # Failure path (if dispatcher raised).
    error_kind: str | None = None
    error_detail: str | None = None


# ---------------------------------------------------------------------------
# Directive loading
# ---------------------------------------------------------------------------


class DirectiveError(Exception):
    """Raised when a directive is missing, malformed, or fails shape validation."""


_SUPPORTED_PROVIDERS: frozenset[str] = frozenset(
    {
        "local_file",
        "pdf",
        "docx",
        "md",
        "url",
        "notion",  # legacy direct REST API path (deprecated; prefer notion_mcp)
        "notion_mcp",  # Story 27-5: MCP-mediated fetch, project-scope stdio
        "playwright_html",
        "box",
        "image",  # Story 27-3: image intake via sensory-bridges image_to_agent
    }
)


# Story 27-2 AC-B.6: per-row shape classification for the dispatcher-wiring cascade.
# Retrieval-shape rows (intent + provider_hints) route through retrieval.dispatcher;
# locator-shape rows (provider + locator) keep the existing _fetch_source path.
# Homogeneous directives only (v1 constraint) — mixed shapes exit 30.
def _classify_directive_shape(src: dict[str, Any]) -> str:
    """Return 'retrieval' | 'locator' | 'malformed' for one source row.

    Per Story 27-2 AC-B.6:
      - retrieval: `intent` + `provider_hints` keys, no `provider`+`locator`
      - locator: `provider` + `locator` keys, no `intent`
      - malformed: both or neither of those pairs present
    """
    has_intent = "intent" in src and "provider_hints" in src
    has_locator = "provider" in src and "locator" in src
    if has_intent and not has_locator:
        return "retrieval"
    if has_locator and not has_intent:
        return "locator"
    return "malformed"


def _load_directive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DirectiveError(f"Directive file not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DirectiveError(f"Directive file is not UTF-8: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise DirectiveError(f"Directive YAML failed to parse: {exc}") from exc
    if not isinstance(data, dict):
        raise DirectiveError("Directive root must be a mapping")

    # Minimum-required shape validation — fail loudly at the door.
    for field in ("run_id", "sources"):
        if field not in data:
            raise DirectiveError(f"Directive missing required field: {field}")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise DirectiveError("Directive.sources must be a non-empty list")

    # Per-row shape classification (Story 27-2 AC-B.6).
    per_row_shapes: list[str] = []
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            raise DirectiveError(f"sources[{i}] must be a mapping")
        shape = _classify_directive_shape(src)
        if shape == "malformed":
            raise DirectiveError(
                f"sources[{i}] ambiguous shape: exactly one of "
                f"{{intent+provider_hints}} or {{provider+locator}} must be "
                f"present; got keys: {sorted(src.keys())}"
            )
        per_row_shapes.append(shape)

    # Homogeneous-directive constraint (v1): all sources share one shape.
    # A mixed directive would require the writer to be called twice with
    # different code_path discriminants, violating the one-report-per-run
    # contract. Split into two directives if both shapes are needed.
    shape_set = set(per_row_shapes)
    if len(shape_set) > 1:
        raise DirectiveError(
            f"Directive mixes retrieval-shape and locator-shape sources "
            f"({sorted(shape_set)}). All sources in a directive must share "
            f"one shape (v1 constraint). Split into two directives if both "
            f"shapes are needed. Per-row shapes: {per_row_shapes}"
        )
    directive_shape = per_row_shapes[0]

    # Shape-specific per-row validation.
    seen_ref_ids: set[str] = set()
    for i, src in enumerate(sources):
        # Universal fields (both shapes).
        for required in ("ref_id", "role"):
            if required not in src:
                raise DirectiveError(
                    f"sources[{i}] missing required field: {required}"
                )
        # Story 27-3: visual-primary / visual-supplementary accepted for image
        # sources so operator can flag an image as the source of truth for a
        # learning-objective chain (visual-primary) vs. illustrative
        # (visual-supplementary). Text-source roles unchanged.
        if src["role"] not in (
            "primary",
            "validation",
            "supplementary",
            "visual-primary",
            "visual-supplementary",
        ):
            raise DirectiveError(
                f"sources[{i}].role must be primary|validation|supplementary"
                f"|visual-primary|visual-supplementary, got {src['role']!r}"
            )
        ref_id = src["ref_id"]
        if not isinstance(ref_id, str) or not ref_id.strip():
            raise DirectiveError(
                f"sources[{i}].ref_id must be a non-empty string"
            )
        if ref_id in seen_ref_ids:
            raise DirectiveError(
                f"sources[{i}].ref_id={ref_id!r} is a duplicate; ref_ids must be unique"
            )
        seen_ref_ids.add(ref_id)

        if directive_shape == "locator":
            # Legacy locator-shape validation (unchanged pre-27-2).
            for required in ("provider", "locator"):
                if required not in src:
                    raise DirectiveError(
                        f"sources[{i}] missing required field: {required}"
                    )
            if src["provider"] not in _SUPPORTED_PROVIDERS:
                raise DirectiveError(
                    f"sources[{i}].provider must be one of "
                    f"{sorted(_SUPPORTED_PROVIDERS)}, got {src['provider']!r}"
                )
        else:  # retrieval-shape
            # Intent must be a non-empty string.
            intent = src.get("intent")
            if not isinstance(intent, str) or not intent.strip():
                raise DirectiveError(
                    f"sources[{i}].intent must be a non-empty string for "
                    f"retrieval-shape directive"
                )
            # provider_hints must be a non-empty list of dicts with 'provider' keys.
            hints = src.get("provider_hints")
            if not isinstance(hints, list) or not hints:
                raise DirectiveError(
                    f"sources[{i}].provider_hints must be a non-empty list "
                    f"(retrieval-shape v1 requires explicit provider naming)"
                )
            for j, hint in enumerate(hints):
                if not isinstance(hint, dict) or "provider" not in hint:
                    raise DirectiveError(
                        f"sources[{i}].provider_hints[{j}] must be a mapping "
                        f"with a 'provider' key; got {hint!r}"
                    )

    # Require at least one primary so downstream consumers always receive content.
    # Story 27-3: `visual-primary` also satisfies the primary-presence check —
    # an operator can anchor a learning-objective chain entirely on a visual
    # source (e.g., a roadmap image) without a text-role companion.
    roles = [s["role"] for s in sources]
    if not any(r in ("primary", "visual-primary") for r in roles):
        raise DirectiveError(
            "Directive has no role: primary (or visual-primary) source; "
            "extraction cannot produce extracted.md without at least one "
            "primary-class role"
        )

    # Annotate directive with its shape for the run() dispatch branch.
    data["_directive_shape"] = directive_shape
    return data


# ---------------------------------------------------------------------------
# Retrieval-shape dispatch (Story 27-2 AC-B.6)
# ---------------------------------------------------------------------------


def _wrangle_retrieval_source(
    src: dict[str, Any],
    run_timestamp: str,
) -> RetrievalOutcome:
    """Wrangle one retrieval-shape directive source via `retrieval.dispatcher`.

    Per AC-B.6: construct `RetrievalIntent` from directive row; call
    `dispatcher.dispatch(intent)`; collect the resulting TexasRows.

    Anti-pattern #3 guard: this path is DISJOINT from `_fetch_source` /
    `_wrangle_source`; locator-shape sources are NOT routed through here.
    The directive-load homogeneity check in `_load_directive` ensures the
    entire directive uses one shape.

    Dispatcher exceptions (DispatchError, MCPAuthError, etc.) are captured
    into a FAILED-shape `RetrievalOutcome` with `error_kind` populated so
    the writer still produces a report (same "always produce a report"
    contract as locator-shape path).
    """
    # Lazy import — keeps legacy-directive smoke paths unaffected by retrieval
    # package load cost. Also avoids import-time cycles since retrieval imports
    # are already eager via `skills/bmad-agent-texas/scripts/retrieval/__init__.py`.
    from pydantic import ValidationError  # noqa: PLC0415 — lazy, narrow catch scope
    from retrieval import (  # noqa: PLC0415 — lazy-import intentional per anti-pattern #3 isolation
        AcceptanceCriteria,
        ProviderHint,
        RetrievalIntent,
        dispatch,
    )

    ref_id = src["ref_id"]
    role = src["role"]

    # Construct RetrievalIntent from directive row (v1.1 schema additive fields).
    # PATCH-4 (2026-04-18): narrow the except to ValidationError / ValueError /
    # KeyError / TypeError — the actual shapes we expect from malformed input.
    # Bare `Exception` previously swallowed programmer bugs (AttributeError,
    # NameError) as `retrieval_intent_invalid`, masking real issues.
    try:
        hints = [
            ProviderHint(
                provider=h["provider"],
                params=dict(h.get("params", {})),
            )
            for h in src["provider_hints"]
        ]
        acceptance_raw = src.get("acceptance_criteria", {})
        acceptance = AcceptanceCriteria(
            mechanical=dict(acceptance_raw.get("mechanical", {})),
            provider_scored=dict(acceptance_raw.get("provider_scored", {})),
            semantic_deferred=acceptance_raw.get("semantic_deferred"),
        )
        intent_obj = RetrievalIntent(
            intent=src["intent"],
            provider_hints=hints,
            kind=src.get("kind", "query"),
            acceptance_criteria=acceptance,
            iteration_budget=int(src.get("iteration_budget", 3)),
            convergence_required=bool(src.get("convergence_required", True)),
            cross_validate=bool(src.get("cross_validate", False)),
        )
    except (ValidationError, ValueError, KeyError, TypeError) as exc:
        # PATCH-5 (2026-04-18): sanitize the error-path provider_hints into a
        # writer-safe shape. Downstream writers iterate `h['provider']`; a raw
        # malformed directive dict (e.g., `{"not_provider": "x"}`) without a
        # `provider` key would KeyError in `_write_retrieval_ingestion_evidence`.
        # Coerce to `[{"provider": str(...), "params": dict(...)}]` with safe
        # defaults so the report still renders.
        safe_hints: list[dict[str, Any]] = []
        for h in src.get("provider_hints", []) or []:
            if isinstance(h, dict):
                safe_hints.append({
                    "provider": str(h.get("provider") or "<unknown>"),
                    "params": dict(h.get("params", {}))
                    if isinstance(h.get("params"), dict)
                    else {},
                })
            else:
                safe_hints.append({"provider": "<unknown>", "params": {}})
        return RetrievalOutcome(
            ref_id=ref_id,
            role=role,
            fetched_at=run_timestamp,
            intent=str(src.get("intent", "")),
            provider_hints=safe_hints,
            cross_validate=bool(src.get("cross_validate", False)),
            source_origin=str(src.get("source_origin", "operator-named")),
            tracy_row_ref=src.get("tracy_row_ref"),
            rows=[],
            acceptance_met=False,
            iterations_used=0,
            refinement_log=[],
            error_kind="retrieval_intent_invalid",
            error_detail=f"{type(exc).__name__}: {exc}",
        )

    # Dispatch — dispatcher returns ProviderResult or list[ProviderResult].
    try:
        result = dispatch(intent_obj)
    except Exception as exc:
        return RetrievalOutcome(
            ref_id=ref_id,
            role=role,
            fetched_at=run_timestamp,
            intent=intent_obj.intent,
            provider_hints=[
                {"provider": h.provider, "params": dict(h.params)}
                for h in intent_obj.provider_hints
            ],
            cross_validate=intent_obj.cross_validate,
            source_origin=str(src.get("source_origin", "operator-named")),
            tracy_row_ref=src.get("tracy_row_ref"),
            rows=[],
            acceptance_met=False,
            iterations_used=0,
            refinement_log=[],
            error_kind=_classify_retrieval_error(exc),
            error_detail=f"{type(exc).__name__}: {exc}",
        )

    # Flatten per-provider results (single or cross-validated) into one row list.
    if isinstance(result, list):
        all_rows: list[Any] = []
        all_logs: list[Any] = []
        iterations = 0
        acceptance_met = True
        for pr in result:
            all_rows.extend(pr.rows)
            all_logs.extend(pr.refinement_log)
            iterations = max(iterations, pr.iterations_used)
            acceptance_met = acceptance_met and pr.acceptance_met
    else:
        all_rows = list(result.rows)
        all_logs = list(result.refinement_log)
        iterations = result.iterations_used
        acceptance_met = result.acceptance_met

    return RetrievalOutcome(
        ref_id=ref_id,
        role=role,
        fetched_at=run_timestamp,
        intent=intent_obj.intent,
        provider_hints=[
            {"provider": h.provider, "params": dict(h.params)}
            for h in intent_obj.provider_hints
        ],
        cross_validate=intent_obj.cross_validate,
        source_origin=str(src.get("source_origin", "operator-named")),
        tracy_row_ref=src.get("tracy_row_ref"),
        rows=all_rows,
        acceptance_met=acceptance_met,
        iterations_used=iterations,
        refinement_log=all_logs,
    )


def _classify_retrieval_error(exc: BaseException) -> str:
    """Map retrieval-shape dispatcher / adapter exceptions to error_kind vocab.

    Mirrors `_classify_fetch_error` module-prefix discipline (Winston
    MUST-FIX #2 / AC-T.10): identifies MCPClient errors via
    `type(exc).__module__.startswith("retrieval.")` so they cannot be
    confused with foreign exception classes of the same name.
    """
    cls_name = type(exc).__name__
    module = type(exc).__module__ or ""
    # DispatchError from retrieval.dispatcher — directive-level dispatch failure.
    if module.startswith("retrieval.") and cls_name == "DispatchError":
        return "retrieval_dispatch_error"
    # MCPClient exception family — provider-side HTTP failures.
    if module.startswith("retrieval.") and cls_name == "MCPAuthError":
        return "retrieval_auth_failed"
    if module.startswith("retrieval.") and cls_name == "MCPRateLimitError":
        return "retrieval_rate_limited"
    if module.startswith("retrieval.") and cls_name == "MCPProtocolError":
        return "retrieval_protocol_error"
    if module.startswith("retrieval.") and cls_name == "MCPFetchError":
        return "retrieval_fetch_failed"
    # PATCH-3 (2026-04-18): distinct sentinel for unknown exception classes —
    # prior version collapsed this into `retrieval_fetch_failed`, which lost
    # the diagnostic signal that the classifier had never seen this type before.
    return "retrieval_unknown_error"


# ---------------------------------------------------------------------------
# Fetch dispatch (locator-shape — Story 27-2 anti-pattern #3: UNCHANGED)
# ---------------------------------------------------------------------------


def _fetch_source(src: dict[str, Any]) -> tuple[str, str, Any]:
    """Dispatch to the Texas fetch helper matching the provider.

    Returns (section_title, extracted_text, provenance_record).
    Raises ValueError on unsupported provider or bad input.
    """
    provider = src["provider"]
    locator = src["locator"]

    if provider in ("local_file", "pdf", "docx", "md"):
        path = Path(locator)
        if not path.is_file():
            raise ValueError(f"File not found: {locator}")
        suffix = path.suffix.lower()
        if suffix == ".pdf" or provider == "pdf":
            title, body, rec = _source_ops.wrangle_local_pdf(path)
            return title, body, rec
        # Story 27-1: DOCX wired via python-docx before the text-read fall-through.
        # Branch raises python-docx PackageNotFoundError on malformed DOCX; the
        # adapter (_wrangle_source → _classify_fetch_error) maps that to
        # error_kind="docx_extraction_failed" with known_losses=["docx_open_failed"]
        # so the text-read fall-through below is NOT re-entered after failure
        # (which would re-introduce the binary-garbage defect 27-1 exists to fix).
        if provider == "docx" and suffix != ".docx":
            raise ValueError(
                f"provider 'docx' requires a .docx locator, got: {locator}"
            )
        if suffix == ".docx" or provider == "docx":
            title, body, rec = _source_ops.wrangle_local_docx(path)
            return title, body, rec
        # Markdown (Notion-export-safe): route through wrangle_local_md so
        # Notion's backslash-escaped export format (\#, \*\*, &#x20;, etc.)
        # is normalized before the extractor + validator see it. Handles
        # both the explicit `provider: md` directive and the `local_file`
        # fallback for .md / .markdown files — catches the defect where a
        # Notion export fell through to raw read_text_file and produced
        # garbage-encoded extracted.md (2026-04-19 trial diagnosis).
        if suffix in (".md", ".markdown") or provider == "md":
            title, body, rec = _source_ops.wrangle_local_md(path)
            return title, body, rec
        # Local .txt / other text — read directly.
        body = _source_ops.read_text_file(path)
        rec = _source_ops.SourceRecord(
            kind="local_file",
            ref=str(path.resolve()),
            note=f"local text read ({suffix or 'no-ext'})",
        )
        title = path.stem.replace("_", " ")
        return title, body, rec

    if provider == "url":
        title, body, rec = _source_ops.summarize_url_for_envelope(locator)
        return title, body, rec

    if provider == "notion":
        # wrangle_notion_page returns (title, markdown_body, page_id).
        # LEGACY direct-REST path — kept for backwards compatibility. Prefer
        # provider='notion_mcp' (Story 27-5) for new directives.
        title, body, page_id = _source_ops.wrangle_notion_page(locator)
        rec = _source_ops.SourceRecord(
            kind="notion_page",
            ref=locator,
            note=f"notion page_id={page_id}",
        )
        return title, body, rec

    if provider == "notion_mcp":
        # Story 27-5: MCP-mediated Notion fetch. The harness must supply a
        # NotionMCPFetcher via src['_mcp_fetcher'] (out-of-band injection
        # keyed with a leading underscore so directive schemas don't see it).
        # In live runs, Marcus resolves the page via the project-scope stdio
        # Notion MCP server and passes the pre-fetched result via the
        # fetcher. In tests, a fake fetcher is injected.
        mcp_fetcher = src.get("_mcp_fetcher")
        if mcp_fetcher is None:
            raise ValueError(
                "provider 'notion_mcp' requires a NotionMCPFetcher injected "
                "via src['_mcp_fetcher']. The runtime harness (Marcus) is "
                "responsible for pre-fetching via the project-scope stdio "
                "Notion MCP and providing the fetcher. See Story 27-5."
            )
        expected_scope = src.get("_mcp_expected_scope", "project")
        title, body, rec = _source_ops.wrangle_notion_mcp_page(
            locator, fetcher=mcp_fetcher, expected_scope=expected_scope
        )
        return title, body, rec

    if provider == "playwright_html":
        title, body, rec = _source_ops.wrangle_playwright_saved_html(
            locator,
            source_url=src.get("source_url"),
        )
        return title, body, rec

    # Story 27-6: Box fetch layer. Resolves a Box file ID or shared link to a
    # local file and dispatches to the suffix-appropriate extractor within
    # wrangle_box_file. Box is not itself a format — the local file that comes
    # out still routes through wrangle_local_pdf / wrangle_local_docx /
    # wrangle_local_md / read_text_file. See source_wrangler_operations.py
    # for the provider implementation.
    if provider == "box":
        title, body, rec = _source_ops.wrangle_box_file(locator)
        return title, body, rec

    # Story 27-3: Image intake via sensory-bridges. The wrangle_local_image
    # helper lives in skills/sensory-bridges/scripts/image_to_agent.py (loaded
    # lazily below to keep the runner import graph shallow). An analyzer can
    # be injected via src['_image_analyzer'] for trials / harness scenarios;
    # in production, the v1 VisionLLMAnalyzer stub surfaces remediation
    # pointing at the live-vision follow-on story. The SourceRecord returned
    # here carries kind='image_source' — the SourceRecord type is the
    # source_wrangler_operations.SourceRecord dataclass, adapted below.
    if provider == "image":
        title, body, rec = _wrangle_image_via_bridge(
            locator, analyzer=src.get("_image_analyzer")
        )
        return title, body, rec

    raise ValueError(f"Unsupported provider: {provider!r}")


def _wrangle_image_via_bridge(
    locator: str,
    *,
    analyzer: Any | None = None,
) -> tuple[str, str, Any]:
    """Dispatch image intake to the sensory-bridges helper.

    Isolated in its own function so the import of the hyphenated
    sensory-bridges path happens lazily — consistent with how
    `_fetch_source` keeps other heavy extractors out of the top-level
    import graph. Adapts the helper's local SourceRecord dataclass to the
    canonical `source_wrangler_operations.SourceRecord` the runner carries.
    """
    import importlib.util
    import sys as _sys
    from pathlib import Path as _Path

    # Resolve the image bridge by file path — the sensory-bridges dir is
    # hyphenated so `from skills.sensory_bridges...` is unreliable across
    # execution contexts (script vs. pytest vs. module). This mirrors the
    # load_module_from_path pattern used at the top of this file. Cache the
    # loaded module in sys.modules so dataclass introspection (which walks
    # sys.modules for the defining-class module) resolves correctly on
    # subsequent calls within the same process.
    module_name = "texas_image_bridge"
    cached = _sys.modules.get(module_name)
    if cached is not None:
        bridge = cached
    else:
        here = _Path(__file__).resolve()
        bridge_path = (
            here.parents[2]
            / "sensory-bridges"
            / "scripts"
            / "image_to_agent.py"
        )
        spec = importlib.util.spec_from_file_location(module_name, bridge_path)
        assert spec is not None and spec.loader is not None
        bridge = importlib.util.module_from_spec(spec)
        _sys.modules[module_name] = bridge
        spec.loader.exec_module(bridge)

    title, body, local_rec = bridge.wrangle_local_image(locator, analyzer=analyzer)
    rec = _source_ops.SourceRecord(
        kind=local_rec.kind,
        ref=local_rec.ref,
        note=local_rec.note,
    )
    return title, body, rec


# ---------------------------------------------------------------------------
# Per-source wrangling
# ---------------------------------------------------------------------------


def _expected_pages_for_source(src: dict[str, Any], body: str) -> dict[str, Any]:
    """Build the source_meta dict consumed by extraction_validator."""
    meta: dict[str, Any] = {
        "source_type": _PROVIDER_SOURCE_TYPE.get(src["provider"], "default"),
        "filename": src.get("description") or src["locator"],
    }
    # If the operator declared a page count in the directive, respect it.
    if "pages_total" in src:
        meta["pages_total"] = src["pages_total"]
    if "expected_min_words" in src:
        meta["expected_min_words_override"] = src["expected_min_words"]
    return meta


def _wrangle_source(src: dict[str, Any], now: str) -> SourceOutcome:
    """Fetch + validate a single source.

    Captures runtime errors (network, decode, IO, unsupported-provider fallback)
    into a FAILED outcome rather than letting them propagate — the runner always
    produces a report for real-world fetch or parse failures. Programming errors
    still surface because we don't catch BaseException. `now` is the
    run-scoped timestamp (captured once in run() so all artifacts align).
    """
    ref_id = src["ref_id"]
    provider = src["provider"]
    locator = src["locator"]
    role = src["role"]
    description = src.get("description") or locator
    extractor_label = _EXTRACTOR_LABELS.get(provider, "unknown")

    try:
        title, body, rec = _fetch_source(src)
    except Exception as exc:
        # Fetch-layer failure (network, file not found, PDF parse error,
        # Notion auth, unicode decode, or unsupported-provider fallback).
        # Synthesize a FAILED outcome so the runner's "always produces a
        # report" contract holds end-to-end.
        exc_class = type(exc).__name__
        error_kind = _classify_fetch_error(exc)
        detail = f"{exc_class}: {exc}"
        empty_report = _extraction_validator.ExtractionReport(
            tier=_extraction_validator.QualityTier.FAILED,
            word_count=0,
            line_count=0,
            heading_count=0,
            expected_min_words=0,
            completeness_ratio=0.0,
            structural_fidelity="none",
            evidence=[f"Fetch failed for ref_id={ref_id}: {detail}"],
            known_losses=_fetch_error_known_losses(error_kind, detail),
            recommendations=_fetch_error_recommendations(error_kind, provider),
        )
        return SourceOutcome(
            ref_id=ref_id,
            provider=provider,
            locator=locator,
            role=role,
            description=description,
            extractor_used=extractor_label,
            fetched_at=now,
            content_text="",
            section_title=description,
            report=empty_report,
            error_kind=error_kind,
            error_detail=detail,
        )

    # Prefer per-kind extractor label (distinguishes local_text_read / local_pdf /
    # local_docx inside the shared "local_file" provider).
    kind_label = _EXTRACTOR_LABELS_BY_KIND.get(rec.kind) if rec else None
    if kind_label:
        extractor_label = kind_label

    meta = _expected_pages_for_source(src, body)
    report = _extraction_validator.validate_extraction(body, meta)
    # Override the expected_min_words if directive-supplied. Evidence strings
    # embedded by validate_extraction reflect the validator-estimated floor;
    # when the operator asserts an explicit floor via the directive, rewrite
    # those strings so the evidence trail doesn't lie about what was checked.
    if "expected_min_words_override" in meta:
        override = int(meta["expected_min_words_override"])
        original_min = report.expected_min_words
        report.expected_min_words = override
        report.completeness_ratio = (
            report.word_count / override if override > 0 else 0.0
        )
        # Re-derive the tier from the override-adjusted ratio — otherwise an
        # operator declaring `expected_min_words: 4800` against a 500-word
        # extraction would still show FULL_FIDELITY if the validator's
        # own heuristic estimated a 100-word floor. The tripwire depends
        # on the tier, not on completeness_ratio alone.
        report.tier = _rederive_tier_for_override(
            report.word_count,
            override,
            report.structural_fidelity,
            original_tier=report.tier,
        )
        ratio_pct = f"{report.completeness_ratio:.1%}"
        rewritten_evidence: list[str] = []
        for line in report.evidence:
            if line.startswith("Expected minimum:"):
                rewritten_evidence.append(
                    f"Expected minimum: {override} words "
                    f"(completeness ratio: {ratio_pct}; "
                    f"operator-declared floor overrode validator estimate of {original_min})"
                )
            else:
                rewritten_evidence.append(line)
        rewritten_evidence.append(
            f"Tier re-derived after operator-declared floor: {report.tier.name}"
        )
        report.evidence = rewritten_evidence

    return SourceOutcome(
        ref_id=ref_id,
        provider=provider,
        locator=locator,
        role=role,
        description=description,
        extractor_used=extractor_label,
        fetched_at=now,
        content_text=body,
        section_title=title or description,
        report=report,
    )


def _classify_fetch_error(exc: BaseException) -> str:
    """Map a fetch exception to the canonical error_kind vocabulary."""
    # Unsupported-provider fallback from _fetch_source — message-based because
    # it's the one programmer-authored ValueError with stable phrasing.
    message = str(exc)
    if isinstance(exc, ValueError) and "Unsupported provider" in message:
        return "unsupported_provider"
    # Story 27-1: python-docx PackageNotFoundError surfaces for malformed-ZIP /
    # non-DOCX input. Classify by exception class name + module prefix to avoid
    # a hard import of docx into run_wrangler's module-load path (docx is
    # imported by source_wrangler_operations). Module qualification guards
    # against foreign PackageNotFoundError classes (e.g., importlib.metadata,
    # pkg_resources) that share the name but signal unrelated failures —
    # code-review finding (Blind+Edge Hunter, 2026-04-17).
    if (
        type(exc).__name__ == "PackageNotFoundError"
        and type(exc).__module__.startswith("docx.")
    ):
        return "docx_extraction_failed"
    # Story 27-3: image-intake typed errors. Identified by class-name prefix
    # to avoid importing the image bridge into the runner module-load path
    # (the bridge is loaded lazily in _wrangle_image_via_bridge). The four
    # subclasses each map to a dedicated error_kind so downstream consumers
    # can act on fetch-vs-decode-vs-OCR-vs-vision distinctions.
    class_name = type(exc).__name__
    if class_name == "ImageFetchError":
        return "image_fetch_failed"
    if class_name == "ImageDecodeError":
        return "image_decode_failed"
    if class_name == "ImageOCRFailureError":
        return "image_ocr_failed"
    if class_name == "ImageVisionAPIError":
        return "image_vision_unavailable"
    # Missing file is a common shape — surface cleanly.
    if isinstance(exc, FileNotFoundError):
        return "fetch_failed"
    # Decode failures fall under fetch_failed for operator-action purposes.
    if isinstance(exc, UnicodeDecodeError):
        return "fetch_failed"
    return "fetch_failed"


# Story 27-1 AC-B.3: error-kind → known_losses sentinel mapping for the
# FAILED outcome's ExtractionReport. DOCX gets a distinct "docx_open_failed"
# token so cross-validation and operator routing can tell "the file was
# there but unreadable as DOCX" apart from "generic fetch failed."
_ERROR_KIND_TO_KNOWN_LOSSES: dict[str, list[str]] = {
    "docx_extraction_failed": ["docx_open_failed"],
    # Story 27-3: image-intake failure tokens. Each is distinct so the
    # retrospective / operator triage paths can partition image failures by
    # root cause (bad path vs corrupt header vs blank-image vs no-vision-API)
    # without parsing error messages.
    "image_fetch_failed": ["image_fetch_failed"],
    "image_decode_failed": ["image_decode_failed"],
    "image_ocr_failed": ["image_ocr_failed"],
    "image_vision_unavailable": ["image_vision_unavailable"],
}


def _fetch_error_known_losses(error_kind: str, detail: str) -> list[str]:
    """Return the known_losses list for an error_kind, with per-kind overrides."""
    sentinel = _ERROR_KIND_TO_KNOWN_LOSSES.get(error_kind)
    if sentinel is not None:
        return list(sentinel)
    return [f"Source not fetchable: {detail}"]


def _fetch_error_recommendations(error_kind: str, provider: str) -> list[str]:
    if error_kind == "unsupported_provider":
        return [
            "Check the directive's provider field against the delegation contract",
            "Consult transform-registry.md for supported provider values",
        ]
    return [
        f"Verify the locator for provider={provider!r} is reachable and readable",
        "Check network / auth / file permissions as applicable to the provider",
        "Consult fallback-resolution.md for alternative paths",
    ]


def _rederive_tier_for_override(
    word_count: int,
    expected_min: int,
    structural_fidelity: str,
    original_tier: Any,
) -> Any:
    """Apply the same tier-threshold logic as extraction_validator to the
    override-adjusted ratio. Mirrors the validator's _TIER_THRESHOLDS so
    operator-declared floors drive tier assignment consistently."""
    quality_tier = _extraction_validator.QualityTier
    if expected_min <= 0:
        # Degenerate override: keep the validator's original tier rather than
        # picking a tier based on a meaningless ratio.
        return original_tier
    ratio = word_count / expected_min
    if ratio >= 0.80 and structural_fidelity in ("high", "medium"):
        return quality_tier.FULL_FIDELITY
    if ratio >= 0.50:
        return quality_tier.ADEQUATE_WITH_GAPS
    if ratio >= 0.20:
        return quality_tier.DEGRADED
    return quality_tier.FAILED


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------


def _run_cross_validation(
    primaries: list[SourceOutcome],
    validators: list[SourceOutcome],
    directive_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Run cross_validator for each (primary, validation) pair.

    Returns a list of dicts matching the extraction-report-schema
    cross_validation[] shape. Empty list when no validation assets present.
    """
    if not validators or not primaries:
        return []

    entries: list[dict[str, Any]] = []
    for primary in primaries:
        if not primary.content_text:
            continue
        for validator_src in validators:
            if not validator_src.content_text:
                continue
            directive_entry = next(
                (s for s in directive_sources if s["ref_id"] == validator_src.ref_id),
                {},
            )
            coverage_scope = directive_entry.get("coverage_scope", "unspecified")

            result = _cross_validator.cross_validate(
                extracted_text=primary.content_text,
                reference_text=validator_src.content_text,
                reference_meta={
                    "ref_id": validator_src.ref_id,
                    "description": validator_src.description,
                    "coverage_scope": coverage_scope,
                },
            )
            entry = {
                "primary_ref_id": primary.ref_id,
                "asset_ref_id": result.asset_ref_id,
                "asset_description": result.asset_description,
                "coverage_scope": result.coverage_scope,
                "sections_in_reference": result.sections_in_reference,
                "sections_matched": result.sections_matched,
                "key_terms_total": result.key_terms_total,
                "key_terms_found": result.key_terms_found,
                "key_terms_coverage": round(result.key_terms_coverage, 3),
                "word_count_ratio": round(result.word_count_ratio, 2),
                "verdict": result.verdict,
                "passed": bool(result.passed),
                "missing_sections": list(result.missing_sections[:10]),
                "missing_key_terms": list(result.missing_key_terms[:10]),
            }
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Overall status derivation
# ---------------------------------------------------------------------------


def _derive_overall_status(
    outcomes: list[Any],
    cross_entries: list[dict[str, Any]],
    *,
    code_path: str = "locator",
) -> tuple[str, list[dict[str, Any]]]:
    """Return (overall_status, blocking_issues[]).

    Story 27-2: `code_path` param routes retrieval-shape outcomes through a
    simpler rule-set (no extraction-tier concept — acceptance is binary per
    `acceptance_met` + refinement log depth).
    """
    if code_path == "retrieval":
        return _derive_overall_status_retrieval(outcomes)
    quality_tier = _extraction_validator.QualityTier
    blocking: list[dict[str, Any]] = []

    any_failed = False
    any_degraded = False
    any_warnings = False

    for o in outcomes:
        if o.error_kind:
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": o.error_kind,
                    "detail": o.error_detail or "fetch error",
                    "operator_question": "Provide a working locator or switch providers",
                }
            )
            any_failed = True
            continue
        tier = o.report.tier
        if tier == quality_tier.FAILED:
            any_failed = True
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": "insufficient_content",
                    "detail": (
                        f"Extraction produced only {o.report.word_count} words "
                        f"({o.report.completeness_ratio:.0%} of expected "
                        f"{o.report.expected_min_words})"
                    ),
                    "operator_question": (
                        "Is the source scanned/image-only, or is a different "
                        "provider needed?"
                    ),
                }
            )
        elif tier == quality_tier.DEGRADED:
            any_degraded = True
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": "insufficient_content",
                    "detail": (
                        f"Degraded extraction: {o.report.completeness_ratio:.0%} "
                        f"of expected volume — below the 50% adequacy floor"
                    ),
                    "operator_question": (
                        "Try the documented fallback chain for this provider "
                        "or supply a validation-role asset"
                    ),
                }
            )
        elif tier == quality_tier.ADEQUATE_WITH_GAPS:
            any_warnings = True

    if any_failed or any_degraded:
        return "blocked", blocking

    # Any failed cross-validation on a primary elevates to warnings.
    for entry in cross_entries:
        if not entry["passed"]:
            any_warnings = True
            break

    if any_warnings:
        return "complete_with_warnings", blocking

    return "complete", blocking


def _derive_overall_status_retrieval(
    outcomes: list[RetrievalOutcome],
) -> tuple[str, list[dict[str, Any]]]:
    """Story 27-2: overall status for retrieval-shape runs.

    Rules (applied per-outcome across ALL roles — PATCH-2, 2026-04-18):
      - Primary outcome with `error_kind` → blocked.
      - Primary outcome with `acceptance_met=False` AND no rows → blocked.
      - Primary outcome with `acceptance_met=False` AND rows → warnings.
      - Validation or supplementary outcome with `error_kind` → warnings
        (surfaces operator signal without blocking the run; the primary
        still produced output).
      - Otherwise → complete.

    Rationale: prior version filtered to primaries only, which rendered
    validation-role errors (e.g., `MCPAuthError` on a cross-validation
    partner) completely invisible in the status + blocking_issues surface.
    Mirror the locator-shape `_derive_overall_status` shape (which iterates
    all outcomes) while keeping role-specific severity rules.
    """
    blocking: list[dict[str, Any]] = []
    any_failed = False
    any_warnings = False

    for o in outcomes:
        is_primary = o.role == "primary"
        if o.error_kind is not None:
            blocking.append({
                "ref_id": o.ref_id,
                "reason": o.error_kind,
                "detail": o.error_detail or "retrieval dispatch error",
                "operator_question": (
                    "Verify provider credentials / rate limits / MCP endpoint "
                    "availability for the retrieval-shape directive"
                ),
            })
            if is_primary:
                any_failed = True
            else:
                # Validation/supplementary errors degrade but do not block.
                any_warnings = True
            continue
        if is_primary and not o.acceptance_met and not o.rows:
            blocking.append({
                "ref_id": o.ref_id,
                "reason": "acceptance_criteria_unmet_no_rows",
                "detail": (
                    f"Retrieval dispatch produced 0 rows after "
                    f"{o.iterations_used} iteration(s); acceptance criteria "
                    f"not met"
                ),
                "operator_question": (
                    "Loosen acceptance criteria, widen iteration_budget, or "
                    "switch providers"
                ),
            })
            any_failed = True
        elif not o.acceptance_met:
            any_warnings = True

    if any_failed:
        return "blocked", blocking
    if any_warnings:
        return "complete_with_warnings", blocking
    return "complete", blocking


# ---------------------------------------------------------------------------
# Artifact writers
# ---------------------------------------------------------------------------


def _write_extracted_md(
    bundle_dir: Path,
    run_id: str,
    primaries: list[SourceOutcome],
) -> Path:
    """Build and write extracted.md from primary sources only."""
    sections = [(p.section_title, p.content_text) for p in primaries if p.content_text]
    title = f"Source bundle for {run_id}"
    extracted = _source_ops.build_extracted_markdown(title, sections)
    path = bundle_dir / "extracted.md"
    path.write_text(extracted, encoding="utf-8")
    return path


def _write_metadata_json(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    run_timestamp: str,
) -> Path:
    """Write metadata.json with the provenance chain preserved."""
    provenance = [
        {
            "ref_id": o.ref_id,
            "kind": o.provider,
            "ref": o.locator,
            "role": o.role,
            "description": o.description,
            "extractor_used": o.extractor_used,
            "fetched_at": o.fetched_at,
        }
        for o in outcomes
    ]
    meta = {
        "run_id": run_id,
        "generated_at": run_timestamp,
        "provenance": provenance,
        "primary_consumption_path": "extracted.md",
    }
    path = bundle_dir / "metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path


def _source_outcome_to_report_entry(o: SourceOutcome) -> dict[str, Any]:
    return {
        "ref_id": o.ref_id,
        "provider": o.provider,
        "locator": o.locator,
        "role": o.role,
        "tier": o.report.tier.name,
        "tier_value": o.report.tier.value,
        "passed": bool(o.report.passed),
        "counts": {
            "words": o.report.word_count,
            "lines": o.report.line_count,
            "headings": o.report.heading_count,
            "expected_min_words": o.report.expected_min_words,
        },
        "structural_fidelity": o.report.structural_fidelity,
        "completeness_ratio": round(o.report.completeness_ratio, 3),
        "extractor_used": o.extractor_used,
        "fetched_at": o.fetched_at,
        "content_path": "extracted.md" if o.role == "primary" else None,
        "evidence": list(o.report.evidence),
        "known_losses": list(o.report.known_losses),
        "recommendations": list(o.report.recommendations),
    }


def _write_extraction_report(
    bundle_dir: Path,
    run_id: str,
    overall_status: str,
    outcomes: list[Any],  # list[SourceOutcome] for locator; list[RetrievalOutcome] for retrieval
    cross_entries: list[dict[str, Any]],
    blocking_issues: list[dict[str, Any]],
    run_timestamp: str,
    *,
    code_path: str = "locator",
) -> Path:
    """Write extraction-report.yaml with dual-emit schema_version (AC-C.11).

    Story 27-2 Winston MUST-FIX #1: the `code_path` discriminant is a CONTRACT,
    not a hint. Mismatched outcome types raise `ValueError` rather than silently
    default-filling. Dual-emit prevents dual-drift.

      - `code_path="locator"` → `schema_version: "1.0"`; outcomes must be all
        `SourceOutcome`; any `RetrievalOutcome` in the list raises.
      - `code_path="retrieval"` → `schema_version: "1.1"`; outcomes must be all
        `RetrievalOutcome`; any `SourceOutcome` in the list raises.
    """
    if code_path not in ("locator", "retrieval"):
        raise ValueError(
            f"_write_extraction_report: code_path must be 'locator' or "
            f"'retrieval'; got {code_path!r}"
        )

    # Enforce row / code_path consistency (Winston MUST-FIX #1 teeth).
    if code_path == "locator":
        for o in outcomes:
            if not isinstance(o, SourceOutcome):
                raise ValueError(
                    f"write_extraction_report received non-locator row on "
                    f"locator code path: {type(o).__name__} (expected SourceOutcome)"
                )
        schema_version = "1.0"
        report_sources = [_source_outcome_to_report_entry(o) for o in outcomes]
    else:  # retrieval
        for o in outcomes:
            if not isinstance(o, RetrievalOutcome):
                raise ValueError(
                    f"write_extraction_report received non-retrieval row on "
                    f"retrieval code path: {type(o).__name__} (expected RetrievalOutcome)"
                )
        schema_version = "1.1"
        report_sources = _retrieval_outcomes_to_report_entries(outcomes)

    evidence_summary = _build_evidence_summary(
        overall_status, outcomes, cross_entries, code_path=code_path
    )
    report = {
        "schema_version": schema_version,
        "run_id": run_id,
        "generated_at": run_timestamp,
        "overall_status": overall_status,
        "validator_version": VALIDATOR_VERSION,
        "sources": report_sources,
        "cross_validation": cross_entries,
        "evidence_summary": evidence_summary,
        "recommendations": _collect_recommendations(outcomes, code_path=code_path),
    }
    if overall_status == "blocked" and blocking_issues:
        report["blocking_issues"] = blocking_issues
    path = bundle_dir / "extraction-report.yaml"
    path.write_text(
        yaml.safe_dump(report, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


def _retrieval_outcomes_to_report_entries(
    outcomes: list[RetrievalOutcome],
) -> list[dict[str, Any]]:
    """Flatten retrieval-shape outcomes into v1.1 source entries.

    Each `RetrievalOutcome` contributes:
      - One entry per `TexasRow` in `outcome.rows` (flattened).
      - Retrieval context (intent, provider_hints, cross_validate) carried
        onto every row entry for schema v1.1 additive fields.
      - A synthetic-error entry if the dispatcher raised (no rows produced).
    """
    entries: list[dict[str, Any]] = []
    for outcome in outcomes:
        if outcome.error_kind is not None:
            # Dispatcher / adapter failure — emit one error entry preserving
            # retrieval context so the operator can see what was intended.
            entries.append({
                "ref_id": outcome.ref_id,
                "role": outcome.role,
                "retrieval_intent": outcome.intent,
                "provider_hints": list(outcome.provider_hints),
                "cross_validate": outcome.cross_validate,
                "source_origin": outcome.source_origin,
                "tracy_row_ref": outcome.tracy_row_ref,
                "acceptance_met": False,
                "iterations_used": outcome.iterations_used,
                "fetched_at": outcome.fetched_at,
                "error_kind": outcome.error_kind,
                "error_detail": outcome.error_detail,
            })
            continue
        if not outcome.rows:
            # Empty-result (no adapter error, but no rows meeting criteria).
            entries.append({
                "ref_id": outcome.ref_id,
                "role": outcome.role,
                "retrieval_intent": outcome.intent,
                "provider_hints": list(outcome.provider_hints),
                "cross_validate": outcome.cross_validate,
                "source_origin": outcome.source_origin,
                "tracy_row_ref": outcome.tracy_row_ref,
                "acceptance_met": outcome.acceptance_met,
                "iterations_used": outcome.iterations_used,
                "fetched_at": outcome.fetched_at,
                "rows": [],
            })
            continue
        # Happy path: one entry per TexasRow, retrieval context attached.
        for idx, row in enumerate(outcome.rows):
            convergence = None
            if row.convergence_signal is not None:
                convergence = row.convergence_signal.model_dump()
            entries.append({
                "ref_id": f"{outcome.ref_id}-row-{idx + 1}",
                "role": outcome.role,
                "retrieval_intent": outcome.intent,
                "provider_hints": list(outcome.provider_hints),
                "cross_validate": outcome.cross_validate,
                "convergence_signal": convergence,
                "source_origin": row.source_origin or outcome.source_origin,
                "tracy_row_ref": row.tracy_row_ref or outcome.tracy_row_ref,
                "acceptance_met": outcome.acceptance_met,
                "iterations_used": outcome.iterations_used,
                "fetched_at": outcome.fetched_at,
                "source_id": row.source_id,
                "provider": row.provider,
                "title": row.title,
                "body": row.body,
                "authors": list(row.authors),
                "date": row.date,
                "authority_tier": row.authority_tier,
                "provider_metadata": dict(row.provider_metadata or {}),
                "completeness_ratio": row.completeness_ratio,
                "structural_fidelity": row.structural_fidelity,
            })
    return entries


def _build_evidence_summary(
    overall_status: str,
    outcomes: list[Any],
    cross_entries: list[dict[str, Any]],
    *,
    code_path: str = "locator",
) -> list[str]:
    # Schema contract: always produce 2-5 sentences.
    if code_path == "retrieval":
        return _build_evidence_summary_retrieval(overall_status, outcomes)
    primaries = [o for o in outcomes if o.role == "primary"]
    validators = [o for o in outcomes if o.role == "validation"]
    supplementaries = [o for o in outcomes if o.role == "supplementary"]
    lines: list[str] = []
    if primaries:
        tier_names = [o.report.tier.name for o in primaries]
        lines.append(
            f"{len(primaries)} primary source(s) processed; tiers: {', '.join(tier_names)}."
        )
    else:
        # Should be unreachable — directive validation rejects zero-primary
        # directives at load time — but we keep a defensive branch so the
        # evidence summary always explains why a report exists.
        lines.append(
            "No primary sources were processed (directive validation should "
            "have prevented this state)."
        )
    if cross_entries:
        passed = sum(1 for e in cross_entries if e["passed"])
        lines.append(
            f"Cross-validation: {passed}/{len(cross_entries)} validation pairs passed "
            f"across {len(validators)} validation-role asset(s)."
        )
    else:
        lines.append("No validation-role assets supplied; cross-validation skipped.")
    if supplementaries:
        lines.append(
            f"{len(supplementaries)} supplementary source(s) recorded in metadata "
            "provenance but not extracted into extracted.md."
        )
    lines.append(f"Overall status: {overall_status}.")
    return lines


def _build_evidence_summary_retrieval(
    overall_status: str,
    outcomes: list[RetrievalOutcome],
) -> list[str]:
    """Evidence summary for retrieval-shape runs (Story 27-2)."""
    primaries = [o for o in outcomes if o.role == "primary"]
    total_rows = sum(len(o.rows) for o in outcomes if o.error_kind is None)
    errors = [o for o in outcomes if o.error_kind is not None]
    lines: list[str] = []
    lines.append(
        f"{len(primaries)} primary retrieval-shape source(s) dispatched; "
        f"{total_rows} row(s) returned across {len(outcomes)} dispatch(es)."
    )
    met = sum(1 for o in outcomes if o.error_kind is None and o.acceptance_met)
    lines.append(
        f"Acceptance criteria met on {met}/{len(outcomes)} dispatches "
        f"(iteration budgets used: {[o.iterations_used for o in outcomes]})."
    )
    if errors:
        kinds = sorted({o.error_kind for o in errors if o.error_kind})
        lines.append(
            f"{len(errors)} dispatch(es) failed; error kinds: {', '.join(kinds)}."
        )
    lines.append(f"Overall status: {overall_status}.")
    return lines


def _collect_recommendations(
    outcomes: list[Any],
    *,
    code_path: str = "locator",
) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    if code_path == "retrieval":
        # Retrieval-shape: surface refinement-log "reason" values + any error detail.
        for o in outcomes:
            if o.error_kind:
                rec = (
                    f"Retrieval dispatch failed ({o.error_kind}): verify "
                    f"provider auth / rate limits / MCP catalog shape. See "
                    f"provider-specific spec for troubleshooting."
                )
                if rec not in seen:
                    seen.add(rec)
                    out.append(rec)
            for entry in o.refinement_log:
                reason = getattr(entry, "reason", None)
                if reason and reason not in seen:
                    seen.add(reason)
                    out.append(f"Refinement log: {reason}")
        return out
    for o in outcomes:
        for r in o.report.recommendations:
            if r not in seen:
                seen.add(r)
                out.append(r)
    return out


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_manifest_json(
    bundle_dir: Path,
    run_id: str,
    artifact_paths: list[Path],
    run_timestamp: str,
) -> Path:
    """Write manifest.json listing every artifact with sha256 + size.

    Intentionally includes itself-by-omission: manifest.json isn't listed
    because it's written after the content files. Its sha256 would change
    every run anyway. result.yaml is also written after manifest.json so
    it cannot self-hash either; that omission is documented in the delegation
    contract.
    """
    artifacts = []
    for p in artifact_paths:
        if p.is_file():
            artifacts.append(
                {
                    "path": p.relative_to(bundle_dir).as_posix(),
                    "sha256": _sha256_of_file(p),
                    "size_bytes": p.stat().st_size,
                }
            )
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "bundle_dir": Path(bundle_dir).resolve().as_posix(),
        "generated_at": run_timestamp,
        "artifacts": artifacts,
    }
    path = bundle_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def _write_ingestion_evidence(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
    overall_status: str,
    run_timestamp: str,
) -> Path:
    """Human-readable markdown log of the session."""
    lines: list[str] = [
        "# Ingestion Evidence Log",
        "",
        f"**Run ID:** {run_id}",
        f"**Generated at:** {run_timestamp}",
        f"**Overall status:** {overall_status}",
        f"**Runner:** {RUNNER_VERSION}",
        "",
        "## Sources Processed",
        "",
    ]
    for o in outcomes:
        lines.append(f"### {o.ref_id} — {o.description}")
        lines.append("")
        lines.append(f"- Provider: `{o.provider}`")
        lines.append(f"- Role: `{o.role}`")
        lines.append(f"- Extractor: `{o.extractor_used}`")
        lines.append(f"- Fetched at: {o.fetched_at}")
        lines.append(f"- Tier: **{o.report.tier.name}** (tier_value {o.report.tier.value})")
        lines.append(
            f"- Counts: {o.report.word_count} words / "
            f"{o.report.line_count} lines / {o.report.heading_count} headings "
            f"(expected min {o.report.expected_min_words})"
        )
        lines.append(f"- Completeness ratio: {o.report.completeness_ratio:.1%}")
        lines.append(f"- Structural fidelity: {o.report.structural_fidelity}")
        if o.report.evidence:
            lines.append("- Evidence:")
            for e in o.report.evidence:
                lines.append(f"  - {e}")
        if o.report.known_losses:
            lines.append("- Known losses:")
            for loss in o.report.known_losses:
                lines.append(f"  - {loss}")
        if o.error_kind:
            lines.append(f"- **Error:** {o.error_kind} — {o.error_detail}")
        lines.append("")

    if cross_entries:
        lines.append("## Cross-Validation")
        lines.append("")
        for entry in cross_entries:
            verdict_word = "PASS" if entry["passed"] else "FAIL"
            lines.append(
                f"- **{verdict_word}** {entry['primary_ref_id']} ↔ "
                f"{entry['asset_ref_id']}: "
                f"sections {entry['sections_matched']}/{entry['sections_in_reference']}, "
                f"key-term coverage {entry['key_terms_coverage']:.1%}. "
                f"Verdict: {entry['verdict']}"
            )
        lines.append("")

    path = bundle_dir / "ingestion-evidence.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_result_envelope(
    bundle_dir: Path,
    run_id: str,
    overall_status: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
    blocking_issues: list[dict[str, Any]],
    artifact_paths: list[Path],
) -> Path:
    """Write result.yaml matching the delegation-contract Texas -> Marcus return.

    This is the *envelope* Marcus consumes — it mirrors extraction-report.yaml
    but with additional pointers to artifacts and Marcus-facing status.
    """
    materials = []
    for o in outcomes:
        materials.append(
            {
                "ref_id": o.ref_id,
                "role": o.role,
                "quality_tier": o.report.tier.value,
                "extractor_used": o.extractor_used,
                "content_path": "extracted.md" if o.role == "primary" else None,
                "word_count": o.report.word_count,
                "line_count": o.report.line_count,
                "heading_count": o.report.heading_count,
                "quality_report": {
                    "completeness_ratio": round(o.report.completeness_ratio, 3),
                    "structural_fidelity": o.report.structural_fidelity,
                    "known_losses": list(o.report.known_losses),
                    "evidence": list(o.report.evidence),
                },
            }
        )

    envelope = {
        "status": overall_status,
        "run_id": run_id,
        "bundle_dir": Path(bundle_dir).resolve().as_posix(),
        "runner_version": RUNNER_VERSION,
        "materials": materials,
        "cross_validation": cross_entries,
        "blocking_issues": blocking_issues,
        "recommendations": _collect_recommendations(outcomes),
        "artifacts": [p.relative_to(bundle_dir).as_posix() for p in artifact_paths],
        "bundle_manifest_path": "manifest.json",
    }
    dispatch_artifacts = [p.relative_to(bundle_dir).as_posix() for p in artifact_paths]
    dispatch_envelope = build_dispatch_envelope(
        run_id=run_id,
        dispatch_kind=DispatchKind.TEXAS_RETRIEVAL,
        input_packet={
            "directive_shape": "locator",
            "materials_count": len(materials),
        },
        context_refs=dispatch_artifacts,
        correlation_id=f"{run_id}-texas-retrieval",
    )
    dispatch_receipt = build_dispatch_receipt(
        correlation_id=dispatch_envelope.correlation_id,
        specialist_id=dispatch_envelope.specialist_id,
        outcome=_to_dispatch_outcome(overall_status),
        output_artifacts=dispatch_artifacts,
        diagnostics={
            "status": overall_status,
            "materials_count": len(materials),
            "blocking_issues_count": len(blocking_issues),
        },
        duration_ms=0,
    )
    envelope["dispatch_contract"] = {
        "envelope": dispatch_envelope.model_dump(mode="json"),
        "receipt": dispatch_receipt.model_dump(mode="json"),
    }
    path = bundle_dir / "result.yaml"
    path.write_text(
        yaml.safe_dump(envelope, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def _utc_timestamp_z() -> str:
    """ISO-8601 UTC timestamp with trailing Z suffix (matches schema example)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(directive_path: Path, bundle_dir: Path) -> dict[str, Any]:
    """Run the wrangler end-to-end; return the result envelope as a dict.

    Raises DirectiveError on malformed directive (caller maps to exit 30).
    Runtime errors inside source fetching are captured into FAILED outcomes
    per the "always produce a report" contract. Unexpected programming
    errors (TypeError, AttributeError, etc.) still propagate so bugs surface
    rather than being silently swallowed.
    """
    directive = _load_directive(directive_path)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    run_id = str(directive["run_id"])
    # Capture one run-scoped timestamp so every artifact agrees on "when".
    run_timestamp = _utc_timestamp_z()

    # Story 27-2 AC-B.6: branch on directive shape. `_load_directive`
    # already validated homogeneity and annotated the directive with its shape.
    directive_shape = directive["_directive_shape"]

    if directive_shape == "retrieval":
        return _run_retrieval_shape(directive, bundle_dir, run_id, run_timestamp)

    # Legacy locator-shape path (anti-pattern #3: UNCHANGED).
    outcomes: list[SourceOutcome] = []
    for src in directive["sources"]:
        outcomes.append(_wrangle_source(src, run_timestamp))

    primaries = [o for o in outcomes if o.role == "primary"]
    validators = [o for o in outcomes if o.role == "validation"]

    cross_entries = _run_cross_validation(primaries, validators, directive["sources"])
    overall_status, blocking_issues = _derive_overall_status(outcomes, cross_entries)

    # Write artifacts in a specific order so manifest.json indexes all the
    # content-bearing files.
    extracted_path = _write_extracted_md(bundle_dir, run_id, primaries)
    metadata_path = _write_metadata_json(bundle_dir, run_id, outcomes, run_timestamp)
    extraction_report_path = _write_extraction_report(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        cross_entries,
        blocking_issues,
        run_timestamp,
        code_path="locator",
    )
    ingestion_evidence_path = _write_ingestion_evidence(
        bundle_dir, run_id, outcomes, cross_entries, overall_status, run_timestamp
    )

    content_artifacts = [
        extracted_path,
        metadata_path,
        extraction_report_path,
        ingestion_evidence_path,
    ]
    manifest_path = _write_manifest_json(
        bundle_dir, run_id, content_artifacts, run_timestamp
    )

    all_artifacts = content_artifacts + [manifest_path]
    result_path = _write_result_envelope(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        cross_entries,
        blocking_issues,
        all_artifacts,
    )

    # Re-read the written envelope so the in-memory return matches disk exactly.
    return yaml.safe_load(result_path.read_text(encoding="utf-8"))


def _run_retrieval_shape(
    directive: dict[str, Any],
    bundle_dir: Path,
    run_id: str,
    run_timestamp: str,
) -> dict[str, Any]:
    """Story 27-2 AC-B.6: retrieval-shape directive execution path.

    Disjoint from the locator-shape path per anti-pattern #3 (no retrofit of
    locator-shape providers). Writes `schema_version: "1.1"` via the writer's
    `code_path="retrieval"` discriminant.
    """
    outcomes: list[RetrievalOutcome] = [
        _wrangle_retrieval_source(src, run_timestamp)
        for src in directive["sources"]
    ]

    # Retrieval-shape runs do NOT invoke extraction_validator or cross_validator.
    # Those are locator-shape concepts (word counts, page ratios, key-term
    # coverage). Retrieval-shape quality is already reflected in acceptance_met
    # + iterations_used + refinement_log per ProviderResult.
    cross_entries: list[dict[str, Any]] = []
    overall_status, blocking_issues = _derive_overall_status(
        outcomes, cross_entries, code_path="retrieval"
    )

    # Retrieval-shape extracted.md: flat concatenation of row bodies for
    # downstream consumption parity with locator-shape.
    primaries = [o for o in outcomes if o.role == "primary"]
    extracted_path = _write_retrieval_extracted_md(bundle_dir, run_id, primaries)
    metadata_path = _write_retrieval_metadata_json(
        bundle_dir, run_id, outcomes, run_timestamp
    )
    extraction_report_path = _write_extraction_report(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        cross_entries,
        blocking_issues,
        run_timestamp,
        code_path="retrieval",
    )
    ingestion_evidence_path = _write_retrieval_ingestion_evidence(
        bundle_dir, run_id, outcomes, overall_status, run_timestamp
    )

    content_artifacts = [
        extracted_path,
        metadata_path,
        extraction_report_path,
        ingestion_evidence_path,
    ]
    manifest_path = _write_manifest_json(
        bundle_dir, run_id, content_artifacts, run_timestamp
    )

    all_artifacts = content_artifacts + [manifest_path]
    result_path = _write_retrieval_result_envelope(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        blocking_issues,
        all_artifacts,
    )

    return yaml.safe_load(result_path.read_text(encoding="utf-8"))


def _write_retrieval_extracted_md(
    bundle_dir: Path,
    run_id: str,
    primaries: list[RetrievalOutcome],
) -> Path:
    """Retrieval-shape extracted.md — flat concatenation of row bodies."""
    lines = ["# Texas Extracted Bundle (retrieval-shape)\n", f"Run ID: {run_id}\n\n"]
    for outcome in primaries:
        lines.append(f"## Retrieval: {outcome.ref_id}\n")
        lines.append(f"Intent: {outcome.intent}\n\n")
        for row in outcome.rows:
            lines.append(f"### {row.title or row.source_id}\n")
            if row.authors:
                lines.append(f"Authors: {', '.join(row.authors)}\n")
            if row.date:
                lines.append(f"Date: {row.date}\n")
            lines.append(f"\n{row.body}\n\n")
    path = bundle_dir / "extracted.md"
    path.write_text("".join(lines), encoding="utf-8")
    return path


def _write_retrieval_metadata_json(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[RetrievalOutcome],
    run_timestamp: str,
) -> Path:
    """Retrieval-shape metadata.json — per-dispatch provenance."""
    metadata: dict[str, Any] = {
        "schema_version": "1.1",
        "run_id": run_id,
        "generated_at": run_timestamp,
        "directive_shape": "retrieval",
        "dispatches": [
            {
                "ref_id": o.ref_id,
                "role": o.role,
                "intent": o.intent,
                "provider_hints": list(o.provider_hints),
                "cross_validate": o.cross_validate,
                "source_origin": o.source_origin,
                "tracy_row_ref": o.tracy_row_ref,
                "acceptance_met": o.acceptance_met,
                "iterations_used": o.iterations_used,
                "rows_returned": len(o.rows),
                "error_kind": o.error_kind,
                "error_detail": o.error_detail,
            }
            for o in outcomes
        ],
    }
    path = bundle_dir / "metadata.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path


def _write_retrieval_ingestion_evidence(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[RetrievalOutcome],
    overall_status: str,
    run_timestamp: str,
) -> Path:
    """Retrieval-shape ingestion-evidence.md — dispatch summary."""
    lines = [
        "# Ingestion Evidence (retrieval-shape)\n\n",
        f"Run ID: {run_id}\n",
        f"Generated: {run_timestamp}\n",
        f"Overall status: {overall_status}\n\n",
    ]
    for outcome in outcomes:
        lines.append(f"## {outcome.ref_id} ({outcome.role})\n\n")
        lines.append(f"- Intent: `{outcome.intent}`\n")
        lines.append(
            f"- Providers: "
            f"{', '.join(h['provider'] for h in outcome.provider_hints)}\n"
        )
        lines.append(f"- Cross-validate: {outcome.cross_validate}\n")
        lines.append(f"- Acceptance met: {outcome.acceptance_met}\n")
        lines.append(f"- Iterations: {outcome.iterations_used}\n")
        lines.append(f"- Rows returned: {len(outcome.rows)}\n")
        if outcome.error_kind:
            lines.append(f"- **Error:** `{outcome.error_kind}` — {outcome.error_detail}\n")
        if outcome.refinement_log:
            lines.append("\n### Refinement log\n\n")
            for entry in outcome.refinement_log:
                lines.append(
                    f"  - iter={entry.iteration} provider={entry.provider} "
                    f"reason={entry.reason}"
                )
                if entry.criterion_key:
                    lines.append(f" key={entry.criterion_key}")
                lines.append("\n")
        lines.append("\n")
    path = bundle_dir / "ingestion-evidence.md"
    path.write_text("".join(lines), encoding="utf-8")
    return path


def _write_retrieval_result_envelope(
    bundle_dir: Path,
    run_id: str,
    overall_status: str,
    outcomes: list[RetrievalOutcome],
    blocking_issues: list[dict[str, Any]],
    artifact_paths: list[Path],
) -> Path:
    """Retrieval-shape result.yaml — parity with locator-shape envelope."""
    envelope: dict[str, Any] = {
        "schema_version": "1.1",
        "run_id": run_id,
        "directive_shape": "retrieval",
        "status": overall_status,
        "dispatches_count": len(outcomes),
        "rows_total": sum(len(o.rows) for o in outcomes if o.error_kind is None),
        "acceptance_met_count": sum(
            1 for o in outcomes if o.error_kind is None and o.acceptance_met
        ),
        "errors_count": sum(1 for o in outcomes if o.error_kind is not None),
        "artifacts": [p.relative_to(bundle_dir).as_posix() for p in artifact_paths],
    }
    dispatch_artifacts = [p.relative_to(bundle_dir).as_posix() for p in artifact_paths]
    dispatch_envelope = build_dispatch_envelope(
        run_id=run_id,
        dispatch_kind=DispatchKind.TEXAS_RETRIEVAL,
        input_packet={
            "directive_shape": "retrieval",
            "dispatches_count": len(outcomes),
        },
        context_refs=dispatch_artifacts,
        correlation_id=f"{run_id}-texas-retrieval",
    )
    dispatch_receipt = build_dispatch_receipt(
        correlation_id=dispatch_envelope.correlation_id,
        specialist_id=dispatch_envelope.specialist_id,
        outcome=_to_dispatch_outcome(overall_status),
        output_artifacts=dispatch_artifacts,
        diagnostics={
            "status": overall_status,
            "dispatches_count": len(outcomes),
            "rows_total": envelope["rows_total"],
            "errors_count": envelope["errors_count"],
        },
        duration_ms=0,
    )
    envelope["dispatch_contract"] = {
        "envelope": dispatch_envelope.model_dump(mode="json"),
        "receipt": dispatch_receipt.model_dump(mode="json"),
    }
    if blocking_issues:
        envelope["blocking_issues"] = blocking_issues
    path = bundle_dir / "result.yaml"
    path.write_text(
        yaml.safe_dump(envelope, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


def _list_providers_cli(
    *,
    shape: str | None,
    status: str | None,
    as_json: bool,
) -> int:
    """CLI handler for ``--list-providers`` (Story 27-0 AC-B.9).

    Imports the retrieval directory lazily so the rest of run_wrangler's
    boot path is unaffected on installations that haven't built the
    package yet (future rollback safety).
    """
    try:
        from retrieval.provider_directory import list_providers
    except ImportError as exc:
        sys.stderr.write(
            f"[run_wrangler] retrieval package unavailable: {exc}\n"
            "[run_wrangler] --list-providers requires the Story 27-0 "
            "retrieval foundation\n"
        )
        return EXIT_DIRECTIVE_OR_IO_ERROR

    providers = list_providers(shape=shape, status=status)

    if as_json:
        sys.stdout.write(
            json.dumps(
                [p.model_dump() for p in providers],
                indent=2,
            )
            + "\n"
        )
        return EXIT_COMPLETE

    # Human-readable table.
    sys.stdout.write(
        f"\nTexas provider directory ({len(providers)} entries)\n"
    )
    if shape or status:
        filters = []
        if shape:
            filters.append(f"shape={shape}")
        if status:
            filters.append(f"status={status}")
        sys.stdout.write(f"Filters: {', '.join(filters)}\n")
    sys.stdout.write(
        f"  {'ID':22} {'SHAPE':10} {'STATUS':10} {'CAPABILITIES':40} AUTH\n"
    )
    sys.stdout.write(f"  {'-' * 22} {'-' * 10} {'-' * 10} {'-' * 40} {'-' * 20}\n")
    for p in providers:
        caps = ", ".join(p.capabilities[:3])
        if len(p.capabilities) > 3:
            caps += f", +{len(p.capabilities) - 3}"
        auth = ", ".join(p.auth_env_vars) or "-"
        sys.stdout.write(
            f"  {p.id:22} {p.shape:10} {p.status:10} {caps[:40]:40} {auth}\n"
        )
    sys.stdout.write("\n")
    return EXIT_COMPLETE


def main(argv: list[str] | None = None) -> int:
    # Story 26-7 AC-C.2: force UTF-8 stdout/stderr before any print so a
    # Windows cp1252 terminal does not crash on non-ASCII source titles.
    _cli_encoding.ensure_utf8_stdout()

    parser = argparse.ArgumentParser(
        description=(
            "Texas runtime wrangling runner — executes the Marcus ↔ Texas "
            "delegation contract end-to-end."
        )
    )
    parser.add_argument(
        "--directive",
        type=Path,
        required=False,
        help="Path to the wrangling directive YAML.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=False,
        help="Bundle directory where artifacts are written.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the result envelope as JSON to stdout (default: YAML).",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help=(
            "Print the Texas provider directory (what sources Texas can "
            "fetch from) and exit. Skips dispatch entirely; --directive / "
            "--bundle-dir not required."
        ),
    )
    parser.add_argument(
        "--shape",
        choices=["retrieval", "locator"],
        default=None,
        help="Filter --list-providers output by provider shape.",
    )
    parser.add_argument(
        "--status",
        choices=["ready", "stub", "ratified", "backlog"],
        default=None,
        help="Filter --list-providers output by status.",
    )

    args = parser.parse_args(argv)

    # Story 27-0 AC-B.9: --list-providers short-circuits dispatch.
    if args.list_providers:
        # SHOULD-FIX H-6 (code-review 2026-04-18): warn if --directive /
        # --bundle-dir were ALSO supplied — they'll be silently ignored.
        if args.directive is not None or args.bundle_dir is not None:
            sys.stderr.write(
                "[run_wrangler] --list-providers short-circuits dispatch; "
                "--directive / --bundle-dir were supplied but will be ignored\n"
            )
        return _list_providers_cli(
            shape=args.shape, status=args.status, as_json=args.json
        )

    if args.directive is None or args.bundle_dir is None:
        sys.stderr.write(
            "[run_wrangler] --directive and --bundle-dir are required unless "
            "--list-providers is passed\n"
        )
        return EXIT_DIRECTIVE_OR_IO_ERROR

    try:
        envelope = run(args.directive, args.bundle_dir)
    except DirectiveError as exc:
        sys.stderr.write(f"[run_wrangler] directive error: {exc}\n")
        return EXIT_DIRECTIVE_OR_IO_ERROR
    except OSError as exc:
        sys.stderr.write(f"[run_wrangler] IO error: {exc}\n")
        return EXIT_DIRECTIVE_OR_IO_ERROR
    except Exception as exc:  # noqa: BLE001 — deliberate runner-boundary catch
        # Any other exception (programming error, unexpected library fault)
        # is still a runner failure from Marcus's perspective. Report it
        # cleanly rather than letting Python print a traceback and return 1.
        sys.stderr.write(
            f"[run_wrangler] unexpected error ({type(exc).__name__}): {exc}\n"
            "[run_wrangler] this indicates a runner bug or unhandled fetch "
            "exception class — report to the maintainer\n"
        )
        return EXIT_DIRECTIVE_OR_IO_ERROR

    if args.json:
        sys.stdout.write(json.dumps(envelope, indent=2) + "\n")
    else:
        sys.stdout.write(yaml.safe_dump(envelope, sort_keys=False) + "\n")

    status = envelope.get("status", "blocked")
    return _STATUS_TO_EXIT.get(status, EXIT_BLOCKED)


if __name__ == "__main__":
    raise SystemExit(main())
