# Codex dev-story prompt — Story 7c.19 (§09 Four-Artifact Lock Semantics; Marcus-side enforcement; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-19.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 5 — slot 3 (Wave-5 third story; first non-HIL surface in Wave 5).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-DEFERRED** until 7c.17a + 7c.17b close (Wave 4 close-batch).

**Parallel-dispatch context:** Path-disjoint at module level with 7c.18a + 7c.18b (different surfaces). Does NOT touch `pyproject.toml` C6 modules list (Marcus-side enforcement; no HIL surface). **Lite-batchable T11** with 7c.18a/b reviews per AMEND-V3 if ALL three close concurrently.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

This story has a small file footprint (2 new files: lock module + test file). Sub-agent splitting is OPTIONAL — solo dispatch is reasonable for K=1.2× / 1pt scope. If sub-agents are spawned:

- 1 subagent: AC-A + AC-B Marcus-side function + Pydantic-v2 result models
- 1 subagent: AC-C tripwire-ledger entry helper + AC-D test file
- Main thread: T4 verification battery + T10 dropbox

**Shared-file edits — DO NOT modify:**
- `app/marcus/orchestrator/gate_runner.py` (architectural precedent reference; READ-ONLY)
- `app/gates/errors.py` (canonical GateError; import only)
- `app/marcus/orchestrator/writers/` (7c.17a + 7c.17b deliverables; READ-ONLY references)
- `app/specialists/{kira,vera,quinn_r}/` (Slab 7b body deliverables; READ-ONLY references)
- `pyproject.toml` (NO C6 edit — Marcus-side enforcement; lock module inherits M1-M4 by construction)
- `tests/marcus/orchestrator/writers/` (7c.17a + 7c.17b test files; READ-ONLY)
- All closed §section packages — read-only

---

