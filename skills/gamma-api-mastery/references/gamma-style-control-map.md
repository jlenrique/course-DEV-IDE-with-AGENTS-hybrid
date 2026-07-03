# Gamma Style Control Map — traceability matrix

**Status:** authored 2026-07-03 (operator-directed "start over with style creation" arc).
**Scope:** every *style-influencing* control across three layers — Gamma's product UI, Gamma's Generate REST API, and our own code (Gary + the styleguide registry) — mapped to each other, with the **owner** (who sets/edits each value) and **consumer** (who reads it) for every field.

## ⛔ Binding principle (operator-stated 2026-07-03)

> Our style **auditing scripts, the validator, and tests MUST draw upon this matrix — or the source authorities it cites — so that all fields and values stay harmonized and aligned as much as possible, all the time.**

Concretely:
- The **registry** (`state/config/gamma-style-guides.yaml`) stores values in **Gamma's UI vocabulary** — what the operator authors by looking at the Gamma prompt editor (e.g. `amount: minimal`, not the API's `brief`). The registry is faithful to what a human sees in Gamma.
- **This matrix is the mapping authority** (UI label ↔ API value ↔ Gary packet field). It is the single place the UI→API translation is defined.
- The **tooling harmonizes**: Gary translates UI→API at submission time; the validator accepts the UI vocabulary by checking it against this matrix's authorities; `audit_gamma_docs.py` keeps our enums aligned to the *live* Gamma docs. Drift surfaces as a failing audit, never a silent divergence.

Nobody hand-maintains a second, divergent copy of any enum. If a value appears in the validator, the audit manifest, a test, and this matrix, they all trace to the same authority row below.

## Authorities (sources of truth)

| Layer | Authority | Fetch / ref |
|---|---|---|
| Gamma UI controls | Gamma user help | `help.gamma.app` (articles 11029115 page-setup, 11969695 styling/layout, 11016396 cards, 11028318 text) |
| Gamma API fields/values | Gamma developer docs (raw-markdown fetchable: append `.md`, or `llms-full.txt`) | `developers.gamma.app/guides/generate-api-parameters-explained.md`, `/reference/image-model-accepted-values.md`, `/reference/output-language-accepted-values.md`, `/guides/header-and-footer-formatting.md` |
| Gary packet + registry | our code | `app/specialists/gary/_act.py` (`GAMMA_SETTING_KEYS`, enums, `_instructions_for_variant`, packet builders), `app/specialists/gary/styleguide_library.py` (`RESOLVED_API_KEYS`, resolver), `scripts/utilities/validate_gamma_style_guides.py`, the SSOT schema |
| Drift detection | Leg-E doc audit | `scripts/utilities/audit_gamma_docs.py` + `skills/gamma-api-mastery/references/gamma-doc-audit-manifest.yaml` (already covers image-model + amount; **extend to the full surface — see §5**) |

---

## 1. Master matrix — Text content controls

| UI control (label · values) | API field · accepted values | UI→API map | Gary packet (code ref) | Owner (set/edit) | Consumer | Runtime-bound |
|---|---|---|---|---|---|---|
| **Text mode** · Generate / Condense / Preserve | `textMode` · `generate` \| `condense` \| `preserve` (default `generate`) | label≈value (aligned) | `textMode` (conditional; dropped if default/generate) — `_act.py:967` | CD-registry `text_content.mode`; per-variant override | Gamma API | ✅ |
| **Amount of text** · Minimal / Concise / Detailed / Extensive | `textOptions.amount` · `brief` \| `medium` \| `detailed` \| `extensive` (default `medium`) | ⚠️ **UI≠API**: Minimal→`brief`, Concise→`medium`, Detailed→`detailed`, Extensive→`extensive` | `textOptions.amount` (dropped if default) — `_act.py:609-616,970` | CD-registry `text_content.amount`; per-variant override | Gamma API | ✅ |
| **Output language** · language names | `textOptions.language` · 73 ISO codes (`en`,`en-gb`,`es-419`,`pt-br`,`ja`,…) default `en` | ⚠️ UI names → API locale codes | `textOptions.language` — `_act.py:613,621` | CD-registry `text_content.language` | Gamma API | ✅ |
| **Tone** · free text (1–500) | `textOptions.tone` · free text | passthrough | `textOptions.tone` (generate only) — `_act.py:611,617` | CD-registry `text_content.tone` | Gamma API | ✅ |
| **Audience** · free text (1–500) | `textOptions.audience` · free text | passthrough | `textOptions.audience` — `_act.py:612,619` | CD-registry `text_content.audience` | Gamma API | ✅ |
| **Additional instructions** · free text (1–5000) | `additionalInstructions` · free text | passthrough (composite) | `additionalInstructions` — `_act.py:672-709` (see §4) | **composite** — CD-registry style register + orchestrator per-deck + Gary card rule + keywords | Gamma API | ✅ |
| **Content / card split** · Automatically / By dividers | `cardSplit` · `auto` \| `inputTextBreaks` (default `auto`) | label≠value | **Gary-HARDCODED** `"inputTextBreaks"` — `_act.py:956` | Gary-hardcoded (no registry owner) | Gamma API | ✅ |
| **Number of cards** · 1–60 (75 Ultra) | `numCards` · int (default 10; honored only when `cardSplit=auto`) | — | **Gary-HARDCODED** `len(slides)` — `_act.py:946` | Gary-hardcoded (no registry owner) | Gamma API | ✅ |

