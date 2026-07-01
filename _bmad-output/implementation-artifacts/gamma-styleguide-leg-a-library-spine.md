# Leg-A — Gamma Styleguide Library SPINE + core proof (Phase 1)

**Arc:** Gamma Styleguide Library (branch `dev/gamma-styleguide-library-2026-07-01`).
**Class:** S. **Status:** **done** (dual-gate party CLOSE 2026-07-01 — Murat structural CLOSE-WITH-CONDITIONS + Dan/CD + Vera/fidelity CLOSE-WITH-CONDITIONS; all conditions applied: `--check-existence` limit 100→50 fix folded; AC#6 reframed [below]; 8 follow-ons filed in deferred-inventory incl. RIPE `styleguide-retire-default-variant-pair`). Arc GREEN-LIGHT 6/6 RATIFY-WITH-AMENDMENTS 2026-07-01 [Winston/John/Murat/Dan/Gary/Texas] + operator decisions folded — party record `_bmad-output/planning-artifacts/gamma-styleguide-library-greenlight-party-record-2026-07-01.md`. Dev + 3-lane bmad-code-review (Blind/Edge/Acceptance) + 10-item remediation RED-first (118 passed/1 skipped, validator exit 0 offline, ruff clean) + **AC#5 live differential PROVEN** (real Gamma, Classic vs Studio spanned, no-vacuous-green — evidence `evidence/leg-a-styleguide-differential-20260701T164108Z/AC5-SUMMARY.md`). Codex shadow-monitor Poll 11 independently concurred on AC#5.
**Gate mode:** **dual-gate** — Murat (structural: schema/validator/seam/override-removal/isolation) + Dan/CD & Vera (content-fidelity: seeds faithfully promoted, coherence-triad holds, differential proof non-vacuous). Operator holds the final LOOK verdict.
**Phase:** 1 (machinery). This story does NOT include the HTML picker (Leg D), the live-doc audit (Leg E), or roster growth (Leg F / Phase 2). `scripted` block is schema-declared here (optional) but its consumption wiring is Leg C.

## Why (product value / guardrail)

The Marcus-SPOC runtime today controls Gamma look/feel through **five scattered, non-CD-owned stores** + a hard-coded `DEFAULT_VARIANT_PAIR` labeled *"SMOKE FIXTURE, not a product default"* — and a **baked-in code override forces 16:9 on every Classic run regardless of intent** (`_act.py:789`). This makes the look of a *real* exported deck unreliable and un-authored. Leg A gives the CD agent a single, schema-validated, **CD-owned styleguide library** that is the **sole determinant** of what Gamma produces for any real deck, replacing the smoke fixture and removing code-level masking. This is PRODUCT-VALID — it controls real SPOC exports, not a proofing run ([[feedback_spoc_is_goal_not_concierge_proofing_runs]]).

## 🔒 PROTECTED INVARIANT — source-detail → Gamma conveyance (never degrade)

Operator-emphatic 2026-07-01: in the concierge-led production run (BMAD-Marcus + HIL, not the runtime SPOC), the pipeline translated detailed source design-notes (composition, color palette, required text labels, image-gen prompts) into narration script + Gamma illustrations **EXCELLENTLY**. Marcus/Irene/Gary's conveyance of that source detail into the Gamma calls (per-slide `inputText` / `additional_instructions` / `keywords` / image prompts + the `_instructions_for_variant` cascade) MUST be **preserved — possibly enhanced, NEVER degraded** ([[feedback_source_detail_to_gamma_conveyance_protected]]). **Binding on this leg:** the styleguide resolver is a **BASE-LAYER DEFAULT PROVIDER ONLY** — source-derived / per-variant instructions + keywords + prompts compose ON TOP and WIN on conflict; the resolver must not strip, truncate, reorder, or override them. Enforced by AC#8. (This is also *why* the LOW/MED/HIGH detail-spectrum proof corpus matters — the HIGH-detail slide is precisely where this conveyance is most load-bearing.)

## Scout ground truth (SOLID — confirmed in code + seed draft)

- **Consumption seam:** `app/specialists/gary/_act.py::_normalized_gamma_settings` (:349). Unknown-key hard gate at **:375** (`unknown = set(item) - GAMMA_SETTING_KEYS → GaryActError tag="gamma.settings.invalid"`). `GAMMA_SETTING_KEYS` frozenset :84-108 (already includes `production_mode`, `studio_template_id`, `dimensions`). Per-variant merge loop :382; enum validation :418 (`dimensions` vs `CARD_DIMENSION_VALUES` :81); studio-requires-template fail-loud :430.
- **🔑 The baked-in override to REMOVE:** `_act.py:789` → `generation_kwargs["card_options"] = {"dimensions": "16x9", **card_options}` — unconditional Classic-branch 16:9 (comment :780). This is the `27309271` down-payment; §7 always intended it *"superseded by the library default-guide."* Studio branch (:724, `generate_from_template`) does NOT set cardOptions (inherits template frame) — no 16:9 there.
- **Seed styles ready:** `_bmad-output/planning-artifacts/gamma-style-guides-v1-draft-2026-07-01.yaml` carries a complete `style_guides:` map + `column_model` field_type taxonomy (`api_field`/`compiled_field`/`runtime_policy`/`metadata`/`theme_or_template_owned`/`manual_or_ui_only`) + `validation_policy` + `promotion_work_items` (≈1:1 with this leg). Seeds: `classic-freeform-x-cards` (Classic, Tejal `njim9kuhfnljvaa`, **dimensions: fluid**), `hil-2026-apc-blueprint-classic` (Classic, Blueprint `e8tz1vxb9v1urqp`, 16x9), `hil-2026-apc-studio-image-card` (**Studio**, template `g_nv5q4da69qiiu8q`, aspect-ratio guard min 1.4). The draft **already encodes pure representation** — `classic-freeform-x-cards.dimensions: fluid` with the note *"Publication safety overrides such as Descript-bound 16x9 belong in runtime policy, not in the exemplar."*
- **Validator precedent:** `scripts/utilities/creative_directive_validator.py` (mirror its repo-anchored path + schema-load shape).
- **CD authoring boundary:** Dan authors through Marcus's envelope; **never** mutates `state/config` directly (non-waivable). The validator gates write authority.

## The build (ratified)

1. **Runtime-active SSOT** `state/config/gamma-style-guides.yaml` — promote from the draft. Schema across §7's three categories (prompt_configuration / page_settings / foundational theme-or-template via `production_mode` discriminated union) + additive **`presentation` metadata block** (`display_name, distinguishing, narrative{summary/feels_like/use_when/avoid_when/triad_rationale}, example_url, thumbnail_ref, last_used`) + **optional `scripted` block** (`{trigger∈frozen-enum, value, consumed_by, rationale}`; declared here, wired in Leg C). All new display fields = `metadata` field_type → completeness-EXCLUDED, additive-safe.
2. **Hermetic static write-gate** `scripts/utilities/validate_gamma_style_guides.py` — the operator-required **copacetic-quality audit** of the YAML + seed styles. Offline/CI, NO network. Enforces: completeness with **INVERTED polarity** (null/default FAILS on a required field); import **frozen enums** (reuse `_act.py` frozensets — do not re-derive); **discriminated-union** — `production_mode: studio` FORBIDS the Classic-only set `{text_mode, dimensions, amount, tone, audience, language, keywords, num_cards, card_split}` → `gamma.styleguide.surface-violation`, `api` requires theme + full surface; **coherence-triad** (theme + art-style/keywords + dimensions agree, `triad_rationale` prose must align); **roster floor** (≥1 Classic + ≥1 Studio present). Live theme/template existence check is behind a `--check-existence` flag that's the ONLY network-touching path and is OFF in the hermetic CI run.
3. **Gary consumption seam** — resolve `styleguide:<name>` as the base-layer seed inside `_normalized_gamma_settings`; add **only `styleguide`** to `GAMMA_SETTING_KEYS`; the resolver **STRIPS all metadata + `scripted`** before any `gamma_settings[]` item is built (else :375 hard-fails); unresolvable name → `gamma.styleguide.unknown`; studio-carrying-Classic-keys → `gamma.styleguide.surface-violation`. Cascade topology + per-variant override precedence survive. Add `styleguide` to the creative-directive `gamma_settings` schema too.
4. **🔑 REMOVE baked-in generation-time overrides** so the library is the SOLE determinant: **remove the unconditional 16:9 at `_act.py:789`** → the resolved style's `dimensions` alone drives `cardOptions` (fluid→fluid, 16x9→16:9, absent→omit cardOptions). Inventory `_act.py` + `gamma_client.py` for any *other* baked-in forcing and remove/relocate. **PRESERVE the Descript anti-crop OUTCOME** — file a follow-on `styleguide-16x9-publication-boundary-safety` (deferred-inventory) to relocate 16:9 to a publication-time policy; do NOT silently regress Leg-4 finding (a). Phase-2 runs stop at Storyboard B (pre-Descript), so removal is safe for the proof.
5. **CD authors seeds #1/#2** — promote `classic-freeform-x-cards` (Classic) + `hil-2026-apc-studio-image-card` (Studio) into the runtime YAML **through Marcus's envelope** (validator-gated). (The other draft entries may be carried as `status: draft`/`proposed_new` but only the two proof seeds must be validator-clean + live-proven here.)
6. **ONE live differential proof** (Murat no-vacuous-green) — two seed styles (≥1 Classic + ≥1 Studio) over the proof corpus produce **measurably different** Gamma output, real Gamma API, **terminating at Storyboard B** (pure representation, overrides removed, NO Descript assembly).

   **Proof corpus (operator-confirmed 2026-07-01) — C1M1 Part 3 "The Opportunity & The Clinician as an Innovator"** (`course-content/courses/tejal-c1m1-fresh-outline/source-outline.md` lines 492–581). **Deliberately spans the source-design-DETAIL spectrum** (operator-directed), because the degree of source direction modulates how much of the output the *styleguide* controls vs the *source* — turning the proof into a **2-style × 3-detail-level matrix** that reveals where style control is strong vs where source overrides it (all three self-contained; no missing-external-asset dependency):
   - **LOW detail — Part 3 Summary Slide** (~:547–552): "bulleted recap" + 3 bullets, no visual prescription → style expresses with **maximal latitude** → largest expected style differential.
   - **MEDIUM detail — Slide 1 "Physicianship = Innovation Leadership"** (~:493–496): visual format + an image-gen prompt naming a navy/teal palette → style works **within a described image** → moderate differential.
   - **HIGH detail — Design Brief "The Intrapreneur's Maze (Blank Canvas vs. Blueprint)"** (~:514–524): full composition + fixed color palette + required text labels → source **heavily constrains** → smallest expected differential (probes where style control yields to source).

   **Differential-proof implication for AC#5:** the no-vacuous-green bar is met if the two styles differ measurably on the LOW/MEDIUM slides; a *smaller* differential on the HIGH slide is an EXPECTED, informative result (source-dominates), not a failure — record the per-slide differential magnitude across the matrix rather than a single pass/fail. (Swap-in alternative for the HIGH pick if ever needed: the Part-3 "The Deconstruction" design brief ~:528–539.)
7. **Fold ONLY** the coverage-manifest-parity hygiene fix (stale `marcus/` vs `app/marcus/` path in `test_coverage_manifest_json_schema_parity`). Leave import-linter C3 + repo-wide ruff to the harmonize backlog (don't shape the arc around incidentals).

## Acceptance / close bar (Murat structural + Dan/Vera content; die-on-this = ⛔)

1. ⛔ `state/config/gamma-style-guides.yaml` loads + PASSES `validate_gamma_style_guides.py` **offline** (no network); the two proof seeds are validator-clean.
2. ⛔ **Inverted-polarity teeth:** a seed with a required field null/defaulted FAILS the validator (negative fixture). A `studio` guide carrying any Classic-only key FAILS with `gamma.styleguide.surface-violation` (negative fixture).
3. ⛔ Gary resolves `styleguide:<name>` → base-layer API keys with **all metadata stripped**; a metadata key reaching `gamma_settings[]` would trip :375 — assert it does NOT. Unknown name → `gamma.styleguide.unknown`.
4. ⛔ **Override removed:** a Classic run under a `dimensions: fluid` style emits **NO forced 16:9** (cardOptions omit dimensions or =fluid); a `dimensions: 16x9` style emits 16:9. Pinning test proves `_act.py:789`'s unconditional 16:9 is gone and the library value is authoritative.
5. ⛔ **Differential no-vacuous-green (live):** two seed styles over the same corpus → machine-detectably different Gamma artifacts (e.g. different theme/art-style/dimensions in the rendered output/manifest), spanning ≥1 Classic + ≥1 Studio, at Storyboard B. Real Gamma, first-run-stands.
6. ⛔ **CD non-mutation intact + SSOT/write-gate established** (reframed at CLOSE per Dan/CD — the literal "seed promotion rides the runtime envelope" ceremony is NOT exercised in Leg A; that author-and-persist runtime path is a later leg). What Leg A actually proves: (a) a **CD-owned SSOT** `state/config/gamma-style-guides.yaml` (`registry_owner: cd`); (b) `validate_gamma_style_guides.py` is the **write-gate** = the precondition for CD write authority (exit 0 offline); (c) the runtime resolver is **verified read-only** against `state/config` — sole access is `read_text`+`yaml.safe_load`, ZERO runtime write-sites, no `last_used` write-back (deferred to Leg D); no CD-direct state/config write in the diff. The full runtime envelope-authoring ceremony = filed follow-on `styleguide-cd-envelope-authoring-ceremony`.
7. Coverage-manifest-parity test green. Frozen `figure_tokens` neck untouched. `.venv/Scripts/python.exe -m pytest` module suites green.
8. ⛔ **Source-detail conveyance preserved (PROTECTED INVARIANT — never degrade):** a run carrying source-derived per-slide `additional_instructions` + `keywords` (+ per-slide `inputText`/image prompts) PLUS a `styleguide:<name>` still delivers ALL that source detail into the Gamma payload **unclobbered** — the styleguide fills only unset base-layer defaults; source/per-variant fields WIN on conflict; instruction concatenation order preserved. Regression fixture pins a source-rich slide (e.g. the HIGH-detail "Intrapreneur's Maze" design brief — composition + palette + required labels) through the resolver and asserts every source instruction line + keyword survives. Degradation = HARD failure ([[feedback_source_detail_to_gamma_conveyance_protected]]).

## Live vs offline

- **MUST be real-API (no mocks):** the two-style differential Gamma render to Storyboard B (AC#5). Real Gamma key ([[reference_gamma_generations_401_throttle]] — burst-throttle returns 401; single-card sequential dispatch).
- **OFFLINE-OK:** validator positive/negative fixtures (AC#1–2), resolver metadata-strip + unknown-name (AC#3), override-removed pinning (AC#4), envelope-promotion path (AC#6).

## RED-first sequence (dev agent, via bmad-quick-dev + party-spawned dev per [[feedback_bmad_workflows_party_and_dev_agent]])

1. RED: validator rejects a null-required seed + a studio-with-Classic-key seed (inverted polarity + surface-violation).
2. RED: resolver — `styleguide:<name>` expands to API-only keys, metadata stripped; unknown → `gamma.styleguide.unknown`.
3. RED: override-removed pinning — fluid style ⇒ no 16:9; 16x9 style ⇒ 16:9.
4. GREEN: implement schema/YAML promotion + validator + resolver + the `_act.py:789` removal + `styleguide`→`GAMMA_SETTING_KEYS` + creative-directive schema. Module suites green; fold coverage-manifest-parity fix.
5. (Gated on 1–4 green) LIVE two-style differential render to Storyboard B; assert machine-detectable difference (AC#5).

## Files (anticipated)

- NEW `state/config/gamma-style-guides.yaml` (promoted from draft).
- NEW `scripts/utilities/validate_gamma_style_guides.py` (mirror `creative_directive_validator.py`).
- UPDATE `app/specialists/gary/_act.py` — `GAMMA_SETTING_KEYS` (+`styleguide`), `_normalized_gamma_settings` (resolve+strip), remove `:789` unconditional 16:9.
- UPDATE `state/config/schemas/creative-directive.schema.*` — `styleguide` on `gamma_settings`.
- UPDATE the stale coverage-manifest schema path (`marcus/`→`app/marcus/`).
- NEW tests: `tests/**/test_validate_gamma_style_guides.py`, `tests/**/test_styleguide_resolution_seam.py`, `tests/**/test_gary_dimensions_override_removed.py`.

## Lockstep

**No pack bump.** `gary/_act.py`, `state/config/gamma-style-guides.yaml`, and the validator are NOT in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (verified 2026-07-01). Standard dev authority.

## Risks (owned)

- **Metadata leak into the API payload** (Gary) → AC#3 strip-assertion + the :375 gate is the mitigation; NEVER whitelist metadata into `GAMMA_SETTING_KEYS`.
- **Silent 16:9 regression for future Descript runs** → the removal is intended, but file the publication-boundary follow-on so production Descript decks don't crop; Phase-2 stops at Storyboard B so no regression in-arc.
- **Vacuous-green differential** (Murat) → two styles that render indistinguishably = a config or resolver bug; AC#5 requires a machine-detectable difference, not operator taste alone.
- **Studio live-existence** (Gary/Texas) → the Studio seed's `studio_template_id g_nv5q4da69qiiu8q` needs a live template-existence check before the Studio render; if the template is gone, the differential falls back to two Classic styles + a filed Studio follow-on (do not fake it).

## Follow-ons to file (deferred-inventory)

`styleguide-16x9-publication-boundary-safety` (relocate the anti-crop policy); `styleguide-retire-default-variant-pair` (after one green live differential run, retire the SMOKE FIXTURE authority — draft `promotion_work_items` last item); carry Legs B–F.
