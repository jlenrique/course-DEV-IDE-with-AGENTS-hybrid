# Codex dev-story prompt — Story 7c.15 (§11B G4B + §15 G5 + Marcus §15 Bundle Writer; single-gate; STANDARD T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T1-T10 → drops `_codex-handoff/7c-15.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 3 — slot 6 (heaviest Wave-3 story; AMEND-4 dual-FR fold).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-BLOCKED on 7c.17b** (Wave 4 backlog). 7c.15's Marcus §15 bundle writer consumes 7c.17b's outbound-envelope; **DO NOT dispatch until 7c.17b closes.**

**Parallel-dispatch context:** 7c.15 is **NOT parallel-safe with 7c.13/7c.14** in the same batch. Reasons:
1. Standard-tier T11 (vs lite for 7c.13/7c.14) — review queue contention.
2. lookahead_tier=2 (vs 1 for siblings) — heavier substrate touch.
3. Marcus writer module touches `app.marcus.*` namespace — distinct contract regime (M1-M4 vs C6).
4. Predecessor 7c.17b not closed.

Dispatch 7c.15 in its OWN batch after 7c.17b closes. Spec is captured now to prevent scope-loss in Wave-4 churn.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

This story has DUAL §section packages (section_11b + section_15) PLUS a Marcus writer module. Within-story parallelism is feasible but coordination matters:

- **Surface-bound subagents** can run in parallel:
  - 1 subagent: §11B G4B surface (poll_surface + OperatorVerdict + JSON schema + tests)
  - 1 subagent: §15 G5 surface (poll_surface + OperatorVerdict + JSON schema + tests)
  - 1 subagent: Marcus §15 bundle writer + Marcus tests
- **Main-thread coordination:**
  - C6 modules list edit (TWO entries appended; pyproject.toml)
  - Class-conformance arithmetic (+2 for both new shape-pins)
  - Verification battery (T8)
  - T10 dropbox

- **Shared-file forbiddens (DO NOT modify):**
  - `tests/schemas/operator_verdict/_harness.py` (7c.4b D3)
  - `tests/gates/section_02a/` (canonical reference)
  - Wave-3 trio §section packages (7c.6/7c.7/7c.8)
  - Next-batch §section packages (7c.13 section_08b + 7c.14 section_11)
  - 7c.17b's `app/marcus/orchestrator/writers/outbound_envelope.py` (consumed read-only by §15 bundle writer)

---

```
Run bmad-dev-story on Story 7c.15 (Slab 7c Wave 3 slot 6; single-gate; STANDARD T11; AMEND-4 dual-FR fold).

Spec: `_bmad-output/implementation-artifacts/migration-7c-15-section-11b-g4b-section-15-g5-final-operator-handoff.md`.

## Required reading (in order)

1. Story spec (7 ACs A-G; T1-T10 task structure with T2/T3/T4 surface-bound parallelism).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md` + `migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (sibling references; §11B closest match for transport-set CLI+HTTP).
4. `_bmad-output/implementation-artifacts/migration-7c-17b-...md` (predecessor — outbound-envelope writer reference).
5. **`app/gates/section_02a/poll_surface.py`** (canonical pattern).
6. **Wave-3 trio §section packages** (`section_04a/`, `section_04_5/`, `section_04_55/`) (sibling pattern for re-emit-helpers + parity_contract).
7. **Next-batch §section packages** (`section_08b/`, `section_11/` — landed at 7c.13 + 7c.14) (closer pattern reference; same lookahead_tier=1 cohort).
8. **`app/models/operator_verdict_section_02a.py`** + Wave-3 trio + 7c.13/7c.14 OperatorVerdict variants (mirror these for `Section11BOperatorVerdict` + `Section15OperatorVerdict`).
9. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
10. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + Wave-3 trio + 7c.13/7c.14 shape-pins (canonical references).
11. **Wave-3 trio + 7c.13/7c.14 DSL-registration + 3-transport-parity tests** (test pattern reference).
12. `app/models/decision_cards/g4.py` + `app/models/decision_cards/g5.py` (G4Card + G5Card consumption).
13. **`app/marcus/orchestrator/writers/outbound_envelope.py`** (7c.17b deliverable; consumed by §15 bundle writer; READ-ONLY).
14. `app/marcus/orchestrator/writers/` existing writer modules (sanctum-alignment pattern reference).
15. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax).
16. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G4B alias + G5 net-new family per §2).
17. `pyproject.toml::tool.importlinter` (C6 contract; modules list current state).
18. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
19. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern).
20. Governance JSON `7c-15` entry + `wave_3_lookahead_policy::current_cap=3`.

## T1 hard checkpoints

- 7c.5.G4 + 7c.5.G5 + 7c.3b done.
- **7c.17b done (HARD BLOCKER — confirm in sprint-status.yaml).**
- Wave-3 trio (7c.6/7c.7/7c.8) closed; 7c.13 + 7c.14 closed (predecessor pattern references).
- `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
- `app.models.decision_cards.g4.G4Card` + `app.models.decision_cards.g5.G5Card` importable + inherit `DecisionCardBase`.
- `app.marcus.orchestrator.writers.outbound_envelope` importable + emits expected schema.
- Class-conformance baseline: record observed; recompute at T1.
- Broad-regression baseline: re-run.

