# P5 directed-voice S6 — LIVE enrichment-consumption evidence (20260628T000300Z)

Real live-enriched card: `tests/fixtures/p5_workbook_corpus/live_enriched_result_card.json` (corpus_fingerprint=ff1bc965ce63, model_id=marcus, 22 components, 9 annotations).

## Consumer A — narration role-derived voice (per slide, from real roles)

- Slide 1: role(s)=['synthesis'] -> voice_direction={'emotional_tone': 'reflective', 'pace': 'slower', 'energy': 'low'} (pace GUARANTEED).
- Slide 6: role(s)=['worked_example'] -> voice_direction={'emotional_tone': 'neutral', 'pace': 'slower', 'energy': 'medium'} (pace GUARANTEED).

Per-segment emitted voice_direction (real annotation pass):
  - seg-01 (slide-01): pace=slower, emotional_tone=reflective, source=role-derived
  - seg-02 (slide-02): pace=neutral, emotional_tone=neutral, source=cd-authored
  - seg-03 (slide-03): pace=neutral, emotional_tone=neutral, source=cd-authored
  - seg-06 (slide-06): pace=slower, emotional_tone=neutral, source=role-derived

DIFFERENTIATION (pace): {'seg-01': 'slower', 'seg-02': 'neutral', 'seg-03': 'neutral', 'seg-06': 'slower'} — matched slides (synthesis/worked_example) read SLOWER; unmatched slides stay neutral.

## Consumer B — Gary deck directive hint (from real LOs/roles)

Enrichment hint (routed ONLY into additional_instructions):
```
[g0-enrichment] Pedagogical context for slide design (do not restate verbatim). Learning objectives: lo-g0-001: Define the innovation mindset and identify common misconceptions about it. | lo-g0-002: Analyze how psychological safety and fixed/growth mindsets affect team performance, patient safety, and innovation. | lo-g0-003: Apply the Intelligent Failure framework to distinguish between blameworthy and praiseworthy failures in clinical settings. | lo-g0-004: Evaluate your personal innovation mindset, goals, and environment using a structured SWOT analysis. | lo-g0-005: Create an initial innovation portfolio sourced from experience, goals, and daily clinical observation. | lo-g0-006: Quantify the estimated cost and proportion of waste in the US health care system using published data. | lo-g0-007: Identify bureaucratic tasks as a leading driver of physician burnout based on recent reports. | lo-g0-008: Describe the shift from sickcare to proactive, population-focused healthcare models and its economic drivers. | lo-g0-009: Articulate why healthcare is at an inflection point requiring new models of leadership and innovation. | lo-g0-010: Describe the scale of US administrative heal
```

Sentinel LO `lo-g0-001` statement present VERBATIM in the variant-A directive: True
Sentinel ABSENT from the preserve-mode card body (_input_text): True
Sentinel ABSENT from the Studio lock prompt: True

## Live Gamma render (confirmation, NOT a deterministic gate — MUR-5)

Dispatching a 2-card deck (text_mode=preserve) with the enrichment-shaped additional_instructions ...
generation_id=GAyK0cUFhYeRwy2H0fo9W
status=completed  exportUrl=present
exportUrl: https://assets.api.gamma.app/export/image/hvczp6q993ag50c/ee8f1ea8aeb7108feb7de00f5bcd3b75/Healthcare-Waste.zip

L2 source-fidelity numeric audit (GARY-A5) over the rendered/briefed slice:
  status=AUDIT drift_rate=0.0 source_derived=3 unsourced_numeric=0

LIVE RENDER OUTCOME: RENDERED

HONEST FRAMING (MUR-5): the directive SENT to Gamma is enrichment-shaped, byte-deterministically (proven above + in the offline suite); the live render is a CONSUMPTION confirmation, not a claim that the deck deterministically changes.

---

## ADDENDUM — EDGE-1 divergence guard (post-code-review; deterministic, NO new API spend)

bmad-code-review EDGE-1 found the source↔final slide ordinal spaces differ under Pass-1 clustering/drop/reorder. A divergence guard now applies role seeds ONLY when the card's source-slide-ordinal set equals the final deck's slide-ordinal set; otherwise it FAILS OPEN (neutral built-in), never a mis-seed. Re-verified deterministically over the SAME real card (no Gamma/ElevenLabs call):

- Card source-slide ordinals: [1, 3, 6]; seedable by_slide: ['1', '6'] (slide 1 synthesis, slide 6 worked_example; slide 3 ambiguous→no seed).
- ALIGNED deck (slides [1, 3, 6]): seeds APPLY → ['seg-01', 'seg-06'] (seg on slide-01 + slide-06 get role-derived slower pacing).
- CLUSTERED deck (11 renumbered slides): seeds = None → FAIL OPEN (no mis-seed).
- The prior addendum-free harness deck (slides [1,2,3,6]) now also FAILS OPEN under the guard: seeds = None (its set ≠ the card's [1, 3, 6]); the earlier Consumer-A demo reflected pre-guard behavior on a non-aligned synthetic deck.

The live GAMMA render (generation_id=GAyK0cUFhYeRwy2H0fo9W, drift_rate=0.0) and the Consumer-B enriched directive (sentinel LO verbatim, firewall) are UNAFFECTED by EDGE-1 and STAND. Durable content-grounded join filed as `p5-s2-role-seed-robust-source-to-final-slide-linkage`.

