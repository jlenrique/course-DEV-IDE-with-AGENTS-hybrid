# Ratified — Unified Canonical Learning Objective (LO) Schema + Signed LO-Delta Contract

**Status:** RATIFIED by party-mode (Winston, John, Marcus, Mary + **Irene signed**) 2026-06-26. No impasse — unanimous GREEN-WITH-AMENDMENTS / SIGN-WITH-AMENDMENTS.
**Authority:** the A7 pre-req for `g0-enrichment-cycle-charter-2026-06-26.md`. Consumed by `bmad-create-epics-and-stories`.
**Build discipline (charter, binding):** modular + DRY + existing patterns (pydantic-v2 closed-enum idioms; NEW-CYCLE brick pattern); **no mocks — every implicated segment proven by a LIVE run.**

---

## 1. Canonical LO entity (replaces the 3 in-code representations)

DRY mandate: this single entity REPLACES (1) Irene Pass-1's bare `learning_objective` string, (2) `LearningObjectiveBrief` dataclass, (3) `WorkbookSection.learning_objective_id` content; the `learning_objective_map` DB table keys to `objective_id` (unchanged role = alignment tracking).

```python
BloomLevel = Literal["remember","understand","apply","analyze","evaluate","create"]
LOStatus   = Literal["provisional","refined","ratified"]
Confidence = Literal["high","medium","low"]          # A2: first-class but ADVISORY (gates nothing). John dissent: would cut.
AdequacyVerdict = Literal["adequate","thin","gap"]

class SourceRef(BaseModel):                            # Mary A9 — structured locator, NOT a bare string
    source_id: str          # MUST ∈ the A6 deterministically-enumerated source set; fabricated id => RED (mirrors A1)
    locator: str            # page / heading / char-span within that source
    quoted_span: str        # VERBATIM substring of the resolved source text (deterministic containment check)

AdequacyFollowup = Literal["research-run","external-content-expected","special-artifact-guidance"]

class SourceAdequacy(BaseModel):                       # Mary A8 + Irene rubric. ADVISORY — never blocks (see §3.1).
    verdict: AdequacyVerdict   # ALERT ONLY. thin/gap NEVER halts the pipeline / forces a drop / gates a transition.
    rationale: str          # MUST quote the supporting/missing span
    missing: list[str]      # non-empty & CONCRETE (named sub-topic) on verdict in {thin, gap}; may be [] only on adequate
    suggested_followups: list[AdequacyFollowup] = []   # operator value: a thin/gap flag MAY suggest a research run or
                                                       # special artifact-creation guidance. Advisory hint, not an action.

class LearningObjective(BaseModel):
    objective_id: str                 # canonical open-id; IMMUTABLE once minted at G0 (Marcus +e)
    statement: str
    bloom_level: BloomLevel | None    # populated by Irene at refine; REQUIRED only at ratified (Winston+Irene)
    status: LOStatus
    source_refs: list[SourceRef]      # status-conditional cardinality (table below)
    confidence: Confidence            # advisory
    adequacy: SourceAdequacy | None   # None at provisional; REQUIRED at refined+
    origin: Literal["g0","irene-proposed"] = "g0"      # Irene (d) PROPOSE-NEW marker
    recommendation: Literal["keep","drop"] = "keep"    # Irene (e) RECOMMEND-DROP (advice only; Irene never deletes)
```

### Status-conditional invariant table (Winston) — enforced by the model validator
| field | provisional | refined | ratified |
|---|---|---|---|
| `statement` | required | required | required |
| `source_refs` | ≥0 | **≥1** | ≥1 |
| `bloom_level` | optional | optional (populated) | **required** |
| `adequacy` | None | **required** | required |
| `confidence` | required (advisory) | required | required |

`ratified` is a **forbidden output value** for Irene (schema red-reject if she emits it) — the value is only ever set by Marcus's operator-gated handler (§3).

## 2. Status-transition guard (Winston) — authority lives HERE, not in the model

```python
def advance_lo(lo: LearningObjective, target: LOStatus, *, actor: Literal["g0","irene","operator"]) -> LearningObjective: ...
```
Closed allowed-edge map (everything else → `IllegalTransition`):
| from → to | allowed actor |
|---|---|
| (mint) → provisional | `g0` |
| provisional → refined | `irene` |
| refined → ratified | `operator` |

