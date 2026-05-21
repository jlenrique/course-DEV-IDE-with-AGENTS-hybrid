# Codex dev-story prompt — Story 7c.18b (§07C Storyboard Build + HTML Reviewer Surface; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-18b.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 5 — slot 2 (Wave-5 entry; second-of-pair with 7c.18a).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-DEFERRED** until 7c.17a + 7c.17b close (Wave 4 close-batch).

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.18a** (path-disjoint at file level). Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — both qualify), parallel dispatch is in-policy under elevated_cap=N+3.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4/T5 work in parallel within this story (path-disjoint at file level: ~8 new files including HTML emitter + emitter test). Shared-file edits MUST be serialized:

- **`pyproject.toml::tool.importlinter::contracts::C6::modules`** — IF dispatching concurrently with 7c.18a, two-way coordinate-or-sequence (PARALLEL-DISPATCH GUARDRAIL #3). Main thread (or whichever worker integrates first) writes the union of both new §section entries: `[..., app.gates.section_06b, app.gates.section_07c]`. Subsequent worker REBASES before commit.
- **`tests/schemas/operator_verdict/_harness.py`** — DO NOT modify (7c.4b D3 deliverable; canonical helper).
- **`tests/gates/section_02a/`** — DO NOT touch.
- **Wave-3 / next-batch / G2C-fanout §section packages** — DO NOT touch (read-only sibling references).
- **Wave-4 Marcus-writer modules** — DO NOT touch.
- **§08B poll-surface (`app/gates/section_08b/`)** — DO NOT modify (read-only; this story's HTML output feeds §08B's display).

If your runtime supports subagent spawning, prefer:
- 1 subagent: AC-A §section package + poll_surface.py
- 1 subagent: AC-B OperatorVerdict model + JSON schema regen
- 1 subagent: AC-C HTML reviewer artifact emitter helper
- 1 subagent: AC-D shape-pin + AC-E DSL-registration + 3-transport-parity + emitter-determinism tests
- Main thread: AC-E C6 modules list edit + T7 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.18b (Slab 7c Wave 5 slot 2; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-18b-section-07c-storyboard-build-html-reviewer-surface.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-18a-section-06b-literal-visual-operator-build.md` (sibling spec; same operator-build pattern; same pre-author batch).
3. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
4. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (DOWNSTREAM consumer of §07C's HTML artifact).
5. `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling — action-flavored verb-set + 3-way verb-payload `model_validator`).
6. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 predecessor; `GarySlideContent` shape upstream).
7. **`app/gates/section_02a/poll_surface.py`** (canonical pattern reference).
8. **`app/gates/section_11/poll_surface.py`** (action-flavored sibling pattern).
9. **`app/gates/section_08b/poll_surface.py`** (downstream consumer of §07C output — confirm artifact contract assumptions).
10. **`app/models/operator_verdict_section_02a.py`** + **`app/models/operator_verdict_section_11.py`** (canonical + action-verb references).
11. **`app/marcus/orchestrator/writers/slide_content.py`** (7c.17a; `GarySlideContent` shape — upstream slide-content source for `display_storyboard_targets`).
12. **`tests/schemas/operator_verdict/_harness.py`** (FR-7c-49 harness; READ-ONLY).
13. **`tests/schemas/operator_verdict/test_section_02a_shape.py`** + Wave-3 + next-batch shape-pins.
14. **`tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`** + Wave-3 sibling analogues.
15. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract decorator + `alias_of` optional kwarg).
16. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (confirm §07C is NOT in family-aliases catalog).
17. `pyproject.toml::tool.importlinter` (C6 contract).
18. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
19. Governance JSON `7c-18b` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].

## T1 hard checkpoints

