# Reading-Path → LLM-Primary REDIRECT (operator-ratified, 2026-06-23)

**Supersedes** the geometry-grind framing of `codex-dev-prompt-p2-4b-recalibration.md` and the §4.5 party scope's "tighten geometry to ≥0.85" target. **Authority: OPERATOR DIRECTIVE (2026-06-23)** — get the app into production now at very-high quality, small scale, cost secondary; use a frontier model wherever a component needs it; defer clever cost-reducing hybrids to a later scale-up phase. This is an architecture-tier decision made by the operator (overrides the party's geometry scope; the party's overfit/honesty fences below still apply to any reported number).

## Why (evidence-backed)
Measured per-slide diagnosis (subject=built-classifier, substrate=fresh@2026-06-23): deterministic geometry is **5/5 on `split_image_text`** (a spatial question boxes can answer) but **0/6 on the `multi_column`/`card_grid`/`two_pane` family** (a *semantic* question — peers vs one-flow vs contrast — that bounding boxes cannot encode). The 0.50 macro is not a tuning gap; the hard half is likely a **capability ceiling**. The frontier-LLM catalog approach already scored **0.93** on the same task. → Stop grinding geometry; put the frontier model in the primary seat.

## The change (small, focused — speed over ceremony)
1. **LLM-primary reading-path classifier.** The authoritative `reading_path` tuple `{macro_layout × image_role × text_substructure × narration_cadence}` is produced by a **live gpt-5.5 (frontier) call** that reasons holistically over the perceived slide + catalog v1.1 — the SAME approach that hit 0.93. This becomes the authoritative producer feeding Irene Pass-2.
2. **Geometry demoted.** Keep the deterministic classifier as a CHEAP cross-check / telemetry signal only; it MUST NOT override the LLM tuple. (Retain `split_image_text` detection — geometry's one strong axis — as an optional agreement signal, not an authority.)
3. **Escalation collapses.** With LLM-primary, the S3 "escalate on ambiguity" leg is moot for macro/image_role — the LLM does the whole tuple every slide. Keep/repurpose escalation only if a cheap-path subset is later reintroduced (the cost-hybrid, deferred).
4. **Safe-degrade — NEVER hard-block a run.** If the LLM call errors after bounded retry, degrade to the plain `top_down` default tuple (observable/counted) and continue. Reading-path quality must never halt a production run; the fidelity detector + Pass-2 grounding remain the hard gates.
5. **Honesty discipline unchanged.** No mocks; live gpt-5.5; the tuple is a real model output. Every reported accuracy number still carries `(subject, substrate)` per H1–H4.

## Acceptance (lightweight — proof, not a ceremony)
- Re-run `scripts/analysis/reading_path_p2_4b_measure_fresh.py` with the LLM-primary classifier over the 14 fresh perceptions → expect primary-key in the ~0.85–0.93 band (matching the proven approach). Report the honest number, subject/substrate-tagged. **No re-label of gold.** (The party's no-peeking / logic-only / gold-hash fences still hold; here they're easy to satisfy because the classifier is the frontier model, not knobs fit to 14.)
- **A production smoke completes:** a full pipeline run on the frozen corpus (`tejal-apc-c1-m1-p2-trends`) reaches completion with reading-path-informed Pass-2 narration, reading-path safe-degrading where needed, zero hard-blocks attributable to reading-path.

## What this unblocks
The reading-path was the open calibration item gating P2 close. With LLM-primary it stops being a blocker (it's good-at-frontier-quality OR safe-degrades). → Proceed to **production runs on the frozen corpus**, harvest real failures, fix forward, and restore migration-dropped functionality iteratively (operator's "tweak/fix/add-back as we go").

## Still on the books (NOT lost — deferred, not skipped)
- **`reading-path-fresh-naive-holdout-pre-trial`** — the consumed-14 is a dev set; a fresh naive holdout is still the honest way to claim generalization once we're past first production runs.
- **Cost-hybrid (the original `multi_column`/abstaining-geometry idea)** — revisit at scale-up: geometry abstains honestly on the semantic axis, LLM owns it, geometry keeps the cheap spatial axis. Filed as the future optimization, not a launch blocker.
