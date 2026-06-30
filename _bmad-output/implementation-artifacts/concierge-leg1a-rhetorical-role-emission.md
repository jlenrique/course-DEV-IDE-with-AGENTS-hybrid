# Story concierge-leg1a: REAL Irene rhetorical_role emission (deterministic de-inertion)

Status: done

<!-- Arc: Concierge Production Substrate (branch dev/concierge-production-substrate-2026-06-29, Class S). Leg-1a — deterministic de-inertion keystone. Party GREEN-LIGHT + operator-confirmed 2026-06-29. SSOT: _bmad-output/planning-artifacts/concierge-substrate-party-record-2026-06-29.md. Story key: concierge-leg1a-rhetorical-role-emission. GATES Leg-1b (warm_callback authoring + Vera-R7). Single live ElevenLabs slice (~$0.04); no warm_callback / no LLM authoring here. -->

## Story

As the directed-voice pipeline,
I want **Irene to deterministically EMIT a `rhetorical_role` on each role-derived voice-direction seed** (starting with `contrast_emphasis`), flowing through the already-shipped `voice_direction` contract to Enrique,
so that last arc's v3 ElevenLabs tag channel **stops being inert on real decks** — the `[slow]` tag is actually compiled and sent, driven by Irene's own emission rather than the A/B-probe override.

## Why this story exists (the residual it fixes)

The enhanced-vo arc shipped the entire **consumer** side and party-closed it:
- the model-aware v3 branch in Enrique (`app/specialists/enrique/_act.py:528-554`) reads `rhetorical_role = getattr(direction, "rhetorical_role", None)`, branches on `effective_model == DEFAULT_DIALOGUE_MODEL` (`eleven_v3`), compiles, and sends `channels["provider_text"]`;
- the TAG-ONLY compiler (`app/specialists/_shared/voice_provider_text.py`) with the closed 8-tag allowlist, the `RHETORICAL_ROLE_TAGS` table (`contrast_emphasis → ("[slow]",)`, `warm_callback → ("[warm]",)`), the four sha256 channels, and the captions zero-tag-leak gate.

But the **producer** is missing: the role-derived seed Irene emits (`PEDAGOGICAL_ROLE_TO_VOICE` → `role_to_voice_direction`, `app/marcus/orchestrator/enrichment_consumption.py:85-131`) carries **only** `{emotional_tone, pace, energy}` — it has **never carried `rhetorical_role`**. So on a real run `rhetorical_role` is `None`, the v3 branch is skipped, and the tag channel is inert. The only way a role appeared last arc was an **A/B-probe override** injected into `voice_direction_overrides`. This story makes Irene emit the role for real, on the tonal `contrast_emphasis` role (which authors zero new words → zero source-containment risk → no Vera-R7 dependency, which is why `warm_callback` is deferred to Leg-1b).

## Acceptance Criteria

**AC1 — `rhetorical_role` is EMITTED by Irene's role-derived seed path (REAL, not injected).**
- Add a deterministic `pedagogical_role → rhetorical_role` mapping (mirror the frozen `PEDAGOGICAL_ROLE_TO_VOICE` idiom in `enrichment_consumption.py:85-92`: a module-level closed table, exhaustiveness/fail-safe discipline, shape-pinned by a test, NO `source` key in the seed so override precedence is preserved per `ROLE_DERIVED_SOURCE` note at `:107-114`). This slice maps **at least one** pedagogical_role to `contrast_emphasis`; pedagogical_roles with no rhetorical mapping simply omit the key (no `rhetorical_role` → v2 path, byte-identical — AC6). `warm_callback` is NOT mapped here (structural; Leg-1b).
- The emitted `rhetorical_role` rides the role-derived seed through `_overlay` (`app/specialists/irene/authoring/voice_direction_annotation.py:219-225`, copies arbitrary present keys) into the emitted `VoiceDirection.rhetorical_role` (already declared `RhetoricalRole | None`, `app/specialists/irene/authoring/pass_2_template.py:212-216`) — **additive, zero contract change**.
- **RED-first**: run the Irene emission path on the slice with **no `voice_direction_overrides` and no `voice_direction_defaults` supplying `rhetorical_role`**; assert the emitted segment's `voice_direction.rhetorical_role == "contrast_emphasis"` on the role-mapped slide, sourced from the role-derived seed. (If the role only appears when an override injects it, the inert state is reproduced — the test must fail in that case.)

