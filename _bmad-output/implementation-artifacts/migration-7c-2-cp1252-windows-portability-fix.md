# Migration Story 7c.2: cp1252 Windows-Portability Fix + Fixture-Comparison Utility

**Status:** ready-for-dev
**Sprint key:** `migration-7c-2-cp1252-windows-portability-fix`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 1
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-slab7c-thirty-six-stories, story 7c-2; rationale: null — cp1252 fix is below the spec layer; no schema-shape, lane-boundary, or invariant-preservation surface)
**K-target:** ~1.2× (small fix-tier band; ~1-2 pts; bounded surface = `app/marcus/cli/trial.py` print path + UTF-8 explicit-encoding everywhere directive bytes flow + 1 fixture-comparison utility module + 1 NNBSP regression test + anti-pattern A11 augmentation)
**Authored:** 2026-05-04 via `bmad-create-story` workflow (parallel with Codex 7c.0a dev round; AMELIA-P1 path-isolation guard active).
**Wave:** 1 — slot 1 (**opens parallel to 7c.0a + 7c.0b** per John A2; AMELIA-P1 path-isolation guard explicitly forbids touching 7c.0a/0b deliverable paths to prevent merge conflict).

**FR coverage:** FR-7c-5 (UTF-8 round-trip across §02A directive lifecycle: compose → write → print → operator review → edit → re-validate → submit, without Windows cp1252 codepage corruption on macOS-screenshot Unicode U+202F NNBSP and similar non-ASCII characters).

**NFR coverage:** NFR-7c-X1 (Windows-portability — every Slab 7c file UTF-8-encoded; CI lint pass enforces UTF-8 round-trip per FR-7c-46), NFR-7c-X3 (path-portability — `pathlib.Path.as_posix()` patterns), NFR-7c-M5 (sandbox-AC validator PASS).

