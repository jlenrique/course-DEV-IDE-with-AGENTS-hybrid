"""Unit-tier pin for the LangSmith span-tag contract (Story 1.1c, AC-1.1c-D2).

Fast-fails on drift without requiring ``LANGSMITH_API_KEY``. The integration-tier
counterpart (`tests/integration/observability/test_langsmith_span_tags.py`)
asserts the same keys are actually present on emitted spans.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.runtime.span_tags import REQUIRED_SPAN_TAG_KEYS

_GOLDEN_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "observability" / "span_tag_keys.json"
)


_CANONICAL_FOUR: frozenset[str] = frozenset({"trial_id", "node_id", "agent", "lane"})


def test_required_span_tag_keys_match_canonical_four() -> None:
    """The pinned set must equal exactly the four canonical contract keys."""
    assert _CANONICAL_FOUR == REQUIRED_SPAN_TAG_KEYS, (
        f"span-tag contract drift: got {sorted(REQUIRED_SPAN_TAG_KEYS)}; "
        "expected ['agent', 'lane', 'node_id', 'trial_id']."
    )


def test_required_span_tag_keys_match_golden_fixture() -> None:
    """Sorted constant must match the alphabetized golden fixture byte-for-byte."""
    fixture_keys = json.loads(_GOLDEN_FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture_keys == sorted(REQUIRED_SPAN_TAG_KEYS), (
        f"golden fixture drift: fixture={fixture_keys}; "
        f"sorted-constant={sorted(REQUIRED_SPAN_TAG_KEYS)}."
    )
