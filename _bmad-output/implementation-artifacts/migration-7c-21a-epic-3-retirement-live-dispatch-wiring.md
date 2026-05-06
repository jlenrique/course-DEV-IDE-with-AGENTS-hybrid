# Migration Story 7c.21a: Epic 3 Retirement + Live-Dispatch Wiring (FR-7c-48 + FR-7c-43)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1 per governance JSON; **HARD BLOCKER: 7c.21 is in Wave-6 backlog and MUST close before 7c.21a dispatches** — per governance JSON `prerequisite_stories: ["7c-21"]`. Spec pre-authored to capture intent; dispatch holds until 7c.21 closes.)*
**Sprint key:** `migration-7c-21a-epic-3-retirement-live-dispatch-wiring`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 1
**K-target:** 1.3×
**Estimated LOC:** ~250 (live-dispatch authoring in `run_cache_hit_harness.py` ~80 + `run_5_api_smoke.py` ~80 + epics-langchain-langgraph-migration.md §Epic 3 in-place edit ~30 + tests ~60)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** standard (per governance JSON entry `7c-21a`)
**Lookahead-tier:** 1
**files_touched:** ~3 modified + 1 new (test) — 2 harness files modified for live-dispatch + parent migration epics §Epic 3 update + 1 new test
**Tripwire ownership:** TW-7c-4 (live-dispatch scope-creep detection)

---

## Story

As the dev-agent,
I want to author live-dispatch in `run_cache_hit_harness.py` + `run_5_api_smoke.py` + update `epics-langchain-langgraph-migration.md` §Epic 3 in-place to record the 7a+7b+7c replacement,
So that the `slab-7c-live-harness-evidence` deferred-inventory entry closes + original Epic 3 retirement is documented in the parent migration epics file with cross-references to the three closure artifacts.

This is a **Wave 6 strict-last cleanup story** (peeled per John A6 — substrate-touching change distinct from slab-close ceremony 7c.21). Live-dispatch authoring is concentrated in the named harness; **TW-7c-4 (live-dispatch scope-creep) must NOT trip** — keep changes inside the named files only.

---

## Predecessor / Dependency Context

- **7c.21** (HARD PREDECESSOR per governance JSON; in Wave-6 backlog): Slab 7c integration parity suite + closeout ceremony. **HARD DISPATCH-BLOCKER**: 7c.21a cannot dispatch until 7c.21 CLOSED — the slab-close ceremony establishes Trial-3 readiness preconditions that the live-dispatch authoring will reference.
- **`run_cache_hit_harness.py`** (existing): cache-hit-rate harness; current behavior measures cache-hit-rate against shipped specialists (e.g., Irene Pass-2 at FR54). 7c.21a authors LIVE-DISPATCH wiring against the post-Slab-7c substrate.
- **`run_5_api_smoke.py`** (existing): 5-API smoke harness. 7c.21a authors LIVE-DISPATCH wiring.
- **`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3** (existing): the parent migration epics file. 7c.21a updates §Epic 3 in-place to record the 7a+7b+7c replacement with cross-references to:
  - `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md`
  - `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`
  - `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md`
- **`_bmad-output/planning-artifacts/deferred-inventory.md`** entry `slab-7c-live-harness-evidence`: the deferred-inventory entry that THIS STORY closes per FR-7c-43.
- **TW-7c-4 (live-dispatch scope-creep)**: tripwire owned by THIS STORY. Scope-creep = live-dispatch wiring outside the 2 named harness files OR live-dispatch logic in non-harness modules. AUDIT at T9 verifies no scope creep.

---

## Acceptance Criteria

### AC-7c.21a-A — Live-dispatch authoring in named harnesses (FR-7c-48)

**Given** the existing `run_cache_hit_harness.py` + `run_5_api_smoke.py` (likely under `scripts/` or a top-level path; T1 locates exact paths)
**When** the dev-agent authors live-dispatch wiring in BOTH harnesses
**Then**:
1. `run_cache_hit_harness.py` invokes the post-Slab-7c live LangChain/LangGraph specialist substrate (e.g., real Marcus orchestrator + real Irene Pass-2 + real Gary/Vera/Quinn-R per Slab 7b body activation) — NOT the legacy Epic 3 stub-runners.
2. `run_5_api_smoke.py` invokes the 5 LIVE APIs (Gamma + ElevenLabs + Canvas + Qualtrics + Panopto if cred-ready) using the post-Slab-7c API client substrate.
3. **TW-7c-4 anti-scope-creep invariant** (binding=hard): live-dispatch wiring stays IN the named 2 files. Auxiliary helper extraction is permitted ONLY into existing `scripts/utilities/` (no new top-level packages; no new application-layer modules).

### AC-7c.21a-B — Parent migration epics §Epic 3 in-place update (FR-7c-43)

**When** the dev-agent updates `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3 in-place
**Then**:
1. The §Epic 3 section records the 7a+7b+7c replacement: original Epic 3 stories 3.1–3.11 are retired in-place; the substrate is now delivered by Slab 7a (inter-gate orchestration) + Slab 7b (specialist activation) + Slab 7c (orchestrational tail).
2. Cross-references are inline as relative paths to the three closure artifacts:
   - `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md`
   - `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`
   - `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md`
