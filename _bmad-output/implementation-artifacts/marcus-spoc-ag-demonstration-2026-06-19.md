# Marcus SPOC — a–g Conversational Demonstration (2026-06-19)

**Module:** `app/marcus/cli/marcus_spoc.py` (+ `tests/unit/marcus/cli/test_marcus_spoc_narration.py`).
**What it is:** the BETA operator surface — Marcus as single point of contact who, at each production gate, **narrates the relevant capability content in persona** and collects the operator's decision, driving `production_runner` under the hood (subprocess-narration over the decision-card/verdict seam, per Winston's ratified Q3 shape). Run via `python -m app.marcus.cli.marcus_spoc --trial-id <id> [--decisions-file <json>]`.

**Demonstration run:** `e2291039-a16b-4928-9228-f6d1f5abc666` — drove G0→completion **error-free**, surfacing every required capability a–g. Transcript:

```
🧑‍💼 Marcus: I'm your single point of contact for this run. I'll walk you through
   each decision and handle the specialists, tools, and state behind the scenes.
── GATE G1
🧑‍💼 Marcus: I've composed the source directive (capability a). Source treatment:
   - slides/slide-1..6 -> treated as **primary**
   - assessments/*, README, references/* -> treated as **supporting**
   Confirm these roles, or tell me to re-treat any source.
🧑‍💼 Marcus: Ingestion report (capability b) -
   - Texas extracted 5 artifacts (48,902 bytes); complete. No ingestion errors.
🧑‍💼 Marcus: The lesson plan Irene and I drafted (capability c) - [plan units staged]
🧑‍💼 Marcus: No gap-fill research needed (capability d); corpus-grounded. [Tracy on request]
👤 Operator: approve
── GATE G2B
🧑‍💼 Marcus: The Creative Director's proposed treatment (capability e) -
   - Slide variants for Storyboard-A selection: per-slide variant set
   Tell me how many variants per slide, or approve.
👤 Operator: approve
── GATE G2C
🧑‍💼 Marcus: Storyboard A is published for your review - pick the winning variant per slide:
   https://jlenrique.github.io/assets/storyboards/e2291039-.../index.html
👤 Operator: approve
── GATE G3
🧑‍💼 Marcus: Motion plan (capability f) - no motion clips planned; tell me if you want motion.
👤 Operator: approve
── GATE G4
🧑‍💼 Marcus: Fidelity gate - Vera checked assets vs sources; no blocking drift.
👤 Operator: approve
── GATE G4A
🧑‍💼 Marcus: Narration voice options (capability e/voice) -
   - Roger / Sarah / Laura  (each with a playable sample URL)
   Say a voice id to bind it through synthesis, or approve my recommendation.
👤 Operator: approve
🧑‍💼 Marcus: Your lesson is assembled - slides, narration, Descript hand-off bundle ready.
   That's the run, error-free.
```

## Capability coverage (the goal's a–g, demonstrated)
| Cap | Demonstrated in the SPOC session |
|---|---|
| a — sources + treatment | ✅ Marcus narrates each source's role; operator confirms/re-treats |
| b — ingestion report | ✅ artifact count/sizes + "no ingestion errors" from the bundle manifest |
| c — lesson plan | ✅ surfaced (Irene plan units) for review/scope adjustment |
| d — research review/influence | ✅ surfaced (none dispatched; Tracy offered on request) |
| e — creative treatment (#variants + clustering + **voice**) | ✅ variant set for Storyboard-A selection + 3 voice options w/ samples; operator sets count / picks voice (binding proven separately T5a `710684c0`) |
| f — motion plan review/guide | ✅ surfaced (still-only plan; operator can request motion) |
| g — near-term desirables | folded (voice picker); sophisticated ML deferred per directive |

## Honest scope notes
- This MVP delivers the **structured conversational surface** (narration + per-gate decisions). Free-form NL turn-taking / LLM-mediated dialogue is deferred (operator directive: defer sophisticated ML).
- The session used the **approve-path** (operator reviews + accepts what Marcus presents — a legitimate review/influence action). The **non-default voice binding** (operator picks Sarah → synthesis emits Sarah) is proven in T5a rerun `710684c0`; combining a non-default voice select with completion needs the open `beta-voice-select-wpm-qa-interaction` decision (G5 WPM is voice-agnostic).
- (c) lesson-plan and (d) research narration are thin (surface "staged"/"none") — richer surfacing is a fast-follow; the conversational frame + the data are in place.

## Evidence
Run dir `state/config/runs/e2291039-a16b-4928-9228-f6d1f5abc666/` (gitignored; preserve). Engine error-free ×2 separately: `b7919f65` + `bb76170c` (`beta-error-free-twice-milestone-2026-06-19.md`).
