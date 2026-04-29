# Migration Story 7a.4: Per-Slide Subgraph + HTML Review-Pack Skeleton

**Status:** done
**Sprint key:** `migration-7a-4-per-slide-subgraph-html-review-pack-skeleton`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 5
**Gate:** **single-gate-with-k-contract** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-4; rationale: null with K-contract)
**K-target:** ~1.4× (gate-shape band 2.4-2.8K; ~3.5K target)
**K-contract:** HTML review-pack BOUNDED to skeleton-only (semantic structure + checkbox + delta-field; no full styling). **Tripwire at K-actual >4.08K (1.7× band-floor) → escalate to dual-gate via party-mode triage; close dev round.**
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 4 — slot 1 (needs 7a.3 + 7a.6 [both Wave 3]; parallel with 7a.5 [Wave 4 slot 2]).
**FR coverage:** 15 — FR11, FR12, FR13, FR14, FR15; FR-A15, FR-A16, FR-A18; FR-O5, FR-O6, FR-O7, FR-O8, FR-O10, FR-O11, FR-O12
**Standing-guardrail enforcement:**
- SG-1 unchanged.
- SG-2 G2B / G2F-merged / G3B per-slide rows preserved with subgraph-mechanism citation.
- SG-3 Composition Spec §3.5 (per-specialist non-blocking) honored — each per-slide subgraph has isolated checkpoint boundary.

**Implementation cycle (NEW per operator instruction 2026-04-28):**
- **Claude:** authored this spec. Gate-1 party-mode NOT called (single-gate; substrate is LangGraph subgraph-with-`interrupt()` which is well-established LangGraph pattern).
- **Codex:** develops source + tests; reaches `review`; produces G6 self-review.
- **Claude:** does final `bmad-code-review`; remediates; commits; flips done.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- Stories 7a.1 + 7a.2 CLOSED done. 7a.3 + 7a.6 ready-for-dev (Wave 3); 7a.4 dev opens after BOTH 7a.3 + 7a.6 close.
- 7a.6 (vocabulary registry) provides `EscapeCardOption` enum (`accept-as-is, reject-and-skip-slide, abort-run`) — used by AC-7.4-E max-3-oscillation-guard escape card.
- 7a.3 (pre-gate-marcus) provides `pre_gate_marcus.invoke_pre_gate_marcus(gate_id, slot_values)` for per-slide pre-fill (each per-slide subgraph instance invokes pre-gate-marcus once per slide).
- 7a.2 (manifest fold-flags) provides orchestration-only-node lockstep tolerance — the new `per-slide-subgraph` orchestration node + HTML-review-pack-emitter node land as orchestration-only nodes per the same pattern as 7a.1's `directive-composer` and 7a.3's `pre-gate-marcus`.

**Live substrate (verified at authoring; do NOT regress):**
- `app/marcus/orchestrator/` houses orchestration modules (siblings: directive_composer, dispatch_adapter, production_runner, pre_gate_marcus). New modules: `per_slide_subgraph.py` + `html_review_pack.py`.
- `app/models/state/operator_verdict.py` is the existing OperatorVerdict Pydantic model. AC-7.4-E extends it with a `revise_count` field (additive Pydantic v2; four-file-lockstep per NFR-CG4).
- `state/config/pipeline-manifest.yaml` has nodes for G2B (variant selection by Gary, currently folded with G2C per 7a.2 fold annotations), G2F-merged (motion designation+approval by Kira), G3B (Storyboard B HIL review by Quinn-R). 7a.4 doesn't change fold-flag annotations; it adds a new orchestration node that runs BEFORE each per-slide-array gate and emits the HTML pack.
- Existing `app/specialists/{gary,kira,quinn_r}/` directories carry the per-specialist scaffolds; 7a.4 does NOT modify any specialist body (substrate-isolation invariant N4).
- `state/runs/<trial_id>/` is the canonical per-trial output directory (used by 7a.1 for `directive.yaml` + `bundle/`). 7a.4 emits per-gate HTML packs at `runs/<trial_id>/gates/<gate>-review-pack.html` + `runs/<trial_id>/gates/<gate>-pack-open.log` + `runs/<trial_id>/gates/_history/<gate>-v{N}.html` for revisions.

