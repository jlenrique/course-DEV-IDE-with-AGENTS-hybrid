# Migration Story 34-6: Legacy `directive_composer.py` Deletion + 7-File Test Rewire/Delete (C1 cleanup)

**Status:** ready-for-dev *(spec authored 2026-05-22; predecessor Stories 34-1..34-5 expected `done` at dispatch.)*
**Sprint key:** `migration-34-6-legacy-directive-composer-deletion`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence
**Pts:** 5
**Gate:** **dual-gate** (production code deletion + 7-file test rewire surface)
**K-target:** ~1.5×
**R-tier:** **R2**
**T11-tier:** standard
**Files touched (substrate-verified 2026-05-22):**

**Deleted:**
- `app/marcus/orchestrator/directive_composer.py` (legacy Story-7a.1 broken-fallback composer; runtime-dead post §02A wiring SCP-2026-05-21-trial3-wiring; substrate-verified 0 imports in `app/` via grep)

**Modified or deleted (per-file decision at T1 by Codex; 7 test files with substrate-verified hit counts):**
- `tests/unit/marcus/orchestrator/test_directive_composer_pure.py` (20 hits — DELETE expected; pure unit tests of dead code; nothing to rewire to)
- `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py` (23 hits — DELETE expected; pure unit tests of materialization function)
- `tests/composition/test_texas_to_cd_chain.py` (5 hits — REWIRE expected; composition smoke against §02A `compose()`)
- `tests/parity/test_trial_475_directive_composition_regression.py` (2 hits — REWIRE expected; name says "directive composition" which is now §02A)
- `tests/parity/test_trial_475_texas_hardening_regression.py` (2 hits — REWIRE or DELETE; T1 classify)
- `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` (2 hits — REWIRE or DELETE; T1 classify)
- `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py` (2 hits — REWIRE; "real directive" suggests fixture-based)

**Lookahead tier:** **2** (multi-file; deletion + rewire across test surface).
**Wave:** 1 — slot 6 (after substrate stable; before Epic close).

**FR coverage:** FR-E34-7 (legacy composer deletion + 7-file test rewire/delete).
**NFR coverage:** NFR-E34-1 (Story-34-1 ratchet stays GREEN), NFR-E34-8 (TW-7c-4 dual-predicate; all 8 touched files pre-allowlisted at C1).

**Contract Decisions (LOCKED 2026-05-22 — SUBSTRATE-VERIFIED):**

**D1. Direction-may-flip re-validation (AC-34-6-A BINDING):**

At T1, Codex SHALL re-run the runtime-import grep:
```
grep -rn "from app.marcus.orchestrator.directive_composer\|import directive_composer\|orchestrator\.directive_composer" app/
```

**Substrate-audit result at spec-author time (2026-05-22): 0 matches.** If T1 re-run STILL returns 0 → proceed with deletion. If T1 surfaces ANY runtime caller (e.g., a Story 34-2/34-3/34-4/34-5 close accidentally introduced an import), HALT-AND-SURFACE — story flips to "harmonize legacy composer to current §02A vocab" instead of "delete" per CLAUDE.md §Deferred inventory governance direction-may-flip caveat.

**D2. Legacy composer deletion:**

Once D1 confirms zero runtime callers, DELETE `app/marcus/orchestrator/directive_composer.py` entirely (~270 LOC). Verify via `git status` post-delete.

Verify `app/marcus/orchestrator/__init__.py` does NOT re-export the legacy composer (Winston W-SCP-A1 audit at SCP-ratification verified this — no re-export to clean up).

**D3. Per-file test classification (T1-driven; substrate-verified hit counts):**

For each of the 7 test files, Codex T1 SHALL:
1. Read the file fully.
2. Classify per the decision tree below.
3. Document the classification in T9 self-review with rationale per file.

**Classification decision tree:**
- **DELETE** if the file's tests are PURE unit tests of the legacy composer's behavior (e.g., `test_compose_directive_pure_function_output_shape`). There's nothing to rewire to — §02A's `compose()` has a different signature + does different work (LLM-driven vs corpus-scan).
- **REWIRE** if the file uses the legacy composer as a FIXTURE/SETUP HELPER for testing something else (e.g., Texas dispatch, slab-7b composition smoke). Replace with §02A `compose()` invocation OR with a synthetic-Directive fixture if §02A is overkill.
- **KEEP-WITH-IMPORT-FIX** if the file ONLY imports the legacy symbols for type hints (unlikely; verify).

