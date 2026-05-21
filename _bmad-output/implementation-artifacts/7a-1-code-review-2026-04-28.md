# Story 7a.1 Code Review - Directive Composer

**Report path:** `_bmad-output/implementation-artifacts/7a-1-code-review-2026-04-28.md`  
**Review executed:** 2026-04-29 local session; filename kept as requested for the 2026-04-28 story cycle.  
**Branch:** `dev/langchain-langgraph-foundation`  
**HEAD:** `d0ef522`  
**Review mode:** full `bmad-code-review` style pass: Blind Hunter, Edge Case Hunter, Acceptance Auditor.  
**Reviewed surface:** working tree Story 7a.1 files plus required docs. `git diff --shortstat HEAD` reports `10 files changed, 577 insertions(+), 32 deletions(-)` before untracked new Story 7a.1 files.

## Verdict

**HALT-AND-REMEDIATE.**

The focused and broad verification batteries are green, but the story is not ready for `review -> done`. There are five PATCH findings that affect acceptance traceability or substrate-shape confidence:

1. The trial-475 regression does not actually prove the production runner/Texas path receives the composed directive.
2. The binding M-R4 composition test case was not added to `tests/composition/test_texas_to_cd_chain.py`.
3. The required Composition Spec Section 10 decision-log entry for `runner_supplied_payload` is missing and was incorrectly pushed into a deferred follow-on.
4. Windows-stable path serialization is partial; `trial-start.json` still emits several `str(Path)` values.
5. The editor fallback path is not fully fail-loud or Windows-portable under the edge cases named in the review prompt.

One additional low-risk test pin is also PATCH: the CLI exit-code-2 cancel path is implemented, but not directly tested at the CLI wrapper.

## Layer Findings

### Layer 1 - Blind Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| BH-1 | HIGH | PATCH | trial-475 regression overclaims production dispatch coverage. | `tests/parity/test_trial_475_directive_composition_regression.py:102-129` asserts directive materialization only and explicitly notes offline mode skips Texas. `:191-220` calls `retrieval_dispatch.dispatch_retrieval(...)` directly, bypassing `start_trial -> run_production_trial -> adapter -> texas.graph._act`. |
| BH-2 | MED | PATCH | Single-file `--input` can still run with `directive_path=None`, preserving the silent fixture fallback risk for that boundary. | `app/marcus/cli/trial.py:183-189` activates composition only for directories; `run_production_trial(..., directive_path=None)` can reach Texas without runner payload. |
| BH-3 | MED | PATCH | W-R6 POSIX path serialization is incomplete. | `app/marcus/cli/trial.py:258-263` serializes `input`, `run_registry_path`, and cost-report paths with `str(Path)` into `trial-start.json` / CLI JSON. |
| BH-4 | LOW | DISMISS | PyYAML byte drift is possible in principle across future versions. | Current `uv.lock` pins PyYAML 6.0.3 and the golden bytes test fails on drift. No immediate patch required. |

### Layer 2 - Edge Case Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| EH-1 | HIGH | PATCH | Binding M-R4 case is missing from the actual composition test file. | `tests/composition/test_texas_to_cd_chain.py:15-35` has one parametrized `trial_id` case only; no directive-composer-driven case exists. |
| EH-2 | MED | PATCH | `_resolve_editor()` and `_edit_directive_in_editor()` do not cover the requested edge cases. | `app/marcus/cli/trial.py:53-75` returns whitespace `$EDITOR` values, does not check fallback availability, catches only `FileNotFoundError`, and ignores non-zero editor exit codes. |
| EH-3 | LOW | PATCH | CLI cancel exit code is not directly pinned. | `start_trial_cli` returns `2` at `app/marcus/cli/trial.py:296-297`, but `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py:197-221` only calls `start_trial`, not `start_trial_cli`. |
| EH-4 | LOW | DEFER | Resume mode does not re-thread `directive_path`, but current Path Z semantics make this safe for 7a.1. | `resume_production_trial` starts from post-gate checkpoint and skips already-present Texas contributions; current production gates are G1/G2C/G3/G4. Re-derive from `<run_dir>/directive.yaml` before future G0/fold work. |
| EH-5 | LOW | DISMISS | `runner_supplied_payload` collision with upstream output keys is not a current overwrite bug. | `_payload_from_dependencies` nests upstream contribution output under `dependency_map` input keys; only an input key named `directive_path`/`bundle_dir` collides, and the docstring states runner payload wins. |

