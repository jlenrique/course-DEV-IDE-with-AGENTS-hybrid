"""`OpenAlexProvider` — open metadata + OA full-text *links* (no SSO).

Usual-suspect open acquisition (operator 2026-07-10 TRAIL). Complements
Scite/Consensus discovery and Jefferson paywall PDF. Scope (party MUST):
DOI metadata + open-access location URLs only — **no** PDF download, no SSO,
no claim validation.

Hermetic tests inject ``fetch_fn`` — zero network.
Live uses the public OpenAlex Works API (mailto courtesy header optional).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)
from .normalize import build_texas_row

OPENALEX_MAILTO_ENV = "OPENALEX_MAILTO"
OPENALEX_API_BASE = "https://api.openalex.org"

_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)

FetchFn = Callable[[dict[str, Any]], list[dict[str, Any]]]


class OpenAlexFetchError(RuntimeError):
    """OpenAlex HTTP / parse failure (no transport types leak)."""


def _extract_doi(text: str) -> str | None:
    match = _DOI_RE.search(text or "")
    if not match:
        return None
    return match.group(0).rstrip(".,;)")


def _clean_url(value: str) -> str:
    """Strip common upstream junk from OpenAlex location URLs."""
    return value.strip().strip("\"'").rstrip(".,;)")


def _oa_urls_from_work(work: dict[str, Any]) -> list[str]:
    """Collect open-access landing / PDF *links* (never download bytes)."""
    urls: list[str] = []
    oa = work.get("open_access") if isinstance(work.get("open_access"), dict) else {}
    oa_url = _clean_url(str(oa.get("oa_url") or ""))
    if oa_url:
        urls.append(oa_url)
    primary = work.get("primary_location")
    if isinstance(primary, dict):
        for key in ("pdf_url", "landing_page_url"):
            value = _clean_url(str(primary.get(key) or ""))
            if value and value not in urls:
                urls.append(value)
    for loc in work.get("locations") or []:
        if not isinstance(loc, dict):
            continue
        for key in ("pdf_url", "landing_page_url"):
            value = _clean_url(str(loc.get(key) or ""))
            if value and value not in urls:
                urls.append(value)
    return urls


def _normalize_work(work: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(work, dict):
        return None
    ids = work.get("ids") if isinstance(work.get("ids"), dict) else {}
    doi = str(ids.get("doi") or "").strip()
    if doi.lower().startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/") :]
    if not doi:
        doi = _extract_doi(str(work.get("doi") or work.get("id") or "")) or ""
    openalex_id = str(work.get("id") or ids.get("openalex") or "").strip()
    source_id = doi or openalex_id
    if not source_id:
        return None
    title = str(work.get("display_name") or work.get("title") or "").strip()
    year = work.get("publication_year")
    date = str(year) if year is not None else None
    oa = work.get("open_access") if isinstance(work.get("open_access"), dict) else {}
    authors: list[str] = []
    for authorship in work.get("authorships") or []:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author")
        if isinstance(author, dict):
            name = str(author.get("display_name") or "").strip()
            if name:
                authors.append(name)
    return {
        "doi": doi or None,
        "openalex_id": openalex_id or None,
        "source_id": source_id,
        "title": title,
        "date": date,
        "authors": authors,
        "is_oa": bool(oa.get("is_oa")),
        "oa_status": str(oa.get("oa_status") or "") or None,
        "oa_urls": _oa_urls_from_work(work),
        "cited_by_count": work.get("cited_by_count"),
        "type": str(work.get("type") or "") or None,
    }


def fetch_works_via_openalex_api(query: dict[str, Any]) -> list[dict[str, Any]]:
    """Live OpenAlex Works fetch (metadata + OA links only)."""
    mode = str(query.get("mode") or "search")
    mailto = os.environ.get(OPENALEX_MAILTO_ENV, "").strip() or "research@localhost"
    headers = {
        "User-Agent": f"course-DEV-IDE-openalex/1.0 (mailto:{mailto})",
        "Accept": "application/json",
    }
    if mode == "doi":
        doi = str(query.get("doi") or "").strip()
        if not doi:
            return []
        # OpenAlex work id form: https://doi.org/{doi}
        encoded = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
        url = f"{OPENALEX_API_BASE}/works/{encoded}"
    else:
        search = str(query.get("search") or "").strip()
        if not search:
            return []
        params = urllib.parse.urlencode(
            {"search": search, "per_page": int(query.get("per_page") or 5)}
        )
        url = f"{OPENALEX_API_BASE}/works?{params}"

    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise OpenAlexFetchError(f"OpenAlex HTTP {exc.code}: {exc.reason}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise OpenAlexFetchError(f"OpenAlex fetch failed: {exc}") from exc

    if mode == "doi":
        normalized = _normalize_work(payload)
        return [normalized] if normalized else []

    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        return []
    out: list[dict[str, Any]] = []
    for work in results:
        normalized = _normalize_work(work)
        if normalized:
            out.append(normalized)
    return out


class OpenAlexProvider(RetrievalAdapter):
    """OpenAlex open-metadata + OA-link discovery adapter."""

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="openalex",
        shape="retrieval",
        status="ready",
        capabilities=[
            "doi-metadata",
            "oa-fulltext-links",
            "open-bibliographic",
        ],
        auth_env_vars=[OPENALEX_MAILTO_ENV],
        spec_ref=(
            "_bmad-output/planning-artifacts/"
            "trail-trio-party-greenlight-2026-07-10.md"
        ),
        notes=(
            "Usual-suspect open acquisition. Public API; optional OPENALEX_MAILTO "
            "courtesy header. Metadata + OA URLs only — no PDF bytes, no SSO."
        ),
    )

    HONORED_CRITERIA: ClassVar[frozenset[str]] = frozenset(
        {"min_results", "exclude_ids"}
    )

    def __init__(self, *, fetch_fn: FetchFn | None = None) -> None:
        self._fetch_fn = fetch_fn

    def formulate_query(self, intent: RetrievalIntent) -> dict[str, Any]:
        params: dict[str, Any] = {}
        for hint in intent.provider_hints:
            if hint.provider == self.PROVIDER_INFO.id:
                params = dict(hint.params)
                break
        doi = str(params.get("doi") or "").strip()
        if not doi:
            doi = _extract_doi(str(params.get("search") or intent.intent)) or ""
        search = str(params.get("search") or "").strip()
        if doi:
            return {"mode": "doi", "doi": doi.rstrip(".,;)")}
        if not search:
            search = intent.intent.strip()
        return {
            "mode": "search",
            "search": search,
            "per_page": int(params.get("per_page") or 5),
        }

    def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        if self._fetch_fn is not None:
            return list(self._fetch_fn(query))
        return fetch_works_via_openalex_api(query)

    def apply_mechanical(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        out = list(results)
        exclude = criteria.get("exclude_ids") or []
        if exclude:
            exclude_set = {str(x).lower() for x in exclude}
            out = [
                row
                for row in out
                if str(row.get("doi") or row.get("source_id") or "").lower()
                not in exclude_set
            ]
        return out

    def apply_provider_scored(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return list(results)

    def normalize(self, results: list[dict[str, Any]]) -> list[TexasRow]:
        rows: list[TexasRow] = []
        for result in results:
            if not isinstance(result, dict):
                continue
            source_id = str(result.get("source_id") or result.get("doi") or "").strip()
            if not source_id:
                continue
            title = str(result.get("title") or "")
            oa_urls = result.get("oa_urls") if isinstance(result.get("oa_urls"), list) else []
            is_oa = bool(result.get("is_oa"))
            body = (
                f"[openalex metadata; is_oa={is_oa}; "
                f"oa_status={result.get('oa_status')}; "
                f"oa_link_count={len(oa_urls)}]"
            )
            rows.append(
                build_texas_row(
                    source_id=source_id,
                    provider=self.PROVIDER_INFO.id,
                    title=title,
                    body=body,
                    authors=result.get("authors"),
                    date=result.get("date"),
                    # OA status is not peer-review standing (Amelia CLOSE MUST-FIX).
                    authority_tier=None,
                    provider_metadata={
                        "openalex": {
                            "doi": result.get("doi"),
                            "openalex_id": result.get("openalex_id"),
                            "is_oa": is_oa,
                            "oa_status": result.get("oa_status"),
                            "oa_urls": list(oa_urls),
                            "cited_by_count": result.get("cited_by_count"),
                            "type": result.get("type"),
                            "known_losses": (
                                []
                                if oa_urls
                                else ["no_oa_fulltext_link_on_record"]
                            ),
                        }
                    },
                )
            )
        return rows

    def refine(
        self,
        previous_query: dict[str, Any],
        _previous_results: list[dict[str, Any]],
        _criteria: AcceptanceCriteria,
    ) -> dict[str, Any] | None:
        # Thin v1: no iterative refine (search already returns a page).
        return None

    def identity_key(self, row: TexasRow) -> str:
        meta = (row.provider_metadata or {}).get("openalex") or {}
        doi = str(meta.get("doi") or "").strip()
        if doi.lower().startswith("10."):
            return doi.lower()
        if row.source_id:
            return str(row.source_id).lower()
        raise NotImplementedError(
            f"OpenAlexProvider.identity_key: DOI/source_id required on row {row!r}"
        )

    def declare_honored_criteria(self) -> set[str]:
        return set(self.HONORED_CRITERIA)


__all__ = [
    "OPENALEX_API_BASE",
    "OPENALEX_MAILTO_ENV",
    "OpenAlexFetchError",
    "OpenAlexProvider",
    "fetch_works_via_openalex_api",
]
