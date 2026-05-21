---
name: compositor
description: Deterministically localize approved lesson media and regenerate the Descript Assembly Guide. Use when Marcus reaches G3 assembly handoff or when an operator invokes the compositor pipeline.
---

# Compositor

## Purpose

Compositor is a Class-D2 deterministic assembly specialist. It is not a persona agent and does not call an LLM. It copies approved stills and motion clips into the assembly bundle and regenerates `DESCRIPT-ASSEMBLY-GUIDE.md` from fixed inputs.

## Activation Hot-Load

Load the operational sidecar at `_bmad/memory/bmad-agent-compositor/`:

- `contract.md` - input, output, side-effect, and error contracts.
- `version.md` - behavioral version pinning.
- `chronology.md` - append-only pipeline-run history.
- `access-boundaries.md` - read, write, and deny zones.

## Runtime Body

The LangGraph body lives at `app/specialists/compositor/` and consumes `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/`.

Primary operations:

- `sync_visuals`: copy still PNGs to `[bundle_path]/assembly-bundle/visuals/<slide_id>.png`.
- `sync_motion`: copy motion clips to `[bundle_path]/assembly-bundle/motion/<slide_id>.mp4|webm`.
- `regenerate_assembly_guide`: write `[bundle_path]/DESCRIPT-ASSEMBLY-GUIDE.md`.
- `field_masked_hash`: mask `generated_at`, `run_id`, and `build_timestamp` before hash comparison.

## Operating Rules

- Use only fixed filesystem inputs from the dispatch envelope.
- Preserve source bytes for localized assets.
- Do not import provider clients or chat/model adapters.
- Do not create `skills/bmad-agent-compositor/`.
- Do not create persona-continuity files in the sidecar.