### Layer 3 - Acceptance Auditor

| ID | Severity | Disposition | Finding | Violated AC / rider |
|---|---|---|---|---|
| AA-1 | HIGH | PATCH | AC-7.1-H is partially orphaned: the test does not prove Texas receives the composed directive through the production code path. | AC-H, M-R1, M-R5 |
| AA-2 | HIGH | PATCH | M-R4 did not land. | M-R4; AC-7.1-E test pin |
| AA-3 | HIGH | PATCH | Composition Spec Section 10 decision-log entry for `runner_supplied_payload` is missing and cannot be deferred beyond this story close. | A-R3; AC-7.1-D; AC-7.1-L |
| AA-4 | MED | PATCH | W-R6 is partial; several serialized CLI payload paths use platform-native `str(Path)`. | W-R6; AC-7.1-D/B path stability |
| AA-5 | MED | PATCH | P-R6 editor fallback chain is only partly implemented and partly tested. | P-R6; AC-7.1-C |
| AA-6 | LOW | DISMISS | The `directive-composer` manifest node itself is deferred to 7a.2. | Accepted by story Dev Agent Record and the operator prompt for A-R4; structural deferral pin exists in `tests/structural/test_pipeline_manifest_directive_composer_node.py`. |

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 6 |
| DEFER | 1 |
| DISMISS | 3 |

No `decision_needed` items remain. The correct remediation path is concrete.

## Independent Verification Battery

### Focused pytest

Command:

```powershell
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator tests/integration/marcus/test_directive_confirm_or_edit_prompt.py tests/integration/marcus/test_production_runner_threads_directive.py tests/parity/test_trial_475_directive_composition_regression.py tests/composition/ tests/structural/ -q --tb=short
```

Stdout:

```text
......................................................................   [100%]
70 passed in 4.73s
```

### Pipeline manifest lockstep

Command:

```powershell
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
```

Stdout:

```text
lockstep-check exit=0 trace=C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid\reports\dev-coherence\2026-04-29-0344\check-pipeline-manifest-lockstep.PASS.yaml
```

### Sandbox-AC validator

Command:

```powershell
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md
```

Stdout:

```text
PASS — no sandbox-AC violations across 1 story file(s).
```

### Ruff

Command:

```powershell
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/directive_composer.py app/marcus/cli/trial.py app/marcus/orchestrator/production_runner.py app/marcus/orchestrator/dispatch_adapter.py tests/unit/marcus/orchestrator tests/integration/marcus/test_directive_confirm_or_edit_prompt.py tests/integration/marcus/test_production_runner_threads_directive.py tests/parity/test_trial_475_directive_composition_regression.py tests/composition/test_slab_7a_opener_composition_smoke.py tests/structural
```

Stdout:

```text
All checks passed!
```

### Import linter

Command:

```powershell
.venv/Scripts/lint-imports.exe
```

Stdout:

```text
=============
Import Linter
=============


---------
Contracts
---------

Analyzed 281 files, 1199 dependencies.
--------------------------------------

app.marcus and app.cora are lane-isolated siblings (D3 + D4 lane separation) KEPT
Marcus Contract M1 - only app.marcus.orchestrator.write_api may import 
app.models.state.run_state KEPT
Marcus Contract M2 - app.marcus may not import app.cora KEPT
Cora Contract C1 - app.cora may not import app.marcus or marcus KEPT
Cora Contract C2 - Marcus may not import app.cora KEPT
Marcus Contract M3 - app.specialists may not import app.marcus 
facade/intake/orchestrator KEPT
Marcus Contract M4 - app.marcus.dispatch stays dependency-light KEPT
app.gates.** may not import schedulers (D3 HIL tamper-evidence) KEPT
Contract C3 — only the three authorized bridge modules may import 
app.gates.resume_api (D3) KEPT

Contracts: 9 kept, 0 broken.
```

