# Story enhanced-vo.2: v3 provider-text compiler (TAG-ONLY) + four-channel separation (Slice 1)

Status: done (offline) — AC-B1..B10/B12 party-CLOSED + committed 077d68e2; AC-B11 live A/B done at CLIP level (operator verdict B, SUBTLE — intonation>pace); Descript-final/full-mix cross-confirm OWED (Descript publish failed; follow-on enhanced-vo-descript-final-mix-cross-confirm)

<!-- Epic: enhanced-vo. Depends on enhanced-vo-1 (slide_key identity join) being green — it is (party-CLOSED 2026-06-29, commit d4455e4f). Party GREEN-LIGHT CONSENSUS 2026-06-29 (Dr. Quinn). SSOT: _bmad-output/planning-artifacts/enhanced-vo-party-consensus-2026-06-29.md. -->

## Story

As the directed-voice pipeline on a real clustered Gary deck (where Story A now makes the role FIRE on the right slide),
I want a deterministic **TAG-ONLY** v3 provider-text compiler that turns a per-segment `rhetorical_role` into an ElevenLabs `eleven_v3` provider string, kept rigorously separate from the canonical narration / display / captions channels,
so that an audible rhetorical delivery can be synthesized and **ear-proven on the Descript final** without ever altering the educational wording a learner reads or leaking bracket tags into captions.

## Acceptance Criteria

**AC-B1 — TAG-ONLY pure compiler in `app/specialists/_shared/voice_provider_text.py`.**
- New pure leaf mirroring `voice_direction_map.py` idioms (frozen `MappingProxyType`/`frozenset` constants loaded once at import; `compiler_version` constant; typed `VoiceProviderTextError(tag=...)`; M3 fence — NO `app.marcus` import, `VoiceDirection` only under `TYPE_CHECKING`; default-OFF feature behavior). NO LLM at render — the compiler only ASSEMBLES (tag + canonical), never authors words.
- Core invariant, **ASSERTED, build-breaking**: `strip_tags(provider_text) == canonical_text` BYTE-EXACT for every produced segment.

**AC-B2 — CLOSED enumerated `eleven_v3` tag allowlist (PRE-CONDITION — SATISFIED).**
- Frozen allowlist = the 8 live-exercised v3 tags: `[slow] [sighs] [whispers] [urgent] [warm] [curious] [serious] [excited]` (source: `evidence/elevenlabs-v3-rhetorical-audition-20260629/manifest.json`). `strip_tags` derives ONLY from this same constant.
- An unrecognized bracket token in compiler output → **fail loud** (`VoiceProviderTextError`), never silently stripped or passed through. (Pre-condition met: vocabulary is enumerable; no HAND-BACK on this axis.)

