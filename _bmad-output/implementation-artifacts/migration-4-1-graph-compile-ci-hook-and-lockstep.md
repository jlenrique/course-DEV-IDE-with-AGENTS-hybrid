# Migration Story 4.1: Graph-Compile-Time CI Hook + Lockstep Enforcement

**Status:** ready-for-dev
**Sprint key:** `migration-4-1-graph-compile-ci-hook-and-lockstep`
**Epic:** Slab 4 (migration Epic 4 — Lockstep + Gates + Cora + Ledger + Frozen-Graph; M4 go/no-go gate "Governance regime is architectural") — **OPENING story; Slab 4 kickoff**.
**Pts:** 5 | **Gate:** dual (per governance JSON `4-1.expected_gate_mode = "dual-gate"`, rationale: `ci_or_compile_shape`). **K-target:** ~1.4× (target 14 / floor 10; CI hook script + GHA workflow + LockstepError on drift + intentionally-drifted PR rejection test + ≤60sec NFR-P6 perf budget + integration with existing 33-2 check_pipeline_manifest_lockstep.py).

**Predecessor:** Slab 3 must be `done` (Marcus orchestrator + manifest infrastructure stable). Drafted-for-queue.

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `4-1.expected_gate_mode = "dual-gate"` (rationale: `ci_or_compile_shape`).
2. **Existing 33-2 substrate (BINDING)** — `scripts/utilities/check_pipeline_manifest_lockstep.py` exists per Epic 33 regime; 8 deterministic checks per `docs/dev-guide/pipeline-manifest-regime.md:26`. Story 4.1's NEW script `scripts/check_manifest_lockstep.py` is COMPLEMENTARY (graph-compile-time validation), NOT a replacement. Existing 33-2 script stays.
3. **D6 compiler substrate** — Slab 1 substrate `compile_run_graph(manifest, validation_mode=True)` per architecture D6. Verify exists; if absent, surface to operator (Slab 1 close-state regression).
4. **Dev-graph compiler substrate** — `compile_dev_graph(dev_manifest, validation_mode=True)` ships at 4.2 (Cora dev-graph). 4.1 references the symbol but tolerates 4.2-pending state (test parametrize-skip if dev-graph not yet shipped).
5. **block_mode_trigger_paths manifest** — `state/config/pipeline-manifest.yaml:32-...` carries the block-mode trigger paths list per Epic 33 §33-4 governance.
6. **PR-R forward-port (eventual M5)** — `check_dispatch_registry_lockstep.py` from primary repo's PR-R is the future companion script per epic 4.1 wording. Forward-port deferred to M5 per `architecture` doc; 4.1 ships WITHOUT requiring PR-R companion (defer-tolerant per epic).
7. **GHA workflow infrastructure** — verify `.github/workflows/` directory exists; if absent, 4.1 creates it.
8. **NFR-P6** — script wall-clock ≤60sec.
9. **Anti-patterns catalog** — A1-A14 post-2c.4 close.
10. **Severance posture** — hybrid working tree.

### Slab 4.1 artifact-existence sweep (6-point)

- **A** `scripts/utilities/check_pipeline_manifest_lockstep.py` exists per Epic 33; 8 deterministic checks.
- **B** `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` populated.
- **C** `compile_run_graph(manifest, validation_mode=True)` callable per Slab 1.
- **D** `compile_dev_graph(dev_manifest, validation_mode=True)` may not exist until 4.2; 4.1 tolerates pending.
- **E** `.github/workflows/` directory state — verify.
- **F** PR-R `check_dispatch_registry_lockstep.py` NOT yet on hybrid (forward-port deferred to M5); 4.1 ships without it.

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

**Two:** (1) Epic 4.1 references "scripts/check_manifest_lockstep.py" — placement `scripts/` vs existing 33-2 at `scripts/utilities/`. **Resolution:** 4.1 places NEW script at `scripts/utilities/check_manifest_lockstep.py` (consistent with 33-2 location convention); update epic if needed. (2) Epic references PR-R `check_dispatch_registry_lockstep.py` "when forward-ported" — this is M5 forward-port scope, not 4.1. **Resolution:** 4.1's script accepts a future `--dispatch-registry-check` flag that no-ops on hybrid pre-M5; M5 forward-port story enables it.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) `scripts/utilities/check_manifest_lockstep.py` consuming `compile_run_graph(...)` + `compile_dev_graph(...)` (latter defer-tolerant); (b) PR-diff iteration + per-block-mode-trigger-path companion-update assertion; (c) `LockstepError` raise on drift; (d) GHA workflow at `.github/workflows/manifest-lockstep.yml`; (e) intentionally-drifted PR rejection test; (f) ≤60sec NFR-P6 perf assertion. NOT in scope: Cora dev-graph (4.2); learning ledger (4.4); PR-R `check_dispatch_registry_lockstep.py` forward-port (M5).

**Decision #2 — In-process invocation per NFR-P6:** GHA workflow runs the script in-process (NOT subprocess) for performance per epic 4.1 + NFR-P6. Implementation: `python -c "from scripts.utilities.check_manifest_lockstep import main; main()"`.

