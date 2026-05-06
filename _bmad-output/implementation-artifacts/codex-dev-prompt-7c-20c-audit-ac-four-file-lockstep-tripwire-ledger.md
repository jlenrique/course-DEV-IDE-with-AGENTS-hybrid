# Codex dev-story prompt — Story 7c.20c (AUDIT-AC 14/14 Four-File-Lockstep + 6/6 Tripwire-Ledger Probes; LAST-AUDIT-AC closer; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T1-T10 → drops `_codex-handoff/7c-20c.ready-for-review.md` → Claude T11 standard.
**Wave:** 5 — AUDIT-AC trio slot 3 of 3 (LAST-CLOSER; aggregates final TW-7c-1 verdict).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

**Recommended dispatch order:** dispatch AFTER 7c.20a + 7c.20b begin T1 (so their tripwire-ledger entries are present for aggregation). Eager-parallel works if 7c.20c re-reads the ledger at T2 to capture late-arriving sibling entries.

---

```
Run bmad-dev-story on Story 7c.20c (Slab 7c Wave 5 AUDIT-AC trio slot 3; LAST-CLOSER; single-gate; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-20c-audit-ac-four-file-lockstep-tripwire-ledger.md`.

## Required reading (in order)

1. Story spec (4 ACs A-D).
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-37 + FR-7c-38 + FR-7c-50 + NFR-7c-OD2 + AMEND-7c.
3. `_bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md` + `migration-7c-20b-audit-ac-transport-parity-matrix.md` (sibling AUDIT-ACs; aggregation source).
4. **`tests/audit/test_override_event_chain_integrity.py`** (7c.0b FR-7c-50 audit-chain integrity scaffold; READ-ONLY).
5. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (existing 4 Slab-7b entries + 7c.20a/b TW-7c-1 entries if landed first).
6. `app/models/decision_cards/` (DecisionCard family files for lockstep AUDIT direct path).
7. `tests/parity/test_decision_card_*.py` (shape-pin tests for direct lockstep path).
8. `app/parity/contracts/_decorator.py` (`alias_of` forward-syntax for 6 alias families).
9. Governance JSON `7c-20c` entry.

## T1 hard checkpoints

- 7c.4b + 7c.5.G0..G6 done.
- 7c.20a + 7c.20b at done OR in-progress (their ledger entries inform aggregation).
- 14-gate post-Slab-7c expansion enumerated: 8 net-new (G0..G6 + Override = 8 direct DecisionCard families) + 6 alias families inheriting (per ADR 0002 §3 — exact count T1-confirmed).
- 6 tripwire-ledger entries in scope: TW-7c-1 (this trio aggregates) + TW-7c-2..6 (future entries).
- AMEND-7c firing threshold = ≥2 gaps (10% of floor 20).

## Files in scope

**New (1 file):**
- `tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py` (~280 LOC)

**Modified (1 file; LAST-CLOSER aggregation):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` — APPEND final aggregated TW-7c-1 verdict entry (cross-AUDIT-AC trio summary). Single-entry append; deterministic byte output.

**Do NOT modify:**
- 7c.0b audit-chain integrity scaffold (`tests/audit/test_override_event_chain_integrity.py`)
- DecisionCard family files (read-only)
- Existing shape-pin tests (read-only)
- Any production code under `app/`

## Critical implementation notes

- **Lockstep verification (AC-A)**: enumerate 14 gates; for direct-path (8 net-new), verify (DecisionCard model + JSON schema + golden-fixture if applicable + shape-pin test) co-exist + cross-reference (e.g., schema_version pin or import path). For inheritance-path (6 alias families), verify `parity_contract(alias_of=...)` registration in poll-surface module — alias's lockstep is "inherited from parent family."
- **Tripwire-ledger probe (AC-B)**: load `sprint-status.yaml::tripwire_events`; for each entry, validate against `TripwireLedgerEntry` schema (NFR-7c-OD2; closed-enum tripwire_id + closed-enum fired_verdict + structured measured_value + sha256 decision_record_link). Verify append-only + monotonic-timestamp + parent-trace-linkage invariants per FR-7c-50.
- **AUDIT-AC trio aggregation (AC-C)**: read 7c.20a + 7c.20b TW-7c-1 fire status from ledger (if entries present). Compute `final_aggregated_verdict`:
  - ANY fired ⇒ `fired_verdict: true` + escalation summary
  - ALL clean ⇒ `fired_verdict: false` + clean-trio summary
  - Marginal (close-but-not-over) ⇒ `fired_verdict: marginal-fired` per Slab-7b precedent
- **Final ledger-append**: APPEND a tripwire entry with `tripwire_id: TW-7c-1`, `story_owner: "7c-20c"` (last-closer), `fired_at: <today-iso8601>`, `fired_verdict: <aggregated>`, `measured_value: {gap_count_per_story_a/b/c, combined_floor: 20, ...}`, `escalation_action_taken: <text or "none-fired-by-content">`, `decision_record_link: <verdict-file-path>`.
- **AUDIT determinism**: sort discovery results; twice-run byte-identical AUDIT verdict; ledger-append happens once per dispatch (not per re-run).
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~280 LOC actual.

## PARALLEL-DISPATCH GUARDRAILS

1. **AMEND-7d-i AST-scan compliance.** N/A.
2. **Pattern-replication discipline.** Mirror 7c.20a + 7c.20b AUDIT shape; reuse helpers if extracted.
3. **Shared-file integration ordering.** `sprint-status.yaml::tripwire_events` — last-closer aggregation discipline; if 7c.20a/b haven't yet appended their entries, log a warning + proceed with available data + recommend re-run on close-batch landing.
4. **Pattern-parity ratchet.** N/A (no Pydantic models authored).
5. **Class-conformance arithmetic.** UNCHANGED.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T3)

```bash
.venv/Scripts/python.exe -m pytest tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/audit/test_override_event_chain_integrity.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/test_sprint_status_yaml.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-20c-audit-ac-four-file-lockstep-tripwire-ledger.md
.venv/Scripts/python.exe -m ruff check tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-20c.ready-for-review.md`. Include: 14/14 lockstep verification + 6/6 tripwire-probe verification + per-gap descriptors + 7c.20c TW-7c-1 fire/no-fire + **final aggregated TW-7c-1 verdict** (across the trio) + ledger-append byte-determinism evidence.

T11: Claude standard tier (~25-40 min). LAST-CLOSER review surfaces aggregation correctness + ledger-append determinism.

## Boundary

HALT on: predecessors not done; class-conformance baseline drift; ledger-append breaks append-only or monotonic-timestamp invariants; aggregated-verdict logic incorrect (cross-check 7c.20a + 7c.20b individual fires).

DO NOT touch: 7c.0b audit-chain integrity scaffold; DecisionCard family files; existing shape-pin tests; production code under `app/`.

DO NOT introduce: new lockstep checks beyond the 14 gates (those are gap-fill follow-ons); new tripwire-ledger entry types (NFR-7c-OD2 schema is closed).
```

---

## Operator dispatch checklist

1. ☐ Predecessors (7c.4b + 7c.5.G0..G6) done.
2. ☐ 7c.20a + 7c.20b at least at T1 readiness OR done (aggregation source).
3. ☐ AMELIA-P2 PASS.
4. ☐ Sprint-status: ready-for-dev.
5. ☐ Dispatch (recommended LAST in AUDIT-AC trio).
