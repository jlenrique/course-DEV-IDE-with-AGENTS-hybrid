# Migration Story 3.2: DecisionCard Schema Family + Per-Gate Models

**Status:** ready-for-dev
**Sprint key:** `migration-3-2-decision-card-schema-family`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; M3 go/no-go gate).
**Pts:** 4 | **Gate:** dual (per governance JSON `3-2.expected_gate_mode = "dual-gate"`, rationale: `schema_shape`). **K-target:** ~1.5× (target 16 / floor 12; 4 per-gate model families × four-file-lockstep + DecisionCardMeta + manifest dotted-reference resolver test + golden-fixture parity).

**Predecessor:** Story 3.1 must be `done` (`app.marcus.routing` consumes manifest `edge.decision_card_schema` dotted-reference per AC-3.2-B; 3.1 establishes Marcus orchestrator package that 3.2's models plug into).

**SUBSTRATE-AWARE ADAPTATION applied 2026-04-26 post-Codex 3.1 T1 halt cascade analysis:** 3.2 substrate verified — `app/models/decision_cards/` has only `__init__.py` + `README.md` (Slab-1 stub; genuine substrate gap, 3.2 IS additive authoring). Three corrections applied:
- **Manifest path correction:** `state/config/run-manifest.yaml` → `state/config/pipeline-manifest.yaml` (live filename verified 2026-04-26).
- **Manifest field shape correction:** epic 3.2's hypothetical `edge.decision_card_schema` field does NOT exist on hybrid `pipeline-manifest.yaml`; live shape uses `nodes[*].specialist_id` + `edges[*].dispatch_envelope`. **AC-C resolver test reframed:** assert dotted-reference resolver mechanism works for any future manifest field carrying the form `<module>:<ClassName>`; T1 sub-task verifies whether `decision_card_schema` field is added at this story OR deferred (operator decision; default = add as additive optional manifest field at this story since 3.2 is the schema-family ship-target).
- **RunState path correction:** any references to `app/state/run_state.py` rewrite to `app/models/state/run_state.py` (live location verified at app/models/state/{cache_state, model_resolution_entry, node_checkpoint, operator_verdict, run_state, sanctum_fingerprint, specialist_envelope, specialist_return, story_state}.py + validators/ subdir).

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia):** 5 RIDERs integrated:
- **A-R1-3.2 (resolver substrate verification):** T1 sub-task — verify `app/manifest/refs.py::resolve_dotted_ref(manifest, "edge.decision_card_schema")` (or equivalent) callable exists; if aspirational, dev-agent T1 scaffolds before per-gate model imports.
- **A-R2-3.2 (gate enum cross-check):** T1 sub-task — cross-check `marcus.gates.Gate` (or wherever gate enum landed at 3.1) for exact members; if 3.1 deferred a gate, ship 3 models + DEFERRED row OR expand the enum.
- **A-R3-3.2 (pydantic-v2 checklist citation):** T1 readings explicitly cite `docs/dev-guide/pydantic-v2-schema-checklist.md` 14 idioms; G6 will MUST-FIX if missing.
- **M-R1-3.2 (negative tests per family):** Each Pydantic family MUST have ≥1 **negative** test per closed enum + ≥1 **timezone-naive datetime rejection** test (per checklist §triple-layer red-rejection). Don't ship 10 happy-path tests claiming K=10.
- **M-R2-3.2 (schema-emission hashing):** JSON Schema golden tests hash the emitted schema (sha256 over canonical JSON), NOT deep-compare dicts (dict-compare flakes on key ordering across Pydantic patches).

