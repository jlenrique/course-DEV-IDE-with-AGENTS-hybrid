# Codex dispatch: pre-trial Batch 1 (B1+B2+B3+B5+B7+B9 + B-extra + B-cr)

**Session:** 2026-04-26 (operator-authorized post-Slab-5a-close, M5 SHIP-CONDITIONAL window through 2026-05-03)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor:** Slab 5a closed (commits `649c3a6` 5a.1 → `9e244c3` 5a.2 → `383ff18` 5a.3 → `04d6c21` 5a.4 → `24c4899` 5a.5).
**Mission:** maximize the migrated runtime's production-readiness BEFORE the operator sits down to run the first real trial. Reduce the operator-window work from "validate everything end-to-end" to "execute the M2/M3 ceremonies + run one real trial."

## Why this batch exists

Operator wants to be able to sit down for a single focused trial-run session and have the runtime work without surprises. The M5 SHIP-CONDITIONAL verdict named 4 carried conditions; this batch closes one of them (B9) and prepares the substrate so that the operator's real trial run validates the other 3 conditions cleanly rather than uncovering new defects.

Two findings surfaced during the post-Slab-5a review that this batch fixes (B1, B2). Three add new value the operator will need (B3, B5, B7). One closes an M5 condition (B9). One optional task (B-extra) builds the production-clone launcher Codex documented as missing in 5a.2 — if scoped tight, this could close a second M5 condition.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Same discipline as Slab 5a — substrate-aware adaptation if a path turns out wrong, party-mode where genuinely contested, sandbox-AC discipline throughout.

## Tasks (run in roughly this order; many can parallelize)

### B1 — Cascade YAML real OpenAI model IDs

**Problem:** `runtime/config/model_cascade.yaml` declares `gpt-5.4` and `gpt-5-haiku`; `runtime/config/openai_pricing.yaml` adds `gpt-5-codex`. None match OpenAI's real catalog. Live calls would 404. The YAML even claims these are "registry-backed model ids" — they aren't.

**Fix:**
1. Read OpenAI's current model catalog (assume the operator-D5 default: `gpt-5` for frontier, `gpt-5-mini` for mid-tier, `gpt-5-nano` for narrow-task; verify against current OpenAI public docs at implementation time — if `gpt-5` isn't shipped yet by April 2026, fall back to `gpt-4.1` / `gpt-4.1-mini` / `gpt-4o-mini` per current OpenAI Public availability).
2. Update `runtime/config/model_cascade.yaml`: replace `gpt-5.4` → frontier ID; `gpt-5-haiku` → narrow-task ID. Preserve all rationale strings.
3. Update `runtime/config/openai_pricing.yaml`: replace fictitious model IDs with real ones; populate `input_per_1m_tokens_usd` / `output_per_1m_tokens_usd` from current OpenAI public pricing at implementation time.
4. Re-run `python -m app.runtime.economics --trial C1-M1-PRES-20260419B` (or equivalent CLI) against the synthetic fixture to confirm pricing math still works.
5. Update the characterization baseline at `_bmad-output/economics-baselines/migrated-runtime-characterization-2026-04-26.md` if cost numbers shift. Note the model-ID correction in the characterization preamble.
6. Update the cascade/pricing digest values in any test fixtures that pinned them.

**Verify:** unit tests in `tests/unit/runtime/` still pass; `tests/integration/runtime/test_pricing_table_covers_cascade.py` still passes; characterization baseline regenerates cleanly.

**Time estimate:** ~30-45 min.

### B2 — Cascade YAML registry-ID alignment

**Problem:** Cascade YAML uses persona names (`irene`, `gary`, `kira`, `cd`, `enrique`); the specialist registry at `skills/bmad-agent-marcus/references/specialist-registry.yaml` uses different IDs (`content-creator`, `gamma-specialist`, `kling-specialist`, `creative-director`, `elevenlabs-specialist`). Aliases exist for `quinn-r → quinn_r` and `elevenlabs → enrique` only. A real lookup keyed on registry IDs would miss most agents.

**Fix:** Pick ONE direction:

- **Option A (preferred):** invert the cascade. Use registry IDs as cascade keys (`content-creator: ...`, `gamma-specialist: ...`, etc.); add `aliases: [irene]`, `aliases: [gary]`, etc. to each entry for human-readable persona names.
- **Option B:** keep persona names as cascade keys; add full alias coverage so every registry ID resolves (`irene` entry gains `aliases: [content-creator]`, etc.).

Pick Option A unless a substrate dependency forces Option B. Document the choice in the cascade YAML header comment.

**Verify:** add `tests/integration/runtime/test_cascade_registry_alignment.py` (1 test) that loads the cascade + the registry, then asserts every active registry ID resolves to exactly one cascade entry (via key OR alias). No silent misses.

**Time estimate:** ~30-45 min.

### B3 — Live-API smoke test scaffolds

**Problem:** No live-API smoke tests exist for any provider. The architecture is wired; live exercise is operator-window work. When the operator finally sits down to run a trial, any provider that breaks costs operator presence to debug. Scaffolds let issues surface earlier (when operator sets a key and runs `pytest tests/live/`) rather than mid-trial.

**Build:**
1. `tests/live/__init__.py` + `tests/live/conftest.py` with a shared `pytest.fixture` that returns the API key for a given provider or skips if unset (`pytest.skip(f"{key_name} not set in env")`).
2. One smoke test per provider, each with a single GET / cheap call:
   - `tests/live/test_openai_smoke.py` — model list call (free); verifies key + auth.
   - `tests/live/test_langsmith_smoke.py` — workspace info / project list (free).
   - `tests/live/test_wondercraft_smoke.py` — capability list / account info (free if available; otherwise document the cheapest live call).
   - `tests/live/test_elevenlabs_smoke.py` — voice list (free).
   - `tests/live/test_gamma_smoke.py` — capability check.
   - `tests/live/test_kling_smoke.py` — capability check.
   - `tests/live/test_canva_smoke.py` — auth check.
   - `tests/live/test_qualtrics_smoke.py` — survey list (cheap).
   - `tests/live/test_consensus_smoke.py` — quota check.
   - `tests/live/test_notion_smoke.py` — workspace info.
   - `tests/live/test_botpress_smoke.py` — bot list.
3. Each test pattern: `(a)` skip if key absent; `(b)` make ONE cheap call; `(c)` assert response shape; `(d)` assert latency < 10s. NO retries, NO follow-up calls, NO state mutation.
4. Add to `pyproject.toml` an optional `[project.optional-dependencies]` block named `live-smoke` listing the providers' Python deps if any are not already shipped.
5. Document in `docs/dev-guide/live-smoke-testing.md`: "set the env vars listed in `.env.example`, then run `pytest tests/live/ -q`. Tests skip when keys absent."

