# Codex Handoff Prompt — Slab 3 Batch Development (3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6)

**For:** Codex dev agent
**Issued:** 2026-04-26
**Branch:** `dev/langchain-langgraph-foundation`
**Anchor commit:** `9d284cb` (Slab 3 batch authored ready-for-dev with party-mode amendments + 2c.x Codex handoff bundle)
**Predecessor:** Slab 2c CLOSED-WITH-CONDITIONAL-M2 at commit `e49297a` (your prior 4 commits 6ddf338+ecf2f47+21b5bf6+e49297a). M2 verdict: CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM (2c.2 AC-D-OP deferred per A-R6-2c.3 hard-gate path); resolves when operator runs the live Wondercraft API window.

---

## Mission

Develop all 6 Slab 3 stories in strict sequence (3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6). Slab 3 = **Marcus Orchestration**; M3 go/no-go gate "Marcus orchestrates end-to-end" closes at 3.6 with 5-agent party-mode acceptance verdict.

**Total scope:** 25pts across 6 stories. 4 dual-gate (3.1 + 3.2 + 3.3 + 3.6) + 2 single-gate (3.4 + 3.5).

---

## Hard sequencing (BINDING)

```
3.1 done ──► 3.2 open
             3.2 done ──► 3.3 open
                          3.3 done ──► 3.4 open
                                       3.4 done ──► 3.5 open
                                                    3.5 done ──► 3.6 open ──► Slab 3 CLOSED
```

**Do NOT open 3.N+1 until 3.N is BMAD-CLOSED.** 3.3 needs 3.2's DecisionCard; 3.4 needs 3.3's resume_api + bridge stubs; 3.5 needs 3.4's transports; 3.6 needs everything.

---

## Per-story BMAD cycle (apply uniformly; same as 2c.x cycle)

For each of 3.1, 3.2, 3.3, 3.4, 3.5, 3.6:

1. **Read the spec end-to-end** at `_bmad-output/implementation-artifacts/migration-3-{N}-*.md`. Specs already incorporate party-mode amendments (BLOCKERs RESOLVED + RIDERs integrated; see header of each spec).
2. **Run T1 Readiness Block** verifying every pre-flight item + artifact-existence sweep + epic-doc-vs-architecture cross-check. **Halt and surface to operator if any pre-flight fails.**
3. **Implement the AC sequence** in declared order. Adhere to all RESOLVED-BY-VERIFICATION pins.
4. **Run regression suite** at T8: `.venv/Scripts/python.exe -m pytest -q --tb=short`. Baseline target: post-Slab-2c-close pytest collection (T1 pin per Murat M-R8-3.1 — copy actual numbers from sprint-status post-2c.4 close; 2c.x dev added ~54 collected for the 2c-scoped subset).
5. **Run lint:** `.venv/Scripts/python.exe -m ruff check app/ tests/ skills/ scripts/ marcus/` (note: `marcus/` top-level shim from 3.1) AND `.venv/Scripts/python.exe -m lint_imports --config pyproject.toml`. Both must be clean (import-linter contracts EXPAND from 3/3 → 7/7 KEPT at 3.1; +2 ignore_imports at 3.3 + scheduler-forbidden contract; 3.4 raises N to 8 by adding facade-reachability rule).
6. **G6 single-gate self-conducted code review** per CLAUDE.md. For dual-gate stories (3.1/3.2/3.3/3.6) also run dual-gate gate-2 protocol per spec.
7. **Run `bmad-code-review`** on the diff in scope per CLAUDE.md §3.
8. **D12 close protocol** per spec AC. Sprint-status flip + closeout hygiene per CLAUDE.md.
9. **Commit per story.** Suggested message format:
   ```
   feat(3.N): <one-line summary>
   ```
