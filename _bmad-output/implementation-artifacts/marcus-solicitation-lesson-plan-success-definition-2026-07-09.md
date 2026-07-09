# SUCCESS DEFINITION — Marcus-driven solicitation → lesson plan
## Measurable live-test output assets (party-bound)
**Date:** 2026-07-09  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Party:** John / Winston / Amelia / Murat (fully spawned)  
**Operator ask:** Define success so enhanced Marcus solicitation is proven by **live-test run output assets** in measurable ways.  
**Product thesis:** elicitation/ingestion → ratification artifacts → Irene → **lesson plan as primary downstream pipe** (+ links/refs).

---

## 0. Two claims (do not conflate)

| Claim | What it proves | Live Irene LLM? |
|-------|----------------|-----------------|
| **Claim A — Ratification substrate** | Marcus can solicit/record purpose·audience·workflow·gap-fill; artifacts load; selection changes; local compose succeeds | **No** |
| **Claim B — Solicitation informed the lesson plan** | The run’s Irene Pass-1 plan assets measurably reflect that solicitation | **Yes** (or equivalent real Pass-1 emit) |

**Operator product ask = Claim B.**  
Claim A is necessary substrate; **Claim A alone must not be reported as “bespoke lesson planning.”**

Party concurrence on that split: John / Murat / Amelia agree. Winston agrees on the chain and additionally requires machine `planning_provenance` on the plan object for Claim B (see §4).

---

## 1. One-sentence success claims

**Claim A (substrate):**  
Marcus `plan-ratify` wrote loadable ratification + intent under a real run directory; selection differs from baseline; local `compose_and_digest` succeeds on the ratified selection; trial start threads that selection into `run_summary` (no Gamma).

**Claim B (product):**  
After Claim A, Irene Pass-1 on that run emits a lesson plan whose on-disk assets show purpose/audience/(LO) acknowledgment via coverage receipt **and** a measurable plan-text delta vs an identical no-ratification control — with digests linking the plan to the ratification companions.

---

## 2. Canonical asset chain (ordered)

All positive proofs use a real consumer root:

`RUN_DIR = runs/<trial_uuid>/`  
Evidence under `_bmad-output/.../evidence/` may **mirror** RUN_DIR; mirrors alone are **not** SUCCESS.

| Hop | Asset | Role |
|-----|-------|------|
| 1 | `RUN_DIR/planning-ratification.json` | Solicited purpose/audience/assessment/workflow/gap-fill |
| 2 | `RUN_DIR/ratified-collateral-intent.yaml` | Ratified selection intent |
| 3 | `RUN_DIR/ratified-los.json` | Optional; **required** when claiming LO/bespoke improvement |
| 4 | Irene runner payload | `planning_context` present **only** for Irene Pass-1 |
| 5 | `RUN_DIR/irene-pass1.md` + `run.json` → `irene_pass1.lesson_plan` | Primary lesson-plan asset |
| 6 | Coverage receipt | `planning_context_coverage` on contribution and/or `RUN_DIR/planning-context-coverage.json` |
| 7 | `selection-delta.json` | before (baseline) ≠ after (ratified) |
| 8 | Compose digest dump | `compose_and_digest(after.selection)` succeeded |
| 9 | `RUN_DIR/trial-start.json` + `run_summary.yaml` | Intent path + bundle_id + `component_selection` == after |
| 10 | Control tree | Same corpus, **no** ratification → different plan hash / no coverage |

Hops 1–3 + 7–9 = Claim A.  
Hops 1–6 + 10 = Claim B.  
Full product SUCCESS = Claim A **and** Claim B.

---

## 3. Measurable predicates (pass/fail)

### Claim A — required

**`planning-ratification.json`**
- `schema_version == "0.1"`
- `purpose` and `audience` non-empty; match CLI/solicitation flags
- `source_assessment.richness` ∈ {`thin`,`rich`}; corpus id matches leaf used
- `gap_fill.chosen` ∈ closed set; appears in `considered`
- SHA-256 of file banked in evidence index

**`ratified-collateral-intent.yaml`**
- `ratification_status == ratified`
- `resolve_intent_file` → `source == "ratified"`
- `bundle_id` matches chosen workflow

**Selection delta**
- `compute_selection_delta(baseline, after).changed == true`
- At least one of deck/motion/workbook differs from `default_baseline_selection()`

**Compose (W5 local)**
- `compose_and_digest(after.selection)` succeeds
- Non-empty `composed_graph_digest` (use real `TwoPartDigest` fields — not invented attrs)
- Compose pin == **after** selection, **not** baseline

