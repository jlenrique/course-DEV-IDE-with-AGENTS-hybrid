"""Per-component universal-md record builder (DD5 / DD6).

Builds the lossless, provenance-anchored universal-md record for one typed
component: a deterministic front matter (via
:func:`universal_markdown_preamble.emit_front_matter`) plus a demarcated body
(``<<<CLEAN_BODY>>>`` + ``<<<PROVENANCE_ANNOTATION>>>``). NO paraphrase.

A4 RED (DD6, HARD): at ``content_fingerprint`` freeze the verbatim excerpt MUST
be a markdown-normalized substring of its parent source, else the record's
``resolution_status`` is ``ungrounded`` — never a silent sha over un-grounded
text. The normalizer is INJECTED (reuse of the canonical
``g0_enrichment_wiring._normalize_for_groundedness``) so this Texas-side module
needs no back-arrow import into ``app.marcus``.

DEPENDENCY DIRECTION (DD2): no ``app.marcus`` import. ``content_fingerprint``
uses ``hashlib.sha256`` directly — the SAME algorithm as
``g0_enrichment.file_content_hash`` / ``corpus_fingerprint`` (DRY by shared
algorithm, not by a cross-arrow import of a Path-taking helper).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from typing import Any

from .universal_markdown_preamble import (
    CLEAN_BODY_MARKER,
    PROVENANCE_ANNOTATION_MARKER,
    emit_front_matter,
)

NORMALIZATION_VERSION = "tex-norm-v1"


def content_fingerprint(text: str) -> str:
    """sha256 hex of a UTF-8 text span (same primitive as g0 ``file_content_hash``)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_excerpt_grounded(
    excerpt: str,
    source_text: str,
    normalize_fn: Callable[[str], str],
) -> bool:
    """True iff ``excerpt`` is a substring of ``source_text`` after normalization.

    Both sides pass through the INJECTED ``normalize_fn`` (the canonical
    ``_normalize_for_groundedness``: blockquote-strip + ``\\$``->``$`` unescape +
    whitespace-collapse). An excerpt that normalizes to empty is grounded
    (nothing to ground). Scope is excerpt-vs-source ONLY (DD6) — never
    resolved-metadata-vs-source.
    """
    norm_excerpt = normalize_fn(excerpt)
    if not norm_excerpt:
        return True
    return norm_excerpt in normalize_fn(source_text)


def build_component_record(
    *,
    component_id: str,
    component_type: str,
    locator: str,
    verbatim_excerpt: str,
    source_ref: dict[str, Any] | None,
    extraction_provenance: dict[str, Any] | None,
    doc_ordinal: int,
    source_text: str | None,
    normalize_fn: Callable[[str], str] | None = None,
    part: str | None = None,
    resolved_ref: dict[str, Any] | None = None,
    resolution_status: str | None = None,
) -> dict[str, Any]:
    """Build a universal-md record (front-matter ``fields`` + demarcated ``body``).

    Returns a dict with:
      - ``fields``: the front-matter dict (DD5 key set) — feed to
        :func:`emit_front_matter`;
      - ``body``: the demarcated ``<<<CLEAN_BODY>>>`` + ``<<<PROVENANCE_ANNOTATION>>>``
        spans (verbatim; NO paraphrase);
      - ``markdown``: the full record (front matter + body);
      - ``grounded``: whether the A4 check passed (False -> resolution_status forced
        ``ungrounded``).

    ``resolution_status`` precedence: an A4 groundedness FAILURE forces
    ``ungrounded`` (DD6 hard rule) regardless of any caller-supplied citation
    status; otherwise the caller's ``resolution_status`` (e.g. the
    ``CitationResolution`` verdict) is used, defaulting to ``resolved`` when the
    excerpt is grounded and no citation verdict applies.
    """
    grounded = True
    if normalize_fn is not None and source_text is not None:
        grounded = is_excerpt_grounded(verbatim_excerpt, source_text, normalize_fn)

    if not grounded:
        effective_status = "ungrounded"
    elif resolution_status is not None:
        effective_status = resolution_status
    else:
        effective_status = "resolved"

    fields: dict[str, Any] = {
        "component_id": component_id,
        "type": component_type,
        "part": part,
        "locator": locator,
        "source_ref": source_ref,
        "verbatim_excerpt": verbatim_excerpt,
        "content_fingerprint": content_fingerprint(verbatim_excerpt),
        "extraction_provenance": extraction_provenance,
        "resolution_status": effective_status,
        "resolved_ref": resolved_ref,
        "normalization_version": NORMALIZATION_VERSION,
        "doc_ordinal": doc_ordinal,
    }

    provenance_note = _provenance_annotation(
        locator=locator,
        source_ref=source_ref,
        extraction_provenance=extraction_provenance,
        grounded=grounded,
        resolution_status=effective_status,
    )
    body = (
        f"{CLEAN_BODY_MARKER}\n{verbatim_excerpt}\n"
        f"{PROVENANCE_ANNOTATION_MARKER}\n{provenance_note}\n"
    )
    front_matter = emit_front_matter(fields)
    return {
        "fields": fields,
        "body": body,
        "markdown": front_matter + body,
        "grounded": grounded,
    }


def _provenance_annotation(
    *,
    locator: str,
    source_ref: dict[str, Any] | None,
    extraction_provenance: dict[str, Any] | None,
    grounded: bool,
    resolution_status: str,
) -> str:
    """Human-readable provenance note (Irene #5). Verbatim facts only, no paraphrase."""
    lines = [
        f"locator: {locator}",
        f"grounded: {grounded}",
        f"resolution_status: {resolution_status}",
    ]
    if source_ref:
        lines.append(f"source_ref: {source_ref}")
    if extraction_provenance:
        lines.append(f"extraction_provenance: {extraction_provenance}")
    return "\n".join(lines)


__all__ = [
    "NORMALIZATION_VERSION",
    "build_component_record",
    "content_fingerprint",
    "is_excerpt_grounded",
]
