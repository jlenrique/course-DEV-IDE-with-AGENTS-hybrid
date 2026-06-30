# Next-Session Development Plan — Concierge → Production Hardening

**Date:** 2026-06-30
**Author:** Marcus (Part-1 concierge run, conversation-space SPOC)
**Status:** PRE-PLANNING backlog candidate — to be authored as BMAD stories via `bmad-create-story` next dev session (not code-ready yet).

## Sources (two parallel concierge runs)
1. **Part-2 run** (other Marcus) — `concierge-production-2026-06-30/production-development-lessons-2026-06-30.md` (10 issues, Stories A–E). Reached a published Descript final (475s, 13 slides) but discovered aspect-ratio problems *inside Descript*.
2. **Part-1 run** (this Marcus) — `concierge-part1-narrated-20260630/` (this run). Engineered the aspect-ratio + perception + fidelity gates *upfront*; surfaced new code defects en route.

**Why this matters:** the two runs CONVERGE on the same production-contract gaps. Where both runs independently hit an issue, that's the strongest possible signal for a code fix. Where our run already worked around an issue successfully, that's a working spec for the fix.

---

## A0. 🔒 PROTECTED INVARIANT — VO↔on-screen alignment (operator-emphatic 2026-06-30; HIGHEST priority, non-waivable)

**Finding:** on playing the finished Descript video, the operator judged the **VO-narration-to-on-screen-display/layout alignment EXCELLENT** and issued a standing order: **protect this capability against regression AT ALL COSTS — no future enhancement may degrade VO↔on-screen tracking, even as voice nuance/variety grows.** This is the run's top takeaway.

**What produced it:** the new **07G PNG-grounded perception** (gpt-5.5 vision → per-slide `reading_path`) + **Irene Pass-2 narration redo** matching the VO to each slide's reading-path were most critical; **Quinn-R** (slide↔VO coherence) + **Vera** (fidelity) confirmed; clustering was deferred this run but the invariant must hold when it is ON.

**The regression guard (must become codified governance — outranks all items below):**
1. **Channel orthogonality.** VO↔on-screen tracking lives in the **canonical narration text** (content + order, matched to reading-path). Voice nuance/variety lives in the **prosody/tag channel** (v3 `eleven_v3` tags, multi-voice, directed reads). Future expressiveness work MUST stay in the prosody/tag channel and MUST NOT reorder/restructure/re-scope the canonical text. (Mirrors the enhanced-vo tag-only provider-text separation — keep orthogonal.)
2. **Non-waivable gate.** ANY future story touching narration authoring, voice rendering (directed-voice/v3 tags/voice variety), the perception service, clustering, or deck layout MUST run 07G perception → narration read-path-match and PROVE no regression: every slide's narration still "follows" its perceived reading-path; ZERO new oppositional-cue conflicts; Quinn-R slide↔VO coherence not lowered vs baseline. Failure BLOCKS — cannot be waived as cosmetic.
3. **Baseline yardstick:** this run's `perception/narration-script-review.md` (9/9 follow after the s09 fix) + `quality/quinn-r-quality-receipt.json` (coherence 0.95).
4. **Story candidate (NEW, top of backlog): "VO↔on-screen reading-path tracking — protected-invariant regression harness"** — a standing automated check + acceptance gate that future voice/narration/clustering/layout stories must pass.

## A. Cross-run convergence (BOTH runs hit it → highest-priority code fixes)

> **GENERALIZED PRINCIPLE (operator-affirmed 2026-06-30): publication-target ratio contract.**
> When a deck's publication target is a fixed-canvas platform (Descript = 16:9 / 1920×1080; and any future target with its own canvas), the slide PNGs MUST be produced/normalized to that target's exact aspect ratio as a **hard, pre-assembly contract** — verified by a dimension gate BEFORE any platform API call. The source of truth is the **destination canvas**, not the deck tool's default export. Non-conformant PNGs either block (fail-loud) or pass through an explicit, receipt-backed repair stage; they are NEVER silently fit/cropped by the destination assembler. Store the intended `video_canvas` in the run manifest before deck generation.

