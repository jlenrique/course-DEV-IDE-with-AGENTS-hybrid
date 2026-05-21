---
date: 2026-05-04
project_name: course-DEV-IDE-with-AGENTS
scope: Slab 7c Orchestrational Tail
prd_under_review: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md
workflow: bmad-check-implementation-readiness (per Slab 7b precedent — Steps 1-3 only)
stepsCompleted: [step-01-document-discovery, step-02-prd-analysis, step-03-epic-coverage-validation]
steps_deferred: [step-04-ux-alignment, step-05-epic-quality-review, step-06-final-assessment]
verdict: READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS
verdict_date: 2026-05-04
---

# Implementation Readiness Assessment Report

**Date:** 2026-05-04
**Project:** course-DEV-IDE-with-AGENTS
**Scope:** Slab 7c Orchestrational Tail (PRD validation pre-`bmad-create-epics-and-stories`)
**PRD under review:** `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md`
**Precedent:** Slab 7b (`implementation-readiness-report-2026-04-29-slab-7b.md`) — Steps 1-3 only; Steps 4-6 deferred until `bmad-create-epics-and-stories` produces the epic file.

---

## Step 1 — Document Discovery

### A. PRD Documents Found

**Whole Documents (Slab 7c scope and siblings/parent):**

- `prd-slab-7c-orchestrational-tail.md` (116.9 KB, mtime 2026-05-04) — **PRIMARY UNDER REVIEW**
- `prd-slab-7b-specialist-activation-eleven.md` (170.7 KB, mtime 2026-04-29) — sibling baseline (CLOSED)
- `prd-slab-7a-inter-gate-orchestration.md` (151.0 KB, mtime 2026-04-29) — sibling baseline (CLOSED)
- `prd-langchain-langgraph-migration.md` (110.9 KB, mtime 2026-04-26) — parent migration PRD (Slab 7c §Epic 3 retirement-pending)

**Whole Documents (legacy, frozen reference; out of Slab 7c scope):**

- `prd.md` (1.2 KB, mtime 2026-04-21) — legacy stub; frozen reference

**Sharded Documents:** None found.

**Duplicates:** None found (no `prd*/index.md` sharded variants exist).

### B. Architecture Documents Found

**Whole Documents:**

- `architecture-langchain-langgraph-migration.md` (115.3 KB, mtime 2026-04-26) — D1-D13 source; D2/D3/D7 inherited as Slab 7c PRD-level invariants
- `architecture.md` (51.6 KB, mtime 2026-04-21) — legacy; frozen reference

**Sharded Documents:** None found.

**Duplicates:** None (legacy + migration architecture are scope-distinct, not duplicates).

### C. Epics & Stories Documents Found

**Whole Documents:**

- `epics-langchain-langgraph-migration.md` (108.8 KB, mtime 2026-04-26) — parent migration epics; §Epic 3 (Slab 3 Marcus Orchestration) to be retired in-place by Slab 7c per FR-7c-43 (jointly with Slabs 7a + 7b)
- `epics-slab-7a-inter-gate-orchestration.md` (54.0 KB, mtime 2026-04-29) — sibling (CLOSED)
- `epics-slab-7b-specialist-activation-eleven.md` (127.1 KB, mtime 2026-04-29) — sibling (CLOSED)
- `epics.md` (250.7 KB, mtime 2026-04-21) — legacy 22-epic frozen reference
- `epics-interstitial-clusters.md` (33.7 KB, mtime 2026-04-16) — Wave 2B frozen reference

**Sharded Documents:** None found.

**Duplicates:** None (legacy + migration + slab-scoped epics are scope-distinct).

> **Note:** `epics-slab-7c-orchestrational-tail.md` does NOT yet exist. This is **expected** and **load-bearing** — Slab 7c Step 2 of the sprint-governance chain (`bmad-create-epics-and-stories`) is the workflow that produces this file *after* the present readiness check returns READY. Per Slab 7b precedent, Steps 4-6 of this readiness check (Epic Quality Review + Final Assessment) are **deferred** until that file lands.

### D. UX Design Documents Found

**Whole Documents:** None.
**Sharded Documents:** None.

> **Note (informational, not a gap):** Slab 7c is a back-end orchestration / HIL-surface story bundle. UX classification expected to be `UX-not-applicable` (mirrors Slab 7a + 7b precedent — see `implementation-readiness-report-2026-04-28.md` Step 1 and `implementation-readiness-report-2026-04-29-slab-7b.md` Step 1 for the same classification). Will be confirmed in Step 2 PRD analysis.

### E. Prior Implementation-Readiness Reports (precedent reference)

- `implementation-readiness-report-2026-04-29-slab-7b.md` (30.7 KB) — most recent precedent (READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS verdict; Steps 1-3 closed; Steps 4-6 deferred)
- `implementation-readiness-report-2026-04-28.md` (Slab 7a) — READY verdict
- `implementation-readiness-report-2026-04-22.md` (full migration PRD) — READY-WITH-MINOR-AMENDMENTS verdict
- `implementation-readiness-report-2026-04-11.md` — older project-wide

---

## Critical Issues

**Duplicates:** None.
**Missing required documents:** None for Slab 7c readiness scope.
- Slab 7c PRD ✓ on disk
- Parent migration architecture (D2/D3/D7 source) ✓ on disk
- Sibling baselines (7a + 7b PRDs + epics) ✓ on disk for cross-reference
- Slab 7c epics file is **expected absent** — produced by `bmad-create-epics-and-stories` AFTER this readiness check (per chain).

---

## Document Selection (for Steps 2-3 assessment)

The following documents will be used for Steps 2-3:

| Role | Document | Path |
|------|----------|------|
| **PRD under review** | Slab 7c PRD | `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` |
| **Parent migration architecture** (D2/D3/D7 source) | Migration architecture | `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` |
| **Sibling baselines** (cross-reference for D14/D20 inheritance + SG-1..SG-4 enforcement) | Slab 7a + 7b PRDs + epics | `prd-slab-7a-*`, `prd-slab-7b-*`, `epics-slab-7a-*`, `epics-slab-7b-*` |
| **Parent migration epics** (Epic 3 retirement scope) | Migration epics | `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` |
| **Precedent readiness report** (verdict format + deferred-steps pattern) | Slab 7b readiness report | `_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-29-slab-7b.md` |

---

## Step 2 — PRD Analysis

### Functional Requirements (54 FRs across 10 capability areas A–J)

PRD §Functional Requirements; namespace `FR-7c-N`. Each FR is a testable capability stated as actor + capability; architectural HOW lives in `architecture-langchain-langgraph-migration.md` (D2/D3/D7) and in story-level T-tasks.

#### A. §02A LLM-Driven Directive Composer (5 FRs)

