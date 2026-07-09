# S8 Close Letter — Claim Envelope (Quinn synthesis) — 2026-07-08

## Status line (binding)

**`S8 CLOSED`** — not `S8 COMPLETE` (end-to-end), not “still open.”

## Claim envelope (verbatim)

Composed HIL start proven (compose → G0 edit/confirm → G0E/G0R/G1 variety);
AFK HIL = authorized real HIL. Full terminal walk not claimed — blocked at
known `gamma.export.brief-unmatched` (recover same). Out of S8: no production
patch for proof flake.

## Party record

| Seat | Initial vote | After Quinn synthesis |
| --- | --- | --- |
| John (PM) | A (COMPLETE + riders) | Accept CLOSED + riders (substance of A) |
| Winston (Arch) | C (narrow) | Accept CLOSED with fenced claim |
| Amelia (Dev) | C | Accept CLOSED with claim boundary |
| Paige (Docs) | C | Accept CLOSED with anti-overclaim docs |
| Dr. Quinn | Synthesis D | **Adopted** — lexical A-vs-C resolved |

Impasse chain: A vs C → Quinn synthesis → no John tiebreak needed.

## What closed inside S8

1. First selection-edge runtime slice (`282ea82f`).
2. Planning-input selection contract (`f69ed471`).
3. Lesson-plan / workflow-direction prose (`22d63e9d`).
4. Full-close preflight artifact (`455a4a2e`).
5. Tejal Part-4 corpus prep + checker + ratification + wrapper (`205dc513`).
6. Local Marcus-SPOC AFK HIL composed-start proof on Part-4:
   - Evidence: `_bmad-output/implementation-artifacts/evidence/s8-tejal-p4-hil-liveproof-20260708T213400/`
   - Trial: `9b6dc48b-031a-4b02-870c-ab7f76047c8d`
   - No `--auto-confirm-directive`; no `--allow-offline-cost-report`
   - G0: edit → confirm; G0E/G0R approve; G1 edit-inspect
   - Bundle: `narrated-deck-with-workbook`
   - Stop: `gamma.export.brief-unmatched` at Gary node 07; recover1 same after 3 auto-retries

## Explicit non-claims

- Not a full walk to `completed` / workbook terminal sidecar.
- Not `production_clone_launch_evidence: true` (start stamped
  `registered-offline` / `skipped-no-langsmith-env` despite keys — secondary).
- Not a Gamma matcher product fix inside S8.
- Not HAI/PHS ingestion, LO ratification UX, projector families, Batch LLM.

## Named post-S8 gate (immediate)

1. **`s8-followon-terminal-composed-walk`** — **Gary-clear half MET 2026-07-09**
   (trial `62308889-3d83-4c54-a3ca-24e6b3e71c3c`; evidence
   `_bmad-output/implementation-artifacts/evidence/s8-tejal-p4-terminal-walk-20260709T001441/`).
   Product fix `spec-gamma-title-residue-cover-drop.md` @ `8f6e861c` live-bound
   `A_slide-01.png`…`05` (no `brief-unmatched`). Walk then paused at
   `irene.pass2.figure-contradiction` — **not** end-to-end COMPLETE.
2. **`irene-pass2-figure-contradiction-s8-p4`** — next product gate (party
   2026-07-09 consensus B: keep S8 CLOSED; residue CLOSED as product work).
3. Triage **`langsmith-start-receipt-offline-stamp`** (keys present; receipt
   says skipped; cost report still has smith URL).
4. Standing deferred: `workbook-learner-ready-prose-uplift`,
   `g0-enrichment-flag-retirement`, `research-dispatch-flag-retirement`,
   real HAI/PHS ingestion, LO ratification, course/SME routing, Batch LLM.

## Amendment 2026-07-09 (residue fix + Gary-clear; S8 still CLOSED)

Operator corrected that title-residue/cover-drop was immediate work (not
deferred). Shipped + live-proved; party (Winston/Amelia/John) voted **B**:
do **not** promote to S8 COMPLETE while Irene figure-contradiction remains.
Matcher product claim in “Explicit non-claims” above is superseded for the
residue/lone-PNG paths only — those are CLOSED product work outside the
original S8 claim envelope.

## Operator authority notes

Operator authorized AFK HIL runner (scripted `confirm_fn` + `OperatorVerdict`
loop as `juanl`) for authentic E2E while AFK — same class as S6/S7 ACL
liveproof drivers. That satisfies the “real HIL verdicts” bar under this
authorization; it does not authorize silent `--auto-confirm-directive`.
