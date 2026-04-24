---
name: context-envelope-schema
code: ENV
description: Marcus → Wanda dispatch envelope + Wanda → Marcus receipt shapes
---

# Context envelope schema

Wanda consumes standard Marcus dispatch envelopes (per Sprint 1 PR-R
`marcus/dispatch/contract.py`) and returns standard receipts. The Wondercraft-
specific shapes below layer on top of the base envelope.

## Inbound (Marcus → Wanda)

Required fields on the base `DispatchEnvelope`:

- `run_id` — production run identifier.
- `specialist_id` — `"wanda"`.
- `dispatch_kind` — one of:
  - `wanda_podcast_episode` (EP)
  - `wanda_podcast_dialogue` (DP)
  - `wanda_audio_summary` (AS)
  - `wanda_music_bed_apply` (MB)
  - `wanda_chapter_markers_emit` (CM)
  - `wanda_audio_assembly_handoff` (AH)
- `input_packet` — capability-specific; see each capability reference for required keys.
- `context_refs` — paths to source artifacts (script, manifest, prior audio, music beds).
- `correlation_id` — for round-trip tracing.
- `timestamp_utc` — timezone-aware.

Optional capability-common fields in `input_packet`:

- `voice_policy`:
  - `continuity`: `true` / `false`
  - `previous_voice_selection_path`: path to a prior voice-selection receipt (Voice Director)
- `engine_preference`: `"wondercraft"` / `"elevenlabs"` / `"auto"` (default `"auto"`)
- `budget`:
  - `wondercraft_credits_max`: integer cap
  - `elevenlabs_minutes_max`: integer cap
- `chapter_policy`:
  - `mode`: `"derive-from-beats"` (default) / `"explicit"` (operator supplies markers) / `"none"`
- `descript_handoff`: `true` / `false` (default `false`)
- `governance`:
  - `invocation_mode`, `current_gate`, `authority_chain`, `decision_scope`, `allowed_outputs`

## Outbound (Wanda → Marcus)

Standard `DispatchReceipt` fields plus diagnostics:

- `outcome`: `complete` / `partial` / `failed`
- `output_artifacts`: tuple of artifact paths (audio MP3, VTT, RSS metadata JSON, Descript project JSON).
- `diagnostics`:
  - `engine_used`: `"wondercraft"` / `"elevenlabs"` / `"both"`
  - `voice_decisions`: mapping of segment/beat → voice_id
  - `chapter_markers`: list of `{title, start_seconds}` (when emitted)
  - `credits_used`: integer (Wondercraft)
  - `elevenlabs_minutes_used`: integer (ElevenLabs)
  - `cost_estimate_usd`: optional float when cost surface is exposed
  - `parameter_decisions`: exact settings passed to upstream API
- `duration_ms`

## Scope-violation posture

If `input_packet` requests work outside `governance.allowed_outputs` or Wanda's
`decision_scope`, return with `outcome=failed` and `diagnostics.scope_violation={reason, route_to}`. Do NOT silently produce out-of-scope artifacts.
