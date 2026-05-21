# Migration Story 2b.16: Scaffold-Conformance Framework Hardening + Per-Specialist Test Generation

**Status:** done
**Sprint key:** `migration-2b-16-scaffold-conformance-framework-hardening-scaffold-migration`
**Epic:** Slab 2b â€” sixteenth story; SECOND cross-cutting (after 2b.15); per epic 2b.16.
**Pts:** 3 | **Gate:** single (governance JSON `2b-16.expected_gate_mode = "single-gate"`). **K-target:** ~1.3Ã— (target 14 / floor 11; framework-hardening + per-specialist auto-discovery).

**Lean batched party-mode amendments applied 2026-04-25 (Murat + Amelia, batched with 2b.17):**
- **Murat 2b.16-R1 (NIT):** AC-A test-pin language adds "(K-floor counts the parametrize *function*, not parametrized cases â€” per M-R18)" to prevent dev-agent confusion at T8 K-band justification.
- **Murat 2b.16-R2 (BINDING â€” FR14 enforcement):** Add positive-regression test in `test_framework_auto_discovery.py` that *generates* a throwaway specialist via 2a.5-hardened generator (under tmp_path with cleanup) and asserts framework picks it up with ZERO framework-file diff (`git diff --quiet tests/integration/scaffold_conformance/scaffold_contract.py` semantically). Without this, "ZERO framework changes" is prose, not verified invariant.
- **Amelia A-2b.16-R1:** AC-A spec text PINS iteration mechanism: `Path("app/specialists").iterdir()` + filter `is_dir() and not name.startswith(("_", "."))`. Prevents `pkgutil.walk_packages` / `importlib.resources` accidental drift.
- **Amelia A-2b.16-R2:** AC-B retirement count: replace "16+" with "17 (3 from Slab 2a + 14 from 2b.1-2b.14)" for grep-clarity.

Extends scaffold-conformance framework from Story 1.7 to **auto-discover all `app/specialists/*/` directories** and parametrize the 14 conformance rules (FR14 assertions) over every non-`_scaffold` specialist. Eliminates per-specialist conformance test files (`test_scaffold_<specialist>.py`) from 2b.1-2b.14 + 2a.2-2a.4 â€” replaces with single parametrized framework test that picks up new specialists with ZERO framework changes (FR14 architecturally enforced).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.15. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” 2b.16-specific deltas:**
- **C** Reference patterns: Story 1.7 scaffold-conformance framework at `tests/integration/scaffold_conformance/scaffold_contract.py` + per-specialist test files `test_scaffold_{irene,kira,texas,gary,...,irene_pass_1}.py`.
- **F** `pyproject.toml` C3 contains 18 rows post-2b.15 close. 2b.16 does NOT change C3.
- **G** FR54 N/A.
- **R2 importlib loader status:** UNCHANGED.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** No new drifts at 2b.16 (cross-cutting framework).

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** framework-hardening + parametrize-collapse of per-specialist conformance tests.
- **R13 N/A:** cross-cutting.
- **R14 N/A:** cross-cutting.

---

## Story

As a **dev agent ensuring zero-drift on the 9-node scaffold across 14 specialists post-Slab-2b**,
I want **the conformance framework extended to auto-discover all `app/specialists/*/` directories and parametrize the 14 conformance rules + retire per-specialist conformance test files**,
So that **adding a specialist requires NO framework changes (FR14 architecturally enforced) and the test surface stays bounded as the specialist roster grows in Slab 3+**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. NO `@pytest.mark.llm_live` tests.

### AC-2b.16-A â€” Auto-discovery framework

- **Given** `tests/integration/scaffold_conformance/scaffold_contract.py` carries the 14 conformance rules from 1.7.
- **When** the dev agent extends framework to auto-discover all `app/specialists/*/` directories (excluding `_scaffold` reference but treating it as conformant per AC-3).
- **Then** `pytest tests/integration/scaffold_conformance/` runs the 14 rules against EVERY discovered specialist via `pytest.mark.parametrize`. A fresh generated specialist appears in the test sweep with ZERO framework changes (FR14 architecturally enforced).

