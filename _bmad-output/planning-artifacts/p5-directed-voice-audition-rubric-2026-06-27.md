# P5 Directed Voice Palette and Audition Rubric

Date: 2026-06-27
Author: BMAD Marcus, with Codex transport verification
Audience: Claude Code agent and its active BMAD workflow / party-mode review team
Status: Complementary advisory artifact; use with the active goal statement, control cards, and Claude team's own BMAD decisions

## 0. Advisory Role

This artifact is not intended to overwrite Claude Code's active BMAD workflow, party-mode review, story decisions, or implementation findings. It is a complementary support note from BMAD Marcus, meant to reduce ambiguity and give the implementing team a grounded checklist of current repo/API facts to consider.

If Claude's BMAD party-mode team finds newer local evidence, a better implementation path, or a necessary schema adjustment, their reviewed decision should govern. In that case, update this artifact or supersede it with a dated follow-up so the advisory record stays aligned with the implementation.

## 1. Non-Negotiable Grounding

This artifact is intentionally limited to structures, enum values, mapper behavior, and API fields that are present in the repository or verified against the current ElevenLabs API docs at the time of writing.

Recommendation: do not invent new directorial fields, palette values, or API settings during P5 implementation without an explicit BMAD-reviewed schema decision. If a desired direction cannot be represented by the current contract, record it as a follow-on schema decision.

Important product interpretation: the current v1 product schema is a starting scaffold, not the ceiling for expressive voice. The first major P5 gain is moving from batch-level voice settings to clip-level/per-segment control with reviewable metadata and receipts. The broader expressive/conversational range should be explored through the API sweep and then promoted into a later schema only after Claude's BMAD workflow has evidence that the control is reliable, maintainable, and worth exposing to specialist agents.

Verified local sources:

| Source | Current implementation fact |
| --- | --- |
| `app/specialists/irene/authoring/pass_2_template.py` | Defines `VoiceDirection`, `ElevenLabsSettings`, and `DialogueTurn`; this is the authoring contract. |
| `app/specialists/enrique/voice_direction_map.yaml` | Defines the frozen v1 tone/pace/energy to TTS settings table. |
| `app/specialists/_shared/voice_direction_map.py` | Pure mapper from `VoiceDirection` to flat TTS settings; default-off feature flag is `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE`. |
| `scripts/api_clients/elevenlabs_client.py` | Local ElevenLabs client supports TTS, TTS with timestamps, and Text-to-Dialogue. |
| `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` | Existing narration generation path already uses timestamps, VTT output, request ids, style-guide defaults, and continuity ids. |

Verified external docs:

| API doc | Use |
| --- | --- |
| `https://elevenlabs.io/docs/api-reference/text-to-speech/convert` | TTS conversion endpoint and fields such as `voice_settings`, `stability`, `similarity_boost`, `style`, `speed`, `seed`, and request continuity fields. |
| `https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert` | Text-to-Dialogue endpoint, `inputs`, `settings`, `voice_id`, `text`, `model_id`, `seed`, and `output_format`. |

## 2. Current Legal VoiceDirection Contract

The v1 segment field is:

`SegmentManifestSegment.voice_direction: VoiceDirection | None`

Legal `VoiceDirection` fields:

| Field | Legal values or bounds | P5 usage |
| --- | --- | --- |
| `schema_version` | `"voice-direction.v1"` | Required version marker. |
| `render_strategy` | `"tts"` or `"dialogue"` | `tts` is consumed in v1. `dialogue` is modeled but not consumed in v1. |
| `delivery_intent` | string, max 500 chars | Human-readable direction/provenance only. Do not send as narration. |
| `emotional_tone` | `neutral`, `warm`, `concerned`, `urgent`, `reflective`, `encouraging` | Coarse palette value mapped through YAML. |
| `pace` | `slower`, `neutral`, `faster` | Maps to speed through YAML. |
| `energy` | `low`, `medium`, `high` | Maps to stability/style through YAML and overrides tone on those fields. |
| `delivery_tag` | string, max 120 chars | Generation-text-only cue. Must remain isolated from displayed/gated narration. |
| `pause_before_seconds` | 0.0 to 5.0 | Metadata for intended timing; ensure downstream use is explicit before relying on it. |
| `pause_after_seconds` | 0.0 to 5.0 | Metadata for intended timing; ensure downstream use is explicit before relying on it. |
| `elevenlabs` | `ElevenLabsSettings | None` | Explicit per-field override. |
| `dialogue_turns` | tuple of `{speaker, text, voice_id}` | Modeled only in v1; do not wire to production TTD without an explicit follow-on story. |
| `source` | `role-derived`, `cd-authored`, `operator-override` | Provenance for review and precedence. |

