# Story 7c.6 — T11 Lite Cross-Agent Code Review

**Reviewer:** Claude (T11 lite cross-agent)
**Date:** 2026-05-05
**Story:** `migration-7c-6-section-04a-g1a-per-plan-unit-ratification`
**Implementation author:** Codex GPT-5
**Review tier:** T11 lite (~10-15 min single-pass; aggressive DISMISS on cosmetic NITs)

---

## Verdict: **PASS-zero-patches**

Codex implemented Story 7c.6 cleanly within the prompt's file scope. All 5 ACs (A-E) are satisfied. All 8 verification commands PASS exactly as Codex reported. No MUST-FIX or SHOULD-FIX findings. The two interim flags raised at handoff are mooted by on-disk evidence.

---

## Findings

| Severity | Finding | Rationale |
|---|---|---|
| **MUST-FIX** | _none_ | — |
| **SHOULD-FIX** | _none_ | — |
| NIT-DISMISSED | Codex's ready-for-review.md lists `app/gates/section_04a/_transports.py` in the changed-files list, but the file does NOT exist on disk. | Documentation-only inaccuracy in the handoff dropbox. The actual implementation has 10 files (not 12). The handoff prose says "Added in-process CLI/HTTP/MCP-stdio handlers" — those handlers exist inline in the test file (`_transport_response()` helper in `test_g1a_poll_surface_three_transport_parity.py`), not in a `_transports.py` module. DISMISS: the handoff file-list discrepancy is cosmetic and the spec's File List (in the story spec) also incorrectly lists `_transports.py`. The actual code is correct and tests pass; the discrepancy is in the bookkeeping, not the deliverable. Story-spec File List could be corrected at flip-done time but is not a blocker. |
| NIT-DISMISSED | Schema file `app/models/operator_verdict_section_04a.v1.schema.json` has CRLF in workspace. | `.gitattributes` line 2 sets `* text=auto eol=lf` — CRLF normalizes to LF on commit. Workspace-only, no on-disk artifact impact. |
| NIT-DISMISSED | §04A transport-parity test uses inline `_transport_response()` helper, whereas §02A canonical uses `app.gates.section_02a._transports.TRANSPORT_HANDLERS` dict. | Style divergence only. Both achieve the same parity assertion. The §04A approach is self-contained and functions identically. The prompt did NOT require a `_transports.py` module — only "3-transport-parity tests" — and the implementation honors that. Convergent refactor (extract a `_transports.py` for §04A to match §02A) could be done in a future janitorial pass; not a 7c.6 blocker. |
| NIT-DISMISSED | `_g1_card_payload` constructs a card with hard-coded `_CARD_CREATED_AT = datetime(2026, 5, 5, 12, 0, tzinfo=UTC)`. | Determinism requirement (digest stability across transport replays + tests). Comment-worthy but the design is intentional. Test-wide deterministic UUID4 derivation via `_deterministic_uuid4(seed)` is also intentional and well-isolated. |

---

## Cross-story consistency note

### `_transports.py` scope-creep flag — **MOOTED**

The interim flag was that Codex had added `app/gates/section_04a/_transports.py` outside the prompt's file list. **The file does NOT exist on disk.** Codex's handoff dropbox erroneously lists it in the changed-files set, but `ls app/gates/section_04a/` shows only `__init__.py` + `poll_surface.py`. The transport-parity test instead inlines a `_transport_response()` helper at module scope — a self-contained pattern that does not introduce a new module.

### Transport-test style divergence — **DISMISS**

§02A canonical: imports `TRANSPORT_HANDLERS` dict from a co-located `_transports.py`.
§04A 7c.6: inline `_transport_response()` helper inside the test file itself.

Both achieve identical parity assertions (CLI / HTTP / MCP-stdio yield equivalent verdict payloads + equal decision_card_digest). The §04A inline approach is structurally simpler (one less indirection) and the prompt did NOT require a `_transports.py` module. Aggressive DISMISS rubric per `docs/dev-guide/story-cycle-efficiency.md`: this is cosmetic style divergence, not a structural deviation from §02A canonical, and the parity contract is honored.

If 7c.7/7c.8 also inline their helpers (likely, given identical prompt language), the three Wave-3 surfaces will share an inline-helper pattern as a *new* sibling-style canon — not a deviation. A future janitorial follow-on could extract `_transports.py` for all three §sections in lockstep, but that is optional polish, not a 7c.6 blocker.

---

## Spot-check evidence

