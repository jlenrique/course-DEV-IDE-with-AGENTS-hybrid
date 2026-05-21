# Migration Story 7c.3b: §02A G0 Poll-Surface Canonical HIL Pattern — Pattern Author for 10 Wave-3 HIL Surfaces

**Status:** review *(spec authored 2026-05-05; predecessor 7c-3a CLOSED `done` with `Directive` + `DirectiveSource` models frozen; Codex dev-story completed 2026-05-05 and ready for T11 review.)*
**Sprint key:** `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**Gate:** **dual-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-velocity-amendments-bundle, story 7c-3b; rationale: `substrate_shape` — pattern-author for 10 Wave-3 HIL surface replications)
**K-target:** ~1.4× (substrate-shape pattern-author; ~2-3 pts; bounded surface = §02A G0 poll-surface module + 3 transport handlers + per-surface OperatorVerdict variant + parity-contract registration + 4 tests)
**R-tier (regression scope):** **R2** — focused + impact-zone + smoke. Pattern-author story; downstream consumers (7c.6..15) inherit the pattern but don't share tight runtime coupling, so R2 (smoke) is sufficient. R3 NOT required (no broad-substrate change).
**T11-tier (review approach):** **standard** — single-gate-or-dual; pattern-author for 10 downstream stories warrants 3-layer Blind/Edge/Auditor review on the canonical pattern.
**Files touched (declared at spec-author time):**
- `app/gates/section_02a/__init__.py` (NEW; package marker + public exports)
- `app/gates/section_02a/poll_surface.py` (NEW; G0 poll-surface module with `display_directive` + `submit_verdict` callables)
- `app/gates/section_02a/_transports.py` (NEW; CLI + HTTP + MCP-stdio transport handlers OR delegate to existing transport scaffolding if present — verify at T1)
- `app/models/operator_verdict_section_02a.py` (NEW; OR extend existing operator_verdict.py with §02A discriminated-union variant — verify at T1)
- `tests/gates/section_02a/__init__.py` (NEW package marker)
- `tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py` (NEW; AC-A test pin)
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` (NEW; AC-B test pin)
- `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py` (NEW; AC-C test pin — parity-contract registration via `@parity_contract`)
- `tests/schemas/operator_verdict/test_section_02a_shape.py` (NEW; AC-D test pin — FR-7c-49 schema-stability across 3 transports)
**Lookahead tier:** **2 → AUTHORED** — was Tier 2 (skeleton-ahead with placeholders); upgraded to AUTHORED at 2026-05-05 once 7c.3a closed (Directive + DirectiveSource models now frozen).
**Authored:** 2026-05-05 via `bmad-create-story` workflow + AMEND-V5 lookahead Tier 2 promotion post-predecessor-close.
**Wave:** 1 — slot 4 (pattern-author for 10 Wave-3 HIL surfaces).

**FR coverage:**
- **FR-7c-3** Operator can review composed directive at §02A poll surface and emit {approve, edit, reject} verdicts via CLI / FastAPI / MCP-stdio with verdict-digest match enforced on resume.
- **FR-7c-4** Operator can edit field-level directive values at §02A poll surface and have edited directive re-validated before submission.
- **FR-7c-20** Each HIL surface declares mandatory transports at slab-open via parity-contract DSL (FR-7c-30..33) + self-registers into the parameterized parity-test harness.
- **FR-7c-49 (registration of §02A case)** per-HIL-surface `OperatorVerdict` schema-stability case for §02A.

**NFR coverage:**
- **NFR-7c-P4** HIL surface poll latency ≤2s p99 in-process per transport (CLI / HTTP); ≤4s p99 MCP-stdio.
- **NFR-7c-S1** HIL tamper-evidence at writer boundary per D3 — `OperatorVerdict.decision_card_digest` matches emitted card; resume rejects via `GateError` on mismatch.
- **NFR-7c-X2** Multi-transport byte-equivalence: same `OperatorVerdict` payload via CLI / HTTP / MCP-stdio produces byte-identical (or canonicalized-identical) graph-resumption state, identical ledger events, identical LangSmith traces.
- **NFR-7c-M5** sandbox-AC validator PASS.

**Standing-guardrail enforcement:**
- SG-1 unchanged.
- SG-2 §02A row in mapping checklist preserved + status improved at retrospective (canonical HIL pattern landed).
- SG-3 Composition Spec §6 (HIL pattern) — ESTABLISHES the canonical pattern for §04A..§15. SG-3 primary enforcement here.
- SG-4 unchanged.