**Authoring queue position:** drafted-for-queue per operator directive 2026-04-26 (parallel to Codex 2c.x batch-dev). Spec stays at `ready-for-dev` BUT will not enter dev until 3.1 closes.

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `3-2.expected_gate_mode = "dual-gate"` (rationale: `schema_shape`). Do not relitigate.
2. **31-1 precedent (BINDING)** — `_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md` is THE schema-shape story precedent for this migration's four-file-lockstep convention (Pydantic v2 model + emitted JSON Schema + shape-pin tests + golden fixture). All 14 Pydantic-v2 idioms at `docs/dev-guide/pydantic-v2-schema-checklist.md` are MANDATORY.
3. **Schema-story scaffold (BINDING per Lesson-Planner-MVP convention)** — `docs/dev-guide/scaffolds/schema-story/` carries the canonical 4-file-lockstep recipe + `instantiate_schema_story_scaffold.py` script. Pre-instantiate stubs for ALL 4 gate families (G1, G2C, G3, G4) before dev opens substantive work.
4. **Architecture doc D2 + D7** — `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` §D2 (DecisionCardMeta carries cache_state + affected_nodes + override_trail) + §D7 (per-gate schema family).
5. **3.1 architectural foundation** — `app/marcus/orchestrator/routing.py` consumes `manifest.edges[node].decision_card_schema` dotted-reference (per Story 3.1 AC-I + Decision #6 D6 manifest validation).
6. **Slab 1 substrate** — `app/models/decision_cards/__init__.py` is empty Slab-1 stub; this story populates the package.
7. **Pydantic-v2 schema checklist** — `docs/dev-guide/pydantic-v2-schema-checklist.md` 14 idioms (validate_assignment=True; tz-aware datetimes; UUID4 validation; closed-enum triple-layer rejection; Field(exclude=True)+SkipJsonSchema for internal audit fields; etc.).
8. **31-1 G6 patches as anti-pattern targets** — A4 silent-mutation, A5 naive datetime, A6 closed-enum-one-rejection-surface — DO NOT REPRODUCE.
9. **Anti-patterns catalog** — `docs/dev-guide/specialist-anti-patterns.md` A4-A8 schema-family entries (post-31-1 close).
10. **Severance posture** — hybrid working tree.

### Slab 3.2 artifact-existence sweep (6-point)

- **A** `app/models/decision_cards/__init__.py` exists as Slab-1 stub.
- **B** `app/marcus/orchestrator/routing.py` exists post-3.1 (consumes `decision_card_schema` dotted-reference).
- **C** `state/config/run-manifest.yaml` carries `edge.decision_card_schema` field shape per 3.1 AC-I (verify; if absent, 3.1 close-state regression).
- **D** `docs/dev-guide/scaffolds/schema-story/` scaffold present + `instantiate_schema_story_scaffold.py` runnable.
- **E** `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` exists per 31-1 R2 rider AM-1 precedent (one CHANGELOG per shape family).
- **F** `docs/dev-guide/pydantic-v2-schema-checklist.md` exists with 14 idioms.

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

**One drift:** epic 3.2 lists 4 gates `G1, G2C, G3, G4`; architecture doc D7 lists same. Some prior planning artifacts reference `G2A, G2B, G2C` separately. **Resolution:** epic 3.2 is canonical for THIS story; G2A/G2B are Slab-4-Cora-scope (not Marcus-orchestrator); G1/G2C/G3/G4 ship at 3.2.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) `app/models/decision_cards/{base, g1, g2c, g3, g4}.py` Pydantic-v2 strict + four-file-lockstep × 4 gates; (b) `DecisionCardMeta` carrying cache_state + override_trail + reject_rate context per D2; (c) manifest dotted-reference resolver test (D6 validation); (d) golden-fixture parity per family. NOT in scope: OperatorVerdict (3.3); resume_api impl (3.3); transport surfaces (3.4); model-override surfaces (3.5).

**Decision #2 — Per-gate field discrimination:** each gate carries a `gate_id: Literal["G1"|"G2C"|"G3"|"G4"]` discriminator; cross-gate operations on a `DecisionCard` use Pydantic discriminated-union. Validates closed-enum triple-layer rejection per A6 anti-pattern.

**Decision #3 — `OverrideEvent` reuse vs new model:** D2 mandates `override_trail: list[OverrideEvent]`. If `OverrideEvent` exists at Slab-1 substrate, reuse; else author at this story (additive minimal extension; document if NEW). Verify at T1.

---

## Story

As a **dev agent implementing HIL gates per FR32 + D7**,
I want **`app/models/decision_cards/{base,g1,g2c,g3,g4}.py` with per-gate Pydantic v2 strict subclasses + `DecisionCardMeta` carrying `cache_state: Literal["healthy","mixed","cold"]` + `affected_nodes: list[str]` + `override_trail: list[OverrideEvent]` per D2 + four-file-lockstep × 4 gates + manifest dotted-reference resolver test (D6) + golden-fixture parity**,
So that **FR32 + D7 per-gate schema family is in place, gate schema drift is compile-time detectable via discriminated-union strict typing, and Stories 3.3-3.6 build on a stable contract**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Sandbox-AC compliant.

### AC-3.2-A — Base `DecisionCard` + `DecisionCardMeta` per D2

- **Given** no `app/models/decision_cards/base.py` exists beyond Slab-1 `__init__.py` stub
- **When** the dev agent authors `base.py::DecisionCard` + `DecisionCardMeta`:
  - `DecisionCard` Pydantic v2 strict (`model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=False)`); fields: `card_id: UUID4`, `trial_id: UUID4`, `gate_id: str`, `created_at: datetime` (tz-aware UTC), `drafted_proposal: dict[str, Any]`, `evidence: list[dict[str, Any]]`, `risks: list[str]`, `verb: Literal["approve", "edit", "reject"]`, `meta: DecisionCardMeta`
  - `DecisionCardMeta` Pydantic v2 strict; fields: `cache_state: Literal["healthy", "mixed", "cold"]`, `affected_nodes: list[str]`, `override_trail: list[OverrideEvent]`, `reject_rate: float = Field(ge=0.0, le=1.0)`
