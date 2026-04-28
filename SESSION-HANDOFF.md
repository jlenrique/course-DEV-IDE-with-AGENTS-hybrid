# Session Handoff — 2026-04-28 evening (First tracked production trial: plumbing-PASS, content-FAIL, halted at G1; mitigation work filed)

**Session window:** 2026-04-28 evening (interactive operator session; 1 commit on `dev/langchain-langgraph-foundation`).
**Branch touched:** `dev/langchain-langgraph-foundation` (hybrid clone).
**Operator:** Juan Leon.
**Session mode:** First tracked production trial — plumbing shake-out + fix-on-the-fly patches.
**Commit range:** `72a94c5` (prior session-close) → this session's wrapup commit.
**Migration verdict at session-close:** **UNCONDITIONALLY SHIPPED** (commit `97842ac`, 2026-04-27, unchanged). Slab 6 trial-experience bundle 3/3 CLOSED 2026-04-28 morning (unchanged). **First tracked trial executed this evening; plumbing verified end-to-end; first-CONTENT-trial blocked on directive-composition seam (filed in deferred-inventory; mitigation is next session's anchor).**

---

## What Was Completed This Session

### 1. First tracked production trial executed (paused-at-gate G1, halted by operator decision)

- **Trial ID:** `475df528-7d75-48a3-be56-82b54a0b7b8b`
- **Corpus attempted:** `course-content/courses/tejal-APC-C1/` (~13 files: DOCX + PDF + PPTX + MD + visual exemplars)
- **Status at trial-stop:** `paused-at-gate G1 (gate_focus: trial_open)`. Operator did NOT submit a verdict. Trial sits paused indefinitely; bundle preserved at `state/config/runs/475df528-7d75-48a3-be56-82b54a0b7b8b/` (gitignored — local audit trail).
- **Bundle artifacts preserved:** `run.json`, `decision-card-G1.json`, `checkpoint.json`, `cost-report.json/.md`, `trace-fixture.json`.
- **LangSmith trace:** recorded under project `course-content-production` filterable by `metadata.trial_id == 475df528-7d75-48a3-be56-82b54a0b7b8b`.

### 2. Production-runner end-to-end plumbing VERIFIED real

End-to-end smoke evidence from the live trial:

| Concern | Result |
|---|---|
| `trial start --preset production --input <corpus-path>` invocation | PASS — registered trial, created bundle dir, opened Postgres checkpointer, started LangSmith trace, compiled graph, ran nodes 01–04 autonomously |
| Postgres checkpointer thread namespace | PASS — `run/475df528-...` persists in DB |
| LangSmith trace root span | PASS — `langsmith_trace_status: measured-from-langsmith`; `production_clone_launch_evidence: true` (reason: `live-specialist-call-recorded`) |
| Cost rollup | PASS — `cost-report.json/.md` produced; per-agent breakdown by model (`gpt-5-nano` 1 call / 25 in / 10 out / $0.000005) |
| Decision card emission | PASS — `decision-card-G1.json` written with `verb: approve`, `gate_focus: trial_open`, signed digest + server_nonce |
| Pause-and-wait at first declared gate | PASS — runner halted cleanly at G1; awaits `trial resume --verdict-file ...` |

**Migration verdict implication:** the `production_clone_launch_evidence: true` flag is genuinely earned at this trial (live OpenAI call + LangSmith span); migration's "SHIPPED" status holds.

### 3. Real defect surfaced: production-runner Texas directive-composition seam missing

**Diagnosis:** Texas's contribution at nodes 02 (Source Authority Map) + 03 (Ingestion + Evidence Log) returned the deterministic test fixture at `tests/fixtures/specialists/texas/fixture_bundle/` (10 lines of placeholder content; `run_id: TEXAS-FIXTURE-001`), NOT the operator's Tejal corpus. Real cost was $0.000005 (token-counter scale, not real DOCX extraction).

**Root cause:** `app/specialists/texas/retrieval_dispatch.py::dispatch_retrieval()` is a CORRECT Slab 2a.4 dispatch seam with explicit fork:

```python
if not directive_path or not bundle_dir:
    return {"status": "mocked", "bundle_dir": str(DEFAULT_FIXTURE_BUNDLE), ...}
# else: subprocess shell out to skills/bmad-agent-texas/scripts/run_wrangler.py --directive ... --bundle-dir ... --json
```

The production runner currently invokes this seam with `directive_path=None` AND `bundle_dir=None`, so it falls through to fixture stub. **The directive-composition step (corpus_path → directive YAML → `dispatch_retrieval(directive_path=..., bundle_dir=...)` real-args invocation) is missing upstream of the seam.**

**Implication:** approving G1 would have advanced to G1A (Irene Pass 1 lesson-plan coauthoring) — but Irene's `dependencies: upstream_output: "texas"` means she'd coauthor with the operator using fixture content, not the Tejal corpus. That's substantively pointless, so operator chose to halt.

**Filed:** `production-runner-texas-directive-composition-seam` in `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons. Recommended BMAD workflow for mitigation: `bmad-create-story` → `bmad-dev-story`. Recommended fix shape (also captured): new `app/runtime/compose_directive.py` module (walks `corpus_path`, classifies files by extension, emits directive YAML to `state/config/runs/<trial_id>/directive.yaml`) + runner wiring at trial-init + round-trip test against Tejal corpus + playbook §3 update describing operator override semantics.

### 4. Eight fix-on-the-fly patches landed inline during trial setup + execution

Per operator's stated stance ("fix-on-the-fly as much as possible through this entire trial"). All patches verified clean (ruff PASS on `run_hud.py`; doc patches don't lint).

| # | File | Change |
|---|---|---|
| 1 | `docs/operator/production-trial-playbook.md` §1.4 | Bare `python -c` Postgres-reachability command replaced with dotenv-aware version. Root cause: bare `python -c` does NOT inherit `.env`; operator hit `KeyError: 'DATABASE_URL'` even though value was correctly present in `.env`. FIRST-TRIAL-FILL block populated with discovery + resolution sequence. |
| 2 | `docs/dev-guide/local-postgres-setup.md` | Added Windows winget unattended install path: `winget install -e --id PostgreSQL.PostgreSQL.17 --silent --override "--mode unattended ... --superpassword postgres ..."` + Windows-aware bootstrap command (full path to `psql.exe` since not on PATH by default). Cross-reference to playbook §1.4 added. |
| 3 | `docs/operator/production-trial-playbook.md` Phase 3 + Phase 4 | Phase 3 retitled "Course corpus preparation (pre-run)" with explicit "Nothing is initialized at this phase" framing. Old §3.3 "Bundle initialization" deleted (no such pre-step exists). §3.3 prior-run-defaults reframed as "heads-up, not an action" (it fires DURING run at Step 02A). Phase 4 retitled "Run initialization (trial launch)" with explicit list of what gets created at §4.1 fire (bundle dir, run-constants.yaml, checkpointer thread, LangSmith span, graph compile). |
| 4 | `docs/operator/production-trial-playbook.md` §3.2 | Disk-files-only convention; locator/retrieval shape table; URL-list-file exception. Removed misleading `course-content/sources/` path; corrected to `course-content/courses/<lesson_slug>/` per operator-stated convention. Added "What goes where, by source kind" table covering local file / URL list / Notion / Box-URL / Playwright-URL / retrieval-shape; "static-vs-dynamic is not the locator/retrieval boundary" clarification. |
| 5 | `docs/operator/production-trial-playbook.md` §4.1 | Canonical launch command (template) + concrete-for-this-trial example + optional flags documented (`--operator-id`, `--trial-id`, `--allow-offline-cost-report` with caveat). HTTP transport noted as alternative gate-verdict channel (NOT alternative launcher). |
| 6 | `docs/operator/production-trial-playbook.md` §4.3 | HUD invocation patched: module form `python -m scripts.utilities.run_hud` (script-path form fails with `ModuleNotFoundError: No module named 'scripts.utilities'` because Python puts script's directory on sys.path, not repo root). Canonical flags documented as `--watch --open --trial-id <uuid>` together; "why each flag" explanation added. |
| 7 | `scripts/utilities/run_hud.py` defect #1 | `--watch --open` together previously broken: the `if args.open:` block was outside the `while True:` loop, so browser only opened after Ctrl+C. Patched: extracted `_open_in_browser()` helper; opens browser on iteration 1 in watch mode (single-shot path also calls helper after snapshot). |
| 8 | `scripts/utilities/run_hud.py` defect #2 | Header label and page title showed "No active run" even with `--trial-id <uuid>` set, because `rc.get("RUN_ID", ...)` only consulted the legacy source-bundle's `run-constants.yaml` and ignored the `active_trial` data flowing in from `read_active_trial()`. Patched: when `data.get("active_trial")` is non-None, header reads `<first-8-chars> (<status>)` (e.g., `475df528 (paused-at-gate)`); legacy path preserved when no migrated trial active. |

### 5. PostgreSQL 17 installed natively on operator's machine

Per CLAUDE.md `project_no_docker` operator preference. Service `postgresql-x64-17` running, listening on `0.0.0.0:5432`. Role `user` + DB `course_dev_ide_migration` + pgcrypto extension created via `scripts/dev/init_postgres.sql`. Persistent across sessions — next session does NOT need to re-install.

### 6. Workflow-shape discovery: migrated runtime is structurally different from legacy

Material conceptual finding from this trial. Legacy v4.2 prompt-pack model: Marcus delivers prose conversationally at every prompt section (1 → 2 → 2A → 3 → ...); operator answers per-section. Migrated LangGraph model: specialists run **autonomously between gates**; conversational interaction happens at gate decision-card review, NOT per-section.

This means the legacy "now I start talking with Marcus and confirm sources" mental model does not map to the migrated runtime. Operator-Marcus interaction concentrates at gate boundaries (G1 trial-open ratification, G1A Irene Pass 1 lesson-plan coauthoring, G2C Compositor, G3 Audio, G4 Final). Between gates the runtime is autonomous.

The `prompt-pack-reduction-internalization` deferred-inventory entry (filed prior session) is even more relevant after this trial. Future trial work should explicitly reckon with what conversational surface Marcus DOES expose during a gate-paused state vs what's deferred to specialist `_act` body knowledge.

### 7. Memory + governance updates landed

- New project memory file: `project_first_trial_outcome.md` — records the trial outcome + fix-on-the-fly patches that already landed, so next session has continuity.
- New project memory file: `project_corpus_path_convention.md` — operator's `course-content/courses/<lesson_slug>/` convention.
- New feedback memory file: `feedback_corpus_directory_scope.md` — disk-files-only scoping rule for the corpus directory.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — new entry `production-runner-texas-directive-composition-seam` filed; counts updated to 53 filed.

---

## What Is Next (broader context)

The session-immediate next action is on `next-session-start-here.md` (story-cycle the directive-composition seam). Broader context:

- **First-content-trial unlocks Epic 15 (Learning & Compound Intelligence) reactivation.** Per Epic 15's reactivation trigger ("at least one tracked trial run completed"), the directive-composition mitigation + a real first-content-trial is the gating sequence for Epic 15 work.
- **Slab 7 (or new slab) directive-composition story** is a candidate scope. Could fit under existing Slab 6.x substrate-polish OR open a new slab boundary depending on size + party-mode consensus at story-authoring time.
- **`bmad-create-story` + `bmad-dev-story`** are the recommended workflows. NOT `bmad-quick-dev` — this is real substrate work, not a tactical patch.
- **Trial-experience polish opportunities** also surfaced: HUD's "No active run" was a real defect that affected operator experience; future HUD polish should consider per-step blocker/warning auto-expand for active trial, gate-decision-card preview pane in HUD, etc. Defer to Slab 6.5 successor or a future trial-experience polish slab.

---

## Unresolved Issues or Risks

### Pre-closure / Audra-equivalent gaps

- **Cora dissolved per Slab 2 reconciliation** — `/harmonize` and `/preclosure` slash commands are not available; manual close protocols substitute. Steps 0a/0b of the WRAPUP protocol were skipped accordingly. No L1/L2 findings deferred (none generated; manual-substitute protocol).
- **Audit-trail gap acknowledged:** without `/harmonize`, this session has no `reports/dev-coherence/<ts>/` directory. Substitute audit trail: this SESSION-HANDOFF.md + `state/config/runs/475df528-.../` (trial bundle preserved) + git log of the wrapup commit.

### Active gotchas carried forward (still active for next session)

1. **Slab 6.1 LangSmith trace_id is synthetic at runner level** (deferred-inventory entry exists; cost rollup works; trial lookup by metadata works).
2. **Multi-pass envelope Path Z** (operator-ratified Slab 6.1): repeated specialist nodes — only the FIRST contribution lands. Verified at this trial (Texas appears once in `production_envelope.contributions` despite running at both nodes 02 + 03).
3. **Step 04A Maya intake_callable** UI integration deferred per deferred-inventory entry. Operator anticipates fix-on-the-fly when a future trial reaches Step 04A.
4. **Replay regression pre-existing pack-hash drift** — separate investigation; not affected by this session.
5. **Ruff debt** — repo-wide `ruff check .` reports ~1217 errors (latent debt; per-touched-file ruff was clean throughout this session).

### NEW gotcha from this session

6. **Production runner directive-composition seam missing** — first-content-trial blocked. See `production-runner-texas-directive-composition-seam` deferred-inventory entry. Mitigation is next session's anchor.

### Non-blocking observations worth noting

- **`scripts/operator/check_keys.py`** doesn't enumerate `LANGSMITH_PROJECT` or `DATABASE_URL`; both are required per playbook §1.3 but the script only checks API-key-shaped values. Cosmetic gap; not blocking.
- **CONSENSUS_PASSWORD shows `(short)` in check_keys output and `[??]` in `.env`** — placeholder. Texas's Consensus retrieval adapter (per Story 27-2.5) won't function until filled. Not blocking unless future trial dispatches Consensus.
- **YouTube + Box API + Canva credentials are MISSING/placeholder.** Same shape: only matters if a future trial dispatches those providers.

---

## Key Lessons Learned

1. **The migrated runtime's gates are NOT equivalent to legacy v4.2 prompt-pack sections.** Operator-Marcus conversation in the migrated stack happens at gate decision-card review boundaries, not at every prompt section. This is a structural difference that must be reflected in operator-facing docs (the playbook patches landed in this session take a first cut; more substantive prompt-pack-reduction work is deferred).
2. **Fix-on-the-fly works for tactical patches but NOT substrate work.** Operator's stance is sound for command-bug fixes, missing flags, doc errors, environment-setup gaps. It's NOT appropriate for new modules, runner wiring changes, schema migrations — those should route through `bmad-create-story` + `bmad-dev-story` even mid-trial. The directive-composition gap is the canonical example: tempting to "just write the composer inline," but it's structural runner work and deserves a story.
3. **Trial bundles are valuable evidence even when content is fixture-stubbed.** The `state/config/runs/475df528-.../` bundle is the audit trail for "production-runner plumbing was verified real on 2026-04-28." Don't delete; this evidence is referenceable for migration-verdict defense + future regression debugging.
4. **`production_clone_launch_evidence: true` is a real flag with real semantics.** It fires when a live OpenAI call is recorded during the run, even if the call was a token-counter-scale stub through a fixture-bound specialist. The flag is honest about what it tracks (live-call-recorded) but doesn't claim "real content was produced." Operator should not over-read the flag as "trial succeeded content-wise."
5. **HUD defects can mask real trial state for hours.** The "No active run" header on the HUD wasn't just cosmetic — it actively misled the operator into thinking their `--trial-id` flag wasn't working when in fact the migrated trial was loaded; the page title and label rendering just hadn't been updated to consult `active_trial`. Future HUD polish work should run a "is everything that depends on `active_trial` actually using `active_trial`" audit.
6. **Operator's stated convention for corpus path was different from playbook draft.** `course-content/courses/<lesson_slug>/` not `course-content/sources/`. Saved to memory; saved to playbook; saved to deferred-inventory cross-reference. Convention is now durable across sessions.

---

## Validation Summary

| What | How | Result |
|---|---|---|
| Phase 1.1–1.3 (venv + deps + keys) | Per playbook commands | PASS — operator confirmed with `[OK]` markers in playbook |
| Phase 1.4 (Postgres reachable) | dotenv-aware `python -c` after install + bootstrap | PASS — `OK` returned |
| Phase 2.1 (full migration health check) | `migration_full_health_check.py` | PASS — 213 passed + 1 skipped across 11/11 slices in ~30s |
| Phase 4.1 (trial start) | `app.marcus.cli trial start --preset production` | PASS — `paused-at-gate G1`; `production_clone_launch_evidence: true` |
| Phase 4.3 (HUD launch) | After 2 patches: module form + canonical flags | PASS — browser opened on iteration 1 with active-trial header |
| Step 1 quality gate (ruff) | `.venv/Scripts/ruff.exe check scripts/utilities/run_hud.py` | PASS — All checks passed! |

No automated test runs invoked beyond `migration_full_health_check.py`. No new tests added (no substrate code changes — only patches to a CLI script + docs).

---

## Course Content Summary

No course content was created or moved this session. Staging directories (`course-content/staging/tracked/`) unchanged. Tejal APC C1-M1 corpus at `course-content/courses/tejal-APC-C1/` unchanged; remains ready for re-use once directive-composition seam ships.

---

## Artifact Update Checklist

- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` — new entry filed; counts updated
- [x] `docs/operator/production-trial-playbook.md` — 5 patches across §1.4, Phase 3, §3.2, §4.1, §4.3
- [x] `docs/dev-guide/local-postgres-setup.md` — Windows winget path + cross-platform bootstrap
- [x] `scripts/utilities/run_hud.py` — 2 defects fixed
- [x] `next-session-start-here.md` — finalized with mitigation anchor + branch metadata + active gotchas
- [x] `SESSION-HANDOFF.md` — this file
- [x] Memory files: `project_first_trial_outcome.md`, `project_corpus_path_convention.md`, `feedback_corpus_directory_scope.md`
- [ ] `_bmad-output/implementation-artifacts/sprint-status.yaml` — NO CHANGE (no story flips this session)
- [ ] `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` — NO CHANGE (no phase transition)
- [ ] `docs/project-context.md` — NO CHANGE (no architectural shift this session)
- [ ] `docs/agent-environment.md` — NO CHANGE (no MCP/API/skill changes)
- [ ] `docs/user-guide.md` / `admin-guide.md` / `dev-guide.md` — NO CHANGE (the local-postgres-setup.md patch is the relevant dev-guide-territory change)

---

## Audit-Trail References

- **Trial bundle:** `state/config/runs/475df528-7d75-48a3-be56-82b54a0b7b8b/` (gitignored — local-only audit trail; do NOT delete)
- **LangSmith trace:** `https://smith.langchain.com/traces/475df528-7d75-48a3-be56-82b54a0b7b8b` (per cost-report.md)
- **Deferred-inventory entry:** `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons → search `production-runner-texas-directive-composition-seam`
- **No `/harmonize` report this session** (Cora dissolved per Slab 2 reconciliation; manual close protocol substitutes; this SESSION-HANDOFF + git log of the wrapup commit serve as the substitute audit trail)

---

---

## Post-Wrapup Scope Correction (2026-04-28 evening, after wrapup commit `e6b1967`)

After the WRAPUP commit landed, the operator asked the BIG QUESTION: *"Why didn't we use the legacy v4.2 prompts 01/02/02A/03 in their proven sequence?"* — and pasted the full legacy prompt prose for those four sections.

That review exposed that the deferred-inventory entry I filed (`production-runner-texas-directive-composition-seam`) **understated the scope of the gap**. The legacy prompts ARE the missing wiring template — every one of Prompts 01/02/02A/03 encodes operator-Marcus conversation that the migrated runtime currently skips. Three layers are missing:

1. **Early-gate HIL pause discipline** — manifest declares G0/G0A/G0B as gates but production runner only honors terminal gates (G1/G2C/G3/G4)
2. **Conversational composition surface** — no Marcus-runtime interface to author `source-authority-map.md` / `operator-directives.md` / etc. at gate-paused state; decision cards today only carry binary `verb: approve` verdicts
3. **Inter-gate composition logic** — once §2 + §2A artifacts exist, no code reads them and emits `directive.yaml` for Texas; legacy Marcus-the-persona did this manually. Same shape applies to every other inter-gate composition step the legacy prompt pack defines

**Operator-stated correction (post-wrapup):** *"Slab 7 should involve not only preproduction but ALL the 'skipper' intermediate activity between gates. Otherwise we'll get the same 'surprises' as we move from one Gate to another in the next trial run."*

### Corrected mitigation framing

- Slab 7 **renamed** from "Pre-Production Conversational Orchestration" → **"Inter-Gate Conversational Orchestration"** to cover ALL gate transitions (G0→G0A→G0B→G1→G1A→G2C→G3→G4), not just pre-production.
- Legacy v4.2 prompt pack at `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` is the canonical inventory of what conversational orchestration was present pre-migration. Slab 7 PRD authoring should walk that pack section-by-section to scope the full set of stories.
- **Recommended BMAD workflow corrected:** `bmad-create-prd` (or `bmad-party-mode` for architectural alignment) FIRST, BEFORE `bmad-create-story`. Three architectural questions to settle in party-mode: (a) where operator-Marcus conversation happens at non-terminal gates (CLI / Maya UI / IDE-chat-wrapped-runner); (b) what's truly conversational vs auto-derivable from corpus + defaults; (c) how `--verdict-file` evolves to carry operator-authored prose, not just binary verdicts.
- The originally-filed narrower "directive composition module" becomes ONE downstream story under Slab 7, not the whole answer.

### Artifact corrections landed in this post-wrapup pass

- `_bmad-output/planning-artifacts/deferred-inventory.md` — entry renamed `slab-7-inter-gate-conversational-orchestration`; supersedes-banner notes the original narrower framing; three-layer diagnosis; PRD-first workflow recommendation; legacy prompt-pack pointer.
- `next-session-start-here.md` — Immediate-next-action rewritten: open Slab 7 PRD, party-mode architectural alignment FIRST, then epics/stories, then per-story dev cycles.
- This SESSION-HANDOFF.md — added this section so the permanent record reflects the corrected scope.

### Lesson learned (added to the §Key Lessons set above in spirit)

7. **First-trial diagnosis can underestimate scope when only one symptom is examined.** The Texas fixture-stub was the loudest symptom but not the whole disease; the real disease is systemic loss of inter-gate conversational orchestration. Any future "first surprising symptom in a trial run" should be re-examined for "what other manifestations of the same root cause are downstream?" before scoping mitigation. The legacy prompt pack is the single best document to consult against runtime behavior to find the full set.

---

**This file is the permanent backward-looking record. `next-session-start-here.md` is the forward-looking action trigger for the next session.**
