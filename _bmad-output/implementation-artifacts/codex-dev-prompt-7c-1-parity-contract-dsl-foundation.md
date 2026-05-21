# Codex dev-story prompt — Story 7c.1 (Parity-Contract DSL Foundation; refactor 8 transport-parity files onto DSL)

**Cycle:** Claude spec → Codex T1-T4 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 slot 1 (substrate-precondition for HIL surface stories 7c.6..7c.15 + per-gate stories 7c.5.G0..G6).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline + AMEND-V5 lookahead Tier 1.
**Dispatch ordering:** **DISPATCH AFTER 7c.0c CLOSES.** Predecessor chain technically clean post-7c.0b (commit `9114337`), BUT Codex single-thread + highest-amortization-leverage rule means 7c.0c (xdist diagnostic) dispatches first; 7c.1 follows. Operator dispatches 7c.1 once 7c.0c is `done`. AMELIA-P2 freshness check at dispatch.

---

```
Run bmad-dev-story on Story 7c.1 (Slab 7c Wave 1 slot 1; dual-gate; refactor 8 transport-parity test files onto the parity-contract DSL primitives shipped in 7c.0b).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-1-parity-contract-dsl-foundation.md` (status: ready-for-dev; 4 ACs A-D; 4 task groups T1-T4 + T10/T11).
2. **Predecessor 7c.0a's FROZEN ADR**: `docs/dev-guide/adr/0001-parity-contract-dsl.md` — §1 (decorator registration) + §2 (`SurfaceTransportDeclaration` schema) + §3 (the 8-file refactor target list — THIS STORY'S deliverable).
3. **Predecessor 7c.0b's FROZEN DSL package**: `app/parity/contracts/__init__.py` (public surface) + `_reference_surface.py` (pattern-precedent).
4. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-30..33 + NFR-7c-P3.
5. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.1 section starting at line 414).
6. Velocity-amendments artifact: `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — R-tier + T11-tier + lookahead-tier conventions.
7. Required readings:
   - `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + A-test-1 mocking-the-SUT + module-level vs per-function decoration anti-patterns.
   - `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.4×.
8. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-1` (dual-gate; expected_pts=3; expected_k_target=1.4; r_tier=R3; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-0b]).
9. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
10. T11 reference: `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-04.md` — informational PASS verdict; the DSL primitives this story consumes are review-confirmed clean.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.0a `done` (commit `f926867`) + 7c.0b `done` (commit `9114337`) — both predecessors closed.
- 7c.0c `done` — operationally required per Codex single-thread + xdist amortization. If 7c.0c is NOT yet done at dispatch time, surface to operator (acceptable to dispatch 7c.1 in parallel since paths are disjoint, but operationally the queue blocks).
- DSL primitives importable: `from app.parity.contracts import parity_contract, SurfaceTransportDeclaration, iter_registered_surfaces` resolves without error.
- Reference surface registers at import: `from app.parity.contracts._reference_surface import reference_surface_placeholder` triggers registration; `iter_registered_surfaces()` yields `surface_id="reference_7c0b_scaffold"`.
- All 8 refactor target files exist at canonical ADR §3 paths (verified at spec-authoring 2026-05-04). DO NOT relocate.
- pyproject.toml C4 forbidden_modules unchanged: 12 KEPT / 0 broken via lint-imports.
- Class-conformance: 11 conforming activation contracts.
- Refresh broad-regression baseline at current HEAD: `pytest -p no:randomly -q --tb=no` → record total pass/fail/skip counts as comparison baseline for T4.3.

## Files in scope

**Modified (8 files; transport-parity test files):**
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py`
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py`
- `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py`
- `tests/integration/transports/test_transport_parity.py`
- `tests/integration/transports/test_override_transport_parity.py`
- `tests/integration/transports/test_cli_gate_decide.py`
- `tests/integration/transports/test_http_gate_endpoint.py`
- `tests/integration/transports/test_mcp_gate_decide_tool.py`

Per-file refactor pattern (canonical):
```python
# Add at module top:
from app.parity.contracts import parity_contract


# Add at module level (or class level if scoping to a test class):
@parity_contract(
    surface_id="<filename-stem-without-test-prefix>",
    mandatory_transports=[<derived-from-file-content-at-T1.5>],
    optional_transports=[<derived-from-file-content-at-T1.5>],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for <filename>."""
    return "<filename-stem>"
```

OR class-level (if existing test class is already module-defining):
```python
@parity_contract(surface_id="...", mandatory_transports=[...], optional_transports=[...])
class TestExistingTransportParity:
    ...
```

Pick ONE pattern; consistency across all 8 files is a minor PATCH-finding at T11 if mixed.

**New (2 files; structural tests):**
- `tests/structural/test_transport_parity_files_register_via_dsl.py` — AST scan + import-load + surface_id-in-registry assertion per AC-7c.1-A test pin.
- `tests/structural/test_transport_parity_dsl_registration_floor.py` — invokes `run_self_registration_audit` with explicit `discovery_roots=("app.gates", "app.composers", "tests.integration.transport_parity", "tests.integration.transports")` + `declared_floor=9`; asserts `audit_status == "PASS"`.

