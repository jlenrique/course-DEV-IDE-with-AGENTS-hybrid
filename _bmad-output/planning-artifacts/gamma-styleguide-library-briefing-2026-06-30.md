# Briefing — Gamma visual control today & the CD-owned Style-Guide Library (2026-06-30)

**Driver (operator):** more reliable control over the look/feel/attributes (incl. size & proportions) of Gamma screens. Build a robust **style-guide library** the **CD agent owns and evolves**, specifying a configured set across every "Gamma screen production influencer": selected **template**, selected **theme**, the **API parameters** Gary can pass (+ ranges), and **other Gamma settings** (incl. API-only "page settings" like aspect ratio) not yet codified. First step: *how do we control/set these now?*

**Guardrail check:** PRODUCT-VALID. This controls what the **Marcus-SPOC runtime** exports for *any* real deck, not a proofing run. ([[feedback_spoc_is_goal_not_concierge_proofing_runs]])

---

## 1. How we control Gamma config TODAY (the honest map)

**Two live dispatch paths** (Gary routes on payload shape — `app/specialists/gary/_act.py:904`):
- **Production variant path** `generate_gamma_variants` (`_act.py:699`) → Classic `/generations` (`GammaClient.generate`) **or** Studio `from-template` (`GammaClient.generate_from_template`). HTTP client: `scripts/api_clients/gamma_client.py`.
- **Legacy style-preset path** `execute_generation` (`skills/gamma-api-mastery/scripts/gamma_operations.py:718`) — reachable only with a `directive_path` + no slides; owns `merge_parameters`, double-dispatch, and `gamma-style-presets.yaml`.

**Where each influencer is set:**
- **Template (Studio):** `studio_template_id: g_nv5q4da69qiiu8q` — currently in a *run artifact* `runs/studio-trial/studio-b-gamma-settings.yaml:7`; applied **per-slide** in the from-template path (`_act.py:655,670`) with a frozen lock-wrapper + an aspect-ratio guard (`_STUDIO_MIN_ASPECT_RATIO=1.4`, `_act.py:133`). Used only for a variant explicitly set `production_mode: studio`.
- **Theme:** the two production themes live in `DEFAULT_VARIANT_PAIR` (`_act.py:134-203`) — **A `njim9kuhfnljvaa`** (2026 HIL APC (Nejal), illustration) / **B `e8tz1vxb9v1urqp`** (Blueprint Editorial, lineArt). That block is explicitly labeled **"SMOKE FIXTURE, not a product default."** The same theme is *also* duplicated in `state/config/gamma-style-presets.yaml` and pointed at by an **opaque `theme_selection` run-constant**. (Files spell it "Nejal"; "Tejal" is the corpus name for the same family.)
- **API params:** the allowed knob set is frozen as `GAMMA_SETTING_KEYS` (`_act.py:84`); the *full passable surface* is catalogued in `skills/gamma-api-mastery/references/parameter-catalog.md` (documentation of what's possible, not what's chosen).
- **Selection flow:** config default (`DEFAULT_VARIANT_PAIR`) → optional CD `creative-directive` `gamma_settings` array (`creative-directive.schema.yaml:89` — the *field exists* but the deterministic builder `build_gary_briefs` **never populates it**) → operator `trial start --gamma-settings-file` / **G2B gate** override → final per-slide pick at Storyboard A / **G2C**.

**The CD agent (Dan) is structurally BLIND to Gamma visuals.** Dan owns only `experience_profile` + `slide_mode_proportions` + the 11 `narration_profile_controls` + `creative_rationale` (`skills/bmad-agent-cd/SKILL.md`). A full grep of the CD skill for gamma/theme/stylePreset/dimensions/template returns **zero** substantive hits. The directive→Gary *visual* link is only a **provenance string** (`creative_directive_id` on `gary-theme-resolution`), not an authored visual payload.

