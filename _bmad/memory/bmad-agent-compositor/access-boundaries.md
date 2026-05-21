# Access boundaries - compositor

**Specialist:** compositor (Class D2 pipeline-greenfield)

Declares read, write, and deny zones for deterministic assembly. Operational metadata only.

## Read zones

- `[bundle_path]/assembly-bundle/` - existing narration, captions, audio beds, and upstream outputs.
- Gary storyboard or slide manifest paths supplied in `gary_slide_output`.
- Kira motion receipt paths supplied in `motion_receipts` or `motion_asset_paths`.
- Enrique narration package paths supplied in `audio_paths`.
- Wanda audio-bed paths supplied in `audio_bed_paths`.
- `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/field-mask.yaml` - field-mask convention.

## Write zones

- `[bundle_path]/assembly-bundle/visuals/<slide_id>.png` - localized approved stills.
- `[bundle_path]/assembly-bundle/motion/<slide_id>.mp4|webm` - localized approved motion clips.
- `[bundle_path]/DESCRIPT-ASSEMBLY-GUIDE.md` - regenerated Descript handoff guide.
- `_bmad/memory/bmad-agent-compositor/chronology.md` - append-only future pipeline-run records.

## Deny zones

- `app/marcus/orchestrator/dispatch_adapter.py:70-95` - Marcus duality boundary; frozen per FR113.
- `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` templates - consume only; do not modify during Story 7b.11.
- `_bmad/memory/bmad-agent-<other_specialist>/` - other specialist sanctums.
- `skills/bmad-agent-<other_specialist>/` - other specialist skill directories.
- `skills/bmad-agent-compositor/` - must not exist for Class-D2.

## Boundary enforcement

- Test-time parity asserts exactly four sidecar files at `_bmad/memory/bmad-agent-compositor/`.
- Validator Class-D2 assertions enforce no LLM call, no third-party API import, H-Pipeline harness wiring, and frozen-boundary avoidance.
