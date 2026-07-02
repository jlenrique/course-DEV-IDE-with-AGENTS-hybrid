# Gamma API Parameter Catalog

Complete parameter reference for Gary's Gamma API operations. Sourced from [Gamma Developer Docs](https://developers.gamma.app) via Ref MCP doc refresh (2026-03-27).

## Endpoint: POST /v1.0/generations (Text Generation)

### Required Parameters

#### `inputText` (string, required)
Content used to generate the gamma. Supports text, structured markdown, and inline image URLs.
- Token limit: ~100,000 tokens (~400,000 chars)
- Use `\n---\n` to control card breaks (with `cardSplit: inputTextBreaks`)
- Image URLs can be embedded inline where they should appear
- **Medical ed guidance**: For faithful reproduction, provide exact final text. For lecture generation, provide outlines or notes.

#### `textMode` (string, required)
Controls how `inputText` is modified.
- `generate` — Gamma rewrites and expands. Best for brief outlines → full slides.
- `condense` — Gamma summarizes. Best for long notes → concise slides.
- `preserve` — Gamma retains exact text, may add structural headings. For zero modifications, add `additionalInstructions: "Do not modify the provided text in any way."`
- **Medical ed guidance**: Use `preserve` for finalized SME content. Use `generate` for outline-to-slides. Use `condense` for lengthy notes.
- **Known quirk**: Even in preserve mode, Gamma may add decorative elements, subtitles, or diagrams. Constrain via `additionalInstructions`.

### Optional Parameters

#### `format` (string, default: `presentation`)
- `presentation` | `document` | `social` | `webpage`
- **Medical ed guidance**: Always `presentation` for slides. Use `document` only for long-form handouts.

#### `themeId` (string, default: workspace default)
Theme ID from `GET /v1.0/themes`. Controls colors, fonts, visual style.
- Copy from Gamma app or list via API.
- **Medical ed guidance**: Use JCPH-branded theme if registered. Professional medical aesthetic, not consumer health.

#### `numCards` (integer, default: 10)
- Pro/Teams/Business: 1-60. Ultra: 1-75.
- **Medical ed guidance**: `1` for single-slide exemplars. `auto` for lecture decks. Pair with `textOptions.amount` to control density.

#### `cardSplit` (string, default: `auto`)
- `auto` — Gamma divides content by `numCards`.
- `inputTextBreaks` — Gamma splits on `\n---\n` in input (ignores `numCards`).
- **Medical ed guidance**: Use `inputTextBreaks` for L5+ multi-slide decks where you control the narrative flow.

#### `additionalInstructions` (string, 1-5000 chars)
Free-text guidance for layout, tone, structure, visual style.
- **Medical ed guidance**: Critical for embellishment control and layout specification.
- **Effective constraint phrasings**:
  - Strict: `"Output ONLY the provided text. Do not add content, steps, or diagrams beyond what is given."`
  - Layout: `"Two-column parallel comparison layout"`, `"Three-column card layout with equal-width sections"`
  - Assessment: `"Interactive assessment layout. Question prompt prominent. Answer options clearly separated."`

#### `folderIds` (array of strings)
Folder IDs for organizing output in Gamma workspace.

#### `exportAs` (string)
- `pdf` | `pptx` | `png` — one format per request.
- Export URLs are signed, expire ~7 days. Download immediately.
- **Medical ed guidance**: Default to `png` for production — slides are visual assets for video production and course embedding. Use `pdf` for human review at checkpoint gates and woodshed comparison. Use `pptx` when downstream editing is planned.

### textOptions (object)

#### `textOptions.amount` (string, default: `medium`)
- `brief` | `medium` | `detailed` | `extensive`
- Only relevant when `textMode` is `generate` or `condense`.
- **Medical ed guidance**: `brief` + `numCards: 1` = focused impact slides. `medium` + `numCards: auto` = balanced lecture decks.

#### `textOptions.tone` (string, 1-500 chars)
- Only relevant when `textMode` is `generate`.
- **Medical ed guidance**: `"Professional medical education, clear and evidence-based"` or `"Clinical narrative, patient-centered"`

#### `textOptions.audience` (string, 1-500 chars)
- Only relevant when `textMode` is `generate`.
- **Medical ed guidance**: `"Practicing physicians and health sciences graduate students"`

#### `textOptions.language` (string, default: `en`)
- ISO language code. See Gamma docs for accepted values.

### imageOptions (object)

