# Forward Development Sequence — 2026-06-24 (dev-plan revisit)

**Status:** ratified direction (operator-set 2026-06-24). Centerpiece = **clustering re-activation for VO follow-along**, proven on **A/B per-slide variant production runs to Descript**.
**Authorities:** memory `chunking-via-clustering-followalong`; STATE-OF-THE-APP §11; party-mode brainstorm 2026-06-24 (Caravaggio/Sally/Winston/Quinn); clustering-live verification 2026-06-24.

## Organizing principle
Every trial is now a real production run. The **next** trial must demonstrably improve follow-along AND keep the capabilities already proven on the 2026-06-24 mirror runs (`7d530d0a`/`6cb8eafd`): genuine per-slide **A/B** selection completing **fully to Descript** package creation, with the **figure-citation gate holding live (no ghost numbers in VO)**. So clustering comes BEFORE the next trial, and the honesty gates sit where they actually bind.

## Decided amendments (operator, 2026-06-24)
- **Fork resolved → clustering-first.** The next trial includes clustering; no baseline single-variant trial first.
- **Trials are A/B per-slide proof runs to Descript** each time (not single-variant).
- **"No ghost numbers in VO"** is a live success criterion → the figure-gate N≥15 validation folds into these B-heavy proof runs.
- **Success = reproduce the prior mirror-run achievement, raised:** successful A/B runs fully to Descript, now WITH clustering, VO-to-screen tightness, and no ghost numbers.

---

## Phase 1a GREEN-LIGHT — OUTCOME (2026-06-24): APPROVED 4/4 GREEN-WITH-AMENDMENTS (Winston/John/Murat/Mary, no impasse)

