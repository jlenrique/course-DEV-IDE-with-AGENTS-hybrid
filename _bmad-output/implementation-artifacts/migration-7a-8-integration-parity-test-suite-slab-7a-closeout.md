# Migration Story 7a.8: Integration + Parity-Test Suite + Slab 7a Closeout

**Status:** ready-for-dev
**Sprint key:** `migration-7a-8-integration-parity-test-suite-slab-7a-closeout`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 4
**Gate:** **dual-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-8; rationale: `operator_acceptance_gate + invariant_preservation`; FLIPPED from single-gate per Step 1 batch-approved adjustment — integration story; cross-story failure modes justify conservative review)
**K-target:** ~1.6× (gate-shape band 1.8-2.2K; ~3K target)
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 5 — slot 2 (strict-last; parallel start with 7a.7).
**FR coverage:** 17 FR-line + NFR-CG block + NFR-I8 — FR25, FR26, FR27, FR28, FR36, FR37; FR-A21, FR-A22, FR-A24; FR-O9, FR-O13, FR-O14, FR-O15, FR-O16, FR-O23, FR-O24, FR-O25; NFR-CG1-CG11 (block); NFR-I8
**Standing-guardrail enforcement:**
- **SG-1 AGGREGATED assertion HERE** — parity suite asserts `len(roster) == 11` + name-set equality.
- **SG-2 AGGREGATED assertion HERE** — parity suite enumerates 33 tests (per operator-ratified amendment 2026-04-29); row-count CI assertion blocks merge.
- **SG-3 AGGREGATED assertion HERE** — Composition Spec invariant test suite enforces all 7 sections (§3.1, §3.5, §3.6, §6, §9, §10, §11).

**Implementation cycle (NEW):** Claude spec → Codex dev+tests → Claude review+commit. **DUAL-GATE — operator-witnessed Gate-2 evidence ceremony required at T10/T11 boundary** (T-task list reflects).

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- All 7 prior Slab 7a stories MUST be `done` before 7a.8 dev opens (strict prereq):
  - 7a.1 (directive-composer) — DONE 2026-04-29
  - 7a.2 (manifest fold-flags + compiler ext) — DONE 2026-04-29
  - 7a.6 (vocabulary registry + parity-table) — pending Codex dev
  - 7a.3 (pre-gate-marcus shared LLM node) — pending Codex dev
  - 7a.4 (per-slide subgraph + HTML review-pack skeleton) — pending Codex dev
  - 7a.5 (conversation persistence + specialist-summary writer) — pending Codex dev
  - 7a.7 (A2 single-decision shims) — pending Codex dev
- 7a.8 is the strict-last Slab 7a story. Trial-2 readiness predicate (BS-2) green at 7a.8 close.

**Live substrate (verified at authoring; updates as prior stories close):**
- 7a.1: directive-composer + runner_supplied_payload + Composition Smoke pattern.
- 7a.2: production_gate_ids(manifest) + GateBypassError + orchestration-only-node lockstep tolerance + manifest fold-flag annotations.
- 7a.6: vocabulary registry + 11-roster `SpecialistId` enum + 33-row parity-test suite scaffolds.
- 7a.3: pre-gate-marcus invocation + Jinja2 templates.
- 7a.4: per-slide subgraph + HTML review-pack + max-3 oscillation guard + OperatorVerdict.revise_count.
- 7a.5: conversation persistence + SHA256 chain + specialist-summary writer + run_summary.yaml emit.
- 7a.7: A2 shims for terminal gates + OPERATOR/INPUTS/OUTPUTS/REFERENCE help-text.

**Block-mode trigger paths touched by this story:** none (7a.8 wires substrate together; no manifest/lockstep change).

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-5 strict-last (FLIPPED from single-gate to dual-gate per Step 1 batch-approved adjustment — integration story; cross-story failure modes justify conservative review). Integration + parity-test suite (33-row mapping checklist 1:1) + Composition Spec invariant test suite (NFR-I8) + calibration-tripwire wiring + gate-bypass detection + max-3 oscillation guard + engagement-decay reporting + Slab 7a closeout artifacts. SG-1 + SG-2 + SG-3 aggregated structural enforcement here. Operator acceptance for trial-2 readiness predicate.

**T1 conclusion:** Implementation proceeds AFTER all 7 prior Slab 7a stories close. Hard checkpoint at T1: confirm ALL 7 prior stories are `done` in BOTH spec status + sprint-status.yaml.

---

## Story

