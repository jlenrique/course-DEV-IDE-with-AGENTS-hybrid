# Codex dev-story prompt — Story 7c.18a (§06B Literal-Visual Operator Build HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-18a.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 5 — slot 1 (Wave-5 entry; first-of-pair with 7c.18b).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-DEFERRED** until 7c.17a + 7c.17b close (Wave 4 close-batch).

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.18b** (path-disjoint at file level: 7c.18a authors `section_06b`; 7c.18b authors `section_07c`). Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — both 7c.18a and 7c.18b qualify), parallel dispatch is in-policy under elevated_cap=N+3.

**NOTE: 7c.19 (§09 four-artifact lock) is the next Wave-5 story** but pre-authoring it depends on observing 7c.17a + 7c.17b close-batch substrate. Defer 7c.19 spec to next idle cycle.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4 work in parallel within this story (path-disjoint at the file level: ~7 new files). Shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — IF dispatching concurrently with 7c.18b, two-way coordinate-or-sequence (per PARALLEL-DISPATCH GUARDRAIL #3). Main thread (or whichever worker integrates first) writes the union of both new §section entries: `[..., app.gates.section_06b, app.gates.section_07c]`. Subsequent worker REBASES before commit.
- **`tests/schemas/operator_verdict/_harness.py`** — DO NOT modify (7c.4b D3 deliverable; canonical helper).
- **`tests/gates/section_02a/`** — DO NOT touch (7c.3b deliverable).
- **Wave-3 / next-batch / G2C-fanout §section packages** (`app/gates/section_*/` for 04a, 04_5, 04_55, 05_5, 07b, 07d, 07f, 08b, 11) — DO NOT touch (read-only sibling references).
- **Wave-4 Marcus-writer modules** (`app/marcus/orchestrator/writers/diagram_cards.py` + `fidelity_slides.py`) — DO NOT touch (7c.17a deliverables; READ-ONLY references).

If your runtime supports subagent spawning, prefer:
- 1 subagent: AC-A §section package + poll_surface.py
- 1 subagent: AC-B OperatorVerdict model + JSON schema regen
- 1 subagent: AC-C shape-pin + AC-D DSL-registration + 3-transport-parity tests
- Main thread: AC-E C6 modules list edit + T6 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.18a (Slab 7c Wave 5 slot 1; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-18a-section-06b-literal-visual-operator-build.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling — action-flavored verb-set `select/edit/reject` + 3-way verb-payload `model_validator(mode="after")`).
4. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 predecessor; `DiagramCard` + Vera-fidelity-flagged slide list shape).
5. **`app/gates/section_02a/poll_surface.py`** (canonical pattern reference).
6. **`app/gates/section_11/poll_surface.py`** (action-flavored sibling pattern).
7. **`app/models/operator_verdict_section_02a.py`** (canonical OperatorVerdict variant).
8. **`app/models/operator_verdict_section_11.py`** (action-verb sibling — 3-way verb-payload `model_validator(mode="after")` reference).
9. **`app/marcus/orchestrator/writers/diagram_cards.py`** (7c.17a; `DiagramCard` + `DiagramVisualKind` Literal — alignment-or-divergence decision for `SlideVisualSpecification` / `VisualSpecKind`).
10. **`app/marcus/orchestrator/writers/fidelity_slides.py`** (7c.17a; Vera-fidelity-flagged slide list shape — upstream-payload candidate for `display_literal_visual_targets`).
11. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; 7c.4b D3 deliverable; READ-ONLY).
12. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + `test_section_11_shape.py` (canonical + action-verb shape-pins).
13. **`tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`** + Wave-3 sibling analogues.
14. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract decorator + `alias_of` is OPTIONAL — confirm; §06B omits or passes None).
15. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (confirm §06B is NOT in family-aliases catalog; this is a NEW family).
16. `pyproject.toml::tool.importlinter` (C6 contract; modules list).
17. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
18. Governance JSON `7c-18a` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].

## T1 hard checkpoints

