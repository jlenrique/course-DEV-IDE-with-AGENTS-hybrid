# M5 Forward-Port Readiness Checklist

**Purpose:** operator sign-off artifact for the Slab-2b dispatch-contract DUAL-gate close per Story 2b.15 AC-2b.15-OP-K + Winston W-R-gate + Murat M-R-operator-gate amendments. The Schema gate (AC-A through AC-F per Story 2b.15) is verified by automated tests; this Operator gate captures the cross-slab readiness items no test can prove until M5 actually runs.

**Authored at:** Story 2b.15 close (Slab 2b dispatch-contract-hardening structural completion).
**Sign-off ledger:** operator pastes the completed checklist into the Completion Notes block of `_bmad-output/implementation-artifacts/migration-2b-15-dispatch-contract-hardening-scaffold-migration.md` under an explicit `## Operator Gate — M5 Forward-Port Readiness Sign-Off` heading. CI does NOT exercise the operator gate; checklist is operator-manual at story-close per CLAUDE.md sandbox-AC discipline.

---

## §8.2 PR-R Reconciliation Checklist (M5 trigger)

Per Story 2b.15 AC-C (Paige P-2b.15-R1 NEW §8.2 subsection — NOT inline §8 HISTORICAL). Seven items, BLOCKING in step order:

- [ ] **(1) Replace interim `state/config/dispatch-registry.yaml` with primary's PR-R registry at M5.** BLOCKING step 1. The `_status: interim` structured key + `_lifecycle.reconcile_at: M5` mark the swap target. Set sentinel env `STORY_3_X_FORWARD_PORT_COMPLETE=1` after swap so `tests/integration/scaffold_conformance/test_dispatch_contract_hardening.py::test_dispatch_registry_m5_swap_guard` flips assertion direction (asserts `_status` removed). Without the swap, the failing-by-default test guard correctly remains pre-M5 GREEN; post-M5 the env-var flip becomes mandatory.
- [ ] **(2) Wire L1 `check_dispatch_registry_lockstep.py` validator as library call from graph-compile CI per D4.** Validator must run on every graph-compile; failure breaks CI. Slab-3 inherits from primary's PR-R toolchain.
- [ ] **(3) Verify receipt-shape has `sanctum_fingerprint` field per D1 OR amend at forward-port.** D1 sanctum-hybrid invariant requires every dispatch receipt to carry a sanctum fingerprint for tamper-evidence. Audit each `app/models/dispatch/<specialist>/receipt.py` post-M5; if PR-R adds the field, migrate the Pydantic class additively (don't break existing call-sites that don't yet supply it).
- [ ] **(4) Verify Pydantic schemas pass `docs/dev-guide/pydantic-v2-schema-checklist.md` per A22.** Run the 14-idiom checklist against each of the 42 dispatch classes (14 specialists × 3 shapes). Triple-layer red-rejection on any closed enum; `validate_assignment=True` already pinned at story-author time; timezone-aware datetimes if any temporal fields land at M5; UUID4 validation if any identifier fields land at M5.
- [ ] **(5) Reconcile NEW C4 import-linter contract against PR-R's contract list (per Story 2b.15 AC-A).** C4 directs `app.specialists.<name>.graph` MAY import `app.models.dispatch.{input,receipt,error}` (NEW dependency). PR-R may define its own contracts; verify no conflicts; merge contract lists if needed.
- [ ] **(6) Plan retire-and-replace for `app/specialists/_scaffold/dispatch_loader.py` if PR-R ships its own shared loader (added per Story 2b.15 AC-D extraction).** The Slab-2b extraction migrated Kira/Vera/Quinn-R/Enrique to the shared loader. If PR-R provides an equivalent, retire the Slab-2b version + migrate the four specialists to PR-R's module. Same disposition for `app/specialists/_scaffold/sanctum_exceptions.py` (Story 2b.15 AC-E extraction; Texas/Gary/Vera/Quinn-R/Desmond/CD/Tracy/Irene 8-consumer base).
- [ ] **(7) Schema-evolution audit of dispatch-receipt drift between hybrid-2b.15-shipped vs PR-R-final.** For each of the 14 strict-typed receipt fields (`gary_slide_output / vera_finding / quinn_r_review / desmond_handoff / tracy_manifest / cd_directive / enrique_audio / wanda_audio / kim_checklist / vyx_storyboard / aria_storyline_spec / mira_prompt_set / tamara_design_spec / irene_lesson_design + irene_pass_2_envelope`), compare against PR-R's strict-typed shape; resolve any divergence by migrating hybrid receipt to PR-R shape (PR-R is authoritative at M5).

---

## Operator sign-off block (paste into Completion Notes)

```markdown
## Operator Gate — M5 Forward-Port Readiness Sign-Off

**Story:** 2b.15 dispatch-contract-hardening
**Operator:** {operator_name}
**Date:** {YYYY-MM-DD}
**Outcome:** {SIGNED-OFF | DEFERRED-PENDING-PR-R-LANDING | BLOCKED}

**Checklist evidence:**
- (1) Registry swap: {PASS | DEFERRED | NOT-APPLICABLE-PRE-M5}
- (2) L1 validator wiring: {PASS | DEFERRED}
- (3) sanctum_fingerprint receipt audit: {PASS | DEFERRED | AMENDED-AT-M5}
- (4) pydantic-v2-schema-checklist: {PASS | DEFERRED}
- (5) C4 contract reconciliation: {PASS | DEFERRED}
- (6) Shared loader + sanctum_exceptions retire-and-replace plan: {DOCUMENTED | NOT-NEEDED-PR-R-COMPATIBLE}
- (7) Schema-evolution audit (14 receipts): {PASS | DRIFT-FOUND-MIGRATING}

**Notes:** {free-form operator commentary}
```

---

## Pre-M5 vs Post-M5 disposition

**Pre-M5 (current state at Story 2b.15 close 2026-04-25):**
- Schema gate: PASS (all 42 dispatch classes shipped; per-specialist tests parametrize-collapsed; C4 contract added).
- Operator gate: SIGNED-OFF as DEFERRED-PENDING-PR-R-LANDING. None of items (1)–(7) can be executed without PR-R artifacts on hybrid; the deferred-inventory entry `slab-3-m5-dispatch-registry-swap` carries the inheritance gate.

**Post-M5 (when PR-R lands on hybrid via forward-port):**
- M5 forward-port story author reads this checklist as T1 reading; executes items (1)–(7) in order; pastes filled-in checklist into THAT story's Completion Notes (NOT this story's, which is already closed); flips test-guard sentinel env var.

---

## Cross-references

- Story 2b.15 spec: [`_bmad-output/implementation-artifacts/migration-2b-15-dispatch-contract-hardening-scaffold-migration.md`](../../_bmad-output/implementation-artifacts/migration-2b-15-dispatch-contract-hardening-scaffold-migration.md)
- §8.2 in migration guide: [`docs/dev-guide/langgraph-migration-guide.md`](langgraph-migration-guide.md) (cascade-renumber pending — interim placement may be `§8.2` directly OR appended depending on slab-2b retrospective doc-restructure)
- Pydantic v2 schema checklist: [`docs/dev-guide/pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md)
- Sandbox-AC governance: CLAUDE.md `## LangChain/LangGraph migration — sandbox-AC + gate-mode governance`
- Deferred-inventory entry: `slab-3-m5-dispatch-registry-swap` in `_bmad-output/planning-artifacts/deferred-inventory.md`
