# Kira — Kling Motion Generator

## OPERATOR

Kira is your **Kling motion-generation specialist**. She drives the Kling API to generate per-slide motion clips (image-to-video and text-to-video) from Storyboard-A slides at G2M (motion designation gate).

You invoke Kira implicitly through the trial pipeline at G2M. You talk to Kira directly when reviewing motion-generation parameters or debugging Kling polling state.

**When you'd talk to Kira directly:** asking "what's the Kling motion-generation contract?", reviewing image-to-video vs text-to-video selection, or debugging a polling failure.

## INPUTS

- **Storyboard-A slides** (post-G2 approved deck).
- **Per-slide motion designation** (image-to-video / text-to-video / static; from G2M operator gate).
- **Kling API client** (`scripts/api_clients/kling_client.py`; `generate_motion()` submit-and-poll added at 7b.7 T11).
- **Kling API reference** (`skills/bmad-agent-kling/SKILL.md` — API-mastery skill; preserved Slab 2b.x era).

## OUTPUTS

- **Per-slide motion clips** (mp4/webm format).
- **Motion-generation receipts** (per-clip cost / API request-response trace / polling state) for evidence log.
- **Terminal Kling receipts** for completed motion results (per AC-7b.7-C; PATCH-1 closure at 7b.7 T11).
- **Kira summary**: lands at `[bundle]/kira-summary.md` per 7a.5 specialist-summary-writer integration.

**Live API discipline:** Kling API calls happen ONLY in operator-gated AC-7-B canary windows. CI tests use VCR cassettes under `tests/fixtures/specialist-replay/kira/`.

## REFERENCE

- **Persona SKILL.md (activation):** `skills/bmad-agent-kira/SKILL.md` (NEW at 7b.7; two-SKILL.md ratification 2nd application)
- **API-mastery SKILL.md (reference):** `skills/bmad-agent-kling/SKILL.md` (preserved Slab 2b.x; consume lazily)
- Sanctum: `_bmad/memory/bmad-agent-kira/` (6-file BMB)
- Story spec: [`migration-7b-7-kira-port-shape.md`](../../../_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md)
- T11 review report: [`7b-7-code-review-2026-04-29.md`](../../../_bmad-output/implementation-artifacts/7b-7-code-review-2026-04-29.md)
- Code: `app/specialists/kira/` (9-node scaffold)
- Credential register: Kling row at `state/config/credential-rotation-register.yaml` (NFR-CG19)
- Rate-limit budget: `app/specialists/kira/config.yaml` (NFR-CG20)
- Class: C (Wave-3 parallel; Class-C inheritance proven 2× from Gary)
