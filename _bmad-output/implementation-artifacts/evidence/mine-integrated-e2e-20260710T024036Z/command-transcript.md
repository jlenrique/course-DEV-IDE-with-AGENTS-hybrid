# Integrated Six-Mine E2E transcript — 20260710T024036Z
primary_run_id: 8099669e-e677-4578-9889-a62250c38fb0

## Step 1 — plan-dialogue
plan-dialogue exit=0
## Step 2 — live Irene Pass-1
irene plan_json=True md=True collateral_forced=False
## Step 3 — auto-derive ComponentSelection
derived source=plan_collateral bundle=narrated-deck-with-workbook selection={'deck': True, 'motion': True, 'workbook': True}
negative absent-collateral fail-loud=True
## Step 4 — trial start consumes selection
trial_spy captured selection_match=True keys=['allow_offline_cost_report', 'component_selection', 'corpus_path', 'directive_path', 'operator_id', 'pause_at_gates', 'preset', 'runs_root', 'trial_id']
CLI --lesson-plan-json resolve ok=True
## Step 5 — SME resolution
sme tejal_bound=True hai_gap=True unknown_fail=True diverged=['sme_key', 'styleguide_id', 'attribution', 'approval_route', 'voice_profile_ref', 'unbound', 'fallback']
## Step 6 — adjuncts (canonical / drill / prose)
adjuncts leaf=True run_dir=True drill=practice-drill.md empty_refused=True prose_markers_cleared=True
