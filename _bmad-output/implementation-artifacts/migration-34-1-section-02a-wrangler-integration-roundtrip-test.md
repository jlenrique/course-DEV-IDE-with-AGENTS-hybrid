# Migration Story 34-1: §02A → Texas Wrangler Subprocess Integration Round-Trip Test (Quinn-synthesis Option 5 ratchet ship-proof)

**Status:** ready-for-dev *(spec authored 2026-05-22 with locked contract decisions D1-D8 per Round-1 SCP-ratification party-mode 4-of-4 APPROVE-with-amendments; predecessor C1 substrate amendment CLOSED at commit `3159a0e`. Awaiting Codex T1-T9 dispatch + T10 self-review + Claude T11 cross-agent `bmad-code-review`.)*
**Sprint key:** `migration-34-1-section-02a-wrangler-integration-roundtrip-test`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence ([`epics-section-02a-downstream-coherence.md`](../planning-artifacts/epics-section-02a-downstream-coherence.md))
**Pts:** 5
**Gate:** **dual-gate** + **cross-agent code-review MANDATORY** (per Epic 34 §Story 34-1 R-tier R2 + Murat M-Murat-1 binding: real subprocess + real fixture + forensic-anchor assertion; load-bearing integration ratchet for all 6 downstream stories)
**K-target:** ~1.5× (5 pts; bounded surface = 1 new integration test + 1 new temporary translator scaffold + 1 fixture-copy of Trial-3 attempt-2 forensic directive + optional fixture-corpus subset)
**R-tier (regression scope):** **R2** — substrate-touching (new translator file in `app/`; new test surface). Full broad regression run at T9 per dual-gate discipline.
**T11-tier (review approach):** **cross-agent** — MANDATORY full-fresh-context Blind/Edge/Auditor per Murat M-Murat-1 binding (mock-surface audit is the load-bearing review item).
**Files touched (declared at spec-author time):**

