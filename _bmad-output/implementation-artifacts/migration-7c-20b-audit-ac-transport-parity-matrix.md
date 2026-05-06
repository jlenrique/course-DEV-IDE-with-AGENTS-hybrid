# Migration Story 7c.20b: AUDIT-AC ≥15 Cells in 5-Family × 3-Transport Matrix + 8 Named Gate Tests (FR-7c-35)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=2 per governance JSON; predecessors 7c.1 + 7c.4b done — story fully unblocked at this commit. AUDIT-only verification of shipped substrate.)*
**Sprint key:** `migration-7c-20b-audit-ac-transport-parity-matrix`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.2×
**Estimated LOC:** ~250 (AUDIT test module ~150 + transport-matrix discovery helper ~50 + named-gate-test verification ~50)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R3
**T11-tier:** standard (per governance JSON entry `7c-20b`)
**Lookahead-tier:** 2
**files_touched:** 1 new + 0 modified
**Tripwire ownership:** TW-7c-1 (gap-fill detection)

---

## Story

As the test-architect,
I want to verify that ≥15 cells in the 5-family × 3-transport matrix are populated and green at slab-close + 8 named gate tests pass, verifying original Epic 3 story 3.3 verdict-authority enforcement against the shipped substrate,
So that AUDIT-AC verifies the gate-invariant + transport-parity coverage already shipped — confirming `test_no_scheduler_import.py` + `test_resume_from_verdict_digest_match.py` + `test_resume_api_authority.py` + `test_m3_bypass_attempt_rejected.py` + `test_m4_evidence_trace_link_present.py` + `test_consolidated_decision_card_carries_contributions.py` + `test_party_mode_as_interrupt.py` + `test_resume_from_verdict_card_missing.py` are all green.

If gap-rate exceeds AMEND-7c percentage threshold (≥3 gaps = 13% of combined floor 23; closest to 10% boundary at this story size), TW-7c-1 fires; gap-fill follow-ons file as `7c.X.gate-invariant-coverage-gap`.

---

## Predecessor / Dependency Context

- **7c.1** (CLOSED): 8 transport-parity test files registered via parity_contract DSL.
- **7c.4b** (CLOSED): D5 C6 contract independence pivot; 12 KEPT.
- **`tests/integration/transport_parity/`** + **`tests/integration/transports/`**: 8 transport-parity test files (per Codex 7c.1 close attestation).
- **5-family × 3-transport matrix**: 5 DecisionCard families (G1/G2C/G3/G4/Override or G1/G2C/G3/G4/G5 — T1 decision per current matrix layout) × 3 transports (CLI/HTTP/MCP-stdio) = 15 cells minimum (= floor).
- **Combined floor 23** = 15 cells + 8 named gate tests.

---

## Acceptance Criteria

### AC-7c.20b-A — 5-family × 3-transport matrix coverage AUDIT (FR-7c-35; ≥15 cells)

**Given** the shipped 8 transport-parity tests under `tests/integration/transport_parity/` + `tests/integration/transports/` + the parity-DSL registry queryable via `app.parity.contracts.iter_registered_surfaces`
**When** the dev-agent authors `tests/audit/test_audit_ac_transport_parity_matrix.py` + runs the AUDIT
**Then**:
1. The AUDIT enumerates the 5-family × 3-transport matrix (15 cells minimum).
2. For each cell (family, transport), the AUDIT asserts at least one passing test exists demonstrating the cell's coverage.
3. Cell discovery uses the parity_contract DSL registry (`iter_registered_surfaces`) + transport-parity test introspection (pytest collection or filesystem glob) — T1-T9 decision.
4. The AUDIT asserts populated-cell count ≥ **15** (5 × 3 minimum).

### AC-7c.20b-B — 8 named gate tests AUDIT (FR-7c-35)

**When** the AUDIT runs
**Then** the AUDIT confirms each of the following 8 named gate tests is green (PASSING) under `pytest -p no:randomly`:
1. `test_no_scheduler_import.py`
2. `test_resume_from_verdict_digest_match.py`
3. `test_resume_api_authority.py`
4. `test_m3_bypass_attempt_rejected.py`
5. `test_m4_evidence_trace_link_present.py`
6. `test_consolidated_decision_card_carries_contributions.py`
7. `test_party_mode_as_interrupt.py`
8. `test_resume_from_verdict_card_missing.py`

