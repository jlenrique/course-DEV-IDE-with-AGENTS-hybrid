---
title: 'malformed-plan-json selection negatives — fail-loud pins at trial start'
type: 'feature'
created: '2026-07-11'
status: 'done'
review_loop_iteration: 1
final_revision: '7f0035019f902260d473e72862f37fa5682ff672'
baseline_revision: 'ca064d52df06bd501b43404e44375ad3120241ca'
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The plan-json selection path has fail-loud behavior for every malformed shape (`CollateralSelectionError` with distinct messages) but almost no negative coverage: only the happy-path round-trip and one derive-level negative are pinned. Nothing drives `--lesson-plan-json` through the CLI with a bad file, and the programmatic sniff's fall-through (a dict with no `ratification_status` and no plan keys routes to the intent loader and binds nothing) is unpinned. Deferred residual `malformed-plan-json-selection-negative` (Phase-2 six-mine CLOSE-amendment).

**Approach:** Test-only. Add unit negatives for `load_selection_from_lesson_plan_json` / `derive_selection_from_lesson_plan` covering the five malformed shapes; add one CLI integration negative for `--lesson-plan-json` (exit 1, clean stderr, no run.json — replicating the existing invalid-intent CLI negative pattern); add one programmatic pin of the sniff fall-through routing.

## Boundaries & Constraints

**Always:** Hermetic (no API keys, no live walk — the fail-loud fires before `run_production_trial`; use the established `_spy` monkeypatch only where a test must pass the resolve stage). Use `.venv/Scripts/python.exe -m pytest`. Match existing test-file conventions (fixtures, `tmp_path`, `capsys`, `monkeypatch`, `_pin_g0_enrichment_off` autouse in test_trial_cli.py). Assert on the distinct error-message substrings already emitted by `collateral_selection.py`.

**Block If:** Any test reveals the documented fail-loud behavior does NOT hold (that would be a production bug needing a human-gated fix, not a quiet test adjustment).

**Never:** No production-code changes. No new test *frameworks* or fixtures beyond the established patterns. No live LangGraph walk. Do not "fix" the sniff fall-through — pin it as-is (its design disposition is a filed defer).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Missing file | `--lesson-plan-json` path does not exist | `CollateralSelectionError` | msg contains "does not exist" |
| Invalid bytes | file with invalid UTF-8/unparseable YAML | `CollateralSelectionError` | msg contains "not valid JSON/YAML" |
| Non-object top level | file decodes to a list/scalar | `CollateralSelectionError` | msg contains "must decode to an object" |
| Wrapper missing plan | `{"lesson_plan": 42}` | `CollateralSelectionError` | msg contains "missing plan object" |
| Missing collateral key | plan dict without `collateral` | `CollateralSelectionError` | msg contains "collateral is required" |
| Bad collateral shape | `collateral` fails CollateralSpec validation | `CollateralSelectionError` | msg contains "failed CollateralSpec validation" |
| CLI bad plan-json | `trial start ... --lesson-plan-json <malformed>` | exit code 1, one-line `ERROR:` on stderr | no `run.json` written; no traceback |
| Sniff fall-through | `start_trial(lesson_plan_collateral_intent_path=)` dict with no `ratification_status`, no plan keys | routes to intent loader, resolves `source="unratified"`, binds nothing (default selection preserved) | no exception (current behavior, pinned) |

</intent-contract>

## Code Map

- `app/marcus/lesson_plan/collateral_selection.py:294-318, 249-291` — loaders under test (read-only; message anchors).
- `app/marcus/cli/trial.py:662-732 (_resolve_start_component_selection), 735-767 (start_trial_cli catch → "ERROR:" + exit 1), 391-441 (programmatic sniff)` — read-only.
- `tests/marcus/lesson_plan/test_collateral_selection.py` — ADD unit negatives (six shapes above) plus 0-byte file (fires "must decode to an object") and YAMLError arm (`{unclosed: [` fires "not valid JSON/YAML"). Use the UNIQUE message anchors: "lesson-plan JSON file does not exist", "lesson_plan.collateral is required", and include "declaration" in the bad-shape match. Top-level imports, no per-test re-imports.
- `tests/integration/marcus/test_trial_cli.py` — ADD one CLI negative `test_trial_start_cli_rejects_malformed_lesson_plan_json` modeled on ~L472; assert the `"ERROR: "` stderr prefix + "lesson_plan.collateral is required"; no dead "Traceback" assertion; no run.json.
- `tests/integration/marcus/test_trial_plan_json_selection.py` — ADD programmatic sniff pins that OBSERVE ROUTING: monkeypatch-spy `app.marcus.cli.trial.load_lesson_plan_collateral_selection` AND `app.marcus.cli.trial.load_selection_from_lesson_plan_json` (record call args, delegate to real fn). Pin (a) fall-through `{"note":...}` → intent-loader spy called with the path, plan-loader spy NOT called, captured component_selection is None; (b) sniff boundary: `{"plan_units": [], "ratification_status": "draft"}` → PLAN loader (raises "collateral is required") — pins the `!= "ratified"` predicate arm. Single start_trial call per pin (no redundant comparison call).