- **Then** four-file-lockstep present: model + JSON Schema (`schema/decision_card_base.v1.schema.json`) + shape-pin test + golden fixture.
- **Test pin:** `tests/unit/models/decision_cards/test_decision_card_base_strict.py` — 3 tests: model_config (`extra="forbid"` + `validate_assignment=True`), tz-aware datetime rejection (naive datetime raises), verb closed-enum triple-layer rejection (invalid verb raises at construction + assignment + JSON parse).

### AC-3.2-B — Per-gate subclasses G1, G2C, G3, G4 (DUAL-GATE schema-shape gate-1)

- **Given** `base.py` shipped at AC-A
- **When** the dev agent authors `app/models/decision_cards/{g1, g2c, g3, g4}.py` per-gate subclasses:
  - Each subclass inherits `DecisionCard`; pins `gate_id: Literal["G1"]` (or G2C/G3/G4) — closed-enum-one-value pattern per gate
  - Each gate adds gate-specific fields per architecture D7 (G1 = trial-open envelope; G2C = pre-execution sanity check; G3 = mid-trial verdict; G4 = post-trial close); fields enumerated in spec body at dev-time per substrate research
  - Discriminated-union pattern: `from typing import Annotated; AnyDecisionCard = Annotated[Union[G1Card, G2CCard, G3Card, G4Card], Field(discriminator="gate_id")]` exported from `app/models/decision_cards/__init__.py`
- **Then** four-file-lockstep × 4 gates: 4 model files + 4 JSON Schemas + 4 shape-pin tests + 4 golden fixtures.
- **Test pins:**
  1. `tests/unit/models/decision_cards/test_per_gate_strict.py` — 4 tests (parametrize over G1/G2C/G3/G4 → 1 K-floor unit per Murat M-R18 same-property convention): each subclass has `extra="forbid"` + `validate_assignment=True` + `gate_id` Literal-pinned + `verb` closed-enum.
  2. `tests/unit/models/decision_cards/test_discriminated_union_routing.py` — 4 tests (parametrize → 1 K-floor unit): construct each gate from JSON; assert discriminated-union routes to correct subclass.
  3. `tests/unit/models/decision_cards/test_per_gate_json_schema_parity.py` — 4 tests (parametrize → 1 K-floor unit): each emitted JSON Schema matches the model's `model_json_schema()` (post-31-1 G6 by_alias=True audit-path test per A4).
  4. `tests/unit/models/decision_cards/test_per_gate_golden_fixtures.py` — 4 tests (parametrize → 1 K-floor unit): each golden fixture round-trips (parse → serialize → byte-identical).

### AC-3.2-C — Manifest dotted-reference resolver test (D6 validation)