- 7c.17a + 7c.17b done (Wave-4 close-batch landed).
- §02A canonical + Wave-3 trio + Wave-3 next-batch + G2C-aliased fanout all closed (10 §section packages preceding §06B).
- `parity_contract` decorator accepts surface registration without `alias_of` (or with explicit `alias_of=None`); confirm by reading `_decorator.py`.
- ADR 0002 confirms §06B is NOT in family-aliases catalog (NEW family).
- 7c.17a's `DiagramCard` + `DiagramVisualKind` Literal importable + understood for alignment-vs-divergence decision.
- Class-conformance baseline: record observed (~19 + N for Wave-3 trio + next-batch + G2C-fanout shape-pins; recompute at T1).
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_06b/__init__.py` (empty namespace)
- `app/gates/section_06b/poll_surface.py` (~120 LOC; mirror §02A + Wave-3-trio re-emit pattern)
- `app/models/operator_verdict_section_06b.py` (~100 LOC; `Section06BOperatorVerdict` + `LiteralVisualBuildPayload` + `SlideVisualSpecification` + `LiteralVisualEditPayload` + `Section06BBuildVerb` + `VisualSpecKind` + `SECTION_06B_SURFACE_ID`)
- `app/models/operator_verdict_section_06b.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_06b_shape.py` (FR-7c-49 harness)
- `tests/gates/section_06b/__init__.py` + `_helpers.py` + `test_literal_visual_build_dsl_registration.py` + `test_literal_visual_build_three_transport_parity.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_06b` to `tool.importlinter::contracts::C6::modules`. **Coordinate-or-sequence with 7c.18b if concurrent.**

**Do NOT modify:**
- §02A + all closed Wave-3 / next-batch / G2C-fanout §section packages — read-only sibling references
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- 7c.17a Marcus writer modules (diagram_cards.py + fidelity_slides.py + slide_content.py) — read-only references
- `app/parity/contracts/` (read-only; consume parity_contract decorator)
- `app/models/decision_cards/` (no upstream Card for §06B; reference only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_06b_literal_visual_build", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"])`. **No `alias_of` kwarg** — §06B is a NEW family per ADR 0002. Verify the decorator accepts this; if it requires `alias_of` even for new families, pass `alias_of=None` explicitly.
- **Closed verb Literal:** `Section06BBuildVerb = Literal["submit", "edit", "discard"]` per FR-7c-26 operator-build framing (mirror 7c.14's action-flavored 3-way verb-set).
- **Closed `VisualSpecKind` Literal:** mirror 7c.17a's `DiagramVisualKind` minimum set `{"flowchart", "sequence", "comparison", "literal-visual"}`. T1 decision: alignment (import from 7c.17a, OR re-declare locally per C6 isolation pattern of canonical_model_bytes/compute_model_digest re-emit) vs partial divergence (document rationale at T10).
- **`decision_card_digest: str (sha256-hex)`** field semantics for build surface: digest of build_payload (operator-submitted content) OR digest of upstream artifact (e.g., upstream Vera fidelity-flagged slide list from 7c.17a's `gary-fidelity-slides.json`). T1-T9 decision documented in Completion Notes. Per §02A precedent, the field is a sha256-hex pattern; preserve the pattern, document the semantic at T10.
- **3-way verb-payload `model_validator(mode="after")` mirroring 7c.14:**
  - verb=submit ⇒ `build_payload` mandatory + `edit_payload` absent
  - verb=edit ⇒ `edit_payload` mandatory + `build_payload` absent
  - verb=discard ⇒ neither payload (operator abandon; no content to track)
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection. LF-only; verify NO BOM.
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section06BOperatorVerdict, surface_id="section_06b_literal_visual_build", transports=["cli", "http", "mcp-stdio"])`.
- **Re-emit helpers (NOT import from §02A):** Per Wave-3 trio + next-batch + G2C-fanout precedent, this story RE-EMITS `canonical_model_bytes` + `compute_model_digest` locally in `app/gates/section_06b/poll_surface.py`. C6 isolation rule.
- **C6 modules list append:** binding=hard. Coordinate-or-sequence with concurrent 7c.18b dispatch.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count = 5 + sibling-files only + new §section package + new OperatorVerdict variant + 3-transport schema-stability via FR-7c-49 harness + Codex T10 self-review clean + single-gate.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules from V6+V7)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories (no shape-pin in `tests/parity/test_decision_card_*` scope).
2. **Pattern-replication discipline.** Read §02A canonical + 7c.14 action-verb sibling + Wave-3 trio re-emit pattern. Mirror exactly except for §06B-specific surface_id + verb literal + payload shape.
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — coordinate-or-sequence with concurrent 7c.18b. NO blind concurrent overwrites.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields per G2A canonical. `Field(...)` with description on every field. UUID4-typed run_id. tz-aware submitted_at. sha256-hex decision_card_digest. 3-way verb-payload consistency `model_validator(mode="after")`.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required.

## Verification battery (T6)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_06b/ tests/schemas/operator_verdict/test_section_06b_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-18a-section-06b-literal-visual-operator-build.md
.venv/Scripts/python.exe -m ruff check app/gates/section_06b/ app/models/operator_verdict_section_06b.py tests/gates/section_06b/ tests/schemas/operator_verdict/test_section_06b_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-18a.ready-for-review.md`. Include: 7-file lockstep verification + parity_contract registration evidence (no alias_of OR alias_of=None + transport set CLI mandatory / HTTP+MCP-stdio optional) + §02A non-regression confirmation + Wave-3 + next-batch + G2C-fanout non-regression confirmation + Wave-4 Marcus-writer non-regression confirmation + class-conformance delta + broad-regression delta with per-failure attribution + (if concurrent dispatch) C6 modules list integration coordination evidence with 7c.18b + T1-T9 decisions: upstream-payload source for `display_literal_visual_targets` + `decision_card_digest` semantics for build-surface + alignment-vs-divergence verdict for `VisualSpecKind` (vs 7c.17a's `DiagramVisualKind`).

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.18b review).

## Boundary

HALT on: 7c.17a + 7c.17b not done; ADR 0002 indicates §06B IS in family-aliases catalog (rare; spec assumes new family — verify); class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent 7c.18b worker (coordinate-or-sequence; do NOT silently overwrite); parity_contract decorator rejects no-alias_of registration (rare; pass alias_of=None explicitly OR escalate as PRD-level finding).

DO NOT touch: §02A canonical (read-only); Wave-3 trio + next-batch + G2C-fanout §section packages (read-only); harness (7c.4b D3); 7c.17a Marcus writer modules; parity_contract decorator (7c.4b D1).

DO NOT introduce: new third-party deps; defensive enum widening on verb or surface_id or visual_kind; non-deterministic test fixtures; integration logic between §06B output and Gary dispatch (out of scope — emission shape only).
```

---

## Operator dispatch checklist

1. ☐ 7c.17a + 7c.17b done (Wave 4 close-batch landed).
2. ☐ AMELIA-P2 freshness check (re-run validator post-Wave-4 close).
3. ☐ Sandbox-AC validator PASS.
4. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=1 pre-author commit).
5. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_06b` + `app.gates.section_07c` (operator main-thread coordination — same precedent as Wave-3 trio main-thread C6 union).
6. ☐ If parallel-dispatching with 7c.18b: confirm Codex understands C6 modules list coordinate-or-sequence rule.
7. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.18b lands concurrently, spawn both in parallel + close-batch commit when both PASS.
