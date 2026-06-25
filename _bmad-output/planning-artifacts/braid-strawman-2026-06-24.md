# Braid Strawman — Marcus-Interlocutor + Research Foundations + Lesson-Planning-with-Workbook-Companion (2026-06-24)

**Status:** STRAWMAN for party-mode green-light + sequencing. Operator-set direction (2026-06-24). NOT yet ratified.
**Purpose:** Give the tailored party a concrete artifact to pressure-test so the round produces a LOCK (decided render-target + minimal first-run slice + sequence), not an open brainstorm.
**Authorities:** operator vision 2026-06-24 (this session); STATE-OF-THE-APP §7/§11; `forward-development-sequence-2026-06-24.md`; specialist-registry.yaml; Epic 27 retrieval architecture; Epics 28–32 Lesson Planner; Epic 17 Research; Epic 18 asset families.

---

## 1. The braid (operator vision, verbatim-faithful)

Three interlocking capabilities, ONE product story — not three separate arcs:

1. **Marcus as a true interlocutor** — NOT a fixed table-of-contents that talks. An agent that works on the operator's behalf to **clarify the operator's own needs/wants and what is actually possible**, that **knows what every specialist can and can't do in the *current* state of the app**, and that runs on the **frontier model + fullest intelligence + largest context window** (other specialists may run leaner).
2. **Research as a foundational capability** — essential functions stood up, including **citations to presentation content**, with research output having a real home (the workbook).
3. **Lesson planning that specifies collateral assets, not just the deck** — via Marcus + Irene, the lesson plan offers a variety of assets bakeable into a lesson. Flagship: a **workbook/worksheet companion** to the presentation carrying **transcript + fuller narrative** (the depth deliberately kept OFF the glance-slides and out of heard-only narration), **exercises**, and **research + citations**. Pattern: state the PURPOSE → Marcus/Irene design the artifact → add to the production flow. Open-ended by design; **for the upcoming run, predefined** (workbook companion is a known high-priority client ask: deeper educational impact + durable resource).

**Unifying insight:** the interlocutor's *purpose* is to elicit the lesson plan; the lesson plan specifies research goals + assets; the workbook is where research, citations, and depth accumulate. The glance-deck (perception-tuned, tight VO — just optimized by the clustering arc) and the read-in-depth workbook are dual-coding partners. The VO can stay tight precisely BECAUSE the workbook carries the depth.

---

## 2. Reuse map — this is mostly wiring + ONE new producer

| Need | Already exists | Gap |
|---|---|---|
| Transcript backbone | Irene Pass-2 narration script / segment manifest | reuse as workbook transcript |
| Citation provenance | `source_ref` mandatory across schemas (Epic 2A); **L2 source-fidelity audit module** (just built) = same sourced/unsourced engine | citation INJECTION into a doc + link-to-slide-content is new |
| Retrieval foundation | Epic 27-0: dispatcher, provider directory, contracts, cross-validation (`skills/bmad-agent-texas/scripts/retrieval/`); Texas = retrieval dispatcher | research NOT wired to the production trial path (BETA (d) orphaned) |
| Lesson-plan schema | Epics 28–32 Lesson Planner MVP substrate (registries, log, producer ABC) landed | production-path orphaned; not driving collateral |
| Authoring | Irene Pass-1 (plan) + Pass-2 (narration) | extend Pass-1 to emit collateral-asset + research-enrichment specs |
| Capability model for Marcus | `skills/bmad-agent-marcus/references/specialist-registry.yaml` (14 specialists + 11 personas + partial/dissolved) | needs a LIVE "wired vs orphaned in current app state" overlay; the static registry alone over-promises |
| Delivery | Desmond / Descript (deck video) | workbook delivery target undecided |

**Net-new build is small and localized:** a **workbook producer** (+ its render target + schema) and **Marcus's capability-self-model + intent-elicitation loop**. Everything else is connect-and-extend.

---

## 3. DECISION POINTS the party must resolve (strawman recommendation in **bold**)

