# P5 Directed-Voice + S2-Enrichment Arc — Green-Light Strawman

Date: 2026-06-27 · Branch `dev/p5-downstream-consumption-2026-06-26` · HEAD `0cade15`
Authority: operator `/goal` 2026-06-27 + `p5-directed-voice-immediate-roadmap-2026-06-27.md`.
Substrate map: this session's Explore pass (file:line references inline).

This strawman is the SSOT the green-light party reacts to. It proposes (A) the arc sequencing, (B) the Step-1 `voice_direction` contract shape, (C) the dev posture, and (D) the binding constraints carried from prior closes. Party verdict + amendments append to this file (or the party record), not a new doc.

---

## A. Arc sequencing (the 9 steps)

The roadmap's 9 steps split into two interleavable tracks plus a terminal:

- **Track V (directed voice):** Step 1 contract → Step 2 emission → Step 3 Storyboard B → Step 4 Enrique consumption → Step 5 verify (RED + live).
- **Track E (enrichment consumption):** Step 6 (Gary deck + Enrique narration consume `G0EnrichmentResult`).
- **Terminal:** Step 7 Descript demo → Step 8 CF-A true E2E → Step 9 next-planning bridge.

**Proposed order:** V (1→5) FIRST, then E (6), then terminal (7→8), then 9. Rationale: the voice-direction contract (Step 1) is additive/low-regression and unblocks Steps 2–5; enrichment-into-deck (Step 6) is the highest-regression item (proven-live Gary/Enrique producers) and benefits from the directed-voice plumbing already in place. Steps 7–8 publish/prove the combined result. **Open question OQ-A1:** should Step 6 land before Step 5's live proof (so the terminal bundle is enrichment-shaped from first audio), or after (smaller blast radius per story)? Strawman: after — keep Track V independently shippable and regression-isolated.

Each step is its own story under BMAD discipline: own party round where the roadmap/governance calls for it, RED-first tests, `bmad-code-review` before done, live proof for production claims.

---

## B. Step-1 contract: `voice_direction` per segment

### B.1 Shape (proposed `VoiceDirection` Pydantic submodel)

A new optional `voice_direction: VoiceDirection | None = None` field on `SegmentManifestSegment` (`app/specialists/irene/authoring/pass_2_template.py:120-141`). Optional ⇒ old manifests stay valid (backward-compat AC). Proposed `VoiceDirection`:

| Field | Type | Notes |
|---|---|---|
| `render_strategy` | enum `single_voice` \| `dialogue` | default `single_voice`; `dialogue` reserved for Text-to-Dialogue follow-on (carry, not built now) |
| `delivery_intent` | str \| None | free-text director's note ("warm explainer", "urgent call-to-action") |
| `emotional_tone` | enum (closed; e.g. `neutral`/`warm`/`serious`/`energetic`/`reflective`/`urgent`) \| None | closed enum, triple-layer red-reject per pydantic-v2 checklist |
| `pace` | enum `slow`/`measured`/`brisk` \| None | maps to ElevenLabs speed / SSML-ish hints |
| `energy` | enum `low`/`medium`/`high` \| None | |
| `pause_before` | float ≥0 (seconds) \| None | bounded (e.g. ≤5s) |
| `pause_after` | float ≥0 (seconds) \| None | bounded |
| `elevenlabs` | `ElevenLabsSettings \| None` | OPTIONAL explicit override: `voice_id`, `stability`, `similarity_boost`, `style`, `model_id` — mirrors `elevenlabs_client.text_to_speech()` params (`scripts/api_clients/elevenlabs_client.py:101-180`) |
| `dialogue_turns` | `tuple[DialogueTurn, ...] \| None` | OPTIONAL; only meaningful when `render_strategy=dialogue`; each turn = `{speaker, text, voice_id?}`. Modeled now, NOT consumed now (Step 9 follow-on). |

**Mapping seam (the one new deterministic primitive):** a pure `map_voice_direction_to_tts(direction, global_defaults) -> ElevenLabsTTSSettings` function — single source of truth shared by Enrique (Step 4) and Storyboard B display (Step 3), analogous to `figure_tokens.py` as a frozen shared neck. Direction → settings is deterministic; explicit `elevenlabs` overrides win; unset fields fall back to global defaults. **OQ-B1:** do we hard-pin the enum→settings table now (frozen-neck governance) or keep it tunable behind a config yaml? Strawman: config yaml (`app/specialists/enrique/voice_direction_map.yaml`) with a shape-pin test, so CD can tune without a code change but tokenization can't silently drift.

### B.2 Backward-compat / honesty bar

- DONE-1: schema/model accept BOTH a legacy manifest (no `voice_direction`) and a directed manifest (with it). RED-first fixtures for both.
- DONE-2: Honesty bar mirrors workbook (`workbook_enrichment.py:8-12`): a field is "honestly consumed" iff changing it changes the rendered output. For Step 1 the bar is just *accepts + round-trips*; consumption is proven at Steps 3/4.
- Flag: `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` (two-level `*_ACTIVE` + reuse `MARCUS_*_DISPATCH_LIVE` for the live audio leg), default OFF — non-directed runs byte-identical.

### B.3 Carry-through points (from the substrate map)

`narration_join.py:20-62` (propagate field), `storyboard_publisher.py:_write_segment_manifest_for_b()` (display), `enrique/_act.py:334` + `payload_contract.py` (consume; add to `CONSUMED_PAYLOAD_KEYS`), `elevenlabs_client.text_to_speech()` (already parameterized — no change).

---

## C. Dev posture

Per CLAUDE.md + `feedback_bmad_workflows_party_and_dev_agent`: substrate/code changes run through **`bmad-quick-dev` with a fully-spawned party team + a dev agent**, NOT Claude-direct (this is production substrate, not a cleanup arc). Each step: party green-light (where called for) → dev story (RED-first) → `bmad-code-review` → party CLOSE. **OQ-C1:** single-gate vs dual-gate per step? Strawman: single-gate for Steps 1/3 (additive contract + display), dual-gate for Steps 4/6 (proven-live producers, higher regression risk).

---

## D. Binding constraints carried in (non-negotiable)

1. **Narration grounding is NOT weakened (Step 2).** `voice_direction` is *delivery metadata*, never narration text. The figure-citation gate (`pass2-figure-citation-gate`, `_assert_figure_citations_within_perceived`) and G5 Quinn-R stay untouched. Emitting direction must not change which figures/words the script grounds to.
2. **P2 binding conditions ride the CF-A E2E (Step 8).** `p2-condition1-wired-live-run` + `p2-condition3-live-a4`: the live `build_enrichment_result(dispatch_live=True)` in Step 8 MUST show BOTH `resolved` and `failed` in one output AND exercise A4 `ungrounded`, or P2 is retroactively not-closed.
3. **No mocks for production claims.** Live ElevenLabs proof (Step 5) + live Descript publish (Step 7) + live runner E2E (Step 8). Unit/integration use deterministic test doubles ONLY for fast RED-first; final evidence is real (request IDs / receipts / Descript URL).
4. **Regression-safe defaults.** Deck-default byte-identical (Step 6 flag-gated); non-directed audio byte-identical when the flag is OFF (Step 1–4).
5. **Live-key + gpt-5 gotchas.** `os.environ.pop("OPENAI_API_KEY",None); load_dotenv(REPO/.env, override=True)`; gpt-5 rejects `temperature=0` (bind at construction); run live FOREGROUND + hard timeout + flushed.
6. **DRY / existing patterns.** Mirror `workbook_enrichment.py` for Step 6 (read-only projection); reuse `elevenlabs_client` params; one shared direction→settings mapper (frozen neck).

