"""Source bundle construction: URLs, local files, Notion, Box, Playwright HTML, PDF, DOCX."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from docx import Document as _DocxDocument
from docx.oxml.ns import qn as _docx_qn
from docx.table import Table as _DocxTable
from docx.text.paragraph import Paragraph as _DocxParagraph

from scripts.api_clients.notion_client import NotionClient


class GammaDocsURLNotSupportedError(ValueError):
    """Hosted Gamma doc URLs cannot be fetched via HTTP.

    Use Gary / Gamma API or Playwright capture instead.
    """


def is_gamma_app_docs_url(url: str) -> bool:
    """True for gamma.app viewer URLs (Cloudflare / JS); never use plain GET for these."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    path_lower = (parsed.path or "").lower()
    return host == "gamma.app" and "/docs/" in path_lower


def _reject_gamma_docs_url(url: str) -> None:
    if is_gamma_app_docs_url(url):
        raise GammaDocsURLNotSupportedError(
            "gamma.app/docs URLs are not supported for HTTP fetch (Cloudflare). "
            "Use Gary + gamma-api-mastery / Gamma MCP to export the deck, then "
            "wrangle_local_pdf() on the export; or save HTML via Playwright and "
            "wrangle_playwright_saved_html()."
        )


def verify_local_source_paths(paths: Sequence[str | Path]) -> list[Path]:
    """Return paths that are missing or not files (preflight before bundles)."""
    missing: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_file():
            missing.append(p)
    return missing


def require_local_source_files(paths: Sequence[str | Path]) -> None:
    """Raise FileNotFoundError if any expected local source file is absent."""
    missing = verify_local_source_paths(paths)
    if missing:
        joined = ", ".join(str(p) for p in missing)
        raise FileNotFoundError(
            f"Expected source file(s) missing for bundle / preflight: {joined}"
        )


def extract_pdf_text(
    path: str | Path,
    *,
    max_pages: int | None = 120,
    max_chars: int | None = 600_000,
) -> tuple[str, dict[str, Any]]:
    """Extract text from a text-based PDF using pypdf.

    Args:
        path: Path to the PDF.
        max_pages: Cap pages read (None = all).
        max_chars: Cap total extracted characters (None = unlimited).

    Returns:
        (text, meta) where meta includes pages_total, pages_extracted, truncated, engine.
    """
    from pypdf import PdfReader

    p = Path(path)
    reader = PdfReader(str(p))
    total = len(reader.pages)
    limit = total if max_pages is None else min(total, max_pages)

    parts: list[str] = []
    used_chars = 0
    truncated = False
    for i in range(limit):
        chunk = (reader.pages[i].extract_text() or "").strip()
        if not chunk:
            continue
        if max_chars is not None:
            remaining = max_chars - used_chars
            if remaining <= 0:
                truncated = True
                break
            if len(chunk) > remaining:
                chunk = chunk[:remaining]
                truncated = True
            used_chars += len(chunk)
        parts.append(f"### Page {i + 1}\n\n{chunk}")
        if truncated:
            break

    text = "\n\n".join(parts).strip()
    meta: dict[str, Any] = {
        "engine": "pypdf",
        "pages_total": total,
        "pages_scanned": limit,
        "truncated": truncated,
    }
    return text, meta


class _StripHTMLParser(HTMLParser):
    """Extract visible text; skip script/style/nav/footer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        elif tag in {"br", "p", "div", "li", "tr", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag in {"p", "div", "li", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return re.sub(r"[ \t]+", " ", raw).strip()


def html_to_text(html: str) -> str:
    """Convert HTML string to plain text (best-effort)."""
    parser = _StripHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.text()


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read .md, .txt, or decode as utf-8 with replacement."""
    p = Path(path)
    return p.read_text(encoding=encoding, errors="replace")


def read_html_file(path: str | Path) -> tuple[str, str]:
    """Return (raw_html, extracted_text)."""
    raw = read_text_file(path)
    return raw, html_to_text(raw)


