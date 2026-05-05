# Migration Story 7c.0c: Pytest-xdist Classification + Smoke-Suite Curation (Velocity-Amendment Diagnostic)

**Status:** ready-for-dev *(spec authored 2026-05-04; **DISPATCH HELD until predecessor 7c.0b closes** per governance JSON `prerequisite_stories: [7c-0b]`. Dispatched IMMEDIATELY after 7c.0b closes — AHEAD OF 7c.4a per highest amortization leverage; xdist + smoke-suite gains amortize across ALL subsequent T9 runs in the slab.)*
**Sprint key:** `migration-7c-0c-pytest-xdist-classification`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 3
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-velocity-amendments-bundle, story 7c-0c; rationale: null — diagnostic + governance configuration; no schema/contract/lane-boundary/invariant-preservation surface)
**K-target:** ~1.2× (diagnostic-tier; ~3 pts; bounded surface = pytest.ini + pyproject.toml flag-config + serial markers + smoke-suite manifest curation script + documentation)
**R-tier (regression scope):** **R3** — diagnostic against the FULL suite IS the deliverable; full broad regression is not a verification-add but the work-product itself.
**T11-tier (review approach):** **standard** — single-gate but cross-cutting (touches pytest invocation defaults for the whole project); needs a 3-layer review pass.
**Files touched (declared at spec-author time):**
- `pytest.ini` (NEW or extend; project-wide pytest defaults)
- `pyproject.toml` (potentially `[tool.pytest.ini_options]` if pytest config lives there instead of `pytest.ini`; verify at T1)
- `tests/_smoke_suite_manifest.json` (NEW; ~200-test curated manifest for R-tier R2)
- `scripts/utilities/curate_smoke_suite.py` (NEW; helper script that curates the smoke-suite manifest from `--durations=0 --cov` data)
- `docs/dev-guide/pytest-xdist-classification.md` (NEW; documents safe parallel invocation + classification methodology)
- Various test files: zero or more `@pytest.mark.serial` markers added on classified non-parallel-safe tests (touched at minimum-necessary scope; expected ≤30 markers based on Murat's risk model)
**Lookahead tier:** **1** — author-ahead-aggressively (diagnostic-shape; depends only on stable substrate; PRD-not-required since this is a velocity-amendment-derived governance story).
**Authored:** 2026-05-04 via velocity-amendments-bundle AMEND-V1 dispatch.
**Wave:** 0 — slot 3 (diagnostic; consumes 7c.0a + 7c.0b; precedes Wave 1 dispatch).

**FR coverage:** None direct (governance/diagnostic story; not a feature delivery). Enables NFR-7c-P3 (parity-test wall-clock budget) by reducing per-T9 cost across remaining stories.

**NFR coverage:** **NFR-7c-P3** (parity-test ≤90s @ ~15-cell scale; ≤6 min @ ~68-cell post-Slab-7c) — xdist parallelism contributes to staying under that ceiling at ~68-cell scale. **NFR-7c-R2** (≥1403 deterministic baseline at `-p no:randomly`) — the diagnostic VERIFIES this baseline is preserved under xdist (via `serial` marker on RNG-coupled tests) before adoption. **NFR-7c-M5** sandbox-AC validator PASS.

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged (governance-tier; no functional surface).

**Tripwire ownership:** none — diagnostic story doesn't OWN any tripwire firing; it ENABLES TW-7c-6 (parity flake) detection by improving the per-cell flake-rate calculator's data quality (post-xdist, faster runs mean more samples per unit time).

**Implementation cycle (NEW CYCLE):**
- **Claude (Opus 4.7):** authored this spec 2026-05-04; sandbox-AC validator PASS; governance JSON entry added at velocity-amendments-bundle commit; pre-authors `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-0c-pytest-xdist-classification.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops the diagnostic + classification + smoke-suite curation per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md`.
- **Claude T11 standard review:** verifies the classification is sound, the serial-markers are correctly applied, the smoke-suite manifest covers load-bearing modules, and the post-adoption verification battery still preserves NFR-7c-R2 (≥1403 deterministic baseline). Commits + flips `migration-7c-0c-pytest-xdist-classification: review → done`.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — AMEND-V1 + AMEND-V2 source spec; this story's deliverables are the V1+V2 enabling work.
- `docs/dev-guide/migration-story-governance.json::r_tier_legend` + `t11_tier_legend` — the conventions this story enables for downstream.
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability still applies.

**Predecessor state (verified at dispatch time):**
- 7c.0a `done` (commit f926867).
- 7c.0b `done` (review verdict landed at `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-NN.md`).
- Governance JSON at version `2026-05-04-velocity-amendments-bundle` or later.
- Class-conformance: 11 conforming activation contracts (post-7c.0b should be ≥11; verify at T1).
- Broad-regression baseline (serial): ~3990 passed / 37 failed pre-existing (per 7c.0a + 7c.2 close-time evidence; refresh at T1 against current state).

**Live substrate (verified at T1):**
- Existing pytest invocation: `pytest -p no:randomly` — the `-p no:randomly` plugin disables random test ordering and is critical for the NFR-7c-R2 1403 deterministic baseline. xdist adoption MUST preserve this.
- `pytest.ini` (project root) OR `[tool.pytest.ini_options]` in `pyproject.toml` — verify which holds the canonical config; both can carry `addopts`.
- pytest-xdist availability: check `pyproject.toml` dev-deps + `.venv/Lib/site-packages/xdist/` for installation. If absent, T1 surfaces as `decision_needed` (pip install requirement).
- Test count baseline: ~4054 collected (3990 passed + 27 skipped + 37 failed pre-existing); diagnostic against this exact count.

**Gate-mode rationale (from governance JSON):** single-gate; diagnostic + governance config; not a feature delivery; no schema/contract risk surface; standard T11 review sufficient.

**T1 conclusion:** No unanticipated architectural disagreement. Implementation proceeds: full-suite xdist run + classification + serial-markers + pytest config update + smoke-suite manifest curation + documentation. **Hard checkpoints at T1:** (a) 7c.0a + 7c.0b both `done`; (b) pytest-xdist installed in `.venv` (if absent, surface as `decision_needed`); (c) verify `pytest.ini` vs `pyproject.toml` canonical config location; (d) refresh broad-regression baseline against current HEAD before xdist run (so the comparison is HEAD-stable).

---

## Story

As the velocity-amendment governance owner (and as Codex, who runs broad regression at every T9),
I want pytest-xdist parallelism classified, validated, and adopted as the project default WHILE preserving the NFR-7c-R2 ≥1403 deterministic baseline, AND a curated ~200-test smoke-suite manifest at `tests/_smoke_suite_manifest.json` enabling R-tier R2 regression scope,
so that every subsequent Slab 7c story's T9 broad regression cost reduces from ~7 min serial to ~2-4 min parallel (multiplicative speedup), AND R2-eligible stories run a 2-3 min smoke pass instead of the 7 min full pass — compounding to ~5-8 hrs wall-clock saved across the remaining 30 stories.

---

## Acceptance Criteria

### AC-7c.0c-A — pytest-xdist classification + serial-marker application + project-wide config update (AMEND-V1 deliverable)

**Given** the current pytest baseline (`pytest -p no:randomly` serial; ~3990 passed / 37 failed pre-existing / 27 skipped / 46 deselected / 2 xfailed at ~7 min wall-clock)
**When** the dev-agent runs `pytest -n auto --dist loadfile -p no:randomly` against the full suite
**Then** the dev-agent records:
1. Wall-clock delta vs serial baseline.
2. Pass/fail/skip count delta (the serial baseline is the source of truth for the ≥1403 invariant per NFR-7c-R2; xdist adoption MUST preserve total pass count).
3. For each test that fails under xdist but passes serial, classification into ONE of:
   - **DB-shared-state** (PostgreSQL fixture sharing schema/table without per-worker isolation)
   - **Filesystem collisions** (tests writing to fixed path like `/tmp/foo` or `_bmad-output/` without `tmp_path` fixture)
   - **Port-binding** (httpx test servers, LangSmith mock endpoints, MCP transport ports)
   - **LangSmith trace coupling** (tests asserting on global tracer state)
   - **Random-seed coupling** (tests sharing global RNG state — likely contributes to NFR-7c-R2 invariant)
   - **Other** (document with hypothesis + evidence)

**And** every test classified above receives `@pytest.mark.serial` decorator (or class-level marker for test-class groupings); the marker is registered in `pytest.ini` (or `pyproject.toml::[tool.pytest.ini_options]`):

```ini
# pytest.ini OR pyproject.toml::[tool.pytest.ini_options]
markers =
    serial: marks tests that cannot run under xdist parallelism (DB-state / FS / port / LangSmith / RNG coupling); run with -m "serial" -n0
addopts = -p no:randomly -n auto --dist loadfile -m "not serial"
```

**And** the post-classification verification is **two passes**:
1. **Parallel pass:** `pytest -n auto --dist loadfile -p no:randomly -m "not serial"` — runs the parallel-safe subset.
2. **Serial pass:** `pytest -n0 -p no:randomly -m "serial"` — runs the serial-marked subset.
3. **Combined result:** total passed/failed/skipped MUST match the pre-xdist serial baseline (delta = 0). Any deviation surfaces as `decision_needed` at T10.

**And** wall-clock measurement: parallel pass + serial pass combined wall-clock should be substantially below the original ~7 min serial-only baseline. Recommend reporting ratio (e.g., "7 min → 3.2 min = 2.2× speedup"); operator-acceptance threshold for adoption is **at least 1.5× speedup** on the operator's current hardware. If speedup < 1.5×, surface as `decision_needed` (xdist adoption may not be worth the maintenance overhead; rolling back is the alternative).

**Test pin:** `tests/structural/test_pytest_xdist_config_present.py` — asserts (a) `markers.serial` registered in pytest config; (b) `addopts` contains `-n auto --dist loadfile -m "not serial"` OR an equivalent default; (c) any test file marked `@pytest.mark.serial` is acknowledged in `docs/dev-guide/pytest-xdist-classification.md` Markers section (cross-reference check).

> **Notes for 7c.0c-A.** This AC is **dev-agent-executable** (pytest + marker authoring + config edit). The classification work is empirical — Codex runs the diagnostic, captures the failures, classifies each. Murat's risk model anticipates ~5-30 tests need `serial` marker; >100 markers is a flag to surface (high state-coupling indicates xdist adoption ROI shrinks).

### AC-7c.0c-B — Curated ~200-test smoke-suite manifest at `tests/_smoke_suite_manifest.json` (AMEND-V2 R-tier R2 enabler)

**Given** the AMEND-V2 R-tier convention (R2 = focused + impact-zone + cross-cutting smoke; ~2-3 min wall-clock at ~200 tests)
**When** the dev-agent curates the smoke-suite manifest
**Then** the manifest at `tests/_smoke_suite_manifest.json` contains a JSON array of test-node-ids (full pytest node-id format; e.g., `"tests/parity/test_tripwire_ledger_entry_shape.py::test_validate_assignment_true_rejects_invalid_mutation"`) with:
1. **Cardinality:** ≥150, ≤250 (target ~200; gives ~2-3 min wall-clock under post-xdist parallelism).
2. **Coverage of load-bearing modules** (sanity-check by Codex):
   - Substrate-shape: `app/models/decision_cards/`, `app/models/tripwire_ledger.py`, `app/models/state/run_state.py`, `app/models/operator_verdict.py`
   - Retrieval contract: Texas wrangler / retrieval providers (per `skills/bmad-agent-texas/references/retrieval-contract.md`)
   - Party-mode loop / gate-loop kernel: `app/marcus/orchestrator/`, `app/gates/`
   - Schema validators (Pydantic-v2 idiom enforcement): `tests/parity/test_*_shape.py`
   - Class-conformance: existing 11 activation contract tests
3. **Curation methodology** (canonical; documented in helper script `scripts/utilities/curate_smoke_suite.py`):
   - Run `pytest --durations=0 --co --cov=app --cov-report=json` against full suite (collect-only with coverage data).
   - Score each test by (covered-lines × not-already-covered) / wall-clock. Rank descending.
   - Take top-200 by score. Verify load-bearing-module coverage by manual inspection (Codex's T10 self-review acknowledges coverage check).
   - Emit JSON array. Include manifest-generation timestamp + tool-versions in a sibling `tests/_smoke_suite_manifest.json.meta` file for reproducibility.

**And** the manifest is invokable via:
```bash
.venv/Scripts/python.exe -m pytest @tests/_smoke_suite_manifest.json -p no:randomly -q --tb=short
# Or via the curated wrapper:
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
```

(The `--smoke` shortcut is OPTIONAL; recommend implementing if `pytest-pickled-plugin` shape is already in the project, OTHERWISE use the `@<file>` arg-file syntax which is pytest-native and zero-dep.)

**Test pin:** `tests/structural/test_smoke_suite_manifest_present.py` — asserts (a) `tests/_smoke_suite_manifest.json` exists and parses as JSON array; (b) cardinality 150≤N≤250; (c) every entry is a valid pytest node-id pointing to an existing test (resolves via `pytest --collect-only @<manifest>`); (d) the manifest is invokable end-to-end (run smoke; assert exit 0 OR document any pre-existing red tests in the manifest with `--ignore-pre-existing-fails`).

> **Notes for 7c.0c-B.** This AC is **dev-agent-executable**. The manifest is data, not code. Re-curation cadence: recommend re-running the curator script at every Wave-close (Wave 1 close, Wave 2 close, etc.) so the smoke-suite reflects added coverage. Document this cadence in the helper script's docstring.

### AC-7c.0c-C — Documentation: `docs/dev-guide/pytest-xdist-classification.md` (AMEND-V1 + AMEND-V2 reference)

**Given** AC-A + AC-B deliverables landed
**When** the dev-agent authors `docs/dev-guide/pytest-xdist-classification.md`
**Then** the doc contains the following sections:
1. **Background.** Why xdist; NFR-7c-R2 invariant preservation; AMEND-V1 source spec link.
2. **Classification methodology.** The 5-bucket failure-mode taxonomy from AC-A; how to apply `@pytest.mark.serial` to new tests in future stories.
3. **Markers registry.** List every test file (or test class / test function) that carries `@pytest.mark.serial`; for each, the failure-mode bucket + 1-line rationale.
4. **Project-default invocation.** Documented `addopts` line; commands for parallel pass + serial pass + smoke pass + full pass.
5. **Smoke-suite manifest.** AMEND-V2 R-tier R2 convention; manifest path; re-curation cadence; coverage validation.
6. **Maintenance.** When a new story adds tests: how to determine if `serial` marker is needed (default: do NOT mark unless empirical xdist failure observed); how to re-curate smoke-suite at Wave-close.

**Test pin:** `tests/structural/test_pytest_xdist_classification_doc_present.py` — asserts the file exists + contains all 6 section keywords + cross-references the velocity-amendments-2026-05-04.md artifact.

> **Notes for 7c.0c-C.** Dev-agent-executable markdown authoring. Doc is the authoritative reference for downstream stories.

### AC-7c.0c-D — Verification battery: post-adoption broad regression matches pre-xdist baseline (NFR-7c-R2 invariant)

**Given** AC-A + AC-B + AC-C landed and the new pytest defaults are in `pytest.ini` (or `pyproject.toml::[tool.pytest.ini_options]`)
**When** the dev-agent runs the FULL VERIFICATION BATTERY at T9:

```bash
# Parallel pass (default):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Serial pass:
.venv/Scripts/python.exe -m pytest -n0 -p no:randomly -m "serial" -q --tb=line

# Smoke pass (sanity):
.venv/Scripts/python.exe -m pytest @tests/_smoke_suite_manifest.json -p no:randomly -q --tb=short

# Class-conformance:
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Lint-imports:
.venv/Scripts/lint-imports.exe

# Sandbox-AC:
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0c-pytest-xdist-classification.md

# Ruff:
.venv/Scripts/python.exe -m ruff check pytest.ini pyproject.toml scripts/utilities/curate_smoke_suite.py tests/structural/test_pytest_xdist_config_present.py tests/structural/test_smoke_suite_manifest_present.py tests/structural/test_pytest_xdist_classification_doc_present.py
```

**Then** the combined parallel + serial pass produces the SAME pass/fail/skip totals as the pre-xdist serial baseline (delta = 0; or any delta is documented as a NEW pre-existing failure unrelated to xdist). Specifically:
- ≥1403 deterministic baseline (NFR-7c-R2) preserved.
- 37 pre-existing failures unchanged (or fewer; never more).
- Class-conformance: 11 activation contracts (no regression).
- Lint-imports: 12 KEPT (or higher if 7c.0b populated more contracts; no contract demotion).

**And** the wall-clock report (parallel + serial + smoke) is recorded in the Codex T10 self-review notice + the `pytest-xdist-classification.md` doc Markers section; operator-acceptance threshold for adoption = **at least 1.5× combined speedup vs serial-only ~7 min baseline**.

> **Notes for 7c.0c-D.** Dev-agent-executable. The combined-pass invariant is non-negotiable: if combined parallel + serial pass total ≠ serial-only baseline, surface as HALT-AND-SURFACE for operator decision (rollback xdist adoption OR investigate the divergent test).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.0a + 7c.0b both `done`.
  - [ ] T1.2 Confirm pytest-xdist installed in `.venv`; if absent, surface `decision_needed` (operator decides: install or scrap V1).
  - [ ] T1.3 Verify canonical pytest config location (`pytest.ini` vs `pyproject.toml::[tool.pytest.ini_options]`); pick the existing one for consistency.
  - [ ] T1.4 Refresh broad-regression baseline at current HEAD: `pytest -p no:randomly -q --tb=no` → record total pass/fail/skip counts as the comparison baseline.
  - [ ] T1.5 Run sandbox-AC validator on this spec; expect PASS.

- [ ] **T2 — Run xdist classification diagnostic (AC: 7c.0c-A)**
  - [ ] T2.1 Run `pytest -n auto --dist loadfile -p no:randomly -q --tb=line` against full suite; capture output.
  - [ ] T2.2 For each test that fails under xdist but passed serial (per T1.4 baseline), classify into 5-bucket taxonomy.
  - [ ] T2.3 Apply `@pytest.mark.serial` markers (or class-level / function-level as appropriate) to classified tests.
  - [ ] T2.4 Register `serial` marker in pytest config; update `addopts` to default-parallel-with-serial-exclusion.

- [ ] **T3 — Curate smoke-suite manifest (AC: 7c.0c-B)**
  - [ ] T3.1 Author `scripts/utilities/curate_smoke_suite.py` with the canonical curation methodology.
  - [ ] T3.2 Run the curator against current full suite; emit `tests/_smoke_suite_manifest.json` + sibling `.meta`.
  - [ ] T3.3 Sanity-check coverage by spot-reading the manifest for substrate-shape / retrieval / party-mode / gate-loop / schema-validator entries.
  - [ ] T3.4 Smoke-pass test: `.venv/Scripts/python.exe -m pytest @tests/_smoke_suite_manifest.json -p no:randomly -q --tb=short` exits 0 (or has documented pre-existing reds).

- [ ] **T4 — Author documentation (AC: 7c.0c-C)**
  - [ ] T4.1 `docs/dev-guide/pytest-xdist-classification.md` with all 6 sections per AC.
  - [ ] T4.2 Markers registry section enumerates every classified test + bucket + rationale.
  - [ ] T4.3 Cross-reference link to `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md`.

- [ ] **T5 — Author 3 structural tests (AC: 7c.0c-A + 7c.0c-B + 7c.0c-C test pins)**
  - [ ] T5.1 `tests/structural/test_pytest_xdist_config_present.py`.
  - [ ] T5.2 `tests/structural/test_smoke_suite_manifest_present.py`.
  - [ ] T5.3 `tests/structural/test_pytest_xdist_classification_doc_present.py`.

- [ ] **T6 — Combined verification battery (AC: 7c.0c-D)**
  - [ ] T6.1 Parallel pass + serial pass; assert combined total = T1.4 baseline.
  - [ ] T6.2 Smoke pass; assert exit 0 or document.
  - [ ] T6.3 Class-conformance: 11 activation contracts.
  - [ ] T6.4 Lint-imports: KEPT count unchanged or higher.
  - [ ] T6.5 Sandbox-AC: PASS.
  - [ ] T6.6 Ruff: clean.
  - [ ] T6.7 Wall-clock report: parallel + serial + smoke times; acceptance = ≥1.5× combined speedup.

- [ ] **T10 — Codex self-review (NEW CYCLE T10)**
  - [ ] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md` summarizing: file list (~7 NEW + 2 modified config + ≤30 test files with new markers), full classification table (test-name + bucket + rationale), wall-clock report, smoke-suite cardinality + coverage spot-check, T1 `decision_needed` resolutions.

- [ ] **T11 — Claude `bmad-code-review` (single-gate; standard tier)**
  - [ ] T11.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the diff; produces verdict at `_bmad-output/implementation-artifacts/7c-0c-code-review-2026-05-NN.md`; applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-0c-pytest-xdist-classification: review → done`.

---

## Dev Notes

**Why this story exists:** AMEND-V1 + AMEND-V2 deliverables from velocity-amendments-bundle 2026-05-04. Pytest cost reduction is the dominant velocity lever per party-mode consultation (Murat: "5+ hours of regression on the critical path"; Winston: "single biggest fixed cost in the budget"). This diagnostic story unlocks both the parallelism (V1) and the smoke-suite tier (V2 R2).

**Why dispatch ahead of 7c.4a:** highest amortization leverage. Every subsequent T9 broad regression in remaining 30 stories benefits from xdist + R2 smoke-suite. 7c.4a is decision-only ADR (~1pt; R1; lite review); deferring 7c.4a by ~1 dispatch cycle costs nothing, but landing 7c.0c first compounds pytest savings across all downstream stories.

**Murat's risk model (party-mode 2026-05-04):**
- 4-core box: 7 min → 3-4 min (~50% reduction)
- 8-core box: 7 min → 2 min (~70% reduction)
- Risk: NFR-7c-R2 ≥1403 deterministic baseline relies on test ordering; xdist adoption MUST preserve via `serial` marker.
- Skepticism: "If diagnostic finds >100 tests need `serial` marker, ROI shrinks." If T2 classification surfaces >100 markers, surface for re-evaluation; xdist may not be net-positive.

**File / module placement:**
- `pytest.ini` OR `pyproject.toml::[tool.pytest.ini_options]` (verify at T1.3).
- `tests/_smoke_suite_manifest.json` + sibling `.meta` (NEW; manifest is data; meta is provenance).
- `scripts/utilities/curate_smoke_suite.py` (NEW; curator helper).
- `docs/dev-guide/pytest-xdist-classification.md` (NEW; reference).
- 3 structural tests under `tests/structural/`.
- `@pytest.mark.serial` markers added in-place on classified tests (≤30 expected).

**Anti-patterns to avoid:**
- **Over-marking serial:** if you can't reproduce a specific xdist failure, do NOT mark `serial` defensively. Marker should reflect empirical evidence of state-coupling.
- **Smoke-suite cherry-picking:** don't manually pick "important-feeling" tests; trust the coverage-per-second curation. Override the curator's ranking only with documented rationale (e.g., "added test_retrieval_contract_invariant manually because it covers the Texas wrangler contract not yet hit by curator's ranking" + ranking explanation).
- **A11 Windows-portability:** all new files UTF-8-encoded; `pathlib.Path.as_posix()` for path strings in scripts.

**K-discipline:**
- K-target 1.2× = ~2.4K LOC ceiling. Documentation ~500-800 LOC; classification table ~200-400 LOC; pytest config ~30 LOC; curator script ~150 LOC; 3 structural tests ~100 LOC each; ≤30 test files with marker additions ~30-60 LOC total. Estimate: ~1.4-2.0K LOC. Comfortable.
- If T2 classification surfaces >100 markers OR T3 curation requires deep coverage rebalancing, surface for K-budget renegotiation.

### Project Structure Notes

- **Alignment with unified project structure:** all new file paths conform to existing conventions. Marker registration in pytest config matches existing pattern. Smoke-suite manifest is a new file but conceptually follows the existing `tests/parity/` parametrize-fixture pattern.
- **Detected variances:** none anticipated; T1.3 verifies pytest config location.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-0c]
- [Source: _bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md] (AMEND-V1 + AMEND-V2 source)
- [Source: docs/dev-guide/migration-story-governance.json#r_tier_legend + #t11_tier_legend + #lookahead_tier_legend + #velocity_amendment_record]
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 Windows-portability)
- [Source: NFR-7c-R2 1403 deterministic baseline at -p no:randomly] (preserved invariant)
- [Source: NFR-7c-P3 parity-test wall-clock budget] (this story enables the budget)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

(Populated during dev round.)

### Completion Notes List

(Populated during dev round; MUST include classification table + wall-clock report + serial-marker count + smoke-suite cardinality + coverage spot-check verdict.)

### File List

(Populated during dev round; expected: ~7 NEW files + 2 MODIFIED config + ≤30 test files with marker additions. Net: ~1.4-2.0K LOC.)
