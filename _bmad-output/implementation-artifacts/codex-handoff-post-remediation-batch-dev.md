# Codex dispatch: post-remediation batch (re-run B3 + B5 + assess B7/B-extra/B-cr)

**Session:** 2026-04-26 (operator-authorized post-Plausible-Token-Substrate-Contamination remediation)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:** Operator-session remediation complete. M5 SHIP-CONDITIONAL conditional window through 2026-05-03 still open. Condition #4 (Plausible-Token Substrate Contamination — REMEDIATED-CODE / PENDING-LIVE-VERIFICATION) added to upstream-state.md.
**Codex prior state:** You were mid-Batch-1 when operator stopped you. ~70 files modified in working tree, NOT committed. Per party-mode round-2 close-review (Quinn-R + Amelia consensus), the pre-stop B3 partial work is HALTED and your tail tasks are re-dispatched here with corrected substrate.

## Why this dispatch exists

Your prior Batch-1 work was substantially correct on B2 (registry-ID alignment) and B9 (dispatch-registry promotion), but B1 (cascade YAML real OpenAI model IDs) replaced one set of fictitious IDs (`gpt-5.4` / `gpt-5-haiku`) with another set of fictitious IDs (`gpt-5.4-nano`). Subsequent operator-session remediation discovered the defect was substrate-wide (not just cascade YAML) and fixed all production-code surfaces. Anti-pattern A15 (Plausible-Token Substrate Contamination) was filed under the new "Post-Cycle Harvest" subheading.

This dispatch picks up your remaining Batch-1 work (B3, B5, B7, B-extra, B-cr) under the corrected substrate. Two are RESTART per Quinn-R's HALT-and-restart call; two are CHERRY-PICK if your prior working tree is salvageable; one (B-cr) is FINAL after the rest lands.

## Operator preferences (binding, same as prior dispatches)

- "Do it right, no band-aids, only rational trade-offs that get named in writing." Substrate-aware adaptation if a path turns out wrong, party-mode where genuinely contested, sandbox-AC discipline throughout.
- The lint guard at `tests/test_no_fictitious_model_ids.py` is non-negotiable structural prevention; do NOT disable it or weaken its scope to make tests pass.
- The catalog-membership test at `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` is the allowlist; if you add a new model_id, add it to `tests/fixtures/openai_catalog_snapshot.json` first.
- Real OpenAI catalog (April 2026): `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o4-mini`. Refer to the catalog snapshot, not historical specs.

## Tasks

### B3-RESTART — live-API smoke scaffolds (clean restart)

**Why restart, not cherry-pick:** Your prior B3 work created partial scaffolds for ~7 providers (canva, consensus, elevenlabs, gamma, kling, langsmith, botpress). Per Quinn-R's read: "Partial scaffolds across 7 providers is exactly the shape of defect that just bit us." Restart with the lint-guard pattern baked in from the start.

**Scope:** author one smoke test per provider with `pytest.mark.live` + skip-when-key-absent + cheap-call discipline.

**Use the existing fixtures already in `tests/live/`:**
- `tests/live/conftest.py` exports `env_value` (skip-when-key-absent) + `timed_call` (latency assertion). Use these.
- `tests/live/test_openai_cascade_tiers_smoke.py` is the operator-session reference shape; mirror it.
- `tests/live/test_langsmith_smoke.py` is your prior pattern; verify it conforms to the reference shape, patch if not.

**Per-provider tests to author (or verify if your prior file exists and is sound):**

| Provider | Cheap call | Test file |
|---|---|---|
| OpenAI | (already shipped per cascade-tier test) | (exists) |
| LangSmith | (already shipped) | (exists; verify) |
| ElevenLabs | voice list | tests/live/test_elevenlabs_smoke.py |
| Wondercraft | capability/account info | tests/live/test_wondercraft_smoke.py |
| Gamma | capability check | tests/live/test_gamma_smoke.py |
| Kling | capability check | tests/live/test_kling_smoke.py |
| Canva | auth check | tests/live/test_canva_smoke.py |
| Qualtrics | survey list | tests/live/test_qualtrics_smoke.py |
| Consensus | quota check | tests/live/test_consensus_smoke.py |
| Notion | workspace info | tests/live/test_notion_smoke.py |
| Botpress | bot list | tests/live/test_botpress_smoke.py |

**Discipline per test (non-negotiable):**
1. Skip cleanly when key absent (use `env_value` fixture).
2. ONE cheap call only (no retries, no multi-step).
3. Assert response shape + non-zero behavior; do NOT assert content.
4. Latency budget < 10s (already enforced by `timed_call`).
5. `pytest.mark.live` so the test doesn't fire in default `pytest` runs.
6. If your test names a model_id, capability slug, or endpoint URL, add it to a vendored snapshot for that provider (mirror `tests/fixtures/openai_catalog_snapshot.json` shape) and add a sibling allowlist test.