**Block-mode trigger paths touched by this story:** `state/config/pipeline-manifest.yaml` (Tier-1 patch — additive orchestration nodes); lockstep PASS via 7a.2 tolerance.

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-4: per-slide subgraph + HTML review-pack skeleton. Subgraph-with-`interrupt()` fan-out for G2B/G2F-merged/G3B per-slide arrays. FM-3 AST scan critical (subgraph-degenerating-to-parent-graph-loop check). Single-gate WITH k_contract tripwire per Step 1 batch-approved adjustment.

**T1 conclusion:** Implementation proceeds. Hard checkpoints at T1: confirm 7a.3 + 7a.6 done; confirm `EscapeCardOption` enum is loadable; verify K-actual stays ≤4.08K via per-task K-tracking.

---

## Story

As the operator,
I want per-slide arrays at G2B (variant selection by Gary), G2F-merged (motion designation+approval by Kira), and G3B (Storyboard B HIL review by Quinn-R) to surface as a generated HTML review-pack at `runs/<trial_id>/gates/<gate>-review-pack.html` opened in my browser at gate entry, with each slide carrying a checkbox + free-text delta-directive field, backed structurally by a LangGraph subgraph-with-`interrupt()` fan-out pattern,
so that I can review and decide on 30 slides without the per-slide CLI-loop collapse failure mode, and substrate (not policy) prevents rubber-stamping by structurally fanning out per-slide decision boundaries.

---

## Acceptance Criteria

### AC-7.4-A — Per-slide subgraph fan-out (FR-A15, FR-A16, FR-A18)

**Given** the per-slide subgraph at `app/marcus/orchestrator/per_slide_subgraph.py`
**When** Gary/Kira/Quinn-R produce per-slide outputs
**Then** the parent graph fans out one subgraph instance per slide, each with isolated checkpoint boundary (LangGraph `Send` API or equivalent fan-out primitive).
**And** each subgraph instance emits a separate `interrupt()` per slide.
**And** the parent graph joins on completion of all per-slide subgraph instances before advancing to the next pipeline step.

**Test pin:** `tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py` — 4 cases: (a) 1 slide → 1 subgraph instance, (b) N slides → N subgraph instances, (c) per-slide isolated checkpoint boundary verified, (d) parent join correctness when slides complete out-of-order.

### AC-7.4-B — FM-3 AST scan: subgraph-not-degenerating-to-parent-graph-loop (FR-A18 structural enforcement)

**Given** the FM-3 anti-pattern (subgraph degenerating into a per-slide `for` loop in the parent graph defeats the fan-out purpose)
**When** the dev agent authors `tests/structural/test_per_slide_subgraph_pattern.py`
**Then** the test AST-scans `app/marcus/orchestrator/per_slide_subgraph.py` AND any module that imports it, asserting NO parent graph contains repeated `interrupt()` inside a per-slide `for` loop.
**And** the test fails on the canonical FM-3 anti-pattern (verified by injecting a fake `for slide in slides: state = invoke_subgraph(slide); interrupt(...)` loop into a tmp file).

**Test pin:** `tests/structural/test_per_slide_subgraph_pattern.py` (per AC-B test pin).

### AC-7.4-C — HTML review-pack generator (FR-O5, FR-O7)

