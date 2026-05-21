# Codex Handoff Prompt — Slab 4 Batch Development (4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6 → 4.7)

**For:** Codex dev agent
**Issued:** 2026-04-26
**Branch:** `dev/langchain-langgraph-foundation`
**Anchor commit:** `9a4d8b3` (Slab 3 close — your prior Slab-3 sequence: 7d9a9bf+dcb4149+9e441f7+d8f4c05+6ecfed3+9a4d8b3)
**Predecessor close-state:** Slab 3 CLOSED-WITH-CONDITIONAL-M3 — M3 verdict CONDITIONAL-GREEN per W-R1-3.6-4 bounded-trigger rule (evidence-completeness gap only — Texas AC-B-OP M1-M5 DEFERRED-PENDING-OPERATOR-WINDOW; behavioral pass clean; Marcus-envelope baseline captured at `tests/fixtures/marcus/baseline_envelope/2026-04-26/`). M3 conditional rolls up to 5a.5 M5 ship verdict.

---

## Mission

Develop all 7 Slab 4 stories in strict sequence (4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6 → 4.7). Slab 4 = **Lockstep + Gates + Cora + Ledger + Frozen-Graph**; M4 go/no-go gate **"Governance regime is architectural"** closes at 4.7 with 5-agent party-mode acceptance verdict.

**Total scope:** 27pts across 7 stories. 3 dual-gate (4.1 ci_or_compile_shape + 4.2 lane_or_package_boundary + 4.4 schema_shape) + 4 single-gate (4.3 + 4.5 + 4.6 + 4.7 SLAB CLOSING).

---

## Hard sequencing (BINDING)

```
4.1 done ──► 4.2 open
             4.2 done ──► 4.3 open
                          4.3 done ──► 4.4 open
                                       4.4 done ──► 4.5 open
                                                    4.5 done ──► 4.6 open
                                                                 4.6 done ──► 4.7 open ──► Slab 4 CLOSED
```

**Do NOT open 4.N+1 until 4.N is BMAD-CLOSED.** 4.4 ledger is consumed by 4.6 SanctumMutationEvent emission; 4.7 SLAB CLOSING aggregates evidence from all six predecessors.

---

## Per-story BMAD cycle (apply uniformly; same as 2c.x + 3.x cycles)

For each of 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7:

1. **Read the spec end-to-end** at `_bmad-output/implementation-artifacts/migration-4-{N}-*.md`. Specs already incorporate party-mode lite-amendments where authored — Slab 4 specs were authored more concisely than Slab 3 (less per-story party-mode pre-review); rely on T1 substrate verification + your dev judgment.
2. **Run T1 Readiness Block** verifying every pre-flight item + artifact-existence sweep + epic-doc-vs-architecture cross-check. **Halt and surface to operator if any pre-flight fails** (especially `app/cora/` or `app/ledger/` substrate-existence at 4.2/4.4 open).
3. **Implement the AC sequence** in declared order. Adhere to all RESOLVED-BY-VERIFICATION pins from spec headers + the substrate truths from Slab-3 close.
4. **Run regression suite** at T8: `.venv/Scripts/python.exe -m pytest -q --tb=short`. Baseline target: post-Slab-3-close pytest collection (T1-pin per Murat M-R8 inheritance — copy actual numbers from sprint-status post-3.6 close; Slab 3 added ~111 collected for the 3-scoped subset).
5. **Run lint:** `.venv/Scripts/python.exe -m ruff check app/ tests/ skills/ scripts/ marcus/` AND `.venv/Scripts/lint-imports.exe --config pyproject.toml`. Both must be clean. Import-linter contracts EXPAND from 7/7 KEPT (post-3.6) → 9/9 KEPT (4.2 adds bidirectional Cora ⊥ Marcus rules) → 10/10 (4.3 may add party-mode contract) → variants per substrate. Verify exact count post-each-story.
6. **G6 single-gate self-conducted code review** per CLAUDE.md. For dual-gate stories (4.1/4.2/4.4) also run dual-gate gate-2 protocol per spec.
7. **Run `bmad-code-review`** on the diff in scope per CLAUDE.md §3. **NEW for Slab 4 per 4.3 AC-D (FR42 evidence target):** at least one bmad-code-review finding record at Slab 4 should cite a LangSmith trace link as evidence (M4 Required Evidence per FR42; can satisfy at any 4.x story OR defer to 4.7 close for operator-paste).
8. **D12 close protocol** per spec AC. Sprint-status flip + closeout hygiene per CLAUDE.md.
9. **Commit per story.** Suggested message format:
   ```
   feat(4.N): <one-line summary>
   ```
