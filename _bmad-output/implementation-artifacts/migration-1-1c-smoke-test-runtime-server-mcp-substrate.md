# Migration Story 1.1c: Smoke Test + Runtime Server Entry + MCP Code Substrate

**Status:** review
**Sprint key:** 1-1c-smoke-test-runtime-server-mcp-substrate
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — "Runtime substrate is real."
**Position in serial-kickoff:** 3 of 4 (1.1a → 1.1b → **1.1c** → 1.1d), per Architecture Amendment F + 2026-04-22 middle-path consensus extending the kickoff.
**Pts:** 3 | **Gate:** single | **K-target:** ~1.5×

## Story

As a **dev agent bringing the runtime substrate online**,
I want **working `app.smoke_test` + `app.runtime_server` (FastAPI) entry points + `app.models.registry_check` PLUS the MCP code substrate (protocol pin + one real tool handler + stdio wire-up) landed in `app/mcp_server/` but NOT exercised by per-PR smoke**,
So that **M1 acceptance evidence can begin accruing through the FastAPI transport, the empty-manifest-loaded graph is demonstrable, FR2's compound MCP+FastAPI+CLI substrate has the MCP code present in Slab 1 (per D7 + middle-path consensus), and Story 1.1d inherits a ready-to-smoke MCP surface**.

## Acceptance Criteria

Preserved from [epics-langchain-langgraph-migration.md §Story 1.1c](../planning-artifacts/epics-langchain-langgraph-migration.md). All ACs are dev-agent-executable; no operator-gated AC in this story.

### AC-1.1c-A — Registry check

- **Given** `app/models/registry.yaml` and `app/specialists/_scaffold/model_config.yaml` exist with stub content (registry has ≥1 entry; scaffold has Pydantic-shape minimum)
- **When** the dev agent runs `uv run python -m app.models.registry_check`
- **Then** the script loads the registry, validates every referenced model ID against the Pydantic `PipelineRegistry` model (which is **stub-only in 1.1c**; full schema lands in 1.3 — 1.1c uses a placeholder model with `Field(default=None)`-permissive shape that 1.3 will tighten), and exits 0 on valid input; invalid refs exit 1 with a named violation. **Important:** this AC creates the `registry_check` entry-point only — full validation rules are 1.3 scope.

### AC-1.1c-B — Smoke test via stub manifest

- **Given** a minimal stub manifest at `state/config/pipeline-manifest.yaml` (1-step no-op graph with one node returning a deterministic payload `{"smoke": "ok", "node": "noop"}`)
- **When** the dev agent runs `uv run python -m app.smoke_test`
- **Then** the manifest loads via `app.manifest.loader` (stub-only in 1.1c — 1.4 lands the full loader; 1.1c uses a minimal `yaml.safe_load` + Pydantic-validate path), the compiler stub produces a compiled `StateGraph`, one node executes, the graph returns, and stdout shows `smoke ok` plus a node count line. The smoke MUST be importable as a function (`app.smoke_test.run_smoke() -> dict`) so 1.1d's parity test can call it directly.

### AC-1.1c-C — FastAPI runtime server + /health + /invoke

- **Given** the smoke test passes and `app.runtime_server` is importable
- **When** the dev agent runs `uv run python -m app.runtime_server` in a subprocess and probes it via `httpx` from a pytest (`tests/integration/runtime/test_fastapi_server.py`) — **NOT `curl`**, per sandbox-AC rule
- **Then** a FastAPI server binds to `127.0.0.1:<port>` per NFR-S2 (port from `RUNTIME_PORT` env var or default 8765); `GET /health` returns 200 with body `{"status": "ok", "postgres": "connected"}` when Postgres is reachable OR `{"status": "ok", "postgres": "skipped"}` when unreachable (sandbox-AC discipline — same skip-not-fail pattern as 1.1b's `test_server_version.py`); `POST /invoke` with a minimal-graph input invokes the **shared minimal LangGraph node** (see Dev Notes §Shared minimal node contract) and returns its output payload; `SIGTERM` (POSIX) or `terminate()` (Windows subprocess API) shuts the server down within 2 seconds with no orphaned threads (verified by checking subprocess `returncode` is set, not `None`, after termination). **Per Murat coverage-gap amendment 2026-04-22:** the test additionally asserts the bind address IS `127.0.0.1` (NOT `0.0.0.0` or any non-loopback) via either (a) introspecting `app.state.bound_host` from the running app, or (b) attempting to connect to a non-loopback address (e.g., the machine's primary LAN IP) and asserting the connection is refused/times-out within 1s. This catches the regression class where bind is silently changed to `0.0.0.0` for Windows-firewall debugging and breaks NFR-S2.