## Files in scope

**New (~14 files):**
- `app/gates/section_11b/{__init__,poll_surface}.py`
- `app/gates/section_15/{__init__,poll_surface}.py`
- `app/models/operator_verdict_section_11b.py` + `operator_verdict_section_11b.v1.schema.json`
- `app/models/operator_verdict_section_15.py` + `operator_verdict_section_15.v1.schema.json`
- `app/marcus/orchestrator/writers/section_15_bundle.py` (~150 LOC)
- `tests/schemas/operator_verdict/test_section_11b_shape.py`
- `tests/schemas/operator_verdict/test_section_15_shape.py`
- `tests/gates/section_11b/{__init__,_helpers,test_g4b_poll_surface_dsl_registration,test_g4b_poll_surface_three_transport_parity}.py`
- `tests/gates/section_15/{__init__,_helpers,test_g5_poll_surface_dsl_registration,test_g5_poll_surface_three_transport_parity}.py`
- `tests/marcus/orchestrator/writers/test_section_15_bundle.py`

**Modified (1 file):**
- `pyproject.toml` — append BOTH `app.gates.section_11b` AND `app.gates.section_15` to `tool.importlinter::contracts::C6::modules`.
- Marcus activation block — sanctum-alignment row for `section_15_bundle` writer (per Slab 7b precedent) OR Cora-sidecar exception.

