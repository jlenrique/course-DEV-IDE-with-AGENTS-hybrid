# Epic 28: Tracy the Detective (Research Specialist)

**Status:** in-progress (reshape complete — all 4 reshape stories 28-1/28-2/28-3/28-4 BMAD-CLOSED 2026-04-19; original 28-1/28-2 roster retired via supersession)
**Created:** 2026-04-17
**Reshaped:** 2026-04-19 (Round-3 Shape 3-Disciplined + post-pilot consensus: original 9+3pt roster retired; new 4-story 13pt reshape roster landed + closed same-day)
**Driver:** Introduce a new production-tier specialist — **Tracy** — who partners with Texas to source high-value supplementary research for lessons under development, dispatched by Irene (via Marcus) when the lesson plan reveals enrichment gaps. Tracy's output lands in Pass 2, informing script finalization and downstream asset creation.

## Why This Is Its Own Epic

Tracy is a new specialist born into the production tier. Different JTBD from Epic 27:
- **Epic 27** = technician-capability upgrade (Texas: mechanical, deterministic, "does python-docx handle the contract?"). Acceptance is mechanical.
- **Epic 28** = new editorial-judgment agent. Probabilistic. Iterative. Confidence-scoring. Dispatch semantics with Irene. Acceptance requires operator-feedback loops.

Party-mode consensus (Round 1 + 2 + 3, 2026-04-17): combining these epics would hide Epic 28's iteration cost behind Epic 27's library-wiring cadence. Separate epics. Separate burndowns. Separate risk registers.

## Tracy's Identity (Operator-Authored)

> **Texas is more the technician who knows how to get his hands on things and mutate them into optimal formats for use downstream.** The HIL Operator is the primary indicator of where and what source material is. However, our lesson planner, Irene, may benefit from dispatching (either directly or via Marcus) a Research Assistant — but let's give him the sexier role of Detective and call him **Tracy**. Tracy partners with Texas to search and recover material of potential high value to the lesson under development.

Tracy's signature move: scoped research dispatch. Given a brief from Irene (*cluster 3 needs background on X; cluster 7 needs a counter-example for Y*), Tracy formulates queries, evaluates candidates using domain-specific signals (for scite.ai pilot: supporting/contradicting citation counts, authority tier, recency), and returns a curated manifest with editorial judgment attached.

Tracy does not fetch. Tracy **detects, scopes, and scores**. When the operator approves resources from Tracy's manifest, Marcus dispatches Texas to do the actual fetch + extract. Classic specialist separation: Tracy is the editorial mind; Texas is the technician's hands.

## Scope

**In scope (v1 pilot):**
- Tracy born as a BMB-sanctum specialist under scaffold v0.2.
- Pilot provider: **scite.ai** (scholarly citation retrieval). Tracy's search + scoring limited to this provider in v1.
- Dispatch protocol: Irene → Marcus → Tracy. Tracy writes `suggested-resources.yaml`. Operator approves via Marcus landing-point. Marcus dispatches Texas with approved rows for second-pass extraction (Epic 27 Story 27-2 provider).
- Hard pre-Pass-2 gate: Irene Pass 2 cannot start until Tracy's work (dispatch + approval + Texas second-pass) is complete or formally resolved (empty / failed with operator acknowledgment).
- Manifest vocabulary: `intent_class` (controlled) + `intent_detail` (free-form) + `reserved` sentinel. Day-1 intent_class enum: `narration_citation`, `supporting_evidence`, `counter_example`, `reserved`.
- `editorial_note` field per resource — Tracy's one-line editorial judgment.
- `provider_metadata.scite` sub-object carrying scite-specific signals.
- SSOT discipline: `tracy/vocabulary.yaml` → generated MD doc → L1 `tracy-vocab-lockstep` check.