**Given** the HTML review-pack generator at `app/marcus/orchestrator/html_review_pack.py`
**When** a per-slide-array gate fires
**Then** the generator writes `runs/<trial_id>/gates/<gate>-review-pack.html` with one row per slide; each row carries:
- Slide identifier (label + index).
- Specialist-output preview (e.g. Gary's selected variant; Kira's motion designation; Quinn-R's storyboard-B summary).
- Checkbox: approve / revise / skip.
- Free-text delta-directive field (textarea).
- Hidden form fields for trial_id, gate_id, slide_index, output_digest.

**And** the HTML serialization schema is fixed (semantic HTML structure; deterministic field IDs; `data-` attributes for slide_index + gate_id).
**And** the HTML is SKELETON-ONLY per the K-contract — no full CSS styling beyond minimal inline style for legibility (e.g. `<style>td { padding: 4px; } .blocker { color: red; }</style>`).

**Test pin:** `tests/unit/marcus/orchestrator/test_html_review_pack.py` — 5 cases: (a) generator produces valid HTML for N slides, (b) form fields are deterministic, (c) data-* attributes present, (d) output_digest field is non-empty, (e) skeleton-only style (no external CSS, no JavaScript framework imports — just minimal `<style>` block + form-submit JS for sessionStorage persistence).

### AC-7.4-D — Browser-open hook + open-event log (FR-O6, FM-7 verification)

**Given** a browser-open event hook
**When** the review-pack file is generated
**Then** the operator's default browser is invoked via `webbrowser.open(file_url)` AND a browser-open event is logged at `runs/<trial_id>/gates/<gate>-pack-open.log` (one line per open: ISO timestamp + trial_id + gate_id + pack_path).
**And** the gate cannot advance without an open-event timestamp present in the log.

**Test pin:** `tests/integration/marcus/test_html_review_pack_browser_open.py` — 3 cases: (a) browser open invoked + log entry written, (b) gate-advance refuses without log entry, (c) `webbrowser.open` failure (e.g. no display) raises `BrowserOpenError(RuntimeError)` instead of silently advancing.

### AC-7.4-E — Max-3 oscillation guard + escape card (FR-A21, FR-O11, NFR-OC4, NFR-OR1)

**Given** the operator submits a delta-directive for slide N as `revise`
**When** the substrate routes the delta back to the producing specialist subgraph
**Then** the specialist regenerates slide N as v2; the HTML review-pack regenerates with v2 highlighted; prior pack retained at `runs/<trial_id>/gates/_history/<gate>-v1.html` for audit (FR-O8).

**Given** the operator clicks `revise` a 4th time on the same slide
**When** the substrate evaluates the revise count
**Then** the substrate refuses (state-machine invariant `revise_count <= 3` per `app/models/state/operator_verdict.py` extension; FR-A21 enforces).
**And** an `oscillation_escape_required` decision-card surfaces with three options (`accept-as-is`, `reject-and-skip-slide`, `abort-run`) — tokens drawn from `EscapeCardOption` enum in 7a.6's vocabulary registry.
**And** `accept-as-is` requires non-empty rationale string >20 chars (FR-O11; substrate rejects shorter input at the writer; NFR-OX3 floor).
**And** the escape card surfaces in <500ms (NFR-OR1 SLA pin).

**Test pin:** `tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py` — 6 cases: (a) revise count 1→2→3 succeeds, (b) revise count 4 raises with escape card, (c) `accept-as-is` with rationale ≥20 chars succeeds, (d) `accept-as-is` with rationale <20 chars rejected at writer, (e) `reject-and-skip-slide` succeeds and marks slide as skipped, (f) `abort-run` succeeds and halts trial.

### AC-7.4-F — OperatorVerdict.revise_count four-file-lockstep (NFR-CG4)

**Given** the four-file-lockstep on `app/models/state/operator_verdict.py` extension
**When** the dev-agent commits the model change
**Then** the same PR includes:
1. **Model:** `app/models/state/operator_verdict.py` — additive `revise_count: int = Field(default=0, ge=0, le=3)` field.
2. **Emitted JSON Schema:** `app/models/schemas/operator_verdict.schema.json` — re-emitted via `python -m app.models.operator_verdict --emit-schema` flag (or CI sync-check that re-emits + asserts byte-equality).
3. **Golden fixture:** `tests/fixtures/operator_verdict/operator_verdict_with_revise_count_golden.json` — pinned valid verdict with `revise_count: 2`.
4. **Shape-pin tests:** `tests/unit/models/test_operator_verdict_revise_count.py` — 4 cases: default value 0, valid range 0-3, value 4 raises ValidationError, JSON Schema byte-equality.

**Test pin:** see (4) above.

### AC-7.4-G — K-contract enforcement (single-gate-with-k-contract; tripwire)

**Given** the K-contract: HTML review-pack BOUNDED to skeleton-only
**When** the dev agent opens 7a.4
**Then** the AC explicitly bounds HTML review-pack to skeleton-only:
- Semantic HTML structure (tables, forms, labels).
- Checkbox + delta-field per row.
- Minimal inline `<style>` block ≤30 lines.
- NO external CSS file imports.
- NO JavaScript framework (React, Vue, etc.) imports.
- Minimal vanilla JS for sessionStorage persistence (≤50 lines).
**And** if scope grows beyond skeleton at any T-task, the K-tripwire (>1.7× band-floor = >4.08K LOC) fires; the dev round closes; 7a.4 escalates to dual-gate via party-mode triage (per `migration-story-governance.json::stories.7a-4.k_contract.tripwire_action`).
**And** Codex MUST report K-actual at T9 + T10 self-review.

### AC-7.4-H — Manifest registration of per-slide subgraph + HTML pack emitter (FR-A15)

**Given** the new orchestration nodes
**When** the dev agent edits `state/config/pipeline-manifest.yaml`
**Then** TWO new orchestration-only nodes land (per the 7a.1/7a.3 pattern; orchestration-only-node lockstep tolerance from 7a.2 is the prereq):

```yaml
  - id: "per-slide-subgraph"
    label: "Per-Slide Subgraph Fan-Out (Slab 7a / Story 7a.4)"
    specialist_id: null
    gate: false
    hud_tracked: false
    dependencies: {}
    fold_with: null
    fold_target: null
    rationale: "Fan-out subgraph for G2B/G2F-merged/G3B per-slide arrays; isolated checkpoint per slide."

  - id: "html-review-pack-emitter"
    label: "HTML Review-Pack Emitter (Slab 7a / Story 7a.4)"
    specialist_id: null
    gate: false
    hud_tracked: false
    dependencies: {}
    fold_with: null
    fold_target: null
    rationale: "Emits runs/<trial_id>/gates/<gate>-review-pack.html before per-slide-array gates."
```

**And** lockstep PASSES (orchestration-only tolerance carries through).

**Test pin:** `tests/structural/test_per_slide_subgraph_node_registered.py` — asserts both nodes exist with canonical orchestration-only fields.

### AC-7.4-I — N-item + anti-pattern + Composition Spec trace

The implementation must record:
- **N1 PASS:** new modules follow substrate-inventory checklist.
- **N2 PASS:** Composition Spec §3.5 (per-specialist non-blocking) honored — each per-slide subgraph has isolated checkpoint boundary.
- **N4 PASS:** specialist isolation preserved — Gary/Kira/Quinn-R bodies untouched.
- **N9 PASS-PENDING-OPERATOR:** operator validates HTML pack UX at story close.
- **N10 PASS:** A12 procedural-coupling re-read; subgraph + HTML pack are wired (no manual operator step).
- **A11 honored:** HTML emission uses `\n` line endings; file paths via `Path.as_posix()`.

### AC-7.4-J — D12 close protocol

At close: sprint-status flip; cite sandbox-AC + lockstep + ruff + lint-imports + K-actual; confirm Composition Spec §11 trigger did not fire.

---

## Tasks / Subtasks

- [x] **T1: Readiness review (Codex)** — confirm 7a.3 + 7a.6 done; verify `EscapeCardOption` enum loadable from 7a.6; confirm `app/models/state/operator_verdict.py` exists (current shape).
- [x] **T2: Author `per_slide_subgraph.py`** (AC-A) — fan-out via LangGraph `Send` API or equivalent; isolated checkpoint per slide. Author 4-case unit test.
- [x] **T3: FM-3 AST scan structural test** (AC-B) — per AC-B test pin.
- [x] **T4: Author `html_review_pack.py`** (AC-C) — generator + skeleton-only HTML emit. Author 5-case unit test.
- [x] **T5: Browser-open hook + log** (AC-D) — `webbrowser.open` + log file + gate-advance refusal. Author 3-case integration test.
- [x] **T6: Max-3 oscillation guard** (AC-E) — state-machine invariant + escape card. Author 6-case unit test.
- [x] **T7: OperatorVerdict.revise_count four-file-lockstep** (AC-F) — model + emitted JSON Schema + golden + shape-pin tests.
- [x] **T8: Manifest registration** (AC-H) — add 2 orchestration-only nodes; lockstep PASS; structural test.
- [x] **T9: Verification battery** — full focused + wider regression slice; K-actual reported.
- [x] **T10: Codex G6 self-review** — Blind / Edge / Auditor.
- [ ] **T11: Claude bmad-code-review + remediation + commit + close.**

---

## File Structure Requirements

**New:** `app/marcus/orchestrator/per_slide_subgraph.py`, `app/marcus/orchestrator/html_review_pack.py`, `app/models/schemas/operator_verdict.schema.json`, `tests/fixtures/operator_verdict/operator_verdict_with_revise_count_golden.json`, `tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py`, `tests/unit/marcus/orchestrator/test_html_review_pack.py`, `tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py`, `tests/unit/models/test_operator_verdict_revise_count.py`, `tests/integration/marcus/test_html_review_pack_browser_open.py`, `tests/structural/test_per_slide_subgraph_pattern.py`, `tests/structural/test_per_slide_subgraph_node_registered.py`, `_bmad-output/implementation-artifacts/7a-4-codex-self-review-2026-04-XX.md`.

**Modified:** `app/models/state/operator_verdict.py` (additive `revise_count` field), `state/config/pipeline-manifest.yaml` (additive 2 orchestration-only nodes), `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** any specialist body (Gary/Kira/Quinn-R untouched per N4); 7a.1/7a.2/7a.3/7a.6 surfaces; v4.2 prompt pack.

---

## Testing Requirements

**K-floor 14 + K-target ~28 (per gate-shape band 2.4-2.8K + ~3.5K target):**
- 4 per-slide-subgraph cases (AC-A)
- 1 FM-3 AST scan (AC-B; 1 active + 1 fake-injection negative case = 2 total)
- 5 HTML pack cases (AC-C)
- 3 browser-open + log cases (AC-D)
- 6 max-3 oscillation cases (AC-E)
- 4 OperatorVerdict.revise_count shape-pin cases (AC-F)
- 1 manifest-node registered (AC-H)

**K-tripwire (BINDING per K-contract):** if K-actual exceeds 1.7× band-floor (~4.08K LOC OR ~28 active tests excluding skipped placeholders), close the dev round + escalate to dual-gate via party-mode triage. Codex MUST report K-actual breakdown at T9 + T10.

---

## Dev Notes

**Architecture compliance:** Composition Spec §3.5 honored (per-specialist gates non-blocking; per-slide subgraph has isolated checkpoint); Composition Spec §11 trigger check NEGATIVE (additive orchestration nodes; no fan-out at the SPECIALIST level — fan-out is at the SLIDE level within an existing specialist's output).

**Library/framework:** LangGraph `Send` API (already used by Slab 6 substrate); Python `webbrowser` stdlib; PyYAML for any YAML emit; vanilla HTML/CSS/JS for review pack. NO new third-party deps.

**Anti-patterns to avoid:** FM-3 (subgraph degenerating to parent-graph loop) — AC-B AST scan; A12 procedural-coupling — gate-advance refusal is structural; A11 Windows-portability — POSIX paths in HTML attributes.

**Previous story intelligence:**
- 7a.1: orchestration-only node pattern + sandbox-AC discipline.
- 7a.2: lockstep orchestration-only tolerance + manifest pattern.
- 7a.3: Jinja2 templates for pre-fill (the per-slide HTML pack uses simpler string formatting; not Jinja2 since it's emitting HTML to disk for browser consumption rather than feeding LLM prompts).
- 7a.6: `EscapeCardOption` enum + vocabulary registry for closed-set decision tokens.

**References:** Epic Story 1.5; PRD §FR11-FR15 + §FR-A15-A18 + §FR-O5-O12; governance JSON `7a-4`; Composition Spec §3.5/§11; CLAUDE.md governance.

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5), 2026-04-29 dev-story execution. Claude authored the spec; Codex owns T1-T10 and leaves T11 final review/commit/close to Claude per story boundary.

### Debug Log References

- T1 readiness opened with 7a.3 still showing `review` in the 7a.3 story file and sprint-status, but the operator explicitly instructed "Consider 7a.3 closed." Codex treated that as the closure override and did not edit 7a.3 surfaces.
- T1 verified 7a.6 `done` in both story and sprint-status.
- T1 verified `EscapeCardOption` imports from `app.models.decision_cards`, `OperatorVerdict` imports from `app.models.state.operator_verdict`, and LangGraph `Send` is available from `langgraph.types`.

### Completion Notes List

- Added `app/marcus/orchestrator/per_slide_subgraph.py` with LangGraph `Send` fan-out, isolated per-slide checkpoint namespaces, one interrupt boundary inside the per-slide subgraph node, parent join ordering, and max-3 revise escape-card guard.
- Added `app/marcus/orchestrator/html_review_pack.py` with deterministic skeleton-only HTML output, hidden fields, output digests, sessionStorage persistence, revision history archiving, browser-open logging, and fail-closed gate advance checks.
- Extended `OperatorVerdict` with additive `revise_count: int = Field(default=0, ge=0, le=3)` plus emitted schema, golden fixture, shape-pin tests, and refreshed existing state schema pin.
- Registered `per-slide-subgraph` and `html-review-pack-emitter` as orchestration-only manifest nodes; lockstep PASS records the two new nodes alongside existing orchestration-only nodes.
- K-actual at T9/T10: 853 source/test/support LOC across the 7a.4 files counted; 27 active focused tests; below 4.08K LOC and active-test tripwire.
- N1 PASS: new modules follow substrate-inventory discipline and have focused tests.
- N2 PASS: Composition Spec Section 3.5 honored; fan-out is slide-level, not specialist-level.
- N4 PASS: Gary/Kira/Quinn-R specialist bodies untouched.
- N9 PASS-PENDING-OPERATOR: operator HTML-pack UX validation remains a closeout/operator check.
- N10 PASS: A12 procedural-coupling re-read; pack open and gate-advance refusal are wired functions, not manual-only instructions.
- A11 honored: generated HTML uses LF writes and POSIX path serialization via `Path.as_posix()`.
- Composition Spec Section 11 trigger did not fire; manifest changes are additive orchestration-only nodes.

### File List

- `_bmad-output/implementation-artifacts/7a-4-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md`
- `app/marcus/orchestrator/per_slide_subgraph.py`
- `app/marcus/orchestrator/html_review_pack.py`
- `app/models/state/operator_verdict.py`
- `app/models/schemas/operator_verdict.schema.json`
- `state/config/pipeline-manifest.yaml`
- `tests/fixtures/models/state/schema_pin_operator_verdict.json`
- `tests/fixtures/operator_verdict/operator_verdict_with_revise_count_golden.json`
- `tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py`
- `tests/unit/marcus/orchestrator/test_html_review_pack.py`
- `tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py`
- `tests/unit/models/test_operator_verdict_revise_count.py`
- `tests/integration/marcus/test_html_review_pack_browser_open.py`
- `tests/structural/test_per_slide_subgraph_pattern.py`
- `tests/structural/test_per_slide_subgraph_node_registered.py`
- `tests/structural/test_lockstep_orchestration_only_tolerance.py`
- `tests/unit/manifest/test_compiler.py`

### Verification

```
.venv\Scripts\python.exe -m pytest tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py tests/unit/marcus/orchestrator/test_html_review_pack.py tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py tests/unit/models/test_operator_verdict_revise_count.py tests/integration/marcus/test_html_review_pack_browser_open.py tests/structural/test_per_slide_subgraph_pattern.py tests/structural/test_per_slide_subgraph_node_registered.py -q --tb=short
-> 27 passed

.venv\Scripts\python.exe -m pytest tests/unit/models/test_operator_verdict_revise_count.py tests/unit/models/state/test_schema_pin.py -q --tb=short
-> 14 passed

.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
-> 287 passed, 20 skipped with temporary POSIX vi shim

.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py
-> PASS

.venv\Scripts\python.exe scripts\utilities\validate_migration_story_sandbox_acs.py _bmad-output\implementation-artifacts\migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md
-> PASS

.venv\Scripts\python.exe -m ruff check app\marcus\orchestrator\per_slide_subgraph.py app\marcus\orchestrator\html_review_pack.py app\models\state\operator_verdict.py tests\unit\marcus\orchestrator tests\unit\models\test_operator_verdict_revise_count.py tests\integration\marcus\test_html_review_pack_browser_open.py tests\structural
-> All checks passed

.venv\Scripts\lint-imports.exe
-> Contracts: 9 kept, 0 broken
```

### Change Log

- 2026-04-29: Codex opened Story 7a.4 for implementation; status `ready-for-dev` -> `in-progress`.
- 2026-04-29: Codex completed T1-T10, authored self-review, and moved story status `in-progress` -> `review`.