### A1. Gamma→Descript aspect-ratio contract is missing *(their #1/#2/#3; our deck-stage constraint)*
- **Their experience:** non-16:9 PNGs reached Descript, "cover" fit cropped titles; fixed only via a source-side smart-extension repair pass discovered late.
- **Our experience:** we made strict 16:9 a *binding upfront constraint* — generated at 16:9, then a **dimension gate** caught 3/18 over-tall cards (content-overflow growth, not 4:3), and we letterboxed the one selected over-tall card to exact 2400×1350 BEFORE any Descript step. No title ever clipped.
- **Convergent fix (validated by our run):** a **pre-Descript visual preflight gate** that (a) reads every PNG dimension, (b) requires exact/tolerance 16:9, (c) fails loud otherwise, (d) emits a receipt with source/target dims + selected repair policy. Plus record intended `video_canvas` in the run manifest BEFORE Gamma generation and verify exported dims after download.
- **PLACEMENT DECISION (operator-affirmed 2026-06-30):** the ratio/size-conformance check must be a **codified, standing part of the §13 pre-composition QA contract** (target-canvas-aware), NOT something a concierge orchestrator remembers to add to a QA dispatch. §13 already answers "are these assets ready for assembly"; "conformant to the destination platform's canvas (Descript 16:9 / 1920×1080)" IS that question. So: fold the dimension/ratio gate into the production §13 pre-composition QA as a first-class check that BLOCKS NOT-READY on any non-conformant PNG — with the destination canvas as a parameter. (In this Part-1 run we hand-added it as Quinn-R pre-comp check #3; production must own it by default.)
- **New nuance our run adds:** the off-ratio cause is often **content-overflow vertical growth** (Gamma extends a card when text+infographic overflow 16:9), producing *variable* heights (we measured 1510/1558/1592 vs 1350) — NOT a fixed 4:3. The gate must handle per-card variance, and the *real* prevention is keeping cards within 16:9 content budget at generation (without sacrificing density/beauty — see A5).

### A2. Perception / reading-path receipts must be non-optional *(their #7; our 07G gate)*
- **Both runs:** reading-path is essential so VO + attention follow the slide naturally.
- **Our experience:** we ran **07G PNG-grounded perception** (real gpt-5.5 vision, `perceive_png` + `reading_path_classifier`) as a hard gate; it caught a real s09 VO↔grid mismatch + an s05 skipped-rows issue, which drove an Irene Pass-2 redo. **Concrete proof the gate earns its place.**
- **Convergent fix:** a slide cannot enter final narration assembly without a perception receipt; the script must reference the same slide/component identity. Make 07G a required handoff, not optional.

### A3. v3 Sarah voice path should be the production default *(their #9; our gate-12 config)*
- **Both runs** used v3 / Sarah and approved the audio quality.
- **Convergent fix:** promote v3 (`eleven_v3`, `v3_provider_text`) to the production default; ensure config doesn't surface stale v2 settings as current; persist voice + model + request-ids + per-segment cost in the run asset ledger.

### A4. Fidelity findings need severity + explicit waivers *(their #8; our Vera-with-teeth)*
- **Their experience:** the source-figure checker was imperfect and *silently waived*.
- **Our experience:** Vera ran with TEETH (independent re-derivation, BLOCK authority); correctly dropped an ungrounded "unmet needs" token; applied the lenient figure-grounding bar deliberately.
- **Convergent fix:** split fidelity by severity — hard-blocking (changed numerals / clinical terms / negations / comparators), review-blocking (suspicious grounding), advisory (formatting). Waivers must be explicit in the run receipt (reason, approver, timestamp, risk note) — never silent. *(Ties directly to the coverage-assurance-interlock arc already in flight on the main branch.)*

---

## B. NEW findings from the Part-1 run (not in the Part-2 list)

### B1. `execute_generation(double_dispatch=True)` crashes on an all-illustrated deck *(real bug)*
- The A/B double-dispatch wrapper routes through a **mixed-fidelity** path that assumes ≥1 literal card, then crashes in `validate_theme_mapping_handshake` on an empty `theme_resolution`. We fell back to the real lower-level per-variant `generate_slide` path to ship A/B.
- **Fix candidate:** make `double_dispatch` support a uniform-fidelity (all-illustrated) deck without forcing a literal card; or fix the theme-handshake to tolerate the all-illustrated path.

### B2. Storyboard A real emitter is single-variant — can't represent A/B selection
- `app/gates/section_07c/storyboard_html_emitter.py` (`_slide_block`) has no A-vs-B slot, so an A/B Storyboard-A selection surface had to be a purpose-built HTML (the publish push itself reused the real pages-repo mechanism).
- **Fix candidate:** extend the emitter with an A/B-per-card mode so the real emitter can render the variant-selection surface.

### B3. `narration/` is git-untracked → no byte-diff across a Pass-2 redo *(Vera soft note)*
- When Irene re-authored the script, Vera could not byte-diff the 7 "unchanged" segments vs the prior PASSed text (overwritten in place, untracked).
- **Fix candidate:** snapshot the prior narration (or version the segment-manifest) before a redo so a deterministic byte-diff is possible; lets fidelity re-runs confirm "unchanged = literally unchanged."

### B3a. Descript assembly state is OPAQUE while the build runs detached *(new, reinforces their #4/#5/Story C)*
- In our run, the build (driven in background) created the project + imported all media, and the Underlord assembly job was running **server-side inside the detached process** — but at one mid-assembly moment the composition read **duration 0** via the API with no *visible* queued agent job from the coordinator's vantage. The coordinator (correctly cautious) flagged a possible orphan; on direct query the agent job (`project-agent-edit-…`) was found `running` with the comp already climbing to ~486s, and was awaited foreground to success. **Net: NOT actually orphaned — but the detach made "in-flight" indistinguishable from "orphaned/empty" from outside.** Build ultimately exited 0 (the Part-2 Story-C nonzero anomaly did NOT reproduce this run).
- **Fix candidate (folds into Story C):** the build must (a) run assembly **synchronously / foreground to a terminal job state**, OR (b) **expose the assembly agent-job id** so the caller can `wait_for_job` deterministically — never leave the caller polling raw composition state, where mid-assembly looks identical to empty. The **publication receipt must assert `composition.duration > 0` and ≈ expected audio total** before `published: true` — the success signal is the *assembled composition*, not project-created + media-imported.

### B4. Pass-2 package contract *(their #6 — confirm against our run)*
- Their run needed concierge normalization before strict validation passed. **Our run built the segment-manifest by hand** (didn't exercise the strict producer contract), so we did NOT independently confirm the producer emits the normalized shape. **Action:** validate our `segment-manifest.yaml` against the strict Pass-2 schema next session to see whether the producer-side hardening (their Story D) is still needed.

---

## C. What our run VALIDATED (working specs for the fixes)
- **Strict-16:9-upfront + dimension gate + letterbox** → zero title clipping (validates Stories A + B of the Part-2 list).
- **Perception as a hard gate** → caught a real read-path defect (validates their #7).
- **Vera independent fidelity with BLOCK authority** → caught an ungrounded token (validates their #8 severity model).
- **v3 / Sarah** → clean synthesis path (validates their #9).
- **Full careful gate sequence** (source → perception → Pass-2 → Vera → Quinn-R → pre-spend → audio → QA → Descript) ran end-to-end in conversation-space without a fidelity miss.

---

## D. Proposed next-session story backlog (merged + prioritized)
Harmonize with the Part-2 run's Stories A–E; do NOT duplicate. Priority order:

1. **Story A — Fail-loud Gamma aspect-ratio gate** (their A) + **content-overflow variance handling** (our A1 nuance). Pre-Descript preflight; record `video_canvas` pre-generation; verify post-download.
2. **Story B — Source-side smart visual-repair component** (their B) with `reject | gamma-reexport | smart-extend | contain-matte` modes, contact sheet, ledger policy. *(Our letterbox = the minimal `contain-matte` proof.)*
3. **Story C — Descript publication receipt + PowerShell-clean exit** (their C). (We'll hit this live at our own Descript gate this session — capture our experience as input.)
4. **Story D — Pass-2 package contract hardening** (their D) — gated on B4 confirmation.
5. **Story F (NEW) — A/B-capable Storyboard-A emitter** (our B2).
6. **Story G (NEW) — `double_dispatch` all-illustrated support / theme-handshake fix** (our B1).
7. **Story E — Run Asset Index continuation view** (their E) — resume from Gamma URL / run id / Descript id.
8. **Fidelity severity + explicit-waiver ledger** (their #8 / our A4) — coordinate with the in-flight coverage-assurance-interlock arc (likely the same home).
9. **Story H (NEW, small) — narration snapshot/versioning before Pass-2 redo** (our B3).

## E. Governance note
- These are **conversation-space concierge findings** → they become real work only via the BMAD spine (party green-light → `bmad-create-story` → dev → review → close). This doc is the pre-planning input, not the authority.
- Both concierge runs are **substrate-verification probes** for the production-hardening goal — exactly the weed-clearing posture. The job now is to convert "a human noticed and repaired at each stage" into "the app detects, blocks, receipts, and resumes."
- Feed this into the canonical `next-session-start-here.md` / deferred-inventory at session close (do not clobber the coverage-interlock banner mid-run).
