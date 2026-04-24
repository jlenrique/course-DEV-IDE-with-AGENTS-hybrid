---
name: podcast-dialogue-produce
code: DP
description: Multi-voice dialogue / interview / case-discussion format
---

# Capability DP — podcast_dialogue_produce

Produce a multi-voice podcast episode from a dialogue or interview script.

## Inbound shape (input_packet)

Required:
- `script_path` — dialogue script in canonical dialogue or interview structure (see discovery-podcasts-audio-content.md §Goal 2).
- `voices` — mapping of speaker label (e.g., `"host"` / `"guest"` / `"case-lead"`) → `voice_id`.
- `target_duration_minutes` — integer length envelope.

Optional:
- `pronunciation_dictionary_path`
- `turn_transition_sfx` — SFX library key for between-turn transitions.
- `scaffold_mode` — `"intro_outro"` / `"full"` / `"none"` for interview scaffolding.

## Dispatch logic

1. Always route to Wondercraft — dialogue / conversation mode is Wondercraft's sweet spot.
2. Call `create_conversation_podcast(title, script)` for turn-taking content OR `create_scripted_podcast` when operator has pre-scripted every turn.
3. Poll with `wait_for_job(job_id)` (budget-capped).
4. On completion, download audio, emit VTT with per-turn speaker labels.

## Outbound shape

- `audio_path` — MP3 / M4A (with chapters if `chapter_policy.mode == "derive-from-beats"`).
- `transcript_path` — VTT with speaker labels per turn.
- `rss_metadata_path` — optional.

## Cost posture

Conversation-mode runs ~1.5× the credits of monologue. Surface estimate before synthesis. Typical 20-minute dialogue ≈ 8-12 Wondercraft credits.

## Voice continuity

When `voice_policy.continuity` is `true` AND the lesson already has ElevenLabs narration in scope, consult `previous_voice_selection_path` to choose Wondercraft voices whose register matches the ElevenLabs voice. Emit `voice_decisions` in the receipt so Quinn-R can audit.

## Test coverage (cassette-backed)

- Happy path: 2-voice dialogue → MP3 + VTT with speaker labels.
- Scripted mode fallback when turn-taking is pre-resolved.
- Voice continuity: consult prior selection, emit matching choice.
- Unsupported voice_id: returns `failed` with remediation.