### Composition smoke script

Command:

```powershell
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
```

Stdout:

```text
PASS slab-7a-opener composition smoke
  trial_id=dbc37787-ff05-47b3-b405-f7c3c2a2a270
  directive_digest=1d84e81b440c2984...
  texas_contribution_digest=3709fb520ce5c041...
```

### Broad regression slice

Command:

```powershell
.venv/Scripts/python.exe -m pytest tests/unit/marcus tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
```

Stdout:

```text
........................................................................ [ 36%]
...............................................s........................ [ 72%]
.......................................................                  [100%]
198 passed, 1 skipped in 12.69s
```

## Composition Spec Section 11 Trigger Check

**Verdict:** no Option B -> Option C migration trigger fires.

Reasoning:

- No fan-out/parallel dispatch need is introduced.
- No partial-state mid-execution need is introduced.
- No gate precedence promotion is introduced.
- Adapter LOC remains well below the Section 11 threshold.
- No new Texas `_act` body category is introduced; this is a carrier addition.

**Required PATCH:** the additive `runner_supplied_payload` kwarg is still a composition-substrate decision under Composition Spec Section 10. The story already says the entry is required at close, but the Dev Agent Record incorrectly lists it as a deferred follow-on. It must land before Story 7a.1 is marked done.

## AC Coverage Matrix

| AC | Status | Test pins / evidence | Audit note |
|---|---|---|---|
| A - composer module + pure function | PASS-WITH-PATCH | `tests/unit/marcus/orchestrator/test_directive_composer_pure.py`; `tests/parity/test_trial_475_directive_composition_regression.py::test_composer_replays_trial_475_corpus_shape` | Directory, nested, urls.txt, overrides, empty/missing are covered. Single-file behavior is only covered by direct composer failure, while `start_trial` skips composition for files; see PATCH P4. |
| B - materialization + digest | PASS | `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py` | Golden fixture exists and matches. Implementation uses PyYAML, not ruamel; accepted by dev-cycle halt-and-adapt because PyYAML is the shipped dep. |
| C - confirm/edit prompt | PASS-WITH-PATCH | `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py` | Basic c/e/s/x, invalid loop, non-TTY, auto-confirm are covered. Editor fallback edge cases named in prompt are thin; see PATCH P5. |
| D - Texas dispatch threading | PASS-WITH-PATCH | `tests/integration/marcus/test_production_runner_threads_directive.py` | Helper and adapter merge semantics are covered. Full runner-to-Texas dispatch path with composed directive is not covered; see PATCH P1. |
| E - envelope append-only + SHA256 | FAIL-PATCH | Existing `tests/composition/test_texas_to_cd_chain.py` | Existing fixture-stub Texas->CD chain still passes, but the required directive-composer-driven parametrize case is missing; see PATCH P2. |
| F - Composition Smoke | PASS | `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`; `tests/composition/test_slab_7a_opener_composition_smoke.py` | Smoke writes directive and appends one Texas contribution. |
| G - pipeline manifest declaration | DEFER-ACCEPTED | `tests/structural/test_pipeline_manifest_directive_composer_node.py`; manifest comment at `state/config/pipeline-manifest.yaml:60-68`; lockstep PASS | Node itself is deferred to 7a.2 per dev-cycle finding. Structural deferral pin landed. |
| H - trial-475 regression | FAIL-PATCH | `tests/parity/test_trial_475_directive_composition_regression.py` | Materialization is tested; actual production dispatch threading is not. Direct dispatch test bypasses runner/adapter/Texas graph. |
| I - G0 at-gate doc | PASS | `docs/conversational-gates/g0-directive-composition.md`; `tests/structural/test_g0_directive_composition_doc_exists.py` | Four subsections, reservation sentence, Mermaid diagram, and local_file worked example are present. |
| J - cancel-trial path | PASS-WITH-PATCH | `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py::test_cancel_path_writes_cancellation_record_and_exits_2`; code `start_trial_cli` lines 278-298 | `start_trial` payload and cancellation record are covered. CLI wrapper exit code 2 is not directly tested; see PATCH P6. |
| K - N-item / anti-pattern / Composition Spec trace | PASS-WITH-PATCH | Story Dev Agent Record N-item trace lines 556-564 | Trace exists, but Section 10 decision-log entry is missing and should not be deferred. |
| L - D12 close protocol | PENDING | Story remains `review`; sprint-status flip intentionally not performed by Codex | Do not close until PATCH items land and verification is rerun. |

