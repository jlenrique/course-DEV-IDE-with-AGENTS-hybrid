# Migration Story 3.1: Marcus Intake + Orchestrator + Facade Split (Story 30-1 forward-port)

**Status:** ready-for-dev
**Sprint key:** `migration-3-1-marcus-intake-orchestrator-facade-split`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; M3 go/no-go gate "Marcus orchestrates end-to-end") — **OPENING story; Slab 3 kickoff**.
**Pts:** 5 | **Gate:** dual (per governance JSON `3-1.expected_gate_mode = "dual-gate"`, rationale: `lane_or_package_boundary`). **K-target:** ~1.5× (target 18 / floor 12; multi-module package authoring + import-linter contract + supervisor reasoning-loop preset switching + cold-read sanctum discipline; substantial new test surface).

**Slab 3 framing:** Story 3.1 is the **architectural foundation** for Slab 3. It establishes `app/marcus/` package structure (currently `__init__.py` stub only at Slab 1 close), forward-ports primary repo's **Story 30-1 duality split** (Marcus-Intake vs Marcus-Orchestrator separation with single-writer rule + Maya-facing single facade), and lands the import-linter package-boundary contracts that all subsequent Slab-3 stories depend on. Stories 3.2-3.6 build on this foundation; do NOT defer-to-later.

**Story 30-1 forward-port context (per architecture doc §"PR-R" + lesson-planner-mvp-plan.md §Epic 30):** primary repo's Story 30-1 (`30-1-marcus-duality-split`) split Marcus into:
- **Marcus-Intake** (`marcus/intake/`) — pre-packet extraction (01-04 + 4A pre-packet); emits exactly ONE event (`pre_packet_snapshot`) at 4A entry via Orchestrator's write API
- **Marcus-Orchestrator** (`marcus/orchestrator/`) — 4A loop + lock + 05+ fan-out; **sole writer** on Lesson Plan log (Quinn single-writer rule)
- **Single facade** (`facade.py::get_facade()`) — Maya-facing surface; "Marcus is Marcus, one voice" (lesson-planner-mvp-plan.md ruling amendment 17 — no user-facing string references "Intake" or "Orchestrator")
- **Golden-Trace Baseline Gate (Murat RED, primary-binding):** primary captured pre-refactor Marcus envelope I/O on trial corpus as committed fixture before opening 30-1; DoD required byte-identical post-refactor + zero test edits + coverage non-regression + facade-leak detector AC

The migration forward-ports the **package shape** (intake.py + orchestrator/{write_api,supervisor,routing}.py + facade.py per architecture doc §"app/marcus/" tree at lines 928-936) but adapts the **substrate** to LangChain/LangGraph (Plan-and-Execute supervisor by default; ReAct on `explore` preset per FR27). The Golden-Trace Baseline Gate has NO direct migration analog (no pre-existing Marcus envelope on hybrid to baseline against); migration substitutes a **facade-leak detector** + **import-linter contract** as the architectural-enforcement equivalents.

**Inheritance: marcus.dispatch.contract substrate-establishment (BINDING from 2a.4 deferred-inventory):** Texas's `run_wrangler.py:58` imports `marcus.dispatch.contract` consumed at runtime (lines 120-125, 1707-1709, 1717, 2021-2031). Story 2a.4 deferred AC-B-OP live retrieval-dispatch reactivation pending Slab-3 marcus.dispatch.contract forward-port. **Story 3.1 establishes `app/marcus/dispatch/contract.py` substrate** (DispatchKind enum + build_dispatch_envelope + build_dispatch_receipt + DispatchOutcome) so Slab 3 close can re-execute Texas AC-B-OP per the binding Murat hard-caveat at deferred-inventory entry `2a.4-followon-ac-b-op-live-retrieval`.

**Authoring queue position:** 3.1 spec authored first in Slab 3 sequence. Stories 3.2-3.6 depend on 3.1 architectural foundation; sequencing is hard:

**SUBSTRATE-AWARE ADAPTATION applied 2026-04-26 post-Codex T1 halt (Codex hard-caveat — 4 substrate mismatches verified concrete):** Story 3.1 SCOPE INVERTS — `marcus/` is the CANONICAL home (Epic 30/31 lesson-planner work shipped pre-migration; verified extensive substrate at `marcus/{intake/pre_packet.py, orchestrator/{dispatch,fanout,hil_intake,learning_event_wiring,loop,maya_walkthrough,stub_dials,trial_smoke_harness,workflow_runner,write_api}.py, facade.py, lesson_plan/}`). The migration's planned `app/marcus/` shim path was based on an incorrect mental model. **Story 3.1 narrows to the SUBSTRATE GAPS only:**

- **Substrate truth #1 — Manifest path:** `state/config/pipeline-manifest.yaml` (NOT `run-manifest.yaml` — does not exist).
- **Substrate truth #2 — Manifest field shape:** `nodes[*].specialist_id` + `edges[*].dispatch_envelope` (NOT `edges[*].dispatch_target`); verified at `pipeline-manifest.yaml` lines 45-265+. Decision #2 + AC-I rewritten.
- **Substrate truth #3 — `marcus/` is canonical, NOT a shim opportunity:** package already shipped at repo root with extensive lesson-planner substrate. Migration `app/marcus/__init__.py` Slab-1 stub remains as namespace placeholder; canonical Marcus runtime IS the existing `marcus/` package. NEW work additive only.
- **Substrate truth #4 — RunState location:** `app/models/state/run_state.py` (NOT `app/state/run_state.py`); rich substrate at `app/models/state/{_base, cache_state, model_resolution_entry, node_checkpoint, operator_verdict, run_state, sanctum_fingerprint, specialist_envelope, specialist_return, story_state, validators/}.py`.
- **Substrate truth #5 — `marcus.dispatch.contract` is the ONE genuine substrate gap:** verified via `find . -name "contract.py" -path "*marcus*"` (zero hits) + `grep -rn "class DispatchKind\|class DispatchOutcome"` (zero hits anywhere in repo). Texas's `from marcus.dispatch.contract import (DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt,)` import target IS NEW; needs additive `marcus/dispatch/{__init__, contract}.py` submodule extension to existing canonical `marcus/` package.
- **Substrate truth #6 — supervisor.py + routing.py are GENUINE gaps:** `marcus/orchestrator/` has 10 modules (dispatch, fanout, hil_intake, learning_event_wiring, loop, maya_walkthrough, stub_dials, trial_smoke_harness, workflow_runner, write_api) but NO `supervisor.py` (Plan-and-Execute + ReAct preset) and NO `routing.py` (manifest-driven). 3.1 ADDS both as additive minimal extensions.
- **Substrate truth #7 — `marcus/orchestrator/dispatch.py` is LessonPlanLog-event dispatch (Story 30-3a):** NOT the marcus.dispatch.contract substrate. Different concerns; coexist additively.

**SCOPE NARROWING — what 3.1 actually authors (post-substrate-aware adaptation):**

| Original spec said | Substrate reality | 3.1 actual scope |
|---|---|---|
| Author `app/marcus/intake.py` | `marcus/intake/pre_packet.py` already exists | **NO-OP at app/; verify existing marcus/intake/ structure adequate** |
| Author `app/marcus/orchestrator/{__init__,write_api,supervisor,routing}.py` | `marcus/orchestrator/{__init__,write_api,...}.py` exists; supervisor + routing missing | **ADD `marcus/orchestrator/supervisor.py` + `marcus/orchestrator/routing.py` only** |
| Author `app/marcus/facade.py` | `marcus/facade.py` already exists per Story 30-1 done | **NO-OP at app/; verify existing facade adequate for Marcus-first activation** |
| Author `app/marcus/dispatch/{__init__,contract}.py` + top-level `marcus/dispatch/` shim | `marcus/dispatch/` does NOT exist | **ADD `marcus/dispatch/{__init__,contract}.py` to existing canonical marcus/ package (additive minimal extension; NOT a shim — the canonical home)** |

**Per Codex T1 halt findings (verified by Claude pre-amendment):**