def fetch_url(
    url: str,
    timeout: int = 30,
    max_bytes: int = 5_000_000,
) -> tuple[str, str, str]:
    """GET url; return (content_type, raw_text, extracted_text).

    For HTML, extracted_text is html_to_text; for other types, raw in both.
    """
    _reject_gamma_docs_url(url)
    headers = {
        "User-Agent": "course-DEV-IDE-with-AGENTS-source-wrangler/1.0",
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    raw_bytes = resp.content[:max_bytes]
    ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    charset = resp.encoding or "utf-8"
    raw_text = raw_bytes.decode(charset, errors="replace")
    if "html" in ctype:
        return ctype, raw_text, html_to_text(raw_text)
    return ctype, raw_text, raw_text.strip()


def list_box_files(
    box_root: str | Path,
    glob_pattern: str = "**/*",
    max_files: int = 50,
    extensions: frozenset[str] | None = None,
) -> list[Path]:
    """List files under BOX_DRIVE_PATH (bounded)."""
    root = Path(box_root)
    if not root.is_dir():
        raise FileNotFoundError(f"BOX_DRIVE_PATH is not a directory: {root}")
    exts = extensions or frozenset(
        {".md", ".txt", ".pdf", ".docx", ".html", ".htm"}
    )
    out: list[Path] = []
    for p in root.glob(glob_pattern):
        if len(out) >= max_files:
            break
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p)
    return sorted(out)


@dataclass
class SourceRecord:
    """One provenance entry."""

    kind: str
    ref: str
    note: str = ""
    fetched_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "ref": self.ref,
            "note": self.note,
            "fetched_at": self.fetched_at,
        }


def wrangle_local_pdf(
    path: str | Path,
    *,
    max_pages: int | None = 120,
    max_chars: int | None = 600_000,
) -> tuple[str, str, SourceRecord]:
    """Read a local PDF; return (title_guess, extracted_text, provenance)."""
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"PDF not found: {p}")
    if p.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {p}")

    body, meta = extract_pdf_text(p, max_pages=max_pages, max_chars=max_chars)
    title = p.stem.replace("_", " ")
    note = (
        f"pypdf scanned={meta['pages_scanned']}/{meta['pages_total']}"
        f"{' truncated' if meta.get('truncated') else ''}"
    )
    rec = SourceRecord(kind="local_pdf", ref=str(p), note=note)
    return title, body, rec


# ---------------------------------------------------------------------------
# Story 27-1: DOCX provider wiring
#
# Mirrors wrangle_local_pdf signature. Uses body-order iteration over
# doc.element.body so tables and paragraphs interleave correctly in output
# (Murat's AC-T.1 iteration-order guard). Heading 1..6 styles render as
# markdown `#`..`######`. Tables render as pipe-separated rows. Known losses
# per transform-registry.md: style/formatting beyond headings, cell-merge /
# vertical-align on tables, inline images, footnotes, comments, tracked
# changes. Malformed DOCX raises python-docx's PackageNotFoundError which
# run_wrangler._wrangle_source() catches and maps to FAILED SourceOutcome
# with error_kind="docx_extraction_failed" (AC-B.3 / AC-T.2b).
# ---------------------------------------------------------------------------


_HEADING_STYLE_RE = re.compile(r"^Heading (\d+)$")


