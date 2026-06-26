# Story G0-S3 — Irene Refinement Loop + Ratify-Gate #2 + Completeness Assert

**Epic:** G0 Source-Content Enrichment (v1) — `_bmad-output/planning-artifacts/epics-g0-enrichment.md`
**Authority:** `lo-schema-ratification-2026-06-26.md` §3 (signed LO-delta contract — ALL channels), §3.1 (adequacy is ADVISORY — verdict never gates), §2 (advance_lo: irene moves provisional→refined, NEVER ratified), §5 (S3 rewires the LO refiner natively). Charter: the Irene refinement loop is the operator's NON-NEGOTIABLE v1 requirement.
**Class:** S · **Type:** brick (Irene refinement node + ratify-gate) · **Gate mode:** single-gate · **Status:** ready-for-dev (blocked by S2 commit; integration points marked "confirm vs S2 as-built")
**Closes:** A5, A8, A9 (consumer side), A11 + the operator-mandated Irene refinement loop. **Depends on:** S1 (the LO entity + `advance_lo`) + S2 (provisional LOs at gate #1, the gate/two-walk pattern, the corpus-keyed LLM pre-pass seam).
**Required dev readings (T1):** S2 as-built (the G0-enrichment node + gate #1 + the decision-card + the two-walk wiring — MIRROR this pattern for gate #2); `app/specialists/irene_pass1/_act.py` (current Pass-1 — emits a bare `learning_objective` string at ~L171; S3 rewires it to consume/produce the canonical entity); `[[project_production_runner_two_walks]]`; ratification §3/§3.1.

## Goal
After gate #1 confirms the typed manifest + provisional LOs, **Irene inspects the live full source AGAINST those LOs**, refines them in place (`provisional→refined`), produces a per-LO **source-content adequacy ALERT** (advisory), and emits the **signed LO-delta contract** back to Marcus-SPOC. Marcus re-presents the refined plan + LO-delta + adequacy report at **operator ratify-gate #2**; the operator's verdict moves `refined→ratified`. A **completeness hard-assert** (access + assessment-presence, NOT adequacy outcome) gates progress to lesson-planning / hand-off-to-Gary.

## Acceptance Criteria

### AC-S3-1 — Irene refines provisional→refined IN PLACE (native consumer rewire)
Rewire the LO refiner (`app/specialists/irene_pass1`) to CONSUME the gate-#1-confirmed provisional `LearningObjective`s (not a bare string) and emit refined ones via `advance_lo(lo, "refined", actor="irene")`. Refinement is IN PLACE (status transition on the same `objective_id` — immutable id carried through), NOT a parallel set. Reconciliation is by STATUS, never by merge/deletion. Populate `bloom_level` at refine (not gated until ratified). Reuse the S2 corpus-keyed LLM pre-pass seam (`make_chat_model("marcus")` / the conversational-gates template pattern); offline guard for tests. Irene physically has no code path that sets `ratified` (S1 guard).

### AC-S3-2 — Per-LO SourceAdequacy is produced — ADVISORY, never a blocker (§3.1)
For each refined LO, Irene produces `SourceAdequacy{verdict, rationale (quotes the span), missing (concrete on thin/gap), suggested_followups}`. Verdict rubric: `adequate` = teach-leg AND assess-leg both supported by `source_refs`; `thin` = one leg partial (assess-leg is the discriminator); `gap` = below the teachable floor. **The verdict value NEVER halts the pipeline, forces a drop, or gates a transition** — it is an ALERT for the operator + off-world SME (final adequacy call is theirs; content may come from outside the app). A `thin`/`gap` MAY set `suggested_followups` (research-run / external-content-expected / special-artifact-guidance). RED-first: a run with a `gap` LO still advances to gate #2 (not blocked); the assert in AC-S3-5 does not fail on a gap verdict.

### AC-S3-3 — Signed LO-delta contract (all channels) emitted to Marcus-SPOC
Emit the ratified §3 contract as a reconcilable ledger, per `objective_id`: (a) refined LO + `provisional→refined` transition; (b) source-tied rationale diff per CHANGED LO (citing `SourceRef` provenance; provenance-less diff rejected pre-surface); (c) per-LO `SourceAdequacy`; **(+d) disposition code** ∈ {refined-in-place, unchanged, split→[ids], merged←[ids], flagged-inadequate, proposed-new, recommend-drop} — exactly one per id, **NO silent drops** (a returned id with no disposition is a BLOCK); **(+e)** carry-through of the frozen G0 fields + immutable `objective_id` (a mutated id/frozen field = provenance break). **PROPOSE-NEW channel:** source teaches something assessable the provisional set missed → new LO at `status=provisional`, `origin="irene-proposed"`, with `source_refs` (Irene cannot self-promote it to refined). **RECOMMEND-DROP channel:** source can't support a provisional LO → held `provisional` + `adequacy.verdict="gap"` + `recommendation="drop"` (Irene never deletes; operator executes). **Count reconciliation:** G0_count reconciles to Irene_count via the disposition ledger (split/merge/new/drop are explained deltas). RED-first tests for each channel + the no-silent-drop invariant + the reconciliation.

### AC-S3-4 — Ratify-gate #2 wired into BOTH walks (mirror S2 gate #1)
Register a ratify-gate (gate_code e.g. "G0R") after the Irene-refinement node; Marcus-SPOC `narrate_gate` re-presents the refined plan + LO-delta + adequacy report (with the count reconciliation + any `recommend-drop`/`proposed-new` flagged for the operator's call). Operator verdict → `advance_lo(lo, "ratified", actor="operator")` in the gate handler. **Wire the gate side-effect into BOTH `run_production_trial` AND `_continue_production_walk`** (reachable via resume + recover) — mirror S2's exact two-walk pattern. **A8:** the ratify handler never overturns/re-stamps an operator's prior ratification unilaterally — a touched prior-ratified LO requires explicit operator re-confirm (do NOT lean on `advance_lo` idempotency to satisfy A8 — that S1 NIT was deferred here). Deterministic guard: the model never auto-ratifies.

### AC-S3-5 — Completeness hard-assert (ACCESS + ASSESSMENT-PRESENCE, not adequacy outcome)
Before hand-off to lesson-planning/Gary: assert every source span is typed-or-`ignored` (operator-confirmed); every LO (all non-dropped) has ≥1 **resolvable** `SourceRef` AND a **populated** adequacy verdict (assessed, not silently absent); any **unreachable** source = RED (A1). **A `thin`/`gap` adequacy verdict does NOT fail the assert** — the run proceeds (§3.1). RED-first: a missing adequacy assessment fails; an unreachable source fails; a `gap` verdict passes.

### AC-S3-6 — Refined lesson plan returned for iteration; regression + blast-radius
Irene bakes the refined LOs + adequacy into her refined lesson plan, returned to Marcus-SPOC (the existing G1 lesson-plan flow consumes the ratified LO entities — rewire the Pass-1→workbook/G1 consumers off the bare string / `LearningObjectiveBrief` per ratification §5; delete the S1 adapter bridge functions whose last consumer is now rewired). Existing G1 / Irene Pass-1 tests pass (updated for the entity). Full suites + ruff + lint-imports green. NO new Gamma/video/audio — the live proof stops at hand-off-to-Gary.

### AC-S3-7 — LIVE-segment proof (no mocks)
A REAL run on a real corpus continues from S2's gate #1 through Irene refinement → adequacy → ratify-gate #2 → completeness assert → poised at hand-off-to-Gary: provisional LOs refined in place; a real adequacy report (incl. at least one non-`adequate` verdict surfaced as a non-blocking alert); the LO-delta ledger reconciles; gate #2 ratifies on operator verdict. Captured as evidence.

## Definition of Done
All ACs green; Irene rewired to the canonical entity (S1 adapter bridge retired where consumed); LO-delta contract emitted with all channels + reconciliation; adequacy advisory (never blocks); ratify-gate #2 in both walks; completeness assert (access + assessment-presence); live-segment proof captured; full suite + ruff + lint-imports green; T11 `bmad-code-review` clean; **full party-close** (substrate-impacting + the operator-mandated loop). NO new expensive assets.

## Integration points to CONFIRM against S2 as-built (do not guess)
- The exact gate/decision-card/narrate_gate API S2 established (mirror it for gate #2).
- Where S2 parks the gate-#1-confirmed provisional LOs in run state (Irene reads them from there).
- The two-walk wiring sites S2 used (add gate #2's side-effect at the same two sites).
- The corpus-keyed cache + offline-LLM-guard helpers S2 created (reuse, don't duplicate).
