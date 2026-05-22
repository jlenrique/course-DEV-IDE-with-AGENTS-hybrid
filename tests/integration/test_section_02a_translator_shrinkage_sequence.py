"""Translator-shrinkage sequence test for Story 34-5.

Asserts the Quinn-synthesis Option 5 monotonic-shrinkage property of the
Section 02A to wrangler translator scaffold. The translator's
TRANSLATOR_ACTIVE_MAPPINGS frozenset shrinks across Epic 34 stories:

  Story 34-1 close: {src-id-to-ref-id, role-supporting-to-supplementary, filter-ignored-rows}
  Story 34-2 close: {src-id-to-ref-id}
  Story 34-3 close: frozenset()
  Story 34-4 close: frozenset()
  Story 34-5 close: frozenset()
  Story 34-6 close: frozenset()
  Story 34-7 close: translator file deleted entirely

This test is the forensic ratchet: if a future story accidentally adds back a
mapping through typo, drift, or scope creep, this test fails loudly.
"""

from __future__ import annotations

import inspect

from app.composers.section_02a._wrangler_translator import (
    TRANSLATOR_ACTIVE_MAPPINGS,
    translate_directive_for_wrangler,
)

_RECOGNIZED_MAPPING_NAMES: frozenset[str] = frozenset(
    {
        "src-id-to-ref-id",
        "role-supporting-to-supplementary",
        "filter-ignored-rows",
    }
)


def test_translator_active_mappings_is_empty_at_story_34_5_close() -> None:
    """AC-34-5-A: all historical mappings are retired at Story 34-5 close."""
    assert frozenset() == TRANSLATOR_ACTIVE_MAPPINGS, (
        f"TRANSLATOR_ACTIVE_MAPPINGS expected to be empty at Story 34-5 close, "
        f"got {TRANSLATOR_ACTIVE_MAPPINGS!r}. Predecessor Story 34-2 or 34-3 "
        f"may have missed its shrinkage AC; investigate."
    )


def test_translator_active_mappings_constant_is_production_load_bearing() -> None:
    """AC-34-5-A: the mapping constant is read by the runtime translator."""
    source = inspect.getsource(translate_directive_for_wrangler)
    assert "TRANSLATOR_ACTIVE_MAPPINGS" in source, (
        "translate_directive_for_wrangler does not reference "
        "TRANSLATOR_ACTIVE_MAPPINGS at runtime. Per Murat new-A9-surface-2 "
        "mitigation and AC-34-5-A, the constant must be production-load-bearing."
    )


def test_translator_active_mappings_contains_only_recognized_keys() -> None:
    """AC-34-5-A sibling assertion: mapping names stay in the closed set."""
    unrecognized = TRANSLATOR_ACTIVE_MAPPINGS - _RECOGNIZED_MAPPING_NAMES
    assert not unrecognized, (
        f"TRANSLATOR_ACTIVE_MAPPINGS contains unrecognized mapping names: "
        f"{unrecognized!r}. Recognized set: {sorted(_RECOGNIZED_MAPPING_NAMES)}. "
        f"If adding a new mapping, update _RECOGNIZED_MAPPING_NAMES in lockstep "
        f"and add a corresponding test."
    )
