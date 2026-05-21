# Migration Story 1.1a: Runtime Substrate Environment + Dependencies

Status: done (re-opened 2026-04-22 for `mcp` SDK micro-fix per Set-A green-light review BLOCKER-2 — see §Re-Opening 2026-04-22 below; closes back to `done` after lockfile relock + import-smoke green)

**Track:** LangChain + LangGraph migration (hybrid clone only — `dev/langchain-langgraph-foundation` on remote `course-DEV-IDE-with-AGENTS-hybrid`).
**Epic:** Slab 1 Substrate — Runtime + Models + Manifest + Bridges + Docs (migration Epic 1).
**Milestone anchored:** M1 — "Runtime substrate is real."
**Serial-kickoff position:** 1 of 3 (1.1a → 1.1b → 1.1c strict serial per Architecture Amendment F).

<!-- Validation optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **dev agent onboarding the hybrid clone**,
I want **a locked Python 3.12+ venv with the migration's nine core dependencies installed and pinned, plus pyproject linter contracts and a `.env.example` template in place**,
So that **every subsequent Slab 1 story (1.1b, 1.1c, 1.2–1.7) starts from an identical, reproducible baseline, FR60 backport-freeze discipline is wired Day 1, and NFR-S1 secret-management posture is codified before any migration code lands**.

## Re-Opening 2026-04-22 — `mcp` SDK Micro-Fix

The Set-A party-mode green-light review (2026-04-22) surfaced that the `mcp` PyPI SDK is **absent from `requirements.lock`** even though Set-A Stories 1.1c (MCP code substrate) and 1.1d (MCP transport smoke + parity) require `mcp.server.Server` + `mcp.server.stdio.stdio_server` + `mcp.client.stdio.stdio_client` + `ClientSession`. Operator decision (2026-04-22): re-open 1.1a as a micro-fix to extend the install list and relock, rather than ride the dep change into 1.1c's commit (which would couple a substrate-bootstrap concern to an application story).

**Micro-fix scope:**
- **AC-MF1 — Dep installed.** `uv pip install mcp` (or `uv add mcp` if pyproject is the source of truth) succeeds against the existing 1.1a venv; `uv pip freeze > requirements.lock` re-emitted with `mcp` plus its transitive deps pinned.
- **AC-MF2 — SDK exposes the required primitives.** `uv run python -c "from mcp.server import Server; from mcp.server.stdio import stdio_server; from mcp.client.stdio import stdio_client; from mcp import ClientSession; print('ok')"` prints `ok` with exit 0. If the locked version of `mcp` does NOT expose any of these four import paths, ESCALATE before relocking — that's a 1.1d redesign trigger, not a silent dep-version downgrade.
- **AC-MF3 — Existing 1.1a ACs still green.** AC-1, AC-2, AC-3, AC-4 from the original 1.1a re-run green: import smoke still works (now extended to import `mcp` too); `ruff check app` still clean; `lint-imports` still clean; `.env.example` unchanged.
- **AC-MF4 — Re-close commit.** New commit on `dev/langchain-langgraph-foundation`: `chore(migration): Slab 1 Story 1.1a micro-fix — add mcp SDK to lockfile (Set-A BLOCKER-2 closure)`. Body cites the 2026-04-22 set-level party-mode review finding + the operator's "1.1a microfix" disposition. Story status returns to `done`.

The total dep count rises 9 → 10 (`langgraph, langchain, langchain-openai, openai, langgraph-checkpoint-postgres, pydantic>=2, fastapi, langsmith, psycopg[binary], mcp`). The architecture's "nine-package locked starting palette" line is amended in this commit's body to "ten-package locked starting palette as of 2026-04-22 micro-fix; mcp added per Set-A consensus on MCP-in-Slab-1 (5/5 MIDDLE PATH)."

---

## Acceptance Criteria

Preserved verbatim from [epics-langchain-langgraph-migration.md §Epic 1 Story 1.1a](../planning-artifacts/epics-langchain-langgraph-migration.md) (Given/When/Then form; each AC is self-verifying via a deterministic command).

