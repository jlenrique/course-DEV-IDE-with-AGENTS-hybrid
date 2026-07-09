---
title: 'Phase-2 evolutionary bridge: assessed source → purpose/audience → conversational plan/gap-fill → ComponentSelection'
type: 'feature'
created: '2026-07-09'
status: 'done'
story_key: 'phase2-evolutionary-planning-to-selection-bridge'
gate_mode: 'dual-gate'
baseline_commit: '1f48fbf6'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md'
  - '{project-root}/_bmad-output/implementation-artifacts/claude-shadow-monitor-phase2-evolutionary-2026-07-09.md'
  - '{project-root}/_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/_bmad-output/implementation-artifacts/s8-planning-input-selection-contract-2026-07-08.md'
  - '{project-root}/_bmad-output/implementation-artifacts/s7-phase2-story-d-close-record-2026-07-08.md'
---

<!-- Party green-light 2026-07-09 (fully spawned BMAD seats):
     Round-1 claim envelope: John/Winston/Amelia/Murat = 4/4 GO-WITH-AMENDMENTS.
     Round-2 story AC review: 4/4 GO-WITH-AMENDMENTS — MUST amendments FOLDED below.
     Binding claim envelope: phase2-evolutionary-claim-envelope-2026-07-09.md
     Impasse: Quinn → John → human.
     BMAD path: bmad-create-story → bmad-dev-story (not quick-dev).
     Gate: dual-gate (interlocution + selection delta + compose claim).
     Operator rule: party consensus + orchestrator agree = approval (no Checkpoint-1 hold). -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Course-content development runs arrive with **different types and amounts of source**. The platform already has course-source assessment/gaps (S7 Phase-2 A–D), Irene collateral, SPOC interlocution, and an S8 selection edge (`RatifiedLessonPlanCollateralIntent` → catalog → `ComponentSelection`). What is missing is the **evolutionary glue**: assess/tag available material → elicit or find instructional purpose + audience → Marcus-SPOC **lesson-planning conversation** about what assets to create, their attributes, which workflow, and **production gap-fill tradeoffs** (synthesize vs wait vs ask operator/SME vs lighter collateral) → a **ratified** outcome that **drives** `ComponentSelection` → composed local production — not a static front-door/`--bundle` pick.

**Approach:** Land a thin planning-to-selection bridge on Marcus-SPOC that (1) summarizes assessed source + gaps from existing substrate, (2) captures purpose/audience + conversational plan + gap-fill disposition into a structured ratification artifact, (3) derives a catalog-blessed `ComponentSelection` via the **existing** S8 resolver (no semantic redesign), and (4) proves thin≠rich variability with fixtures already on disk. Conversation captures decisions; it does not own composition.

**Claim fence:** This does **not** claim full lecture-video / remote HAI·PHS media ingestion, SME-routing implementation, projector-family buildout, Irene Pass-1 signature reshape, S8 reopen, or Pass-2 figure/numeral HELR.

## Boundaries & Constraints

