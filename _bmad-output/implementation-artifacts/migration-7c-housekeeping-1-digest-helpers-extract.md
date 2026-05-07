# Migration Story 7c-housekeeping-1: Extract `canonical_model_bytes` + `compute_model_digest` to `app/gates/_common/digest_helpers.py`

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessor Slab 7c at 36/36 dev-stories closed; cross-Wave follow-on filed by 7c.7 T11 reviewer + carried across Wave-3/4/5 closes.)*
**Sprint key:** `migration-7c-housekeeping-1-digest-helpers-extract`
**Source:** Story 7c.7 T11 review SHOULD-FIX-DEFERRED (`_bmad-output/implementation-artifacts/7c-7-code-review-2026-05-05.md`); deferred-inventory entry `digest-helpers-extract-to-app-gates-_common`.
**Pts:** 1-2
**K-target:** 1.2×
**Estimated LOC:** ~250 (-~210 net after duplication elimination: new `app/gates/_common/digest_helpers.py` ~50 + 14 poll-surface modules each shrink ~30 LOC removing local re-emit; net delta ~ -370 LOC; plus 1 new test ~50)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite
**Lookahead-tier:** 1
**files_touched:** 1 new + 14 modified (1 new `app/gates/_common/digest_helpers.py` + 14 poll-surface modules under `app/gates/section_*/`)

---

## Story

As the dev-agent,
I want `canonical_model_bytes` + `compute_model_digest` extracted to `app/gates/_common/digest_helpers.py` so all 14 §section poll-surface modules import from a single source-of-truth instead of re-emitting the helpers locally,
So that the ~40 LOC × 14-package duplication is eliminated while preserving C6 cross-§section independence (the new `_common` module lives **outside** the C6 modules set per `pyproject.toml::tool.importlinter::C6::modules`).

This is a **Wave-4-or-later cross-Wave follow-on** filed by the 7c.7 T11 reviewer + reinforced by every Wave-3/4/5 §section close (see verdict files `7c-7-code-review-2026-05-05.md` + Wave-3-trio close commits). C6 contract is `independence` between `app.gates.section_*` modules — but `app.gates._common.digest_helpers` is NOT in the C6 modules list, so cross-imports from §section packages to `_common` are LEGAL.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED): D5 C6 contract type pivot to `independence`; modules list grew to 14 entries across Slab 7c.
- **14 §section poll-surface modules** (one per HIL surface): section_02a, section_04a, section_04_5, section_04_55, section_05_5, section_06b, section_07b, section_07c, section_07d, section_07f, section_08b, section_11, section_11b, section_15. Each contains identical `canonical_model_bytes` + `compute_model_digest` definitions (~30 LOC duplication per file).
- **C6 modules list** at `pyproject.toml::tool.importlinter::contracts::C6::modules`: 14 entries. `app.gates._common` NOT in this list — cross-imports from §section to `_common` are permitted.

---

## Acceptance Criteria

### AC-1 — `app/gates/_common/digest_helpers.py` extraction

**Given** the 14 §section poll-surface modules' duplicated `canonical_model_bytes` + `compute_model_digest`
**When** the dev-agent authors `app/gates/_common/__init__.py` (empty namespace) + `app/gates/_common/digest_helpers.py`
**Then** the new module exposes:
1. `canonical_model_bytes(model: BaseModel) -> bytes` — byte-identical to existing implementations across the 14 §section files.
2. `compute_model_digest(model: BaseModel) -> str` — sha256-hex digest; byte-identical signature.
3. Module-level `__all__ = ["canonical_model_bytes", "compute_model_digest"]`.

### AC-2 — 14 §section poll-surface modules refactored

**When** the dev-agent updates each of the 14 §section poll-surface modules:
**Then**:
1. Local `canonical_model_bytes` + `compute_model_digest` definitions REMOVED.
2. Import added: `from app.gates._common.digest_helpers import canonical_model_bytes, compute_model_digest`.
3. All call-sites in the file continue to use the SAME function names (no rename).
4. The local `__all__` list is updated to NO LONGER export `canonical_model_bytes` + `compute_model_digest` (they're now sourced from `_common`).

### AC-3 — Determinism + behavior-preservation

**Then**:
1. All existing parity-DSL shape-pin tests + 3-transport parity tests + DSL-registration audit tests continue to PASS (no behavior change; pure refactor).
2. Decision-card digest values across §sections remain byte-identical pre- and post-refactor (sha256-stable).
3. Class-conformance count UNCHANGED at 19.
4. Lint-imports 12 KEPT UNCHANGED (C6 modules list NOT modified — `_common` is outside C6 by design).

### AC-4 — New shared-helper test

**Then** the dev-agent authors `tests/gates/_common/test_digest_helpers.py`:
1. Asserts `canonical_model_bytes` produces deterministic byte output across re-invocations.
2. Asserts `compute_model_digest` returns sha256-hex (64 chars; `r"^[0-9a-f]{64}$"`).
3. Asserts the function signatures match the contracts replaced in §section modules.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm Slab 7c at 36/36 dev-stories closed in sprint-status.
  - [ ] T1.2 Inventory the 14 §section poll-surface modules (verify exact list); read one or two for the canonical helper shape.
  - [ ] T1.3 Verify `app.gates._common` NOT in C6 modules list per `pyproject.toml`.
  - [ ] T1.4 Refresh broad-regression baseline.

- [ ] **T2 — Author shared helper module (AC-1)**
  - [ ] T2.1 `app/gates/_common/__init__.py` (empty namespace).
  - [ ] T2.2 `app/gates/_common/digest_helpers.py` with byte-identical helper definitions.

- [ ] **T3 — Refactor 14 §section poll-surface modules (AC-2)**
  - [ ] T3.1 For each of the 14 files: remove local helper definitions; add import from `_common`; update local `__all__`.

- [ ] **T4 — Author shared-helper test (AC-4)**
  - [ ] T4.1 `tests/gates/_common/__init__.py` + `tests/gates/_common/test_digest_helpers.py`.

- [ ] **T5 — Verification battery (R-tier R2; T11-tier lite)**
  - [ ] T5.1 Focused: `pytest tests/gates/ tests/schemas/operator_verdict/` PASS (all 14 §sections + shape-pins continue to PASS).
  - [ ] T5.2 Focused: `pytest tests/gates/_common/test_digest_helpers.py` PASS.
  - [ ] T5.3 Smoke 181/18 UNCHANGED.
  - [ ] T5.4 R2 broad: delta ≤ 0.
  - [ ] T5.5 Class-conformance UNCHANGED at 19.
  - [ ] T5.6 Lint-imports 12 KEPT UNCHANGED.
  - [ ] T5.7 Sandbox-AC PASS.
  - [ ] T5.8 Ruff clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-housekeeping-1.ready-for-review.md` with: refactor scope (1 new + 14 modified) + per-§section call-site count unchanged + sha256 byte-determinism evidence.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/7c-7-code-review-2026-05-05.md` (origin — SHOULD-FIX-DEFERRED finding).
3. `app/gates/section_02a/poll_surface.py` (canonical helper shape).
4. Any 2-3 other §section poll-surface modules for byte-identicality verification.
5. `pyproject.toml::tool.importlinter::contracts::C6` (verify `_common` NOT in modules list).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. Solo dispatch (single-pkg refactor; no parallel siblings).
