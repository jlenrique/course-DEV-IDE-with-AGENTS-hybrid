---
id: 41-1
epic: 41
status: ready-for-dev
depends_on: null   # first story of the arc; BLOCKING — unblocks resuming any paid walk past G1
gate_mode: single-gate
anchor_provenance: HEAD 23480353  # all line anchors verified against this tree; re-verify at dev-open
baseline_commit: 23480353273418c785740dcd68fc877f753ff547  # dev-open baseline 2026-07-16
---

# Story 41.1: Resume/recover live-env preflight — a keyless resume fails loud at the front door

Status: done  # 2026-07-16 dev complete (fresh Claude dev agent) + bmad-code-review 3-layer PASS-after-remediation; single-gate; not lockstep

## Story

As the operator steering a paid Marcus-SPOC production trial,
I want `trial resume` / `trial recover` to refuse loudly when the live LLM env is missing — exactly as `trial start` already does —
so that a resume from a fresh shell without `OPENAI_API_KEY` never silently degrades into a no-dispatch walk that strands the run three nodes later with a misattributed error.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `_bmad-output/planning-artifacts/epics-resume-walk-dispatch-integrity-2026-07-16.md` §Story 41-1 (E41-AC1).
- **Green-light:** `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (amendment P-1: A and B are one defect, two stories; 41-1 is the front-door guardrail and ships first).
- **Root-cause evidence:** frozen trial `bc747b51` — CD node 4.75 entered (`operator-surface.json`), zero CD calls (`cost-report.json`), envelope stops at `research_wiring @ 04.55` (`run.json`), `allow_offline_cost_report=False` (persisted runner). The operator resumed from a fresh PowerShell without the key (documented gotcha: gate pause returns to PowerShell). `start_trial` (`trial.py:390-396`) enforces the key; resume/recover do not.
- **DAG:** 41-1 → 41-2. 41-1 is independently shippable and unblocks honest recovery of `bc747b51` (recover with the key set).

## T1 Readiness (BINDING readings before any code)

1. `app/marcus/cli/trial.py` — `start_trial` preflight (L390-396): `if not allow_offline_cost_report and (not os.getenv("OPENAI_API_KEY") or not _has_langsmith_env()): raise RuntimeError(...)`. This is the EXACT shape to mirror.
2. `app/marcus/cli/trial.py` — `resume_trial` (L850), `resume_trial_cli` (L935), `recover_trial` (L992), `recover_trial_cli` (L1053), `resume_batch_trial`/`resume_batch_trial_cli` (L1136/L1171). Identify each continuation entry point that leads into `_continue_production_walk` and whether it carries an `allow_offline_cost_report` flag (persisted in `runner`).
3. `app/marcus/orchestrator/production_runner.py` — `_has_live_openai` (L211-212 = `bool(os.getenv("OPENAI_API_KEY"))`), `_has_langsmith_env` (L215-217). The preflight must gate on the SAME predicate the dispatch branch reads, so preflight-pass ⇒ dispatch-live.
4. The persisted `runner.allow_offline_cost_report` on a paused run (`error-pause.json` / `run.json`) — the preflight must honor `--allow-offline-cost-report` continuations (offline harness) exactly as `start_trial` does, and read the flag from the same place the walk will.

## Acceptance Criteria

1. **Resume/recover preflight parity with start.** `resume_trial` and `recover_trial` (and `resume_batch_trial`) apply the same live-env preflight as `start_trial`: when the continuation will run live (`allow_offline_cost_report` is False for that run — read from the persisted `runner`, not re-defaulted), a missing `OPENAI_API_KEY` **or** missing LangSmith env raises a `RuntimeError` **before** `_continue_production_walk` is entered. The message is actionable and names the missing variable(s) and the resume context, e.g. `"OPENAI_API_KEY (and LANGSMITH_API_KEY/LANGSMITH_PROJECT) are required to resume production trial <id>: a keyless resume would silently skip live specialist dispatch. Export the key or use --allow-offline-cost-report for offline harness checks."`
2. **Offline continuations still work.** A run persisted with `allow_offline_cost_report=True` (offline harness) resumes/recovers WITHOUT the env requirement — the preflight is gated on `not allow_offline_cost_report`, byte-identical to the `start_trial` condition. No behavior change for offline harness resume paths.
3. **Predicate agreement (anti-drift).** The preflight reads `os.getenv("OPENAI_API_KEY")` / `_has_langsmith_env()` — the SAME predicates `production_runner._has_live_openai` / `_has_langsmith_env` read — so a preflight PASS guarantees the resume walk's specialist-dispatch guard is live. Pin this agreement (a test that asserts preflight-pass ⇒ `_has_live_openai()` True).
4. **Frozen-run reproduction.** A test reconstructs the `bc747b51` resume entry with `OPENAI_API_KEY` unset and `allow_offline_cost_report=False` and asserts the resume raises the actionable `RuntimeError` at the front door — NOT a walk that reaches node 06 with a missing `cd`. (Uses the persisted `runner`/envelope shape; no live call, no network.)
5. **Batch-resume covered.** `resume_batch_trial`/`resume_batch_trial_cli` get the same preflight (batch mode still dispatches live specialists on continuation). If batch has a distinct offline path, honor it identically to realtime.

## Scope Fences (hard NO)

- **NO changes to `production_runner.py`** — that's 41-2 (the fail-loud invariant at the node). 41-1 is the CLI front door only. (If 41-1 and 41-2 are implemented in one head per P-1, they remain two diffs / two stories.)
- **NO change to the offline-harness contract** — `--allow-offline-cost-report` resume must stay keyless.
- **NO new env var** — reuse `OPENAI_API_KEY` + the existing `_has_langsmith_env()` contract.
- **NO auto-loading of `.env` inside resume** — the fix is to FAIL LOUD, not to silently source a key the operator didn't set (that would mask the very misconfiguration we want surfaced). Coaching the operator to export the key is the intended UX.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/cli/trial.py` | not listed | yes (resume/recover/resume-batch preflight) |
| `app/marcus/orchestrator/production_runner.py` | **trigger** | **NO** (41-2 owns it) |

