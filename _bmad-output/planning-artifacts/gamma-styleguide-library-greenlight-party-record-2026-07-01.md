# Gamma Styleguide Library — Arc GREEN-LIGHT Party Record (2026-07-01)

**Branch:** `dev/gamma-styleguide-library-2026-07-01` (fresh from master `d02f456c`).
**Inputs:** [`gamma-styleguide-library-scope-addendum-2026-07-01.md`](gamma-styleguide-library-scope-addendum-2026-07-01.md) (operator's 3 additions + workflow) + [`gamma-styleguide-library-briefing-2026-06-30.md`](gamma-styleguide-library-briefing-2026-06-30.md) (§7 core RATIFY 5/5).
**Team:** canonical core **Winston** (architect) / **John** (PM, tiebreak) / **Murat** (test) + specialty **Dan** (CD) / **Gary** (Gamma); **Texas** (retrieval) joined for the audit leg only (not a standing seat → ≤2-specialist rule preserved).
**Round type:** fully-spawned (6 independent subagents). **Outcome: 6/6 RATIFY-WITH-AMENDMENTS. No impasse → Quinn/John tiebreak not invoked.**

---

## Verdict tally

| Voice | Verdict | Headline amendment |
|---|---|---|
| 🏗️ Winston | RATIFY-WITH-AMENDMENTS | 6-leg schema-spine-first ordering; audit & validator are TWO components (hermetic write-gate + live superset); learned-rules never runtime-written to config |
| 🧪 Murat | RATIFY-WITH-AMENDMENTS | Audit CI runs vs committed recorded-fetch snapshot (live fetch = separate alerting job, never gates build); `scripted` needs differential-effect-fired proof; learned-rule append-only count pin |
| 📋 John (PM) | RATIFY-WITH-AMENDMENTS | Reframe `scripted`→one declarative field + BLOCK open-ended engine until a 2nd instance; split audit (enforcement MVP / live-fetch fast-follow); picker fast-follow; DONE-bar = 3 styles not 8 |
| 🎨 Dan (CD) | RATIFY-WITH-AMENDMENTS | Audit ownership splits 3 ways (Texas fetch / validator enforce / CD rule-content); narrative-description shape; `scripted` = closed-vocab CD intent; learned-loop two-store split |
| 🎰 Gary (Gamma) | RATIFY-WITH-AMENDMENTS | [HARD] metadata quarantine — only `styleguide` joins `GAMMA_SETTING_KEYS`; 8 documented + 3 learned dependency rules seeded; thumbnail = harvest slide-01; identified real Gary-side `scripted` classes |
| 🤠 Texas (retrieval) | RATIFY-WITH-AMENDMENTS (audit leg) | `gamma_docs` = real directory-registered RetrievalAdapter; 3 terminal states never 2; provenance triple + digest-diff drift; documented≠learned two-tier |

---

## Resolved design decisions (party consensus)

1. **Audit vs §7 validator = TWO binaries, one contract.** The static `validate_gamma_style_guides.py` stays hermetic/offline/blocking (the CD write-gate: frozen enums, discriminated-union, completeness polarity-inverted, live theme/template existence). The live-grounded **audit** is a superset that calls the static gate first, then consumes Texas's fresh fetch + enforces documented/learned dependencies. **Never put a live fetch in the write hot path.** (Winston/Murat/Dan/Texas unanimous.)
2. **Audit ownership splits 3 ways:** Texas owns the fresh external-doc **fetch** (`gamma_docs` provider); a validator owns **enforcement**; CD owns only the **rule content** (coherence-triad rules, narrative, `scripted` intent, learned rules), authored through Marcus's envelope. "CD never mutates state/config" stays non-waivable. Specialty seats = Dan+Gary; Texas owns the provider but is not a standing seat.
3. **Learned-dependency persistence = two-store split.** Raw **observations** → append-only asset-ledger + BMAD memory sidecar (runtime-written; not CD). Promoted **rules** → CD-authored `learned_dependencies` block in the YAML **via the envelope only**, provenance-cited, validator-gated. **A rule is not "learned" until its birthing run is a committed failing-case fixture** (Murat); append-only count/identity regression pin — silent shrinkage = red build.
4. **`scripted` = closed-vocabulary declarative data**, `{trigger∈frozen-enum, value, consumed_by, rationale}` — no code, no eval, no lambdas. Every trigger must name an existing consumption seam or hard-reject (`gamma.styleguide.scripted.unbound-trigger`). **v1 ships exactly ONE class end-to-end** (`min_cluster_floor` → Irene Pass-1, honoring the non-waivable 07G perception gate). The vocabulary is **extensible by later party consensus** — Gary named real further classes (model-fallback / credit-budget / sequential-dispatch / guard-threshold) that prove it is not a population-of-one, but they ship only when their seam exists.
5. **Schema extension = additive `metadata`.** New display fields (`presentation.{display_name, distinguishing, narrative, example_url, thumbnail_ref, last_used}`) are `metadata` field_type — **completeness-excluded, additive-safe.** [HARD, Gary] add **only** `styleguide` to `GAMMA_SETTING_KEYS`; the resolver **strips all metadata before any `gamma_settings[]` item is built**, or the `_act.py:375` unknown-key gate hard-fails the dispatch. `last_used` is joined from the ledger / written by a **non-CD (runtime/Marcus-side) writer** — idempotent, monotonic, isolated.
6. **Thumbnails = harvest slide-01 of each trial-refine run** (zero extra credits); refresh keyed to the record `version` bump (not `last_used`); Studio thumbnails harvested from the Studio from-template branch.
7. **HTML picker** supports **A/B two-select** (§4a binds two guides; single-select is degenerate); carries a **provenance round-trip identity test** (picked → applied → recorded winner, correct A/B attribution per slide).
8. **Audit fetch discipline (Texas):** `gamma_docs` = deterministic `RetrievalAdapter` over a version-pinned URL manifest (`state/config/gamma-docs-sources.yaml`), no LLM in the fetch path; **three terminal states** `VERIFIED-FRESH / VERIFIED-STALE-FALLBACK / FETCH-FAILED` — an empty/shell/failed fetch **never** collapses to "no constraint → pass"; provenance triple `{source_url, fetched_at, content_digest}` + digest-diff drift → flag-for-CD. Audit **diffs fresh docs against the six `_act.py` frozensets** as the current snapshot. Cadence = on-YAML-change hook + scheduled digest-refresh + cache-TTL on pre-run; **NOT** blocking session-START/every-run.
9. **Documented dependency rules seeded from Gary's experience (8):** custom-preset⇒style-required; image_model honored only under aiGenerated; named stylePreset⇒`style` ignored; **Studio surface-violation forbidden-set** = `{text_mode, dimensions, amount, tone, audience, language, keywords, num_cards, card_split}` (grounded in `generate_from_template`'s signature) + studio⇒template-required; numCards only under card_split=auto; dimensions built Classic-only; one export_as per request; theme_id must exist in live `list_themes()`. **Learned candidates (3):** model UI-name≠API-string churn; burst-throttle 401≠429; account parallel-task cap.
10. **Hygiene fold-in discipline:** fold **only** the coverage-manifest-parity fix (`marcus/` vs `app/marcus/`) into the schema leg (it's on this arc's validator path). The import-linter **C3 break** + repo-wide ruff noise stay in the harmonize backlog — do NOT expand arc scope around incidentals (Winston/Dan/Murat aligned).

