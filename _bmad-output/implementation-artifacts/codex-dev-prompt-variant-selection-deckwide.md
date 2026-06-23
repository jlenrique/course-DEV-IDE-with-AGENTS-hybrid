# Codex Dev Prompt — Deck-Wide Variant Selection + Gamma Control Layer (NEW CYCLE)

**You are Codex (T1–T10).** Claude runs T11. Party green-light: **5/5 GREEN-WITH-AMENDMENTS** (Winston/John/Murat/Mary/Amelia, no impasse). Authority: `variant-selection-deckwide-fix-scope-2026-06-23.md` + `variant-selection-downstream-gap-2026-06-23.md`. **Do NOT relitigate scope.** All amendments below are BINDING ACs.

## Goal
Two coupled things, **D1 first and independently committable**:
1. **D1 — Deck-wide variant FILTER (the trial blocker):** consume the operator's `selected_variant_id` so the chosen variant's render flows downstream and the deck stops doubling.
2. **D3 + D7 — Gamma control layer + theme validation:** wire the full API-reachable Gamma knob set (validated) into both standard and per-variant production, and fail-loud on bad themes.

Studio card-design-mode + Import-with-AI are **NOT in the Gamma API** (confirmed live) → deferred to a future variant C (Playwright). Do NOT attempt them. Theme-picker interactive gate = separate follow-on, out of scope.

## T1 PRECONDITION (report in Dev Notes BEFORE code)
Read `app/marcus/orchestrator/production_runner.py` (`_variant_candidates` ~:443, `_apply`/merge ~:854, `_SELECTABLE_KEYS_BY_GATE` ~:816, the node order around the vision-perception node 07F), `app/specialists/irene/graph.py` (`_slide_roster` :118), `app/specialists/gary/_act.py` (`_theme_id` :127, `_theme_id_for_variant` :175, `_normalized_gamma_settings` :140, `_text_options_for_variant` :182, `_image_options_for_variant` :193, `DEFAULT_VARIANT_PAIR` :25), `payload_contract.py`. **Confirm:** (a) `gary_slide_output` rows carry `dispatch_variant` (the variant key) — the filter matches on THAT, not `variant_id`; (b) the exact node seam where the G2B/G2C pick is recorded vs where 07F runs (filter goes between them); (c) `gamma_settings` is the only carrier needed (no new top-level payload key). Report findings; if the seam differs from this prompt, flag before proceeding.

## The change

### D1 — Deck-wide variant filter (LANDS FIRST, independently committable — John)
In `production_runner.py`, immediately **after** the G2B/G2C selection is merged and **before** the vision-perception node (07F): filter the envelope's `gary_slide_output` to the rows whose `dispatch_variant` matches `selected_variant_id`.
- **Match predicate (Amelia):** `str(row.get("dispatch_variant") or "A") == selected_variant_id`. NOT `variant_id`.
- **Derived no-op (Amelia/Winston A1):** when `selected_variant_id` is absent/None → pass ALL rows unchanged (same code path, not a special-case branch). A single-variant deck (all rows `dispatch_variant="A"`, no pick) flows untouched → legacy byte-identical.
- **Fail-loud on empty match (Winston A1 / Murat / Amelia):** if `selected_variant_id` is set but matches ZERO rows → raise (contract violation), do NOT silently empty the deck.
- **Post-filter invariant assertion (Winston A1):** after filtering with a pick present, assert **exactly one row per `slide_id`**. The invariant is "exactly one," not "at most one."

### D3 — Fail-loud theme validation (both paths, ONE shared helper — Amelia)
In `_act.py`: add a single shared `_resolve_and_validate_theme(...)` helper used by BOTH `_theme_id` (run-level/standard) and `_theme_id_for_variant` (per-variant). Do NOT duplicate membership logic.
- name→id resolution runs BEFORE the membership assertion (a friendly name resolves to its id, then validates).
- Validation fires ONLY when a non-empty theme string is present. **A legitimate `None`/absent theme stays legal** (→ Gamma default) — do NOT turn absence into a fail-loud.
- Membership is checked against `list_themes()` using the **same `theme_limit` window** the resolver uses (else a valid theme past the limit false-rejects).
- Fail loud (before any credit-spending call) on a present-but-absent theme.

