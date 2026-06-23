# Codex Dev Prompt — Reading-Path LLM-PRIMARY (operator-ratified; SHIP-oriented)

**You are Codex (T1–T10).** Claude T11 (lightweight: re-measure + production smoke + commit). **This SUPERSEDES** `codex-dev-prompt-p2-4b-recalibration.md` (geometry-grind) and the geometry delivery filed on branch `reference/codex-p2-4b-geometry-recal-2026-06-23`. Authority: `reading-path-llm-primary-redirect-2026-06-23.md` + operator directive (ship now, high quality, cost secondary, frontier model where needed).

## Goal (small, focused)
Make a **live frontier-LLM call (gpt-5.5) the PRIMARY producer of the reading-path tuple** — the same holistic "read the slide + catalog, assign the tuple" reasoning that already scored 0.93 — replacing the deterministic geometry as the authority. Deterministic geometry is demoted to a cheap cross-check/telemetry signal only. Reading-path **safe-degrades** so it can never hard-block a production run.

## Why (evidence)
Measured: geometry is 5/5 on `split_image_text` (spatial) but 0/6 on `multi_column`/`card_grid`/`two_pane` (semantic — a capability ceiling boxes can't cross). The frontier-LLM catalog approach already hit 0.93 on the same 14. Operator decision: ship with the frontier model; defer the cost-hybrid to scale-up.

## The change
1. **LLM-primary classifier.** Add a function (in/near `scripts/utilities/reading_path_classifier.py`) that, given a `PerceptionArtifact` (elements + bboxes + text + image roles) + the catalog v1.1 definitions (`reading-path-patterns-catalog.md` — load the pattern/tuple definitions as prompt context), makes ONE live **gpt-5.5** call (reuse the house `ChatOpenAI`/cascade used by `app/specialists/vision/provider.py`; do NOT invent a new client) and returns the full tuple `{macro_layout, image_role, text_substructure, narration_cadence, callout_intent}` with a short rationale per axis. This becomes the value of the authoritative `reading_path`/tuple fields on the artifact.
2. **Wire as the authoritative producer feeding Irene Pass-2** — the same consumption seam the deterministic `with_classified_reading_path` fed. Pass-2 narration keys off this tuple.
3. **Demote geometry.** Keep the deterministic classifier callable as a cheap cross-check (emit it as a separate telemetry field for later hybrid work + agreement logging), but it MUST NOT override the LLM tuple.
4. **Safe-degrade (never hard-block).** Bounded retry on the LLM call (transport/parse only — no retry-to-green on content); on exhaustion, degrade to the plain `top_down` default tuple, mark `degraded=true` (observable/counted), and continue. The fidelity detector + Pass-2 grounding remain the hard gates — reading-path never halts a run.
5. **Reuse (optional) from the reference branch:** `reference/codex-p2-4b-geometry-recal-2026-06-23` added an authoritative `dominant_image_role` field + schema to `PerceptionArtifact`. Cherry-pick that field IF it cleanly helps (the LLM can also just emit image_role directly). The geometry-PRIMARY classifier on that branch is superseded — do not adopt it.

## Honesty discipline (unchanged)
No mocks; live gpt-5.5; the tuple is a real model output. Every reported accuracy number carries `(subject, substrate)` per anti-patterns H1–H4. Gold frozen — never re-labeled.

## Acceptance (lightweight — proof, not ceremony)
1. **Re-measure:** run `scripts/analysis/reading_path_p2_4b_measure_fresh.py` (adapt it to call the LLM-primary classifier) over the 14 FROZEN fresh perceptions in `reading-path-holdout-rescan-2026-06-23/perceptions/` → report honest primary-key (expect ~0.85–0.93, matching the proven approach), subject/substrate-tagged. First-run-stands. (No knob-tuning to the 14 — the classifier is the frontier model, so overfit risk is inherently low; do NOT special-case slide_ids.)
2. **Production smoke:** a full pipeline run on the frozen corpus `course-content/courses/tejal-apc-c1-m1-p2-trends` reaches completion with reading-path-informed Pass-2 narration; reading-path safe-degrades where needed; zero hard-blocks attributable to reading-path.
3. Touched files ruff-clean; no production-substrate left half-modified (no 4-file-lockstep / pack / manifest touch — confirm at T1).

## Handoff → Claude T11
Deliver to `_bmad-output/implementation-artifacts/_codex-handoff/reading-path-llm-primary-ready-for-review.md`: the re-measure number (subject/substrate-tagged), the production-smoke result (run dir + completion status), baseline-diff attestation for any "pre-existing" failure. Claude T11 = battery + bmad-code-review (lightweight) + independent re-measure + production smoke + commit + flip.
