# Migration Story 7c-housekeeping-2: AST-Based Rewrite of `test_no_unauthorized_callers` (per A19 Anti-Pattern)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessor 7c.21 closed (D12-2 anti-pattern A19 documents the remediation contract).)*
**Sprint key:** `migration-7c-housekeeping-2-scanner-staleness-rewrite`
**Source:** Stories 7c.13 + 7c.14 T11 review NIT-DISMISSED (per `7c-13-code-review-2026-05-06.md` + `7c-14-code-review-2026-05-06.md`); D12-2 anti-pattern **A19 "Class-definition substring scanners go stale when class names change"** at `docs/dev-guide/specialist-anti-patterns.md` (landed at 7c.21 close).
**Pts:** 1
**K-target:** 1.2×
**Estimated LOC:** ~150 (rewrite `tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` ~80 + parametrized fixture cases ~50 + integration test for AST visitor ~20)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite
**Lookahead-tier:** 1
**files_touched:** 1 modified (`tests/integration/gates/test_resume_api_authority.py`) + 0 new

---

## Story

As the dev-agent,
I want `test_no_unauthorized_callers` rewritten from substring-scan-with-singular-filename-exclusion to AST-walk-for-Call-nodes-with-glob-filename-exclusion,
So that the test correctly distinguishes class definitions (`class Section02AOperatorVerdict(BaseModel):`) from direct constructor invocations (`OperatorVerdict(...)` outside authorized files), and the filename exclusion `operator_verdict*.py` glob captures all 14+ §section variants instead of just the original singular `operator_verdict.py`.