**Config is scattered across FIVE disconnected stores, none CD-owned:**
| Visual concern | Where today | CD-owned? |
|---|---|---|
| Brand color/type/accessibility (design language) | `resources/style-bible/master-style-bible.md` (no Gamma params — Gary must *manually* translate hex/font into `additionalInstructions`) | No (manual) |
| Gamma stubs + template registry home | `state/config/style_guide.yaml → tool_parameters.gamma` (**empty stubs**) | No |
| The only real "single configured set" | `state/config/gamma-style-presets.yaml` (theme_id + imageOptions + cardOptions.dimensions + numCards + additionalInstructions) | No (user/Gary) |
| Selected theme (opaque) | run-constants `theme_selection` / `theme_paramset_key` | No (Marcus) |
| Per-run resolved theme | `gary-theme-resolution.json` (hand-shaped) | No (Marcus writer) |
| **Narrative frame** (proportions, register) | creative-directive + `experience-profiles.yaml` | **Yes (CD)** |

**The repo already names the fix:** `_bmad-output/implementation-artifacts/variant-demo/variant-demo-gamma-settings.yaml:2-3` calls itself *"the interim stand-in for the **future Marcus-SPOC CD-curated treatment pick-list**."* Your wish-list IS that pick-list.

---

## 2. Prompt-page field inventory (from your two screenshots → API → our config)

The Gamma **Prompt editor** left "Settings" panel — every field, with the value set observed, mapped to the API param and our `gamma_settings` key. (Screenshot A = Standard/Preserve; Screenshot B = Variant-B/Generate/Studio, which reveals the amount/audience/tone fields hidden in Preserve mode.)

| Prompt-page field | UI values (observed) | Gamma API param | our `gamma_settings` key | set in a DEFAULT prod run? |
|---|---|---|---|---|
| **Text content** mode | Generate · Condense · **Preserve** | `textMode` | `text_mode` | only if `gamma_settings` present |
| **Amount** (Generate only) | Just vibes · **Minimal text** · A little context · Plenty of text | `textOptions.amount` (brief/medium/detailed/extensive) | `amount`/`density` | conditional |
| **Write for…** (audience) | free text ("Faculty & IDs familiar with Canvas…") | `textOptions.audience` | `audience` | conditional |
| **Tone** | free text ("Clear, professional, engaging…") | `textOptions.tone` | `tone` | conditional |
| **Output language** | English (US) | `textOptions.language` | `language` (en only) | conditional |
| **Theme** | 2026 HIL APC (Nejal) A / B tiles + *View more* | `themeId` | `theme` | YES (via default pair, gated) |
| **Image source** | AI images · (Pexels/No images…) | `imageOptions.source` | `image_source` | conditional |
| **AI image model** | Auto-select · 30+ models (per-image credit shown) | `imageOptions.model` | `image_model` | conditional |
| **Image art style** | Suggested/Photo/Illustration/Abstract/3D/Line art/Custom + tiles | `imageOptions.stylePreset` (+`style`) | `image_style_preset` / `image_style` | conditional |
| **Add reference** (image) | upload a reference image | *(UI-only; not a live API field)* | — | NO (UI-only) |
| **Add extra keywords** | chips: minimalist · bold · flat · geometric | *(folded into `additionalInstructions`)* | `keywords` | conditional → instructions |
| **Format** type | **Presentation** · Webpage · Document · Social | `format` | *(no key)* | NO — always defaults `presentation` |
| **Format variant** | Traditional (dropdown) | `formatVariant` | — | NO (UI-only / not a generate kwarg) |
| **Card design mode** | **Classic** · **Studio** | path selector | `production_mode` (api/studio) | YES (per variant) |
| **Content** layout | Freeform · **Card-by-card** | `cardSplit` (auto / inputTextBreaks) | *(hard-coded `inputTextBreaks`)* | YES (hard-coded) |
| (per-card text) | the slide prompts | `inputText` | *(from builder `slides`)* | YES |
| **Num cards** stepper | "10 cards" | `numCards` (1–60 Pro / 1–75 Ultra) | *(= len(slides))* | YES |
| **Additional instructions** | the right panel | `additionalInstructions` | *(from builder)* | YES |

