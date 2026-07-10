# Phase-2 Evolutionary Claim Envelope — 2026-07-09

**Branch:** `dev/lesson-planning-2026-07-09`  
**Party:** John / Winston / Amelia / Murat — fully spawned independent seats  
**Verdict:** **GO-WITH-AMENDMENTS** (4/4)  
**Product:** Marcus-SPOC local runtime — not concierge/proofing convenience  
**Do not reopen:** S8; Irene-literal MET; Pass-2 figure/numeral HELR parked  
**Styleguide policy:** never ad-hoc-edit approved registry guides

**Binding vision:** Runs arrive with different types/amounts of source. Ingestion
assesses and tags what is available (and gaps). After eliciting or finding
instructional purpose + audience, Marcus-SPOC holds a lesson-planning
conversation about assets to create, attributes, workflow, and production
gap-fill tradeoffs (synthesize vs wait vs lighter collateral). The ratified
outcome drives `ComponentSelection` → composed local production — not a static
front-door bundle pick.

**SSOT:** `lesson-plan-rationale-platform-positioning-2026-07-07.md` §4 +
`deferred-inventory.md` §Lesson-Plan-as-Rationale Platform (spine
`lesson-plan-directs-production-collateral-to-selection-edge`).

---

## 1. Party verdicts

| Seat | Verdict |
| --- | --- |
| John (PM) | GO-WITH-AMENDMENTS |
| Winston (Architect) | GO-WITH-AMENDMENTS |
| Amelia (Dev) | GO-WITH-AMENDMENTS |
| Murat (TEA) | GO-WITH-AMENDMENTS |

**Consensus:** proceed. Frame as an evolutionary **planning-to-selection bridge**,
not a full lesson-planning platform rebuild.

---

## 2. Claim envelope IN (~6h session)

At close we may claim:

1. **Variable source assessed** — same mechanism on thin (HAI/PHS syllabus
   fixtures) and rich (Tejal curated); assess/tag + gap inventory differ in kind
   or count (not cosmetic filenames).
2. **Purpose + audience** — elicited or confirmed before asset/workflow decisions;
   downstream selection reads that context.
3. **Conversational plan** — Marcus-SPOC lesson-planning conversation produces a
   **ratified** lesson-production plan naming assets, attributes, workflow, and
   gap-fill disposition (`synthesize` | `wait` | `ask_sme/operator` | `lighter_collateral`).
4. **Derivation edge** — ratified plan deterministically maps into existing
   `ComponentSelection` / S8 selection-edge contract (`collateral_selection.py`
   semantics preserved).
5. **Selection delta** — ratification changes ComponentSelection vs
   default/no-tradeoff baseline (before/after artifact).
6. **Compose** — local compose succeeds on the *changed* selection when claiming
   composed production (Murat W5).

---

## 3. FENCED (not this session / not this claim)

- Full lecture-video / real remote HAI·PHS media ingestion as a done criterion
- Filling HAI/PHS containers as a prerequisite (thin fixtures are intentional)
- SME-routing implementation (may *name* `ask_sme` as a gap-fill option only)
- Projector-family buildout
- Broad ingestion/tag robustness hardening beyond what variability proof needs
- Irene Pass-1 signature reshape; S8 reopen; composition DAG semantic churn
- Concierge/proofing convenience paths; styleguide registry ad-hoc edits
- Pass-2 figure/numeral HELR; LO ratification UX beyond minimum elicitation

---

## 4. Existing seams vs missing glue

**Exists:** S7 Phase-2 A–D course-source + gaps; S8 wrapper→catalog→
`ComponentSelection`→runner; Irene `lesson_plan["collateral"]`; SPOC interlocution;
thin vs rich fixtures on disk; composition DAG.

**Missing glue:** SPOC ratification artifact (structured); deterministic
derivation ratified-plan → `ComponentSelection`; front_door/local path preferring
derived selection over static pick; gap-fill vocabulary + traceability; evidence
that thin≠rich paths behave differently.

