# Tejal Part 4 — Full Production Walk Success Metrics (advance)

**Stamp:** 2026-07-10  
**Corpus:** `course-content/courses/tejal-c1m1-p4-assessments-bridge`  
**Bundle:** `narrated-deck-with-workbook` (deck + motion + workbook)  
**Styleguide:** `hil-2026-apc-crossroads-classic-preserve`  
**Operator stand-in:** AFK HIL driver (edit→confirm G0; varied gate verbs)  
**Spend:** operator-authorized (Gamma + Kling + ElevenLabs + OpenAI)  
**Out of scope:** Descript publish (stop after Desmond aggregation)  
**New trust config:** `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE=1` for this process only (default remains OFF in product)

Evidence pack: `tejal-p4-fullwalk-*`  
Driver: `tejal_p4_fullwalk_driver.py`

---

## Claim envelope (what “success” means)

| Claim | Pass condition |
|-------|----------------|
| **C1 Terminal complete** | `run.json` `status == completed` |
| **C2 No Descript publish** | No Descript share URL / publish receipt required; Desmond brief + assembly-bundle present |
| **C3 Planning → downstream** | Plan-dialogue (or ratified intent) LOs + enrichment surfaces appear in Pass-1 plan and workbook grounding |
| **C4 Fidelity flag exercised** | Env flag ON during Pass-2; either sail OR fail-loud with expected fidelity tag + documented recover |
| **C5 Full artifact set** | Deck PNGs + motion MP4(s) + narration audio + workbook md/docx + Desmond brief |

**Not claimed:** trust-COMPLETE default-ON; Batch LLM; HAI/PHS; S8 reopen; Descript import.

---

## Gate metrics (HIL stand-in)

| Gate | Required verb path | Pass metric |
|------|--------------------|-------------|
| **G0 confirm** | edit → confirm (not `--auto-confirm-directive`) | `g0_confirm_path == ["e","c"]`; `directive.yaml` present |
| **G0E** | approve | Decision card + resume advances |
| **G0R** | approve | `ratified-los.json` written; non-empty LO list |
| **G1** | edit-inspect (first) or approve | `irene-pass1.lesson-plan.json` or Pass-1 contribution present; planning_context / purpose-audience coverage if companions present |
| **G2B** | select all **A** | Variant selections recorded for every offered slide |
| **G2C** | approve | Storyboard/asset approval; no silent empty exports |
| **G3** | approve | Storyboard lock |
| **G4 / G4A / G4B** | approve as presented | Voice / package checkpoints clear |
| **G5** | approve | Quinn-R pre-composition QA clear |

Any unexpected `paused-at-error` before G2C with tag `gamma.export.brief-unmatched` → **FAIL** (known Part-4 flake class; recover/retry allowed once).

---

## Node / specialist metrics

| Node / specialist | Pass metric |
|-------------------|-------------|
| **Texas (01–04)** | `bundle/extracted.md` exists; corpus leaf ingested |
| **G0 enrichment** | `g0-enrichment.json` present when enrichment active |
| **Irene Pass-1 (05B)** | Lesson plan JSON on disk; collateral declaration present for workbook; LOs reflect ratified / dialogue set |
| **CD / Gary (07)** | ≥1 slide PNG under run exports / assembly visuals; no terminal `gamma.export.brief-unmatched` |
| **Kira motion (07D–07F)** | ≥1 `.mp4` under run `motion/` or assembly-bundle `motion/` |
| **Vision (07G)** | Perception artifacts present for rendered slides |
| **Irene Pass-2 (08)** | Segment manifest / narration contribution; **with flag ON:** no unsourced / conflict / positive-carry miss **OR** halt with those tags (honest fail) |
| **Enrique (12)** | ≥1 audio file under assembly-bundle `audio/` (or run audio path) |
| **Quinn-R G5 (13)** | Gate cleared; no `join-collapsed` refuse without recover |
| **Compositor (14)** | `assembly-bundle/` + `DESCRIPT-ASSEMBLY-GUIDE.md` |
| **Desmond (14.5)** | `DESMOND-OPERATOR-BRIEF.md` with `## Automation Advisory` |
| **Marcus handoff (15)** | Completed / Descript-ready marker without calling Descript API |
| **Workbook (07W)** | `workbook.md` + `workbook.docx`; sections cite Part-4 assessment sources |

---

## Completed-artifact attribute metrics

### Deck
- [ ] At least one slide image (PNG) produced
- [ ] Slide content reflects bridge / Module-1→2 framing (not empty Gamma stub)
- [ ] Styleguide bind = preserve sibling (not condense)

### Motion
- [ ] At least one Kling MP4
- [ ] Motion scoped to this trial run dir (no global `runs/kira-motion` pollution)

### Audio narration
- [ ] Audio segments exist and are non-empty
- [ ] Segment count aligns with storyboard / join (no collapsed-id publish)

### Workbook companion
- [ ] MD + DOCX present
- [ ] Mentions or grounds ≥1 of: discussion peer eval, knowledge check, opportunity-radar playbook
- [ ] Does not invent missing PDF/DOI/deck assets as present (gap-aware)

### Planning / LO / enrichment downstream
- [ ] `ratified-los.json` present
- [ ] Pass-1 plan acknowledges purpose/audience when planning companions present
- [ ] Component selection = deck+motion+workbook (`narrated-deck-with-workbook`)

### Desmond aggregation (no publish)
- [ ] `DESMOND-OPERATOR-BRIEF.md` present
- [ ] Assembly bundle lists visuals + motion + audio
- [ ] Explicit: **no** Descript share URL required for pass

### Figure fidelity (new)
- [ ] Process env had flag ON through Pass-2
- [ ] Either: Pass-2 sailed under flag, **or** fail-loud with `irene.pass2.figure-*` tag and recover transcript
- [ ] After run: document that product default remains OFF

---

## Overall scorecard

| Grade | Definition |
|-------|------------|
| **PASS** | C1–C5 all true; all critical artifact checks green |
| **PASS-WITH-RECOVER** | C1 eventually true after ≤2 recovers; fidelity halt recovered honestly |
| **PARTIAL** | Deck+audio+workbook OR motion missing one pillar; Desmond present |
| **FAIL** | Terminal error without recoverable path; or Descript publish attempted as success criterion |

Scorer writes `metrics-scorecard.json` into the evidence pack after the walk.