**Expected per-file classifications (T1 verify):**
- `test_directive_composer_pure.py` (20 hits) — DELETE (pure unit tests; dead code)
- `test_directive_composer_materialization.py` (23 hits) — DELETE (pure unit tests of materialization)
- `test_texas_to_cd_chain.py` (5 hits) — REWIRE to §02A (composition smoke; uses legacy as fixture for Texas dispatch)
- `test_trial_475_directive_composition_regression.py` (2 hits) — REWIRE (regression test for directive composition; §02A is the current shape)
- `test_trial_475_texas_hardening_regression.py` (2 hits) — REWIRE or DELETE per T1 read
- `test_slab_7b_wave_1_opener_composition_smoke.py` (2 hits) — REWIRE or DELETE per T1 read
- `test_texas_live_retrieval_against_real_directive.py` (2 hits) — REWIRE (real-directive fixture)

**D4. Rewire pattern (when applicable):**

For files classified REWIRE, replace legacy imports with §02A composer:

```python
# OLD:
from app.marcus.orchestrator.directive_composer import (
    compose_directive,
    materialize_directive,
)
composed = compose_directive(corpus_path=tmp_path, run_id=str(trial_id))
directive_path, digest = materialize_directive(composed, run_dir)

# NEW (§02A composer):
from app.composers.section_02a.cli_adapter import compose_and_write
# Note: post-Story-34-3, compose_and_write requires run_id parameter:
directive_path, digest = compose_and_write(
    corpus_dir=tmp_path,
    run_dir=run_dir,
    run_id=trial_id,
    # llm=<fake or omit to use make_chat_model("marcus")>
)
```

If the test needs an INJECTABLE LLM (avoid real LLM in tests), pass a fake `BaseChatModel`. The §02A composer accepts `llm` parameter for test injection.

**D5. Story 34-1 ratchet preservation (AC-34-6-D BINDING):**

Story 34-1's `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` MUST stay GREEN at Story 34-6 close. The legacy composer deletion does NOT touch the §02A composer OR the wrangler — ratchet should be unaffected.

**D6. Result: zero orphans:**

Post-Story-34-6 close, the codebase MUST satisfy:
1. `grep -rn "from app.marcus.orchestrator.directive_composer" .` returns 0 matches (production + tests).
2. `grep -rn "compose_directive\|materialize_directive\|ComposedDirective\|ComposedDirectiveSource" .` returns 0 matches in production code; ONLY matches in deferred-inventory + planning-artifacts + retired test files (if classified DELETE).
3. No skipped tests left behind (every classified-DELETE file is gone; every classified-REWIRE file PASSES with §02A imports).

---

## Task chain T1-T11

**T1 readiness check:**
- C1 + Stories 34-1..34-5 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS.
- D1 re-grep: 0 production-code imports of legacy composer.
- Per-file Read of 7 test files; T1 classifies each per D3 tree.

**T2 legacy composer deletion:** D2 implementation.

**T3 per-file test action:** D3/D4 implementation per file.

**T4 ruff + lint-imports + focused suite.**

**T5 Story-34-1 ratchet + broad regression sweep.**

**T6 orphan check (D6):** the 3 grep-zero checks.

**T7-T11 standard pattern.**

---

## Acceptance Criteria

- **AC-34-6-A** (direction revalidation): D1 BINDING.
- **AC-34-6-B** (legacy composer deletion): D2 BINDING.
- **AC-34-6-C** (7-file test rewire/delete): D3/D4 BINDING; classification documented at T9.
- **AC-34-6-D** (Story-34-1 ratchet preserved): D5 BINDING.
- **AC-34-6-E** (Trial-3-PASS gate readiness check): operator-runnable check at story close — all D1+D2+D3 resolved + ratchet GREEN + only Story 34-7 substrate scaffolding remains.

## Cross-references

- Epic 34 §"Story 34-6"
- Phase A probe §"🧹 CLEANUP-class C1 (not blocking but worth folding into Epic 34)"
- `app/marcus/orchestrator/directive_composer.py` (deletion target)
- 7 test files listed above
