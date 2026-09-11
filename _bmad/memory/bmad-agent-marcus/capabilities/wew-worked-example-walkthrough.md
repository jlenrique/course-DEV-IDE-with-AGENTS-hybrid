---
name: worked-example walkthrough video
code: WEW
description: Orchestrate a faculty-seminar assignment walkthrough as a visual-led narrated slide lesson (the PHS 620 W03 Box v02 pattern).
---

# WEW — Worked-example walkthrough video

Proven on `LP-PHS620-W03-BOXV02` (2026-09-11). Ship artifact = Descript **Narrated Slide Lesson**. Conversation-space is fine for this family; do not invent an engine `production_run_id` unless the operator asks for a tracked trial.

## When to invoke

The operator wants another video **like this one**: a recorded stand-in that walks a design task / assignment / blueprint with a named case, not a text-led lecture deck.

Trigger phrases: “another walkthrough like Week 3,” “worked example walk-thru,” “Alignment Studio style,” “Box brief to Descript.”

Do **not** invoke for Tejal-style text-led cards, workbook-only jobs, or motion-first lessons unless the operator explicitly mixes those in.

## Inputs

Ask, one at a time:

1. Source pack (Box folder or local copy) — treat a finished storyboard + script as a **production brief**, not a sketch.
2. Settings: tracked vs ad-hoc; quality (default **production** if they intend to ship).
3. Whether Gate 2M / workbook / Canvas are in scope this session (default **held** until named).

Canvas is the check when a Box extract looks thin (LOs, discussion title, due dates).

## Pairing locks (defaults until the operator changes them)

These are the Box v02 locks that made the lesson work. Re-confirm, do not silently drop.

| # | Lock | Box v02 value |
|---|------|----------------|
| 1 | Experience | Visual-led. **Image is the slide.** |
| 2 | Look | `hil-2026-apc-studio-image-card` / Studio template `g_nv5q4da69qiiu8q`. Two rolls, **same style**, not two styles. |
| 3 | Photoreal | Forbidden. Illustration / diagram / graphic only. |
| 4 | Module LOs | **Off-slide.** Inform the week job; do not print the five bullets or case `LO-n` on the image. |
| 5 | Card count | Target **17–18** from a ~12-beat assignment map. Do not invent a thirteenth teaching beat. |
| 6 | Clusters | Keep the instructional clusters that carry the walkthrough (alignment, criteria/safety, sequenced phases). **No components interstitial** — four jobs stay on one sparse parent. Register: **at most one** interstitial. |
| 7 | Interstitials | Subtractive / low narration. **No new concepts.** Quality fail-closed on **Vera** (G4-18), not spoken-bridge word lists. |
| 8 | Case | One continuous hypothetical (Maya / CHW on the donor). Through-line, not a cameo. |
| 9 | VO persona | Colleague / supportive coach. Linked transitions. Coverage + on-screen tracking. No poster stacks. |
| 10 | Voice slate | American-only until further notice: Marc, **Matilda**, Chris. No British / Spanish / international accents. |
| 11 | TTS method | Synthesize **ordinary v2 and theatrical `eleven_v3`** into separate folders. Operator A/B **before** Descript. Canonical words stay tag-free; tags are delivery only. Donor chose theatrical Matilda throughout; populated roles were `warm_callback` / `contrast_emphasis` (`[warm]` / `[slow]` only). |
| 12 | Timing | Stay inside the brief envelope (donor ≤15:00). No due date on the recording. |
| 13 | Motion / LMS | Gate 2M, Kira, workbook ship, Canvas — **held** unless named. |

## Procedure

1. **Inventory the pack** as a numbered table (Marcus). Do not dispatch Texas unless retrieval is actually missing.
2. **Live Irene Pass 1.** Working-paper folders are not Irene. Envelope: pairing constraints above; Irene does not write VO; do not lock a Gamma template in Pass 1.
3. **Gate 1** on the live pairing. Paginate. Numbered rows.
4. **Writers → Gary** two-roll A/B, same Studio look, no-photoreal steer in the studio prompt.
5. **Gate 2 stills** per card. Do not flatten to “all B because B won often.” Donor mix: `BBBBBAAAAAABBAABAB`.
6. **Irene Pass 2 after winners.** Colleague-coach. Do not Cursor-author VO. Refresh Storyboard B from the **Enrique-bound** script (stale first-look B lies). Pass 2 “First / First / First” authoring rule is still **deferred** — catch it on Storyboard B, do not invent a patch unless asked.
7. **Gate 3 / Storyboard B** with live narration. Operator approves the board before Enrique is final.
8. **Enrique.** Ordinary + theatrical on disk. Operator picks. Promote the winner to `assembly-bundle/`. Archive the other.
9. **Quinn-R precomp.** WPM (or similar) fails may be **operator-waived**; write a receipt. Do not silently ignore.
10. **Compositor → Descript-named pack → Desmond builder.** After Underlord, attest the composition whose **duration matches expected audio**, never `compositions[0]` (often a dur=0 default).
11. **Stop** when the operator confirms the Narrated Slide Lesson in Descript. Do not auto-open 2M / Kira / Canvas.

## Outputs / artifacts

- Bundle under `course-content/staging/` (gitignored). Copy the bundle if the next session is another machine.
- Gate receipts, authorized storyboard, segment manifest, assembly-bundle, Descript project URL.
- This capability file stays the **tracked** recipe; pairing media does not go to git.

## Gates / checkpoints

Gate 1 (pairing) → Gate 2 (stills) → Storyboard B / Gate 3 (VO) → Descript confirm. Gate 2M only if named.

## Examples

**Donor:** PHS 620 Module 03 recorded Alignment Studio. Pairing `LP-PHS620-W03-BOXV02`. Descript https://web.descript.com/79ba51c2-cdf7-4513-8499-702b39ff7a63 (composition **Narrated Slide Lesson**, ~580.8s). Storyboard B2 https://jlenrique.github.io/assets/storyboards/PHS620-W03-BOXV02-STUDIOAB-B2/index.html. Local bundle (this clone only): `course-content/staging/tracked/source-bundles/phs-620-w03-box-v02-20260910/`.

**Do not confuse with:** parked remake-v2 at `.../phs-620-w03-recorded-20260909/remake-v2/` (8-slide donor, VO never finally accepted).