1. **`state/config/run-manifest.yaml` does NOT exist; live is `pipeline-manifest.yaml`.** Spec corrected throughout.
2. **`edges[*].dispatch_target` does NOT exist; live shape is `nodes[*].specialist_id` + `edges[*].dispatch_envelope`.** AC-I + Decision #2 + Decision #5 (routing) rewritten against actual manifest shape.
3. **`marcus/` is OCCUPIED** — Epic 30/31 lesson-planner package with intake + orchestrator + lesson_plan + facade ALREADY SHIPPED. Original W-R2 "top-level marcus/ shim" plan is INVERTED — `marcus/` IS the canonical home; `app/marcus/__init__.py` is the Slab-1 stub that stays as namespace placeholder OR is retired (operator decision; default = retire to remove confusion).
4. **`app/state/run_state.py` does NOT exist; live is `app/models/state/run_state.py`** with full substrate. AC-E sanctum cold-read writes fingerprint to `app.models.state.run_state.RunState` (or its `sanctum_fingerprint.py` sibling — verify at T1 which is the authoritative field-host).

**Lean party-mode amendments applied 2026-04-26 (Winston + Murat + Amelia + Paige) — RECONTEXTUALIZED post-substrate-aware-adaptation:** 3 W-BLOCKERs RESOLVED-BY-SUBSTRATE-VERIFICATION + 18 RIDERs integrated, NOW SUPERSEDED IN PART by substrate-aware adaptation above. Specifically: **W-R2 "top-level marcus/ shim" framing is RETIRED-MOOT** — `marcus/` is the canonical home, not a shim; the substance of W-R2 (Texas import resolution) STILL applies but via additive `marcus/dispatch/` submodule, NOT a re-exporting shim. Other W/M/A/P riders carry forward unchanged.

