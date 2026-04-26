# Migration Story 3.4: Three-Transport Verdict Parity (MCP + FastAPI + CLI)

**Status:** ready-for-dev
**Sprint key:** `migration-3-4-three-transport-verdict-parity`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; M3 go/no-go gate).
**Pts:** 3 | **Gate:** single (per governance JSON `3-4.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.4× (target 12 / floor 9; 3 transport implementations + state-equality contract test + ledger/trace parity + operator_id + cache-state surface).

**Predecessor:** Stories 3.1 + 3.2 + 3.3 must be `done`. 3.4 builds on 3.3's `resume_from_verdict` + bridge stubs (`gate_cli` + `gate_endpoint`); fills in the FastAPI route + MCP tool + CLI body.

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia):** 1 BLOCKER + 4 RIDERs integrated:
- **A-BLOCKER-3.4-A (FastAPI dependency):** T1 sub-task — check `pyproject.toml` for `fastapi` + `httpx` (test client). If absent, add via operator-gated AC-B (split AC-B into AC-B-1 dev-agent FastAPI route + AC-B-2 operator-gated `uv add fastapi httpx` evidence-paste). Sandbox-AC discipline preserved.
- **A-R1-3.4 (hard dep on 3.3):** Spec declares hard dep on 3.3 close (NO parallel dev with 3.3) since 3.3 ships the bridge-stub callable surface that 3.4 fills.
- **A-R2-3.4 (single source-of-truth fixture):** Transport parity contract test uses ONE verdict payload + 3 transport adapters + ONE parametrized test asserting identical resulting `RunState` mutation. NO three independent test files (parity drifts).
- **M-R1-3.4 (in-process MCP harness):** MCP transport tests MUST NOT spawn subprocess; use in-process MCP harness. Subprocess transport tests are #1 source of CI flake.
- **M-R2-3.4 (structural-equivalence not string-equal):** Parity contract test asserts **structural equivalence of verdict envelope** (define equivalence predicate explicitly: same RunState mutation + same ledger key-set + identical span_name + transport_kind tag legitimately differs), NOT string-equal serialized output (transports legitimately differ in framing).

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `3-4.expected_gate_mode = "single-gate"` (rationale: null).
2. **3.3 substrate** — `app/marcus/cli/gate_cli.py` + `app/http/gate_endpoint.py` exist as bridge stubs; this story populates them with full transport bodies. `app/mcp_server/tools/gate_decide.py` exists from Slab-1 substrate per pyproject.toml:108 ignore_imports entry; this story extends it with the `gate.decide` MCP tool surface.
3. **OperatorVerdict + resume_from_verdict** per 3.3.
4. **DecisionCardMeta cache_state surface** per 3.2 (`Literal["healthy", "mixed", "cold"]` + `affected_nodes` + `override_trail`).
5. **MCP server substrate** — `app/mcp_server/` Slab-1 substrate (verify shape at T1).
6. **FastAPI substrate** — verify if FastAPI is in `pyproject.toml` deps (httpx is shipped per CLAUDE.md sandbox-AC; FastAPI may need adding).
7. **D7 transport parity** — three transports MUST produce IDENTICAL graph-resumption state; contract test asserts state equality + identical ledger events + identical LangSmith traces.
8. **Severance posture** — hybrid working tree.

### Slab 3.4 artifact-existence sweep (5-point)

- **A** `app/mcp_server/tools/gate_decide.py` exists per Slab-1 (verify); 3.4 extends with `gate.decide` tool surface.
- **B** `app/marcus/cli/gate_cli.py` exists as 3.3 bridge stub; 3.4 fills CLI body (argparse subcommand `gate decide`).
- **C** `app/http/gate_endpoint.py` exists as 3.3 bridge stub; 3.4 fills FastAPI route `POST /gate/verdict`.
- **D** FastAPI dep present in `pyproject.toml`; if absent, 3.4 adds it (operator-approved or `pip install fastapi`).
- **E** Ledger emission infrastructure carries `kind="verdict"` event shape (Slab-4 owns ledger schema; 3.4 emits proto-events that Slab-4 will consume — verify pre-Slab-4 emission shape carries forward).

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

**One:** epic 3.4 references `app/mcp_server/tools/gate.py`, `app/http/gate.py`, `app/marcus/cli/gate.py`; 3.3 established stubs at `gate_decide.py`, `gate_endpoint.py`, `gate_cli.py`. **Resolution:** 3.4 follows the 3.3 file naming (more specific); if epic literal `gate.py` is referenced elsewhere, document divergence.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) `app/mcp_server/tools/gate_decide.py` extension with `gate.decide` MCP tool implementation; (b) `app/marcus/cli/gate_cli.py` body — argparse subcommand `gate decide --trial-id ... --gate-id ... --verb ... --decision-card-digest ...`; (c) `app/http/gate_endpoint.py` body — FastAPI `POST /gate/verdict` route accepting OperatorVerdict JSON; (d) transport parity contract test asserting state equality across 3 transports; (e) ledger event emission per transport carrying `operator_id`; (f) DecisionCardMeta cache_state population at gate emission time. NOT in scope: model-override (3.5); E2E trial (3.6); ledger schema (Slab 4).

**Decision #2 — operator_id population per transport:** each transport MUST populate `operator_id` from a real source (not null, not a scheduler/system name). MCP: `operator_id = mcp_session.principal.id`; FastAPI: `operator_id = request.headers["X-Operator-Id"]` (validated regex per 3.3 OperatorVerdict pin); CLI: `operator_id = args.operator_id` (required argparse arg). Scaffold-conformance test greps for unauthorized `operator_id` values (system identifiers like `"scheduler"`, `"system"`, `null`).

**Decision #3 — Transport parity test invariants:** contract test asserts (a) graph-resumption state byte-equal post-resume across 3 transports; (b) ledger events emitted match key-set + values (excluding transport-specific transport_kind tag); (c) LangSmith trace tags carry transport_kind discriminator but resume_from_verdict span is identical across transports.

---

## Story

As an **operator with transport freedom per FR33 + D7**,
I want **identical `OperatorVerdict` submission via MCP `gate.decide`, FastAPI `POST /gate/verdict`, CLI `app.marcus.cli gate decide`, all routing through `resume_api.resume_from_verdict()`, with operator_id populated per transport + DecisionCardMeta cache_state surfaced on every emitted card**,
So that **FR33 + D7 transport parity is operator-verified, no transport shortcut bypasses tamper-evidence (3.3 enforcement), and operator UX is consistent across CLI/MCP/FastAPI**.

---

## Acceptance Criteria

### AC-3.4-A — MCP `gate.decide` tool implementation

- **Given** `app/mcp_server/tools/gate_decide.py` exists per Slab-1 substrate (3.3 may have populated minimal stub; 3.4 fills full tool surface)
- **When** the dev agent extends with the `gate.decide` MCP tool: accepts `{trial_id, gate_id, verb, decision_card_digest, edit_payload?}` payload + reads `operator_id` from MCP session principal + constructs OperatorVerdict + calls `resume_from_verdict(verdict)` + returns `{status, resumed_at}` response
- **Then** integration test exercises the tool surface end-to-end against a fixture trial
- **Test pin:** `tests/integration/transports/test_mcp_gate_decide_tool.py` — 1 test (full-flow integration).

### AC-3.4-B — FastAPI `POST /gate/verdict` route implementation

- **Given** `app/http/gate_endpoint.py` exists per 3.3 bridge stub
- **When** the dev agent fills the body: FastAPI route accepts JSON OperatorVerdict + reads `operator_id` from `X-Operator-Id` header + validates per OperatorVerdict pin + calls `resume_from_verdict(verdict)` + returns 200 with response dict OR 400 on invalid verdict OR 409 on `GateError("digest_mismatch")`
- **Then** integration test exercises the route via FastAPI TestClient
- **Test pins:**
  1. `tests/integration/transports/test_http_gate_endpoint.py` — 3 tests: happy-path 200, invalid-verdict 400, digest-mismatch 409.
  2. `tests/integration/transports/test_http_operator_id_header_required.py` — 1 test: missing `X-Operator-Id` → 400.

### AC-3.4-C — CLI `gate decide` subcommand body

- **Given** `app/marcus/cli/gate_cli.py` exists per 3.3 bridge stub
- **When** the dev agent fills the argparse body: subcommand `gate decide` with required `--trial-id`, `--gate-id`, `--verb`, `--decision-card-digest`, `--operator-id` args + optional `--edit-payload` (JSON file path)
- **Then** CLI invocation produces the same OperatorVerdict + same resume-graph effect as MCP/FastAPI
- **Test pin:** `tests/integration/transports/test_cli_gate_decide.py` — 2 tests: happy-path (subprocess invoke + assert exit 0 + state-resumed); invalid-args (missing required arg → exit non-zero + stderr regex).

### AC-3.4-D — Transport parity contract test (D7 binding)

- **Given** all 3 transports implemented (AC-A, AC-B, AC-C); contract test invariant per Decision #3
- **When** the same OperatorVerdict payload is submitted through each transport against the same fixture trial state
- **Then**:
  1. Graph-resumption state is BYTE-EQUAL across 3 transports (via `RunState` JSON serialization comparison)
  2. Ledger events emitted match key-set + values (excluding `transport_kind` tag — that's expected to differ)
  3. LangSmith trace tags carry `transport_kind` discriminator BUT the `resume_from_verdict` span is identical (span_id will differ; span_name + span_attributes match)
- **Test pin:** `tests/integration/transports/test_transport_parity.py` — 3 tests (one per invariant).

### AC-3.4-E — `operator_id` population per transport (Decision #2)

- **Given** each transport populates `operator_id` from a real source
- **When** scaffold-conformance test greps for unauthorized `operator_id` values
- **Then** test asserts no `operator_id` literal is in the forbidden set `{"scheduler", "system", "auto", "marcus", "cora", "", null, None}` across all 3 transport call sites
- **Test pin:** `tests/integration/transports/test_operator_id_real_source.py` — 1 test asserting AST-grep (NOT regex per Murat M-R4 + Amelia A-R1 reuse from 3.1) for forbidden literals in transport files.

### AC-3.4-F — DecisionCardMeta cache_state surfaced per FR24

- **Given** `DecisionCardMeta.cache_state` per 3.2 carries `Literal["healthy", "mixed", "cold"]`
- **When** operator views any gate's DecisionCard via any transport
- **Then** `meta.cache_state` reflects current prefix warmth at emit time + `meta.override_trail` shows applied overrides + D2 warning fires before override applies (override surface in 3.5; cache_state surface lands at 3.4)
- **Test pin:** `tests/integration/transports/test_decision_card_cache_state_populated.py` — 1 test asserting card emitted via each transport carries non-null cache_state value matching one of the 3 literals.

### AC-3.4-G — Anti-pattern catalog harvest (per R6)

NO new entries expected. If transport-parity drift surfaces, file as candidate.

### AC-3.4-H — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored.

### AC-3.4-I — D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** D7 transport parity (3 transports = 1 OperatorVerdict path); FR34 tamper-evidence (3.3) survives via single resume_api routing; FR33 transport freedom enforced.
2. **Anti-pattern harvest:** N/A.
3. **Migration-guide update:** §"Transport Parity" added (or extended) with 3-transport pattern.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: 3 transports + 3 invariant tests + 1 operator_id real-source AST-grep + 1 cache_state surface test.

### AC-3.4-J — Sprint-status state-flips at filing AND at close

At filing: `migration-3-4-...: ready-for-dev`. At close: `migration-3-4-...: done`.

---

## File Structure Requirements

### MODIFIED files (3.3 stubs filled in; ALL bridge bodies land at 3.4)

- `app/mcp_server/tools/gate_decide.py` — full MCP tool body per AC-A.
- `app/marcus/cli/gate_cli.py` — full argparse body per AC-C.
- `app/http/gate_endpoint.py` — full FastAPI route body per AC-B.

### NEW files

```
tests/integration/transports/
├── __init__.py
├── test_mcp_gate_decide_tool.py                     # 1 test (AC-A)
├── test_http_gate_endpoint.py                       # 3 tests (AC-B)
├── test_http_operator_id_header_required.py         # 1 test (AC-B)
├── test_cli_gate_decide.py                          # 2 tests (AC-C)
├── test_transport_parity.py                         # 3 tests (AC-D)
├── test_operator_id_real_source.py                  # 1 test (AC-E)
└── test_decision_card_cache_state_populated.py      # 1 test (AC-F)
```

### MODIFIED (other)

- `pyproject.toml` — add FastAPI dep if absent (operator-approved or `pip install fastapi`); ruff clean post-add.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-J.

---

## Testing Requirements

**K-target ~1.4× (target 12 / floor 9).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 1 (MCP tool full-flow) | **1** |
| B | 3 (200/400/409) + 1 (header-missing) = 4 | **2** (status-code-matrix collapsed to 1; header-required orthogonal property) |
| C | 2 (happy-path + invalid-args) | **2** |
| D | 3 (state-equality + ledger-parity + trace-parity) | **3** |
| E | 1 (operator_id real-source AST-grep) | **1** |
| F | 1 (cache_state populated) | **1** |
| **Total** | **12 collected** | **10 K-floor units** |

**Honest K-floor: 10** (above floor 9). Within ~1.4× K-target band (12/9 = 1.33×; 10/9 = 1.11×). Recalibrate to ~1.3× honest at story-open if needed.

**Regression target at T8:** baseline + previous Slab 3 + 12 collected. Import-linter contracts: C3 ignore_imports for the 2 NEW transport bridges per 3.3 already added; 3.4 does NOT add more contracts (transport bodies populate the existing authorized paths). Sandbox-AC PASS (FastAPI TestClient + MCP test fixture + CLI subprocess all via shipped Python deps).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
