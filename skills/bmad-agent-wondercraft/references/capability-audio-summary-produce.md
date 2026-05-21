---
name: audio-summary-produce
code: AS
description: Short-form recap / summary audio
---

# Capability AS — audio_summary_produce

Produce a short-form (2-4 minute) recap or summary audio episode.

## Inbound shape (input_packet)

Required:
- `script_path` — short monologue script (target 300-600 words).
- `voice_id` — explicit OR `"voice_director_auto"`.

Optional:
- `intro_outro_template_key`
- `bumper_duration_seconds` — if operator wants a branded bumper attached (calls MB capability internally).

## Dispatch logic

1. Default engine: Voice Director (ElevenLabs) — cost ~4× lower than Wondercraft for short-form equivalent quality.
2. Operator can override to Wondercraft via `engine_preference: "wondercraft"`.
3. When bumper requested, after synthesis call `music_bed_apply` (MB) with the bumper duration.

## Outbound shape

- `audio_path` — MP3 with optional bumper/music bed.
- `transcript_path` — VTT.

## Test coverage (cassette-backed)

- Happy path: 400-word script → 2-3 minute MP3.
- Bumper attachment: MB capability invoked internally on request.
- Engine override: Wondercraft path exercised when operator flags it.