---

## Decomposed leg/story plan (synthesized, MVP-first, all in-arc)

| Leg | Scope | Gate | Depends |
|---|---|---|---|
| **A — Library spine + core proof** | runtime-active `state/config/gamma-style-guides.yaml` (§7 three categories + `presentation` metadata + optional `scripted`) + hermetic `validate_gamma_style_guides.py` write-gate + Gary consumption seam (only `styleguide`→`GAMMA_SETTING_KEYS`; metadata-strip; unknown/surface-violation errors) + CD authors seeds #1/#2 via envelope + **ONE live differential run over 3 slides (Classic+Studio)**. Fold coverage-manifest-parity fix. | **dual** | — |
| **B — Dependency enforcement** | extend validator w/ the 8 documented rules + `learned_dependencies` store (append-only count pin; per-rule failing-case fixture) | **dual** | A |
| **C — `min_cluster_floor` scripted class** | closed-vocab `scripted` block; wire →Irene Pass-1 cluster floor honoring 07G; differential effect-fired proof; dead-config detector | **dual (+07G non-waivable)** | A |
| **D — HTML style-picker + CD-entry gate** | Storyboard-A-analogous publish; radio+submit at CD-entry; A/B two-select; per-row name/distinguishing/narrative/thumbnail/last_used; provenance round-trip; last_used write-back; thumbnail harvest+version-refresh | **single** | A |
| **E — Live-doc audit + `gamma_docs` provider** | Texas `gamma_docs` RetrievalAdapter; audit superset (static-gate-first → live diff vs frozensets); 3 terminal states; provenance triple; cadence; two-tier report | **dual** | A, B |
| **F — Roster growth + trial-refine confirmation** | grow to ~8 via reconciled 6 additions; differential matrix + expressiveness coverage-manifest; corpus ≥1 dense + ≥1 vertical slide; alt-dimension flagged for Descript-16:9 collision | **single (operator-eye)** | A–E |