## Tasks & Acceptance

**Execution:**
- [x] `tests/marcus/lesson_plan/test_collateral_selection.py` — add 6 unit negatives per I/O matrix rows 1-6 — closes the loader-level gap.
- [x] `tests/integration/marcus/test_trial_cli.py` — add CLI negative (row 7) — closes the trial-start fail-loud gap named by the residual.
- [x] `tests/integration/marcus/test_trial_plan_json_selection.py` — add sniff fall-through pin (row 8) — converts the review-filed drift risk into a pinned contract.

**Acceptance Criteria:**
- Given the new tests, when run with `.venv/Scripts/python.exe -m pytest <the three files> -q`, then all pass hermetically with no API keys.
- Given the full pre-existing suites in those three files, when run, then zero regressions.
- Given `git diff`, when inspected, then only the three test files changed.

## Spec Change Log

- **2026-07-11 loop 1 (bad_spec):** Review mutation probe proved the sniff fall-through pin hollow — spec had prescribed observing only `captured["component_selection"] is None`, which passes even with the whole programmatic seam deleted. Code Map amended to require loader-spy routing observation + the `!= "ratified"` boundary pin; unique message anchors mandated; dead Traceback assertion and redundant comparison call removed; 0-byte + YAMLError arms added. **KEEP:** the six unit-negative scenarios and the CLI-negative scaffolding (delenv trio + `_load_env_if_available` stub + `_pin_g0_enrichment_off`, `tests/fixtures/trial_corpus/README.md` corpus, tmp_path runs-root, no-run.json assert) worked well — preserve their structure, upgrading only the match anchors. Known-bad state avoided: assertions that cannot distinguish routed-and-bound-nothing from silently-ignored.

## Review Triage Log

### 2026-07-11 — Review pass (loop 0)
- intent_gap: 0
- bad_spec: 1: (high 1, medium 0, low 0)
- patch: 0 (folded into loopback re-derive)
- defer: 1: (low 1)
- reject: 3
- addressed_findings:
  - `[high]` `[bad_spec]` mutation probe proved the sniff fall-through pin hollow (passed with the seam deleted) — spec had prescribed a non-observing assertion. Spec Code Map amended (loader-spy routing observation + boundary pin + unique anchors + 0-byte/YAMLError arms); code reverted and re-derived.

### 2026-07-11 — Review pass (loop 1)
- intent_gap: 0
- bad_spec: 0
- patch: 5: (high 0, medium 2, low 3)
- defer: 1: (low 1)
- reject: 4
- addressed_findings:
  - `[medium]` `[patch]` ratified-stamped plan-shape arm unpinned (deleting the `!= "ratified"` conjunct survived) — added routing pin (intent loader called, plan loader not).
  - `[medium]` `[patch]` wrapper-shape sniff disjunct unpinned — added routing pin ({"lesson_plan": {...}} → plan loader).
  - `[low]` `[patch]` fall-through docstring overclaimed source="unratified" (not observed) — softened.
  - `[low]` `[patch]` CLI test name said "malformed" for well-formed-JSON-missing-collateral — renamed.
  - `[low]` `[patch]` declaration negative could pass on any validation error — added "Input should be" anchor (closed-Literal arm).

## Auto Run Result

- **Summary:** Deferred residual `malformed-plan-json-selection-negative` cleared: 12 new hermetic tests pinning every plan-json fail-loud arm (8 loader negatives incl. 0-byte + YAMLError), the CLI trial-start negative (exit 1, ERROR: prefix, no run.json), and 4 routing-observed sniff pins (fall-through, draft-stamped, ratified-stamped, wrapper shape) with a designed-in mutation kill.
- **Files changed:** tests/marcus/lesson_plan/test_collateral_selection.py (+93), tests/integration/marcus/test_trial_cli.py (+45), tests/integration/marcus/test_trial_plan_json_selection.py (+189). Test-only.
- **Review breakdown:** loop 0 → 1 bad_spec (hollow pin, mutation-proven) triggered spec amendment + re-derive; loop 1 → 5 patches applied, 2 defers filed (sniff swallow-arm routing; plus loop-0's), 7 rejected across passes (pre-existing file conventions the spec mandated matching).
- **Verification:** 45 passed hermetically across the three files; self-mutation check on the seam predicate kills via the pin pair; edge-hunter pass 2 returned zero findings with empirical confirmation of every construct.
- **Residual risks:** production comment at trial.py ~396-402 asserts the wrong arm for draft-stamped companions (pre-existing from iteration 1's review patch — routed to orchestrator for an out-of-spec docs fix); `lesson_plan_selection_source` receipt remains unasserted anywhere (existing defer).