## Rider Trace

| Rider | Status | Evidence / gap |
|---|---|---|
| W-R4 named carrier | LANDED | `dispatch_adapter.py:62-79`; `test_production_runner_threads_directive.py:60-107` asserts top-level `directive_path` + `bundle_dir` and runner payload wins. |
| M-R4 correct test file pin | MISSING - PATCH | No composer-driven parametrize case in `tests/composition/test_texas_to_cd_chain.py`; file has one case only. |
| M-R5 monkeypatch boundary | PARTIAL - PATCH | `dispatch_retrieval` is monkeypatched in the parity test fixture, but the start-trial tests run offline and skip Texas; the direct dispatch test bypasses the runner/adapter path. |
| P-R4 doc worked example + reservation | LANDED | `docs/conversational-gates/g0-directive-composition.md`; structural tests assert reservation and local_file-only worked example. |
| A-R3 Option A | PARTIAL - PATCH | Additive kwarg landed and runner gates it to canonical `texas`; Section 10 decision-log entry is missing. |
| A-R5 bundle_dir derivation | LANDED | `production_runner.py:533-538` derives `bundle_dir = run_dir / "bundle"` and creates it. |
| W-R5 lockstep tolerance | LANDED | `pipeline_manifest.py` includes `v4.2-migration-stub-with-fold-flags`; lockstep check exits 0. |
| W-R6 POSIX paths | PARTIAL - PATCH | Directive locators and runner payload use `.as_posix()`, but `trial-start.json` still serializes several paths via `str(Path)`. |
| M-R6 golden bytes | LANDED | `tests/fixtures/directives/composed_directive_golden.yaml.bytes`; materialization golden test passes. |
| P-R5 Mermaid diagram | LANDED | Structural test asserts `sequenceDiagram` in G0 doc. |
| P-R6 editor fallback | PARTIAL - PATCH | Env -> platform fallback exists, but whitespace env, missing fallback binary, `OSError`, and non-zero editor return are not fail-loud. |
| A-R4 canonical manifest field names | DEFER-ACCEPTED | Node deferred to 7a.2; manifest comment and structural pin landed. |

## Halt-And-Adapt Cycle Audit

| Cycle | Dev record claim | Review verdict |
|---|---|---|
| 1 | `ruamel.yaml` not shipped; switched to PyYAML. | Sound. PyYAML is in `pyproject.toml` and `uv.lock`; golden bytes test mitigates drift. Clean up stale ruamel wording opportunistically. |
| 2 | Composer manifest node tripped lockstep set-equality; deferred to 7a.2. | Acceptable for A-R4 per operator prompt. Keep deferral visible and file deferred-inventory at T12. |
| 3 | Resume-mode does not thread `directive_path`; safe under Path Z first-contribution-wins. | Acceptable for 7a.1 because Texas runs before current production pause gates. Must be revisited before G0/fold work can pause pre-Texas. |
| 4 | Temporary `tests/integration/marcus/__init__.py` package collision removed. | Sound; broad regression is green. |