**Ordering:** A first (spine — inert without a consumer, so A lands schema+validator+Gary-seam+one proof together). Then B; C, D, E parallelize after their deps; F is confirmation. **MVP = Leg A proves the library end-to-end on one real run.**

**Roster (to reconcile at Leg F):** Dan's 6 (density-low / Studio-2nd-template / 9:16-vertical / scripted-high / photo-art-style / brand-binding) ∩ Gary's 6 (Studio-full-bleed / photorealistic / 3D / abstract / text-forward-noImages / alt-dimension). Strong overlap on Studio-second, photo, and alt-dimension; CD reconciles the final six at Leg F.

---

## Forks surfaced to operator (party recommendation; operator authority overrides)

These touch features the operator called "critical," so they are flagged rather than silently adopted:

- **F1 — `scripted` scope.** John pushed to cut the open-ended channel to a lone `min_clusters` field. **Synthesis (adopted): keep the closed-vocabulary `scripted` block** (honors the operator's "channel for audible calls / code-fired triggers") but **wire exactly one class (`min_cluster_floor`) end-to-end in v1**; further classes (Gary's fallback/budget/sequencing/guard-threshold) ship as their seams appear, by party consensus. This reconciles the operator's intent with the no-backdoor guardrail. *Gary's evidence that ≥4 real non-declarative rules exist defeats John's "population of one" objection — the channel is justified.*
- **F2 — Picker + live-doc audit sequencing.** John argued both are fast-follows. **Synthesis (adopted): both stay IN this arc** (operator called them critical) as **later legs D/E**, MVP-sequenced — the library proves end-to-end at Leg A without them, then they layer on.
- **F3 — DONE-bar: 3 vs 8 styles.** **Synthesis (adopted): the HARD arc gate = mechanism-proven differential (Murat's no-vacuous-green) across the seeds + Classic/Studio dual-surface + ≥1 proven-fired `scripted` rule.** Growing to the full ~8 roster is the arc's expressiveness trajectory pursued in Leg F and tracked via the coverage-manifest, but the arc does not block on all 8 being live-perfect. Honors "add ~6" as the direction without coupling arc-close to 8 rounds of expensive live iteration.

---

## Operator decisions (2026-07-01, post-green-light — BINDING)

The operator ratified the synthesis with these decisions:

1. **Fork 3 = Option A.** Arc DONE-bar = **machinery proven** (library + validator/audit + Gary seam + `scripted` + picker, demonstrated producing faithful, differentiable output on the seed styles spanning ≥1 Classic + ≥1 Studio). Growing to the full ~8 roster continues **after** the arc's machinery gate, not as a blocker. Forks 1 & 2 adopted as framed (closed-vocab `scripted` with one class wired in v1; picker + live-doc audit both in-arc as later legs).

2. **Two-phase execution shape (binding):**
   - **PHASE 1 — machinery (autonomous, full BMAD spine).** Legs A–E: build + prove the library spine, the copacetic-quality audit (static validator + dependency enforcement + live-doc grounding), the Gary seam, the `min_cluster_floor` `scripted` class, and the HTML picker. The operator specifically requires a **reliable audit of the "copacetic" quality of the YAML AND the seed styles** as part of what "machinery proven" means. Phase-1 close = one live differential proof (two seed styles → measurably different Gamma output, Classic+Studio spanning).
   - **PHASE 2 — interactive roster growth (operator + Marcus, conversational).** Leg F reframed: grow the ~6 additional styles via **short experimental runs that produce Gammas and terminate at Storyboard B only** (never Descript assembly), refining each style's library representation interactively with the operator as Marcus. Not autonomous — Marcus-mediated.

3. **🔑 REMOVE baked-in generation-time overrides (binding, Phase-1 / Leg A).** The code currently forces settings regardless of the library (e.g. the unconditional Classic-branch `cardOptions.dimensions=16x9` from `27309271`). **These must be removed so the styleguide library config is the SOLE determinant of what Gamma produces — a pure representation, nothing masked by code.** Requirements:
   - **Inventory** every baked-in generation-time override the code applies (16:9 is the known one; audit `gary/_act.py` + `gamma_client.py` for others) and remove/relocate them so the resolved styleguide record is authoritative.
   - The library's `dimensions` field (fluid / 16x9 / 9x16 / …) alone controls card dimensions; a `fluid` style renders fluid, a `16x9` style renders 16:9 — no forcing.
   - **Preserve the anti-cropping OUTCOME, don't regress it:** the 16:9 forcing existed to fix Descript strict-16:9 title-cropping (Leg-4 finding (a)). Relocate that safety to the **publication boundary** (a publication-time policy or an operator/style choice), filed as a follow-on. Phase-2 runs stop at Storyboard B (pre-Descript), so removal is safe for the proof loop; only future Descript-bound production runs need the publication-boundary safety.
   - This completes §7's original intent ("16:9 down-payment … commented as superseded by the library default-guide") and is prerequisite to a faithful Phase-1 differential proof — an override that masks the library's dimensions makes "pure representation" impossible.

### Revised phase mapping of the legs

| Leg | Phase |
|---|---|
| A — Library spine + validator + Gary seam + **override removal** + seeds + live differential proof | **Phase 1** |
| B — Dependency enforcement (copacetic-quality, documented rules + learned store) | **Phase 1** |
| C — `min_cluster_floor` scripted class → Irene, 07G-gated | **Phase 1** |
| D — HTML style-picker + CD-entry gate (used to drive Phase-2 selection) | **Phase 1** |
| E — Live-doc audit + `gamma_docs` provider (keeps copacetic-quality current) | **Phase 1** |
| F — Roster growth to ~8, Storyboard-B-terminating experimental runs | **Phase 2 (interactive w/ Marcus)** |

## Next step

Party green-light GRANTED + operator decisions folded. Proceed down the BMAD spine: **`bmad-create-story` on Leg A** — runtime-active `gamma-style-guides.yaml` schema + hermetic `validate_gamma_style_guides.py` write-gate (the copacetic-quality static audit) + Gary `styleguide:<name>` consumption seam (only `styleguide` → `GAMMA_SETTING_KEYS`, metadata-strip, surface-violation) + **removal of baked-in generation-time overrides (16:9 + inventory)** + CD authors seeds #1/#2 via envelope + ONE live differential proof (2 seeds, Classic+Studio, terminate at Storyboard B) + fold the coverage-manifest-parity hygiene fix. Dual-gate. Then RED-first dev → `bmad-code-review` → party CLOSE. Legs B–E follow (Phase 1); Leg F is the Phase-2 interactive loop.
