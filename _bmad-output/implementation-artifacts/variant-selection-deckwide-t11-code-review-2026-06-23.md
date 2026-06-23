# Variant Selection Deckwide — T11 Code Review (2026-06-23)

Codex T1–T10 → Claude T11. Source: `codex-dev-prompt-variant-selection-deckwide.md`. Handoff:
`_codex-handoff/variant-selection-deckwide-ready-for-review.md`. **First-pass verdict: HAND BACK**
(1 MUST-FIX + SHOULD-FIX cluster). Remediation prompt: `codex-remediation-prompt-variant-selection-deckwide-t11.md`.
No party ratification (operator-authorized direct hand-back/close; clear-cut bmad-code-review output).

## ✅ re-T11 CLOSE — DONE 2026-06-23 (remediation verified)
Codex executed the correct remediation prompt; Claude re-T11 verified every item IN CODE + non-vacuous
RED-first tests. Handoff: `_codex-handoff/variant-selection-deckwide-t11-remediation-ready.md` (RED
transcript: 8 failed pre-fix → 15 passed post-fix). **All findings resolved:**
- **MF-1** ✅ `_apply_deckwide_variant_selection` captures `original_slide_ids` + raises on `missing`
  (enforces ≥1 per original slide alongside the ≤1 duplicate guard = exactly-one-per-original-slide).
- **SF-1/2** ✅ `_validate_enum_setting` per-knob `omit_sentinels` (amount→{…,balanced}, text_mode→{…,
  generate}, image_model→{…,auto}; dimensions/language/source/stylePreset→{"",default}) — invalid
  values (dimensions="auto" etc.) now fail-loud before spend; legacy omit preserved at emit time.
- **SF-3** ✅ custom requires image_style · **SF-4** ✅ non-list keywords rejected · **SF-5** ✅ non-dict
  cache_prefix raises · **NIT-2** ✅ `_theme_id_for_variant` reuses the themes window · **AC3** ✅
  per-knob bad-input tests (gary 12→15, all assert `generate_calls == []`).
- **Battery:** 67 focused passed / 0 failed; lint-imports 15 kept; ruff clean; contracts 14 ambient
  (same set, 0 new reds — baseline-diff satisfied). Byte-identity wording corrected (Gamma wire request
  unchanged on legacy path; receipt dict +2 additive keys). Fences clean (no pack/manifest/lockstep).
- **VERDICT: CLOSE / done.** Committed; substrate ready. The 2-variant trial now waits only on the
  interim variant wiring (inject A/B treatment pair into the directive + G2B select) per the approved plan.

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

## Live B gate — ✅ CLEARED 2026-06-23
B live-201 + eye-check SATISFIED. After the rate window recovered, A and B rendered cleanly via two
spaced `/generations` calls (proving Gamma is production-viable; the earlier 401 was a self-inflicted
debug-burst throttle that self-cleared in ~20 min — NOT an account/eligibility problem). B's
first-exercised knobs are live-proven: `stylePreset: lineArt` + `model: recraft-v3-svg` + theme
`e8tz1vxb9v1urqp` → 201 + completed. **Operator eye-check CONFIRMED: A (standard Tejal) and B
(Blueprint Editorial / Tejal-B) are tastefully, distinctly different + on-brand.** Evidence:
A `https://gamma.app/docs/0i06u5ee4lsihss`, B `https://gamma.app/docs/53kgsscsltu962p`. So the
2-variant trial is no longer B-gate-blocked — it now waits only on the T11 remediation (MF-1 + cluster)
landing + re-T11. Single-variant trial unaffected.

**Follow-on noted (operator 2026-06-23):** B slides' smallest font reads too small. Font/typography is
NOT an API parameter (Gamma docs: theme-owned, editable only in the web editor) — fix is on the B theme
(`e8tz1vxb9v1urqp`) typography scale, OR (if the small text is baked into the line-art image, not card
typography) an `additionalInstructions` legibility nudge for the image model. Filed:
`gamma-b-theme-font-legibility`.
