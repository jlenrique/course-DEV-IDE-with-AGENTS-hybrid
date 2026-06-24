# Clustering downstream — T1 SURVIVAL PROBE verdict (2026-06-24)

**Governance:** Phase-1a green-light amendment #2 (John) — *before* re-wiring Pass-1
cluster emission, hand-feed a cluster input through the dormant downstream to confirm
the April machinery still **EXECUTES** (survival-in-code ≠ survival-in-execution).
Murat amendment #3: gate on the **witness**, never on a green unit suite alone.

**VERDICT: GREEN — no bit-rot. The dormant downstream executes on FRESH cluster input.**
Risk is confined to the Pass-1 emission seam, as the dormancy diagnosis predicted.
Story 1.1 proceeds as scoped; **no party re-entry / re-scope required.**

## Evidence

### Leg A — dormant cluster unit/contract suite on clean HEAD
`190 passed in 10.93s` across the full cluster test surface:
- `skills/bmad-agent-marcus/scripts/tests/test_cluster_{coherence_validation,dispatch_sequencing,fidelity_contracts,prompt_engineering,template_library,template_planner,template_selector}.py`
- `…/test_evaluate_cluster_template_selection.py`, `…/test_run_g1_5_cluster_gate.py`, `…/test_validate_cluster_plan.py`
- `tests/test_cluster_aware_pass2_contract_docs.py`, `tests/test_run_gary_dispatch.py`
- `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py`
- `tests/specialists/irene/test_irene_act_node_pass2_procedures.py`
- `tests/unit/specialists/irene/test_pass_2_template_strict.py`

### Leg B — artifact-level witness (fresh hand-fed cluster input, NOT frozen fixtures)
Probe script preserved at `_bmad-output/implementation-artifacts/clustering-survival-probe.py`.
All 11 checks PASS:

1. `run_gary_dispatch._derive_clusters` executes on fresh slides → finds 2 heads.
2. Explicit `cluster_interstitial_count` honored (c-probe01 → 2).
3. Member-derived count when count is None (c-probe02 → 1, counted from interstitials).
4. `narrative_arc` carried on head into the derived cluster.
5. `_merge_slide_cluster_fields` copies cluster_id/role/parent + aggregate fields.
6. `_slide_cluster_metadata` extracts narrative_arc + cluster_interstitial_count.
7. Declared-`clusters` envelope path executes (alternate derivation route).
8. Cluster-bearing `IrenePass2AuthoringEnvelope` validates end-to-end.
9. cluster_id/role/position survive validation on the segment.
10. `cluster_arc_continuity` procedural rule present in the validated envelope.
11. Negative control: `cluster_role`-required guard **actively rejects** cluster_id-without-role.

## Substrate map (confirmed alive)
- **Schema (ALIVE):** `app/specialists/irene/authoring/pass_2_template.py` — `ClusterRole`/`ClusterPosition`/`BridgeType` (L27-32); `SegmentManifestSegment.cluster_{id,role,position}` (L133-135); cluster_role-required validator (L264-273); `cluster_arc_continuity` in `REQUIRED_PROCEDURAL_RULES`.
- **Gary consumer (ALIVE):** `scripts/utilities/run_gary_dispatch.py` — `CLUSTER_OUTPUT_FIELDS`/`CLUSTER_AGGREGATE_FIELDS` (L42-50), `_slide_cluster_metadata`/`_merge_slide_cluster_fields`/`_derive_clusters` (L78-132).
- **Density/estimator (ALIVE):** `scripts/utilities/slide_count_runtime_estimator.py` — reads `cluster_expansion` from the experience profile.
- **special_treatment_directives (ALIVE):** `scripts/utilities/operator_directives_poll.py` — Story 1.3 extension point.
- **EMISSION BREAK (DORMANT):** `app/specialists/irene_pass1/_act.py` — `assemble_pass1_prompt` emission schema (L132-134) requests only `{unit_id,title,learning_objective,scope_decision,rationale}`; `parse_pass1_response`/`write_lesson_plan` handle only flat fields. Loads `cluster-planning.md` reference but never asks for cluster fields. **← the single dropped wire Story 1.1 reconnects.**
- **Second flat schema:** `app/marcus/lesson_plan/schema.py::PlanUnit` also lacks cluster fields (Story 1.1 must assess whether to extend it too).
- **April reference:** `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/assembly-bundle/segment-manifest.yaml` — 14 clustered segments, real head/interstitial/establish/tension structure.

## Reading-path disclaimer (amendment #10)
This probe does NOT advance the reading-path fresh-naive-holdout generalization gate; that gate remains open. No halo overclaim.
