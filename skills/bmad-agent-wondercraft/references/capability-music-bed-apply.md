---
name: music-bed-apply
code: MB
description: Apply background music bed to an existing audio artifact
---

# Capability MB — music_bed_apply

Apply a background music bed to an existing episode or bumper.

## Inbound shape (input_packet)

Required:
- `audio_path` — existing MP3/WAV to bed.
- `bed_key` — key into `resources/audio/music-beds/` index (mood-based: `calm` / `energetic` / `reflective` / `neutral`).

Optional:
- `mix_level_db` — default -18 dB for voice-over safety.
- `fade_in_seconds`, `fade_out_seconds` — default 2.0 each.
- `intro_bumper_seconds` — if a full-volume bumper precedes the voice section.

## Dispatch logic

1. Music beds are applied **post-synthesis** — this capability is a finishing pass.
2. If Wondercraft has native music-bed support in the episode API, use it at production time. Otherwise, apply via a local ffmpeg pipeline in this capability.
3. Emit the new audio file; do NOT overwrite the original (operator may want both).

## Outbound shape

- `audio_path` — new MP3 with music bed applied (e.g., `_bedded` suffix in filename).
- `bed_applied` — diagnostic mapping: `{bed_key, mix_level_db, fade_in_seconds, fade_out_seconds}`.

## Non-goals

- Arbitrary music library integration (operator's library is cataloged in `resources/audio/music-beds/`; external library support is a follow-on).
- Dynamic bed switching mid-episode (use Descript handoff for that).

## Test coverage (cassette-backed)

- Happy path: mono voice + calm bed → bedded MP3 emitted with correct mix level.
- Missing bed_key: returns `failed` with available bed-keys enumerated.
- Ffmpeg missing: returns `failed` with remediation (install ffmpeg or use Descript handoff instead).