- 7c.17a + 7c.17b done (Wave-4 close-batch landed).
- §02A canonical + Wave-3 trio + Wave-3 next-batch + G2C-aliased fanout + 7c.13 + 7c.14 all closed (preceding §section packages).
- §08B poll-surface importable + understood for downstream-consumer artifact contract.
- 7c.17a's `GarySlideContent` shape importable + understood for upstream slide-content source.
- `parity_contract` decorator accepts surface registration without `alias_of` (or with explicit `alias_of=None`).
- ADR 0002 confirms §07C is NOT in family-aliases catalog (NEW family).
- Class-conformance baseline: record observed (~19 + N for closed Wave-3 + next-batch + G2C-fanout + 7c.18a if landed first; recompute at T1).
- Broad-regression baseline: re-run.

## Files in scope

**New (8 files):**
- `app/gates/section_07c/__init__.py` (empty namespace)
- `app/gates/section_07c/poll_surface.py` (~120 LOC; mirror §02A + Wave-3-trio re-emit pattern)
- `app/gates/section_07c/storyboard_html_emitter.py` (~60 LOC; deterministic HTML emitter — Python stdlib only) **OR** inlined in poll_surface.py (T1-T9 size decision)
- `app/models/operator_verdict_section_07c.py` (~120 LOC; `Section07COperatorVerdict` + `StoryboardBuildPayload` + `StoryboardEditPayload` + `Section07CBuildVerb` + `SECTION_07C_SURFACE_ID`)
- `app/models/operator_verdict_section_07c.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_07c_shape.py` (FR-7c-49 harness)
- `tests/gates/section_07c/__init__.py` + `_helpers.py` + `test_storyboard_build_dsl_registration.py` + `test_storyboard_build_three_transport_parity.py` + `test_storyboard_html_emitter_determinism.py`

**Modified (1 file):**
- `pyproject.toml` — append `app.gates.section_07c` to `tool.importlinter::contracts::C6::modules`. **Coordinate-or-sequence with 7c.18a if concurrent.**

**Do NOT modify:**
- §02A canonical (read-only)
- All closed Wave-3 / next-batch / G2C-fanout §section packages — read-only sibling references
- §08B poll-surface (downstream consumer; read-only)
- 7c.17a Marcus writer modules — read-only references
- `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; read-only)
- `app/parity/contracts/` (read-only)
- `app/models/decision_cards/` (no upstream Card for §07C; reference only)

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_07c_storyboard_build", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"])`. **No `alias_of`** — §07C is a new family.
- **Closed verb Literal:** `Section07CBuildVerb = Literal["submit", "edit", "discard"]` per FR-7c-27 operator-build framing (mirror 7c.18a sibling pattern).
- **3-way verb-payload `model_validator(mode="after")` mirroring 7c.18a / 7c.14:**
  - verb=submit ⇒ `build_payload` mandatory + `edit_payload` absent
  - verb=edit ⇒ `edit_payload` mandatory + `build_payload` absent
  - verb=discard ⇒ neither payload
- **`storyboard_html_path` validator:** strip-then-non-empty + `.html` suffix check via `field_validator` per Pydantic-v2 idiom.
- **`storyboard_html_digest: str` (sha256-hex)**: tamper-evidence per NFR-7c-S1; computed at emit time; verified at submit time. Use the existing sha256-hex pattern from §02A canonical (`Field(..., pattern=r"^[0-9a-f]{64}$")`).
- **HTML emitter determinism (AC-C):** Python stdlib only — no Jinja, no MarkupSafe addition. Use `html.escape` + string-template + manual `\n` line endings (NO `\r\n`); write via `Path.write_text(..., encoding="utf-8", newline="\n")`. Test asserts sha256-stable bytes across two emitter invocations with identical input.
- **JSON schema regen:** Path.write_text(... encoding="utf-8") per A18. NO PowerShell `>` redirection. LF-only; verify NO BOM.
- **Shape-pin via FR-7c-49 harness:** `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section07COperatorVerdict, surface_id="section_07c_storyboard_build", transports=["cli", "http", "mcp-stdio"])`.
- **Re-emit helpers:** Per Wave-3 + next-batch + G2C-fanout precedent, RE-EMIT `canonical_model_bytes` + `compute_model_digest` locally in `app/gates/section_07c/poll_surface.py`. C6 isolation rule.
- **C6 modules list append:** binding=hard. Coordinate-or-sequence with concurrent 7c.18a dispatch.
- **K-target 1.3× ≈ 580 LOC ceiling.** Estimate ~450 LOC actual.
- **T11 lite tier:** AC count = 5 + sibling-files only + new §section package + new OperatorVerdict variant + HTML emitter is standalone helper (Python stdlib only — no new deps) + 3-transport schema-stability + Codex T10 self-review clean + single-gate.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch)

