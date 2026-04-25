# Irene expertise (L5 — narration Pass 2)

Specialist `irene` reads domain references from this directory during the
`plan` stage of its 9-node scaffold. Per architecture D5 (sanctum cold-read +
cache-prefix stability), references are loaded by dotted convention from
the operator-facing skill tree at
[`skills/bmad-agent-content-creator/references/`](../../../../skills/bmad-agent-content-creator/references/)
— Irene's app-side specialist directory carries pointers, not duplicated content.

- **mcp_tool:** `none` (Pass 2 is pure-LLM narration authoring; no external tool calls)
- **expertise_tier:** `L5-narration-pass-2`
- **sanctum:** `_bmad/memory/bmad-agent-content-creator/` (hybrid path; epic-doc
  drift A11 — see `docs/dev-guide/specialist-anti-patterns.md`)

## Sanctum-state convention (Story 2a.2)

Per the D2 SYNTHESIS verdict ratified at this story's pre-T1 party-mode round
2026-04-24, the sanctum is **empty for the duration of this story** to give
the FR54 cache-hit-rate baseline a deterministic empty-fingerprint reference.
The pre-2a.2 46-file payload was archived to
`_bmad/memory/_archive/bmad-agent-content-creator-pre-2a2-2026-04-24/`.
Story 2a.3 (Kira) inherits the populated-and-locked pattern and exercises
the dotted-reference convention against a curated first-breath population.

See [`docs/dev-guide/sanctum-reference-conventions.md`](../../../../docs/dev-guide/sanctum-reference-conventions.md)
§Epoch-note for the activation-baseline vs steady-state distinction.

## L5 reference set (loaded at `plan` node via dotted convention)

| Dotted reference | Source-tree path | Pass-2 step |
|---|---|---|
| `pass-2-procedure.md` | [skills/bmad-agent-content-creator/references/pass-2-procedure.md](../../../../skills/bmad-agent-content-creator/references/pass-2-procedure.md) | All steps — primary procedure |
| `pass-2-authoring-template.md` | [skills/bmad-agent-content-creator/references/pass-2-authoring-template.md](../../../../skills/bmad-agent-content-creator/references/pass-2-authoring-template.md) | Step 2 — segment-manifest schema + lint |
| `pass-2-grammar-riders-examples.md` | [skills/bmad-agent-content-creator/references/pass-2-grammar-riders-examples.md](../../../../skills/bmad-agent-content-creator/references/pass-2-grammar-riders-examples.md) | Step 2 — narration grammar exemplars |
| `retrieval-intake-contract.md` | [skills/bmad-agent-content-creator/references/retrieval-intake-contract.md](../../../../skills/bmad-agent-content-creator/references/retrieval-intake-contract.md) | Intake — Texas retrieval evidence merger |
| `cluster-narrative-arc-schema.md` | [skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md](../../../../skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md) | Step 2 — cluster-aware narration arcs |
| `spoken-bridging-language.md` | [skills/bmad-agent-content-creator/references/spoken-bridging-language.md](../../../../skills/bmad-agent-content-creator/references/spoken-bridging-language.md) | Step 2 — bridge cadence verbiage |
| `runtime-variability-framework.md` | [skills/bmad-agent-content-creator/references/runtime-variability-framework.md](../../../../skills/bmad-agent-content-creator/references/runtime-variability-framework.md) | Step 2 — slide-length variance grounded in purpose |
| `visual-reference-injection.md` | [skills/bmad-agent-content-creator/references/visual-reference-injection.md](../../../../skills/bmad-agent-content-creator/references/visual-reference-injection.md) | Step 2 — visual_references[] injection per slide |
| `motion-plan-hydration.md` | [skills/bmad-agent-content-creator/references/motion-plan-hydration.md](../../../../skills/bmad-agent-content-creator/references/motion-plan-hydration.md) | Step 3 — motion-enabled segment manifest |
| `motion-perception-confirmation.md` | [skills/bmad-agent-content-creator/references/motion-perception-confirmation.md](../../../../skills/bmad-agent-content-creator/references/motion-perception-confirmation.md) | Step 4 — non-static segment perception |

These references are loaded as text into the Pass 2 act-node prompt assembly.
`SanctumFingerprint.compute(...)` hashes the sanctum directory contents at run
start; for empty-sanctum runs (this story) the hash is the deterministic empty
sorted-listing sha256.
