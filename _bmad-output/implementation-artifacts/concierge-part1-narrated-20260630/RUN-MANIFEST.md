# Concierge Production Run — C1M1 **Part 1** (narrated slide deck → Descript)

**Run owner:** Marcus (this instance), conversation-space SPOC — NOT the deterministic engine.
**Opened:** 2026-06-30
**Mode:** ad-hoc (real APIs, no mocks; quality/fidelity gates still honored). Not a tracked/durable engine run.
**Branch:** `dev/concierge-production-substrate-2026-06-29`

## Scope
- **Source:** most-recent C1M1 set, **Part 1 only** ("The Call — Setting the Stage"), taken **as the SME authored it** (overlap with later parts preserved — fidelity to Dr. Tejal Naik's intent is a demonstration point).
- **Components in scope:** SLIDES + their attending design notes only.
- **Components OUT of scope:** assessments / knowledge-checks, standalone videos, discussion posts, other non-slide components.
- **Deliverable:** narrated slide presentation posted into **Descript**.
- **Workflow spine:** source package → deck → narration → audio → Descript.

## Isolation discipline (do NOT confuse with other active work)
- **All artifacts live under this directory only:** `_bmad-output/implementation-artifacts/concierge-part1-narrated-20260630/`
- **HANDS-OFF (other Marcus, Part 2):** `_bmad-output/implementation-artifacts/concierge-production-2026-06-30/` and engine run `30ac2cce-4ab6-47a3-92a3-240fd09685f1` — read-only, never written, never resumed by this run.
- Any runtime/run-id this run creates will be NEW and recorded here; we do not reuse the Part-2 run.

## Specialist lane (provenance on every surface)
- **Texas** — Part-1 slides source package assembly + cross-validation (in progress).
- **Gary** — deck visual substrate.
- **Irene / Enrique** — narration authoring + directed voice.
- **Vera** — fidelity (source-containment, numeric/clinical).
- **Quinn-R** — pre/post-composition quality.
- **Compositor / Desmond** — Descript assembly + posting.

## Run principle (operator-set, binding 2026-06-30)
- **Follow the canonical pipeline.** At each segment, run REAL app code / real APIs wherever reachable. **Simulate a segment ONLY when the real path isn't callable in conversation-space — and label it as a simulation explicitly.**
- Applied: Texas source-wrangling + Irene Pass-1 instructional overlay = subagent SIMULATIONS of those segments (no clean standalone app entrypoint outside the runner). Gary/Gamma deck, Enrique/ElevenLabs audio, Descript posting = REAL app code + REAL APIs (no mocks).

## Deck-stage constraints (operator-set, binding)
- **Storyboard A = A/B per slide/card**, surfaced for per-slide operator selection on the storyboard.
- **A/B = two distinct operator-authored Gamma THEMES** (CONFIRMED by operator 2026-06-30; supersedes the earlier preset-approach reading):
  - **A slides** = `2026 HIL APC (Nejal)` — house theme — theme_id **`njim9kuhfnljvaa`**
  - **B slides** = `2026 HIL APC (Nejal) (B variant)` — operator-authored B theme — theme_id **`e8tz1vxb9v1urqp`**
  - A/B generation = `execute_generation` `double_dispatch: True` + `variant_strategies: {A: {theme_id: njim9kuhfnljvaa}, B: {theme_id: e8tz1vxb9v1urqp}}`. Both Classic, both 16:9. Source of mapping: `variant-selection-deckwide-fix-scope-2026-06-23.md`; both themes are live in the Gamma account `list_themes()`.
- **Both A and B = Gamma CLASSIC mode** (standard `/generations`, the default). **NOT** Studio image-cards (the `from-template` lock-and-replace special case is explicitly excluded for this run).
- **16:9 STRICT-RATIO SOURCE discipline (added 2026-06-30 after the Part-2 run hit title-clipping; corrected — NOT a density issue).** The Part-2 slides rendered beautifully in Gamma (no squished fonts); titles clipped only because ~4:3 PNGs (measured 2400×1766) reached Descript's 16:9 canvas and were "cover"-fit. **Generation beauty is NOT the problem and must NOT be reduced — no density capping, no squish, no regression.** Two distinct levers:
  - **Generation (beauty):** theme/layout/imageOptions/content/A-B variants — kept rich, untouched by the ratio fix.
  - **Export ratio (strict source to Descript):** the real code already targets 16:9 (`_GAMMA_EXPORT_WIDTH=2400`, `_GAMMA_EXPORT_HEIGHT=1350`) but the Part-2 path delivered ~4:3 instead. A center-crop normalizer exists but would clip the title band → do NOT rely on it for title-bearing cards.
  - **Binding fix:** (1) **generate at 16:9 presentation format** so cards are designed for the frame; (2) **export natively at 2400×1350** so Descript receives exact-ratio source and does ZERO fitting (no crop, no bars, no squish); (3) **dimension gate** before Descript verifies each PNG == 2400×1350 (16:9); off-ratio cards are re-generated/re-exported correctly, NEVER center-cropped to fit. Confirm the generation-format aspect control when building the Gary dispatch.

## Gate log
_Mapped to canonical v42 sections. Motion (07D–07F) + companion workbook (07W) are OUT of scope (narrated slide deck only)._

| # | Stage (v42 §) | Status | Notes |
|---|------|--------|-------|
| 1 | Source package (06) | ✅ LOCKED | Texas rev2: 9 slides, FULLY-SPECIFIED, fabrication=none. Expansion folded in; Slide 3→newer cited set; Slide-4 defs shipped. |
| 2 | Irene Pass-1 briefs (06) | ✅ APPROVED | 9 Gary-ready briefs; all LO-mapped; fabrication=none. |
| 3 | Gary deck A/B (07/07B) | ✅ DONE | Live A=`ybe73zv0075z4ov` / B=`me7xktka2ya09z2`. 15/18 exact 2400×1350; 3 over-tall (content-overflow, not clipped). double_dispatch wrapper crash on all-illustrated → lower-level generate_slide (follow-on). |
| 4 | Storyboard A (07C) | ✅ DONE | Published https://jlenrique.github.io/assets/storyboards/concierge-part1-narrated-20260630/index.html (commit 8be608e4). Surface=simulated A/B HTML; publish real. |
| 5 | Selection + final deck (07B) | ✅ LOCKED | Picks 1-9 = **B,A,B,B,B,A,B,B,A**. `deck-final/` all 9 @ exact 2400×1350 (card 2/A letterboxed, no crop). |
| 6 | **07G PNG-grounded perception** (gpt-5.5 vision) | ✅ DONE 2026-06-30 | Real engine (`perceive_png` + reading_path_classifier), 2 live gpt-5.5 calls/slide. 9/9 perceived, all `llm_primary`, HIGH conf 0.96-0.98. 8/9 VO-follows; s09 MISMATCH (4-pillar grid not walked, directive dropped); s05 soft note. No oppositional cues. |
| 7 | **Irene Pass-2 narration REDO** (08, perception-informed) | ✅ DONE 2026-06-30 | 7/9 unchanged (already followed eye-path); s05 bridge over skipped lexicon rows; s09 re-authored to walk 4 pillars (Gap→Mission→Journey→Mindset)+directive. "friction points" voiced (LO5-grounded); "unmet needs" dropped (zero source hits — fidelity beats display-match). fabrication=none. |
| 8 | Vera fidelity (10-fidelity) — re-run | ✅ PASS 2026-06-30 | 9/9 clean, 0 blocking. s09 unmet-needs drop CORRECT (zero source hits); friction-points restore GROUNDED (LO5); 4-pillar no-new-claims; s05 bridge grounded; 7 unchanged re-derived clean. Receipt: narration/vera-fidelity-receipt-redo.json. |
| 9 | Quinn-R quality (10-quality) | ✅ CLEAR-WITH-NOTES 2026-06-30 | No CONCERNS, no script edit. Scores: narration .92 / coherence .95 / pacing .97 / pedagogy .95 / duration .85. Notes: cards 3&9 longest (defensible); **card-3 proper-noun pronunciation → spot-check after synthesis** (fix in v3 tag layer if needed); card-9 unmet-needs divergence minor. Receipt: quality/quinn-r-quality-receipt.json. |
| 10 | Storyboard B (08B) | ⏭️ SKIPPED (operator 2026-06-30) | Review-only; operator waives the review stop. NOT downstream-required (Enrique consumes Irene's segment-manifest directly, not a B-generated one). Audit trail covered by segment-manifest + perception review. Produce only if a downstream/audit need arises. |
| 11 | Pre-spend lock + operator OK (09/11B) | ✅ OK 2026-06-30 | Operator green-lit paid synthesis. Both gates green (Vera PASS + Quinn-R CLEAR-WITH-NOTES). 9 segments, ~7.6 min, Sarah/v3. |
| 12 | Enrique audio (12) | ✅ DONE 2026-06-30 | LIVE v3/Sarah, 9/9. Model `eleven_v3`, render_mode `v3_provider_text`, voice Sarah `EXAVITQu4vr4xnSDxMaL`, no v2 fallback. 486s total. 9 mp3 + 9 vtt + receipt (per-segment request_ids). Key lacks user_read scope (/user 401) but TTS-authorized — non-blocking. ✅ Operator card-3 pronunciation listen-check APPROVED 2026-06-30 (no re-synth needed). |
| 13 | Quinn-R pre-composition QA (13) | ✅ READY-FOR-DESCRIPT 2026-06-30 | 6/6 PASS. 9/9/9, 1:1 pairing clean, all slides 2400×1350 (ratio check ✅), audio 486.034s delta 0.0, captions byte-exact, eleven_v3/Sarah/9 request-ids. Receipt: quality/quinn-r-precomp-qa-receipt.json. |
| 14 | Compositor + Desmond (14/14.5) → Descript (15) | ✅ DONE 2026-06-30 | **LIVE: https://web.descript.com/d4c69938-751c-458f-be93-036874eaa81b** · composition `e4a0d038…` duration 486.025s (delta −0.009s, independently API-verified) · 9 scenes 1:1 · native 16:9 no crop · repair=none, waivers=none · build exited 0 (Story-C anomaly did NOT reproduce). "Published"=assembled+live; MP4 share-export NOT run (out of directive). Receipt: descript/descript-publication-receipt.json. |

**🏁 RUN COMPLETE** — full pipeline source→deck→perception→VO→audio→Descript, every gate honored. Terminal deliverable: the live Descript narrated lesson above.
