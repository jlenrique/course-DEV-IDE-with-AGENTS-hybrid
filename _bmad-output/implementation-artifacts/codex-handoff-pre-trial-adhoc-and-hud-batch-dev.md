# Codex dispatch: pre-trial Batch 3 — Ad-hoc CLI + HUD modernization

**Session:** 2026-04-26 (operator-authorized; runs AFTER Batches 1+2 close)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor:** Batch 1 (`codex-handoff-pre-trial-batch-dev.md`) closed; Batch 2 (`codex-handoff-pre-trial-defensibility-batch-dev.md`) closed; M5 SHIP-CONDITIONAL window through 2026-05-03 still open.
**Mission:** ship two operator-experience features the migrated runtime does not yet have but the operator will use heavily during and after the conditional window: a runtime ad-hoc CLI for free-form exploration of Marcus, and a HUD modernization that surfaces live trial state instead of legacy data sources.

## Why this batch exists

Two distinct operator surfaces are missing from the migrated runtime:

1. **Ad-hoc / chat mode.** The legacy app had a way for the operator to send free-form prompts to the orchestrator without registering a trial — closest equivalent to "ask Marcus a question and get an answer." The migrated runtime does NOT have this. Today the ONLY runtime entry points are the gate CLI subcommands (`gate decide` / `override submit` / `override apply`), the planned `trial start` (B-extra-A from Batch 1), and direct Python import of `app.marcus.facade`. None of those is suitable for "I want to ask Marcus what would happen if X" or "Marcus, summarize this lesson outline" scenarios.

2. **HUD modernization.** The legacy HUD survives migration as `scripts/utilities/run_hud.py` + `scripts/utilities/progress_map.py` + `tests/test_run_hud.py`, with output at `reports/run-hud.html`. It works structurally (invocable via `python -m scripts.utilities.run_hud`) but reads legacy data sources (sprint-status.yaml, pipeline-manifest.yaml, coordination.db SQLite). It does NOT yet surface migrated-runtime data — RunState, per-trial cost-report.json, LangSmith trace links, gate state from Postgres checkpointer, drift alerts, etc. The HUD is exactly the "where am I in the workflow + what are the constants + what are the current values" reference an operator wants during a real trial. Modernizing it is high-value pre-trial work.

Both are operator-experience features that materially change "sitting for a trial" from "type commands and watch logs" to "engage with the runtime conversationally + see live state at a glance."

**Operator preference (binding, same as Batches 1+2):** "do it right, no band-aids, only rational trade-offs that get named in writing." Substrate-aware adaptation if a path turns out wrong, party-mode where genuinely contested, sandbox-AC discipline throughout.

## Tasks

### B-adhoc — `app.marcus.cli ask` ad-hoc subcommand

**Goal:** add a runtime CLI subcommand that lets the operator send a free-form prompt to Marcus, get a response, without registering a tracked trial. The closest equivalent to legacy ad-hoc mode but built on the migrated LangGraph runtime.

**Behavior contract:**

```bash
.venv/Scripts/python.exe -m app.marcus.cli ask "<your prompt here>"
```

- Accepts a single positional `prompt` argument (multi-word; quote it).
- Optional `--cascade-override <agent>=<model>` flag for one-off model overrides scoped to this invocation only (does NOT mutate `runtime/config/model_cascade.yaml`).
- Optional `--max-tokens <N>` cap on response length.
- Optional `--no-trace` flag to skip LangSmith trace upload (default: trace, but in a separate "ad-hoc" project to keep trial traces clean).
- Optional `--json` flag for machine-readable output.

**What it does NOT do:**
- Does NOT register a trial in `state/config/runs/`.
- Does NOT write to the cost-report (cost is logged inline to stdout instead).
- Does NOT trigger HIL gates (ad-hoc is not a gated workflow).
- Does NOT dispatch the full pipeline (no §01-§15 cascade; just direct Marcus reasoning).
- Does NOT mutate sanctum.

**Implementation shape:**
1. Add `app/marcus/cli/adhoc_cli.py` exporting `adhoc_ask_cli(args) -> int` per the existing `gate_cli.py` shape pattern.
2. Wire into `app/marcus/cli/__init__.py` exports + `build_parser()` in `gate_cli.py` (or refactor to a new top-level `app/marcus/cli/__main__.py` if cleaner — operator decision via party-mode if non-trivial scope creep).
3. Implementation: construct a minimal LangGraph state with the prompt as input; route through `app.marcus.facade.get_facade().ask(prompt, ...)` (NEW facade method); return Marcus's response.
4. The facade `ask` method: invoke the orchestrator's supervisor with the prompt as a single-step query; uses the cascade per the YAML; returns `AdhocResponse(text: str, model_used: str, tokens: TokenCount, cost_usd: float)` Pydantic-strict.
5. CLI prints the response text to stdout + a 1-line cost summary to stderr.

**Pydantic v2 four-file-lockstep for `AdhocResponse`** per the schema checklist (model + JSON Schema + shape-pin tests + golden fixture). Same discipline as 5a.3's `TrialEconomicsReport`.

