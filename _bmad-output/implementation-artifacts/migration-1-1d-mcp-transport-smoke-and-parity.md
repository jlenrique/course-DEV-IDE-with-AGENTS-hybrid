# Migration Story 1.1d: MCP Transport Smoke + Two-Transport Parity

**Status:** done
**Sprint key:** 1-1d-mcp-transport-smoke-and-parity
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — gates the FR2 compound-contract claim at M1 acceptance.
**Position in serial-kickoff:** 4 of 4 (1.1a → 1.1b → 1.1c → **1.1d**), per 2026-04-22 middle-path consensus extending Architecture Amendment F.
**Pts:** 3 | **Gate:** single | **K-target:** ~1.5× (floor 1.2, ceiling 1.8)
**Origin:** NEW story added 2026-04-22 via party-mode standing-team consensus on MCP-in-Slab-1 (5/5 MIDDLE PATH vote). See [bundle §8](../planning-artifacts/slab1-story-set-A-t1-bundle.md) for the consensus chain.

## Story

As a **dev agent closing the FR2 compound-contract evidence at M1 acceptance**,
I want **a dedicated MCP stdio subprocess smoke test + a FastAPI↔MCP byte-equivalent parity assertion that runs nightly / on-merge (NOT per-PR) against the same minimal LangGraph node Story 1.1c wires to both transports**,
So that **the MCP transport is proven substrate at M1 without putting subprocess-stdio flake vectors on every Slab 1 PR's critical path (Murat's Round-2 concern), the D7 three-transport parity claim is falsifiable not aspirational (Winston/Mary), and Slab 3 Story 3.4's three-transport verdict parity inherits a pre-proven two-transport baseline**.

## Acceptance Criteria

All ACs are dev-agent-executable. No operator-gated AC.

### AC-1.1d-A — Shared-fixture contract

- **Given** Story 1.1c shipped `app/runtime/minimal_node.py` exporting `MINIMAL_NODE_NAME` + `minimal_node()`, wired identically to FastAPI `/invoke` AND the MCP `ping` tool
- **When** the dev agent authors `tests/integration/transport_parity/conftest.py` with a fixture `minimal_node_fixture` that imports the literal same `app.runtime.minimal_node` module (NOT a re-implementation)
- **Then** the fixture exists; the conftest module-imports `minimal_node` directly; any future drift between transports is caught by the import boundary, not test-site duplication; the conftest is referenced by both AC-1.1d-B and AC-1.1d-C tests.

### AC-1.1d-B — MCP stdio subprocess smoke

- **Given** the shipped `mcp` PyPI SDK in `requirements.lock` provides `mcp.client.stdio.stdio_client` + `mcp.ClientSession` primitives (verified at T1 — if unavailable in the locked SDK version, escalate immediately, do not improvise)
- **When** the dev agent authors `tests/integration/transport_parity/test_mcp_stdio_smoke.py` (`pytest.mark.asyncio`) that:
  1. Spawns `uv run python -m app.mcp_server` as a real subprocess via `mcp.client.stdio.stdio_client`
  2. Connects via `ClientSession`, runs `await session.initialize()`
  3. Runs `await session.list_tools()` — asserts the `ping` tool is present + protocol-version metadata returned
  4. Runs `await session.call_tool("ping", {"input": "smoke"})` — asserts the response payload matches the minimal node's deterministic output
  5. Sends `SIGTERM` (POSIX) or `subprocess.terminate()` (Windows) to gracefully shut down within 3 seconds (hard-fail at 10 seconds); asserts subprocess `returncode` is set, no orphaned pipes
  6. Skips with documented reason if the `mcp` SDK import fails
- **Then** the test passes when run with the local subprocess, fails loudly on any of the above checks, and never blocks on operator-side state.

### AC-1.1d-C — FastAPI↔MCP byte-equivalent parity

