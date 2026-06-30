# Concierge Production Substrate arc — party record (SSOT)

Branch: `dev/concierge-production-substrate-2026-06-29` (fresh from master `6f72ee30`). Class S.
Opened 2026-06-29. This file is the SSOT for agreed decisions across the arc.

## Arc framing (operator-set)

**Terminal DoD:** one concierge true-production deck + motion + workbook + Descript run on prepared substrate.

**Four legs (operator order: 1 → 2 → 3 → 4):**
1. Wire REAL Irene `rhetorical_role` emission + strong text-direction wrapped into `callback` — KEYSTONE (de-inerts last arc's enhanced-vo v3 tag channel, which is inert because the role was only ever set via an A/B override, never emitted by Irene).
2. Validate motion bundle composition (deck+motion B2/B3) for a real run.
3. Bring `callback` + intelligent clustering online.
4. Tighten asset/fidelity ledgers (UDAC run-asset-index + fidelity firewall).

**Operator scope rulings (2026-06-29):** full-mix blind A/B DROPPED (no requirement of any kind); deck→Descript publish already proven; Irene `rhetorical_role` emission is indispensable.

**Governance:** autonomous run, gate at story CLOSES + genuine impasse. HARD per-component live-test gate (real-API, no mocks; no workstream advances past a new/edited component until it is live-tested, or an honest live-FAIL is recorded as a finding). BMAD spine per story: party GREEN-LIGHT → bmad-create-story (+validate) → bmad-dev-story RED-first → bmad-code-review → party CLOSE. Party = canonical core + ≤2 specialty; Dr. Quinn synthesizes; John/PM tiebreaks only at impasse.

## Round 1 — GREEN-LIGHT (2026-06-29)

**Voices:** John (PM), Winston (Architect), Amelia (Dev), Murat (Test Architect), Irene (Instructional Architect), Dan (Creative Director). Grounded in a fresh read-only substrate scout (file:line verified).

**Outcome: GREEN, strong consensus, no impasse.** All six green-light the 4-leg decomposition + ordering. Leg-1 RATIFIED as a SPLIT (operator-confirmed):

### Leg-1a — deterministic de-inertion (keystone, ships first)
- Extend `_role_derived_seeds_for_deltas` (`app/specialists/irene/graph.py:1121`) so each per-slide seed carries `rhetorical_role`; de-inert the read site (`app/specialists/enrique/_act.py:528→531→547→554`). Additive, zero contract change (`VoiceDirection.rhetorical_role` already declared, `pass_2_template.py:212-216`; `_overlay` copies arbitrary keys, `voice_direction_annotation.py:219-225`).
- Prove live on the 3-slide slice with **`contrast_emphasis`→[slow]** (tonal; authors zero new words → no containment risk).
- **Close bar (Murat + Winston + Amelia):** (1) emission is REAL not injected — run with the A/B override removed, role still appears; (2) receipt shows the EFFECTIVE model flipped to v3 (assert effective model at the read site, not just the flag — Winston); (3) provider tags exact-match the role→tag table AND one of the 6 fail-loud unmapped roles is exercised live and raises (Murat); (4) distinct real request_ids; (5) captions == canonical byte-level, zero tag leak, with a deliberately-leaking fixture proving the test catches a leak (Amelia). Fully RED-first.

### Leg-1b — structural callback (bundled, ships after 1a)
- Pass-2 callback-shaped AUTHORING **delegated to a writer** (Paige/Sophia/Caravaggio) — Irene's correction: she does NOT author the warm line herself; she owns pedagogical intent + the anchor reference + behavioral-fidelity validation at handoff.
- Wire **Vera-R7 source-containment** (`audit_rhetorical_source_containment`, `voice_provider_text.py:267-350`, currently PROVIDED-BUT-UNWIRED) **with teeth** — Murat: inject an authored callback containing a numeral/term absent from source, assert R7 catches and blocks it ("I will not accept R7 as wired until I've seen it reject something").
- Populate `warm_callback`→[warm], proven on a deliberately HAND-ANCHORED slice so the callback is genuinely real.
- **Binding rule (Murat + Irene + Dan):** structural LLM authoring and its containment gate are INSEPARABLE — never ship authored learner-facing (medical) audio text with the firewall built-but-off. `contrast_emphasis` (tonal, text-preserving) may emit before R7 is wired; authored `warm_callback` text may NOT.
- **CRAFT verdict explicitly deferred to Leg-3** (Dan + Irene): a callback is hollow without a real anchor + separation, which only real cluster/sequence structure produces. Leg-1b proves mechanics + containment, NOT that the callback "lands."

### Cross-cutting decisions (adopted)
- **Leg-3 confirm-scope spike** — read-only `bmad-investigate` resolving whether clustering is actually dormant, BEFORE Leg-3 is specced. Scout could NOT corroborate the prior-note claim that "Pass-1 dropped cluster emission" — `normalize_clusters` + emission instructions still live (`app/specialists/irene_pass1/_act.py:161-201,264-398`). Does not gate Legs 1–2.
- **Roles:** populate only `contrast_emphasis` (1a) + `warm_callback` (1b). Do NOT widen the role→tag table in Leg-1 — the 6 fail-loud unmapped roles are correct posture. Named follow-on: "role→tag table widening, roles 3–8", trigger = after the keystone proves the two-role path end-to-end on a real run. Irene's pedagogy-priority next roles (post-Leg-3 seeding): `definitional_anchor` (the anchor-registry that earns honest callbacks) → `clinical-caveat` (highest safety yield) → `enumeration`; defer inherently-cross-slide roles (e.g. `summary_synthesis`) to post-Leg-3.
- **Honesty mechanisms replacing the dropped A/B** (Dan): a **named-beat ledger** (Pass-2 records one sentence per emitted role — *why this beat earned this role*; hollow sentence = hollow read) + **one operator ear-check on the real clustered deck at Leg-3** (not a forced-choice gate — "keep the ear, drop the ceremony").

### Scout-flagged contradictions vs prior-session notes (corrected)
1. No `render_strategy:v3` exists — v3 is keyed on effective MODEL == `eleven_v3`.
2. Enrique read site is `enrique/_act.py:97-110,239-261`, NOT `graph.py:993` (that line is inside Irene's graph.py).
3. "Pass-1 rebuild dropped cluster emission" NOT corroborated — confirm via the Leg-3 spike.
4. The live-key "`os.environ.pop OPENAI_API_KEY`" recipe is an auto-skip guard, not a literal pop; proven live mechanism is `load_dotenv(.env, override=True)` + sentinel-guarded key.

**Dissent noted (not an impasse):** Dan framed it as "one leg, don't split the emit/author/contain triangle" — reconciled, because the split keeps author+contain together in 1b and 1a takes only the tonal role that authors nothing.

## Round 2 — Leg-1a CLOSE (2026-06-30)

**Voices:** Murat (Test Architect), Winston (Architect), Irene (Instructional Architect). **Outcome: UNANIMOUS CLOSE, no conditions, no impasse.**

What shipped: closed `PEDAGOGICAL_ROLE_TO_RHETORICAL` table (`synthesis → contrast_emphasis`; all other pedagogical_roles → `None`) + import-time exhaustiveness guard + fail-safe accessor in `app/marcus/orchestrator/enrichment_consumption.py`, threaded additively onto the role-derived seed in `role_to_voice_direction`. De-inerts the already-shipped (enhanced-vo-2) Enrique v3 consumer + compiler.

Evidence: offline 91 passed (touched) + 406 regression; ruff clean; lint-imports only pre-existing C3 (M3 KEPT). **LIVE gate PASS** (real ElevenLabs ~$0.052, first-run-stands): both segments `render_mode=v3_provider_text`, effective model `eleven_v3`, `provider_text_tags==["[slow]"]`, distinct real request_ids `YFOlLfEgaezZuZ0uCVbj`/`9erzIMO53zxtlqH9rK8S`, captions==canonical. Evidence `evidence/concierge-leg1a-live-gate-20260630T021715Z.json` + harness `evidence/concierge-leg1a-live-gate.py`.

3-layer adversarial review (Blind Hunter / Edge Case Hunter / Acceptance Auditor): **0 MUST-FIX.** Triage:
- **SHOULD-FIX, remediated:** (Auditor NIT-1) unpopulated-role list now pinned == `RhetoricalRole` taxonomy minus populated (self-guards drift). (Edge #1) on a v2 directed run a synthesis segment's receipt `effective_voice_direction` records `rhetorical_role` (model_dump not v3-gated, `_act.py:838-839`) while audio/cost/provider-block stay byte-identical — **RULED faithful-record** (Murat + Winston + Irene): the receipt honestly records authored intent; the v3 gate stays solely in the consumer; pinned by `test_leg1a_v2_directed_synthesis_records_rhetorical_role_but_sends_canonical`.
- **Follow-on (ratified):** Edge #2 `directed-voice-override-cannot-suppress-rhetorical-role` — `_overlay` skips `None` so an override can't suppress a role-derived role to `None`; consistent with the existing tone-field limitation; narrow scope; filed in deferred-inventory.
- **NITs (no action):** Blind Hunter accessor unknown-vs-None distinction; live-harness reproducibility (harness committed).

**Binding forward rulings (for the record):**
- **Murat:** **Leg-1b is DUAL-GATE.** The moment a role authors NEW lexical content, "faithful-record" stops being a receipt question and becomes a content-fidelity question — his warm_callback/Vera-R7 teeth bar binds there.
- **Irene:** keep the `contrast_emphasis` vocabulary honest as the map grows (the tag behaves as intrinsic *measured emphasis*, not relational cross-slide contrast). And **`clinical-caveat` carries a containment obligation** — when the next roles (`definitional_anchor`/`clinical-caveat`/`enumeration`) open, clinical-caveat travels with Vera, NOT on the synthesis (zero-new-words) precedent.
- **Winston:** if an operator-facing "what will actually render" view is ever needed, it is a *projection over* the faithful receipt computed at the read site with model-awareness — never a mutation of the authored record.

## Round 3 — Topic-Coverage-Assurance Interlock amendment (2026-06-30)

**Trigger:** operator deferred Leg-1b to insert a coverage-assurance interlock first (briefing `claude-code-brief-topic-coverage-assurance-before-leg1b-2026-06-29.md`). Required deliverable: an operator-facing PRODUCTION REPORT accounting for ALL points in the course SOURCE NOTES (= per-slide presentation/speaker notes), each mapped to slide screen OR narration (or signed exclusion).

**Voices:** John (PM), Winston (Architect), Murat (Test), Irene (Pedagogy), Vera (Fidelity); **Dr. Quinn synthesized.** Grounded in a reuse-first scout (CONTAINMENT exists everywhere; source→deliverable COVERAGE genuinely ABSENT; `TypedComponent.component_id` ≈ a source point; P5 consumption already wired but emits no back-receipt; UDAC RAI is the receipt infra; presentation notes = a markdown convention extracted as ONE narration component per block, NOT atomized; Storyboard-B HTML is the report surface).

**Core contradiction (granularity/ingest):** Winston (ride `component_id` 1:1, no new id space) vs Irene (the honest unit is the teaching ASSERTION, ~2–4 per block, needs re-segmentation + first-class notes ingest, NON-NEGOTIABLE).

**Dr. Quinn synthesis (dissolved the fault line, 5/5 ACCEPT, NO impasse → no PM tiebreak):** separate *identity space* from *unit of accounting*. `source_point_id = component_id#ordinal` — a CHILD sub-locator inside the existing id space (no new namespace, no new source_type → Winston satisfied), while the denominator iterates over assertion-level children (→ Irene satisfied). Segmentation staged behind a T0 spike with a `segmentation` provenance stamp as the honesty fuse.

**OPERATOR RULING (overrides Quinn's staged-fallback):** **assertion-level required FIRST.** `block_level_v1` is a diagnostic only, NOT an acceptable v1 ship state; if assertion-level re-segmentation proves unbounded in the T0 spike, ESCALATE — do not ship coarse.

**Ratified v1 contract** (full detail: `coverage-assurance-interlock-design-2026-06-30.md`): child-id identity; coverage-intent as a SET (derived-first, LLM-refine-at-ambiguity, operator-signed exclusions; slides=gist/narration=detail default, BOTH for LO-load-bearing/safety/organizing-claim); two orthogonal axes (coverage × containment) joined never merged; risk taxonomy → deterministic verbatim floor + R7 binding; per-cell `vouch_level` honesty fuse; deterministic locator anchor FIRST (no anchor → forced `missing`); fail-loud-before-audio on `must-cover ∧ missing ∧ no-planned-surface` at the both-walks UDAC seam; receipt DERIVED from existing joins (no producer self-report, no parallel ledger) on the RAI; rendered to Storyboard-B HTML; additive → out of block-mode. R7 binds in THIS interlock at report-gen time (its first reporting caller).

**Three binding AC caveats:** (Winston) child-id is NEVER a join key; (Vera) render-time assertion — no cell renders `verified` without a `vouch_level`; (Irene) the provenance stamp is load-bearing, not droppable.

**Leg-1b amendment dispositions:** #1 structural gate (callback cites anchors, referential-integrity), #4 gate (+ negative-case demo), #5 keystone hard gate; #2 → WARN field; #3 split (numeric/term introduction gates, comparator/negation flip WARN).

**Deferred (named):** deterministic corpus matcher; full Leg-4 UDAC; workbook gating; hard verbatim enforcement; ≥3-run-calibrated WARN→gate promotion; span-aware negation/comparator detector (Vera-R7 hard-gate triad).

## Round 4 — Coverage interlock RUNNER-INTEGRATION approach (2026-06-30)

**Trigger:** 3-layer adversarial review found the offline foundation clean but the gate INERT in a real run (producer chain unwired) + a dead gate-predicate term. Operator: remediate-now-then-close. Contained fixes landed (gate predicate, detail_in_narration, empty-response alarm, assertion_level gate, contractions, default-path timeout; 80 tests). This round ratifies the runner-integration approach.

**Voices:** Winston, Marcus (runtime owner), Murat, Amelia. **4/4 consensus, no impasse** (render fork resolved unanimously to B1; no Quinn tiebreak needed). Grounded in a read-only integration scout.

**Ratified approach:**
- **PASS attach** mirrors P3 pedagogy: `_attach_coverage_annotations` after `g0_enrichment_wiring.py:1004` → constructor `:1041` (same dispatch_live + chat_model_factory; card firewall prunes empty → byte-identical OFF).
- **Derive+write+gate at the G3 storyboard-publish seam**, ONE shared helper called at BOTH walk sites (`production_runner.py:2153` start + `:2873` continuation), guarded `gate_id=="G3"`. The continuation walk is the live path (start walk stops at G1 — the two-walks gotcha [[project_production_runner_two_walks]]); both for safety. The fail-loud gate at `_dispatch_specialist_at_node:1844` is walk-invariant (universal dispatch chokepoint).
- **Marcus keystone — gate FAIL-LOUD on missing-receipt-at-audio** (not the provisional no-op): if enrique is about to dispatch past G3 with no receipt, RAISE. A dev flag preserves the no-op for intermediate-integration shippability (Amelia); shipped default = fail-loud. Closes the bypass review found at its root.
- **Anchor join-key reconciliation (FORK A):** one source-ordinal spine keyed on coverage `SourcePoint.slide_key`; deck side via reused enhanced-vo-1 `_resolve_slide_key_map` (source_ref→plan_units; absorbs clustering — NOT the flag-gated segment write-back); narration from the component's own `Slide N` locator. **`build_coverage_anchors(gary_slide_content, joined_narration, slide_key_map, ambiguous_ordinals) → dict[slide_key, AnchorResolution]` is a PURE function with the reconciliation passed IN** (Amelia) → offline-testable; the only live seam is a ≤20-line marshalling adapter with a loud receipt-level diagnostic on unresolved joins. v1: narration_text reads from the component (follow-on: verify vs published segments when slide_key is unconditional).
- **Render (FORK B → unanimous B1):** standalone `coverage-report.html` via the built `render_coverage_section` + run_summary link + `coverage_plan_view` on the G0E card; legacy `generate-storyboard.py` UNTOUCHED. Receipt JSON = machine truth (RAI); HTML = human view. AC10 satisfied-by-intent (deviation rationale recorded).
- **FORK C:** `project_ambiguous_narration_ordinals(card)→set[str]` (the :335 0/>1 drop), sharing the candidate block at `enrichment_consumption.py:313-333` via an extracted helper (no duplication).
- **RAI register:** `GATE_ASSET_MAP["G3"] = AssetSpec(coverage-receipt, CANONICAL_SHA256)`; `_udac_ratify_gate("G3")` picks it up like g0-enrichment at G0E. **Receipt body MUST be canonicalized + idempotent** (sorted keys, NO volatile timestamps/run_id in the hashed projection; recompute-from-surfaces never append) so the SHA pin survives the resume/recover G3 crossing (Winston+Murat). Empty-coverage → PASS-vacuous, never crash/block.

**Build sequence (Amelia):** Step 0 pure core (resolve_slide_key_map / :335 projector / build_coverage_anchors / derive+write) all offline RED-first; Step 1 PASS-attach; Step 2 RAI row; Step 3 render; Step 4 the live marshalling adapter (pre-capture real `gary_slide_content`/`joined_narration` shapes first → live trial = confirmation); Step 5 one `studio-smoke-min` live trial. Steps 0-3 are independently mergeable (gate tolerates absent receipt until the adapter lands).

**Integrated re-prove CLOSE bar (Murat):** one runner-emitted A→B→C→D chain (coverage pass in g0-enrichment.json → receipt written at G3 reconcilable to the run's own deck+narration surfaces → RAI entry → gate raises CoverageAssuranceError → paused-with-coverage-tag) with **provably ZERO ElevenLabs spend on the block path** (die-on-this); a discriminating pair (genuinely-uncovered block via upstream ablation — NEVER a hand-edited receipt — + a covered-only run that sails to real audio); the continuation-walk read proven across a REAL pause/resume (not a structural test); the fuzzy axis (altered/risky, negation/comparator) confirmed ledger-only with the block-cause tag hard-axis only; real gpt-5, first-run-stands. Trial: `studio-smoke-min`, G0-enrichment live, an uncovered must-cover point → gate raises before enrique = $0 ElevenLabs; pauses at G3.

## Status
- **Leg-1a: ✅ DONE — party-CLOSED 2026-06-30, live-proven.**
- **Coverage-assurance interlock: party-RATIFIED (5/5, no impasse) + operator granularity ruling applied; design record written; awaiting operator sign-off to open `bmad-create-story`.** Sequenced AHEAD of Leg-1b.
- Leg-1b (warm_callback authoring + Vera-R7): queued BEHIND the interlock (consumes its source-point anchors); **DUAL-GATE** per Murat. Needs its own party GREEN-LIGHT before dev.
- Leg-3 confirm spike: queued (read-only, anytime before Leg-3 green-light).
- Legs 2 / 4: queued.