```
Run bmad-dev-story on Story 7c.19 (Slab 7c Wave 5 slot 3; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-19-section-09-four-artifact-lock-semantics.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 predecessor; `GarySlideContent` shape).
3. `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` Appendix A (FR-7c-50 audit-chain integrity invariants — append-only + monotonic-timestamp + parent-trace-linkage).
4. **`app/marcus/orchestrator/gate_runner.py`** (architectural precedent — shared gate-runner guardrails + `_append_jsonl` pattern + `MarcusDualityBoundaryError` style; READ-ONLY).
5. **`app/gates/errors.py`** (GateError signature + import location; READ-ONLY).
6. **`app/gates/resume_api.py`** (4× GateError-raise pattern reference; structured failure context style; READ-ONLY).
7. **`app/marcus/orchestrator/production_runner.py`** (2× GateError-raise + `MissingUpstreamContributionError` + `GateBypassError` precedents; READ-ONLY).
8. **`app/marcus/orchestrator/writers/slide_content.py`** (7c.17a; `GarySlideContent`).
9. **`app/specialists/kira/`** + **`app/specialists/vera/`** + **`app/specialists/quinn_r/`** (Slab 7b body deliverables — identify Pydantic-v2 models for Kira motion-plan + Vera fidelity-verdict + Quinn-R QA-verdict; T1 decision documented at T10).
10. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening — apply if any schema regen happens; otherwise N/A).
12. `pyproject.toml::tool.importlinter` (M1-M4 contracts; confirm coverage scope).
13. Governance JSON `7c-19` entry: gate_mode=single-gate, K=1.2×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].

## T1 hard checkpoints

- 7c.17a + 7c.17b done (Wave-4 close-batch landed).
- `app.gates.errors.GateError` importable.
- `app.marcus.orchestrator.writers.slide_content.GarySlideContent` importable (7c.17a deliverable).
- T1 decision: locate Pydantic-v2 models for Kira motion-plan + Vera fidelity-verdict + Quinn-R QA-verdict under `app/specialists/{kira,vera,quinn_r}/`. If located, import for structural validation. If absent, document the gap at T10 + use a minimal local model that captures the lock-relevant fields (`plan_unit_id` + producer-specific shape).
- Class-conformance baseline: record observed (UNCHANGED expected — Marcus enforcement is NOT an HIL surface; no parity_contract).
- Broad-regression baseline: re-run.

## Files in scope

**New (2 files):**
- `app/marcus/orchestrator/section_09_lock.py` (~200 LOC; `enforce_section_09_lock` function + `Section09LockArtifactPaths` + `Section09LockArtifactRef` + `Section09LockResult` Pydantic-v2 models + `_append_section_09_tripwire` helper mirroring `gate_runner.py:_append_jsonl`)
- `tests/marcus/orchestrator/test_section_09_lock.py` (~200 LOC; happy + 4 absent + 3+ inconsistency paths + determinism + schema-hash STABLE pin)

**Conditionally new (1 file; create only if not already present from 7c.17a/17b):**
- `tests/marcus/orchestrator/__init__.py` (empty namespace; check first via `git ls-files` or filesystem)

**Modified (0 files):**
- (No existing-file edits required.)

**Do NOT modify:**
- `app/marcus/orchestrator/gate_runner.py` (architectural reference; READ-ONLY)
- `app/gates/errors.py` (READ-ONLY; import GateError)
- `app/marcus/orchestrator/writers/` (7c.17a + 7c.17b; READ-ONLY)
- `app/specialists/` (READ-ONLY references)
- `pyproject.toml` (NO contract edit)
- All closed §section packages
- 7c.18a / 7c.18b deliverables (sibling stories; if they close concurrently, READ-ONLY)

## Critical implementation notes

- **GateError import:** `from app.gates.errors import GateError`. Mirror existing pattern from `app/gates/resume_api.py` + `app/marcus/orchestrator/production_runner.py`.
- **Pydantic-v2 ConfigDict discipline:** all 3 models declare `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Closed-enum Literal types on every enumerated field. Strip-then-non-empty validators on all `str` fields.
- **`schema_version: int = 1`** on `Section09LockResult` per FR-7c-51 schema_version discipline.
- **Closed enum on `artifact_kind`:** `Literal["gary-slide-content", "kira-motion-plan", "vera-fidelity-verdict", "quinn-r-qa-verdict"]`. Widening requires party-mode consensus (do NOT widen to support new artifact kinds without ratification).
- **`lock_status: Literal["locked"]`** on success-only — failure raises GateError, not returns. Do NOT add `Literal["unlocked", "failed"]` variants; the API contract is "lock or raise."
- **Plan-unit-id consistency check:** ALL FOUR artifacts MUST reference the same `plan_unit_id`. Mismatch raises GateError. Implementation: extract `plan_unit_id` from each artifact (via the producer's Pydantic-v2 model OR — if a producer model is unavailable — minimal local-model parse), then `len({four_plan_unit_ids}) == 1` invariant check.
- **Tripwire-ledger entry shape:**
  ```json
  {"event": "section_09_lock_failure", "plan_unit_id": "<id>", "failure_kind": "absent|parse_error|plan_unit_id_mismatch|validation_error", "failed_artifact_kind": "<one-of-4-kinds>", "fired_at": "<iso8601-tz-aware>", "schema_version": 1}
  ```
  Append via `Path(tripwire_log_path).open("a", encoding="utf-8", newline="\n").write(json.dumps(entry, sort_keys=True) + "\n")`. Mirror `gate_runner.py:_append_jsonl` style. Default tripwire_log_path: `_artifacts/section_09_lock_tripwire.jsonl` (if directory does not exist, mkdir parents=True).
- **Test determinism:** tripwire-ledger writes are byte-deterministic across re-invocations with identical input. Test asserts via `tmp_path` fixture + sha256-stable bytes assertion.
- **Schema-hash STABLE pin:** `assert hashlib.sha256(json.dumps(Section09LockResult.model_json_schema(), sort_keys=True).encode()).hexdigest() == "<frozen-literal>"`. Codex generates the literal at T2-completion + freezes in test.
- **No parity_contract decorator** — this is Marcus-side enforcement, NOT an HIL surface. Class-conformance count is UNCHANGED.
- **No pyproject.toml edit** — Marcus M1-M4 contracts already in place; new module inherits.
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~400 LOC actual.
- **T11 lite tier:** AC count = 5 + Marcus-orchestrator-side enforcement function + new Pydantic-v2 result model + sibling tests + no parity_contract DSL touch + no HIL surface + no C6 modules list edit + Codex T10 self-review clean + single-gate.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch)

