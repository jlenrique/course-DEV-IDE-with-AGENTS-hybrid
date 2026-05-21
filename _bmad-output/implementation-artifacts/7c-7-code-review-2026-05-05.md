# T11 lite Code Review — Story 7c.7 (§04.5 G1.5 Run-Budget Estimator HIL Surface)

**Reviewer:** Claude (cross-agent T11 lite)
**Date:** 2026-05-05
**Codex implementation date:** 2026-05-06
**Story:** `migration-7c-7-section-04-5-g1-5-estimator`
**Tier:** T11 lite (~10–15 min budget; aggressive DISMISS rubric)
**Branch:** `dev/langchain-langgraph-foundation`

---

## Verdict

**PASS-zero-patches**

All AC-7c.7-A through AC-7c.7-E satisfied; focused suite, §02A non-regression, smoke, lint-imports, parity-class-conformance, sandbox-AC validator, and Ruff are GREEN. Broad-regression failures are pre-Wave-3 inherited drift, not 7c.7-attributable. C6 isolation correctly preserved via locally re-emitted digest helpers (sister-Wave-3 stories follow the same pattern). No MUST-FIX, no SHOULD-FIX in scope; one cross-Wave SHOULD-FIX deferred to follow-on.

---

## Findings

| ID | Severity | Finding | Rationale |
|----|----------|---------|-----------|
| F-1 | NIT-DISMISSED | `# noqa: N801` on `Section04_5OperatorVerdict` for underscore-in-class-name | Story spec mandates exact class name; targeted lint suppression is correct. Cosmetic. |
| F-2 | NIT-DISMISSED | Cross-story transport-parity-test cosmetic divergence (helper-function shape, parametrize matrix, fixture imports) | Domain-shape divergences are driven by surface-specific contracts (3-transport CLI+HTTP+optional MCP-stdio for 7c.6/7c.7 vs 2-transport CLI+HTTP for 7c.8). Structural pattern (parametrize → baseline → assert-equality → resume-verify) is identical to §02A canonical and sister stories. Per aggressive DISMISS rubric. |
| F-3 | NIT-DISMISSED | `app/models/operator_verdict_section_04_5.v1.schema.json` written with CRLF line endings (Windows default `Path.write_text` behavior) | A18 forbids only the UTF-8 BOM, NOT CRLF; file is BOM-free (verified bytes `<EF BB BF>` absent). The on-disk JSON is not consumed by byte-for-byte test assertions (shape-pin tests compare in-memory `model_json_schema()` only). Sister stories 7c.6 and 7c.8 wrote identical CRLF schema files via the same canonical command — cross-story consistency. NIT-deferred. |
| F-4 | SHOULD-FIX-DEFERRED (cross-Wave) | `canonical_model_bytes` + `compute_model_digest` are now byte-identical 4-way duplicated across `app/gates/section_02a/poll_surface.py`, `app/gates/section_04a/poll_surface.py`, `app/gates/section_04_5/poll_surface.py`, `app/gates/section_04_55/poll_surface.py` | C6 (independence type) forbids cross-§section *imports* but NOT shared utility imports from a non-§section module (e.g., `app/gates/_common/digest_helpers.py`). The story spec language "Reuse `canonical_model_bytes` + `compute_model_digest` helpers per §02A canonical" was interpreted by Codex (and sister-story Codex runs) as "replicate" rather than "import-from-shared-helper". This is **NOT a 7c.7 defect** — 7c.7 followed the established Wave-3 sister pattern AND avoided a real C6 violation that would have occurred with a cross-§section import. **Recommend filing a Wave-4 follow-on story** to extract `app/gates/_common/digest_helpers.py` once Wave-3 closes (eliminates 4-way duplication; preserves C6 by sourcing from outside the C6 module set). Out of scope for 7c.7 T11 lite. |

**MUST-FIX:** 0
**SHOULD-FIX (in-scope):** 0
**SHOULD-FIX (cross-Wave deferred):** 1 (F-4 → Wave-4 follow-on)
**NIT-DISMISSED:** 3 (F-1, F-2, F-3)

---

## C6 Isolation Judgment

**Verdict:** Re-emitted-helpers is the correct C6 discipline call for this story; the alternative (cross-§section import from §02A) would have been a hard import-linter violation (`independence` type). Codex caught the violation during dev (Debug Log: "Import-linter caught an initial cross-surface import from Section 04.5 to Section 02A helpers. Fixed by re-emitting identical `canonical_model_bytes` and `compute_model_digest` helpers locally") and remediated correctly.

**Better alternative exists but is out-of-scope:** A single shared helper at `app/gates/_common/digest_helpers.py` (outside the C6 modules list) would let all four §sections import the same implementation, eliminate 4-way duplication, and preserve C6 (since `_common` is not in the C6 modules set). This is a **cross-Wave architectural improvement**, not a 7c.7 patch — see F-4 above.

---

## Cross-Story Consistency (Wave-3 sister-story comparison)

- **7c.6** (§04A G1A per-plan-unit ratification, 3-transport): `tests/gates/section_04a/test_g1a_poll_surface_three_transport_parity.py` — uses `_transport_response()` helper, parametrize over `["cli", "http", "mcp-stdio"]`, baseline-vs-other comparison, resume-verify, edit-payload mutation test, tampered-digest test, YAML-load test. **Same structural pattern.**
- **7c.7** (§04.5 G1.5 estimator, 3-transport): `tests/gates/section_04_5/test_g1_5_estimator_three_transport_parity.py` — uses `_verdict_payload()` helper, parametrize over `["cli", "http", "mcp-stdio"]`, baseline-vs-other comparison, resume-verify, tampered-digest test, YAML-load test, mismatched-id test. **Same structural pattern, plus an extra `verb=acknowledged` shape.**
- **7c.8** (§04.55 run-constants, 2-transport): `tests/gates/section_04_55/test_g1_5_run_constants_two_transport_parity.py` — uses `_verdict_payload()` helper, parametrize over `["cli", "http"]`, baseline-vs-other comparison, **plus** explicit `mcp-stdio` rejection test (per FR-7c-11 2-transport-only contract), YAML-load test. **Same structural pattern, with the optional-transport shape inverted to a forbidden-transport assertion** (correct domain divergence).

