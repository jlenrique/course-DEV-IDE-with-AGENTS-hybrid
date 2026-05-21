---
name: podcast-episode-produce
code: EP
description: Single-host monologue episode from narration script
---

# Capability EP — podcast_episode_produce

Produce a single-host monologue podcast episode from an approved narration script.

## Inbound shape (input_packet)

Required:
- `script_path` — path to monologue script in the canonical monologue structure (see `_bmad-output/planning-artifacts/discovery-podcasts-audio-content.md §Goal 2`).
- `target_duration_minutes` — integer length envelope.
- `voice_id` — explicit voice OR `"voice_director_auto"` to delegate voice choice to Voice Director.

Optional:
- `pronunciation_dictionary_path` — per-course pronunciation YAML.
- `sfx_markers` — mapping of marker tokens to SFX library keys.
- `intro_outro_template_key` — key into `state/config/audio/podcast-intro-outro.yaml`.

## Dispatch logic

1. If operator `engine_preference` is `"elevenlabs"` OR `target_duration_minutes <= 4`, route to Voice Director (Enrique) — delegation envelope emitted as `handoff_elevenlabs` diagnostic.
2. Else route to Wondercraft `create_scripted_podcast(title, script, voice_id=...)`.
3. Poll with `wait_for_job(job_id)` (budget-capped).
4. On completion, download audio, emit VTT from script structure, attach intro/outro per template.

## Outbound shape (output_artifacts)

- `audio_path` — MP3 (default) or WAV (if operator requested uncompressed).
- `transcript_path` — VTT.
- `rss_metadata_path` — optional JSON for feed integration.

## Cost posture

Surface credit estimate BEFORE synthesis: typical lecture-podcast episode ≈ 2-4 Wondercraft credits per 10 minutes. If `budget.wondercraft_credits_max` would be exceeded, return `failed` with remediation pointing at the operator budget dial.

## Test coverage (cassette-backed)

- Happy path: 6-minute script → MP3 + VTT emitted.
- Voice-director routing: short-form → Voice Director delegation emitted.
- Budget exceeded: returns `failed` with structured remediation.
- Script malformed: returns `failed` before any API call.
