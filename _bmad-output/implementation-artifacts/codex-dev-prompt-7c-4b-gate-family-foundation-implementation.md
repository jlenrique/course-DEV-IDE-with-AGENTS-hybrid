# Codex dev-story prompt — Story 7c.4b (Gate-Family Foundation Implementation; cross-agent MANDATORY; D1-D8 contract-locked)

**Cycle:** Claude spec (D1-D8 LOCKED per AMEND-V5) → Codex T1-T10 → drops `_codex-handoff/7c-4b.ready-for-review.md` → Claude T11 cross-agent MANDATORY → commit + flip done.
**Wave:** 2 — slot 2 (substrate-foundation; precedes 7c.5.G0..G6 8 per-gate stories).
**Pre-authored:** 2026-05-05 with cross-agent contract negotiation per AMEND-V5.
**Dispatch state:** **DISPATCHABLE NOW** post-7c.4a-close.

---

```
Run bmad-dev-story on Story 7c.4b (Slab 7c Wave 2 slot 2; dual-gate; cross-agent MANDATORY).

## ⚠️ CONTRACT-LOCKED — D1-D8 verify, don't relitigate.

Spec: `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (D1-D8 in §Contract Negotiation Decisions).

## Required reading (in order)

1. Story spec (D1-D8).
2. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (frozen taxonomy; alias_of forward-syntax).
3. `docs/dev-guide/adr/0001-parity-contract-dsl.md` (DSL primitives).
4. `app/parity/contracts/_declaration.py` + `_decorator.py` + `_registry.py` (extend with alias_of per D1).
5. `app/models/tripwire_ledger.py` (TripwireLedgerEntry pattern reference).
6. `app/models/decision_cards/` (existing per-gate models; verify _base.py existence).
7. `app/manifest/compiler.py` (Slab 7a substrate; extend per D7).
8. `scripts/utilities/validate_parity_test_class_conformance.py` (extend per D6).
9. `tests/schemas/operator_verdict/test_section_02a_shape.py` (7c.3b pattern-precedent).
10. Governance JSON `7c-4b` (dual-gate; cross_agent_review_required=true; pts=3; K=1.4; r_tier=R3; t11_tier=cross-agent; lookahead_tier=3-AUTHORED; prerequisite_stories=[7c-0b, 7c-4a]).
11. Required readings: pydantic-v2-schema-checklist + dev-agent-anti-patterns + story-cycle-efficiency + pytest-xdist-classification.

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.0b + 7c.4a both `done`.
- ADR 0001 + 0002 present.
- DSL primitives importable.
- `app/models/decision_cards/_base.py` existence — extend or create; document.
- `app/manifest/compiler.py` Slab 7a substrate present.
- pyproject.toml C6 contract present (12 source_modules; empty forbidden_modules).
- 7c.3b's `app/gates/section_02a/` doesn't cross-import other §sections.

## Files in scope

**New (~8 files):**
- `app/models/decision_cards/_base.py` — DecisionCardBase + DecisionCardMeta per D2.
- `app/parity/contracts/tw_7c_3_firing.py` — LOCKSTEP_CHECK + FOUR_FILE_GLOBS + LockstepResult per D4.
- `app/gates/_shared/__init__.py` — package marker if absent (per D5).
- `tests/schemas/operator_verdict/_harness.py` — parametrized harness per D3.
- `tests/parity/test_decision_card_base_shape.py` — AC-A pin.
- `tests/parity/test_class_conformance_validator_extension.py` — AC-D pin.
- `tests/structural/test_import_linter_c6_target_list_populated.py` — AC-F pin.
- `tests/structural/test_tw_7c_3_firing_spec_single_source.py` — AMEND-7d-i pin.
- `tests/parametrized_harness/test_operator_verdict_harness_consumable.py` — AC-C pin.
- `tests/integration/manifest/test_compiler_honors_new_gate_codes.py` — AC-E pin.

**Modified (~5 files):**
- `app/parity/contracts/_declaration.py` — extend SurfaceTransportDeclaration with alias_of field per D1.
- `app/parity/contracts/_decorator.py` — extend parity_contract decorator with alias_of kwarg per D1.
- `scripts/utilities/validate_parity_test_class_conformance.py` — extend per D6.
- `app/manifest/compiler.py` — extend per D7.
- `pyproject.toml` — populate C6 forbidden_modules per D5.