**New (~6 files):**
- `app/composers/section_02a/_wrangler_translator.py` (NEW; temporary in-tree translator scaffolding with `__epic_34_scaffolding__ = True` module-level constant + `# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING` docstring marker per AC-34-1-C; deleted at Story 34-7 per NFR-E34-10 + AC-34-7-A/B)
- `tests/integration/__init__.py` (NEW; package marker IF doesn't exist — Codex T1 check)
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (NEW; AC-34-1-A through AC-34-1-E test pin; the load-bearing integration ratchet)
- `tests/fixtures/integration/__init__.py` (NEW; package marker; defensive per Murat seam allowlisted at C1)
- `tests/fixtures/integration/section_02a/__init__.py` (NEW; package marker; defensive per Murat seam allowlisted at C1)
- `tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml` (NEW; copy of Trial-3 attempt-2 forensic directive at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml`; sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; the AC-34-1-B assertion target)

**Modified (1 file; optional T8 if K-budget tight; surface decision_needed if blocked):**
- `tests/fixtures/integration/section_02a/conftest.py` (NEW IF needed for fixture-loading; only if Codex T1-T9 needs fixtures via `pytest` fixture-injection — otherwise direct file-path read in the test is sufficient)

**Do NOT modify in this story:**
- `app/composers/section_02a/composer.py` — Story 34-3 surface; READ ONLY at T1
- `app/composers/section_02a/directive_model.py` — Story 34-3 surface; READ ONLY at T1
- `app/composers/section_02a/cli_adapter.py` — already wired post SCP-2026-05-21; READ ONLY at T1
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — Story 34-2 + 34-4 surface; READ ONLY at T1 (subprocess invocation only)
- §02A composer 12-test suite — Story 34-3 surface; READ ONLY at T1

**Lookahead tier:** **2** (R2 substrate-touching; spec authored at C1 close).
**Authored:** 2026-05-22 via `bmad-create-story`-equivalent direct-Claude authoring under NEW CYCLE single-Codex pattern per CLAUDE.md §Cleanup-arc execution mode.
**Wave:** 1 — slot 1 (FIRST story in Epic 34 per Quinn-synthesis Option 5 binding: integration test FIRST, RED→GREEN via temporary translator, then substrate harmonization).

**FR coverage:**
- **NFR-E34-1** Integration-coverage tests MANDATORY per story — NOT unit tests with mocks. This story IS the integration coverage gate; downstream stories 34-2..34-7 inherit the ratchet.
- **NFR-E34-7** Round-trip integration test MUST assert against the actual Trial-3 attempt-2 forensic directive (sha256 `351a57f...`). AC-34-1-B owns this assertion.
- **NFR-E34-10** Temporary in-tree translator MUST carry delete-at-Epic-close hard AC (Story 34-7 AC-34-7-A/B + AC-34-7-H grep-sweep). AC-34-1-C owns the scaffold creation; story 34-7 owns the deletion.
- **Story 34-1 ratchet stay-green is BINDING abort trigger** (per Round-1 Murat tightening, folded into SCP §5).

**NFR coverage:**
- **NFR-E34-2** Pydantic-v2 closed-enum discipline preserved (Directive model not modified here; translator is non-Pydantic Python module).
- **NFR-E34-3** Pydantic-v2 hygiene preserved (no model modifications in this story).
- **NFR-E34-6** UUID4-tz-aware preserved (no UUID-handling changes in this story).
- **NFR-E34-8** TW-7c-4 freeze-safety preserved — Story 34-1's path additions are pre-allowlisted at C1 commit `3159a0e`.
- **NFR-E34-11** NEW CYCLE single-Codex discipline (Claude pre-author this spec; Codex T1-T9 + T10 self-review; Claude T11 cross-agent review).
- **NFR-E34-12** Sandbox-AC discipline — dev-agent ACs (AC-34-1-A through E) use shipped Python deps + subprocess; live-LLM evidence (AC-34-1-F) operator-gated.
- **NFR-E34-13** `python scripts/utilities/validate_migration_story_sandbox_acs.py <story-file>` MUST PASS at ready-for-dev finalization AND at `bmad-dev-story` open.

**Standing-guardrail enforcement:**
- SG-1 unchanged (integration test is dev-tooling, not specialist code).
- SG-2 unchanged.
- SG-3 unchanged.
- SG-4 unchanged.

**Tripwire ownership:**
- **TW-7c-4** Story 34-1 path additions ratified at C1 commit `3159a0e`; both dual-predicate assertions (L84 `app_scope == []` + L96 `unexpected == []`) PASS with the 27-path allowlist.
- **Anti-pattern A9 (vacuous test passes):** Story 34-1's `len(materials) >= 1` assertion before row-shape (AC-34-1-A; per Murat new-A9-surface-1 mitigation) is the defense.

**Implementation cycle (NEW CYCLE single-Codex):**
- **Claude (Opus 4.7):** authored this spec with locked contract decisions per Round-1 SCP-ratification 2026-05-22; sandbox-AC validator PASS expected at story-author close; governance JSON entry pending registration.
- **Codex (Sonnet 4.5 or later):** develops `_wrangler_translator.py` + integration test + fixture-copy per the locked contract decisions below; reaches `review` status; produces self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md`.
- **Claude T11 cross-agent review:** verifies Codex's implementation matches the locked contract (decisions NOT relitigated; only verification). Cross-agent review is MANDATORY per Murat M-Murat-1 binding (mock-surface audit is the load-bearing review item). Commits + flips `migration-34-1-section-02a-wrangler-integration-roundtrip-test: review → done`.

---

## Contract Negotiation Decisions (LOCKED 2026-05-22 per Round-1 SCP-ratification party-mode)

D1-D8 are LOCKED at spec-author time. Cross-agent T11 review verifies Codex's implementation matches; does NOT relitigate the contract. Any Codex deviation surfaces as HALT-AND-SURFACE for operator decision at T10 self-review.

**D1. Translator module path:** `app/composers/section_02a/_wrangler_translator.py` (underscore-prefixed = private; co-located with §02A composer package per Winston A1+A2 substrate-coherence; deleted at Story 34-7).

**D2. Translator scaffolding markers (BINDING per AC-34-1-C + AC-34-7-H grep-sweep):**

```python
"""Temporary in-tree translator scaffold for Epic 34 §02A → Texas wrangler boundary.

# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING

This module is BORN DEAD at Story 34-1 (integration test landing) and DIES at
Story 34-7 (translator deletion + A23/P5 anti-pattern entries + Epic 34 close).
See `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md`
NFR-E34-10 + AC-34-7-A/B/H for the deletion gate.

Do NOT import this module from any production runtime path EXCEPT via the
integration test at `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`.
The translator's job is to bridge §02A's `Directive` output schema to the Texas
wrangler's currently-stricter input schema while Stories 34-2/34-3/34-4 harmonize
the substrate one drift dimension at a time. Translator's TRANSLATOR_ACTIVE_MAPPINGS
shrinks monotonically across the Epic; Story 34-7 verifies it reaches frozenset()
empty before deleting the file.
"""

__epic_34_scaffolding__ = True  # AC-34-7-H grep-sweep target (post-Story-34-7 must return 0)
```

**D3. Translator API signature (D-shaped, intentionally minimal — easy to delete):**

```python
def translate_directive_for_wrangler(directive: Directive) -> dict[str, Any]:
    """Map §02A Directive → wrangler-acceptable plain dict at Story 34-1's substrate-snapshot.

    At Story 34-1's close (post-C1, pre-Story-34-2), the wrangler at
    `skills/bmad-agent-texas/scripts/run_wrangler.py` rejects:
      - `src_id` (wants `ref_id` per line 319)
      - `role=supporting` (wants `supplementary` per line 328-338)
      - `role=ignored` (no equivalent; would crash on validation)

    This function applies three mappings:
      1. `src_id` → `ref_id` (per-source field rename)
      2. `role=supporting` → `role=supplementary` (per-source role rename)
      3. Filter out rows with `role=ignored` (Trial-3 Tejal corpus has none;
         future corpora with `.gitkeep`/`.DS_Store` would have these)

    Each mapping is also entered in `TRANSLATOR_ACTIVE_MAPPINGS` so Story 34-5's
    sequence test can assert monotonic shrinkage as Stories 34-2/34-3 land.
    Returns a plain dict matching wrangler's `_load_directive` expected shape;
    caller dumps as YAML to disk.
    """
```

**D4. `TRANSLATOR_ACTIVE_MAPPINGS` constant (MUST be production-load-bearing per Murat new-A9-surface-2 + AC-34-5-A):**

```python
TRANSLATOR_ACTIVE_MAPPINGS: frozenset[str] = frozenset({
    "src-id-to-ref-id",           # Story 34-3 retires this (after wrangler keeps ref_id, §02A renames src_id → ref_id)
    "role-supporting-to-supplementary",  # Story 34-2 retires this (wrangler accepts `supporting` natively)
    "filter-ignored-rows",        # Story 34-2 retires this (wrangler handles `ignored` natively with excluded_reason)
})
```

**The constant MUST be READ by `translate_directive_for_wrangler` at runtime** (NOT just declared at module-top for test observability). Each mapping check inside the function MUST gate on membership in the frozenset. This makes the constant load-bearing in production, not just test-observable. Story 34-5's `AC-34-5-A` sibling-assertion verifies a grep-confirmation that the function reads the constant.

**D5. Integration test file location:** `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (in `tests/integration/`; NEW directory if `tests/integration/__init__.py` doesn't exist — verify at T1).

**D6. Integration test core flow (AC-34-1-A through AC-34-1-E):**

```python
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from app.composers.section_02a._wrangler_translator import (
    TRANSLATOR_ACTIVE_MAPPINGS,
    translate_directive_for_wrangler,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WRANGLER_SCRIPT = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
FORENSIC_DIRECTIVE_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "integration"
    / "section_02a"
    / "forensic_directive_trial_3_attempt_2.yaml"
)
FORENSIC_DIRECTIVE_SHA256 = (
    "351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703"
)

# AC-34-1-D mock-surface audit: this test MUST NOT mock:
#   - the wrangler subprocess (use real subprocess.run)
#   - the directive YAML write path (use real tmp_path/directive.yaml)
#   - the translator (use real translate_directive_for_wrangler call)
# This test MAY mock:
#   - the §02A composer's LLM call (Story 34-1's scope does NOT include LLM exercise;
#     fixture-replay via the forensic directive carries the real LLM-judged shape)
#   - any HTTP / external-service calls (none expected for this test)

def test_forensic_directive_round_trips_through_wrangler_subprocess_via_translator(tmp_path):
    """AC-34-1-B forensic-anchor assertion: the Trial-3 attempt-2 directive
    that crashed the wrangler (run-id 6a3393f8-...) MUST round-trip cleanly
    through the wrangler subprocess AFTER translation. This is the load-bearing
    proof that Epic 34's substrate harmonization closes the exact seam crash.
    """
    # Verify fixture exists + sha256 matches the forensic anchor.
    assert FORENSIC_DIRECTIVE_FIXTURE.exists(), (
        f"Forensic fixture missing at {FORENSIC_DIRECTIVE_FIXTURE}. "
        f"Copy from state/config/runs/6a3393f8-.../directive.yaml at C2 spec authoring."
    )
    import hashlib
    fixture_sha = hashlib.sha256(FORENSIC_DIRECTIVE_FIXTURE.read_bytes()).hexdigest()
    assert fixture_sha == FORENSIC_DIRECTIVE_SHA256, (
        f"Forensic fixture sha256 drift: expected {FORENSIC_DIRECTIVE_SHA256}, "
        f"got {fixture_sha}. Fixture must be a byte-identical copy of the Trial-3 "
        f"attempt-2 forensic anchor; re-copy if drift surfaced."
    )

    # Load the forensic directive into a §02A Directive instance via composer reload.
    # (The forensic fixture is YAML in §02A's `Directive` shape; load via Directive model.)
    from app.composers.section_02a.directive_model import Directive
    forensic_yaml_text = FORENSIC_DIRECTIVE_FIXTURE.read_text(encoding="utf-8")
    forensic_data = yaml.safe_load(forensic_yaml_text)
    directive = Directive.model_validate(forensic_data)

    # Translate to wrangler-acceptable shape.
    translated = translate_directive_for_wrangler(directive)

    # Write translated directive to disk for subprocess.
    directive_yaml_path = tmp_path / "directive.yaml"
    directive_yaml_path.write_text(
        yaml.safe_dump(translated, sort_keys=False),
        encoding="utf-8",
    )

    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()

    # Invoke wrangler as REAL subprocess (NOT in-process import).
    result = subprocess.run(
        [
            sys.executable,
            str(WRANGLER_SCRIPT),
            "--directive", str(directive_yaml_path),
            "--bundle-dir", str(bundle_dir),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    # AC-34-1-A assertion: wrangler exits 0.
    assert result.returncode == 0, (
        f"Wrangler exited with code {result.returncode}: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )

    # AC-34-1-A vacuous-pass mitigation: assert non-empty materials BEFORE row-shape.
    result_yaml = yaml.safe_load((bundle_dir / "result.yaml").read_text(encoding="utf-8"))
    assert "materials" in result_yaml, f"result.yaml missing 'materials' key: {result_yaml.keys()}"
    assert len(result_yaml["materials"]) >= 1, (
        f"result.yaml.materials is empty: {result_yaml['materials']!r}. "
        f"Trial-3 attempt-2 fixture has 11 sources; at least 1 primary expected post-translation."
    )

    # AC-34-1-A row-shape assertion: at least one primary row carries word_count + content_path.
    primary_rows = [m for m in result_yaml["materials"] if m.get("role") == "primary"]
    assert len(primary_rows) >= 1, f"No role=primary rows in materials: {result_yaml['materials']!r}"
    assert all("word_count" in row for row in primary_rows), "primary rows missing word_count"
    assert any(row.get("content_path") == "extracted.md" for row in primary_rows), (
        "no primary row has content_path=extracted.md"
    )

    # NOTE: metadata.json::sme_refs[] assertion DEFERRED to Story 34-4 AC-34-4-A-EXT.
    # The wrangler at Story 34-1 close writes only `{run_id, generated_at, provenance,
    # primary_consumption_path}` to metadata.json; sme_refs[] is Story 34-4's additive
    # emission. Story 34-4 will EXTEND this test to add the sme_refs assertion block
    # in lockstep with the new wrangler behavior — per Quinn-synthesis Option 5
    # per-story ratchet-extension pattern.


def test_translator_active_mappings_is_load_bearing_in_production():
    """AC-34-5-A precursor: at Story 34-1 close, all 3 mappings are active.
    Story 34-5's sequence test extends this with parametrized monotonic shrinkage.
    """
    expected_mappings = frozenset({
        "src-id-to-ref-id",
        "role-supporting-to-supplementary",
        "filter-ignored-rows",
    })
    assert TRANSLATOR_ACTIVE_MAPPINGS == expected_mappings, (
        f"Translator mappings drift: expected {expected_mappings}, got {TRANSLATOR_ACTIVE_MAPPINGS}"
    )
    # Verify the function reads the constant (grep-confirmation per AC-34-5-A binding).
    import inspect
    source = inspect.getsource(translate_directive_for_wrangler)
    assert "TRANSLATOR_ACTIVE_MAPPINGS" in source, (
        "translate_directive_for_wrangler does NOT reference TRANSLATOR_ACTIVE_MAPPINGS at runtime. "
        "Per Murat new-A9-surface-2 mitigation + AC-34-5-A, the constant MUST be production-load-bearing."
    )


def test_translator_module_carries_deletion_markers():
    """AC-34-1-C + AC-34-7-H prep: the scaffold markers MUST be present so the
    Story-34-7 grep-sweep correctly identifies the file as scaffolding-to-delete.
    """
    translator_path = (
        REPO_ROOT / "app" / "composers" / "section_02a" / "_wrangler_translator.py"
    )
    text = translator_path.read_text(encoding="utf-8")
    assert "__epic_34_scaffolding__ = True" in text, (
        "Translator missing __epic_34_scaffolding__ module-level marker per D2"
    )
    assert "DELETE-AT-EPIC-34-CLOSE" in text, (
        "Translator missing DELETE-AT-EPIC-34-CLOSE docstring marker per D2"
    )
```

**D7. Forensic fixture copy mechanism (BINDING per AC-34-1-B):**

The Trial-3 attempt-2 forensic directive at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml` is gitignored. **Codex T2 MUST copy this file** to `tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml` so the fixture lands in the test surface (allowlisted at C1 via fixture-dir defensive entries; per Murat seam analysis, `.yaml` fixtures escape the `*.py`-scoped predicate, so the YAML fixture itself is NOT in `PERMITTED_PYTHON_DIFFS` — it's a regular tracked file).

Copy command (Codex T2):
```bash
cp state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml \
   tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml
```

OR PowerShell:
```powershell
Copy-Item state\config\runs\6a3393f8-f369-4a30-b7c1-b50c60c1d1a2\directive.yaml `
          tests\fixtures\integration\section_02a\forensic_directive_trial_3_attempt_2.yaml
```

Verify byte-identical via sha256 (test asserts this dynamically per D6).

**HALT-AND-SURFACE condition (T2):** if the forensic fixture path does not exist (operator may have cleaned it up between session-close and Codex dispatch), Codex SHALL NOT proceed with the test as authored. Surface `decision_needed` for operator: (a) re-launch Trial-3 attempt-2 to regenerate the fixture; (b) use a synthetic-equivalent directive (loses forensic-anchor proof); (c) defer Story 34-1 close until fixture is reconstructable.

**D8. Sandbox-AC split (binding per CLAUDE.md §LangChain/LangGraph migration sandbox-AC + gate-mode governance):**

AC-34-1-A through AC-34-1-E are **dev-agent verifiable** (shipped Python deps: `pytest`, `subprocess`, `yaml`, `hashlib`; no live LLM call; fixture-replay only).

AC-34-1-F is **operator-gated**:
- Operator runs the live-LLM variant of Story 34-1 against the real Tejal corpus (`course-content/courses/tejal-apc-c1-m1-p2-trends/`) to confirm the full §02A composer → wrangler chain works against real LLM-judged output (not just the fixture).
- Operator pastes the live-LLM evidence block into Completion Notes per CLAUDE.md.
- Dev-agent SHALL NOT exercise live LLM (no `OPENAI_API_KEY` exercise in dev-agent ACs).

`scripts/utilities/validate_migration_story_sandbox_acs.py` will inspect the AC block at ready-for-dev finalization and verify the split is honored.

---

## Task chain T1-T11

**T1 readiness check (Codex):**
- Read this spec FULLY.
- Read [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) — touches `app/composers/section_02a/` per Epic 33 Standing Regime; verify regime applicability.
- Read [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — translator is NOT Pydantic but the test reuses §02A's Pydantic `Directive` model; understand the 14 idioms it MUST conform to.
- Read [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md) — A11 Windows-portability + A9 vacuous-test passes.
- Read [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) — confirm `subprocess` invocations of `run_wrangler.py` are in the `dev_agent_available` set (they are: shipped Python via `sys.executable`).
- Verify forensic fixture exists at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml`; if absent, HALT-AND-SURFACE per D7.
- Verify wrangler exists at `skills/bmad-agent-texas/scripts/run_wrangler.py`; verify it's runnable via `python -m skills.bmad-agent-texas.scripts.run_wrangler --help` (use direct path; the wrangler may not be importable as a module if its dir isn't on sys.path).

**T2 fixture copy:**
- Create `tests/fixtures/integration/section_02a/` dir if not exists.
- Copy forensic directive per D7 mechanism.
- Verify sha256 matches `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`.

**T3 translator scaffold author:**
- Create `app/composers/section_02a/_wrangler_translator.py` per D1/D2/D3/D4 contract.
- Pre-commit will run ruff on this file — `# noqa: E501` or similar if line-length nits surface (don't fight the linter on a scaffold).
- Confirm `__epic_34_scaffolding__ = True` and `DELETE-AT-EPIC-34-CLOSE` are present in the file (test D2 verifies this).

**T4 integration test author:**
- Create `tests/integration/__init__.py` if not exists (package marker).
- Create `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` per D6 (use the template; adapt as needed for Codex's actual implementation details).
- Test MUST exercise the real subprocess; mock-surface limited to LLM call (which the fixture-replay obviates).

**T5 ruff + lint-imports:**
- `.venv/Scripts/python.exe -m ruff check tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py app/composers/section_02a/_wrangler_translator.py`
- Expect 0 violations. If linter flags anything in the scaffold, document inline why it's acceptable (scaffold-shaped exceptions OK; production-shaped fixes preferred).
- `.venv/Scripts/python.exe -m lint_imports` — expect KEPT count unchanged (no new import-linter contracts; `_wrangler_translator.py` lives inside §02A package so existing C1-C6 contracts cover it).

**T6 focused suite run:**
- `.venv/Scripts/python.exe -m pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v`
- Expect 3 tests PASS (or whatever count Codex implements per D6 template).
- §02A 12-test composer suite + M-A1 4-test wiring-contract suite stay GREEN unchanged.

**T7 broad regression sweep:**
- `.venv/Scripts/python.exe -m pytest --tb=no -q | tail -5` (or equivalent)
- Compare against 88-baseline at `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md`.
- Per SCP §5 abort tripwire: delta MUST be ≤ +10 OR no new failure IDs outside the 88 baseline.

**T8 (optional; defer if K-budget tight):** docs update — file a one-line cross-reference in `docs/dev-guide/specialist-anti-patterns.md` or `docs/dev-guide/dev-agent-anti-patterns.md` noting Story 34-1 as the first integration-boundary green test for §02A→wrangler chain. Lower priority; surface decision_needed if blocked.

**T9 self-conducted G6 layered review:**
- Codex authors a layered Blind/Edge/Auditor review at `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` per Murat M-Murat-1 binding (mock-surface audit is the load-bearing review item).
- Mock-surface audit MUST enumerate every mock used in the test + the rationale per mock per AC-34-1-D pattern.

**T10 ready-for-review handoff:**
- Codex flips Story 34-1 to `review` status in `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- Codex writes handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` summarizing implementation + T9 review + any deviation surfaces.

**T11 Claude cross-agent review:**
- Claude reviews FULL diff in fresh context per Murat M-Murat-1 binding.
- Verifies contract D1-D8 compliance (NOT renegotiates).
- Verifies mock-surface audit + AC-34-1-D enumeration is faithful.
- Verifies forensic-anchor assertion (AC-34-1-B) is byte-identical sha256 match.
- Verifies `__epic_34_scaffolding__` markers present per D2.
- Verifies AC-34-1-A vacuous-pass mitigation (`len(materials) >= 1` before row-shape).
- Verifies TRANSLATOR_ACTIVE_MAPPINGS is grep-readable in the production function per AC-34-5-A precursor.
- On PASS: commits + flips Story 34-1 done.
- On FAIL: surfaces deviation per Murat code-review dissent clause; story stays `review`; Codex re-iterates.

---

## Acceptance Criteria (carryforward from Epic 34 spec; amendments folded from Round-1 SCP-ratification)

**AC-34-1-A** (test landing — Story-34-1-substrate-only assertions; AMENDED 2026-05-22 post-Codex-T1-surface):
**Given** the §02A composer produces directives via `app/composers/section_02a/composer.compose()` and the Texas wrangler validates input via `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 280-394
**When** I author `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`
**Then** the test composes a §02A `Directive` via the actual composer entry point (LLM call mocked with deterministic fixture corpus is acceptable; the composer-to-wrangler boundary MUST be real),
**And** writes the directive YAML to a real `tmp_path/directive.yaml`,
**And** invokes `run_wrangler.py` as a REAL subprocess (NOT in-process import),
**And** asserts `result.returncode == 0`,
**And** asserts `len(result.yaml::materials) >= 1` BEFORE asserting per-row shape (Murat new-A9-surface mitigation: prevents vacuous-pass on empty-materials case),
**And** asserts at least one row with `role=primary` carrying `word_count` + `content_path` exists in `result.yaml::materials[]`.

**Scope discipline (post-Codex-T1-surface amendment 2026-05-22):** Story 34-1 SHALL NOT assert `metadata.json::sme_refs[]` shape — Story 34-4 owns the wrangler's metadata.json sme_refs[] emission. Story 34-1's translator only translates directive INPUT shape, not wrangler OUTPUT shape; the wrangler still writes only `{run_id, generated_at, provenance, primary_consumption_path}` to metadata.json at Story 34-1 close. The sme_refs forward-contract assertion is RELOCATED to Story 34-4 AC-34-4-A-EXT (Story 34-4 EXTENDS this round-trip test to add the sme_refs assertion block when sme_refs becomes real). This honors Quinn-synthesis Option 5's "one drift dimension per story" sequencing and per-story ratchet-extension pattern.

**AC-34-1-B** (forensic-anchor assertion — Murat M-Murat-5):
**Given** the Trial-3 attempt-2 forensic directive at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml` (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; gitignored — fixture-copy MUST land under `tests/fixtures/integration/section_02a/`)
**When** the same round-trip test feeds this exact forensic directive to the wrangler subprocess
**Then** the test asserts `result.returncode == 0` (proving the exact seam crash that triggered this Epic is closed by translator + harmonization).

**AC-34-1-C** (temporary translator scaffolding):
**Given** Story 34-2/34-3/34-4 substrate harmonization has not yet landed
**When** the test runs at Story 34-1 close
**Then** a temporary in-tree translator at `app/composers/section_02a/_wrangler_translator.py` (NEW file) maps §02A's `Directive` output → wrangler-acceptable shape (renames `src_id` → `ref_id`; maps `supporting` → `supplementary`; filters out `ignored` rows),
**And** the translator carries a top-of-file docstring marker `# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING` plus a `__epic_34_scaffolding__ = True` module-level constant for grep-based deletion verification per Story 34-7 AC-34-7-H,
**And** the round-trip test imports + invokes the translator at directive-write time.

**AC-34-1-D** (mock-surface audit — M-Murat-4 equivalent):
**Given** the LLM call inside the §02A composer is mocked via fixture-replay in this integration test
**When** the test is reviewed at Claude T11 `bmad-code-review` step on Story 34-1
**Then** every mock the test uses MUST be listed in test docstring with the rationale "this mock does NOT bypass the §02A → wrangler boundary; only the upstream LLM call is bounded for determinism."

**AC-34-1-E** (verification):
**Given** Story 34-1 close
**When** the operator runs `.\.venv\Scripts\python.exe -m pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v`
**Then** all assertions pass; exit 0; test reports >=3 assertion lines (one for AC-A round-trip; one for AC-B forensic-anchor; one for AC-C translator-invocation).

**AC-34-1-F** (sandbox-AC governance — operator-gated, separate AC block per CLAUDE.md sandbox-AC discipline):
**Given** AC-A through AC-E are dev-agent verifiable
**When** operator runs the live-LLM variant of Story 34-1 against the real Tejal corpus
**Then** operator pastes the live-LLM evidence block into Completion Notes per CLAUDE.md §LangChain/LangGraph migration sandbox-AC discipline. (Dev-agent does NOT exercise live LLM; only the LLM-mocked path is dev-agent ACed.)

---

## Cross-references

- Epic 34 spec: [`_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md`](../planning-artifacts/epics-section-02a-downstream-coherence.md) §Story 34-1
- Phase A probe (drift inventory): [`_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md`](../planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md)
- Phase B consensus (Quinn synthesis Option 5): [`_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md`](../planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md)
- Substrate amendment SCP (C1 ratified + executed at `3159a0e`): [`_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md`](../planning-artifacts/sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md)
- Parent SCP (§02A wiring; established `compose()` is invoked at G0): [`_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md`](../planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md)
- Codex dev-prompt for this story: [`codex-dev-prompt-34-1-section-02a-wrangler-integration-roundtrip-test.md`](codex-dev-prompt-34-1-section-02a-wrangler-integration-roundtrip-test.md)
