# Scaffold-Conformance Framework (Slab 1 → Slab 2 handoff)

Slab 2+ specialist migrations ship a `graph.py` exposing a LangGraph subgraph
with the canonical 9-node scaffold. The framework authored at Story 1.7
validates that each specialist conforms; a non-conforming specialist fails
the conformance test and blocks the story's close.

> **You-are-here** (Slab 2+ dev-agent reading order at T1):
> 1. **This doc** — 9-node canonical contract + T1 Readiness Pre-Flight (see §T1 Readiness Pre-Flight below)
> 2. [`langgraph-state-idioms.md`](langgraph-state-idioms.md) — state-shape idioms (interrupt, Command, Send, reducers)
> 3. [`model-selection-guide.md`](model-selection-guide.md) — three-level cascade
> 4. [`specialist-anti-patterns.md`](specialist-anti-patterns.md) — known traps (read before writing ACs)
>
> For gate-decision node binding semantics (interrupt vs resume_from_verdict),
> see [`gate-decision-binding-semantics.md`](gate-decision-binding-semantics.md).

## T1 Readiness Pre-Flight (standing protocol, Slab 2+)

Every Slab 2+ story's T1 Readiness block MUST include an **epic-doc-vs-framework
cross-check** line item per anti-pattern #3 (architecture-vs-epics drift):

> **Cross-check:** identify the authoritative framework source for any contract
> referenced in the story's ACs (e.g., `scaffold_contract.py::SCAFFOLD_NODE_IDS`
> for node names, `app/models/state/` for state shapes, `model_config.yaml` for
> cascade). Compare against the epic-doc AC text. If drifts exist, flag in T1
> Readiness, use the framework, and harvest the drift as a
> [`specialist-anti-patterns.md`](specialist-anti-patterns.md) entry at close.

**Worked example (Story 2a.1, 2026-04-24):** the 2a.1 spec identified that Epic
2a line 555 used stale node names
(`plan/enter_sanctum/load_expertise/reason/act/validate/emit/return/exit_sanctum`)
that did not match `scaffold_contract.py::SCAFFOLD_NODE_IDS`
(`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`).
T1 Readiness flagged the drift; framework won; epic-doc line 555 was retained
unmodified as live exhibit material with an inline KNOWN-DRIFT marker; story
closure added anti-pattern catalog entry.

**AC-I' closure note (Story 2a.1):** This section is the standing Slab-2+
pre-flight template reference. Story 2a.1 dev-story completion verified this
line item remains present and authoritative for follow-on stories.

## How specialists register

Per-specialist conformance tests live at
`tests/integration/scaffold_conformance/test_scaffold_<specialist>.py`. A
minimal registration looks like:

```python
# tests/integration/scaffold_conformance/test_scaffold_texas.py
from app.specialists.texas.graph import build_texas_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_texas_conforms_to_9_node_scaffold() -> None:
    subgraph = build_texas_graph()
    result = validate_scaffold("texas", subgraph)
    assert result.is_conforming, (
        f"Texas scaffold drift — missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
```

The 9 canonical node ids are frozen at Slab 1 close and live in
`tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`.
Changing the set is a Slab-wide architecture amendment (party-mode required).

## The 9 nodes

| Node id | Role |
|---|---|
| `receive` | Accept `SpecialistEnvelope`; validate lane + cache-prefix. |
| `plan` | Pre-act planning; cache-warming + resolution-trail append. |
| `act` | The LLM-invoking step (Slab 1 passthrough stub target). |
| `verify` | Cross-field invariants + schema-pin checks on outputs. |
| `reflect` | Self-assessment; feeds Vera-style drift detection. |
| `emit_spans` | LangSmith span emission per NFR-O4 resolution trail. |
| `gate_decision` | Optional HIL gate pause via `interrupt()`. |
| `finalize` | Build `SpecialistReturn`; attach `OperatorVerdict` if present. |
| `handoff` | Return `Command(goto=..., update=...)` to orchestrator. |

## FR14 coverage

FR14 requires programmatic validation of specialist scaffold conformance. This
framework satisfies FR14's substrate claim at Slab 1 close; per-specialist
assertion happens at each Slab 2 migration story. Until specialists register,
running `pytest tests/integration/scaffold_conformance/` exercises the
framework-itself tests + the validator's accept/reject/diagnostic behavior.

## How to extend

The framework is intentionally minimal — a single frozenset of node ids plus a
structural-type `validate_scaffold()` function. If Slab 2 surfaces a need for
richer checks (node signature validation, state-flow contract, reducer-field
discipline), extend `scaffold_contract.py` in a dedicated story; party-mode
amendment required because downstream per-specialist tests bind to this
surface.

## Related

- Story 1.7 AC-1.7-D (this framework's anchor)
- Architecture §Specialist Scaffold (Slab 2 decomposition canonical spec)
- PRD FR14 (scaffold conformance requirement)
- Slab 2 Story 2a.1 (first specialist to register)