**AC-1 — Venv creation + dependency install + lockfile**

- **Given** a fresh clone of the `dev/langchain-langgraph-foundation` branch
- **When** the dev agent runs:
  ```bash
  uv venv .venv --python 3.12
  # activate: source .venv/bin/activate  (Unix) | .venv\Scripts\activate  (Windows)
  uv pip install langgraph langchain langchain-openai openai \
    langgraph-checkpoint-postgres "pydantic>=2" fastapi langsmith "psycopg[binary]"
  uv pip freeze > requirements.lock
  ```
- **Then** the venv activates, all **nine** core packages install without conflict, and `requirements.lock` is emitted and committed.

**AC-2 — Import smoke**

- **Given** the lockfile is committed
- **When** the dev agent runs `uv run python -c "import langgraph, langchain_openai, pydantic, fastapi, langsmith; print('ok')"`
- **Then** stdout is exactly `ok` with exit code 0; no ImportError, no version-conflict warning.

**AC-3 — pyproject + ruff + import-linter clean on empty `app/`**

- **Given** `pyproject.toml` is extended with (a) `[tool.importlinter]` section declaring the two Slab-1 contract stubs and (b) `[tool.uv]` / `[tool.ruff]` adjustments as required
- **When** the dev agent runs `ruff check .` and `lint-imports --config pyproject.toml` (the import-linter CLI entry-point is `lint-imports`; see §Dev Notes)
- **Then** both tools report clean on the currently-empty `app/` tree. The two contract stubs are **declared but trivially pass** because `app/marcus/`, `app/cora/`, and `app/gates/` do not yet exist:
  - Contract **C1** (`type = "independence"`): `app.marcus` ⊥ `app.cora` — mutual import ban per architecture D3 + D6 lane separation.
  - Contract **C2** (`type = "forbidden"`): `app.gates.**` may not import `threading`, `apscheduler.*`, `schedule.*` (import-level scheduler ban per D3). Callable-level `asyncio.sleep` ban is a TODO — see T4 for the rationale and deferred-to-Slab-3 handling.

**AC-4 — `.env.example` template + `.env` gitignore posture (NFR-S1)**

- **Given** no `.env.example` exists yet and `.env` is already gitignored
- **When** the dev agent creates `.env.example` at repo root with four placeholders:
  - `OPENAI_API_KEY=<placeholder>`
  - `LANGSMITH_API_KEY=<placeholder>`
  - `LANGSMITH_PROJECT=course-dev-ide-migration`
  - `DATABASE_URL=postgresql://user:pass@localhost:5432/course_dev_ide_migration`
- **Then** `.env.example` is committed; the existing `.gitignore` line `.env.*` is amended with a `!.env.example` negation so the template is trackable; `.env` itself remains gitignored per NFR-S1.

## Tasks / Subtasks