**Optionally modified:**
- `tests/schemas/operator_verdict/test_section_02a_shape.py` — reshape to consume harness OR keep standalone (T1 decision).

**Do NOT modify:**
- 7c.0a's TripwireLedgerEntry or ADR.
- 7c.0b's DSL package internals (only extend declaration + decorator).
- 7c.3a's composer body or directive_model.
- 7c.3b's poll_surface or operator_verdict_section_02a.
- 7c.4a's ADR 0002.
- C4 + C5 forbidden_modules.

## Critical implementation notes

- D1-D8 LOCKED. Surface deviations as `decision_needed` at T10 BEFORE completing.
- alias_of validator MUST reject non-family-IDs (closed set: G0/G1/G2A/G2C/G3/G4/G5/G6).
- DecisionCardBase mirrors TripwireLedgerEntry triple-layer red-rejection on cache_state.
- LOCKSTEP_CHECK is the SINGLE source of truth; 7c.5.G* MUST cite by reference (verified by `tests/structural/test_tw_7c_3_firing_spec_single_source.py` AST scan).
- C6 KEPT count UNCHANGED at 12 (target population only; no new contract).
- TW-7c-3 firing uses TripwireLedgerEntry from 7c.0a; writes to sprint-status.yaml::tripwire_events (consume the schema, don't re-derive).
- K-target 1.4× ≈ ~3.5K LOC ceiling. Estimate ~2.0-3.0K LOC.
- R-tier R3 (full broad regression).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_base_shape.py tests/parity/test_class_conformance_validator_extension.py tests/structural/test_import_linter_c6_target_list_populated.py tests/structural/test_tw_7c_3_firing_spec_single_source.py tests/parametrized_harness/test_operator_verdict_harness_consumable.py tests/integration/manifest/test_compiler_honors_new_gate_codes.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R3 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/_base.py app/parity/contracts/ app/manifest/compiler.py scripts/utilities/validate_parity_test_class_conformance.py tests/schemas/operator_verdict/ tests/parity/test_decision_card_base_shape.py tests/parity/test_class_conformance_validator_extension.py tests/structural/test_import_linter_c6_target_list_populated.py tests/structural/test_tw_7c_3_firing_spec_single_source.py tests/parametrized_harness/ tests/integration/manifest/
```

Expected:
- All focused/structural tests PASS.
- R3 broad regression: failure count UNCHANGED (T1 baseline; ~39 known checkout-level).
- Class-conformance ≥11.
- Lint-imports 12 KEPT.
- Sandbox-AC PASS.
- Ruff clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-4b.ready-for-review.md`. Include D1-D8 compliance table per decision; verification battery; broad-regression delta; T1 decisions documented.

T11: Claude cross-agent MANDATORY review. Verifies D1-D8 line-by-line. Verdict at `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-NN.md`.

## Boundary

HALT on: predecessor not done; D1-D8 deviation (surface as decision_needed BEFORE completing); broad-regression failure count > T1 baseline; lint-imports KEPT ≠ 12; class-conformance < 11; alias_of validator accepts invalid family-ID; LOCKSTEP_CHECK re-derived in any per-gate test (would fail AMEND-7d-i).

DO NOT touch: 7c.0a/0b/3a/3b/4a deliverables (read-only); C4/C5 forbidden_modules; existing test logic outside the 7c.3b reshape decision.

DO NOT introduce: new third-party deps; defensive serial markers; mocked DecisionCardBase; YAML serialization (keep canonicalization JSON for parity with 7c.3b's compute_model_digest).
```

---

## Operator dispatch checklist

1. ☐ 7c.0b + 7c.4a `done` (verified post-7c.4a-close commit `12fb0f2`).
2. ☐ Sandbox-AC validator PASS on spec.
3. ☐ AMELIA-P2 freshness check.
4. ☐ Governance JSON entry current.
5. ☐ Sprint-status: `migration-7c-4b-gate-family-foundation-implementation: ready-for-dev`.
6. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice.
2. Claude T11 cross-agent MANDATORY review (~30-40 min; layered Blind/Edge/Auditor; D1-D8 verification).
3. Apply remediation cycles per HALT-AND-REMEDIATE.
4. Commit + flip done.
5. At 7c.4b close, **8 per-gate stories 7c.5.G0..G6 unblock** (4 fresh-author + 4 extend-and-audit per AMEND-5).