**Binding amendments (consolidated):**
1. **Story split** (Winston+John): 1.1 re-wire Pass-1 emission (smallest, first) → 1.2 downstream integrity checkpoint → 1.3 three small adds (3 isolable commits) → 1.4 clustering×A/B reconciliation (gated, last). NOT one NEW CYCLE blob.
2. **T1 survival probe** (John): before re-wiring Pass-1, hand-feed a cluster input through the dormant downstream to confirm the April machinery still EXECUTES (survival-in-code ≠ survival-in-execution). Bit-rot → re-scope 1.1 via party re-entry.
3. **1.2 acceptance = three ARTIFACT gates** (Murat), not code-path smoke: (A) emission — pre-identified dense slide carries cluster fields count≥2 in the real Pass-1 artifact; (B) propagation — that slide → ≥2 segments in the segment manifest; (C) narration — VO partitioned along the cluster boundaries. Gate on the witness, never on a green unit suite.
4. **Schema-additive** (Winston): cluster fields additive; flat slide = degenerate size-1 cluster; downstream tolerance-of-absence is an AC.
5. **keep-dense as INPUT not veto** (Winston): a keep-dense unit is never a chunk candidate — stated in 1.1's cluster-decision spec, shipped in 1.3.
6. **PRODUCT DECISION (John, PM): A/B at cluster-HEAD, not per sub-slide.** Chooser decides A/B once per original slide; chunk-expand the CHOSEN variant downstream. Keeps 1.4 from exploding (per-sub-slide A/B = render volume × chunk-factor for ~zero marginal value). Figure-gate still re-runs per sub-slide. **→ OPERATOR-CONFIRM (touches the just-shipped per-slide A/B substrate; John wants Marcus's read).** **OPERATOR RESOLVED 2026-06-24: OVERRIDDEN → PER-SUB-SLIDE A/B.** Operator wants maximum follow-along granularity; each chunked sub-slide gets its own A/B pick. Story 1.4 scope expands accordingly (chooser + dispatch + figure-gate each address every post-chunk sub-slide; render volume × chunk-factor accepted). See memory `project-clustering-ab-granularity-decision`.
7. **Measurable success** (Murat+Mary): ghost-numbers = HARD gate (figure-contradiction count=0, pinned extraction, published count); "tightness" = deterministic structural proxy (VO-unit↔cluster alignment, no look-ahead leakage, violations=0) + perceptual tightness = logged operator/blind eye-read, NEVER auto-green.
8. **Raised success bar** (Murat+Mary): 3 CONSECUTIVE clean runs (ghost=0 + propagation every run, reset-on-failure, first-run-stands) + 1 CROSS-DECK run. Claims scoped "on tejal" until the cross-deck run. **→ OPERATOR-CONFIRM (raises the operator's stated "prove twice" bar).**
9. **Baseline anchoring** (John): frozen VO-follow-along baselines = the clean 2026-06-24 A/B mirror runs `7d530d0a` + `6cb8eafd` (un-clustered control, on disk). Phase 2 measures the delta against these.
10. **Reading-path disclaimer** (Mary): close-out states explicitly "this arc does NOT advance the reading-path holdout gate; that gate remains open." No halo overclaim.
11. **File 1.4/Phase-1.5 to deferred-inventory now** (Winston, per CLAUDE.md governance) — done.

---

## Phase 1 — Clustering re-activation *(centerpiece; gates the next trial)*
**Finding (verified 2026-06-24):** clustering is BUILT but DORMANT. Old pipeline genuinely ran it (April manifest `...20260419b-motion` = 74 cluster-field entries, real head+interstitial). Current LLM-first Pass-1 emits flat "one slide per unit" — no clusters; the rebuild dropped cluster emission. Downstream (Gary `CLUSTER_OUTPUT_FIELDS`, segment-manifest cluster carry in `pass_2_template.py`, Epic-23 bridges, density controls, `slide_count_runtime_estimator`) survives in code but unexercised since migration.

- **1a. Party-mode green-light the scope** (substrate → governance). *(STARTED 2026-06-24.)*
- **1b. NEW CYCLE — re-wire cluster emission into LLM-first Pass-1** (Codex T1–T10 → Claude T11): emit `cluster_id`/`cluster_role`/`cluster_position`/`narrative_arc` in `plan_units` + the cluster-decision/density logic the migration dropped.
- **1c. Re-verify downstream end-to-end** on a real smoke (Gary → segment manifest → Epic-23 bridges → timing). **Main schedule risk = bit-rot** since April; re-verify EARLY and re-scope if the chain needs repair, not just reconnection.
- **1d. Three small adds:** per-slide **chunk directive** (extend `special_treatment_directives`); **keep-dense marker** for synthesis/big-picture slides (Irene keeps them dense — do not chunk a gestalt); **inter-sub-slide transition timing** in the segment manifest (the one genuinely-new piece).
- **Exit gate:** a fresh smoke produces a *clustered* deck end-to-end (clusters in manifest + bridges in narration + correct timing).

## Phase 1.5 — Clustering × per-slide A/B integration *(first-class risk)*
Chunking expands N source slides into more sub-slides; the per-slide A/B chooser + variant dispatch + figure-gate must all address the post-chunk slide set coherently (each addressable sub-slide; variant pick per sub-slide; combinatorics + Gamma render volume bounded). Reconcile in the trial/repair loop; surface to operator if it needs a product decision (e.g., A/B at cluster-head level vs per sub-slide).

## Phase 2 — A/B proof runs to Descript *(the trial; fix-on-the-fly)*
- Real trials with clustering ON + per-slide A/B selection via real Playwright chooser clicks (as in the mirror runs) → complete to Descript segment-manifest + ElevenLabs audio, 0 errors.
- **Verify live on REAL artifacts** (not code-intent): clusters in the manifest, bridges in narration, VO-to-screen tightness, and **no figure-contradiction (no ghost numbers)**.
- **Honesty:** verification-not-benchmark; resubstitution stamp on every reading-path number (consumed-14; no generalization claim).
- **Pre-trial checklist (verify, don't assume):** `v5-manifest-coherence-reconciliation` (filed binding pre-next-trial); G0 pre-flight green.
- **Prove twice:** an A/B mix + a mirror, each error-free to Descript with clustering + tight VO + no ghost numbers — the prior mirror-run bar, raised.

## Phase 3 — Honesty / generalization gates *(parallelizable; gate claims, not the trial)*
- **Fresh naive holdout** for reading-path (operator labels ≥12–15 new slides) — binding before any "reading-path generalizes" claim (Mary's standing dissent).

## Phase 4 — Real conversational Marcus SPOC
The standing dispositive commitment (LLM stop-and-chat REPL replacing the scripted narrator). Class S; party → NEW CYCLE → T11. After the clustering trial delivers near-term value.

## Phase 5 — Epic 15 (Learning) + beyond
Turn tracked trials into compounding intelligence — most reactivation-ready shelf epic.

## Ongoing hygiene *(low-priority, batchable, non-blocking)*
17 ambient contract stale-pins + 4 caveat rider follow-ons (resolver-align, retry-net trigger, frozen-neck pin, shape-pin debt).

---

## Governance
Party-mode green-light precedes substrate dev; bmad-code-review before any done; NEW CYCLE (Codex T1–T10 → Claude T11) on substrate; cleanup-arc Claude-direct; Quinn→John chain on impasse before escalating to operator. No mocks; live APIs; first-run-stands; no retry-to-green; never leave the lockstep/manifest half-modified; push at checkpoints; no force-push/--no-verify.

**Automation:** `goal-clustering-followalong-trial.txt` (repo root) is the autonomous-goal statement driving Phase 1 → Phase 2 with live trial→review→repair cycles.