10. **Run sandbox-AC validator** post-close on the next story before opening it: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-4-{N+1}-*.md`. Should still PASS.

---

## Pre-existing test collection errors (NOT Slab 4's concern unless touched)

**Verified at pre-Slab-3 commits:** the **8 manifest-schema collection errors** in `tests/contracts/test_33_2_*`, `tests/test_check_pipeline_manifest_lockstep.py`, `tests/test_run_wrangler_*`, `tests/test_marcus_workflow_runner_32_1.py`, `tests/test_progress_map.py`, `tests/test_run_hud.py` cluster — all tied to a `PipelineManifest` Pydantic schema mismatch (`steps` field vs `lane/entrypoint/frozen_graph_version/nodes/edges`). **PRE-EXISTING tech debt; NOT Slab 3 regressions; NOT Slab 4's concern.**

**HOWEVER:** Story 4.1 directly touches the manifest-lockstep substrate. **At 4.1 T1 sub-task:** investigate whether the PipelineManifest schema mismatch is in 4.1's path — if your `compile_run_graph(manifest, validation_mode=True)` call invokes the same schema that the failing tests probe, you may need to surface this to operator BEFORE opening dev (4.1 spec authoring did NOT verify this path; substrate-aware adaptation may be needed). Investigation steps:
- Read `tests/test_check_pipeline_manifest_lockstep.py` to see what schema fields it expects
- Compare against current `state/config/pipeline-manifest.yaml` shape (lines 45+ enumerate `nodes[*].specialist_id` + `edges[*].dispatch_envelope` per Slab-3 substrate-aware adaptation)
- If the mismatch IS in 4.1's path: HALT + surface to operator with substrate-aware adaptation recommendation (mirror Slab-3 3.1 T1 halt pattern)

**Ruff legacy failures** in unrelated files outside Slab 4 scope — do NOT attempt to fix unless your story directly touches the affected paths.

---

## Story-specific landmines (READ BEFORE OPENING EACH)

### 4.1 — Graph-Compile-Time CI Hook + Lockstep Enforcement (5pt dual ci_or_compile_shape; OPENING STORY)

- **Decision #1 bounded scope:** new `scripts/utilities/check_manifest_lockstep.py` is COMPLEMENTARY to existing `scripts/utilities/check_pipeline_manifest_lockstep.py` (Epic 33 substrate; DO NOT TOUCH).
- **Decision #4 defer-tolerance for compile_dev_graph:** 4.2 ships `compile_dev_graph`; at 4.1 dev-time, `try/except ImportError` with `pytest.skip(...)` fallback; test parametrize-skips dev-graph cases until 4.2 lands.
- **Decision #2 in-process invocation per NFR-P6:** GHA workflow invokes `python -c "from scripts.utilities.check_manifest_lockstep import main; sys.exit(main())"` (NOT subprocess).
- **Decision #3 LockstepError discriminated:** `ManifestDriftError` (block-mode-trigger-path touched without companion update) + `CompileError` (compile_run_graph or compile_dev_graph fails validation). Single base class.
- **PRE-FLIGHT INVESTIGATION (per "Pre-existing test collection errors" above):** verify whether PipelineManifest schema mismatch affects 4.1's path; HALT if substrate-aware adaptation needed.

### 4.2 — Cora Dev-Graph + Separate Thread Namespace (5pt dual lane_or_package_boundary)

- **Decision #1 bounded scope:** `app/cora/{__init__,graph,block_mode_node}.py + handlers/{plan_story,implement_story,test_story,review_story,close_story}.py` + `state/config/dev-graph-manifest.yaml`.
- **Decision #2 thread namespace:** Cora's `dev/{story_id}` MUST be distinct from Marcus's `run/{trial_id}`.
- **Decision #3 BIDIRECTIONAL `app.cora ⊥ app.marcus` import-linter (BIDIRECTIONAL — per Slab-3 substrate-aware adaptation, also against canonical `marcus/` top-level home):**
  - `app.cora.*` MUST NOT import `app.marcus.*` OR top-level `marcus.*`
  - `app.marcus.*` AND top-level `marcus.*` MUST NOT import `app.cora.*`
- **Decision #4 block-mode hook elevation:** existing `skills/bmad-agent-cora/scripts/preclosure_hook.py` runs as a NODE in the Cora graph (NOT just pre-commit hook). Pre-commit continues firing as outer guard.
- **Substrate sweep at T1:** verify `app/cora/` does NOT exist; verify `state/config/dev-graph-manifest.yaml` does NOT exist; verify `skills/bmad-agent-cora/scripts/preclosure_hook.py` exists per Epic 33 substrate.

### 4.3 — Party-Mode-as-`interrupt()` + Trace-First Review (4pt single)

- **Decision #1 bounded scope:** `app/gates/party_mode_as_interrupt.py` + `PartyModeContribution` Pydantic v2 strict + four-file-lockstep + consolidated DecisionCard meta enrichment.
- **Decision #2 PartyModeContribution shape:** `{contribution_id: UUID4, persona: str, payload: dict[str, Any], submitted_at: datetime tz-aware, trace_link: str | None}`.
- **Decision #3 trace_link format:** `https://smith.langchain.com/traces/<trace_id>` OR repo-relative trace export path; FR42 satisfied when ≥1 bmad-code-review finding record contains a trace_link matching the regex.
- **AC-D M4 evidence MAY DEFER to 4.7 close** for operator-paste OR satisfy at any 4.x story's bmad-code-review run (whichever is more practical).
- **OperatorVerdict canonical home pin from Slab-3 substrate-aware adaptation:** `from app.models.state.operator_verdict import OperatorVerdict` (NOT `app.gates.verdict`).

