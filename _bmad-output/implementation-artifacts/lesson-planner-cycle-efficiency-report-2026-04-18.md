# Lesson Planner Remaining-Stories Efficiency Report

**Date:** 2026-04-18
**Scope:** Production-cycle analysis of Story `31-1-lesson-plan-schema` and Story `31-2-lesson-plan-log`
**Purpose:** Identify the main sources of cycle inefficiency across the first two Lesson Planner MVP stories and define concrete remediations to apply across the remaining stories.
**Sources:** repo-local story artifacts, governance docs, and deferred-work register only. No web research used.

---

## Executive Summary

The first two Epic 31 stories proved that the quality gates are valuable, but they also exposed a repeatable cycle-cost pattern:

1. **Test volume inflated far beyond the declared K floors.**
2. **Too much knowledge was discovered during G5/G6 instead of being front-loaded at T1.**
3. **Foundation-grade ceremony is appropriate for 31-1 and 31-2, but would be wasteful if repeated across the remaining non-foundation stories.**
4. **Scaffold adoption is partially codified but not yet operationalized as a hard precondition.**
5. **Review triage still spends material time on cosmetic noise.**
6. **Parallel pre-work exists, but is not yet being run as a disciplined runway.**
7. **Status and handoff artifacts drifted behind execution, creating avoidable re-orientation overhead.**

The highest-leverage changes to implement now are:

- Enforce **single-gate vs dual-gate** exactly as already defined.
- Enforce **1.2x-1.5x K test targets** unless excess tests carry named coverage justification.
- Make **T1 reading + scaffold instantiation** a hard pre-dev gate for every applicable story.
- Use a **runway queue** so side work starts while a main story is waiting on reviews.
- Treat the deferred-work register as **touch-triggered backlog**, not ambient work that keeps re-entering the active lane.

If applied consistently, the repo's own estimate of roughly **40% cycle-time reduction** across the remaining plan is credible.

---

## Review of Prior Analysis

The prior party's 1-pager is strong and materially improves this report in one important way: it converts several of my "implement now" recommendations into **already-landed operational interventions**.

### Where it agrees with this report

- It starts from the same diagnosis: `31-1` ran at roughly **5x** its intended K-floor range.
- It targets the same leverage points:
  - reduce repeat schema-story boilerplate,
  - keep authority boundaries clean,
  - remove pre-work from the `30-1` critical path,
  - compound gains across `31-3`, `29-1`, and `32-2`.

### What it adds beyond this report

It contributes four concrete interventions that are more operational than my first pass:

1. **Sprint-status append-block for Epics 28-32**
2. **Non-authoritative pre-seed relocation for `31-3`**
3. **`30-1` golden-trace capture scaffold split from pipeline wiring**
4. **One-command scaffold instantiator for schema-shape stories**

These are not alternate ideas. They are the missing bridge between "we know the efficient process" and "we can actually run it repeatably."

### My assessment

I accept all four interventions as part of the final plan.

- The **sprint-status append-block** solves story discovery friction.
- The **pre-seed relocation** correctly protects the authority boundary around `bmad-create-story`.
- The **golden-trace scaffold split** is exactly the right way to de-risk `30-1` without waiting for the full refactor story to open.
- The **scaffold instantiator** is the most concrete answer to repeated schema-story boilerplate and directly compounds on the remaining schema-shape stories.

The main thing the 1-pager does **not** replace is the cycle-governance layer already captured in this report:

- K-floor discipline
- single-gate vs dual-gate enforcement
- aggressive G6 DISMISS
- T1 readiness discipline
- deferred-work touch-trigger discipline

So the correct synthesis is: **keep the governance from this report, and operationalize it using the four interventions from the prior analysis.**

---

## Baseline Evidence

### Story 31-1

- 31-1 added **131 tests** at G3, then another **66 passing tests** during the G5/G6 patch cycle, for a total well above its K floor of 25. See [`31-1-lesson-plan-schema.md`](../../_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md) at the regression summary and patch-cycle closure.
- G6 surfaced **6 MUST-FIX**, **12 DEFER**, and **23 DISMISS** findings. See [`31-1-lesson-plan-schema.md`](../../_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md).
- Many of the G6 findings were generalized afterward into the Pydantic checklist and anti-pattern catalog. See [`pydantic-v2-schema-checklist.md`](./pydantic-v2-schema-checklist.md) and [`dev-agent-anti-patterns.md`](./dev-agent-anti-patterns.md).