**AC2 — De-inert end-to-end: the EFFECTIVE model resolves to `eleven_v3` at the read site.**
- The live slice receipt shows `render_mode == "v3_provider_text"` and the **effective** model resolved to `eleven_v3` at the Enrique read site (`_act.py:516,529`) — assert the *effective* model (`_DirectedPlan.effective_model`), not merely the requested flag/config (Winston: a flag set but silently downgraded would pass for the wrong reason).

**AC3 — Provider tags EXACT-match the role→tag table + a fail-loud role is exercised live.**
- For the `contrast_emphasis` segment, the compiled provider tags == `["[slow]"]` (exact equality via `extract_tags`, not "contains"); `strip_tags(provider) == canonical` (the firewall invariant already asserted in `compile_provider_text`).
- Exercise **at least one of the 6 unpopulated `RhetoricalRole` values** through the live/real path and assert it **raises/halts** (`EnriqueActError` tag `elevenlabs.v3.role.unpopulated` at `_act.py:535-541`, or the compiler's `VoiceProviderTextError` same tag) — Murat: a fail-loud path never run is an assumption, not a behavior. (May be a focused offline-real assertion on the shipped compile path; it must actually invoke the guard, not assert on a constant.)

**AC4 — Distinct real request_ids (no mocks, no cached fan-out).**
- The live slice produces **distinct real ElevenLabs `request_id`s** across its segments, proving separate real API calls (per the binding per-component live-test gate; real `ElevenLabsClient`, no mocks).

**AC5 — Captions channel == canonical byte-level, ZERO tag leak (with a leaking-fixture proof).**
- On the `contrast_emphasis` segment, `channels["captions_text"] == canonical` byte-level and contains no allowlisted v3 tag (`assert_no_tag_leak` holds). Include a **deliberately-leaking fixture** (a captions string carrying `[slow]`) and assert the no-leak gate **catches it** (turns red) — Amelia: the highest-value regression guard, proven to have teeth.

**AC6 — Flag-OFF / non-v3 byte-identical (regression firewall).**
- With `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` OFF, or on any non-`eleven_v3` model, deck/narration/provider output is **byte-identical** to today: no `rhetorical_role` is emitted into a path that changes bytes, and the v3 branch is not taken. Pin it.
- **Faithful-record clarification (review remediation):** on a v2 directed run a synthesis segment's receipt `effective_voice_direction` FAITHFULLY RECORDS the authored `rhetorical_role` (`contrast_emphasis`) — this is `plan.direction.model_dump`, NOT v3-gated (`_act.py:838-839`) — while the v3-gated provider block is correctly ABSENT and the audio/sent-text/captions stay canonical (no `[slow]`). Audio/cost/provider-block are unaffected (AC-B12 byte-identity preserved); the role is recorded, not rendered. Pinned by `test_leg1a_v2_directed_synthesis_records_rhetorical_role_but_sends_canonical`.
- All offline gates RED-first (red→green→refactor). `ruff` + `lint-imports` clean on touched files (only the pre-existing C3 `workbook_producer.graph → resume_api` break is permitted — not this work). M3 fence holds: the producer table lives in the orchestrator-side `enrichment_consumption.py` (or the specialist seed path) as DATA; no consumer imports clustering/authoring code.

## Tasks / Subtasks

- [x] **T1 Readiness** (AC: all) — read the SSOT party record + this story. Confirm block-mode NOT triggered: `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` does NOT list `enrichment_consumption.py`, `irene/graph.py`, `voice_direction_annotation.py`, `pass_2_template.py`, `enrique/_act.py`, or `voice_provider_text.py` (a closed-table data add does not trip it — mirror enhanced-vo-1 §8). If you end up editing `pipeline-manifest.yaml` itself, read `docs/dev-guide/pipeline-manifest-regime.md` first.
- [x] **T2 RED emission test** (AC: 1) — assert the role-derived seed emits `rhetorical_role == "contrast_emphasis"` on the role-mapped slide with NO override/default supplying it; assert a pedagogical_role with no rhetorical mapping omits the key (v2-identical). Extend `tests/specialists/irene/test_role_derived_seed_wiring.py` + `tests/marcus/orchestrator/test_enrichment_consumption.py`.
- [x] **T3 Deterministic mapping** (AC: 1) — add the closed `pedagogical_role → rhetorical_role` table (mapping ≥1 role to `contrast_emphasis`; NOT `warm_callback`) with exhaustiveness/fail-safe + shape-pin, NO `source` in the seed; thread the value into the role-derived seed dict so `_overlay` carries it into `VoiceDirection`.
- [x] **T4 RED tag/channel + fail-loud tests** (AC: 3, 5) — provider tags == `["[slow]"]` exact; one unpopulated role raises live/real; captions==canonical + the deliberately-leaking fixture turns the no-leak gate red.
- [x] **T5 Regression** (AC: 6) — flag-OFF / non-v3 byte-identical; full irene/enrique/_shared suites green; `ruff` + `lint-imports` (only pre-existing C3 permitted).
- [x] **T6 LIVE slice** (AC: 2, 3, 4, 5) — DONE 2026-06-30 (orchestrator-run, real ElevenLabs, ~$0.052). 2 v3 `contrast_emphasis` segments through the SHIPPED `build_assembly_bundle` (real `ElevenLabsClient` default), Sarah `EXAVITQu4vr4xnSDxMaL`, flag ON. **ALL PASS**: both receipts `render_mode=="v3_provider_text"` + effective model `eleven_v3` (AC2); `provider_text_tags==["[slow]"]` exact (AC3); distinct real request_ids `YFOlLfEgaezZuZ0uCVbj` / `9erzIMO53zxtlqH9rK8S` (AC4); captions==canonical, no `[slow]` leak (AC5). Evidence: `_bmad-output/implementation-artifacts/evidence/concierge-leg1a-live-gate-20260630T021715Z.json`.

## Dev Notes

### The exact gap (verified file:line, 2026-06-29 as-built)
- **Consumer = DONE (party-closed enhanced-vo-2).** v3 branch `app/specialists/enrique/_act.py:514-573`: `effective_model = resolved.get("model_id") or DEFAULT_TTS_MODEL` (`:516`); `rhetorical_role = getattr(direction, "rhetorical_role", None)` (`:528`); `is_v3 = effective_model == DEFAULT_DIALOGUE_MODEL` (`:529`); unpopulated-role fail-loud `:535-541`; `compile_provider_text` + `build_text_channels` `:546-548`; `render_mode="v3_provider_text"`, `sent_text=channels["provider_text"]` `:553-554`.
- **Compiler = DONE.** `app/specialists/_shared/voice_provider_text.py`: `ELEVEN_V3_TAG_ALLOWLIST` (8 tags, `:52-63`); `RHETORICAL_ROLE_TAGS` (`warm_callback→[warm]`, `contrast_emphasis→[slow]`, `:78-83`) + `POPULATED_RHETORICAL_ROLES` (`:84`); `compile_provider_text` firewall `:159-201`; `build_text_channels` + captions gate `:204-224`; `assert_no_tag_leak` `:142-156`.
- **Producer = THE GAP.** The role-derived seed carries only tone: `PEDAGOGICAL_ROLE_TO_VOICE` rows are `{emotional_tone, pace, energy}` (`app/marcus/orchestrator/enrichment_consumption.py:85-92`); `role_to_voice_direction` returns a copy of that row, NO `rhetorical_role` (`:117-131`); `project_role_derived_voice_by_slide` builds `{slide_ordinal_str: seed}` from those (`:190-259`). The specialist join `_role_derived_seeds_for_deltas(work_deltas, by_slide)` (`app/specialists/irene/graph.py:1121`) maps each delta's `slide_key` to its seed, then `annotate_segments_with_voice_direction(..., role_derived_seeds=...)` (`:1122-1127`) merges via `_overlay`. **Add `rhetorical_role` to the seed here and it flows to `VoiceDirection.rhetorical_role` with no contract change.**
- **Contract already declares the field.** `VoiceDirection.rhetorical_role: RhetoricalRole | None = None` (`app/specialists/irene/authoring/pass_2_template.py:212-216`); the model is `_StrictModel` (`extra="forbid"`), so the field must be declared — it is. `_overlay` copies arbitrary present keys (`voice_direction_annotation.py:219-225`), `model_validate` at `:231`.
- **slide_key join already shipped** (enhanced-vo-1, `d4455e4f`): `_resolve_slide_key_map` + grounding assert + `_stamp_slide_keys` (`graph.py:1086-1120`); Enrique reads deltas from `cache_prefix` (`enrique/_act.py:97-110, 239-261`), NOT `contributions[]`. The seed already lands on the correct final segment by identity.

### Where `rhetorical_role` comes FROM (the deterministic source — implementation decision for dev)
The seed is derived from the enrichment card's per-slide `pedagogical_role` (`project_role_derived_voice_by_slide`, narration component, teachable, exactly-one-eligible → `:233-259`). So the natural deterministic source for `rhetorical_role` is the **same `pedagogical_role`** via a NEW closed map alongside `PEDAGOGICAL_ROLE_TO_VOICE`. Pick at least one pedagogical_role whose delivery is genuinely a tonal "this matters / measured" beat to map → `contrast_emphasis` (the `[slow]` tonal role; candidates by existing tone: the `pace="slower"` rows — `worked_example`/`synthesis`/`assessment`). Keep it conservative and shape-pinned; the exact role(s) chosen is a dev decision to make explicit and test, NOT to leave vague. Do NOT map anything to `warm_callback` (Leg-1b owns structural authoring + Vera-R7).

### Reconciled contradictions (prior-session notes vs as-built — scout-flagged)
1. **No `render_strategy:v3`.** v3 is keyed on `effective_model == eleven_v3` (`_act.py:518-529`). `render_strategy` stays `Literal["tts","dialogue"]`. Do not introduce a `render_strategy:v3`.
2. **Enrique read site is `enrique/_act.py`** (`:97-110, 239-261, 514-573`), NOT `graph.py:993` (Enrique's `graph.py` is ~152 lines; line ~993 is inside *Irene's* graph.py).
3. **Live-key recipe** = `load_dotenv(.env, override=True)` + sentinel-guarded `ELEVENLABS_API_KEY` + the `tests/live/conftest.py` `env_value` skip-guard; NOT a literal `os.environ.pop`.

### Testing standards
- RED-first; NO mocks for live/real assertions (real `ElevenLabsClient`, real ElevenLabs; ~$0.04 slice — Step-4 precedent 2 seg ~$0.038, evidence `_bmad-output/implementation-artifacts/evidence/p5-directed-voice-s4-live-enrique-20260627T230440Z.md`). `.venv/Scripts/python.exe`; `PYTHONIOENCODING=utf-8`. Run live FOREGROUND + hard timeout + flushed. Most-relevant tests to extend: `tests/specialists/irene/test_role_derived_seed_wiring.py`, `tests/marcus/orchestrator/test_enrichment_consumption.py`, `tests/specialists/enrique/test_enrique_v3_provider_text.py`, `tests/specialists/_shared/test_voice_provider_text.py`, `tests/live/test_elevenlabs_smoke.py`. Slice: `course-content/courses/tejal-c1m1-3slide-slice/`.

### Project Structure Notes
- **Single-gate / lite-T11.** Additive closed-table data add on the producer; the consumer is already party-proven. No new node/edge, no schema/contract version bump (the `VoiceDirection` field already exists). M3 fence holds (data only; no consumer imports clustering/authoring). If dev finds the rhetorical map belongs on the specialist side rather than orchestrator-side, keep the M3 fence (replicate, don't cross-import) — but prefer co-locating with `PEDAGOGICAL_ROLE_TO_VOICE` for cohesion.
- Verify via shipped deps, not operator CLIs.

## Out of scope (Leg-1b — concierge-leg1b)
- `warm_callback`, any Pass-2 callback-shaped **authoring** (delegated to a writer; Irene owns intent + anchor reference + handoff validation, not the prose), wiring **Vera-R7** source-containment (`audit_rhetorical_source_containment`, `voice_provider_text.py:267-350`, currently provided-but-unwired) with its negative/teeth case, and the hand-anchored callback slice. The `warm_callback` craft verdict is deferred to Leg-3. Do NOT map `warm_callback` or author callback text here.
- Widening the role→tag table beyond the two roles (named follow-on; trigger = after the two-role path proves end-to-end on a real run). Irene's pedagogy-priority next roles seed post-Leg-3 work: `definitional_anchor` → `clinical-caveat` → `enumeration`.

## References
- [Source: _bmad-output/planning-artifacts/concierge-substrate-party-record-2026-06-29.md] — Round-1 GREEN-LIGHT; Leg-1a/1b split; close bar (Murat 1–5 + Winston effective-model + Amelia leaking-fixture).
- [Source: app/specialists/enrique/_act.py:514-573, :97-110, :239-261] — shipped v3 consumer branch + read site.
- [Source: app/specialists/_shared/voice_provider_text.py:52-224] — shipped compiler, allowlist, role→tag table, channels, no-leak gate.
- [Source: app/marcus/orchestrator/enrichment_consumption.py:85-131, :190-259] — `PEDAGOGICAL_ROLE_TO_VOICE` / `role_to_voice_direction` / `project_role_derived_voice_by_slide` (the producer to extend).
- [Source: app/specialists/irene/graph.py:1086-1128] — slide_key stamp + role-derived seed join + annotate.
- [Source: app/specialists/irene/authoring/pass_2_template.py:212-216] ; [voice_direction_annotation.py:219-231] — VoiceDirection.rhetorical_role + `_overlay` merge.
- [Source: _bmad-output/implementation-artifacts/enhanced-vo-1-role-slide-linkage.md] — the slide_key join this builds on. [enhanced-vo-2-v3-provider-text-compiler.md] — the shipped consumer.

## Dev Agent Record
### Agent Model Used
Amelia (BMAD senior dev agent) — Opus 4.8 (1M context). RED-first offline implementation; T6 live slice deferred to the orchestrator.

### Debug Log References
- RED confirmation (pre-impl): `pytest tests/marcus/orchestrator/test_enrichment_consumption.py -k leg1a tests/specialists/irene/test_role_derived_seed_wiring.py::test_leg1a_real_producer_emits_rhetorical_role_end_to_end` → **6 failed, 1 passed** (the 6 producer-emission tests RED with `AttributeError: ...has no attribute 'rhetorical_role_for_pedagogical_role'` / `KeyError: 'rhetorical_role'`; the 1 pass is the unmapped-role-omits-key test, already byte-identical today). The keystone AC1 end-to-end `test_leg1a_real_producer_emits_rhetorical_role_end_to_end` was RED.
- AC3/AC5 provider tests (pre-impl, against the SHIPPED compiler): `pytest tests/specialists/_shared/test_voice_provider_text.py -k leg1a` → **9 passed** (consumer already shipped + party-closed; these are confirmation/regression pins that the producer's chosen role compiles to exactly `["[slow]"]` and every unpopulated role fails loud).
- Post-impl touched suites: `pytest tests/marcus/orchestrator/test_enrichment_consumption.py tests/specialists/irene/test_role_derived_seed_wiring.py tests/specialists/_shared/test_voice_provider_text.py` → **79 passed**.
- Regression: `pytest tests/specialists/irene tests/specialists/enrique tests/specialists/_shared tests/marcus/orchestrator` → **406 passed**.
- `ruff check` on touched files → **All checks passed!**
- `lint-imports` → **14 kept, 1 broken** — the sole break is the pre-existing/permitted C3 `app.specialists.workbook_producer.graph -> app.gates.resume_api`; Marcus Contract **M3 KEPT** (`app.specialists` ↛ `app.marcus`).

### Completion Notes List
- **The deterministic map (T3).** Added closed `PEDAGOGICAL_ROLE_TO_RHETORICAL` co-located with `PEDAGOGICAL_ROLE_TO_VOICE` in `app/marcus/orchestrator/enrichment_consumption.py`, mirroring its idiom exactly (module-level closed table + import-time `RuntimeError` exhaustiveness guard over `PEDAGOGY_ROLES` + fail-safe `dict.get` accessor `rhetorical_role_for_pedagogical_role`). Map:
  - `synthesis → "contrast_emphasis"`
  - `definition / motivation / worked_example / assessment / practice → None`
- **Role chosen → `contrast_emphasis`: `synthesis`. Rationale (1 sentence):** synthesis is the lesson's "pull it together — here's the key insight" beat, and its existing voice row (`emotional_tone=reflective`, `energy=low`, `pace=slower`) is already the measured/weighty delivery signature that `contrast_emphasis`'s `[slow]` tag reinforces — and it authors zero new words (no source-containment risk → no Vera-R7 dependency, which is why `warm_callback` is left to Leg-1b).
- **Threading.** Threaded the value in `role_to_voice_direction` (the single role→seed transform): the rhetorical key is ADDED to the seed copy ONLY when the role maps to a non-`None` rhetorical role, so an unmapped role's seed is byte-identical to today (AC6). NO `source` key added (override precedence preserved per `ROLE_DERIVED_SOURCE`). The seed flows unchanged through `project_role_derived_voice_by_slide` → `graph._role_derived_seeds_for_deltas` → `annotate_segments_with_voice_direction._overlay` → `VoiceDirection.rhetorical_role` (already declared `RhetoricalRole | None`) — zero contract change.
- **M3 fence held (judgment call).** Kept the rhetorical value as a plain `str` rather than importing `RhetoricalRole` from `app.specialists.irene.authoring.pass_2_template` into the orchestrator, to avoid an `app.marcus → app.specialists` edge; correctness of the value is enforced downstream by the `VoiceDirection` contract (`extra="forbid"` + the `RhetoricalRole` Literal). Mirrors how the consumer leaf `voice_provider_text.py` treats `rhetorical_role` as a plain str.
- **AC1 keystone test is genuinely end-to-end + RED-first.** `test_leg1a_real_producer_emits_rhetorical_role_end_to_end` runs the REAL orchestrator projector (`ec.project_role_derived_voice_by_slide`) on a synthesis card, feeds the result as `by_slide` with NO `voice_direction_overrides`/`voice_direction_defaults`, and asserts the emitted `VoiceDirection.rhetorical_role == "contrast_emphasis"` sourced `role-derived` — so an A/B-probe injection cannot make it pass (it was RED before the producer change).
- **AC3/AC5 note.** The compiler-side AC3 (`extract_tags(provider) == ["[slow]"]` exact; each of the 6 unpopulated `RhetoricalRole` values raises `elevenlabs.v3.role.unpopulated` via the real guard) and AC5 (`captions == canonical` byte-level + a deliberately-leaking `[slow]` captions fixture turns `assert_no_tag_leak` red) tests pass against the already-shipped, party-closed compiler — they are confirmation/regression pins for the producer's chosen `contrast_emphasis → [slow]` path, not new consumer behavior.
- **Collateral test updates.** Two pre-existing exact-equality shape-pins now include the additive `rhetorical_role` for synthesis: `test_a1_role_to_voice_byte_map` and `test_matcher_on_fixture_role_diverse_slice` (the live-enriched fixture's Slide 1 is synthesis). Subscript-based assertions (worked_example etc.) were unaffected.
- **T6 (live ElevenLabs slice) NOT run** — deferred to the orchestrator per the brief. ZERO live/network calls were made in this implementation; all tests are offline/pure.
- **No deviations from spec.** Single judgment call flagged above (plain-str value to hold the M3 fence — the spec explicitly sanctioned "replicate, don't cross-import").

### Review remediation (2026-06-30)
Two characterization/regression PINS added post-review (no production-code change; tests + doc only; zero live calls):
- **Acceptance Auditor NIT-1 — taxonomy self-guard.** `test_leg1a_unpopulated_role_list_is_exactly_taxonomy_minus_populated` (in `tests/specialists/_shared/test_voice_provider_text.py`) pins the hand-written `_UNPOPULATED_RHETORICAL_ROLES` parametrize list against the real `RhetoricalRole` Literal (`pass_2_template`, via `typing.get_args`): asserts `set(_UNPOPULATED_RHETORICAL_ROLES) | set(vpt.POPULATED_RHETORICAL_ROLES) == taxonomy` and the two sets are disjoint. A future taxonomy change (9th role / role promotion) now fails until the unpopulated list is updated in lockstep.
- **Edge Case Hunter Finding #1 — v2 directed run faithfully records `rhetorical_role`, audio unaffected.** `test_leg1a_v2_directed_synthesis_records_rhetorical_role_but_sends_canonical` (in `tests/specialists/enrique/test_enrique_v3_provider_text.py`) pins that a v2-model directed segment carrying `rhetorical_role="contrast_emphasis"` sends CANONICAL (no `[slow]`), has NO provider block on the receipt (AC-B12), BUT `effective_voice_direction["rhetorical_role"] == "contrast_emphasis"` (faithful record), and captions == canonical with no leak.
- Verification: 4 touched/adjacent suites **91 passed**; `ruff check` on both touched test files **All checks passed!**.

### File List
- `app/marcus/orchestrator/enrichment_consumption.py` (modified) — added `PEDAGOGICAL_ROLE_TO_RHETORICAL` closed table + import-time exhaustiveness guard + `rhetorical_role_for_pedagogical_role` accessor; threaded the rhetorical value into `role_to_voice_direction`'s seed copy (additive).
- `tests/marcus/orchestrator/test_enrichment_consumption.py` (modified) — added 6 leg1a producer-emission tests (map shape-pin, exhaustiveness, accessor fail-safe, synthesis seed emits, unmapped omits key, projector end-to-end); updated 2 collateral exact-equality pins for the additive synthesis `rhetorical_role`.
- `tests/specialists/irene/test_role_derived_seed_wiring.py` (modified) — added the AC1 end-to-end real-producer emission test + the AC6 flag-off byte-identity-with-rhetorical-seed firewall; added `enrichment_consumption` import.
- `tests/specialists/_shared/test_voice_provider_text.py` (modified) — added AC3 (`contrast_emphasis → ["[slow]"]` exact; each of 6 unpopulated roles fails loud) + AC5 (`contrast_emphasis` captions byte-level + `[slow]` leak turns red) confirmation pins; **review remediation:** added `test_leg1a_unpopulated_role_list_is_exactly_taxonomy_minus_populated` (taxonomy self-guard, Acceptance Auditor NIT-1).
- `tests/specialists/enrique/test_enrique_v3_provider_text.py` (modified, review remediation) — added `test_leg1a_v2_directed_synthesis_records_rhetorical_role_but_sends_canonical` pinning the v2-directed faithful-record behavior (Edge Case Hunter Finding #1).
- `_bmad-output/implementation-artifacts/evidence/concierge-leg1a-live-gate-20260630T021715Z.json` (new) — T6 live-gate evidence (real ElevenLabs; AC2/AC3/AC4/AC5 PASS; request_ids + provider shas + per-segment receipts).

### Live-gate (T6) — orchestrator-run evidence
- Harness: `scratchpad/leg1a_live_gate.py` (foreground, hard timeout 300s, flushed). Real `ElevenLabsClient` default; `load_dotenv(.env, override=True)` + sentinel-guarded `ELEVENLABS_API_KEY`.
- seg-01: `req=YFOlLfEgaezZuZ0uCVbj` cost $0.0264; seg-02: `req=9erzIMO53zxtlqH9rK8S` cost $0.0252. Both `render=v3_provider_text model=eleven_v3 tags=['[slow]'] captions_clean=True`. Verdict PASS, first-run-stands.
