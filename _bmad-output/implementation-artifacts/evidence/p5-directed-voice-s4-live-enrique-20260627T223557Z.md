> ⚠️ SUPERSEDED — PREDATES REMEDIATION. The canonical Step-4 live evidence is
> `p5-directed-voice-s4-live-enrique-20260627T230440Z.md` (bundle
> `p5-s4-live-enrique-20260627T230440Z/`), produced through the REMEDIATED shipped
> `build_assembly_bundle`. This run's receipts lack `audio_sha256`/`request_id_present`
> and record `model_id: null`. Retained for history only; do NOT cite as canonical.

# P5 Directed-Voice Step 4 — LIVE Enrique consumption (REAL ElevenLabs)

- Date: 2026-06-27T22:35:57Z
- Flag: `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE=1`
- Policy: §L close-loop — external-API step ⇒ small, cost-bounded REAL call.
- Run: foreground, hard timeout, `load_dotenv(REPO/.env, override=True)`, sentinel-guarded `ELEVENLABS_API_KEY` (key present, len 51).
- Real voice: `CwhRBWXzGAHq8TQ4Fs17` (Roger — Laid-Back, Casual, Resonant), from live `list_voices()`.
- Bundle: `_bmad-output/implementation-artifacts/evidence/p5-s4-live-enrique-20260627T223557Z/`

## What this proves

Enrique consumes per-segment `voice_direction` LIVE through the SHARED 5-tier mapper:
2 adjacent segments with materially-different directions produced **2 real ElevenLabs
calls** with **distinct REAL request-ids** and **distinct resolved settings actually
sent**, plus real MP3 audio + VTT + measured durations + receipts. This is the
consumption-works-live proof; the rigorous acoustic "materially different" analysis
is Step 5 (clips left for Step 5 to analyze).

## The two REAL calls

| Segment | Direction | Resolved settings SENT (stability / style / speed) | REAL request_id | Measured dur | MP3 bytes |
|---|---|---|---|---|---|
| seg-01-reflective | reflective / slower / low | 0.75 / 0.10 / 0.94 | `l0EhRkTP1Q96FgrMoyTj` | 3.37 s | 53,960 |
| seg-02-urgent | urgent / faster / high | 0.30 / 0.65 / 1.10 | `WuZ6JmV1S0ul6MoZho9p` | 3.448 s | 55,214 |

- Distinct request-ids: `l0EhRkTP1Q96FgrMoyTj` ≠ `WuZ6JmV1S0ul6MoZho9p` (surfaced via the new
  `ElevenLabsClient.text_to_speech_with_request_id` reading the provider `request-id` header — ENRIQUE-A2).
- Distinct resolved settings: stability 0.75↔0.30, style 0.10↔0.65, speed 0.94↔1.10
  (pace→speed clean; energy→stability/style bounded; tone coarse, energy overrides) — proven SENT, not just modeled.
- `effective_voice_source = voice-selection.json` (tier-4 default wired this step; no per-segment override).
- `similarity_boost = 0.75` filled from tier-5 `state/config/style_guide.yaml` (no derivation source).
- `render_strategy = tts`; `model_id` resolved None across tiers → client applied its default model.

## Artifacts on disk (under the bundle above)

- `assembly-bundle/audio/seg-01-reflective.mp3` (ID3/MPEG, 53,960 bytes)
- `assembly-bundle/audio/seg-02-urgent.mp3` (ID3/MPEG, 55,214 bytes)
- `assembly-bundle/captions/seg-01-reflective.vtt`, `assembly-bundle/captions/seg-02-urgent.vtt`
- `assembly-bundle/receipts/seg-01-reflective.json`, `assembly-bundle/receipts/seg-02-urgent.json`
- `live-summary.json` (the full machine-readable summary)

Each receipt carries `{segment_id, voice_id, render_strategy, effective_voice_direction,
effective_elevenlabs_settings, effective_voice_source, request_id, model_id, char_count,
cost_usd, narration_file, narration_vtt, narration_duration, pause_*_seconds,
assembled_duration_seconds}` (Card 3 / ENRIQUE-A1).

## Cost

~$0.038 total (char-count proxy: 0.0195 + 0.0186 USD) — cost-bounded, 2 short sentences.

## Post-remediation note (bmad-code-review Step-4 follow-up)

This live run + its captured receipts PRE-DATE the Edge/Blind remediation and STAND as the
live-consumption proof (no re-spend was incurred for the fixes). The remediation changed the
receipt SHAPE: receipts now record `model_id` as the EFFECTIVE model actually used
(`eleven_multilingual_v2`, not `null` — M2), plus `request_id_present: bool` and
`audio_sha256` (S3 — a billed call stays provable even when the provider returns no
request-id header). These shape changes are proven by the offline RED-first unit tests
(`tests/specialists/enrique/test_enrique_directed_voice_remediation.py`) against the MUR-5
fake; the live distinct-request-id / distinct-settings result above is unaffected.