### Story 31-2

- 31-2 added **+80 collecting tests** by T18 and **+19 more** during G6 hardening, for **+99 collecting tests** against **K=17**. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).
- G6 still produced **6 MUST-FIX**, **10 DEFER**, and **20 DISMISSED** findings. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).
- The story itself states it was authored **before** the new checklist / anti-pattern / cycle-efficiency docs existed, so those lessons were learned mid-flight instead of preloaded. See the "Mid-Flight Memo" in [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).

### Process codification already landed

- The repo already codifies K-floor discipline, single-gate vs dual-gate review, aggressive G6 DISMISS, scaffold reuse, T-task parallelism, and runway pre-work in [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).
- The repo already requires T1 reading of the efficiency doc, anti-pattern catalog, and Pydantic checklist in [`CLAUDE.md`](../../CLAUDE.md).

The problem is no longer "we do not know what efficient looks like." The problem is **operationalizing these rules before the next 19 stories start**.

---

## Findings

## 1. Test-count inflation is the largest repeated cycle drag

**Evidence**

- `31-1` shipped **131 tests against K=25 (5.2x)**; the efficiency doc explicitly says only one extra coverage gap was genuinely justified. See [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).
- `31-2` shipped **+99 collecting tests against K=17**, again clearing the floor by more than 5x. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).
- The anti-pattern catalog explicitly names this as a recurring trap. See [`dev-agent-anti-patterns.md`](./dev-agent-anti-patterns.md).

**Why it slows the cycle**

- More tests means more authoring time, more review surface, more re-run time, and more G6 hardening work.
- Parametrized matrix expansion creates the appearance of rigor while often adding little new failure-mode coverage.

**Remediation**

- Set a hard operating rule for remaining stories: **target 1.2x-1.5x K**.
- If a story exceeds 1.5x K, require a short "coverage justification" note in the Dev Agent Record naming the extra gap per additional ~5 tests.
- Count a parametrized matrix as **one conceptual test** unless it closes a named edge-condition class.

**Implement now**

- Apply this immediately to `31-3`, `29-1`, `32-2`, and all single-gate stories.
- Use the story spec to declare a **planned test range** at T1, not just a minimum K.

## 2. Too much defect discovery happened at G5/G6 instead of T1

**Evidence**

- `31-1` G6 caught real correctness issues that were later distilled into checklist rules: `validate_assignment=True`, tz-aware datetimes, UUID4 validation, no-leak handling, state-machine bypass guards, etc. See [`pydantic-v2-schema-checklist.md`](./pydantic-v2-schema-checklist.md).
- `31-2` explicitly notes those references landed only after the story had already been authored, so the team had to retrofit them mid-flight. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).
- `CLAUDE.md` now requires those references at T1 for Lesson Planner stories. See [`CLAUDE.md`](../../CLAUDE.md).

**Why it slows the cycle**

- Discovering reusable rules during review forces code churn, new tests, new docs, and a second reasoning pass over the same surface.
- The later a rule is discovered, the more files it touches.

**Remediation**

- Treat the T1 doc-read set as a **pre-dev gate**, not a suggestion.
- At T1, the dev agent should explicitly state:
  - which checklist sections apply,
  - which anti-pattern categories are relevant,
  - whether the story is single-gate or dual-gate,
  - whether scaffold instantiation is required.

**Implement now**

- Add a mandatory "T1 readiness checklist" block to every new story spec from `31-3` onward.
- Refuse `bmad-dev-story` start if that block is missing.

## 3. Ceremony is correctly heavy for foundation stories, but must not be copied onto peripheral stories

**Evidence**

- The anti-pattern catalog calls out the trap of treating every story as foundation-tier. See [`dev-agent-anti-patterns.md`](./dev-agent-anti-patterns.md).
- The efficiency doc already classifies the remaining stories into **dual-gate** and **single-gate** lanes. See [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).

**Why it slows the cycle**

- R2 + G5 + G6 is the right price for `31-1` and `31-2`, but not for small, low-risk, precedent-heavy stories.
- If a 2-point story pays full foundation ceremony, process time overtakes implementation time.

**Remediation**

- Follow the repo's own classification exactly:
  - **Dual-gate** only for foundation/refactor/integration stories.
  - **Single-gate** for the peripheral and precedent-heavy stories already named in the efficiency doc.

**Implement now**