- Deterministic + total; no LLM. `content_entity_manager` calls `advance_lo` exclusively — nobody hand-mutates `.status`.
- Idempotency: replaying an already-applied `(from,to,actor)` is a no-op or hard error, never a silent re-run (preserves graph-replay determinism under corpus-keyed caching).
- A8 (charter): a prior `ratified` LO touched again requires explicit operator re-confirm, never a silent re-stamp.

## 3. Signed LO-delta contract — what Irene returns to Marcus-SPOC

**Irene SIGNED this** (with her amendments). It is a **reconcilable ledger** (Marcus), not just new state. Per `objective_id`:
- **(a)** the refined LO with its `provisional→refined` transition;
- **(b)** a **source-tied rationale diff** for each CHANGED LO (what changed + why, citing `SourceRef` provenance — same A2 bar; provenance-less diff rejected pre-surface);
- **(c)** the per-LO `SourceAdequacy` (verdict + span-quoting rationale + concrete `missing[]`);
- **(+d) disposition code** — exactly one of: `refined-in-place | unchanged | split→[ids] | merged←[ids] | flagged-inadequate | proposed-new | recommend-drop`. (Marcus's reconciliation spine + Irene's two channels unified.) **No silent drops** — a `objective_id` that returns with no disposition is a guardrail BLOCK.
- **(+e) carry-through** of Marcus's frozen G0 fields + **immutable `objective_id`**; a mutated id/frozen field = provenance break, not a refinement.
- **(d-channel) PROPOSE-NEW:** source teaches something assessable the provisional set missed → Irene emits a new LO at `status=provisional`, `origin="irene-proposed"`, with `source_refs`. (She cannot self-promote her invention to `refined`; SPOC/operator ratifies it into the loop.)
- **(e-channel) RECOMMEND-DROP:** source can't support a provisional LO → held at `provisional` + `adequacy.verdict="gap"` + `recommendation="drop"` + rationale. SPOC/operator executes any drop.

**Reconciliation guarantee:** `G0_count` reconciles to `Irene_count` via the disposition ledger (splits/merges/new/drop are *explained* deltas). Marcus presents: "N in at G0, N accounted for, M changed + why, K flagged thin/gap."

### 3.1 Adequacy is ADVISORY — never a blocker (operator-binding, 2026-06-26)
Source adequacy is **an ALERT from Irene, not a gate.** Binding rules:
- A `thin`/`gap` verdict **NEVER** halts the pipeline, forces a drop, or gates a status transition. It is a warning flag carried forward for the operator.
- **Final adequacy determination = the operator + off-world SME**, not Irene and not the app. Lesson content may legitimately be created OUTSIDE this app (other tools/people), so a perceived in-corpus gap is a heads-up, not a defect.
- Adequacy warnings are a **valuable output**: a `thin`/`gap` flag MAY suggest a research run (Texas/Tracy) or special guidance when creating artifacts (slides, movies, etc.) — captured in `suggested_followups`. Advisory only.
- This is DISTINCT from reliable-ACCESS (A1): whether we can *read* a source at all stays a hard deterministic gate (RED on unreachable). Whether a readable source *supports* an LO is advisory. Do not conflate.
- `recommendation="drop"` (Irene channel e) stays a *recommendation* the operator may ignore; Irene never drops.

### Adequacy rubric (Mary A8 ∩ Irene) — operational, falsifiable (the verdict is an alert, see §3.1)
- **`adequate`** — every clause of the LO `statement` maps to ≥1 `source_ref` span that teaches it AND source supports authoring a defensible assessment (both the teach-leg and the **assess-leg** present).
- **`thin`** — one leg holds, the other partial (teachable but not assessable from source alone, or vice-versa). `missing[]` names the specific gap. The assess-leg is the discriminator. (Warning; may suggest research/guidance.)
- **`gap`** — source below the teachable floor (passing mention or nothing). (Warning; the LO proceeds; operator+SME decide whether to supply external content, trigger a research run, or drop.)

