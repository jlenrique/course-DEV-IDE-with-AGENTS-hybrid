# Per-Slide Variant Selection (Storyboard A) + Irene Presenter Voice — Design + Build Spec

**Goal (operator `/goal` 2026-06-24):** Restore real **per-slide A/B selection via button-clicks on the published Storyboard A**, propagating each slide's pick downstream; fix Irene's narration to **presenter voice** (no slide-tracking regression). Prove with **two live error-free runs to Descript delivery** — Run 1 a mixed per-slide A/B pick, Run 2 the **mirror** of those same slides — with the selection **actuated via Playwright clicking the real gh-pages buttons (no faking)**. BMAD workflows + party + dev agent (NO Codex).

## Party design (5/5 converged — Winston/Sally/Caravaggio/John/Murat, no impasse)

### The loop
Gary makes A+B per slide (works) → publish a **CHOOSER page** (A/B side-by-side per slide + click-to-pick buttons + "Copy my selections") at the **G2B** variant gate, from Gary's per-slide A/B PNGs → operator/client opens the gh-pages chooser URL, **clicks each slide's pick** → page emits a human-readable code `SBA-<runtag>-1:A 2:B 3:A…` → pasted as the **G2B verdict `edit_payload`** (rides the existing select/verdict/resume channel — no server) → handler **parses + validates total per-slide coverage, FAIL-LOUD on any gap** → writes `slide_variant_selections.json` (`{slide_id: "A"|"B"}`) → **per-slide resolver replaces the deck-wide filter**, collapsing A/B → one deck *per slide* **before perception** (downstream sees a flat single-variant deck, untouched) → resolved deck published + reviewed truthfully at G2C.

### Build slices (John's order)
- **1D** — Fix the Marcus narration LIE: G2B narration points to the chooser ("pick your variant per slide here: <url>"); G2C narration reviews the **resolved** deck (drop the false "pick the winning variant per slide" claim). *Immediate.*
- **1B** — Selection schema + capture (design FIRST): `slide_variant_selections.json` contract `{slide_id: "A"|"B"}`; parse the `SBA-<tag>-N:V …` code; add G2B selectable key `slide_variant_selections`; validate.
- **1A** — Chooser page: new `storyboard_html_emitter` mode rendering A/B per slide (from `_variant_candidates` options) + click buttons + copy-code JS; publish at G2B via `storyboard_publisher`; URL into the G2B card.
- **1C** — Per-slide propagation: replace `_apply_deckwide_variant_selection` (+ `selected_variant_id`) with `_apply_per_slide_variant_selection(slides, selections)` → resolved single-variant deck.
- **Item 2** — Irene presenter persona (`irene/graph.py:85`): recast "Instructional Architect" → "senior instructor speaking to a live room"; Caravaggio's 4 rules (slide = evidence behind you, never the grammatical subject; grounding = accuracy not content; address audience + give every fact a stake; one idea spoken not a parts-inventory; **caption self-test**). Keep perception-grounding.

### Load-bearing invariant (Winston/Murat)
Before perception: **exactly one chosen variant per slide — total coverage.** `set(selections) == set(all slide_ids)`, every value ∈ {A,B}, each (slide,variant) asset exists. Partial/extra/unknown/empty → **HALT, name the offending slide_id** (never silent-default-to-A). Keyed by **slide_id, not index**. Resolver pure + idempotent.

### Test bar (Murat — RED-first)
- **Permutation test (binding):** pick A=1/3/5, B=2/4/6 → assert downstream uses that exact per-slide mix (variant-discriminating marker survives to terminal artifact). **+ mirror** (B=1/3/5) to kill position-keyed hardcodes. RED-first vs current deck-wide ("expected slide 2=B, got A").
- **Capture seam:** map round-trip deep-equality; cardinality/identity HALT tests (missing/extra/unknown/empty → raise naming the id); slide-id-keyed not index-keyed.
- **Marcus-lie governance:** capability claims need a RED-first backing test (claim→test registry idea). The G2C "per slide" claim only ships if the permutation test is green — here we move the per-slide claim to G2B (the chooser) where it's now TRUE.
- **Item 2 (subjective):** 3-tier — negative tripwire (regression guard only) + named-criteria temp-0 LLM judge (addresses-audience / asserts-a-point / **perception-grounded as separate hard axis**, cited evidence, first-run-stands) + held-out human spot-check. Honest correlate, not proof.

## Live validation (the goal's terminal condition)
Two runs on `tejal-apc-c1-m1-p2-trends`, each through to Descript-ready delivery, error-free:
- **Run 1:** Playwright clicks a mixed per-slide pick (e.g. A,B,A,B,A,B) on the live chooser URL → code → G2B verdict → resolver → completion. Verify the final deck/narration honor the per-slide mix.
- **Run 2 (mirror):** same slides flipped (B,A,B,A,B,A) → completion → honors the mirror.
Plus: Irene narration reads as presenter (judge + spot-check), slide-tracking not regressed.

## Reference (prior-app target)
`…/reviews/20260408a/C1-M1-PRES-…` is the **approved-review** storyboard (chosen deck, motion-video previews, presenter narration) — confirms presenter voice + rich-card bar. Motion preview = deferred (narrated-deck scope).
