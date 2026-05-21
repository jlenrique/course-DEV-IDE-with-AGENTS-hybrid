# ADR 0002: Slab 7c Gate Taxonomy

Status: ACCEPTED - 2026-05-05 by single-gate dev round, Story 7c.4a.

Predecessor state: 7c.0a and 7c.0b are done. ADR 0001 fixed decorator-based
parity-contract registration and the Pydantic-v2 transport declaration shape.
The executable 7c.0b scaffold does not yet expose an alias field, so this ADR
ratifies the alias taxonomy and the forward syntax that 7c.4b and the 7c.5
gate stories consume.

References:

- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md`
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md`
- `docs/dev-guide/adr/0001-parity-contract-dsl.md`
- `docs/dev-guide/migration-story-governance.json` story `7c-4a`
- Downstream consumers: 7c.4b, 7c.5.G0 through 7c.5.G6, and 7c.20c

## Decision

Slab 7c uses one frozen gate taxonomy with three distinct counts:

1. Eight family contracts are authored or extended by Wave 2 stories:
   `G0`, `G1`, `G2A`, `G2C`, `G3`, `G4`, `G5`, `G6`.
2. Ten explicit alias mappings are valid. The older "6 alias gates" wording is
   a stale count; the enumerated mappings are authoritative.
3. The FR-7c-6 runtime `PRODUCTION_GATE_IDS` set is the 18-ID list enumerated
   in the PRD: `G0`, `G0A`, `G0B`, `G1`, `G1A`, `G1.5`, `G2`, `G2B`, `G2C`,
   `G2M`, `G2.5`, `G2F`, `G3`, `G3B`, `G4`, `G4A`, `G4B`, `G5`.

The "4 -> 14" phrase remains a planning shorthand for Slab 7c expansion and
AUDIT grouping. It is not the final runtime ID cardinality. For implementation,
downstream stories must treat the explicit 18 runtime IDs as canonical and must
treat the eight family contracts as the four-file-lockstep authoring target.

## 1. Net-New Gate Families

This section freezes the eight family contracts that downstream Wave 2 stories
author or extend. Four are fresh-author stories; four are shipped substrate
families that move through extend-and-audit contract evolution.

| Family | Meaning | Treatment |
| --- | --- | --- |
| `G0` | Trial-open / corpus-confirm gate. | Fresh-author in 7c.5.G0. |
| `G1` | Directive-ratification gate. | Already shipped; extend-and-audit in 7c.5.G1. |
| `G2A` | Plan-unit-ratification gate family. | Fresh-author in 7c.5.G2A. |
| `G2C` | Pre-composition QA gate. | Already shipped; extend-and-audit in 7c.5.G2C. |
| `G3` | Motion-clip approval gate. | Already shipped; extend-and-audit in 7c.5.G3. |
| `G4` | Fidelity gate. | Already shipped; extend-and-audit in 7c.5.G4. |
| `G5` | Final operator handoff gate. | Fresh-author in 7c.5.G5. |
| `G6` | Slab-close ceremony gate. | Fresh-author in 7c.5.G6. |

Reconciliation: story text sometimes calls all eight "net-new gate families"
even though `G1`, `G2C`, `G3`, and `G4` already exist. The operational reading
is eight post-Slab-7c family contracts: four fresh-author (`G0`, `G2A`, `G5`,
`G6`) plus four extend-and-audit (`G1`, `G2C`, `G3`, `G4`).

`G2A` and `G6` are family-contract authoring targets. They are not part of the
FR-7c-6 18-ID Trial-3 runtime list unless a later manifest story explicitly
promotes them into runtime dispatch. This keeps the PRD's explicit runtime list
authoritative while preserving the Wave 2 per-family story plan.

## 2. Alias Gates

The canonical alias count is ten explicit mappings. The "6 alias gates" wording
in earlier PRD and epic prose is stale because it conflicts with the mappings
listed in the same sources.

| Alias | Parent family | Consumer surface |
| --- | --- | --- |
| `G0A` | `G1` | Operator-corrects-corpus surface. |
| `G0B` | `G1` | Operator-edits-directive surface. |
| `G1A` | `G1` | Per-plan-unit ratification surface, section 04A. |
| `G2B` | `G2C` | Per-slide mode surface, section 05.5. |
| `G2M` | `G2C` | Per-slide A/B variant surface, section 07B. |
| `G2.5` | `G2C` | Motion-plan polling surface, section 07D. |
| `G2F` | `G2C` | Motion gate surface, section 07F. |
| `G3B` | `G3` | Storyboard B plus live-URL surface, section 08B. |
| `G4A` | `G4` | Voice-selection surface, section 11. |
| `G4B` | `G4` | Input-package and final handoff surface, section 11B / 15. |

Alias gates do not receive independent four-file-lockstep stories. They inherit
the parent family contract and are verified through alias-aware lockstep audit.