**Always:**
- Product target = Marcus-SPOC local runtime (not concierge/proofing convenience).
- Keep `ComponentSelection` + S8 `resolve_lesson_plan_collateral_selection` / `load_lesson_plan_collateral_selection` semantics intact; derive via ratified intent / catalog, do not invent a parallel selection engine. **Zero behavior change** to `_bundle_from_intent` / catalog match rules — tests may pin compatibility only.
- `planning_ratification.py` is a **lightweight decision/artifact recorder**, not a new planning workflow engine or second orchestrator.
- Dual-path proof is **AND** (not OR): thin (HAI 510 **and** PHS 620 syllabus fixtures both exercised) **and** rich (Tejal curated, e.g. `tejal-c1m1-p4-assessments-bridge`); any path skipped = fail DoD (anti Tejal-only false green).
- Gap-fill vocabulary closed this slice: `synthesize` | `wait` | `ask_operator` | `ask_sme` | `lighter_collateral` (names only for SME — no routing impl). Tradeoff witness must be **structured** (chosen + ≥1 considered alternative, or explicit `none` sentinel) — Completion Notes prose alone insufficient.
- Ratification artifact must be loadable as (or emit) `RatifiedLessonPlanCollateralIntent` with `ratification_status: ratified` so trial start `--lesson-plan-collateral-intent` / `_resolve_start_component_selection` precedence already works (ratified > `--bundle` > default). Companion ratification record OK **only if** it also emits the canonical S8 intent (no drifting dual contracts).
- Selection **delta** required as a **machine-checkable artifact** (named path/fields: before vs after `bundle_id` / `ComponentSelection`); no delta ⇒ claim fails even if compose succeeds.
- Live-test each authored/edited component as built; bank Murat witnesses W1–W4. **W5 compose is stretch/diagnostic** unless explicitly claimed in close — do not block 6h bar on W5.
- Shadow-monitor ledger is a **hard Gate-2 DoD input** (`claude-shadow-monitor-phase2-evolutionary-2026-07-09.md`); “tests green, monitor deferred” = not done.
- Named styleguide variants only — never ad-hoc-edit approved registry guides.
- Inventory spine name: `lesson-plan-directs-production-collateral-to-selection-edge`.
- Hard exclusions (Dev Notes + ACs): **no** projector family, **no** Irene Pass-1 reshape, **no** SME routing implementation, **no** S8 redesign.

**Ask First:**
- Changing `ComponentSelection` model fields (additive only if party re-approves).
- Touching `state/config/pipeline-manifest.yaml`, HUD, workflow_runner, or pack paths (invoke pipeline regime).
- Expanding gap-fill enum beyond the closed set above.
- Implementing SME styleguide/voice routing or a second projector kind.
- Replacing interlocutor gate REPL with a full pre-start conversational product surface beyond the thin ratification capture this story needs.

**Never:**
- Redesign S8 resolver / reopen S8 claim letter.
- Require filling HAI/PHS containers with lecture video as a prerequisite.
- Silent static bundle pick renamed as “planning.”
- Mock ComponentSelection in liveproof instead of driving it from ratified artifact.
- Concierge-only convenience paths; styleguide registry in-place mutation.
- Claim “full lecture ingestion proven” or “all source types covered.”

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Thin source assess | HAI or PHS course-source scan / input bundle | Tags + non-empty gap ledger (or explicit justified empty); differs from Tejal | Fail loud if assess collapses to Tejal-shaped fake richness |
| Rich source assess | Tejal curated corpus / planning context | Assess/tag + gaps differ in **kind or count** from thin | Cosmetic filename-only diff = fail AC |
| Purpose/audience | Operator/SPOC supplies or confirms | Stored on ratification artifact; selection path can read it | Missing purpose/audience blocks ratification (fail loud) |
| Gap-fill tradeoff | Thin source + workbook-capable ask | ≥1 tradeoff presented; choice recorded (`synthesize`/`wait`/`ask_*`/`lighter_collateral`) | Unrecorded choice = fail W3 |
| Lighter collateral | Thin + choose `lighter_collateral` or omit workbook | Ratified intent resolves to catalog bundle **without** workbook (e.g. `narrated-deck-with-motion` or `narrated-deck`) | Must not silently force workbook |
| Rich → workbook path | Tejal + choose present workbook collateral | Ratified intent resolves to `narrated-deck-with-workbook` (or equivalent catalog match) | Conflict with explicit opposing `bundle_id` = fail loud (S8 rules) |
| Selection delta | Same thin fixture, two dispositions | Before/after `ComponentSelection` differ | No delta = fail W4 |
| Precedence | Ratified intent + `--bundle` disagree | Existing S8/trial conflict rules; ratified path wins when valid | Do not weaken conflict checks |
| Unratified / absent | No ratification artifact | Fall through to `--bundle` / default (existing behavior) | Do not invent auto-ratify |
| Compose (optional claim) | Changed selection | Local compose / trial start threads `component_selection` | Compose-on-wrong-selection is not a substitute for W4 |

