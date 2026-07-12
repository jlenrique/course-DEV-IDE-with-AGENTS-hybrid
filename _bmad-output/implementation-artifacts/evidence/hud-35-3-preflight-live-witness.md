# Story 35.3 — L3 Live Pre-flight Witness

Banked 2026-07-12. Ran `run_preflight(...)` **standalone** against LIVE services
with real operator keys loaded via `scripts.utilities.env_loader.load_env()`.
NFR5 honored — no mocks: the OpenAI and Gamma items are real network calls.
**No paid specialist walk was started** (`run_preflight` invoked directly; the
SPOC walk / `run_production_trial` was NOT run), so this witness costs only the
two cheap heartbeat pings.

## Invocation

```
OperatorSurfaceAssembler(trial_id, runs_root).emit(<registered stub envelope>)
run_preflight(trial_id, runs_root, PreflightDeps(env=os.environ))
```

Key presence at run time: `OPENAI_API_KEY`, `LANGSMITH_API_KEY`,
`LANGSMITH_PROJECT`, `GAMMA_API_KEY` all present.

## Result — all_green = TRUE

| # | item | phase | state | latency_ms | quota_confidence | output |
| - | ---- | ----- | ----- | ---------- | ---------------- | ------ |
| 1 | env-keys-present | 01 | pass | — | — | OPENAI_API_KEY + LANGSMITH_API_KEY present |
| 2 | runs-root-writable | 01 | pass | — | — | (temp runs root) |
| 3 | coordination-db-readable | 01 (soft) | pass | — | — | state/runtime/coordination.db |
| 4 | litellm-importable | 01 | pass | — | — | import ok |
| 5 | cascade-config-validates | 01 | pass | — | — | cascade + pricing validated |
| 6 | **openai** | 02 (LIVE) | pass | **1375.0** | unknown | GET /v1/models 200 (no rate-limit headers) |
| 7 | **gamma** | 02 (LIVE) | pass | **234.0** | proxy | list_themes 200 (1 theme reachable) |
| 8 | langsmith | 02 (env-presence) | pass | — | — | LANGSMITH_API_KEY present (project=course-content-production) |

### Notes / honest readings
- **openai** confidence = `unknown`: the `GET /v1/models` response carried no
  `x-ratelimit-remaining-*` header on this call, so no quota proxy was
  available. Never-false-green holds: `unknown` confidence never renders a green
  quota reading (the *item* is a reachability pass, not a quota claim).
- **gamma** confidence = `proxy`: `list_themes` proved auth + reachability but
  exposes no credit balance, so the reading is a proxy, not a `direct` credit
  count (matches AD-11 addendum §C — Gamma credits piggyback generation polls,
  not the themes list).
- **langsmith** = env-presence only per greenlight amendment 10 (v1 heartbeat
  set = OpenAI + Gamma + LangSmith-env-presence).

### Full-trial start-to-spawn-gate L3
A full `trial start` → SPOC-spawn-gate L3 (server child up + healthz identity
item live) is **deferred to the Story 35.7 E2E witness run**: driving it here
would spend a real specialist walk (paid), which this story is explicitly told
not to start. The pre-flight function — the load-bearing new surface — is proven
live above; the healthz identity item is proven hermetically
(`test_start_path_sequence.py::test_gate_launches_server_before_running_preflight`
and `test_preflight.py::test_healthz_*`, including wrong-server-on-port).
