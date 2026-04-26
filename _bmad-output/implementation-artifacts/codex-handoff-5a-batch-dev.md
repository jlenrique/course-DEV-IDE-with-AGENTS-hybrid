# Codex Handoff Prompt — Slab 5a Batch Development (5a.1 → 5a.2 → 5a.3 → 5a.4 → 5a.5)

**For:** Codex dev agent
**Issued:** 2026-04-26
**Branch:** `dev/langchain-langgraph-foundation`
**Anchor commit:** `34e192b` (Slab 4 close — your prior Slab-4 sequence: 42c70fb + c5f35ee + 6d8a7c1 + edcd313 + 40437bc + 34e192b plus the 4.1 commit)
**Predecessor close-state:** Slab 4 CLOSED-WITH-CONDITIONAL-M4 — M4 verdict GREEN-WITH-RIDERS per 5-agent party-mode (Winston+Amelia CONDITIONAL-GREEN; Murat+Paige+Quinn-R GREEN-WITH-RIDERS; consensus GREEN-WITH-RIDERS); riders RESOLVED in same close cycle (verdict artifact recorded; sprint-status reconciled; M2/M3/M4 explicit M5 carry-forward documented).

---

## Mission

Develop all 5 Slab 5a stories in strict sequence (5a.1 → 5a.2 → 5a.3 → 5a.4 → 5a.5). Slab 5a = **Acceptance** (Trial-Replay Regression + Head-to-Head Parity + Economics + 15-Invariant Audit Matrix + M5 Ship Decision); **M5 GO/NO-GO GATE "Migration ships"** closes at 5a.5 with **6-AGENT party-mode** acceptance verdict. **THIS IS THE CENTRAL MIGRATION ACCEPTANCE GATE.**

**Total scope:** 18pts across 5 stories. 3 dual-gate (5a.1 acceptance-shape + 5a.2 acceptance-gate + 5a.5 operator-decision SLAB CLOSING) + 2 single-gate (5a.3 + 5a.4).

---

## Hard sequencing (BINDING)

```
5a.1 done ──► 5a.2 open
              5a.2 done ──► 5a.3 open
                            5a.3 done ──► 5a.4 open
                                          5a.4 done ──► 5a.5 open ──► Slab 5a CLOSED + M5 verdict
```

**Do NOT open 5a.N+1 until 5a.N is BMAD-CLOSED.** 5a.5 is THE migration acceptance vote — it inherits ALL prior conditional milestones (M2 + M3 + M4) and resolves them in the M5 verdict path.

---

## Per-story BMAD cycle (apply uniformly; same as 2c.x + 3.x + 4.x cycles)

For each of 5a.1, 5a.2, 5a.3, 5a.4, 5a.5:

1. **Read the spec end-to-end** at `_bmad-output/implementation-artifacts/migration-5a-{N}-*.md`. Specs were authored in batch with party-mode amendments at lite-cadence; rely on T1 substrate verification + your dev judgment.
2. **Run T1 Readiness Block** verifying every pre-flight item + artifact-existence sweep + epic-doc-vs-architecture cross-check. **Halt and surface to operator if any pre-flight fails.**
3. **Implement the AC sequence** in declared order. Adhere to all RESOLVED-BY-VERIFICATION pins.
4. **Run regression suite** at T8: `.venv/Scripts/python.exe -m pytest -q --tb=short`. Baseline target: post-Slab-4-close pytest collection: **3180 passed / 22 skipped / 30 deselected / 2 xfailed** + 19 known-pre-existing failures (do NOT increase the failure count; do NOT regress the pass count).
5. **Run lint:** `.venv/Scripts/python.exe -m ruff check app/ tests/ skills/ scripts/ marcus/` (998 known pre-existing legacy debt — do NOT increase) AND `.venv/Scripts/lint-imports.exe --config pyproject.toml` (currently 9 KEPT, 0 BROKEN — must remain clean; may EXPAND if a story adds a contract).
6. **G6 single-gate self-conducted code review** per CLAUDE.md. For dual-gate stories (5a.1/5a.2/5a.5) also run dual-gate gate-2 protocol per spec.
7. **Run `bmad-code-review`** on the diff in scope per CLAUDE.md §3.
8. **D12 close protocol** per spec AC. Sprint-status flip + closeout hygiene per CLAUDE.md.
9. **Commit per story.** Suggested message format:
   ```
   feat(5a.N): <one-line summary>
   ```
