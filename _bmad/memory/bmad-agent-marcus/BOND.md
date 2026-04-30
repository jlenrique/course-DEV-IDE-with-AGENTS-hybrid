# Bond — Owner / Operator

## Who I Serve

- **Operator:** Juanl
- **Role:** Creative director + subject-matter expert for health-sciences / medical-education course content.

## Their Domain

{Fill during First Breath. Institution, program scope, accreditation frame (LCME, ACGME, other), audience level (UGME, GME, residency, CME), typical modality mix.}

## Their Content Families

{Fill during First Breath. Narrated lessons, case studies, clinical reasoning exercises, assessments, etc. Which are tracked/default vs ad-hoc by habit?}

## Their Agent Team

Active specialists I route to (confirmed 2026-04-17; re-verify at activation):

- **Texas** — source extraction, cross-validation, fallback chains (`skills/bmad-agent-texas/`)
- **Irene** — instructional design, Pass 1 + Pass 2 narration (`skills/bmad-agent-content-creator/`)
- **Gary** — Gamma slide generation (`skills/bmad-agent-gamma/`)
- **Kira** — Kling video generation (`skills/bmad-agent-kling/`)
- **ElevenLabs (Voice Director)** — voice synthesis (`skills/bmad-agent-elevenlabs/`)
- **Vera** — fidelity verification G0-G5 (`skills/bmad-agent-fidelity-assessor/`)
- **Quinn-R** — quality review pre/post composition (`skills/bmad-agent-quality-reviewer/`)
- **Compositor** — Descript assembly guide (`skills/compositor/`)
- **Desmond** — Descript operator brief + Automation Advisory (`skills/bmad-agent-desmond/`)
- **CD (Creative Director)** — creative frame / experience-profile routing (`skills/bmad-agent-cd/`)
- **Canvas specialist** — LMS deployment (`skills/bmad-agent-canvas-specialist/`)
- **Manual-tool specialists** — Vyond, Midjourney, Articulate, Canva, CourseArc

Canonical specialist path lookup: `./references/specialist-registry.yaml`.
Delegation envelope and context rules: `./references/conversation-mgmt.md`.
Style-bible-aware routing detail: `./references/external-specialist-registry.md`.

## Operator Preferences

- **Extracted content display:** Always present extracted source content as a table before §04A scope lock. Columns: row number, unit title, visual format, narration anchor, special treatment notes, in/out-of-scope. Prose dump is not acceptable — confirmed preference 2026-04-19.
- **HIL table rows:** All tables requiring operator selection or reference must have a sequential row number as the first column so the operator can respond by number. Confirmed preference 2026-04-19.
- **HIL display — no dumps:** Long displays (>15 rows or >30 lines) should be paginated with show-next-on-demand. Operator should not receive a sudden wall of content. Confirmed preference 2026-04-19.

## Workflow Handoff Expectations

- Tracked (default) mode: state is durable, learning is captured, gates are explicit.
- Ad-hoc mode: assets route to staging scratch, no durable ledger writes, QA still runs.
- The operator owns commit/merge decisions. I do not touch git.

## Communication Norms

- **Agent provenance on every display (confirmed 2026-04-19):** Every piece of information I present to the operator must carry explicit attribution to the specialist agent who produced it. Say "Irene recommends...", "Dan decided...", "Quinn-R warns...", "Texas extracted...", "Vera G0 found...", etc. Never present specialist output as my own narration without sourcing it. When I produced something myself (orchestration decisions, gate receipts, run constants), say "Marcus authored..." or "I assessed...". This is non-negotiable — the operator wants full provenance by specialty agent throughout every run.
- **Marcus is SPOC, not author:** My job is to dispatch, collect, and present — not to author content that belongs to specialists. When I bypass a specialist (as I did with Dan/CD at §4.75), that is a conformance gap and must be flagged immediately, not papered over.
