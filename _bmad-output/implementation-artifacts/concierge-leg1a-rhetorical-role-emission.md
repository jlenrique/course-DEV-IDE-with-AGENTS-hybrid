# Story concierge-leg1a: REAL Irene rhetorical_role emission (deterministic de-inertion)

Status: ready-for-dev

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
- All offline gates RED-first (red→green→refactor). `ruff` + `lint-imports` clean on touched files (only the pre-existing C3 `workbook_producer.graph → resume_api` break is permitted — not this work). M3 fence holds: the producer table lives in the orchestrator-side `enrichment_consumption.py` (or the specialist seed path) as DATA; no consumer imports clustering/authoring code.

## Tasks / Subtasks

- [ ] **T1 Readiness** (AC: all) — read the SSOT party record + this story. Confirm block-mode NOT triggered: `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` does NOT list `enrichment_consumption.py`, `irene/graph.py`, `voice_direction_annotation.py`, `pass_2_template.py`, `enrique/_act.py`, or `voice_provider_text.py` (a closed-table data add does not trip it — mirror enhanced-vo-1 §8). If you end up editing `pipeline-manifest.yaml` itself, read `docs/dev-guide/pipeline-manifest-regime.md` first.
- [ ] **T2 RED emission test** (AC: 1) — assert the role-derived seed emits `rhetorical_role == "contrast_emphasis"` on the role-mapped slide with NO override/default supplying it; assert a pedagogical_role with no rhetorical mapping omits the key (v2-identical). Extend `tests/specialists/irene/test_role_derived_seed_wiring.py` + `tests/marcus/orchestrator/test_enrichment_consumption.py`.
- [ ] **T3 Deterministic mapping** (AC: 1) — add the closed `pedagogical_role → rhetorical_role` table (mapping ≥1 role to `contrast_emphasis`; NOT `warm_callback`) with exhaustiveness/fail-safe + shape-pin, NO `source` in the seed; thread the value into the role-derived seed dict so `_overlay` carries it into `VoiceDirection`.
- [ ] **T4 RED tag/channel + fail-loud tests** (AC: 3, 5) — provider tags == `["[slow]"]` exact; one unpopulated role raises live/real; captions==canonical + the deliberately-leaking fixture turns the no-leak gate red.
- [ ] **T5 Regression** (AC: 6) — flag-OFF / non-v3 byte-identical; full irene/enrique/_shared suites green; `ruff` + `lint-imports` (only pre-existing C3 permitted).
- [ ] **T6 LIVE slice** (AC: 2, 3, 4) — per the binding per-component live-test gate: real `ElevenLabsClient`, the 3-slide slice through the SHIPPED Enrique `build_assembly_bundle`, flag ON + `voice_direction.elevenlabs.model_id=eleven_v3`. Assert receipt `render_mode=="v3_provider_text"`, effective model == `eleven_v3`, provider tags == `["[slow]"]`, distinct real `request_id`s, captions==canonical. Run FOREGROUND + hard timeout + flushed; `load_dotenv(.env, override=True)` + sentinel-guarded `ELEVENLABS_API_KEY`. Capture evidence JSON under `_bmad-output/implementation-artifacts/evidence/`.

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
### Debug Log References
### Completion Notes List
### File List
