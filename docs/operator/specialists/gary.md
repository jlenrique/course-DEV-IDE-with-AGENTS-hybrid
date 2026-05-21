# Gary — Gamma Slide Generator

## OPERATOR

Gary is your **Gamma slide-generation specialist**. He drives the Gamma API to generate Storyboard-A slides from the Pass-2 narration manifest, then exports them for review at G2 (Storyboard-A approval gate).

You invoke Gary implicitly through the trial pipeline at G2. You talk to Gary directly when reviewing slide-generation parameters or debugging Gamma API responses.

**When you'd talk to Gary directly:** asking "what's the Gamma API parameter contract?", reviewing slide export options, or debugging a Gamma generation failure (live canary mode).

## INPUTS

- **Pass-2 narration manifest** (segment-level narration + visual cues).
- **Gamma API client** (`scripts/api_clients/gamma_client.py`; consumed unchanged).
- **Gamma API reference** (`skills/bmad-agent-gamma/SKILL.md` — API-mastery skill; preserved Slab 2b.x era; consumed lazily as reference material).
- **Storyboard-A authorize gate context** (G2 lever).

## OUTPUTS

- **Storyboard-A slide deck** (Gamma export format).
- **Slide-generation receipts** (per-slide cost / API request-response trace / fingerprints) for evidence log.
- **Gary summary**: lands at `[bundle]/gary-summary.md` per 7a.5 specialist-summary-writer integration.

**Live API discipline:** Gamma API calls happen ONLY in operator-gated AC-6-B canary windows (≤3 canaries; ≤$0.40/canary). CI tests use VCR cassettes under `tests/fixtures/specialist-replay/gary/`.

## REFERENCE

- **Persona SKILL.md (activation):** `skills/bmad-agent-gary/SKILL.md` (NEW at 7b.6; minimal FR101 R1 frontmatter; activation hot-load batch references the BMB sanctum)
- **API-mastery SKILL.md (reference):** `skills/bmad-agent-gamma/SKILL.md` (preserved Slab 2b.x; consume lazily; NOT modified by Slab 7b)
- Sanctum: `_bmad/memory/bmad-agent-gary/` (6-file BMB)
- Story spec: [`migration-7b-6-gary-port-shape.md`](../../../_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md)
- Code: `app/specialists/gary/` (9-node scaffold; `gamma_dispatch.py` consumed unchanged)
- Credential register: Gamma row at `state/config/credential-rotation-register.yaml` (NFR-CG19)
- Rate-limit budget: `app/specialists/gary/config.yaml` (NFR-CG20)
- Class: C (Wave-3 first port; **first Class-C two-SKILL.md application**, ratified party-mode 4/4 unanimous Round-(f) 2026-04-29)
