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

## Status
- **Leg-1a: ✅ DONE — party-CLOSED 2026-06-30, live-proven.**
- Leg-1b (warm_callback authoring + Vera-R7): queued; **DUAL-GATE** per Murat. Party GREEN-LIGHT required before dev opens.
- Leg-3 confirm spike: queued (read-only, anytime before Leg-3 green-light).
- Legs 2 / 4: queued.
