# Cycle-6 content review — operator-led walkthrough

**Run:** `f8da20ae-3ed7-44b1-a054-794b0c5e09a0` · lesson `tejal-apc-c1-m1-p2-trends` (APC C1·M1·P2 — macro trends in healthcare) · 6 slides / 6 narration segments.
**Purpose:** Operator content review = the gating input for the BLOCKED WAVE-0 storyboard-correctness slice. Output is a consolidated glitch list that anchors the storyboard-correctness dispatch.
**Started:** 2026-06-17 · **Reviewer:** operator (Juan) · **Facilitator:** Claude (Opus 4.8)
**Status:** IN PROGRESS

## How to pause / resume
- Say **"pause"** (or just stop) at any moment — progress is saved to this file after every captured response.
- To resume (same session or days later, even cold): reopen this file, read the `▶ RESUME HERE` marker, and we continue from there.
- Controls during the walkthrough: **"next"** (advance), **"back"**, **"skip"** (mark step skipped), **"jump to <step>"**, **"pause"**, **"done for now"**.

## Artifacts under review
| Artifact | Path / URL |
|---|---|
| Storyboard A (visual deck) | `…/exports/storyboard-A-pack/storyboard/` · online: https://jlenrique.github.io/assets/storyboards/f8da20ae-3ed7-44b1-a054-794b0c5e09a0/index.html |
| Storyboard B (A + Pass-2 narration overlay) | `…/exports/storyboard-B-pack/storyboard/` · online: https://jlenrique.github.io/assets/storyboards/f8da20ae-3ed7-44b1-a054-794b0c5e09a0-b/index.html |
| Storyboard-B segment manifest (Glitch #1 suspect) | `…/exports/segment-manifest-storyboard-b.yaml` |
| Gary slides (6) | `…/exports/gary/gary_slide_01..06.png` |
| Narration audio + captions | `…/enrique-narration/assembly-bundle/audio/seg-01..06.mp3` · `…/captions/` |
| Yardstick | `…/directive.yaml`, `…/irene-pass1.md`, decision cards G1/G2C/G3/G4 |

(`…` = `state/config/runs/f8da20ae-3ed7-44b1-a054-794b0c5e09a0`)

## Proposed review map
1. **Orientation / yardstick** — what this lesson was supposed to be; set the bar for "correct." ◀ current
2. **Storyboard A — deck overview** — 6-slide structure, completeness, blank fields.
3. **Storyboard A — slide-by-slide** (1→6) — visual / title / content correctness.
4. **Storyboard B — overview** — the narration overlay; home of known Glitch #1.
5. **Storyboard B — per-slide VO↔slide sync** (1→6) — does each slide's narration match its slide? (Glitch #1 anchor at slide 1.)
6. **Audio** (optional) — seg-01..06 vs captions / WPM feel.
7. **Wrap** — consolidate the glitch list; route to the storyboard-correctness story.

(Order is adjustable — operator may reorder/skip at Step 1.)

---

## Known-going-in
- **Glitch #1 (operator-reported 2026-06-12):** Storyboard B VO for slide 1 narrates slide 2's illustrations and references things on slide 1 that exist nowhere (broadly on-theme). Suspected `b-manifest-join-lossiness` (`_write_segment_manifest_for_b` joins each delta to its FIRST perception_source; `text_by_id.get(id, "")` publishes silently-empty on id mismatch). To be confirmed/expanded in Step 5.

---

## GOVERNING BAR (set at Step 1, applies to every judgment below)
**Production fidelity ONLY.** The question for every artifact is: *did the app + its agents faithfully assemble what they were instructed to build — correct slides, correct narration, correct sync, nothing blank/dropped/desynced — and is the wiring robust?* Pedagogical quality, content variety, and validation-procedure rigor are explicitly OUT OF SCOPE here — those are the agents' responsibility, to be refined/educated/expanded in a later pass. A "glitch" = a wiring/assembly/fidelity defect, NOT a quality opinion.

## Captured responses
_(appended after each step; verbatim operator responses)_

### Step 1 — Orientation / yardstick — DONE (2026-06-17)
**Q1 (bar for correct):** Operator: *"We are looking for production fidelity now. the app and its agents are responsible for pedagogical quality and for quality reviews/assurance, but we need to ensure the wiring is in place and robust now. afterward, we'll refine, educate, and add abilities/skills to the agents to enhance lesson quality and variety, add reliability to validation procedures, etc."*
→ Bar = production fidelity (see GOVERNING BAR above). Pedagogical quality / QA = out of scope this pass.
**Q2 (order):** Not separately specified → proceeding with proposed map (build A → B); Glitch #1 surfaces at Step 5.
**Q3 (other noticed):** None volunteered beyond Glitch #1.

---

### Publish-wiring verification (2026-06-17) — FIDELITY POSITIVE
Both recorded `publish_url`s fetched live and return HTTP 200 with full content (A = "Storyboard A Review", 6 slides; B = "Storyboard B Review", 6 slides + per-slide narration). The run's recorded publish URLs are genuinely reachable — publish wiring intact. (Operator's initial 404 was a copy-paste artifact: two `%20` spaces injected into the run-id stem `44b1` → `4  4b1`; not a publish failure.) Clean URLs:
- A: `https://jlenrique.github.io/assets/storyboards/f8da20ae-3ed7-44b1-a054-794b0c5e09a0/index.html`
- B: `https://jlenrique.github.io/assets/storyboards/f8da20ae-3ed7-44b1-a054-794b0c5e09a0-b/index.html`

