"""`ConsensusProvider` implementation for Story 27-2.5.

Implements Consensus retrieval integration as a `RetrievalAdapter` subclass,
including deterministic query building, filtering, normalization, refinement,
and identity-key semantics for cross-validation with scite.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)
from .mcp_client import MCPClient, MCPServerConfig
from .normalize import build_texas_row, coerce_authors
from .refinement_registry import drop_filters_in_order, get_strategy

CONSENSUS_MCP_URL = os.environ.get("CONSENSUS_MCP_URL", "https://mcp.consensus.app/mcp")
"""Consensus MCP endpoint. Override via `CONSENSUS_MCP_URL` for local testing.

Default matches Consensus docs + Cursor ``mcp-remote`` config (``mcp.consensus.app``).
The legacy ``api.consensus.app/mcp`` host returns HTTP 404 for tools/call and is
rewritten to the official endpoint when detected.
"""
if CONSENSUS_MCP_URL.rstrip("/").endswith("api.consensus.app/mcp"):
    CONSENSUS_MCP_URL = "https://mcp.consensus.app/mcp"

CONSENSUS_API_KEY_ENV_VAR = "CONSENSUS_API_KEY"
CONSENSUS_BASIC_AUTH_ENV_VARS: tuple[str, str] = (
    "CONSENSUS_USER_NAME",
    "CONSENSUS_PASSWORD",
)
CONSENSUS_AUTH_ENV_VARS: tuple[str, ...] = (
    CONSENSUS_API_KEY_ENV_VAR,
    *CONSENSUS_BASIC_AUTH_ENV_VARS,
)
"""Accepted Consensus auth env vars. Runtime prefers bearer, then basic."""

# Live Consensus MCP (2026-07) returns markdown in MCP content blocks, e.g.:
# [1] [Title](https://consensus.app/papers/details/<id>/...) (Authors, 2023, 29 citations, Journal)
_MARKDOWN_PAPER_RE = re.compile(
    r"\[(?P<n>\d+)\]\s+"
    r"\[(?P<title>[^\]]+)\]\((?P<url>https://consensus\.app/papers/details/"
    r"(?P<paper_id>[a-f0-9]+)[^)]*)\)\s+"
    r"\((?P<meta>.+?)\)\n"
    r"(?P<body>.*?)(?=\n\n\[\d+\]|\n\nIMPORTANT|\Z)",
    re.DOTALL,
)

_HONORED_CRITERIA: frozenset[str] = frozenset(
    {
        "date_range",
        "min_results",
        "exclude_ids",
        "consensus_score_min",
        "study_design_allow",
        "sample_size_min",
        "license_allow",
    }
)

CONSENSUS_REFINEMENT_KEY_ORDER: tuple[str, ...] = (
    "sample_size_min",
    "consensus_score_min",
    "study_design_allow",
    "date_range",
)

_CONSENSUS_TOOL_SEARCH = "search"
_CONSENSUS_TOOL_PAPER = "paper_metadata"


def load_consensus_oauth_token_from_mcp_auth(
    *,
    mcp_auth_root: Path | None = None,
) -> str | None:
    """Load the newest mcp-remote OAuth access_token from ``~/.mcp-auth``.

    Cursor ``mcp-remote`` stores tokens after interactive OAuth. Texas can reuse
    that Bearer token as ``CONSENSUS_API_KEY`` for live dispatch without a
    separate enterprise API key. Returns ``None`` when no token file exists.
    Does not print or log the token value.
    """
    root = mcp_auth_root or (Path.home() / ".mcp-auth")
    if not root.is_dir():
        return None
    candidates = sorted(
        root.rglob("*_tokens.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        token = str(payload.get("access_token") or "").strip()
        if token:
            return token
    return None


def ensure_consensus_bearer_from_mcp_auth() -> bool:
    """If ``CONSENSUS_API_KEY`` is unset, populate it from mcp-remote OAuth cache.

    Returns True when a bearer token is available after this call.
    """
    existing = os.environ.get(CONSENSUS_API_KEY_ENV_VAR, "").strip()
    if existing:
        return True
    token = load_consensus_oauth_token_from_mcp_auth()
    if not token:
        return False
    os.environ[CONSENSUS_API_KEY_ENV_VAR] = token
    return True


def _parse_markdown_papers(text: str) -> list[dict[str, Any]]:
    """Parse Consensus MCP markdown search text into paper dicts."""
    papers: list[dict[str, Any]] = []
    for match in _MARKDOWN_PAPER_RE.finditer(text):
        meta = match.group("meta")
        # Authors, Year, N citations, Journal — authors may contain commas.
        meta_match = re.match(
            r"^(?P<authors>.+),\s+(?P<year>\d{4}),\s+"
            r"(?P<citations>\d+)\s+citations?,\s+(?P<venue>.+)$",
            meta,
        )
        authors_raw = meta_match.group("authors") if meta_match else meta
        year = int(meta_match.group("year")) if meta_match else None
        citations = (
            int(meta_match.group("citations")) if meta_match else None
        )
        venue = meta_match.group("venue") if meta_match else None
        body = (match.group("body") or "").strip()
        if body.lower().startswith("abstract "):
            body = body[9:].strip()
        doi_match = re.search(
            r"10\.\d{4,9}/[^\s\"<>\]]+",
            f"{match.group('url')} {body}",
            re.IGNORECASE,
        )
        doi = doi_match.group(0).rstrip(".,;)") if doi_match else None
        papers.append(
            {
                "title": match.group("title").strip(),
                "consensus_paper_id": match.group("paper_id"),
                "consensus_url": match.group("url").split("?")[0],
                "authors": authors_raw,
                "year": year,
                "venue": venue,
                "abstract": body,
                "cited_by_count": citations,
                "doi": doi,
                "source_id": doi or match.group("paper_id"),
            }
        )
    return papers


def _extract_search_results(result: Any) -> list[dict[str, Any]]:
    """Lift paper list from Consensus search result (fixture OR live MCP).

    Accepts:
      - ``{papers: [...]}`` (legacy fixtures / older API shape)
      - MCP ``{content:[{type:text,text:<json-or-markdown>}]}``
      - Markdown paper list (live Consensus MCP 2026-07)
    """
    if isinstance(result, dict) and result.get("isError") is True:
        return []

    payload: Any = result
    text_blobs: list[str] = []
    if isinstance(result, dict) and isinstance(result.get("content"), list):
        for part in result["content"]:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                text = part["text"]
                text_blobs.append(text)
                try:
                    payload = json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    continue
                break

    if isinstance(payload, dict):
        for key in ("papers", "hits", "results"):
            if isinstance(payload.get(key), list):
                return [row for row in payload[key] if isinstance(row, dict)]

    for text in text_blobs:
        parsed = _parse_markdown_papers(text)
        if parsed:
            return parsed
    if isinstance(result, dict) and isinstance(result.get("papers"), list):
        return [row for row in result["papers"] if isinstance(row, dict)]
    return []


def _consensus_auth_config() -> tuple[list[str], str]:
    """Resolve Consensus auth mode lazily at call time.

    Order:
    1. Bearer token via CONSENSUS_API_KEY
    2. HTTP Basic via CONSENSUS_USER_NAME + CONSENSUS_PASSWORD
    """
    api_key = os.environ.get(CONSENSUS_API_KEY_ENV_VAR, "").strip()
    if api_key:
        return [CONSENSUS_API_KEY_ENV_VAR], "bearer"

    username = os.environ.get(CONSENSUS_BASIC_AUTH_ENV_VARS[0], "").strip()
    password = os.environ.get(CONSENSUS_BASIC_AUTH_ENV_VARS[1], "").strip()
    if username and password:
        return list(CONSENSUS_BASIC_AUTH_ENV_VARS), "basic"

    # Keep legacy behavior/error surface when nothing is configured.
    return [CONSENSUS_API_KEY_ENV_VAR], "bearer"


def _mode_from_intent(intent: RetrievalIntent) -> str:
    """Resolve consensus query mode from provider hints + intent kind."""
    for hint in intent.provider_hints:
        if hint.provider == "consensus":
            mode = hint.params.get("mode")
            if mode in ("search", "paper"):
                return mode
    if intent.kind == "direct_ref":
        return "paper"
    return "search"


def _extract_search_filters(mechanical: dict[str, Any]) -> dict[str, Any]:
    """Lift mechanical criteria into deterministic filter ordering."""
    filters: dict[str, Any] = {}
    for key in ("date_range", "exclude_ids", "license_allow"):
        if key in mechanical:
            filters[key] = mechanical[key]
    return filters


def _normalize_identity_token(value: str, *, is_doi: bool = False) -> str:
    token = value.strip()
    if is_doi:
        return token.lower()
    return token


class ConsensusProvider(RetrievalAdapter):
    """Consensus retrieval adapter for query/build/filter/normalize flows."""

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="consensus",
        shape="retrieval",
        status="ready",
        capabilities=[
            "evidence-synthesis",
            "meta-analysis",
            "cross-validation-partner-to-scite",
            "study-design-tagging",
        ],
        auth_env_vars=list(CONSENSUS_AUTH_ENV_VARS),
        spec_ref="_bmad-output/implementation-artifacts/27-2.5-consensus-adapter.md",
        notes=(
            "Consensus.app retrieval adapter for deterministic search + "
            "paper-metadata retrieval, filtering, normalization, and "
            "cross-validation identity-key support."
        ),
    )

    HONORED_CRITERIA: ClassVar[frozenset[str]] = _HONORED_CRITERIA

    def __init__(
        self,
        mcp_client: MCPClient | None = None,
        *,
        mcp_url: str | None = None,
    ) -> None:
        self._mcp_client = mcp_client
        self._mcp_url = mcp_url or CONSENSUS_MCP_URL

    def _client(self) -> MCPClient:
        """Instantiate MCPClient lazily so auth env is resolved at call time."""
        if self._mcp_client is None:
            auth_env, auth_style = _consensus_auth_config()
            config = MCPServerConfig(
                url=self._mcp_url,
                auth_env=auth_env,
                auth_style=auth_style,
            )
            self._mcp_client = MCPClient({self.PROVIDER_INFO.id: config})
        return self._mcp_client

    def formulate_query(self, intent: RetrievalIntent) -> dict[str, Any]:
        mode = _mode_from_intent(intent)
        consensus_params: dict[str, Any] = {}
        for hint in intent.provider_hints:
            if hint.provider == self.PROVIDER_INFO.id:
                consensus_params = dict(hint.params)
                break

        if mode == "paper":
            return self._build_query_paper(intent, consensus_params)
        return self._build_query_search(intent, consensus_params)

    def _build_query_search(
        self,
        intent: RetrievalIntent,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a deterministic Consensus search-mode query payload."""
        mechanical = intent.acceptance_criteria.mechanical or {}
        scored = intent.acceptance_criteria.provider_scored or {}
        filters = _extract_search_filters(mechanical)

        for key in ("consensus_score_min", "study_design_allow", "sample_size_min"):
            if key in scored:
                filters[key] = scored[key]

        max_results = params.get("max_results", mechanical.get("min_results", 10))
        return {
            "mode": "search",
            "query": intent.intent,
            "max_results": int(max_results),
            "filters": filters,
        }

    def _build_query_paper(
        self,
        intent: RetrievalIntent,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a deterministic Consensus DOI-direct metadata query payload."""
        doi = _none_if_empty(params.get("doi"))
        if doi is None:
            doi = _none_if_empty(intent.intent)
        if doi is None:
            raise ValueError("Consensus paper mode requires a non-empty DOI")
        return {
            "mode": "paper",
            "doi": doi,
        }

    def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        client = self._client()
        mode = query.get("mode")

        if mode == "paper":
            args = {"doi": query["doi"]}
            result = client.call_tool(self.PROVIDER_INFO.id, _CONSENSUS_TOOL_PAPER, args)
            if isinstance(result, dict) and result:
                return [result]
            return []

        # Live Consensus MCP search tool accepts top-level ``query`` (+ optional
        # filter fields). Nested ``filters`` / ``max_results`` are ignored by the
        # hosted tool and must not be required for a successful call.
        args: dict[str, Any] = {"query": query["query"]}
        filters = query.get("filters") if isinstance(query.get("filters"), dict) else {}
        for key in (
            "year_min",
            "year_max",
            "sample_size_min",
            "study_types",
            "human",
            "sjr_max",
            "medical_mode",
            "exclude_preprints",
        ):
            if key in filters and filters[key] is not None:
                args[key] = filters[key]
            elif key in query and query[key] is not None:
                args[key] = query[key]
        result = client.call_tool(self.PROVIDER_INFO.id, _CONSENSUS_TOOL_SEARCH, args)
        return _extract_search_results(result)

    def apply_mechanical(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        out = [row for row in results if isinstance(row, dict)]

        date_range = criteria.get("date_range")
        if isinstance(date_range, list | tuple) and len(date_range) == 2:
            start, end = str(date_range[0]), str(date_range[1])
            out = [
                row
                for row in out
                if _row_date(row) is None or (start <= _row_date(row) <= end)
            ]

        exclude_ids = criteria.get("exclude_ids") or []
        if exclude_ids:
            excluded: set[str] = set()
            for item in exclude_ids:
                token = _none_if_empty(item)
                if token is None:
                    continue
                excluded.add(token)
                excluded.add(token.lower())
            out = [
                row
                for row in out
                if _row_identity_tokens(row).isdisjoint(excluded)
            ]

        license_allow = criteria.get("license_allow")
        if isinstance(license_allow, list | tuple) and license_allow:
            allow_lower = {str(item).lower() for item in license_allow}
            out = [
                row
                for row in out
                if str(row.get("license", "")).lower() in allow_lower
                or not row.get("license")
            ]

        # `min_results` is dispatcher-evaluated post-filter; no adapter mutation.
        return out

    def apply_provider_scored(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        out = [row for row in results if isinstance(row, dict)]

        score_min = _coerce_float_or_none(criteria.get("consensus_score_min"))
        if score_min is not None:
            out = [
                row
                for row in out
                if (
                    (score := _coerce_float_or_none(row.get("consensus_score")))
                    is not None
                    and score >= score_min
                )
            ]

        study_design_allow = criteria.get("study_design_allow")
        if isinstance(study_design_allow, list | tuple) and study_design_allow:
            allowed = {str(item).lower() for item in study_design_allow}
            out = [
                row
                for row in out
                if str(row.get("study_design_tag", "")).lower() in allowed
            ]

        sample_size_min = _coerce_int_or_none(criteria.get("sample_size_min"))
        if sample_size_min is not None:
            out = [
                row
                for row in out
                if (
                    (sample_size := _coerce_int_or_none(row.get("sample_size")))
                    is not None
                    and sample_size >= sample_size_min
                )
            ]

        return out

    def normalize(self, results: list[dict[str, Any]]) -> list[TexasRow]:
        rows: list[TexasRow] = []
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                continue

            doi = _none_if_empty(result.get("doi"))
            paper_id = _none_if_empty(result.get("consensus_paper_id"))
            source_id = (
                doi
                or paper_id
                or _none_if_empty(result.get("source_id"))
                or _none_if_empty(result.get("id"))
                or f"consensus-unknown-{index}"
            )

            publication_date = _none_if_empty(result.get("publication_date"))
            year = _coerce_year(result.get("year"), publication_date)
            abstract = str(result.get("abstract") or "")
            study_design_tag = _none_if_empty(result.get("study_design_tag"))
            sample_size = _coerce_int_or_none(result.get("sample_size"))
            evidence_strength = _none_if_empty(result.get("evidence_strength"))

            known_losses: list[str] = ["abstract_only"]
            if study_design_tag is None:
                known_losses.append("study_design_unknown")
            if sample_size is None:
                known_losses.append("sample_size_unknown")
            if evidence_strength is None:
                known_losses.append("evidence_strength_unknown")

            provider_metadata: dict[str, Any] = {
                "consensus": {
                    "doi": doi,
                    "consensus_paper_id": paper_id,
                    "title": str(result.get("title") or ""),
                    "authors": coerce_authors(result.get("authors")),
                    "year": year,
                    "venue": _none_if_empty(result.get("venue")),
                    "abstract": abstract,
                    "consensus_score": _coerce_float_or_none(result.get("consensus_score")),
                    "study_design_tag": study_design_tag,
                    "sample_size": sample_size,
                    "evidence_strength": evidence_strength,
                    "consensus_url": _none_if_empty(result.get("consensus_url")),
                    "known_losses": known_losses,
                }
            }

            row = build_texas_row(
                source_id=source_id,
                provider=self.PROVIDER_INFO.id,
                title=str(result.get("title") or ""),
                body=abstract,
                authors=result.get("authors"),
                date=publication_date or (f"{year:04d}-01-01" if year else None),
                provider_metadata=provider_metadata,
            )
            rows.append(row)
        return rows

    def refine(
        self,
        previous_query: dict[str, Any],
        _previous_results: list[dict[str, Any]],
        _criteria: AcceptanceCriteria,
    ) -> dict[str, Any] | None:
        if previous_query.get("mode") != "search":
            return None

        iteration = int(previous_query.get("_refinement_iteration", 0)) + 1
        current_filters = dict(previous_query.get("filters", {}))
        key_order = [
            key
            for key in CONSENSUS_REFINEMENT_KEY_ORDER
            if key in current_filters
        ]
        if not key_order:
            return None

        # Registry presence check (contract) + deterministic ordered drop.
        get_strategy("drop_filters_in_order")
        new_filters = drop_filters_in_order(
            current_filters,
            _criteria,
            iteration=1,
            order=list(key_order),
        )

        if new_filters is None:
            return None

        new_query = dict(previous_query)
        new_query["filters"] = new_filters
        new_query["_refinement_iteration"] = iteration
        return new_query

    def identity_key(self, row: TexasRow) -> str:
        metadata = row.provider_metadata or {}
        consensus_meta = metadata.get("consensus") or {}

        doi = _none_if_empty(consensus_meta.get("doi") or metadata.get("doi"))
        if doi is not None:
            return doi.lower()

        from .triangulator import normalize_title_key  # noqa: PLC0415

        title_key = normalize_title_key(
            str(consensus_meta.get("title") or row.title or "")
        )
        if title_key:
            return f"title:{title_key}"

        paper_id = _none_if_empty(
            consensus_meta.get("consensus_paper_id")
            or metadata.get("consensus_paper_id")
        )
        if paper_id is not None:
            return paper_id

        source_id = _none_if_empty(row.source_id)
        if source_id is not None:
            return source_id

        raise NotImplementedError(
            "ConsensusProvider.identity_key: no DOI / title / consensus_paper_id / "
            f"source_id on row {row!r}. Cross-validation requires one of these."
        )

    def declare_honored_criteria(self) -> set[str]:
        return set(self.HONORED_CRITERIA)


def _row_date(result: dict[str, Any]) -> str | None:
    publication_date = result.get("publication_date")
    if isinstance(publication_date, str) and publication_date:
        return publication_date[:10]
    year = result.get("year")
    if isinstance(year, int):
        return f"{year:04d}-01-01"
    if isinstance(year, str):
        parsed_year = _coerce_int_or_none(year)
        if parsed_year is not None:
            return f"{parsed_year:04d}-01-01"
    return None


def _row_identity_tokens(result: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in ("doi", "consensus_paper_id", "source_id", "id"):
        value = result.get(key)
        if value is not None and str(value):
            token = _normalize_identity_token(str(value), is_doi=(key == "doi"))
            tokens.add(token)
            tokens.add(token.lower())
    return tokens


def _none_if_empty(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if value is None:
        return None
    as_str = str(value).strip()
    return as_str or None


def _coerce_int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_year(year: Any, publication_date: str | None) -> int | None:
    parsed_year = _coerce_int_or_none(year)
    if parsed_year is not None:
        return parsed_year
    if publication_date and len(publication_date) >= 4:
        return _coerce_int_or_none(publication_date[:4])
    return None


__all__ = ["ConsensusProvider"]
