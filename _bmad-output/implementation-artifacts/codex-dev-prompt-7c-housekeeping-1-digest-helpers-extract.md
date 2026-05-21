# Codex dev-story prompt — 7c-housekeeping-1 (digest helpers extract; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-housekeeping-1.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

---

```
Run bmad-dev-story on Story 7c-housekeeping-1 (digest helpers extract; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-housekeeping-1-digest-helpers-extract.md`.

## Required reading

1. Story spec (4 ACs A-D).
2. `_bmad-output/implementation-artifacts/7c-7-code-review-2026-05-05.md` §"SHOULD-FIX-DEFERRED" (origin).
3. `app/gates/section_02a/poll_surface.py` (canonical helper shape; READ-ONLY).
4. `pyproject.toml::tool.importlinter::contracts::C6` (confirm `_common` NOT in modules list).

## T1 hard checkpoints

- 14 §section poll-surface modules inventory matches: section_02a, section_04a, section_04_5, section_04_55, section_05_5, section_06b, section_07b, section_07c, section_07d, section_07f, section_08b, section_11, section_11b, section_15.
- All 14 contain byte-identical `canonical_model_bytes` + `compute_model_digest` definitions.
- `app.gates._common` NOT in C6 modules list.
- Class-conformance baseline = 19.

## Files in scope

**New (3 files):**
- `app/gates/_common/__init__.py` (empty)
- `app/gates/_common/digest_helpers.py` (~50 LOC; canonical_model_bytes + compute_model_digest)
- `tests/gates/_common/__init__.py` + `tests/gates/_common/test_digest_helpers.py` (~50 LOC)

**Modified (14 files):**
- `app/gates/section_02a/poll_surface.py`
- `app/gates/section_04a/poll_surface.py`
- `app/gates/section_04_5/poll_surface.py`
- `app/gates/section_04_55/poll_surface.py`
- `app/gates/section_05_5/poll_surface.py`
- `app/gates/section_06b/poll_surface.py`
- `app/gates/section_07b/poll_surface.py`
- `app/gates/section_07c/poll_surface.py`
- `app/gates/section_07d/poll_surface.py`
- `app/gates/section_07f/poll_surface.py`
- `app/gates/section_08b/poll_surface.py`
- `app/gates/section_11/poll_surface.py`
- `app/gates/section_11b/poll_surface.py`
- `app/gates/section_15/poll_surface.py`

For each modified file: REMOVE local `canonical_model_bytes` + `compute_model_digest` definitions; ADD `from app.gates._common.digest_helpers import canonical_model_bytes, compute_model_digest`; UPDATE local `__all__` to no longer export the two helpers; verify all call-sites still resolve.

**Do NOT modify:**
- `pyproject.toml` (C6 contract stays unchanged; `_common` is outside C6 by design)
- Any test files outside `tests/gates/_common/`
- Any production code beyond the 14 named poll_surface.py files

## Critical implementation notes

- **Byte-identicality**: helpers in `_common` MUST produce identical output to the existing implementations. Verify via spot-check sha256 comparison across one or two §section before-and-after the refactor.
- **C6 isolation preserved**: `_common` is NOT in C6 modules list. §section → `_common` cross-imports are LEGAL (one direction). C6 contract `independence` between §section modules is preserved (no §section imports another §section).
- **No behavior change**: pure refactor. All existing tests must continue to PASS unchanged.
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~250 LOC delta (much of it deletion).
- **T11 lite tier**: structural refactor; no new contracts; no schema changes.

## Verification battery (T5)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/ tests/schemas/operator_verdict/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/_common/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-housekeeping-1-digest-helpers-extract.md
.venv/Scripts/python.exe -m ruff check app/gates/_common/ tests/gates/_common/ <14 modified poll_surface.py paths>
```

## T10

T10: dropbox at `_codex-handoff/7c-housekeeping-1.ready-for-review.md`. Include: 1 new dir + 14 modified poll-surface files + per-§section call-site count unchanged + sha256 byte-determinism comparison evidence (spot-check 2-3 §sections pre/post).

## Boundary

HALT on: any §section test failure post-refactor; class-conformance count change; lint-imports KEPT count change; broad-regression delta > 0.

DO NOT introduce: new public API surface; behavior changes; new contracts; pyproject.toml edits.
```

---

## Operator dispatch checklist

1. ☐ AMELIA-P2 freshness check.
2. ☐ Sandbox-AC PASS.
3. ☐ Sprint-status: ready-for-dev.
4. ☐ Dispatch (solo).
