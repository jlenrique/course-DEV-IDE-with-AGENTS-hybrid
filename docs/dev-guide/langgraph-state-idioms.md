# LangGraph State Idioms (Amendment E)

Six idioms every migration specialist author must know, pulled from Story 1.2's
Pydantic state base classes and the bundle §3 LangGraph-state-idioms digest.
Architecture Amendment E designates this doc as a Slab 1 deliverable; Slab 2+
specialists reference it at T1 before touching state-schema code.

> **You-are-here** (Slab 2+ dev-agent reading order at T1):
> 1. [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md) — 9-node canonical contract + T1 pre-flight
> 2. **This doc** — state-shape idioms (interrupt, Command, Send, reducers)
> 3. [`model-selection-guide.md`](model-selection-guide.md) — three-level cascade
> 4. [`specialist-anti-patterns.md`](specialist-anti-patterns.md) — known traps (read before writing ACs)
>
> For gate-decision node binding semantics (import-but-not-invoke discipline),
> see [`gate-decision-binding-semantics.md`](gate-decision-binding-semantics.md).

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

## 6. RetryPolicy + Pydantic interaction

The concrete failure mode in the hybrid runtime is narrower than the original
placeholder implied. The problem is not that LangGraph cannot run with a
Pydantic state schema; that path is already the project baseline. The problem
is that a node which performs its own `model_validate(...)` call against a
flaky intermediate payload and then lets the raw `ValidationError` escape will
not be retried by LangGraph's default `RetryPolicy`. In practice, that means
provider or tool payload validation can fail on attempt one even when the
second invocation would have returned a valid shape. For this project, that is
the wrong boundary: transient payload-shape failures should be retryable,
while terminal schema mismatches should still surface explicitly after the
retry budget is exhausted.

Story 4.7 closes the gap with a wrap-and-route discipline owned by
`app/runtime/retry_policy.py`. The rule is simple: keep Pydantic validation at
the node boundary, but translate `ValidationError` into a runtime-owned
exception class that the graph can intentionally retry. The helper
`validate_for_retry(...)` performs the `model_validate(...)` call and raises
`RetryableValidationNodeError` instead of leaking the raw Pydantic exception.
The companion helper `pydantic_retry_policy(...)` returns a LangGraph
`RetryPolicy` preconfigured with `retry_on=RetryableValidationNodeError`. That
keeps the retry contract explicit and local to the node rather than relying on
framework defaults that are aimed at generic transport failures.

The discipline is deliberately boundary-scoped. Do **not** turn all schema
errors into retryable ones, and do **not** relax the Pydantic models to make
the retry layer happy. Validation that proves a local programming bug, a
closed-enum violation, or a deterministic manifest mismatch should still fail
loudly. The wrapper belongs only around payloads that are expected to be noisy
at the edge: tool output, provider responses, or intermediate envelopes that
become stable on replay. If the payload is locally authored and deterministic,
retrying it is usually cargo culting.

Worked example:

```python
from pydantic import BaseModel

from app.runtime.retry_policy import (
    pydantic_retry_policy,
    validate_for_retry,
)


class Payload(BaseModel):
    value: int


def compose_return(state: dict[str, object]) -> dict[str, object]:
    payload = validate_for_retry(
        Payload,
        flaky_provider_call(),
        node_name="compose_return",
    )
    return {"value": payload.value}


builder.add_node(
    "compose_return",
    compose_return,
    retry_policy=pydantic_retry_policy(max_attempts=2, jitter=False),
)
```

The paired integration test in
`tests/integration/runtime/test_retry_policy_pydantic.py` demonstrates both
sides of the boundary. Without the wrapper, a bad first payload raises raw
`ValidationError` and the graph stops after a single attempt. With the wrapper
and the retry policy helper, the first bad payload becomes a retryable
runtime-owned exception, the node runs a second time, and the valid payload
completes successfully. That is the architecture the migration needs: retries
for transient edge payloads, explicit failure for deterministic schema drift,
and no silent relaxation of the Pydantic contract.

## Related

- Architecture Amendment E (this doc's anchor)
- Pydantic v2 14-idiom checklist:
  [`pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md)
- State base classes: `app/models/state/_base.py` + the eight state models under
  `app/models/state/`
- Story 1.2 closure: `_bmad-output/implementation-artifacts/migration-1-2-pydantic-state-base-classes.md`
