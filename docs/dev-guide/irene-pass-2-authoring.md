# Irene Pass 2 Authoring

Irene Pass 2 now has a schema-first authoring contract plus the existing procedural validator.

Authoritative surfaces:
- Pydantic source: `app/specialists/irene/authoring/pass_2_template.py`
- Generated schema: `schema/irene_pass_2_authoring.v1.schema.json`
- Prompt-facing template: `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`
- Procedural oracle: `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`

Validation order is schema-first, then procedural. The schema covers structural fields such as Gary slide output, perception artifact alignment, segment timing fields, visual detail load, visual references, cluster role, cluster position, and composition mode. Procedural validation covers prose-level rules such as bridge cadence, cluster arc continuity, narration cue presence in spoken narration, behavioral intent parity, motion perception confirmation, and traceable visual references.

## Minimal Passing Example

```json
{
  "schema_version": "irene-pass-2-authoring.v1",
  "run_id": "PASS2-GOLDEN-001",
  "generated_at_utc": "2026-04-28T10:00:00Z",
  "composition_mode": "composed",
  "gary_slide_output": [{"slide_id": "slide-01", "card_number": 1, "file_path": "bundle/slide-01.png", "source_ref": "slide-brief.md#Slide 1"}],
  "perception_artifacts": [{"slide_id": "slide-01", "source_image_path": "bundle/slide-01.png", "visual_elements": []}],
  "segment_manifest": {
    "segments": [{
      "id": "seg-01",
      "slide_id": "slide-01",
      "card_number": 1,
      "narration_text": "Notice the clinician at the workstation.",
      "behavioral_intent": "credible",
      "visual_file": "bundle/slide-01.png",
      "visual_detail_load": "medium",
      "timing_role": "concept-build",
      "content_density": "medium",
      "duration_rationale": "Medium density needs guided explanation.",
      "bridge_type": "none",
      "cluster_id": "c1",
      "cluster_role": "head",
      "cluster_position": "establish",
      "visual_references": [{"element": "Clinician", "location_on_slide": "center", "narration_cue": "clinician", "perception_source": "slide-01"}]
    }]
  },
  "narration_script_markers": ["seg-01"],
  "procedural_rules": [
    "behavioral_intent_parity",
    "bridge_cadence",
    "cluster_arc_continuity",
    "motion_perception_confirmation",
    "narration_cue_presence",
    "traceable_visual_references"
  ]
}
```

Use `composition_mode: isolated` for M3 harness/direct specialist trials and `composition_mode: composed` for production runner use through `ProductionDispatchAdapter`.
