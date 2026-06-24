# Clustering + per-sub-slide A/B → Descript — LIVE RUN WITNESS (2026-06-24)

**Terminal (b) ACHIEVED:** ONE genuine A/B-to-Descript run WITH clustering active + no ghost numbers.

**Trial:** `c2c6dcbf-5734-42d0-b525-2ea3212aa3f0` · preset production · corpus `tejal-apc-c1-m1-p2-trends` · status **completed** ("all assets delivered, Descript-ready").

## What was proven LIVE (verified on real artifacts, not code-intent)
- **Clustering active:** 6 source slides → 13 plan_units (3 dense slides chunked into head+interstitial clusters + keep-dense singletons), rendered as a 13-sub-slide deck.
- **Genuine per-sub-slide A/B selection:** A/B variant pair injected (`--gamma-settings-file variant-demo-gamma-settings.yaml`); 26 Gamma renders (A+B × 13 sub-slides); the G2B chooser published to gh-pages with **13 individually-addressable sub-slides each offering A/B**; selection actuated via **real Playwright button clicks** on the published chooser (`drive_per_slide_trial.py`, picks A,B,A,B,A,B,A,B,A,B,A,B,A) → `slide_variant_selections` recorded → G2B `select` verdict. **Clustering × per-sub-slide A/B works** (the operator's chosen integration; no Story-1.4 gap surfaced downstream).
- **Story 1.2a delta-id fix verified end-to-end:** the enrique/ElevenLabs audio leg synthesized ALL 13 segments OK (seg-01…seg-13, each with duration+cost) — no `elevenlabs.join.dropped-segments`. (The pre-fix run `52890be7` dropped all 13 here.)
- **No ghost numbers:** zero `figure-contradiction` in the run — the figure-citation gate held live across the A/B mix (B-variant figure-free slides did not produce ghost-number citations).
- **Delivered to Descript:** `exports/storyboard-c2c6dcbf-…-b` published + `.zip` + publish-receipts.

## Honesty tags
- "VO tightness" here = the run completed with cluster-aligned per-sub-slide narration segments (deterministic structural proxy: 13 narration segments ↔ 13 sub-slides). **Perceptual tightness = operator eye-read, NOT auto-claimed.**
- Reading-path numbers stay on the consumed-14 resubstitution basis; this run does NOT advance the fresh-naive-holdout generalization gate (Mary's standing dissent).
- Gamma render variance note: two earlier fresh trials hit `gamma.export.brief-unmatched` (deterministic per-render fuzzy-match miss on one sub-slide); a fresh render cleared it. Operator-raised follow-on filed: `gary-export-llm-brief-to-page-matcher` (LLM semantic matcher for the residue).
- Desmond delivery note: the final Descript-delivery node tripped a Desmond **sanctum lock** on the operator's uncommitted Desmond sanctum WIP (CAPABILITIES.md/MEMORY.md/sessions/2026-06-24.md). Per operator authorization, the WIP was temporarily set aside (backed up), the run delivered, and the WIP **restored byte-identical**. Not a clustering issue.

## Terminal-state ladder
- (d) LOCKED (Story 1.1 + T11). (c) MET (clustering re-wired + downstream verified green on a live smoke). **(b) MET (this run).** (a) = prove twice → needs a mirror run (B,A,B,A… selection). Operator's raised bar (amendment #8): 3 consecutive clean + 1 cross-deck — this is run 1 of that ladder.