- [x] **T1 — Read required context before any code.** (AC: pre-work)
  - [ ] Read [architecture-langchain-langgraph-migration.md §Decisions D1–D13 + §First Implementation Stories Amendment F + §Architectural Decisions Baked Into the Scaffold + §Implementation Patterns §1–§3](../planning-artifacts/architecture-langchain-langgraph-migration.md).
  - [ ] Read [prd-langchain-langgraph-migration.md §Functional Requirements FR1–FR8 + FR17–FR25 + FR58–FR60 + §Non-Functional Requirements NFR-S1 / NFR-M2–M7 / NFR-X1–X5 / NFR-O4](../planning-artifacts/prd-langchain-langgraph-migration.md).
  - [ ] Skim [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — not consumed by 1.1a code (substrate bootstrap, not a schema-shape story) but Story 1.2 lands Pydantic state models that inherit this checklist; register the 14 idioms now so 1.1b/1.1c reviewers anchor on them.
  - [ ] Skim [docs/dev-guide/story-cycle-efficiency.md §K-floor discipline](../../docs/dev-guide/story-cycle-efficiency.md) — K-target for this story is **1.3×** (Pts = 1).

- [x] **T2 — Create venv and install the nine core dependencies.** (AC-1)
  - [ ] `uv venv .venv --python 3.12` at repo root. Confirm `python -V` inside venv reports Python 3.12.x.
  - [ ] `uv pip install` the exact nine packages named in AC-1 (no more, no less for this story). Order as listed.
  - [ ] Confirm zero resolver conflicts in stderr. Any conflict = stop, triage, escalate; do not silently add version pins.
  - [ ] `uv pip freeze > requirements.lock`. Inspect the lockfile — must contain the nine packages + their transitive dependencies, one per line.

- [x] **T3 — Verify import smoke.** (AC-2)
  - [ ] Run the one-line `uv run python -c "..."` import check verbatim from AC-2.
  - [ ] Capture stdout; assert exactly `ok`. Capture stderr; assert empty.
  - [ ] If any `ImportError` or `RuntimeError` surfaces, stop and triage before proceeding. Do not mask by reinstalling.

- [x] **T4 — Extend `pyproject.toml` with linter contracts and dev-tooling dependency.** (AC-3)
  - [ ] Add `import-linter>=2.0,<3` to `[project.optional-dependencies].dev` (currently line 24–33 of `pyproject.toml`).
  - [ ] Add top-level `[tool.importlinter]` section with `root_packages = ["app"]`.
  - [ ] Add `[[tool.importlinter.contracts]]` block **C1** with `type = "independence"`, `name = "app.marcus and app.cora are lane-isolated siblings (D3 + D4 lane separation)"`, `modules = ["app.marcus", "app.cora"]`. The `independence` contract type is the correct one for a mutual import-ban (architecture D3 + D6 state "no imports either direction"); `forbidden` is one-directional and would require two blocks. **Open boundary question to document in Completion Notes:** does import-linter treat non-existent `source_modules`/`modules` (empty Slab-1 `app.marcus` + `app.cora`) as a fatal error, a warning, or silently skip? If fatal, the dev agent has two options: (a) create empty `app/marcus/__init__.py` + `app/cora/__init__.py` stubs this story (boundary-creep into 1.1b), or (b) add `ignore_imports = []` with an explanatory comment and accept the warning until 1.1b creates the packages. Prefer (b); flag for reviewer.
  - [ ] Add `[[tool.importlinter.contracts]]` block **C2** with `type = "forbidden"`, `name = "app.gates.** may not import schedulers (D3 HIL tamper-evidence)"`, `source_modules = ["app.gates"]`, `forbidden_modules = ["threading", "apscheduler", "schedule"]`. **Important callable-level gap:** architecture D3 lists `asyncio.sleep` in the forbidden set, but import-linter matches at module level — `asyncio.sleep` is an attribute of `asyncio`, not an importable module. A full `asyncio` ban is too broad (breaks FastAPI and LangGraph internals). The correct long-term enforcement is a ruff custom rule or a runtime assertion in `app/gates/resume_api.py`. For Slab 1 stub, C2 captures the import-level bans (`threading.Timer`, `apscheduler.*`, `schedule.*`) and a `# TODO Slab 3: callable-level asyncio.sleep ban via ruff custom rule or import-time assertion in app/gates/resume_api.py` comment is added to the contract block. Same non-existent-module question as C1 applies — document resolution in Completion Notes.
  - [ ] Decide whether to bump `requires-python` in `pyproject.toml` from `">=3.11"` → `">=3.12"` (architecture §Architectural Decisions Baked Into the Scaffold says Python 3.12+). **Recommended:** leave `requires-python = ">=3.11"` unchanged for this story (primary-repo legacy code under `skills/`, `scripts/` still targets 3.11; the migration venv enforces 3.12 via `uv venv --python 3.12`). Document the divergence in the Completion Notes. If operator prefers the bump, flag at dev-story review.

- [x] **T5 — Run `ruff check` and `lint-imports`; confirm both clean.** (AC-3)
  - [ ] `uv run ruff check .` — must exit 0 against the (still-empty) `app/` tree and the two newly-added contract blocks.
  - [ ] `uv run lint-imports --config pyproject.toml` — must exit 0. Both contracts trivially pass because source modules (`app.marcus`, `app.gates`) do not exist yet.
  - [ ] **Known pre-existing condition:** the repo's legacy Python code under `skills/`, `scripts/`, and `tests/` already reports 1338 ruff errors per [next-session-start-here.md §Ambient worktree state](../../next-session-start-here.md). This story does NOT remediate legacy errors. `ruff check app/` (scoped to the migration tree) is what must be green. If running unscoped `ruff check .` still surfaces only the pre-existing 1338, document that in Completion Notes. No new errors introduced by this story.

- [x] **T6 — Author `.env.example` and amend `.gitignore` for tracking exception.** (AC-4)
  - [ ] Create `.env.example` at repo root containing exactly the four placeholder lines listed in AC-4. No real secrets. No additional keys this story.
  - [ ] Verify current `.gitignore` lines 2–3 are `.env` + `.env.*`. Add a new line `!.env.example` below them to negate the `.env.*` pattern for the template file. Placement matters (gitignore patterns are order-sensitive; the negation must come AFTER the ignore).
  - [ ] Confirm via `git check-ignore -v .env.example` that the negation works: it should report "not ignored" (exit 1 means not ignored — correct outcome).
  - [ ] `git add .env.example` and commit. Confirm `.env` itself is still ignored (`git check-ignore -v .env` returns the `.gitignore:2:.env` line).

- [x] **T7 — Commit all six deliverables as a single logical commit.** (closure)
  - [ ] Files modified/added this story: `requirements.lock` (new), `pyproject.toml` (extended), `.env.example` (new), `.gitignore` (amended).
  - [ ] Commit message: `feat(migration): Slab 1 Story 1.1a — runtime substrate environment + dependencies`. Body references Architecture D1–D13 + Amendment F per D12 protocol.
  - [ ] Do not push without operator's sign-off. Single-gate story; review is code-review-only, no party-mode.

## Dev Notes

### Architecture compliance — load-bearing decisions relevant to 1.1a

This story is the first concrete realization of the scaffold architecture. Four decisions directly shape 1.1a:

- **Amendment F (single→triple-story split):** Rejected Option-a single story (K ≈ 4.5–5× target, fails `story-cycle-efficiency.md §K-floor`). Strict serial 1a → 1b → 1c with K-targets 1.3× / 1.4× / 1.6×. 1.1a is intentionally minimal — lockfile + linter contract stubs + env template. Resist scope drift into 1.1b territory (package creation, Postgres, sanctum fork notice) or 1.1c (smoke test, runtime server, registry_check).
- **Architectural Decisions Baked Into the Scaffold** (architecture §Architectural Decisions Baked Into the Scaffold): `uv` is the lock tool (not poetry, not pip-tools). `requirements.lock` is a Slab-1 acceptance artifact. `ruff` inherits from primary. Import-linter is the package-boundary enforcement tool.
- **D3 HIL tamper-evidence (excerpt for C2 contract):** `app/gates/**` may not import schedulers. Rationale: a future sprint under pressure cannot silently add an "auto-approve on timeout" path. The contract stub lands now, Slab 3 wires real `app/gates/` content, and Slab 4's CI elevates the contract to graph-compile-time hook. Keep the contract broad at Slab 1; tighten in Slab 3.
- **D13 model-registry mid-migration bump:** registry governance; not directly exercised by 1.1a but note that the nine-package core list in AC-1 is the **locked starting palette**. Additive new packages in later stories are Tier-1 patch (dev-agent authority with registry-version line in slab closing-story AC). Subtractive or version-pin changes require party-mode consensus.

### The nine core packages — exact list, no substitutions

Copy-paste exact from architecture §First Implementation Stories 1a:

```
langgraph
langchain
langchain-openai
openai
langgraph-checkpoint-postgres
pydantic>=2
fastapi
langsmith
psycopg[binary]
```

Rationale per package:
- **langgraph + langchain + langchain-openai + openai:** runtime substrate. PRD §Decision 3 ("reject the LangChain cage") mandates direct `ChatOpenAI` adapter use, not high-level agent abstractions. The LangChain top-level package is included anyway because LangGraph has transitive imports from it.
- **langgraph-checkpoint-postgres:** Postgres checkpointer (D1 + D6 + NFR-P3). Installed Slab 1; wired Slab 1 Story 1.1c + Story 1.5 (retention policy).
- **pydantic>=2:** Pydantic v2 is the state-model contract (NFR-M5 four-file-lockstep). Existing primary-repo `pyproject.toml` line 14 already pins `pydantic>=2.7,<3` — uv resolver should satisfy both constraints without conflict.
- **fastapi:** operator-surface HTTP bridge (D7 three-transport parity). Localhost-only per NFR-S2.
- **langsmith:** tracing substrate (FR58 + NFR-O4 resolution-trail spans).
- **psycopg[binary]:** Postgres driver. `[binary]` extra includes libpq — avoids ambient-system-libpq install requirement on Windows dev boxes.

### Pre-existing repo conditions the dev agent should know about

- **`pyproject.toml` line 5** currently declares `requires-python = ">=3.11"`. See T4 — recommended: leave unchanged for this story.
- **`.gitignore` lines 2–3** already ignore `.env` and `.env.*`. The `.env.*` pattern would exclude `.env.example` unless a `!.env.example` negation is added (T6). Don't forget the bang.
- **Existing `.env`** contains real secrets for primary-repo work (DESCRIPT_API_KEY, Canvas tokens, etc.). This story does NOT touch `.env`; `.env.example` is a fresh template with only the four migration placeholder keys.
- **`requirements.txt`** exists in repo root (primary-repo legacy). Do NOT overwrite or delete it. `requirements.lock` is a distinct file introduced by this story.
- **Windows bash vs PowerShell:** the hybrid clone is on Windows 11 per CLAUDE.md environment. Use `source .venv/Scripts/activate` under Git Bash, `.venv\Scripts\Activate.ps1` under PowerShell. uv itself is cross-shell.

### Testing standards summary

- **No pytest code this story.** 1.1a verification is command-based (run `ruff`, run `lint-imports`, run import-smoke one-liner). Architecture line 271 explicitly says "smoke-import shape-pin test lives in 1b AC, not a separate story" — that test lands in 1.1b.
- **K-floor target 1.3×** (Pts = 1 → target 1.3 verification signals). Counting AC verification points: AC-1 (lockfile committed + install clean + 9 packages present = 3 signals), AC-2 (stdout==ok + stderr empty = 2 signals), AC-3 (ruff exit 0 + lint-imports exit 0 = 2 signals), AC-4 (check-ignore template=not-ignored + check-ignore .env=ignored + 4-placeholder file shape = 3 signals). Total ≈ 10 deterministic signals — K ≈ 10/1pt = effective 10× if each signal counts as a test. Adjust the framing: K-floor is measured against author-created test nodes, and this story creates zero test nodes (no pytest). The K-floor rule doesn't apply cleanly to substrate-bootstrap stories — document in Completion Notes and flag for operator calibration.
- **What review checks instead:** single-gate `bmad-code-review` verifies the four AC commands produce the stated outputs on a reviewer's box. Layered (Blind / Edge / Auditor) review optional for 1pt single-gate.

### Project Structure Notes

- **New files created by this story:** `requirements.lock` (repo root), `.env.example` (repo root).
- **Modified files:** `pyproject.toml` (extend `[project.optional-dependencies].dev` + add `[tool.importlinter]` + contracts), `.gitignore` (append `!.env.example` line).
- **No new directories beyond import-linter contract stubs.** `lint-imports` requires `app.marcus`, `app.cora`, and `app.gates` to exist, so Story 1.1a seeds only those minimal stub packages. `tests/` scaffolding is Story 1.1b scope. Native-Postgres bootstrap (`scripts/dev/init_postgres.sql` + `docs/dev-guide/local-postgres-setup.md`) is Story 1.1b scope. **No Docker / no docker-compose.yml — operator runs Postgres 15+ natively on the dev machine per the 2026-04-22 no-container decision; this line previously said "`docker-compose.yml` is Story 1.1b scope" and was revised after Story 1.1a closed.**
- **No sanctum edits.** `CLONE-FORK-NOTICE.md` per specialist is Story 1.1b scope (Amendment G).

### Forward-port freeze (FR60) semantics — what lands NOW

> Per [next-session-start-here.md §Branch Baseline](../../next-session-start-here.md) and sprint governance, **FR60 becomes active when Story 1.1a is accepted as `done` on the migration branch.** This story opens Slab 1, but the branch-management policy change is treated as active only once the bootstrap commit has cleared review. After that point, `git merge upstream/master` for primary-repo catchup stops being on-policy and convergence goes through the migration-guide §8 forward-port playbook.

The commit message should explicitly name FR60 activation so the policy change is grep-able later.

### References

- [Source: _bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md §Epic 1 Story 1.1a — Runtime Substrate Environment + Dependencies](../planning-artifacts/epics-langchain-langgraph-migration.md) — authoritative AC source.
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §First Implementation Stories — Slab 1 Story 1a/1b/1c (Amendment F)](../planning-artifacts/architecture-langchain-langgraph-migration.md) — commands + rationale + K-target.
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D1 — Sanctum Snapshot Strategy](../planning-artifacts/architecture-langchain-langgraph-migration.md) — hash infra referenced by Story 1.2 onward; T1 context only for 1.1a.
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D2 — Model-Cascade Code Location + Override Flow](../planning-artifacts/architecture-langchain-langgraph-migration.md) — nine-package list rationale for `langchain-openai` + `openai`.
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D3 — HIL Invariant Tamper-Evidence](../planning-artifacts/architecture-langchain-langgraph-migration.md) — Contract C2 rationale (`app.gates.**` scheduler-forbidden).
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D6 — Manifest-as-Graph-Config Loader](../planning-artifacts/architecture-langchain-langgraph-migration.md) — topology contract that 1.1c smoke test exercises; T1 context only.
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D12 — Cross-Slab Governance Artifact Ownership](../planning-artifacts/architecture-langchain-langgraph-migration.md) — three-line protocol at slab-closing stories; 1.1a is NOT a slab-closing story (1.7 is), but the commit message body should still cite D12 to anchor the pattern.
- [Source: _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md §FR60 — Forward-port freeze policy](../planning-artifacts/prd-langchain-langgraph-migration.md) — activates at this commit.
- [Source: _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md §NFR-S1 — API-key secret management](../planning-artifacts/prd-langchain-langgraph-migration.md) — `.env` never committed; `.env.*` pattern with `!.env.example` negation.
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — T1 context for 1.2+ follow-on schema-shape stories (not applied in 1.1a code).
- [Source: docs/dev-guide/story-cycle-efficiency.md — K-floor discipline](../../docs/dev-guide/story-cycle-efficiency.md) — K-target 1.3× for Pts=1; note K-floor framing adjustment for substrate-bootstrap stories.
- [Source: CLAUDE.md §BMAD sprint governance](../../CLAUDE.md) — single-gate story; review runs `bmad-code-review`; no party-mode required unless reviewer finds a governance-scope finding.
- [Source: next-session-start-here.md §Branch Baseline + §Hot-Start Gotchas](../../next-session-start-here.md) — FR60 activation at this commit; Windows environment notes; ambient ruff 1338 pre-existing errors are out-of-scope.