**Tripwire ownership:** none direct. Pattern-author story; downstream consumers inherit but don't fire tripwires.

**Implementation cycle (NEW CYCLE):**
- **Claude (Opus 4.7):** authored this spec 2026-05-05 to immediately unblock Codex; sandbox-AC validator PASS; pre-authored `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops poll-surface module + 3 transport handlers + OperatorVerdict variant + 4 tests + parity-contract registration per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-3b.ready-for-review.md`.
- **Claude T11 standard review:** verifies the canonical pattern is replicable (10 Wave-3 stories will copy) + 3-transport byte-equivalence + verdict-digest match + field-level edit re-validation. Commits + flips `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern: review → done`.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `app/composers/section_02a/directive_model.py` — 7c.3a's frozen `Directive` + `DirectiveSource` + `DirectiveRole` + `ExcludedReason` Pydantic v2 models. The poll surface displays a `Directive` instance + accepts edits that produce new validated `Directive` instances.
- `app/composers/section_02a/__init__.py` — public surface (post-7c.3a). Imports: `Directive`, `DirectiveSource`, `DirectiveRole`, `ExcludedReason`.
- `app/parity/contracts/__init__.py` — DSL primitives (post-7c.0b/7c.1). `@parity_contract` decorator + `SurfaceTransportDeclaration` model.
- `app/models/operator_verdict.py` (existing; verify at T1) OR analogous — the `OperatorVerdict` discriminated-union root model. The §02A variant either extends this OR lives in a sibling file; surface as `decision_needed` at T1.
- `app/audit/__init__.py` — `verify_audit_chain` + error classes (post-7c.0b). Informational; the §02A poll surface emits OperatorVerdict events that downstream might audit-chain-verify.
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — 7c.0a's frozen ADR; ADR §2 `SurfaceTransportDeclaration` schema (mandatory_transports + optional_transports).
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py` (post-7c.1) — pattern-precedent for 3-transport parity test shape; the §02A poll surface's 3-transport parity test mirrors this structure but at a different level (HIL surface emit-verdict test, not transport-server smoke test).
- `tests/integration/transports/` (post-7c.1) — 8 refactored transport files registered via `@parity_contract`; the §02A poll surface registers similarly.
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 idioms; the §02A `OperatorVerdict` variant MUST conform.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 + A-test-1.
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.4×.
- `docs/dev-guide/pytest-xdist-classification.md` (post-7c.0c) — R-tier conventions; this story is R2 (smoke + focused + impact-zone).
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-3/4/20/49 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.3b section starting at line 516).
- `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — R-tier + T11-tier + lookahead-tier conventions.

