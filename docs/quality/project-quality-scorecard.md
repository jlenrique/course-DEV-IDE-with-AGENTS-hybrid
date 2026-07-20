# Project Quality Scorecard

**What this is.** A project-specific, evidence-grounded quality assessment scored on a small set of dimensions that matter *for this project in particular* — not generic code metrics. Each dimension has a rubric, a current score with cited evidence, and a refresh cadence. The scorecard is **emitted into every production run's final report** (`run_summary.yaml::quality_scorecard`) and **refreshed regularly during development** (see §Cadence).

**How scoring works.** Scores are **rubric-based judgment grounded in mechanically-checkable signals** — not false-precision automation. An intelligent assessment (a review pass or a fully-spawned party round) evaluates the project against each dimension's criteria, cites evidence (code, flags, deferred-inventory entries, trial outcomes), and records a per-criterion level. A machine-readable block at the bottom of this file carries the current headline numbers so tooling can surface them; the prose is the authority.

**Dimensions.** (More will be added; each is a top-level ## section.)
1. **Dynamic Intelligence vs Determinism (DID)** — the balance this project most depends on.
2. **Cost-efficiency (paid-walk discipline)** — whether paid walks are cost-disciplined, honest, and reproducibly attested.

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

### 1.6 Current assessment — Band **B−** — "strong design, non-uniform enforcement"

*As of 2026-07-19. Baseline — first assessment (`trend: baseline`; no prior snapshot yet in `docs/quality/scorecard-history.jsonl`).*

**Headline (read this first).**

- **Band: B−.** The architecture is right and live-proven — the fence exists and is enforced where it *defines* the product ("intelligence at the necks"). The Band is held down not by a missing pattern but by **non-uniform enforcement**: teeth off by default, discipline not uniform across necks, and unclosed honesty/calibration debts. *(The internal 13/20 → 65/100 sum is the arithmetic-pin reasoning trace below — not a false-precise headline number.)*
- **Trend: ▬ baseline.** First assessment; there is no prior snapshot to compare against, so the trend is `baseline` (computed from the history ledger, never painted).
- **Open leaks — ranked (5).** The path from B− toward A, ranked by outcome weight (paid-walk → learner-trust → governance). Each is tagged `did_leak: <slug>` in `_bmad-output/planning-artifacts/deferred-inventory.md`, so `open_leak_count_signal()` == 5 == the machine block's `open_leaks` (the leak-count honesty pin reconciles doc↔code). These 5 are the DID contribution to the shared project ranked-leak list (GL-13; Q1.4b's projector consumes it — today DID is the only contributor).

  1. **[C3] Fidelity fence exists but is OFF by default** — *Leak 1, paid-walk (strongest)* → `leg4-narration-fidelity-gate-precision-before-flag-on`
  2. **[C2] Gary export title-match: determinism pretending to be intelligence** — *Leak 3, paid-walk* → `gary-export-llm-brief-to-page-matcher`
  3. **[C5] Workbook semantic audit WARNs, doesn't gate** — *Leak 2, learner-trust* → `braid-workbook-semantic-claim-citation-audit`
  4. **[C5] Reading-path / perception neck uncalibrated — fresh-naive holdout OWED** — *Leak 4, learner-trust; cross-links Q3.4 (counted once, here)* → `reading-path-fresh-naive-holdout-pre-trial`
  5. **[C5] Capability ledger lag (governance honesty)** — *Leak 5, governance* → `workbook-capability-tier-honesty-lag`

  **A verification TODO, NOT a leak:** motion's `bundle_catalog.py` capability tier (`proven_regressed_repairable`) is *likely stale* the same way Leak 5's workbook tier was — but it is **unverified**, so it is an explicit **VERIFY** item (re-read the motion tier against live motion output), deliberately **excluded** from `open_leaks`.

**Per-criterion levels (0–4) — the reasoning trace under the Band.** The Band is the summary; these five judgments are the trace. Each carries `{level, signal, evidence_ref}`; where a mechanical signal exists, the level's derivation is named. The 0–4 scores roll up to the machine block's Σ = 13/20 = 65/100 (an internal arithmetic-pin trace the CLI/`did_score_ref` read — **not** a headline).