**Critical:** these tests **must not appear in the default `pytest` run** (don't want them firing on every dev machine + burning quota). Mark with `@pytest.mark.live` and add `addopts = "-m 'not live'"` to `pyproject.toml [tool.pytest.ini_options]` (or extend existing config).

**Verify:** `pytest tests/live/ -q -m live` runs without errors when no keys set (everything skips). `pytest tests/ -q` (default) does NOT collect or run any live tests.

**Time estimate:** ~2-3 hours.

### B5 — Doc actualization to SHIP-CONDITIONAL state

**Problem:** Several operator-facing docs were written before the M5 verdict; they speculate about what shipping would look like. Now that the verdict is real, they should describe the actual state.

**Update:**

1. **`README.md`** — update §Status to read "M5 SHIP-CONDITIONAL accepted 2026-04-26; conditional window through 2026-05-03; remaining conditions: [list 4]." Update §Quick-start to reflect the actual ready-for-trial state.

2. **`docs/operator/post-m5-runbook.md`** — replace the "if/then per verdict path" speculative content with the actual SHIP-CONDITIONAL path now active. Concrete steps: how to run M2 ceremony, how to run M3 ceremony, how to run a real trial, how to confirm `migration-master-status` flip from `shipped` to unconditional shipped, how to handle the demotion case if 2026-05-03 lapses.

3. **`docs/operator/conditional-gate-addendum-playbook.md`** — name the 4 specific conditions inline. Provide the exact addendum-paste templates for the M2 verdict file (`_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`) and M3 verdict file. Include the deferred-inventory cleanup commands.

4. **`docs/operator/trial-run-runbook.md`** — validate against the actual cost-engineering foundation. Update cost-cap discussion to reference `MARCUS_TRIAL_BUDGET_USD` env per D7. Reference the cascade YAML location for "if you want to swap a model." Reference the per-trial cost-report location at `state/config/runs/<trial-id>/cost-report.{json,md}`.

5. **`docs/admin-guide.md`, `docs/user-guide.md`, `docs/agent-environment.md`** — update the migration banner from "in flight" to "M5 SHIP-CONDITIONAL through 2026-05-03; see `_bmad-output/upstream-state.md` for current ship state." Strip any forward-looking "we plan to" language now superseded by actual ship.

6. **`next-session-start-here.md`** — replace stale Slab 5a opening framing with M5 SHIP-CONDITIONAL hot-start: current verdict, 4 carried conditions, window expiry, what the operator typically does first in a session during the conditional window.

**Verify:** `grep -r "in flight\|in progress\|TBD\|forthcoming" docs/ README.md next-session-start-here.md | grep -v "_bmad-output"` returns no migration-status references that should now reflect SHIP-CONDITIONAL state. Run a doc-coverage diff against the diff-stat for visual sanity.

**CRITICAL framing guard — runtime vs. BMAD persona distinction:**

This repo has *two* "Marcuses" and they must never be conflated in operator docs:

1. **Marcus the runtime** — Python service at `app/marcus/`. Operator invokes via `python -m app.marcus.cli ...` (CLI), via FastAPI HTTP, via MCP transport, or via direct Python import. Calls OpenAI APIs through the cascade YAML. **No Claude / Claude Code in the runtime path.** Production trials are pure Python invocation.

2. **Marcus the BMAD development persona** — roleplay defined in `skills/bmad-agent-marcus/SKILL.md` + sanctum at `_bmad/memory/bmad-agent-marcus/`. Used in Claude Code sessions for *development* work (planning, scoping, code review, batch dispatch). Same archetypal voice as the runtime; entirely separate mechanism.

When refreshing operator-facing docs (especially `trial-run-runbook.md`, `post-m5-runbook.md`, `README.md`, and any "how to run a trial" prose):

- **Trial runs and production runs invoke the runtime.** Document them as Python CLI / HTTP / MCP / import operations. Never describe a trial as "open Claude Code and talk to Marcus."
- **The BMAD persona is for development sessions.** It can be useful as a debugging companion *while* the runtime executes elsewhere, but it is not the runtime.
- **If a doc currently confuses the two**, fix it. The trial-run-runbook and post-m5-runbook were already partially re-authored in operator session 2026-04-26 with the corrected mental model — preserve those edits and extend the same discipline to other docs.
- **Ad-hoc / chat-with-Marcus mode at the runtime level does not exist today.** The legacy app may have had this; the migrated runtime does not. Batch 3 builds it (`app.marcus.cli ask "<prompt>"`). Until then, the closest substitute is the BMAD persona in Claude Code, which docs should describe as a learning/exploration aid, not as the runtime.

If during B5 you discover a doc that currently treats Claude Code or BMAD-persona chat as the runtime, **patch it**. Do not preserve the conflation in the name of "minimal edits."

**Time estimate:** ~1-2 hours.

### B7 — Pre-flight one-command harness

**Build:** `scripts/setup/ready_for_trial.{ps1,sh}` that runs in order:

1. `python scripts/utilities/trial_run_preflight.py` (existing 14-check sweep).
2. `python scripts/utilities/migration_health_dashboard.py` (existing 13-metric).
3. `python scripts/utilities/m5_pre_vote_audit.py` (existing pre-vote audit).
4. `python -m app.runtime.cascade_config validate` (NEW thin wrapper invoking `load_cascade()` + `load_pricing()` + asserts pricing-covers-cascade).
5. `python -c "from os import environ; missing = [k for k in ['OPENAI_API_KEY','LANGSMITH_API_KEY'] if not environ.get(k)]; assert not missing, f'Missing required keys: {missing}'"` (key presence check).
6. `.venv/Scripts/ruff check app/runtime app/replay app/models/runtime tests/unit/runtime tests/integration/runtime tests/integration/replay tests/migration tests/trial_replay`.
7. `.venv/Scripts/lint-imports --config pyproject.toml`.
8. `.venv/Scripts/python -m pytest tests/migration -q --tb=short` (filesystem-only slice; safe on Windows ACL-tainted machines).
9. **Final summary:** PASS/FAIL banner + per-step result + "you are READY FOR TRIAL" or "BLOCKED — see [step] above."

Single command exits 0 on full PASS, non-zero on any FAIL. Operator runs once before sitting for trial; either ready or knows what's blocking.

**Verify:** runs cleanly on the current branch state. Document in `docs/operator/trial-run-runbook.md` step 0: "run `scripts/setup/ready_for_trial.ps1` (Windows) or `.sh` (Linux/Mac)."

**Time estimate:** ~30-45 min.

### B9 — `slab-3-m5-dispatch-registry-swap` resolution

**Problem:** `state/config/dispatch-registry.yaml` and `runtime/graphs/v42/dispatch-registry-snapshot.yaml` both remain `_status: interim`. Named as 1 of the 4 M5 conditions in `m5-decision.md` and `upstream-state.md`. Closes WITHOUT operator presence.

**Resolve:**
1. Read both registry YAMLs to verify what `_status: interim` actually means in this context (likely a Slab 2b/4 marker indicating the registry was authored ahead of full specialist coverage).
2. If the registry is in fact production-ready (all 14 specialists registered + every entry verified valid against the live tree), promote `_status: interim` → `_status: production` (or whatever the convention is).
3. Update the frozen snapshot at `runtime/graphs/v42/dispatch-registry-snapshot.yaml` to match.
4. Add `tests/migration/test_dispatch_registry_promoted.py` asserting `_status` is no longer `interim` in either file.
5. Update `_bmad-output/upstream-state.md` Open Conditions §, removing condition 4 (or marking it RESOLVED-2026-04-26).
6. Update `_bmad-output/planning-artifacts/deferred-inventory.md`: flip `slab-3-m5-dispatch-registry-swap` from DEFERRED-CONTINUES to RESOLVED-2026-04-26 with brief close note.
7. Update `_bmad-output/implementation-artifacts/m5-decision.md` §"Inherited Conditional States" to mark this condition RESOLVED.

**If the registry is NOT actually production-ready** (e.g., a specialist entry is missing or wrong), HALT and report — do not promote with known defects. The operator decides whether to defer further or remediate now.

**Verify:** `grep -r "_status: interim" state/config runtime/graphs` returns no dispatch-registry hits. Test passes. Documents updated.

**Time estimate:** ~45-60 min.

### B-extra (optional, scope-with-care) — production-clone trial launcher

**Problem:** Story 5a.2 closed CONDITIONAL-GREEN because the authored launcher `app.marcus.cli trial start --preset production --input <corpus-path>` doesn't exist on this branch. The 5a.2 rider names this as an open M5 condition. If a real launcher exists by 2026-05-03, the operator can run a real trial that closes the rider in the same session.

**Scope decision required:** This is **bigger than B1-B9**. It touches the Marcus CLI surface, the LangGraph runtime invocation path, the `state/config/runs/` registration, LangSmith trace upload wiring, and the trial-id generation contract. Could be 4-8 hours of careful work depending on how much of the wiring already exists vs. needs to be built.

**Two paths:**

- **B-extra-A (minimal launcher):** thin CLI shim at `app/marcus/cli/trial.py` that takes `--preset production --input <corpus-path>`, generates a trial-id, registers in `state/config/runs/<trial-id>/`, invokes the existing Marcus orchestration entry point with the corpus, ensures LangSmith trace upload works, writes the cost report. **Scope tight; ~3-4 hours; produces a working launcher even if not fully polished.**

- **B-extra-B (defer):** file `5a-2-production-clone-launcher` follow-on as a post-trial story; operator runs the M2 + M3 ceremonies on the existing flow + accepts that the 5a.2 rider stays open through this conditional window; resolves at the next session.

**Recommendation:** ATTEMPT B-extra-A. If at any T1-style halt point the substrate doesn't support the path cleanly, fall back to B-extra-B and document the substrate gap. Operator wants the tight ship; this closes the second M5 condition without operator presence if it works, and the fallback is honest if it doesn't.

If B-extra-A succeeds: closes 5a.2 rider + the third condition; operator sits down for one focused trial that exercises everything.
If B-extra-A halts: file the follow-on, no harm done.

**Time estimate (with halt allowance):** ~4-5 hours; halt early if substrate gaps surface.

### B-cr — `bmad-code-review` on the Slab 5a diff (FINAL HARDENING PASS)

**Problem:** the Slab 5a body of work (~3762 insertions across 53 files) deserves a structured multi-layer code review with triage before the operator runs a real trial. The 5a.5 6-agent party-mode produced a verdict, but that was a SHIP/ITERATE/ROLLBACK judgment — not a defect-finding pass. `bmad-code-review` is the right tool for diff-level defect surfacing.

**Why bmad-code-review specifically:** it orchestrates three independent layers (Blind Hunter / Edge Case Hunter / Acceptance Auditor) plus triage into patch/defer/dismiss/decision_needed. The Acceptance Auditor layer is the qualitative differentiator — it reads the spec + ACs and traces the diff against them, catching "we built X but the AC asked for Y" defects that single-layer adversarial review misses.

**Run AFTER B1+B2+B9 land** (and B-extra if attempted) so the review covers the post-fix state, not a moving target.

**Invocation:**
1. Invoke `bmad-code-review` skill via the Skill tool.
2. Diff input: `git diff HEAD~5 HEAD` (the 5 5a commits) + any commits added by B1+B2+B9+B-extra at the time of running. Compute the actual range from `git log --oneline` at run time.
3. Spec input: the 5 Slab 5a story specs at `_bmad-output/implementation-artifacts/migration-5a-{1,2,3,4,5}-*.md` (Acceptance Auditor reads these).
4. Mode: `"full"` (so Acceptance Auditor activates; do NOT use `"no-spec"` mode).
5. Project context: existing `docs/project-context.md` + `CLAUDE.md` for repo conventions.

**Deliverable:** triaged punch list at `_bmad-output/implementation-artifacts/5a-code-review-2026-04-26.md` with the standard `bmad-code-review` output format (per-layer findings + triage classification + final summary).

**Disposition rule:**
- `patch` items: Codex addresses them in this batch before declaring done. Each `patch` becomes a small commit with descriptive message referencing the review file.
- `defer` items: file as deferred-inventory entries with explicit reactivation gates; do NOT silently shelve.
- `dismiss` items: explain in the close note why the dismissal is justified (mirror the Lesson Planner G6 DISMISS rubric — cosmetic NITs vs. real findings).
- `decision_needed` items: HALT and surface to operator with each option's tradeoff. Do not silently choose.

**Critical:** do NOT use this review as a license to expand scope. Findings outside the Slab 5a diff (e.g., "the Slab 2c specialist registry could use a refactor") get filed to deferred-inventory, not patched in this batch. Stay disciplined to the 5a surface.

**Verify:** review file exists; all `patch` items have corresponding commits; all `defer` items appear in `_bmad-output/planning-artifacts/deferred-inventory.md`; all `decision_needed` items appear in this batch's close report for operator attention.

**Time estimate:** ~2-4 hours (3 layers run in parallel; triage + patch follow-up sequential).

**Why B-cr replaces my earlier "B4 adversarial-review" proposal:** the standalone `bmad-review-adversarial-general` skill is one of the three layers `bmad-code-review` orchestrates. Running it standalone gives unfiltered findings without Acceptance Auditor traceability or triage. `bmad-code-review` is qualitatively stronger for the same diff.

---

## What NOT to do in this batch

- **No new specialist work.** All 14 specialists are scaffold-conformant. Do not refactor.
- **No invariant matrix re-litigation.** All 15 are PRESERVED.
- **No retro of the M5 verdict.** SHIP-CONDITIONAL stands.
- **No anti-pattern catalog edits.** Cycle-complete annotation is final.
- **No frozen-graph v42 changes.** Pack stays as shipped.
- **No live-API CALLS during dev.** B3 builds scaffolds only; tests skip when keys absent. Operator runs them later.

## Verification gates at batch close

For each completed task:
- `python scripts/utilities/validate_migration_story_sandbox_acs.py <relevant-story>.md` — PASS where applicable.
- `pytest <task-relevant-slice> -q --tb=short` — all pass.
- `ruff check <touched-surfaces>` — clean.
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if a new contract is added).