## Dev Agent Record

### Agent Model Used

gpt-5.4

### Debug Log References

- T1 reading set completed: architecture-langchain-langgraph-migration.md; prd-langchain-langgraph-migration.md; docs/dev-guide/pydantic-v2-schema-checklist.md; docs/dev-guide/story-cycle-efficiency.md.
- Existing repo-root `.venv` inspected as Python 3.13.6 via `.venv/pyvenv.cfg`, then renamed to `.venv-py310-legacy` before Story 1.1a created the required Python 3.12 environment.
- `python -m uv` used instead of bare `uv` because the user-scope `uv` install was not on PowerShell `PATH`.
- AC-2/AC-3 commands executed with `UV_CACHE_DIR=.uv-cache` and `uv run --no-project` to avoid sandbox cache-permission issues and setuptools editable-build discovery on this non-packaged repo.

### Completion Notes List

- Created `.venv` with Python 3.12.13. Installed the nine core packages in AC-1 with zero resolver conflicts; `requirements.lock` was re-emitted during review remediation as plain UTF-8 text with 49 pinned lines covering the nine direct packages plus transitive dependencies.
- AC-2 import smoke passed with `STDOUT=ok` and empty stderr using `python -m uv run --no-project --python .\.venv\Scripts\python.exe python -c "import langgraph, langchain_openai, pydantic, fastapi, langsmith; print('ok')"`.
- `requires-python` was intentionally left at `>=3.11`. Story 1.1a enforces Python 3.12 at the migration venv boundary while legacy primary-repo code remains 3.11-compatible.
- `ruff check .` still reports the known 1338 pre-existing legacy findings outside migration scope. Scoped validation `ruff check app` exits 0, which is the relevant Story 1.1a migration-tree gate.
- Import-linter did not silently skip a missing root package: review confirmed that `lint-imports --config pyproject.toml` fails with `Module 'app.marcus' does not exist.` when lane/gate stubs are absent. Minimal stub packages `app/`, `app/marcus/`, `app/cora/`, and `app/gates/` remain the smallest practical substrate, and Story 1.1b now treats them as pre-seeded scaffolds.
- Callable-level `asyncio.sleep` enforcement remains deferred to Slab 3 as documented in the TOML TODO, because import-linter operates at module-import granularity, not attribute-call granularity.
- `.env.example` is trackable (`git check-ignore .env.example` exit 1 after negation) and `.env` remains ignored via `.gitignore:2:.env`.
- K-floor framing note: this substrate-bootstrap story creates zero pytest nodes, so the 1.3× K target was treated as command-verification coverage rather than test-node count.
- FR60 activation baseline commit SHA remains `a905de0`; review remediation aligned story text with sprint governance so freeze activation is keyed to Story 1.1a status `done`.

