# Migration Story 7c.1: Parity-Contract DSL Foundation — Refactor 8 Existing Transport-Parity Files onto the DSL

**Status:** done *(spec authored 2026-05-04; predecessor 7c-0b CLOSED `done` commit `9114337`. Codex T1-T10 completed 2026-05-05 after operator accepted 7c.0c closed; operator accepted complete/closed 2026-05-05.)*
**Sprint key:** `migration-7c-1-parity-contract-dsl-foundation`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 3
**Gate:** **dual-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-velocity-amendments-bundle, story 7c-1; rationale: `substrate_shape`)
**K-target:** ~1.4× (substrate-shape; ~3 pts; bounded surface = 8 transport-parity test file refactors + ~5-10 new test scaffolding lines per file + manifest regeneration if needed)
**R-tier (regression scope):** **R3** — full broad regression. The 8 refactored files exercise transport parity matrix at the ~15-cell baseline; substrate-shape risk for downstream HIL surface stories (7c.6..15) is high enough to warrant full coverage. xdist parallelism (post-7c.0c adoption) reduces wall-clock cost.
**T11-tier (review approach):** **standard** — single-gate-or-dual; substrate-shape but pattern-replication; 3-layer Blind/Edge/Auditor review on the refactored 8 files + DSL invocation correctness.
**Files touched (declared at spec-author time):**
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py` (REFACTOR; consume DSL)
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py` (REFACTOR)
- `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py` (REFACTOR)
- `tests/integration/transports/test_transport_parity.py` (REFACTOR)
- `tests/integration/transports/test_override_transport_parity.py` (REFACTOR)
- `tests/integration/transports/test_cli_gate_decide.py` (REFACTOR)
- `tests/integration/transports/test_http_gate_endpoint.py` (REFACTOR)
- `tests/integration/transports/test_mcp_gate_decide_tool.py` (REFACTOR)
- (Optionally NEW) `tests/integration/transports/__init__.py` or shared helper module if refactor surfaces a common DSL-invocation pattern worth extracting; surface as `decision_needed` at T1.
**Lookahead tier:** **1** — author-ahead-aggressively (predecessor 7c.0b closed; DSL primitives + reference surface frozen at commit `9114337`; PRD-locked refactor target list per 7c.0a ADR §3 frozen at commit `f926867`).
**Authored:** 2026-05-04 via `bmad-create-story` workflow + AMEND-V5 lookahead Tier 1.
**Wave:** 1 — slot 1 (substrate-precondition for HIL surface stories 7c.6..15 and per-gate stories 7c.5.G0..G6).

**FR coverage:** FR-7c-30..33 — DSL primitives + self-registration + transport-declaration enforcement consumed by the 8 refactored files. Specifically:
- FR-7c-30 parity-contract DSL primitive set under `app/parity/contracts/` — primitives shipped in 7c.0b; this story EXERCISES them via the 8-file refactor.
- FR-7c-31 DSL self-registers each declared surface — verified by the refactor (each refactored file declares parity contract via `@parity_contract` decorator).
- FR-7c-32 per-surface mandatory-transport declaration; surfaces without declaration denied parity-test budget — already enforced by `SurfaceTransportDeclaration` model validator (shipped 7c.0b); the refactor MUST honor mandatory_transports per file.
- FR-7c-33 existing 8 transport-parity test files refactor to consume DSL primitives, preserving current ~15-cell coverage as baseline.

**NFR coverage:** NFR-7c-P3 (parity-test full run ≤90s @ ~15-cell scale; ≤6 min @ ~68-cell scale). NFR-7c-R2 (≥1403 deterministic baseline at `-p no:randomly`; preserved). NFR-7c-X4 (no regression). NFR-7c-M5 sandbox-AC validator PASS.

**Standing-guardrail enforcement:**
- SG-1 unchanged (no specialist-roster change).
- SG-2 unchanged (no mapping-checklist row change directly; transport parity rows preserve via the refactor).
- SG-3 Composition Spec §3.1 / §3.5 / §3.6 honored on DSL primitive contract — the DSL is below the gate-decision layer; per-specialist precedence rule UNALTERED.
- SG-4 unchanged.