| Criterion | Level | Score | Signal / derivation | Evidence (enumerated + re-checkable) |
|---|---|:---:|---|---|
| C1 Neck placement | strong | 4/4 | judgment | **Enumerated neck→digest-binding set, each checkable against manifest/code:** the **G0R** lock, the **§04.55** lock, and the **G3** four-artifact lock (irreversible necks — downstream may only execute); per-neck **contribution digests** (typed, sha256-bound; §06 builder fails closed on a missing contribution); the compile-time content-addressed **`app/runtime/compiled_graph_digest.py`** substrate. Necks (Operator/SPOC, CD, G0/LO, Irene P1/P2, research-detective, 07G perception, HIL) are correctly identified and live-proven — the product *already is* "intelligence at the necks." |
| C2 Bone determinism | strong | 3/4 | judgment-with-evidence (`bone_inventory_signal`) | **Enumerated `model_config_ref` roster (52 nodes):** 49/52 carry `model_config_ref: null`; `gates_all_model_config_ref_null = true`. The **3 nodes carrying a non-null ref** are `07G` PNG-Grounded Vision Perception (the perception *neck* — correctly an LLM), plus `07W.1` + `07W.3` Workbook writer seams (writer ref; deterministic stubs today). **Proxy caveat (honest fact, NOT certification):** `model_config_ref`-nullness does **not** prove determinism — Irene Pass-2 (node `08`) and the Irene Pass-1 *gate* nodes are LLMs with a **null** ref; so the roster can only flag a *breach* (an LLM ref on a gate node), never award `strong`. The `strong` is the §1.6 architecture judgment; the residual gap — **Leak 3** (Gary export title-match determinism-pretending) — is why it is 3/4, not 4/4. |
| C3 Fence enforcement (teeth ON) | weak | 1/4 | signal-derived (`fences_enabled_signal`) | **Enumerated preset-fenced list on `--preset production` (read env-INDEPENDENTLY):** `{fidelity: OFF, coverage: OFF, udac: OFF}` — 0/3 fences wired ON → `weak` (== `level_from_signal(fences_enabled_signal())`; the fence-claim pin agrees doc↔code). The fidelity/coverage/UDAC fences *exist* but default OFF; the production preset auto-enables none → intelligence runs *un*-fenced on paid walks unless opted in. The single biggest Band-limiter — **Leak 1**. |
| C4 Lock + contract discipline | strong | 3/4 | judgment-with-evidence (`lock_contract_signal`) | Live-proven pattern: digest-binding, contribution contracts with §06 fail-closed, HIL-before-spend, Epic-41 fail-loud. Honest residual: the runtime silent-bypass axis is **`undetected`** (no detector wired) and `digest_module_present_on_disk` is file-existence only (not proof of runtime wiring) — so the *mechanical* derivation is NON-clean; the `strong` rests on the durable basis above, and non-uniformity across *every* neck is why it is 3/4, not 4/4. |
| C5 Honesty + calibration | partial | 2/4 | judgment | Three open honesty debts, all encoded in `partial`: reading-path neck **uncalibrated** (see the metric-citation below — **Leak 4**); workbook semantic audit is **WARN-only, not FAIL** (**Leak 2**); capability tiers **lag** produced reality (**Leak 5**). The level already encodes "reading-path uncalibrated + WARN-only + tier-lag." |

**Reading-path metric citation (Mary, binding — every reading-path number carries `(subject, substrate@date)`).** The only reading-path accuracy number that was actually **measured** is:

> **`subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23`: primary-key 0.071 (1/14)** — with full-tuple 0.0, macro 0.50, image_role 0.21, escalation 0.93 on the same run (per `_bmad-output/implementation-artifacts/p2-4b-honest-measurement-and-recalibration-2026-06-23.md`).

**⚠️ Two DISTINCT quantities both round to 0.93 — do NOT let one inherit the other's provenance.** The `0.93` in the blockquote is the **built-classifier ESCALATION rate** (≈0.929 — an *over*-escalation defect, not an accuracy). It is a *different quantity* from the frequently-cited catalog-approach **PRIMARY-KEY accuracy 0.93**. They are numerically coincidental; the accuracy of the built classifier is the **0.071** primary-key above, NOT either 0.93. Specifically: the frequently-cited **`0.93` accuracy was the *catalog-approach* (Claude-labelled) number — a DIFFERENT thing, NOT the built classifier.** Critically, the **fresh NAIVE holdout is OWED / UNMEASURED**: the 14 held-out slides were *consumed* (labelled) to produce the 0.071, so that number is a **resubstitution / upper-bound** on a non-naive dev set, not a generalization estimate — **no fresh-naive number has been measured, and none may be implied.** A fresh naive holdout (operator labels ≥12–15 NEW slides, scored in a separate gate) is REQUIRED before any trial-ready claim (Mary firm dissent against claiming trial-ready off the consumed-14). C5's reading-path evidence therefore reads: *"uncalibrated; built-classifier 0.071 resubstitution@2026-06-23; fresh-naive holdout OWED/unmeasured."* This is **Leak 4** and cross-links Q3.4 (calibration) — counted once, here.