This is a **pure test-hardening story** — no app/* impact. The 7c.21 D12-2 anti-pattern A19 document specifies the AST remediation contract; this story implements it.

---

## Predecessor / Dependency Context

- **`tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers`** (current state at line 17-30): substring scan for `OperatorVerdict(` against `app/**/*.py`; filename exclusion `if path.name == "operator_verdict.py": continue` matches ONLY the singular original; misses all variant filenames (`operator_verdict_section_*.py`).
- **A19 anti-pattern** at `docs/dev-guide/specialist-anti-patterns.md` (landed at 7c.21 close): documents the staleness root cause + AST remediation contract + Story 7c.20b attribution.
- **14+ OperatorVerdict variant files** under `app/models/operator_verdict_section_*.py`: each has `class Section{NN}OperatorVerdict(BaseModel):` definitions that the substring scanner currently incorrectly classifies as offenders.
- **3 authorized bridge modules** (allowed-list): `app/mcp_server/tools/gate_decide.py` + `app/http/gate_endpoint.py` + `app/marcus/cli/gate_cli.py`. These import `resume_api` directly + may construct `OperatorVerdict` instances — they're allowed.

---

## Acceptance Criteria

### AC-1 — AST-based scanner for Call-nodes (replaces substring scan)

**Given** the current substring-based scanner that catches class definitions
**When** the dev-agent rewrites `test_no_unauthorized_callers` to use AST traversal
**Then**:
1. The test parses each `app/**/*.py` file via `ast.parse(text)`.
2. For each module's AST, visit `Call` nodes via an `ast.NodeVisitor` subclass.
3. Detect direct constructor calls to `OperatorVerdict` OR any `Section*OperatorVerdict` subclass: `Call.func.id` matches the regex `^Section\w*OperatorVerdict$|^OperatorVerdict$` (or equivalent).
4. Class definitions (`ClassDef`) are NEVER flagged — visitor only inspects `Call` nodes.
5. The offender list contains only files with **direct constructor calls** to OperatorVerdict subclasses outside the allowed-list.

### AC-2 — Glob-based filename exclusion (handles 14+ variant files)

**When** the AUDIT runs:
**Then** the filename exclusion is generalized:
1. From: `if path.name == "operator_verdict.py": continue` (singular).
2. To: `if fnmatch.fnmatch(path.name, "operator_verdict*.py"): continue` (or equivalent regex `re.match(r"^operator_verdict.*\.py$", path.name)`).
3. All 14+ variant files (`operator_verdict_section_02a.py`, `operator_verdict_section_06b.py`, etc.) are correctly excluded.
4. The 3 authorized bridge modules in the `allowed` set continue to be excluded.

### AC-3 — Test PASSES post-rewrite (no false positives)

**Then** running `pytest tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` PASSES:
1. No false-positive offender entries (no class definitions; no variant model files).
2. If a real unauthorized constructor call EXISTS in app/*.py outside the allowed-list, the test FAILS with a clear offender list (verify by spot-test: temporarily add `OperatorVerdict(...)` to a non-allowed app file; assert test fails; revert).

### AC-4 — Parametrized fixture cases for AST visitor (defense-in-depth)

**Then** the dev-agent adds parametrized fixture cases to verify the AST visitor's behavior:
1. Class definition pattern: `class Foo(OperatorVerdict): pass` → NOT flagged.
2. Direct constructor pattern: `Foo()` where `Foo` is `OperatorVerdict` subclass → flagged.
3. Class-definition pattern with subclass: `class Section02AOperatorVerdict(BaseModel): pass` → NOT flagged.
4. Constructor pattern at module-level: `verdict = Section02AOperatorVerdict(...)` outside allowed → flagged.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Read current `tests/integration/gates/test_resume_api_authority.py` (lines 17-30).
  - [ ] T1.2 Read A19 anti-pattern at `docs/dev-guide/specialist-anti-patterns.md` for remediation contract.
  - [ ] T1.3 Verify `app/models/operator_verdict_section_*.py` count (expected: 14+ variants).
  - [ ] T1.4 Refresh broad-regression baseline.

- [ ] **T2 — Rewrite scanner with AST + glob exclusion (AC-1 + AC-2)**
  - [ ] T2.1 Author `_OperatorVerdictCallVisitor(ast.NodeVisitor)` class.
  - [ ] T2.2 Replace substring scan loop with `ast.parse(text)` + `_OperatorVerdictCallVisitor().visit(tree)`.
  - [ ] T2.3 Replace singular filename exclusion with glob/regex.

- [ ] **T3 — Add parametrized fixture cases (AC-4)**
  - [ ] T3.1 Use `pytest.mark.parametrize` with synthetic Python source code samples covering AC-4 cases (a)-(d).

- [ ] **T4 — Verification battery (R-tier R2; T11-tier lite)**
  - [ ] T4.1 Focused: `pytest tests/integration/gates/test_resume_api_authority.py -p no:randomly -q --tb=short` PASS.
  - [ ] T4.2 Spot-test: temporarily add `Section02AOperatorVerdict(...)` to non-allowed app file → assert test FAILS; revert.
  - [ ] T4.3 Smoke 181/18 UNCHANGED.
  - [ ] T4.4 R2 broad: failure count delta improves by 1 (the inherited `test_no_unauthorized_callers` failure flips PASS).
  - [ ] T4.5 Class-conformance UNCHANGED at 19.
  - [ ] T4.6 Lint-imports 12 KEPT UNCHANGED.
  - [ ] T4.7 Sandbox-AC PASS.
  - [ ] T4.8 Ruff clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-housekeeping-2.ready-for-review.md` with: AST visitor implementation evidence + parametrized cases + spot-test fail-then-pass evidence + before-and-after broad-regression delta showing the inherited failure flipping to PASS.

---

## Required Readings (T1)

1. This story spec.
2. `docs/dev-guide/specialist-anti-patterns.md::A19. Class-definition substring scanners go stale when class names change` (D12-2 remediation contract; landed at 7c.21).
3. `tests/integration/gates/test_resume_api_authority.py` (current substring-scan implementation).
4. `_bmad-output/implementation-artifacts/7c-13-code-review-2026-05-06.md` + `7c-14-code-review-2026-05-06.md` (origin — DISMISSED-as-PRE-EXISTING reviews).
5. Python `ast` module docs (Python stdlib — `ast.NodeVisitor`, `ast.Call`, `ast.parse`, `ast.ClassDef`).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. Solo dispatch.

---

## Closeout impact

When this story closes, the inherited `test_no_unauthorized_callers` failure flips PASS, **reducing broad-regression failure count by 1**. This is the long-standing "scanner-staleness" entry that's been DISMISSED across multiple Slab 7c verdicts (7c.9/10/11/12/13/14/20b). Its closure is a small but visible cleanup signal.
