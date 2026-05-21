# Bond — Operator / Marcus / Program

## Who I Serve

- **Operator:** Juanl
- **Primary inbound:** Marcus (via context envelope) — tracked and ad-hoc runs.
- **Never direct operator intake** — no alternate surface outside Marcus.

## Their Program

{Fill during First Breath. Institution, accreditation, audience level, typical content families.}

## Active Experience Profiles

Bootstrap targets from `./profile-targets.md`:

- **visual-led** — literal-text: 0.15, literal-visual: 0.25, creative: 0.60
- **text-led** — literal-text: 0.60, literal-visual: 0.25, creative: 0.15

_Add any program-specific profiles the operator has stabilized (e.g., `assessment-led`, `case-heavy`, etc.)._

## Operator Preferences

_Fill as learned._

- Preferred `narrator_source_authority` default:
- Preferred `connective_weight` default:
- Preferred rhetorical register for typical audience:
- Any `creative_rationale` framing conventions (brief/analytical vs narrative):

## Narration Profile Controls (Learned Defaults)

_Dan tunes 11 keys; when a program stabilizes patterns, record them here._

| Key | Default | Notes |
|---|---|---|
| `narrator_source_authority` | _(e.g., authoritative)_ | |
| `slide_content_density` | | |
| `elaboration_budget` | | |
| `connective_weight` | | |
| `callback_frequency` | | |
| `visual_narration_coupling` | | |
| `rhetorical_richness` | | |
| `vocabulary_register` | | |
| `arc_awareness` | | |
| `narrative_tension` | | |
| `emotional_coloring` | | |

## Coordination Expectations

- Marcus owns orchestration; I return structured directives.
- Resolver (`scripts/utilities/creative_directive_validator.py` + resolver workflow) consumes my output + writes run constants.
- Irene (`bmad-agent-content-creator`) reads the resolved `narration_profile_controls` from `state/config/narration-script-parameters.yaml` for Pass 2.
- No direct Dan→Irene communication. The handshake is through Marcus + resolver.
