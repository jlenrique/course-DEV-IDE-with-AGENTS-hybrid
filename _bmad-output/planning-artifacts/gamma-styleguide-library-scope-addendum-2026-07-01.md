# Gamma Styleguide Library — Scope Addendum (operator, 2026-07-01)

**Purpose:** Extends the party-ratified briefing [`gamma-styleguide-library-briefing-2026-06-30.md`](gamma-styleguide-library-briefing-2026-06-30.md) (§7 RATIFY 5/5) with **three operator-mandated additions** + the **proof/refinement workflow** for the arc opened on branch `dev/gamma-styleguide-library-2026-07-01`. This is the input to the arc GREEN-LIGHT party round. Guardrail: PRODUCT-VALID — controls what the Marcus-SPOC runtime exports for real decks ([[feedback_spoc_is_goal_not_concierge_proofing_runs]]).

The §7-ratified core (CD-owned SSOT `state/config/gamma-style-guides.yaml`; ≥4 named guides ≥1 Classic + ≥1 Studio; author-and-persist ownership; discriminated-union `production_mode`; strangler-fig migration; Gary `styleguide:<name>` consumption seam; validator write-gate; picker→library learning loop) **stands unchanged**. The additions below layer onto it.

---

## Addition ① — Styleguide AUDIT capability

**What:** An audit that verifies (a) the styleguide YAML's **structure + data** are copacetic, and (b) its **supporting files/documents** (companion field-control doc, narrative descriptions, brand-bible linkage, thumbnails/example refs) are coherent and present.

**Source of truth = FRESH LIVE READS, not stale enums.** The audit grounds its field-legality + value-range checks in **direct, fresh reads of published/public Gamma user & developer guides** (and other authoritative resources as needed) — so the config is validated against what Gamma *actually* supports today, not a hardcoded snapshot that silently rots. This is a **Texas-retrieval-shaped** obligation (live external-doc fetch + normalization).

**Cross-field DEPENDENCY enforcement (the load-bearing part).** The audit looks for and enforces **configuration dependencies**: choosing value X in field A may *require* a specific Template, or *require* / *unlock* / *forbid* a value in field B that would otherwise be unavailable. Rule provenance is two-tier:
- **Documented rules** — explicit in Gamma docs (fetched fresh per above).
- **Learned rules** — discovered **through experience in real Gamma runs** (a run proves that combination X+Y fails, or that value Z silently requires Template T). These persist and accumulate → ties directly into the §7-ratified **picker→library learning loop** and BMAD memory sidecars.

**Cadence + ownership (party to finalize):** runs **at specified times** (candidates: session-START gate, pre-live-run gate, scheduled/cron, on-YAML-change hook), owned by **the appropriate agent**. Working lean for the party: **Texas** owns the fresh external-doc fetch (retrieval provider); **CD (Dan) / a `validate_gamma_style_guides.py`-class validator** owns dependency-rule enforcement + the copacetic-structure verdict. Final owner + cadence = a green-light decision.

**Relation to the §7 validator:** the §7 `validate_gamma_style_guides.py` (completeness/enum/discriminated-union write-gate) is the *static* precondition for CD write authority. This audit is a *superset/complement*: it adds live-doc-grounded legality, supporting-file coherence, and dependency-rule enforcement (documented + learned). Party to decide whether they're one component with modes or two.

---

## Addition ② — HTML style-picker MENU (Storyboard-A-analogous operator gate)

**What:** A published HTML menu from which the operator **picks the styleguide to apply to a particular run**, presented **right about when the CD agent enters the pipeline**. Directly analogous to **Storyboard A**: published to Git (the `jlenrique.github.io` publish pattern), a **radio-button** listing + a **submit button** that records the choice back into the run.

**Per-style listing row shows:**
- **Name** + **distinguishing field values** (the values that make this style identifiably different).
- Link to the style's **narrative description** (the human "what this style is/feels like" text each style carries).
- Link to a **live example** of the style in use (a real published Gamma deck URL).
- A **thumbnail** — one representative single Gamma screen for the style.
- A **`last_used` date**.

**Repository-design implication (binding on the schema):** because the HTML's **sole data source is the styleguide YAML**, the repository record must now carry, as **first-class fields**: `last_used` (date), thumbnail reference, live-example URL, narrative-description link/text, + any misc supporting data the HTML capability needs (e.g. display name, distinguishing-fields hint, ordering). The §7 schema must be extended to account for these before the picker can be built.