### 4.4 — Learning Ledger + Queries (4pt dual schema_shape)

- **Decision #1 bounded scope:** `app/ledger/{events,emitter,queries}.py + schema.sql` + LedgerEvent discriminated union (3 kinds × 4-file-lockstep = 12 lockstep artifacts) + Postgres + idempotent emission per NFR-R4 + non-fatal per NFR-I2 parallel.
- **Decision #2 LedgerEvent discriminated-union per `kind`:** `kind: Literal["verdict", "override", "sanctum_mutation"]`; per-kind subclasses; future-extensible.
- **Decision #3 idempotency key:** `idempotency_key = sha256(f"{trial_id}|{gate_id}|{kind}|{event_specific_natural_key}")`.
- **Decision #4 Postgres failure non-fatal:** if `psycopg.connect(...)` fails, return `EmissionResult(status="failed", reason=...)` + log warning + counter increment (`ledger_emission_failures_total`); caller-node does NOT raise; trial continues.
- **Sandbox-AC discipline:** `psycopg` shipped Python dep + `pytest.skip(...)` on missing service per CLAUDE.md.
- **3.5 ledger event proto-events** absorption: 3.5's submit_override + apply_override emit `kind="override"` proto-events; 4.4 LedgerEvent discriminated union absorbs these. Verify 3.5 close-state at T1.

