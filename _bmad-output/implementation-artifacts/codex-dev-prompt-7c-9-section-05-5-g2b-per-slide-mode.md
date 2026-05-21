# Codex dev-story prompt — Story 7c.9 (§05.5 G2B Per-Slide Presentation Mode HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-9.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 7 (first G2C-aliased fanout under V7 v2 Murat triple-condition).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-Wave-3-next-batch close (cbcd7e3).

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.10 + 7c.11 + 7c.12** (G2C-aliased Wave-3 fanout — 4-story batch). AMELIA-P3 ≥30-min-stagger normally required (G2C-aliased) but **AUTO-SATISFIED under single-Codex dispatch** per governance JSON `auto_satisfied_under: single_codex_dispatch` + memory `feedback_velocity_amendments_slab_7c.md`. Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — all four qualify), parallel dispatch is in-policy under elevated_cap=N+3.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4 work in parallel within this story (path-disjoint at the file level: ~7 new files all in this story's scope). Shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — 4-WAY coordinate-or-sequence with 7c.10/7c.11/7c.12 (per PARALLEL-DISPATCH GUARDRAIL #3). Main thread (or whichever worker integrates first) writes the union of all four new §section entries: `[..., section_05_5, section_07b, section_07d, section_07f]` (post-state: 10 entries total; pre-state: 6 entries from Wave-3 trio + next-batch). Subsequent workers REBASE before commit.
- **`tests/schemas/operator_verdict/_harness.py`** — DO NOT modify (7c.4b D3; READ-ONLY).
- **`tests/gates/section_02a/`** — DO NOT touch (7c.3b deliverable; canonical pattern reference).
- **Wave-3 trio + next-batch §section packages** (`section_04a`, `section_04_5`, `section_04_55`, `section_08b`, `section_11`) — DO NOT touch (7c.6/7/8/13/14 deliverables; sibling-pattern reference only).

If your runtime supports subagent spawning, prefer:
- 1 subagent: AC-A §section package + poll_surface.py
- 1 subagent: AC-B OperatorVerdict model + JSON schema regen
- 1 subagent: AC-C shape-pin + AC-D DSL-registration + 3-transport-parity tests
- Main thread: AC-E C6 modules list edit + T6 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.9 (Slab 7c Wave 3 slot 7; single-gate; lite T11; G2C-aliased fanout slot 1 of 4).

Spec: `_bmad-output/implementation-artifacts/migration-7c-9-section-05-5-g2b-per-slide-mode.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor; 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` + `migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling; same lite-tier follower pattern; just closed at cbcd7e3).
4. **`app/gates/section_02a/poll_surface.py`** (canonical pattern; ~120 LOC).
5. **`app/gates/section_04a/poll_surface.py`** + **`app/gates/section_08b/poll_surface.py`** (Wave-3 sibling re-emit patterns; CLI-mandatory match for 7c.9).
6. **`app/models/operator_verdict_section_02a.py`** (canonical OperatorVerdict variant).
7. **`app/models/operator_verdict_section_11.py`** (Wave-3 sibling; closest pattern match — verb=Literal["select","edit","reject"] + payload-required-iff-select; mirror this for `Section05_5OperatorVerdict`).
8. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
9. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + Wave-3 sibling shape-pins (canonical references).
10. **Wave-3 sibling DSL-registration + 3-transport-parity tests** (test pattern reference).
11. `app/models/decision_cards/g2c.py` (POST-7c.5.G2C-migration; inherits DecisionCardBase per 0ec80df; G2CCard consumed by §05.5 surface).
12. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax; 7c.4b D1 deliverable).
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2B alias mapping per §2: "G2B → G2C → Per-slide presentation mode surface, section 05.5").
14. `pyproject.toml::tool.importlinter` (C6 contract; current 6-entry state post-cbcd7e3).
15. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
16. Governance JSON `7c-9` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v2 promoted).

## T1 hard checkpoints

- 7c.5.G2C + 7c.3b done (verified at 0ec80df + f8fc1a8).
- Wave-3 trio (7c.6/7/8) + Wave-3 next-batch (7c.13/7c.14) closed (verified at 636fbff + cbcd7e3).
- `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
- `app.models.decision_cards.g2c.G2CCard` importable + inherits `DecisionCardBase` (per 0ec80df 2-class-regime migration).
- Class-conformance baseline: record observed (likely 19); recompute at T1.
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_05_5/__init__.py` (empty namespace)
- `app/gates/section_05_5/poll_surface.py` (~120 LOC; mirror §02A + Wave-3-sibling re-emit pattern)
- `app/models/operator_verdict_section_05_5.py` (~50 LOC; Section05_5OperatorVerdict + PerSlideModePayload + PerSlideModeEditPayload + Section05_5VerdictVerb + SECTION_05_5_SURFACE_ID)
- `app/models/operator_verdict_section_05_5.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_05_5_shape.py` (FR-7c-49 harness)
- `tests/gates/section_05_5/__init__.py` + `_helpers.py` + `test_g2b_poll_surface_dsl_registration.py` + `test_g2b_poll_surface_three_transport_parity.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_05_5` to `tool.importlinter::contracts::C6::modules`. **4-way coordinate-or-sequence with 7c.10/7c.11/7c.12.**

**Do NOT modify:**
- `app/gates/section_02a/` (canonical; read-only)
- `app/gates/section_04a/`, `section_04_5/`, `section_04_55/`, `section_08b/`, `section_11/` (Wave-3 trio + next-batch; read-only sibling references)
- `tests/gates/section_02a/` + Wave-3 sibling test dirs (read-only)
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/models/decision_cards/` (G2CCard consumed read-only)
- `app/parity/contracts/` (7c.4b D1 deliverables; read-only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_05_5_g2b_per_slide_mode", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G2C")`. Per FR-7c-13: CLI mandatory; HTTP + MCP-stdio optional. Per ADR 0002 §3: alias_of forward syntax. **Transport-set IDENTICAL to 7c.6 + 7c.14** (CLI mandatory only).
- **Closed verb Literal:** `Section05_5VerdictVerb = Literal["select", "edit", "reject"]` (mode-picker action verb; mirror 7c.14 pattern).
- **Verb-payload consistency (`@model_validator(mode="after")`):**
  - `verb=select` → requires `select_payload: PerSlideModePayload` (with `selected_mode: Literal["narrated-deck", "motion-enabled-narrated-lesson"]`); forbids `edit_payload` and `reject_reason`.
  - `verb=edit` → requires `edit_payload: PerSlideModeEditPayload`; forbids `select_payload` and `reject_reason`.
  - `verb=reject` → requires `reject_reason`; forbids `select_payload` and `edit_payload`.
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection. LF-only; verify NO BOM.
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section05_5OperatorVerdict, surface_id="section_05_5_g2b_per_slide_mode", transports=["cli", "http", "mcp-stdio"])`.
- **Re-emit helpers (NOT import from §02A):** Per Wave-3 trio + next-batch precedent.
- **C6 modules list append:** binding=hard. **4-way coordinate-or-sequence** with concurrent 7c.10/7c.11/7c.12.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count ≤5 + sibling-files only + no schema/contract/governance touch.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories.
2. **Pattern-replication discipline.** Mirror §02A canonical AND Wave-3-trio + 7c.13/7c.14 sibling patterns. 7c.14 is closest match for verb-pattern (select/edit/reject + 3-way `model_validator(mode="after")`).
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — 4-way coordinate-or-sequence with concurrent G2C-aliased siblings.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields. `Field(..., description=...)` on every field. UUID4-typed run_id. tz-aware submitted_at. sha256-hex decision_card_digest.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_05_5/ tests/schemas/operator_verdict/test_section_05_5_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-9-section-05-5-g2b-per-slide-mode.md
.venv/Scripts/python.exe -m ruff check app/gates/section_05_5/ app/models/operator_verdict_section_05_5.py tests/gates/section_05_5/ tests/schemas/operator_verdict/test_section_05_5_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-9.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract registration evidence (alias_of="G2C" + transport set CLI mandatory) + §02A + Wave-3 sibling non-regression confirmation + class-conformance delta + broad-regression delta + 4-way C6 union coordination evidence.

T11: Claude lite tier (~10-15 min); lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.10/7c.11/7c.12 reviews.

## Boundary

HALT on: 7c.5.G2C + 7c.3b not done; Wave-3 trio + next-batch not closed; alias_of forward syntax not in parity_contract decorator; class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent worker.

DO NOT touch: §02A canonical (read-only); Wave-3 trio + next-batch §section packages (read-only); harness; G2CCard model; parity_contract decorator.

DO NOT introduce: new third-party deps; defensive enum widening; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

1. ☐ 7c.5.G2C + 7c.3b done.
2. ☐ Wave-3 trio + next-batch (7c.6/7/8 + 7c.13/14) closed.
3. ☐ V7 v2 in effect (auto-fired post-Wave-3-trio close).
4. ☐ AMELIA-P2 freshness check.
5. ☐ Sandbox-AC validator PASS.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_05_5 + section_07b + section_07d + section_07f` (operator main-thread coordination — same precedent as Wave-3 trio + next-batch).
8. ☐ If parallel-dispatching with 7c.10/7c.11/7c.12: confirm Codex understands 4-way C6 modules list coordinate-or-sequence rule.
9. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.10/7c.11/7c.12 land concurrently, spawn all four in parallel + close-batch commit when all four PASS (~15-20 min wall-clock total).
