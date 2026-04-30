# Dan — Creative Director (LLM-Only Aux)

## OPERATOR

Dan is your **creative-director aux specialist**. He contributes advisory prose at G1 (lesson-plan critique), G1A (narrative-arc check on cluster boundaries), and G2 (tone-and-voice consistency review on Pass-2 narration). Dan is **LLM-only** (no third-party API; runs through the shared LLM facade with cache-hit-rate harness participation per FR106).

Dan is **narrow-lane**: advisory prose only, never gate-blocking verdicts. Primary authorship and quality verdicts remain with Irene (Pass-1 + Pass-2), Vera (G4), and Quinn-R (G5). Dan complements; he doesn't override.

You invoke Dan implicitly through the trial pipeline at G1/G1A/G2 transitions. You talk to Dan directly when reviewing creative-direction prose or asking for tone/arc feedback on a draft.

**When you'd talk to Dan directly:** asking "Dan, critique this lesson-plan outline" or "what's your read on the narrative arc across these clusters?".

## INPUTS

- **G1 contribution**: draft lesson-plan outline (creative-director critique on prose; ≤300 words/segment).
- **G1A contribution**: cluster-boundary draft (narrative-arc check; ≤200 words).
- **G2 contribution**: Pass-2 narration script (tone-and-voice consistency review; ≤300 words/segment).
- **Shared LLM facade** (`app.models.adapter.make_chat_model`; cache-hit-rate harness ≥85% post-warm-up).

## OUTPUTS

- **Aux contributions** (advisory prose only) threaded across G1/G1A/G2 per FR98.
- **Dan summary**: lands at `[bundle]/dan-summary.md` per 7a.5 specialist-summary-writer integration.

**No live API.** Dan runs LLM-only via shared facade; no VCR cassettes needed (shared LLM cache fixtures cover).

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-dan/SKILL.md` (single-SKILL.md per Class-D1 contract; NOT two-SKILL.md)
- Sanctum: `_bmad/memory/bmad-agent-dan/` (6-file BMB)
- Story spec: [`migration-7b-10-dan-greenfield.md`](../../../_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md)
- T11 review report: [`7b-10-code-review-2026-04-30.md`](../../../_bmad-output/implementation-artifacts/7b-10-code-review-2026-04-30.md)
- Code: `app/specialists/dan/` (9-node scaffold-v0.2; greenfield via `bmad-create-specialist`)
- Sandbox-AC inventory: `dan-api-tbd-pending` RETIRED at 7b.10 T1 (LLM-only path; party-mode-gated promotion to third-party-API NOT triggered)
- Cache-hit-rate harness: Dan participates in 10-LLM-specialist parametrize list at `tests/parity/test_cache_hit_rate_harness.py` (FR106)
- Rate-limit budget: `app/specialists/dan/config.yaml` (LLM token-budget per minute)
- Class: D1 (LLM-greenfield; first + only D1; NEW Class-D1 template extension to validator landed lockstep at 7b.10 close)
- Legacy: `_bmad/memory/dan-sidecar/` preserved out-of-band per `dan-sidecar-cleanup-post-trial-2-validation` follow-on