**Verify:** `pytest tests/live/ -q -m live` runs without errors when no keys set (everything skips). `pytest tests/live/ -q` (default) does NOT collect any live tests.

**Effort:** ~3-4 hours.

### B5-RESTART — operator-facing doc actualization (clean restart)

**Why restart:** Your prior B5 draft predates the gpt-5 substrate correction. Per Amelia's round-2 read: "docs reference model IDs by name in prose, and Codex's draft predates the gpt-5 substrate correction; restarting is cheaper than line-by-line reconciliation."

**Scope:** refresh 6 operator-facing docs to reflect actual M5 SHIP-CONDITIONAL state + the post-remediation reality.

| Doc | What to update |
|---|---|
| `README.md` | §Status to current SHIP-CONDITIONAL state; §Quick-start to ready-for-trial state; reference real OpenAI catalog where relevant |
| `docs/operator/post-m5-runbook.md` | Already updated in operator session (ACTIVE PATH section). Verify; add anything missed |
| `docs/operator/conditional-gate-addendum-playbook.md` | Name the 5 specific conditions inline (M2 Wondercraft + M3 Texas + 5a.2 launcher + dispatch-registry-RESOLVED + Plausible-Token-Substrate-Contamination-REMEDIATED-CODE-PENDING-LIVE-VERIFICATION); provide exact addendum-paste templates |
| `docs/operator/trial-run-runbook.md` | Already partially updated in operator session. Validate against actual cost-engineering foundation. Reference real model IDs not fictitious. |
| `docs/admin-guide.md`, `docs/user-guide.md`, `docs/agent-environment.md` | Update migration banner to reflect SHIP-CONDITIONAL through 2026-05-03 + M5 condition #4 status |
| `next-session-start-here.md` | M5 SHIP-CONDITIONAL hot-start framing + 4 carried conditions + window expiry + remediation provenance |

**CRITICAL framing-guard (preserve from prior dispatch):** Two distinct "Marcuses" must never be conflated.
1. **Marcus the runtime** — Python service at `app/marcus/`. Operator invokes via `python -m app.marcus.cli ...` (CLI), via FastAPI HTTP, via MCP transport, or via direct Python import. Calls OpenAI APIs through the cascade YAML. **No Claude / Claude Code in the runtime path.**
2. **Marcus the BMAD development persona** — roleplay defined in `skills/bmad-agent-marcus/SKILL.md`. Used in Claude Code sessions for *development* work. Same archetypal voice; entirely separate mechanism.

Trial runs and production runs invoke the runtime, not the BMAD persona. Operator-session edits to `trial-run-runbook.md` and `post-m5-runbook.md` already encode this distinction; preserve.

**Verify:** `grep -rE "in flight|in progress|TBD|forthcoming" docs/ README.md next-session-start-here.md | grep -v "_bmad-output"` returns no migration-status references that should now reflect SHIP-CONDITIONAL state. Run a doc-coverage diff against the diff-stat for visual sanity.

**Effort:** ~2-3 hours.

### B7-CHERRY-PICK — ready-for-trial harness

**Disposition:** assess your prior working-tree state. If `scripts/setup/ready_for_trial.{ps1,sh}` exists and is substrate-correct, cherry-pick it. If it has fictitious model IDs in its validation step, restart.

**Scope reminder:** single-command harness that runs preflight + dashboard + audit + cascade YAML validation + ruff + lint-imports + migration-only pytest slice + the 3 new model-ID guard tests (`test_no_fictitious_model_ids` + `test_cascade_ids_in_openai_published_catalog` + `test_cascade_config_loading`). Single PASS/FAIL banner.

**Add to verification chain (NEW per remediation):** the harness must invoke the lint guard + catalog-membership test before declaring READY FOR TRIAL.

**Effort:** ~30-60 min if cherry-pickable; ~45 min if restart.

### B-extra-ASSESS — production-clone trial launcher

**Disposition:** read your prior working-tree state for `app/marcus/cli/trial.py` (if you authored it) + any related facade additions. Check whether it uses fictitious model IDs anywhere or whether its tests pin to fictitious values. If clean, cherry-pick + verify. If contaminated, restart.

**Scope reminder (from original dispatch):** thin CLI shim at `app/marcus/cli/trial.py` that takes `--preset production --input <corpus-path>`, generates a trial-id, registers in `state/config/runs/<trial-id>/`, invokes the existing Marcus orchestration entry point with the corpus, ensures LangSmith trace upload works, writes the cost report.

**Effort:** ~3-4 hours if restart; ~1-2 hours if cherry-pick.

