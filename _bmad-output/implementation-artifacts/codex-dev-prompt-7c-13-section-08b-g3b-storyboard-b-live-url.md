# Codex dev-story prompt — Story 7c.13 (§08B G3B Storyboard B + Live-URL HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-13.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 4 (post-Wave-3-trio close; first lookahead-tier=1 Wave-3 follower under V7 v2).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-DEFERRED** until Wave-3 trio (7c.6/7c.7/7c.8) close-batch lands and V7 v2 auto-fires.

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.14** (path-disjoint; both author NEW §section packages — section_08b and section_11). Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — both 7c.13 and 7c.14 qualify), parallel dispatch is in-policy under elevated_cap=N+3.

**NOTE: 7c.15 is NOT parallel-safe with 7c.13/7c.14** in the same batch — 7c.15 is lookahead_tier=2 + t11_tier=standard + has unmet predecessor 7c.17b (Wave-4 backlog). Defer 7c.15 dispatch to a separate batch after 7c.17b closes.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4 work in parallel within this story (path-disjoint at the file level: `__init__.py` + `poll_surface.py` + `OperatorVerdict` model + JSON schema + 3 test files = ~7 new files, all in this story's scope). Shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — IF dispatching concurrently with 7c.14, two-way coordinate-or-sequence (per PARALLEL-DISPATCH GUARDRAIL #3). The main thread (or whichever worker integrates first) writes the union of both new §section entries: `[..., app.gates.section_08b, app.gates.section_11]`. Subsequent worker REBASES before commit.
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
Run bmad-dev-story on Story 7c.13 (Slab 7c Wave 3 slot 4; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor; 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md` (Wave-3 trio sibling; same lite-tier follower pattern).
4. **`app/gates/section_02a/poll_surface.py`** (canonical pattern; ~120 LOC; mirror inheritance + parity_contract decorator + helpers).
5. **`app/gates/section_04a/poll_surface.py`** (Wave-3 sibling; precedent for re-emit-helpers C6-isolation pattern).
6. **`app/models/operator_verdict_section_02a.py`** (canonical OperatorVerdict variant).
7. **`app/models/operator_verdict_section_04a.py`** (Wave-3 sibling; mirror this for `Section08BOperatorVerdict`).
8. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; 7c.4b D3 deliverable; READ-ONLY).
9. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + `test_section_04a_shape.py` (canonical + Wave-3 shape-pins).
10. **`tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`** + `test_g0_poll_surface_three_transport_parity.py` + Wave-3 sibling analogues at `tests/gates/section_04a/`.
11. `app/models/decision_cards/g3.py` (POST-7c.5.G3-migration; inherits DecisionCardBase per 0ec80df; G3Card consumed by §08B surface).
12. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax; 7c.4b D1 deliverable).
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G3B alias mapping per §2: "G3B → G3 → Storyboard B + live-URL review surface, section 08B").
14. `pyproject.toml::tool.importlinter` (C6 contract; modules list current state — post-Wave-3 trio: `[section_02a, section_04a, section_04_5, section_04_55]`).
15. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening; canonical Path.write_text command in this prompt).
16. Governance JSON `7c-13` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1 elevated; V7 v2 auto-fired post-Wave-3-trio close).

## T1 hard checkpoints

- 7c.5.G3 + 7c.3b done (verified at 0ec80df + f8fc1a8).
- Wave-3 trio (7c.6/7c.7/7c.8) closed (close-batch commit verified by operator pre-dispatch).
- `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
- `app.models.decision_cards.g3.G3Card` importable + inherits `DecisionCardBase` (per 0ec80df 2-class-regime migration).
- Class-conformance baseline: record observed (likely 19 + N for Wave-3 trio's added shape-pins; recompute at T1).
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_08b/__init__.py` (empty namespace)
- `app/gates/section_08b/poll_surface.py` (~120 LOC; mirror §02A + Wave-3-trio re-emit pattern for digest helpers)
- `app/models/operator_verdict_section_08b.py` (~50 LOC; Section08BOperatorVerdict + StoryboardBEditPayload + Section08BVerdictVerb + SECTION_08B_SURFACE_ID)
- `app/models/operator_verdict_section_08b.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_08b_shape.py` (FR-7c-49 harness)
- `tests/gates/section_08b/__init__.py` + `_helpers.py` + `test_g3b_poll_surface_dsl_registration.py` + `test_g3b_poll_surface_three_transport_parity.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_08b` to `tool.importlinter::contracts::C6::modules`. **Coordinate-or-sequence with 7c.14 if concurrent.**

**Do NOT modify:**
- `app/gates/section_02a/` (canonical pattern; read-only)
- `app/gates/section_04a/`, `section_04_5/`, `section_04_55/` (Wave-3 trio; read-only sibling references)
- `tests/gates/section_02a/` + Wave-3 trio test dirs (read-only)
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/models/decision_cards/` (G3Card consumed read-only)
- `app/parity/contracts/` (7c.4b D1 deliverables; read-only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_08b_g3b_poll", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G3")`. Per FR-7c-17: CLI + HTTP mandatory; MCP-stdio optional. Per ADR 0002 §3: alias_of forward syntax.
- **Closed verb Literal:** `Section08BVerdictVerb = Literal["approve", "edit", "reject"]` per FR-7c-17 (storyboard review pattern; mirror §02A approve/edit/reject).
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection. LF-only; verify NO BOM (per 7c.5.G2C precedent — same Codex prompt produced different EOL contexts; pin LF deterministically).
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section08BOperatorVerdict, surface_id="section_08b_g3b_poll", transports=["cli", "http", "mcp-stdio"])`.
- **Re-emit helpers (NOT import from §02A):** Per Wave-3 trio precedent (7c.6/7c.7/7c.8 all re-emitted `canonical_model_bytes` + `compute_model_digest` locally rather than importing across §section boundary), this story RE-EMITS the same helpers in `app/gates/section_08b/poll_surface.py`. Rationale: C6 import-linter independence — HIL surfaces may not import each other across surfaces. Helpers are byte-identical to §02A canonical.
- **C6 modules list append:** binding=hard per 7c.4b D5 P-1 patch. Coordinate-or-sequence with concurrent 7c.14 dispatch.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count ≤5 + sibling-files only + no schema/contract/governance touch (parity_contract registration is consumption, not extension; pyproject.toml C6 is a modules-list append).

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules from V6+V7)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories (no shape-pin in `tests/parity/test_decision_card_*` scope). DSL-registration test does NOT import LOCKSTEP_CHECK.
2. **Pattern-replication discipline.** Read `app/gates/section_02a/poll_surface.py` AND `app/gates/section_04a/poll_surface.py` (Wave-3 trio precedent) AND `app/models/operator_verdict_section_02a.py` AND `tests/schemas/operator_verdict/test_section_02a_shape.py` as canonical references. Mirror exactly except for §08B-specific surface_id + transport list + alias_of value + verb literal.
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — coordinate-or-sequence with concurrent 7c.14. NO blind concurrent overwrites.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields per G2A canonical. `Field(..., description=...)` on every field. UUID4-typed run_id. tz-aware submitted_at. sha256-hex decision_card_digest. verb-payload consistency `model_validator(mode="after")`.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required for any failures present.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_08b/ tests/schemas/operator_verdict/test_section_08b_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md
.venv/Scripts/python.exe -m ruff check app/gates/section_08b/ app/models/operator_verdict_section_08b.py tests/gates/section_08b/ tests/schemas/operator_verdict/test_section_08b_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-13.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract registration evidence (alias_of="G3" + transport set CLI+HTTP mandatory / MCP-stdio optional) + §02A non-regression confirmation + Wave-3 trio non-regression confirmation + class-conformance delta + broad-regression delta with per-failure attribution + (if concurrent dispatch) C6 modules list integration coordination evidence.

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.14 review).

## Boundary

HALT on: 7c.5.G3 + 7c.3b not done; Wave-3 trio not closed; alias_of forward syntax not in parity_contract decorator; class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent worker (coordinate-or-sequence; do NOT silently overwrite).

DO NOT touch: §02A canonical (read-only); Wave-3 trio §section packages (read-only); harness (7c.4b D3); G3Card model; parity_contract decorator (7c.4b D1).

DO NOT introduce: new third-party deps; defensive enum widening on verb or surface_id; non-deterministic test fixtures.
```

---

## Operator dispatch checklist

1. ☐ 7c.5.G3 + 7c.3b done.
2. ☐ Wave-3 trio (7c.6/7c.7/7c.8) closed via close-batch commit.
3. ☐ V7 v2 auto-fired post-Wave-3-trio close (`wave_3_closed_count >= 3`).
4. ☐ AMELIA-P2 freshness check.
5. ☐ Sandbox-AC validator PASS.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_08b` + `app.gates.section_11` (operator main-thread coordination — same precedent as Wave-3 trio main-thread C6 union).
8. ☐ If parallel-dispatching with 7c.14: confirm Codex understands C6 modules list coordinate-or-sequence rule.
9. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.14 lands concurrently, spawn both in parallel + close-batch commit when both PASS.
