# Migration Story 34-5: Translator-Shrinkage Sequence Test (Carrier Story; Murat new-A9-surface-2 mitigation)

**Status:** ready-for-dev *(spec authored 2026-05-22; predecessor Stories 34-1 through 34-4 expected `done` at dispatch.)*
**Sprint key:** `migration-34-5-translator-shrinkage-sequence-test`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence
**Pts:** 3
**Gate:** **single-gate** (carrier story; test-only; no production code; backed by Story 34-1's ratchet)
**K-target:** ~1.5× (3 pts; bounded surface = 1 new test file with 3 tests)
**R-tier:** **R1**
**T11-tier:** standard
**Files touched (substrate-verified 2026-05-22):**

**New (1 file):**
- `tests/integration/test_section_02a_translator_shrinkage_sequence.py` (NEW; lives next to Story 34-1's `test_section_02a_to_wrangler_subprocess_roundtrip.py`; pre-allowlisted at C1)

**Do NOT modify:**
- `app/composers/section_02a/_wrangler_translator.py` — Story 34-5 is test-only; no production code change. Translator state at dispatch time should be EMPTY frozenset (Stories 34-2 + 34-3 retired all 3 mappings before this story).
- Story 34-1 integration test (separate concern; THIS story is a carrier).

**Lookahead tier:** **1** (focused; test-only).
**Wave:** 1 — slot 5 (carrier story after substrate harmonization Stories 34-1..34-4).

**FR coverage:** n/a (carrier; no FR).
**NFR coverage:** NFR-E34-1 (integration coverage), NFR-E34-10 (Story 34-7 deletes translator; THIS story verifies the constant reaches frozenset() empty before Story 34-7's deletion gate fires), NFR-E34-11..13.

**Contract Decisions (LOCKED 2026-05-22 — SUBSTRATE-VERIFIED):**

**D1. Test file location and shape (carrier discipline):**

`tests/integration/test_section_02a_translator_shrinkage_sequence.py` — pre-allowlisted at C1. No `__init__.py` package marker needed (Codex Story 34-1 T10 note: pytest collection works without it).

**D2. Expected `TRANSLATOR_ACTIVE_MAPPINGS` state at Story 34-5 dispatch (substrate-verified):**

Given the Quinn-synthesis Option 5 sequence:
- Story 34-1 creates translator with `frozenset({"src-id-to-ref-id", "role-supporting-to-supplementary", "filter-ignored-rows"})` (3 mappings; verified at `app/composers/section_02a/_wrangler_translator.py:27-33`)
- Story 34-2 removes `role-supporting-to-supplementary` + `filter-ignored-rows` (wrangler natively accepts both post-34-2) → frozenset reduces to `{"src-id-to-ref-id"}` (1 mapping)
- Story 34-3 removes `src-id-to-ref-id` (§02A natively emits `ref_id` post-34-3) → frozenset reduces to `frozenset()` (empty)
- Story 34-4 does NOT touch translator (metadata-writer change is wrangler-OUTPUT, not translator-INPUT)

**Expected state at Story 34-5 dispatch: `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` (empty).**

If state is NOT empty at dispatch, that means Story 34-2 OR Story 34-3 left a mapping behind — surface as HALT-AND-SURFACE; do NOT proceed; investigate which prior story missed its shrinkage AC.

**D3. Three tests to author (AC-34-5-A BINDING):**

```python
"""Translator-shrinkage sequence test (Story 34-5 carrier).

Asserts the Quinn-synthesis Option 5 monotonic-shrinkage property of the
§02A → wrangler translator scaffold. The translator's TRANSLATOR_ACTIVE_MAPPINGS
frozenset shrinks across Epic 34 stories:

  Story 34-1 close: {src-id-to-ref-id, role-supporting-to-supplementary, filter-ignored-rows}
  Story 34-2 close: {src-id-to-ref-id} (role-supporting + filter-ignored retired)
  Story 34-3 close: frozenset() (src-id-to-ref-id retired)
  Story 34-4 close: frozenset() (Story 34-4 doesn't touch translator)
  Story 34-5 close: frozenset() (THIS story; carrier test ratchet)
  Story 34-6 close: frozenset() (Story 34-6 deletes legacy directive_composer.py; doesn't touch translator)
  Story 34-7 close: translator file DELETED entirely (NFR-E34-10 hard AC; AC-34-7-A/B/H)

This test is the forensic ratchet — if a future Story accidentally adds back
a mapping (typo, drift, scope creep), this test fails loudly.
"""

import inspect

from app.composers.section_02a._wrangler_translator import (
    TRANSLATOR_ACTIVE_MAPPINGS,
    translate_directive_for_wrangler,
)

# Closed set of recognized mapping names. Catches typos + unrecognized keys.
_RECOGNIZED_MAPPING_NAMES: frozenset[str] = frozenset({
    "src-id-to-ref-id",
    "role-supporting-to-supplementary",
    "filter-ignored-rows",
})


def test_translator_active_mappings_is_empty_at_story_34_5_close() -> None:
    """AC-34-5-A BINDING: at Story 34-5 close, all 3 historical mappings have
    been retired by predecessor stories (34-2 retired 2; 34-3 retired the
    final 1). Translator function still exists (deleted at Story 34-7); but
    its active mappings set is empty — calling it is a no-op pass-through.
    """
    assert TRANSLATOR_ACTIVE_MAPPINGS == frozenset(), (
        f"TRANSLATOR_ACTIVE_MAPPINGS expected to be empty at Story 34-5 close, "
        f"got {TRANSLATOR_ACTIVE_MAPPINGS!r}. Predecessor Story 34-2 or 34-3 "
        f"may have missed its shrinkage AC; investigate."
    )


def test_translator_active_mappings_constant_is_production_load_bearing() -> None:
    """AC-34-5-A BINDING (Murat new-A9-surface-2 mitigation): the constant
    MUST be READ by `translate_directive_for_wrangler` at runtime — not just
    declared at module-top. This prevents a vacuous-shrinkage-test surface
    where the constant could be set to empty without any production-behavior
    change.
    """
    source = inspect.getsource(translate_directive_for_wrangler)
    # The constant MUST be referenced at least once per mapping check.
    # Story 34-1's implementation has 3 references (one per mapping branch);
    # post-Story-34-2 + 34-3, references may remain even though set is empty
    # (the branches still gate on membership; just nothing in the set to match).
    assert "TRANSLATOR_ACTIVE_MAPPINGS" in source, (
        "translate_directive_for_wrangler does NOT reference "
        "TRANSLATOR_ACTIVE_MAPPINGS at runtime. Per Murat new-A9-surface-2 "
        "mitigation + AC-34-5-A, the constant MUST be production-load-bearing "
        "(not just test-observable)."
    )


def test_translator_active_mappings_contains_only_recognized_keys() -> None:
    """AC-34-5-A sibling assertion: every element in TRANSLATOR_ACTIVE_MAPPINGS
    MUST be in the closed set of recognized mapping names. Catches typos
    + unrecognized future additions that drift the contract.
    """
    unrecognized = TRANSLATOR_ACTIVE_MAPPINGS - _RECOGNIZED_MAPPING_NAMES
    assert not unrecognized, (
        f"TRANSLATOR_ACTIVE_MAPPINGS contains unrecognized mapping names: "
        f"{unrecognized!r}. Recognized set: {sorted(_RECOGNIZED_MAPPING_NAMES)}. "
        f"If you're adding a new mapping, update _RECOGNIZED_MAPPING_NAMES in "
        f"lockstep + add a corresponding test."
    )
```

**D4. Carrier-story discipline (AC-34-5-C BINDING):**

- Story 34-5 SHALL NOT modify production code. Translator file (`app/composers/section_02a/_wrangler_translator.py`) is READ ONLY at this story.
- Every AC is dev-agent-verifiable (`pytest exit 0`; no live-service evidence; sandbox-AC validator PASS).
- T11 review is standard (NOT cross-agent; the carrier discipline + load-bearing-constant verification is straightforward against the substrate).

**D5. Story 34-1 ratchet preservation (AC-34-5-B BINDING):**

Story 34-1's `test_section_02a_to_wrangler_subprocess_roundtrip.py::test_forensic_directive_round_trips_through_wrangler_subprocess_via_translator` MUST stay GREEN after Story 34-5 lands. Story 34-5 adds a NEW test file; should not break the existing test.

---

## Task chain T1-T11

**T1 readiness check:**
- C1 + Stories 34-1 + 34-2 + 34-3 + 34-4 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS.
- Verify `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` at dispatch time (HALT-AND-SURFACE if not empty — predecessor missed an AC).
- Verify translator file still exists at `app/composers/section_02a/_wrangler_translator.py` (will be deleted at Story 34-7, NOT Story 34-5).

**T2 test author:** D3 implementation literal — 3 tests as shown.

**T3 ruff + focused suite + Story-34-1 ratchet check.**

**T4 broad regression sweep.**

**T5-T9 standard pattern (self-G6 + ready-for-review).**

**T10 Claude T11 standard review + commit + flip done.**

---

## Acceptance Criteria

**AC-34-5-A** (parametrized translator-state test + production-load-bearing constant): D2 + D3 BINDING.

**AC-34-5-B** (Story-34-1 ratchet preserved): D5 BINDING.

**AC-34-5-C** (carrier story discipline): D4 BINDING.

## Cross-references

- Epic 34 §"Story 34-5"
- Story 34-1 spec (translator scaffold)
- Story 34-7 spec (translator deletion gate; AC-34-7-A/B/H grep-sweep target)
- `app/composers/section_02a/_wrangler_translator.py` (the substrate under test)