**Decision #3 — LockstepError discriminated by drift-kind:** raise typed errors: `ManifestDriftError` (block-mode-trigger-path touched without companion update); `CompileError` (compile_run_graph or compile_dev_graph fails validation). Single `LockstepError` base class.

**Decision #4 — Defer-tolerance for compile_dev_graph (4.2 not yet shipped):** at 4.1 dev-time, `compile_dev_graph` import wrapped in `try/except ImportError` with skip-with-reason fallback; test parametrize-skips dev-graph cases until 4.2 lands.

---

## Story

As a **CI governance system enforcing Pipeline Lockstep per FR38 + FR39**,
I want **`scripts/utilities/check_manifest_lockstep.py` consuming the D6 compiler (validation mode) for both run-graph and dev-graph + GHA workflow running on every PR + LockstepError raised on block-mode-trigger-path drift + intentionally-drifted PR rejection (M4 Required Evidence)**,
So that **FR38 + FR39 are architecturally enforced + drift-impossible-to-merge + the existing 33-2 pipeline-manifest lockstep check is complemented (NOT replaced) at the graph-compile layer**.

---

## Acceptance Criteria

### AC-4.1-A — `scripts/utilities/check_manifest_lockstep.py` script implementation

- **Given** no `scripts/utilities/check_manifest_lockstep.py` exists; existing `check_pipeline_manifest_lockstep.py` shipped per Epic 33 (verified at T1)
- **When** the dev agent authors the NEW script:
  ```python
  def main(diff_files: list[str] | None = None) -> int:
      """Returns 0 on no-drift, non-zero on LockstepError."""
      # 1. Load manifest from state/config/pipeline-manifest.yaml
      # 2. Load dev-manifest from state/config/dev-graph-manifest.yaml (if exists; defer-tolerate)
      # 3. Call compile_run_graph(manifest, validation_mode=True); raise CompileError on fail
      # 4. Call compile_dev_graph(dev_manifest, validation_mode=True) if available; defer-tolerate
      # 5. Iterate PR diff (--diff-from <ref> arg or stdin); for each block-mode-trigger-path touched,
      #    assert companion updates in manifest + L1 script + pack
      # 6. Raise LockstepError on drift; return non-zero exit code
  ```
- **Then** script callable via `python -m scripts.utilities.check_manifest_lockstep --diff-from origin/master`; exit 0 on no-drift; non-zero on drift.
- **Test pin:** `tests/integration/lockstep/test_check_manifest_lockstep_script.py` — 3 tests:
  1. `test_no_drift_exits_zero` — clean PR diff (no manifest paths touched) → exit 0.
  2. `test_compile_error_raises` — synthetic invalid manifest → CompileError raised + non-zero exit.
  3. `test_dev_graph_defer_tolerant` — when `compile_dev_graph` not yet importable (pre-4.2), script proceeds with skip-with-reason log.

### AC-4.1-B — Intentionally-drifted PR rejection (M4 Required Evidence; DUAL-GATE gate-1)

- **Given** GHA workflow runs the script per AC-D
- **When** a synthetic test-PR intentionally touches a `block_mode_trigger_paths` entry WITHOUT companion updates
- **Then** CI fails with `LockstepError` naming the drifted file + missing companion; merge blocked
- **Test pin:** `tests/integration/lockstep/test_intentionally_drifted_pr_rejected.py` — 2 tests:
  1. `test_drift_in_pipeline_manifest_yaml_rejected` — synthetic diff touches `state/config/pipeline-manifest.yaml` without companion L1 script update; assert script raises `ManifestDriftError` with regex match on filename + missing-companion-name.
  2. `test_drift_in_l1_script_rejected` — synthetic diff touches `scripts/utilities/check_pipeline_manifest_lockstep.py` without manifest companion update; assert script raises `ManifestDriftError`.

### AC-4.1-C — Companion-update assertion logic per block-mode-trigger-path

- **Given** `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` enumerates the contract surfaces (L1 check script, run_hud.py, progress_map.py, workflow_runner.py, v4.2 pack, v4.2 generator package, learning-event schema/capture, etc. per CLAUDE.md §"Pipeline lockstep regime")
- **When** PR diff touches one of these paths
- **Then** the script asserts companion updates per the lockstep regime: e.g., touching `state/config/pipeline-manifest.yaml` REQUIRES companion edit to `scripts/utilities/check_pipeline_manifest_lockstep.py` AND/OR pack regeneration. Companion-rules table embedded in the script's source as a lookup.
- **Test pin:** `tests/integration/lockstep/test_companion_assertion_per_path.py` — 4 tests parametrize over 4 representative trigger-path-families → 1 K-floor unit per Murat M-R18.

### AC-4.1-D — GHA workflow at `.github/workflows/manifest-lockstep.yml` (in-process per NFR-P6)

