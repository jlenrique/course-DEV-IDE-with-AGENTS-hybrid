# Codex dev-story prompt — Story 7c.20b (AUDIT-AC ≥15 Cells in 5-Family × 3-Transport Matrix + 8 Named Gate Tests; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T1-T10 → drops `_codex-handoff/7c-20b.ready-for-review.md` → Claude T11 standard.
**Wave:** 5 — AUDIT-AC trio slot 2 of 3.
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

**Parallel-dispatch context:** Path-disjoint with 7c.20a + 7c.20c. Shared TW-7c-1 ownership; STOP-and-escalate per AMEND-7c if firing threshold trips.

---

```
Run bmad-dev-story on Story 7c.20b (Slab 7c Wave 5 AUDIT-AC trio slot 2; single-gate; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-20b-audit-ac-transport-parity-matrix.md`.

## Required reading (in order)

1. Story spec (4 ACs A-D).
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-35 + AMEND-7c.
3. `_bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md` (sibling AUDIT-AC; pattern reference).
4. **`tests/integration/transport_parity/`** + **`tests/integration/transports/`** (existing 8 transport-parity test files; READ-ONLY).
5. **The 8 named gate tests** (locate via pytest collection or filesystem-find): `test_no_scheduler_import.py`, `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`, `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`, `test_consolidated_decision_card_carries_contributions.py`, `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`.
6. **`app/parity/contracts/__init__.py`** + **`_registry.py`** (`iter_registered_surfaces` API for matrix discovery).
7. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (ledger schema).
8. Governance JSON `7c-20b` entry.

## T1 hard checkpoints

- 7c.1 + 7c.4b done.
- Existing 8 transport-parity test files inventoried (read filenames + parameterizations).
- All 8 named gate tests located + last-known-PASS status confirmed.
- 5-family × 3-transport matrix discovery via `iter_registered_surfaces` produces ≥15 cells.
- AMEND-7c firing threshold = ≥3 gaps (13% of floor 23).

## Files in scope

**New (1 file):**
- `tests/audit/test_audit_ac_transport_parity_matrix.py` (~250 LOC)

**Modified (0 files normally; 1 modified IF gap-rate trips):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events`

**Do NOT modify:**
- Existing transport-parity tests
- The 8 named gate tests
- `app/parity/contracts/` (read-only)
- Any production code under `app/`

## Critical implementation notes

- **AUDIT-not-BUILD framing**: same as 7c.20a; verify, do NOT add coverage.
- **Matrix discovery**: 5 families × 3 transports = 15 cells minimum. Use `iter_registered_surfaces()` from `app.parity.contracts` to enumerate registered surfaces by (family, transport) pair.
- **Named-gate-test verification**: for each of 8 named tests, locate via pytest collection; assert PASS status.
- **TW-7c-1 firing path**: same as 7c.20a; ledger append-only on ≥3 gaps.
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~250 LOC actual.

## PARALLEL-DISPATCH GUARDRAILS (same six rules)

Sibling AUDIT-AC pattern; no shared production-code edits; ledger append-only first-mover-then-rebase per AMELIA-P3 dispatch staggering norm. Pattern-parity ratchet aligns with 7c.20a's AUDIT shape (ratcheted at 7c.20a authoring).

## Verification battery (T3)

```bash
.venv/Scripts/python.exe -m pytest tests/audit/test_audit_ac_transport_parity_matrix.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/integration/transport_parity/ tests/integration/transports/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-20b-audit-ac-transport-parity-matrix.md
.venv/Scripts/python.exe -m ruff check tests/audit/test_audit_ac_transport_parity_matrix.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-20b.ready-for-review.md`. Include: matrix-cell count + 8-named-test verification result + per-gap descriptors + TW-7c-1 fire/no-fire verdict + AUDIT determinism evidence.

T11: Claude standard tier (~25-40 min).

## Boundary

HALT on: 7c.1 / 7c.4b not done; class-conformance baseline drift; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; ≥3 named-gate-test absent (high-severity gap, fires TW-7c-1 unconditionally).

DO NOT touch: existing transport-parity tests, named gate tests, app/ production code.

DO NOT introduce: new transport-parity tests in 7c.20b scope (those are gap-fill follow-ons).
```

---

## Operator dispatch checklist

1. ☐ Predecessors (7c.1 + 7c.4b) done.
2. ☐ AMELIA-P2 PASS.
3. ☐ Sprint-status: ready-for-dev.
4. ☐ Dispatch.