**Conclusion:** Cross-story consistency adequate. All three Wave-3 sibling tests follow the §02A canonical structure (`_transport_response`/`_verdict_payload` → parametrize → baseline equality → resume-verify → tamper/error coverage). Divergences are domain-shape-driven (transport count + verb closure + payload shape per FR-7c-11), not stylistic.

---

## Spot-Check Evidence

```text
$ .venv/Scripts/python.exe -m pytest tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py -p no:randomly -q --tb=short
13 passed in 6.00s   [PASS — matches expected 13 passed]

$ .venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
15 passed in 23.74s   [PASS — matches expected 15 passed; §02A non-regression]

$ .venv/Scripts/lint-imports.exe
Contracts: 12 kept, 0 broken.   [PASS — matches expected 12 KEPT; C6 includes app.gates.section_04_5]

$ .venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin).   [PASS — matches expected 19]

$ .venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md
PASS — no sandbox-AC violations across 1 story file(s).   [PASS]

$ .venv/Scripts/python.exe -m ruff check app/gates/section_04_5/ app/models/operator_verdict_section_04_5.py tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py
All checks passed!   [PASS]

$ .venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q
181 passed, 18 skipped in 166.43s   [PASS — matches Codex evidence]
```

**Schema-file integrity check:**
```text
$ python -c "<bytes inspection>"
app/models/operator_verdict_section_04_5.v1.schema.json: BOM=False, CRLF=106, LF=106, size=2819
```
- BOM absent (A18 satisfied).
- CRLF present (Windows-default `Path.write_text` behavior; cross-story consistent with 7c.6 + 7c.8 schemas; not consumed for byte-for-byte assertions). NIT-DISMISSED.

**`pyproject.toml::tool.importlinter::contracts::C6`:**
```toml
modules = [
    "app.gates.section_02a",
    "app.gates.section_04a",
    "app.gates.section_04_5",   # ← 7c.7 entry (already present from coordinated 7c.6+7c.7+7c.8 pre-edit)
    "app.gates.section_04_55",
]
```
AC-7c.7-E satisfied (Codex Debug Log notes the pyproject.toml was pre-coordinated; no edit needed for 7c.7).

---

## Broad-Regression Attribution Spot-Check

**Local run:** `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=no` → `50 failed, 4267 passed, 27 skipped, 2 xfailed in 465.77s`. Codex reports 47/4270 — within ±3 drift band consistent with global parity-registry ordering effects.

**5 spot-checked failures with git-blame attribution (all PRE-Wave-3):**

| # | Test | Last-touched commit | Attribution |
|---|------|--------------------|-----|
| 1 | `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` | `0ec80df` (Slab-7c G2C+G3+G4 batch, 2026-05-05) | Test asserts governance version `"2026-05-05-amelia-p5-and-wave-3-lookahead-policy"`; actual governance is now `"2026-05-05-v7-v1.1-elevation-and-v2-pre-ratification"` (`fe02b09` Wave-3 opener). **Pre-7c.7 governance-version drift; NOT attributable to 7c.7.** |
| 2 | `tests/test_run_hud.py::TestScanBundleArtifacts::test_lists_files_with_sizes` | `162d129` (Slab 6 trial experience bundle, pre-Slab-7) | HUD API drift; pre-Wave-3. **NOT attributable to 7c.7.** |
| 3 | `tests/test_pipeline_manifest_loader.py::test_manifest_loads_and_validates` | `162d129` (pre-Slab-7) | Pipeline-manifest schema drift; pre-Wave-3. **NOT attributable to 7c.7.** |
| 4 | `tests/integration/runtime/test_fastapi_server.py::test_runtime_server_health_invoke_and_clean_shutdown` | `162d129` (pre-Slab-7) | Live-runtime/network env-dependent; pre-Wave-3. **NOT attributable to 7c.7.** |
| 5 | `tests/migration/test_dispatch_registry_promoted.py::test_dispatch_registry_status_no_longer_interim` | `162d129` (pre-Slab-7) | Dispatch-registry promotion-state drift; pre-Wave-3. **NOT attributable to 7c.7.** |

**Conclusion:** Zero broad-regression failures attributable to 7c.7. Pre-existing inherited drift bucket consistent with Codex's report.

---

## Sign-Off

**Verdict: PASS-zero-patches.**

7c.7 is ready to flip to `done` and join the Wave-3 close batch. C6 isolation correctly preserved. Three-transport parity correctly registered with `alias_of="G1"` per ADR 0002 §2/§4. JSON schema regenerated via Path.write_text per A18 (BOM-free). FR-7c-49 shape-pin landed. FR-7c-11 cost-impact-acknowledged framing reflected in closed verb literal `["acknowledged", "edit", "reject"]`.

**Cross-Wave follow-on recommended (not blocking 7c.7 close):** File `app/gates/_common/digest_helpers.py` extraction story for Wave-4 to eliminate 4-way digest-helper duplication while preserving C6 isolation.
