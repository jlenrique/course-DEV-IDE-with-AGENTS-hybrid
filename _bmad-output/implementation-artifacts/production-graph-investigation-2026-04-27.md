# Production Graph Investigation - 2026-04-27

## Verdict

**Recommended path:** Path (c) - HALT. Substantial production orchestration code is missing. Do not wire `python -m app.marcus.cli trial start` to claim production clone-launch evidence on the current substrate.

The branch has an honest registration shim and several reusable substrate pieces, but it does not expose a callable live production-graph entry point that composes the migrated graph, invokes real specialists, honors HIL gates as pauses, uploads LangSmith trace data, and writes cost evidence for a live OpenAI trial.

## Entry Points Found

| Surface | Finding |
|---|---|
| `app/marcus/facade.py` | Compatibility wrapper over `marcus.facade`; exports `Facade`, `get_facade`, and `reset_facade`. No `run_production_trial(...)` or equivalent live trial runner. |
| `app/marcus/orchestrator/supervisor.py` | Compatibility wrapper over `marcus.orchestrator.supervisor`; no production graph launch surface. |
| `app/marcus/orchestrator/routing.py` | Compatibility wrapper over root routing helper; no live graph launch surface. |
| `app/marcus/orchestrator/write_api.py` | Local append-event helper only. |
| `app/marcus/orchestrator/__init__.py` | Re-exports wrappers and write helper only. |
| `app/marcus/intake.py` | Pre-packet snapshot helper; no trial runner. |
| `app/marcus/dispatch/contract.py` | Alias to root dispatch contract models; no invocation surface. |
| `app/marcus/cli/trial.py` | Current CLI shim calls `marcus.orchestrator.m3_trial.run_local_m3_trial(...)`; it preserves honest evidence flags but does not launch a live production graph. |
| `marcus/orchestrator/m3_trial.py` | Deterministic local M3 harness; valid replay/control-plane substrate, but not a live OpenAI production graph runner. |

## Graph And Manifest Findings

| Artifact | Finding |
|---|---|
| `state/config/pipeline-manifest.yaml` | Full 33-step v4.2 manifest exists, but comments and data still describe Slab 1 manifest compilation via scaffold/passthrough behavior. All production-relevant nodes inspected have `model_config_ref: null`. |
| `app/manifest/compiler.py` | Compiler explicitly adds `_passthrough_node(...)` for each manifest node. The module docstring says real specialist resolution is future/full resolution, but the current implementation still compiles passthrough handlers rather than dispatch-registry specialists. |
| `app/manifest/lanes.py` | `compile_run_graph(...)` loads and compiles the manifest, but it delegates to the passthrough compiler. It returns an invokable graph, not a production-specialist graph. |
| `runtime/graphs/v42/` | Contains `compiled-graph-digest.txt`, manifest snapshots, dispatch-registry snapshot, and pack version metadata. It does not contain a serialized invokable graph or loader that can restore a production compiled graph. |
| `state/config/dispatch-registry.yaml` and `runtime/graphs/v42/dispatch-registry-snapshot.yaml` | Production-promoted specialist-to-builder mappings exist, but the manifest compiler does not consume them. |

## Specialist And Cost Substrate Findings

| Substrate | Finding |
|---|---|
| `app/specialists/<name>/graph.py` | Many specialists expose LangGraph builders and call `app.models.adapter.make_chat_model(...)`, which routes through real OpenAI model IDs when invoked. These are reusable pieces, not a composed production runner. |
| `app/models/adapter.py` | Live OpenAI invocation path exists at the specialist-node level when `OPENAI_API_KEY` is set. |
| `runtime/config/model_cascade.yaml` | Real OpenAI model IDs are present and usable for cost attribution and adapter routing. |
| `app/runtime/economics.py` | LangSmith trace reading and cost-report persistence exist. They require an actual trace with billable spans; they do not themselves launch a trial. |

## Gap

The missing component is a production trial runner that integrates these pieces:

1. Reads `state/config/pipeline-manifest.yaml`.
2. Resolves manifest nodes to dispatch-registry specialist graph builders rather than passthrough handlers.
3. Bridges specialist subgraph inputs/outputs to the shared `RunState` contract.
4. Treats HIL gate nodes as real pauses awaiting `OperatorVerdict` via the existing FR34 resume API instead of auto-verdicting.
5. Wraps the trial in LangSmith trace context with `trial_id` metadata so `measure_trial_cost(...)` can find the trace.
6. Persists the run registry and cost artifacts with `production_clone_launch_evidence=true` only after a real production graph invocation completes.

Building that runner is not a small wiring change. It is new orchestration integration across manifest compilation, dispatch-registry resolution, gate suspension/resume semantics, LangSmith trace scoping, and trial lifecycle persistence.

## Disposition

HALT at Phase A. Leave M5 condition #3 open.

New deferred-inventory entry filed: `5a-2-production-graph-entrypoint-substrate-gap`.

Recommended follow-on: authorize a dedicated production-graph-runner dispatch or story with explicit scope for:

- Replacing manifest compiler passthrough resolution with dispatch-registry-backed specialist invocation for the run lane.
- Defining the production `TrialEnvelope` or equivalent run registry schema distinct from the deterministic M3 harness envelope.
- Implementing HIL gate pause/resume instead of deterministic auto-verdicts.
- Binding LangSmith root trace metadata to `trial_id`.
- Adding non-live and live-gated tests for trial launch evidence without fabricating production completion.

Until that lands, `app.marcus.cli trial start --preset production --input <corpus-path>` must continue to avoid claiming production clone-launch equivalence.
