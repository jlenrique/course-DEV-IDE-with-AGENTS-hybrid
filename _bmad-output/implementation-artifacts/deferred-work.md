## Deferred from: code review of migration-1-1a-runtime-substrate-environment-and-dependencies (2026-04-22)

- Broader repo bootstrap docs still point clean installs at `requirements.txt`, which does not include the migration-only `import-linter` tool. This is outside Story 1.1a's acceptance-command path and should be resolved as a separate hybrid bootstrap/docs alignment task.


## Deferred from: code review of trial-3-five-fix-batch (2026-06-11 batch; reviewed 2026-06-11)

- [blind] cd31b33 commit-hygiene defect: "PURE EXTRACTION ... suite run UNMODIFIED" proof claim is contradicted by the same commit (irene_pass1 roster change + modified tests/integration/marcus/test_run_summary_yaml_emit.py). Commits are pushed; remediation is process-tier — record at Trial-3 postmortem as a P-tier anti-pattern candidate (commit-message proof claims must be verifiable against the commit's own diff; roster change deserved its own commit).
- [edge] Per-segment trace-fixture/cost-report rebuild drops prior segments' pre-gate-Marcus runs (production_runner.py:1214-1217 rehydrates child_runs from contributions only; pause/completion overwrite trace-fixture.json + recompute cost with history=[]). Cumulative trial cost under-counted across pause cycles — relevant to the <=$3.00 trial criterion. Fold into `trial-3-pause-write-sequence-atomicity` redesign (same persistence-sequence surface).
- [blind] `specialist_calls` semantics fork between _pause_at_gate callers: start walker passes segment-local counter, resume walker passes len(production_envelope.contributions) (cumulative). _has_production_evidence can report live-call evidence from prior-segment contributions on a zero-call resume segment. Fold into `trial-3-max-specialist-calls-segment-cap-semantics` design story (same counter surface; needs the cap-semantics design decision first).
- [blind] Offline gate-traversal block now duplicated in resume branch (pending/pre_fill/child_runs-append reimplemented; same sequence lives in _pause_at_gate and start walker offline branch) — the A23 fork-at-function-granularity pattern the extraction was meant to kill. Refactor follow-on at next runner-touching story.
- [blind] TW-7c-4 PERMITTED_PYTHON_DIFFS grew +9 paths across three commits with author-written self-certifying rationale and no sunset mechanism. Governance observation for Epic-34/Trial-3 retrospective: tripwire allowlist needs an expiry/review discipline or it converges on a no-op.
- [edge] Composer >=1-primary invariant is corpus-level but section-02a-composer.j2 decides one file at a time — zero-primary directive still emittable on tie/degenerate corpora (README/url-list-only). Already-acknowledged residual of the bb81b6f fix; compose-time aggregation check is the named follow-on; operator G0 eyeball + wrangler fail-loud are the current backstops.


## Deferred from: code review of spec-phantom-delta-silent-audio-gap (2026-06-12)

- [edge] G5 `narration_segments` pass-through branch (quality_control_dispatch.py run_g5_grounding early return) bypasses phantom detection entirely: a legacy/direct payload carrying an empty-text segment still counts its slide as covered (run_g5_checks counts coverage by slide_id regardless of text). Same silent-gap family; pre-existing; spec fenced the fix to the join path. Candidate fold: count coverage only for non-empty-text segments at next G5-touching story.
- [edge] Enrique non-join branches (`segments` payload key + locked_manifest_path/manifest_path) still silent-skip empty-text rows in the TTS loop (`if not text: continue`). Pre-existing; spec "Ask First" fenced. Same silent-gap family; fold with the row above.
- [blind] Join id-truthiness policy collapses falsy delta ids (0/""/None) to "" (narration_join.py line 39 pre-existing; phantom helper mirrors it for consistency). Revisit with the dp-v2 segment-manifest schema rework alongside b-manifest-join-lossiness (same policy home).
- [edge] G5 emits no verdict-level signal when a dropped phantom's slide is covered by another real segment (witness key `phantom_segment_ids_dropped` records it in the grounded payload; enrique refuse guards the live path at node 12). Consider escalating to a G5 advisory entry at next G5-touching story — would change verdict shape, needs its own ceremony.


## Deferred from: code review of spec-dp-v1-2-hygiene-mini-batch (2026-06-12)

- [edge+blind] Ninth-seam inline-roster regex (tests/audit/test_no_silent_fixture_fallbacks.py) does not match multi-key or multi-row literal rosters; live near-instance exists at app/specialists/gary/_act.py:95 (two-key fabricated roster on the empty-input path, module NOT on ALLOWED_FIXTURE_MODULES). Widen the regex WHEN gary re-bases (taxonomy re-base slice, gary first) — widening now would fire on gary before his fix lands.
- [auditor] quinn_r residual dead subtree one level down: _act_precomposition/_act_postcomposition (+ transitively _invoke_quinn_r_llm, _assemble_quinn_r_prompt) lost their only caller (_run_gate_phase, deleted this batch) yet remain __all__-exported with zero test imports; live act body (quinn_r/_act.py) calls validators directly. Next quinn_r-touching story: either delete the subtree + __all__ rows or document why the export surface stays.
- [blind] _require_bundle_path enforces presence, not run-scopedness — an explicit repo-root bundle_path (".", "runs/enrique-narration") still writes outside a run dir. Callers own scoping today (act() injects); revisit if a non-act caller appears.
