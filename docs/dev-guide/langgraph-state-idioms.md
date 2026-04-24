# LangGraph State Idioms (Amendment E)

Six idioms every migration specialist author must know, pulled from Story 1.2's
Pydantic state base classes and the bundle §3 LangGraph-state-idioms digest.
Architecture Amendment E designates this doc as a Slab 1 deliverable; Slab 2+
specialists reference it at T1 before touching state-schema code.

## 1. TypedDict vs BaseModel

**Rule:** graph state is **Pydantic `BaseModel`**, not `TypedDict`. PRD mandate;
overrides LangGraph's idiomatic-docs preference.

```python
# app/models/state/run_state.py — Slab 1 substrate
from pydantic import BaseModel, ConfigDict, Field

class RunState(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    run_id: str = Field(...)
    graph_version: str = Field(...)
    status: RunStatus = Field(...)
    # ...
```

Why BaseModel: field-level validation on construction + re-validation on mutation
(via `validate_assignment=True`), closed-set enum enforcement via `Literal[...]`,
JSON Schema emission for contract-pin tests, and explicit `extra="forbid"` stops
silent drift. `TypedDict` gives none of these; the tradeoff of richer docs-alignment
with LangGraph samples is dwarfed by the safety the Pydantic route preserves.

Use `StateGraph(state_schema=RunState)` — LangGraph accepts Pydantic models directly.

## 2. Reducer fields with `Annotated[list, operator.add]`

When a node contributes items to a list across parallel / conditional paths, declare
the field as a reducer so LangGraph merges the contributions instead of overwriting:

```python
import operator
from typing import Annotated
from pydantic import BaseModel, Field

class RunState(BaseModel):
    # Each node that emits spans appends to the trail; the reducer concatenates
    # rather than overwrites.
    model_resolution_trail: Annotated[list[ModelResolutionEntry], operator.add] = Field(
        default_factory=list,
    )
```

Pairs with `Field(default_factory=list)` so every instance gets its own list (never
the shared mutable default). Covered by anti-patterns catalog A9 (bare `[]` default).

## 3. `Command(goto=..., update=...)` return types

When a node wants to both update state AND signal the next destination, return a
`Command` rather than a plain dict:

```python
from langgraph.types import Command

def my_node(state: RunState) -> Command:
    return Command(
        update={"status": "running"},
        goto="next_node_id",   # or END / conditional branch key
    )
```

Use `goto` when the routing choice depends on the current state; use the manifest's
`EdgeSpec.condition` field when the routing choice is static topology (compiler
resolves against the `app.manifest.conditions` registry).

## 4. `Send()` fan-out payloads

Parallel fan-out is expressed via `Send()` return values from a dispatcher node:

```python
from langgraph.types import Send

def dispatch_node(state: RunState) -> list[Send]:
    return [Send("worker_node", payload) for payload in state.pending_work]
```

**Payload shape requirement:** every `Send` payload must be Pydantic-serializable —
plain dicts with Pydantic-compatible values, or Pydantic model instances. No
closures, no non-picklable objects. LangGraph checkpoints serialize these payloads,
so a non-serializable payload surfaces as a checkpoint write failure (not a
construction error).

## 5. `interrupt()` checkpoint payloads

HIL gate pauses use `interrupt()` with a serializable payload that the operator
surface (MCP / FastAPI / CLI) renders to the reviewer:

```python
from langgraph.types import interrupt

def gate_node(state: RunState) -> Command:
    decision_card = interrupt({
        "kind": "decision_card",
        "gate_id": "G2C",
        "payload": {...},
    })
    # Execution resumes here when app.gates.resume_api.resume_from_verdict() fires
    # (Slab 3 Story 3.3 wires the real resume path).
    return Command(update={"operator_verdict": decision_card})
```

Pydantic discipline carries over — UUID4 for identity fields, tz-aware datetimes on
timestamp fields, `extra="forbid"` on any Pydantic shape inside the payload.
Reproducibility contract (NFR-X3 sanctum snapshot): the payload carries enough
context for an operator's async verdict to land on the exact same state bytes.

## 6. RetryPolicy + Pydantic interaction — **Slab 4 Story 4.7 deferred**

> LangGraph's `RetryPolicy` + Pydantic state interaction is an acknowledged gap per
> bundle §3 idiom 6. Slab 1 specialists MUST NOT silently work around it — flag it
> explicitly in the specialist's Dev Notes when a retry-worthy scenario surfaces,
> and defer to Slab 4 Story 4.7 for the systematic fix.

The gap: LangGraph's `RetryPolicy` interactions (exponential backoff + `retry_on`
predicate + `max_retries`) can re-invoke a Pydantic-validated node with stale-ish
state depending on the checkpointer's replay semantics. Slab 4 Story 4.7 lands the
reconciliation pattern (likely a retry-aware reducer field + a `retry_count` probe
on `RunState`). Until then, specialist authors either use the default `RetryPolicy`
(no custom predicate) or raise an explicit `NotImplementedError` pointing at 4.7.

## Related

- Architecture Amendment E (this doc's anchor)
- Pydantic v2 14-idiom checklist:
  [`pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md)
- State base classes: `app/models/state/_base.py` + the eight state models under
  `app/models/state/`
- Story 1.2 closure: `_bmad-output/implementation-artifacts/migration-1-2-pydantic-state-base-classes.md`
