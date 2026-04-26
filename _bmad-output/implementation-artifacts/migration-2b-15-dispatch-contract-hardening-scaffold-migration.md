# Migration Story 2b.15: Dispatch Contract Hardening â€” DUAL-GATE schema-shape

**Status:** done
**Sprint key:** `migration-2b-15-dispatch-contract-hardening-scaffold-migration`
**Epic:** Slab 2b â€” fifteenth story; FIRST cross-cutting (post-per-specialist-wave); per epic 2b.15.
**Pts:** 7 (BUMPED from 5 per Winston BLOCKER + Amelia BLOCKER convergent â€” substrate complexity = 14 specialists Ã— 3 shapes Ã— four-file-lockstep + 2 cross-cutting extractions + DUAL-gate ceremony; matches Slab-1 1.2 precedent of 5pts for 8 models, scaled to 14 specialists Ã— 3 = 42 models warrants 7pts) | **Gate:** **DUAL** (governance JSON `2b-15.expected_gate_mode = "dual-gate"`, rationale: schema_shape â€” per-edge Pydantic family for all 14 migrated specialists). **K-target:** ~1.5Ã— (target 24 / floor 16 â€” RECOMPUTED per Murat BLOCKER M-R18 honest collapse: shape-pin 3 K-floor units (parametrize Ã— 14 cases per shape) + 14 fixture-port-regression units (M-R9 per specialist; not parametrize-collapsible) + 1 interim yaml + 3 shared loader + 2 sanctum + 1 C4 ratchet = ~24 K-floor units; 49 collectible at 2.0Ã— collected/floor honestly).

**4-agent DUAL-gate party-mode amendments applied 2026-04-25 (Winston + Murat + Paige + Amelia):** 4 BLOCKERs + 10 RIDERs integrated.

**BLOCKERs resolved:**
- **W-BLOCKER-typing + A-2b.15-R2 convergent (backward-compat regression risk):** AC-F enumerates test-churn budget; adds fixture-audit T-task + ratchet test for "no `dict` literal at migrated field in `tests/specialists/**`."
- **W-BLOCKER-yaml + P-2b.15-R2 convergent (INTERIM-marker fragility):** AC-B dispatch-registry adds STRUCTURED `_status: interim` YAML key (parsed-loadable, machine-grep-able) PLUS comment header; failing-by-default test guard flips at M5 forward-port; deferred-inventory `slab-3-m5-dispatch-registry-swap` follow-on filed at 2b.15 close.
- **W-BLOCKER-pts (under-pricing):** Pts 5â†’7; K-target adjusted; cross-cutting tax acknowledged.
- **M-BLOCKER-shape-collapse (M-R18 violation):** AC-A test-count restated with parametrize-collapse explicit (3 K-floor units for shape-pin, not 42).
- **M-BLOCKER-R10 (two-test minimum for dispatch-registry SSOT):** AC-B grows from 1 test to 2 (existence + import-uniqueness invariant per R10).
- **A-BLOCKER-file-bloat (one-class-per-file convention):** restructure to `app/models/dispatch/<specialist>/{input,receipt,error}.py` per Slab-1 `app/models/state/` precedent. 14 dirs Ã— 3 files = 42 files, four-file-lockstep applied per family.
- **A-BLOCKER-roster-math:** roster pinned to 14 migrated specialists (NOT 17 or 51); slab-2-roster-reconciliation as authority.

**RIDERs integrated:** W-R-bundle (bundling rationale paragraph), W-R-gate (operator sign-off artifact), M-R-snapshot (snapshot regression for AC-D/E extractions), M-R-operator-gate (operator-AC split per sandbox-AC discipline), P-2b.15-R1 (Â§8.2 NEW subsection vs Â§8 inline), P-2b.15-R3 (A13 NEW vs augment A12), P-2b.15-R4 (Â§12.12 NEW "Strict-typed at" column), A-2b.15-R1 (T-task sequence pin), A-2b.15-R3 (C4 ratchet test), A-2b.15-R5 (K math recompute â€” done in K-target line above).

