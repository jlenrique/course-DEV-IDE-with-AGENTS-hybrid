# Tracy — Pass-2 Research-Shaped Intent Enricher

## OPERATOR

Tracy is your **Pass-2 research-shaped intent enrichment companion** for Texas retrieval. She runs between Pass-1 (Texas retrieval done) and Pass-2 (Irene narration), enriching the operator-directive into a `RetrievalIntent` shape that Texas can re-fetch against. She does NOT translate provider DSLs (provider adapters own that knowledge).

You invoke Tracy implicitly through the trial pipeline at the Pass-1→Pass-2 transition. You talk to Tracy directly when refining a research intent or when retrieval coverage gaps surface at Pass-1.

**When you'd talk to Tracy directly:** asking "what would research-shape this gap into?", reviewing the RetrievalIntent emission shape, or seeing how a posture-dispatch hint would refine a directive.

## INPUTS

- **Pass-1 retrieval bundle** (six canonical artifacts from Texas).
- **Operator directive** (the original or as edited at G0).
- **Posture dispatch context** (from `posture_dispatch.py`; consumed unchanged from Slab 2b era).

## OUTPUTS

- **`RetrievalIntent`**: natural-language emission shape per `skills/bmad-agent-texas/references/retrieval-contract.md`. Texas re-consumes this for Pass-2 retrieval.
- **Tracy summary**: lands at `[bundle]/tracy-summary.md` per 7a.5 specialist-summary-writer integration.

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-tracy/SKILL.md`
- Sanctum: `_bmad/memory/bmad-agent-tracy/` (4-file Class-C+ sidecar pattern: `INDEX.md` / `PERSONA.md` / `chronology.md` / `access-boundaries.md`)
- Story spec: [`migration-7b-5-tracy-port-shape-sidecar.md`](../../../_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md)
- Code: `app/specialists/tracy/` (9-node scaffold; `posture_dispatch.py` consumed unchanged)
- Class: C+ (4-file sidecar variant; canonical Class-C+ pattern per NFR-CG15 Decision Log §10)
- Required AC reference: Texas retrieval-contract per Round-(e) E4 binding-hard
- Note: `skills/bmad-agent-tracy/` (HYPHENATED) carries SKILL.md only; `skills/bmad_agent_tracy/` (UNDERSCORED) is the Python-package with `references/postures.md` + `references/vocabulary.yaml` consumed by the body