---

## 5. MUST amendments (binding before specs/code)

1. Story named as next evolutionary spine from
   `lesson-plan-directs-production-collateral-to-selection-edge`.
2. Keep `ComponentSelection` as production selection contract; S8 resolver
   semantics not redesigned.
3. Derivation edge deterministic + testable; Irene = upstream evidence, not
   ratification owner; conversation captures decisions, does not own composition.
4. Dual-path AC: thin fixture + rich Tejal required; Tejal-only = fail DoD.
5. Gap observability + ≥1 gap-fill tradeoff witness in SPOC evidence.
6. Selection delta AC (before/after); no delta ⇒ claim fails even if compose OK.
7. Claim fence in story header: does **not** claim full lecture ingestion.
8. Shadow-monitor: every open ledger item = fix / defer-with-ticket / false-alarm
   before done.
9. **Gate mode:** dual-gate for the first story that claims interlocution +
   selection delta + compose (Murat; Amelia single-gate only if a pure
   plumbing-only split story — default this session = dual-gate spine story).
10. BMAD path: **`bmad-create-story` → `bmad-dev-story`** (not quick-dev).
11. Trigger-path discipline: prefer `app/marcus/lesson_plan/**`,
    `app/marcus/cli/front_door.py`, focused tests; stop and invoke pipeline
    regime if touching manifest/HUD/runner pack paths.

---

## 6. Witness matrix (Murat — minimum)

| ID | Witness | Pass |
| --- | --- | --- |
| W1 | Thin source (HAI/PHS) | assess/tag + gaps (or explicit justified empty) |
| W2 | Rich source (Tejal) | assess/tag + gaps differ in kind/count from W1 |
| W3 | Gap-fill tradeoff | ≥1 SPOC tradeoff presented + choice recorded |
| W4 | Selection delta | ComponentSelection before ≠ after ratification |
| W5 | Compose | local compose on changed selection |

Done for evolutionary claim: **W1–W4** minimum; **W5** required to claim composed
local production.

---

## 7. Disposition of Phase-2 residuals

| Item | Disposition |
| --- | --- |
| LO/purpose residue | Minimum elicitation IN; full ratification UX FENCED |
| SME-routing residue | FENCED (name option only) |
| Projector family | FENCED |
| Ingestion/tag robustness | Rely on substrate; only what variability proof needs |

---

## 8. Recommended slice shape (Winston + Amelia)

One dual-gate spine story (~6h if held):

- Ratification artifact at Marcus-SPOC lesson-planning boundary
- Adapter: ratified collateral decision → `ComponentSelection`
- Route via existing S8 selection runner; front_door may prefer derived selection
- RED-first tests: Tejal rich + HAI thin + PHS thin (no auto video-fill)
- Live SPOC transcript witness

Likely paths (Amelia sketch): `source_assessment.py`, `planning_conversation.py`,
`front_door.py` adapter, tests under `tests/marcus/lesson_plan/`.

---

## 9. Done-bar (party close)

Fully spawned BMAD party concurs when: story/spec matches this envelope; MUST
fences present; W1–W4 (and W5 if compose claimed) banked; shadow-monitor acted;
no S8 reopen; no styleguide registry mutation; Marcus-SPOC remains the product
target; COMPLETE or COMPLETE-with-named-fenced residuals only.

---

## 10. Canonical evolution rule (operator-ratified 2026-07-09)

SSOT detail: `lesson-plan-rationale-platform-positioning-2026-07-07.md` §4.1.

This bridge is **durable foundation**. Today's coarse catalog+gap-fill choice is
the spine; future work grows vocabulary/options (workflows, plan richness,
specialists, asset attributes) so the same ratification pattern feels like
**commissioning bespoke lessons**. Conversational Marcus-SPOC sits **on top** of
this contract — it must not invent a parallel selection engine. Replaceable:
scripted-recorder UX only.