def extract_docx_text(
    path: str | Path,
    *,
    max_chars: int | None = 600_000,
) -> tuple[str, dict[str, Any]]:
    """Extract markdown body + structural counts from a DOCX via python-docx.

    Returns (body, meta). meta keys: paragraphs, headings, tables, truncated.

    Body-order iteration walks doc.element.body so tables appear inline at
    their document position instead of clustered. Each rendered block
    (heading / paragraph / table) is separated by a blank line so the
    output matches markdown paragraph convention (which extraction_validator
    _assess_structural_fidelity relies on via `\\n\\n` detection).
    Heading-styled paragraphs (style name "Heading 1".."Heading 6") render
    as markdown `#`..`######`. Tables render as `| cell | cell |` rows,
    one line per row. Character budget (`max_chars`) truncates at item
    boundaries; the trailing `[...truncated]` marker is appended when the
    cap fires.

    Raises docx.opc.exceptions.PackageNotFoundError on malformed-ZIP / non-DOCX
    input — caller is responsible for catching + FAILED-outcome synthesis
    (run_wrangler._wrangle_source handles this).
    """
    doc = _DocxDocument(str(path))
    blocks: list[str] = []  # Each element is a rendered block; joined with "\n\n".
    counts = {"paragraphs": 0, "headings": 0, "tables": 0}
    truncated = False
    running_chars = 0
    # Note: doc.element.body + python-docx qname constants are community-
    # canonical workarounds for python-docx's split paragraphs/tables
    # surfaces (the library's public API exposes these as two flat
    # collections, which would lose body-order). Validated against
    # python-docx 1.1-1.2; the `<2` upper pin in pyproject guards against
    # an unannounced 2.x rename of these internals.
    p_tag = _docx_qn("w:p")
    tbl_tag = _docx_qn("w:tbl")

    def _append_block(block: str) -> bool:
        """Append block respecting max_chars; return False when truncated."""
        nonlocal running_chars
        add_len = len(block) + 2  # account for "\n\n" separator
        if max_chars is not None and running_chars + add_len > max_chars:
            return False
        blocks.append(block)
        running_chars += add_len
        return True

    for child in doc.element.body.iterchildren():
        tag = child.tag
        if tag == p_tag:
            para = _DocxParagraph(child, doc)
            text = (para.text or "").rstrip()
            style_name = para.style.name if para.style is not None else ""
            m = _HEADING_STYLE_RE.match(style_name or "")
            # Counter semantics (code-review Blind+Auditor, 2026-04-17): count
            # only content that is actually rendered to the body, so rec.note
            # counts match what a reader of extracted.md sees — not the raw
            # python-docx element count (which inflates on layout-spacer
            # empty paragraphs and would-be-empty headings).
            if m:
                if not text:
                    continue  # empty heading — skip, do not count
                level = min(int(m.group(1)), 6)
                rendered = f"{'#' * level} {text}".rstrip()
                counts["headings"] += 1
                counts["paragraphs"] += 1
                if not _append_block(rendered):
                    truncated = True
                    break
            else:
                if not text:
                    continue  # empty paragraph (layout spacer) — skip, do not count
                counts["paragraphs"] += 1
                if not _append_block(text):
                    truncated = True
                    break
        elif tag == tbl_tag:
            table = _DocxTable(child, doc)
            counts["tables"] += 1
            table_rows: list[str] = []
            for row in table.rows:
                # De-duplicate consecutive _tc references per row: python-docx's
                # row.cells returns the SAME _Cell object for each logical grid
                # position a horizontally-merged cell spans, producing duplicate
                # text in pipe-rows (code-review Blind+Edge Hunter, 2026-04-17).
                # Track the underlying <w:tc> element identity to render each
                # physical cell exactly once.
                unique_cells: list[str] = []
                seen_tc_ids: set[int] = set()
                for cell in row.cells:
                    tc_id = id(cell._tc)
                    if tc_id in seen_tc_ids:
                        continue
                    seen_tc_ids.add(tc_id)
                    unique_cells.append(cell.text.replace("\n", " ").strip())
                table_rows.append("| " + " | ".join(unique_cells) + " |")
            rendered = "\n".join(table_rows)
            if not _append_block(rendered):
                truncated = True
                break

    body = "\n\n".join(blocks).strip()
    if body:
        body = body + "\n"
    if truncated:
        body = (body + "[...truncated]\n") if body else "[...truncated]\n"

    meta: dict[str, Any] = {**counts, "truncated": truncated}
    return body, meta


def wrangle_local_docx(
    path: str | Path,
    *,
    max_chars: int | None = 600_000,
) -> tuple[str, str, SourceRecord]:
    """Read a local DOCX; return (title_guess, extracted_text, provenance).

    Signature + return shape mirror wrangle_local_pdf. Title derives from
    Path(path).stem with underscores → spaces (Winston's PDF-parity note).
    `rec.kind == "local_docx"` (distinct from "local_file" for .md/.txt
    text reads). `rec.note` reports paragraph/heading/table counts.

    Raises FileNotFoundError if path is missing; ValueError on wrong suffix;
    python-docx PackageNotFoundError on malformed-ZIP / invalid-DOCX input
    (surfaces the library exception for adapter-layer classification —
    AC-B.3 / AC-T.2a).
    """
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"DOCX not found: {p}")
    if p.suffix.lower() != ".docx":
        raise ValueError(f"Expected a .docx file, got: {p}")

    body, meta = extract_docx_text(p, max_chars=max_chars)
    title = p.stem.replace("_", " ")
    note_parts = [
        f"python-docx paragraphs={meta['paragraphs']}",
        f"headings={meta['headings']}",
        f"tables={meta['tables']}",
    ]
    if meta.get("truncated"):
        note_parts.append("truncated")
    note = " ".join(note_parts)
    rec = SourceRecord(kind="local_docx", ref=str(p), note=note)
    return title, body, rec


# ---------------------------------------------------------------------------
# Local Markdown provider wiring
#
# Signature mirrors wrangle_local_pdf / wrangle_local_docx so the runner's
# suffix-branch in _fetch_source can route .md files through here without
# any structural reshape. Normalization (backslash-unescape, HTML entity
# decode, blank-line collapse) is delegated to source_ops/normalize_notion_md
# which is loaded lazily because the parent directory contains a hyphen and
# cannot be imported via standard ``from ... import`` syntax.
# ---------------------------------------------------------------------------