**Test pin:** 1 parametrized function Ã— N specialist cases = 1 K-floor unit (per Murat M-R18 collapse). Plus 1 framework-self-test asserting auto-discovery picks up `_scaffold` + all migrated specialists.

### AC-2b.16-B â€” Per-specialist conformance test files RETIRED

For each existing per-specialist test file (`test_scaffold_irene.py / kira.py / texas.py / gary.py / vera.py / quinn_r.py / desmond.py / tracy.py / cd.py / enrique.py / wanda.py / kim.py / vyx.py / aria.py / mira.py / tamara.py` + `irene_pass_1` integration), DELETE the file (functionality absorbed by parametrize at AC-A).

### AC-2b.16-C â€” Sanctum/symlink rule with specific error

Per epic 2b.16 second AC: scaffold-conformance finds a specialist missing `sanctum/` symlink â†’ test fails with specific error naming missing file + FR14 rule violated. (Note: hybrid uses BMB direct-dir convention, NOT symlink; rule adapted to "missing BMB sanctum directory at `_bmad/memory/bmad-agent-<skill>/`.")

**Test pin:** 1 negative test asserting clear error message on synthetic missing-sanctum case.

### AC-2b.16-D â€” `_scaffold/` reference treated as specialist for self-consistency

Per epic 2b.16 third AC. **Test pin:** 1 test asserts `_scaffold/` passes the same conformance rules as migrated specialists.

### AC-2b.16-E â€” TEMPLATE compliance (per R1â€“R14 v2.3)

R1â€“R14 v2.3 honored where applicable.

### AC-2b.16-F â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; FR14 architecturally enforced via auto-discovery; per-specialist test count drops by 16+ (one per specialist) but coverage UNCHANGED via parametrize.
2. **Anti-pattern harvest:** N/A (no new drifts).
3. **Migration-guide update:** Â§12.14 Verification commands (post-2b.9 cascade) updated to point at single parametrized framework test instead of per-specialist test files.
4. **TEMPLATE compliance:** R1â€“R14 v2.3 honored. Framework-hardening lands cleanly.

### AC-2b.16-G â€” Sprint-status state-flips at filing AND at close

At filing: ready-for-dev. At close: done.

---

## File Structure Requirements

### MODIFIED files

- `tests/integration/scaffold_conformance/scaffold_contract.py` â€” extend with auto-discovery + parametrize machinery.
- `tests/integration/scaffold_conformance/test_scaffold_*.py` (16+ files) â€” DELETE; functionality absorbed by parametrize.
- `docs/dev-guide/langgraph-migration-guide.md` Â§12.14 (Verification commands post-2b.9 cascade) â€” update.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.

### NEW files

- `tests/integration/scaffold_conformance/test_framework_auto_discovery.py` â€” 3 tests: parametrized conformance + auto-discovery sweep + missing-sanctum error.

---

## Testing Requirements

**K-target ~1.3Ã— (target 14 / floor 11).** Test count: 1 parametrized function Ã— N specialist cases (collapses to 1 K-floor unit) + 1 framework-self-test + 1 missing-sanctum negative + 1 _scaffold self-consistency = **4 K-floor units / N+3 collected**. Coverage UNCHANGED from per-specialist files (just parametrized).

**Regression target at T8:** â‰¥352 passed / â‰¥10 skipped placeholder-key (small net +2 over 2b.15 close due to framework tests + minus 16 retired per-specialist conformance files).

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


## Closure Notes (Dev)
- Replaced per-specialist conformance files with auto-discovery framework tests using Path('app/specialists').iterdir() directory filter.
- Added positive regression for zero framework changes when adding a specialist directory.
- Retired legacy per-specialist conformance test files.

### T8 Evidence
- pytest (owned scopes): PASS
- ruff check (owned scopes): PASS
- lint-imports: PASS

