# Story — style-level `additional_instructions` channel (CD Gamma styleguide registry)

- **Status:** ready-for-dev → done (single-gate; wire-level story, party-GREEN 6/6 2026-07-02)
- **Green-light record:** `gamma-style-additional-instructions-channel-greenlight-party-record-2026-07-02.md`
- **Branch:** `dev/gamma-styleguide-phase2-2026-07-02` (worktree `agent-a97301884687ce65d`)
- **Files touched:** `app/specialists/gary/styleguide_library.py`, `app/specialists/gary/_act.py`, `scripts/utilities/validate_gamma_style_guides.py`, `state/config/gamma-style-guides.yaml` (schema-comment ONLY), tests under `tests/specialists/gary/` + `tests/utilities/`.

## T1 Readiness
- Required readings honored: CLAUDE.md (SPOC-is-the-goal guardrail; verify-via-shipped-deps; push cadence), the PROTECTED source-detail→Gamma conveyance invariant, the `gamma-instructions-channel-cleanup` operator principle (additionalInstructions is a legitimate primary channel but never merely-redundant with nor contradicting a structured param).
- Verified seams (not re-derived): resolver `styleguide_library.py` (`RESOLVED_API_KEYS`, `_expand_api`, `expand_record` leak-assert); `_act.py` (`GAMMA_SETTING_KEYS`, import-time subset assert, `_normalized_gamma_settings`, `_instructions_for_variant`); validator write-gate; existing tests.

## Feature
Each style may carry persistent deck-level prose (`prompt_configuration.additional_instructions`, optional list of strings) delivered to Gamma via the real `additionalInstructions` generation param. It **complements, never overwrites** the per-deck source-derived instructions (built upstream by the orchestrator from CD directive + source enrichment — PROTECTED) and Gary's hardcoded card-structure rule. Complement is structurally guaranteed by CONCATENATION (a `parts` list join) + threading through the resolved STYLE settings (never the payload key), so a key collision — the only overwrite vector — cannot occur.

## Acceptance criteria

- **AC-1 (schema + validator):** Registry accepts an optional `prompt_configuration.additional_instructions` = **list of non-empty strings**. Validator RED on: non-list, empty list, or any non-string / blank item (`[gamma.styleguide.additional-instructions-invalid]`). Additive-safe: absent ⇒ behavior byte-identical to today.
- **AC-2 (resolver):** `additional_instructions` added to `RESOLVED_API_KEYS`; `_expand_api` emits the cleaned non-empty list (empty-after-clean ⇒ key absent). `_expand_studio` unchanged; the Studio template-lock list stays documented + unconsumed and is **not** a surface-violation (documented explicitly). `additional_instructions` added to `GAMMA_SETTING_KEYS` (subset assert stays green) but **excluded from the per-variant override loop** (style-only channel).
- **AC-3 (composition):** `_instructions_for_variant` composes the style block as a SEPARATE part, ordered **style-first → per-deck payload source-derived → card rule → keywords → "Variant X."**. Nothing dropped.
- **AC-4 (TESTED no-overwrite):** a composition test asserts ALL parts survive in the emitted string simultaneously (payload content instr + style block + card rule + keywords imagery + variant) AND pins their relative ORDER via `.index()`; a parametrized clobber-each-part battery (unique sentinels) goes RED if any part is removed/clobbered.
- **AC-5 (non-contradiction write-gate):** advances the filed `gamma-prose-vs-param-noncontradiction-validator`. ERROR (`gamma.prose.contradicts-param`) when style prose contradicts a structured param: non-photographic preset + photographic prose; `photorealistic` preset + illustration/vector/line-art prose; `image_source=aiGenerated` + stock-photo prose. WARN (`gamma.prose.echoes-param`) when prose merely echoes Gary's card rule. Conservative first cut; no existing style trips it.
- **AC-6 (additive-safe byte-identity):** the composition emits a byte-identical `additionalInstructions` string when no style `additional_instructions` is present (absent AND empty-list AND whitespace-only-items all ⇒ identical). Proven with exact-`==`.
- **AC-7 (REVISED — no live render):** NO paid live Gamma A/B. A synthetic-fixture wire-level unit test proves the style prose reaches `generate_gamma_variants` → `generation_kwargs["additional_instructions"]` as its own concatenated part, using a hand-built guide dict / monkeypatched resolve — never an SSOT edit, never a live call.

## Non-goals / deferred
- No new style; no populated `additional_instructions` values in the SSOT (records byte-unchanged).
- Per-variant `additional_instructions` override (style-only for now).
- `gamma-keywords-to-imageoptions-style-channel` (independent image-channel routing) — out of scope.
- Broadening the non-contradiction rule-set beyond the conservative axes above (extensible later under the filed follow-on).
