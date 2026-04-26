# Migration Story 2b.2: Migrate Vera (Fidelity Assessor) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2b-2-vera-fidelity-assessor-scaffold-migration`
**Epic:** Slab 2b (migration Epic 2b — Per-Specialist Migration Wave) — **second per-specialist migration; first inheritor of the 2b.1 Gary TEMPLATE**.
**Pts:** 3 | **Gate:** single (per governance JSON `2b-2.expected_gate_mode = "single-gate"`, rationale: "Follows 2b.1 TEMPLATE; scaffold-conformant specialist migration"). **K-target:** ~1.4× (target 13 / floor 10; rationale: TEMPLATE inheritor — no new category-establishing surfaces; Vera-specific surfaces are the L2 LLM-judgment evaluation + sensory-bridges dispatch + Fidelity-Trace-Report parsing).

**Lean inheritor party-mode amendments applied 2026-04-25 (post-greenlight Murat + Amelia, 2 of 4 stock agents per workflow.md "Pick 2-4 agents" guidance for inheritor reviews):** 4 APPLY riders integrated — M-R5 (test count arithmetic recount with parametrize-collapse explicit), M-R6 (`ftr.parsed.*` artifact-noun namespace, NOT `finding.parsed.*` process-noun), A-R8 BLOCKER (sensory-bridges importlib loader, NOT direct package import; hyphenated dir + 0-byte `__init__.py` block direct import; entrypoint `perceive(...)` not `perceive_artifact(...)`), A-R9 (`_act` LOC budget option-b: keep ≤115 + extract `_parse_ftr` helper).