#### Open leaks (detail — the path from B− toward A)

1. **[C3] Fidelity fence exists but is OFF by default (strongest).** Irene Pass-2 intelligence runs; the `narration ⊆ source` fail-loud gate does not unless opted in. Same for coverage/UDAC — mechanisms exist, default OFF; `--preset production` does not auto-enable. *Evidence:* `app/specialists/irene/graph.py` `narration_figure_fidelity_active()` defaults OFF (~L180–187); `coverage_gate_wiring.py` (~L71); `udac_wiring.py` header; deferred `leg4-narration-fidelity-gate-precision-before-flag-on` (false-positive over-block unsolved).
2. **[C5] Workbook semantic audit WARNs, doesn't gate.** Deterministic assembly can ship prose a heuristic flags as unsourced framing; production is not failed. *Evidence:* `app/specialists/_shared/source_fidelity_audit.py` `SEMANTIC_TRIPWIRE` = `mode: warn_only`, `gates_production: False`; deferred `braid-workbook-semantic-claim-citation-audit`.
3. **[C2] Gary export title-match: determinism pretending to be intelligence.** A spine step does judgment-shaped work (brief↔rendered page) with brittle string matching; a Gamma title reword fail-loud-pauses (correct honesty, wrong tool). *Evidence:* `app/specialists/gary/_act.py` `materialize_exported_slide_paths_by_title` raises `gamma.export.brief-unmatched` (~L1388–1408); deferred `gary-export-llm-brief-to-page-matcher` (hybrid: fuzzy first, LLM only on residue, bijection required, else loud halt).
4. **[C5] Reading-path / perception: intelligent neck without a closed calibration fence.** LLM-first is correct; the quality gate on the neck is not closed. *Evidence (metric-cited):* the built classifier scored **primary-key 0.071 (`subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23`)** — a **resubstitution / upper-bound** on the 14 held-out slides that were *consumed* to produce it (per the metric-citation in §1.6 above). The `0.93` cited elsewhere was the *catalog-approach* (Claude-labelled) number, **not** the built classifier. A **fresh-naive holdout is OWED / UNMEASURED** before any generalization or trial-ready claim — **no fresh-naive number has been measured or may be implied.** Deferred `reading-path-fresh-naive-holdout-pre-trial` (cross-links Q3.4).
5. **[C5] Capability ledger lag (governance honesty).** Front-door honesty *understates* produced reality (fail-safe, but declared reality drifts from produced). *Evidence:* `app/marcus/lesson_plan/bundle_catalog.py` workbook `tier="mechanism_only_never_produced"` — contradicted by live workbook MD+DOCX (trial `a940c5eb`, Epics 36–40 live gate); deferred `workbook-capability-tier-honesty-lag` (S-1). **VERIFY (not a leak):** motion's `proven_regressed_repairable` tier is *likely stale* the same way — an explicit verification TODO (re-read the motion tier against live motion output), deliberately **NOT** counted in `open_leaks`.

#### Not leaks anymore (closed — keep them closed)

| Item | Status |
|---|---|
| G0 raw YAML dump | Closed — `trial.py` `render_gate_content(..., "directive")`; Epic 43 |
| HIL allowlist of unrendered types | Emptied — `KNOWN_UNRENDERED_ALLOWLIST` empty after 43-9 |
| Workbook producer calling LLM | No LLM in workbook producer/enrichment (deterministic compose) |
| Motion planner as LLM node | Manifest `model_config_ref: null` / "deterministic, NO LLM" |

#### The discipline that raises the Band (not just fixes)

Every time a component is hardened, ask: **"did we move judgment upstream into a locked artifact, or did we just delete judgment?"** Only the first preserves dynamic intelligence while buying determinism. Ranked if forced to cut: **Leaks 1 and 3** most affect paid walks; **Leaks 2 and 4** most affect learner-trust; **Leak 5** is governance hygiene before it becomes believed-green in the *other* direction.

### Cadence (how this dimension stays honest)

