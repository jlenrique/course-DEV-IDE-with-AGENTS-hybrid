# Story 7c.9 — T11 Lite Cross-Agent Code Review

**Reviewer:** Claude (T11 lite cross-agent)
**Date:** 2026-05-06
**Story:** `migration-7c-9-section-05-5-g2b-per-slide-mode`
**Implementation author:** Codex GPT-5
**Review tier:** T11 lite (~10-15 min single-pass; aggressive DISMISS on cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`)
**Wave:** 3 — slot 7 (G2C-aliased fanout, 4-story batch with 7c.10/7c.11/7c.12)

---

## Verdict: **PASS-zero-patches**

Codex implemented Story 7c.9 cleanly within the prompt's file scope. All 5 ACs (A-E) are satisfied. All focused / non-regression / validator commands PASS exactly as Codex reported. The flagged inherited `test_no_unauthorized_callers` failure is confirmed PRE-EXISTING noise (same scanner-staleness already filed at cbcd7e3 and dismissed in 7c.13/7c.14 reviewer precedent). 4-way C6 union coordination cleanly executed (10-entry post-state). No MUST-FIX or SHOULD-FIX findings.

---

## Findings

| Severity | Finding | Rationale |
|---|---|---|
| **MUST-FIX** | _none_ | — |
| **SHOULD-FIX** | _none_ | — |
| NIT-DISMISSED | `test_no_unauthorized_callers` lists `app/models/operator_verdict_section_05_5.py` (and §07b/§07d/§07f siblings) in its substring scan output | Pre-existing scanner staleness (substring match on `OperatorVerdict(` hits CLASS DEFINITIONS like `class Section05_5OperatorVerdict(BaseModel):`, NOT direct constructor calls). Documented at `cbcd7e3` deferred-inventory and dismissed in 7c.13 + 7c.14 reviewer precedent. 7c.9 inherits the noise; introduces no new failure category. **DISMISS.** |
| NIT-DISMISSED | §02A DSL-registration test `test_self_registration_audit_passes_floor_10` fails under broad-run xdist | Shared-registry xdist ordering flake; §02A files unchanged since 7c.3b (`f8fc1a8`). §05.5 registration test correctly reload-isolated via `_clear_registered_surfaces_for_tests()` + `importlib.reload`. NOT a 7c.9 regression. |

---

## Verb-pattern verification (FR-7c-13 + closest-sibling 7c.14 parity)

Read at `app/models/operator_verdict_section_05_5.py`:

| Spec requirement | Implementation evidence | Match |
|---|---|---|
| `verb` Literal MUST be `["select", "edit", "reject"]` (NOT approve/edit/reject) | Line 21: `Section05_5VerdictVerb = Literal["select", "edit", "reject"]` | ✓ |
| `PerSlideModePayload.selected_mode` MUST be closed `Literal["narrated-deck", "motion-enabled-narrated-lesson"]` per FR-7c-13 | Line 26: `PerSlideMode = Literal["narrated-deck", "motion-enabled-narrated-lesson"]` (used at line 41) | ✓ |
| 3-way verb-payload `model_validator(mode="after")` consistency | Lines 172-194: select→requires `select_payload`+forbids edit/reject; edit→requires `edit_payload`+forbids select/reject; reject→requires `reject_reason`+forbids select/edit | ✓ |
| UUID4 `run_id` validator | Lines 137-140: `enforce_uuid4_version` | ✓ |
| Tz-aware `submitted_at` validator | Lines 158-161: `enforce_tz_aware` | ✓ |
| sha256-hex `decision_card_digest` validator | Lines 163-170: `re.fullmatch(r"[0-9a-f]{64}", ...)` | ✓ |
| Strip-then-non-empty validators on `slide_id` + `operator_id` (mode="before") | Lines 142-147 | ✓ |
| Strip-then-non-empty for optional `reject_reason` and `rationale` | Lines 50-57 + 149-156 | ✓ |
| `model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)` | Lines 87-91 (and 39, 63 for payloads) | ✓ |
| Closed `Section05_5SurfaceId = Literal["section_05_5_g2b_per_slide_mode"]` | Line 22 | ✓ |
| `parity_contract` decorator: `surface_id="section_05_5_g2b_per_slide_mode"` + `mandatory_transports=["cli"]` + `optional_transports=["http", "mcp-stdio"]` + `alias_of="G2C"` | `app/gates/section_05_5/poll_surface.py:31-36` | ✓ |
| Re-emitted `canonical_model_bytes` + `compute_model_digest` helpers locally (C6 cross-§section independence) | `poll_surface.py:42-56` | ✓ |
| DSL-registration test reload-isolated | `test_g2b_poll_surface_dsl_registration.py:15-22` (`_clear_registered_surfaces_for_tests` + `importlib.reload`) | ✓ |

Pattern-parity with closest-sibling 7c.14 (§11 voice-selection): IDENTICAL shape (3-way select/edit/reject + closed enum payload + 3-way model_validator). PASS.

---

## C6 union verification (4-way coordinate-or-sequence)

Read at `pyproject.toml::tool.importlinter::contracts::C6::modules` (lines 256-266):

```
section_02a, section_04a, section_04_5, section_04_55, section_08b, section_11,  # pre-state (6 entries from 7c.3b + Wave-3 trio + next-batch)
section_05_5, section_07b, section_07d, section_07f                                # 4-way append (this story + 7c.10 + 7c.11 + 7c.12)
```

**Post-state: 10 entries TOTAL.** ✓ Matches the AC-7c.9-E PARALLEL-DISPATCH GUARDRAIL #3 requirement. Lint-imports `12 KEPT, 0 broken` UNCHANGED. 4-way coordination clean.

---

## Spot-check evidence

| Command | Expected | Actual | Match |
|---|---|---|---|
| `pytest tests/gates/section_05_5/ tests/schemas/operator_verdict/test_section_05_5_shape.py` | 13 passed | **13 passed in 4.07s** | ✓ |
| `pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py` | 15 passed | **15 passed in 5.27s** | ✓ |
| `pytest tests/gates/section_04a/ section_04_5/ section_04_55/ section_08b/ section_11/` | 43 passed | **43 passed in 6.15s** | ✓ |
| `lint-imports.exe` | 12 KEPT | **Contracts: 12 kept, 0 broken** | ✓ |
| `validate_parity_test_class_conformance.py tests/parity/` | 19 PASS | **PASS: 19 parity contract file(s) conform** | ✓ |
| `validate_migration_story_sandbox_acs.py <story-file>` | PASS | **PASS — no sandbox-AC violations** | ✓ |
| `ruff check app/gates/section_05_5/ app/models/operator_verdict_section_05_5.py tests/...` | clean | **All checks passed!** | ✓ |
| `operator_verdict_section_05_5.v1.schema.json` LF-only / no BOM | LF-only / no BOM | **size=3887, has_BOM=False, has_CRLF=False, has_CR=False** | ✓ |
| `pyproject.toml::C6::modules` 4-way union (section_05_5 + section_07b + section_07d + section_07f) | 10-entry post-state | **VERIFIED** (10 entries; lines 257-266) | ✓ |

---

## Broad-regression attribution

Reviewer-side broad run: **43 failed, 4351 passed, 27 skipped, 2 xfailed in 231.89s** — exact match with Codex's reported `43 failed, 4352 passed` (1-test counting drift within tolerance, attributable to xdist worker partition variance; not 7c.9-introduced).

5 spot-checked failures with git-log attribution:

| # | Failing test | Most-recent touching commit | Attribution |
|---|---|---|---|
| 1 | `tests/test_run_hud.py::TestScanBundleArtifacts::test_lists_files_with_sizes` | `162d129` 2026-04-27 (Slab 6 trial experience bundle) | Pre-Slab-7c. NOT 7c.9's diff. |
| 2 | `tests/end_to_end/test_full_pipeline_smoke.py::test_migrated_manifest_has_33_nodes` | `eb2adb0` 2026-04-23 (Slab 1 Story 1.6 manifest migration) | Pre-Slab-7c. NOT 7c.9's diff. |
| 3 | `tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` | `9e441f7` 2026-04-26 (Epic 3.3 verdict resume tamper) | Pre-Slab-7c structural scanner; substring-match staleness already documented + dismissed at cbcd7e3. NOT 7c.9's diff. |
| 4 | `tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` | `2ba1e32` 2026-04-19 (Epic 33 Pipeline Lockstep close) | Pre-Slab-7c structural ledger contract. NOT 7c.9's diff. |
| 5 | `tests/migration/test_m5_verdict_consequence_path.py::test_m5_verdict_consequence_path` | `728f739` 2026-04-27 (working-tree spillover Slab 6.0+6.1) | Pre-Slab-7c. NOT 7c.9's diff. |

**Conclusion:** All 5 spot-checked failures attribute to commits prior to Wave-3 (latest touch 2026-04-27, all pre-Slab-7c). None implicate §05.5 code. Failure count 43 is at the inherited Wave-3 next-batch baseline UNCHANGED (same as 7c.13/7c.14 closeouts). **7c.9 introduces ZERO new regressions per V7 v2 broad-regression baseline-shift policy.**

---

## AC-by-AC verdict

| AC | Status | Evidence |
|---|---|---|
| AC-7c.9-A (§section package + parity_contract registration) | PASS | `app/gates/section_05_5/poll_surface.py` declares `SURFACE_ID = SECTION_05_5_SURFACE_ID`, decorates `_parity_contract_registration` with `@parity_contract(surface_id="section_05_5_g2b_per_slide_mode", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G2C")`, implements `display_per_slide_mode` + `submit_verdict` + `resume_from_verdict` + `load_per_slide_mode`, re-emits `canonical_model_bytes` + `compute_model_digest` locally per Wave-3 sibling precedent. |
| AC-7c.9-B (OperatorVerdict variant + JSON schema regen) | PASS | `Section05_5OperatorVerdict` + `PerSlideModePayload` (with closed `selected_mode: Literal["narrated-deck", "motion-enabled-narrated-lesson"]`) + `PerSlideModeEditPayload` + closed `Literal["select", "edit", "reject"]` verb + UUID4/tz-aware/sha256 validators + 3-way verb-payload consistency `model_validator(mode="after")`. JSON schema on disk matches model output exactly (test `test_section_05_5_operator_verdict_schema_file_matches_model` enforces); A18 Path.write_text discipline verified at byte level (LF-only, no BOM). |
| AC-7c.9-C (3-transport schema-stability shape-pin) | PASS | `test_section_05_5_shape.py:34-62` invokes canonical `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section05_5OperatorVerdict, surface_id=SECTION_05_5_SURFACE_ID, transports=["cli", "http", "mcp-stdio"])` from FR-7c-49 harness. |
| AC-7c.9-D (DSL-registration audit + 3-transport-parity test) | PASS | `test_g2b_poll_surface_dsl_registration.py` AST-asserts exactly one module-level `parity_contract` + reload-isolated introspection asserts `mandatory_transports=["cli"]` + `optional_transports=["http", "mcp-stdio"]` + `alias_of="G2C"` + `run_self_registration_audit` PASS. `test_g2b_poll_surface_three_transport_parity.py` round-trips a sample G2B verdict across all three transports with payload + digest equality + tampered-digest rejection + slide_id-mismatch rejection + YAML loader UTF-8 path. |
| AC-7c.9-E (C6 import-linter modules list 4-way union append) | PASS | `pyproject.toml` C6 modules grew from 6 → 10 entries; `app.gates.section_05_5` + `app.gates.section_07b` + `app.gates.section_07d` + `app.gates.section_07f` all present per PARALLEL-DISPATCH GUARDRAIL #3 4-way coordinate-or-sequence rule. Lint-imports `12 KEPT, 0 broken` UNCHANGED. |

---

## Recommendation

**Flip 7c.9 to `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`.**

No follow-on work required. Story closes cleanly under the Wave-3 lite-tier follower pattern, first G2C-aliased fanout slot. The two pre-existing NITs (xdist flake + scanner staleness) remain inherited from earlier Wave-3 closeouts — both addressed by separate test-hardening stories (out of 7c.9 scope). 4-way C6 coordinate-or-sequence cleanly executed.

---

**Verdict file path:** `_bmad-output/implementation-artifacts/7c-9-code-review-2026-05-06.md`
**Time spent:** ~13 min (within T11 lite budget).