**Tripwire ownership:** **TW-7c-2** detection (cp1252 regression — fires high severity if §02A composer regression test fails Trial-2 finding #1 byte-equivalence preservation OR if cp1252 fixture-comparison utility reports byte-divergence) + **TW-7c-5 partial** (cp1252 encoding regression — TW-7c-5's full FR-7c-46 UTF-8 CI lint pass scaffold lives in 7c.0b; 7c.2 contributes the cp1252-specific fixture-comparison utility that 7c.0b's lint pass invokes).

**Standing-guardrail enforcement:**
- SG-1 unchanged (no specialist-roster change).
- SG-2 unchanged (no mapping-checklist row change directly; §02A row status improves indirectly when 7c.3a closes).
- SG-3 Composition Spec invariants UNAFFECTED — cp1252 fix is below the spec layer.
- SG-4 unchanged (no sanctum-alignment change).

**Implementation cycle (NEW CYCLE per memory entry `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 lookahead-discipline revision):**
- **Claude (Opus 4.7):** authored this spec; sandbox-AC validator PASS confirmed at finalize; governance JSON entry verified (single-gate; no cross_agent_review_required); pre-authors `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-2-cp1252-windows-portability-fix.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops the fix + fixture-comparison utility + NNBSP regression test + A11 anti-pattern augmentation per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-2.ready-for-review.md`.
- **Claude:** does the FINAL `bmad-code-review` (T11 — single-gate; cross-agent NOT mandatory but Claude review remains mandatory per BMAD sprint governance §3); applies remediation cycles; commits; flips `migration-7c-2-cp1252-windows-portability-fix` review → done in sprint-status.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/dev-agent-anti-patterns.md` — **A11 Windows-portability** anti-pattern catalog. 7c.2 augments this catalog with a Slab 7c §02A worked example.
- `docs/dev-guide/story-cycle-efficiency.md` — K-floor discipline (target 1.2-1.5× K, not 5×); single-gate review policy.
- `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` — Trial-2 finding #1 forensic detail (run `d44128e9-4e17-4452-a535-989e826cd7da`; crash at `app/marcus/cli/trial.py:132`).
- `_bmad-output/planning-artifacts/deferred-inventory.md` (`trial-2-finding-1-cp1252-crash` entry) — recommended fix paths: `sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b'\n')` OR `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` once at module import.
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-5 (UTF-8 round-trip) + TW-7c-2 firing rule + Trial-2 finding #1 closure precondition.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.2 section starting at line 446).

**Predecessor state (verified at authoring 2026-05-04):**
- **NONE.** 7c.2 has NO prerequisite stories per governance JSON v2026-05-04-slab7c-thirty-six-stories. AMELIA-P1 path-isolation guard explicitly authorizes parallel execution alongside 7c.0a + 7c.0b.
- Slab 7b CLOSED end-to-end; validator reports 11 conforming activation contracts; no regression expected from 7c.2.
- Trial-2 forensic fixture preserved at `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/` (per Trial-2 postmortem; gitignored but operator-pinned per NFR-7c-OD6).

**Live substrate (verified at authoring; do NOT regress):**
- **Crash site:** `app/marcus/cli/trial.py:123` (declaration) / line 132 (call site) — the default `print_fn = (lambda msg: print(msg))` is what crashes. Fix replaces the default with a UTF-8-safe writer.
- **Directive read/write paths to audit:** `state/config/runs/<run-id>/directive.yaml` is read or written from multiple sites including `app/marcus/orchestrator/directive_composer.py` + `app/marcus/cli/trial.py` (`_confirm_or_edit_directive`) + any §02A composer body that 7c.3a later authors. 7c.2 audits ALL current sites and converts them to UTF-8-explicit; new 7c.3a-introduced sites inherit the convention.
- **Anti-pattern catalog target:** `docs/dev-guide/specialist-anti-patterns.md` (or `docs/dev-guide/dev-agent-anti-patterns.md` — verify actual filename at T1; the epic AC says "specialist-anti-patterns.md" but the de-facto catalog at the dev-agent level is `dev-agent-anti-patterns.md`. Surface as `decision_needed` if both exist; pick the canonical one or update both).

**AMELIA-P1 path-isolation guard (binding=hard; parallel-execution merge-conflict prevention):**

7c.2 spec **MUST NOT** modify ANY file under the following 7c.0a/0b deliverable paths. These paths are reserved for 7c.0a (currently in dev) and 7c.0b (gating; opens at 7c.0a close). Any modification under these paths during the 7c.2 dev round is a **HARD HALT** condition for the dev-agent.

```
FORBIDDEN PATHS (binding=hard):
- app/parity/contracts/**            # 7c.0b DSL primitives (entire subtree)
- app/models/tripwire_ledger.py      # 7c.0a TripwireLedgerEntry primary enforcement
- app/audit/**                       # 7c.0b audit-chain integrity scaffold (entire subtree if exists)
- tests/audit/test_override_event_chain_integrity.py  # 7c.0b executable scaffold
- docs/dev-guide/adr/0001-parity-contract-dsl.md      # 7c.0a ADR
- docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md    # 7c.4a (NOT 7c.0a/0b but reserved; do NOT collide)
- pyproject.toml::[tool.importlinter] C4/C5/C6 contract definitions  # 7c.0a contracts
- TW-7c-4/5/6 detection scaffolds (7c.0b; locations TBD per 7c.0b spec)
```

If 7c.2 dev surfaces a need to modify ANY of these paths, Codex SHALL HALT-AND-SURFACE to operator; do NOT proceed with the modification. The fix can ALWAYS land outside these paths (the cp1252 crash site is `app/marcus/cli/trial.py`, which is unrelated to 7c.0a/0b territory).

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 1 (parallel to 7c.0a/0b per John A2; AMELIA-P1 path-isolation guard active). cp1252 Windows-portability fix + fixture-comparison utility (FR-7c-5). Owns TW-7c-2 detection (cp1252 regression) + TW-7c-5 partial (cp1252 encoding regression). Closes Trial-2 finding #1 root cause structurally (not via PYTHONIOENCODING=utf-8 workaround). Single-gate justified: cp1252 fix is below the spec layer; no schema-shape, lane-boundary, or invariant-preservation risk.

**T1 conclusion:** No unanticipated architectural disagreement requires halting the dev round. Implementation proceeds: replace `app/marcus/cli/trial.py` print_fn default with UTF-8-safe writer + audit all directive read/write sites for UTF-8-explicit encoding + author cp1252 fixture-comparison utility + author NNBSP regression test + augment A11 anti-pattern catalog with §02A worked example. **Hard checkpoints at T1:** confirm `app/marcus/cli/trial.py:123` is still the print_fn declaration site (or surface the actual line if drift); confirm anti-pattern catalog filename (`specialist-anti-patterns.md` vs `dev-agent-anti-patterns.md`) and pick canonical home; confirm Trial-2 forensic fixture path `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/` exists for regression-test fixture pin.

---

## Story

As the operator (Juanl, running Trial-3 on Windows with macOS-screenshot Unicode in corpus content),
I want UTF-8 round-trip preservation across the §02A directive lifecycle (compose → write → print → operator review → edit → re-validate → submit) on Windows + a cp1252 fixture-comparison utility that catches regressions on macOS-screenshot Unicode (U+202F NNBSP and similar non-ASCII characters),
so that Trial-2 finding #1 (G0 print cp1252 crash at run `d44128e9-...`) is **structurally retired by construction** — not via the `PYTHONIOENCODING=utf-8` operator-environment workaround validated at Trial-2 attempts 5+.

---

## Acceptance Criteria

### AC-7c.2-A — AMELIA-P1 path-isolation guard honored throughout the dev round (binding=hard; merge-conflict prevention)

**Given** the AMELIA-P1 path-isolation guard from epic-decomposition party-mode Round-2 2026-05-04 (Amelia P1 amendment; binding=hard)
**When** the dev-agent develops 7c.2
**Then** **NO file** under any of the following 7c.0a/0b reserved paths is modified at any point during the dev round:

```
- app/parity/contracts/**
- app/models/tripwire_ledger.py
- app/audit/**
- tests/audit/test_override_event_chain_integrity.py
- docs/dev-guide/adr/0001-parity-contract-dsl.md
- docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md
- pyproject.toml::[tool.importlinter] C4 / C5 / C6 contract entries
- (any path 7c.0a or 7c.0b subsequently surfaces as a deliverable; check current 7c.0a/0b spec at T1 for the canonical list)
```

**And** at T9 verification, a structural test asserts the `git diff` for the 7c.2 dev round (vs the pre-7c.2 baseline) contains ZERO file modifications under any of the forbidden paths.

**Test pin:** `tests/structural/test_7c_2_path_isolation_honored.py` — runs `git diff --name-only HEAD~N..HEAD` (N = 7c.2 commit count) OR parses a `.git/diff-snapshot` fixture if git not available; asserts no file path matches the forbidden glob set.

> **Notes for 7c.2-A.** This AC is **dev-agent-executable** (git is on the dev-agent PATH per `migration-ac-sandbox-inventory.json` `dev_agent_available`). The test pin is a structural guardrail — if it ever fails, the implication is a merge-conflict-risk leak with the parallel 7c.0a/0b dev round. HALT-AND-SURFACE to operator.

### AC-7c.2-B — Print-path uses UTF-8 stream wrapping; directive bytes flow via UTF-8-explicit encoding everywhere (FR-7c-5 / NFR-7c-X1)

**Given** the Trial-2 finding #1 cp1252 print crash root cause at `app/marcus/cli/trial.py:123` (`print_fn = (lambda msg: print(msg))` default; crashes on `print()` to Windows console cp1252 stdout for U+202F NNBSP)
**When** the dev-agent identifies and replaces the default print_fn
**Then** the print-path uses UTF-8 stream wrapping. RECOMMEND (Codex picks one at T1 with rationale documented in Dev Notes):

**Option A (per-call buffer write; preferred — minimal surface):**
```python
def _utf8_safe_print(msg: str) -> None:
    """Print via UTF-8 buffer (Trial-2 finding #1 fix; Story 7c.2)."""
    sys.stdout.buffer.write(msg.encode("utf-8", errors="replace") + b"\n")
    sys.stdout.flush()


# Then in the calling site:
print_fn = _utf8_safe_print
```

**Option B (module-level reconfigure; alternate — broader surface):**
```python
# At app/marcus/cli/trial.py module top:
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

**And** EVERY site that reads or writes `state/config/runs/<run-id>/directive.yaml` uses UTF-8-explicit encoding:
```python
# READ: with open(path, encoding="utf-8") as f: ...    (NOT: open(path) — relies on default)
# WRITE: with open(path, "w", encoding="utf-8") as f: ...
# pathlib equivalents: path.read_text(encoding="utf-8") / path.write_text(text, encoding="utf-8")
# yaml: yaml.safe_load(path.read_text(encoding="utf-8")) — NOT yaml.safe_load(open(path)) — same default-encoding trap
```

**And** `app/marcus/orchestrator/directive_composer.py` (the existing 7a.1 composer) is audited for default-encoding sites and converted to UTF-8-explicit.

**Test pin:** `tests/integration/marcus/cli/test_trial_print_utf8_safe.py` — runs the `print_fn` against U+202F NNBSP-bearing input via captured stdout (`capsys` fixture); asserts no `UnicodeEncodeError` raised + asserts the captured bytes round-trip via UTF-8 decode.

> **Notes for 7c.2-B.** This AC is **dev-agent-executable** (pytest + capsys; no operator-only CLI). Codex picks Option A or B at T1 and documents rationale. Option A is preferred (per deferred-inventory recommendation; minimal surface = single function + single assignment). Option B has broader implications (reconfigures stderr too; affects ALL print/log calls in the CLI process — could mask other latent encoding bugs by fixing them silently). RECOMMEND Option A unless T1 surfaces a strong argument for B.

### AC-7c.2-C — cp1252 fixture-comparison utility lands at canonical path; cross-platform byte-equivalence assert (FR-7c-5 / TW-7c-2)

**Given** the cp1252 fixture-comparison utility (per Murat M1 amendment — 7c.2 absorbs fixture-utility scope)
**When** the dev-agent lands the utility at `app/marcus/utils/cp1252_fixture_compare.py` (or `scripts/utilities/compare_cp1252_fixtures.py` — surface as `decision_needed` at T1; pick the canonical home matching existing utility conventions)
**Then** the utility:

1. Accepts two paths (a directive bytes fixture path + an expected UTF-8 bytes path).
2. Reads both as raw bytes (NOT as text); does NOT trigger any text-mode default-encoding fallback.
3. Asserts byte-equivalence across Windows + Linux + macOS line-ending conventions (normalize `\r\n` ↔ `\n` if applicable; document the normalization rule in module docstring).
4. Surfaces a structured comparison verdict (Pydantic model OR plain dataclass — pick one): `{equivalent: bool, byte_count_a: int, byte_count_b: int, first_divergence_offset: int | None, divergence_context: str | None}`.
5. CLI entrypoint via `python -m app.marcus.utils.cp1252_fixture_compare path_a path_b` exits 0 on equivalence; exit 1 on divergence + prints divergence context.

**And** the utility is invokable from the FR-7c-46 UTF-8 CI lint pass (which 7c.0b scaffolds — 7c.2 contributes the cp1252-specific comparator that the lint pass calls).

**Test pin:** `tests/unit/marcus/utils/test_cp1252_fixture_compare.py` — covers (a) byte-equivalent UTF-8 fixtures pass; (b) cp1252-encoded fixture mismatch caught with first_divergence_offset populated; (c) CRLF↔LF normalization handled per documented rule; (d) U+202F NNBSP byte-sequence (`\xe2\x80\xaf` in UTF-8) preserved across the comparator.

> **Notes for 7c.2-C.** This AC is **dev-agent-executable** (pytest + raw-bytes I/O). The utility is a generic comparator — NOT a §02A-specific helper. 7c.0b's UTF-8 CI lint pass invokes it; 7c.3a's §02A composer regression test (against the Trial-2 forensic fixture) invokes it. Path placement: prefer `app/marcus/utils/` over `scripts/utilities/` because the utility is application-runtime (callable from §02A composer regression test in-process), not a one-off CLI script — surface as `decision_needed` at T1 if existing convention contradicts.

### AC-7c.2-D — U+202F NNBSP regression test passes on Windows without `PYTHONIOENCODING=utf-8` (FR-7c-5 / TW-7c-2)

**Given** the U+202F NARROW NO-BREAK SPACE regression test (closes Trial-2 finding #1 by construction)
**When** the dev-agent lands `tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py`
**Then** the test:

1. Constructs a directive YAML containing macOS-screenshot Unicode (e.g., a filename `differential diagnosis Screenshot 2026-02-10 at 5.38.36 PM.png` mirroring the Trial-2 trigger).
2. Invokes the `_confirm_or_edit_directive` G0 print path with the constructed directive.
3. Asserts the print succeeds (no `UnicodeEncodeError`) on Windows-default cp1252 stdout WITHOUT `PYTHONIOENCODING=utf-8` set in the test environment.
4. Asserts the printed bytes round-trip via UTF-8 decode to the original directive content (no character substitution).

**And** the test is parametrized over the canonical macOS-screenshot Unicode set (per epic prose — at minimum: U+202F NARROW NO-BREAK SPACE; U+00A0 NO-BREAK SPACE; U+2014 EM DASH; U+2018/U+2019 SINGLE QUOTATION MARKS; U+201C/U+201D DOUBLE QUOTATION MARKS).

**And** the test environment management explicitly removes any inherited `PYTHONIOENCODING=utf-8` from the test process environment (use `monkeypatch.delenv("PYTHONIOENCODING", raising=False)`); this verifies the structural fix is doing the work, not the operator-env workaround.

**Test pin:** the test itself is the regression pin. ALSO extend `tests/structural/test_directive_io_uses_utf8_explicit.py` (NEW) — AST scan asserts that every site reading or writing `state/config/runs/**/directive.yaml` uses UTF-8-explicit encoding (catches future regressions where a new site relies on default encoding).

> **Notes for 7c.2-D.** This AC is **dev-agent-executable** (pytest + monkeypatch + AST scan). The Trial-2 forensic fixture at `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/` MAY be used as an additional fixture-pin if the directory structure is preserved at T1 — but the regression test SHALL also be self-contained (constructs its own NNBSP-bearing directive in a tmp_path) so it remains green even if the forensic fixture is gitignored or pruned later.

### AC-7c.2-E — Anti-pattern A11 augmented with Slab 7c §02A worked example (epic AC #4; deferred-inventory closure)

**Given** the Trial-2 finding #1 deferred-inventory closure precondition
**When** 7c.2 closes
**Then** anti-pattern A11 (Windows-portability) in `docs/dev-guide/dev-agent-anti-patterns.md` (or `specialist-anti-patterns.md` — pick canonical at T1) is augmented with a Slab 7c §02A worked example documenting:

1. **Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode character ' ' in position N` at `print(text)` on Windows console with macOS-screenshot Unicode in the input.
2. **Root cause:** Python's `print()` uses `sys.stdout.encoding` which defaults to `cp1252` on Windows console; non-Latin-1 codepoints raise.
3. **Anti-fix:** `PYTHONIOENCODING=utf-8` operator-environment workaround (validated at Trial-2 attempts 5+; addresses symptom but leaks workaround responsibility to operator; not a structural fix).
4. **Structural fix (canonical):** Replace `print(msg)` with `sys.stdout.buffer.write(msg.encode("utf-8", errors="replace") + b"\n")` (Option A from 7c.2-B); ALWAYS pass `encoding="utf-8"` explicitly to `open()` / `Path.read_text()` / `Path.write_text()` / `yaml.safe_load(path.read_text(...))`.
5. **Detection guardrail:** `tests/structural/test_directive_io_uses_utf8_explicit.py` (AST scan from 7c.2-D) + cp1252 fixture-comparison utility (7c.2-C) + FR-7c-46 UTF-8 CI lint pass (7c.0b).
6. **Reference:** Trial-2 postmortem run `d44128e9-4e17-4452-a535-989e826cd7da` 2026-05-04; Trial-2 finding #1 closure recorded at Slab 7c retrospective per FR-7c-43.

**And** the deferred-inventory entry `trial-2-finding-1-cp1252-crash` is updated with status `closed-by-7c.2` + cross-reference to this story key + the augmented A11 entry.

**Test pin:** `tests/structural/test_anti_pattern_a11_slab_7c_example_present.py` — asserts the catalog file contains the keyword set `{"Slab 7c", "§02A", "U+202F", "structural fix", "PYTHONIOENCODING"}` co-located within a single A11 section.

> **Notes for 7c.2-E.** This AC is **dev-agent-executable** (markdown authoring + structural test + deferred-inventory edit). The deferred-inventory edit is markdown-only (no code change). Codex SHALL touch `_bmad-output/planning-artifacts/deferred-inventory.md` at section `trial-2-finding-1-cp1252-crash` only; do not modify other deferred-inventory entries.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks (AC: T1 Readiness Block + 7c.2-A path-isolation)**
  - [ ] T1.1 Confirm `app/marcus/cli/trial.py:123` is still the print_fn declaration site; surface actual line if drifted.
  - [ ] T1.2 Pick canonical anti-pattern catalog filename (`dev-agent-anti-patterns.md` vs `specialist-anti-patterns.md`); document in Dev Notes.
  - [ ] T1.3 Confirm Trial-2 forensic fixture `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/` exists (informational — regression test does NOT depend on it).
  - [ ] T1.4 Pick canonical home for cp1252 fixture-comparison utility (`app/marcus/utils/` vs `scripts/utilities/`); document rationale.
  - [ ] T1.5 Pick Option A or Option B for print_fn UTF-8 fix (per 7c.2-B; recommend Option A).
  - [ ] T1.6 Verify AMELIA-P1 path-isolation: read 7c.0a + 7c.0b spec deliverable file lists; confirm 7c.2 plan touches NONE of them.
  - [ ] T1.7 Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-2-cp1252-windows-portability-fix.md`; expect PASS.
  - [ ] T1.8 Read dev-agent-anti-patterns.md (A11 entry) + story-cycle-efficiency.md (cite-by-reference; no re-derivation).

- [ ] **T2 — Replace print_fn default with UTF-8-safe writer (AC: 7c.2-B)**
  - [ ] T2.1 Edit `app/marcus/cli/trial.py` per Option A (preferred) or Option B (per T1.5).
  - [ ] T2.2 Audit ALL directive read/write sites; convert default-encoding to UTF-8-explicit.

- [ ] **T3 — Author cp1252 fixture-comparison utility (AC: 7c.2-C)**
  - [ ] T3.1 Land utility at canonical path per T1.4.
  - [ ] T3.2 Pydantic model OR dataclass for the comparison verdict.
  - [ ] T3.3 CLI entrypoint `python -m <module> path_a path_b`.
  - [ ] T3.4 Module docstring documents CRLF↔LF normalization rule.

- [ ] **T4 — Author U+202F NNBSP regression test (AC: 7c.2-D)**
  - [ ] T4.1 `tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py` parametrized over canonical macOS-screenshot Unicode set.
  - [ ] T4.2 `monkeypatch.delenv("PYTHONIOENCODING", raising=False)` to verify structural fix.
  - [ ] T4.3 Self-contained NNBSP-bearing directive in `tmp_path` (do NOT depend on Trial-2 forensic fixture).

- [ ] **T5 — Author AST scan structural test (AC: 7c.2-D test pin)**
  - [ ] T5.1 `tests/structural/test_directive_io_uses_utf8_explicit.py` — AST scan of all sites reading/writing `state/config/runs/**/directive.yaml`.
  - [ ] T5.2 Assert every `open()` / `Path.read_text()` / `Path.write_text()` call site has `encoding="utf-8"` explicitly.

- [ ] **T6 — Author cp1252 fixture-comparison utility unit test (AC: 7c.2-C test pin)**
  - [ ] T6.1 `tests/unit/marcus/utils/test_cp1252_fixture_compare.py` covering 4 cases (byte-equivalent / cp1252-mismatch-caught / CRLF-normalized / U+202F preserved).

- [ ] **T7 — Augment anti-pattern A11 catalog (AC: 7c.2-E)**
  - [ ] T7.1 Add Slab 7c §02A worked example with all 6 required elements (symptom + root cause + anti-fix + structural fix + detection guardrail + reference).
  - [ ] T7.2 Update `_bmad-output/planning-artifacts/deferred-inventory.md` `trial-2-finding-1-cp1252-crash` entry with `closed-by-7c.2` status.
  - [ ] T7.3 Author `tests/structural/test_anti_pattern_a11_slab_7c_example_present.py` keyword-set assertion.

- [ ] **T8 — Author path-isolation guard test (AC: 7c.2-A)**
  - [ ] T8.1 `tests/structural/test_7c_2_path_isolation_honored.py` — `git diff` parsing OR `.git/diff-snapshot` fixture; asserts no forbidden-path modifications across the 7c.2 commit set.

- [ ] **T9 — CI hygiene clean (NFR-7c-R5 / NFR-7c-X4 / NFR-7c-M5)**
  - [ ] T9.1 `ruff check` on all touched files — clean.
  - [ ] T9.2 Run focused tests: `pytest tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py tests/integration/marcus/cli/test_trial_print_utf8_safe.py tests/unit/marcus/utils/test_cp1252_fixture_compare.py tests/structural/test_directive_io_uses_utf8_explicit.py tests/structural/test_anti_pattern_a11_slab_7c_example_present.py tests/structural/test_7c_2_path_isolation_honored.py -p no:randomly` — all pass.
  - [ ] T9.3 Run broad regression: `pytest -p no:randomly` — ≥1403 baseline preserved (no regression).
  - [ ] T9.4 Sandbox-AC validator PASS (re-run from T1.7).
  - [ ] T9.5 Class-conformance validator: 11 conforming activation contracts (no regression; 7c.2 is not an activation-contract change).
  - [ ] T9.6 `lint-imports` clean (KEPT count unchanged from pre-7c.2 baseline; 7c.2 does not add or modify import-linter contracts).

- [ ] **T10 — Codex self-review (NEW CYCLE T10)**
  - [ ] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-2.ready-for-review.md` summarizing: file list, test counts, ruff status, broad-regression delta, sandbox-AC validator status, AMELIA-P1 path-isolation verification (zero forbidden-path modifications confirmed), Option A/B picked at T1.5, any T1 `decision_needed` resolutions, deferred follow-ons surfaced.

- [ ] **T11 — Claude `bmad-code-review` (single-gate; cross-agent NOT mandatory)**
  - [ ] T11.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the 7c.2 diff; produces verdict at `_bmad-output/implementation-artifacts/7c-2-code-review-2026-05-NN.md`; applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-2-cp1252-windows-portability-fix: review → done` in sprint-status.

---

## Dev Notes

**Architecture decisions inherited from epic-decomposition party-mode 2026-05-04:**
- **John A2** — 7c.2 opens parallel to 7c.0a + 7c.0b. Does NOT wait. Per Slab 7c epic Story 7c.2 metadata.
- **AMELIA-P1** (binding=hard) — 7c.2 spec MUST forbid touching any 7c.0a/0b deliverable path. Forbidden-paths list explicit in AC-7c.2-A. Test pin asserts zero modifications.
- **Murat M1** — 7c.2 absorbs cp1252 fixture-comparison utility scope (alternative was a separate utility-tier story; folded for K-economy).

**Trial-2 forensic context:**
- Run ID: `d44128e9-4e17-4452-a535-989e826cd7da` (2026-05-04 ≈17:00 UTC).
- Crash signature: `UnicodeEncodeError: 'charmap' codec can't encode character ' ' in position 2001` at `app/marcus/cli/trial.py:132` (call `print_fn(directive_path.read_text(encoding="utf-8"))` — read was UTF-8-safe; the `print_fn` itself was the failure).
- Trigger filename: `differential diagnosis Screenshot 2026-02-10 at 5.38.36 PM.png` — macOS embeds U+202F NNBSP between time and AM/PM.
- Workaround validated: `PYTHONIOENCODING=utf-8` resolved at Trial-2 attempts 5+. 7c.2 retires this workaround structurally.

**File / module placement:**
- `app/marcus/cli/trial.py` — modify in place (replace print_fn default).
- `app/marcus/orchestrator/directive_composer.py` — audit + convert any default-encoding sites.
- `app/marcus/utils/cp1252_fixture_compare.py` (recommend) OR `scripts/utilities/compare_cp1252_fixtures.py` — surface at T1; pick canonical home matching existing utility conventions.
- `tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py` — NEW; integration test.
- `tests/integration/marcus/cli/test_trial_print_utf8_safe.py` — NEW; integration test.
- `tests/unit/marcus/utils/test_cp1252_fixture_compare.py` — NEW; unit test.
- `tests/structural/test_directive_io_uses_utf8_explicit.py` — NEW; AST scan.
- `tests/structural/test_anti_pattern_a11_slab_7c_example_present.py` — NEW; structural test.
- `tests/structural/test_7c_2_path_isolation_honored.py` — NEW; structural test.
- `docs/dev-guide/dev-agent-anti-patterns.md` (or `specialist-anti-patterns.md`) — augment A11.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — update `trial-2-finding-1-cp1252-crash` entry.

**Anti-patterns to avoid (from `dev-agent-anti-patterns.md`):**
- **A11 Windows-portability** (the topic of THIS story) — every new line of code MUST use UTF-8-explicit encoding. The fix MUST NOT introduce a new default-encoding site.
- **A-test-1 Mocking the system-under-test** — the U+202F regression test MUST exercise the real `_confirm_or_edit_directive` print path; do NOT mock `print_fn` in a way that bypasses the actual cp1252 stdout encoding.

**K-discipline (from `story-cycle-efficiency.md`):**
- K-target 1.2× = ~1.5K LOC band-floor × 1.2 = ~1.8K LOC at T-shape ceiling; ~1 pt. Print-fn fix ~10-30 LOC; encoding audit ~50-150 LOC across multiple sites; cp1252 utility ~150 LOC; 6 test files ~80-200 LOC each (~600-1200 LOC total); A11 catalog augmentation ~30-50 LOC; deferred-inventory edit ~5-10 LOC. Estimate: ~1.0-1.5K LOC. Comfortable headroom under K-target ceiling.
- If T1 surfaces additional default-encoding sites that grow the audit-and-fix surface beyond ~300 LOC, re-evaluate K-projection and surface in Codex T10 self-review.

**Testing standards:**
- Pytest with `-p no:randomly` for deterministic-baseline preservation (NFR-7c-R2).
- Integration tests for CLI behavior (real `print_fn` + real stdout); unit tests for utility (raw bytes I/O); structural tests for AST scan + path-isolation + anti-pattern catalog.
- `monkeypatch.delenv("PYTHONIOENCODING")` is mandatory in the NNBSP regression test — verify the structural fix, not the operator-env workaround.

### Project Structure Notes

- **Alignment with unified project structure:** All new test paths conform to existing conventions (`tests/integration/marcus/cli/`, `tests/unit/marcus/utils/`, `tests/structural/`). Application module placement (`app/marcus/utils/cp1252_fixture_compare.py`) is consistent with sibling utilities under `app/marcus/`.
- **Detected variances:** Anti-pattern catalog filename ambiguity (`dev-agent-anti-patterns.md` vs `specialist-anti-patterns.md`) surfaces at T1 as `decision_needed`; cp1252 fixture-comparison utility canonical-home decision (app/marcus/utils/ vs scripts/utilities/) surfaces at T1 as `decision_needed`. Codex SHALL pick + document rationale; both decisions are reversible if cross-agent code-review at T11 disagrees.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-2]
- [Source: docs/dev-guide/dev-agent-anti-patterns.md#A11-Windows-portability]
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline; single-gate review policy)
- [Source: _bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md] (Trial-2 finding #1 forensic detail; run `d44128e9-...` crash trace)
- [Source: _bmad-output/planning-artifacts/deferred-inventory.md#trial-2-finding-1-cp1252-crash] (deferred-inventory entry; recommended fix paths; reactivation criteria)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md#FR-7c-5] (UTF-8 round-trip across §02A directive lifecycle)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md#TW-7c-2] (cp1252 regression detection; high severity)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.2] (Story 7c.2 section starting at line 446; AMELIA-P1 path-isolation guard)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

(Populated during dev round.)

### Completion Notes List

(Populated during dev round.)

### File List

(Populated during dev round; expected: ~10 files — 1 modified `app/marcus/cli/trial.py` + 0-2 modified directive read/write sites + 1 NEW `app/marcus/utils/cp1252_fixture_compare.py` + 6 NEW test files + 1 modified `docs/dev-guide/dev-agent-anti-patterns.md` + 1 modified `_bmad-output/planning-artifacts/deferred-inventory.md`. Net: ~10 files touched; ~1.0-1.5K LOC.)
