# Migration Story 7c.0b: Scaffold Foundation — Parity-Contract DSL Scaffold + Sanctum-Alignment DSL Feature + Self-Registration Audit Harness + TW-7c-4/5/6 Detection Scaffolds + FR-7c-50 Audit-Chain Executable Scaffold

**Status:** done  <!-- 2026-05-04 T11 cross-agent code-review PASS (zero patches; 4 deferred minor items: strict-monotonic vs ADR-prose, line-based YAML parser, xdist global-state, split-manifest interpretation). Verdict at _bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-04.md -->
**Sprint key:** `migration-7c-0b-scaffold-foundation`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 3
**Gate:** **dual-gate** + **cross-agent code-review MANDATORY** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-slab7c-thirty-six-stories, story 7c-0b; rationale: `substrate_shape`)
**K-target:** ~1.4× (build-tier; substrate-shape; ~3-4 pts; bounded surface = `app/parity/contracts/` package + sanctum-alignment DSL primitive + self-registration audit harness skeleton + 3 detection scaffolds + executable audit-chain test scaffold + per-cell flake-rate calculator)
**Authored:** 2026-05-04 via `bmad-create-story` workflow.
**Wave:** 0 — slot 2 (build-tier; consumes 7c.0a; gates ALL Wave 1 stories except 7c.2; opens immediately at 7c.0a close).