**Trial threading**
- `trial-start.json.lesson_plan_collateral_bundle_id` == after bundle
- `run_summary.yaml.component_selection` == after selection map
- `run.json` exists

### Claim B — required (in addition to A)

**Irene saw context**
- `load_planning_context(RUN_DIR)` returns purpose/audience matching hop 1
- Irene prompt contains stable labeled section marker (framing, not unlabeled JSON dump of full context)
- Other specialists’ payloads omit `planning_context`

**Coverage receipt**
- Receipt on disk / contribution with `context_present == true`
- `purpose_acknowledged == true` AND `audience_acknowledged == true`
- If LOs solicited: `lo_coverage ∈ {partial, present}` — **`absent` = FAIL** (fail-loud is not SUCCESS)
- If LOs solicited: `supported_objective_ids` length ≥ 1 **or** documented partial with ≥1 touch

**Lesson plan asset**
- `irene-pass1.md` exists with ≥1 plan unit
- Plan-text shares significant tokens with purpose **and** audience (same token rules as coverage assessor)
- Byte/hash **≠** control `irene-pass1.md` from hop 10

**Control**
- Same corpus; no ratification artifacts
- `load_planning_context` → `None`
- Plan hash differs from treatment

### Claim B — “bespoke” vs “framing-only”

| Label | Requires |
|-------|----------|
| **Framing-only SUCCESS** | Claim A + purpose/audience ack + plan delta vs control (LOs empty OK) |
| **Bespoke SUCCESS** | Framing-only **plus** non-empty LOs **plus** `lo_coverage ∈ {partial,present}` **plus** ≥1 LO touch in plan_units |

Purpose string alone without LO touch must **not** be called bespoke.

---

## 4. Lesson-plan provenance refs (`planning_provenance`)

| Seat | Position |
|------|----------|
| Winston | **IN** for Claim B — digests on `lesson_plan` object |
| John | Allowed as fenced residual for COMPLETE-with-fenced-residuals; **not** a substitute for coverage + plan delta |
| Amelia / prior slice | OUT of current plan-ratify AC-M5 |
| Murat | Claiming refs without emit = overclaim FAIL |

**Binding synthesis (orchestrator + party):**
- For **Claim B COMPLETE:** `planning_provenance` on emitted `lesson_plan` is **IN** (Winston pipe thesis).
- Minimal shape:

```json
"planning_provenance": {
  "schema_version": "0.1",
  "ratification_path": "planning-ratification.json",
  "ratification_digest": "sha256:<64hex>",
  "ratified_los_path": "ratified-los.json" | null,
  "ratified_los_digest": "sha256:<64hex>" | null,
  "intent_path": "ratified-collateral-intent.yaml" | null,
  "intent_digest": "sha256:<64hex>" | null,
  "coverage_lo_status": "present" | "partial" | "absent" | "framing_only"
}
```

- Digests must match companion file bytes still readable from RUN_DIR.
- Omit key entirely when no planning context was consumed.
- **COMPLETE-with-fenced-residuals** may defer provenance emit **only if** Claim B coverage + plan-delta predicates still pass and the fence is named explicitly.

---

## 5. False-green kill list (binding)

| ID | Theater | Required counter-proof |
|----|---------|------------------------|
| FG-1 | Files written; Irene never saw them | `load_planning_context(RUN_DIR)` + labeled prompt section + Irene-only payload key |
| FG-2 | Prompt substring only | Structured coverage receipt on disk |
| FG-3 | Selection unchanged | `selection-delta.changed == true` |
| FG-4 | Compose on default selection | Compose pin == after, ≠ baseline |
| FG-5 | “Bespoke” with purpose only / LOs ignored | Non-empty LOs + `lo_coverage ≠ absent` + LO touch |
| FG-6 | Evidence only under `_bmad-output` | Consumer proofs cite real `runs/<uuid>/` |
| FG-7 | Intent file exists ≠ consumed | trial-start / run_summary show `source=ratified` + after bundle |
| FG-8 | W5 claimed via Gamma spend | Local compose only; Gamma calls = 0 |
| FG-9 | Provenance claimed without emit | Digests present on plan **or** explicit fence |
| FG-10 | Vacuous always-true receipt | Non-empty supported/weak lists when LOs present |

---

## 6. Required negative cases