</frozen-after-approval>

## T1 Readiness

- [x] Claim envelope party 4/4 GO-WITH-AMENDMENTS banked
- [x] Shadow-monitor ledger opened
- [x] Seam map: `collateral_selection.py`, `front_door.py`, `trial._resolve_start_component_selection`, `LessonPlanningInputBundle`/`GapLedger`, SPOC interlocutor (post-start) vs pre-start gap
- [x] Dual-gate designated
- [x] Required readings: claim envelope, positioning §4, S8 planning-input contract, Story D close, deferred-inventory spine entry
- [ ] Dev agent re-reads claim envelope + this story before code
- [ ] Shadow-monitor POLL after story author (this file) — disposition any findings before RED

## Code Map (target)

| Area | Path | Role |
|------|------|------|
| Source assessment summary | `app/marcus/lesson_plan/source_assessment.py` (NEW) | Thin adapter over course-source scan / input-bundle gaps → tags + gap summary for planning |
| Planning ratification | `app/marcus/lesson_plan/planning_ratification.py` (NEW) | Purpose/audience + assets/attributes/workflow + gap-fill → emit `RatifiedLessonPlanCollateralIntent` (or YAML writer) |
| Optional CLI/helper | `scripts/utilities/` or `app/marcus/cli/` thin entry | Scripted ratification for liveproof (not a second orchestrator) |
| Selection (EXISTING) | `app/marcus/lesson_plan/collateral_selection.py` | **Do not redesign** — consume ratified intent |
| Trial precedence (EXISTING) | `app/marcus/cli/trial.py` `_resolve_start_component_selection` | Prefer ratified intent; may add thin helper only |
| Front door (EXISTING) | `app/marcus/cli/front_door.py` | Remains fallback when no ratified artifact |
| Course-source (EXISTING) | `app/marcus/course_source/*` | Gaps/manifests/input bundles as evidence |
| Tests | `tests/marcus/lesson_plan/test_source_assessment.py` (NEW), `tests/marcus/lesson_plan/test_planning_ratification.py` (NEW), extend `test_collateral_selection.py`, `tests/integration/marcus/test_trial_cli.py` | RED-first dual-path + delta |

## Tasks & Acceptance

### AC-P2-1 — Source assessment (variable source) — dual-path AND
**Given** thin HAI **and** thin PHS fixtures **and** rich Tejal corpus on disk  
**When** assessment runs for each  
**Then** machine-checkable tags + gap summary exist for all three; thin≠rich in kind or count  
**And** skipping any of the three paths = fail DoD  
**And** no requirement to add lecture video files  

### AC-P2-2 — Purpose + audience on ratification
**Given** operator/SPOC supplies purpose and audience  
**When** ratification artifact is written  
**Then** both fields are present and readable by the selection/planning path  
**And** missing either blocks ratification (fail loud)  
**And** ratification without prior source assessment fails loud

### AC-P2-3 — Conversational plan + gap-fill disposition (structured)
**Given** assessed gaps and purpose/audience  
**When** planning ratification runs (scripted SPOC/HIL witness acceptable this slice)  
**Then** artifact records assets-to-create / attributes / workflow choice **and** a structured gap-fill tradeoff (`chosen` + `considered[]` or `none` sentinel) from the closed vocabulary  
**And** SME appears only as `ask_sme` option name (no routing)  
**And** Completion Notes prose alone does not satisfy this AC

### AC-P2-4 — Derivation via existing S8 edge (frozen resolver)
**Given** a ratified artifact that emits canonical `RatifiedLessonPlanCollateralIntent`  
**When** `load_lesson_plan_collateral_selection` / trial start intent path runs  
**Then** `ResolvedCollateralSelection.source == "ratified"` and `selection` is catalog-blessed  
**And** S8 resolver semantics unchanged — pin with compatibility tests; **do not modify** `_bundle_from_intent` behavior  
**And** missing intent falls back to `--bundle` / front_door / default; malformed intent fails loud

