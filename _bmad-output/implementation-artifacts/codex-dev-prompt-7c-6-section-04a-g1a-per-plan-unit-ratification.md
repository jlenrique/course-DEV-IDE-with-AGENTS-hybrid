# Codex dev-story prompt — Story 7c.6 (§04A G1A Per-Plan-Unit Ratification HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-6.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 1 (first Wave-3 HIL surface; canonical Wave-3 reference for sibling 7c.7 + 7c.8).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-READY post-V7-v1.1 codification.**

**Parallel-dispatch context:** This story is intended for concurrent dispatch with 7c.7 + 7c.8 (path-disjoint Wave-3 trio per C6 import-linter contract; each authors a NEW §section package). Per V7 v1.1 elevated_cap=N+3 (codified at slab-opener party-mode 2026-05-05; 3-voice round Murat+Winston+Amelia confirmed v1 elevation; 2-1 majority pre-ratified v2 with Murat+Winston revert/revisit clauses), all three lite-tier Wave-3 stories may dispatch concurrently.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE (NEW for Wave-3)

You may launch your own subagents to execute T2/T3/T4 work in parallel within this story (path-disjoint at the file level: `__init__.py` + `poll_surface.py` + `OperatorVerdict` model + JSON schema + 3 test files = ~7 new files, all in this story's scope). However, certain shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — IF dispatching concurrently with 7c.7 + 7c.8, three-way coordinate-or-sequence (per PARALLEL-DISPATCH GUARDRAIL #3, codified in `docs/dev-guide/migration-story-governance.json`). The main thread (or whichever worker integrates first) writes the union of all three new §section entries: `[app.gates.section_02a, app.gates.section_04a, app.gates.section_04_5, app.gates.section_04_55]`. Subsequent workers REBASE before commit.
- **`tests/schemas/operator_verdict/_harness.py`** — DO NOT modify (7c.4b D3 deliverable; canonical helper). Just import + use.
- **`tests/gates/section_02a/`** — DO NOT touch (7c.3b deliverable; canonical pattern reference).

If your runtime supports subagent spawning, prefer:
- 1 subagent: AC-A §section package + poll_surface.py
- 1 subagent: AC-B OperatorVerdict model + JSON schema regen
- 1 subagent: AC-C shape-pin + AC-D DSL-registration + 3-transport-parity tests
- Main thread: AC-E C6 modules list edit + T6 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.6 (Slab 7c Wave 3 slot 1; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical Wave-3 HIL predecessor; pattern reference).
3. **`app/gates/section_02a/poll_surface.py`** (canonical pattern; ~120 LOC; mirror inheritance + parity_contract decorator + helpers).
4. **`app/models/operator_verdict_section_02a.py`** (canonical OperatorVerdict variant).
5. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; 7c.4b D3 deliverable; READ-ONLY).
6. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** (canonical shape-pin).
7. **`tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`** + `test_g0_poll_surface_three_transport_parity.py` (canonical DSL-registration + 3-transport-parity tests).
8. `app/models/decision_cards/g1.py` (POST-7c.5.G1-migration; inherits DecisionCardBase per 0ec80df; G1Card consumed by §04A surface).
9. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax; 7c.4b D1 deliverable).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G1A alias mapping per §2: "G1A → G1 → Per-plan-unit ratification surface, section 04A").
11. `pyproject.toml::tool.importlinter` (C6 contract; modules list current state).
12. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening; canonical Path.write_text command in this prompt).
13. Governance JSON `7c-6` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1).

## T1 hard checkpoints

