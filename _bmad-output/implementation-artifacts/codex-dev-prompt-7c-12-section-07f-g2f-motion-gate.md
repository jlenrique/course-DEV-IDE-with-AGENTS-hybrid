# Codex dev-story prompt — Story 7c.12 (§07F G2F Motion Gate HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec → Codex T1-T10 → drops `_codex-handoff/7c-12.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 10 (G2C-aliased fanout slot 4 of 4; closes G2C-aliased fanout).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-cbcd7e3.

**Parallel-dispatch context:** Concurrent dispatch with 7c.9 + 7c.10 + 7c.11 (G2C-aliased Wave-3 fanout — 4-story batch). AMELIA-P3 ≥30-min-stagger auto-satisfied under single-Codex. V7 v2 Murat triple-condition qualifies parallel dispatch.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

Same as 7c.9 prompt. Key rule: **`pyproject.toml::C6::modules` is 4-WAY coordinate-or-sequence** with 7c.9/7c.10/7c.11. DO NOT touch §02A canonical, Wave-3 trio + next-batch §section packages, or `tests/schemas/operator_verdict/_harness.py`.

---

```
Run bmad-dev-story on Story 7c.12 (Slab 7c Wave 3 slot 10; single-gate; lite T11; G2C-aliased fanout slot 4 of 4 — closes G2C-aliased fanout).

Spec: `_bmad-output/implementation-artifacts/migration-7c-12-section-07f-g2f-motion-gate.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (closest sibling — same CLI+HTTP-mandatory transport-set + approve/edit/reject verb-pattern).
4. **`app/gates/section_02a/poll_surface.py`** (canonical pattern).
5. **`app/gates/section_08b/poll_surface.py`** (Wave-3 sibling closest to 7c.12 — CLI+HTTP-mandatory match).
6. **`app/models/operator_verdict_section_08b.py`** (mirror this for `Section07FOperatorVerdict`; verb=Literal["approve","edit","reject"] + standard payload pattern).
7. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
8. `tests/schemas/operator_verdict/test_section_08b_shape.py` + Wave-3 sibling shape-pins.
9. `tests/gates/section_08b/*.py` + Wave-3 sibling DSL-registration + 3-transport-parity tests.
10. `app/models/decision_cards/g2c.py` (POST-G2C-migration; G2CCard consumed by §07F).
11. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax).
12. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2F alias mapping per §2: "G2F → G2C → Motion-clip approval surface, section 07F").
13. `pyproject.toml::tool.importlinter` (C6; current 6-entry state post-cbcd7e3).
14. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
15. Governance JSON `7c-12` entry.

## T1 hard checkpoints

- 7c.5.G2C + 7c.3b done.
- Wave-3 trio + next-batch closed (verified at 636fbff + cbcd7e3).
- `parity_contract` decorator accepts `alias_of` kwarg.
- `app.models.decision_cards.g2c.G2CCard` importable + inherits `DecisionCardBase`.
- Class-conformance + broad-regression baselines recorded.

## Files in scope

**New (7 files):**
- `app/gates/section_07f/__init__.py` (empty namespace)
- `app/gates/section_07f/poll_surface.py` (~120 LOC)
- `app/models/operator_verdict_section_07f.py` (~50 LOC; Section07FOperatorVerdict + MotionClipEditPayload + Section07FVerdictVerb + SECTION_07F_SURFACE_ID)
- `app/models/operator_verdict_section_07f.v1.schema.json`
- `tests/schemas/operator_verdict/test_section_07f_shape.py`
- `tests/gates/section_07f/__init__.py` + `_helpers.py` + `test_g2f_poll_surface_dsl_registration.py` + `test_g2f_poll_surface_three_transport_parity.py`

**Modified (1 file):** `pyproject.toml` — append `app.gates.section_07f` to C6. **4-way coordinate-or-sequence with 7c.9/7c.10/7c.11.**

**Do NOT modify:** Wave-3 trio + next-batch §section packages; §02A canonical; harness; G2CCard model; parity_contract decorator.

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_07f_g2f_motion_gate", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G2C")`. **Transport-set IDENTICAL to 7c.13** (CLI+HTTP mandatory + MCP-stdio optional) — use 7c.13 as primary structural reference.
- **Closed verb Literal:** `Section07FVerdictVerb = Literal["approve", "edit", "reject"]` (motion-clip approval gate).
- **Verb-payload consistency (`@model_validator(mode="after")`):** mirror §02A canonical 2-way pattern (approve no payload; edit requires edit_payload; reject requires reject_reason).
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. LF-only; NO BOM.
- **Re-emit helpers locally** per Wave-3 precedent.
- **C6 modules list:** 4-way coordinate-or-sequence.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC.

## PARALLEL-DISPATCH GUARDRAILS (binding)

Same six rules as 7c.9. Closest sibling for pattern-replication: **7c.13** (CLI+HTTP-mandatory + approve/edit/reject; mirror its OperatorVerdict and parity_contract registration).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_07f/ tests/schemas/operator_verdict/test_section_07f_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-12-section-07f-g2f-motion-gate.md
.venv/Scripts/python.exe -m ruff check app/gates/section_07f/ app/models/operator_verdict_section_07f.py tests/gates/section_07f/ tests/schemas/operator_verdict/test_section_07f_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-12.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract evidence (alias_of="G2C") + §02A + Wave-3 + sibling fanout non-regression + class-conformance delta + broad-regression delta + 4-way C6 union coordination evidence.

T11: Claude lite tier (~10-15 min); lite-batchable per AMEND-V3.

## Boundary

Same as 7c.9 with §07F substitutions. HALT on predecessor-not-done; class-conformance count != T1+1; broad-regression delta > 0 with new failure not git-log-verified-inherited; C6 modules list integration conflict.

DO NOT touch: §02A canonical; Wave-3 trio + next-batch + concurrent G2C-fanout-siblings §section packages; harness; G2CCard model; parity_contract decorator.

DO NOT introduce: new third-party deps; defensive enum widening; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

Same as 7c.9. Pre-stage pyproject.toml C6 modules list with all four §section entries (`section_05_5 + section_07b + section_07d + section_07f`).

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.9/7c.10/7c.11 land concurrently, spawn all four in parallel + close-batch commit when all four PASS.