- **Every production run:** `run_summary.yaml::quality_scorecard` carries the current headline score + per-run fence signals (e.g. `silent_bypass_events`, which fences were enabled for that run). Read it in the run's final report.
- **Every Class-S WRAPUP (Step 9):** review this scorecard for currency alongside the guides; refresh the assessment if the diff moved a criterion (a fence turned on, a leak closed, a neck calibrated).
- **Every epic retrospective:** re-score the affected criteria; record the trend (rising/flat/falling) so believed-green in either direction is caught.
- **Staleness ratchet (SECONDARY nag, not the honesty guard):** `scripts/utilities/quality_scorecard.py --check` warns if the machine block's `as_of` is older than the threshold or malformed. It only checks *age*, never whether the claims still match the code. The anti-believed-green **honesty guard** is `tests/quality/test_scorecard_honesty_pins.py` — pins that FAIL when a machine-block claim contradicts a code-computed reality (fence level vs the signal reader, `open_leaks` vs the counted `did_leak:` tags, score↔level↔band↔sum, `trend` vs computed-from-history).
- **Trend history is an append-only ledger** at `docs/quality/scorecard-history.jsonl`: every scorecard edit MUST append (new `as_of`) or update-in-place (same-day) a snapshot mirroring the machine block, and any score INCREASE must advance `as_verified` and cite fresh evidence (the pins enforce all three). **Honest residual (stated plainly):** this ledger records a *judgment history*, not observed system state — the pins cannot mechanically detect a *coordinated* fabrication of BOTH the doc and the ledger in one edit. That last gap is a review/governance concern, not a mechanical guarantee.

---

## Dimension 2 — Cost-efficiency (paid-walk discipline)

> **Why this dimension is load-bearing for this project.** Every production run spends real money on paid LLM walks. Two failure modes corrode trust and burn budget: (a) a paid walk runs **un-capped** — nothing stops spend when a run goes wrong; and (b) the reported cost is **not honest** — a lower-bound estimate reads as an exact figure, or drift/attribution is invisible. This dimension scores **whether paid walks are cost-disciplined (a real brake that actually stops spend), cost-honest (the reported posture never over-claims exactness), and reproducibly attested (per-agent / per-model breakdown + config digests so a run's cost can be re-derived).** It is scored from the EXISTING economics emitters — `app/runtime/economics.py` (`check_trial_budget`, `compute_per_agent_drift`) and the `cost_posture` on `app/models/runtime/trial_economics_report.py` — with no parallel plumbing.

### 2.0 The rule (one line)

**A paid walk must be brake-able, cost-honest, and reproducibly attested — and the brake must be ON by default, not opt-in.** Telemetry that only *reports* after the spend is transparency, not discipline; discipline is a stop that fires *before* the money is gone.

### 2.5 Scoring rubric

Four criteria, each scored 0–4 (0 absent · 1 weak · 2 partial · 3 strong · 4 uniform/complete). Sum → /16, normalized to /100. Bands: **A** ≥90 · **B** 75–89 · **B−** 60–74 · **C** 40–59 · **D** <40 (shared with §1.5).

| # | Criterion | What "4/4" looks like |
|---|---|---|
| CE1 | **Budget-stop default posture** | The dollar brake is wired **ON by default** on the production preset — a paid walk is cost-fenced without the operator opting in. |
| CE2 | **Cost-posture honesty** | The reported cost is `exact`, or an explicitly-declared lower-bound floor with a counted set of unavailable attempts; the posture can never over-claim exactness. |
| CE3 | **Per-agent drift monitoring** | Rolling-median per-agent drift is monitored on every trial and (at 4/4) gates, not merely warns. |
| CE4 | **Cost transparency** | Per-agent + per-model breakdown + cascade/pricing digests give a fully reproducible, auditable cost attestation. |

**Outcome-weighted reading (for prioritization, not a separate score):** CE1 most affects *paid walks* (an un-capped walk is the direct money risk); CE2 and CE4 most affect *learner/operator-trust* in the reported numbers; CE3 is the discipline that catches cost regressions before they compound.

### 2.6 Current assessment — Band **B−** — "real economics telemetry; budget brake opt-in on paid walks"

*As of 2026-07-19. Baseline — first assessment (`trend: baseline`; first `cost_efficiency` snapshot in `docs/quality/scorecard-history.jsonl`).*

**Headline (read this first).**

- **Band: B−.** The economics substrate is genuinely strong — cost is honestly posture-tagged (a lower-bound can never masquerade as exact), per-agent drift is monitored against a rolling median, and every trial carries a reproducible per-agent/per-model + digest attestation. The Band is held down by **one honest gap: the dollar brake is a REAL Epic-41 enforced stop *when set*, but it is OPT-IN — the production preset wires no default budget, so `check_trial_budget(total, None)` returns `no-cap` and the default paid walk runs un-capped.** *(The internal 10/16 → 62/100 sum is the arithmetic-pin reasoning trace below — not a false-precise headline number.)*
- **Trend: ▬ baseline.** First `cost_efficiency` assessment; no prior snapshot, so the trend is `baseline` (computed from the history ledger, never painted).
- **Open leaks — ranked (1).** One paid-walk leak; tagged `cost_leak: cost-efficiency-budget-stop-opt-in-default-no-cap` in the `## Cost-Efficiency Scorecard Leak Registry` of `_bmad-output/planning-artifacts/deferred-inventory.md`, so `cost_leak_count_signal()` == 1 == the machine block's `open_leaks` (the cost leak-count + slug-identity pins reconcile doc↔registry). This is the cost_efficiency contribution to the shared project ranked-leak list (GL-13; it interleaves with DID's paid-walk leaks by lane priority).

  1. **[CE1] Budget-stop is a real enforced brake but OPT-IN by default** — *Leak 1, paid-walk* → `cost-efficiency-budget-stop-opt-in-default-no-cap`