T1-T9 decision: locate each named test via `find tests/ -name "<test_name>.py"` or pytest collection. If a named test is absent, that's a hard gap (1 of 8) — counts toward TW-7c-1 firing precondition.

### AC-7c.20b-C — TW-7c-1 firing on gap-rate threshold (AMEND-7c)

**Given** combined floor 23 = 15 cells + 8 named gate tests
**When** the AUDIT discovers gaps
**Then**:
1. If discovered gap count is **≥3** (13% gap-rate; closest to 10% boundary at this story size): TW-7c-1 (high severity) fires + tripwire-ledger entry written to `sprint-status.yaml::tripwire_events` per AMEND-7c.
2. Test FAILS hard (no soft-skip); gap-fill follow-ons file as `7c.X.gate-invariant-coverage-gap`.
3. If gap count <3: AUDIT PASSES; per-gap notes recorded for visibility but NO tripwire fire.

### AC-7c.20b-D — AUDIT determinism + read-only invariant

**Then** the AUDIT module:
1. Is read-only against the substrate.
2. Produces deterministic AUDIT output (twice-run byte-identical).
3. Surfaces gap-fill descriptors in stable order (sorted by family-transport pair, then by named-test alphabetical).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.1 + 7c.4b done in sprint-status.
  - [ ] T1.2 Read existing 8 transport-parity test files under `tests/integration/transport_parity/` + `tests/integration/transports/` to inventory cell coverage.
  - [ ] T1.3 Locate each of the 8 named gate tests via pytest collection or filesystem-find.
  - [ ] T1.4 Read AMEND-7c percentage-threshold logic from PRD + governance JSON for TW-7c-1 firing rule.
  - [ ] T1.5 Read `app.parity.contracts.iter_registered_surfaces` API for matrix discovery.
  - [ ] T1.6 Refresh broad-regression baseline + record current class-conformance baseline.

- [ ] **T2 — Author AUDIT test module**
  - [ ] T2.1 Author `tests/audit/test_audit_ac_transport_parity_matrix.py` per ACs A-D.
  - [ ] T2.2 Implement matrix-cell discovery helper: enumerate (family, transport) pairs vs registered surfaces / passing tests.
  - [ ] T2.3 Implement named-gate-test verification: for each of 8 named tests, assert location + last-known-PASS status (via pytest --collect-only).
  - [ ] T2.4 Implement TW-7c-1 firing path: on gap-rate ≥13% (≥3 gaps), write tripwire-ledger entry to `sprint-status.yaml::tripwire_events` (append-only).

- [ ] **T3 — Verification battery (R-tier R3; T11-tier standard)**
  - [ ] T3.1 Focused: `pytest tests/audit/test_audit_ac_transport_parity_matrix.py -p no:randomly -q --tb=short` PASS (or STOP-and-escalate per AMEND-7c if gap-rate trips).
  - [ ] T3.2 Non-regression sweep: §02A + Wave-3/4/5 + Marcus writer PASS UNCHANGED.
  - [ ] T3.3 R3 broad: delta ≤ 0.
  - [ ] T3.4 Class-conformance UNCHANGED (no parity_contract registered).
  - [ ] T3.5 Lint-imports: 12 KEPT UNCHANGED.
  - [ ] T3.6 Sandbox-AC: PASS.
  - [ ] T3.7 Ruff: clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-20b.ready-for-review.md` with: matrix-cell count + 8-named-test verification result + per-gap descriptors + TW-7c-1 fire/no-fire verdict + AUDIT determinism evidence.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-35 + AMEND-7c.
3. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.20b`.
4. `_bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md` (sibling AUDIT-AC for pattern parity).
5. `tests/integration/transport_parity/` + `tests/integration/transports/` (existing transport-parity test files).
6. The 8 named gate tests (locate via pytest collection).
7. `app/parity/contracts/__init__.py` + `_registry.py` (iter_registered_surfaces API).
8. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events`.
9. Governance JSON `7c-20b` entry.

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. Predecessors 7c.1 + 7c.4b done.

**Parallel-dispatch viable with 7c.20a + 7c.20c** — AUDIT-AC trio; path-disjoint at file level (each `tests/audit/test_audit_ac_*.py` module is separate). Coordinate STOP-and-escalate posture if ANY of the three AUDITs trips TW-7c-1.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T3)

### Completion Notes List

(populated by Codex at T10)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=2) for Wave-5 AUDIT-AC trio dispatch.