- **W-R1-3.1 + Amelia BLOCKER-1 (Decision #4 substrate mismatch) RESOLVED-BY-VERIFICATION:** Verified `skills/bmad-agent-texas/scripts/run_wrangler.py:58-63` literal import: `from marcus.dispatch.contract import (DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt,)` — **only 4 symbols** (NOT 6; DispatchEnvelope and DispatchReceipt are RETURNED by builders, not directly imported). `DispatchOutcome` is an **Enum** with members `COMPLETE / PARTIAL / FAILED` (verified at lines 120-125 `_to_dispatch_outcome` returns `.COMPLETE / .PARTIAL / .FAILED`), **NOT** a BaseModel. Builder signatures (verified at lines 1707-1709 + 2021-2023): `build_dispatch_envelope(*, dispatch_kind=DispatchKind.TEXAS_RETRIEVAL, ...)` (keyword `dispatch_kind`, not `kind`). Decision #4 + AC-G fully rebound below.

- **W-R2-3.1 + Amelia BLOCKER-1 (symbol-path namespace) RESOLVED-BY-VERIFICATION:** Texas's path resolution at lines 49-56 sets `_REPO_ROOT = _THIS_DIR.parents[2]` (= repo root) and `sys.path.insert(0, str(_REPO_ROOT))`. Texas then imports `marcus.dispatch.contract` (NO `app.` prefix). **Resolution path (b) per Amelia framing:** Story 3.1 authors a **top-level `marcus/` shim package at repo root** (`marcus/__init__.py` + `marcus/dispatch/__init__.py` + `marcus/dispatch/contract.py`) that re-exports from `app.marcus.dispatch.contract`. Architecturally cleaner than (c) PYTHONPATH gymnastics; preserves the lane-boundary discipline because the shim is a thin re-exporter, not duplicate logic. AC-G test 3 strengthened to assert `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind` (identity, not equality — catches double-import bugs).

- **W-R3-3.1 + AC-B import-linter unused-ignore (BLOCKER) RESOLVED-BY-PRECEDENT:** Verified `pyproject.toml:88-95` C3 precedent: "Slab 3 Story 3.3 adds the two future ignore_imports entries (`app.http.gate_endpoint ->` and `app.marcus.cli.gate_cli ->`) when the bridge modules materialize; import-linter rejects unused ignores, so pre-seeding them here would fail." AC-B contract 1 (facade-reachability) MUST follow C3 staged-delivery pattern: ship narrow 3.1 contract (facade reachable from the package itself + tests); stage transport-allowlist additions to 3.4 when transports materialize. Updated AC-B + K-floor table accordingly.

- **W-R4-3.1 (drop runtime stack-inspection):** AC-D's `inspect.stack()` debug-mode tripwire DROPPED. Async/await frame-walking under LangGraph event-loop is unreliable; per-mutation overhead compounds in AC-F 50-iter loop; mode-dependent enforcement violates Quinn-rule uniformity. AC-D test 2 collapses to "import-linter contract flags it" only.

- **W-R5-3.1 (per-session UUID in fingerprint):** `RunState.marcus_fingerprint = (sha256_digest, session_id)` where `session_id = uuid.uuid4()` per session-init. Closes in-process session-bleed gap that pure content-fingerprinting leaves open (FR30 cold-read).

- **W-R6-3.1 (specialist-to-marcus boundary rule):** ADDED 5th import-linter rule: `app.specialists.** -> app.marcus.{intake, orchestrator, facade}` forbidden; `app.specialists.** -> app.marcus.dispatch.contract` permitted. Pre-declares Slab 5+ specialist boundary discipline.

- **W-R7-3.1 (filed-forward to 3.6):** baseline-capture AC at 3.6 (post-3.6 Marcus envelope captured as frozen fixture; rebinds primary's amendment 12 Golden-Trace to migration substrate from Slab 4 onward). Filed in deferred-inventory as `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` named-but-not-filed follow-on.

- **M-R1-3.1 (AC-G K-recount):** Drop "Texas-import-success" as separate K-unit (derivable from importability via same `spec_from_file_location` path); AC-G K-floor: 2 (importability + Pydantic-strict).

- **M-R2-3.1 (AC-B K-recount):** 4 import-linter rules are 4 distinct architectural properties (NOT same-property-different-inputs); count as **4 K-floor units** (not 1 collapsed).

- **M-R3-3.1 (AC-F loop-count justification):** parametrize 50-iter loop over **preset variants** (`production`, `explore`) instead of arbitrary iteration count; 50 iters × 2 presets = 100 iterations total; leak-surfacing more likely under preset diversity than raw count.

- **M-R4-3.1 (AC-F string-sweep regex maintainability) + Amelia A-R1-3.1 (AST not regex):** AC-F point 2 uses **AST-based visitor** (`ast.NodeVisitor` walking `ast.Constant` with `isinstance(node.value, str)`), NOT regex. Two visitors: one for operator-facing string literals, one for code-identifier leaks. Spec calls out "AST-based, not regex-based" explicitly.

- **M-R5-3.1 (AC-E mock-the-spy anti-pattern):** AC-E test 3 reframed as PRIMARY test: write sanctum file content A → init session → capture fingerprint; overwrite with content B → init session → capture; assert fingerprints differ. Mock-spy invocation-count test demoted to supplementary smoke-check.

- **M-R6-3.1 (AC-D runtime stack-inspection FRAGILE):** confirmed with W-R4 above — DROP runtime stack-inspection; rely on import-linter static contract only.

- **M-R7-3.1 (AC-G hyphenated-path CI portability):** test uses `pathlib.Path` (NOT string concat) to build `Path(__file__).parent.parent.parent / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"`; `pytest.skip` with explicit reason if `spec_from_file_location` returns `None`. Tested cross-platform.

- **M-R8-3.1 (regression target anchoring):** T1 readiness gate adds explicit checklist item: "Regression baseline pinned to Slab-2c-close pytest collection (P passed / S skipped) — copy from `sprint-status.yaml` after 2c closes." If 2c hasn't closed when 3.1 opens, that's a **predecessor block** (not paper-overable).

- **M-R9-3.1 (AC-F leak-detector evidence collection):** test emits first iteration where leak surfaced + leaked symbol/string to debug artifact on failure (not just `assert no_leak`).

- **A-R2-3.1 (manifest substrate verification):** T1 sub-task — run `grep -r "dispatch_target" state/config/`; if absent, AC-I splits or scope inflates. Verify before dev-open. Currently UNVERIFIED at story-author time; flagged as T1 gating item.

- **A-R3-3.1 (D12 line count vs 31-1 precedent):** dev confirms at T1 against 31-1's actual D12 close protocol; spec proposes 5 lines but pin against precedent (Paige P-R3 also).

- **A-R4-3.1 (sanctum digest port — allowlist not rglob):** `_read_marcus_sanctum_digest` reads file allowlist from `skills/bmad-agent-marcus/SKILL.md` activation-sequence (or sibling manifest), NOT `rglob("*")`. Test asserts unknown subdirectories skipped (forward-compat).

- **A-R5-3.1 (`get_facade()` semantics) RESOLVED:** chose **Option C** — pure re-read each call (sanctum re-read each `get_facade()` call; no caching; performance acceptable because Marcus invoked at session-start only). Decision #5 reworded to remove "lazy accessor" framing.

- **P-R1-3.1 (migration-guide §2 sub-structure):** sub-structure third bullet renamed from "invariants preserved" to **"facade identity preserved"** to reflect orchestrator-vs-specialist role.

- **P-R2-3.1 (canonical naming):** replace "facade-leak detector" with **"facade-identity invariant test"** (test lane) + **"import-linter facade contract"** (static-analysis lane). Slab 2 invariant-family naming consistency. "Facade-leak detector" survives as informal prose only.

- **P-R3-3.1 (D12 line count):** confirmed with A-R3 above — pin against 31-1.

- **P-R4-3.1 (forward-port framing post-severance):** replace "forward-port primary's Story 30-1" globally with **"adapt primary's Story 30-1 pattern (substrate-mined from frozen upstream/master @ 3ed7c56, severance 2026-04-24 per MEMORY.md `project_upstream_severance`)"**.

- **P-R5-3.1 (amendments reconciliation paragraph):** explicit reconciliation: "Amendments 12/13/17 informed primary's Story 30-1; for the migration, hybrid governance D1-D13 supersedes where they conflict; no conflicts identified at authoring."

- **P-R6-3.1 (Decisions count):** dev evaluates at T1 whether Decisions #1-#3 (drift-resolutions) collapse into single "drift-sweep applied per TEMPLATE R6(a)" Decision block; reduces 6 → 4. Decision #6 stays as story-specific.

- **P-R7-3.1 (full D1-D13 drift sweep at T1):** T1 sub-task — full sweep of architecture-doc D1-D13 against epic-3 wording. Three-drift authoring count is acceptable; no T1 broader sweep is not.

- **P-R8-3.1 (deferred-inventory consult at story-author):** confirmed — `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` (per W-R7) lands in deferred-inventory at THIS story authoring (NOT at D12).


```
3.1 (architectural foundation) ──► 3.2 (DecisionCards) ──► 3.3 (Verdict + ResumeApi)
                                                          ──► 3.4 (transport parity)
                                                          ──► 3.5 (model override)
                                                          ──► 3.6 (E2E + M3 close)
```
3.4 + 3.5 depend on 3.3 (resume_api + DecisionCardMeta consumed); 3.6 depends on all five.

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `3-1.expected_gate_mode = "dual-gate"` (rationale: `lane_or_package_boundary`). DUAL-gate per governance pin; do not relitigate.
2. **Architecture doc** — [`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`](../planning-artifacts/architecture-langchain-langgraph-migration.md) §"app/marcus/" tree at lines 928-940 + §FR26-FR30 row at line 850. Decisions of record D1-D13 carry the architectural envelope.
3. **Epic 3 spec** — `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3 lines 892-1066 (all 6 Slab-3 stories) + §Story 3.1 lines 904-928.
4. **Migration-guide** — [`docs/dev-guide/langgraph-migration-guide.md`](../../docs/dev-guide/langgraph-migration-guide.md) §"app/marcus/" stub note at line 93 + §"Marcus" walkthrough (per AC-2c.4-H §3 anchor) — Slab 3 deepens §2 with Marcus walkthrough.
5. **Story 30-1 substrate (primary)** — `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md` §Epic 30 lines 110-115 (story 30-1 specifics) + §"R5 — Marcus duality refactor regressions" line 204 (Golden-Trace Baseline Gate context). MIGRATION ADAPTATION: substitute facade-leak detector + import-linter contract for primary's Golden-Trace Baseline (no pre-existing Marcus envelope on hybrid to baseline against).
6. **Marcus-first activation discipline** — CLAUDE.md §"Marcus first (APP production cold start)" + `skills/bmad-agent-marcus/SKILL.md` activation sequence. The supervisor's `_init_marcus()` must read `_bmad/memory/bmad-agent-marcus/` cold each session per FR30.
7. **Sanctum cold-read pattern** — Wanda's 2c.2 + Texas's 2a.4 establish the sanctum-digest read-fingerprint pattern; Marcus extends this with FR30 "no in-memory continuity from prior sessions" semantics. Reference: `app/specialists/wanda/graph.py:80-96` `_read_sanctum_digest` for the digest pattern.
8. **Texas dispatch-contract consumer (CRITICAL)** — `skills/bmad-agent-texas/scripts/run_wrangler.py:58` imports `marcus.dispatch.contract`; consumer call sites at `:120-125 _to_dispatch_outcome()`, `:1707-1709 build_dispatch_envelope(DispatchKind.TEXAS_RETRIEVAL)`, `:1717 build_dispatch_receipt()`, `:2021-2031 second-invocation-site`. Story 3.1 establishes the contract substrate; Slab 3 close (3.6) reactivates Texas AC-B-OP per `2a.4-followon-ac-b-op-live-retrieval` deferred-inventory entry.
9. **Manifest substrate (carried from Slab 1)** — `state/config/run-manifest.yaml` (or equivalent) ships per Slab 1 close; supervisor's `routing.py` consumes `compile_run_graph(manifest)` per architecture D6 validation. Verify file existence at T1; if absent, surface to operator (Slab 1 close-state regression).
10. **Severance posture** — hybrid working tree is sole input surface; upstream/master severed at commit `3ed7c56` on 2026-04-24 per CLAUDE.md `project_no_docker` + `project_upstream_severance` memory entries. Story 30-1 forward-port references the primary repo's specs (read-only); does NOT pull source code via merge.
11. **Predecessor close evidence** — Slab 2c expected `done` per sprint-status.yaml. Slab 3 opens after M2 GREEN-LIGHT (or CONDITIONAL-GREEN with addendum-pending — operator decides if 3.1 authoring proceeds with conditional state). Verify Slab 2c epic state at T1.

### Slab 3.1 artifact-existence sweep (8-point)

- **A** `app/marcus/__init__.py` exists (Slab 1 stub; verified 2026-04-26 line 1: `"""Marcus lane stub for Slab 1 import-linter contracts."""`). Story 3.1 expands the package; preserves the package marker.
- **B** `app/gates/{__init__.py, resume_api.py}` exist (Slab 1 stubs). Story 3.1 does NOT modify resume_api (that's 3.3 scope); does consume any existing import-linter contracts on the gates module.
- **C** `app/models/decision_cards/__init__.py` exists (Slab 1 stub). Story 3.1 does NOT populate (that's 3.2 scope); only references the future model-import path in routing.py for manifest's `edge.decision_card_schema` dotted-reference resolution.
- **D** `state/config/run-manifest.yaml` exists with at least the Slab-1-shape manifest (verify at T1).
- **E** `_bmad/memory/bmad-agent-marcus/` exists with sanctum content (verified per CLAUDE.md "talk to Marcus" cold-start references at `skills/bmad-agent-marcus/SKILL.md`).
- **F** `pyproject.toml` `[tool.importlinter]` C3 ignore_imports list shipped (post-2a.5 + Slab 2 close); 14 specialist + 1 wanda_validation rows.
- **G** `tests/integration/` directory + `tests/unit/` directory both exist with prior-slab tests (no `tests/unit/marcus/` yet — created at AC-D).
- **H** `skills/bmad-agent-texas/scripts/run_wrangler.py` line 58 imports `marcus.dispatch.contract` (verify; this is the Texas AC-B-OP reactivation gate consumer).

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

**Three drifts from epic spec to architecture doc + lesson-planner-mvp-plan.md:**
- **Drift D1 — Module path:** epic 3.1 says `app/marcus/orchestrator/{write_api.py, supervisor.py, routing.py}` (3 files); architecture doc tree at lines 930-936 says same 3 files PLUS `state.py` is implied via `RunState` reference. **Resolution:** epic is canonical for THIS story (only the 3 files per epic AC); `RunState` continues to live at `app/state/run_state.py` (Slab 1 substrate).
- **Drift D2 — Marcus dispatch contract:** epic 3.1 does NOT mention `marcus.dispatch.contract` substrate; the 2a.4 deferred-inventory entry mandates Slab 3 forward-port this. **Resolution:** Story 3.1 ALSO establishes `app/marcus/dispatch/contract.py` per A-2a.4-followon BINDING (NOT an epic AC, but inherited binding from prior Slab); document as Decision #4 below.
- **Drift D3 — `app/marcus/cli/`:** epic 3.4 references `app/marcus/cli/gate.py`; epic 3.3 references `app.marcus.cli.gate_cli`. CLI substrate land at 3.4 (operator-facing transports), NOT 3.1. **Resolution:** 3.1 does NOT touch `app/marcus/cli/`.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1 — adapted from migration TEMPLATE for Slab 3 architectural-foundation framing):** scope is (a) authoring `app/marcus/{intake.py, orchestrator/{__init__,write_api,supervisor,routing}.py, facade.py}`; (b) authoring `app/marcus/dispatch/{__init__,contract}.py` per Decision #4; (c) import-linter contract additions for Marcus package boundaries; (d) cold-read sanctum discipline implementation (FR30); (e) preset switching unit test (FR27); (f) facade-leak detector test (substitute for primary's Golden-Trace Baseline). NOT in scope: DecisionCard schemas (3.2); OperatorVerdict + resume_from_verdict implementations (3.3 — though resume_api stub at Slab 1 close stays consumed); transport implementations (3.4 — MCP/HTTP/CLI); model-override surfaces (3.5); E2E trial run (3.6); Cora dev-graph (Slab 4); learning ledger (Slab 4).

**Decision #2 — Plan-and-Execute vs ReAct preset semantics:** per epic 3.1 + FR27, supervisor enters Plan-and-Execute by default; ReAct on `preset: explore`. Authoritative preset enum lives at `app/marcus/orchestrator/supervisor.py::SupervisorPreset = Literal["production", "explore"]`. Manifest (`run-manifest.yaml`) carries the per-trial preset value; supervisor reads it at `_init_supervisor`. Switching is **deterministic via preset** (no LLM decision; no environment variable; no runtime mutation post-init). Unit test `tests/unit/marcus/test_preset_switching.py` covers BOTH paths.

**Decision #3 — Single-writer rule (Quinn single-writer rule per Story 30-1 forward-port):** `app/marcus/orchestrator/write_api.py` is the **sole writer** on shared state (Lesson Plan log per primary; on hybrid this generalizes to `RunState.lesson_plan_log` + `RunState.events` mutations + any other shared write paths). Marcus-Intake emits exactly ONE event (`pre_packet_snapshot`) at 4A entry **via Orchestrator's write API** (NOT directly). Architectural enforcement: import-linter contract makes `app.marcus.orchestrator.write_api` the only authorized mutator of shared state across `app/marcus/**`.

**Decision #4 (REBOUND-TO-SUBSTRATE per W-R1+W-R2 BLOCKERs RESOLVED) — `marcus.dispatch.contract` substrate establishment per 2a.4 deferred-inventory binding:**

**Verified Texas substrate at `skills/bmad-agent-texas/scripts/run_wrangler.py:58-63` (literal):**
```python
from marcus.dispatch.contract import (  # noqa: E402
    DispatchKind,
    DispatchOutcome,
    build_dispatch_envelope,
    build_dispatch_receipt,
)
```
**Path resolution context (lines 49-56):** `_REPO_ROOT = _THIS_DIR.parents[2]` (= repo root); `sys.path.insert(0, str(_REPO_ROOT))`. Texas thus expects a top-level `marcus/` package at repo root.

**Story 3.1 establishes BOTH surfaces:**
1. **Authoritative implementation at `app/marcus/dispatch/contract.py`** — the canonical home; consumed via `app.marcus.dispatch.contract` import path by future Slab 3+ stories
2. **Top-level shim at repo root: `marcus/__init__.py` + `marcus/dispatch/__init__.py` + `marcus/dispatch/contract.py`** — thin re-exporter via `from app.marcus.dispatch.contract import *` (or explicit named re-exports). Resolves Texas's `marcus.dispatch.contract` import to the same symbols. NO duplicate logic; pure pass-through.

**Authoritative symbol set (4 symbols Texas imports + 2 used internally — total 6 definitions):**

| Symbol | Type | Verified consumer | Notes |
|---|---|---|---|
| `DispatchKind` | `Enum` | Texas line 1709 `DispatchKind.TEXAS_RETRIEVAL`, line 2023 same | Member: `TEXAS_RETRIEVAL`. Future Slab 5+ specialists add members. |
| `DispatchOutcome` | **`Enum`** (NOT BaseModel; verified at lines 122-125: `return DispatchOutcome.COMPLETE / .PARTIAL / .FAILED`) | Texas `_to_dispatch_outcome()` line 120-125 | Members: `COMPLETE`, `PARTIAL`, `FAILED`. |
| `build_dispatch_envelope` | function | Texas lines 1707-1709, 2021-2023 | Signature: `build_dispatch_envelope(*, dispatch_kind: DispatchKind, run_id: str, input_packet: dict[str, Any], context_refs: list[str], correlation_id: str) -> DispatchEnvelope`. Verified keyword `dispatch_kind=DispatchKind.TEXAS_RETRIEVAL` (NOT `kind=...`). |
| `build_dispatch_receipt` | function | Texas lines 1717, 2031 | Signature: `build_dispatch_receipt(*, correlation_id: str, specialist_id: str, outcome: DispatchOutcome, output_artifacts: list[dict[str, Any]], diagnostics: list[dict[str, Any]], duration_ms: int) -> DispatchReceipt`. |
| `DispatchEnvelope` | `BaseModel` (Pydantic-v2 strict) | RETURNED by `build_dispatch_envelope` (NOT directly imported by Texas) | `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Fields per envelope-shape research; pin at dev-time against Texas builder call-site keyword args. |
| `DispatchReceipt` | `BaseModel` (Pydantic-v2 strict) | RETURNED by `build_dispatch_receipt` (NOT directly imported by Texas) | `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Fields per receipt-shape research; pin at dev-time against Texas builder call-site keyword args. |

This ENABLES (does NOT execute) Texas AC-B-OP reactivation; Slab 3 close (3.6) re-runs the live Texas evidence per Murat hard-caveat at deferred-inventory entry. **Why establish here, not at 3.6:** Texas's import statement currently fails at module-load if `marcus.dispatch.contract` is absent; Slab 2 specialists' tests work around this via `pytest.skip(...)` patterns; establishing the substrate at 3.1 unblocks Slab-3 work that may transitively touch the Texas import path.

**Identity invariant (top-level shim correctness):** `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind` (Python `is` identity, not equality). Catches double-import bugs where the shim accidentally creates parallel symbol definitions instead of re-exporting. AC-G test 3 asserts this identity.

**Decision #5 (REWORDED per W-R5 + A-R4 + A-R5 RESOLUTION = Option C) — Marcus-first activation discipline implementation (FR30 cold-read):** supervisor's `_init_marcus()` reads `_bmad/memory/bmad-agent-marcus/` fresh on each session-open via `_read_marcus_sanctum_digest` (allowlist-based, NOT `rglob("*")` — reads file allowlist from `skills/bmad-agent-marcus/SKILL.md` activation-sequence per A-R4-3.1; unknown subdirectories skipped for forward-compat). Fingerprint stored as **tuple `(sha256_digest: str, session_id: uuid.UUID)`** per W-R5-3.1 — `session_id = uuid.uuid4()` per session-init closes the in-process session-bleed gap that pure content-fingerprinting leaves open. **Pure re-read each `get_facade()` call (Option C per A-R5-3.1):** `get_facade()` returns a fresh instance each call; sanctum re-read each call. Performance acceptable because Marcus invoked at session-start only. **NO module-level singleton; NO `@lru_cache`; NO class-instance state survives any boundary.** "Lazy accessor" framing dropped from spec language (was misleading per A-R5).

**Decision #6 (RENAMED per Paige P-R2-3.1) — Facade-identity invariant test + import-linter facade contract (substitute for primary's Golden-Trace Baseline):** since hybrid has NO pre-existing Marcus envelope to baseline against (per P-R4-3.1: substrate-mined from frozen upstream/master @ 3ed7c56, severance 2026-04-24 per MEMORY.md `project_upstream_severance`), the migration substitutes the **facade-identity invariant test** (test lane) + **import-linter facade contract** (static-analysis lane) as the architectural-enforcement equivalents. Slab 2 invariant-family naming preserved.

**Test mechanics per amendments:**
- **AC-F point 1 (50-iter loop) parametrized over preset variants per Murat M-R3-3.1:** `production` preset × 50 iters AND `explore` preset × 50 iters = 100 iterations total; leak-surfacing more likely under preset diversity than raw iteration count.
- **AC-F point 2 (operator-string sweep) is AST-based per Murat M-R4-3.1 + Amelia A-R1-3.1:** `ast.NodeVisitor` walking `ast.Constant` nodes with `isinstance(node.value, str)` — distinguishes operator-facing string literals from code identifiers reliably; NO regex on source text. Two visitors: one for string literals, one for code-identifier leaks (`ast.Name` / `ast.Attribute`).
- **AC-F point 3 (negative-import test) covered via import-linter contract** at AC-B (5 rules per W-R6-3.1).
- **AC-F evidence collection per Murat M-R9-3.1:** on test failure, emit first iteration where leak surfaced + leaked symbol/string to debug artifact.

Lesson-planner-mvp-plan.md ruling amendment 17 ("Marcus is Marcus, one voice — no user-facing string references 'Intake' or 'Orchestrator'") is the substrate origin per P-R5-3.1 reconciliation paragraph: "Amendments 12/13/17 informed primary's Story 30-1; for the migration, hybrid governance D1-D13 supersedes where they conflict; no conflicts identified at authoring."

**Filed-forward to 3.6 per W-R7-3.1 (NEW deferred-inventory entry at story-author per CLAUDE.md §3):** `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` — at 3.6 spec-author time, file an explicit baseline-capture AC: capture post-3.6 Marcus envelope on first trial corpus run as frozen fixture; rebinds primary's amendment 12 (Golden-Trace Baseline) to migration substrate from Slab 4 onward; without this, regression-detection blind spot persists indefinitely.

---

## Story

As a **dev agent forward-porting primary repo's Story 30-1 duality split + establishing the Slab 3 architectural foundation**,
I want **`app/marcus/{intake.py, orchestrator/{__init__,write_api,supervisor,routing}.py, facade.py, dispatch/{__init__,contract}.py}` authored with Marcus-first activation discipline + Plan-and-Execute supervisor (ReAct on `explore` preset) + manifest-driven routing + sanctioned single-writer pattern + cold-read sanctum (FR30) + import-linter contracts enforcing package boundary + facade-leak detector substitute for primary's Golden-Trace Baseline + marcus.dispatch.contract substrate enabling 2a.4-deferred Texas AC-B-OP reactivation at Slab 3 close**,
So that **FR26 + FR27 + FR30 are met, Marcus is the SPOT operator-facing surface via `app.marcus.facade.get_facade()`, the Slab 3 architectural foundation is in place for stories 3.2-3.6 to build on, and Texas's `marcus.dispatch.contract` import is no longer a soft-fail (live AC-B-OP can re-execute at 3.6)**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Sandbox-AC compliant.

### AC-3.1-A — `marcus/` package canonical-extension (substrate-aware adaptation)

- **Given** `marcus/` package is OCCUPIED with Epic 30/31 lesson-planner substrate (verified 2026-04-26: `marcus/{__init__.py, facade.py, intake/pre_packet.py, orchestrator/{__init__,dispatch,fanout,hil_intake,learning_event_wiring,loop,maya_walkthrough,stub_dials,trial_smoke_harness,workflow_runner,write_api}.py, lesson_plan/...}`); **`marcus/dispatch/`, `marcus/orchestrator/supervisor.py`, `marcus/orchestrator/routing.py` do NOT exist** (genuine substrate gaps)
- **And** `app/marcus/__init__.py` Slab-1 stub remains as namespace placeholder (operator decision at T1 whether to retire or keep — default = keep with comment annotating "Slab-1 stub; canonical Marcus runtime is at top-level marcus/ per Story 31-1 / 30-1 lesson-planner package")
- **When** the dev agent authors **additive minimal extensions to existing canonical `marcus/` package**:
  ```
  marcus/
  ├── orchestrator/
  │   ├── supervisor.py                 # NEW — Plan-and-Execute default, ReAct on explore preset (FR27)
  │   └── routing.py                    # NEW — manifest-driven specialist routing (consumes pipeline-manifest.yaml::nodes[*].specialist_id + edges[*].dispatch_envelope per substrate-truth #2)
  └── dispatch/
      ├── __init__.py                   # NEW
      └── contract.py                   # NEW per Decision #4 (Texas import target — ONE genuine substrate gap)
  ```
- **Verification of existing substrate (T1 sub-task):** confirm `marcus/intake/pre_packet.py`, `marcus/facade.py`, `marcus/orchestrator/write_api.py` are adequate for FR26+FR30 OR file deltas as in-scope additive extensions. **DO NOT duplicate logic** at `app/marcus/`; canonical home is `marcus/`.
- **Then** 4 NEW files exist (supervisor + routing + dispatch/__init__ + dispatch/contract); existing 12+ marcus/ modules untouched; ruff clean; `pyproject.toml` C3 `ignore_imports` extended IFF any new direct `marcus.*.* -> app.gates.resume_api` imports occur (likely none at 3.1 — supervisor + routing don't depend on resume_api).
- **Test pin:** `tests/unit/marcus/test_marcus_package_canonical_extension.py` — 1 test asserting (a) existing 12+ marcus/ modules still importable (no regression to Epic 30/31 work); (b) NEW 4 files exist + each imports cleanly; (c) `marcus/dispatch/contract.py` exposes the 4 Texas-needed symbols + 2 BaseModels per Decision #4 substrate-rebound.

### AC-3.1-B — Import-linter package boundary contract (DUAL-GATE gate-1; staged-delivery per W-R3 + C3 precedent)

- **Given** import-linter contracts at `pyproject.toml [tool.importlinter]` carry the Slab-1 + Slab-2 contract baseline (3/3 KEPT per `pyproject.toml:88-95` C3 precedent: "import-linter rejects unused ignores, so pre-seeding them here would fail")
- **When** the dev agent extends contracts with Marcus package-boundary rules — **STAGED DELIVERY per W-R3-3.1 + C3 precedent: only rules whose source/forbidden modules MATERIALIZE at 3.1 close ship now; transport-allowlist additions deferred to 3.4 when transports materialize**:
  - **Rule 1 (3.1-shippable) — write_api single-writer (Decision #3):** `app.marcus.orchestrator.write_api` is the ONLY authorized mutator surface across `app/marcus/**`; other modules in `app.marcus.**` MUST NOT import shared-state mutation paths (e.g., direct `RunState.events.append` from `app.marcus.intake` is forbidden).
  - **Rule 2 (3.1-shippable) — no-cora-imports:** `app.marcus.*` MUST NOT import `app.cora.*` (forward-pointer to Slab 4 Cora dev-graph; lane separation per FR40). NOTE: `app.cora` does not exist at 3.1; rule type is "forbidden contract" with `forbidden_modules = ["app.cora"]` — works without the target existing (no unused ignore).
  - **Rule 3 (3.1-shippable) — dispatch-contract reachability:** `app.marcus.dispatch.contract` MAY be re-exported by top-level `marcus.dispatch.contract` shim (per Decision #4 W-R2 RESOLVED); this is a documented architectural exception, not enforced by import-linter (contracts target `app.*` namespace; `marcus/` shim sits outside).
  - **Rule 4 (3.1-shippable per W-R6-3.1 NEW) — specialist-to-marcus boundary:** `app.specialists.**` MUST NOT import `app.marcus.{intake, orchestrator, facade}`; MAY import `app.marcus.dispatch.contract`. Pre-declares Slab 5+ specialist boundary discipline.
  - **Rule 5 (DEFERRED TO 3.4 per W-R3-3.1 + C3 precedent) — facade-reachability:** `app.marcus.facade` reachable ONLY from `app.marcus.cli.*` + `app.mcp_server.tools.*` + `app.http.*`. **DO NOT SHIP AT 3.1** — `app.marcus.cli.*` and `app.http.*` do not exist at 3.1; pre-seeding the ignore_imports would fail per C3 line-93 precedent. Story 3.4 adds this rule when transports materialize.
- **Then** `lint-imports --config pyproject.toml` returns **N/N KEPT** where N = baseline 3 + 4 new (Rules 1-4) = **7/7 KEPT** at 3.1 close. Story 3.4 raises N to 8 by adding Rule 5.
- **Test pins per Murat M-R2-3.1 (4 K-floor units; NOT collapsed):**
  1. `tests/integration/marcus/test_marcus_import_linter_contract.py` — 4 tests, **one per rule** (each tests a DISTINCT architectural property; M-R18 parametrize-collapse does NOT apply — same-property-different-inputs is the collapse criterion, but 4 different rules are 4 different properties): `test_write_api_single_writer_rule`, `test_no_cora_imports_rule`, `test_dispatch_contract_shim_re_export_identity`, `test_specialist_to_marcus_boundary_rule`. Each test constructs synthetic violation + asserts rejection.
  2. Lint-imports CI integration verified by running the harness post-AC-A authoring; 7/7 KEPT.

### AC-3.1-C — Plan-and-Execute supervisor with ReAct preset switch (FR27)

- **Given** `app/marcus/orchestrator/supervisor.py` is authored
- **When** a trial is started with `preset: production`
- **Then** Plan-and-Execute reasoning loop runs; each step is routed per manifest via `routing.py`; **no inline specialist selection** (every routing decision goes through `routing.route_step(state, manifest)` which reads the manifest's `edge.dispatch_target`).
- **Given** the same trial is started with `preset: explore`
- **When** the supervisor enters
- **Then** ReAct mode runs instead; switching is **deterministic via preset** (no LLM-decided; no environment variable; no runtime mutation post-init).
- **Test pin:** `tests/unit/marcus/test_preset_switching.py` — 2 tests:
  1. `test_supervisor_runs_plan_and_execute_when_preset_production` — construct `Supervisor(preset="production")` + run a 3-step trial against fixture manifest; assert reasoning-loop type is Plan-and-Execute (mode flag or class hierarchy check); assert 3 manifest-driven routing decisions occurred.
  2. `test_supervisor_runs_react_when_preset_explore` — construct `Supervisor(preset="explore")` + run a 3-step trial; assert mode flag is ReAct; assert 3 manifest-driven routing decisions occurred (preset switches reasoning loop, NOT routing source).

### AC-3.1-D — Single-writer rule enforcement (Decision #3 + import-linter ONLY per W-R4 + M-R6 BLOCKERs)

- **Given** `app/marcus/orchestrator/write_api.py` is the sole writer on shared state per Decision #3 + Quinn single-writer rule
- **When** `intake.py::extract_pre_packet(state)` runs at 4A entry
- **Then** intake emits the `pre_packet_snapshot` event **via `write_api.append_event(state, event)`** (NOT direct `state.events.append(...)`). Direct `RunState` mutation outside `write_api` is forbidden by the **import-linter contract from AC-B Rule 1** as the SOLE architectural enforcement. **`inspect.stack()` runtime tripwire DROPPED per W-R4-3.1 + M-R6-3.1 BLOCKERs:** async/await frame-walking under LangGraph event-loop is unreliable; per-mutation overhead compounds in AC-F 100-iter loop; mode-dependent enforcement violates Quinn-rule uniformity.
- **Test pin:** `tests/unit/marcus/test_single_writer_rule.py` — 2 tests:
  1. `test_intake_emits_via_write_api` — invoke `extract_pre_packet(state)`; assert exactly ONE event appended to `state.events`; assert event was emitted via `write_api.append_event` (mock-spy assertion on the function).
  2. `test_direct_mutation_outside_write_api_is_caught_by_import_linter` — synthetic test asserts the import-linter Rule 1 from AC-B flags a direct mutation source. **NO runtime stack-inspection path** (dropped per W-R4 + M-R6).

### AC-3.1-E — FR30 cold-read sanctum discipline (Marcus-first activation; per Decision #5 REWORDED + W-R5 + A-R4 + M-R5)

- **Given** `_bmad/memory/bmad-agent-marcus/` exists with sanctum content
- **When** a new session opens and `get_facade()` is invoked (Option C per Decision #5: pure re-read each call; NO singleton, NO `@lru_cache`)
- **Then** `_read_marcus_sanctum_digest()` is invoked fresh; fingerprint stored in `RunState.marcus_fingerprint = (sha256_digest: str, session_id: uuid.UUID)` per W-R5-3.1 (per-session UUID closes in-process session-bleed gap); allowlist-based file enumeration per A-R4-3.1 (reads file allowlist from `skills/bmad-agent-marcus/SKILL.md` activation-sequence; NOT `rglob("*")`).
- **Given** sanctum content changes between sessions
- **When** the supervisor re-initializes
- **Then** `marcus_fingerprint[0]` (sha256_digest) updates to reflect the new content; `marcus_fingerprint[1]` (session_id) is a fresh UUID; ledger event emitted for the sanctum read.
- **Test pin per Murat M-R5-3.1 (mock-the-spy anti-pattern fix):** `tests/unit/marcus/test_marcus_cold_read.py` — 3 tests (parametrize-collapsible per Murat M-R18 → 2 K-floor units; **fingerprint-changes-on-content-change is the PRIMARY test, not invocation-count spy**):
  1. **PRIMARY (M-R5):** `test_marcus_fingerprint_changes_when_sanctum_changes` — write sanctum file content A → init session → capture fingerprint; overwrite with content B → init session → capture fingerprint; assert `fingerprint_a[0] != fingerprint_b[0]` (sha256 changed); assert `fingerprint_a[1] != fingerprint_b[1]` (session_id is fresh UUID).
  2. `test_marcus_fingerprint_populated_on_init` — call `get_facade()`; assert `state.marcus_fingerprint` is `(non-empty-sha256-hex, uuid.UUID-instance)`.
  3. **SUPPLEMENTARY smoke-check:** `test_no_singleton_short_circuit_across_calls` — call `get_facade()` twice with NO intervening sanctum mutation; assert each returns a FRESH instance (`facade_1 is not facade_2`); assert each has its OWN fresh `session_id` (proves no module-level singleton).
- **Allowlist-source pin per A-R4-3.1:** `_read_marcus_sanctum_digest` reads file allowlist from `skills/bmad-agent-marcus/SKILL.md` activation-sequence (parse Markdown for the activation-files block). Test asserts unknown subdirectories under `_bmad/memory/bmad-agent-marcus/` are SKIPPED (forward-compat: when sanctum grows new dirs, digest stays stable until allowlist is bumped).

### AC-3.1-F — Facade-identity invariant test + import-linter facade contract (substitute for Golden-Trace Baseline per Decision #6 RENAMED + M-R3 + M-R4 + M-R9 + A-R1)

- **Given** primary repo's Story 30-1 had a Golden-Trace Baseline Gate (Murat RED, primary-binding) that hybrid does NOT have a baseline-target for (substrate-mined from frozen `upstream/master @ 3ed7c56` per P-R4-3.1)
- **When** the dev agent authors the substitute facade-identity invariant test
- **Then** `tests/integration/marcus/test_facade_identity_invariant.py` (renamed per P-R2-3.1) covers:
  1. **PRESET-PARAMETRIZED 100-iter loop per Murat M-R3-3.1:** parametrize over 2 preset variants (`production`, `explore`); 50 iterations each = 100 total. Simulate plan-and-execute iterations through `get_facade().run_step(state)`; assert operator-visible `state.events` log shows ONE Marcus identity (no `actor: "Marcus-Intake"` or `actor: "Marcus-Orchestrator"` separate identities; only `actor: "Marcus"`). Per Murat M-R9-3.1: on failure, emit first iteration where leak surfaced + the leaked symbol/string to a debug artifact (NOT just `assert no_leak`).
  2. **AST-based operator-facing string sweep per Murat M-R4-3.1 + Amelia A-R1-3.1:** TWO `ast.NodeVisitor` visitors:
     - **Visitor A (string literals):** walks `ast.Constant` nodes with `isinstance(node.value, str)`; checks each string for leak patterns (`"Marcus-Intake"`, `"Marcus-Orchestrator"`, etc. — operator-facing labels). Excludes module-docstrings (`ast.Module.body[0].value` if it's a `Constant` of `str`).
     - **Visitor B (code-identifier leaks):** walks `ast.Name` and `ast.Attribute` nodes; flags references like `intake_module` / `orchestrator_module` accessed from outside `app/marcus/_internal/` package.
     - **NO regex on source text** — regex is fragile against docstrings, f-strings, multi-line strings (rejected per Amelia A-R1).
  3. **Negative test:** non-facade direct invocation of `app.marcus.orchestrator.supervisor.run_step(...)` from a test surface that's NOT in the facade-allowlist fails the **import-linter facade contract** (deferred to 3.4 per AC-B Rule 5 staging; at 3.1 this test asserts the package-internal mutation rules from AC-B Rules 1+4 only).
- **Test pin per Murat M-R3 + M-R4 + M-R9 + Amelia A-R1:** `tests/integration/marcus/test_facade_identity_invariant.py` — 3 tests; each is independent property (NOT collapsible). Loop test parametrizes over 2 presets × 50 iters = 100 total iterations.

### AC-3.1-G — `marcus.dispatch.contract` substrate enables Texas import (BINDING per 2a.4 deferred-inventory; SUBSTRATE-REBOUND per W-R1+W-R2 RESOLVED)

- **Given** Texas's `skills/bmad-agent-texas/scripts/run_wrangler.py:58-63` imports literal: `from marcus.dispatch.contract import (DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt,)` — **only 4 symbols** (verified 2026-04-26); consumed at lines 120-125 (`_to_dispatch_outcome` returns `DispatchOutcome.COMPLETE / .PARTIAL / .FAILED`), 1707-1709 (`build_dispatch_envelope(*, dispatch_kind=DispatchKind.TEXAS_RETRIEVAL, ...)`), 1717 (`build_dispatch_receipt(*, ...)`), 2021-2031
- **When** the dev agent authors:
  1. **Authoritative implementation** at `app/marcus/dispatch/contract.py` per Decision #4 (REBOUND) — 4 Texas-imported symbols + 2 internal types (DispatchEnvelope + DispatchReceipt as Pydantic-v2 BaseModels returned by builders); `DispatchKind` and `DispatchOutcome` as **Enums** (NOT BaseModels per W-R1 RESOLVED)
  2. **Top-level shim** at repo root: `marcus/__init__.py` + `marcus/dispatch/__init__.py` + `marcus/dispatch/contract.py` re-exporting via `from app.marcus.dispatch.contract import *` (or explicit named re-exports of 4 Texas-needed symbols + 2 BaseModel types) per W-R2 RESOLVED
- **Then** BOTH import paths resolve to the same symbols:
  - `from app.marcus.dispatch.contract import DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt` succeeds
  - `from marcus.dispatch.contract import DispatchKind, DispatchOutcome, build_dispatch_envelope, build_dispatch_receipt` succeeds (Texas's actual import line)
  - **Identity invariant per W-R2:** `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind` (Python `is` identity, not equality) — proves shim re-exports rather than parallel definitions
- **And** `DispatchKind.TEXAS_RETRIEVAL` is a valid enum member (Texas-binding); `DispatchOutcome.{COMPLETE, PARTIAL, FAILED}` are valid enum members
- **And** importing the contract module does NOT execute live API calls (substrate-only; Texas AC-B-OP reactivation is deferred to Slab 3 close 3.6)
- **And** the Pydantic-v2 model contracts (DispatchEnvelope + DispatchReceipt; the 2 BaseModels — NOT DispatchKind or DispatchOutcome which are Enums) carry `model_config = ConfigDict(extra="forbid", validate_assignment=True)` per migration four-file-lockstep convention
- **Test pins per Murat M-R1-3.1 K-recount (AC-G K-floor: 2; "Texas-import-success" derivable from importability):**
  1. `tests/unit/marcus/test_dispatch_contract_importable.py` — 1 test asserting BOTH `marcus.dispatch.contract` AND `app.marcus.dispatch.contract` import cleanly + all 4 Texas-needed symbols present at both paths + `DispatchKind.TEXAS_RETRIEVAL` member exists + `DispatchOutcome.{COMPLETE, PARTIAL, FAILED}` members exist + **identity invariant**: `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind`. **K-floor: 1 (single multi-property test).**
  2. `tests/unit/marcus/test_dispatch_contract_pydantic_strict.py` — 2 tests (parametrize over 2 model classes → 1 K-floor unit per M-R18) asserting `DispatchEnvelope` + `DispatchReceipt` each have `extra="forbid"` + `validate_assignment=True`. **K-floor: 1.**
  3. `tests/integration/marcus/test_texas_run_wrangler_imports_succeed.py` — 1 test asserting Texas's `run_wrangler.py` is module-loadable per Murat M-R7-3.1 mechanics: use `importlib.util.spec_from_file_location("run_wrangler", Path(__file__).parents[3] / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py")` (`pathlib.Path` parts, NOT string concat for cross-platform); `pytest.skip` with explicit reason if `spec_from_file_location` returns `None`. **NOT a separate K-floor unit per M-R1-3.1** (derivable from importability via same path-resolution mechanism).

### AC-3.1-H — `app/marcus/intake.py` pre-packet extraction (Story 30-1 lift)

- **Given** `intake.py` does not exist at Slab 1 close
- **When** the dev agent authors `intake.py::extract_pre_packet(state) -> PrePacketSnapshot` per Story 30-1 lift
- **Then** the function reads the operator-supplied input bundle fields (per Slab 1 input-bundle schema), normalizes them per the 4A pre-packet shape, and returns a Pydantic-v2 strict `PrePacketSnapshot` model (extra=forbid + validate_assignment=True).
- **And** intake emits the `pre_packet_snapshot` event via `write_api.append_event(state, event)` per Decision #3 (NOT direct mutation).
- **Test pin:** `tests/unit/marcus/test_intake_pre_packet.py` — 2 tests:
  1. `test_pre_packet_snapshot_shape_strict` — construct snapshot with valid fields; assert model_config; reject `extra_field=...` with `ValidationError`.
  2. `test_intake_appends_one_event_via_write_api` — invoke `extract_pre_packet(state)`; assert exactly one `pre_packet_snapshot` event appended; mock-spy on `write_api.append_event` (called exactly once).

### AC-3.1-I — `app/marcus/orchestrator/routing.py` manifest-driven specialist routing

- **Given** `state/config/run-manifest.yaml` exists with edge dotted-references for specialists (per Slab 1 substrate)
- **When** the dev agent authors `routing.py::route_step(state, manifest) -> RoutingDecision`
- **Then** the function reads `manifest.edges[state.current_node].dispatch_target` (or equivalent manifest path) + returns a typed `RoutingDecision(target_specialist, dispatch_kind, ...)`. **No inline specialist selection** (no `if state.current_node == 'narration': use Irene` patterns; everything routed through manifest).
- **Test pin:** `tests/unit/marcus/test_routing_manifest_driven.py` — 2 tests:
  1. `test_routing_reads_manifest_edge_dispatch_target` — fixture manifest with 3 edges; invoke `route_step(state, manifest)` for each; assert returned target matches manifest spec.
  2. `test_routing_no_inline_specialist_selection` — grep `app/marcus/orchestrator/routing.py` source for hardcoded specialist names (Irene, Kira, Texas, Gary, Vera, Quinn-R, etc.); assert ZERO hits (everything via manifest lookup).

### AC-3.1-J — Anti-pattern catalog harvest (per R6)

- **Given** the catalog is at A1-A13 + 2c.4 harvest verdict (catalog count 13-N post-2c.4 close)
- **When** 3.1 close runs
- **Then** **NO new anti-pattern signals expected** at this story (Slab 3 architectural foundation; mostly forward-port from primary). If any signals surface during dev (e.g., "primary spec bound implementation pattern that doesn't translate cleanly to LangGraph"), file as candidate A<N+1> per harvest-gate (documented burn OR party-mode consensus).

### AC-3.1-K — TEMPLATE compliance (per R1–R14 v2.4)

R1–R14 v2.4 honored where applicable. **Most rules adapted for Slab-3 architectural-foundation framing** (TEMPLATE was authored for Slab 2b per-specialist migration; Slab 3 is foundational not migrational). Applicable: R1 bounded scope (Decision #1); R6 framework-drift harvest (per (a) above); R8 K-floor recalibration (~1.5× target 18 / floor 12); R-DUAL-GATE protocol (per AC-L below).

### AC-3.1-L — D12 close protocol (DUAL-gate; lane_or_package_boundary; FIVE-line for dual)

1. **Invariant preservation:** Marcus SPOT (`get_facade()` is sole operator-facing surface); cold-start sanctum-read fingerprint discipline (FR30); HIL-paused (preserved via not-yet-implemented OperatorVerdict at 3.3); Marcus-first activation discipline (CLAUDE.md); specialist registry preserved (not modified at 3.1; consumed via routing).
2. **Anti-pattern harvest:** N/A unless surfaced (per AC-J).
3. **Migration-guide update:** §2 (Specialist Walkthrough) gains a new "Marcus" section with FR26-FR30 mapping + the duality-split forward-port reference + facade-leak detector substitute rationale.
4. **TEMPLATE compliance:** R1, R6, R8, R-DUAL-GATE honored. Numeric anchors recorded: 9 NEW files + 1 MODIFIED + 4/4 import-linter contracts + 50-iteration facade-leak loop.
5. **Dual-gate gate-1 (architectural):** import-linter contract additions verified GREEN at 4/4 KEPT; package boundary architecturally enforced. **Dual-gate gate-2 (operator architectural review):** operator confirms Marcus-first activation discipline implementation + facade-leak detector adequacy as Golden-Trace-Baseline-substitute (reading Decision #6 reasoning).

### AC-3.1-M — Sprint-status state-flips at filing AND at close

At filing: `migration-3-1-marcus-intake-orchestrator-facade-split: ready-for-dev` + `migration-epic-3-slab-3-marcus-orchestration: in-progress` opens. At close: `migration-3-1-...: done`; epic stays `in-progress` (closes at 3.6 SLAB-CLOSING). `last_updated` field updated.

---

## File Structure Requirements

### NEW files (PERSISTENT)

```
app/marcus/
├── intake.py                                 # AC-H Story 30-1 pattern (substrate-mined per P-R4)
├── orchestrator/
│   ├── __init__.py
│   ├── write_api.py                          # AC-D single-writer per Decision #3 (import-linter ONLY enforcement per W-R4)
│   ├── supervisor.py                         # AC-C Plan-and-Execute + ReAct preset
│   └── routing.py                            # AC-I manifest-driven
├── facade.py                                 # AC-A get_facade() pure re-read per Decision #5 Option C (NO singleton)
└── dispatch/
    ├── __init__.py
    └── contract.py                           # AC-G Decision #4 REBOUND substrate (DispatchKind+DispatchOutcome Enums; DispatchEnvelope+DispatchReceipt BaseModels; build_dispatch_envelope+build_dispatch_receipt functions)

marcus/                                       # NEW top-level shim per W-R2 BLOCKER RESOLVED (Texas's `from marcus.dispatch.contract import` resolution path)
├── __init__.py                               # thin re-exporter
└── dispatch/
    ├── __init__.py
    └── contract.py                           # `from app.marcus.dispatch.contract import *` (or named re-exports)

tests/unit/marcus/
├── __init__.py
├── test_marcus_package_shape.py              # 1 test (AC-A; includes top-level marcus/ shim presence)
├── test_preset_switching.py                  # 2 tests (AC-C)
├── test_single_writer_rule.py                # 2 tests (AC-D; import-linter ONLY per W-R4 + M-R6)
├── test_marcus_cold_read.py                  # 3 tests (AC-E; PRIMARY = fingerprint-changes-on-content-change per M-R5; parametrize-collapsible to 2 K-floor)
├── test_intake_pre_packet.py                 # 2 tests (AC-H)
├── test_routing_manifest_driven.py           # 2 tests (AC-I)
├── test_dispatch_contract_importable.py      # 1 test (AC-G; both import paths + identity invariant per W-R2)
└── test_dispatch_contract_pydantic_strict.py # 2 tests (AC-G; only 2 BaseModels per W-R1 RESOLVED — DispatchEnvelope + DispatchReceipt; DispatchKind+DispatchOutcome are Enums)

tests/integration/marcus/
├── __init__.py
├── test_marcus_import_linter_contract.py     # 4 tests (AC-B; 4 distinct rules → 4 K-floor units per M-R2; staged-delivery: 4 of 5 rules ship at 3.1)
├── test_facade_identity_invariant.py         # 3 tests (AC-F renamed per P-R2; preset-parametrized 100-iter loop per M-R3; AST-based string sweep per M-R4+A-R1; debug-artifact emission per M-R9)
└── test_texas_run_wrangler_imports_succeed.py # 1 test (AC-G; Path-based per M-R7; NOT separate K-floor — derivable from importability per M-R1)
```

### MODIFIED files

- `app/marcus/__init__.py` — exports `get_facade` only per Decision #6 (single-identity surface).
- `pyproject.toml` `[tool.importlinter]` — 1 new package-boundary contract added (Marcus); existing 3 contracts preserved (4/4 total).
- `state/config/run-manifest.yaml` — verify shape carries `edge.dispatch_target` field for routing.py consumption; if missing, add per Slab 1 forward-port pattern.
- `docs/dev-guide/langgraph-migration-guide.md` — §2 Marcus walkthrough section added per AC-L §3.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-M.

### NOT modified

- `app/gates/resume_api.py` — Slab 1 stub preserved; AC-3.3 implements `resume_from_verdict`.
- `app/models/decision_cards/` — empty Slab 1 stub preserved; AC-3.2 implements DecisionCard schemas.
- `app/specialists/**` — DO NOT TOUCH (Slab 2 substrate; Marcus consumes via routing only).
- `_bmad/memory/bmad-agent-marcus/` — READ-ONLY substrate (operator-curated).
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — DO NOT TOUCH (Texas substrate; only enables its import via AC-G; live AC-B-OP reactivation deferred to 3.6 per `2a.4-followon-ac-b-op-live-retrieval`).
- `app/cora/` — DO NOT TOUCH (Slab 4 scope; lane separation per FR40 enforced via import-linter rule from AC-B).

---

## Testing Requirements

**K-target ~1.5× (target 18 / floor 12).** Test count and K-floor accounting per Murat M-R18 honest-count discipline + post-amendment recount per Murat M-R1+M-R2 BLOCKERs:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 1 (package shape; includes top-level marcus/ shim presence) | **1** |
| B | 4 (4 distinct rules per M-R2; NOT collapsed) + lint-imports CI | **5** (4 rules + lint-imports CI as 5th orthogonal property) |
| C | 2 (preset production + preset explore) | **2** |
| D | 2 (write_api spy + import-linter-flags-direct-mutation; runtime stack-inspection DROPPED per W-R4+M-R6) | **2** |
| E | 3 (PRIMARY fingerprint-changes-on-content per M-R5 + populated-on-init + no-singleton-short-circuit) | **2** (parametrize-collapsible per M-R18) |
| F | 3 (preset-parametrized 100-iter loop per M-R3 + AST-based string sweep per M-R4 + negative-import) | **3** |
| G | 1 (importability + identity invariant per W-R2) + 2 (Pydantic-strict on 2 BaseModels per W-R1) + 1 (Texas-import-success — derivable, NOT separate K per M-R1) | **2** (importability + Pydantic-strict; Texas-import-success NOT separate K per M-R1) |
| H | 2 (snapshot shape + write_api spy) | **2** |
| I | 2 (manifest-driven + no-inline-selection) | **2** |
| **Total** | **23 collected** | **21 K-floor units** |

**Honest K-floor: 21 (well above floor 12 minimum + above target 18).** Conforms to ~1.5× K-target (target 18 / floor 12; 21/12 = 1.75× upper-band, 21/18 = 1.17× of target). The Slab 3 architectural foundation legitimately surfaces more orthogonal properties than Slab 2b per-specialist migration TEMPLATE; ~1.17-1.75× is the appropriate band for foundational stories. Per Murat M-R2 recount: AC-B's 4 rules legitimately count as 4 (NOT 1 collapsed); per M-R1 recount: AC-G's "Texas-import-success" is derivable from importability (NOT separate K). Net post-recount: honest 21 (was 19 pre-recount; +4 AC-B, -1 AC-G, -1 AC-D runtime drop = net +2).

**Regression target at T8 per Murat M-R8-3.1:** **T1 readiness gate REQUIRED to pin baseline against post-Slab-2c-close pytest collection (P passed / S skipped — copy from `sprint-status.yaml` after 2c closes).** If 2c hasn't closed when 3.1 opens, that's a **predecessor block** (per Authoring queue position); NOT paper-overable. Story-author-time placeholder: ≥562 passed / ≥7 skipped + ≥N additional from Slab 2c close (N filled at T1). +23 collected at file level for 3.1. Import-linter contracts EXPAND from 3/3 KEPT → **7/7 KEPT** (4 new Marcus rules per AC-B staged-delivery; Rule 5 facade-reachability stages to 3.4 per W-R3 + C3 precedent). Ruff clean. Sandbox-AC PASS (no live API calls; all tests via shipped Python tooling + import-linter as substrate).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness

_(Populated at T1)_

### T2–T7 Implementation Notes

_(Populated during implementation)_

### T8 Regression Evidence + Architectural Foundation Verification

_(Populated at T8 with import-linter 4/4 KEPT + 22 tests collected + facade-leak loop verdict + Texas-import-success verdict + Marcus-first cold-read fingerprint sample)_

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

_(Dual-gate per AC-L; populated at T8)_

### Operator Architectural Review (Dual-Gate Gate-2)

_(Operator confirms Marcus-first discipline + facade-leak detector adequacy per AC-L §5)_

### D12 Close Stub

_(Populated at story close per AC-3.1-L)_

### Completion Notes

_(Populated at story close)_

### File List

_(Populated at story close)_