As the operator + the substrate-completeness gate,
I want a parity-test suite at `tests/parity/` mirroring the 33-row mapping checklist (one test per legacy operator-control lever), Composition Spec invariant test suite at `tests/parity/test_composition_spec_invariants.py`, calibration-tripwire substrate behavior wired into the gate-runner, gate-bypass detection hook, max-3 oscillation guard as state-machine invariant, engagement-decay reporting, sandbox-AC validator pass on every Slab 7a story, and Slab 7a closeout artifacts (sprint-status update, deferred-inventory entries, retrospective evidence),
so that all seven scope-binding commitments (Subgraph-with-`interrupt()` / Max-3 / Frozen 10-gate inventory / Pre-composition QA validator / Decision-card vocabulary registry / C1 calibration-tripwire / Parity-test suite) are landed and tested, and trial-2 closes through G3 cleanly with all 11 specialists active.

---

## Acceptance Criteria

### AC-7.8-A — Parity-test suite mirrors 33-row mapping checklist (FR34, FR35, FR-O20, NFR-I6, SG-2 aggregated)

**Given** the 33-row mapping checklist
**When** the parity-test suite at `tests/parity/test_mapping_checklist_row_NN.py` is executed (one file per row OR consolidated per-row test functions in a single file — operator-decision)
**Then** the suite enumerates 33 tests; each test header declares `REFERENCES_FRS = [...]` + `MAPPING_CHECKLIST_ROW = NN`.
**And** CI fails if any row lacks a test, any referenced FR is unimplemented, or any referenced FR lacks a passing unit test.

### AC-7.8-B — Composition Spec invariant test suite (FR-O22, NFR-I8, SG-3 aggregated)

**Given** the Composition Spec invariant test suite at `tests/parity/test_composition_spec_invariants.py`
**When** CI runs
**Then** all SEVEN Composition Spec invariant sections are tested:
- §3.1 envelope append-only + SHA256.
- §3.5 gate precedence (per-specialist non-blocking by default).
- §3.6 manifest-declared dependencies.
- §6 chain-test-per-PR.
- §9 Composition Smoke gate at slab-opener.
- §10 Decision Log entries present for substrate-shape evolutions.
- §11 migration triggers tracked.

### AC-7.8-C — Calibration-tripwire substrate (FR-A22, FR-O23, FR-O24, NFR-OT1, NFR-OT4)