This story is the **FIRST INHERITOR of TEMPLATE rules R1–R7** codified in [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1 at Story 2b.1 close. Vera's act-body category is **LLM+tool-dispatch** (parallel to Kira §12.6) — Vera invokes LLM at `_act` for L2 agentic evaluation against L1 deterministic contracts, with perception dispatched via the `sensory-bridges` skill. Vera adds **one row to §12.12 inheritor catalog matrix** under §12.6 parent (NOT a new §12.x worked example, per R3).

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads the standing pre-flight items list. **For inheritor stories, item 11 is load-bearing — `specialist-migration-template.md` carries the rules; this spec only documents Vera-specific deviations + decisions.**

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `2b-2.expected_gate_mode = "single-gate"` (rationale: "Follows 2b.1 TEMPLATE").
2. **Canonical 9-node contract** — `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` frozenset.
3. **Sanctum reference conventions** — [`docs/dev-guide/sanctum-reference-conventions.md`](../../docs/dev-guide/sanctum-reference-conventions.md). Vera's BMB sanctum at `_bmad/memory/bmad-agent-fidelity-assessor/` — verify state at T1; default to graceful-degrade case per R5+R6.
4. **Gate-decision binding** — [`docs/dev-guide/gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md). Generator emits `interrupt()` pattern; precedent-inherited drift uniformly fixed at Slab 3.
5. **State contracts** — `app/models/state/`. `VeraEnvelope(SpecialistEnvelope)` + `VeraReturn(SpecialistReturn)`. Per R4 (one new field, loose-typed): `vera_finding: dict[str, Any] | None` (the Fidelity Trace Report per Vera SKILL.md outbound contract).
6. **Model cascade** — `docs/dev-guide/model-selection-guide.md` + `app/models/selection_policy.yaml`. Vera's L2 agentic evaluation is reasoning-heavy (forensic verification with O/I/A taxonomy + severity tagging) → `tier_request: reasoning` → resolves to `gpt-5.4`. Vera DOES invoke LLM at `_act` (LLM+tool-dispatch category, NOT pure-tool-dispatch like Texas/Gary).
7. **LLM-live skip-fixture** — `tests/conftest.py` auto-skips `@pytest.mark.llm_live` when `OPENAI_API_KEY` is unset. Vera carries one `@pytest.mark.llm_live` test (AC-2b.2-B live evaluation against fixture artifacts).
8. **Severance posture** — hybrid working tree is sole input surface.
9. **Generator entrypoint** — `skills/bmad_create_specialist/`. Auto-emit C3 row machinery from Story 2a.5 fires via R5.
10. **Predecessor close evidence** — Story 2b.1 (Gary TEMPLATE) ready-for-dev (spec amended 2026-04-25 with 14 party-mode APPLY riders); will close before 2b.2 dev-story opens per batch-dev-cycle plan. Slab-1 substrate intact; lint-imports 3/3 KEPT.
11. **TEMPLATE rules canonical doc** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1. **R1–R7 apply per AC-2b.2-K. No deviation expected.**

### Slab 2b artifact-existence sweep (9-point — same as 2b.1)

- **A** `app/manifest/compiler.py::compile()` raises `CompileError` (additive-only).
- **B** `app/models/state/specialist_envelope.py::SpecialistEnvelope` + `specialist_return.py::SpecialistReturn`.
- **C** `app/specialists/{irene,kira,texas,gary}/graph.py::build_*_graph` — four reference patterns; **Kira (§12.6) is closest precedent** (LLM+tool-dispatch).
- **D** `app/gates/resume_api.py::resume_from_verdict` raises `NotImplementedError`.
- **E** `app/specialists/_scaffold/{graph,state,model_config,expertise}` populated.
- **F** `skills/bmad_create_specialist/scripts/generate.py::_plan_pyproject_c3_mutation` (auto-emit). `pyproject.toml` C3 contains `app.specialists.gary.graph -> app.gates.resume_api` row post-2b.1 close (6 rows pre-Vera; Vera's auto-emit makes 7).
- **G** `tests/end_to_end/test_cache_hit_rate_kira_populated.py` — Vera's act invokes LLM, so FR54 cache-hit-rate substrate IS applicable in principle; however, fidelity-assessment prompts vary per-artifact (no stable prefix to cache). Defer FR54 measurement at Vera layer to Slab-3 if/when an applicability case emerges. No cache-hit harness at 2b.2.
- **H** `docs/dev-guide/sanctum-reference-conventions.md` exists.
- **I** `docs/dev-guide/specialist-anti-patterns.md` carries A10 with three examples (Irene/Kira/Gary) + A11 retitled to "sanctum/sidecar contract drift" with two examples (Irene/Gary). Vera adds A11 third example (sidecar contract divergence — `bmad-agent-fidelity-assessor` skill-dir vs `vera-sidecar` SKILL.md activation).

### Epic-doc-vs-framework cross-check (per R6 — split sub-subsections)

#### (a) Framework drifts (harvest as anti-pattern bullets)

**Drift #1 — Sanctum/sidecar contract divergence (A11 THIRD example):** Vera's skill-dir is `bmad-agent-fidelity-assessor` (BMB convention; runtime persona is `vera`); BMB sanctum dir is `_bmad/memory/bmad-agent-fidelity-assessor/` (matches skill-dir name); Vera's SKILL.md activation reads `_bmad/memory/vera-sidecar/index.md` (legacy sidecar). Same drift class as Irene + Gary. **Harvest as A11 third bullet** at AC-2b.2-J. **Resolution:** LangGraph runtime uses BMB convention; sidecar contract OUT OF SCOPE.

**Drift #2 — Model tier "L2 agentic evaluation" not in selection_policy:** Vera SKILL.md describes L2 agentic evaluation as a tier; `selection_policy.yaml` has `reasoning / fast / code` only. **Resolution:** L2 agentic evaluation maps to `tier_request: reasoning` → `gpt-5.4`. **Harvest as A10 fourth example** at AC-2b.2-J.

#### (b) TEMPLATE scope decisions (codified per R1)

**Decision #1 — Bounded scope:** Vera's SKILL.md describes capabilities including L1 contract evaluation, L2 agentic LLM judgment, learning-from-corrections. **Migration scope:** the headless dispatch path (Marcus invokes Vera at fidelity gates → Vera perceives → Vera evaluates → Vera returns FTR). Learning-from-corrections is a memory sidecar concern, OUT OF SCOPE for the LangGraph runtime migration. Per R1.

**Decision #2 — Sensory-bridges dispatch seam (per Amelia A-R8 amendment 2026-04-25):** Vera dispatches to the `sensory-bridges` skill for artifact perception. **Verified at story-author time:** `skills/sensory-bridges/` directory uses HYPHEN (not snake_case); `__init__.py` is 0 bytes; the dir is NOT directly importable as `skills.sensory_bridges` (hyphen breaks Python identifier). The canonical access pattern (per `skills/sensory-bridges/scripts/bridge_utils.py:50-60` itself) is via `importlib.util.spec_from_file_location` setting up `sys.modules` stubs. Public entrypoint is `perceive(artifact_path, modality, gate, requesting_agent)` at `skills/sensory-bridges/scripts/bridge_utils.py` (per SKILL.md §Invocation), NOT `perceive_artifact(...)`. **Decision (per R2 sub-mechanism rule):** use **importlib loader pattern** parallel to Kira's `_load_target_module` (NOT direct package import like Gary). The `sensory_bridges_dispatch.py` wrapper exposes a Vera-specific signature `dispatch_to_sensory_bridges(artifact_path, source_of_truth_path, modality, gate)` internally calling `perceive(...)`. **Seam-divergence narrative correction:** Kira/Vera both use importlib loader (2 occurrences); Gary direct-package-import (1 occurrence); Texas subprocess (1 occurrence in this seam family). Extraction threshold (R2: third occurrence of SAME seam category) — for importlib-loader specifically, met if 2b.3 Quinn-R also lands an importlib loader. Track at 2b.3 T1.

---

## Story

As a **migration dev agent inheriting the 2b.1 Gary TEMPLATE**,
I want **Vera (Fidelity Assessor) rehomed into `app/specialists/vera/` with the 9-node scaffold + LLM+tool-dispatch act-body that invokes the model cascade for L2 agentic evaluation and dispatches to `sensory-bridges` for artifact perception + per-R5 auto-emit C3 row positive regression test + §12.12 inheritor catalog row added under §12.6 parent**,
So that **the 2b.1 TEMPLATE's seven rules (R1–R7) are exercised by the first inheritor without deviation, the LLM+tool-dispatch category gains a second inhabitant (Kira → Vera), the §12.12 catalog matrix establishes the inheritor-row pattern that 2b.3-2b.13 will follow, and Slab 2b's per-specialist migration cadence proves out**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Vera carries ONE `@pytest.mark.llm_live` test (AC-B live LLM evaluation).

### AC-2b.2-A — Generator emits Vera + auto-emits C3 row (per R5)

Per R5 of `specialist-migration-template.md`. Test pin: `tests/specialists/vera/test_vera_generator_auto_emit_c3_row.py` — 3 tests using `temp_repo_root` fixture (NOT live `pyproject.toml`). Pre-baseline 5 rows (fixture); post-emit 6 rows with `app.specialists.vera.graph -> app.gates.resume_api` row + comment marker. Same hermetic pattern as 2b.1 AC-A.

Generator invocation:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name vera --mcp none --expertise-tier L4-fidelity-assessment \
  --from-skill skills/bmad-agent-fidelity-assessor
```

### AC-2b.2-B — Vera `act` node wires LLM+tool-dispatch (Kira-pattern inheritor)

- **Given** Vera is a fidelity assessor; her `_act` (1) dispatches via `app.specialists.vera.sensory_bridges_dispatch.dispatch_to_sensory_bridges(artifact_path, source_of_truth_path, modality, gate)` (mockable importlib-loader wrapper around `perceive(...)` from `skills/sensory-bridges/scripts/bridge_utils.py` per Decision #2 above; NOT `perceive_artifact`); (2) invokes LLM (`tier_request: reasoning` → `gpt-5.4`) with the perceived payload + L1 contracts + O/I/A taxonomy guidance to produce a Fidelity Trace Report (FTR); (3) parses the LLM response via the extracted helper `_parse_ftr(raw_text) -> dict` (per Amelia A-R9 — option-b chosen: keep `_act ≤ 115 LOC` + extract parser as module-level helper parallel to Kira's `_extract_kling_response` so the 6-branch parametrize matrix targets the helper, not `_act`); (4) returns `{cache_state: {cache_prefix: <output_blob>, entries_count: ...}}` with FTR encoded as sorted-keys canonical JSON.
- **When** the dev agent implements `_act` per the LLM+tool-dispatch pattern (Kira precedent at `app/specialists/kira/graph.py`).
- **Then** invoking `build_vera_graph()` with a fixture envelope + dispatch monkey-patched produces a non-empty result containing `vera_finding` (the FTR) + provenance metadata.
- **LOC budget per R2 + Amelia A-R3 carry-forward:** `_act ≤ 115 LOC` AND `sensory_bridges_dispatch ≤ 75 LOC`.
- **Tag namespace per Murat M-R2 (artifact-noun convention):** `ftr.parsed.*` — tags `ftr.parsed.ok / malformed / missing-key / wrong-type / empty / contract-failure`. Six parametrized parse-branch cases.
- **Live LLM test (`@pytest.mark.llm_live`):** AC-B-LIVE asserts the live `gpt-5.4` call produces a structurally valid FTR shape against a fixture artifact (no semantic assertion; that's Quinn-R territory). Skips on placeholder OPENAI_API_KEY.

### AC-2b.2-B-OP — Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Vera against a real Marcus-staged fidelity gate (one fidelity-gate evaluation; ~1500 tokens). Pastes FTR + LLM cost into Completion Notes. Tighter than Texas's Slab-3-deferred; matches Gary's operator-window deferral pattern.

### AC-2b.2-C — Model cascade at `_plan` (per R7)

Trail-entry resolution at `_plan` MANDATORY per R7 even though Vera DOES invoke LLM at `_act` (the trail entry is required regardless of invocation; uniformity is the FR16 invariant). Test pin: 2 tests (default + override).

### AC-2b.2-D — Sanctum cold-read at `_plan` (graceful-degrade case)

Per R5+R6. Vera's BMB sanctum at `_bmad/memory/bmad-agent-fidelity-assessor/` likely absent at story-author time (operator first-breath ceremony deferred). Graceful-degrade per Kira 2a.3 + Gary 2b.1 precedent. Test pin: 3 tests (deterministic empty/populated + readme-list-shape + lock-baseline-OR-skip with `PERSONA.md` sentinel per Amelia A-R5 carry-forward). Imports `SanctumLockViolation` from `app.specialists.texas.graph` per cross-cutting refactor deferral (third occurrence threshold unmet).

### AC-2b.2-E — Gate-decision binding (precedent-inherited)

Same shape as 2a.2/2a.3/2a.4/2b.1. Test pin: 2 tests (present + transitions chain).

### AC-2b.2-F — Resolution trail (FR16 fifth per-specialist exercise)

Test pin: 1 test.

### AC-2b.2-G — Vera shape-pin tests (per R4)

Per R4 (one new field, loose-typed): `vera_finding: dict[str, Any] | None`. Strict-typing deferred to 2b.15. Test pin: 4 tests (envelope + return + round-trip + invalid-payload).

### AC-2b.2-H — Scaffold-conformance test registered

`tests/integration/scaffold_conformance/test_scaffold_vera.py` — 1 test asserting `validate_scaffold("vera", build_vera_graph()).is_conforming is True`.

### AC-2b.2-I — Migration-guide §12.12 grows ONE inheritor row (per R3)

Per R3, Vera does NOT add a new §12.x. Vera adds ONE row to §12.12 inheritor catalog matrix:

| Specialist | Parent §12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Vera | §12.6 (Kira LLM+tool-dispatch) | sensory-bridges importlib-loader pattern (parallel to Kira's `_load_target_module`; chosen because hyphenated dir + 0-byte `__init__.py` block direct package import per A-R8 verification) | graceful-degrade (BMB sanctum unpopulated) | A10 4th example (`reasoning`-tier mapping) + A11 3rd example (sidecar contract divergence) | 2b.2 |

Update §12.5 framing sentence to reflect "fifth specialist proven on 9-node scaffold; four established categories — narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API tool-dispatch."

### AC-2b.2-J — Anti-pattern catalog harvest (A10 fourth example + A11 third example)

Two augmented bullets per R6:

- **A10 fourth example:** Vera's `tier_request` "L2 agentic evaluation" not in `selection_policy.yaml`; maps to `reasoning` → `gpt-5.4`.
- **A11 third example:** Vera's skill-dir `bmad-agent-fidelity-assessor` vs runtime persona `vera`; SKILL.md activation reads `vera-sidecar` (legacy sidecar). Same shape as Irene + Gary.

### AC-2b.2-K — TEMPLATE compliance (per R1–R7)

TEMPLATE rules R1–R7 from `docs/dev-guide/specialist-migration-template.md` v1 apply. **No deviation expected.** Document any deviation + rationale in Dev Agent Record. Compliance evidence at D12 close.

### AC-2b.2-L — D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired correctly for Vera (positive regression evidence at AC-A); FR54 substrate intact (Vera's per-artifact prompts have no stable prefix; substrate doesn't fire here).
2. **Anti-pattern harvest:** A10 fourth example + A11 third example per AC-J.
3. **Migration-guide update:** §12.12 inheritor row added under §12.6 parent per AC-I + R3; framing sentence updated. NO new §12.x.
4. **TEMPLATE compliance:** R1–R7 honored without deviation. Numeric anchors: `_act` LOC measured / sensory_bridges_dispatch LOC measured / 6 parse-branch tests / 1 @llm_live test / sanctum graceful-degrade case / pyproject.toml C3 row count growth in temp fixture.

### AC-2b.2-M — Sprint-status state-flips at filing AND at close

- **At filing:** `migration-2b-2-vera-fidelity-assessor-scaffold-migration: ready-for-dev` added under Slab 2 block.
- **At close:** flip to `done`; epic stays `in-progress` (only flips at slab close at 2b.17).

---

## File Structure Requirements

### NEW files

```
app/specialists/vera/
├── __init__.py                                 # generator-emitted
├── graph.py                                    # generator-emitted; _act body filled at T2 (LLM+tool-dispatch)
├── state.py                                    # generator-emitted; VeraReturn extended with vera_finding
├── model_config.yaml                           # generator-emitted; Vera tier-mapping (reasoning) comments added
├── sensory_bridges_dispatch.py                 # NEW (~50-75 LOC); importlib loader per R2 sub-mechanism + A-R8 (hyphenated dir + 0-byte __init__.py block direct import); wraps `perceive(...)` from `skills/sensory-bridges/scripts/bridge_utils.py`
├── expertise/
│   ├── README.md                               # generator-emitted; dotted reference table for 5 Vera refs
│   └── __init__.py

tests/specialists/vera/
├── __init__.py                                 # NEW (empty marker per A-R6)
├── test_vera_generator_auto_emit_c3_row.py     # NEW (3 tests; AC-A; temp_repo_root fixture per R5)
├── test_vera_act_node_dispatch.py              # NEW (~7 tests; AC-B with 6 parse-branches + 1 @llm_live)
├── test_vera_sensory_bridges_dispatch.py       # NEW (3 tests; AC-B SEAM differences + sensory-bridges import)
├── test_vera_model_cascade.py                  # NEW (2 tests; AC-C)
├── test_vera_sanctum_cold_read.py              # NEW (3 tests; AC-D graceful-degrade per R5+R6)
├── test_vera_gate_decision_binding.py          # NEW (2 tests; AC-E)
├── test_vera_resolution_trail.py               # NEW (1 test; AC-F)
└── test_vera_state_shape.py                    # NEW (4 tests; AC-G four-file-lockstep)

tests/integration/scaffold_conformance/
└── test_scaffold_vera.py                       # NEW (1 test; AC-H)

tests/fixtures/specialists/vera/
├── golden_envelope.json                        # NEW; AC-G
├── golden_return.json                          # NEW; AC-G (with vera_finding populated)
└── fixture_artifacts/                          # NEW; mock artifacts for AC-B perception tests
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` — §12.12 NEW row (Vera under §12.6 parent); §12.5 framing sentence updated.
- `docs/dev-guide/specialist-anti-patterns.md` — A10 fourth example + A11 third example bullets.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-M.
- `pyproject.toml` — auto-emitted; **NOT manually edited**.

---

## Testing Requirements

**K-target ~1.4× (target 13 / floor 10).** TEMPLATE-inheritor — no new category surfaces. **Test count breakdown per Murat M-R5 amendment 2026-04-25:** 26 collectible test functions; ~21 K-floor units after parametrize-collapse per `story-cycle-efficiency.md §1` (the 6-case `ftr.parsed.*` parse-branch matrix collapses to 1 unit; 1 happy-path + 1 @llm_live = 2 separate units; sanctum 3 units; cascade 2 units; gate-decision 2 units; trail 1 unit; state-shape 4 units; conformance 1 unit; auto-emit 3 units; sensory-bridges SEAM 3 units). Effective ratio ~2.1× floor / ~1.6× target — within `1.2-1.5×` policy band when measured against target 13. Anti-padding-band-creep guard: any test count drift beyond the 26 collectible budget requires Murat consultation; G6 DISMISSes drift absent novel LLM+tool-dispatch failure mode.

**Regression target at T8:** ≥190 passed / ≥2 skipped placeholder-key (was ≥185 at 2b.1 close projected; +5 at floor / +8 at target). Import-linter 3/3 KEPT. Ruff clean. Sandbox-AC PASS.

---

## Dev Agent Record

### T1 Readiness

- Read order completed per operator sequence: `CLAUDE.md` -> `specialist-migration-template.md` v2.3 -> `specialist-anti-patterns.md` -> `migration-story-governance.json` -> `scaffold-conformance-framework.md` -> `sanctum-reference-conventions.md` -> `pydantic-v2-schema-checklist.md` -> `slab-2a-retrospective.md` -> `sprint-status.yaml`.
- Sandbox-AC validator PASS:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-2-vera-fidelity-assessor-scaffold-migration.md`
- Template applicability confirmed: R1–R7 inherited with no deviations.

### T2–T7 Implementation Notes

- Implemented Vera specialist runtime under `app/specialists/vera/`:
  - `_plan` model cascade trail entry (`tier_request: reasoning`).
  - `_act` LLM+tool-dispatch flow with sensory-bridges wrapper and canonical JSON output.
  - `_parse_ftr` extracted helper with `ftr.parsed.*` branch taxonomy:
    - `ok / malformed / missing-key / wrong-type / empty / contract-failure`.
- Implemented `sensory_bridges_dispatch.py` importlib loader seam and patched runtime registration in `sys.modules` for real bridge-utils resolution.
- Added/extended tests to cover:
  - full parser branch/tag matrix,
  - two-sided trail-tag assertion on failure paths,
  - envelope decode error-tagging,
  - dispatch failure tagging,
  - LOC budget guards (`_act <= 115`, dispatch wrapper <= 75),
  - scaffold conformance and state shape pins.
- Updated docs:
  - `docs/dev-guide/langgraph-migration-guide.md`: §12 framing + §12.12 Vera inheritor row + §12.13 verification commands + changelog row.
  - `docs/dev-guide/specialist-anti-patterns.md`: A10 fourth example, A11 third example.

### T8 Regression Evidence

- Vera-focused:
  - `.venv/Scripts/python.exe -m pytest tests/specialists/vera tests/integration/scaffold_conformance/test_scaffold_vera.py -q`
  - Result: **40 passed / 1 skipped**
- Migration specialist+conformance anchor:
  - `.venv/Scripts/python.exe -m pytest tests/specialists tests/integration/scaffold_conformance -q`
  - Result: **211 passed / 3 skipped**
- Ruff:
  - `.venv/Scripts/python.exe -m ruff check app/specialists/vera tests/specialists/vera tests/integration/scaffold_conformance/test_scaffold_vera.py docs/dev-guide/langgraph-migration-guide.md docs/dev-guide/specialist-anti-patterns.md`
  - Result: **All checks passed**
- Import-linter:
  - `.venv/Scripts/lint-imports.exe`
  - Result: **3 kept / 0 broken**
- Sandbox AC:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-2-vera-fidelity-assessor-scaffold-migration.md`
  - Result: **PASS**

### Party-Mode Review (3-agent: Winston + Murat + Amelia)

Top-line moved from RED to GREEN after PATCHes.

- **PATCH applied**
  1. Sensory-bridges loader runtime registration bug fixed (`sys.modules` registration + package stubs) in `sensory_bridges_dispatch.py`.
  2. `_act` now tags and trails envelope/dispatch/model-invocation failures via `ftr.parsed.contract-failure` (plus malformed/wrong-type for envelope decode).
  3. Parser matrix tests upgraded to assert both message and branch tag for all six `ftr.parsed.*` outcomes.
  4. Added two-sided trail-tag tests for parser failure, malformed envelope, wrong-type envelope, and dispatch failure.
  5. Added LOC budget pin tests for `_act` and dispatch wrapper.
  6. Strengthened live smoke structural assertion for `vera_finding`.
- **DEFER**
  1. Cross-cutting runtime import of scaffold contract from `tests.*` is inherited from earlier specialist pattern; defer relocation to shared runtime module with framework-hardening scope.
  2. Additional filesystem corruption edge cases (`PermissionError`/`UnicodeDecodeError`) in sanctum/reference read paths deferred as non-story-critical.
- **DISMISS**
  1. Subagent environment mismatch findings (Python 3.10 / missing deps) dismissed because authoritative runs in this session used `.venv/Scripts/python.exe` and passed.

### G6 Layered Code Review (Blind / Edge / Acceptance)

Top-line: GREEN after remediation and governance closeout.

- **PATCH applied**
  1. Runtime sensory-bridge import seam hardening (`sys.modules` and package stub registration).
  2. `_act` error-path trail tagging expanded for non-parse failures.
  3. Acceptance/governance closure artifacts populated (this record + sprint-status 2b.2 entry).
- **DEFER**
  1. Cross-specialist scaffold-contract import-source normalization to non-test module deferred to cross-cutting framework hardening.
  2. AC-D note about `SanctumLockViolation` import path treated as non-behavioral prose drift (no runtime defect); defer harmonization to story-authoring/doc cleanup.
- **DISMISS**
  1. Suggested parser contract expansion to allow empty findings was dismissed because AC-B explicitly includes `ftr.parsed.empty` as a required branch.

### D12 Close Stub

1. Invariant preservation: Slab-1 substrate remains intact; auto-emit C3 machinery validated by Vera generator tests; FR54 substrate remains intact though Vera’s per-artifact prompts do not produce a stable prefix.
2. Anti-pattern harvest: A10 fourth example + A11 third example landed in `docs/dev-guide/specialist-anti-patterns.md`.
3. Migration-guide update: §12.12 added Vera inheritor row under §12.6 and §12 framing/verification sections updated; no new §12.x worked example added.
4. TEMPLATE compliance: R1–R7 honored without deviation. Numeric anchors: `_act` LOC guard <=115, dispatch LOC guard <=75, 6 parse-branch tags pinned, 1 `@pytest.mark.llm_live` test, sanctum graceful-degrade case exercised, C3 row behavior verified in generator fixture tests.

### Completion Notes

- AC-B-OP remains **DEFERRED-PENDING-OPERATOR-WINDOW** (operator-gated evidence).
- Test-count governance note: this story runs above original collectible estimate after post-review hardening; retained as justified PATCH coverage due concrete seam/runtime defects caught in party/G6 rounds.

### File List

- `app/specialists/vera/__init__.py`
- `app/specialists/vera/graph.py`
- `app/specialists/vera/sensory_bridges_dispatch.py`
- `app/specialists/vera/state.py`
- `app/specialists/vera/model_config.yaml`
- `app/specialists/vera/expertise/README.md`
- `tests/specialists/vera/__init__.py`
- `tests/specialists/vera/test_vera_generator_auto_emit_c3_row.py`
- `tests/specialists/vera/test_vera_act_node_dispatch.py`
- `tests/specialists/vera/test_vera_sensory_bridges_dispatch.py`
- `tests/specialists/vera/test_vera_model_cascade.py`
- `tests/specialists/vera/test_vera_sanctum_cold_read.py`
- `tests/specialists/vera/test_vera_gate_decision_binding.py`
- `tests/specialists/vera/test_vera_resolution_trail.py`
- `tests/specialists/vera/test_vera_state_shape.py`
- `tests/integration/scaffold_conformance/test_scaffold_vera.py`
- `tests/fixtures/specialists/vera/golden_envelope.json`
- `tests/fixtures/specialists/vera/golden_return.json`
- `tests/fixtures/specialists/vera/fixture_artifacts/sample.txt`
- `docs/dev-guide/langgraph-migration-guide.md`
- `docs/dev-guide/specialist-anti-patterns.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
