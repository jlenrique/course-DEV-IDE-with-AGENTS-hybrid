# CI Lane: `transport_parity` (skeleton)

**Status:** placeholder lane documentation, Slab 1 Story 1.1d AC-1.1d-D. Full CI wiring lands in **Slab 4 Story 4.1** (graph-compile-time hook). This file documents the intent + reopen-trigger so the future CI author has the contract.

## Intent

Run `pytest -m transport_parity` on a **nightly / on-merge** cadence — explicitly NOT per-PR. Per the 2026-04-22 middle-path consensus on MCP-in-Slab-1 (5/5 vote), MCP subprocess + FastAPI↔MCP parity tests carry per-PR-flake risk that does not belong on the Slab 1 critical path. The per-PR Slab 1 smoke (FastAPI-only, from Story 1.1c) stays narrow.

## Tests covered

- `tests/integration/transport_parity/test_mcp_stdio_smoke.py` — MCP stdio subprocess smoke (initialize / list_tools / call_tool round-trip).
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py` — FastAPI↔MCP byte-equivalent residual parity.

## Cadence

| Trigger                 | Run? | Rationale                                                                  |
| ----------------------- | ---- | -------------------------------------------------------------------------- |
| Per-PR push             | NO   | Subprocess + stdio carries per-PR-flake risk (Murat Round-2 concern).      |
| Merge to main / dev/*   | YES  | Catches regressions before they propagate.                                 |
| Nightly scheduled run   | YES  | Catches environment drift (SDK upgrades, OS subprocess behavior shifts).   |
| Manual operator trigger | YES  | Allows on-demand evidence collection for M1 acceptance pack.               |

## Reopen-trigger (from AC-1.1d-D)

> If the subprocess smoke or parity test flakes >2% across its first 20 runs, reopen the MCP-in-Slab-1 deferral conversation per the 2026-04-22 middle-path consensus contingency.

The flake percentage is computed across the first 20 cumulative runs (whether nightly + on-merge mixed). The dev agent records the per-run pass/fail in Story 1.1d's Completion Notes; the CI author wires the equivalent telemetry when this skeleton becomes a real workflow.

**Do NOT silently retry-loop the test until it passes.** Flakiness here is diagnostic data about whether MCP-in-Slab-1 was the right call. If the budget is breached, convene party-mode to re-evaluate (see [bundle §8](../_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md)).

## Slab 4 wire-up checklist (for the future CI author)

When Story 4.1 lands the graph-compile-time CI hook:

1. Add a workflow trigger for `schedule:` (cron, nightly) and `push: branches: [main, dev/*]`.
2. Run `pytest -m transport_parity tests/integration/transport_parity` against a fresh venv built from `requirements.lock`.
3. Capture per-run pass/fail to a structured artifact (JSON or YAML) for trend tracking.
4. If any 20-run rolling window shows >2% flake, post to the team channel + open a "reopen MCP-in-Slab-1" ticket; do NOT auto-disable the lane.
5. The lane is NOT a blocking gate for per-PR merges — it's a milestone-level signal.
