---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
workflowComplete: true
completedAt: 2026-05-04
fr_nfr_signoff:
  date: 2026-05-04
  voices: [John, Winston, Amelia, Murat]
  verdict: 'Unanimous ACCEPT-WITH-AMENDMENT (4/4); 19 amendments folded into PRD'
  amendments_folded:
    fr_amendments:
      - FR-7c-1 binding Pydantic output contract + composer infra hooks (John A1 + Amelia A1)
      - FR-7c-7 four lockstep files enumerated verbatim (Amelia A2)
      - FR-7c-10..19 enumerated as standalone capability contracts (John A2)
      - FR-7c-25 envelope schema path + fields (Amelia A3)
      - FR-7c-34..38 quantitative coverage floors (Murat A4)
      - FR-7c-46 UTF-8 CI lint glob pinned (Winston A5)
    new_frs:
      - FR-7c-49 per-HIL-surface OperatorVerdict schema-stability test (Amelia + Murat)
      - FR-7c-50 override_event audit-chain integrity test (Amelia + Murat)
      - FR-7c-51 schema_version field + Trial-3 transcript schema test (Amelia + Murat)
      - FR-7c-52 codex-dev-prompt-{story-key}.md NEW CYCLE artifact (Amelia)
      - FR-7c-53 import-linter contracts C4/C5/C6 for §02A composer + parity DSL + HIL boundaries (Winston A1)
      - FR-7c-54 sanctum-invariant declaration for 5 Marcus-bound writers (Winston A2)
    nfr_amendments:
      - NFR-7c-P1 calibration band semantics + p50/p99 over ≥20 fixture-replay runs (John + Amelia + Murat)
      - NFR-7c-P2 cache-key normalization rule SHA256(normalized_prompt) (Amelia A10)
      - NFR-7c-P4 ≤2s p99 in-process / ≤4s p99 MCP-stdio split (Amelia A11)
      - NFR-7c-R1 cite Slab 7b flake bar explicitly (Murat A2)
      - NFR-7c-R7 split into R7a + R7b (John + Murat A3)
      - NFR-7c-S3/S4/S7 explicit import-linter scope (Winston A3)
      - NFR-7c-OD2 Pydantic-v2 TripwireLedgerEntry schema enforcement (Murat A5; highest-leverage)
      - NFR-7c-OD7 NEW parity-DSL self-registration audit (Winston A4)
    story_decomposition:
      - 'Wave 0 added: Story 7c.0 Parity-Contract DSL ADR + scaffold (Amelia A4; required before FR-7c-30..33)'
story_decomposition_signoff:
  date: 2026-05-04
  voices: [John, Winston, Amelia, Murat]
  verdict: 'Unanimous ACCEPT-WITH-AMENDMENT (4/4); all consolidated amendments folded'
  amendments_folded:
    structural:
      - 'Wave-3 per-surface overlap with Wave 2 (John A1)'
      - '7c.2 opens parallel to 7c.0; does NOT wait (John A2)'
      - 'Split 7c.3 into 7c.3a composer-body + 7c.3b §02A poll-surface; both Wave 1 (Winston A4)'
      - 'Wave 3 drops 11 → 10 HIL surfaces; §02A lifted to Wave 1 (Winston A4 + Amelia A2)'
      - 'Split 7c.4 into 7c.4a decision + 7c.4b foundation (Winston A3)'
      - 'Lock alias decision now: 8 net-new gate families + 6 alias gates (Amelia A3)'
      - 'Split 7c.17 into 7c.17a (3 writers) + 7c.17b (2 writers + envelope) (Amelia A4)'
      - 'Mandatory split 7c.18 → 7c.18a §06B + 7c.18b §07C (John A3 + Amelia A5)'
      - 'Hard-split 7c.20 → 7c.20a/b/c per Murat M3 (heterogeneous test cost)'
      - 'Peel 7c.21 → 7c.21 ceremony + 7c.21a Epic 3 retirement + live-dispatch (John A6)'
    infra_ownership:
      - '7c.0 owns: FR-7c-50 + FR-7c-53 C4 + FR-7c-54 sanctum-mechanism + NFR-7c-OD2 TripwireLedgerEntry + NFR-7c-OD7 audit harness + TW-7c-4/5/6 detection scaffolds (Winston A1/A2 + Amelia A1 + Murat M1/M2)'
      - '7c.2 owns: cp1252 fix + cp1252 fixture-comparison utility (Murat M1)'
      - '7c.3a owns: FR-7c-53 C5 §02A composer boundary (Winston A2)'
      - '7c.4b owns: FR-7c-49 OperatorVerdict schema-stability + FR-7c-53 C6 HIL boundaries + TW-7c-3 lockstep checker registration + class-conformance extension (Winston A2 + Amelia A1 + Murat M1)'
      - '7c.5.G0..G6 own: TW-7c-3 firing per-gate (Murat M1)'
      - '7c.6..7c.15 own: per-surface OperatorVerdict schema-stability cases (FR-7c-49 parametrized)'
      - '7c.17a/b own: FR-7c-54 sanctum-alignment consumption per writer'
      - '7c.20a/b/c own: TW-7c-1 detection + AUDIT-AC verification per coverage floor'
      - '7c.21 owns: FR-7c-51 schema_version + Trial3Transcript + TW-7c-6 50-run firing + Trial-3 readiness AC (Amelia A1 + Murat M4)'
    cross_agent_review_designated:
      - 7c.0 (architectural pre-decision)
      - 7c.3a (§02A composer dual-nature)
      - 7c.4b (gate-family taxonomy foundation)
      - 7c.21 (slab-closer; 7b.12 precedent)
    velocity_realism:
      - 'Realistic actual: 5.5-7 days NEW CYCLE Codex/Claude (Amelia A7); collapse-paths to ~4.5-6 days available'
    operator_picks_resolved:
      - 'Alias decision LOCKED at PRD Step 11 per Amelia A3 (8 net-new + 6 alias; not deferred to 7c.4 sprint-planning)'
      - '7c.20 hard-split per Murat M3 (not envelope-clause per Amelia A6; Amelia A6 envelope-clause folded as fallback if any AUDIT discovers gaps)'
  story_count_final: 26
  pts_estimate_range: 60-72
  duration_estimate_days: 5.5-7
classification:
  projectType: multi-agent-orchestration-platform-operator-conversational-tail
  domain: ai-orchestrated-online-course-content-production
  complexity: high
  projectContext: brownfield-migration-closeout-sub-slab
inputDocuments:
  - _bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/slab-7b-retrospective.md
  - _bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md
  - _bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md
  - _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/implementation-artifacts/bmm-workflow-status.yaml
  - next-session-start-here.md
  - docs/project-context.md
  - docs/agent-environment.md
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 13
workflowType: 'prd'
slab: 7c
slabDescriptor: 'marcus orchestrational tail'
priorPartyModeRoundtable:
  date: 2026-05-04
  voices: [John, Winston, Amelia, Murat]
  framingVerdict: 'Reading 1 unanimous — Slab 7a + 7b + 7c REPLACE original Epic 3'
  preLoadedDeliverables:
    - 'Goals/Vision paragraph (Winston-led, fold John §02A dual-nature caveat)'
    - 'D2/D3/D7 PRD-level invariants (Winston, non-negotiable)'
    - '5 AUDIT-ACs (3.2-3.6 verify-then-file-if-gap; 3.6 = Trial-3 ceremony)'
    - '6 tripwires (TW-7c-1 amended through TW-7c-6 new on parity-budget)'
    - 'Trial-3 separate post-close ceremony (precedent: 7a.8 + 7b.12)'
  pendingDiscoveryQuestions:
    - '14-gate family taxonomy (Winston+Murat call): alias-via-discriminator vs new-shape vs hybrid'
    - '11 HIL surfaces transport-parity-matrix shape (Winston leans option-c parity-contract DSL)'
---

# Product Requirements Document — Slab 7c Marcus Orchestrational Tail

**Project:** course-DEV-IDE-with-AGENTS (LangChain/LangGraph migration; hybrid clone)
**Author:** Juanl
**Date:** 2026-05-04
**Branch:** `dev/langchain-langgraph-foundation`
**Slab:** 7c — Marcus Orchestrational Tail
**Replaces:** original Slab 3 / Epic 3 (Marcus Orchestration; jointly with Slabs 7a + 7b)
**Driving evidence:** Trial-2 2026-05-04 structured-stop ceremony; three findings; substrate validated.

> *Workflow scaffolding: PRD authored via `bmad-create-prd` step-file workflow. Step 11
> Document Polish complete (Step 12 Complete PRD pending operator close).*

## Table of Contents

