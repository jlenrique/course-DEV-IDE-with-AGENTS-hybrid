# Codex dev-story prompt — Story 7c.0c (pytest-xdist classification + smoke-suite curation; AMEND-V1+V2 diagnostic)

**Cycle:** Claude spec → Codex T1-T6 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 0 slot 3 (diagnostic; consumes 7c.0a + 7c.0b; precedes Wave 1 dispatch).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline + `feedback_velocity_amendments_slab_7c.md` lookahead Tier 1.
**Dispatch state:** **DISPATCH HELD until 7c.0b closes.** Once 7c.0b closes, DISPATCH 7c.0c IMMEDIATELY (ahead of 7c.4a) per highest-amortization-leverage rationale: every subsequent T9 broad regression in remaining ~30 stories benefits from xdist + R2 smoke-suite. AMELIA-P2 freshness check at dispatch.

---

```
Run bmad-dev-story on Story 7c.0c (Slab 7c Wave 0 slot 3; single-gate; AMEND-V1+V2 diagnostic = pytest-xdist classification + smoke-suite curation + project-default config).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-0c-pytest-xdist-classification.md` (status: ready-for-dev; 4 ACs A-D; 6 task groups T1-T6 + T10/T11).
2. **Velocity-amendments artifact:** `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — AMEND-V1 + AMEND-V2 source spec; this story's deliverables ARE V1+V2 enabling work.
3. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-0c` (single-gate; expected_pts=3; expected_k_target=1.2; r_tier=R3; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-0b]).
4. Governance legends: `r_tier_legend` + `t11_tier_legend` + `lookahead_tier_legend` (your story enables R2 for downstream — your `tests/_smoke_suite_manifest.json` is what R2 invokes).
5. NFR-7c-R2 invariant: ≥1403 deterministic baseline at `-p no:randomly`. Adoption of xdist MUST preserve this; serial-marker is the mechanism.
6. NFR-7c-P3 wall-clock budget: parity-test ≤90s @ ~15-cell scale; ≤6 min @ ~68-cell scale post-Slab-7c. xdist contributes to ceiling preservation.
7. Required readings:
   - `docs/dev-guide/story-cycle-efficiency.md` (K-discipline 1.2x).
   - `docs/dev-guide/dev-agent-anti-patterns.md` (A11 Windows-portability still applies).
8. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.0a + 7c.0b both `done` in spec files + sprint-status.yaml. **Both must be TRUE before T1 begins** (predecessor chain).
- `pytest-xdist` is installed in `.venv`. Check via `.venv/Scripts/python.exe -c "import xdist; print(xdist.__version__)"`. If absent → surface `decision_needed` (operator decides: install via `uv pip install pytest-xdist` and proceed, OR scrap V1 and accept current 7-min broad regression cost).
- Canonical pytest config location: `pytest.ini` OR `pyproject.toml::[tool.pytest.ini_options]`. Pick the existing one for consistency. If both exist, surface `decision_needed`.
- Refresh broad-regression baseline at current HEAD: `pytest -p no:randomly -q --tb=no` → record total pass/fail/skip/xfail counts. THIS is the comparison baseline for T6 verification, not the 2026-05-04 7c.0a-close baseline (which may have drifted).
- Class-conformance currently reports 11 conforming activation contracts (or higher post-7c.0b; refresh).

## Files in scope

**New (~7 files):**
- `pytest.ini` (NEW or extend if exists; project-wide pytest defaults)
   OR equivalent change to `pyproject.toml::[tool.pytest.ini_options]` if that's the canonical location.
- `tests/_smoke_suite_manifest.json` (NEW; ~150-250 test-node-ids; target ~200).
- `tests/_smoke_suite_manifest.json.meta` (NEW sibling; provenance: timestamp + tool versions + curation-script-version).
- `scripts/utilities/curate_smoke_suite.py` (NEW; curator helper script).
- `docs/dev-guide/pytest-xdist-classification.md` (NEW; reference doc with 6 sections).
- `tests/structural/test_pytest_xdist_config_present.py` (NEW; structural test).
- `tests/structural/test_smoke_suite_manifest_present.py` (NEW; structural test).
- `tests/structural/test_pytest_xdist_classification_doc_present.py` (NEW; structural test).

**Modified:**
- `pytest.ini` OR `pyproject.toml` (config addition for `markers.serial` + `addopts` defaults).
- ≤30 test files (expected) with `@pytest.mark.serial` decorator additions on classified non-parallel-safe tests.