**Out of scope (deferred to v2 backlog):**
- **Coherence gate** (Dr. Quinn Round 2): pre-Pass-2 check that Tracy's additions are register-coherent with primary-source material. Real concern, not pilot-scope.
- **Pre-indexed domain map** (Dr. Quinn Round 2 TRIZ): cached per-domain authority priors, refreshed async. Architecture-expansion, post-pilot.
- **Dispatch budget** (Dr. Quinn Round 2): Tracy-per-brief cap + approval-queue throttling. Watch for Loop B (supply creates demand) in pilot operation; add if/when evidence surfaces.
- **Additional providers for Tracy** (Notion, Box, YouTube, Playwright, scite's scholarly peers): Epic 27 grows Texas's intake surface; Tracy's dispatch of those providers is a follow-on Epic (tentatively Epic 29+).
- **Asset-intent fan-out beyond Pass 2 narration/slides**: handouts, podcasts, test images, games. Tracy's manifest carries the intent tags; actual asset-specialist agents and their consumption of Tracy's tags are later epics.
- **Operator-pulled Tracy** (Dr. Quinn's reframing): v1 is Irene-dispatched. Re-litigate post-pilot with real evidence.

## Story Roster

### Active roster (post-reshape, 2026-04-19)

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| **28-1-tracy-reshape-charter** | Retire original pilot spec + codify three postures (embellish / corroborate / gap-fill) under John's four-part contract | 2 | **done** (BMAD-closed 2026-04-19) |
| **28-2-tracy-three-modes** | Implement tracy.embellish() / tracy.corroborate() / tracy.gap_fill() dispatching to provider_directory via IdentifiedGap or dial logic | 5 | **done** (BMAD-closed 2026-04-19) |
| **28-3-irene-tracy-bridge** | IreneTracyBridge for in-scope gap dispatching + dial operator endorsements | 3 | **done** (BMAD-closed 2026-04-19) |
| **28-4-tracy-smoke-fixtures** | Tracy-owned read-only loader seam + 4 canonical brief/result fixtures under tests/fixtures/retrieval/tracy_smoke/ (unblocks 32-3 trial-run smoke harness reuse) | 3 | **done** (BMAD-closed 2026-04-19) |

**Total: 13 points. Epic 28 implementation-layer COMPLETE.** Original roster (below) retired via supersession.

### Retired roster (original, pre-reshape)

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| ~~28-1-tracy-pilot-scite-ai~~ | ~~Tracy pilot end-to-end (scite.ai)~~ | ~~9~~ | **retired** (superseded by 28-1-tracy-reshape-charter + 28-2-tracy-three-modes; pre-reshape spec preserved at `28-1-tracy-pilot-scite-ai.md` for archival reference) |
| ~~28-2-tracy-gate-hardening~~ | ~~Gate family + regression hardening~~ | ~~3~~ | **retired** (superseded by 28-1-tracy-reshape-charter + 28-2-tracy-three-modes; fail-closed / refuse-on-ambiguous tests absorbed into reshape roster) |

**Reshape rationale (2026-04-19):** Round-3 Shape 3-Disciplined made the original pilot framing obsolete — Tracy should wrap `retrieval.dispatcher` rather than own scite-specific DSL knowledge (which moved to 27-2 scite adapter). Three-posture architecture (embellish / corroborate / gap-fill) cleanly separates editorial judgment (Tracy) from mechanical fetch (Texas). Gate-hardening absorbed into each posture's fail-closed + refuse-on-ambiguous tests. 13pt total is 1pt over the original 12pt estimate — added 28-3 bridge + 28-4 smoke fixtures proved worth the scope cost.

## Dependency Graph

```
Epic 27: 27-1 DOCX ──► 27-2 scite.ai provider ──► 28-1 Tracy pilot (blocked on 27-2 merge) ──► 28-2 Gate hardening
                                              │
                                              └──► 27-3/4/5/6/7 fan out (not on Epic 28 critical path)
```

**Critical path: 27-1 → 27-2 → 28-1 → 28-2.** Linear, no parallelism on the spine. 28-1 may begin scaffolding (sanctum, vocabulary.yaml) against a stubbed scite provider while 27-2 lands code.

## AC Spine — Cross-Cutting Acceptance Criteria

Every 28-N story must satisfy (shared AC spine at [epic-28/_shared/ac-spine.md](./epic-28/_shared/ac-spine.md)):

- **AC-S1: Dispatch-vs-artifact rule honored.** Tracy never invokes Texas at runtime. Marcus owns every dispatch edge. Artifact handoffs via filesystem are fine.
- **AC-S2: Artifact atomicity.** Tracy's manifest writes are atomic (temp + rename) OR carry an explicit `status: complete` marker. No half-written handoffs visible to Marcus's dispatch check.
- **AC-S3: Hard pre-Pass-2 gate.** Irene Pass 2 cannot start unless `tracy-complete.yaml` receipt is present, valid, and resolves to `complete | empty | failed` — all three with operator acknowledgment via Marcus landing-point when non-complete.
- **AC-S4: Manifest schema compliance.** Every Tracy output validates against the published `suggested-resources.schema.yaml`. Drift = CI failure.
- **AC-S5: Vocabulary SSOT.** `tracy/vocabulary.yaml` is source of truth. Generated MD doc + L1 `tracy-vocab-lockstep` check fail commit if code drifts from vocabulary.
- **AC-S6: `editorial_note` required on every row.** Empty note = lint failure. Vacuous note (would pass on any resource) flagged by static heuristic — not a hard fail in v1, but warning surfaced in review.
- **AC-S7: Test coverage floor.** Minimum 3 tests per story (Murat's xfail-strict pattern during implementation, flipping green as AC lands).
- **AC-S8: Dispatch audit trail.** Every Tracy dispatch produces an entry in `runs/<run-id>/tracy/dispatch-log.yaml` — which brief, what queries, how many candidates evaluated, how many surfaced, operator action on each.

## Non-Functional Requirements

- **Latency budget:** Tracy dispatch + operator approval + Texas second-pass targets combined ≤90 seconds for typical brief (2-5 candidates). Hard cap at 180 seconds per dispatch before timeout + operator intervention.
- **Cassette-first test doctrine:** every scite.ai call cassette-backed. Real-network tests in `tests/live/` with `@pytest.mark.live`, not in default suite.
- **Fail-closed gate semantics:** an unresolved gate receipt is a block, never a silent skip. Pass 2 refuses with exit code + grep-able log line.
- **Operator agency:** every approve/reject/refine decision logged with timestamp and rationale field for post-pilot feedback analysis.

## Risk Register

| Risk | Owner | Mitigation |
|------|-------|-----------|
| **Tracy scoring rubric undefined in pilot** (John Round-3 flag) | Tracy + Paige | 28-1 AC requires documented scoring rubric even if v1 is naive. Rubric iteration expected post-pilot. |
| **Silent-orphan asset intents** (Murat Round 2) | Murat | `tests/contracts/test_asset_intent_registry.py` — bidirectional consumer registration check. |
| **Hallucinated URLs or scite-absent papers** | Amelia / Murat | Texas second-pass fetch validates URL + content; hallucinated rows fail fetch and are flagged pre-Pass-2. Gate receipt marks these as `status: partial`. |
| **Operator rubber-stamps high-confidence rows then regrets** (Sally Round 1 Case B) | Sally / Tracy | Auto-adopted rows (≥0.85 all scores) shown in manifest with full title + domain visible for scan-time review. Operator has one-click demote. |
| **Loop B (supply creates demand)** — Irene flags more gaps once Tracy is reliable (Dr. Quinn Round 2) | Winston | Monitor dispatch rate per run; if avg dispatches/run climbs past 3 in first 5 runs, trigger 28-v2-b (dispatch budget) story. |
| **Loop C (vocabulary capture)** — Irene's planning conforms to Tracy's `intent_class` enum (Dr. Quinn Round 2) | Winston | Independent audit pattern: post-pilot retro reviews what Irene did NOT flag vs what primary-source evidence reveals. Structural audit not individual-brief audit. |
| **Coherence drift across downstream assets** (Dr. Quinn Round 2 adversarial scenario) | Quinn-R | Logged as 28-v2-a coherence-gate story. Not pilot scope, but documented as a first-retrospective question. |
| **Scite.ai rate limit or API outage during a live run** | Amelia | Cassette-backed test for 429 response shape; real-run retry with exponential backoff + operator-visible status. |
| **Operator approval as bottleneck** (Dr. Quinn TOC analysis) | Sally | Tiered confidence + auto-adopt for high-scoring items keeps review-table to ~5 items typical; redlineable manifest (not prompt-per-item) enables 45-sec review. |

## v2 Backlog (Named Tonight, Not Scoped)

Per John's Round 3 call — stub correctness-concern items now, defer optimization items to post-pilot retro:

**Stubbed (named, one-line AC, no estimate):**
- **28-v2-a — Coherence gate** (Dr. Quinn). Before Pass 2 ingestion, Tracy's returned resources checked against Irene's brief thesis for register/vocabulary/framing drift. Correctness concern.
- **28-v2-b — Dispatch budget** (Dr. Quinn). Soft cap on Tracy-dispatches-per-run + approval-queue throttling. Promote if Loop B evidence surfaces.

**Deferred to post-pilot retro (not stubbed, mentioned here):**
- Pre-indexed domain map (Dr. Quinn TRIZ resolution): cached per-domain authority priors.
- Full L1 lockstep vocabulary check beyond single AC line (Paige) — wait for pilot drift evidence.
- Operator-pulled Tracy (Dr. Quinn reframing) — wait for usage data.
- Additional Tracy providers (Notion, Box, YouTube, Playwright) — Epic 29+.

## Definition of Done (Epic Level)

- Tracy sanctum bundle at [`skills/bmad-agent-tracy/`](../../skills/bmad-agent-tracy/) — SKILL.md + references + scripts + schemas — complete per scaffold v0.2.
- First-Breath protocol works: Tracy can be born fresh into `_bmad/memory/bmad-agent-tracy/` from the sanctum bundle.
- 28-1 and 28-2 `done` in `sprint-status.yaml`.
- Pilot scite.ai dispatch demonstrated end-to-end: Irene brief → Tracy manifest → operator approval → Texas second-pass → Irene Pass 2 ingestion of new material.
- Hard gate verified under all three resolution paths: `complete`, `empty`, `failed`.
- Vocabulary lockstep check (L1 `tracy-vocab-lockstep`) passing.
- No pytest regressions. 0 new default-suite skips.
- Post-pilot retrospective completed: Loop B + Loop C + coherence-drift assessed against v1 evidence; v2 backlog priorities updated.

## Party-Mode Consensus Record

- **Round 1 (2026-04-17)** — Winston, John, Sally, Mary: Tracy = pure specialist with own manifest. Irene dispatches via Marcus. Specialists don't dispatch specialists at runtime. Mary's cognitive-lineage analysis: Tracy inherits triangulation + authoritativeness discipline from analyst role, disinherits saturation instinct. Sally's operator-UX scenario: Irene self-surfaces trigger, Marcus asks operator, redlineable manifest (not prompt chain).
- **Round 2 (2026-04-17)** — Amelia, Murat, Paige, Dr. Quinn: hard pre-Pass-2 gate plumbing; 3-field manifest extension for asset-intent coupling (Amelia) ↔ 2-field controlled+free (Paige — adopted); Murat's 3-test floor + cassette strategy + xfail-strict doctrine; Dr. Quinn's TOC analysis (approval is CCR, not Tracy), Five Whys on empty-return (three signals in one costume), TRIZ preliminary-action principle, Loop B/C naming, coherence-drift adversarial scenario.
- **Round 3 (2026-04-17)** — John, Amelia, Paige, Murat: story-split converges at 2 stories (compressed from 3); scoring rubric called out explicitly as AC; scite.ai enum (4 day-1 values); `provider_metadata.scite` sub-object pattern; ratification test (Murat) protecting cross-lane consistency; xfail-alongside-story-artifact doctrine.
- **Dispatch-vs-artifact ratification (2026-04-17)** — Winston: orchestration through Marcus (non-negotiable); artifact handoff via filesystem (not a rule violation); atomic writes + staleness checks as implementation hygiene.

## Shared Artifacts

Located at [`_bmad-output/implementation-artifacts/epic-28/_shared/`](./epic-28/_shared/):

- [`ac-spine.md`](./epic-28/_shared/ac-spine.md) — the 8 cross-cutting ACs above, formal version.
- [`runbook.md`](./epic-28/_shared/runbook.md) — step-by-step Tracy dispatch end-to-end (Irene → Marcus → Tracy → scite.ai → operator approval → Texas second-pass → Irene Pass 2).
- [`worksheet-template.md`](./epic-28/_shared/worksheet-template.md) — per-story worksheet (mirrors Epic 26 pattern).

## Links

- [Story 28-1: Tracy pilot (scite.ai end-to-end)](./28-1-tracy-pilot-scite-ai.md)
- [Story 28-2: Gate family + regression hardening](./28-2-tracy-gate-hardening.md)
- [Epic 27: Texas Intake Surface Expansion](./epic-27-texas-intake-expansion.md) — depends on 27-2 landing first
- [Tracy sanctum bundle: `skills/bmad-agent-tracy/`](../../skills/bmad-agent-tracy/) — born in 28-1