### File List

- `.gitignore`
- `.env.example`
- `app/__init__.py`
- `app/cora/__init__.py`
- `app/gates/__init__.py`
- `app/marcus/__init__.py`
- `pyproject.toml`
- `requirements.lock`
- `_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-22: Completed Story 1.1a runtime substrate bootstrap. Added Python 3.12 migration venv lockfile, pyproject import-linter contract stubs, minimal `app/` package stubs required for import-linter execution, and `.env.example` gitignore exception. Scoped migration-tree validation passed (`ruff check app`, `lint-imports`, import smoke).
- 2026-04-22: Code-review remediation re-emitted `requirements.lock` as UTF-8 text, aligned Story 1.1b handoff assumptions with import-linter stub-package requirements, and repaired Story 1.1a closeout integrity.

### Review Findings

- [x] [Review][Patch] Regenerate requirements.lock as plain UTF-8 text [requirements.lock:1]
- [x] [Review][Patch] Align Story 1.1a/1.1b serial handoff with import-linter stub-package requirement [_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md:186]
- [x] [Review][Patch] Repair Story 1.1a closeout record and FR60 timing note [_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md:3]
- [x] [Review][Defer] Broader hybrid bootstrap docs still install from requirements.txt without migration-only import-linter tooling [requirements.txt:26] - deferred, pre-existing
