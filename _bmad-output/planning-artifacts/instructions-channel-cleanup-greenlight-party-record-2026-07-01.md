# GREEN-LIGHT Party Record — `gamma-instructions-channel-cleanup`

**Date:** 2026-07-01 · **Arc:** Gamma Styleguide Library · **Branch:** `dev/gamma-styleguide-library-2026-07-01` · **Phase:** 4-implementation
**Trigger:** operator-surfaced from live Gamma runs — variant style settings are dumped as PROSE into `additionalInstructions` even though they're already sent via the structured Gamma API params.
**Verdict:** **RATIFY-WITH-AMENDMENTS, 6/6** (all GREEN or AMEND-toward-GREEN; no BLOCK). No impasse.

## Operator design principle (binding frame)
> "additional instructions are powerful, and certain styles may end up being defined largely by what is stated there rather than elsewhere. That is fine. But those instructions should never **contradict** other parameter settings and be **merely redundant**." (operator 2026-07-01)

`additionalInstructions` is a **legitimate — even primary — style channel.** The defect is NOT "style guidance in prose"; it is two pathologies: **(1) merely redundant** (echoing a structured setting) and **(2) contradictory** (fighting a structured setting, incl. the nonsense `image_style=None`). The contract: the two channels are **complementary**; no instruction may merely echo nor contradict a structured param.

## Party composition
Winston (architect), John (PM), Murat (TEA), Amelia (dev) — core. Gary (Gamma specialist, owns `_act.py`) + Vera (fidelity, guards the protected invariant) — specialists.

## The defect (code-confirmed)
`app/specialists/gary/_act.py::_instructions_for_variant` (:649-655) appends to `additionalInstructions`:
`"Apply this variant's Gamma settings: image_style_preset=…; image_style=None; amount=…; tone=…;{keywords=…}{template=…}"`. But `image_style_preset→imageOptions.stylePreset` and `amount/tone/audience/language→textOptions` are ALREADY forwarded structurally (`_image_options_for_variant`/`_text_options_for_variant` → gamma_client `payload["imageOptions"]`/`["textOptions"]`). So the prose is redundant + wrong-channel (the model may echo `image_style_preset=illustration` onto a card) + `image_style=None` is a literal bug.

## Blocking pre-reqs (discharged before green-light)
- **No downstream parser** of the emitted prose exists (grep app/scripts/skills) — the only `image_style_preset=` hits are the emitter + the validator's settings-DICT check (not the prose string). ✅
- **`template`** has no structured Classic home — reaches Gamma only via the prose clause, which renders only for non-default templates; all seeds use `"default"` → vestigial, safe to drop (confirm at T1). ✅
- **Source keywords currently ride the `keywords=` prose field** (per `test_gary_dimensions_override_removed.py:121-164`) → the de-tokenize MUST preserve their VALUES (Vera's drop-path guard). ✅

## Per-decision consensus

**1. SCOPE — 6/6 GREEN.** Remove `image_style_preset`/`image_style`/`amount`/`tone` from the prose dump + the `image_style=None` bug + the vestigial `template=` clause. Delete the whole assembled settings-sentence, not tokens.

**2. KEYWORDS — refined.** De-tokenize `keywords=X,Y;` → natural imagery-guidance prose (e.g. "Emphasize this imagery: X, Y."), **kept in the prose channel** (preserves source keywords + source-wins precedence — Vera). Only when `keywords` non-empty (keep the empty-guard). **Gary's Gamma-truth** (imageOptions.style is a free-text style-descriptor home; style-medium keywords like "vector, minimalist" land STRONGER there than in prose; prose is the weakest of {stylePreset selector / imageOptions.style descriptor / image-prompt subject / additionalInstructions}) is captured as a **filed follow-on**, NOT this story — it's a render-affecting optimization needing its own A/B + source-wins precedence design, and the operator affirmed prose is a legitimate style channel. Keeping keywords in prose here also fully avoids Vera's drop-path (values preserved).

**3. PROTECTED-INVARIANT GUARD — strengthened.** Not "test stays green" but real tripwires: (a) invert the `:161` pin to assert the settings-dump is ABSENT; (b) **redaction assertion** — no `image_style_preset=`/`amount=`/`tone=`/`image_style=None`/`key=value` settings-token survives in the emitted string; (c) source `additional_instructions` + source keywords appear **byte-verbatim** in the emitted payload (upgrade `:121-164` from "present" to "character-equal"); (d) source instructions precede + WIN over keyword guidance (ordering pin); (e) no double-spaces / dangling separators from the removed segment; (f) empty-settings/empty-keywords None-safety. Ratchet-D sentinel-LO test (`test_gary_deck_enrichment_hint.py`) stays green.

**4. GATE MODE — DUAL-GATE** (Murat structural + Vera fidelity). 4/6 dual (Winston/Amelia/Gary/Vera); John "single+named-Vera-assertion", Murat "single-PLUS asymmetric = Murat structural + Vera narrow spot-check". Resolved to dual-gate with **Vera's scope BOUNDED to the conveyance seam** (she does not re-litigate the whole pipeline) — satisfies Murat's/John's proportionality while giving Vera the fidelity seat she requires for the keywords-precedence risk.

**5. LIVE-PROOF BAR — de-subjectified.** Real Gamma A/B (structured-only vs prior prose-dump, same source input/variant/structured params): (a) capture the outbound `additionalInstructions` payload — assert NO settings-dump / NO literal `None` / NO `key=value` token; (b) structured `imageOptions{source,model,style,stylePreset}` + `textOptions{amount,tone}` **byte-identical** pre/post (co-regression tripwire — proves we moved nothing that was working); (c) a **HIGH-source-detail slide** renders its required labels + specified palette/composition (Vera — conveyance preserved); (d) image style still lands (same-or-better) — the eyeball A/B is a BONUS confidence read, NOT the gate (no subjective aesthetic-parity judge gates). Classic branch mandatory; Studio if keywords touch its imagery path.

**6. SEQUENCING / RISK — GREEN.** Standalone story now, ahead of Leg-B (operator-directed; self-contained, de-risks every later Gamma call). Grep discharged clean. Drop the vestigial `template=` clause (confirm at T1 no non-default-template Classic variant relies on it).

## Gate designation
**DUAL-GATE** (Murat structural + Vera fidelity/conveyance-seam). RED-first. Live A/B real Gamma, no mocks, first-run-stands, payload captured as evidence.

## Follow-ons to file (deferred-inventory)
- 🟡 **`gamma-keywords-to-imageoptions-style-channel`** (Gary) — route style-medium keywords (vector/minimalist/flat/line-art class) to the structured `imageOptions.style` descriptor (stronger Gamma signal than prose), with source-wins precedence over styleguide-base keywords; subject keywords → image prompt. Render-affecting → own live A/B. Deferred because the operator affirmed prose-as-style is fine and it exceeds this cleanup's scope.
- 🟡 **`gamma-prose-vs-param-noncontradiction-validator`** — extend the Leg-A `validate_gamma_style_guides.py` coherence check to flag a styleguide whose prose `additional_instructions` CONTRADICTS its structured settings (e.g. prose implies photographic while `stylePreset=illustration`). Enforces the operator's non-contradiction half of the contract at author-time.
