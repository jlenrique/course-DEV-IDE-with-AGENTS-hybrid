"""Shared universal-md front-matter writer (DD2 / DD5).

A SLIM, EXPORTED front-matter contract consumed by BOTH ``run_wrangler`` and the
P5 workbook producer so there is ONE front-matter shape for the whole arc. The
public surface is :func:`emit_front_matter` (fields dict -> markdown string) with
a paired :func:`parse_front_matter` so the contract is round-trippable.

DD5 field order (deterministic): ``component_id, type, part, locator,
source_ref, verbatim_excerpt, content_fingerprint, extraction_provenance,
resolution_status, resolved_ref, normalization_version, doc_ordinal,
provisional_los``. ``provisional_los`` (the P1 provisional LO id list) is appended
LAST so the established order is undisturbed; it is the one key that defaults to an
EMPTY LIST (not ``null``) when absent, so P3 can validate ``lo_refs ⊆
provisional_los`` without a null-guard.

The body of a universal-md record (built by :mod:`universal_md`) carries two
DEMARCATED spans appended AFTER the front matter:
  - ``<<<CLEAN_BODY>>>`` — the markdown-normalized verbatim span P3/P5 consume;
  - ``<<<PROVENANCE_ANNOTATION>>>`` — the human-readable provenance note (Irene #5).
NO paraphrase ever enters either span.
"""

from __future__ import annotations

from typing import Any

import yaml

# DD5 — canonical front-matter key order (a list, not a set, so emission is
# byte-deterministic). ``emit_front_matter`` writes exactly these keys in this
# order; a field absent from ``fields`` is emitted as ``null`` so the shape is
# stable for every component (P5 consumers can rely on every key being present).
FRONT_MATTER_KEYS: tuple[str, ...] = (
    "component_id",
    "type",
    "part",
    "locator",
    "source_ref",
    "verbatim_excerpt",
    "content_fingerprint",
    "extraction_provenance",
    "resolution_status",
    "resolved_ref",
    "normalization_version",
    "doc_ordinal",
    "provisional_los",
)

# Keys whose ABSENT default is an empty list (not ``null``). ``provisional_los``
# is a passthrough list of P1 provisional LO ids; P3 validates ``lo_refs ⊆
# provisional_los`` and an empty-list default removes a null-guard from that check.
_LIST_DEFAULT_KEYS: frozenset[str] = frozenset({"provisional_los"})

FRONT_MATTER_FENCE = "---"

# Body demarcation tokens (DD5). Kept as module constants so the workbook producer
# and run_wrangler split on the SAME literals.
CLEAN_BODY_MARKER = "<<<CLEAN_BODY>>>"
PROVENANCE_ANNOTATION_MARKER = "<<<PROVENANCE_ANNOTATION>>>"


def emit_front_matter(fields: dict[str, Any]) -> str:
    """Render ``fields`` as a deterministic YAML front-matter block.

    Emits EVERY :data:`FRONT_MATTER_KEYS` key in declared order (missing keys ->
    ``null``) between two ``---`` fences. Deterministic: the same ``fields`` dict
    always yields byte-identical output (``sort_keys=False`` + fixed key order +
    ``allow_unicode``). Round-trippable via :func:`parse_front_matter`.

    Extra keys present in ``fields`` but NOT in :data:`FRONT_MATTER_KEYS` are
    rejected (closed front-matter contract — a silent typo'd key would drift the
    shape P5 depends on).
    """
    extra = set(fields) - set(FRONT_MATTER_KEYS)
    if extra:
        raise ValueError(
            f"emit_front_matter: unknown front-matter key(s) {sorted(extra)!r}; "
            f"the contract is closed to {list(FRONT_MATTER_KEYS)!r}"
        )
    ordered = {
        key: fields.get(key, [] if key in _LIST_DEFAULT_KEYS else None)
        for key in FRONT_MATTER_KEYS
    }
    body = yaml.safe_dump(
        ordered,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,  # never wrap a long verbatim excerpt mid-value
    )
    return f"{FRONT_MATTER_FENCE}\n{body}{FRONT_MATTER_FENCE}\n"


def parse_front_matter(text: str) -> dict[str, Any]:
    """Parse a front-matter block produced by :func:`emit_front_matter`.

    The inverse of :func:`emit_front_matter` (round-trip identity on the declared
    keys). Raises ``ValueError`` if the fences are missing.
    """
    stripped = text.lstrip()
    if not stripped.startswith(FRONT_MATTER_FENCE):
        raise ValueError("parse_front_matter: missing opening '---' fence")
    rest = stripped[len(FRONT_MATTER_FENCE):]
    end = rest.find(f"\n{FRONT_MATTER_FENCE}")
    if end == -1:
        raise ValueError("parse_front_matter: missing closing '---' fence")
    block = rest[:end]
    parsed = yaml.safe_load(block)
    return parsed if isinstance(parsed, dict) else {}


__all__ = [
    "CLEAN_BODY_MARKER",
    "FRONT_MATTER_FENCE",
    "FRONT_MATTER_KEYS",
    "PROVENANCE_ANNOTATION_MARKER",
    "emit_front_matter",
    "parse_front_matter",
]