### AC-P2-5 — Selection delta artifact (anti theater)
**Given** the same thin fixture with two different gap-fill/plan choices  
**When** both are ratified and resolved  
**Then** a machine-checkable selection-delta artifact records before/after `bundle_id` and/or `ComponentSelection` and they differ  
**And** missing/empty/identical-when-change-required delta = fail  
**And** evidence package includes the delta artifact path

### AC-P2-6 — Dual-path liveproof witnesses (Murat W1–W4; W5 stretch)
**Given** evidence dir under `_bmad-output/implementation-artifacts/evidence/`  
**When** story claims done  
**Then** W1 thin (HAI+PHS), W2 rich (Tejal), W3 tradeoff, W4 delta are banked with named artifact paths  
**And** W5 compose is optional stretch unless close explicitly claims composed local production  
**And** Tejal-only or any single-path package = fail DoD

### AC-P2-7 — Shadow-monitor + claim-fence negative
**Given** the evolutionary shadow ledger  
**When** close is requested  
**Then** every open finding is fix / defer-with-ticket / false-alarm (monitor absence = not done)  
**And** an automated/contract check rejects over-claim signals for “full lecture ingestion” / “lecture-complete selection”  
**And** story header claim fence remains true

## Dev Notes

- Prefer composing `LessonPlanningInputBundle.gap_ledger` + `component_selection` into ratified intent over inventing a parallel schema; extend only if purpose/audience/gap-fill cannot ride provenance fields without lying.
- If purpose/audience/gap-fill need structured fields beyond current `RatifiedLessonPlanCollateralIntent`, prefer an **additive companion** ratification record that **emits** the closed S8 intent for the runner — do not fork selection. Never let two intent records drift.
- `planning_ratification` = recorder only; do not grow a planning workflow engine.
- **Hard no:** projector family, Irene Pass-1 reshape, SME routing implementation, S8 redesign, full lecture ingestion as DoD.
- Liveproof may use scripted confirm_fn / AFK HIL class already authorized for SPOC; not `--auto-confirm-directive` silent.
- Trigger paths: stay in `app/marcus/lesson_plan/**`, thin CLI, tests. Stop if pipeline-manifest regime paths appear.
- First RED tests (Amelia): thin HAI classify, thin PHS classify, Tejal rich classify, ratification requires assessment, emits selection delta, rejects missing delta, S8 resolver frozen pin.

## Definition of Done

- All AC-P2-1..7 green with evidence
- `bmad-code-review` completed; MUST-FIX remediated; re-live-tested
- Dual-gate party close concurs COMPLETE or COMPLETE-with-named-fenced residuals
- Inventory spine entry updated (MET or partial-MET with honest residual)
- STATE / project-context / claim envelope close note updated
- No S8 reopen; no styleguide registry mutation

## Close Record (2026-07-09)

**Party CLOSE:** John CONCUR · Winston CONCUR-W-FINDINGS · Amelia CONCUR-W-FINDINGS · Murat CONCUR  
**Disposition:** **COMPLETE-with-named-fenced-residuals**

**Landed:**
- `app/marcus/lesson_plan/source_assessment.py`
- `app/marcus/lesson_plan/planning_ratification.py`
- Tests: 16 passed (`test_source_assessment` + `test_planning_ratification`)
- Evidence: `_bmad-output/implementation-artifacts/evidence/phase2-evolutionary-bridge-20260709T204500/` (W1–W4)
- S8 resolver frozen; front_door fallback preserved
- Shadow-monitor dispositioned

**Named residuals (fenced):**
- F-P2-005 interactive pre-start SPOC planning REPL
- Automatic Irene-collateral→selection without ratification recorder
- W5 compose liveproof
- SME routing / projector family / full LO ratification UX / full lecture ingestion

**Does not claim:** full lecture ingestion; lecture-complete selection; Phase-2 program 100% closed.

**Canonical evolution rule:** see positioning SSOT §4.1 — this contract is durable foundation; conversational Marcus-SPOC and richer/bespoke option space grow *on top* of it (not a parallel selection engine).