For the batch as a whole:
- `bash scripts/setup/ready_for_trial.sh` (or `.ps1`) — exits 0 with READY FOR TRIAL banner.
- The 4 M5 conditions in `_bmad-output/upstream-state.md` reflect resolution status (1 closed by B9; possibly 2 closed by B-extra-A if it succeeds; M2 + M3 remain operator-window).
- `_bmad-output/planning-artifacts/deferred-inventory.md` reflects all status flips.
- **`_bmad-output/implementation-artifacts/5a-code-review-2026-04-26.md` exists** with all `patch` items resolved, `defer` items filed, `dismiss` items justified, `decision_needed` items surfaced for operator.

## Operator-presence work that remains AFTER this batch

If everything in this batch lands cleanly:

1. **M2 Wondercraft live-artifact ceremony** (~10-15 min operator + render time).
2. **M3 Texas live-retrieval ceremony** (~5-10 min operator).
3. **One real trial run** through the migrated runtime against live OpenAI (~30-60 min operator + trial duration).

Three operator-windows in one focused session. After: unconditional SHIP at the next session, well within the 2026-05-03 conditional window.

If B-extra-A succeeds, item 3 also closes the 5a.2 launcher rider in the same operator session.

## Carry-forward notes

- Repo-wide pytest remains environment-tainted on operator's Windows machine (temp-root ACL defect). Document any new tests with a Windows-tainted note if they trip the issue. Do not let this block the batch — story-owned slice + migration-only slice are the trustworthy gates.
- Cascade YAML edits (B1, B2) will trigger digest changes in cost-report fixtures. Update fixtures in lockstep.
- B3 live-smoke tests use `pytest.mark.live` — make sure pytest config excludes this mark from default collection so dev machines don't hit live APIs by accident.
- For B5 docs, prefer surgical edits to wholesale rewrites — preserve the operator's intentional language style throughout the existing docs.

