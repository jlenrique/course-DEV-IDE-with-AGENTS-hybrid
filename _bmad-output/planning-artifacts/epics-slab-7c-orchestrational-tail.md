---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
status: complete
completedAt: 2026-05-04
finalValidation:
  fr_coverage: '54/54 = 100% (FR-7c-1..54 all referenced)'
  nfr_coverage: '37/37 = 100% (P:5 + S:7 + R:8 + M:6 + X:4 + OD:7)'
  tripwire_coverage: '6/6 (TW-7c-1..6) + TW-7c-6a deferred'
  sg_coverage: 'SG-1 (23 mentions) + SG-2 (14) + SG-3 (14) + SG-4 (11) — all 4 standing guardrails enforced'
  story_count: '36 (18 explicit headers + 8 7c.5.G* template + 10 7c.6..7c.15 template = 36)'
  cross_agent_designation: '5 stories (7c.0a + 7c.0b + 7c.3a + 7c.4b + 7c.21)'
  amendments_folded: 'AMEND-2/3/4/5/6/7a/7b/7c/7d + WINSTON-W1/W2/W3/W4/W5/W6 + AMELIA-P1/P2/P3/P4 + JTBD-1/2/3'
partyModeRatification:
  round_1_2026_05_04:
    date: 2026-05-04
    topic: 'Single-epic vs multi-epic decomposition'
    voices: [John, Winston, Amelia, Murat]
    verdict: 'Unanimous (4/4) ratify single-epic; 2 amendments folded'
    amendments_folded:
      - 'Winston: open epic prose with explicit 7c.0 foundational-substrate framing — "Stories 7c.1–7c.25 extend or apply that substrate"'
      - 'Murat: file TW-7c-6a wave-canary as deferred-inventory item (conditional 5-run wave-3-boundary firing). Out-of-scope for Slab 7c; registered shape for future activation.'
  round_2_2026_05_04:
    date: 2026-05-04
    topic: 'Story-decomposition review (35-story shape + AMEND-6 + structural amendments)'
    voices: [John, Winston, Amelia, Murat]
    verdict: 'AMEND-7 (a/b/c/d) + Winston structural triplet (7c.0 split + C4/C5/C6 consolidation + extend-and-audit gate-mode) + Amelia process-discipline triplet + JTBD gap audit ALL FOLDED'
    amendments_folded:
      - 'Winston W1: split 7c.0 → 7c.0a (Decision Foundation) + 7c.0b (Scaffold Foundation); breaking-point rule = >5 decision-bearing artifacts forces split'
      - 'Winston W2: C4/C5/C6 import-linter contracts ALL land in 7c.0a (with empty target lists); 7c.3a + 7c.4b populate targets only. Architectural rule for Slab 7c ADR.'
      - 'Winston W3: promote `extend-and-audit` to a NAMED GATE-MODE distinct from dual-gate-cross-agent. T1 readiness requires (a) diff-against-prior-contract artifact reviewed BEFORE T2 + (b) backward-consumer audit per call site. Applied to 7c.5.G1/G2A/G2C/G3/G4 (5 stories).'
      - 'Winston W4: name the Decision-then-Foundation pattern (7c.4a→7c.4b + 7c.0a→7c.0b) explicitly in the Slab 7c ADR for future-slab reuse.'
      - 'Winston W5: name the 7c.17a/17b partition principle in story spec (architectural vs process partition).'
      - 'Winston W6: D7 transport-DSL-completeness policy — ADR enumerates what DSL does NOT cover + escape-hatch policy.'
      - 'Murat AMEND-7a: per-cell flake budget tightens to <0.05% for 7c-added cells; pre-7c cells grandfather at 0.1%. Codified in 7c.21 + deferred-inventory.'
      - 'Murat AMEND-7b: TW-7c-6a deferred entry adds Pearson correlation check (r > 0.3 between any pair of HIL-surface flake-event vectors during 25-run canary).'
      - 'Murat AMEND-7c: TW-7c-1 firing rule switches from absolute-2-gap to ≥10% gap-rate against combined floor per AUDIT-AC story (7c.20a: ≥4 gaps; 7c.20b: ≥3 gaps; 7c.20c: ≥2 gaps).'
      - 'Murat AMEND-7d-i: TW-7c-3 firing-spec single-source in 7c.4b; seven gate stories (7c.5.G0..G6) cite by reference.'
      - 'Murat AMEND-7d-ii: 7c.0a + 7c.0b AC blocks enumerate scaffold-completeness per tripwire family separately (two PASS/FAIL flags).'
      - 'Murat AMEND-7d-iii: 7c.21 explicit STOP-on-TW-7c-6-fire branch (do NOT proceed to retrospective if TW-7c-6 fires during ceremony).'
      - 'Amelia P1: 7c.2 spec MUST forbid touching 7c.0a/0b deliverable paths (parallel-execution merge-conflict guard).'
      - 'Amelia P2: NEW CYCLE freshness check — Claude re-diffs migration-{story-key}.md against pre-authored codex-dev-prompt at dispatch-time; regenerate if spec hash changed.'
      - 'Amelia P3: Wave-3 G2C-fanout staggering (~30min apart) to prevent T11 review-queue collision; document as Wave-3 dispatch protocol.'
      - 'Amelia P4: extend-and-audit stories include delta-AC verifying prior-gate body file frozen-at-ship hash before extension begins.'
      - 'John JTBD-1: operator-failure-recovery resume path → deferred-inventory entry (out-of-scope for Slab 7c; named for Slab 4 PRD scope).'
      - 'John JTBD-2: tripwire user-surface (operator visibility when tripwire fires) → in-scope for 7c.21 retrospective close artifact + Slab 4 PRD scope for runtime surface.'
      - 'John JTBD-3: paused-trial-resume rendering (4-days-later partial-state bundle) → Slab 4 PRD scope; out-of-scope for Slab 7c.'
      - 'John PM-1: confirm 7c.5.G0..G6 + 7c.6..7c.15 template-section bullets carry per-row delta fields (gate-mode + K + pts + AMEND-5 bucket + four-file paths + predecessor link).'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-05-04-slab-7c.md
  - _bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md
  - _bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md
  - _bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/implementation-artifacts/bmm-workflow-status.yaml
project_name: course-DEV-IDE-with-AGENTS
slab: 7c
slabDescriptor: marcus orchestrational tail
date: 2026-05-04
branch: dev/langchain-langgraph-foundation
prdReference: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md
readinessVerdict: READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS
readinessReport: _bmad-output/planning-artifacts/implementation-readiness-report-2026-05-04-slab-7c.md
storyCountActual: 36  # post-Round-2 party-mode amendment Winston W1: 7c.0 split → 7c.0a + 7c.0b. Original 35 (PRD body count) + 1 (7c.0 split) = 36.
storyCountPreSplit: 35  # PRD §Story Decomposition body pre-Winston-W1-split count: 1 (7c.0) + 4 (Wave 1) + 10 (Wave 2) + 10 (Wave 3) + 2 (Wave 4) + 6 (Wave 5) + 2 (Wave 6) = 35.
storyCountFrontmatterClaim: 26  # PRD frontmatter story_count_final: 26 collapses 7c.5.G0..G6 (8) and 7c.20a/b/c (3) into bundle counts (35 - 7 - 2 = 26). AMEND-6 corrects PRD frontmatter at next edit.
ptsEstimateRange: 60-72
durationEstimateDays: 5.5-7
amendmentsApplied:
  - AMEND-2 preserve 7c.17a/7c.17b numbering (do NOT renumber)
  - AMEND-3 pin specific writer-to-story split — 7c.17a={slide-content,fidelity-slides,diagram-cards}; 7c.17b={theme-resolution,outbound-envelope+pre-dispatch-package-gary.md}
  - AMEND-4 enumerate FR-7c-29 (Marcus-side §15 bundle emission) under 7c.15 alongside FR-7c-19
  - AMEND-5 label 7c.5.G1/G2A/G2C/G3/G4 as "extend-and-audit existing shipped gate to post-Slab-7c contract" (vs G0/G5/G6 = fresh-author)
  - AMEND-6 PRD frontmatter story_count_final 26 → 36 (granular per-gate + per-AUDIT-AC + 7c.0 split count is operationally authoritative)
  - AMEND-7a per-cell flake budget tightens to <0.05% for 7c-added cells (Murat); pre-7c cells grandfather at 0.1%
  - AMEND-7b TW-7c-6a deferred entry adds Pearson correlation check (r > 0.3 between any pair of HIL-surface flake-event vectors during 25-run canary) (Murat)
  - AMEND-7c TW-7c-1 firing rule = ≥10% gap-rate against combined floor per AUDIT-AC story (7c.20a ≥4 / 7c.20b ≥3 / 7c.20c ≥2) (Murat)
  - AMEND-7d TW-7c-3 single-source firing-spec in 7c.4b + 7c.0a/0b per-tripwire-family completeness flags + 7c.21 STOP-on-TW-7c-6-fire branch (Murat)
  - WINSTON-W1 split 7c.0 → 7c.0a + 7c.0b (Decision Foundation + Scaffold Foundation)
  - WINSTON-W2 C4/C5/C6 ALL land in 7c.0a; 7c.3a + 7c.4b populate targets only
  - WINSTON-W3 promote `extend-and-audit` to a NAMED GATE-MODE (5 stories: 7c.5.G1/G2A/G2C/G3/G4) with diff-against-prior-contract + backward-consumer-audit T1 deliverables
  - AMELIA-P1 7c.2 spec forbids touching 7c.0a/0b deliverable paths (parallel-execution merge-conflict guard)
  - AMELIA-P2 NEW CYCLE freshness check at dispatch time (Claude re-diffs spec vs pre-authored codex-dev-prompt; regenerate if spec hash changed)
  - AMELIA-P3 Wave-3 G2C-fanout staggering ~30min apart to prevent T11 review-queue collision
  - AMELIA-P4 extend-and-audit stories include delta-AC verifying prior-gate body file frozen-at-ship hash
  - JTBD-1/2/3 operator-failure-recovery + tripwire-user-surface + paused-trial-resume gaps assigned to Slab 4 PRD scope (out-of-scope for 7c except 7c.21 retrospective close artifact for tripwire visibility)
---

# course-DEV-IDE-with-AGENTS — Slab 7c Orchestrational Tail Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for **Slab 7c — Marcus Orchestrational Tail**, decomposing the 54 FRs + 37 NFRs + 3 architectural invariants (D2/D3/D7) + 6 tripwires + 4 standing guardrails from `prd-slab-7c-orchestrational-tail.md` into 26 implementable stories across 6 waves.

**Sub-slab role:** Slab 7c is the third in a three-sub-slab decomposition (7a substrate + 7b body + 7c orchestrational tail) that formally REPLACES original Slab 3 / Epic 3 of `epics-langchain-langgraph-migration.md`. Original Epic 3 retirement is recorded in-place at Slab 7c retrospective close per FR-7c-43 (story 7c.21a).

**Single-epic decomposition** per Slab 7a + 7b precedent: substrate-completeness is one user-value bundle; multi-epic split would fail the standalone-epic principle (no separable user value within Slab 7c).

## Requirements Inventory

### Functional Requirements

#### A. §02A LLM-Driven Directive Composer (5 FRs)

