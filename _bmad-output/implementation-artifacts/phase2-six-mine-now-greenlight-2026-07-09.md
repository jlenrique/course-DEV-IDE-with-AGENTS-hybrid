# Party GREEN-LIGHT — Phase-2 Six Mine-Now Complete
**Date:** 2026-07-09  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Goal file:** `goal-phase2-six-mine-now-complete-2026-07-09.txt`  
**Seats:** John / Winston / Amelia / Murat (fully spawned)  
**Orchestrator synthesis:** **GO-WITH-AMENDMENTS** (4/4)

---

## Binding program claim

Fully develop + live-validate all 6 operator-named aspects. Session **cannot close** until a later party CLOSE agrees each item’s SUCCESS predicates are MET.

| # | Operator name | Inventory target |
|---|---------------|------------------|
| 1 | Automatic Lesson_plan | `lesson_plan["collateral"] → ComponentSelection` (auto-derive) |
| 2 | Interactive SPOC | SPOC planning REPL + LO ratification UX |
| 3 | Per-SME voice | Per-SME voice/styleguide/attribution/approval |
| 4 | Canonical processed-source | Canonical fully-processed source structure + harden |
| 5 | Drill | Drill collateral projector |
| 6 | workbook-learner-ready-prose-uplift | Learner-ready workbook prose uplift |

S8 stays CLOSED. Product = Marcus-SPOC local runtime.

---

## MUST amendments (folded)

1. **Item 1 = Winston Option A:** derive `ComponentSelection` from Irene `lesson_plan["collateral"]` automatically; **fail-loud** on gaps. Do **not** require a second ratification recorder for the auto path (ratify CLI remains available; auto path is the spine residual).
2. **Item 4 before Item 5:** processed-source `kind` shape-pin before drill projector opens.
3. **Item 3 named-variant styleguide before Item 6:** no Tejal silent fallthrough; unknown SME → marked-fallback-or-gap / hard-fail per Murat.
4. **Items 2 and 4 may split A/B** (John): party CLOSE for the operator-named aspect is on the **A claim** that meets Murat liveproof; B hardenings file to deferred-inventory if needed — but A must still satisfy “fully developed and validated” for the operator short name.
5. **Operator content defaults (Amelia gates — orchestrator proposes, operator may override):**
   - **SME map:** HAI 510 + PHS 620 + Tejal as first three SME keys; non-Tejal must not silently reuse Tejal styleguide (brief §5.5).
   - **Canonical structure:** `slides/` · `references/` · `assessments/` · `bundle/extracted.md` · `g0-enrichment.json` (+ manifest/gap ledger already from Story A–D).
   - **Drill:** minimal schema = LO-linked short practice items (prompt + expected_focus + source_refs); Markdown artifact family distinct from workbook.
6. **Murat evidence:** shared `runs/<uuid>/` OK; **six** `evidence/<item-slug>/verdict.json` stamps required. Live-consumer predicates, not file-existence theater.

---

## Sequencing (binding)

```
Track A (spine):     1 (auto selection) ──► 2 (interactive SPOC REPL)
Track B (source):    4 (canonical structure) ──► 5 (drill) ──► 6 (prose uplift)
Track C (SME):       3 (per-SME voice) ──► (hard gate into) 6
```

- 1 and 4 may proceed in parallel.
- 5 blocked on 4 shape-pin.
- 6 blocked on 3 (named-variant) + preferably after 5 if same workbook corpus, but 3 is the hard gate.
- 2 after 1 (REPL presents resolved plan / fail-loud selection).

---

## Per-item SUCCESS (minimal) + OUT fences

### 1 — Automatic Lesson_plan
- **IN:** From a real Pass-1 `lesson_plan` with collateral, derive `ComponentSelection` without manual intent file; fail-loud when collateral insufficient; live `runs/<uuid>/` shows selection consumed by compose or trial-start path.
- **OUT:** Interactive REPL (2); Gamma spend; rewriting ratification library.

### 2 — Interactive SPOC
- **IN:** Operator-facing planning dialogue in SPOC path: purpose/audience/LOs/workflow/gap-fill → writes ratification companions → loadable by Irene/plan path; ≥1 logged round-trip in `runs/<uuid>/`.
- **OUT:** Full conversational memory/session OS; re-deriving selection (reads plan/auto path); Gamma.

### 3 — Per-SME voice
- **IN:** SME-keyed resolution for voice/styleguide/attribution/approval; two SME runs diverge on ≥1 attribution/styleguide token; unknown SME hard-fail or marked gap (never silent Tejal).
- **OUT:** Multi-SME UI; ad-hoc edit of approved styleguide records (named variants only).

### 4 — Canonical processed-source
- **IN:** Documented + automated canonical layout; ingestion/normalize produces it; reader checksum/manifest; `kind` present on enrichment nodes (shape-pin for 5).
- **OUT:** Full historical backfill; cloud storage; output projectors (5/6).

### 5 — Drill
- **IN:** Drill projector emits LO-linked drill artifact distinct from workbook; consumer produces non-empty render; schema-validated.
- **OUT:** Full adaptive curriculum; workbook prose (6).

### 6 — Workbook prose uplift
- **IN:** Before/after learner-ready prose with measurable delta; REVOICE path exercised on real workbook sections; SME voice from (3) honored where applicable.
- **OUT:** Full S8 reopen; structural plumbing belonging to 1–5.

---

## Negative tests (Murat — binding)

1. Missing/insufficient collateral → fail-loud, not silent default  
2. Malformed REPL input → error logged, no hang  
3. Unknown SME → hard fail / marked gap, no silent Tejal  
4. Incomplete canonical tree → structured error, not partial-success claim  
5. Empty drill source → empty + warning, not silent zero-byte success  
6. Double uplift → idempotent  

---

## Party concurrence

| Seat | Verdict |
|------|---------|
| John | GO-WITH-AMENDMENTS (split 2/4; 4 before 1&5 — **orchestrator softens 4→1** per Winston: 4→5 hard, 1∥4) |
| Winston | GO-WITH-AMENDMENTS (Option A; 4→5; 3→6; 1→2) |
| Amelia | GO-WITH-AMENDMENTS (operator gates on 3/4/5 — defaults proposed above) |
| Murat | GO-WITH-AMENDMENTS (per-item liveproof + six stamps) |

**Orchestrator:** Proceed under Winston ordering + John split discipline + Amelia defaults + Murat bars.
