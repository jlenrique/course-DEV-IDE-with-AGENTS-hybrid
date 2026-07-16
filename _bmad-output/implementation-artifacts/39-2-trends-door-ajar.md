---
id: 39-2
epic: 39
key: 39-2-trends-door-ajar
status: review
anchor_provenance: post-38-2-T4 tree at commit 19c3e73e
baseline_commit: 5e688cca0df19fb4c43ef8ff128e2ec301b43c95
anchor_reverification: anchors re-verified at 468de34f (artifacts-only diff since baseline); re-verified again at dev baseline 5e688cca
---

# Story 39.2: Trends / Hot-topics as the Door-Ajar

Status: review

## Story

As the learner,
I want a bounded "where the field is going" callout scoped to my abilities — composed from the finely-focused Ask-B hot-topics research pass, not from the broad generic research smear,
so that the lesson opens a forward quest that is honest, packet-grounded, and never forecasting theater (FR9 + epics §6.1 beat-4).

## Dependency Position

`38.0 → 38.3b → {36, 37.1, 37.2a, 37.3, 37.4} → 38.3a → 38.1 → 37.2b → 39.1 → 38.2 → 39.2 → 40.1`

38-2 (`38-2-ask-b-hot-topics-wiring`, re-homed key verbatim) is **`done-awaiting-live-witness`** at HEAD `468de34f` (A-1, green-light 2026-07-16): its component probe attempt `79f1920e` returned **PASS_USABLE_MINT** (9/9 judge criteria; witness `ask-b-38-2-live-79f1920e` frozen + enrolled, STRICT 27/27). Nothing gates this story's deterministic work: the Ask-B contract family, the strict reader at `ask_b_hot_topics@07W.4`, and the `_valid_ask_b_output` fixture idiom are all landed and pinned — and a REAL usable frozen Ask-B pack now exists for fixture grounding (M-5). The formerly-pending probe-verdict branches on run-B boarding posture are RESOLVED-COUNTERFACTUAL (see §Provenance — M-5/J-2 rider, per A-2 + J-1 + J-2). This story is the SOLE consumer of the Ask-B packet (ratified Epic-38 graph-shape record) and blocks 40.1 only through the wave batch-run sequencing, not through code.

## Provenance & Dependencies

**Landed 38-2 substrate (verified in the tree at `19c3e73e` — HEAD at authoring time):**

- `app/marcus/lesson_plan/ask_b_hot_topics.py` — the strict, frozen, extra-forbid Ask-B contract family: entries carry `ask-b-cite-###` citation ids (natural-width `{3,}`, L335), ordered `supports_ability_ids` + ordered `matched_ability_tokens` evidence pairs, full credibility fields (tier/peer/provenance/triangulation), and `known_losses` including the scope-loss lattice (`scene_identity_absent`, per-ability `ability_association_basis_absent:<id>`). Dispositions: 3 typed retryables + `completed_empty` / `completed_degraded` / `completed_ready` (L73–80).
- `app/marcus/lesson_plan/research_packet.py` — `resolve_for_hot_topics(run_dir, require_usable=...)` (L382–392) resolves exactly `ask_b_hot_topics@07W.4` through the STRICT Ask-B reader branch (L228–244, the 38-2 AC 3 decided mandate) with the duplicate-contribution collision guard (L178–195). Generic `04.55` leniency is coordinate-exact-untouched and re-pinned by 38-2.
- **Sole-consumer contract (keys on specialist/node identity, not story number):** `specialist_id=ask_b_hot_topics`, `node_id=07W.4`, own witnessed `packet_digest`, **39.2 sole consumer** — per the ratified Epic-38 graph-shape record ("**39.2 re-points** trends → Ask-B").
- The 38-2 boundary pin THIS story consciously flips: `tests/unit/marcus/lesson_plan/test_ask_b_trends_consumer_pin_38_2.py::test_trends_inputs_from_run_is_not_repointed_to_ask_b` (L89–95) — deliberately authored in a NEW module (38-2 A-4) precisely so this story's re-point opens conflict-free.

**Inherited obligations (BINDING — deferred-inventory §"Story 39.2 grooming", J-3 handoff rider filed at 38-2 green-light):**

