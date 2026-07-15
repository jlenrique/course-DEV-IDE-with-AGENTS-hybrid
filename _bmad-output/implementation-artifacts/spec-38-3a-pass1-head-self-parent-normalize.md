---
title: 'Irene Pass-1: normalize self-referential parent_slide_id on head units (live variance)'
type: 'bugfix'
created: '2026-07-15'
status: 'ready-for-dev'
baseline_commit: '9d4f0593'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-38-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Governed live trial `5ee9ac39` (the LO-bridge verification run) paused at node 04A: `[irene-pass1.authority-invalid] head unit u01 must not carry parent_slide_id`. The live model emitted `parent_slide_id: "<own unit_id>"` on every HEAD unit (u01→u01 … u06→u06) while emitting perfectly-formed interstitials (u03i1/u03i2→u03, matching cluster). The Pass-1 cluster-reconciliation pipeline (`app/specialists/irene_pass1/_act.py` Pass 1–5) normalizes many live-variance shapes but nothing strips a head's self-referential `parent_slide_id`, so it survives to `_validate_cluster_authority` (`app/marcus/lesson_plan/pass1_authority.py:199-204`) and red-rejects the whole run. Run frozen as immutable negative witness per first-run-stands.

**Approach:** Deterministic, minimal normalization at the existing reconciliation seam (Pass 2 head branch of `normalize_clusters`, `_act.py:889-904` — Pass 1 role coercion already precedes it, and normalization runs at parse, before BOTH `finalize_plan_authority` and persistence, so plan and receipt identities stay coupled). Mechanism (party W2): `unit.pop("parent_slide_id", None)` — key ABSENT, matching today's happy-path heads and the Pass-3 orphan-demotion idiom; never set `None`. Predicate (party W3/M-F2): normalize when `parent_slide_id` is empty/whitespace, or when `str(parent).strip() == str(unit.get("unit_id")).strip()` on the RAW `unit_id` (never the `_uid()` positional fallback). A head carrying anything else — a different unit's id, a case-differing id, its own `cluster_id`, a non-string — remains fail-loud (genuinely ambiguous). No validator loosening — `_validate_cluster_authority` stays exactly as strict.

## Boundaries & Constraints

**Always:**
- Fix at the deterministic normalization seam in `app/specialists/irene_pass1/_act.py` (the same Pass 1–5 pipeline that already demotes orphans), so the persisted plan and the authority receipt both see canonical heads.
- Preserve fail-loud for the ambiguous case (head with a non-self, non-empty parent_slide_id) — assert it still raises.
- Deterministic tests use the exact emitted shape from trial `5ee9ac39` (`runs/5ee9ac39…/irene-pass1-call-04A.v1.json` raw_response plan units: 6 self-parent heads + 2 well-formed interstitials) as fixture data. The run dir is READ-ONLY evidence.

**Ask First:**
- Any change to `_validate_cluster_authority` semantics or the Pass-1 prompt text (prompt hardening is allowed only as an ADDITIVE clarification, not a substitute for the deterministic fix).

