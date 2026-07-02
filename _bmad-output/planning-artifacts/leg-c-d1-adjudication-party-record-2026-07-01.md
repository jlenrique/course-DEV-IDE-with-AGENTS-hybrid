# Leg-C D1 Adjudication — Party Record (2026-07-01, session 03)

**Arc:** Gamma Styleguide Library · **Branch:** `dev/gamma-styleguide-leg-c-live-2026-07-01` · **Story:** `leg-c-min-cluster-floor-scripted.md`
**Round type:** fully-spawned party (6 seats): Winston (arch) / John (PM) / Murat (test-arch) / Amelia (dev) + specialty Irene (Pass-1/content) / Dan (CD contract). Two rounds. **Outcome: UNANIMOUS 6/6 — RATIFY D1 NO-GO + REWIRE R3-with-R2-veto, baseline-first.** No impasse; Quinn/John chain not needed (round-2 evidence resolved the R2/R3/R1 split on each seat's own stated conditions).

## The finding (hard evidence, file:line — established pre-party, zero live spend)

1. **The Leg-C floor honoring is UNREACHABLE in production.** It lives in `app/specialists/irene/graph.py::_act_pass_1` behind `pass_phase == "pass-1"` (graph.py:2235-2242); `pass_phase` appears nowhere in `state/config/pipeline-manifest.yaml` or the runner. Production nodes 04A/05/05B dispatch `specialist_id: "irene-pass1"` = the SEPARATE module `app/specialists/irene_pass1/`; node 08 dispatches `irene` (pass-2 only).
2. **`app/specialists/irene_pass1/` has ZERO floor references** — a bound floor is live dead config; the AC#7 dead-config guard also lives in the unreachable branch (a fully closed loop of tautology — Winston).
3. **D-0 (Dan, hardened):** the real path has NO hidden-key strip at all — `irene_pass1/_act.py:154-155` embeds the full envelope payload into the LLM-visible prompt, so a bound floor LEAKS to the model: an uncontrolled re-parameterization of the clustering objective, in production today, violating the binding "never re-parameterize" amendment. The `_LLM_HIDDEN_PAYLOAD_KEYS` guard exists only in dead code.
4. **The REAL Pass-1 output contract** (golden run 8d819b8d @04A/05/05B + the emission prompt `irene_pass1/_act.py:161-201`): flat `plan_units[]` with the Epic-19/20c cluster vocabulary (cluster_id, cluster_role head|interstitial, cluster_position, narrative_arc, develop_type, parent_slide_id, cluster_interstitial_count) + lesson_summary + collateral. NO per-unit member sub-structure, NO figure/narration role tags. `cluster_floor.py`'s `_MEMBER_KEYS` expects a nested cluster-with-members shape — a straight type mismatch (Amelia).
5. **Keepable Leg-C substrate:** SSOT scripted block, validator rules, scripted-only accessor, Gary leak-guard, runner threading (`production_runner.py:1488`). Only the consumption seam is misplaced.
6. **R2's join target is dark by default** (Amelia, verified; Murat re-verified path `app/marcus/orchestrator/g0_enrichment_wiring.py:123-130`): G0 coverage_annotations exist only when `G0_ENRICHMENT_ACTIVE_ENV` is set (default OFF), and plan_units share no ID with SourcePoint anchors → pure R2 = a floor that never fires.

## Round-1 verdicts
Winston R3 (+W-1/W-2) · John R2 (J-1..J-4) · Murat R2-conditional ("R1/R3 only if R2 provably can't deliver"; M-1..M-3) · Amelia R3 (A-1..A-4; the flag-OFF evidence) · Irene R3 (I-1..I-4; corpus ruling) · Dan R1 (D-0..D-3). NO-GO ratified 6/6 in round 1.

## Round-2 (evidence circulated) — CONCUR 6/6
- **John:** withdraws J-1 ("machinery that's flag-OFF by default … isn't proven-live for this join"); accepts baseline-first ("three jobs on one dispatch"). Scope guardrail: port mechanically, file improvements, protect Leg-D runway.
- **Murat:** reserve clause resolved ("provably can't deliver" met); CONCUR with M-1/M-2/M-3 verbatim + baseline-validity-four + **condition 5: the floor-off control run must assert ZERO floor bytes reach the prompt**. "The R2 veto discipline is what makes R3 acceptable — remove it and my concurrence goes with it."
- **Dan:** withdraws R1 on Winston's anchor-vs-structure distinction ("I was proposing a governed version of the thing I policed"). Precision holds: **the strip keys off the scripted NAMESPACE, not a hand-listed key**; **AC#7 confirms anchors carry no scripted value/hint (byte-identical model input with/without a bound floor survives the rewire)**.

## RATIFIED DESIGN — R3 with R2's veto discipline

Pass-1 (irene_pass1) additionally emits per-plan-unit **`source_refs[]`** — verbatim anchors into the source it already had in context (an ANCHOR emission — citations of work already done — not a STRUCTURE emission; the never-re-parameterize amendment holds). The deterministic honoring derives split seams FROM THE SOURCE at those anchors; splits land as new interstitial plan_units in the EXISTING cluster vocabulary (parent_slide_id = head, cluster_role interstitial, head's cluster_interstitial_count incremented). Role classification at seams uses the fixed vocabulary **{figure, narration, claim}** via the existing verbatim-anchor machinery (deterministic; no new anchor format). **Veto discipline (binding):** unresolvable / ambiguous / malformed / role-unverifiable ref → REFUSE via the soft styleguide-vs-content mismatch — never guess-and-split. Figure↔narration atomicity inviolable; keep-dense singletons protected; assessment/knowledge-check units floor-exempt by construction.

## BINDING AMENDMENTS (consolidated)
- **W-1** R2 fail-safe folded into R3 (unresolvable anchor → soft-mismatch refuse). **W-2** follow-on: delete the dead `_act_pass_1` floor plumbing from `irene/graph.py` once the moved module is live-proven (no shared/duplicated honoring).
- **J-3** the D-0 prompt-leak strip ships IN the rewire story as a DISTINCT commit (clean revert point). **J-4/M-3 = new AC#14:** production-dispatch-path pin — resolve the manifest's specialist_id set to real modules; the floor-consuming module must be in the resolved set; **lands FIRST, before the rewire**; non-waivable.
- **M-1** AC#9's arbiter = the same on-disk artifact the dispatch-path pin resolves to. **M-2** rewired AC#4/5/6 fixtures are generated FROM the live baseline's on-disk output, sha256-pinned + drift-checked; the AC#11 teeth-witness re-runs AFTER the rewire. **Murat-5** the floor-off control asserts zero floor bytes in the prompt/carrier.
- **Baseline validity (all four):** real adapter payload assembly; real `make_chat_model` binding; corpus staged exactly as node 04A stages it; first-run-stands (a surprising K is data, not a retry trigger). **Winston-iii:** capture the raw model output verbatim into evidence.
- **A-3** port `cluster_floor.py`'s split/atomicity/soft-mismatch engine — do NOT rewrite; only the member-detection layer becomes source_refs seam derivation. **A-4** 05/05B refinement passes carry `source_refs` forward on plan_units (no re-derivation); refuse-floor if refs absent.
- **I-3** role tags fixed at {figure, narration, claim}; expansion = fresh party round. **I-4** knowledge-check/assessment units floor-exempt, pinned by a regression test.
- **D-0** hidden-key strip in irene_pass1 keyed off the scripted NAMESPACE (blocking AC before any live-consumption claim). **D-1** dead-config guard co-located with the dispatched module. **D-2** CI import-reachability assertion: a registered scripted class's consumer must be reachable from the production dispatch graph (dead consumer fails CI). **D-3** AC#7 discriminating pair rewritten against irene_pass1 + anchors carry no scripted hint.
- **Dan honesty disclaimer (verbatim, into the story):** "The scripted channel conveys CD style-identity intent (SSOT → validator → accessor → leak-guard → runner threading) faithfully to the runtime boundary; per-class consumption at the real Pass-1 surface is corrected and live-proven only for `min_cluster_floor`, and scripted-as-general-intent-language remains out of scope."
- **2nd-class rider** (deferred-inventory `gamma-scripted-2nd-class-admission`): at 2nd-class admission, re-evaluate an R1-style member-structure emission against TWO concrete classes, with its own eval cycle.
- **Irene product framing (honest claim):** chunk-by-default means a well-behaved Pass-1 on dense source already lands near the floor — the floor is a BACKSTOP for styleguide/content mismatches, not the mechanism doing the pedagogical work.

## CORPUS RULING (Irene, ratified)
Part-3 slice (`course-content/courses/tejal-c1m1-p3-opportunity/part3-opportunity-clinician-innovator.md`, extracted verbatim from `tejal-c1m1-fresh-outline/source-outline.md:492-580`, 2296 words). AC#9/AC#12 material = the two Design Briefs (genuine internal composition seams; distinct figure+narration units legitimately splittable). AC#13 negative controls = Slides 1-4 + the Intrapreneurship-formula block (bonded figure+narration / continuous claim → refuse). Keep-dense witness = the Part-3 Summary slide (must NOT split at any floor). Knowledge check included as an exclusion boundary (floor-exempt by construction; splitting a Q&A block = hard bug). Expected legitimate-seam capacity: ~2 of 9 units support a real split.

## SEQUENCING (ratified)
1. **Floor-off LIVE baseline** (this session, immediately): real `run_production_trial` walk on the Part-3 corpus, weed-clearing approve G0/G0A/G0B/G1, STOP at G2 → capture both irene_pass1 contributions (04A creation + 05 refinement) verbatim; count_K = distinct cluster_ids; zero-floor-leak assert. Triple duty: M-2 fixture source + Winston-iii raw capture + AC#9 control-K.
2. **AC#14 dispatch-path pin** (lands first), then the **R3 rewire** RED-first via a spawned dev agent (D-0 strip as a distinct commit), 3-lane review discipline per arc governance.
3. **Floor-on differential + K′ determinism pin + AC#9-13 live proof** through the same driver, then dual-gate CLOSE (Murat structural + Irene content; 07G non-waivable).

**Live-spend authorization:** ~3 Pass-1-bearing walks (K, K′, T) on the agreed corpus — party-authorized this record.

---

## CLOSE ADDENDUM (2026-07-02) — DUAL-GATE CLOSED

**Murat (structural): CONCUR-CLOSE** (independent on-disk re-verification: 153-test battery; count_K=7 from both control trials; T3 `00db047c` single-walked, 04A=10 no-op / 05 fires honoring / 05B arbiter 8 distinct incl. `c-u04#f1`; AC#13 tag confirmed; all four conditions discharged/filed; F1/F2 ruled legitimate remediate-then-new-arm, not retry-to-green). **Irene (content): CONCUR-CLOSE** (split shape pedagogically legitimate — model-declared seam promoted to cluster boundary; keep-dense + assessment exemption re-witnessed; backstop sequence exactly as framed; AC#12 by-construction + disclaimer; conditions confirmed filed).

**Live-proof headline:** the CD-declared `scripted.min_cluster_floor` was honored DETERMINISTICALLY on a real production walk — anti-vacuous differential 7 < 8 ≤ 8, minted cluster + provenance on-disk, honest refusal at N=20 live at $0 downstream, zero floor bytes in any LLM prompt. Three live-only defects (D1-class alias threading; anchor punctuation debris; the T2 double-walk race — now the pause-write-atomicity reproduction fixture) were found ONLY because the proof was live — the incremental-live-testing doctrine's strongest witness this arc.
