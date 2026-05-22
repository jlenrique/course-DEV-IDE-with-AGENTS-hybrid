# Codex dev-story prompt — Story 34-2 (Texas Wrangler 6-Role Union + excluded_reason + Cross-Field Invariants; Winston A1 binding)

**Cycle:** Claude spec (D1-D5 LOCKED 2026-05-22) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-2.ready-for-review.md` → **Claude T11 standard `bmad-code-review`** (NOT cross-agent — single-gate substrate edit with Story-34-1 ratchet underneath) → Claude commit + flip done.
**Wave:** 1 — slot 2 (substrate change; lands BEFORE Story 34-3 per Winston A3).
**Dispatch ordering:** **DISPATCH AFTER Story 34-1 CLOSES** (`migration-34-1-section-02a-wrangler-integration-roundtrip-test: done` in `sprint-status.yaml`).

---

```
Run bmad-dev-story on Story 34-2 (Epic 34 Wave 1; single-gate; standard T11; wrangler 6-role union + excluded_reason + cross-field invariants — Winston A1 binding).

## ⚠️ CONTRACT-LOCKED — D1-D5 ARE LOCKED.

Spec: `_bmad-output/implementation-artifacts/migration-34-2-wrangler-six-role-union-excluded-reason.md`

## Required reading (in order)

1. Story spec D1-D5 contract.
2. Story 34-1 spec — translator scaffold contract; you shrink its TRANSLATOR_ACTIVE_MAPPINGS at T4.
3. `app/composers/section_02a/directive_model.py:80-106` — §02A cross-field invariants you migrate to wrangler.
4. `skills/bmad-agent-texas/scripts/run_wrangler.py:280-394` — current wrangler validator; the edit target.
5. Epic 34 spec §"Story 34-2" — AC-34-2-A through AC-34-2-F.
6. Phase B consensus + Quinn synthesis (context: why this story exists).
7. C1 SCP allowlist — confirm your touched paths (run_wrangler.py + translator + new test file) are pre-allowlisted.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- C1 commit `3159a0e` is ancestor of HEAD.
- Story 34-1 = `done` in `sprint-status.yaml`.
- Story 34-1 round-trip test PASS on clean tree (verify via `pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v`).
- `_wrangler_translator.py::TRANSLATOR_ACTIVE_MAPPINGS` currently contains 3 elements (`src-id-to-ref-id`, `role-supporting-to-supplementary`, `filter-ignored-rows`); T4 reduces it to 1.

## Files in scope

**Modified:**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (D1/D2/D3/D4/D5 implementation)
- `app/composers/section_02a/_wrangler_translator.py` (T4 shrinkage)

**New:**
- `tests/specialists/texas/test_wrangler_role_enum_union_and_excluded_reason.py` (OR adjacent path — verify at T1)

**Do NOT modify:**
- `app/composers/section_02a/directive_model.py` (Story 34-3 surface; READ ONLY)
- `app/composers/section_02a/composer.py` (Story 34-3 surface)
- §02A composer test suite (Story 34-3 surface)
- Story 34-1 integration test (READ ONLY — must stay green underneath you)

## Critical implementation notes (SUBSTRATE-AUDIT-CORRECTED 2026-05-22)

- **D1 inline-tuple-to-constant refactor IS story scope (not assumed).** Current wrangler at lines 328-338 uses an INLINE tuple `if src["role"] not in ("primary", "validation", ...)`. Story 34-2 extracts to a module-level `_ALLOWED_ROLES: frozenset[str]` constant + extends to 7 elements (1 existing + 2 new §02A + 4 existing wrangler vocab preserved). See spec D1 for the exact code; the constant placement is alongside `_SUPPORTED_PROVIDERS` at line 228.
- **D2 excluded_reason validation location is the boundary at line 338-339** (after role check, before ref_id check). See spec D2 code block — `_ALLOWED_EXCLUDED_REASONS: frozenset[str]` constant at module top + new validation block inserted at the boundary.
- **D3 cross-field invariants migrated from §02A directive_model.py:80-106.** Each invariant raises `DirectiveError` with the specific clause cited (mirror §02A's error message style). Line range 80-106 is stable across Story 34-3 (the rename is at line 58, not 80-106).
- **D4 ignored-row filtering at line 1776** (immediately before the locator-shape materialization for-loop). See spec D4 for code; filter `directive["sources"]` into `ignored_sources` + `non_ignored_sources`; iterate only over `non_ignored_sources`; emit audit log to STDERR per filtered row.
- **D5 primary-presence rule UNCHANGED** — operates on POST-filter sources list (after D4 removes ignored). Rule at line 388-394 stays intact.
- **Translator shrinkage (T4)** — `TRANSLATOR_ACTIVE_MAPPINGS` reduces from 3 → 1 element. Story 34-1 round-trip test continues to PASS (test asserts current state; you update lockstep if needed). Story 34-1 spec D6 has the test only assert non-empty membership, so removal of 2 elements should not break the round-trip test.
- **K-target 1.5× ≈ ~7.5K LOC ceiling.** Estimate ~200-400 LOC. Comfortable.
- **Story 34-1 ratchet stay-green is BINDING abort trigger** per SCP §5 abort tripwire.
- **Test file location:** `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py` (co-located with existing `test_run_wrangler.py`; NOT under `tests/specialists/texas/` which is the LangGraph specialist surface).

## T9 self-conducted G6 layered review

Standard layered (NOT cross-agent). Blind/Edge/Auditor. Mock-surface audit not required (no mocks in wrangler-side substrate edit).

## T10 ready-for-review handoff

- Flip to `review` in `sprint-status.yaml`.
- Write handoff at `_codex-handoff/34-2.ready-for-review.md`.
- Report Story 34-1 ratchet status (PASS expected).
- Report broad-regression delta vs 88-baseline.

## Cycle-close discipline

After Claude T11 commits + flips done, dispatch Story 34-3 (§02A `src_id` → `ref_id` rename + J-A1(a)/(b) cli_adapter completion).

```

---

**Authored 2026-05-22 by Claude orchestrator. Ready for Codex dispatch post-Story-34-1-close.**
