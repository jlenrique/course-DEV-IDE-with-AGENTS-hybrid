# Codex dev-story prompt — 7c-housekeeping-2 (scanner staleness AST-rewrite; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-housekeeping-2.ready-for-review.md` → Claude T11 lite → commit + flip done.

---

```
Run bmad-dev-story on Story 7c-housekeeping-2 (scanner staleness AST-rewrite).

Spec: `_bmad-output/implementation-artifacts/migration-7c-housekeeping-2-scanner-staleness-rewrite.md`.

## Required reading

1. Story spec (4 ACs A-D).
2. `docs/dev-guide/specialist-anti-patterns.md::A19` (D12-2 remediation contract; landed at 7c.21).
3. `tests/integration/gates/test_resume_api_authority.py` (current substring scanner; READ + REWRITE in place).
4. Python stdlib `ast` module docs.

## T1 hard checkpoints

- A19 anti-pattern entry exists in specialist-anti-patterns.md.
- 14+ `app/models/operator_verdict_section_*.py` files present.
- Broad-regression baseline includes the inherited `test_no_unauthorized_callers` failure (will flip PASS post-rewrite).

## Files in scope

**New (0 files)**.

**Modified (1 file):**
- `tests/integration/gates/test_resume_api_authority.py` — REWRITE `test_no_unauthorized_callers` with AST visitor + glob filename exclusion. Preserve `test_authorized_bridges_call_resume_api` unchanged.

**Do NOT modify:**
- Any production code under `app/` (this is test-hardening only)
- The 3 authorized bridge modules
- The 14+ OperatorVerdict variant files

## Critical implementation notes

- **AST visitor**: subclass `ast.NodeVisitor` with `visit_Call` method. Inside, check `node.func` for `ast.Name` with `id` matching `OperatorVerdict` or `Section*OperatorVerdict` patterns. Optionally also handle `ast.Attribute` for fully-qualified call paths.
- **Glob exclusion**: `import fnmatch; if fnmatch.fnmatch(path.name, "operator_verdict*.py"): continue`. Or use `re.match(r"^operator_verdict.*\.py$", path.name)`.
- **Allowed-list preserved**: keep the 3 authorized bridge module exclusions unchanged.
- **Parametrized fixtures**: use `pytest.mark.parametrize` with inline Python source samples; parse each via `ast.parse`; assert visitor classification matches expected.
- **Spot-test**: at T4.2, manually add a synthetic `Section02AOperatorVerdict(...)` call to a non-allowed app file (e.g., a temp file under `app/`); assert test FAILS with the path in offenders; revert. Document in dropbox.
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~150 LOC.
- **T11 lite tier**: pure test rewrite; no app changes.

## Verification battery (T4)

```bash
.venv/Scripts/python.exe -m pytest tests/integration/gates/test_resume_api_authority.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-housekeeping-2-scanner-staleness-rewrite.md
.venv/Scripts/python.exe -m ruff check tests/integration/gates/test_resume_api_authority.py
```

## T10

T10: dropbox at `_codex-handoff/7c-housekeeping-2.ready-for-review.md`. Include: AST visitor implementation evidence + parametrized cases + spot-test fail-then-pass evidence + before/after broad-regression delta (-1 expected as the inherited scanner-staleness failure flips PASS).

## Boundary

HALT on: parametrized cases not covering AC-4 (a)-(d); spot-test (manual offender add) does NOT trigger fail; broad-regression delta NOT improved by ≥1 post-rewrite; class-conformance count change.

DO NOT introduce: changes to production code under `app/`; new test files outside `tests/integration/gates/`; new dependencies (use Python stdlib only — `ast`, `fnmatch`/`re`).
```

---

## Operator dispatch checklist

1. ☐ AMELIA-P2 PASS.
2. ☐ Sandbox-AC PASS.
3. ☐ Sprint-status: ready-for-dev.
4. ☐ Dispatch (solo; eliminates long-standing scanner-staleness DISMISS thread).
