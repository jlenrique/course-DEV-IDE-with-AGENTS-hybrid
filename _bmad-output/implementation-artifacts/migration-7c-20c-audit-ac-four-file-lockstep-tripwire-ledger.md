# Migration Story 7c.20c: AUDIT-AC 14/14 Four-File-Lockstep + 6/6 Tripwire-Ledger Probes (FR-7c-37 + FR-7c-38)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=2 per governance JSON; predecessors 7c.4b + 7c.5.G0..G6 all DONE — story fully unblocked. **LAST-AUDIT-AC closer**: aggregates final TW-7c-1 fired_verdict at sprint-status.yaml::tripwire_events.)*
**Sprint key:** `migration-7c-20c-audit-ac-four-file-lockstep-tripwire-ledger`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 1-2
**K-target:** 1.2×
**Estimated LOC:** ~280 (AUDIT test module ~150 + 4-file-lockstep co-commit verification ~50 + tripwire-ledger probe verification ~50 + final TW-7c-1 verdict aggregation ~30)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R3
**T11-tier:** standard (per governance JSON entry `7c-20c`)
**Lookahead-tier:** 2
**files_touched:** 1 new + 1 modified (final TW-7c-1 verdict aggregation written to `sprint-status.yaml::tripwire_events`)
**Tripwire ownership:** TW-7c-1 (gap-fill detection; AGGREGATES final verdict across the 3 AUDIT-ACs)

---

## Story

As the test-architect,
I want to verify 14/14 four-file-lockstep co-commit checks + 6/6 tripwire-ledger probes at slab-close, verifying original Epic 3 stories 3.5 + 3.6 against the shipped substrate, and aggregate the final TW-7c-1 fired_verdict across the AUDIT-AC trio,
So that AUDIT-AC verifies cache-impact + operator-id override flow + override_event audit chain shape + every TW-7c-1..6 entry passes audit-chain validator on emit, with the **last-AUDIT-AC closer** writing the aggregated TW-7c-1 verdict to the ledger.

If gap-rate exceeds AMEND-7c percentage threshold (≥2 gaps = 10% of combined floor 20), TW-7c-1 fires; gap-fill follow-ons file as `7c.X.override-event-coverage-gap`.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED): D5 C6 contract independence pivot; 12 KEPT.
- **7c.5.G0..G6** (ALL CLOSED): 7-DecisionCard family migration to DecisionCardBase.
- **14-gate post-Slab-7c expansion**: 8 net-new HIL surfaces (§02A + §04A + §04.5 + §04.55 + §05.5 + §07B + §07D + §07F + §08B + §11 + §06B + §07C + §11B + §15) + 6 alias families inheriting via alias-DSL clause (G0/G1/G2A/G2C/G3/G4/G5/G6 — actually count is 14 total per the 14/14 lockstep AC; T1 confirms exact mapping).
- **6 tripwire-ledger entries (TW-7c-1..6)** at `sprint-status.yaml::tripwire_events`: `wave_1_close` + `wave_2b_close` + `wave_3_first_port` + `wave_3_parallel_close_kira` (Slab 7b) + future TW-7c-1..6 entries to be added by 7c.20a/b/c + 7c.21 (Slab 7c).
- **FR-7c-50 audit-chain integrity test scaffold**: shipped at 7c.0b — `tests/audit/test_override_event_chain_integrity.py` asserts append-only invariant + monotonic timestamp + parent-trace linkage + red-rejection error semantics.
- **Combined floor 20** = 14 lockstep checks + 6 tripwire-ledger probes.
- **AUDIT-AC sibling stories**: 7c.20a + 7c.20b. **THIS STORY IS THE LAST-AUDIT-AC CLOSER**: aggregates final TW-7c-1 verdict (`fired_verdict: true | false | marginal-fired`) at `sprint-status.yaml::tripwire_events` per AMEND-7c protocol. If 7c.20a or 7c.20b individually fired TW-7c-1, this story's aggregated verdict reflects that.

---

## Acceptance Criteria

### AC-7c.20c-A — Four-file-lockstep co-commit AUDIT (FR-7c-37; 14/14)

