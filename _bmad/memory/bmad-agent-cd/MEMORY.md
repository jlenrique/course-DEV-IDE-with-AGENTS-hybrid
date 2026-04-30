# Memory

Curated long-term knowledge. Session logs live in `sessions/`.

## Current Directive State

_Updated per session. If there's an active directive request, record:_

- **Run ID + module/lesson:**
- **Requested experience profile** (if specified by operator):
- **Resolved profile:**
- **Directive artifact path:** (returned to Marcus)
- **Validator result:**

## Profile Tuning Patterns

_Learned over multiple runs. 3+ consistent runs before promoting to a durable pattern._

- (empty — accumulates)

## Narration Profile Control Defaults by Content Type

_Patterns that stabilize per program._

- (empty)

## Creative Rationale Phrasing Conventions

_Operator's preferred framing style over time._

- (empty)

## Operator Preferences

_Promoted from BOND when stable._

- (empty)

## Known Gotchas

- **2026-04-17**: Schema v1.0 requires all 11 `narration_profile_controls` keys explicitly. Partial directives fail `creative_directive_validator.py`. Use BOND's Learned Defaults as starting point, not a license to omit.
- **2026-04-17**: `slide_mode_proportions` floats must sum to 1.0 ±0.001. If target anchors sum to exactly 1.0, avoid rounding individual values in the directive — validator is strict.

## Historical Context

- **2026-04-17**: Migrated from legacy sidecar (`_bmad/memory/dan-sidecar/`) to BMB sanctum (`_bmad/memory/bmad-agent-cd/`) as Epic 26 Story 26-3. Predecessor pilots: Marcus 26-1, Irene 26-2.
- **2026-04-16**: Persona named "Dan" (was descriptor-only "Creative Director (CD) Agent" before). "CD" preserved as the lane/role shorthand in contracts and lane-matrix.
- **Wave 2B (Epic 20c)**: Dan's contract and the 11-key `narration_profile_controls` surface were closed as part of stories 20c-9 (narration parameter expansion), 20c-10 (CD agent creation), 20c-11 (creative directive schema), 20c-12 (experience profile definitions), 20c-13 (profile resolver wiring), 20c-14 (E2E validation).
