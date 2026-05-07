# Codex dev-story prompt — 7c-housekeeping-4 (legacy sidecar cleanup vera+dan; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T1-T10 → drops `_codex-handoff/7c-housekeeping-4.ready-for-review.md` → Claude T11 lite → commit + flip done.

**DISPATCH-DEFERRED** until operator confirms Trial-2 validation evidence per spec AC-1.

---

```
Run bmad-dev-story on Story 7c-housekeeping-4 (vera + dan legacy sidecar cleanup).

Spec: `_bmad-output/implementation-artifacts/migration-7c-housekeeping-4-legacy-sidecar-cleanup.md`.

## Required reading

1. Story spec (4 ACs A-D).
2. `_bmad-output/planning-artifacts/deferred-inventory.md` (locate `vera-sidecar-cleanup-post-trial-2-validation` + `dan-sidecar-cleanup-post-trial-2-validation` entries).
3. `_bmad/memory/bmad-agent-vera/` + `_bmad/memory/bmad-agent-dan/` (BMB-canonical sanctums; READ-ONLY; verify 6-file pattern).
4. `_bmad/memory/vera-sidecar/` + `_bmad/memory/dan-sidecar/` (legacy sidecars; will be archived or removed).
5. Trial-2 validation evidence (operator-supplied; HALT if missing).

## T1 hard checkpoints

- Operator confirms Trial-2 validation evidence per AC-1 (one of three shapes).
- BMB-canonical sanctums intact (6 files each: INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES).
- Legacy sidecars present at `_bmad/memory/vera-sidecar/` + `_bmad/memory/dan-sidecar/`.
- Operator-choice: archive (default) vs removal.

## Files in scope

**Conditionally moved or removed (2 directories):**
- `_bmad/memory/vera-sidecar/` → archive: `_bmad/memory/_archive/vera-sidecar-pre-7b-3-2026-04-29/` OR removal: `git rm -rf`.
- `_bmad/memory/dan-sidecar/` → archive: `_bmad/memory/_archive/dan-sidecar-pre-7b-10-2026-04-30/` OR removal: `git rm -rf`.

**Modified (1 file):**
- `_bmad-output/planning-artifacts/deferred-inventory.md` — mark both entries as ~~CLOSED~~ with closure provenance.

**Do NOT modify:**
- `_bmad/memory/bmad-agent-vera/` or `_bmad/memory/bmad-agent-dan/` (BMB-canonical sanctums; READ-ONLY)
- Any other production code or test
- pyproject.toml

## Critical implementation notes

- **HALT discipline at T1**: if operator does NOT confirm Trial-2 validation evidence, HALT and request authorization. Do NOT proceed.
- **Archive path** (default): `git mv` preserves git history for audit trail. Naming convention: `_bmad/memory/_archive/<sidecar-name>-pre-<closing-story>-<date>/`.
- **Removal path** (operator-override): `git rm -rf`. Pre-cleanup state remains in git history.
- **Deferred-inventory closure shape**: prefix entries with `~~` and suffix with `~~` to strikethrough; add closure note: `**CLOSED <date> via 7c-housekeeping-4** (commit SHA <sha>; archived to <path> | removed from disk).`
- **K-target 1.1× ≈ 55 LOC ceiling**. Estimate ~50 LOC.
- **T11 lite tier**: minimal scope; mostly file moves + 2 deferred-inventory entries.

## Verification battery (T4)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_sanctum_alignment_dsl.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-housekeeping-4-legacy-sidecar-cleanup.md
```

## T10

T10: dropbox at `_codex-handoff/7c-housekeeping-4.ready-for-review.md`. Include: chosen path (archive vs removal) + Trial-2 evidence pointer + per-sidecar archive/removal evidence + deferred-inventory closure entry shape.

## Boundary

HALT on: Trial-2 validation evidence missing/unclear; BMB-canonical sanctums missing/incomplete; class-conformance count change.

DO NOT introduce: changes to BMB-canonical sanctums; new pyproject.toml contracts; changes to skill files (`skills/bmad-agent-{vera,dan}/SKILL.md`).
```

---

## Operator dispatch checklist

1. ☐ **Trial-2 validation evidence confirmed (AC-1; HARD GATE).**
2. ☐ Operator selects archive vs removal path.
3. ☐ AMELIA-P2 PASS.
4. ☐ Sandbox-AC PASS.
5. ☐ Sprint-status: ready-for-dev → in-progress.
6. ☐ Dispatch (solo; minimal Codex effort).
