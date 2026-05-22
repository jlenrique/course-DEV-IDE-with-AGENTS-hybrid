# Codex dev-story prompt — Story 34-7 (Translator Deletion + A23/P5 Anti-Pattern Entries + Epic 34 Close; FINAL STORY)

**Cycle:** Claude spec (D1-D7 LOCKED 2026-05-22; SUBSTRATE-VERIFIED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-7.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done + Epic 34 closure ceremony.
**Wave:** 1 — slot 7 (FINAL story of Epic 34).
**Dispatch ordering:** **DISPATCH AFTER Stories 34-1..34-6 CLOSE.**

---

```
Run bmad-dev-story on Story 34-7 (Epic 34 Wave 1; dual-gate; standard T11; translator deletion + A23/P5 anti-pattern entries + Epic 34 close — FINAL STORY; closes deferred-inventory §02A entry).

## ⚠️ CONTRACT-LOCKED — D1-D7 ARE LOCKED.

Spec: `_bmad-output/implementation-artifacts/migration-34-7-translator-deletion-anti-pattern-entries-epic-close.md`

## Required reading

1. Story 34-7 spec D1-D7 (substrate-verified throughout).
2. Story 34-1 spec D2 (scaffold marker source-of-truth: `__epic_34_scaffolding__ = True` + `DELETE-AT-EPIC-34-CLOSE`).
3. Phase B consensus + Quinn-synthesis Option 5 record (Murat M-Murat-2 binding for A23 + P5).
4. `docs/dev-guide/specialist-anti-patterns.md` — format-frozen 4-field shape; substrate-verified next ordinals A23 + P5 (current ends at A22 + P4).
5. `_bmad-output/planning-artifacts/deferred-inventory.md` §"CRITICAL Trial-3-blocking" entry to close.
6. Story 34-5 sequence test (DELETING) + Story 34-1 round-trip test (SIMPLIFYING).

## T1 hard checkpoints

- C1 + Stories 34-1..34-6 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS on clean tree.
- `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` (read + verify via grep).
- Story 34-5 sequence test PASSES at dispatch (asserts the empty state).
- All 5 TW-7c-4 audit tests PASS.
- Anti-pattern doc confirmed at A22 + P4 highest ordinals (verify via grep `^### A\|^### P`).

## Files in scope

**Deleted (1 file):**
- `app/composers/section_02a/_wrangler_translator.py` (pre-allowlisted at C1)

**Deleted (1 test file):**
- `tests/integration/test_section_02a_translator_shrinkage_sequence.py` (Story 34-5 deliverable; redundant once translator deleted)

**Modified (3 files):**
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (remove translator imports + invocation; test runs §02A → wrangler directly)
- `docs/dev-guide/specialist-anti-patterns.md` (append A23 + P5 per format-frozen 4-field shape)
- `_bmad-output/planning-artifacts/deferred-inventory.md` (closure markers per D5)

**Do NOT modify:**
- §02A composer (Story 34-3 surface; stable post-Story-34-3)
- Texas wrangler (Story 34-2 + 34-4 surface; stable)
- `app/marcus/orchestrator/directive_composer.py` (deleted at Story 34-6; should NOT exist at Story 34-7 dispatch)
- §02A test suite (Story 34-3 surface; stable)

## Critical implementation notes (SUBSTRATE-VERIFIED 2026-05-22)

- **D1 translator deletion is BINDING.** Pre-condition: `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()`. If non-empty at dispatch, HALT-AND-SURFACE — earlier story missed shrinkage AC.
- **D2 Story-34-1 test simplification:** REMOVE translator import + `translate_directive_for_wrangler` call. Test writes `directive.model_dump(mode="json")` DIRECTLY to YAML. Forensic-anchor + sme_refs + materials + exit-code assertions all STAY (substrate harmonization complete; §02A directly matches wrangler vocab).
- **D3 Story-34-5 sequence-test DELETED** — the module it tested no longer exists; import would fail.
- **D4 A23 + P5 entries per format-frozen 4-field shape** (literal markdown blocks in spec D4). Anti-pattern doc next ordinals: A23 + P5 (verify via grep at T1).
- **D5 deferred-inventory closure markers** — `section-02a-downstream-consumer-compatibility-systemic-drift` + J-A1(a) + J-A1(b) all get strikethrough + closure markers per spec D5 markdown.
- **D6 forensic grep-sweep BINDING:** `grep -rn "__epic_34_scaffolding__" .` AND `grep -rn "DELETE-AT-EPIC-34-CLOSE" .` MUST BOTH return 0 matches post-deletion. Codex T9 self-review handoff MUST include grep evidence as forensic proof.
- **D7 Trial-3-PASS gate satisfaction:** at Story 34-7 close, operator can launch Trial-3 attempt-3 immediately. No substrate work remaining.
- **K-target 1.5× ≈ ~4.5K LOC for 3-pt story.** Estimate ~200-400 LOC delta (mostly deletions + 2 new anti-pattern markdown blocks + closure markers). Comfortable.

## T9 self-G6 + grep-evidence requirement

T9 handoff at `_codex-handoff/34-7.ready-for-review.md` MUST include:
- Standard Blind/Edge/Auditor sections
- **D6 grep-sweep evidence section:** literal output of both greps showing 0 matches across N files; this is the AC-34-7-H forensic proof for Claude T11 review.
- Per-file change summary (translator deletion + Story-34-1 simplification + Story-34-5 deletion + anti-pattern entries + deferred-inventory closures).

## Cycle-close — EPIC 34 CLOSURE CEREMONY

After Claude T11 commits + flips Story 34-7 done:
1. **🎉 Epic 34 §02A Downstream-Consumer Schema Coherence FULLY COMPLETE: 7/7 stories DONE.**
2. Sprint-status.yaml gets Epic-close ceremony entry.
3. `next-session-start-here.md` updated to reflect Trial-3 attempt-3 launch readiness.
4. Operator can dispatch Trial-3 attempt-3 from `course-content/courses/tejal-apc-c1-m1-p2-trends/` on FULLY harmonized substrate (no temporary translator; no legacy composer; canonical §02A vocabulary).

The Trial-3-PASS gate per Epic 34 header is SATISFIED at this story's close.

```

---

**Authored 2026-05-22 by Claude orchestrator (substrate-tested discipline). Ready for Codex dispatch post-Stories-34-1-through-34-6-close. FINAL Epic-34 story.**