---

## E. Asks of the green-light party

1. **Green-light the arc sequencing** (§A) — V→E→terminal, or reorder (OQ-A1)?
2. **Ratify the `voice_direction` contract shape** (§B) — fields, optionality, the mapping-seam home (OQ-B1).
3. **Confirm dev posture + gate modes** (§C, OQ-C1).
4. **Affirm the binding constraints** (§D) carry verbatim.
5. Surface any blocker that should pause before Step 1 dev opens.

Proposed tailored team: **Winston** (architect — contract/seam/two-walk), **Murat** (test architect — RED-first + live-proof + the P2 binding conditions), **Irene** (narration grounding — voice_direction must not weaken grounding), **Enrique** (TTS consumption realism — settings mapping, receipts), **CD** (script/direction emission — who authors direction and how). Marcus orchestrates.

---

## F. GREEN-LIGHT PARTY VERDICT (2026-06-27) — RATIFIED, NO IMPASSE

**Team:** Winston 🏗️ / Murat 🧪 / Irene ✍️ / Enrique 🎙️ / CD 🎬 (each a real independent subagent). **All five: GREEN-WITH-AMENDMENTS/CONDITIONS. No RED-to-block. No impasse.** Step 1 may open once the amendments below are written into the contract (done in §G).

### F.1 Resolved open questions

- **OQ-A1 (Step 5 live proof before/after Step 6):** **AFTER** — Track V ships and is live-proven before Track E (enrichment-into-deck) opens. Unanimous (Winston, Irene, CD, Murat). Keeps the highest-regression item (proven-live Gary/Enrique producers) regression-isolated.
- **OQ-B1 (mapping-seam home):** **SYNTHESIS that satisfies all five.** The tone/pace/energy→TTS-settings table AND tunable course defaults live in a **config yaml** (`app/specialists/enrique/voice_direction_map.yaml`) — CD tunes without a code change — BUT (a) it is **loaded once at import into a frozen module constant** so `map_voice_direction_to_tts(...)` is a **pure** function over that constant (honors Winston's purity), (b) a **shape-pin test** pins the exact float outputs so the table cannot drift silently (honors Murat/Enrique), and (c) the yaml carries a `map_version` stamp + a "touching this is governance, not refactor" marker (honors Winston's frozen-neck governance). Resolves the Winston-vs-(CD/Murat/Enrique) tension fully.
- **OQ-C1 (gate modes):** Step 1 **single-gate dev** but **contract shape frozen THIS round** + `schema_version` stamp (Winston W-A5); Step 2 gains an **explicit grounding-non-regression gate** (Murat MUR-2 — strawman had none); Step 3 **single-gate + display↔dispatch parity** (Murat MUR-3) + two-walk (Winston W-A4); Steps 4/6 **dual-gate**; live-proof / Descript / CF-A steps **dual-gate**.
- **Step numbering (Murat MUR-0):** the **operator `/goal` 9-step numbering is canonical** (the roadmap-doc table is a support doc with different numbering). Goal-Step-5 = "directed-audio verification (RED tests **+** small live proof)"; **the live directed-audio proof is a non-collapsible sub-gate inside Step 5**, not a separate convenience bundle.

### F.2 Binding conditions carried into the arc (all accepted)

- **MUR-1 (overrides strawman §D-2):** the two BINDING P2 conditions (`p2-condition1-wired-live-run` = one live `build_enrichment_result(dispatch_live=True)` output showing BOTH `resolved` AND `failed`; `p2-condition3-live-a4` = A4 `ungrounded` exercised live) get a **standalone early live discharge, decoupled from CF-A**, runnable in parallel with Step 1 (it gates nothing downstream). CF-A (Step 8) **re-confirms** but is not the sole owner. Evidence must show resolved+failed in ONE output, A4 ungrounded on that output, **real provider request IDs**, committed run artifact.
- **IR-1 (BLOCKING — written into the contract):** `voice_direction` is emitted by a **separate post-freeze annotation pass** that takes the figure-gate-passed narration as **read-only** input; assert `narration_text` + `visual_references` **byte-identical pre/post annotation**. Direction never re-generates the script.
- **IR-2 / IR-5 (grounding firewall, RED-tested):** the figure-citation gate extracts citations from `narration_text` ONLY; a pin test asserts `voice_direction` string fields are **never** passed to `_assert_figure_citations_within_perceived`; an `lo_refs`/`teaches_after` figure absent from the chosen variant must **red-fail** the gate, not relax it (Step 6).
- **MUR-2:** Step 2 carries a grounding-non-regression gate (figure-citation suite + G5 Quinn-R + byte-identical narration text with flag OFF and ON-no-direction).
- **MUR-3 / ENRIQUE-A6:** Step 3 enforces display↔dispatch parity (Storyboard B shows the **resolved** TTS settings the dispatcher will send) + a pre-spend cost preview before any ElevenLabs call.
- **MUR-4 (live "materially different" bar):** control-floor first (same text+direction twice = nondeterminism floor F), then test leg delta > 3×F on a **direction-targeted acoustic scalar** (primary = clip-duration for pace slow-vs-brisk; energy→LUFS/RMS; tone→F0), **distinct real request IDs**, and locked-source non-mutation. Vibes are rejected evidence.
- **MUR-5 / ENRIQUE-A2 (test double + client gap):** a `FakeElevenLabsClient` with the **same signature**, single injected seam, emitting **deterministic settings-sensitive parseable bytes** (pace→duration, energy→amplitude, voice_id→tone) so a dropped `voice_direction` fails RED; captures synthetic request_ids; guarded non-substitutable for live legs. **The real client must surface the `request-id` header (lands in Step 4).**
- **ENRIQUE-A3 (precedence, per-field):** one resolver resolves voice_id AND settings; merge **per field** — explicit `elevenlabs.{field}` > derived-from-direction (yaml) > global default; voice_id = explicit > global `selected_voice_id`. Composes with CD AM-6's four-tier authoring precedence (operator > CD per-segment > role-derived > lesson-global).
- **Winston W-A2/A4/A6:** mapper is a **pure leaf** imported downward by Enrique + Storyboard-B (no `app.specialists`→`app.marcus.orchestrator` edge; name the import-linter contract per the `workbook_enrichment.py:29-35` precedent); Storyboard-B display + directed-audio side-effects fire in **BOTH** runner walks; precedence asserted as a tested invariant.

### F.3 One overruled item (named dissent, folded — not an impasse)