### Step 2 — Storyboard A deck overview — SURFACED (awaiting operator response)
**Facts surfaced (from storyboard.json, `storyboard_view: slides_only`):**
- 6 slides; `review_meta`: **missing_assets=0, remote_assets=0** — all 6 visuals present on disk (`gary_slide_01..06.png`, all exist), `preview_kind=image`, `asset_status=present`.
- Visual arc (from `visual_description`): 1 Economic & Structural Reality · 2 Human Cost: System Waste & Burnout · 3 Knowledge Explosion & New Technologies · 4 Consumer Shift & The Digital Front Door · 5 The Leadership Gap · 6 Case for Change Summary & Knowledge Check.
- **Observation A (fidelity):** `display_title` = `"slide-01"…"slide-06"` (the slide *ID*), NOT the real title — the actual titles live inside `visual_description`. Title field appears not wired to the real slide title.
- **Observation B (fidelity):** `source_ref` is blank on all 6 — no provenance link from storyboard row back to the corpus source doc.
- Expected-by-design (NOT glitches for A): `narration_status=pending` / empty narration on all 6 (narration is Storyboard B's job; `slides_with_narration=0`); `selected=False` / `double_dispatch 0/6` (A/B variant pick folded — known voice/variant-HIL-fold deferred item); all motion/cluster fields blank (no-motion literal deck).
**Critical questions posed (chat):** (Q1) rendered deck — all 6 visuals show, none broken? (Q2) title-as-slide-id — log as glitch or accept as chrome? (Q3) is the 6-slide SET complete & correctly ordered vs expectation? (sub: source_ref provenance blank — log or out-of-scope?)

### Step 2 — Storyboard A deck overview — OPERATOR RESPONSE CAPTURED (2026-06-17)
**Operator verbatim:** *"slide thumbnails are visible, and expanding, as expected. layout it usable. slide vs. slide content notes (and thus future scripts) are out of step with each other: slide content notes for slide 01 are actually for 02; notes for 02 are actually for 03; etc. Many displays of field values are blank. I can't check them all, but perhaps most are not expected to be populated now, and some are just special case or aspirational?"* (+ screenshot of slide-01 "Evidence & provenance" panel — most fields n/a, Motion type=static, File path=gary/gary_slide_01.png, Quality: Vera None | Quinn None.)

**Q1 asset wiring → PASS.** Thumbnails visible + expanding; layout usable. Matches `missing_assets=0`.

**Q3 set/order → off-by-one found (see Glitch #2).**

**Blank-fields triage (answers operator's Q):** confirmed — large majority expected-blank or aspirational, NOT defects:
- Expected-by-design (static literal deck): Motion type=`static` (correct); motion status/source/duration/asset n/a; cluster position / interstitial type / isolation target / bridge type n/a (no clustering); matched segments / narration refs / visual refs / visual mode / visual file n/a on A (narration+matching is Storyboard B's job).
- Aspirational/future (agents' responsibility per operator's own bar): Quality Vera/Quinn (QA scoring); content density / visual detail load / behavioral intent (pedagogy richness); runtime target / timing role / duration rationale.
- Fidelity-relevant blank now: `source_ref`=n/a (Observation B, provenance), low severity.

## GLITCH LOG (production-fidelity defects)
- **Glitch #1 (Storyboard B — narration↔slide desync) — RESOLVED INTO Glitch #2 (2026-06-17, Step 4/5).** CONFIRMED same root cause as Glitch #2 (Gary cover-page export shift). Evidence: B's `storyboard.json` shows narration is CORRECTLY ordered + cleanly matched 1:1 (seg-01→slide-01 … seg-06→slide-06; `multi_match_narration=0`; `slides_with_narration=6`, none pending). Per-row VO topics match content order exactly (01 Economic "$5.2T line climbing", 02 Human Cost "25% admin waste/burnout", 03 Knowledge "doubles in weeks", 04 Consumer "smartphone→AI-triage→provider", 05 Leadership "interest towers, training barely registers", 06 Summary "stitch the story"). BUT row slide-01's image is the COVER (`gary_slide_01.png`), so the (correct) Economic VO references "$5.2T line on the left" — a chart on `gary_slide_02.png`, absent from the cover shown beside it. ⇒ exactly the reported symptom, caused by the image shift, NOT a narration bug. **`b-manifest-join-lossiness` rider CLEARED for this run** (join was clean 1:1; no first-perception-source collision, no empty `text_by_id`). One bug, two surfaces.
- **Observation C (Storyboard B — narration/slide number mismatch) — PARKED, OUT OF SCOPE (content/QA, not wiring)** [Step 4/5]: slide-01 VO says "$5.2 trillion"; the Economic slide image shows "$4.5T / 18% of GDP". A narration-vs-slide content inconsistency = the agents' grounding/QA responsibility in the later pedagogical pass, NOT a production-fidelity wiring defect. Captured so it isn't lost; do NOT action under the current bar.
- **🔴 Glitch #2 (Storyboard A — cover-page export shift) — CONFIRMED 2026-06-17.** Operator (Step 2 disambiguation): *"'Script Notes' is out of step with the slide to its immediate left. It matches, instead, to the slide that is down one row."* → Script Notes lead the images by one row. **Mechanism CONFIRMED by direct PNG inspection:** `gary_slide_01.png` = the deck COVER ("The Case for Physician Leadership / Module 1", no body); `gary_slide_02.png` = "The Economic & Structural Reality" (= the slide-01 notes-row topic); `gary_slide_06.png` = "The Leadership Gap — and the Case for Change". So Gary's export captured the COVER as page 1, shifting every content image down one slot. Script Notes are correctly ordered (01=Economic … 06=Summary); the IMAGE sequence carries an extra leading page. Net: each row pairs an image with the notes for the *previous* content slide; the cover has no notes row; the final content slide (Summary & Knowledge Check) is squeezed off the image sequence end (slide-06 image is Leadership/Summary-combined; needs slide-by-slide confirm if pursued). **Fix target:** Gary export page→slide_id mapping must skip/account for the cover page (likely the `_paths_from_generation` / export-URL materialization leg — known-fragile per prior gary export fixes). **CONSOLIDATION HYPOTHESIS (strong):** Glitch #1 (B VO↔slide desync) is the SAME root cause — B reuses these shifted images; VO keyed to correct content order + shifted image ⇒ "slide-1 VO narrates slide-2's illustrations / references slide-1 items that exist nowhere." If confirmed at Step 4–5, Glitch #1 + #2 collapse to ONE bug (cover-page export off-by-one), and the `b-manifest-join-lossiness` rider may be moot or secondary. CONFIRM at Step 5.
- **Observation A (Storyboard A — title not wired)** [Step 2]: `display_title` = slide-id (`"slide-01"…`) not the real title; real titles live in visual_description. Low severity; log.
- **Observation B (Storyboard A — provenance blank)** [Step 2]: `source_ref`=n/a on all 6; no row→corpus-doc provenance link. Low severity; log.

### Step 2 — Storyboard A — COMPLETE (2026-06-17)
Outcome: asset wiring PASS; blank-fields triaged (mostly expected/aspirational); **Glitch #2 CONFIRMED** (cover-page export shift) with mechanism nailed via PNG inspection; Observations A/B logged; strong consolidation hypothesis that Glitch #1 = Glitch #2.

### Step 4/5 — Storyboard B — COMPLETE (2026-06-17)
Outcome: B narration correct + cleanly matched 1:1; images are the same cover-shifted Gary set; **Glitch #1 CONFIRMED = Glitch #2 (one root cause: Gary cover-page export shift)**; `b-manifest-join-lossiness` rider CLEARED for this run; Observation C (content number mismatch) parked out-of-scope.

**Operator verbatim (Step 4/5):** *"Storyboard B confirms A's issue, also all it's 'variability' settings show no values (probable due to the trial's limited scope). The Script is indeed off set (in keeping with the offset Script Notes), however the rational for slide duration is present and excellent, as are a few other fields visible when the 'evidence and provenance' panel is opened. See especially 'behavioral intent'. A step in the right direction for sure!"* (+ Image#2 header chips: Runtime/Emotional/Pace variability n/a, Target total n/a, Avg slide n/a, WPM 150±pace n/a, Engagement stance=collegial_guide, Narration density target=150; + Image#3 slide-02 panel: Matched seg-02, Timing role=concept-build, Content density=medium, Visual detail load=light, Bridge type=none, Behavioral intent=alarming, Duration rationale="Two headline stats with a design implication; brief contrast plus action frame suffices", Source ref=n/a.)

**POSITIVES (production-fidelity wins to record):**
- B script-policy wiring PRODUCES real, slide-specific values: behavioral_intent (`alarming`), duration_rationale (contextual + sensible), timing_role (`concept-build`), content_density (`medium`), visual_detail_load (`light`). Operator: "present and excellent… a step in the right direction."
- Narration↔segment join clean 1:1 on all 6 (corroborates the b-manifest rider clearance).
- **CORRECTION to Step-2 triage:** the fields I labeled "aspirational/not-wired" (behavioral_intent, content_density, visual_detail_load, duration_rationale, timing_role) are NOT unwired — they are blank on **A** because A is the *pre-script* view, and they correctly POPULATE on **B** once the script-policy pass runs. Stage-appropriate, not a gap.

**Expected-blank (trial-scope, by design):** the "variability" header chips (runtime/emotional/pace variability, target total, avg slide, WPM±pace) belong to the runtime-plan / pacing / voice-variant layer not exercised in this frozen literal-deck trial (ties to deferred voice-HIL-fold + runtime-variability work). Engagement stance=`collegial_guide`, narration density target=150 ARE populated.
**Observation B persists on B:** `source_ref`=n/a on B too (spans both storyboards). Low severity.

### Step 3/C — dropped/merged-Summary sub-question — RESOLVED (2026-06-17)
Full image sequence (inspected all 6 PNGs + raw `gary/gary_A/` export + `gary-dispatch-payload.json`):
- **Brief:** 6 content slide_ids (slide-01..06: Economic, HumanCost, Knowledge, Consumer, Leadership, Summary&KnowledgeCheck).
- **Gamma raw export (`gary/gary_A/`) = 6 pages, 1 cover + 5 content:** `1_The-Case-for-Physician-Leadership` (COVER, no brief) · `2_Economic` · `3_Human-Cost` · `4_Knowledge` · `5_Consumer` · `6_The-Leadership-Gap-and-the-Case-for-Change` (Leadership MERGED with Summary).
- **Mapping = positional** (export page N → `gary_slide_0N` → `slide-0N`), so the cover consumes `slide-01` and shifts all content down one.
- **Answer:** the standalone "Summary & Knowledge Check" brief has **NO dedicated image** — Gamma merged it into the Leadership page, and the cover ate the freed slot. So it's not a clean "dropped last slide"; it's cover-injection + a brief→page merge.

## CONSOLIDATED FINDING (storyboard correctness) — REVIEW COMPLETE
**ONE blocking production-fidelity bug, TWO coupled defects** in the Gary deck-export → slide_id mapping:
1. **Cover injection:** Gamma generates a title/cover page (`The-Case-for-Physician-Leadership`) that maps to NO briefed slide_id; the positional page→slide mapping lets it consume `slide-01`, shifting every content image down one slot.
2. **Brief→page cardinality mismatch:** Gamma collapsed the 6 briefed content topics into 5 content pages (Leadership + Summary merged); even absent the cover, the "Summary & Knowledge Check" brief has no dedicated page.

**Symptoms (both storyboards, same root cause):** A — Script Notes/Script match the slide one row down; B — each slide's (correct, cleanly-1:1-matched) VO narrates the *next* image's content and references items absent from the shown (shifted/cover) image. This is operator Glitch #1 + Glitch #2 = ONE bug.

**Fix target / direction (for the storyboard-correctness dispatch):** replace fragile **positional** page→slide_id assignment with **title-based matching** (the `gary_A` page filenames carry titles that match the briefs) — this both *skips the unmatched cover* and *surfaces the missing Summary page as a fail-loud gap* (NOT a silent positional fill). Likely surface: gary `_paths_from_generation` / export-URL materialization leg (known-fragile per prior gary export fixes). Open question for the fix author: should the cover be (a) dropped, or (b) retained as an intentional title slide with its own row? — and how to handle Gamma merging/dropping a briefed topic (enforce 1:1, or detect+flag).

**Riders (low severity, log with the dispatch):** Observation A — `display_title` = slide-id not real title (title field not wired). Observation B — `source_ref` blank on all rows, both storyboards (no row→corpus provenance).
**Parked / OUT OF SCOPE (content-QA, agents' later pass — NOT wiring):** Observation C — slide-01 VO "$5.2T" vs Economic slide image "$4.5T" (narration grounding/number fidelity).
**Production-fidelity POSITIVES confirmed this review:** publish wiring live (A+B 200); all 6 assets present (missing_assets=0); narration↔segment join clean 1:1; B script-policy fields populate with real slide-specific values (behavioral_intent, duration_rationale, timing_role, content_density, visual_detail_load); motion correctly `static` (no-motion deck honored).

## Review status: COMPLETE (2026-06-17)
Steps engaged: 1 (orientation) · 2 (Storyboard A) · 3/C (image-sequence/Summary sub-question) · 4-5 (Storyboard B). Step 6 (audio) SKIPPED — operator already checked audio, reported fine. Step 7 (wrap) = this section. Routing: feeds the BLOCKED WAVE-0 storyboard-correctness slice (was gated on this operator review; now unblocked with a root-caused, single-bug finding + fix direction).

▶ RESUME HERE: review COMPLETE. Next action belongs to the storyboard-correctness DISPATCH (spec the cover-injection + cardinality fix per the "title-based matching" direction; party-mode per CLAUDE.md sprint governance). This ledger is the gating-input record.
