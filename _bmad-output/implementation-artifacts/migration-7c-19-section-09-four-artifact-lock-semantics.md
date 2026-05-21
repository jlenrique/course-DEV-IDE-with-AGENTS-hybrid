# Migration Story 7c.19: §09 Four-Artifact Lock Semantics (FR-7c-28)

**Status:** review *(Codex implementation complete 2026-05-06; ready for T11 lite review.)*
**Sprint key:** `migration-7c-19-section-09-four-artifact-lock-semantics`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 1
**K-target:** 1.2×
**Estimated LOC:** ~400 (Marcus-side lock-check function ~120 + Section09LockResult Pydantic-v2 model + LockArtifactRef sub-model ~50 + tripwire-ledger linkage helper ~30 + test file with happy + 4 absent-artifact + 2-3 inconsistency paths ~200)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON entry `7c-19`; AC count ≤5 + Marcus-orchestrator-side enforcement function + new Pydantic-v2 result model + sibling tests + no parity_contract DSL touch + no HIL surface + no C6 modules list edit + Codex T10 self-review clean + single-gate)
**Lookahead-tier:** 1
**files_touched:** 2 new + 0 modified (greenfield Marcus-side lock module + test file)

---

## Story

As Marcus,
I want to enforce four-artifact lock semantics at §09 (post-Gary slide-content + post-Kira motion-plan + post-Vera fidelity-verdict + post-Quinn-R QA-verdict), preventing downstream advancement until all four lock-quartet artifacts are present + consistent,
So that §11 voice-selection (and downstream surfaces) cannot fire prematurely against incomplete artifact sets — raising `GateError` on absence/inconsistency with tripwire-ledger linkage per NFR-7c-R3.

This is **NOT an HIL surface story** (distinct from 7c.18a/b operator-build pattern + 7c.13/7c.14 verdict pattern). It is a **Marcus-side enforcement function** colocated with existing Marcus orchestrator guardrails (`app/marcus/orchestrator/gate_runner.py` precedent for shared gate-runner guardrails). No parity_contract DSL registration; no OperatorVerdict variant; no C6 modules list append; no 3-transport schema-stability. The lock is a runtime guard at the §09 transition.

---

## Predecessor / Dependency Context

