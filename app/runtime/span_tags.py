"""LangSmith span-tag contract pin (Slab 1 Story 1.1c, AC-1.1c-D2).

Per architecture §8 span-tag contract + FR7, every LangSmith span emitted by
the migration runtime must carry these four tag keys exactly. Re-exported as
a frozenset so any future drift fails loudly at unit-tier (no LangSmith API
key required) AND at integration-tier (AC-1.1c-D, asserts the tags are
actually present in the LangSmith export).

Adding or removing a tag here is a downstream-breaking schema change; do it
via party-mode amendment, not a quiet edit.
"""

from __future__ import annotations

REQUIRED_SPAN_TAG_KEYS: frozenset[str] = frozenset({"trial_id", "node_id", "agent", "lane"})

__all__ = ["REQUIRED_SPAN_TAG_KEYS"]
