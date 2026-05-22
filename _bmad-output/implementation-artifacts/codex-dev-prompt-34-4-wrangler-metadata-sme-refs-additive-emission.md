# Codex dev-story prompt — Story 34-4 (Wrangler `metadata.json` `sme_refs[]` Additive Emission; Murat M-Murat-3 binding)

**Cycle:** Claude spec (D1-D5 LOCKED 2026-05-22; SUBSTRATE-VERIFIED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-4.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 — slot 4 (downstream of substrate harmonization 34-2 + 34-3; closes D5/D6 soft-degrade).
**Dispatch ordering:** **DISPATCH AFTER Stories 34-1 + 34-2 + 34-3 CLOSE.**

---

```
Run bmad-dev-story on Story 34-4 (Epic 34 Wave 1; single-gate; standard T11; wrangler metadata.json sme_refs[] additive emission — Murat M-Murat-3 binding).

## ⚠️ CONTRACT-LOCKED — D1-D5 ARE LOCKED.

Spec: `_bmad-output/implementation-artifacts/migration-34-4-wrangler-metadata-sme-refs-additive-emission.md`

## Required reading

1. Story 34-4 spec D1-D5 (substrate-verified; code blocks in D1 + D5 are the literal target shape).
2. Stories 34-1 + 34-2 + 34-3 specs (predecessor context; Story 34-1's integration test is the ratchet you EXTEND).
3. `skills/bmad-agent-texas/scripts/run_wrangler.py:1239-1266` — current `_write_metadata_json` (your edit target).
4. `skills/bmad-agent-texas/scripts/run_wrangler.py:171-187` — `SourceOutcome` dataclass with `content_text` field for per-source digest.
5. `app/marcus/intake/pre_packet.py:175-207` — consumer `_build_sme_refs` (verify at T5 that NO pre_packet change is needed).
6. `app/marcus/lesson_plan/log.py:311-336` — `SourceRef` Pydantic model (the shape your sme_refs entries must satisfy).
7. Epic 34 §"Story 34-4" + AC-34-4-A-EXT (the integration-test extension you MUST author per ratchet pattern).

## T1 hard checkpoints

- C1 commit `3159a0e` is ancestor of HEAD.
- Stories 34-1 + 34-2 + 34-3 = `done` in sprint-status.yaml (all three predecessors must close).
- Story 34-1 round-trip test PASS on clean tree (`pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v` → 3 passed).
- All 5 TW-7c-4 audit tests PASS.
- Verify `SourceOutcome.content_text` field exists at `run_wrangler.py:183`.
- Verify `hashlib` imported at `run_wrangler.py` top (Phase A confirmed).
- Verify `_write_metadata_json` signature at `run_wrangler.py:1239-1266` matches spec D1 expected shape.

## Files in scope

**Modified (2 files):**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (D1: lines 1239-1266 metadata writer + add `hashlib.sha256(...)` per-source)
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (D5: extend with sme_refs assertion block per AC-34-4-A-EXT)

**New (1 file):**
- `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py` (D3 wrangler-side unit tests)

**Conditionally modified (verify at T5; likely NO-OP):**
- `app/marcus/intake/pre_packet.py` — existing `_build_sme_refs` should fire its preferred-branch on new wrangler output; no change expected.

**Do NOT modify:**
- `app/composers/section_02a/_wrangler_translator.py` — Story 34-4 does NOT affect translator (translator is INPUT shape; sme_refs is OUTPUT shape). TRANSLATOR_ACTIVE_MAPPINGS unchanged at this story.
- §02A composer + tests (Story 34-3 surface).
- `app/marcus/lesson_plan/log.py` — SourceRef model is the CONTRACT; you write to match it, not modify it.

## Critical implementation notes (SUBSTRATE-VERIFIED 2026-05-22)

- **D1 additive emission (Murat M-Murat-3 BINDING):** `provenance` MUST be preserved unchanged. `sme_refs` is an ADDITIVE new key. Use the literal code block in spec D1 — verbatim.
- **D2 per-source content_digest:** `hashlib.sha256(o.content_text.encode("utf-8")).hexdigest()` — per outcome's `content_text` field, NOT whole-bundle sha256 of extracted.md.
- **D3 path semantics:** `o.locator if o.provider == "local_file" else None`. SourceRef validator at `log.py:329-335` rejects absolute paths + traversal segments — pre_packet enforces this on read. Your wrangler emission passes the locator unchanged; if locator is absolute OR contains `..`, that's a directive-side problem (not Story 34-4's bug).
- **D4 ignored-row exclusion** is INHERITED from Story 34-2 D4 — `outcomes` list at this point already excludes ignored rows. Do NOT add separate filtering.
- **D5 Story 34-1 ratchet extension:** literal assertion block from spec D5 — add to `test_forensic_directive_round_trips_through_wrangler_subprocess_via_translator` AFTER the existing materials-non-empty + row-shape assertions. Total assertion delta: ~12 new lines per spec D5.
- **K-target 1.5× ≈ ~4.5K LOC ceiling for 3-pt story.** Estimate ~100-200 LOC. Comfortable.
- **Story 34-1 ratchet stay-green is BINDING abort trigger.** Once D5 extension lands, the ratchet test ASSERTS the new behavior + the existing assertions. If the ratchet drops to RED, abort + revert per SCP §5.

## T9 self-G6 + T10 ready-for-review handoff (standard pattern).

## Cycle-close discipline

After Claude T11 commits + flips done, dispatch Story 34-5 (translator-shrinkage sequence test; carrier story).

```

---

**Authored 2026-05-22 by Claude orchestrator (substrate-tested discipline post-4-HALT-AND-SURFACE-recovery). Ready for Codex dispatch post-Stories-34-1-34-2-34-3-close.**