Legal `VoiceDirection.elevenlabs` override fields:

| Field | Bounds | Notes |
| --- | --- | --- |
| `voice_id` | string | Highest priority voice override. |
| `model_id` | string | Explicit model override. |
| `stability` | 0.0 to 1.0 | Overrides tone/energy-derived stability. |
| `similarity_boost` | 0.0 to 1.0 | No tone/energy derivation; override or defaults only. |
| `style` | 0.0 to 1.0 | Overrides tone/energy-derived style. |
| `speed` | 0.7 to 1.2 | Overrides pace-derived speed. |

Do not add `seed`, `use_speaker_boost`, `output_format`, `language_code`, `previous_request_ids`, `next_request_ids`, or pronunciation dictionaries to `VoiceDirection.elevenlabs` in P5 unless the schema is intentionally expanded. The local client supports some of those fields, but the current per-segment contract does not.

## 3. Current YAML Palette

The current map version is `voice-direction-map.v1`.

### Pace

| `pace` | Derived ElevenLabs `speed` |
| --- | ---: |
| `slower` | 0.94 |
| `neutral` | 1.0 |
| `faster` | 1.1 |

### Energy

Energy overrides tone on the shared `stability` and `style` fields.

| `energy` | Derived `stability` | Derived `style` |
| --- | ---: | ---: |
| `low` | 0.75 | 0.10 |
| `medium` | 0.50 | 0.35 |
| `high` | 0.30 | 0.65 |

### Emotional Tone

Tone provides coarse defaults unless `energy` is also present.

| `emotional_tone` | Derived `stability` | Derived `style` |
| --- | ---: | ---: |
| `neutral` | 0.50 | 0.30 |
| `warm` | 0.55 | 0.40 |
| `concerned` | 0.60 | 0.25 |
| `urgent` | 0.30 | 0.55 |
| `reflective` | 0.62 | 0.22 |
| `encouraging` | 0.45 | 0.50 |

Unsupported v1 tone labels include `skeptical`, `calm`, `serious`, `curious`, `whispered`, `dramatic`, `empathetic`, and `transitional`. These may appear in `delivery_intent` prose, but not as enum values.

## 4. Recommended P5 Audition Palette

Use a small matrix that proves real per-segment variation without multiplying risk.

| Audition case | Recommended fields | Purpose |
| --- | --- | --- |
| Baseline narration | `emotional_tone: neutral`, `pace: neutral`, `energy: medium` | Confirms no-regression reference against ordinary narration. |
| Reflective synthesis | `emotional_tone: reflective`, `pace: slower`, `energy: low` or `medium` | Tests slower, steadier summary delivery. |
| Warm orientation | `emotional_tone: warm`, `pace: neutral`, `energy: medium` | Tests welcome, transition, and reassurance tone. |
| Concerned risk cue | `emotional_tone: concerned`, `pace: neutral` or `slower`, `energy: medium` | Tests safety/risk material without melodrama. |
| Urgent caution | `emotional_tone: urgent`, `pace: faster`, `energy: high` | Tests sparing alert emphasis; use only for genuinely time-sensitive moments. |
| Encouraging action | `emotional_tone: encouraging`, `pace: neutral` or `faster`, `energy: medium` or `high` | Tests call-to-action and learner confidence moments. |

For natural conversational range, vary only one or two dimensions at a time unless the slide has a strong reason. Example: do not combine `urgent`, `faster`, `high`, and an aggressive `delivery_tag` on ordinary explanatory content.

## 5. Delivery Tags and Nuance

Directorial nuances such as "whispering", "thoughtfully", "with a small pause", or "almost aside" are not ElevenLabs numeric parameters in the current app contract. For P5, they may be attempted only through `delivery_tag`, and must satisfy these rules:

1. `delivery_tag` is generation-text-only.
2. `delivery_tag` must never appear in learner-facing Storyboard B narration text.
3. `delivery_tag` must never reach the figure-citation gate as narration text.
4. `delivery_tag` effects must be auditioned, not assumed. The API may ignore, overplay, or inconsistently interpret the cue.
5. If a tag changes spoken wording or caption text, the case fails.

Recommended initial tags for audition only:

| Tag | Safe use |
| --- | --- |
| `[thoughtfully]` | Reflective synthesis or debrief. |
| `[warmly]` | Orientation or reassurance. |
| `[with concern]` | Risk cue or learner safety issue. |
| `[brief pause]` | Transition, only if VTT and duration remain acceptable. |

Do not promise whispering as a production control in P5. Treat it as an audition experiment until live proof shows reliable output and no caption/script contamination.

## 6. TTS vs Text-to-Dialogue Decision

Use TTS for P5 directed narration. It already supports per-segment voice settings through the current schema and mapper.

Use Text-to-Dialogue only for a later explicit story where:

1. The slide truly requires multiple speakers or turn-taking.
2. `dialogue_turns` are wired from the already gated `narration_text` without adding new learner speech.
3. Storyboard B displays the turns before spend.
4. Enrique has a real `render_strategy: dialogue` dispatch path.
5. Captions, receipts, and review artifacts preserve per-turn provenance.

Do not use TTD merely to get whispering, urgency, warmth, or pacing. Those are P5 TTS direction/audition concerns.

## 6A. API Exploration Lane

The production heartbeat and the API exploration sweep are related but distinct.

Recommended sequencing:

1. First get the directed-voice heartbeat working through the current P5 path: Storyboard B visible direction, Enrique consumption, generated audio, VTT, and receipt.
2. Then run an explicit ElevenLabs exploration sweep that exercises every locally available request parameter at least once, even if many fields never become agent-facing product controls.
3. Keep the sweep evidence separate from production schema decisions. A successful exploratory call does not automatically mean Irene, CD, or another specialist should be allowed to set that field.

For continuous numeric controls, "every value" means min, midpoint/default-style, and max coverage, not every real number.

This lane is not optional nice-to-have learning if schedule allows. It is the evidence path that protects the larger purpose of the feature: discovering how much expressive and conversational range ElevenLabs can actually provide before the app freezes a narrow vocabulary around it.

### TTS / TTS-with-Timestamps Sweep

Use `scripts/api_clients/elevenlabs_client.py::text_to_speech()` and `text_to_speech_with_timestamps()` as the local callable surface. Prefer `text_to_speech_with_timestamps()` for production-like proof because it returns timing data and request metadata.

| Parameter or field | Sweep coverage recommendation | Notes |
| --- | --- | --- |
| `text` | Short sentence, longer narration paragraph, punctuation-heavy sentence, pronunciation-sensitive term. | Confirms plain narration and edge text. |
| `voice_id` | Default selected voice plus at least one alternate available voice. | Must come from `list_voices()` or existing voice-selection artifact. |
| `model_id` | Current default `eleven_multilingual_v2` plus any other account-available TTS models from `list_models()`. | Do not hard-code model availability beyond what the account reports. |
| `stability` | 0.0, 0.5, 1.0. | Numeric boundary/midpoint coverage. |
| `similarity_boost` | 0.0, 0.75, 1.0. | Includes local default-style value. |
| `style` | 0.0, 0.5, 1.0. | Confirms style exaggeration range. |
| `speed` | 0.7, 1.0, 1.2. | Matches current contract bounds. |
| `use_speaker_boost` | `true`, `false`, and omitted. | Omitted matters because `_clean_payload` removes null fields. |
| `output_format` | Each docs-visible format at least once if account supports it. | Log unsupported/plan-gated responses without treating them as failures of directed voice. |
| `language_code` | Omitted plus at least one explicit relevant code, for example `en`. | Use course language context; do not invent multilingual product scope from one call. |
| `pronunciation_dictionary_locators` | Omitted plus one real dictionary locator if available. | If no dictionary exists, record as blocked/unavailable rather than faking the field. |
| `seed` | Omitted plus one fixed integer repeated twice. | Measures practical repeatability, not a guarantee of determinism. |
| `previous_text` | Omitted plus preceding-context text. | Tests context continuity without request ids. |
| `next_text` | Omitted plus following-context text. | Tests context continuity without request ids. |
| `previous_request_ids` | Omitted plus the prior call's returned request id. | Exercises continuity stitching. |
| `next_request_ids` | Omitted plus a future/known request id only if a safe test sequence can provide one. | If not practical, record rationale. |
| `use_pvc_as_ivc` | `true`, `false`, and omitted where voice/account support allows. | May be voice/account constrained. |
| `apply_text_normalization` | `auto`, `on`, `off`, and omitted. | Local client documents these values. |
| `apply_language_text_normalization` | `true`, `false`, and omitted. | TTS-only local parameter. |

Docs-visible `output_format` strings observed for TTS/TTD at artifact time:

`mp3_22050_32`, `mp3_24000_48`, `mp3_44100_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`, `mp3_44100_192`, `opus_48000_32`, `opus_48000_64`, `opus_48000_96`, `opus_48000_128`, `opus_48000_192`, `pcm_8000`, `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_32000`, `pcm_44100`, `pcm_48000`, `ulaw_8000`, `alaw_8000`.

If the docs or account report additional formats at runtime, include them in the sweep and update the evidence note.

### Text-to-Dialogue Sweep

Use `scripts/api_clients/elevenlabs_client.py::text_to_dialogue()` for exploration only unless Claude's BMAD team intentionally expands P5 scope.

| Parameter or field | Sweep coverage recommendation | Notes |
| --- | --- | --- |
| `inputs` | One two-turn exchange, one three-turn exchange, and one same-speaker repeated-turn case. | Each input should include supported `voice_id` and `text` fields. |
| `model_id` | Current default `eleven_v3` plus any account-available dialogue models from `list_models()`. | Confirm actual account availability. |
| `language_code` | Omitted plus one explicit relevant code. | Same caution as TTS. |
| `settings` | Omitted plus one non-empty settings dict accepted by the API. | The local client passes this through as a dict; verify accepted keys from current docs/account behavior before relying on them. |
| `pronunciation_dictionary_locators` | Omitted plus one real dictionary locator if available. | Same constraint as TTS. |
| `seed` | Omitted plus one fixed integer repeated twice. | Compare outputs qualitatively and via metadata/hash. |
| `apply_text_normalization` | `auto`, `on`, `off`, and omitted. | Same value set as local TTS parameter. |
| `output_format` | Same docs-visible output formats as TTS where account supports them. | Log unsupported formats. |

TTD exploration should answer one question only: what additional control surface is real and reliable enough to justify a later story? It should not delay the P5 TTS heartbeat unless Claude's BMAD team decides the current goal requires it.

### Sweep Evidence Record

Each exploratory call should record:

| Field | Purpose |
| --- | --- |
| endpoint/method | `text_to_speech`, `text_to_speech_with_timestamps`, or `text_to_dialogue`. |
| request parameter set | Redacted if needed, but complete enough to reproduce. |
| model and voice ids | Proves what actually generated the clip. |
| request id | Supports continuity and auditability. |
| output path and format | Confirms artifact creation. |
| duration and VTT path where available | Confirms timing/caption behavior. |
| success, API rejection, or account limitation | Rejections are evidence, not noise. |
| reviewer note | Captures audible effect and whether it is product-worthy. |

## 7. Mapper and Precedence Expectations

Advisory recommendation: preserve the current 5-tier per-field precedence unless Claude's BMAD workflow deliberately changes the contract:

1. Segment `voice_direction.elevenlabs.{field}`
2. Direction-derived values from `pace`, `energy`, and `emotional_tone`
3. Pass-2 `voice_direction_defaults`
4. `voice-selection.json` selected default
5. `state/config/style_guide.yaml` defaults

For `voice_id`, tier 2 is the segment `voice_id`, not a derived setting:

1. `voice_direction.elevenlabs.voice_id`
2. Segment `voice_id`
3. Pass-2 defaults
4. Voice-selection default
5. Style-guide default

`energy` overrides `emotional_tone` for `stability` and `style`. `pace` independently derives `speed`.

`render_strategy: dialogue` and `dialogue_turns` remain modeled-not-consumed in P5 unless the active goal is explicitly changed.

## 8. Storyboard B Review Requirements

Storyboard B should show enough direction metadata for human review before audio spend. Treat this as an advisory checklist for Claude's implementation and party-mode review:

| Display item | Required behavior |
| --- | --- |
| `render_strategy` | Show `tts`; show `dialogue` only as modeled/inert unless wired in a later story. |
| `delivery_intent` | Show as review/provenance metadata, not as script. |
| `emotional_tone` | Show exact enum value or blank. |
| `pace` | Show exact enum value or blank. |
| `energy` | Show exact enum value or blank. |
| `delivery_tag` | Show as generation-only cue, visually distinct from narration. |
| `pause_before_seconds` / `pause_after_seconds` | Show if present. |
| explicit `elevenlabs` overrides | Show only populated fields. |
| `source` | Show provenance. |

Storyboard B must continue to keep learner-facing narration separate from direction metadata.

## 9. Audition Rubric

Score each auditioned segment as Pass, Warn, or Fail.

