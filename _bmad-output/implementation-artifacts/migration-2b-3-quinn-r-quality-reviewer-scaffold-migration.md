# Migration Story 2b.3: Migrate Quinn-R (Quality Reviewer) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2b-3-quinn-r-quality-reviewer-scaffold-migration`
**Epic:** Slab 2b — third per-specialist migration; second inheritor of 2b.1 Gary TEMPLATE; **TRIGGERS R2 IMPORTLIB-LOADER EXTRACTION** (Quinn-R is the THIRD occurrence of importlib loader after Kira + Vera).
**Pts:** 4 | **Gate:** single (per governance JSON `2b-3.expected_gate_mode = "single-gate"`, rationale: "Follows 2b.1 TEMPLATE"). **K-target:** ~1.5× (target 17 / floor 12; +1 over original 16 to absorb Murat M-R7 cross-wrapper coordination test + Amelia A-R3 gate_phase invalid-value test).

**3-agent party-mode amendments applied 2026-04-25 (Winston + Murat + Amelia):** 1 BLOCKER + 8 APPLY riders integrated — W-R1 factor `_act` into dispatcher (≤40) + per-branch helpers (≤60 each) NOT lift to 130; W-R2 + A-R4 + A-R5 SPLIT SanctumLockViolation extraction into separate follow-on from loader extraction; M-R7 add cross-wrapper coordination test; M-R8 dimension-failure secondary-tag (8 dimensions); M-R9 binds future R2 extraction story to regression-prevention test discipline; **A-R2 BLOCKER: `skills/quality-control/` has NO `__init__.py` + hyphenated dirname; quality_control_dispatch.py MUST use importlib loader (parallel to Vera A-R8 — same blocker class)**; A-R3 inline `gate_phase` Literal validation in `_act` with negative test; A-R6 add `tests/specialists/quinn_r/conftest.py` + template-doc R2-activation audit bullet; A-R7 D12 4th line "R2 EXTRACTION FILED, NOT EXECUTED" + numeric anchors. Quality-control scripts verified to have `if __name__ == "__main__":` guards (importlib-safe).

Quinn-R is **LLM+tool-dispatch** (§12.6 inheritor like Vera) with **two dispatch wrappers** (sensory-bridges + quality-control deterministic checks) and a **two-pass branchable act** (pre-composition vs post-composition gate). Quinn-R adds ONE row to §12.12 inheritor catalog matrix under §12.6 parent (per R3) AND triggers **R2 third-occurrence extraction** of the importlib loader pattern: Kira (`_load_target_module` for kling) + Vera (sensory_bridges_dispatch importlib loader) + Quinn-R (sensory_bridges_dispatch importlib loader + quality_control_dispatch importlib loader) = three independent occurrences of the same loader sub-mechanism.

---

## T1 Readiness Block

Standing Pre-Flight items 1–10 same as 2b.2 (TEMPLATE inheritor pattern). Item 11: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1, R1–R7 apply.

### Slab 2b artifact-existence sweep — Quinn-R-specific deltas

- **C** Reference patterns: Vera 2b.2 (LLM+tool-dispatch inheritor closest precedent; single dispatch wrapper); Kira 2a.3 (LLM+tool-dispatch original; importlib loader sub-mechanism source).
- **F** `pyproject.toml` C3 contains 7 rows pre-Quinn-R (5 baseline + Gary at 2b.1 close + Vera at 2b.2 close). Quinn-R auto-emit makes 8.
- **G** Cache-hit-rate: same disposition as Vera — per-artifact prompts; no stable prefix; no harness at 2b.3.
- **NEW R2 extraction surface (third importlib-loader occurrence):** at T1, dev agent decides whether to (a) inline both dispatch wrappers in Quinn-R AND queue extraction as a 2b.x-mid-slab cross-cutting story, OR (b) extract immediately to `app/specialists/_scaffold/dispatch_loader.py` (or similar) at 2b.3 close as part of D12 protocol. **Default: option (a)** — don't expand 2b.3 scope; queue extraction as `slab-2b-mid-cross-cutting-importlib-loader-extraction` (~1pt single-gate) targeting 2b.4 close. Document choice in T1 Readiness.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 — Sanctum/sidecar contract (A11 FOURTH example):** skill-dir `bmad-agent-quality-reviewer`, runtime persona `quinn-r`, sidecar `_bmad/memory/quinn-r-sidecar/` (legacy). BMB sanctum at `_bmad/memory/bmad-agent-quality-reviewer/` likely absent (graceful-degrade). Same A11 class. Harvest at AC-J.