## Suggested PATCH Commits

### P1 - Add real production-path trial-475 dispatch proof

**Files:** `tests/parity/test_trial_475_directive_composition_regression.py` and/or `tests/integration/marcus/test_production_runner_threads_directive.py`.

Suggested shape:

```diff
+def test_start_trial_threads_composed_directive_to_texas_dispatch(...):
+    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
+    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
+    monkeypatch.setenv("LANGSMITH_PROJECT", "test")
+    monkeypatch.setattr(production_runner, "_has_live_openai", lambda: True)
+    monkeypatch.setattr(
+        "app.specialists.texas.graph.dispatch_retrieval",
+        fake_dispatch_capture,
+    )
+    payload = start_trial(
+        preset="production",
+        input_path=MINI_CORPUS,
+        operator_id="trial-475-regression",
+        trial_id=uuid4(),
+        runs_root=runs_root,
+        auto_confirm_directive=True,
+        allow_offline_cost_report=False,
+    )
+    assert dispatch_capture["calls"][0]["directive_path"]
+    assert dispatch_capture["calls"][0]["bundle_dir"]
+    assert payload["directive_path"]
```

If using `retrieval_dispatch.dispatch_retrieval` as the monkeypatch target, avoid the direct-import trap: `app.specialists.texas.graph` imports `dispatch_retrieval` at module load, so patch `app.specialists.texas.graph.dispatch_retrieval` for graph-path tests, or patch `subprocess.run` inside `retrieval_dispatch`.

### P2 - Add M-R4 composer-driven case to `test_texas_to_cd_chain.py`

**File:** `tests/composition/test_texas_to_cd_chain.py`.

Suggested shape:

```diff
-@pytest.mark.parametrize("trial_id", [TRIAL_ID])
-def test_texas_to_cd_chain_accumulates_envelope_and_threads_dependency(...):
+@pytest.mark.parametrize("directive_source", ["fixture_stub", "composer_directive"])
+def test_texas_to_cd_chain_accumulates_envelope_and_threads_dependency(
+    trial_id: UUID,
+    monkeypatch: pytest.MonkeyPatch,
+    tmp_path: Path,
+    directive_source: str,
+):
+    if directive_source == "composer_directive":
+        composed = compose_directive(corpus_path=mini_corpus, run_id=str(trial_id))
+        directive_path, _ = materialize_directive(composed, tmp_path / str(trial_id))
+        monkeypatch.setattr(
+            "app.specialists.texas.graph.dispatch_retrieval",
+            lambda **kw: fake_bundle_receipt(directive_path=kw["directive_path"]),
+        )
```

The assertion should still prove envelope append, digest presence, and CD dependency input shape.

### P3 - Add Composition Spec Section 10 decision-log entry before close

**File:** `docs/dev-guide/composition-specification.md`.

Suggested row:

```diff
+| 2026-04-29 | Story 7a.1 runner-supplied directive carrier: `ProductionDispatchAdapter.build_specialist_state(..., runner_supplied_payload=None)` accepts a runner-owned payload merged into `cache_prefix`; Story 7a.1 uses reserved top-level keys `directive_path` and `bundle_dir`, gated to Texas only. | Closes trial-475 Gap 2 without synthetic specialist contribution or specialist-body coupling; preserves composer as orchestration and keeps adapter as the sole sanctioned coupling point. | Slab 7a.1 A-R3 Option A | Claude dev + Codex code review; operator close pending |
```

Use the story close date chosen by Claude/operator at remediation time. The important part is: do not leave this as deferred inventory.

### P4 - Decide and patch single-file `--input` behavior

**File:** `app/marcus/cli/trial.py`; tests in `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py` or parity.

Preferred fail-loud patch if single-file corpus is out of scope:

