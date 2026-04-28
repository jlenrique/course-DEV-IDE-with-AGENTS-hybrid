# Step 02A Prior-Run Defaults

Step 02A can surface prior `operator-directives.md` content as named defaults for repeated or resumed lesson runs.

## Selection Rule

Marcus first checks the current bundle for `operator-directives.md`. If present and valid, that file is presented for reconfirmation before any older bundle is considered. If present but invalid, Step 02A halts for repair; Marcus does not fall through to older defaults.

If the current bundle has no directives file, Marcus scans sibling tracked source bundles for valid `operator-directives.md` files whose `run-constants.yaml` has the same `lesson_slug` and tracked/default execution mode. The current bundle is excluded. The latest file by modification time wins; identical modification times are resolved by lexicographic `run_id` descending.

Invalid prior directives are ignored and the normal no-prior poll path continues.

## Operator Choices

When a default is presented, Marcus must show the source `run_id`, modified UTC time, source bundle path, source directives path, and the three directive sections. Marcus writes the current run's `operator-directives.md` only after one explicit choice:

- accept prior defaults unchanged: copy only the three directive sections into a new current-run artifact with current `run_id`, current timestamps, and `source_attribution` fields for `prior_run_id`, `prior_bundle_path`, and `accepted_at`
- modify prior defaults
- replace from scratch

The written file must pass `scripts/utilities/validate-operator-directives.py` before replacing any existing current-run directives and before Prompt 3 starts.

## Scope

This helper is a Step 02A pack helper. It does not call Marcus PR-* capability surfaces and does not merge multiple prior runs.