**⚠️ Headline caveat — do NOT read B− as adequate pre-spend cost discipline (equal-weight scoring, honest reading).** This dimension is scored equal-weight (consistent with §1's DID model — no weighted scoring here). But the §2.0 thesis is that *discipline is a stop that fires **before** the money is gone; telemetry after the spend is transparency, not discipline.* Three of the four criteria (CE2 posture-honesty, CE3 advisory-drift, CE4 report-time-transparency) are explicitly **post-spend** and each scores strong; the ONE **pre-spend** criterion — CE1, the actual brake and the thesis — is **weak (opt-in)**. So the B− is **lifted by post-spend telemetry while the pre-spend brake is weak**: read it as "excellent cost *honesty/transparency*, but paid walks are **not** cost-*disciplined* by default," NOT as "cost discipline is decent." (This is the "outcome-weighted reading" below, elevated to the headline so it cannot be missed.)

**Say it plainly (honesty is the bar).** The Epic-41 dollar brake (`MARCUS_TRIAL_BUDGET_USD` → the `check_trial_budget` SSOT, enforced at both walks' dispatch chokepoint — Story 41-4) is a **real economic stop when a budget is set** — it is not absent, and this assessment does not understate it. But the production preset defines **no default-budget source**, so by default the brake never fires (`no-cap`). That is the DID-C3 pattern — a mechanism that exists but is default-OFF — and it is why CE1 is **weak**, not absent and not strong. **Weak (1) vs partial (2) is a deliberate DID-C3-consistent conservative call:** the brake is *fully* enforced when set (both walks, pre- + post-spend chokepoints), so "partial" is arguable — but the criterion scores the *default* posture, which is entirely off, so it is scored `weak` (1) to mirror DID-C3 `fence_enforcement_default_on` (also 1 for a default-off-but-real mechanism) and to err conservative, not as an oversight. The assessment does **not** claim "cost-fenced": the default paid walk is not budget-fenced.

**Per-criterion levels (0–4) — the reasoning trace under the Band.** Each carries `{level, signal, evidence_ref}`; where a mechanical signal exists, the level's derivation is named. The 0–4 scores roll up to the machine block's Σ = 10/16 = 62/100 (an internal arithmetic-pin trace — **not** a headline).

| Criterion | Level | Score | Signal / derivation | Evidence (enumerated + re-checkable) |
|---|---|:---:|---|---|
| CE1 Budget-stop default posture | weak | 1/4 | signal-derived (`budget_stop_default_signal`) | **Env-INDEPENDENT production-preset posture:** `MARCUS_TRIAL_BUDGET_USD` unset → `_resolve_preset_default_budget()` == `None` → `check_trial_budget(1.0, None).state` == `no-cap` → `default_budget_enforced` == `False` → `weak` (== `level_from_signal("budget_stop_default_on", budget_stop_default_signal())`; the fence-claim pin agrees doc↔code). The brake EXISTS and is enforced *when set* (Epic-41 / Story 41-4, both walks' dispatch chokepoint) but is OPT-IN by default. Anti-drift: seeding a default cap flips `default_budget_enforced` True → the derived level would be `strong`. This is **Leak 1**. |
| CE2 Cost-posture honesty | strong | 3/4 | judgment-with-evidence (`cost_posture_signal`) | `cost_posture` ∈ `{exact, known-lower-bound-with-explicit-unavailable-attempts}` with `unavailable_attempt_count`; the model validator on `TrialEconomicsReport` **forbids** `exact` when `unavailable_attempt_count > 0`, so a lower-bound posture is an honestly-declared **floor** and the posture cannot lie. Residual (why 3/4, not 4/4): a lower-bound posture (when it occurs) *is* a floor, not exact — an honest honesty-gap; the mechanism cannot certify "always exact". |
| CE3 Per-agent drift monitoring | strong | 3/4 | judgment-with-evidence (`cost_drift_signal`) | `compute_per_agent_drift` (`app/runtime/economics.py:362`) computes a rolling 5-trial median and raises a `DriftAlert` on a ≥50% per-call deviation; alerts ride the trial economics report (`drift_alerts`). Monitoring is wired end-to-end. Residual (why 3/4): drift needs ≥5 history to fire (cold-start blind) and is **advisory** (informational, not a spend gate). |
| CE4 Cost transparency | strong | 3/4 | judgment-with-evidence (`cost_transparency_signal`) | The report carries `per_agent_breakdown` + `per_model_breakdown` + 64-hex `cascade_config_digest` + `pricing_table_digest` — a reproducible cost attestation (a run's cost can be re-derived and audited). Residual (why 3/4): transparency is report-time, **not** a live spend fence. |

#### Open leaks (detail — the path from B− toward A)

1. **[CE1] Budget-stop is a real enforced brake but OPT-IN by default (paid-walk).** The dollar brake fires only when the operator sets `MARCUS_TRIAL_BUDGET_USD`; the production preset defines no default-budget source, so the default paid walk is un-capped (`check_trial_budget(total, None)` → `no-cap`). **Closing it needs runtime substrate, not just a doc bump:** the runtime's only budget source today is that one env var (`_resolve_trial_budget_usd` reads it live; there is no preset/config default). The close-path = ADD a preset-default budget source the runtime resolver returns (the preset sets a sensible default, or the resolver grows a preset-config cap) — at which point CE1's `budget_stop_default_signal` (which delegates to that resolver source, `_resolve_runtime_default_budget`) reports `default_budget_enforced=True` and the criterion earns `strong`. The reader is not a hardcoded constant: the seeded-override test proves its level logic reaches `strong` on a real resolved cap; only the substrate that feeds a real preset-default is deferred. *Evidence:* `app/runtime/economics.py:347` (`check_trial_budget` → `no-cap` when budget None); `app/marcus/orchestrator/production_runner.py:3535` (`_resolve_trial_budget_usd` → `None` when unset; env-only, no preset/config default) + `:3597` (the enforced dispatch chokepoint, Story 41-4); registry `cost-efficiency-budget-stop-opt-in-default-no-cap`.

#### The discipline that raises the Band (not just fixes)

Every time cost telemetry is added, ask: **"did we add a stop that fires *before* the spend, or only a nicer *report* after it?"** Only the first raises CE1/CE3 toward gating discipline. Ranked if forced to cut: **Leak 1** (CE1) is the one paid-walk money risk; CE2/CE4 are trust-in-the-numbers (already strong); CE3 becomes a fence, not just a monitor, at 4/4.

### Cadence (how this dimension stays honest)

- **Every production run:** the per-run `cost_posture` fact already rides Q1.4a's `fence_state` in `run_summary.yaml`; read it in the run's final report alongside the Band.
- **Every Class-S WRAPUP (Step 9):** review this dimension for currency — if a default budget gets wired (CE1 → strong), if drift is promoted to a gate (CE3 → 4/4), or if a lower-bound posture recurs, refresh the assessment.
- **Every epic retrospective:** re-score the affected criteria; record the trend so believed-green in either direction is caught.
- **Honesty guard:** `tests/quality/test_scorecard_honesty_pins.py` (the `cost_efficiency` pins — budget-fence-claim, cost leak-count + slug-identity, score-arithmetic) + `tests/quality/test_cost_efficiency_dimension.py` (the signal readers + drift math + RED-under-seeded proofs) FAIL when a machine-block claim contradicts a code-computed reality. The **budget-fence-claim pin** reds if CE1 is bumped to `strong` without a default budget actually wired (GL-9).

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
relabels justification, not the score. Q1.5 LANDED: the 5 `did_leak:` tags now exist in
deferred-inventory.md so open_leak_count_signal() == 5 == open_leaks (the leak-count
pin is now a HARD reconciliation, not xfail); §1.6 is reframed Band-primary
(ranked-leaks + trend) with the /100 sum kept as the arithmetic-pin reasoning trace. -->


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
    # leak-count RECONCILED (Q1.5 / GL-14): app.quality.signals.open_leak_count_signal
    # now returns 5 — the 5 `did_leak:` tags landed in deferred-inventory.md (one per
    # ranked DID leak). open_leaks:5 == the counted tags, so the leak-count honesty pin
    # is a HARD doc↔code reconciliation (Q1.3's xfail(strict) was removed by Q1.5).
    open_leaks: 5
    # STRUCTURED leak list (Q1.4b / GL-13). Machine-readable mirror of the §1.6
    # "Open leaks — ranked (5)" headline + the `## DID Scorecard Leak Registry`
    # slugs. Each entry: {rank, criterion, slug, lane}. `rank` = the §1.6 ranked
    # display position (1–5, already ordered by lane priority paid-walk →
    # learner-trust → governance, then the original leak number). `criterion` is
    # the §1.6 C-label; `lane` ∈ paid-walk / learner-trust / governance.
    # ADDITIVE: len(leaks) == open_leaks == open_leak_count_signal() == 5. The
    # mirror honesty pin mirrors {score,band,levels,open_leaks,as_of,as_verified}
    # — NOT `leaks` — so this addition does not touch it. app.quality.report.
    # ranked_project_leaks aggregates EVERY dimension's `leaks` into ONE shared
    # cross-dimensional project ranked-leak list (DID is the sole contributor
    # today; Q2/Q3 dimensions MUST add their own `leaks` list to register — see
    # docs/dev-guide/quality-scorecard-dimension-authoring.md).
    leaks:
      - rank: 1
        criterion: C3
        slug: leg4-narration-fidelity-gate-precision-before-flag-on
        lane: paid-walk
      - rank: 2
        criterion: C2
        slug: gary-export-llm-brief-to-page-matcher
        lane: paid-walk
      - rank: 3
        criterion: C5
        slug: braid-workbook-semantic-claim-citation-audit
        lane: learner-trust
      - rank: 4
        criterion: C5
        slug: reading-path-fresh-naive-holdout-pre-trial
        lane: learner-trust
      - rank: 5
        criterion: C5
        slug: workbook-capability-tier-honesty-lag
        lane: governance
    trend: baseline
  cost_efficiency:
    # Dimension 2 (Story Q2.1) — Cost-efficiency / paid-walk discipline, scored from
    # the EXISTING economics emitters (GL-15 reuse; NO parallel plumbing). The §2 prose
    # is the authority; this mirrors the headline numbers. Honest baseline: the Epic-41
    # dollar brake (MARCUS_TRIAL_BUDGET_USD → check_trial_budget) is a REAL enforced stop
    # WHEN SET but OPT-IN by default (production preset sets no default budget →
    # check_trial_budget(total, None)=='no-cap') — the DID-C3 pattern (mechanism exists,
    # default OFF) → a cost-efficiency LEAK on the paid walk. Cost_posture honesty, drift
    # monitoring, and cost transparency are real strengths.
    label: Cost-efficiency
    rubric_version: 1
    as_of: 2026-07-19
    as_verified: 2026-07-19
    score: 62
    max: 100
    band: "B-"
    band_note: "B- is lifted by post-spend telemetry (posture/drift/transparency strong); the PRE-SPEND brake (CE1, the thesis) is weak/opt-in — do NOT read B- as adequate pre-spend cost discipline"
    criteria:
      budget_stop_default_on:
        # SIGNAL-DERIVED (purely mechanical, mirrors DID C3): level ==
        # level_from_signal(budget_stop_default_signal()). The reader delegates to the
        # runtime's OWN budget source (_resolve_runtime_default_budget — the same
        # MARCUS_TRIAL_BUDGET_USD the runtime resolver reads); the production preset
        # defines no default-budget source → resolver None → check_trial_budget(total,
        # None)=='no-cap' → default_budget_enforced=False → weak. NOT a hardcoded
        # constant: when the preset gains a default-budget source the resolver returns,
        # the reader detects it and this earns strong (close-path needs that substrate;
        # the seeded-override test proves the level logic reaches strong on a real cap).
        # The pin reads the preset-default posture (ambient operator opt-in cleared in-
        # test), read-only (no os.environ mutation).
        level: weak
        derivation: signal-derived
        signal:
          reader: app.quality.signals.budget_stop_default_signal
          derived_level: weak
          fact: >-
            the production preset defines no default-budget source, so the runtime budget
            resolver returns None and check_trial_budget(total, None)=='no-cap' → the
            Epic-41 dollar brake (enforced at both walks' dispatch chokepoint WHEN SET) is
            OPT-IN by default (default=no cap). This is the DID-C3 pattern (mechanism
            exists, default OFF) → the paid-walk cost leak below. Closing it needs runtime
            substrate (a preset-default budget source the resolver returns), at which point
            this reader detects it and the derived level becomes strong.
        evidence_ref: "§2.6 CE1 · Cost Leak (budget-stop opt-in, default no-cap)"
        score: 1
        max: 4
      cost_posture_honesty:
        # JUDGMENT-with-evidence: the cost_posture Literal + unavailable_attempt_count +
        # the model validator (which FORBIDS claiming 'exact' when attempts were
        # unavailable) make the reported cost honestly exact-or-a-declared-floor. The
        # signal carries that fact; the level is a §2.6 human judgment (a per-run posture
        # is exact OR a floor — the mechanism cannot mechanically certify 'always exact').
        level: strong
        derivation: judgment-with-evidence
        signal:
          reader: app.quality.signals.cost_posture_signal
          fact: >-
            cost_posture ∈ {exact, known-lower-bound-with-explicit-unavailable-attempts}
            with unavailable_attempt_count; the model validator forbids 'exact' when
            unavailable_attempt_count>0, so a lower-bound posture is a HONEST floor and
            the posture cannot lie.
          caveat: >-
            a lower-bound posture (when it occurs) = the reported cost is a FLOOR, not
            exact — an honest honesty-gap; the mechanism cannot certify 'always exact',
            so 'strong' is a §2.6 judgment (3/4, not 4/4).
        evidence_ref: "§2.6 CE2 · cost_posture honesty (exact vs declared floor)"
        score: 3
        max: 4
      cost_drift_monitoring:
        # JUDGMENT-with-evidence: compute_per_agent_drift (rolling 5-trial median; a
        # >=50% per-call deviation → a DriftAlert) is wired and emits into the report.
        # The signal reports monitoring-wired + a report's alert count; 'strong' is a
        # §2.6 judgment. Residual (why 3/4): drift needs >=5 history to fire and is
        # ADVISORY (informational, not a spend gate).
        level: strong
        derivation: judgment-with-evidence
        signal:
          reader: app.quality.signals.cost_drift_signal
          fact: >-
            compute_per_agent_drift computes a rolling 5-trial median and raises a
            DriftAlert on a >=50% per-call deviation; alerts ride the trial economics
            report (drift_alerts). Monitoring is wired end-to-end.
          caveat: >-
            drift needs >=5 history to fire (cold-start blind) and is ADVISORY
            (informational, not a spend gate) — why 'strong' is 3/4, not 4/4.
        evidence_ref: "§2.6 CE3 · per-agent drift monitoring (rolling-median advisory)"
        score: 3
        max: 4
      cost_transparency:
        # JUDGMENT-with-evidence: per_agent_breakdown + per_model_breakdown +
        # 64-hex cascade_config_digest + pricing_table_digest = a reproducible cost
        # attestation. The signal reports per-field presence; 'strong' is a §2.6
        # judgment. Residual (why 3/4): transparency is report-time, not a live fence.
        level: strong
        derivation: judgment-with-evidence
        signal:
          reader: app.quality.signals.cost_transparency_signal
          fact: >-
            the trial economics report carries per_agent_breakdown, per_model_breakdown,
            and 64-hex cascade_config_digest + pricing_table_digest — a reproducible
            cost attestation (a run's cost can be re-derived and audited).
          caveat: >-
            transparency is report-time (a reproducible attestation), NOT a live spend
            fence — why 'strong' is 3/4, not 4/4.
        evidence_ref: "§2.6 CE4 · cost transparency (reproducible attestation)"
        score: 3
        max: 4
    # ONE open leak: the budget brake is OPT-IN by default (default no-cap) on paid
    # walks. Counted (line-anchored) as `cost_leak:` in the `## Cost-Efficiency
    # Scorecard Leak Registry` of deferred-inventory.md — a SEPARATE per-dimension
    # namespace from `did_leak:` (so the two counts never collide). len(leaks) ==
    # open_leaks == cost_leak_count_signal() == 1 (the cost leak-count + slug-identity
    # pins reconcile doc↔registry).
    open_leaks: 1
    leaks:
      - rank: 1
        criterion: CE1
        slug: cost-efficiency-budget-stop-opt-in-default-no-cap
        lane: paid-walk
    trend: baseline
```