1. **AMEND-7d-i AST-scan compliance.** N/A for Marcus-side enforcement (no shape-pin in `tests/parity/test_decision_card_*` scope; no parity_contract).
2. **Pattern-replication discipline.** Read `gate_runner.py` for shared-guardrail-module style + `_append_jsonl` pattern. Read `app/gates/resume_api.py` for GateError-raise pattern. Read 7c.17a's `slide_content.py` for `GarySlideContent` model usage.
3. **Shared-file integration ordering.** N/A — no shared file edits.
4. **Pattern-parity ratchet.** strip-then-non-empty on all string fields. `Field(...)` with description. Closed-enum Literal types. `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Timezone-aware datetime for `locked_at`. sha256-hex `artifact_digest`.
5. **Class-conformance arithmetic.** UNCHANGED (no parity_contract decorator added).
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T4)

```bash
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/test_section_09_lock.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-19-section-09-four-artifact-lock-semantics.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/section_09_lock.py tests/marcus/orchestrator/test_section_09_lock.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-19.ready-for-review.md`. Include: 2-file lockstep verification + Marcus-side function evidence (`enforce_section_09_lock` signature + 4-artifact-kind lock semantics + GateError-raise path verified) + tripwire-ledger entry shape evidence (sample JSONL line bytes) + Marcus M1-M4 import-linter UNCHANGED (12 KEPT) + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + T1-T9 decisions: which Pydantic-v2 models for Kira/Vera/Quinn-R artifact validation (located under `app/specialists/` OR fallback minimal-model-with-rationale).

T11: Claude lite tier (~10-15 min). Lite-batchable per AMEND-V3 if path-disjoint with concurrent 7c.18a/b reviews.

## Boundary

HALT on: 7c.17a + 7c.17b not done; class-conformance count != T1-baseline (UNCHANGED expected); broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; tripwire-ledger non-deterministic (test fails; root-cause); GateError raised but not propagated to caller (lock function should NOT swallow the exception).

DO NOT touch: `app/marcus/orchestrator/gate_runner.py`; `app/gates/errors.py`; `app/marcus/orchestrator/writers/`; `app/specialists/`; pyproject.toml; closed §section packages; 7c.18a/b deliverables.

DO NOT introduce: new third-party deps; defensive widening on `artifact_kind` Literal or `lock_status` Literal; new exception classes (use canonical `GateError` from `app.gates.errors`); silent-error-swallowing patterns (lock failure must raise); integration logic for what advances downstream (out of scope — lock CHECK only; downstream advancement gating is the caller's responsibility).
```

---

## Operator dispatch checklist

1. ☐ 7c.17a + 7c.17b done (Wave 4 close-batch landed).
2. ☐ AMELIA-P2 freshness check (re-run validator post-Wave-4 close).
3. ☐ Sandbox-AC validator PASS.
4. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=1 pre-author commit).
5. ☐ Confirm `app/specialists/{kira,vera,quinn_r}/` Pydantic-v2 models locatable (T1 readiness check) OR allow fallback minimal-model approach.
6. ☐ Dispatch (solo OR concurrent with 7c.18a/b — path-disjoint).

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.18a/b land concurrently, spawn all three T11 reviews in parallel + close-batch commit when all PASS.