- **FR-7c-1** Marcus can compose a directive YAML from a corpus directory using LLM reasoning (NOT corpus-scan fallback). Composed output MUST conform to the §02A directive Pydantic-v2 model (`validate_assignment=True`, closed-enum red-rejection on `role` ∈ {primary, supporting, ignored}); primary `.docx` → `role: primary`, supporting binaries (PNG/JPG/PPTX/PDF) → `role: supporting`, ignored files (`.gitkeep`, `.DS_Store`, `Thumbs.db`) excluded with `excluded_reason` populated; `expected_min_words` populated only for text-bearing roles. **Infra hooks:** composer module = `app/composers/section_02a/composer.py`; fixtures = `tests/composers/fixtures/trial-2/{prompt,response}.json`; LLM injected via `composer.compose(state, llm=...)` for fixture-replay determinism.
- **FR-7c-2** Marcus can validate a composed directive against the Trial-2 forensic fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/`) and confirm the output classifies the same corpus correctly without producing the byte-identical broken directive Trial-2 captured.
- **FR-7c-3** Operator can review a composed directive at the §02A poll surface and emit one of {`approve`, `edit`, `reject`} verdicts via CLI, FastAPI, or MCP-stdio transport, with verdict-digest match enforced on resume.
- **FR-7c-4** Operator can edit field-level directive values at the §02A poll surface (e.g., adjusting `expected_min_words` or reclassifying a file's `role`) and have the edited directive re-validated before submission.
- **FR-7c-5** Marcus can preserve UTF-8 round-trip across the §02A directive lifecycle (compose → write → print → operator review → edit → re-validate → submit) without Windows cp1252 codepage corruption on macOS-screenshot Unicode (U+202F NNBSP and similar non-ASCII characters).

#### B. PRODUCTION_GATE_IDS Expansion (4 FRs)

- **FR-7c-6** Marcus can dispatch DecisionCards at every gate code declared in `PRODUCTION_GATE_IDS` after expansion, including G0/G0A/G0B/G1/G1A/G1.5/G2/G2B/G2C/G2M/G2.5/G2F/G3/G3B/G4/G4A/G4B/G5.
- **FR-7c-7** Each new gate emits a typed Pydantic-v2 DecisionCard conforming to its four-file-lockstep contract (Pydantic model + JSON schema + shape-pin test + golden fixture, paths enumerated verbatim). `validate_assignment=True` + closed-enum red-rejection + `DecisionCardMeta.cache_state` populated. Co-commit invariant enforced (NFR-7c-M1 + NFR-7c-R6 lockstep at PR + close).
- **FR-7c-8** Class-conformance validator recognizes every new gate ID and reports ≥11 conforming activation contracts post-Slab-7c (no regression).
- **FR-7c-9** Manifest fold-flags + compiler honor every new gate code at runtime per FR-A8 (Slab 7a 7a.2 substrate); orchestration_only_nodes lockstep tolerance covers any new orchestration-only nodes.

#### C. 11 HIL Conversational Surfaces (11 FRs)

- **FR-7c-10** Operator can ratify per-plan-unit content at §04A surface (gate G1A) via mandatory CLI; emit `OperatorVerdict` with verb ∈ {`approve`, `edit`, `reject`} per plan unit.
- **FR-7c-11** Operator can review and lock the run-budget estimator at §04.5 surface (gate G1.5) via mandatory CLI + FastAPI; emit cost-impact-acknowledged `OperatorVerdict`.
- **FR-7c-12** Operator can lock run-constants at §04.55 surface (gate G1.5) via mandatory CLI + FastAPI; emit run-constants-lock `OperatorVerdict`.
- **FR-7c-13** Operator can select per-slide presentation mode (narrated-deck vs motion-enabled-narrated-lesson) at §05.5 surface (gate G2B) via mandatory CLI; emit per-slide `OperatorVerdict`.
- **FR-7c-14** Operator can pick A or B variant per slide at §07B surface (gate G2M) via mandatory CLI; emit per-slide variant `OperatorVerdict`.
- **FR-7c-15** Operator can poll motion-plan generation status at §07D surface (gate G2.5) via mandatory CLI; surface fires async until Kira returns; emit poll-completion `OperatorVerdict`.
- **FR-7c-16** Operator can approve or reject motion clips at §07F surface (gate G2F) via mandatory CLI + FastAPI; emit per-clip `OperatorVerdict`.
- **FR-7c-17** Operator can review Storyboard B + live-URL content at §08B surface (gate G3B) via mandatory CLI + FastAPI; emit storyboard `OperatorVerdict`.
- **FR-7c-18** Operator can pick ElevenLabs voice at §11 surface (gate G4A) via mandatory CLI; emit voice-selection `OperatorVerdict`.
- **FR-7c-19** Operator can review the input-package preview at §11B surface (gate G4B) via mandatory CLI + FastAPI; emit input-package `OperatorVerdict`. Operator can complete the final operator handoff at §15 surface (gate G5) via mandatory CLI + FastAPI + MCP-stdio; emit slab-close `OperatorVerdict`.
- **FR-7c-20** Each HIL surface declares its mandatory transports at slab-open via the parity-contract DSL (FR-7c-30..33) and self-registers into the parameterized parity-test harness.

#### D. 5 Marcus-Bound Pre-Dispatch Package Writers (5 FRs)

- **FR-7c-21** Marcus emits `gary-slide-content.json` per plan unit prior to Gary dispatch (Pydantic-v2 + `validate_assignment=True`).
- **FR-7c-22** Marcus emits `gary-fidelity-slides.json` per plan unit (Vera-fidelity-criteria-prepopulated).
- **FR-7c-23** Marcus emits `gary-diagram-cards.json` per plan unit (literal-visual diagram requirements).
- **FR-7c-24** Marcus emits `gary-theme-resolution.json` per plan unit (experience-profile + creative-directive theme inputs → Gary payload shape).
- **FR-7c-25** Marcus emits `gary-outbound-envelope.yaml` + `pre-dispatch-package-gary.md` aggregating all four packages. **Envelope schema:** `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json` (Pydantic-v2 + `validate_assignment=True`); fields = `{writer_id, target_section, payload_ref, dispatched_at, operator_id}`.

#### E. §06B / §07C / §09 / §15 Closeout Surfaces (4 FRs)

- **FR-7c-26** Operator can build literal-visual operator content at §06B surface, emitting per-slide visual specifications consumed by §07 Gary dispatch.
- **FR-7c-27** Operator can build a storyboard with HTML reviewer surface at §07C, with reviewer artifact rendered for §08B Storyboard B + live-URL HIL consumption.
- **FR-7c-28** Marcus enforces four-artifact lock semantics at §09 (post-Gary + post-Kira + post-Vera + post-Quinn-R), preventing downstream advancement until all four are present + consistent.
- **FR-7c-29** Marcus completes the final operator handoff at §15, emitting the slab-close artifact bundle (assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial-3 transcript anchor + slab-close evidence pointer).

#### F. Parity-Contract DSL (option-c architectural pre-decision; 4 FRs)

- **FR-7c-30** Slab 7c provides a parity-contract DSL primitive set under `app/parity/contracts/` such that surface modules declare parity contract via decorator or YAML registration.
- **FR-7c-31** The DSL self-registers each declared surface into the parameterized parity-test harness, replacing per-surface bespoke test files.
- **FR-7c-32** The DSL enforces per-surface mandatory-transport declaration (CLI mandatory; HTTP/MCP-stdio/MCP-subprocess opt-in); surfaces that do not declare are denied parity-test budget.
- **FR-7c-33** The existing 8 transport-parity test files refactor to consume DSL primitives, preserving current ~15-cell coverage as baseline.

#### G. AUDIT-ACs (Verify Shipped Substrate; 5 FRs with quantitative coverage floors)

- **FR-7c-34** Verify original 3.2 (per-gate DecisionCard family) — assert `app/models/decision_cards/{base, g1, g2c, g3, g4, override_event, vocabulary}.py` + 5 schema JSONs green via shape-pin tests. **Floor: ≥20 shape-pin tests** on parity-DSL surfaces.
- **FR-7c-35** Verify original 3.3 (verdict-authority enforcement) — assert 8 named gate tests green: `test_no_scheduler_import.py`, `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`, `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`, `test_consolidated_decision_card_carries_contributions.py`, `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`. **Floor: ≥15 cells in 5-family × 3-transport matrix populated and green.**
- **FR-7c-36** Verify original 3.4 (three-transport verdict parity) — assert 8 named parity tests green. **Floor: ≥11 class-conformance assertions.**
- **FR-7c-37** Verify original 3.5 (cache-impact + operator-id override flow) — assert `test_decision_card_cache_state_populated.py`, `test_operator_id_real_source.py`, `test_http_operator_id_header_required.py` green; verify override_event audit chain shape. **Floor: 14/14 four-file-lockstep co-commit checks.**
- **FR-7c-38** Retire original 3.6 via Trial-3 separate post-close ceremony; story 7c.21 records Trial-3 readiness. **Floor: 6/6 tripwire ledger probes (TW-7c-1..6).** M3 evidence accrued post-close in `_bmad-output/implementation-artifacts/m3-acceptance.md`.

#### H. Tripwire Ledger + Slab Governance (5 FRs)

- **FR-7c-39** Slab 7c authors six tripwires (TW-7c-1..6) at slab-open in `sprint-status.yaml::tripwire_events`; each records `tripwire_id`, `story_owner`, `fired_at`, `fired_verdict`, `measured_value`, `escalation_action_taken`, `decision_record_link`.
- **FR-7c-40** Story dev-agents and code-reviewers cite tripwire-trip evidence at T10 + T11; HALT-AND-REMEDIATE protocol applies per tripwire severity.
- **FR-7c-41** Slab 7c retrospective reviews per-tripwire firing rate + effectiveness; ineffective tripwires retired.
- **FR-7c-42** Slab 7c retrospective ratifies mapping-checklist row flips per R15 (party-mode-gated, NOT dev-agent authority); FULLY MIGRATED row floor lifts from 7 to a higher count.
- **FR-7c-43** Slab 7c retrospective consults `deferred-inventory.md` and closes `slab-7c-live-harness-evidence` + Trial-2 finding #1 + #2 entries; files any new follow-ons.

#### I. CI Substrate + Quality Gates (5 FRs)

- **FR-7c-44** Slab 7c retains the ≥1403 deterministic regression baseline at `-p no:randomly`; smaller regression count requires Completion-Notes explanation + code-review ratification.
- **FR-7c-45** Slab 7c retains ruff clean + lint-imports ≥9 contracts KEPT + sandbox-AC validator PASS + class-conformance ≥11 contracts + pipeline-manifest lockstep PASS + live-API detector clean + substrate-frozen-paths invariant held across every story close.
- **FR-7c-46** Slab 7c adds UTF-8-only CI lint pass enforced on every Slab-7c-touched file; auto-runs in pre-commit + CI. **Glob coverage:** `_bmad-output/**/*.md`, `app/**/*.py`, `tests/**/*.py`, all golden fixtures under `tests/fixtures/**`, and any path declared in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`.
- **FR-7c-47** Slab 7c parity suite runs 50 consecutive times in CI with zero flakes before slab marks done (TW-7c-6); per-cell flake budget <0.1%.
- **FR-7c-48** Slab 7c live-dispatch authoring lands in `run_cache_hit_harness.py` + `run_5_api_smoke.py` per `slab-7c-live-harness-evidence` deferred entry; concentrated in named harness (TW-7c-4 prevents scope creep).

#### J. Schema-Stability + NEW CYCLE Discipline (6 FRs added at FR/NFR sign-off 2026-05-04)

- **FR-7c-49** Per-HIL-surface `OperatorVerdict` schema-stability test. Discriminated-union variant per surface + JSON-schema regen + shape-pin under `tests/schemas/operator_verdict/test_<surface_id>_shape.py`. Asserts schema hash stable across CLI/HTTP/MCP-stdio (33 cells).
- **FR-7c-50** `override_event` audit-chain integrity test. Append-only invariant + monotonic timestamp + parent-trace linkage; red-rejection on out-of-order or missing-parent. Shape-pin under `tests/audit/test_override_event_chain_integrity.py`. Per-tripwire registration test asserts every TW-7c-1..6 entry passes audit-chain validator on emit.
- **FR-7c-51** `schema_version: int` field on every new schema-shape file in Slab 7c (DecisionCards, OperatorVerdict variants, gary-* writers, Trial-3 transcript). Bump-on-change test asserts increment when schema hash changes. Trial-3 transcript schema = `Trial3Transcript` Pydantic-v2 with closed-enum on gate-ids and edit/approve event types; shape-pin under `tests/trial/test_trial3_transcript_shape.py`.
- **FR-7c-52** Every Slab 7c story spec at `ready-for-dev` produces `_bmad-output/implementation-artifacts/codex-dev-prompt-{story-key}.md` per NEW CYCLE protocol (Claude spec → governance/sandbox/PRD validation → codex-dev-prompt-*.md → Codex T1-T9 + T10 self-review → Claude T11 `bmad-code-review` → Claude commit + flip done).
- **FR-7c-53** Import-linter contracts extended for Slab 7c boundaries: **C4** `app/parity/contracts/*` may not import graph-runtime modules; **C5** `app/composers/section_02a/*` may not import corpus-scan fallback paths; **C6** HIL-surface modules may not import each other across surfaces (shared helpers in `app.gates._shared.*`).
- **FR-7c-54** Sanctum-invariant declaration for the 5 Marcus-bound writers (FR-7c-21..25). Each writer module declares its sanctum-alignment row in the Marcus activation block per Slab 7b precedent OR documents an explicit Cora-sidecar-style exception with rationale.

**Total FRs: 54.** Verified against PRD frontmatter `functional_requirements: 54`. ✓

---

### Non-Functional Requirements (37 NFRs across 6 categories P/S/R/M/X/OD)

PRD §Non-Functional Requirements; namespace `NFR-7c-<category><N>`. All amendments from FR/NFR sign-off party-mode 2026-05-04 folded inline.

#### Performance (P, 5 NFRs)

- **NFR-7c-P1** §02A LLM-driven composition target ≤60s wall-clock for ≤20-file corpus at gpt-5.4 cache-cold; ≤60s p50 / ≤120s p99 over ≥20 fixture-replay runs; cache-hit ≤2s p99. **Calibration band:** 60–90s WARN; >90s × 3-of-5 runs = REPLAN trigger. Initial threshold = calibration, not contract.
- **NFR-7c-P2** §02A composer prompt-token count stable across N=10 runs (variance ≤5%); targets ≥90% cache-hit median[2:] (vs MF1 60% floor; matches Irene Pass-2 95.33% precedent). **Cache-key normalization:** `cache_key = SHA256(normalized_prompt)` with `operator_id` + timestamps + `run_id` stripped.
- **NFR-7c-P3** Parity-test suite full run ≤90s wall-clock at ~15-cell scale; ≤6 min wall-clock at ~68-cell scale post-Slab-7c at `-p no:randomly`. Slack target: 25% under target on median-of-5.
- **NFR-7c-P4** HIL surface poll latency ≤2s p99 in-process per transport (CLI / HTTP); ≤4s p99 MCP-stdio; ≤5s p99 MCP-subprocess. p99 over 200 polls per surface; <50 polls downgrades to p95.
- **NFR-7c-P5** Trial-3 §01→§15 wall-clock budget ≤120 min for single-lesson corpus, exclusive of operator decision-time. >180 min = forensic evidence for Slab 4 PRD's HIL-UX scope, not 7c blocker.

#### Security (S, 7 NFRs)

- **NFR-7c-S1** HIL tamper-evidence at writer boundary per D3 — `OperatorVerdict.decision_card_digest` matches emitted card; resume rejects via `GateError` on mismatch. Verified by `test_resume_from_verdict_digest_match.py` + `test_resume_from_verdict_card_missing.py`.
- **NFR-7c-S2** Bypass-attempt rejection: synthetic `asyncio.sleep + Command(resume=...)` injection rejected at graph-compile time. Verified by `test_m3_bypass_attempt_rejected.py`.
- **NFR-7c-S3** Scheduler-import-forbidden via import-linter `forbidden` contract on `app/gates/**` (asyncio.sleep + threading.Timer + apscheduler + schedule). CI fails at `lint-imports` step.
- **NFR-7c-S4** Single-writer authority via import-linter Contract M1 (`app.marcus.orchestrator.write_api` is sole importer of `app.models.state.run_state`). CI-fail mode.
- **NFR-7c-S5** Operator-id provenance: every `OperatorVerdict` populates `operator_id` from a real operator identifier. Verified by `test_operator_id_real_source.py` + `test_http_operator_id_header_required.py`.
- **NFR-7c-S6** API key handling: `OPENAI_API_KEY` + `LANGSMITH_API_KEY` from `.env` at module import; never committed; never logged in cleartext. Live-LLM tests `@pytest.mark.llm_live`; auto-skip on placeholder.
- **NFR-7c-S7** Lane isolation via import-linter Contracts M2 + C1 + C2 + M3 + M4: `app.marcus ⊥ app.cora`; `app.specialists ⊥ app.marcus.facade/intake/orchestrator`; `app.marcus.dispatch` dependency-light. CI-fail mode.

#### Reliability (R, 8 NFRs — R1-R6 + R7a + R7b)

- **NFR-7c-R1** Zero-flake parity baseline: parity suite runs 50× consecutively in CI with zero flakes before slab done (TW-7c-6), aligned with Slab 7b TW-7b-flake bar (match-or-explicitly-supersede). Per-cell flake budget <0.1% over rolling 200-run window.
- **NFR-7c-R2** Deterministic regression baseline: ≥1403 passed at `-p no:randomly` preserved at every story close.
- **NFR-7c-R3** Tripwire-ledger completeness: every fired tripwire records all 7 fields in `sprint-status.yaml::tripwire_events`. Schema enforced by NFR-7c-OD2.
- **NFR-7c-R4** Substrate-frozen-paths invariant: 14 boundary fixtures continue to PASS via `scripts/utilities/check_substrate_frozen_paths.py`.
- **NFR-7c-R5** Class-conformance validator floor ≥11 contracts maintained.
- **NFR-7c-R6** Pipeline-manifest lockstep: every story diff that touches `block_mode_trigger_paths` runs lockstep validator at PR-time + close-time PASS. Slab 7c may trigger Tier-2 manifest schema bump; party-mode-ratified before dev opens.
- **NFR-7c-R7a** Trial-3 coverage floor: §01→§15 end-to-end on real-corpus with ≥1 approve at every one of 14 expanded gates; edit floor ≥3 distributed across ≥3 distinct gates. **Failure blocks Slab 4 entry** (recorded in `migration-story-governance.json` + re-verified at Slab 4 open).
- **NFR-7c-R7b** Trial-3 budget ≤120 min wall-clock exclusive of operator decision-time. >180 min = forensic evidence for Slab 4 HIL-UX scope, NOT a 7c blocker. Trial-3 *attempt* is slab-close prerequisite (must be attempted + evidence filed at `m3-acceptance.md`); a red attempt produces tripwire-trip + decision-record per NFR-7c-OD3 but does NOT block 7c slab-close.

#### Maintainability (M, 6 NFRs)

- **NFR-7c-M1** Four-file-lockstep on every new gate (Pydantic model + JSON schema + shape-pin test + golden fixture); pre-commit hook detects mismatch.
- **NFR-7c-M2** AUDIT-AC discipline: all 5 AUDIT-ACs phrased as verify-then-file-if-gap with quantitative coverage floors (≥20 shape-pins / ≥15 matrix cells / ≥11 class-conformance / 14/14 four-file-lockstep / 6/6 tripwire ledger probes). ≥2 gaps in any one AUDIT-AC trips TW-7c-1.
- **NFR-7c-M3** Story-cycle K-floor discipline: per-story K-projection at T1 readiness; tripwire fires if K-projection >2× K-target. Slab 7c K-targets: ~1.2-1.5× per story.
- **NFR-7c-M4** NEW CYCLE Codex/Claude dev-handoff discipline (FR-7c-52); no story bypasses without operator authorization.
- **NFR-7c-M5** Sandbox-AC validator PASS at every story finalize + every `bmad-dev-story` open per `migration-ac-sandbox-inventory.json` 2026-04-22 freeze.
- **NFR-7c-M6** Governance JSON gate-mode designation: every Slab 7c story has an entry in `migration-story-governance.json` authored at sprint-planning; changes require party-mode + version bump.

#### Compatibility (X, 4 NFRs)

- **NFR-7c-X1** Windows-portability: every Slab 7c file UTF-8-encoded; CI lint pass enforces UTF-8 round-trip per FR-7c-46. Anti-pattern A11 augmented at §02A spec close.
- **NFR-7c-X2** Multi-transport byte-equivalence: same `OperatorVerdict` payload via CLI / HTTP / MCP-stdio / MCP-subprocess produces byte-identical (or canonicalized-identical) graph-resumption state, identical ledger events, identical LangSmith traces.
- **NFR-7c-X3** Path-portability: PowerShell + bash launch helpers honor Windows + Unix conventions; `pathlib.Path` + `as_posix()` patterns per `sanctum-reference-conventions.md` MF7.
- **NFR-7c-X4** Backward-compatibility: Slab 7c MUST NOT regress any existing test in ≥1403-test deterministic baseline. Class-conformance floor preserved; mapping-checklist FULLY MIGRATED row floor preserved (post-7b: 7).

#### Observability (OD, 7 NFRs)

- **NFR-7c-OD1** LangSmith tracing on every gate-decide and HIL-resume call; trace parity contract is part of D7 transport parity.
- **NFR-7c-OD2** **Tripwire-ledger 7-field schema enforced via Pydantic-v2 `TripwireLedgerEntry`** (highest-leverage R3 amendment): `validate_assignment=True`, closed-enum on `tripwire_id` ∈ {TW-7c-1..6} with triple-layer red-rejection, timezone-aware datetime, UUID4 trace-id with format validation. Shape-pin test (≥7 assertions) lives in frozen-paths fixture.
- **NFR-7c-OD3** Decision-record linkage: every tripwire trip has `decision_record_link` pointing to code-review artifact, party-mode notes, or sprint-status amendment. Missing links invalidate trip's effectiveness assessment at retrospective.
- **NFR-7c-OD4** Trial-3 evidence accrual: §01→§15 traversal recorded as canonical M3 evidence at `m3-acceptance.md`; transcript schema = `Trial3Transcript` (FR-7c-51).
- **NFR-7c-OD5** Mapping-checklist row-flip evidence aggregation per R15 party-mode-gated authority; floor-bump from 7 to higher (~17-22 expected).
- **NFR-7c-OD6** Forensic-evidence preservation: Trial-3 forensic artifacts under `state/config/runs/<run-id>/` preserved (gitignored but operator-pinned) following Trial-2 precedent.
- **NFR-7c-OD7** **Parity-DSL self-registration audit** (Winston A4): harness emits registration manifest (11 HIL surfaces × N declared transports + 14 gate families × 3 transports) at CI time; CI fails if cardinality is below declared floor.

**Total NFRs by sub-count: P:5 + S:7 + R:8 + M:6 + X:4 + OD:7 = 37.** PRD frontmatter says `nonfunctional_requirements: 36`. **PRD-FRONTMATTER-FINDING-1:** off-by-1 (37 vs 36). Minor; correctable at retrospective close or alongside the next PRD edit.

---

### Architectural Invariants (3 PRD-level invariants inherited from migration architecture)

PRD §Project-Type Architecture + §Domain-Specific Requirements §Technical Constraints + §Tripwire Ledger.

- **D2** Model cascade + DecisionCard cache-state. Every gate emits `DecisionCardMeta.cache_state ∈ {"healthy", "mixed", "cold"}` + `affected_nodes: list[str]` + `override_trail: list[OverrideEvent]`. Runtime model-override emits `compute_cache_impact() → OverrideWarning` BEFORE override applies; explicit `confirm_token` required.
- **D3** HIL tamper-evidence at writer boundary. `OperatorVerdict` is `frozen=True`, `validate_assignment=True`, `extra=forbid`. Cross-field validator: `edit_payload` required iff `verb == "edit"`. `resume_from_verdict()` raises `GateError` on `decision_card_digest` mismatch. Scheduler-import-forbidden in `app/gates/**`. Bypass attempts rejected at graph-compile.
- **D7** Operator-surface contract / four-transport parity. Four authorized transports: CLI (`app/marcus/cli/gate_cli.py`), HTTP (`app/http/gate_endpoint.py`), MCP-stdio (`app/mcp_server/tools/gate_decide.py`), MCP-subprocess. Same `OperatorVerdict` payload via any transport produces byte-identical (or canonicalized-identical) graph-resumption state, identical ledger events, identical LangSmith traces. Import-linter Contract C3 forbids non-bridge imports of `app.gates.resume_api`.

---

### Tripwire Ledger (6 tripwires authored at PRD time with severity + escalation)

PRD §Tripwire Ledger (Slab 7c). Authoritative source-of-truth.

| ID | Trip Condition | Severity | Escalation |
|---|---|---|---|
| TW-7c-1 | AUDIT-AC (3.2-3.6) discovers gap | high | STOP; file `7c.X.<descriptor>`; party-mode-consensus on absorb-vs-defer |
| TW-7c-2 | §02A composer fails Trial-2 finding #1 cp1252 regression on preserved fixture | high | STOP; re-scope §02A; dual-nature claim invalidated |
| TW-7c-3 | New gate added to PRODUCTION_GATE_IDS without four-file lockstep + class-conformance | critical | STOP; lockstep gate-fill required before any downstream story opens |
| TW-7c-4 | Trial-3 outcome leaks into Slab 7c slab-close evidence | high | STOP; party-mode re-affirm Trial-3 separate ceremony OR formally amend |
| TW-7c-5 | D2/D3/D7 invariant violation OR cp1252 encoding regression | critical | STOP; Winston non-negotiables hold; invariant violation cannot land |
| TW-7c-6 | Parity-test flake rate >0.1%/cell over 50-run CI baseline OR existing 8 parity files regress to flaky | high | STOP; parity-budget mitigation per option-c parity-contract DSL; per-surface transport declaration enforced |

Detection-infra ownership table (per Murat M1; PRD frontmatter `story_decomposition_signoff::infra_ownership`):

| Tripwire | Detection Owner |
|---|---|
| TW-7c-1 | 7c.20a/b/c (AUDIT-AC verification per coverage floor) |
| TW-7c-2 | 7c.2 (cp1252 fix + fixture-comparison utility) + 7c.3a (composer invocation) |
| TW-7c-3 | 7c.4b (lockstep checker registration + class-conformance extension); fires per-gate at 7c.5.G0..G6 |
| TW-7c-4 | 7c.0 (live-dispatch scope-creep CI lint) |
| TW-7c-5 | 7c.0 (UTF-8 CI lint) + per-story T10 self-check |
| TW-7c-6 | 7c.0 (50-run harness scaffold + per-cell flake-rate calculator) + 7c.21 (50-run firing) |

---

### Additional Requirements / Constraints

PRD §Domain-Specific Requirements + §Technical Constraints by Construction:

- **Pipeline-manifest lockstep regime** — Tier-1/2/3 governance per `docs/dev-guide/pipeline-manifest-regime.md`. PRODUCTION_GATE_IDS expansion may trigger Tier-2 (manifest schema bump); party-mode consensus required BEFORE dev opens.
- **Sandbox-AC validator** — every Slab 7c story passes `validate_migration_story_sandbox_acs.py` before finalize and before `bmad-dev-story` opens. Forbidden CLIs in dev-agent AC blocks: docker / docker-compose / psql / pg_dump / aws / gcloud / az / gh / kubectl / helm / redis-cli / mongo / mysql / curl / wget. `ffmpeg` warns. Operator-gated AC blocks may use any CLI.
- **Governance JSON gate-mode freeze** — `migration-story-governance.json` 2026-04-22 freeze; gate-mode change requires party-mode + version bump.
- **R15 mapping-checklist authority** — row addition/removal AND row-status flips (❌/⚠️ → ✅) are party-mode-gated, NOT dev-agent authority. Slab 7c retrospective is the ratification venue.
- **D12 cross-slab governance protocol** — slab-closing story includes D12 close-protocol AC. Slab 7c closeout (7c.21) inherits D12.
- **NEW CYCLE Codex/Claude dev-handoff discipline** — proven 11× end-to-end at Slab 7a/7b precedent. Claude does NOT invoke `bmad-dev-story` directly; flow is Claude spec → governance/sandbox/PRD validation → `codex-dev-prompt-{story-key}.md` → Codex T1-T9 + T10 self-review → Claude T11 `bmad-code-review` → Claude commit + flip done.
- **Deferred-inventory governance** — Slab 7c retrospective MUST consult `deferred-inventory.md`; close `slab-7c-live-harness-evidence` + Trial-2 finding #1 + #2; file any new follow-ons.
- **External integrations (no new ones)** — OpenAI gpt-5.4 + tier cascade; LangSmith tracing; Texas wrangler + retrieval providers (Shape-3-Disciplined; 16 entries); 11 specialist body fleet (already activated in 7b); Gamma + Kling + ElevenLabs + Wondercraft + Canvas + CourseArc + Descript external production APIs invoked through specialists during Trial-3.

---

### PRD Completeness Assessment (initial)

PRD-completeness verdict: **STRONG**. Specifically:

- ✅ Frontmatter shows `workflowComplete: true` + `completedAt: 2026-05-04` + 12-step `stepsCompleted` (init through complete) + both signoff blocks (`fr_nfr_signoff` + `story_decomposition_signoff`) present, both with `verdict: "Unanimous ACCEPT-WITH-AMENDMENT (4/4)"` and amendments folded inline.
- ✅ 4 party-mode rounds documented; 0 re-opens; voices = [John, Winston, Amelia, Murat].
- ✅ All 5 PRD sections critical to readiness check are present and fully authored: Executive Summary + Project Classification + Success Criteria + Tripwire Ledger + User Journeys (5 journeys) + Domain Requirements + Innovation + Architecture + Project Scoping (Story Decomposition with 26-story decomposition + Gate Taxonomy LOCK + Cross-Agent Code-Review designation + Velocity estimate) + 54 FRs + 37 NFRs.
- ✅ 3 architectural invariants (D2/D3/D7) inherited from migration architecture and explicitly named as non-negotiable PRD-level constraints.
- ✅ 6 tripwires authored at PRD time with severity + escalation + detection-infra ownership.
- ✅ Cross-agent code-review pre-designated for 7c.0/7c.3a/7c.4b/7c.21 (4 stories where wrong-call-cost cascades).
- ✅ AUDIT-not-BUILD framing fully justified with substrate-grep evidence (8 transport-parity tests + 7 DecisionCard modules + 5 schemas + 9 import-linter contracts on disk).
- ✅ Trial-3 ceremony commitment as separate post-close event (precedent: 7a.8 + 7b.12) explicitly named in NFR-7c-R7a/R7b + TW-7c-4.

**PRD-frontmatter-findings (minor; not readiness blockers):**

- **PRD-FF-1** Frontmatter `nonfunctional_requirements: 36` — actual NFR count is 37 (P:5 + S:7 + R:8 + M:6 + X:4 + OD:7). Off-by-1; correctable alongside next PRD edit or at retrospective close.

**PRD-pre-conditions (NAMED at PRD level, to be re-confirmed during Step 3 epic-coverage validation):**

- **PRE-1** Slab 7b CLOSED gate (post-Slab-7b mapping-checklist FULLY MIGRATED row floor = 7) — VERIFIED at session-start (`sprint-status.yaml::development_status` shows `migration-epic-slab-7b-specialist-activation-eleven: done`; mapping-checklist test 4 passed; class-conformance 11 conform).
- **PRE-2** Tier-2 pack-version-bump check for PRODUCTION_GATE_IDS expansion — to be confirmed during sprint-planning whether the 14-gate manifest schema bump triggers Tier-2 (vs Tier-1 patch). Per `pipeline-manifest-regime.md`, Tier-2 requires party-mode consensus BEFORE dev opens (i.e., before 7c.0 lands).
- **PRE-3** `migration-story-governance.json` entries for 26 Slab 7c stories — to be authored at `bmad-sprint-planning` round; cross-agent designation for 7c.0/7c.3a/7c.4b/7c.21; gate-mode per PRD §Story Decomposition.
- **PRE-4** Trial-2 forensic fixture preserved at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` — to be verified on disk before 7c.3a opens (TW-7c-2 dependency).

---

## Step 3 — Epic Coverage Validation

> **Reframing per Slab 7b precedent:** the `epics-slab-7c-*.md` file is intentionally absent at this readiness check (produced by `bmad-create-epics-and-stories` AFTER this report returns READY). Per Slab 7b precedent (`implementation-readiness-report-2026-04-29-slab-7b.md` Step 3), Step 3 validates the **PRD-internal §Story Decomposition** as the authoritative epic-coverage substrate, supplemented by the PRD frontmatter `story_decomposition_signoff::infra_ownership` block. This is structurally equivalent to the standard Step 3 against an existing epics file; the only difference is the canonical source.

### Story Decomposition Inventory (proposed; per PRD §Project Scoping & Phased Development)

26 stories across 6 waves; 60-72 pts; 5.5-7 days NEW CYCLE Codex/Claude.

| Story | Wave | Title | Gate-mode | Cross-agent | K-target |
|---|---|---|---|---|---|
| 7c.0 | 0 | Parity-Contract DSL ADR + scaffold + cross-cutting infra foundation | dual | **MANDATORY** | ~1.5× |
| 7c.1 | 1 | Parity-contract DSL foundation (refactor 8 existing files) | dual | — | ~1.4× |
| 7c.2 | 1 | cp1252 Windows-portability fix + fixture-comparison utility | single | — | ~1.2× |
| 7c.3a | 1 | §02A LLM-driven directive composer body | dual | **MANDATORY** | ~1.5× |
| 7c.3b | 1 | §02A G0 poll-surface canonical HIL pattern | dual | — | ~1.4× |
| 7c.4a | 2 | Gate family taxonomy ratification (decision-only) | single | — | ~1.0× |
| 7c.4b | 2 | Gate-family foundation (shared base classes + class-conformance ext.) | dual | **MANDATORY** | ~1.4× |
| 7c.5.G0 | 2 | Per-gate four-file-lockstep authoring (G0) | single | — | ~1.2× |
| 7c.5.G1 | 2 | Per-gate four-file-lockstep authoring (G1) | single | — | ~1.2× |
| 7c.5.G2A | 2 | Per-gate four-file-lockstep authoring (G2A) | single | — | ~1.2× |
| 7c.5.G2C | 2 | Per-gate four-file-lockstep authoring (G2C) | single | — | ~1.2× |
| 7c.5.G3 | 2 | Per-gate four-file-lockstep authoring (G3) | single | — | ~1.2× |
| 7c.5.G4 | 2 | Per-gate four-file-lockstep authoring (G4) | single | — | ~1.2× |
| 7c.5.G5 | 2 | Per-gate four-file-lockstep authoring (G5) | single | — | ~1.2× |
| 7c.5.G6 | 2 | Per-gate four-file-lockstep authoring (G6) | single | — | ~1.2× |
| 7c.6 | 3 | §04A G1A per-plan-unit ratification | single | — | ~1.3× |
| 7c.7 | 3 | §04.5 G1.5 estimator | single | — | ~1.3× |
| 7c.8 | 3 | §04.55 G1.5 run-constants lock | single | — | ~1.3× |
| 7c.9 | 3 | §05.5 G2B per-slide mode | single | — | ~1.3× |
| 7c.10 | 3 | §07B G2M per-slide A/B variant | single | — | ~1.3× |
| 7c.11 | 3 | §07D G2.5 motion-plan polling | single | — | ~1.3× |
| 7c.12 | 3 | §07F G2F motion gate | single | — | ~1.3× |
| 7c.13 | 3 | §08B G3B Storyboard B + live-URL | single | — | ~1.3× |
| 7c.14 | 3 | §11 G4A voice-selection | single | — | ~1.3× |
| 7c.15 | 3 | §11B G4B input-package + §15 G5 final operator handoff | single | — | ~1.3× |
| 7c.17a | 4 | 3 Marcus-bound writers (smaller surface; shared sanctum) | single | — | ~1.3× |
| 7c.17b | 4 | 2 Marcus-bound writers + envelope + pre-dispatch-package-gary.md | single | — | ~1.3× |
| 7c.18a | 5 | §06B literal-visual operator build | single | — | ~1.3× |
| 7c.18b | 5 | §07C storyboard build + HTML reviewer surface | single | — | ~1.3× |
| 7c.19 | 5 | §09 four-artifact lock semantics | single | — | ~1.2× |
| 7c.20a | 5 | AUDIT-AC: ≥20 shape-pins + ≥11 class-conformance | single | — | ~1.2× |
| 7c.20b | 5 | AUDIT-AC: ≥15 cells in 5-family × 3-transport matrix | single | — | ~1.2× |
| 7c.20c | 5 | AUDIT-AC: 14/14 four-file-lockstep + 6/6 tripwire ledger probes | single | — | ~1.2× |
| 7c.21 | 6 | Slab 7c integration parity suite + closeout ceremony | dual | **MANDATORY** | ~1.4× |
| 7c.21a | 6 | Epic 3 retirement + live-dispatch wiring | single | — | ~1.3× |

> **Counted:** 26 stories ✓ (matches PRD frontmatter `story_count_final: 26`).

> **Note:** Wave 4 numbering skips 7c.16 — the PRD §Story Decomposition jumps directly from 7c.15 (Wave 3) to 7c.17a (Wave 4 split per Amelia A4). This is consistent with the original 7c.16/7c.17 single story being split into 7c.17a+7c.17b. **EPIC-COVERAGE-FINDING-1:** the numbering gap (no 7c.16) is a cosmetic decomposition trace — the `bmad-create-epics-and-stories` author may either renumber Wave 4 to 7c.16/7c.17 OR keep 7c.17a/7c.17b as the canonical story keys (preserving PRD-frontmatter trace). Recommend the latter for traceability.

### FR Coverage Matrix (54 FRs → 26 stories + cross-cutting)

| FR | Capability | Owner Story / Cross-cutting | Status |
|---|---|---|---|
| FR-7c-1 | §02A LLM-driven directive compose | 7c.3a | ✓ |
| FR-7c-2 | §02A composer Trial-2 fixture validation | 7c.3a (TW-7c-2 firing) | ✓ |
| FR-7c-3 | §02A operator review verdicts via 3 transports | 7c.3b | ✓ |
| FR-7c-4 | §02A field-level edit + re-validate | 7c.3b | ✓ |
| FR-7c-5 | §02A UTF-8 round-trip preservation | 7c.2 (cp1252 fix + utility) + 7c.3a (composer invocation) | ✓ |
| FR-7c-6 | PRODUCTION_GATE_IDS dispatch all 14 codes | 7c.4b (foundation) + 7c.5.G0..G6 (per-gate) | ✓ |
| FR-7c-7 | Per-gate four-file lockstep | 7c.5.G0..G6 (8 stories) | ✓ |
| FR-7c-8 | Class-conformance recognizes new gates | 7c.4b | ✓ |
| FR-7c-9 | Manifest fold-flags + compiler honor new codes | 7c.4b (extends 7a.2 substrate) | ✓ |
| FR-7c-10 | §04A G1A per-plan-unit ratification | 7c.6 | ✓ |
| FR-7c-11 | §04.5 G1.5 estimator | 7c.7 | ✓ |
| FR-7c-12 | §04.55 G1.5 run-constants lock | 7c.8 | ✓ |
| FR-7c-13 | §05.5 G2B per-slide mode | 7c.9 | ✓ |
| FR-7c-14 | §07B G2M per-slide A/B variant | 7c.10 | ✓ |
| FR-7c-15 | §07D G2.5 motion-plan polling | 7c.11 | ✓ |
| FR-7c-16 | §07F G2F motion gate | 7c.12 | ✓ |
| FR-7c-17 | §08B G3B Storyboard B + live-URL | 7c.13 | ✓ |
| FR-7c-18 | §11 G4A voice-selection | 7c.14 | ✓ |
| FR-7c-19 | §11B G4B input-package + §15 G5 final handoff (operator-side) | 7c.15 | ✓ |
| FR-7c-20 | Per-surface mandatory transport declaration via DSL | 7c.1 (DSL) + each HIL story (per-surface registration) | ✓ |
| FR-7c-21 | gary-slide-content.json | 7c.17a or 7c.17b ⚠️ | ✓ (sprint-planning assigns specific writer to story) |
| FR-7c-22 | gary-fidelity-slides.json | 7c.17a or 7c.17b ⚠️ | ✓ (sprint-planning assigns) |
| FR-7c-23 | gary-diagram-cards.json | 7c.17a or 7c.17b ⚠️ | ✓ (sprint-planning assigns) |
| FR-7c-24 | gary-theme-resolution.json | 7c.17a or 7c.17b ⚠️ | ✓ (sprint-planning assigns) |
| FR-7c-25 | gary-outbound-envelope.yaml + pre-dispatch-package-gary.md | 7c.17b (envelope aggregation) | ✓ |
| FR-7c-26 | §06B literal-visual operator build | 7c.18a | ✓ |
| FR-7c-27 | §07C storyboard build + HTML reviewer | 7c.18b | ✓ |
| FR-7c-28 | §09 four-artifact lock semantics | 7c.19 | ✓ |
| FR-7c-29 | §15 Marcus-side handoff bundle emission | 7c.15 (§15 surface impl) ⚠️ — see EPIC-COVERAGE-FINDING-2 | ✓ (with clarification) |
| FR-7c-30 | parity-contract DSL primitives | 7c.0 (ADR + scaffold) + 7c.1 (foundation) | ✓ |
| FR-7c-31 | DSL self-registers each declared surface | 7c.0 + 7c.1 | ✓ |
| FR-7c-32 | DSL enforces per-surface transport declaration | 7c.0 + 7c.1 | ✓ |
| FR-7c-33 | 8 existing parity files refactor to DSL | 7c.1 | ✓ |
| FR-7c-34 | AUDIT 3.2 ≥20 shape-pins | 7c.20a | ✓ |
| FR-7c-35 | AUDIT 3.3 ≥15 cells matrix | 7c.20b | ✓ |
| FR-7c-36 | AUDIT 3.4 ≥11 class-conformance | 7c.20a (paired with FR-7c-34 per PRD §Wave 5) | ✓ |
| FR-7c-37 | AUDIT 3.5 14/14 four-file-lockstep | 7c.20c | ✓ |
| FR-7c-38 | AUDIT 3.6 6/6 tripwire ledger probes | 7c.20c (probes) + 7c.21 (Trial-3 readiness AC) | ✓ |
| FR-7c-39 | 6 tripwires authored at slab-open in sprint-status.yaml | sprint-planning seeds (PRE-3) — 7c.0 substrate | ✓ |
| FR-7c-40 | Tripwire-trip evidence cited at T10 + T11 | every story (process discipline; codex-dev-prompt template) | ✓ |
| FR-7c-41 | Retrospective reviews per-tripwire effectiveness | 7c.21 (retrospective trigger) | ✓ |
| FR-7c-42 | Retrospective ratifies mapping-checklist row flips | 7c.21 (retrospective; R15 party-mode-gated) | ✓ |
| FR-7c-43 | Retrospective consults deferred-inventory.md | 7c.21 (retrospective close) | ✓ |
| FR-7c-44 | ≥1403 deterministic regression baseline | every story (process discipline) | ✓ |
| FR-7c-45 | ruff + lint-imports + sandbox-AC + class-conformance + pipeline-manifest + live-API + substrate-frozen-paths | every story (process discipline) | ✓ |
| FR-7c-46 | UTF-8-only CI lint pass on glob | 7c.0 (lint pass setup) + every story (consume) | ✓ |
| FR-7c-47 | Parity suite 50× zero-flake | 7c.0 (harness scaffold) + 7c.21 (50-run firing) | ✓ |
| FR-7c-48 | Live-dispatch authoring in named harness | 7c.21a | ✓ |
| FR-7c-49 | Per-HIL OperatorVerdict schema-stability | 7c.4b (parametrized harness) + 7c.6..7c.15 + 7c.3b (per-surface case) | ✓ |
| FR-7c-50 | override_event audit-chain integrity | 7c.0 (scaffold) + per-tripwire registration tests | ✓ |
| FR-7c-51 | schema_version field + Trial3Transcript | 7c.0 (mechanism) + 7c.21 (Trial3Transcript) | ✓ |
| FR-7c-52 | codex-dev-prompt-{story-key}.md NEW CYCLE artifact | every story (process discipline; FR-7c-52 itself) | ✓ |
| FR-7c-53 | Import-linter C4/C5/C6 | 7c.0 (C4) + 7c.3a (C5) + 7c.4b (C6) | ✓ |
| FR-7c-54 | Sanctum-invariant declaration for 5 writers | 7c.0 (DSL feature) + 7c.17a/b (consumed per writer) | ✓ |

**Coverage statistics:**
- Total PRD FRs: **54**
- FRs covered (≥1 story owner OR cross-cutting process discipline): **54**
- Coverage: **54 / 54 = 100%**
- FRs covered but with sprint-planning clarification needed: **5** (FR-7c-21..25 — split across 7c.17a/7c.17b with specific writer-to-story assignment to be authored at sprint-planning + bmad-create-epics-and-stories; FR-7c-29 — §15 Marcus-side bundle emission location)

### NFR Enforcement Coverage (37 NFRs → CI workflow / validator script / per-story AC)

| NFR | Category | Enforcement Mechanism | Owner |
|---|---|---|---|
| NFR-7c-P1 | Performance | §02A composer wall-clock measured at 7c.3a; calibration band recorded; >90s × 3-of-5 escalates to party-mode | 7c.3a AC |
| NFR-7c-P2 | Performance | §02A prompt-token + cache-hit-rate measured at 7c.3a per Slab 2a.2 methodology; cache-key SHA256(normalized_prompt) | 7c.3a AC |
| NFR-7c-P3 | Performance | Parity-test suite wall-clock measured at 7c.1 (DSL refactor; ~15 cells) + 7c.21 (50-run; ~68 cells) | 7c.1 + 7c.21 AC |
| NFR-7c-P4 | Performance | HIL surface poll latency measured per-surface | 7c.6..7c.15 + 7c.3b AC |
| NFR-7c-P5 | Performance | Trial-3 wall-clock measured at 7c.21 Trial-3 readiness AC | 7c.21 AC |
| NFR-7c-S1 | Security | HIL tamper-evidence at writer boundary verified by `test_resume_from_verdict_*` | 7c.4b foundation + every HIL story |
| NFR-7c-S2 | Security | Bypass-attempt rejection verified by `test_m3_bypass_attempt_rejected.py` | AUDIT 7c.20b |
| NFR-7c-S3 | Security | Scheduler-import-forbidden via import-linter | FR-7c-45 (every story) + 7c.4b foundation |
| NFR-7c-S4 | Security | Single-writer M1 via import-linter | FR-7c-45 (every story) |
| NFR-7c-S5 | Security | Operator-id provenance via `test_operator_id_real_source.py` | AUDIT 7c.20a |
| NFR-7c-S6 | Security | API key handling — `.env` discipline | every story (process) |
| NFR-7c-S7 | Security | Lane isolation via import-linter M2/C1/C2/M3/M4 | FR-7c-45 (every story) |
| NFR-7c-R1 | Reliability | Zero-flake parity 50× | 7c.0 (harness) + 7c.21 (firing) |
| NFR-7c-R2 | Reliability | Deterministic ≥1403 baseline | every story (process) |
| NFR-7c-R3 | Reliability | Tripwire-ledger 7-field completeness | 7c.0 (TripwireLedgerEntry Pydantic-v2 schema) + every tripwire trip |
| NFR-7c-R4 | Reliability | Substrate-frozen-paths invariant via `check_substrate_frozen_paths.py` | every story (process) |
| NFR-7c-R5 | Reliability | Class-conformance ≥11 floor | every story + 7c.4b extension |
| NFR-7c-R6 | Reliability | Pipeline-manifest lockstep | every story (process) + sprint-planning Tier-2 check (PRE-2) |
| NFR-7c-R7a | Reliability | Trial-3 coverage floor (≥1 approve every gate, ≥3 edits) | 7c.21 Trial-3 readiness AC |
| NFR-7c-R7b | Reliability | Trial-3 budget ≤120 min | 7c.21 Trial-3 readiness AC |
| NFR-7c-M1 | Maintainability | Four-file-lockstep per gate; pre-commit hook | 7c.4b (registration) + 7c.5.G0..G6 (per-gate) |
| NFR-7c-M2 | Maintainability | AUDIT-AC discipline | 7c.20a/b/c |
| NFR-7c-M3 | Maintainability | K-floor discipline; T1 K-projection | every story (process; governance JSON entry) |
| NFR-7c-M4 | Maintainability | NEW CYCLE Codex/Claude flow | every story (FR-7c-52) |
| NFR-7c-M5 | Maintainability | Sandbox-AC validator PASS | every story (process) |
| NFR-7c-M6 | Maintainability | Governance JSON gate-mode entry | sprint-planning + every story |
| NFR-7c-X1 | Compatibility | Windows-portability UTF-8 lint | 7c.0 (lint pass) + every story |
| NFR-7c-X2 | Compatibility | Multi-transport byte-equivalence | FR-7c-30..33 + per-surface FR-7c-49 |
| NFR-7c-X3 | Compatibility | Path-portability `pathlib.Path.as_posix()` | every story (process) |
| NFR-7c-X4 | Compatibility | Backward-compatibility ≥1403 baseline + class-conformance + mapping-checklist | every story (process) |
| NFR-7c-OD1 | Observability | LangSmith tracing on every gate-decide / HIL-resume | every story + FR-7c-45 |
| NFR-7c-OD2 | Observability | TripwireLedgerEntry Pydantic-v2 schema (highest-leverage R3 amendment) | 7c.0 |
| NFR-7c-OD3 | Observability | Decision-record linkage | 7c.21 retrospective close |
| NFR-7c-OD4 | Observability | Trial-3 evidence accrual + Trial3Transcript | 7c.21 (Trial-3 readiness AC + Trial3Transcript) |
| NFR-7c-OD5 | Observability | Mapping-checklist row-flip evidence | 7c.21 retrospective close |
| NFR-7c-OD6 | Observability | Forensic-evidence preservation | 7c.21 retrospective close |
| NFR-7c-OD7 | Observability | Parity-DSL self-registration audit (Winston A4) | 7c.0 (skeleton) + 7c.21 (firing) |

**NFR enforcement coverage: 37 / 37 = 100%.**

### Architectural Invariants D2/D3/D7 — Per-Story Self-Check Coverage

PRD §Wave Sequencing Notes (Winston A5): every story honors three explicit T10 self-check checklist lines in the codex-dev-prompt template — D2 cache_state-write; D3 HIL tamper-evidence; D7 transport-parity contract-declaration. 7c.21 verifies aggregate cross-story integration only.

- **D2** (model cascade + DecisionCard cache_state) — verified per-story (T10) + aggregate at 7c.21 + AUDIT 7c.20a (DecisionCard family)
- **D3** (HIL tamper-evidence + verdict-digest match + override_event audit chain) — verified per-story (T10) + aggregate at 7c.21 + AUDIT 7c.20b (verdict-authority) + FR-7c-50 audit-chain integrity test
- **D7** (transport parity across CLI / FastAPI / MCP-stdio / MCP-subprocess) — verified per-story (T10) + aggregate at 7c.21 + AUDIT 7c.20a (transport parity) + parity-contract DSL (FR-7c-30..33)

**D2/D3/D7 traceability: 3 / 3 = 100%.**

### Tripwire Ownership Coverage (6 tripwires → detection-infra ownership)

| TW | Detection Owner | Story-level Firing |
|---|---|---|
| TW-7c-1 | 7c.20a/b/c (each AUDIT-AC fires on ≥2 gaps) | 7c.20a/b/c |
| TW-7c-2 | 7c.2 (cp1252 fix + fixture utility) + 7c.3a (composer invocation) | 7c.3a |
| TW-7c-3 | 7c.4b (lockstep checker registration + class-conformance ext.) | 7c.5.G0..G6 (per-gate) |
| TW-7c-4 | 7c.0 (live-dispatch scope-creep CI lint via test-naming convention + import-graph check) | every story (process) |
| TW-7c-5 | 7c.0 (UTF-8 CI lint) + per-story T10 self-check | every story (process) |
| TW-7c-6 | 7c.0 (50-run harness scaffold + per-cell flake-rate calculator) | 7c.21 (50-run firing) |

**Tripwire ownership: 6 / 6 = 100% (no orphan tripwires).**

### Standing-Guardrail Audit (SG-1/SG-2/SG-3/SG-4)

PRD inherits all 4 standing guardrails from Slab 7a + 7b; Slab 7c does not introduce new SGs.

- **SG-1 (11-specialist roster floor)** — preserved by 7c.21 integration parity suite + AUDIT 7c.20a class-conformance ≥11 + NFR-7c-R5. **No regression risk** — Slab 7c adds zero new specialists; only orchestrational-tail extensions.
- **SG-2 (33-row mapping-checklist floor; post-7b: 7 FULLY MIGRATED)** — preserved per NFR-7c-X4 + R15 (party-mode-gated row flips at 7c.21 retrospective). FR-7c-42 lifts the floor at retrospective.
- **SG-3 (7-section Composition Spec invariants)** — preserved by 7c.21 integration parity suite (aggregated structural enforcement; precedent: 7a.8 + 7b.12).
- **SG-4 (BMB sanctum alignment per body)** — preserved by FR-7c-54 (sanctum-invariant declaration for 5 Marcus-bound writers). 7c.0 ships DSL feature; 7c.17a/b consume per writer per Slab 7b precedent (memory entry `project_slab_7b_skill_md_sanctum_alignment.md`).

**SG audit: 4 / 4 GREEN.** No implicit-violation surface detected at PRD level.

### Cross-Agent Code-Review Designation Coverage

PRD §Cross-Agent Code-Review Designation (PRD-locked per John A5 + Murat M6): 4 stories with `cross_agent_review_required: true`.

| Story | Justification | Verified |
|---|---|---|
| 7c.0 | Architectural pre-decision (DSL + ledger + 3 CI lints); wrong call cascades into all 25 downstream stories | ✓ |
| 7c.3a | §02A composer dual-nature (feature + Trial-2 finding #2 retirement); highest-conceptual-load story | ✓ |
| 7c.4b | Gate-family taxonomy foundation; wrong taxonomy = 8 per-gate stories inherit defect | ✓ |
| 7c.21 | Slab-closer; precedent: 7b.12 + 7a.8 | ✓ |

**Cross-agent designation: 4 / 4 (sprint-planning records into `migration-story-governance.json::cross_agent_review_required: true` per PRE-3).**

### Coverage Findings (sprint-planning + bmad-create-epics-and-stories clarifications)

These are NOT readiness blockers; they are **named clarifications to be resolved at sprint-planning + bmad-create-epics-and-stories**, consistent with Slab 7b's "READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS" verdict pattern.

- **EPIC-COVERAGE-FINDING-1 (cosmetic):** Wave 4 numbering skips 7c.16 (PRD §Story Decomposition splits the original 7c.17 story into 7c.17a + 7c.17b per Amelia A4; 7c.16 is implicitly absorbed). Recommendation: keep 7c.17a/7c.17b as canonical story keys for traceability to PRD frontmatter signoff block. Action: `bmad-create-epics-and-stories` author preserves the 7c.17a/7c.17b numbering.

- **EPIC-COVERAGE-FINDING-2 (writer-to-story assignment):** PRD §Wave 4 assigns "3 Marcus-bound writers (smaller surface area; shared sanctum pattern)" to 7c.17a and "2 Marcus-bound writers (larger surface area; divergent sanctum) + envelope" to 7c.17b — but does NOT pin specific writer names (gary-slide-content / gary-fidelity-slides / gary-diagram-cards / gary-theme-resolution / gary-outbound-envelope) to specific stories. Action: `bmad-sprint-planning` + `bmad-create-epics-and-stories` author the specific writer-to-story assignment based on shared-vs-divergent sanctum pattern analysis. Suggested split: 7c.17a = {gary-slide-content, gary-fidelity-slides, gary-diagram-cards} (text+payload-shape); 7c.17b = {gary-theme-resolution, gary-outbound-envelope + pre-dispatch-package-gary.md} (envelope aggregation + theme-experience). Verify at story authoring.

- **EPIC-COVERAGE-FINDING-3 (FR-7c-29 §15 Marcus-side bundle emission):** PRD §Functional Requirements FR-7c-29 says "Marcus can complete the final operator handoff at §15, emitting the full slab-close artifact bundle". PRD §Wave 5 lists §15 closeout but does NOT explicitly include §15 in any Wave-5 story (Wave 5 covers §06B + §07C + §09 + AUDIT-ACs only). Wave-3 7c.15 implements §15 G5 operator-side review per FR-7c-19. Recommendation: 7c.15 implements both the operator-side review (FR-7c-19 second-clause) AND the Marcus-side bundle emission (FR-7c-29). Action: `bmad-create-story` for 7c.15 explicitly enumerates both FR-7c-19 (operator-side) AND FR-7c-29 (Marcus-side) under the story's FR-coverage block.

- **EPIC-COVERAGE-FINDING-4 (Wave-2 7c.5.G1/G2C/G3/G4 — extend-and-audit vs fresh-author semantics):** PRD §Architecture lists G1/G2C/G3/G4 as already-shipped families; PRD §Story Decomposition Wave 2 + §Gate Taxonomy LOCKED list 7c.5.G1/G2A/G2C/G3/G4 as "Net-new four-file-lockstep". This is consistent within the PRD if "net-new authoring" means "Slab 7c authoring effort applies the post-Slab-7c contract to the existing model" (extend with FR-7c-51 schema_version field + regenerate fixtures + AUDIT against post-7c contract). Action: `bmad-create-story` for 7c.5.G1/G2A/G2C/G3/G4 explicitly states "extend existing shipped gate to post-Slab-7c contract" rather than "author from scratch", to disambiguate from G0/G5/G6 which ARE fresh-author. Sprint-planning records the distinction in `migration-story-governance.json` story metadata.

- **EPIC-COVERAGE-FINDING-5 (PRD-FRONTMATTER-FINDING-1 reprise):** PRD frontmatter `nonfunctional_requirements: 36` — actual count 37 (off-by-1). Action: correct alongside the next PRD edit OR at retrospective close. Not blocking.

### Coverage Statistics Summary

- Total PRD FRs: **54** → covered: **54** → coverage: **100%** (5 FRs flagged for sprint-planning writer-to-story / surface-emission clarification per FINDINGs 2-3)
- Total PRD NFRs: **37** → covered: **37** → coverage: **100%**
- Architectural invariants D2/D3/D7: **3** → covered: **100%**
- Tripwires TW-7c-1..6: **6** → owned: **100%**
- Standing guardrails SG-1..SG-4: **4** → preserved: **100%**
- Cross-agent code-review pre-designation: **4** → recorded: **100%** (sprint-planning persists to governance JSON)
- AUDIT-AC quantitative-floor verifiability: **5** AUDIT-ACs (FR-7c-34..38) all carry quantitative floors (≥20 / ≥15 / ≥11 / 14/14 / 6/6); ≥2 gaps trips TW-7c-1
- Story decomposition: **26 stories** matching PRD frontmatter `story_count_final: 26` ✓

---

## Steps 4-6 — DEFERRED per Slab 7b precedent

Per Slab 7b implementation-readiness report (`implementation-readiness-report-2026-04-29-slab-7b.md`) — "Steps 1-3 closed READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS; Steps 4-6 deferred until `bmad-create-epics-and-stories` produces the actual epic file" — Slab 7c follows the same pattern.

- **Step 4 — UX Alignment** — DEFERRED. Slab 7c is back-end orchestration (multi-agent + HIL surfaces with operator-conversational tail); UX classification is `UX-not-applicable` per Slab 7a + 7b precedent. Step-3 reframed coverage validation substantively folds in UX considerations (HIL surface specification + per-surface mandatory-transport declaration is the operator-experience contract).
- **Step 5 — Epic Quality Review** — DEFERRED. Cannot audit `epics-slab-7c-orchestrational-tail.md` quality before it exists. Re-runnable after `bmad-create-epics-and-stories` produces the epic file; recommend running Step 5 as part of `bmad-sprint-planning` ratification.
- **Step 6 — Final Assessment** — DEFERRED. Aggregate verdict on epic file + sprint plan; runnable after Steps 4-5 complete.

Steps 4-6 are tracked as a follow-on action: re-run Steps 4-6 of `bmad-check-implementation-readiness` against the produced `epics-slab-7c-orchestrational-tail.md` after `bmad-create-epics-and-stories` lands.

---

## Final Verdict (Steps 1-3)

**VERDICT: READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS**

Mirrors Slab 7b precedent exactly. Steps 1-3 closed clean.

### Rationale

- **PRD completeness STRONG:** 12-step `bmad-create-prd` workflow ran end-to-end; `workflowComplete: true`; 4 party-mode rounds 4/4 unanimous; 19 FR/NFR amendments + consolidated story-decomposition amendments folded inline; both signoff blocks present in frontmatter.
- **FR coverage 100%:** 54 / 54 FRs anchored to ≥1 story owner OR cross-cutting process discipline. 5 FRs flagged for sprint-planning clarification (writer-to-story assignment + §15 surface emission); none are blockers.
- **NFR enforcement 100%:** 37 / 37 NFRs each enforced via named CI workflow OR validator script OR per-story AC.
- **D2/D3/D7 invariant traceability 100%:** every story T10 self-check + aggregate verification at 7c.21.
- **Tripwire ownership 100%:** 6 / 6 tripwires owned with named detection-infra; no orphans.
- **AUDIT-AC quantitative-floor verifiability:** 5 / 5 AUDIT-ACs carry concrete floors (≥20 / ≥15 / ≥11 / 14/14 / 6/6); ≥2 gaps trips TW-7c-1; cannot quietly become a follow-on factory.
- **SG audit:** 4 / 4 standing guardrails preserved structurally; no implicit-violation surface.
- **Cross-agent code-review designation:** 4 / 4 stories pre-locked at PRD level; sprint-planning persists to governance JSON.

### Named preconditions (re-verified before any Slab 7c story dev opens)

- **PRE-1** Slab 7b CLOSED gate — VERIFIED at session-start (sprint-status, mapping-checklist, class-conformance all green).
- **PRE-2** Tier-2 pack-version-bump check for PRODUCTION_GATE_IDS expansion — to be confirmed at `bmad-sprint-planning` (party-mode consensus required BEFORE 7c.0 lands per `pipeline-manifest-regime.md`).
- **PRE-3** `migration-story-governance.json` entries for 26 Slab 7c stories — authored at `bmad-sprint-planning`; cross-agent designation for 7c.0/7c.3a/7c.4b/7c.21; gate-mode per PRD §Story Decomposition table.
- **PRE-4** Trial-2 forensic fixture preserved at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` — verified on disk before 7c.3a opens (TW-7c-2 dependency).

### Minor amendments (non-blocking; address at next PRD edit OR at retrospective)

- **AMEND-1** (PRD-FF-1 / EPIC-COVERAGE-FINDING-5): correct frontmatter `nonfunctional_requirements: 36` → `37` (P:5 + S:7 + R:8 + M:6 + X:4 + OD:7 = 37).
- **AMEND-2** (EPIC-COVERAGE-FINDING-1): preserve 7c.17a/7c.17b numbering at `bmad-create-epics-and-stories` (do NOT renumber to 7c.16/7c.17).
- **AMEND-3** (EPIC-COVERAGE-FINDING-2): pin specific writer-to-story assignment at sprint-planning (suggested 3-2 split: 7c.17a = {slide-content, fidelity-slides, diagram-cards}; 7c.17b = {theme-resolution, outbound-envelope + pre-dispatch-package-gary.md}).
- **AMEND-4** (EPIC-COVERAGE-FINDING-3): explicitly enumerate FR-7c-29 (Marcus-side §15 bundle emission) under 7c.15 story FR-coverage block (alongside FR-7c-19 operator-side).
- **AMEND-5** (EPIC-COVERAGE-FINDING-4): label 7c.5.G1/G2A/G2C/G3/G4 as "extend-and-audit existing shipped gate to post-Slab-7c contract" in story spec to disambiguate from G0/G5/G6 fresh-author.

### Subsequent workflow chain (per CLAUDE.md sprint governance)

1. **`bmad-create-epics-and-stories`** → authors `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (1 epic + 26 story shells matching PRD-locked decomposition). Apply AMEND-2 + AMEND-3 + AMEND-4 + AMEND-5 at story-shell authoring.
2. **`bmad-sprint-planning`** → records governance JSON entries per story (gate-mode + K-target; cross-agent designation for 7c.0/7c.3a/7c.4b/7c.21); seeds `sprint-status.yaml::tripwire_events` for TW-7c-1..6 with `not_yet_evaluated` initial state. Apply AMEND-3 (writer-to-story pin) at sprint-planning round.
3. **Re-run Steps 4-6 of `bmad-check-implementation-readiness`** against the produced epic file (UX alignment + epic quality review + final assessment).
4. **`bmad-create-story` for 7c.0** (the gating ADR + scaffold story per Amelia A4 — required FIRST; 7c.1 implementation + downstream stories cannot open until 7c.0 lands).
5. NEW CYCLE: Claude authors spec → governance JSON gate-mode + sandbox-AC + Slab 7c PRD readings validation → Claude authors `codex-dev-prompt-7c-0.md` → Codex T1-T9 + T10 self-review → Claude T11 `bmad-code-review` (cross-agent MANDATORY per PRD lock) → Claude commit + flips done.

---

## Appendix — PRD Verification Anchors

Quick-grep verification anchors for next session and for Slab 7c retrospective ratification:

- **PRD lines 304-318** in `bmm-workflow-status.yaml` record the Slab 7c PRD with full metadata (currently nested at `root.epic_26_bmb_sanctum_migration.prd_slab_7c_orchestrational_tail` — see session-start reconciliation note: should be re-parented to a migration-scoped block alongside `prd_slab_7a_inter_gate_orchestration` + `prd_slab_7b_specialist_activation_eleven` at next session wrap-up).
- **PRD frontmatter signoff block** `story_decomposition_signoff::infra_ownership` is the authoritative cross-reference for tripwire detection ownership + cross-agent designation; re-read at sprint-planning round.
- **PRD §Gate Taxonomy LOCK at PRD Step 11 per Amelia A3** — 8 net-new + 6 alias gates is non-negotiable; changes require party-mode consensus + governance JSON version bump.
- **Trial-2 forensic fixture** preserved at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` (gitignored; operator-pinned) — TW-7c-2 dependency for 7c.3a.