def _load_notion_md_normalizer() -> Any:
    """Lazy-load the source_ops.normalize_notion_md module.

    Uses the same ``importlib.util.spec_from_file_location`` pattern the
    runner relies on for hyphenated-parent-directory imports.
    """
    import importlib.util

    module_path = Path(__file__).resolve().parent / "source_ops" / "normalize_notion_md.py"
    spec = importlib.util.spec_from_file_location(
        "texas_normalize_notion_md", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load normalize_notion_md from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wrangle_local_md(path: str | Path) -> tuple[str, str, SourceRecord]:
    """Read a local Markdown file and normalize Notion-export artefacts.

    Handles Notion's escaped-Markdown export format (``\\#`` → ``#``,
    ``&#x20;`` → space, triple-blank-line collapse). Falls through the
    same normalization path even for hand-authored Markdown — the
    operation is idempotent and never corrupts clean Markdown.

    Signature + return shape mirror :func:`wrangle_local_pdf` and
    :func:`wrangle_local_docx`. Title derives from ``Path(path).stem``
    with underscores replaced by spaces. ``rec.kind == "local_md"`` so
    provenance can distinguish a normalized Markdown read from the
    generic ``local_text_read`` fall-through.

    Raises:
        FileNotFoundError: if ``path`` is missing.
        ValueError: if ``path`` does not have a ``.md`` or ``.markdown``
            suffix (use :func:`read_text_file` for generic text files).
    """
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Markdown file not found: {p}")
    if p.suffix.lower() not in (".md", ".markdown"):
        raise ValueError(f"Expected a .md or .markdown file, got: {p}")

    raw = read_text_file(p)
    normalizer = _load_notion_md_normalizer()
    body = normalizer.normalize_notion_markdown(raw)

    title = p.stem.replace("_", " ")
    raw_lines = raw.count("\n")
    cleaned_lines = body.count("\n")
    escapes_removed = raw.count("\\") - body.count("\\")
    note_parts = [
        f"markdown normalize raw_lines={raw_lines}",
        f"cleaned_lines={cleaned_lines}",
        f"escapes_removed={max(escapes_removed, 0)}",
    ]
    note = " ".join(note_parts)
    rec = SourceRecord(kind="local_md", ref=str(p), note=note)
    return title, body, rec


def build_extracted_markdown(
    title: str,
    sections: list[tuple[str, str]],
) -> str:
    """sections: (heading, body_markdown_or_text)."""
    lines = [f"# Source bundle: {title}", ""]
    for head, body in sections:
        lines.append(f"## {head}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_source_bundle(
    output_dir: str | Path,
    title: str,
    extracted_md: str,
    provenance: list[SourceRecord],
    raw_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Write bundle to disk; return summary paths.

    raw_files: optional basename -> content to place under raw/
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_dir = out / "raw"
    if raw_files:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for name, content in raw_files.items():
            safe = Path(name).name
            (raw_dir / safe).write_text(content, encoding="utf-8")

    (out / "extracted.md").write_text(extracted_md, encoding="utf-8")
    meta = {
        "title": title,
        "generated_at": datetime.now(UTC).isoformat(),
        "provenance": [p.to_dict() for p in provenance],
        "primary_consumption_path": str(out / "extracted.md"),
    }
    (out / "metadata.json").write_text(
        json.dumps(meta, indent=2),
        encoding="utf-8",
    )
    return {
        "bundle_dir": str(out.resolve()),
        "extracted_md": str((out / "extracted.md").resolve()),
        "metadata_json": str((out / "metadata.json").resolve()),
    }


def wrangle_notion_page(
    page_id: str,
    client: NotionClient | None = None,
) -> tuple[str, str, str]:
    """Return (title, markdown_body, page_id) from Notion."""
    c = client or NotionClient()
    title, body = c.page_to_markdown(page_id)
    return title, body, page_id.strip()


# ---------------------------------------------------------------------------
# Box fetch-layer provider (Story 27-6)
#
# Box is a LOCATOR-SHAPE fetch layer — it resolves a Box file/folder/shared-link
# locator to a local file, then routes the local file through the existing
# format-specific extractors (wrangle_local_pdf, wrangle_local_docx,
# wrangle_local_md, read_text_file). Box itself is not a new extraction format;
# it is a fetch adapter that widens Texas's intake surface to Box-hosted
# content.
#
# Dependency injection: the BoxFetcher Protocol lets tests substitute a fake
# implementation without requiring `boxsdk` to be installed. The default
# production implementation is `BoxSDKFetcher` which imports `boxsdk` lazily.
#
# Auth model: developer token (env var `BOX_DEVELOPER_TOKEN`). OAuth2 refresh
# and JWT service-account auth are future work; the provider raises
# BoxAuthError with actionable remediation text when the token is missing,
# expired, or lacks permission for a requested item.
#
# LangGraph portability: no imports from marcus.orchestrator.* or
# marcus.dispatch.*; pure fetch → local-file → format-extractor pipeline.
# ---------------------------------------------------------------------------


class BoxError(Exception):
    """Base class for Box provider errors (auth, not-found, permission, rate)."""

    def __init__(self, message: str, *, remediation: str | None = None) -> None:
        super().__init__(message)
        self.remediation = remediation

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        if self.remediation:
            return f"{base}\n\n{self.remediation}"
        return base


class BoxAuthError(BoxError):
    """Raised on 401/403-class authentication failures.

    Carries operator-facing remediation text naming the config file, env var,
    and Box developer-console URL per Story 27-6 AC-1 (Sally UX rider).
    """


class BoxNotFoundError(BoxError):
    """Raised when a Box file/folder ID or shared link cannot be resolved."""


class BoxPermissionError(BoxError):
    """Raised on permission-denied for a resolvable-but-unauthorized item."""


class BoxRateLimitError(BoxError):
    """Raised when Box rate-limit exhausts the configured backoff budget."""


@dataclass(frozen=True)
class BoxFetchResult:
    """Metadata + local path for a Box item resolved to disk.

    `local_path` is a path under the caller-provided dest_dir where the file
    contents have been written. Box-specific provenance flows through the
    remaining fields and lands in `provider_metadata.box` downstream.
    """

    local_path: Path
    item_id: str
    item_name: str
    item_type: str  # "file" | "folder-child-file"
    size_bytes: int
    modified_at: str
    created_by: str
    parent_path: str


class BoxFetcher:
    """Protocol-style base class for Box-fetch implementations.

    Production: BoxSDKFetcher (wraps boxsdk). Tests: FakeBoxFetcher
    (substitutes pre-scripted results). Dependency injection keeps `boxsdk`
    out of the test import graph.
    """

    def fetch_file(self, locator: str, dest_dir: Path) -> BoxFetchResult:
        raise NotImplementedError

    def fetch_folder(
        self,
        locator: str,
        dest_dir: Path,
        *,
        max_depth: int = 3,
    ) -> list[BoxFetchResult]:
        raise NotImplementedError


_BOX_AUTH_REMEDIATION_TEMPLATE = (
    "Your Box developer token is missing, expired, or lacks permission for "
    "item '{locator}'.\n"
    "Remediation:\n"
    "  1. Open the Box Developer Console: "
    "https://app.box.com/developers/console\n"
    "  2. Select your application → Configuration → Developer Token.\n"
    "  3. Click 'Generate Developer Token' (tokens expire after 60 minutes).\n"
    "  4. Update the `BOX_DEVELOPER_TOKEN` environment variable (or "
    "`state/config/providers/box.yaml::developer_token`) with the new value.\n"
    "  5. Re-run the directive."
)


def _box_auth_remediation(locator: str) -> str:
    """Produce the operator-facing remediation string for a Box auth failure.

    Per Sally UX rider (Story 27-6): must name the file path to edit, the
    Box console URL, and the re-run step. Extracted as a pure function so
    tests can assert its stability without constructing a live error.
    """
    return _BOX_AUTH_REMEDIATION_TEMPLATE.format(locator=locator)


def _suffix_from_name(name: str) -> str:
    """Lowercased suffix helper (e.g., 'Report.PDF' -> '.pdf')."""
    return Path(name).suffix.lower()


def _extract_by_suffix(
    local_path: Path,
    display_name: str,
) -> tuple[str, str, SourceRecord]:
    """Route a Box-fetched local file through the format-appropriate extractor.

    Dispatch mirrors `run_wrangler._fetch_source` so Box inherits the same
    format routing rules (PDF, DOCX, MD, text). The caller-visible return
    shape matches the other wrangle_* functions: (title, body, SourceRecord).
    """
    suffix = _suffix_from_name(display_name)
    if suffix == ".pdf":
        return wrangle_local_pdf(local_path)
    if suffix == ".docx":
        return wrangle_local_docx(local_path)
    if suffix in (".md", ".markdown"):
        return wrangle_local_md(local_path)
    # Fall through: plain-text read.
    body = read_text_file(local_path)
    rec = SourceRecord(
        kind="local_file",
        ref=str(local_path.resolve()),
        note=f"box → local text read ({suffix or 'no-ext'})",
    )
    title = Path(display_name).stem.replace("_", " ")
    return title, body, rec


def wrangle_box_file(
    locator: str,
    *,
    fetcher: BoxFetcher | None = None,
    dest_dir: str | Path | None = None,
) -> tuple[str, str, SourceRecord]:
    """Fetch a single Box file by ID or shared link, then extract its contents.

    :param locator: Box file ID (numeric string) or shared-link URL.
    :param fetcher: BoxFetcher implementation; defaults to BoxSDKFetcher.
    :param dest_dir: Local directory for the downloaded file; defaults to
        the OS temp dir. Caller owns cleanup if a custom dest_dir is supplied.
    :returns: (title, extracted_text, SourceRecord) — identical contract to
        wrangle_local_pdf / wrangle_local_docx / wrangle_local_md so the
        runner's _fetch_source dispatch can route Box items through the
        same post-fetch pipeline.
    :raises BoxAuthError: Token missing/expired/insufficient.
    :raises BoxNotFoundError: Locator does not resolve.
    :raises BoxPermissionError: Locator resolves but access denied.
    :raises BoxRateLimitError: Backoff budget exhausted.
    """
    import tempfile

    f = fetcher if fetcher is not None else BoxSDKFetcher()
    target_dir = Path(dest_dir) if dest_dir is not None else Path(tempfile.gettempdir())
    target_dir.mkdir(parents=True, exist_ok=True)

    result = f.fetch_file(locator, target_dir)
    title, body, rec = _extract_by_suffix(result.local_path, result.item_name)
    # Enrich provenance with Box-specific metadata (flows into
    # provider_metadata.box downstream). Keep the wrangle-kind string
    # distinct so the lockstep contract test can recognize the Box path.
    enriched_note = (
        f"{rec.note} | box item_id={result.item_id} "
        f"item_type={result.item_type} size={result.size_bytes} "
        f"modified_at={result.modified_at} parent_path={result.parent_path}"
    )
    enriched = SourceRecord(
        kind="box_file",
        ref=f"box://{result.item_id}",
        note=enriched_note,
    )
    return title, body, enriched


def wrangle_box_folder(
    locator: str,
    *,
    fetcher: BoxFetcher | None = None,
    dest_dir: str | Path | None = None,
    max_depth: int = 3,
) -> list[tuple[str, str, SourceRecord]]:
    """Fetch every supported file under a Box folder, recursing to max_depth.

    Returns a list of (title, body, SourceRecord) tuples — one per fetched
    file. Unsupported suffixes within the folder are skipped with a
    SourceRecord note; fetch errors on individual children raise upward
    (callers decide per-source granularity).
    """
    import tempfile

    f = fetcher if fetcher is not None else BoxSDKFetcher()
    target_dir = Path(dest_dir) if dest_dir is not None else Path(tempfile.gettempdir())
    target_dir.mkdir(parents=True, exist_ok=True)

    fetched = f.fetch_folder(locator, target_dir, max_depth=max_depth)
    results: list[tuple[str, str, SourceRecord]] = []
    for item in fetched:
        title, body, rec = _extract_by_suffix(item.local_path, item.item_name)
        enriched_note = (
            f"{rec.note} | box item_id={item.item_id} "
            f"item_type={item.item_type} size={item.size_bytes} "
            f"modified_at={item.modified_at} parent_path={item.parent_path}"
        )
        enriched = SourceRecord(
            kind="box_file",
            ref=f"box://{item.item_id}",
            note=enriched_note,
        )
        results.append((title, body, enriched))
    return results


class BoxSDKFetcher(BoxFetcher):
    """boxsdk-backed fetcher (lazy import so the test suite doesn't require it).

    Auth: developer token from env var `BOX_DEVELOPER_TOKEN`. Raises
    BoxAuthError with operator-facing remediation text if the env var is
    missing at first use.
    """

    def __init__(self, *, developer_token: str | None = None) -> None:
        self._token = developer_token
        self._client: Any | None = None

    def _resolve_token(self, locator: str) -> str:
        import os

        token = self._token or os.environ.get("BOX_DEVELOPER_TOKEN")
        if not token:
            raise BoxAuthError(
                "BOX_DEVELOPER_TOKEN is not set.",
                remediation=_box_auth_remediation(locator),
            )
        return token

    def _get_client(self, locator: str) -> Any:
        if self._client is not None:
            return self._client
        token = self._resolve_token(locator)
        try:
            from boxsdk import Client, OAuth2  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - env-dependent
            raise BoxAuthError(
                "boxsdk is not installed.",
                remediation=(
                    "Install boxsdk: `pip install boxsdk`. Then ensure "
                    "`BOX_DEVELOPER_TOKEN` is set per the remediation for "
                    f"locator {locator!r}."
                ),
            ) from exc
        oauth = OAuth2(client_id=None, client_secret=None, access_token=token)
        self._client = Client(oauth)
        return self._client

    def fetch_file(self, locator: str, dest_dir: Path) -> BoxFetchResult:
        # This method is intentionally minimal — the test suite uses
        # FakeBoxFetcher to avoid depending on boxsdk. A live integration test
        # gated on BOX_DEVELOPER_TOKEN exercises this path.
        client = self._get_client(locator)
        file_id = self._resolve_file_id(client, locator)
        try:
            info = client.file(file_id).get()
        except Exception as exc:  # pragma: no cover - boxsdk error mapping
            raise _map_boxsdk_error(exc, locator) from exc
        local = dest_dir / info.name
        with open(local, "wb") as fp:
            client.file(file_id).download_to(fp)
        return BoxFetchResult(
            local_path=local,
            item_id=str(info.id),
            item_name=str(info.name),
            item_type="file",
            size_bytes=int(getattr(info, "size", 0) or 0),
            modified_at=str(getattr(info, "modified_at", "") or ""),
            created_by=str(
                getattr(getattr(info, "created_by", None), "login", "") or ""
            ),
            parent_path=str(getattr(getattr(info, "parent", None), "name", "") or ""),
        )

    def fetch_folder(
        self,
        locator: str,
        dest_dir: Path,
        *,
        max_depth: int = 3,
    ) -> list[BoxFetchResult]:  # pragma: no cover - exercised via FakeBoxFetcher
        raise NotImplementedError(
            "BoxSDKFetcher.fetch_folder is deferred to a follow-on story; "
            "file-level fetch is the v1 scope."
        )

    @staticmethod
    def _resolve_file_id(client: Any, locator: str) -> str:
        """Resolve a Box locator (file ID or shared link URL) to a file ID."""
        if locator.startswith(("http://", "https://")):
            try:
                item = client.get_shared_item(locator)
            except Exception as exc:  # pragma: no cover - boxsdk error mapping
                raise _map_boxsdk_error(exc, locator) from exc
            return str(item.id)
        # Assume numeric file ID.
        return locator.strip()


# ---------------------------------------------------------------------------
# Notion MCP fetch-layer provider (Story 27-5)
#
# Distinct from the legacy `notion` provider (which uses scripts/api_clients/
# notion_client.py against Notion's direct REST API). The MCP-mediated path
# leverages the harness-loaded MCP server so auth, rate-limiting, and block
# traversal are primitives provided by the server, not reimplemented here.
#
# Architecture (Winston green-light ruling): the Python adapter does NOT call
# MCP directly. The runtime harness (Marcus or test fixture) resolves the
# Notion page via the MCP call `mcp__claude_ai_Notion__notion-fetch` and
# provides the resulting markdown content to `wrangle_notion_mcp_page` via
# the NotionMCPFetcher Protocol. This keeps the Python runner free of
# MCP-transport concerns and preserves LangGraph portability.
#
# Scope binding (Amelia rider + user memory): Texas-headless runs MUST use
# the project-scope stdio Notion MCP (not the user-scope hosted one). The
# provider surfaces `scope` on NotionFetchResult so the scope can be
# asserted at the runner's dispatch boundary.
#
# Sally UX rider (non-negotiable): when a page is not shared with the
# project-scope Notion integration (the exact Tejal-trial 2026-04-17
# blocker), the provider raises NotionMCPPermissionError with remediation
# text that walks the operator through the Notion Connections UI in
# literal string form. The test suite asserts on verbatim substrings.
# ---------------------------------------------------------------------------


class NotionMCPError(Exception):
    """Base class for Notion MCP provider errors."""

    def __init__(self, message: str, *, remediation: str | None = None) -> None:
        super().__init__(message)
        self.remediation = remediation

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        if self.remediation:
            return f"{base}\n\n{self.remediation}"
        return base


class NotionMCPAuthError(NotionMCPError):
    """Raised when the Notion MCP integration token is missing/invalid."""


class NotionMCPNotFoundError(NotionMCPError):
    """Raised when a Notion page ID or URL cannot be resolved."""


class NotionMCPPermissionError(NotionMCPError):
    """Raised when the MCP integration is not granted access to a page.

    This is the Tejal-trial 2026-04-17 blocker. Remediation text MUST walk
    the operator through the Notion UI step by step — tested literally.
    """


@dataclass(frozen=True)
class NotionFetchResult:
    """Result of resolving a Notion page via MCP.

    `markdown_body` is the page content in Markdown form (the Notion MCP
    server's notion-fetch tool returns rich-text with block structure; the
    harness is responsible for converting to Markdown before handoff).
    `scope` is "project" for Texas-headless runs, "user" for Tracy-IDE runs.
    """

    page_id: str
    page_title: str
    markdown_body: str
    scope: str  # "project" | "user"
    last_edited_time: str
    last_edited_by: str
    parent_path: str


class NotionMCPFetcher:
    """Protocol-style base class for Notion MCP fetch implementations."""

    def fetch_page(self, page_locator: str) -> NotionFetchResult:
        raise NotImplementedError


def _notion_mcp_permission_remediation(
    page_title: str, page_id: str, integration_name: str = "[your project-scope integration]"
) -> str:
    """Produce the Tejal-trial remediation text for permission-denied.

    Extracted as a pure function so the test suite can assert the literal
    substrings without invoking the fetcher. Any edit to this template
    MUST be accompanied by a test update.
    """
    return (
        f"Notion page '{page_title}' ({page_id}) is not shared with the "
        f"project-scope Notion integration used by Texas-headless.\n"
        f"Remediation (in Notion UI):\n"
        f"  1. Open the page in Notion.\n"
        f"  2. Click the '...' menu in the top-right.\n"
        f"  3. Select 'Connections' → 'Add connections'.\n"
        f"  4. Select {integration_name}.\n"
        f"  5. Re-run the directive.\n"
        f"If you intended to use the user-scope integration (Tracy-IDE), "
        f"change the directive provider to 'notion' (legacy) or route "
        f"through the Tracy-IDE session."
    )


def wrangle_notion_mcp_page(
    page_locator: str,
    *,
    fetcher: NotionMCPFetcher,
    expected_scope: str = "project",
) -> tuple[str, str, SourceRecord]:
    """Fetch a Notion page via MCP and return (title, body, provenance).

    :param page_locator: Notion page ID or URL.
    :param fetcher: NotionMCPFetcher implementation (DI — no default).
    :param expected_scope: Must match `result.scope` or the fetcher's scope
        is rejected via NotionMCPAuthError (the scope-binding rider).
    :raises NotionMCPAuthError: Missing/invalid token OR scope mismatch.
    :raises NotionMCPPermissionError: Integration not granted for page.
    :raises NotionMCPNotFoundError: Page ID cannot be resolved.
    """
    result = fetcher.fetch_page(page_locator)
    if result.scope != expected_scope:
        raise NotionMCPAuthError(
            f"Notion MCP scope mismatch: expected {expected_scope!r}, got "
            f"{result.scope!r}. Texas-headless runs must use the project-"
            f"scope stdio Notion MCP (not the user-scope hosted one)."
        )
    note = (
        f"notion_mcp page_id={result.page_id} scope={result.scope} "
        f"last_edited_time={result.last_edited_time} "
        f"last_edited_by={result.last_edited_by} "
        f"parent_path={result.parent_path}"
    )
    rec = SourceRecord(
        kind="notion_mcp_page",
        ref=f"notion_mcp://{result.page_id}",
        note=note,
    )
    return result.page_title, result.markdown_body, rec


def _map_boxsdk_error(exc: Exception, locator: str) -> BoxError:
    """Translate a raw boxsdk exception into a typed Box* error.

    Falls back to BoxError for unmapped shapes. Status-code inspection is
    duck-typed so the test suite can exercise this without importing
    boxsdk.exception.
    """
    status = getattr(exc, "status", None)
    if status == 401 or status == 403:
        return BoxAuthError(
            f"Box authentication failed (status={status}) for {locator!r}.",
            remediation=_box_auth_remediation(locator),
        )
    if status == 404:
        return BoxNotFoundError(
            f"Box item not found for locator {locator!r} (status=404)."
        )
    if status == 429:
        return BoxRateLimitError(
            f"Box rate-limit exhausted for locator {locator!r} (status=429)."
        )
    return BoxError(f"Box fetch failed for {locator!r}: {exc!r}")


def wrangle_playwright_saved_html(
    html_path: str | Path,
    source_url: str | None = None,
) -> tuple[str, str, SourceRecord]:
    """Process HTML saved by Playwright MCP (or any save-as)."""
    raw, text = read_html_file(html_path)
    path = Path(html_path)
    ref = source_url or str(path.resolve())
    note = f"HTML capture file: {path.name}"
    rec = SourceRecord(kind="playwright_html", ref=ref, note=note)
    title = path.stem.replace("_", " ")
    return title, text, rec


def summarize_url_for_envelope(url: str) -> tuple[str, str, SourceRecord]:
    """Fetch URL and return title guess, extracted text, provenance."""
    parsed = urlparse(url)
    title = (parsed.netloc + parsed.path).strip("/") or url
    ctype, _raw, extracted = fetch_url(url)
    rec = SourceRecord(kind="url", ref=url, note=f"Content-Type: {ctype}")
    return title, extracted, rec
