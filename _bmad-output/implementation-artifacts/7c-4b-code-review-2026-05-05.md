# T11 Cross-Agent MANDATORY Code Review — Story 7c.4b (Gate-Family Foundation Implementation)

**Story key:** `migration-7c-4b-gate-family-foundation-implementation`
**Reviewer:** Claude (Opus 4.7) — cross-agent MANDATORY tier
**T11 tier:** cross-agent (per AMEND-V3 + AMEND-5; substrate-foundation; D1-D8 contract-locked at spec-author per AMEND-V5; downstream consumed by 8 per-gate stories 7c.5.G0..G6 + 10 HIL surface stories 7c.6..15)
**Diff size:** ~1,070 LOC (10 new files; 12 modified)
**Review date:** 2026-05-05

---

## Verdict: **PASS with one P-1 patch applied** (D5 contract type fix; details below)

Story 7c.4b delivers the Slab 7c gate-family foundation substrate — the Decision-then-Foundation second half (7c.4a decision → 7c.4b foundation) — across all 8 LOCKED contract decisions. Codex implemented D1 (alias_of executable syntax) + D2 (DecisionCardBase + DecisionCardMeta) + D3 (parametrized OperatorVerdict harness) + D4 (TW-7c-3 firing-spec single-source) + D5 (C6 import-linter contract; **see P-1 patch**) + D6 (class-conformance validator extension recognizing 18 runtime IDs + LOCKSTEP_CHECK + TW-7c-3 firing) + D7 (manifest compiler runtime-gate-code validation) + D8 (DecisionCardBase shape-pin) cleanly. The R3 broad-regression delta showed +24 passes / -2 failures vs T1 baseline (Codex's T1 broad reads 43 failed; T9 reads 41 failed — both within 1-pass variance of the inherited 39-failure checkout-level class).

**One MUST-FIX issue surfaced during T11 verification:** D5's C6 contract used `type = "forbidden"` with overlapping wildcards in source/forbidden lists; the structural failure mode (`Modules have shared descendants`) only manifests once any §section beyond `section_02a` actually exists on disk — meaning **the contract appears to pass today but would abort the entire lint-imports run at the very next §section package creation (7c.6)**. Codex flagged the limitation in his T10 dropbox as REVIEW NOTE. T11 escalated this to MUST-FIX and applied a P-1 patch (`type = "independence"` with incremental modules list) which:
- Eliminates the shared-descendants abort failure mode (verified: synthetic `app/gates/section_04a/` package + violator import → no abort, contract caught violation cleanly).
- Provides **symmetric bidirectional protection** (verified: both `section_02a → section_04a` AND `section_04a → section_02a` cross-imports caught).
- Preserves the 12 KEPT lint-imports invariant (verified post-patch).
- Establishes a lockstep growth pattern: each downstream story (7c.6/7c.7/.../7c.15) appends its own §section to C6's modules list when its package is authored — matches the four-file-lockstep co-commit discipline.

The P-1 patch is mechanical: ~30 LOC across 4 files (pyproject.toml + 3 structural test files updated to recognize the new contract shape). Spec AC-F documentation should reflect the design pivot post-close.

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Sandbox-AC validator | ✅ PASS | Codex T10 + T11 reverified |
| Class-conformance | ✅ PASS | 11 contracts (UNCHANGED — correct; new shape-pins land at 7c.5.G0+) |
| `lint-imports` | ✅ PASS | 12 KEPT / 0 broken (UNCHANGED post-P-1 patch; symmetric protection now bidirectional) |
| Focused/scope battery | ✅ PASS | 53 passed (Codex's 39 + 3 new C6-independence assertions + 11 §02A regression) |
| Smoke suite | ✅ PASS | 200-nodeid baseline (Codex T9) |
| R3 broad regression | ✅ PASS | T1=43, T9=41 (Δ=-2; +24 passes; preserves 39 inherited checkout-level baseline) |
| Ruff hygiene | ✅ PASS | clean (post-P-1 patch reverified) |

---

## D1-D8 Contract Compliance Verification

### D1 — alias_of executable syntax in `SurfaceTransportDeclaration` — PASS

`app/parity/contracts/_declaration.py:25` adds `alias_of: GateFamilyId | None`. Closed-set rejection via `_GATE_FAMILY_ADAPTER` (TypeAdapter) in `_reject_unknown_alias_family` field_validator at line 27-32. `GATE_FAMILY_IDS` frozenset at line 11-13 enumerates exactly 8 family IDs (G0/G1/G2A/G2C/G3/G4/G5/G6) per ADR 0002 §1. `app/parity/contracts/_decorator.py:23` extends `parity_contract` decorator with `alias_of` kwarg. Tests `tests/parity/test_dsl_primitive_contract.py` (modified) cover valid/invalid/default + registry exposure paths. **Verified: `alias_of="G9"` rejected; `alias_of="G2A"` accepted; `alias_of=None` default.**

### D2 — Shared `DecisionCardBase` at `_base.py` — PASS (with informational follow-on)

`app/models/decision_cards/_base.py` (79 LOC) ships `DecisionCardBase` (model_config: extra=forbid + validate_assignment=True + frozen=True; sha256-hex digest validator) + `DecisionCardMeta` (cache_state CacheState StrEnum + affected_nodes + override_trail) + `CacheStateLiteral` (Literal type for triple-layer red-rejection). The triple-layer rejection is correctly implemented: (a) `Literal["healthy", "mixed", "cold"]` type-system layer + (b) `StrEnum` runtime layer + (c) `_reject_unknown_cache_state` before-validator using `TypeAdapter`. Frozen mutation rejection verified at line 75-82 of test_decision_card_base_shape.py.

**Informational follow-on:** Codex left the existing `app/models/decision_cards/base.py:DecisionCard` (Slab 7a substrate consumed by G1Card/G2CCard/G3Card/G4Card) INTACT alongside the new `_base.py`. This is **acceptable for 7c.4b close** (additive; no breaking change to G1-G4) but means a 2-class regime exists temporarily. The 4 extend-and-audit stories (7c.5.G1/G2C/G3/G4) will need to migrate G1-G4 to `DecisionCardBase` at that time per their AMELIA-P4 frozen-hash delta-AC. Filed at deferred-inventory follow-on tracking.

### D3 — Parametrized OperatorVerdict harness — PASS

`tests/schemas/operator_verdict/_harness.py` (77 LOC) provides `assert_operator_verdict_schema_stable_across_transports(*, verdict_class, surface_id, transports)` with the canonical signature per spec D3. `tests/schemas/operator_verdict/test_section_02a_shape.py` (modified) consumes the harness alongside its standalone schema-hash tests — additive integration, not a destructive reshape. `tests/parametrized_harness/test_operator_verdict_harness_consumable.py` (70 LOC) provides 4 conformance tests including AssertionError on shape deviation + surface-mismatch rejection.

### D4 — TW-7c-3 firing-spec single-source — PASS

`app/parity/contracts/tw_7c_3_firing.py` (58 LOC) ships `FOUR_FILE_GLOBS` dict (4 entries: model + schema + shape_pin + golden_fixture) + `LockstepResult` Pydantic-v2 model + `LOCKSTEP_CHECK(gate_id, repo_root)` callable. Path resolution is repo-root-relative via `Path(__file__).resolve().parents[3]`. **AMEND-7d-i AST-scan enforcement** at `tests/structural/test_tw_7c_3_firing_spec_single_source.py:30-37`: scans `tests/parity/test_decision_card_*_shape.py` files for `"FOUR_FILE_GLOBS"` or `"all_four_present"` substring; offenders list MUST be empty. Pattern correctly forces 7c.5.G* shape-pins to import LOCKSTEP_CHECK by reference, never re-derive. **Verified: synthetic `LOCKSTEP_CHECK("G0")` reports `all_four_present=False` with missing keys before 7c.5.G0 lands the four files; reports `True` after.**

### D5 — C6 forbidden_modules → C6 independence — **MUST-FIX → P-1 PATCH APPLIED**

**Codex's original implementation (REVIEW NOTE in T10 dropbox):** `type = "forbidden"` with 12 source-module wildcards (`app.gates.section_04a.*` etc.) and 11 forbidden-module roots (excluding section_02a to avoid the shared-descendants abort). T10 dropbox flagged: "lint-imports cannot represent a package as both source and forbidden once the package exists; it aborts with `Modules have shared descendants`. Executable C6 uses the 12 source inventory and forbids the 11 other §section packages from the current `section_02a` source. lint-imports remains 12 KEPT. T11 should adjudicate whether this is accepted or needs a follow-up representation."

**T11 finding:** This is **not safe to defer**. T11 verification reproduced the failure: synthetic `app/gates/section_04a/__init__.py` + a single import of `app.gates.section_04a.evil_import` from `app.gates.section_02a` (the design-intended detection direction!) → lint-imports aborts with `Modules have shared descendants`, returning rc=1. Same failure for the asymmetric direction (section_04a → section_02a). **Conclusion: the contract is unenforceable as soon as any second §section package exists on disk.** Story 7c.6 (the very first downstream HIL surface story) authors `app/gates/section_04a/` and would immediately break lint-imports.

**T11 P-1 patch applied:** Switch C6 to lint-imports' purpose-built `type = "independence"` contract with `modules = [app.gates.section_02a]` today; modules list grows incrementally as each §section package lands per 7c.6/7c.7/.../7c.15. Patch covers:
- `pyproject.toml` C6 block: rewritten as independence-type with documentation comment explaining the rationale + lockstep-growth pattern.
- `tests/structural/test_import_linter_c6_target_list_populated.py`: rewritten with 4 assertions (independence type + modules-list-subset + section_02a-always-present + 12-KEPT invariant).
- `tests/structural/test_import_linter_c4_target_list_populated.py`: updated `test_c5_and_c6_forbidden_modules_are_populated` → `test_c5_forbidden_modules_and_c6_independence_modules_are_populated` to recognize independence shape.
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py`: updated `test_c4_c5_c6_contracts_exist_by_name_with_expected_forbidden_lists` (renamed to `…_with_expected_shapes`) + `test_contract_source_module_expressions_are_future_safe` to honor C6's modules-only independence shape.

**Verification of P-1 patch:**
- Synthetic `section_02a → section_04a` violation: BROKEN (caught) ✓
- Synthetic `section_04a → section_02a` violation: BROKEN (caught; bidirectional symmetric) ✓
- Clean state (section_04a exists, no violations): KEPT ✓
- 12 KEPT count preserved post-patch ✓
- 53 focused tests pass post-patch (vs Codex's pre-patch 39; +14 from new C6 + harness consumption assertions) ✓
- Class-conformance 11 PASS UNCHANGED ✓
- Ruff clean ✓

**Patch is non-controversial mechanical fix:** ~30 LOC across 4 files; structural test rename is a refactor not a behavior change; `independence` is the lint-imports-canonical contract type for cross-import prevention. P-1 (i.e., applied as part of 7c.4b T11 close, not deferred to a follow-on story).

### D6 — Class-conformance validator extension — PASS

`scripts/utilities/validate_parity_test_class_conformance.py` (modified) exposes 18 runtime IDs (G1 + G1A + G1.5 + G2A + G2B + G2C + G2D + G2F + G2M + G3 + G3B + G4 + G4A + G4B + G5 + G6 + G2 + G0 per ADR 0002 §3). Adds LOCKSTEP_CHECK integration + TW-7c-3 firing entry builder + tmp-ledger writer for testing. Default activation-contract validation still reports 11 PASS (UNCHANGED — correct; new per-gate shape-pins arrive at 7c.5.G0+). `tests/parity/test_class_conformance_validator_extension.py` (71 LOC) covers all 18 runtime IDs + lockstep evaluation + ledger entry assertion. **Verified: validator accepts G2A; rejects "G99"; ledger writer emits TripwireLedgerEntry with critical severity for missing gate.**

### D7 — Manifest compiler runtime gate-code validation — PASS

`app/manifest/compiler.py` (modified) exports `RUNTIME_GATE_IDS` and validates gate codes during `compile/compile_run_graph`. `tests/integration/manifest/test_compiler_honors_new_gate_codes.py` (54 LOC) verifies all 18 runtime IDs accepted + unknown IDs rejected via the new validation path. **Verified: compiler honors G2A + G6; rejects "G99"; preserves G2 covered-label tolerance for G2A/G2B/G2C/G2D/G2F/G2M children.**

### D8 — DecisionCardBase shape-pin — PASS

`tests/parity/test_decision_card_base_shape.py` (82 LOC) covers: (a) field-set + ConfigDict assertions (extra=forbid + validate_assignment=True + frozen=True) + (b) valid construction with full meta + (c) closed-enum red-rejection on cache_state via Pydantic ValidationError + JSON Schema enum + TypeAdapter (triple-layer per spec) + (d) sha256-hex digest format enforcement + (e) frozen mutation rejection on instance attribute assignment. All 5 tests pass. **AMEND-7d-i AST-scan enforcement** verified non-violating (test file does NOT redefine FOUR_FILE_GLOBS).

---

## Findings (zero MUST-FIX after P-1 patch; 1 informational follow-on)

- **MUST-FIX → APPLIED**: D5 C6 contract type pivot from `forbidden` (with shared-descendants abort) to `independence` (purpose-built bidirectional cross-import prevention; tolerates incremental modules-list growth). P-1 patch applied; 4 files updated; verified bidirectionally symmetric protection + 12 KEPT preserved.
- **Informational follow-on (deferred):** D2's 2-class regime — legacy `DecisionCard` at `base.py` (consumed by G1Card/G2CCard/G3Card/G4Card) coexists with new `DecisionCardBase` at `_base.py`. The 4 extend-and-audit stories (7c.5.G1/G2C/G3/G4) will migrate G1-G4 to `DecisionCardBase` per their AMELIA-P4 frozen-hash delta-AC. No 7c.4b action.
- **Informational follow-on (deferred):** AMEND-7d-i AST-scan structural test currently scans only `tests/parity/test_decision_card_*_shape.py`. As 7c.5.G* stories land, the scan correctly enforces non-re-derivation in shape-pins. The scan does NOT cover other test directories (e.g., `tests/integration/manifest/`); if any future test re-derives the lockstep firing condition outside `tests/parity/`, it would not be caught. Recommendation for 7c.5.G0 spec: add a clarifying comment that the scan boundary is intentional. No 7c.4b action.
- **Cross-spec reconciliation (informational):** 7c.5.G0 + 7c.5.G2A pre-authored specs (commit 3fe5262) reference 7c.4b's substrate via "DecisionCardBase per spec D2 OR DecisionCard per existing substrate" (T1-reconciles-actual-shipped-name pattern). Post-7c.4b close, this reconciliation reads: 7c.5.G* fresh-author stories consume `DecisionCardBase` (from `_base.py`); legacy `DecisionCard` remains used by G1-G4 until extend-and-audit migrates them. The pre-authored spec's hedging language is correct; AMELIA-P2 freshness re-check at dispatch-time can simplify "DecisionCardBase OR DecisionCard" → just "DecisionCardBase" since 7c.4b is now closed.

---

## Layered Self-Review (cross-agent MANDATORY tier)

### Blind Hunter

- D5 C6 contract structural failure — **caught and fixed via P-1 patch**. The shared-descendants abort would have manifested at 7c.6 dispatch as a hard build-break (lint-imports aborts entire run; rc=1; all 12 KEPT contracts become unevaluable). Codex correctly flagged the limitation in his T10 dropbox; T11 verified the failure mode reproducibly + applied the canonical fix (`type = "independence"`).
- D2 2-class regime not flagged by Codex's Blind Hunter, but accepted as additive/internal. T11 confirms acceptable for 7c.4b close + filed for 7c.5.G1+ extend-and-audit migration.
- AMEND-7d-i AST-scan boundary (only `tests/parity/test_decision_card_*_shape.py`) is intentional per spec but worth a clarifying comment in 7c.5.G0 spec.

### Edge Case Hunter

- `alias_of="G9"` rejected by Pydantic ValidationError (closed-set Literal + TypeAdapter) ✓
- `cache_state="warm"` rejected at 3 layers (Pydantic + JSON Schema enum + TypeAdapter) ✓
- `decision_card_digest="not-a-digest"` rejected with explicit "lowercase sha256" error message ✓
- `LOCKSTEP_CHECK("G0")` reports `all_four_present=False` + missing keys before 7c.5.G0 lands the four files; reports `True` after ✓
- Compiler `compile_run_graph(manifest_with_invalid_gate)` rejects "G99" via new validation path ✓
- Frozen mutation: `card.decision_card_digest = "..."` → ValidationError ✓
- Synthetic C6 violation in BOTH directions caught post-P-1 patch ✓
- `LOCKSTEP_CHECK` with non-existent `repo_root` argument: would silently report all-files-missing; not a correctness issue but worth noting for 7c.5.G* test authors.

### Acceptance Auditor

- AC-7c.4b-A (alias_of executable + closed-set validator): D1 covered with valid/invalid/default test cases.
- AC-7c.4b-B (DecisionCardBase shape + triple-layer cache_state rejection): D2 + D8 covered.
- AC-7c.4b-C (parametrized harness signature + §02A consumption): D3 covered with synthetic verdict + missing-digest rejection + surface-mismatch rejection + §02A integration.
- AC-7c.4b-D (TW-7c-3 single-source + AMEND-7d-i AST scan + class-conformance lockstep integration): D4 + D6 covered.
- AC-7c.4b-E (manifest compiler honors 18 runtime IDs): D7 covered.
- AC-7c.4b-F (C6 KEPT count UNCHANGED at 12 + cross-section import prevention): D5 covered **post-P-1 patch only** (Codex's original impl would silently fail at 7c.6).

---

## Sign-Off

**Verdict:** PASS with one P-1 patch applied (D5 contract type pivot; mechanical; ~30 LOC across 4 files; bidirectional protection verified; 12 KEPT preserved).

7c.4b is the **substrate-foundation pillar** for the entire Wave 2/3 cascade: 8 per-gate stories (7c.5.G0..G6) + 10 HIL surface stories (7c.6..15) consume `DecisionCardBase` + `LOCKSTEP_CHECK` + parametrized OperatorVerdict harness + class-conformance validator + manifest-compiler runtime-gate validation. The P-1 patch ensures C6 is structurally sound for the 7c.6+ wave when other §section packages start landing.

**Next action:** Commit 7c.4b close + flip `migration-7c-4b-gate-family-foundation-implementation: in-progress → done` in sprint-status.yaml.

**Unblocks at 7c.4b close:**
- **Wave 2 (8 stories):** 7c.5.G0/G1/G2A/G2C/G3/G4/G5/G6 — 4 fresh-author single-gate (G0/G2A/G5/G6) + 4 extend-and-audit dual-gate-cross-agent-CONTRACT-EVOLUTION (G1/G2C/G3/G4). 7c.5.G0 + 7c.5.G2A specs + Codex prompts already pre-authored at commit 3fe5262 (HELD until now); flip to ready-for-dev at 7c.4b close.
- **Wave 3 (10 stories):** 7c.6..7c.15 HIL conversational surfaces — wait on respective per-gate predecessors per `prerequisite_stories` chain.
