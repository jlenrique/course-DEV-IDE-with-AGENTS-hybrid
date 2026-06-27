# P5 Directed-Voice Step 4 — LIVE Enrique consumption (REAL ElevenLabs, REMEDIATED path)

- Date: 2026-06-27T23:04:40Z
- Flag: `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE=1`
- Policy: §L close-loop — external-API step ⇒ small, cost-bounded REAL call.
- Run: foreground, hard timeout, `load_dotenv(REPO/.env, override=True)`, sentinel-guarded `ELEVENLABS_API_KEY` (key present, len 51).
- Real voice: `CwhRBWXzGAHq8TQ4Fs17` (Roger — Laid-Back, Casual, Resonant), from live `list_voices()`.
- **Canonical bundle:** `_bmad-output/implementation-artifacts/evidence/p5-s4-live-enrique-20260627T230440Z/`
- **Supersedes** `p5-s4-live-enrique-20260627T223557Z` (that run predates the bmad-code-review remediation; its receipts lack `audio_sha256`/`request_id_present` and record `model_id: null`). This bundle was produced through the REMEDIATED, shipped `build_assembly_bundle` so the canonical evidence matches shipped code.

## What this proves (against the SHIPPED, remediated code)

Enrique consumes per-segment `voice_direction` LIVE through the SHARED 5-tier mapper. Two
adjacent segments with materially-different directions produced **2 real ElevenLabs calls**
with **distinct REAL request-ids**, the full remediated receipt shape, real MP3 + VTT +
measured durations. This is the consumption-works-live proof; the rigorous acoustic
"materially different" analysis is Step 5 (clips left for Step 5).

## The two REAL calls (post-remediation receipt fields verified live)

| Segment | Direction | Resolved settings SENT (stability / style / speed) | REAL request_id | `request_id_present` | `model_id` (effective) | `audio_sha256` (first 12) | Measured dur | MP3 bytes |
|---|---|---|---|---|---|---|---|---|
| seg-01-reflective | reflective / slower / low | 0.75 / 0.10 / 0.94 | `VAUuakU9yaMrqmLrcz1a` | `true` | `eleven_multilingual_v2` | `0aa674e30c00` | 3.396 s | 54,378 |
| seg-02-urgent | urgent / faster / high | 0.30 / 0.65 / 1.10 | `cLIZF5tykK3TkLD3RxOY` | `true` | `eleven_multilingual_v2` | `f398b6c1c69c` | 3.37 s | 53,960 |

Live-asserted in the run (all PASSED — `[live] POST-REMEDIATION ASSERTIONS PASSED`):
- **Distinct real request-ids:** `VAUuakU9yaMrqmLrcz1a` ≠ `cLIZF5tykK3TkLD3RxOY` (surfaced via `text_to_speech_with_request_id` reading the provider `request-id` header).
- **request_id_present = true** on both (S3).
- **audio_sha256** matches `sha256(narration_file bytes)` on both (S3 — billed-call proof; the assertion re-reads the written mp3 and recomputes).
- **model_id = `eleven_multilingual_v2`** (the EFFECTIVE model actually used — M2; no `null`) in both the receipt and `effective_elevenlabs_settings`, and that is the model SENT.
- **Distinct resolved settings:** stability 0.75↔0.30, style 0.10↔0.65, speed 0.94↔1.10 — proven SENT, not just modeled.
- `effective_voice_source = voice-selection.json` (tier-4 default); `similarity_boost = 0.75` from tier-5 `state/config/style_guide.yaml`.

## Artifacts on disk (under the canonical bundle)

- `assembly-bundle/audio/seg-01-reflective.mp3` (ID3/MPEG, 54,378 bytes), `assembly-bundle/audio/seg-02-urgent.mp3` (ID3/MPEG, 53,960 bytes)
- `assembly-bundle/captions/seg-01-reflective.vtt`, `assembly-bundle/captions/seg-02-urgent.vtt`
- `assembly-bundle/receipts/seg-01-reflective.json`, `assembly-bundle/receipts/seg-02-urgent.json`
- `live-summary.json`

Each receipt carries `{segment_id, voice_id, render_strategy, effective_voice_direction,
effective_elevenlabs_settings, effective_voice_source, request_id, request_id_present,
audio_sha256, model_id, char_count, cost_usd, narration_file, narration_vtt,
narration_duration, pause_*_seconds, assembled_duration_seconds}` (Card 3 / ENRIQUE-A1 + remediation S3/M2).

## Cost

~$0.038 total (char-count proxy: 0.0195 + 0.0186 USD) — cost-bounded, 2 short sentences.