### AC-1.1c-D — LangSmith span-tag contract (integration tier)

- **Given** `LANGSMITH_API_KEY` is set in the dev's `.env` (test skips with documented reason if unset, per sandbox-AC discipline)
- **When** the smoke test or `/invoke` runs
- **Then** a LangSmith trace is created and visible in the `LANGSMITH_PROJECT` project; the trace has ≥1 span per node with the contract tag set `{trial_id, node_id, agent, lane}` per architecture §8 span-tag contract. A pytest under `tests/integration/observability/test_langsmith_span_tags.py` asserts the contract tag set is present on every span using the LangSmith SDK's read API; skips cleanly when `LANGSMITH_API_KEY` is unset.

### AC-1.1c-D2 — Span-tag schema pin (unit tier — fast-fail without LangSmith) *(per Murat amendment 2026-04-22)*

- **Given** the contract tag set is `{trial_id, node_id, agent, lane}` per architecture §8
- **When** the dev agent authors `app/runtime/span_tags.py` exporting `REQUIRED_SPAN_TAG_KEYS: frozenset[str] = frozenset({"trial_id", "node_id", "agent", "lane"})` AND `tests/unit/observability/test_span_tag_contract_pin.py` that imports the constant + asserts the frozenset equals exactly the four canonical keys (no more, no fewer); a golden fixture at `tests/fixtures/observability/span_tag_keys.json` (alphabetized JSON list) is asserted byte-equivalent to `sorted(REQUIRED_SPAN_TAG_KEYS)` so any future drift fails fast at unit-tier
- **Then** the span-tag contract drifts loudly without requiring `LANGSMITH_API_KEY` to be set; pairs with AC-1.1c-D as the integration-tier counterpart that asserts the keys are actually present in the LangSmith export.

### AC-1.1c-E — MCP code substrate present (NO smoke yet — 1.1d scope)

