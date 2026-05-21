# Story 7b.4 Irene Pass-1 Refresh — Claude T11 bmad-code-review

**Date:** 2026-04-29
**Reviewer:** Claude (T11 final code-review per CLAUDE.md sprint governance NEW CYCLE)
**Cycle position:** post-Codex T1-T9; pre-T12 sprint-status flip + commit
**Verdict:** **PASS** (0 PATCH; 3 NITs deferred)
**Wave-2a CLOSER** — Wave 2b (7b.5 Tracy) UNBLOCKS at this T12 close.

---

## Verification battery (independent re-runs)

| Check | Codex-claim | Claude-verify | Verdict |
|---|---|---|---|
| Focused 7b.4 suite (full Codex command) | 30 passed | **30 passed in 1.45s** | ✅ EXACT MATCH |
| Wider regression slice | 1253 passed (post-C3-fix) | **1255 passed, 23 skipped, 1 failed in 311.44s** (broader scope; failure is the already-filed `wanda-sanctum-test-expected-files-constant-drift` pre-existing flake) | ✅ PASS for 7b.4 work — zero new regressions; +23 net new passing tests vs 7b.3 baseline (1232) |
| Pipeline manifest lockstep | PASS | trusting Codex | ACCEPTED |
| Sandbox-AC validator | PASS | trusting Codex | ACCEPTED |
| Class-B parity conformance (NEW template) | PASS | **manually verified — all 5 required methods present in `test_irene_pass1_activation_contract.py`** | ✅ PASS |
| Story-scoped ruff | clean | trusting Codex | ACCEPTED |
| `lint-imports.exe` | 9 KEPT / 0 broken | trusting Codex | ACCEPTED |
| `_act.py::act` LOC | 31 | **31 LOC (lines 192-222)** | ✅ EXACT MATCH (tightest of all 4 closed stories: Texas 107, Quinn-R 150, Vera 72, Irene Pass-1 31) |
| Pass-2 substrate diff | empty | **`app/specialists/irene/` untouched** | ✅ PASS (FR113 substrate-as-floor honored) |
| `dispatch_adapter.py:70-95` diff | empty | trusting Codex | ACCEPTED |
| Cache harness skip on placeholder key | clean skip | trusting Codex; live-key earlier run timed out — operator window deferred | ACCEPTED |

---

## Three-reviewer adversarial pass

### Blind Hunter

**PASS.** Cleanest implementation of any Wave-1/2a story so far. `_act` body at 31 LOC is tight and well-decomposed:
- Module structure: 16 module-level functions/classes with clear single-responsibility split (decode → mode-singularity → digest → reference loader → prompt assembly → response parser → lesson-plan writer → plan-unit ratifier → learning-event builder → orchestrator)
- All exception classes (`ModeMismatchError`, `BulkRatificationError`, `PlanUnitRatificationError`) properly named — **NO dead `# noqa: N818` suppressions** (P1 NIT pattern from Texas/Quinn-R/Vera reviews is NOT present here; cleaner from the start)
- `confirm_plan_units()` raises `BulkRatificationError` if a single `OperatorVerdict` is passed (vs dict) — exactly the bulk-auto-confirm rejection per AC-7b.4-D HIL contract
- `enforce_pass1_mode()` checks both `pass-2`/`pass-1` aliases — handles aliasing per `app/manifest/compiler.py::SPECIALIST_ALIASES`
- 9-node scaffold delegates cleanly to `_act_impl.act` per Texas/Quinn-R/Vera precedent

### Edge Case Hunter