**Do NOT modify:**
- `app/gates/section_02a/` + Wave-3 trio + 7c.13/7c.14 §section packages (read-only)
- `tests/gates/section_02a/` + Wave-3 trio + 7c.13/7c.14 test dirs (read-only)
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/models/decision_cards/` (G4Card + G5Card consumed read-only)
- `app/marcus/orchestrator/writers/outbound_envelope.py` (7c.17b deliverable; consumed read-only)
- `app/parity/contracts/` (7c.4b D1 deliverables; read-only)

## Critical implementation notes

- **§11B G4B parity_contract registration:** `@parity_contract(surface_id="section_11b_g4b_input_package", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G4")`. Per FR-7c-19 §11B: CLI + HTTP mandatory; MCP-stdio optional.
- **§15 G5 parity_contract registration:** `@parity_contract(surface_id="section_15_g5_final_handoff", mandatory_transports=["cli", "http", "mcp-stdio"], optional_transports=[], alias_of="G5")`. Per FR-7c-19 §15: ALL 3 mandatory; NO optional. **Note:** 7c.8 (§04.55 G1.5) used `optional_transports=[]` — same pattern; reference 7c.8's parity_contract registration.
- **Closed verb Literals:**
  - `Section11BVerdictVerb = Literal["approve", "edit", "reject"]` (review framing for input-package preview).
  - `Section15VerdictVerb = Literal["complete", "edit", "reject"]` (completion-action verb per FR-7c-19 §15 "Operator completes final operator handoff").
- **Verb-payload consistency (`@model_validator(mode="after")`):** standard pattern per §02A canonical (each verb requires its specific payload field; forbids the others).
- **Marcus §15 bundle writer (`Section15Bundle`):**
  - Pydantic-v2 with `validate_assignment=True`.
  - Triggered ON §15 G5 verb=complete acceptance (NOT on `edit` or `reject`).
  - Consumes 7c.17b's `outbound_envelope.yaml` (read via Path; parse via existing 7c.17b loader).
  - Regenerates DESCRIPT-ASSEMBLY-GUIDE.md from per-plan-unit packages + outbound-envelope state.
  - Computes Trial-3 transcript anchor via sha256 of the live-trial transcript file path (path provided by run-state context).
  - Writes slab-close evidence pointer to consolidated path (per FR-7c-29 schema).
  - Sanctum-alignment per FR-7c-54: declare row in Marcus activation block per Slab 7b precedent (`project_slab_7b_skill_md_sanctum_alignment.md`).
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18 (×2 schemas). NO PowerShell `>` redirection. LF-only; verify NO BOM.
- **Shape-pins via FR-7c-49 harness:** ×2 — one per surface.
- **Re-emit helpers (NOT import from §02A):** Per Wave-3 trio precedent, both new §section poll-surfaces re-emit `canonical_model_bytes` + `compute_model_digest` locally.
- **C6 modules list:** TWO entries appended atomically (`section_11b` + `section_15`).
- **K-target 1.6× ≈ 1100 LOC ceiling.** Estimate ~700 LOC actual.
- **T11 STANDARD tier:** AC count 7 + Marcus writer module + dual surface + sanctum-alignment touch — does NOT qualify for lite. Plan for ~25-40 min standard T11 review (vs ~15 min lite).

## PARALLEL-DISPATCH GUARDRAILS (binding)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories. Marcus writer is also out-of-scope for `tests/parity/test_decision_card_*` AST scan.
2. **Pattern-replication discipline.** Mirror §02A canonical AND Wave-3-trio + 7c.13/7c.14 sibling patterns.
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — atomic 2-entry append.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields. `Field(..., description=...)` on every field. UUID4-typed run_id. tz-aware submitted_at. sha256-hex decision_card_digest. verb-payload consistency `model_validator(mode="after")`. **Marcus writer:** Pydantic-v2 `validate_assignment=True` + `extra="forbid"` on `Section15Bundle`.
5. **Class-conformance arithmetic.** +2 (TWO new shape-pin files). Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_11b/ tests/gates/section_15/ tests/schemas/operator_verdict/test_section_11b_shape.py tests/schemas/operator_verdict/test_section_15_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/test_section_15_bundle.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short  # Marcus contracts M1-M4 non-regression
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line  # broad
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-15-section-11b-g4b-section-15-g5-final-operator-handoff.md
.venv/Scripts/python.exe -m ruff check app/gates/section_11b/ app/gates/section_15/ app/models/operator_verdict_section_11b.py app/models/operator_verdict_section_15.py app/marcus/orchestrator/writers/section_15_bundle.py tests/gates/section_11b/ tests/gates/section_15/ tests/schemas/operator_verdict/test_section_11b_shape.py tests/schemas/operator_verdict/test_section_15_shape.py tests/marcus/orchestrator/writers/test_section_15_bundle.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-15.ready-for-review.md`. STANDARD-tier dropbox includes:
- 14-file lockstep verification across BOTH §section packages
- parity_contract registration evidence (×2: alias_of="G4" + alias_of="G5"; transport sets verified)
- Marcus writer evidence (Section15Bundle shape + emit function + DESCRIPT-ASSEMBLY-GUIDE.md regen determinism + Trial-3 anchor sha256 + slab-close evidence pointer wiring)
- Sanctum-alignment row evidence in Marcus activation block (per Slab 7b precedent)
- §02A + Wave-3 trio + 7c.13/7c.14 non-regression confirmations
- Marcus contracts M1-M4 non-regression confirmation
- Class-conformance delta (+2)
- Broad-regression delta with per-failure attribution
- C6 modules list 2-entry append integration evidence

T11: Claude STANDARD tier (~25-40 min: spec-checklist + diff-review + sanctum-alignment audit + Marcus writer behavior verification + cross-surface coordination + status flip).

## Boundary

HALT on:
- 7c.5.G4 + 7c.5.G5 + 7c.3b not done.
- **7c.17b not done (HARD BLOCKER).**
- alias_of forward syntax not in parity_contract decorator.
- class-conformance count != T1-baseline + 2.
- broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited.
- Marcus contracts M1-M4 ANY broken (Marcus writer must respect lane separation).
- Sanctum-alignment row missing AND no Cora-sidecar exception documented.

DO NOT touch: §02A canonical (read-only); Wave-3 trio + 7c.13/7c.14 §section packages (read-only); harness; G4Card + G5Card models; parity_contract decorator; 7c.17b's outbound_envelope writer.

DO NOT introduce: new third-party deps; defensive enum widening; non-deterministic test fixtures; Marcus writer that violates M1-M4 lane separation.
```

---

## Operator dispatch checklist

1. ☐ 7c.5.G4 + 7c.5.G5 + 7c.3b done.
2. ☐ **7c.17b closed (HARD BLOCKER — verify in sprint-status.yaml).**
3. ☐ Wave-3 trio (7c.6/7c.7/7c.8) closed; 7c.13 + 7c.14 closed (sibling pattern references).
4. ☐ V7 v2 auto-fired post-Wave-3-trio close.
5. ☐ AMELIA-P2 freshness check.
6. ☐ Sandbox-AC validator PASS.
7. ☐ Sprint-status: ready-for-dev.
8. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_11b` + `app.gates.section_15`.
9. ☐ Dispatch (own batch; NOT parallel-safe with 7c.13/7c.14 in same batch).

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 STANDARD review subagent (~25-40 min). Single-story batch — no concurrent close-batch coordination needed. Standard-tier T11 review covers Marcus writer behavior + sanctum-alignment + cross-surface coordination + dual-FR fold rationale verification.
