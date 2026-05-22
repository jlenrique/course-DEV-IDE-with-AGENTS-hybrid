# Codex dev-story prompt — Story 34-6 (Legacy `directive_composer.py` Deletion + 7-File Test Rewire/Delete)

**Cycle:** Claude spec (D1-D6 LOCKED 2026-05-22; SUBSTRATE-VERIFIED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-6.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 — slot 6 (after substrate stable; before Epic close at 34-7).
**Dispatch ordering:** **DISPATCH AFTER Stories 34-1..34-5 CLOSE.**

---

```
Run bmad-dev-story on Story 34-6 (Epic 34 Wave 1; dual-gate; standard T11; legacy directive_composer.py deletion + 7-file test rewire/delete — C1 cleanup per Phase A inventory).

## ⚠️ CONTRACT-LOCKED — D1-D6 ARE LOCKED. DIRECTION-MAY-FLIP CAVEAT AT D1.

Spec: `_bmad-output/implementation-artifacts/migration-34-6-legacy-directive-composer-deletion.md`

## Required reading

1. Story 34-6 spec D1-D6 (substrate-verified hit counts in D3 are the authoritative per-file inventory).
2. Phase A probe §"CLEANUP-class C1": `_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md`
3. Legacy composer file: `app/marcus/orchestrator/directive_composer.py` (READ at T1 to understand the legacy shape; DELETE at T2).
4. §02A composer cli_adapter (post-Story-34-3): `app/composers/section_02a/cli_adapter.py` (the REWIRE target for D4 rewire pattern).
5. The 7 test files in scope (full Read at T1 for per-file classification):
   - `tests/unit/marcus/orchestrator/test_directive_composer_pure.py` (20 hits — likely DELETE)
   - `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py` (23 hits — likely DELETE)
   - `tests/composition/test_texas_to_cd_chain.py` (5 hits — likely REWIRE)
   - `tests/parity/test_trial_475_directive_composition_regression.py` (2 hits — likely REWIRE)
   - `tests/parity/test_trial_475_texas_hardening_regression.py` (2 hits — classify per T1)
   - `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` (2 hits — classify per T1)
   - `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py` (2 hits — likely REWIRE)

## T1 hard checkpoints

- C1 + Stories 34-1..34-5 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS.
- All 5 TW-7c-4 audit tests PASS.
- **D1 direction-may-flip re-grep:** `grep -rn "from app.marcus.orchestrator.directive_composer\|import directive_composer\|orchestrator\.directive_composer" app/` MUST return 0. If non-zero, HALT-AND-SURFACE — story flips to "harmonize" instead of "delete."

## Files in scope

**DELETED (1 file):**
- `app/marcus/orchestrator/directive_composer.py` (pre-allowlisted at C1)

**DELETED or MODIFIED (per-file T1 classification; 7 test files; ALL pre-allowlisted at C1):**
See spec D3 for the decision tree + expected classifications. Codex T1 reads each file + applies the tree + documents the classification in T9 self-review.

**Do NOT modify:**
- `app/composers/section_02a/_wrangler_translator.py` — Story 34-7 deletes; Story 34-6 leaves alone.
- Story 34-1 integration test (separate concern; STAYS GREEN per AC-34-6-D).

## Critical implementation notes (SUBSTRATE-VERIFIED 2026-05-22)

- **D1 direction-may-flip BINDING.** Re-grep at T1; if any runtime caller exists, HALT.
- **D2 deletion:** ~270 LOC removed entirely. `app/marcus/orchestrator/__init__.py` does NOT re-export legacy composer (Winston W-SCP-A1 verified) — no `__init__.py` edit needed.
- **D3 per-file classification:** the substrate-verified hit counts in the spec are authoritative starting points. Codex's T1 read + decision tree settles each file. Pure unit tests of legacy behavior = DELETE; fixture/setup uses = REWIRE.
- **D4 rewire pattern:** post-Story-34-3, `compose_and_write` REQUIRES `run_id: UUID` parameter. Use the spec D4 code shape for rewires.
- **D5 Story 34-1 ratchet stay-green is BINDING abort trigger.**
- **D6 zero-orphan invariant:** post-close, 3 grep-zero checks. Codex T9 self-review runs these 3 greps + reports results.
- **K-target 1.5× ≈ ~7.5K LOC for 5-pt story.** Multi-file but deletion-heavy; estimate ~400-800 LOC delta (mostly deletions; some rewires). Comfortable.

## T9 self-G6 + T10 ready-for-review handoff (standard pattern). Document per-file classification + rationale.

## Cycle-close

After Claude T11 commits + flips done, dispatch Story 34-7 (FINAL story; translator deletion + A23/P5 anti-pattern entries + Epic close + deferred-inventory closure markers).

```

---

**Authored 2026-05-22 by Claude orchestrator (substrate-tested discipline). Ready for Codex dispatch post-Stories-34-1-through-34-5-close.**
