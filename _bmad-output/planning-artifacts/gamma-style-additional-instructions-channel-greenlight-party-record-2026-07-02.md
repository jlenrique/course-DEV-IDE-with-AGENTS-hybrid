# Green-light party record — style-level `additional_instructions` channel

- **Date:** 2026-07-02
- **Branch (worktree):** `dev/gamma-styleguide-phase2-2026-07-02` (isolated worktree `agent-a97301884687ce65d`)
- **Feature:** Add a style-level `additional_instructions` channel to the CD-owned Gamma styleguide registry so each style can carry persistent deck-level prose to Gamma's LLM that **complements, never overwrites**, the per-deck source-derived content instructions and Gary's hardcoded card-structure rule.
- **Gate:** `bmad-party-mode` roundtable (BMAD sprint-governance §2). Canonical core **Winston / John / Murat / Amelia** + specialty add-ons **Gary** (Gamma specialist) and **Dan** (CD). Each voice spawned as an independent agent and judged from verified seam facts.
- **Scope frame (operator-corrected, binding):** NO new style authored; the SSOT `state/config/gamma-style-guides.yaml` **records stay byte-unchanged** (field wired but unpopulated, for FUTURE authoring); **no paid live render / no live driver**. Wiring proven with a synthetic-fixture wire-level unit test. SPOC-is-the-goal guardrail: the change earns its place by making the real styleguide surface more capable, not to pass any proofing run.

## Verdict: GREEN ×6 (unanimous, with folded refinements)

