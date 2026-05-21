# Codex dev-story prompt — Story 7c.21a (Epic 3 Retirement + Live-Dispatch Wiring; Wave 6 strict-last cleanup; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-21a.ready-for-review.md` → Claude T11 standard.
**Wave:** 6 — strict-last cleanup story.
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-DEFERRED** until 7c.21 close (HARD predecessor per governance JSON).

---

```
Run bmad-dev-story on Story 7c.21a (Slab 7c Wave 6 strict-last cleanup; single-gate; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-21a-epic-3-retirement-live-dispatch-wiring.md`.

## Required reading (in order)

1. Story spec (4 ACs A-D; T1-T10 task structure).
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-43 + FR-7c-48 + TW-7c-4.
3. `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md §Epic 3` (in-place update target).
4. `_bmad-output/planning-artifacts/deferred-inventory.md` (find `slab-7c-live-harness-evidence` entry).
5. **Existing `run_cache_hit_harness.py` + `run_5_api_smoke.py`** — locate via `find . -name "run_cache_hit_harness.py" -o -name "run_5_api_smoke.py"` at T1 (likely under `scripts/` or top-level).
6. `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` + `epics-slab-7b-specialist-activation-eleven.md` (cross-reference targets).
7. Slab-2a Story 2a.2 close note (Irene Pass-2 LLM cache-hit-rate measurement precedent; FR54 wiring).
8. Governance JSON `7c-21a` entry.

## T1 hard checkpoints

- 7c.21 done in sprint-status (HARD predecessor block).
- 2 named harness files located + current behavior inventoried.
- `slab-7c-live-harness-evidence` entry present in deferred-inventory.md.

## Files in scope

**Modified (3 files):**
- `<path>/run_cache_hit_harness.py` — replace legacy Epic 3 stub-runners with post-Slab-7c live invocation
- `<path>/run_5_api_smoke.py` — update 5-API smoke wiring to invoke post-Slab-7c API clients
- `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md §Epic 3` — in-place retirement record + cross-references
- `_bmad-output/planning-artifacts/deferred-inventory.md` — close `slab-7c-live-harness-evidence` entry

**New (1 file):**
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (~80 LOC; verifies diff scope is bounded)

**Do NOT modify:**
- Any other production code under `app/` (live-dispatch is concentrated in 2 named harnesses)
- Any closed §section package, Wave-3/4/5 deliverable, Marcus writer, or AUDIT module
- Slab 7a + 7b epic files (cross-reference TARGETS only; do not edit)
- pyproject.toml

## Critical implementation notes

- **TW-7c-4 anti-scope-creep invariant** (binding=hard): live-dispatch wiring stays IN the 2 named harness files. Auxiliary helper extraction permitted ONLY into existing `scripts/utilities/`. NO new top-level packages. NO new application-layer modules under `app/`.
- **Cache-hit-rate harness wiring**: invoke real Marcus orchestrator + real Irene Pass-2 (FR54-aligned per Slab-2a precedent) + Gary/Vera/Quinn-R per Slab 7b body activation. Preserve cache-hit-rate measurement contract.
- **5-API smoke wiring**: invoke 5 LIVE APIs (Gamma + ElevenLabs + Canvas + Qualtrics + Panopto if cred-ready). Preserve cred-skip discipline (`@pytest.mark.llm_live` + auto-skip on placeholder per Slab-2a SF3 anti-erosion).
- **§Epic 3 in-place update**: retire-via-7a+7b+7c with cross-references; preserve mapping-checklist row (do NOT delete) for SG-2 row-floor invariant.
- **Deferred-inventory close**: mark `slab-7c-live-harness-evidence` entry CLOSED with this story's SHA + verdict reference.
- **TW-7c-4 AUDIT**: enumerate diff vs HEAD~1; verify all changes are in 2 harnesses + permitted helpers; FAIL hard if scope-creep detected.
- **K-target 1.3× ≈ 520 LOC ceiling.** Estimate ~250 LOC actual.

## PARALLEL-DISPATCH GUARDRAILS

1. **AMEND-7d-i AST-scan compliance.** N/A.
2. **Pattern-replication discipline.** Mirror Slab-2a Story 2a.2 cache-hit-rate measurement precedent.
3. **Shared-file integration ordering.** Strict-last; no parallel siblings.
4. **Pattern-parity ratchet.** N/A.
5. **Class-conformance arithmetic.** UNCHANGED.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T7)

```bash
.venv/Scripts/python.exe -m pytest tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-21a-epic-3-retirement-live-dispatch-wiring.md
.venv/Scripts/python.exe -m ruff check <2 harness paths> tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-21a.ready-for-review.md`. Include: live-dispatch evidence (2 harnesses) + §Epic 3 update evidence + deferred-inventory close evidence + TW-7c-4 AUDIT no-fire confirmation + diff-scope verification (bounded to harnesses + helpers only) + Trial-3-readiness preconditions verified post-7c.21 close.

T11: Claude standard tier (~25-40 min). Strict-last review surfaces TW-7c-4 scope-creep verification + parent-migration-epics §Epic 3 retirement record correctness.

## Boundary

HALT on: 7c.21 not done; live-dispatch logic outside 2 named harnesses (TW-7c-4 fires); §Epic 3 cross-references stale or wrong relative-paths; deferred-inventory entry not closed correctly; SG-2 row-floor invariant violated (Epic 3 row deleted instead of status-flipped).

DO NOT touch: any closed §section package, Marcus writer, AUDIT module; pyproject.toml; Slab 7a + 7b epic files.

DO NOT introduce: new application-layer modules under `app/`; new top-level packages; new tripwire-ledger entry types (TW-7c-4 schema is established).
```

---

## Operator dispatch checklist

1. ☐ 7c.21 done (Wave 6 closeout ceremony — HARD predecessor).
2. ☐ AMELIA-P2 freshness check.
3. ☐ Sandbox-AC PASS.
4. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=1 pre-author).
5. ☐ Dispatch (strict-last; solo).

## Slab 7c retrospective (post-7c.21a)

`migration-epic-slab-7c-orchestrational-tail-retrospective: optional` per governance JSON. RECOMMENDED post-7c.21a close — captures Day-3 marathon learnings + V7 v2 ratification + AMEND-7c percentage-threshold verdict + Trial-3 readiness handoff.
