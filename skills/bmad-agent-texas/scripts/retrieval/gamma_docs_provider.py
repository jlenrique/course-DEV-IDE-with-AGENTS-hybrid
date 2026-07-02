"""`GammaDocsProvider` — Gamma live-documentation fetch adapter (Leg-E AC#1).

Shape-3 retrieval adapter (`kind="direct_ref"`) that fetches developers.gamma.app
documentation pages as RAW MARKDOWN (the `.md` suffix endpoints). It exists for
the Leg-E doc-audit driver (`scripts/utilities/audit_gamma_docs.py`), which
compares live doc content against code-authoritative frozen enums and doc-fact
expectations.

PURE LEAF (Winston W-1, binding): ZERO ``app.*`` imports, zero writes, no LLM,
no retry, no ledger knowledge. All comparison + observation-filing lives in the
driver. An ``app.*`` import here would execute inside EVERY production Texas
retrieval dispatch (``retrieval/__init__.py`` eager-imports every provider).

Three INTENTIONAL degeneracies, declared per anti-pattern #3 (Texas T-1) so no
future dev "fixes" them into ceremony:

* ``formulate_query`` is a pass-through: it canonicalizes + dedupes the
  ``params: {pages: [...]}`` URL list — there is no query DSL to formulate.
* ``refine()`` always returns ``None``: loosening cannot help a direct-ref
  document fetch.
* cross-validation is N/A: there is exactly one source of truth for a doc URL
  (``identity_key`` = canonical URL, so the dispatcher preflight still works).

Determinism discipline (Winston W-6): no clock/LLM/retry in the DETERMINISTIC
methods (formulate_query / normalize / refine / identity_key). ``execute`` is
the network step; it records ``fetched_at`` at fetch time as part of the raw
observation (AC#1 requires it in ``provider_metadata.gamma_docs``) — the audit
driver separately stamps ``observed_at`` for ledger rows.
"""

from __future__ import annotations

import hashlib
import time
import unicodedata
from datetime import UTC, datetime
from typing import Any, ClassVar
from urllib.parse import urlsplit, urlunsplit

import requests

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)

# ---------------------------------------------------------------------------
# Module-level constants — data, not inference.
# ---------------------------------------------------------------------------

GAMMA_DOCS_USER_AGENT = "bmad-gamma-docs-audit/0.1"
"""Polite, self-identifying UA for all doc fetches (story Dev Notes)."""

GAMMA_DOCS_FETCH_INTERVAL_S = 1.0
"""<= 1 request/second: sleep between consecutive pages in one execute()."""

GAMMA_DOCS_TIMEOUT_S = 30.0
"""Per-request timeout. No retry on expiry (M-11: zero mid-run retries)."""

GAMMA_DOCS_EXTRACTION_PATTERN = "raw-markdown-passthrough"
"""The only extraction pattern v1: the `.md` endpoint body IS the content.
Recorded in provider_metadata so structural_fidelity is deterministically
assignable from it (Texas T-9)."""


class GammaDocsTransportError(RuntimeError):
    """Transport-level fetch failure (DNS/timeout/connection).

    Raised so no ``requests.*``/``urllib3.*`` exception type leaks across the
    adapter boundary (Option-X discipline, scite precedent). HTTP error
    STATUSES are not exceptions — they surface as raw rows with
    ``http_status`` set, which the audit driver classifies ``indeterminate``
    per S-2. A 401 during an audit is a known Gamma burst-throttle signal and
    must reach the driver as data, not a crash.
    """


_MARKDOWN_CONTENT_TYPES = frozenset({"text/markdown", "text/plain"})
"""The text/markdown Content-Type family (P8): anything else on a 200 gets a
``content_type_not_markdown`` known_losses sentinel (a missing header passes)."""


def canonical_doc_url(url: str) -> str:
    """Canonicalize a doc URL: strip whitespace, fragment, query, and any
    trailing slash; lowercase scheme + host (path case is significant and
    preserved). Empty/relative URLs fail loud (N7).

    The canonical URL is the row identity (Texas T-3: identity is the URL;
    the content digest lives in provider_metadata, never in the identity).
    """
    cleaned = str(url).strip()
    parts = urlsplit(cleaned)
    if not parts.scheme or not parts.netloc:
        raise ValueError(
            f"canonical_doc_url requires an absolute http(s) URL with a host; "
            f"got {url!r} (N7)"
        )
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", "")
    )