| Voice | Verdict | Load-bearing point |
|---|---|---|
| Winston (architect) | GREEN | Two drift-guards move in lockstep; additive-safety airtight; studio left untouched (not a Classic-only key → no surface-violation). Require: pin ORDER (not just co-presence); test empty/whitespace list ⇒ byte-identical. |
| John (PM) | GREEN | Right-sized for the SPOC product; AC-4 + AC-6 are non-waivable safety proofs; AC-5 must **advance the filed follow-on**, not fork it; `gamma-keywords-to-imageoptions-style-channel` does not gate this text channel. Require: assert ordering explicitly. |
| Murat (test architect) | GREEN | Index-based ordering assertion; absent-vs-empty resolver branch (empty list ⇒ key absent); multi-item list test; **unique sentinel prose** to kill tautology risk; exact-`==` for AC-6; synthetic fixture via `resolve_styleguide(..., guides={...})` / monkeypatch — never a fixture file in the guide dir. |
| Amelia (dev) | GREEN | Keep the key in `GAMMA_SETTING_KEYS` (satisfies the subset assert) but **EXCLUDE it from the per-variant override loop** (`GAMMA_SETTING_KEYS - {variant_id, styleguide, additional_instructions}`) — strictly less code, removes the `str()`-clobber hazard by construction. Module-level `_join_...` helper; confirm single list→str join site at the API boundary. |
| Gary (Gamma specialist) | GREEN | STYLE-first-then-payload is the correct precedence (last-mentioned/most-concrete dominates for Gamma's LLM). **Add the `image_source=aiGenerated` vs stock-photo-prose contradiction axis (ERROR)**; optional WARN for tone/amount echo. PROTECTED source conveyance not at risk. |
| Dan (CD) | GREEN | LIST is the right authoring shape (mirrors the Studio template-lock list; line-by-line auditable). WARN/ERROR split correct (redundancy = smell/advisory; contradiction = fault/blocking). **DO document the field in the YAML schema-comment block** — "byte-unchanged" binds RECORDS; a schema comment is structure, not a populated record, and a dormant undocumented field is a future-author trap. Absent must equal empty-list. |

## Ratified design decisions

1. **Field shape:** `prompt_configuration.additional_instructions` — optional **list of non-empty strings** (mirrors the existing Studio template-lock list; coherent across `api` + `studio`). Absent ⇒ byte-identical to today. Empty list / whitespace-only items ⇒ treated as absent (Dan/Murat).
2. **Resolver:** add `additional_instructions` to `RESOLVED_API_KEYS`; `_expand_api` emits the cleaned non-empty list (drops when empty after cleaning); `_expand_studio` **unchanged** — the Studio list stays documented template-lock intent (unconsumed as today), and because `additional_instructions` is **not** a Classic-only key it is not a surface-violation.
3. **`GAMMA_SETTING_KEYS`:** add the key (keeps the import-time `RESOLVED_API_KEYS ⊆ GAMMA_SETTING_KEYS` assert green and lets the resolved base flow into `settings`), but **exclude it from the per-variant override iteration** (style-only channel; no per-variant override in this story).
4. **Composition (`_instructions_for_variant`):** style block read from `settings` (**never** `payload["additional_instructions"]`), joined list→prose via a module-level helper, composed as a **separate** part ordered **style-first → per-deck source-derived → Gary card rule → keywords imagery → "Variant X."**. Absent/empty ⇒ `""` ⇒ dropped by the existing filter-join ⇒ byte-identical.
5. **No-overwrite guarantee (AC-4):** an all-parts-survive test asserts every part co-exists in the emitted string AND pins their relative order via `.index()`; a parametrized clobber-each-part battery (unique sentinels) goes RED.
6. **AC-5 non-contradiction write-gate (advances filed `gamma-prose-vs-param-noncontradiction-validator`):** ERROR when prose contradicts a structured param — (a) non-photographic preset {illustration, lineArt, abstract, 3D} + photographic prose tokens, (b) `photorealistic` preset + illustration/vector/line-art prose tokens, (c) `image_source=aiGenerated` + stock-photo prose tokens (Gary's added axis). WARN when prose merely echoes Gary's hardcoded card rule. Conservative first cut, additive-safe (no existing style trips it).
7. **AC-7 REVISED:** drop the paid live A/B. Prove the field reaches `generation_kwargs["additional_instructions"]` end-to-end with a **synthetic-fixture** wire-level unit test (FakeGammaClient), never an SSOT edit, never a live render.
8. **SSOT touch (the only one):** a schema-comment documentation block appended to the trailing comment region of `gamma-style-guides.yaml` (parallel to the existing `scripted_enum` doc). **Zero records changed, zero values populated** — honors "records byte-unchanged" + "nobody populates it yet" while making the dormant field discoverable (Dan, party-consented).

## Studio disposition — micro-ratification (Gary + Dan, unanimous)

After the operator clarified that `prompt_configuration.additional_instructions` is an EXISTING but INERT field (currently silently dropped by the resolver) carried on the studio record, a focused 2-voice ratification decided the studio path explicitly:

**RATIFIED: OPTION B — TEMPLATE-LOCK-ONLY BY DESIGN.** The Gamma create-from-template call has no `additionalInstructions` channel; the `studio_prompt_lock` wrapper is the sole studio style-authority surface and already enforces the exact intent the annotation states. Threading it (Option A) would be redundant with the lock and risk diluting it on a paid render path. So a studio record MAY carry `additional_instructions` (validated for shape, NOT a surface-violation), but the resolver **deliberately does not emit it** — the value is a documented template-lock annotation and the previously-silent drop is now **intentional + documented + tested** (`_expand_studio` comment + `test_studio_resolver_never_emits_additional_instructions`). Gary: "the api/Classic path has a real channel; studio does not — correct channel allocation, no paid-path risk." Dan: "the template is the authority; the annotation is documentary; a documented, shape-checked, test-pinned deliberate non-emission converts a latent surprise into a guarded invariant."

## Code review (3-lane bmad-code-review) — outcome

Three independent lanes (Blind Hunter, Edge Case Hunter, Acceptance Auditor) reviewed the diff. **No MUST-FIX.** Acceptance Auditor: all 7 ACs MET with non-vacuous tests. Two SHOULD-FIX + one NIT were independently raised by BOTH hunter lanes and REMEDIATED RED-first:

1. **Per-variant `additional_instructions` silent-drop → fail-loud** (both hunters): adding the key to `GAMMA_SETTING_KEYS` (required by the subset assert) meant the unknown-key gate no longer rejected a per-variant item carrying it, and the excluded override loop silently ignored it. Now raises `GaryActError(tag='gamma.settings.invalid')` — symmetric with the module's other fail-loud guards.
2. **Non-contradiction ERROR false-positives** (both hunters): bare `photo`/`vector` substring bleed ("photosynthesis", "telephoto", "vector field") and negation ("never use photographs") could hard-block legitimate future prose. Remediated with leading-word-boundary matching, tightened high-precision token lists (dropped bare `photo`/`vector`/`sketch`), and a best-effort same-clause negation guard.
3. **Card-rule echo WARN on studio** (NIT, both hunters): gated the echo WARN to `production_mode == 'api'` (studio prose is never emitted).

Dismissed NITs (write-gate-guarded defensive tolerance; pre-existing non-dict-`prompt_configuration` pattern) per the aggressive-DISMISS rubric. Post-remediation: 215 passed / 1 skipped across gary + validator suites; validator CLI exit 0; ruff clean; `git diff --check` clean.

## No impasse

Unanimous GREEN; no Dr. Quinn synthesis / John tiebreaker needed. Refinements + code-review remediations folded into the implementation and the AC spec (`gamma-style-additional-instructions-channel.md`).
