# Shadow Monitor — Planning-context → Irene Pass-1 handoff (2026-07-09)

**Arc:** Step 2→3 — purpose·audience·LOs·source assessment → Irene Pass-1 → lesson_plan → downstream  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Story:** `planning-context-to-irene-pass1-handoff.md`  
**Baseline:** `5be7de46`  
**Rule:** every open finding = fix / defer-with-ticket / false-alarm before done.  
**Operator standing rule:** live-test each major component as created (not late bolt-on).

---

## POLL-000 — Arc activated → CLOSED

**Status:** CLOSED after dual-gate review remediation + per-component live-tests.

**Watchpoints dispositioned:**
- Prompt-substring-only false green → FIXED (BH-4 scrub + receipt)
- Soft receipt always-true → FIXED (touch/support/missing split)
- Corpus replacement / hash drift → PINNED
- Fail-loud total-ignore → IMPLEMENTED (absent = zero touch)
- Scope creep → FENCED in PROOF
- Absent path → PINNED
- Skipping per-component live-test → BANKED under `evidence/.../per-component/`

## Live-test ledger

| Component | AC | Status | Evidence |
| --- | --- | --- | --- |
| PlanningContext loader | H1 | GREEN | `01-loader-H1.txt` (9) |
| Runner thread | H2 | GREEN | `02-runner-H2.txt` (4) |
| Prompt + receipt + fail-loud | H3/H5 | GREEN | `03-…txt` (10) |
| Absent path + corpus pin + continuity | H4/H6 | GREEN | same + strip regression |

## Finding log

| ID | Sev | Status | Note |
| --- | --- | --- | --- |
| BH-1 / ECH-03 | HIGH | FIXED | SpecialistDispatchError wrap |
| BH-2 / ECH-01/04/05 | HIGH | FIXED | stopwords + touch heuristic |
| BH-3 / ECH-07 | MED | FIXED | conflict fail-loud |
| BH-4 | MED | FIXED | scrub from envelope JSON |
| BH-5 | MED | FIXED | consumer-shaped continuity |
| ECH-06 | HIGH | FIXED | skip ignore on format fallback |
| ECH-09 | MED | FIXED | receipt file before raise |
| ECH-08/10/12 | MED/LOW | DEFER | ratification-embedded LOs; non-str coerce; runs_root None — out of claim fence |