**Drift #2 — Model tier "Quality Guardian" framing (A10 FIFTH example):** Quinn-R SKILL.md describes calibration-learning + 8-dimension review; selection_policy has `reasoning / fast / code` only. Maps to `tier_request: reasoning` → `gpt-5.4`. Harvest at AC-J.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1):** Quinn-R SKILL.md describes calibration-learning, two-pass model (pre-composition + post-composition), 8 quality dimensions. Migration scope: the headless dispatch path Marcus invokes at quality gates. Calibration-learning is a memory sidecar concern, OUT OF SCOPE. **Two-pass branchable act IS in scope** — Quinn-R's `_act` accepts a `gate_phase: "pre-composition" | "post-composition"` envelope field and branches dispatch accordingly (single specialist, branchable behavior, NOT two specialists). Document branch logic in `_act`; pin both branches in test surface.

**Decision #2 — Two dispatch wrappers, BOTH importlib loader (per Amelia A-R2 BLOCKER amendment 2026-04-25):** Quinn-R dispatches to (i) `sensory-bridges` for non-text artifact perception (PNG/audio/video; importlib-loader wrapper PARALLEL to Vera 2b.2's `sensory_bridges_dispatch.py`); (ii) `quality-control` skill for deterministic checks. **Verified at story-author time:** `skills/quality-control/` has NO `__init__.py` at package root AND NO `__init__.py` in `scripts/`; hyphenated dirname blocks direct package import (same A-R8 failure mode as sensory-bridges). All five quality-control scripts (`precomposition_validator.py`, `accessibility_checker.py`, `brand_validator.py`, `quality_logger.py`, `visual_fill_validator.py`) DO have `if __name__ == "__main__":` guards — importlib loading IS safe. **Decision (per R2 sub-mechanism rule):** use **importlib loader pattern** for BOTH dispatch wrappers. The `quality_control_dispatch.py` wrapper exposes Quinn-R-specific signatures internally calling per-script entrypoints (`validate(...)` from precomposition_validator, `check_accessibility(...)` from accessibility_checker, etc.). Triggers R2 third-occurrence extraction at this story (Kira + Vera + Quinn-R = 3 importlib loader occurrences) — see Decision #3.

**Decision #3 — R2 third-occurrence extraction triggered + filed as TWO separate follow-ons (per Winston W-R2 + Amelia A-R4/A-R5 amendments 2026-04-25):** Kira + Vera + Quinn-R = 3 importlib-loader occurrences. Per R2: "extraction at THIRD occurrence." Quinn-R IS the third (Quinn-R uses TWO importlib loaders so it's effectively occurrences 3 + 4 in this story alone). **Extraction work owed but DEFERRED to TWO separate cross-cutting stories** (W-R2 + A-R4 + A-R5 convergence: bundling loader + SanctumLockViolation extractions is wrong — different layers, different test surfaces, different rollback profiles):