- **FR-7c-1** Marcus can compose a directive YAML from a corpus directory using LLM reasoning (NOT corpus-scan fallback). Conforms to §02A directive Pydantic-v2 model with `validate_assignment=True` + closed-enum red-rejection on `role` ∈ {primary, supporting, ignored}; primary `.docx` → `role: primary`, supporting binaries → `role: supporting`, ignored files (`.gitkeep`, `.DS_Store`, `Thumbs.db`) excluded with `excluded_reason`. Composer module = `app/composers/section_02a/composer.py`; fixtures under `tests/composers/fixtures/trial-2/`; LLM injected via `composer.compose(state, llm=...)` for fixture-replay determinism.
- **FR-7c-2** Marcus can validate composed directive against Trial-2 forensic fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/`) without reproducing the byte-identical broken directive Trial-2 captured.
- **FR-7c-3** Operator can review composed directive at §02A poll surface and emit {approve, edit, reject} verdicts via CLI / FastAPI / MCP-stdio with verdict-digest match enforced on resume.
- **FR-7c-4** Operator can edit field-level directive values at §02A poll surface and have edited directive re-validated before submission.
- **FR-7c-5** Marcus preserves UTF-8 round-trip across §02A lifecycle (compose → write → print → review → edit → re-validate → submit) without Windows cp1252 codepage corruption on macOS-screenshot Unicode (U+202F NNBSP and similar).

#### B. PRODUCTION_GATE_IDS Expansion 4 → 14 (4 FRs)

- **FR-7c-6** Marcus dispatches DecisionCards at every gate code in `PRODUCTION_GATE_IDS` after expansion (G0/G0A/G0B/G1/G1A/G1.5/G2/G2B/G2C/G2M/G2.5/G2F/G3/G3B/G4/G4A/G4B/G5).
- **FR-7c-7** Each new gate emits typed Pydantic-v2 DecisionCard conforming to four-file-lockstep contract — paths enumerated verbatim: (i) `app/models/decision_cards/<gate>.py`; (ii) `app/models/decision_cards/schema/<gate>.v1.schema.json`; (iii) `tests/parity/test_decision_card_<gate>_shape.py`; (iv) `tests/fixtures/decision_cards/<gate>_golden.json`. `validate_assignment=True` + closed-enum red-rejection + `DecisionCardMeta.cache_state` populated. Co-commit invariant (NFR-7c-M1 + NFR-7c-R6).
- **FR-7c-8** Class-conformance validator recognizes every new gate ID; reports ≥11 conforming activation contracts post-Slab-7c (no regression).
- **FR-7c-9** Manifest fold-flags + compiler honor every new gate code at runtime per FR-A8 (Slab 7a 7a.2 substrate); orchestration_only_nodes lockstep tolerance covers any new orchestration-only nodes.

#### C. 11 HIL Conversational Surfaces (11 FRs)

- **FR-7c-10** Operator ratifies per-plan-unit content at §04A surface (gate G1A) via mandatory CLI; emits `OperatorVerdict` with verb ∈ {approve, edit, reject} per plan unit.
- **FR-7c-11** Operator reviews + locks run-budget estimator at §04.5 surface (gate G1.5) via mandatory CLI + FastAPI; emits cost-impact-acknowledged `OperatorVerdict`.
- **FR-7c-12** Operator locks run-constants at §04.55 surface (gate G1.5) via mandatory CLI + FastAPI; emits run-constants-lock `OperatorVerdict`.
- **FR-7c-13** Operator selects per-slide presentation mode (narrated-deck vs motion-enabled-narrated-lesson) at §05.5 surface (gate G2B) via mandatory CLI; emits per-slide `OperatorVerdict`.
- **FR-7c-14** Operator picks A or B variant per slide at §07B surface (gate G2M) via mandatory CLI; emits per-slide variant `OperatorVerdict`.
- **FR-7c-15** Operator polls motion-plan generation status at §07D surface (gate G2.5) via mandatory CLI; surface fires async until Kira returns; emits poll-completion `OperatorVerdict`.
- **FR-7c-16** Operator approves or rejects motion clips at §07F surface (gate G2F) via mandatory CLI + FastAPI; emits per-clip `OperatorVerdict`.
- **FR-7c-17** Operator reviews Storyboard B + live-URL content at §08B surface (gate G3B) via mandatory CLI + FastAPI; emits storyboard `OperatorVerdict`.
- **FR-7c-18** Operator picks ElevenLabs voice at §11 surface (gate G4A) via mandatory CLI; emits voice-selection `OperatorVerdict`.
- **FR-7c-19** Operator reviews input-package preview at §11B surface (gate G4B) via mandatory CLI + FastAPI; emits input-package `OperatorVerdict`. Operator completes final operator handoff at §15 surface (gate G5) via mandatory CLI + FastAPI + MCP-stdio; emits slab-close `OperatorVerdict`.
- **FR-7c-20** Each HIL surface declares mandatory transports at slab-open via parity-contract DSL (FR-7c-30..33) + self-registers into the parameterized parity-test harness.

#### D. 5 Marcus-Bound Pre-Dispatch Package Writers (5 FRs)

- **FR-7c-21** Marcus emits `gary-slide-content.json` per plan unit prior to Gary dispatch (Pydantic-v2 + `validate_assignment=True`).
- **FR-7c-22** Marcus emits `gary-fidelity-slides.json` per plan unit (Vera-fidelity-criteria-prepopulated).
- **FR-7c-23** Marcus emits `gary-diagram-cards.json` per plan unit (literal-visual diagram requirements).
- **FR-7c-24** Marcus emits `gary-theme-resolution.json` per plan unit (experience-profile + creative-directive theme inputs → Gary payload shape).
- **FR-7c-25** Marcus emits `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md` aggregating all four packages. Envelope schema = `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`; fields = `{writer_id, target_section, payload_ref, dispatched_at, operator_id}`.

#### E. §06B / §07C / §09 / §15 Closeout Surfaces (4 FRs)

- **FR-7c-26** Operator builds literal-visual operator content at §06B surface, emitting per-slide visual specifications consumed by §07 Gary dispatch.
- **FR-7c-27** Operator builds storyboard with HTML reviewer surface at §07C, with reviewer artifact rendered for §08B Storyboard B + live-URL HIL.
- **FR-7c-28** Marcus enforces four-artifact lock semantics at §09 (post-Gary + post-Kira + post-Vera + post-Quinn-R), preventing downstream advancement until all four are present + consistent.
- **FR-7c-29** Marcus completes final operator handoff at §15, emitting full slab-close artifact bundle (assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial-3 transcript anchor + slab-close evidence pointer).

#### F. Parity-Contract DSL (option-c architectural pre-decision; 4 FRs)

- **FR-7c-30** Slab 7c provides parity-contract DSL primitive set under `app/parity/contracts/` such that surface modules declare parity contract via decorator or YAML registration.
- **FR-7c-31** DSL self-registers each declared surface into the parameterized parity-test harness.
- **FR-7c-32** DSL enforces per-surface mandatory-transport declaration (CLI mandatory; HTTP/MCP-stdio/MCP-subprocess opt-in); surfaces that do not declare are denied parity-test budget.
- **FR-7c-33** Existing 8 transport-parity test files refactor to consume DSL primitives, preserving current ~15-cell coverage as baseline.

#### G. AUDIT-ACs (Verify Shipped Substrate; 5 FRs with quantitative coverage floors)

- **FR-7c-34** Verify original 3.2 (per-gate DecisionCard family) — assert `app/models/decision_cards/{base, g1, g2c, g3, g4, override_event, vocabulary}.py` + 5 schema JSONs green via shape-pin tests. Floor: ≥20 shape-pin tests on parity-DSL surfaces.
- **FR-7c-35** Verify original 3.3 (verdict-authority enforcement) — assert 8 named gate tests green: `test_no_scheduler_import.py`, `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`, `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`, `test_consolidated_decision_card_carries_contributions.py`, `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`. Floor: ≥15 cells in 5-family × 3-transport matrix populated and green.
- **FR-7c-36** Verify original 3.4 (three-transport verdict parity) — assert 8 named parity tests green. Floor: ≥11 class-conformance assertions.
- **FR-7c-37** Verify original 3.5 (cache-impact + operator-id override flow) — assert `test_decision_card_cache_state_populated.py`, `test_operator_id_real_source.py`, `test_http_operator_id_header_required.py` green; verify override_event audit chain shape. Floor: 14/14 four-file-lockstep co-commit checks.
- **FR-7c-38** Retire original 3.6 via Trial-3 separate post-close ceremony; story 7c.21 records Trial-3 readiness. Floor: 6/6 tripwire ledger probes (TW-7c-1..6). M3 evidence accrued post-close in `_bmad-output/implementation-artifacts/m3-acceptance.md`.

#### H. Tripwire Ledger + Slab Governance (5 FRs)

- **FR-7c-39** Slab 7c authors six tripwires (TW-7c-1..6) at slab-open in `sprint-status.yaml::tripwire_events`; each records `tripwire_id`, `story_owner`, `fired_at`, `fired_verdict`, `measured_value`, `escalation_action_taken`, `decision_record_link`.
- **FR-7c-40** Story dev-agents + code-reviewers cite tripwire-trip evidence at T10 + T11; HALT-AND-REMEDIATE protocol applies per tripwire severity.
- **FR-7c-41** Slab 7c retrospective reviews per-tripwire firing rate + effectiveness; ineffective tripwires retired.
- **FR-7c-42** Slab 7c retrospective ratifies mapping-checklist row flips per R15 (party-mode-gated, NOT dev-agent authority); FULLY MIGRATED row floor lifts from 7 to higher count.
- **FR-7c-43** Slab 7c retrospective consults `deferred-inventory.md` and closes `slab-7c-live-harness-evidence` + Trial-2 finding #1 + #2 entries; files any new follow-ons.

#### I. CI Substrate + Quality Gates (5 FRs)

- **FR-7c-44** Slab 7c retains ≥1403 deterministic regression baseline at `-p no:randomly`.
- **FR-7c-45** Slab 7c retains ruff clean + lint-imports ≥9 contracts KEPT + sandbox-AC validator PASS + class-conformance ≥11 contracts + pipeline-manifest lockstep PASS + live-API detector clean + substrate-frozen-paths invariant held across every story close.
- **FR-7c-46** Slab 7c adds UTF-8-only CI lint pass enforced on every Slab-7c-touched file (auto-runs in pre-commit + CI). Glob coverage: `_bmad-output/**/*.md`, `app/**/*.py`, `tests/**/*.py`, all golden fixtures under `tests/fixtures/**`, and any path declared in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`.
- **FR-7c-47** Slab 7c parity suite runs 50× consecutively in CI with zero flakes before slab marks done (TW-7c-6); per-cell flake budget <0.1%.
- **FR-7c-48** Slab 7c live-dispatch authoring lands in `run_cache_hit_harness.py` + `run_5_api_smoke.py` per `slab-7c-live-harness-evidence` deferred entry; concentrated in named harness (TW-7c-4 prevents scope creep).

#### J. Schema-Stability + NEW CYCLE Discipline (6 FRs)

- **FR-7c-49** Per-HIL-surface `OperatorVerdict` schema-stability test. Discriminated-union variant per surface + JSON-schema regen + shape-pin under `tests/schemas/operator_verdict/test_<surface_id>_shape.py`. Asserts schema hash stable across CLI/HTTP/MCP-stdio (33 cells).
- **FR-7c-50** `override_event` audit-chain integrity test. Append-only invariant + monotonic timestamp + parent-trace linkage; red-rejection on out-of-order or missing-parent. Shape-pin under `tests/audit/test_override_event_chain_integrity.py`. Per-tripwire registration test asserts every TW-7c-1..6 entry passes audit-chain validator on emit.
- **FR-7c-51** `schema_version: int` field on every new schema-shape file in Slab 7c (DecisionCards, OperatorVerdict variants, gary-* writers, Trial-3 transcript). Bump-on-change test asserts increment when schema hash changes. Trial-3 transcript schema = `Trial3Transcript` Pydantic-v2 with closed-enum on gate-ids and edit/approve event types; shape-pin under `tests/trial/test_trial3_transcript_shape.py`.
- **FR-7c-52** Every Slab 7c story spec at `ready-for-dev` produces `_bmad-output/implementation-artifacts/codex-dev-prompt-{story-key}.md` per NEW CYCLE protocol (Claude spec → governance/sandbox/PRD validation → codex-dev-prompt-*.md → Codex T1-T9 + T10 self-review → Codex drops completion notice into Claude-watched `_bmad-output/implementation-artifacts/_codex-handoff/{story-key}.ready-for-review.md` → Claude T11 `bmad-code-review` → Claude commit + flip done).
- **FR-7c-53** Import-linter contracts extended for Slab 7c boundaries: **C4** `app/parity/contracts/*` may not import graph-runtime modules; **C5** `app/composers/section_02a/*` may not import corpus-scan fallback paths; **C6** HIL-surface modules may not import each other across surfaces (shared helpers in `app.gates._shared.*`).
- **FR-7c-54** Sanctum-invariant declaration for the 5 Marcus-bound writers (FR-7c-21..25). Each writer module declares its sanctum-alignment row in the Marcus activation block per Slab 7b precedent OR documents an explicit Cora-sidecar-style exception with rationale.

**Total FRs: 54.**

### NonFunctional Requirements

#### Performance (5)

- **NFR-7c-P1** §02A LLM-driven composition target ≤60s wall-clock for ≤20-file corpus at gpt-5.4 cache-cold; ≤60s p50 / ≤120s p99 over ≥20 fixture-replay runs; cache-hit ≤2s p99. Calibration band: 60-90s WARN; >90s × 3-of-5 runs = REPLAN trigger.
- **NFR-7c-P2** §02A composer prompt-token count stable across N=10 runs (variance ≤5%); targets ≥90% cache-hit median[2:]; cache-key normalization rule = `cache_key = SHA256(normalized_prompt)` with `operator_id` + timestamps + `run_id` stripped.
- **NFR-7c-P3** Parity-test suite full run ≤90s wall-clock at ~15-cell scale; ≤6 min wall-clock at ~68-cell scale post-Slab-7c at `-p no:randomly`. Slack: 25% under target on median-of-5.
- **NFR-7c-P4** HIL surface poll latency ≤2s p99 in-process per transport (CLI / HTTP); ≤4s p99 MCP-stdio; ≤5s p99 MCP-subprocess. p99 over 200 polls per surface; <50 polls downgrades to p95.
- **NFR-7c-P5** Trial-3 §01→§15 wall-clock budget ≤120 min for single-lesson corpus, exclusive of operator decision-time. >180 min = forensic evidence for Slab 4 PRD's HIL-UX scope.

#### Security (7)

- **NFR-7c-S1** HIL tamper-evidence at writer boundary per D3 — `OperatorVerdict.decision_card_digest` matches emitted card; resume rejects via `GateError` on mismatch.
- **NFR-7c-S2** Bypass-attempt rejection: synthetic `asyncio.sleep + Command(resume=...)` injection rejected at graph-compile time.
- **NFR-7c-S3** Scheduler-import-forbidden via import-linter `forbidden` contract on `app/gates/**` (asyncio.sleep + threading.Timer + apscheduler + schedule).
- **NFR-7c-S4** Single-writer authority via import-linter Contract M1 (`app.marcus.orchestrator.write_api` is sole importer of `app.models.state.run_state`).
- **NFR-7c-S5** Operator-id provenance: every `OperatorVerdict` populates `operator_id` from a real operator identifier.
- **NFR-7c-S6** API key handling: `OPENAI_API_KEY` + `LANGSMITH_API_KEY` from `.env`; never committed; never logged in cleartext. Live-LLM tests `@pytest.mark.llm_live`; auto-skip on placeholder.
- **NFR-7c-S7** Lane isolation via import-linter Contracts M2 + C1 + C2 + M3 + M4.

#### Reliability (8 — R1-R6 + R7a + R7b)

- **NFR-7c-R1** Zero-flake parity baseline: parity suite runs 50× consecutively in CI with zero flakes before slab done; per-cell flake budget <0.1% over rolling 200-run window.
- **NFR-7c-R2** Deterministic regression baseline: ≥1403 passed at `-p no:randomly` preserved at every story close.
- **NFR-7c-R3** Tripwire-ledger completeness: every fired tripwire records all 7 fields. Schema enforced by NFR-7c-OD2.
- **NFR-7c-R4** Substrate-frozen-paths invariant: 14 boundary fixtures continue to PASS via `scripts/utilities/check_substrate_frozen_paths.py`.
- **NFR-7c-R5** Class-conformance validator floor ≥11 contracts maintained.
- **NFR-7c-R6** Pipeline-manifest lockstep: every story diff that touches `block_mode_trigger_paths` runs lockstep validator at PR-time + close-time PASS.
- **NFR-7c-R7a** Trial-3 coverage floor: §01→§15 end-to-end on real-corpus with ≥1 approve at every one of 14 expanded gates; edit floor ≥3 distributed across ≥3 distinct gates. Failure blocks Slab 4 entry.
- **NFR-7c-R7b** Trial-3 budget ≤120 min wall-clock exclusive of operator decision-time. >180 min = forensic evidence for Slab 4 HIL-UX scope, NOT a 7c blocker. Trial-3 *attempt* is slab-close prerequisite (must be attempted + evidence filed at `m3-acceptance.md`); a red attempt produces tripwire-trip + decision-record per NFR-7c-OD3 but does NOT block 7c slab-close.

#### Maintainability (6)

- **NFR-7c-M1** Four-file-lockstep on every new gate; pre-commit hook detects mismatch.
- **NFR-7c-M2** AUDIT-AC discipline: all 5 AUDIT-ACs phrased as verify-then-file-if-gap with quantitative coverage floors. ≥2 gaps in any one AUDIT-AC trips TW-7c-1.
- **NFR-7c-M3** Story-cycle K-floor discipline: per-story K-projection at T1 readiness; tripwire fires if K-projection >2× K-target. Slab 7c K-targets: ~1.2-1.5× per story.
- **NFR-7c-M4** NEW CYCLE Codex/Claude dev-handoff discipline (FR-7c-52); no story bypasses without operator authorization.
- **NFR-7c-M5** Sandbox-AC validator PASS at every story finalize + every `bmad-dev-story` open.
- **NFR-7c-M6** Governance JSON gate-mode designation: every Slab 7c story has an entry in `migration-story-governance.json` authored at sprint-planning.

#### Compatibility (4)

- **NFR-7c-X1** Windows-portability: every Slab 7c file UTF-8-encoded; CI lint pass enforces UTF-8 round-trip per FR-7c-46.
- **NFR-7c-X2** Multi-transport byte-equivalence: same `OperatorVerdict` payload via CLI / HTTP / MCP-stdio / MCP-subprocess produces byte-identical (or canonicalized-identical) graph-resumption state, identical ledger events, identical LangSmith traces.
- **NFR-7c-X3** Path-portability: PowerShell + bash launch helpers honor Windows + Unix conventions; `pathlib.Path` + `as_posix()` patterns.
- **NFR-7c-X4** Backward-compatibility: Slab 7c MUST NOT regress any existing test in ≥1403-test deterministic baseline.

#### Observability (7)

- **NFR-7c-OD1** LangSmith tracing on every gate-decide and HIL-resume call.
- **NFR-7c-OD2** Tripwire-ledger 7-field schema enforced via Pydantic-v2 `TripwireLedgerEntry` (highest-leverage R3 amendment): `validate_assignment=True`, closed-enum on `tripwire_id` ∈ {TW-7c-1..6} with triple-layer red-rejection, timezone-aware datetime, UUID4 trace-id with format validation.
- **NFR-7c-OD3** Decision-record linkage: every tripwire trip has `decision_record_link` pointing to code-review artifact, party-mode notes, or sprint-status amendment.
- **NFR-7c-OD4** Trial-3 evidence accrual: §01→§15 traversal recorded as canonical M3 evidence at `m3-acceptance.md`.
- **NFR-7c-OD5** Mapping-checklist row-flip evidence aggregation per R15 party-mode-gated authority; floor-bump from 7 to higher (~17-22 expected).
- **NFR-7c-OD6** Forensic-evidence preservation: Trial-3 forensic artifacts under `state/config/runs/<run-id>/` preserved (gitignored but operator-pinned).
- **NFR-7c-OD7** Parity-DSL self-registration audit (Winston A4): harness emits registration manifest at CI time; CI fails if cardinality is below declared floor.

**Total NFRs: 37.** (PRD frontmatter says 36; AMEND-1 corrects.)

### Additional Requirements

Architectural invariants + governance regimes inherited from migration architecture and prior slabs:

- **D2** Model cascade + DecisionCard cache_state — every gate emits `DecisionCardMeta.cache_state` ∈ {healthy, mixed, cold} + `affected_nodes` + `override_trail`. Runtime model-override emits `compute_cache_impact() → OverrideWarning` BEFORE override applies.
- **D3** HIL tamper-evidence at writer boundary — `OperatorVerdict` is `frozen=True`, `validate_assignment=True`, `extra=forbid`. Cross-field validator: `edit_payload` required iff `verb == "edit"`. `resume_from_verdict()` raises `GateError` on `decision_card_digest` mismatch. Scheduler-import-forbidden in `app/gates/**`.
- **D7** Operator-surface contract / four-transport parity — CLI / HTTP / MCP-stdio / MCP-subprocess; same payload produces byte-identical (or canonicalized-identical) graph-resumption state, ledger events, LangSmith traces. Import-linter Contract C3 forbids non-bridge imports of `app.gates.resume_api`.
- **Pipeline-manifest lockstep regime** — Tier-1/2/3 governance per `docs/dev-guide/pipeline-manifest-regime.md`. PRODUCTION_GATE_IDS expansion may trigger Tier-2 (manifest schema bump); party-mode consensus required BEFORE 7c.0 lands.
- **Sandbox-AC validator** — every Slab 7c story passes `validate_migration_story_sandbox_acs.py` before finalize and before `bmad-dev-story` opens. Forbidden CLIs in dev-agent AC blocks per `migration-ac-sandbox-inventory.json` 2026-04-22 freeze.
- **Governance JSON gate-mode freeze** — `migration-story-governance.json` 2026-04-22 freeze; gate-mode change requires party-mode + version bump.
- **R15 mapping-checklist authority** — row addition/removal AND row-status flips (❌/⚠️ → ✅) are party-mode-gated. Slab 7c retrospective is the ratification venue for orchestrational-tail row flips.
- **D12 cross-slab governance protocol** — slab-closing story (7c.21) inherits D12 close-protocol AC.
- **NEW CYCLE Codex/Claude dev-handoff discipline** — Claude authors spec + codex-dev-prompt; Codex runs T1-T9 + T10 self-review + drops completion notice into `_bmad-output/implementation-artifacts/_codex-handoff/{story-key}.ready-for-review.md`; Claude T11 `bmad-code-review` + commits + flips done. Claude does NOT invoke `bmad-dev-story` directly.
- **Deferred-inventory governance** — Slab 7c retrospective MUST consult `deferred-inventory.md`; close `slab-7c-live-harness-evidence` + Trial-2 finding #1 + #2; file any new follow-ons.
- **External integrations (no new ones)** — OpenAI gpt-5.4 + tier cascade; LangSmith tracing; Texas wrangler + retrieval providers; 11 specialist body fleet (already activated in 7b); Gamma + Kling + ElevenLabs + Wondercraft + Canvas + CourseArc + Descript external APIs invoked through specialists during Trial-3.

### UX Design Requirements

Not applicable. Slab 7c is back-end orchestration with operator-conversational tail; UX classification = `UX-not-applicable` per Slab 7a + 7b precedent. HIL surface specification with per-surface mandatory transports (FR-7c-10..20 + FR-7c-30..33) is the operator-experience contract.

### FR Coverage Map

All 54 FRs map to **Epic 1** (single-epic decomposition; party-mode-ratified 2026-05-04 unanimous 4/4):

| FR Range | Capability Area | Epic |
|---|---|---|
| FR-7c-1..5 | A. §02A LLM-Driven Directive Composer | Epic 1 |
| FR-7c-6..9 | B. PRODUCTION_GATE_IDS Expansion 4 → 14 | Epic 1 |
| FR-7c-10..20 | C. 11 HIL Conversational Surfaces | Epic 1 |
| FR-7c-21..25 | D. 5 Marcus-Bound Pre-Dispatch Package Writers | Epic 1 |
| FR-7c-26..29 | E. §06B / §07C / §09 / §15 Closeout Surfaces | Epic 1 |
| FR-7c-30..33 | F. Parity-Contract DSL (option-c architectural pre-decision) | Epic 1 |
| FR-7c-34..38 | G. AUDIT-ACs (Verify Shipped Substrate) | Epic 1 |
| FR-7c-39..43 | H. Tripwire Ledger + Slab Governance | Epic 1 |
| FR-7c-44..48 | I. CI Substrate + Quality Gates | Epic 1 |
| FR-7c-49..54 | J. Schema-Stability + NEW CYCLE Discipline | Epic 1 |

**Coverage: 54 / 54 = 100%.** No orphan FRs.

## Epic List

### Epic 1: Slab 7c Marcus Orchestrational Tail

**User Outcome:** Operator (Juanl) launches a Trial-3 corpus run and traverses §01→§15 end-to-end with Marcus as supervisor — directives composed via LLM (not corpus-scan), 14 PRODUCTION_GATE_IDS dispatching DecisionCards, 11 HIL conversational surfaces firing per §-section, 5 Marcus-bound pre-dispatch package writers emitting, four-artifact lock semantics enforced at §09, final operator handoff bundle emitted at §15. The legacy v4.2 prompt-pack's "general-contractor experience" lands as a real LLM-driven orchestrational surface, with adversarial-grade tamper-evidence (D3) + four-transport parity (D7) + cache-state visibility (D2) preserved by construction. Slab 7b body-tier specialists become operationally dispatchable from the orchestrational tail; original Epic 3 retires in-place at Slab 7c retrospective close (jointly with 7a + 7b); Slab 4 (Cora dev-graph + lockstep + ledger) unblocks.

**Foundational substrate (Winston party-mode Round-1 + Round-2 amendments 2026-05-04):** Wave 0 splits per Round-2 W1 amendment into **7c.0a (Decision Foundation)** + **7c.0b (Scaffold Foundation)** — breaking-point rule = >5 decision-bearing artifacts forces split (original 7c.0 carried 10 seams).

- **Story 7c.0a (Decision Foundation; architecture-tier; dual-gate cross-agent MANDATORY)** lands: parity-contract DSL ADR; **C4/C5/C6 import-linter contracts ALL together with empty target lists per Round-2 W2 amendment** (7c.3a + 7c.4b populate targets only); TripwireLedgerEntry Pydantic-v2 model spec (NFR-7c-OD2); FR-7c-50 audit-chain integrity conceptual design.
- **Story 7c.0b (Scaffold Foundation; build-tier; dual-gate cross-agent MANDATORY)** lands: parity-contract DSL scaffold (executable); FR-7c-54 sanctum-alignment DSL feature; NFR-7c-OD7 self-registration audit harness skeleton; TW-7c-4/5/6 detection scaffolds. Consumes 7c.0a's artifacts.

**Stories 7c.1–7c.21a extend or apply that substrate.** Architectural-seam visibility lives inside the epic at the wave-decomposition boundaries; multi-epic split would have fragmented D2/D3/D7 binding language across artifacts.

**Decision-then-Foundation pattern (Winston W4):** the 7c.0a→7c.0b and 7c.4a→7c.4b splits are both instances of the same architectural pattern. Named explicitly in Slab 7c ADR for future-slab reuse.

**`extend-and-audit` named gate-mode (Winston W3):** 7c.5.G1/G2A/G2C/G3/G4 (5 stories) carry the new gate-mode label `dual-gate-cross-agent-CONTRACT-EVOLUTION` with two T1-readiness deliverables — (1) diff-against-prior-contract artifact reviewed BEFORE T2 + (2) backward-consumer audit per call site. AMELIA-P4 adds delta-AC verifying prior-gate body file frozen-at-ship hash before extension.

**D7 transport-DSL-completeness policy (Winston W6):** 7c.0a ADR enumerates what the parity-contract DSL does NOT cover (timeout semantics, streaming, backpressure, error-frame encoding) + escape-hatch policy ("extend the DSL" vs "per-transport addendum documented inline").

**FRs covered:** FR-7c-1 .. FR-7c-54 (all 54)
**NFRs covered:** NFR-7c-P1..P5 + NFR-7c-S1..S7 + NFR-7c-R1..R7b + NFR-7c-M1..M6 + NFR-7c-X1..X4 + NFR-7c-OD1..OD7 (all 37)
**Architectural invariants:** D2 (model cascade + DecisionCard cache_state) + D3 (HIL tamper-evidence at writer boundary) + D7 (four-transport parity)
**Tripwires owned:** TW-7c-1..6 (all 6)
**Standing guardrails preserved:** SG-1 (11-roster) + SG-2 (33-row mapping-checklist) + SG-3 (7-section Composition Spec) + SG-4 (BMB sanctum alignment per body)
**Wave plan:** 6 waves; 36 stories (post-Round-2 W1 split)
- **Wave 0** (2 stories; both dual-gate + cross-agent MANDATORY): 7c.0a Decision Foundation + 7c.0b Scaffold Foundation
- **Wave 1** (4 stories; post-7c.0b; 7c.2 parallel to 7c.0a/0b per John A2 + AMELIA-P1 path-isolation guard): 7c.1 DSL foundation + 7c.2 cp1252 fix + 7c.3a §02A composer + 7c.3b §02A poll-surface canonical HIL pattern
- **Wave 2** (10 stories; alias decision LOCKED at PRD Step 11): 7c.4a taxonomy + 7c.4b foundation + 7c.5.G0..G6 (8 net-new gate stories)
- **Wave 3** (10 stories; per-surface overlap with Wave 2 per John A1): 7c.6..7c.15 HIL followers
- **Wave 4** (2 stories): 7c.17a + 7c.17b (5 Marcus-bound writers split per Amelia A4)
- **Wave 5** (6 stories): 7c.18a §06B + 7c.18b §07C + 7c.19 §09 + 7c.20a/b/c (3 AUDIT-ACs)
- **Wave 6** (2 stories): 7c.21 ceremony (cross-agent) + 7c.21a Epic 3 retirement + live-dispatch wiring

**Cross-agent code-review pre-designated:** 7c.0a + 7c.0b + 7c.3a + 7c.4b + 7c.21 (5 stories post-W1 split)
**Velocity:** 5.5-7 days NEW CYCLE Codex/Claude (collapse-paths to ~4.5-6 available); +0.25 day for 7c.0 split fold = ~6-7.25 days realistic
**Story count:** 36 (post-W1 split; pre-split body was 35; PRD frontmatter `story_count_final: 26` collapsed bundles per AMEND-6)

**Replaces in lineage:** original Epic 3 (Slab 3 Marcus Orchestration; stories 3.1-3.6) of `epics-langchain-langgraph-migration.md` — jointly with Slab 7a + Slab 7b. In-place retirement recorded at Slab 7c retrospective close per FR-7c-43 (story 7c.21a).

**Story count reconciliation:** PRD §Story Decomposition body enumerated **35 stories** pre-split (granular per-gate + per-AUDIT-AC operational count); post-Round-2 Winston W1 amendment splits 7c.0 → 7c.0a + 7c.0b for **36 total**. PRD frontmatter `story_count_final: 26` collapsed 7c.5.G0..G6 (8 stories) and 7c.20a/b/c (3 stories) into bundle counts (35 − 7 − 2 = 26). The 36-story granular count is operationally authoritative. AMEND-6 records PRD frontmatter correction (26 → 36).

## Epic 1: Slab 7c Marcus Orchestrational Tail

(Epic goal statement above in §Epic List.)

---

### Story 7c.0a: Decision Foundation — Parity-Contract DSL ADR + Import-Linter Contracts C4/C5/C6 + TripwireLedgerEntry Schema + Audit-Chain Conceptual Design

As the architect,
I want one architecture-tier story that lands all decision-bearing artifacts (ADR + import-linter contracts + Pydantic schema specs + audit-chain conceptual design) **before** any executable scaffold lands,
So that the Slab 7c architectural decisions crystallize once with cross-agent review, and all downstream stories inherit a frozen architectural substrate that cannot drift mid-slab.

**Story metadata (W1 split):** Wave 0 (architecture-tier; precedes 7c.0b); **dual-gate**; **cross-agent code-review MANDATORY**; K-target ~1.3×; ~3 pts; FR coverage = FR-7c-30..33 (DSL design only — no executable scaffold here) + FR-7c-50 (audit-chain integrity *conceptual design only*) + FR-7c-53 C4/C5/C6 (per W2 — ALL three contracts land here with empty target lists); NFR coverage = NFR-7c-OD2 (TripwireLedgerEntry Pydantic-v2 primary enforcement here).

**Decision-then-Foundation pattern:** 7c.0a (decisions) → 7c.0b (executable scaffold). Same architectural pattern as 7c.4a → 7c.4b.

**Acceptance Criteria:**

**Given** the Winston Round-2 W2 amendment (C4/C5/C6 ALL land in 7c.0a)
**When** the dev-agent updates `pyproject.toml::[tool.importlinter]`
**Then** Contract C4 (parity-DSL boundary) is defined with empty target list ready to populate; Contract C5 (§02A composer boundary) is defined with empty target list (7c.3a populates); Contract C6 (HIL boundaries) is defined with empty target list (7c.4b populates). All three contracts ENFORCE from 7c.0a forward (CI-fail mode at `lint-imports`); empty target list = no current violations + ready-state for downstream population.

**Given** FR-7c-30..33 DSL design
**When** the dev-agent authors `docs/dev-guide/adr/0001-parity-contract-dsl.md`
**Then** the ADR documents (a) registration mechanism choice (decorator vs entry-point vs YAML); (b) per-surface transport declaration schema (Pydantic vs YAML); (c) refactor target list (the 8 existing parity files; refactor lands in 7c.1); (d) **per Winston W6 D7 transport-DSL-completeness policy:** explicit enumeration of what DSL does NOT cover (timeout semantics + streaming + backpressure + error-frame encoding) + escape-hatch policy ("extend the DSL" vs "per-transport addendum documented inline"); (e) **Decision-then-Foundation pattern named explicitly per Winston W4** for future-slab reuse; (f) **AMEND-7d-ii completeness flags:** ADR specifies that 7c.0b AC block enumerates scaffold-completeness per tripwire family separately (TW-7c-4 PASS/FAIL + TW-7c-5 PASS/FAIL + TW-7c-6 PASS/FAIL); composite "all-PASS" insufficient.

**Given** NFR-7c-OD2 (Murat A5 highest-leverage amendment)
**When** the dev-agent lands `TripwireLedgerEntry` Pydantic-v2 model spec at `app/models/tripwire_ledger.py`
**Then** model has `validate_assignment=True`, closed-enum on `tripwire_id` ∈ {TW-7c-1..TW-7c-6} with triple-layer red-rejection, timezone-aware datetime, UUID4 trace-id with format validation. Shape-pin test (≥7 assertions covering all 7 fields + closed-enum red-rejection) lives in frozen-paths fixture. AUDIT asserts `model_validate({...})` round-trips for all 6 TW IDs × both severity tiers.

**Given** FR-7c-50 audit-chain integrity conceptual design
**When** the dev-agent authors the conceptual design section in the ADR
**Then** the design specifies append-only invariant + monotonic timestamp + parent-trace linkage; red-rejection rules on out-of-order or missing-parent (executable test scaffold lives in 7c.0b).

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged (decision artifacts only).

**Story-scoped NFR predicates:** NFR-7c-OD2 primary enforcement; NFR-7c-S3 + S4 + S7 (import-linter contracts CI-enforce from 7c.0a forward); NFR-7c-M5 sandbox-AC validator PASS.

---

### Story 7c.0b: Scaffold Foundation — DSL Scaffold + Sanctum-Alignment DSL Feature + Self-Registration Harness + Tripwire Detection Scaffolds

As the dev-agent,
I want one build-tier story that lands the executable parity-contract DSL scaffold + sanctum-alignment DSL feature + self-registration audit harness skeleton + TW-7c-4/5/6 detection scaffolds,
So that downstream stories (7c.1 + 7c.3a + 7c.4b + 7c.5.* + 7c.6..7c.15 + 7c.17a/b) inherit a working executable substrate.

**Story metadata (W1 split):** Wave 0 (build-tier; consumes 7c.0a); **dual-gate**; **cross-agent code-review MANDATORY**; K-target ~1.4×; ~3-4 pts; FR coverage = FR-7c-30..33 (DSL scaffold executable) + FR-7c-50 (audit-chain integrity scaffold executable) + FR-7c-54 (sanctum DSL feature) + FR-7c-46 (UTF-8 lint pass setup); NFR coverage = NFR-7c-OD7 (self-registration audit skeleton primary enforcement here).

**Acceptance Criteria:**

**Given** 7c.0a's ADR + C4/C5/C6 contract definitions (empty target lists)
**When** the dev-agent lands `app/parity/contracts/__init__.py` + ONE reference contract migrated as proof-of-pattern
**Then** the DSL primitives expose decorator OR YAML-registration interface per the ADR + a self-registration call site that downstream stories will invoke + Contract C4 target list begins populating with `app/parity/contracts/*` entries.

**Given** FR-7c-54 sanctum-alignment DSL feature
**When** the dev-agent lands the DSL primitive
**Then** the primitive accepts a writer module's sanctum-alignment row declaration consumable by 7c.17a/17b per Slab 7b precedent.

**Given** NFR-7c-OD7 (Winston A4 — failing-closed acceptable for this story)
**When** the dev-agent lands the self-registration audit harness skeleton
**Then** the harness emits a registration manifest (initially empty; downstream stories register surfaces) at CI time; CI fails if cardinality is below the declared floor at slab-close (firing in 7c.21).

**Given** FR-7c-50 audit-chain integrity executable scaffold (per 7c.0a conceptual design)
**When** the dev-agent lands `tests/audit/test_override_event_chain_integrity.py`
**Then** the test asserts append-only invariant + monotonic timestamp + parent-trace linkage; red-rejection on out-of-order events or missing-parent.

**Given** Murat M1 detection-infra ownership table
**When** the dev-agent lands TW-7c-4/5/6 detection scaffolds
**Then** TW-7c-4 (live-dispatch scope-creep) lands as CI lint via test-naming convention + import-graph check; TW-7c-5 (UTF-8 violations) lands as the FR-7c-46 UTF-8 CI lint pass with the declared glob; TW-7c-6 (parity flake) lands as 50-run harness scaffold + per-cell flake-rate calculator.

**Given** AMEND-7d-ii (Murat scaffold-completeness per tripwire family)
**When** the dev-agent's done-status is asserted
**Then** the AC block enumerates THREE separate PASS/FAIL flags — TW-7c-4 detection PASS/FAIL + TW-7c-5 detection PASS/FAIL + TW-7c-6 detection PASS/FAIL — composite "all-three-PASS" required for done-flip; ANY one FAIL blocks done.

**Given** AMEND-7a (per-cell flake budget tightens to <0.05% for 7c-added cells)
**When** the dev-agent lands the per-cell flake-rate calculator
**Then** the calculator distinguishes pre-7c cells (grandfathered at 0.1%) from 7c-added cells (<0.05% budget); TW-7c-6 fires per-cell-class accordingly.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 unchanged; SG-3 Composition Spec invariants honored on DSL primitives; **SG-4 sanctum-alignment DSL feature shipped** (consumed by 7c.17a/b).

**Story-scoped NFR predicates:** NFR-7c-M1 (lockstep precondition only); NFR-7c-M5 sandbox-AC validator PASS; NFR-7c-OD7 primary enforcement; NFR-7c-OD2 schema enforcement (consuming 7c.0a's spec).

---

### Story 7c.1: Parity-Contract DSL Foundation (Refactor 8 Existing Files)

As the dev-agent,
I want the parity-contract DSL foundation primitives + the 8 existing transport-parity test files refactored to consume the DSL,
So that subsequent HIL-surface stories (7c.6..7c.15) and per-gate stories (7c.5.G0..G6) self-register into the parameterized harness rather than authoring per-surface bespoke tests.

**Story metadata:** Wave 1 (post-7c.0b scaffold close; substrate-precondition for HIL surface stories); **dual-gate**; K-target ~1.4×; ~3-4 pts; FR coverage = FR-7c-30..33 (DSL primitives + self-registration + transport-declaration enforcement + 8-file refactor); NFR coverage = NFR-7c-P3 (parity-test suite ≤90s wall-clock at ~15-cell scale).

**Acceptance Criteria:**

**Given** the 7c.0a ADR + 7c.0b scaffold
**When** the dev-agent lands `app/parity/contracts/` primitives per the ADR
**Then** the primitives expose decorator + YAML-registration interface; surface modules can declare parity contract at module level.

**Given** the existing 8 transport-parity test files (`tests/integration/transport_parity/{test_fastapi_mcp_parity.py, test_mcp_stdio_smoke.py, test_mcp_subprocess_hygiene.py}` + `tests/integration/transports/{test_transport_parity.py, test_override_transport_parity.py, test_cli_gate_decide.py, test_http_gate_endpoint.py, test_mcp_gate_decide_tool.py}`)
**When** the dev-agent refactors them to consume DSL primitives
**Then** all 8 files pass after refactor + parity matrix coverage at ~15-cell baseline preserved + zero regression in `tests/parity/` suite.

**Given** FR-7c-32 (per-surface mandatory-transport declaration enforcement)
**When** a surface module attempts to register without declaring mandatory transports
**Then** the DSL denies parity-test budget + raises a typed exception at registration.

**Given** NFR-7c-P3
**When** the parity-test suite runs at ~15-cell post-refactor scale
**Then** wall-clock ≤90s with 25% slack on median-of-5.

**Standing-guardrail enforcement:** SG-1/2/4 unchanged; SG-3 Composition Spec §3.1/§3.5/§3.6 honored on DSL primitive contract.

**Story-scoped NFR predicates:** NFR-7c-P3 (suite wall-clock); NFR-7c-R2 (≥1403 baseline preserved); NFR-7c-X4 (no test regressions).

---

### Story 7c.2: cp1252 Windows-Portability Fix + Fixture-Comparison Utility

As the operator,
I want UTF-8 round-trip preservation across the §02A directive lifecycle on Windows + a cp1252 fixture-comparison utility that catches regressions on macOS-screenshot Unicode (U+202F NNBSP and similar),
So that Trial-2 finding #1 (G0 print cp1252 crash) is structurally retired by construction (not by `PYTHONIOENCODING=utf-8` workaround).

**Story metadata:** Wave 1; **opens parallel to 7c.0a + 7c.0b** (per John A2 — does NOT wait); single-gate; K-target ~1.2×; ~1-2 pts; FR coverage = FR-7c-5 (UTF-8 round-trip); owns TW-7c-2 detection (cp1252 regression) + TW-7c-5 partial (cp1252 encoding regression).

**AMELIA-P1 path-isolation guard (parallel-execution merge-conflict prevention):** 7c.2 spec MUST forbid touching any artifact 7c.0a or 7c.0b produces. Forbidden paths: `app/parity/contracts/**`, `app/models/tripwire_ledger.py`, `tests/audit/test_override_event_chain_integrity.py`, `docs/dev-guide/adr/0001-parity-contract-dsl.md`, `pyproject.toml::[tool.importlinter]` C4/C5/C6 contract definitions, TW-7c-4/5/6 detection scaffolds. AC explicit: "MUST NOT modify files under <7c.0a/0b deliverable paths>."

**Acceptance Criteria:**

**Given** the Trial-2 finding #1 cp1252 print crash root cause
**When** the dev-agent identifies the print-path codepath that defaults to Windows cp1252
**Then** the print-path uses UTF-8 stream wrapping + writes directive bytes via UTF-8-explicit encoding everywhere `state/config/runs/<run-id>/directive.yaml` is read or written.

**Given** the cp1252 fixture-comparison utility (per Murat M1 amendment — 7c.2 absorbs fixture-utility scope)
**When** the dev-agent lands the utility
**Then** it can compare a directive bytes fixture against expected UTF-8 bytes across Windows + Linux + macOS + assert byte-equivalence.

**Given** the U+202F NNBSP regression test
**When** the dev-agent lands a test that prints macOS-screenshot Unicode through the G0 print path
**Then** the test passes on Windows without `PYTHONIOENCODING=utf-8`.

**Given** Trial-2 finding #1 deferred-inventory closure precondition
**When** 7c.2 closes
**Then** anti-pattern A11 (Windows-portability) is augmented in `docs/dev-guide/specialist-anti-patterns.md` with a Slab 7c §02A worked example.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged; SG-3 Composition Spec invariants unaffected (cp1252 fix is below the spec layer).

**Story-scoped NFR predicates:** NFR-7c-X1 (Windows-portability UTF-8 lint); NFR-7c-X3 (path-portability `pathlib.Path.as_posix()`); TW-7c-2 detection ownership.

---

### Story 7c.3a: §02A LLM-Driven Directive Composer Body

As the operator,
I want the §02A directive composer to compose a directive YAML via LLM reasoning (replacing the corpus-scan fallback that produced byte-identical broken directives in Trial-2 across 5 successive runs),
So that Trial-3 G0 ratification surface displays a real LLM-driven directive that classifies primary `.docx` lesson content correctly, ignores `.gitkeep`, and does not assign `expected_min_words` to PNG/JPG/PPTX/PDF binaries.

**Story metadata:** Wave 1 (highest-priority story within Slab 7c — dual-nature feature + Trial-2 finding #2 retirement); **dual-gate**; **cross-agent code-review MANDATORY** (per Murat M6); K-target ~1.5×; ~4-5 pts; FR coverage = FR-7c-1 (composer body) + FR-7c-2 (Trial-2 forensic-fixture regression test) + FR-7c-5 (UTF-8 composer write) + FR-7c-53 C5 (composer boundary import-linter contract); owns TW-7c-2 firing.

**Acceptance Criteria:**

**Given** the composer module path = `app/composers/section_02a/composer.py`
**When** the dev-agent authors the composer body
**Then** `composer.compose(state, llm=...)` accepts injected LLM client for fixture-replay determinism + emits directive YAML conforming to the §02A directive Pydantic-v2 model with `validate_assignment=True` + closed-enum red-rejection on `role` ∈ {primary, supporting, ignored}.

**Given** the Trial-2 forensic fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` + `run.json`)
**When** the composer runs against the same corpus
**Then** primary `.docx` lesson content is classified `role: primary`; `.gitkeep` is excluded with `excluded_reason` populated; PNG/JPG/PPTX/PDF binaries have no `expected_min_words` field; the regression test asserts non-byte-identicality with the broken Trial-2 fixture.

**Given** FR-7c-53 C5 (composer boundary; **contract DEFINED at 7c.0a per W2; this story populates target list**)
**When** the dev-agent populates `pyproject.toml::[tool.importlinter]` C5 target list
**Then** C5 forbidden-imports list grows from empty to forbidding `app/composers/section_02a/*` from importing corpus-scan fallback paths (`app.composers._fallback`, `app.composers.legacy.*`); CI-fail mode at `lint-imports` was already active from 7c.0a forward.

**Given** NFR-7c-P1 + NFR-7c-P2 measurement requirements
**When** the dev-agent runs the §02A composer against the 20-file Tejal-APC-C1 corpus
**Then** wall-clock ≤60s p50 / ≤120s p99 over ≥20 fixture-replay runs at gpt-5.4 cache-cold + ≥90% cache-hit median[2:] + cache-key normalization rule `cache_key = SHA256(normalized_prompt)` with `operator_id` + timestamps + `run_id` stripped.

**Given** TW-7c-2 firing precondition
**When** the regression test against the Trial-2 fixture fails
**Then** TW-7c-2 fires (high severity); STOP; re-scope §02A; dual-nature claim invalidated.

**Standing-guardrail enforcement:** SG-1 unchanged (composer is orchestration, not specialist); SG-2 §02A row in mapping checklist preserved; SG-3 Composition Spec §3.1/§3.5/§3.6 honored on composer envelope contribution; SG-4 unchanged.

**Story-scoped NFR predicates:** NFR-7c-P1 (composer wall-clock + calibration band); NFR-7c-P2 (cache-hit-rate); NFR-7c-S1 (HIL tamper-evidence at writer boundary); NFR-7c-S6 (API key handling); TW-7c-2 detection ownership.

---

### Story 7c.3b: §02A G0 Poll-Surface Canonical HIL Pattern

As the operator,
I want the §02A G0 poll-surface to display the composed directive + accept {approve, edit, reject} verdicts via CLI + FastAPI + MCP-stdio with verdict-digest match enforced on resume + field-level edit + re-validation,
So that 7c.3b ships the **canonical HIL surface pattern** that 7c.6..7c.15 (10 stories) replicate.

**Story metadata:** Wave 1 (pattern-author, not pattern-consumer); **dual-gate**; K-target ~1.4×; ~2-3 pts; FR coverage = FR-7c-3 (3-transport verdicts with digest match) + FR-7c-4 (field-level edit + re-validation) + FR-7c-20 (parity-contract DSL declaration); registers per-surface OperatorVerdict schema-stability case (FR-7c-49).

**Acceptance Criteria:**

**Given** the composed directive emitted by 7c.3a at `state/config/runs/<run-id>/directive.yaml`
**When** the operator submits an `approve` verdict via CLI
**Then** the surface emits `OperatorVerdict<§02A>` with `decision_card_digest` matching emitted card; resume rejects via `GateError` on mismatch.

**Given** the §02A G0 poll surface
**When** the operator submits an `edit` verdict with a field-level edit (e.g., `expected_min_words` adjustment OR `role` reclassification)
**Then** the edited directive is re-validated against the §02A Pydantic-v2 model before submission + only validated edits resume the graph.

**Given** FR-7c-20 (DSL self-registration)
**When** the §02A surface module is imported
**Then** it self-registers into the parameterized parity-test harness via the 7c.0 + 7c.1 DSL primitives + declares mandatory transports = {CLI, HTTP, MCP-stdio} + opt-in transport = MCP-subprocess.

**Given** FR-7c-49 per-HIL-surface OperatorVerdict schema-stability test
**When** the dev-agent lands `tests/schemas/operator_verdict/test_section_02a_shape.py`
**Then** the discriminated-union variant asserts schema hash stable across CLI/HTTP/MCP-stdio for §02A.

**Standing-guardrail enforcement:** SG-1/2/3 unchanged; SG-3 Composition Spec §6 (HIL pattern) honored — establishes the canonical pattern for §04A..§15.

**Story-scoped NFR predicates:** NFR-7c-P4 (HIL poll latency); NFR-7c-S1 (writer-boundary tamper-evidence); NFR-7c-X2 (multi-transport byte-equivalence); FR-7c-49 schema-stability.

---

### Story 7c.4a: Gate Family Taxonomy Ratification (Decision-Only)

As the architect,
I want the gate-family taxonomy decision (8 net-new gate families + 6 alias gates per the PRD-locked alias map) ratified as a decision-only spec without implementation,
So that 7c.4b foundation + 7c.5.G0..G6 per-gate stories proceed against an unambiguous taxonomy with no relitigation at story-author time.

**Story metadata:** Wave 2; single-gate (decision artifact; no code); K-target ~1.0×; ~1 pt; FR coverage = none direct (decision artifact only; ratifies the taxonomy that FR-7c-6..9 + FR-7c-7 (4-file lockstep) + FR-7c-37 (14/14 co-commit) operate against).

**Acceptance Criteria:**

**Given** the PRD §Gate Taxonomy LOCK at PRD Step 11 per Amelia A3
**When** the dev-agent lands the decision artifact at `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md`
**Then** the artifact records (a) 8 net-new gate families: G0, G1, G2A, G2C, G3, G4, G5, G6; (b) 6 alias gates: G0A→G1, G0B→G1, G1A→G1, G2B→G2C, G2M→G2C, G2.5→G2C, G2F→G2C, G3B→G3, G4A→G4, G4B→G4 (alias-DSL clause inherits parent's lockstep); (c) FR-7c-37 14/14 four-file-lockstep co-commit checks satisfied via inheritance.

**Given** the alias-DSL clause defined in 7c.0
**When** an alias gate (e.g., G0A) is consumed
**Then** the alias inherits parent G1's four-file-lockstep contract via the clause; no separate per-gate four-file-lockstep stories needed for the 6 aliases.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged.

**Story-scoped NFR predicates:** None direct (decision artifact); enables NFR-7c-M1 + NFR-7c-R6 + NFR-7c-OD7 downstream.

---

### Story 7c.4b: Gate-Family Foundation Implementation

As the dev-agent,
I want the gate-family shared base classes + class-conformance validator extension + FR-7c-49 OperatorVerdict schema-stability harness + FR-7c-53 C6 HIL boundaries import-linter contract + TW-7c-3 lockstep checker registration,
So that 7c.5.G0..G6 (8 per-gate stories) have a shared substrate that enforces four-file-lockstep + class-conformance + per-surface OperatorVerdict schema-stability at slab-open.

**Story metadata:** Wave 2; **dual-gate**; **cross-agent code-review MANDATORY** (per John A5 + Murat M6); K-target ~1.4×; ~3-4 pts; FR coverage = FR-7c-8 (class-conformance recognizes new gates) + FR-7c-9 (manifest fold-flags + compiler) + FR-7c-49 (parametrized harness) + FR-7c-53 C6 (HIL boundaries); owns TW-7c-3 detection registration + class-conformance extension.

**Acceptance Criteria:**

**Given** the 7c.4a taxonomy ratification
**When** the dev-agent lands shared base classes per the taxonomy at `app/models/decision_cards/_base.py` (or analogous architecture path)
**Then** the base classes expose `cache_state` + `affected_nodes` + `override_trail` + `decision_card_digest` invariants that all 8 net-new gate families inherit.

**Given** FR-7c-49 parametrized harness
**When** the dev-agent lands `tests/schemas/operator_verdict/_harness.py` (parametrized by surface_id × transport)
**Then** the harness asserts schema hash stable across CLI/HTTP/MCP-stdio for any registered surface; per-surface cases (7c.6..7c.15) consume the parametrization.

**Given** FR-7c-53 C6 (HIL boundaries; **contract DEFINED at 7c.0a per W2; this story populates target list**)
**When** the dev-agent populates `pyproject.toml::[tool.importlinter]` C6 target list
**Then** C6 forbidden-imports list grows from empty to forbidding HIL-surface modules from importing each other across surfaces (e.g., `app.gates.section_05_5.*` cannot import `app.gates.section_07b.*`); shared helpers must live in `app.gates._shared.*`; CI-fail mode at `lint-imports` was already active from 7c.0a forward.

**Given** AMEND-7d-i (TW-7c-3 firing-spec single-source per Murat)
**When** the dev-agent lands the lockstep-checker registration in 7c.4b
**Then** the firing-spec block lives at `app/parity/contracts/tw_7c_3_firing.py` (or analogous architecture path) as the **single source of truth** for the four-file-lockstep firing condition; the seven gate stories (7c.5.G0..G6) cite by reference (`from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK`) rather than re-deriving the firing condition. One source; seven citations; prevents drift.

**Given** FR-7c-8 + Murat M1 TW-7c-3 detection ownership
**When** the dev-agent extends `scripts/utilities/validate_parity_test_class_conformance.py`
**Then** the validator recognizes every new gate ID + reports ≥11 conforming activation contracts post-Slab-7c (no regression); TW-7c-3 fires (critical) if a new gate is added without four-file-lockstep + class-conformance.

**Given** FR-7c-9 (manifest fold-flags + compiler honor new codes)
**When** the dev-agent extends `app/manifest/compiler.py` per FR-A8 (Slab 7a 7a.2 substrate)
**Then** the compiler honors every new gate code at runtime + orchestration_only_nodes lockstep tolerance covers any new orchestration-only nodes.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 PRODUCTION_GATE_IDS expansion row preserved; SG-3 Composition Spec §3.5 (gate-family invariants) honored on shared base; SG-4 unchanged.

**Story-scoped NFR predicates:** NFR-7c-M1 (four-file-lockstep precondition); NFR-7c-R5 (class-conformance ≥11); NFR-7c-OD2 + OD7 (tripwire-ledger + self-registration audit consumption); FR-7c-49 schema-stability harness primary enforcement here.

---

### Stories 7c.5.G0 .. 7c.5.G6 (8 stories): Per-Gate Four-File-Lockstep Authoring

For the 8 net-new gate families per the PRD-locked taxonomy (G0, G1, G2A, G2C, G3, G4, G5, G6), each gate gets one story authoring four-file lockstep co-commit: (i) `app/models/decision_cards/<gate>.py` Pydantic-v2 model; (ii) `app/models/decision_cards/schema/<gate>.v1.schema.json` JSON schema; (iii) `tests/parity/test_decision_card_<gate>_shape.py` shape-pin; (iv) `tests/fixtures/decision_cards/<gate>_golden.json` golden fixture.

Each story shares a common shape (template below; per-gate AC variations in `bmad-create-story` per-story spec):

**Story metadata (per gate; with two-flavor gate-mode per Winston W3):**
- **Fresh-author (G0/G5/G6):** Wave 2 (post-7c.4b); **single-gate**; K-target ~1.2×; ~1-2 pts; FR coverage = FR-7c-6 + FR-7c-7 + FR-7c-49; fires TW-7c-3.
- **Extend-and-audit (G1/G2A/G2C/G3/G4):** Wave 2 (post-7c.4b); **`dual-gate-cross-agent-CONTRACT-EVOLUTION`** (NEW gate-mode per Winston W3); K-target ~1.4× (heavier than fresh-author due to backward-consumer audit load); ~2-3 pts; FR coverage = FR-7c-6 + FR-7c-7 + FR-7c-49; fires TW-7c-3 per-gate; T1 readiness REQUIRES (a) diff-against-prior-contract artifact reviewed BEFORE T2 + (b) backward-consumer audit per call site + (c) AMELIA-P4 delta-AC verifying prior-gate body file frozen-at-ship hash before extension begins.

**Per-row delta fields (per John PM-1 + Amelia Q1; embedded in per-gate breakdown bullets below):** each gate carries gate-mode + K-target + pts envelope + AMEND-5 bucket + four-file paths + predecessor link.

**AMEND-5 disambiguation:** 7c.5.G0 + 7c.5.G5 + 7c.5.G6 are **fresh-author** (gates not previously shipped; standard single-gate); 7c.5.G1 + 7c.5.G2A + 7c.5.G2C + 7c.5.G3 + 7c.5.G4 are **extend-and-audit existing shipped gate to post-Slab-7c contract** (G1/G2C/G3/G4 already on disk per Slab 7a substrate; extend with FR-7c-51 schema_version + regenerate fixtures + AUDIT against post-7c contract; G2A is fresh-author per the alias map). Wait — correction: per Gate Taxonomy, G2A IS net-new (fresh-author). Five extend-and-audit gates: G1, G2C, G3, G4 (already shipped). Per ADR check, G2A is fresh-author. Re-tally: fresh-author = G0/G2A/G5/G6 (4 stories); extend-and-audit = G1/G2C/G3/G4 (4 stories).

**Acceptance Criteria (template, applied per-gate):**

**Given** the 7c.4a taxonomy decision + 7c.4b shared base classes + AMEND-7d-i firing-spec single-source citation
**When** the dev-agent authors the four files for `<gate>` (atomic co-commit) + cites `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK`
**Then** the Pydantic-v2 model has `validate_assignment=True` + closed-enum red-rejection + `DecisionCardMeta.cache_state ∈ {"healthy", "mixed", "cold"}` populated + the JSON schema regenerates from the model (bump-on-change per FR-7c-51) + the shape-pin asserts field-presence + closed-enum red-rejection + JSON-Schema emission + golden-fixture round-trip + the golden fixture is deterministic.

**Given** TW-7c-3 detection (lockstep-checker registered at 7c.4b; firing-spec single-sourced per AMEND-7d-i)
**When** any of the four files is missing or out-of-sync
**Then** TW-7c-3 fires (critical); STOP; lockstep gate-fill required.

**Given** Winston W3 + AMELIA-P4 (extend-and-audit gate-mode T1 readiness; applies ONLY to G1/G2C/G3/G4)
**When** the dev-agent opens an extend-and-audit story
**Then** T1 readiness produces (a) diff-against-prior-contract artifact (`_bmad-output/implementation-artifacts/migration-7c-5-G<gate>-contract-diff.md`) — what the prior gate guaranteed vs post-7c contract — reviewed by cross-agent reviewer BEFORE T2; (b) backward-consumer audit (grep/import-graph artifact) showing every call site of the prior gate contract + per-site verdict ("unchanged behavior" / "behavior changes — acceptable because X" / "behavior changes — requires consumer-side amendment in story 7c.Y"); (c) **AMELIA-P4 delta-AC: prior-gate body file SHA256 matches frozen-at-ship hash recorded in `app/models/decision_cards/_frozen_hashes.py` BEFORE extension begins** — protects against silent inheritance of stale body.

**Given** FR-7c-49 per-HIL-surface schema-stability case
**When** the gate is consumed by an HIL surface (e.g., G2B by §05.5)
**Then** the per-surface case at `tests/schemas/operator_verdict/test_<surface>_shape.py` asserts schema hash stable across CLI/HTTP/MCP-stdio for that surface.

**Given** FR-7c-37 14/14 four-file-lockstep co-commit AUDIT
**When** the AUDIT runs at 7c.20c
**Then** the gate's lockstep is verified for the gate itself + alias inheritance via the alias-DSL clause.

**Standing-guardrail enforcement (per-story):** SG-1/2/3/4 unchanged; SG-3 Composition Spec §3.5 (gate-family invariants) honored.

**Story-scoped NFR predicates (per-story):** NFR-7c-M1 (four-file-lockstep enforced); NFR-7c-R5 (class-conformance ≥11); NFR-7c-R6 (pipeline-manifest lockstep); FR-7c-49 schema-stability case.

**Per-gate breakdown (8 stories with explicit per-row delta fields per John PM-1):**

- **7c.5.G0** — **fresh-author**; gate-mode = single-gate; K ~1.2×; ~1-2 pts; G0 = trial-open / corpus-confirm gate. Files = `app/models/decision_cards/g0.py` + `schema/g0.v1.schema.json` + `tests/parity/test_decision_card_g0_shape.py` + `tests/fixtures/decision_cards/g0_golden.json`. Predecessor: 7c.4b.
- **7c.5.G1** — **extend-and-audit**; gate-mode = `dual-gate-cross-agent-CONTRACT-EVOLUTION`; K ~1.4×; ~2-3 pts; G1 = directive-ratification gate (already shipped at 7a substrate at `app/models/decision_cards/g1.py`); extends with FR-7c-51 schema_version + regenerated fixtures. T1 deliverables: contract-diff + backward-consumer audit + AMELIA-P4 frozen-hash delta-AC. Files = (existing) g1.py + (existing) schema/g1.v1.schema.json + (existing) test_decision_card_g1_shape.py + (existing) g1_golden.json. Predecessor: 7c.4b.
- **7c.5.G2A** — **fresh-author**; gate-mode = single-gate; K ~1.2×; ~1-2 pts; G2A = plan-unit-ratification gate per the taxonomy alias map. Files = `g2a.py` + `schema/g2a.v1.schema.json` + `test_decision_card_g2a_shape.py` + `g2a_golden.json`. Predecessor: 7c.4b.
- **7c.5.G2C** — **extend-and-audit**; gate-mode = `dual-gate-cross-agent-CONTRACT-EVOLUTION`; K ~1.4×; ~2-3 pts; G2C = pre-composition QA gate (already shipped). T1 deliverables per W3. Files = (existing) g2c.py et al. Predecessor: 7c.4b.
- **7c.5.G3** — **extend-and-audit**; gate-mode = `dual-gate-cross-agent-CONTRACT-EVOLUTION`; K ~1.4×; ~2-3 pts; G3 = motion-clip approval gate (already shipped). T1 deliverables per W3. Files = (existing) g3.py et al. Predecessor: 7c.4b.
- **7c.5.G4** — **extend-and-audit**; gate-mode = `dual-gate-cross-agent-CONTRACT-EVOLUTION`; K ~1.4×; ~2-3 pts; G4 = fidelity gate (already shipped). T1 deliverables per W3. Files = (existing) g4.py et al. Predecessor: 7c.4b.
- **7c.5.G5** — **fresh-author**; gate-mode = single-gate; K ~1.2×; ~1-2 pts; G5 = final operator handoff gate. Files = `g5.py` + `schema/g5.v1.schema.json` + `test_decision_card_g5_shape.py` + `g5_golden.json`. Predecessor: 7c.4b.
- **7c.5.G6** — **fresh-author**; gate-mode = single-gate; K ~1.2×; ~1-2 pts; G6 = slab-close ceremony gate. Files = `g6.py` + `schema/g6.v1.schema.json` + `test_decision_card_g6_shape.py` + `g6_golden.json`. Predecessor: 7c.4b.

**Wave-2 effective gate-mode count:** 4 fresh-author single-gate (G0/G2A/G5/G6) + 4 extend-and-audit dual-gate-cross-agent-CONTRACT-EVOLUTION (G1/G2C/G3/G4).

---

### Stories 7c.6 .. 7c.15 (10 stories): HIL Conversational Surfaces (Follower Pattern)

Each HIL surface story opens **as soon as its specific 7c.5.G<gate> predecessor lands**, not after all 7c.5.* close (per John A1 wave-overlap). §02A is NOT in Wave 3 (lives in 7c.3b per Winston A4 + Amelia A2). Each surface authors module + parity-contract declaration + transport handlers + per-surface OperatorVerdict schema-stability case (FR-7c-49 parametrized).

**AMELIA-P3 G2C-fanout staggering protocol:** When 7c.5.G2C lands, four HIL stories alias to G2C (7c.9 §05.5 + 7c.10 §07B + 7c.11 §07D + 7c.12 §07F). Codex dispatches MUST stagger ~30 minutes apart to prevent T11 `bmad-code-review` queue collision (Claude reviews serially; concurrent `.ready-for-review.md` notice drops would queue 4× T11 latency). Operator dispatch protocol: pick one G2C-aliased story per 30-min window; document Wave-3 dispatch protocol explicitly in `next-session-start-here.md` at session-start once 7c.5.G2C close approaches.

**Story metadata (per HIL surface):** Wave 3; single-gate; K-target ~1.3×; ~2-3 pts each; FR coverage = one of FR-7c-10..19; uses 7c.3b canonical pattern.

**Acceptance Criteria (template, applied per-surface):**

**Given** the 7c.3b §02A canonical HIL pattern + the surface's predecessor 7c.5.G<gate> landing
**When** the dev-agent authors the surface module + transport handlers
**Then** the surface emits `OperatorVerdict<surface>` per FR-7c-49 + self-registers into the parameterized parity-test harness via the 7c.0 + 7c.1 DSL primitives + declares mandatory transports per the PRD §HIL Surface Specification table.

**Given** FR-7c-49 per-HIL-surface OperatorVerdict schema-stability case
**When** the dev-agent lands `tests/schemas/operator_verdict/test_<surface_id>_shape.py`
**Then** the discriminated-union variant asserts schema hash stable across CLI/HTTP/MCP-stdio for that surface.

**Given** the writer-boundary D3 invariant
**When** the operator submits a verdict via any transport
**Then** verdict-digest match is enforced on resume; mismatch raises `GateError`.

**Standing-guardrail enforcement (per-story):** SG-1 unchanged; SG-2 surface row in mapping checklist preserved + status improved (one of ~17-22 row improvements at retrospective); SG-3 Composition Spec §6 (HIL pattern) honored; SG-4 unchanged.

**Story-scoped NFR predicates (per-story):** NFR-7c-P4 (HIL poll latency); NFR-7c-S1 (writer-boundary tamper-evidence); NFR-7c-X2 (multi-transport byte-equivalence); FR-7c-49 schema-stability case.

**Per-surface breakdown (10 stories with per-row delta fields per John PM-1):**

- **7c.6** — §04A G1A per-plan-unit ratification (FR-7c-10). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory transports: CLI. Optional: HTTP, MCP-stdio. Predecessor: 7c.5.G1.
- **7c.7** — §04.5 G1.5 estimator (FR-7c-11). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI + HTTP. Optional: MCP-stdio. Predecessor: 7c.5.G1.
- **7c.8** — §04.55 G1.5 run-constants lock (FR-7c-12). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI + HTTP. Optional: MCP-stdio. Predecessor: 7c.5.G1.
- **7c.9** — §05.5 G2B per-slide mode (FR-7c-13). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI. Optional: HTTP, MCP-stdio. Predecessor: 7c.5.G2C (G2B aliases to G2C). **AMELIA-P3 staggering applies (G2C-aliased; ≥30 min from siblings).**
- **7c.10** — §07B G2M per-slide A/B variant (FR-7c-14). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI. Optional: HTTP, MCP-stdio. Predecessor: 7c.5.G2C. **AMELIA-P3 staggering applies.**
- **7c.11** — §07D G2.5 motion-plan polling (FR-7c-15). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI. Optional: HTTP, MCP-stdio. Predecessor: 7c.5.G2C. **AMELIA-P3 staggering applies.**
- **7c.12** — §07F G2F motion gate (FR-7c-16). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI + HTTP. Optional: MCP-stdio. Predecessor: 7c.5.G2C. **AMELIA-P3 staggering applies.**
- **7c.13** — §08B G3B Storyboard B + live-URL (FR-7c-17). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI + HTTP. Optional: MCP-stdio. Predecessor: 7c.5.G3 (G3B aliases to G3).
- **7c.14** — §11 G4A voice-selection (FR-7c-18). Gate-mode: single-gate. K ~1.3×. ~2-3 pts. Mandatory: CLI. Optional: HTTP, MCP-stdio. Predecessor: 7c.5.G4 (G4A aliases to G4).
- **7c.15** — §11B G4B input-package + §15 G5 final operator handoff (FR-7c-19 + **FR-7c-29 Marcus-side §15 bundle emission per AMEND-4**). Gate-mode: single-gate (per John PM Round-2: dual-FR co-dependent — JTBD round-trip; do not split). K-target sized for both FRs ~1.5–1.8× a single-FR sibling story. ~3-4 pts (heavier than other Wave-3 stories due to dual-FR + §15 bundle aggregation). Mandatory transports: CLI + HTTP + MCP-stdio (§15 final handoff). Predecessors: 7c.5.G4 (G4B aliases) + 7c.5.G5.

> **AMEND-4 fold:** 7c.15 implements both the operator-side review (FR-7c-19) AND the Marcus-side bundle emission at §15 (FR-7c-29 — `assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial-3 transcript anchor + slab-close evidence pointer`).

---

### Story 7c.17a: 3 Marcus-Bound Writers (Slide-Content + Fidelity-Slides + Diagram-Cards) — Shared-Sanctum Partition

As Marcus,
I want to emit `gary-slide-content.json` + `gary-fidelity-slides.json` + `gary-diagram-cards.json` per plan unit prior to Gary dispatch,
So that Gary receives the text+payload-shape pre-dispatch package with Vera-fidelity-criteria-prepopulated payload + literal-visual diagram requirements.

**Story metadata:** Wave 4; single-gate; K-target ~1.3×; ~2 pts; FR coverage = FR-7c-21 + FR-7c-22 + FR-7c-23 + FR-7c-54 sanctum-alignment consumption per writer (3 writers); per AMEND-3 specific writer-to-story assignment.

**Partition principle (Winston W5):** **architectural partition** = 3 writers sharing a *transport boundary* (text+payload-shape pre-dispatch with Vera-fidelity criteria as the unifying contract). NOT a process partition. The 7c.17a/17b seam runs between "writers that share Vera-criteria-prepopulated payload shape" (7c.17a) and "writers that aggregate into the outbound envelope + theme-resolution layer" (7c.17b). Future maintenance of these 5 writers inherits this partition logic; cross-story refactors will respect it.

**Acceptance Criteria:**

**Given** the 5 Marcus-bound writers + 7c.0 sanctum-alignment DSL feature
**When** the dev-agent authors `app/marcus/orchestrator/writers/{slide_content,fidelity_slides,diagram_cards}.py`
**Then** each writer emits the corresponding JSON file conforming to a Pydantic-v2 schema with `validate_assignment=True` + each writer module declares its sanctum-alignment row in the Marcus activation block per Slab 7b precedent (memory entry `project_slab_7b_skill_md_sanctum_alignment.md`) OR documents an explicit Cora-sidecar-style exception.

**Given** the Vera-fidelity-criteria-prepopulated payload (FR-7c-22)
**When** `gary-fidelity-slides.json` is emitted
**Then** the payload includes Vera's pre-resolved fidelity criteria for the plan unit + cross-references the §06 Vera contract.

**Given** the literal-visual diagram requirements (FR-7c-23)
**When** `gary-diagram-cards.json` is emitted
**Then** the payload includes per-slide visual specifications consumable by §07 Gary dispatch.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 §06 row preserved + status improved at retrospective; SG-3 unchanged; **SG-4 primary enforcement here** (FR-7c-54 sanctum-alignment for 3 writers).

**Story-scoped NFR predicates:** NFR-7c-S1 (writer-boundary HIL tamper-evidence); NFR-7c-S4 (single-writer authority via M1); FR-7c-54 sanctum-alignment consumption.

---

### Story 7c.17b: 2 Marcus-Bound Writers (Theme-Resolution + Outbound-Envelope) + pre-dispatch-package-gary.md Aggregation

As Marcus,
I want to emit `gary-theme-resolution.json` + `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md` aggregating all five per-plan-unit packages into a single bundle for Gary dispatch,
So that Gary receives the experience-profile + creative-directive theme inputs in resolved form + a single envelope handoff replaces the 5-file scattered shape.

**Story metadata:** Wave 4; single-gate; K-target ~1.3×; ~2 pts; FR coverage = FR-7c-24 + FR-7c-25 + FR-7c-54 sanctum-alignment consumption per writer (2 writers + envelope); per AMEND-3 specific writer-to-story assignment (larger surface area; divergent sanctum + envelope aggregation).

**Acceptance Criteria:**

**Given** the experience-profile + creative-directive theme inputs (FR-7c-24)
**When** the dev-agent authors `app/marcus/orchestrator/writers/theme_resolution.py`
**Then** `gary-theme-resolution.json` resolves theme inputs to Gary's expected payload shape per the Pydantic-v2 schema.

**Given** the FR-7c-25 envelope schema at `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`
**When** the dev-agent authors `gary-outbound-envelope.yaml` writer + `pre-dispatch-package-gary.md` aggregation
**Then** the envelope conforms to the Pydantic-v2 schema with fields `{writer_id, target_section, payload_ref, dispatched_at, operator_id}` + the markdown aggregates the 5 per-plan-unit packages into a single bundle.

**Given** SG-4 sanctum-alignment for the 2 divergent-sanctum writers
**When** the dev-agent declares each writer's sanctum-alignment row in the Marcus activation block
**Then** FR-7c-54 sanctum-alignment is verified for theme-resolution + outbound-envelope.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 §06 envelope-aggregation row preserved + status improved; SG-3 Composition Spec §3.1 SHA256+append-only honored on envelope; SG-4 sanctum-alignment for 2 writers + envelope.

**Story-scoped NFR predicates:** NFR-7c-S1 (writer-boundary tamper-evidence); NFR-7c-S4 (single-writer authority); FR-7c-54 sanctum-alignment consumption.

---

### Story 7c.18a: §06B Literal-Visual Operator Build

As the operator,
I want to build literal-visual operator content at the §06B surface, emitting per-slide visual specifications consumed by §07 Gary dispatch,
So that diagram-bearing slides have explicit operator-authored visual specifications (not auto-generated guesses).

**Story metadata:** Wave 5; single-gate; K-target ~1.3×; ~1-2 pts; FR coverage = FR-7c-26.

**Acceptance Criteria:**

**Given** the 7c.17a + 7c.17b pre-dispatch-package-gary substrate
**When** the operator builds literal-visual content at §06B
**Then** the surface emits per-slide visual specifications + the specifications are consumed by §07 Gary dispatch.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged; SG-2 §06B row preserved + status improved.

**Story-scoped NFR predicates:** NFR-7c-P4 (HIL poll latency); FR-7c-49 schema-stability case.

---

### Story 7c.18b: §07C Storyboard Build + HTML Reviewer Surface

As the operator,
I want to build a storyboard with HTML reviewer surface at §07C, with reviewer artifact rendered for §08B Storyboard B + live-URL HIL consumption,
So that storyboard review has a structured HTML surface (not a flat text dump).

**Story metadata:** Wave 5; single-gate; K-target ~1.3×; ~2 pts; FR coverage = FR-7c-27.

**Acceptance Criteria:**

**Given** the §07 Gary dispatch outputs
**When** the operator builds the storyboard at §07C
**Then** the storyboard emits an HTML reviewer artifact + the artifact is consumable by §08B Storyboard B + live-URL HIL.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged; SG-2 §07C row preserved + status improved.

**Story-scoped NFR predicates:** NFR-7c-P4 (HIL poll latency); FR-7c-49 schema-stability case.

---

### Story 7c.19: §09 Four-Artifact Lock Semantics

As Marcus,
I want to enforce four-artifact lock semantics at §09 (post-Gary + post-Kira + post-Vera + post-Quinn-R), preventing downstream advancement until all four artifacts are present + consistent,
So that §11 voice-selection and downstream surfaces cannot fire prematurely against incomplete artifact sets.

**Story metadata:** Wave 5; single-gate; K-target ~1.2×; ~1-2 pts; FR coverage = FR-7c-28.

**Acceptance Criteria:**

**Given** the four upstream artifacts (Gary slide-content + Kira motion-plan + Vera fidelity-verdict + Quinn-R QA-verdict)
**When** Marcus checks §09 lock
**Then** the lock raises `GateError` if any of the four is absent or inconsistent + downstream advancement is blocked.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged; SG-2 §09 row preserved + status improved.

**Story-scoped NFR predicates:** NFR-7c-S1 (writer-boundary tamper-evidence); NFR-7c-R3 (tripwire-ledger completeness on lock failures).

---

### Story 7c.20a: AUDIT-AC ≥20 Shape-Pins + ≥11 Class-Conformance

As the test-architect,
I want to verify that ≥20 shape-pin tests on parity-DSL surfaces + ≥11 class-conformance assertions are green at slab-close (verifying original Epic 3 stories 3.2 + 3.4 against shipped substrate),
So that AUDIT-AC compresses Slab 7c's net-new build to coverage-only audit per the AUDIT-not-BUILD framing.

**Story metadata:** Wave 5; single-gate; K-target ~1.2×; ~2 pts; FR coverage = FR-7c-34 (≥20 shape-pins) + FR-7c-36 (≥11 class-conformance); fires TW-7c-1 per **AMEND-7c percentage threshold** (combined floor 31; trips at ≥4 gaps = 10% gap-rate).

**Acceptance Criteria:**

**Given** the shipped substrate (7 DecisionCard modules + 5 schemas + class-conformance validator)
**When** the dev-agent runs the AUDIT
**Then** ≥20 shape-pin tests on parity-DSL surfaces (G1/G2C/G3/G4/Override × {field-presence, closed-enum red-reject, JSON-Schema emission, golden-fixture round-trip}) are green + ≥11 class-conformance assertions match current activation-contract validator floor.

**Given** TW-7c-1 firing precondition (per AMEND-7c percentage threshold)
**When** ≥4 gaps are discovered (10% gap-rate against combined floor of 31)
**Then** TW-7c-1 fires (high severity); STOP; party-mode-consensus on absorb-vs-defer per gap; gap-fill stories file as `7c.X.<descriptor>` follow-ons (cap 5 per AUDIT-AC; >5 escalates to party-mode impasse).

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged.

**Story-scoped NFR predicates:** NFR-7c-M2 (AUDIT-AC discipline); NFR-7c-R5 (class-conformance floor); TW-7c-1 detection ownership.

---

### Story 7c.20b: AUDIT-AC ≥15 Cells in 5-Family × 3-Transport Matrix

As the test-architect,
I want to verify that ≥15 cells in the 5-family × 3-transport matrix are populated and green at slab-close (verifying original Epic 3 story 3.3 verdict-authority enforcement against shipped substrate),
So that AUDIT-AC verifies 8 named gate tests green: `test_no_scheduler_import.py`, `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`, `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`, `test_consolidated_decision_card_carries_contributions.py`, `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`.

**Story metadata:** Wave 5; single-gate; K-target ~1.2×; ~2 pts; FR coverage = FR-7c-35; fires TW-7c-1 per **AMEND-7c percentage threshold** (combined floor 23; trips at ≥3 gaps = 13% gap-rate; closest to 10% boundary at this story size).

**Acceptance Criteria:**

**Given** the shipped substrate (8 transport-parity tests under `tests/integration/transport_parity/` + `tests/integration/transports/`)
**When** the dev-agent runs the AUDIT
**Then** ≥15 cells in 5-family × 3-transport matrix populated and green + 8 named gate tests pass.

**Given** TW-7c-1 firing precondition (per AMEND-7c percentage threshold)
**When** ≥3 gaps are discovered (10% gap-rate against combined floor of 23)
**Then** TW-7c-1 fires; gap-fill follow-ons file as `7c.X.gate-invariant-coverage-gap`.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged.

**Story-scoped NFR predicates:** NFR-7c-M2 (AUDIT-AC discipline); NFR-7c-S2 (bypass-attempt rejection verified); NFR-7c-S5 (operator-id provenance verified).

---

### Story 7c.20c: AUDIT-AC 14/14 Four-File-Lockstep + 6/6 Tripwire Ledger Probes

As the test-architect,
I want to verify 14/14 four-file-lockstep co-commit checks + 6/6 tripwire ledger probes at slab-close (verifying original Epic 3 stories 3.5 + 3.6 against shipped substrate),
So that AUDIT-AC verifies cache-impact + operator-id override flow + override_event audit chain shape + every TW-7c-1..6 entry passes audit-chain validator on emit.

**Story metadata:** Wave 5; single-gate; K-target ~1.2×; ~1-2 pts; FR coverage = FR-7c-37 (14/14 lockstep) + FR-7c-38 (6/6 tripwire probes); fires TW-7c-1 per **AMEND-7c percentage threshold** (combined floor 20; trips at ≥2 gaps = 10% gap-rate).

**Acceptance Criteria:**

**Given** the 14-gate post-Slab-7c expansion (8 net-new + 6 alias inheriting via alias-DSL clause)
**When** the dev-agent runs the AUDIT
**Then** all 14 gates have four-file-lockstep co-commit verified (8 net-new directly + 6 aliases via alias-DSL inheritance).

**Given** the 6 TW-7c-1..6 ledger entries
**When** the dev-agent runs FR-7c-50 audit-chain integrity test
**Then** every TW-7c-1..6 entry passes audit-chain validator on emit (NFR-7c-OD2 schema enforcement + append-only invariant + monotonic timestamp + parent-trace linkage).

**Given** TW-7c-1 firing precondition (per AMEND-7c percentage threshold)
**When** ≥2 gaps are discovered (10% gap-rate against combined floor of 20)
**Then** TW-7c-1 fires; gap-fill follow-ons file as `7c.X.override-event-coverage-gap`.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged.

**Story-scoped NFR predicates:** NFR-7c-M2 (AUDIT-AC discipline); NFR-7c-OD2 (TripwireLedgerEntry schema); FR-7c-50 audit-chain integrity.

---

### Story 7c.21: Slab 7c Integration Parity Suite + Closeout Ceremony

As the operator,
I want one slab-closing ceremony story that aggregates SG-1+SG-2+SG-3+SG-4 enforcement + fires TW-7c-6 50-run zero-flake parity baseline + lands FR-7c-51 schema_version + Trial3Transcript schema + records Trial-3 readiness AC + triggers Slab 7c retrospective + closes deferred-inventory entries,
So that Slab 7c reaches done with full structural enforcement + Trial-3 unblocked.

**Story metadata:** Wave 6; **dual-gate**; **cross-agent code-review MANDATORY** (per John A5 + Murat M6 + 7b.12 precedent); K-target ~1.4×; ~4 pts; FR coverage = FR-7c-39..43 (tripwire ledger + retrospective + mapping-checklist row flips + deferred-inventory closure) + FR-7c-47 (50-run zero-flake) + FR-7c-51 (schema_version + Trial3Transcript).

**Acceptance Criteria:**

**Given** the 7c.0b 50-run harness scaffold + per-cell flake-rate calculator (with AMEND-7a tightened budget)
**When** the dev-agent fires the 50-run zero-flake parity baseline at slab-close
**Then** the parity suite runs 50 consecutive times in CI with zero flakes against the full ~68-cell post-Slab-7c matrix; per-cell flake budget <0.05% for 7c-added cells (per AMEND-7a) + <0.1% grandfathered for pre-7c cells; TW-7c-6 (high severity) fires on per-class budget breach.

**Given** AMEND-7d-iii (Murat STOP-on-TW-7c-6-fire branch)
**When** TW-7c-6 fires during 7c.21 ceremony
**Then** STOP; do NOT proceed to retrospective; escalate to party-mode for parity-budget mitigation per option-c parity-contract DSL; per-surface transport declaration enforcement reviewed; ceremony resumes only after fix lands. The slab-close ceremony itself is in the failure-loop ONLY if explicit STOP-branch is honored.

**Given** Winston W6 D7 transport-DSL-completeness policy (codified in 7c.0a ADR)
**When** the dev-agent runs slab-close audit
**Then** the audit verifies the ADR's escape-hatch policy was honored across all transports; any per-transport addendum is documented inline at the surface module per ADR; no implicit DSL escape hatches exist.

**Given** FR-7c-51 schema_version + Trial3Transcript schema
**When** the dev-agent lands `Trial3Transcript` Pydantic-v2 model + `tests/trial/test_trial3_transcript_shape.py`
**Then** the model has closed-enum on gate-ids and edit/approve event types + the shape-pin asserts schema hash stable + `schema_version: int` field on every new schema-shape file in Slab 7c (DecisionCards, OperatorVerdict variants, gary-* writers, Trial-3 transcript) bumps when schema hash changes.

**Given** NFR-7c-R7a + R7b Trial-3 readiness AC (Murat M4)
**When** the dev-agent verifies Trial-3 readiness preconditions
**Then** (a) all 6 tripwire ledger entries are queryable; (b) R7a precondition fixtures present; (c) R7b 120/180-min forensic-evidence harness operational; (d) all 11 HIL surfaces emit class-conformance markers.

**Given** FR-7c-41..43 retrospective deliverables
**When** the dev-agent triggers `bmad-retrospective`
**Then** the retrospective reviews per-tripwire firing rate + effectiveness (FR-7c-41) + ratifies mapping-checklist row flips per R15 (FR-7c-42; ~17-22 row-flip evidence) + consults `deferred-inventory.md` and closes `slab-7c-live-harness-evidence` + Trial-2 finding #1 + #2 (FR-7c-43).

**Given** D12 cross-slab governance protocol
**When** the dev-agent closes Slab 7c
**Then** the close protocol AC preserves invariants + captures anti-pattern entries + deepens the migration guide.

**Standing-guardrail enforcement:** SG-1+SG-2+SG-3+SG-4 **aggregated structural enforcement here** (precedent: 7a.8 + 7b.12); SG-1 11-roster floor preserved (no specialist roster change); SG-2 mapping-checklist row-flip evidence aggregated; SG-3 Composition Spec invariants verified; SG-4 BMB sanctum alignment per writer verified.

**Story-scoped NFR predicates:** NFR-7c-R1 (zero-flake parity 50× firing); NFR-7c-R7a + R7b (Trial-3 readiness); NFR-7c-OD3 (decision-record linkage); NFR-7c-OD4 (Trial-3 evidence accrual + Trial3Transcript); NFR-7c-OD5 (mapping-checklist row-flip evidence aggregation); NFR-7c-OD6 (forensic-evidence preservation); NFR-7c-OD7 (parity-DSL self-registration audit firing).

---

### Story 7c.21a: Epic 3 Retirement + Live-Dispatch Wiring

As the dev-agent,
I want to author live-dispatch in `run_cache_hit_harness.py` + `run_5_api_smoke.py` + update `epics-langchain-langgraph-migration.md` §Epic 3 in-place to record the 7a+7b+7c replacement,
So that the `slab-7c-live-harness-evidence` deferred-inventory entry closes + original Epic 3 retirement is documented in the parent migration epics file with cross-references to closure artifacts.

**Story metadata:** Wave 6 (peeled per John A6 — substrate-touching change distinct from slab-close ceremony); single-gate; K-target ~1.3×; ~1-2 pts; FR coverage = FR-7c-48 (live-dispatch authoring); closes deferred-inventory entry `slab-7c-live-harness-evidence`.

**Acceptance Criteria:**

**Given** the `slab-7c-live-harness-evidence` deferred-inventory entry
**When** the dev-agent authors live-dispatch in `run_cache_hit_harness.py` + `run_5_api_smoke.py`
**Then** live-dispatch authoring is concentrated in the named harness; TW-7c-4 (live-dispatch scope-creep) is not tripped.

**Given** the parent migration epics file `epics-langchain-langgraph-migration.md` §Epic 3
**When** the dev-agent updates the §Epic 3 section in-place
**Then** the section records the 7a+7b+7c replacement with cross-references to the three closure artifacts (`epics-slab-7a-inter-gate-orchestration.md` + `epics-slab-7b-specialist-activation-eleven.md` + `epics-slab-7c-orchestrational-tail.md`) per FR-7c-43.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged; SG-2 Epic 3 row in mapping checklist preserved + status flipped to "retired-via-7a+7b+7c".

**Story-scoped NFR predicates:** TW-7c-4 detection (no scope creep); NFR-7c-OD3 (decision-record linkage to Slab 4 governance JSON entry).