**DP1 — Marcus interlocutor: capability-model source of truth + interaction posture.**
- Strawman: Marcus grounds on `specialist-registry.yaml` PLUS a generated **capability-state overlay** (machine-readable: per-specialist `wired | partial | orphaned | shelf` against the *current* dispatch graph) so the frontier model cannot promise unbuilt capability (the believed-green / over-promising failure mode). Interaction = **goal-elicitation loop** (clarify needs → propose what's possible *now* → confirm scope → emit a structured intent the pipeline consumes), replacing the scripted one-pass narrator. Frontier model + max context for Marcus; specialists leaner. **Recommend: this is the design-heaviest piece — its own NEW CYCLE story.**

**DP2 — Research foundations scope + the Tracy namespace collision.**
- ⚠️ **Collision:** `specialist-registry.yaml::personas.tracy` = "typography + visual-design adjudication (§07B/§08B)"; but Epic 27/28 + BETA (d) + STATE-OF-THE-APP treat "Tracy" as **research/editorial-intent** owner (with Texas as retrieval dispatcher). Filed: `beta-marcus-namespace-collision-rename`. **Must resolve before research wiring** — who owns research-editorial intent, and what is that persona NAMED?
- Strawman: **research-FOUNDATIONS (thin), not full Epic 17.** Wire the existing Epic 27-0 retrieval (Texas dispatcher + provider directory) onto the trial path, driven by lesson-plan research-enrichment goals; output lands as cited entries in the workbook. Defer hypothesis-research / full Epic 17. Resolve the Tracy name as part of DP2 (rename the typography persona OR name a distinct research-editorial persona).

**DP3 — Workbook render-target + producer ownership (THE load-bearing decision).**
- Options: (a) **Gamma document/page mode** (reuse Gary/Gamma; ⚠️ memory says Gamma API is Classic-cards only — doc mode may be API-inaccessible); (b) **Markdown → PDF/DOCX** deterministic producer (new, fully controllable, no new API dependency); (c) **new pack family** (Epic 18 handouts/workbook) rendered via an existing doc tool.
- Strawman: **(b) Markdown→PDF/DOCX deterministic producer** for v1 — maximal control, no API-availability risk, citations + transcript + exercises are text-native, and it composes with the existing compositor/bundle pattern. Revisit richer rendering later. Producer owned by **Irene (content) + a new deterministic workbook producer module** (Class-D2-like, no API).

**DP4 — Lesson-plan-as-driver.**
- Strawman: extend Irene **Pass-1** to emit, alongside the slide brief, a **collateral-asset spec** (workbook: sections, exercises, depth targets) + a **research-enrichment goals** block (what to fetch + cite). Additive to the existing plan schema; degenerate-empty = today's deck-only behavior (no regression).

**DP5 — Minimal coherent slice for the UPCOMING run (predefined v1 on tejal).**
- Strawman: v1 = **predefined** workbook spec + predefined research-enrichment goals for the frozen `tejal-apc-c1-m1-p2-trends` deck; Marcus **elicits/confirms** rather than free-form-invents; deck pipeline unchanged (clustered, per-sub-slide A/B, tight VO, no ghost numbers); workbook produced as a paired durable artifact with ≥1 cited research entry linked to slide content. The open-ended "state purpose → agents design the asset" pattern is explicitly **v-next**, out of v1 scope.

**DP6 — Frozen-Gamma reuse policy (operator-stated).**
- Strawman (operator-stated, codify): **freeze + reuse already-produced Gamma slides on any run that does not entail/impact slide production**; require **fresh Gamma generation when a run must confirm new slide-affecting functionality or check for regressions**. The workbook arc is largely slide-independent → most workbook iterations reuse frozen Gammas; a clustering/A-B-touching change triggers fresh gen.

**DP7 — Sequencing + NEW CYCLE story breakdown.**
- Strawman sequence (each: party green-light → NEW CYCLE dev → Claude T11 → small-scale live run → iterate):
  1. **Marcus capability-self-model** (DP1 substrate: registry + live overlay) — prerequisite for honest interlocution.
  2. **Lesson-plan collateral+research spec** (DP4: Irene Pass-1 additive emission).
  3. **Workbook producer** (DP3: render-target + producer + schema) — consumes transcript + plan spec.
  4. **Research wiring (thin)** (DP2: Texas/retrieval onto trial path → cited workbook entries; resolve Tracy name).
  5. **Marcus interlocution loop** (DP1 interaction: goal-elicitation REPL on the frontier model) — ties it together.
  - 2/3/4 are substantially independent (parallelizable); 1 precedes 5; 5 integrates all.

---

## 4. Honesty gates that ride alongside (not optional)
- `v5-manifest-coherence-reconciliation` — binding pre-next-trial.
- Fresh-naive-holdout for any reading-path generalization claim (Mary's standing dissent) — this arc does NOT advance it.
- Citation fidelity: every workbook citation must trace to a real `source_ref` (reuse the L2 audit engine); no invented citations — same "compose freely; assert only what's sourced" principle as the fidelity arc.
- No mocks; live APIs; first-run-stands; small-scale live runs validate each story; never leave lockstep/manifest half-modified.

---

## 5. What the party must DELIVER this round (goal completion criteria)
1. Pressure-test the braid; confirm it's one coherent arc or split it.
2. **Decide DP3 (workbook render-target)** + resolve **DP2 (Tracy collision + research scope)**.
3. **Lock DP5 (minimal first-run slice)** + ratify DP6 (frozen-Gamma policy).
4. Ratify DP7 sequence + the NEW CYCLE story breakdown.
5. Concur that the above is enough to author **ready-to-implement specs** and launch dev agents with small-scale-live-run iteration.