1. **The re-point:** `trends_inputs_from_run` / the trends consumer path re-points from the generic `04.55` packet to the Ask-B packet (`ask_b_hot_topics@07W.4` via `resolve_for_hot_topics`). 38-2 deliberately left `trends_projection.py` at ZERO lines changed (scope fence); the boundary pin flips consciously here.
2. **Post-re-point `reject_model_prior_topic` pin:** re-assert the ungrounded-topic `unusable` marking against the Ask-B packet **through the re-pointed consumer path** (38-2's pin exercised it against a hand-resolved Ask-B packet; this story proves it through `trends_inputs_from_run` itself).
3. **FR16 (Ask-B leg) + FR9 wave-close assertion:** asserted at the Epic-39-wave close bar by 38-2 + 39-2 together. 38-2's close records only its half (packet minted + witnessed); THIS story's close record must assert BOTH FR16's Ask-B leg and FR9 (the rendered Door-Ajar half) — see AC 7.

**Paid-Run Economy Protocol rider (BINDING — wave-3940 party record §D3):** this story is **DETERMINISTIC-CONSUME** — the Ask-B packet is minted upstream at `07W.4`; this story adds **NO new LLM surface** ⇒ **NO component probe owed** (D3 plank 3 governs new LLM surfaces only; precedent: 39-1b boarded run B-eligible on suite-green with no probe). It boards **governed batch run B** (after 38-2 + 39-2 + 40-1) on suite-green. Riders:

- **Per-story verdict line (M-D3-3 / John F1–F2):** the run-B evidence pack carries a verdict line for this story keyed to the rendered Door-Ajar — the `## Research Trends` section of the terminal `07W` presentation-support deliverable composed from the `ask_b_hot_topics@07W.4` packet. REACHED+PASS = witness; NOT-REACHED = the claim stays OPEN (no-evidence — never pass, never fail); "aboard" ≠ tested.
- **Same-diff deliverable-bar clause (plank 5, Winston D3-2):** the machine-asserted runner bar (`_assert_completed_workbook_deliverable` in `scripts/utilities/marcus_spoc_live_test_runner.py`) gains a trends/Door-Ajar clause **in THIS story's diff** — per-story DoD, never "next touch" — with negative-witness pins (M-D3-2b): the bar is fed known-bad mutated frozen shapes and must REJECT (AC 6).
- **M-5/J-2 empty-packet acknowledgment rule — RESOLVED-COUNTERFACTUAL at green-light (A-2 + J-1 + J-2, 2026-07-16):** 38-2's probe attempt `79f1920e` returned `PASS_USABLE_MINT`, so the `completed_empty`-boarding branch never fires: **no governed acknowledgment line is owed, and the usable-mint half is CLOSED** (not OPEN). The design principle stands timelessly — a persistently-empty Ask-B yields an empty-honest Door-Ajar, **the designed honest outcome, not a defect** — and the three empty classes (AC 4) plus the conforming-empty bar pin (AC 6 / matrix row 12) are KEPT as timeless defense pins, never "fixed" into refusals. AC 7's expected run-B evidence for this story now defaults to a **USABLE Door-Ajar render**; an empty-honest render is acceptable ONLY if the live run legitimately mints empty — recorded honestly in the verdict line, never failed, never retried-to-green.
- **Status vocabulary:** pre-run-B status is exactly `done-awaiting-live-witness  # deterministic+review green; no probe owed (deterministic-consume, D3 plank 3); full-run witness owed by batch run B` — the flip to `done` cites the witnessing run id. Never overload `in-progress`; never early-`done`.

## T1 Readiness (BINDING)

The dev agent MUST read, in order, before any code:

1. `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — §Story 39.2 (the original AC: FR9 + §6.1 beat-4 — Door-Ajar composes the Ask-B (38.2) trends/hot-topics as a standard review beat via the existing `trends_projection` render, honest + bounded, empty-honesty when thin) + §"Epic 38 graph-shape decision — RATIFIED" (three-packets table: `ask_b_hot_topics@07W.4`, Door-Ajar/trends (39.2) is the sole consumer; "**39.2 re-points** trends → Ask-B").
2. `_bmad-output/planning-artifacts/deferred-inventory.md` §"Story 39.2 grooming" — the three J-3 inherited obligations + the M-5/J-2 operator note (verbatim authority for §Provenance above).
3. `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — §D3 (all six planks + amendments; especially plank 5 same-diff bars, M-D3-2b negative-witness pins, M-D3-3 batch attribution, John F2 status vocabulary, M-5/J-2 probe verdict licensing).
4. `_bmad-output/implementation-artifacts/38-2-ask-b-hot-topics-wiring.md` — AC 4 (empty-honesty + the consumer-side pin this story supersedes through the re-pointed path) + AC 8 (the downstream boundary this story now crosses by design) + AC 9 (probe verdict classes; run-B boarding rider).
5. Landed substrate (real anchors, re-verify at T1 — all verified in the tree at `19c3e73e`):
   - `app/marcus/lesson_plan/trends_projection.py` — `trends_inputs_from_run` (L305–319; the `resolve_for_trends_projector` call at L313 is THE re-point site); `project_trends_from_packet` (L215–302; injected-topic guard L283–285; the two projection-level empty branches L228–237 + L287–296); `reject_model_prior_topic` (L173–212 — **this is where it actually lives**: consumer-side, grounds a topic against packet-entry titles, returns `confidence="unusable"` when ungrounded); `render_trends_markdown` (L340–405: explicit-empty branch L343–352, `#### Research trends` / `#### Hot topics` beats, `#### Rejected / unusable topics` honesty block, the anti-theater line L383–385); `_strip_inline_comments` (L325–337); `TRENDS_WRITER_REQUIRED_MARKER` (L24); `ResearchTrendsBrief.usable` (L94–99).
   - `app/marcus/lesson_plan/research_packet.py` — Ask-B literals (L32–33); strict Ask-B reader branch (L228–244); `_empty_packet` (L122–147); status/loss machinery (L289–303: `research_entries_empty`, `research_entries_all_invalid`); `resolve_for_hot_topics` (L382–392); `resolve_for_trends_projector` (L360–366 — stays byte-untouched, see AC 1); `ResearchPacket.usable` (L86–89). **Trigger row — expected touch ZERO** (§Lockstep).
   - `app/specialists/workbook_producer/_act.py` — L1217 `research_trends = trends_inputs_from_run(run_dir)` (the sole production call site — default caps, no injected topics); source_ref_manifest joins L1218–1226; `_sidecar_refs` L1577–1598 (**substrate fact: NO trends receipt is persisted on the 07W contribution** — unlike glossary (07W.3 contribution authority) and exercises (persisted `exercise_composition` receipt); the bar's structured authority is therefore the deterministic recompute from `run.json`, AC 6). Expected touch ZERO.
   - `app/marcus/lesson_plan/workbook_producer.py` — L1034–1045: the Research Trends block is appended after References with heading `## Research Trends` (level-2, L1045) **unconditionally in BOTH render profiles** (legacy + presentation_support) — the bar clause therefore scopes to presentation-support sentinel deliverables per the 39-1 idiom (AC 6). Expected touch ZERO.
   - `scripts/utilities/marcus_spoc_live_test_runner.py` — the bar-clause idioms to mirror: `_assert_glossary_conformant_markdown` (L1312–1338 docstring = the structured-artifact-first + MD-floor pattern; P15 no-authority refusal L1350–1362; `_md_section_body` sectioning; heading-singularity counting L1378) and `_assert_exercise_composition_conformant` (L1600–1618; R3-style tolerance L1669–1675); the call spine `_assert_completed_workbook_deliverable` (L1882–1939 — the new clause is invoked there, after the exercise clause); sentinel constants L1239–1244 (`_PRESENTATION_SUPPORT_MD_SENTINEL`, `_GLOSSARY_HEADING` naming convention). NOT a `block_mode_trigger_paths` row (verified L60–110).
   - `tests/unit/marcus/lesson_plan/test_ask_b_trends_consumer_pin_38_2.py` — the declared central pin flip (L89–95) + the `_write_ask_b_run` fixture idiom (L28–56) + the shared `_valid_ask_b_output` fixture import (from `test_research_packet_w1.py` L116) this story's tests reuse.
   - `tests/unit/marcus/lesson_plan/test_trends_w3.py` — `test_trends_inputs_from_run` (L228–232) writes a **generic `04.55`** run and asserts a usable brief through `trends_inputs_from_run` — the SECOND conscious flip (AC 2). All other tests in the module are packet-object-level (`project_trends_from_packet` / `render` paths) and survive unchanged.
   - `tests/unit/marcus/lesson_plan/test_workbook_w4_empty_honesty.py` (L24–36) — empty run dir is empty-honest through BOTH coordinates; survives unchanged (regression-proven, not flipped).
6. `docs/dev-guide/pipeline-manifest-regime.md` + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (L60–110) — `trends_projection.py` is NOT a trigger row; `research_packet.py` IS (L110) with expected touch ZERO; the runner script is NOT a row. If any trigger row is unexpectedly forced, stop and declare per the regime doc before proceeding.

## Acceptance Criteria

1. **The re-point — Door-Ajar reads the Ask-B packet at the exact coordinate via the strict reader**
   - `trends_inputs_from_run` (`trends_projection.py` L305–319) resolves the **Ask-B packet** — `ask_b_hot_topics@07W.4` via `resolve_for_hot_topics(run_dir, require_usable=False)` — instead of the generic `04.55` packet. This routes the read through the strict Ask-B reader branch + duplicate-coordinate collision guard automatically (landed in 38-2; zero reader work here).
   - The sole production consumer (`_act.py` L1217) is re-pointed transitively with ZERO `_act.py` line changes — it already calls `trends_inputs_from_run(run_dir)`.
   - **Digest witness pin (one-witness rule):** a test proves the packet the re-pointed path consumes witnesses the SAME `packet_digest` as a direct `resolve_for_hot_topics` load on the same run, and that digest is distinct from the generic `04.55` digest on the same run (extends the standing three-digest distinctness pin).
   - **Generic `04.55` stays untouched for its OTHER consumers:** `resolve_for_trends_projector` (`research_packet.py` L360–366) stays **byte-untouched** — it survives as the generic-packet reader used by the frozen live-evidence scripts (`run_workbook_w1_live_evidence.py` L125, `run_workbook_w4_live_evidence.py` L170; paid-run economy: frozen evidence scripts are never reopened). `irene_intake` / `spoc_receipt` / `future_collateral` / glossary-legacy reads of `04.55` are proven unchanged by regression. A pinned test proves `resolve_for_trends_projector` STILL resolves `research_wiring@04.55` (the legacy resolver is not silently dragged along by the re-point) — it extends the resolver baseline pin at `test_research_packet_w1.py` L332 (A-5). Disposition of the now-production-orphaned legacy resolver (retire/rename) is explicitly NOT this story's scope — **FILED at green-light (J-3, 2026-07-16)** as `trends-legacy-resolver-retire-or-rename` under `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons (per CLAUDE.md §Deferred inventory rule 3).
   - **Strictness upgrade pinned at AC level (W-1 + M-2 — the story's ONLY new production failure mode, pinned not footnoted):** the re-pointed path inherits the strict Ask-B reader's fail-loud behavior — a forged/malformed Ask-B contribution at `ask_b_hot_topics@07W.4` consumed through `trends_inputs_from_run` raises `ResearchPacketShapeError`, and that exception reaches the production call at `_act.py` L1217 (the old lenient generic read degraded silently). Named matrix row 13 pins it.
   - `research_packet.py` line changes: **ZERO** (trigger row — the resolver exists; §Lockstep).

2. **The conscious flip of the 38-2 boundary pin (declared — the central pin flip of this story)**
   - `test_ask_b_trends_consumer_pin_38_2.py::test_trends_inputs_from_run_is_not_repointed_to_ask_b` (L89–95) currently proves trends is NOT re-pointed (an Ask-B-only run yields an empty brief through `trends_inputs_from_run`). This story **consciously flips it** to its inverse: an Ask-B-only run (no `04.55` contribution) now yields a USABLE brief through `trends_inputs_from_run`, with entries traceable to `ask-b-cite-###` ids. Rationale carried on the flip (one line, in the test): the J-3 grooming note declared this pin "flips consciously at 39-2"; 38-2 AC 8 scoped the old direction as "39.2 owns the re-point." Never silent; the flipped test is renamed to state the new truth (e.g. `test_trends_inputs_from_run_is_repointed_to_ask_b`).
   - **Second conscious flip (enumerated):** `test_trends_w3.py::test_trends_inputs_from_run` (L228–232) writes a generic-`04.55`-only run and asserts a usable brief — post-re-point that run yields an empty-honest brief. Flip it to assert the NEW truth (generic-only run → empty-honest through the re-pointed path — which doubles as an AC 4 empty-class pin), with the same one-line rationale. No other test in `test_trends_w3.py` flips (they are packet-object-level).
   - **Flip inventory is closed:** the traceability table declares BOTH flips (and asserts no third `trends_inputs_from_run`-coordinate pin exists in the tree — `test_workbook_w4_empty_honesty.py` is regression-proven unchanged, not flipped).

3. **`reject_model_prior_topic` proven post-re-point (J-3 obligation 2)**
   - Through the RE-POINTED path (`trends_inputs_from_run(run_dir, injected_topics=(...))` against an Ask-B-only run): an ungrounded/injected topic is marked `unusable`, renders ONLY under `#### Rejected / unusable topics`, contributes zero supporting citations, and never upgrades the brief to usable on its own.
   - A packet-grounded topic (title-matched against Ask-B entry titles) is NOT marked unusable — the grounded/ungrounded discrimination survives the coordinate change (mirror of the 38-2 pins at L59–76 of the pin module, now exercised through the consumer path).
   - `reject_model_prior_topic` itself (`trends_projection.py` L173–212) needs ZERO logic change — this AC is proof-at-the-new-coordinate, not redesign.

4. **Bounded + honest render — existing beats; empty-honesty across the three empty classes**
   - The render is the EXISTING `trends_projection` beats (epics §39.2 AC: "existing `trends_projection` render") — `render_trends_markdown` + the `## Research Trends` composition seam (`workbook_producer.py` L1034–1045) change ZERO lines unless a defect is found (any forced render change is declared in the lockstep table + gets the D3 Blind+Edge bar-module review). Bounded = the existing caps (`max_trends=5`, `max_hot_topics=3`, visible `trends_capped_at_N` loss) — no new knobs.
   - **Empty-honesty is pinned across the three empty classes (each a named test + matrix row):**
     - **(a) Packet absent** — pre-38-2 runs / band-unreached runs: no `ask_b_hot_topics@07W.4` contribution in `run.json` → packet `status="empty"` with `packet_contribution_absent:ask_b_hot_topics@07W.4` (no `run.json` at all → `status="absent"` with `run_json_absent`). Brief is empty-honest (`empty_reason` set; `trends == ()`); render is the explicit-empty branch.
     - **(b) `completed_empty`** — a strict Ask-B contribution with zero rows (honest "we asked, nothing usable came back") → packet `status="empty"` carrying the producer's typed `known_losses` (scope losses lead) + `research_entries_empty`. Brief empty-honest; render explicit-empty. This is the M-5/J-2 designed honest outcome — never treated as a defect anywhere in this story's tests or bar. (Kept as a TIMELESS defense pin per A-2 — the run-B boarding branch of M-5/J-2 is resolved-counterfactual, the empty classes are not.)
     - **(c) All-rows-unusable** — packet present but zero trends-eligible rows survive projection → the L287–296 branch ("research packet present but no trends-eligible rows"), with any unusable/injected topics surfaced under the Rejected block. **Substrate-honest note:** a contract-valid strict Ask-B entry always carries `source_ref`/`citation_id`/provenance, so `_confidence_for_entry` (L116–128) cannot return `unusable` for a live strict mint — this class is exercised at the projection layer (packet-object fixtures / injected topics / bar-side mutated shapes), and the story claims it as a defense-in-depth honesty pin, NOT as a plausible live-mint outcome. Say so in the test docstring.
   - In every empty class: no fabricated topics, no DOIs, no `ask-b-cite-` tokens, no provenance lines in the rendered section; the `empty_reason` line renders verbatim inside `*(...)*`.

5. **NO forecasting-theater (bar-testable phrasing)**
   - Machine-checkable formulation (this is what the tests + AC 6 bar assert — never a vibe): **every rendered trend claim and every usable rendered hot topic must be backed by a packet row** — its rendered `citation_id` ∈ the Ask-B packet's entry `citation_id` set AND its rendered `source_ref` ∈ the packet's entry `source_ref` set; a rendered usable hot topic's `supporting_citation_ids` all resolve into packet entries. Any rendered claim/topic with no backing packet row = fabricated = REJECT.
   - No invented trajectories: the rendered section carries the existing anti-theater sentinel line ("*Bounded callout from wrangled evidence — not trend-forecasting theater.*", L383–385) whenever the non-empty branch renders, and no rendered line claims a forecast (the claim template's "not a forecast" honesty text survives byte-identical — pinned).
   - The `TRENDS_WRITER_REQUIRED_MARKER` stays in the `HotTopicCallout.rationale` FIELD (programmatic signal) and never reaches the rendered MD/DOCX (the `_strip_inline_comments` guarantee, L325–337 — regression-pinned, not new work).

6. **Same-diff runner bar clause + negative pins (D3 plank 5 + M-D3-2b)**
   - Add `_assert_trends_door_ajar_conformant(run_dir, md_paths)` to `scripts/utilities/marcus_spoc_live_test_runner.py`, invoked from `_assert_completed_workbook_deliverable` after the exercise clause (L1937–1939 idiom). Test-harness-side only; production runtime untouched. Mirror the `_assert_glossary_conformant_markdown` structured-artifact-first pattern with this story's substrate-forced difference declared honestly in the clause docstring: **no trends receipt is persisted on the 07W contribution** (`_sidecar_refs` L1577–1598), and the projection is a pure deterministic function of `run.json` — so the structured authority is the deterministic recompute: `resolve_for_hot_topics(run_dir)` → `project_trends_from_packet(packet)` with the `_act.py` production defaults (`max_trends=5`, `max_hot_topics=3`, no injected topics), compared against the rendered section.
   - **Defaults-drift pin (W-2 — named test):** the bar clause's recompute defaults (`max_trends=5`, `max_hot_topics=3`, no injected topics) are asserted EQUAL to the `_act.py` L1217 effective call defaults — if either side drifts, the pin fails, so the bar's recompute authority can never silently diverge from the production call it stands in for.
   - **Residual named honestly in the clause docstring (M-6):** bar-time and render-time share `project_trends_from_packet` — a bug INSIDE that pure function is invisible to the recompute comparison; it is covered by the deterministic unit pins (ACs 3–5), not the bar. The clause docstring says exactly this.
   - **Clause floor (presentation-support sentinel MDs only, mirroring the 39.1 scope; legacy-profile deliverables are out of clause scope):**
     - Exactly ONE `## Research Trends` section per deliverable (counted, not first-match — P9 idiom).
     - Recomputed brief NOT usable ⇒ the section must be the explicit-empty render: carries the recomputed `empty_reason` text, and carries NO `#### Research trends` claim list, NO usable hot-topic lines, NO `ask-b-cite-` tokens, NO `Provenance:` lines, NO DOIs (unusable/Rejected honesty block permitted).
     - Recomputed brief usable ⇒ every rendered trend's `citation_id` + `source_ref` and every usable hot topic's supporting citation ids resolve into the recomputed packet entries (AC 5 formulation); rendered-vs-recomputed claim/topic sets reconcile exactly (missing rendered claim, extra rendered claim, or reordered confidence labels = REJECT); unusable topics appear ONLY under `#### Rejected / unusable topics`.
     - No `run.json` ⇒ a presentation-support MD whose Research Trends section carries any grounded-claim content (claim lines / `ask-b-cite-` tokens / `Provenance:` lines) is REJECTED (P15 mirror: no structured authority may back no claims); an explicit-empty section is tolerated (the R3-style tolerance — the section renders in every profile/run shape, so bare presence is never the refusal trigger, unlike the glossary heading).
   - **Negative-witness pins (mutated frozen shapes fed to the bar; each a named test that must REJECT):**
     1. **Fabricated trend without packet backing** — a conformant deliverable's MD mutated to add a trend claim line (citation id/source_ref not in the packet) → REJECT.
     2. **Unusable row rendered as usable** — an unusable/rejected topic moved out of the Rejected block into the usable `#### Hot topics` list (or its `confidence=unusable` label rewritten) → REJECT.
     3. **Empty packet with non-empty trends render** — run.json carrying an empty-class Ask-B state (any of the three AC 4 classes) while the MD renders a populated claim list → REJECT.
     4. **USABLE row DROPPED from an otherwise-conformant render (M-1 — the silent-loss direction)** — the recompute yields a usable claim/topic but the rendered set is missing it (deliverable otherwise conformant) → REJECT. Matrix row 14.
   - **Conforming-empty POSITIVE pin (M-5/J-2 — KEPT as a timeless defense pin per A-2):** an empty-class run whose MD carries the honest explicit-empty render is ACCEPTED by the bar — pinned as a passing case so the empty-honesty rule can never be "fixed" into a refusal later. (The run-B `completed_empty` boarding branch is resolved-counterfactual; this pin is not.)
   - The bar clause module addition gets Blind+Edge review on change (D3 M-D3-2b standing rule); no existing bar clause (`glossary`, `lo_overlay`, `exercise_composition`, deep-dive) is weakened or reordered.

7. **Verification, run-B boarding, and the FR16/FR9 wave-close assertion (close bar)**
   - **Deterministic:** hermetic tests (dispatch never invoked — consume-only; fixtures via the `_write_ask_b_run` / `_valid_ask_b_output` idiom PLUS the digest-bound extract of the REAL frozen pack `_bmad-output/implementation-artifacts/evidence/ask-b-38-2-live-79f1920e/run/run.json` per M-5), covering: the re-point + digest witness; both conscious flips; post-re-point `reject_model_prior_topic` (grounded + ungrounded); all three empty classes; render honesty (anti-theater phrasing, marker stripping, caps/losses); the W-1/M-2 strictness-upgrade row (13); bar clause positive + all FOUR negative pins (incl. the M-1 dropped-row pin, row 14) + conforming-empty pin (row 12) + the W-2 defaults-drift pin; byte-determinism (M-3, row 15); both-profiles scoping (M-4, row 16); unchanged `04.55`/Ask-A/glossary/exercise/LO-bar regressions; `resolve_for_trends_projector` still-generic pin (extends `test_research_packet_w1.py` L332, A-5). Maintain an AC-to-named-test traceability table declaring the two flips (AC 2) as CONSCIOUS ENUMERATED FLIPS with one-line rationales. Run focused + dependency regressions, strict warnings, Ruff, import-boundary checks, and `python scripts/utilities/check_pipeline_manifest_lockstep.py` (assert exit 0; expected trivially green — zero trigger rows touched). Record the exact pre/post baseline command + per-failure signatures for every inherited failure (count alone insufficient).
   - **No probe:** deterministic-consume ⇒ no probe owed (D3 plank 3; 39-1b precedent). Do NOT author a probe script; do NOT enroll a witness family (the `ask-b-hot-topics-call.v1` family is 38-2's; this story adds no call path).
   - **Run-B boarding:** on suite-green, status flips to exactly `done-awaiting-live-witness  # deterministic+review green; no probe owed (deterministic-consume, D3 plank 3); full-run witness owed by batch run B`. The run-B verdict line for this story keys to the rendered Door-Ajar (§Provenance rider). **A-2 + J-1 + J-2 (green-light):** 38-2's probe returned `PASS_USABLE_MINT` (witness `ask-b-38-2-live-79f1920e`), so the `completed_empty` boarding branch is RESOLVED-COUNTERFACTUAL — no acknowledgment line is owed, the usable-mint half is CLOSED. This story's expected run-B evidence therefore defaults to a **USABLE Door-Ajar render** (bar-conforming); an empty-honest render is acceptable ONLY if the live run legitimately mints empty — recorded honestly in the verdict line, never failed, never retried-to-green.
   - **FR16/FR9 wave-close assertion (J-3 obligation 3 — MUST appear in this story's close record):** at story close (the `done` flip citing the witnessing run id), the closure record asserts: (i) **FR16's Ask-B leg** — the two-asks graph order delivered end-to-end: the Ask-B packet minted at `07W.4` (38-2's half, cross-referenced) AND consumed by its sole consumer (this story's half); (ii) **FR9** — the Door-Ajar renders the Ask-B trends/hot-topics bounded + honest with machine-asserted empty-honesty. 38-2 + 39-2 jointly satisfy both at the 39-wave close bar; neither story's record claims them alone (mirror of the 38-2 AC 9 FR-assertion note, other half).

### Deterministic I/O matrix (pre-dev floor — each row is a named test before implementation completes)

| # | Input condition | Required output |
|---|---|---|
| 1 | Run with a strict usable Ask-B contribution at `ask_b_hot_topics@07W.4` — grounded in the REAL frozen pack `_bmad-output/implementation-artifacts/evidence/ask-b-38-2-live-79f1920e/run/run.json` (digest-bound extract, M-5) | `trends_inputs_from_run` yields a USABLE brief; every trend `citation_id` matches `ask-b-cite-###` and ∈ packet entries; witnessed `packet_digest` == direct `resolve_for_hot_topics` digest (and ≠ generic `04.55` digest on the same run) |
| 2 | Ask-B-only run (no `04.55` contribution) — the FLIPPED 38-2 boundary pin | Usable brief through the re-pointed path (inverse of `test_trends_inputs_from_run_is_not_repointed_to_ask_b`; conscious flip #1, rationale carried) |
| 3 | Generic-`04.55`-only run (no Ask-B contribution) — conscious flip #2 | Empty-honest brief (`empty_reason` set, `trends == ()`); empty class (a): `packet_contribution_absent:ask_b_hot_topics@07W.4` in the packet losses |
| 4 | No `run.json` at all (pre-38-2 / cold dir) | Empty-honest brief; packet `status="absent"` w/ `run_json_absent`; render explicit-empty; regression: `test_workbook_w4_empty_honesty` unchanged |
| 5 | Strict `completed_empty` Ask-B contribution (zero rows, typed losses) | Empty class (b): brief empty-honest; producer scope losses lead the packet losses; render explicit-empty; NEVER treated as defect (M-5/J-2) |
| 6 | Packet present, zero trends-eligible rows at projection (packet-object fixture) | Empty class (c): "packet present but no trends-eligible rows" reason; Rejected block carries any unusable topics; defense-in-depth note in docstring |
| 7 | Ungrounded/injected topic through the RE-POINTED path (`injected_topics=(...)` on an Ask-B run) | Marked `unusable`; renders only under `#### Rejected / unusable topics`; zero supporting citations; grounded topic NOT marked unusable (post-re-point J-3 pin) |
| 8 | `resolve_for_trends_projector` called directly on a two-packet run | STILL resolves `research_wiring@04.55` (legacy resolver untouched; generic leniency + consumers unchanged) |
| 9 | Bar: conformant deliverable MD mutated — fabricated trend line w/o packet backing | `_assert_trends_door_ajar_conformant` REJECTS (`workbook-deliverable-nonconforming-despite-completed`) |
| 10 | Bar: unusable topic re-rendered as usable (moved out of Rejected block / label rewritten) | REJECT |
| 11 | Bar: empty-class packet (any of a/b/c) + populated trends render in the MD | REJECT |
| 12 | Bar: empty-class packet + honest explicit-empty render | **ACCEPT** (conforming-empty positive pin — the M-5/J-2 designed outcome is bar-conforming; KEPT as a timeless defense pin per A-2) |
| 13 | Forged/malformed Ask-B contribution at `ask_b_hot_topics@07W.4` consumed through `trends_inputs_from_run` (W-1 + M-2) | `ResearchPacketShapeError` raised fail-loud, reaching the production call at `_act.py` L1217 — the story's ONLY new production failure mode, pinned not footnoted |
| 14 | Bar: USABLE row DROPPED from an otherwise-conformant render — recompute usable, rendered set missing a claim (M-1, negative pin #4) | REJECT (the silent-loss direction) |
| 15 | Same `run.json` recomputed + rendered twice (M-3 byte-determinism) | Identical brief digest both times AND byte-identical `## Research Trends` section |
| 16 | Legacy-profile deliverable MD on the same run (M-4 both-profiles) | The section RENDERS in the legacy profile (per the unconditional `workbook_producer.py` L1034–1045 seam) AND is proven OUT of bar-clause scope — the presentation-support-sentinel scoping is pinned, not assumed |

**Fixture grounding (M-5):** row 1 / the bar baseline derive from the REAL frozen pack `_bmad-output/implementation-artifacts/evidence/ask-b-38-2-live-79f1920e/run/run.json` (digest-bound extract); the bar-mutation rows (9–14) derive their mutants from it; `_valid_ask_b_output` stays as the hermetic unit-pin fixture (reuse, don't re-derive).

## Scope Fences

- **NO `ask_b_hot_topics.py` or Ask-B wiring changes** — the contract family, `ask_b_research_wiring.py`, `workbook_wiring.py`, journals, and the probe/witness surfaces are 38-2's landed substrate; consume-only.
- **NO `research_packet.py` changes** — trigger row; expected touch **ZERO** (the resolver exists; the strict reader landed in 38-2). Any forced touch is a stop-and-declare, not a dev-authority call.
- **NO `07W` terminal exercise/glossary/deep-dive surfaces** — `_act.py`, `workbook_producer.py` composition, glossary projection, exercise composition, LO overlay, References, Check/Reflection, MD/DOCX renderers: expected touch ZERO (`trends_inputs_from_run` is already the wired seam). Any forced render/producer touch is declared in the lockstep table with rationale.
- **NO manifest / `production_runner.py` / graph / pack / learning-event / gate / HUD changes** — zero nodes, zero edges, zero events; no pack-version bump (v4.2-lineage untouched).
- **NO new LLM calls, NO new provider surface, NO probe, NO witness-family enrollment** — deterministic-consume (D3).
- **NO weakening** of the model-free pins, G2, the M-R3 LO shippability bar, or any existing runner bar clause; the new clause is additive and last in the spine.
- **NO deferred-inventory edits in this diff** — the legacy-resolver follow-on (AC 1) was FILED at green-light (J-3, 2026-07-16) as `trends-legacy-resolver-retire-or-rename` under §Named-But-Not-Filed Follow-Ons; the dev diff touches the inventory ZERO times.

## Lockstep declaration (verified against `pipeline-manifest.yaml::block_mode_trigger_paths` L60–110 in the tree at `19c3e73e`)

| Scoped file | Trigger row? | Expected touch | Note |
|---|---|---|---|
| `app/marcus/lesson_plan/trends_projection.py` | **no** (verified absent from L60–110) | **TOUCHED** | the re-point: `trends_inputs_from_run` resolves via `resolve_for_hot_topics` (L313 swap) |
| `app/marcus/lesson_plan/research_packet.py` | YES (L110) | **UNTOUCHED — ZERO** | resolver landed 38-0; strict reader landed 38-2; any forced touch = stop-and-declare |
| `scripts/utilities/marcus_spoc_live_test_runner.py` | no (verified) | TOUCHED | new `_assert_trends_door_ajar_conformant` clause + spine call (AC 6); test-harness-side only |
| `app/specialists/workbook_producer/_act.py` | no | **UNTOUCHED expected** | already calls `trends_inputs_from_run(run_dir)` (L1217); re-point is transitive |
| `app/marcus/lesson_plan/workbook_producer.py` | no | **UNTOUCHED expected** | `## Research Trends` composition seam (L1034–1045) unchanged; render is the existing beats |
| `state/config/pipeline-manifest.yaml` | YES (itself, L61) | **UNTOUCHED — verified** | zero node/edge/pack/event changes |
| `app/marcus/orchestrator/production_runner.py` / `workbook_wiring.py` | YES (L106/L109) | **UNTOUCHED** | consume-only story; band untouched |
| `tests/unit/marcus/lesson_plan/test_ask_b_trends_consumer_pin_38_2.py` | no | TOUCHED | conscious flip #1 (AC 2) |
| `tests/unit/marcus/lesson_plan/test_trends_w3.py` | no | TOUCHED | conscious flip #2 only (`test_trends_inputs_from_run`, L228); all other tests unchanged |
| new test modules (re-point/digest/empty-class/bar pins) | no | TOUCHED (new) | hermetic; fixture reuse via `_valid_ask_b_output` |

Expected trigger-row touches: **ZERO** — `check_pipeline_manifest_lockstep.py` must exit 0 trivially; Cora's block-mode hook should classify this diff as non-blocking. If any trigger row is forced, the regime doc governs before code proceeds.

## Tasks / Subtasks

- [x] Task 1: The re-point + digest witness (AC 1)
  - [x] Swap the L313 resolver call in `trends_inputs_from_run` to `resolve_for_hot_topics`; update the module/function docstrings to state the Ask-B coordinate truth (W3 header comment included).
  - [x] Digest-witness pin (re-pointed path == `resolve_for_hot_topics` digest; ≠ generic digest); `resolve_for_trends_projector` still-generic pin (extends `test_research_packet_w1.py` L332, A-5); `04.55`-consumer regressions.
  - [x] Strictness-upgrade pin (W-1 + M-2, matrix row 13): forged/malformed Ask-B contribution through `trends_inputs_from_run` raises `ResearchPacketShapeError` reaching the `_act.py` L1217 seam.
- [x] Task 2: Conscious flips + post-re-point pins (AC 2, 3)
  - [x] Flip the 38-2 boundary pin (rename + invert + rationale line); flip `test_trends_w3.py::test_trends_inputs_from_run` (generic-only → empty-honest + rationale line).
  - [x] Post-re-point `reject_model_prior_topic` pins through `trends_inputs_from_run(injected_topics=...)` (ungrounded unusable; grounded not).
- [x] Task 3: Empty-class + render honesty pins (AC 4, 5)
  - [x] Three empty-class tests (matrix rows 3–6) incl. the class-(c) defense-in-depth docstring note; render-honesty pins (anti-theater line, no marker leakage, caps/losses, no fabricated tokens in empty renders); byte-determinism pin (M-3, row 15).
- [x] Task 4: Runner bar clause + negative pins (AC 6)
  - [x] `_assert_trends_door_ajar_conformant` (deterministic-recompute authority + presentation-support MD floor + P15-mirror no-authority rule + the M-6 residual-honesty docstring) wired into `_assert_completed_workbook_deliverable`; W-2 defaults-drift pin (bar recompute defaults == `_act.py` L1217 effective defaults).
  - [x] Negative pins (matrix rows 9–11 + the M-1 dropped-row pin, row 14) + conforming-empty positive pin (row 12) + both-profiles scoping pin (M-4, row 16) — mutants derived from the frozen pack per M-5; Blind+Edge review flagged for the bar module change.
- [ ] Task 5: Verification + close (AC 7)
  - [x] Full matrix, traceability table (flip declarations), baseline comparison, Ruff/import-linter/lockstep (exit 0), strict warnings.
  - [ ] Status → `done-awaiting-live-witness` with the exact D3 vocabulary (ORCHESTRATOR, post-review); run-B verdict-line contract recorded incl. the M-5/J-2 empty-acknowledgment branch.
  - [ ] At the `done` flip (post-run-B): close record asserts FR16's Ask-B leg + FR9 jointly with 38-2 (wave-close bar); strike the J-3 grooming entry in deferred-inventory (bidirectional cross-ref); the legacy-resolver follow-on is ALREADY FILED at green-light (J-3, 2026-07-16) — verify the cross-ref only. (ORCHESTRATOR.)

## Dev Notes

### Code map (anchors verified in the tree at `19c3e73e` — re-verify at T1)

- `app/marcus/lesson_plan/trends_projection.py`
  - L19–22 imports `resolve_for_trends_projector` from `research_packet` — the import swaps to `resolve_for_hot_topics`.
  - L305–319 `trends_inputs_from_run` — THE re-point site (L313). Signature (`max_trends`, `max_hot_topics`, `injected_topics`) unchanged.
  - L215–302 `project_trends_from_packet` — pure over `ResearchPacket`; needs ZERO change (the packet dataclass shape is identical across coordinates — 38-0's whole point). Empty branches L228–237 (`not packet.usable`) and L287–296 (no eligible rows).
  - L173–212 `reject_model_prior_topic` — grounding = case-folded substring against packet-entry titles; ZERO change; proof moves to the new coordinate (AC 3).
  - L340–405 `render_trends_markdown` — ZERO change expected; L343–352 explicit-empty branch; L354/L381 `#### Research trends` / `#### Hot topics`; L383–385 the anti-theater sentinel; L349/L402 `#### Rejected / unusable topics`; L387–399 the usable-topic line format the bar parses (`confidence=`, `Supporting:`, `source_refs:`).
  - L116–128 `_confidence_for_entry` — returns `unusable` only when `source_ref` is blank; strict Ask-B entries always carry `source_ref` (NonBlankLine) ⇒ empty class (c) is projection-layer/mutation-only (AC 4 substrate-honest note).
- `app/marcus/lesson_plan/research_packet.py` (READ-ONLY this story)
  - L32–33 `ASK_B_HOT_TOPICS_SPECIALIST_ID` / `_NODE_ID`; L382–392 `resolve_for_hot_topics`; L360–366 `resolve_for_trends_projector` (stays generic, byte-untouched); L228–244 strict Ask-B branch (`ResearchPacketShapeError` on invalid contract — the re-pointed path now inherits fail-loud on forged Ask-B contributions, a strictness UPGRADE over the old lenient generic read; pinned at AC level per W-1 + M-2, matrix row 13 — the story's only new production failure mode, no longer a footnote); L178–195 duplicate-coordinate guard; L122–147 `_empty_packet` (+ loss strings L175 `run_json_absent`, L205 `packet_contribution_absent:...`, L291/L294 reader losses); L86–89 `ResearchPacket.usable`.
- `app/marcus/lesson_plan/ask_b_hot_topics.py` (READ-ONLY) — L73–80 dispositions; L301–352 `AskBKnowledgeEntryV1` (L335 `ask-b-cite-[0-9]{3,}` namespace the bar/tests key on); L446–543 `AskBContributionOutputV1` (`completed_empty` shape rules L532–538).
- `app/specialists/workbook_producer/_act.py` (READ-ONLY) — L1217 sole production call (defaults: caps 5/3, no injected topics — the bar recompute MUST use the same defaults); L1218–1226 source_ref_manifest joins (Ask-B `source_ref`s now flow into the manifest — regression-check the citation audit stays clean on Ask-B-shaped refs); L1577–1598 `_sidecar_refs` — NO trends receipt persisted (the bar-design forcing fact).
- `app/marcus/lesson_plan/workbook_producer.py` (READ-ONLY) — L1034–1045: trends block after References, BOTH profiles, heading `## Research Trends`; L1036–1044 the producer-side `None`-brief fallback (explicit-empty) — the bar's no-authority tolerance must accept this shape too.
- `scripts/utilities/marcus_spoc_live_test_runner.py`
  - L1239–1244 sentinel/heading constants — add `_TRENDS_HEADING = "## Research Trends"` beside them.
  - L1312–1338 `_assert_glossary_conformant_markdown` — the docstring discipline + P9 counted-singularity + P15 no-authority refusal + `_md_section_body` idioms to mirror.
  - L1600–1618 `_assert_exercise_composition_conformant` — the R3-style tolerance idiom (this clause's no-`run.json` explicit-empty tolerance mirrors it).
  - L1882–1939 `_assert_completed_workbook_deliverable` — append the new clause after the exercise clause (L1937–1939); refusal token is the existing `workbook-deliverable-nonconforming-despite-completed`.
- Fixtures: `tests/unit/marcus/lesson_plan/test_research_packet_w1.py` L116 `_valid_ask_b_output` (the shared strict fixture — reuse, don't re-derive; stays for hermetic unit pins per M-5) + L332 (the resolver baseline pin AC 1 extends, A-5); `test_ask_b_trends_consumer_pin_38_2.py` L28–56 `_write_ask_b_run` (envelope-writing idiom); **the REAL frozen pack `_bmad-output/implementation-artifacts/evidence/ask-b-38-2-live-79f1920e/run/run.json` (M-5)** — grounds matrix row 1 / the bar baseline via a digest-bound extract; the bar-mutation rows (9–14) derive their mutants from it.
- Frozen evidence scripts that reference the OLD coordinate (NOT re-run, NOT touched — paid-run economy): `run_workbook_w1_live_evidence.py` L125/L256, `run_workbook_w3_live_evidence.py` L51/L110 (uses `trends_inputs_from_run` — its frozen evidence predates the re-point; a re-run would now read Ask-B, which is the intended new truth, but frozen packs are never reopened), `run_workbook_w4_live_evidence.py` L133–180/L276.

### Bar-clause design note (the substrate-forced difference from the 39.1 idiom)

The glossary clause reads a persisted structured artifact (the 07W.3 contribution); the exercise clause reads a persisted receipt (`exercise_composition`). Trends persists NOTHING on the contribution — and because this story is deterministic-consume, the projection is a pure function of `run.json`: `resolve_for_hot_topics` → `project_trends_from_packet` with the `_act.py` defaults reproduces the producer's exact brief. The bar therefore recomputes rather than reads a receipt — equally structured-first, and it makes the four negative pins sharp (mutating the MD cannot move the recomputed authority). The recompute MUST use the `_act.py` L1217 effective defaults and PIN that equality (W-2 — the defaults-drift pin), and the clause docstring MUST name the residual honestly (M-6): bar-time and render-time share `project_trends_from_packet`, so bugs inside that pure function are covered by the deterministic unit pins, not the bar. Do NOT add a persisted trends receipt to `_sidecar_refs` to force the receipt idiom — that would touch the producer for the bar's convenience (scope fence; and the recompute is strictly stronger evidence). If review disagrees, that is a party question, not a dev-authority call.

### Velocity tiers

The Epic-38/39-wave story family (38-1, 38-2, 39-1, 39-1b) carries no `r_tier`/`t11_tier` frontmatter (Slab-7c convention not applied to this family); this spec follows the precedent and omits them.

### Size honesty (story author; size DECLARED at green-light per A-4)

- The production diff is deliberately TINY (one resolver-call swap in `trends_projection.py`); the story's real weight is the bar clause + the pin economy (2 conscious flips, 16 matrix rows, 4 negative + 1 positive bar pins + defaults-drift/byte-determinism/both-profiles pins). Overall = **M** (declared, A-4) — consume-side, no journal/replay/parity surface, no probe.

### Guardrails

- Product work only: the Door-Ajar is a SPOC-product deliverable section; never add proofing-run-only behavior (CLAUDE.md design guardrail).
- `lesson_plan` may not import `marcus.orchestrator`; the clause lives in the test-harness runner script, which may import `lesson_plan` (existing idiom).
- Baseline discipline: record the exact pre-story pytest command + per-failure signatures before any code; the two known inherited signatures at `19c3e73e` (see 38-2 Dev Agent Record) compare by node/exception signature, never by count.
- No live spend is owed by this story; run-B boarding follows the D3 STRICT pre-flight rules at the batch boundary (orchestrator's ceremony, not this diff's).

## Green-Light Round Record (2026-07-16)

**Verdict: 4/4 GREEN-WITH-AMENDMENTS** — Winston (Architect), John (PM), Amelia (Dev), Murat (TEA), via two combined seats (Winston+Amelia, John+Murat); orchestrator concurred. Per CLAUDE.md §Push cadence policy "Party consensus = approval": fully-spawned party consensus + orchestrator agreement proceeds without a redundant human Checkpoint-1 hold (operator may override asynchronously). All amendments folded into this spec per the map below; status flipped to `ready-for-dev`.

**Per-id fold map (amendment → where it landed in this spec):**

| Id | Amendment (substance) | Folded at |
|---|---|---|
| W-1 | Strictness upgrade elevated to AC level + named matrix row 13: forged/malformed Ask-B contribution through `trends_inputs_from_run` raises `ResearchPacketShapeError` reaching the production call at `_act.py` L1217 — the story's ONLY new production failure mode, pinned not footnoted | AC 1 (new strictness-upgrade bullet); matrix row 13; Task 1; Dev Notes code map (`research_packet.py` L228–244 note rewritten) |
| W-2 | Named defaults-drift pin: bar recompute defaults (`max_trends=5`, `max_hot_topics=3`, no injected topics) asserted equal to the `_act.py` L1217 effective call defaults | AC 6 (Defaults-drift pin bullet); AC 7 pin inventory; Task 4; Dev Notes bar-clause design note |
| A-1 | Dependency Position rewritten: at HEAD `468de34f` 38-2 is `done-awaiting-live-witness`; probe attempt `79f1920e` PASS_USABLE_MINT (9/9 judge; witness `ask-b-38-2-live-79f1920e` frozen+enrolled, STRICT 27/27) | §Dependency Position (rewritten in full) |
| A-2 + J-1 + J-2 | M-5/J-2 empty-probe run-B branches RESOLVED-COUNTERFACTUAL (no acknowledgment line owed; usable-mint half CLOSED); AC 7 expected run-B evidence defaults to a USABLE Door-Ajar render (empty-honest acceptable only if the live run legitimately mints empty — recorded, never retried); empty classes + matrix row 12 KEPT as timeless defense pins | §Provenance rider (M-5/J-2 bullet rewritten); AC 4 class (b) note; AC 6 conforming-empty pin note; AC 7 run-B boarding; matrix row 12 note |
| A-3 | Frontmatter keeps `baseline_commit: 19c3e73e` + adds anchors re-verified at `468de34f` (artifacts-only diff since baseline) | Frontmatter `anchor_reverification` field |
| A-4 | Size = M (declared) | Dev Notes §Size honesty |
| A-5 | AC 1 cites `test_research_packet_w1.py` L332 as the resolver baseline the still-generic pin extends | AC 1 (still-generic pin bullet); AC 7; Task 1; Dev Notes fixtures |
| M-1 | Negative pin #4: a USABLE row DROPPED from an otherwise-conformant render (recompute usable, rendered set missing a claim) ⇒ REJECT — the silent-loss direction | AC 6 negative-witness pin 4; matrix row 14; Task 4 |
| M-2 | Merged into W-1's row (same substance); both ids cited on the row | AC 1 strictness bullet + matrix row 13 (cited as W-1 + M-2) |
| M-3 | Byte-determinism matrix row: same `run.json` recomputed/rendered twice ⇒ identical brief digest + byte-identical `## Research Trends` section | Matrix row 15; AC 7; Task 3 |
| M-4 | Both-profiles matrix row: legacy-profile MD renders the section AND is proven out of clause scope (presentation-support-sentinel scoping pinned) | Matrix row 16; AC 7; Task 4 |
| M-5 | Fixture family grounds row-1/baseline in the REAL frozen pack `_bmad-output/implementation-artifacts/evidence/ask-b-38-2-live-79f1920e/run/run.json` (digest-bound extract; bar-row mutants — rows 9–14 — derived from it); `_valid_ask_b_output` stays for hermetic unit pins | Matrix row 1 + fixture-grounding note under the matrix; AC 7 deterministic bullet; Dev Notes fixtures. (Numbering note: the party's "rows 9–13" mutant family gains the M-1 row, landed as row 14 to keep row 12/13 ids stable per A-2/W-1.) |
| M-6 | Bar clause docstring names the residual honestly: bar-time and render-time share `project_trends_from_packet`, so bugs inside that pure function are covered by the deterministic unit pins, not the bar | AC 6 (Residual-honesty bullet); Task 4; Dev Notes bar-clause design note |
| J-3 | Legacy-resolver (`resolve_for_trends_projector`) retire/rename follow-on FILED under `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons as `trends-legacy-resolver-retire-or-rename`, sourced to 39-2 | `_bmad-output/planning-artifacts/deferred-inventory.md` (filed 2026-07-16); AC 1, Scope Fences, Task 5 updated to cite the filing |

40-1 rider (mirrored): 40-1 appends `_assert_cover_conformant` after this story's trends clause; "last in the spine" holds only until 40-1 lands.

## Dev Agent Record

### Agent Model Used

claude-fable-5 (Claude Code dev agent, fresh dispatch 2026-07-16; baseline `5e688cca`)

### Implementation Plan

T1 executed in full (all six readings, in order; every line anchor re-verified byte-for-byte in the tree at `5e688cca` — `trends_projection.py` L313/L305–319/L173–212/L215–302/L340–405, `research_packet.py` L228–244/L360–366/L382–392, runner L1239–1244/L1312–1338/L1600–1618/L1882–1939, manifest `block_mode_trigger_paths` L60–110). Order of work: (1) re-point + docstrings; (2) the two conscious flips; (3) shared `tests/helpers/trends_39_2.py` (M-5 digest-bound frozen-pack extract + `swap_trends_section`, mirroring the 39-1 `swap_glossary_section` precedent); (4) runner bar clause + spine wiring + 40-1 tail rider; (5) conforming-render swaps in the three existing bar rigs (37-2b / 39-1 / 39-1b) whose frozen fixture MD carries the pre-39.2 generic-packet trends section; (6) new unit-pin module + new bar-pin module; (7) batteries/ruff/import-linter/lockstep/STRICT-replay.

### AC-to-named-test traceability (matrix rows; flips declared)

| Row | Named test | Module |
|---|---|---|
| 1 | `test_row1_repointed_path_consumes_real_frozen_ask_b_pack` + `test_row1_digest_witness_one_witness_rule` | `tests/unit/marcus/lesson_plan/test_trends_door_ajar_39_2.py` |
| 2 | `test_trends_inputs_from_run_is_repointed_to_ask_b` — **CONSCIOUS FLIP #1** (rename+invert of `…is_not_repointed_to_ask_b`); rationale carried in-test: J-3 grooming note declared the pin "flips consciously at 39-2"; 38-2 AC 8 scoped the old direction as "39.2 owns the re-point" | `test_ask_b_trends_consumer_pin_38_2.py` |
| 3 | `test_trends_inputs_from_run` — **CONSCIOUS FLIP #2** (generic-only run → empty-honest, class (a) loss asserted); same rationale carried in-test | `test_trends_w3.py` |
| 4 | `test_row4_no_run_json_is_empty_honest_absent`; regression: `test_workbook_w4_empty_honesty.py` UNCHANGED (regression-proven, not flipped) | `test_trends_door_ajar_39_2.py` |
| 5 | `test_row5_completed_empty_is_designed_honest_outcome` (scope losses lead; M-5/J-2 timeless defense pin) | `test_trends_door_ajar_39_2.py` |
| 6 | `test_row6_all_rows_unusable_projection_layer_empty` (class-(c) defense-in-depth docstring note included) | `test_trends_door_ajar_39_2.py` |
| 7 | `test_row7_injected_ungrounded_topic_unusable_through_repointed_path` + `test_row7_grounded_topic_not_marked_unusable_through_repointed_path` (J-3 obligation 2) | `test_trends_door_ajar_39_2.py` |
| 8 | `test_row8_resolve_for_trends_projector_still_resolves_generic` (extends the `test_research_packet_w1.py` L332 resolver baseline, A-5) | `test_trends_door_ajar_39_2.py` |
| 9 | `test_row9_fabricated_trend_without_packet_backing_rejects` | `tests/unit/scripts/test_workbook_deliverable_bar_39_2.py` |
| 10 | `test_row10_unusable_topic_rendered_as_usable_rejects` + `test_row10_confidence_label_rewritten_rejects` | `test_workbook_deliverable_bar_39_2.py` |
| 11 | `test_row11_empty_packet_with_populated_render_rejects` + `test_row11_completed_empty_with_populated_render_rejects` | `test_workbook_deliverable_bar_39_2.py` |
| 12 | `test_row12_conforming_empty_class_a_passes` + `test_row12_conforming_empty_class_b_passes` (**ACCEPT** — timeless defense pin per A-2) | `test_workbook_deliverable_bar_39_2.py` |
| 13 | `test_row13_forged_ask_b_contribution_fails_loud_through_consumer` + `test_row13_forged_ask_b_reaches_production_call_at_act_seam` (W-1 + M-2; propagates uncaught through `build_workbook_inputs` to the `_act.py` L1217 seam) | `test_trends_door_ajar_39_2.py` |
| 14 | `test_row14_usable_row_dropped_from_render_rejects` (M-1 silent-loss direction) | `test_workbook_deliverable_bar_39_2.py` |
| 15 | `test_row15_recompute_and_render_are_byte_deterministic` (M-3) | `test_trends_door_ajar_39_2.py` |
| 16 | `test_row16_section_renders_in_both_profiles` + `test_row16_legacy_profile_deliverable_out_of_clause_scope` (M-4) | `test_workbook_deliverable_bar_39_2.py` |
| W-2 | `test_w2_bar_recompute_defaults_equal_act_call_defaults` (signature defaults == bar constants == 5/3/(); AST-pins the sole `_act.py` call site passes no overrides) | `test_workbook_deliverable_bar_39_2.py` |
| P9/P15 | `test_p9_duplicate_trends_section_rejects`; `test_no_run_json_grounded_trends_content_rejects` + `test_no_run_json_explicit_empty_section_tolerated` (incl. the producer None-brief fallback shape) | `test_workbook_deliverable_bar_39_2.py` |
| AC 4/5 | `test_ac4_caps_are_bounded_with_visible_loss`; `test_ac5_anti_theater_line_and_no_forecast_template` (marker stripped from MD, retained in field) | `test_trends_door_ajar_39_2.py` |

**Flip inventory is CLOSED:** exactly the two enumerated flips landed (rows 2 + 3). Grep of the tree confirms no third `trends_inputs_from_run`-coordinate pin exists: remaining callers are `test_workbook_w4_empty_honesty.py` (unchanged, regression-green), the frozen live-evidence scripts (NOT re-run, NOT touched — paid-run economy), and this story's new modules.

### Completion Notes

- **The re-point (AC 1):** one-line resolver swap at `trends_projection.py` L313 (`resolve_for_trends_projector` → `resolve_for_hot_topics`) + import swap + module/function docstring truth updates. `research_packet.py` line changes: **ZERO** (trigger row held). `_act.py` re-pointed transitively with ZERO line changes. The legacy resolver survives byte-untouched for its frozen-evidence consumers (row 8 pin). Note: `_act.py` L23 module-docstring still names `resolve_for_trends_projector` — stale doc nit left in place because `_act.py` is expected-touch-ZERO (fence outranks the nit; flagged for the already-FILED `trends-legacy-resolver-retire-or-rename` follow-on).
- **Flip rationale lines as landed:** (1) `test_trends_inputs_from_run_is_repointed_to_ask_b` — "the J-3 grooming note declared the 38-2 boundary pin 'flips consciously at 39-2'; 38-2 AC 8 scoped the old direction as '39.2 owns the re-point' — the re-point is now LANDED…"; (2) `test_trends_w3.py::test_trends_inputs_from_run` — "the J-3 grooming note declared the trends consumer re-points to Ask-B at 39-2, so a generic-04.55-only run now yields an EMPTY-HONEST brief… the inverse of the pre-re-point assertion." The flipped 38-2 module's header docstring was updated in the same diff to state the new truth (documentation accuracy on the flipped pin, cited to 39-2 AC 2).
- **Bar clause (AC 6):** `_assert_trends_door_ajar_conformant` appended LAST in `_assert_completed_workbook_deliverable` (after the exercise clause) with the 40-1 spine-tail rider comment. Recompute authority = `resolve_for_hot_topics` → `project_trends_from_packet` with the pinned production defaults; parse-based exact reconciliation (claim texts + provenance triples + topic tuples, order-sensitive) + AC 5 packet-membership; M-6 residual named verbatim in the clause docstring; presentation-support-sentinel scoped; P15-mirror no-authority branch with the R3-style explicit-empty tolerance (incl. the `workbook_producer.py` None-brief fallback shape). No existing clause weakened or reordered. **Blind+Edge review of the bar-module change is FLAGGED for the review gate (M-D3-2b standing rule).**
- **Rig adaptations forced by the re-point (test-harness side only, documented):** the frozen `u01@1.rendered-workbook.md` fixture (digest-pinned) carries the PRE-39.2 generic-packet trends section; a new shared helper `tests/helpers/trends_39_2.py` provides `swap_trends_section` (in-memory swap to the recomputed conforming render — exact mirror of the 39-1 `swap_glossary_section` precedent) + the M-5 digest-bound frozen-pack extract (`frozen_ask_b_output`, pinned to output_digest `a10c67b9…`). The three existing bar rigs (37-2b/39-1/39-1b) swap at emit time. Additionally `test_exercise_merge_composition_39_1b.py::test_row_c_prime_replay_full_8b275e5b_run_composition` (local-only replay probe; CI-skipped) now replays off a tmp COPY of the frozen 8b275e5b run with the legacy pre-38-2 Ask-B STUB contribution dropped: under the W-1 strictness upgrade the strict reader fail-louds on the raw stub BY DESIGN, and on a live run the band's reconcile-upgrade replaces the stub before terminal consumption — empty class (a) is the honest replay posture. The frozen run dir is never mutated. This was investigated per binding rule 4 and is a designed-behavior consequence, not a regression.
- **Verification evidence:** baseline (pre-code, at `5e688cca`): focused battery `pytest tests/unit/marcus/lesson_plan/test_trends_w3.py test_ask_b_trends_consumer_pin_38_2.py test_workbook_w4_empty_honesty.py test_research_packet_w1.py tests/unit/scripts/ tests/specialists/workbook_producer/` → **349 passed, 2 skipped**; post-diff full three-tree battery (`tests/unit/marcus/lesson_plan/ tests/unit/scripts/ tests/specialists/workbook_producer/`) → **1643 passed, 6 skipped, 0 failed**. Per-failure signatures: ZERO inherited failures pre AND post; all 6 skips are the known WinError-1314 symlink-privilege environment class (`test_research_packet_w1.py:540`, `test_research_demand_38_3a.py:124/329`, `test_research_demand_38_2_ask_b.py:240`, `test_marcus_spoc_live_test_runner.py:865`) — identical class pre/post. New/flipped modules under `-W error` (strict warnings): 38 passed. `WITNESS_REPLAY_STRICT=1 pytest tests/live_witness_replay -n 0`: **27 passed, 0 skipped** (pre AND post). `check_pipeline_manifest_lockstep.py`: **exit 0** (pre AND post; zero trigger rows touched — trivially green as declared). Ruff on all touched files: clean. import-linter: **18 kept, 0 broken**. No probe authored, no witness family enrolled (deterministic-consume, D3 plank 3).
- **Run-B verdict-line contract (recorded per §Provenance rider):** the run-B evidence pack carries a per-story verdict line for 39-2 keyed to the rendered Door-Ajar — the `## Research Trends` section of the terminal `07W` presentation-support deliverable composed from `ask_b_hot_topics@07W.4`. REACHED+PASS = witness; NOT-REACHED = OPEN (no-evidence — never pass, never fail); "aboard" ≠ tested. Expected evidence defaults to a **USABLE Door-Ajar render** (A-2/J-1/J-2: 38-2 probe PASS_USABLE_MINT; the `completed_empty` boarding branch is resolved-counterfactual, no acknowledgment line owed); an empty-honest render is acceptable ONLY if the live run legitimately mints empty — recorded honestly, never failed, never retried-to-green.
- **FR16/FR9 wave-close assertion:** owed at the `done` flip (post-run-B, ORCHESTRATOR): (i) FR16's Ask-B leg — packet minted at `07W.4` (38-2's half, cross-referenced) AND consumed by its sole consumer (this story's half, landed here); (ii) FR9 — the Door-Ajar renders Ask-B trends/hot-topics bounded + honest with machine-asserted empty-honesty. Neither story's record claims them alone.
- **Scope-fence confirmation by git:** modified files are exactly `trends_projection.py`, `marcus_spoc_live_test_runner.py`, the two flip modules, the three existing bar-rig modules, `test_exercise_merge_composition_39_1b.py` (+ 3 new files). `research_packet.py`, `_act.py`, `workbook_producer.py`, `ask_b_hot_topics.py`, `ask_b_research_wiring.py`, `workbook_wiring.py`, `production_runner.py`, `pipeline-manifest.yaml`, and `deferred-inventory.md` are all UNTOUCHED.

### File List

- `app/marcus/lesson_plan/trends_projection.py` — MODIFIED (the re-point: import + L313 resolver swap + docstrings; zero logic change elsewhere)
- `scripts/utilities/marcus_spoc_live_test_runner.py` — MODIFIED (trends clause constants + `_assert_trends_door_ajar_conformant` + spine call after the exercise clause + 40-1 tail rider comment)
- `tests/helpers/trends_39_2.py` — NEW (M-5 digest-bound frozen-pack extract; `swap_trends_section` / `conforming_trends_body`)
- `tests/unit/marcus/lesson_plan/test_trends_door_ajar_39_2.py` — NEW (matrix rows 1, 4–8, 13, 15 + AC 4/5 render-honesty pins; 13 tests)
- `tests/unit/scripts/test_workbook_deliverable_bar_39_2.py` — NEW (rows 9–12, 14, 16 + W-2 + P9/P15 pins; 15 tests; 39-1b rig)
- `tests/unit/marcus/lesson_plan/test_ask_b_trends_consumer_pin_38_2.py` — MODIFIED (CONSCIOUS FLIP #1 + module-docstring truth)
- `tests/unit/marcus/lesson_plan/test_trends_w3.py` — MODIFIED (CONSCIOUS FLIP #2 only; all other tests unchanged)
- `tests/unit/scripts/test_workbook_deliverable_bar_37_2b.py` — MODIFIED (rig: trends swap at emit)
- `tests/unit/scripts/test_workbook_deliverable_bar_39_1.py` — MODIFIED (rig: trends swap at emit, both rigs)
- `tests/unit/scripts/test_workbook_deliverable_bar_39_1b.py` — MODIFIED (rig: trends swap at emit + pre-receipt-tolerance test)
- `tests/specialists/workbook_producer/test_exercise_merge_composition_39_1b.py` — MODIFIED (8b275e5b replay probe: tmp-copy rig dropping the legacy Ask-B stub; frozen run dir never mutated)

### Change Log

- 2026-07-16 (claude-fable-5): 39-2 implemented at baseline `5e688cca` — Door-Ajar re-pointed to `ask_b_hot_topics@07W.4` via `resolve_for_hot_topics`; two enumerated conscious pin flips landed with rationales; `_assert_trends_door_ajar_conformant` bar clause (recompute authority, M-6 residual named, W-2 defaults pin) appended to the deliverable-bar spine with 4 negative + conforming-empty positive pins; 16-row matrix fully named-test-covered; fixtures grounded on the frozen 79f1920e pack (digest-bound). Batteries: 1643 passed / 6 env-skips; STRICT replay 27/27; lockstep exit 0; ruff + import-linter clean. Status → review.