**Tests:**
- `tests/unit/marcus/test_adhoc_response_strict.py` — 3 tests (strict_config + cost-non-neg + token-shape).
- `tests/integration/marcus/test_adhoc_facade.py` — 2 tests (happy path + cascade-override path; both use `pytest.skip` if OPENAI_API_KEY absent).
- `tests/integration/marcus/test_adhoc_cli.py` — 2 tests (subprocess invocation + JSON output shape).

**Critical scope-bound:**
- This is NOT a "rebuild legacy ad-hoc mode feature-for-feature." If the legacy ad-hoc mode had specific subcommands (e.g., `lesson-summary`, `assessment-draft`), we do NOT port those — they belong in their own follow-on stories if the operator wants them. B-adhoc ships the *foundation*: free-form prompt → runtime → response. Specific operator-facing prompt templates can be operator-side conventions or scripts that wrap the `ask` subcommand.
- Default cascade per current YAML; operator overrides via flag.
- LangSmith trace project: NEW project `course-content-adhoc` (distinct from `course-content-production`) so ad-hoc traces don't mix with trial traces.

**Documentation:**
- `docs/operator/adhoc-mode.md` (NEW) — short page explaining what ad-hoc is, what it isn't, common usage patterns, cost considerations.
- `docs/operator/trial-run-runbook.md` — update §"See also" section to point at adhoc-mode.md (currently mentions Batch 3 as the source of ad-hoc; update to point at the doc once it exists).
- Migration-guide §"Ad-hoc Mode" added.

**Effort:** ~4-6 hours.

**Verification gates:**
- All listed tests pass.
- `python -m app.marcus.cli ask "hello"` returns Marcus's response on a real OpenAI key + skips with clear message when key absent.
- Sandbox-AC validator PASS on any spec authored for this work.
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if new contract added).
- Migration-guide updated.

### B-hud — HUD modernization for migrated runtime

**Goal:** modernize `scripts/utilities/run_hud.py` to surface live migrated-runtime state alongside the existing pipeline-manifest + sprint-status views. The HUD becomes a real operator dashboard for "where am I in the workflow + what are the constants + what are current values."

**What the legacy HUD shows today (preserve):**
- Production run pipeline position (which §-step is active).
- Gate results.
- Dev cycle progress (epics/stories from sprint-status.yaml).
- Critical constants from pipeline-manifest.yaml.

**What the modernized HUD adds (NEW):**

1. **Active-trial section** (when a trial is in flight or recently complete):
   - Trial ID + status (running / paused-at-gate / complete).
   - Current §-step + agent + model in use.
   - Per-agent cost so far (running total).
   - LangSmith trace URL (clickable in the HTML).
   - Drift alerts (last 24h).

2. **Cost-engineering panel** (always visible):
   - Cascade YAML preview (which agent runs which model).
   - Pricing table preview.
   - Median trial cost (last 5 trials) per `migration_health_dashboard.py` rows.
   - Soft-cap budget if `MARCUS_TRIAL_BUDGET_USD` set.

3. **M5 conditional-window panel** (visible while window open):
   - Days remaining in window.
   - Open conditions (1-4) with current resolution status.
   - Ship-state demotion threshold visible.

4. **Ad-hoc mode panel** (post-B-adhoc):
   - Total ad-hoc cost last 24h (if `course-content-adhoc` LangSmith project queryable).
   - Quick-reference template for `python -m app.marcus.cli ask "..."`.

5. **Live update behavior:**
   - Today the HTML uses a JS timer that `location.reload()`s every 10s but data only refreshes when the script reruns.
   - Add a `--watch` flag that re-runs the HUD every N seconds (default 30s), so during a real trial the operator can have it open and see live updates.
   - Document the cost: each `--watch` cycle queries Postgres + reads trace data from LangSmith (cheap) + reads filesystem (free). At 30s intervals this is negligible.
   - Watch mode is optional; non-watch invocation remains a single-snapshot.

**Implementation shape:**
1. Refactor `scripts/utilities/run_hud.py` to a modular structure: each panel is a function returning a chunk of HTML; main `render_html()` composes panels.
2. New module `scripts/utilities/hud_data_sources.py` for the data-fetching layer:
   - `read_active_trial(trial_id: str | None) -> ActiveTrialView | None` reads from `state/config/runs/<trial-id>/` + Postgres checkpointer.
   - `read_cost_engineering_state() -> CostEngineeringView` reads cascade + pricing YAMLs + recent cost reports.
   - `read_m5_window_state() -> M5WindowView` reads `_bmad-output/upstream-state.md` + deferred-inventory.
   - `read_adhoc_summary() -> AdhocSummaryView | None` queries LangSmith `course-content-adhoc` project (post-B-adhoc).
3. Watch-mode loop: simple `while True: render(); sleep(N)`. Honor SIGINT cleanly.
4. CSS/HTML minimal; aim for "operator-readable at a glance," not pretty design. Simple grid + colored status badges.

