# Spec — Story 1.1: Re-wire cluster emission into LLM-first Pass-1

**Status:** ready-for-dev
**Class:** S (substrate)
**Phase:** Clustering re-activation (Phase 1), first story (smallest, first — Winston/John split)
**Gate mode:** single-gate (focused additive change on one live module + references + tests)
**Authority:** `forward-development-sequence-2026-06-24.md` §Phase-1 1b + Phase-1a amendments; memory `chunking-via-clustering-followalong`; survival-probe verdict `clustering-survival-probe-2026-06-24.md` (downstream confirmed live, no bit-rot).
**r_tier:** R2 · **t11_tier:** standard · **lookahead_tier:** 2 · **files_touched:** `app/specialists/irene_pass1/_act.py` (+ unit tests; NO manifest/pack/lockstep path → not block-mode).

---

## Problem

The post-severance LLM-first Pass-1 rebuild **dropped cluster emission.** `app/specialists/irene_pass1/_act.py::assemble_pass1_prompt` (L132-134) requests only flat plan_units `{unit_id, title, learning_objective, scope_decision, rationale}`. The downstream cluster machinery (Gary `_derive_clusters`, segment-manifest cluster carry, Epic-23 bridges, density/estimator) is **confirmed live** (survival probe, 11/11 + 190 unit tests green) but **never fed** because Pass-1 emits no cluster fields. Result: every dense slide stays one slide → loose VO-to-screen coupling → the follow-along problem.