### B-cr-FINAL — bmad-code-review on post-remediation diff

**Run AFTER** B3-RESTART + B5-RESTART + B7 + B-extra all land. Review covers the entire post-remediation state, not the original Slab 5a diff.

**Diff input:** `git diff <commit-just-before-Codex-stop> HEAD` (compute at run time from `git log --oneline`).

**Spec input:** the 5 Slab 5a story specs + this dispatch + the operator-session remediation provenance (sprint-status.yaml + upstream-state.md + m5-decision.md + anti-pattern A15).

**Mode:** `"full"` (so Acceptance Auditor activates).

**Critical:** the Acceptance Auditor must verify that the executed remediation actually closes A15 (Plausible-Token Substrate Contamination) — every production-code surface must reference only real OpenAI catalog IDs; the lint guard must pass; the catalog-membership test must pass; the live-smoke skeletons must skip cleanly.

**Deliverable:** triaged punch list at `_bmad-output/implementation-artifacts/post-remediation-code-review-2026-04-XX.md` (date when run) with patch/defer/dismiss/decision_needed classification.

**Disposition rules** (same as prior B-cr):
- `patch` items: address before declaring batch done.
- `defer` items: file as deferred-inventory entries with explicit reactivation gates.
- `dismiss` items: explain in close note.
- `decision_needed` items: HALT and surface to operator.

**Effort:** ~2-4 hours (3 layers parallel; triage + patch sequential).

## What NOT to do in this batch

- **No new fictitious model IDs.** The lint guard will catch you. Use real OpenAI catalog only.
- **No re-litigating M5 verdict.** SHIP-CONDITIONAL stands; condition #4 captures the post-vote discovery.
- **No expansion outside the named B3/B5/B7/B-extra/B-cr scope.** Other findings get filed to deferred-inventory.
- **No silent edits to the lint guard or catalog snapshot.** Both are governance artifacts; changes require party-mode if structural.

## Sequencing

1. **Phase A — assessments (parallel):** Read your prior working-tree state for B3, B5, B7, B-extra. Decide cherry-pick vs restart per task. Report your assessments before starting any execution.
2. **Phase B — execution:** B3-RESTART + B5-RESTART (parallel; independent surfaces). Then B7 cherry-pick or restart. Then B-extra assess + execute.
3. **Phase C — final hardening:** B-cr-FINAL on the post-Phase-B state.

## Verification gates at batch close

- `pytest tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` — both PASS.
- `pytest tests/live/ -q -m live` — runs without errors when no keys set; all tests skip cleanly.
- `pytest <relevant-slice>` — green per task.
- `ruff check <touched surfaces>` — clean.
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if contracts added).
- `bash scripts/setup/ready_for_trial.sh` (or `.ps1`) — exits 0 with READY FOR TRIAL banner (after B7).
- B-cr punch list addressed: `patch` items have commits; `defer` items in deferred-inventory; `dismiss` items justified; `decision_needed` items surfaced.

## Operator-presence work that remains AFTER this batch

If everything in this batch lands cleanly:

1. **Live-OpenAI cascade-tier smoke** (~3 min, ~$0.0003) — closes M5 condition #4.
2. **M2 Wondercraft live-artifact ceremony** (~10-15 min + render).
3. **M3 Texas live-retrieval ceremony** (~5-10 min).
4. **One real production-clone trial run** through the migrated runtime against live OpenAI (~30-60 min + trial duration). Closes condition #3.

Four operator-windows in one focused session, with strong operator surfaces. After: unconditional SHIP at the next session.

## Carry-forward notes

- Operator-session remediation added 5 deferred-inventory entries (Layer-1/Layer-2 cascade collapse, OpenAI catalog snapshot staleness CI guard, tautology audit on cost/router fixtures, full perturbation procedure, broader silent-substrate audit). These are NOT in this batch's scope; they're tracked for post-trial follow-up.
- Repo-wide pytest remains environment-tainted on operator's Windows machine. Document any new tests with a Windows-tainted note if they trip the issue.
- The Plausible-Token Substrate Contamination defect is documented as anti-pattern A15 under the "Post-Cycle Harvest" subheading at `docs/dev-guide/specialist-anti-patterns.md`. New entries follow that pattern (post-cycle additions go under that subheading; do NOT retroactively edit the cycle-complete annotation).

## Final notes

This batch closes the Batch-1 tail under the corrected substrate. Operator's "do it right" preference held: the remediation was discovered, ratified by party-mode, executed, validated by party-mode close-review, and tracked in writing through anti-pattern catalog + M5 condition + deferred-inventory + sprint-status.

After this batch + the operator-presence work above, the migration's M5 SHIP-CONDITIONAL window can close to unconditional SHIP with full evidentiary integrity intact.