**Tests:**
- `tests/test_run_hud.py` — extend existing tests to cover new panels (each panel renders with empty data + with populated data).
- `tests/unit/hud/test_hud_data_sources.py` (NEW) — unit tests per data-source function.
- `tests/integration/hud/test_hud_watch_mode.py` (NEW) — invoke `--watch 1 --max-iterations 2` (add this flag for testability) and assert two snapshots produced.

**Compatibility:**
- Preserve the existing CLI surface — `python -m scripts.utilities.run_hud` still works without flags.
- Add new flags additively: `--trial-id`, `--watch`, `--max-iterations`, `--no-adhoc-panel`, etc.
- Output path defaults to `reports/run-hud.html` as today.

**Documentation:**
- `docs/operator/hud-guide.md` (NEW) — what each panel shows; how to use watch mode; how to interpret drift alerts; how to read cost trends.
- `docs/operator/trial-run-runbook.md` §"See also" — update HUD reference to point at hud-guide.md + remove the "HUD modernization in Batch 3" caveat.

**Effort:** ~6-8 hours (modular refactor + 4 new panels + watch mode + tests).

**Verification gates:**
- `python -m scripts.utilities.run_hud --open` produces HTML with all panels visible (some may show "no data" if no trial active — that's expected).
- `python -m scripts.utilities.run_hud --watch 5 --max-iterations 3` produces 3 snapshots cleanly.
- `pytest tests/test_run_hud.py tests/unit/hud tests/integration/hud -q --tb=short` all pass.
- `ruff check scripts/utilities/run_hud.py scripts/utilities/hud_data_sources.py tests/unit/hud tests/integration/hud` clean.
- `lint-imports --config pyproject.toml` — 9 KEPT.
- HUD-guide doc exists.

## What NOT to do in this batch

- **No re-litigating M5.** SHIP-CONDITIONAL is settled.
- **No expansion of ad-hoc to multi-turn conversation.** B-adhoc ships single-prompt-single-response. Multi-turn / interactive REPL is a follow-on if the operator wants it.
- **No HUD UX redesign.** Modernization adds new data; preserve existing structure. A real visual redesign is post-ship 5b polish work.
- **No legacy ad-hoc subcommand porting.** B-adhoc is foundation-only; specific use-case subcommands belong to follow-on stories.
- **No live-API calls during dev.** Tests must skip when keys absent.

## Sequencing

B-adhoc and B-hud are independent surfaces and can run in parallel. Both should land before any operator trial run during the conditional window so the operator has both the conversational entry point and the live dashboard available.

If only one fits in the window: prefer **B-adhoc** for capability completeness (the runtime gains a real feature), and run **B-hud** as a polish follow-on. The HUD already exists in legacy form; modernization is improvement, while ad-hoc is a missing capability.

## Verification gates at batch close

Per task above, plus:
- The 4 new docs exist: `adhoc-mode.md`, `hud-guide.md`, plus migration-guide updates for both.
- Sprint-status reflects any new test additions.
- No B-adhoc or B-hud findings should silently shelve to deferred-inventory; surface in close report.

## Operator-presence work that remains AFTER all three batches

If Batches 1+2+3 land cleanly:
1. M2 Wondercraft live-artifact ceremony (~10-15 min + render).
2. M3 Texas live-retrieval ceremony (~5-10 min).
3. One real trial run through the migrated runtime against live OpenAI (~30-60 min + trial duration). With B-adhoc shipped, operator can also do free-form Marcus exploration as part of the same session. With B-hud shipped, operator has a live dashboard during the trial.

Three operator-windows in one focused session, with strong operator surfaces. After: unconditional SHIP at the next session.

## Carry-forward notes

- B-adhoc adds a new LangSmith project (`course-content-adhoc`); ensure operator's LangSmith Personal Access Key has permissions for project creation, or pre-create the project in the LangSmith UI.
- B-hud watch mode polls; if the operator wants true push-based updates, that's a future story (LangSmith webhooks or Postgres LISTEN/NOTIFY). Watch-poll is acceptable and ships in this batch.
- Repo-wide pytest remains environment-tainted on operator's Windows machine. New tests should be filesystem-friendly where possible; live tests use `pytest.mark.live` (per Batch 1 B3 convention).

## Why this batch matters

The migration shipped a sound runtime but not a sound operator experience around it. The legacy app, whatever its other faults, gave the operator (a) a way to chat with the orchestrator without ceremony, and (b) a HUD that showed state at a glance. The migration's value isn't fully realized if the operator has worse ergonomics post-ship than pre-ship.

This batch closes that gap: ad-hoc as runtime feature (parity with legacy capability); modernized HUD (parity with legacy dashboard, plus migration-runtime-aware additions). After this batch, the operator's day-to-day experience is at-or-above legacy parity.

## Final notes

These two surfaces are bigger than Batch 1's defect-fix work and Batch 2's read-and-report passes. Plan for ~10-14 hours of careful work across both. Halt early and surface if substrate gaps appear (same discipline as 3.1 + 5a.2 + 5a.3 substrate-aware adaptation precedent).

After Batch 3: the operator-experience layer matches the runtime quality, and the conditional window can close with confidence that post-ship operations are well-supported.