## Sequencing note

Execute in this order (parallelism within each phase OK):

1. **Defect-fix phase:** B1 + B2 + B9 (close-the-known-issues; these change state).
2. **Operator-readiness phase:** B3 + B5 + B7 (build operator-facing surfaces; these add capability).
3. **Optional condition-closer phase:** B-extra (production-clone launcher; halt early if substrate gaps surface).
4. **Final hardening phase:** B-cr (bmad-code-review on the post-fix diff; produces triaged findings).
5. **Patch any `patch`-classified findings from B-cr** before declaring batch done. This may produce additional commits; that's expected.

Phase 1 and Phase 2 may parallelize if surfaces don't conflict. B-extra runs after Phase 1+2. B-cr runs LAST so the review covers everything else.

## Follow-on batch (already authored)

After this batch closes, a second dispatch at `_bmad-output/implementation-artifacts/codex-handoff-pre-trial-defensibility-batch-dev.md` covers SHIP-defensibility passes (`bmad-testarch-trace` + `bmad-testarch-nfr` + `bmad-testarch-test-review`). Those produce evidence artifacts — they don't change code. Run that batch only after this one is done so the defensibility passes assess the actual ship state.

## Final notes

This batch is the difference between "operator runs a trial and discovers issues mid-flight" vs. "operator runs a trial and it works." The former costs an operator session per defect; the latter costs one focused session that closes 3 conditions. Operator's stated preference is "do it right" — that's what this batch buys.

Slab 5a closed structurally clean. This batch is the polish that makes the close meaningful. B-cr is the discipline check that the polish itself didn't introduce new defects.