**Studio caveat:** the `from-template` endpoint exposes ONLY `gammaId`, `prompt`, `exportAs`, (`themeId`/`imageOptions`/`sharingOptions` available-unused). `textMode`/`textOptions`/`cardOptions`/`numCards` **do not exist** on the template endpoint — Studio look is governed by the template itself + the lock-wrapper.

---

## 3. "Page settings" — the API-only category (NOT on the prompt page)

Confirmed by both screenshots: **aspect ratio is NOT on the Prompt editor page.** It is a separate "page setting" reachable only via the API (or the generated deck's settings UI). This is exactly the category you flagged.

| Page setting (API-only) | Values | API param | our key | set in a DEFAULT prod run? |
|---|---|---|---|---|
| **Aspect ratio / dimensions** | fluid · **16x9** · 4x3 · 9x16 · 1x1 · 4x5 · pageless/letter/a4 | `cardOptions.dimensions` | `dimensions` | ⚠️ **NO by default — the cropping bug** |
| Header / footer | on/off | `cardOptions.headerFooter` | — | NO (never populated) |
| Sharing | workspace/external access | `sharingOptions` | — | NO |
| Folder | folder IDs | `folderIds` | — | NO |
| Export format | pdf/pptx/png | `exportAs` | *(hard-coded png)* | YES |

**⚠️ The aspect-ratio defect (root cause).** A `16x9` knob *exists* (`CARD_DIMENSION_VALUES`, `_act.py:81-83`; `DEFAULT_VARIANT_PAIR` sets `dimensions: 16x9`), BUT `cardOptions` is only built `if variant_settings is not None`, and `_normalized_gamma_settings` returns `[]` the moment a payload has no `gamma_settings` key — which the deterministic builder **never emits**. So a standard orchestrator run sends **NO `cardOptions` at all → Gamma falls back to its own (non-16:9) default → title-cropping in Descript.** 16:9 only takes effect today if the operator passes `--gamma-settings-file`. (This is Leg-4 finding (a); a one-line "default `cardOptions.dimensions=16x9` unconditionally" closes the *bug* — but not the larger goal.)

---

## 4. The ultimate goal — a CD-owned Style-Guide Library (target data structure)

**Operator-confirmed target (2026-06-30):** a data structure holding **at least 4 named styleguides** (some confirmed/promoted from what exists, some newly created). Each styleguide name specifies, exhaustively, **three addressable categories**:
1. **All API-addressable *prompt-configuration* fields** — every knob the Gamma API exposes for the prompt editor (the §2 table: text mode/amount/audience/tone/language, theme, image source/model/art-style/keywords, format/variant, card-design-mode, cardSplit, numCards, additionalInstructions).
2. **All API-addressable *page-settings* fields** — the API-only category not on the prompt page (the §3 table: **dimensions/aspect-ratio**, headerFooter, sharing, folder, exportAs).
3. **The foundational *Gamma Template or Gamma Theme*** a given run sits on (a `production_mode: studio` styleguide → a `studio_template_id`; a Classic styleguide → a `themeId`).

A **named style guide** = a single, schema-validated record across all three categories, **owned and evolved by the CD agent**, attached to the creative directive as a **first-class visual payload** (not a provenance string), and consumed by Marcus's theme-resolver + Gary's cascade — **replacing** the scattered five stores and retiring the "smoke fixture." The library holds ≥4 such records (e.g. the two existing production looks A/B promoted to real named guides, the Studio template look, plus ≥1 new — operator confirms the roster).

### 4a. Variant ↔ styleguide binding model (operator-confirmed 2026-06-30)

A styleguide name is **one complete look** — NOT a pair. A run that requests a per-slide **A/B comparison** (a "B" to compare against an "A" in the **Storyboard A picker**) **binds TWO named styleguides** for that run: one to **variant A**, one to **variant B**. This is the robust generalization of what `DEFAULT_VARIANT_PAIR` already began (A=Nejal/illustration, B=Blueprint/lineArt hard-coded inline) — except each variant now carries a `styleguide: <name>` **reference into the library** instead of inline smoke-fixture settings. Mechanics:
- The existing per-variant `gamma_settings` array (`variant_id: A|B`, `_act.py` / `creative-directive.schema.yaml:89`) gains a `styleguide` reference per variant; Gary resolves `name → full record` and applies that variant's prompt-config + page-settings + template/theme.
- The two existing production looks become the **first two named library entries** (A and B), promoted from "SMOKE FIXTURE" to real, independently-selectable named styleguides — plus ≥2 more to reach the ≥4 roster.
- **Provenance carries through the picker:** each per-slide render in the Storyboard A picker is tagged with the styleguide that produced it, so the operator's A-or-B pick records *which styleguide won* per slide (feeds the asset/fidelity ledger + future CD learning).
- A single-variant (non-comparison) run binds **one** styleguide; A/B binds **two**.

Proposed shape (analogous to `experience-profiles.yaml`), e.g. `state/config/gamma-style-guides.yaml`:
```yaml
style_guides:
  hil-2026-apc-standard-A:            # the "name"
    template:        null              # or studio_template_id g_nv5q4da69qiiu8q
    production_mode: api               # api | studio
    theme:           njim9kuhfnljvaa   # 2026 HIL APC (Nejal)
    text_content:    { mode: preserve, amount: minimal, audience: "...", tone: "...", language: en }
    visuals:         { image_source: aiGenerated, image_model: auto, art_style: illustration, keywords: [minimalist, bold] }
    format:          { type: presentation, variant: traditional, card_split: inputTextBreaks }
    page_settings:   { dimensions: 16x9, header_footer: off }   # the API-only constraints
    brand_binding:   master-style-bible   # machine link to brand truth (color/type/a11y)
  hil-2026-apc-blueprint-B: { ... lineArt / recraft-v3-svg / 16x9 ... }
```
**Param ranges** drawn from `gamma-api-mastery/parameter-catalog.md`; **brand constraints** linked from `master-style-bible.md` (closing the manual hex/font→`additionalInstructions` translation tax); **validation** mirrors `creative_directive_validator.py`.

---

## 5. Recommendation, sequencing & where it slots

This is a **new capability** — *giving the CD agent visual authority it has never had* — so it is its **own party-greenlit arc** (PRD-light → schema → CD-ownership wiring → Gary-consumption → live proof), not a Leg-1b rider. Two down-payments can land cheaply/independently and are worth pulling forward:
1. **Default `cardOptions.dimensions=16x9` unconditionally** in `generate_gamma_variants` (closes the cropping bug now; this is Leg-4 finding (a)'s core).
2. **Promote the theme/template config out of the "smoke fixture" + the `runs/` artifact** into a real `state/config/` home (pre-figures the library).

**Relationship to the active arc:** this is adjacent to the Concierge Production Substrate arc but distinct — it advances **CD/creative-control** (the second pillar alongside Marcus). It can run after Leg-1b green-light, or be sequenced as a parallel CD-substrate arc. The aspect-ratio piece is already a Leg-4 item; the *library* is bigger than Leg-4.

---

## 6. Decisions to confirm before specifying

1. **Ownership model:** CD agent (Dan) **authors+evolves** the library, operator-approves (operator said "CD agents will own and evolve")? Dan is currently advisory-only and never writes `state/config/` — making him the owner is a real lane change requiring party ratification.
2. ~~**Granularity of a "name":** single look vs paired A/B set?~~ **RESOLVED (operator 2026-06-30):** a name = **one complete look**; an A/B run **binds two** named styleguides (one per variant) — see §4a.
3. **Studio vs Classic:** is `production_mode` a *field within* a style guide, or do Studio and Classic get separate named guides?
4. **Brand linkage:** machine-link to `master-style-bible.md` now (auto-translate color/type into params), or keep brand as human-curated context Gary reads?
5. **Scope of "every field":** include the UI-only fields (reference image, formatVariant) as *intent-captured-but-not-enforced* rows, or API-enforceable fields only?

---

## 7. Party ratification — 5/5 RATIFY-WITH-AMENDMENTS (2026-06-30, no impasse)

Fully-spawned team: **Winston (architect) / John (PM, tiebreak) / Murat (test)** + **Dan (CD) / Gary (Gamma)** as the two specialty add-ons. All five RATIFY-WITH-AMENDMENTS; Quinn/John tiebreak not needed (John's ownership ruling aligned with all). Binding amendments (full set memorialized in auto-memory `project_gamma_styleguide_library_design`):

- **SSOT registry + strangler-fig migration** (Winston/Gary): one CD-owned `state/config/gamma-style-guides.yaml`; absorb-and-retire the 5 scattered stores (Phase 0 16:9 → 1 land → 2 promote A/B → 3 delete), DEFAULT_VARIANT_PAIR as fallback until one green live A/B run; migrate `gamma-style-presets.yaml` + the `runs/…` template id in, then freeze legacy.
- **Ownership = AUTHOR-AND-PERSIST** (John tiebreak / Winston / Dan-self / Murat): CD authors+evolves the content via a versioned `cd_styleguide_library` block through Marcus's envelope; Marcus/operator persists; **"CD never mutates state/config" stays non-waivable**; `validate_gamma_style_guides.py` (mirror `creative_directive_validator.py`) is the precondition for write authority. (Resolves decision #1.)
- **`production_mode` = discriminated-union** (Winston/Murat/Gary/Dan/John): studio FORBIDS Classic-only keys (cardOptions/textMode/numCards) → hard-reject `gamma.styleguide.surface-violation`; api requires theme + full surface; completeness is surface-relative. (Resolves decision #3.)
- **Validation bar** (Murat): completeness **inverts polarity** (null/default FAILS on required); import frozen enums; live theme/template existence; coverage-manifest drift gate (universe = `GAMMA_SETTING_KEYS` ∪ page-settings); **differential no-vacuous-green** live test (two guides → measurably different artifacts); LOOK verdict stays operator-eye.
- **Consumption seam** (Gary): resolve `styleguide:<name>` as the base-layer seed in `_normalized_gamma_settings`; add `styleguide` to `GAMMA_SETTING_KEYS`; unresolvable → `gamma.styleguide.unknown`. Cascade topology survives.
- **16:9 down-payment lands NOW, decoupled** (Classic-branch unconditional `cardOptions.dimensions=16x9`, commented as superseded by the library default-guide); Studio 16:9 = template + `_assert_studio_image_card` guard; dual-surface live proof.
- **text_mode defaults `preserve`** (Winston, binding leaky-neck guard upstream of the L2 source-fidelity audit).
- **CD coherence triad** (Dan): theme + art-style/keywords + dimensions must agree, rejected at authoring if violated.
- **Picker→library learning loop is a v1 requirement** (Dan/John/Murat): per-slide styleguide-winner ledger feeds CD-authored library vN+1; provenance round-trip is a test obligation. (Resolves decision #2 mechanics.)
- **Profile↔styleguide = orthogonal registries + a CD-authored affinity layer** (reconciled Winston/Dan).
- **brand_binding reference in v1; auto-translation compiler deferred** fast-follow (Resolves decision #4). **UI-only fields `enforced:false`/manual-finish checklist, excluded from the completeness claim** (Resolves decision #5).
- **Roster:** ≥4 named coherent styleguides spanning ≥1 Classic + ≥1 Studio; the SMOKE FIXTURE pair = seed #1/#2.

**Disposition:** ratified design memorialized; this is its **own future party-greenlit CD-substrate arc** (only the 16:9 down-payment is shared with Leg-4 finding (a)). The active arc's next dev remains **Leg-1b**.

---

## 8. Seed exemplar registry — draft artifacts folded in (operator directive, 2026-07-01)

**Operator directive (2026-07-01):** *fold the Gamma styleguide registry exemplars into the upcoming styleguide registry spec.* Two draft artifacts are the seed for the formal registry schema/spec (**seed, not runtime-active config yet** — the runtime target `state/config/gamma-style-guides.yaml` is not written; these live under `_bmad-output/planning-artifacts/`):

| Artifact | Role |
|---|---|
| [`gamma-style-guides-v1-draft-2026-07-01.yaml`](gamma-style-guides-v1-draft-2026-07-01.yaml) | **Compact registry / data artifact** — selected values per style only (one schema-validated record per named guide across the §4 three categories). `schema_version: 0.1-draft`, `status: draft`, `registry_owner: cd`. |
| [`gamma-style-guides-v1-field-control-companion-2026-07-01.md`](gamma-style-guides-v1-field-control-companion-2026-07-01.md) | **Field-control reference** — the control dictionary: value choices, UI↔API mapping, implementation status, and current unknowns. The YAML stores selected values; this companion explains what each field means and how (or whether) the repo wires it. |

### 8a. Seed exemplar styles (captured)

These promote the §4a "SMOKE FIXTURE pair = seed #1/#2" intent into real, independently-selectable named exemplars, plus a second Classic look that tests registry generality:

- **`classic-freeform-x-cards`** — display `Classic-Freeform_X-Cards`; live example `https://the-modern-clinicians-di-a6j7emh.gamma.site/`. Classic · Freeform · Default/Fluid · Classic card mode · Tejal theme (`njim9kuhfnljvaa`) · AI-generated illustrated visuals · minimal/condensed screen text. (Seed from `DEFAULT_VARIANT_PAIR[0]`.)
- **`classic-cards-fluid-visuals-magazine-ai-direction-detailed`** — display `Classic-Cards_Fluid-Visuals_Magazine+AI-Direction_Detailed`; live example `https://the-economic-structural--1t485b6.gamma.site/`. Classic · Card-by-card · Default/Fluid · Magazine art direction · AI images · auto-selected model · detailed visual-led additional instructions. (Captured 2026-07-01 to test registry generality; `Magazine` is a UI art style with no documented named `stylePreset` → compiled via `custom_style`.)

(The draft YAML also carries `hil-2026-apc-blueprint-classic` [seed #2, B look], `hil-2026-apc-studio-image-card` [the Studio-template seed satisfying the ≥1-Studio roster rule], and a `proposed_new` `hil-2026-apc-data-clean-classic` candidate toward the ≥4 roster.)

### 8b. Binding design decision — exemplars capture SELECTED values, not runtime overrides

**A clean style exemplar records the style's actual selected values, not publication/runtime overrides.** Canonical case: a Default/Fluid style keeps `cardOptions.dimensions: fluid` in the exemplar **even if** Descript-bound production later applies a **16:9 publication safety override** (Leg-4 finding (a) / §3 aspect-ratio defect). The 16:9 forcing is **runtime policy**, not this style's selected value — encoding it into the exemplar would corrupt the style's identity. (Recorded on the YAML `dimensions` field note; both seed exemplars are `dimensions: fluid` accordingly.) This preserves the strangler-fig migration (§7) — the library records what each style *is*, while publication safety overrides stay in the runtime layer.

### 8c. Field-control categorization (companion legend → future schema)

Every field is classified by **how it reaches Gamma, if at all** — the seed for the formal registry schema's per-field control model:
- **API-wired** (`documented+wired`) — documented by Gamma AND wired through local Gary/client today.
- **Client-only** (`documented+client-only`) — passable by the raw client but not exposed by Gary normalization/dispatch (e.g. `sharingOptions`, `folderIds`).
- **UI-only / unknown** (`ui-or-unknown`) — visible in the Gamma UI or operator-desired, no documented per-request API mapping (e.g. reference image, `formatVariant`, card width/alignment/font-size). Carried `enforced:false` / manual-finish, **excluded from the completeness claim** (§7 decision #5).
- **Theme/template-owned** — controlled by the selected theme or template design, not a per-request field (the entire Studio look).
- **Runtime policy** — controls which API path or runtime behavior fires (`generation_method`, `num_cards_policy`, and the 16:9 publication override above); plus `compiled` (transformed into ≥1 API field, e.g. `keywords`→`additionalInstructions`) and `metadata` (registry/provenance, not sent to Gamma).

**Status:** this remains a **draft seed for the formal registry schema/spec, NOT runtime-active config.** Promotion (create `state/config/gamma-style-guides.yaml` + `validate_gamma_style_guides.py` + Gary consumption seam) is the §7-ratified, party-greenlit CD-substrate arc — see the YAML's `promotion_work_items`.
