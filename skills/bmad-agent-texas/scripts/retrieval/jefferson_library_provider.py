"""`JeffersonLibraryProvider` — institutional full-text via browser SSO session.

Agentic Research Foundations R5. Full-text is **additive** to the DOI identity
spine (Scite/Consensus remain primary for cross-validation). Live fetch uses
the proven headed Playwright + Chrome cookie-copy pattern (see
``jefferson-access-probe-session3-20260710T213250Z``); bare HTTP cannot clear
Cloudflare / ``cookieAbsent``.

Hermetic tests inject ``fetch_fn`` — zero network, zero Playwright.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)
from .normalize import build_texas_row

JEFFERSON_CHROME_USER_DATA_ENV = "JEFFERSON_CHROME_USER_DATA_DIR"
JEFFERSON_ALLOW_LIVE_ENV = "JEFFERSON_LIBRARY_LIVE"

_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)

FetchFn = Callable[[dict[str, Any]], list[dict[str, Any]]]


class JeffersonLibraryAuthError(RuntimeError):
    """SSO / browser-session unavailable or blocked (no transport types leak)."""


class JeffersonLibraryFetchError(RuntimeError):
    """Full-text fetch failed after session attempt."""


def default_chrome_user_data_dir() -> Path:
    """Windows Chrome default; override via ``JEFFERSON_CHROME_USER_DATA_DIR``."""
    override = os.environ.get(JEFFERSON_CHROME_USER_DATA_ENV, "").strip()
    if override:
        return Path(override)
    return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"


def jefferson_session_preflight() -> dict[str, Any]:
    """Report whether a live Jefferson session fetch is plausible."""
    chrome_user = default_chrome_user_data_dir()
    chrome_count: int | str = "unknown"
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-Process chrome -ErrorAction SilentlyContinue).Count",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        raw = (proc.stdout or "").strip()
        chrome_count = int(raw) if raw.isdigit() else raw or "unknown"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        chrome_count = "unknown"

    live_armed = os.environ.get(JEFFERSON_ALLOW_LIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "on",
        "yes",
    }
    return {
        "chrome_user_data": str(chrome_user),
        "chrome_user_data_exists": chrome_user.is_dir(),
        "chrome_process_count": chrome_count,
        "cookies_likely_locked": isinstance(chrome_count, int) and chrome_count > 0,
        "live_armed": live_armed,
        "ready": bool(
            live_armed
            and chrome_user.is_dir()
            and not (isinstance(chrome_count, int) and chrome_count > 0)
        ),
    }


def _copy_chrome_profile(src_user: Path, dst_user: Path) -> None:
    dst_user.mkdir(parents=True, exist_ok=True)
    if (src_user / "Local State").exists():
        shutil.copy2(src_user / "Local State", dst_user / "Local State")
    src_default = src_user / "Default"
    dst_default = dst_user / "Default"
    dst_default.mkdir(parents=True, exist_ok=True)
    for rel in ("Network", "Preferences", "Secure Preferences"):
        src = src_default / rel
        if not src.exists():
            continue
        dst = dst_default / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def _extract_doi(text: str) -> str | None:
    match = _DOI_RE.search(text or "")
    if not match:
        return None
    return match.group(0).rstrip(".,;)").lower()


def fetch_fulltext_via_browser_session(query: dict[str, Any]) -> list[dict[str, Any]]:
    """Live path: headed Chrome persistent context + in-page fetch.

    Raises ``JeffersonLibraryAuthError`` / ``JeffersonLibraryFetchError``.
    """
    preflight = jefferson_session_preflight()
    if not preflight["live_armed"]:
        raise JeffersonLibraryAuthError(
            f"Set {JEFFERSON_ALLOW_LIVE_ENV}=1 to arm Jefferson live fetch "
            "(browser SSO session required)."
        )
    if not preflight["chrome_user_data_exists"]:
        raise JeffersonLibraryAuthError(
            f"Chrome user data missing at {preflight['chrome_user_data']}"
        )
    if preflight["cookies_likely_locked"]:
        raise JeffersonLibraryAuthError(
            "Chrome is running — quit Chrome so the cookie DB can be copied "
            "(Jefferson SSO session path)."
        )

    doi = str(query.get("doi") or "")
    pdf_url = str(query.get("pdf_url") or "")
    openurl = str(query.get("openurl") or "")
    if not pdf_url and doi:
        # Generic publisher PDF path works for NEJM probe; callers may override.
        pdf_url = f"https://www.nejm.org/doi/pdf/{doi}"
    if not openurl and doi:
        openurl = (
            "https://jefferson.primo.exlibrisgroup.com/discovery/openurl"
            f"?vid=01TJU_INST:01TJU&url_ver=Z39.88-2004&rft_id=info:doi/{doi}"
        )
    if not pdf_url:
        raise JeffersonLibraryFetchError("jefferson_library query missing pdf_url/doi")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise JeffersonLibraryAuthError(
            f"playwright not installed: {exc}"
        ) from exc

    chrome_user = Path(preflight["chrome_user_data"])
    tmp = Path(tempfile.mkdtemp(prefix="jeff-library-"))
    try:
        _copy_chrome_profile(chrome_user, tmp)
    except OSError as exc:
        raise JeffersonLibraryAuthError(
            f"failed to copy Chrome profile cookies: {exc}"
        ) from exc

    pdf_bytes: bytes | None = None
    final_url = pdf_url
    try:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(tmp),
                channel="chrome",
                headless=False,
                accept_downloads=True,
                viewport={"width": 1400, "height": 900},
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled"],
            )
            try:
                page = context.new_page()
                page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', "
                    "{get: () => undefined});"
                )
                if openurl:
                    page.goto(openurl, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(3000)
                page.goto(pdf_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)
                final_url = page.url
                fetch_meta = page.evaluate(
                    """async (url) => {
                      const r = await fetch(url, {credentials:'include'});
                      const buf = await r.arrayBuffer();
                      const u8 = new Uint8Array(buf);
                      return {
                        status: r.status,
                        size: u8.length,
                        contentType: r.headers.get('content-type'),
                        isPdf: u8[0]===0x25 && u8[1]===0x50 &&
                               u8[2]===0x44 && u8[3]===0x46,
                        bytes: Array.from(u8)
                      };
                    }""",
                    pdf_url,
                )
                if fetch_meta.get("isPdf") and fetch_meta.get("bytes"):
                    pdf_bytes = bytes(fetch_meta["bytes"])
            finally:
                context.close()
    except JeffersonLibraryAuthError:
        raise
    except Exception as exc:  # noqa: BLE001 — map to library error surface
        raise JeffersonLibraryFetchError(
            f"browser session fetch failed: {type(exc).__name__}: {exc}"
        ) from None

    if not pdf_bytes or pdf_bytes[:4] != b"%PDF":
        raise JeffersonLibraryFetchError(
            "Jefferson session did not return PDF bytes "
            f"(final_url={final_url!r}; Cloudflare/cookieAbsent likely)"
        )

    digest = hashlib.sha256(pdf_bytes).hexdigest()
    return [
        {
            "doi": doi,
            "title": str(query.get("title") or f"Full text for {doi}"),
            "pdf_bytes_len": len(pdf_bytes),
            "pdf_sha256": digest,
            "content_type": "application/pdf",
            "access_url": final_url,
            "pdf_url": pdf_url,
            "openurl": openurl or None,
            "is_pdf": True,
            "access_path": "browser_session_page_fetch",
        }
    ]


class JeffersonLibraryProvider(RetrievalAdapter):
    """Institutional library full-text adapter (DOI → PDF/metadata)."""

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="jefferson_library",
        shape="retrieval",
        status="ready",
        capabilities=[
            "institutional-fulltext",
            "doi-openurl",
            "browser-session-sso",
        ],
        auth_env_vars=[JEFFERSON_CHROME_USER_DATA_ENV, JEFFERSON_ALLOW_LIVE_ENV],
        spec_ref=(
            "_bmad-output/implementation-artifacts/"
            "agentic-research-foundations-stories-2026-07-10.md"
        ),
        notes=(
            "R5 Jefferson / TJU library. Live = headed Playwright + Chrome SSO "
            "cookies (not API key). Full-text additive; DOI identity spine stays "
            "Scite/Consensus. Arm with JEFFERSON_LIBRARY_LIVE=1; quit Chrome first."
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
            doi = _extract_doi(intent.intent) or intent.intent.strip()
        doi = doi.rstrip(".,;)")
        pdf_url = str(params.get("pdf_url") or "").strip() or None
        openurl = str(params.get("openurl") or "").strip() or None
        title = str(params.get("title") or "").strip() or None
        return {
            "mode": "fulltext_by_doi",
            "doi": doi,
            "pdf_url": pdf_url,
            "openurl": openurl,
            "title": title,
        }

    def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        if self._fetch_fn is not None:
            return list(self._fetch_fn(query))
        return fetch_fulltext_via_browser_session(query)

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
                if str(row.get("doi") or "").lower() not in exclude_set
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
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                continue
            doi = str(result.get("doi") or "").strip() or f"jefferson-unknown-{index}"
            title = str(result.get("title") or f"Jefferson full text {doi}")
            pdf_len = int(result.get("pdf_bytes_len") or 0)
            body = (
                f"[jefferson_library full-text PDF; {pdf_len} bytes; "
                f"sha256={result.get('pdf_sha256')}]"
            )
            rows.append(
                build_texas_row(
                    source_id=doi,
                    provider=self.PROVIDER_INFO.id,
                    title=title,
                    body=body,
                    authority_tier="peer_reviewed",
                    provider_metadata={
                        "jefferson_library": {
                            "doi": doi,
                            "pdf_bytes_len": pdf_len,
                            "pdf_sha256": result.get("pdf_sha256"),
                            "content_type": result.get("content_type"),
                            "access_url": result.get("access_url"),
                            "pdf_url": result.get("pdf_url"),
                            "openurl": result.get("openurl"),
                            "is_pdf": bool(result.get("is_pdf")),
                            "access_path": result.get("access_path"),
                            "known_losses": ["fulltext_bytes_not_inlined_in_body"],
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
        # Direct-ref full-text: loosening cannot help (gamma_docs precedent).
        return None

    def identity_key(self, row: TexasRow) -> str:
        meta = (row.provider_metadata or {}).get("jefferson_library") or {}
        doi = str(meta.get("doi") or row.source_id or "").strip()
        if doi.lower().startswith("10."):
            return doi.lower()
        if row.source_id:
            return str(row.source_id)
        raise NotImplementedError(
            "JeffersonLibraryProvider.identity_key: DOI/source_id required "
            f"on row {row!r}"
        )

    def declare_honored_criteria(self) -> set[str]:
        return set(self.HONORED_CRITERIA)


__all__ = [
    "JEFFERSON_ALLOW_LIVE_ENV",
    "JEFFERSON_CHROME_USER_DATA_ENV",
    "JeffersonLibraryAuthError",
    "JeffersonLibraryFetchError",
    "JeffersonLibraryProvider",
    "default_chrome_user_data_dir",
    "fetch_fulltext_via_browser_session",
    "jefferson_session_preflight",
]