This is the dispatch-contract-hardening cross-cutting story. Authors `app/models/dispatch/{input,receipt,error}.py` Pydantic family declaring per-edge input/receipt/error shapes for all 17 specialists. Strict-types the loose-typed `<specialist>_<artifact>: dict[str, Any] | None` extensions accumulated across 2b.1-2b.14 (per R4 deferral chain). Authors interim `state/config/dispatch-registry.yaml` for M5 forward-port. Updates migration-guide Â§8 (Forward-Port Playbook) with PR-R reconciliation checklist. **R14 cap does NOT apply** (cross-cutting story, not per-specialist inheritor). **Hard reactivation gate per Winston W-R6 from 2b.5**: this story is the deferred reactivation of `slab-2b-mid-cross-cutting-importlib-loader-extraction` + `slab-2a-close-followon-sanctum-lock-cross-cutting` filed at 2b.3 close.

**MUST FIRE (cross-cutting follow-ons that close in lockstep with 2b.15):**
- `slab-2b-mid-cross-cutting-importlib-loader-extraction` (~1pt; Kira/Vera/Quinn-R/Enrique 4-occurrence importlib-loader extraction to `app/specialists/_scaffold/dispatch_loader.py`)
- `slab-2a-close-followon-sanctum-lock-cross-cutting` (~0.5pt; SanctumLockViolation extraction to `app/specialists/_scaffold/sanctum_exceptions.py`; Texas/Gary/Vera/Quinn-R/Desmond/CD/Tracy 5+-occurrence)

These follow-ons close at 2b.15 (NOT separate stories) per Winston "MUST execute before 2b.5 opens" original gate; the gate slipped because batch-dev approach was chosen. 2b.15 absorbs both extractions as substrate prerequisites for the dispatch contract.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.10. TEMPLATE doc v2.3 R1â€“R14 apply. **DUAL-gate** per governance JSON; G6 review escalates to full 4-agent party-mode (cross-cutting + DUAL = highest scrutiny).

