# 35.7 RE-WITNESS (post F-E2E-1 + F-E2E-2 fixes) — 2026-07-12

Trial: 31ff847c-78c3-4029-b554-ed34baaf7fc6 · corpus tejal-c1m1-p4-assessments-bridge · narrated-deck-with-workbook · realtime · --hud on. Fresh paid run with BOTH HUD fixes (F-E2E-1 ffc97f45, F-E2E-2 ed9d1c25).

## RESULT: reached `completed` ($0.38, terminal_gate G4A, silent_bypass_events 0, deck+motion+workbook, motion/slide-01.mp4 1.33MB).

## F-E2E-1 (gate paste-command) — PROVEN LIVE END-TO-END, ALL 8 GATES
Every gate was driven by reading the HUD's OWN verbatim `next_action.command` from the projection and executing it verbatim (a true operator paste). Results (all `PASTE exit=0`, accepted first try, NO card_missing):
- G0E ✓ (trial resume ...) → G0R
- G0R ✓ → G1
- G1  ✓ → G2B (after the research figure-normalizer fix cleared node 08)
- G2B ✓ → G2C
- G2C ✓ → G3
- G3  ✓ → G4
- G4  ✓ → G4A
- G4A ✓ → COMPLETED
The HUD's rendered gate command is now `trial resume --trial-id ... --gate-id ... --verb approve --card-id ... --decision-card-digest ... --operator-id ...` and works when pasted from a fresh shell. JTBD#1 restored.

## F-E2E-2 (ambient instruments) — PROVEN LIVE, EVERY GATE + COMPLETED
health/specialists/modalities/trace all NON-NULL at every pause and at completed. Observed: health 3 tiles; specialists roster grew 1→3 through the walk; modalities.mode=realtime; trace events accumulated (7→16→...). The in-flight lifecycle witness warning no longer fires. FR7/FR8/FR9/FR10 restored.

## Deliverables render (completed) — deliverables section populated (components + $0.38 + export_paths); FR16 works.
## Zero-lie held throughout (projection status == run.json at every checkpoint).

## Two production bugs fixed on the way (proofing-run value; NOT HUD):
- vision realtime prompt_cache_key/model_kwargs (247cf72d) — first run, node 07G.
- research _normalize_figure crash on DOI/retrieval tokens ending in 'x' — this run, node 08.

## Fence satisfied: the party's operator-readiness gate was "F-E2E-1 fixed AND re-witnessed end-to-end (paste→accepted first try) + F-E2E-2 emits non-empty." BOTH met, on a COMPLETED run, all 8 gates paste-driven.

## Honesty disclosures (contrarian claim-check, Level + Splinter — non-blocking)
- **Deliverables are 2-of-3 CONSUMABLE, not 3.** deck (23 PNGs) + motion (slide-01.mp4) are real files; the `workbook` component flag is true but `workbook_producer` emitted "Emitted artifacts: none" (cache payload only) — NO workbook.md/.docx. This is a pre-existing PRODUCTION/pipeline gap (filed F-E2E-4), NOT a HUD defect; the HUD honestly renders the component flags it's given.
- **Gate-paused projection snapshot debt:** only the `completed` re-witness projection JSON was saved (`rewitness-projection-completed.json`; next_action null, correct). The intermediate `projection-*.json` on disk are STALE originals from trial 69338610 (old `gate decide` form). The new `trial resume` command shape is proven by: `next_action.py:72`, the G0E/G0R captured commands (rewitness-gate-commands.txt), and 8 clean `card_missing`-free paste-exit-0 transitions — evidence via behavior+code, a notch below a saved gate-snapshot. Debt: capture a gate-paused re-witness projection + promote to L2 golden on the next gate-pausing run.
- **Production fix commits (corrected):** vision = 247cf72d; research figure-normalizer = 5ace59f7.
