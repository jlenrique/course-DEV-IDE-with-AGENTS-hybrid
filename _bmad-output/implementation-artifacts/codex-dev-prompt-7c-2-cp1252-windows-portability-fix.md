# Codex dev-story prompt — Story 7c.2 (cp1252 Windows-portability fix + fixture-comparison utility)

**Cycle:** Claude spec → Codex T1-T9 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-2.ready-for-review.md` → Claude T11 `bmad-code-review` (single-gate; cross-agent NOT mandatory) → Claude commit + flip done.
**Wave:** 1 slot 1 (**parallel with 7c.0a + 7c.0b** per John A2; AMELIA-P1 path-isolation guard ACTIVE — see Boundary section).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline revision.
**AMELIA-P2 freshness check:** Claude re-diffs `migration-7c-2-cp1252-windows-portability-fix.md` (spec) against this prompt at operator dispatch time; if spec hash changed, Claude regenerates this prompt before dispatch.

---

```
Run bmad-dev-story on Story 7c.2 (Slab 7c Wave 1 slot 1; single-gate; cp1252 Windows-portability fix + fixture-comparison utility + U+202F NNBSP regression test + A11 anti-pattern augmentation; closes Trial-2 finding #1 structurally).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-2-cp1252-windows-portability-fix.md` (status: ready-for-dev; 5 ACs A-E; 11 tasks T1-T11; you own T1-T10).
2. Trial-2 postmortem: `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` — Trial-2 finding #1 forensic detail (run `d44128e9-4e17-4452-a535-989e826cd7da` crash at `app/marcus/cli/trial.py:132`).
3. Deferred inventory: `_bmad-output/planning-artifacts/deferred-inventory.md` — `trial-2-finding-1-cp1252-crash` entry (recommended fix paths; reactivation criteria).
4. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-5 (UTF-8 round-trip) + TW-7c-2 firing rule.
5. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.2 section starting at line 446; AMELIA-P1 path-isolation guard).
6. Required readings:
   - `docs/dev-guide/dev-agent-anti-patterns.md` (A11 Windows-portability; the anti-pattern this story augments).
   - `docs/dev-guide/story-cycle-efficiency.md` (K-discipline; single-gate review policy).
7. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-2` (single-gate; expected_pts=1; expected_k_target=1.2; path_isolation_guard with binding=hard).
8. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
9. Crash site: `app/marcus/cli/trial.py:123` (declaration) / `:132` (call site) — `print_fn = (lambda msg: print(msg))` default crashes Windows console cp1252 stdout on U+202F NNBSP.
10. Companion 7c.0a + 7c.0b spec lists (read at T1 to verify AMELIA-P1 forbidden-paths set is current):
    - `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` (currently in dev by Codex 2026-05-04 OR done by your dispatch time).
    - `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` if it exists at T1 (it does NOT exist yet at 2026-05-04 spec authoring; check at dispatch time).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- `app/marcus/cli/trial.py:123` (or current declaration line) STILL contains `print_fn = (lambda msg: print(msg))` (or analogous default-print-based pattern). If drift, surface actual line number + new pattern in T10 self-review and adjust the fix to match.
- AMELIA-P1 forbidden-paths set verified against current 7c.0a spec deliverable list. If 7c.0a has surfaced ADDITIONAL paths beyond the canonical list (see Boundary), HALT-AND-SURFACE; do NOT proceed without operator/Claude confirmation that the additional paths are still forbidden for 7c.2.
- Anti-pattern catalog filename: pick `dev-agent-anti-patterns.md` (default) OR `specialist-anti-patterns.md` if it is the authoritative file at T1. Surface as `decision_needed` if both exist; pick the canonical one and document rationale.
- cp1252 fixture-comparison utility home: pick `app/marcus/utils/cp1252_fixture_compare.py` (default; matches application-runtime convention) OR `scripts/utilities/compare_cp1252_fixtures.py` if existing utility convention contradicts. Surface as `decision_needed`.
- Print-fn fix: pick **Option A** (per-call buffer write — preferred; minimal surface) OR **Option B** (module-level reconfigure — broader surface). Default Option A; document rationale if picking B.
- `monkeypatch.delenv("PYTHONIOENCODING", raising=False)` works in pytest (default; should be fine with `pytest>=7`).
- Trial-2 forensic fixture path `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/` informational only — regression test SHALL be self-contained (constructs NNBSP fixture in `tmp_path`).

## Files in scope

**New (~7 files):**
- `app/marcus/utils/cp1252_fixture_compare.py` (or scripts/utilities/ alternative; pick at T1) — comparator utility + Pydantic/dataclass verdict + CLI entrypoint (`python -m <module> path_a path_b`).
- `tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py` — U+202F NNBSP regression test parametrized over 7 macOS-screenshot Unicode codepoints (U+202F, U+00A0, U+2014, U+2018, U+2019, U+201C, U+201D); `monkeypatch.delenv("PYTHONIOENCODING")`.
- `tests/integration/marcus/cli/test_trial_print_utf8_safe.py` — print-fn UTF-8 safe test via capsys.
- `tests/unit/marcus/utils/test_cp1252_fixture_compare.py` — utility unit test (4 cases).
- `tests/structural/test_directive_io_uses_utf8_explicit.py` — AST scan asserting all `state/config/runs/**/directive.yaml` read/write sites use `encoding="utf-8"` explicitly.
- `tests/structural/test_anti_pattern_a11_slab_7c_example_present.py` — keyword-set assertion on the anti-pattern catalog.
- `tests/structural/test_7c_2_path_isolation_honored.py` — `git diff` parsing OR `.git/diff-snapshot` fixture; asserts no forbidden-path modifications.

**Modified (~3 files):**
- `app/marcus/cli/trial.py` — replace `print_fn` default per Option A (preferred); audit + convert any default-encoding sites to UTF-8-explicit.
- `app/marcus/orchestrator/directive_composer.py` — audit + convert any default-encoding sites that read/write `directive.yaml`.
- `docs/dev-guide/dev-agent-anti-patterns.md` (or `specialist-anti-patterns.md` per T1) — augment A11 Windows-portability with Slab 7c §02A worked example (6 required elements: symptom + root cause + anti-fix + structural fix + detection guardrail + reference).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — update `trial-2-finding-1-cp1252-crash` entry with `closed-by-7c.2` status + cross-reference.

**Do NOT modify (AMELIA-P1 path-isolation guard; binding=hard):**

```
- app/parity/contracts/**            # 7c.0b DSL primitives subtree
- app/models/tripwire_ledger.py      # 7c.0a TripwireLedgerEntry (currently in Codex dev)
- app/audit/**                       # 7c.0b audit-chain subtree if exists
- tests/audit/test_override_event_chain_integrity.py  # 7c.0b executable scaffold
- docs/dev-guide/adr/0001-parity-contract-dsl.md      # 7c.0a ADR
- docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md    # 7c.4a (reserved; do NOT collide)
- pyproject.toml::[tool.importlinter] C4 / C5 / C6 contract entries  # 7c.0a contracts
- TW-7c-4/5/6 detection scaffolds (7c.0b territory)
- (any path 7c.0a or 7c.0b spec subsequently surfaces; verify at T1)
```

If your fix surfaces a need to touch any of these paths, **HALT-AND-SURFACE** to operator immediately. The fix can ALWAYS land outside these paths — `app/marcus/cli/trial.py` + `app/marcus/orchestrator/directive_composer.py` + `app/marcus/utils/` + new test files + anti-pattern catalog + deferred-inventory are ALL outside the forbidden set.

## Critical implementation notes

- **K-target 1.2× ≈ ~1.8K LOC ceiling.** Print-fn fix ~30 LOC; encoding audit ~50-150 LOC; cp1252 utility ~150 LOC; 6 test files ~600-1200 LOC; A11 catalog ~30-50 LOC; deferred-inventory edit ~5-10 LOC. Estimate ~1.0-1.5K LOC. Comfortable headroom.
- **Single-gate** — Claude T11 review is mandatory (per BMAD sprint governance §3) but cross-agent NOT mandatory. Claude reviews in fresh context; T10 Codex self-review is supplemental.
- **AMELIA-P1 path-isolation is BINDING=HARD.** Test pin asserts zero forbidden-path modifications. The risk model is: 7c.2 + 7c.0a + 7c.0b are all in dev simultaneously; touching shared paths produces merge conflicts at commit time. The fix is to keep them disjoint by construction.
- **U+202F regression test MUST `monkeypatch.delenv("PYTHONIOENCODING")`.** This verifies the structural fix is doing the work, not the operator-env workaround validated at Trial-2 attempts 5+. If the test passes only with `PYTHONIOENCODING=utf-8` set, the fix is incomplete.
- **Print-fn Option A vs B:** Option A (per-call `sys.stdout.buffer.write(msg.encode("utf-8", errors="replace") + b"\n")`) is preferred — minimal surface; does NOT reconfigure stderr. Option B (module-level `sys.stdout.reconfigure(encoding="utf-8")`) reconfigures stderr too and could mask other latent encoding bugs by silently fixing them. RECOMMEND Option A.
- **Anti-pattern A11 augmentation MUST contain all 6 required elements** (symptom + root cause + anti-fix + structural fix + detection guardrail + reference). Test pin asserts keyword set `{"Slab 7c", "§02A", "U+202F", "structural fix", "PYTHONIOENCODING"}` co-located in a single A11 section.
- **No new third-party deps.** Pydantic v2 + tomllib + pathlib (stdlib).
- **Windows portability is THIS STORY'S TOPIC.** Every line of new code MUST use UTF-8-explicit encoding; do NOT introduce a NEW default-encoding site as part of this fix.

## Verification battery (T9)

```bash
# Focused tests (6 new test files):
.venv/Scripts/python.exe -m pytest tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py tests/integration/marcus/cli/test_trial_print_utf8_safe.py tests/unit/marcus/utils/test_cp1252_fixture_compare.py tests/structural/test_directive_io_uses_utf8_explicit.py tests/structural/test_anti_pattern_a11_slab_7c_example_present.py tests/structural/test_7c_2_path_isolation_honored.py -p no:randomly -q --tb=short

# Broad regression slice (NFR-7c-R2; preserve ≥1403 deterministic baseline):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Class-conformance validator (NFR-7c-R5; expect 11 conforming activation contracts; no regression — 7c.2 is NOT an activation-contract change):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Import-linter (KEPT count UNCHANGED from pre-7c.2 baseline; 7c.2 does NOT add or modify import-linter contracts):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator (NFR-7c-M5):
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-2-cp1252-windows-portability-fix.md

# Ruff hygiene on the touched files:
.venv/Scripts/python.exe -m ruff check app/marcus/cli/trial.py app/marcus/orchestrator/directive_composer.py app/marcus/utils/cp1252_fixture_compare.py tests/integration/marcus/cli/test_trial_g0_print_nnbsp.py tests/integration/marcus/cli/test_trial_print_utf8_safe.py tests/unit/marcus/utils/test_cp1252_fixture_compare.py tests/structural/test_directive_io_uses_utf8_explicit.py tests/structural/test_anti_pattern_a11_slab_7c_example_present.py tests/structural/test_7c_2_path_isolation_honored.py
```

Expected post-7c.2 baseline:
- ≥1403 broad-regression deterministic baseline preserved (no test regression introduced).
- `lint-imports` KEPT count UNCHANGED from pre-7c.2 baseline (7c.2 does not add/modify contracts).
- `validate_parity_test_class_conformance.py` reports 11 conforming activation contracts (no class-conformance change).
- Sandbox-AC validator PASS.
- Ruff CLEAN on the ~9 touched files.
- Path-isolation test green: zero forbidden-path modifications across the 7c.2 commit set.

## T10 + T11

**T10:** Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/_codex-handoff/7c-2.ready-for-review.md`. Per `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 dropbox protocol — drop the completion notice into the Claude-watched dropbox path. Flip story status `in-progress` → `review` in the spec file. Hand to Claude via the dropbox.

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (single-gate; cross-agent NOT mandatory but Claude review remains mandatory per BMAD sprint governance §3). Review verdict lands at `_bmad-output/implementation-artifacts/7c-2-code-review-2026-05-NN.md`. Claude applies remediation cycles if HALT-AND-REMEDIATE; commits the diff (~7 NEW + ~3 MODIFIED files); flips `migration-7c-2-cp1252-windows-portability-fix: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) AMELIA-P1 path-isolation violation — ANY modification under any forbidden-paths-set entry. Even a one-line change to `pyproject.toml`'s `[tool.importlinter]` C4/C5/C6 block is a halt condition.
  (b) Drift in `app/marcus/cli/trial.py:123` print_fn declaration site (different line / different pattern).
  (c) U+202F regression test fails on Windows even with the structural fix in place — root-cause investigate; the structural fix is incomplete.
  (d) AST scan finds a directive read/write site that cannot be cleanly converted to UTF-8-explicit (e.g., a third-party library call that internally relies on default encoding) — surface for design discussion.
  (e) Anti-pattern catalog has an existing A11 Slab 7c §02A example that conflicts with this story's augmentation — surface; pick the canonical phrasing.
  (f) K-actual exceeds 1.7× target (~3K LOC) — surface for K-budget renegotiation; story scope likely too broad.
  (g) ANY sandbox-AC violation — should not happen given dev-agent-only ACs.
  (h) Broad-regression delta < 0 (any pre-existing test regresses) — investigate root cause; do NOT skip the test.
  (i) `lint-imports` KEPT count changes from baseline — 7c.2 should NOT touch import-linter contracts; if changed, you accidentally modified `pyproject.toml::[tool.importlinter]`.

- **Do NOT touch:**
  - ANY path under the AMELIA-P1 forbidden-paths set (see Files in scope §Do NOT modify).
  - Any specialist body (`app/specialists/**`).
  - Any HIL surface module (`app/gates/**`).
  - `state/config/pipeline-manifest.yaml` (this is a CLI/encoding fix; pipeline-manifest does NOT change).
  - Composition Spec (`docs/dev-guide/composition-specification.md`; cp1252 fix is below the spec layer).
  - Slab 7b retrospective artifacts.

- **Do NOT introduce:**
  - New third-party deps.
  - New default-encoding sites (`open()` without `encoding="utf-8"`, `Path.read_text()` without `encoding="utf-8"`, etc.).
  - `PYTHONIOENCODING=utf-8` workarounds in test fixtures or production code (the entire point of this story is to retire that workaround).
  - Pydantic v2 model duplicates of TripwireLedgerEntry (that lives in `app/models/tripwire_ledger.py` per 7c.0a; do NOT touch).
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-2-cp1252-windows-portability-fix.md` → expect PASS.
2. ☐ Verify governance JSON entry for 7c-2 is current (single-gate; K=1.2; pts=1; path_isolation_guard binding=hard) — locked at v2026-05-04-slab7c-thirty-six-stories.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-2-cp1252-windows-portability-fix.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ AMELIA-P1 forbidden-paths set verified against current 7c.0a + 7c.0b spec deliverable lists at dispatch time. If 7c.0a has CLOSED, the forbidden-paths set narrows to the 7c.0b territory — update the prompt's Boundary section accordingly before dispatch.
5. ☐ Confirm sprint-status.yaml shows `migration-7c-2-cp1252-windows-portability-fix: ready-for-dev`.
6. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.
7. ☐ **Operator may dispatch 7c.2 BEFORE 7c.0a closes** — the AMELIA-P1 path-isolation guard makes this safe. Operator MAY choose to wait until 7c.0a closes for simplicity, but parallelism is supported.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-2.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~10-file diff; runs `bmad-code-review` (T11; single-gate; cross-agent NOT mandatory).
3. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
4. ☐ Claude commits + flips `migration-7c-2-cp1252-windows-portability-fix: review → done` in sprint-status.yaml.
5. ☐ At 7c.2 close, no new stories unblock directly (7c.2 is a parallel branch; its closure does not gate any other Wave 1+ story); but Trial-3 G0 print path is structurally retired, removing one Trial-3 readiness blocker.