**Do NOT modify:**
- Any specialist body (`app/specialists/**`).
- Any HIL surface module (`app/gates/**`).
- 7c.0a's ADR (`docs/dev-guide/adr/0001-parity-contract-dsl.md` — read only).
- 7c.0a's TripwireLedgerEntry (`app/models/tripwire_ledger.py` — read only).
- 7c.0b's deliverables (`app/parity/contracts/`, `app/audit/`, `tests/audit/` — read only).
- Existing test BUSINESS LOGIC (only marker additions, never test-content changes).

## Critical implementation notes

- **The classification work is empirical, not theoretical.** Run xdist; observe which tests fail; classify; mark. Do NOT pre-mark tests defensively based on "looks like state-coupling." Marker should reflect empirical evidence.
- **Murat's risk model (party-mode 2026-05-04):**
  - 4-core box: 7 min → 3-4 min expected (~50% reduction).
  - 8-core box: 7 min → 2 min expected (~70% reduction).
  - >100 markers needed = surface for re-evaluation (xdist ROI shrinks).
- **NFR-7c-R2 invariant is non-negotiable.** Combined parallel + serial pass total MUST equal pre-xdist serial baseline (delta = 0). If divergent: HALT-AND-SURFACE; either rollback OR investigate the divergent test as a real bug.
- **Operator-acceptance threshold:** at least 1.5× combined speedup vs serial-only ~7 min baseline. If <1.5× speedup, surface as `decision_needed` (xdist may not be worth the maintenance overhead).
- **R-tier=R3 here is intentional:** the diagnostic AGAINST the full suite IS the deliverable; running broad regression on this story isn't a verification, it's the work-product. Don't misread R-tier as "skip broad regression"; this story has it baked in.
- **Smoke-suite curation methodology** (canonical; document in `curate_smoke_suite.py` docstring):
  - `pytest --durations=0 --co --cov=app --cov-report=json` (collect + coverage).
  - Score = (covered-lines × not-already-covered) / wall-clock. Rank descending. Top-200.
  - Verify load-bearing module coverage by manual spot-check at T3.3.
  - Document in T10 self-review notice.
- **No new third-party deps beyond pytest-xdist.** If T1.2 surfaces pytest-xdist absent and operator approves install → that's THE one new dep.
- **Windows portability per NFR-7c-X3:** UTF-8 explicit everywhere; `pathlib.Path.as_posix()` for path strings; `pytest -p no:randomly` flag preserved in default `addopts`.
- **`@pytest.mark.serial` registration in config:** the `markers` section MUST register `serial` so pytest doesn't warn about unknown markers.

## Verification battery (T6)

```bash
# Parallel pass (default after addopts change):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Serial pass:
.venv/Scripts/python.exe -m pytest -n0 -p no:randomly -m "serial" -q --tb=line

# Smoke pass (sanity; should be ~2-3 min):
.venv/Scripts/python.exe -m pytest @tests/_smoke_suite_manifest.json -p no:randomly -q --tb=short

# Class-conformance (≥11 activation contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Lint-imports (KEPT count unchanged or higher; no contract demotion):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator:
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0c-pytest-xdist-classification.md

# Ruff hygiene on touched files:
.venv/Scripts/python.exe -m ruff check pytest.ini pyproject.toml scripts/utilities/curate_smoke_suite.py tests/structural/test_pytest_xdist_config_present.py tests/structural/test_smoke_suite_manifest_present.py tests/structural/test_pytest_xdist_classification_doc_present.py

# Combined-pass invariant check (NFR-7c-R2 preservation; combined = serial-only baseline):
# Codex MUST report parallel-pass total + serial-pass total + delta vs T1.4 baseline in T10 self-review.
```

Expected post-7c.0c outcomes:
- Combined parallel + serial pass total = T1.4 baseline (delta = 0; no xdist-introduced regressions).
- Wall-clock: parallel pass + serial pass combined < ~5 min (vs ~7 min serial-only baseline; ≥1.4× speedup).
- Smoke pass: ~2-3 min wall-clock; cardinality 150≤N≤250.
- Class-conformance: ≥11 activation contracts.
- Lint-imports: KEPT count ≥12 (post-7c.0b state preserved).
- Ruff: clean.

## T10 + T11

**T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in spec file.