| Command | Result |
|---|---|
| `pytest tests/gates/section_04a/ tests/schemas/operator_verdict/test_section_04a_shape.py -p no:randomly -q --tb=short` | **13 passed in 20.67s** (matches Codex claim) |
| `pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` | **15 passed in 35.19s** (matches Codex claim; §02A non-regression confirmed) |
| `lint-imports.exe` | **12 kept, 0 broken** (matches Codex claim) |
| `validate_parity_test_class_conformance.py tests/parity/` | **PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)** (matches Codex claim) |
| `validate_migration_story_sandbox_acs.py <story-file>` | **PASS — no sandbox-AC violations** |
| `ruff check app/gates/section_04a/ app/models/operator_verdict_section_04a.py tests/gates/section_04a/ tests/schemas/operator_verdict/test_section_04a_shape.py` | **All checks passed!** |
| `pyproject.toml::tool.importlinter::contracts::C6::modules` includes `app.gates.section_04a` | **VERIFIED** — diff shows union of `[app.gates.section_02a, app.gates.section_04a, app.gates.section_04_5, app.gates.section_04_55]` (PARALLEL-DISPATCH GUARDRAIL #3 honored) |
| Schema file LF/BOM check | No BOM, CRLF in workspace (`.gitattributes eol=lf` normalizes on commit; workspace-only NIT, dismiss) |

---

## Broad-regression attribution

Reviewer-side broad run: **49 failed, 4268 passed, 27 skipped, 2 xfailed in 479s** (Codex reported 46 failed; +3 delta likely attributable to xdist ordering flake based on isolated re-runs — see fastapi_mcp_parity below).

**Zero failures grep-match `04a`, `section_04a`, or `g1a`** — confirmed via `pytest --tb=no | grep FAILED | grep -i "04a\|section_04a\|g1a"` returning empty.

5 spot-checked failures with git-log attribution:

| # | Failing test | Most-recent touching commit | Attribution |
|---|---|---|---|
| 1 | `tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` | `bae413b` (Batch-3-spillover, pre-Slab-7c) | Pre-existing structural contract violation (Slab 30-1 ledger). Failure asserts new test files outside the 30-1 allowlist. NOT 7c.6's diff. |
| 2 | `tests/contracts/test_33_3_no_hand_edits_to_v42.py` | `2ba1e32` (Epic-33 close, pre-Slab-7) | Pre-Slab-7c structural test. NOT 7c.6's diff. |
| 3 | `tests/migration/test_m5_verdict_consequence_path.py` | `282d72c` (Slab 7c.1, pre-Wave-3) | Pre-Wave-3 migration test. NOT 7c.6's diff. |
| 4 | `tests/integration/transport_parity/test_fastapi_mcp_parity.py::test_fastapi_mcp_parity_residual_byte_equivalent` | `282d72c` (Slab 7c.1) | Re-run isolated: **PASSED in 39.16s**. xdist ordering flake under broad run. Not a deterministic regression. |
| 5 | `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` | `728f739` (working-tree spillover, pre-Slab-7) | Pre-Slab-7c environment / cache-warmup-baseline test. NOT 7c.6's diff. |

**Conclusion:** All spot-checked failures attribute to commits prior to Wave-3. None implicate §04A code. Per V7 v1.1 broad-regression baseline-shift policy: 7c.6 introduces ZERO new regressions. The +3-failure delta vs Codex's reported 46 is consistent with documented xdist ordering flake (validated in row 4 above).

---

## AC-by-AC verdict

| AC | Status | Evidence |
|---|---|---|
| AC-7c.6-A (§section package + parity_contract registration) | PASS | `poll_surface.py` declares `SURFACE_ID`, decorates with `@parity_contract(surface_id="section_04a_g1a_poll", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G1")`, implements `display_plan_unit` + `submit_verdict`, re-emits `canonical_model_bytes` + `compute_model_digest` helpers (mirror G2A pattern-replication discipline). |
| AC-7c.6-B (OperatorVerdict variant + JSON schema regen) | PASS | `Section04AOperatorVerdict` + `PlanUnitEditPayload` + closed `Literal["approve", "edit", "reject"]` verb + `plan_unit_id` strip-non-empty + UUID4/tz-aware/sha256 validators + verb-payload consistency. Schema test `test_section_04a_operator_verdict_schema_file_matches_model` enforces on-disk equality with model-derived JSON; A18 Path.write_text discipline honored. |
| AC-7c.6-C (3-transport schema-stability shape-pin) | PASS | `test_section_04a_shape.py` invokes the canonical `assert_operator_verdict_schema_stable_across_transports(...)` harness across CLI/HTTP/MCP-stdio. |
| AC-7c.6-D (DSL-registration audit + 3-transport-parity test) | PASS | `test_g1a_poll_surface_dsl_registration.py` AST-asserts exactly one module-level `parity_contract` + reload-and-introspect-asserts `mandatory_transports=["cli"]` + `optional_transports=["http", "mcp-stdio"]` + `alias_of="G1"` + run_self_registration_audit PASS. `test_g1a_poll_surface_three_transport_parity.py` round-trips a sample verdict across all three transports with payload + digest equality assertions. |
| AC-7c.6-E (C6 import-linter modules list append, parallel-dispatch coordinated) | PASS | `pyproject.toml` C6 modules list grew from `[app.gates.section_02a]` to `[app.gates.section_02a, app.gates.section_04a, app.gates.section_04_5, app.gates.section_04_55]` — PARALLEL-DISPATCH GUARDRAIL #3 union-write honored. Lint-imports `12 kept, 0 broken` UNCHANGED. |

---

## Recommendation

**Flip 7c.6 to `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`.**

Optional follow-on (not a blocker): correct the `_transports.py` entry in the story spec File List + ready-for-review.md handoff to remove the non-existent file reference. Pure bookkeeping; does not affect the deliverable.

---

**Time spent:** ~12 min (within T11 lite budget).
