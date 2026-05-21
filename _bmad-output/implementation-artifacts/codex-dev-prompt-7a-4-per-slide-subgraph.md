# Codex dev-story prompt — Story 7a.4 (per-slide subgraph + HTML review-pack skeleton)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 4 slot 1 (needs 7a.3 + 7a.6 [both Wave 3]; parallel with 7a.5 [Wave 4 slot 2]).
**Gate:** **single-gate-with-K-contract** — HTML BOUNDED to skeleton-only; tripwire 4.08 KLOC → escalate to dual-gate via party-mode.

---

```
Run bmad-dev-story on Story 7a.4 (Slab 7a Wave 4 slot 1; single-gate-with-K-contract; per-slide subgraph fan-out + HTML review-pack skeleton + max-3 oscillation guard).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md` (status: ready-for-dev; 10 ACs A-J; 11 tasks T1-T11; you own T1-T10)
2. Predecessor 7a.3 (vocabulary may not yet be active): `_bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md` — must be `done` before 7a.4 dev opens
3. Predecessor 7a.6 (registry): `_bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md` — must be `done` before 7a.4 dev opens (provides `EscapeCardOption` enum used by AC-7.4-E escape card)
4. 7a.1/7a.2 substrate: orchestration-only-node lockstep tolerance + manifest fold-flag pattern
5. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-4` (single-gate-with-k_contract; expected_pts=5; expected_k_target=1.4; k_contract.tripwire_threshold_kloc=4.08; k_contract.tripwire_action="escalate_to_dual_gate_via_party_mode")
6. Pydantic v2 checklist: `docs/dev-guide/pydantic-v2-schema-checklist.md` (four-file-lockstep on OperatorVerdict.revise_count extension)
7. `app/models/state/operator_verdict.py` — current shape; 7a.4 adds additive `revise_count: int = Field(default=0, ge=0, le=3)`
8. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7a.3 + 7a.6 BOTH `done` in spec status + sprint-status.yaml.
- `EscapeCardOption` enum loadable from `app/models/decision_cards.py` (lands when 7a.6 closes).
- `app/models/state/operator_verdict.py::OperatorVerdict` is the current Pydantic model.
- LangGraph `Send` API (or equivalent fan-out primitive) is available (already used by Slab 6 substrate).

## Files in scope

**New:** `app/marcus/orchestrator/per_slide_subgraph.py`, `app/marcus/orchestrator/html_review_pack.py`, `app/models/schemas/operator_verdict.schema.json`, `tests/fixtures/operator_verdict/operator_verdict_with_revise_count_golden.json`, `tests/unit/marcus/orchestrator/test_{per_slide_subgraph_fanout,html_review_pack,max_3_oscillation_guard}.py`, `tests/unit/models/test_operator_verdict_revise_count.py`, `tests/integration/marcus/test_html_review_pack_browser_open.py`, `tests/structural/test_{per_slide_subgraph_pattern,per_slide_subgraph_node_registered}.py`, `_bmad-output/implementation-artifacts/7a-4-codex-self-review-2026-04-XX.md`.

**Modified:** `app/models/state/operator_verdict.py` (additive `revise_count` field per AC-7.4-F four-file-lockstep); `state/config/pipeline-manifest.yaml` (additive 2 orchestration-only nodes per AC-7.4-H); `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** Gary/Kira/Quinn-R bodies (substrate-isolation invariant N4); 7a.1/7a.2/7a.3/7a.6 surfaces; v4.2 prompt pack.

## Critical implementation notes

- **K-contract BINDING:** HTML review-pack BOUNDED to skeleton-only. NO external CSS, NO JS framework imports, minimal inline `<style>` ≤30 lines, minimal vanilla JS ≤50 lines for sessionStorage. If scope grows beyond skeleton at any T-task, K-tripwire (>4.08K LOC) fires; close dev round; escalate to dual-gate via party-mode (per `migration-story-governance.json::stories.7a-4.k_contract.tripwire_action`). **Report K-actual at T9 + T10.**
- **FM-3 AST scan (AC-7.4-B BINDING):** `tests/structural/test_per_slide_subgraph_pattern.py` AST-scans `app/marcus/orchestrator/per_slide_subgraph.py` and any importer; FAILS if any parent graph contains repeated `interrupt()` inside a per-slide `for` loop. Verify with both clean baseline + injected fake FM-3 anti-pattern.
- **Browser-open hook (AC-7.4-D):** use `webbrowser.open(file_url)`; log to `runs/<trial_id>/gates/<gate>-pack-open.log`; gate-advance refuses without log entry; `webbrowser.open` failure raises `BrowserOpenError(RuntimeError)` (NOT silent advance).
- **Max-3 oscillation guard (AC-7.4-E):** state-machine invariant via `OperatorVerdict.revise_count <= 3`; 4th revise raises with escape card surfaced in <500ms (NFR-OR1); `EscapeCardOption` from 7a.6's vocabulary registry; `accept-as-is` requires non-empty rationale ≥20 chars (NFR-OX3 floor).
- **OperatorVerdict.revise_count four-file-lockstep (AC-7.4-F):** model + emitted JSON Schema + golden fixture + shape-pin tests (NFR-CG4); follow Pydantic v2 checklist exactly.
- **Per-slide subgraph (AC-7.4-A):** LangGraph `Send` API for fan-out; isolated checkpoint per slide; parent join on completion.
- **Manifest registration (AC-7.4-H):** 2 NEW orchestration-only nodes (`per-slide-subgraph` + `html-review-pack-emitter`); orchestration-only-node lockstep tolerance from 7a.2 carries through.
- **No new third-party deps.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator/test_{per_slide_subgraph_fanout,html_review_pack,max_3_oscillation_guard}.py tests/unit/models/test_operator_verdict_revise_count.py tests/integration/marcus/test_html_review_pack_browser_open.py tests/structural/test_{per_slide_subgraph_pattern,per_slide_subgraph_node_registered}.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/per_slide_subgraph.py app/marcus/orchestrator/html_review_pack.py app/models/state/operator_verdict.py tests/unit/marcus/orchestrator tests/unit/models/test_operator_verdict_revise_count.py tests/integration/marcus/test_html_review_pack_browser_open.py tests/structural
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7a.3 + post-7a.6 baseline.

## T10 + T11

T10: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-4-codex-self-review-2026-04-XX.md`. **MUST report K-actual breakdown** (LOC + active-test-count vs K-target 3.5K + ~28 active tests, vs tripwire 4.08K + 35-40 tripwire tests). Flip story status to `review`. Hand to Claude.

T11: Claude does FINAL bmad-code-review + remediation + commit + flips `migration-7a-4-per-slide-subgraph-html-review-pack-skeleton` review → done.

## Boundary

- HALT and surface on: (a) 7a.3 OR 7a.6 status mismatch, (b) K-actual exceeds 1.7× band-floor (~4.08K LOC OR ~28 active tests excluding skipped placeholders) — close round + escalate to dual-gate, (c) FM-3 anti-pattern detected in your own implementation, (d) Composition Spec §11 trigger fires (additive orchestration nodes; should not), (e) any sandbox-AC violation, (f) browser-open hook can't be tested (e.g. CI environment lacks display) — use mock + assert call args.
- Do NOT touch Gary/Kira/Quinn-R bodies.
- Do NOT introduce ruamel.yaml or new third-party deps.
```
