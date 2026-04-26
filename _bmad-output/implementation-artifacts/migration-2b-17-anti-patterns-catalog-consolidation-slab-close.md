# Migration Story 2b.17: Anti-Patterns Catalog Consolidation + Slab 2b CLOSE

**Status:** done
**Sprint key:** `migration-2b-17-anti-patterns-catalog-consolidation-slab-close`
**Epic:** Slab 2b â€” seventeenth story; **THIRD cross-cutting + SLAB-CLOSING story**. Closes migration-epic-2b in lockstep at story close (per AC-G).
**Pts:** 2 | **Gate:** single (governance JSON `2b-17.expected_gate_mode = "single-gate"`). **K-target:** ~1.2Ã— (target 8 / floor 6; documentation-heavy + retrospective + minimal new test surface).

**Lean batched party-mode amendments applied 2026-04-25 (Murat + Amelia, batched with 2b.16):**
- **Murat 2b.17-R1 (NICE-TO-HAVE):** Add bullet 9 to AC-C retrospective section list: "K-cycle efficiency across 14 inheritors (target-vs-actual band; M-R20 cap holds or breaks)." Promotes to BINDING if Paige's slab-2a precedent has parallel section (verify at dev T2).
- **Murat 2b.17-R2 (BINDING â€” governance lockstep):** AC-F TEMPLATE v2.4 bump MUST cite party-mode consensus stamp in v2.4 header table per format-freeze rule "Updates to the rules require party-mode consensus + a version bump." Without consensus citation, the v2.4 bump itself violates its own governance contract.
- **Amelia A-2b.17-R1:** AC-G enumerates ALL FOUR sprint-status mutations at slab-close (epic flip + story flip + last_updated + `next-session-start-here.md` deferred-inventory status counts per CLAUDE.md governance binding consultation point #2). Prevents closeout-hygiene drift.
- **Amelia A-2b.17-R2:** AC-F enumerates v2.3â†’v2.4 changelog row content verbatim in spec text (which advisories codified â€” M-R22/M-R24/Paige Â§12.10 â€” which sections amended) so dev agent pastes rather than re-derives at T8.

Slab 2b closing story. Consolidates anti-patterns catalog (â‰¥5 entries harvested from 2b.1-2b.14), authors `slab-2b-retrospective.md` per Slab 2a precedent, updates Â§12 framing for slab-close, files final deferred-inventory items, flips epic to done. **Closes Slab 2b.** Slab 2c (Wondercraft validation pilot â€” generator pre-emptively absorbed via Path A at 2b.8 close, so Slab 2c.1 needs operator decision on alternative generator-validation subject) opens after 2b.17 close.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.16. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” 2b.17-specific deltas:**
- **C** Reference patterns: `slab-2a-retrospective.md` (precedent for slab-close retrospective).
- **F** `pyproject.toml` C3 contains 18 rows. 2b.17 does NOT change C3.
- **G** FR54 retrospective summary across all specialists migrated in Slab 2b.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** No new drifts at 2b.17.

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** retrospective + catalog consolidation + sprint-status flips. Slab-3 substrate setup OUT OF SCOPE.
- **R13 N/A:** slab-closing.
- **R14 N/A:** slab-closing.

---

## Story

As a **dev agent closing Slab 2b**,
I want **anti-patterns catalog consolidated with â‰¥5 entries harvested across 2b.1-2b.14 + slab-2b-retrospective.md authored + migration-guide Â§12 framing updated for slab-close + epic flipped to done**,
So that **FR64 is met before Slab 2c opens, the scaffold-generator (Slab 2c) can reference real anti-patterns, and Slab 2b closes with the same governance discipline as Slab 2a**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. NO `@pytest.mark.llm_live` tests.

### AC-2b.17-A â€” Anti-patterns catalog â‰¥5 confirmed entries harvested from 2b migration

- **Given** `docs/dev-guide/specialist-anti-patterns.md` contains seed entries from 1.7 + Slab-2a additions (A9, A10, A11, A12-RESOLVED) + Slab-2b additions (A11 sub-shapes A-D, A13 NEW from 2b.15).
- **When** dev agent reviews entries harvested during 2b.1-2b.14:
  - A11 sub-shape A (persona-divergence): Irene/Gary/Vera/Quinn-R/Desmond examples (5+ at freeze per M-R23)
  - A11 sub-shape B (snake-case-divergence): Tracy
  - A11 sub-shape C (lane-divergence): CD
  - A11 sub-shape D (vendor-name-divergence): Enrique/Wanda/Kim/Vyx/Aria FROZEN at 5
  - A10: model-tier framing drift (Irene/Kira/Gary/Vera/Quinn-R/Desmond/CD = 7 examples)
  - A13 NEW (loose-typing accumulation across multi-specialist migration; resolved at 2b.15)
- **Then** catalog has â‰¥5 entries harvested from real migration work (NOT seed entries); each entry has name + example + counter-pattern + slab-of-discovery per anti-patterns.md format-freeze.

**Test pin:** 1 catalog-shape test asserts each entry conforms to 4-field format.

### AC-2b.17-B â€” Migration-guide Â§Anti-Patterns Appendix cites catalog

Per epic 2b.17. Migration-guide Â§4 (Gate Migration) and Â§12 (Specialist Walkthrough) cross-reference anti-pattern entries where relevant.

### AC-2b.17-C â€” Slab 2b retrospective authored

Per Slab 2a precedent at `_bmad-output/implementation-artifacts/slab-2a-retrospective.md`. NEW file `_bmad-output/implementation-artifacts/slab-2b-retrospective.md` covering:
- Stories landed (2b.1-2b.17, 17 stories)
- FR coverage (FR9-FR16 across 14 specialists; FR14 architecturally enforced via 2b.16; FR64 met via 2b.17 catalog)
- 5 specialist-shape categories validated (narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API-tool-dispatch / operator-instructions thin node)
- Cumulative regression intelligence (started â‰¥175 at 2a.5 close; finished â‰¥352 at 2b.16 close)
- Anti-pattern catalog growth (Slab 1.7 seed â†’ A11 retitled + sub-shapes A/B/C/D + A12-RESOLVED + A13 NEW)
- TEMPLATE doc v1 â†’ v2.3 evolution (R1-R7 â†’ R1-R14)
- Deferred-inventory follow-ons surfaced + closed in lockstep (sanctum-lock cross-cutting, importlib-loader extraction at 2b.15; Tracy/Mira/Kim FR54 follow-ons; Slab-3 reactivation gates)
- Slab 2c kickoff readiness checklist (Wondercraft Path A absorbed; alternative generator-validation subject TBD)
- Slab 2c kickoff handoff section per Paige P-R6 precedent

### AC-2b.17-D â€” Migration-guide Â§12 framing updated for slab-close

Â§12.5 framing sentence updated: "Slab 2b closed at 2b.17; 5 specialist-shape categories validated across 14 per-specialist migrations; Â§12 reference structurally complete for Slab 2c inheritance." Add Â§12.10.2 sub-subsection (Slab 2b retrospective) per Paige P-R3 deferred container restructure (deferred at 2b.5; lands NOW at slab-close per the deferral plan).

### AC-2b.17-E â€” Deferred-inventory final sweep

- Close lockstep follow-ons: `slab-2b-mid-cross-cutting-importlib-loader-extraction` + `slab-2a-close-followon-sanctum-lock-cross-cutting` (closed at 2b.15).
- File at 2b.17 close: Slab 2c.1 generator-validation-target decision (operator picks subject).
- Update Â§"Inventory Summary" counts.

### AC-2b.17-F â€” TEMPLATE compliance (per R1â€“R14 v2.3) + amendment to v2.4

R1â€“R14 v2.3 honored. **TEMPLATE doc bumped to v2.4** at slab-close to codify M-R22 advisory (tag-namespace-root-tracks-category) + M-R24 advisory (wave-close framing) + Paige Â§12.10 retrospective container restructure (deferred from 2b.5).

### AC-2b.17-G â€” D12 SLAB-CLOSING close protocol + epic flip + sprint-status

1. **Invariant preservation:** Slab-1 substrate intact; FR9-FR16 fully exercised across 14 specialists; FR14 architecturally enforced via 2b.16; FR54 substrate intact; FR64 met via this story.
2. **Anti-pattern harvest:** catalog consolidated; A13 NEW + A11 sub-shapes documented.
3. **Migration-guide update:** Â§12 slab-close framing + Â§12.10.2 Slab 2b retrospective sub-subsection per restructure.
4. **TEMPLATE compliance:** R1â€“R14 v2.3 â†’ v2.4 amendment; cross-cutting + slab-close discipline maintained throughout Slab 2b.

**Sprint-status flip:** `migration-2b-17-...: done`; **`migration-epic-2b-slab-2-per-specialist-wave: done`** (slab close); update `last_updated`.

---

## File Structure Requirements

### NEW files

- `_bmad-output/implementation-artifacts/slab-2b-retrospective.md` â€” NEW per AC-C.

### MODIFIED files

- `docs/dev-guide/specialist-anti-patterns.md` â€” consolidation per AC-A.
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.5 framing updated; Â§12.10 â†’ container with Â§12.10.2 NEW per AC-D + Paige restructure; Â§4 + Â§12 cross-references to anti-patterns per AC-B.
- `docs/dev-guide/specialist-migration-template.md` â€” bumped v2.3 â†’ v2.4 per AC-F.
- `_bmad-output/planning-artifacts/deferred-inventory.md` â€” final sweep per AC-E.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-G.

---

## Testing Requirements

**K-target ~1.2Ã— (target 8 / floor 6).** Test count: 1 (catalog format) + 2 (cross-reference grep + retrospective file existence) + 1 (slab-close framing assertion) + 2 (template doc version + deferred-inventory consistency) + 2 (sprint-status epic flip + close note) = **8 K-floor units / 8 collected**. Documentation-heavy story; minimal new test surface justified.

**Regression target at T8:** â‰¥354 passed / â‰¥10 skipped placeholder-key. Import-linter 3/3 KEPT (or 4/4 if C4 added at 2b.15); Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


## Closure Notes (Dev)
- Updated migration guide, anti-pattern catalog, and template doc for slab-close governance updates (v2.4 bump).
- Authored Slab 2b retrospective and updated sprint/deferred trackers for story + epic close.
- Applied final status flips for 2b.14-2b.17 and migration-epic-2b.

### T8 Evidence
- pytest (owned scopes): PASS
- ruff check (owned scopes): PASS
- lint-imports: PASS

