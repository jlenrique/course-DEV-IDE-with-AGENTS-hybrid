# callout_intent Harvest Protocol (D2 follow-on) — 2026-06-23

**Purpose:** graduate the provisional `callout_intent` speech-act axis (catalog v1.1 §2 AXIS 5) from probationary → scored, under evidence + agreement discipline. **Authority:** catalog v1.1 §2 AXIS 5 + §11 (D2); `reading-path-gap-resolution-G2-G3-2026-06-22.md` (D2 placement: optional sibling field, LLM/S3-resident, OUT of the primary key, VO mandate tested separately).
**Invariant (NEVER relaxed):** `callout_intent` stays OUT of the geometric primary key `{macro_layout × image_role}` forever — promotion only ever moves a value into the **per-axis reported vector**. A RED-first fixture pins this invariant.

## Seeded vs hypothesis values
- **Seeded (provisional):** `invite_response`, `challenge_quiz`, `directive_cta` (held-out evidence: 18_/5_/22_). `inform`/null = unmarked default (no-op).
- **Harvest hypotheses (NOT in the frozen enum):** `takeaway_imperative`, `contact` — admitted to the frozen enum ONLY if they clear the same N≥4 bar.
- **Merge-risk watch (Caravaggio):** `takeaway_imperative` vs `directive_cta` — monitored at a specific confusion-matrix cell; default collapse direction = fold `takeaway_imperative`→`directive_cta` if they confuse (carry the direction-may-flip caveat).

## Gated protocol G0–G8
- **G0 — scope freeze.** Harvest pool = the **54 working/discovery slides** (+ future corpora). The **held-out 14 are CONSUMED** (operator-confirmed in the confirm/deny round) → reserved as a frozen back-check exhibit only, NEVER harvest-N. Artifacts live in a new sibling dir `reading-path-corpus-scan/callout-intent-harvest-scan/`.
- **G1 — candidate extraction.** Run the live ≥gpt-5.5 perceiver/escalation over the pool; collect every slide carrying a callout-kind element; record candidate intent per callout. (Deterministic regex pre-flags contact/CTA cues; the label is the model's.)
- **G2 — target N.** Each value needs **N≥4 confirmed exemplars across ≥2 content genres**. Track per-value counts; a value below N≥4 stays a hypothesis (deferred), not dropped.
- **G3 — double-labeling (blind).** Labeler A = operator; Labeler B = a fresh independent ≥gpt-5.5 subagent. Blind to each other; separate files; first-pass-stands (no retry-to-green).
- **G4 — agreement floor.** Per value (one-vs-rest): raw agreement **≥0.80 AND Cohen's κ ≥0.6**; plus an overall multi-class κ; emit a committed **confusion-matrix artifact**. 
- **G5 — failure tree.** Value fails the floor → (a) **low base-rate** (too few instances) → defer/keep hypothesis; (b) **one-cell confusion** (confuses with exactly one sibling) → **merge** per the default collapse direction; (c) **diffuse confusion** (spreads across siblings) → **drop** the value.
- **G6 — VO directness mandate (separate generation track).** Author one line per surviving value (e.g. invite_response → "pose it as an invitation and leave air"). Test as a GENERATION directive with an independent judge — two bars, never one (perception-label accuracy AND generation-honors-intent are separate). Promotion requires the directness track to exist AND pass.
- **G7 — promotion gate (5, all must hold).** (1) N≥4 across ≥2 genres; (2) agreement ≥0.80 + κ≥0.6; (3) confusion-matrix shows no diffuse confusion; (4) VO directness track passes; (5) party (Murat/Caravaggio/Mary/Winston/Amelia) + operator ratify. On pass → the value enters the **per-axis reported vector** (still OUT of the primary key). Wiring into scoring is a separate downstream dispatch.
- **G8 — re-harvest trigger (HARVEST-2).** Fires when new corpora land; re-runs G1–G7 on the delta; re-validates merged/dropped values (direction-may-flip).

## Coupling
- The confirmed exemplars + VO mandates seed `[[vo-narration-layout-tracking-trained-patterns]]` (the operator's exemplar/training build).
- Bidirectional with `[[callout-intent-speech-act-axis-harvest]]` (the deferred-inventory follow-on this protocol operationalizes).
- P2-4b consumes `callout_intent` only as the probationary per-axis vector (excluded from top-1) until G7 promotion.
