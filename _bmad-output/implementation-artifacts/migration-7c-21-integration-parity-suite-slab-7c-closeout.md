# Migration Story 7c.21: Slab 7c Integration Parity Suite + Closeout Ceremony (FR-7c-39..43 + FR-7c-47 + FR-7c-51)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=3 per governance JSON; 28 prerequisites all DONE — story fully unblocked at this commit. AUDIT-AC trio CLEAN — TW-7c-1 not_fired @ 1.35% combined gap rate; substrate verified at floors with substantial headroom; Wave 6 closeout unblocked.)*
**Sprint key:** `migration-7c-21-integration-parity-suite-slab-7c-closeout`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 4
**K-target:** 1.4×
**Estimated LOC:** ~1.2K (Trial3Transcript Pydantic-v2 + JSON schema ~200 + 50-run firing wrapper script ~150 + R7a/R7b Trial-3 readiness verification harness ~250 + D12 close-protocol AUDIT ~150 + SG-aggregate AUDIT ~150 + retrospective-evidence-pack generator ~200 + 5 test files ~400; doc-edits to migration-guide + anti-pattern catalog + deferred-inventory + parent migration epics file via D12 protocol)
**Gate-mode:** dual-gate (operator_acceptance_gate + invariant_preservation per governance JSON)
**Cross-agent review:** **MANDATORY** (per governance JSON `cross_agent_review_required: true`; aligns with 7a.8 + 7b.12 strict-last precedent)
**R-tier:** R3
**T11-tier:** **cross-agent** (per governance JSON entry `7c-21`; deepest review tier)
**Lookahead-tier:** 3
**files_touched:** ~6 new + ~4 modified
**Tripwire ownership:** TW-7c-6 (parity flake; 50-run zero-flake firing baseline)
**Stop-on-tripwire-fire:** TW-7c-6 hard-binding per AMEND-7d-iii (Murat); STOP; do NOT proceed to retrospective; escalate to party-mode for parity-budget mitigation

---

## Story

As the operator,
I want one slab-closing ceremony story that fires the TW-7c-6 50-run zero-flake parity baseline + lands FR-7c-51 schema_version + Trial3Transcript schema + records Trial-3 readiness AC + aggregates SG-1+SG-2+SG-3+SG-4 enforcement evidence + prepares the Slab 7c retrospective evidence pack + closes deferred-inventory entries,
So that Slab 7c reaches done with full structural enforcement + Trial-3 unblocked.

This is the **Wave 6 strict-last ceremony** (per governance JSON: dual-gate cross-agent MANDATORY; lookahead_tier=3 deepest; STOP-on-TW-7c-6-fire branch per AMEND-7d-iii). It carries 4 pts at K=1.4× and aggregates SG-1+SG-2+SG-3+SG-4 structural enforcement (precedent: 7a.8 + 7b.12).

---

## Scope carve-out: dev-agent vs operator-driven Gate-2

The 7c.21 epic-level AC text (line 935 of `epics-slab-7c-orchestrational-tail.md`) reads *"the dev-agent triggers `bmad-retrospective`"*. This wording is a **spec defect**: `bmad-retrospective` is a facilitator-driven multi-agent workflow that requires operator + party-mode participation; it is NOT executable under `bmad-dev-story` discipline. This spec corrects the carve-out:

**Dev-agent scope (Codex bmad-dev-story):**
1. Fire TW-7c-6 50-run zero-flake parity baseline (consumes 7c.0b harness)
2. Land Trial3Transcript Pydantic-v2 schema + JSON-Schema regen + shape-pin
3. Verify NFR-7c-R7a + R7b Trial-3 readiness preconditions (existence + operational checks)
4. Verify D12 cross-slab governance protocol three-line set (per architecture decision D12)
5. AUDIT SG-1+SG-2+SG-3+SG-4 structural enforcement at slab-close
6. Prepare retrospective evidence pack at `_bmad-output/implementation-artifacts/slab-7c-retrospective-evidence-pack.md` (markdown summary; consumed by operator at Gate-2)
7. Verify deferred-inventory closures (`slab-7c-live-harness-evidence` not yet closeable; `trial-2-finding-1` + `trial-2-finding-2` already CLOSED-BY 7c.2 + 7c.3a — verification only)
8. D12 close-protocol three-line set: invariant-preservation note + anti-pattern harvest + migration-guide §-update for Slab 7c