### D7 — Control layer inside `gamma_settings` (NO new top-level key — Amelia/Winston/governance)
Extend `_normalized_gamma_settings` allowed-key set (currently `theme/template/image_style/density/tone` at :167) to the full reachable set, and emit them in `_text_options_for_variant` / `_image_options_for_variant` / theme / cardOptions:
- **Text:** `amount`→`textOptions.amount` (enum brief/medium/detailed/extensive), `tone`→`textOptions.tone` (free-text), `audience`→`textOptions.audience` (free-text), `language`→`textOptions.language` (enum). `text_mode`→`textMode` (enum).
- **Image:** `image_style_preset`→`imageOptions.stylePreset` (enum photorealistic/illustration/abstract/3D/lineArt/custom), `image_model`→`imageOptions.model` (enum), `image_source`→`imageOptions.source` (enum), `image_style`→`imageOptions.style` (free-text, custom path only).
- **Layout:** `dimensions`→`cardOptions.dimensions` (enum).
- **stylePreset↔style coherence rule (Amelia — MUTUALLY EXCLUSIVE IN ONE EMITTER):** the image-options emitter is ONE function returning the dict. If `stylePreset` resolves to a named tile → emit `stylePreset`, **MUST NOT emit `style`**. If preset is `custom`/absent → emit `style` (from `image_style`) as the prompt. Both keys can NEVER coexist in the output (coexistence = the API silently ignores `style` = the original bug re-expressed).
- **Enum-vs-free-text partition (Amelia/Murat — pin explicitly):** closed-enum knobs (`amount`, `language`, `stylePreset`, `image_model`, `image_source`, `dimensions`, `text_mode`) → fail-loud membership validation. Free-text knobs (`tone`, `audience`, `image_style`/custom) → pass-through, NO validation.
- **Sentinel-omit symmetry (Amelia — load-bearing for byte-identity):** every new knob's unset/default value maps to **omit the key entirely** (no empty-string, no null). Preserve existing sentinels (`balanced`/`professional`/`default` = omit).
- Applies to BOTH standard (base) and per-variant production.

### DEFAULT_VARIANT_PAIR update (:25) — the locked looks
- **A (standard/Tejal):** theme `njim9kuhfnljvaa`, stylePreset `illustration`, amount `brief`, audience "Faculty and instructional designers familiar with Canvas and course design, American English", tone "Clear, professional, engaging in American English", language `en`, source `aiGenerated`, dimensions `16x9`. (model auto = omit.)
- **B (Blueprint Editorial):** theme `e8tz1vxb9v1urqp`, stylePreset `lineArt`, model `recraft-v3-svg`, keywords [blueprint, technical line drawing, dotted construction lines, architectural, single-accent color] (→ additionalInstructions), amount `brief`, tone "Confident, precise, lightly editorial — American English", audience/language/source/dimensions same as A.

### 401-throttle retry (NARROW — Winston A3 / Murat #5)
Add retry-with-backoff for `401` on the Gamma **`/generations`** path ONLY, **validated-key-only** (a key that already succeeded on an auth/`list_themes` probe this session = warm), bounded retries + backoff ceiling, then surface loud. Do **NOT** globally redefine `base_client`'s `AuthenticationError` 401 semantics (shared by every specialist). A `401` on a cold/unvalidated key stays fatal/fast-fail. Implement narrowly in Gary's Gamma path (e.g. `gamma_dispatch`/`gamma_client`), not in shared `base_client`.