**Party to finalize:** the exact pipeline node/gate for the picker (identify the CD-entry seam; is it a new operator gate, or a fold into an existing G2-class gate?); single-select vs the A/B two-bind case (§4a binds TWO guides for an A/B run — does the picker support selecting an A and a B?); thumbnail **generation + refresh** mechanism (a real cached Gamma render per style; when regenerated); `last_used` write-back timing.

---

## Addition ③ — New per-style field `scripted` (imperative / non-declarative style channel)

**What:** A per-style repository field (`scripted`, or better name TBD by party) capturing style impact that is **NOT expressible** through any standard declarative surface — i.e. **not** an API field, page-setting, prompt-setup, chosen Template, or Theme. Examples the operator named:
- "This style requires **≥ N clusters** minimum" — telling an active run a floor.
- Other **"audible" calls** / **code-fired triggers**: conditions the code detects at runtime that then impose a style effect (a programmatic/imperative hook the run honors).

**Design implications for the party (substantial):**
- **Where the run reads it** — clustering floor touches Irene Pass-1 / the cluster model; other triggers may touch Gary, the compositor, or motion. Needs a defined consumption seam per trigger class.
- **Contract shape** — a constrained mini-vocabulary of trigger→effect rules (auditable, validatable), NOT arbitrary code. Must stay inside the fail-loud/validator regime and the "CD never mutates state/config" invariant.
- **Interaction with the audit (①)** — `scripted` rules are prime candidates for the *learned-dependency* store; the audit should validate them too.
- **Guardrail check** — every `scripted` effect must earn its place by improving the SPOC product, and must not become a backdoor that bypasses the declarative library's auditability.

---

## Proof / refinement WORKFLOW for the arc

**Corpus:** select **3 slides** to develop — likely from **Part 3** of the current course source material (party/operator to confirm the exact slugs).

**Loop:** an **iterative trial-refine cycle** — make a **fresh run per style, one style after another**, over the same 3 slides; use each run's real output to **refine that style's representation in the repository** (values, dependencies, narrative, `scripted` rules, thumbnail).

**Roster growth:** start from the **~2 seeded styles** (the §8 seed exemplars) and **add ~6 more → ~8 total**, deliberately **exercising the full range of expressiveness we can control** (Classic + Studio; distinct themes/art-styles/densities/dimensions/`scripted` behaviors). Final roster count + which 6 = a CD/party call, but the target is "~8, spanning the control range."

**Live-testing discipline (standing):** incremental live tests as each style/component lands — no mocks, real Gamma/Texas/CD; the final multi-style run is a confirmation, not first contact ([[feedback_incremental_live_testing_not_deferred]], [[feedback_no_mocks_real_live_apis]]).

---

## Open decisions routed to the GREEN-LIGHT party (not operator-picked)

1. **Arc decomposition** — legs/stories across: schema-extension (last_used/thumbnail/example/narrative/`scripted`), audit component(s), HTML picker + gate, `scripted` consumption seams, the trial-refine loop. Ordering + gate modes.
2. **Audit owner + cadence** + whether audit and the §7 validator are one component or two.
3. **Learned-dependency-rule persistence** — where/how learned rules are stored + fed back (memory sidecar? a `learned_dependencies` block in the YAML? both?).
4. **Picker gate placement** (CD-entry node) + A/B two-bind support + thumbnail generation/refresh + `last_used` write-back.
5. **`scripted` contract shape + consumption seams** per trigger class; validatability.
6. **Corpus** — confirm the 3 Part-3 slides; **roster** — confirm the ~6 additions to reach ~8.
7. **Team** — canonical core Winston/John/Murat (+Amelia at dev) + ≤2 specialists **Dan (CD)** + **Gary (Gamma)**; **Texas** likely needed as a third specialty for the live-fetch audit — party to confirm the ≤2 rule handling (Texas may join for the audit leg specifically).

**Pre-existing hygiene queued (from 2026-07-01 full-repo /harmonize, NOT arc-introduced; report `reports/dev-coherence/2026-07-01-1027/`):** import-linter C3 actually BROKEN (workbook_producer.graph→resume_api, `b914bb9e`); `test_coverage_manifest_json_schema_parity` stale `marcus/` vs `app/marcus/` path; motion v4.2-pack marker order; repo-wide ruff noise. Flag if any should fold into this arc.
