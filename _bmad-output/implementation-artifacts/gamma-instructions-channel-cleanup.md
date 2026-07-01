# gamma-instructions-channel-cleanup — de-redundant the additionalInstructions channel

**Arc:** Gamma Styleguide Library (branch `dev/gamma-styleguide-library-2026-07-01`).
**Class:** S. **Status:** **done** (DUAL-GATE CLOSE 2026-07-01 — 🧪 Murat structural 8/8 bars + 🛡️ Vera fidelity 6/6 bars, no blocking conditions). RED-first proven (6 failed pre-fix; AC#1/#2 RED). AC#8 live real-Gamma A/B PASS (wire captured: no dump/None; `imageOptions.stylePreset=illustration` + `textOptions` carry amount/tone structurally; source design-note verbatim+leading; source keywords WON over styleguide base live — `vector, minimalist, single-accent color`; high-detail maze card rendered 929KB). 201 gary/styleguide tests green, ruff clean. Evidence `evidence/instructions-cleanup-ac8-20260701T182809Z/`. **Phase:** 4-implementation.
**Gate mode:** **DUAL-GATE** — Murat (structural: channel separation, test inversion, None/empty-guard) + Vera (fidelity: source-detail conveyance preserved, keywords precedence), Vera's scope bounded to the conveyance seam. Live A/B real Gamma, no mocks, first-run-stands.
**GREEN-LIGHT:** 6/6 RATIFY-WITH-AMENDMENTS 2026-07-01 [Winston/John/Murat/Amelia/Gary/Vera] — party record `_bmad-output/planning-artifacts/instructions-channel-cleanup-greenlight-party-record-2026-07-01.md`.

## Operator design principle (binding frame)
> "additional instructions are powerful, and certain styles may end up being defined largely by what is stated there rather than elsewhere. That is fine. But those instructions should never **contradict** other parameter settings and be **merely redundant**." (operator 2026-07-01)

`additionalInstructions` is a **legitimate, even primary, style channel.** This story does NOT strip style prose; it removes the two pathologies: **merely-redundant** echoes of structured settings, and the **contradictory** `image_style=None` literal. The channels are **complementary**: an instruction may carry real art-direction, but must never merely echo nor contradict a structured param.

## Why (product value / guardrail)
The operator saw, in live Gamma runs, `additionalInstructions` carrying `"Apply this variant's Gamma settings: image_style_preset=illustration; image_style=None; amount=brief; tone=…; keywords=…"`. `image_style_preset`, `amount`, `tone` are ALREADY sent structurally (`imageOptions.stylePreset`, `textOptions`) — so the prose is redundant + wrong-channel (the generation model may echo `image_style_preset=illustration` onto a card) + `image_style=None` is a literal bug. This is a real SPOC-runtime control-correctness fix (cleaner Gamma control, frees the instructions channel for the source detail the operator cares most about), NOT proofing-driven ([[feedback_spoc_is_goal_not_concierge_proofing_runs]]).

## 🔒 PROTECTED INVARIANT — source-detail → Gamma conveyance (never degrade)
`_instructions_for_variant` is INSIDE the protected cascade ([[feedback_source_detail_to_gamma_conveyance_protected]]). Source-derived `additional_instructions` + per-variant source keywords compose ON TOP and WIN. This story must PRESERVE (ideally enhance by de-noising) that conveyance, never degrade it. Enforced by AC#4/#5/#8.

## Scout ground truth (confirmed in code + grep)
- **Seam:** `app/specialists/gary/_act.py::_instructions_for_variant` (:627-657). `parts` = [source `additional_instructions`] + [card-split directives] + [settings-sentence :649-655] + [`Variant X.`]. Settings-sentence assembles `image_style_preset`/`image_style`/`amount`/`tone` + conditional `keyword_text` (:641-643) + conditional `template_text` (:647-648).
- **Structured forwarding CONFIRMED:** `_image_options_for_variant` → `imageOptions.stylePreset`/style/model/source; `_text_options_for_variant` → `textOptions.amount`/tone/audience/language; forwarded at gamma_client `payload["imageOptions"]`/`["textOptions"]`.
- **No downstream parser** of the emitted prose (grep app/scripts/skills clean — only the emitter + the validator's settings-DICT check).
- **`template`** has no structured Classic home (theme_id is the Classic selector; studio uses studio_template_id) — the prose `template=` clause is the only channel, renders only for non-default templates, and all seeds use `"default"` → **vestigial, drop it** (confirm at T1 no non-default-template Classic variant exists).
- **Source keywords ride the `keywords=` field** today (per `test_gary_dimensions_override_removed.py:121-164`) → de-tokenize MUST preserve their values (Vera's guard).
- **Test surface:** `test_gary_dimensions_override_removed.py:161` asserts the settings-dump PRESENT (must INVERT to absent) + `:164` asserts `keywords=X;` (must become guidance-prose assertion); `:121-164` pins compose-on-top (STAY GREEN, upgrade to byte-equal); `test_gary_deck_enrichment_hint.py` Ratchet-D sentinel-LO (STAY GREEN); `test_gary_gamma_dispatch.py:490` reads the string (must stay well-formed).

## The build (ratified)
1. **Delete the settings-sentence** (`_act.py:649-655`) — remove `image_style_preset`/`image_style`/`amount`/`tone` prose entirely (they flow via `imageOptions`/`textOptions` only). Kill the `image_style=None` literal by construction.
2. **Drop the vestigial `template_text`** (:647-648) — confirm at T1 no non-default-template Classic variant relies on it; if one does, keep + file a follow-on instead.
3. **De-tokenize keywords** — when `keywords` non-empty, append a single natural-language imagery-guidance sentence (e.g. `"Emphasize this imagery: {', '.join(keywords)}."`) to `parts`, preserving the keyword VALUES verbatim and the empty-guard. Keep source-wins precedence (source keywords compose on top).
4. **Preserve** source `additional_instructions` + card-split directives + `Variant X.` label byte-for-byte; clean join (no double-spaces / dangling separators).

## Acceptance criteria (RED-first; dual-gate)
- **AC#1 [RED — invert the pin]** `_instructions_for_variant` output for a settings-bound variant does NOT contain `"Apply this variant's Gamma settings"`, nor `image_style_preset=`, `amount=`, `tone=`, `template=` tokens. (`test_gary_dimensions_override_removed.py:161` inverts.)
- **AC#2 [RED — kill the bug]** the emitted string never contains the literal `None` (nor `image_style=None`), for any settings/keywords/empty combination.
- **AC#3 [keywords as guidance]** when `keywords` non-empty, the values appear as natural-language imagery guidance (values present; NO `keywords=` machine-field). When empty, no keyword clause + no dangling separator.
- **AC#4 [🔒 source verbatim]** source-derived `additional_instructions` substring appears **byte-identical** in the emitted string (upgrade compose-on-top from "present" to "character-equal"); source keywords preserved verbatim; source content precedes + wins over base guidance (ordering pin).
- **AC#5 [structured unchanged — co-regression tripwire]** `imageOptions{source,model,style,stylePreset}` + `textOptions{amount,tone,audience,language}` are **byte-identical** before vs after the change for the same payload (proves the settings still travel structurally; nothing that worked was moved).
- **AC#6 [Ratchet-D green]** `test_gary_deck_enrichment_hint.py` sentinel-LO reaches `additional_instructions` verbatim (unchanged regression fence).
- **AC#7 [no dangling seams]** removing the settings-segment leaves no double-space / dangling separator; the string is well-formed for empty-settings, empty-keywords, and full cases.
- **AC#8 [LIVE dual-gate — real Gamma A/B, de-subjectified]** deterministic driver, real Gamma, no mocks. On a **HIGH-source-detail slide** (required labels + specified palette + image-prompt in source notes): (a) capture the outbound `additionalInstructions` payload — assert NO settings-dump / NO literal `None` / NO `key=value` token; (b) structured `imageOptions`/`textOptions` byte-identical vs the pre-change arm; (c) the rendered card carries its required labels + specified palette/composition (Vera — conveyance preserved); (d) image style still lands same-or-better (eyeball = BONUS, not the gate). Classic branch mandatory. Re-judge from the captured payload + on-disk artifacts (not an inline judge).

## T1 Readiness
- **Required reads:** this spec; the green-light record; `_act.py:627-657` (emitter) + `:566-583` (`_image_options_for_variant`/`_card_options`) + `:840-905` (consumer); [[feedback_source_detail_to_gamma_conveyance_protected]]; the 3 tests named above. Confirm `_act.py` NOT in `block_mode_trigger_paths` (it isn't).
- **Blocking pre-reqs (discharged at green-light):** no prose parser exists; template vestigial; source keywords ride `keywords=`.
- **Dev vehicle:** spawned dev agent, RED-first ([[feedback_bmad_workflows_party_and_dev_agent]]); AC#1/#2 demonstrated RED before code; AC#4/#5/#6 never go red. **No mocks** on AC#8 (real `GAMMA_API_KEY`, `load_dotenv(override=True)`; reuse a known-good corpus / clean titles to dodge the bijective title-matcher flake).
- **Scope fence:** de-redundant the prose channel + de-tokenize keywords ONLY. Do NOT route keywords to `imageOptions.style` (filed follow-on). Do NOT build the prose-vs-param non-contradiction validator (filed follow-on).

## Follow-ons to file (deferred-inventory)
- 🟡 `gamma-keywords-to-imageoptions-style-channel` — route style-medium keywords (vector/minimalist/flat/line-art) to the structured `imageOptions.style` descriptor (stronger Gamma signal than prose), source-wins precedence; subject keywords → image prompt. Render-affecting → own live A/B. (Gary's Gamma-truth; deferred as the operator affirmed prose-as-style is fine.)
- 🟡 `gamma-prose-vs-param-noncontradiction-validator` — extend `validate_gamma_style_guides.py` coherence check to flag a styleguide whose prose contradicts its structured settings (enforces the operator's non-contradiction half at author-time).
