# Codex dev-story prompt — Story 7c.14 (§11 G4A Voice-Selection HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-14.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 5 (post-Wave-3-trio close; second lookahead-tier=1 Wave-3 follower under V7 v2; concurrent-eligible with 7c.13).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-DEFERRED** until Wave-3 trio (7c.6/7c.7/7c.8) close-batch lands and V7 v2 auto-fires.

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.13** (path-disjoint; both author NEW §section packages — section_08b and section_11). Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — both 7c.13 and 7c.14 qualify), parallel dispatch is in-policy under elevated_cap=N+3.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4 work in parallel within this story (path-disjoint at the file level: ~7 new files, all in this story's scope). Shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — IF dispatching concurrently with 7c.13, two-way coordinate-or-sequence (per PARALLEL-DISPATCH GUARDRAIL #3). The main thread (or whichever worker integrates first) writes the union of both new §section entries: `[..., app.gates.section_08b, app.gates.section_11]`. Subsequent worker REBASES before commit.
- **`tests/schemas/operator_verdict/_harness.py`** — DO NOT modify (7c.4b D3 deliverable; canonical helper). Just import + use.
- **`tests/gates/section_02a/`** — DO NOT touch (7c.3b deliverable; canonical pattern reference).
- **Wave-3 trio §section packages** (`app/gates/section_04a/`, `section_04_5/`, `section_04_55/`) — DO NOT touch (7c.6/7c.7/7c.8 deliverables; sibling-pattern reference only).

If your runtime supports subagent spawning, prefer:
- 1 subagent: AC-A §section package + poll_surface.py
- 1 subagent: AC-B OperatorVerdict model + JSON schema regen
- 1 subagent: AC-C shape-pin + AC-D DSL-registration + 3-transport-parity tests
- Main thread: AC-E C6 modules list edit + T6 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.14 (Slab 7c Wave 3 slot 5; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor; 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md` (Wave-3 sibling; closest transport-set match — CLI mandatory only).
4. **`app/gates/section_02a/poll_surface.py`** (canonical pattern; ~120 LOC).
5. **`app/gates/section_04a/poll_surface.py`** (Wave-3 sibling; precedent for re-emit-helpers C6-isolation pattern + CLI-mandatory transport set).
6. **`app/models/operator_verdict_section_02a.py`** (canonical OperatorVerdict variant).
7. **`app/models/operator_verdict_section_04a.py`** (Wave-3 sibling; mirror this for `Section11OperatorVerdict`).
8. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
9. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + `test_section_04a_shape.py` (canonical + Wave-3 shape-pins).
10. **`tests/gates/section_02a/*.py`** + `tests/gates/section_04a/*.py` (canonical + Wave-3 DSL-registration + 3-transport-parity tests).
11. `app/models/decision_cards/g4.py` (POST-7c.5.G4-migration; inherits DecisionCardBase per 0ec80df; voice-selection-payload schema reference).
12. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax; 7c.4b D1 deliverable).
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G4A alias mapping per §2: "G4A → G4 → ElevenLabs voice-selection surface, section 11").
14. `pyproject.toml::tool.importlinter` (C6 contract; modules list current state).
15. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
16. Governance JSON `7c-14` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1 elevated; V7 v2 auto-fired post-Wave-3-trio close).

## T1 hard checkpoints

- 7c.5.G4 + 7c.3b done (verified at 0ec80df + f8fc1a8).
- Wave-3 trio (7c.6/7c.7/7c.8) closed (close-batch commit verified by operator pre-dispatch).
- `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
- `app.models.decision_cards.g4.G4Card` importable + inherits `DecisionCardBase` (per 0ec80df 2-class-regime migration).
- Class-conformance baseline: record observed; recompute at T1.
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_11/__init__.py` (empty namespace)
- `app/gates/section_11/poll_surface.py` (~120 LOC; mirror §02A + Wave-3-trio re-emit pattern for digest helpers)
- `app/models/operator_verdict_section_11.py` (~50 LOC; Section11OperatorVerdict + VoiceSelectionPayload + VoiceSelectionEditPayload + Section11VerdictVerb + SECTION_11_SURFACE_ID)
- `app/models/operator_verdict_section_11.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_11_shape.py` (FR-7c-49 harness)
- `tests/gates/section_11/__init__.py` + `_helpers.py` + `test_g4a_poll_surface_dsl_registration.py` + `test_g4a_poll_surface_three_transport_parity.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_11` to `tool.importlinter::contracts::C6::modules`. **Coordinate-or-sequence with 7c.13 if concurrent.**

**Do NOT modify:**
- `app/gates/section_02a/` (canonical pattern; read-only)
- `app/gates/section_04a/`, `section_04_5/`, `section_04_55/` (Wave-3 trio; read-only sibling references)
- `tests/gates/section_02a/` + Wave-3 trio test dirs (read-only)
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/models/decision_cards/` (G4Card consumed read-only)
- `app/parity/contracts/` (7c.4b D1 deliverables; read-only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_11_g4a_voice_selection", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G4")`. Per FR-7c-18: CLI mandatory; HTTP + MCP-stdio optional. Per ADR 0002 §3: alias_of forward syntax. **Transport-set IDENTICAL to 7c.6** (CLI mandatory only) — use 7c.6 as primary structural reference.
- **Closed verb Literal:** `Section11VerdictVerb = Literal["select", "edit", "reject"]` per FR-7c-18 (voice-selection action verb; "select" is the natural voice-picker action).
- **Verb-payload consistency (`@model_validator(mode="after")`):**
  - `verb=select` → requires `select_payload: VoiceSelectionPayload` (with `selected_voice_id`); forbids `edit_payload` and `reject_reason`.
  - `verb=edit` → requires `edit_payload: VoiceSelectionEditPayload`; forbids `select_payload` and `reject_reason`.
  - `verb=reject` → requires `reject_reason`; forbids `select_payload` and `edit_payload`.
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection. LF-only; verify NO BOM.
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section11OperatorVerdict, surface_id="section_11_g4a_voice_selection", transports=["cli", "http", "mcp-stdio"])`.
- **Re-emit helpers (NOT import from §02A):** Per Wave-3 trio precedent.
- **C6 modules list append:** binding=hard. Coordinate-or-sequence with concurrent 7c.13 dispatch.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count ≤5 + sibling-files only + no schema/contract/governance touch.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories.
2. **Pattern-replication discipline.** Read §02A canonical AND §04A Wave-3 sibling (closest transport-set match). Mirror exactly except for §11-specific surface_id + verb literal + payload-types ({Voice}SelectionPayload + VoiceSelectionEditPayload).
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — coordinate-or-sequence with concurrent 7c.13.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields (selected_voice_id + voice_selection_id + operator_id). `Field(..., description=...)` on every field. UUID4-typed run_id. tz-aware submitted_at. sha256-hex decision_card_digest.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_11/ tests/schemas/operator_verdict/test_section_11_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md
.venv/Scripts/python.exe -m ruff check app/gates/section_11/ app/models/operator_verdict_section_11.py tests/gates/section_11/ tests/schemas/operator_verdict/test_section_11_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-14.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract registration evidence (alias_of="G4" + transport set CLI mandatory / HTTP+MCP-stdio optional) + §02A non-regression confirmation + Wave-3 trio non-regression confirmation + class-conformance delta + broad-regression delta with per-failure attribution + (if concurrent dispatch) C6 modules list integration coordination evidence.

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.13 review).

## Boundary

HALT on: 7c.5.G4 + 7c.3b not done; Wave-3 trio not closed; alias_of forward syntax not in parity_contract decorator; class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent worker.

DO NOT touch: §02A canonical (read-only); Wave-3 trio §section packages (read-only); harness; G4Card model; parity_contract decorator.

DO NOT introduce: new third-party deps; defensive enum widening on verb or surface_id; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

1. ☐ 7c.5.G4 + 7c.3b done.
2. ☐ Wave-3 trio (7c.6/7c.7/7c.8) closed via close-batch commit.
3. ☐ V7 v2 auto-fired post-Wave-3-trio close.
4. ☐ AMELIA-P2 freshness check.
5. ☐ Sandbox-AC validator PASS.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_08b` + `app.gates.section_11` (operator main-thread coordination — same precedent as Wave-3 trio main-thread C6 union).
8. ☐ If parallel-dispatching with 7c.13: confirm Codex understands C6 modules list coordinate-or-sequence rule.
9. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.13 lands concurrently, spawn both in parallel + close-batch commit when both PASS.