## 2. Master matrix — Visuals controls

| UI control (label · values) | API field · accepted values | UI→API map | Gary packet (code ref) | Owner | Consumer | Runtime |
|---|---|---|---|---|---|---|
| **Image source** · AI images / Stock (Pexels) / GIF (Giphy) / Web / Pictographic / None | `imageOptions.source` · `aiGenerated`,`pictographic`,`pexels`,`giphy`,`webAllImages`,`webFreeToUse`,`webFreeToUseCommercially`,`themeAccent`,`placeholder`,`noImages` (default `aiGenerated`) | ⚠️ friendly UI labels → API enums | `imageOptions.source` — `_act.py:630,632` | CD-registry `visuals.image_source` | Gamma API | ✅ |
| **Image choices / Art style** · category chips + named style cards (see scratchpad-observed vocabulary below) | `imageOptions.style` · **free text** (1–5000) — *no documented `stylePreset` enum* | ⚠️ **DISCREPANCY** (see §6): live UI exposes many named style labels; docs expose only free-text `style` | Gary sends `imageOptions.stylePreset` (from `visuals.style_preset`) **and** `imageOptions.style` (from `visuals.custom_style`) — `_act.py:628,636-647` | CD-registry `visuals.style_preset` / `visuals.custom_style` | Gamma API | ✅ |
| **AI image model** · marketing names ("Nano Banana Pro"…) | `imageOptions.model` · 50+ technical IDs across Standard/Advanced/Premium/Ultra tiers | ⚠️ UI marketing name → API technical ID | `imageOptions.model` (dropped if auto) — `_act.py:629,634` | CD-registry `visuals.image_model` | Gamma API | ✅ |

Image-model authority = `reference/image-model-accepted-values.md`, **already drift-audited** (`audit_gamma_docs.py` item `enum-parity-image-model` ↔ `_act.py:IMAGE_MODEL_VALUES`). Do not duplicate the 50-model list here — cite the audit.

Scratchpad-observed Image choices vocabulary (`scratchpad/Recording 2026-07-02 230921.mp4`, sampled 2026-07-03):

- Category chips: `All`, `Scenic`, `Realistic`, `Minimal`, `Playful`, `Bold`, `Abstract`.
- Named style cards observed: `Digital Collage`, `Isometric`, `Gouache Paint`, `Spot Color`, `Doodle`, `Bold Poster`, `Continuous Line Art`, `Watercolor`, `Collage`, `Bauhaus`, `Paper Cutout`, `Felt`, `3D`, `Neon Glow`, `Photo`, `Cinematic`, `Lifestyle`, `Editorial`, `Still life`, `Waves`, `Liquid glass`, `Mesh`, `Paint swirl`.
- Evidence status: observed from a UI recording, not yet proven exhaustive and not yet mapped to a stable API enum. Treat these labels as Gamma UI vocabulary until live packet proof establishes the exact `stylePreset`/`style` behavior.

## 3. Master matrix — Page/card, format, export, theme