**Critical T10 content:**
- Full classification table: every `@pytest.mark.serial`-marked test + bucket + 1-line rationale.
- Wall-clock report: parallel pass + serial pass + smoke pass times; combined-vs-baseline ratio.
- Smoke-suite cardinality + load-bearing-module coverage spot-check verdict (pass/fail per module).
- T1 `decision_needed` resolutions (pytest-xdist install? canonical config location? other).
- Combined-pass invariant verification: `parallel_total + serial_total = baseline_total` (numbers).
- Operator-acceptance threshold: speedup ratio (must be ≥1.5×; if not, surface).

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (single-gate; **standard tier** per t11_tier=standard). Review verdict at `_bmad-output/implementation-artifacts/7c-0c-code-review-2026-05-NN.md`. Claude verifies:
- Classification table is sound (no over-marking; markers reflect empirical evidence).
- `serial` marker is correctly registered in pytest config.
- Smoke-suite manifest cardinality + coverage match AC-7c.0c-B.
- Combined-pass invariant holds (NFR-7c-R2 preserved).
- Documentation is complete (6 sections per AC-7c.0c-C).
- Wall-clock speedup ≥1.5×; otherwise reviewer surfaces for operator-decision (rollback or accept).

Claude applies remediation cycles per HALT-AND-REMEDIATE; commits the diff; flips `migration-7c-0c-pytest-xdist-classification: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.0a OR 7c.0b status NOT `done` (this prompt was dispatched too early).
  (b) pytest-xdist not installed in `.venv` AND operator hasn't pre-authorized install.
  (c) Combined parallel + serial pass total ≠ T1.4 baseline (NFR-7c-R2 invariant violation).
  (d) Speedup ratio <1.5× combined (xdist ROI insufficient; rollback may be the right answer).
  (e) Classification surfaces >100 `serial` markers needed (high state-coupling; xdist ROI shrinks; surface for re-evaluation).
  (f) Smoke-suite curation can't reach 150 tests (suite too thin) OR overshoots 250 (no useful tier separation from R3 broad regression).
  (g) ANY sandbox-AC violation.

- **Do NOT touch:**
  - Specialist bodies, HIL surface modules, pipeline-manifest, 7c.0a's ADR, 7c.0a's TripwireLedgerEntry, 7c.0b's deliverables.
  - Existing test BUSINESS LOGIC (only marker additions; no content changes).

- **Do NOT introduce:**
  - New third-party deps beyond pytest-xdist (and only if operator approves install at T1.2).
  - Defensive `serial` markers without empirical xdist-failure evidence.
  - Manual smoke-suite cherry-picking that overrides curator ranking without documented rationale.
  - `PYTHONIOENCODING=utf-8` workarounds in test fixtures or production code.
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify `migration-7c-0a-decision-foundation: done` AND `migration-7c-0b-scaffold-foundation: done` in BOTH spec files AND sprint-status.yaml.
2. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0c-pytest-xdist-classification.md` → expect PASS.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-0c-pytest-xdist-classification.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Verify governance JSON entry for 7c-0c is current (single-gate; r_tier=R3; t11_tier=standard; lookahead_tier=1; pts=3; K=1.2; prerequisite_stories=[7c-0b]) — locked at v2026-05-04-velocity-amendments-bundle.
5. ☐ Confirm sprint-status.yaml shows `migration-7c-0c-pytest-xdist-classification: ready-for-dev`.
6. ☐ Pre-flight: verify pytest-xdist is installed via `.venv/Scripts/python.exe -c "import xdist; print(xdist.__version__)"`. If absent, decide install vs scrap-V1 BEFORE dispatch.
7. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.
8. ☐ **Dispatch ORDER:** 7c.0c BEFORE 7c.4a, despite 7c.4a being authored first. Highest-amortization-leverage rule (per AMEND-V1 + velocity-amendments-bundle).

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0c.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~7-file diff + classification table + wall-clock report; runs `bmad-code-review` (T11; standard tier).
3. ☐ Claude verifies combined-pass invariant + speedup-ratio ≥1.5× + classification soundness + manifest coverage.
4. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
5. ☐ Claude commits + flips `migration-7c-0c-pytest-xdist-classification: review → done` in sprint-status.yaml.
6. ☐ At 7c.0c close, **all subsequent stories' T9 verification batteries adopt the new defaults** (parallel + serial pass) and R-tier R2 stories invoke smoke-suite via `pytest @tests/_smoke_suite_manifest.json`. Pytest savings amortize across remaining ~30 stories.
