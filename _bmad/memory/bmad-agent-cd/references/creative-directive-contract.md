---
name: creative-directive-contract
code: DR
description: Creative directive schema v1.0 — mode key enum, numeric constraints (sum-to-1.0 ±0.001), 11-key narration_profile_controls surface, validator-enforced on emission
---

# Creative Directive Contract (20c-10)

## Schema

```yaml
schema_version: "1.0"
experience_profile: string  # one of: visual-led, text-led
slide_mode_proportions:
  literal-text: float
  literal-visual: float
  creative: float
narration_profile_controls:
  narrator_source_authority: string
  slide_content_density: string
  elaboration_budget: string
  connective_weight: string
  callback_frequency: string
  visual_narration_coupling: string
  rhetorical_richness: string
  vocabulary_register: string
  arc_awareness: string
  narrative_tension: string
  emotional_coloring: string
creative_rationale: string
```

## Validation Rules

1. `slide_mode_proportions` must contain exactly these keys:
   - `literal-text`
   - `literal-visual`
   - `creative`
2. Each proportion must be numeric and in `[0, 1]`.
3. Proportions must sum to `1.0` within tolerance `±0.001`.
4. `experience_profile` maps to a profile target in `state/config/experience-profiles.yaml`.
5. `narration_profile_controls` must include the full 11-key Wave 2B control surface with valid enum values.
6. Unknown top-level keys are disallowed for v1.0.

Machine enforcement is provided by `scripts/utilities/creative_directive_validator.py`.
