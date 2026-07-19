# Project Quality Scorecard

**What this is.** A project-specific, evidence-grounded quality assessment scored on a small set of dimensions that matter *for this project in particular* — not generic code metrics. Each dimension has a rubric, a current score with cited evidence, and a refresh cadence. The scorecard is **emitted into every production run's final report** (`run_summary.yaml::quality_scorecard`) and **refreshed regularly during development** (see §Cadence).

**How scoring works.** Scores are **rubric-based judgment grounded in mechanically-checkable signals** — not false-precision automation. An intelligent assessment (a review pass or a fully-spawned party round) evaluates the project against each dimension's criteria, cites evidence (code, flags, deferred-inventory entries, trial outcomes), and records a per-criterion level. A machine-readable block at the bottom of this file carries the current headline numbers so tooling can surface them; the prose is the authority.

**Dimensions.** (More will be added; each is a top-level ## section.)
1. **Dynamic Intelligence vs Determinism (DID)** — the balance this project most depends on.

---

## Dimension 1 — Dynamic Intelligence vs Determinism (DID)

> **Why this dimension is load-bearing for this project.** The product is a multi-agent content pipeline where LLM judgment ("dynamic intelligence") and compiled, reproducible machinery ("determinism") must each do exactly their job. Get the balance wrong and you either (a) starve the creative/pedagogical quality that is the whole point, or (b) let non-deterministic judgment leak into places that must be reproducible, auditable, and cheap-to-fail — which corrodes trust and burns money on paid walks. This dimension scores **how well the architecture, routines, and — especially — outcomes keep intelligence and determinism on the right sides of a fence.**

### 1.0 The fence (one rule)

**Intelligence authors meaning; determinism executes and proves.**
Dynamic judgment may invent, choose, or interpret — but only inside a **locked envelope**. Downstream may only **transform** that envelope. If something needs new judgment, it goes **back upstream through a gate**, not sideways in a paid node. (This is already how SPOC works: the LLM chats; the *human verdict* advances the engine. The rule extends that pattern to every specialist.)

North star:

```text
[Dynamic necks] → lock/digest → [Deterministic spine] → HIL → [Dynamic necks] → lock → …
```

Intelligence at the **necks**; machinery in the **bones**.

### 1.1 Where intelligence stays dynamic (the necks) — protect these

These necks earn LLM variance; making them deterministic would delete the product's quality:

| Neck | Why it stays dynamic |
|---|---|
| Operator + Marcus-SPOC | Intent, tradeoffs, "what is this lesson for?" |
| CD / styleguide / experience | Creative frame — one steerable surface |
| G0 enrichment + LO authoring | Semantic typing of source; what learners should leave knowing |
| Irene Pass-1 (plan / structure) | Instructional architecture, clustering judgment |
| Irene Pass-2 (narration) | Voice, pedagogy, VO↔content craft |
| Research detective (opt-in) | Claim posture, triage — not retrieval plumbing |
| Perception (07G) | "What is on this slide?" (LLM-first, deliberately) |
| HIL gates | Human is the final intelligence; cards present, they decide |

**Protected by:** digest-binding outputs (sha256 of plan / LOs / four-artifact lock), HIL-before-spend, fail-loud if a contribution is missing (Epic 41 pattern), and **never letting a downstream node re-interpret** what a neck decided.

### 1.2 Where determinism rules (the bones) — keep these LLM-free

If a node's job is **render, assemble, verify, route, or publish**, it must not call an LLM. It should consume a prior neck's locked artifact or pause for HIL:

| Band | Deterministic |
|---|---|
| Compose / freeze / resume | selection → composed graph → checkpointer |
| Texas dispatch plumbing | provider routing, schemas (judgment is *what* to fetch, not *how* HTTP works) |
| Motion plan (07D.5), compositor, workbook MD→DOCX | no LLM in the critical path |
| Enrique / Kling / Gamma transport | params from envelope; APIs are weather, not authors |
| Fidelity / coverage / UDAC | detectors + halt rules — intelligence proposes; machines refuse spend |
| HIL projectors / HUD / next_action | Epic 43: display is deterministic over card JSON |
| gh-pages publish | deterministic transport |

### 1.3 The three fence mechanisms (already trusted here)

1. **Lock points (irreversible necks).** After G0R / §04.55 lock / G3 four-artifact lock, downstream may only *execute*. New meaning → new gate or reject/redo upstream.
2. **Contribution contracts.** Each intelligent neck emits a typed, digest-bound contribution; every consumer is **READ-ONLY** on it; §06 builder fails closed if a contribution is missing. The growth path is making this **uniform** across every neck.
3. **Capability portfolio (live / fenced-dormant / retired).** Dynamic surfaces not on a re-witness cadence are fenced-dormant — still intelligent in design, not falsely "always on." Keeps intelligence from rotting into believed-green.

### 1.4 Anti-patterns (do NOT do)

- Don't "make Irene deterministic" by templating narration — that's where the quality lives (VO↔on-screen).
- Don't put intelligence in the runner ("smart recover"). Recover must be **dumb and honest**.
- Don't let conversation-space Marcus invent production meaning that bypasses the engine (the AM guardrail — keep it sacred).

### 1.5 Scoring rubric

Five criteria, each scored 0–4 (0 absent · 1 weak · 2 partial · 3 strong · 4 uniform/complete). Sum → /20, normalized to /100. Bands: **A** ≥90 · **B** 75–89 · **B−** 60–74 · **C** 40–59 · **D** <40.

| # | Criterion | What "4/4" looks like |
|---|---|---|
| C1 | **Neck placement** | Dynamic intelligence lives only at necks that earn variance; nothing template-flattened that shouldn't be. |
| C2 | **Bone determinism** | Every render/assemble/verify/route/publish node is LLM-free; no "determinism pretending to be intelligence" and no stray LLM in the spine. |
| C3 | **Fence enforcement — teeth ON by default** | Fidelity / coverage / UDAC fences are enforced by default on the production preset, not opt-in; intelligence is never *un*-fenced on a paid walk. |
| C4 | **Lock + contribution-contract discipline** | *Every* neck is digest-bound, its consumers READ-ONLY, and HIL-before-spend holds — uniformly, not mostly. |
| C5 | **Honesty + calibration of outcomes** | Every intelligent neck is calibrated (measured on fresh holdout, not resubstitution); capability tiers match produced reality; semantic-faithfulness gates FAIL, not merely WARN. |

**Outcome-weighted reading (for prioritization, not a separate score):** C3 and C2 most affect *paid walks*; C5 most affects *learner-trust claims*; C4 is the discipline that makes the rest durable.

### 1.6 Current assessment — score **65 / 100 (B−)** — "strong design, non-uniform enforcement"

*As of 2026-07-19. Baseline — first assessment.*

| Criterion | Score | Level | Basis |
|---|:---:|---|---|
| C1 Neck placement | **4/4** | strong | Architecture is right and live-proven: necks are correctly identified (Operator/SPOC, CD, G0/LO, Irene P1/P2, research-detective, perception, HIL); the product *already is* "intelligence at the necks." |
| C2 Bone determinism | **3/4** | strong | Most bones are LLM-free and proven (compose/freeze, motion planner `model_config_ref: null`, workbook producer no-LLM, Epic-43 deterministic projectors, gh-pages). **Gap:** Gary export title-match is *determinism pretending to be intelligence* (Leak 3), plus a few historical Gamma/export mixed edges. |
| C3 Fence enforcement (teeth ON) | **1/4** | weak | The fidelity / coverage / UDAC fences **exist but default OFF**; `--preset production` does not auto-enable them → intelligence runs *un*-fenced on paid walks unless opted in (Leak 1). Biggest single gap. |
| C4 Lock + contract discipline | **3/4** | strong | The pattern is live-proven (digest-binding, contribution contracts with §06 fail-closed, HIL-before-spend, Epic-41 fail-loud). **Gap:** not *every* intelligent neck has the same digest→READ-ONLY→HIL discipline — it's not yet uniform. |
| C5 Honesty + calibration | **2/4** | partial | Reading-path neck is *uncalibrated* (~0.071 primary-key on fresh holdout; the 0.93 is catalog-approach, not the built classifier — Leak 4); workbook semantic audit is **WARN-only, not FAIL** (Leak 2); capability tiers lag produced reality (Leak 5). |
| **Total** | **13/20 = 65** | **B−** | Strong architecture; enforcement, uniformity, and calibration are the gap. |

**The headline:** this project is **well past "halfway"** on the *architecture* — the fence exists and is live-proven where it defines the product. The score is held down not by a missing pattern but by **non-uniform enforcement**: teeth off by default, discipline not uniform across necks, and unclosed honesty/calibration debts.

#### Open leaks (the path from 65 → 90)

1. **[C3] Fidelity fence exists but is OFF by default (strongest).** Irene Pass-2 intelligence runs; the `narration ⊆ source` fail-loud gate does not unless opted in. Same for coverage/UDAC — mechanisms exist, default OFF; `--preset production` does not auto-enable. *Evidence:* `app/specialists/irene/graph.py` `narration_figure_fidelity_active()` defaults OFF (~L180–187); `coverage_gate_wiring.py` (~L71); `udac_wiring.py` header; deferred `leg4-narration-fidelity-gate-precision-before-flag-on` (false-positive over-block unsolved).
2. **[C5] Workbook semantic audit WARNs, doesn't gate.** Deterministic assembly can ship prose a heuristic flags as unsourced framing; production is not failed. *Evidence:* `app/specialists/_shared/source_fidelity_audit.py` `SEMANTIC_TRIPWIRE` = `mode: warn_only`, `gates_production: False`; deferred `braid-workbook-semantic-claim-citation-audit`.
3. **[C2] Gary export title-match: determinism pretending to be intelligence.** A spine step does judgment-shaped work (brief↔rendered page) with brittle string matching; a Gamma title reword fail-loud-pauses (correct honesty, wrong tool). *Evidence:* `app/specialists/gary/_act.py` `materialize_exported_slide_paths_by_title` raises `gamma.export.brief-unmatched` (~L1388–1408); deferred `gary-export-llm-brief-to-page-matcher` (hybrid: fuzzy first, LLM only on residue, bijection required, else loud halt).
4. **[C5] Reading-path / perception: intelligent neck without a closed calibration fence.** LLM-first is correct; the quality gate on the neck is not closed. *Evidence:* built classifier ~0.071 primary-key on fresh held-out; `reading-path-fresh-naive-holdout-pre-trial` owed before generalization claims.
5. **[C5] Capability ledger lag (governance honesty).** Front-door honesty *understates* produced reality (fail-safe, but declared reality drifts from produced). *Evidence:* `app/marcus/lesson_plan/bundle_catalog.py` workbook `tier="mechanism_only_never_produced"` — contradicted by live workbook MD+DOCX (trial `a940c5eb`, Epics 36–40 live gate); deferred `workbook-capability-tier-honesty-lag` (S-1); motion's `proven_regressed_repairable` likely stale the same way.

#### Not leaks anymore (closed — keep them closed)

| Item | Status |
|---|---|
| G0 raw YAML dump | Closed — `trial.py` `render_gate_content(..., "directive")`; Epic 43 |
| HIL allowlist of unrendered types | Emptied — `KNOWN_UNRENDERED_ALLOWLIST` empty after 43-9 |
| Workbook producer calling LLM | No LLM in workbook producer/enrichment (deterministic compose) |
| Motion planner as LLM node | Manifest `model_config_ref: null` / "deterministic, NO LLM" |

#### The discipline that raises the score (not just fixes)

Every time a component is hardened, ask: **"did we move judgment upstream into a locked artifact, or did we just delete judgment?"** Only the first preserves dynamic intelligence while buying determinism. Prioritization if forced to cut: **(1) and (3)** most affect paid walks; **(2) and (4)** most affect learner-trust; **(5)** is governance hygiene before it becomes believed-green in the *other* direction.

### Cadence (how this dimension stays honest)

- **Every production run:** `run_summary.yaml::quality_scorecard` carries the current headline score + per-run fence signals (e.g. `silent_bypass_events`, which fences were enabled for that run). Read it in the run's final report.
- **Every Class-S WRAPUP (Step 9):** review this scorecard for currency alongside the guides; refresh the assessment if the diff moved a criterion (a fence turned on, a leak closed, a neck calibrated).
- **Every epic retrospective:** re-score the affected criteria; record the trend (rising/flat/falling) so believed-green in either direction is caught.
- **Staleness ratchet:** `scripts/utilities/quality_scorecard.py --check` warns if the machine block's `as_of` is older than the threshold or malformed.

---

<!-- QUALITY-SCORECARD-MACHINE-BLOCK v2 — parsed by app/quality/scorecard.py (dimension_ref / did_score_ref) and scripts/utilities/quality_scorecard.py. Keep the fenced yaml below valid. The prose above is the authority; this mirrors the headline numbers for tooling. v2 (Story Q1.1): schema is dimension-agnostic — per-dimension rubric_version/as_of/as_verified + per-criterion {level, signal, evidence_ref} (score/max retained as the 0–4 reasoning trace). STRUCTURAL migration only: every value below is carried verbatim from v1. Q1.2 (post
code-review honesty rework) adds a per-criterion `derivation` field naming HOW the
level is justified — and it does NOT falsely mechanize a proxy:
  • C3 fence_enforcement is the ONLY purely-mechanical criterion (`derivation:
    signal-derived`): level == level_from_signal(fences_enabled_signal()) == weak, the
    env-INDEPENDENT production-preset posture (0/3 fences ON).
  • C2 bone_determinism and C4 lock_and_contract are `derivation: judgment-with-evidence`:
    their `signal` carries honest FACTS but those facts CANNOT mechanically certify the
    level — model_config_ref-nullness is a determinism PROXY (node 08 Irene Pass-2 is an
    LLM with a null ref), and runtime bypass detection is honestly `undetected`. The
    `level: strong` is a documented HUMAN judgment from the §1.6 durable basis
    (digest-binding + contribution contracts + HIL-before-spend + Epic-41 fail-loud for
    C4; the architecture for C2), NOT a signal claim. level_from_signal() for C2/C4
    returns a NON-clean value today (proxy/unverified) — the divergence is the honesty.
  • C1 neck_placement / C5 honesty stay `derivation: judgment`, signal:null (C5 = Q1.5).
The DID numbers are UNCHANGED (65/B-; strong/strong/weak/strong/partial); the rework
relabels justification, not the score. leak-count reader returns 0 today (open_leaks:5
stays hand-carried until Q1.5 tags the leaks — GL-14). The /100→Band reframe is Q1.5. -->

```yaml
schema: quality-scorecard/v2
as_of: 2026-07-19
dimensions:
  dynamic_intelligence_vs_determinism:
    label: Dynamic Intelligence vs Determinism
    # rubric_version pins the §1.5 rubric edition; as_of = prose last-edited,
    # as_verified = evidence last-re-checked. Equal at this baseline migration
    # (no new evidence checked); the split earns its keep in Q1.3/Q1.5.
    rubric_version: 1
    as_of: 2026-07-19
    as_verified: 2026-07-19
    score: 65
    max: 100
    band: "B-"
    band_note: "strong design, non-uniform enforcement"
    criteria:
      # Each criterion carries a `derivation`: signal-derived (level == the reader's
      # mechanical output), judgment-with-evidence (honest signal facts that CANNOT
      # certify the level — the level is a §1.6 human judgment), or judgment (no signal).
      neck_placement:
        level: strong
        derivation: judgment
        signal: null
        evidence_ref: "§1.6 C1 · Neck placement"
        score: 4
        max: 4
      bone_determinism:
        # JUDGMENT-with-evidence: model_config_ref-nullness is a determinism PROXY, not
        # proof (node 08 Irene Pass-2 is an LLM with a null ref) — the signal cannot
        # mechanically certify 'strong'. level_from_signal(bone_inventory_signal())
        # returns NON-clean ('unavailable') today; 'strong' is the §1.6 architecture
        # judgment. The mechanical signal can only DOWNGRADE on a detected boundary
        # breach (an LLM ref on a gate node).
        level: strong
        derivation: judgment-with-evidence
        signal:
          reader: app.quality.signals.bone_inventory_signal
          fact: >-
            49/52 manifest nodes carry model_config_ref:null (a determinism PROXY, not
            proof — see caveat); the config-ref-set roster (07G vision perception neck,
            07W.1/07W.3 workbook-writer seams) sits off every gate node
            (gates_all_model_config_ref_null=true).
          caveat: >-
            model_config_ref nullness does NOT prove determinism: Irene Pass-2 (id 08)
            and Irene Pass-1 gate nodes are LLMs with null refs; 07W.1/07W.3 carry a
            writer ref while deterministic stubs today. So this signal cannot award
            'strong' — it only flags a breach (an LLM ref on a gate). The strong is the
            §1.6 architecture judgment; the residual gap (Leak-3 Gary export
            determinism-pretending) is why it is 3/4, not 4/4.
        evidence_ref: "§1.6 C2 · Leak 3 (Gary export title-match); architecture judgment"
        score: 3
        max: 4
      fence_enforcement_default_on:
        # SIGNAL-DERIVED (purely mechanical): level == level_from_signal(
        # fences_enabled_signal()) — the env-INDEPENDENT production-preset posture is
        # 0/3 fences ON → weak. This is the one criterion the code fully owns.
        level: weak
        derivation: signal-derived
        signal:
          reader: app.quality.signals.fences_enabled_signal
          derived_level: weak
          fact: >-
            fidelity/coverage/UDAC gate fns are env-toggle default-OFF and --preset
            production sets none of their env keys; the signal is read env-INDEPENDENTLY
            (ambient shell cleared) → {fidelity:false, coverage:false, udac:false}
            (0/3 ON) → weak. Anti-drift: patching a gate fn ON flips exactly that key.
        evidence_ref: "§1.6 C3 · Leak 1 (fidelity/coverage/UDAC default-OFF)"
        score: 1
        max: 4
      lock_and_contract_discipline:
        # JUDGMENT-with-evidence: runtime bypass detection is honestly 'undetected'
        # (no detector wired) and digest_module_present_on_disk is file-existence only
        # (NOT proof of runtime wiring) — neither certifies a clean level.
        # level_from_signal(lock_contract_signal()) returns 'partial' today (undetected
        # can never award clean); 'strong' is the §1.6 judgment (digest-binding +
        # contribution contracts + HIL-before-spend + Epic-41 fail-loud, which do NOT
        # depend on runtime bypass-counting). The undetected runtime-bypass axis is a
        # known gap = part of why C4 is 3/4 not 4/4. The GL-8 enforcement pin is Q1.3.
        level: strong
        derivation: judgment-with-evidence
        signal:
          reader: app.quality.signals.lock_contract_signal
          fact: >-
            digest_module_present_on_disk=true (app/runtime/compiled_graph_digest.py
            exists — file-existence only, NOT proof it is runtime-wired);
            silent_bypass_events consumes Q1.4a run_summary fence_state, honest
            'undetected' with no run observed (never coerced to 0).
          caveat: >-
            'undetected' + file-existence cannot certify clean discipline; the
            mechanical derivation is NON-clean ('partial'). The 'strong' rests on the
            §1.6 durable basis (digest-binding, contribution contracts, HIL-before-spend,
            Epic-41 fail-loud), NOT on the runtime-bypass axis, which is a known gap.
        evidence_ref: "§1.6 C4 · lock + contribution-contract discipline (runtime-bypass axis undetected)"
        score: 3
        max: 4
      honesty_and_calibration:
        level: partial
        derivation: judgment
        signal: null
        evidence_ref: "§1.6 C5 · Leaks 2, 4, 5"
        score: 2
        max: 4
    # leak-count TRANSITIONAL (Q1.2 / GL-14): app.quality.signals.open_leak_count_signal
    # returns 0 today — 0 `did_leak:` tags exist in deferred-inventory.md yet. The
    # hand-carried open_leaks:5 stays until Q1.5 tags the 5 leaks; only then does the
    # reader override this value. Q1.2 deliberately does NOT overwrite open_leaks here.
    open_leaks: 5
    trend: baseline
```
