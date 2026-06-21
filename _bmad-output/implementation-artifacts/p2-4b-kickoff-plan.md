# P2-4b Kickoff Plan — Slide-Image-Tracking VO Narration: functionality + reliability

**Status:** READY TO ENACT next session. **Authored:** 2026-06-21 (P2 arc wrapup). **Branch:** `fidelity-perception-arc-2026-06-19`.
**What this closes:** the LAST P2 story — reading-path repertoire growth + real-slide scan-order conformance (the "narration tracks the slide's layout, reliably" capability). Filed: `deferred-inventory.md::p2-4b-reading-path-repertoire-and-conformance-corpus`.
**Predecessor state:** P2-1/2/3/4a CLOSED; disaster grounding-regression STRUCK (AC-6 live strike fired). P2-4a shipped the reading-path MACHINERY (classifier + fail-loud verify-node + 7-pattern lockstep). P2-4b is the CALIBRATION + reliability leg.

---

## The single blocking input (operator-derived — cannot be machine-generated)

A **labeled scan-order held-out corpus** — the ground truth the reliability claim is graded against. Per-slide, the operator provides:

| Field | What the operator provides | Why |
|---|---|---|
| **The slide** | which deck + slide id (Claude renders/pulls the PNG) | the artifact narrated |
| **Expected scan order** | the operator's ordering of the slide's perceived elements — the sequence narration should follow | the held-out label the classifier is graded against |
| **Pattern (optional)** | which reading pattern, if obvious (Z / F / center-out / top-down / multi-column / grid / sequence-numbered) | trains/validates the classifier |

**Quantities (minimum for a non-vacuous test):**
- **8–10 real slides**, **disjoint from any tuning fixture** (Claude guarantees disjointness).
- **≥1 "known-wrong-default" slide** — naive top-to-bottom reading is WRONG and the operator states the correct order. **This is the anti-vacuity anchor** (Murat): without it, the test can pass while the classifier is confidently wrong.

**Validity rule (binding):** the expected-order labels must NOT be pre-filled from the classifier-under-test (self-fulfilling). Claude drafts from a NEUTRAL source (raw element list / a different heuristic) or leaves blank; the operator supplies the judgment.

## Two operator decisions

1. **Which deck.** Frozen corpus `course-content/courses/tejal-apc-c1-m1-p2-trends/` is only **6 slides** — thin for an 8–10 held-out set. Either (a) supplement with a few more slides, or (b) point at a richer deck the operator will actually narrate.
2. **Conformance bar + repertoire growth.** (a) Confirm the **≥80%** scan-order-match threshold (or set another). (b) Whether to add **`triptych`** + **`image-dominant-first`** patterns now — they land ONLY if the operator's corpus shows the existing 7 genuinely mis-fit real slides (evidence-gated; else stay at 7, warning-severity first per Mary).

---

## IMMEDIATE NEXT ACTION next session (Claude, before asking the operator for anything)

**Build the labeling kit** so the operator's part is ~1 hour of pure judgment:
1. Render/pull the chosen deck's slides to PNG.
2. Run the (committed) vision perception over them → extract each slide's perceived elements + positions.
3. Generate a fill-in template per slide (elements pre-listed with positions; order field BLANK or neutral-drafted, never classifier-drafted) for the operator to drag into reading order + flag the wrong-default slide.
4. Hand the kit to the operator. (This is the "synthesized exemplary examples" hour the operator flagged in `vo-narration-layout-tracking-trained-patterns`.)

## What Claude does once the operator returns the labeled corpus (no further operator input)

1. Freeze the labels as the held-out fixture; wire FR17/FR18 accuracy against them; finalize the operator-gated **AC-9** ≥80% bar.
2. Land the **two deferred reliability fixes** safely (they need the operator's keying ground truth to avoid false alarms) — both are named P2-4b riders in the inventory:
   - **conformance keying-contract pin** — so a mis-keyed narration **fails loud** instead of silently passing (closes Murat's named-dissent hole; RED-first fixture required).
   - **ordinal-gate calibration** — so prose like "first… then…" stops mis-classifying `sequence_numbered`.
3. Add any justified new patterns (triptych / image-dominant-first) at warning-severity first.
4. Run the **NEW CYCLE** for P2-4b: party-mode green-light → Codex T1–T10 → Claude T11 close → strike the calibration riders → P2 epic retrospective.

## Reliability confirmation (recommended, optional — operator go-ahead only)

After the code lands, Claude runs a **live trial over the operator's deck** (same pattern as the AC-6 strike: fresh independent subagent, committed detector as judge, raw verdict, first-run-stands, no retry-to-green) to prove end-to-end that real narration tracks the real slide's scan order in production. Cost is not a constraint per operator preference; just needs a yes.

---

## Definition of done (P2-4b → P2 arc fully closed)

- Held-out scan-order corpus committed (operator-labeled, disjoint, ≥1 wrong-default).
- Classifier accuracy ≥ the ratified bar on the held-out set; FR18 verify-node enforces it fail-loud.
- The two reliability riders fixed (keying-contract + ordinal-gate), RED-first.
- New patterns added iff evidence-justified.
- (Optional) live-trial reliability confirmation green.
- Strike the P2-4b inventory entry + the combined-arc "last asterisk"; P2 epic retrospective.

**Bottom line:** one operator artifact (the 8–10-slide labeled scan-order set + ≥1 wrong-default) + two decisions (deck, ≥80%/repertoire) unblock everything. Next session opens by building the labeling kit so the operator's hour is spent only on judgment.