### 4.5 — Frozen-Graph-Version Ceremony Doc + v42 Populate + Bump Policy (3pt single)

- **Decision #1 bounded scope:** `docs/dev-guide/frozen-graph-version-ceremony.md` + `runtime/graphs/v42/` populated with manifest-snapshot + dev-graph-manifest-snapshot (from 4.2) + pack-version + dispatch-registry-snapshot (interim per 2b.15 `_status` BINDING; M5 reconciles per `slab-3-m5-dispatch-registry-swap` deferred-inventory) + compiled-graph-digest stable across runs.
- **Decision #2 Tier-1/2/3 alignment with pack-version policy** per CLAUDE.md §"Pipeline lockstep regime" §"Pack version bumps are governance, not technical."
- **Decision #3 compiled-graph-digest:** SHA-256 of canonical-JSON serialization of compiled StateGraph introspection (sorted node IDs + sorted edge tuples + manifest schema_version + pack-version).
- **Substrate sweep at T1:** verify `runtime/graphs/v42/` Slab-1 stub state.
- **K-target ~1.2× honest 6 K-floor under floor 7** — operator may recalibrate at story-open OR add `test_pack_version_text_format` orthogonal to reach floor 7.

### 4.6 — Sanctum Invalidation Hook (FR59) + NFR-O3 Warnings (3pt single)

- **Decision #1 bounded scope:** `app/runtime/sanctum_watcher.py` watchdog + hash-delta + LedgerEvent SanctumMutationEvent emission (per 4.4 ledger union; verify 4.4 close-state at T1) + DecisionCardMeta `sanctum_warnings` additive field (per 3.2 cache_state extension; verify if 3.2 shipped this field OR additive minimal extension at 4.6).
- **Decision #2 mutation-timing semantics:** before-invocation → no spurious warning; during-invocation → warning logs + surfaces at next gate (NFR-O3 non-fatal); after-invocation → next-trial cold-read picks up.
- **Decision #3 hash-delta evidence shape:** SanctumMutationEvent payload = `{file_path, hash_before, hash_after, mutated_at, suggested_invalidating_commit | None}`.
- **`watchdog` Python dep verification at T1:** if absent in `pyproject.toml`, add via operator-gated AC OR sandbox-AC dev-agent install.
- **DecisionCardMeta sanctum_warnings field:** if 3.2 didn't ship this field, additive minimal extension at 4.6 (verify Slab-3 close state).

### 4.7 — Pydantic + RetryPolicy + Slab 4 Close (3pt single SLAB CLOSING; M4 GO/NO-GO GATE)

- **Decision #1 bounded scope:** (a) `app/runtime/retry_policy.py` workaround per PRD §Implementation Considerations; (b) `langgraph-state-idioms.md §6` finalized; (c) 5-agent party-mode M4 verdict at `slab-4-m4-acceptance-verdict.md` (mirror 2c.3+3.6 5-agent pattern); (d) `slab-4-retrospective.md` (mirror slab-3-retrospective.md format); (e) anti-patterns harvest cycle complete annotation; (f) D12 close protocol; (g) `next-session-start-here.md` update.
- **Decision #2 workaround pattern:** read PRD §Implementation Considerations + `langgraph-state-idioms.md §6` placeholder for the specific Pydantic + LangGraph RetryPolicy gotcha; workaround likely involves explicit re-validation OR retry-policy state-shape pin.
- **Decision #3 M4 verdict format mirrors 2c.3 + 3.6:** 4-enum consensus level (GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN / YELLOW / RED); 6-enum per-agent (adds ABSTAIN). Verbatim recording per 2c.3 P-R1 + 3.6 W-R1 binding.
- **Decision #4 retrospective format mirrors slab-3:** 4 §-headers (Pre-Audit Bundle / Slab Outcomes / Next-Slab Preparation / Slab 5a Handoff) with per-entry deferred-inventory verdicts per Murat M-R5+P-R1 binding from 2c.4.
- **Anti-patterns harvest-gate (BINDING per 2c.4 + 3.6 + Mary harvest-gate):** verdicts NOT preempted at story-author; 4.7 dev-time runs final harvest-gate evaluation; cycle-complete annotation per 2c.4 P-R3 / 3.6 AC-H pattern.
- **CONDITIONAL-M4 inheritance pattern:** if any 4.x conditional state surfaces, mirror 3.6 + 2c.4 hard-gate inheritance — Slab 4 closes as `CLOSED-WITH-CONDITIONAL-M4` if M4 verdict is CONDITIONAL-GREEN; M4 conditional rolls up to 5a.5 M5 ship verdict.