**Given** the calibration-tripwire substrate at `app/marcus/orchestrator/gate_runner.py` (or shared substrate module)
**When** the operator-override-rate at any gate exceeds threshold over rolling N-run window
**Then** batch-approve auto-locks at the affected gate for the next 3 trials; tripwire log records BOTH fire and quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl`; FM-5 inverse — silence is not assumed healthy; quiet must be witnessed.

**Given** synthetic tripwire trip during dev
**When** 7a.8 executes the synthetic-disagreement injection fixture
**Then** the tripwire fires on ≥3-axis disagreement, stays quiet on consensus; ≥1 fire + ≥1 quiet captured in trial-2.

### AC-7.8-D — Gate-bypass detection hook (FR-A23, FR27, NFR-OC5)

**Given** the gate-bypass detection hook
**When** the runner attempts a transition that skips a declared gate_code
**Then** the runner refuses (already implemented in 7a.2's `GateBypassError`; 7a.8 ADDS a CI test that verifies trial-2's `_artifacts/trial-2/run_summary.yaml::silent_bypass_events == 0`).

### AC-7.8-E — Engagement-decay report (FR-O14, FR-O15, NFR-OX1, NFR-OT3)

**Given** the engagement-decay report generator
**When** trial-2 closes
**Then** `_artifacts/trial-2/engagement_decay_report.md` is auto-generated reporting first-quartile rate, last-quartile rate, ratio, pass/fail.
**And** SM-4 threshold (last-quartile ratio ≥ 0.30 × first-quartile) breach triggers C1 calibration-tripwire.

### AC-7.8-F — Max-3 oscillation guard as state-machine invariant (FR-A21, FR-O9, NFR-R4, NFR-OC4)

**Given** the gate-runner shared substrate
**When** any gate executes
**Then** max-3 oscillation guard is implemented as state-machine invariant (already landed in 7a.4's `OperatorVerdict.revise_count` extension; 7a.8 ADDS a CI test that verifies the invariant is enforced across ALL gates, not just per-gate hand-rolling).

### AC-7.8-G — Marcus-duality boundary (FR-A24, NFR-CG9)

**Given** the Marcus-duality boundary
**When** the dispatch adapter executes any Marcus-touching transition
**Then** orchestrator-mode state never mixes with operator-handoff state; runtime-asserted boundary; reviewer confirms in code review.

### AC-7.8-H — Sandbox-AC validator + BMAD sprint governance + deferred-inventory + four-file-lockstep + K-floor + gate-mode + pre-commit + anti-pattern + Composition Smoke (NFR-CG1-CG11)

**The full NFR-CG block is structurally enforced by aggregating prior-story checks at 7a.8 close:**
- **NFR-CG1:** sandbox-AC validator returns zero warnings on EVERY Slab 7a story file (re-run at close).
- **NFR-CG2:** Composition Smoke gate at slab-opener (7a.1 evidence) referenced.
- **NFR-CG3:** N1-N12 substrate-inventory checklist trace per Slab 7a story.
- **NFR-CG4:** four-file-lockstep on every Pydantic touch (7a.1/7a.4/7a.5/7a.6 each with their own four-file artifacts).
- **NFR-CG5:** K-floor / target-range discipline; over-spend tripwire fires across all 8 stories.
- **NFR-CG6:** gate-mode designations from frozen `migration-story-governance.json` v2026-04-28-slab7a-eight-stories.
- **NFR-CG7:** pre-commit stack (ruff + orphan-detector + co-commit-invariant) green; no `--no-verify` bypass.
- **NFR-CG8:** anti-pattern catalog (A12, A17, P3) explicitly cited in code-review checklists.
- **NFR-CG9:** Marcus-duality boundary (AC-G).
- **NFR-CG10:** BMAD sprint governance compliance (`bmad-create-prd → bmad-party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story → bmad-code-review`); under NEW cycle: Claude spec → Codex dev → Claude review.
- **NFR-CG11:** deferred-inventory governance (every named-but-not-filed follow-on lands in deferred-inventory.md).

**Test pin:** `tests/parity/test_nfr_cg_block_aggregated.py` — 11 cases (one per NFR-CG); each asserts the relevant artifact exists + meets the criterion.

### AC-7.8-I — Trial-2 readiness predicate (BS-2; A-1..A-7)

**Given** the trial-2 readiness predicate
**When** all 8 Slab 7a stories close + Slab 7b activations complete (trial-2 readiness is BS-2 from the PRD; A-1..A-7 are the seven acceptance clauses)
**Then** trial-2 is launchable against Slab 7a substrate without further code changes; all 7 acceptance clauses A-1..A-7 from PRD §Success Criteria green at 7a.8 close.

### AC-7.8-J — Closeout deliverables (post-AC; D12 close protocol)

At close:
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: Slab 7a stories all closed; Slab 7b queued.
- Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`: Slab 7a PRD entry done; Slab 7a epic entry done.
- Update `next-session-start-here.md`: immediate-next-action = Slab 7b PRD authoring OR trial-2 dry-run.
- Update `_bmad-output/planning-artifacts/deferred-inventory.md`: Slab 7a-named follow-ons filed (Doc-7-D harvest items, structural polish-pass deferrals, sanctum-reference-conventions verification).
- Author Slab 7a retrospective per `bmad-retrospective` skill.

### AC-7.8-K — Golden-trace fixtures from trial-2 (NFR-T4)

**Given** golden-trace fixtures
**When** trial-2 has run by 7a.8 close
**Then** record-once-replay-forever fixtures are committed under `_bmad-output/trial-fixtures/<trial-2-id>/`; quarterly re-record cadence calendar-tracked (operator-gated).
**OR** IF trial-2 hasn't run by 7a.8 close, fixtures land in Slab 7b kickoff (Slab 7b inherits as input, does NOT block on them) per Murat's Step 1 finding.

### AC-7.8-L — N-item / anti-pattern / Composition Spec trace + dual-gate Gate-2 evidence

**N-item / Composition Spec / anti-pattern trace:** all 11 NFR-CG (per AC-H) + NFR-I8 (per AC-B) + 17 FR-line entries cross-reference checked.

**Operator-witnessed dual-gate Gate-2 evidence ceremony (T10):** operator runs the full focused + wider regression battery + sandbox-AC + lockstep + ruff + lint-imports + Composition Smoke; pastes verbatim stdout into Completion Notes. Operator also runs trial-2 (or trial-2 dry-run) and pastes the trial-2 close artifact paths into Completion Notes.

---

## Tasks / Subtasks

