# Transport-Parity Envelope Exceptions

**Status:** authoritative reference for the FastAPI↔MCP byte-equivalent parity test (`tests/integration/transport_parity/test_fastapi_mcp_parity.py`, Slab 1 Story 1.1d AC-1.1d-C). Future transport additions (CLI in Slab 3 Story 3.4, SSE later) extend this doc; widening the test's exception set without an entry here is a regression.

## Purpose

Architecture decision **D7** (Operator-surface contract — three-transport parity) requires that the same operator request return the same payload regardless of transport. Some transport-level differences are inherent (HTTP headers exist on FastAPI but not MCP; MCP wraps content in `CallToolResult.content[0].text`) and would otherwise break a naive `payload_a == payload_b` assertion. This doc enumerates the **allowed** divergences.

The parity test:

1. Drives both transports with the same input (`{"input": "parity"}`).
2. Extracts the residual payload from each transport (parsing JSON, unwrapping envelopes per the table below).
3. Asserts the residuals are byte-equivalent (`payload_a == payload_b`).

Anything not on this list, that differs, is a real parity failure.

## Allowed-divergence table (Slab 1 baseline)

| Field / envelope element             | FastAPI side                                              | MCP side                                                              | Rationale                                                                                                            |
| ------------------------------------ | --------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| HTTP status code                     | `200` on success                                          | (no equivalent — MCP uses `CallToolResult.isError`)                   | Transport-specific success signaling. Both are normalized to "this call succeeded" before the residual comparison.   |
| HTTP response headers                | `Content-Type`, `Content-Length`, etc.                    | (no equivalent — JSON-RPC frames over stdio carry no HTTP headers)    | Transport-only metadata. Stripped from the residual.                                                                 |
| MCP `CallToolResult.meta`            | (no equivalent)                                           | Optional `_meta` envelope dict; absent for `ping` in Slab 1            | MCP framing field. Stripped from the residual.                                                                       |
| MCP `CallToolResult.isError`         | (no equivalent — HTTP status carries this)               | `False` on success                                                     | Transport-specific success signal. Asserted separately (must be `False`); not part of the residual comparison.       |
| MCP `CallToolResult.structuredContent` | (no equivalent)                                         | Optional structured output; not used by `ping` in Slab 1               | MCP framing field. Absent in Slab 1 — guard for future use only.                                                    |
| MCP content-array structure          | (FastAPI returns the dict directly as JSON body)          | `content[0].text` is a JSON string that, when parsed, equals the body | MCP requires content to be wrapped in `TextContent` blocks; the parity test parses `content[0].text` to unwrap.     |
| `request_id` (FUTURE — not in Slab 1) | Will appear in response when added                        | Will appear in MCP `_meta` when added                                  | Transport-tagged correlation ID. Per-transport so values cannot match; entry reserved here so the future addition does not silently widen the test. |
| `transport_name` (FUTURE)            | Reserved                                                  | Reserved                                                              | Reserved entry so a future addition does not silently widen the test.                                                |
| `timestamp_iso` (FUTURE)             | Reserved                                                  | Reserved                                                              | Wall-clock timestamps differ by I/O scheduling; reserved entry so future additions do not silently widen the test.  |
| `latency_ms` (FUTURE)                | Reserved                                                  | Reserved                                                              | Per-transport timing differs by definition; reserved entry so future additions do not silently widen the test.       |

## Residual payload (Slab 1 baseline — what MUST match byte-for-byte)

After applying the allowed-divergence stripping above, the residual payload from BOTH transports must equal:

```json
{
  "node": "noop",
  "result": {
    "smoke": "ok",
    "node": "noop",
    "echo": "<input value>"
  }
}
```

Any divergence on these fields is a real parity failure and a Story-1.1d test regression.

## Extension protocol

When adding a new transport (CLI in Story 3.4, SSE later, etc.) or a new framing field on an existing transport:

1. Add a row to the table above with the field name, per-transport value or `(no equivalent)`, and a one-line rationale.
2. Update the parity test's stripping logic to remove the new field from the residual.
3. Do not silently widen the parity test's exception set without a row here.

This file is the authority. The test is the enforcement.
