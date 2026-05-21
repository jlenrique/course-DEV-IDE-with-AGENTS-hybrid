# T11 Standard Code Review — Story 7c.1 (Parity-Contract DSL Foundation; 8-File Refactor)

**Story key:** `migration-7c-1-parity-contract-dsl-foundation`
**Reviewer:** Claude (Opus 4.7), fresh review pass per BMAD sprint governance §3
**T11 tier:** standard (per governance JSON post-velocity-bundle; dual-gate but not cross-agent MANDATORY)
**Diff size:** ~325 LOC (12 files; 8 modified transport-parity test files + 2 new structural tests + 2 spec/sprint-status flips)
**Codex T10 dropbox notice:** PRESENT at `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md`
**Review date:** 2026-05-04

---

## Verdict: **PASS** (zero patches; zero deferred items)

Story 7c.1 delivers all 4 ACs (A/B/C/D) cleanly. The 8-file refactor follows a uniform pattern (module-level `@parity_contract` + sentinel `_parity_contract_registration` function with filename-stem surface_id). Transport derivation per file is documented in Codex's T10 evidence table and matches the spec recommendations exactly. Two new structural tests validate (a) AST-scan-based decorator presence + surface_id + mandatory_transports per file and (b) self-registration audit at floor=9 with explicit discovery_roots covering both production packages (app.gates + app.composers) and test packages (tests.integration.transport_parity + tests.integration.transports).

**Key wins:**
- **Consistent refactor pattern across all 8 files** — single sentinel function `_parity_contract_registration` per file; surface_id = filename-stem-without-`test_`-prefix; zero-deviation across the set.
- **Audit floor=9 PASS:** 8 refactored files + 1 reference surface (`reference_7c0b_scaffold` from 7c.0b) = 9 baseline registrations. Self-registration audit harness now has empirical evidence to score against; downstream HIL surface stories (7c.6..15) inherit the canonical pattern.
- **Zero broad-regression delta:** failure count remains 39 (pre-existing checkout drift); pass count increases by exactly 10 (2 new structural test files × 9 + 1 cases). NFR-7c-R2 invariant preserved.
- **NFR-7c-P3 wall-clock budget:** parity suite serial 7.15s, parallel 9.49s (parallel slightly slower than serial for ~15-cell suite due to xdist worker overhead — expected per Murat's risk model; both well under ≤90s budget).

---

## Verification Battery (per Codex T10)

| Check | Status | Evidence |
|---|---|---|
| Sandbox-AC validator | ✅ PASS | Codex T10 |
| Class-conformance | ✅ PASS | 11 activation contracts (UNCHANGED) |
| `lint-imports` | ✅ PASS | 12 KEPT / 0 broken (UNCHANGED) |
| Focused transport suite | ✅ PASS | 19 passed in 11.30s |
| Structural pins (10 cases) | ✅ PASS | 10 passed in 8.94s |
| Self-registration audit at floor=9 | ✅ PASS | All 9 expected surface_ids present in manifest |
| Broad post-refactor pass | ✅ PASS | 39 failed / 4058 passed / 27 skipped / 2 xfailed in 215.39s; failures match T1 baseline |
| Serial marker pass | ✅ PASS | 2 passed / 4172 deselected in 11.01s |
| Parity wall-clock | ✅ PASS | serial 7.15s + parallel 9.49s (both <<90s) |
| Ruff hygiene | ✅ PASS | All checks passed |

---

## Layered Findings (Blind / Edge / Auditor)

### Blind Hunter
- **B-1 [PASS]** Each of 8 refactored files imports `parity_contract` from `app.parity.contracts` + adds exactly one module-level decorator on a sentinel function. Diff per file = ~10 LOC; zero changes to existing test logic.
- **B-2 [PASS]** Surface_id naming convention (`<filename-stem-without-test_-prefix>`) applied uniformly: `fastapi_mcp_parity` / `mcp_stdio_smoke` / `mcp_subprocess_hygiene` / `transport_parity` / `override_transport_parity` / `cli_gate_decide` / `http_gate_endpoint` / `mcp_gate_decide_tool`.
- **B-3 [PASS]** Transport derivation per file matches spec recommendations exactly (Codex's table cross-validated against AC-7c.1-A bullet 4 recommendations).
- **B-4 [PASS]** No new helper modules under `app.parity.contracts.*` (out-of-scope guard honored). No new third-party deps.
- **B-5 [PASS]** No `@pytest.mark.serial` markers introduced — refactor is xdist-safe by construction.

### Edge Case Hunter
- **E-1 [PASS]** AST-scan structural test correctly identifies module-level decorators on `FunctionDef | ClassDef` nodes; uses `ast.unparse(decorator.func) == "parity_contract"` for resolution; cross-checks `surface_id` and `mandatory_transports` keyword args via `ast.literal_eval`. Robust against per-test-function decoration anti-pattern.
- **E-2 [PASS]** Self-registration audit test clears registry before invocation (`_clear_registered_surfaces_for_tests`); explicit `discovery_roots` parameter exercises the `_audit.py` override path; asserts `EXPECTED_SURFACES.issubset(surface_ids)` (subset, not equality — tolerant of additional surfaces from `app.gates`/`app.composers` if any are added later).
- **E-3 [PASS]** Audit harness's discovery walks include test packages (`tests.integration.transport_parity` + `tests.integration.transports`) — verifies the 7c.0b harness's `discovery_roots` parameter override path works end-to-end.

### Acceptance Auditor
- **A-AC-A [PASS]** All 8 files refactored per locked pattern; AST-scan structural test validates per file; surface_id + mandatory_transports verified.
- **A-AC-B [PASS]** Self-registration audit at floor=9 PASS with explicit discovery_roots; manifest contains all 9 EXPECTED_SURFACES.
- **A-AC-C [PASS]** Wall-clock 7.15s serial / 9.49s parallel; both <<NFR-7c-P3 ≤90s budget. Existing 8 files pass post-refactor (zero functional regression).
- **A-AC-D [PASS]** Broad-regression delta = +10 passed (2 new structural test files); failure count UNCHANGED at 39 (NFR-7c-R2 invariant); class-conformance 11 (UNCHANGED); lint-imports 12 KEPT (UNCHANGED); sandbox-AC PASS; ruff clean.

---

## Sign-Off

**Verdict:** PASS (zero patches; zero deferred items).

7c.1 is a textbook substrate-precondition refactor: predecessor frozen, pattern uniform, semantics preserved, broad-regression delta = +10 (exactly the 10 new structural test cases), zero functional regression. Downstream HIL surface stories (7c.6..15) and per-gate stories (7c.5.G0..G6) inherit the canonical `@parity_contract` + sentinel-function pattern from this refactor.

**Next action:** Stage and commit 7c.1 deliverables; flip `migration-7c-1-parity-contract-dsl-foundation: review → done` in sprint-status.yaml.

**Cumulative slab progress post-7c.1:** 5 stories closed (7c.0a / 7c.2 / 7c.0b / 7c.0c / 7c.1) + 7c.4a in-flight + 7c.3a authored ready-for-dev. ~31 of original 36 remaining (now 30 after 7c.4a closes); velocity-amendments savings (xdist + smoke-suite + R-tier + T11-tier) compounding across the remainder.