- Run `31-3`, `29-1`, `28-1`, `30-2a`, `30-2b`, `30-5`, `32-1`, `32-2`, and `32-4` as **single-gate** stories.
- Reserve full dual-gate cycles for `29-2`, `28-2`, `30-1`, `30-3a`, `30-3b`, `30-4`, `31-4`, `31-5`, and `32-3`.

## 4. Scaffold reuse is defined, but not yet fully operationalized

**Evidence**

- The efficiency doc says schema-shape stories should start from the scaffold and should have pre-instantiated stubs before dev begins. See [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).
- `CLAUDE.md` says the same, naming `31-2`, `31-3`, `29-1`, and `32-2` as scaffold-default stories. See [`CLAUDE.md`](../../CLAUDE.md).
- The scaffold now exists in [`docs/dev-guide/scaffolds/schema-story/`](./scaffolds/schema-story/).
- There is a pre-seed draft for `31-3` in [`_bmad-output/specs/pre-seed-drafts/31-3-registries-PRE-SEED.md`](../../_bmad-output/specs/pre-seed-drafts/31-3-registries-PRE-SEED.md), but the flow is not yet fully automated.

**Why it slows the cycle**

- Re-deriving 31-1 patterns story-by-story recreates the same design and test decisions.
- Mid-flight scaffold adoption is much less effective than starting from stubs that already encode the idioms.

**Remediation**

- Make scaffold instantiation a concrete preparatory step owned by the orchestrator before dev starts.
- For every schema-shape story, pre-create:
  - source stub,
  - parity test,
  - shape-pin test,
  - no-leak test,
  - changelog entry stub.

**Implement now**

- Instantiate scaffold-based stubs before `31-3`, `29-1`, and `32-2`.
- Treat absence of pre-instantiated stubs as a pre-dev blocker for those stories.

## 5. G6 triage still wastes time on low-value cosmetic noise

**Evidence**

- `31-1` dismissed **23 NITs**. See [`31-1-lesson-plan-schema.md`](../../_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md).
- `31-2` dismissed about **20 NITs**. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).
- The efficiency doc already defines an aggressive DISMISS rubric specifically to compress this overhead. See [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).

**Why it slows the cycle**

- Paragraph-level triage on cosmetic findings burns attention that should go to correctness and contract risk.
- NIT churn also inflates patch sets and follow-up commentary.

**Remediation**

- Use only four fast-dismiss labels unless confidence >= 0.7 or correctness is implicated:
  - `DISMISS (cosmetic)`
  - `DISMISS (DRY-noise)`
  - `DISMISS (pragma)`
  - `DISMISS (test-theater)`

**Implement now**

- Make this the default triage format for all remaining G6 passes.
- Do not persist cosmetic dismissals into deferred-work unless they create actual future confusion.

## 6. Parallel pre-work is available but underused

**Evidence**

- The efficiency doc explicitly names side-work opportunities: `30-1` golden-trace baseline capture, and spec skeleton authoring for `29-1`, `32-1`, `32-2`, `32-4`. See [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).
- The repo already contains runway seeds:
  - [`_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md`](../../_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md)
  - [`tests/fixtures/golden_trace/`](../../tests/fixtures/golden_trace/)
  - [`tests/fixtures/trial_corpus/`](../../tests/fixtures/trial_corpus/)

**Why it slows the cycle**

- Waiting on review gates or patch cycles without running independent prep work leaves the next story cold-starting from zero.

**Remediation**

- Maintain a **runway queue** with at least 2-3 ready side tasks at all times.
- Use idle time during reviews to:
  - capture fixtures,
  - author next-story specs,
  - instantiate scaffold stubs,
  - update shared docs from newly discovered findings.

**Implement now**

- Start two side tasks immediately while `31-3` is being authored/implemented:
  - `30-1` golden-trace baseline capture
  - spec/stub preparation for `29-1`

## 7. Deferred-work tail is real, but should be treated as touch-triggered, not ambient scope

**Evidence**

- `31-1` left **12 deferred findings**. See [`deferred-work.md`](../../_bmad-output/maps/deferred-work.md).
- `31-2` left **10 deferred findings**. See [`deferred-work.md`](../../_bmad-output/maps/deferred-work.md).
- Several of these are real but non-blocking hardening items: perf polish, snapshot semantics docs, MappingProxyType hardening, CRLF determinism, etc.

**Why it slows the cycle**

- If deferred findings are mentally carried into every new story, they become constant re-triage overhead.
- Teams lose focus by revisiting non-blocking hardening work unrelated to the active story.

