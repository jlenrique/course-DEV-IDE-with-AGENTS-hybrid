# Gate-Decision Node Binding Semantics (Slab 2 convention)

**Adopted:** 2026-04-24 party-mode round 3 Amelia caveat + Mary H5 surface.
**Scope:** every specialist graph in `app/specialists/<name>/graph.py` that
emits a `gate_decision` node (all of them per `SCAFFOLD_NODE_IDS` 9-node
contract).

---

## Problem statement

Slab 1 Story 1.4 shipped `app/gates/resume_api.py` with a **signature-stable
stub**: `resume_from_verdict(verdict: OperatorVerdict) -> NoReturn` that
**raises `NotImplementedError` always**. The stub exists so:

1. Import-linter Contract C3 has a concrete symbol to constrain (the three
   bridge modules — MCP tool `gate_decide`, FastAPI endpoint `gate_endpoint`,
   CLI `gate_cli` — are the ONLY permitted importers).
2. `OperatorVerdict` has a typed consumer surface documented at Slab 1.
3. The tamper-evidence chain has a named entry point the ledger can track.

The full body lands in **Slab 3 Story 3.3**. Until then, calling
`resume_from_verdict()` at runtime raises.

Slab 2 specialists emit `gate_decision` nodes per the 9-node scaffold
contract. **Naively binding the node handler to `resume_from_verdict`
detonates any smoke test that routes through a gate.** This document pins
the correct binding semantics.

---

## Rule

Every specialist's `gate_decision` node:

1. **Imports `resume_from_verdict`** from `app.gates.resume_api` at
   module-level for Contract C3 binding stability (the import is the C3
   binding point; the runtime call is not).
2. **Does NOT invoke `resume_from_verdict` at node-execution time** until
   Slab 3 Story 3.3 replaces the stub body.
3. **Implements the node body as an `interrupt()` placeholder** per
   [`langgraph-state-idioms.md` §5 interrupt()](langgraph-state-idioms.md).
   The interrupt pauses the graph; operator verdict resumes it via the
   bridge modules (also Slab 3).

Slab 2 smoke tests that route through `gate_decision` hit the `interrupt()`
pause, not the raise. Test fixtures that want to exercise the gate path
either (a) pre-populate an `OperatorVerdict` in state and skip the
interrupt, or (b) assert the interrupt fires and halt the test.

## Template (generator emits this pattern — Story 2a.1 AC-D clarification)

```python
# app/specialists/<name>/graph.py
from langgraph.graph import StateGraph
from langgraph.types import interrupt

from app.gates.resume_api import resume_from_verdict  # noqa: F401 — C3 binding; body stays stubbed until Slab 3.3
from app.models.state.run_state import RunState


def gate_decision_node(state: RunState) -> dict:
    """Pause graph for operator verdict; resumes via app.http.gate_endpoint
    or app.mcp_server.tools.gate_decide or app.marcus.cli.gate_cli (Slab 3.3
    bridge modules). Does NOT invoke resume_from_verdict directly."""
    # Slab 2 placeholder: pause; operator verdict arrives via bridge modules.
    # Slab 3 Story 3.3 replaces resume_api.py body with the real resume path
    # AND this node's body stays unchanged (interrupt is the pause surface).
    verdict = interrupt(
        {
            "gate_id": state.current_gate_id,
            "pending_artifact_paths": state.pending_artifact_paths,
            "verdict_verb_options": ["approve", "edit", "reject"],
        }
    )
    # Post-resume: verdict is an OperatorVerdict dict
    return {"last_verdict": verdict}
```

## Test fixtures (two patterns)

**Pattern 1 — pre-populate verdict, skip interrupt:**

```python
def test_gary_passes_gate_with_approve_verdict(tmp_path: Path) -> None:
    graph = build_gary_graph()
    state = RunState(
        run_id=..., graph_version=..., temperature=0.0,
        # Pre-populate so gate_decision's interrupt receives the value via state
        pending_verdict=OperatorVerdict(verb="approve", gate_id="g1.5", ...),
    )
    result = graph.invoke(state)
    assert result.last_verdict.verb == "approve"
```

**Pattern 2 — assert interrupt fires, halt:**

```python
def test_gary_interrupts_at_gate_decision() -> None:
    graph = build_gary_graph()
    state = RunState(run_id=..., graph_version=..., temperature=0.0)
    with pytest.raises(InterruptException):  # langgraph-specific; actual import per LangGraph docs
        graph.invoke(state)
```

---

## §LLM-live (ancillary — Slab 2+ LLM-invoking tests)

Tests that invoke a live LLM must carry `@pytest.mark.llm_live`. The
`tests/conftest.py` skip-fixture auto-skips when `OPENAI_API_KEY` is unset
or equals the Slab-1 placeholder sentinel `sk-substrate-no-real-key-do-not-invoke`.

This prevents the cryptic "invalid api key" failure mode from OpenAI when a
test accidentally reaches a real `.invoke(...)` in an environment without a
real key.

```python
@pytest.mark.llm_live
def test_irene_pass_2_narration_emits_real_output() -> None:
    # Auto-skipped when OPENAI_API_KEY is placeholder or unset
    ...
```

Party-mode round 3 Amelia caveat SP4 (2026-04-24) identified this as the
highest-priority ticking-bomb: without the skip-fixture, a Slab 2b.7 dev
agent who adds a live LLM call in an integration test discovers the problem
via cryptic OpenAI error at CI time instead of clean skip.

---

## Cross-references

- [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md) — 9-node canonical contract; `gate_decision` is node #7
- [`langgraph-state-idioms.md` §5 interrupt()](langgraph-state-idioms.md) — interrupt pattern
- [`langgraph-migration-guide.md §8.1 Upstream Severance`](langgraph-migration-guide.md#81-upstream-severance-slab-2) — severance posture
- [`decision-records/DR-SLAB-1-CLOSE-2026-04-24.md`](../../_bmad-output/planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md) — DR-1 golden ratification; DR-5 forward (severance-reversal teeth)
- `app/gates/resume_api.py` — stub source + Slab 3 Story 3.3 body landing point