**Never:**
- No validator loosening, no LLM calls in tests, no mocks, no retry-to-green of frozen runs.
- Do not touch pipeline-manifest/graph topology (HALT if unavoidable). Do not modify `runs/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Live shape (5ee9ac39) | 6 heads each with `parent_slide_id == unit_id`; u03i1/u03i2 interstitials → u03 | Heads normalize to KEY-ABSENT; interstitials untouched; `finalize_plan_authority` passes | N/A |
| Whitespace-padded self parent | head `u01` with `parent_slide_id: " u01 "` | Normalizes (stripped-equality predicate) | N/A |
| Empty-string parent on head | head with `parent_slide_id: ""` or `"  "` | Normalizes to absent; authority passes | N/A |
| Ambiguous head parent | head u02 with `parent_slide_id: "u01"` | NOT normalized; `_validate_cluster_authority` raises exactly as today | Fail-loud preserved |
| Case-differing parent | head `u01` with `parent_slide_id: "U01"` | NOT normalized (exact stripped equality — no casefolding); fail-loud | Fail-loud preserved |
| Non-string parent | head with `parent_slide_id: 1` (int) | NOT normalized; fail-loud | Fail-loud preserved |
| Head parent equals cluster_id | head `u01`, `cluster_id "c-u01"`, `parent_slide_id: "c-u01"` | NOT normalized (guards over-normalization `parent in {unit_id, cluster_id}`); fail-loud | Fail-loud preserved |
| Interstitial self-parent — VALIDATOR seam (party W1/M-F1/A-F2) | raw units fed DIRECTLY to `finalize_plan_authority` (bypassing reconciliation), interstitial `parent_slide_id == unit_id` | `Pass1PlanAuthorityError` (validator strictness unchanged) | Fail-loud pinned at the validator |
| Interstitial self-parent — RECONCILIATION seam | same shape through `normalize_clusters` | Pass 3 resolve-or-demote exactly as today (cluster_id fallback rewrites parent to the real head, or orphan-demotes) — pinned AS-IS so this fix does not change Pass 3 | Never silently corrupted into a wrong parent |
| Head with parent_slide_id: None / absent | today's happy path | Byte-identical behavior | N/A |

</frozen-after-approval>

## Code Map

- `app/specialists/irene_pass1/_act.py` — cluster-reconciliation pipeline (head pass ~L880-905; interstitial Pass 3 ~L906-937); normalization lands in the head pass.
- `app/marcus/lesson_plan/pass1_authority.py:193-225` — `_validate_cluster_authority` (UNCHANGED; heads must carry no parent, interstitials validated strictly).
- `runs/5ee9ac39-347b-485e-bcab-81928f8d4379/irene-pass1-call-04A.v1.json` — read-only evidence (raw_response carries the exact self-parent shape).
- `tests/specialists/irene_pass1/` — existing Pass-1 suites; new tests co-locate.

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/irene_pass1/_act.py` — in the Pass 2 head branch of `normalize_clusters` (L889-904), `unit.pop("parent_slide_id", None)` when the value is a string that is empty/whitespace or stripped-equal to the unit's RAW `unit_id`; leave any other value untouched (comment: live-variance normalization, trial 5ee9ac39) — rationale: deterministic seam already owns shape canonicalization; runs before authority finalization AND persistence so plan/receipt identities stay coupled.
- [x] `app/specialists/irene_pass1/_act.py` (prompt text, ~L695) — ADDITIVE clarification only (party J-B, pre-authorized): state explicitly that HEAD units must OMIT `parent_slide_id` entirely — rationale: defense in depth against new variance shapes; never a substitute for the deterministic fix. (Landed as an additive guidance bullet in `_cluster_emission_instructions`; no prompt byte-stability/digest pin exists in the suite — `test_prompt_assembly_is_byte_stable` pins determinism across calls, not a golden.)
- [x] `tests/specialists/irene_pass1/test_head_self_parent_normalize_5ee9ac39.py` — pin every matrix row; cluster-topology fields lifted verbatim from trial 5ee9ac39; for the `finalize_plan_authority` end-to-end pass, re-bind `source_ref_ids` + inject `source_span_catalog_digest` from a synthetic catalog via `build_pass1_source_span_catalog` (party A-F3 — the raw digests bind the live run's source bytes; established pattern in `test_pass1_authority_amendment6.py`) — rationale: regression floor on the real negative witness. (19 tests, all matrix rows incl. the row-8/row-9 validator-vs-reconciliation seam split.)
- [x] Pre-flight witness replay (party J-A): before the paid run, replay the Pass-1 raw_response plan shapes from ALL frozen negative witnesses that captured one (`runs/<witness>/irene-pass1-call-04A.v1.json` where present: 399bcd61, 7dd3e6ed, 503e54c1, 4614f21f, dfc372b7, 5ee9ac39) through `normalize_clusters` + cluster validation offline; if any OTHER known live shape still red-rejects, batch that fix into THIS cycle — rationale: don't burn the paid run on the next known layer. (Replayed ALL 9 journals on disk — the 6 named plus 30850735, a940c5eb, b07962e3: only 5ee9ac39 red-rejected pre-normalize (`head unit u01 must not carry parent_slide_id`); ALL 9 PASS through the production parse path post-fix. No other known live shape red-rejects; nothing further to batch.)

**Acceptance Criteria (deterministic done-bar):**
- Given the exact plan-unit shape emitted in trial `5ee9ac39`, when Pass-1 reconciliation + `finalize_plan_authority` run, then no `Pass1PlanAuthorityError` is raised and heads carry no parent_slide_id.
- Given a head carrying a different unit's id, when authority finalizes, then the run still fails loud exactly as today.
- Given `pytest tests/specialists/irene_pass1 tests/specialists/workbook_producer -q` (non-live), then green; ruff clean on touched files.

**Acceptance Criterion (operator-gated live leg — outside the deterministic bar):**
- Given one fresh governed live run (`MARCUS_G0_DISPATCH_LIVE=1`, fresh trial id, first-run-stands), when it completes, then it passes 04A and (combined with the LO-bridge fix) renders a workbook whose Learning Objectives section carries real statements with no placeholders and no loss callout. A failed run stands as evidence; file and return to spec.

## Verification

**Commands:**
- `.venv/Scripts/python.exe -m pytest tests/specialists/irene_pass1 -q` — green.
- `.venv/Scripts/python.exe -m pytest tests/specialists/workbook_producer -q` — green (no coupling regressions).
- `.venv/Scripts/ruff.exe check app/specialists/irene_pass1/_act.py tests/specialists/irene_pass1/` — clean.

## Party Green-Light Record

2026-07-15: Winston / John / Amelia / Murat — 4/4 APPROVE-WITH-AMENDMENTS, all folded (W1+M-F1+A-F2 row-4 seam split; W2 pop-not-None; W3+M-F2 stripped-raw-unit_id predicate + boundary rows; M-F3 cluster_id guard; J-A witness pre-flight replay; J-B additive prompt clarification pre-authorized; A-F3 synthetic span-catalog re-binding for the e2e floor; Murat F4 confirms normalize-before-receipt coupling). Orchestrator concurred; Checkpoint-1 satisfied per party-consensus-=-approval. Operator directive this session: implement and launch the fresh run once approved.