```diff
     directive_path: Path | None = None
     directive_digest: str | None = None
-    if input_path.is_dir():
+    if not input_path.is_dir():
+        raise DirectiveConfirmationRequiredError(
+            "G0 directive composition requires a corpus directory; single-file "
+            "--input would leave Texas without directive_path and is refused"
+        )
+    if input_path.is_dir():
         composed = compose_directive(
```

Alternative patch: support a one-file source map and materialize a one-source directive. Either is acceptable, but do not allow production Texas dispatch with `directive_path=None`.

### P5 - Complete W-R6 POSIX serialization

**File:** `app/marcus/cli/trial.py`.

Suggested patch:

```diff
-        "input": str(input_path),
+        "input": input_path.as_posix(),
         "operator_id": operator_id,
-        "run_registry_path": str(run_json),
-        "cost_report_json": str(cost_json) if cost_json is not None else None,
+        "run_registry_path": run_json.as_posix(),
+        "cost_report_json": cost_json.as_posix() if cost_json is not None else None,
         "cost_report_markdown": (
-            str(cost_json.with_suffix(".md")) if cost_json is not None else None
+            cost_json.with_suffix(".md").as_posix() if cost_json is not None else None
         ),
```

Add a Windows-style-path unit pin using `PureWindowsPath` or monkeypatched paths if practical.

### P6 - Harden editor fallback and test CLI exit 2

**File:** `app/marcus/cli/trial.py`; tests in `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py`.

Suggested patch:

```diff
+import shutil
 ...
 def _resolve_editor() -> str:
-    editor = os.environ.get("EDITOR")
+    editor = (os.environ.get("EDITOR") or "").strip()
     if editor:
         return editor
-    if sys.platform.startswith("win"):
-        return "notepad"
-    return "vi"
+    fallback = "notepad" if sys.platform.startswith("win") else "vi"
+    if shutil.which(fallback) is None:
+        raise EditorUnavailableError(
+            f"editor fallback {fallback!r} not found; set EDITOR"
+        )
+    return fallback
 ...
     try:
-        subprocess.call([editor, str(directive_path)])
-    except FileNotFoundError as exc:
+        exit_code = subprocess.call([editor, str(directive_path)])
+    except OSError as exc:
         raise EditorUnavailableError(...) from exc
+    if exit_code != 0:
+        raise EditorUnavailableError(f"editor {editor!r} exited {exit_code}")
```

Add a direct `start_trial_cli` cancel test:

```diff
+def test_start_trial_cli_cancel_returns_exit_2(...):
+    monkeypatch.setattr(trial_module, "start_trial", lambda **_: {"status": "cancelled-at-g0"})
+    assert trial_module.start_trial_cli(args) == 2
```

## Deferred Item

**D-1 - Resume-mode directive re-derive.** Keep the planned follow-on, but do not treat it as blocking Story 7a.1 because current Path Z first-contribution-wins means Texas's contribution is already present before resume on the current production gate set. Reactivate before Story 7a.2+ work makes G0/fold points pause before Texas.

## Dismissed Items

| ID | Rationale |
|---|---|
| X-1 PyYAML drift | `uv.lock` pins PyYAML 6.0.3 and golden bytes test catches changes. |
| X-2 runner payload collision with upstream output dict keys | Upstream outputs are nested by dependency input key; only direct input-key collision is overwritten, and that behavior is documented as runner payload wins. |
| X-3 manifest node deferral | The operator review prompt explicitly treats A-R4 as N/A because composer node is deferred to 7a.2; deferral comment and structural pin are present. |

## Close Guidance

Claude should remediate PATCH items P1-P6, rerun the focused and broad verification battery, then update the story close artifacts. Do not flip `sprint-status.yaml` to done until:

- AC-H proves production dispatch threading through the real path.
- M-R4 is visibly present in `tests/composition/test_texas_to_cd_chain.py`.
- Composition Spec Section 10 contains the A-R3 decision entry.
- W-R6/P-R6 edge tests are green.
