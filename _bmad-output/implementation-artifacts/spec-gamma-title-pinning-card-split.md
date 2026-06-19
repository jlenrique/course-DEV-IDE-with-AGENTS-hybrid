# Spec — Gamma generation title-pinning + card-count pinning (WAVE-0 storyboard-correctness)

**Date:** 2026-06-19 · **Branch:** `trial/4-2026-06-12` · **Mode:** quick-dev (Claude-direct) + 3-lane self-review
**Surfaced by:** Trial 4 (`d7ad4dac-…`) error-pause at Gary node 07 (`gamma.export.brief-unmatched`), twice (start + recover).

## Problem
Gary's deck-export title-matcher (`materialize_exported_slide_paths_by_title`, party-ratified 2026-06-18) is a frozen, deterministic **bijective title-containment** contract. It correctly fail-louds rather than silently shifting slides. But it kept failing because the **generation** call upstream let Gamma:
- **merge/split** briefed slides (6 briefs → 5 pages, e.g. `Module-4-and-5`), orphaning briefs (`brief-unmatched`), and
- **invent page titles** (`Module-1`, `A-System-Under-Pressure`) that share no distinctive tokens with the briefed titles → nothing binds.

The matcher is correct; the generation call was under-constrained. No downstream matcher can fix titles Gamma never aligned.

## Fix (`app/specialists/gary/_act.py`)
1. **`card_split="inputTextBreaks"`** on `generate_deck(...)` — Gamma emits exactly one card per `\n---\n` input chunk; card count is pinned to the brief count (no merge/split).
2. **Title-led chunks** — new `_slide_title(slide, index)` helper is the single source for both the Gamma card heading (`_input_text` builds `# {title}\n\n{body}` chunks) and the matcher key (`expected_slots`), so heading and match-key are identical by construction.
3. **Strengthened `additional_instructions`** — preserve each section heading as the card title verbatim; one card per section; no cover/agenda/divider/summary; no merge/split; keep builder instructions + variant marker.
4. **Edge hardening** — body neutralizes any embedded `\n---\n` (now load-bearing under inputTextBreaks).

## Non-goals / preserved invariants
- Matcher logic + fail-loud guards UNCHANGED — if Gamma still misbehaves, Gary error-pauses recoverably (no silent regression path introduced).
- Probabilistic, not a guarantee: Gamma may still inject a leading cover (matcher already drops a *leading* unmatched page) or rarely defy instructions → recoverable error-pause, not a crash.

## Validation
- ruff clean; lint-imports 13 kept.
- `tests/specialists/gary/` 57 passed incl. new `test_gary_generation_pins_titles_and_card_split` (asserts cardSplit + title-leading chunks + `\n---\n` count + instruction content).
- `tests/integration/marcus/test_package_builders.py` + `tests/specialists/gary/test_gamma_title_matching.py` 26 passed.

## 3-lane self-review
- **Blind:** card_split forwards `generate_deck(**options)`→`generate(card_split=)`; matcher untouched. No silent regression.
- **Edge:** load-bearing `\n---\n` delimiter → body sanitization applied. Single-slide (no break) and missing-title fallbacks covered.
- **Acceptance:** fix at correct upstream layer; pins count + title fidelity; tests assert both.

## Follow-on (harvest)
- Variant A/B differentiation is now title-identical (titles pinned); meaningful per-slide variant *distinction* belongs to the deferred binding-variant-picker (the "big leap" for the next trial).