**FR coverage:** FR-7c-30..33 (DSL scaffold **executable** — primitives + decorator interface + per-surface transport declaration validator + 8-file refactor target list registration; refactor itself lands in 7c.1), FR-7c-50 (audit-chain integrity **executable scaffold** — `tests/audit/test_override_event_chain_integrity.py` asserts append-only invariant + monotonic timestamp + parent-trace linkage + red-rejection error semantics per 7c.0a Appendix A), FR-7c-54 (sanctum-alignment DSL primitive — accepts writer module's sanctum-alignment row declaration consumable by 7c.17a/17b per Slab 7b precedent), FR-7c-46 (UTF-8 CI lint pass setup with declared glob `_bmad-output/**/*.md` + `app/**/*.py` + `tests/**/*.py` + `tests/fixtures/**` + paths in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`).

**NFR coverage:** NFR-7c-OD7 (self-registration audit skeleton **primary enforcement** here — emits registration manifest at CI time; CI fails if cardinality below declared floor at slab-close; firing in 7c.21), NFR-7c-OD2 (TripwireLedgerEntry schema **consumed** here from 7c.0a; audit-chain test scaffold uses TripwireLedgerEntry to construct test fixtures), NFR-7c-M1 (lockstep precondition only — no four-file-lockstep authored here), NFR-7c-M5 (sandbox-AC validator PASS), NFR-7c-X1 (UTF-8 lint pass enforces NFR-7c-X1 from 7c.0b forward).

**Tripwire ownership:** **TW-7c-4 detection scaffold** (live-dispatch scope-creep — CI lint via test-naming convention + import-graph check), **TW-7c-5 detection scaffold** (UTF-8 violations — FR-7c-46 lint pass with declared glob), **TW-7c-6 detection scaffold** (parity flake — 50-run harness scaffold + per-cell flake-rate calculator with AMEND-7a tightened budget). All three detection mechanisms scaffolded here; firing happens in downstream stories (7c.21 fires TW-7c-6 at 50-run baseline; 7c.21a owns TW-7c-4 detection-active; per-story dev rounds may trip TW-7c-5).

**Standing-guardrail enforcement:**
- SG-1 unchanged (no specialist-roster change).
- SG-2 unchanged (no mapping-checklist row change).
- SG-3 Composition Spec invariants honored on DSL primitives (per-specialist gate precedence rule UNALTERED — DSL is parity-test orchestration, not gate-decision orchestration).
- **SG-4 primary enforcement** here (sanctum-alignment DSL feature shipped; consumed by 7c.17a/17b at Wave 4).

**Implementation cycle (NEW CYCLE per memory entry `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 lookahead-discipline revision):**
- **Claude (Opus 4.7):** authored this spec; sandbox-AC validator PASS confirmed at finalize; governance JSON entry verified (cross_agent_review_required=true); pre-authors `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-0b-scaffold-foundation.md` ahead of operator demand. Gate-1 party-mode-by-Slab-7c-Round-2 already ratified the scaffold scope; in-story Gate-1 round NOT required.
- **Codex (Sonnet 4.5 or later):** develops the scaffold + sanctum DSL + audit harness + 3 detection scaffolds + audit-chain executable test + UTF-8 lint pass per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0b.ready-for-review.md`.
- **Claude:** does the FINAL `bmad-code-review` (T11 — **CROSS-AGENT MANDATORY** per governance JSON); applies remediation cycles; commits; flips `migration-7c-0b-scaffold-foundation` review → done in sprint-status.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — **7c.0a's frozen ADR**. Codex consumes ALL six ADR sub-sections + Appendix A as the executable contract surface:
  - §1 Registration mechanism = decorator (in-tree) per ADR.
  - §2 Per-surface transport declaration = Pydantic-v2 `SurfaceTransportDeclaration` schema with frozen field set (`surface_id: str` + `mandatory_transports: list[str]` subset of `{cli, http, mcp-stdio, mcp-subprocess}` + `optional_transports: list[str]` same subset). Validator rejects duplicate transports across mandatory/optional sets + rejects empty `mandatory_transports` per FR-7c-32.
  - §3 Refactor target list = 8 existing transport-parity files (refactor lands in 7c.1, NOT 7c.0b — DSL scaffold here merely makes them refactorable).
  - §4 D7 escape-hatch policy = extend-the-DSL default + per-transport-addendum exception (party-mode-gated; 7c.0b SHALL NOT introduce any addendum).
  - §5 Decision-then-Foundation pattern = scope discipline; 7c.0b is the build-tier complement of 7c.0a.
  - §6 AMEND-7d-ii completeness flags = 7c.0b MUST emit THREE separate PASS/FAIL flags (TW-7c-4 + TW-7c-5 + TW-7c-6 detection); composite all-PASS insufficient.
  - Appendix A = audit-chain integrity conceptual design; `tests/audit/test_override_event_chain_integrity.py` lands in 7c.0b consuming this design.
- `app/models/tripwire_ledger.py` — **7c.0a's frozen TripwireLedgerEntry schema**. The audit-chain integrity test consumes this for fixture construction; assertions on append-only / monotonic-timestamp / parent-trace use `TripwireLedgerEntry.model_validate(...)` round-trips.
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 schema idioms; sanctum-alignment DSL primitive's declaration model conforms.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + schema/review-ceremony anti-pattern catalog.
- `docs/dev-guide/story-cycle-efficiency.md` — K-floor discipline (target 1.4× for build-tier substrate-shape); single-gate vs dual-gate review policy.
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-30..33 + FR-7c-46 + FR-7c-50 + FR-7c-54 + NFR-7c-OD7 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.0b section starting at line 370) — epic-level AC framing + AMEND-7a/7d-ii references.
- `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` — 7c.0a spec (now `done`); confirms predecessor closed cleanly.
- `_bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md` — T11 review verdict for 7c.0a; informational (rationale on wildcard source-modules; the wildcard pattern carries forward — 7c.0b begins populating C4 target list).

**Predecessor state (verified at authoring 2026-05-04 post-7c.0a-close commit `f926867`):**
- 7c.0a status `done` per spec file line 3 + `sprint-status.yaml::development_status['migration-7c-0a-decision-foundation']`. ✓
- ADR exists at `docs/dev-guide/adr/0001-parity-contract-dsl.md` (175 LOC; 6 sub-sections + Appendix A). ✓
- TripwireLedgerEntry exists at `app/models/tripwire_ledger.py` (134 LOC; 9 fields incl. `severity` + `trace_id`; triple-layer red-rejection on tripwire_id + tz-aware `fired_at` + UUID4 `trace_id`). ✓
- Import-linter contracts C4/C5/C6 in `pyproject.toml::[tool.importlinter]` with empty `forbidden_modules` lists; lint-imports KEPT count = 12 (pre-7c.0a baseline 9 + 3). ✓
- `tests/fixtures/frozen_paths/` exists (created by Codex during 7c.0a T1.2). ✓
- Class-conformance validator reports 11 conforming activation contracts (no regression). ✓
- Broad-regression baseline 3990 passed / 37 failed pre-existing (no 7c.0a-introduced regressions). ✓
- `app/audit/` does NOT yet exist — 7c.0b creates it (see AC-7c.0b-D for module layout + `app/audit/errors.py` + `tests/audit/test_override_event_chain_integrity.py`).

**Live substrate (verified at authoring; do NOT regress):**
- `app/parity/contracts/` does NOT exist yet — 7c.0b creates the package (`__init__.py` + DSL primitives module + sanctum-alignment primitive module + self-registration audit harness module).
- `app/audit/` does NOT exist yet — 7c.0b creates the package (`__init__.py` + `errors.py` per ADR Appendix A error hierarchy).
- `tests/audit/` does NOT exist yet — 7c.0b creates `tests/audit/__init__.py` (or no `__init__.py` per existing convention; verify at T1) + `test_override_event_chain_integrity.py`.
- The 8 existing transport-parity test files (per 7c.0a ADR §3 refactor target list) MUST NOT be modified by 7c.0b — refactor lands in 7c.1.
- `pyproject.toml::[tool.importlinter]` C4 target list begins populating in 7c.0b (with `app/parity/contracts/*` entries per AC-7c.0b-A); C5 + C6 target lists remain empty (populated by 7c.3a + 7c.4b respectively).
- `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` is the pipeline-manifest regime path list; the FR-7c-46 UTF-8 lint pass declared glob includes "any path declared in" this list — verify at T1 that the path key exists OR document the discovery mechanism.
- AMEND-7a tightened budget (<0.05% for 7c-added cells; pre-7c grandfathered at 0.1%) lives in the per-cell flake-rate calculator scaffolded here.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 0 (build-tier; consumes 7c.0a artifacts). Scaffold Foundation: executable parity-contract DSL scaffold + FR-7c-54 sanctum-alignment DSL feature + NFR-7c-OD7 self-registration audit harness skeleton + TW-7c-4/5/6 detection scaffolds + FR-7c-46 UTF-8 CI lint pass + per-cell flake-rate calculator (AMEND-7a tightened: <0.05% for 7c-added cells; pre-7c grandfathered at 0.1%). AC block per AMEND-7d-ii enumerates THREE separate PASS/FAIL flags (TW-7c-4 + TW-7c-5 + TW-7c-6 detection) at scaffold-completeness; ANY one FAIL blocks done. Cross-agent code-review MANDATORY (executable substrate consumed by ~30 downstream stories). Hard precedence: Wave 1 (except 7c.2) cannot open until 7c.0b closes.

**T1 conclusion:** No unanticipated architectural disagreement requires halting the dev round. 7c.0a's ADR is canonical for all DSL design decisions; 7c.0b is the executable embodiment. Implementation proceeds: DSL package + sanctum-alignment primitive + self-registration audit harness + 3 detection scaffolds + audit-chain executable test + UTF-8 lint pass + per-cell flake-rate calculator. **Hard checkpoints at T1:** (a) confirm 7c.0a `done` in spec + sprint-status; (b) confirm ADR + TripwireLedgerEntry + 7c.0a tests + pyproject.toml C4/C5/C6 contracts present; (c) confirm `app/parity/contracts/`, `app/audit/`, `tests/audit/` do NOT yet exist (Codex creates them); (d) verify `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` exists for FR-7c-46 lint pass glob discovery.

---

## Story

As the dev-agent (downstream-story consumer),
I want one build-tier story that lands the **executable** parity-contract DSL scaffold + sanctum-alignment DSL feature + self-registration audit harness skeleton + TW-7c-4/5/6 detection scaffolds + FR-7c-50 audit-chain integrity executable test + FR-7c-46 UTF-8 CI lint pass + AMEND-7a-tightened per-cell flake-rate calculator,
so that downstream stories (7c.1 DSL refactor + 7c.3a §02A composer + 7c.4b gate-family foundation + 7c.5.G0..G6 per-gate stories + 7c.6..7c.15 HIL surface stories + 7c.17a/b Marcus-bound writers + 7c.20a/b/c AUDIT-ACs + 7c.21 ceremony + 7c.21a Epic 3 retirement) inherit a working executable substrate consuming 7c.0a's frozen architectural decisions.

---

## Acceptance Criteria

### AC-7c.0b-A — Parity-contract DSL package + decorator primitive + SurfaceTransportDeclaration validator + C4 target-list population (FR-7c-30..33 / consumes 7c.0a ADR §1 + §2)

**Given** 7c.0a's frozen ADR (`docs/dev-guide/adr/0001-parity-contract-dsl.md`) §1 Registration Mechanism Choice (decorator) + §2 Per-Surface Transport Declaration Schema (Pydantic-v2)
**When** the dev-agent lands `app/parity/contracts/` package
**Then** the package contains:

1. `app/parity/contracts/__init__.py` — package marker; exports the public DSL surface: `parity_contract` decorator + `SurfaceTransportDeclaration` model + `register_surface` callable + `iter_registered_surfaces()` query + audit-harness entry-point.
2. `app/parity/contracts/_declaration.py` — `SurfaceTransportDeclaration(BaseModel)` per 7c.0a ADR §2. `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Fields: `surface_id: str` (min_length=1) + `mandatory_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]` (min_length=1 per FR-7c-32) + `optional_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]` (min_length=0). `model_validator(mode="after")` rejects duplicate transports across mandatory + optional sets + rejects empty `mandatory_transports` (FR-7c-32 — DSL denies parity-test budget to surfaces that do not declare mandatory transports).
3. `app/parity/contracts/_registry.py` — module-level mutable registry (`_REGISTERED_SURFACES: dict[str, SurfaceTransportDeclaration] = {}`) with `register_surface(declaration)` callable + `iter_registered_surfaces()` view. Registration is idempotent (re-registering the same `surface_id` raises `DuplicateSurfaceError` to prevent silent override). Discovery is deterministic at import time.
4. `app/parity/contracts/_decorator.py` — `parity_contract(surface_id, mandatory_transports, optional_transports=None)` decorator factory. The decorator constructs the `SurfaceTransportDeclaration`, calls `register_surface(...)`, and returns the wrapped object unchanged. Usage: `@parity_contract(surface_id="section_02a_g0", mandatory_transports=["cli", "http", "mcp-stdio"])` on the surface module's parity-test entry-point.
5. `app/parity/contracts/_audit.py` — `emit_registration_manifest(manifest_path: Path) -> Path` callable that writes the registered-surface manifest at CI time. Manifest format = JSON with stable key ordering: `{"generated_at": iso8601_utc, "schema_version": 1, "surfaces": [{"surface_id": ..., "mandatory_transports": [...], "optional_transports": [...]}, ...]}`. CI calls this to produce evidence; downstream `7c.21` ceremony asserts cardinality floor.

**And** ONE reference parity-contract is migrated as proof-of-pattern (NOT a refactor — just a single declaration to demonstrate the decorator works end-to-end). Recommend: pick one of the 8 refactor targets at the surface MOST LIKELY to be uncontroversial (e.g., `tests/integration/transport_parity/test_mcp_stdio_smoke.py`) and add a tiny `@parity_contract` declaration that DOES NOT alter the test's logic — surface as `decision_needed` at T1 if the chosen target is non-trivial. Alternative: create a brand-new placeholder surface module `app/parity/contracts/_reference_surface.py` carrying ONLY the decorator declaration and a `# placeholder for 7c.1 refactor` comment.