- **CD AM-2 ("cut `dialogue_turns` from v1")** is **overruled** because the operator `/goal` Step 1 explicitly lists "optional dialogue turns." Resolution honoring CD/Irene/Winston: `render_strategy` is an **extensible enum fixed at `single_voice`** for consumption; `dialogue_turns` is **modeled but test-fenced as modeled-not-consumed** (Winston W-A3) AND pre-constrained at modeling time (Irene IR-4: concatenated turn text must be a partition/derivation of the already-gated `narration_text` — no speech channel may bypass the figure gate). CD's rot concern is met by the explicit inert-fence test. **CD dissent recorded; CD remains GREEN overall.**

### F.4 Accepted additive amendment

- **CD AM-1 (emphasis):** add `emphasis: tuple[str, ...] | None` to v1, **grounding-constrained** (Irene-safe): every emphasis token MUST be a substring of `narration_text` (cannot introduce words/figures). Monotone-within-segment is the #1 undirected-TTS tell; small, additive, high payoff.
- **CD AM-4/AM-5 (provenance + approvability):** every segment's direction carries `source: role-derived | cd-authored | operator-override`; Storyboard B (Step 3) renders per segment the marked-up script (emphasis visible), the plain-language `delivery_intent`, the provenance badge, the **resolved** TTS settings, adjacency context, and flags >1-step adjacent dial swings (anti-jitter).

## G. FROZEN STEP-1 CONTRACT (ratified this round — `schema_version: "voice-direction.v1"`)

`SegmentManifestSegment.voice_direction: VoiceDirection | None = None` (optional ⇒ legacy manifests valid). `VoiceDirection` (`_StrictModel`, `extra="forbid"`):

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `Literal["voice-direction.v1"]` | frozen-neck version stamp |
| `render_strategy` | `Literal["single_voice"]` (extensible enum; `dialogue` reserved) | v1 fixed at single_voice |
| `delivery_intent` | `str \| None` (bounded len) | free-text director's note; display/provenance only; never sent to API; never narration |
| `emotional_tone` | closed enum `neutral/warm/serious/energetic/reflective/urgent` `\| None` | maps to coarse stability/style preset (ceiling documented) |
| `pace` | `Literal["slow","measured","brisk"] \| None` | → ElevenLabs `speed` (clean 1:1) |
| `energy` | `Literal["low","medium","high"] \| None` | → `style`↑ + `stability`↓ (coupled, bounded) |
| `emphasis` | `tuple[str, ...] \| None` | each token MUST be a substring of `narration_text` (grounding-constrained) |
| `pause_before` / `pause_after` | `float \| None`, 0 ≤ x ≤ 5 | assembly silence-padding, NOT SSML-in-text |
| `elevenlabs` | `ElevenLabsSettings \| None` | optional explicit override: `voice_id/stability/similarity_boost/style/model_id/speed` (per-field) |
| `dialogue_turns` | `tuple[DialogueTurn, ...] \| None` | MODELED, test-fenced inert v1; `DialogueTurn.text` docstring: when consumed, ⋃ turn texts ⊆ grounded `narration_text` |
| `source` | `Literal["role-derived","cd-authored","operator-override"] \| None` | provenance for Storyboard B + Epic-15 learning |

Flag: `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` (default OFF; flag-OFF ⇒ byte-identical). Mapper: pure `map_voice_direction_to_tts(direction, global_defaults)` over an import-frozen yaml table (`voice_direction_map.yaml`, `map_version` + shape-pin test).

## G-RECONCILED. Marcus control-card override (2026-06-27) — AUTHORITATIVE over §G field specifics

