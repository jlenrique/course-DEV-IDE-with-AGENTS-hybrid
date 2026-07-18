# How to add a HIL tabular renderer for a gate

*(Established by Epic 43 — HIL Surface Tabular Coverage, 2026-07-17. The operator requirement `hil-operator-surfaces-must-be-tabular`: every operator-facing HIL review surface must project into a table, never a raw YAML/JSON dump.)*

The CLI HIL surface is rendered by **`app/marcus/cli/hil_tabular_projector.py`**. When a paused gate shows the operator review content, that content must be tabled. This is the integration contract for adding a renderer for a new (or currently-generic) gate content type.

## The five steps

1. **Write the renderer** in `hil_tabular_projector.py`:
   `def render_<x>(content: Mapping[str, Any], *, title: str = "...", page_size: int = PAGE_SIZE) -> str:`
   Reuse `_md_table(headers, rows)` + `_truncate_cell(text, width)` (fixed-width, no 80-col wrap). Bound nested values with the `_summarize_nested_value` pattern (240-char cap) — never dump raw nested JSON. **Tolerate both** the nested `display_*` shape and the bare decision-card/payload body (the live paused path feeds the card body; fixtures may carry the full display shape).
2. **Register it:** `register_renderer("<canonical_key>", render_<x>)` at import.
3. **Add the canonical key** to `GATE_CONTENT_TYPES` (the SSOT frozenset).
4. **Bridge the gate → key** in `GATE_TO_CONTENT_TYPE`, and make sure `_emit_gate_surface_if_paused` (in `trial.py`) resolves it via `resolve_content_type`. **Discovery gotcha:** the paused-gate string (`gate` / decision-card `gate_id`) is often shared across gates that fold together (e.g. G2B/G2M share `G2C`; G4B/G5/G4A fold to `G4`; motion folds to `G3`). When shared, key by the poll-surface **`surface_id`** instead and leave the shared gate string **deliberately unmapped** (a pinning test asserts this — unmapped → generic fallback, still tabular).
5. **Move the key off `KNOWN_UNRENDERED_ALLOWLIST`** — or `tests/marcus/cli/test_projector_coverage_ratchet_43_10.py` **fails CI** (the RED-first ratchet: every canonical type must be registered XOR waived, and the allowlist must reach empty at epic close).

## Invariants (non-negotiable)

- **stdout stays machine JSON; the human table goes to stderr.** The projector returns strings only; `trial.py` writes them to `sys.stderr`. (This was the 42-1 escape — a contract-wide change must re-assert it.)
- **The projector stays stdlib-pure** — imports only `collections.abc` / `typing`. Do NOT import `yaml` or any `poll_surface` into it (import-linter C6 enforces this). If the renderer needs parsed input, the caller (`trial.py`, which already imports yaml) parses and passes a mapping.
- **Additive-within-v1** — a new renderer/key is additive; do NOT bump the `operator_surface` schema for a render feature (AD-4 / 35.9 precedent).

## Fixtures + tests

- **Synthesize fixtures from the REAL card model** — invoke the real Pydantic card model / `display_*` function to build `tests/fixtures/hil_projector/poll-<x>-synthetic.json` (shape fidelity by construction, zero spend). Real G0/G0E/G0R/G1 fixtures are frozen from runs `5169a872`/`bc747b51`.
- **Model-binding check (43-4 lesson):** verify the poll_surface's declared model matches the card that actually flows at the paused gate (check on-disk `state/config/runs/**/decision-card-*.json`). If a poll_surface binds a different model and fields are genuinely absent, target the renderer at the REAL card body and FILE the mismatch to deferred-inventory — do NOT fix the binding in the renderer story.
- **Register any new test `.py` file** in `PERMITTED_PYTHON_DIFFS` (`tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`, Epic-43 block) or the TW-7c-4 scope tripwire fires.

## Not every gate content type is a HIL surface

`research_packet` and `workbook` were in the provisional canonical set but are NOT operator-reviewed at a paused gate (workbook runs post-G5; research is consumed internally at 04.55). The honest resolution was to **remove them from `GATE_CONTENT_TYPES`** with rationale — not to build phantom renderers. Do the same for any "content type" that has no operator review gate.
