# ADR 0001: Parity-Contract DSL

Status: ACCEPTED - 2026-05-04 by party-mode Round-2 4/4 unanimous (John+Winston+Amelia+Murat)

## Context

Slab 7c introduces HIL surfaces and parity checks that must stay coherent across CLI, HTTP, MCP-stdio, and MCP-subprocess transports. The existing parity tests are useful but file-local. They do not give downstream stories one stable declaration mechanism for mandatory transports, and they do not name the boundaries that keep the parity layer away from graph-runtime code.

This ADR records the decision-bearing portion of Story 7c.0a only. Executable primitives land in Story 7c.0b. The 7c.1 refactor consumes the executable scaffold and moves existing transport-parity tests onto the DSL. This split follows the Decision-then-Foundation pattern described below.

References:

- PRD FR-7c-30..33: parity-contract DSL requirements.
- PRD FR-7c-50: audit-chain integrity requirement.
- PRD FR-7c-53: import-linter contracts C4/C5/C6.
- Epic Story 7c.0a section in `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md`.
- Governance JSON story `7c-0a` in `docs/dev-guide/migration-story-governance.json`.
- Pydantic-v2 checklist in `docs/dev-guide/pydantic-v2-schema-checklist.md`.

## Decision Summary

Story 7c.0a lands the architecture decisions and guardrails:

- The parity-contract DSL uses decorator registration for in-tree surface modules.
- Per-surface transport declarations use a Pydantic-v2 schema.
- The existing eight parity files are refactor targets for 7c.1, not 7c.0a.
- D7 transport-DSL completeness is bounded; timeout, streaming, backpressure, and error-frame encoding need explicit extension or addendum.
- The Decision-then-Foundation pattern is named for future slabs.
- Scaffold-completeness in 7c.0b must evaluate TW-7c-4, TW-7c-5, and TW-7c-6 independently.
- Audit-chain integrity is specified conceptually in Appendix A; executable tests land in 7c.0b.

## 1. Registration Mechanism Choice

Decision: use decorator registration for Slab 7c surface modules.

The DSL will expose a decorator-style declaration on in-tree modules under `app/gates/**` once the executable scaffold lands in 7c.0b. A surface should declare its parity contract near the transport handlers it protects, for example by decorating a module-local declaration function or object. The exact callable shape is intentionally deferred to 7c.0b.

Tradeoffs considered:

- Decorator registration keeps declarations close to the surface code and fits the Slab 7c in-tree use case. The cost is coupling to module import order, so the 7c.0b scaffold must define one deterministic discovery path and test it.
- Entry-point registration is pip-discoverable and plugin-friendly, but it is heavyweight for this repo-local slab. It is reserved for post-Slab-7c extensibility.
- YAML registration separates declarations from Python import order, but it adds parser and path-lockstep overhead. It also moves a behavioral contract away from the modules that own the transports.

Decorator registration is therefore the default. If a future plugin model requires out-of-tree surfaces, entry-point registration can extend the DSL without invalidating the in-tree decorator form.

## 2. Per-Surface Transport Declaration Schema

Decision: use a Pydantic-v2 declaration model, not a YAML-only schema.

The scaffold in 7c.0b should define a schema equivalent to:

```python
class SurfaceTransportDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    surface_id: str
    mandatory_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]
    optional_transports: list[Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]]
```

The exact class name and module path belong to 7c.0b. The field set is frozen here:

- `surface_id: str`
- `mandatory_transports: list[str]`, subset of `{"cli", "http", "mcp-stdio", "mcp-subprocess"}`
- `optional_transports: list[str]`, same subset

Pydantic-v2 is selected because this slab already relies on schema-shape idioms: `validate_assignment=True`, `extra="forbid"`, closed-enum rejection, and JSON Schema parity. The OperatorVerdict shape-stability work in FR-7c-49 can use the same validator discipline.

The declaration validator should reject duplicate transports across mandatory and optional sets. It should also reject surfaces that declare no mandatory transports, because FR-7c-32 denies parity-test budget to undeclared mandatory transport surfaces.

## 3. Refactor Target List

Story 7c.1 owns the refactor of existing parity files. Story 7c.0a does not modify these tests, and Story 7c.0b only provides the executable DSL scaffold they will consume.

The eight refactor targets are:

- `tests/integration/transport_parity/test_fastapi_mcp_parity.py`
- `tests/integration/transport_parity/test_mcp_stdio_smoke.py`
- `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py`
- `tests/integration/transports/test_transport_parity.py`
- `tests/integration/transports/test_override_transport_parity.py`
- `tests/integration/transports/test_cli_gate_decide.py`
- `tests/integration/transports/test_http_gate_endpoint.py`
- `tests/integration/transports/test_mcp_gate_decide_tool.py`