## 4. Marcus-side G0 artifacts (anti-anchoring + dissent)
- **A4 independent-parse-first:** sidecar `independent_parse{proposal, ts}` written BEFORE `operator_merge{suggestion, ts}`; deterministic guard `independent_parse.ts < operator_merge.ts` or reject pre-surface.
- **A3 dissent (Mary A11-hardened):** per-LO `dissent{against, marcus_position, operator_position, disposition: "upheld"|"overruled-by-operator"|"folded-into-adequacy"} | null`; **run-level invariant ≥1 real dissent** across the corpus; must be independent-parse-sourced and show run-to-run variance (a never-varying field carries no information).
- **A10 residual-completeness (Mary):** the manifest-confirm gate surfaces, per source, its **enumeration provenance** (which traversal/connector/root yielded it) AND the **traversal roots themselves** (Notion page IDs / Box folder IDs / URL-list walked) — so the operator confirms "these were the 3 roots I pointed you at," not just the leaf-file set. Cheapest affordance against a silently-pruned branch under D2-without-inventory.

## 5. Migration (Winston Q4 ∩ John staging)
- **Replace-and-rewire; no persisted parallel entity.** Pre-req story (S1) delivers the entity + `advance_lo` guard + emitted JSON Schema + shape-pin tests + a thin **adapter FUNCTION** (not a persisted dataclass) over the 4 reps (first adapter = the hard-coded Irene-string→workbook-brief map in `produce_tejal_workbook.py`).
- Native producer/consumer rewiring is distributed into S2 (G0 brick produces the entity) and S3 (Irene + workbook consume it) where those seams are already touched; the adapter function is deleted when the last consumer is rewired. `assert_learning_objective_bindings()` rewires to read `LearningObjective` directly and binds the workbook only against `status in {refined, ratified}` (a `provisional` LO must never reach a learner-facing workbook — free correctness win).

## 6. Ratified v1 story breakdown (John) → feeds `bmad-create-epics-and-stories`
1. **S1 — LO canonical schema + transition guard + adapter** (pre-req; schema-shape; single-gate). Entity + `advance_lo` + JSON Schema + shape-pin tests + adapter function. Status/provenance/adequacy types land here.
2. **S2 — G0-enrichment brick** (Marcus-SPOC-owned). Source-span typing (10-type closed enum + `other:<label>` escape hatch) + candidate-LO extraction emitting `status=provisional` with `SourceRef`s, OFF the deterministic critical path (LLM pre-pass, corpus-keyed cache). Includes **operator confirm-gate #1** + A4 independent-parse + A3 dissent scaffold + A10 manifest enumeration-provenance/roots. Wire gate side-effects into BOTH `production_runner` walks.
3. **S3 — Irene refinement loop + ratify-gate + completeness assert.** Refine in place provisional→refined; per-LO adequacy (ADVISORY, §3.1 — assessed, never gating); emit the signed LO-delta contract (all channels). **Operator gate #2** (ratify refined→ratified). Completeness hard-assert is about ACCESS + ASSESSMENT-PRESENCE, NOT adequacy outcome: every source span typed-or-ignored; every LO has ≥1 resolvable `SourceRef` AND a *populated* adequacy verdict (assessed, not silently absent); source **unreachable** = RED. A `thin`/`gap` adequacy verdict is a warning that does NOT fail the assert — the run proceeds to hand-off.

**Deferred follow-ons (→ `deferred-inventory.md`):** native producer/consumer rewiring beyond S2/S3; multi-turn Marcus↔operator LO negotiation (v1 = confirm-or-rerun at each gate); acted-upon typing (routing typed spans INTO generators — where 07W/07D.5 become consumers); a `quiz`/`rubric`/`exercise-lab` generator (consumer-less types today).

## 7. Named dissents (recorded, not impasses)
- **John:** would cut `confidence` from v1 (operator gate is the confidence mechanism). Overridden by locked charter A2 (confidence is first-class); kept as advisory enum. 

## 8. Build sequence (charter build-then-trial, no mocks)
S1 → S2 → S3, strict. Each: spec → dev → T11 (bmad-code-review) → **LIVE-segment trial on real content** → party-close. The mandatory A3 dissent artifact + A1/A6 completeness/RED-access invariants are themselves live-trial acceptance evidence. Goal DoD: a real trial runs G0 → enrichment → Irene loop → pre-planning → **hand-off-to-Gary gate, error-free, twice.**
