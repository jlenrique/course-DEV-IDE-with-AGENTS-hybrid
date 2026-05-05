# Migration Story 7c.4b: Gate-Family Foundation Implementation — Shared Base + Class-Conformance + FR-7c-49 Harness + C6 Population + TW-7c-3 Single-Source

**Status:** ready-for-dev *(spec authored 2026-05-05 with cross-agent contract negotiation per AMEND-V5 pre-flight; predecessors 7c-0b + 7c-4a CLOSED `done`. **DISPATCHABLE NOW** — operator can pick this up immediately to keep Codex unblocked.)*
**Sprint key:** `migration-7c-4b-gate-family-foundation-implementation`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 3
**Gate:** **dual-gate** + **cross-agent code-review MANDATORY** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-velocity-amendments-bundle, story 7c-4b; rationale: `ci_or_compile_shape + substrate_shape`; cross-agent justified per John A5 + Murat M6 — substrate is inherited by 8 per-gate stories)
**K-target:** ~1.4× (substrate-shape; ~3-4 pts; bounded surface = shared base classes + class-conformance validator extension + parametrized OperatorVerdict harness + C6 target population + TW-7c-3 firing-spec single-source + manifest compiler extension)
**R-tier (regression scope):** **R3** — full broad regression. Substrate-shape inherited by 8 per-gate stories + parametrized harness + manifest compiler change all warrant full coverage.
**T11-tier (review approach):** **cross-agent** — MANDATORY full-fresh-context Blind/Edge/Auditor per governance JSON `cross_agent_review_required: true`. NEVER batched.
**Files touched (declared at spec-author time):**
- `app/models/decision_cards/_base.py` (NEW or extend if exists; shared `DecisionCardBase` Pydantic-v2 base class with cache_state + affected_nodes + override_trail + decision_card_digest invariants)
- `app/parity/contracts/tw_7c_3_firing.py` (NEW; AMEND-7d-i single-source for TW-7c-3 firing-spec; `LOCKSTEP_CHECK` callable + four-file glob constants)
- `app/parity/contracts/_aliases.py` (NEW; OR extend existing `_declaration.py` per D1 below; ratifies the alias_of forward-syntax from 7c.4a ADR 0002)
- `tests/schemas/operator_verdict/_harness.py` (NEW; parametrized harness fixture per FR-7c-49; consumed by 7c.6..15 + 7c.3b's existing `test_section_02a_shape.py` reshapes to consume parametrization)
- `scripts/utilities/validate_parity_test_class_conformance.py` (MODIFY; extend to recognize new gate IDs per FR-7c-8 + register TW-7c-3 firing condition)
- `app/manifest/compiler.py` (MODIFY; extend per FR-7c-9 to honor new gate codes; orchestration_only_nodes tolerance for new orchestration-only nodes)
- `pyproject.toml` (MODIFY; populate C6 `forbidden_modules` per FR-7c-53 — 12-source-modules cross-import prevention)
- `tests/parity/test_decision_card_base_shape.py` (NEW; shape-pin for shared base class invariants)
- `tests/parity/test_class_conformance_validator_extension.py` (NEW; verifies validator recognizes new gate IDs + TW-7c-3 firing detection)
- `tests/structural/test_import_linter_c6_target_list_populated.py` (NEW; structural test verifies C6 populated post-7c.4b)
- `tests/structural/test_tw_7c_3_firing_spec_single_source.py` (NEW; AMEND-7d-i structural pin — 7c.5.G* stories MUST cite by reference)
- `tests/parametrized_harness/test_operator_verdict_harness_consumable.py` (NEW; verifies harness shape with synthetic registered surfaces)
- `tests/integration/manifest/test_compiler_honors_new_gate_codes.py` (NEW; FR-7c-9 enforcement)
**Lookahead tier:** **3 → AUTHORED** — was Tier 3 (held until 7c.4a closed); promoted to AUTHORED post-7c.4a-close. Cross-agent T11 review collapses to verification per AMEND-V5 cross-agent pre-flight rule.
**Authored:** 2026-05-05 via `bmad-create-story` workflow + AMEND-V5 cross-agent pre-flight contract negotiation.
**Wave:** 2 — slot 2 (substrate-foundation; precedes 7c.5.G0..G6 8 per-gate stories).

**FR coverage:**
- **FR-7c-8** Class-conformance validator recognizes every new gate ID; reports ≥11 conforming activation contracts post-Slab-7c (no regression).
- **FR-7c-9** Manifest fold-flags + compiler honor every new gate code at runtime per FR-A8 (Slab 7a 7a.2 substrate); orchestration_only_nodes lockstep tolerance covers any new orchestration-only nodes.
- **FR-7c-49** parametrized OperatorVerdict schema-stability harness — primary enforcement here. 7c.6..15 (10 HIL surfaces) consume the parametrization; 7c.3b's `test_section_02a_shape.py` already pre-warmed the per-surface case shape.
- **FR-7c-53 C6** HIL boundaries import-linter contract — populate C6 `forbidden_modules` to prevent cross-surface imports.

**NFR coverage:** NFR-7c-M1 (four-file-lockstep precondition; via TW-7c-3 firing-spec single-source); NFR-7c-R5 (class-conformance ≥11; UNCHANGED); NFR-7c-OD2 (TripwireLedgerEntry consumption from 7c.0a); NFR-7c-OD7 (self-registration audit harness consumption from 7c.0b); NFR-7c-X4 (no regression); NFR-7c-M5 (sandbox-AC validator PASS).

**Standing-guardrail enforcement:**
- SG-1 unchanged.
- SG-2 PRODUCTION_GATE_IDS expansion row preserved (7c.4a's 18-ID list canonical; 7c.4b's compiler extension honors them at runtime).
- SG-3 Composition Spec §3.5 gate-family invariants honored on shared base.
- SG-4 unchanged.

**Tripwire ownership:** **TW-7c-3** detection registration ownership (firing-spec single-source per AMEND-7d-i at `app/parity/contracts/tw_7c_3_firing.py`; 7c.5.G0..G6 cite by reference; firing condition: any new gate added without four-file-lockstep co-commit + class-conformance assertion).

**Implementation cycle (NEW CYCLE):**
- **Claude (Opus 4.7):** authored this spec with locked contract decisions per AMEND-V5 pre-flight 2026-05-05; sandbox-AC validator PASS; pre-authored `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-4b-gate-family-foundation-implementation.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops shared base + class-conformance extension + parametrized harness + alias_of executable syntax + C6 population + TW-7c-3 firing-spec single-source + manifest compiler extension + 6 tests per the locked contract decisions; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-4b.ready-for-review.md`.
- **Claude T11 cross-agent review:** verifies Codex's implementation matches the locked contract; D1-D? compliance table verified line-by-line.

---

## Contract Negotiation Decisions (LOCKED 2026-05-05 per AMEND-V5 pre-flight)

The following decisions are LOCKED at spec-author time. T11 cross-agent review verifies; does NOT relitigate.

**D1. alias_of executable syntax: extend `SurfaceTransportDeclaration` in `app/parity/contracts/_declaration.py`** (NOT a new `AliasGateDeclaration` class). Rationale per 7c.4a ADR 0002 §3 + Codex T10 self-review on 7c.4a: minimum-churn path; preserves the registry semantics; one declaration model with optional `alias_of` field.

```python
# Extend SurfaceTransportDeclaration in app/parity/contracts/_declaration.py:
class SurfaceTransportDeclaration(BaseModel):
    surface_id: str
    mandatory_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]
    optional_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]
    alias_of: str | None = None  # NEW — names parent family from 7c.4a's 8-family taxonomy
```

The decorator `parity_contract` accepts an `alias_of` keyword arg; passes through to the declaration. Registry stores the relationship; `iter_registered_surfaces()` exposes it; audit reports both surface_id and alias_of.

**D2. Shared `DecisionCardBase` location: `app/models/decision_cards/_base.py`** (NEW; underscore-prefix denotes internal-only inheritance interface; per Slab 7a precedent for analogous shared bases). Pydantic-v2 base class with the 4 frozen invariants:

```python
class DecisionCardMeta(BaseModel):
    cache_state: Literal["healthy", "mixed", "cold"]
    affected_nodes: list[str]
    override_trail: list[OverrideEvent]


class DecisionCardBase(BaseModel):
    """Shared base class for all 8 net-new gate-family DecisionCards."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    decision_card_digest: str  # sha256 hex; mirrors 7c.3b digest convention
    meta: DecisionCardMeta

    @field_validator("decision_card_digest")
    @classmethod
    def _require_sha256_hex(cls, value: str) -> str: ...
```

**D3. Parametrized OperatorVerdict harness signature** at `tests/schemas/operator_verdict/_harness.py`:

```python
def assert_operator_verdict_schema_stable_across_transports(
    *,
    verdict_class: type[BaseModel],  # any §-specific OperatorVerdict variant
    surface_id: str,
    transports: Sequence[Literal["cli", "http", "mcp-stdio"]] = ("cli", "http", "mcp-stdio"),
) -> None:
    """Assert JSON-Schema hash stable across the 3 transports for a given verdict class."""
```

This is the canonical harness that 7c.6..15 (10 stories) consume via parametrize. 7c.3b's existing `test_section_02a_shape.py` may either keep its current standalone shape OR reshape to consume the harness — surface as `decision_needed` at T1; recommend reshape for consistency.

**D4. TW-7c-3 firing-spec single-source location:** `app/parity/contracts/tw_7c_3_firing.py` (NEW). Per AMEND-7d-i. Module exports:

```python
LOCKSTEP_CHECK: Callable[[str], LockstepResult]  # the single source of truth

FOUR_FILE_GLOBS = {
    "model": "app/models/decision_cards/{gate_id_lower}.py",
    "schema": "app/models/decision_cards/schema/{gate_id_lower}.v1.schema.json",
    "shape_pin": "tests/parity/test_decision_card_{gate_id_lower}_shape.py",
    "golden_fixture": "tests/fixtures/decision_cards/{gate_id_lower}_golden.json",
}


class LockstepResult(BaseModel):
    gate_id: str
    files_present: dict[str, bool]
    all_four_present: bool
    failure_reason: str | None


def LOCKSTEP_CHECK(gate_id: str) -> LockstepResult: ...
```

7c.5.G0..G6 stories cite by reference: `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK`. NEVER re-derive in per-gate stories.

**D5. C6 forbidden_modules canonical list (12 source-modules; cross-import prevention):**

```toml
forbidden_modules = [
    "app.gates.section_02a",  # 7c.3b just added; can't be cross-imported by other §sections
    "app.gates.section_04a",
    "app.gates.section_04_5",
    "app.gates.section_04_55",
    "app.gates.section_05_5",
    "app.gates.section_07b",
    "app.gates.section_07d",
    "app.gates.section_07f",
    "app.gates.section_08b",
    "app.gates.section_11",
    "app.gates.section_11b",
    "app.gates.section_15",
]
```

Wait — C6 source_modules are ALREADY the 12 §sections (per 7c.0a's `pyproject.toml` C6 contract); this story populates the FORBIDDEN_MODULES with the SAME 12 §sections, since the contract is "any §section module cannot import any OTHER §section module". The lint-imports rule treats each source_module independently against the forbidden list (a §section can't import another §section). KEPT count stays 12 (no new contract).

**D6. Class-conformance validator extension** at `scripts/utilities/validate_parity_test_class_conformance.py`:
- Accept gate IDs from 7c.4a's 18-ID enumerated runtime list as valid surface_ids.
- Cross-check four-file-lockstep via `LOCKSTEP_CHECK(gate_id)` (D4).
- Report ≥11 conforming activation contracts post-Slab-7c (UNCHANGED; this story doesn't ADD activation contracts; just gate-family base class which is a shape-pin not an activation contract).
- TW-7c-3 fires (CRITICAL severity; written via TripwireLedgerEntry from 7c.0a) if a gate is added without 4-file-lockstep.

**D7. Manifest compiler extension** at `app/manifest/compiler.py`:
- Honor every new gate code at runtime per FR-A8 (Slab 7a 7a.2 substrate already added 14 gate codes; 7c.4b extends to 18 per 7c.4a's runtime list).
- `orchestration_only_nodes` lockstep tolerance covers any new orchestration-only nodes (7c.4a's `G2` + `G1.5` covered-labels).

**D8. Test fixture for shared base class shape-pin:** `tests/parity/test_decision_card_base_shape.py` — covers 4 invariants (cache_state closed-enum + affected_nodes list-of-str + override_trail list-of-OverrideEvent + decision_card_digest sha256-hex regex). Mirrors 7c.0a's TripwireLedgerEntry shape-pin pattern.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (7c.4a's frozen ADR; 8 family + 10 alias + 18 runtime IDs + alias_of forward-syntax).
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` (7c.0a's frozen ADR; SurfaceTransportDeclaration shape).
- `app/parity/contracts/_declaration.py` — SurfaceTransportDeclaration current shape (post-7c.0b; 7c.4b extends with `alias_of`).
- `app/parity/contracts/_decorator.py` — `parity_contract` decorator factory (post-7c.0b; 7c.4b extends to accept `alias_of` kwarg).
- `app/parity/contracts/_registry.py` — registry semantics (post-7c.0b).
- `app/audit/__init__.py` — audit-chain helpers (post-7c.0b; informational).
- `app/models/tripwire_ledger.py` — TripwireLedgerEntry pattern reference for shape-pin discipline.
- `app/models/decision_cards/` — existing per-gate models (G1, G2C, G3, G4 from Slab 7a substrate; verify at T1; the 7c.4b shared base class is parent to all 8 post-Slab-7c families).
- `app/manifest/compiler.py` — Slab 7a substrate (post-7a.2 manifest fold-flags; 7c.4b extends).
- `scripts/utilities/validate_parity_test_class_conformance.py` — 7c.0a/0b foundation; 7c.4b extends.
- `tests/schemas/operator_verdict/test_section_02a_shape.py` (post-7c.3b) — pattern-precedent for §02A schema-stability case.
- `tests/parity/test_tripwire_ledger_entry_shape.py` (post-7c.0a) — shape-pin pattern reference for `_base.py` test.
- `docs/dev-guide/migration-story-governance.json::r_tier_legend + t11_tier_legend + lookahead_tier_legend` — convention reference.
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 idioms; DecisionCardBase + LockstepResult + AliasGateDeclaration MUST conform.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 + A-test-1.
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.4×.
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-8/9/49/53 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.4b section starting at line 572).

**Predecessor state (verified at dispatch time):**
- 7c.0a + 7c.0b + 7c.0c + 7c.1 + 7c.2 + 7c.3a + 7c.4a all `done`.
- 7c.3b `done` recommended (operationally serial via Codex single-thread; review state acceptable).
- ADR 0001 + ADR 0002 frozen.
- DSL primitives importable; `@parity_contract` accepts `surface_id`, `mandatory_transports`, `optional_transports` keyword args (alias_of NOT yet accepted; this story adds it).
- `app/models/decision_cards/{base.py?, g1.py, g2c.py, g3.py, g4.py, override_event.py, vocabulary.py}` exist from Slab 7a substrate; verify at T1 whether `_base.py` already exists (if so, 7c.4b extends; if not, 7c.4b creates).
- Class-conformance: 11 contracts; lint-imports: 12 KEPT.

**Live substrate (verified at T1):**
- `app/parity/contracts/_declaration.py` extension to add `alias_of` field (post-D1).
- `app/parity/contracts/_decorator.py` extension to accept `alias_of` kwarg.
- `app/manifest/compiler.py` location; verify existence + read 7a.2 substrate before extending.
- `scripts/utilities/validate_parity_test_class_conformance.py` location; verify existence + extension surface.
- `tests/schemas/operator_verdict/_harness.py` location.
- pyproject.toml C6 contract source_modules + currently empty forbidden_modules.

**Gate-mode rationale (from governance JSON):** Slab 7c Wave 2 (gate-family foundation; cross-agent MANDATORY per John A5 + Murat M6). Shared base classes + class-conformance validator extension + manifest compiler extension + parametrized OperatorVerdict harness + C6 target population + TW-7c-3 firing-spec single-source. Substrate inherited by 8 per-gate stories. K-target 1.4x.

**T1 conclusion:** Locked-contract decisions D1-D8 cover the full implementation surface; T11 review collapses to verification per AMEND-V5. **Hard checkpoints at T1:**
- (a) 7c.4a `done` (frozen taxonomy in ADR 0002).
- (b) 7c.0b `done` (DSL primitives importable; decorator factory).
- (c) `app/models/decision_cards/_base.py` existence — extend vs create. Document.
- (d) `app/manifest/compiler.py` — verify Slab 7a substrate landed cleanly.
- (e) C6 contract source_modules currently set to 12 §sections; verify forbidden_modules currently empty.
- (f) Refresh broad-regression baseline (post-7c.3b).

---

## Story

As the dev-agent (and 8 downstream per-gate stories' substrate consumer),
I want the gate-family shared base class + class-conformance validator extension + parametrized OperatorVerdict schema-stability harness + alias_of executable syntax in `parity_contract` decorator + C6 HIL boundaries import-linter contract + TW-7c-3 lockstep checker registration + manifest compiler extension to honor 7c.4a's 18 runtime IDs,
so that 7c.5.G0..G6 (8 per-gate stories) inherit a working executable substrate enforcing four-file-lockstep + class-conformance + per-surface OperatorVerdict schema-stability at slab-open, AND 10 alias gates from 7c.4a's taxonomy can self-register via `@parity_contract(alias_of="G1")` syntax that Codex implements here.

---

## Acceptance Criteria

### AC-7c.4b-A — Shared `DecisionCardBase` Pydantic-v2 base class lands at `app/models/decision_cards/_base.py` (D2)

**Given** locked D2 + 7c.4a's 8 family contracts taxonomy
**When** the dev-agent lands `app/models/decision_cards/_base.py`
**Then** the module exposes `DecisionCardBase` Pydantic-v2 with `validate_assignment=True`, `extra="forbid"`, `frozen=True`, the 4 invariants per D2 (`decision_card_digest` sha256-hex regex; `meta` of `DecisionCardMeta` shape with cache_state closed-enum + affected_nodes list-of-str + override_trail list-of-OverrideEvent).

**And** `DecisionCardMeta` is a Pydantic-v2 sub-model with `cache_state: Literal["healthy", "mixed", "cold"]` closed-enum (triple-layer red-rejection mirroring TripwireLedgerEntry pattern from 7c.0a).

**Test pin:** `tests/parity/test_decision_card_base_shape.py` — 7+ assertions covering 4 fields + closed-enum red-rejection on cache_state + sha256-hex regex on decision_card_digest + frozen-after-construction.

### AC-7c.4b-B — `alias_of` executable syntax in `parity_contract` decorator (D1; consumes 7c.4a ADR 0002 §3)

**Given** locked D1 + 7c.4a's ADR 0002 forward-syntax ratification
**When** the dev-agent extends `app/parity/contracts/_declaration.py::SurfaceTransportDeclaration` with `alias_of: str | None = None` field + extends `app/parity/contracts/_decorator.py::parity_contract` to accept `alias_of` kwarg
**Then**:

1. `SurfaceTransportDeclaration(surface_id="G0A", mandatory_transports=["cli"], alias_of="G1")` validates cleanly.
2. `@parity_contract(surface_id="G0A", mandatory_transports=["cli"], alias_of="G1")` registers the alias relationship in the registry.
3. `iter_registered_surfaces()` exposes both `surface_id` AND `alias_of` for each declaration.
4. `alias_of` value MUST be one of 7c.4a's 8 family contract IDs (`G0`, `G1`, `G2A`, `G2C`, `G3`, `G4`, `G5`, `G6`); validator rejects any other string.

**And** `alias_of=None` (default) is unchanged behavior — non-alias surface_ids continue to register as before.

**Test pin:** `tests/parity/test_dsl_primitive_contract.py` (extend; +3 cases for alias_of valid/invalid family/None default).

### AC-7c.4b-C — Parametrized OperatorVerdict harness lands at `tests/schemas/operator_verdict/_harness.py` (D3 / FR-7c-49)

**Given** locked D3 + 7c.3b's `test_section_02a_shape.py` pattern-precedent
**When** the dev-agent lands `tests/schemas/operator_verdict/_harness.py`
**Then** the module exposes `assert_operator_verdict_schema_stable_across_transports(*, verdict_class, surface_id, transports=("cli","http","mcp-stdio"))` per D3 signature.

**And** the harness:
1. Computes JSON-Schema for `verdict_class.model_json_schema()`.
2. Asserts the schema hash is STABLE (single canonical schema; transport-independent because Pydantic schemas don't depend on transport).
3. Asserts the discriminated-union `surface_id` field matches the passed-in surface_id.
4. Asserts the verdict-class shape conforms to a base discriminator pattern (verb + decision_card_digest + run_id + operator_id + submitted_at + optional edit/reject payloads).

**Test pin:** `tests/parametrized_harness/test_operator_verdict_harness_consumable.py` — invokes the harness against synthetic verdict classes (a small Pydantic v2 model mimicking `Section02AOperatorVerdict` shape from 7c.3b); asserts harness raises on shape deviations + passes on conforming.

> **Note for 7c.4b-C:** 7c.3b's existing `tests/schemas/operator_verdict/test_section_02a_shape.py` MAY reshape to consume the harness OR remain standalone — surface as `decision_needed` at T1; if reshape is chosen, 7c.4b's diff includes the reshape (overlay-only; no semantic change to 7c.3b's existing assertions).

### AC-7c.4b-D — Class-conformance validator extension recognizes 7c.4a's 18 runtime IDs + TW-7c-3 firing registration (D6 / FR-7c-8 / AMEND-7d-i)

**Given** locked D4 (TW-7c-3 firing-spec single-source at `app/parity/contracts/tw_7c_3_firing.py`) + locked D6 (validator extension)
**When** the dev-agent:

1. Lands `app/parity/contracts/tw_7c_3_firing.py` with `LOCKSTEP_CHECK` callable + `FOUR_FILE_GLOBS` constant + `LockstepResult` Pydantic-v2 model per D4.
2. Extends `scripts/utilities/validate_parity_test_class_conformance.py` to:
   - Recognize all 18 runtime IDs from 7c.4a's enumeration as valid surface_ids.
   - Cross-check four-file-lockstep via `LOCKSTEP_CHECK(gate_id)`.
   - For each gate that fails lockstep, fire TW-7c-3 (CRITICAL severity) by writing a TripwireLedgerEntry to `sprint-status.yaml::tripwire_events` (consuming 7c.0a's TripwireLedgerEntry schema).
3. Reports ≥11 conforming activation contracts post-extension (UNCHANGED; the shared base class is a shape-pin not an activation contract).

**Test pin:** `tests/parity/test_class_conformance_validator_extension.py` — covers (a) validator recognizes all 18 runtime IDs; (b) `LOCKSTEP_CHECK("G0")` returns LockstepResult with all_four_present=False (since G0's 4 files don't exist yet — 7c.5.G0 lands them); (c) TW-7c-3 firing path is exercised on synthetic missing-file scenario (without actually writing to sprint-status; use a tmp_path for the ledger).

**Test pin:** `tests/structural/test_tw_7c_3_firing_spec_single_source.py` — AST scan asserts (a) `app/parity/contracts/tw_7c_3_firing.py` exists with LOCKSTEP_CHECK + FOUR_FILE_GLOBS + LockstepResult exports; (b) NO other module under `tests/parity/test_decision_card_*_shape.py` re-derives the firing condition (would re-introduce drift). 7c.5.G* stories cite by reference `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK`.

### AC-7c.4b-E — Manifest compiler extension honors 7c.4a's 18 runtime IDs (FR-7c-9)

**Given** Slab 7a 7a.2 substrate (manifest fold-flags + compiler extension landed)
**When** the dev-agent extends `app/manifest/compiler.py`
**Then** the compiler honors every new gate code from 7c.4a's 18-ID enumeration at runtime + orchestration_only_nodes lockstep tolerance covers `G2` and `G1.5` covered-label runtime IDs (per 7c.4a §4 documentation).

**Test pin:** `tests/integration/manifest/test_compiler_honors_new_gate_codes.py` — for each of the 18 runtime IDs, assert compiler accepts the gate code without error + manifest compilation produces a node entry.

### AC-7c.4b-F — C6 import-linter contract populated; cross-§section import prevented (FR-7c-53 / D5)

**Given** locked D5 + 7c.0a's C6 contract definition (12 source_modules; empty forbidden_modules)
**When** the dev-agent populates `pyproject.toml::[tool.importlinter]` C6 forbidden_modules with the 12 §sections (per D5 list)
**Then**:

1. Each of the 12 §section modules is FORBIDDEN from importing any of the 11 OTHER §section modules.
2. `lint-imports` exits 0 with 12 KEPT (UNCHANGED; just target-list population).
3. Shared helpers MUST live in `app.gates._shared.*` (NEW package marker if doesn't exist; verify at T1 + create if absent).

**Test pin:** `tests/structural/test_import_linter_c6_target_list_populated.py` — `tomllib` parse + assert C6 forbidden_modules matches expected 12-entry set; subprocess `lint-imports` + assert KEPT count = 12.

> **Note for 7c.4b-F:** 7c.3b's `app/gates/section_02a/` package was the FIRST §section module shipped post-7c.4b. C6 prevents future §sections (7c.6..15 + others) from cross-importing it. Codex MUST verify at T1 that 7c.3b's `section_02a` doesn't accidentally import any of the OTHER 11 §section paths (it shouldn't; `app.gates.section_02a` only depends on `app.gates.errors` + 7c.0a/0b/3a substrate).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.4a + 7c.0b `done` + 7c.3b `review`-or-`done`.
  - [ ] T1.2 Verify ADR 0002 + ADR 0001 importable + present.
  - [ ] T1.3 Verify `app/models/decision_cards/_base.py` existence; document extend-vs-create.
  - [ ] T1.4 Verify `app/manifest/compiler.py` Slab 7a substrate.
  - [ ] T1.5 Verify pyproject.toml C6 contract present (12 source_modules; empty forbidden_modules).
  - [ ] T1.6 Verify 7c.3b's `section_02a` doesn't cross-import other §sections (post-D5).
  - [ ] T1.7 Refresh broad-regression baseline.
  - [ ] T1.8 Run sandbox-AC validator on this spec; expect PASS.

- [ ] **T2 — Land shared `DecisionCardBase` (AC: 7c.4b-A; D2)**
  - [ ] T2.1 `app/models/decision_cards/_base.py` Pydantic-v2 base class + DecisionCardMeta sub-model.
  - [ ] T2.2 Triple-layer red-rejection on `cache_state` (mirror TripwireLedgerEntry pattern).
  - [ ] T2.3 Update `app/models/decision_cards/__init__.py` exports.

- [ ] **T3 — Extend `parity_contract` with `alias_of` syntax (AC: 7c.4b-B; D1)**
  - [ ] T3.1 Extend `SurfaceTransportDeclaration` in `_declaration.py` with `alias_of: str | None = None` + validator rejecting non-family-IDs.
  - [ ] T3.2 Extend `parity_contract` decorator in `_decorator.py` to accept `alias_of` kwarg.
  - [ ] T3.3 Verify `iter_registered_surfaces()` exposes alias_of.

- [ ] **T4 — Land parametrized OperatorVerdict harness (AC: 7c.4b-C; D3 / FR-7c-49)**
  - [ ] T4.1 `tests/schemas/operator_verdict/_harness.py` with `assert_operator_verdict_schema_stable_across_transports`.
  - [ ] T4.2 Surface-as-decision-needed: reshape 7c.3b's `test_section_02a_shape.py` to consume harness, OR keep standalone.

- [ ] **T5 — Land TW-7c-3 firing-spec single-source (AC: 7c.4b-D; D4 / AMEND-7d-i)**
  - [ ] T5.1 `app/parity/contracts/tw_7c_3_firing.py` with LOCKSTEP_CHECK + FOUR_FILE_GLOBS + LockstepResult.

- [ ] **T6 — Extend class-conformance validator (AC: 7c.4b-D; D6 / FR-7c-8)**
  - [ ] T6.1 `scripts/utilities/validate_parity_test_class_conformance.py` extension to recognize 18 runtime IDs + LOCKSTEP_CHECK integration + TW-7c-3 firing.

- [ ] **T7 — Extend manifest compiler (AC: 7c.4b-E; D7 / FR-7c-9)**
  - [ ] T7.1 `app/manifest/compiler.py` extension to honor 18 runtime IDs.

- [ ] **T8 — Populate C6 forbidden_modules (AC: 7c.4b-F; D5 / FR-7c-53)**
  - [ ] T8.1 Edit `pyproject.toml::[tool.importlinter]` C6 forbidden_modules per D5.
  - [ ] T8.2 Verify lint-imports KEPT 12 (UNCHANGED).

- [ ] **T9 — Author 6 tests (AC test pins)**
  - [ ] T9.1 `tests/parity/test_decision_card_base_shape.py`.
  - [ ] T9.2 `tests/parity/test_class_conformance_validator_extension.py`.
  - [ ] T9.3 `tests/structural/test_import_linter_c6_target_list_populated.py`.
  - [ ] T9.4 `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
  - [ ] T9.5 `tests/parametrized_harness/test_operator_verdict_harness_consumable.py`.
  - [ ] T9.6 `tests/integration/manifest/test_compiler_honors_new_gate_codes.py`.

- [ ] **T10 — Codex T10 self-review at `_codex-handoff/7c-4b.ready-for-review.md`**
  - [ ] T10.1 Document: file list (~14 files; 7+ new + 5 modified), D1-D8 contract compliance table, broad-regression delta, lint-imports KEPT 12, class-conformance ≥11, ruff status.

- [ ] **T11 — Claude `bmad-code-review` (CROSS-AGENT MANDATORY; cross-agent tier)**
  - [ ] T11.1 Verify D1-D8 contract compliance line-by-line; commit + flip done.

---

## Dev Notes

**Why this story is substrate-foundation:** 7c.4b lands the executable shared substrate that 8 per-gate stories (7c.5.G0..G6) inherit. Without this, each per-gate story re-derives base-class invariants + four-file-lockstep firing condition + class-conformance assertion → drift inevitable.

**Why cross-agent MANDATORY at T11:** John A5 + Murat M6. Substrate-shape inherited by 8 stories.

**File / module placement summary (post-D1-D8):**
- `app/models/decision_cards/_base.py` (NEW; underscore-prefix internal interface).
- `app/parity/contracts/tw_7c_3_firing.py` (NEW; AMEND-7d-i single-source).
- `app/parity/contracts/_declaration.py` (extend; +alias_of field).
- `app/parity/contracts/_decorator.py` (extend; +alias_of kwarg).
- `app/manifest/compiler.py` (extend; honor 18 runtime IDs).
- `scripts/utilities/validate_parity_test_class_conformance.py` (extend; +18 ID recognition + LOCKSTEP_CHECK integration + TW-7c-3 firing).
- `pyproject.toml` C6 forbidden_modules population.
- `tests/schemas/operator_verdict/_harness.py` (NEW).
- 6 NEW test files.

**Anti-patterns to avoid:**
- A11 Windows-portability + A-test-1 mocking-SUT.
- Drift-prone re-derivation: 7c.5.G* MUST cite `LOCKSTEP_CHECK` by reference, NEVER re-derive.
- Cross-§section imports: structurally prevented by C6.
- Defensive `serial` markers without empirical xdist failure.

**K-discipline:** K-target 1.4× ≈ ~3.5K LOC ceiling. Estimate ~2.0-3.0K LOC. Comfortable.

### Project Structure Notes

- `tests/parametrized_harness/` is a NEW test directory (verify at T1; create if absent).
- `app/gates/_shared/` is a NEW package (verify at T1; create if absent + add to test-collection paths).

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-4b]
- [Source: docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md] (7c.4a's frozen ADR)
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (7c.0a's frozen ADR)
- [Source: app/parity/contracts/_declaration.py + _decorator.py + _registry.py] (7c.0b's DSL primitives)
- [Source: app/models/tripwire_ledger.py] (7c.0a TripwireLedgerEntry pattern)
- [Source: app/audit/__init__.py] (7c.0b audit-chain helpers; informational)
- [Source: tests/schemas/operator_verdict/test_section_02a_shape.py] (7c.3b pattern-precedent)
- [Source: app/manifest/compiler.py] (Slab 7a 7a.2 substrate)
- [Source: scripts/utilities/validate_parity_test_class_conformance.py] (7c.0a/0b foundation)
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md] (14 idioms)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 + A-test-1)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline 1.4×)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (FR-7c-8/9/49/53)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.4b] (Story 7c.4b section starting at line 572)
- [Source: _bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md#AMEND-V5] (cross-agent pre-flight rationale)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

(Populated during dev round.)

### Completion Notes List

(Populated during dev round; MUST include D1-D8 contract compliance table + lint-imports KEPT 12 + class-conformance ≥11 + broad-regression delta.)

### File List

(Populated during dev round; expected: ~14 files — 7 NEW app modules + 6 NEW tests + 5 modified config/scripts. Net: ~2.0-3.0K LOC.)
