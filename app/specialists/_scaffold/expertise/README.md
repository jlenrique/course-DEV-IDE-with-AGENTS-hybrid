# _scaffold expertise contract

`expertise/` stores specialist-specific reference material used by the `plan`
phase. The scaffold keeps this directory as a documented placeholder so
generated specialists have a stable location for domain files.

Guardrails:
- Node lifecycle stays on the canonical chain:
  `receive -> plan -> act -> verify -> reflect -> emit_spans -> gate_decision -> finalize -> handoff`.
- `state.py` keeps specialist ID pinned via `ClassVar` (`_SPECIALIST_ID`), not
  field shadowing.
- Generator denylist (`audra`, `cora`) is governance-preserving and mandatory.

For concrete specialists, populate this directory with source documents and
update this README with an index of files that the specialist consumes.