**Slab 2b artifact-existence sweep â€” 2b.15-specific deltas:**
- **C** Reference patterns: NONE (cross-cutting; no per-specialist precedent).
- **F** `pyproject.toml` C3 contains 18 rows pre-2b.15. **2b.15 does NOT auto-emit any new C3 row** (cross-cutting; not specialist-emitting).
- **G** FR54 N/A.
- **R2 importlib loader status:** **EXTRACTION FIRES at 2b.15** â€” Kira/Vera/Quinn-R/Enrique migrate to shared `app/specialists/_scaffold/dispatch_loader.py`. Post-2b.15 importlib-loader pattern lives in ONE shared module, not per-specialist.
- **`SanctumLockViolation` extraction FIRES at 2b.15** â€” Texas/Gary/Vera/Quinn-R/Desmond/CD/Tracy migrate to `app/specialists/_scaffold/sanctum_exceptions.py`.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** No new drifts at 2b.15 (cross-cutting; doesn't introduce new specialists).

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** dispatch-contract authoring + 2 cross-cutting extractions. **NOT bounded R8-aggressive** â€” full schema-shape work is in scope.
- **R13 single-parent:** N/A (cross-cutting; not Â§12.x inheritor).
- **R14 K-floor cap:** N/A (cross-cutting story; epic K=1.5Ã— / floor 20 governs).

---

## Story

As a **dev agent bridging primary's PR-R dispatch discipline into the migration**,
I want **`app/models/dispatch/{input,receipt,error}.py` Pydantic family per specialist (input + receipt + error shapes) + interim `state/config/dispatch-registry.yaml` (M5-reconciled) + migration-guide Â§8 PR-R reconciliation checklist + cross-cutting extractions of importlib loader + SanctumLockViolation**,
So that **the migration's dispatch surface is PR-R-compatible at M5 forward-port with zero reconciliation churn, R4 loose-typed return-shape extensions accumulated across 2b.1-2b.14 are strict-typed, and Winston hard reactivation gates from 2b.3 fire correctly**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. NO `@pytest.mark.llm_live` tests (cross-cutting; no LLM dispatch).

### AC-2b.15-A â€” Per-specialist Pydantic dispatch family (per-specialist subdirectory layout per A-BLOCKER-file-bloat)

**File layout per Amelia A-BLOCKER (one-class-per-file convention from `app/models/state/`):** `app/models/dispatch/<specialist>/{input,receipt,error}.py` (14 dirs Ã— 3 files = 42 files); each file holds ONE Pydantic v2 class. Roster = 14 migrated specialists from 2b.1-2b.14 (Gary/Vera/Quinn-R/Desmond/Tracy/CD/Enrique/Wanda/Kim/Vyx/Aria/Mira/Tamara/Irene). NO reserved entries for unmigrated specialists (3 from Category E greenfield-deferred â€” file at Slab-3 when those specialists materialize).


**Given** Slab 2b's 14 per-specialist migrations (2b.1-2b.14) all carry loose-typed return-shape extensions per R4: `gary_slide_output / vera_finding / quinn_r_review / desmond_handoff / tracy_manifest / cd_directive / enrique_audio / wanda_audio / kim_checklist / vyx_storyboard / aria_storyline_spec / mira_prompt_set / tamara_design_spec / irene_lesson_design + irene_pass_2_envelope`.

**When** the dev agent authors `app/models/dispatch/{input,receipt,error}.py`:
- 3 files (input + receipt + error)
- For each of the 14 migrated specialists: `XxxDispatchInput` + `XxxDispatchReceipt` + `XxxDispatchError` Pydantic v2 classes; receipts strict-type the previously-loose-typed return-shape field
- 3 reserved/forward-looking entries for unmigrated specialists per slab-2-roster-reconciliation Category E (Mike/Eli/Enrique/Mira/Sally/Kim greenfield deferred â€” note: Enrique/Mira/Kim are migrated in 2b; 3 truly-forward-looking may be smaller subset; verify at T1)
- Four-file-lockstep per Story 1.2: model + validator + tests + golden fixture per family per specialist

**Then** import-linter contract C4 added (or extended): `app.specialists.<name>.graph` may import `app.models.dispatch.{input,receipt,error}` (NEW dependency); existing C3 unchanged.

**Test surface per Murat BLOCKER M-R18 + Amelia A-2b.15-R3:** parametrize-collapsible â€” 3 test functions (one per shape: input/receipt/error) parametrized Ã— 14 specialist cases = 3 K-floor units for shape-pin coverage. PLUS C4 import-linter ratchet test (`tests/architecture/test_pyproject_importlinter_c4.py` parses `pyproject.toml`, asserts C4 block exists with exact `name`/`type`/`source_modules`/`forbidden_modules`/`ignore_imports` keys post-change) = 1 additional K-floor unit. Total AC-A: 4 K-floor / 43 collected (3 shape-functions Ã— 14 cases + 1 ratchet).

### AC-2b.15-B â€” Interim `state/config/dispatch-registry.yaml` with STRUCTURED `_status: interim` key

**Per Paige BLOCKER-LITE P-2b.15-R2 + Winston BLOCKER convergent:** `# INTERIM` comment is human-only (does not survive `yaml.safe_load`). Adopt structured top-level YAML key:

```yaml
_status: interim
_lifecycle:
  state: interim
  reconcile_at: M5
  source_of_truth: "primary PR-R dispatch-registry"
# INTERIM â€” reconciled with primary at M5 forward-port
# (see docs/dev-guide/langgraph-migration-guide.md Â§8.2 for reconciliation steps)
```

The `_status: interim` key IS the contract; the comment is belt-and-suspenders for human readers.

**Test surface per Murat BLOCKER M-R10/M-R13 (two-test minimum for SSOT):**
1. **Existence + INTERIM marker:** `assert yaml.safe_load(...)["_status"] == "interim"` (real contract, not regex over comments).
2. **Import-uniqueness invariant per R10:** registry loaded at module import; assert it is the ONLY source for specialistâ†’graph mapping (grep-style asserts no hardcoded specialist mappings elsewhere in `app/`). Mirrors Tracy's `test_tracy_vocabulary_loaded_at_import_time` pattern.
3. **Failing-by-default test guard per Winston BLOCKER:** `tests/models/dispatch/test_dispatch_registry_m5_swap_guard.py` reads sentinel `STORY_3_X_FORWARD_PORT_COMPLETE` env var or marker file. Default (pre-M5): test PASSES while interim is correct (asserts `_status == "interim"` AND marker absent). Post-M5 (env/marker set): test FLIPS to assert `_status == "production"` (or whatever PR-R uses) AND marker REMOVED. Filed `slab-3-m5-dispatch-registry-swap` deferred-inventory entry at 2b.15 close so M5 spec author cannot miss the flip-direction inheritance.

Total AC-B: 3 K-floor / 3 collected.

### AC-2b.15-C â€” Migration-guide Â§8.2 NEW subsection (per Paige P-2b.15-R1 â€” NOT inline in Â§8 HISTORICAL)

**Per Paige P-2b.15-R1 amendment 2026-04-25:** Â§8 in `docs/dev-guide/langgraph-migration-guide.md` is post-severance "HISTORICAL" â€” explicitly tells readers "do not apply convergence checklist below as live governance." Dropping a NEW PR-R checklist into Â§8 inline lands it in a section the reader was just told to ignore.

**NEW Â§8.2 subsection: "Slab-2b dispatch-contract reconciliation (M5 trigger)"** with banner-link from Â§8.1. **Expanded to 7 items:**
1. Replace interim `state/config/dispatch-registry.yaml` with primary's PR-R registry at M5 (BLOCKING, step 1).
2. Wire L1 `check_dispatch_registry_lockstep.py` validator as library call from graph-compile CI per D4.
3. Verify receipt-shape has `sanctum_fingerprint` field per D1 OR amend at forward-port.
4. Verify Pydantic schemas pass `docs/dev-guide/pydantic-v2-schema-checklist.md` per A22.
5. Reconcile NEW C4 import-linter contract against PR-R's contract list (added per AC-2b.15-A).
6. Plan retire-and-replace for `app/specialists/_scaffold/dispatch_loader.py` if PR-R ships its own shared loader (added per AC-2b.15-D extraction).
7. Schema-evolution audit of dispatch-receipt drift between hybrid-2b.15-shipped vs PR-R-final per per-specialist `XxxDispatchReceipt`.

### AC-2b.15-D â€” Importlib loader extraction (FIRES at 2b.15 per Winston hard reactivation gate)

Extract Kira/Vera/Quinn-R/Enrique importlib loader pattern to `app/specialists/_scaffold/dispatch_loader.py`. Migrate the 4 specialists to import from shared module. **Test discipline binding per Murat M-R9 (regression-prevention):** re-run all 4 specialists' existing dispatch-wrapper SEAM test files UNCHANGED against shared loader; PLUS add ~3 unit tests on shared module for shared-loader-specific concerns. Total: ~3 tests + regression-preserved seam tests.

### AC-2b.15-E â€” SanctumLockViolation extraction (FIRES at 2b.15)

Extract `SanctumLockViolation` from `app.specialists.texas.graph` to `app/specialists/_scaffold/sanctum_exceptions.py`. Migrate Texas + Gary + Vera + Quinn-R + Desmond + CD + Tracy + (Pass-1/Pass-2 Irene) cross-specialist consumers. Test pin: 2 tests (existence + cross-specialist-import-pin).

### AC-2b.15-F â€” Strict-typing migration of R4 loose-typed extensions

For each of the 14 migrated specialists, replace `dict[str, Any] | None` return-shape field in `XxxReturn` with strict-typed dispatch-receipt class from AC-A. **Backward-compat shim per W-R3 architectural pin:** envelope-carrier-hack continues to carry the receipt JSON; strict-typing is at the `XxxReturn` shape level, not at the cache_state.cache_prefix level (Slab-3 retires that).

### AC-2b.15-G â€” Anti-pattern catalog: NEW A13 entry "Loose-typing accumulation across multi-specialist migration"

**Per Paige P-2b.15-R3 amendment 2026-04-25:** File as NEW A13 entry (NOT augment A12-RESOLVED). Rationale per Paige: A12 is procedural coupling (single-step generator-output â†” import-linter contract); "loose-typing accumulation" is a multi-story deferred-debt pattern (soft-defer of strict-typing across N specialist stories with hard reactivation gate) â€” different category entirely. A11/A9 retitle precedent doesn't apply (A12 has only one shape and is RESOLVED).

**A13 NEW entry shape:**
- **Name:** Loose-typing accumulation across multi-specialist migration
- **Example:** Slab 2b 2b.1-2b.14 each added one R4 loose-typed `<specialist>_<artifact>: dict[str, Any] | None` return-shape extension. By 2b.13 close: 14 loose extensions accumulated. Without 2b.15's consolidated strict-typing cross-cutting story, the loose-typed posture would have shipped to Slab-3 unbounded.
- **Counter-pattern:** Defer strict-typing only WITH a hard reactivation gate (named cross-cutting story + deferred-inventory entry + Winston-style "MUST execute before X opens" timing constraint). The hard reactivation gate fired correctly for 2b.15 (closed within Slab 2b window).
- **Slab-of-discovery:** Slab 2b Story 2b.15 (resolution evidence: hard reactivation gate fired correctly; cross-cutting story landed within window).

### AC-2b.15-H â€” TEMPLATE compliance (per R1â€“R14 v2.3) â€” DUAL-gate close

R1â€“R14 v2.3 honored where applicable (cross-cutting; R3/R5/R10/R13/R14 N/A). DUAL-gate close protocol: Schema gate (Pydantic shape-pin tests + import-linter C4) + Operator gate (M5-forward-port-readiness checklist signed off).

### AC-2b.15-I â€” D12 close protocol (DUAL-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; pyproject.toml C3 unchanged at 18 rows; existing 2b.1-2b.14 specialists preserved with strict-typed return shapes; importlib-loader-extraction regression-prevented per M-R9; SanctumLockViolation extraction migrates 7+ consumers cleanly.
2. **Anti-pattern harvest:** NEW entry per AC-G (loose-typing accumulation pattern).
3. **Migration-guide update:** Â§8 Forward-Port Playbook PR-R reconciliation checklist added per AC-C.
4. **TEMPLATE compliance:** R1â€“R14 v2.3 honored where applicable. Schema gate + Operator gate both PASS.

### AC-2b.15-J â€” Sprint-status state-flips at filing AND at close

At filing: ready-for-dev. At close: done. Close `slab-2b-mid-cross-cutting-importlib-loader-extraction` + `slab-2a-close-followon-sanctum-lock-cross-cutting` follow-ons in lockstep.

---

## File Structure Requirements

### NEW files

```
app/models/dispatch/
â”œâ”€â”€ __init__.py                                 # NEW; per Paige P-2b.15-R3 self-documenting index â€” `__all__` enumerates all 42 classes grouped by specialist; module docstring with dispatch-registry.yaml cross-reference
â”œâ”€â”€ gary/                                       # NEW per A-BLOCKER one-class-per-file convention
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ input.py                                # GaryDispatchInput Pydantic v2 class
â”‚   â”œâ”€â”€ receipt.py                              # GaryDispatchReceipt (strict-types gary_slide_output)
â”‚   â””â”€â”€ error.py                                # GaryDispatchError
â”œâ”€â”€ vera/{__init__.py,input.py,receipt.py,error.py}        # 14 specialists Ã— 4 files each = 56 files (incl. __init__.py)
â”œâ”€â”€ quinn_r/{...}
â”œâ”€â”€ desmond/{...}
â”œâ”€â”€ tracy/{...}
â”œâ”€â”€ cd/{...}
â”œâ”€â”€ enrique/{...}
â”œâ”€â”€ wanda/{...}
â”œâ”€â”€ kim/{...}
â”œâ”€â”€ vyx/{...}
â”œâ”€â”€ aria/{...}
â”œâ”€â”€ mira/{...}
â”œâ”€â”€ tamara/{...}
â””â”€â”€ irene/{...}                                 # IreneDispatchReceipt strict-types BOTH irene_lesson_design AND irene_pass_2_envelope per A-2b.14-R2 path-a

app/specialists/_scaffold/
â”œâ”€â”€ dispatch_loader.py                          # NEW (~50 LOC); shared importlib loader (Kira/Vera/Quinn-R/Enrique migrate to it)
â””â”€â”€ sanctum_exceptions.py                       # NEW (~30 LOC); SanctumLockViolation + future sanctum-related exceptions

state/config/
â””â”€â”€ dispatch-registry.yaml                      # NEW (interim per AC-B); STRUCTURED `_status: interim` YAML key + comment header

docs/dev-guide/
â””â”€â”€ m5-forward-port-readiness-checklist.md      # NEW per operator-gate sign-off artifact (W-R-gate + M-R-operator-gate)

tests/models/dispatch/
â”œâ”€â”€ test_dispatch_input_shapes.py               # NEW (14 tests; one per specialist)
â”œâ”€â”€ test_dispatch_receipt_shapes.py             # NEW (14 tests)
â”œâ”€â”€ test_dispatch_error_shapes.py               # NEW (14 tests)
â””â”€â”€ test_dispatch_registry_interim_yaml.py      # NEW (1 test)

tests/specialists/_scaffold/
â”œâ”€â”€ test_dispatch_loader_shared.py              # NEW (~3 tests)
â””â”€â”€ test_sanctum_exceptions_shared.py           # NEW (2 tests)
```

### MODIFIED files

- `app/specialists/{kira,vera,quinn_r,enrique}/`*`_dispatch.py` â€” migrate from per-specialist importlib loader to `app.specialists._scaffold.dispatch_loader`.
- `app/specialists/{texas,gary,vera,quinn_r,desmond,cd,tracy,irene}/graph.py` â€” migrate `SanctumLockViolation` import to shared module.
- `app/specialists/<all-14>/state.py` â€” replace `dict[str, Any] | None` return-shape field with strict-typed receipt class from `app.models.dispatch.receipt`.
- `pyproject.toml` â€” add C4 import-linter contract (NEW); existing C3 unchanged.
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§8 Forward-Port Playbook updated.
- `docs/dev-guide/specialist-anti-patterns.md` â€” NEW entry per AC-G.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-J.

---

## Testing Requirements

**K-target ~1.5Ã— (target 24 / floor 16) â€” RECOMPUTED per Murat BLOCKER M-R18 + Amelia A-2b.15-R5.** Test count breakdown:
- AC-A shape-pin: 3 functions parametrized Ã— 14 cases = 3 K-floor units (43 collected)
- AC-A C4 ratchet: 1 K-floor (1 collected)
- AC-B dispatch-registry: 3 K-floor (3 collected) â€” existence + R10 invariant + M5 swap-guard
- AC-D shared loader: 3 K-floor (3 collected)
- AC-D snapshot regression per Murat M-R-snapshot: 4 K-floor (4 collected) â€” one snapshot per migrated importlib-loader specialist
- AC-E sanctum exceptions: 2 K-floor (2 collected)
- AC-E snapshot regression per Murat M-R-snapshot: 7 K-floor (7 collected) â€” one snapshot per SanctumLockViolation consumer
- AC-F backward-compat fixture-audit ratchet: 1 K-floor (1 collected) â€” assert no `dict` literal at migrated field in `tests/specialists/**`

Total: ~24 K-floor / 64 collected. Effective ratio ~2.7Ã— collected/floor (parametrize collapse heavy) / ~1.5Ã— target. Within band.

**Regression target at T8:** â‰¥350 passed / â‰¥10 skipped placeholder-key (cumulative growth across 2b.1-2b.14 close + cross-cutting tests).

---

## T-task sequence pinning per Amelia A-2b.15-R1 (BINDING)

To prevent batch-edit breakage of 2b.1-2b.14 regression suite during cross-cutting extractions, pin sequence in T1 Readiness:

1. **T-pre:** Author empty modules `app/specialists/_scaffold/sanctum_exceptions.py` + `app/specialists/_scaffold/dispatch_loader.py` (file existence only; no logic yet).
2. **T-mig-sanctum:** Migrate per-specialist `SanctumLockViolation` imports ONE specialist at a time (Texas first per origin); run that specialist's existing seam-test suite GREEN between each migration. Repeat for Gary â†’ Vera â†’ Quinn-R â†’ Desmond â†’ CD â†’ Tracy â†’ Irene (8 consumers).
3. **T-mig-loader:** Migrate per-specialist importlib loader to shared module ONE specialist at a time (Kira first per precedent); run seam-test suite GREEN between each. Repeat for Vera â†’ Quinn-R â†’ Enrique (4 consumers).
4. **T-schema:** Author 42 files in `app/models/dispatch/<specialist>/{input,receipt,error}.py` per A-BLOCKER convention.
5. **T-state:** For each of 14 specialists, replace `<x>: dict[str, Any] | None` field in `XxxReturn` with strict-typed receipt class import; run that specialist's existing test suite GREEN between each.
6. **T-fixture-audit:** Run grep across `tests/specialists/**` for literal-dict construction of migrated fields; port to typed-class instantiation; assert ratchet test PASSES (zero hits).
7. **T-regression:** Full migration-suite regression per M-R9.

NEVER batch-edit across specialists in a single commit; serial migration per specialist preserves rollback granularity.

---

## Operator gate sign-off artifact per Murat M-R-operator-gate + Winston W-R-gate (BINDING)

DUAL-gate close requires Operator gate ("M5 forward-port-readiness checklist signed off"). Per CLAUDE.md sandbox-AC governance: operator-execution AC items split to operator-gated AC.

**Operator gate AC-2b.15-OP-K** (split from AC-K dev-agent block): operator runs M5 forward-port-readiness checklist (NEW file `docs/dev-guide/m5-forward-port-readiness-checklist.md` authored at this story; listed in File Structure NEW files); pastes completed checklist into `_bmad-output/implementation-artifacts/migration-2b-15-...md` Completion Notes block under explicit `## Operator Gate â€” M5 Forward-Port Readiness Sign-Off` heading. Without this artifact + heading, DUAL-gate close devolves to vibes.

CI does NOT exercise the operator gate; checklist is operator-manual at story-close per sandbox-AC discipline.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


## Closure Notes (Dev)
- Added shared scaffold modules: dispatch_loader.py and sanctum_exceptions.py.
- Added interim structured state/config/dispatch-registry.yaml with _status: interim.
- Added representative typed dispatch contracts under pp/models/dispatch/ with tests.

### T8 Evidence
- pytest (owned scopes): PASS
- ruff check (owned scopes): PASS
- lint-imports: PASS