- **Given** `state/config/run-manifest.yaml::edge.decision_card_schema` field carries dotted-references like `"app.models.decision_cards.g2c:G2CCard"` per Story 3.1 AC-I substrate
- **When** the manifest compiler validates the manifest at compile time (`compile_run_graph(manifest, validation_mode=True)`)
- **Then** each dotted reference is **importable**; compile fails with `ManifestSchemaImportError` if not (per D6 validation).
- **Test pin:** `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — 2 tests:
  1. `test_valid_dotted_reference_imports` — 4 valid references (one per gate) all import successfully via `importlib.import_module(...)` + `getattr(module, class_name)`; assert each returned class is a `DecisionCard` subclass.
  2. `test_invalid_dotted_reference_fails_compile` — synthetic invalid reference `"app.models.decision_cards.g99:G99Card"` raises `ManifestSchemaImportError` at compile.

### AC-3.2-D — `OverrideEvent` model (per Decision #3 — verify reuse vs author)

- **Given** D2 mandates `override_trail: list[OverrideEvent]`
- **When** the dev agent verifies at T1 whether `OverrideEvent` exists at Slab-1 substrate
- **Then**:
  - **If exists:** reuse the existing model; document the import path in spec body.
  - **If absent:** author `OverrideEvent` Pydantic v2 strict at `app/models/decision_cards/override_event.py` with fields: `event_id: UUID4`, `applied_at: datetime` (tz-aware), `node_id: str`, `previous_value: dict[str, Any]`, `new_value: dict[str, Any]`, `operator_id: str`, `confirm_token: str`. Four-file-lockstep applies.
- **Test pin:** `tests/unit/models/decision_cards/test_override_event_strict.py` — 1 test (or skip with reason if reusing existing model + the existing has its own tests).

### AC-3.2-E — Anti-pattern catalog harvest (per R6)

NO new anti-pattern signals expected. If schema-shape friction surfaces (e.g., discriminated-union edge case beyond A6), file as candidate per harvest-gate at 2c.4 close cycle.

### AC-3.2-F — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored. Schema-shape stories follow `docs/dev-guide/scaffolds/schema-story/` scaffold (BINDING per Lesson-Planner-MVP convention; pre-instantiate stubs for all 4 gates before dev opens substantive work).

### AC-3.2-G — D12 close protocol (DUAL-gate; schema_shape; FIVE-line per dual-gate convention pinned at 3.1 P-R3 verification)

1. **Invariant preservation:** schema-shape integrity (4-file-lockstep × 4 gates); discriminated-union routing; manifest D6 validation.
2. **Anti-pattern harvest:** N/A unless surfaced.
3. **Migration-guide update:** §"Schema Shape Stories" deepened with 4-gate DecisionCard family precedent; `SCHEMA_CHANGELOG.md` entry added per 31-1 R2 rider AM-1 (one CHANGELOG per shape family).
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: 4 model files + 4 JSON Schemas + 4 shape-pin tests + 4 golden fixtures + 1 base + 1 meta + 1 OverrideEvent (if NEW).
5. **Dual-gate gate-2 (operator schema-shape review):** operator confirms G1/G2C/G3/G4 field shapes against architecture D7 + reads `SCHEMA_CHANGELOG.md` entry.

### AC-3.2-H — Sprint-status state-flips at filing AND at close

At filing: `migration-3-2-decision-card-schema-family: ready-for-dev`. At close: `migration-3-2-...: done`; epic stays `in-progress`. `last_updated` updated.

---

## File Structure Requirements

### NEW files

```
app/models/decision_cards/
├── base.py                              # AC-A DecisionCard + DecisionCardMeta
├── g1.py                                # AC-B G1Card (trial-open envelope)
├── g2c.py                               # AC-B G2CCard (pre-execution sanity)
├── g3.py                                # AC-B G3Card (mid-trial verdict)
├── g4.py                                # AC-B G4Card (post-trial close)
├── override_event.py                    # AC-D (NEW or reuse — verify at T1)
└── schema/
    ├── decision_card_base.v1.schema.json
    ├── g1.v1.schema.json
    ├── g2c.v1.schema.json
    ├── g3.v1.schema.json
    └── g4.v1.schema.json

tests/unit/models/decision_cards/
├── test_decision_card_base_strict.py                 # 3 tests (AC-A)
├── test_per_gate_strict.py                           # 4 tests parametrize (AC-B)
├── test_discriminated_union_routing.py               # 4 tests parametrize (AC-B)
├── test_per_gate_json_schema_parity.py               # 4 tests parametrize (AC-B)
├── test_per_gate_golden_fixtures.py                  # 4 tests parametrize (AC-B)
├── test_manifest_dotted_reference_resolver.py        # 2 tests (AC-C)
└── test_override_event_strict.py                     # 1 test (AC-D)

tests/fixtures/decision_cards/
├── g1_golden.json
├── g2c_golden.json
├── g3_golden.json
└── g4_golden.json
```

### MODIFIED files

- `app/models/decision_cards/__init__.py` — exports discriminated-union `AnyDecisionCard` + per-gate classes.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — entry per AC-G §3 (one per shape family per 31-1 R2 rider AM-1).
- `docs/dev-guide/langgraph-migration-guide.md` — §"Schema Shape Stories" deepened.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.

---

## Testing Requirements

**K-target ~1.5× (target 16 / floor 12).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 3 (base strict) | **3** (3 orthogonal: strict-config + tz-aware + verb-closed-enum) |
| B | 4×4 = 16 (parametrize × 4 gates × 4 properties) | **4** (4 properties × 1 K-floor unit each per M-R18) |
| C | 2 (resolver) | **2** |
| D | 1 (override_event) | **1** |
| **Total** | **22 collected** | **10 K-floor units** |

**Honest K-floor: 10** (under floor 12). RIDER: AC-A adds 1 supplementary test for `affected_nodes` list-discipline + AC-C adds `test_resolver_caches_imports` for performance pin = 12 K-floor floor met legitimately. Spec-author elects to ship at 10 K-floor with operator override at 12 if dev-time reveals genuine 12-property surface; recalibrate K-target to ~1.4× (target 14 / floor 10) honest if 10 is the firm count.

**Regression target at T8:** baseline post-Slab-2c-close + post-3.1-close (T1-pinned per Murat M-R8 inheritance from 3.1). +22 collected at file level. Import-linter contracts unchanged. Ruff clean. Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