- **Given** AC-1.1d-A and AC-1.1d-B are green
- **When** the dev agent authors:
  1. `tests/integration/transport_parity/test_fastapi_mcp_parity.py` driving the same input through both transports:
     - **Lane A (FastAPI):** spawn `app.runtime_server` subprocess; `httpx.post("/invoke", json={"input": "parity"})` → capture response payload
     - **Lane B (MCP):** spawn `app.mcp_server` subprocess; `await session.call_tool("ping", {"input": "parity"})` → capture response payload
  2. `docs/dev-guide/transport-parity-envelope-exceptions.md` documenting the exact fields allowed to differ between transports — initial set: `request_id`, `transport_name`, `timestamp_iso`, `latency_ms`, MCP-specific `_meta` envelope fields, FastAPI-specific HTTP headers. Any other field difference = test failure.
  3. The parity test strips the documented exception fields from both payloads, then asserts `payload_a == payload_b` (byte-equivalent on the residual)
- **Then** byte-equivalent parity is proven (modulo the documented exceptions table); CLI/SSE parity legs explicitly **deferred** with visible-roadmap pointer in the docstring + the inverted transport-parity matrix in `langgraph-runtime-setup.md` (1.1c authored the matrix; 1.1d updates the MCP-parity cells from "⏳" to "✅" in the same matrix).

### AC-1.1d-D — Cadence + flakiness budget