#### `imageOptions.source` (string, default: `aiGenerated`)
| Value | Use Case |
|-------|----------|
| `aiGenerated` | Custom AI images (can specify model and style) |
| `pexels` | Stock photography |
| `webFreeToUse` | Web images licensed for personal use |
| `webFreeToUseCommercially` | Web images for commercial use |
| `themeAccent` | Accent images from selected theme |
| `placeholder` | Empty placeholders for manual addition |
| `noImages` | No images at all |
| `pictographic` | Pictographic illustrations |
| `giphy` | GIFs |
| `webAllImages` | All web images (licensing unknown) |

- **Medical ed guidance**: Use `noImages` for text-focused faithful reproduction. Use `pexels` for professional imagery. Never use `giphy` for medical education.

#### `imageOptions.model` (string, optional)
AI image model when source is `aiGenerated`. Full current list (as of 2026-03-27 API refresh; reconciled to strict doc-parity 2026-07-02 — removed qwen-image-fast / qwen-image / imagen-4-fast, no longer documented; refresh via `scripts/utilities/audit_gamma_docs.py`):

| Tier | Models |
|------|--------|
| **Standard** | `flux-2-klein`, `flux-kontext-fast`, `imagen-3-flash`, `luma-photon-flash-1`, `flux-2-pro`, `ideogram-v3-turbo`, `luma-photon-1`, `recraft-v4`, `leonardo-phoenix` |
| **Advanced** | `flux-2-flex`, `flux-2-max`, `flux-kontext-pro`, `ideogram-v3`, `imagen-4-pro`, `recraft-v3`, `gemini-3-pro-image`, `gemini-2.5-flash-image`, `gpt-image-1-medium`, `dall-e-3` |
| **Premium** | `gemini-3.1-flash-image-mini`, `recraft-v3-svg`, `recraft-v4-svg`, `ideogram-v3-quality`, `gemini-3.1-flash-image`, `gemini-3-pro-image-hd`, `gemini-3.1-flash-image-hd` |
| **Ultra** | `imagen-4-ultra`, `gpt-image-1-high`, `recraft-v4-pro` |
| **Unclassified — never rendered, tier TBD** | added at the 2026-07-02 doc-parity reconciliation; per-model provenance table below |