`G1.5` and `G2` are runtime IDs in FR-7c-6 but are not separate alias rows in
this table. `G1.5` is covered by the `G1` family contract. `G2` is the runtime
umbrella label for the G2 family path and is covered by `G2A` / `G2C` downstream
interpretation.

## 3. Alias-DSL Clause Inheritance

ADR 0001 chose decorator registration and a Pydantic-v2 declaration model with
these fields:

- `surface_id`
- `mandatory_transports`
- `optional_transports`

The executable 7c.0b scaffold preserves that shape and does not yet include an
alias clause. This ADR therefore ratifies the forward-compatible alias syntax:

```python
@parity_contract(
    surface_id="G0A",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G1",
)
def register_g0a_surface() -> None:
    ...
```

7c.4b owns the executable addition, either as an `alias_of: str | None` field on
the existing declaration model or as an equivalent `AliasGateDeclaration` that
resolves to the same registry semantics. The behavior is fixed here:

- `surface_id` remains the runtime gate or HIL surface ID.
- `alias_of` names one parent family from the eight-family taxonomy.
- The alias inherits the parent's four-file-lockstep contract.
- The alias may declare transport coverage for its own operator surface.
- AUDIT tooling reports both the alias ID and the inherited parent family.

The inheritance relation is about lockstep contract ownership. It does not
erase the alias runtime ID, because FR-7c-6 requires runtime introspection over
the explicit post-expansion ID list.

## 4. PRODUCTION_GATE_IDS Expansion

Pre-Slab-7c shipped runtime card support for four terminal gates:

```text
G1, G2C, G3, G4
```

FR-7c-6 enumerates the post-Slab-7c runtime IDs as:

```text
G0, G0A, G0B, G1, G1A, G1.5, G2, G2B, G2C, G2M, G2.5, G2F, G3, G3B, G4, G4A, G4B, G5
```

That list contains 18 runtime IDs. It is canonical for runtime dispatch,
manifest folding, and Trial-3 observability. The repeated "4 -> 14" phrase is
kept only as historical planning language; it must not be used to drop IDs from
the FR-7c-6 enumeration.

The audit target is not 18 independent four-file-lockstep file sets. The audit
target is eight family contracts plus alias inheritance:

- Direct family contract: `G0`, `G1`, `G2A`, `G2C`, `G3`, `G4`, `G5`, `G6`.
- Alias inheritance: `G0A`, `G0B`, `G1A`, `G2B`, `G2M`, `G2.5`, `G2F`,
  `G3B`, `G4A`, `G4B`.
- Runtime covered labels: `G1.5` under `G1`, and `G2` under the G2 family path.

7c.20c should report both numbers: 18 runtime IDs are visible, and every ID is
covered by one of the eight family contracts directly or by an explicit alias /
covered-label relationship.

## 5. Status Line and Cross-References

Status: ACCEPTED - 2026-05-05 by single-gate dev round, Story 7c.4a.

Predecessor: 7c.0b done. ADR 0001 and the 7c.0b scaffold establish decorator
registration; this ADR establishes alias semantics for downstream executable
work.

Cross-references:

- PRD Gate Taxonomy LOCK, Step 11, Amelia A3.
- Epic Story 7c.4a, plus AMEND-5 fresh-author vs extend-and-audit split.
- Governance JSON story `7c-4a`, single-gate, prerequisite `7c-0b`.
- Downstream 7c.4b: executable alias declaration, class-conformance extension,
  HIL boundary enforcement, and TW-7c-3 lockstep checker registration.
- Downstream 7c.5.G0 through 7c.5.G6: family four-file-lockstep authoring.
- Downstream 7c.20c: AUDIT of runtime ID coverage plus alias inheritance.

## Worked Example: G0A Inherits G1

`G0A` is the operator-corrects-corpus runtime surface. It is a runtime ID but not
a separate DecisionCard family. It inherits `G1`'s lockstep contract.

Proposed 7c.4b declaration:

```python
@parity_contract(
    surface_id="G0A",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G1",
)
def register_operator_corrects_corpus_surface() -> None:
    ...
```

Four-file-lockstep audit routing:

| G0A audit question | Resolved parent artifact |
| --- | --- |
| Pydantic model | `app/models/decision_cards/g1.py` |
| JSON schema | `app/models/decision_cards/schema/g1.v1.schema.json` |
| Shape-pin test | `tests/parity/test_decision_card_g1_shape.py` |
| Golden fixture | `tests/fixtures/decision_cards/g1_golden.json` |

Runtime emission:

- The runtime event may retain `gate_id="G0A"` for traceability and operator
  transcript evidence.
- The typed card shape is the `G1` family shape.
- `DecisionCardMeta.cache_state` is populated exactly as the `G1` parent
  contract requires.
- The audit ledger records `surface_id="G0A"` and `alias_of="G1"` so reviewers
  can distinguish runtime coverage from family-contract ownership.

This example is normative for all alias rows in section 2. An alias can carry
surface-specific transport parity declarations, but it cannot fork the parent's
DecisionCard shape without becoming a new family contract and reopening this ADR.