**Tripwire ownership:** none direct. The refactor exercises 7c.0b's TW-7c-6 detection scaffold (per-cell flake-rate calculator) by creating cells the calculator can score; pre-warming for 7c.21's 50-run baseline.

**Implementation cycle (NEW CYCLE per memory entry `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 + `feedback_velocity_amendments_slab_7c.md`):**
- **Claude (Opus 4.7):** authored this spec 2026-05-04 (lookahead Tier 1 ahead-of-Codex during 7c.0c dev); sandbox-AC validator PASS; governance JSON entry verified post-velocity-bundle; pre-authors `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-1-parity-contract-dsl-foundation.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops the 8-file refactor per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md`.
- **Claude T11 standard review:** verifies the refactor preserves test semantics + each file declares correct mandatory_transports + parity matrix coverage preserved at ~15-cell baseline + no broad-regression delta. Commits + flips `migration-7c-1-parity-contract-dsl-foundation: review → done`.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — 7c.0a's frozen ADR. ADR §1 (decorator registration) + §2 (`SurfaceTransportDeclaration` schema; closed-enum `Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]` for transports) + §3 (the canonical 8-file refactor target list — THIS STORY's deliverable target).
- `app/parity/contracts/__init__.py` — public DSL surface (post-7c.0b commit `9114337`). Imports: `parity_contract`, `SurfaceTransportDeclaration`, `register_surface`, `iter_registered_surfaces`, `DuplicateSurfaceError`, `Transport` literal type.
- `app/parity/contracts/_reference_surface.py` — Codex's 7c.0b reference declaration; pattern-precedent for the refactor:
  ```python
  @parity_contract(
      surface_id="reference_7c0b_scaffold",
      mandatory_transports=["cli"],
      optional_transports=["http"],
  )
  def reference_surface_placeholder() -> str:
      return "reference_7c0b_scaffold"
  ```
- `docs/dev-guide/migration-story-governance.json::r_tier_legend` + `t11_tier_legend` + `velocity_amendment_record` — convention reference (post-velocity-bundle).
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability (preserved by 7c.2 close + binary-skip rule).
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-30..33 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.1 section starting at line 414) — epic-level AC framing.
- `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-04.md` — informational; T11 PASS verdict on 7c.0b deliverables this story consumes.

**Predecessor state (verified at dispatch time):**
- 7c.0a `done` (commit `f926867`).
- 7c.0b `done` (commit `9114337`).
- 7c.0c `done` (after the xdist classification spike closes; brings parallel pytest defaults into pytest config). **Operationally** 7c.1 dispatches AFTER 7c.0c closes per Codex single-thread + highest-amortization-leverage rule, even though prerequisite_stories=[7c-0b] does not strictly require it.
- DSL primitives importable from `app.parity.contracts` (verify: `from app.parity.contracts import parity_contract, SurfaceTransportDeclaration` resolves cleanly).
- Reference surface registers at import time (verify: `from app.parity.contracts._reference_surface import reference_surface_placeholder` triggers registration; `iter_registered_surfaces()` yields at least one entry with `surface_id="reference_7c0b_scaffold"`).
- `pyproject.toml::[tool.importlinter]` C4 forbidden_modules populated post-7c.0b (`app.gates.resume_api`, `app.marcus.orchestrator.write_api`, `app.specialists.*`); refactor MUST NOT introduce any of these as imports under `app.parity.contracts.*`. Note: 7c.1's refactor lives under `tests/integration/transport_parity/` and `tests/integration/transports/` (test files, NOT `app.parity.contracts.*`); C4 doesn't directly bind to the refactor target. But if Codex's refactor introduces helper modules, those MAY need to live under `app.parity.contracts.*` (subject to C4) — surface as `decision_needed` at T1 if helper-module placement is non-obvious.
- Class-conformance: 11 conforming activation contracts (no regression).
- lint-imports: 12 KEPT / 0 broken.
- Broad-regression baseline post-7c.0b/7c.0c: refresh at T1 against current HEAD; record total pass/fail/skip counts as comparison baseline for T9 verification.

**Live substrate (verified at T1):**
- The 8 refactor target files exist at the canonical paths per ADR §3 (verified at spec-authoring 2026-05-04). Codex SHALL NOT relocate any of them.
- Each file currently encodes its parity contract via test-class-level or module-level state (no DSL-decorator pattern; that's the 7c.1 deliverable). Inspect each file at T1 to determine its existing transport coverage.
- Each refactored file MUST declare its parity contract via `@parity_contract` decorator (or YAML registration if the ADR §1 escape-hatch is invoked — but escape-hatch usage requires party-mode consensus per ADR §4, NOT in scope for 7c.1).
- The decorator MUST be applied at module level (or class level if the parity contract scopes to a test class). Per-test-function decoration is anti-pattern (registration-multiplication; surface-id collisions).
- Each surface_id should match the file's transport coverage semantics. Recommend naming convention: `surface_id` = filename-stem-without-`test_`-prefix (e.g., `test_fastapi_mcp_parity.py` → `surface_id="fastapi_mcp_parity"`); document the convention in Dev Notes if Codex picks something different.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 1 (post-7c.0b; substrate-precondition for HIL surface stories). Parity-contract DSL foundation primitives + 8 existing transport-parity test files refactored to consume DSL (FR-7c-30..33). NFR-7c-P3 wall-clock <=90s at ~15-cell baseline preserved. Dual-gate justified by substrate-shape (downstream HIL surfaces 7c.6..7c.15 + per-gate stories 7c.5.G0..G6 self-register through these primitives).

**T1 conclusion:** No unanticipated architectural disagreement requires halting the dev round. Implementation proceeds: 8-file refactor + DSL invocation + transport-coverage preservation + broad-regression delta-zero. **Hard checkpoints at T1:**
- (a) 7c.0b `done` (verified at spec-authoring; refresh at dispatch).
- (b) 7c.0c `done` (Codex single-thread serialization + xdist defaults benefit T9 cost). If 7c.0c is NOT yet done at dispatch time, surface to operator (acceptable to dispatch 7c.1 in parallel since paths are disjoint, but operationally Codex single-thread blocks).
- (c) DSL primitives importable; reference surface registers cleanly.
- (d) C4 forbidden_modules unchanged (12 KEPT preserved).
- (e) Refresh broad-regression baseline at current HEAD before refactor begins.
- (f) Each of the 8 refactor target files exists at its ADR §3 canonical path.

---

## Story

As the substrate-shape consumer (downstream HIL surface stories 7c.6..7c.15 + per-gate stories 7c.5.G0..G6 + Marcus-bound writers 7c.17a/b),
I want the 8 existing transport-parity test files refactored to consume the parity-contract DSL primitives shipped in 7c.0b — `@parity_contract` decorator + `SurfaceTransportDeclaration` model + `register_surface` + `iter_registered_surfaces` self-discovery,
so that subsequent HIL-surface stories (7c.6..7c.15) and per-gate stories (7c.5.G0..G6) self-register into the parameterized parity-test harness rather than authoring per-surface bespoke tests, AND the 7c.21 slab-close ceremony's self-registration audit at non-zero cardinality floor has 8 baseline registrations to count.

---

## Acceptance Criteria

### AC-7c.1-A — 8 transport-parity test files refactored to consume `@parity_contract` decorator + register cleanly via DSL (FR-7c-30..33)

**Given** the 7c.0a ADR §3 refactor target list (frozen at commit `f926867`) + the 7c.0b DSL primitives (frozen at commit `9114337`)
**When** the dev-agent refactors each of the 8 target files
**Then** EACH file:

1. Imports `parity_contract` (and any other DSL surface entities needed) from `app.parity.contracts`.
2. Declares its parity contract via `@parity_contract(surface_id=..., mandatory_transports=[...], optional_transports=[...])` decorator at module level (or class level if the parity contract scopes to a test class). The decorator is invoked at import time; registration is automatic.
3. The `surface_id` matches the canonical convention (recommend: filename-stem-without-`test_`-prefix; document in Dev Notes if Codex deviates).
4. The `mandatory_transports` + `optional_transports` lists accurately reflect the file's pre-refactor transport coverage. Codex SHALL inspect each file at T1 to derive the transport set correctly:
   - `test_fastapi_mcp_parity.py`: FastAPI + MCP-stdio (parity test) → `mandatory_transports=["http", "mcp-stdio"]`, `optional_transports=[]` (likely; verify).
   - `test_mcp_stdio_smoke.py`: MCP-stdio smoke → `mandatory_transports=["mcp-stdio"]`.
   - `test_mcp_subprocess_hygiene.py`: MCP-subprocess hygiene → `mandatory_transports=["mcp-subprocess"]`.
   - `test_transport_parity.py`: full parity matrix → `mandatory_transports=["cli", "http", "mcp-stdio"]` likely.
   - `test_override_transport_parity.py`: parity for override-event flow → `mandatory_transports=["cli", "http", "mcp-stdio"]` likely.
   - `test_cli_gate_decide.py`: CLI-only gate-decide → `mandatory_transports=["cli"]`.
   - `test_http_gate_endpoint.py`: HTTP-only → `mandatory_transports=["http"]`.
   - `test_mcp_gate_decide_tool.py`: MCP-stdio + MCP-subprocess (verify which) → `mandatory_transports=["mcp-stdio"]` likely.
   - These are RECOMMENDATIONS based on filename inspection; Codex MUST verify against actual file content at T1 and adjust per real coverage. Surface as `decision_needed` if any file's transport coverage is ambiguous.
5. The post-refactor file PASSES its own existing tests (no semantic changes; pure registration-overlay refactor).

**And** the test files DO NOT introduce any new test functions or remove existing ones (refactor is registration-overlay only; functional test logic unchanged).

**And** the refactored files DO NOT modify business logic in `app/specialists/**`, `app/gates/**`, `app/marcus/**`, or any other production code. Only the 8 test files are modified.

**Test pin:** `tests/structural/test_transport_parity_files_register_via_dsl.py` (NEW) — for each of the 8 files: (a) parse the file via `ast.parse` and assert exactly one `@parity_contract(...)` decorator present at module or class level; (b) import the file and assert its surface_id appears in `iter_registered_surfaces()` after import; (c) assert `mandatory_transports` is non-empty (FR-7c-32 enforcement).

> **Notes for 7c.1-A.** This AC is **dev-agent-executable**. The transport coverage per file is a T1 verification that requires reading each file. Expected outcome: each file gets one decorator added at module level + an `import` line + zero other changes. Total LOC delta per file: ~5-10 lines. The 8 refactored files MUST import-load cleanly under both serial and (post-7c.0c) parallel pytest invocation.

### AC-7c.1-B — Self-registration audit produces 8 baseline registrations post-refactor (NFR-7c-OD7 progress; AC-F integration prep)

**Given** the 7c.0b self-registration audit harness (`run_self_registration_audit` in `app/parity/contracts/_audit.py`) + the 8 refactored files
**When** the audit harness imports `app.gates` + `app.composers` packages (default `discovery_roots`) + the reference surface
**Then** the registered-surface cardinality is at least **9** (8 newly refactored + 1 reference surface from 7c.0b). Sanctum-registry cardinality remains **0** (sanctum alignments are landed by 7c.17a/b at Wave 4).

**And** the registration manifest emitted by `emit_registration_manifest` contains 9 entries with stable JSON sort order; spot-check that each refactored file's surface_id is present.

**Test pin:** `tests/structural/test_transport_parity_dsl_registration_floor.py` (NEW) — invokes `run_self_registration_audit(declared_floor=9, manifest_path=tmp_path / "manifest.json", discovery_roots=("app.gates", "app.composers", "tests.integration.transport_parity", "tests.integration.transports"))`; asserts `audit_status == "PASS"`. Note: the audit harness's default `discovery_roots = ("app.gates", "app.composers")` doesn't include the test packages — this AC verifies the CLI invocation supports test-package discovery via the explicit `discovery_roots` parameter.

> **Notes for 7c.1-B.** This AC is **dev-agent-executable**. The 7c.0b audit harness already supports per-call `discovery_roots` override; AC-7c.1-B exercises that override path against the refactored test packages. If the audit harness's default `discovery_roots` should change to include test packages permanently, surface as `decision_needed` (architectural decision; recommend NO — keep audit defaults app-only; test discovery is a per-invocation override).

### AC-7c.1-C — Parity matrix coverage preserved at ~15-cell baseline; NFR-7c-P3 wall-clock ≤90s @ ~15-cell scale (FR-7c-33 / NFR-7c-P3)

**Given** the existing transport-parity matrix at ~15-cell baseline (8 files × ~2 transports avg = ~15 parity cells with overlap)
**When** the refactored files run under `pytest tests/integration/transport_parity tests/integration/transports -p no:randomly`
**Then** wall-clock ≤90s on the operator's hardware (per NFR-7c-P3 budget); pass/fail/skip totals match pre-refactor baseline (zero functional regression introduced by the refactor).

**And** post-7c.0c xdist adoption: the same suite under `pytest tests/integration/transport_parity tests/integration/transports -n auto --dist loadfile -p no:randomly` runs in ≤45s (target: 2× speedup vs serial); document actual wall-clock in Dev Notes.

**Test pin:** none direct (wall-clock is observational; document in Codex T10 self-review notice). The functional regression check is covered by the existing test files passing post-refactor.

> **Notes for 7c.1-C.** This AC is **dev-agent-executable**. NFR-7c-P3's ≤90s budget is an operator-acceptance threshold; if wall-clock significantly exceeds 90s, surface as `decision_needed` (refactor may have introduced unnecessary overhead OR the baseline measurement is stale).

### AC-7c.1-D — Zero broad-regression delta vs pre-refactor baseline (NFR-7c-R2 / NFR-7c-X4)

**Given** the broad-regression baseline at current HEAD (refreshed at T1 per checkpoint (e))
**When** the dev-agent runs `pytest -p no:randomly -q --tb=line` post-refactor (R3 tier)
**Then** total pass/fail/skip counts MATCH the T1 baseline (delta = 0). Any deviation surfaces as HALT-AND-SURFACE.

**And** `lint-imports` reports 12 KEPT / 0 broken (UNCHANGED; 7c.1 does not modify import-linter contracts).

**And** `validate_parity_test_class_conformance.py tests/parity/` reports 11 conforming activation contracts (UNCHANGED; the refactored files live under `tests/integration/transport_parity/` + `tests/integration/transports/`, NOT `tests/parity/`; no class-conformance impact).

**And** `validate_migration_story_sandbox_acs.py` PASS.

**And** `ruff check` clean on all touched files.

**Test pin:** none direct (verification battery is the test pin); documented in Codex T10 self-review notice.

> **Notes for 7c.1-D.** This AC is **dev-agent-executable**. NFR-7c-R2 ≥1403 deterministic baseline preservation is the load-bearing invariant; the refactor MUST NOT introduce ordering-dependent failures. xdist parallelism (post-7c.0c) is the secondary check — if any of the 8 refactored files needs `@pytest.mark.serial` due to refactor-introduced state-coupling, the marker is added in 7c.1's diff (NOT a 7c.0c rerun).

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.0a + 7c.0b + 7c.0c all `done` in spec files + sprint-status.
  - [x] T1.2 Confirm DSL primitives importable: `from app.parity.contracts import parity_contract, SurfaceTransportDeclaration, iter_registered_surfaces`.
  - [x] T1.3 Confirm reference surface registers at import: import `app.parity.contracts._reference_surface` and verify `reference_7c0b_scaffold` appears in `iter_registered_surfaces()`.
  - [x] T1.4 Refresh broad-regression baseline at current HEAD: `pytest -p no:randomly -q --tb=no` → record total pass/fail/skip counts as comparison baseline.
  - [x] T1.5 Inspect each of the 8 refactor target files; derive accurate `mandatory_transports` + `optional_transports` from existing test content. Document derivations in Dev Notes.
  - [x] T1.6 Confirm `validate_migration_story_sandbox_acs.py` PASS on this spec.

- [x] **T2 — Refactor 8 transport-parity test files (AC: 7c.1-A)**
  - [x] T2.1 `tests/integration/transport_parity/test_fastapi_mcp_parity.py` — add `@parity_contract` decorator + import.
  - [x] T2.2 `tests/integration/transport_parity/test_mcp_stdio_smoke.py` — same pattern.
  - [x] T2.3 `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py` — same pattern.
  - [x] T2.4 `tests/integration/transports/test_transport_parity.py` — same pattern.
  - [x] T2.5 `tests/integration/transports/test_override_transport_parity.py` — same pattern.
  - [x] T2.6 `tests/integration/transports/test_cli_gate_decide.py` — same pattern.
  - [x] T2.7 `tests/integration/transports/test_http_gate_endpoint.py` — same pattern.
  - [x] T2.8 `tests/integration/transports/test_mcp_gate_decide_tool.py` — same pattern.
  - [x] T2.9 Verify each file passes its OWN tests post-refactor (zero semantic change; pure overlay).

- [x] **T3 — Author 2 structural tests (AC: 7c.1-A + 7c.1-B test pins)**
  - [x] T3.1 `tests/structural/test_transport_parity_files_register_via_dsl.py` — AST scan + import-load + surface_id-in-registry assertion.
  - [x] T3.2 `tests/structural/test_transport_parity_dsl_registration_floor.py` — invoke audit harness with explicit `discovery_roots` + assert `audit_status == "PASS"` at floor=9.

- [x] **T4 — Verification battery (R-tier R3; AC: 7c.1-C + 7c.1-D)**
  - [x] T4.1 Focused refactored tests: `pytest tests/integration/transport_parity tests/integration/transports -p no:randomly -q --tb=short` — all pass.
  - [x] T4.2 New structural tests: `pytest tests/structural/test_transport_parity_files_register_via_dsl.py tests/structural/test_transport_parity_dsl_registration_floor.py -p no:randomly -q --tb=short` — all pass.
  - [x] T4.3 Run R3 broad regression (post-7c.0c parallel defaults): `pytest -p no:randomly -q --tb=line` — combined parallel + serial total = T1.4 baseline (delta = 0).
  - [x] T4.4 NFR-7c-P3 wall-clock check: parity-test suite serial ≤90s; parallel ≤45s. Document actual wall-clock.
  - [x] T4.5 `lint-imports` — 12 KEPT (no contract change).
  - [x] T4.6 Class-conformance: 11 activation contracts (no regression).
  - [x] T4.7 Sandbox-AC validator: PASS.
  - [x] T4.8 Ruff: clean on touched files.

- [x] **T10 — Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md` summarizing: file list (8 refactored + 2 NEW structural tests), transport-coverage derivation per refactored file, surface_id naming convention picked, wall-clock report (serial + parallel), broad-regression delta vs T1 baseline, sandbox-AC + class-conformance + lint-imports verdicts, T1 `decision_needed` resolutions.

- [ ] **T11 — Claude `bmad-code-review` (single-gate; standard tier)**
  - [ ] T11.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the diff; produces verdict at `_bmad-output/implementation-artifacts/7c-1-code-review-2026-05-NN.md`; applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-1-parity-contract-dsl-foundation: review → done`.

---

## Dev Notes

**Why this story exists:** FR-7c-33 explicitly required the refactor (8 existing transport-parity test files refactor to consume DSL primitives, preserving current ~15-cell coverage as baseline). 7c.0a's ADR §3 frozen the target list; 7c.0b's DSL primitives shipped the executable surface. 7c.1 is the consumer story that exercises the substrate end-to-end and creates the 8-baseline registration count for downstream's NFR-7c-OD7 self-registration audit floor.

**Why dispatch BEHIND 7c.0c:** Codex single-thread + highest-amortization-leverage rule. 7c.1's R3 broad regression cost (~7 min serial) reduces to ~2-4 min post-xdist. Dispatching 7c.1 before 7c.0c pays full serial cost; dispatching after compounds velocity savings.

**Refactor pattern (canonical; document in Dev Notes if Codex deviates):**
```python
# At module top of each of the 8 files:
from app.parity.contracts import parity_contract


@parity_contract(
    surface_id="<filename-stem-without-test-prefix>",
    mandatory_transports=[<derived-from-file-content>],
    optional_transports=[<derived-from-file-content>],
)
class _ParityContractRegistration:
    """Marker class for module-level parity-contract registration."""
```

OR module-level decorator on a sentinel function:
```python
@parity_contract(
    surface_id="<filename-stem-without-test-prefix>",
    mandatory_transports=[<derived>],
    optional_transports=[<derived>],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for <filename>."""
    return "<filename-stem>"
```

Codex picks one pattern; consistency across all 8 files is a minor PATCH-finding at T11 if mixed.

**File / module placement:**
- 8 refactored files at their canonical paths (per ADR §3); MUST NOT relocate.
- 2 NEW structural tests under `tests/structural/`.
- NO new helper modules under `app.parity.contracts.*` (would trigger C4 evaluation; not needed for this scope).
- NO modifications to `app/parity/contracts/**`, `app/audit/**`, or 7c.0a/0b deliverables (read-only).

**Anti-patterns to avoid (from `dev-agent-anti-patterns.md`):**
- **A11 Windows-portability** — all new code UTF-8-explicit; `pathlib.Path.as_posix()` for path strings.
- **A-test-1 Mocking the system-under-test** — refactor MUST NOT mock the DSL primitives. Tests use real `parity_contract` decorator + real registry.
- **A-review-ceremony-1 Lying about completion** — at T4.3 broad regression, report ACTUAL pass/fail counts; verify against T1 baseline.
- **Per-test-function decoration** — DO NOT decorate individual test functions with `@parity_contract`. Module-level (or class-level) registration is correct; per-function multiplies registrations + collides surface_ids.
- **Surface_id collisions across files** — each of the 8 files declares a UNIQUE surface_id. T11 review verifies via assertion in test pin AC-7c.1-A.

**K-discipline (from `story-cycle-efficiency.md`):**
- K-target 1.4× = ~2.5K LOC band-floor × 1.4 = ~3.5K LOC at T-shape ceiling. 8 file refactors at ~5-10 LOC each (~80 LOC) + 2 structural tests (~120 LOC each = ~240 LOC) + Dev Notes documentation (~200-400 LOC) = ~600-800 LOC total. WELL under K-target ceiling.
- If T1.5 transport-coverage derivation surfaces ambiguity that grows the refactor surface (e.g., needing helper modules under `app.parity.contracts.*` for shared DSL invocation), surface for K-budget renegotiation.

**Testing standards:**
- Pytest with `-p no:randomly` for deterministic-baseline preservation (NFR-7c-R2).
- Post-7c.0c, parallel pass via `-n auto --dist loadfile`; refactored files MUST be parallel-safe (no `@pytest.mark.serial` markers expected; if any are needed, add in 7c.1's diff).
- AST scan in structural test pin uses `ast.parse` + walks for `Call` nodes matching `parity_contract`.

### Project Structure Notes

- **Alignment with unified project structure:** all 8 file paths are existing canonical paths; 2 new structural test paths conform to existing convention. No new top-level packages.
- **Detected variances:** none anticipated. T1 verification confirms predecessor state + DSL importability; T1.5 derives transport coverage per file.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-1]
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (7c.0a's frozen ADR; §1 + §2 + §3 refactor target list)
- [Source: app/parity/contracts/__init__.py] (7c.0b's frozen DSL public surface)
- [Source: app/parity/contracts/_reference_surface.py] (pattern-precedent for decorator usage)
- [Source: docs/dev-guide/migration-story-governance.json#r_tier_legend + #t11_tier_legend + #lookahead_tier_legend + #velocity_amendment_record] (post-velocity-bundle conventions)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 Windows-portability; refactor anti-patterns)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline 1.4×)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (FR-7c-30..33)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.1] (Story 7c.1 section starting at line 414)
- [Source: _bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-04.md] (7c.0b T11 verdict; informational)
- [Source: _bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md] (R-tier + T11-tier + lookahead-tier conventions; AMEND-V1 7c.0c xdist diagnostic ahead-of-7c.1)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md` + AMEND-V conventions).

### Debug Log References

- T1 DSL import/reference registration: PASS (`DSL importable + reference surface registers`).
- T1 lint-imports: 12 KEPT / 0 broken.
- T1 class-conformance: `PASS: 11 activation contract file(s) conform`.
- T1 sandbox-AC validator: PASS.
- T1 broad baseline wall-clock under post-7c.0c defaults: 201.42s; comparison count baseline inherited from 7c.0c close was `39 failed, 4048 passed, 27 skipped, 2 xfailed` for the pre-7c.1 file set.
- Focused refactored transport tests: `19 passed in 11.30s`.
- New structural tests: `10 passed in 8.94s`.
- Post-refactor broad pass: `39 failed, 4058 passed, 27 skipped, 2 xfailed, 11 warnings in 215.39s`; the +10 pass delta is exactly the two new structural test files.
- Serial marker pass: `2 passed, 4172 deselected in 11.01s`.
- Parity suite wall-clock: serial 7.15s; parallel 9.49s; both under budget.
- Post-refactor lint-imports: 12 KEPT / 0 broken.
- Post-refactor class-conformance: `PASS: 11 activation contract file(s) conform`.
- Post-refactor sandbox-AC validator: PASS.
- Ruff on touched files: `All checks passed`.

### Completion Notes List

- Decoration pattern: one module-level sentinel function named `_parity_contract_registration` per target file; no test logic changed.
- Surface ID convention: filename stem without `test_` prefix.
- Transport derivation table:
  - `test_fastapi_mcp_parity.py` → `fastapi_mcp_parity`; mandatory `["http", "mcp-stdio"]`; FastAPI `/invoke` residual compared with MCP stdio `ping`.
  - `test_mcp_stdio_smoke.py` → `mcp_stdio_smoke`; mandatory `["mcp-stdio"]`; MCP SDK stdio initialize/list_tools/call_tool smoke.
  - `test_mcp_subprocess_hygiene.py` → `mcp_subprocess_hygiene`; mandatory `["mcp-subprocess"]`; raw MCP server subprocess shutdown hygiene.
  - `test_transport_parity.py` → `transport_parity`; mandatory `["cli", "http", "mcp-stdio"]`; compares resume, ledger, and trace responses from all three transport helpers.
  - `test_override_transport_parity.py` → `override_transport_parity`; mandatory `["cli", "http", "mcp-stdio"]`; compares override submit/apply flows across all three transport helpers.
  - `test_cli_gate_decide.py` → `cli_gate_decide`; mandatory `["cli"]`; CLI gate decide happy/invalid paths.
  - `test_http_gate_endpoint.py` → `http_gate_endpoint`; mandatory `["http"]`; HTTP gate endpoint happy/invalid/digest mismatch paths.
  - `test_mcp_gate_decide_tool.py` → `mcp_gate_decide_tool`; mandatory `["mcp-stdio"]`; MCP gate decide tool helper path.
- Self-registration audit: PASS at floor=9 with explicit discovery roots for app gates/composers plus both test packages; manifest contains the 8 new test surfaces plus `reference_7c0b_scaffold`.
- Broad regression retains the existing checkout-level 39 failures; no new failure class introduced by the overlay. Pass count increases by 10 from the two new structural files.
- NFR-7c-P3 wall-clock budget passed: parity suite serial 7.15s (≤90s), parallel 9.49s (≤45s).

### File List

- `tests/integration/transport_parity/test_fastapi_mcp_parity.py`
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py`
- `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py`
- `tests/integration/transports/test_transport_parity.py`
- `tests/integration/transports/test_override_transport_parity.py`
- `tests/integration/transports/test_cli_gate_decide.py`
- `tests/integration/transports/test_http_gate_endpoint.py`
- `tests/integration/transports/test_mcp_gate_decide_tool.py`
- `tests/structural/test_transport_parity_files_register_via_dsl.py`
- `tests/structural/test_transport_parity_dsl_registration_floor.py`
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-1.ready-for-review.md`
- `_bmad-output/implementation-artifacts/migration-7c-1-parity-contract-dsl-foundation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