1. `slab-2b-mid-cross-cutting-importlib-loader-extraction` (~1pt single-gate) — extract Kira/Vera/Quinn-R loader pattern to `app/specialists/_scaffold/dispatch_loader.py`. Test discipline per Murat M-R9 binding (regression-prevention: re-run all three specialists' existing dispatch-wrapper SEAM test files unchanged against the shared loader; THEN add ~3 unit tests on shared module). Filed at 2b.3 close per AC-J.
2. `slab-2b-mid-cross-cutting-sanctum-exception-extraction` (~0.5pt single-gate) — extract `SanctumLockViolation` from `app.specialists.texas.graph` to `app/specialists/_scaffold/sanctum_exceptions.py` (or similar); migrate Texas + Gary + Vera + Quinn-R to import from shared module. **Note:** the existing deferred-inventory entry `slab-2a-close-followon-sanctum-lock-cross-cutting` already covers this — at 2b.3 close, that entry's status flips to "ready-for-dev" with the new module-path naming.

**Decision #4 — Sensory-bridges importlib loader SAME wrapper module as Vera:** Quinn-R uses `app/specialists/quinn_r/sensory_bridges_dispatch.py` (per-specialist module) inheriting Vera's pattern. R2 extraction at Decision #3 unifies the per-specialist modules; until then, Quinn-R's module is a near-copy of Vera's.

**Decision #5 — `_act` factoring per Winston W-R1 (NOT lift to 130 LOC):** instead of one fat 130-LOC `_act`, factor into thin dispatcher (≤40 LOC) + per-branch handlers `_act_precomposition` (≤60 LOC) + `_act_postcomposition` (≤60 LOC). Same single-specialist shape, branchable contract from outside, per-branch testability inside. Inheritor norm `_act ≤ 115 LOC` preserved for the dispatcher pattern; per-branch helpers each have own LOC ceiling. Branchable design demands per-branch *bodies*, not a fatter shared body.

---

## Story

As a **migration dev agent inheriting the 2b.1 TEMPLATE**,
I want **Quinn-R (Quality Guardian) rehomed into `app/specialists/quinn_r/` with the 9-node scaffold + LLM+tool-dispatch act-body that branches on `gate_phase` (pre-composition / post-composition), wraps two dispatch substrates (sensory-bridges + quality-control), per-R5 auto-emit C3 row positive regression test, §12.12 inheritor row added under §12.6 parent, AND triggers R2 third-occurrence importlib-loader extraction filing**,
So that **the LLM+tool-dispatch category survives a heavier surface (dual dispatch + branchable act), the per-specialist migration cadence proves that inheritor stories can absorb edge-case complexity without escalating gate mode, and the importlib-loader extraction work is queued at exactly the threshold R2 names**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Quinn-R carries ONE `@pytest.mark.llm_live` test (AC-B live LLM evaluation against fixture artifacts).

### AC-2b.3-A — Generator emits Quinn-R + auto-emits C3 row (per R5)

Per R5 + 2b.1 hermetic pattern. Test pin: `tests/specialists/quinn_r/test_quinn_r_generator_auto_emit_c3_row.py` — 3 tests using `temp_repo_root` fixture. Pre-baseline 5 → post-emit 6 (in fixture); live repo at story close = 8 rows total.

Generator invocation:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name quinn_r --mcp none --expertise-tier L4-quality-review \
  --from-skill skills/bmad-agent-quality-reviewer
```

**Naming note:** `quinn_r` (snake_case for Python identifier; runtime persona "Quinn-R"). Confirm at T1 the generator accepts hyphenated-OR-snake_case names; if hyphen-only, generate as `quinnr` (no separator) and document the choice. Likely snake_case per Python module-name convention.

### AC-2b.3-B — Quinn-R `act` node wires LLM+tool-dispatch with TWO wrappers + branchable gate-phase

- **Given** Quinn-R's `_act` accepts envelope payload with `gate_phase: "pre-composition" | "post-composition"`; branches dispatch accordingly:
  - **Pre-composition branch:** dispatch to `quality_control_dispatch.run_precomposition_validators(artifact_paths)` (wraps `precomposition_validator.py` + `accessibility_checker.py`); LLM evaluation against L1 contracts + 8 quality dimensions; produces structured Quality Review Report (QRR) with dimension scores + severity-tagged findings.
  - **Post-composition branch:** dispatch to `sensory_bridges_dispatch.dispatch_to_sensory_bridges(artifact_path, modality)` for non-text artifact perception (mirrors Vera 2b.2 wrapper) AND `quality_control_dispatch.run_postcomposition_validators(artifact_path)` for deterministic checks; LLM evaluation; produces QRR.
- **When** the dev agent implements `_act` per the LLM+tool-dispatch + branchable pattern.
- **Then** invoking `build_quinn_r_graph()` with a fixture envelope (one for each gate_phase; both monkey-patched dispatch) produces non-empty results containing `quinn_r_review` (the QRR) + provenance metadata. **NO `@pytest.mark.llm_live` marker on the deterministic shape tests** (3 deterministic + 1 live).
- **LOC budget per Winston W-R1 (factored design — NOT lift to 130):** `_act` thin dispatcher ≤40 LOC; `_act_precomposition` ≤60 LOC; `_act_postcomposition` ≤60 LOC; `_parse_qrr` helper extracted module-level (per Vera A-R9 option-b precedent) so 6-branch parametrize matrix targets the helper, not `_act` branches. Both dispatch wrappers ≤75 LOC each. **Inheritor norm `_act` ≤115 LOC preserved** (dispatcher is naturally smaller than the inheritor `_act` body).
- **`gate_phase` validation pinning per Amelia A-R3:** envelope is loose-typed `dict[str, Any]` per R4. `_act` dispatcher validates inline at top: `gate_phase = payload.get("gate_phase"); if gate_phase not in ("pre-composition", "post-composition"): raise ValueError(f"unknown gate_phase: {gate_phase!r}")`. Test pin: ONE additional negative test in `test_quinn_r_act_node_dispatch.py` for invalid `gate_phase` → ValueError.
- **Tag namespace per Murat M-R2 convention + M-R8 dimension secondary-tag:** `qrr.parsed.*` — tags `qrr.parsed.ok / malformed / missing-key / wrong-type / empty / dimension-failure:{dimension}` where `{dimension}` ∈ `{accessibility | brand | learning | instructional | intent | content | audio | composition}` (8 sub-tags via inner parametrize per M-R8 Option A). The 6-case parametrize matrix in `_parse_qrr` test stays at 6 file-level test functions (parametrize-collapse per `story-cycle-efficiency.md §1`); the dimension-failure case has 8 sub-cases via inner parametrize.
- **Branch coverage:** 2 happy-path tests (one per `gate_phase`) + 6 parse-branches (with M-R8 sub-parametrize on dimension-failure) + 1 negative `gate_phase` test (A-R3) + 1 cross-wrapper coordination test (M-R7) + 1 @llm_live = **11 tests in `test_quinn_r_act_node_dispatch.py`**. Both branches assert two-sided trail-tag per Murat M5.
- **Cross-wrapper coordination test per Murat M-R7:** post-comp branch invokes BOTH sensory-bridges AND quality-control wrappers in sequence. Test asserts independent failure modes: if sensory-bridges raises ImportError, quality-control still attempts AND `_act` returns a structured-degraded QRR with `dimension_scores: {sensory: SKIPPED}` rather than crashing. Belongs in `_act_node_dispatch.py` (orchestration concern), not in the per-wrapper SEAM file.

### AC-2b.3-B-OP — Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Quinn-R against a real Marcus-staged quality gate (one quality-gate evaluation; ~2000 tokens; both pre-comp and post-comp passes if available). Pastes QRR + LLM cost into Completion Notes.

### AC-2b.3-C — Model cascade at `_plan` (per R7)

Trail-entry resolution at `_plan` per R7. Quinn-R DOES invoke LLM at `_act` (LLM+tool-dispatch). Test pin: 2 tests.

### AC-2b.3-D — Sanctum cold-read (graceful-degrade per R5+R6)

Same shape as Vera 2b.2. PERSONA.md sentinel skip per A-R5. Imports `SanctumLockViolation` from `app.specialists.texas.graph` (3rd cross-specialist import; **note the pattern** — this is THIRD occurrence of cross-specialist exception import, parallel to importlib loader. Fold into the R2 extraction follow-on filed at AC-J: extract `SanctumLockViolation` to shared module alongside the loader extraction.). Test pin: 3 tests.

### AC-2b.3-E — Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.3-F — Resolution trail (FR16 sixth per-specialist exercise)

1 test.

### AC-2b.3-G — Quinn-R shape-pin tests (per R4)

Per R4 (one new field, loose-typed): `quinn_r_review: dict[str, Any] | None`. The QRR carries dimension scores + severity-tagged findings + calibration-adjustment notes. 4 tests.

### AC-2b.3-H — Scaffold-conformance test registered

`tests/integration/scaffold_conformance/test_scaffold_quinn_r.py` — 1 test.

### AC-2b.3-I — Migration-guide §12.12 grows ONE inheritor row (per R3) + framing-sentence updated

Per R3, NEW row in §12.12:

| Specialist | Parent §12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Quinn-R | §12.6 (Kira LLM+tool-dispatch) | TWO dispatch wrappers (sensory-bridges importlib loader + quality-control sub-mechanism per T1 verification); branchable `_act` on `gate_phase` (pre-comp / post-comp) | graceful-degrade (BMB sanctum unpopulated) | A10 5th example (`reasoning`-tier mapping) + A11 4th example (sidecar contract divergence) + R2 third-occurrence extraction trigger | 2b.3 |

Update §12.5 framing sentence: "sixth specialist proven on 9-node scaffold; four established categories; LLM+tool-dispatch category now hosts 3 inhabitants (Kira / Vera / Quinn-R) and triggered R2 importlib-loader extraction at Quinn-R landing." Tag-namespace artifact-noun convention reaffirmed (`bundle.parsed.*` Texas; `receipt.parsed.*` Gary; `ftr.parsed.*` Vera; `qrr.parsed.*` Quinn-R).

### AC-2b.3-J — Anti-pattern catalog harvest + R2 extraction TWO-follow-on filing (per W-R2 + A-R4 + A-R5)

- **A10 fifth example bullet:** Quinn-R `tier_request` "Quality Guardian" not in selection_policy; maps to `reasoning` → `gpt-5.4`.
- **A11 fourth example bullet:** Quinn-R skill-dir `bmad-agent-quality-reviewer` vs runtime persona `quinn-r`; SKILL.md activation reads `quinn-r-sidecar`. Same shape.
- **R2 third-occurrence extraction filed as TWO SEPARATE follow-ons (per Winston W-R2 + Amelia A-R4/A-R5):**
  1. `slab-2b-mid-cross-cutting-importlib-loader-extraction` (~1pt single-gate, NEW deferred-inventory entry) — extract Kira/Vera/Quinn-R importlib loader pattern to `app/specialists/_scaffold/dispatch_loader.py`. **Test discipline binding per Murat M-R9:** at the extraction story, (1) migrate Kira/Vera/Quinn-R to shared loader; (2) re-run all three specialists' existing dispatch-wrapper SEAM test files UNCHANGED (they must pass against shared loader — regression-prevention contract); (3) THEN add ~3 unit tests on shared module for shared-loader-specific concerns. Hard reactivation gate per Winston caveat: "MUST execute before 2b.5 opens" to prevent indefinite slip + substrate-rot. Spec-author for 2b.4 reads this entry at T1.
  2. `slab-2a-close-followon-sanctum-lock-cross-cutting` (existing deferred-inventory entry line 77) flips status from "Slab-2-cross-cutting hygiene queued" to "ready-for-dev" at 2b.3 close — Texas + Gary + Vera + Quinn-R = 4 occurrences; threshold met. Extract `SanctumLockViolation` from `app.specialists.texas.graph` to `app/specialists/_scaffold/sanctum_exceptions.py` (or similar); migrate the four specialists to import from shared module. ~0.5pt single-gate. **Bundling with loader extraction is wrong per W-R2 + A-R4 + A-R5** — different layers (dispatch vs sanctum), different test surfaces, different rollback profiles. Separate stories.
- **Calibration-learning follow-on per Winston PASS-with-note:** add `quinn-r-calibration-learning-memory-sidecar-integration` entry to `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons with reactivation gate "opens when memory-sidecar architecture story lands in Slab-3+." Honors CLAUDE.md §Deferred-inventory governance point 3 (every spec naming a follow-on adds it to inventory).

### AC-2b.3-K — TEMPLATE compliance (per R1–R7)

R1–R7 honored. **Documented deviation:** R2 third-occurrence extraction is TRIGGERED at this story (loader pattern). Per R2: "filed as cross-cutting story (NOT scope creep into per-specialist migration)." This story files the cross-cutting work but does NOT execute it. AC-J handles the filing.

### AC-2b.3-L — D12 close protocol (single-gate; FOUR-line per A-R7 + Amelia A2b3-R7 explicit literal anchors)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired correctly (C3 list grows 7→8 rows in live repo).
2. **Anti-pattern harvest:** A10 5th + A11 4th + TWO R2 extraction follow-ons filed (loader + sanctum-exception, separate per W-R2) + calibration-learning entry filed in inventory per Winston note.
3. **Migration-guide update:** §12.12 inheritor row added under §12.6 parent; framing sentence updated; tag-namespace `qrr.parsed.*` documented.
4. **TEMPLATE compliance: R1–R7 honored; R2 EXTRACTION FILED, NOT EXECUTED.** Numeric anchors: `_act` dispatcher LOC measured (≤40 ceiling per W-R1); per-branch `_act_precomposition`/`_act_postcomposition` LOC measured (≤60 each); both dispatch wrappers LOC measured (≤75 each); `_parse_qrr` helper LOC measured; 11 tests in `test_quinn_r_act_node_dispatch.py` (2 happy-path branches + 6 parse-branches with M-R8 dimension sub-parametrize + 1 negative gate_phase + 1 cross-wrapper coordination + 1 @llm_live); sanctum graceful-degrade case; **loader-occurrences pre-2b.3 = 2 (Kira + Vera); post-2b.3 = 3 + sensory-bridges = 4 (extraction trigger met TWICE in this story); shared-utility migration deferred to `slab-2b-mid-cross-cutting-importlib-loader-extraction` story; SanctumLockViolation extraction deferred to existing `slab-2a-close-followon-sanctum-lock-cross-cutting` story now flipped to ready-for-dev**.

### AC-2b.3-M — Sprint-status state-flips at filing AND at close

At filing: `migration-2b-3-quinn-r-quality-reviewer-scaffold-migration: ready-for-dev`. At close: flip to `done`; epic stays `in-progress`. Also at close: file `slab-2b-mid-cross-cutting-importlib-loader-extraction` as `backlog` per AC-J.

---

## File Structure Requirements

### NEW files

```
app/specialists/quinn_r/
├── __init__.py                                 # generator-emitted
├── graph.py                                    # generator-emitted; _act body filled at T2 (LLM+tool-dispatch + branchable)
├── state.py                                    # generator-emitted; QuinnRReturn extended with quinn_r_review
├── model_config.yaml                           # generator-emitted; reasoning-tier comments
├── sensory_bridges_dispatch.py                 # NEW (~50-75 LOC); importlib loader (Vera-pattern copy until R2 extraction)
├── quality_control_dispatch.py                 # NEW (~50-75 LOC); direct-package-import OR importlib loader per T1 verification
├── expertise/
│   ├── README.md                               # generator-emitted; dotted reference table for 5 Quinn-R refs
│   └── __init__.py

tests/specialists/quinn_r/
├── __init__.py                                 # NEW (empty marker per A-R6)
├── conftest.py                                 # NEW per Amelia A2b3-R6 if helper fixtures needed beyond temp_repo_root; verify at T1 — strike if not needed
├── test_quinn_r_generator_auto_emit_c3_row.py  # NEW (3 tests; AC-A)
├── test_quinn_r_act_node_dispatch.py           # NEW (11 tests per W-R1 + M-R7 + M-R8 + A-R3; AC-B with 6 parse-branches + dimension sub-parametrize + 2 happy-path branch tests + 1 negative gate_phase + 1 cross-wrapper coordination + 1 @llm_live)
├── test_quinn_r_dispatch_wrappers.py           # NEW (6 tests; AC-B SEAM differences for BOTH wrappers — 3 each; both importlib loader pattern per A-R2 BLOCKER resolution)
├── test_quinn_r_model_cascade.py               # NEW (2 tests; AC-C)
├── test_quinn_r_sanctum_cold_read.py           # NEW (3 tests; AC-D)
├── test_quinn_r_gate_decision_binding.py       # NEW (2 tests; AC-E)
├── test_quinn_r_resolution_trail.py            # NEW (1 test; AC-F)
└── test_quinn_r_state_shape.py                 # NEW (4 tests; AC-G)

tests/integration/scaffold_conformance/
└── test_scaffold_quinn_r.py                    # NEW (1 test; AC-H)

tests/fixtures/specialists/quinn_r/
├── golden_envelope_precomposition.json         # NEW
├── golden_envelope_postcomposition.json        # NEW
├── golden_return.json                          # NEW
└── fixture_artifacts/                          # NEW; mock artifacts for AC-B perception tests
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` — §12.12 new row; §12.5 framing updated.
- `docs/dev-guide/specialist-anti-patterns.md` — A10 5th + A11 4th bullets.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — file `slab-2b-mid-cross-cutting-importlib-loader-extraction` per AC-J.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-M.
- `pyproject.toml` — auto-emitted; **NOT manually edited**.

---

## Testing Requirements

**K-target ~1.5× (target 17 / floor 12).** Heavier inheritor — dual dispatch + branchable act + cross-wrapper coordination + gate_phase validation. Test count: 3 + 11 + 6 + 2 + 3 + 2 + 1 + 4 + 1 = **33 collectible test functions** (after M-R7 +1 cross-wrapper test + A-R3 +1 negative-gate_phase test); ~25 K-floor units after parametrize-collapse per `story-cycle-efficiency.md §1` (the M-R8 dimension sub-parametrize on the `dimension-failure` case = 1 unit). Effective ratio ~2.08× floor / ~1.56× target. Anti-padding-band-creep guard: dev agent at G6 DISMISSes drift beyond 33 absent novel dual-wrapper failure mode.

**Regression target at T8:** ≥202 passed / ≥2 skipped placeholder-key (was ≥190 at 2b.2 close projected; +12 at floor / +14 at target). Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

### T1 Readiness

- Read order completed per operator sequence and TEMPLATE doc R1-R7 confirmed as binding.
- Sandbox-AC validator PASS:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-3-quinn-r-quality-reviewer-scaffold-migration.md`
- R2 extraction decision at T1: **defer extraction, file follow-on** (option A), no scope creep into 2b.3.

### T2–T7 Implementation Notes

- Generated Quinn-R scaffold with auto-emitted C3 row via generator (no manual `pyproject.toml` edit).
- Implemented Quinn-R runtime in `app/specialists/quinn_r/`:
  - branchable `_act` by `gate_phase` (`pre-composition` / `post-composition`) with explicit validation;
  - `_act` dispatcher + branch helpers (`_act_precomposition`, `_act_postcomposition`) + `_parse_qrr` helper;
  - dual wrappers:
    - `sensory_bridges_dispatch.py` importlib loader seam (hyphenated skill dir compatible),
    - `quality_control_dispatch.py` importlib loader seam for quality-control scripts.
- Implemented `qrr.parsed.*` taxonomy including `qrr.parsed.dimension-failure:{dimension}` for 8 dimensions.
- Implemented two-sided trail-tagging for parse/envelope failures in `_act`.
- Added `quinn_r_review` on `QuinnRReturn` as the single loose-typed return extension for this story.
- AC-D contract note aligned by importing `SanctumLockViolation` from Texas module (shared extraction still deferred).
- Updated docs and deferred inventory:
  - migration-guide §12 framing + §12.12 row + verification set,
  - anti-patterns A10 fifth + A11 fourth examples,
  - deferred inventory: loader extraction follow-on filed, sanctum-exception follow-on flipped ready-for-dev, Quinn-R calibration-learning follow-on filed.

### T8 Regression Evidence

- Quinn-R focused:
  - `.venv/Scripts/python.exe -m pytest tests/specialists/quinn_r tests/integration/scaffold_conformance/test_scaffold_quinn_r.py -q`
  - Result: **49 passed / 1 skipped**
- Migration specialist+conformance anchor:
  - `.venv/Scripts/python.exe -m pytest tests/specialists tests/integration/scaffold_conformance -q`
  - Result: **260 passed / 4 skipped**
- Ruff:
  - `.venv/Scripts/python.exe -m ruff check app/specialists/quinn_r tests/specialists/quinn_r tests/integration/scaffold_conformance/test_scaffold_quinn_r.py docs/dev-guide/langgraph-migration-guide.md docs/dev-guide/specialist-anti-patterns.md _bmad-output/planning-artifacts/deferred-inventory.md`
  - Result: **All checks passed**
- Import-linter:
  - `.venv/Scripts/lint-imports.exe`
  - Result: **3 kept / 0 broken**
- Sandbox AC:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-3-quinn-r-quality-reviewer-scaffold-migration.md`
  - Result: **PASS**

### Party-Mode Review (lean 2-agent: Murat + Amelia)

Top-line moved from RED/YELLOW to GREEN after PATCHes.

- **PATCH applied**
  1. Implemented `qrr.parsed.dimension-failure:{dimension}` with 8-dimension pin tests.
  2. Added two-sided trail-tag tests for `_act` failure paths (exception tag + trail mutation).
  3. Expanded pre-composition deterministic checks to include accessibility checker.
  4. Hardened post-composition wrapper with missing-artifact degrade behavior.
  5. Added wrapper LOC budget checks for both dispatch wrappers.
- **DEFER**
  1. Shared importlib loader extraction and shared sanctum exception extraction remain deferred per AC-J/R2 filing discipline.
- **DISMISS**
  1. Subagent local Python/dependency mismatch findings dismissed; authoritative `.venv` evidence is green in this session.

### G6 Layered Code Review (Blind / Edge / Acceptance)

Top-line: GREEN after remediation and closure bookkeeping.

- **PATCH applied**
  1. Wrapper output status mapping corrected to read upstream `status` contract.
  2. Story-state governance closeout completed: story status, sprint-status row, and follow-on filing state updates.
  3. Migration-guide tag namespace sentence updated to explicitly include `bundle/receipt/ftr/qrr`.
- **DEFER**
  1. Additional unknown-dimension strict validation in `dimension_scores` (non-AC hardening) deferred to dispatch-contract-hardening wave.
- **DISMISS**
  1. `_act` gate-phase validation placement in helper vs inline body dismissed as behaviorally equivalent.

### D12 Close Stub

1. Invariant preservation: Slab-1 substrate intact; C3 row machinery auto-emitted Quinn-R row (live C3 count advanced to 8); FR54 substrate unchanged (no stable prefix harness at Quinn-R layer).
2. Anti-pattern harvest: A10 fifth + A11 fourth landed; follow-ons filed per R2 threshold policy (loader + sanctum-exception split, plus Quinn-R calibration-learning).
3. Migration-guide update: §12.12 Quinn-R row under §12.6 landed; §12 framing sentence updated; tag namespace reaffirmed across `bundle/receipt/ftr/qrr`.
4. TEMPLATE compliance: R1–R7 honored; **R2 EXTRACTION FILED, NOT EXECUTED**. Numeric anchors: `_act` <= 40 LOC dispatcher, `_act_precomposition`/`_act_postcomposition` <= 60 each, wrappers <= 75 each, `test_quinn_r_act_node_dispatch.py` includes branch matrix + gate-phase negative + cross-wrapper + `@llm_live`; loader occurrences threshold exceeded and filed to cross-cutting story.

### Completion Notes

- AC-B-OP remains **DEFERRED-PENDING-OPERATOR-WINDOW** (operator-gated live evidence path).
- AC-M filing/close resolved in `sprint-status.yaml` with `migration-2b-3-...: done` and new backlog entry for `slab-2b-mid-cross-cutting-importlib-loader-extraction`.

### File List

- `app/specialists/quinn_r/__init__.py`
- `app/specialists/quinn_r/graph.py`
- `app/specialists/quinn_r/state.py`
- `app/specialists/quinn_r/model_config.yaml`
- `app/specialists/quinn_r/expertise/README.md`
- `app/specialists/quinn_r/sensory_bridges_dispatch.py`
- `app/specialists/quinn_r/quality_control_dispatch.py`
- `tests/specialists/quinn_r/__init__.py`
- `tests/specialists/quinn_r/conftest.py`
- `tests/specialists/quinn_r/test_quinn_r_generator_auto_emit_c3_row.py`
- `tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py`
- `tests/specialists/quinn_r/test_quinn_r_dispatch_wrappers.py`
- `tests/specialists/quinn_r/test_quinn_r_model_cascade.py`
- `tests/specialists/quinn_r/test_quinn_r_sanctum_cold_read.py`
- `tests/specialists/quinn_r/test_quinn_r_gate_decision_binding.py`
- `tests/specialists/quinn_r/test_quinn_r_resolution_trail.py`
- `tests/specialists/quinn_r/test_quinn_r_state_shape.py`
- `tests/integration/scaffold_conformance/test_scaffold_quinn_r.py`
- `tests/fixtures/specialists/quinn_r/golden_envelope.json`
- `tests/fixtures/specialists/quinn_r/golden_envelope_precomposition.json`
- `tests/fixtures/specialists/quinn_r/golden_envelope_postcomposition.json`
- `tests/fixtures/specialists/quinn_r/golden_return.json`
- `tests/fixtures/specialists/quinn_r/fixture_artifacts/sample.txt`
- `docs/dev-guide/langgraph-migration-guide.md`
- `docs/dev-guide/specialist-anti-patterns.md`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