**Given** the 14-gate post-Slab-7c expansion (8 net-new + 6 alias inheriting via alias-DSL clause)
**When** the dev-agent authors `tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py` + runs the AUDIT
**Then**:
1. The AUDIT enumerates the 14 gate-family-or-alias entries.
2. For each gate, the AUDIT verifies four-file-lockstep co-commit invariant: (a) DecisionCard model file + (b) JSON schema file + (c) golden-fixture file (if applicable for this family) + (d) shape-pin test file all co-commit (i.e., reference each other by digest or import).
3. Direct verification path for 8 net-new gates: each has a dedicated DecisionCard module + schema + shape-pin under `app/models/decision_cards/` + `tests/parity/test_decision_card_*.py`.
4. Inheritance verification path for 6 alias families: alias-DSL clause inheritance via `parity_contract(alias_of=...)` registration; alias's lockstep is `inherited` from its parent family (per ADR 0002 §3 forward-syntax).
5. AUDIT asserts 14/14 lockstep verified (no gap permitted on the lockstep dimension — direct or inherited).

### AC-7c.20c-B — Tripwire-ledger probe AUDIT (FR-7c-38; 6/6)

**Given** the 6 named TW-7c-1..6 ledger entries shape (per NFR-7c-OD2)
**When** the AUDIT runs FR-7c-50 audit-chain integrity test against `sprint-status.yaml::tripwire_events`
**Then** every TW-7c-1..6 entry passes the audit-chain validator on emit:
1. **NFR-7c-OD2 schema enforcement**: each entry conforms to `TripwireLedgerEntry` Pydantic-v2 schema (closed-enum tripwire_id + closed-enum fired_verdict + structured measured_value + sha256 decision_record_link).
2. **Append-only invariant**: no in-place edits; new entries only.
3. **Monotonic timestamp**: each entry's `fired_at` timestamp ≥ prior entry's.
4. **Parent-trace linkage**: each entry references upstream story_owner via `decision_record_link`.
5. AUDIT enumerates and asserts 6/6 entries pass (gap permitted up to AMEND-7c threshold of ≥2 gaps).

### AC-7c.20c-C — TW-7c-1 firing on gap-rate threshold + final aggregated verdict (AMEND-7c)

**Given** combined floor 20 = 14 lockstep + 6 tripwire-ledger probes; AND 7c.20a/b's individual TW-7c-1 fire/no-fire status
**When** the AUDIT discovers gaps + aggregates AUDIT-AC trio verdicts
**Then**:
1. If 7c.20c's discovered gap count is **≥2** (10% gap-rate against floor 20): TW-7c-1 fires for THIS story + tripwire-ledger entry written + final aggregated verdict reflects it.
2. **Final aggregated TW-7c-1 verdict** (across 7c.20a + 7c.20b + 7c.20c):
   - If ANY of the three fired: aggregated `fired_verdict: true` + `escalation_action_taken` reflects per-story fire details.
   - If ALL three did NOT fire: aggregated `fired_verdict: false` + `notes` records "AUDIT-AC trio clean — Slab 7c substrate verified at coverage floors".
   - Marginal fires (close to threshold but not over) are recorded as `fired_verdict: marginal-fired` per Slab-7b precedent (e.g., `wave_1_close` 2026-04-29).
3. THE FINAL VERDICT IS WRITTEN TO `sprint-status.yaml::tripwire_events` BY THIS STORY'S DEV-AGENT (this is the last-AUDIT-AC closer responsibility per governance JSON amendment_note).
4. If aggregated verdict is fired: STOP; do NOT proceed to 7c.21 (Wave 6 closeout); party-mode-consensus on absorb-vs-defer per gap; gap-fill follow-ons file.

### AC-7c.20c-D — AUDIT determinism + read-only invariant on the substrate (write-only on tripwire ledger)

**Then** the AUDIT module:
1. Is read-only against the substrate (does NOT modify any production code or shipped tests).
2. Is **write-allowed** on `sprint-status.yaml::tripwire_events` for the final aggregated TW-7c-1 verdict (single append per AUDIT-AC trio close; deterministic byte output).
3. Produces deterministic AUDIT output (twice-run byte-identical for the AUDIT verdict; tripwire-ledger append happens once per dispatch).
4. Surfaces gap-fill descriptors in stable order.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.4b + 7c.5.G0..G6 done.
  - [ ] T1.2 Confirm 7c.20a + 7c.20b are at done (or in-progress; aggregation requires their fire-status, but T1 readiness allows either).
  - [ ] T1.3 Read existing `tests/audit/test_override_event_chain_integrity.py` (7c.0b deliverable; FR-7c-50 audit-chain integrity scaffold).
  - [ ] T1.4 Read `sprint-status.yaml::tripwire_events` ledger to inventory existing entries (Slab-7b had 4 entries; Slab-7c entries to be added by 7c.20a/b first).
  - [ ] T1.5 Read NFR-7c-OD2 TripwireLedgerEntry schema.
  - [ ] T1.6 Refresh broad-regression baseline + class-conformance baseline.