1. No artifacts → context `None`; no section; no receipt; default selection  
2. Invalid gap-fill / overclaim / workbook-without-collateral → CLI exit ≠ 0; no write  
3. Missing assessment source → exit ≠ 0  
4. Non-empty LOs + zero touch → fail-loud; receipt written before raise  
5. Conflicting purpose/audience across files → fail-loud  
6. Malformed JSON → fail-loud  
7. Forced after==before → delta must not PASS  
8. Compose with baseline while intent ratified → FAIL  
9. Artifacts only in evidence mirror → consumer load FAIL  

---

## 7. Minimum live-run scenario

- **Corpus:** rich Tejal leaf  
  `course-content/courses/tejal-c1m1-p4-assessments-bridge`  
  (thin/empty corpus = NO-GO for Claim B token-ack)
- **Solicitation:** distinctive purpose + audience tokens (≥2 significant tokens each unlikely in baseline plan)
- **For bespoke:** ≥1 LO with distinctive tokens in `ratified-los.json`
- **Workflow:** bundle that forces selection delta vs baseline (e.g. `narrated-deck-with-motion` or lighter `narrated-deck`)
- **Pipe:** plan-ratify → copy/write into RUN_DIR → trial start with `--lesson-plan-collateral-intent` → Irene Pass-1 → bank plan + coverage → compose on after selection
- **Control:** identical path without ratification
- **Out of SUCCESS:** Gamma spend, published deck URL, full SPOC REPL rewrite, SME/projector, lecture ingest

---

## 8. Done-bar

| Status | Criteria |
|--------|----------|
| **Claim A COMPLETE** | Hops 1–3 + 7–9 green; negatives for CLI/absent banked; dual-gate; no Claim B language |
| **Claim B COMPLETE** | Claim A + hops 4–6 + 10 + provenance (§4) green; FG-1..10 countered; dual-gate party CLOSE |
| **Claim B COMPLETE-with-fenced-residuals** | Claim B predicates pass except **named** fences only: provenance emit (§4), richer-than-token LO matching, interactive SPOC REPL, Gamma. **Cannot** fence missing coverage, failed ack, `lo_coverage=absent`, or missing plan delta |
| **NOT COMPLETE** | Any of: no RUN_DIR consumer proof; selection unchanged; compose on baseline; Irene never saw context; purpose-only called “bespoke” |

**Gate mode:** **dual-gate** for Claim B (Murat honesty + Amelia code). Claim A alone may use dual-gate while W5 is in bar.

---

## 9. PROOF.md templates (verbatim)

### PASS — Claim B

```text
PROOF STATUS: PASS — Claim B (solicitation informed the lesson plan)

RUN_DIR=runs/<uuid>/
Marcus plan-ratify wrote planning-ratification.json + ratified-collateral-intent.yaml;
load_planning_context(RUN_DIR) matched solicitation flags;
Irene Pass-1 received labeled planning_context; coverage receipt lo_coverage=<present|partial>;
purpose_acknowledged=true; audience_acknowledged=true;
irene-pass1.md hash ≠ control; plan units acknowledge purpose/audience/(LOs);
selection-delta.changed=true; compose_and_digest pinned to after-selection;
trial-start/run_summary threaded source=ratified + after bundle_id;
planning_provenance digests match companion bytes (or named fence).
Gamma spend = 0.

Non-claims held: no SPOC REPL rewrite; no lecture ingest; no SME/projector;
no planning_context fan-out; no published Gamma walk.
```

### FAIL

```text
PROOF STATUS: FAIL — THEATER / INCOMPLETE

Blocked by: <FG-# or hop #>
Observed: <asset>
Missing: <required predicate>
Consumer root: <path>  (FAIL if only _bmad-output mirror)
Selection: before=… after=… changed=…
Compose pin: <after|baseline|unknown>
Irene: section_marker=… coverage=… lo_coverage=…
Do NOT claim PASS, COMPLETE, bespoke, or W5 until every required cell is true on RUN_DIR.
```

---

## 10. Party record

| Seat | Core ruling |
|------|-------------|
| **John** | Claim B needs plan assets G+H + control; Claim A alone ≠ “improved the lesson plan” |
| **Winston** | Digest-linked chain; `planning_provenance` IN for Claim B; no fan-out |
| **Amelia** | Claim A implementable now without live Irene; Claim B needs Pass-1 emit; fix W5 asserts (`composed_graph_digest`, not invented fields) |
| **Murat** | Dual-gate; RUN_DIR-only consumer proof; matrix S1–S8; purpose-only ≠ bespoke |

**Orchestrator synthesis:** Adopt this document as the binding SUCCESS definition for enhanced Marcus solicitation. Next implementation work that claims product SUCCESS must bank Claim B assets; substrate-only closes must say Claim A explicitly.
