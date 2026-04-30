# Behavioral version history - compositor

**Specialist:** compositor (Class D2 pipeline-greenfield)
**Current version:** v0.1 (initial body activation)

Tracks behavioral changes only. Implementation refactors that preserve this contract do not create a new entry.

## Version history

### v0.1 - 2026-04-30 (initial body activation)

**Story:** 7b.11 Compositor Greenfield
**Behavioral baseline:** Compositor localizes approved Gary still PNGs and Kira motion clips into the assembly bundle, then regenerates a deterministic `DESCRIPT-ASSEMBLY-GUIDE.md` for Descript handoff.
**Determinism contract:** bytes-identical for localized stills and motion; field-masked-hash for assembly guide modulo `generated_at`, `run_id`, and `build_timestamp`.
**Pipeline-determinism harness rate:** target >=0.99; measured during Story 7b.11 T13.

## Version-bump policy

- **Patch bump:** refactor only; no contract or determinism change.
- **Minor bump:** additive input/output contract change; determinism preserved.
- **Major bump:** breaking contract or determinism change; requires party-mode consensus.
