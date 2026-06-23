# Codex Remediation Prompt — Variant Selection Deckwide T11 HAND BACK

**You are Codex.** Claude re-runs T11 after. This is a remediation of the work in
`codex-dev-prompt-variant-selection-deckwide.md` (T1–T10 already landed; build is UNCOMMITTED in the
working tree — extend it, do NOT revert). Claude T11 + 3-layer `bmad-code-review` (Blind/Edge/Auditor)
found **1 MUST-FIX + a SHOULD-FIX cluster**. The **core mechanism is CORRECT** (filter reads the pick
from the right `cache_prefix`; idempotent; digest recompute mandatory; warm-401 retry sound) — do NOT
rework it. Fix exactly the items below, each RED-first.

## MF-1 (MUST-FIX) — partial-coverage short deck
`app/marcus/orchestrator/production_runner.py` `_apply_deckwide_variant_selection`. The duplicate
guard enforces "≤1 row per *surviving* slide" but never "exactly 1 per *original* slide." A slide
present only in the NON-selected variant is silently dropped → short deck, no error. This violates the
binding party AC (Winston A1: "exactly one, not at most one"; the collapse must be **total and
asserted**).
- **Fix:** before filtering, capture the set of all `slide_id`s present in the pre-filter `rows`
  (the full original slide set). After filtering, assert the surviving `slide_id` set **equals** the
  original set. Raise `VariantSelectionError` naming the dropped slide_id(s) if any original slide
  retained zero rows for the selected variant. (Keep the existing exactly-one/duplicate guard — now
  you enforce BOTH "≥1" and "≤1" = exactly one per original slide.)
- **RED-first test:** add a case to `test_deckwide_variant_selection_filter.py` — rows where slide-01
  has A+B but slide-02 has ONLY A; select "B"; assert it raises (naming slide-02). Paste the RED
  (the pre-fix code silently returns a 1-slide deck).

## SF-1 / SF-2 (SHOULD-FIX) — validator sentinel-leak
`app/specialists/gary/_act.py` `_validate_enum_setting`. The skip set `{"", "default", "auto",
"balanced"}` is applied GLOBALLY, so a value that is a sentinel for ONE knob bypasses validation for
knobs where it is invalid, then gets emitted to Gamma: `dimensions="auto"`, `language="balanced"`,
`text_mode="auto"`, `image_model="balanced"` all skip validation and reach the API (violating "bad
raises before any credit-spend").
- **Fix:** make the omit-sentinels **per-knob** — only the token(s) that legitimately mean "omit" for
  THAT knob skip validation; any other non-empty value that isn't in the knob's allowed set raises.
  (E.g. `dimensions` has no "auto"/"balanced" omit-sentinel → `dimensions="auto"` must raise.)
  Keep the empty-string/None = omit behavior.
- **RED-first tests (also closes AC3 gap below):** per-knob bad-input case for EACH of the 6 enum
  knobs lacking one today (`image_style_preset`, `image_model`, `image_source`, `dimensions`,
  `language`, `text_mode`): a structurally-valid-but-absent value RAISES `gamma.settings.invalid`
  AND asserts `client.generate_calls == []` (no spend). Include the leak cases above explicitly.

## SF-3 (SHOULD-FIX) — custom preset without style
`_image_options_for_variant`: `image_style_preset="custom"` with empty `image_style` emits a bare
`{"stylePreset":"custom"}` (no prompt) → likely an API no-op/error. Fix: when preset is `custom`,
require a non-empty `style`; raise `gamma.settings.invalid` if absent. RED-first test.

## SF-4 (SHOULD-FIX) — non-list keywords silently lost
`_normalized_gamma_settings`: `keywords` sent as a string (not list) falls through to the scalar
branch, is stored as a string, then silently dropped by `_instructions_for_variant`'s
`isinstance(list)` check. Fix: reject a non-list `keywords` with `gamma.settings.invalid` (or
normalize a string to a 1-element list — choose reject for fail-loud consistency). RED-first test.

## SF-5 (SHOULD-FIX) — silent no-op on non-dict cache_prefix
`_selected_variant_id_from_run_state`: a parseable-but-non-dict `cache_prefix` (e.g. `"[]"`, `"123"`)
returns `None` → variant selection silently skipped, where the WRITE path
(`_apply_verdict_to_run_state` select branch) RAISES on a non-dict envelope. Align: raise
`VariantSelectionError` on a non-dict JSON envelope (a corrupted-but-parseable prefix must not silently
disable the filter). Keep `None`/absent/`""`/unparseable→None where that already matches the no-op
contract; the specific gap is **valid-JSON-but-not-a-dict**. RED-first test.

## AC2 (SHOULD-FIX) — byte-identity wording + pin
The legacy no-`gamma_settings` test pins the full emitted Gamma kwargs by equality — GOOD — but it is
an inline literal, and the receipt dict now unconditionally gains `gamma_settings`(None) +
`variant_gamma_settings`([]). Two asks: (a) correct any doc/handoff claim of "byte-identical legacy
**output**" → "Gamma **wire request** unchanged on the no-settings path; the receipt dict gains 2
additive keys"; (b) OPTIONAL but preferred — add a guard asserting the legacy receipt gains ONLY those
2 additive keys vs the prior shape (so a future unintended key is caught).

## NIT (do if cheap) — list_themes refetch
`_theme_id` and `_theme_id_for_variant` each call `list_themes()`, so a 2-variant run with explicit
per-variant themes hits it up to 3×. Beyond inefficiency, a transient second fetch could false-reject
a theme that just validated. Thread the already-fetched themes list into `_theme_id_for_variant`
instead of refetching. (Newly motivated: Gamma rate-limits — fewer calls = less throttle risk.)

## Re-T11 pass-bar (Claude will verify)
- The MF-1 RED transcript pasted; the new partial-coverage test + all prior filter tests green.
- Per-knob bad-input tests for all 7 enum/theme knobs: good / bad-raises-before-spend / structurally-
  valid-but-absent. (AC3 closed.)
- SF-3/4/5 RED-first fixtures green.
- ruff + lint-imports green; the 14 ambient contract failures unchanged (baseline-diff attested — same
  set on clean HEAD; ZERO new reds).
- Updated handoff `_codex-handoff/variant-selection-deckwide-t11-remediation-ready.md` with before/after,
  the RED transcripts, all test results, and the corrected byte-identity wording.

## Fences
Data-plane; no `block_mode_trigger_paths` touch; no new top-level payload key; no pack/manifest/lockstep.
Do NOT rework the (correct) core filter wiring, the warm-401 retry, or the stylePreset↔style emitter —
only add the guards/tests above. Live-Gamma legs remain operator-gated.