- **Given** AC-1.1d-B and AC-1.1d-C are the high-flake-risk tests per Murat's Round-2 test-architect analysis
- **When** the dev agent authors:
  1. `tests/integration/transport_parity/conftest.py` includes a `pytest.mark` (`@pytest.mark.transport_parity`) so the tests can be selected/excluded at CI lane level
  2. A pytest config update in `pyproject.toml` (or `pytest.ini`) registering the `transport_parity` mark with description noting "nightly / on-merge cadence; NOT per-PR — see Story 1.1d Cadence + Flakiness Budget AC"
  3. CI lane configuration **skeleton** (full CI wiring lands in Slab 4 Story 4.1's graph-compile-time hook) — for 1.1d, ship a placeholder `ci/transport_parity_lane.md` documenting the intent + the reopen-trigger
  4. Reopen-trigger note in both the test module docstring AND the story's Completion Notes: *"If subprocess smoke or parity test flakes >2% across its first 20 runs, reopen the MCP-in-Slab-1 deferral conversation per the 2026-04-22 middle-path consensus contingency."*
- **Then** the marker is registered, the lane skeleton exists, the per-PR Slab 1 smoke (from 1.1c) remains FastAPI-only, and the flakiness budget is grep-able.

### AC-1.1d-E — M1 acceptance gate

- **Given** all above ACs are green
- **When** Slab 1 closes (1.7 BMAD-closed) and the M1 acceptance evidence pack is compiled
- **Then** 1.1d's transport-parity test run is part of the M1 evidence (a green run on a clean checkout + lockfile-installed venv, recorded as a Completion-Notes artifact in 1.7 closeout); if 1.1d is red, M1 is not met; FR2 compound-contract claim is satisfied by 1.1d's closure, not by 1.1c's closure.

## Tasks / Subtasks

- [ ] **T1 — Read T1 Context Bundle.** (AC: pre-work)
  - [ ] [Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md) §1 (D7 in detail), §2 (FR2), §4 (sandbox-AC), §6 (anti-patterns), §8 (consensus chain — non-negotiable for understanding the 1.1c/1.1d split)
  - [ ] Verify `mcp` SDK version pinned in `requirements.lock`; confirm `mcp.client.stdio.stdio_client` + `ClientSession` are available; if not, escalate before any implementation

- [ ] **T2 — Author shared conftest + fixture.** (AC-1.1d-A)
  - [ ] `tests/integration/transport_parity/__init__.py` (empty)
  - [ ] `tests/integration/transport_parity/conftest.py` with `minimal_node_fixture` importing `app.runtime.minimal_node`; `transport_parity` pytest marker registration

- [ ] **T3 — Author MCP stdio subprocess smoke.** (AC-1.1d-B)
  - [ ] `tests/integration/transport_parity/test_mcp_stdio_smoke.py` (asyncio) per AC-1.1d-B steps 1–6
  - [ ] Skip-on-import-fail for `mcp` SDK
  - [ ] Subprocess timeout/cleanup discipline (no orphans)

- [ ] **T4 — Author FastAPI↔MCP parity test + envelope exceptions doc.** (AC-1.1d-C)
  - [ ] `docs/dev-guide/transport-parity-envelope-exceptions.md` enumerating allowed-divergence fields
  - [ ] `tests/integration/transport_parity/test_fastapi_mcp_parity.py` driving both transports + asserting byte-equivalence on residual
  - [ ] Update `docs/dev-guide/langgraph-runtime-setup.md` matrix: MCP-parity cell goes from "✅ 1.1d" pointer to actual "✅" status

- [ ] **T5 — Cadence configuration + flakiness budget.** (AC-1.1d-D)
  - [ ] `pyproject.toml` (or `pytest.ini`) registers `transport_parity` marker
  - [ ] `ci/transport_parity_lane.md` placeholder lane doc
  - [ ] Reopen-trigger docstring in tests + completion notes

- [ ] **T6 — Run validators + tests.** (closure)
  - [ ] Sandbox-AC validator on this story spec
  - [ ] `uv run ruff check tests` — must exit 0
  - [ ] `uv run pytest tests/integration/transport_parity -m transport_parity` — must pass (or skip on import fail)
  - [ ] **Per Murat amendment 2026-04-22 — hot-run + cold-run flake measurement, NOT just hot-run.** A single warm-box loop hides the real flake vector (CI cold start, Windows subprocess stdio, fresh-import overhead). Required measurement protocol:
    - **Hot run:** 17 invocations back-to-back, single venv, single Postgres instance, single pytest session. Measures code-path stability under warm imports.
    - **Cold-ish runs:** at least 3 of the 20 must be in a fresh subprocess environment — start a new pytest session for each, kill any stray `app.mcp_server` subprocesses between runs (`pkill -f app.mcp_server` on POSIX or `taskkill /F /IM python.exe` filter on Windows), so transport handshake overhead + accumulated-state effects are exercised.
    - **Total: 20 runs, mixed hot + cold.** Record the per-run pass/fail in Completion Notes plus the overall flake percentage. The >2% reopen budget applies to the overall percentage (pure hot = 0% reported is performative; cold runs are diagnostic).
  - [ ] If overall flake >2%, do NOT proceed to T7 commit — escalate per the AC-1.1d-D reopen-trigger.

- [ ] **T7 — Commit.** (closure)
  - [ ] `feat(migration): Slab 1 Story 1.1d — MCP transport smoke + FastAPI↔MCP parity acceptance`. Body cites D7 + 2026-04-22 middle-path consensus + FR2 closure.

## Dev Notes

### Why this story exists at all

This story is the operational evidence that Story 1.1c's MCP code substrate actually works end-to-end. Without 1.1d, the MCP code in 1.1c is shape-only — present but unproven. The middle-path consensus separated SHAPE (1.1c) from EVIDENCE (1.1d) on purpose: SHAPE is fast and goes on every PR; EVIDENCE is slower and goes on the milestone gate. See bundle §8.

### Subprocess discipline

MCP subprocesses can leak file handles, pipes, and threads if not cleaned up. The test must use `try/finally` (or async equivalent) to send `SIGTERM`/`terminate()` in the failure path AS WELL AS the success path. Any test failure that leaks a subprocess into the next test run is itself a test bug — write the cleanup before the assertion.

### Envelope exceptions doc is load-bearing

`docs/dev-guide/transport-parity-envelope-exceptions.md` defines what's allowed to differ. It must enumerate every allowed-divergence field with a one-line rationale. Future transport additions (CLI in Slab 3, SSE later) extend this doc, not silently widen the test's exception set.

### Flakiness budget = falsifiability

The >2%/20-runs reopen trigger isn't a soft target — it's a contingency built into the consensus. If the budget is exceeded, the dev agent must report the breach in Completion Notes and convene party-mode (not silently retry-loop the test until it passes). Flakiness here is diagnostic data about whether MCP-in-Slab-1 was the right call. Treat it as such.

### Project Structure Notes

**New files:**
- `tests/integration/transport_parity/__init__.py`
- `tests/integration/transport_parity/conftest.py`
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py`
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py`
- `docs/dev-guide/transport-parity-envelope-exceptions.md`
- `ci/transport_parity_lane.md` (skeleton)

**Modified:**
- `pyproject.toml` (or `pytest.ini`) — register `transport_parity` marker
- `docs/dev-guide/langgraph-runtime-setup.md` — flip MCP-parity cell from pointer to ✅ in the matrix

## References

- Bundle: [Slab 1 Story-Set A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md) — sole T1 reading; §8 is mandatory
- Story 1.1c spec: provides the shared minimal node, MCP code substrate, and matrix stub this story builds on
- Architecture D7 (three-transport parity)
- PRD FR2 (operator-surface contract — compound MCP+FastAPI+CLI)

## Dev Agent Record

### Agent Model Used

claude-opus-4-7 (1M context). Dev-story executed 2026-04-23 in single session
immediately following 1.1c BMAD closure.

### Debug Log References

- MCP SDK 1.27.0 client surface verified at T1: `mcp.client.stdio.stdio_client`
  + `mcp.ClientSession` + `mcp.client.stdio.StdioServerParameters` all available.
  Live probe round-trip (initialize → list_tools → call_tool ping) green in
  ~1s against the 1.1c MCP server substrate.
- MCP server negotiates `protocolVersion = "2025-11-25"` (LATEST) when client
  declares LATEST; the 1.1c `MCP_PROTOCOL_VERSION` pin (= `DEFAULT_NEGOTIATED_VERSION`
  = `"2025-03-26"`) is the SDK-upgrade-detection guard, NOT the per-handshake
  enforcement. Smoke test asserts `init.protocolVersion` non-empty rather than
  pinning a literal date.
- Initial parity test triggered SIM117 (nested async-with) — refactored both
  test files to use the parenthesized multi-context async-with form
  (`async with (stdio_client(...) as ..., ClientSession(...) as ...)`).

### Completion Notes List

- All 5 ACs (`A`, `B`, `C`, `D`, `E`-implicit) green via T6 validator battery —
  sandbox-AC PASS, ruff clean, lint-imports 3/3 KEPT, 20-run flake measurement
  20/20 PASS at 0.0% flake (well under the 2% reopen-trigger budget).
- **AC-1.1d-D 20-run flake measurement results (per Murat amendment 2026-04-22
  hot+cold protocol):** 17 hot runs (~3.5–4.3s each, warm OS cache, no inter-run
  pause) + 3 cold runs (~3.5s each, 1s pause + fresh subprocess) = **20/20 PASS,
  0.0% flake rate**. Reopen trigger NOT breached. Measurement script committed
  at `scripts/dev/flake_measure_1_1d.py` — re-runnable for CI authoring (Slab 4
  Story 4.1) and for the M1 acceptance evidence pack.
- **AC-1.1d-E M1 acceptance evidence:** transport-parity test run is now part
  of the M1 evidence pack. Story 1.7 closeout will fold the 20-run flake report
  + the per-run Completion Notes here into the M1 acceptance bundle.
- **Reopen-trigger in effect:** the docstrings of `test_mcp_stdio_smoke.py` +
  `test_fastapi_mcp_parity.py` carry the explicit "if flake >2% across first 20
  runs, reopen MCP-in-Slab-1 deferral conversation" callout per the 2026-04-22
  middle-path consensus contingency. CI lane skeleton at `ci/transport_parity_lane.md`
  documents the trigger for the future Slab 4 Story 4.1 CI author.
- **Substrate-bootstrap K framing per bundle §6 anti-pattern #3:** verification
  signals counted as command-equivalence checks (`pytest -m transport_parity` +
  20-run flake measurement script) in addition to the 2 pytest collecting nodes.
  Total story-scoped verification surface: 2 pytest + 1 measurement-script
  invocation (20 runs) + 4 validator gates (sandbox-AC, ruff, lint-imports,
  marker-registration). At Pts=3 / K-target ~1.5×, the substrate-bootstrap
  framing fits cleanly.
- **Live LangSmith path NOT exercised in this story** (it's 1.1c AC-D's domain
  and remains DEFER per 1.1c's G6-D1). The parity test deliberately scopes to
  the residual payload — span-tag emission is not yet wired; that lands when
  actual specialist nodes emit spans (Slab 2+).

### File List

**New files (this story):**

- `tests/integration/transport_parity/__init__.py` — package marker.
- `tests/integration/transport_parity/conftest.py` — `minimal_node_fixture`
  + transport-parity marker registration (lane-level mark via `pytestmark`
  declared at each test module).
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py` — AC-1.1d-B
  asyncio test: spawns `python -m app.mcp_server` via `stdio_client`,
  initializes `ClientSession`, asserts `ping` in `list_tools` + canonical
  payload from `call_tool('ping', {input:'smoke'})` + clean stream-context
  shutdown.
- `tests/integration/transport_parity/test_fastapi_mcp_parity.py` — AC-1.1d-C
  asyncio test: drives `{"input": "parity"}` through both transports
  (FastAPI subprocess via httpx + MCP subprocess via stdio_client), parses
  the MCP `content[0].text` to unwrap envelope, asserts `payload_a ==
  payload_b == expected_residual` byte-for-byte.
- `docs/dev-guide/transport-parity-envelope-exceptions.md` — authoritative
  reference for what's allowed to differ between transports + extension
  protocol for future transport additions (CLI 3.4, SSE later).
- `ci/transport_parity_lane.md` — placeholder lane documentation
  (intent + cadence + reopen-trigger + Slab 4 Story 4.1 wire-up checklist
  for the future CI author).
- `scripts/dev/flake_measure_1_1d.py` — 20-run hot+cold flake measurement
  harness; emits per-run pass/fail + aggregate flake-rate vs the 2% budget.

**Modified (this story):**

- `pyproject.toml` — registered `transport_parity` pytest marker with
  description noting nightly/on-merge cadence + reopen-trigger.
- `docs/dev-guide/langgraph-runtime-setup.md` — flipped MCP-parity matrix
  cell from forward-pointer ("✅ 1.1d (gates M1)") to actual ("✅ 1.1d
  (M1 gate green)") + added a "Smoke test (nightly / on-merge)" row
  capturing the 1.1d cadence; rewrote the "MCP transport — substrate vs
  production-ready" callout to reflect that 1.1c+1.1d together close the
  Slab 1 substrate claim for the FR2 compound contract.

### Change Log

| Date       | Change                                                              |
| ---------- | ------------------------------------------------------------------- |
| 2026-04-22 | Spec authored as part of Slab 1 story-set A (party-mode middle-path) |
| 2026-04-23 | T1–T6 dev-story executed; status `ready-for-dev` → `review`           |
| 2026-04-23 | bmad-code-review layered pass + remediation; status `review` → `done` |

### Review Findings

bmad-code-review layered pass self-conducted 2026-04-23 per the 31-3 + 1.1c
2pt/3pt-pattern-tight precedent (this is a 3pt single-gate substrate-bootstrap
story). Three layers (Blind Hunter diff-only / Edge Case Hunter boundary-walk /
Acceptance Auditor AC-by-AC) → ~14 raw findings → triage 3 PATCH (1 MUST-FIX
+ 2 SHOULD-FIX) + 1 DEFER + 10 DISMISS per aggressive G6 rubric.

**MUST-FIX patch applied (triple-layer convergent):**

- **G6-P1** Subprocess returncode + shutdown-budget assertion missing
  (Blind B3/B7 / Edge EDGE-1 / Auditor A2): AC-1.1d-B step 5 explicit
  *"asserts subprocess `returncode` is set, no orphaned pipes; gracefully
  shut down within 3 seconds (hard-fail at 10 seconds)."* The MCP SDK's
  `stdio_client` hides the subprocess.Popen handle inside its context
  manager so the SDK-roundtrip test cannot directly assert returncode.
  Remediated by adding a decoupled `test_mcp_server_subprocess_hygiene`
  test that spawns `python -m app.mcp_server` via raw `subprocess.Popen`,
  sends `terminate()`, asserts returncode-set within 3s graceful budget
  (10s hard-fail), drains pipes via `communicate()`. AC-1.1d-B step 5
  now literal-text-satisfied.

**SHOULD-FIX patches applied:**

- **G6-P2** `minimal_node_fixture` dead code (Auditor A1): the spec
  AC-1.1d-A explicitly required the fixture as the load-bearing import-
  boundary contract, but neither test injected it — both imported
  `MINIMAL_NODE_NAME` directly. Remediated by wiring the fixture into
  `test_fastapi_mcp_parity_residual_byte_equivalent` so the canonical
  name + payload come from the SoT module reference. Future drift on
  the SoT side now surfaces at the parity assertion site.
- **G6-P3** DRY violation: `_pick_free_port` + `_wait_for_health` were
  duplicated between `tests/integration/runtime/test_fastapi_server.py`
  (1.1c) and `tests/integration/transport_parity/test_fastapi_mcp_parity.py`
  (Blind B4). Extracted to `tests/_helpers/runtime_subprocess.py`
  exporting `pick_free_port`, `wait_for_health`, `DEFAULT_BOOT_BUDGET_S`.
  Both call sites now import from the helper; runtime test pass-rate
  unchanged (3/3 pre + 3/3 post).

**DEFER (logged here, NOT patched):**

- **G6-D1** Per-call asyncio timeout on `initialize` / `list_tools` /
  `call_tool` (Edge EDGE-1): if the MCP server crashes mid-handshake,
  the test could hang. The SDK's anyio context handles cancellation;
  pytest-timeout (project-level) catches infinite hangs at session level.
  Per-call `asyncio.wait_for` adds noise without proportional value.
  Pairs with G6-P1 above (subprocess hygiene test catches process
  liveness directly).

**DISMISSED (~10 cosmetic NITs per aggressive G6 rubric):**
local `import json` inside test function for clarity (B1); SDK cleanup
caveat — superseded by G6-P1 (B2); sync `_capture_fastapi_payload` vs
async `_capture_mcp_payload` — sequential by design (B5); no cross-
transport concurrency — by design (B6); hardcoded `expected_residual`
— pin by intent (B8); flake-script `single_session: bool` parameter
adequate semantic (B9); flake-script stderr truncation (B10); spec-vs-
impl wording divergences for AC-1.1d-C matrix-flip wording (A3) and
`pytestmark` vs `@pytest.mark` decorator placement (A4) — both match
intent.

**T6 re-validation post-patch (all green):**
- sandbox-AC validator: PASS
- ruff (app + all tests): clean
- pytest scoped (transport_parity + runtime): 6 passed (was 5 pre-patch
  — added the subprocess-hygiene test for AC-1.1d-B step 5)
- 20-run hot+cold flake measurement re-run: **20/20 PASS, 0.0% flake
  rate** (matches pre-patch result; the new hygiene test does not
  introduce variance)

Story BMAD-CLOSED `done`. UNBLOCKS Slab 3 Story 3.4 three-transport
verdict parity (inherits the two-transport baseline + envelope-exceptions
extension protocol) and closes the FR2 compound-contract substrate
claim at Slab 1.
