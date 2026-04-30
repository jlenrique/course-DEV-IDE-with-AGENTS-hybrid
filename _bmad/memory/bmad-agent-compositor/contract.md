# Operational contract - compositor

**Specialist:** compositor (Class D2 pipeline-greenfield)
**Authored at:** 2026-04-30 (Story 7b.11 T1 readiness)
**Last updated at:** 2026-04-30

Operational metadata for Class-D2 specialists replaces persona-shaped continuity. Compositor has no `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, or `CAPABILITIES.md`.

## Input contract

**Schema reference:** `app/specialists/compositor/state.py::CompositorEnvelope`

| Field | Type | Required | Source | Description |
|---|---|---|---|---|
| `bundle_path` | path string | yes | Marcus G3 dispatch | Root bundle for deterministic assembly outputs. |
| `gary_slide_output` | list[object] | yes | Gary | Approved still PNG source paths plus slide ids. |
| `motion_receipts` or `motion_asset_paths` | list[object/string] | no | Kira | Approved motion clips for localized motion output. |
| `audio_paths` | list[string] | no | Enrique | Narration audio paths already generated under the assembly bundle. |
| `audio_bed_paths` | list[string] | no | Wanda | Music or bed paths already generated under the assembly bundle. |
| `assembly_guide_path` | path string | no | Marcus or default | Overrides default `[bundle_path]/DESCRIPT-ASSEMBLY-GUIDE.md`. |

## Output contract

**Schema reference:** `app/specialists/compositor/state.py::CompositorReturn`

| Field | Type | Determinism | Description |
|---|---|---|---|
| `bundle_path` | string | bytes-identical | Bundle root used by the run. |
| `synced_assets.visuals` | mapping | bytes-identical | Localized still files under `assembly-bundle/visuals/`. |
| `synced_assets.motion` | mapping | bytes-identical | Localized motion files under `assembly-bundle/motion/`. |
| `assembly_guide_path` | string | field-masked-hash | Regenerated Descript guide path. |
| `assembly_guide_field_masked_hash` | sha256 string | field-masked-hash | Hash after masking `generated_at`, `run_id`, and `build_timestamp`. |

## Side effects

| Path | Format | Determinism | Cleanup behavior |
|---|---|---|---|
| `[bundle_path]/assembly-bundle/visuals/<slide_id>.png` | PNG | bytes-identical | overwritten on rerun |
| `[bundle_path]/assembly-bundle/motion/<slide_id>.mp4|webm` | video | bytes-identical | overwritten on rerun |
| `[bundle_path]/DESCRIPT-ASSEMBLY-GUIDE.md` | markdown | field-masked-hash | overwritten on rerun |

## Substrate paths consumed

- `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/field-mask.yaml` - field-mask source of truth.
- `tests/integration/scaffold_conformance/scaffold_contract.py` - 9-node scaffold verifier.
- `app/models/state/specialist_summary_artifacts.py` - summary landing facade.

## Substrate paths NOT touched

- `app/marcus/orchestrator/dispatch_adapter.py:70-95` - frozen Marcus boundary.
- `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` templates - consumed, not modified.
- Any other specialist sanctum or skill directory.

## Error modes

| Error | When raised | Recovery |
|---|---|---|
| `CompositorActError` | Missing source asset or malformed envelope | Fix upstream bundle paths and rerun. |