**Do NOT modify:**
- ANY production code (`app/specialists/**`, `app/gates/**`, `app/marcus/**`, `app/parity/contracts/**`, `app/audit/**`, `app/composers/**`, `app/models/**`).
- 7c.0a's ADR (`docs/dev-guide/adr/0001-parity-contract-dsl.md` — read only).
- 7c.0b's DSL package (`app/parity/contracts/**` — read only).
- pyproject.toml (no import-linter contract changes; no addopts changes; 7c.0c owns the parallel-default config).
- pytest.ini (no changes).
- Any other test file outside the 8 refactor targets.

**Do NOT introduce:**
- New helper modules under `app.parity.contracts.*` (would trigger C4 evaluation; out of scope).
- Per-test-function `@parity_contract` decoration (anti-pattern; multiplies registrations + collides surface_ids; module-level only).
- Surface_id collisions across files (each surface_id MUST be unique).
- Mocking of the DSL primitives in the structural tests (use real decorator + registry).
- New third-party deps.
- Modifications to existing test logic (refactor is registration-overlay only; tests' functional behavior unchanged).

## Critical implementation notes

- **K-target 1.4× ≈ ~3.5K LOC ceiling.** Estimate ~600-800 LOC: 8 files × ~10 LOC delta each = ~80 LOC + 2 structural tests × ~120 LOC = ~240 LOC + Dev Notes documentation = ~600-800 LOC. Comfortable.
- **Transport-coverage derivation at T1.5 is the highest-risk step.** Each file's `mandatory_transports` MUST reflect the actual transport coverage in the file. Inspect existing test content; document derivation per file in Dev Notes. RECOMMENDATIONS in spec AC-7c.1-A bullet 4 are derived from filename inspection only — verify against actual content. Surface as `decision_needed` if any file's transport coverage is ambiguous (e.g., a file imports both FastAPI and MCP-stdio fixtures but the test logic actually exercises only one).
- **Surface_id naming convention:** filename-stem-without-`test_`-prefix. E.g., `test_fastapi_mcp_parity.py` → `surface_id="fastapi_mcp_parity"`. Document in Dev Notes if Codex deviates.
- **Module-level decoration only.** Per-test-function decoration is anti-pattern (would multiply registrations and create surface_id collisions if the function runs multiple times via parametrize).
- **Refactor is overlay-only.** ZERO semantic changes to existing test logic. Each file's pass/fail/skip count post-refactor MUST match pre-refactor.
- **Post-7c.0c xdist parallelism:** the refactored files MUST be parallel-safe under `-n auto --dist loadfile`. If any file reveals state-coupling at T4.4 wall-clock check, add `@pytest.mark.serial` in 7c.1's diff (NOT a 7c.0c rerun).
- **A11 Windows-portability:** UTF-8 explicit everywhere; `pathlib.Path.as_posix()` for path strings in structural tests.
- **No new third-party deps.** Pydantic v2 + ast (stdlib).

## Verification battery (T4 — implicit at this story)

```bash
# Focused refactored tests:
.venv/Scripts/python.exe -m pytest tests/integration/transport_parity tests/integration/transports -p no:randomly -q --tb=short

# New structural tests:
.venv/Scripts/python.exe -m pytest tests/structural/test_transport_parity_files_register_via_dsl.py tests/structural/test_transport_parity_dsl_registration_floor.py -p no:randomly -q --tb=short

# R3 broad regression (parallel default post-7c.0c; combined parallel + serial):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# NFR-7c-P3 wall-clock check (parity suite serial ≤90s; parallel ≤45s):
time .venv/Scripts/python.exe -m pytest tests/integration/transport_parity tests/integration/transports -p no:randomly --tb=no -q
time .venv/Scripts/python.exe -m pytest tests/integration/transport_parity tests/integration/transports -n auto --dist loadfile -p no:randomly --tb=no -q

# Class-conformance (11 contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Lint-imports (12 KEPT; no contract change):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator:
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-1-parity-contract-dsl-foundation.md

# Ruff hygiene on touched files:
.venv/Scripts/python.exe -m ruff check tests/integration/transport_parity tests/integration/transports tests/structural/test_transport_parity_files_register_via_dsl.py tests/structural/test_transport_parity_dsl_registration_floor.py
```

Expected post-7c.1 outcomes:
- Combined parallel + serial pass total = T1 baseline (delta = 0; no refactor-introduced regressions).
- Wall-clock: parity suite serial ≤90s; parallel ≤45s.
- Class-conformance: 11 activation contracts (UNCHANGED).
- lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Ruff: clean on 10 touched files.
- Self-registration audit at floor=9 with explicit discovery_roots: PASS.

## T10 + T11

**T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in spec file.

**Critical T10 content:**
- Full transport-coverage derivation table: file → mandatory_transports + optional_transports + rationale per file (8 entries).
- Surface_id naming convention picked + applied (8 entries: filename-stem mapping).
- Wall-clock report: parity suite serial + parallel times.
- Broad-regression delta vs T1.4 baseline (numbers).
- T1 `decision_needed` resolutions (transport coverage ambiguities; helper-module placement; etc.).
- Module-level vs class-level decoration pattern picked.
- Self-registration audit cardinality at floor=9 (PASS).

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (single-gate; **standard tier** per t11_tier=standard). Review verdict at `_bmad-output/implementation-artifacts/7c-1-code-review-2026-05-NN.md`. Claude verifies:
- Each refactored file has exactly one `@parity_contract` decorator at module/class level (no per-function multiplication).
- Each surface_id is unique across the 8 files.
- Each `mandatory_transports` is non-empty (FR-7c-32) + accurately reflects file's transport coverage (cross-check against file content).
- No semantic changes to existing test logic (refactor is overlay-only).
- Combined-pass invariant holds (NFR-7c-R2 preserved; broad-regression delta = 0).
- NFR-7c-P3 wall-clock budget honored.
- Self-registration audit cardinality = 9 with explicit discovery_roots.

Claude applies remediation cycles per HALT-AND-REMEDIATE; commits the diff (8 modified + 2 NEW files); flips `migration-7c-1-parity-contract-dsl-foundation: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.0a OR 7c.0b OR 7c.0c status NOT `done`.
  (b) DSL primitives not importable from `app.parity.contracts`.
  (c) Reference surface fails to register at import.
  (d) Transport-coverage derivation ambiguous for any of the 8 files (multiple plausible interpretations of mandatory_transports).
  (e) Combined parallel + serial pass total ≠ T1.4 baseline (NFR-7c-R2 invariant violation).
  (f) NFR-7c-P3 wall-clock significantly exceeded (parity suite serial >120s OR parallel >60s — surface for budget renegotiation).
  (g) Refactor surfaces a need for new helper modules under `app.parity.contracts.*` (out of scope; would require C4 re-evaluation).
  (h) Any file fails its own pre-refactor tests post-refactor (refactor introduced a semantic change; investigate).
  (i) Surface_id collision across files.
  (j) ANY sandbox-AC violation OR class-conformance regression OR lint-imports change.

- **Do NOT touch:**
  - Any production code (`app/**` except `app.parity.contracts.*` which is read-only here).
  - 7c.0a's ADR.
  - 7c.0b's DSL package.
  - pyproject.toml.
  - pytest.ini.
  - Any test file outside the 8 refactor targets + 2 new structural tests.

- **Do NOT introduce:**
  - New helper modules under `app.parity.contracts.*` (out of scope; would trigger C4 evaluation).
  - Per-test-function `@parity_contract` decoration (module-level only).
  - Surface_id collisions.
  - Mocking of DSL primitives.
  - New third-party deps.
  - Semantic changes to existing test logic.
  - `@pytest.mark.serial` markers UNLESS a refactored file empirically fails under xdist post-refactor (then add the marker as part of the fix).
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify `migration-7c-0a-decision-foundation: done` AND `migration-7c-0b-scaffold-foundation: done` AND `migration-7c-0c-pytest-xdist-classification: done` in BOTH spec files AND sprint-status.yaml.
2. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-1-parity-contract-dsl-foundation.md` → expect PASS.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-1-parity-contract-dsl-foundation.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Verify governance JSON entry for 7c-1 is current (dual-gate; r_tier=R3; t11_tier=standard; lookahead_tier=1; pts=3; K=1.4; prerequisite_stories=[7c-0b]) — locked at v2026-05-04-velocity-amendments-bundle.
5. ☐ Confirm sprint-status.yaml shows `migration-7c-1-parity-contract-dsl-foundation: ready-for-dev`.
6. ☐ Pre-flight: verify DSL primitives import cleanly + reference surface registers via:
   ```bash
   .venv/Scripts/python.exe -c "from app.parity.contracts import parity_contract, SurfaceTransportDeclaration, iter_registered_surfaces; from app.parity.contracts._reference_surface import reference_surface_placeholder; assert any(s.surface_id == 'reference_7c0b_scaffold' for s in iter_registered_surfaces()); print('DSL importable + reference surface registers')"
   ```
7. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~10-file diff + transport-coverage derivation table + wall-clock report; runs `bmad-code-review` (T11; standard tier).
3. ☐ Claude verifies decoration-pattern correctness + surface_id uniqueness + transport-coverage accuracy + combined-pass invariant + wall-clock budget + audit-cardinality.
4. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
5. ☐ Claude commits + flips `migration-7c-1-parity-contract-dsl-foundation: review → done` in sprint-status.yaml.
6. ☐ At 7c.1 close, **the parity-contract DSL has 8 baseline registrations** (+1 from reference surface = 9). Downstream HIL surface stories (7c.6..15) and per-gate stories (7c.5.G0..G6) inherit this substrate — they self-register via `@parity_contract` decorator following the canonical pattern from 7c.1.
