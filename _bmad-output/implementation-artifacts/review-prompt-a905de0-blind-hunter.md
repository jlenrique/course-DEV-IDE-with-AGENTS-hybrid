# Review Prompt: Blind Hunter

Review target: commit `a905de0`
Role: Blind Hunter
Mode: Diff only. No project context. No spec. No repo exploration.

Instructions:
- Use an adversarial code review mindset.
- Review only the diff below.
- Focus on concrete bugs, regressions, unsafe assumptions, or incorrect behavior.
- Do not comment on style unless it creates a real defect.
- Output findings as a Markdown list.
- For each finding: short title, severity, evidence from the diff, and why it matters.
- If there are no findings, say `No findings.`

Diff:

```diff
commit a905de0e740eff0440de9252a22f44c0ee35692a
Author: Juan Leon <131621931+jlenrique@users.noreply.github.com>
Date:   Wed Apr 22 18:47:45 2026 -0400

    feat(migration): Slab 1 Story 1.1a - runtime substrate environment + dependencies

    Implements Architecture D1-D13 runtime substrate bootstrap per Amendment F strict-serial Story 1.1a.

    Creates the Python 3.12 migration venv and lockfile, adds Slab 1 import-linter contract stubs, wires the .env.example tracking exception, and activates FR60 forward-port freeze semantics at this commit.

diff --git a/.env.example b/.env.example
new file mode 100644
index 0000000..d55d21f
--- /dev/null
+++ b/.env.example
@@ -0,0 +1,4 @@
+OPENAI_API_KEY=<placeholder>
+LANGSMITH_API_KEY=<placeholder>
+LANGSMITH_PROJECT=course-dev-ide-migration
+DATABASE_URL=postgresql://user:pass@localhost:5432/course_dev_ide_migration
diff --git a/.gitignore b/.gitignore
index 9e76ace..b4d69d8 100644
--- a/.gitignore
+++ b/.gitignore
@@ -1,6 +1,7 @@
 # Local secrets — never commit (document keys in docs/admin-guide.md)
 .env
 .env.*
+!.env.example
 
 # Cursor / Playwright MCP local logs
 .playwright-mcp/
diff --git a/_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md b/_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md
index 6659a1b..60d9ade 100644
--- a/_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md
+++ b/_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md
@@ -1,6 +1,6 @@
 # Migration Story 1.1a: Runtime Substrate Environment + Dependencies
 
-Status: ready-for-dev
+Status: review
 
 **Track:** LangChain + LangGraph migration (hybrid clone only — `dev/langchain-langgraph-foundation` on remote `course-DEV-IDE-with-AGENTS-hybrid`).
 **Epic:** Slab 1 Substrate — Runtime + Models + Manifest + Bridges + Docs (migration Epic 1).
@@ -180,16 +180,46 @@ The commit message should explicitly name FR60 activation so the policy change i
 
 ### Agent Model Used
 
-{{agent_model_name_version}}
+gpt-5.4
 
 ### Debug Log References
 
+- T1 reading set completed: architecture-langchain-langgraph-migration.md; prd-langchain-langgraph-migration.md; docs/dev-guide/pydantic-v2-schema-checklist.md; docs/dev-guide/story-cycle-efficiency.md.
+- Existing repo-root `.venv` inspected as Python 3.13.6 via `.venv/pyvenv.cfg`, then renamed to `.venv-py310-legacy` before Story 1.1a created the required Python 3.12 environment.
+- `python -m uv` used instead of bare `uv` because the user-scope `uv` install was not on PowerShell `PATH`.
+- AC-2/AC-3 commands executed with `UV_CACHE_DIR=.uv-cache` and `uv run --no-project` to avoid sandbox cache-permission issues and setuptools editable-build discovery on this non-packaged repo.
+
 *(populated at dev-story time)*
 
 ### Completion Notes List
 
+- Created `.venv` with Python 3.12.13. Installed the nine core packages in AC-1 with zero resolver conflicts; `requirements.lock` emitted at repo root with 49 pinned lines covering the nine direct packages plus transitive dependencies.
+- AC-2 import smoke passed with `STDOUT=ok` and empty stderr using `python -m uv run --no-project --python .\.venv\Scripts\python.exe python -c "import langgraph, langchain_openai, pydantic, fastapi, langsmith; print('ok')"`.
+- `requires-python` was intentionally left at `>=3.11`. Story 1.1a enforces Python 3.12 at the migration venv boundary while legacy primary-repo code remains 3.11-compatible.
+- `ruff check .` still reports the known 1338 pre-existing legacy findings outside migration scope. Scoped validation `ruff check app` exits 0, which is the relevant Story 1.1a migration-tree gate.
+- Import-linter did not silently skip a missing root package: it fatally required an `app` package to exist, and its forbidden external modules also required `include_external_packages = true`. Minimal stub packages `app/`, `app/marcus/`, `app/cora/`, and `app/gates/` were added so the two Slab-1 contract stubs could execute and pass. This is the smallest practical boundary-creep into 1.1b; reviewer should confirm whether 1.1b now treats these as pre-seeded scaffolds.
+- Callable-level `asyncio.sleep` enforcement remains deferred to Slab 3 as documented in the TOML TODO, because import-linter operates at module-import granularity, not attribute-call granularity.
+- `.env.example` is trackable (`git check-ignore .env.example` exit 1; `git status --short -- .env.example` shows `?? .env.example`). `.env` remains ignored via `.gitignore:2:.env`.
+- K-floor framing note: this substrate-bootstrap story creates zero pytest nodes, so the 1.3× K target was treated as command-verification coverage rather than test-node count.
+- FR60 activation commit SHA: recorded in the commit created for this story and echoed in the final dev-story handoff.
+
 *(populated at dev-story time — include: final ruff/lint-imports exit codes, lockfile package count, import-smoke stdout capture, K-floor framing decision, `requires-python` decision, any linter-contract tightening deferred to Slab 3, FR60-activation commit SHA)*
 
 ### File List
 
+- `.gitignore`
+- `.env.example`
+- `app/__init__.py`
+- `app/cora/__init__.py`
+- `app/gates/__init__.py`
+- `app/marcus/__init__.py`
+- `pyproject.toml`
+- `requirements.lock`
+- `_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md`
+- `_bmad-output/implementation-artifacts/sprint-status.yaml`
+
+### Change Log
+
+- 2026-04-22: Completed Story 1.1a runtime substrate bootstrap. Added Python 3.12 migration venv lockfile, pyproject import-linter contract stubs, minimal `app/` package stubs required for import-linter execution, and `.env.example` gitignore exception. Scoped migration-tree validation passed (`ruff check app`, `lint-imports`, import smoke).
+
 *(populated at dev-story time — expected: `requirements.lock` new, `pyproject.toml` modified, `.env.example` new, `.gitignore` modified)*
diff --git a/_bmad-output/implementation-artifacts/sprint-status.yaml b/_bmad-output/implementation-artifacts/sprint-status.yaml
index d948777..cc00e64 100644
--- a/_bmad-output/implementation-artifacts/sprint-status.yaml
+++ b/_bmad-output/implementation-artifacts/sprint-status.yaml
@@ -734,7 +734,7 @@ development_status:
   # the migration-guide §8 forward-port playbook.
   # =============================================================================
   migration-epic-1-slab-1-substrate: in-progress  # Opened 2026-04-22 by migration-1-1a-runtime-substrate-environment-and-dependencies.
-  migration-1-1a-runtime-substrate-environment-and-dependencies: ready-for-dev  # Authored 2026-04-22 via bmad-create-story. Pts=1, single-gate, K-target 1.3×. Slab 1 kickoff.
+  migration-1-1a-runtime-substrate-environment-and-dependencies: review  # Authored 2026-04-22 via bmad-create-story. Pts=1, single-gate, K-target 1.3×. Slab 1 kickoff.
 
   # =============================================================================
   # LESSON PLANNER MVP SPRINT-STATUS APPEND (2026-04-18, late session)
diff --git a/app/__init__.py b/app/__init__.py
new file mode 100644
index 0000000..fdc63e1
--- /dev/null
+++ b/app/__init__.py
@@ -0,0 +1 @@
+"""Migration app package stub for Slab 1 import-linter contracts."""
diff --git a/app/cora/__init__.py b/app/cora/__init__.py
new file mode 100644
index 0000000..c59c127
--- /dev/null
+++ b/app/cora/__init__.py
@@ -0,0 +1 @@
+"""Cora lane stub for Slab 1 import-linter contracts."""
diff --git a/app/gates/__init__.py b/app/gates/__init__.py
new file mode 100644
index 0000000..5addf11
--- /dev/null
+++ b/app/gates/__init__.py
@@ -0,0 +1 @@
+"""Gate package stub for Slab 1 import-linter contracts."""
diff --git a/app/marcus/__init__.py b/app/marcus/__init__.py
new file mode 100644
index 0000000..0e122b7
--- /dev/null
+++ b/app/marcus/__init__.py
@@ -0,0 +1 @@
+"""Marcus lane stub for Slab 1 import-linter contracts."""
diff --git a/pyproject.toml b/pyproject.toml
index 7e2a025..99059ee 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -28,6 +28,7 @@ dev = [
     "pytest-timeout>=2.3,<3",
     "responses>=0.25,<1",
     "ruff>=0.4,<1",
++    "import-linter>=2.0,<3",
     "pre-commit>=3.7,<5",
     "jsonschema>=4.0,<5",
 ]
@@ -64,6 +65,22 @@ markers = [
     "trial_critical: dev-side tests guarding the pre-Prompt-1 trial path (run_constants validator, preflight receipt, pack-doc schema lockstep). Run before firing any trial production run via `pytest -m trial_critical`. Not a runtime gate — a dev confidence check.",
 ]
 
+[tool.importlinter]
+root_packages = ["app"]
+include_external_packages = true
+
+[[tool.importlinter.contracts]]
+name = "app.marcus and app.cora are lane-isolated siblings (D3 + D4 lane separation)"
+type = "independence"
+modules = ["app.marcus", "app.cora"]
+
+[[tool.importlinter.contracts]]
+name = "app.gates.** may not import schedulers (D3 HIL tamper-evidence)"
+type = "forbidden"
+source_modules = ["app.gates"]
+forbidden_modules = ["threading", "apscheduler", "schedule"]
+# TODO Slab 3: callable-level asyncio.sleep ban via ruff custom rule or import-time assertion in app/gates/resume_api.py
+
 [build-system]
 requires = ["setuptools>=68"]
 build-backend = "setuptools.build_meta"
diff --git a/requirements.lock b/requirements.lock
new file mode 100644
index 0000000..d6d8e66
Binary files /dev/null and b/requirements.lock differ
```