- 7c.5.G1 + 7c.3b done.
- `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
- `app.models.decision_cards.g1.G1Card` importable + inherits `DecisionCardBase` (per 0ec80df 2-class-regime migration).
- Class-conformance baseline: record observed (likely 19 post-G2C+G3+G4 close).
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_04a/__init__.py` (empty namespace)
- `app/gates/section_04a/poll_surface.py` (~120 LOC; mirror §02A)
- `app/models/operator_verdict_section_04a.py` (~50 LOC; Section04AOperatorVerdict + PlanUnitEditPayload + Section04AVerdictVerb + SECTION_04A_SURFACE_ID)
- `app/models/operator_verdict_section_04a.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_04a_shape.py` (FR-7c-49 harness)
- `tests/gates/section_04a/__init__.py` + `_helpers.py` + `test_g1a_poll_surface_dsl_registration.py` + `test_g1a_poll_surface_three_transport_parity.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_04a` to `tool.importlinter::contracts::C6::modules`. **Coordinate-or-sequence with 7c.7 + 7c.8 if concurrent.**

**Do NOT modify:**
- `app/gates/section_02a/` (canonical pattern; read-only)
- `tests/gates/section_02a/` (read-only)
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/models/decision_cards/` (G1Card consumed read-only)
- `app/parity/contracts/` (7c.4b D1 deliverables; read-only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_04a_g1a_poll", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G1")`. Per FR-7c-10: CLI mandatory; HTTP + MCP-stdio optional. Per ADR 0002 §3: alias_of forward syntax.
- **Closed verb Literal:** `Section04AVerdictVerb = Literal["approve", "edit", "reject"]` per FR-7c-10.
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection.
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section04AOperatorVerdict, surface_id="section_04a_g1a_poll", transports=["cli", "http", "mcp-stdio"])`.
- **C6 modules list append:** binding=hard per 7c.4b D5 P-1 patch. Coordinate-or-sequence with concurrent 7c.7+7c.8 dispatch.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count ≤5 + sibling-files only (all under app/gates/section_04a/ + app/models/operator_verdict_section_04a.* + tests/gates/section_04a/ + tests/schemas/operator_verdict/test_section_04a_shape.py + pyproject.toml C6 single-line append) + no schema/contract/governance touch (parity_contract registration is consumption, not extension; pyproject.toml C6 is a modules-list append, not a contract definition change).

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules from V6+V7)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories (no shape-pin in `tests/parity/test_decision_card_*` scope). DSL-registration test does NOT import LOCKSTEP_CHECK.
2. **Pattern-replication discipline.** Read `app/gates/section_02a/poll_surface.py` AND `app/models/operator_verdict_section_02a.py` AND `tests/schemas/operator_verdict/test_section_02a_shape.py` as canonical references. Mirror exactly except for §04A-specific surface_id + transport list + alias_of value.
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — coordinate-or-sequence with concurrent 7c.7+7c.8. NO blind concurrent overwrites.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields per G2A canonical. `Field(..., description=...)` on every field.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/schemas/operator_verdict/test_section_04a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md
.venv/Scripts/python.exe -m ruff check app/gates/section_04a/ app/models/operator_verdict_section_04a.py tests/gates/section_04a/ tests/schemas/operator_verdict/test_section_04a_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-6.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract registration evidence (alias_of="G1" + transport set) + §02A non-regression confirmation + class-conformance delta + broad-regression delta with per-failure attribution + (if concurrent dispatch) C6 modules list integration coordination evidence.

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.7+7c.8 reviews).

## Boundary

HALT on: 7c.5.G1 + 7c.3b not done; alias_of forward syntax not in parity_contract decorator; class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent worker (coordinate-or-sequence; do NOT silently overwrite).

DO NOT touch: §02A canonical (read-only); harness (7c.4b D3); G1Card model; parity_contract decorator (7c.4b D1).

DO NOT introduce: new third-party deps; defensive enum widening on verb or surface_id; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

1. ☐ 7c.5.G1 + 7c.3b done.
2. ☐ V7 v1.1 codification landed (current commit).
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC validator PASS.
5. ☐ Sprint-status: ready-for-dev.
6. ☐ If parallel-dispatching with 7c.7 + 7c.8: confirm Codex understands C6 modules list coordinate-or-sequence rule.
7. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.7 + 7c.8 land concurrently, spawn all three in parallel + close-batch commit when all three PASS.
