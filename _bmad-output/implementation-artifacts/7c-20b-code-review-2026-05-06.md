# Story 7c.20b — T11 Standard Code Review

**Reviewer:** Claude (T11 standard)
**Date:** 2026-05-06
**Story:** `migration-7c-20b-audit-ac-transport-parity-matrix`
**Implementation author:** Codex GPT-5
**Review tier:** T11 standard

---

## Verdict: **PASS-zero-patches**

Codex implemented Story 7c.20b cleanly. All 4 ACs (A-D) are satisfied. **AUDIT-AC clean — 1 gap descriptor (below 3-gap firing threshold); TW-7c-1 not fired.** The single gap is the inherited `test_no_unauthorized_callers` scanner-staleness already DISMISSED across multiple prior verdicts (7c.13/14/etc.) — recognized as PRE-EXISTING noise, NOT a Slab-7c regression.

---

## Findings

| Severity | Finding | Rationale |
|---|---|---|
| **MUST-FIX** | _none_ | — |
| **SHOULD-FIX** | _none_ | — |
| NIT-DISMISSED | The 1 gap descriptor (`named-gate-test-failing:tests/integration/gates/test_resume_api_authority.py`) | This failure is the inherited `test_no_unauthorized_callers` scanner-staleness — substring scan matches `OperatorVerdict(` class-definition signatures, NOT direct constructor calls. Documented as PRE-EXISTING noise across multiple prior verdicts (7c.13/14/9/10/11/12). DISMISS as inherited. Will be properly addressed by the test-scanner staleness follow-on already in `deferred-inventory.md`. |
| NIT-DISMISSED | Broad regression 45 failed UNCHANGED | Inherited Wave-5 baseline; no 7c.20b regression. DISMISS. |

---

## AC verification (standard-tier deep dive)

### AC-7c.20b-A — 5-family × 3-transport matrix coverage AUDIT (FR-7c-35; ≥15 cells)
- ✓ Matrix discovery via `iter_registered_surfaces` from parity-contract DSL registry
- ✓ Cell coverage: **15/15** for G1/G2C/G3/G4/G5 across cli/http/mcp-stdio (= floor 15; clean coverage)
- ✓ No matrix gaps

### AC-7c.20b-B — 8 named gate tests AUDIT (FR-7c-35)
- ✓ All 8 named tests located via pytest collection: `test_no_scheduler_import.py`, `test_resume_from_verdict_digest_match.py`, `test_resume_api_authority.py`, `test_m3_bypass_attempt_rejected.py`, `test_m4_evidence_trace_link_present.py`, `test_consolidated_decision_card_carries_contributions.py`, `test_party_mode_as_interrupt.py`, `test_resume_from_verdict_card_missing.py`
- ✓ 8/8 present and collectable
- ⚠️ Runtime named-gate result: **13 passed, 1 failed** — the 1 failure is the inherited `test_no_unauthorized_callers` scanner-staleness (DISMISS as PRE-EXISTING per established precedent)

### AC-7c.20b-C — TW-7c-1 firing on gap-rate threshold (AMEND-7c)
- ✓ Combined floor 23 (15 cells + 8 named tests); discovered gap count **1**; gap rate **4.3%** vs threshold 13% (≥3 gaps)
- ✓ TW-7c-1 verdict for 7c.20b: **`not_fired`** (1 gap below firing threshold)
- ✓ Per-story gap count tracked for 7c.20c LAST-CLOSER aggregation

### AC-7c.20b-D — AUDIT determinism + read-only invariant
- ✓ Read-only against substrate
- ✓ Stable ordering of gap-fill descriptors

---

## Spot-check evidence

| Command | Expected | Actual | Match |
|---|---|---|---|
| `pytest tests/audit/` (4 modules) | combined PASS | **18 passed in 30.95s** | ✓ |
| `lint-imports.exe` | 12 KEPT UNCHANGED | **12 kept, 0 broken** | ✓ |
| `validate_parity_test_class_conformance.py` | 19 PASS UNCHANGED | **PASS: 19** | ✓ |
| Sandbox-AC | PASS | **PASS** (per Codex evidence) | ✓ |
| Smoke | 181/18 UNCHANGED | **181 passed / 18 skipped** | ✓ |

---

## Standard-tier ratchet check

- **Matrix discovery via registry** — uses `iter_registered_surfaces` (DSL-driven; future-proof against new surfaces) ✓
- **Named-gate-test verification** — pytest collection-based; properly classifies inherited vs new failures ✓
- **TW-7c-1 ownership discipline** — gap count below threshold; correct `not_fired` verdict ✓
- **Inherited gap correctly classified** — Codex did NOT count `test_no_unauthorized_callers` failure as a Slab-7c regression; correctly attributed to inherited scanner-staleness ✓

---

## Velocity record

- Wave 5 AUDIT-AC trio second close (paired with 7c.20a + 7c.20c).
- Transport-parity matrix at floor exactly (15/15) — no matrix gaps; full coverage.
- 1 inherited gap correctly dismissed; AUDIT-AC narrowly avoids firing while preserving signal integrity.
- T11 standard cycle: ~25-40 min; PASS-zero-patches.
- Recommend **flip done** + close-batch.

---

## Closeout actions

1. ☑ Verdict written: PASS-zero-patches
2. ☐ Sprint-status flip: `migration-7c-20b-audit-ac-transport-parity-matrix: review → done`
3. ☐ Close-batch commit (combined with 7c.20a + 7c.20c PASS verdicts)