10. **Run sandbox-AC validator** post-close on the next story before opening it: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-5a-{N+1}-*.md`. Should still PASS.

---

## Pre-existing test failures (NOT Slab-5a's concern unless touched)

**19 failures** confirmed by Codex 4.7 close + verified by health dashboard:

- `tests/specialists/{gary,quinn_r,tracy,vera,...}/test_*_generator_auto_emit_c3_row.py::test_temp_pyproject_baseline_is_5_rows` — generator-fixture baseline drift; tests assert temp pyproject has 5 rows but live pyproject has 18+ post-Slab-2 specialist auto-emits. Fixture needs re-baselining; NOT a 5a regression.
- `tests/test_integration_canva.py::test_local_env_template_is_not_committed` — primary-repo legacy test
- `tests/test_python_infrastructure.py::TestEnvDocumentation::test_no_env_example_in_repo` + `test_env_is_gitignored` — primary-repo legacy assertions; conflicts with the migration's `.env.example` extension (operator's choice; do not regress)
- `tests/test_orchestrator_agent_skill_path.py::test_orchestrator_agent_skill_path` — Marcus skill-path-related; pre-Slab-3-substrate-adaptation legacy
- `tests/test_structural_walk.py::test_motion_dry_run_preview_adds_marcus_motion_sequence` — primary-repo motion-preview integration

**HOWEVER:** Story 5a.1 trial-replay regression suite COVERS 100% of closed trials per AC-A. If any of the 19 failures correspond to trials the harness will replay, you must surface — Story 5a.1 may need either (a) excluding those trials from replay coverage with explicit rationale, OR (b) coordinating with operator on legacy-test cleanup BEFORE 5a.1 opens. **At 5a.1 T1, sub-task to investigate.**

---

## Story-specific landmines (READ BEFORE OPENING EACH)

### 5a.1 — Trial-Replay Regression Suite + CI Fail-Loud Mode (5pt dual acceptance-shape; OPENING STORY)

- **Decision #1 bounded scope:** `app/replay/{regression,discovery}.py` + `tests/trial_replay/` 100% coverage of Slab 2/3/4 closed trials + ReplayError discriminated by drift-kind + D1 sanctum variance policy + GHA workflow nightly cron + per-trial ≤15min wall-clock budget.
- **Decision #2 closed-trial discovery mechanism:** `list_closed_trials()` walks LangGraph checkpointer storage (Postgres tables OR `state/trials/` filesystem per Slab-1 substrate); verify path at T1.
- **Decision #3 ReplayError discriminated:** `PackHashDriftError` + `SanctumFingerprintDriftError` + `ManifestSnapshotDriftError`; single `ReplayError` base.
- **PRE-FLIGHT INVESTIGATION:** verify whether the 19 pre-existing test failures correspond to closed trials in checkpointer storage; if so, halt + surface for operator decision (exclude OR fix legacy first).
- **Substrate path verification:** `app/replay/` does NOT exist; `tests/trial_replay/` does NOT exist (verify; epic 5a.1 says "empty"); GHA `.github/workflows/trial-replay.yml` does NOT exist.

### 5a.2 — Head-to-Head Parity Trial vs Primary (5pt dual acceptance-gate)

- **Decision #1 bounded scope:** operator-driven E2E producing new clone trial `C1-M1-PRES-<clone-date>` against same input as primary frozen-reference trial; side-by-side artifact comparison via `app/replay/parity_comparison.py` two-tier scoring (TIER 1 file-presence ≥80% + TIER 2 structural-match ≥60% per Murat M-R2-2c.1 inheritance); 5-agent party-mode parity verdict.
- **Decision #2 primary baseline source:** mine from `upstream/master @ 3ed7c56` frozen reference per `MEMORY.md::project_upstream_severance` (NOT live forward-port). Operator provides path to primary trial artifact set; if absent, AC-A halts pre-trial.
- **Decision #4 5-agent party-mode roster pinned:** Winston + Murat + Paige + Quinn-R + Amelia (per 2c.3 + 3.6 + 4.7 inheritance pattern). Verbatim recording at `5a-2-parity-verdict.md`.
- **Operator-driven AC-A:** trial-run is E2E + operator-supplied corpus; evidence captured in Dev Agent Record. No automated test for AC-A (operator-paste pattern per 3.6 AC-A precedent).

### 5a.3 — Economics + ≥50% Cost-Reduction Bar (3pt single)

- **Decision #1 bounded scope:** `app/runtime/economics.py::measure_trial_cost(trial_id) -> TrialEconomicsReport` + `compute_reduction_percentage(baseline, new)` + `cache_hit_rate_per_node(trial_id)` per FR54 substitute metric + TrialEconomicsReport Pydantic v2 strict four-file-lockstep + dashboard CLI minimal (full dashboard 5b.2).
- **Decision #2 ≥80% cache-hit-rate median bar:** if median <0.80, prefix-stability audit triggers; emit `_bmad-output/economics-baselines/prefix-stability-audit-<date>.md`.
- **Decision #3 ≥50% reduction bar enforcement:** if <0.50, M5 verdict at 5a.5 defaults to Revise; <0.30 → Revise/Rollback per PRD §Cost Projection.
- **Operator-supplied baseline:** `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` must be present at T1; if absent, halt pre-measurement.
- **CLI bridge home (per Slab-3 substrate adaptation):** `marcus/cli/` (canonical), NOT `app/marcus/cli/`. `marcus.cli economics report` subcommand.

### 5a.4 — 15-Invariant Audit Matrix + FR64 Catalog Final (3pt single)

- **HARD INHERITANCE BINDING:** CREATES `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` long-deferred from 2c.3 A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL.
- **Stub absorption per Decision #3:** read `slab-2c-wondercraft-invariant-stub.md` (per 2c.3 AC-D) + `slab-3-marcus-invariant-stub.md` (per 3.6 AC-G) + per-slab D12 close-stubs across Slabs 1-5a; map each entry to one of 15 invariants. **NEW for Slab 4:** absorb 4.x close-stubs covering invariants from 4.1 (lockstep deterministic-neck) + 4.2 (Cora lane sep) + 4.3 (party-mode-as-interrupt) + 4.4 (ledger emit/idempotent) + 4.5 (frozen-graph reproducibility) + 4.6 (sanctum invalidation hook).
- **Decision #2 matrix table format:** 15 rows × N columns (`invariant_name | slab_of_introduction | slab_of_close | named_files | named_tests | preservation_evidence | status enum {PRESERVED|DEFERRED|VIOLATED}`); conditional-states from M2/M3/M4 noted in `preservation_evidence` column.
- **Decision #4 FR64 catalog final:** anti-patterns catalog at A1-A14+ (verify count post-2c.4 + 3.6 + 4.7 cycle-complete annotations); add `"Slab 1+2+3+4+5a harvest cycle complete"` annotation per Decision #4 wording. **Harvest-gate verdicts NOT preempted at story-author per Mary harvest-gate.**
- **Migration-guide cross-references:** §1 OR §12 appendix added per AC-D.

### 5a.5 — M5 Ship Decision + Slab Close (2pt dual operator_acceptance_gate; SLAB CLOSING + THE CENTRAL MIGRATION ACCEPTANCE GATE)

- **HARD PREDECESSORS:** 5a.1 + 5a.2 + 5a.3 + 5a.4 ALL `done` per sprint-status.yaml.
- **6-AGENT party-mode roster pinned (HARD; NEW expansion from 5-agent pattern):** Winston + Murat + Paige + Quinn-R + Amelia + **Dr. Quinn for strategic framing** per epic 5a.5 binding. Dr. Quinn's voice is novel at this gate.
- **Decision #2 6-agent prompt (BINDING; enumerates all 3 inherited conditional states):**
  ```
  M5 ship/iterate/rollback verdict review for migration LangChain/LangGraph
  (Slabs 1-5a complete). Full evidence: 5a.1 trial-replay regression + 5a.2
  head-to-head parity verdict + 5a.3 economics ≥50% reduction + 5a.4 15-invariant
  audit matrix + FR64 catalog final.
  Inherited conditional states: M2=CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM
  (Wondercraft AC-D-OP); M3=CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM
  (Texas AC-B-OP M1-M5); M4=GREEN-WITH-RIDERS (M2/M3 explicit M5 carry-forward).
  Verdict (one of 6 per-agent enum): SHIP / ITERATE / ROLLBACK / SHIP-WITH-RIDERS
  / SHIP-CONDITIONAL / ABSTAIN.
  Roster fixed at 6 (Winston + Murat + Paige + Quinn-R + Amelia + Dr. Quinn for
  strategic framing); do not substitute.
  ```
- **Decision #3 verdict-path operational consequences (per epic 5a.5 + FR60/FR61/FR62):** see spec for full detail per verdict.
- **NEW top-level `migration-master-status` enum** at sprint-status.yaml: `shipped` | `iterate-pending` | `rolled-back`. Define at this story.
- **Decision #4 retrospective format:** mirrors `slab-4-retrospective.md` (which mirrors slab-3 + slab-2c) — 4 §-headers (Pre-Audit Bundle / Slab Outcomes / Next-Slab Preparation / Slab 5b Handoff [optional if cuttable]).
- **AC-C inherited-conditional resolution:** each conditional resolved pre-vote (operator addendum landed) OR carried forward as SHIP-CONDITIONAL with named window OR escalated to BLOCK; record in `m5-decision.md` §"Inherited Conditional States" before convening party-mode.
- **CLI bridge home (per Slab-3 substrate adaptation):** `marcus/cli/` (canonical), NOT `app/marcus/cli/`. Any new CLI subcommands land at `marcus/cli/`.

---

## Substrate truths inherited from prior Slabs (READ BEFORE OPENING ANY 5a.x STORY)

- **Marcus canonical home:** `marcus/` (NOT `app/marcus/` which is Slab-1 namespace stub) per Slab-3 substrate-aware adaptation. Includes `marcus/{intake/pre_packet.py, orchestrator/{write_api,supervisor,routing,dispatch,fanout,hil_intake,learning_event_wiring,loop,maya_walkthrough,stub_dials,trial_smoke_harness,workflow_runner,m3_trial}.py, facade.py, dispatch/contract.py, lesson_plan/, cli/}`.
- **OperatorVerdict canonical home:** `app/models/state/operator_verdict.py` per architecture D3 BINDING (NOT `app/gates/verdict.py`).
- **RunState canonical home:** `app/models/state/run_state.py` (NOT `app/state/`).
- **Pipeline manifest:** `state/config/pipeline-manifest.yaml` (NOT `run-manifest.yaml`); shape is `nodes[*].specialist_id` + `edges[*].dispatch_envelope` (NOT `dispatch_target`).
- **Marcus-envelope baseline:** `tests/fixtures/marcus/baseline_envelope/2026-04-26/{envelope.json, BASELINE_METADATA.md}` per 3.6 W-R7. 5a.1 may consume for replay-comparison.
- **Frozen-graph v42:** `runtime/graphs/v42/{manifest-snapshot, dev-graph-manifest-snapshot, dispatch-registry-snapshot}.yaml + pack-version.txt + compiled-graph-digest.txt` per 4.5 close.
- **Dispatch-registry _status=interim:** per 2b.15 substrate; M5 reconciles per `slab-3-m5-dispatch-registry-swap` deferred-inventory entry — **5a.5 ship verdict triggers the swap if SHIP path activates**.
- **App tree:** `app/{cora, gates, ledger, http, marcus (Slab-1 stub), mcp_server, models, replay (Slab 5a.1 ships), runtime, specialists}/` all populated post-Slab-4.

---

## Conditional-state resolution checklist (BEFORE 5a.5 vote)

Per `docs/operator/conditional-gate-addendum-playbook.md` — operator addresses each conditional state pre-5a.5 OR explicitly carries forward as SHIP-CONDITIONAL:

- [ ] **M2** (Wondercraft AC-D-OP): operator runs live `pytest tests/specialists/wanda/test_wanda_live_api_artifact.py --run-live`; pastes addendum to `slab-2c-m2-acceptance-verdict.md`. If unresolved, M2 carries to SHIP-CONDITIONAL with named window.
- [ ] **M3** (Texas AC-B-OP M1-M5): operator runs `scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py --directive ... --bundle-dir ...`; pastes M1-M5 evidence to `slab-3-m3-acceptance-verdict.md`. If unresolved, M3 carries to SHIP-CONDITIONAL.
- [ ] **M4** (carries M2+M3 forward): no NEW M4 condition; M4 is GREEN-WITH-RIDERS with riders RESOLVED at 4.7 close. M4's role is the explicit M2/M3 carry-forward documentation.

**5a.5 dev opens regardless of M2/M3 resolution state** — but the verdict path differs:
- M2 + M3 + M4 all resolved pre-vote → **SHIP** path possible
- M2 OR M3 unresolved → **SHIP-CONDITIONAL** with named window per Decision #3
- 3+ riders surfaced at vote → **SHIP-WITH-RIDERS**
- Behavioral gap surfaced (cost <30%, parity score <60%, invariant VIOLATED) → **ITERATE** or **ROLLBACK**

---

## Governance non-negotiables (recap)

- **Sandbox-AC discipline (CLAUDE.md):** dev-agent ACs MUST verify via shipped Python deps + `pytest.skip(...)` on missing service. Run `validate_migration_story_sandbox_acs.py` before opening any story.
- **Gate-mode pinned at governance JSON** (`docs/dev-guide/migration-story-governance.json:72-76`). DO NOT relitigate.
- **Live API discipline:** N/A for Slab 5a (no live API calls in 5a.1-5a.4 scope; 5a.2 head-to-head trial may consume live LLM if operator chooses but is operator-discretion).
- **Hybrid working tree is sole input surface:** upstream/master severed at `3ed7c56` 2026-04-24.
- **Closeout hygiene:** every story close updates `sprint-status.yaml` first, then `next-session-start-here.md`.
- **Deferred inventory governance:** every new follow-on goes to `_bmad-output/planning-artifacts/deferred-inventory.md` (current count: 59 entries); 5a.5 retrospective enforces per-entry consultation verdicts per Murat M-R5+P-R1 + Paige P-R1 inheritance from 2c.4.
- **Substrate-aware adaptation discipline (Slab-3 lesson):** if T1 readiness reveals substrate mismatches against spec assumptions, HALT + apply substrate-aware adaptation pattern. Do NOT force-fit code against bad spec assumptions.
- **No commits without per-story BMAD-CLOSE; no force-push, no `--no-verify`, no `--amend` published commits.**

---

## What "done" means for the batch

- All 5 stories show `done` in sprint-status.yaml.
- `migration-epic-5a-acceptance: done` (with trailing comment naming verdict per 2c.4 AC-E enum-clarification pattern).
- M5 milestone: `SHIP` OR `SHIP-WITH-RIDERS` OR `SHIP-CONDITIONAL` OR `ITERATE` OR `ROLLBACK` (recorded in `m5-decision.md`).
- `migration-master-status: shipped` OR `iterate-pending` OR `rolled-back` per verdict (NEW top-level enum at sprint-status.yaml).
- `slab-5a-retrospective.md` exists with 4 canonical §-headers + per-entry deferred-inventory verdicts.
- `15-invariant-audit-matrix.md` CREATED at 5a.4 (long-deferred since 2c.3 BLOCKER B1).
- Anti-patterns catalog migration-complete annotation per 5a.5 AC-E.
- TrialEconomicsReport four-file-lockstep + Postgres economics baseline storage (5a.3).
- `app/replay/` populated with regression + discovery + parity_comparison (5a.1 + 5a.2).
- `_bmad-output/implementation-artifacts/{m5-decision, m5-ship-riders (if SHIP-WITH-RIDERS), 5a-2-parity-evidence-<date>, 5a-2-parity-verdict, slab-5a-retrospective}.md` all present.
- `next-session-start-here.md` reflects M5 verdict + Slab 5b status (open per SHIP; defer per ITERATE/ROLLBACK).
- Regression suite: 3180 passed baseline preserved; 19 known-pre-existing failures NOT increased; collection errors stay at 0.
- Import-linter contracts: 9/9 KEPT baseline preserved; may EXPAND if a 5a story adds a contract (unlikely per spec scope).
- One commit per story-close (5 commits total).

---

## Escalation triggers (HALT and surface to operator)

- T1 pre-flight fails on any story (predecessor not `done`, anchor file missing, etc.).
- Sandbox-AC validator FAILS (substrate state has drifted since authoring).
- 5a.1 trial-replay coverage CONFLICTS with the 19 pre-existing test failures (some closed trials may need exclusion-with-rationale).
- 5a.2 primary frozen-reference trial baseline cannot be located OR has drifted from `3ed7c56` snapshot.
- 5a.3 cost reduction <30% (PRD §Cost Projection auto-defaults to Revise/Rollback).
- 5a.3 cache-hit-rate median <80% (triggers prefix-stability audit; remediation may be needed before 5a.5 vote).
- 5a.4 invariant audit reveals VIOLATED status on any of 15 invariants (cannot CLOSE 5a as GREEN; either remediate OR carry to ITERATE).
- 5a.5 6-agent party-mode returns ITERATE or ROLLBACK verdict — do NOT proceed to commit; surface for operator strategic decision.
- 5a.5 6-agent party-mode encounters Dr. Quinn skill-invocation issue (NEW persona at this gate — Dr. Quinn is `bmad-agent-dr-quinn` or similar; verify skill availability at T1).
- Any new architectural decision surfaces requiring party-mode consensus.

---

## Reference anchors

- Spec files: `_bmad-output/implementation-artifacts/migration-5a-{1..5}-*.md` (commit `113b949`)
- Sprint status: `_bmad-output/implementation-artifacts/sprint-status.yaml` (Slab 5a block at line ~838+)
- Governance JSON: `docs/dev-guide/migration-story-governance.json:72-76` (5a-1 through 5a-5 gate-modes pinned)
- Architecture doc: `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` (FR49-FR57 + FR63 + FR64 + D1 sanctum variance + D8 frozen-graph ceremony)
- Epic 5a: `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 5a lines 1248-1377
- PRD §Cost Projection (FR55-FR56 + ≥50% bar): `_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md` §Cost Projection
- PRD §FR60/FR61/FR62 (ship/iterate/rollback paths): `_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md`
- Anti-patterns: `docs/dev-guide/specialist-anti-patterns.md` (post-Slab-4 close state; A1-A14+ per cycles)
- Conditional-gate addendum playbook: `docs/operator/conditional-gate-addendum-playbook.md`
- Post-M5 runbook (per-verdict-path operations): `docs/operator/post-m5-runbook.md`
- Trial-run runbook: `docs/operator/trial-run-runbook.md`
- 2a.4 deferred-inventory binding (Texas AC-B-OP — operator-window pending): `_bmad-output/planning-artifacts/deferred-inventory.md` §`2a.4-followon-ac-b-op-live-retrieval`
- M2 conditional state: `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`
- M3 conditional state: `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md`
- M4 verdict + riders RESOLVED: `_bmad-output/implementation-artifacts/slab-4-m4-acceptance-verdict.md`
- Slab close artifacts (precedent for 5a.5): `_bmad-output/implementation-artifacts/{slab-2c, slab-3, slab-4}-retrospective.md`
- 2c.x + 3.x + 4.x Codex prior-batch precedents: `_bmad-output/implementation-artifacts/codex-handoff-{2c, 3, 4}-batch-dev.md`
- Marcus canonical home: `marcus/` (Story 30-1 lesson-planner + Slab-3 additive marcus/{dispatch/contract.py + orchestrator/{supervisor,routing}.py})
- Slab-3 substrate-aware adaptation precedent (READ if 5a.x T1 surfaces substrate mismatches): `_bmad-output/implementation-artifacts/migration-3-1-marcus-intake-orchestrator-facade-split.md` §"SUBSTRATE-AWARE ADAPTATION" header

Proceed.