Operator delivered `p5-directed-voice-implementation-control-cards-2026-06-27.md` (Marcus's control cards). It **supersedes §G on field spellings, `render_strategy`, precedence, and adds `delivery_tag`**. The green-light party's SAFETY amendments (IR-1 separate annotation pass, IR-2/IR-5 grounding firewall, MUR-1 P2 decouple, MUR-2/3/4/5 test bars, ENRIQUE-A2 request-id capture, Winston two-walk + pure-leaf mapper) are **PRESERVED and reinforced** by the cards (Card 3 delivery-tag isolation = Enrique firewall; Card 4 RED-first = Murat). No control-card item contradicts a party safety amendment, so this is an operator-authoritative refinement, not a re-litigation. Reconciled frozen contract:

`SegmentManifestSegment.voice_direction: VoiceDirection | None = None` (optional ⇒ legacy valid). `VoiceDirection` (`_StrictModel`):

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `Literal["voice-direction.v1"]` | version stamp (party W-A5) |
| `render_strategy` | `Literal["tts","dialogue"] = "tts"` | **tts** implemented now (default); **dialogue** = schema-tolerated deferred stub, test-fenced inert (W-A3); fail-loud on unsupported values (Card 3) |
| `delivery_intent` | `str \| None` (bounded ≤500) | **free-text** (CD hard ask); display/provenance only; never sent as narration |
| `emotional_tone` | `Literal["neutral","warm","concerned","urgent","reflective","encouraging"] \| None` | control-card enum; → coarse stability/style preset |
| `pace` | `Literal["slower","neutral","faster"] \| None` | → ElevenLabs `speed` |
| `energy` | `Literal["low","medium","high"] \| None` | → `style`↑ + `stability`↓ (coupled, bounded) |
| `delivery_tag` | `str \| None` (e.g. `"[thoughtfully]"`) | **generation-text-only, ISOLATED from the figure-gated displayed narration** (Card 3 + Enrique firewall ENRIQUE-A5); conservative; never pollutes learner-facing script |
| `pause_before_seconds` / `pause_after_seconds` | `float \| None`, 0 ≤ x ≤ 5 | assembly silence-padding, NOT SSML-in-text |
| `elevenlabs` | `ElevenLabsSettings \| None` | per-field override: `voice_id/stability/similarity_boost/style/model_id/speed` |
| `dialogue_turns` | `tuple[DialogueTurn, ...] \| None` | MODELED, test-fenced inert v1; `DialogueTurn.text` docstring = ⋃ turns ⊆ grounded `narration_text` (IR-4) |
| `source` | `Literal["role-derived","cd-authored","operator-override"] \| None` | provenance (party AM-4; additive — Storyboard B badge + Epic-15) |

**5-tier precedence (control card; per-field for settings):** (1) segment `voice_direction.elevenlabs.{field}` → (2) segment `voice_id` → (3) Pass-2 `voice_direction_defaults` → (4) `voice-selection.json` selected default voice → (5) `state/config/style_guide.yaml` defaults. Replaces §G's 3-tier; the mapper implements this.

**Receipt fields (Card 3, refines ENRIQUE-A1):** `segment_id, voice_id, render_strategy, effective_voice_direction, effective_elevenlabs_settings, request_id, narration_file, narration_vtt, narration_duration`.

**DROPPED from §G:** `emphasis` (folded into `delivery_tag`; CD-emphasis "stress specific words" → deferred follow-on `voice-direction-word-emphasis`). **CHANGED:** `render_strategy` single_voice→tts/dialogue; enum spellings; pause field names; precedence 3→5-tier.

**Definition-of-Done alignment (Card §DoD):** the slice ships only when voice_direction is typed/backward-compat (Step 1), CD/Irene emit it (Step 2), Storyboard B exposes it pre-spend (Step 3), Enrique consumes with 5-tier precedence (Step 4), tests cover legacy/override/display/receipt (Steps 1/3/4/5), live proof = **≥3 intentionally-different treatments** (neutral baseline / reflective-or-concerned / warm-or-encouraging) (Step 5), P5-S2 not displaced (Step 6), party signs off, code-review passes. Live-proof team adds **Quinn-R** (learner-facing quality) per Card 4.

## H. Audition rubric + API-sweep advisory (2026-06-27) — Marcus advisory, folded as governing Step-3/5 artifacts

Operator delivered `p5-directed-voice-audition-rubric-2026-06-27.md` (Marcus's palette/rubric addendum). **Advisory, not an override** — active BMAD/party decisions govern; this reduces ambiguity. Its §2 v1 contract **exactly matches §G-RECONCILED** (confirms the contract; no schema change). Folded:

- **Production heartbeat vs API-sweep — the operator's binding distinction:** (i) the **production heartbeat** = per-segment `voice_direction` authored → displayed in Storyboard B → consumed by Enrique → rendered to audio/VTT → recorded with receipts (Steps 1–5); (ii) the **broader ElevenLabs exploration sweep** = exercise every locally-available request parameter at least once (min/mid/max for numerics) OR record why unavailable/account-blocked (rubric §6A). The sweep is a **separate lane**, sequenced AFTER the heartbeat works, and feeds **later BMAD-reviewed schema expansion** — explored fields are NOT forced into the current product contract. v1 schema is a scaffold, not the expressive ceiling.
- **Step-5 governing artifacts:** the live-proof treatments come from the rubric **§4 audition palette** (≥3 distinct, ≥1 non-neutral); each segment scored **Pass/Warn/Fail** on the **§9 rubric** (contract validity / narration integrity / audible differentiation / fit-to-slide-role / captions+timing / receipt quality / maintainability) by the Step-5 party (Quinn-R leads learner-facing quality); the **§10 completion bar** (8 items, incl. item 5 = the API sweep is REQUIRED, item 8 = party explicitly rules production-credible vs narrower palette) is the Step-5 DoD.
- **delivery_tag audition rules (rubric §5):** generation-text-only; never in Storyboard B narration or the figure gate; effects auditioned-not-assumed; if a tag changes spoken/caption text the case FAILS. Initial tags: `[thoughtfully]`/`[warmly]`/`[with concern]`/`[brief pause]`. Whispering is audition-only, not a promised production control.
- **Storyboard B display checklist (rubric §8)** governs Step 3; **5-tier precedence (rubric §7)** matches §G-RECONCILED.
- **New tracked lane:** the **API exploration sweep** (rubric §6A, evidence-record format §6A.Sweep) is added as a sibling of Step 5 — required for close (completion-bar item 5). It is a live-cost leg; run it after the heartbeat is live-proven, capture the §6A evidence record per call, and treat API rejections/account-limits as evidence (not failures). Sweep findings → Step 9 schema-expansion planning, NOT auto-promoted into the contract.

## S. STEP-9 CLOSE — NEXT-INCREMENT PLANNING BRIDGE (2026-06-28) — SIGNED OFF, UNANIMOUS, no impasse

**The P5 directed-voice arc is COMPLETE** (Steps 1–8 + 8.5 UDAC + §10-item-5 ElevenLabs sweep all signed off; the consumption loop is closed + live-proven: enriched corpus → Gary deck + Enrique role-paced narration → published Descript lesson). Step-9 party (Marcus 🧭 SPOC, John 📋 PM, CD 🎬 direction, Murat 🧪 test-architect) decided the next increment. **Unanimous, no impasse.**

**RULING — NEXT INCREMENT = E: "make the directed voice REAL" (harden-first).** All four ranked E #1. Rationale (shared): the arc's headline feature is shipped at the PLUMBING level but is **largely inert on real decks** (EDGE-1 role-seed fail-opens to neutral on clustered/real-Gary decks + gpt-5 locator-suffix variance) and **inaudible even when it fires** (slower=0.94 swamped by a ~0.42s render-nondeterminism floor; no role maps to the only audibly-separating "faster" pole). Adding a NEW expressive surface (A Text-to-Dialogue) on top would stack inert-on-inert and erode every sign-off behind it; proving generality (C) today would just multiply a null result across more decks. Harden before broaden. Client-value-first: a directed voice a learner can't hear is a receipt, not value.

**E scope (ready-for-dev shape, synthesized):**
1. **Content-grounded role→slide linkage** replacing the ordinal-across-two-ordinal-spaces join (the EDGE-1 durable fix `p5-s2-role-seed-robust-source-to-final-slide-linkage`): key on `lo_refs`/`pedagogical_role` matched to slide CONTENT (or thread Pass-1's source→final cluster map), not position — so seeds survive clustered Gary decks + locator-suffix variance instead of fail-opening to neutral. **Murat precondition:** confirm the join is **LLM-free** first; then a deterministic `corpus → expected role-seed` source→final slide-map fixture is an honest RED-first pin (no mock of a real-LLM risk).
2. **Widen the pace dynamic range** (`directed-voice-slower-pace-value-underpowered`): lower `slower→~0.85` AND map ≥1 `pedagogical_role` to the audibly-separating `faster` pole. **CD amendment (binding for audibility):** pace ALONE is below the JND — ship a **coordinated per-role pace+stability(+style) gesture** (lower stability on energized/faster roles, higher on grave/slower roles); stability is the real perceptual lever.
3. **Graduate `seed` into the directed-TTS contract** (folds in sweep candidate D-seed — it is an INGREDIENT of E, not a competing increment): byte-identical determinism (sweep-confirmed live) collapses the ~0.42s render-nondeterminism floor that currently eats the pace tell. Trivially RED-first pinnable (hash-equal at fixed seed / unequal on flip).
**E success bar (live, real-deck, fail-loud):** directed voice **FIRES** (not fail-open-neutral) on ≥1 real clustered Gary deck AND the Step-5 MUR-4 acoustic verifier shows a pace delta **exceeding the now-seed-collapsed floor**, **cross-confirmed on a 2nd real deck**. CD adds the human bar: **ear-proven blind A/B** — if the operator can't blind-call the "slow/grave" vs "energized/fast" read, it is NOT cleared (plumbing-proven ≠ ear-proven).

**Ranked menu + dispositions (consensus):**
- **#1 E** — as above. Reuses already-proven deterministic substrate (MUR-4 judge + fixture join); RED-first essentially pre-written. Highest value-per-effort (recovers stranded value, doesn't break new ground).
- **#2 C — Cross-corpus BETA** — teed up immediately after E; proves the loop GENERALIZES once it carries real value (and becomes the forcing function for whether the audible tell matters across content). Live-integration, not a deterministic unit increment.
- **#3 A — Text-to-Dialogue** — held one slot behind E (ideally after C). **Murat precondition to open safely (binding):** freeze a `dialogue_turns` fixture (fixed input text) and pin ONLY the synthesis+grounding leg deterministically (existing MUR-4 acoustic judge + UDAC grounding firewall — every spoken numeral/token present in the frozen turns); the LLM-authoring leg is verified SEPARATELY and operator-gated, never via a deterministic content-equivalence assertion. Without the input-freeze split it inherits the `teaches_after`/narration-callback deferral problem and STAYS deferred.
- **D split** — `seed` folds into E (above); **`output_format`** = cosmetic-tier, defer; **`apply_text_normalization`** = **grounding-firewall-sensitive** (it MUTATES spoken text — numeral/acronym reads can perturb what the VO is allowed to say vs what's on-slide) → defer-with-flag, requires its OWN grounding-impact review, travels with A's risk class NOT seed's. Do NOT bundle it into E casually.
- **B — Media-placement gate** — biggest new surface of the five (places figures/b-roll/motion into BOTH deck + narration timeline); no spec, no seam, two subsystems. Needs its own PRD/architecture chain + a verification-shape spike (rule-driven map vs LLM/aesthetic judgment?) before it is even a story. **Stay deferred.**

**Governance note (Marcus):** this is a routing recommendation INTO the greenlight gate, not a substitute for it — next session takes E into a `bmad-create-story` chain and lets party-mode ratify scope before dev opens (per sprint-governance §§1–2). Deferred-inventory + next-session-start-here updated per goal Step 9.

## Q. STEP-7 CLOSE (2026-06-28) — SIGNED OFF, no impasse (+ folds in the Step-6 A-live confirmation condition)

**Terminal Descript enriched bundle — DONE + LIVE PUBLISHED.** One honest **enriched** bundle assembled and published live to Descript via the proven path (`import_media + prompt_project_agent/Underlord + publish`): **project** `https://web.descript.com/ec7782de-040f-4451-9d5b-caa54c945409`, **share** `https://share.descript.com/view/7RYEE0ARzuq` — 3 enrichment-shaped Studio slides + role-paced narration clips + the P5-S1 (loop-closed) workbook, stitched to ~35.21s / 3 scenes / synced captions (composition `82402c33-…`, 6/6 uploads HTTP 200). ElevenLabs (Part-A narration) ≈ $0.38.
**Step-6 A-live condition DISCHARGED (folded in):** Part-A aligned-deck run produced the role-derived voice seeds **APPLIED, not EDGE-1 fail-open** (`by_slide={1:slower, 2:neutral, 3:slower}`, `source_slide_ordinals=[1,2,3]`, all `source=role-derived`); role-differentiated ElevenLabs settings **sent live** (synthesis/worked_example `speed=0.94` vs definition `speed=1.00`) with **distinct real request IDs**; the **no-enrichment anti-tautology control collapses to neutral** (proves the differentiation came from enrichment, not a constant). The role→pace projection provably fires end-to-end. Evidence: `evidence/p5-directed-voice-s6-live-narration-aligned-20260628T024652Z.md`.
**Provenance (Desmond condition — named plainly so the evidence is never over-read):** **Reused, prior-run** (operator-sanctioned spend-limiting) = the Studio deck *render + motion assets* (`runs/studio-trial/descript-slides/slide-01..03.png`, from Gamma render `GAyK0cUFhYeRwy2H0fo9W`, drift_rate=0.0) + the P5-S1 workbook artifact. **Freshly produced this run, in-scope** = (a) the enrichment-shaped deck **content** (Step-6 Consumer-B LO-hinted directive), (b) the role-paced ElevenLabs **narration clips** (live, ~$0.38). The DONE bar ("Descript evidence proves enrichment-shaped narration + directed clips") maps to the narration/directed-clip artifacts, **NOT** to deck-render freshness — this run does not prove fresh deck/motion *rendering*. Evidence: `evidence/p5-directed-voice-s7-terminal-descript-20260628T024652Z.md` + bundle `p5-s7-aligned-20260628T024652Z/`.
**Honest caveat (Murat + CD condition — carried in the close, first-run-stands, NOT retried-to-green):** Pace remains the production-credible primary voice-direction dial and the role→pace projection is proven **wired-and-sent live**; however, with the current frozen settings table the per-role **audible** difference is weak (`slower`=0.94 is swamped by a ~0.42s render-nondeterminism floor, and no `pedagogical_role` maps to the only audibly-separating `faster` pole), so today's durable value is the **provable directed-voice plumbing** (provenance + role-differentiated settings, audit-traceable), **not yet a listener-perceptible directed read**. Operator-facing descriptions of this bundle say "role-shaped narration (audible tell currently subtle)", never an unqualified "audibly directed voice." Tracked as follow-on `directed-voice-slower-pace-value-underpowered` (lower slower→0.85, and/or map a role→faster, and/or add a prosody dial) — filed in `deferred-inventory.md`, stays OPEN (do not archive as cosmetic).
**Party CLOSE:** Murat 🧪 **PASS-WITH-CONDITION** (STEP-7 bar met + Step-6 A-live discharged on the non-tautological control + distinct request IDs; underpowered-tell is a value-tuning follow-on, not a blocker; close must state the caveat + keep the follow-on open), CD 🎬 **PASS-WITH-CONDITION** (close on the proven plumbing not a perceptible read; keep the pace-primary ruling, attach the caveat), Desmond 📦 **PASS-WITH-CONDITION** (honest live publish through the proven path; name reused-vs-fresh provenance with source IDs). **Unanimous, no impasse.** All three conditions satisfied above. **§10 item 5 (ElevenLabs API exploration sweep) remains the distinct outstanding lane before broader expressive claims; Step 9 (planning bridge) follows.**

## P. STEP-8 CLOSE (2026-06-28) — SIGNED OFF, no impasse (run before Step 7 — reordered: Step 8 is gpt-5-gated/unblocked while Step 7 is ElevenLabs-cooldown-gated)

**CF-A true E2E through `production_runner` — DONE.** Real START + full CONTINUATION/recover walk to `completed` (trial `8a997d43`, live gpt-5 + live scite): `g0-enrichment.json` **byte-identical** through the walk; two-walk `component_selection` rehydrated NON-default (deck/motion/workbook — the exact thing the standing two-walk gotcha breaks); **voice_direction role-seed re-projected on the CONTINUATION walk** at irene node 08 (`by_slide={1,3,6}`, matching live enrichment); **`run_g0_enrichment → 07W` reached**. Validates the Step-6 A6 claim (seed fires on the continuation walk via the shared `_continue_production_walk` dispatch site) end-to-end on a REAL runner walk.
**BINDING P2 conditions DISCHARGED** (trial `0118a772`, one live `build_enrichment_result`): `resolved` (JAMA) + `failed` (fail-probe) in ONE output (cond1) + A4 `ungrounded` exercised live (cond3), real scite dispatch evidence; corroborated by `394ce491`. **P2 stays CLOSED — the retroactive-un-close trip did NOT fire.**
**Honest scope:** specialist API BODIES (Gamma/Kling/ElevenLabs) were a deterministic recording adapter — the runner WALK CODE ran real on live gpt-5+scite (the metadata path); ElevenLabs audio skipped (cooldown); the API bodies are already live-proven (Steps 4/5/6 + the Step-6 Gamma render). The ungrounded leg + the voice-seed leg are each proven on a real runner run but not the SAME sampling (gpt-5 locator-suffix variance; the runner correctly fail-safes to no mis-seed).
**Party CLOSE:** Murat 🧪 **CLOSE** (P2 discharged; metadata E2E DONE; recording-adapter honest+sufficient; split-sampling acceptable), Winston 🏗️ **CLOSE** (continuation-walk preservation genuine; non-default rehydration the right witness; A6 confirmed E2E; EDGE-1 fail-safe), Texas 🤠 **CLOSE** (P2 resolved/failed/ungrounded real live, no fabrication; P2 follow-ons untouched). **Unanimous, no impasse.** Condition (bookkeeping, done): EDGE-1 `> Narration` locator-variance finding folded into `p5-s2-role-seed-robust-source-to-final-slide-linkage` (gates a single-run all-in-one demo, not this close). Evidence: `evidence/p5-directed-voice-s8-cfa-e2e-20260628T0137Z.md`.

## R. §10 ITEM 5 — ElevenLabs API EXPLORATION SWEEP (2026-06-28) — DONE (distinct lane, NOT the heartbeat)

**The broader API-exploration sweep (audition-rubric §6A), deliberately distinct from the v1 production contract.** Every locally-available ElevenLabs request parameter exercised at least once with a REAL live call, or recorded UNAVAILABLE/REJECTED with the exact API reason. ~39 live calls (~31 billable TTS gens, ~650 chars, negligible cost). Voice `CwhRBWXzGAHq8TQ4Fs17` (Roger, premade) held constant; default model `eleven_multilingual_v2`, alt `eleven_turbo_v2_5` (8 TTS-capable models available).
**ACCEPTED (live, with real request_ids):** `model_id`, `stability`, `similarity_boost`, `style`, `speed`, `use_speaker_boost`, `output_format` (mp3_44100_128 / mp3_44100_64 / pcm_16000), `language_code`, `pronunciation_dictionary_locators` (a real dictionary was already provisioned → true ACCEPTED), `seed`, `previous_text`, `next_text`, `previous_request_ids`, `next_request_ids`, `use_pvc_as_ivc`, `apply_text_normalization` (auto/on/off), `text_to_speech_with_timestamps` (21 char-level timestamps). `list_models`/`list_voices`/`get_voice` OK.
**UNAVAILABLE / REJECTED (exact reasons, first-run-stands):** `get_user` + `/user/subscription` → **401 `missing_permissions` (key lacks `user_read`)** — a key-SCOPE limit, NOT a bad key (the same key drove all 31 TTS gens); so account tier/quota is unconfirmable from this key. `apply_language_text_normalization=True` → **400 `language_text_normalization_not_supported`** unless paired with a supported `language_code` (Japanese `ja` ACCEPTED; English `en` + Chinese `zh` explicitly REJECTED) — it is NOT a plain boolean.
**Honest surprise:** **`seed` is byte-identical-deterministic** on this account (two identical seeded calls → same MD5) — a stronger guarantee than expected.
**Exploration-stage graduation candidates (input to Step 9 — explicitly NOT contract changes yet):** `seed` (reproducibility/regression-pinning of directed audio), `output_format` (delivery-target fit), `apply_text_normalization` (numeral/acronym read fidelity — touches the figure-grounding surface, so any graduation must respect the grounding firewall). Evidence: `evidence/p5-directed-voice-elevenlabs-api-sweep-20260628T030646Z.md` (+ `.calls.json`, `.summary.json`, `elevenlabs-sweep-audio/`); script `scripts/diagnostics/elevenlabs_api_sweep.py`.

## O. STEP-5 CLOSE (2026-06-27) — SIGNED OFF, no impasse

**Built:** directed-audio verification under a **deterministic-judge / first-run-stands** protocol. New pure-leaf `scripts/analysis/directed_voice_acoustics.py`: `analyze_clip` (ffmpeg-decode via bundled `imageio_ffmpeg` → numpy → duration_s/rms/peak) + `materially_different` judge (floor F = same-text+same-direction nondeterminism; PASS iff Δ > k·F, **k=3 fixed before the run**). RED-first: synthetic-WAV analyzer correctness (closed-form ground truth, no API) + a real anti-tautology integration test (dropped direction collapses the delta to RED via the settings-sensitive fake + the REAL `build_assembly_bundle`).
**LIVE proof (MUR-4, first-run-stands, 5 real ElevenLabs clips, ~$0.10, distinct request_ids):** **pace→duration PASS** (F=0.0464s, 3F=0.139s, reflective-vs-urgent Δ=0.186s); **energy→rms FAIL** (Δ=0.0018 < 3F=0.0099) — reported honestly, NOT re-run; diagnosed as a measurement-PROXY limit (stability/style move timbre/prosody, not broadband loudness; settings were SENT per receipts). **MUR-4 overall PASS** (≥1 targeted scalar clears 3×F). Evidence: `evidence/p5-directed-voice-s5-live-acoustic-proof-20260627T231354Z.md` + `…/p5-s5-live-acoustic-20260627T231354Z/` (5 MP3s + receipts + summary). 11 harness/judge tests green; ruff clean; M3 KEPT.
**Party CLOSE (audition-review team):** Murat **CLOSE** (judge deterministic, RED-first real, anti-tautology genuine, ≥1-scalar bar correct, first-run-stands honored), Quinn-R **CLOSE-WITH-AMENDMENTS** (narration integrity PASS; §10-item-8 = production-credible pace-primary, don't narrow), CD **CLOSE-WITH-AMENDMENTS** (full-palette-with-honest-labeling; police the "controls energy" over-promise), Enrique **CLOSE-WITH-AMENDMENTS** (switch energy scalar to LUFS+F0, reuse the 5 clips; MD style 0.30→0.35 fixed to match receipts). **Unanimous, no impasse.**
**§10 item 8 RULING (rubric §12):** production-credible AS-IS; **pace = guaranteed dial, tone/energy = best-effort/aspirational (honestly labeled)**; keep full palette; `urgent` sparing. Follow-on filed: `directed-voice-energy-scalar-and-best-effort-labeling` (LUFS+F0 + Storyboard-B best-effort label). **§10 item 5 (API exploration sweep) still OUTSTANDING** — the distinct §6A lane (task), must close before broader expressive claims.

> **§G-RECONCILED labeling note (Step-5 ruling):** in the v1 contract, `pace` is the GUARANTEED reliably-perceptible directed dial; `emotional_tone` + `energy` are BEST-EFFORT expressive nuance (auditioned, not promised) on the current ElevenLabs model — do not advertise "energy/intensity control" until the LUFS/F0 follow-on confirms a perceptible scalar.

## N. STEP-4 CLOSE (2026-06-27) — SIGNED OFF, no impasse

**Built:** Enrique consumes per-segment `voice_direction` → directed ElevenLabs audio. Real seam = `app/specialists/enrique/_act.py::build_assembly_bundle`. Per-segment TTS settings resolved via the SAME shared `map_voice_direction_to_tts` (single-sourced with Storyboard B parity); **5-tier per-field precedence** (explicit elevenlabs > direction-derived > pass2 defaults > voice-selection.json > style_guide.yaml — tier-4/5 file reads wired); request-id surfaced from the ElevenLabs client (`TtsResult`/`text_to_speech_with_request_id`, legacy `text_to_speech` preserved); per-segment **receipts** (segment_id, resolved voice_id + single-sourced source, effective model_id, effective_elevenlabs_settings, request_id + request_id_present + audio_sha256, char_count, cost_usd, narration_file/vtt/duration). Fail-loud (pre-flight, before any spend) on unsupported render_strategy / malformed direction / corrupt style_guide (tagged recoverable). `delivery_tag` never in the spoken text/VTT (receipt-only); pauses recorded-only (compositor wiring filed). Flag-OFF byte-identical. `FakeElevenLabsClient` = settings-sensitive deterministic bytes (RED-first headline).
**LIVE-EXECUTION (§L):** real ElevenLabs calls (cost-bounded ~$0.04). Canonical bundle (matches shipped/remediated code): `p5-s4-live-enrique-20260627T230440Z` — 2 segments (reflective/slower/low vs urgent/faster/high), distinct REAL request_ids (`VAUuakU9yaMrqmLrcz1a` / `cLIZF5tykK3TkLD3RxOY`), `request_id_present:true`, verified `audio_sha256`, effective `model_id=eleven_multilingual_v2`, distinct settings actually sent (stability 0.75/0.30, speed 0.94/1.10), real ID3 MP3s + VTTs + receipts. (Earlier `…223557Z` bundle SUPERSEDED — predates remediation.)
**Proof:** 188 tests green (RED-first); ruff clean; import-linter M3 KEPT (only pre-existing C3); flag-OFF byte-identical.
**`bmad-code-review`:** 3 layers (Acceptance Auditor = ACCEPT). MUST-FIX (tier-3 string cleaning; effective model_id) + SHOULD-FIX (pre-flight-before-spend; null-request_id audio_sha256 proof; yaml taxonomy; single-source voice-source; KeyError guard; anti-mis-threading test) + S2 resume-reuse implemented + S5 pause→compositor honestly filed — all remediated; live evidence refreshed to shipped code (A1).
**Party CLOSE:** Murat **CLOSE** (money/proof remediation real, RED-first), Winston **CLOSE** (single-source precedence can't drift; M3 taxonomy correct; residual filed), Enrique **CLOSE-WITH-AMENDMENTS** (A1 live-evidence refresh — DONE; A2 residual filed). **Unanimous, no impasse.** Step-4 carries CLOSED with pinning tests (`empty-voice-id-callsite-guard`, `render-strategy-fail-loud`, `storyboardb-display-dispatch-header-tier345`); new follow-ons filed: `directed-voice-enrique-resume-idempotency-double-spend`, `directed-voice-pause-padding-compositor-wiring`.

## M. STEP-3 CLOSE (2026-06-27) — SIGNED OFF, no impasse

**Built:** Storyboard B now displays per-segment `voice_direction` before audio spend. `_write_segment_manifest_for_b` re-attaches `voice_direction` past the frozen join (additive, id-collision-guarded); `generate-storyboard.py` renders a per-segment voice panel (render_strategy, delivery_intent as review-metadata, tone/pace/energy, delivery_tag as a distinct generation-only cue, populated elevenlabs overrides, `source` provenance badge with baseline-vs-deliberate disambiguation), a global-defaults header, and **MUR-3 display↔dispatch parity** (resolved settings via the SAME shared `map_voice_direction_to_tts` Enrique uses — single-sourced, no drift). Missing direction is EXPLICIT; multi-segment slides show one panel per segment (no hidden spend); a malformed direction renders a visible "⚠ INVALID — will fail synthesis" note (degrade-not-crash at the gate); app-unavailable shows an explicit banner.
**LIVE-EXECUTION (§L policy):** real Storyboard B rendered from REAL run `036e7ff8` (6 real Pass-2 segments, flag ON) → real 57,963-byte `index.html` with 6 voice panels + resolved settings (0.75/0.1/0.94) + delivery_tag isolation + a deliberately-invalid seg-05 showing the "INVALID … pause_after_seconds" note. Retroactively live-covers Steps 1–2. Evidence: `_bmad-output/implementation-artifacts/evidence/p5-directed-voice-s3-live-storyboardb-036e7ff8.{md,yaml,html}`.
**Proof:** 18 new tests + 177 broader (1 pre-existing publisher byte-stability failure, unchanged, out of scope); ruff clean; import-linter M3 KEPT (only pre-existing C3). Flag-OFF manifest + storyboard.json byte-identical (no key).
**`bmad-code-review`:** 3 layers (Acceptance Auditor = PASS). HTML escaping CLEAN. MUST-FIX (invalid-direction visible note) + SHOULD-FIX (multi-segment, standalone banner, id-collision guard, 2 fake-green legs, additive storyboard.json) all remediated + re-verified.
**Party CLOSE:** Murat **CLOSE** (gate-safety fix real; fake-green fixes now discriminating), CD **CLOSE** (operator can approve/challenge from this surface alone; Step-2 watch-item closed), Winston **CLOSE** (parity single-sourced; degrade-not-crash; M3 intact). **Unanimous, no impasse.** Follow-ons filed: `directed-voice-storyboardb-display-dispatch-header-tier345` (Step-4 AC), `directed-voice-adjacency-anti-jitter-audition` (Step-5/audition); the `source-baseline-vs-cd-authored` follow-on is CLOSED.

## L. CLOSE-LOOP POLICY — live-execution-as-it-lands (operator-mandated 2026-06-27)

**Binding for EVERY step's close, not just Steps 5/8.** The full review loop per step is:
**dev (RED-first) → independent verify (re-run tests) → LIVE EXECUTION of the component/routine on a representative slice (flip the feature flag ON, run the REAL routine — no mocks — capture evidence) → `bmad-code-review` (3 adversarial layers) → close-party sign-off → commit/push.**

- "Live execution" = the real component runs in a real process on real-shaped data, with the flag ON, producing a real artifact — NOT a fixture-only unit test. Per `feedback_incremental_live_testing_not_deferred` + `feedback_no_mocks_real_live_apis`: the final E2E (Step 8) is a CONFIRMATION, not first live contact.
- For pure-deterministic steps (1–3: contract / emission / Storyboard B), live = run the real annotation + manifest-writer + storyboard generator on a real prior Pass-2 output (real run dir), flag ON, and produce a real `segment-manifest-storyboard-b.yaml` + rendered Storyboard B carrying `voice_direction`. No external API needed, but the routines are exercised for real end-to-end.
- For external-API steps (4 Enrique, 5 proof, 7 Descript, the API sweep): live = a small, cost-bounded REAL call (real ElevenLabs / Descript), capturing request IDs / receipts / URLs.
- **Retroactive coverage:** Steps 1–2 closed on unit tests only; their live-execution leg is satisfied by Step 3's live leg (the real Pass-2 → annotation → Storyboard B chain live-exercises the Step-1 contract + Step-2 emission in one real run). Evidence captured at Step 3 close.

## K. STEP-2 CLOSE (2026-06-27) — SIGNED OFF, no impasse

**Built:** a separate, pure, deterministic **post-freeze annotation pass** (`app/specialists/irene/authoring/voice_direction_annotation.py`) wired into `irene/graph.py` `_act_pass_2` at line 1118 — strictly AFTER the figure-citation gate (1112). Attaches `voice_direction` per segment (precedence: explicit per-segment override > CD defaults > role-derived seed [Step-6 hook, stubbed-not-wired] > conservative built-in neutral/neutral/medium/tts), `source` provenance by value-contribution. Flag-gated (`MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE`, default OFF ⇒ byte-identical). Fail-loud tagged `VoiceDirectionError` (→ recoverable error-pause) on bad value / unknown key / unmatched segment-id / non-dict — UDAC-aligned no-silent posture. **Proof:** 36 new tests + 258 broader green; narration byte-identity proven via a non-tautological live control; ruff clean; import-linter M3 KEPT (only pre-existing C3 broken); pre-existing publisher byte-stability failure unchanged (out of scope, confirmed via stash-baseline).
**`bmad-code-review`:** 3 adversarial layers (Acceptance Auditor = PASS, ship-ready). Grounding firewall CLEAN (both Blind + Edge confirmed). SHOULD-FIX remediated: provenance value-presence; fail-loud-with-context; raise-on-unmatched-key; match-by-segment-id-only; non-dict guard; two-walk investigation (finding 5a — no checkpointer, runner skips re-dispatch on resume → annotation runs once, baked deltas reused, no divergence; flag-flip hazard pinned + filed).
**Party CLOSE:** Winston **CLOSE** (W-A4 two-walk verified accurate vs `production_runner.py:2338`; W-A2/M3 intact; UDAC-forward-compat), Irene **CLOSE** (IR-1/IR-2/MUR-2 hold; grounding byte-identical; firewall intact under fail-loud paths), Murat **CLOSE** (RED-first real; fail-loud genuinely raises; provenance both cases proven; two-walk honestly deferred), CD **CLOSE** (provenance trustworthy; one Step-3/Epic-15 watch-item). **Unanimous, no impasse.** Follow-ons filed to `deferred-inventory.md §P5 directed-voice arc follow-ons`: `directed-voice-flag-capture-once-into-runstate`, `directed-voice-two-walk-integration-pin`, `directed-voice-source-baseline-vs-cd-authored-disambiguation`.

## J. STEP 8.5 — UDAC (Universal Downstream Asset Contract) — operator-mandated 2026-06-27

Operator added a cross-cutting hardening story: enforce **two guarantees universally**, not per-consumer.
- **ACCESS:** a **Run Asset Index / Context Manifest** built at the ratification boundary — `{asset_id, path, digest, revision/run id, authority status}` for source bundle, directive, extracted MD, lesson plan, LOs, `g0-enrichment.json`, `authorized-storyboard.json`, `pass2-envelope.json`, `segment-manifest.yaml`, voice-selection, motion plan. **Threaded through BOTH `production_runner` walks** (start + continuation/recover) — standing two-walk discipline (W-A4). No downstream agent rediscovers paths ad hoc.
- **USE:** anti-tautology tests per major consumer — mutate an enriched LO / source / pedagogy / citation / `voice_direction` sentinel and prove **Gary / Irene / Enrique / workbook / compositor / motion** output changes where expected. Generalizes the proven P5-S1 workbook pattern.
- **DECLARATION:** each specialist declares consumed assets in its input/receipt — `asset_id, path, digest, used | available-only`. Composes with the `emit_spans` pattern + Step-4 receipts.
- **FAIL-LOUD:** past the ratification boundary, a missing/stale ratified asset RAISES (kira `_load_motion_plan` fail-loud precedent); fallback constants = an **explicit legacy-mode marker**, never silent.

**Sequencing:** after Step 8 (CF-A E2E) — which provides the live substrate to enforce against — and before Step 9. **Own green-light party + design strawman** before dev (major architectural addition: both walks + every specialist contract). Reuse content-addressed digest machinery (`compiled_graph_digest.py` v2.0 / content-fingerprint), do NOT reinvent. Existing partial patterns to generalize: g0-enrichment frozen+cached; `workbook_enrichment.py` real consumption tests; the prompt pack naming downstream inputs.
**Forward-compat threading (do NOW so we don't redo work):** Step-4 Enrique receipts and Step-6 enrichment anti-tautology tests are shaped to the UDAC declaration/sentinel format from the start, so UDAC generalizes them rather than re-deriving.

## I. STEP-1 CLOSE (2026-06-27) — SIGNED OFF, no impasse

**Built:** `VoiceDirection`/`ElevenLabsSettings`/`DialogueTurn` models + optional `voice_direction` on `SegmentManifestSegment` (`pass_2_template.py`); pure-leaf 5-tier mapper `map_voice_direction_to_tts` over an import-frozen (`MappingProxyType`) yaml table (`voice_direction_map.py` + `voice_direction_map.yaml`); `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` flag (default OFF); schema regen. RED-first. **Proof:** 68 contract/mapper tests + 285 broader irene/_shared green; ruff clean; import-linter 14 kept / 1 broken (pre-existing C3 baseline only — M3 specialists↛marcus KEPT); no new reds; backward-compat pair proven; grounding firewall behaviorally pinned (voice_direction strings never reach `_assert_figure_citations_within_perceived`).
**`bmad-code-review`:** 3 adversarial layers (Blind Hunter / Edge Case Hunter / Acceptance Auditor = PASS). 1 MUST-FIX (empty-string voice_id `min_length=1`) + cheap SHOULD-FIX hardening (yaml required-key governance error; recursive `MappingProxyType` freeze; dead-code removal; 3 weak-test tightenings; nested extra-key reject; intentional-omission pin; W-A2 contract marker) — all remediated + re-verified.
**Party CLOSE:** Winston **CLOSE** (W-A1..A6 all landed real+tested; W-A4 two-walk correctly deferred to Steps 3/8), Irene **CLOSE** (grounding integrity preserved; IR-2 behavioral pin; IR-4 docstring + filed validator follow-on), Murat **CLOSE** (RED-first genuine; 3 fake-green fixes real; MUR-1/4/5 correctly not-claimed at Step 1). **Unanimous, no impasse.** Follow-ons filed to `deferred-inventory.md §P5 directed-voice arc follow-ons`: `dialogue-turns-grounding-validator-when-consumed`, `directed-voice-step4-empty-voice-id-callsite-guard`, `voice-direction-word-emphasis`, `directed-voice-render-strategy-fail-loud-step4`. Committed at the Step-1 commit.
