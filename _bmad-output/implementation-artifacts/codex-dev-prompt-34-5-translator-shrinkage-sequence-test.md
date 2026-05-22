# Codex dev-story prompt — Story 34-5 (Translator-Shrinkage Sequence Test; Carrier Story; Murat new-A9-surface-2 mitigation)

**Cycle:** Claude spec (D1-D5 LOCKED 2026-05-22; SUBSTRATE-VERIFIED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-5.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 — slot 5 (carrier story after Stories 34-1..34-4).
**Dispatch ordering:** **DISPATCH AFTER Stories 34-1 + 34-2 + 34-3 + 34-4 CLOSE.**

---

```
Run bmad-dev-story on Story 34-5 (Epic 34 Wave 1; single-gate; standard T11; translator-shrinkage sequence test — carrier story; Murat new-A9-surface-2 production-load-bearing mitigation).

## ⚠️ CONTRACT-LOCKED — D1-D5 ARE LOCKED.

Spec: `_bmad-output/implementation-artifacts/migration-34-5-translator-shrinkage-sequence-test.md`

## Required reading

1. Story 34-5 spec D1-D5 (test code in D3 is the literal target).
2. Stories 34-1 + 34-2 + 34-3 specs (predecessor context; translator state at dispatch reflects their close states).
3. `app/composers/section_02a/_wrangler_translator.py` — the substrate under test. At Story 34-5 dispatch, `TRANSLATOR_ACTIVE_MAPPINGS` MUST be `frozenset()` (empty).

## T1 hard checkpoints

- C1 + Stories 34-1 + 34-2 + 34-3 + 34-4 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS on clean tree.
- All 5 TW-7c-4 audit tests PASS.
- Verify `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` at dispatch (`Read` the file + grep). If not empty, HALT-AND-SURFACE — predecessor Story 34-2 or 34-3 missed its shrinkage AC.

## Files in scope

**New (1 file):**
- `tests/integration/test_section_02a_translator_shrinkage_sequence.py` (D3 literal target)

**Do NOT modify:**
- `app/composers/section_02a/_wrangler_translator.py` — READ ONLY at Story 34-5; deleted at Story 34-7.
- Story 34-1 integration test (separate concern).
- ANY production code (carrier-story discipline; test-only story).

## Critical implementation notes

- **3 tests per D3** — literal code block; copy-paste-and-adapt.
- **AC-34-5-A** requires assertion that constant is production-load-bearing — use `inspect.getsource(translate_directive_for_wrangler)` and check for `TRANSLATOR_ACTIVE_MAPPINGS` substring presence.
- **AC-34-5-A sibling assertion** uses `_RECOGNIZED_MAPPING_NAMES` closed set to catch typos/drift.
- **AC-34-5-B** Story 34-1 ratchet stays GREEN — verify post-test-author by running `pytest tests/integration/ -v` (both files); both should pass.
- **K-target 1.5× ≈ ~4.5K LOC for 3-pt story.** Estimate ~80-120 LOC (3 tests + docstring). Comfortable.
- **No `__init__.py` markers needed** (per Codex Story 34-1 T10 note; pytest collection works without).

## T9 self-G6 + T10 ready-for-review handoff (standard).

## Cycle-close

After Claude T11 commits + flips done, dispatch Story 34-6 (legacy directive_composer.py deletion + 7-file test rewire).

```

---

**Authored 2026-05-22 by Claude orchestrator (substrate-tested discipline). Ready for Codex dispatch post-Stories-34-1-34-2-34-3-34-4-close.**