**Remediation**

- Adopt a **touch-trigger rule**:
  - If a story touches a module with deferred findings, re-evaluate only the deferred items relevant to the touched surface.
  - Otherwise, leave them parked.

**Implement now**

- For `31-3`: ignore 31-1/31-2 deferred items unless the story touches the same file or behavior.
- For `30-1`, `30-4`, and `32-2`: review only the log-related deferred items relevant to their touched surfaces.

## 8. Status drift in handoff artifacts causes avoidable re-orientation work

**Evidence**

- `sprint-status.yaml` had the up-to-date truth, but `next-session-start-here.md` and the top status line in the plan doc had already gone stale before they were refreshed.
- `31-2` also flagged status-file edits as operator-adjudicated rather than applied directly during the story cycle. See [`31-2-lesson-plan-log.md`](../../_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md).

**Why it slows the cycle**

- Every stale hot-start document forces a new session to spend time re-validating reality.
- That overhead compounds across a 19-story run.

**Remediation**

- Make `sprint-status.yaml` the explicit source of truth.
- Treat hot-start docs as derived operational aids that must be refreshed at session close if the current objective changed.

**Implement now**

- Add a closeout checklist item: if any story moved to `done`, update:
  - `sprint-status.yaml`
  - `next-session-start-here.md`
  - any top-level plan status line that is now misleading

---

## Recommendations to Apply Immediately

## Priority 1 - Change how the next story starts

Before starting `31-3`:

1. Author the real `31-3` story from the pre-seed draft.
2. Instantiate scaffold-based stubs at target paths.
3. Add a T1 readiness block naming:
   - gate mode: single-gate
   - target test range: `K=8`, target `10-12`
   - checklist sections read
   - anti-pattern categories relevant
4. Start side-work on `30-1` golden-trace capture while `31-3` is in progress.

## Priority 2 - Lock the gate policy

For the remaining stories:

- Use **single-gate** for the stories already designated as single-gate in [`story-cycle-efficiency.md`](./story-cycle-efficiency.md).
- Keep **dual-gate + full G6** only for the explicitly designated high-risk stories.
- Do not "promote" a story to dual-gate out of habit; require a concrete reason.

## Priority 3 - Cap test sprawl

For every remaining story:

- Declare `K` and a target test range at T1.
- Require justification if actual collecting tests exceed 1.5x `K`.
- Prefer boundary-coverage and representative matrices over combinatorial expansion.

## Priority 4 - Make the runway explicit

Maintain a small live queue of side tasks:

- `30-1` golden-trace baseline capture
- `29-1` spec + stubs
- `32-1` spec skeleton
- `32-2` spec skeleton + scaffold prep
- `32-4` walkthrough skeleton

Idle review time should pull from this queue automatically.

## Priority 5 - Stop paying full price for NIT triage

At every remaining G6:

- Fast-dismiss cosmetic findings using the existing rubric.
- Persist only meaningful deferred items.
- Spend review attention on correctness, invariants, performance budgets, and operator-surface behavior.

---

## Final Immediate Plan

This is the merged plan to execute now.

## A. Accept the four prior interventions as active infrastructure

These are now part of the working method, not optional nice-to-haves:

1. **Use `sprint-status.yaml` as the story-discovery source of truth.**
2. **Keep pre-seeds in `_bmad-output/specs/pre-seed-drafts/`, never in the authoritative implementation-artifacts path.**
3. **Treat the `30-1` golden-trace scaffold as pre-work that can run in parallel before `30-1` opens.**
4. **Use `scripts/utilities/instantiate_schema_story_scaffold.py` for schema-shape story stub generation.**

## B. Lock the authority boundary

Effective immediately:

- **Authoritative story specs** are created by the authoritative `bmad-create-story` flow in `_bmad-output/implementation-artifacts/`.
- **Cowork/prep artifacts** stay in non-authoritative locations such as:
  - `_bmad-output/specs/pre-seed-drafts/`
  - `docs/dev-guide/scaffolds/`
  - utility scripts / fixture plans
- No helper or prep script writes into the authoritative story path unless that lane is explicitly the authoritative author.

This keeps the prior party's collision-avoidance rule intact and prevents rework.

## C. Execute the next three work items in two lanes

### Lane 1 — Mainline story lane