1. **AMEND-7d-i AST-scan compliance.** N/A for HIL surface stories.
2. **Pattern-replication discipline.** Read §02A canonical + 7c.14 action-verb sibling + 7c.18a sibling spec + Wave-3 trio re-emit pattern. Mirror exactly except for §07C-specific surface_id + verb literal + payload shape + HTML emitter helper.
3. **Shared-file integration ordering.** `pyproject.toml` C6 modules list — coordinate-or-sequence with concurrent 7c.18a. NO blind concurrent overwrites.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on string fields per G2A canonical. `Field(...)` with description. UUID4-typed run_id. tz-aware submitted_at. sha256-hex `decision_card_digest` + sha256-hex `storyboard_html_digest`. 3-way verb-payload consistency `model_validator(mode="after")`.
5. **Class-conformance arithmetic.** +1 if landing alone; +N if landing in concurrent-batch. Document at T10.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T7)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_07c/ tests/schemas/operator_verdict/test_section_07c_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-18b-section-07c-storyboard-build-html-reviewer-surface.md
.venv/Scripts/python.exe -m ruff check app/gates/section_07c/ app/models/operator_verdict_section_07c.py tests/gates/section_07c/ tests/schemas/operator_verdict/test_section_07c_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-18b.ready-for-review.md`. Include: 8-file lockstep verification + parity_contract registration evidence (no alias_of OR alias_of=None + transport set CLI mandatory / HTTP+MCP-stdio optional) + HTML emitter determinism test PASS evidence + §02A non-regression + Wave-3 + next-batch + G2C-fanout non-regression + Wave-4 Marcus-writer non-regression + §08B non-regression (downstream consumer; confirms no contract break) + class-conformance delta + broad-regression delta with per-failure attribution + (if concurrent dispatch) C6 modules list integration coordination evidence with 7c.18a + T1-T9 decisions: emitter colocation choice + HTML rendering structure decisions vs §08B consumption.

T11: Claude lite tier (~10-15 min). Lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.18a review.

## Boundary

HALT on: 7c.17a + 7c.17b not done; ADR 0002 indicates §07C IS in family-aliases catalog (rare); class-conformance count != T1-baseline + 1; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; pyproject.toml C6 modules list integration conflict with concurrent 7c.18a (coordinate-or-sequence); parity_contract decorator rejects no-alias_of registration (rare); HTML emitter non-deterministic (test fails; root-cause); §08B downstream regression (signals contract break — escalate before continuing).

DO NOT touch: §02A canonical; Wave-3 + next-batch + G2C-fanout §section packages; harness; 7c.17a Marcus writer modules; §08B poll-surface; parity_contract decorator.

DO NOT introduce: new third-party deps (NO Jinja, NO MarkupSafe — Python stdlib `html.escape` + string-template only); defensive enum widening; non-deterministic test fixtures; integration logic between §07C output and §08B consumption (out of scope — emission shape only; §08B already consumes whatever shape it consumes per 7c.13 close).
```

---

## Operator dispatch checklist

1. ☐ 7c.17a + 7c.17b done (Wave 4 close-batch landed).
2. ☐ AMELIA-P2 freshness check (re-run validator post-Wave-4 close).
3. ☐ Sandbox-AC validator PASS.
4. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=1 pre-author commit).
5. ☐ pyproject.toml C6 modules list pre-staged for `app.gates.section_06b` + `app.gates.section_07c` (operator main-thread coordination).
6. ☐ If parallel-dispatching with 7c.18a: confirm Codex understands C6 modules list coordinate-or-sequence rule.
7. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.18a lands concurrently, spawn both in parallel + close-batch commit when both PASS.