10. **Run sandbox-AC validator** post-close on the next story before opening it: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-3-{N+1}-*.md`. Should still PASS.

---

## Pre-existing test collection errors (NOT 2c.x regressions; NOT your concern unless touched)

Verified at pre-Codex commit `8654086`: **13 collection errors** in `tests/contracts/test_33_2_*`, `tests/test_check_pipeline_manifest_lockstep.py`, `tests/test_run_wrangler_*`, etc. — all tied to a `PipelineManifest` Pydantic schema mismatch (`steps` field vs `lane/entrypoint/frozen_graph_version/nodes/edges`). This is unrelated tech debt PRE-DATING Slab 2c. **Do NOT attempt to fix as part of Slab 3 dev unless your story directly touches the affected paths.** If your story DOES touch those paths, surface to operator before changing the schema (it's likely a Slab-1/Slab-4 manifest concern that needs party-mode coordination).

---

## Story-specific landmines (READ BEFORE OPENING EACH)

### 3.1 — Marcus Intake + Orchestrator + Facade Split (5pt dual; OPENING STORY)

- **W-R1+W-R2 SUBSTRATE-VERIFIED RESOLVED:** Texas's `run_wrangler.py:58-63` literal import is `from marcus.dispatch.contract import (DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt,)` — **only 4 symbols** (DispatchEnvelope+DispatchReceipt are RETURNED by builders, NOT directly imported). `DispatchOutcome` is an **Enum** (`COMPLETE`/`PARTIAL`/`FAILED`) per `_to_dispatch_outcome` at lines 122-125, **NOT** BaseModel. Builder signatures verified at lines 1707-1709: `build_dispatch_envelope(*, dispatch_kind=DispatchKind.TEXAS_RETRIEVAL, ...)` (keyword `dispatch_kind`, NOT `kind`).
- **Top-level `marcus/` shim REQUIRED at repo root** per W-R2 (Texas's `_REPO_ROOT = _THIS_DIR.parents[2]` + `sys.path.insert(0, str(_REPO_ROOT))` at lines 49-56). Author `marcus/__init__.py` + `marcus/dispatch/__init__.py` + `marcus/dispatch/contract.py` re-exporting from `app.marcus.dispatch.contract`. Identity invariant test: `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind`.
- **W-R3 import-linter STAGED-DELIVERY per C3 precedent:** AC-B ships only 4 of 5 rules at 3.1; **DO NOT pre-seed `app.marcus.cli.*` or `app.http.*` ignore_imports** (would fail unused-ignore rejection per `pyproject.toml:88-95` C3 precedent). Rule 5 facade-reachability ships at 3.4 when transports materialize.
- **W-R4 DROP runtime stack-inspection** for single-writer enforcement; rely on import-linter only (async/await frame-walking unreliable; per-mutation overhead compounds in AC-F 100-iter loop).
- **W-R5 fingerprint = `(sha256_digest, session_id: uuid.UUID)`** — closes in-process session-bleed gap that pure content-fingerprinting leaves open.
- **W-R6 5th rule:** `app.specialists.** -> app.marcus.{intake,orchestrator,facade}` forbidden; `app.specialists.** -> app.marcus.dispatch.contract` permitted.
- **A-R5 `get_facade()` Option C:** pure re-read each call; NO singleton, NO `@lru_cache`, NO module-level state.
- **A-R4 sanctum digest allowlist-based** (NOT `rglob("*")`) — read file allowlist from `skills/bmad-agent-marcus/SKILL.md` activation-sequence.
- **M-R3 facade-identity loop parametrize over presets** (production + explore) × 50 iters = 100 total; AST-based string sweep (NOT regex) per M-R4+A-R1; debug-artifact emission on AC-F failure per M-R9.
- **A-R2 manifest substrate verification at T1** (UNVERIFIED at story-author): grep `state/config/run-manifest.yaml` for `dispatch_target` field shape; if absent, AC-I splits or scope inflates.
- **P-R3 D12 line-count vs 31-1 precedent** at T1 (5-line dual-gate proposal needs precedent confirmation).
- **P-R7 full D1-D13 drift sweep at T1** (architecture doc vs epic 3).

### 3.2 — DecisionCard Schema Family (4pt dual schema_shape)

- **A-R1 resolver substrate verification at T1:** grep for `app/manifest/refs.py::resolve_dotted_ref` (or equivalent); if aspirational, dev-agent T1 scaffolds.
- **A-R2 gate enum cross-check at T1** vs what 3.1 actually shipped.
- **A-R3 explicit pydantic-v2 checklist citation** in T1 readings (G6 MUST-FIX otherwise).
- **M-R1 negative tests per family:** ≥1 negative test per closed enum + ≥1 tz-naive datetime rejection per family. Don't ship 10 happy-path tests claiming K=10.
- **M-R2 schema-emission hashing** (sha256 over canonical JSON), NOT dict-deep-compare (flakes on key ordering across Pydantic patches).
- **Schema-story scaffold (BINDING per Lesson-Planner-MVP convention):** `docs/dev-guide/scaffolds/schema-story/` carries 4-file-lockstep recipe; pre-instantiate stubs for ALL 4 gates before dev opens.

### 3.3 — OperatorVerdict + ResumeApi + Tamper-Evidence (5pt dual invariant_preservation)

- **A-BLOCKER-3.3-A:** Verify `app/marcus/cli/` and `app/http/` parent dirs exist; if absent, T0 `mkdir + __init__.py` for both before any AC-D work.
- **W-R1-3.3-2 ANTI-REPLAY DIGEST BINDING (CRITICAL SECURITY BOUNDARY):** `decision_card_digest` MUST bind tuple `(card_content_canonical_json, trial_run_id, issuance_timestamp_iso, server_nonce)` — NOT just card_content. Server-issued nonce + replay-rejection. AC-B adds explicit `test_resume_from_verdict_rejects_replayed_verdict_from_prior_trial`.
- **W-R1-3.3-1 runtime sys.modules guard** in `app/gates/verdict.py` module init: assert scheduler modules not in `sys.modules` at import time (closes dynamic `importlib.import_module` evasion).
- **W-R1-3.3-3 transport=stub markers** on bridge stubs (X-Gate-Transport: stub HTTP header + [transport=stub] CLI log prefix); 3.4 transport bodies REMOVE these markers.
- **A-R1 quad-layer enumerated EXPLICITLY:** ruff + import-linter + AST test + pre-commit hook. NO under-implementation via "quad-layer" hand-wave.
- **A-R2 cross-module verdict↔card linkage:** OperatorVerdict adds `card_id: UUID4` field with FK-style validator.
- **M-R1 mutation tests for digest:** flip one byte → reject. Non-negotiable for invariant_preservation gate.
- **M-R2 asyncio test consistency** + **M-R3 don't mock digest function** (use real hashlib; mock storage layer only).
- **C3 import-linter extension:** add `app.http.gate_endpoint -> app.gates.resume_api` + `app.marcus.cli.gate_cli -> app.gates.resume_api` per pyproject.toml:88-95 staged-delivery comment (now in scope to add since bridge stubs materialize at AC-D).

### 3.4 — Three-Transport Verdict Parity (3pt single)

- **A-BLOCKER-3.4-A FastAPI dep:** Check `pyproject.toml`; if absent, split AC-B into AC-B-1 (dev-agent FastAPI route) + AC-B-2 (operator-gated `uv add fastapi httpx` evidence-paste).
- **A-R1 hard dep on 3.3 close** (NO parallel dev — bridge stubs MUST exist).
- **A-R2 single source-of-truth fixture** for parity: ONE verdict + 3 transport adapters + ONE parametrized test.
- **M-R1 in-process MCP harness** (NOT subprocess; #1 source of CI flake).
- **M-R2 structural-equivalence predicate explicit** (NOT string-equal; transports legitimately differ in framing).

### 3.5 — Runtime Model-Override + Cache Warning (3pt single)

- **A-BLOCKER-3.5-A RunState extension safety:** Verify current `app/state/run_state.py` shape; if `frozen=True` Pydantic, schema bump requires backward-compat for resumed runs serialized pre-3.5.
- **A-R1 rename `OverrideWarning` → `ModelOverrideWarning`** (avoid stdlib Warning collision).
- **A-R2 Phase-1 idempotency:** `submit_override` idempotent on operator re-submission (idempotency key = `(trial_id, node_id, new_model)` tuple OR explicit operator-supplied token).
- **M-R1 token-replay vs token-mismatch SEPARATE orthogonal tests** (NOT collapsed).
- **M-R2 caplog NOT stdout-sniff** for cache-warning emission.

### 3.6 — E2E Trial Run + M3 Acceptance (5pt dual operator_acceptance_gate; SLAB CLOSING)

- **A-BLOCKER-3.6-A pipeline-manifest step ID staleness:** Cross-check `state/config/pipeline-manifest.yaml` for actual step IDs; reference by NAME not ordinal at dev-time. **NOTE:** this manifest may be the source of the pre-existing 13 collection errors — investigate before §01-§15 enumeration if errors persist.
- **HARD INHERITANCE BLOCKING:** Texas AC-B-OP live reactivation per 2a.4 deferred-inventory entry `2a.4-followon-ac-b-op-live-retrieval` (Murat hard-caveat point c) — Slab-3 close MUST re-execute on live wire with full M1-M5 test discipline. Helper script + directive template pre-authored at 2a.4 SHIP UNINVOKABLE-ON-HYBRID-TODAY: `scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py` + `tests/fixtures/specialists/texas/ac_b_op_directive.yaml`.
- **HARD INHERITANCE per W-R7-3.1:** Capture post-3.6 Marcus envelope on first trial corpus run as frozen fixture at `tests/fixtures/marcus/baseline_envelope/2026-04-XX/` + `BASELINE_METADATA.md` companion (rebinds primary's amendment 12 Golden-Trace Baseline to migration substrate).
- **5-agent party-mode pinned (HARD):** Winston + Murat + Paige + Quinn-R + Amelia. Mirror 2c.3 5-agent + verbatim recording pattern at `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md`.
- **W-R1-3.6-1 provider-failure isolation policy** for Texas AC-B-OP (graceful-degrade per-provider PASS/FAIL/SKIP; one flaky provider does NOT fail entire AC-B-OP).
- **W-R1-3.6-3 capture-environment hash** in BASELINE_METADATA.md (Marcus persona-load SHA + sanctum-state SHA + reference-set SHA + capturing-agent + capture-command).
- **W-R1-3.6-4 CONDITIONAL-GREEN bounded triggers** at M3: ONLY evidence-completeness gaps; behavioral gaps route to YELLOW/RED.
- **M-R1 phase-vs-test K disambiguation:** E2E §01-§15 = K=1 (one logical scenario), NOT 15 K-floor units. Phases are assertions within one pytest function.
- **M-R3 golden-file content-hash NOT byte-equal** for baseline (forward-compat).
- **M-R4 5-agent party-mode is process-gate NOT test** (don't inflate K count).
- **AC-D-PARTIAL operator-window inheritance:** Slab 3 may close `CLOSED-WITH-CONDITIONAL-M3` if Texas live-wire deferred OR Marcus-envelope baseline metadata gap; mirror 2c.4 sprint-status enum convention (status=`done` + trailing comment).

---

## Governance non-negotiables (same as 2c.x; recap)

- **Sandbox-AC discipline (CLAUDE.md):** dev-agent ACs MUST verify via shipped Python deps + `pytest.skip(...)` on missing service. Run `validate_migration_story_sandbox_acs.py` before opening any story.
- **Gate-mode pinned at governance JSON** (`docs/dev-guide/migration-story-governance.json:57-62`). DO NOT relitigate.
- **Live API discipline:** Texas AC-B-OP at 3.6 is operator-gated — do NOT autonomously incur cost.
- **Hybrid working tree is sole input surface:** upstream/master severed at `3ed7c56` 2026-04-24.
- **Closeout hygiene:** every story close updates `sprint-status.yaml` first, then `next-session-start-here.md`.
- **Deferred inventory governance:** every new follow-on goes to `_bmad-output/planning-artifacts/deferred-inventory.md`; 3.6 retrospective enforces per-entry consultation verdicts.
- **No commits without per-story BMAD-CLOSE; no force-push, no `--no-verify`, no `--amend` published commits.**

---

## What "done" means for the batch

- All 6 stories show `done` in sprint-status.yaml.
- `migration-epic-3-slab-3-marcus-orchestration: done` (with trailing comment if M3 conditional).
- M3 milestone: `GREEN-LIGHT 2026-04-XX` OR `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` (recorded in `slab-3-m3-acceptance-verdict.md`).
- `slab-3-retrospective.md` exists with 4 canonical §-headers + per-entry deferred-inventory verdicts.
- `slab-3-marcus-invariant-stub.md` for Slab 5a absorption.
- Anti-patterns catalog: any 3.x harvest verdicts recorded; cycle-complete annotation per AC-H.
- Marcus-envelope baseline captured at `tests/fixtures/marcus/baseline_envelope/2026-04-XX/`.
- Texas AC-B-OP M1-M5 evidence pasted (or DEFERRED-PENDING-OPERATOR-WINDOW with reactivation gate).
- `2a.4-followon-ac-b-op-live-retrieval` deferred-inventory entry marked RESOLVED-AT-3.6 (or DEFERRED-CONTINUES if operator window pending).
- `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` deferred-inventory entry marked RESOLVED-AT-3.6.
- `next-session-start-here.md` reflects Slab 3 CLOSED + post-3.6 deferred-inventory counts.
- Regression suite: post-Slab-2c-close baseline preserved (T1-pinned per Murat M-R8-3.1).
- Import-linter contracts: EXPAND to 7/7 KEPT at 3.1, +1 to 8/8 at 3.4 (facade-reachability), + scheduler-forbidden contract at 3.3.
- One commit per story-close (6 commits total).

---

## Escalation triggers (HALT and surface to operator)

- T1 pre-flight fails on any story (predecessor not `done`, anchor file missing, etc.).
- Sandbox-AC validator FAILS (substrate state has drifted since authoring).
- 3.1 W-R2 top-level `marcus/` shim creates double-import bug (identity invariant test fails).
- 3.3 W-R1-3.3-2 anti-replay digest binding has unresolvable substrate gap.
- 3.6 M3 party-mode returns YELLOW or RED verdict (cannot close Slab 3 cleanly).
- 3.6 Texas AC-B-OP M1-M5 evidence cannot be gathered (live providers unavailable + helper script broken).
- Pre-existing 13 collection errors expand OR a new test starts failing that wasn't broken pre-3.x.
- Live API call exceeds cost ceiling (Texas reactivation has no explicit ceiling; flag operator before incurring >$5).

---

## Reference anchors

- Spec files: `_bmad-output/implementation-artifacts/migration-3-{1,2,3,4,5,6}-*.md` (commit `9d284cb`)
- Sprint status: `_bmad-output/implementation-artifacts/sprint-status.yaml` (Slab 3 block at line 800+)
- Governance JSON: `docs/dev-guide/migration-story-governance.json:57-62`
- Architecture doc: `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` §"app/marcus/" lines 928-940 + §FR26-FR30 line 850
- Epic 3: `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3 lines 892-1066
- Anti-patterns: `docs/dev-guide/specialist-anti-patterns.md` (A1-A14 post-2c.4)
- Pydantic v2 checklist: `docs/dev-guide/pydantic-v2-schema-checklist.md`
- Schema-story scaffold: `docs/dev-guide/scaffolds/schema-story/`
- 2a.4 deferred-inventory binding: `_bmad-output/planning-artifacts/deferred-inventory.md` §`2a.4-followon-ac-b-op-live-retrieval`
- Texas substrate: `skills/bmad-agent-texas/scripts/run_wrangler.py:58-63` (4-symbol import) + `:120-125` (DispatchOutcome Enum) + `:1707-1709` (builder keyword args)
- C3 import-linter precedent: `pyproject.toml:88-95`
- 2c.x Codex prior-batch precedent: `_bmad-output/implementation-artifacts/codex-handoff-2c-batch-dev.md` (your prior prompt; mirror format/cadence)

Proceed.