---

## Governance non-negotiables (same as 2c.x + 3.x; recap)

- **Sandbox-AC discipline (CLAUDE.md):** dev-agent ACs MUST verify via shipped Python deps + `pytest.skip(...)` on missing service. Run `validate_migration_story_sandbox_acs.py` before opening any story.
- **Gate-mode pinned at governance JSON** (`docs/dev-guide/migration-story-governance.json:64-70`). DO NOT relitigate.
- **Live API discipline:** N/A for Slab 4 (no live API calls in scope; psycopg may need live Postgres but pytest.skip on missing).
- **Hybrid working tree is sole input surface:** upstream/master severed at `3ed7c56` 2026-04-24.
- **Closeout hygiene:** every story close updates `sprint-status.yaml` first, then `next-session-start-here.md`.
- **Deferred inventory governance:** every new follow-on goes to `_bmad-output/planning-artifacts/deferred-inventory.md`; 4.7 retrospective enforces per-entry consultation verdicts per Murat M-R5+P-R1 + Paige P-R1 inheritance from 2c.4.
- **Substrate-aware adaptation discipline (Slab-3 lesson):** if T1 readiness reveals substrate mismatches against spec assumptions, HALT + apply substrate-aware adaptation pattern (mirror Slab-3 3.1 T1 halt; document in commit message). Do NOT force-fit code against bad spec assumptions.
- **No commits without per-story BMAD-CLOSE; no force-push, no `--no-verify`, no `--amend` published commits.**

---

## What "done" means for the batch

- All 7 stories show `done` in sprint-status.yaml.
- `migration-epic-4-slab-4-lockstep-gates-cora-ledger: done` (with trailing comment per AC-E enum-clarification pattern if M4 conditional per 2c.4 inheritance).
- M4 milestone: `GREEN-LIGHT 2026-04-XX` OR `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` (recorded in `slab-4-m4-acceptance-verdict.md`).
- `slab-4-retrospective.md` exists with 4 canonical §-headers + per-entry deferred-inventory verdicts.
- Anti-patterns catalog: harvest-cycle-complete annotation per 2c.4 + 3.6 patterns.
- `app/cora/` + `state/config/dev-graph-manifest.yaml` populated per 4.2.
- `app/ledger/` populated with 3 LedgerEvent kinds + queries + Postgres schema per 4.4.
- `runtime/graphs/v42/` populated per 4.5 (5 artifacts + compiled-graph-digest stable).
- `app/runtime/sanctum_watcher.py` + `app/runtime/retry_policy.py` shipped per 4.6 + 4.7.
- `next-session-start-here.md` reflects Slab 4 CLOSED + post-4.7 deferred-inventory counts.
- Regression suite: post-Slab-3-close baseline preserved (T1-pinned per Murat M-R8 inheritance).
- Import-linter contracts: EXPAND from 7/7 (post-3.6) → 9/9 (4.2 adds bidirectional Cora ⊥ Marcus) → variants per substrate at each story; verify exact count post-each-story.
- One commit per story-close (7 commits total).

---

## Escalation triggers (HALT and surface to operator)