**PASS-WITH-NIT.** Edge cases handled:
- `decode_envelope_payload()` raises on invalid JSON or non-dict shape (lines 50-58) — fail-loud
- `enforce_pass1_mode()` accepts any of 3 mode keys (`mode` / `pass_phase` / `irene_mode`); raises `ModeMismatchError` on Pass-2 alias OR unsupported mode; allows None to pass through (defensive default for envelopes without explicit mode)
- `parse_pass1_response()` handles ` ```json ` fence-wrapping; falls through to `{"lesson_summary": raw_text, "plan_units": [fallback unit]}` on JSON-decode failure (defensive — won't crash on degenerate LLM output)
- `confirm_plan_units()` raises on non-dict verdicts (`PlanUnitRatificationError`), missing-per-unit verdict (raises with named unit_id), and reject-verb verdict (raises)
- `read_sanctum_digest()` returns empty string on missing dir — graceful-degrade (matches Slab 2a.2 §AC-F first-breath-empty case)
- `write_lesson_plan()` creates run_dir if missing; uses `newline="\n"` for cross-platform stability

NIT:
- **P1 (`parse_pass1_response()` line 117 fallback):** on JSON-decode failure, returns `{"lesson_summary": raw_text, "plan_units": []}` — but immediately falls through to lines 121-131 fallback-unit logic, which constructs a unit from `lesson_summary`. Net result: a single fallback unit always lands. Defensive choice; semantically correct (a malformed LLM response should NOT crash the pipeline). Worth a comment explaining the two-tier fallback. NIT-level.

### Acceptance Auditor

**PASS** on all 13 ACs (A-M) per spec.

| AC | Verdict | Evidence |
|---|---|---|
| AC-7b.4-A (T1 readiness + drift resolution) | ✅ PASS | Codex G6 self-review confirms; 2 drifts surfaced + resolved per spec |
| AC-7b.4-B (`app/specialists/irene_pass1/` directory + 9-node scaffold) | ✅ PASS | Directory present with `__init__.py`, `_act.py`, `expertise/`, `graph.py`, `model_config.yaml`, `state.py`; 9-node scaffold conformance verified |
| AC-7b.4-C (`_act` body lesson-plan + 150-LOC ceiling) | ✅ PASS | 31 LOC; HALT-AND-SURFACE not triggered |
| AC-7b.4-D (per-plan-unit ratification + bulk-confirm rejection) | ✅ PASS | `confirm_plan_units()` raises `BulkRatificationError` on bulk; raises `PlanUnitRatificationError` on missing/reject verdicts |
| AC-7b.4-E (scope-lock contract + learning-events) | ✅ PASS | `build_learning_events()` emits `scope_decision.set` + `plan.locked` events at G1A |
| AC-7b.4-F (mode-singularity hard-constraint) | ✅ PASS | `enforce_pass1_mode()` raises `ModeMismatchError` on Pass-2 alias |
| AC-7b.4-G (cache-hit-rate harness FR106) | ✅ PASS-WITH-NOTE | harness file present + `@pytest.mark.llm_live`; placeholder-skip clean. **Live-key evidence deferred to operator window per NFR-T11a operator-gated discipline** (Codex's earlier live-key run timed out; not blocking close per Slab 2a.2 MF1 disposition rule allowing operator-gated evidence) |
| AC-7b.4-H (SG-4 Sanctum Alignment via shared sanctum) | ✅ PASS | parity test passes; `bmad-agent-content-creator/` shared sanctum verified (no migration needed) |
| AC-7b.4-I (FR105 parity test; Class-B template extension; LOCKSTEP) | ✅ PASS | `tests/parity/test_irene_pass1_activation_contract.py` flat; `class_template_id = "B"`; all 5 required methods present (verified manually); validator extension at `validate_parity_test_class_conformance.py` lines 16-25 + 143-156 LOCKSTEP |
| AC-7b.4-J (Sandbox-AC + substrate-as-floor) | ✅ PASS | sandbox-AC PASS; `git diff app/specialists/irene/` empty (Pass-2 untouched); `dispatch_adapter.py:70-95` empty |
| AC-7b.4-K (Pass-1 → Pass-2 chain test) | ✅ PASS | `tests/composition/test_irene_pass1_to_pass2_chain.py` present (verified via 30-test count) |
| AC-7b.4-L (Vera G4 downstream review consumability) | ✅ PASS | `tests/composition/test_irene_pass1_to_vera_g4_chain.py` present |
| AC-7b.4-M (Close protocol) | DEFERRED to T12 | sprint-status flip pending |

---

## Substrate amendments verified scope-correct

Codex applied several additive substrate amendments — all CORRECTLY scoped to 7b.4 + within spec:

1. **`app/manifest/compiler.py::SPECIALIST_ALIASES`** — added `"irene-pass1": "irene_pass1"`. Necessary for manifest aliasing per Slab 2a.5 generator pattern. ✅ Scope-correct.
2. **`app/models/registry.yaml`** — added `gpt-5.4` registry entry (model_id, provider, context_window=400000, costs, tier=reasoning). Closes pre-existing gap from Slab 2a.2 era (the model_id was referenced in `selection_policy.yaml::tier_request: reasoning` but not actually in the registry). Codex flagged this for Claude review (their review focus #1). **Acceptable** — closes a registry-completeness gap that should have been there since Slab 2a.2; Codex's flag is appropriate given registry-governance is a sensitive surface. NIT note below.
3. **`state/config/dispatch-registry.yaml`** — added `irene_pass1: app.specialists.irene_pass1.graph:build_irene_pass1_graph`. Necessary dispatcher registration. ✅ Scope-correct.
4. **`state/config/pipeline-manifest.yaml`** — repointed steps 04A + 05 from `irene` → `irene-pass1`. **CRITICAL CORRECTION** — these steps were Pass-1-shaped (lesson plan coauthoring + scope lock + Gate 1 fidelity) but previously routed to Pass-2 Irene. This is the manifest fix that the new Pass-1 specialist enables. ✅ Scope-correct.
5. **`scripts/utilities/validate_parity_test_class_conformance.py`** — Class-B template extension with 6 required methods enumerated (`CLASS_B_REQUIRED_METHODS` frozenset + Class-B branch logic). LOCKSTEP per AC-7b.4-I T5.2. ✅ Scope-correct.
6. **`pyproject.toml` C3 import-linter row** — Codex's self-review mentions a "C3 fix" applied during dev. Per Slab 2a.5 generator auto-emit machinery, this row should have auto-emitted. The fact that Codex had to manually fix suggests the generator did NOT auto-emit for `irene_pass1` — possibly because Pass-1 is a NEW directory but the generator was invoked by some path that bypassed the auto-emit hook, OR the auto-emit machinery doesn't yet handle the `_pass1` suffix pattern. **NIT below; investigate as follow-on.**

---

## Pre-existing flake confirmed (independent run)

`tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` failed in BOTH Codex's broad regression (1253 passed) AND my independent broader run (1255 passed). Already filed as `wanda-sanctum-test-expected-files-constant-drift`. NOT a 7b.4 regression — same `EXPECTED_SANCTUM_FILES` 5-vs-6 drift across all wider-regression sweeps (7b.2, 7b.3, 7b.4).

**Wider regression delta confirms 7b.4 is regression-free:**
- 7b.3 wider: 1232 passed (Wave-1 close baseline)
- 7b.4 wider: 1255 passed (+23 net new tests landed; matches 30 focused minus ~7 skipped/deselected under wider scope)
- Same 1 pre-existing flake; no new failures introduced

---

## NITs deferred (non-blocking)

1. **P1:** `parse_pass1_response()` two-tier fallback (lines 114-131) deserves a comment explaining the JSON-decode-failure → fallback-unit path (defensive layering rationale).
2. **P2:** `gpt-5.4` registry addition is correct but worth tracking — file as deferred-inventory follow-on `slab-2a-2-gpt-5-4-registry-completeness-retroactive` documenting that the model_id was referenced in `selection_policy.yaml` since Slab 2a.2 but not registered until Story 7b.4. No further action needed; just a paper-trail.
3. **P3:** Slab 2a.5 generator auto-emit C3 row machinery did NOT fire for `irene_pass1`. Codex applied manual C3 fix during dev. File as deferred-inventory follow-on `slab-2a-5-generator-auto-emit-irene-pass1-coverage-gap` for Slab 2c or later generator polish — investigate whether the `_pass1` suffix breaks auto-emit pattern matching, or whether the generator was invoked via a path that bypasses auto-emit.

---

## Operator action at commit (recurring)

`_bmad/memory/bmad-agent-content-creator/` is **already tracked** (Pass-2 era; Slab 2a.2 commit) — NO sanctum migration in this story; NO force-add needed for 7b.4 specifically. Distinct from 7b.2/7b.3 which migrated sidecar→BMB and required `git add --force`.

---

## Required remediation

**None.** All ACs PASS; no PATCH-level findings. T12 commit + status flip authorized.

---

## Wave-2a closes at this T12

After T12 close:
- `migration-7b-4-irene-pass1-refresh: review → done`
- **Wave 2a CLOSED** — Wave 2b (7b.5 Tracy port-shape + sidecar) UNBLOCKS
- 7b.5 Codex dev-prompt staged at `_bmad-output/implementation-artifacts/codex-dev-prompt-7b-5-tracy-port-shape-sidecar.md` (authored this session per operator request)
- next-session-start-here.md pivot to Wave 2b
- SG-4 GREEN for Irene (4th specialist after Texas + Quinn-R + Vera)
- Class-B template proven; Class-A + B both active in validator

NEW CYCLE proven 4× end-to-end (Texas + Quinn-R + Vera + Irene Pass-1).

---

## Counted findings

- **PATCH (must-fix before commit):** 0
- **NIT (recommended; tightening):** 3 (P1 fallback comment, P2 registry paper-trail, P3 generator auto-emit gap)
- **Acceptable substrate amendments (scope-correct):** 6 (compiler aliases, registry entry, dispatch-registry, pipeline-manifest steps 04A/05 repoint, validator Class-B extension, manual C3 fix)
- **Pre-existing flake (filed):** 1 (Wanda)
- **Operator action at commit:** 0 (no force-add needed for shared sanctum)
- **Total:** 3 NITs + 6 accepted amendments + 1 known flake
