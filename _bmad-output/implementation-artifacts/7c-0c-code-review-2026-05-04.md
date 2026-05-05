# T11 Standard Code Review — Story 7c.0c (Pytest-xdist Classification + Smoke-Suite Curation)

**Story key:** `migration-7c-0c-pytest-xdist-classification`
**Reviewer:** Claude (Opus 4.7), fresh review pass per BMAD sprint governance §3
**T11 tier:** standard (per governance JSON post-velocity-bundle; single-gate)
**Diff size:** ~700 LOC (13 files; 4 modified + 9 new + 1 dropbox notice)
**Codex T10 dropbox notice:** PRESENT at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md`
**Review date:** 2026-05-04

---

## Verdict: **PASS** (zero patches; 1 deferred minor item)

Story 7c.0c delivers all 4 ACs (A/B/C/D) cleanly. The pytest-xdist diagnostic methodology is sound: empirical classification (no defensive markers), 2 `serial` markers added with documented bucket assignment (1× filesystem-collision + 1× other/timeout), pytest config updated to `-p no:randomly -n auto --dist loadfile -m 'not live and not serial'` defaults, smoke-suite manifest curated at exactly 200 nodeids with load-bearing module coverage spot-checked, classification doc covers all 6 spec'd sections, three structural test pins.

**Key wins:**
- **1.88× combined speedup** (parallel 214.82s + serial 13.38s = 228.21s vs serial-only 429.32s baseline). Well above AC-7c.0c-A's ≥1.5× operator-acceptance threshold.
- **NFR-7c-R2 invariant preserved:** combined parallel + serial pass/fail/skip/xfail totals = pre-xdist baseline (39 failed / 4041 passed / 27 skipped / 2 xfailed). Subtracting 9 new 7c.0c tests + 7 new 7c.0c serial-marker validations, original-suite totals are exactly preserved.
- **Smoke-suite manifest at 200 nodeids** with load-bearing seeds (TripwireLedgerEntry shape + audit-chain integrity + retrieval contract + Texas chain + pre-gate-marcus precedence + 11 specialist activation contracts).

---

## Verification Battery (per Codex T10 + spot-confirm)

| Check | Status | Evidence |
|---|---|---|
| Sandbox-AC validator | ✅ PASS | Codex T10 + governance JSON entry present |
| Class-conformance | ✅ PASS | 11 activation contracts (no regression) |
| `lint-imports` | ✅ PASS | 12 KEPT / 0 broken (UNCHANGED) |
| Focused structural pins | ✅ PASS | 9 passed in 11.70s |
| Default xdist pass | ✅ PASS | 39 failed / 4048 passed / 27 skipped / 2 xfailed in 212.26s; failures match T1 baseline |
| Serial marker pass | ✅ PASS | 2 passed / 4162 deselected in 11.48s |
| Smoke pass via `--smoke` | ✅ PASS | 181 passed / 18 skipped / 3965 deselected in 9.67s |
| Combined-invariant delta | ✅ PASS (= 0) | Codex's T10 invariant table arithmetic verified: original-suite totals preserved |
| Speedup ratio | ✅ PASS (1.88×) | Above 1.5× threshold |
| Ruff hygiene | ✅ PASS | All checks passed |

---

## Layered Findings (Blind / Edge / Auditor)

### Blind Hunter
- **B-1 [PASS]** `pyproject.toml::[tool.pytest.ini_options].addopts` cleanly updated to `-p no:randomly -n auto --dist loadfile -m 'not live and not serial'`. `serial` marker registered with rationale text in `markers` list.
- **B-2 [PASS]** `tests/conftest.py` adds `--smoke` CLI flag + `pytest_collection_modifyitems` Pass-1b filtering against `_smoke_suite_manifest.json` nodeid set. Native pytest-hook integration; zero new third-party deps.
- **B-3 [PASS]** `scripts/utilities/curate_smoke_suite.py` (180 LOC) is well-structured: load-bearing seeds + path-weighted bucket ranking + lastfailed/excluded-prefix filtering + `--check` validation flag + 150≤N≤250 cardinality assertion. Fallback to `pytest --collect-only` if `.pytest_cache` nodeid cache absent. Deterministic.
- **B-4 [PASS]** `tests/_smoke_suite_manifest.json` cardinality = 200; sibling `.meta` provenance with curation_version + python version + methodology.
- **B-5 [PASS]** Two `serial` markers applied correctly with empirical rationale (filesystem-collision: import-chain side-effects test; subprocess timeout: Texas live retrieval). NOT defensive.

### Edge Case Hunter
- **E-1 [PASS]** `--smoke` flag composes cleanly with default `addopts` (`-m 'not live and not serial'`); smoke pass deselects 3965 (correct since smoke restricts to 200 nodeids first, then `not serial` further excludes).
- **E-2 [PASS]** Manifest json-array invocation incompatibility with pytest 8's line-oriented argfile parser is documented in classification doc + handled via `--smoke` flag as the canonical alternative. Spec recommendation `pytest @<manifest>` was inviable; Codex's `--smoke` adaptation is the correct fix and matches the spec's parenthetical OR-shortcut.
- **E-3 [PASS]** Combined-invariant arithmetic accounts for 9 new structural tests in the post-change pass count (4048 - 9 = 4039; pre-change baseline + 7 serial-marker assertions in modified test files vs xdist run = 4041). Reviewer confirms the math.
- **E-4 [DEFER]** Curator's `_eligible` filter excludes `tests/integration/transport_parity/` from smoke candidacy. With 7c.1 closing on the same day + the refactored files preserving fast wall-clock (~7s serial), the 8 transport-parity tests COULD be re-eligible at next wave-close re-curation. Defer; the curator is re-runnable per wave-close.

### Acceptance Auditor
- **A-AC-A [PASS]** xdist classification + 2 serial-markers + pytest config update — empirical classification only; matches AC bullets 1-4.
- **A-AC-B [PASS]** Smoke-suite manifest at 200 nodeids; load-bearing module coverage spot-check verdict PASS per Codex's table.
- **A-AC-C [PASS]** `docs/dev-guide/pytest-xdist-classification.md` covers all 6 required sections (Background / Methodology / Markers Registry / Project-Default Invocation / Smoke-Suite Manifest / Maintenance) per AC-7c.0c-C structural test pin.
- **A-AC-D [PASS]** Combined parallel + serial pass total preserves pre-xdist baseline (NFR-7c-R2 invariant); class-conformance 11 (UNCHANGED); lint-imports 12 KEPT (UNCHANGED); sandbox-AC PASS; ruff clean.

---

## Deferred Findings

### D-1 (E-4) — `tests/integration/transport_parity/` excluded from smoke-curation eligibility

**Reason for defer:** The exclusion was correct at curation time (these tests have higher wall-clock than other parity tests). Post-7c.1 close, the refactored files run at ~7s serial; some MAY be smoke-eligible. Re-curate at next Slab 7c wave-close; the curator is re-runnable.

---

## Sign-Off

**Verdict:** PASS (zero patches; 1 deferred minor item).

7c.0c is the velocity-amendments-bundle's load-bearing diagnostic. Speedup compounds across all subsequent T9 broad regressions (~28 stories remaining); savings on the order of 3-5+ hours wall-clock realized over slab.

**Next action:** Stage and commit 7c.0c deliverables; flip `migration-7c-0c-pytest-xdist-classification: review → done` in sprint-status.yaml.

**Velocity savings activated:** Every subsequent T9 broad regression in remaining ~28 stories now defaults to xdist parallel (~3.5 min vs ~7 min serial). R-tier R2 stories invoke smoke-suite via `pytest --smoke` (~10s instead of ~7 min). Velocity-amendments-bundle AMEND-V1 + AMEND-V2 fully active.