**Predecessor state (verified at dispatch time):**
- 7c.0a + 7c.0b + 7c.0c + 7c.1 + 7c.3a all `done` (or operator-marked-done pending T11 commit; the working-tree state of 7c.3a's deliverables is sufficient for 7c.3b to consume).
- `Directive` + `DirectiveSource` Pydantic models frozen at `app/composers/section_02a/directive_model.py`.
- DSL `@parity_contract` decorator importable from `app.parity.contracts`.
- 8 transport-parity tests refactored onto DSL (post-7c.1); pattern-precedent available.
- pytest-xdist + smoke-suite + R-tier defaults active (post-7c.0c).
- C5 forbidden_modules populated post-7c.3a (composer boundary; informational — 7c.3b's poll surface lives under `app/gates/section_02a/`, NOT under `app/composers/section_02a/`, so C5 doesn't directly bind).
- Class-conformance: 11 contracts; lint-imports: 12 KEPT.

**Live substrate (verified at T1):**
- `app/gates/` package may need `section_02a/` subpackage creation (verify at T1; sibling pattern: any other `app/gates/section_*/` packages from prior slabs).
- `app/models/operator_verdict.py` existence — surface at T1: extend with §02A discriminated-union variant (preferred) OR create sibling `app/models/operator_verdict_section_02a.py` if the discriminated-union pattern doesn't fit cleanly; document choice in Dev Notes.
- `tests/gates/section_02a/` test directory creation.
- `tests/schemas/operator_verdict/` directory existence — verify at T1; create if absent.
- LangChain transport infrastructure for HTTP/MCP-stdio testing — reuse the runtime-subprocess helper from `tests/_helpers/runtime_subprocess.py` if available (used in 7c.1's refactored test files); confirm at T1.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 1 (pattern-author, NOT pattern-consumer). §02A G0 poll-surface canonical HIL pattern: 3-transport verdicts with digest match + field-level edit + re-validation (FR-7c-3 + FR-7c-4 + FR-7c-20 + FR-7c-49 schema-stability case). 7c.6..7c.15 (10 stories) replicate this pattern. Dual-gate justified by substrate-shape (canonical HIL pattern establishes the contract for the entire orchestrational tail).

**T1 conclusion:** No unanticipated architectural disagreement. The canonical HIL pattern is well-bounded (display directive + 3 transport handlers + verdict-digest match + field-level edit + re-validation + DSL registration). **Hard checkpoints at T1:**
- (a) 7c.3a deliverables present in working tree (Directive model + composer body); operator-marked-done is sufficient.
- (b) DSL `@parity_contract` importable.
- (c) `app/models/operator_verdict.py` location confirmed; pick extend-vs-sibling and document.
- (d) Refresh broad-regression baseline.
- (e) Confirm `tests/_helpers/runtime_subprocess.py` (or analogous transport-test helper) is available for 3-transport tests.

---

## Story

As the operator (running Trial-3 against §02A G0 ratification surface),
I want the §02A G0 poll-surface to display the composed directive emitted by 7c.3a's composer, accept {approve, edit, reject} verdicts via CLI + FastAPI + MCP-stdio transports with verdict-digest match enforced on resume, AND support field-level edits that re-validate the edited directive against the Pydantic-v2 model before submission,
so that 7c.3b ships the **canonical HIL surface pattern** that 10 downstream Wave-3 HIL surface stories (7c.6 §04A G1A / 7c.7 §04.5 G1.5 / 7c.8 §04.55 G1.5 / 7c.9 §05.5 G2B / 7c.10 §07B G2M / 7c.11 §07D G2.5 / 7c.12 §07F G2F / 7c.13 §08B G3B / 7c.14 §11 G4A / 7c.15 §11B G4B+§15 G5) replicate by copy-and-adapt — the canonical pattern is the substrate.

---

## Acceptance Criteria

### AC-7c.3b-A — §02A G0 poll-surface module displays Directive + emits OperatorVerdict via 3 transports with verdict-digest match (FR-7c-3 / NFR-7c-S1 / NFR-7c-X2)

**Given** the composed directive emitted by 7c.3a at `state/config/runs/<run-id>/directive.yaml`
**When** the operator submits an `approve` verdict via CLI / FastAPI / MCP-stdio
**Then** the poll surface:

1. Loads the `Directive` Pydantic-v2 model from disk (uses 7c.3a's `Directive.model_validate` + UTF-8-explicit `Path.read_text`).
2. Computes a `decision_card_digest` (SHA256 of canonicalized directive bytes; recommend `hashlib.sha256(yaml.safe_dump(directive.model_dump(mode="json"), sort_keys=True).encode("utf-8")).hexdigest()`; document in Dev Notes if Codex deviates).
3. Renders the directive for operator review — exact rendering format per transport varies (CLI: text + structured table; HTTP: JSON; MCP-stdio: JSON).
4. Accepts {approve, edit, reject} verdict input via the transport handler.
5. Emits `OperatorVerdict<§02A>(verb=Literal["approve", "edit", "reject"], decision_card_digest=<hex>, edit_payload=<DirectiveEditPayload | None>, ...)` Pydantic-v2 model.
6. Returns the verdict as the transport response.
7. **Resume-side enforcement:** `resume_from_verdict()` (existing helper or sibling) rejects via `GateError` if `decision_card_digest` does NOT match the emitted card's digest (NFR-7c-S1 D3 invariant).

**And** the 3-transport parity test asserts byte-identicality (or canonicalized-identicality) of the emitted `OperatorVerdict` payload across CLI / HTTP / MCP-stdio for the same input directive + same operator action.

**Test pin:** `tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py` — 3 parametrized cases (one per transport: CLI, HTTP, MCP-stdio) submitting `approve` verdict against a fixture directive; assert (a) `OperatorVerdict.decision_card_digest` matches across all 3 transports; (b) `resume_from_verdict(verdict)` succeeds when digest matches; (c) `resume_from_verdict(verdict_with_tampered_digest)` raises `GateError`.

> **Notes for 7c.3b-A.** This AC is **dev-agent-executable**. Codex picks the canonicalization rule for `decision_card_digest` at T1 (recommend YAML-serialize with sort_keys + UTF-8 encode + SHA256). Document the choice in Dev Notes; it becomes the canonical convention for all 10 downstream HIL surface stories.

### AC-7c.3b-B — Field-level edit + re-validation flow (FR-7c-4)

**Given** the §02A G0 poll surface
**When** the operator submits an `edit` verdict with a field-level edit payload (e.g., `expected_min_words` adjustment for a `DirectiveSource` OR `role` reclassification from `IGNORED` → `SUPPORTING`)
**Then** the poll surface:

1. Constructs an updated `Directive` by applying the edit_payload to the original directive.
2. Re-validates the updated directive via `Directive.model_validate` — this enforces ALL D4 invariants from 7c.3a (closed-enum role + conditional `expected_min_words` / `excluded_reason` requirements + binary-file invariant).
3. If re-validation FAILS, the poll surface re-prompts the operator with the validation error (do NOT silently drop the edit; do NOT submit invalid).
4. If re-validation PASSES, the poll surface emits an `OperatorVerdict<§02A>(verb="edit", decision_card_digest=<hex of UPDATED directive>, edit_payload=<DirectiveEditPayload>)` and resumes the graph with the validated edited directive.
5. The resume-side enforcement uses the UPDATED digest (not the original); resume rejects if digest mismatches.

**And** the field-level edit-payload schema is a Pydantic-v2 model: `DirectiveEditPayload` with shape per the implementation choice (recommend a `dict[str, dict[str, object]]` mapping `src_id → field-name → new-value`; document in Dev Notes).

**Test pin:** `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` — 4 cases: (a) valid `expected_min_words` edit on primary `.docx` source → re-validation PASSES + edited directive submitted; (b) invalid edit (e.g., `role=IGNORED + expected_min_words=200` violates D4 binary-file invariant from 7c.3a) → re-validation FAILS + re-prompt; (c) valid `role` reclassification → PASSES; (d) edit_payload mutates a non-existent `src_id` → re-validation FAILS with explicit error.

> **Notes for 7c.3b-B.** This AC is **dev-agent-executable**. The re-validation flow is the heart of the HIL pattern's safety: it guarantees the operator cannot submit a structurally-broken directive. Downstream HIL surfaces (7c.6..15) MUST replicate this re-validation flow for their respective domain models.

### AC-7c.3b-C — Parity-contract DSL self-registration (FR-7c-20)

**Given** FR-7c-20 (DSL self-registration) + 7c.0b's `@parity_contract` decorator + 7c.1's pattern-precedent
**When** the §02A poll-surface module is imported
**Then** the module declares its parity contract via `@parity_contract` decorator at module level (sentinel-function pattern from 7c.1):

```python
from app.parity.contracts import parity_contract


@parity_contract(
    surface_id="section_02a_g0_poll",
    mandatory_transports=["cli", "http", "mcp-stdio"],
    optional_transports=["mcp-subprocess"],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for §02A G0 poll surface."""
    return "section_02a_g0_poll"
```

**And** invoking `iter_registered_surfaces()` post-import yields a registration with `surface_id="section_02a_g0_poll"` + `mandatory_transports=["cli", "http", "mcp-stdio"]` + `optional_transports=["mcp-subprocess"]`.

**And** the self-registration audit at `floor=10` (post-7c.1's 9 + this story's 1) PASSES with explicit `discovery_roots=("app.gates.section_02a", ...)`.

**Test pin:** `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py` — (a) AST scan asserts exactly one module-level `@parity_contract` on the poll surface module; (b) import + `iter_registered_surfaces` membership check; (c) audit at floor=10 PASSES.

> **Notes for 7c.3b-C.** This AC is **dev-agent-executable**. The mandatory_transports set `[cli, http, mcp-stdio]` is the canonical 3-transport HIL set per FR-7c-20. The `mcp-subprocess` opt-in is consistent with the existing transport convention (per 7c.1's transport derivations).

### AC-7c.3b-D — Per-HIL-surface OperatorVerdict schema-stability case (FR-7c-49)

**Given** FR-7c-49 per-HIL-surface OperatorVerdict schema-stability test (parametrized harness from 7c.4b — but 7c.4b hasn't closed yet; pattern is forward-compatible)
**When** the dev-agent lands `tests/schemas/operator_verdict/test_section_02a_shape.py`
**Then** the test:

1. Constructs an `OperatorVerdict<§02A>` instance for each transport (CLI / HTTP / MCP-stdio).
2. Asserts JSON-Schema hash is STABLE across the 3 transports for the same payload (canonicalized identical).
3. Asserts the discriminated-union variant is correctly tagged with `surface_id="section_02a_g0_poll"` (consistent with the parity-contract registration).
4. Asserts the §02A `edit_payload` field's nested schema matches the `DirectiveEditPayload` model.

**And** the test serves as the pattern-precedent for the 10 downstream HIL surface stories' parametrized harness consumption (when 7c.4b's harness lands, this story's test re-shapes to consume the parametrized harness; documented as a forward-compatibility note).

**Test pin:** the test IS the AC pin.

> **Notes for 7c.3b-D.** This AC is **dev-agent-executable**. JSON-Schema hashing: recommend `hashlib.sha256(json.dumps(operator_verdict.model_json_schema(), sort_keys=True).encode("utf-8")).hexdigest()`. Document in Dev Notes.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.3a deliverables present (Directive + DirectiveSource models importable).
  - [x] T1.2 Confirm DSL `@parity_contract` importable.
  - [x] T1.3 Determine OperatorVerdict location: extend `app/models/operator_verdict.py` OR create sibling. Document choice.
  - [x] T1.4 Confirm `tests/_helpers/runtime_subprocess.py` (or analogous) available for 3-transport tests.
  - [x] T1.5 Refresh broad-regression baseline.
  - [x] T1.6 Run sandbox-AC validator on this spec; expect PASS.

- [x] **T2 — Author §02A G0 poll-surface module (AC: 7c.3b-A + 7c.3b-C)**
  - [x] T2.1 `app/gates/section_02a/__init__.py` package marker + exports.
  - [x] T2.2 `app/gates/section_02a/poll_surface.py` — `display_directive` + `submit_verdict` callables; canonicalized digest computation.
  - [x] T2.3 `app/gates/section_02a/_transports.py` — CLI + HTTP + MCP-stdio handlers (or delegate to existing transport scaffolding).
  - [x] T2.4 Module-level `@parity_contract` decorator with `surface_id="section_02a_g0_poll"` + 3-transport mandatory.

- [x] **T3 — Author OperatorVerdict §02A variant (AC: 7c.3b-A + 7c.3b-D)**
  - [x] T3.1 Either extend `app/models/operator_verdict.py` with §02A discriminated-union variant OR create `app/models/operator_verdict_section_02a.py` per T1.3.
  - [x] T3.2 `DirectiveEditPayload` Pydantic-v2 model for field-level edits.

- [x] **T4 — Author 4 tests (AC: 7c.3b-A + 7c.3b-B + 7c.3b-C + 7c.3b-D test pins)**
  - [x] T4.1 `tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py` (3 parametrized cases + tamper-detection).
  - [x] T4.2 `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` (4 cases incl. binary-file invariant violation re-validation).
  - [x] T4.3 `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py` (AST + iter_registered + audit at floor=10).
  - [x] T4.4 `tests/schemas/operator_verdict/test_section_02a_shape.py` (JSON-Schema hash stability + discriminated-union variant + edit_payload nested schema).

- [x] **T5 — Verification battery (R-tier R2)**
  - [x] T5.1 Focused tests: 4 new test files PASS.
  - [x] T5.2 R2 smoke pass: `pytest --smoke -p no:randomly -q --tb=short` — 200 nodeids pass (UNCHANGED smoke set; 7c.3b adds tests but they're not in smoke manifest yet — re-curate at next wave-close).
  - [x] T5.3 Class-conformance: 11 contracts (UNCHANGED).
  - [x] T5.4 Lint-imports: 12 KEPT (UNCHANGED; no contract change).
  - [x] T5.5 Sandbox-AC: PASS.
  - [x] T5.6 Ruff: clean.

- [x] **T10 — Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-3b.ready-for-review.md` summarizing: file list (~9 files: 4 NEW app modules + 1 NEW model + 4 NEW tests) + canonical-pattern compliance verdict + 3-transport byte-equivalence wall-clock + audit floor=10 PASS evidence.

- [ ] **T11 — Claude `bmad-code-review` (single-gate; standard tier)**
  - [ ] T11.1 Claude (separate cold context) runs `bmad-code-review` against the diff; produces verdict at `_bmad-output/implementation-artifacts/7c-3b-code-review-2026-05-NN.md`. Verifies (a) canonical pattern is replicable (10 Wave-3 stories will copy); (b) 3-transport byte-equivalence; (c) verdict-digest match enforced on resume; (d) field-level edit re-validation flow correctly catches D4 invariants. Commits + flips done.

---

## Dev Notes

**Why this story exists:** §02A G0 is the FIRST HIL surface; 10 Wave-3 surfaces (7c.6..15) replicate this pattern. The canonical pattern includes: directive display + 3-transport verdict emission + verdict-digest match + field-level edit + re-validation + DSL self-registration. Each downstream HIL surface adapts these to its specific domain model (e.g., 7c.6 §04A G1A operates on `PlanUnit` instead of `Directive`).

**Pattern-replicability check at T11:** the verdict artifact MUST confirm the pattern is copy-and-adapt-friendly. Specifically: each domain-specific helper (digest computation; edit_payload structure; re-validation flow) MUST be parameterizable, NOT §02A-specific. If the pattern bakes in §02A-specific assumptions, downstream replications duplicate code; T11 surfaces this as a refactor-candidate.

**Canonicalization conventions (lock at T1; document in Dev Notes):**
- `decision_card_digest` = `SHA256(yaml.safe_dump(directive.model_dump(mode="json"), sort_keys=True).encode("utf-8"))`. Variation: JSON-serialize instead of YAML if YAML is too lossy. Codex picks; document.
- `OperatorVerdict.surface_id` = `"section_02a_g0_poll"` (matches parity-contract registration).
- `edit_payload` Pydantic shape = `dict[str, dict[str, object]]` mapping `src_id → field-name → new-value`. Variation: typed `DirectiveEditPayload` with explicit fields. Codex picks; document.

**Codex T1 decisions (2026-05-05):**
- OperatorVerdict location: created sibling `app/models/operator_verdict_section_02a.py`. Rationale: the live canonical global model is `app/models/state/operator_verdict.py`, not `app/models/operator_verdict.py`; extending the global state verdict would require unrelated schema/golden lockstep churn outside 7c.3b's bounded surface.
- Digest canonicalization: selected SHA256 over canonical JSON bytes (`model_dump(mode="json")`, sorted keys, compact separators, UTF-8). Rationale: JSON canonicalization is transport-neutral, avoids YAML emitter variance, and is parameterized over `BaseModel` for downstream HIL surfaces.
- Edit payload schema: selected `DirectiveEditPayload(edits: dict[str, dict[str, Any]])`. Rationale: explicit Pydantic-v2 model keeps nested schema visible for FR-7c-49 while retaining the copy-and-adapt source-id-to-field-update pattern.

**File / module placement:**
- `app/gates/section_02a/` (NEW; sibling of any other `app/gates/section_*/` packages from prior slabs).
- `app/models/operator_verdict.py` extension OR `app/models/operator_verdict_section_02a.py` sibling — T1.3 decision.
- `tests/gates/section_02a/` test directory (NEW).
- `tests/schemas/operator_verdict/` directory — verify at T1; create if absent.

**Anti-patterns to avoid:**
- **A11 Windows-portability** — UTF-8 explicit on directive read (consume 7c.3a + 7c.2 conventions); `pathlib.Path.as_posix()`.
- **A-test-1 Mocking the SUT** — 3-transport parity test uses real transport handlers + real OperatorVerdict; do NOT mock the discriminated-union variant.
- **§02A-specific pattern bake-in** — domain-specific helpers MUST be parameterizable. T11 verifies replicability.
- **Per-test-function `@parity_contract`** — module-level only (consume 7c.1's pattern-precedent).

**K-discipline:**
- K-target 1.4× ≈ ~3.5K LOC ceiling. Estimate: 3 app modules ~300-500 LOC + 1 model file ~100-200 LOC + 4 test files ~100-200 LOC each = ~800-1500 LOC. Comfortable.

### Project Structure Notes

- **Alignment with unified project structure:** all new file paths conform to existing convention. `app/gates/section_02a/` is a NEW subpackage; verify at T1 whether `app/gates/__init__.py` exists.
- **Detected variances:** OperatorVerdict location decision at T1.3.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-3b]
- [Source: app/composers/section_02a/directive_model.py] (7c.3a frozen Directive + DirectiveSource models)
- [Source: app/parity/contracts/__init__.py] (DSL primitives post-7c.0b/7c.1)
- [Source: app/audit/__init__.py] (audit-chain helpers post-7c.0b)
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (ADR §1 + §2 informational)
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md] (14 idioms; OperatorVerdict §02A variant conforms)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 + A-test-1)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline 1.4×)
- [Source: docs/dev-guide/pytest-xdist-classification.md] (R-tier R2 smoke convention post-7c.0c)
- [Source: tests/integration/transport_parity/test_fastapi_mcp_parity.py] (post-7c.1 pattern-precedent for transport parity)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (FR-7c-3 + FR-7c-4 + FR-7c-20 + FR-7c-49 + NFR-7c-P4 + NFR-7c-S1 + NFR-7c-X2)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.3b] (Story 7c.3b section starting at line 516)
- [Source: _bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md] (R-tier + T11-tier conventions)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

- T1 import checks: Directive + DirectiveSource importable; `@parity_contract` importable; `tests/_helpers/runtime_subprocess.py` exists.
- T1 broad baseline refresh: `39 failed, 4077 passed, 27 skipped, 2 xfailed, 11 warnings` (same known 39-failure checkout baseline class as 7c.3a).
- Focused tests: `.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` -> `15 passed`.
- Impact-zone: same known inherited failures in `tests/parity/test_nfr_cg_block_aggregated.py::...NFR-CG6` and `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py::test_tw_7c_4_detector_exists_and_passes`; no 7c.3b-specific failures.
- Smoke: `.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short` -> `181 passed, 18 skipped`.
- Class conformance: `PASS: 11 activation contract file(s) conform`.
- Lint-imports: `12 kept, 0 broken`.
- Sandbox-AC: `PASS`.
- Ruff: clean on touched app/test files.
- Self-registration audit floor=10: PASS with explicit roots `app.gates.section_02a`, `tests.integration.transport_parity`, `tests.integration.transports` -> `surface_cardinality=10`.
- Audit CLI note: `.venv/Scripts/python.exe -m app.parity.contracts._audit --declared-floor 10` still FAILS with default app-only roots (`surface_cardinality=2`); this is a discovery-root mismatch in the inherited audit CLI, not a missing 7c.3b registration. T11 should adjudicate whether to patch `_audit` in a later DSL-owned story.

### Completion Notes List

- Implemented the Section 02A G0 poll surface with `display_directive`, canonical digest computation, `submit_verdict`, edit application/re-validation, and `resume_from_verdict` digest enforcement.
- Added in-process CLI/HTTP/MCP-stdio handlers that emit canonicalized-identical `Section02AOperatorVerdict` payloads for the same directive and operator action.
- Added `Section02AOperatorVerdict` and `DirectiveEditPayload` Pydantic-v2 models with `extra="forbid"`, `validate_assignment=True`, frozen value-object semantics, UUID4/tz-aware/sha256 validators, closed surface id, and verb-payload consistency.
- Field-level edit coverage includes valid expected-word edit, valid role reclassification, unknown `src_id` rejection, and the 7c.3a binary-file invariant rejection path.
- Pattern-replicability: `canonical_model_bytes(model: BaseModel)` and `compute_model_digest(model: BaseModel)` are domain-agnostic; transport handlers delegate through one neutral `submit_verdict` path; Section 02A-specific edit application is isolated for downstream copy-and-adapt.

### File List

- `app/gates/section_02a/__init__.py`
- `app/gates/section_02a/_transports.py`
- `app/gates/section_02a/poll_surface.py`
- `app/models/operator_verdict_section_02a.py`
- `tests/gates/__init__.py`
- `tests/gates/section_02a/__init__.py`
- `tests/gates/section_02a/_helpers.py`
- `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py`
- `tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py`
- `tests/schemas/operator_verdict/__init__.py`
- `tests/schemas/operator_verdict/test_section_02a_shape.py`

### Change Log

- 2026-05-05: Codex implemented Story 7c.3b through T10 and moved status to review.