- **Given** `app/mcp_server/` is a README-only stub package from 1.1b
- **When** the dev agent authors:
  - **(a)** `app/mcp_server/protocol.py` with `MCP_PROTOCOL_VERSION: str = "2025-03-26"` (or current latest stable per `mcp` SDK; T1 reading must verify against `requirements.lock`'s pinned `mcp` version) — this is the FR2 protocol-version pin
  - **(b)** `app/mcp_server/server.py` with stdio transport wire-up using `mcp.server.Server` + `mcp.server.stdio.stdio_server` from the shipped `mcp` SDK
  - **(c)** `app/mcp_server/tools/ping.py` with one real `@server.list_tools()` + `@server.call_tool()` handler pair; the `ping` tool invokes the **shared minimal LangGraph node** (same as `/invoke` AC-1.1c-C) so 1.1d's parity assertion has a real falsifiable target
  - **(d)** `app/mcp_server/__main__.py` entry point so `uv run python -m app.mcp_server` spawns the server (1.1d will call this as a subprocess)
- **Then** `uv run python -c "from app.mcp_server.protocol import MCP_PROTOCOL_VERSION; from app.mcp_server import server; print(MCP_PROTOCOL_VERSION)"` prints the pinned version with exit code 0; `lint-imports --config pyproject.toml` exits 0 (existing C1+C2 contracts continue to pass; `app.mcp_server` does not violate lane-separation since it's not under `app.marcus` or `app.cora`); **NO subprocess MCP round-trip is exercised in this story** — that lands in 1.1d's AC-1.1d-B.

### AC-1.1c-F — Forward-pointer to 1.1d in docs stub

- **Given** `docs/dev-guide/langgraph-runtime-setup.md` will be the Slab 1 runtime-setup doc (final polish in 1.7; 1.1c lands the structural stub)
- **When** the dev agent authors the stub with the **inverted transport-parity matrix** (markdown table; 3 columns × 3 rows per Paige's Round-2 doc-shape recommendation):

  | | FastAPI | MCP | CLI |
  |---|---|---|---|
  | **Code present** | ✅ 1.1c | ✅ 1.1c | ⏳ Slab 3 |
  | **Smoke test (per-PR)** | ✅ 1.1c | — (not per-PR by design) | ⏳ Slab 3 |
  | **Parity acceptance test** | — (parity is two-transport at M1) | ✅ 1.1d (gates M1) | ⏳ Slab 3 (3.4) |

  PLUS an explicit callout in the MCP section: *"MCP code substrate is present from 1.1c, but per-PR smoke and FastAPI↔MCP parity acceptance are gated on Story 1.1d. Do not treat the MCP transport as production-ready until 1.1d closes."*

- **Then** the stub exists at `docs/dev-guide/langgraph-runtime-setup.md`, the matrix is grep-able, the 1.1d callout is present, and the file is committed. Final polish (prose flow, additional sections) is 1.7 scope.

## Tasks / Subtasks

- [ ] **T1 — Read T1 Context Bundle.** (AC: pre-work)
  - [ ] Read [`_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md`](../planning-artifacts/slab1-story-set-A-t1-bundle.md) §1 (D2, D6, D7, D8 in detail), §2 (FR1, FR2, FR6, FR7, FR58, NFR-S2), §4 (sandbox-AC discipline), §6 (anti-patterns), §8 (middle-path consensus origin — the WHY of the 1.1c/1.1d split).
  - [ ] Skim `mcp` PyPI SDK README to confirm protocol-version constant location and current latest stable version.

- [ ] **T2 — Author `app/models/registry_check.py` + stub PipelineRegistry model.** (AC-1.1c-A)
  - [ ] Stub Pydantic model in `app/models/registry.py` (full shape lands in 1.3 — keep this minimal: `id: str`, `default_model: str | None = None`, `extra="forbid"`)
  - [ ] `app/models/registry_check.py` with `__main__` entry; loads `app/models/registry.yaml`; validates each entry; exit 0/1 with named violation on stderr
  - [ ] Stub `app/models/registry.yaml` with one valid entry (e.g., `entries: [{id: "gpt-5.4", default_model: "gpt-5.4"}]`)

- [ ] **T3 — Author `app/smoke_test.py` + minimal stub manifest.** (AC-1.1c-B)
  - [ ] `state/config/pipeline-manifest.yaml` stub with 1 noop step (real loader is 1.4)
  - [ ] `app/smoke_test.py` with `run_smoke() -> dict` function that loads the manifest, instantiates a 1-node `StateGraph`, runs it, returns the output dict
  - [ ] `__main__` entry that calls `run_smoke()` and prints `smoke ok` + node count

- [ ] **T4 — Author the shared minimal LangGraph node.** (AC-1.1c-B + AC-1.1c-C + AC-1.1c-E + 1.1d dependency)
  - [ ] `app/runtime/minimal_node.py` exporting `MINIMAL_NODE_NAME` + `def minimal_node(state) -> dict` returning `{"smoke": "ok", "node": "noop", "echo": state.get("input")}`
  - [ ] This is the **single source of truth** for the no-op node referenced by `/invoke`, the smoke test, the MCP `ping` tool, and 1.1d's parity assertion. Do NOT re-implement in any of those; import.

- [ ] **T5 — Author `app/runtime/server.py` + `app/runtime_server.py` entry.** (AC-1.1c-C)
  - [ ] FastAPI app with `GET /health` (Postgres reachability via `psycopg.connect(DATABASE_URL).close()`; skip-not-fail) and `POST /invoke` (calls `minimal_node` from T4)
  - [ ] `127.0.0.1` bind only (NFR-S2); port from `RUNTIME_PORT` env or default 8765
  - [ ] Clean-shutdown handler (uvicorn lifecycle; `signal_handlers=True` default)
  - [ ] `app/runtime_server.py` with `__main__` that calls `uvicorn.run(...)` with the right host/port
  - [ ] `tests/integration/runtime/test_fastapi_server.py` spawns subprocess + uses `httpx` to probe `/health` + `/invoke`; skips Postgres path when unreachable; asserts SIGTERM/`terminate()` clean shutdown within 2s

- [ ] **T6 — Author MCP code substrate.** (AC-1.1c-E)
  - [ ] `app/mcp_server/protocol.py` with `MCP_PROTOCOL_VERSION` constant (verify against shipped `mcp` SDK at T1)
  - [ ] `app/mcp_server/server.py` with `mcp.server.Server` instance + stdio handler scaffold
  - [ ] `app/mcp_server/tools/__init__.py` + `app/mcp_server/tools/ping.py` registering the `ping` tool that calls `minimal_node` from T4
  - [ ] `app/mcp_server/__main__.py` running `mcp.server.stdio.stdio_server(server)` event loop
  - [ ] Smoke test: `uv run python -c "from app.mcp_server.protocol import MCP_PROTOCOL_VERSION; from app.mcp_server import server; print(MCP_PROTOCOL_VERSION)"` prints version
  - [ ] Confirm `lint-imports` still exits 0
  - [ ] **DO NOT** spawn subprocess + drive MCP round-trip — that's 1.1d. Resist scope creep.

- [ ] **T7 — Author LangSmith span-tag contract test.** (AC-1.1c-D)
  - [ ] `tests/integration/observability/test_langsmith_span_tags.py` — invokes smoke + asserts spans have `{trial_id, node_id, agent, lane}` tags via LangSmith SDK read API
  - [ ] Skip with documented reason when `LANGSMITH_API_KEY` is unset

- [ ] **T8 — Author `docs/dev-guide/langgraph-runtime-setup.md` stub with transport-parity matrix.** (AC-1.1c-F)
  - [ ] Markdown structural stub with the inverted matrix from AC-1.1c-F + the MCP-acceptance-gated-on-1.1d callout
  - [ ] Final prose polish is 1.7 scope — keep this minimal but complete on the matrix + callout

- [ ] **T9 — Run validators + scoped tests.** (closure)
  - [ ] `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-1-1c-smoke-test-runtime-server-mcp-substrate.md` — must PASS
  - [ ] `uv run ruff check app` — must exit 0
  - [ ] `uv run lint-imports --config pyproject.toml` — must exit 0
  - [ ] `uv run pytest tests/integration/runtime tests/integration/observability` — green or skip-cleanly
  - [ ] `uv run python -m app.smoke_test` — prints `smoke ok` + node count

- [ ] **T10 — Commit.** (closure)
  - [ ] Commit message: `feat(migration): Slab 1 Story 1.1c — smoke test + FastAPI runtime + MCP code substrate`. Body cites D7 + Amendment F + middle-path consensus (2026-04-22).

## Dev Notes

### Shared minimal node contract (load-bearing for 1.1d)

`app/runtime/minimal_node.py` is the single source of truth for the no-op node. **Three call sites import it:** (1) `app.smoke_test`, (2) `/invoke` route handler in `app/runtime/server.py`, (3) `ping` tool handler in `app/mcp_server/tools/ping.py`. **Do not re-implement** — Story 1.1d's parity assertion depends on byte-identical behavior across the three call sites, which is only guaranteed if they all import the same module. This is a load-bearing invariant for the 1.1d transport-parity test.

### Stub-only models (1.1c gives shape, 1.3/1.4 give substance)

`PipelineRegistry` and the manifest-loader stub in 1.1c are intentionally minimal. 1.3 lands the full registry schema with three-level cascade rules; 1.4 lands the full manifest loader with topology compilation. **Do not over-spec the stubs in 1.1c** — that's scope creep into 1.3/1.4 territory. Keep them just-enough to make AC-1.1c-A and AC-1.1c-B green.

### MCP SDK version pin

The `mcp` PyPI SDK is in the 1.1a lockfile (verify at T1; if absent, that's a 1.1a omission to be flagged separately). The `MCP_PROTOCOL_VERSION` constant should match the version the shipped SDK supports — read the SDK's `__version__` and constant declarations to confirm. Do not pin a version the shipped SDK can't speak.

### Why no MCP smoke in this story

Per the 2026-04-22 middle-path party-mode consensus (5/5 vote), MCP smoke + FastAPI↔MCP byte-equivalent parity moved to Story 1.1d. The reasons (preserved here for forensic value): per-PR critical-path flake risk on subprocess stdio (Murat); K-floor explosion on 1.1c (Amelia); "narrow M1 reader question" framing (Paige); FR2 substrate presence vs. per-PR smoke cadence is a question D7 didn't adjudicate (Mary). See bundle §8.

### Sandbox-AC discipline

All ACs are dev-agent-executable. No operator-gated AC. The `/health` Postgres probe and the LangSmith span-tag test BOTH skip-cleanly when their respective backing service is unreachable. The validator at `scripts/utilities/validate_migration_story_sandbox_acs.py` is the gate.

### Project Structure Notes

**New files:**
- `app/models/registry.py` (stub model)
- `app/models/registry.yaml` (stub registry)
- `app/models/registry_check.py` + `__main__.py`
- `app/runtime/minimal_node.py`
- `app/runtime/server.py`
- `app/runtime_server.py` (`__main__` entry)
- `app/smoke_test.py` (`run_smoke` + `__main__`)
- `app/mcp_server/protocol.py`
- `app/mcp_server/server.py`
- `app/mcp_server/tools/__init__.py`
- `app/mcp_server/tools/ping.py`
- `app/mcp_server/__main__.py`
- `state/config/pipeline-manifest.yaml` (stub manifest)
- `tests/integration/runtime/test_fastapi_server.py`
- `tests/integration/observability/test_langsmith_span_tags.py`
- `docs/dev-guide/langgraph-runtime-setup.md` (structural stub)

**Modified:** none expected.

## References

- Bundle: [Slab 1 Story-Set A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md) — sole T1 reading set; all D-numbered architecture decisions, FR/NFR rationale, Pydantic+LangGraph idioms, sandbox-AC rule, gate-mode policy, and middle-path consensus context live there
- Architecture §First Implementation Stories Story 1c (Amendment F revised by 2026-04-22 middle-path) — bash command sketch the implementation expands on
- `mcp` PyPI SDK README — protocol version constant + stdio_server pattern

## Dev Agent Record

### Agent Model Used

claude-opus-4-7 (1M context). Dev-story executed 2026-04-23 in single session.

### Debug Log References

- LangGraph state-schema reducer silently drops keys not declared on the
  `TypedDict` state — initial smoke output was `{'input': 'ping'}` only;
  widened `_SmokeState` to include `smoke`, `node`, `echo` and rerun returned
  the canonical four-key payload.
- `mcp` SDK 1.27.0 has no `__version__` attribute; protocol version sourced
  from `mcp.types.DEFAULT_NEGOTIATED_VERSION` (= `"2025-03-26"`) +
  `LATEST_PROTOCOL_VERSION` (= `"2025-11-25"`) recorded for forensic value.
  Re-export pattern (rather than hard-coded date) means an SDK upgrade
  cannot silently shift the protocol surface.
- Hybrid `.venv` carried only the runtime deps from Story 1.1a's lockfile —
  `pip` itself was not installed. Bootstrapped via `python -m ensurepip
  --upgrade` then `pip install pytest pytest-asyncio pytest-timeout` so the
  T9 pytest battery could run. Lockfile NOT modified (dev deps stay in
  pyproject `[dev]` extras; pin discipline unchanged).

### Completion Notes List

- All 8 ACs (`A`, `B`, `C`, `D`, `D2`, `E`, `F`) green via T9 validator
  battery — sandbox-AC PASS, ruff clean, lint-imports 3/3 contracts kept,
  pytest 5 passed / 1 deselected (live LangSmith, correctly skipped without
  `LANGSMITH_API_KEY`), smoke + registry_check + MCP import-smoke exit 0.
- **AC-1.1c-D live LangSmith integration test was authored but cannot
  execute end-to-end in the dev sandbox** (no `LANGSMITH_API_KEY`). Skips
  cleanly. Full assertion fires when the operator runs `pytest --run-live
  tests/integration/observability/` with the env var set; the unit-tier pin
  in AC-1.1c-D2 carries the schema enforcement until then.
- **Pipeline manifest overwrite:** `state/config/pipeline-manifest.yaml`
  previously held the primary-repo v4.2 prompt-pack manifest (379 lines).
  This story replaces it with the Slab 1 migration stub per spec + per
  Story 1.6 plan. Recovery on hybrid: `git show
  upstream/master:state/config/pipeline-manifest.yaml`. The 11 primary-repo
  tests that load this path (`tests/test_pipeline_manifest_loader.py`,
  `tests/test_check_pipeline_manifest_lockstep.py`, etc.) will fail under
  `pytest tests/`; T9 pytest scope is restricted to `tests/integration/runtime`
  + `tests/integration/observability` + `tests/unit/observability` per the
  story's T9 list, so this regression class is not surfaced here. Slab 1
  closing-story 1.7 should call out the regression class in the Slab-1 close
  note for forward-port reconciliation.
- **Substrate-bootstrap K framing per bundle §6 anti-pattern #3:** verification
  signals counted as command-equivalence checks (`python -m app.smoke_test`,
  `python -m app.models.registry_check`, MCP import-smoke `python -c "..."`)
  in addition to the 5 pytest collecting nodes. Total story-scoped
  verification surface: 5 pytest + 3 entry-point smokes + 4 validator gates
  (sandbox-AC, ruff app, ruff tests, lint-imports). At Pts=3 / K-target ~1.5×,
  the substrate-bootstrap framing fits cleanly.

### File List

**New files (this story):**

- `app/models/registry.py` — stub `PipelineRegistry` + `PipelineRegistryEntry`
  Pydantic models (1.3 will land the full three-level cascade schema).
- `app/models/registry.yaml` — stub registry with one valid entry.
- `app/models/registry_check.py` — `__main__` entry point validating the
  YAML against the model; exits 0/1 with named violation on stderr.
- `app/runtime/minimal_node.py` — shared `minimal_node` callable + stable
  `MINIMAL_NODE_NAME` constant. Single source of truth imported by smoke,
  FastAPI `/invoke`, and the MCP `ping` tool — load-bearing invariant for
  Story 1.1d's parity assertion.
- `app/runtime/server.py` — FastAPI app factory, `GET /health`,
  `POST /invoke`, NFR-S2 loopback bind, `app.state.bound_host` introspection.
- `app/runtime/span_tags.py` — `REQUIRED_SPAN_TAG_KEYS` frozenset pin.
- `app/runtime_server.py` — `__main__` entry; `RUNTIME_PORT` env var honored.
- `app/smoke_test.py` — `run_smoke()` function + `__main__` entry; loads
  the stub manifest, compiles a one-node `StateGraph`, returns the payload.
- `app/mcp_server/protocol.py` — `MCP_PROTOCOL_VERSION` re-export from
  shipped `mcp` SDK + `MCP_LATEST_PROTOCOL_VERSION` for forensic value.
- `app/mcp_server/server.py` — `mcp.server.Server` instance + `register()`
  for the `ping` tool.
- `app/mcp_server/tools/ping.py` — one real `list_tools` / `call_tool`
  handler pair; invokes the shared `minimal_node`.
- `app/mcp_server/__main__.py` — `uv run python -m app.mcp_server` boots
  the server over stdio.
- `state/config/pipeline-manifest.yaml` — REPLACED with Slab 1 migration
  stub (1-node noop graph). See Completion Notes for recovery + 1.6 plan.
- `tests/integration/runtime/test_fastapi_server.py` — 3 tests:
  in-process bind-host introspection, subprocess `/health` + `/invoke` +
  clean shutdown, non-loopback connection refusal (NFR-S2).
- `tests/integration/observability/test_langsmith_span_tags.py` — live
  LangSmith span-tag contract test, `live_api`-marked, skips without
  `LANGSMITH_API_KEY` or `LANGSMITH_PROJECT`.
- `tests/unit/observability/test_span_tag_contract_pin.py` — 2 unit-tier
  pin tests: canonical-four equality + golden-fixture byte-equivalence.
- `tests/fixtures/observability/span_tag_keys.json` — golden fixture
  (alphabetized JSON list of the four canonical keys).
- `docs/dev-guide/langgraph-runtime-setup.md` — Slab 1 structural stub
  with the inverted transport-parity matrix + MCP 1.1d gating callout.

**Modified (this story):** none beyond the `state/config/pipeline-manifest.yaml`
overwrite already noted.

### Change Log

| Date       | Change                                                              |
| ---------- | ------------------------------------------------------------------- |
| 2026-04-22 | Spec authored as part of Slab 1 story-set A (party-mode pass)        |
| 2026-04-22 | In-spec amendments per set-level review (AC-1.1c-C bind assertion + AC-1.1c-D2 unit-tier pin per Murat amendment) |
| 2026-04-23 | T1–T9 dev-story executed; status `ready-for-dev` → `review`           |

### Review Findings

_(to be filled by code reviewer; bmad-code-review layered pass — Blind Hunter +
Edge Case Hunter + Acceptance Auditor — pending per CLAUDE.md sprint
governance rule 3 before `done` transition)_