The baseline to preserve is the existing transport parity matrix before HIL surface registration. The DSL should reduce per-surface bespoke tests, not shrink current coverage.

## 4. D7 Transport-DSL-Completeness Policy

Decision: the DSL covers declaration and parity-test registration. It does not silently claim full transport semantics.

The DSL does not cover:

- Timeout semantics.
- Streaming.
- Backpressure.
- Error-frame encoding.

Default escape hatch: extend the DSL when one of these semantics becomes a repeated transport contract. The extension must carry tests and ADR or decision-log coverage appropriate to its blast radius.

Exception escape hatch: a per-transport addendum may be documented inline at the surface module. This requires party-mode consensus because it creates a local semantic exception. The addendum must name why the general DSL should not be extended yet, which transport is exceptional, and which tests own that exception.

No implicit escape hatches are allowed. A downstream story either extends the DSL or records the addendum with consensus.

## 5. Decision-then-Foundation Pattern

Decision: name and reuse the Decision-then-Foundation pattern.

Pattern statement:

> When a substrate-touching change carries more than five decision-bearing artifacts, split into one architecture-tier story that lands all decisions, import-linter contracts, Pydantic spec stubs, and ADR text with no executable scaffold, and one build-tier story that lands the executable scaffold consuming those prior decisions.

Breaking-point rule: more than five decision-bearing artifacts forces the split.

The original 7c.0 carried ten seams. Splitting 7c.0 into 7c.0a and 7c.0b prevents downstream stories from inheriting a moving architecture target. The 7c.4a to 7c.4b taxonomy/foundation split is the same pattern.

Future slabs should use this rule when a single story would otherwise mix architecture decisions, import boundaries, schema contracts, executable substrate, migration tests, and downstream story gates.

## 6. AMEND-7d-ii Completeness-Flags Planning

Decision: Story 7c.0b must expose three separate scaffold-completeness flags:

- TW-7c-4 detection PASS/FAIL.
- TW-7c-5 detection PASS/FAIL.
- TW-7c-6 detection PASS/FAIL.

The done condition is composite all-three-PASS, but the evidence cannot be a single composite flag. Any one FAIL blocks the 7c.0b done flip. A single "all-three-PASS" field is insufficient because it hides which tripwire family failed and weakens remediation routing.

This ADR records the rule so 7c.0b can implement it without reopening the policy decision.

## Consequences

Positive consequences:

- Downstream stories inherit one registration decision instead of relitigating decorator versus YAML versus entry-point.
- Import-linter contracts C4/C5/C6 can enforce from 7c.0a forward while target lists remain empty.
- Existing parity tests have an explicit refactor target list.
- Audit-chain integrity has named error semantics before executable tests land.

Costs and constraints:

- Decorator discovery must be deterministic in 7c.0b.
- Future out-of-tree plugins will need an entry-point extension.
- Transport behaviors outside the DSL need explicit extension or addendum.
- The 7c.0a contract sources are future module expressions because the executable packages intentionally do not exist until 7c.0b and later surface stories.

## Appendix A: Audit-Chain Integrity Conceptual Design

FR-7c-50 requires audit-chain integrity for tripwire and override-event style ledgers. Story 7c.0a records the conceptual design only. The executable test scaffold lands in Story 7c.0b at `tests/audit/test_override_event_chain_integrity.py`.

### Append-Only Invariant

Rows in `sprint-status.yaml::tripwire_events` are append-only at the file level. New events are added as new rows. Existing rows must not be rewritten without audit evidence.

If a row must be updated in place, for example `fired_verdict: not_yet_evaluated` to `fired`, the update must increment `revision: int` and retain the prior revision in `revision_history: list[dict]`. The revision fields are part of the FR-7c-50 design surface and should land with the executable audit-chain validator in 7c.0b, not in the 7c.0a `TripwireLedgerEntry` minimum schema unless 7c.0b explicitly chooses to extend it.

### Monotonic Timestamp

For each `tripwire_id`, every entry's `fired_at` must be greater than or equal to the prior entry's `fired_at`. Out-of-order timestamps are red-rejection triggers in the audit-chain validator.

### Parent-Trace Linkage

If `trace_id` is populated, it must link to the LangSmith trace where the tripwire fire decision was made. Missing `trace_id` when `fired_verdict` is `fired` or `marginal-fired` is a red-rejection trigger.

### Red-Rejection Error Semantics

Error hierarchy:

- Root: `AuditChainIntegrityError`.
- Out-of-order timestamp: `AuditChainOrderError`.
- Missing parent trace: `AuditChainParentLinkError`.

Module placement for these errors: `app/audit/errors.py`.

At 7c.0a T1, `app/audit/` does not exist in this checkout. That is acceptable for this decision-tier story. The conceptual module path is reserved here; the package and error classes land with 7c.0b's executable scaffold.