**AC-B3 — Four sha256'd text channels.** Each segment carries four DISTINCT channels, each with a `*_sha256`:
- `canonical_text` = the figure-gated narration (today's `plan.text`) — the truth artifact Irene/Vera/Quinn-R treat as real.
- `provider_text` = compiler output (canonical + allowlisted tags) — sent to TTS.
- `display_text` = what Storyboard B shows (provider, expandable) — see AC-B9.
- `captions_text` = canonical (never provider) — see AC-B5.
Carried on the receipt + (where needed) the manifest; populated only on directed+enriched v3 runs.

**AC-B4 — Model-aware v3 branch + additive `rhetorical_role`.**
- Additive optional `rhetorical_role` field on `VoiceDirection` (`pass_2_template.py:183-211`, `_StrictModel`/extra=forbid → MUST be declared); closed enum (the role taxonomy; this slice ships `warm_callback` + `contrast_emphasis`, model carries the rest as accepted-but-deferred). Additive, NOT a contract version bump.
- The v3 rendering branch routes Enrique's directed synthesis through the compiler when the **effective model is `eleven_v3`**. DESIGN NOTE for dev/Winston: the consensus shorthand "render_strategy:v3" must be reconciled — `render_strategy` is currently `Literal["tts","dialogue"]` (synthesis MODE), while v2/v3 is the MODEL. Prefer branching on `effective_model == eleven_v3` (keep `render_strategy="tts"`), OR widen render_strategy only if Winston rules it cleaner. The v2 numeric mapper (`voice_direction_map.py`) stays FROZEN; the v3 branch is a sibling.

**AC-B5 — Captions zero-tag-leak HARD gate + cross-channel tag-bleed MUTATION test.**
- `_write_vtt` (`_act.py:336-343`, called directed at `:710`) MUST receive `canonical_text`, never `provider_text`. HARD assertion: no allowlisted/bracket token ever appears in any caption channel.
- **MUTATION test (HAND-BACK if absent):** plant a tag in the captions channel → the zero-leak gate MUST turn red. Tag-strip survivorship is the load-bearing invariant; it must be mutation-proven, not merely asserted.

**AC-B6 — skip-if-exists re-keyed on provider sha.**
- `_reusable_receipt` (`_act.py:508-527`) reuse key extends from `(effective_elevenlabs_settings, voice_id)` to ALSO compare `provider_text_sha256` (and `canonical_text_sha256`). A provider-text change MUST force re-synthesis (no stale-audio reuse). The new sha fields are written into the receipt (AC-B7) AND compared here.

**AC-B7 — Enrique sends provider_text via the PROVEN call; receipts extended.**
- At the directed call site (`_act.py:686-697`), when the v3 branch is active, send `provider_text` (not canonical) to `scripts/api_clients/elevenlabs_client.py::text_to_speech_with_request_id` with `model_id=eleven_v3` + `seed` (test-hygiene, AC-B10) — **REUSE this proven call; do NOT reinvent the ElevenLabs request.** v2/non-v3 path unchanged (sends canonical).
- Receipt (`_act.py:732-753`) gains: `canonical_text_sha256`, `provider_text_sha256`, `provider_text`, `provider_text_strategy` (the rhetorical_role), `provider_text_tags` (list), `provider_text_compiler_version`, `render_mode` (`v2_settings` | `v3_provider_text`), `effective_model` (already present as `model_id`).

**AC-B8 — Fidelity firewall (tag-only) + Vera R7 authoring-gate.**
- The compiler is TAG-ONLY → `strip_tags(provider)==canonical` IS the firewall (the compiler can introduce NO spoken token absent from canonical). For STRUCTURAL roles (warm_callback), the rhetorical WORDING is authored UPSTREAM by Irene as canonical narration; the compiler only adds `[warm]`.
- **Vera R7:** any Irene-authored rhetorical wording that realizes a role (e.g. the callback sentence) must pass a SOURCE-CONTAINMENT check vs the ORIGINAL source narration — numerals/units/clinical-terms/negations/comparators introduced by it are ZERO-tolerance traceable to source (a purely connective callback with no new semantic token is clean). This keeps the figure-grounding bar attached to where generative authorship actually happens (Irene), not the compiler.

**AC-B9 — Storyboard B shows literal provider bytes BEFORE any live spend.**
- Operator-facing review (`generate-storyboard.py` ~`:2466` narration `<pre>` / the voice-direction panel `:537-660`) shows: canonical narration, the literal `provider_text` (tags inline, per slide), the rhetorical_role, model, voice, AND the captions channel proving zero tag-leak — side by side, fed from manifest-B. The operator must SEE exactly what goes to ElevenLabs (and that captions stay canonical) before any cent is spent.

**AC-B10 — Roles + voice + seed (this slice).**
- Two roles: `warm_callback` (STRUCTURAL — Irene authors the callback as canonical, compiler adds `[warm]`; its A/B is a rhetoric-vs-tag decomposition) + `contrast_emphasis` (TONAL — the tag does the work on identical words; the clean tag-channel probe). `curious_pivot` etc. deferred (model accepts, compiler unpopulated).
- One voice: **Sarah** (`EXAVITQu4vr4xnSDxMaL`). `seed` graduated into the directed v3 call (test-hygiene) so the blind A/B differs by direction, not render noise.

**AC-B11 — Live leg + pre-registered success bar (operator-judged).**
- Produce TWO Descript-final arms on a real clustered Gary deck with IDENTICAL canonical words: **A = strip_tags (no tag)**, **B = compiler `[tag]`** — via real `eleven_v3` synthesis (`build_descript_narrated_lesson.py` per arm; NEW two-arm audio driver, reuse the per-arm producer). Live **transcript no-tag-leak proxy**: the synthesized audio for a tagged segment must not speak the literal tag token (deterministic leakage check, valid — unlike rms).
- **SUCCESS BAR (pre-registered, BOTH outcomes valued):** blind A/B on the DESCRIPT FINAL video, on the tonal-role (`contrast_emphasis`) slide, identical words both arms; **OPERATOR judge; first-run-stands; 2nd-deck cross-confirm.** "Indistinguishable" = the tag is plumbing-only = a FUNDABLE FINDING (redirect to rhetoric+voice), NOT a failure. **NO numeric expressiveness metric** (rebuilds the energy→rms honest-fail). Only the offline deterministic gates + the live transcript no-leak proxy can FAIL the story; the perceptual A/B is a finding, not a gate. This step is OPERATOR-GATED by design (the operator's ear is the judge).

**AC-B12 — v2 / non-v3 / flag-OFF byte-identical.**
- With directed voice OFF, or effective model ≠ eleven_v3, output is byte-identical (no provider_text, no compiler call, captions=canonical as today). The compiler + channels are additive.

## Tasks / Subtasks (RED-first; live LAST + CI-deselected)
- [x] T1 Readiness — block-mode NOT triggered (substrate map §10). render_strategy-v3-vs-effective_model reconciled: branch on `effective_model == "eleven_v3"`, keep `render_strategy="tts"` (model is a different axis from synthesis mode; v2 mapper stays frozen).
- [x] T2 RED→GREEN: compiler unit tests — `strip_tags(provider)==canonical` byte-exact per role; tag placement; allowlist frozen; unpopulated-role fail-loud. (M1 corrective: allowlist-aware strip/leak gates + bracketed-canonical round-trip + canonical-already-tagged precondition.)
- [x] T3 RED→GREEN: four-channel separation + captions zero-tag-leak HARD + cross-channel tag-bleed MUTATION (AC-B5).
- [x] T4 RED→GREEN: skip-if-exists invalidation on provider sha (AC-B6) + S3 render-mode reuse guard.
- [x] T5 GREEN: built `app/specialists/_shared/voice_provider_text.py` (compiler + frozen allowlist) + `rhetorical_role` field + model-aware branch (S1 deferred-role fail-loud) + receipt extension + enrique sends provider_text (AC-B1/B2/B3/B4/B7).
- [x] T6 GREEN: Vera R7 authoring-gate (AC-B8; provided-but-unwired — S4 follow-on filed) + Storyboard B provider/captions display (AC-B9; S2 surfaces dispatch failures, no swallow).
- [x] T7 Regression: directed-OFF + non-v3 + bracketed-canonical byte-identical (AC-B12); _shared/enrique/irene/marcus/section_07c suites GREEN; ruff clean on touched files; import-linter C3-only, M3 KEPT.
- [ ] T8 LIVE (operator-gated, `@pytest.mark.live` / CI-deselected): two Descript-final arms (A strip / B [tag]) on a real clustered deck via real eleven_v3 + transcript no-leak proxy (AC-B11). NOT RUN this build (operator-gated; out of offline scope).
- [ ] T9 Hand operator the blind A/B → record the finding (either outcome) in the consensus record + handoff. NOT RUN (depends on T8).

## Dev Notes (verified file:line — from the Story B substrate map)
- Canonical→TTS: `_segment_text`/`plan.text` `app/specialists/enrique/_act.py:275-278,635`; directed call site `:686-697`; legacy `:579`. `text_to_speech_with_request_id` sig `scripts/api_clients/elevenlabs_client.py:186-208` (supports model_id/seed/previous_text/next_text/previous_request_ids/apply_text_normalization). `DEFAULT_TTS_MODEL="eleven_multilingual_v2"`; `DEFAULT_DIALOGUE_MODEL="eleven_v3"` (`:36-37`). Client forwards text VERBATIM (no tag parsing) → allowlist enforcement lives in the compiler.
- Receipts `_act.py:732-753` (path `assembly-bundle/receipts/{sid}.json`); effective_settings `:392-399`; audio_sha256 `:707`.
- skip-if-exists `_reusable_receipt` `_act.py:508-527`; call site `:654-684`.
- Captions `_write_vtt` `_act.py:336-343`; directed call `:710` (canonical text). Descript also transcribes audio downstream (`build_descript_narrated_lesson.py:64`) — tag-safe since tags aren't spoken, but the gate is the enrique VTT seam.
- Storyboard B: `storyboard_publisher.py:87-181` (manifest-B) + `generate-storyboard.py:2466` (narration), voice-direction panel `:537-660`, delivery_tag cue `:650-656` (precedent: a tag rendered as a SEPARATE code cue, never inside narration).
- VoiceDirection model `pass_2_template.py:183-211` (extra=forbid). v2 mapper `_shared/voice_direction_map.py` frozen (`SUPPORTED_RENDER_STRATEGIES=frozenset({"tts"})` `:113`, omits delivery_tag `:39-41`).
- Compiler idioms to mirror: `voice_direction_map.py:71-107` (freeze/load), `:22-27,55-56` (M3 fence), `:135-144` (typed error), `:193-200` (flag).
- A/B Descript: `build_descript_narrated_lesson.py` per-arm producer; variant-demo `drive_per_slide_trial.py` is image-variant (NOT audio) — Story B's strip-vs-tag two-arm audio A/B is a NEW driver reusing the per-arm producer.
- Tag allowlist evidence: `evidence/elevenlabs-v3-rhetorical-audition-20260629/manifest.json` (8 tags, 27 samples, Sarah/Shannon/Stark).

### Project Structure Notes
- M3 fence: compiler is a pure `_shared` leaf (no `app.marcus` import); rhetorical_role rides as data; orchestrator/Storyboard read provider_text/channels as data.
- Additive: `rhetorical_role` field + four channels + receipt fields are additive; directed-OFF / non-v3 byte-identical (pin it).

## References
- [Source: _bmad-output/planning-artifacts/enhanced-vo-party-consensus-2026-06-29.md] — Story B ACs, Vera R7, the pre-registered operator-judged A/B, the tag-only invariant, the two roles.
- [Source: _bmad-output/implementation-artifacts/claude-code-brief-enhanced-vo-v3-generation-2026-06-29.md] — the v3 control taxonomy, the canonical-vs-provider-vs-display-vs-captions separation (central hardening), the proposed data shapes.
- [Source: enhanced-vo-1-role-slide-linkage.md] — the slide_key identity join this story builds on (role FIRES on the right slide).

## Dev Agent Record
### Agent Model Used
Amelia (BMAD dev agent) on Claude Opus 4.8 (1M). Offline build T1–T7 + 3-layer-review corrective remediation (M1/S1/S2/S3/S4 + NITs). T8/T9 live legs NOT run (operator-gated).

### Debug Log References
- Compiler RED→GREEN: `tests/specialists/_shared/test_voice_provider_text.py` (31 passed).
- Enrique v3 RED→GREEN: `tests/specialists/enrique/test_enrique_v3_provider_text.py` (10 passed).
- Storyboard B RED→GREEN: `tests/integration/marcus/test_storyboard_v3_provider_text_display.py` (4 passed).
- Consolidated regression: `_shared + enrique + irene + integration/marcus + gates/section_07c` → 672 passed, 2 skipped (pre-existing live-API guards; 3 pre-existing Windows-subprocess-encoding harness failures deselected, confirmed unrelated via clean-HEAD stash).
- `lint-imports` → 14 kept, 1 broken (pre-existing C3 `workbook_producer.graph→resume_api`); M3 KEPT.

### Completion Notes List
- DESIGN: v3 routing branches on `effective_model == "eleven_v3"`; `render_strategy` left as `"tts"` (model vs synthesis-mode are orthogonal). v2 numeric mapper untouched/frozen.
- M1 (MUST-FIX): gates are ALLOWLIST-AWARE, not bracket-blind — canonical brackets ([1]/[Figure 2]/[CO2]/[Na+]/[sic]) are legitimate content that pass through `strip_tags` verbatim, never trip `assert_no_tag_leak`, never appear in `provider_text_tags`. v2/non-v3 path builds NO channels and runs NO gate (channels are a v3-only concern) → bracketed canonical synthesizes byte-identical (AC-B12). compile precondition fails loud if canonical already carries a literal v3 tag.
- S1: a v3 segment with a non-populated (deferred) `rhetorical_role` FAILS LOUD at Enrique pre-flight (`elevenlabs.v3.role.unpopulated`) — no silent v2 downgrade.
- S2: Storyboard B uses the SAME resolved-tier is-v3 decision Enrique uses and SURFACES compile/deferred failures as an explicit "WILL FAIL AT DISPATCH: <reason>" marker (never swallowed to a clean panel).
- S3: skip-if-exists refuses reuse when prior receipt render_mode != current (a v3 [tag]-rendered audio can never satisfy a v2 plan, or vice versa).
- S4: Vera R7 audit is provided-but-unwired this slice (docstring note added incl. the bag-of-words flipped-negation limitation); follow-on `directed-voice-vera-r7-wire-clinical-lexicon` filed in deferred-inventory.
- NITs: cost billed over `plan.sent_text` (provider on v3); storyboard provider block wrapped in `<dl>` (dt/dd nesting); eleven_v3 ~5000-char length guard flagged-not-implemented.

### File List
- NEW `app/specialists/_shared/voice_provider_text.py` — TAG-ONLY v3 compiler + frozen 8-tag allowlist + four-channel builder + allowlist-aware gates + Vera R7 audit (unwired).
- MOD `app/specialists/irene/authoring/pass_2_template.py` — `RhetoricalRole` closed enum + additive optional `rhetorical_role` field on `VoiceDirection`.
- MOD `app/specialists/enrique/_act.py` — model-aware v3 branch (S1 fail-loud), provider_text + seed at the proven call, captions canonical-only seam, receipt extension (v3-only), skip-if-exists provider-sha + render-mode re-key (S3), cost over sent_text.
- MOD `skills/bmad-agent-marcus/scripts/generate-storyboard.py` — manifest-B narration threading + v3 provider/captions display + S2 dispatch-failure marker.
- MOD `_bmad-output/planning-artifacts/deferred-inventory.md` — S4 follow-on `directed-voice-vera-r7-wire-clinical-lexicon`.
- NEW tests: `tests/specialists/_shared/test_voice_provider_text.py`, `tests/specialists/enrique/test_enrique_v3_provider_text.py`, `tests/integration/marcus/test_storyboard_v3_provider_text_display.py`.