def normalize_doc_text(text: str) -> str:
    """Normalize extracted text: strip a leading BOM (P9), CRLF/CR -> LF,
    strip trailing whitespace per line (P10), then unicode NFC (A-8 / M-6).

    Digests and anchor matching run over THIS form only — raw-byte churn
    (CDN/build artifacts, encoding form, trailing-space churn) must never
    read as doc drift.
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    unified = text.replace("\r\n", "\n").replace("\r", "\n")
    unified = "\n".join(line.rstrip() for line in unified.split("\n"))
    return unicodedata.normalize("NFC", unified)


def content_digest(normalized_text: str) -> str:
    """sha256 over the NORMALIZED text, ``sha256:`` prefixed (M-6)."""
    return "sha256:" + hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def _page_title(normalized_text: str) -> str:
    """First markdown H1 (``# ...``) line, or empty string."""
    for line in normalized_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


class GammaDocsProvider(RetrievalAdapter):
    """developers.gamma.app raw-markdown fetch adapter — Leg-E."""

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="gamma_docs",
        shape="retrieval",
        # T-4 status discipline: landed-unproven = "stub". Flips to "ready"
        # ONLY in the change-set carrying the AC#9-12 live proof.
        status="stub",
        capabilities=["doc-fetch", "raw-markdown", "doc-audit"],
        auth_env_vars=[],  # T-5: the adapter NEVER holds GAMMA_API_KEY.
        spec_ref="_bmad-output/implementation-artifacts/leg-e-gamma-docs-live-doc-audit.md",
        notes=(
            "doc-audit tooling — not a course-content retrieval source. Fetches "
            "developers.gamma.app pages as raw markdown (.md endpoints) for the "
            "gamma-doc-audit driver. Intentional degeneracies (do not 'fix'): "
            "pass-through formulate_query (params {pages:[...]} only); "
            "refine() -> None (loosening cannot help a direct-ref doc fetch); "
            "cross-validate N/A (identity_key = canonical doc URL). Pure leaf: "
            "no app.* imports, no writes, no retry."
        ),
    )

    def __init__(self, session: Any | None = None) -> None:
        # Optional injected client (requests.Session-compatible: has .get).
        # Default ctor must work — AdapterFactory.get() calls cls() no-args.
        self._session = session

    # ---- formulate_query: pass-through with params purity (T-2) ------------

    def formulate_query(self, intent: RetrievalIntent) -> dict[str, Any]:
        """Canonicalize + dedupe ``params.pages`` for the gamma_docs hint.

        Deterministic; byte-identical across invocations. Rejects any params
        vocabulary beyond ``pages`` (audit-fact knowledge is DRIVER knowledge,
        recorded in ``semantic_deferred`` as a string when needed).
        """
        params: dict[str, Any] = {}
        for hint in intent.provider_hints:
            if hint.provider == self.PROVIDER_INFO.id:
                params = dict(hint.params)
                break
        unknown = sorted(set(params) - {"pages"})
        if unknown:
            raise ValueError(
                f"gamma_docs params purity: only 'pages' is accepted; got "
                f"unknown keys {unknown} (Texas T-2)"
            )
        pages = params.get("pages")
        if not isinstance(pages, list) or not pages:
            raise ValueError(
                "gamma_docs requires params: {pages: [<doc-url>, ...]} with at "
                "least one page URL"
            )
        seen: set[str] = set()
        canonical: list[str] = []
        for page in pages:
            url = canonical_doc_url(str(page))
            if url not in seen:
                seen.add(url)
                canonical.append(url)
        return {"pages": canonical}

    # ---- execute: polite GET per page, no retry ----------------------------

    def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """One GET per canonical page URL; <=1 req/s; explicit UTF-8 decode.

        Returns raw per-page dicts (normalize() converts to TexasRow). HTTP
        error statuses are DATA (rows with ``http_status``); transport-level
        failures raise :class:`GammaDocsTransportError` — the audit driver
        catches per-page and classifies ``indeterminate`` (W-5 / S-2).
        """
        client = self._session or requests
        rows: list[dict[str, Any]] = []
        for index, url in enumerate(query["pages"]):
            if index:
                time.sleep(GAMMA_DOCS_FETCH_INTERVAL_S)
            fetched_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                response = client.get(
                    url,
                    headers={"User-Agent": GAMMA_DOCS_USER_AGENT},
                    timeout=GAMMA_DOCS_TIMEOUT_S,
                )
            except requests.RequestException as exc:
                raise GammaDocsTransportError(
                    f"gamma_docs transport failure fetching {url}: {exc}"
                ) from exc
            # A-8 / P9: decode bytes as UTF-8 explicitly — never requests'
            # apparent-encoding guess. STRICT first; a stream that is not
            # valid UTF-8 falls back to errors="replace" and is FLAGGED so
            # normalize() can file a decode_replacement known_losses sentinel.
            try:
                text = response.content.decode("utf-8")
                decode_replacement = False
            except UnicodeDecodeError:
                text = response.content.decode("utf-8", errors="replace")
                decode_replacement = True
            rows.append(
                {
                    "doc_url": url,
                    "http_status": int(response.status_code),
                    "text": text,
                    "fetched_at": fetched_at,
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    # P8: the Content-Type is honesty data for normalize().
                    "content_type": response.headers.get("Content-Type"),
                    # N2: the post-redirect response URL (requests follows
                    # redirects by default).
                    "final_url": str(response.url) if response.url else url,
                    "decode_replacement": decode_replacement,
                }
            )
        return rows

    # ---- declared passthrough filters (degeneracy, T-1) --------------------

    def apply_mechanical(
        self, results: list[dict[str, Any]], criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Declared pass-through: doc pages carry no mechanical filter surface."""
        return results

    def apply_provider_scored(
        self, results: list[dict[str, Any]], criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Declared pass-through: no provider-native scoring signals exist."""
        return results

    # ---- normalize: honest TexasRow (T-9) ----------------------------------

    def normalize(self, results: list[dict[str, Any]]) -> list[TexasRow]:
        rows: list[TexasRow] = []
        for raw in results:
            doc_url = str(raw.get("doc_url") or "")
            status = raw.get("http_status")
            ok = status == 200
            normalized = normalize_doc_text(str(raw.get("text") or ""))
            known_losses: list[str] = []
            if not ok:
                known_losses.append(f"fetch_failed_http_{status}")
            # P8: a 200 whose Content-Type is outside the text/markdown
            # family (text/markdown, text/plain, or missing) is NOT honest
            # markdown — sentinel it; the driver's T-7 floor then keeps the
            # page from ever minting `confirmed`.
            content_type = str(raw.get("content_type") or "")
            main_type = content_type.split(";", 1)[0].strip().lower()
            if ok and main_type and main_type not in _MARKDOWN_CONTENT_TYPES:
                known_losses.append("content_type_not_markdown")
            # P9: replacement-decoded bytes are a lossy read of the page.
            if ok and raw.get("decode_replacement"):
                known_losses.append("decode_replacement")
            # N2: a redirect away from the requested canonical URL means the
            # fetched content may not be the cataloged page.
            final_url = str(raw.get("final_url") or "") or doc_url
            if ok and final_url:
                try:
                    redirected = canonical_doc_url(final_url) != doc_url
                except ValueError:
                    redirected = True
                if redirected:
                    known_losses.append("redirected")
            body = normalized if ok else ""
            provider_metadata = {
                "gamma_docs": {
                    "doc_url": doc_url,
                    "final_url": final_url,
                    "content_type": content_type or None,
                    "fetched_at": raw.get("fetched_at"),
                    "http_status": status,
                    "content_sha256": content_digest(normalized) if ok else None,
                    "raw_sha256": (
                        "sha256:"
                        + hashlib.sha256(
                            str(raw.get("text") or "").encode("utf-8")
                        ).hexdigest()
                        if ok
                        else None
                    ),
                    "extraction_pattern": GAMMA_DOCS_EXTRACTION_PATTERN,
                    "etag": raw.get("etag"),
                    "last_modified": raw.get("last_modified"),
                    "known_losses": known_losses,
                    "page_title": _page_title(normalized) if ok else "",
                    "content_length_chars": len(normalized) if ok else 0,
                },
            }
            rows.append(
                TexasRow(
                    source_id=doc_url,
                    title=_page_title(normalized) if ok else "",
                    body=body,
                    provider=self.PROVIDER_INFO.id,
                    provider_metadata=provider_metadata,
                    source_origin="operator-named",
                    # Honest, deterministic from the extraction pattern (T-9):
                    # raw-markdown passthrough is lossless when the fetch
                    # succeeded; unknown (None + sentinel) when it did not.
                    completeness_ratio=1.0 if ok else None,
                    structural_fidelity=1.0 if ok else None,
                )
            )
        return rows

    # ---- refine: declared degenerate ---------------------------------------

    def refine(
        self,
        previous_query: dict[str, Any],
        previous_results: list[dict[str, Any]],
        criteria: AcceptanceCriteria,
    ) -> None:
        """Always None: a direct-ref doc fetch has nothing to loosen (T-1)."""
        return None

    # ---- identity: canonical doc URL (T-3) ---------------------------------

    def identity_key(self, row: TexasRow) -> str:
        meta = (row.provider_metadata or {}).get("gamma_docs") or {}
        doc_url = meta.get("doc_url")
        if isinstance(doc_url, str) and doc_url:
            return doc_url
        if row.source_id:
            return row.source_id
        raise NotImplementedError(
            f"GammaDocsProvider.identity_key: no doc_url / source_id on row "
            f"{row!r}."
        )

    def declare_honored_criteria(self) -> set[str]:
        """Declared degenerate: audit-fact vocabulary is driver knowledge (T-2)."""
        return set()


__all__ = [
    "GAMMA_DOCS_EXTRACTION_PATTERN",
    "GAMMA_DOCS_FETCH_INTERVAL_S",
    "GAMMA_DOCS_TIMEOUT_S",
    "GAMMA_DOCS_USER_AGENT",
    "GammaDocsProvider",
    "GammaDocsTransportError",
    "canonical_doc_url",
    "content_digest",
    "normalize_doc_text",
]
