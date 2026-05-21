# Enrique — ElevenLabs Voice Director

## OPERATOR

Enrique is your **ElevenLabs voice-direction specialist**. He runs the voice-selection HIL at G11/G11B (your choice between candidate voices), then drives ElevenLabs narration synthesis at G12, emitting per-segment audio + captions into the assembly bundle.

You invoke Enrique implicitly through the trial pipeline at G11/G11B/G12. You talk to Enrique directly during the voice-selection HIL — that's a real human-in-the-loop ratification point.

**When you'd talk to Enrique directly:** reviewing `voice-preview-options.json` candidate voices, marking your selection in `voice-selection-review.md`, or asking about voice_settings parameter tuning.

## INPUTS

- **Locked Pass-2 narration script** (post-G3 lock).
- **Storyboard manifest** (segment boundaries + timing).
- **Voice-selection HIL artifacts** (operator-driven):
  - `voice-preview-options.json` — N candidate voices per run-constants (Enrique generates).
  - `voice-selection-review.md` — operator's review markdown (one-line-per-voice; mark recommended).
  - `voice-selection.json` — operator's final selection (Enrique consumes).
- **ElevenLabs API client** (`scripts/api_clients/elevenlabs_client.py`; consumed unchanged).

## OUTPUTS

- **Per-segment audio**: `[bundle]/assembly-bundle/audio/<segment_id>.{mp3|wav}`.
- **Per-segment captions**: `[bundle]/assembly-bundle/captions/<segment_id>.vtt`.
- **Per-segment stderr progress**: `Enrique segment <id> [N/total] OK | duration=<s>s | cost=<usd>` (per AC-7b.8-K binding).
- **Enrique summary**: lands at `[bundle]/enrique-summary.md` per 7a.5 specialist-summary-writer integration; uses `specialist_id="enrique"` with `elevenlabs` aliasing.

**Live API discipline:** ElevenLabs API calls happen ONLY in operator-gated AC-8-B canary windows. CI tests use VCR cassettes under `tests/fixtures/specialist-replay/enrique/`.

## REFERENCE

- **Persona SKILL.md (activation):** `skills/bmad-agent-enrique/SKILL.md` (NEW at 7b.8; two-SKILL.md ratification 3rd application)
- **API-mastery SKILL.md (reference):** `skills/bmad-agent-elevenlabs/SKILL.md` (preserved Slab 2b.x; consume lazily)
- Sanctum: `_bmad/memory/bmad-agent-enrique/` (6-file BMB)
- Story spec: [`migration-7b-8-enrique-port-shape.md`](../../../_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md)
- T11 review report: [`7b-8-code-review-2026-04-29.md`](../../../_bmad-output/implementation-artifacts/7b-8-code-review-2026-04-29.md)
- Code: `app/specialists/enrique/` (9-node scaffold; legacy `elevenlabs_dispatch.py` consumed unchanged)
- Specialist alias: `enrique` ↔ `elevenlabs` per `app/manifest/compiler.py:43-46`
- Credential register: ElevenLabs row at `state/config/credential-rotation-register.yaml` (NFR-CG19)
- Rate-limit budget: `app/specialists/enrique/config.yaml` (NFR-CG20)
- Class: C (Wave-3 LAST closer; closes Wave 3; Class-C inheritance proven 3× — template fully proven inheritable, NO new validator extension)