**Operator-driven Gate-2 scope (NOT dev-agent; runs separately at slab-close ceremony):**
- Trigger `bmad-retrospective` via the BMAD facilitator workflow
- Mapping-checklist row-status flips per R15 / FR-7c-42 (party-mode-ratified; per `slab-7b-mapping-checklist-row-status-update` deferred-inventory entry — dev-agent path is structurally NOT authorized)
- Per-tripwire firing-rate review per FR-7c-41

The dev-agent's retrospective evidence pack (item 6 above) is the operator's reading material for the Gate-2 retrospective; row-flips happen there, not in the dev-agent diff.

---

## Predecessor / Dependency Context

- **28 prerequisite stories** (per governance JSON; ALL DONE 2026-05-06): 7c.1 + 7c.3a + 7c.3b + 7c.4b + 7c.5.G0..G6 + 7c.6..7c.15 + 7c.17a + 7c.17b + 7c.18a + 7c.18b + 7c.19 + 7c.20a + 7c.20b + 7c.20c.
- **AUDIT-AC trio outcomes (CLEAN)**: TW-7c-1 final aggregated verdict `not_fired`; combined gap rate 1.35% (1 inherited gap from 7c.20b's scanner-staleness, well below 10% per-story threshold). 7c.20c LAST-CLOSER ledger entry written at `2026-05-06T15:48:01-04:00`.
- **7c.0b deliverables (consumed)**: 50-run flake-rate calculator at `app/parity/contracts/_flake_rate.py` + harness scaffold at `scripts/utilities/detect_tw_7c_6_parity_flake.py` + audit-chain integrity at `app/audit/chain.py` + TripwireLedgerEntry at `app/models/tripwire_ledger.py`.
- **PRODUCTION_GATE_IDS** at `app/manifest/compiler.py:98` — manifest-derived `frozenset[str]` per FR-A8 (consumed for Trial3Transcript closed-enum gate-ids).
- **Mapping checklist** at `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` (33-row floor; SG-2; integrity test at `tests/parity/test_mapping_checklist_status.py`). **Row-status flips DEFERRED to Gate-2 retrospective per `slab-7b-mapping-checklist-row-status-update` deferred-inventory governance.**
- **D12 protocol** at `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D12 (line 563)` — three mandatory AC lines at slab close: (1) invariant-preservation note + (2) anti-pattern harvest + (3) migration-guide §-update.
- **Migration guide** at `docs/dev-guide/langgraph-migration-guide.md` (D12 §-update target).
- **Anti-pattern catalog** at `docs/dev-guide/specialist-anti-patterns.md` (D12 anti-pattern harvest target).
- **Trial-2 finding closures**: `trial-2-finding-1-g0-print-cp1252-crash` CLOSED-BY 7c.2; `trial-2-finding-2-directive-composer-corpus-scan-fallback` CLOSED-BY 7c.3a. Both verified-closed in `deferred-inventory.md` (lines 355-356). 7c.21 documents these closures in the retrospective evidence pack — NOT closing them anew.
- **`slab-7c-live-harness-evidence` deferred-inventory entry** (line 346): closes via 7c.21a (Wave 6 strict-last; HARD predecessor on 7c.21). 7c.21 records the entry as still-deferred → 7c.21a will close.
- **NFR-7c-R7a + R7b Trial-3 readiness** (PRD lines 1720-1725): R7a = precondition fixtures present (existence check); R7b = 120/180-min forensic-evidence harness operational. 7c.21 verifies; does NOT ship the fixtures themselves (they are pre-existing scaffolds from Slab-7a/7b body-activation).

---

## Acceptance Criteria

### AC-7c.21-A — Trial3Transcript Pydantic-v2 schema + JSON Schema regen + shape-pin (FR-7c-51)

**Given** the FR-7c-51 schema_version + Trial3Transcript schema requirement + manifest-derived `production_gate_ids` source-of-truth
**When** the dev-agent authors `app/models/trial3_transcript.py` + regenerates `app/models/trial3_transcript.v1.schema.json` + authors `tests/trial/test_trial3_transcript_shape.py`
**Then**:
1. `Trial3Transcript` Pydantic-v2 model: `model_config = ConfigDict(extra="forbid", validate_assignment=True)` + closed-enum `gate_id: GateId` Literal sourced from `production_gate_ids(manifest)` (T1-T9 decision: code-generated Literal vs runtime-derived constraint — operator/Codex picks; for closed-enum semantics, code-generated Literal is preferred).
2. Closed-enum `event_type: TrialEventType` Literal: `Literal["edit", "approve", "reject", "complete"]` per spec wording (PRD line 928).
3. Standard envelope fields: `trial_id: UUID4`, `started_at: datetime` (tz-aware UTC), `completed_at: datetime | None`, `events: list[TrialEvent]` (`min_length=1`), `schema_version: int = 1`.
4. `TrialEvent` sub-model: `event_id: UUID4`, `gate_id: GateId`, `event_type: TrialEventType`, `event_at: datetime` (tz-aware), `operator_id: str` (`min_length=1` + strip-then-non-empty), `payload_digest: str` (`pattern=r"^[0-9a-f]{64}$"`).
5. Shape-pin test asserts schema hash STABLE across regenerations (sha256 frozen literal pin per Wave-3/4/5 precedent).
6. Schema-version bump-on-change discipline: when schema hash changes, `schema_version` MUST increment per FR-7c-51 invariant.

### AC-7c.21-B — TW-7c-6 50-run zero-flake parity baseline firing (FR-7c-47 + AMEND-7d-iii)

**Given** the 7c.0b harness scaffold at `scripts/utilities/detect_tw_7c_6_parity_flake.py` + per-cell flake-rate calculator at `app/parity/contracts/_flake_rate.py` (AMEND-7a tightened budget: <0.05% for 7c-added cells; <0.1% grandfathered for pre-7c cells)
**When** the dev-agent authors `scripts/utilities/run_slab_close_50_run_parity.py` (slab-close wrapper) + invokes the 50-run firing
**Then**:
1. The parity suite runs **50 consecutive times** in CI against the full ~68-cell post-Slab-7c matrix.
2. For each cell: pass-rate computed; per-cell flake-rate = (failed_runs / total_runs).
3. AMEND-7a budget verified: 7c-added cells must have flake-rate <0.05%; pre-7c cells must have flake-rate <0.1%.
4. **TW-7c-6 firing path (binding=hard per AMEND-7d-iii)**: if ANY per-class budget is breached, TW-7c-6 (high severity) fires; tripwire-ledger entry appended to `sprint-status.yaml::tripwire_events`; **STOP — do NOT proceed to retrospective**; escalate to party-mode for parity-budget mitigation per option-c parity-contract DSL; per-surface transport declaration enforcement reviewed; ceremony resumes only after fix lands.
5. If TW-7c-6 NOT fired: AUDIT PASSES; aggregated `fired_verdict: not_fired` recorded in tripwire-ledger; ceremony continues.
6. The 50-run firing is **deterministic-execution-only-per-run** (within a single 50-run batch, runs are independent; across batches, results may differ — that's the point of measuring flake-rate).

### AC-7c.21-C — NFR-7c-R7a + R7b Trial-3 readiness AC verification (Murat M4)

**Given** the Trial-3 readiness predicates per PRD lines 930-932:
- (a) all 6 tripwire-ledger entries are queryable
- (b) R7a precondition fixtures present
- (c) R7b 120/180-min forensic-evidence harness operational
- (d) all 11 HIL surfaces emit class-conformance markers

**When** the dev-agent authors `tests/trial/test_trial3_readiness.py`
**Then** the test verifies:
1. (a) `sprint-status.yaml::tripwire_events` contains 6 named TW-7c-1..6 entries; each conforms to TripwireLedgerEntry schema; queryable via `app.audit.chain.verify_audit_chain`.
2. (b) R7a precondition fixtures present at expected paths (T1 locates exact paths under `tests/trial/` or `_bmad-output/implementation-artifacts/`; existence check only).
3. (c) R7b 120/180-min forensic-evidence harness operational (T1 locates harness; existence + minimal-invocation smoke check).
4. (d) all 11 HIL surfaces (per Slab-7b body-activation roster) emit class-conformance markers — uses `validate_parity_test_class_conformance.py` at floor 11 + dynamic discovery for the 11 specialists.
5. Test PASSES if all four readiness predicates green; FAILS hard if any predicate missing (gap-fill follow-on filed per AMEND-7c discipline; STOP if breach).

### AC-7c.21-D — D12 cross-slab governance protocol three-line AUDIT (D12 architecture decision)

**Given** D12 protocol: three mandatory AC lines at slab close per `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` Decision D12
**When** the dev-agent authors `tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py` + lands the three D12 deliverables
**Then**:
1. **(D12-1) Invariant-preservation note**: a Slab-7c invariant-preservation entry lands at `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` (or appropriate cross-reference target) listing each load-bearing invariant touched in Slab 7c with file/test references (feeds FR63 M5 audit matrix). Minimum entries: SG-1 (11-roster) + SG-2 (33-row) + SG-3 (Composition Spec invariants) + SG-4 (sanctum-alignment).
2. **(D12-2) Anti-pattern harvest entry**: per Slab-7c development, append entries to `docs/dev-guide/specialist-anti-patterns.md` (or new catalog file) for any anti-pattern encountered. Minimum at slab close: ≥1 concrete entry (e.g., A18 PowerShell BOM; cap on naive corpus-scan fallback per 7c.3a; class-definition-substring scanner staleness per 7c.13/14 precedent). NO entry-cap; entries cumulative across Slabs.
3. **(D12-3) Migration-guide §-update**: `docs/dev-guide/langgraph-migration-guide.md` is updated with a Slab 7c section documenting key learnings (orchestrational-tail patterns, parity-DSL adoption, AUDIT-AC framing, AMEND-7c percentage threshold, Wave structure, sanctum-alignment for Marcus writers, dual-FR fold (7c.15) precedent).
4. AUDIT test asserts all three D12 lines present + non-empty + content-validated (e.g., regex-match for slab-7c-specific keywords).

### AC-7c.21-E — SG-1+SG-2+SG-3+SG-4 aggregated structural enforcement AUDIT

**Given** the four standing guardrails: SG-1 (11-roster floor), SG-2 (33-row mapping-checklist floor), SG-3 (Composition Spec invariants), SG-4 (sanctum-alignment per writer)
**When** the dev-agent authors `tests/audit/test_audit_ac_sg_aggregate_enforcement.py`
**Then** the test verifies:
1. **SG-1**: 11-specialist roster floor — call `validate_parity_test_class_conformance.py` and assert ≥11 activation contracts.
2. **SG-2**: 33-row mapping-checklist floor — call `tests/parity/test_mapping_checklist_status.py::test_no_row_silently_dropped` (or analogous) and assert PASS.
3. **SG-3**: Composition Spec invariants honored — assert `Composition Spec §3.1 SHA256+append-only` is enforced on envelope writers (read existence + structural-shape check on `app/marcus/orchestrator/writers/outbound_envelope.py::GaryOutboundEnvelope`).
4. **SG-4**: sanctum-alignment registry contains ≥6 writer_ids (5 `gary-*` from 7c.17a/b + `section-15-bundle` from 7c.15) — call `iter_sanctum_alignments` + assert count ≥6.
5. AUDIT test FAILS hard if any SG fails; the failure is a Slab 7c regression that blocks closeout.

### AC-7c.21-F — Retrospective evidence pack preparation (consumed by operator at Gate-2)

**Given** the carve-out: dev-agent prepares; operator triggers `bmad-retrospective` separately at Gate-2
**When** the dev-agent authors `_bmad-output/implementation-artifacts/slab-7c-retrospective-evidence-pack.md`
**Then** the markdown evidence pack contains (operator-readable; structured for Gate-2 review):
1. **Tripwire firing-rate summary** (per FR-7c-41 retrospective deliverable input): per-tripwire firing rate across Slab 7c (TW-7c-1..6); derived from `sprint-status.yaml::tripwire_events`.
2. **Mapping-checklist row-status snapshot** (per FR-7c-42 retrospective deliverable input): current state of all 33 rows; explicit "candidates for ✅ FULLY MIGRATED flip" (~17-22 candidates per R15) — operator + party-mode ratifies row-flips at Gate-2.
3. **Deferred-inventory consultation report** (per FR-7c-43): Slab-7c-relevant entries with status (still-deferred / closed / new-this-slab); explicit closure recommendations.
4. **Slab 7c epic chronicle**: 36-story Wave-by-Wave summary (Wave 0-6); per-wave story count + close dates.
5. **Trial-3 readiness verdict**: PASS/FAIL on R7a + R7b + 11-HIL-class-conformance per AC-7c.21-C.
6. **D12 close-protocol set summary**: pointers to invariant-preservation note + anti-pattern entries + migration-guide §-update.
7. **TW-7c-6 50-run baseline result**: `not_fired` (PASS) or `fired` (BLOCK).
8. **Recommended next actions for Gate-2**: row-flip ratification + retrospective trigger + 7c.21a unblock.

The dev-agent does NOT trigger `bmad-retrospective` — that is operator-driven Gate-2 work.

### AC-7c.21-G — Deferred-inventory verifications (FR-7c-43)

**When** the dev-agent reads `_bmad-output/planning-artifacts/deferred-inventory.md`
**Then** the AUDIT verifies:
1. `slab-7c-live-harness-evidence` is still listed (NOT yet closed; closure is 7c.21a's job — strict-last cleanup).
2. `trial-2-finding-1-g0-print-cp1252-crash` shows CLOSED-BY 7c.2 (closure verified-recorded; do NOT re-close).
3. `trial-2-finding-2-directive-composer-corpus-scan-fallback` shows CLOSED-BY 7c.3a (closure verified-recorded; do NOT re-close).
4. AUDIT PASSES if all three above states match expected; ANY deviation is a regression flag.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 28 prerequisites all done in sprint-status.
  - [ ] T1.2 Confirm AUDIT-AC trio TW-7c-1 verdict at `not_fired` (read `sprint-status.yaml::tripwire_events`).
  - [ ] T1.3 Read 7c.0b's flake-rate calculator + 50-run harness scaffold; understand the wrapping interface.
  - [ ] T1.4 Read `app/manifest/compiler.py::production_gate_ids` for Trial3Transcript closed-enum source.
  - [ ] T1.5 Read mapping checklist + `tests/parity/test_mapping_checklist_status.py` for SG-2 invariant assertion.
  - [ ] T1.6 Locate R7a + R7b Trial-3 readiness fixtures (search `tests/trial/`, `_bmad-output/implementation-artifacts/`, `tests/integration/trial/`).
  - [ ] T1.7 Read D12 architecture decision + locate migration-guide + anti-pattern catalog.
  - [ ] T1.8 Refresh broad-regression baseline.

- [ ] **T2 — Author Trial3Transcript Pydantic-v2 + schema regen + shape-pin (AC-A)**
  - [ ] T2.1 `app/models/trial3_transcript.py` (~120 LOC; Trial3Transcript + TrialEvent + GateId + TrialEventType Literals).
  - [ ] T2.2 Generate `app/models/trial3_transcript.v1.schema.json` via Path.write_text per A18.
  - [ ] T2.3 `tests/trial/test_trial3_transcript_shape.py` (~80 LOC; schema-hash STABLE pin + closed-enum red-rejection + tz-aware datetime + UUID4 round-trip).

- [ ] **T3 — Author 50-run firing wrapper + invoke (AC-B)**
  - [ ] T3.1 `scripts/utilities/run_slab_close_50_run_parity.py` (~150 LOC; wraps `detect_tw_7c_6_parity_flake.py`; emits per-cell flake-rate report; AMEND-7a budget check).
  - [ ] T3.2 Run the 50-run firing + capture verdict; if TW-7c-6 fires, STOP-AND-ESCALATE per AMEND-7d-iii.
  - [ ] T3.3 If `not_fired`: append aggregated TW-7c-6 ledger entry to `sprint-status.yaml::tripwire_events` (mirror 7c.20c last-closer pattern).

- [ ] **T4 — Author Trial-3 readiness AC verification (AC-C)**
  - [ ] T4.1 `tests/trial/test_trial3_readiness.py` (~150 LOC; covers (a)-(d) predicates).

- [ ] **T5 — Author D12 close-protocol AUDIT + land 3 deliverables (AC-D)**
  - [ ] T5.1 `tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py` (~150 LOC; verifies D12-1 + D12-2 + D12-3 present).
  - [ ] T5.2 Land D12-1 invariant-preservation note (in parent migration epics file).
  - [ ] T5.3 Land D12-2 anti-pattern harvest entries (≥1) in specialist-anti-patterns.md or new catalog.
  - [ ] T5.4 Land D12-3 migration-guide §Slab 7c update.

- [ ] **T6 — Author SG-aggregate AUDIT (AC-E)**
  - [ ] T6.1 `tests/audit/test_audit_ac_sg_aggregate_enforcement.py` (~120 LOC; covers SG-1+2+3+4).

- [ ] **T7 — Author retrospective evidence pack (AC-F)**
  - [ ] T7.1 `_bmad-output/implementation-artifacts/slab-7c-retrospective-evidence-pack.md` (~200 LOC markdown; 8 sections per AC-F).

- [ ] **T8 — Deferred-inventory verifications (AC-G)**
  - [ ] T8.1 Verify slab-7c-live-harness-evidence still-deferred + Trial-2 #1/#2 already-closed via existing inventory entries.

- [ ] **T9 — Verification battery (R-tier R3; T11-tier cross-agent)**
  - [ ] T9.1 Focused: `pytest tests/trial/ tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py tests/audit/test_audit_ac_sg_aggregate_enforcement.py -p no:randomly -q --tb=short` PASS.
  - [ ] T9.2 50-run firing reproducibility (re-invoke harness; assert prior verdict consistent within noise band).
  - [ ] T9.3 Full Slab-7c non-regression sweep PASS UNCHANGED.
  - [ ] T9.4 Smoke 181/18 UNCHANGED.
  - [ ] T9.5 R3 broad: failure count ≤ T1 baseline.
  - [ ] T9.6 Class-conformance UNCHANGED at 19 (no parity_contract added; this story authors ceremony evidence + Trial3Transcript schema).
  - [ ] T9.7 Lint-imports 12 KEPT UNCHANGED (no contract changes; new modules inherit existing scope).
  - [ ] T9.8 Sandbox-AC PASS.
  - [ ] T9.9 Ruff clean.
  - [ ] T9.10 Sprint-status YAML hygiene PASS post-ledger-append.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-21.ready-for-review.md` with: Trial3Transcript schema hash + 50-run TW-7c-6 verdict + R7a/R7b Trial-3 readiness verdict + D12 three-line evidence + SG-aggregate AUDIT verdict + retrospective evidence pack pointer + deferred-inventory verification report.

- [ ] **T11 — Cross-agent code-review (MANDATORY per governance JSON)**
  - [ ] T11.1 Cross-agent review (Claude T11; deeper than standard — strict-last + dual-gate + cross-agent MANDATORY).
  - [ ] T11.2 Review covers: AMEND-4 dual-FR fold integrity, TW-7c-6 firing correctness, D12 three-line completeness, retrospective evidence pack quality, all 7 ACs A-G.

- [ ] **T12 — Operator-driven Gate-2 (NOT dev-agent; runs separately)**
  - [ ] T12.1 Operator triggers `bmad-retrospective` skill via the BMAD facilitator workflow (consumes the retrospective evidence pack from T7).
  - [ ] T12.2 Mapping-checklist row-status flips per R15 / FR-7c-42 (party-mode-ratified at retrospective close).
  - [ ] T12.3 Final close commit + sprint-status flip review→done.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-39..43 + FR-7c-47 + FR-7c-51 + NFR-7c-R7a + NFR-7c-R7b.
3. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.21`.
4. `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D12` (cross-slab governance protocol).
5. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` (50-run harness scaffold + per-cell flake-rate calculator inheritance).
6. `_bmad-output/implementation-artifacts/migration-7c-20c-audit-ac-four-file-lockstep-tripwire-ledger.md` (LAST-CLOSER ledger-append pattern; mirror for TW-7c-6 entry).
7. `app/audit/chain.py` + `app/models/tripwire_ledger.py` (audit-chain integrity + ledger schema).
8. `app/parity/contracts/_flake_rate.py` + `scripts/utilities/detect_tw_7c_6_parity_flake.py` (50-run harness invocation).
9. `app/manifest/compiler.py::production_gate_ids` (Trial3Transcript closed-enum gate-ids source).
10. `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` (33-row floor; SG-2).
11. `tests/parity/test_mapping_checklist_status.py` (SG-2 integrity test).
12. `_bmad-output/planning-artifacts/deferred-inventory.md` (slab-7c-live-harness-evidence + trial-2-finding-1/2 entries).
13. `docs/dev-guide/langgraph-migration-guide.md` (D12-3 migration-guide §-update target).
14. `docs/dev-guide/specialist-anti-patterns.md` (D12-2 anti-pattern catalog).
15. Governance JSON `7c-21` entry: gate_mode=dual-gate, K=1.4×, t11_tier=cross-agent, lookahead_tier=3, prerequisites=28 stories, tripwire_ownership=["TW-7c-6"], stop_on_tripwire_fire=hard.
16. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening for any artifact regen).
17. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms — apply to Trial3Transcript).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. All 28 prerequisites done; AUDIT-AC trio CLEAN (TW-7c-1 not_fired); substrate verified at floors with headroom.

**Lookahead-tier=3 rationale**: deepest tier per governance JSON. This is the slab-close ceremony — by far the heaviest story in Slab 7c (4 pts; K=1.4×; ~1.2K LOC; dual-gate cross-agent MANDATORY).

**Critical-path**: 7c.21 close UNBLOCKS 7c.21a (Wave 6 strict-last cleanup; HARD predecessor relationship per governance JSON).

**STOP-on-TW-7c-6-fire** binding=hard per AMEND-7d-iii (Murat). If TW-7c-6 fires during 50-run firing, ceremony halts; party-mode mitigation required before resumption.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T9)

### Completion Notes List

(populated by Codex at T10; include T1-T9 decisions + 50-run firing TW-7c-6 verdict + R7a/R7b verdict + D12 three-line locations + SG-aggregate verdict)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=3) for Wave-6 closeout-ceremony dispatch with carved-out retrospective scope (operator-driven Gate-2; dev-agent prepares evidence pack only).