1. **Open `31-3-registries` next.**
2. Run it as a **single-gate** story.
3. Before dev starts:
   - instantiate stubs with the scaffold instantiator,
   - carry a T1 readiness checklist,
   - set `K=8`, target test range `10-12`,
   - use the anti-pattern and checklist docs as mandatory inputs.
4. Do not drag 31-1 / 31-2 deferred items into `31-3` unless the touched surface actually overlaps.

### Lane 2 — Parallel prep lane

Run these while `31-3` is in motion:

1. **Finish the `30-1` golden-trace capture pre-work**
   - wire `_run_marcus_pipeline()`
   - capture the baseline fixture
   - commit the manifest/fixture pair before `30-1` opens
2. **Prepare `29-1`**
   - author the spec/pre-seed as needed
   - instantiate scaffold stubs
   - set its T1 checklist and K target in advance

This is the key compounding move: when `31-3` closes, both `29-1` and `30-1` should be warm-started rather than cold-started.

## D. Enforce the remaining-story operating rules

These become mandatory immediately:

1. **Single-gate vs dual-gate**
   - Use the classification already defined in `story-cycle-efficiency.md`.
   - Do not promote a story to dual-gate without a specific risk reason.

2. **K-floor discipline**
   - Default target is `1.2x-1.5x K`.
   - Above `1.5x K` requires explicit coverage justification.

3. **T1 readiness checklist**
   - checklist sections read
   - anti-pattern categories relevant
   - gate mode
   - scaffold requirement
   - target test range

4. **Aggressive G6 DISMISS**
   - one-line dismiss for cosmetic / DRY-noise / pragma / test-theater findings

5. **Deferred-work touch-trigger**
   - review deferred items only when the active story touches the affected module or behavior

## E. Sequence after `31-3`

If the parallel prep lane runs correctly, the next sequence should be:

1. `31-3` closes
2. `29-1` opens immediately as a warm-started single-gate schema story
3. `30-1` opens only after the golden-trace baseline is fully captured and committed
4. `29-2` and `30-1` become the next real high-cost stories, with their prep already staged

## F. Definition of success for the next two stories

The plan is working if:

- `31-3` starts from scaffolded stubs, not blank files
- `31-3` lands near its K target instead of 4x-5x over it
- `29-1` can start without a fresh cold-start planning pass
- `30-1` does not block on "we still need the baseline fixture"
- review time shifts away from rediscovering known schema traps

---

## Suggested Operating Model for the Remaining Stories

1. **Foundation lane**
   - Finish `31-3`
   - Then open `29-1` and `30-1` with prep already staged

2. **Parallel prep lane**
   - Capture `30-1` golden trace
   - Author/stub `29-1`, `32-1`, `32-2`, `32-4`

3. **Review lane**
   - Apply aggressive DISMISS
   - Treat deferred items as touch-triggered only
   - Keep G6 mandatory where already designated

4. **Closeout lane**
   - Refresh canonical status first
   - Refresh hot-start docs second
   - Do not leave handoff docs behind the sprint file

---

## Immediate Plan Execution Status (2026-04-18)

The support-lane portion of the immediate plan is now materially in place.

- **Ready now for authoritative `31-3` start**
  - `sprint-status.yaml` exposes `31-3-registries` as the next backlog story.
  - the non-authoritative pre-seed is in place
  - the schema-story instantiator is operational
  - the schema scaffold now emits dormant-by-default contract tests, so warm-start stubs no longer create avoidable suite noise before the real dev pass
  - targeted verification of the support toolchain is green

- **Still pending, but intentionally outside the `31-3` authoring lane**
  - `30-1` golden-trace baseline capture still requires Marcus pipeline wiring and fixture capture in the dedicated `dev/30-1-baseline-capture` lane before Story `30-1` opens

- **Authority boundary remains unchanged**
  - story specs and implementation remain owned by the authoritative Cursor/Claude Code BMAD workflows
  - support-lane artifacts exist only to reduce cold-start friction, not to replace those workflows

---

## Bottom Line

The main inefficiency is not that BMAD is too heavy. The main inefficiency is that **31-1 had to discover the rules the rest of the run should already know**, and `31-2` still paid part of that learning tax. The repo now has the right process assets:

- checklist,
- anti-pattern catalog,
- efficiency rules,
- scaffold,
- runway opportunities.

The fastest path through the remaining stories is to treat those assets as **binding preconditions**, not reference material.

If that discipline holds, the remaining stories should be materially faster than `31-1` and noticeably cleaner than `31-2`.
