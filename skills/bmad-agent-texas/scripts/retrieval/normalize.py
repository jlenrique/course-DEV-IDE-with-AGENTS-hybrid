"""Canonical `TexasRow` normalization helpers — Story 27-0.

Thin utilities for adapters that want to lift provider-specific dicts into
the canonical shape with uniform coercion + sensible defaults. Each adapter
is free to build `TexasRow` instances directly; these helpers exist to keep
common patterns (author-list coercion, metadata-passthrough) from being
reimplemented per provider.
"""

from collections.abc import Iterable
from typing import Any

from .contracts import SourceOrigin, TexasRow


def coerce_authors(raw: Any) -> list[str]:
    """Normalize provider author fields into `list[str]`.

    Accepts: string (split on common delimiters), list of strings, list of
    dicts with a `name` key, or None.
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        for sep in (";", " and ", ", "):
            if sep in raw:
                return [a.strip() for a in raw.split(sep) if a.strip()]
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, Iterable):
        out: list[str] = []
        for item in raw:
            if isinstance(item, str):
                if item.strip():
                    out.append(item.strip())
            elif isinstance(item, dict):
                name = (
                    item.get("name")
                    or item.get("full_name")
                    or item.get("author")
                    or item.get("authorName")  # scite live MCP shape
                )
                if isinstance(name, str) and name.strip():
                    out.append(name.strip())
        return out
    return []


def build_texas_row(
    *,
    source_id: str,
    provider: str,
    title: str = "",
    body: str = "",
    authors: Any = None,
    date: str | None = None,
    source_origin: SourceOrigin = "operator-named",
    tracy_row_ref: str | None = None,
    authority_tier: str | None = None,
    provider_metadata: dict[str, Any] | None = None,
    completeness_ratio: float | None = None,
    structural_fidelity: float | None = None,
) -> TexasRow:
    """Build a canonical `TexasRow` from provider-shaped inputs.

    Equivalent to calling `TexasRow(...)` directly but applies the standard
    author-coercion + metadata-passthrough so adapters share one lift path.
    """
    return TexasRow(
        source_id=source_id,
        provider=provider,
        title=title,
        body=body,
        authors=coerce_authors(authors),
        date=date,
        source_origin=source_origin,
        tracy_row_ref=tracy_row_ref,
        authority_tier=authority_tier,
        provider_metadata=dict(provider_metadata or {}),
        completeness_ratio=completeness_ratio,
        structural_fidelity=structural_fidelity,
    )


__all__ = [
    "build_texas_row",
    "coerce_authors",
]