This story reconnects the single dropped wire at the Pass-1 seam. **Schema-additive, downstream already tolerant** (cluster fields nullable; tolerance proven by the probe's negative control). It does NOT touch `pass_2_template.py` (cluster fields already there), Gary, bridges, the estimator, or any block-mode path.

## Scope (in `app/specialists/irene_pass1/_act.py` only)

### 1. Load the cluster decision/arc references into the prompt
`PASS_1_REFERENCES` (L19-26) currently loads only the umbrella `cluster-planning.md`. Add the detailed references the model needs to actually decide + populate clusters:
- `cluster-decision-criteria.md` (CD — the 4-criterion chunk decision + decision table)
- `cluster-narrative-arc-schema.md` (NA — `narrative_arc` "From X to Y through Z", Sophia four-beat → establish/tension/develop/resolve, `master_behavioral_intent` vocab, `develop_type`)
- `cluster-density-controls.md` (DC — interstitial counts, per-slide overrides)

(`content-sequencing.md` already loaded. `interstitial-brief-specification.md` / `spoken-bridging-language.md` are Pass-2/Gary-side; not required here.)

### 2. Extend the emission contract (`assemble_pass1_prompt`)
The returned JSON instruction must request, **per plan_unit**, the additive cluster fields, and instruct the model to apply the CD framework:

```
Return JSON: {"plan_units":[{
  "unit_id":"...","title":"...","learning_objective":"...",
  "scope_decision":"in-scope|out-of-scope","rationale":"...",
  "cluster_id":"c-uNN",                       // every unit belongs to a cluster; singleton = its own
  "cluster_role":"head|interstitial",
  "cluster_position":"establish|tension|develop|resolve",
  "narrative_arc":"From <start> to <end> through <mechanism>",  // on head; inherited by members
  "master_behavioral_intent":"credible|alarming|provocative|reflective|moving|clear-guidance|attention-reset", // on head
  "develop_type":"deepen|reframe|exemplify|null",              // develop-position interstitials only
  "parent_slide_id":"<head unit_id>",          // interstitials only
  "cluster_interstitial_count":<int>           // on head (0 for a singleton/keep-dense unit)
}],"lesson_summary":"..."}
```

Cluster-decision guidance to embed in the prompt (from CD + the chunking memory routing):
- **Chunk by DEFAULT** a dense unit (3+ explanatory beats / high concept-density or visual-complexity or pedagogical-weight) into a **head + N interstitials** (N=1–3) under one shared `narrative_arc`, beats ordered establish→tension→develop→resolve. Each interstitial is its own plan_unit with `cluster_role:interstitial`, `parent_slide_id`=head, same `cluster_id`.
- **KEEP DENSE (singleton, never chunk a gestalt):** synthesis / big-picture / comparison (two-up) / diagram-driven / before-after / the "resolve"/takeaway slide whose value IS the simultaneous whole. Emit ONE plan_unit, `cluster_role:head`, `cluster_position:establish`, `cluster_interstitial_count:0`. **keep-dense is an INPUT to the decision, never a veto applied after** (amendment #5; the explicit per-slide marker ships in Story 1.3).
- Singletons still carry a `cluster_id` (degenerate size-1 cluster) — amendment #4.

### 3. Deterministic normalization backstop — new `normalize_clusters(plan)` 
LLM output is variance-prone; add a pure post-parse function that makes the cluster structure well-formed and downstream-valid regardless of model sloppiness:
- Every unit missing `cluster_id` → assign a singleton id derived from `unit_id`.
- Missing `cluster_role` → default `head`; missing `cluster_position` → default `establish`.
- Coerce/validate enums (`cluster_role`, `cluster_position`, `develop_type`, `master_behavioral_intent`) against the canonical literals; invalid → drop the offending field to None (tolerance-of-absence), never crash.
- **narrative_arc inheritance:** interstitials inherit their head's `narrative_arc` if absent (NA inheritance rule).
- Interstitial whose `parent_slide_id` matches no head in the plan → demote to a singleton head (no orphans reach Gary).
- Recompute `cluster_interstitial_count` on each head from its actual interstitial members (authoritative; ignore a stale model count).
- Idempotent: `normalize_clusters(normalize_clusters(p)) == normalize_clusters(p)`.

Call `normalize_clusters` inside `parse_pass1_response` (after JSON parse, before the fallback-unit branch) so both LLM output and the fallback unit are normalized. The **fallback unit** (L154-162) becomes a degenerate size-1 cluster (`cluster_id`, `cluster_role:head`, `cluster_position:establish`, `cluster_interstitial_count:0`).

### 4. Write cluster fields into the artifact (`write_lesson_plan`)
Extend the per-unit markdown block (L174-183) so the cluster fields are visible in `irene-pass1.md` — this is the witness the Story 1.2 **emission gate** reads ("dense slide carries cluster fields count≥2 in the real Pass-1 artifact"). Emit, per unit: cluster_id, cluster_role, cluster_position, narrative_arc, parent_slide_id (if interstitial), cluster_interstitial_count (if head). Keep the existing flat lines (additive, no removal).

### 5. Output carries clusters downstream
`act()` already puts `plan["plan_units"]` into `lesson_plan`, `locked_scope`, and the cache_prefix output (L246-256). Once plan_units carry cluster fields, they flow to Gary unchanged. No additional change needed — **add an AC asserting the cluster fields are present in `locked_scope` after `act()`** (round-trip).

## Out of scope (explicit)
- `app/marcus/lesson_plan/schema.py::PlanUnit` — a separate (Marcus-precursor) validation model NOT on the live `_act.py` dict-based emission path; extending it is additive but deferred (flag only; not required for the live wire).
- The per-slide chunk **directive** + keep-dense **marker** (`special_treatment_directives`) + inter-sub-slide transition timing → **Story 1.3**.
- Clustering × per-sub-slide A/B → **Story 1.4**.
- Live proof that gpt-5.5 actually emits clusters on the tejal corpus → **Story 1.2** artifact gates (not unit-testable here).

## Acceptance criteria (RED-first; all dev-agent verifiable via shipped deps, no operator CLIs)

- **AC-1 (emission contract):** `assemble_pass1_prompt(...)` user message contains the cluster-field JSON keys (cluster_id, cluster_role, cluster_position, narrative_arc, cluster_interstitial_count, parent_slide_id, develop_type) AND the chunk-by-default + keep-dense-singleton guidance.
- **AC-2 (references loaded):** the prompt includes the bodies of `cluster-decision-criteria.md` and `cluster-narrative-arc-schema.md` (assert a unique sentinel phrase from each, e.g. "If a slide requires 3+ distinct explanatory beats" and "From [start state] to [end state]").
- **AC-3 (parse preserves clusters):** `parse_pass1_response` on a cluster-bearing JSON response returns plan_units retaining cluster_id/role/position/narrative_arc; a head with 2 interstitials yields 3 plan_units with the shared cluster_id.
- **AC-4 (normalize backstop):** `normalize_clusters` — singleton gets cluster_id + head/establish + count 0; interstitial inherits head's narrative_arc; invalid cluster_position → None (no crash); orphan interstitial → singleton head; cluster_interstitial_count recomputed from members; idempotent.
- **AC-5 (fallback = size-1 cluster):** the unstructured-response fallback unit is a normalized degenerate size-1 cluster (cluster_role head, cluster_position establish).
- **AC-6 (artifact witness):** `write_lesson_plan` writes cluster_id/role/position/narrative_arc into `irene-pass1.md`; assert by reading the file back.
- **AC-7 (tolerance-of-absence — amendment #4):** a plan_units list with NO cluster fields parses + normalizes + writes without error (degrades to singleton size-1 clusters / None), and a downstream `IrenePass2AuthoringEnvelope` built from cluster-absent segments still validates (reuse the survival-probe path).
- **AC-8 (downstream round-trip):** cluster-bearing plan_units fed into `run_gary_dispatch._derive_clusters` yield the expected heads + interstitial counts (link 1.1 emission to the live consumer; reuse the probe's Gary leg).
- **AC-9 (non-regression):** existing irene_pass1 tests + the 190-test dormant cluster suite + lint-imports stay green; flat (no-cluster) behavior is unchanged when the model emits no cluster fields.

## Non-regression / fences
- Additive only: no removal of the flat fields or flat-path behavior; reading-path / per-slide-variant / figure-gate / pipeline untouched. G5 figure detector UNTOUCHED. No block-mode/manifest/pack path touched (no version bump). No `--no-verify`, no force-push.

## Review Findings (T11 — bmad-code-review 3-layer, 2026-06-24)

Dev cycle (independent agent, T1–T10) shipped all 9 ACs green (18 tests). Claude T11 reproduced the battery (first-run-stands) and ran 3 adversarial layers:
- **Acceptance Auditor → ACCEPT.** All 9 ACs genuinely satisfied; no out-of-scope creep; minimal import surface honored; AC-2 sentinel phrases confirmed verbatim-unique to the new references (strongest form); AC-7/AC-8 exercise the real downstream. Two cosmetic NITs only (spec-compliant).
- **Blind Hunter + Edge Case Hunter → one shared root cause (MAJOR):** `normalize_clusters` keyed orphan-demotion on `parent_slide_id ∈ unit_id-set` but keyed count + arc-inheritance on `cluster_id`, never reconciling them → miscount/phantom-cluster/collapsed-singleton on divergent, duplicate, or missing-id model output. Plus a tautological `cluster_position in (None, "establish")` test.

**Resolution — PATCHED at T11 (remediation applied directly + 6 new regression tests; 24 tests green):**
- `[Patch]` Parent linkage now AUTHORITATIVE: an interstitial's cluster_id + narrative_arc are derived from its resolved head (via `parent_slide_id`, or a matching head `cluster_id` when parent omitted) → count/arc/grouping mutually consistent. (Blind MAJOR-1 / Edge #1, #10)
- `[Patch]` Roles coerced BEFORE the head set is computed (mis-cased "Head" no longer orphans real interstitials). (Edge #2)
- `[Patch]` Duplicate head cluster_ids split via a uniqueness set; demoted orphans get their own singleton id. (Edge #3, Blind MINOR)
- `[Patch]` Index-stable synthetic keys so distinct missing/duplicate unit_id units never collapse into one cluster. (Edge #5, #6)
- `[Patch]` Position semantics: head → establish (anchor); interstitial missing/invalid → None (never forced to establish). Tautological test rewritten to assert the real behavior. (Blind MAJOR-2 + MINOR, Edge #4)
- `[Patch]` Non-dict `plan` guard (public fn robustness). (Blind MINOR)

**DEFERRED (filed; non-blocking):**
- `[Defer]` Edge #9 — the production seam is `plan_units → gary-slide-content.json → _derive_clusters` (Gary builds slide rows in between), not plan_units fed straight to `_derive_clusters`. AC-8 covers the direct call; the REAL seam is verified by **Story 1.2's live propagation artifact gate**. Folded into Story 1.2 scope.
- `[Defer]` Numeric-id representational drift (`1.0` vs `1`) across head/parent — exotic; real LLM emits string ids. Low-priority hardening nit.
- `[Defer]` Optional artifact emission of `master_behavioral_intent`/`develop_type` + a dedicated coercion test — spec-compliant omission (§4 lists 6 fields); optional 1.2/1.3 enhancement.

**DISMISSED (noise/by-design):** AC-2 "brittle pinned prose" (it's the intended proof-of-load technique, Auditor-praised); always-appended cluster lines (by-design witness, flat fields preserved); `|null` pseudo-enum (self-correcting via normalize); double-normalize (confirmed no hazard); arc-less head (can't synthesize an arc — model-completeness, surfaced by 1.2 live gate).

**Status: done** (battery green, MAJORs remediated, downstream non-regression confirmed).

## Dev notes
- `parse_pass1_response` already passes through unknown dict keys (json.loads), so cluster fields survive parse today — the real gaps are the **prompt request**, the **normalization backstop**, and the **artifact write**. Don't over-engineer parse.
- Canonical enums live in `app/specialists/irene/authoring/pass_2_template.py` (`ClusterRole`, `ClusterPosition`, `BridgeType`) and `cluster-narrative-arc-schema.md` (`master_behavioral_intent`, `develop_type`). Reuse the Literal sets; do not invent new vocab.
- Keep `normalize_clusters` pure (no I/O) and exported in `__all__` for testability.