## Tests (RED-first; all BINDING — Murat / Amelia)
1. **D1 doubling RED-first (Murat #1 / Amelia):** build a 2-variant `gary_slide_output`, set `selected_variant_id="B"`, assert the roster handed to 07F = exactly one variant's slides with `dispatch_variant=="B"`. **Paste the RED transcript** (the assertion failing on pre-filter code). Must assert the DOUBLING, not "a filter exists." Pin all three cases: 2-variant→filtered, single-variant→no-op, **no-match→fail-loud**.
2. **Legacy byte-identity (Winston A2 / Murat #4 / Amelia):** golden-payload snapshot **captured from pre-change code** (generate the golden from current HEAD BEFORE the knob code lands); a single-variant all-default run's emitted Gamma payload asserted **byte-identical** to the golden.
3. **Validators — three-assertion shape (Murat #2), per enum knob + theme:** (a) known-good passes; (b) known-bad raises **before any credit-spend** (assert NO Gamma client call happened — not merely "an exception"); (c) calibration: validator reads the real membership set, bad input is **structurally valid but semantically wrong** (e.g. a real-looking theme id absent from `list_themes()`).
4. **stylePreset↔style coherence:** named tile → output has `stylePreset`, NOT `style`; custom → output has `style`, NOT `stylePreset`. Never both.
5. **401-throttle retry scoping:** warm-401 (post-validated-key) → retried-with-backoff; cold-401 → fail-fast.
6. **Live-Gamma legs are OPERATOR-GATED (Amelia / sandbox-AC rule):** any AC that exercises live Gamma acceptance (stylePreset/model/source acceptance, the B `recraft-v3-svg` 201) is operator-gated evidence into Completion Notes — NOT a dev-agent AC that bursts the API. Dev-agent legs assert payload **shape** via shipped deps only.

## Wired ≠ proven — B gating (Murat #3 / Mary)
B (lineArt + recraft-v3-svg) is the first exercise of those knobs. **B is NOT "done" on structural validity.** Before any 2-variant trial dispatches B, there must be a clean isolated **HTTP 201 for the full B payload + an operator eye-check render**. If the Gamma rate window blocks this at T11, T11 lands the wiring + unit proof and carries **B's live-201 + eye-check as a named BLOCKING follow-on** gating B trial dispatch. A's 201 already stands (probed 2026-06-23).

## Honesty ledger (record in the handoff / Completion Notes — Mary)
- Studio-vs-Classic structural caveat: this API path ships **Classic cards** (theme+content-directive fidelity), NOT the canonical Studio image-cards.
- Perception/reading-path findings from this cycle apply to the **Classic-card render only**; canonical Studio reading-path is unmeasured (pending variant C).
- No claim of A/B **visual distinctness** or aesthetic fidelity until the live eye-check render; B-distinctness is "engineered, not verified" until then.
- Reliability language capped by the 401-throttle finding (known soft-failure).

## Fences / governance
**Data-plane NEW CYCLE.** None of the touched files (`production_runner.py`, `gary/_act.py`, `irene/graph.py`, Gamma client/dispatch) are on `block_mode_trigger_paths`; control layer rides inside the already-declared `gamma_settings` `CONSUMED_PAYLOAD_KEYS` entry → **no pack/manifest/4-file-lockstep edit, no pack version bump** (confirm untouched at T1). No new top-level payload key. No mocks for live legs (operator-gated). ruff + lint-imports + focused tests green. Codex T1–T10 → Claude T11.

## Handoff → Claude T11
`_codex-handoff/variant-selection-deckwide-ready-for-review.md`: the T1 seam/keying report; before/after; the RED transcript for the doubling bug; all 6 test results; the byte-identity golden attestation; the enum/theme three-assertion evidence; the stylePreset↔style coherence evidence; the 401-retry scoping evidence; baseline-diff attestation; and the explicit B-gating status (live-201 done, or named blocking follow-on).

## NOTE (John): D1 is the trial blocker and lands first/independently. The control layer is operator-requested enhancement riding the same files because it's governance-clean. If control-layer T11 throws more than a couple MUST-FIX, carve it to fast-follow — do NOT let it delay the D1 unblock.