- **7c.17a** (Wave 4; close-pending; predecessor): produces `gary-slide-content.json` (FR-7c-21) — one of the four lock-quartet artifacts. THIS STORY's lock-check reads the artifact via 7c.17a's `GarySlideContent` Pydantic-v2 model for structural validation.
- **7c.17b** (Wave 4; close-pending; predecessor): produces `gary-outbound-envelope.yaml` aggregation referencing the 5 per-plan-unit packages. While the §09 lock-quartet specifically checks the 4 downstream artifacts (slide-content + motion-plan + fidelity-verdict + QA-verdict), the lock function may consume 7c.17b's envelope for plan_unit_id resolution.
- **7b.6 Gary** (CLOSED `1f81965` 2026-04-30): Class-C body-activated specialist; producer of slide-content artifact (post-Gary). Read-only sibling reference.
- **7b.7 Kira** (CLOSED `1f81965` 2026-04-30): Class-C body-activated specialist; producer of motion-plan artifact (post-Kira). Read-only sibling reference.
- **7b.3 Vera** (CLOSED `1f81965` 2026-04-30): Class-A hardened specialist; producer of fidelity-verdict (post-Vera). Read-only sibling reference.
- **7b.2 Quinn-R** (CLOSED `1f81965` 2026-04-30): Class-A hardened specialist; producer of QA-verdict (post-Quinn-R). Read-only sibling reference.
- **`app.gates.errors.GateError`**: the canonical exception type raised across Slab-7a/b/c gate-runner code (`app/gates/resume_api.py` raises 4×; `app/marcus/orchestrator/production_runner.py` raises 2×). THIS STORY raises `GateError` on lock failure (no new exception class; extend the canonical pattern).
- **`app/marcus/orchestrator/gate_runner.py`**: existing shared gate-runner guardrail module (Slab 7a closeout). Includes `MarcusDualityBoundaryError` + `evaluate_calibration_tripwire`. Provides the architectural precedent for "Marcus-side enforcement function with tripwire-ledger linkage" — THIS STORY follows the pattern.
- **NFR-7c-R3 tripwire-ledger completeness**: lock failures must be recorded to a tripwire-ledger (runtime path TBD by Codex T1; default: extend `gate_runner.py`'s `_append_jsonl` pattern — runtime tripwire log file under `_artifacts/` path). Per FR-7c-50 audit-chain integrity, the ledger entries follow append-only + monotonic-timestamp + parent-trace-linkage invariants.
- **No HIL surface; no parity_contract DSL; no C6 modules list edit; no pyproject.toml edit.** Marcus-side enforcement is governed by Marcus contracts M1-M4 (already in place); no new contracts.

---

## Acceptance Criteria

### AC-7c.19-A — `enforce_section_09_lock` Marcus-side function (FR-7c-28)

**Given** the four upstream artifacts (Gary slide-content + Kira motion-plan + Vera fidelity-verdict + Quinn-R QA-verdict) for a given plan_unit_id
**When** the dev-agent authors `app/marcus/orchestrator/section_09_lock.py` (greenfield Marcus-side module; mirrors `gate_runner.py`'s shared-guardrail-module style)
**Then** the module exposes:
1. `enforce_section_09_lock(plan_unit_id: str, artifact_paths: Section09LockArtifactPaths, *, tripwire_log_path: Path | None = None) -> Section09LockResult` — primary enforcement function.
2. Reads each of the 4 artifacts (paths supplied via `Section09LockArtifactPaths` Pydantic-v2 model with strip-then-non-empty Path validators).
3. For each artifact: validates structural shape via the producer's Pydantic-v2 model (`GarySlideContent` from 7c.17a; T1-T9 decision: identify the analogous models for Kira motion-plan, Vera fidelity-verdict, Quinn-R QA-verdict — these likely live under `app/specialists/{kira,vera,quinn_r}/` per Slab-7b body activation).
4. Validates **consistency**: all four artifacts reference the SAME `plan_unit_id` (cross-artifact `plan_unit_id` field equality check; T1-T9 decision: confirm each producer model carries `plan_unit_id` or equivalent identifier).
5. On success: returns `Section09LockResult` with `lock_status: Literal["locked"]` + 4 artifact-reference sub-fields (Gary/Kira/Vera/Quinn-R) carrying digest + path + plan_unit_id triplet per artifact.
6. On failure (any of: artifact-absent, parse-error, plan_unit_id-mismatch, model-validation-error): raises `GateError` (imported from `app.gates.errors`) with structured failure context (which artifact, what kind of failure) + appends a tripwire-ledger entry per NFR-7c-R3.

### AC-7c.19-B — Section09LockResult + Section09LockArtifactPaths Pydantic-v2 models

**When** the dev-agent declares the Pydantic-v2 result + input models inside `app/marcus/orchestrator/section_09_lock.py`:
1. `Section09LockArtifactPaths`: `model_config = ConfigDict(extra="forbid", validate_assignment=True)`; fields `gary_slide_content_path: Path` + `kira_motion_plan_path: Path` + `vera_fidelity_verdict_path: Path` + `quinn_r_qa_verdict_path: Path` (all 4 mandatory; strip-then-non-empty + Path-existence validation deferred to runtime — fields capture the PATHS the operator/Marcus expects to find).
2. `Section09LockArtifactRef` sub-model: `artifact_kind: Literal["gary-slide-content", "kira-motion-plan", "vera-fidelity-verdict", "quinn-r-qa-verdict"]` (closed enum) + `plan_unit_id: str` (`min_length=1` + strip-then-non-empty) + `artifact_digest: str` (sha256-hex pattern `^[0-9a-f]{64}$`) + `artifact_path: Path`.
3. `Section09LockResult`: `model_config = ConfigDict(extra="forbid", validate_assignment=True)`; fields `lock_status: Literal["locked"]` (success-only — failure raises GateError, not returns) + `plan_unit_id: str` + `gary_slide_content: Section09LockArtifactRef` + `kira_motion_plan: Section09LockArtifactRef` + `vera_fidelity_verdict: Section09LockArtifactRef` + `quinn_r_qa_verdict: Section09LockArtifactRef` + `locked_at: datetime` (timezone-aware UTC) + `schema_version: int = 1` (per FR-7c-51).

### AC-7c.19-C — Tripwire-ledger entry on lock failure (NFR-7c-R3)

**Given** any lock-failure path (artifact-absent / parse-error / plan_unit_id-mismatch / model-validation-error)
**When** `enforce_section_09_lock` detects the failure
**Then**:
1. The function appends a tripwire-ledger entry via `_append_jsonl`-style helper (mirror `app/marcus/orchestrator/gate_runner.py:_append_jsonl` precedent) at `tripwire_log_path` (default: `_artifacts/section_09_lock_tripwire.jsonl`).
2. Ledger entry shape: `{"event": "section_09_lock_failure", "plan_unit_id": str, "failure_kind": Literal[absent, parse_error, plan_unit_id_mismatch, validation_error], "failed_artifact_kind": Literal[<the 4 kinds>], "fired_at": iso8601-tz-aware, "schema_version": 1}` (deterministic dict ordering via `sort_keys=True` per JSONL append).
3. The function then raises `GateError` (so the caller sees the failure; the ledger entry is for audit-trail completeness).
4. The tripwire-ledger write is **append-only + monotonic-timestamp + JSON-serializable** per FR-7c-50 audit-chain integrity (no in-place edits; never overwrite).

### AC-7c.19-D — Tests for happy + 4 absent-artifact + ≥3 inconsistency paths

**Then** the dev-agent authors `tests/marcus/orchestrator/test_section_09_lock.py`:
1. **Happy path**: 4 valid artifacts on disk → `enforce_section_09_lock` returns `Section09LockResult(lock_status="locked")` + result fields populated correctly + sha256 digests verified.
2. **4 absent-artifact paths** (one per artifact_kind): each artifact missing in turn → `pytest.raises(GateError)` + tripwire-ledger entry asserted.
3. **3+ inconsistency paths**:
   a. plan_unit_id mismatch (Gary's plan_unit_id ≠ Kira's) → GateError + ledger entry.
   b. Pydantic validation error (e.g., Gary's slide-content has invalid `slide_index < 1`) → GateError + ledger entry.
   c. JSON parse error (corrupt artifact) → GateError + ledger entry.
4. **Determinism**: tripwire-ledger writes are byte-deterministic across re-invocations with identical input (sha256-stable JSONL line bytes).
5. **Schema-hash STABLE pin** on `Section09LockResult`: assert `hashlib.sha256(json.dumps(Section09LockResult.model_json_schema(), sort_keys=True).encode()).hexdigest()` matches a frozen literal (per FR-7c-51 schema_version discipline).

### AC-7c.19-E — Marcus M1-M4 import-linter contracts hold

**When** the dev-agent runs `lint-imports`:
**Then** all 12 import-linter contracts KEEP UNCHANGED. The new module `app.marcus.orchestrator.section_09_lock` falls under existing M1-M4 contract scope:
- M1: NOT a write_api caller (lock function does not import `app.models.state.run_state`).
- M2: does not import `app.cora`.
- M3: not imported by `app.specialists` (specialists run upstream of §09 lock; lock is downstream Marcus enforcement).
- M4: not imported by `app.marcus.dispatch` (dispatch stays dependency-light).

**Verification:** run `.venv/Scripts/lint-imports.exe` post-implementation; expect 12 KEPT / 0 broken UNCHANGED.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.17a + 7c.17b done in sprint-status (HARD predecessor block; lock-check consumes `GarySlideContent` from 7c.17a).
  - [x] T1.2 Read `app/marcus/orchestrator/gate_runner.py` (architectural precedent — shared gate-runner guardrail module; `_append_jsonl` pattern; `MarcusDualityBoundaryError` style).
  - [x] T1.3 Read `app/gates/errors.py` for `GateError` import location + signature.
  - [x] T1.4 Read `app/marcus/orchestrator/writers/slide_content.py` (7c.17a deliverable; `GarySlideContent` model for slide-content validation).
  - [x] T1.5 Identify Pydantic-v2 models for Kira motion-plan, Vera fidelity-verdict, Quinn-R QA-verdict (T1-T9 lookup under `app/specialists/{kira,vera,quinn_r}/` per Slab 7b body activation; if absent, document the gap and use a minimal local model that captures the lock-relevant fields — `plan_unit_id` + structural validation).
  - [x] T1.6 Read `pyproject.toml::tool.importlinter` (M1-M4 contracts; confirm scope coverage of new module).
  - [x] T1.7 Read `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` Appendix A (FR-7c-50 audit-chain integrity invariants — append-only + monotonic-timestamp + parent-trace-linkage).
  - [x] T1.8 Refresh broad-regression baseline + record class-conformance baseline.

- [x] **T2 — Author `app/marcus/orchestrator/section_09_lock.py` (AC-A + AC-B + AC-C)**
  - [x] T2.1 Author Pydantic-v2 models (`Section09LockArtifactPaths` + `Section09LockArtifactRef` + `Section09LockResult`).
  - [x] T2.2 Author `enforce_section_09_lock` function with structural validation + plan_unit_id consistency check.
  - [x] T2.3 Author `_append_section_09_tripwire` helper mirroring `gate_runner.py:_append_jsonl` style.

- [x] **T3 — Author tests (AC-D)**
  - [x] T3.1 `tests/marcus/orchestrator/__init__.py` (if not already present from 7c.17a; check first).
  - [x] T3.2 `tests/marcus/orchestrator/test_section_09_lock.py` covering happy + 4 absent + 3+ inconsistency paths + determinism + schema-hash STABLE pin.

- [x] **T4 — Verification battery (R-tier R2; T11-tier lite)**
  - [x] T4.1 Focused: `.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/test_section_09_lock.py -p no:randomly -q --tb=short` PASS.
  - [x] T4.2 Marcus orchestrator non-regression: `.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short` PASS UNCHANGED + 1 new test file.
  - [x] T4.3 Wave-3 + next-batch + G2C-fanout non-regression sweep: PASS UNCHANGED.
  - [x] T4.4 Wave-4 Marcus-writer non-regression: `.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T4.5 Smoke: nodeid baseline UNCHANGED.
  - [x] T4.6 R2 broad: failure count ≤ T1 baseline (45 failed vs inherited 47-failure Wave-5 pre-fix run; structural new-target failures resolved).
  - [x] T4.7 Class-conformance: PASS at 19 parity contract files; no parity_contract decorator added.
  - [x] T4.8 Lint-imports: 12 KEPT / 0 broken UNCHANGED.
  - [x] T4.9 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-19-section-09-four-artifact-lock-semantics.md` PASS.
  - [x] T4.10 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-19.ready-for-review.md` with: 2-file lockstep verification + Marcus-side function evidence (`enforce_section_09_lock` signature + 4-artifact-kind lock semantics + GateError-raise path verified) + tripwire-ledger entry shape evidence + Marcus M1-M4 import-linter UNCHANGED + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + T1-T9 decisions: which Pydantic-v2 models for Kira/Vera/Quinn-R artifact validation (located under `app/specialists/` OR fallback minimal-model-with-rationale).

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 predecessor; `GarySlideContent` shape).
3. `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` Appendix A (FR-7c-50 audit-chain integrity invariants).
4. `app/marcus/orchestrator/gate_runner.py` (architectural precedent — shared gate-runner guardrails + `_append_jsonl` pattern + `MarcusDualityBoundaryError` style).
5. `app/gates/errors.py` (`GateError` import + signature).
6. `app/gates/resume_api.py` (4× GateError-raise pattern reference; structured failure context).
7. `app/marcus/orchestrator/production_runner.py` (2× GateError-raise pattern reference + `MissingUpstreamContributionError` + `GateBypassError` precedents).
8. `app/marcus/orchestrator/writers/slide_content.py` (7c.17a; `GarySlideContent`).
9. `app/specialists/kira/` + `app/specialists/vera/` + `app/specialists/quinn_r/` (Slab 7b body deliverables; identify Pydantic-v2 models for the 3 non-Marcus artifacts).
10. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms; apply to Section09LockResult + sub-models).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening; if any schema regen happens).
12. `pyproject.toml::tool.importlinter` (M1-M4 contracts).
13. Governance JSON `7c-19` entry: gate_mode=single-gate, K=1.2×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].
14. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.19` (epic-level scope authority).
15. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-28 + NFR-7c-S1 (writer-boundary tamper-evidence) + NFR-7c-R3 (tripwire-ledger completeness).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-DEFERRED** until 7c.17a + 7c.17b close. Per governance JSON entry, this story has `prerequisite_stories=["7c-17a", "7c-17b"]` (binding=hard).

**Lookahead-tier=1 rationale:** spec is pre-authored to capture Wave-5 third-story intent. Dispatch occurs after Wave-4 close + Wave-5 entry pair (7c.18a + 7c.18b) close; OR can dispatch concurrently with 7c.18a/b if operator chooses.

**Parallel-dispatch viable with 7c.18a + 7c.18b:** path-disjoint at module level (7c.19 authors `app/marcus/orchestrator/section_09_lock.py`; 7c.18a/b author `app/gates/section_06b/` + `app/gates/section_07c/`). 7c.19 does NOT touch `pyproject.toml` C6 modules list — no coordinate-or-sequence with 7c.18a/b on that file. **However**, 7c.19's V7 v2 Murat triple-condition fit is partial: lookahead_tier=1 ✓ + t11_tier=lite ✓ + C6-touching ✗ (does NOT touch C6). Per V7 v2 conservative rule, parallel-dispatch with C6-touching siblings is in policy if the non-C6 story's surface is path-disjoint AND its T11 cycle is independent (LITE-batchable per AMEND-V3 = OK).

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- 2026-05-06: Focused Wave-5 new tests: 35 passed.
- 2026-05-06: Broad regression: 45 failed, 4412 passed, 27 skipped, 2 xfailed. Remaining failures are inherited baseline classes; prior new structural failures are resolved.
- 2026-05-06: Ruff clean; lint-imports 12 kept / 0 broken; class-conformance PASS at 19; sandbox-AC PASS.
- 2026-05-06: `Section09LockResult` schema hash pinned at `b26b0fb68a4bba3b06e57d764c2c16e4ea36b868d2d348485857cdd1db447f39`.

### Completion Notes List

- Implemented `enforce_section_09_lock(plan_unit_id, artifact_paths, *, tripwire_log_path=None)` with four-artifact presence, parse, validation, digest, and plan-unit consistency checks.
- Gary slide content validates through the 7c.17a `GarySlideContent` model.
- Kira motion-plan, Vera fidelity-verdict, and Quinn-R QA-verdict lock-ready Pydantic-v2 producer models were not located under `app/specialists/`; the lock uses a local minimal plan-unit model for those three artifacts and documents that fallback for T11.
- Failure paths append deterministic JSONL tripwire entries to `_artifacts/section_09_lock_tripwire.jsonl` by default, then raise canonical `GateError`.

### File List

- `app/marcus/orchestrator/section_09_lock.py`
- `tests/marcus/orchestrator/__init__.py`
- `tests/marcus/orchestrator/test_section_09_lock.py`

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-5 third-story dispatch post-Wave-4 close.
- 2026-05-06: Codex implemented §09 four-artifact lock semantics, tripwire ledger failure path, schema hash pin, tests, and ready-for-review handoff.