**Verdict: zero trigger paths touched — lockstep regime not triggered.** Any drift into `production_runner.py` is a STOP → that's 41-2.

## Dev Notes

- Extract the `start_trial` preflight into a small shared helper (e.g. `_require_live_env_unless_offline(*, allow_offline_cost_report, trial_id, context)`) so start/resume/recover/resume-batch all call one implementation — Yui's anti-duplication note; the four call sites must not drift. Keep the raised message context-specific (start vs resume vs recover) via a `context` arg.
- Read `allow_offline_cost_report` from the persisted `runner` dict on the paused run (same source `_continue_production_walk` reads at L4150: `runner.get("allow_offline_cost_report", False)`), so the preflight decision matches the walk's decision exactly.
- Tests: `tests/marcus/cli/test_trial_resume_preflight.py` (new) — keyless resume raises; offline resume passes; predicate-agreement pin; batch-resume covered; frozen-`bc747b51`-shape reproduction (persisted runner fixture, `OPENAI_API_KEY` monkeypatched-absent). No live LLM, no network.

## References

- `_bmad-output/planning-artifacts/epics-resume-walk-dispatch-integrity-2026-07-16.md`
- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md`
- `_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md` §6
- `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/{error-pause.json,run.json,cost-report.json}`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Winston/John/Amelia/Murat/Sally, orchestrator concurred (party record above). Folded: P-1 (two-story split); Murat's frozen-run reproduction AC; Winston's predicate-agreement pin; the "fail-loud not auto-source-.env" fence (do not mask the misconfiguration). Status → ready-for-dev.

## Dev Agent Record

**Dev complete 2026-07-16 (fresh Claude dev agent, general-purpose subagent). Baseline `23480353`. Status → review → done (post code-review remediation).**

### File List
- `app/marcus/cli/trial.py` (M) — new `_require_live_env_unless_offline` + `_persisted_allow_offline_cost_report` helpers; `start_trial` inline preflight refactored to the shared helper (`context="start"`, byte-identical message); preflight inserted into `resume_trial` (reads `checkpoint.json`), `recover_trial` (reads `error-pause.json`), `resume_batch_trial` (reads `provider-batch-pause.json`) after their existing `_load_env_if_available()`.
- `tests/integration/marcus/test_trial_resume_preflight.py` (A) — 10 hermetic tests (AC-1..AC-5).
- `tests/unit/marcus/cli/test_trial_start_picker_preflight.py` (M) — **code-review remediation**: `test_resume_and_recover_never_prompt` now seeds `checkpoint.json`+`error-pause.json` with `{"runner":{"allow_offline_cost_report":true}}` so the new preflight short-circuits (offline), keeping the test hermetic without `.env` (house idiom per `test_trial_legacy_workbook_migration_36_4.py`).

### Completion Notes
- Shared helper unifies all four front doors (start/resume/recover/resume-batch) on ONE preflight; gate byte-identical to the original `start_trial` condition; offline (`allow_offline_cost_report=True`) stays keyless. `allow_offline_cost_report` read from the SAME persisted `runner` the continuation walk rehydrates (verified: resume←checkpoint.json, recover←error-pause.json, batch←provider-batch-pause.json all match `production_runner`'s rehydration + the `:4150` flag read).
- Root cause confirmed: `env_loader.load_env` uses no-override semantics (`key not in os.environ`), so an empty/unset `OPENAI_API_KEY` in the resume shell → `_has_live_openai()` falsy → CD silently skipped. The preflight (running after the pre-existing `_load_env_if_available()`, checking the same predicate) now fails loud on exactly that, coaching "export the key."
- `production_runner.py` untouched (41-2 owns the node-level fail-loud). No `.env` auto-load added; no new env var; offline contract unchanged.

### Change Log
- 2026-07-16: implemented live-env preflight parity for resume/recover/resume-batch (Story 41-1); code-review remediation (1 Med: test hermeticity) applied; done.

## Senior Developer Review (AI) — 2026-07-16

**Reviewer:** orchestrator via `bmad-code-review` (3 parallel adversarial layers: Blind Hunter, Edge Case Hunter, Acceptance Auditor — fresh contexts, same model tier). **Outcome: APPROVE (after remediation).**

**Acceptance Auditor:** PASS on all AC-1..AC-5; all Scope Fences held; `start_trial` refactor byte-behavior-identical; no existing test pins the start message.

**Edge Case Hunter:** load-bearing concerns verified clean — pause-file/field parity exact across all three continuations; all malformed pause shapes (`absent`/`""`/`{}`/`{"runner":null}`/list) fail safe to live-required; offline short-circuit correct; empty-string key falsy→raises agreeing with the walk guard.

**Blind Hunter:** found the one real regression (below).

**Action items:**
- ✅ **[Med — FIXED] Existing `test_resume_and_recover_never_prompt` was non-hermetic** — the new preflight made it depend on `.env` (empty run dir + no seeded runner → require-live → raised when `.env` absent). CONFIRMED by moving `.env` aside (CI simulation): test failed; with `.env`: passed. Remediated by seeding offline pause records (house idiom); re-verified: `tests/unit/marcus/cli/` = 115 passed WITHOUT `.env`, 11 passed WITH.
- ⚖️ **[Med — ADJUDICATED intended] Preflight requires LangSmith but the walk's *dispatch* guard checks only OPENAI.** Correct parity: `start_trial` already requires LangSmith and `_has_production_evidence` (`production_runner.py:1832`) needs it, so a live run without LangSmith earns no production evidence — and a paused live run always had LangSmith at start (start would have refused otherwise). Blocking a resume shell that dropped LangSmith is correct, per spec AC-1. Not a regression (the "used to work" start-without-LangSmith state is unreachable).
- 📝 **[Low — DOCUMENTED residual, not fixed] Non-empty invalid/placeholder `OPENAI_API_KEY` passes the preflight** (truthiness-only, consistent with the walk's own guard and with `start_trial`). Out of scope for 41-1; validating a key requires a live call. Inherent property of every key check in this codebase; not filed as a follow-on (no inventory value).
- 📝 **[Low — DISMISSED] Empty-string-`OPENAI_API_KEY`-shadows-`.env` message** — the message already coaches "export the key," which is a working remedy under no-override `load_env`. Adequate.
- 📝 **[Low — DISMISSED] Error-precedence** (preflight before verdict/status validation) — env-first fail-loud is defensible; a keyless resume can do nothing regardless.

**Verification at close:** new preflight suite 10/10; fixed existing test hermetic (115 passed without `.env`); ruff clean on all touched files; `production_runner.py` untouched; pre-existing unrelated failure `test_start_trial_ratified_collateral_intent_runs_local_runtime` stash-witnessed at baseline (not introduced by this story).
