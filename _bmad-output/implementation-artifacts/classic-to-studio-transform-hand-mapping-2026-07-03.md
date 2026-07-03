# Classic → Studio transform — reference hand-mapping (transformer-skill spec)

Session-10 (2026-07-03). Produced by hand-transforming the Classic style
`hil-2026-apc-crossroads-blueprint` → the Studio companion
`hil-2026-apc-crossroads-blueprint-studio` through the studio-via-API override
plumbing. **This table IS the spec for the deferred `Classic → Studio` transformer
skill** (next arc): it names, field-by-field, what maps, what is dropped, and what
Studio adds — with the rationale a generalizing transformer needs.

Source (Classic) record: `state/config/gamma-style-guides.yaml::hil-2026-apc-crossroads-blueprint`
Target (Studio) record: `…::hil-2026-apc-crossroads-blueprint-studio`

## Column 1 — MAPS (carried across, possibly re-homed)

| Classic field | → Studio field | Transform + rationale |
|---|---|---|
| `production_mode: api` | `production_mode: studio` | The declarative type-tag flip. Everything else follows from the modality (declarative, not an orthogonal switch). |
| `theme.id: e8tz1vxb9v1urqp` | `studio_template.theme_id: e8tz1vxb9v1urqp` | The Blueprint Editorial palette is the load-bearing visual identity — it RE-HOMES from the Classic `theme` block to the Studio per-record `theme_id` override on the base template. This is the single most important carry: it is what makes the Studio deck *this* style rather than the bare Studio-B template. |
| `visuals.image_model: recraft-v3` | `studio_template.image_model: recraft-v3` | The clean-Western image model re-homes from the Classic `visuals` surface to the Studio per-record `image_model` override. Carries the runner-up decision (recraft-v3 over gpt-image-2-mini) intact. |
| `presentation.*` (display_name, distinguishing, narrative, feels_like, use/avoid) | `presentation.*` (rewritten for Studio) | Re-authored, not copied: the *register* is preserved (crossroads / Blueprint palette / clinical) but the delivery description changes (per-slide illustration + real text → full-bleed 16:9 image-card with embedded text). |
| Western/no-iconography intent (Classic `additional_instructions` prose) | subsumed by `image_model: recraft-v3` + the wrapper English-only constant | The *English-only* half is now enforced code-side (`_STUDIO_ENGLISH_ONLY_STEER` inside `_STUDIO_LOCK_WRAPPER`, applies to ALL studio records); the *Western/no-iconography* half is carried implicitly by recraft-v3's clean-Western prior. See the transformer note below. |

## Column 2 — DROPPED (Classic-only surface; forbidden on a studio record, by name)

These are the Classic surface keys the discriminated union forbids on a studio record
(`STYLEGUIDE_CLASSIC_ONLY_KEYS`). The transformer must DROP each — the Studio template
plus the two overrides are the sole style authority:

- `prompt_configuration.text_content.mode` (`condense`) — Studio template owns typography
- `prompt_configuration.text_content.amount` (`minimal`)
- `prompt_configuration.text_content.audience` / `tone` (null here)
- `prompt_configuration.text_content.language` (`en`) — English is enforced by the wrapper steer instead
- `prompt_configuration.visuals.image_source` (`aiGenerated`)
- `prompt_configuration.visuals.style_preset` (`illustration`) — the template look is the authority
- `prompt_configuration.visuals.custom_style` (null)
- `prompt_configuration.visuals.keywords` (`[]`) — no Classic keyword channel on Studio
- `page_settings.card_options.dimensions` (`fluid`) — Studio is full-bleed 16:9 via the template, not a Classic dimension
- `page_settings.ui_only_reference.*` (card_width / content_alignment / font_size / show_card_backdrops / animations / card_headers_footers) — Classic UI reference, no Studio meaning
- (The Classic `theme` block and `visuals.image_model` are *re-homed*, not dropped — see Column 1.)

## Column 3 — STUDIO-ONLY ADDITIONS (no Classic source; the transformer must synthesize)

| Studio field | Value | Why the transformer must add it |
|---|---|---|
| `studio_template.gamma_id` | `g_nv5q4da69qiiu8q` | The base full-bleed Studio-B template. **Transformer input:** which base template to build on (constant for now; a future menu). |
| `studio_template.theme_id` | (from Classic `theme.id`) | The override slot the plumbing added. Carries the Classic theme. |
| `studio_template.image_model` | (from Classic `visuals.image_model`) | The override slot the plumbing added. Carries the Classic model. |
| `studio_prompt_lock.{wrapper_id, behavior, guard}` | `gary_studio_lock_wrapper_v1` + `aspect_ratio_min 1.4 / 1.7778` | The lock-and-swap contract + the 16:9 aspect guard that proves no Classic fallback. Constant across studio records. |
| `_STUDIO_LOCK_WRAPPER` + `_STUDIO_ENGLISH_ONLY_STEER` | code-level (`_act.py`) | Not a record field — applies to every studio dispatch. The transformer relies on it (does NOT re-encode English-only in the record). |
| `derived_from` | `hil-2026-apc-crossroads-blueprint` | Lineage pointer to the Classic sibling (inert provenance; never read by the resolver). **The transformer sets this automatically** = the source record's id. |
| `authored_session` / `promotion_criteria` / `provenance.runner_up` | (candidate contract) | Lifecycle fields for a born-candidate record; the promotion_criteria encodes the Studio-specific gates (micro-text legibility, sibling-parity). |
| `theme: null` | — | A studio record carries no Classic `theme` block; the theme rides `studio_template.theme_id` instead. |

## Transformer notes (for the skill, next arc)

1. **The re-home pattern is the core insight:** Classic `theme.id` → `studio_template.theme_id`, Classic `visuals.image_model` → `studio_template.image_model`. Two fields cross the modality boundary; everything else in the Classic `prompt_configuration`/`page_settings` surface is dropped.
2. **The Western/no-iconography steer needs a decision the transformer must make explicit:** here it is subsumed (recraft-v3 + the English-only wrapper constant). If a Classic style's steer carries subject-specific content that recraft-v3 does NOT cover, the transformer must surface it (a studio record cannot carry Classic keyword/instruction surface — so subject steering has to live in the per-slide brief or be accepted as a limitation). Flag this as a transformer decision point, not a silent drop.
3. **Promotion is always deferred to the operator eye** — the transformer produces a `candidate`, never a `permanent`.
4. **Sibling-parity:** a Studio companion may not be promoted above its still-candidate Classic parent (encoded in criterion 6).
