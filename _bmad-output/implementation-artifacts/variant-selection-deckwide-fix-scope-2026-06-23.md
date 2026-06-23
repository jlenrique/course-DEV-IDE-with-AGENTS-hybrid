# Variant Selection — Deck-Wide Fix: Agreed Scope (NEW CYCLE prelude, 2026-06-23)

Builds on `variant-selection-downstream-gap-2026-06-23.md` (the forensic finding). Operator
chose **Option 1 (deck-wide)** and, in this session, expanded the scope to make **theme the
primary distinctness lever** with strict validation. This note captures the agreed decisions
to take into the party green-light → Codex T1–T10 → Claude T11.

## Agreed decisions

**D1 — Deck-wide variant filter (the load-bearing fix).**
Immediately after the G2B/G2C selection is recorded and **before** the vision-perception node
(07F), filter `gary_slide_output` so exactly one row per `slide_id` survives — the row matching
the operator's `selected_variant_id`. Drop the rest. No-op when `selected_variant_id is None`
and ≤1 row/slide (preserves today's single-variant behavior). Closes the deck-doubling bug at
`irene/graph.py:118` `_slide_roster`. **RED-first test** pinning both the doubling bug and the
filter.

**D2 — Theme as the primary distinctness lever; pin BOTH A and B to explicit theme IDs.**
Change `DEFAULT_VARIANT_PAIR` (`gary/_act.py:25`) so A and B each carry a **real Gamma theme ID**
(no `theme: "default"` float for A — today that resolves to "first theme `list_themes()` returns",
which is order-dependent/non-reproducible; it lands on the house theme TODAY only because the two
custom HIL themes sort ahead of the alphabetical stock themes — fragile coincidence, not a pin).
The distinct B theme bundles palette + typography + layout + accent imagery and does the heavy
lifting on distinctness. Parameter knobs layer on top (they stack independently).
**LOCKED (validated live against the account 2026-06-23):**
- **A = `njim9kuhfnljvaa`** ("2026 HIL APC (Nejal)") — house theme.
- **B = `e8tz1vxb9v1urqp`** ("2026 HIL APC (Nejal) (B variant)") — operator-authored B theme.
B's non-theme parameter values (image stylePreset/keywords/text amount/tone/audience) = PENDING
operator confirm (the 2026-06-23 Prompt-Editor capture is the reference; see D7 below).

**D3 — Theme-validation hardening (fail-loud, both paths).**
Resolve + membership-check each chosen theme against `list_themes()` before credits are spent;
fail-loud if it doesn't exist; support name→id resolution (today only id/themeId/gammaId match).
Applies to BOTH:
- the per-variant `theme` path (`_theme_id_for_variant`, `:175` — currently passes through with
  no check), AND
- **the single-slide / run-level `theme_id` path** (`_theme_id`, `:127` — currently `if requested:
  return requested` returns the requested id verbatim without confirming it exists in the fetched
  themes list). Operator explicitly agreed to harden this too.

**D4 — Optional amplifier (operator decision pending).**
Wire `imageOptions.source` per-variant (e.g. `themeAccent` to let the B theme's own accent imagery
dominate instead of AI-generating new images). Only if operator opts in when picking B values.
Filed follow-on today; cheap to fold into the same cycle.

**D5 — Theme picker (TP capability) is OUT OF SCOPE for this fix.**
The interactive theme-selection gate (`theme-template-preview.md`) is NOT wired into the production
trial flow. `list_themes()` itself works (proven live 2026-06-23); what's missing is the gate
(options node + select-verb capture + envelope consumption), ~voice-select-arc footprint
(story-sized, own RED-first tests). NOT needed for this trial — D2 pinned IDs + D3 validation give
deterministic, validated theme selection without it. Filed as a separate follow-on
(`gamma-theme-picker-interactive-gate`); do NOT fold into the variant cycle.

**D6 — Studio card-design mode deferred to a future "variant C" (Playwright UI automation).**
Confirmed 2026-06-23 from the live Gamma developer docs + the MCP Generate schema + the repo's own
`gamma-style-presets.yaml:99` note: the Generate API has **NO** card-design-mode / Studio-vs-Classic /
`formatVariant` parameter (`cardOptions` exposes only `dimensions` + `headerFooter`). Studio is
UI-only. Future variant C would drive the Gamma editor UI via Playwright (simulate operator at
keyboard → select Studio → export → ingest). Separate arc; filed follow-on
(`gamma-studio-mode-variant-c-playwright`). A/B proceeds via the API with theme as the lever.

**D7 — Image-style wiring fix: use `stylePreset` (named tile), not free-text `style`.**
Gary today wires `image_style` → `imageOptions.style` (free-text), which the API **IGNORES when a
named stylePreset is set** (per live docs + `gamma-style-presets.yaml:87`). The B capture uses the
**Illustration** named tile + keywords [minimalist, bold, flat, geometric]. To faithfully reproduce
even the reachable look, Gary must wire **`imageOptions.stylePreset`** (+ optionally `model`,
`source`, keywords-as-hint). The repo's `hil-2026-apc-nejal-A` preset already encodes correct values
(`stylePreset: illustration`, model `gemini-3.1-flash-image-mini`, keywords). Fold this into the cycle.

## LOCKED LOOKS (going forward = theme + fully-realized parameter set)

**Studio decision:** NOT param-approximable (Classic cards cannot bake text into a single image).
Deferred to **variant C (Playwright UI automation)** per D6. B gets a fresh native-API identity instead.

**Standard "A" — Tejal, fully parameterized** (the canonical 2026 HIL APC Nejal look, now wired
end-to-end at runtime instead of floating on list-ordering):
- theme `njim9kuhfnljvaa` · textMode `generate` · amount `brief` · audience "Faculty &
  instructional designers familiar with Canvas and course design, American English" ·
  tone "Clear, professional, engaging — American English" · language `en` · source `aiGenerated` ·
  model auto (omit) · stylePreset `illustration` · format `presentation` · dimensions `16x9`.
- Matches the operator's 2026-05-28 `gamma_visuals` recipe on every API-reachable field; the only
  unreachable fields are `format_substyle: Traditional` + `card_design_mode: Studio` (UI-only).

**Variant "B" — "Blueprint Editorial"** (Claude judgment; analogous skeleton, distinct register):
- theme `e8tz1vxb9v1urqp` (B variant) · stylePreset `lineArt` (vs A illustration — headline diff) ·
  model `recraft-v3-svg` (vector/line-optimized; PROBE) · keywords [blueprint, technical line
  drawing, dotted construction lines, architectural, single-accent color] · tone "Confident,
  precise, lightly editorial" · amount `brief` · audience/language/dimensions/source = same as A.
- A reads warm full-color illustration; B reads crisp architectural blueprint editorial. Both
  on-brand; distinct at a glance; eye-checked at G2C. `recraft-v3-svg` + `audience` are
  first-exercised → live pre-flight probe confirms API acceptance.

## Knob → Gamma param reference (current wiring)
| Gary knob | Gamma param | Values | Default sentinel (=omit) |
|---|---|---|---|
| `theme` | `themeId` (live `list_themes()`) | account theme **IDs** | `default` → base theme |
| `image_style` | `imageOptions.style` (free-text art prompt) | any phrase | unset |
| `density` | `textOptions.amount` (enum) | brief · medium · detailed · extensive | `balanced` → omit |
| `tone` | `textOptions.tone` (free-text) | any tone word | `professional` → omit |
| `template` | advisory-only (echoed in `additionalInstructions`) | — | `default` |

## Open inputs (block locking the spec)
1. ✅ DONE — operator authored the B theme; both IDs captured + validated live (D2).
2. **Operator confirms B's non-theme params** from the 2026-06-23 capture: stylePreset `illustration`
   + keywords [minimalist, bold, flat, geometric]; text amount `brief` ("Minimal text"); tone
   "Clear, professional, engaging"; audience "Faculty and instructional designers…"; source
   `aiGenerated`, model auto. (Or "theme-swap only for now" if the operator wants to keep B's
   non-theme params equal to A this round.)
3. Confirm whether to wire `imageOptions.source`/`model`/`audience`/`language` per-variant now
   (D4/D7) or defer to a follow-on.

## Live pre-flight probe results (2026-06-23)

**Generation works; A param shape validated.** ~13 live `POST /generations` calls succeeded (201)
during probing, including the **full A payload** (`themeId njim9kuhfnljvaa` + `textOptions`
{amount:brief, audience, tone, language} + `imageOptions`{source:aiGenerated, stylePreset:illustration}
+ `cardOptions`{dimensions:16x9}) → **201, only a benign warning** ("numCards ignored when
cardSplit=inputTextBreaks"). So `audience` IS REST-accepted, and `stylePreset` (named tile) is the
correct image-style field (confirms D7). **B param shape** (themeId `e8tz1vxb9v1urqp`,
stylePreset `lineArt`, model `recraft-v3-svg`) is structurally identical with valid enum values →
HIGH-confidence accepted, but NOT yet isolated-201'd before the throttle hit (below). Eye-check
render of A vs B deferred to a cooldown window.

**🟠 FINDING — Gamma `/generations` returns `401 {"message":"Invalid API key"}` as a throttle under
burst load.** After ~13 rapid generations the key tipped into *sustained* 401 (did not clear across
4×20s backoffs). The key is valid (GET `/themes` 200 throughout; credits fine — this is a RATE
window, not credits). Implications:
- A NORMAL trial does only ~1–2 generation calls per run (one per variant; a deck is one call), so
  it is unlikely to trip this — my debug volume was the anomaly.
- BUT the trial dispatch should treat **401-on-generate as retryable-with-backoff**, not a hard auth
  fail (today `AuthenticationError` on 401/403 is non-retryable in `base_client.py`; Gary's
  `gamma_dispatch` normalizes all exceptions to `receipt.parsed.api-error`). Worth a Codex/T11 note:
  add 401-as-throttle handling (longer backoff) so a transient Gamma throttle doesn't hard-kill a trial.
- My earlier "generate_deck wrapper bug" hypothesis was WRONG (corrected): identical payloads via
  `c.post` also 401 once throttled. No wrapper bug; it's the throttle.

## Party green-light — RATIFIED 2026-06-23 (5/5 GREEN-WITH-AMENDMENTS, no impasse)
`bmad-party-mode`: Winston (architect), John (PM), Murat (TEA), Mary (analyst), Amelia (dev).
Quinn→John escalation NOT triggered. Binding amendments folded into the Codex dev-prompt
`codex-dev-prompt-variant-selection-deckwide.md` as ACs:
- **D1 filter:** match on `dispatch_variant` (not variant_id); **derived** no-op (absent pick → pass all,
  same path); post-filter assert **exactly one row per slide_id**; **no-match → fail-loud**; RED-first
  test asserts the DOUBLING (not "filter exists"). **Lands FIRST + independently committable** (John).
- **Legacy byte-stability:** golden-payload snapshot from **pre-change** code, byte-identical for a
  single-variant all-default run; sentinel-omit extends symmetrically to every new knob (unset → omit).
- **Validators not vacuous:** three-assertion shape (good / bad-blocked-before-spend / calibration vs
  live source; bad input = real-looking-but-absent); D3 = one shared resolve+validate helper, None
  legal, same `theme_limit`; explicit enum (fail-loud) vs free-text (pass-through) partition.
- **Coherence:** stylePreset↔style mutually-exclusive-in-one-emitter.
- **Carrier:** no new top-level payload key; stays in `gamma_settings`.
- **401-throttle retry:** narrow to the Gamma `/generations` path, validated-key-only, bounded — do
  NOT globally redefine `base_client` 401 semantics.
- **Wired ≠ proven (B gating):** B needs isolated 201 + eye-check before any B trial; if cooldown
  blocks T11, B is a named BLOCKING follow-on, not done on structural validity. A's 201 stands.
- **Sandbox-AC:** live-Gamma legs operator-gated; dev-agent legs assert payload shape via shipped deps.
- **Honesty ledger:** Studio-vs-Classic caveat recorded; perception findings scope-fenced to
  Classic-card renders; distinctness/fidelity claims withheld until eye-check.
- **Hygiene:** Studio→variant C (`gamma-studio-mode-variant-c-playwright`) + theme-picker
  (`gamma-theme-picker-interactive-gate`) FILED in `deferred-inventory.md`.

## Governance
NEW CYCLE (substrate; `production_runner.py` + `gary/_act.py` + Irene roster/Pass-2 chokepoint
wiring + RED-first tests). Data-plane — no `block_mode_trigger_paths` touch, no pack/manifest/lockstep,
no version bump. Codex T1–T10 → Claude T11. Pre-2-variant-trial blocker; single-variant trial
unaffected. Codex prompt: `codex-dev-prompt-variant-selection-deckwide.md`.