- [ ] **T2 — Author AUDIT test module**
  - [ ] T2.1 Author `tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py` per ACs A-D.
  - [ ] T2.2 Implement four-file-lockstep verification: enumerate 14 gates (8 direct + 6 inherited via alias-DSL); verify lockstep co-commit for each.
  - [ ] T2.3 Implement tripwire-ledger probe verification: load `sprint-status.yaml::tripwire_events`; validate each entry against TripwireLedgerEntry schema + append-only + monotonic-timestamp + parent-trace invariants.
  - [ ] T2.4 Implement AUDIT-AC trio aggregation logic: read 7c.20a/b individual TW-7c-1 fire status (if their tripwire entries are present); compute final aggregated verdict.
  - [ ] T2.5 Implement final TW-7c-1 ledger entry write: APPEND aggregated verdict entry to `sprint-status.yaml::tripwire_events` (append-only; deterministic byte output).

- [ ] **T3 — Verification battery (R-tier R3; T11-tier standard)**
  - [ ] T3.1 Focused: `pytest tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py -p no:randomly -q --tb=short` PASS (or STOP-and-escalate per AMEND-7c).
  - [ ] T3.2 Audit-chain integrity test PASS UNCHANGED (`tests/audit/test_override_event_chain_integrity.py` continues passing; new ledger entry must conform).
  - [ ] T3.3 Non-regression sweep: §02A + Wave-3/4/5 + Marcus writer + AUDIT-AC siblings PASS UNCHANGED.
  - [ ] T3.4 R3 broad: delta ≤ 0.
  - [ ] T3.5 Class-conformance UNCHANGED.
  - [ ] T3.6 Lint-imports: 12 KEPT UNCHANGED.
  - [ ] T3.7 Sandbox-AC: PASS.
  - [ ] T3.8 Ruff: clean.
  - [ ] T3.9 Sprint-status YAML hygiene test PASS post-ledger-append.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-20c.ready-for-review.md` with: 14/14 lockstep verification + 6/6 tripwire-probe verification + per-gap descriptors + 7c.20c TW-7c-1 fire/no-fire + **final aggregated TW-7c-1 verdict** (across the trio) + ledger-append byte-determinism evidence.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-37 + FR-7c-38 + FR-7c-50 + NFR-7c-OD2 + AMEND-7c.
3. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.20c`.
4. `_bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md` + `migration-7c-20b-audit-ac-transport-parity-matrix.md` (sibling AUDIT-ACs; aggregation source).
5. `tests/audit/test_override_event_chain_integrity.py` (7c.0b FR-7c-50 audit-chain integrity scaffold).
6. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (existing 4 Slab-7b entries; Slab-7c entries to be added by 7c.20a/b).
7. `app/models/decision_cards/` (DecisionCard family files for lockstep AUDIT).
8. `tests/parity/test_decision_card_*.py` (shape-pin tests for lockstep AUDIT direct path).
9. `app/parity/contracts/_decorator.py` for `alias_of` forward-syntax (alias-DSL inheritance for 6 alias families).
10. Governance JSON `7c-20c` entry.

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. Predecessors 7c.4b + 7c.5.G0..G6 done.

**Recommended dispatch order:** 7c.20c is the LAST-AUDIT-AC closer; should dispatch AFTER 7c.20a + 7c.20b have at least begun T1 (so their tripwire-ledger entries are present for aggregation). Strict serial vs eager-parallel is operator decision — eager-parallel works if 7c.20c re-reads the ledger at T2 to capture late-arriving sibling entries.

**Lookahead-tier=2 rationale:** spec is pre-authored at deeper lookahead per governance.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T3)

### Completion Notes List

(populated by Codex at T10; include 14/14 lockstep + 6/6 tripwire verification + 7c.20c TW-7c-1 fire/no-fire + final aggregated trio verdict + ledger-append determinism)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=2) for Wave-5 AUDIT-AC trio dispatch (last-closer aggregation responsibility).