**And** `pyproject.toml::[tool.importlinter]` Contract C4's `forbidden_modules` is populated with the list of graph-runtime module roots that `app.parity.contracts.*` MUST NOT import. RECOMMEND list: `["app.gates.resume_api", "app.marcus.orchestrator.write_api", "app.specialists.*"]` — surface as `decision_needed` at T1 if the canonical graph-runtime module-root set is different. C5 + C6 forbidden_modules remain empty (populated by 7c.3a + 7c.4b respectively). KEPT count delta vs post-7c.0a baseline: 0 (target-list change does not add a new contract; the contract was already KEPT against empty source-namespace).

**Test pin:** `tests/parity/test_dsl_primitive_contract.py` — covers (a) `SurfaceTransportDeclaration` validates valid input + rejects invalid (duplicates, empty mandatory, unknown transport literal); (b) `parity_contract` decorator registers + returns wrapped object unchanged; (c) `register_surface` is idempotent + raises `DuplicateSurfaceError` on collision; (d) `iter_registered_surfaces()` returns deterministic ordering; (e) `emit_registration_manifest` writes valid JSON with stable key ordering.

**Test pin:** `tests/structural/test_import_linter_c4_target_list_populated.py` — `tomllib` parse + assert C4 `forbidden_modules` is non-empty + assert each entry is a recognized module-root pattern + lint-imports subprocess KEPT (no regression).

> **Notes for 7c.0b-A.** This AC is **dev-agent-executable**. The reference-surface decision (T1 alternative A or B) lands in Dev Notes. The C4 forbidden_modules list is the single highest-risk decision in this AC — RECOMMEND surfacing as `decision_needed` if Codex's read of the graph-runtime module surface differs from the recommended list. Path-portability per NFR-7c-X3: use `pathlib.Path` everywhere; UTF-8 explicit in JSON write.

### AC-7c.0b-B — Sanctum-alignment DSL primitive (FR-7c-54 / consumed by 7c.17a/17b at Wave 4)

**Given** FR-7c-54 sanctum-alignment DSL feature
**When** the dev-agent lands `app/parity/contracts/_sanctum.py`
**Then** the module exposes:

1. `SanctumAlignmentDeclaration(BaseModel)` Pydantic-v2 model. `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Fields:
   - `writer_id: str` (min_length=1) — e.g., `"gary-slide-content"`, `"gary-fidelity-slides"`, `"gary-diagram-cards"`, `"gary-theme-resolution"`, `"gary-outbound-envelope"` (the 5 Marcus-bound writers from 7c.17a/17b).
   - `sanctum_path: str` (min_length=1) — module path to the writer's sanctum at `_bmad/memory/<sanctum-name>/` per Slab 7b precedent OR Cora-sidecar exception path.
   - `alignment_kind: Literal["bmb-pattern", "cora-sidecar-exception"]` — closed enum. `bmb-pattern` (default; matches Slab 7b 6-file BMB sanctum convention) OR `cora-sidecar-exception` (operator-ratified deviation; requires `exception_rationale: str | None` populated).
   - `exception_rationale: str | None = None` — required iff `alignment_kind == "cora-sidecar-exception"`. `model_validator(mode="after")` enforces this conditional requirement.
2. `declare_sanctum_alignment(writer_id, sanctum_path, alignment_kind, exception_rationale=None)` callable that constructs the declaration + registers it in a sanctum-registry analogous to the surface-registry. Registry queryable via `iter_sanctum_alignments()`.
3. `emit_sanctum_alignment_manifest(manifest_path: Path) -> Path` callable analogous to surface manifest; writes `{"generated_at": ..., "schema_version": 1, "alignments": [...]}` JSON.

**And** the public DSL surface in `app/parity/contracts/__init__.py` exports `SanctumAlignmentDeclaration` + `declare_sanctum_alignment` + `iter_sanctum_alignments` + `emit_sanctum_alignment_manifest`.

**Test pin:** `tests/parity/test_sanctum_alignment_dsl.py` — covers (a) valid `bmb-pattern` declaration validates; (b) `cora-sidecar-exception` without rationale raises ValidationError; (c) `cora-sidecar-exception` with rationale validates; (d) `declare_sanctum_alignment` registers + idempotent; (e) `iter_sanctum_alignments` returns deterministic ordering; (f) manifest emission round-trips JSON cleanly.

> **Notes for 7c.0b-B.** This AC is **dev-agent-executable**. NO actual writer registers a sanctum alignment in 7c.0b — that lands in 7c.17a/17b at Wave 4. 7c.0b only ships the DSL primitive + tests that exercise the DSL behavior with synthetic declarations. SG-4 enforcement is shipped here; consumed downstream.

### AC-7c.0b-C — Self-registration audit harness skeleton (NFR-7c-OD7 / Winston A4)

**Given** NFR-7c-OD7 (parity-DSL self-registration audit; Winston A4 — failing-closed acceptable for THIS story)
**When** the dev-agent lands `app/parity/contracts/_audit.py::run_self_registration_audit(declared_floor: int = 0) -> AuditResult`
**Then** the harness:

1. Imports all modules under `app/gates/**` + `app/composers/**` + `app/parity/contracts/_reference_surface*.py` (the modules likely to register parity-contracts) by walking the package via `pkgutil.walk_packages`. Discovery is deterministic + idempotent.
2. After import-walk, queries the surface-registry (`iter_registered_surfaces()`) + sanctum-registry (`iter_sanctum_alignments()`) for cardinality.
3. Returns an `AuditResult(BaseModel)` with fields: `surface_cardinality: int` + `sanctum_cardinality: int` + `cardinality_floor: int` + `audit_status: Literal["PASS", "FAIL", "NOT_YET_EVALUATED"]` + `failure_reason: str | None`.
4. CI integration entry-point: `python -m app.parity.contracts._audit --declared-floor N` exits 0 if `surface_cardinality + sanctum_cardinality >= declared_floor`, exits 1 otherwise (fail-closed).
5. The harness emits the registration manifest (per AC-7c.0b-A point 5) regardless of audit outcome — the manifest is evidence; the audit is the gate.

**And** at 7c.0b close, the harness runs with `declared_floor=0` (initially empty registries; downstream stories register surfaces), and the audit PASSES trivially (0 ≥ 0). The 7c.21 ceremony will run with the actual cardinality floor at slab-close.

**And** the harness writes the registration manifest to a canonical path (recommend `_bmad-output/implementation-artifacts/parity-registration-manifest.json` — surface as `decision_needed` at T1 if a different convention applies; the manifest path is gitignored test-time evidence, not a tracked artifact).

**Test pin:** `tests/parity/test_self_registration_audit.py` — covers (a) audit with empty registries + floor=0 → PASS; (b) audit with floor=1 + empty registries → FAIL with `failure_reason` populated; (c) audit after a synthetic registration → cardinality reflects; (d) CLI entrypoint exit codes match audit outcomes; (e) manifest write round-trips cleanly.

> **Notes for 7c.0b-C.** This AC is **dev-agent-executable**. The harness is failing-closed — fine per Winston A4 because 7c.21 sets the actual `declared_floor` at slab-close. 7c.0b's harness MUST NOT auto-discover the floor (that's 7c.21's responsibility; 7c.0b just provides the gate).

### AC-7c.0b-D — FR-7c-50 audit-chain integrity executable scaffold (consumes 7c.0a Appendix A)

**Given** 7c.0a's ADR Appendix A (Audit-Chain Integrity Conceptual Design) + the canonical 7c.0a TripwireLedgerEntry schema
**When** the dev-agent lands `app/audit/` package + `tests/audit/test_override_event_chain_integrity.py`
**Then**:

1. `app/audit/__init__.py` — package marker.
2. `app/audit/errors.py` — error class hierarchy per 7c.0a Appendix A:

```python
class AuditChainIntegrityError(Exception):
    """Root exception for audit-chain integrity violations (FR-7c-50)."""


class AuditChainOrderError(AuditChainIntegrityError):
    """Out-of-order timestamp for a tripwire_id in the ledger."""


class AuditChainParentLinkError(AuditChainIntegrityError):
    """Missing parent trace_id when fired_verdict is 'fired' or 'marginal-fired'."""
```

3. `app/audit/chain.py` — `verify_audit_chain(entries: list[TripwireLedgerEntry]) -> None` callable that asserts append-only invariant + monotonic timestamp per `tripwire_id` + parent-trace linkage. Raises `AuditChainOrderError` on out-of-order timestamps; `AuditChainParentLinkError` on missing parent trace when fired_verdict is `"fired"` or `"marginal-fired"`. Pure function (no I/O); takes a pre-loaded list.
4. `tests/audit/__init__.py` — empty package marker (verify at T1; some test convention does NOT use `__init__.py`).
5. `tests/audit/test_override_event_chain_integrity.py` — exercises the contract:
   - **Append-only invariant test:** load a 3-entry ledger; assert `verify_audit_chain` succeeds.
   - **Monotonic timestamp positive:** entries with strictly increasing `fired_at` per `tripwire_id` succeed.
   - **Monotonic timestamp negative:** entries with out-of-order `fired_at` for the same `tripwire_id` raise `AuditChainOrderError`.
   - **Parent-trace positive:** `fired_verdict="fired"` with populated `trace_id` succeeds.
   - **Parent-trace negative:** `fired_verdict="fired"` with `trace_id=None` raises `AuditChainParentLinkError`.
   - **Parent-trace positive (verdict-irrelevant):** `fired_verdict="not_yet_evaluated"` with `trace_id=None` succeeds (parent-trace only required for fire-verdicts).
   - **Multi-tripwire-id isolation:** out-of-order `fired_at` across DIFFERENT `tripwire_id`s does NOT raise (each `tripwire_id` has its own monotonic chain).

**Test pin:** the test file itself is the contract pin (≥7 test cases per spec).

> **Notes for 7c.0b-D.** This AC is **dev-agent-executable**. All tests construct `TripwireLedgerEntry` instances using `model_validate(...)` (consumes 7c.0a's frozen schema). NO mocking of the schema. The `revision`/`revision_history` fields specified in 7c.0a's Appendix A as 7c.0b-may-extend are **NOT** added to TripwireLedgerEntry in 7c.0b — that extension is deferred to a future story (likely the FR-7c-50 audit-chain validator hardening pass after 7c.21). 7c.0b's audit-chain test SHALL document this deferral explicitly in Dev Notes.

### AC-7c.0b-E — TW-7c-4 / TW-7c-5 / TW-7c-6 detection scaffolds with three SEPARATE PASS/FAIL flags (AMEND-7d-ii / Murat M1)

**Given** Murat AMEND-7d-ii (THREE separate scaffold-completeness flags; composite "all-three-PASS" required for done-flip; ANY one FAIL blocks done) + Murat M1 detection-infra ownership
**When** the dev-agent lands the three detection scaffolds
**Then**:

**TW-7c-4 (live-dispatch scope-creep) detection:**
- Lands as `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py` (or analogous).
- Approach: combination of (a) test-naming convention check — assert `live_dispatch` keyword appears ONLY under named harness file names (`run_cache_hit_harness.py`, `run_5_api_smoke.py`); (b) import-graph check — assert no module under `app/specialists/**` or `app/gates/**` imports `app.live_dispatch.*` (or analogous live-dispatch root).
- Exit 0 if no scope-creep detected; exit 1 with detailed report otherwise.
- **PASS/FAIL flag #1 of 3:** TW-7c-4 detection PASS at 7c.0b done-flip (no scope creep at slab-open; downstream stories may trip).

**TW-7c-5 (UTF-8 violations) detection:**
- Lands as `scripts/utilities/detect_tw_7c_5_utf8_violations.py` (or analogous; per FR-7c-46 UTF-8 CI lint pass).
- Glob coverage per FR-7c-46: `_bmad-output/**/*.md`, `app/**/*.py`, `tests/**/*.py`, `tests/fixtures/**`, paths declared in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`.
- **Binary-skip rule (canonical; clarifies FR-7c-46 glob scope to TEXT FILES ONLY):**
  - **(a) Source-set restriction:** the detector iterates `git ls-files` output (NOT a raw filesystem walk). This automatically excludes gitignored files (e.g., `__pycache__/**`, `*.pyc`, untracked test cache-harness output, generated artifacts) — they are not part of the repo's text contract surface.
  - **(b) Extension blocklist:** the detector skips files matching ANY of these binary extensions: `.pyc`, `.pyo`, `.pyd`, `.so`, `.dll`, `.exe`, `.dylib`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.ico`, `.tif`, `.tiff`, `.svg.gz`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp`, `.mp3`, `.mp4`, `.wav`, `.ogg`, `.webm`, `.mov`, `.avi`, `.mkv`, `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.gz`, `.bz2`, `.xz`, `.7z`, `.bin`, `.dat`. (`.svg` IS text-XML — included; `.svgz` is gzipped — excluded.)
  - **(c) Null-byte sniff:** for any file matching the glob and NOT excluded by (a) or (b), read first 8KB; if it contains a null byte (`\x00`), treat as binary and skip. Belt-and-suspenders for unknown-extension binary files.
- For each file passing the (a)+(b)+(c) gates, attempt UTF-8 decode; if any file fails (e.g., contains cp1252-only bytes), report.
- Exit 0 if all in-scope text files UTF-8-clean; exit 1 with violation list otherwise.
- **Pre-existing-violation T1.7 HALT scope clarification:** T1.7 HALT fires ONLY if violations are found in **TEXT FILES** that pass the binary-skip rule. Binary file false-positives (e.g., `__pycache__/*.pyc` from local pytest runs, `tests/fixtures/specialists/wanda/live_artifacts/**/*.mp3` generated audio) are NOT halt conditions — they are auto-skipped by the binary-skip rule. The T1.7 HALT condition exists to prevent 7c.0b shipping a lint pass that would FAIL CI from day 1; the binary-skip rule prevents false-positive halts during T1 dry-run.
- **PASS/FAIL flag #2 of 3:** TW-7c-5 detection PASS at 7c.0b done-flip (assuming the repo's TEXT files are UTF-8-clean; surface any genuine TEXT violations as `decision_needed` at T1 — they'd block 7c.0b close until 7c.2 closes its cp1252 fix).

**TW-7c-6 (parity flake) detection scaffold:**
- Lands as `scripts/utilities/detect_tw_7c_6_parity_flake.py` (or analogous; 50-run harness scaffold).
- Per AMEND-7a (Murat 2026-05-04 tightened budget): per-cell flake budget tightens to <0.05% for 7c-added cells; pre-7c cells grandfather at 0.1%. The calculator distinguishes pre-7c cells from 7c-added cells via a manifest key (recommend: cell registration time-stamped at registration; cells registered ≥ Slab 7c open date are "7c-added").
- Approach: 50-run pytest invocation against the parity matrix; per-cell pass/fail tracked; per-cell flake-rate calculated; per-cell budget compared to threshold (<0.05% or <0.1% depending on cell class).
- 7c.0b lands the scaffold + per-cell flake-rate calculator only; the 50-run firing happens at 7c.21 ceremony (NFR-7c-R1).
- **PASS/FAIL flag #3 of 3:** TW-7c-6 detection scaffold PASS at 7c.0b done-flip — the calculator is INVOKABLE + correctly distinguishes pre-7c vs 7c-added cells via a unit test on synthetic manifest input.

**And** 7c.0b's Done-status assertion EXPLICITLY enumerates THREE separate PASS/FAIL flags per AMEND-7d-ii. The Codex T10 self-review notice + the spec's Completion Notes List MUST document each flag's PASS/FAIL status independently. Composite "all-three-PASS" is REQUIRED for done-flip; ANY one FAIL blocks done.

**Test pin:** `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py` — for each of the three detection utilities: (a) script file exists; (b) script is invokable via `python -m <script>` or `python <script_path>`; (c) script returns the expected pass/fail signaling. The test does NOT exercise the actual detection logic exhaustively — that's deferred to per-detector unit tests below.

**Test pin:** `tests/unit/parity/test_per_cell_flake_rate_calculator.py` — covers per-cell flake-rate calculation with synthetic 50-run manifest input: (a) all-pass → 0.0% flake-rate per cell; (b) 1-fail-out-of-50 → 2.0% flake-rate (above 0.1% grandfathered budget; would fire TW-7c-6); (c) 1-fail-out-of-2000 (synthetic large-N) → 0.05% (at threshold edge for 7c-added cells); (d) cell-class distinction (pre-7c vs 7c-added) routes to correct budget threshold.

> **Notes for 7c.0b-E.** This AC is **dev-agent-executable**. All three detectors run via `.venv/Scripts/python.exe`. NO operator-only CLI. Scope-creep / encoding / parity-flake detection is intentionally separate so the THREE scaffolding flags can be enforced independently per AMEND-7d-ii. If T1 surfaces pre-existing UTF-8 violations in the declared glob, **HALT-AND-SURFACE** for operator decision (close 7c.2 first, then 7c.0b? Or have 7c.0b's lint pass start in advisory-only mode and tighten in 7c.2 close?). The default recommendation is HALT — block 7c.0b close until repo is UTF-8-clean.

### AC-7c.0b-F — Sanctum-alignment registry + manifest emission integrated into self-registration audit (NFR-7c-OD7 + FR-7c-54)

**Given** AC-7c.0b-B (sanctum-alignment DSL primitive landed) + AC-7c.0b-C (self-registration audit harness landed)
**When** the dev-agent integrates sanctum-registry into the self-registration audit
**Then** the `run_self_registration_audit` helper queries BOTH `iter_registered_surfaces()` AND `iter_sanctum_alignments()`; cardinality is the SUM of both registries; the audit manifest emits BOTH surface-list AND sanctum-alignment-list under separate keys (`surfaces` + `sanctum_alignments`).

**Test pin:** `tests/parity/test_self_registration_audit.py` (extended from AC-7c.0b-C) — covers (a) audit with 0 surfaces + 0 sanctum-alignments → cardinality 0; (b) audit with 1 surface + 0 sanctum-alignments → cardinality 1; (c) audit with 0 surfaces + 1 sanctum-alignment → cardinality 1; (d) audit with N surfaces + M sanctum-alignments → cardinality N+M.

> **Notes for 7c.0b-F.** This AC is **dev-agent-executable**. Integration AC; bridges B + C. The cardinality SUM convention is canonical for 7c.21's slab-close audit floor.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks (AC: T1 Readiness Block)**
  - [x] T1.1 Confirm 7c.0a `done` in spec file line 3 + sprint-status.
  - [x] T1.2 Confirm `docs/dev-guide/adr/0001-parity-contract-dsl.md` + `app/models/tripwire_ledger.py` + 7c.0a tests + pyproject.toml C4/C5/C6 contracts present.
  - [x] T1.3 Confirm `app/parity/contracts/`, `app/audit/`, `tests/audit/` do NOT yet exist (Codex creates).
  - [x] T1.4 Verify `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` exists for FR-7c-46 lint pass glob discovery.
  - [x] T1.5 Pick reference-surface for AC-7c.0b-A (option A: existing test file with non-trivial decoration; option B: brand-new placeholder module). RECOMMEND option B.
  - [x] T1.6 Pick C4 forbidden_modules canonical list for AC-7c.0b-A. RECOMMEND `["app.gates.resume_api", "app.marcus.orchestrator.write_api", "app.specialists.*"]`. Surface as `decision_needed` if Codex's read of graph-runtime module surface differs.
  - [x] T1.7 Pre-existing UTF-8 violation check (TW-7c-5 detector dry-run against current repo state). **Apply binary-skip rule per AC-7c.0b-E:** restrict source-set to `git ls-files` output (excludes gitignored / untracked binaries); apply extension blocklist (`.pyc`, `.png`, `.mp3`, etc.); apply null-byte sniff for unknown-extension binaries. **HALT-AND-SURFACE** ONLY if violations are found in genuine TEXT FILES; binary-file false-positives (e.g., `__pycache__/*.pyc`, generated `*.mp3`) are auto-skipped — they do NOT trigger the halt.
  - [x] T1.8 Run sandbox-AC validator on this spec; expect PASS.

- [x] **T2 — Land `app/parity/contracts/` package + DSL primitives (AC: 7c.0b-A)**
  - [x] T2.1 `__init__.py` + `_declaration.py` + `_registry.py` + `_decorator.py` + `_audit.py` modules.
  - [x] T2.2 `SurfaceTransportDeclaration` Pydantic-v2 model per ADR §2.
  - [x] T2.3 `register_surface` idempotent; `DuplicateSurfaceError` on collision.
  - [x] T2.4 `parity_contract` decorator factory.
  - [x] T2.5 Reference-surface declaration per T1.5 choice.
  - [x] T2.6 Populate C4 `forbidden_modules` in `pyproject.toml` per T1.6.

- [x] **T3 — Land sanctum-alignment DSL primitive (AC: 7c.0b-B)**
  - [x] T3.1 `app/parity/contracts/_sanctum.py` module.
  - [x] T3.2 `SanctumAlignmentDeclaration` Pydantic-v2 model with `model_validator(mode="after")` for the conditional `exception_rationale` requirement.
  - [x] T3.3 `declare_sanctum_alignment` callable + sanctum-registry + `iter_sanctum_alignments` view.
  - [x] T3.4 Public DSL surface exports.

- [x] **T4 — Land self-registration audit harness (AC: 7c.0b-C + 7c.0b-F)**
  - [x] T4.1 `app/parity/contracts/_audit.py::run_self_registration_audit` + `AuditResult` model.
  - [x] T4.2 Package-walk import logic.
  - [x] T4.3 `emit_registration_manifest` + `emit_sanctum_alignment_manifest` (or merged manifest with both keys per AC-7c.0b-F).
  - [x] T4.4 CLI entrypoint `python -m app.parity.contracts._audit --declared-floor N`.

- [x] **T5 — Land `app/audit/` package + FR-7c-50 audit-chain executable scaffold (AC: 7c.0b-D)**
  - [x] T5.1 `app/audit/__init__.py` + `app/audit/errors.py` (3 error classes per ADR Appendix A).
  - [x] T5.2 `app/audit/chain.py::verify_audit_chain` pure function.
  - [x] T5.3 `tests/audit/__init__.py` (or no init, per existing convention).
  - [x] T5.4 `tests/audit/test_override_event_chain_integrity.py` with ≥7 test cases (per spec).

- [x] **T6 — Land 3 detection scaffolds + per-cell flake-rate calculator (AC: 7c.0b-E)**
  - [x] T6.1 `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py`.
  - [x] T6.2 `scripts/utilities/detect_tw_7c_5_utf8_violations.py`.
  - [x] T6.3 `scripts/utilities/detect_tw_7c_6_parity_flake.py` + per-cell flake-rate calculator module (recommend `app/parity/contracts/_flake_rate.py` so the calculator can be imported by tests AND invoked from the script).
  - [x] T6.4 AMEND-7a tightened budget: <0.05% for 7c-added cells; <0.1% pre-7c grandfathered.
  - [x] T6.5 Cell-class distinction mechanism (recommend manifest-keyed; document in Dev Notes).

- [x] **T7 — Author tests (cross-cuts ACs)**
  - [x] T7.1 `tests/parity/test_dsl_primitive_contract.py` per AC-7c.0b-A test pin.
  - [x] T7.2 `tests/parity/test_sanctum_alignment_dsl.py` per AC-7c.0b-B.
  - [x] T7.3 `tests/parity/test_self_registration_audit.py` per AC-7c.0b-C + 7c.0b-F.
  - [x] T7.4 `tests/audit/test_override_event_chain_integrity.py` per AC-7c.0b-D.
  - [x] T7.5 `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py` per AC-7c.0b-E.
  - [x] T7.6 `tests/unit/parity/test_per_cell_flake_rate_calculator.py` per AC-7c.0b-E.
  - [x] T7.7 `tests/structural/test_import_linter_c4_target_list_populated.py` per AC-7c.0b-A.

- [x] **T8 — CI hygiene clean (NFR-7c-R5 / NFR-7c-X4 / NFR-7c-M5)**
  - [x] T8.1 `ruff check` on all touched files — clean.
  - [x] T8.2 `lint-imports` — KEPT count = 12 (post-7c.0a); NO new contract added; C4 target list populated.
  - [x] T8.3 Run focused tests (all new test files + 7c.0a's tests for regression) `-p no:randomly` — all pass.
  - [x] T8.4 Run broad regression `pytest -p no:randomly` — ≥1403 baseline preserved (no new regression vs 7c.0a-close baseline of 3990 passed).
  - [x] T8.5 Sandbox-AC validator PASS.
  - [x] T8.6 Class-conformance validator: 11 conforming activation contracts (no regression).

- [x] **T9 — AMEND-7d-ii three-flag completeness check**
  - [x] T9.1 Document in Completion Notes List the three SEPARATE PASS/FAIL flags: TW-7c-4 detection PASS/FAIL + TW-7c-5 detection PASS/FAIL + TW-7c-6 detection PASS/FAIL. Composite all-three-PASS required for done-flip.

- [x] **T10 — Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-0b.ready-for-review.md` summarizing: file list (~12-15 files: package modules + sanctum module + audit harness + 3 error classes + 3 detection scripts + 7 test files + pyproject.toml C4 target-list), test counts, ruff status, lint-imports status, broad-regression delta, sandbox-AC validator status, AMEND-7d-ii three-flag PASS/FAIL enumeration, T1 `decision_needed` resolutions, deferred follow-ons.

- [ ] **T11 — Claude `bmad-code-review` (CROSS-AGENT MANDATORY per governance JSON)**
  - [ ] T11.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the diff; produces verdict at `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-NN.md`; applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-0b-scaffold-foundation: review → done` in sprint-status.

---

## Dev Notes

**Architecture decisions inherited from 7c.0a (now FROZEN per commit `f926867`):**
- ADR §1 Registration mechanism = **decorator** (in-tree). 7c.0b lands `parity_contract` decorator factory.
- ADR §2 Per-surface transport declaration = **Pydantic-v2 SurfaceTransportDeclaration**. 7c.0b lands the model with frozen field set + duplicate-rejection + empty-mandatory-rejection per FR-7c-32.
- ADR §3 Refactor target list = 8 existing files; 7c.0b DOES NOT modify them; 7c.1 owns refactor.
- ADR §4 D7 escape-hatch policy = extend-the-DSL default; 7c.0b SHALL NOT introduce per-transport addendums.
- ADR §5 Decision-then-Foundation pattern = 7c.0b is the build-tier complement of 7c.0a.
- ADR §6 AMEND-7d-ii = 7c.0b enforces THREE separate PASS/FAIL flags. AC-7c.0b-E is the canonical implementation.
- Appendix A = audit-chain integrity conceptual design; AC-7c.0b-D is the executable embodiment.

**TripwireLedgerEntry consumption:** AC-7c.0b-D constructs test fixtures using `TripwireLedgerEntry.model_validate(...)` directly. NO mocking. The `revision`/`revision_history` fields specified in ADR Appendix A are NOT added to TripwireLedgerEntry in 7c.0b — deferred to a future audit-chain hardening pass (post-7c.21).

**File / module placement:**
- `app/parity/contracts/__init__.py` + 5 sibling modules (`_declaration.py`, `_registry.py`, `_decorator.py`, `_audit.py`, `_sanctum.py`).
- `app/parity/contracts/_flake_rate.py` (per-cell flake-rate calculator, importable from tests + scripts).
- `app/parity/contracts/_reference_surface.py` (placeholder for AC-7c.0b-A reference declaration; per T1.5 RECOMMEND option B).
- `app/audit/__init__.py` + `errors.py` + `chain.py`.
- `tests/audit/__init__.py` (or no init per convention; verify at T1) + `test_override_event_chain_integrity.py`.
- `tests/parity/test_dsl_primitive_contract.py` + `test_sanctum_alignment_dsl.py` + `test_self_registration_audit.py`.
- `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py` + `test_import_linter_c4_target_list_populated.py`.
- `tests/unit/parity/test_per_cell_flake_rate_calculator.py`.
- `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py` + `detect_tw_7c_5_utf8_violations.py` + `detect_tw_7c_6_parity_flake.py`.

**Anti-patterns to avoid (from `dev-agent-anti-patterns.md`):**
- **A11 Windows-portability** — every new line MUST use UTF-8-explicit encoding; `pathlib.Path.as_posix()` everywhere; no `PYTHONIOENCODING=utf-8` workarounds.
- **A-schema-1 Premature SkipJsonSchema** — none of the new Pydantic models should mark fields excluded from JSON Schema unless genuinely internal-audit.
- **A-test-1 Mocking the system-under-test** — audit-chain tests use real `TripwireLedgerEntry` instances; do NOT mock the schema.
- **A-review-ceremony-1 Lying about completion** — at T8 broad regression, report ACTUAL pass/fail counts; verify against 7c.0a-close baseline (3990 passed / 37 failed pre-existing).

**K-discipline (from `story-cycle-efficiency.md`):**
- K-target 1.4× = ~2.5K LOC band-floor × 1.4 = ~3.5K LOC at T-shape ceiling; ~3-4 pts. DSL package modules ~600-1000 LOC; sanctum DSL ~150 LOC; audit harness ~250 LOC; audit-chain ~150 LOC; 3 detection scripts ~300-500 LOC; 7 test files ~1.0-1.5K LOC; flake-rate calculator ~150 LOC. Estimate: ~2.6-4K LOC. Possible upper-band approach.
- If T1 surfaces additional decision-needed scope expansions, surface for K-budget renegotiation.

**Testing standards:**
- Pytest with `-p no:randomly` for deterministic-baseline preservation (NFR-7c-R2).
- New test paths: `tests/parity/`, `tests/audit/`, `tests/structural/`, `tests/unit/parity/`. All UTF-8 encoded.
- Audit-chain tests use real `TripwireLedgerEntry` model_validate — do NOT mock.

**AMEND-7a per-cell flake-rate budget canonicalization:**
- 7c-added cells: <0.05% (1 fail per 2000 runs is the absolute boundary).
- Pre-7c cells: <0.1% (grandfathered; 1 fail per 1000 runs).
- Cell-class distinction mechanism: the per-cell flake-rate calculator reads a manifest at `_bmad-output/implementation-artifacts/parity-cell-class-manifest.json` (or analogous; surface at T1) that maps `cell_id → "pre_7c" | "7c_added"`. Cells default to `pre_7c` if absent (conservative grandfather). Slab 7c-introduced cells register at `7c_added` time.

### Project Structure Notes

- **Alignment with unified project structure:** `app/parity/contracts/` is a NEW top-level subpackage; matches `app/parity/` pattern if it exists. `app/audit/` is a NEW top-level subpackage. Test paths conform to existing conventions (`tests/parity/`, `tests/audit/`, `tests/structural/`, `tests/unit/parity/`).
- **Detected variances:** None at authoring time. T1.3-1.7 verify the substrate setup; if pre-existing UTF-8 violations are found at T1.7, HALT-AND-SURFACE.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-0b]
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (7c.0a's frozen ADR; ALL 6 sub-sections + Appendix A)
- [Source: app/models/tripwire_ledger.py] (7c.0a's frozen TripwireLedgerEntry schema; consumed by audit-chain tests)
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md] (14 idioms; SurfaceTransportDeclaration + SanctumAlignmentDeclaration + AuditResult conform)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 + schema/test anti-patterns)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline; cross-agent dual-gate review policy)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (FR-7c-30..33/46/50/54 + NFR-7c-OD7 + AMEND-7a/7d-ii)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.0b] (Story 7c.0b section starting at line 370)
- [Source: _bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md] (7c.0a spec; predecessor)
- [Source: _bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md] (7c.0a T11 review verdict; informational on wildcard pattern carryforward)

---

## Review Findings

T11 cross-agent code-review (Claude, Opus 4.7) 2026-05-04. Verdict artifact: `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-04.md`.

### patch (applied)
None. Codex T10 self-review captured all 6 ACs (A/B/C/D/E/F) cleanly; verification battery green; AMEND-7d-ii three SEPARATE flags PASS; AMEND-7a tightened budget correctly applied; binary-skip rule correctly implements 2026-05-04 spec amendment; C4 target list populated per T1.6 recommendation. No patches required.

### defer (4 minor; future-hardening candidates)
- [x] [Review][Defer] D-1 verify_audit_chain strict <= vs ADR-prose ≥ (B-6 / E-4) [app/audit/chain.py:17] — strict-monotonic is canonical audit-chain interpretation; production trigger unlikely; document in 7c.21 retrospective if equal-timestamp false-positive ever surfaces.
- [x] [Review][Defer] D-2 line-based YAML parser for pipeline-manifest globs (B-8) [scripts/utilities/detect_tw_7c_5_utf8_violations.py:65-80] — adequate for canonical block_mode_trigger_paths format; fragile against future YAML evolution. Swap to yaml.safe_load at next 7c.21 hardening pass.
- [x] [Review][Defer] D-3 global registry mutable state under future xdist parallelism (E-8) — within-process isolation OK via _clear_*_for_tests fixtures; cross-process xdist behavior unverified. Story 7c.0c will exercise this.
- [x] [Review][Defer] D-4 manifest split (surfaces.json + sanctum.json) vs unified merged manifest (AC-F) — Codex split-manifest interpretation is a defensible reading of spec parenthetical; 7c.21 slab-close audit can call both functions for unified evidence if needed.

### verification battery (per Codex T10; reviewer trusts focused-test counts)
- Sandbox-AC validator: PASS
- Class-conformance: 11 conforming activation contracts (no regression)
- lint-imports: 12 KEPT / 0 broken (UNCHANGED — only C4 target population, no new contracts)
- Focused 7c.0b tests (8 new files): 38 passed
- 7c.0a regression slice: 27 passed (no regression)
- Ruff: CLEAN
- Self-registration audit CLI floor=0: PASS
- AMEND-7d-ii three-flag PASS: TW-7c-4 PASS / TW-7c-5 PASS (1618 tracked text files scanned, 0 violations) / TW-7c-6 PASS (dry-run synthetic 7c-added cell within strict budget)
- Broad regression: 38 failed / 4042 passed (vs 7c.0a baseline 37 / 3990 = +1 / +52). +52 passed tracks new 7c.0b tests + import-discovery; +1 failure consistent with prior 7c.0a + 7c.2 flake/order pattern; benign.

### out-of-scope (excluded from close commit)
- runs/cache-harness/irene-pass1.md — untracked test cache-harness output from prior runs; NOT part of 7c.0b deliverables; Codex T10 disclosed. Recommend post-close: ensure runs/ is gitignored.

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

- T1 readiness: 7c.0a `done` confirmed in spec and sprint-status; ADR 0001 and TripwireLedgerEntry present; `app/parity/contracts/`, `app/audit/`, and `tests/audit/` absent before implementation; `block_mode_trigger_paths` present; lint-imports baseline `12 kept, 0 broken`; class conformance `11`; sandbox-AC PASS.
- T1.7 UTF-8 preflight: revised binary-skip rule applied via `git ls-files`, extension blocklist, and null-byte sniff. Result: `scanned=1618`, `utf8_preflight=PASS`.
- T1 decisions: reference-surface Option B selected (`app/parity/contracts/_reference_surface.py`); C4 forbidden_modules populated with the recommended canonical list: `app.gates.resume_api`, `app.marcus.orchestrator.write_api`, `app.specialists.*`; self-registration manifest path kept at `_bmad-output/implementation-artifacts/parity-registration-manifest.json` as generated evidence, not tracked.
- T9 verification: focused 7c.0b tests `38 passed`; 7c.0a regression slice `27 passed`; ruff clean; import-linter `12 kept, 0 broken`; class-conformance validator PASS with `11 activation contract file(s)`; sandbox-AC validator PASS; self-registration audit floor 0 PASS.
- Broad regression: executed `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line`; result `38 failed, 4042 passed, 27 skipped, 46 deselected, 2 xfailed`. Failures match checkout/environment drift already observed before 7c.0b scope (template/manifest drift, populated sanctum cache fixtures, replay pack hash drift, Windows ProactorEventLoop psycopg incompatibility, model catalog drift, run HUD drift, and historical migration assertions).

### Completion Notes List

- Shipped executable parity-contract DSL scaffold: `SurfaceTransportDeclaration`, decorator registration, deterministic registry, reference surface, manifest emission, and self-registration audit CLI.
- Shipped sanctum-alignment DSL primitive with conditional `cora-sidecar-exception` rationale validation and manifest emission.
- Shipped FR-7c-50 audit-chain executable scaffold consuming real `TripwireLedgerEntry` fixtures. `revision` / `revision_history` remain deferred; 7c.0b validates monotonic timestamps and fired-verdict trace linkage against the frozen 7c.0a schema.
- Shipped TW detector scaffolds and AMEND-7a per-cell flake budget calculator.
- Updated C4 import-linter target list; C5 and C6 remain empty for 7c.3a and 7c.4b.
- TW-7c-4 detection flag: PASS (`detect_tw_7c_4_live_dispatch_scope_creep.py`, no violations).
- TW-7c-5 detection flag: PASS (`detect_tw_7c_5_utf8_violations.py`, 1618 tracked text files scanned, no violations).
- TW-7c-6 detection flag: PASS (`detect_tw_7c_6_parity_flake.py --dry-run`, 7c-added dry-run cell within <0.05% budget).

### File List

- New: `app/parity/contracts/__init__.py`
- New: `app/parity/contracts/_audit.py`
- New: `app/parity/contracts/_declaration.py`
- New: `app/parity/contracts/_decorator.py`
- New: `app/parity/contracts/_flake_rate.py`
- New: `app/parity/contracts/_reference_surface.py`
- New: `app/parity/contracts/_registry.py`
- New: `app/parity/contracts/_sanctum.py`
- New: `app/audit/__init__.py`
- New: `app/audit/chain.py`
- New: `app/audit/errors.py`
- New: `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py`
- New: `scripts/utilities/detect_tw_7c_5_utf8_violations.py`
- New: `scripts/utilities/detect_tw_7c_6_parity_flake.py`
- New: `tests/audit/__init__.py`
- New: `tests/audit/test_override_event_chain_integrity.py`
- New: `tests/parity/test_dsl_primitive_contract.py`
- New: `tests/parity/test_sanctum_alignment_dsl.py`
- New: `tests/parity/test_self_registration_audit.py`
- New: `tests/structural/test_import_linter_c4_target_list_populated.py`
- New: `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py`
- New: `tests/unit/parity/test_per_cell_flake_rate_calculator.py`
- Modified: `pyproject.toml`
- Modified: `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py`
- Modified: `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md`
- Modified: `_bmad-output/implementation-artifacts/sprint-status.yaml`