| UI control (label · values) | API field · accepted values | Gary packet | Owner | Consumer | Runtime |
|---|---|---|---|---|---|
| **Card size** · Fluid / 16:9 / 4:3 (pres); Pageless/Letter/A4 (doc); 1:1/4:5/9:16 (social) | `cardOptions.dimensions` · `fluid`,`16x9`,`4x3`,`pageless`,`letter`,`a4`,`1x1`,`4x5`,`9x16` | `cardOptions.dimensions` — `_act.py:651,981` | CD-registry `page_settings.card_options.dimensions` | Gamma API | ✅ (**the only runtime-bound page-setup field**) |
| **Card headers & footers** · 6 positions, text/image/cardNumber (Pro) | `cardOptions.headerFooter` · positions + element types | — **NOT emitted** | CD-registry `page_settings.ui_only_reference.card_headers_footers` | **NONE** (API supports it; Gary doesn't wire it) | ❌ dropped |
| **Theme** · gallery | `themeId` · workspace theme ID | `themeId` — `_act.py:947` | CD-registry `theme.id`; per-variant override | Gamma API | ✅ |
| **Format** · Presentation / Document / Webpage / Social | `format` · `presentation`,`document`,`webpage`,`social` (default `presentation`) | — not sent (defaults to presentation) | — | Gamma API default | ❌ not wired |
| **Export as** · PDF / PPTX / PNG | `exportAs` · `pdf`,`pptx`,`png` | **Gary-HARDCODED** `"png"` — `_act.py:962,854` | Gary-hardcoded | Gamma API | ✅ (registry `page_settings.export.export_as` was **dropped** session-08 — Gary hardcodes png) |
| **Content alignment** · Top/Center/Bottom | — *no API field* | — | CD-registry `content_alignment` | **NONE (UI-only)** | ❌ |
| **Card width** · S / M / L *(screenshot-observed letter sizes — crossroads = `L`; the help-doc "Narrow/Medium/Wide" wording is stale vs the live UI)* | — *no API field* | — | CD-registry `card_width` | **NONE (UI-only)** | ❌ |
| **Font size** · Small/Medium/Large | — *no API field* | — | CD-registry `font_size` | **NONE (UI-only)** | ❌ |
| **Show card backdrops** · On/Off | — *no API field* | — | CD-registry `show_card_backdrops` | **NONE (UI-only)** | ❌ |
| **Animations** · On/Off | — *no API field* | — | CD-registry `animations` | **NONE (UI-only)** | ❌ |
| **Background / Accent-image layout / Card color / Full-bleed** | — *no API field* | — | — | **NONE (UI/editor-only)** | ❌ |
| **Card design mode** · Classic / Studio | — *no Generate-API enum* | routed by `production_mode`; Studio reached via `generate_from_template` lock-and-replace | CD-registry `production_mode` | Gary fork (`_act.py:920`) | ✅ (routing) |

## 4. `additionalInstructions` — the composite channel

Built by concatenation in `_instructions_for_variant` (`_act.py:672-709`); **complement-not-overwrite** (separate dict keys, style-first order — source detail is never dropped):

| # | Part | Source | Owner | file:line |
|---|---|---|---|---|
| 1 | style prose register | `settings["additional_instructions"]` ← registry `prompt_configuration.additional_instructions` | **CD-registry** (the new first-class field) | `_act.py:686` · resolver `:245` |
| 2 | per-deck source-derived instructions | `payload["additional_instructions"]` | **Orchestrator** — `package_builders.py:166` (CD directive) + `enrichment_consumption.py` (source enrichment) — *protected conveyance* | `_act.py:691` |
| 3 | card-structure rule | literal | **Gary-hardcoded (no owner)** | `_act.py:692-694` |
| 4 | keyword imagery prose ("Emphasize this imagery: …") | `settings["keywords"]` ← registry `visuals.keywords` | CD-registry | `_act.py:703-707` |
| 5 | `Variant {variant}.` | literal | Gary-hardcoded | `_act.py:708` |

## 5. Gap register (what a "faithful style" can and cannot control)

**A. UI controls with NO API field — a style CANNOT set these via the Generate API** (editor-only): content alignment, card width, font size, show-backdrops, animations, background, accent-image layout, card color, full-bleed. Any registry field carrying these is documentation-of-intent, not runtime behavior.

> **NOT in this list: Classic vs Studio.** It is not a UI-only toggle and needs no Playwright/UI automation (that approach is retired). `production_mode` routes which **API method** Gary calls: `api` → `POST /generations` (Classic), `studio` → **create-from-template** (`generate_from_template`, Studio image-cards via lock-and-replace on a Studio template `gamma_id`). Both are fully API-driven; the plain `/generations` endpoint simply has no `cardDesignMode` parameter because Studio lives behind a different endpoint.

**B. Registry fields authored but consumed by NO ONE (decorative — now grouped under an explicit label, NOT pruned):** `page_settings.ui_only_reference.{card_width, content_alignment, font_size, show_card_backdrops, animations, card_headers_footers}`, `studio_prompt_lock.{wrapper_id,behavior,guard}`, `coherence.*`, `provenance.*`. (`presentation.*` is picker-display-only by design — not decorative.)

> **Session-08 formalization (2026-07-03):** these decorative UI-only page-setup fields were regrouped OUT of `page_settings.card_options` into a dedicated `page_settings.ui_only_reference` block so they no longer read as active runtime settings. The ONLY runtime-bound page field is `page_settings.card_options.dimensions`. `page_settings.export.export_as` was **dropped** (Gary hardcodes `exportAs=png` — part C). `card_headers_footers` DOES have an API field (`cardOptions.headerFooter`, part D) but Gary does not wire it. A future validator/consumer following this map should read the decorative controls at `ui_only_reference`, and `dimensions` at `card_options`.

**C. API fields Gary hardcodes (no registry owner):** `cardSplit=inputTextBreaks`, `exportAs=png`, `numCards=len(slides)`, additionalInstructions parts 3 & 5, the `# title` + `\n---\n` input structure, the Studio lock wrapper + aspect guard.

**D. API fields Gary does NOT wire (available, unused):** `format`, `cardOptions.headerFooter`, `sharingOptions.*`, `folderIds`, `title`, `pages`, and the non-`aiGenerated` image sources.

## 5b. Registry vocabulary-normalization status (UI vocab ↔ API)

**Principle (operator, 2026-07-03):** the registry stores Gamma **UI vocabulary** (what the operator sees in the prompt editor); Gary translates to the API value at packet-build. **Ordering rule:** a field's registry value may be normalized to UI vocab ONLY AFTER its translator exists — normalizing ahead of the translator ships a UI label straight to the API and breaks the render.

| Field | Registry vocab today | Translator | Status / next |
|---|---|---|---|
| `text_content.amount` | **UI** (`minimal`/`concise`…) | ✅ `TEXT_AMOUNT_UI_TO_API` → `_normalized_gamma_settings` + `_text_options_for_variant` | **DONE** |
| `visuals.image_source` | API (`aiGenerated`) | — none | **NEXT** — small closed set (`AI images`→`aiGenerated`, `Stock photos`→`pexels`, …). Build translator, then normalize registry values. |
| `visuals.image_model` | API (`gpt-image-2-mini`) | — none | **FOLLOW-ON** — 50+ UI marketing names ↔ API IDs (authority `image-model-accepted-values.md`); bigger map. |
| `visuals.style_preset` | API (`illustration`) | — none | candidate (UI Image choices / Art style labels) — scratchpad shows a richer UI vocabulary than the old chip list; resolve §6 `stylePreset` discrepancy before normalizing registry values. |
| `text_content.language` | API code (`en`) | — none | candidate (UI language names ↔ codes). |
| `card_options.dimensions` | mixed (`fluid`/`16x9`) | — none (UI ≈ API) | low priority — UI `16:9` vs API `16x9` is cosmetic. |

**Crossroads decision (this review):** leave `image_source`/`image_model` **API-facing for now** — do NOT store `AI images` / `GPT Image 2 Mini` in the registry until their translators land, or crossroads' next render breaks. Sequence: extend the layer to `image_source`, then `image_model`, then re-normalize crossroads' stored values. Tracked as tasks.

## 6. ⚠️ Art-style field — `imageOptions.style` (canonical) vs `stylePreset` (legacy)

**Canonical field (operator, 2026-07-03):** Gamma's DOCUMENTED field for the art-style control is free-text **`imageOptions.style`**. `stylePreset` is **not documented** — Gary sends `imageOptions.stylePreset` (from `visuals.style_preset`, e.g. `illustration`) and wire receipts confirm it renders, but that is tolerated-but-undocumented legacy behavior. The current UI compiles its named "Image choices" (category chips + many named style cards — §2) into the free-text `style` field.

So `illustration` — and every named style (`Watercolor`, `Editorial`, `Isometric`, …) — is naturally a **value of `style`**, not a separate enum. Our `IMAGE_STYLE_PRESET_VALUES` 6-value allowlist (`photorealistic/illustration/abstract/3D/lineArt/custom`) is a legacy artifact.

> **✅ PROVEN for named styles (2026-07-03, session-09).** The `hil-2026-apc-crossroads-digital-collage` style ships `style_preset: custom` + `custom_style: "Digital Collage"`, which the resolver/packet-builder lands on the wire as **`imageOptions.style: "Digital Collage"`** (wire receipt captured), and a live briefed render produced exactly the expected mixed-media collage (operator-approved, promoted permanent). So a NAMED, non-preset art style DOES ride the free-text `style` channel end-to-end. **Reliability requirement (matrix §8):** the art-style channel sets the *register* (collage vs illustration vs line-art), but clean on-message *imagery* still needs the per-slide `Illustration:` content brief — un-briefed slides photo-grid and garble signage regardless of the style value. **Still open:** whether a *legacy `stylePreset` value* (e.g. `illustration`) renders **equally** through `style` vs `stylePreset` — that equivalence gates the crossroads-A migration off `style_preset`, so crossroads-A stays on the proven `style_preset: illustration` until a same-content A/B proves parity.

**Plan — unify on `style` (one live test gates it):** confirm that `illustration` (and one named style, e.g. `Watercolor`) render as well via free-text `style` as via `stylePreset`. If yes → collapse the registry's art-style onto a single `style` field holding any UI style name (retire the separate `style_preset` enum path + allowlist; matches "registry stores UI vocab" with no translation table needed — the UI style name IS the value). If the curated preset renders more consistently for its supported values, keep `stylePreset` for those and use `style` for the rest. **Ordering rule holds:** keep crossroads on the proven `style_preset: illustration` until the test proves the `style`-field path renders equally, then migrate. Add the resolved `stylePreset`/`style` behavior to the doc-audit manifest.

## 7. How the tooling draws on this matrix (implementation contract)

1. **UI→API translation (Gary/resolver):** the registry holds UI vocabulary; the resolver/packet-builder maps to API values per the §1–3 maps *before* the API call (e.g. `amount: minimal`→`brief`). One mapping table, cited here, referenced by code — not duplicated.
2. **Validator (`validate_gamma_style_guides.py`):** accepts the **UI vocabulary** and validates it against the UI-side value sets in this matrix (whose authority is the Gamma docs), instead of the raw API enum. A value the operator can pick in Gamma's UI must validate.
3. **Drift audit (`audit_gamma_docs.py` + manifest):** extend the doc-audit manifest beyond image-model/amount to every enum in §1–3 (`textMode`, `imageOptions.source`, `cardOptions.dimensions`, `textOptions.language`, `cardSplit`) so a Gamma-side change fails the audit.
4. **Tests:** reference the matrix's value sets / the same authorities rather than re-hardcoding enums.

Follow-on implementation tasks are tracked in the harmonization arc; this document is their authority.

## 8. Style-development lessons (procedures)

Binding lessons for authoring + validating any new style. Future style-development runs
(green-light party → author → render-verify) must honor these.

1. **Image quality rides in the slide CONTENT, not the style.** A clean, on-message,
   correctly-labeled illustration comes from a per-slide **`Illustration: …` brief** baked
   into the card content (the source design-notes → the protected source-detail→Gamma
   conveyance). The style config (theme, model, preset, `additional_instructions`) does
   **not** supply composition — it sets register/typography/palette. Proven 2026-07-03:
   the *identical* crossroads config + model (`gpt-image-2-mini`) + `additional_instructions`
   produced CJK-in-image garbage on an un-briefed slide and a clean, English-labeled,
   on-message crossroads illustration on the same slide once an `Illustration:` brief was
   present in the content (evidence `crossroads-goldstandard-20260703T041136Z` vs
   `crossroads-render-20260703T034348Z`).
2. **Instruction-neutral corpora cannot validate image behavior.** `style-test-strip-v1`
   is deliberately instruction-neutral (so the *style* is the only variable) — which makes
   it a great test of typography/layout/palette but a **misleading** test of imagery: with
   no `Illustration:` brief, the image model falls back to its raw training default
   (`gpt-image-2-mini` → Japanese/Chinese in-image text). To validate a style's imagery,
   render at least one **briefed** slide (content carrying an `Illustration:` note), as the
   gold standard does.
3. **Don't misattribute a content-gap to the style.** Before "fixing" a style config over a
   bad image, check whether the slide content carried an image brief. A missing brief is a
   content/pipeline issue, not a style defect.
4. **Model bias is real but guided-away, not swapped-away.** `gpt-image-2-mini` has a
   foreign-text default; it renders beautifully when the content briefs the scene (and, if
   ever needed for thin-brief production slides, a style-level in-image-text-English guard in
   `additional_instructions` is the belt-and-suspenders backstop — optional, not required
   when briefs are present).
