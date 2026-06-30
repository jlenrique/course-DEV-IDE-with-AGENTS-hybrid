# Leg-1b — bmad-code-review (3-lane) + remediation (T11)

**3-lane adversarial review** (Blind Hunter / Edge-Case Hunter / Acceptance Auditor) on the diff (graph.py +273, 2 leaf modules, 2 test files). Acceptance Auditor: all 7 ACs ENFORCED, no overclaim, frozen neck untouched. Blind+Edge surfaced defects the green build + isolated live close-bar hid:

**MUST-FIX (all remediated RED-first):**
- M1 exception containment — malformed grounding (ValueError) / transient gpt-5 error no longer crashes Pass-2 (skip-callback silent + audit; gates still propagate).
- M2 figure-gate hole — inject + figure gate now share the gate-read canonical field; a kept callback carrying a figure absent from the CURRENT slide → DROP (block-by-omission), not a run-abort.
- M3 both-flags precedence — warm_callback rhetorical_role re-stamped after _attach_voice_direction (survives the production both-flags-on config).
- M4 delta-None on a KEPT callback → DROP (never ships unstamped/un-teethed).

**SHOULD-FIX (all remediated):** S1 07G raises only on reading-path-order-failed (missing → silent DROP) + honest docstring; S2 blank-source_text anchors filtered (caller-side, slice-1 pins intact); S3 v3-tag-in-callback → DROP.

**Result:** 10 new RED-first tests (9 failed pre-fix → 285 passed post); ruff clean; frozen `figure_tokens` neck untouched; flag-OFF byte-identical preserved.

**LIVE close-bar (real gpt-5, foreground, first-run-stands) — ALL_PASS, twice (pre + post remediation):** (1) positive grounded callback fires, anchor=c1, R7 PASS, figure gate clean; (2) real gpt-5-authored "70%" callback → real R7 + frozen neck detect percent:70 → omitted; (3) first-component → silent; (4) out-of-order refs on a fired callback → Pass2ReadingPathError. Evidence: leg1b_live_close_bar_result*.json.

**Honest scope / documented follow-ons:** numeral/figure-token facet ONLY (clinical `deferred (no lexicon)`; unsupported-concept NOT R7-enforced → Leg-4). Feature is FLAG-OFF by default. Production activation needs (NOTE#1) the orchestrator projection of `warm_callback_grounding` from Leg-1 source_point parents, and (M3) both-flags-on. AC6(ii) negation = positive-structural-contract + bag-of-words backstop; span/dep-aware upgrade + a live polarity-reversal probe → Leg-4.
