# G4 — Operator Reference

**Use this doc when:** you've received a paused-at-G4 notification from a trial and need to author a verdict file.

## Verdict file shape

```json
{
  "verdict_id": "<uuid>",
  "trial_id": "<uuid matching --trial-id>",
  "card_id": "<uuid matching the decision-card-G4.json>",
  "verb": "approve" | "edit" | "reject",
  "gate_id": "G4",
  "decision_card_digest": "<sha256 hex from decision-card-G4.json>",
  "operator_id": "<your operator id>",
  "edit_payload": null,
  "reject_reason": null,
  "revise_count": 0,
  "timestamp": "<ISO 8601 UTC>"
}
```

The exact OperatorVerdict shape is canonical at `app/models/state/operator_verdict.py` and emitted JSON Schema at `app/models/schemas/operator_verdict.schema.json`.

## Decision tokens

The shim emits a single-decision verdict per the `verb` field. Closed enum values:

- **approve** — pass-through; trial advances to next gate.
- **edit** — operator-provided `edit_payload` propagates into resume state; trial advances.
- **reject** — operator-provided `reject_reason` halts the trial.

The richer decision/directive vocabulary from `docs/conversational-gates/_registry/vocabulary.yaml` (Story 7a.6) is consumed by the pre-fill mechanism (Story 7a.3) BEFORE the shim is invoked; the shim itself only handles the terminal verdict.

## Directive tokens

Not applicable to A2 single-decision shims — the shim's job is to load + validate + dispatch a verdict file, not to compose a multi-field directive. For richer directive emission, see Story 7a.3 (pre-gate-marcus) and 7a.6 (vocabulary registry).

## Common patterns

### Minimal approve

```json
{
  "verdict_id": "11111111-1111-4111-8111-111111111111",
  "trial_id": "<your-trial-uuid>",
  "card_id": "<from decision-card-G4.json>",
  "verb": "approve",
  "gate_id": "G4",
  "decision_card_digest": "<from decision-card-G4.json>",
  "operator_id": "juanl",
  "edit_payload": null,
  "reject_reason": null,
  "revise_count": 0,
  "timestamp": "2026-04-29T12:00:00Z"
}
```

Run: `python -m app.marcus.cli.gate_shims.g4_shim --trial-id <uuid> --verdict-file path/to/verdict.json --operator-id juanl`.

### Edit-with-rationale

Set `"verb": "edit"` and populate `"edit_payload": { ... }` with the deltas. The payload propagates into resume state per Slab 6.1 substrate; trial advances after edit-payload application.

### Reject

Set `"verb": "reject"` and populate `"reject_reason": "<rationale>"`. Trial halts; status transitions to "failed".

## Troubleshooting

- **exit 0** — success; resume payload printed as JSON on stdout.
- **exit 1** — RuntimeError: trial-id mismatch, or trial not paused at G4, or downstream resume failure. Inspect stderr for the message.
- **exit 2** — ValidationError: verdict file is not a valid OperatorVerdict shape. Re-emit per the schema and retry.

For the `silent_bypass_events` invariant (must be 0 per FR-A23 from Story 7a.2), see `runs/<trial_id>/run_summary.yaml` post-trial.

---

**Gate label:** Fidelity + Quality Pre-Spend (Vera G4 + Quinn-R pre-composition)
**Story 7a.7 spec:** `_bmad-output/implementation-artifacts/migration-7a-7-a2-single-decision-shims-terminal-gates.md`