- **Given** `.github/workflows/` directory state per T1 sweep
- **When** the dev agent authors `manifest-lockstep.yml`:
  ```yaml
  name: manifest-lockstep
  on: [pull_request]
  jobs:
    check:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with: { fetch-depth: 0 }  # for git diff
        - uses: actions/setup-python@v5
          with: { python-version: "3.11" }
        - name: Install deps
          run: pip install -e .
        - name: Run lockstep check (in-process per NFR-P6)
          run: python -c "from scripts.utilities.check_manifest_lockstep import main; sys.exit(main())"
  ```
- **Then** workflow runs on every PR; in-process invocation per Decision #2.
- **Test pin:** `tests/integration/lockstep/test_gha_workflow_present.py` — 1 test asserting workflow file exists + parses as valid YAML + has `on: pull_request` trigger + invokes script in-process (regex match on `python -c`).

### AC-4.1-E — NFR-P6 wall-clock ≤60sec performance budget

- **Given** epic 4.1 + NFR-P6 require ≤60sec script completion
- **When** the script runs against a representative PR diff
- **Then** wall-clock ≤60sec (measured via `time.perf_counter()` start/stop in test)
- **Test pin:** `tests/integration/lockstep/test_lockstep_perf_budget.py` — 1 test: invoke script against synthetic 10-file diff fixture; assert elapsed ≤60sec.

### AC-4.1-F — Anti-pattern catalog harvest (per R6)

NO new entries expected. If lockstep-pattern surfaces (e.g., "CI hook silently passing because import-error"), file as candidate.

### AC-4.1-G — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored.

### AC-4.1-H — D12 close protocol (DUAL-gate; ci_or_compile_shape; FIVE-line per dual-gate convention)

1. **Invariant preservation:** Pipeline Lockstep deterministic-neck (FR38/FR39); manifest CI architectural-not-conventional; existing 33-2 substrate intact (NOT replaced); D6 compiler validation-mode usage.
2. **Anti-pattern harvest:** N/A unless surfaced.
3. **Migration-guide update:** §6 (Lockstep CI) added or deepened with the 33-2 + 4.1 layered architecture.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: 1 NEW script + 1 GHA workflow + ≤60sec perf budget + 4 representative trigger-path families covered.
5. **Dual-gate gate-2 (operator CI-shape review):** operator confirms in-process invocation + LockstepError discriminated semantics + intentionally-drifted PR rejection demonstrated.

### AC-4.1-I — Sprint-status state-flips at filing AND at close

At filing: `migration-4-1-...: ready-for-dev` + `migration-epic-4-slab-4-lockstep-gates-cora-ledger: in-progress` opens. At close: `migration-4-1-...: done`.

---

## File Structure Requirements

### NEW files

```
scripts/utilities/
└── check_manifest_lockstep.py                    # AC-A; complementary to existing check_pipeline_manifest_lockstep.py (NOT replacement)

.github/workflows/
└── manifest-lockstep.yml                         # AC-D in-process invocation per NFR-P6

tests/integration/lockstep/
├── __init__.py
├── test_check_manifest_lockstep_script.py        # 3 tests (AC-A)
├── test_intentionally_drifted_pr_rejected.py     # 2 tests (AC-B)
├── test_companion_assertion_per_path.py          # 4 tests parametrize → 1 K-floor (AC-C)
├── test_gha_workflow_present.py                  # 1 test (AC-D)
└── test_lockstep_perf_budget.py                  # 1 test (AC-E)
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` — §6 (Lockstep CI) added/deepened per AC-H §3.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I.

### NOT modified

- `scripts/utilities/check_pipeline_manifest_lockstep.py` — DO NOT TOUCH (Epic 33 substrate; complementary not replacement).
- `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` — DO NOT TOUCH (Epic 33 governance).

---

## Testing Requirements

**K-target ~1.4× (target 14 / floor 10).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 3 (no-drift + compile-error + defer-tolerant) | **3** |
| B | 2 (manifest-yaml-drift + l1-script-drift) | **2** |
| C | 4 parametrize → 1 K-floor (4 trigger-path families same property) | **1** |
| D | 1 (GHA workflow present + in-process) | **1** |
| E | 1 (perf budget) | **1** |
| **Total** | **11 collected** | **8 K-floor units** |

**Honest K-floor: 8** — under floor 10 minimum. **RIDER:** AC-A adds `test_dev_graph_skip_logged_with_reason` orthogonal property (defer-tolerance has TWO sub-properties: (1) script proceeds, (2) skip-with-reason logged) → +1; AC-B adds `test_lockstep_error_classes_discriminated` (ManifestDriftError vs CompileError as orthogonal Decision #3 property) → +1. Total honest K-floor: 10 (meets floor minimum). Within ~1.4× K-target band (14/10 = 1.4×; 10/10 = 1.0×).

**Regression target at T8:** baseline post-Slab-3-close (T1-pinned per Murat M-R8 inheritance). +11 collected at file level. Import-linter contracts unchanged. Sandbox-AC PASS (script invocation via `subprocess.run([.venv/Scripts/python.exe, -m, scripts.utilities.check_manifest_lockstep, ...])` OR programmatic via `from scripts.utilities.check_manifest_lockstep import main`).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
