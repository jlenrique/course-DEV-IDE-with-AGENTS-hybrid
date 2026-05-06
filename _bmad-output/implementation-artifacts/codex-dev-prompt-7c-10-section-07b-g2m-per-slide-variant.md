# Codex dev-story prompt — Story 7c.10 (§07B G2M Per-Slide A/B Variant HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec → Codex T1-T10 → drops `_codex-handoff/7c-10.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 8 (G2C-aliased fanout slot 2 of 4).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-cbcd7e3.

**Parallel-dispatch context:** Concurrent dispatch with 7c.9 + 7c.11 + 7c.12 (G2C-aliased Wave-3 fanout — 4-story batch). AMELIA-P3 ≥30-min-stagger auto-satisfied under single-Codex per governance JSON. Per V7 v2 Murat triple-condition, parallel dispatch in-policy.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

Same as 7c.9 prompt — see `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-9-section-05-5-g2b-per-slide-mode.md` for full guidance. Key rule: **`pyproject.toml::C6::modules` is 4-WAY coordinate-or-sequence** with 7c.9/7c.11/7c.12 (post-state: 10 entries; pre-state: 6 entries). DO NOT touch §02A canonical, Wave-3 trio + next-batch §section packages, or `tests/schemas/operator_verdict/_harness.py`.

---

```
Run bmad-dev-story on Story 7c.10 (Slab 7c Wave 3 slot 8; single-gate; lite T11; G2C-aliased fanout slot 2 of 4).

Spec: `_bmad-output/implementation-artifacts/migration-7c-10-section-07b-g2m-per-slide-variant.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling — same select/edit/reject verb-pattern + 3-way model_validator).
4. **`app/gates/section_02a/poll_surface.py`** (canonical pattern).
5. **`app/gates/section_11/poll_surface.py`** (Wave-3 sibling closest to 7c.10's CLI-mandatory + select-verb pattern).
6. **`app/models/operator_verdict_section_11.py`** (mirror this for `Section07BOperatorVerdict`; verb=Literal["select","edit","reject"] + payload-required-iff-select pattern).
7. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
8. `tests/schemas/operator_verdict/test_section_11_shape.py` + Wave-3 sibling shape-pins.
9. `tests/gates/section_11/*.py` + Wave-3 sibling DSL-registration + 3-transport-parity tests.
10. `app/models/decision_cards/g2c.py` (POST-G2C-migration; G2CCard consumed by §07B).
11. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax).
12. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2M alias mapping per §2: "G2M → G2C → Per-slide A/B variant surface, section 07B").
13. `pyproject.toml::tool.importlinter` (C6; current 6-entry state post-cbcd7e3).
14. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
15. Governance JSON `7c-10` entry.

## T1 hard checkpoints

- 7c.5.G2C + 7c.3b done (verified at 0ec80df + f8fc1a8).
- Wave-3 trio + next-batch (7c.6/7/8 + 7c.13/14) closed (verified at 636fbff + cbcd7e3).
- `parity_contract` decorator accepts `alias_of` kwarg.
- `app.models.decision_cards.g2c.G2CCard` importable + inherits `DecisionCardBase`.
- Class-conformance + broad-regression baselines recorded.

## Files in scope

**New (7 files):**
- `app/gates/section_07b/__init__.py` (empty namespace)
- `app/gates/section_07b/poll_surface.py` (~120 LOC)
- `app/models/operator_verdict_section_07b.py` (~50 LOC; Section07BOperatorVerdict + PerSlideVariantPayload + PerSlideVariantEditPayload + Section07BVerdictVerb + SECTION_07B_SURFACE_ID)
- `app/models/operator_verdict_section_07b.v1.schema.json`
- `tests/schemas/operator_verdict/test_section_07b_shape.py`
- `tests/gates/section_07b/__init__.py` + `_helpers.py` + `test_g2m_poll_surface_dsl_registration.py` + `test_g2m_poll_surface_three_transport_parity.py`

**Modified (1 file):** `pyproject.toml` — append `app.gates.section_07b` to C6. **4-way coordinate-or-sequence with 7c.9/7c.11/7c.12.**

**Do NOT modify:** Wave-3 trio + next-batch §section packages; §02A canonical; harness; G2CCard model; parity_contract decorator.

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_07b_g2m_per_slide_variant", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G2C")`.
- **Closed verb Literal:** `Section07BVerdictVerb = Literal["select", "edit", "reject"]` (A/B variant picker).
- **Verb-payload consistency (`@model_validator(mode="after")`):**
  - `verb=select` → requires `select_payload: PerSlideVariantPayload` (with `selected_variant: Literal["A", "B"]`); forbids edit_payload + reject_reason.
  - `verb=edit` → requires `edit_payload: PerSlideVariantEditPayload`; forbids select_payload + reject_reason.
  - `verb=reject` → requires `reject_reason`; forbids select_payload + edit_payload.
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. LF-only; NO BOM.
- **Re-emit helpers locally** per Wave-3 precedent.
- **C6 modules list:** 4-way coordinate-or-sequence.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC.

## PARALLEL-DISPATCH GUARDRAILS (binding)

Same six rules as 7c.9. Closest sibling for pattern-replication: **7c.14** (CLI-mandatory + select/edit/reject + 3-way verb-payload consistency).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_07b/ tests/schemas/operator_verdict/test_section_07b_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-10-section-07b-g2m-per-slide-variant.md
.venv/Scripts/python.exe -m ruff check app/gates/section_07b/ app/models/operator_verdict_section_07b.py tests/gates/section_07b/ tests/schemas/operator_verdict/test_section_07b_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-10.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract evidence (alias_of="G2C") + §02A + Wave-3 + sibling fanout non-regression + class-conformance delta + broad-regression delta + 4-way C6 union coordination evidence.

T11: Claude lite tier (~10-15 min); lite-batchable per AMEND-V3.

## Boundary

Same as 7c.9 with §07B substitutions. HALT on predecessor-not-done; class-conformance count != T1+1; broad-regression delta > 0 with new failure not git-log-verified-inherited; C6 modules list integration conflict.

DO NOT touch: §02A canonical; Wave-3 trio + next-batch + concurrent G2C-fanout-siblings §section packages; harness; G2CCard model; parity_contract decorator.

DO NOT introduce: new third-party deps; defensive enum widening; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

Same as 7c.9. Pre-stage pyproject.toml C6 modules list with all four §section entries (`section_05_5 + section_07b + section_07d + section_07f`) before Codex begins.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.9/7c.11/7c.12 land concurrently, spawn all four in parallel + close-batch commit when all four PASS.