| Criterion | Pass | Warn | Fail |
| --- | --- | --- | --- |
| Contract validity | Uses only legal v1 fields and values. | Uses legal fields but direction is vague or over-specified. | Uses unsupported enum/API fields. |
| Narration integrity | Spoken words match approved narration; citations remain untouched. | Minor pronunciation or pacing concern. | Direction changes wording, visible script, or citation behavior. |
| Audible differentiation | Directed version is clearly but appropriately different from baseline. | Difference is subtle but acceptable for the slide. | No meaningful difference, or effect is exaggerated. |
| Fit to slide role | Direction matches slide intent, cluster role, and instructional purpose. | Plausible but not strongly motivated. | Direction fights the slide's purpose. |
| Captions and timing | VTT aligns and duration remains acceptable. | Small timing drift requiring review. | Captions unusable or duration breaks composition. |
| Receipt quality | Segment receipt records effective direction/settings and request id. | Receipt incomplete but recoverable. | No auditable evidence of what was sent/generated. |
| Maintainability | Uses mapper/defaults/receipts rather than ad hoc one-off logic. | Minor duplication. | Bypasses the contract or mapper. |

## 10. P5 Completion Bar for Directed Voice

Recommended P5 completion bar for the directed-voice slice:

1. At least three distinct directed treatments are visible in Storyboard B before spend.
2. The same treatments are consumed by Enrique through the shared mapper or an equally reviewable contract-preserving path.
3. Generated receipts include effective direction/settings, `voice_id`, `request_id`, audio path, VTT path, and duration.
4. A live proof compares baseline against directed outputs and includes at least one non-neutral treatment.
5. A separate API exploration sweep exercises every locally available ElevenLabs request parameter at least once, or records why a parameter was unavailable/account-blocked.
6. No unsupported palette values or schema fields are introduced into the production P5 contract without BMAD-reviewed expansion.
7. `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` default-off behavior preserves old narration behavior when disabled.
8. BMAD party review explicitly decides whether the audible variation is production-credible or requires a narrower palette.

## 11. Claude Handoff Sentence

Advisory handoff to Claude: Load `_bmad-output/planning-artifacts/p5-directed-voice-audition-rubric-2026-06-27.md` as Marcus's complementary grounded palette/rubric addendum. Consider its listed v1 fields, enum values, YAML settings, mapper precedence, and API-supported local client behavior during BMAD review, but let Claude's active BMAD workflow and party-mode decisions govern final implementation choices.

## 12. STEP-5 PARTY RULING (2026-06-27) — §10 item 8 RESOLVED

Step-5 close party (Murat 🧪 / Quinn-R 🔎 / CD 🎬 / Enrique 🎙️, unanimous CLOSE, no impasse) ruled on §10 item 8 (production-credible vs narrower palette), against the deterministic acoustic proof (`evidence/p5-directed-voice-s5-live-acoustic-proof-20260627T231354Z.md`):

- **RULING: production-credible AS-IS — keep the full §4 palette, with a TIERED, HONESTLY-LABELED product promise.** Do NOT narrow to pace-only.
- **`pace` = the GUARANTEED, reliably-perceptible directed dial** (pace→duration cleared 3×floor cleanly: Δ0.186s on a ~3.3s clip, ~4× the nondeterminism floor; pedagogically-correct direction). Specialists MAY set it by pedagogical role.
- **`emotional_tone` + `energy` = BEST-EFFORT / aspirational expressive nuance — auditioned, NOT promised.** The settings ARE sent (receipts), but ElevenLabs spends `stability`/`style` on timbre/prosody, not broadband loudness (energy→RMS sat at the nondeterminism floor — a measurement-PROXY finding, honestly reported, NOT a defect or a pipeline failure). Do NOT advertise "energy/intensity control" to specialist agents or in any product copy until the LUFS/F0 follow-on confirms a perceptible scalar.
- **Binding labeling (CD/Quinn-R):** mark this tiering in the contract/Storyboard-B/rubric framing — pace guaranteed, tone/energy best-effort. (This §12 + the strawman §G-RECONCILED note are the authoritative record; the Storyboard-B panel best-effort label rides the `directed-voice-energy-scalar-and-best-effort-labeling` follow-on.)
- **Keep `urgent`/`faster`/`high` sparing** (Quinn-R / §4), never stacked with an aggressive `delivery_tag` on ordinary explanatory content.
- **§10 item 5 (full API exploration sweep) remains OUTSTANDING** — a distinct §6A lane that must close before the directed-voice product's expressive ceiling is claimed. Does not block this learner-facing verification close.