**Unclassified — never rendered, tier TBD** (documented accepted values added 2026-07-02; NO production render has exercised any of these yet — tier placement above is deliberately deferred until a real render. The "Documented tier / Credits" columns cite Gamma's own docs verbatim from <https://developers.gamma.app/reference/image-model-accepted-values.md>, fetched 2026-07-02T05:43:58Z; they are Gamma's claims, not our vetting. The machine-readable provenance marking clears ONLY on a real production render — another doc read does not clear it. Phase-2's first styleguide binding one of these models is the designated live availability witness.):

| Model | Documented tier (Gamma docs) | Documented Credits/Image | Provenance |
|-------|------------------------------|--------------------------|------------|
| `flux-1-quick` | Standard models | 2 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-1-mini-low` | Standard models | 2 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-2-mini` | Standard models | 5 | `provenance: documented-tier, unverified-in-production` |
| `flux-1-pro` | Standard models | 8 | `provenance: documented-tier, unverified-in-production` |
| `imagen-3-pro` | Standard models | 8 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-1-mini-medium` | Standard models | 8 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-1-mini-high` | Advanced models | 20 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-2` | Advanced models | 20 | `provenance: documented-tier, unverified-in-production` |
| `flux-1-ultra` | Advanced models | 30 | `provenance: documented-tier, unverified-in-production` |
| `flux-kontext-max` | Premium models | 40 | `provenance: documented-tier, unverified-in-production` |
| `gpt-image-2-hd` | Ultra models | 115 | `provenance: documented-tier, unverified-in-production` |

**Medical ed guidance by use case:**
- **Style-reference matching (Approach B)**: `flux-kontext-pro` — designed for style-reference controlled generation; best for "make it look like this exemplar"
- **Text accuracy in images**: `ideogram-v3` / `ideogram-v3-quality` — specifically strong at rendering readable text; use for text-bearing concept slides
- **Illustration/lineart**: `recraft-v3`, `recraft-v4`, `gemini-3.1-flash-image-mini` (Nano Banana 2 Mini) — proven for editorial medical illustration style
- **Photorealistic**: `flux-2-pro`, `luma-photon-1`
- **High quality / production**: `gpt-image-1-high`, `recraft-v4-pro`, `imagen-4-ultra`
- **Fast/cheap iteration**: `flux-2-klein`, `flux-kontext-fast`, `ideogram-v3-turbo`

#### `imageOptions.stylePreset` (string, optional) — **added Feb 27, 2026**
Named art style tile. **When set to a named value, `imageOptions.style` is IGNORED.**

| Value | Gamma UI tile | Use |
|-------|---------------|-----|
| `photorealistic` | Photo | Clinical photography aesthetic |
| `illustration` | Illustration | Diagrams, infographics, editorial art |
| `abstract` | Abstract | Conceptual, atmospheric backgrounds |
| `3D` | 3D | Volumetric, dimensional graphics |
| `lineArt` | (line art tile) | Clean line-drawing style |
| `custom` | Custom (auto-set on reference upload) | Free-form style via `style` prompt |

- **Approach A**: Set `stylePreset` to a named value. `style` field unused by API.
- **Approach B**: Set `stylePreset: custom`. `style` field IS the prompt (1-500 chars).
- **Reference image upload** (UI-only, not in API): When a user uploads a PNG in the Gamma UI "Add style references" area, the tile switches to `custom` and Gamma generates a style embedding from the image. **Not yet exposed as an API parameter.** Use `referenceImagePath` in the style preset as a design-intent record — Gary/Marcus reads the image to craft a better `style` prompt.
- **Medical ed guidance**: Use `illustration` for most HIL 2026 content (Approach A). Use `custom` + `flux-kontext-pro` for Approach B style-matching experiments.

#### `imageOptions.style` (string, 1-500 chars, optional)
- **Only respected when `imageOptions.stylePreset` is `custom` or when `stylePreset` is not set.**
- When `stylePreset` is a named tile, this field is ignored by the API.
- **Approach B prompt guidance**: Be specific about line weight, fill, shading, color palette, and medium. "Line drawing, clean black ink lines on white, minimal fill, editorial medical infographic, no shading, no photorealism, vector aesthetic, flat-color accents only" performs better than generic descriptions.
- **Style preset integration**: See `style-preset-library.md` for how keywords are appended at flatten time.

### cardOptions (object)

#### `cardOptions.dimensions` (string)
- Presentation: `fluid` (default) | `16x9` | `4x3`
- Document: `fluid` (default) | `pageless` | `letter` | `a4`
- Social: `1x1` | `4x5` (default) | `9x16`
- **Medical ed guidance**: `16x9` for standard lecture presentations. `fluid` for content-first layouts.

#### `cardOptions.headerFooter` (object)
Positions: `topLeft`, `topRight`, `topCenter`, `bottomLeft`, `bottomRight`, `bottomCenter`
Types: `text` (value required), `image` (source: `themeLogo` | `custom`), `cardNumber`
Options: `hideFromFirstCard`, `hideFromLastCard`

### sharingOptions (object)

#### `sharingOptions.workspaceAccess` (string)
`noAccess` | `view` | `comment` | `edit` | `fullAccess`

#### `sharingOptions.externalAccess` (string)
`noAccess` | `view` | `comment` | `edit`

#### `sharingOptions.emailOptions` (object)
`recipients` (array of emails), `access` (string)

---

## Endpoint: POST /v1.0/generations/from-template

Template-based generation preserves an existing layout while swapping content.

### Required Parameters

#### `gammaId` (string, required)
The ID of the template gamma. Template must contain exactly one page. Copy from the Gamma app.

#### `prompt` (string, required)
Text content and instructions for how to use the content with the template.
- Token limit: ~100,000 minus template tokens.
- Can include image URLs inline.
- **Medical ed guidance**: Describe what content to swap in. E.g., `"Replace the deep sea content with: [clinical case study text]"`

### Optional Parameters
- `themeId`, `folderIds`, `exportAs`, `sharingOptions` — same as text generation.
- `imageOptions` — new images match the template's image source by default. Override with `imageOptions.model` and `imageOptions.style` if source is `aiGenerated`.

---

## Endpoint: GET /v1.0/generations/{id}

Poll for generation status. Returns `status`: `pending` | `completed` | `failed`.
On completion: `gammaUrl`, `exportUrl` (if `exportAs` was set), credit usage.

## Endpoint: GET /v1.0/themes

List workspace themes. Returns `id`, `name`, `type`, `colorKeywords`, `toneKeywords`.

## Endpoint: GET /v1.0/folders

List workspace folders. Returns `id`, `name`.
