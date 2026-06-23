# Codex Dev Prompt — Variant Directive Injection Seam (NEW CYCLE)

**You are Codex (T1–T10).** Claude runs T11. This is a **tight** cycle (~small, well-scoped). No party round (uncontroversial extension of the already-green-lit `gamma_settings` carrier; operator-authorized direct). Authority: `variant-selection-deckwide-fix-scope-2026-06-23.md` + the `marcus-spoc-variant-treatment-template-picklist` follow-on (this seam is its first concrete piece).

## Goal
Add a **trial-start seam** to supply per-variant `gamma_settings` so it lands in the composed `directive.yaml` **at compose time (before the digest)** — enabling a 2-variant demonstration trial with the locked A/B looks (Tejal + Blueprint Editorial). Today the directive is composed fresh at G0 by `compose_and_write` with NO `gamma_settings` seam; a mid-trial edit is ruled out (it breaks the conversation-persistence digest chain). So the injection must happen during composition.

**Downstream is already built:** `production_runner._gamma_settings_from_directive` reads `gamma_settings` from `directive.yaml` → Gary's payload → `_normalized_gamma_settings` (which SEEDS from `DEFAULT_VARIANT_PAIR`). So a **minimal** directive entry `gamma_settings: [{variant_id: A}, {variant_id: B}]` auto-expands to the full locked A/B looks. Do NOT rebuild any of that.

## T1 PRECONDITION (report in Dev Notes BEFORE code)
1. `app/composers/section_02a/directive_model.py:131` `class Directive` is `ConfigDict(extra="forbid", validate_assignment=True)` and has **no `gamma_settings` field**. So setting it requires ADDING an optional field. **Critical byte-stability constraint:** the §02A Directive is governed (Epic 34 forensic ratchet — a sha256-pinned fixture loads via `Directive.model_validate`; the trial digest pins single-variant runs). The new field MUST serialize **excluded when absent/None** so every directive WITHOUT `gamma_settings` is **byte-identical** to today. Confirm the §02A forensic ratchet + schema-coherence tests are green pre-change (capture the baseline).
2. Confirm `write_directive_yaml` (`composer.py:175`) serialization path + that `_gamma_settings_from_directive` (`production_runner.py:1096`) reads the raw YAML key (it does) — so the field name in the model must serialize to `gamma_settings`.
3. Confirm none of the touched files are on `block_mode_trigger_paths` (they are not: directive_model.py / composer.py / cli_adapter.py / trial.py). No pack/manifest/lockstep.

## The change
1. **Directive model** (`directive_model.py`): add an **additive optional** `gamma_settings: list[dict[str, Any]] | None = None` (or a typed sub-model if the schema warrants; the schema already defines the item shape). **Must serialize-excluded when None** (`Field(default=None)` + `model_dump(exclude_none=True)` at the write path, or `exclude` semantics) so absent → byte-identical directive. Keep `extra="forbid"`.
2. **`write_directive_yaml`** (`composer.py:175`): ensure `gamma_settings` is written when present, **omitted entirely when None/absent** (byte-stability for legacy/single-variant).
3. **`compose_and_write`** (`app/composers/section_02a/cli_adapter.py:30`): add an optional `gamma_settings: list[dict[str, Any]] | None = None` param; after `compose(...)` returns the Directive and BEFORE `write_directive_yaml` + digest, overlay it onto the directive (set the field). Digest is then computed over the final directive (consistent — no mid-trial mutation).
4. **`trial start` CLI** (`app/marcus/cli/trial.py`, around `compose_and_write` at :247): add a **`--gamma-settings-file <path>`** flag — loads a JSON/YAML list of per-variant settings and threads it into `compose_and_write`. (This is the forward-compatible seam the future Marcus-SPOC treatment pick-list will write to.) Absent flag → `gamma_settings=None` → today's behavior exactly.

## Tests (RED-first; all BINDING)
1. **Injection round-trip:** `compose_and_write(..., gamma_settings=[{"variant_id":"A"},{"variant_id":"B"}])` → `directive.yaml` contains the `gamma_settings` list → `_gamma_settings_from_directive(directive_path)` returns it → (assert it reaches a Gary payload via the existing builder). RED-first: pre-change `compose_and_write` has no such param.
2. **Legacy byte-identity (LOAD-BEARING):** `compose_and_write(...)` with NO `gamma_settings` → `directive.yaml` is **byte-identical** to the pre-change output (no `gamma_settings` key emitted); the §02A forensic ratchet + schema-coherence tests stay green; the directive digest is unchanged. Capture the pre-change golden.
3. **Directive model additive:** `Directive` accepts an optional `gamma_settings`; `model_dump`/serialization EXCLUDES it when None (byte-stable); a directive WITH it round-trips through `model_validate`.
4. **CLI threading:** `trial start --gamma-settings-file <f>` loads the file and passes it to `compose_and_write`; absent flag → None.

## Fences / governance
Data-plane; **§02A additive only** — the Directive change must NOT break the Epic-34 forensic ratchet or the schema-coherence tests (baseline-diff attest: same ambient set, zero new reds). No pack/manifest/4-file-lockstep edit, no new top-level payload key beyond the already-declared `gamma_settings`. Excluded-when-absent serialization is the backward-compat keystone. ruff + lint-imports + focused tests green. Codex T1–T10 → Claude T11.

## Handoff → Claude T11
`_codex-handoff/variant-directive-injection-ready-for-review.md`: the T1 model/serialization + baseline report; the RED transcript; the 4 test results; the legacy byte-identity golden attestation; the §02A ratchet/schema-coherence baseline-diff attestation; a sample `gamma_settings` file + the resulting `directive.yaml` excerpt showing the A/B pair landed.

## NOTE
After this lands + T11 closes, Claude runs the 2-variant demonstration trial: `trial start … --gamma-settings-file <A/B-pair-file>` → SPOC `--decisions-file` G2B select → drive to completion. The demo file is the minimal `[{variant_id:A},{variant_id:B}]` (DEFAULT_VARIANT_PAIR fills the Tejal/Blueprint looks).