- T1 pre-flight fails on any story (predecessor not `done`, anchor file missing, etc.).
- Sandbox-AC validator FAILS (substrate state has drifted since authoring).
- 4.1 substrate investigation reveals PipelineManifest schema mismatch IS in 4.1's path — HALT + surface for substrate-aware adaptation (mirror 3.1 T1 halt pattern).
- 4.2 substrate sweep reveals `app/cora/` already exists with content (would invert architectural model like marcus/ at Slab 3) — HALT + surface for substrate-aware adaptation.
- 4.4 Postgres unavailable for substantive period blocking AC-A through AC-D dev — surface for operator decision (defer 4.4 OR mock Postgres at unit-level + integration-level deferred).
- 4.6 watchdog Python dep absent from pyproject.toml AND operator unavailable for `uv add watchdog` — surface for decision.
- 4.7 M4 party-mode returns YELLOW or RED verdict (cannot close Slab 4 cleanly).
- Pre-existing 8 collection errors expand OR a new test starts failing that wasn't broken pre-4.x.
- Any new architectural decision surfaces (e.g., new import-linter rule beyond planned set; new dev-graph manifest field shape) requiring party-mode consensus.

---

## Reference anchors

- Spec files: `_bmad-output/implementation-artifacts/migration-4-{1..7}-*.md` (commit `7f86db3` original; potentially patched in subsequent commits)
- Sprint status: `_bmad-output/implementation-artifacts/sprint-status.yaml` (Slab 4 block at line ~810+)
- Governance JSON: `docs/dev-guide/migration-story-governance.json:64-70` (4-1 through 4-7 gate-modes pinned)
- Architecture doc: `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` (FR38-FR45 + D3 + D5 + D8 sections)
- Epic 4: `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 4 lines 1068-1245
- Anti-patterns: `docs/dev-guide/specialist-anti-patterns.md` (post-Slab-3 close state)
- Pydantic v2 checklist: `docs/dev-guide/pydantic-v2-schema-checklist.md`
- Schema-story scaffold (BINDING for 4.4): `docs/dev-guide/scaffolds/schema-story/`
- 2a.4 deferred-inventory binding (Texas AC-B-OP — REMAINS DEFERRED through Slab 4; operator addendum lands at 5a.5 latest): `_bmad-output/planning-artifacts/deferred-inventory.md` §`2a.4-followon-ac-b-op-live-retrieval`
- C3 import-linter precedent: `pyproject.toml` (line numbers vary post-Slab-3; verify before staged-delivery decisions)
- Slab-3 close evidence + Marcus canonical home: `marcus/` (Epic 30/31 lesson-planner package + 3.1 additive extensions: marcus/dispatch/contract.py + marcus/orchestrator/{supervisor,routing}.py)
- Slab-3 substrate-aware adaptation precedent (READ before opening any 4.x story): `_bmad-output/implementation-artifacts/migration-3-1-marcus-intake-orchestrator-facade-split.md` §"SUBSTRATE-AWARE ADAPTATION" header (apply same discipline if 4.x T1 reveals mismatches)
- Slab-3 close artifacts (precedent for 4.7): `_bmad-output/implementation-artifacts/{slab-3-m3-acceptance-verdict, slab-3-marcus-invariant-stub, slab-3-retrospective}.md`
- 2c.x + 3.x Codex prior-batch precedents: `_bmad-output/implementation-artifacts/{codex-handoff-2c-batch-dev, codex-handoff-3-batch-dev}.md`
- M3 conditional state context: `slab-3-m3-acceptance-verdict.md` — M3 CONDITIONAL-GREEN per W-R1-3.6-4 evidence-completeness gap (Texas AC-B-OP M1-M5 DEFERRED-PENDING-OPERATOR-WINDOW); behavioral pass clean; rolls up to 5a.5 M5 ship verdict
- M2 conditional state context: `slab-2c-m2-acceptance-verdict.md` — M2 CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per 2c.2 AC-D-OP DEFERRED; rolls up to 5a.5 M5 ship verdict

Proceed.