3. SG-2 mapping-checklist row for Epic 3: status flips to `retired-via-7a+7b+7c`. Preserve the row (do NOT delete) to maintain SG-2 row-floor invariant per Slab-7c retrospective ratification.

### AC-7c.21a-C — Deferred-inventory entry closure (FR-7c-43)

**Given** `_bmad-output/planning-artifacts/deferred-inventory.md` entry `slab-7c-live-harness-evidence`
**When** the dev-agent closes the entry
**Then** the deferred-inventory entry is marked `CLOSED 2026-05-XX via 7c.21a` with cross-reference to this story's commit SHA + verdict file.

### AC-7c.21a-D — TW-7c-4 detection AUDIT

**Given** the AC-A binding=hard scope-creep invariant
**When** the dev-agent authors `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`
**Then** the AUDIT verifies:
1. Live-dispatch logic is concentrated in the 2 named harness files + permitted auxiliary helpers in `scripts/utilities/`.
2. NO new application-layer modules under `app/` were authored as part of 7c.21a's diff.
3. NO new top-level packages were created.
4. AUDIT raises a TW-7c-4 fire signal if scope-creep is detected (test FAILS hard); otherwise PASSES with `fired: false` recorded inline (no ledger entry needed for clean AUDITs).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.21 done in sprint-status (HARD predecessor block).
  - [ ] T1.2 Locate `run_cache_hit_harness.py` + `run_5_api_smoke.py` in the repo (likely under `scripts/`; T1 verifies exact paths).
  - [ ] T1.3 Read `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3 for in-place update target.
  - [ ] T1.4 Read `_bmad-output/planning-artifacts/deferred-inventory.md` for `slab-7c-live-harness-evidence` entry shape.
  - [ ] T1.5 Inventory current live-dispatch wiring (if any) in the 2 named harnesses; identify what needs replacement vs new.
  - [ ] T1.6 Refresh broad-regression baseline.

- [ ] **T2 — Author live-dispatch in run_cache_hit_harness.py (AC-A)**
  - [ ] T2.1 Replace legacy Epic 3 stub-runners with post-Slab-7c live invocation (real Marcus orchestrator + specialist substrate).
  - [ ] T2.2 Preserve existing cache-hit-rate measurement contract (FR54-aligned; per Slab-2a precedent).

- [ ] **T3 — Author live-dispatch in run_5_api_smoke.py (AC-A)**
  - [ ] T3.1 Update 5-API smoke wiring to invoke post-Slab-7c API clients.
  - [ ] T3.2 Preserve cred-skip discipline (Panopto auto-skip on placeholder per existing pattern).

- [ ] **T4 — Update parent migration epics §Epic 3 (AC-B)**
  - [ ] T4.1 In-place edit `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 3 with retirement record + cross-references.
  - [ ] T4.2 Preserve mapping-checklist row for Epic 3 with status `retired-via-7a+7b+7c`.