- [ ] **T1: Readiness review (Codex)** — confirm ALL 7 prior Slab 7a stories `done` in BOTH spec status + sprint-status.yaml.
- [ ] **T2: Parity-test suite mirrors 33-row checklist** (AC-A) — author OR populate (depending on 7a.6's parity-test scaffold approach) one test per row with REFERENCES_FRS + MAPPING_CHECKLIST_ROW headers.
- [ ] **T3: Composition Spec invariant test suite** (AC-B) — `tests/parity/test_composition_spec_invariants.py` covering all 7 sections.
- [ ] **T4: Calibration-tripwire substrate** (AC-C) — wire into `app/marcus/orchestrator/gate_runner.py` (extend or create); synthetic-disagreement injection fixture.
- [ ] **T5: Gate-bypass detection CI test** (AC-D) — leverages 7a.2's `GateBypassError`; CI test verifies `silent_bypass_events == 0`.
- [ ] **T6: Engagement-decay report generator** (AC-E) — auto-emit at trial close; SM-4 threshold check.
- [ ] **T7: Max-3 oscillation guard CI test** (AC-F) — leverages 7a.4's revise_count; CI test verifies invariant across ALL gates.
- [ ] **T8: Marcus-duality boundary runtime assertion** (AC-G) — runtime-asserted boundary in dispatch adapter; reviewer confirmation in code-review.
- [ ] **T9: NFR-CG block aggregated test** (AC-H) — `tests/parity/test_nfr_cg_block_aggregated.py` with 11 cases.
- [ ] **T10: Verification battery + DUAL-GATE Gate-2 operator ceremony** (AC-L) — operator runs full battery + trial-2 (or dry-run); pastes verbatim stdout.
- [ ] **T11: Codex G6 self-review** (Blind / Edge / Auditor).
- [ ] **T12: Claude bmad-code-review + remediation + commit + Slab 7a CLOSEOUT** (AC-J + K) — D12 close protocol + retrospective + golden-trace fixtures (or defer to Slab 7b kickoff if trial-2 not run).

---

## File Structure Requirements

**New:** `tests/parity/test_mapping_checklist_row_NN.py` (or 33 individual files) per AC-A; `tests/parity/test_composition_spec_invariants.py` per AC-B; `tests/parity/test_nfr_cg_block_aggregated.py` per AC-H; `tests/integration/marcus/test_calibration_tripwire.py`, `tests/integration/marcus/test_engagement_decay_report.py`, `tests/integration/marcus/test_marcus_duality_boundary.py`; `_bmad-output/implementation-artifacts/slab-7a-retrospective.md`; `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/orchestrator/gate_runner.py` (extend or create for tripwire + duality assertion) — additive; `_bmad-output/implementation-artifacts/sprint-status.yaml` + `bmm-workflow-status.yaml` + `next-session-start-here.md` + `deferred-inventory.md` per AC-J close protocol.

**Do NOT modify:** specialist bodies; 7a.1-7a.7 surfaces (only consume); manifest; v4.2 prompt pack.

---

## Testing Requirements

**K-floor 14 + K-target ~26 (per gate-shape band 1.8-2.2K + ~3K target):**
- 33 parity-test functions per row (AC-A; many @pytest.mark.skip placeholders awaiting Slab 7b activations)
- 7 Composition Spec invariant cases (AC-B)
- 4 calibration-tripwire cases (AC-C)
- 1 gate-bypass detection (AC-D)
- 3 engagement-decay cases (AC-E)
- 1 max-3 oscillation invariant (AC-F)
- 2 Marcus-duality cases (AC-G)
- 11 NFR-CG block cases (AC-H)

**K-tripwire (BINDING per dual-gate):** 1.7× target (~5.1K LOC OR ~44 active tests excluding skipped placeholders) → close round + party-mode triage.

---

## Dev Notes

**Architecture compliance:** ALL Composition Spec invariants honored (§3.1/§3.5/§3.6/§6/§9/§10/§11); §11 trigger NEGATIVE for 7a.8 itself (additive parity tests; aggregating substrate built by prior 7 stories); §10 entries from 7a.1 (`runner_supplied_payload`) + 7a.2 (fold-flag schema extension) referenced.

**Library/framework:** stdlib + PyYAML + Pydantic v2. NO new third-party deps.

**Anti-patterns to avoid:** A12, A17, P3 (NFR-CG8 explicit catalog citation); A11 Windows-portability throughout.

**Previous story intelligence:** 7a.1-7a.7 substrate is the input; 7a.8 wires it together + adds the parity test suite that proves the 33-row floor is honored.

**References:** Epic Story 1.8; PRD §FR25-28, FR36, FR37 + §FR-A21, A22, A24 + §FR-O9, O13-16, O23-25 + §NFR-CG1-CG11 + §NFR-I8; governance JSON `7a-8`; ALL prior Slab 7a stories; CLAUDE.md governance.

---

## Dev Agent Record

(populate at dev-open)