- [Executive Summary](#executive-summary) · [Project Classification](#project-classification)
- [Success Criteria](#success-criteria) — User / Business / Technical / Measurable
- [Product Scope](#product-scope) — forward-reference to §Project Scoping & Phased Development
- [Tripwire Ledger (Slab 7c)](#tripwire-ledger-slab-7c) — **authoritative source-of-truth** for TW-7c-1..TW-7c-6
- [User Journeys](#user-journeys) — 5 journeys (operator happy/edge + dev / code-review / CI substrate)
- [Domain-Specific Requirements](#domain-specific-requirements) — Migration governance regime + invariants
- [Innovation & Novel Patterns](#innovation--novel-patterns) — AUDIT-not-BUILD + 6 tripwires + parity-DSL
- [Slab 7c Project-Type Architecture](#slab-7c-project-type-architecture) — Marcus + 11 specialists + 4 transports + parity-DSL
- [Project Scoping & Phased Development](#project-scoping--phased-development) — **authoritative §Story Decomposition** (~26 stories / ~60-72 pts / 5.5-7 days)
- [Functional Requirements](#functional-requirements) — 54 FRs across 10 capability areas A-J
- [Non-Functional Requirements](#non-functional-requirements) — 36 NFRs across 6 categories (P/S/R/M/X/OD)

## Executive Summary

Slab 7c is the **scope-binding closeout** of the work originally chartered as Epic 3 (Marcus
Orchestration, stories 3.1–3.6) in `epics-langchain-langgraph-migration.md`. Slabs 7a (CLOSED
2026-04-29) and 7b (CLOSED 2026-05-01) jointly **replaced** Epic 3 in lineage, shipping the
Marcus orchestration substrate (supervisor + routing + facade + manifest-driven `PRODUCTION_GATE_IDS`
+ pre-gate-marcus shared LLM node + conversation persistence) and 11 specialist body activations
onto that substrate. Slab 7c finishes the orchestrational tail: it elevates the `pre-gate-marcus`
directive composer from corpus-scan FALLBACK to LLM-driven (Trial-2 2026-05-04 finding #2 — first
PRD priority within 7c), expands `PRODUCTION_GATE_IDS` from 4 to 14, ships 11 conversational
HIL surfaces (§04A per-plan-unit ratification, §04.5/§04.55 estimator + run-constants lock,
§05.5 per-slide mode, §07B per-slide A/B variant, §07D motion-plan polling, §07F motion gate,
§08B Storyboard B + live-URL, §11 voice selection, §11B input-package, §15 final operator
handoff) plus §02A operator-directives poll surface, ships 5 Marcus-bound pre-dispatch package
writers (`gary-slide-content.json`, `gary-fidelity-slides.json`, `gary-diagram-cards.json`,
`gary-theme-resolution.json`, `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md`),
and adds §06B literal-visual operator build, §07C storyboard build + HTML reviewer surface, and
§09 four-artifact lock semantics. Original Epic 3 carry-forwards 3.2 / 3.3 / 3.4 / 3.5 enter
Slab 7c as **AUDIT-ACs** against shipped substrate (transport-parity suite under
`tests/integration/transport_parity/` + `tests/integration/transports/`, per-gate DecisionCard
Pydantic family at `app/models/decision_cards/`, import-linter Contract C3 + M1–M4 +
scheduler-ban in `pyproject.toml`) — verify-then-file-if-gap, not build-from-scratch. Original
Epic 3 story 3.6 M3 acceptance is re-vehicled as **Trial-3** — a separate operator-witnessed
post-close ceremony, not a Slab 7c slab-close gate (precedent: Story 7a.8 Trial-1, Story 7b.12
Trial-2). The slab is bounded by three architectural invariants from
`architecture-langchain-langgraph-migration.md` that every gate and HIL surface inherits by
construction: **D2** (model cascade + DecisionCard cache-state), **D3** (HIL tamper-evidence
via verdict-digest match + override-event audit chain), **D7** (transport parity across
CLI / FastAPI / MCP-stdio / MCP-subprocess).

### What Makes This Special

Slab 7c turns Marcus from the silent happy-path runner that Trial-2 evidence-confirmed as
substrate-correct into the **LLM-driven conversational orchestrator** the legacy v4.2
production-prompt-pack experience established as the operator's "general contractor" surface.
Three structural moves make this load-bearing rather than aspirational. **First**, the AUDIT-not-
BUILD reframing of original 3.2 / 3.3 / 3.4 / 3.5 (substrate-grep 2026-05-04 confirmed plumbing
shipped on disk: 8 transport-parity tests, 7 DecisionCard modules + 5 schemas, 9 import-linter
contracts) compresses Slab 7c's net-new build to the *coverage* dimension only — story authors
verify the existing substrate is green and comprehensive, file gaps as 7c.X follow-ons, and
spend their build budget on the 14-gate expansion + 11 HIL surfaces. **Second**, the §02A
directive-composer surface is **dual-nature** — both a Trial-2 finding-#2 substrate-bug-fix
(directive composer must become genuinely LLM-driven, not corpus-scan fallback that produces
byte-identical broken output across 5 successive runs) AND the first conversational HIL surface
the operator actually meets in a Trial-3 run; the PRD names both hats explicitly so the AC
shape carries both the feature contract and the regression-fix contract. **Third**, six
tripwires (TW-7c-1 through TW-7c-6) make implicit risks explicit at slab-open: DecisionCard
schema-completion drift on the 14-gate expansion, transport-parity flake exposure
(parity-budget exhaustion at ~68 cells, 4.5× the current ~15-cell matrix), §02A composer
regression on Trial-2 finding #1 cp1252 fix, Trial-3 leakage into slab-close evidence,
D2/D3/D7 invariant violation during build, and live-dispatch scope creep into non-live-harness
stories. The architectural call on the 11 HIL surfaces' parity-matrix shape is decided **once
in the PRD** (Winston leans option-c parity-contract DSL so HIL surfaces self-register), not
hand-waved to story-author time where it would produce 11 inconsistent decisions.

## Project Classification

- **Project Type:** Multi-agent orchestration platform — operator-conversational tail (Python +
  LangChain + LangGraph; Marcus orchestrator + 11 specialists + 14 gate codes + HIL surfaces
  across CLI / FastAPI / MCP-stdio / MCP-subprocess transports).
- **Domain:** AI-orchestrated online course content production (Texas wrangling →
  Irene Pass-1/Pass-2 authoring → Gary slide generation → Kira motion → ElevenLabs voice →
  Compositor assembly → Quinn-R review → Vera fidelity → Canvas/CourseArc deployment).
- **Complexity:** HIGH — HIL tamper-evidence + import-linter Contract C3 + four-file lockstep +
  audit-grade evidence trail; novel multi-transport verdict-parity byte-equivalence requirement;
  parity-test budget exposure; cross-slab governance (pipeline-manifest lockstep regime +
  sandbox-AC validator + governance JSON freeze rules).
- **Project Context:** BROWNFIELD migration — explicit closeout sub-slab (third in a three-sub-
  slab decomposition: 7a substrate + 7b body + 7c orchestrational tail) that formally REPLACES
  original Slab 3 / Epic 3. Substrate validated end-to-end by Trial-2 2026-05-04 (Texas
  fail-loud guardrail engaged correctly on broken directive). Slab 7c's net-new build is
  bounded by the §02A elevation + PRODUCTION_GATE_IDS expansion + 11 HIL + 5 writers + §06B/
  §07C/§09/§15; original 3.2/3.3/3.4/3.5 plumbing audits in place.

## Success Criteria

### User Success

The "user" for Slab 7c is the **operator** launching a real-corpus course-content production
run. User success is the operator-experience shift from Trial-2's structured-stop posture
("substrate correct, but cannot produce reviewable content because directive composer is
corpus-scan fallback") to Trial-3's general-contractor posture (Marcus polls, ratifies, gates,
hands off across §02A → §15). Concrete user-success moments:

- **§02A first directive ratification:** the operator launches a Trial-3 corpus run, and the
  pre-gate-marcus directive composer emits an LLM-driven directive YAML the operator either
  approves verbatim or edits at the §02A poll surface. The directive correctly classifies primary
  vs supporting roles (no `.gitkeep` as `role: primary`; primary `.docx` content keeps
  `role: primary`; PNG/JPG binaries are not assigned `expected_min_words`). Trial-2 finding #2
  is structurally retired by this moment.
- **End-to-end §01→§15 traversal:** Trial-3 reaches §15 final operator handoff, with at least
  one HIL surface fired at every conversational decision point (§02A, §04A, §04.5/§04.55,
  §05.5, §07B, §07D, §07F, §08B, §11, §11B, §15). Operator emits at least one `edit` verdict
  in addition to `approve` verdicts, exercising the override surface and DecisionCardMeta
  cache_state warning chain (D2 enforcement).
- **G0 print Windows-portability:** the operator running on Windows with macOS-screenshot
  Unicode (U+202F NNBSP) corpus content does not see a cp1252 print crash at G0 (Trial-2
  finding #1 retired); UTF-8 round-trip is preserved end-to-end without `PYTHONIOENCODING=utf-8`
  workaround.

### Business Success

Business success for Slab 7c maps to the parent migration PRD's **M3 milestone** ("Marcus
orchestrates end-to-end") evidence accrual, re-vehicled as **Trial-3 ceremony** (post-close):

- **M3 evidence accrual:** Trial-3 produces operator-witnessed evidence that §01→§15 completes
  with Marcus as supervisor, DecisionCards emitted at every gate including the 14-gate
  expansion, and verdicts dispatched via CLI minimum (MCP/FastAPI parity optional-but-
  demonstrated). Evidence pasted into a named M3-acceptance artifact under
  `_bmad-output/implementation-artifacts/`.
- **Slab-7c-live-harness-evidence retired:** `run_cache_hit_harness.py` and
  `run_5_api_smoke.py` ship live-dispatch authoring (filed as deferred-inventory entry
  `slab-7c-live-harness-evidence` 2026-05-01). Deferred-inventory entry CLOSED at Slab 7c
  retrospective.
- **Trial-2 deferred-inventory closure:** both Trial-2 finding #1 (cp1252 crash) and finding
  #2 (directive-composer fallback) deferred-inventory entries CLOSED by Slab 7c work.
- **Original Epic 3 retirement:** `epics-langchain-langgraph-migration.md` §Epic 3 updated
  in-place at Slab 7c retrospective close to record the 7a+7b+7c replacement, with cross-
  references to the three closure artifacts. No orphan stories from the original 6-story
  decomposition remain pending.
- **Slab 7c retrospective produced:** authored per `bmad-retrospective`, captures lessons
  learned, deferred-inventory delta, mapping-checklist row updates (✅/⚠️/❌ flips for §01,
  §02A, §04A, §04.5, §04.55, §05.5, §06, §06B, §07B, §07C, §07D, §07F, §08B, §09, §11,
  §11B, §15 rows that were "Stay ❌ — Marcus orchestration" or "Stay ⚠️" post-Slab-7b).
- **Unblocks Slab 4** (Cora dev-graph + lockstep + frozen-graph + ledger): Slab 7c is the
  last gate before Slab 4 opens.

### Technical Success

Technical success is structural: every AUDIT-AC green, every BUILD-AC green, every tripwire
not fired (or fired-and-resolved per protocol), every architectural invariant preserved.

- **5 AUDIT-ACs (3.2/3.3/3.4/3.5/3.6) all green** — verify-then-file-if-gap closure. Any gap
  found during AUDIT filed as `7c.X.<descriptor>` follow-on, party-mode-consensus on
  absorb-vs-defer (TW-7c-1).
- **PRODUCTION_GATE_IDS expansion 4 → 14 with four-file lockstep** for every new gate
  (Pydantic model + JSON schema + shape-pin test + golden fixture; existing G1/G2C/G3/G4
  family pattern is the authoritative scaffold; copy-and-extend, no re-derivation).
- **11 HIL surfaces shipped** with parity-contract coverage decided once at PRD level
  (Winston leans option-c parity-contract DSL); each HIL surface declares mandatory
  transports at slab-open (CLI minimum; HTTP/MCP opt-in per surface).
- **5 Marcus-bound writers shipped** (`gary-slide-content.json`,
  `gary-fidelity-slides.json`, `gary-diagram-cards.json`, `gary-theme-resolution.json`,
  `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md`).
- **§02A LLM-driven directive composer shipped** — replaces corpus-scan fallback; passes
  Trial-2 fixture regression test (preserved at `state/config/runs/db276994-edf4-47a2-83bc-
  771cc214c3c1/` and bash launch helper at `C:\tmp\run-trial-2.sh`); UTF-8 round-trip
  preserved (Trial-2 finding #1 fix folded into §02A spec OR shipped as standalone pre-§02A
  patch — operator decides at PRD Step 11 readiness gate).
- **D2/D3/D7 invariants preserved by construction:** every new gate emits DecisionCardMeta
  cache_state (D2); every new HIL surface emits OperatorVerdict + override_event audit chain
  (D3); every new operator surface conforms to four-transport parity contract (D7).
- **Parity-test budget held:** parity suite runs 50 consecutive times in CI with zero flakes
  before slab marks done (TW-7c-6). Per-surface transport declaration enforced
  (CLI mandatory; HTTP + MCP opt-in declared at slab-open).
- **Class-conformance validator floor maintained:** ≥11 conforming activation contracts
  (current floor; do not regress).
- **Mapping-checklist invariants held:** SG-1 (11-roster) + SG-2 (33-row) + SG-3 (7-section
  Composition Spec) + SG-4 (BMB sanctum alignment) all green via parity suite. Mapping-
  checklist FULLY MIGRATED rows floor lifts from 7 (post-Slab-7b ratification) to a higher
  floor reflecting orchestrational-tail row flips (precise count ratified at Slab 7c
  retrospective).
- **CI substrate green:** ruff clean; lint-imports 9+ contracts KEPT; sandbox-AC validator
  PASS; pipeline-manifest lockstep PASS; live-API detector clean; substrate-frozen-paths
  invariant held; full regression ≥1403 deterministic baseline (current floor).
- **UTF-8-only CI lint pass enforced** on every file touched by Slab 7c (TW-7c-5
  amendment).

### Measurable Outcomes

| Metric | Pre-Slab-7c (today) | Post-Slab-7c target |
|---|---|---|
| `PRODUCTION_GATE_IDS` honored at runtime | 4 (G1/G2C/G3/G4) | 14 (G0/G0A/G0B/G1/G1A/G1.5/G2/G2B/G2C/G2M/G2.5/G2F/G3/G3B/G4/G4A/G4B/G5 — exact taxonomy ratified at PRD discovery) |
| Conversational HIL surfaces fired in a Trial run | 0 (Trial-2 stopped at G0) | 11 (§04A + §04.5/§04.55 + §05.5 + §07B + §07D + §07F + §08B + §11 + §11B + §15 + §02A) |
| Marcus-bound writers shipped | 0 | 5 (per §06 specification) |
| §02A directive composition mode | corpus-scan fallback | LLM-driven |
| Trial-2 deferred-inventory entries open | 2 | 0 |
| Mapping-checklist ✅ FULLY MIGRATED row floor | 7 | TBD at Slab 7c retrospective close (≥7; expected ~17–22 based on §01/§02A/§04A/§04.5/§04.55/§05.5/§06/§06B/§07B/§07C/§07D/§07F/§08B/§09/§11/§11B/§15 row-flip candidates) |
| Slab-7c-live-harness-evidence deferred-inventory entry | open | CLOSED |
| Class-conformance contracts | 11 | ≥11 (no regression) |
| Parity-test flake rate | unmeasured | <0.1% per cell over 50-run CI baseline |
| Trial-3 readiness | blocked at G0 | UNBLOCKED end-to-end §01→§15 |

## Product Scope

> **Forward-reference:** detailed MVP / Growth / Vision scope, story decomposition,
> wave sequencing, gate taxonomy, cross-agent code-review designations, and velocity
> estimate live in §[Project Scoping & Phased Development](#project-scoping--phased-development)
> below. This block carries the high-altitude summary; the authoritative scoping lives there.

**MVP — Slab 7c is the MVP closeout sub-slab.** No "MVP-vs-full" subdivision; no descope
path. Per party-mode 2026-05-04 unanimous Reading 1, the full scope (§02A LLM-driven
composer + PRODUCTION_GATE_IDS expansion 4 → 14 + 11 HIL surfaces + 5 Marcus-bound writers
+ §06B/§07C/§09/§15 closeout + AUDIT-ACs + Trial-3 readiness) ships together. Splitting
would reopen the Slab-3-vs-Slab-7c framing question this PRD resolved (TW-7c-4) and would
invert the slab-close vs ceremony precedent established by Slab 7a 7a.8 + Slab 7b 7b.12.

**Growth (Post-Slab-7c)** is reserved for **Slab 4** (Cora dev-graph + lockstep +
frozen-graph + ledger; M4 gate; developer-side observability) and **Slab 5a** (Acceptance:
trial-replay regression suite + head-to-head parity + 15-invariant audit matrix; M5
ship/iterate/rollback gate), already scoped in `epics-langchain-langgraph-migration.md`.
In-Slab-7c follow-on candidates (filed as deferred-inventory entries, not in-scope):
live-dispatch verification beyond the named harness (TW-7c-4 enforced); mapping-checklist
deferred-row detection strengthening (filed 2026-04-30); Class-C validator method-name
provider-agnostic rename (filed 2026-04-29); pre-existing full ruff debt cleanup pass
(filed 2026-04-30).

**Vision** beyond Slab 4 + 5a + 5b: four backlog epics named in the migration plan
(Epic 15 Learning, Epic 16 Autonomy, Epic 17 Research, Epic 18 Assets) plus Post-M5
Greenfield Specialists. Out of Slab 7c scope.

---

## Tripwire Ledger (Slab 7c)

> **Authoritative source-of-truth** for TW-7c-1..TW-7c-6. Per-tripwire detection-infra
> ownership lives in §[Project Scoping & Phased Development](#project-scoping--phased-development)
> §Story Decomposition (frontmatter `story_decomposition_signoff::infra_ownership` + Murat M1
> tripwire ownership table). Schema enforcement via Pydantic-v2 `TripwireLedgerEntry` is
> NFR-7c-OD2 (highest-leverage Round-3 amendment).

Six tripwires ratified by party-mode 2026-05-04. Stored at slab-open in
`sprint-status.yaml::tripwire_events` per Slab 7b precedent (Round-(e) E2 Mary amendment).
Each tripwire entry records: `tripwire_id`, `story_owner`, `fired_at`, `fired_verdict`,
`measured_value`, `escalation_action_taken`, `decision_record_link`.

| ID | Trip Condition | Severity | Escalation |
|---|---|---|---|
| TW-7c-1 | AUDIT-AC (3.2-3.6) discovers gap | high | STOP; file `7c.X.<descriptor>`; party-mode-consensus on absorb-vs-defer |
| TW-7c-2 | §02A composer fails Trial-2 finding #1 cp1252 regression on preserved fixture | high | STOP; re-scope §02A; dual-nature claim invalidated |
| TW-7c-3 | New gate added to PRODUCTION_GATE_IDS without four-file lockstep + class-conformance | critical | STOP; lockstep gate-fill required before any downstream story opens |
| TW-7c-4 | Trial-3 outcome leaks into Slab 7c slab-close evidence | high | STOP; party-mode re-affirm Trial-3 separate ceremony OR formally amend |
| TW-7c-5 | D2/D3/D7 invariant violation during build OR cp1252 encoding regression | critical | STOP; Winston non-negotiables hold; invariant violation cannot land |
| TW-7c-6 | Parity-test flake rate >0.1%/cell over 50-run CI baseline OR existing 8 parity files regress to flaky | high | STOP; parity-budget mitigation per option-c parity-contract DSL; per-surface transport declaration enforced |

## User Journeys

### Journey 1 — Operator Trial-3 Happy Path (Primary User, Success)

**Persona:** **Juanl** (operator). Owns the migration; ran Trial-2 2026-05-04 to structured-stop;
ratified Reading 1 framing the same day; expects Slab 7c to retire Trial-2's two findings and
unblock M3 acceptance via Trial-3.

**Opening Scene:** Slab 7c retrospective has just closed. Juanl opens a fresh terminal on
`dev/langchain-langgraph-foundation`, post-Slab-7c HEAD. Pre-flight gates green (Slab 7c CLOSED;
class-conformance ≥11; mapping-checklist invariants held; parity suite zero-flake on 50-run
baseline; UTF-8 lint clean). The Trial-2 forensic evidence (`state/config/runs/db276994-edf4-
47a2-83bc-771cc214c3c1/`) sits preserved as the regression fixture §02A had to clear.

**Rising Action:** Juanl invokes `app/marcus/cli/trial.py --input course-content/courses/tejal-
APC-C1/`. The pre-gate-marcus shared LLM node fires (Slab 7a 7a.3 substrate); the LLM-driven
directive composer (Slab 7c §02A) reads the corpus, classifies primary `.docx` lesson content
as `role: primary`, classifies `.gitkeep` as ignored, classifies PNG/JPG binaries as
non-text (no `expected_min_words: 200` for binaries), and emits a directive YAML at
`state/config/runs/<run-id>/directive.yaml`. G0 confirm-or-edit fires; Juanl reviews the
directive at the §02A poll surface and edits one expected-min-words value, then submits. Texas
extracts cleanly (no exit-30; the broken-directive guardrail does not engage because the
directive is not broken). The §04A per-plan-unit ratification fires; Juanl approves three plan
units and edits one. §04.5/§04.55 estimator + run-constants lock fires; Juanl approves the run
budget. Irene Pass-1 runs; §05.5 per-slide mode HIL fires for each slide; Juanl picks
narrated-deck for most, motion-enabled-narrated-lesson for two. §06 pre-dispatch package
writers (5 Marcus-bound) emit `gary-slide-content.json`, `gary-fidelity-slides.json`,
`gary-diagram-cards.json`, `gary-theme-resolution.json`, `gary-outbound-envelope.yaml` +
`pre-dispatch-package-gary.md`. §06B literal-visual operator build fires for slides with
diagram requirements. Gary Gamma dispatches; §07B per-slide A/B variant fires; Juanl picks A
for two, B for one. §07C storyboard build + HTML reviewer surface fires. §07D motion-plan
polling fires for the two motion-enabled slides; §07F motion gate fires after Kira returns;
Juanl approves both motion clips. §08B Storyboard B + live-URL HIL fires; Juanl reviews. Vera
G4 fires (19-criterion fidelity). Quinn-R G5 fires (5-sub-check pre-composition QA). §09
four-artifact lock semantics fires. §11 voice-selection HIL fires; Juanl picks ElevenLabs
voice. §11B input-package HIL fires. Compositor §14 assembly bundle ships. §15 final operator
handoff fires.

**Climax:** Trial-3 reaches §15 with one operator-witnessed `edit` verdict at §02A, three more
across §04A/§07B/§07F, full DecisionCard chain emitted at every gate (G0/G0A/G0B/G1/G1A/
G1.5/G2/G2B/G2C/G2M/G2.5/G2F/G3/G3B/G4/G4A/G4B/G5 — exact taxonomy ratified at PRD discovery),
verdict-digest match enforced on every resume (D3), DecisionCardMeta cache_state populated at
every gate (D2), all dispatches via CLI with at least one parity-demonstration via MCP-stdio
or FastAPI (D7).

**Resolution:** M3 evidence accrues. Juanl pastes Trial-3 transcript into
`_bmad-output/implementation-artifacts/m3-acceptance.md`. Both Trial-2 deferred-inventory
entries (finding #1 cp1252 + finding #2 directive-composer-fallback) close formally.
`epics-langchain-langgraph-migration.md` §Epic 3 is updated in-place to record the 7a+7b+7c
replacement. Slab 4 (Cora dev-graph + lockstep + frozen-graph + ledger) opens.

**Capabilities revealed:** §02A LLM-driven composer; PRODUCTION_GATE_IDS expansion to 14;
11 HIL conversational surfaces; 5 Marcus-bound writers; §06B/§07C/§09/§15; UTF-8 round-trip
preservation; D2/D3/D7 enforcement by construction; CLI-minimum + MCP/FastAPI parity-
demonstrated.

### Journey 2 — Operator Trial-3 Edge Case (Primary User, Recovery)

**Persona:** Juanl, mid-Trial-3, with corpus content that has macOS-screenshot Unicode
(U+202F NNBSP) embedded in lesson `.docx` text — the same character that crashed Trial-2 G0
print at attempt 1 (run `d44128e9-...`).

**Opening Scene:** Trial-3 launch on Windows; corpus contains the U+202F-bearing screenshot
caption text Trial-2 first hit.

**Rising Action:** §02A LLM-driven composer reads the corpus including U+202F text. Composer
emits directive YAML; G0 print fires. Per Slab 7c TW-7c-5 amendment (UTF-8-only CI lint
pass), the composer wrote directive bytes via UTF-8-explicit encoding; per the Trial-2
finding #1 fix folded into §02A spec, the print path uses UTF-8 stream wrapping rather than
Windows cp1252 default codepage.

**Climax:** G0 print completes cleanly without `PYTHONIOENCODING=utf-8` workaround. Juanl
sees the directive at §02A poll surface; ratifies; run continues. No structured-stop.

**Resolution:** Trial-2 finding #1 deferred-inventory entry closed by structural construction
(not by workaround). Anti-pattern A11 (Windows-portability) augmented with Slab 7c §02A
worked example.

**Capabilities revealed:** UTF-8 round-trip preservation by construction; Anti-pattern A11
remediation; cp1252-regression test in CI substrate.

### Journey 3 — Dev Agent Authoring a Slab 7c Story (Secondary User, BMAD Discipline)

**Persona:** **Codex** (dev agent under NEW CYCLE per CLAUDE.md `feedback_new_cycle_codex_dev_handoff.md`),
picking up a Slab 7c story spec authored by Claude. Story is `7c.X.<descriptor>` (e.g.
`7c.5.directive-composer-llm-driven` or `7c.6.production-gate-ids-expansion-g0-g0a-g0b`).

**Opening Scene:** Story spec is `ready-for-dev` after Claude authored it via `bmad-create-
story` and ran the migration sandbox-AC validator + governance JSON gate-mode check + Slab
7c PRD invariant check. Claude has authored a Codex dev-handoff prompt at
`_bmad-output/implementation-artifacts/codex-dev-prompt-{story-key}.md` (NEW CYCLE artifact).

**Rising Action:** Codex reads the dev-handoff prompt. T1 readiness reads the Slab 7c PRD
required-readings (this PRD, parent migration PRD, Slab 7b retrospective, pipeline-manifest-
regime cheatsheet if pipeline-manifest paths are touched, anti-patterns, specialist-
migration-template R15 + R-block). T2-T13 cycle: Codex authors source + tests; honors four-
file lockstep on any new gate; respects D2/D3/D7 invariants; declares mandatory transports
per HIL surface at slab-open (TW-7c-6 mitigation); runs ruff + lint-imports + sandbox-AC
validator + class-conformance validator + parity-suite locally. T10 self-review: Codex
flags any tripwire trip (TW-7c-1..6) explicitly.

**Climax:** Codex hands back to Claude. Claude T11 runs `bmad-code-review` on the diff
(adversarial / edge-case / acceptance-auditor layered triage). Findings remediated or
explicitly waived; review record updated in story artifact. Cycle-1 PASS or PASS-WITH-PATCH.

**Resolution:** Story flips `review` → `done` in `sprint-status.yaml`. Atomic commit lands
on `dev/langchain-langgraph-foundation`. Mapping-checklist row flip evidence captured for
Slab 7c retrospective ratification.

**Capabilities revealed:** NEW CYCLE Codex/Claude split; spec → dev-handoff-prompt → T1-T13
discipline; 4-tripwire detection at T10; bmad-code-review at T11; atomic landing.

### Journey 4 — bmad-code-review on a Tripwire Trip (Secondary User, Adversarial)

**Persona:** **Claude** (code-reviewer agent), invoked at story T11 with a Slab 7c diff that
trips TW-7c-3 (PRODUCTION_GATE_IDS expansion without four-file lockstep).

**Opening Scene:** Codex T10 self-review missed the tripwire (or applied a partial fix); the
diff added G0A to PRODUCTION_GATE_IDS but only emitted the Pydantic model — JSON schema +
shape-pin test + golden fixture absent.

**Rising Action:** Claude runs adversarial review (Blind Hunter + Edge Case Hunter +
Acceptance Auditor). Acceptance Auditor catches the AC violation: AC declares four-file
lockstep but diff has 1-of-4 files. Severity: critical (TW-7c-3).

**Climax:** Claude emits HALT-AND-REMEDIATE verdict with PATCH items: (P1) emit JSON schema
at `app/models/decision_cards/schema/g0a.v1.schema.json`; (P2) emit shape-pin test at
`tests/parity/test_decision_card_g0a_shape.py`; (P3) emit golden fixture at
`tests/fixtures/decision_cards/g0a_golden.json`; (P4) update class-conformance validator to
recognize G0A; (P5) re-run parity suite + ruff + lint-imports.

**Resolution:** Codex P1-P5 cycle. Cycle-1 PASS. Story flips `review` → `done`. Tripwire
ledger entry recorded at `sprint-status.yaml::tripwire_events` with `fired_verdict: fired`,
`escalation_action_taken: cycle-1 PATCH P1-P5`, `decision_record_link: <code-review-artifact>`.

**Capabilities revealed:** layered code-review discipline; tripwire ledger recording; HALT-
AND-REMEDIATE → cycle-1 PATCH protocol; class-conformance validator extension.

### Journey 5 — CI Substrate Detecting Parity-Budget Exhaustion (Automated Gatekeeper, TW-7c-6)

**Persona:** **CI substrate** (parity-test runner + ruff + lint-imports + UTF-8 lint pass)
running on every PR-style atomic commit during Slab 7c story dev.

**Opening Scene:** Slab 7c story 7c.X-eleventh-hil-surface lands the last of 11 HIL surfaces.
Parity-test count grew to ~68 cells (current ~15 + 14-gate × 3 transports + 11 HIL × 3 mandatory-
declared transports — exact count depends on declarative outputs).

**Rising Action:** Per TW-7c-6, the slab-close gate runs the parity suite 50 consecutive times
deterministically (`-p no:randomly` + fixed seeds where applicable). On run #34, one parity
cell flakes (1/50 = 2%, exceeds 0.1% per-cell budget by 20×).

**Climax:** Slab-close gate refuses to flip the slab `done`. CI emits the flake fixture +
trace. Tripwire TW-7c-6 fires; party-mode convenes. Murat triages: flake is in HTTP-transport
state-equality assertion under MCP race condition. Mitigation: serialize parity-test execution
on the offending cell (parametrized harness honors per-cell concurrency declaration). Per-
surface transport declaration enforced post-mitigation.

**Resolution:** Mitigation lands as a follow-on story (deferred-inventory entry: zero — closed
in-Slab-7c). Parity suite reruns 50× zero-flake. Slab-close proceeds.

**Capabilities revealed:** parity-budget governance; per-surface transport declaration
discipline; TW-7c-6 enforcement; flake-as-debt principle.

### Journey Requirements Summary

The five journeys reveal these capability areas Slab 7c must deliver:

1. **§02A LLM-driven directive composer** (Journey 1 climax + Journey 2 climax) — replaces
   corpus-scan fallback; UTF-8 round-trip preserved; primary/supporting role classification
   correct on real corpus.
2. **PRODUCTION_GATE_IDS 14-gate expansion with four-file lockstep** (Journey 1 + Journey 4
   tripwire) — Pydantic model + JSON schema + shape-pin test + golden fixture per gate; class-
   conformance validator extended.
3. **11 HIL conversational surfaces with parity-contract coverage** (Journey 1 + Journey 5) —
   per-surface mandatory transport declaration; CLI mandatory; HTTP/MCP opt-in; parity-budget
   honored.
4. **5 Marcus-bound pre-dispatch package writers** (Journey 1 §06) — gary-* artifacts +
   pre-dispatch-package-gary.md.
5. **§06B + §07C + §09 + §15 closeout work** (Journey 1) — literal-visual operator build,
   storyboard build + HTML reviewer surface, four-artifact lock semantics, final operator
   handoff.
6. **Trial-2 finding #1 cp1252 fix** (Journey 2) — folded into §02A spec or shipped pre-§02A;
   UTF-8-only CI lint pass enforced.
7. **D2/D3/D7 invariant enforcement by construction** (Journey 1) — DecisionCardMeta cache_
   state at every gate; OperatorVerdict + override_event audit chain at every HIL; four-
   transport parity contract.
8. **AUDIT-AC verification** (Journey 3 dev-agent T1 readiness) — 5 AUDIT-ACs against
   shipped substrate; gap → 7c.X follow-on per TW-7c-1.
9. **NEW CYCLE Codex/Claude dev-handoff discipline** (Journey 3) — spec → dev-handoff-prompt
   → T1-T13 → T11 bmad-code-review → atomic landing.
10. **Tripwire ledger recording at `sprint-status.yaml::tripwire_events`** (Journey 4 + 5) —
    per-tripwire entries with `fired_verdict` + `escalation_action_taken` + `decision_record_link`.
11. **Slab-close gate parity-budget enforcement** (Journey 5) — 50-run zero-flake baseline;
    per-cell flake budget <0.1%; per-surface transport declaration enforced.
12. **Trial-3 ceremony commitment as separate post-close event** (Journey 1 resolution) — M3
    evidence accrual at named artifact; precedent: Story 7a.8 Trial-1, Story 7b.12 Trial-2.

## Domain-Specific Requirements

The "domain" for Slab 7c is the **LangChain/LangGraph migration governance regime** layered
over the AI-orchestrated course content production substrate. Compliance, constraints, and
risk mitigations below are project-internal but function with regulatory-grade rigor (every
violation is a tripwire with named escalation; no surface ships without structural enforcement).

### Compliance & Regulatory (Project-Internal Compliance Regime)

- **Pipeline-manifest lockstep regime** — per `docs/dev-guide/pipeline-manifest-regime.md` and
  CLAUDE.md §"Pipeline lockstep regime", any Slab 7c diff that touches a path listed in
  `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (manifest itself, L1 check
  script, run_hud.py, progress_map.py, workflow_runner.py, v4.2 pack, v4.2 generator package,
  learning-event schema/capture, etc.) requires the dev agent to read the lockstep cheatsheet
  at T1 before any code. Pack version bumps are governance, not technical. Tier-2 minor
  (e.g., new pipeline step) and Tier-3 major (e.g., new pack family) require party-mode
  consensus BEFORE dev opens. Tier-1 patch proceeds under dev-agent authority gated by Cora's
  block-mode hook. **Slab 7c expectation**: PRODUCTION_GATE_IDS expansion may trigger Tier-2
  (manifest schema bump). Confirm at PRD Step 11 readiness gate before any dev-story opens.
- **Sandbox-AC validator** — per `docs/dev-guide/migration-ac-sandbox-inventory.json` (freeze
  date 2026-04-22) and CLAUDE.md §"LangChain/LangGraph migration — sandbox-AC + gate-mode
  governance", every Slab 7c story must pass
  `python scripts/utilities/validate_migration_story_sandbox_acs.py <story-file>` before
  finalize and again before `bmad-dev-story` opens. Forbidden CLIs in dev-agent AC blocks:
  `docker`, `docker-compose`, `psql`, `pg_dump`, `aws`, `gcloud`, `az`, `gh`, `kubectl`,
  `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`. `ffmpeg` warns. Operator-gated AC
  blocks may use any CLI. Inventory additions to `dev_agent_available` require party-mode
  consensus.
- **Governance JSON gate-mode freeze** — per `docs/dev-guide/migration-story-governance.json`
  (freeze date 2026-04-22). Authoritative gate-mode designation per migration story; do not
  relitigate at story-authoring time. Slab 7c stories will need governance JSON entries
  (single-gate vs dual-gate per story) authored at Slab 7c sprint-planning round.
  Per-story version bump required for any gate-mode change.
- **R15 mapping-checklist authority** — per `docs/dev-guide/specialist-migration-template.md`
  v2.5 R15. Row addition/removal AND row-status flips (❌/⚠️ → ✅) require party-mode
  consensus, NOT dev-agent authority. Spec authors writing acceptance criteria that touch
  the mapping-checklist MUST phrase tests as integrity-preservation invariants over party-
  mode-ratified row updates ("asserts ≥ N FULLY MIGRATED rows" with N = post-retrospective
  floor), not as aspirational dev-agent-authored improvements. Slab 7c retrospective is the
  ratification venue for the orchestrational-tail row flips.
- **D12 cross-slab governance protocol** — per `architecture-langchain-langgraph-migration.md`
  decision D12. Every slab-closing story includes a D12 close protocol AC that preserves
  invariants, captures anti-pattern entries if any, and deepens the migration guide. Slab 7c
  closeout story (probably 7c.last) inherits D12.
- **NEW CYCLE Codex/Claude dev-handoff discipline** — per CLAUDE.md memory entry
  `feedback_new_cycle_codex_dev_handoff.md` and Slab 7a/7b precedent (proven 11× end-to-end).
  Story flow: Claude authors spec via `bmad-create-story` → Claude validates governance JSON
  gate-mode + sandbox-AC + Slab 7c PRD readings → Claude authors `codex-dev-prompt-{story-
  key}.md` → Codex runs T1-T9 + T10 self-review → Claude runs T11 `bmad-code-review` (or
  uses cross-agent reviewer per story designation) → Claude commits + flips
  `review` → `done`. Claude does NOT invoke `bmad-dev-story` directly.
- **Deferred-inventory governance** — per CLAUDE.md §"Deferred inventory governance". Three
  binding consultation points: every epic retrospective; every session hot-start; every new
  story spec that names a follow-on. Inventory at
  `_bmad-output/planning-artifacts/deferred-inventory.md`. Slab 7c retrospective MUST consult
  inventory; close `slab-7c-live-harness-evidence` + Trial-2 finding #1 + Trial-2 finding #2
  entries; file any new follow-ons.

### Technical Constraints (Architectural Invariants by Construction)

- **D2 — Model cascade + DecisionCard cache-state** (per `architecture-langchain-langgraph-
  migration.md` D2). Three-level model cascade (Opus / Sonnet / Haiku per FR54 + Slab 2a.2
  cache-hit-rate measured 95.33% median). Every gate added to PRODUCTION_GATE_IDS MUST emit
  `DecisionCardMeta.cache_state ∈ {"healthy", "mixed", "cold"}` populated with current
  prefix warmth; `affected_nodes: list[str]` named explicitly; `override_trail: list[OverrideEvent]`
  audit chain present. Runtime model-override surface (per original 3.5) MUST emit
  `compute_cache_impact() → OverrideWarning` BEFORE override applies; explicit `confirm_token`
  required. Cache-invalidation warning is operator-visible at every gate.
- **D3 — HIL tamper-evidence** (per `architecture-langchain-langgraph-migration.md` D3 +
  FR34). HIL tamper-evidence enforced at the WRITER boundary via verdict-digest match +
  override-event audit chain, NOT at the operator surface. `OperatorVerdict` Pydantic model
  is `frozen=True`, `validate_assignment=True`, `extra=forbid`. Cross-field validator
  enforces `edit_payload` required iff `verb == "edit"`. `resume_from_verdict()` raises
  `GateError` if `decision_card_digest` doesn't match emitted card. Scheduler-import-
  forbidden (`asyncio.sleep`, `threading.Timer`, `apscheduler`, `schedule`) in
  `app/gates/**` per import-linter contract. Bypass attempt rejected at graph-compile (M3
  evidence per `tests/integration/gates/test_m3_bypass_attempt_rejected.py`).
- **D7 — Operator-surface contract / four-transport parity** (per `architecture-langchain-
  langgraph-migration.md` D7 + FR33). Four authorized transports: CLI
  (`app/marcus/cli/gate_cli.py`), HTTP (`app/http/gate_endpoint.py`), MCP-stdio
  (`app/mcp_server/tools/gate_decide.py`), MCP-subprocess. Same `OperatorVerdict` payload
  via any transport produces byte-identical (or canonicalized-identical) graph-resumption
  state, identical ledger events, identical LangSmith traces. Import-linter Contract C3
  forbids non-bridge modules from importing `app.gates.resume_api`. Each new HIL surface
  declares mandatory transports at slab-open (CLI mandatory; HTTP/MCP opt-in per surface)
  per TW-7c-6 mitigation.
- **Four-file lockstep** — every gate added to PRODUCTION_GATE_IDS MUST land four files
  atomically: (i) Pydantic model at `app/models/decision_cards/<gate>.py`; (ii) JSON schema
  at `app/models/decision_cards/schema/<gate>.v1.schema.json`; (iii) shape-pin test at
  `tests/parity/test_decision_card_<gate>_shape.py`; (iv) golden fixture at
  `tests/fixtures/decision_cards/<gate>_golden.json`. Existing G1/G2C/G3/G4 lockstep is the
  authoritative scaffold — copy-and-extend, no re-derivation. TW-7c-3 fires if four-file
  lockstep is violated.
- **Class-conformance validator** — `scripts/utilities/validate_parity_test_class_conformance.py`
  currently reports 11 conforming activation contracts. Slab 7c MUST NOT regress this floor.
  New gates that introduce new specialist classes (unlikely; most expansion reuses existing
  specialists) extend the validator per Class-A/B/C+/C/D1/D2 taxonomy.
- **Import-linter (≥9 contracts)** — per `pyproject.toml::[tool.importlinter]`. Contracts
  M1-M4 (Marcus orchestrator + dispatch + lane isolation), C1-C3 (Cora lane isolation +
  bridge authority), scheduler-import-forbidden, lane-isolation independence. New HIL
  surfaces MUST NOT introduce new contract violations; new contracts may be added.
- **Parity-test budget** — per TW-7c-6. Current ~15-cell parity matrix; post-Slab-7c
  projection ~68 cells (4.5×). Per-cell flake budget <0.1% over 50-run zero-flake CI baseline.
  Per-surface transport declaration enforced (CLI mandatory; HTTP/MCP opt-in declared at
  slab-open).
- **UTF-8-only encoding** — per TW-7c-5 amendment. CI lint pass enforces UTF-8 on every file
  touched by Slab 7c. Trial-2 finding #1 cp1252 regression is a structural prevention, not
  a workaround. Anti-pattern A11 (Windows-portability) augmented at Slab 7c §02A spec close.
- **CI substrate baseline** — full regression deterministic ≥1403 passed (current floor;
  do not regress). Run with `-p no:randomly` for determinism. Ruff clean across all touched
  files; lint-imports 9+ contracts KEPT.

### Integration Requirements (External Surfaces Slab 7c Touches)

- **OpenAI API (gpt-5.4 + tier cascade)** — per FR54 + Slab 2a.2. Pre-gate-marcus shared
  LLM node (Slab 7a 7a.3) consumes OpenAI for §02A LLM-driven directive composition.
  `OPENAI_API_KEY` required in `.env` (verified loaded at session-start). Live-LLM tests
  marked `@pytest.mark.llm_live`; auto-skip on placeholder sentinel.
- **LangSmith tracing** — per FR48 + parent migration architecture. Every gate-decide and
  HIL-resume call emits a LangSmith trace. Trace parity contract is part of D7 transport
  parity (identical traces across transports).
- **Texas wrangler + retrieval providers** — per Slab 7b 7b.1 hardening. Texas extracts
  per directive (LLM-driven post-§02A). Retrieval providers per
  `skills/bmad-agent-texas/references/retrieval-contract.md` (Shape 3-Disciplined; 16
  entries: 11 locator + 5 retrieval).
- **Specialist body fleet** — 11 specialists activated in Slab 7b (Texas/Quinn-R/Vera/
  Irene Pass-1/Tracy/Gary/Kira/Wanda/Enrique/Dan/Compositor). Slab 7c HIL surfaces dispatch
  to these specialists via routing.py manifest. No new specialist activations in Slab 7c.
- **Gamma API + Kling API + ElevenLabs API + Wondercraft API + Canvas API + CourseArc** —
  external production APIs invoked through specialists during Trial-3. Slab 7c does not add
  new external integrations; it adds the conversational tail that orchestrates dispatches.
- **MCP server + FastAPI + CLI transports** — three operator-facing transports. All three
  bridges shipped (verified at substrate-grep 2026-05-04). Slab 7c HIL surfaces extend the
  transport surface; D7 parity contract enforced per surface.

### Risk Mitigations

- **Risk: §02A LLM-driven composer regression to corpus-scan fallback.**
  Mitigation: TW-7c-2 fires if §02A composer fails Trial-2 finding #1 cp1252 regression on
  preserved fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml`
  +`run.json`). Test asserts LLM composition produces a non-broken directive on the trial
  corpus (no `.gitkeep` as primary; primary `.docx` keeps `role: primary`; PNG/JPG no
  `expected_min_words`). Story-level AC MUST cite this fixture.
- **Risk: PRODUCTION_GATE_IDS expansion silently breaks four-file lockstep on new gates.**
  Mitigation: TW-7c-3 fires (severity critical). Class-conformance validator extended to
  recognize new gate IDs. Code-review (Acceptance Auditor) catches the violation; HALT-
  AND-REMEDIATE → cycle-1 PATCH protocol resolves.
- **Risk: Parity-test flake exposure scales multiplicatively with cell count.**
  Mitigation: TW-7c-6 fires. 50-run zero-flake CI baseline before slab-close. Per-surface
  transport declaration enforces minimum-necessary parity coverage (CLI mandatory; HTTP/MCP
  opt-in). Existing 8-file scaffold is authoritative pattern; parameterized harness, not
  per-surface bespoke test files.
- **Risk: Trial-3 leakage into slab-close evidence (governance erosion).**
  Mitigation: TW-7c-4 fires. Trial-3 = separate post-close ceremony. Precedent ratified by
  Slab 7a 7a.8 (Trial-1) + Slab 7b 7b.12 (Trial-2). Slab 7c retrospective is NOT the venue
  to relitigate.
- **Risk: D2/D3/D7 invariant violation tempts story authors to weaken contract.**
  Mitigation: TW-7c-5 fires (severity critical). Winston's three invariants are non-
  negotiable PRD-level constraints, not story-author judgment calls. PRD Step 11 readiness
  gate verifies every story-spec respects D2/D3/D7. import-linter + class-conformance
  validator + parity suite enforce by construction.
- **Risk: AUDIT-AC discovers gap in shipped substrate, expanding Slab 7c scope mid-flight.**
  Mitigation: TW-7c-1 fires. STOP; file `7c.X.<descriptor>` follow-on; party-mode-consensus
  on absorb-vs-defer. Substrate-grep 2026-05-04 confirmed plumbing on disk for 3.2/3.3/3.4/
  3.5 — gap-discovery probability is bounded.
- **Risk: Cross-slab governance drift (pipeline-manifest, sandbox-AC, governance JSON,
  deferred-inventory) is missed at story-author time.**
  Mitigation: PRD Step 11 readiness gate enforces all four governance surfaces are checked
  before any Slab 7c story opens. Slab 7c sprint-planning round authors governance JSON
  entries for every story up-front.

## Innovation & Novel Patterns

### Detected Innovation Areas

Slab 7c is a closeout migration sub-slab, not a market product — its "innovation" is project-
internal governance and architectural discipline that did not exist in prior slabs. Three
genuine novelties identified:

**1. AUDIT-not-BUILD slab framing.** Slab 7c reframes original Epic 3 carry-forwards
(stories 3.2 DecisionCard schema family, 3.3 OperatorVerdict + ResumeApi tamper-evidence,
3.4 three-transport verdict parity, 3.5 cache-impact override flow) as **verify-then-file-
if-gap AUDIT-ACs** against shipped substrate (substrate-grep 2026-05-04 confirmed plumbing
on disk: 8 transport-parity tests, 7 DecisionCard modules + 5 schemas, 9 import-linter
contracts). No prior slab at this project structurally compressed build-scope to coverage-
only audit. The pattern lifts story authoring out of "re-derive from spec" and into
"verify against shipped substrate, file gaps as 7c.X follow-ons" — a governance posture
that no Slab 1/2a/2b/2c/4/5/6/7a/7b PRD adopted.

**2. Six-tripwire structural enforcement at slab-open with per-tripwire severity.** Slab 7b
introduced the tripwire-ledger pattern (Round-(e) E2 Mary amendment;
`sprint-status.yaml::tripwire_events`); four named K-aggregate tripwires fired evaluation
at Slab 7b waypoints. Slab 7c is the first slab to author **six tripwires at PRD time**
(TW-7c-1..TW-7c-6) with named severity (high vs critical) and named escalation, including
the novel **parity-budget exhaustion tripwire (TW-7c-6)** that emerged from Murat's risk-
model update on substrate-grep evidence. The pattern transforms tripwires from "fired-by-
runtime-evaluation" to "structural-pre-condition-enforced-at-slab-open" — story authors
inherit the tripwire ledger at T1 readiness and cite tripwire-trip evidence at T10 self-
review.

**3. Parity-contract DSL as architectural pre-decision (option-c).** Winston's option-c
framing for the 11 HIL surfaces' transport-parity matrix decides ONCE at PRD whether
parity-test extension proceeds via (a) blind parameter expansion (untenable: ~68 cells at
0.1% per-cell flake = ~1 flake / 15 CI runs), (b) bespoke per-surface tests (untenable:
11 inconsistent decisions; flake-debt compounds), or (c) a parity-contract DSL where each
HIL surface declares mandatory transports at slab-open + self-registers into the
parameterized harness. Option-c is novel for this project — all prior parity work assumed
the existing harness extends by parameter expansion alone. Slab 7c lifts the parity
contract to a first-class declarative artifact.

### Market Context & Competitive Landscape

Not applicable. Slab 7c is a project-internal closeout, not a market-facing product.
Industry context relevant to the architectural innovations:

- **AUDIT-not-BUILD pattern** maps loosely to enterprise software's "preserve-then-extend"
  discipline (e.g., legacy-modernization migration patterns where existing tested code is
  audited before new code lands). Project-internal precedent: Slab 7b retrospective's
  honest-accounting correction of mapping-checklist row flips (Decision 1) — same
  philosophy applied to plumbing-vs-substrate.
- **Tripwire ledger with per-trip severity** maps loosely to incident-response runbook
  discipline (PagerDuty / Opsgenie severity-based escalation). Project-internal precedent:
  Slab 7b Round-(e) E2 (4-tripwire ledger; runtime evaluation only). Slab 7c innovation
  shifts evaluation to slab-open + adds severity grading.
- **Parity-contract DSL** maps loosely to Pact-style consumer-driven contract testing
  (where consumers declare contracts; providers validate against them). Project-internal
  precedent: none — this is a Slab-7c-introduced pattern.

### Validation Approach

Each of the three innovations validates structurally:

**1. AUDIT-not-BUILD validation:** PRD Step 11 implementation-readiness gate verifies the 5
AUDIT-ACs (3.2/3.3/3.4/3.5/3.6) cite specific test paths on disk; substrate-grep evidence
confirmed at PRD authoring time. If any AUDIT-AC discovers a gap during Slab 7c story dev,
TW-7c-1 fires; party-mode-consensus on absorb-vs-defer. Gap rate predicts the audit
framing's accuracy: zero gaps validates AUDIT-not-BUILD; multiple gaps invalidates and
forces partial re-framing toward BUILD.

**2. Six-tripwire validation:** every tripwire records `fired_verdict` (`true`/`false`/
`not_yet_evaluated`), `measured_value`, `escalation_action_taken`, `decision_record_link`
in `sprint-status.yaml::tripwire_events`. Slab 7c retrospective reviews per-tripwire firing
rate + escalation effectiveness. Pattern is validated if (a) no tripwire fires silently
(surfacing failure mode in code review or runtime); (b) every fired tripwire's escalation
prevented downstream damage; (c) tripwire trip rate is bounded (1-2 trips per slab is
healthy; 0 may indicate over-engineering; >3 indicates systemic risk concentration).

**3. Parity-contract DSL validation:** measured at slab-close via per-cell flake rate
across the 50-run CI baseline. <0.1% per-cell flake validates DSL approach; ≥0.1%
indicates DSL is necessary-but-not-sufficient and serialization or fixture-determinism
remediation is required (Murat Journey 5 mitigation pattern).

### Risk Mitigation

**1. AUDIT-not-BUILD risk: shipped substrate has hidden gaps not caught by grep.**
Substrate-grep at PRD authoring is path-presence-based; it does not run the tests or assess
coverage comprehensiveness. Mitigation: AUDIT-ACs are phrased "verify GREEN + comprehensive
(cite test count + AC coverage)" — the dev agent runs the actual tests + greps coverage at
T1 readiness. TW-7c-1 catches discrepancies; party-mode resolves. Fallback if multiple
AUDIT-ACs fail: split Slab 7c into 7c.1 (audit gap-fill) + 7c.2 (orchestrational tail) and
sequence them — accept the velocity cost rather than ship orchestrational work on
unverified substrate.

**2. Six-tripwire risk: tripwire ledger becomes paperwork without runtime enforcement.**
Mitigation: each tripwire has a NAMED escalation that is structurally verifiable (TW-7c-3
must trigger HALT-AND-REMEDIATE with PATCH items; TW-7c-6 must serialize parity execution).
Slab 7c retrospective reviews per-tripwire effectiveness; ineffective tripwires retired.
Fallback: revert to Slab-7b-style 4-tripwire pattern (runtime-evaluation-only) for Slab 8+.

**3. Parity-contract DSL risk: declarative-DSL surface adds complexity that 11-surface
volume doesn't warrant.**
Mitigation: TW-7c-6 is the failure-detection signal. If parity-contract DSL implementation
cost exceeds the scaffold-extension savings, party-mode convenes to re-evaluate option-b
(per-surface bespoke) at the first HIL surface story close. Fallback: option-b absorbs as
many HIL surfaces as possible with shared helpers; option-c DSL retired as Slab-7c-only
experiment.

## Slab 7c Project-Type Architecture

### Project-Type Overview

Slab 7c sits inside the **course-DEV-IDE-with-AGENTS** repo on branch
`dev/langchain-langgraph-foundation` (hybrid clone severed from `upstream/master @ 3ed7c56`
2026-04-24). It is the **third sub-slab in a three-sub-slab decomposition** (7a substrate +
7b body + 7c orchestrational tail) that formally REPLACES original Slab 3 / Epic 3 of
`epics-langchain-langgraph-migration.md`. Architecture is locked in
`architecture-langchain-langgraph-migration.md` (13 decisions D1-D13; 9 amendments accepted
in party-mode Round 1; 15/15 substrate invariants preserving patterns ratified). Slab 7c
operates inside that frozen architectural frame; net-new design decisions are bounded to
the orchestrational-tail surfaces (parity-contract DSL option-c is the single architectural
pre-decision Slab 7c PRD owns).

### Technical Architecture Considerations

#### Marcus Orchestrator (already shipped; Slab 7c extends coverage)

- **Substrate locations (shipped 7a):** `app/marcus/intake.py`,
  `app/marcus/orchestrator/{write_api.py, supervisor.py, routing.py}`,
  `app/marcus/facade.py`, `app/marcus/cli/{trial.py, gate_cli.py, gate_shims/}`.
- **Sanctioned single-writer:** `app/marcus/orchestrator/write_api.py` is the sole importer
  of `app/models/state/run_state.py` per import-linter Contract M1.
- **Lane isolation (shipped 7a):** `app.marcus` and `app.cora` are independence-contract
  isolated (M2 + C1 + C2). Specialists may not import Marcus facade/intake/orchestrator
  (M3). Marcus dispatch stays dependency-light (M4).
- **Cold-start discipline (shipped 7a):** sanctum cold-read every session; fingerprint
  recorded; no in-memory continuity.
- **Slab 7c net-new in Marcus surface:** §02A LLM-driven directive composer (replaces
  corpus-scan fallback; shared LLM-node infrastructure already shipped at 7a.3); 5 Marcus-
  bound pre-dispatch package writers under `app/marcus/orchestrator/writers/` (or similar
  per architecture pattern); §15 final operator handoff orchestration.

#### Specialist Body Fleet (already activated; no new specialists in Slab 7c)

Class-A (hardening): Texas, Quinn-R, Vera. Class-B (refresh): Irene Pass-1.
Class-C+ (sidecar): Tracy. Class-C (port-shape): Gary, Kira, Wanda, Enrique. Class-D1
(LLM-greenfield): Dan. Class-D2 (pipeline-greenfield): Compositor. All 11 closed BMAD-
clean at Slab 7b 2026-05-01 with conforming activation contracts. **Slab 7c HIL surfaces
dispatch to these specialists via `routing.py` manifest; NO new specialist activations.**

#### Gate Family + DecisionCard (4-gate shipped; expanding to 14)

- **Shipped (4 gate families):** `app/models/decision_cards/{base, g1, g2c, g3, g4,
  override_event, vocabulary}.py` + JSON schemas at
  `app/models/decision_cards/schema/{decision_card_base, g1, g2c, g3, g4}.v1.schema.json`.
  Validated by `tests/parity/test_decision_card_*` shape-pin discipline.
- **Expansion target (14 total):** G0/G0A/G0B/G1/G1A/G1.5/G2/G2B/G2C/G2M/G2.5/G2F/G3/G3B/
  G4/G4A/G4B/G5. Exact taxonomy (alias-via-discriminator vs new-shape vs hybrid) ratified
  at PRD Step 8 scoping or PRD Step 11 implementation-readiness gate via party-mode
  re-convene if Winston+Murat have not yet ratified.
- **Four-file lockstep per new gate (TW-7c-3 enforced):** Pydantic model + JSON schema +
  shape-pin test + golden fixture, copy-and-extend from G1/G2C/G3/G4 scaffold.
- **DecisionCardMeta cache_state (D2 enforcement):** every gate populates `cache_state ∈
  {"healthy", "mixed", "cold"}` + `affected_nodes: list[str]` + `override_trail:
  list[OverrideEvent]`.

#### Four-Transport Surface (D7 — already shipped; Slab 7c extends to 11 HIL surfaces)

- **CLI** — `app/marcus/cli/gate_cli.py` (mandatory transport for every gate + every HIL
  surface).
- **HTTP/FastAPI** — `app/http/gate_endpoint.py` (opt-in per-surface declared at slab-open).
- **MCP-stdio** — `app/mcp_server/tools/gate_decide.py` (opt-in per-surface declared at
  slab-open).
- **MCP-subprocess** — covered by parity-test `test_mcp_subprocess_hygiene.py` (opt-in
  per-surface declared at slab-open).
- **Import-linter Contract C3:** only the three authorized bridges may import
  `app.gates.resume_api`. New transports require party-mode consensus + new contract entry.

#### Parity-Contract DSL (Slab 7c architectural pre-decision; option-c)

- **Existing harness (shipped):** `tests/integration/transport_parity/{test_fastapi_mcp_parity.py,
  test_mcp_stdio_smoke.py, test_mcp_subprocess_hygiene.py}` +
  `tests/integration/transports/{test_transport_parity.py, test_override_transport_parity.py,
  test_cli_gate_decide.py, test_http_gate_endpoint.py, test_mcp_gate_decide_tool.py}`.
  ~15-cell parity matrix (5 gate families × 3 transports).
- **Slab 7c DSL (option-c):** each new gate + each new HIL surface declares mandatory
  transports at slab-open via a parity-contract declaration (e.g., `parity_contract.yaml`
  per surface OR a `@parity_contract` decorator on the surface registration). Self-
  registers into the parameterized harness. Per-cell flake budget <0.1% over 50-run zero-
  flake CI baseline (TW-7c-6).
- **Implementation location (proposed):** `app/parity/contracts/` for the DSL primitives;
  per-surface declarations in the surface module itself; harness extension in
  `tests/integration/transport_parity/_harness.py` (or similar).
- **Migration path:** existing 8 parity files refactored to consume DSL primitives in
  Slab 7c story 7c.X-parity-contract-dsl-foundation; subsequent HIL-surface stories register
  their parity contracts.

#### LangGraph State Machine + LangSmith Tracing

- **State location (shipped):** `app/models/state/run_state.py` (sanctioned single-writer).
- **Graph compilation (shipped 7a):** `app/marcus/orchestrator/supervisor.py` Plan-and-Execute
  default; ReAct on `preset: explore`. Manifest-derived `PRODUCTION_GATE_IDS` per FR-A8
  (7a.2).
- **Tracing (shipped, FR48):** every gate-decide and HIL-resume call emits LangSmith trace.
  D7 transport parity contract requires identical traces across transports.
- **Resume semantics (shipped, D3):** `app.gates.resume_api.resume_from_verdict()` raises
  `GateError` on `decision_card_digest` mismatch. Bypass attempts rejected at graph-compile.

### HIL Surface Specification (Slab 7c primary build)

The 11 HIL surfaces and 1 §02A directive-poll surface, each with: code location pattern,
transport declaration, gate code association, OperatorVerdict shape, parity-contract entry.

| Surface | Gate | Mandatory transports | Optional transports | Notes |
|---|---|---|---|---|
| §02A operator-directives poll | G0 | CLI, HTTP, MCP-stdio | MCP-subprocess | Dual-nature (feature + cp1252 fix); first PRD priority |
| §04A per-plan-unit ratification | G1A | CLI | HTTP, MCP-stdio | Per-plan-unit OperatorVerdict |
| §04.5/§04.55 estimator + run-constants lock | G1.5 | CLI, HTTP | MCP-stdio | Run-budget surface |
| §05.5 per-slide mode HIL | G2B | CLI | HTTP, MCP-stdio | narrated-deck vs motion-enabled selection |
| §07B per-slide A/B variant | G2M | CLI | HTTP, MCP-stdio | Variant selection per slide |
| §07D motion-plan polling | G2.5 | CLI | HTTP, MCP-stdio | Async polling pattern |
| §07F motion gate | G2F | CLI, HTTP | MCP-stdio | Motion approval per slide |
| §08B Storyboard B + live-URL HIL | G3B | CLI, HTTP | MCP-stdio | Live-URL review |
| §11 voice-selection HIL | G4A | CLI | HTTP, MCP-stdio | ElevenLabs voice picker |
| §11B input-package HIL | G4B | CLI, HTTP | MCP-stdio | Input-package preview |
| §15 final operator handoff | G5 | CLI, HTTP, MCP-stdio | MCP-subprocess | Slab-close ceremony |

(Mandatory-transport assignments above are PRD Step 7 proposed defaults; PRD Step 11
implementation-readiness re-confirms with party-mode if any are contested.)

### Implementation Considerations

- **Story decomposition target (estimated; finalized at PRD Step 8 scoping):**
  - **Slab opener** (substrate-prep): parity-contract DSL foundation; cp1252 fix folded
    in OR shipped pre-§02A — operator chooses at PRD Step 11.
  - **§02A LLM-driven directive composer** (high priority; dual-nature; carries Trial-2
    finding #1 + #2 retirement).
  - **PRODUCTION_GATE_IDS expansion + four-file lockstep** for the 10 net-new gates
    (G0/G0A/G0B/G1A/G1.5/G2B/G2M/G2.5/G2F/G3B/G4A/G4B/G5 — exact count depends on alias
    decision).
  - **5 Marcus-bound writers** (likely one story per writer or one bundled story; finalize
    at sprint-planning).
  - **11 HIL surfaces** — likely one story per surface; parity-contract DSL extension per
    surface; total story count drives sprint-planning velocity projection.
  - **§06B + §07C + §09 + §15 closeout work** — likely standalone stories.
  - **5 AUDIT-AC verification stories** (one per 3.2/3.3/3.4/3.5/3.6, or bundled if no
    gaps emerge) — file gaps as `7c.X.<descriptor>` follow-ons per TW-7c-1.
  - **Slab-closing story (7c.last)** — D12 close protocol; Slab 7c retrospective triggers;
    mapping-checklist row-flip evidence aggregation; deferred-inventory closure.

- **Gate-mode designation per story:** all stories pre-designated single-gate vs dual-gate
  in `docs/dev-guide/migration-story-governance.json` at Slab 7c sprint-planning round.
  Default: dual-gate for slab-opener + slab-closer + §02A; single-gate for HIL surfaces +
  AUDIT-AC stories. Gate-mode change requires party-mode consensus + governance JSON
  version bump.

- **K-contract per story:** target 1.2-1.5× K (per `docs/dev-guide/story-cycle-efficiency.md`
  K-floor discipline; adopted from Lesson Planner MVP discipline). K-projection at T1
  readiness; tripwire fires at T1 if K-projection >2× K-target.

- **NEW CYCLE Codex/Claude split:** per CLAUDE.md memory. Claude authors spec + dev-handoff
  prompt at `_bmad-output/implementation-artifacts/codex-dev-prompt-{story-key}.md`; Codex
  runs T1-T9 + T10 self-review; Claude runs T11 `bmad-code-review` + commits + flips
  `review` → `done`.

- **Cross-agent code-review per story designation:** per Slab 7b precedent (proven at 7a.1
  + 7b.12), some stories use cross-agent reviewer (Claude reviews Codex; Codex reviews
  Claude) for adversarial diversity. Designation in story spec at PRD Step 8 scoping.

- **Atomic close commits:** per Slab 7a/7b precedent. Each story closes with one atomic
  commit (`feat(slab-7c-<story-key>): close <story> — <one-line summary>`) on
  `dev/langchain-langgraph-foundation`. Sprint-status flip + mapping-checklist evidence
  + deferred-inventory updates land in the same commit.

- **CI substrate (no new infrastructure):** existing `.venv/Scripts/python.exe` invocation
  pattern; ruff + lint-imports + sandbox-AC validator + class-conformance validator +
  parity-suite + pipeline-manifest lockstep + live-API detector + substrate-frozen-paths
  + UTF-8 lint pass. Slab 7c may add UTF-8 lint pass as new CI step (per TW-7c-5
  amendment).

- **Test-flakiness budget:** zero. Per-cell parity flake <0.1% over 50-run zero-flake CI
  baseline before slab-close (TW-7c-6).

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach: Closeout Sub-Slab.** Slab 7c is not an iterative MVP. It is the third in
a three-sub-slab decomposition (7a + 7b + 7c) that formally REPLACES original Epic 3.
There is no "thin slice ship + iterate" path because the slab's purpose IS to retire
prior scope cleanly. Per party-mode 2026-05-04 unanimous Reading 1: full 14-gate +
11-HIL + 5-writer + closeout scope ships in Slab 7c. No descope path. The "MVP-style"
question for Slab 7c is **story sequencing**, not feature gating.

**Resource Requirements:**
- One operator (Juanl) running the BMAD orchestration.
- One spec author (Claude) per NEW CYCLE protocol.
- One dev agent (Codex) per NEW CYCLE protocol; cross-agent code-review (Claude
  reviews Codex; Codex reviews Claude on designated stories) per Slab 7a/7b precedent.
- BMAD party-mode (John + Winston + Amelia + Murat + occasional Mary/Paige) for green-
  lights at sprint-planning, gate-mode designation, mid-flight tripwire firings, and
  retrospective close.
- CI substrate: `.venv/Scripts/python.exe` + ruff + lint-imports + sandbox-AC validator
  + class-conformance validator + parity-suite + pipeline-manifest lockstep + live-API
  detector + UTF-8 lint pass (new). No new infrastructure.

### MVP Feature Set (Phase 1 = Slab 7c entire scope)

**Core User Journeys Supported (all 5 Step 4 journeys):**
- Operator Trial-3 happy path (§01→§15 with all 11 HIL surfaces firing).
- Operator Trial-3 edge case (cp1252 Windows-portability holds end-to-end).
- Dev agent authoring Slab 7c story under NEW CYCLE.
- Code-review (Claude) catching tripwire trips (TW-7c-1..6).
- CI substrate enforcing parity-budget + UTF-8 + tripwire ledger (TW-7c-6).

**Must-Have Capabilities (12 areas, all in-scope; no descope):**
1. §02A LLM-driven directive composer + dual-nature (cp1252 fix folded OR pre-§02A patch).
2. PRODUCTION_GATE_IDS expansion 4 → 14 with four-file lockstep per new gate.
3. 11 HIL surfaces with parity-contract DSL coverage.
4. 5 Marcus-bound pre-dispatch package writers.
5. §06B literal-visual operator build.
6. §07C storyboard build + HTML reviewer surface.
7. §09 four-artifact lock semantics.
8. §15 final operator handoff.
9. 5 AUDIT-AC verification (3.2/3.3/3.4/3.5/3.6).
10. D2/D3/D7 invariant enforcement by construction.
11. Parity-test budget enforcement (50-run zero-flake CI baseline; per-cell <0.1%).
12. Slab-close ceremony (mapping-checklist row flips, deferred-inventory closure,
    Epic 3 in-place retirement note, Slab 7c retrospective).

### Story Decomposition (Slab 7c — finalized at story-decomposition party-mode 2026-05-04)

Story-count target: **~26 stories / ~60-72 pts** post-amendments. Decomposition reviewed
+ ratified at story-decomposition party-mode round 2026-05-04 (John + Winston + Amelia +
Murat ACCEPT-WITH-AMENDMENT × 4). All consolidated amendments folded inline below.

**Wave 0 — ADR + scaffold + cross-cutting infra (must precede Wave 1):**
- **7c.0** Parity-Contract DSL ADR + scaffold + cross-cutting infra foundation.
  **Deliverables:**
  (a) ADR at `docs/dev-guide/adr/0001-parity-contract-dsl.md` documenting registration
  mechanism choice (decorator vs entry-point vs YAML), per-surface transport declaration
  schema (Pydantic vs YAML), refactor target list (the 8 existing parity files);
  (b) scaffold under `app/parity/contracts/__init__.py` + ONE reference contract migrated
  as proof-of-pattern;
  (c) **import-linter Contract C4** (parity-DSL boundary forbidding graph-runtime imports;
  provisional forbidden-list acceptable; per FR-7c-53 + Winston A1);
  (d) **NFR-7c-OD7 self-registration audit harness skeleton** (failing-closed with TODO
  entries acceptable; per Winston A1);
  (e) **`TripwireLedgerEntry` Pydantic-v2 model** + `tripwire_ledger.py` module + JSONL
  append path (per NFR-7c-OD2 + Murat M2; AUDIT-AC asserts `model_validate({...})`
  round-trips for all 6 TW IDs × both severity tiers);
  (f) **TW-7c-4 detection** (live-dispatch scope-creep CI lint via test-naming convention
  + import-graph check; per Murat M1);
  (g) **TW-7c-5 UTF-8 CI lint** (per FR-7c-46 + TW-7c-5 amendment; per Murat M1);
  (h) **TW-7c-6 50-run harness scaffold + per-cell flake-rate calculator** (per Murat M1
  + M5 interim-checkpoint observability);
  (i) **FR-7c-50 override_event audit-chain integrity test scaffold** under
  `tests/audit/test_override_event_chain_integrity.py` (per Amelia A1);
  (j) **FR-7c-54 sanctum-alignment declaration mechanism** (DSL feature; consumed
  per-writer in 7c.17a/17b; per Winston A2).
  **Gate-mode:** dual (architectural pre-decision; one-shot ratification; no relitigation
  downstream). **Cross-agent code-review: MANDATORY** (per John A5 + Murat M6).
  **K-target:** ~1.5×. **Estimated:** ~5 pts (was 3; bumped per Winston A1 + Amelia A1 +
  Murat M1 cross-cutting absorption).
  **Required before 7c.1 implementation opens.**

**Wave 1 — Substrate prep (4 stories; parallel-authorable; mostly post-7c.0):**
- **7c.1** Parity-contract DSL foundation. Authors `app/parity/contracts/` primitives
  per the 7c.0 ADR; refactors existing 8 parity files to consume DSL. Substrate-
  precondition for HIL surface stories. Gate-mode: dual. K-target: ~1.4×. ~3-4 pts.
- **7c.2** cp1252 Windows-portability fix + cp1252 fixture-comparison utility (per
  Murat M1; bumps 7c.2 scope to absorb fixture-utility). **Opens parallel to 7c.0**
  (per John A2 — does NOT wait on 7c.0). Standalone story (not folded into 7c.3a; per
  PRD Step 11 alias-lock decision). Gate-mode: single. K-target: ~1.2×. ~1-2 pts.
- **7c.3a** §02A LLM-driven directive composer body (lifted from old 7c.3; per Winston A4
  + Amelia A2). Replaces corpus-scan fallback; passes Trial-2 forensic-fixture regression
  test (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/`). Dual-nature (feature
  + Trial-2 finding #2 fix; FR-7c-1 + FR-7c-2). Owns **FR-7c-53 C5** (§02A composer
  boundary import-linter contract; per Winston A2). Highest-priority story within
  Slab 7c. Gate-mode: dual. **Cross-agent code-review: MANDATORY** (per Murat M6).
  K-target: ~1.5×. ~4-5 pts.
- **7c.3b** §02A G0 poll-surface canonical HIL pattern (NEW; lifted from old Wave 3 per
  Winston A4). Operator-facing UI + parity-contract declaration + transport handlers
  for §02A operator review/edit/approve at G0 (FR-7c-3 + FR-7c-4). Ships the canonical
  HIL-surface pattern that 7c.6..7c.15 (10 stories) replicate. Gate-mode: dual
  (pattern-author, not pattern-consumer). K-target: ~1.4×. ~2-3 pts.

**Wave 2 — PRODUCTION_GATE_IDS expansion (alias decision LOCKED at PRD Step 11; per
Amelia A3 + Winston A3):**
- **7c.4a** Gate family taxonomy ratification (decision-only spec; party-mode-ratified
  alias map per Amelia A3 — see §Gate Taxonomy below). Gate-mode: single (decision
  artifact; no implementation). K-target: ~1.0×. ~1 pt.
- **7c.4b** Gate-family foundation implementation. Authors shared base classes per
  ratified taxonomy + class-conformance validator extension + **FR-7c-49 OperatorVerdict
  schema-stability harness** (per Amelia A1) + **FR-7c-53 C6 HIL boundaries** (gate-
  family-shaped, single contract covers all 10; per Winston A2) + **TW-7c-3 four-file-
  lockstep checker registration** (per Murat M1). Gate-mode: dual. **Cross-agent
  code-review: MANDATORY** (per John A5 + Murat M6). K-target: ~1.4×. ~3-4 pts.
- **7c.5.G0 .. 7c.5.G6** (8 stories) Per-gate four-file-lockstep authoring for the 8
  net-new gate families per the ratified alias map (G0, G1, G2A, G2C, G3, G4, G5, G6 —
  see §Gate Taxonomy). Each story re-runs TW-7c-3 lockstep checker as AC (per Murat M1).
  Aliases (G0A→G1; G2B/G2M/G2.5/G2F→G2C; G3B→G3; G4A/G4B→G4) inherit parent's lockstep
  contract via the alias-DSL clause defined in 7c.0; no separate stories needed. Each
  story: gate-mode single, K-target ~1.2×, ~1-2 pts.

**Wave 3 — HIL surfaces (10 stories; per-surface overlap with Wave 2 per John A1):**

Each HIL surface story opens **as soon as its specific 7c.5.G<gate> predecessor lands**,
not after all 7c.5.* close (per John A1 wave-overlap). §02A is NOT in Wave 3 (it lives
in 7c.3b per Winston A4 + Amelia A2).

- **7c.6** §04A G1A per-plan-unit ratification (FR-7c-10).
- **7c.7** §04.5 G1.5 estimator (FR-7c-11).
- **7c.8** §04.55 G1.5 run-constants lock (FR-7c-12).
- **7c.9** §05.5 G2B per-slide mode (FR-7c-13).
- **7c.10** §07B G2M per-slide A/B variant (FR-7c-14).
- **7c.11** §07D G2.5 motion-plan polling (FR-7c-15).
- **7c.12** §07F G2F motion gate (FR-7c-16).
- **7c.13** §08B G3B Storyboard B + live-URL (FR-7c-17).
- **7c.14** §11 G4A voice-selection (FR-7c-18).
- **7c.15** §11B G4B input-package + §15 G5 final operator handoff (FR-7c-19).

Each surface authors module + parity-contract declaration + transport handlers + per-
surface OperatorVerdict schema-stability case (FR-7c-49 parametrized; per Amelia A1).
Gate-mode: single. K-target: ~1.3×. ~2-3 pts per story.

**Wave 4 — Pre-dispatch package writers (split into 2 stories per Amelia A4):**
- **7c.17a** 3 Marcus-bound writers (smaller surface area; shared sanctum pattern).
  Owns FR-7c-54 sanctum-alignment consumption for these 3 writers. Gate-mode: single.
  K-target: ~1.3×. ~2 pts.
- **7c.17b** 2 Marcus-bound writers (larger surface area; divergent sanctum) +
  `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md` aggregation. Owns
  FR-7c-54 sanctum-alignment consumption for these 2 writers. Gate-mode: single.
  K-target: ~1.3×. ~2 pts.

**Wave 5 — Closeout work + AUDIT-ACs (split into 6 stories per Amelia A5 + Murat M3):**

Wave-3-close + Wave-4-close interim flake checkpoints (25-run, 0.2% non-gating; per
Murat M5) fire as observability inputs into Wave 5 — cells flaking at 0.15% become
"fix in next available story" items, not slab-blockers.

- **7c.18a** §06B literal-visual operator build (FR-7c-26). Gate-mode: single.
  K-target: ~1.3×. ~1-2 pts.
- **7c.18b** §07C storyboard build + HTML reviewer surface (FR-7c-27). Gate-mode:
  single. K-target: ~1.3×. ~2 pts.
- **7c.19** §09 four-artifact lock semantics (FR-7c-28). Gate-mode: single. K-target:
  ~1.2×. ~1-2 pts.
- **7c.20a** AUDIT-AC: ≥20 shape-pins + ≥11 class-conformance assertions (FR-7c-34 +
  FR-7c-36; pin-style; per Murat M3). Verify-then-file-if-gap; ≥2 gaps trips TW-7c-1.
  Gate-mode: single. K-target: ~1.2×. ~2 pts.
- **7c.20b** AUDIT-AC: ≥15 cells in 5-family × 3-transport matrix populated and green
  (FR-7c-35; fixture-heavy; per Murat M3). Verify-then-file-if-gap; ≥2 gaps trips
  TW-7c-1. Gate-mode: single. K-target: ~1.2×. ~2 pts.
- **7c.20c** AUDIT-AC: 14/14 four-file-lockstep co-commit checks + 6/6 tripwire ledger
  probes (FR-7c-37 + FR-7c-38; per Murat M3). Verify-then-file-if-gap; ≥2 gaps trips
  TW-7c-1. Gate-mode: single. K-target: ~1.2×. ~1-2 pts.

**Wave 5 envelope clause (per Amelia A6):** if any 7c.20a/b/c discovers ≥1 gap, each
gap files as parallel `7c.20.<descriptor>` follow-on (cap 5 follow-ons per AUDIT-AC;
>5 gaps escalates to party-mode impasse). Wave 6 (slab-closer) blocks until all
7c.20.* follow-ons close.

**Wave 6 — Slab-close (split into 2 stories per John A6):**
- **7c.21** Slab 7c integration parity suite + closeout ceremony (analogous to 7a.8 +
  7b.12 minus Epic 3 retirement). Owns: D12 close protocol; mapping-checklist row-flip
  evidence aggregation; deferred-inventory closure (`slab-7c-live-harness-evidence` +
  Trial-2 finding #1 + #2); Slab 7c retrospective trigger; **TW-7c-6 50-run flake
  baseline firing** (per Murat M1 split; harness was scaffolded in 7c.0); **FR-7c-51
  schema_version + Trial3Transcript schema** (per Amelia A1); **Trial-3 readiness AC**
  (per Murat M4): (a) all 6 tripwire ledger entries queryable; (b) R7a precondition
  fixtures present; (c) R7b 120/180 min forensic-evidence harness operational; (d) all
  10 HIL surfaces emit class-conformance markers. Gate-mode: dual. **Cross-agent
  code-review: MANDATORY** (per John A5 + Murat M6 + 7b.12 precedent). K-target: ~1.4×.
  ~4 pts.
- **7c.21a** Epic 3 retirement + live-dispatch wiring (peeled per John A6 — substrate-
  touching change distinct from slab-close ceremony). Authors live-dispatch in
  `run_cache_hit_harness.py` + `run_5_api_smoke.py` (closes
  `slab-7c-live-harness-evidence` deferred-inventory entry); updates
  `epics-langchain-langgraph-migration.md` §Epic 3 in-place to record 7a+7b+7c
  replacement with cross-references to closure artifacts. Gate-mode: single
  (substrate-additive). K-target: ~1.3×. ~1-2 pts.

### Gate Taxonomy (LOCKED at PRD Step 11; per Amelia A3 ratification)

The PRODUCTION_GATE_IDS expansion 4 → 14 lands as **8 net-new gate families** (full
four-file-lockstep authored) + **6 alias gates** (inherit parent's lockstep via
alias-DSL clause defined in 7c.0; no separate four-file-lockstep stories).

| Gate | Story | Treatment | Parent (if alias) |
|---|---|---|---|
| G0 | 7c.5.G0 | Net-new four-file-lockstep | — |
| G0A | (alias) | Alias-DSL clause | G1 |
| G0B | (alias) | Alias-DSL clause | G1 |
| G1 | 7c.5.G1 | Net-new four-file-lockstep | — |
| G1A | (alias) | Alias-DSL clause | G1 |
| G1.5 | 7c.5.G1 | Covered by G1 | (not separate alias; §04.5 + §04.55 share G1.5) |
| G2A | 7c.5.G2A | Net-new four-file-lockstep | — |
| G2B | (alias) | Alias-DSL clause | G2C |
| G2C | 7c.5.G2C | Net-new four-file-lockstep | — |
| G2M | (alias) | Alias-DSL clause | G2C |
| G2.5 | (alias) | Alias-DSL clause | G2C |
| G2F | (alias) | Alias-DSL clause | G2C |
| G3 | 7c.5.G3 | Net-new four-file-lockstep | — |
| G3B | (alias) | Alias-DSL clause | G3 |
| G4 | 7c.5.G4 | Net-new four-file-lockstep | — |
| G4A | (alias) | Alias-DSL clause | G4 |
| G4B | (alias) | Alias-DSL clause | G4 |
| G5 | 7c.5.G5 | Net-new four-file-lockstep | — |
| G6 | 7c.5.G6 | Net-new four-file-lockstep | — |

FR-7c-37 "14/14 four-file-lockstep co-commit checks" satisfied because each alias
inherits the parent's lockstep contract via the alias-DSL clause; AUDIT-AC 7c.20c
verifies inheritance for all 14 gates.

### Cross-Agent Code-Review Designation (PRD-locked; per John A5 + Murat M6)

Pre-designated `cross_agent_review_required: true` in
`docs/dev-guide/migration-story-governance.json` for the four architecturally
load-bearing stories where wrong-call-cost cascades downstream:

- **7c.0** — architectural pre-decision (DSL scaffold, ledger model, three CI lints).
  Wrong call cascades into all 25 downstream stories.
- **7c.3a** — §02A composer dual-nature (feature + Trial-2 finding #2 retirement);
  highest-conceptual-load story in the slab.
- **7c.4b** — gate-family taxonomy foundation; wrong taxonomy = 8 per-gate stories
  inherit the defect.
- **7c.21** — slab-closer; precedent set by 7b.12.

Other stories default to single-agent T11 (Claude reviews Codex per NEW CYCLE) unless
sprint-planning escalates per-story.

### Wave Sequencing Notes (per John A1 + Amelia A7)

- **7c.2 opens parallel to 7c.0** (per John A2; one-line cp1252 fix + utility does NOT
  wait on 7c.0 ADR).
- **Wave 3 opens per-surface** as soon as that surface's specific 7c.5.G<gate>
  predecessor lands, not after all Wave 2 close (per John A1 wave-overlap).
- **D2/D3/D7 per-story self-check at T10** in codex-dev-prompt template — three
  explicit checklist lines per story (D2 cache_state-write; D3 HIL tamper-evidence;
  D7 transport-parity contract-declaration). 7c.21 verifies aggregate cross-story
  integration only (per Winston A5).
- **Interim flake checkpoints** (per Murat M5; non-gating observability):
  Wave-3-close 25-run @ 0.2% threshold; Wave-4-close 25-run @ 0.2%; 7c.21 slab-close
  50-run @ 0.1% gating (TW-7c-6).

### Velocity Estimate (per Amelia A7)

- Wave 0 (1 story dual + cross-agent): ~0.5 day
- Wave 1 (4 stories — 1 dual cross-agent + 3 dual): ~1-1.5 days
- Wave 2 (1 fast single + 1 dual cross-agent + 8 single): ~1.5-2 days
- Wave 3 (10 single, partially overlapping Wave 2 per John A1): ~1-1.5 days
- Wave 4 (2 single): ~0.5 day
- Wave 5 (3 closeout + 3 AUDIT + ≤5 follow-ons cap): ~1-1.5 days
- Wave 6 (1 dual cross-agent + 1 single): ~0.5-1 day

**Realistic actual: 5.5-7 days NEW CYCLE Codex/Claude end-to-end** (vs Slab 7a's flat
8-story 1-day and Slab 7b's 12-story 3-day baselines; Slab 7c's 6-wave sequencing
with hard gates costs the marginal 2-4 days). Operator may collapse Wave 0 into
Wave 1 (7c.0 + 7c.1 same dual-gate session) and parallelize Wave 4+5 — saves ~1 day,
lands at ~4.5-6 days.

**Estimated total: ~26 stories / ~60-72 pts / 5.5-7 days actual.**

### Risk Mitigation Strategy

**Technical Risks:**
- *Parity-contract DSL implementation cost > scaffold-extension savings.* Mitigation:
  TW-7c-6 detection signal; party-mode reconvenes to evaluate option-b at first HIL
  surface story close. Fallback: option-b absorbs as many surfaces as possible with
  shared helpers; option-c retired as Slab-7c-only experiment.
- *§02A LLM-driven composer fails on Trial-2 forensic fixture.* Mitigation: TW-7c-2
  fires; story 7c.3 cannot close until fixture passes. Operator may extend story scope
  or split (7c.3a directive composition + 7c.3b prompt engineering) without touching
  rest of Slab 7c.
- *14-gate expansion blows up four-file-lockstep budget.* Mitigation: TW-7c-3 fires
  per-gate; copy-and-extend from G1/G2C/G3/G4 scaffold caps per-gate effort. Alias-via-
  discriminator decision at 7c.4 minimizes net-new-shape count.
- *Parity-test flake exposure (~68 cells).* Mitigation: TW-7c-6; per-surface mandatory-
  transport declaration enforces minimum coverage; 50-run zero-flake CI baseline before
  slab-close.

**Market / Operator-Experience Risks:**
- *Trial-3 ceremony does not produce M3 evidence cleanly.* Mitigation: Trial-3 is
  separate post-close ceremony (TW-7c-4); failure does not block Slab 7c done flip,
  but does block Slab 4 opening. Operator runs Trial-3 forensics ceremony per Trial-2
  precedent if findings emerge.
- *AUDIT-AC discovers substrate gap, expanding Slab 7c scope mid-flight.* Mitigation:
  TW-7c-1 fires; party-mode-consensus on absorb-vs-defer per gap. Substrate-grep
  2026-05-04 bounded the discovery probability; multiple gaps would force Slab 7c split
  (7c.1-audit-gap-fill + 7c.2-orchestrational-tail).

**Resource / Velocity Risks:**
- *Story count (~21) exceeds Slab 7b's 12 by ~75%.* Mitigation: 14-gate expansion
  authoring is bulk-parallelizable post-7c.4; HIL surface stories are bulk-parallelizable
  post-7c.1; sprint-planning sequences waves to maximize Codex parallel-pickup. Velocity
  projection at sprint-planning will cite Slab 7a's "8 stories closed in ~1 day actual
  vs 7-9 wk plan" precedent (NEW CYCLE proven 11× end-to-end).
- *K-contract violations on individual stories.* Mitigation: K-projection at T1 readiness
  per `docs/dev-guide/story-cycle-efficiency.md`; tripwire fires at T1 if K-projection
  >2× K-target; party-mode reconvenes to split or rescope.
- *Cross-agent code-review (Claude reviews Codex; Codex reviews Claude) capacity.*
  Mitigation: per Slab 7b precedent (Codex T11 cross-agent on 7b.12), only designated
  stories use cross-agent; default is Claude-reviews-Codex. Designation in story spec.

## Functional Requirements

Slab 7c FRs use the prefix `FR-7c-N` paralleling Slab 7b's `FR88-FR113` and Slab 7a's
`FR-A1..FR-A8` namespace conventions. Each FR is a testable capability, implementation-
agnostic, stated as actor + capability. Architectural HOW belongs in
`architecture-langchain-langgraph-migration.md` (D2/D3/D7 etc.) and in story-level T-tasks.

### A. §02A LLM-Driven Directive Composer

- **FR-7c-1** Marcus can compose a directive YAML from a corpus directory using LLM
  reasoning (NOT corpus-scan fallback). Composed output MUST conform to the §02A
  directive Pydantic-v2 model (`validate_assignment=True`, closed-enum red-rejection
  on `role` ∈ {primary, supporting, ignored}); primary `.docx` → `role: primary`,
  supporting binaries (PNG/JPG/PPTX/PDF) → `role: supporting`, ignored files
  (`.gitkeep`, `.DS_Store`, `Thumbs.db`) excluded with `excluded_reason` populated;
  `expected_min_words` populated only for text-bearing roles and absent (not null)
  otherwise. Conformance verified by shape-pin test against the Trial-2 forensic
  fixture per FR-7c-2. **Infra hooks:** composer module path =
  `app/composers/section_02a/composer.py`; fixtures =
  `tests/composers/fixtures/trial-2/{prompt,response}.json`; LLM client injected
  via `composer.compose(state, llm=...)` for fixture-replay determinism.
- **FR-7c-2** Marcus can validate a composed directive against the Trial-2 forensic
  fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/`) and confirm the
  output classifies the same corpus correctly without producing the byte-identical
  broken directive Trial-2 captured.
- **FR-7c-3** Operator can review a composed directive at the §02A poll surface and
  emit one of {`approve`, `edit`, `reject`} verdicts via CLI, FastAPI, or MCP-stdio
  transport, with verdict-digest match enforced on resume.
- **FR-7c-4** Operator can edit field-level directive values at the §02A poll surface
  (e.g., adjusting `expected_min_words` or reclassifying a file's `role`) and have the
  edited directive re-validated before submission.
- **FR-7c-5** Marcus can preserve UTF-8 round-trip across the §02A directive lifecycle
  (compose → write → print → operator review → edit → re-validate → submit) without
  Windows cp1252 codepage corruption on macOS-screenshot Unicode (U+202F NNBSP and
  similar non-ASCII characters).

### B. PRODUCTION_GATE_IDS Expansion (4 → 14)

- **FR-7c-6** Marcus can dispatch DecisionCards at every gate code declared in
  `PRODUCTION_GATE_IDS` after expansion, including G0/G0A/G0B/G1/G1A/G1.5/G2/G2B/G2C/
  G2M/G2.5/G2F/G3/G3B/G4/G4A/G4B/G5 (exact taxonomy ratified at PRD Step 11).
- **FR-7c-7** Each new gate (post-expansion) emits a typed Pydantic-v2 DecisionCard
  conforming to its four-file-lockstep contract — the four files are enumerated
  verbatim: (i) Pydantic model at `app/models/decision_cards/<gate>.py`; (ii) JSON
  schema at `app/models/decision_cards/schema/<gate>.v1.schema.json`; (iii) shape-pin
  test at `tests/parity/test_decision_card_<gate>_shape.py`; (iv) golden fixture at
  `tests/fixtures/decision_cards/<gate>_golden.json`. Each emitted DecisionCard has
  `validate_assignment=True` + closed-enum red-rejection + `DecisionCardMeta.cache_state`
  populated. Co-commit invariant enforced (NFR-7c-M1 + NFR-7c-R6 lockstep at PR + close).
- **FR-7c-8** Class-conformance validator recognizes every new gate ID and reports
  ≥11 conforming activation contracts post-Slab-7c (no regression from current floor).
- **FR-7c-9** Manifest fold-flags + compiler honor every new gate code at runtime per
  FR-A8 (Slab 7a 7a.2 substrate); orchestration_only_nodes lockstep tolerance covers
  any new orchestration-only nodes introduced.

### C. 11 HIL Conversational Surfaces

Each of the 11 HIL surfaces below is a **standalone capability contract** verified by
its own parity-test row (per Step 7 HIL Surface table mandatory-transport assignments).
Mandatory-transport set per surface inherits from Step 7 table and is enforced at
slab-open by FR-7c-20.

- **FR-7c-10** Operator can ratify per-plan-unit content at the §04A surface (gate
  G1A) via mandatory CLI; emit `OperatorVerdict` with verb ∈ {`approve`, `edit`,
  `reject`} per plan unit.
- **FR-7c-11** Operator can review and lock the run-budget estimator at §04.5
  surface (gate G1.5) via mandatory CLI + FastAPI; emit cost-impact-acknowledged
  `OperatorVerdict`.
- **FR-7c-12** Operator can lock run-constants at §04.55 surface (gate G1.5) via
  mandatory CLI + FastAPI; emit run-constants-lock `OperatorVerdict`.
- **FR-7c-13** Operator can select per-slide presentation mode (narrated-deck vs
  motion-enabled-narrated-lesson) at §05.5 surface (gate G2B) via mandatory CLI;
  emit per-slide `OperatorVerdict`.
- **FR-7c-14** Operator can pick A or B variant per slide at §07B surface (gate
  G2M) via mandatory CLI; emit per-slide variant `OperatorVerdict`.
- **FR-7c-15** Operator can poll motion-plan generation status at §07D surface
  (gate G2.5) via mandatory CLI; surface fires async until Kira returns; emit
  poll-completion `OperatorVerdict`.
- **FR-7c-16** Operator can approve or reject motion clips at §07F surface (gate
  G2F) via mandatory CLI + FastAPI; emit per-clip `OperatorVerdict`.
- **FR-7c-17** Operator can review Storyboard B + live-URL content at §08B surface
  (gate G3B) via mandatory CLI + FastAPI; emit storyboard `OperatorVerdict`.
- **FR-7c-18** Operator can pick ElevenLabs voice at §11 surface (gate G4A) via
  mandatory CLI; emit voice-selection `OperatorVerdict`.
- **FR-7c-19** Operator can review the input-package preview at §11B surface
  (gate G4B) via mandatory CLI + FastAPI; emit input-package `OperatorVerdict`.
  Operator can complete the final operator handoff at §15 surface (gate G5) via
  mandatory CLI + FastAPI + MCP-stdio; emit slab-close `OperatorVerdict`.
- **FR-7c-20** Each HIL surface declares its mandatory transports at slab-open via
  the parity-contract DSL (FR-7c-30..33) and self-registers into the parameterized
  parity-test harness.

### D. 5 Marcus-Bound Pre-Dispatch Package Writers (§06)

- **FR-7c-21** Marcus can emit `gary-slide-content.json` per plan unit prior to Gary
  dispatch, conforming to a Pydantic-v2 schema with `validate_assignment=True`.
- **FR-7c-22** Marcus can emit `gary-fidelity-slides.json` per plan unit with
  Vera-fidelity-criteria-prepopulated payload prior to Gary dispatch.
- **FR-7c-23** Marcus can emit `gary-diagram-cards.json` per plan unit with
  literal-visual diagram requirements prior to Gary dispatch.
- **FR-7c-24** Marcus can emit `gary-theme-resolution.json` per plan unit resolving
  experience-profile + creative-directive theme inputs to Gary's expected payload
  shape.
- **FR-7c-25** Marcus can emit `gary-outbound-envelope.yaml` + `pre-dispatch-package-
  gary.md` aggregating all four per-plan-unit packages into a single bundle for
  Gary dispatch. **Envelope schema:** `_bmad/memory/bmad-agent-marcus/schemas/pre-
  dispatch-package.schema.json` (Pydantic-v2; `validate_assignment=True`); fields =
  `{writer_id, target_section, payload_ref, dispatched_at, operator_id}`.

### E. §06B / §07C / §09 / §15 Closeout Surfaces

- **FR-7c-26** Operator can build literal-visual operator content at §06B surface,
  emitting per-slide visual specifications consumed by §07 Gary dispatch.
- **FR-7c-27** Operator can build a storyboard with HTML reviewer surface at §07C,
  with reviewer artifact rendered for §08B Storyboard B + live-URL HIL consumption.
- **FR-7c-28** Marcus can enforce four-artifact lock semantics at §09 (post-Gary +
  post-Kira + post-Vera + post-Quinn-R), preventing downstream advancement until
  all four lock-quartet artifacts are present + consistent.
- **FR-7c-29** Marcus can complete the final operator handoff at §15, emitting the
  full slab-close artifact bundle (assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md
  regen + Trial-3 transcript anchor + slab-close evidence pointer).

### F. Parity-Contract DSL (option-c architectural pre-decision)

- **FR-7c-30** Slab 7c provides a parity-contract DSL primitive set under
  `app/parity/contracts/` (or analogous architecture path) such that surface
  modules can declare their parity contract via decorator or YAML registration.
- **FR-7c-31** The parity-contract DSL self-registers each declared surface into the
  parameterized parity-test harness, replacing the need for per-surface bespoke
  test files.
- **FR-7c-32** The parity-contract DSL enforces a per-surface mandatory-transport
  declaration (CLI mandatory; HTTP/MCP-stdio/MCP-subprocess opt-in per surface);
  surfaces that do not declare mandatory transports are denied parity-test budget.
- **FR-7c-33** The existing 8 transport-parity test files refactor to consume DSL
  primitives, preserving current ~15-cell coverage as the baseline before HIL
  surface registration.

### G. AUDIT-ACs (Verify Shipped Substrate; File Gaps as Follow-Ons)

Each AUDIT-AC carries a quantitative coverage floor; ≥2 gaps in any one AUDIT-AC
trips TW-7c-1 (so AUDIT-ACs cannot quietly become a follow-on factory).

- **FR-7c-34** Slab 7c verifies original Epic 3 story 3.2 (per-gate DecisionCard
  Pydantic family) by asserting `app/models/decision_cards/{base, g1, g2c, g3, g4,
  override_event, vocabulary}.py` + 5 schema JSONs green via shape-pin tests.
  **Coverage floor: ≥20 shape-pin tests on parity-DSL surfaces** (G1/G2C/G3/G4/Override
  × {field-presence, closed-enum red-reject, JSON-Schema emission, golden-fixture
  round-trip}). Any gap files `7c.X.decision-card-shape-pin-gap` follow-on per TW-7c-1.
- **FR-7c-35** Slab 7c verifies original Epic 3 story 3.3 (verdict-authority
  enforcement) by asserting 8 named gate tests green: `test_no_scheduler_import.py`,
  `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`,
  `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`,
  `test_consolidated_decision_card_carries_contributions.py`,
  `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`.
  **Coverage floor: ≥15 cells in 5-family × 3-transport matrix populated and green.**
  Any gap files `7c.X.gate-invariant-coverage-gap` follow-on.
- **FR-7c-36** Slab 7c verifies original Epic 3 story 3.4 (three-transport verdict
  parity) by asserting 8 named parity tests green. **Coverage floor: ≥11 class-
  conformance assertions** (matches current activation-contract validator floor).
  Any gap files `7c.X.transport-parity-cell-gap` follow-on.
- **FR-7c-37** Slab 7c verifies original Epic 3 story 3.5 (cache-impact + operator-id
  override flow) by asserting `test_decision_card_cache_state_populated.py`,
  `test_operator_id_real_source.py`, `test_http_operator_id_header_required.py`
  green; verifying override_event audit chain shape. **Coverage floor: 14/14 four-
  file-lockstep co-commit checks** (one per gate post-expansion). Any gap files
  `7c.X.override-event-coverage-gap` follow-on.
- **FR-7c-38** Slab 7c retires original Epic 3 story 3.6 (M3 evidence accrual) via
  Trial-3 ceremony as a separate post-close event; story 7c.last (slab-closer)
  records Trial-3 readiness. **Coverage floor: 6/6 tripwire ledger probes** (one
  per TW-7c-1..6). M3 evidence accrued post-close in
  `_bmad-output/implementation-artifacts/m3-acceptance.md`.

### H. Tripwire Ledger + Slab Governance

- **FR-7c-39** Slab 7c authors six tripwires (TW-7c-1 through TW-7c-6) at slab-open
  in `sprint-status.yaml::tripwire_events`; each tripwire records `tripwire_id`,
  `story_owner`, `fired_at`, `fired_verdict`, `measured_value`,
  `escalation_action_taken`, `decision_record_link`.
- **FR-7c-40** Story dev-agents and code-reviewers cite tripwire-trip evidence at
  T10 self-review and T11 bmad-code-review; HALT-AND-REMEDIATE protocol applies
  per tripwire severity (high vs critical).
- **FR-7c-41** Slab 7c retrospective reviews per-tripwire firing rate +
  effectiveness; ineffective tripwires are retired; pattern is validated only if
  no tripwire fired silently and every fired tripwire's escalation prevented
  downstream damage.
- **FR-7c-42** Slab 7c retrospective ratifies mapping-checklist row flips per R15
  (party-mode-gated, NOT dev-agent authority); post-Slab-7c FULLY MIGRATED row
  floor lifts from 7 to a higher count reflecting orchestrational-tail flips.
- **FR-7c-43** Slab 7c retrospective consults `deferred-inventory.md` and closes
  `slab-7c-live-harness-evidence` + Trial-2 finding #1 + Trial-2 finding #2 entries;
  files any new follow-ons.

### I. CI Substrate + Quality Gates

- **FR-7c-44** Slab 7c retains the ≥1403 deterministic regression baseline at
  `-p no:randomly` post-close; no story may close with a smaller regression count
  unless the count change is explained in the story's Completion Notes and ratified
  at code-review.
- **FR-7c-45** Slab 7c retains ruff clean + lint-imports ≥9 contracts KEPT +
  sandbox-AC validator PASS + class-conformance ≥11 contracts + pipeline-manifest
  lockstep PASS + live-API detector clean + substrate-frozen-paths invariant held
  across every story close.
- **FR-7c-46** Slab 7c adds a UTF-8-only CI lint pass enforced on every file
  touched by Slab 7c (TW-7c-5 amendment); the lint pass auto-runs in pre-commit
  + CI. **Glob coverage:** `_bmad-output/**/*.md`, `app/**/*.py`,
  `tests/**/*.py`, all golden fixtures under `tests/fixtures/**`, and any path
  declared in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`.
  Files outside the glob are not lint-covered (story author cannot silently
  introduce non-UTF-8 paths to evade the lint).
- **FR-7c-47** Slab 7c parity suite runs 50 consecutive times in CI with zero flakes
  before slab marks done (TW-7c-6); per-cell flake budget <0.1%.
- **FR-7c-48** Slab 7c live-dispatch authoring lands in `run_cache_hit_harness.py` +
  `run_5_api_smoke.py` per `slab-7c-live-harness-evidence` deferred-inventory entry;
  authoring is concentrated in the named harness (TW-7c-4 prevents scope creep into
  non-live-harness stories).

### J. Schema-Stability + NEW CYCLE Discipline (added at FR/NFR sign-off 2026-05-04)

Six FRs added per FR/NFR sign-off party-mode (Amelia + Murat + Winston merged
amendments) to close test-shape gaps that would otherwise force post-close discovery.

- **FR-7c-49** Per-HIL-surface `OperatorVerdict` schema-stability test. Each HIL-
  surface story (FR-7c-10..19 + §02A) lands a discriminated-union variant
  `OperatorVerdict<SurfaceId>` with JSON-schema regen + shape-pin test under
  `tests/schemas/operator_verdict/test_<surface_id>_shape.py`. Each shape-pin
  asserts schema hash stable across CLI/HTTP/MCP-stdio for that surface. With
  11 HIL surfaces × 3 transports = 33 (surface, transport) cells of potential
  drift; per-surface shape-pin closes the drift surface.
- **FR-7c-50** `override_event` audit-chain integrity test. Append-only invariant
  + monotonic timestamp + parent-trace linkage; red-rejection on out-of-order
  events or missing-parent. Shape-pin under
  `tests/audit/test_override_event_chain_integrity.py`. Per-tripwire registration
  test asserts every TW-7c-1..6 entry passes audit-chain validator on emit.
- **FR-7c-51** `schema_version: int` field on every new schema-shape file in Slab
  7c (DecisionCards, OperatorVerdict variants, gary-* writers, Trial-3 transcript)
  per `docs/dev-guide/pydantic-v2-schema-checklist.md` precedent. Bump-on-change
  test asserts schema_version increments when schema hash changes. Trial-3
  transcript schema is its own Pydantic-v2 model `Trial3Transcript` with closed-
  enum on gate-ids and edit/approve event types; shape-pin under
  `tests/trial/test_trial3_transcript_shape.py`.
- **FR-7c-52** Every Slab 7c story spec at `ready-for-dev` produces
  `_bmad-output/implementation-artifacts/codex-dev-prompt-{story-key}.md` per
  NEW CYCLE protocol (CLAUDE.md memory `feedback_new_cycle_codex_dev_handoff.md`):
  Claude authors spec → Claude validates governance JSON gate-mode + sandbox-AC
  + Slab 7c PRD readings → Claude authors `codex-dev-prompt-{story-key}.md` →
  Codex T1-T9 + T10 self-review → Claude T11 `bmad-code-review` → Claude commit
  + flips `review` → `done`. No story bypasses this flow without operator
  authorization.
- **FR-7c-53** Import-linter contracts extended for Slab 7c boundaries
  (`pyproject.toml::[tool.importlinter]`):
  - **C4 (new):** `app/parity/contracts/*` may not import graph-runtime modules
    (`app.gates.resume_api`, `app.marcus.orchestrator.supervisor`,
    `app.marcus.orchestrator.write_api`).
  - **C5 (new):** `app/composers/section_02a/*` may not import corpus-scan
    fallback paths (`app.composers._fallback`, `app.composers.legacy.*`).
  - **C6 (new):** HIL-surface modules may not import each other across surfaces
    (e.g., `app.gates.section_05_5.*` may not import `app.gates.section_07b.*`);
    shared helpers must live in `app.gates._shared.*`.
- **FR-7c-54** Sanctum-invariant declaration for the 5 Marcus-bound writers
  (FR-7c-21..25). Each writer module declares its sanctum-alignment row in the
  Marcus activation block (`_bmad/memory/bmad-agent-marcus/INDEX.md` or
  equivalent) per Slab 7b precedent (memory entry
  `project_slab_7b_skill_md_sanctum_alignment.md`), OR documents an explicit
  Cora-sidecar-style exception in the story spec with rationale.

## Non-Functional Requirements

Slab 7c NFRs use the prefix `NFR-7c-N` paralleling Slab 7b's `NFR-T9..T12 / NFR-CG12..CG20 /
NFR-I9..I13 / NFR-OD3..OD6` and Slab 7a's NFR ranges. NFRs categorize by quality-attribute,
not by code path. Each NFR is testable via existing CI substrate or new tripwire infrastructure.
All NFR amendments from FR/NFR sign-off party-mode 2026-05-04 (John A1 + Winston A3 + Amelia
A9-A11 + Murat A1-A6) are folded inline.

### Performance

- **NFR-7c-P1** §02A LLM-driven directive composition target ≤60s wall-clock for a
  corpus of ≤20 files at gpt-5.4 cache-cold, measured ≤60s p50 / ≤120s p99 over ≥20
  fixture-replay runs; cache-hit path ≤2s p99. **Calibration band semantics** (Murat A1):
  60s–90s = WARN (record + continue); >90s sustained over 3 of 5 runs = REPLAN trigger
  (escalate to party-mode for budget revision or model swap). Initial threshold is
  calibration, not contract — first 5 production runs reset the band.
- **NFR-7c-P2** §02A composer prompt-token count remains stable across N=10 runs
  (variance ≤5%) per Slab 2a.2 cache-hit-rate measurement methodology; targets ≥90%
  cache-hit-rate median[2:] (vs MF1 60% floor; matches Irene Pass-2 95.33% precedent
  established at Story 2a.2 close). **Cache-key normalization rule** (Amelia A10):
  `cache_key = SHA256(normalized_prompt)` where normalization strips `operator_id` +
  timestamps + `run_id` from prompt content so cache hits are not collapsed to ~0% by
  per-run identifiers.
- **NFR-7c-P3** Parity-test suite full run completes within 90 seconds wall-clock at
  current ~15-cell scale; post-Slab-7c at ~68-cell scale, completes within 6 minutes
  wall-clock at `-p no:randomly` deterministic execution. Target slack: 25% under
  target on median-of-5.
- **NFR-7c-P4** HIL surface poll latency (operator submits verdict → graph resumes)
  ≤2s p99 in-process per transport (CLI / HTTP); ≤4s p99 MCP-stdio (stdio framing +
  JSON-RPC round-trip on cold start) (Amelia A11); ≤5s p99 MCP-subprocess (subprocess
  startup overhead). p99 computed over 200 polls per surface in steady-state harness;
  insufficient sample (<50 polls) downgrades reporting to p95 (Murat Q1 nit).
- **NFR-7c-P5** Trial-3 §01→§15 wall-clock budget ≤120 minutes for a single-lesson
  corpus with one operator-witnessed traversal, exclusive of operator decision-time
  at HIL surfaces. >180 min = forensic evidence for Slab 4 PRD's HIL-UX scope, not a
  7c blocker (Murat A3 framing).

### Security

- **NFR-7c-S1** HIL tamper-evidence enforced at the writer boundary per D3 — every
  `OperatorVerdict` carries `decision_card_digest` matching emitted card; resume rejects
  via `GateError` on mismatch. Verified by `tests/integration/gates/test_resume_from_verdict_
  digest_match.py` + `test_resume_from_verdict_card_missing.py`.
- **NFR-7c-S2** Bypass-attempt rejection: synthetic `asyncio.sleep + direct Command(resume=...)`
  injection at any point in the supervisor graph rejected at graph-compile time. Verified
  by `tests/integration/gates/test_m3_bypass_attempt_rejected.py`.
- **NFR-7c-S3** Scheduler-import-forbidden enforced via **import-linter `forbidden`
  contract** (Winston A3) on `app/gates/**` (asyncio.sleep + threading.Timer +
  apscheduler + schedule). Failure mode: CI fails at the `lint-imports` step (FR-7c-45),
  NOT at runtime test-assertion. New HIL surfaces under `app/gates/**` MUST NOT
  introduce scheduler imports.
- **NFR-7c-S4** Single-writer authority enforced via **import-linter Contract M1**
  (Winston A3): `app.marcus.orchestrator.write_api` is sole importer of
  `app.models.state.run_state`. Failure mode: CI fails at `lint-imports`, NOT at
  test-assertion. New writers MUST flow through `write_api`.
- **NFR-7c-S5** Operator-id provenance: every `OperatorVerdict` populates `operator_id`
  from a real operator identifier (not null, not a scheduler name). Verified by
  `tests/integration/transports/test_operator_id_real_source.py` +
  `test_http_operator_id_header_required.py`.
- **NFR-7c-S6** API key handling: `OPENAI_API_KEY` + `LANGSMITH_API_KEY` are read from
  `.env` at module import, never committed to git, never logged in cleartext. `.env`
  is gitignored. Live-LLM tests marked `@pytest.mark.llm_live`; auto-skip on placeholder
  sentinel.
- **NFR-7c-S7** Lane isolation enforced via **import-linter Contracts M2 + C1 + C2 +
  M3 + M4** (Winston A3): `app.marcus ⊥ app.cora` (M2/C1/C2);
  `app.specialists ⊥ app.marcus.facade/intake/orchestrator` (M3); `app.marcus.dispatch`
  dependency-light (M4). Failure mode: CI fails at `lint-imports`, NOT at
  test-assertion. Slab 7c MUST NOT introduce new cross-lane imports.

### Reliability

- **NFR-7c-R1** Zero-flake parity baseline: parity suite runs 50 consecutive times in
  CI with zero flakes before slab marks done (TW-7c-6), **aligned with Slab 7b's
  TW-7b-flake bar** (Murat A2 — spec author MUST confirm Slab 7b's exact number from
  `slab-7b-retrospective.md` before sign-off; match-or-explicitly-supersede). Per-cell
  flake budget <0.1% over rolling 200-run window once available.
- **NFR-7c-R2** Deterministic regression baseline: ≥1403 passed at `-p no:randomly`
  preserved at every story close (no regression from current floor).
- **NFR-7c-R3** Tripwire-ledger completeness: every fired tripwire records all 7
  fields (`tripwire_id`, `story_owner`, `fired_at`, `fired_verdict`, `measured_value`,
  `escalation_action_taken`, `decision_record_link`) in
  `sprint-status.yaml::tripwire_events`. Schema enforced at NFR-7c-OD2 (Pydantic-v2
  `TripwireLedgerEntry`); missing fields invalidate the ledger entry.
- **NFR-7c-R4** Substrate-frozen-paths invariant held across every story close
  (Slab 7b 7b.12 PATCH-4 boundary fixtures + parser at
  `scripts/utilities/check_substrate_frozen_paths.py`); 14 boundary fixtures continue
  to PASS.
- **NFR-7c-R5** Class-conformance validator floor ≥11 contracts maintained across every
  story close (`scripts/utilities/validate_parity_test_class_conformance.py`).
- **NFR-7c-R6** Pipeline-manifest lockstep: every story diff that touches
  `block_mode_trigger_paths` runs lockstep validator at PR-time + close-time PASS.
  Slab 7c expectation: PRODUCTION_GATE_IDS expansion may trigger Tier-2 manifest schema
  bump; party-mode-ratified before dev-story opens.
- **NFR-7c-R7a** Trial-3 coverage floor (Murat A3 + John A3): Trial-3 §01→§15
  end-to-end runs on real-corpus with ≥1 approve at every one of the 14 expanded
  gates. Edit floor is ≥3 edits distributed across at least 3 distinct gates (NOT
  required at every gate). **Failure blocks Slab 4 entry** (recorded in
  `docs/dev-guide/migration-story-governance.json` and re-verified at Slab 4 open).
- **NFR-7c-R7b** Trial-3 budget (Murat A3 + John A3): Trial-3 wall-clock target
  ≤120 minutes exclusive of operator decision-time. >180 min = forensic evidence for
  Slab 4 PRD's HIL-UX scope, not a 7c blocker. Trial-3 *attempt* is a Slab 7c
  slab-close prerequisite (must be attempted + evidence filed at
  `_bmad-output/implementation-artifacts/m3-acceptance.md`); a red Trial-3 attempt
  produces a tripwire-trip + decision-record per NFR-7c-OD3 but does NOT block 7c
  slab-close.

### Maintainability

- **NFR-7c-M1** Four-file-lockstep on every new gate: Pydantic model + JSON schema +
  shape-pin test + golden fixture co-commit-invariant enforced (see
  `tests/parity/test_decision_card_*` shape-pin precedent). Pre-commit hook detects
  mismatch.
- **NFR-7c-M2** AUDIT-AC discipline: all 5 AUDIT-ACs (FR-7c-34 through FR-7c-38) phrased
  as verify-then-file-if-gap with quantitative coverage floors (≥20 shape-pins / ≥15
  matrix cells / ≥11 class-conformance / 14-of-14 four-file-lockstep / 6-of-6 tripwire
  ledger probes). ≥2 gaps in any one AUDIT-AC trips TW-7c-1 (Murat A4).
- **NFR-7c-M3** Story-cycle K-floor discipline: per-story K-projection at T1 readiness
  per `docs/dev-guide/story-cycle-efficiency.md`; tripwire fires at T1 if K-projection
  >2× K-target. Slab 7c K-targets: ~1.2-1.5× per story (per Step 8 decomposition).
- **NFR-7c-M4** NEW CYCLE Codex/Claude dev-handoff discipline (FR-7c-52): every Slab
  7c story flows Claude spec → `codex-dev-prompt-{story-key}.md` → Codex T1-T9 + T10
  self-review → Claude T11 `bmad-code-review` → Claude commit + flip done. No story
  bypasses this flow without operator authorization.
- **NFR-7c-M5** Sandbox-AC validator PASS at every story finalize + every
  `bmad-dev-story` open: `python scripts/utilities/validate_migration_story_sandbox_acs.py
  <story-file>`. Forbidden CLIs in dev-agent AC blocks per
  `docs/dev-guide/migration-ac-sandbox-inventory.json` 2026-04-22 freeze.
- **NFR-7c-M6** Governance JSON gate-mode designation: every Slab 7c story has an
  entry in `docs/dev-guide/migration-story-governance.json` authored at sprint-planning;
  changes require party-mode consensus + version bump.

### Compatibility

- **NFR-7c-X1** Windows-portability: every Slab 7c file is UTF-8-encoded; CI lint pass
  enforces UTF-8 round-trip on every file touched (TW-7c-5 amendment + FR-7c-46 glob).
  Trial-2 finding #1 cp1252 regression is a structural prevention, not a workaround.
  Anti-pattern A11 augmented at §02A spec close.
- **NFR-7c-X2** Multi-transport byte-equivalence: same `OperatorVerdict` payload via
  CLI / HTTP / MCP-stdio / MCP-subprocess produces byte-identical (or canonicalized-
  identical) graph-resumption state, identical ledger events, identical LangSmith
  traces. Verified per FR-7c-30..33 parity-contract DSL coverage + FR-7c-49
  per-surface OperatorVerdict schema-stability.
- **NFR-7c-X3** Path-portability: PowerShell + bash launch helpers (e.g.,
  `7b-12-gate2-evidence-commands.ps1` precedent + `C:\tmp\run-trial-2.sh` Trial-2
  helper) honor Windows + Unix conventions; `pathlib.Path` + `as_posix()` patterns per
  `docs/dev-guide/sanctum-reference-conventions.md` MF7 conventions.
- **NFR-7c-X4** Backward-compatibility with shipped substrate: Slab 7c MUST NOT
  regress any existing test in the ≥1403-test deterministic baseline. Class-conformance
  validator floor preserved; mapping-checklist FULLY MIGRATED row floor preserved
  (post-7b: 7).

### Observability

- **NFR-7c-OD1** LangSmith tracing: every gate-decide and HIL-resume call emits a
  LangSmith trace; `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT` + `LANGSMITH_TRACING` keys
  loaded from `.env`. Trace parity contract is part of D7 transport parity (identical
  traces across transports).
- **NFR-7c-OD2** **Tripwire-ledger 7-field schema enforced via Pydantic-v2 model**
  (Murat A5 — highest-leverage amendment): `TripwireLedgerEntry` with
  `validate_assignment=True`, closed-enum on `tripwire_id` ∈ {TW-7c-1..TW-7c-6} with
  triple-layer red-rejection, timezone-aware datetime (no naive datetimes per 31-1
  finding), UUID4 trace-id with format validation. Shape-pin test (≥7 assertions
  covering all 7 fields + closed-enum red-rejection) lives in frozen-paths fixture.
  Retrospective review is complementary, not a substitute.
- **NFR-7c-OD3** Decision-record linkage: every tripwire trip has a
  `decision_record_link` pointing to the code-review artifact, party-mode round notes,
  or sprint-status amendment that resolved the trip. Linkage is checked at retrospective
  close; missing links invalidate the trip's effectiveness assessment.
- **NFR-7c-OD4** Trial-3 evidence accrual: §01→§15 traversal recorded as canonical
  M3 evidence at `_bmad-output/implementation-artifacts/m3-acceptance.md`; transcript
  pasted into Slab 7c retrospective deferred-inventory closure section. Transcript
  schema enforced by `Trial3Transcript` Pydantic model (FR-7c-51).
- **NFR-7c-OD5** Mapping-checklist row-flip evidence aggregation: Slab 7c retrospective
  records per-row flip evidence (which story closed which row) per R15 party-mode-gated
  authority; floor-bump from 7 to higher count (~17-22 expected).
- **NFR-7c-OD6** Forensic-evidence preservation: Trial-3 forensic artifacts under
  `state/config/runs/<run-id>/` preserved (gitignored but operator-pinned) following
  Trial-2 precedent (`d44128e9-...`, `9eabd5ac-...`, `c8c3b6be-...`, `db05cda7-...`,
  `db276994-...`).
- **NFR-7c-OD7** **Parity-DSL self-registration audit** (Winston A4 — added at
  sign-off): the harness emits a registration manifest (11 HIL surfaces × N declared
  transports + 14 gate families × 3 transports) at CI time; CI fails if cardinality
  is below the declared floor. Same shape as the ≥1403 baseline floor (NFR-7c-R2) — a
  counted invariant. Without this, "self-registration" silently degrades when someone
  forgets an import.
