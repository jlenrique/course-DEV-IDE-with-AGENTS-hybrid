# Variant Selection Deckwide — T11 Code Review (2026-06-23)

Codex T1–T10 → Claude T11. Source: `codex-dev-prompt-variant-selection-deckwide.md`. Handoff:
`_codex-handoff/variant-selection-deckwide-ready-for-review.md`. **Verdict: HAND BACK** (1 MUST-FIX +
SHOULD-FIX cluster). Remediation prompt: `codex-remediation-prompt-variant-selection-deckwide-t11.md`.
No party ratification (operator-authorized direct hand-back; clear-cut bmad-code-review output).

## Battery / attestation (Claude-run)
- Focused suites green (56 + broader 409 passed); lint-imports 15 kept; ruff clean on touched files.
- **Baseline-diff attested:** 14 `tests/contracts/` failures are the documented ambient severance
  path-pins (`ambient-contract-test-suite-debt`) — IDENTICAL set on clean HEAD with Codex changes
  stashed. **Zero new reds.**

## 3-layer bmad-code-review (Blind / Edge / Acceptance)
**Core mechanism CORRECT (Blind Hunter):** filter reads `selected_variant_id` from the same
`cache_prefix` the G2B select-verb merge writes (verified the merge runs before the walk); idempotent
across resumes; `output_digest` recompute is mandatory (`SpecialistContribution._enforce_output_digest`
rejects a stale digest); warm-401 retry armed/bounded/selective on all 5 sub-questions. No correctness
MUST-FIX. ACs 1/4/5/6 ENFORCED with non-vacuous tests (Acceptance Auditor).

### Findings
- **MF-1 (MUST-FIX) — partial-coverage short deck.** `_apply_deckwide_variant_selection` enforces
  "≤1 row per surviving slide," never "exactly 1 per ORIGINAL slide" → a slide present only in the
  non-selected variant is silently dropped. Gap vs binding Winston-A1 ("exactly one, not at most one").
  Latent (normal runs cover every slide in both variants); fail-loud invariant exists to catch the
  abnormal case. Fix: assert post-filter slide_id set == pre-filter set.
- **SF-1/SF-2 — validator sentinel-leak.** `_validate_enum_setting` skips `{"",default,auto,balanced}`
  globally → `dimensions="auto"`/`language="balanced"`/`text_mode="auto"`/`image_model="balanced"`
  bypass validation and reach the API (violates "bad raises before spend"). Per-knob sentinels.
- **SF-3** custom-preset-without-style emits bare `{stylePreset:custom}`. **SF-4** non-list `keywords`
  silently stringified+dropped. **SF-5** `_selected_variant_id_from_run_state` returns None (silent
  no-op) on parseable-but-non-dict cache_prefix where the write path raises.
- **AC2 (WEAK→SHOULD)** legacy payload pinned by inline literal, not a pre-change golden (Gamma WIRE
  request IS unchanged on the no-settings path; receipt dict gains 2 additive keys — correct the
  "byte-identical output" wording). **AC3 (WEAK→SHOULD)** bad-input no-spend test only for amount+theme;
  6 other enum knobs untested (same helper). Closes alongside SF-1.
- **NITs:** `or "A"` dispatch_variant default (by-design, consistent w/ `_variant_candidates`);
  `list_themes()` re-fetched 2–3×/run.

## Follow-on filed
`gamma-ratelimit-header-aware-throttle` — Gamma exposes `x-ratelimit-{remaining}-{burst,,-daily}`
headers (developers.gamma.app); the proactive fix for the 401-throttle is reading them to self-throttle,
beyond Codex's reactive warm-401 retry. Non-blocking enhancement.

## Live B gate
B live-201 + eye-check render still pending Gamma rate-window recovery (Claude's ~15 debug generations
exhausted the API-generation allowance; needs a longer cooldown). Remains the named blocking gate before
any 2-variant trial (Murat #3 / Mary). Single-variant trial unaffected.
