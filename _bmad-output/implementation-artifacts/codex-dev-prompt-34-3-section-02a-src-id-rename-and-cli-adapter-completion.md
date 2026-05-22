# Codex dev-story prompt — Story 34-3 (§02A `src_id` → `ref_id` Rename + J-A1(a)/(b) cli_adapter Completion; Winston A2 binding)

**Cycle:** Claude spec (D1-D7 LOCKED 2026-05-22) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-3.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 — slot 3 (lands AFTER Stories 34-1 + 34-2).
**Dispatch ordering:** **DISPATCH AFTER Stories 34-1 AND 34-2 CLOSE.**

---

```
Run bmad-dev-story on Story 34-3 (Epic 34 Wave 1; dual-gate; §02A src_id → ref_id rename + J-A1(a)/(b) cli_adapter completion — Winston A2 binding).

## ⚠️ CONTRACT-LOCKED — D1-D7 ARE LOCKED.

Spec: `_bmad-output/implementation-artifacts/migration-34-3-section-02a-src-id-rename-and-cli-adapter-completion.md`

## Required reading

1. Story 34-3 spec D1-D7.
2. Stories 34-1 + 34-2 specs (translator context; predecessor changes).
3. `app/composers/section_02a/directive_model.py` — current field name `src_id`.
4. `app/composers/section_02a/composer.py` + `cli_adapter.py` — current signatures + call patterns.
5. `app/marcus/cli/trial.py` — the upstream call site with `effective_trial_id`.
6. `app/models/adapter.py` — `ChatModelHandle` NamedTuple + `ModelResolutionEntry` shape.
7. `_bmad-output/planning-artifacts/deferred-inventory.md` J-A1(a) + J-A1(b) entries.
8. Epic 34 §"Story 34-3" — AC-34-3-A through AC-34-3-F.
9. C1 SCP allowlist — confirm all 13 modified paths + 2 new test paths are pre-allowlisted.

## T1 hard checkpoints

- C1 commit `3159a0e` is ancestor of HEAD.
- Stories 34-1 AND 34-2 = `done` in `sprint-status.yaml`.
- Story 34-1 round-trip test PASS on clean tree.
- `TRANSLATOR_ACTIVE_MAPPINGS` contains exactly 1 element (`src-id-to-ref-id`).
- §02A composer importable; `compose()` signature confirmed (no prior `run_id` parameter).

## Files in scope

**Modified (~13 files per D1+D2+D5+D6):**
See spec §"Files touched". Notable:
- `app/composers/section_02a/directive_model.py` (D1)
- `app/composers/section_02a/{composer.py, _prompt.py, _cache.py, cli_adapter.py, __init__.py}` (D2 + D3 + D4)
- `app/marcus/cli/trial.py` (call-site update)
- `docs/conversational-gates/section-02a-composer.j2` (D2 if it names src_id)
- 8 §02A test-surface files (D5)
- `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` (D6)

**New:**
- `tests/marcus_cli/test_cli_adapter_run_id_thread_through.py` (D3 J-A1(a) regression)
- `tests/marcus_cli/test_cli_adapter_model_resolution_trail.py` (D4 J-A1(b) regression)

**Modified — translator (D7):**
- `app/composers/section_02a/_wrangler_translator.py` — remove `src-id-to-ref-id` from `TRANSLATOR_ACTIVE_MAPPINGS` (resulting in empty frozenset)

**Do NOT modify:**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (Stories 34-2 + 34-4 surface; READ ONLY at T1)
- Story 34-1 integration test (READ ONLY)

## Critical implementation notes (SUBSTRATE-AUDIT-CORRECTED 2026-05-22)

- **D1 rename:** the field `src_id` → `ref_id` in DirectiveSource (`directive_model.py:58`). Pydantic field constraints preserved.
- **D2 cascading sweep — NARROWED post-audit:**
  - `docs/conversational-gates/section-02a-composer.j2` is a **NO-OP** (0 src_id references; verified via grep). Remove from your touch list.
  - `app/composers/section_02a/{composer.py, _prompt.py, _cache.py, cli_adapter.py, __init__.py}`: Codex T1 SHALL `grep -rn "src_id" app/composers/section_02a/` to enumerate exact per-file hits. Touch ONLY files with non-zero hits. Do NOT touch files with 0 hits.
- **D3 J-A1(a) signature — SUBSTRATE-CORRECTED:**
  - Current `compose_and_write` signature is **`compose_and_write(corpus_dir, run_dir, *, llm=None)`** (positional+kwarg), NOT all-kwarg.
  - Add `run_id: UUID` as **keyword-only REQUIRED** (after the `*` and before `llm`). Preserve existing `llm` kwarg.
  - `trial.py` call site at lines 241-244 ALREADY uses keyword args; simply add `run_id=effective_trial_id`. `effective_trial_id` is in scope at trial.py line 220.
  - **CRITICAL: REMOVE the `TODO(post-trial-3-retro)` docstring block at cli_adapter.py:50-63** in lockstep with the code fix. Replace with single-line: `Threads operator-supplied run_id (J-A1(a)) and writes model_resolution_trail sidecar (J-A1(b)).`
- **D4 J-A1(b) — import path SUBSTRATE-CORRECTED:**
  - `ModelResolutionEntry` import is `from app.models.state.model_resolution_entry import ModelResolutionEntry`, NOT `from app.models.adapter import ModelResolutionEntry`.
  - At T1, `Read app/models/state/model_resolution_entry.py` to verify the field shape (the sidecar JSON includes those fields).
  - Sidecar landing path: `run_dir / "model_resolution_trail.json"`.
- **D5 test migration — COUNT SUBSTRATE-CORRECTED:**
  - **Actual `src_id|ref_id` hits live in 4 files** (verified via grep), NOT 8:
    - `tests/composers/section_02a/test_composer_directive_model_shape.py` (2)
    - `tests/composers/section_02a/test_composer_utf8_write.py` (1)
    - `tests/gates/section_02a/_helpers.py` (3)
    - `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` (1)
  - The other 4 files allowlisted at C1 may need touches IF wider grep (attribute access via `.src_id`) surfaces hits. Codex T1 SHALL run wider grep to confirm; do NOT modify files with 0 hits.
- **D6 M-A1 wiring tests:** update existing 4 tests at `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` + author 2 new J-A1 regression tests. Codex T1 SHALL read the existing test file to understand the actual mock pattern before authoring.
- **D7 translator shrinkage:** `TRANSLATOR_ACTIVE_MAPPINGS = frozenset()` at this story's close. Story 34-5's sequence test will verify the empty state.
- **K-target 1.5× ≈ ~7.5K LOC.** Multi-file rename + 2 new tests. Estimate ~400-700 LOC (smaller after D5 count correction). Comfortable.
- **Story 34-1 ratchet stay-green is BINDING abort trigger.** With the translator's `src-id-to-ref-id` mapping removed, §02A now natively emits `ref_id` so the wrangler accepts it directly. Test should still pass.

## T9 self-G6 + T10 ready-for-review handoff (standard pattern).

## Cycle-close discipline

After Claude T11 commits + flips done, dispatch Story 34-4 (wrangler metadata.json sme_refs additive emission).

```

---

**Authored 2026-05-22 by Claude orchestrator. Ready for Codex dispatch post-Stories-34-1-and-34-2-close.**