- [ ] **T5 — Close deferred-inventory entry (AC-C)**
  - [ ] T5.1 Mark `slab-7c-live-harness-evidence` CLOSED in `deferred-inventory.md` with this story's SHA + verdict reference.

- [ ] **T6 — Author TW-7c-4 scope-creep AUDIT (AC-D)**
  - [ ] T6.1 Author `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` — verifies diff scope is bounded to 2 harnesses + permitted helpers.

- [ ] **T7 — Verification battery (R-tier R2; T11-tier standard)**
  - [ ] T7.1 Focused: `pytest tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -p no:randomly -q --tb=short` PASS.
  - [ ] T7.2 Cache-hit-rate live-harness smoke (if tractable in CI; mark `@pytest.mark.llm_live` to gate on real-key per Slab-2a precedent).
  - [ ] T7.3 5-API smoke (if tractable; mark live-only).
  - [ ] T7.4 Non-regression sweep: full Slab-7c test surface PASS UNCHANGED.
  - [ ] T7.5 R2 broad: delta ≤ 0.
  - [ ] T7.6 Class-conformance UNCHANGED.
  - [ ] T7.7 Lint-imports: 12 KEPT UNCHANGED.
  - [ ] T7.8 Sandbox-AC: PASS.
  - [ ] T7.9 Ruff: clean on edited files.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-21a.ready-for-review.md` with: live-dispatch evidence (2 harnesses) + §Epic 3 in-place update evidence + deferred-inventory close evidence + TW-7c-4 AUDIT no-fire confirmation + diff-scope verification (bounded to harnesses + helpers only).

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-43 + FR-7c-48 + TW-7c-4.
3. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.21a`.
4. `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md §Epic 3` (in-place update target).
5. `_bmad-output/planning-artifacts/deferred-inventory.md` (find `slab-7c-live-harness-evidence`).
6. Existing `run_cache_hit_harness.py` + `run_5_api_smoke.py` (locate via `find . -name "run_cache_hit_harness.py" -o -name "run_5_api_smoke.py"` at T1; likely under `scripts/` or top-level).
7. `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` + `epics-slab-7b-specialist-activation-eleven.md` (cross-reference targets).
8. Slab-2a `Story 2a.2` close note (Irene Pass-2 LLM cache-hit-rate measurement precedent; FR54 wiring reference).
9. Governance JSON `7c-21a` entry: gate_mode=single-gate, K=1.3×, t11_tier=standard, lookahead_tier=1, prerequisite=["7c-21"], tripwire_ownership=["TW-7c-4"].

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-DEFERRED** until 7c.21 close. Per governance JSON, `prerequisite_stories: ["7c-21"]` (binding=hard) — 7c.21 is the slab-close ceremony with TW-7c-6 50-run zero-flake parity baseline + Trial-3 readiness AC + retrospective deliverables. 7c.21a is the strict-last cleanup story.

**Lookahead-tier=1 rationale (per governance):** governance pins this story at lookahead_tier=1 despite the strict-last position, reflecting that the live-dispatch authoring + Epic 3 retirement docs are well-understood + scoped; the deferred-tier choice is purely about predecessor-chain depth (7c.21 must close first).

**Parallel-dispatch fit:** N/A — strict-last; 7c.21a dispatches solo after 7c.21 closes.

**Slab 7c retrospective**: optional but RECOMMENDED post-7c.21a. Per governance JSON `migration-epic-slab-7c-orchestrational-tail-retrospective: optional`.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T7)

### Completion Notes List

(populated by Codex at T10; include T1 path-discovery for 2 harnesses + diff-scope evidence + TW-7c-4 no-fire confirmation)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-6 strict-last dispatch post-7c.21 close.
