# Wanda — Wondercraft Audio-Bed Generator

## OPERATOR

Wanda is your **Wondercraft podcast/audio-bed generation specialist**. She generates podcast/audio-bed audio scoped into the storyboard's audio track, complementing Enrique's narration. Beds enrich the audio track with mood/genre cues per Pass-2 narration manifest.

You invoke Wanda implicitly through the trial pipeline at the audio-bed generation stage (post-narration). You talk to Wanda directly when reviewing bed parameters or auditing audio-track scoping.

**When you'd talk to Wanda directly:** asking "what bed mood/genre fits this segment?", reviewing bed-generation parameters, or debugging Wondercraft API responses.

## INPUTS

- **Pass-2 narration manifest** (storyboard cluster boundaries + mood/genre cues).
- **Locked Pass-2 storyboard's audio track** (post-Enrique narration).
- **Wondercraft API client** (`scripts/api_clients/wondercraft_client.py`; consumed unchanged; story-frozen).
- **Wondercraft API reference** (`skills/bmad-agent-wondercraft/SKILL.md` — API-mastery skill; preserved Slab 2b.x era).

## OUTPUTS

- **Per-bed audio**: `[bundle]/assembly-bundle/audio/beds/<bed_id>.{mp3|wav}`.
- **Bed-generation receipts** (per-bed cost / API request-response trace) for evidence log.
- **Wanda summary**: lands at `[bundle]/wanda-summary.md` per 7a.5 specialist-summary-writer integration.

**Live API discipline:** Wondercraft API calls happen ONLY in operator-gated AC-9-B canary windows. CI tests use VCR cassettes under `tests/fixtures/specialist-replay/wanda/`.

## REFERENCE

- **Persona SKILL.md (activation):** `skills/bmad-agent-wanda/SKILL.md` (NEW at 7b.9; two-SKILL.md ratification 4th application)
- **API-mastery SKILL.md (reference):** `skills/bmad-agent-wondercraft/SKILL.md` (preserved Slab 2b.x; consume lazily)
- Sanctum: `_bmad/memory/bmad-agent-wanda/` (6-file BMB; migrated from legacy `_bmad/memory/wanda-sidecar/` 5+1-sidecar pattern at 7b.9 T2; legacy path REMOVED)
- Story spec: [`migration-7b-9-wanda-port-shape-onto-scaffold.md`](../../../_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md)
- T11 review report: [`7b-9-code-review-2026-04-29.md`](../../../_bmad-output/implementation-artifacts/7b-9-code-review-2026-04-29.md)
- Code: `app/specialists/wanda/` (9-node scaffold-v0.2 aligned at 7b.9 per FR96; closes pre-Slab-2b client-landed-not-on-scaffold gap; legacy `wondercraft_dispatch.py` consumed unchanged)
- Credential register: Wondercraft row at `state/config/credential-rotation-register.yaml` (NFR-CG19)
- Rate-limit budget: `app/specialists/wanda/config.yaml` (NFR-CG20)
- Class: C (Wave-4 single-story; Class-C inheritance proven 4× from Gary/Kira/Enrique)
