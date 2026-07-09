---
title: 'Planning-context → Irene Pass-1 handoff (purpose/audience/LOs/source assessment)'
type: 'feature'
created: '2026-07-09'
status: 'done'
story_key: 'planning-context-to-irene-pass1-handoff'
gate_mode: 'dual-gate'
baseline_commit: '5be7de46'
context:
  - '{project-root}/_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md'
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md'
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-planning-to-selection-bridge.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<!-- Party green-light 2026-07-09 Step 2→3 (fully spawned BMAD seats):
     John / Winston / Amelia / Murat = 4/4 GO-WITH-AMENDMENTS.
     MUST amendments FOLDED below. Impasse: Quinn → John → human.
     Operator rule: party consensus + orchestrator agree = approval.
     Do not reopen S8; do not rebuild step-1 selection bridge. -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Purpose, audience, LOs, and source assessment can be elicited/recorded (G0R `ratified-los.json`, Phase-2 `planning-ratification.json`), but Irene Pass-1 still plans almost exclusively from `extracted.md`. Structured planning context does not reach Irene; `ratified-los.json` is largely orphaned.

**Approach:** Thread optional structured **`planning_context`** into Irene Pass-1 (runner context + labeled prompt section). Merge on-disk artifacts per rules below. Corpus (`extracted.md`) remains the ONLY topic/source-of-truth; planning context is framing/emphasis. Downstream continues via existing `lesson_plan` → `run.json` / package-builder paths. No parallel selection engine (§4.1).

**Claim fence:** Does not claim interactive SPOC planning REPL, full lecture ingestion, SME routing, projector family, or full compose liveproof. Does not redesign S8 / rebuild step-1 bridge. Does not replace corpus grounding.

## Party decisions (binding)

- **LO ignore policy:** Soft coverage receipt ALWAYS emitted when context present. **Fail-loud** if context carries non-empty LOs and emitted plan has **zero** LO overlap (total ignore) or empty `plan_units`. Partial coverage = receipt documents supported/weak/missing — generation may proceed.
- **Merge:** `ratified-los.json` authoritative for LO list when non-empty; `planning-ratification.json` authoritative for purpose/audience/source assessment. Empty must not overwrite present. Conflicting non-empty purpose/audience → fail loud.
- **Downstream done-bar THIS session:** pin continuity + scoped liveproof (prompt+plan+receipt+package-builder continuity) — NOT full asset compose liveproof.
- **Honesty:** prompt presence alone is insufficient; plan/receipt must show context was considered (or fail-loud on total ignore).

## Boundaries & Constraints

**Always:**
- Marcus-SPOC product path only; additive optional key; absent = today’s behavior.
- Corpus primary; planning_context advisory framing only (Winston).
- Read `planning-ratification.json` and/or `ratified-los.json` from run_dir.
- Dual-gate; **live-test each major component as it is created** (loader → runner → prompt/receipt → absent/corpus pin) before moving on — not one late suite only.
- Shadow-monitor acted.
- Never ad-hoc-edit approved styleguide guides.

**Never:**
- Metadata-receipt-only / prompt-substring-only done claim.
- Parallel selection engine; S8 reopen; step-1 rebuild.
- Silent drop of provided LOs when context present.
- Interactive REPL; full lecture ingestion claim; full compose as DoD.

## I/O & Edge-Case Matrix

| Scenario | Expected |
|----------|----------|
| No artifacts | Irene unchanged; no planning_context key required |
| Ratification only | purpose/audience/assessment loaded; LOs empty OK |
| ratified-los only | LOs loaded; purpose/audience optional empty |
| Both | merge per party rules |
| Context + LOs + plan ignores all LOs | fail-loud |
| Context + partial LO coverage | soft receipt; proceed |
| Malformed JSON | fail loud |
| Corpus after handoff | bytes/hash unchanged |

</frozen-after-approval>

## T1 Readiness

- [x] Step 1 bridge closed `20246475` / `5be7de46`
- [x] Party 4/4 GO-WITH-AMENDMENTS folded
- [x] Dual-gate
- [x] Shadow-monitor activated
- [ ] Dev re-reads this story before code

## Code Map

| Area | Path |
|------|------|
| NEW | `app/marcus/lesson_plan/planning_context.py` |
| Runner | `app/marcus/orchestrator/production_runner.py` `_runner_payload_for_specialist` |
| Contract | `app/specialists/irene_pass1/payload_contract.py` |
| Prompt + receipt | `app/specialists/irene_pass1/_act.py` |
| Tests | `tests/marcus/lesson_plan/test_planning_context.py`, `tests/specialists/irene_pass1/test_planning_context_handoff.py` |

## Acceptance Criteria

### AC-H1 — PlanningContext loader
Load/merge from run_dir; rules above; malformed fail loud; absent → None.

### AC-H2 — Runner threads irene_pass1 only
`planning_context` in runner payload when loadable; other specialists unchanged.

### AC-H3 — Prompt surfaces labeled context
Stable section marker; corpus remains ONLY topic basis; explicit “framing not corpus” wording.

### AC-H4 — Absent path unbroken
No artifacts → no raise; no required context section; corpus path unchanged.

### AC-H5 — Soft coverage receipt + fail-loud total ignore
When context present: emit structured receipt (`present`/`partial`/`absent` LO coverage). Fail-loud on total LO ignore when LOs non-empty.

### AC-H6 — Downstream continuity + corpus immutability
`lesson_plan` still resolvable by package_builder / lesson_plan-from-run patterns; corpus hash pin in tests; no full-compose DoD.

### AC-H7 — Claim fence
Evidence/story state: no REPL / full lecture ingestion / S8 redesign claims.

## Definition of Done

AC-H1..H7 green; dual-gate party close; shadow-monitor dispositioned; inventory `course-purpose-and-operator-owned-lo-inputs` updated for Pass-1 signature slice; STATE/project-context updated; commit+push.

## Completion Notes (2026-07-09)

- Party green-light 4/4 GO-WITH-AMENDMENTS folded; dual-gate review remediated (BH-1..5, ECH-01/03/06/07/09).
- Per-component live-tests banked under `evidence/irene-planning-context-handoff-20260709T180555/per-component/`.
- Party CLOSE: COMPLETE-with-named-fenced-residuals (ECH-08/10/12).
- Claim fence held.
